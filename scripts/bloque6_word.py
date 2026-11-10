"""Genera la sección 6 del informe final: dictamen y mejores prácticas (6.1 a 6.5; bloque 6).

Uso:
    python scripts/bloque6_word.py
    python scripts/entrega1_estilos.py docs/entregas/Final_Seccion_6_Dictamen.docx

Mismo formato que las secciones anteriores (utilidades copiadas de bloque5_word.py). Las cifras
salen de scripts/bloque5_residual.py, de docs/REGISTRO_RIESGOS.md y de las secciones 1 a 5;
el script se detiene si el residual verificado no es el del bloque 7 (580 -> 202).
Las referencias (6.6) se arman al ensamblar el informe (scripts/final_ensamblar.py).
Numeración: las tablas de la sección 6 empiezan en la 54 (la sección 5 termina en la 53); las
referencias a tablas de las secciones 3 y 4 usan la numeración de los Word por bloque y las
renumera final_ensamblar.py.
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
SALIDA = RAIZ / "docs/entregas/Final_Seccion_6_Dictamen.docx"

TABLA_INICIAL = 54   # la sección 5 terminó en la Tabla 53
FIGURA_INICIAL = 14  # y en la Figura 13

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
import re as _re
import sys as _sys

_sys.path.insert(0, str(RAIZ / "scripts"))
import bloque5_residual as _res  # noqa: E402

FILAS = _res.cargar()
RES = _res.resumen(FILAS)
S0, _, S2 = RES["suma"]
assert (S0, S2) == (580, 202), RES["suma"]
assert RES["verificado"]["Crítico"] == 0 and RES["verificado"]["Alto"] == 1
assert dict(RES["estados"]) == {"aceptado": 1, "parcial": 2, "configuracion": 6, "prueba": 31, "eliminado": 1}


def pxi(p, i):
    return f"{p}×{i} = {p * i}"


# ================================================================ contenido
titulo("6. Dictamen y mejores prácticas", 1)
parrafo(
    "Esta sección cierra el proyecto. Primero damos el dictamen y las conclusiones, contrastando "
    "cada objetivo específico de la sección 1.2 con el resultado medido. Después proponemos las "
    "recomendaciones técnicas y el roadmap para mantener la seguridad de forma continua, y "
    "terminamos con las lecciones aprendidas, los anexos y las referencias."
)

# ---------------------------------------------------------------- 6.1
titulo("6.1 Conclusiones", 2)
titulo("6.1.1 Dictamen", 3)
parrafo(
    "Con base en las pruebas de las secciones 3 a 5, dictaminamos que Q-Wallet, en su versión 1 "
    "desplegada en AWS, tiene un riesgo residual aceptable. Las 41 amenazas "
    "del modelo STRIDE pasaron de una suma de riesgo inherente de 580 puntos a un residual "
    "verificado de 202, una reducción del 65 %. No queda ninguna amenaza en nivel Crítico, que al "
    "inicio eran 18, y queda una sola en nivel Alto, RSK-11 (saturación de la API y consumo de "
    "costo), aceptada de forma temporal y formal por el dueño del riesgo con un plan de acción "
    "(sección 5.6)."
)
parrafo(
    "El dictamen es favorable para el alcance evaluado y tiene tres condiciones antes de "
    "pasar a producción: encender el WAF de forma permanente, que baja RSK-11 a Medio; "
    "ajustar la capacidad de la API para que una ráfaga de clientes autenticados reciba 429 y no "
    "500 (HAL-17), subiendo el límite de ejecuciones simultáneas de Lambda y dejando la ráfaga de "
    "API Gateway por debajo de él; y subir la app a Expo SDK 58 antes del 31 de enero de 2027, "
    "fecha en que vencen las dos excepciones de dependencias que siguen abiertas (HAL-02 y la "
    "parte de HAL-03 que corresponde a zod). Ninguna de las tres exige rediseñar la "
    "arquitectura: las tres están en el roadmap de la sección 6.3. La condición que tenía la "
    "versión anterior de este dictamen, terminar el inicio de sesión real y repetir CA-07 con un "
    "token, quedó cumplida (Tabla 45)."
)
titulo("6.1.2 Cumplimiento de los objetivos", 3)
parrafo(
    "La Tabla 54 compara la meta de cada objetivo específico (Tabla 2) con el resultado "
    "obtenido y la evidencia que lo respalda. Cumplimos cuatro objetivos por completo y uno "
    "(OE3) en 12 de sus 13 casos; explicamos la diferencia debajo de la tabla."
)
tabla(
    "Cumplimiento de los objetivos específicos",
    ["OE", "Meta (Tabla 2)", "Resultado obtenido", "Evidencia", "Estado"],
    [
        ["OE1", "≥ 25 activos en 6 tipos; 100 % de amenazas con DREAD y P×I; 7 capas",
         "28 activos en 6 tipos; 41 amenazas STRIDE con DREAD y P×I; al menos un riesgo en cada una de las 7 capas",
         "Tablas 12, 17, 20 a 22", "Cumplido"],
        ["OE2", "0 hallazgos altos o críticos sin justificar en la rama principal; flujo con SAST, SCA, secretos e IaC",
         "Arquitectura desplegada con Terraform por OIDC; Checkov 282 pasan y 0 fallan; las compuertas detuvieron cambios reales (HAL-06, HAL-15); 2 avisos altos aceptados con motivo y fecha",
         "Tablas 29, 30, 31, 32, 33 y 37; EVD-3-01 a 3-06", "Cumplido"],
        ["OE3", "13 de 13 casos de abuso con evidencia de bloqueo",
         "12 de 13 bloqueados con evidencia, incluido CA-07 con un token real; CA-03 a medias (datos enmascarados; el 429 se demostró en GET /me y no en la búsqueda por teléfono). Además, 18 de 18 pruebas OWASP API y 9 de 9 ataques al WAF bloqueados",
         "Tablas 39, 40, 43 y 45; EVD-4-03 a 4-13, EVD-5-02, EVD-7-01 y 7-05", "Parcial (92 %)"],
        ["OE4", "0 críticos; altos solo con aceptación justificada; 100 % de hallazgos con plan",
         "0 críticos y 1 alto aceptado (RSK-11); 17 de 17 hallazgos con decisión: 13 cerrados, 2 aceptados, 1 descartado y 1 abierto con plan (HAL-17)",
         "Tablas 50 a 53; Figura 13; EVD-5-09", "Cumplido"],
        ["OE5", "100 % de amenazas con trazabilidad; informe en formato UMG y APA 7",
         "Trazabilidad de las 41 amenazas hasta su evidencia y su residual (Anexo B); este informe",
         "Tabla 59", "Cumplido"],
    ],
    tam=9,
    nota_txt=(
        "Elaboración propia. Los números de tabla y figura son los de este informe. «Parcial» "
        "indica que la meta no se alcanzó completa; la causa y el plan están en el texto."
    ),
)
parrafo(
    "La meta de OE3 no se cumplió completa por un caso, y en él el control no falló ante el "
    "ataque. En CA-03 (enumerar usuarios por teléfono) los datos salieron enmascarados, pero en "
    "la prueba de la Fase 4 el límite de solicitudes no devolvió el código 429. Al repetir la "
    "prueba de saturación con un token real (EVD-7-05) entendimos por qué: API Gateway solo cuenta "
    "para el límite las solicitudes que pasan el authorizer, y con un token el límite sí respondió "
    "429. Esa prueba usó GET /me y no la búsqueda por teléfono, que tiene la misma configuración; "
    "repetir CA-03 sobre esa ruta es parte de R4. CA-07 (extraer tokens del dispositivo), que en "
    "la versión anterior no tenía token que robar, se cerró con un inicio de sesión real: con root "
    "el refresh token solo aparece cifrado con Android Keystore (Tabla 45)."
)
titulo("6.1.3 Conclusiones por componente", 3)
parrafo(
    "Análisis de riesgos y activos. Partir de un inventario ISO/IEC 27001 y de diagramas de "
    "flujo de datos permitió que cada amenaza tuviera un activo, una frontera de confianza y "
    "una capa de defensa. Esa trazabilidad fue lo que después hizo posible medir el residual "
    "con pruebas y no con supuestos: de las 41 amenazas, 31 se verificaron con un ataque real, "
    "6 leyendo la configuración desplegada, 2 quedaron parciales, 1 se aceptó y 1 se eliminó "
    "al cambiar la arquitectura (el SIEM local se reemplazó por CloudWatch)."
)
parrafo(
    "Arquitectura cloud y DevSecOps. La arquitectura sin servidor (API Gateway, Cognito, Lambda "
    "y DynamoDB) cumplió el principio de Zero Trust con un costo compatible con el presupuesto: "
    "cada solicitud se autentica con un token de 15 minutos, cada Lambda tiene su propio rol con "
    "acceso solo a sus tablas y todo se cifra con una llave KMS propia y TLS 1.3. El flujo de "
    "GitHub Actions no solo revisó el código: detuvo dos veces el trabajo sin que nadie cambiara "
    "una línea, cuando se publicaron vulnerabilidades nuevas en node-forge (HAL-06) y en la "
    "imagen base de Lambda (HAL-15). Eso confirma que la seguridad continua tiene que vigilar "
    "también lo que no escribimos."
)
parrafo(
    "Ciberdefensa. Las pruebas de caja gris y caja negra confirmaron los controles de "
    "autorización, el PIN con bloqueo, la idempotencia de las transferencias y el perímetro "
    "(solo el puerto 443, solo TLS 1.3 y todo 401 sin token). La prueba más valiosa fue la de "
    "intercepción en el emulador: encontró que la fijación de certificados no protegía la "
    "conexión, porque en Expo SDK 57 la función fetch no pasa por el componente que aplica los "
    "pines (HAL-13). Ninguna revisión de código ni escáner lo había detectado."
)
parrafo(
    "Ciberseguridad y operación. El WAF bloqueó los nueve ataques de la prueba con la regla "
    "correcta, freeRASP detectó el emulador, el root y la instrumentación con Frida, y el SIEM en "
    "CloudWatch detectó y avisó por correo en unos seis minutos. Leer los registros del SIEM "
    "también sirvió para corregirnos: así encontramos que el log de acceso de API Gateway estaba "
    "vacío (HAL-14) y que un hallazgo de Prowler era un falso positivo (HAL-10)."
)

# ---------------------------------------------------------------- 6.2
titulo("6.2 Recomendaciones técnicas", 2)
parrafo(
    "Las recomendaciones de la Tabla 55 salen de los riesgos que quedaron en Alto o parciales, "
    "de los hallazgos abiertos o aceptados y de las verificaciones de Prowler que aceptamos por "
    "costo. Las ordenamos por prioridad: Alta es antes de pasar a producción; Media, en los "
    "primeros meses de operación; Baja, mejora continua."
)
tabla(
    "Recomendaciones técnicas por prioridad",
    ["#", "Recomendación", "Riesgo o hallazgo", "Prioridad", "Costo estimado"],
    [
        ["R1", "Encender el AWS WAF de forma permanente en la etapa de producción, con las mismas cuatro reglas y su alarma", "RSK-11, HAL-16", "Alta", "~US$9 al mes (sección 5.1)"],
        ["R2", "Conectar las pantallas de saldo, movimientos, presupuestos y transferencias con la API (hoy muestran datos de ejemplo) y probar el desbloqueo con biometría en un teléfono físico", "RSK-02; Figura 101", "Media", "Sin costo de AWS; trabajo de desarrollo"],
        ["R3", "Subir la app a Expo SDK 58 y quitar las dos excepciones de npm audit antes del 31-ene-2027", "HAL-02, HAL-03 (zod)", "Alta", "Sin costo; repetir las pruebas de movil.yml"],
        ["R4", "Pedir el aumento del límite de ejecuciones simultáneas de Lambda (Service Quotas), dejar la ráfaga de API Gateway por debajo de él y repetir la prueba de saturación con token, incluida la búsqueda por teléfono (CA-03)", "HAL-17, CA-03", "Alta", "Sin costo"],
        ["R5", "Usar un dominio propio con certificado de ACM, para tener HSTS también en la raíz del host y fijar un nombre estable en la app", "HAL-09", "Media", "Costo anual del dominio"],
        ["R6", "Firmar la app con Play App Signing y registrar esa huella en freeRASP, para detectar copias reempaquetadas", "MobSF (certificado de depuración)", "Media", "Pago único de la cuenta de desarrollador de Google Play"],
        ["R7", "Administrar la cuenta con un usuario de IAM Identity Center con MFA y dejar la cuenta raíz solo para emergencias, con llave física", "Alarma uso-root; Prowler (crítica aceptada)", "Media", "Sin costo; la llave física tiene costo"],
        ["R8", "Habilitar copias con AWS Backup y evaluar una segunda región para DynamoDB (tablas globales)", "RSK-01", "Media", "Según el volumen de datos"],
        ["R9", "Agrupar en Dependabot las acciones que deben subir juntas (init y analyze de CodeQL) y revisar sus PR cada semana", "PR #54 y #55 (fallaron separados)", "Baja", "Sin costo"],
        ["R10", "Llevar el SIEM a Wazuh o a una solución con respuesta automática si el volumen de eventos crece, conservando las 14 reglas actuales", "CTRL-20", "Baja", "Según la opción elegida"],
    ],
    tam=9,
    nota_txt=(
        "Elaboración propia. Salvo el del WAF, los costos no se cuantifican: deben calcularse con "
        "la calculadora de precios de cada proveedor antes de decidir."
    ),
)

# ---------------------------------------------------------------- 6.3
titulo("6.3 Roadmap de seguridad continua", 2)
parrafo(
    "El roadmap ordena las recomendaciones en el tiempo y fija las actividades que se repiten. "
    "La seguridad de Q-Wallet no termina con este informe: las dependencias y las imágenes base "
    "cambian cada semana, como mostraron HAL-06 y HAL-15, y cada función nueva de la app abre "
    "amenazas nuevas que hay que modelar antes de construirla. La Tabla 56 muestra el plan por "
    "horizonte y la Tabla 57 las actividades permanentes, que ya están automatizadas en su mayoría."
)
tabla(
    "Roadmap de seguridad por horizonte",
    ["Horizonte", "Fecha límite", "Actividades", "Resultado esperado"],
    [
        ["Inmediato", "31-ene-2027", "R3 (Expo SDK 58), R4 (concurrencia de Lambda y ráfaga) y revisión de las alarmas con el ajuste del rol de plan", "0 excepciones de SCA vigentes; HAL-17 cerrado: una ráfaga autenticada recibe 429 y no 500"],
        ["Antes de producción", "Antes de pasar a producción", "R1 (WAF permanente), R2 (pantallas conectadas a la API y biometría en teléfono físico), R5 (dominio propio) y R6 (Play App Signing); repetir el pentest completo", "RSK-11 en Medio; 13 de 13 casos de abuso con evidencia; ningún riesgo en Alto"],
        ["Primeros 3 meses de operación", "Producción + 3 meses", "R7 (IAM Identity Center), R8 (copias y segunda región) y simulacro de incidente con el SIEM", "Cuenta raíz sin uso diario; recuperación probada"],
        ["Mediano plazo", "Producción + 6 meses", "R10 (SIEM con respuesta automática) y revisión del modelo de amenazas de las funciones nuevas", "Detección y respuesta con menos pasos manuales"],
    ],
    tam=9,
    nota_txt="Elaboración propia. R1 a R10 son las recomendaciones de la Tabla 55.",
)
tabla(
    "Actividades permanentes de seguridad",
    ["Frecuencia", "Actividad", "Cómo se hace hoy"],
    [
        ["Cada pull request", "SAST, SCA, secretos, IaC, imágenes y pruebas por control", "Automático: devsecops.yml e infra.yml; el merge exige que pasen"],
        ["Cada despliegue", "Verificación de TLS, IAM y cifrado; pentest de caja negra y Prowler", "Automático: infra.yml y pentest.yml, con aprobación manual del despliegue"],
        ["Cada cambio de la app", "APK de producción contra MobSF, Frida, MITM y revisión del almacenamiento", "Automático: movil.yml en un emulador Android"],
        ["Semanal", "Revisar los PR de Dependabot y las alertas de GitHub", "Manual, con los resultados de los flujos en cada PR"],
        ["Mensual", "Revisar el tablero del SIEM, las alarmas disparadas y el gasto de AWS", "Manual: tablero qwallet-seguridad y presupuesto de US$5 con alerta"],
        ["Al vencer una excepción", "Corregir o renovar con motivo y fecha nueva, firmada por el dueño del riesgo", "La compuerta de SCA vuelve a fallar sola cuando vence la fecha"],
        ["Cada función nueva", "Actualizar el modelo de amenazas y la matriz de riesgos antes de construirla", "Manual: modelo en OWASP Threat Dragon y registro de riesgos del repositorio"],
    ],
    tam=9,
    nota_txt="Elaboración propia con los flujos de GitHub Actions descritos en las secciones 4.6 y 5.5.",
)

# ---------------------------------------------------------------- 6.4
titulo("6.4 Lecciones aprendidas", 2)
lecciones = [
    ("Probar el control con un ataque real, no solo revisarlo. ",
     "El pinning estaba instalado, configurado y revisado, y aun así no protegía nada (HAL-13); "
     "freeRASP estaba en las dependencias, pero nunca se iniciaba (HAL-11). Los dos fallos solo "
     "aparecieron cuando atacamos el APK de producción en un emulador. Desde entonces, un control "
     "no cuenta como cumplido hasta tener una prueba que lo intente romper."),
    ("Las herramientas también se equivocan. ",
     "Prowler marcó el MFA de Cognito como no obligatorio porque su rol no podía leer esa "
     "configuración (HAL-10), y la regla que Prowler pedía para el rol de logs dejó vacío el log "
     "de acceso de API Gateway (HAL-14). Cruzar dos fuentes antes de aceptar o corregir un "
     "hallazgo evitó una corrección innecesaria y una que nos habría dejado sin datos."),
    ("La seguridad continua vigila lo que no escribimos. ",
     "Dos de los diecisiete hallazgos aparecieron sin ningún cambio en el código: avisos nuevos "
     "publicados para dependencias e imágenes que ya usábamos. Sin compuertas en cada ejecución, "
     "esos avisos habrían llegado a producción en silencio."),
    ("El costo es un requisito de diseño. ",
     "El presupuesto de US$5 al mes descartó RDS, NAT Gateway y Lambdas dentro de una VPC, y nos "
     "llevó a encender el WAF solo para las pruebas. Aceptar ese riesgo de forma explícita, con "
     "dueño, fecha y plan, fue más honesto que esconderlo, y dejó claro qué cambia al pasar a "
     "producción."),
    ("Diseñar seguro desde el inicio abarata las pruebas. ",
     "Como el modelo de amenazas existía antes del código, cada control nació con su caso de "
     "abuso y su prueba. El arnés de caja gris corre los 11 casos de abuso del servidor y las 18 pruebas OWASP API en "
     "cada pull request en segundos, en lugar de repetir un pentest manual."),
    ("Las reglas del proveedor limitan el pentest. ",
     "La política de pruebas de AWS no permite inundar servicios ni forzar el inicio de sesión de "
     "Cognito. Tuvimos que rediseñar tres casos de abuso (Tabla 11) y probar la saturación con "
     "cargas acotadas. La primera prueba, sin token, no mostró ningún 429 (HAL-16); solo al "
     "repetirla con un token real vimos que el authorizer rechaza esas solicitudes antes del "
     "límite y que el límite sí protege a los clientes autenticados, y apareció un hallazgo nuevo "
     "(HAL-17). Probar como el usuario real, y no solo como el atacante anónimo, cambió la conclusión."),
    ("La evidencia se automatiza o se pierde. ",
     "Como la presentación no admite demostraciones en vivo, cada prueba publica su resultado en "
     "un comentario del PR o en un issue del repositorio, con la cuenta y los correos tapados. "
     "Eso nos permitió reconstruir cualquier cifra del informe con su ejecución original."),
]
for negrita, texto in lecciones:
    p = parrafo(texto)
    r = p.runs[0]
    nueva = p.add_run(negrita)
    nueva.bold = True
    nueva.font.size = Pt(12)
    r._r.addprevious(nueva._r)

# ---------------------------------------------------------------- 6.5
titulo("6.5 Anexos", 2)
parrafo(
    "Los anexos reúnen el índice de evidencias (Anexo A), la matriz de trazabilidad de las 41 "
    "amenazas (Anexo B), la ubicación del código y de los flujos que generan cada resultado "
    "(Anexo C) y las capturas de pantalla que no aparecen en el cuerpo (Anexo D). Todo está en el repositorio público github.com/dbarrios95/q-wallet."
)
titulo("Anexo A. Índice de evidencias", 3)
EVID = [
    ["EVD-1-01", "Arquitectura de seguridad con fronteras de confianza y controles", "Figura 1; docs/evidencias"],
    ["EVD-1-03", "Cuenta de AWS: MFA, presupuesto de US$5 con alerta y plan gratuito", "Figura 104; docs/evidencias"],
    ["EVD-1-04", "GitHub: protección de secretos, Dependabot y ruleset de main", "Figura 105; docs/evidencias"],
    ["EVD-1-06 y 1-07", "Push directo a main rechazado; gitleaks sobre el historial", "Figuras 105 y 106"],
    ["EVD-2-01 a 2-03", "Diagramas de flujo de datos de niveles 0, 1 y 2", "Figuras 2 a 4"],
    ["EVD-2-05 y 2-07", "Mapas de calor inherente y residual proyectado", "Figuras 5 y 6"],
    ["EVD-3-01", "Flujo DevSecOps con todas sus etapas", "Comentarios de PR; issue Evidencias DevSecOps"],
    ["EVD-3-02 y 3-03", "SAST: Semgrep (reglas públicas y 7 propias) y CodeQL", "Tablas 30 y 31"],
    ["EVD-3-04 y 3-05", "SCA: npm audit con compuerta, Trivy y SBOM; Trivy sobre las 5 imágenes", "Tablas 32 y 33"],
    ["EVD-3-06", "Checkov sobre Terraform y Dockerfile: 282 pasan, 0 fallan, 39 omitidas", "Tabla 29; PR #22"],
    ["EVD-3-07", "MobSF sobre el APK de producción", "docs/evidencias/bloque5"],
    ["EVD-3-08", "Arquitectura con el flujo de datos numerado", "Figura 7"],
    ["EVD-3-09", "Prowler sobre la cuenta, antes y después", "Tablas 41 y 51"],
    ["EVD-3-10", "La compuerta de SCA detiene un PR vulnerable", "PR #37"],
    ["EVD-3-11 a 3-13", "Verificación del despliegue: IAM por rol y tabla, TLS 1.3, Cognito y CloudTrail", "Issue Evidencias AWS"],
    ["EVD-3-14 y 3-15", "Pruebas por control y prueba de humo de las imágenes", "Comentarios de PR"],
    ["EVD-3-16 y 3-17", "Figura del flujo DevSecOps; app en release con minSdk 29", "Figura 8; docs/evidencias"],
    ["EVD-4-01 y 4-02", "Caja negra: Nmap y TLS; ZAP baseline", "Tabla 38; issue Evidencias Pentest"],
    ["EVD-4-03 a 4-13", "Casos de abuso CA-01 a CA-13 y OWASP API Top 10", "Tablas 39, 40 y 45; Figura 107"],
    ["EVD-4-14", "Perímetro del software", "Figura 9"],
    ["EVD-5-01 y 5-02", "Reglas del WAF y ataques bloqueados, con la regla que decidió", "Tablas 42 y 43"],
    ["EVD-5-03", "freeRASP: detección del emulador y pantalla de bloqueo", "Figura 10"],
    ["EVD-5-04", "Llave KMS propia y cifrado de las 8 tablas", "Issue Evidencias AWS"],
    ["EVD-5-05 a 5-07", "SIEM en CloudWatch, reglas, alarmas, correos y tablero", "Tablas 46 a 49; Figuras 12 y 108"],
    ["EVD-5-08", "Arquitectura del SIEM y re-test de cada hallazgo", "Figura 11; Tabla 50"],
    ["EVD-5-09", "Mapa de calor antes y después verificado", "Figura 13"],
    ["EVD-5-11", "Ofuscación y firma del APK (Hermes y R8)", "docs/evidencias/bloque5"],
    ["EVD-6-01 a 6-05", "Pantallas principales de la app en el emulador", "Figura 101"],
    ["EVD-6-06 y 6-07", "FLAG_SECURE: captura desde Android en negro y flag SECURE en dumpsys", "Figura 103"],
    ["EVD-7-01 a 7-04", "Inicio de sesión real con Cognito (PKCE y MFA) y CA-07 con un token real: almacenamiento, desbloqueo y cierre de sesión", "Figura 102; Tabla 45; docs/evidencias/bloque7"],
    ["EVD-7-05", "Prueba de saturación con y sin token (HAL-16 y HAL-17)", "Tabla 50; docs/evidencias/bloque7"],
]
tabla(
    "Índice de evidencias del proyecto",
    ["Evidencia", "Qué muestra", "Dónde está"],
    EVID,
    tam=9,
    nota_txt=(
        "Elaboración propia. Las rutas son relativas al repositorio. Los issues «Evidencias AWS», "
        "«Evidencias DevSecOps», «Evidencias Pentest», «Evidencias WAF y SIEM» y «Evidencias "
        "Móvil» y la rama evidencias-ci guardan la salida de cada ejecución, con el número de "
        "cuenta, los ARN y los correos tapados."
    ),
)

seccion(True)
titulo("Anexo B. Matriz de trazabilidad de las amenazas", 3)
EST = {"prueba": "Prueba", "configuracion": "Configuración", "parcial": "Parcial",
       "aceptado": "Aceptado", "eliminado": "Eliminado"}
filas_b = []
for f in FILAS:
    filas_b.append([
        f["ame"], f["titulo"], f["capa"], ", ".join(c[5:] for c in f["ctrls"]) or "—", EST[f["estado"]],
        ", ".join(e[4:] for e in f["evid"]) or "—",
        pxi(f["P"], f["I"]), pxi(f["Pv"], f["Iv"]), _res.nivel(f["Pv"] * f["Iv"]),
    ])
tabla(
    "Trazabilidad de las 41 amenazas hasta su evidencia y su riesgo residual",
    ["AME", "Amenaza", "Capa", "CTRL", "Verificación", "Evidencia (EVD)", "Inherente", "Residual", "Nivel"],
    filas_b,
    tam=8,
    total=9.0,
    nota_txt=(
        "Elaboración propia con el modelo de amenazas y el registro de verificación de cada "
        "amenaza (carpeta docs/threat-model del repositorio). El riesgo "
        "RSK-nn corresponde a la amenaza AME-nn. Capa: capa de defensa de la sección 2.5.4. CTRL: "
        "número del control de la sección 4.2. Verificación: Prueba = ataque ejecutado y "
        "bloqueado; Configuración = configuración desplegada leída; Parcial = parte del control "
        "falta o no se pudo probar. Inherente y residual en P×I."
    ),
)
seccion(False)

titulo("Anexo C. Repositorio, código y flujos", 3)
tabla(
    "Ubicación del código y de los flujos que generan los resultados",
    ["Ruta en el repositorio", "Contenido"],
    [
        ["mobile/", "App Android (Expo SDK 57, TypeScript): inicio de sesión con Cognito, sesión en Keystore, freeRASP, pinning y pantallas"],
        ["services/", "Los 5 microservicios (svc-profile, svc-accounts, svc-transfers, svc-budgets y svc-admin) y el arnés de pentest de caja gris"],
        ["infra/", "Terraform de toda la arquitectura, bootstrap de OIDC y scripts de verificación"],
        [".github/workflows/devsecops.yml", "SAST, SCA, secretos, pruebas por control y pentest de caja gris en cada PR"],
        [".github/workflows/infra.yml", "Revisión de Terraform, plan, despliegue con aprobación y verificación en AWS"],
        [".github/workflows/pentest.yml", "Caja negra (Nmap, TLS y ZAP) y Prowler después de cada despliegue"],
        [".github/workflows/movil.yml", "APK de producción, MobSF y pruebas en emulador (freeRASP, Frida, MITM, almacenamiento e inicio de sesión real)"],
        [".github/workflows/saturacion.yml", "Prueba de saturación de la API con y sin token (HAL-16 y HAL-17)"],
        [".github/workflows/waf-siem.yml", "Prueba del WAF y del SIEM; apaga el WAF al terminar"],
        ["docs/REGISTRO_RIESGOS.md", "Activos, amenazas, casos de abuso y hallazgos"],
        ["docs/threat-model/", "Modelo de amenazas (OWASP Threat Dragon) y verificación de cada amenaza"],
        ["scripts/", "Generadores de figuras y de este informe"],
    ],
    tam=9,
    nota_txt="Elaboración propia. Repositorio: https://github.com/dbarrios95/q-wallet",
)

doc.save(str(SALIDA))
print("Generado:", SALIDA)
