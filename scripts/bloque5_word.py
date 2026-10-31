"""Genera las secciones 5.1 a 5.6 del informe (Fase 6, bloque 5).

Uso:
    python scripts/bloque5_diagrama_siem.py            # Figura del SIEM (EVD-5-08)
    python scripts/bloque5_residual.py figura          # mapa de calor antes y después (EVD-5-09)
    python scripts/bloque5_word.py                     # Word de las secciones
    python scripts/entrega1_estilos.py docs/entregas/Final_Secciones_5-1_a_5-6_Operaciones.docx

Mismo formato que las entregas anteriores. Las cifras salen de ejecuciones reales de los flujos
movil.yml, waf-siem.yml, infra.yml y pentest.yml; sus evidencias están copiadas en
docs/evidencias/bloque5/ (desde la rama evidencias-ci y los issues de evidencias).
El riesgo residual se calcula con scripts/bloque5_residual.py.
Numeración provisional: continúa el bloque 4 (Tabla 41, Figura 9); se ajusta al ensamblar.
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
SALIDA = RAIZ / "docs/entregas/Final_Secciones_5-1_a_5-6_Operaciones.docx"

TABLA_INICIAL = 42   # el bloque 4 terminó en la Tabla 41
FIGURA_INICIAL = 10  # y en la Figura 9

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




# ================================================================ datos
import json as _json
import sys as _sys

_sys.path.insert(0, str(RAIZ / "scripts"))
import bloque5_residual as _res  # noqa: E402

EVD = RAIZ / "docs/evidencias/bloque5"
R = _json.load(open(EVD / "resultados.json", encoding="utf-8"))
FILAS = _res.cargar()
RES = _res.resumen(FILAS)

# Tipo, impacto de negocio y dueño de cada riesgo: Tabla 21 del informe de la Entrega 1.
_t21 = [t for t in docx.Document(str(PLANTILLA)).tables if [c.text.strip() for c in t.rows[0].cells][:2] == ["RSK", "AME"]][0]
T21 = {r.cells[0].text.strip(): [c.text.strip() for c in r.cells] for r in _t21.rows[1:]}


def pxi(p, i):
    return f"{p}×{i} = {p * i}"


# ================================================================ contenido
parrafo(
    "La sección 5 cubre la Fase 6 del enunciado: operar la aplicación con controles que "
    "detectan y frenan ataques en tiempo real, y cerrar el ciclo de gestión del riesgo. En las "
    "fases anteriores construimos Q-Wallet con sus controles desde el diseño y demostramos con "
    "pruebas que funcionan; aquí agregamos la capa de operación: el firewall de aplicaciones "
    "(WAF), la protección en tiempo de ejecución de la app (RASP), la centralización y "
    "correlación de eventos (SIEM), las alertas, la gestión continua de vulnerabilidades y la "
    "decisión formal sobre cada riesgo, con el mapa de calor antes y después de los controles."
)
parrafo(
    "Igual que en el pentest, todas las pruebas de esta fase corren en GitHub Actions: el flujo "
    "waf-siem.yml enciende el WAF, lanza ataques acotados, lee los registros y comprueba que las "
    "alarmas se disparan, y el flujo movil.yml compila el APK de producción y lo ataca en un "
    "emulador Android. Las evidencias quedan en los issues «Evidencias WAF y SIEM» y «Evidencias "
    "Móvil» del repositorio, con el número de cuenta, los ARN y los correos tapados."
)

# ---------------------------------------------------------------- 5.1
titulo("5.1 WAF", 2)
parrafo(
    "Pusimos AWS WAF delante de la etapa v1 de API Gateway, en modo regional. Todo lo que llega "
    "desde internet pasa primero por el WAF, que evalúa cada solicitud contra sus reglas antes "
    "de que toque el autorizador de Cognito o una Lambda (CTRL-17, capa 5). La acción por "
    "defecto es permitir y cada regla bloquea lo que reconoce como ataque. La Tabla 42 resume las "
    "reglas y qué parte del OWASP Top 10 (2025) cubre cada una."
)
tabla(
    "Reglas del AWS WAF de Q-Wallet",
    ["Prioridad", "Regla", "Qué bloquea", "OWASP Top 10:2025"],
    [
        ["10", "AWSManagedRulesCommonRuleSet", "XSS, lectura de archivos (path traversal), inclusión remota, SSRF a metadatos, cuerpos de más de 8 KB, solicitudes sin User-Agent", "A01, A05"],
        ["15", "AWSManagedRulesSQLiRuleSet", "Inyección SQL en parámetros, cuerpo, cabeceras y cookies", "A05"],
        ["20", "AWSManagedRulesKnownBadInputsRuleSet", "Entradas maliciosas conocidas, como Log4Shell (${jndi:...})", "A03"],
        ["30", "limite-por-ip (rate-based)", "Más de 100 solicitudes de una misma IP en 5 minutos", "Abuso / DoS de capa 7"],
    ],
    tam=10,
    nota_txt=(
        "El WAF registra cada decisión en el grupo de CloudWatch aws-waf-logs-qwallet, cifrado con "
        "la CMK, y redacta la cabecera Authorization para no guardar tokens (CTRL-09). Capacidad "
        f"usada: {R['waf']['wcu']} de 1 500 unidades (WCU)."
    ),
)
parrafo(
    "Al preparar esta fase revisamos el contenido de cada grupo de reglas y encontramos una "
    "brecha: el conjunto común (CRS) no trae firmas de inyección SQL. Con solo CRS y Known Bad "
    "Inputs, el WAF no cubría la categoría de inyección (A05:2025). Lo registramos como hallazgo "
    "HAL-07 y lo corregimos agregando AWSManagedRulesSQLiRuleSet con prioridad 15."
)
parrafo(
    "Decisión de operación por costo. El WAF cuesta unos US$9 al mes mientras existe (US$5 por "
    "la lista de control y US$1 por cada grupo de reglas), casi el doble del presupuesto de US$5 "
    "del proyecto. Por eso Terraform lo crea solo cuando se prueba (variable waf_habilitado) y el "
    "flujo de prueba lo apaga siempre al terminar, aunque algo falle. En operación normal la "
    "protección de perímetro queda en el throttling de API Gateway (ráfaga de 20 y 10 solicitudes "
    "por segundo) y en la validación estricta de cada Lambda. La sección 5.6 refleja esta "
    "decisión en el riesgo residual de RSK-11."
)
parrafo(
    "Prueba. Con el WAF encendido lanzamos un ataque por cada tipo de regla, una sola solicitud "
    "por ataque, y una ráfaga corta para la regla de límite por IP que se detiene en cuanto "
    "aparece el bloqueo (política de pentest de AWS: sin inundación). Cada solicitud lleva un "
    "marcador (caso=Cxx) para encontrarla después en los registros del WAF y saber qué regla la "
    "detuvo. La Tabla 43 resume el resultado."
)
tabla(
    "Ataques contra la API con el WAF encendido",
    ["Caso", "Ataque", "Esperado", "Obtenido", "Regla que decidió"],
    R["waf"]["casos"],
    tam=9,
    nota_txt=R["waf"]["nota"],
)
parrafo(R["waf"]["conclusion"])

# ---------------------------------------------------------------- 5.2
titulo("5.2 RASP / Protección en tiempo de ejecución", 2)
parrafo(
    "La protección en tiempo de ejecución trabaja en dos lados. En el teléfono, la app se "
    "defiende sola con freeRASP (Talsec), que vigila el entorno mientras la app corre: root, "
    "herramientas de instrumentación como Frida, depurador, emulador, APK re-firmado y otras "
    "señales (CTRL-15). En el servidor, cada Lambda detecta comportamientos anómalos en el "
    "momento en que ocurren (un PIN fallado cinco veces, un acceso a un objeto ajeno, una entrada "
    "con campos no permitidos), los rechaza y deja un evento estructurado que el SIEM convierte "
    "en alerta (secciones 5.3 y 5.4)."
)
parrafo(
    "Al revisar la app encontramos que freeRASP estaba instalado desde el inicio pero nunca se "
    "iniciaba, y que al iniciarlo la compilación fallaba porque faltaba una dependencia (buffer). "
    "Lo registramos como HAL-11 y lo corregimos: la app inicia freeRASP en el arranque y aplica "
    "la política de reacción de la Tabla 44. En la versión de desarrollo solo registra, para no "
    "bloquear el emulador de trabajo."
)
tabla(
    "Política de reacción de freeRASP en la versión de producción",
    ["Amenaza detectada", "Qué significa", "Reacción"],
    [
        ["privilegedAccess", "El teléfono tiene root", "Bloquear la app"],
        ["hooks", "Frida u otra herramienta modifica la app en memoria", "Bloquear la app"],
        ["debug", "Un depurador está conectado", "Bloquear la app"],
        ["appIntegrity", "El APK fue modificado o firmado con otro certificado", "Bloquear la app"],
        ["simulator", "La app corre en un emulador", "Bloquear la app"],
        ["unofficialStore, devMode, adbEnabled, passcode, systemVPN y otras", "Señales del entorno que no prueban un ataque", "Solo registrar"],
    ],
    tam=10,
    nota_txt=(
        "Bloquear significa que la app muestra una pantalla de seguridad y no presenta datos ni "
        "permite operar. Las detecciones se registran con una marca técnica sin datos personales."
    ),
)
parrafo(
    "En la misma conexión con la API activamos el pinning de llave pública (CTRL-08): la app "
    "solo acepta conexiones cuya cadena de certificados pase por una de las cuatro raíces de "
    "Amazon Trust Services. Antes de compilar, el flujo comprueba que la cadena real del endpoint "
    f"pasa por una llave fijada ({R['movil']['pines']}). Como prueba mínima de la conexión, la "
    "app llama a GET /me sin token al arrancar: lo correcto es un 401."
)
parrafo(
    "Prueba en emulador. El flujo movil.yml compila el APK de producción (Hermes y R8), lo "
    "instala en un emulador Android 13 con root y ejecuta cuatro escenarios de ataque. La Tabla "
    "45 resume el resultado."
)
tabla(
    "Pruebas de la app en emulador Android",
    ["Escenario", "Ataque", "Resultado", "EVD"],
    R["movil"]["escenarios"],
    tam=9,
    nota_txt=R["movil"]["nota"],
)
if R["movil"].get("captura"):
    figura("Pantalla de bloqueo de la app al detectar el emulador (freeRASP)", EVD / R["movil"]["captura"], 2.4,
           "Captura tomada por el flujo movil.yml en el emulador de GitHub Actions (EVD-5-03).")
parrafo(
    "El análisis estático del mismo APK completa la protección en tiempo de ejecución: el código "
    f"JavaScript va como bytecode de Hermes, R8 renombró {R['movil']['r8']} y gitleaks y la "
    "búsqueda de patrones no encontraron secretos (EVD-4-11 y EVD-5-11). La revisión del "
    "manifiesto mostró permisos que la app no usa (almacenamiento externo, ventana superpuesta, "
    "imágenes y arranque del sistema), heredados de librerías. Los registramos como HAL-12 y los "
    "bloqueamos en app.json; el APK corregido ya no los pide."
)

# ---------------------------------------------------------------- 5.3
titulo("5.3 SIEM / Correlación de eventos", 2)
parrafo(
    "El SIEM centraliza los registros de auditoría y los convierte en señales. En la Entrega 1 lo "
    "planteamos con Wazuh en un contenedor local; al llegar a esta fase lo cambiamos por los "
    "servicios nativos de AWS (CloudWatch Logs, filtros de métrica, Logs Insights y alarmas). "
    "Wazuh necesita 4 GB de memoria o más y un servidor encendido, lo que no cabe en el "
    "presupuesto de US$5, mientras que CloudWatch no tiene servidores propios y cuesta menos de "
    "US$1 al mes con este volumen. Wazuh queda en el roadmap (sección 6.3). La Figura 10 muestra "
    "el diseño."
)
figura("SIEM de Q-Wallet en CloudWatch: fuentes, correlación, alerta y respuesta",
       RAIZ / "docs/evidencias/EVD-5-08_siem.png", 6.5,
       "Elaboración propia (EVD-5-08). Toda la configuración está en infra/monitoreo.tf.")
tabla(
    "Fuentes de eventos del SIEM",
    ["Fuente", "Qué registra", "Retención y cifrado"],
    [
        ["CloudTrail (multirregión)", "Toda llamada a la API de AWS de la cuenta y cada invocación de las Lambdas de Q-Wallet (eventos de datos)", "365 días en CloudWatch y archivo en S3 con validación de integridad; CMK"],
        ["Log de acceso de API Gateway", "IP, usuario (sub), método, ruta, estado HTTP, decisión del WAF y latencia; sin tokens ni cuerpos", "365 días; CMK"],
        ["Logs JSON de las 5 Lambdas", "Evento, código de rechazo y correlationId, con tokens y PII redactados (CTRL-09)", "365 días; CMK"],
        ["Logs del WAF", "Acción y regla que decidió cada solicitud; Authorization redactada", "365 días; CMK"],
        ["Tabla qwallet-auditoria (DynamoDB)", "Acciones de negocio: transferencias, PIN, bloqueo de usuarios", "PITR; CMK"],
    ],
    tam=10,
)
parrafo(
    "La correlación se hace en dos niveles. Primero, 14 reglas (filtros de métrica) reconocen un "
    "patrón de ataque en una fuente y cuentan cada aparición; la Tabla 47 las resume. Segundo, "
    "cinco consultas guardadas de Logs Insights cruzan fuentes: siguen una solicitud de punta a "
    "punta por su correlationId (API Gateway y la Lambda que la atendió), agrupan los rechazos por "
    "usuario e IP para detectar enumeración de objetos o fuerza bruta del PIN, y separan las "
    "llamadas a AWS negadas por rol."
)
tabla(
    "Reglas de correlación del SIEM",
    ["Regla", "Fuente", "Patrón que reconoce", "Amenaza o caso"],
    [
        ["pin_bloqueado / pin_incorrecto", "Lambdas", "Código de rechazo del PIN", "AME-38, CA-02"],
        ["acceso_prohibido", "Lambdas", "Acceso a función u objeto ajeno", "AME-17, AME-23, CA-01, CA-09"],
        ["entrada_invalida", "Lambdas", "Campos no permitidos o cuerpo demasiado grande", "AME-12, AME-21, CA-04"],
        ["error_no_controlado", "Lambdas", "Excepción no prevista", "AME-14"],
        ["api_no_autenticado / api_limite / api_bloqueo_waf", "API Gateway", "Respuestas 401, 429 y bloqueos del WAF", "AME-11, AME-16, CA-06, CA-13"],
        ["trail_no_autorizado", "CloudTrail", "Llamadas negadas por IAM (CIS 4.1); excluye el escaneo autorizado de Prowler", "AME-19, AME-27"],
        ["trail_uso_root / trail_consola_sin_mfa", "CloudTrail", "Uso del usuario raíz; consola sin MFA (CIS 4.2 y 4.3)", "AME-04"],
        ["trail_auditoria_y_llaves", "CloudTrail", "Cambios a CloudTrail, a la CMK o al propio SIEM; borrado de datos", "AME-28, AME-29, AME-31"],
        ["trail_cambios_iam / trail_admin_cognito", "CloudTrail", "Cambios de permisos; bloqueo de usuarios o cambios en Cognito", "AME-03, AME-24"],
    ],
    tam=9,
    nota_txt=(
        "Antes de usarlas, cada regla se probó contra una muestra de ataque y una normal con el "
        f"formato real de cada fuente: {R['siem']['reglas']} (EVD-5-06a)."
    ),
)
parrafo(R["siem"]["correlacion"])

# ---------------------------------------------------------------- 5.4
titulo("5.4 Alertas y dashboards", 2)
parrafo(
    "Cada regla que indica un ataque en curso tiene una alarma de CloudWatch. Cuando la alarma "
    "pasa a estado ALARM publica en el tema SNS qwallet-alertas, cifrado con la CMK y que solo "
    "acepta mensajes de las alarmas de la cuenta, y el tema envía un correo al responsable. La "
    "Tabla 48 lista las alarmas, su umbral y la primera acción de respuesta; el dueño de la "
    "respuesta es el Lead Security Architect (I1)."
)
tabla(
    "Alarmas de seguridad y primera respuesta",
    ["Alarma", "Se dispara con", "Severidad", "Primera acción"],
    [
        ["uso-root", "1 uso del usuario raíz en 5 min", "Crítica", "Confirmar con el dueño; si no fue él, cambiar clave y revisar CloudTrail"],
        ["consola-sin-mfa", "1 inicio de sesión sin MFA", "Crítica", "Revocar sesiones del usuario y exigir MFA"],
        ["auditoria-y-llaves", "1 cambio a CloudTrail, la CMK, el SIEM o borrado de datos", "Crítica", "Comparar con despliegues aprobados; si no lo es, restaurar y bloquear el rol"],
        ["pin-bloqueado", "1 PIN bloqueado en 5 min", "Alta", "Revisar el usuario con la consulta de rechazos; contactarlo por otro canal (CTRL-23)"],
        ["acceso-prohibido", "5 accesos prohibidos en 5 min", "Alta", "Identificar usuario e IP; bloquear la cuenta si es enumeración"],
        ["aws-no-autorizado", "5 llamadas negadas por IAM en 5 min", "Alta", "Identificar el rol en CloudTrail; revocar su sesión si no es esperada"],
        ["rafaga-401", "50 solicitudes sin token válido en 5 min", "Media", "Revisar IPs sospechosas; encender el WAF si sigue"],
        ["throttling", "20 respuestas 429 en 5 min", "Media", "Igual que la anterior"],
        ["error-no-controlado", "1 error no controlado", "Media", "Seguir el correlationId; abrir HAL si es un defecto"],
        ["waf-bloqueos", "10 bloqueos del WAF en 5 min (solo con WAF encendido)", "Media", "Revisar la consulta de bloqueos por regla e IP"],
    ],
    tam=9,
    nota_txt=(
        "Las alarmas avisan también cuando vuelven a OK. Las métricas solo publican datos cuando hay "
        "eventos, por lo que una alarma sin datos se considera normal (treat_missing_data = notBreaching)."
    ),
)
parrafo(R["alertas"]["prueba"])
tabla(
    "Disparo real de las alarmas durante la prueba",
    ["Alarma", "Qué la disparó", "Estado", "Aviso por correo"],
    R["alertas"]["disparos"],
    tam=10,
    nota_txt=R["alertas"]["nota"],
)
parrafo(
    "El tablero qwallet-seguridad reúne en una sola pantalla el estado de las alarmas, los "
    "rechazos de la aplicación por regla, el perímetro (401, 429 y bloqueos del WAF), los eventos "
    "de CloudTrail por regla, el tráfico de API Gateway y una tabla con los usuarios que acumulan "
    "rechazos. La Figura 12 es una de sus gráficas durante la prueba, generada por la API de "
    "CloudWatch sin capturas manuales de la consola."
)
if R["alertas"].get("grafica"):
    figura("Perímetro de la API durante la prueba del WAF (tablero qwallet-seguridad)",
           EVD / R["alertas"]["grafica"], 6.3,
           "Imagen generada con GetMetricWidgetImage de CloudWatch (EVD-5-07).")

# ---------------------------------------------------------------- 5.5
titulo("5.5 Gestión continua de vulnerabilidades", 2)
parrafo(
    "La gestión de vulnerabilidades no termina con el pentest: corre en cada cambio y también "
    "cuando no hay cambios. El ciclo tiene cuatro pasos. Detectar: en cada pull request corren "
    "Semgrep, CodeQL, gitleaks, npm audit, Trivy y Checkov; después de cada despliegue corren "
    "Prowler y ZAP; Dependabot vigila las dependencias todos los días; y ahora también MobSF y "
    "el análisis del APK. Priorizar: una compuerta detiene el flujo ante avisos High o Critical "
    "y solo deja pasar excepciones aprobadas con motivo y fecha de vencimiento. Corregir: cada "
    "hallazgo real se registra como HAL y se corrige por rama y pull request. Verificar: la misma "
    "herramienta vuelve a correr y su resultado limpio es la evidencia de cierre."
)
parrafo(
    "El ciclo se puso a prueba solo durante esta fase. El 31 de octubre se publicaron avisos "
    "nuevos de node-forge, una dependencia indirecta de las herramientas de compilación de Expo. "
    "La compuerta de SCA, que el día anterior pasaba, empezó a fallar en main sin que nadie "
    "cambiara el código. Lo registramos como HAL-06, forzamos la versión corregida (1.4.2) con "
    "overrides de npm y quitamos la excepción que ya no hacía falta. Es el escenario para el que "
    "existe la gestión continua: la vulnerabilidad apareció después del despliegue y se detectó "
    "y corrigió el mismo día."
)
tabla(
    "Hallazgos reales y su estado al cierre de la Fase 6",
    ["HAL", "Origen", "Hallazgo", "Tratamiento", "Estado"],
    R["hal"],
    tam=9,
    nota_txt=(
        "HAL-01 a HAL-05 vienen de las fases anteriores (sección 3). Las excepciones temporales "
        "vencen el 28 de noviembre de 2026: si no se corrigen antes, la compuerta vuelve a fallar."
    ),
)
parrafo(R["prowler"]["texto"])
tabla(
    "Decisión sobre los hallazgos de Prowler",
    ["Hallazgos de Prowler", "Decisión", "Motivo"],
    R["prowler"]["filas"],
    tam=9,
)
parrafo(R["mobsf"]["texto"])

# ---------------------------------------------------------------- 5.6
titulo("5.6 Tratamiento del riesgo", 2)
parrafo(
    "En la sección 2.5 asignamos a cada uno de los 41 riesgos un tratamiento y proyectamos el "
    "riesgo residual esperado. En esta sección lo verificamos: para cada amenaza revisamos si "
    "sus controles quedaron probados con un ataque real, solo comprobados por configuración, o "
    "solo en parte, y con eso calculamos el riesgo residual verificado. La regla es conservadora: "
    "si el control se probó o su configuración desplegada se comprobó, se mantiene el residual "
    "proyectado; si quedó en parte, la probabilidad sube un nivel (sin pasar del inherente). Dos "
    "amenazas se re-evaluaron porque el cambio de SIEM cambió su análisis."
)
_estados = RES["estados"]
parrafo(
    f"Resultado: de las 41 amenazas, {_estados['prueba']} quedaron verificadas con una prueba, "
    f"{_estados['configuracion']} por configuración, {_estados['parcial']} en parte, "
    f"{_estados.get('aceptado', 0)} se mantiene aceptada y {_estados.get('eliminado', 0)} se eliminó. "
    f"El riesgo inherente sumaba {RES['suma'][0]} puntos (P×I); el residual proyectado, "
    f"{RES['suma'][1]}; y el residual verificado, {RES['suma'][2]}, una reducción del "
    f"{round(100 * (RES['suma'][0] - RES['suma'][2]) / RES['suma'][0])} %. Ninguna amenaza quedó "
    f"en nivel Crítico; quedaron {RES['verificado']['Alto']} en Alto, {RES['verificado']['Medio']} "
    f"en Medio y {RES['verificado']['Bajo']} en Bajo. La Figura 13 compara el mapa de calor antes "
    "y después."
)
figura("Mapa de calor de riesgo antes (inherente) y después (residual verificado)",
       RAIZ / "docs/evidencias/EVD-5-09_heatmap_antes_despues.png", 6.5,
       "Elaboración propia con scripts/bloque5_residual.py a partir del modelo de amenazas y de "
       "docs/threat-model/verificacion_bloque5.json (EVD-5-09). Escala P×I de la sección 2.5.1.")
cambios = [f for f in FILAS if (f["Pv"], f["Iv"]) != (f["Pr"], f["Ir"])]
tabla(
    "Amenazas cuyo residual verificado difiere del proyectado",
    ["RSK", "Amenaza", "Proyectado", "Verificado", "Motivo"],
    [[f["rsk"], f["titulo"], pxi(f["Pr"], f["Ir"]), pxi(f["Pv"], f["Iv"]), f["nota"]] for f in cambios],
    tam=9,
)
parrafo(R["tratamiento"]["altos"])
parrafo(
    "Sobre las cinco opciones de tratamiento del enunciado: mitigamos 39 riesgos con controles; "
    "aceptamos uno (RSK-01, una sola región por costo); y eliminamos uno (RSK-41), porque al "
    "cambiar a un SIEM dentro de la cuenta ya no existen credenciales de AWS fuera de ella. No "
    "transferimos ningún riesgo: Q-Wallet no contrata un seguro ni un tercero que responda por "
    "sus pérdidas, y AWS solo responde por su parte del modelo de responsabilidad compartida. "
    "Tampoco evitamos riesgos dentro del modelo, aunque la decisión de no procesar tarjetas ni "
    "dinero real (sección 1.3) es en sí una forma de evitar el riesgo de PCI DSS y de fraude real."
)
parrafo(
    "La Tabla 51 es la matriz de decisiones por riesgo que pide el enunciado: para cada uno, su "
    "tipo, el impacto en el negocio, la decisión, los controles, cómo se verificó y el riesgo "
    "antes y después."
)

seccion(True)
filas51 = []
for f in FILAS:
    t21 = T21[f["rsk"]]
    est = {"prueba": "Prueba", "configuracion": "Configuración", "parcial": "Parcial",
           "aceptado": "Aceptado", "eliminado": "Eliminado"}[f["estado"]]
    filas51.append([
        f["rsk"], f["titulo"], t21[7], t21[8], f["trat"], ", ".join(c[5:] for c in f["ctrls"]) or "—",
        est, f"{pxi(f['P'], f['I'])}\n{_res.nivel(f['P'] * f['I'])}", f"{pxi(f['Pv'], f['Iv'])}\n{_res.nivel(f['Pv'] * f['Iv'])}",
    ])
tabla(
    "Matriz de decisiones por riesgo con el residual verificado",
    ["RSK", "Amenaza", "Tipo", "Impacto", "Decisión", "CTRL", "Verificación", "Antes", "Después"],
    filas51,
    tam=8,
    total=9.0,
    nota_txt=(
        "Tipo de riesgo e impacto de negocio de la Tabla 21. CTRL: número de los controles de la "
        "sección 4.2. Verificación: Prueba = el ataque se ejecutó y quedó bloqueado; Configuración = "
        "se leyó la configuración desplegada; Parcial = parte del control falta o no se pudo probar. "
        "Antes = riesgo inherente; Después = residual verificado (P×I y nivel)."
    ),
)
seccion(False)
parrafo(R["tratamiento"]["cierre"])

doc.save(str(SALIDA))
print("Generado:", SALIDA)
