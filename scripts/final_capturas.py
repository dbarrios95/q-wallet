"""Inserta en el Anexo D las capturas de consola de AWS y GitHub tomadas por Daniel al cierre.

Uso (sobre el Word que deja final_entrega.py; después correr entrega1_estilos.py y entrega1_indice.py):
    python scripts/final_capturas.py docs/entregas/Informe_Final_QWallet.docx

Las capturas están en docs/evidencias/final/CAP-xx_*.png, con el número de cuenta, el ARN y el ID
de la llave tapados. Se insertan después de la última figura del Anexo D, antes de 6.6 Referencias,
con el mismo formato APA 7 de las figuras existentes (número en negrita, título en cursiva, imagen
y nota). Si falta una captura, se omite y la numeración se ajusta. Agrega además una frase en 4.5
con el resultado de Checkov del 10-nov (337 / 0 / 38), que es el que muestra la captura CAP-05.
Requiere python-docx.
"""
import copy
import re
import sys
from pathlib import Path

import docx
from docx.oxml.ns import qn
from docx.shared import Inches
from docx.text.paragraph import Paragraph
from PIL import Image

DOCX = sys.argv[1]
EV = Path(__file__).resolve().parent.parent / "docs/evidencias/final"
ANCHO, ALTO = 6.5, 4.2  # pulgadas disponibles (márgenes de 2.54 cm)

CAPTURAS = [
    ("CAP-01_devsecops_verde.png", "Flujo devsecops en verde sobre la rama main",
     "Ejecución programada n.º 97 del flujo devsecops, del 23 de noviembre de 2026, terminada con "
     "éxito en 1 min 28 s. Complementa la sección 4.6 y la Tabla 41."),
    ("CAP-02_pr60_devsecops.png", "Resultado de las compuertas DevSecOps en el PR #60",
     "Comentario automático del flujo sobre el commit 2003036 (10 de noviembre de 2026): pruebas por "
     "control, pentest de caja gris, Semgrep, CodeQL, npm audit con Trivy, gitleaks, OWASP "
     "Dependency-Check y Snyk, todos con resultado success. Complementa las secciones 3.4 y 3.5."),
    ("CAP-05_checkov_pr60.png", "Resultado de Checkov sobre el Terraform en el PR #60",
     "Revisión estática del 10 de noviembre de 2026: 337 verificaciones aprobadas, 0 fallidas y 38 "
     "omitidas con motivo. Complementa la sección 4.5 y la Tabla 40."),
    ("CAP-04_zap_issue.png", "Issue «Evidencias Pentest» con los resultados de la caja negra",
     "El flujo pentest.yml publica en este issue, sin número de cuenta ni ARN, el perímetro (EVD-4-01), "
     "el análisis base de ZAP (EVD-4-02) y Prowler (EVD-3-09) de la ejecución del 30 de octubre de "
     "2026. Complementa la sección 3.1 y la Tabla 24."),
    ("CAP-06_cognito_mfa.png", "MFA obligatorio con aplicación de autenticación en Amazon Cognito",
     "Grupo de usuarios qwallet-usuarios: inicio de sesión con correo, MFA obligatorio (Require MFA) "
     "y método de aplicación de autenticación (TOTP). Complementa la sección 4.1.2 y la Tabla 9."),
    ("CAP-07_apigw_tls13.png", "Política de seguridad TLS 1.3 de la API en API Gateway",
     "La API qwallet-api usa la política SecurityPolicy_TLS13_1_3_2025_09 en modo de acceso estricto. "
     "Complementa la sección 4.2.2."),
    ("CAP-08_kms_rotacion.png", "Llave administrada por el cliente alias/qwallet-datos en AWS KMS",
     "Llave simétrica habilitada para cifrar y descifrar, con el ID tapado. Complementa la sección "
     "4.2.2 y la Tabla 35."),
    ("CAP-09_dynamodb_cifrado.png", "Cifrado de la tabla qwallet-cuentas con la llave del cliente",
     "La tabla tiene la protección contra borrado activada y se cifra con la llave administrada por "
     "el cliente en AWS KMS; el ARN de la llave está tapado. Captura del 27 de noviembre de 2026. "
     "Complementa la sección 4.2.2 y la Tabla 35."),
    ("CAP-10_alarmas.png", "Alarmas de seguridad del SIEM en Amazon CloudWatch",
     "Nueve alarmas con su acción habilitada; la décima, qwallet-waf-bloqueos, solo existe mientras el "
     "WAF está encendido. qwallet-uso-root y qwallet-aws-no-autorizado pasaron a «In alarm» el 27 de "
     "noviembre de 2026 a las 16:29 y 16:33 UTC, a la hora en que se tomaron estas capturas en la "
     "consola. Complementa la sección 5.4 y la Tabla 48."),
    ("CAP-11_panel.png", "Panel qwallet-seguridad en Amazon CloudWatch",
     "Panel personalizado del SIEM, actualizado por última vez el 31 de octubre de 2026. Complementa la "
     "sección 5.4."),
]

FRASE_45 = ("En la última revisión antes del cierre (PR #60, 10 de noviembre de 2026), con la "
            "infraestructura completa, Checkov aprobó 337 verificaciones, 0 fallaron y 38 "
            "se omitieron con motivo ({fig}).")


def texto(p):
    return "".join(t.text or "" for t in p.iter(qn("w:t")))


def poner_texto(p, nuevo):
    """Deja el texto en la primera corrida con texto y vacía las demás (conserva el formato)."""
    runs = [r for r in p.iter(qn("w:r")) if r.find(qn("w:t")) is not None]
    for i, r in enumerate(runs):
        for t in r.findall(qn("w:t")):
            t.text = nuevo if i == 0 else ""
            t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            nuevo = "" if i == 0 else nuevo


def main():
    d = docx.Document(DOCX)
    cuerpo = d.element.body
    if any("CAP-01" in texto(p) or "devsecops en verde" in texto(p) for p in cuerpo.iter(qn("w:p"))):
        raise SystemExit("Las capturas ya están insertadas: partir del Word de final_entrega.py")
    ps = list(cuerpo.iter(qn("w:p")))
    nums = [int(m.group(1)) for p in ps if (m := re.fullmatch(r"Figura (\d+)", texto(p).strip()))]
    ultima = max(nums)
    i = [k for k, p in enumerate(ps) if texto(p).strip() == f"Figura {ultima}"][0]
    p_num, p_tit, p_img, p_nota = ps[i], ps[i + 1], ps[i + 2], ps[i + 3]
    assert p_img.findall(".//" + qn("w:drawing")) and texto(p_nota).startswith("Nota.")
    ancla = p_nota
    disponibles = [c for c in CAPTURAS if (EV / c[0]).exists()]

    # Párrafo de introducción con el formato de un párrafo de cuerpo (el de la intro del Anexo D).
    intro_modelo = next(p for p in ps if texto(p).startswith("Este anexo reúne las capturas"))
    intro = copy.deepcopy(intro_modelo)
    n0 = ultima + 1
    poner_texto(intro, f"Las Figuras {n0} a {ultima + len(disponibles)} son capturas de GitHub y de la consola "
                       "de AWS (región us-east-1) tomadas al cierre del proyecto, el 27 de noviembre de 2026, "
                       "con el número de cuenta, los ARN y el ID de la llave tapados.")
    ancla.addnext(intro)
    ancla = intro

    fig_checkov = None
    for k, (archivo, titulo, nota) in enumerate(disponibles):
        n = n0 + k
        if archivo.startswith("CAP-05"):
            fig_checkov = f"Figura {n}"
        a = copy.deepcopy(p_num); poner_texto(a, f"Figura {n}")
        b = copy.deepcopy(p_tit); poner_texto(b, titulo)
        c = copy.deepcopy(p_nota)
        runs = [r for r in c.iter(qn("w:r")) if r.find(qn("w:t")) is not None]
        runs[0].find(qn("w:t")).text = "Nota."
        for r in runs[1:]:
            for t in r.findall(qn("w:t")):
                t.text = ""
        runs[1].find(qn("w:t")).text = " " + nota
        runs[1].find(qn("w:t")).set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        # Imagen: párrafo nuevo con el mismo formato del párrafo de imagen, tamaño ajustado.
        img = copy.deepcopy(p_img)
        for r in list(img.findall(qn("w:r"))):
            img.remove(r)
        w, h = Image.open(EV / archivo).size
        ancho = min(ANCHO, ALTO * w / h)
        Paragraph(img, d._body).add_run().add_picture(str(EV / archivo), width=Inches(ancho))
        for el in (a, b, img, c):
            ancla.addnext(el)
            ancla = el

    # Frase de 4.5 con el último resultado de Checkov.
    if fig_checkov:
        p45 = next(p for p in cuerpo.iter(qn("w:p")) if "282 verificaciones pasaron, 0 fallaron y 39" in texto(p))
        runs = [r for r in p45.iter(qn("w:r")) if r.find(qn("w:t")) is not None]
        t = runs[-1].find(qn("w:t"))
        t.text = (t.text or "").rstrip() + " " + FRASE_45.format(fig=fig_checkov)
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")

    d.save(DOCX)
    print(f"Insertadas {len(disponibles)} capturas como Figuras {n0} a {ultima + len(disponibles)}")
    faltan = [c[0] for c in CAPTURAS if c not in disponibles]
    if faltan:
        print("Faltan:", ", ".join(faltan))


if __name__ == "__main__":
    main()
