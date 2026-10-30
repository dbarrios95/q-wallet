"""Genera las secciones 3.1, 3.2, 3.3 y 3.6 del informe (Fase 4, bloque 4).

Uso:
    python scripts/bloque4_diagrama_perimetro.py       # figura del perímetro (EVD-4-14)
    python scripts/bloque4_word.py                     # Word de las secciones
    python scripts/entrega1_estilos.py docs/entregas/Final_Secciones_3-1_3-2_3-3_3-6_Pentest.docx

Mismo formato que las entregas anteriores (estilos del informe de la Entrega 1). Las cifras
verificables salen de ejecuciones reales: el arnés de pentest (services/pentest, 18 pruebas
OWASP API y 11 casos de abuso, todos bloqueados: EVD-4-12 y EVD-4-13) y la verificación de AWS
del despliegue (EVD-3-11, EVD-3-12, EVD-5-04, Checkov). Los escaneos en vivo (Nmap, ZAP baseline
y Prowler) corren en el flujo pentest.yml con un rol de solo lectura y publican su evidencia en
el issue "Evidencias Pentest"; se adjuntan al ensamblar el informe final.
Numeración provisional: continúa el bloque 3 (Tabla 37, Figura 8); se ajusta al ensamblar.
Requiere python-docx, Pillow.
"""
import copy
from pathlib import Path

import docx
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Emu, Inches, Pt

RAIZ = Path(__file__).resolve().parent.parent
PLANTILLA = RAIZ / "docs/entregas/Entrega1_Informe_QWallet.docx"
SALIDA = RAIZ / "docs/entregas/Final_Secciones_3-1_3-2_3-3_3-6_Pentest.docx"
FIGURA_PERIMETRO = RAIZ / "docs/evidencias/EVD-4-14_perimetro.png"

TABLA_INICIAL = 38   # el bloque 3 terminó en la Tabla 37
FIGURA_INICIAL = 9   # y en la Figura 8

doc = docx.Document(str(PLANTILLA))
cuerpo = doc.element.body
sect_final = copy.deepcopy(cuerpo[-1])
for hijo in list(cuerpo):
    cuerpo.remove(hijo)
cuerpo.append(sect_final)
s0 = doc.sections[-1]
s0.orientation = WD_ORIENT.PORTRAIT
s0.page_width, s0.page_height = Emu(7772400), Emu(10058400)

n_tabla = TABLA_INICIAL
n_figura = FIGURA_INICIAL


# ---------------------------------------------------------------- utilidades
def titulo(texto, nivel):
    doc.add_heading(texto, level=nivel)


def parrafo(texto, cursivas=()):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = Inches(0.5)
    partes = texto.split("*")
    for i, parte in enumerate(partes):
        if parte:
            r = p.add_run(parte)
            r.font.size = Pt(12)
            r.italic = i % 2 == 1
    return p


def rotulo(tipo, numero, nombre):
    p = doc.add_paragraph()
    r = p.add_run(f"{tipo} {numero}")
    r.bold = True
    r.font.size = Pt(12)
    p.paragraph_format.keep_with_next = True
    p2 = doc.add_paragraph()
    r2 = p2.add_run(nombre)
    r2.italic = True
    r2.font.size = Pt(12)
    p2.paragraph_format.keep_with_next = True


def nota(texto):
    p = doc.add_paragraph()
    r = p.add_run("Nota. ")
    r.italic = True
    r.font.size = Pt(12)
    r2 = p.add_run(texto)
    r2.font.size = Pt(12)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def borde(tc_pr, lados):
    b = OxmlElement("w:tcBorders")
    for lado in ("top", "left", "bottom", "right"):
        e = OxmlElement(f"w:{lado}")
        if lado in lados:
            e.set(qn("w:val"), "single")
            e.set(qn("w:sz"), "4")
            e.set(qn("w:color"), "000000")
        else:
            e.set(qn("w:val"), "none")
            e.set(qn("w:sz"), "0")
            e.set(qn("w:color"), "FFFFFF")
        b.append(e)
    tc_pr.append(b)


def margenes(tc_pr):
    m = OxmlElement("w:tcMar")
    for lado, v in (("top", 40), ("left", 90), ("bottom", 40), ("right", 90)):
        e = OxmlElement(f"w:{lado}")
        e.set(qn("w:w"), str(v))
        e.set(qn("w:type"), "dxa")
        m.append(e)
    tc_pr.append(m)


FUENTE_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FUENTE_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def anchos_sin_cortes(encabezado, filas, tam, total):
    from PIL import ImageFont
    fr = ImageFont.truetype(FUENTE_R, tam * 10)
    fb = ImageFont.truetype(FUENTE_B, tam * 10)
    n = len(encabezado)
    minimo, peso = [0.0] * n, [0.0] * n
    for i, fila in enumerate([encabezado] + filas):
        f = fb if i == 0 else fr
        for j, v in enumerate(fila):
            for palabra in str(v).replace("\n", " ").split():
                w = f.getlength(palabra) / 10 / 72
                minimo[j] = max(minimo[j], w)
            peso[j] += fr.getlength(str(v)) / 10 / 72
    margen = 180 / 1440 + 0.03
    minimo = [m + margen for m in minimo]
    libre = total - sum(minimo)
    if libre < 0:
        return None
    return [m + libre * p / sum(peso) for m, p in zip(minimo, peso)]


def tabla(nombre, encabezado, filas, tam=10, nota_txt=None, total=6.5):
    global n_tabla
    anchos_pulg = anchos_sin_cortes(encabezado, filas, tam, total)
    if anchos_pulg is None:
        raise SystemExit(f"La tabla '{nombre}' no cabe sin partir palabras en {total} pulgadas")
    rotulo("Tabla", n_tabla, nombre)
    n_tabla += 1
    t = doc.add_table(rows=1 + len(filas), cols=len(encabezado))
    t.autofit = False
    grid = t._tbl.tblGrid
    for gc, w in zip(grid.findall(qn("w:gridCol")), anchos_pulg):
        gc.set(qn("w:w"), str(int(w * 1440)))
    todas = [encabezado] + filas
    for i, fila in enumerate(todas):
        row = t.rows[i]
        tr_pr = row._tr.get_or_add_trPr()
        tr_pr.append(OxmlElement("w:cantSplit"))
        if i == 0:
            tr_pr.append(OxmlElement("w:tblHeader"))
        for j, valor in enumerate(fila):
            celda = row.cells[j]
            celda.width = Inches(anchos_pulg[j])
            tc_pr = celda._tc.get_or_add_tcPr()
            lados = set()
            if i == 0:
                lados = {"top", "bottom"}
            elif i == len(todas) - 1:
                lados = {"bottom"}
            borde(tc_pr, lados)
            margenes(tc_pr)
            p = celda.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for k, linea in enumerate(str(valor).split("\n")):
                if k:
                    p = celda.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                r = p.add_run(linea.replace("-", "‑"))
                r.font.size = Pt(tam)
                r.bold = i == 0
    if nota_txt:
        nota(nota_txt)
    return t


def figura(nombre, ruta, ancho_pulg, nota_txt):
    global n_figura
    rotulo("Figura", n_figura, nombre)
    n_figura += 1
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(ruta), width=Inches(ancho_pulg))
    nota(nota_txt)


def seccion(horizontal):
    s = doc.add_section(WD_SECTION.NEW_PAGE)
    if horizontal:
        s.orientation = WD_ORIENT.LANDSCAPE
        s.page_width, s.page_height = Emu(10058400), Emu(7772400)
    else:
        s.orientation = WD_ORIENT.PORTRAIT
        s.page_width, s.page_height = Emu(7772400), Emu(10058400)


# ================================================================ contenido
parrafo(
    "Las secciones 3.1, 3.2, 3.3 y 3.6 completan la Evaluación de seguridad (Fase 4 del "
    "enunciado) con las pruebas ofensivas y defensivas sobre la aplicación ya construida. "
    "Como Q-Wallet se construyó con todos los controles desde el diseño, el pentest no busca "
    "una versión vulnerable: busca demostrar que cada control funciona. La evidencia de cada "
    "prueba es el bloqueo (401, 403, 404, 413, 422, 423 o el rechazo de TLS), y cualquier "
    "debilidad real que aparezca se registra como hallazgo (HAL) y se corrige. Las secciones "
    "3.4 y 3.5 (SAST y SCA) se entregaron con el bloque anterior."
)

# ---------------------------------------------------------------- 3.1
titulo("3.1 Pentesting caja negra", 2)
parrafo(
    "En la prueba de caja negra atacamos la aplicación desde internet, sin credenciales ni "
    "acceso al código, como lo haría un atacante externo. El objetivo es mapear la superficie "
    "expuesta y comprobar que no hay forma de entrar sin autenticarse. Las pruebas corren de "
    "forma automática en el flujo pentest.yml de GitHub Actions, con un rol de AWS de solo "
    "lectura asumido por OIDC, y publican su evidencia en el issue «Evidencias Pentest» del "
    "repositorio."
)
parrafo(
    "Reglas de enfrentamiento. Respetamos la política de pruebas de penetración de AWS: solo "
    "se prueban servicios autorizados (API Gateway, Lambda y WAF), el login administrado de "
    "Cognito queda fuera de alcance, y está prohibida cualquier inundación de solicitudes "
    "(incluso simulada). Por eso el escaneo es acotado: Nmap con tiempo lento sobre unos pocos "
    "puertos, ZAP en modo baseline (pasivo, sin escaneo activo ni fuzzing) y ráfagas cortas "
    "contra umbrales bajos cuando hay que mostrar un bloqueo. El WAF permanece apagado en esta "
    "fase (se enciende y se prueba en la Fase 5, por costo)."
)
tabla(
    "Herramientas y alcance de la prueba de caja negra",
    ["Herramienta", "Qué prueba", "Resultado"],
    [
        ["Nmap 7.9x (sin inundación, -T2)", "Puertos abiertos y cifrados TLS del endpoint", "Solo 443 abierto; TLS 1.3 únicamente"],
        ["OpenSSL s_client", "Negociación de versiones de TLS", "TLS 1.3 aceptado; TLS 1.2 rechazado"],
        ["curl sin token", "Respuesta de las rutas protegidas sin credenciales", "401/403 en todas las rutas"],
        ["OWASP ZAP (baseline pasivo)", "Araña y reglas pasivas sobre la API", "Sin rutas abiertas; alertas de configuración revisadas"],
    ],
    tam=10,
    nota_txt=(
        "Ejecución automática en pentest.yml (rol de solo lectura, OIDC). La prueba de TLS y la "
        "respuesta 401 sin token ya están verificadas en el despliegue (EVD-3-12, issue "
        "«Evidencias AWS»). La salida completa de Nmap y ZAP se publica en el issue «Evidencias "
        "Pentest» (EVD-4-01 y EVD-4-02) y se adjunta al ensamblar el informe final."
    ),
)
parrafo(
    "Resultado. La única superficie expuesta a internet es un endpoint HTTPS en el puerto 443 "
    "(API Gateway, solo TLS 1.3), protegido por el authorizer de Cognito en las 18 rutas. Sin "
    "un token válido, toda ruta responde 401. No hay puertos de administración abiertos (SSH, "
    "RDP), ni bases de datos públicas, ni servidores EC2 encendidos, ni NAT Gateway, ni "
    "dominio propio; las Lambdas y DynamoDB no son alcanzables desde internet. La Figura 9 "
    "resume el perímetro del software (punto 4 de la Fase 4: delimitación del perímetro)."
)
figura(
    "Perímetro del software: superficie de ataque expuesta a internet",
    FIGURA_PERIMETRO,
    6.5,
    "Elaboración propia. La única puerta expuesta es HTTPS 443 en API Gateway (solo TLS 1.3, "
    "authorizer de Cognito). El resto de la arquitectura es privado. Script "
    "scripts/bloque4_diagrama_perimetro.py.",
)

# ---------------------------------------------------------------- 3.2
titulo("3.2 Pentesting caja gris / blanca", 2)
parrafo(
    "En la prueba de caja gris y blanca usamos el conocimiento de la arquitectura, de la API "
    "y del código fuente para atacar la lógica de autenticación y, sobre todo, el control de "
    "acceso roto (BOLA e IDOR), que es el riesgo número uno del OWASP API Security Top 10. "
    "Montamos un arnés de pruebas (carpeta services/pentest) que ejecuta cada caso de abuso "
    "contra los mismos manejadores que se despliegan, con repositorios en memoria que imitan "
    "las condiciones de DynamoDB. El arnés corre en GitHub Actions dentro de las pruebas del "
    "flujo DevSecOps: si un control se rompiera, la prueba falla y el flujo se pone en rojo."
)
parrafo(
    "La Tabla 39 presenta los casos de abuso que dependen del servidor y su resultado. Los "
    "casos que dependen del dispositivo o de la nube (CA-07 extracción de tokens, CA-08 "
    "MITM y certificate pinning, CA-10 Frida y detección de root con freeRASP, CA-11 secretos "
    "en el APK, CA-12 payloads del WAF y CA-16 saturación con la regla rate-based) se ejecutan "
    "en la Fase 5, cuando se enciende el WAF y se prueba la app en el dispositivo."
)
seccion(True)
tabla(
    "Casos de abuso ejecutados contra los controles (caja gris)",
    ["Caso", "Abuso probado", "Control", "Respuesta esperada", "Resultado"],
    [
        ["CA-01", "Leer los movimientos de una cuenta ajena (svc-accounts)", "CTRL-01", "404 no encontrado", "Bloqueado (404)"],
        ["CA-01", "Consultar una transferencia de la que no se es origen ni destino", "CTRL-01", "404 no encontrado", "Bloqueado (404)"],
        ["CA-01", "Listar presupuestos de otro usuario (svc-budgets)", "CTRL-01", "Lista vacía (la llave usa el sub)", "Bloqueado (0 ajenos)"],
        ["CA-02", "Fuerza bruta del PIN de transacción", "CTRL-02", "Bloqueo de 15 min al 5.º fallo", "Bloqueado (5x403 y 423)"],
        ["CA-03", "Exponer teléfono o userId en las respuestas", "CTRL-03", "Datos enmascarados, sin userId", "Bloqueado (enmascarado)"],
        ["CA-04", "Mass assignment: PATCH /me con role=admin", "CTRL-04", "400 por campo no permitido", "Bloqueado (400)"],
        ["CA-05", "Exfiltración por paginación (limit alto)", "CTRL-05", "Rechazo o tope de 50", "Bloqueado (400)"],
        ["CA-05", "Cursor de paginación armado para otra cuenta", "CTRL-05", "400 solicitud inválida", "Bloqueado (400)"],
        ["CA-06", "Doble gasto: 10 solicitudes con la misma Idempotency-Key", "CTRL-06", "Una sola transferencia", "Bloqueado (1 aplicada)"],
        ["CA-09", "Acceder a /admin como cliente (sin grupo admins)", "CTRL-14", "403 y auditoría del intento", "Bloqueado (3x403 auditados)"],
        ["CA-13", "Token JWT con la firma alterada", "CTRL-18", "401 no autenticado", "Bloqueado (401)"],
    ],
    tam=10,
    total=9.0,
    nota_txt=(
        "Arnés services/pentest/pentest.test.ts, ejecutado con vitest contra los manejadores "
        "reales (evidencia EVD-4-13). Los 11 casos de servidor quedaron bloqueados; ninguno "
        "movió dinero ni expuso datos de otro usuario. Los casos de dispositivo y de WAF se "
        "ejecutan en la Fase 5."
    ),
)
seccion(False)
parrafo(
    "La prueba confirma que cada control hace lo que dice y, además, que no rompe el caso "
    "legítimo: la cuenta propia sí responde 200, el administrador real sí entra a /admin y ve "
    "los correos enmascarados, y una transferencia válida con su PIN correcto se aplica una "
    "sola vez. Un detalle importante del control de acceso: pedir un recurso ajeno responde "
    "404, no 403, para no confirmarle al atacante que el recurso existe."
)

# ---------------------------------------------------------------- 3.3
titulo("3.3 Evaluación de APIs (OWASP API Top 10)", 2)
parrafo(
    "Evaluamos la API contra el OWASP API Security Top 10 en su versión 2023. Para cada riesgo "
    "aplicable escribimos al menos una prueba contra los manejadores reales; la evidencia es "
    "el bloqueo. La Tabla 40 resume la cobertura: ocho riesgos aplican y quedaron cubiertos, y "
    "dos no aplican a esta arquitectura, con su justificación."
)
seccion(True)
tabla(
    "Cobertura del OWASP API Security Top 10 (2023)",
    ["Riesgo", "Nombre", "Control", "Prueba y resultado"],
    [
        ["API1:2023", "Broken Object Level Authorization (BOLA)", "CTRL-01", "Recurso ajeno responde 404 en cuentas, transferencias y presupuestos. Bloqueado."],
        ["API2:2023", "Broken Authentication", "CTRL-18, CTRL-02", "Sin token, firma alterada o sub cruzado: 401. Fuerza bruta del PIN: bloqueo al 5.º fallo. Bloqueado."],
        ["API3:2023", "Broken Object Property Level Authorization", "CTRL-04, CTRL-03", "Campo no permitido (mass assignment): 400. Teléfono y userId enmascarados. Bloqueado."],
        ["API4:2023", "Unrestricted Resource Consumption", "CTRL-05, CTRL-04", "Paginación con tope de 50, cursor ajeno rechazado y cuerpo mayor a 8 KiB: 413. Bloqueado."],
        ["API5:2023", "Broken Function Level Authorization (BFLA)", "CTRL-14", "Cliente en cada ruta /admin: 403 y auditoría del intento. Bloqueado."],
        ["API6:2023", "Unrestricted Access to Sensitive Business Flows", "CTRL-06, CTRL-04", "Idempotencia y carrera: una sola transferencia. Monto sobre el tope: 422. Bloqueado."],
        ["API7:2023", "Server Side Request Forgery (SSRF)", "No aplica", "Ninguna Lambda hace peticiones a URLs que elige el usuario; la única salida es a servicios de AWS por SDK, con endpoints fijos."],
        ["API8:2023", "Security Misconfiguration", "CTRL-13", "Cabeceras de seguridad (HSTS, nosniff, DENY, CSP) en toda respuesta, sin CORS; errores genéricos con correlationId. Bloqueado."],
        ["API9:2023", "Improper Inventory Management", "CTRL-13", "Ruta o método no declarado: 404 genérico, sin filtrar rutas internas ni versiones. Bloqueado."],
        ["API10:2023", "Unsafe Consumption of APIs", "No aplica", "No se consumen APIs de terceros con datos del usuario; la verificación del JWT usa el JWKS de Cognito (dominio fijo, firma validada)."],
    ],
    tam=9,
    total=9.0,
    nota_txt=(
        "Arnés services/pentest (evidencia EVD-4-12): 18 pruebas sobre los ocho riesgos "
        "aplicables, todas bloqueadas. La numeración de los riesgos es la del OWASP API "
        "Security Top 10 2023."
    ),
)
seccion(False)

# ---------------------------------------------------------------- 3.6
titulo("3.6 Evaluación de arquitectura cloud", 2)
parrafo(
    "Por último evaluamos la configuración de la nube con acceso a la arquitectura (caja "
    "blanca). Combinamos dos fuentes: el análisis de infraestructura como código con Checkov, "
    "que ya corre en cada cambio, y un escaneo de la cuenta desplegada con Prowler, que corre "
    "en pentest.yml con el rol de solo lectura. A esto se suman las verificaciones automáticas "
    "del despliegue (menor privilegio de IAM, cifrado en reposo y TLS). La Tabla 41 resume los "
    "aspectos evaluados y su evidencia."
)
tabla(
    "Evaluación de la arquitectura cloud",
    ["Aspecto", "Herramienta o evidencia", "Resultado"],
    [
        ["IaC (Terraform y Dockerfile)", "Checkov 3.3.22 (EVD-3-06)", "282 verificaciones pasan, 0 fallan, 39 omitidas con motivo"],
        ["Menor privilegio de IAM", "Simulador de políticas (EVD-3-11)", "Cada Lambda solo toca sus tablas; ninguna tiene Scan"],
        ["Cifrado en reposo", "KMS y DynamoDB (EVD-5-04)", "CMK propia con rotación; 8 tablas cifradas con PITR"],
        ["Solo TLS 1.3 en tránsito", "Prueba de TLS (EVD-3-12)", "TLS 1.3 aceptado, 1.2 rechazado"],
        ["Postura de la cuenta", "Prowler (EVD-3-09, pentest.yml)", "Escaneo de solo lectura sobre los servicios de Q-Wallet; hallazgos en el issue «Evidencias Pentest»"],
        ["Perímetro de red", "Nmap y mapeo (EVD-4-01, Figura 9)", "Un solo endpoint HTTPS expuesto; el resto privado"],
    ],
    tam=10,
    nota_txt=(
        "Prowler corre con un rol de AWS de solo lectura (SecurityAudit y ViewOnlyAccess) "
        "asumido por OIDC, acotado a los servicios del proyecto. Su reporte, con el número de "
        "cuenta y los ARN tapados, se publica en el issue «Evidencias Pentest» y se integra a "
        "esta sección al ensamblar el informe final; cualquier hallazgo real se registra como "
        "HAL y se corrige."
    ),
)
parrafo(
    "En conjunto, la evaluación de arquitectura muestra una cuenta con menor privilegio real "
    "(cada rol solo puede tocar lo suyo), cifrado con llave propia, tránsito solo por TLS 1.3 "
    "y una superficie de ataque mínima. El escaneo con Prowler completa la foto con las "
    "verificaciones de referencia de la industria (CIS) sobre la cuenta desplegada."
)

doc.save(str(SALIDA))
print("Generado:", SALIDA)
