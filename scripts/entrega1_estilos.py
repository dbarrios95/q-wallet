"""Aplica el formato acordado el 15-oct-2026 (observación de Katherine) al Word final.

Uso (después de entrega1_revision_paco.py y antes de entrega1_indice.py):
    python scripts/entrega1_estilos.py docs/entregas/Entrega1_Informe_QWallet.docx

Reglas (CONTEXTO, sección 9):
- Letra Times New Roman en todo el documento (cuerpo, títulos, tablas, notas, índice y encabezado).
- Texto fuera de tablas: interlineado doble, 0 pt antes y 8 pt después.
- Texto dentro de tablas: interlineado 1.5, 0 pt antes y 0 pt después.
- No cambia tamaños de letra, sangrías, márgenes, alineación ni contenido.
Requiere: lxml.
"""
import shutil
import sys
import zipfile

from lxml import etree

DOCX = sys.argv[1]
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
q = lambda t: '{%s}%s' % (W, t)
FONT = 'Times New Roman'
CUERPO = {'before': '0', 'after': '160', 'line': '480', 'lineRule': 'auto'}
TABLA = {'before': '0', 'after': '0', 'line': '360', 'lineRule': 'auto'}
# Orden de los hijos de w:pPr según el esquema (solo los que preceden a w:spacing).
ANTES_DE_SPACING = ['pStyle', 'keepNext', 'keepLines', 'pageBreakBefore', 'framePr', 'widowControl',
                    'numPr', 'suppressLineNumbers', 'pBdr', 'shd', 'tabs', 'suppressAutoHyphens',
                    'kinsoku', 'wordWrap', 'overflowPunct', 'topLinePunct', 'autoSpaceDE',
                    'autoSpaceDN', 'bidi', 'adjustRightInd', 'snapToGrid']


def fuentes(root):
    for rf in root.iter(q('rFonts')):
        for a in ('asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme'):
            rf.attrib.pop(q(a), None)
        for a in ('ascii', 'hAnsi', 'eastAsia', 'cs'):
            rf.set(q(a), FONT)


def set_spacing(ppr, vals):
    sp = ppr.find(q('spacing'))
    if sp is None:
        sp = etree.Element(q('spacing'))
        pos = 0
        for i, ch in enumerate(ppr):
            if etree.QName(ch).localname in ANTES_DE_SPACING:
                pos = i + 1
        ppr.insert(pos, sp)
    for a in ('beforeAutospacing', 'afterAutospacing', 'beforeLines', 'afterLines'):
        sp.attrib.pop(q(a), None)
    for k, v in vals.items():
        sp.set(q(k), v)


def get_ppr(p):
    ppr = p.find(q('pPr'))
    if ppr is None:
        ppr = etree.Element(q('pPr'))
        p.insert(0, ppr)
    return ppr


z = zipfile.ZipFile(DOCX)
out = {}
doc = etree.fromstring(z.read('word/document.xml'))
fuentes(doc)
n_cuerpo = n_tabla = 0
for p in doc.iter(q('p')):
    en_tabla = any(a.tag == q('tc') for a in p.iterancestors())
    set_spacing(get_ppr(p), TABLA if en_tabla else CUERPO)
    if en_tabla:
        n_tabla += 1
    else:
        n_cuerpo += 1
out['word/document.xml'] = doc

sty = etree.fromstring(z.read('word/styles.xml'))
fuentes(sty)
dd = sty.find(q('docDefaults'))
set_spacing(dd.find(q('pPrDefault')).find(q('pPr')), CUERPO)
for st in sty.findall(q('style')):
    if st.get(q('type')) != 'paragraph':
        continue
    ppr = st.find(q('pPr'))
    if ppr is not None and ppr.find(q('spacing')) is not None:
        set_spacing(ppr, CUERPO)
out['word/styles.xml'] = sty

for name in z.namelist():
    if name.startswith('word/header') or name.startswith('word/footer') or name in (
            'word/footnotes.xml', 'word/endnotes.xml', 'word/comments.xml', 'word/numbering.xml'):
        r = etree.fromstring(z.read(name))
        fuentes(r)
        out[name] = r

ft = z.read('word/fontTable.xml').decode('utf-8')
if f'w:name="{FONT}"' not in ft:
    ft = ft.replace('</w:fonts>', f'<w:font w:name="{FONT}"><w:panose1 w:val="02020603050405020304"/>'
                    '<w:charset w:val="00"/><w:family w:val="roman"/><w:pitch w:val="variable"/></w:font></w:fonts>')

tmp = DOCX + '.tmp'
with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
    for it in z.infolist():
        if it.filename in out:
            data = etree.tostring(out[it.filename], xml_declaration=True, encoding='UTF-8', standalone=True)
        elif it.filename == 'word/fontTable.xml':
            data = ft.encode('utf-8')
        else:
            data = z.read(it.filename)
        zo.writestr(it, data)
shutil.move(tmp, DOCX)
print(f'Párrafos de cuerpo: {n_cuerpo} (doble, 0/8 pt) · en tablas: {n_tabla} (1.5, 0/0 pt) · letra {FONT}')
