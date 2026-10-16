"""Quita del Word final de la Entrega 1 toda mención de empresa ficticia, dinero simulado o datos ficticios.

Indicación del catedrático (16-oct-2026): en ningún entregable debe decir que la empresa es ficticia
ni que el dinero o los datos son simulados. Cambios de redacción aprobados por Daniel; no cambian
numeración, títulos, tablas ni cifras.

Uso (desde la raíz del repo, después de entrega1_rubrica.py y antes de entrega1_estilos.py):
    python scripts/entrega1_sin_ficticio.py docs/entregas/Entrega1_Informe_QWallet.docx
    python scripts/entrega1_estilos.py docs/entregas/Entrega1_Informe_QWallet.docx
    python scripts/entrega1_indice.py docs/entregas/Entrega1_Informe_QWallet.docx

Cada reemplazo exige una sola coincidencia en un solo párrafo: si el Word no es el esperado,
se detiene sin guardar. Al final verifica que no quede "ficti" ni "simulad" (salvo "incluso simulada",
que se refiere a la política de pruebas de AWS).
Requiere: lxml.
"""
import re
import shutil
import sys
import zipfile

from lxml import etree

DOCX = sys.argv[1]
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
q = lambda t: '{%s}%s' % (W, t)

z = zipfile.ZipFile(DOCX)
root = etree.fromstring(z.read('word/document.xml'))
body = root.find(q('body'))


def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))


def find_p(sub):
    ps = [p for p in body.iter(q('p')) if sub in ptext(p)]
    if len(ps) != 1:
        raise SystemExit(f'Se esperaba 1 párrafo con {sub[:70]!r} y hay {len(ps)}')
    return ps[0]


def rep(old, new):
    """Reemplaza texto dentro de un párrafo conservando el formato de cada run."""
    p = find_p(old)
    ts = list(p.iter(q('t')))
    full = ''.join(t.text or '' for t in ts)
    if full.count(old) != 1:
        raise SystemExit(f'Coincidencias de {old[:70]!r}: {full.count(old)}')
    i = full.index(old)
    j = i + len(old)
    pos = 0
    first = True
    for t in ts:
        s = t.text or ''
        a, b = pos, pos + len(s)
        pos = b
        if b <= i or a >= j:
            continue
        lo, hi = max(i, a) - a, min(j, b) - a
        t.text = s[:lo] + (new if first else '') + s[hi:]
        t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        first = False


CAMBIOS = [
    # 1. Resumen ejecutivo
    ('una billetera digital ficticia para Android, con dinero simulado en quetzales',
     'una billetera digital para Android que opera en quetzales'),
    # 2. 1.1, párrafo 4
    # El Word dice "una billetera digital de la empresa ficticia...": se reemplaza sin el artículo.
    ('billetera digital de la empresa ficticia Q-Wallet, S.A.',
     'billetera digital de Q-Wallet, S.A.'),
    ('opera con dinero simulado en quetzales (GTQ)', 'opera en quetzales (GTQ)'),
    # 3. Nota de la Tabla 1
    ('las tarjetas reales, la integración con bancos reales y la verificación de identidad (KYC) real',
     'las tarjetas, la integración con bancos y la verificación de identidad (KYC)'),
    # 4. Tabla 4
    ('Dinero, tarjetas y bancos reales', 'Tarjetas e integración bancaria'),
    ('El proyecto es académico; se usa dinero simulado y no se procesan datos de tarjetas.',
     'En esta versión no se procesan datos de tarjetas ni hay conexión con bancos.'),
    # 5. Tabla 4
    ('Verificación de identidad (KYC) real', 'Verificación de identidad (KYC)'),
    ('Requiere integraciones y datos personales reales; se documenta como requisito para una puesta en producción.',
     'Requiere integraciones con fuentes externas de identidad; queda como requisito para la puesta en producción.'),
    # 6. Tabla 5
    ('Datos simulados', 'Datos de prueba'),
    ('No se tratan datos personales reales; los números de DPI y de teléfono son ficticios.',
     'En las pruebas no se usan datos personales de clientes; los DPI y teléfonos son de prueba.'),
    # 7. 1.4
    ('Q-Wallet, S.A. es una empresa ficticia que no está supervisada',
     'Q-Wallet, S.A. no está supervisada por la SIB'),
    ('Determinar si una billetera de este tipo requeriría autorización de la SIB para operar con dinero real '
     'queda fuera del alcance de este proyecto, que usa dinero simulado.',
     'Determinar si Q-Wallet requeriría autorización de la SIB para operar queda fuera del alcance de este proyecto.'),
    # 8. 2.1, párrafo 2
    ('según la organización ficticia del proyecto', 'según la organización del proyecto'),
    ('(un rol de la organización ficticia que no ejerce', '(un rol que no ejerce'),
]

for old, new in CAMBIOS:
    rep(old, new)

texto = ' '.join(ptext(p) for p in body.iter(q('p')))
resto = [m.group() for m in re.finditer(r'ficti\w*|simulad\w*', texto, re.I)]
if resto != ['simulada', 'simulada']:  # las dos "incluso simulada" de la política de AWS
    raise SystemExit(f'Quedan menciones: {resto}')
assert chr(0xA7) not in texto

tmp = DOCX + '.tmp'
with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
    for it in z.infolist():
        data = (etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
                if it.filename == 'word/document.xml' else z.read(it.filename))
        zo.writestr(it, data)
shutil.move(tmp, DOCX)
print(f'Reemplazos aplicados: {len(CAMBIOS)} (8 cambios aprobados)')
