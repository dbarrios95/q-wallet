# ESTADO — Q-Wallet

> Punto de arranque de cada chat. Se reescribe al cerrar cada bloque. Máximo una página.

**Actualizado:** 10-nov-2026 · **Hoy toca:** revisión de Daniel y presentaciones (los 7 bloques están terminados)

## Fechas
| Hito | Fecha | Fase del enunciado |
|---|---|---|
| Entrega 1 | 17-oct-2026 ✔ | Fase 1 |
| Entrega 2: Word de la sección 4 ✔ + **presentación de 5 min, cámara abierta** | **sáb 14-nov-2026** | Fase 2 |
| **Entrega final**: informe completo + presentación final (10 min) | **sáb 28-nov-2026** | Fases 1 a 6 |

## Bloques
| # | Bloque | Secciones | Estado |
|---|---|---|---|
| 1 a 5 | Terraform, presentación E2, Lambdas, pentest, operación | 3, 4, 5 | ☑ |
| 6 | Informe final, dictamen, presentación final | 0 a 6 | ☑ |
| 7 | Login real con Cognito, CA-07, HAL-16 y ajustes del informe | 3.2, 4.3, 5.2, 5.5, 5.6, 6 | ☑ PR #63 |

## Qué dejó el bloque 7
- **App:** inicio de sesión real con el login administrado de Cognito (código de autorización + PKCE S256, MFA TOTP). Canje y renovación de tokens por XHR con pinning (los pines también cubren el dominio de Cognito, verificado contra la cadena real). Access token solo en memoria; refresh token cifrado con Keystore (SecureStore), abierto con biometría o con el bloqueo del teléfono; revocación al cerrar sesión. Sin sesión simulada ni PIN falso. Código en `mobile/src/seguridad/sesion.ts`.
- **CA-07 con token real** (EVD-7-01 a 7-04, `movil.yml`): login automático en el emulador con el usuario de prueba, 0 tokens legibles con root, 0 en logcat, desbloqueo con PIN y revocación HTTP 200. Usa una copia del APK con freeRASP en modo registro (`EXPO_PUBLIC_QWALLET_APK_PRUEBA=ca07`, nunca se publica).
- **HAL-16 cerrado** (EVD-7-05, `saturacion.yml`): sin token, 0 × 429 en 2 540 solicitudes porque el authorizer rechaza antes del throttling; con token real, 244 × 429 de 600. **HAL-17 nuevo (abierto):** ráfagas autenticadas simultáneas reciben 500 porque el límite de Lambda de la cuenta es 10 (Daniel lo verificó en CloudShell) y la ráfaga de API Gateway es 20.
- **Riesgo:** AME-02 y AME-10 pasan a "prueba": residual 580 → 202 (−65 %), 0 críticos, 1 alto, 25 medios, 15 bajos. OE3: 12 de 13. 17 hallazgos.
- **Informe** `Informe_Final_QWallet.docx` (166 págs., 60 tablas, 21 figuras): sin «simulado» ni «ficticio», «antes de pasar a producción», nada «pendiente»; Figura 9 sin la pantalla de login; Figura 10 nueva (login real); dictamen con tres condiciones: WAF permanente, HAL-17 y Expo SDK 58. Cadena: `bloque5_residual.py figura` → `bloque5_word.py` → `bloque6_word.py` → `bloque6_capturas.py` (cada uno con `entrega1_estilos.py`) → `final_ensamblar.py` → `bloque7_ajustes.py` → `entrega1_estilos.py` → `entrega1_indice.py`.
- **Presentación final** (Claude Slides) actualizada: 580 → 202, 12 de 13, 17 hallazgos, nuevas condiciones y números de figura.

## Lo que le toca a Daniel
1. Revisar y hacer merge del PR #63. No toca Terraform: no hay despliegue que aprobar.
2. Abrir el Word final, clic derecho en el índice → Actualizar campo → Toda la tabla, y leerlo completo.
3. Resolver los dos `[VERIFICAR]` que quedan: costo de CloudWatch en la factura de noviembre (sección 5.3) y origen de `files/tcb` (Tabla 45; ya se sabe que existe antes de iniciar sesión, no es de la sesión).
4. Capturas que Daniel va a tomar (tapar cuenta, ARN y correo). GitHub: (1) devsecops en verde en main; (2) comentario «DevSecOps» del PR #60; (3) Security → Code scanning con 0 alertas; (4) resumen de ZAP en el issue «Evidencias Pentest»; (5) comentario «Revisión estática» del PR #60 con Checkov 282/0. AWS us-east-1: (6) Cognito MFA obligatorio TOTP; (7) API Gateway con TLS 1.3; (8) KMS `alias/qwallet-datos` con rotación; (9) DynamoDB cifrado con la CMK; (10) alarmas `qwallet-*`; (11) panel `qwallet-seguridad`. Van a 3.4, 3.5, 4.2, 4.5, 5.3 y 5.4 con `bloque6_capturas.py`.
5. Exportar cada presentación como PDF de respaldo y ensayar con cronómetro.

## Datos útiles
- Usuario de prueba de Cognito: `ca07-202611102156@qwallet.example` (MFA TOTP), creado con `infra/scripts/usuario_prueba.py`; sus datos están en los secretos `QWALLET_PRUEBA_*` de GitHub. Dominio reservado: no recibe correo ni tiene datos.
- Los flujos `movil.yml` y `saturacion.yml` se pueden relanzar a mano desde Actions (Run workflow).

## Roadmap (sección 6.3)
Expo SDK 58 (vence la excepción el 31-ene-2027); HAL-17 (límite de Lambda y ráfaga; repetir CA-03 en la búsqueda); conectar las pantallas de saldo, movimientos, presupuestos y transferencias con la API; biometría en teléfono físico; WAF permanente; dominio propio (HAL-09); Play App Signing; IAM Identity Center en vez de root; Wazuh.

## Recursos AWS
Cuenta de Daniel, us-east-1: toda la arquitectura, SIEM y alarmas desplegados; WAF apagado. Gasto esperado ~US$2–3 al mes [VERIFICAR en la factura]; el WAF ~US$9 al mes solo encendido. Las pruebas del bloque 7 sumaron unas 3 300 solicitudes a la API y ~900 invocaciones de Lambda (costo despreciable). Antes de cerrar la cuenta o borrar recursos después del curso: preguntar y respaldar (regla de borrado).
