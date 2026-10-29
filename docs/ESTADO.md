# ESTADO — Q-Wallet

> Punto de arranque de cada chat. Se reescribe al cerrar cada bloque. Máximo una página.

**Actualizado:** 29-oct-2026 · **Hoy toca:** primer despliegue (pasos manuales de abajo) y luego bloque 2

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
| 2 | Presentación del 7-nov (5 diapositivas) | 2 | — | ☐ Siguiente |
| 3 | Lambdas con código seguro + SAST/SCA en el flujo automático + minSdk 29 | 3 | 3.4, 3.5, 4.3, 4.4, 4.6 | ☐ |
| 4 | Pentest caja negra y gris, OWASP API Top 10, casos de abuso, perímetro | 4 | 3.1, 3.2, 3.3, 3.6 | ☐ |
| 5 | WAF, RASP, SIEM, alertas, tratamiento, mapa de calor "después" | 6 | 5.1 a 5.6 | ☐ |
| 6 | Word final, dictamen, presentación final | Todas | 0, 6 | ☐ |

## Qué dejó el bloque 1
- `/infra`: KMS (AES-256, rotación anual), 8 tablas DynamoDB (una por tipo de dato), Cognito (PKCE, MFA TOTP, tokens de 15 min), API Gateway solo TLS 1.3 con authorizer en las 18 rutas, 5 Lambdas en contenedor (imagen provisional `services/hola`, responde 501) con un rol IAM por función, ECR, CloudTrail, WAF apagable (`WAF_HABILITADO`).
- `infra/bootstrap/bootstrap.sh`: bucket del estado, OIDC, límite de permisos y los roles `qwallet-gha-plan` y `qwallet-gha-despliegue` (este último no puede borrar la llave, tablas, user pool, buckets ni la auditoría).
- `.github/workflows/infra.yml`: en cada PR fmt, validate, Checkov y plan; al hacer merge, despliegue (se detiene si el plan borra algo no aprobado en `infra/destrucciones_aprobadas.txt`) y verificación automática (EVD-3-11, 3-12, 3-13, 5-04) publicada en el issue "Evidencias AWS".
- Word `docs/entregas/Entrega2_Seccion_4_Arquitectura_Controles.docx` (13 págs.): 4.1, 4.2 y 4.5, Figura 7 y Tablas 24 a 29 (numeración provisional). Faltan las evidencias del despliegue (marcadas `[EVIDENCIA PENDIENTE]`) y los títulos exactos de 4 y 4.5 (`[VERIFICAR]`).

## Lo que Daniel hace a mano (una sola vez, después del merge del PR #22)
1. GitHub → Settings → Environments → New environment `dev` → Deployment branches: "Selected branches" → agregar `main`.
2. Consola de AWS en **us-east-1** con el usuario administrador → abrir CloudShell → pegar:
   `curl -fsSLO https://raw.githubusercontent.com/dbarrios95/q-wallet/main/infra/bootstrap/bootstrap.sh && bash bootstrap.sh`
   Resultado esperado: termina con "Listo." y muestra el número de cuenta.
3. GitHub → Settings → Secrets and variables → Actions → New repository secret `AWS_ACCOUNT_ID` con ese número (no pegarlo en el chat).
4. GitHub → Actions → infra → Run workflow (rama main). Ese es el primer despliegue.
5. Confirmar en la consola que el plan gratuito permite AWS WAF y ECR (si ECR falla, el paso 4 lo muestra).

## Decisiones pendientes
- Aprobación manual en el entorno `dev` antes de cada despliegue (preguntada al cerrar el bloque 1).
- Borrado automático de imágenes viejas en ECR (preguntado al cerrar el bloque 1).
- Títulos exactos de la sección 4 y de 4.5 en el enunciado.
- SIEM (bloque 5): Wazuh necesita 4 GB+ de RAM y no cabe en US$5; opción: CloudWatch + alarmas + CloudTrail.
- Pruebas en el teléfono (Frida, freeRASP): emulador en la computadora de Daniel o intento en GitHub Actions.

## Recursos AWS
Ninguno desplegado. Gasto US$0. Región us-east-1. Al desplegar: ~US$1 al mes (llave KMS); WAF ~US$8 al mes solo encendido.
