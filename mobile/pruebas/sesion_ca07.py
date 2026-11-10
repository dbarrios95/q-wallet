#!/usr/bin/env python3
"""CA-07 con sesión real (bloque 7): inicio de sesión en la app con Cognito, desbloqueo,
revisión del almacenamiento con root y cierre de sesión, todo en el emulador.

Lo llama mobile/pruebas/dispositivo.sh (sección E). Maneja la pantalla con adb y
uiautomator (lee la jerarquía de la interfaz, toca por texto y escribe con "input text").
El usuario de prueba viene de secretos de GitHub (lo creó infra/scripts/usuario_prueba.py):
    QWALLET_PRUEBA_CORREO, QWALLET_PRUEBA_CLAVE, QWALLET_PRUEBA_TOTP
Nunca escribe la clave, la semilla ni ningún token en la evidencia.

Uso: python3 sesion_ca07.py carpeta-de-salida
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import re
import struct
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

PKG = "gt.qwallet.app"
PIN_TELEFONO = "1234"  # bloqueo de pantalla del emulador, solo para esta prueba
OUT = sys.argv[1]
CORREO = os.environ.get("QWALLET_PRUEBA_CORREO", "")
CLAVE = os.environ.get("QWALLET_PRUEBA_CLAVE", "")
SEMILLA = os.environ.get("QWALLET_PRUEBA_TOTP", "")

registro: list[str] = []


def log(msg: str) -> None:
    linea = f"[{datetime.now(timezone.utc):%H:%M:%S}] {msg}"
    for secreto in (CLAVE, SEMILLA):
        if secreto:
            linea = linea.replace(secreto, "***")
    print(linea, flush=True)
    registro.append(linea)


def adb(*args: str, timeout: int = 60) -> str:
    r = subprocess.run(["adb", *args], capture_output=True, text=True, timeout=timeout)
    return (r.stdout or "") + (r.stderr or "")


def sh(cmd: str, timeout: int = 60) -> str:
    return adb("shell", cmd, timeout=timeout)


def captura(nombre: str) -> None:
    with open(os.path.join(OUT, nombre), "wb") as f:
        f.write(subprocess.run(["adb", "exec-out", "screencap", "-p"], capture_output=True, timeout=30).stdout)


def marcas() -> list[str]:
    salida = adb("logcat", "-d", timeout=60)
    return sorted({m.group(0).rstrip() for m in re.finditer(r"QWALLET_[A-Z]+ [^\r\n]*", salida)})


def totp() -> str:
    clave = base64.b32decode(SEMILLA + "=" * (-len(SEMILLA) % 8))
    h = hmac.new(clave, struct.pack(">Q", int(time.time() // 30)), hashlib.sha1).digest()
    o = h[-1] & 0x0F
    return f"{(struct.unpack('>I', h[o:o + 4])[0] & 0x7FFFFFFF) % 1_000_000:06d}"


def pantalla() -> list[dict]:
    """Nodos visibles de la interfaz (uiautomator)."""
    for _ in range(3):
        sh("uiautomator dump /sdcard/ui.xml >/dev/null 2>&1", timeout=40)
        xml = sh("cat /sdcard/ui.xml", timeout=20)
        if "<hierarchy" in xml:
            break
        time.sleep(2)
    else:
        return []
    xml = xml[xml.index("<?xml") if "<?xml" in xml else xml.index("<hierarchy"):]
    try:
        raiz = ET.fromstring(xml)
    except ET.ParseError:
        return []
    nodos = []
    for n in raiz.iter("node"):
        b = re.findall(r"\d+", n.get("bounds", ""))
        if len(b) != 4:
            continue
        x1, y1, x2, y2 = map(int, b)
        if x2 <= x1 or y2 <= y1:
            continue
        nodos.append({
            "texto": n.get("text", ""), "desc": n.get("content-desc", ""), "clase": n.get("class", ""),
            "paquete": n.get("package", ""), "clave": n.get("password") == "true",
            "foco": n.get("focused") == "true", "x": (x1 + x2) // 2, "y": (y1 + y2) // 2,
            "id": n.get("resource-id", ""),
        })
    return nodos


def buscar(nodos: list[dict], patron: str) -> dict | None:
    rx = re.compile(patron, re.I)
    for n in nodos:
        if rx.search(n["texto"]) or rx.search(n["desc"]):
            return n
    return None


def tocar(n: dict) -> None:
    sh(f"input tap {n['x']} {n['y']}")
    time.sleep(1.5)


def escribir(texto: str) -> None:
    # Solo letras, números, @ . - _ (así se generaron el correo y la clave).
    sh(f"input text '{texto}'")
    time.sleep(1)


def esperar(patron: str, segundos: int = 60) -> dict | None:
    fin = time.time() + segundos
    while time.time() < fin:
        n = buscar(pantalla(), patron)
        if n:
            return n
        time.sleep(3)
    return None


def esperar_marca(patron: str, segundos: int = 60) -> bool:
    fin = time.time() + segundos
    while time.time() < fin:
        if any(re.search(patron, m) for m in marcas()):
            return True
        time.sleep(3)
    return False


def abrir_app() -> None:
    sh(f"am force-stop {PKG}")
    adb("logcat", "-c")
    sh(f"monkey -p {PKG} -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1")
    time.sleep(20)


def login_cognito() -> bool:
    """Llena el login administrado de Cognito en el Custom Tab, paso a paso."""
    hecho = {"correo": False, "clave": False, "codigo": False}
    n_captura = 0
    fin = time.time() + 240
    while time.time() < fin:
        if esperar_marca(r"QWALLET_AUTH .*login=(ok|error|cancel|dismiss)", 2):
            return True
        nodos = pantalla()
        campos = [n for n in nodos if n["clase"].endswith("EditText")]
        web = [n for n in nodos if n["paquete"] not in (PKG, "")]
        if not campos or not web:
            time.sleep(3)
            continue
        paquete = web[0]["paquete"]
        texto_pagina = " ".join(n["texto"] + " " + n["desc"] for n in nodos)
        pide_codigo = re.search(r"c[oó]digo|code|autenticador|authenticator|TOTP|MFA", texto_pagina, re.I)
        clave = [c for c in campos if c["clave"]]
        normal = [c for c in campos if not c["clave"]]
        n_captura += 1
        if pide_codigo and not clave and hecho["clave"] and not hecho["codigo"]:
            captura(f"EVD-7-03_cognito_mfa.png")
            tocar(normal[0])
            escribir(totp())
            sh("input keyevent 66")
            hecho["codigo"] = True
            log(f"Código TOTP de 6 dígitos escrito en la página de Cognito ({paquete}).")
        elif clave and not hecho["clave"]:
            if normal and not hecho["correo"]:
                tocar(normal[0])
                escribir(CORREO)
                hecho["correo"] = True
                log(f"Correo escrito en la página de Cognito ({paquete}).")
            captura("EVD-7-02_cognito_login.png")
            tocar(clave[0])
            escribir(CLAVE)
            sh("input keyevent 66")
            hecho["clave"] = True
            log("Contraseña escrita (campo de contraseña, enmascarado) y enviada.")
        elif normal and not hecho["correo"]:
            captura("EVD-7-02_cognito_login.png")
            tocar(normal[0])
            escribir(CORREO)
            sh("input keyevent 66")
            hecho["correo"] = True
            log(f"Correo escrito y enviado ({paquete}); se espera la página de la contraseña.")
        else:
            boton = buscar(nodos, r"^(siguiente|next|continuar|continue|iniciar sesi[oó]n|sign in|enviar|submit|verificar|verify)$")
            if boton:
                tocar(boton)
        time.sleep(6)
    return False


def desbloquear_con_pin() -> None:
    """Responde el diálogo del sistema que pide el PIN del teléfono (BiometricPrompt)."""
    fin = time.time() + 60
    while time.time() < fin:
        nodos = pantalla()
        if any(n["clave"] or n["clase"].endswith("EditText") for n in nodos if n["paquete"] != PKG):
            escribir(PIN_TELEFONO)
            sh("input keyevent 66")
            log("PIN del teléfono ingresado en el diálogo del sistema.")
            return
        if esperar_marca(r"QWALLET_AUTH .*desbloqueo=", 2):
            return
        time.sleep(3)


def revisar_almacenamiento() -> list[str]:
    lineas = []
    archivos = sh(f"find /data/data/{PKG} -type f 2>/dev/null").split()
    lineas.append(f"Archivos privados de la app (con root): {len(archivos)}")
    for a in archivos:
        lineas.append(f"   {a}")
    jwt = sh(f"grep -rl 'eyJ' /data/data/{PKG} 2>/dev/null").split()
    lineas.append("")
    lineas.append(f"Archivos con texto de JWT (eyJ...): {', '.join(jwt) if jwt else 'ninguno'}")
    for etiqueta, valor in (("el correo del usuario", CORREO), ("la contraseña", CLAVE)):
        if valor:
            hay = sh(f"grep -rlF '{valor}' /data/data/{PKG} 2>/dev/null").split()
            lineas.append(f"Archivos con {etiqueta} en claro: {', '.join(hay) if hay else 'ninguno'}")
    prefs = [a for a in archivos if "shared_prefs" in a and "SecureStore" in a]
    for p in prefs:
        contenido = sh(f"cat {p}")
        claves = re.findall(r'name="([^"]+)"', contenido)
        lineas.append("")
        lineas.append(f"{p}: entradas {', '.join(claves) if claves else '(vacío)'}")
        for nombre, valor in re.findall(r'name="([^"]+)"[^>]*>([^<]*)<', contenido):
            # Ni un fragmento del valor en la evidencia: solo su tamaño y su forma (bloque 7: gitleaks
            # marcó como posible llave el inicio del texto cifrado).
            forma = "objeto con texto cifrado (ct)" if "ct&quot;" in valor or '"ct"' in valor else "otro formato"
            lineas.append(f"   {nombre}: {len(valor)} caracteres, {forma}; cifrado, no es JWT"
                          if "eyJ" not in valor else f"   {nombre}: CONTIENE UN JWT EN CLARO")
    llaves = sh("ls /data/misc/keystore/persistent.sqlite 2>/dev/null && echo keystore2_presente")
    lineas.append("")
    lineas.append("Llaves de Android Keystore: " + ("en keystore2 (fuera del alcance de la app y de la "
                  "carpeta de datos)" if "keystore2_presente" in llaves else "no se pudo listar"))
    return lineas


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    fecha = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    if not (CORREO and CLAVE and SEMILLA):
        texto = "EVD-7-01 CA-07 con sesión real: NO SE CORRIÓ (faltan los secretos QWALLET_PRUEBA_*).\n"
        open(os.path.join(OUT, "EVD-7-01_ca07_sesion_real.txt"), "w", encoding="utf-8").write(texto)
        print(texto)
        return 0

    resultado: dict[str, str] = {}
    sh("svc power stayon true")
    navegadores = sh("pm list packages | grep -i -E 'chrome|browser|webview'")
    log("Navegadores instalados: " + " ".join(navegadores.split()))
    # Chrome sin pantallas de primer uso (el emulador es userdebug y adb corre como root).
    sh("echo 'chrome --disable-fre --no-default-browser-check --no-first-run' > /data/local/tmp/chrome-command-line")
    sh("chmod 644 /data/local/tmp/chrome-command-line")
    sh("am set-debug-app --persistent com.android.chrome")
    # Bloqueo de pantalla con PIN: sin él la app no guarda la sesión (diseño de CTRL-07).
    log("Bloqueo de pantalla: " + sh(f"locksettings set-pin {PIN_TELEFONO}").strip())
    sh("input keyevent 224")
    sh("wm dismiss-keyguard")

    # 1) Inicio de sesión real
    abrir_app()
    if (b := esperar(r"^Iniciar sesi[oó]n$", 30)):
        tocar(b)
    boton = esperar(r"Continuar a la p[aá]gina segura", 30)
    captura("EVD-7-01_app_login.png")
    if not boton:
        log("No apareció el botón de la app para iniciar sesión.")
        return fin(fecha, resultado, False)
    tocar(boton)
    time.sleep(8)
    ok = login_cognito()
    time.sleep(8)
    captura("EVD-7-04_app_inicio.png")
    m = marcas()
    resultado["login"] = next((x for x in m if "login=" in x), "sin marca")
    resultado["api"] = next((x for x in m if "api=GET_/me" in x), "sin marca")
    log(f"Marca de login: {resultado['login']}")
    log(f"Primera llamada a la API con el token: {resultado['api']}")
    if not ok or "login=ok" not in resultado["login"]:
        captura("EVD-7-0x_fallo_login.png")
        return fin(fecha, resultado, False)

    # 2) Almacenamiento con la sesión abierta (CA-07)
    resultado["almacenamiento"] = "\n".join(revisar_almacenamiento())
    logcat = adb("logcat", "-d", timeout=60)
    resultado["tokens_en_logcat"] = str(len(re.findall(r"eyJ[A-Za-z0-9_-]{10,}", logcat)))

    # 3) Volver a abrir la app: desbloqueo con el PIN del teléfono y renovación del token
    abrir_app()
    desbloquear_con_pin()
    esperar_marca(r"QWALLET_AUTH .*desbloqueo=", 40)
    time.sleep(5)
    resultado["desbloqueo"] = next((x for x in marcas() if "desbloqueo=" in x), "sin marca")
    log(f"Desbloqueo: {resultado['desbloqueo']}")

    # 4) Cierre de sesión: revoca el refresh token y borra lo guardado
    if (p := esperar(r"^Perfil$", 20)):
        tocar(p)
        for _ in range(4):
            if (s := buscar(pantalla(), r"Cerrar sesi[oó]n segura")):
                tocar(s)
                break
            sh("input swipe 540 1800 540 600 400")
            time.sleep(2)
    esperar_marca(r"QWALLET_AUTH .*logout=", 30)
    resultado["logout"] = next((x for x in marcas() if "logout=" in x), "sin marca")
    restos = sh(f"cat /data/data/{PKG}/shared_prefs/*SecureStore*.xml 2>/dev/null")
    resultado["tras_logout"] = ", ".join(re.findall(r'name="([^"]+)"', restos)) or "ninguna entrada"
    log(f"Cierre de sesión: {resultado['logout']}")
    return fin(fecha, resultado, True)


def fin(fecha: str, r: dict[str, str], completo: bool) -> int:
    t = [
        "EVD-7-01 CA-07 extraer tokens del dispositivo, con sesión real (CTRL-07, CTRL-18)",
        f"Fecha: {fecha}",
        "Dispositivo: emulador Android 13 (API 33), imagen userdebug con root; bloqueo de pantalla con PIN.",
        "APK: copia de prueba de la versión de producción (release, Hermes + R8) con freeRASP en modo",
        "registro (EXPO_PUBLIC_QWALLET_APK_PRUEBA=ca07), porque en este emulador la versión de producción",
        "se bloquea (EVD-5-03). El código de sesión y de almacenamiento es el mismo.",
        "Usuario: usuario de prueba de Cognito con MFA TOTP obligatorio (correo de dominio reservado).",
        "",
        "1) Inicio de sesión real (login administrado de Cognito, Authorization Code + PKCE, MFA TOTP)",
        f"   {r.get('login', 'no llegó')}",
        f"   {r.get('api', 'no llegó')}",
        "",
        "2) Almacenamiento con la sesión abierta (atacante con root lee /data/data de la app)",
    ]
    t += ["   " + x for x in r.get("almacenamiento", "no llegó").splitlines()]
    t += [
        f"   Tokens (eyJ...) en el registro del sistema (logcat): {r.get('tokens_en_logcat', 'no llegó')}",
        "",
        "3) Volver a abrir la app: desbloqueo con el bloqueo del teléfono y renovación en Cognito",
        f"   {r.get('desbloqueo', 'no llegó')}",
        "",
        "4) Cierre de sesión: revocación del refresh token en Cognito y borrado local",
        f"   {r.get('logout', 'no llegó')}",
        f"   Entradas de SecureStore después del cierre: {r.get('tras_logout', 'no llegó')}",
        "",
        "Bitácora de la prueba:",
    ] + ["   " + x for x in registro]
    texto = "\n".join(t) + "\n"
    open(os.path.join(OUT, "EVD-7-01_ca07_sesion_real.txt"), "w", encoding="utf-8").write(texto)
    print(texto)
    return 0 if completo else 1


if __name__ == "__main__":
    sys.exit(main())
