# ESTADO — Q-Wallet

> Punto de arranque de cada chat. Se reescribe al cerrar cada bloque. Máximo una página.

**Actualizado:** 27-nov-2026 (tarde) · **Hoy toca:** instalar el APK nuevo en el teléfono, PDF y ensayo de la demo

## Fechas
| Hito | Fecha | Fase del enunciado |
|---|---|---|
| Entrega 1 | 17-oct-2026 ✔ | Fase 1 |
| Entrega 2 | 14-nov-2026 ✔ | Fase 2 |
| **Entrega final**: informe completo + presentación (recorrido por la app, ~10 min) | **sáb 28-nov-2026** | Fases 1 a 6 |

## Bloques
| # | Bloque | Estado |
|---|---|---|
| 1 a 7 | Terraform, presentación E2, Lambdas, pentest, operación, informe final, login real | ☑ |
| Cierre | Informe listo para entregar (172 págs., capturas en el Anexo D) y guion de la demo | ☑ |
| Demo | App en teléfono físico: arreglos de login, margen inferior y Acciones rápidas (PR `fix/demo-movil`) | ☑ |

## Qué dejó el cierre (25-nov)
- **Informe** `Informe_Final_QWallet.docx` (166 págs.): auditado contra CONTEXTO, sección 9 y APA 7 (Arial, 1.5, 0/8 pt y 0/0 pt en tablas, tablas y figuras en orden, citas y referencias cruzadas sin faltantes). `scripts/final_entrega.py` quitó los 2 [VERIFICAR], cambió «sin demostración en vivo» (OE5, Tabla 5, 1.5), puso 6.6 Referencias en página nueva y llevó las Tablas 53 y 59 a 9 pt. Cadena completa: la del bloque 7 → `final_entrega.py` → `entrega1_estilos.py` → `entrega1_indice.py`.
- **Presentación:** ahora es un recorrido por la app, pantalla por pantalla, sin transferencias ni ataques en vivo. Guion repartido entre los tres en `docs/entregas/Final_Guion_Demo.md`. Las diapositivas de Claude Slides quedan de respaldo.

## App para la demo (27-nov, tarde)
- Se presenta desde el **teléfono de Daniel (sin root) con el APK release** del flujo `movil` (artefacto `movil-apk`), no con Metro. En emulador ese APK se bloquea (freeRASP); ahí iría `movil-apk-prueba`.
- Arreglos del PR `fix/demo-movil`: la pantalla de regreso del login ya no se queda cargando; la barra de pestañas, Bienvenida, Desbloqueo y la ventana del PIN respetan los botones del teléfono; Acciones rápidas en una tarjeta; «Cerrar sesión» cierra también la sesión de Cognito en el navegador (antes se podía volver a entrar sin contraseña ni MFA); la protección contra capturas queda solo en Desbloqueo, Transferir y Perfil mientras están a la vista (antes, al proyectar, toda la app salía en negro).
- Para Metro en la laptop: `npm ci --legacy-peer-deps` en `mobile/` (sin eso falta `buffer`).
- El PIN de Transferir no se valida (pantalla de ejemplo): no hacer transferencias en la demo.

## Lo que le toca a Daniel
1. Opcional: recapturar CAP-04 (ZAP desplegado), CAP-07 (API → API settings, política TLS 1.3) y CAP-08 (pestaña Key rotation) y correr `final_capturas.py` desde el Word de `final_entrega.py`. Revisar las 11 alertas de Dependabot (Security → Dependabot) antes de la defensa.
2. Merge del PR #68 y del PR `fix/demo-movil`; instalar el `app-release.apk` de la corrida de `movil` de ese PR (desinstalar antes la versión anterior si la firma no coincide).
3. Abrir el Word final, clic derecho en el índice → Actualizar campo → Toda la tabla, leerlo y exportar el PDF.
4. Mandar al equipo el Word y el guion; ensayar una vez con cronómetro en el teléfono, con la sesión ya iniciada.

## Datos útiles
- Usuario de prueba de Cognito: `ca07-202611102156@qwallet.example` (MFA TOTP); datos en los secretos `QWALLET_PRUEBA_*` de GitHub. Para la demo, Daniel tiene un segundo usuario `ca07-…` (27-nov) con sus datos fuera del repo.
- Al proyectar, solo Desbloqueo, Transferir y Perfil salen en negro (FLAG_SECURE): se usa en vivo como demostración, con la Figura 11 de respaldo.

## Roadmap (sección 6.3)
Expo SDK 58 (antes del 31-ene-2027); HAL-17 (límite de Lambda y ráfaga; repetir CA-03 en la búsqueda); conectar saldo, movimientos, presupuestos y transferencias con la API; biometría en teléfono físico; WAF permanente; dominio propio (HAL-09); Play App Signing; IAM Identity Center en vez de root; Wazuh.

## Recursos AWS
Cuenta de Daniel, us-east-1: toda la arquitectura, SIEM y alarmas desplegados; WAF apagado. Gasto estimado ~US$2–3 al mes; el WAF ~US$9 al mes solo encendido. Antes de cerrar la cuenta o borrar recursos después del curso: preguntar y respaldar (regla de borrado).
