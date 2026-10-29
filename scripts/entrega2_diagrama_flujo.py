"""Figura de la sección 4.1: arquitectura cloud con el flujo de datos numerado.

Uso: python scripts/entrega2_diagrama_flujo.py
Genera docs/evidencias/EVD-3-08_arquitectura_flujo_datos.svg y .png (EVD-3-08).
El contenido sale del Terraform de /infra (bloque 1); si cambia la arquitectura,
se corrige aquí y se vuelve a generar. Requiere cairosvg.
"""
from pathlib import Path

import cairosvg

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "docs" / "evidencias" / "EVD-3-08_arquitectura_flujo_datos"

AZUL = "#0B1F3A"
VERDE = "#00A86B"
GRIS9 = "#0F172A"
GRIS5 = "#64748B"
GRIS2 = "#E2E8F0"
GRIS0 = "#F8FAFC"
NARANJA = "#F97316"
FUENTE = "Arial, Liberation Sans, Helvetica, sans-serif"

W, H = 1600, 980
el = []


def caja(x, y, w, h, titulo, lineas, borde=AZUL, relleno="#FFFFFF", tam=15):
    el.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{relleno}" stroke="{borde}" stroke-width="2"/>')
    el.append(f'<text x="{x + w / 2}" y="{y + 26}" text-anchor="middle" font-weight="bold" font-size="17" fill="{GRIS9}">{titulo}</text>')
    for i, t in enumerate(lineas):
        el.append(f'<text x="{x + w / 2}" y="{y + 50 + i * 20}" text-anchor="middle" font-size="{tam}" fill="{GRIS5}">{t}</text>')


def zona(x, y, w, h, etiqueta):
    el.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="none" stroke="{GRIS5}" stroke-width="1.5" stroke-dasharray="8 6"/>')
    el.append(f'<text x="{x + 12}" y="{y + 20}" font-size="14" fill="{GRIS5}">{etiqueta}</text>')


def flecha(x1, y1, x2, y2, color=VERDE, ancho=3, guion=None):
    d = f' stroke-dasharray="{guion}"' if guion else ""
    el.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{ancho}"{d} marker-end="url(#punta-{color[1:]})"/>')


def numero(x, y, n, color=VERDE):
    el.append(f'<circle cx="{x}" cy="{y}" r="15" fill="{color}"/>')
    el.append(f'<text x="{x}" y="{y + 6}" text-anchor="middle" font-size="16" font-weight="bold" fill="#FFFFFF">{n}</text>')


def texto(x, y, t, tam=14, color=GRIS9, ancla="middle", peso="normal"):
    el.append(f'<text x="{x}" y="{y}" text-anchor="{ancla}" font-size="{tam}" font-weight="{peso}" fill="{color}">{t}</text>')


# Zonas (fronteras de confianza de la sección 1.5)
zona(20, 150, 270, 470, "TB1 · Dispositivo del cliente")
zona(320, 60, 600, 640, "TB2 · Borde de AWS (us-east-1)")
zona(950, 60, 300, 640, "TB3 · Cómputo")
zona(1280, 60, 300, 640, "TB4 · Datos y llaves")
zona(320, 730, 1260, 230, "TB5 / TB6 · Despliegue y auditoría")

# Cliente
caja(40, 250, 230, 250, "App Android", [
    "Q-Wallet (Expo, minSdk 29)",
    "Tokens en Keystore",
    "(CTRL-07)",
    "Pinning de llave pública",
    "(CTRL-08)",
    "freeRASP (CTRL-15)",
    "Sin secretos (CTRL-16)",
])

# Borde
caja(360, 100, 250, 180, "Amazon Cognito", [
    "Login administrado",
    "OAuth2 código + PKCE",
    "MFA TOTP obligatorio",
    "Access token de 15 min",
    "(CTRL-18)",
], borde=AZUL)
caja(360, 380, 220, 200, "AWS WAF", [
    "Reglas comunes (OWASP)",
    "Entradas maliciosas",
    "conocidas",
    "100 solicitudes / 5 min",
    "por IP (CTRL-17)",
    "Se enciende en pruebas",
], borde=NARANJA)
caja(640, 300, 260, 300, "API Gateway REST", [
    "Endpoint regional",
    "Solo TLS 1.3 (STRICT)",
    "SecurityPolicy_TLS13_1_3",
    "_2025_09 (CTRL-08)",
    "Authorizer de Cognito:",
    "firma, vigencia y scope",
    "qwallet/api del token",
    "Throttling 10/s, ráfaga 20",
    "Errores genéricos (CTRL-13)",
    "Logs de acceso sin tokens",
], tam=14)

# Lambdas
servicios = ["svc-profile", "svc-accounts", "svc-transfers", "svc-budgets", "svc-admin"]
for i, s in enumerate(servicios):
    y = 110 + i * 82
    caja(985, y, 230, 64, s, [f"rol IAM qwallet-{s}"], tam=13)
texto(1100, 540, "Cada función: su propio rol", 14, GRIS5)
texto(1100, 560, "con límite de permisos (CTRL-12)", 14, GRIS5)
texto(1100, 580, "y valida el dueño del recurso", 14, GRIS5)
texto(1100, 600, "con el sub del token (CTRL-01)", 14, GRIS5)
texto(1100, 630, "Imágenes en ECR (CTRL-11)", 14, GRIS5)

# Datos
caja(1305, 100, 250, 230, "DynamoDB", [
    "8 tablas por tipo de dato",
    "perfiles · pin · cuentas",
    "movimientos · transferencias",
    "beneficiarios · presupuestos",
    "auditoría",
    "AES-256 con la CMK",
    "PITR y protección de borrado",
], tam=14)
caja(1305, 370, 250, 150, "AWS KMS", [
    "alias/qwallet-datos",
    "CMK simétrica AES-256",
    "Rotación anual",
    "(CTRL-19)",
])
caja(1305, 560, 250, 110, "SSM Parameter Store", [
    "SecureString por servicio",
    "/qwallet/svc-*/ (CTRL-16)",
], tam=14)

# Despliegue y auditoría
caja(350, 790, 290, 150, "GitHub Actions", [
    "OIDC, sin llaves guardadas",
    "Rol qwallet-gha-despliegue",
    "solo entorno dev / main",
    "Checkov + plan sin borrados",
    "(CTRL-21)",
], tam=14)
caja(700, 790, 260, 150, "Terraform", [
    "Estado en S3 cifrado",
    "con bloqueo nativo",
    "Versionado, sin acceso",
    "público (ACT-09)",
], tam=14)
caja(1020, 790, 260, 150, "CloudWatch Logs", [
    "Logs JSON de Lambda",
    "y API Gateway",
    "Cifrados con la CMK",
    "Retención 365 días (CTRL-09)",
], tam=14)
caja(1310, 790, 250, 150, "CloudTrail → S3", [
    "Multirregión, validación",
    "de integridad, cifrado",
    "con la CMK (CTRL-20)",
    "Fuente del SIEM",
], tam=14)

# Flujo numerado (verde = datos del usuario)
flecha(270, 290, 356, 210)            # 1 login
numero(312, 245, 1)
flecha(358, 250, 274, 330, color=AZUL, guion="6 5")  # 2 tokens
numero(318, 302, 2, AZUL)
flecha(270, 450, 356, 470)            # 3 solicitud TLS 1.3
numero(312, 455, 3)
flecha(580, 480, 636, 470)            # 4 WAF -> API
numero(608, 455, 4)
flecha(640, 330, 560, 282, color=AZUL, guion="6 5")  # 5 authorizer valida con Cognito (claves públicas)
numero(600, 300, 5, AZUL)
flecha(900, 420, 981, 300)            # 6 API -> Lambda
numero(940, 352, 6)
flecha(1215, 300, 1301, 220)          # 7 Lambda -> DynamoDB
numero(1258, 255, 7)
flecha(1430, 330, 1430, 366, color=AZUL, guion="6 5")  # 8 DynamoDB usa KMS
numero(1460, 348, 8, AZUL)
flecha(1215, 420, 1301, 600, color=AZUL, guion="6 5")  # 9 SSM
numero(1258, 515, 9, AZUL)

# Despliegue y logs
flecha(640, 865, 696, 865, color=GRIS5, ancho=2)
flecha(1100, 690, 1130, 786, color=GRIS5, ancho=2, guion="4 4")
flecha(770, 600, 1060, 786, color=GRIS5, ancho=2, guion="4 4")

defs = "".join(
    f'<marker id="punta-{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
    f'<path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
    for c in (VERDE, AZUL, GRIS5)
)

svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FUENTE}">'
    f"<defs>{defs}</defs>"
    f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>'
    + "".join(el)
    + "</svg>"
)

SALIDA.parent.mkdir(parents=True, exist_ok=True)
SALIDA.with_suffix(".svg").write_text(svg, encoding="utf-8")
cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(SALIDA.with_suffix(".png")), output_width=W * 2)
print("Generado:", SALIDA.with_suffix(".png"))
