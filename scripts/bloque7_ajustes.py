"""Bloque 7: ajustes del informe final pedidos por Daniel (10-nov-2026) y resultados del bloque 7.

Uso (desde la raíz del repo), después de final_ensamblar.py y antes del formato y el índice:
    python scripts/final_ensamblar.py
    python scripts/bloque7_ajustes.py
    python scripts/entrega1_estilos.py docs/entregas/Informe_Final_QWallet.docx
    python scripts/entrega1_indice.py docs/entregas/Informe_Final_QWallet.docx

Qué cambia:
  A. Redacción: Q-Wallet, S.A. se presenta como empresa y producto (sin «simulado» ni «ficticio»),
     «antes de manejar dinero real» pasa a «antes de pasar a producción» y nada queda «pendiente»
     (siguiente versión, riesgo aceptado o roadmap). Límite acordado: lo que no se hizo no se
     reporta como hecho.
  B. Resultados del bloque 7: inicio de sesión real con Cognito y CA-07 con un token real
     (EVD-7-01 a 7-04) y la prueba de saturación de HAL-16 (EVD-7-05).
Cada reemplazo exige el número exacto de coincidencias (reemplazar() de final_ensamblar.py):
si el Word no es el esperado, el script se detiene sin guardar.
"""
import sys
from pathlib import Path

from docx import Document

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
from final_ensamblar import estado_fila, reemplazar  # noqa: E402

ARCHIVO = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "docs/entregas/Informe_Final_QWallet.docx"

# ---------------------------------------------------------------- A. redacción
REDACCION = [
    # 1.1 a 1.3 (Entrega 1)
    ("En este contexto planteamos Q-Wallet, una billetera digital de la empresa ficticia Q-Wallet, S.A.,",
     "En este contexto planteamos Q-Wallet, la billetera digital de la empresa Q-Wallet, S.A.,", 1),
    ("La aplicación funciona en Android, opera con dinero simulado en quetzales (GTQ) y almacena",
     "La aplicación funciona en Android, opera en quetzales (GTQ) y almacena", 1),
    ("El proyecto es académico; se usa dinero simulado y no se procesan datos de tarjetas.",
     "La versión 1 no procesa datos de tarjetas ni se conecta con bancos: los saldos se mueven solo entre cuentas de Q-Wallet.", 1),
    ("Datos simulados", "Datos de prueba", 1),
    ("No se tratan datos personales reales; los números de DPI y de teléfono son ficticios.",
     "Las pruebas usan cuentas de prueba creadas para ese fin; no se usan datos personales de clientes.", 1),
    ("La política de AWS prohíbe la denegación de servicio y la inundación de solicitudes, incluso simulada (AWS, s. f.-b).",
     "La política de AWS prohíbe la denegación de servicio y la inundación de solicitudes, aunque sea como prueba (AWS, s. f.-b).", 1),
    ("Q-Wallet, S.A. es una empresa ficticia que no está supervisada, por lo que usamos",
     "Q-Wallet, S.A. no está bajo la supervisión de la SIB, por lo que usamos", 1),
    ("requeriría autorización de la SIB para operar con dinero real queda fuera del alcance de este proyecto, que usa dinero simulado.",
     "requeriría autorización de la SIB para operar queda fuera del alcance de este proyecto.", 1),
    ("y la inundación de solicitudes, incluso simulada, tanto en el inicio de sesión como en la API,",
     "y la inundación de solicitudes, aunque sea como prueba, tanto en el inicio de sesión como en la API,", 1),
    ("Asignamos estos roles según la organización ficticia del proyecto: Gerente de Producto para los activos de negocio (un rol de la organización ficticia que no ejerce",
     "Asignamos estos roles según la organización de Q-Wallet, S.A.: Gerente de Producto para los activos de negocio (un rol que no ejerce", 1),
    # 3.1 (pentest)
    ("y está prohibida cualquier inundación de solicitudes (incluso simulada).",
     "y está prohibida cualquier inundación de solicitudes, aunque sea como prueba.", 1),
    # 3.5 (SCA)
    ("solo corren si existen sus llaves de acceso (NVD_API_KEY y SNYK_TOKEN), que todavía no creamos. La cobertura actual no depende de ellos:",
     "solo corren si existen sus llaves de acceso (NVD_API_KEY y SNYK_TOKEN); no las creamos porque la cobertura no depende de ellos:", 1),
    # 4.3 (DevSecOps)
    ("La app Android todavía muestra datos simulados: en esta fase reforzamos su configuración de compilación y dejamos claro qué controles del cliente faltan. La Tabla 37 separa lo que ya está en el código, lo que configuramos ahora y lo pendiente.",
     "En esta fase reforzamos la configuración de compilación de la app Android. La Tabla 37 muestra cómo quedó cada control del cliente al cierre del proyecto.", 1),
    ("Tope por transferencia: Q5,000.00 de dinero simulado.", "Tope por transferencia: Q5,000.00.", 1),
    # 5.6
    ("aunque la decisión de no procesar tarjetas ni dinero real (sección 1.3)",
     "aunque la decisión de no procesar tarjetas ni conectarse con bancos (sección 1.3)", 1),
    # 6.2
    ("Las ordenamos por prioridad: Alta es antes de manejar dinero real;",
     "Las ordenamos por prioridad: Alta es antes de pasar a producción;", 1),
    ("Antes de manejar dinero real", "Antes de pasar a producción", 1),
]

# ---------------------------------------------------------------- B. resultados del bloque 7
# (se completan con las cifras de EVD-7-01 y EVD-7-05)
RESULTADOS = []
ESTADOS_43 = []


def main():
    doc = Document(str(ARCHIVO))
    for viejo, nuevo, n in REDACCION + RESULTADOS:
        reemplazar(doc, viejo, nuevo, n)
    for primera, nuevo in ESTADOS_43:
        estado_fila(doc, primera, nuevo)
    doc.save(str(ARCHIVO))
    print(f"ok {ARCHIVO}: {len(REDACCION)} ajustes de redacción, {len(RESULTADOS)} de resultados, "
          f"{len(ESTADOS_43)} filas de la Tabla 37")


if __name__ == "__main__":
    main()
