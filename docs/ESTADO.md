# ESTADO — Q-Wallet

> Punto de arranque de cada chat. Se reescribe al cerrar cada bloque. Máximo una página.

**Actualizado:** 10-nov-2026 · **Hoy toca:** bloque 6 (Word final, dictamen 6.1 a 6.6, presentación final)

## Fechas
| Hito | Fecha | Fase del enunciado |
|---|---|---|
| Entrega 1 | 17-oct-2026 ✔ | Fase 1 |
| Entrega 2 (presentación de 5 min) | 7-nov-2026 (tentativo) [VERIFICAR con Daniel si se presentó o se corrió] | Fase 2 |
| **Entrega final** (incluye la presentación final) | **sáb 28-nov-2026** (confirmada) | Fases 3 a 6 + informe completo |

> Las entregas parciales van sin portada ni índice; la portada, el índice y el resumen ejecutivo se agregan solo en el informe final (bloque 6).

## Bloques
| # | Bloque | Secciones | Estado |
|---|---|---|---|
| 1 | Terraform + despliegue OIDC | 4.1, 4.2, 4.5 | ☑ |
| 2 | Presentación del 7-nov | — | ☑ Lista (Claude Slides) |
| 3 | Lambdas, SAST/SCA, minSdk 29 | 3.4, 3.5, 4.3, 4.4, 4.6 | ☑ |
| 4 | Pentest, OWASP API, casos de abuso | 3.1, 3.2, 3.3, 3.6 | ☑ |
| 5 | WAF, RASP, SIEM, alertas, tratamiento, mapa "después" | 5.1 a 5.6 | ☑ PR de cierre (este) |
| 6 | Word final, dictamen, presentación final | 0, 6 | ☐ Siguiente |

## Qué dejó el bloque 5 (PR #47, #50, #51, #52, #58 y este)
- **SIEM en CloudWatch** (`infra/monitoreo.tf`): CloudTrail → CloudWatch Logs, 14 reglas de correlación, 5 consultas guardadas, 9 alarmas (+1 del WAF) → SNS cifrado → correo (confirmado), tablero `qwallet-seguridad`. Probado de punta a punta: correos reales (EVD-5-06d).
- **WAF** con SQLi agregado (HAL-07): 9/9 ataques bloqueados con la regla correcta (EVD-5-02/02b). Flujo `waf-siem.yml` (modo completo o **consultas**); el WAF se apaga solo.
- **App**: freeRASP con política de reacción, pinning de las raíces de Amazon y cliente `llamarApi()` por XHR (HAL-13: `fetch` de Expo SDK 57 no tiene pinning; regla Semgrep lo prohíbe). Flujo `movil.yml`: APK release, MobSF, emulador con Frida, MITM y almacenamiento.
- **Hallazgos HAL-06 a HAL-16** en `docs/REGISTRO_RIESGOS.md` (todos cerrados salvo HAL-09 aceptado y HAL-16 abierto).
- **Riesgo**: inherente 580 → residual verificado 208; 0 Crítico, 1 Alto (RSK-11, aceptado temporal), 26 Medio, 14 Bajo. `scripts/bloque5_residual.py` + `docs/threat-model/verificacion_bloque5.json`.
- **Word** `docs/entregas/Final_Secciones_5-1_a_5-6_Operaciones.docx` (24 págs., Tablas 42–53, Figuras 10–13; Arial 12 / 1.5, render revisado). Evidencias en `docs/evidencias/bloque5/` y `resultados.json`.
- Cuenta endurecida por el bootstrap (S3 BPA de cuenta, política de contraseñas IAM). Despliegues con aprobación manual de Daniel (entorno `dev`).

## Decisiones tomadas por Daniel (31-oct-2026)
SIEM con CloudWatch (Wazuh al roadmap); aviso por correo; pruebas del teléfono en Actions; conexión mínima app–API; gitleaks ignora 13 falsos positivos (`.gitleaksignore`); WAF solo para pruebas (RSK-11 Alto aceptado temporal); aprobación manual de despliegues (RSK-32 → P1×I5).

## Pendientes para el bloque 6
- Ensamblar el informe final (secciones 0 a 6) con los Word de cada bloque; renumerar tablas y figuras; revisar `w:tblLayout` duplicado del Word de la Entrega 2; portada, índice y resumen ejecutivo.
- Dictamen 6.1 a 6.6. Roadmap: Wazuh, inicio de sesión real con Cognito en la app, HAL-16 (throttling), WAF permanente en producción, usuario IAM administrador en vez de root, dominio propio (HAL-09), Play App Signing.
- **Vencen el 28-nov** las excepciones SCA de HAL-02 (decode-uri-component) y zod de `@expo/cli`: revisar Expo SDK 58 antes.
- Alarma `aws-no-autorizado` salta con los planes de PR (rol de plan sin `kms:Decrypt`): excluir ese rol como al de Prowler.
- PR de Dependabot #53 a #57 sin revisar (setup-java 6, CodeQL 4.39.3, proveedor AWS 6.71.0).
- [VERIFICAR] costo real de CloudWatch en la factura de noviembre; origen del archivo `files/tcb` de la app (probable freeRASP).

## Recursos AWS
Cuenta de Daniel, us-east-1: toda la arquitectura, SIEM y alarmas desplegados; WAF apagado. Gasto esperado ~US$2–3 al mes (llave KMS + métricas de CloudWatch) [VERIFICAR]; el WAF ~US$9 al mes solo encendido.
