"""Ensambla el informe final de Q-Wallet (secciones 0 a 6) a partir de los Word de cada bloque.

Uso (desde la raíz del repo):
    python scripts/bloque6_word.py
    python scripts/entrega1_estilos.py docs/entregas/Final_Seccion_6_Dictamen.docx
    python scripts/final_ensamblar.py
    python scripts/entrega1_estilos.py docs/entregas/Informe_Final_QWallet.docx
    python scripts/entrega1_indice.py docs/entregas/Informe_Final_QWallet.docx

Qué hace:
1. Parte del informe de la Entrega 1 (portada, resumen, índice, secciones 1 y 2), cambia la portada,
   reescribe el resumen ejecutivo para todo el proyecto y quita su lista de referencias.
2. Agrega las partes de los Word por bloque en el orden del esquema del enunciado (Opción A):
   3.1-3.3 (pentest), 3.4-3.5 (DevSecOps), 3.6 (pentest), 4.1-4.2 (Entrega 2), 4.3-4.4 (DevSecOps),
   4.5 (Entrega 2), 4.6 (DevSecOps), 5 (operaciones) y 6 (dictamen).
3. Actualiza los textos que quedaron viejos al juntar las entregas (estado de REQ-01, 04 y 05,
   excepciones renovadas, alarma ajustada, frases de "este bloque").
4. Renumera tablas y figuras por orden de aparición y corrige todas sus referencias en el texto.
5. Junta las referencias de todas las partes en 6.6 (APA 7, sin duplicados, en orden alfabético).
6. Reconstruye el índice general (campo TOC); los números de página los pone entrega1_indice.py.
Cada reemplazo de texto exige el número esperado de coincidencias: si un Word no es el esperado,
el script se detiene sin guardar. Requiere python-docx, docxcompose y lxml.
"""
import copy
import re
import sys
import unicodedata
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docxcompose.composer import Composer
from lxml import etree

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import entrega1_ensamblar as e1  # noqa: E402

E = RAIZ / "docs/entregas"
F_E1 = E / "Entrega1_Informe_QWallet.docx"
F_E2 = E / "Entrega2_Seccion_4_Arquitectura_Controles.docx"
F_PEN = E / "Final_Secciones_3-1_3-2_3-3_3-6_Pentest.docx"
F_DEV = E / "Final_Secciones_3-4_3-5_4-3_4-4_4-6_DevSecOps.docx"
F_OPS = E / "Final_Secciones_5-1_a_5-6_Operaciones.docx"
F_D6 = E / "Final_Seccion_6_Dictamen.docx"
SALIDA = Path(sys.argv[1]) if len(sys.argv) > 1 else E / "Informe_Final_QWallet.docx"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def texto(el):
    return "".join(t.text or "" for t in el.iter(qn("w:t")))


def estilo(el):
    ppr = el.find(qn("w:pPr"))
    st = ppr.find(qn("w:pStyle")) if ppr is not None else None
    return st.get(qn("w:val")) if st is not None else ""


def es_titulo(el, prefijo):
    return el.tag == qn("w:p") and estilo(el).startswith("Heading") and texto(el).strip().startswith(prefijo)


def indice(cuerpo, prefijo):
    hits = [i for i, el in enumerate(cuerpo) if es_titulo(el, prefijo)]
    if len(hits) != 1:
        raise SystemExit(f"Título {prefijo!r}: se esperaba 1 y hay {len(hits)}")
    return hits[0]


def parte(ruta, desde, hasta):
    """Documento con los elementos del cuerpo desde el título `desde` (o un índice) hasta antes de `hasta`."""
    d = Document(str(ruta))
    cuerpo = d.element.body
    hijos = [el for el in cuerpo if el.tag != qn("w:sectPr")]
    i = desde if isinstance(desde, int) else indice(hijos, desde)
    j = len(hijos) if hasta is None else (hasta if isinstance(hasta, int) else indice(hijos, hasta))
    for k, el in enumerate(hijos):
        if not i <= k < j:
            cuerpo.remove(el)
    return d


def referencias(ruta, titulo):
    """Párrafos de la lista de referencias de un Word (después del título dado), y los quita."""
    d = Document(str(ruta))
    hijos = list(d.element.body)
    i = max(k for k, el in enumerate(hijos) if es_titulo(el, titulo))
    return [copy.deepcopy(el) for el in hijos[i + 1:] if el.tag == qn("w:p") and texto(el).strip()]


# ------------------------------------------------------------ reemplazos de texto
def reemplazar(doc, viejo, nuevo, n=1):
    """Reemplaza `viejo` por `nuevo` en párrafos (también en tablas). Primero cuenta: si no hay
    exactamente `n` coincidencias, no toca nada y se detiene. Si el texto cruza varias corridas,
    deja el párrafo en la primera corrida (con el formato de esa corrida)."""
    variantes = [viejo] if "-" not in viejo else [viejo, viejo.replace("-", "‑")]
    parrafos = [p for p in doc.element.body.iter(qn("w:p")) if any(v in texto(p) for v in variantes)]
    cuenta = sum(texto(p).count(v) for p in parrafos for v in variantes)
    if cuenta != n:
        donde = " | ".join(texto(p)[:60] for p in parrafos)
        raise SystemExit(f"Se esperaban {n} coincidencias y hay {cuenta}: {viejo[:90]!r} -> {donde}")
    for p in parrafos:
        full = texto(p)
        v = next(x for x in variantes if x in full)
        nv = nuevo if v == viejo else nuevo.replace("-", "‑")
        ts = list(p.iter(qn("w:t")))
        for t in ts:
            if t.text and v in t.text:
                t.text = t.text.replace(v, nv)
        if v in texto(p):
            ts[0].text = full.replace(v, nv)
            ts[0].set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            for t in ts[1:]:
                t.text = ""


def parrafo_como(modelo, txt):
    p = copy.deepcopy(modelo)
    rs = p.findall(qn("w:r"))
    for r in rs[1:]:
        p.remove(r)
    ts = rs[0].findall(qn("w:t"))
    for t in ts[1:]:
        rs[0].remove(t)
    ts[0].text = txt
    ts[0].set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return p


RESUMEN = [
    "Q-Wallet es una billetera digital ficticia para Android, con dinero simulado en quetzales, que "
    "funciona sobre servicios de Amazon Web Services: API Gateway, Cognito, Lambda y DynamoDB. En "
    "este proyecto asumimos el rol de arquitectos de seguridad y recorrimos las seis fases del ciclo "
    "de vida continuo de seguridad de aplicaciones: planificación y modelado de amenazas, diseño de "
    "la arquitectura cloud, desarrollo con DevSecOps, verificación con pruebas de intrusión, "
    "despliegue endurecido y operación con WAF, RASP y SIEM. Construimos la aplicación segura desde "
    "el diseño y usamos las pruebas para demostrar que cada control funciona.",
    "Siguiendo ISO/IEC 27005:2022, inventariamos 28 activos según ISO/IEC 27001:2022 y modelamos 41 "
    "amenazas con STRIDE, valoradas con DREAD sobre una matriz de probabilidad por impacto de 5 × 5 y "
    "repartidas en las siete capas de defensa en profundidad. Sin controles, 18 riesgos eran "
    "críticos y la suma de los puntajes llegaba a 580. Para tratarlos definimos 23 controles.",
    "Desplegamos toda la arquitectura con Terraform desde GitHub Actions, con identidad temporal "
    "(OIDC) y sin llaves guardadas. Cada cambio pasa por análisis estático de código (Semgrep y "
    "CodeQL), análisis de dependencias, búsqueda de secretos, revisión de la infraestructura como "
    "código con Checkov (282 verificaciones aprobadas y 0 fallidas) y escaneo de las imágenes con "
    "Trivy; esas compuertas detuvieron dos veces el trabajo por vulnerabilidades publicadas sin "
    "cambios en nuestro código. Los datos se cifran con una llave KMS propia y la API solo acepta "
    "TLS 1.3.",
    "Las pruebas de caja negra, gris y blanca bloquearon 11 de los 13 casos de abuso, las 18 pruebas "
    "del OWASP API Security Top 10 y los nueve ataques lanzados contra el WAF. En el teléfono, "
    "freeRASP detectó el emulador, el root y la instrumentación con Frida. Registramos 16 hallazgos "
    "reales; el más importante fue que la fijación de certificados no protegía la conexión de la "
    "app, algo que solo apareció al interceptarla en un emulador y que corregimos y volvimos a "
    "probar. El SIEM en CloudWatch correlaciona los eventos con 14 reglas y avisa por correo.",
    "Con los controles desplegados y probados, el riesgo residual verificado quedó en 0 críticos, 1 "
    "alto, 26 medios y 14 bajos, y la suma de los puntajes bajó de 580 a 208, una reducción del "
    "64 %. El único riesgo alto (RSK-11, saturación de la API) se aceptó de forma temporal porque el "
    "WAF permanente excede el presupuesto. Nuestro dictamen es favorable para la versión evaluada, "
    "con tres condiciones antes de manejar dinero real: WAF permanente, inicio de sesión completo "
    "en la app y actualización a Expo SDK 58.",
]

# Textos que cambian al juntar las entregas: (archivo, viejo, nuevo, coincidencias)
EDICIONES = [
    # portada
    ("E1", "Entrega 1: Selección y Planificación; Activos y Riesgos", "Informe final", 1),
    # sección 1 y 2: plazos y proyecciones que ya se cumplieron
    ("E1", "El plazo de OE2 a OE5 es la entrega final del curso, cuya fecha aún no ha sido publicada.",
     "El plazo de OE2 a OE5 es la entrega final del curso, el 28 de noviembre de 2026; el resultado de cada objetivo está en la sección 6.1.", 1),
    ("E1", "Esta conclusión es provisional: el dictamen sobre el riesgo residual lo emitiremos en la entrega final, con la evidencia de las pruebas de los controles y de los casos de abuso.",
     "Esta conclusión era provisional: el riesgo residual verificado con las pruebas de los controles y de los casos de abuso está en la sección 5.6, y el dictamen, en la sección 6.1.", 1),
    ("E1", "Proyección pendiente de verificación con pruebas.",
     "Proyección; el residual verificado con pruebas está en la sección 5.6 (Figura 13).", 1),
    ("E1", "y está pendiente de verificación con pruebas", "y se verificó con pruebas en la sección 5.6", 1),
    # 4.2.3: los tres requisitos que dependían del código ya están cumplidos y probados
    ("E2", "La columna Estado separa lo que ya está en la infraestructura desplegada de lo que se implementa en el código de los servicios y de la app en la fase de desarrollo.",
     "La columna Estado muestra cómo quedó cada requisito al cierre del proyecto. Once se cumplieron en la infraestructura desde el primer despliegue; los tres que dependían del código (REQ-01, REQ-04 y REQ-05) se cumplieron en las fases siguientes y se probaron con ataques (secciones 3.2 y 5.2).", 1),
    ("E2", "Infraestructura lista; pinning en la app pendiente", "Cumplido: el pinning rechazó un MITM con la CA del atacante en el sistema (EVD-4-08, tras HAL-13)", 1),
    ("E2", "Tabla lista; lógica en desarrollo", "Cumplido: bloqueo al quinto intento con 423 (CA-02, EVD-4-04)", 1),
    ("E2", "En desarrollo", "Cumplido: 404 o 403 al pedir una cuenta ajena (CA-01, EVD-4-03)", 1),
    ("E2", "El escaneo de las imágenes con Trivy se agrega en la fase de desarrollo, cuando existan las imágenes reales de los servicios.",
     "El escaneo de las imágenes con Trivy está en la sección 3.5.", 1),
    ("E2", "[EVIDENCIA PENDIENTE: se genera en el primer despliegue.]",
     "Resultado: el despliegue del 30 de octubre de 2026 pasó esta prueba sin fallas.", 2),
    # sección 3: introducciones de las entregas parciales
    ("DEV", "Esta parte del informe reúne las pruebas que hicimos sobre el código y sus dependencias durante la Fase 3 del enunciado (desarrollo seguro y automatización DevSecOps). Las secciones 3.4 y 3.5 presentan el análisis estático de código (SAST) y el análisis de composición de software (SCA). Las pruebas de penetración de caja negra y gris, la evaluación OWASP API Top 10 y la evaluación de la arquitectura cloud (secciones 3.1, 3.2, 3.3 y 3.6) corresponden a la Fase 4 y se agregan al informe cuando terminen.",
     "Esta sección reúne las pruebas que hicimos sobre la aplicación, su código y la nube. Las secciones 3.1 a 3.3 corresponden a la Fase 4 del enunciado: el pentest de caja negra desde internet, el de caja gris y blanca contra los controles y la evaluación OWASP API Top 10. Las secciones 3.4 y 3.5 corresponden a la Fase 3 (desarrollo seguro y automatización DevSecOps): el análisis estático de código (SAST) y el análisis de composición de software (SCA). La sección 3.6 evalúa la arquitectura cloud.", 1),
    ("PEN", "Las secciones 3.1, 3.2, 3.3 y 3.6 completan la Evaluación de seguridad (Fase 4 del enunciado) con las pruebas ofensivas y defensivas sobre la aplicación ya construida. ", "", 1),
    ("PEN", " Las secciones 3.4 y 3.5 (SAST y SCA) se entregaron con el bloque anterior.", "", 1),
    ("DEV", "La Tabla 30 resume la última ejecución sobre el código del bloque 3.", "La Tabla 30 resume la ejecución sobre el código de la Fase 3.", 1),
    ("DEV", "en este bloque reforzamos", "en esta fase reforzamos", 1),
    ("DEV", "Lo configurado en el bloque 3 se aplica", "Lo configurado en la Fase 3 se aplica", 1),
    # excepciones de SCA renovadas el 10-nov-2026 (decisión de Daniel)
    ("DEV", "y vencen el 28 de noviembre de 2026.",
     "y vencían el 28 de noviembre de 2026; el 10 de noviembre el dueño del riesgo las renovó hasta el 31 de enero de 2027, plazo para corregirlas con Expo SDK 58 (sección 6.3).", 1),
    ("DEV", "Aceptar hasta el 28-nov-2026: corregirlo exige Expo SDK 58", "Aceptar hasta el 31-ene-2027 (renovado el 10-nov): corregirlo exige Expo SDK 58", 1),
    ("OPS", "Las excepciones temporales vencen el 28 de noviembre de 2026: si no se corrigen antes, la compuerta vuelve a fallar.",
     "Las excepciones temporales se renovaron el 10 de noviembre hasta el 31 de enero de 2027: si no se corrigen antes, la compuerta vuelve a fallar.", 1),
    ("OPS", "Corregidos; HAL-02 aceptado hasta el 28-nov", "Corregidos; HAL-02 aceptado hasta el 31-ene-2027", 1),
    # alarma aws-no-autorizado ajustada el 10-nov-2026 (PR #60)
    ("OPS", "Ajuste pendiente: la alarma aws-no-autorizado también salta en los planes de los pull request porque el rol de solo lectura del plan no puede descifrar algunos valores; se excluirá ese rol igual que el de Prowler.",
     "Ajuste del 10 de noviembre: la alarma aws-no-autorizado también saltaba en los planes de los pull request porque el rol de solo lectura del plan no puede descifrar algunos valores; ahora la regla ignora solo las negaciones de KMS de ese rol, y cualquier otra negación suya sigue alertando.", 1),
    ("OPS", "excluye el escaneo autorizado de Prowler", "excluye el escaneo autorizado de Prowler y las negaciones de KMS del rol de plan", 1),
    # citas de las referencias que la sección del bloque 3 listaba sin citar en el texto
    ("DEV", "sobre un archivo con casos buenos y malos; las siete pasaron.", "sobre un archivo con casos buenos y malos (Semgrep, s. f.); las siete pasaron.", 1),
    ("DEV", "hasta funciones peligrosas (análisis de flujo).", "hasta funciones peligrosas (análisis de flujo; GitHub, s. f.).", 1),
    ("DEV", "para las imágenes usamos Trivy.", "para las imágenes usamos Trivy (Aqua Security, s. f.).", 1),
    ("DEV", "publicado el 1 de octubre;", "publicado el 1 de octubre (GitHub, 2026);", 1),
    ("DEV", "simulador local de la Runtime API de Lambda,", "simulador local de la Runtime API de Lambda (AWS, s. f.-h),", 1),
    ("DEV", "MASVS = OWASP Mobile Application Security Verification Standard 2.1.0.", "MASVS = OWASP Mobile Application Security Verification Standard 2.1.0 (OWASP Mobile Application Security Project, 2024).", 1),
]


# ------------------------------------------------------------ renumeración
REF = re.compile(r"\b(Tablas?|Figuras?)(\s+)(\d+(?:(?:\s*,\s*|\s+y\s+|\s+e\s+|\s+a\s+)\d+)*)")


def numeros(seq):
    partes = re.split(r"(\s*,\s*|\s+y\s+|\s+e\s+|\s+a\s+)", seq)
    nums, k = [], 0
    while k < len(partes):
        n = int(partes[k])
        if k + 2 < len(partes) and partes[k + 1].strip() == "a":
            nums.extend(range(n, int(partes[k + 2]) + 1))
            k += 4
        else:
            nums.append(n)
            k += 2
    return nums


def formato(nums):
    nums = sorted(set(nums))
    grupos, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        if j - i >= 2:
            grupos.append(f"{nums[i]} a {nums[j]}")
        else:
            grupos.extend(str(n) for n in nums[i:j + 1])
        i = j + 1
    return grupos[0] if len(grupos) == 1 else ", ".join(grupos[:-1]) + " y " + grupos[-1]


def renumerar(doc):
    mapas = {"Tabla": {}, "Figura": {}}
    for p in doc.element.body.findall(qn("w:p")):  # solo rótulos, no celdas de tablas
        m = re.fullmatch(r"(Tabla|Figura) (\d+)", texto(p).strip())
        if m:
            mapa = mapas[m.group(1)]
            if int(m.group(2)) in mapa:
                raise SystemExit(f"Rótulo repetido: {m.group(0)}")
            mapa[int(m.group(2))] = len(mapa) + 1

    def sub(m):
        tipo = "Tabla" if m.group(1).startswith("Tabla") else "Figura"
        nums = numeros(m.group(3))
        nuevos = []
        for n in nums:
            if n not in mapas[tipo]:
                raise SystemExit(f"Referencia a {tipo} {n} sin rótulo: {m.group(0)!r}")
            nuevos.append(mapas[tipo][n])
        if nuevos == nums:
            return m.group(0)
        return m.group(1) + m.group(2) + formato(nuevos)

    cambios = []
    for p in doc.element.body.iter(qn("w:p")):
        antes = texto(p)
        esperado = REF.sub(sub, antes)
        if esperado == antes:
            continue
        for t in p.iter(qn("w:t")):
            if t.text:
                t.text = REF.sub(sub, t.text)
        if texto(p) != esperado:
            raise SystemExit(f"Una referencia cruza corridas; revisar a mano: {antes[:120]!r}")
        cambios.append((antes, esperado))
    return mapas, cambios


# ------------------------------------------------------------ referencias 6.6
def clave_ref(p):
    t = texto(p).strip()
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return t.replace("(s. f.", "(0000")  # APA 7: las obras sin fecha van antes que las fechadas


def ref_id(p):
    """Autor + año + primeras palabras del título: detecta la misma obra escrita dos veces."""
    t = texto(p).strip()
    m = re.match(r"(.+?\(\s*[^)]*\)\.)\s*(.{0,40})", t)
    return clave_ref(p) if not m else (m.group(1) + m.group(2)).lower()


def cursiva_apa(p):
    """APA 7: el título de la obra va en cursiva. Algunas listas por sección lo dejaron sin cursiva
    (o con todo el párrafo en cursiva); en esas se rehace: autor y fecha normales, título en
    cursiva hasta el primer punto, y el resto normal. Las que ya mezclan cursiva se respetan."""
    rs = [r for r in p.findall(qn("w:r")) if texto(r)]
    cursiva = [r.find(qn("w:rPr")) is not None and r.find(qn("w:rPr")).find(qn("w:i")) is not None
               and r.find(qn("w:rPr")).find(qn("w:i")).get(qn("w:val")) not in ("0", "false") for r in rs]
    mal = any(c and ("Recuperado" in texto(r) or "http" in texto(r)) for c, r in zip(cursiva, rs))
    if any(cursiva) and not all(cursiva) and not mal:
        return False
    t = texto(p)
    m = re.match(r"(.+?\((?:s\. f\.(?:-[a-h])?|\d{4}[^)]*)\)\. )(.+?\.)( .*)?$", t)
    if not m:
        raise SystemExit(f"Referencia sin formato APA reconocible: {t[:80]!r}")
    for r in p.findall(qn("w:r")):
        p.remove(r)
    titulo_, resto = m.group(2), m.group(3) or ""
    if " (" in titulo_:  # número de informe o versión: va sin cursiva
        k = titulo_.index(" (")
        titulo_, resto = titulo_[:k], titulo_[k:] + resto
    for parte, it in ((m.group(1), False), (titulo_, True), (resto, False)):
        if not parte:
            continue
        r = etree.SubElement(p, qn("w:r"))
        if it:
            rpr = etree.SubElement(r, qn("w:rPr"))
            etree.SubElement(rpr, qn("w:i"))
            etree.SubElement(rpr, qn("w:iCs"))
        tt = etree.SubElement(r, qn("w:t"))
        tt.text = parte
        tt.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return True


# ------------------------------------------------------------ índice general
TOC_P = ('<w:p xmlns:w="%s"><w:pPr><w:pStyle w:val="TOC%d"/><w:spacing w:before="0" w:after="160" '
         'w:line="360" w:lineRule="auto"/></w:pPr>%s<w:r><w:t xml:space="preserve">%s</w:t></w:r>'
         '<w:r><w:t xml:space="preserve">\t0</w:t></w:r>%s</w:p>')
TOC_INI = ('<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> TOC \\o "1-3" '
           '\\h \\z \\u </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r>')
TOC_FIN = '<w:r><w:fldChar w:fldCharType="end"/></w:r>'


def xml_esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def rehacer_indice(doc):
    cuerpo = doc.element.body
    hijos = list(cuerpo)
    viejas = [el for el in hijos if el.tag == qn("w:p") and estilo(el).startswith("TOC")]
    ancla = viejas[0].getprevious()
    for el in viejas:
        cuerpo.remove(el)
    titulos = []
    for el in cuerpo:
        if el.tag == qn("w:p") and estilo(el) in ("Heading1", "Heading2", "Heading3"):
            t = re.sub(r"\s+", " ", texto(el)).strip()
            if t and t != "Índice general":
                titulos.append((int(estilo(el)[-1]), t))
    nuevos = []
    for k, (nivel, t) in enumerate(titulos):
        xml = TOC_P % (W, nivel, TOC_INI if k == 0 else "", xml_esc(t), TOC_FIN if k == len(titulos) - 1 else "")
        nuevos.append(etree.fromstring(xml))
    for el in reversed(nuevos):
        ancla.addnext(el)
    return len(nuevos)


def main():
    master = Document(str(F_E1))
    cuerpo = master.element.body

    # --- fecha de la portada (el mismo texto aparece en OE1, por eso se busca el párrafo completo)
    fecha = [el for el in cuerpo if el.tag == qn("w:p") and texto(el).strip() == "17 de octubre de 2026"]
    assert len(fecha) == 1
    ts = list(fecha[0].iter(qn("w:t")))
    ts[0].text = "28 de noviembre de 2026"
    for t in ts[1:]:
        t.text = ""

    # --- resumen ejecutivo nuevo
    hijos = list(cuerpo)
    i = next(k for k, el in enumerate(hijos) if es_titulo(el, "Resumen ejecutivo"))
    viejos = []
    for el in hijos[i + 1:]:
        if el.tag == qn("w:p") and texto(el).strip():
            viejos.append(el)
        elif viejos:
            break
    assert len(viejos) == 4, len(viejos)
    ancla = viejos[-1]
    for txt in reversed(RESUMEN):
        ancla.addnext(parrafo_como(viejos[0], txt))
    for el in viejos:
        cuerpo.remove(el)

    # --- referencias de la Entrega 1: se guardan y se quitan
    refs = referencias(F_E1, "Referencias")
    hijos = list(cuerpo)
    i = max(k for k, el in enumerate(hijos) if es_titulo(el, "Referencias"))
    for el in hijos[i:]:
        if el.tag != qn("w:sectPr"):
            cuerpo.remove(el)
    refs += referencias(F_E2, "Referencias de esta sección")
    refs += referencias(F_DEV, "Referencias de esta sección")

    # --- partes en el orden del esquema
    comp = Composer(master)
    piezas = [
        ("DEV", parte(F_DEV, "3. Evaluación de seguridad", "3.4 ")),
        ("PEN", parte(F_PEN, 0, "3.6 ")),
        ("DEV", parte(F_DEV, "3.4 ", "4.3 ")),
        ("PEN", parte(F_PEN, "3.6 ", None)),
        ("E2", parte(F_E2, "4. Mitigación", "4.5 ")),
        ("DEV", parte(F_DEV, "4.3 ", "4.6 ")),
        ("E2", parte(F_E2, "4.5 ", "Referencias de esta sección")),
        ("DEV", parte(F_DEV, "4.6 ", "Referencias de esta sección")),
        ("OPS", parte(F_OPS, 0, None)),
        ("D6", parte(F_D6, 0, None)),
    ]
    # título de la sección 5 (el Word del bloque 5 no lo traía)
    ops = piezas[8][1]
    h = copy.deepcopy(next(el for el in piezas[4][1].element.body if es_titulo(el, "4. Mitigación")))
    for t in h.iter(qn("w:t")):
        t.text = ""
    next(h.iter(qn("w:t"))).text = "5. Operaciones y monitoreo"
    ops.element.body.insert(0, h)

    pendientes = list(EDICIONES)
    for clave, d in [("E1", master)] + piezas:
        for ed in [x for x in pendientes if x[0] == clave]:
            try:
                reemplazar(d, ed[1], ed[2], ed[3])
                pendientes.remove(ed)
            except SystemExit:
                if clave not in ("DEV", "PEN", "E2"):
                    raise
    if pendientes:
        raise SystemExit("Ediciones sin aplicar: " + "; ".join(x[1][:60] for x in pendientes))
    for _, d in piezas:
        comp.append(d)

    # --- 6.6 Referencias
    unicas, vistas = [], set()
    for p in refs:
        k = ref_id(p)
        if k in vistas:
            continue
        vistas.add(k)
        unicas.append(p)
    unicas.sort(key=clave_ref)
    h6 = copy.deepcopy(next(el for el in cuerpo if es_titulo(el, "6.5 Anexos")))
    for t in h6.iter(qn("w:t")):
        t.text = ""
    next(h6.iter(qn("w:t"))).text = "6.6 Referencias"
    final = cuerpo.find(qn("w:sectPr"))
    final.addprevious(h6)
    for p in unicas:
        ppr = p.find(qn("w:pPr"))
        if ppr is None:
            ppr = etree.SubElement(p, qn("w:pPr"))
            p.insert(0, ppr)
        for old in ppr.findall(qn("w:ind")):
            ppr.remove(old)
        ind = etree.SubElement(ppr, qn("w:ind"))
        ind.set(qn("w:left"), "720")
        ind.set(qn("w:hanging"), "720")
        jc = ppr.find(qn("w:jc"))
        if jc is None:
            jc = etree.SubElement(ppr, qn("w:jc"))
        jc.set(qn("w:val"), "left")
        if cursiva_apa(p):
            print("   cursiva APA:", texto(p)[:70])
        final.addprevious(p)

    # --- títulos, numeración, índice y formato
    reemplazar(master, "1. Selección y Planificación", "1. Selección y planificación", 2)
    reemplazar(master, "2. Activos y Riesgos", "2. Activos y riesgos", 2)
    mapas, cambios = renumerar(master)
    e1.NUEVA_PAGINA = ("1. Selección y planificación", "2. Activos y riesgos", "3. Evaluación de seguridad",
                       "4. Mitigación y ciberseguridad", "5. Operaciones y monitoreo",
                       "6. Dictamen y mejores prácticas")
    e1.normalize_headings(master)
    n_toc = rehacer_indice(master)
    e1.fix_styles(master)
    e1.header_everywhere(master)
    e1.schema_order(master)
    for sp in cuerpo.iter(qn("w:spacing")):
        if sp.get(qn("w:line")) and not sp.get(qn("w:lineRule")):
            sp.set(qn("w:lineRule"), "auto")
    master.core_properties.title = "Q-Wallet: informe final de seguridad"
    master.save(str(SALIDA))

    print("Tablas:", len(mapas["Tabla"]), "· Figuras:", len(mapas["Figura"]),
          "· referencias:", len(unicas), f"(de {len(refs)})", "· entradas del índice:", n_toc)
    print("Renumeradas:", {k: v for k, v in mapas["Tabla"].items() if k != v},
          {k: v for k, v in mapas["Figura"].items() if k != v})
    for a, b in cambios:
        dif = [(x.group(0), y.group(0)) for x, y in zip(REF.finditer(a), REF.finditer(b)) if x.group(0) != y.group(0)]
        print("  ", dif)
    print("ok", SALIDA)


if __name__ == "__main__":
    main()
