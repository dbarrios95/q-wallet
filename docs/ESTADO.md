# ESTADO — Q-Wallet

> Punto de arranque de cada chat. Se reescribe al cerrar cada bloque. Máximo una página.

**Actualizado:** 30-oct-2026 · **Hoy toca:** merge del PR del bloque 4 + bootstrap del rol de pentest

## Fechas
| Hito | Fecha | Fase del enunciado |
|---|---|---|
| Entrega 1 | 17-oct-2026 ✔ | Fase 1 |
| **Entrega 2** (presentación de 5 min, cámara abierta, resumen ejecutivo, sin generalidades) | **sáb 7-nov-2026** | Fase 2 |
| Entrega final | sáb 28-nov-2026 `[VERIFICAR]` con el catedrático | Fases 3 a 6 + informe completo |

## Bloques
| # | Bloque | Fases | Secciones del informe | Estado |
|---|---|---|---|---|
| 1 | Terraform de toda la arquitectura + despliegue automático con OIDC + 4.1, 4.2 y 4.5 | 2 y 5 | 4.1, 4.2, 4.5 | ☑ Desplegado y verificado |
| 2 | Presentación del 7-nov (5 diapositivas) | 2 | — | ☑ Lista (Claude Slides; guion en `docs/entregas/Entrega2_Presentacion.md`). Falta ensayarla |
| 3 | Lambdas con código seguro + SAST/SCA + minSdk 29 | 3 | 3.4, 3.5, 4.3, 4.4, 4.6 | ☑ Merge (PR #36) y desplegado el código real |
| 4 | Pentest caja negra y gris, OWASP API Top 10, casos de abuso, perímetro | 4 | 3.1, 3.2, 3.3, 3.6 | ☑ PR abierto (falta merge) |
| 5 | WAF, RASP, SIEM, alertas, tratamiento, mapa de calor "después" | 6 | 5.1 a 5.6 | ☐ Siguiente |
| 6 | Word final, dictamen, presentación final | Todas | 0, 6 | ☐ |

## Qué dejó el bloque 4 (este PR, 30-oct-2026)
- **Arnés de pentest de caja gris** `services/pentest/pentest.test.ts` (vitest): ejecuta cada caso de abuso de servidor y cada riesgo OWASP API Top 10 (2023) contra los manejadores reales. **71 pruebas en verde** (60 del bloque 3 + 11 nuevas). Genera `EVD-4-13` (tabla de 11 casos de abuso, todos bloqueados) y `EVD-4-12` (18 pruebas OWASP API; 8 riesgos aplican y quedan cubiertos, 2 no aplican); cada caso mapea a su evidencia individual del checklist (EVD-4-03 a EVD-4-11). Fluyen al comentario del PR y al issue "Evidencias DevSecOps".
- **Flujo `pentest.yml`**: caja negra en vivo (Nmap acotado, TLS, superficie sin token, ZAP baseline pasivo) y **Prowler**, con rol de AWS de **solo lectura** por OIDC, solo desde `main`. Acotado a la política de pentest de AWS (sin inundación, Cognito fuera, WAF apagado). Tapa cuenta/ARN/correos y publica en el issue "Evidencias Pentest". Corre tras cada despliegue y a mano.
- **Rol `qwallet-gha-pentest`** en el **bootstrap** (no en Terraform: el rol de despliegue tiene Deny sobre `iam:*` en `role/qwallet-gha-*`). Solo lectura: SecurityAudit + ViewOnlyAccess.
- **Figura del perímetro** `docs/evidencias/EVD-4-14_perimetro.{svg,png}`: única puerta expuesta = HTTPS 443 (API Gateway, solo TLS 1.3); el resto privado.
- **Word** `docs/entregas/Final_Secciones_3-1_3-2_3-3_3-6_Pentest.docx` (11 págs., Tablas 38–41, Figura 9; Arial 12 / 1.5, render revisado).
- **Borrado de `services/hola`** (imagen provisional, ya no se usa). Respaldo en la rama `respaldo/services-hola`; se quitaron sus exclusiones en `devsecops.yml` e `infra.yml`.

## Lo que Daniel hace a mano (bloque 4)
1. Revisar y dar **Merge al PR** del bloque 4.
2. **Después del merge, en AWS CloudShell** (us-east-1, bash), re-correr el bootstrap para crear el rol de pentest:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/dbarrios95/q-wallet/main/infra/bootstrap/bootstrap.sh | bash
   ```
   Resultado esperado: entre otras líneas, "== 6. Rol de pentest (solo lectura, rama main)" y "qwallet-gha-pentest: creado". No borra nada; es idempotente.
3. En GitHub, pestaña Actions → flujo **pentest** → **Run workflow** (rama main) para generar EVD-4-01 (perímetro/Nmap), EVD-4-02 (ZAP) y EVD-3-09 (Prowler). Quedan en el issue "Evidencias Pentest". (También corre solo tras cada despliegue.)

## Antes (bloques 1 a 3, detalle en BITÁCORA)
- Cuenta AWS de Daniel (`qwallet-umg`, us-east-1, Free plan, US$100 de crédito). Bootstrap OIDC hecho; MFA raíz y presupuesto de US$5 confirmados. Toda la arquitectura desplegada y verificada (EVD-3-11, 3-12, 3-13, 5-04 en el issue "Evidencias AWS"). Código real de las 5 Lambdas en producción (PR #36 merge).
- Word de la Entrega 2: `docs/entregas/Entrega2_Seccion_4_Arquitectura_Controles.docx` (4.1, 4.2, 4.5). Word del bloque 3: `docs/entregas/Final_Secciones_3-4_3-5_4-3_4-4_4-6_DevSecOps.docx`. Presentación del 7-nov en Claude Slides (privada).

## Decisiones tomadas por Daniel (30-oct-2026, bloque 4)
- Caja negra en vivo **acotada** (Nmap + TLS + ZAP baseline, sin WAF; el WAF se prueba en el bloque 5).
- Casos de abuso de **dispositivo** (CA-07 tokens, CA-08 pinning/MITM, CA-10 Frida/root, CA-11 secretos del APK) y la integración app–API → **bloque 5**.
- **Prowler sí** (rol de solo lectura por OIDC).

## Decisiones pendientes (para el bloque 5)
- SIEM: Wazuh necesita 4 GB+ de RAM y no cabe en US$5; opción CloudWatch + alarmas + CloudTrail.
- Pruebas en el teléfono (Frida, freeRASP): emulador en la computadora de Daniel o intento en GitHub Actions.
- Al ensamblar el Word final: revisar `w:tblLayout` duplicado del Word de la Entrega 2 con el validador; integrar EVD-4-01/4-02/3-09 (salida de pentest.yml) a la sección 3.1 y 3.6.

## Recursos AWS
Cuenta de Daniel, us-east-1: toda la arquitectura desplegada, WAF apagado. Lambdas con el código real (post PR #36). Gasto esperado ~US$1 al mes (llave KMS); el WAF ~US$8 al mes solo encendido. El pentest en vivo (Nmap/TLS/ZAP/Prowler) es de solo lectura y cuesta centavos.
