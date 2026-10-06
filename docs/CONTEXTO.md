# CONTEXTO MAESTRO — Proyecto Final SECAPP 2026 (UMG)

> Fuente única de verdad. Toda IA (Claude, Gemini) y todo integrante parte de aquí.
> Si una decisión cambia, se actualiza **primero este archivo** y luego el resto.
> Estado de avance: §11. Historial detallado: `BITACORA.md`.

---

## 1. Datos del curso

| Campo | Valor |
|---|---|
| Universidad | Universidad Mariano Gálvez de Guatemala — Facultad de Ingeniería en Sistemas, Programa de Postgrados |
| Programa | Maestría en Seguridad Informática |
| Curso | Seguridad en Aplicaciones |
| Catedrático | Msc. Ing. César Rodríguez Minas |
| Grupo | 3 integrantes — nombres: **PENDIENTE** |
| Opción | **A — Aplicación Móvil Banking / Fintech Cloud (Android)** |
| Ponderación oficial | Enunciado: 5 componentes × 4 pts = 20 pts |
| Entrega 1 | **Sábado 17-oct-2026** — Fase "Selección y Planificación" + Fase "Activos y Riesgos" |
| Entrega final | **PENDIENTE** |
| Presentación | Sí, **sin demo en vivo** → toda prueba debe quedar en captura o video |
| Informe | Microsoft Word, formato UMG + APA 7 |

### Ponderación (4 pts c/u)
1. Análisis de Riesgos y Activos — inventario ISO 27001, STRIDE/DREAD, 7 capas, matriz de calor y tratamiento.
2. Arquitectura Cloud & DevSecOps — diagrama (API Gateway, IAM, Cloud), evidencia SAST/SCA, análisis IaC.
3. Implementación de Ciberdefensa — pentest caja negra (ZAP/Burp), caja gris/blanca, casos de abuso y perímetro.
4. Implementación de Ciberseguridad — plan de mitigación por hallazgo, WAF/RASP/cifrado/SIEM.
5. Informe Técnico & APA — formato UMG estricto, dictamen y conclusiones fundamentadas.

---

## 2. La aplicación: **Q-Wallet**

Billetera digital fintech guatemalteca (empresa ficticia **Q-Wallet, S.A.**) con control de gastos integrado.
Dinero **simulado**, moneda **GTQ**, montos almacenados como **enteros en centavos**.

### Roles
- **Cliente**: usa la app móvil.
- **Soporte/Admin**: opera mediante endpoints `/admin/*` (grupo `admins` en Cognito). Sin app web.

### Funciones del MVP
| ID | Función |
|---|---|
| F1 | Registro e inicio de sesión: OAuth2 Authorization Code + PKCE (Cognito managed login), MFA TOTP |
| F2 | Desbloqueo biométrico local (huella/rostro) para reabrir sesión |
| F3 | Consulta de saldo y movimientos (paginado) |
| F4 | Transferencia P2P a otro usuario por número de teléfono, autorizada con PIN de transacción |
| F5 | Beneficiarios frecuentes |
| F6 | Control de gastos: categorías, presupuestos mensuales y alertas al superarlos |
| F7 | Administración: listar/bloquear usuarios, consultar auditoría |

**Fuera de alcance:** iOS, web, tarjetas reales, integración con bancos reales, KYC real.

---

## 3. Stack tecnológico (decidido)

| Capa | Tecnología | Motivo |
|---|---|---|
| App móvil | React Native + **Expo (dev build)** + TypeScript, solo Android | Un solo lenguaje en todo el stack; cobertura completa de SAST (Semgrep, CodeQL, SonarQube) |
| UI | NativeWind (Tailwind) + componentes propios | Diseño moderno sin costo |
| Almacenamiento seguro | `expo-secure-store` (Android Keystore) | MASVS-STORAGE |
| Biometría | `expo-local-authentication` | F2 |
| OAuth2 + PKCE | `expo-auth-session` | F1 |
| TLS Pinning | `react-native-ssl-public-key-pinning` | MASVS-NETWORK |
| RASP móvil | freeRASP (Talsec) — plan gratuito | Root/hook/emulador/tampering |
| Ofuscación | Hermes bytecode + R8/ProGuard | MASVS-RESILIENCE |
| Backend | 5 microservicios **AWS Lambda Node.js 24 (`nodejs24.x`) + TypeScript**, empaquetados como **imágenes de contenedor (ECR)** | Genera Dockerfiles reales para Trivy/Checkov |
| API | **Amazon API Gateway REST** (no HTTP API: AWS WAF solo se asocia a REST) | Authorizer Cognito, throttling, validación |
| Identidad | **Amazon Cognito** User Pool | OAuth2/OIDC, PKCE, MFA |
| Base de datos | **Amazon DynamoDB** cifrado con **KMS CMK** propia | Siempre gratis hasta 25 GB |
| Secretos | SSM Parameter Store SecureString | Sin costo en tier estándar |
| WAF | **AWS WAF** (Core Rule Set, Known Bad Inputs, rate-based) | Se activa solo en días de prueba |
| Logs/Auditoría | CloudWatch Logs + CloudTrail → S3 | Fuente del SIEM |
| SIEM | **Wazuh** en Docker local (lee CloudTrail/CloudWatch) | Gratis |
| IaC | Terraform | Checkov/tfsec/Trivy |
| CI/CD | GitHub Actions, despliegue a AWS vía **OIDC** (sin llaves estáticas) | |
| Repositorio | `github.com/dbarrios95/q-wallet`, **público** desde 05-oct-2026. Ruleset `main-protegida`: sin commits directos a `main` (rama → PR → merge) | Rulesets, secret scanning, push protection y CodeQL gratis solo en repos públicos |
| Región AWS | `us-east-1` | Menor costo, disponibilidad completa de servicios |
| Dominio | Ninguno: endpoint `execute-api` de AWS | Costo $0 |
| Sistema operativo del equipo | Windows (PowerShell); repo en `C:\dev\q-wallet` | Evita el límite de longitud de rutas en builds Android |

### 3.1 Versiones exactas (verificadas el 03-oct-2026)

**Política de versiones**
- npm siempre con `--save-exact` y `package-lock.json` versionado.
- En la app, los paquetes `expo-*` se instalan con `npx expo install` para que queden alineados al SDK 57.
- Las GitHub Actions se fijan por **SHA del commit** (el tag de la tabla se anota como comentario).
- Si una versión cambia, se actualiza esta tabla y se anota en `BITACORA.md`.

#### Entorno local
| Herramienta | Versión |
|---|---|
| Node.js (local y CI) | 24.21.0 (LTS) |
| JDK | Temurin JDK 17.0.20.1 |
| Terraform CLI | 1.16.5 |
| Android SDK | `%LOCALAPPDATA%\Android\Sdk` (Platform 36, Build-Tools 36.0.0, NDK 27.1.12297006) |
| AVD | `Pixel_8_API_36`: Google APIs, x86_64, **sin Google Play** (permite `adb root` para pentest) |
| ADB | 1.0.41 |
| Docker Desktop / Engine | Estable vigente al instalar → anotar en BITACORA |
| AWS CLI | v2, estable vigente al instalar → anotar en BITACORA |
| Antigravity CLI (agy) | 1.2.16 |
| create-expo-app | 5.0.0 (plantilla `blank-typescript@sdk-57`) |

#### Build resuelto por Expo (Android)
| Parámetro | Versión / Valor |
|---|---|
| compileSdk | 36 |
| targetSdk | 36 |
| minSdk | 24 |
| Kotlin | 2.1.20 |
| Gradle | 9.3.1 |
| Metro | 0.84.5 |

#### App móvil (`/mobile`)
| Paquete | Versión |
|---|---|
| expo (SDK 57) | ~57.0.26 |
| babel-preset-expo | ~57.0.13 (instalado con `npx expo install babel-preset-expo -- --legacy-peer-deps`) |
| react-native | 0.86.3 (la fijada por SDK 57; no usar 0.87) |
| react | 19.2.3 |
| typescript | ~6.0.3 |
| @types/react | ~19.2.18 |
| expo-router | ~57.0.24 |
| expo-dev-client | ~57.0.19 |
| expo-auth-session | ~57.0.13 |
| expo-web-browser | ~57.0.3 |
| expo-crypto | ~57.0.3 |
| expo-secure-store | ~57.0.4 |
| expo-local-authentication | ~57.0.3 |
| expo-build-properties | ~57.0.22 |
| expo-image | ~57.0.5 |
| expo-linear-gradient | ~57.0.2 |
| expo-blur | ~57.0.3 |
| expo-haptics | ~57.0.3 |
| expo-font | ~57.0.4 |
| react-native-reanimated | 4.5.1 |
| react-native-worklets | 0.10.1 (requerido por Reanimated 4) |
| expo-linking | ~57.0.11 |
| expo-constants | ~57.0.20 |
| expo-status-bar | ~57.0.1 |
| react-native-safe-area-context | ~5.7.0 |
| react-native-screens | ~4.26.0 |
| react-native-svg | 15.15.4 |
| nativewind | 4.2.7 |
| tailwindcss | 3.4.19 (NativeWind 4 no soporta Tailwind 4) |
| react-native-ssl-public-key-pinning | 1.2.6 |
| freerasp-react-native | 5.2.2 |
| expo-screen-capture | ~57.0.3 |
| expo-splash-screen | ~57.0.9 |
| @expo-google-fonts/inter | 0.4.2 |
| lucide-react-native | 1.51.0 |
| zod | 4.6.5 |
| eslint | 10.12.0 |

#### Configuración de `app.json` (plugins y seguridad nativa)
- **Lista de plugins vigente:** `expo-router`, `expo-build-properties`, `expo-secure-store`, `expo-local-authentication`, `expo-font`, `expo-splash-screen`, `["freerasp-react-native", { "android": {} }]`.
- `expo-screen-capture` **no** es un config plugin: FLAG_SECURE se aplica en runtime en `transfer`, `unlock` y `profile`.
- `expo-build-properties` está registrado **sin opciones**. Es un pendiente de endurecimiento.

#### Backend (`/services`)
| Paquete / componente | Versión |
|---|---|
| Runtime Lambda | `nodejs24.x` — imagen base `public.ecr.aws/lambda/nodejs:24` fijada por digest |
| typescript | 6.0.3 |
| @types/node | 24.19.1 |
| @types/aws-lambda | 8.10.164 |
| @aws-sdk/client-dynamodb | 3.1146.0 |
| @aws-sdk/lib-dynamodb | 3.1146.0 |
| @aws-sdk/client-ssm | 3.1146.0 |
| @aws-sdk/client-cognito-identity-provider | 3.1146.0 |
| aws-jwt-verify | 5.2.1 |
| zod | 4.6.5 |
| uuid | 14.0.2 |
| esbuild | 0.28.2 |
| vitest | 5.0.3 |
| eslint | 10.12.0 |

#### Infraestructura (`/infra`)
| Componente | Versión |
|---|---|
| Terraform | 1.16.5 (`required_version = "= 1.16.5"`) |
| hashicorp/aws provider | 6.67.0 (`version = "= 6.67.0"`) |

#### Seguridad y DevSecOps
| Herramienta | Versión | Uso |
|---|---|---|
| Semgrep CE | 1.179.0 | SAST |
| CodeQL Action | v4 | SAST (GitHub) |
| SonarQube Cloud | SaaS (sin versión) | SAST / calidad |
| OWASP Dependency-Check | 12.1.0 | SCA |
| Snyk CLI | 1.1307.4 | SCA |
| Trivy | 0.75.0 | Contenedores / IaC / SCA |
| Checkov | 3.3.22 | IaC / Dockerfile |
| MobSF | 4.5.3 | Análisis del APK |
| OWASP ZAP | 2.17.0 | DAST / caja negra |
| Burp Suite Community | Estable vigente al instalar → anotar en BITACORA | Pentest |
| Frida / frida-tools | 17.22.0 / 14.11.0 | Instrumentación |
| objection | 1.12.5 | Pentest móvil |
| OWASP Threat Dragon | 2.6.2 | Threat modeling |
| Wazuh | 4.14.8 (Docker single-node) | SIEM |
| gitleaks | 8.30.1 | Detección de secretos |
| Prowler | 5.44.0 | Auditoría de la cuenta AWS (CIS) |

#### GitHub Actions
| Action | Versión |
|---|---|
| actions/checkout | v7.0.1 |
| actions/setup-node | v7.0.0 |
| aws-actions/configure-aws-credentials | v6.3.0 |
| hashicorp/setup-terraform | v4.0.1 |
| aquasecurity/trivy-action | v0.36.0 |
| bridgecrewio/checkov-action | v12.3128.0 |
| zaproxy/action-api-scan | v0.10.0 |
| github/codeql-action | v4 |
| gitleaks/gitleaks-action | v3.0.0 |

### Costos
- Cuenta AWS en **Free Plan** (créditos de US$100–200, 6 meses, sin cobro al agotarse).
- Presupuesto con alerta a US$5. Prohibido: RDS, NAT Gateway, EC2 24/7, EKS, Shield Advanced.
- **Verificar el día 1** que el Free Plan permita AWS WAF y ECR.

---

## 4. Arquitectura (alto nivel)

```
[App Android] --TLS 1.3--> [AWS WAF] --> [API Gateway REST + Cognito Authorizer]
      |                                         |
      +--OAuth2 PKCE--> [Cognito Managed Login]  +--> svc-profile    --+
                                                 +--> svc-accounts   --+--> [DynamoDB (KMS CMK)]
                                                 +--> svc-transfers  --+--> [SSM Parameter Store]
                                                 +--> svc-budgets    --+
                                                 +--> svc-admin      --+
CloudWatch Logs / CloudTrail --> S3 --> [Wazuh local (SIEM)]
GitHub Actions --OIDC--> AWS (ECR, Lambda, Terraform)
```

### Endpoints (superficie de API)
| Servicio | Endpoints |
|---|---|
| svc-profile | `GET /me`, `PATCH /me`, `GET /users/search?phone=`, `POST /pin` |
| svc-accounts | `GET /accounts`, `GET /accounts/{accountId}/transactions?limit=&cursor=` |
| svc-transfers | `POST /transfers`, `GET /transfers/{id}`, `GET/POST/DELETE /beneficiaries` |
| svc-budgets | `GET /categories`, `GET/POST/PUT /budgets` |
| svc-admin | `GET /admin/users`, `POST /admin/users/{id}/block`, `GET /admin/audit` |

### Fronteras de confianza (para el DFD)
| ID | Frontera |
|---|---|
| TB1 | Dispositivo del cliente ↔ Internet |
| TB2 | Internet ↔ Borde AWS (WAF / API Gateway / Cognito) |
| TB3 | API Gateway ↔ Lambdas |
| TB4 | Lambdas ↔ Datos (DynamoDB, KMS, SSM) |
| TB5 | GitHub (CI/CD) ↔ AWS |
| TB6 | AWS ↔ SIEM local |

---

## 5. Estrategia: seguro desde el diseño (indicación del catedrático)

- La app se construye **con todos los controles desde el inicio**. No hay versión vulnerable.
- **Matriz de calor "antes / después"** (ISO/IEC 27005):
  - **Antes** = *riesgo inherente*: el riesgo de cada amenaza STRIDE sin controles. Sale del threat model de la Entrega 1.
  - **Después** = *riesgo residual*: el riesgo con los controles implementados **y verificados** por pruebas.
- **El pentest demuestra que cada control funciona.** Cada caso de abuso se ejecuta y la evidencia es el bloqueo: 401, 403, 429, WAF block o alerta en el SIEM. Cualquier debilidad real que encuentren las herramientas (SCA, MobSF, ZAP, Checkov, Prowler) se registra como HAL y se corrige.
- Toda amenaza identificada en la Entrega 1 debe terminar con: control (CTRL) → prueba → evidencia → riesgo residual.

### Controles de diseño obligatorios
| CTRL | Control | Amenaza que mitiga | Referencia | Capa |
|---|---|---|---|---|
| CTRL-01 | Autorización a nivel de objeto: cada handler valida que el recurso pertenece al `sub` del token | BOLA / IDOR | API1:2023 | 2b |
| CTRL-02 | PIN de transacción con hash `scrypt` (Node crypto) + sal; bloqueo de 15 min tras 5 intentos fallidos | Fuerza bruta del PIN | API6:2023 / CWE-307 | 2b |
| CTRL-03 | DTOs de respuesta mínimos; DPI y teléfono enmascarados (`****1234`) | Exposición excesiva de datos | API3:2023 | 1 / 2d |
| CTRL-04 | Validación de entrada con `zod` en modo `.strict()` (rechaza campos no permitidos) | Mass assignment, inyección | API3:2023 / A03 | 2a |
| CTRL-05 | Paginación por cursor con tope de 50 + throttling por usuario (usage plan) | Exfiltración masiva vía paginación | API4:2023 | 2d / 5 |
| CTRL-06 | Cabecera `Idempotency-Key` + `TransactWriteItems` con `ConditionExpression` (saldo ≥ monto) | Doble gasto / race condition | API6:2023 | 2b |
| CTRL-07 | Tokens en `expo-secure-store` (Keystore) con `requireAuthentication` biométrico | Robo de tokens en el dispositivo | MASVS-STORAGE | 1 |
| CTRL-08 | TLS 1.2+ en el endpoint por defecto de API Gateway (sin dominio propio, por costo) + pinning de las llaves públicas de Amazon Root CA, con pin de respaldo. TLS 1.3 queda como riesgo residual **aceptado** y recomendación del roadmap | MITM | MASVS-NETWORK | 1 |
| CTRL-09 | Logs JSON estructurados con redacción de tokens y PII + `correlationId` | Fuga en logs / repudio | A09 / CWE-532 | 1 / 7 |
| CTRL-10 | SCA en CI que falla con hallazgos High/Critical + Dependabot (alerts + security updates; npm con `open-pull-requests-limit: 0` = solo PR de seguridad) | Dependencias vulnerables | A06 | 2c |
| CTRL-11 | Dockerfile multi-stage, imagen base fijada por digest, usuario no root | Contenedor comprometido | CIS Docker | 3 |
| CTRL-12 | Terraform: S3 con Block Public Access + SSE-KMS + versionado; un rol IAM de menor privilegio por Lambda; Checkov en CI | Mala configuración cloud | CIS AWS | 4 / 5 |
| CTRL-13 | CORS restringido, cabeceras de seguridad, errores genéricos con `correlationId` | Divulgación de información | API8:2023 | 2d |
| CTRL-14 | Autorización por función: grupo Cognito `admins` validado en el authorizer **y** en el handler | BFLA / escalada de privilegios | API5:2023 | 2b |
| CTRL-15 | freeRASP (root/hook/emulador/tampering) + Hermes bytecode + R8 | Ingeniería inversa / hooking | MASVS-RESILIENCE | 2a / 3 |
| CTRL-16 | Cero secretos en el cliente; secretos en SSM; gitleaks en CI + Secret Protection y push protection de GitHub (historial escaneado sin hallazgos antes de publicar) | Secretos expuestos | CWE-798 | 2a / 7 |
| CTRL-17 | AWS WAF: Core Rule Set + Known Bad Inputs + regla rate-based | OWASP Top 10 / DoS de capa 7 | — | 5 |
| CTRL-18 | MFA TOTP obligatorio + OAuth2 Authorization Code + PKCE + tokens de corta vida | Suplantación | MASVS-AUTH | 2b |
| CTRL-19 | DynamoDB, S3 y CloudWatch Logs cifrados con KMS CMK propia, con rotación anual | Divulgación en reposo | ISO 27001 A.8.24 | 1 |
| CTRL-20 | CloudTrail multi-región + CloudWatch → Wazuh con reglas de alerta | Detección / repudio | ISO 27001 A.8.15–16 | 7 |
| CTRL-21 | Despliegue por OIDC GitHub → AWS (sin llaves estáticas); ruleset `main-protegida` (PR obligatorio, sin force push ni borrado, bypass vacío) | Compromiso de CI/CD | SLSA / A08 | 7 |

## 6. Escalas de valoración (fijas, no cambiar)

### Triada CIA y criticidad del activo
- A (Alta) = 3, M (Media) = 2, B (Baja) = 1.
- **Valor = C + I + D** (3–9) → 8–9 Crítica · 6–7 Alta · 4–5 Media · 3 Baja.

### DREAD (cada factor 1–10)
- **Puntaje = (D + R + E + A + Di) / 5** → ≥7 Alta · 4–6.9 Media · <4 Baja.

### Conversión DREAD → matriz 5×5
- **Probabilidad (1–5)** = redondeo hacia arriba de ((R + E + Di) / 3) / 2.
- **Impacto (1–5)** = redondeo hacia arriba de ((D + A) / 2) / 2.
- **Riesgo = P × I** → 1–4 Bajo · 5–9 Medio · 10–14 Alto · 15–25 Crítico.

### Tratamiento (enunciado)
Aceptar · Eliminar · Evitar · Mitigar · Transferir.

- **Tipo de riesgo:** Software · Seguridad · Técnico · Cloud · Cumplimiento.
- **Impacto de negocio:** Reputacional · Operacional · Financiero · Legal.

---

## 7. Las 7 capas aplicadas a Q-Wallet

| # | Capa | Qué se evalúa aquí |
|---|---|---|
| 1 | Datos | Cifrado en reposo (KMS, Keystore) y en tránsito (TLS 1.3), enmascaramiento de DPI/teléfono, gestión de llaves |
| 2a | Código | Sanitización, validación de entrada, secretos, prácticas seguras |
| 2b | Aplicación | Lógica de negocio (transferencias, PIN, límites), autenticación y autorización |
| 2c | Implementación | Dependencias npm, SDKs, frameworks |
| 2d | Perímetro de aplicación | Endpoints públicos vs. privados, CORS, rate limiting por endpoint |
| 3 | Host | Imágenes de contenedor, runtime Lambda, dispositivo Android (root) |
| 4 | Red interna | Roles IAM por Lambda, microsegmentación lógica (Lambdas sin VPC: justificar) |
| 5 | Perímetro cloud / red | AWS WAF, throttling de API Gateway, Shield Standard |
| 6 | Seguridad física | Centros de datos AWS (SOC 2, ISO 27001), dispositivo físico del cliente |
| 7 | Políticas y concientización | Política de contraseñas/MFA, política DevSecOps, gestión de incidentes, capacitación |

---

## 8. Normativas y estándares de referencia

- ISO/IEC 27001:2022 (Anexo A) e ISO/IEC 27005:2022 (gestión de riesgos).
- OWASP MASVS v2 / MASTG, OWASP API Security Top 10 2023, OWASP Top 10 (verificar versión vigente).
- STRIDE (Microsoft), DREAD.
- NIST CSF 2.0.
- PCI DSS v4.0.1 (referencial; no se procesan tarjetas).
- **Guatemala:** Resolución JM-104-2021, Reglamento para la Administración del Riesgo Tecnológico (Junta Monetaria / SIB).
- **Guatemala:** Decreto 67-2001, Ley contra el Lavado de Dinero u Otros Activos (contexto KYC).
- Guatemala no tiene una ley general de protección de datos personales; verificar el estado de iniciativas antes de afirmarlo en el informe.

**Regla:** toda cita APA 7 debe ser una fuente real y verificable. Nunca inventar referencias.

---

## 9. Convenciones

### Identificadores
| Prefijo | Uso |
|---|---|
| `ACT-xx` | Activo |
| `AME-xx` | Amenaza (STRIDE) |
| `HAL-xx` | Hallazgo confirmado en pruebas |
| `RSK-xx` | Riesgo |
| `CTRL-xx` | Control |
| `EVD-xx` | Evidencia (captura/video) |

- **Capturas:** `EVD-<fase>-<nn>_<descripcion>.png` (ej. `EVD-2-03_threatdragon_stride.png`). Siempre con fecha/hora visible cuando sea posible.

### Roles ficticios (para propietario / custodio)
| Rol | Persona |
|---|---|
| Gerente de Producto (propietario de activos de negocio) | — |
| Lead Security Architect | Integrante 1 — PENDIENTE |
| DevSecOps Engineer (custodio de infraestructura) | Integrante 2 — PENDIENTE |
| Pentester / Analista de Riesgos | Integrante 3 — PENDIENTE |

### Repo
```
/docs          contexto, plantillas, threat model (.json Threat Dragon), diagramas
/docs/evidencias  capturas EVD-*
/docs/entregas    Word de cada entrega
/mobile        app Expo
/services      svc-profile, svc-accounts, svc-transfers, svc-budgets, svc-admin
/infra         Terraform
/.github/workflows  pipelines
GEMINI.md
```

### Formato del informe (UMG)
- Arial 12, interlineado 1.5, sangría de primera línea 1.27 cm, márgenes 2.54 cm, texto justificado.
- Tablas y figuras numeradas en estilo APA 7. Referencias en APA 7 con sangría francesa.
- Estructura obligatoria: la del enunciado, **Opción A**, sin renumerar secciones.

---

## 10. Pendientes

- [ ] Nombres de integrantes y asignación de roles.
- [ ] Fecha de entrega final y fechas de otras entregas parciales.
- [ ] ¿La Entrega 1 incluye presentación?
- [ ] ¿Existe plantilla oficial de portada UMG?
- [ ] Verificar que el Free Plan de AWS permite WAF y ECR.
- [ ] Revisar los 6 PR de Dependabot en `/mobile`: cerrar los de versión (Tailwind 4 y TypeScript 7 rompen §3.1).
- [ ] Conciliar 5 alertas de Dependabot vs. 33 de `npm audit` (fase SCA).

---

## 11. Estado actual

> Se reescribe al cierre de **cada** sesión de trabajo. El historial completo queda en `BITACORA.md`.

| Campo | Valor |
|---|---|
| Última actualización | 05-oct-2026 (2) (Manual Claude + PowerShell + GitHub web) |
| Fase actual | Preparación del entorno, cerrando; luego Entrega 1 — Selección y Planificación + Activos y Riesgos |
| Versión de la app | Expo SDK 57 (React Native 0.86.3, TS strict), NativeWind 4.2.7, Tailwind 3.4.19, Reanimated 4, expo-router, freeRASP 5.2.2, 8 pantallas simuladas |
| Completado | Primer build nativo Android (`EVD-1-05`). Repo público con ruleset `main-protegida` verificado (`EVD-1-04c`, `EVD-1-06`), Secret Protection y push protection (`EVD-1-04a`), Dependabot alerts + security updates (`EVD-1-04b`), gitleaks del historial sin hallazgos (`EVD-1-07`). `dependabot.yml` con npm solo seguridad. |
| En curso | — |
| Siguiente paso / Pendientes | 1) Revisar y cerrar PR de Dependabot de versión; 2) Corregir textos falsos de la UI; 3) Configurar `expo-build-properties`; 4) Cuenta AWS; 5) Entrega 1 (17-oct-2026) |
| Regla de trabajo | Sin commits directos a `main` (personas ni agy): rama → PR → merge. Cada cambio de la app se valida con build nativo |
| Bloqueos | Pendientes del §10 |
| Recursos AWS desplegados | Ninguno |
| Gasto AWS acumulado | US$0 |
