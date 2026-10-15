"""Aplica al Word final de la Entrega 1 la revisión de Aroldo (Paco) del 15-oct-2026
y las correcciones pendientes de CONTEXTO, sección 11.

Uso (desde la raíz del repo, sobre el Word del PR #18):
    python scripts/entrega1_revision_paco.py docs/entregas/Entrega1_Informe_QWallet.docx
    python scripts/entrega1_indice.py docs/entregas/Entrega1_Informe_QWallet.docx

Requiere: lxml, Pillow. Las figuras se toman de docs/evidencias (EVD-1-01, EVD-2-05 y
EVD-2-07, ya regeneradas sin título incrustado). Cada reemplazo exige una sola
coincidencia: si el Word no es el esperado, el script se detiene sin guardar.
"""
import copy
import shutil
import sys
import zipfile

from lxml import etree
from PIL import Image

DOCX = sys.argv[1]
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = {'w': W,
      'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
q = lambda t: '{%s}%s' % (W, t)

z = zipfile.ZipFile(DOCX)
root = etree.fromstring(z.read('word/document.xml'))
body = root.find(q('body'))
rels = etree.fromstring(z.read('word/_rels/document.xml.rels'))
media = {}


def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))


def paras():
    return list(body.iter(q('p')))


def find_p(sub, start=None):
    ps = [p for p in paras() if sub in ptext(p)]
    if start is not None:
        ps = [p for p in ps if ptext(p).startswith(start)]
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


def table_after(caption):
    """Tabla que sigue al rótulo 'Tabla N'."""
    p = [x for x in paras() if ptext(x).strip() == caption]
    assert len(p) == 1, caption
    el = p[0]
    while el is not None and el.tag != q('tbl'):
        el = el.getnext()
    return el


def row(tbl, first_cell):
    rs = [tr for tr in tbl.findall(q('tr'))
          if ' '.join(ptext(tr.findall(q('tc'))[0]).split()) == first_cell]
    assert len(rs) == 1, (first_cell, len(rs))
    return rs[0]


def set_cell(tr, idx, text):
    tc = tr.findall(q('tc'))[idx]
    ps = tc.findall(q('p'))
    p = ps[0]
    for extra in ps[1:]:
        tc.remove(extra)
    rs = p.findall(q('r'))
    if not rs:
        ref = [c for c in tr.findall(q('tc')) if c.find('.//' + q('r')) is not None][0]
        p.append(copy.deepcopy(ref.find('.//' + q('r'))))
        rs = p.findall(q('r'))
    for r in rs[1:]:
        p.remove(r)
    ts = rs[0].findall(q('t'))
    if not ts:
        ts = [etree.SubElement(rs[0], q('t'))]
    for t in ts[1:]:
        rs[0].remove(t)
    ts[0].text = text
    ts[0].set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')


def cell_text(tr, idx):
    return ptext(tr.findall(q('tc'))[idx]).strip()


def new_par_like(model, text, before=None, after=None):
    """Párrafo nuevo con el formato del primer run de 'model'."""
    p = copy.deepcopy(model)
    for r in p.findall(q('r'))[1:]:
        p.remove(r)
    for ch in list(p):
        if ch.tag not in (q('pPr'), q('r')):
            p.remove(ch)
    ppr = p.find(q('pPr'))
    if ppr is not None and ppr.find(q('sectPr')) is not None:
        ppr.remove(ppr.find(q('sectPr')))
    r = p.find(q('r'))
    for t in r.findall(q('t'))[1:]:
        r.remove(t)
    t = r.find(q('t'))
    t.text = text
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    (before.addprevious if before is not None else after.addnext)(p)
    return p


# ---------------------------------------------------------------- Resumen
rep('Identificamos 41 amenazas y justificamos 14 casos no aplicables;',
    'Identificamos 41 amenazas y justificamos 14 categorías STRIDE que no requerían una amenaza separada, porque ya las cubre otra;')
rep('Decidimos mitigar 39 riesgos, transferir 1 y aceptar 1.', 'Decidimos mitigar 39 riesgos y aceptar 2.')

# ---------------------------------------------------------------- 1.1 y 1.2
rep('cuenta con un control que la mitiga y que ese control funciona.',
    'cuenta con un control que la mitiga, o con una decisión de tratamiento justificada cuando ningún control aplica (AME-01), y que ese control funciona.')
fp = [p for p in paras() if '[FECHA PENDIENTE]' in ptext(p)]
assert len(fp) == 5, len(fp)
for p in fp:
    rep(' [FECHA PENDIENTE]', '', p)
assert not [p for p in paras() if 'FECHA PENDIENTE' in ptext(p)]
t2 = table_after('Tabla 2')
for oe in ('OE2', 'OE3', 'OE4', 'OE5'):
    tr = row(t2, oe)
    assert cell_text(tr, 3) == 'Pendiente', oe
    set_cell(tr, 3, 'Entrega final')
rep('son relevantes porque cada uno corresponde a un componente de la rúbrica del curso.',
    'son relevantes porque cada uno corresponde a un componente de la rúbrica del curso. El plazo de OE2 a OE5 es la entrega final del curso, cuya fecha aún no ha sido publicada.')
oe5 = find_p('El alcance comprende la aplicación móvil')
cap2 = [p for p in paras() if ptext(p).strip() == 'Tabla 2'][0]
new_par_like(oe5, 'La Tabla 2 traduce cada objetivo específico en un indicador medible, con su meta, su plazo y el componente de la rúbrica al que responde.', before=cap2)

# ---------------------------------------------------------------- 1.3 Tabla 5 (TLS 1.3)
cap5 = [p for p in paras() if ptext(p).strip() == 'Tabla 5'][0]
modelo = find_p('Adoptamos el proceso de gestión de riesgos de ISO/IEC 27005:2022')
new_par_like(modelo, 'La Tabla 5 resume las restricciones del proyecto y el efecto de cada una en el diseño y en las pruebas.', before=cap5)
rep('Se usa el punto de acceso por defecto de API Gateway con TLS 1.2 o superior. TLS 1.3 queda como riesgo residual aceptado y recomendación futura.',
    'Se usa el punto de acceso por defecto de API Gateway (execute-api), sin certificado propio. Le asignamos una política de seguridad que negocia TLS 1.3 y mantiene TLS 1.2 solo como respaldo para dispositivos antiguos.')

# ---------------------------------------------------------------- 1.4
rep('No pudimos consultar el texto oficial en el sitio del Banco de Guatemala, por lo que la citamos a partir de esa fuente secundaria.',
    'El Banco de Guatemala la incluye en su índice oficial de resoluciones de 2025, pero el archivo no pudo abrirse al redactar este informe, por lo que la citamos a partir de esa fuente secundaria.')
rep('Tampoco determinamos si una billetera de este tipo requeriría autorización de la SIB para operar con dinero real [VERIFICAR].',
    'Determinar si una billetera de este tipo requeriría autorización de la SIB para operar con dinero real queda fuera del alcance de este proyecto, que usa dinero simulado.')
rep('En julio de 2026, la Comisión de Asuntos de Seguridad Nacional del Congreso continuaba el análisis de la iniciativa 6464, que propone una ley de protección de datos personales y garantía de derechos digitales (Emisoras Unidas, 2026) [VERIFICAR estado a la fecha de entrega].',
    'La iniciativa 6464, que propone una ley de protección de datos personales y garantía de derechos digitales, se presentó el 29 de octubre de 2024; en julio de 2026, la Comisión de Asuntos de Seguridad Nacional del Congreso continuaba su análisis y aún no había emitido dictamen (Emisoras Unidas, 2026). Al 15 de octubre de 2026 no encontramos noticia de un dictamen ni de su aprobación.')

# ---------------------------------------------------------------- 1.5.1 y Figura 1
rep('Toda solicitud viaja sobre TLS 1.2 o superior con fijación de llaves públicas (pinning) de la autoridad raíz de Amazon; dado que el proyecto no cuenta con un dominio propio y usa el extremo execute-api por defecto, TLS 1.3 queda como riesgo residual aceptado y como recomendación del roadmap.',
    'Toda solicitud viaja cifrada con fijación de llaves públicas (pinning) de la autoridad raíz de Amazon. Aunque el proyecto no cuenta con un dominio propio y usa el extremo execute-api por defecto, le asignamos a la API, de tipo regional, la política de seguridad mejorada SecurityPolicy_TLS13_1_2_2021_06 de API Gateway, que negocia TLS 1.3 y acepta TLS 1.2 solo como respaldo para dispositivos Android anteriores a la versión 10.')
rep('CTRL-23 (verificación de identidad en soporte y capacitación contra ingeniería social) es un control de procedimiento y no se dibuja.',
    'CTRL-23 (verificación de identidad en soporte y capacitación contra ingeniería social) es un control de procedimiento y no se dibuja.')
rep('La Figura 1 muestra la arquitectura con las seis fronteras de confianza y la ubicación de cada control.',
    'La Figura 1 muestra la arquitectura con las seis fronteras de confianza y la ubicación de cada control. En ella, el nodo AWS IAM agrupa los roles de menor privilegio de cada Lambda, el rol de despliegue que GitHub Actions asume por OIDC y la política de la llave KMS (CTRL-12 y CTRL-21). La figura muestra los controles principales de cada servicio; la lista por endpoint está en la Tabla 7.')

# ---------------------------------------------------------------- Notas de las Tablas 7, 8, 9 y 10
rep('Elaboración propia a partir de la arquitectura (CONTEXTO, sección 4).',
    'Elaboración propia a partir de la arquitectura descrita en la sección 1.5.1.')
rep('MITM: ataque de intermediario.',
    'MITM: ataque de intermediario. En las Figuras 1 y 3 cada frontera se rotula con la zona que delimita (por ejemplo, «TB3 Cómputo Lambda»); en esta tabla se nombra por el cruce que controla.',
    p=find_p('BFLA: Broken Function Level Authorization. MITM'))
rep('Elaboración propia a partir del catálogo de controles (CONTEXTO, sección 5). Las capas corresponden a las siete capas de defensa de CONTEXTO, sección 7. CTRL-22 (FLAG_SECURE) se incorpora al catálogo en esta entrega.',
    'Elaboración propia. Las capas corresponden a las siete capas de defensa en profundidad; la capa 2 se divide en 2a (código), 2b (aplicación), 2c (implementación) y 2d (perímetro de aplicación). CTRL-22 (FLAG_SECURE) se incorpora al catálogo en esta entrega. La capa 6 no tiene un control propio: la cubren los controles del dispositivo y el proveedor. La capa 4 depende de un solo control (CTRL-12, roles IAM de menor privilegio), que verificaremos con Checkov y Prowler.')
rep('Elaboración propia a partir de CONTEXTO, sección 3.1.', 'Elaboración propia con las versiones fijadas en el proyecto.')

# ---------------------------------------------------------------- Tabla 9
t9 = table_after('Tabla 9')
tr = row(t9, 'App Android Q-Wallet (TB1)')
assert cell_text(tr, 2) == '2a / 1'
set_cell(tr, 2, '2a / 3 / 1')
tr = row(t9, 'Flujo App ↔ Borde (TB1-TB2)')
set_cell(tr, 3, 'TLS 1.3 (TLS 1.2 de respaldo) con fijación de llaves de Amazon Root CA')
tr = row(t9, 'svc-profile (TB3)')
set_cell(tr, 1, 'CTRL-02, CTRL-03, CTRL-04, CTRL-05, CTRL-14')
set_cell(tr, 2, '1 / 2a / 2b / 2d')
set_cell(tr, 3, 'DTOs mínimos con enmascaramiento; validación zod estricta; hash del PIN (POST /pin); tope en la búsqueda por teléfono; autorización por función al editar el perfil')
tr = row(t9, 'svc-transfers (TB3)')
set_cell(tr, 1, 'CTRL-01, CTRL-02, CTRL-04, CTRL-06')
set_cell(tr, 2, '2a / 2b')
set_cell(tr, 3, 'Autorización de objeto, validación de entrada, PIN con scrypt y escritura idempotente transaccional')
tr = row(t9, 'svc-admin (TB3)')
set_cell(tr, 1, 'CTRL-09, CTRL-14, CTRL-18, CTRL-20')
set_cell(tr, 2, '2b / 7')
set_cell(tr, 3, 'Autorización por función (grupo admins) con MFA obligatorio, registro de auditoría y alertas en el SIEM')
nuevo = copy.deepcopy(row(t9, 'Personal de soporte (TB2)'))
row(t9, 'GitHub Actions (TB5)').addnext(nuevo)
set_cell(nuevo, 0, 'Dispositivo y centros de datos (TB1 y AWS)')
set_cell(nuevo, 1, 'CTRL-07, CTRL-18')
set_cell(nuevo, 2, '6')
set_cell(nuevo, 3, 'Ante la pérdida o el robo del teléfono, desbloqueo biométrico y MFA; la seguridad física de los centros de datos la asegura AWS (responsabilidad compartida)')

# ---------------------------------------------------------------- Tabla 10
t10 = table_after('Tabla 10')
tr = row(t10, 'Contenedores (móvil)')
set_cell(tr, 0, 'Análisis de la app (APK)')

# ---------------------------------------------------------------- 1.5.6 y Tabla 11
rep('Cuatro requieren rediseño para no infringir la prohibición de inundación, y dos de los casos nuevos del modelo de amenazas (CA-14 y CA-16) deben tratarse igual.',
    'Tres infringen la prohibición de inundación y requieren rediseño (CA-02, CA-03 y CA-12); uno queda en el límite y lo acotamos a una ráfaga mínima (CA-06), y en CA-13 excluimos la variante que fuerza el inicio de sesión de Cognito. Además, dos de los casos nuevos del modelo de amenazas (CA-14 y CA-16) también tocan la política.')
rep('CA-14 y CA-16, marcados con asterisco, son casos nuevos del modelo de amenazas (no estaban en los trece originales) pero también tocan la política y los incluimos por su relevancia.',
    'CA-14 y CA-16, marcados con asterisco, son casos propuestos en el modelo de amenazas que no forman parte del catálogo de trece casos de OE3; los incluimos porque también tocan la política. No se ejecutan como ataque: se verifican por configuración, por lo que no producen la evidencia de bloqueo que exige OE3. El resto de los casos propuestos en el modelo (como CA-15) no tocan la política y no se adoptaron en el catálogo.')

# ---------------------------------------------------------------- 2 y 2.1
rep('Los datos de amenazas provienen del modelo de amenazas elaborado en OWASP Threat Dragon (versión 2 del modelo, 41 amenazas sobre tres diagramas de flujo de datos), que se conserva en el repositorio del proyecto.',
    'Los datos de amenazas provienen del modelo de amenazas T2, elaborado en OWASP Threat Dragon (versión 2 del modelo, 41 amenazas sobre tres diagramas de flujo de datos), que se conserva en el repositorio público del proyecto (github.com/dbarrios95/q-wallet).')
rep('Gerente de Producto para los activos de negocio,',
    'Gerente de Producto para los activos de negocio (un rol de la organización ficticia que no ejerce ningún integrante del equipo y que representa a quien aprueba el tratamiento de los riesgos del negocio),')

# ---------------------------------------------------------------- 2.3 Tablas 17 y 18
t17 = table_after('Tabla 17')
tr = row(t17, 'AME-01')
assert cell_text(tr, 6) == ''
set_cell(tr, 6, '— (riesgo aceptado; ver sección 2.5.2)')
tr = row(t17, 'AME-31')
assert cell_text(tr, 6) == 'CTRL-20'
set_cell(tr, 6, 'CTRL-20 (solo CloudTrail; riesgo aceptado)')
rep('Categorías STRIDE revisadas y justificadas como no aplicables', 'Categorías STRIDE revisadas sin amenaza separada')
t18 = table_after('Tabla 18')
hits = [tr for tr in t18.findall(q('tr')) if cell_text(tr, 2) == 'Intercepción del token del administrador']
assert len(hits) == 1 and cell_text(hits[0], 3) == 'AME-03, AME-23, AME-11'
set_cell(hits[0], 3, 'AME-06; además, CTRL-18')
hits = [tr for tr in t18.findall(q('tr')) if cell_text(tr, 2) == 'Lectura de parámetros en tránsito hacia SSM']
assert len(hits) == 1 and cell_text(hits[0], 3) == 'AME-27, AME-08, AME-34'
set_cell(hits[0], 3, 'AME-27')

# ---------------------------------------------------------------- 2.4
rep('La valoración es inherente: suponemos que ninguno de los controles CTRL-01 a CTRL-23 está presente.',
    'La valoración es inherente: suponemos que ninguno de los controles CTRL-01 a CTRL-23 está presente. Las prioridades DREAD (Alta, Media y Baja), los niveles de riesgo de la matriz P×I (Crítico, Alto, Medio y Bajo) y la criticidad CIA de los activos son escalas distintas y no deben compararse entre sí: por ejemplo, 15 amenazas tienen prioridad DREAD Alta, pero 18 riesgos son Críticos en la matriz.')

# ---------------------------------------------------------------- 2.5.2 (RSK-01 pasa a Aceptar)
rep('Dos riesgos reciben otro tratamiento: RSK-01 (indisponibilidad de la región us-east-1) se transfiere a AWS bajo el modelo de responsabilidad compartida, porque la protección física y la disponibilidad de los centros de datos son responsabilidad del proveedor, aunque la decisión de continuidad sigue siendo nuestra; y RSK-31',
    'Los otros dos riesgos se aceptan. RSK-01 (indisponibilidad de la región us-east-1) nace de nuestra decisión de desplegar en una sola región, que responde a la restricción de costo (Tabla 5): AWS responde por la seguridad física de sus centros de datos bajo el modelo de responsabilidad compartida (AWS, s. f.-c), pero no por la continuidad de Q-Wallet, por lo que el riesgo no se transfiere sino que se acepta. RSK-31')
for cap in ('Tabla 21', 'Tabla 23'):
    t = table_after(cap)
    tr = row(t, 'RSK-01')
    cells = tr.findall(q('tc'))
    idx = [i for i, c in enumerate(cells) if ptext(c).strip() == 'Transferir']
    assert len(idx) == 1, cap
    set_cell(tr, idx[0], 'Aceptar')

# ---------------------------------------------------------------- 2.5.5
rep('En consecuencia, 15 riesgos quedan en la celda P1 × I5 = 5 (Medio): su probabilidad llega al mínimo, pero su impacto sigue siendo máximo,',
    'En consecuencia, 15 riesgos quedan en la celda P1 × I5 = 5 (Medio): 14 porque su probabilidad baja al mínimo y RSK-01, que ya partía de ahí; en todos, el impacto sigue siendo máximo,')
rep('uno Medio se acepta con la aprobación del propietario del activo y seguimiento en el SIEM; uno Alto no se acepta sin un plan de tratamiento con fecha,',
    'uno Medio se acepta con la aprobación del propietario del activo y seguimiento en el SIEM (en RSK-31, cuyo activo es el propio SIEM, el seguimiento es una revisión manual semanal de los eventos que conserva CloudTrail); uno Alto no se acepta sin un plan de tratamiento con plazo,')
rep('RSK-01 se transfiere a AWS, lo que traslada la responsabilidad sobre los centros de datos, pero no reduce el impacto que una caída regional tendría sobre Q-Wallet; RSK-31 se acepta, por lo que no se aplica un control adicional y el riesgo queda en 9 (Medio), dentro del criterio.',
    'RSK-01 y RSK-31 se aceptan, por lo que no se aplica un control adicional: RSK-01 queda en 5 y RSK-31 en 9, ambos de nivel Medio y dentro del criterio.')
rep('El plan de tratamiento refuerza CTRL-21 en la fase de arquitectura con tres medidas:',
    'El plan de tratamiento refuerza CTRL-21 en la fase de arquitectura, antes del primer despliegue del pipeline a AWS, con tres medidas:')
ult = find_p('El redondeo hacia arriba es una decisión conservadora')
new_par_like(ult, 'En síntesis, el riesgo inherente de Q-Wallet (18 riesgos críticos, 12 altos y 11 medios, con una suma de 580) no es aceptable sin controles. Con los 23 controles de diseño, la proyección lo lleva a 0 críticos, 1 alto, 26 medios y 14 bajos, con una suma de 207, lo que cumple el criterio de aceptación salvo por RSK-32, que tiene un plan de tratamiento con plazo. Esta conclusión es provisional: el dictamen sobre el riesgo residual lo emitiremos en la entrega final, con la evidencia de las pruebas de los controles y de los casos de abuso.', after=ult)

# ---------------------------------------------------------------- Revisión de 1.5, 2.1 y 2.2 (15-oct, segunda pasada)
rep('Autorizamos las pruebas contra nuestros propios recursos en la cuenta AWS del proyecto: AWS WAF, API Gateway, las funciones Lambda, DynamoDB, SSM, S3 y los roles IAM, además de la aplicación Android sobre el emulador y de la configuración del repositorio.',
    'Autorizamos las pruebas de intrusión contra AWS WAF, API Gateway y las funciones Lambda de nuestra cuenta, los servicios de nuestra arquitectura que la política de AWS permite probar sin solicitud previa (AWS, s. f.-b), además de la aplicación Android sobre el emulador y de la configuración del repositorio. DynamoDB, SSM, S3 e IAM no se atacan directamente: verificamos su configuración con Checkov y Prowler, y su exposición, a través de la API.')
rep('y tomamos los casos de prueba de la OWASP Web Security Testing Guide (OWASP Foundation, s. f.).',
    'y tomamos los casos de prueba de la OWASP Web Security Testing Guide (OWASP Foundation, s. f.) para la API y del MASTG (OWASP Mobile Application Security Project, 2024) para la aplicación móvil.')
rep('El resto de los casos propuestos en el modelo (como CA-15) no tocan la política y no se adoptaron en el catálogo.',
    'Los demás casos propuestos en el modelo (CA-15 y CA-17 a CA-25) no se adoptaron en el catálogo.')
tr = row(t9, 'API Gateway (TB2)')
assert cell_text(tr, 2) == '2d'
set_cell(tr, 2, '2d / 5')
t8 = table_after('Tabla 8')
tr = row(t8, 'TB3 API Gateway ↔ Lambdas')
assert cell_text(tr, 3) == 'CTRL-01, CTRL-02, CTRL-04, CTRL-06, CTRL-14'
set_cell(tr, 3, 'CTRL-01, CTRL-02, CTRL-03, CTRL-04, CTRL-05, CTRL-06, CTRL-14')
tr = row(t8, 'TB2 Internet ↔ Borde AWS')
assert cell_text(tr, 3) == 'CTRL-08, CTRL-13, CTRL-17, CTRL-18, CTRL-05'
set_cell(tr, 3, 'CTRL-05, CTRL-08, CTRL-13, CTRL-17, CTRL-18')
t7 = table_after('Tabla 7')
hits = [tr for tr in t7.findall(q('tr')) if cell_text(tr, 1) == '/admin/users/{id}/block']
assert len(hits) == 1 and cell_text(hits[0], 5) == 'CTRL-14, CTRL-20'
set_cell(hits[0], 5, 'CTRL-14, CTRL-20, CTRL-23')
t12 = table_after('Tabla 12')
tr = row(t12, 'ACT-03')
assert cell_text(tr, 13) == 'DevSecOps Engineer (I2)'
set_cell(tr, 13, 'DevSecOps Engineer (I2) en Cognito; Cliente en el dispositivo')
rep('La Tabla 12 presenta el inventario completo.',
    'El dispositivo del cliente (ACT-18) es propiedad del propio cliente; por eso el dueño de su riesgo es el Gerente de Producto (sección 2.5.2). La Tabla 12 presenta el inventario completo.')
rep('Valoramos cada activo en las tres dimensiones de la tríada CIA con una escala ordinal de tres niveles.',
    'Valoramos cada activo en las tres dimensiones de la tríada CIA con una escala ordinal de tres niveles, como base para clasificar la información según el control 5.12 del Anexo A de ISO/IEC 27001:2022 (ISO e IEC, 2022a).')

# ---------------------------------------------------------------- Notas: Arial 12 e interlineado 1.5
n_notas = 0
for p in paras():
    if not ptext(p).startswith('Nota. '):
        continue
    n_notas += 1
    sp = p.find(q('pPr')).find(q('spacing'))
    sp.set(q('line'), '360')
    for tag in ('sz', 'szCs'):
        for el in p.iter(q(tag)):
            el.set(q('val'), '24')

# ---------------------------------------------------------------- Figuras 1, 5 y 6
def figure_drawing(n):
    cap = [p for p in paras() if ptext(p).strip() == f'Figura {n}']
    assert len(cap) == 1
    el = cap[0].getnext()
    while not list(el.iter('{%s}blip' % NS['a'])):
        el = el.getnext()
    return cap[0], el


def set_image(n, png, width_in):
    cap, dp = figure_drawing(n)
    blip = list(dp.iter('{%s}blip' % NS['a']))[0]
    rid = blip.get('{%s}embed' % NS['r'])
    target = [r for r in rels if r.get('Id') == rid][0].get('Target')
    media['word/' + target] = open(png, 'rb').read()
    w, h = Image.open(png).size
    cx = int(width_in * 914400)
    cy = int(cx * h / w)
    for e in dp.iter('{%s}extent' % NS['wp']):
        e.set('cx', str(cx)); e.set('cy', str(cy))
    for e in dp.iter('{%s}ext' % NS['a']):
        if e.get('cx'):
            e.set('cx', str(cx)); e.set('cy', str(cy))
    return cap, dp


EVD = 'docs/evidencias'
cap1, dp1 = set_image(1, f'{EVD}/EVD-1-01_arquitectura_controles.png', 6.6)
set_image(5, f'{EVD}/EVD-2-05_heatmap_inherente.png', 6.0)
set_image(6, f'{EVD}/EVD-2-07_heatmap_residual_proyectado.png', 6.0)

# Figura 1 en página horizontal: cierra la sección vertical antes del rótulo y la
# horizontal después de la nota (mismo patrón que las Figuras 3 y 4).
sects = [s for s in body.iter(q('sectPr')) if s.getparent().tag == q('pPr')]
vert = [s for s in sects if s.find(q('pgSz')).get(q('orient')) is None][0]
horiz = [s for s in sects if s.find(q('pgSz')).get(q('orient')) == 'landscape'][0]
p_v = etree.SubElement(etree.Element(q('p')), q('pPr'))
p_v.append(copy.deepcopy(vert))
cap1.addprevious(p_v.getparent())
nota1 = [p for p in paras() if ptext(p).startswith('Nota. Elaboración propia. Las líneas verdes')][0]
p_h = etree.SubElement(etree.Element(q('p')), q('pPr'))
p_h.append(copy.deepcopy(horiz))
nota1.addnext(p_h.getparent())

# ---------------------------------------------------------------- Verificaciones
txt = '\n'.join(ptext(p) for p in paras())
assert chr(0xA7) not in txt
assert 'CONTEXTO' not in txt, [l for l in txt.splitlines() if 'CONTEXTO' in l]
assert 'Transferir' not in txt and 'transferir 1' not in txt
print('[VERIFICAR] restantes:', txt.count('[VERIFICAR'))
print('Notas ajustadas:', n_notas)

tmp = DOCX + '.tmp'
with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
    for it in z.infolist():
        if it.filename == 'word/document.xml':
            data = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
        else:
            data = media.get(it.filename, z.read(it.filename))
        zo.writestr(it, data)
shutil.move(tmp, DOCX)
print('Listo:', DOCX)
