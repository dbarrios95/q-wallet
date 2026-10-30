#!/usr/bin/env python3
"""Figura del perímetro del software de Q-Wallet: superficie de ataque expuesta a internet
(informe 3.1 y 3.6, Fase 4, delimitación del perímetro). Genera EVD-4-14 en SVG y PNG.

La idea de la figura: un solo punto de entrada desde internet (HTTPS 443 en API Gateway,
solo TLS 1.3, con el authorizer de Cognito); todo lo demás es privado y no se alcanza desde
internet. No hay SSH, ni base de datos pública, ni EC2/NAT, ni balanceadores abiertos.

Uso: python scripts/bloque4_diagrama_perimetro.py
Requiere: matplotlib y la fuente Liberation Sans (métricas de Arial).
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

RAIZ = Path(__file__).resolve().parent.parent
SVG = RAIZ / "docs/evidencias/EVD-4-14_perimetro.svg"
PNG = RAIZ / "docs/evidencias/EVD-4-14_perimetro.png"

FUENTE = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
fm.fontManager.addfont(FUENTE)
plt.rcParams["font.family"] = fm.FontProperties(fname=FUENTE).get_name()

AZUL = "#1f3b63"
GRIS = "#5b6670"
VERDE = "#1e6b45"
ROJO = "#9c2a2a"
CLARO = "#eef2f7"
BORDE_PRIV = "#8aa0bd"

fig, ax = plt.subplots(figsize=(9.2, 6.4))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")


def caja(x, y, w, h, texto, color_borde=AZUL, relleno="white", tam=10, negrita=False, color_texto="#15202b"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.6",
                                linewidth=1.4, edgecolor=color_borde, facecolor=relleno, zorder=3))
    ax.text(x + w / 2, y + h / 2, texto, ha="center", va="center", fontsize=tam,
            fontweight="bold" if negrita else "normal", color=color_texto, zorder=4)


def flecha(x1, y1, x2, y2, color=AZUL, estilo="-|>", ancho=1.6, guion=None):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=estilo, mutation_scale=16,
                                 linewidth=ancho, color=color, linestyle=guion or "solid", zorder=2))


# --- Zona de internet (no confiable) ---
caja(6, 80, 26, 12, "Atacante / Internet\n(sin credenciales)", color_borde=ROJO, relleno="#fbeeee", tam=10, negrita=True)
caja(6, 62, 26, 11, "App Android\n(cliente legítimo)", color_borde=GRIS, relleno="white", tam=10)

# --- Frontera TB2: borde de AWS, único punto expuesto ---
ax.add_patch(Rectangle((40, 54), 54, 42, linewidth=1.6, edgecolor=BORDE_PRIV,
                       facecolor=CLARO, zorder=1, linestyle=(0, (6, 4))))
ax.text(67, 92.5, "Nube AWS (us-east-1) — red privada", ha="center", va="center",
        fontsize=9.5, color=GRIS, style="italic", zorder=4)

caja(46, 74, 42, 13,
     "ÚNICA PUERTA EXPUESTA\nHTTPS 443 · API Gateway (solo TLS 1.3)\nAuthorizer de Cognito en las 18 rutas",
     color_borde=VERDE, relleno="#e9f3ee", tam=10, negrita=True, color_texto=VERDE)

# --- Detrás del borde: privado, sin acceso desde internet ---
caja(44, 60, 22, 9, "5 Lambdas\n(sin IP pública)", color_borde=AZUL, relleno="white", tam=9)
caja(69, 60, 21, 9, "DynamoDB + KMS\n+ SSM (privados)", color_borde=AZUL, relleno="white", tam=9)

# --- CI/CD por OIDC, sin llaves ---
caja(6, 44, 26, 9, "GitHub Actions\n(OIDC, sin llaves)", color_borde=GRIS, relleno="white", tam=9)

# Flechas de tráfico permitido
flecha(32, 68, 46, 80, color=VERDE)            # app -> puerta expuesta (443 TLS 1.3)
flecha(19, 80, 19, 73.5, color=ROJO)           # atacante -> app zone (conceptual)
flecha(32, 85, 46, 83, color=ROJO, guion=(0, (4, 3)))  # atacante -> puerta (rebota en 401/403)
flecha(60, 74, 55, 69, color=AZUL)             # puerta -> lambdas
flecha(66, 64.5, 69, 64.5, color=AZUL)         # lambdas -> datos
flecha(32, 48, 44, 62, color=GRIS, guion=(0, (4, 3)))  # github oidc -> aws

ax.text(39.5, 86.5, "401/403", ha="right", va="center", fontsize=8.5, color=ROJO, fontweight="bold")
ax.text(39, 74, "TLS 1.3", ha="right", va="center", fontsize=8.5, color=VERDE, fontweight="bold")

# --- Recuadro: lo que NO está expuesto ---
cerrado = ("Cerrado al exterior: sin SSH (22), sin RDP, sin bases de datos públicas,\n"
           "sin EC2 encendido ni NAT Gateway, sin balanceadores abiertos, sin dominio propio.\n"
           "Cognito (login administrado) queda fuera del alcance del pentest por política de AWS.")
ax.add_patch(FancyBboxPatch((6, 24), 88, 13, boxstyle="round,pad=0.5,rounding_size=1.6",
                            linewidth=1.2, edgecolor=GRIS, facecolor="#f7f8fa", zorder=3))
ax.text(50, 30.5, cerrado, ha="center", va="center", fontsize=9, color="#2b3540", zorder=4)

# Leyenda
ax.text(50, 16, "Superficie expuesta a internet = 1 endpoint HTTPS (TCP 443). El resto de la "
                "arquitectura es privado.", ha="center", va="center", fontsize=9.5,
        color=AZUL, fontweight="bold")

fig.tight_layout(pad=0.3)
fig.savefig(SVG, format="svg", bbox_inches="tight")
fig.savefig(PNG, format="png", dpi=200, bbox_inches="tight")
print("Generado:", SVG)
print("Generado:", PNG)
