# ESTADO — Q-Wallet

> Punto de arranque de cada chat. Se reescribe al cerrar cada bloque. Máximo una página.

**Actualizado:** 30-oct-2026 · **Hoy toca:** cerrar el primer despliegue (faltan 2 permisos; bootstrap otra vez y Run workflow, ver "Despliegue") y luego bloque 3

## Fechas
| Hito | Fecha | Fase del enunciado |
|---|---|---|
| Entrega 1 | 17-oct-2026 ✔ | Fase 1 |
| **Entrega 2** (presentación de 5 min, cámara abierta, resumen ejecutivo, sin generalidades) | **sáb 7-nov-2026** | Fase 2 |
| Entrega final | sáb 28-nov-2026 `[VERIFICAR]` con el catedrático | Fases 3 a 6 + informe completo |

## Bloques
| # | Bloque | Fases | Secciones del informe | Estado |
|---|---|---|---|---|
| 1 | Terraform de toda la arquitectura + despliegue automático con OIDC + 4.1, 4.2 y 4.5 del Word | 2 y 5 | 4.1, 4.2, 4.5 | ◐ Código y Word listos (PR #22); falta el primer despliegue |
| 2 | Presentación del 7-nov (5 diapositivas) | 2 | — | ☑ Lista (Claude Slides; guion en `docs/entregas/Entrega2_Presentacion.md`). Falta ensayarla |
| 3 | Lambdas con código seguro + SAST/SCA en el flujo automático + minSdk 29 | 3 | 3.4, 3.5, 4.3, 4.4, 4.6 | ☐ Siguiente |
| 4 | Pentest caja negra y gris, OWASP API Top 10, casos de abuso, perímetro | 4 | 3.1, 3.2, 3.3, 3.6 | ☐ |
| 5 | WAF, RASP, SIEM, alertas, tratamiento, mapa de calor "después" | 6 | 5.1 a 5.6 | ☐ |
| 6 | Word final, dictamen, presentación final | Todas | 0, 6 | ☐ |

## Despliegue (30-oct-2026)
- **Cuenta AWS nueva de Daniel** (`qwallet-umg`, registro clásico "AWS (advanced)", Free plan con US$100 de crédito, us-east-1). Ya no se usa la cuenta de Katherine.
- Se descartó una cuenta de la "nueva experiencia" de AWS (proyectos con Builder ID): sus SCP administradas por AWS prohíben `iam:*Provider*` (no se puede crear el OIDC) y bloquearon `s3:CreateBucket`. No se creó nada en ella.
- Hecho por Daniel: bootstrap en CloudShell **OK** (bucket del estado, OIDC, límite de permisos, roles `qwallet-gha-plan` y `qwallet-gha-despliegue`). Secreto `AWS_ACCOUNT_ID` y entorno `dev` (solo `main`) configurados por Daniel [VERIFICAR que el entorno quedó limitado a `main`].
- OIDC resuelto (PR #30: GitHub manda el `sub` con números fijos del dueño y del repo). El "Run workflow" del 30-oct ya entró a AWS y creó casi todo: imágenes en ECR, llave KMS, tablas, Cognito, las 5 Lambdas, las 18 rutas y CloudTrail.
- **Falló al final por dos permisos** del rol `qwallet-gha-despliegue`: crear el rol vinculado de API Gateway (`AWSServiceRoleForAPIGateway`, se crea una sola vez por cuenta) y `cognito-idp:DescribeUserPoolDomain` (no acepta límite por recurso). Corregido en el PR "fix/permisos-despliegue". Después del merge: bootstrap otra vez en CloudShell y "Run workflow". Terraform sigue desde donde quedó; no borra nada.
- Pendiente de Daniel: MFA de la cuenta raíz y presupuesto de US$5 en Budgets [VERIFICAR si ya se hicieron].
- Evidencia EVD-1-03 (Entrega 1) quedó de la cuenta de Katherine; no se toca.

## Qué dejó el bloque 2
- Presentación Claude Slides "Q-Wallet — Entrega 2 (Fase 2)" en claude.ai, 5 diapositivas (~5 min), letra Inter y paleta de la app, notas del orador en cada una: (1) portada y resumen ejecutivo, (2) flujo de datos en 9 pasos con la Figura 7, (3) Zero Trust y matriz de menor privilegio, (4) cifrado AES-256 y TLS 1.3, (5) cómo se comprueba (Checkov 282/0, 11 de 14 requisitos, 3 pruebas automáticas) y Fase 3.
- Todas las cifras salen del Word de la sección 4. Si el despliegue corre antes del 7-nov, la diapositiva 5 se puede cambiar a resultados reales.

## Qué dejó el bloque 1
- `/infra`: KMS (AES-256, rotación anual), 8 tablas DynamoDB (una por tipo de dato), Cognito (PKCE, MFA TOTP, tokens de 15 min), API Gateway solo TLS 1.3 con authorizer en las 18 rutas, 5 Lambdas en contenedor (imagen provisional `services/hola`, responde 501) con un rol IAM por función, ECR, CloudTrail, WAF apagable (`WAF_HABILITADO`).
- `infra/bootstrap/bootstrap.sh`: bucket del estado, OIDC, límite de permisos y los roles `qwallet-gha-plan` y `qwallet-gha-despliegue` (este último no puede borrar la llave, tablas, user pool, buckets ni la auditoría).
- `.github/workflows/infra.yml`: en cada PR fmt, validate, Checkov y plan; al hacer merge, despliegue (se detiene si el plan borra algo no aprobado en `infra/destrucciones_aprobadas.txt`) y verificación automática (EVD-3-11, 3-12, 3-13, 5-04) publicada en el issue "Evidencias AWS".
- Word `docs/entregas/Entrega2_Seccion_4_Arquitectura_Controles.docx` (13 págs.): 4.1, 4.2 y 4.5, Figura 7 y Tablas 24 a 29 (numeración provisional). Faltan las evidencias del despliegue (marcadas `[EVIDENCIA PENDIENTE]`) . Títulos corregidos con el enunciado ("4. Mitigación y ciberseguridad", "4.5 Hardening de infraestructura cloud").

## Lo que Daniel hace a mano (una sola vez, después del merge del PR #22)
0. Merge del PR #22 primero y después el del bloque 2.
1. GitHub → Settings → Environments → New environment `dev` → Deployment branches: "Selected branches" → agregar `main`.
2. Consola de AWS en **us-east-1** con el usuario administrador → abrir CloudShell → pegar:
   `curl -fsSLO https://raw.githubusercontent.com/dbarrios95/q-wallet/main/infra/bootstrap/bootstrap.sh && bash bootstrap.sh`
   Resultado esperado: termina con "Listo." y muestra el número de cuenta.
3. GitHub → Settings → Secrets and variables → Actions → New repository secret `AWS_ACCOUNT_ID` con ese número (no pegarlo en el chat).
4. GitHub → Actions → infra → Run workflow (rama main). Ese es el primer despliegue.
5. Confirmar en la consola que el plan gratuito permite AWS WAF y ECR (si ECR falla, el paso 4 lo muestra).

## Decisiones tomadas (29-oct-2026)
- El merge del PR cuenta como aprobación del despliegue (sin aprobación manual en el entorno `dev`). En el Word final, ajustar el texto del plan de RSK-32 (sección 2.5.5) a "PR revisado y aprobado por merge + revisión automática de destrucciones".
- ECR conserva las 5 imágenes más recientes por servicio y borra solas las más viejas.
- Las entregas parciales no llevan portada ni índice; solo el informe final.

## Antes del 7-nov
- Ensayar la presentación con cronómetro (notas del orador en cada diapositiva) y descargarla como PDF de respaldo.
- La presentación es privada: si el catedrático necesita el enlace, compartirla desde el menú Compartir; si no, presentar desde la pantalla o el PDF.

## Decisiones pendientes
- SIEM (bloque 5): Wazuh necesita 4 GB+ de RAM y no cabe en US$5; opción: CloudWatch + alarmas + CloudTrail.
- Pruebas en el teléfono (Frida, freeRASP): emulador en la computadora de Daniel o intento en GitHub Actions.

## Recursos AWS
Cuenta de Daniel, us-east-1. Bootstrap (bucket del estado, OIDC, 4 políticas, 2 roles) y, desde el 30-oct, casi toda la arquitectura (despliegue parcial: falta el stage `v1` de API Gateway y el dominio de Cognito). Gasto esperado ~US$1 al mes (llave KMS); WAF ~US$8 al mes solo encendido.
