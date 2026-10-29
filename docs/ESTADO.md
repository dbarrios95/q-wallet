# ESTADO — Q-Wallet

> Punto de arranque de cada chat. Se reescribe al cerrar cada bloque. Máximo una página.

**Actualizado:** 28-oct-2026 · **Hoy toca:** bloque 1

## Fechas
| Hito | Fecha | Fase del enunciado |
|---|---|---|
| Entrega 1 | 17-oct-2026 ✔ | Fase 1 |
| **Entrega 2** (presentación de 5 min, cámara abierta, resumen ejecutivo, sin generalidades) | **sáb 7-nov-2026** | Fase 2 |
| Entrega final | sáb 28-nov-2026 `[VERIFICAR]` con el catedrático | Fases 3 a 6 + informe completo |

## Bloques
| # | Bloque | Fases | Secciones del informe | Estado |
|---|---|---|---|---|
| 1 | Terraform de toda la arquitectura + despliegue automático con OIDC + 4.1 y 4.2 del Word | 2 y 5 | 4.1, 4.2, 4.5 | ☐ Siguiente |
| 2 | Presentación del 7-nov (5 diapositivas) | 2 | — | ☐ |
| 3 | Lambdas con código seguro + SAST/SCA en el flujo automático + minSdk 29 | 3 | 3.4, 3.5, 4.3, 4.4, 4.6 | ☐ |
| 4 | Pentest caja negra y gris, OWASP API Top 10, casos de abuso, perímetro | 4 | 3.1, 3.2, 3.3, 3.6 | ☐ |
| 5 | WAF, RASP, SIEM, alertas, tratamiento, mapa de calor "después" | 6 | 5.1 a 5.6 | ☐ |
| 6 | Word final, dictamen, presentación final | Todas | 0, 6 | ☐ |

## Decisiones tomadas (28-oct-2026)
- Daniel lleva el resto del proyecto solo. Claude hace ramas, commits y PR; Daniel da clic en "Merge". Ver `CLAUDE.md`.
- **Regla de borrado:** Claude pregunta y justifica antes de borrar, y respalda primero (`CLAUDE.md`).
- **Despliegue automático** desde GitHub Actions a AWS con OIDC (sin llaves guardadas). Daniel hace una sola vez el paso de CloudShell.
- **minSdk 24 → 29 y TLS solo 1.3** (`SecurityPolicy_TLS13_1_3_2025_09` en el API Gateway, modo STRICT). Cumple el enunciado tal cual, sin costo ni dominio propio. Reemplaza `SecurityPolicy_TLS13_1_2_2021_06` de CTRL-08. El minSdk se cambia en el bloque 3 (`expo-build-properties`).
- **Fase 2 va en 4.1** (rediseño arquitectónico cloud seguro: diagrama con el flujo numerado y Zero Trust) **y 4.2** (controles: menor privilegio IAM, estrategia de cifrado AES-256/TLS 1.3, matriz de requisitos MASVS).

## Decisiones pendientes
- SIEM (bloque 5): Wazuh necesita 4 GB+ de RAM y no cabe en US$5. Opción a evaluar: CloudWatch + alarmas + CloudTrail Lake o similar, "integración conceptual o práctica" según el enunciado.
- Pruebas en el teléfono (Frida, freeRASP): emulador en la computadora de Daniel o intento en GitHub Actions.

## Lo único que Daniel hace a mano
- Una vez (bloque 1): pegar en AWS CloudShell el comando que crea el rol OIDC y el bucket del estado de Terraform.
- Confirmar en la consola que el plan gratuito permite AWS WAF y ECR (pendiente desde oct).
- Clic en "Merge" en cada PR. Capturas de consola solo donde se pidan.

## Recursos AWS
Ninguno desplegado. Gasto US$0. Región us-east-1.
