"""Ajustes de cierre del informe final para la entrega del 28-nov-2026.

Uso (sobre el Word ya ensamblado; después correr entrega1_estilos.py y entrega1_indice.py):
    python scripts/final_entrega.py docs/entregas/Informe_Final_QWallet.docx

Cambios (decisiones de Daniel del 25-nov-2026):
- La presentación final es un recorrido por la app funcionando (no solo diapositivas): OE5, la
  restricción de la Tabla 5 y la introducción de 1.5 ya no dicen "sin demostración en vivo";
  lo que no se repite en vivo son las pruebas ofensivas.
- Se quitan los dos [VERIFICAR]: costo de CloudWatch como estimado y origen de files/tcb
  como no identificado (lo probado es que existe antes de iniciar sesión).
- APA 7: la lista de referencias empieza en una página nueva.
- Tablas 53 y 59 pasan de 8 a 9 pt (CONTEXTO, sección 9: 8 pt solo en la Tabla 12).
Requiere python-docx.
"""
import sys

import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

DOCX = sys.argv[1]

REEMPLAZOS = [
    ("y presentarlo con evidencias grabadas, sin demostración en vivo, en la entrega final.",
     "y presentarlo en la entrega final con un recorrido por la app en funcionamiento, respaldado "
     "por las evidencias grabadas de cada prueba."),
    ("dado que la evaluación no contempla una demostración en vivo.",
     "dado que las pruebas ofensivas no se repiten en vivo durante la presentación."),
    ("Presentación sin demostración en vivo",
     "Pruebas ofensivas sin repetición en vivo"),
    ("Toda prueba debe quedar respaldada con captura o video identificado como evidencia (EVD).",
     "Toda prueba debe quedar respaldada con captura o video identificado como evidencia (EVD); "
     "en la presentación se muestra la app en funcionamiento, no los ataques."),
    ("su costo se estima en uno o dos dólares al mes por las métricas personalizadas "
     "[VERIFICAR con la factura de noviembre].",
     "su costo se estima en uno o dos dólares al mes por las métricas personalizadas; es una "
     "estimación, porque la factura de noviembre se cierra después de esta entrega."),
    ("existe desde antes de iniciar sesión y no es de la sesión [VERIFICAR origen];",
     "existe desde antes de iniciar sesión, por lo que no pertenece a la sesión (su origen no "
     "se identificó);"),
]


def parrafos(d):
    # Todos los párrafos del cuerpo, también los de las celdas, una sola vez cada uno.
    for p in d.element.body.iter(qn("w:p")):
        yield Paragraph(p, None)


def reemplazar(d):
    hechos = {a: 0 for a, _ in REEMPLAZOS}
    for p in parrafos(d):
        for a, b in REEMPLAZOS:
            if a in p.text:
                for r in p.runs:
                    if a in r.text:
                        r.text = r.text.replace(a, b)
                        hechos[a] += 1
                        break
                else:
                    raise SystemExit(f"El texto está partido en varias corridas: {a[:50]}")
    faltan = [a[:60] for a, n in hechos.items() if n == 0]
    if faltan:
        raise SystemExit(f"No se encontró: {faltan}")


def salto_referencias(d):
    for p in d.paragraphs:
        if p.text.strip() == "6.6 Referencias" and p.style.name.lower().startswith(("heading", "título")):
            ppr = p._p.get_or_add_pPr()
            if ppr.find(qn("w:pageBreakBefore")) is None:
                pb = OxmlElement("w:pageBreakBefore")
                ps = ppr.find(qn("w:pStyle"))
                (ps.addnext(pb) if ps is not None else ppr.insert(0, pb))
            return
    raise SystemExit("No se encontró el título 6.6 Referencias")


def tablas_9pt(d):
    cambiadas = 0
    cuerpo = d.element.body
    ultimo = ""
    for el in cuerpo:
        if el.tag == qn("w:p"):
            t = "".join(x.text or "" for x in el.iter(qn("w:t"))).strip()
            if t:
                ultimo = t
        elif el.tag == qn("w:tbl") and (ultimo.startswith("Matriz de decisiones por riesgo")
                                        or ultimo.startswith("Trazabilidad de las 41 amenazas")):
            for tag in ("w:sz", "w:szCs"):
                for s in el.iter(qn(tag)):
                    if s.get(qn("w:val")) == "16":
                        s.set(qn("w:val"), "18")
            cambiadas += 1
    if cambiadas != 2:
        raise SystemExit(f"Se esperaban 2 tablas a 9 pt y se encontraron {cambiadas}")


def main():
    d = docx.Document(DOCX)
    reemplazar(d)
    salto_referencias(d)
    tablas_9pt(d)
    d.save(DOCX)
    print("Listo:", DOCX)


if __name__ == "__main__":
    main()
