# ESTADO — Q-Wallet

> Punto de arranque de cada chat. Se reescribe al cerrar cada bloque. Máximo una página.

**Actualizado:** 30-oct-2026 · **Hoy toca:** merge del PR #36 y bloque 4

## Fechas
| Hito | Fecha | Fase del enunciado |
|---|---|---|
| Entrega 1 | 17-oct-2026 ✔ | Fase 1 |
| **Entrega 2** (presentación de 5 min, cámara abierta, resumen ejecutivo, sin generalidades) | **sáb 7-nov-2026** | Fase 2 |
| Entrega final | sáb 28-nov-2026 `[VERIFICAR]` con el catedrático | Fases 3 a 6 + informe completo |

## Bloques
| # | Bloque | Fases | Secciones del informe | Estado |
|---|---|---|---|---|
| 1 | Terraform de toda la arquitectura + despliegue automático con OIDC + 4.1, 4.2 y 4.5 del Word | 2 y 5 | 4.1, 4.2, 4.5 | ☑ Desplegado y verificado (30-oct) |
| 2 | Presentación del 7-nov (5 diapositivas) | 2 | — | ☑ Lista (Claude Slides; guion en `docs/entregas/Entrega2_Presentacion.md`). Falta ensayarla |
| 3 | Lambdas con código seguro + SAST/SCA en el flujo automático + minSdk 29 | 3 | 3.4, 3.5, 4.3, 4.4, 4.6 | ☑ PR #36 (falta merge) |
| 4 | Pentest caja negra y gris, OWASP API Top 10, casos de abuso, perímetro | 4 | 3.1, 3.2, 3.3, 3.6 | ☐ Siguiente |
| 5 | WAF, RASP, SIEM, alertas, tratamiento, mapa de calor "después" | 6 | 5.1 a 5.6 | ☐ |
| 6 | Word final, dictamen, presentación final | Todas | 0, 6 | ☐ |

## Qué dejó el bloque 3 (PR #36, 30-oct-2026)
- **Código real de las 5 Lambdas** (`services/`, TypeScript estricto): módulo común con JWT verificado también en la Lambda (aws-jwt-verify), zod `.strict()`, logs con redacción, errores genéricos, auditoría y paginación con tope. PIN con scrypt y bloqueo atómico; transferencias con Idempotency-Key + transacción de DynamoDB; BOLA → 404; `/admin` exige grupo `admins` (CTRL-14) y motivo + canal de verificación (CTRL-23). **60 pruebas vitest, todas en verde.** Cada cuenta nueva empieza con Q1,000.00 simulados; tope Q5,000.00 por transferencia.
- **Flujo `devsecops.yml`**: pruebas, Semgrep (608 reglas + 7 propias, `semgrep --test` 7/7), CodeQL (103 reglas), npm audit con compuerta y excepciones con vencimiento, Trivy + SBOM, gitleaks (89 commits). Todo en 0 hallazgos graves. Corre en cada PR, en main y cada lunes. Resultados en el comentario del PR y en el issue "Evidencias DevSecOps".
- **`infra.yml`**: construye las 5 imágenes reales, prueba de humo con el runtime real (GET /me sin token → 401) y Trivy (24 HIGH → 0). Checkov: Terraform 282 pasan, Dockerfile 295 pasan, 0 fallan.
- **Hallazgos**: HAL-01 zod 4.6.5 (corregido a 4.6.7), HAL-02 y HAL-03 (dependencias de Expo, aceptadas hasta 28-nov), HAL-04 textos falsos de Welcome (corregido), HAL-05 imagen base (corregido). EVD-3-10: PR #37 demostró que la compuerta bloquea zod 4.6.5 (cerrado sin merge, rama conservada).
- **App**: minSdk 29, R8 y shrink en release, sin tráfico en claro, inspector de red apagado. Falta validarlo con un build nativo (abajo).
- **IAM**: svc-profile puede crear la cuenta inicial (PutItem en `cuentas` y `movimientos`). Lambdas con `COGNITO_CLIENT_ID` y `API_SCOPE`. Cambios en sitio, sin destrucciones.
- **Word** `docs/entregas/Final_Secciones_3-4_3-5_4-3_4-4_4-6_DevSecOps.docx` (12 págs., Tablas 30–37, Figura 8, validado y renderizado). Script `scripts/bloque3_word.py`.

## Lo que Daniel hace a mano (bloque 3)
1. Revisar y dar **Merge al PR #36**. El despliegue publica las imágenes reales y verifica AWS (issue "Evidencias AWS").
2. Validar la app con build nativo (PowerShell normal, emulador abierto):
   `cd C:\dev\q-wallet; git pull; . .\scripts\dev-env.ps1; cd mobile; npm install --legacy-peer-deps; npx expo prebuild --clean; npx expo run:android --variant release`
   Resultado esperado: la app abre en el emulador; la pantalla de bienvenida dice "Conexión cifrada TLS 1.3 · Diseñada con referencia a la JM-98-2025". Si falla, copiar las últimas 30 líneas.

## Antes (bloques 1 y 2, detalle en BITÁCORA)
- Cuenta AWS de Daniel (`qwallet-umg`, us-east-1, Free plan, US$100 de crédito). Bootstrap OIDC hecho; MFA raíz y presupuesto de US$5 confirmados. Primer despliegue completo y verificado el 30-oct (EVD-3-11, 3-12, 3-13, 5-04 en el issue "Evidencias AWS", #28).
- Word de la Entrega 2: `docs/entregas/Entrega2_Seccion_4_Arquitectura_Controles.docx` (4.1, 4.2, 4.5). Presentación del 7-nov en Claude Slides (privada).

## Decisiones tomadas (29-oct-2026)
- El merge del PR cuenta como aprobación del despliegue (sin aprobación manual en el entorno `dev`). En el Word final, ajustar el texto del plan de RSK-32 (sección 2.5.5) a "PR revisado y aprobado por merge + revisión automática de destrucciones".
- ECR conserva las 5 imágenes más recientes por servicio y borra solas las más viejas.
- Las entregas parciales no llevan portada ni índice; solo el informe final.

## Antes del 7-nov
- Ensayar la presentación con cronómetro (notas del orador en cada diapositiva) y descargarla como PDF de respaldo.
- La presentación es privada: si el catedrático necesita el enlace, compartirla desde el menú Compartir; si no, presentar desde la pantalla o el PDF.

## Decisiones pendientes
- Tope por transferencia (aplicado: Q5,000.00) y saldo inicial simulado (Q1,000.00).
- Aprobar las excepciones SCA de HAL-02 y HAL-03 (vencen el 28-nov) o subir a Expo SDK 58.
- Dependency-Check y Snyk: crear llaves (`NVD_API_KEY`, `SNYK_TOKEN`) o dejarlos opcionales.
- Borrar `services/hola` (imagen provisional, ya no se usa): requiere aprobación (regla de borrado).
- Integración de la app con la API (PKCE, Keystore, pinning, freeRASP): ¿en el bloque 4 o en el 5?
- SIEM (bloque 5): Wazuh necesita 4 GB+ de RAM y no cabe en US$5; opción: CloudWatch + alarmas + CloudTrail.
- Pruebas en el teléfono (Frida, freeRASP): emulador en la computadora de Daniel o intento en GitHub Actions.
- Al ensamblar el Word final: el Word de la Entrega 2 puede tener `w:tblLayout` duplicado en las tablas (se corrigió en el script del bloque 3; revisar con el validador).

## Recursos AWS
Cuenta de Daniel, us-east-1: bootstrap y toda la arquitectura desplegada el 30-oct (WAF apagado). Las Lambdas todavía corren la imagen provisional hasta el merge del PR #36. Gasto esperado ~US$1 al mes (llave KMS); WAF ~US$8 al mes solo encendido.
