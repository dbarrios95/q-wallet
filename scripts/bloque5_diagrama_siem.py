"""Figura del SIEM en CloudWatch (bloque 5, sección 5.3): EVD-5-08_siem.{svg,png}.

Uso: python scripts/bloque5_diagrama_siem.py
Fuentes -> reglas de correlación (filtros de métrica y consultas) -> alarmas -> SNS -> correo,
y tablero. Paleta de la app (ENTREGA_1, sección 1). Requiere cairosvg.
"""
from pathlib import Path

import cairosvg

SALIDA = Path(__file__).resolve().parent.parent / "docs/evidencias/EVD-5-08_siem"
F = 'font-family="Arial,Helvetica,sans-serif"'
AZUL, VERDE, GRIS, BORDE, TEXTO, SUAVE = "#0B1F3A", "#00A86B", "#F8FAFC", "#CBD5E1", "#0F172A", "#64748B"

o = ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="560" viewBox="0 0 1100 560">',
     '<rect width="1100" height="560" fill="#FFFFFF"/>',
     '<defs><marker id="f" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
     f'<path d="M0,0 L10,5 L0,10 z" fill="{SUAVE}"/></marker></defs>']


def caja(x, y, w, h, titulo, lineas, fondo=GRIS, borde=BORDE, color_t=TEXTO):
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fondo}" stroke="{borde}" stroke-width="1.5"/>')
    o.append(f'<text x="{x + 14}" y="{y + 24}" {F} font-size="14" font-weight="700" fill="{color_t}">{titulo}</text>')
    for k, l in enumerate(lineas):
        o.append(f'<text x="{x + 14}" y="{y + 46 + 18 * k}" {F} font-size="12" fill="{SUAVE if color_t == TEXTO else "#CBD5E1"}">{l}</text>')


def flecha(x1, y1, x2, y2):
    o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{SUAVE}" stroke-width="1.6" marker-end="url(#f)"/>')


def columna(x, texto):
    o.append(f'<text x="{x}" y="34" {F} font-size="13" font-weight="700" fill="{VERDE}">{texto}</text>')


columna(30, "1. FUENTES (CloudWatch Logs, cifrado con la CMK)")
columna(410, "2. CORRELACIÓN")
columna(760, "3. ALERTA Y RESPUESTA")

fuentes = [
    ("CloudTrail (toda la cuenta)", ["Administración + invocaciones de Lambda", "/aws/cloudtrail/qwallet-auditoria"]),
    ("API Gateway, log de acceso", ["IP, usuario (sub), ruta, estado, WAF", "/aws/apigateway/qwallet-api"]),
    ("5 Lambdas, logs JSON", ["evento, código de rechazo, correlationId", "sin tokens ni PII (CTRL-09)"]),
    ("AWS WAF (cuando está encendido)", ["acción y regla que decidió", "aws-waf-logs-qwallet"]),
]
for k, (t, ls) in enumerate(fuentes):
    y = 52 + 112 * k
    caja(30, y, 330, 92, t, ls)
    flecha(360, y + 46, 408, y + 46)

caja(410, 60, 300, 196, "14 reglas (filtros de métrica)", [
    "Aplicación: PIN bloqueado o incorrecto,",
    "acceso prohibido, entrada inválida,",
    "error no controlado",
    "Perímetro: 401, 429, bloqueo del WAF",
    "Cuenta (CIS): IAM negado, root, consola",
    "sin MFA, auditoría/KMS/SIEM, IAM, Cognito",
    "→ métricas QWallet/Seguridad",
])
caja(410, 280, 300, 160, "5 consultas de correlación", [
    "Por correlationId (API Gateway + Lambda)",
    "Rechazos por usuario e IP (BOLA, PIN)",
    "IPs sospechosas (401 + 429 + WAF)",
    "Llamadas negadas por IAM, por rol",
    "Bloqueos del WAF por regla e IP",
])
flecha(710, 158, 758, 158)
flecha(710, 360, 758, 420)

caja(760, 60, 310, 196, "10 alarmas de CloudWatch", [
    "Crítica: root, consola sin MFA,",
    "cambios a auditoría, KMS o al SIEM",
    "Alta: PIN bloqueado, acceso prohibido,",
    "llamadas negadas por IAM",
    "Media: errores, ráfagas de 401 y 429,",
    "bloqueos del WAF",
], fondo=AZUL, borde=AZUL, color_t="#FFFFFF")
flecha(915, 256, 915, 290)
caja(760, 292, 310, 70, "Tema SNS cifrado → correo", ["qwallet-alertas (solo alarmas de la cuenta)"])
caja(760, 380, 310, 70, "Tablero qwallet-seguridad", ["alarmas, reglas por fuente y consulta"])
caja(760, 468, 310, 70, "Respuesta (sección 5.4)", ["procedimiento por alarma, dueño: I1"])

o.append(f'<text x="30" y="545" {F} font-size="12" fill="{SUAVE}">Sin servidores propios: el SIEM usa servicios '
         'administrados de la cuenta (decisión del 31-oct-2026; Wazuh queda en el roadmap).</text>')
o.append("</svg>")
SALIDA.with_suffix(".svg").write_text("".join(o), encoding="utf-8")
cairosvg.svg2png(url=str(SALIDA.with_suffix(".svg")), write_to=str(SALIDA.with_suffix(".png")), scale=2)
print("Figura:", SALIDA.with_suffix(".png"))
