#!/usr/bin/env python3
"""Bloque 7: obtiene un access token real del usuario de prueba, por el mismo camino que la app
(login administrado de Cognito, Authorization Code + PKCE S256, MFA TOTP), con Chromium sin
ventana (Playwright). Lo usa la prueba de saturación de HAL-16 para medir el throttling con
solicitudes autenticadas.

Variables: QWALLET_PRUEBA_CORREO, QWALLET_PRUEBA_CLAVE, QWALLET_PRUEBA_TOTP (secretos de GitHub).
Uso: python3 token_prueba.py <host-cognito> <client-id> <archivo-de-salida> [carpeta-diagnóstico]
Escribe el access token SOLO en el archivo indicado (fuera de la carpeta de evidencias). En la
carpeta de diagnóstico deja qué vio en cada paso (campos visibles, ruta de la página y una
captura), sin la clave, la semilla ni tokens.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import struct
import sys
import time
import urllib.parse
import urllib.request

from playwright.sync_api import sync_playwright

REDIRECT = "qwallet://auth/callback"
SCOPE = "openid email qwallet/api"


def totp(semilla: str) -> str:
    clave = base64.b32decode(semilla + "=" * (-len(semilla) % 8))
    h = hmac.new(clave, struct.pack(">Q", int(time.time() // 30)), hashlib.sha1).digest()
    o = h[-1] & 0x0F
    return f"{(struct.unpack('>I', h[o:o + 4])[0] & 0x7FFFFFFF) % 1_000_000:06d}"


def main() -> int:
    host, client_id, salida = sys.argv[1], sys.argv[2], sys.argv[3]
    diag_dir = sys.argv[4] if len(sys.argv) > 4 else ""
    diag: list[str] = []
    correo, clave, semilla = (os.environ[k] for k in ("QWALLET_PRUEBA_CORREO", "QWALLET_PRUEBA_CLAVE", "QWALLET_PRUEBA_TOTP"))
    verificador = secrets.token_urlsafe(64)
    reto = base64.urlsafe_b64encode(hashlib.sha256(verificador.encode()).digest()).rstrip(b"=").decode()
    estado = secrets.token_urlsafe(16)
    url = f"https://{host}/oauth2/authorize?" + urllib.parse.urlencode({
        "response_type": "code", "client_id": client_id, "redirect_uri": REDIRECT, "scope": SCOPE,
        "state": estado, "code_challenge": reto, "code_challenge_method": "S256", "lang": "es",
    })

    codigo: dict[str, str] = {}

    def al_responder(resp) -> None:
        destino = resp.headers.get("location", "")
        if destino.startswith(REDIRECT):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(destino).query)
            if q.get("state", [""])[0] == estado:
                codigo["code"] = q.get("code", [""])[0]

    with sync_playwright() as p:
        nav = p.chromium.launch()
        pag = nav.new_page()
        pag.on("response", al_responder)
        pag.goto(url, wait_until="networkidle")
        hecho = set()
        fin = time.time() + 120
        paso = 0
        while not codigo and time.time() < fin:
            visibles = lambda sel: [e for e in pag.query_selector_all(sel) if e.is_visible()]  # noqa: E731
            paso += 1
            campos = [f"{e.get_attribute('type')}/{e.get_attribute('name')}/{e.get_attribute('autocomplete')}"
                      for e in visibles("input")]
            botones = [(e.inner_text() or "").strip()[:30] for e in visibles("button")]
            diag.append(f"paso {paso}: {urllib.parse.urlparse(pag.url).path} campos={campos} botones={botones} hecho={sorted(hecho)}")
            if diag_dir and paso <= 6:
                pag.screenshot(path=f"{diag_dir}/EVD-7-05b_token_paso{paso}.png")
            clave_in = visibles("input[type=password]")
            usuario_in = visibles("input[type=email], input[name=username], input[autocomplete=username]")
            codigo_in = visibles("input[autocomplete=one-time-code], input[name*=code i], input[inputmode=numeric]")
            if codigo_in and "clave" in hecho and "codigo" not in hecho:
                codigo_in[0].fill(totp(semilla))
                codigo_in[0].press("Enter")
                hecho.add("codigo")
                print("Código TOTP enviado.", flush=True)
            elif clave_in and "clave" not in hecho:
                if usuario_in and "correo" not in hecho:
                    usuario_in[0].fill(correo)
                    hecho.add("correo")
                clave_in[0].fill(clave)
                clave_in[0].press("Enter")
                hecho.add("clave")
                print("Contraseña enviada.", flush=True)
            elif usuario_in and "correo" not in hecho:
                usuario_in[0].fill(correo)
                usuario_in[0].press("Enter")
                hecho.add("correo")
                print("Correo enviado.", flush=True)
            pag.wait_for_timeout(3000)
        nav.close()

    texto_diag = "EVD-7-05b diagnóstico del login automático (sin secretos)\n" + "\n".join(diag) + "\n"
    if diag_dir:
        with open(f"{diag_dir}/EVD-7-05b_token_diagnostico.txt", "w", encoding="utf-8") as f:
            f.write(texto_diag)
    if not codigo.get("code"):
        print("No se obtuvo el código de autorización.")
        for linea in diag[-6:]:
            print(f"::warning title=token_prueba::{linea}")
        return 1
    cuerpo = urllib.parse.urlencode({
        "grant_type": "authorization_code", "client_id": client_id, "code": codigo["code"],
        "redirect_uri": REDIRECT, "code_verifier": verificador,
    }).encode()
    req = urllib.request.Request(f"https://{host}/oauth2/token", data=cuerpo,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=20) as r:
        tokens = json.loads(r.read())
    with open(salida, "w", encoding="utf-8") as f:
        f.write(tokens["access_token"])
    # Se revoca el refresh token de inmediato: solo se necesita el access token de 15 minutos.
    if "refresh_token" in tokens:
        rv = urllib.request.Request(f"https://{host}/oauth2/revoke",
                                    data=urllib.parse.urlencode({"token": tokens["refresh_token"], "client_id": client_id}).encode(),
                                    headers={"Content-Type": "application/x-www-form-urlencoded"})
        urllib.request.urlopen(rv, timeout=20).read()
    print("Access token obtenido con PKCE + MFA (vence en 15 minutos); refresh token revocado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
