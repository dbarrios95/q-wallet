# REGISTRO DE ACTIVOS, AMENAZAS, RIESGOS Y HALLAZGOS

Las escalas están en `CONTEXTO.md` sección 6. No se cambian.

---

## A. Inventario de activos (ISO 27001) — sección 2.1 / 2.2

| ID | Nombre | Proceso | Descripción | Tipo | Ubicación | C | I | D | Valor | Criticidad | Justificación | Propietario | Custodio | Usuarios |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Semilla (completar y ampliar hasta ≥25)

| ID | Nombre | Tipo | Ubicación |
|---|---|---|---|
| ACT-01 | Datos personales de clientes (nombre, DPI, teléfono, correo) | Información | Cloud |
| ACT-02 | Saldos y movimientos | Información | Cloud |
| ACT-03 | Credenciales y tokens (Cognito, JWT, refresh) | Información | Cloud / Dispositivo |
| ACT-04 | PIN de transacción (hash) | Información | Cloud |
| ACT-05 | Registros de auditoría | Información | Cloud |
| ACT-06 | Llaves KMS | Información | Cloud |
| ACT-07 | Secretos de configuración (SSM) | Información | Cloud |
| ACT-08 | Código fuente | Información | Repositorio |
| ACT-09 | Estado de Terraform | Información | Repositorio / Cloud |
| ACT-10 | App Android Q-Wallet | Software | Dispositivo |
| ACT-11 | Microservicios Lambda (5) | Software | Cloud |
| ACT-12 | API Gateway | Software | Cloud |
| ACT-13 | Cognito User Pool | Software | Cloud |
| ACT-14 | DynamoDB | Software | Cloud |
| ACT-15 | Imágenes de contenedor (ECR) | Software | Cloud |
| ACT-16 | Pipeline CI/CD | Software | Repositorio |
| ACT-17 | Dependencias npm | Software | Repositorio |
| ACT-18 | Dispositivo móvil del cliente | Físico | Dispositivo |
| ACT-19 | Estaciones de trabajo del equipo | Físico | Local |
| ACT-20 | Infraestructura física AWS us-east-1 | Físico | Cloud |
| ACT-21 | Equipo de desarrollo / DevSecOps | Personal | Local |
| ACT-22 | Personal de soporte (admins) | Personal | Local |
| ACT-23 | AWS (proveedor cloud) | Servicios | Cloud |
| ACT-24 | GitHub | Servicios | Repositorio |
| ACT-25 | Servicio de correo de Cognito | Servicios | Cloud |
| ACT-26 | Reputación de la marca | Empresa | — |
| ACT-27 | Cumplimiento regulatorio (JM-104-2021) | Empresa | — |

---

## B. Amenazas STRIDE + DREAD — sección 2.3 / 2.4

| AME | Elemento DFD | Frontera | STRIDE | Descripción | ACT | CTRL | D | R | E | A | Di | DREAD (inherente) | Prioridad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

---

## C. Matriz de riesgos — sección 2.5 (inherente) y 5.6 (residual)

| RSK | AME | P | I | P×I | Nivel | Capa | Tipo | Impacto negocio | Tratamiento | CTRL | P' | I' | Residual |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Resumen por capa (obligatorio: al menos 1 riesgo en cada capa)

| Capa | # riesgos | Críticos | Altos | Medios | Bajos |
|---|---|---|---|---|---|
| 1 Datos | | | | | |
| 2a Código | | | | | |
| 2b Aplicación | | | | | |
| 2c Implementación | | | | | |
| 2d Perímetro app | | | | | |
| 3 Host | | | | | |
| 4 Red interna | | | | | |
| 5 Perímetro cloud | | | | | |
| 6 Física | | | | | |
| 7 Políticas | | | | | |

---

## D. Hallazgos de pruebas — secciones 3 y 4

### D.1 Verificación de controles (casos de abuso)
| Caso | Abuso intentado | CTRL | Herramienta | Resultado esperado | Resultado obtenido | EVD |
|---|---|---|---|---|---|---|
| CA-01 | Leer movimientos de una cuenta ajena | CTRL-01 | Burp | 403/404 | | |
| CA-02 | Fuerza bruta del PIN | CTRL-02 | Burp Intruder | Bloqueo tras 5 intentos | | |
| CA-03 | Enumerar usuarios por teléfono | CTRL-03/05 | Postman | Datos enmascarados + 429 | | |
| CA-04 | `PATCH /me` con `role=admin` | CTRL-04 | Burp | 400 | | |
| CA-05 | `?limit=100000` | CTRL-05 | Postman | 400 o tope de 50 | | |
| CA-06 | 20 transferencias concurrentes con la misma clave | CTRL-06 | Script / Burp Turbo Intruder | Una sola aplicada | | |
| CA-07 | Extraer tokens del dispositivo | CTRL-07 | objection | No legibles | | |
| CA-08 | MITM con certificado de Burp | CTRL-08 | Burp + emulador | Conexión rechazada | | |
| CA-09 | Acceder a `/admin/*` como cliente | CTRL-14 | Burp | 403 | | |
| CA-10 | Hooking / root | CTRL-15 | Frida | freeRASP detecta y reacciona | | |
| CA-11 | Buscar secretos en el APK | CTRL-16 | MobSF / apktool | Ninguno | | |
| CA-12 | SQLi/XSS/payloads OWASP | CTRL-17 | ZAP | WAF 403 | | |
| CA-13 | Login sin MFA / token alterado | CTRL-18 | Burp | 401 | | |

### D.2 Hallazgos reales
| HAL | Prueba (negra/gris/blanca/SAST/SCA/IaC) | Herramienta | Endpoint/archivo | Severidad | EVD hallazgo | Corrección (commit) | EVD re-test | Estado |
|---|---|---|---|---|---|---|---|---|
