"""Ajusta el Word final de la Entrega 1 a la rúbrica y al enunciado (16-oct-2026, aprobado por Daniel).

Uso (desde la raíz del repo, después de entrega1_revision_paco.py):
    python scripts/entrega1_rubrica.py docs/entregas/Entrega1_Informe_QWallet.docx
    python scripts/entrega1_estilos.py docs/entregas/Entrega1_Informe_QWallet.docx
    python scripts/entrega1_indice.py docs/entregas/Entrega1_Informe_QWallet.docx

Cambios:
1. Títulos con la redacción del esquema del enunciado (Opción A); la numeración no cambia.
   Se mantiene el uso de mayúsculas del resto del informe (solo la primera palabra y nombres propios).
2. Cita de 1.1: Carrillo & Asociados (2025) respalda la JM-98-2025 y AWS (s. f.-a) la JM-104-2021,
   que es la única resolución que nombra esa página de AWS (verificado el 15-oct-2026).
3. Se quita el marcador [VERIFICAR] del Findex: la cifra queda con su cita secundaria
   ("como se citó en"), que APA 7 admite.
4. AWS (s. f.-c) con fecha de consulta, igual que (s. f.-a) y (s. f.-b) (página consultada el 16-oct-2026).
5. Tablas 7 a 23 (antes de 6.5 a 9 pt): 10 pt las cortas y 9 pt las largas; Tabla 12 en 8 pt.
   Anchos de columna recalculados para que ninguna palabra se parta.
El formato general (Arial 12, interlineado 1.5) lo aplica entrega1_estilos.py.
Cada reemplazo exige el número esperado de coincidencias: si el Word no es el esperado, se detiene sin guardar.
Requiere: lxml, Pillow y la fuente Liberation Sans (métricas de Arial).
"""
import shutil
import sys
import zipfile

from lxml import etree
from PIL import ImageFont

DOCX = sys.argv[1]
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
q = lambda t: '{%s}%s' % (W, t)

z = zipfile.ZipFile(DOCX)
root = etree.fromstring(z.read('word/document.xml'))
body = root.find(q('body'))


def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))


def paras():
    return list(body.iter(q('p')))


def find_p(sub):
    ps = [p for p in paras() if sub in ptext(p)]
    if len(ps) != 1:
        raise SystemExit(f'Se esperaba 1 párrafo con {sub[:70]!r} y hay {len(ps)}')
    return ps[0]


def rep(old, new, p=None):
    """Reemplaza texto dentro de un párrafo conservando el formato de cada run."""
    p = p if p is not None else find_p(old)
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


# 1. Títulos (el título y su entrada del índice; "Índice" solo existe como título)
TITULOS = [
    ('1.1 Contexto', '1.1 Contexto de la aplicación móvil', 2),
    ('1.4 Normativas y estándares de referencia', '1.4 Normativas y estándares', 2),
    ('2.1 Inventario de activos', '2.1 Inventario de activos (ISO 27001)', 2),
    ('2.3 Modelado de amenazas STRIDE', '2.3 Modelado de amenazas (STRIDE)', 2),
    ('2.4 Valoración DREAD', '2.4 Clasificación de riesgos (DREAD)', 2),
    ('Índice', 'Índice general', 1),
]
for old, new, n in TITULOS:
    ps = [p for p in paras() if ptext(p).split('\t')[0].strip() == old]
    if len(ps) != n:
        raise SystemExit(f'Título {old!r}: se esperaban {n} párrafos y hay {len(ps)}')
    for p in ps:
        rep(old, new, p)

# 2. Cita de AWS (s. f.-a) junto a la JM-104-2021
rep('emitido por la Resolución JM-98-2025, que derogó la Resolución JM-104-2021 '
    '(Amazon Web Services [AWS], s. f.-a; Carrillo & Asociados, 2025).',
    'emitido por la Resolución JM-98-2025 (Carrillo & Asociados, 2025), que derogó la Resolución '
    'JM-104-2021 (Amazon Web Services [AWS], s. f.-a).')

# 3. Marcador del Findex
rep(' [VERIFICAR en la base primaria de Global Findex]', '')

# 4. Fecha de consulta de AWS (s. f.-c)
rep('Shared responsibility model. https://aws.amazon.com/compliance/shared-responsibility-model/',
    'Shared responsibility model. Recuperado el 16 de octubre de 2026, de '
    'https://aws.amazon.com/compliance/shared-responsibility-model/')

# 5. Letra y anchos de las Tablas 7 a 23
# Letra: 10 pt en las tablas cortas y 9 pt en las largas (las que a 10 pt medirían más de una página).
# Tabla 12 (15 columnas obligatorias de ISO 27001): 8 pt con márgenes de celda de 40 dxa por lado,
# lo mínimo para que ninguna palabra se parta en una página horizontal.
# Anchos: cada columna recibe primero el ancho de su palabra más larga (sin partirla) y el sobrante se
# reparte, de 80 en 80 dxa, a la columna que más reduce la altura estimada de la tabla. El ancho total
# no cambia. Las medidas usan Liberation Sans, que tiene las mismas métricas que Arial.
TAM = {n: 20 for n in (7, 8, 10, 11, 13, 15, 16, 19)}
TAM.update({n: 18 for n in (9, 14, 17, 18, 20, 21, 22, 23)})
TAM[12] = 16
MARGEN_T12 = 40
FUENTES = {False: '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
           True: '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'}
HOLGURA = 30
PASO = 80
_cache = {}


def es_negrita(r):
    rpr = r.find(q('rPr'))
    b = rpr.find(q('b')) if rpr is not None else None
    return b is not None and b.get(q('val'), '1') not in ('0', 'false')


def contenido(tc):
    """Palabras de cada párrafo de la celda, con su negrita."""
    out = []
    for p in tc.iter(q('p')):
        ws = []
        for r in p.iter(q('r')):
            ws += [(w, es_negrita(r)) for w in ''.join(t.text or '' for t in r.iter(q('t'))).split()]
        out.append(ws)
    return out


def margen(tc):
    m = tc.find(q('tcPr')).find(q('tcMar'))
    return sum(int(m.find(q(x)).get(q('w'))) for x in ('left', 'right')) if m is not None else 216


def largo(fonts, w, b):
    k = (fonts[False].size, w, b)
    if k not in _cache:
        _cache[k] = fonts[b].getlength(w)
    return _cache[k]


def lineas(pars, ancho, fonts):
    n = 0
    sp = largo(fonts, ' ', False)
    for ws in pars:
        if not ws:
            n += 1
            continue
        l, x = 1, 0
        for w, b in ws:
            wl = largo(fonts, w, b)
            if x == 0:
                x = wl
            elif x + sp + wl <= ancho:
                x += sp + wl
            else:
                l, x = l + 1, wl
            while x > ancho:
                l, x = l + 1, x - ancho
        n += l
    return n


def ajustar(tbl, n, hp):
    if n == 12:
        for m in tbl.iter(q('tcMar')):
            for lado in ('left', 'right'):
                m.find(q(lado)).set(q('w'), str(MARGEN_T12))
    cols = tbl.find(q('tblGrid')).findall(q('gridCol'))
    total = sum(int(c.get(q('w'))) for c in cols)
    trs = tbl.findall(q('tr'))
    tcs = [tr.findall(q('tc')) for tr in trs]
    if any(len(f) != len(cols) for f in tcs):
        raise SystemExit(f'Tabla {n}: celdas combinadas; ajuste manual')
    filas = [[contenido(tc) for tc in f] for f in tcs]
    mar = [max(margen(f[j]) for f in tcs) + HOLGURA for j in range(len(cols))]
    fonts = {b: ImageFont.truetype(f, hp * 10) for b, f in FUENTES.items()}  # 1 px = 1 dxa
    need = [int(max([largo(fonts, w, b) for f in filas for ws in f[j] for (w, b) in ws] or [0])) + mar[j]
            for j in range(len(cols))]
    if sum(need) > total:
        raise SystemExit(f"Tabla {n}: a {hp / 2} pt no cabe sin partir palabras ({sum(need)} > {total} dxa)")

    def alto(w):
        return sum(max(lineas(f[j], w[j] - mar[j], fonts) for j in range(len(w))) for f in filas)

    w = need[:]
    libre = total - sum(w)
    actual = alto(w)
    while libre >= PASO:
        mejor = None
        for j in range(len(w)):
            w[j] += PASO
            h = alto(w)
            w[j] -= PASO
            if mejor is None or h < mejor[0]:
                mejor = (h, j)
        if mejor[0] >= actual:
            break
        w[mejor[1]] += PASO
        libre -= PASO
        actual = mejor[0]
    vol = [sum(len(x) for f in filas for ws in f[j] for x, _ in ws) for j in range(len(w))]
    sv = sum(vol) or 1
    w = [a + libre * v // sv for a, v in zip(w, vol)]
    w[-1] += total - sum(w)
    for c, x in zip(cols, w):
        c.set(q('w'), str(x))
    for f in tcs:
        for tc, x in zip(f, w):
            tcw = tc.find(q('tcPr')).find(q('tcW'))
            tcw.set(q('w'), str(x))
            tcw.set(q('type'), 'dxa')
    for tag in ('sz', 'szCs'):
        for el in tbl.iter(q(tag)):
            el.set(q('val'), str(hp))


tablas = list(body.iter(q('tbl')))
if len(tablas) != 23:
    raise SystemExit(f'Se esperaban 23 tablas y hay {len(tablas)}')
for n, hp in sorted(TAM.items()):
    ajustar(tablas[n - 1], n, hp)
print('Letra de las tablas (pt):', {n: hp / 2 for n, hp in sorted(TAM.items())})

texto = ''.join(ptext(p) for p in paras())
assert '[VERIFICAR' not in texto
assert chr(0xA7) not in texto

tmp = DOCX + '.tmp'
with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
    for it in z.infolist():
        data = (etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
                if it.filename == 'word/document.xml' else z.read(it.filename))
        zo.writestr(it, data)
shutil.move(tmp, DOCX)
print('Títulos: 6 · cita AWS (s. f.-a) movida · [VERIFICAR] quitado · AWS (s. f.-c) con fecha · '
      'Tablas 7-23 con anchos ajustados')
