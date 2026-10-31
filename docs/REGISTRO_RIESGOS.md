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
| ACT-09 | Estado de Terraform | Información | Cloud: S3 con bloqueo nativo (`use_lockfile`), SSE-KMS, versionado y Block Public Access |
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
| ACT-27 | Alineación regulatoria (referencia JM-98-2025) | Empresa | — |
| ACT-28 | SIEM Wazuh (Docker local) | Software | Local |

> Inventario completo con CIA, criticidad y responsables: Tabla 12 de `docs/entregas/Entrega1_Informe_QWallet.docx`. ACT-28 se agregó el 12-oct (lo usan AME-31 y AME-41); ACT-27 se renombró para no afirmar cumplimiento y el 14-oct pasó a JM-98-2025 (derogó la JM-104-2021).

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
| HAL-01 | SCA | npm audit (compuerta propia) | `mobile/package.json` zod 4.6.5; misma versión fijada para `/services` en CONTEXTO 3.1 (GHSA-mrhx-c7xc-m3w5, agotamiento de memoria) | Alta | EVD-3-04 | zod 4.6.7 en app y servicios (PR #36, 30-oct-2026) | EVD-3-04 (services 0 avisos) y EVD-3-10 (la compuerta bloquea zod 4.6.5, PR #37) | Cerrado |
| HAL-02 | SCA | npm audit | `decode-uri-component` 0.2.2 vía expo-router 57 → query-string (GHSA-qr28-fpjm-wq7f) | Alta | EVD-3-04 | Excepción en `mobile/excepciones-sca.json` hasta 28-nov-2026: la corrección exige Expo SDK 58 | — | Aceptado (temporal, aprobado por Daniel el 30-oct) |
| HAL-03 | SCA | npm audit | `node-forge` 1.4.0 y `zod` 3.25.76 dentro de `@expo/cli` (herramienta de compilación; GHSA-86w9-cpqp-85rv, GHSA-mrhx-c7xc-m3w5) | Alta | EVD-3-04 | node-forge: corregido en HAL-06 (1.4.2 por overrides). zod de `@expo/cli`: excepción hasta 28-nov-2026 (no va dentro del APK) | EVD-3-04 (PR #47) | node-forge cerrado; zod aceptado (temporal) |
| HAL-04 | Caja blanca (revisión manual) | — | `mobile/app/(auth)/welcome.tsx`: «cifrado de extremo a extremo» y «cumplimiento JM-104-2021» | Baja | — | Texto: «Conexión cifrada TLS 1.3 · Diseñada con referencia a la JM-98-2025» (PR #36) | Revisión del código | Cerrado |
| HAL-05 | Contenedores | Trivy 0.75.0 | Imagen base `public.ecr.aws/lambda/nodejs:24`: 24 HIGH con corrección en npm, aws-lambda-rie y `/var/runtime/node_modules/@aws-sdk` (axios, undici, brace-expansion, follow-redirects) | Alta | EVD-3-05 (antes) | Digest vigente + se quitan esos componentes de la imagen final (PR #36) | EVD-3-05 (0 HIGH) y EVD-3-15 (prueba de humo) | Cerrado |
| HAL-06 | SCA | npm audit (compuerta) | `node-forge` <=1.4.0 en `/mobile`: avisos nuevos publicados el 31-oct-2026 (GHSA-5x38-2vff-x55p y otros 4 High); main empezó a fallar sin cambios de código | Alta | Issue «Evidencias DevSecOps» (31-oct) | `overrides` de npm a node-forge 1.4.2; se quita la excepción GHSA-86w9 (PR #47) | Compuerta PASA en PR #47 | Cerrado |
| HAL-07 | Revisión de configuración (bloque 5) | — | AWS WAF sin firmas de inyección SQL: el Core Rule Set no las trae | Media | `infra/waf.tf` | `AWSManagedRulesSQLiRuleSet` con prioridad 15 (PR #47) | EVD-5-02 (casos C01 y C02) | Cerrado al verificar |
| HAL-08 | Cloud | Prowler 5.44.0 | Cuenta sin S3 Block Public Access ni política de contraseñas de IAM; Cognito con contraseña de 12 | Alta (S3) / Media | EVD-3-09 | Bootstrap paso 7 y Cognito a 14 caracteres (PR #47) | Prowler después del bloque 5 | Cerrado al verificar |
| HAL-09 | Caja negra | ZAP baseline | Sin cabecera HSTS en la raíz del host execute-api (fuera de la etapa v1) | Baja | EVD-4-02 | Aceptado: esa respuesta la genera AWS antes de la etapa; la etapa v1 sí envía HSTS. Se corrige con dominio propio (roadmap) | — | Aceptado |
| HAL-10 | Cloud | Prowler 5.44.0 | `cognito_user_pool_mfa_enabled` marca el MFA como no obligatorio | Media | EVD-3-09 | Falso positivo: `MfaConfiguration = ON` y TOTP activo leídos con GetUserPoolMfaConfig | EVD-3-13, EVD-5-05 | Descartado |
| HAL-11 | Caja blanca (bloque 5) | Revisión + compilación | freeRASP instalado pero nunca iniciado; al iniciarlo el empaquetado fallaba por la dependencia `buffer` | Alta | Compilación del flujo movil.yml | Inicio de freeRASP con política de reacción + `buffer` 6.0.3 (PR #47) | EVD-5-03, EVD-4-10 | Cerrado |
| HAL-12 | Estático del APK | aapt2 / MobSF | Permisos que la app no usa: almacenamiento externo, ventana superpuesta, imágenes, arranque del sistema | Media | EVD-4-11 (antes) | `android.blockedPermissions` en app.json (PR #47) | EVD-4-11 (después) | Cerrado |
| HAL-13 | Caja gris en emulador | mitmproxy con CA en el sistema | El pinning no protegía la conexión: el proxy leyó la solicitud de la app a la API | Alta | EVD-4-08 (antes) | En corrección (PR #47) | EVD-4-08 (después) | Abierto |
