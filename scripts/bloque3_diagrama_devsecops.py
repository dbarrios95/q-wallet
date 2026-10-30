"""Figura del flujo DevSecOps de Q-Wallet (EVD-3-16), para la sección 4.6.

Uso: python scripts/bloque3_diagrama_devsecops.py
Genera docs/evidencias/EVD-3-16_flujo_devsecops.png. Paleta de la app (CONTEXTO, ENTREGA_1).
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "docs/evidencias/EVD-3-16_flujo_devsecops.png"

AZUL = "#0B1F3A"
VERDE = "#00A86B"
GRIS = "#64748B"
BORDE = "#CBD5E1"
FONDO_ZONA = "#F1F5F9"
ROJO = "#B91C1C"

plt.rcParams["font.family"] = "DejaVu Sans"
for f in ("Liberation Sans", "Arial"):
    try:
        matplotlib.font_manager.findfont(f, fallback_to_default=False)
        plt.rcParams["font.family"] = f
        break
    except ValueError:
        pass

fig, ax = plt.subplots(figsize=(13, 6.2), dpi=200)
ax.set_xlim(0, 130)
ax.set_ylim(0, 62)
ax.axis("off")


def caja(x, y, w, h, titulo, detalle="", color=AZUL, relleno="white"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2", linewidth=1.3, edgecolor=color, facecolor=relleno))
    ax.text(x + w / 2, y + h - 2.3, titulo, ha="center", va="top", fontsize=8.6, fontweight="bold", color=color)
    if detalle:
        ax.text(x + w / 2, y + h - 5.0, detalle, ha="center", va="top", fontsize=7, color="#0F172A", linespacing=1.35)


def flecha(x1, y1, x2, y2, color=GRIS, estilo="-|>"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=estilo, mutation_scale=11, linewidth=1.2, color=color, shrinkA=0, shrinkB=0))


def zona(x, y, w, h, texto):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.5", linewidth=1, edgecolor=BORDE, facecolor=FONDO_ZONA, linestyle="--"))
    ax.text(x + 1.5, y + h - 1.2, texto, ha="left", va="top", fontsize=8, color=GRIS, fontweight="bold")


# Zona 1: pull request
zona(1, 4, 60, 56, "1. Pull request (rama → PR; main protegida)")
caja(3, 25, 12, 12, "Rama + PR", "código de\nservices/, mobile/,\ninfra/")
etapas = [
    ("Pruebas por control", "vitest 5.0.3 · tsc\n60 pruebas"),
    ("SAST Semgrep 1.179.0", "608 reglas públicas\n+ 7 propias"),
    ("SAST CodeQL", "security-extended\nJS/TS"),
    ("SCA", "npm audit + compuerta\nTrivy fs · SBOM"),
    ("Secretos", "gitleaks 8.30.1\ntodo el historial"),
]
for i, (t, d) in enumerate(etapas):
    y = 47.6 - i * 10.2
    caja(20, y, 19, 9.2, t, d)
    flecha(15.8, 31, 19.4, y + 4.6)
    flecha(39.6, y + 4.6, 43.2, 31)
caja(44, 23, 15, 16, "Compuertas", "Falla si hay:\nSAST grave\nSCA High/Critical\nsin excepción\nsecreto · prueba roja", color=ROJO)

# Zona 2: infraestructura y contenedores (mismo PR)
zona(63, 33, 66, 27, "2. Mismo PR: IaC y contenedores (infra.yml)")
caja(65, 41, 14, 12, "Checkov 3.3.22", "Terraform y\nDockerfile")
caja(81, 41, 14, 12, "5 imágenes", "multi-etapa\ndigest · usuario 1000")
caja(97, 41, 14, 12, "Prueba de humo", "runtime real\nGET /me → 401")
caja(113, 41, 14, 12, "Trivy 0.75.0", "HIGH/CRITICAL\ncon corrección")
for x in (79.6, 95.6, 111.6):
    flecha(x, 47, x + 1.2, 47)
caja(65, 35.2, 62, 4.6, "Plan de Terraform con rol de solo lectura (OIDC) → comentario en el PR", color=GRIS)

# Zona 3: merge y despliegue
zona(63, 4, 66, 26, "3. Merge en main (aprobación de Daniel)")
caja(65, 10, 18, 14, "Revisión del plan", "se detiene si borra\no reemplaza algo\nno aprobado")
caja(87, 10, 18, 14, "Despliegue", "OIDC, rol\nqwallet-gha-despliegue\nentorno dev")
caja(109, 10, 18, 14, "Verificación AWS", "TLS 1.3 · IAM\ncifrado · Cognito\nissue de evidencias", color=VERDE)
flecha(83.6, 17, 86.4, 17)
flecha(105.6, 17, 108.4, 17)
flecha(59.6, 31, 64.4, 17, color=VERDE)
ax.text(63.5, 26, "todo en verde", fontsize=7, color=VERDE, ha="left")

ax.text(1, 1.2, "Además: revisión semanal (lunes) del mismo flujo sobre main = gestión continua de vulnerabilidades (5.5).", fontsize=7.5, color=GRIS)
fig.savefig(SALIDA, bbox_inches="tight", facecolor="white")
print("Generado:", SALIDA)
