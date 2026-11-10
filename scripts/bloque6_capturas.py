"""Figuras de capturas de pantalla para el informe final (bloque 6).

Uso:
    python scripts/bloque6_capturas.py
    python scripts/entrega1_estilos.py docs/entregas/Final_Capturas.docx

Arma las figuras compuestas con las capturas de docs/evidencias (EVD-1-xx, EVD-4-10, EVD-5-06d y
EVD-6-01 a EVD-6-07) y un Word con dos partes que final_ensamblar.py inserta en su lugar:
  1. Texto y Figuras de la app al final de la sección 4.3 (pantallas principales y FLAG_SECURE).
  2. "Anexo D. Capturas de pantalla" al final de 6.5.
Numeración provisional desde la Figura 101; final_ensamblar.py la renumera por orden de aparición.
Requiere python-docx y Pillow.
"""
import copy
from pathlib import Path

import docx
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Emu, Inches, Pt

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
EV = RAIZ / "docs/evidencias"
FIG = EV / "bloque6"
FUENTE = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def fila_telefonos(archivos, etiquetas, salida, alto=1200, sep=40, borde_negro=()):
    f = ImageFont.truetype(FUENTE, 44)
    ims = []
    for a in archivos:
        im = Image.open(a).convert("RGB")
        im = im.resize((int(im.width * alto / im.height), alto), Image.LANCZOS)
        ims.append(im)
    ancho = sum(i.width for i in ims) + sep * (len(ims) + 1)
    lienzo = Image.new("RGB", (ancho, alto + 2 * sep + 70), "white")
    d = ImageDraw.Draw(lienzo)
    x = sep
    for k, (im, et) in enumerate(zip(ims, etiquetas)):
        lienzo.paste(im, (x, sep))
        d.rectangle([x - 2, sep - 2, x + im.width + 1, sep + alto + 1], outline="#94A3B8", width=3)
        w = d.textlength(et, font=f)
        d.text((x + (im.width - w) / 2, sep + alto + 18), et, font=f, fill="#0F172A")
        x += im.width + sep
    lienzo.save(salida)
    return salida


def apilar(archivos, salida, ancho=1600, sep=30):
    ims = []
    for a in archivos:
        im = Image.open(a).convert("RGB")
        if im.width > ancho:
            im = im.resize((ancho, int(im.height * ancho / im.width)), Image.LANCZOS)
        ims.append(im)
    w = max(i.width for i in ims)
    lienzo = Image.new("RGB", (w, sum(i.height for i in ims) + sep * (len(ims) - 1)), "white")
    y = 0
    for im in ims:
        lienzo.paste(im, (0, y))
        y += im.height + sep
    lienzo.save(salida)
    return salida


# Bloque 7: sin la pantalla de inicio de sesión de la versión de desarrollo (EVD-6-02); el inicio
# de sesión real con Cognito tiene su propia figura con capturas del emulador de GitHub Actions.
F_APP = fila_telefonos(
    [FIG / "EVD-6-01_bienvenida.png", FIG / "EVD-6-03_inicio.png",
     FIG / "EVD-6-04_movimientos.png", FIG / "EVD-6-05_presupuestos.png"],
    ["Bienvenida", "Inicio", "Movimientos", "Presupuestos"],
    FIG / "FIG_app_pantallas.png")
FIG7 = EV / "bloque7"
F_LOGIN = fila_telefonos(
    [FIG7 / "EVD-7-01_app_login.png", FIG7 / "EVD-7-02_cognito_login.png",
     FIG7 / "EVD-7-03_cognito_mfa.png", FIG7 / "EVD-7-04_app_inicio.png"],
    ["App: inicio de sesión", "Cognito: contraseña", "Cognito: código MFA", "App: sesión abierta"],
    FIG7 / "FIG_login_cognito.png")
F_SECURE = fila_telefonos(
    [FIG / "EVD-6-06a_transferir_en_pantalla.png", FIG / "EVD-6-06b_transferir_screencap.png",
     FIG / "EVD-6-07a_perfil_en_pantalla.png", FIG / "EVD-6-07b_perfil_screencap.png"],
    ["Transferir: pantalla", "Transferir: captura", "Perfil: pantalla", "Perfil: captura"],
    FIG / "FIG_flag_secure.png")
F_AWS = apilar([EV / "EVD-1-03e_aws-mfa-raiz.png", EV / "EVD-1-03c_aws-presupuesto-5usd.png"], FIG / "FIG_aws_cuenta.png")
F_GH = apilar([EV / "EVD-1-04a_github-secret-protection.png", EV / "EVD-1-04c_github-ruleset-main.png",
               EV / "EVD-1-06_ruleset-push-rechazado.png"], FIG / "FIG_github.png", ancho=1340)
F_GL = EV / "EVD-1-07_gitleaks-historial-pre-publico.png"
F_FRIDA = fila_telefonos([EV / "bloque5/EVD-4-10_frida_app.png"], ["Frida y root detectados"], FIG / "FIG_frida.png")
F_CORREO = EV / "bloque5/EVD-5-06d_correo_alarma_auditoria.png"


# ================================================================ Word
PLANTILLA = RAIZ / "docs/entregas/Entrega1_Informe_QWallet.docx"
SALIDA = RAIZ / "docs/entregas/Final_Capturas.docx"
TABLA_INICIAL = 101
FIGURA_INICIAL = 101

doc = docx.Document(str(PLANTILLA))
cuerpo = doc.element.body
sect_final = copy.deepcopy(cuerpo[-1])
for hijo in list(cuerpo):
    cuerpo.remove(hijo)
cuerpo.append(sect_final)
s0 = doc.sections[-1]
s0.orientation = WD_ORIENT.PORTRAIT
s0.page_width, s0.page_height = Emu(7772400), Emu(10058400)

n_tabla = TABLA_INICIAL
n_figura = FIGURA_INICIAL


# ---------------------------------------------------------------- utilidades
def titulo(texto, nivel):
    doc.add_heading(texto, level=nivel)


def parrafo(texto, cursivas=()):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = Inches(0.5)
    partes = texto.split("*")
    for i, parte in enumerate(partes):
        if parte:
            r = p.add_run(parte)
            r.font.size = Pt(12)
            r.italic = i % 2 == 1
    return p


def rotulo(tipo, numero, nombre):
    p = doc.add_paragraph()
    r = p.add_run(f"{tipo} {numero}")
    r.bold = True
    r.font.size = Pt(12)
    p.paragraph_format.keep_with_next = True
    p2 = doc.add_paragraph()
    r2 = p2.add_run(nombre)
    r2.italic = True
    r2.font.size = Pt(12)
    p2.paragraph_format.keep_with_next = True


def nota(texto):
    p = doc.add_paragraph()
    r = p.add_run("Nota. ")
    r.italic = True
    r.font.size = Pt(12)
    r2 = p.add_run(texto)
    r2.font.size = Pt(12)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def borde(tc_pr, lados):
    b = OxmlElement("w:tcBorders")
    for lado in ("top", "left", "bottom", "right"):
        e = OxmlElement(f"w:{lado}")
        if lado in lados:
            e.set(qn("w:val"), "single")
            e.set(qn("w:sz"), "4")
            e.set(qn("w:color"), "000000")
        else:
            e.set(qn("w:val"), "none")
            e.set(qn("w:sz"), "0")
            e.set(qn("w:color"), "FFFFFF")
        b.append(e)
    tc_pr.append(b)


def margenes(tc_pr):
    m = OxmlElement("w:tcMar")
    for lado, v in (("top", 40), ("left", 90), ("bottom", 40), ("right", 90)):
        e = OxmlElement(f"w:{lado}")
        e.set(qn("w:w"), str(v))
        e.set(qn("w:type"), "dxa")
        m.append(e)
    tc_pr.append(m)


FUENTE_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FUENTE_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def anchos_sin_cortes(encabezado, filas, tam, total):
    from PIL import ImageFont
    fr = ImageFont.truetype(FUENTE_R, tam * 10)
    fb = ImageFont.truetype(FUENTE_B, tam * 10)
    n = len(encabezado)
    minimo, peso = [0.0] * n, [0.0] * n
    for i, fila in enumerate([encabezado] + filas):
        f = fb if i == 0 else fr
        for j, v in enumerate(fila):
            for palabra in str(v).replace("\n", " ").split():
                w = f.getlength(palabra) / 10 / 72
                minimo[j] = max(minimo[j], w)
            peso[j] += fr.getlength(str(v)) / 10 / 72
    margen = 180 / 1440 + 0.03
    minimo = [m + margen for m in minimo]
    libre = total - sum(minimo)
    if libre < 0:
        return None
    return [m + libre * p / sum(peso) for m, p in zip(minimo, peso)]


def tabla(nombre, encabezado, filas, tam=10, nota_txt=None, total=6.5):
    global n_tabla
    anchos_pulg = anchos_sin_cortes(encabezado, filas, tam, total)
    if anchos_pulg is None:
        raise SystemExit(f"La tabla '{nombre}' no cabe sin partir palabras en {total} pulgadas")
    rotulo("Tabla", n_tabla, nombre)
    n_tabla += 1
    t = doc.add_table(rows=1 + len(filas), cols=len(encabezado))
    t.autofit = False
    grid = t._tbl.tblGrid
    for gc, w in zip(grid.findall(qn("w:gridCol")), anchos_pulg):
        gc.set(qn("w:w"), str(int(w * 1440)))
    todas = [encabezado] + filas
    for i, fila in enumerate(todas):
        row = t.rows[i]
        tr_pr = row._tr.get_or_add_trPr()
        tr_pr.append(OxmlElement("w:cantSplit"))
        if i == 0:
            tr_pr.append(OxmlElement("w:tblHeader"))
        for j, valor in enumerate(fila):
            celda = row.cells[j]
            celda.width = Inches(anchos_pulg[j])
            tc_pr = celda._tc.get_or_add_tcPr()
            lados = set()
            if i == 0:
                lados = {"top", "bottom"}
            elif i == len(todas) - 1:
                lados = {"bottom"}
            borde(tc_pr, lados)
            margenes(tc_pr)
            p = celda.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for k, linea in enumerate(str(valor).split("\n")):
                if k:
                    p = celda.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                r = p.add_run(linea.replace("-", "‑"))
                r.font.size = Pt(tam)
                r.bold = i == 0
    if nota_txt:
        nota(nota_txt)
    return t


def figura(nombre, ruta, ancho_pulg, nota_txt):
    global n_figura
    rotulo("Figura", n_figura, nombre)
    n_figura += 1
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(ruta), width=Inches(ancho_pulg))
    nota(nota_txt)


def seccion(horizontal):
    s = doc.add_section(WD_SECTION.NEW_PAGE)
    if horizontal:
        s.orientation = WD_ORIENT.LANDSCAPE
        s.page_width, s.page_height = Emu(10058400), Emu(7772400)
    else:
        s.orientation = WD_ORIENT.PORTRAIT
        s.page_width, s.page_height = Emu(7772400), Emu(10058400)






# ---------------------------------------------------------------- parte 1: final de la sección 4.3
parrafo(
    "Para mostrar la app tal como la ve el usuario, la Figura 101 reúne sus pantallas principales. "
    "Las capturamos el 10 de noviembre de 2026 en el emulador Android con la versión de desarrollo, "
    "porque en la versión de producción freeRASP detecta el emulador y bloquea la app (Figura 10). "
    "Las pantallas de saldo, movimientos y presupuestos muestran datos de ejemplo de la propia app; "
    "conectarlas con la API (que ya existe y se probó en la sección 3) es parte de la siguiente "
    "versión (sección 6.3)."
)
figura(
    "Pantallas principales de Q-Wallet en el emulador Android",
    F_APP, 6.3,
    "Capturas propias en el emulador Pixel 8 (Android, API 36), versión de desarrollo, 10 de "
    "noviembre de 2026 (EVD-6-01, EVD-6-03 a EVD-6-05). En algunas pantallas el título queda bajo "
    "la barra de estado: es una observación de interfaz sin efecto en la seguridad.",
)
parrafo(
    "La versión final de la app inicia sesión de verdad (Figura 102). La app abre el inicio de sesión "
    "administrado de Amazon Cognito en una pestaña segura del navegador del teléfono, con el flujo "
    "de código de autorización y PKCE (S256): la contraseña y el código TOTP del segundo factor se "
    "escriben en la página de Cognito y la app nunca los ve. Con el código que devuelve Cognito, la "
    "app pide los tokens por una conexión con fijación de llaves (CTRL-08), guarda el access token "
    "de 15 minutos solo en memoria y el refresh token cifrado con una llave de Android Keystore "
    "(CTRL-07). Al volver a abrir la app, esa llave solo se usa después de la huella, el rostro o el "
    "bloqueo del teléfono, y al cerrar sesión la app revoca el refresh token en Cognito. Las "
    "capturas salen del emulador de GitHub Actions con un usuario de prueba que tiene MFA "
    "obligatorio; el resultado de CA-07 con este token real está en la Tabla 45."
)
figura(
    "Inicio de sesión real con Amazon Cognito: código de autorización con PKCE y MFA TOTP",
    F_LOGIN, 6.3,
    "Capturas propias en el emulador Android 13 (API 33) de GitHub Actions, con la copia de prueba "
    "del APK de producción (EVD-7-01 a EVD-7-04). El correo es el del usuario de prueba, con "
    "dominio reservado; la contraseña se escribe en un campo enmascarado.",
)
parrafo(
    "Con la misma versión probamos FLAG_SECURE (CTRL-22), que hasta entonces solo habíamos "
    "verificado leyendo el código. Con la pantalla Transferir abierta tomamos una captura desde "
    "dentro de Android con adb shell screencap y salió completamente negra; con Perfil pasó lo "
    "mismo. Al mismo tiempo, dumpsys window mostró el flag SECURE en la ventana de la app. La Figura "
    "103 pone lado a lado lo que ve el usuario y lo que obtiene una captura. Con esta prueba, la "
    "amenaza de exposición del saldo en capturas y en la vista de apps recientes (AME-09) pasó de "
    "verificada por configuración a verificada con una prueba; su riesgo residual no cambia."
)
figura(
    "FLAG_SECURE: la pantalla que ve el usuario frente a una captura tomada desde Android",
    F_SECURE, 6.3,
    "En cada par, a la izquierda la pantalla del emulador tomada desde fuera de Android y a la "
    "derecha adb shell screencap desde dentro de Android. Salida de dumpsys window: "
    "fl=LAYOUT_IN_SCREEN SECURE LAYOUT_INSET_DECOR (EVD-6-06 y EVD-6-07).",
)

# ---------------------------------------------------------------- parte 2: Anexo D
titulo("Anexo D. Capturas de pantalla", 3)
parrafo(
    "Este anexo reúne las capturas de la cuenta de AWS, del repositorio y de las pruebas que "
    "respaldan afirmaciones del informe y que no aparecen en el cuerpo. El número de cuenta, los "
    "ARN y los correos están tapados."
)
figura(
    "Cuenta de AWS: MFA del usuario raíz y presupuesto de US$5 con alerta",
    F_AWS, 6.3,
    "Consola de AWS, octubre de 2026 (EVD-1-03e y EVD-1-03c). Respaldan los controles de la "
    "cuenta de la sección 4.5 y la restricción de costo de la sección 1.3.",
)
figura(
    "GitHub: protección de secretos, ruleset de la rama main y push directo rechazado",
    F_GH, 6.3,
    "Configuración del repositorio (EVD-1-04a y EVD-1-04c) y prueba de un push directo a main "
    "rechazado por el ruleset con el error GH013 (EVD-1-06). Respaldan CTRL-16 y CTRL-21.",
)
figura(
    "gitleaks sobre todo el historial antes de publicar el repositorio",
    F_GL, 6.3,
    "Ejecución de gitleaks 8.30.1 en Docker sobre los 16 commits existentes: sin secretos "
    "(EVD-1-07). Respalda CTRL-16.",
)
figura(
    "freeRASP bloquea la app al detectar Frida y root (CA-10)",
    F_FRIDA, 2.6,
    "APK de producción en el emulador de GitHub Actions con frida-server 17.22.0 y un hook dentro "
    "del proceso de la app (EVD-4-10). Complementa la Tabla 45.",
)
figura(
    "Correo de la alarma de cambios a la auditoría y a la llave KMS",
    F_CORREO, 6.3,
    "Correo recibido el 1 de noviembre de 2026 por la alarma qwallet-auditoria-y-llaves "
    "(EVD-5-06d), con la cuenta y el ARN tapados. Complementa la Tabla 49 y la Figura 12.",
)

doc.save(str(SALIDA))
print("Generado:", SALIDA)
