# ESTADO — Q-Wallet

> Punto de arranque de cada chat. Se reescribe al cerrar cada bloque. Máximo una página.

**Actualizado:** 10-nov-2026 · **Hoy toca:** bloque 7 (ajustes del informe final pedidos por Daniel el 10-nov; detalle abajo)

## Fechas
| Hito | Fecha | Fase del enunciado |
|---|---|---|
| Entrega 1 | 17-oct-2026 ✔ | Fase 1 |
| Entrega 2: Word de la sección 4 ✔ + **presentación de 5 min, cámara abierta** | **sáb 14-nov-2026** | Fase 2 |
| **Entrega final**: informe completo + presentación final (10 min) | **sáb 28-nov-2026** | Fases 1 a 6 |

## Bloques
| # | Bloque | Secciones | Estado |
|---|---|---|---|
| 1 | Terraform + despliegue OIDC | 4.1, 4.2, 4.5 | ☑ |
| 2 | Presentación de la Entrega 2 | — | ☑ (diapositiva 5 con resultados, 10-nov) |
| 3 | Lambdas, SAST/SCA, minSdk 29 | 3.4, 3.5, 4.3, 4.4, 4.6 | ☑ |
| 4 | Pentest, OWASP API, casos de abuso | 3.1, 3.2, 3.3, 3.6 | ☑ |
| 5 | WAF, RASP, SIEM, alertas, tratamiento | 5.1 a 5.6 | ☑ |
| 6 | Informe final, dictamen, presentación final | 0 a 6 | ☑ PR #60 y PR de cierre (este) |

## Qué dejó el bloque 6
- **Informe final** `docs/entregas/Informe_Final_QWallet.docx`: 161 págs., secciones 0 a 6 en el orden del enunciado, 60 tablas y 20 figuras renumeradas (con capturas de la app y Anexo D), 35 referencias APA 7 en 6.6, índice general. Se rearma con: `bloque6_word.py` y `bloque6_capturas.py` (cada uno con `entrega1_estilos.py`) → `final_ensamblar.py` → `entrega1_estilos.py` → `entrega1_indice.py`.
- **Dictamen** (sección 6): favorable para la versión evaluada, con tres condiciones antes de dinero real: WAF permanente, inicio de sesión real con CA-07 y Expo SDK 58 antes del 31-ene-2027. OE1, OE2, OE4 y OE5 cumplidos; OE3 parcial (11 de 13).
- **Presentaciones** en Claude Slides: "Q-Wallet — Entrega 2 (Fase 2)" actualizada y "Q-Wallet — Presentación final" (10 diapositivas, ~10 min). Guiones en `docs/entregas/`.
- **Capturas**: pantallas de la app y prueba de FLAG_SECURE en el emulador (EVD-6-01 a 6-07, `docs/evidencias/bloque6/`); AME-09 ahora verificada con prueba.
- **PR #60**: alarma `aws-no-autorizado` sin el falso positivo del rol de plan; excepciones SCA renovadas al 31-ene-2027; Dependabot #53 a #57 aplicados juntos.

## Bloque 7: ajustes pedidos por Daniel (10-nov-2026)
1. **Redacción sin «simulado» ni «ficticio»**: presentar a Q-Wallet, S.A. como empresa y producto reales (el catedrático ya lo sabe). Son unas 15 frases, desde 1.1 hasta el dictamen; «antes de manejar dinero real» pasa a «antes de pasar a producción». Se ubican con `simulad|ficti|pendient|aún no|todavía no|dinero real` en `Informe_Final_QWallet.docx`. Quitar la pantalla de login de la Figura 9: muestra el botón «Entrar con sesión simulada (Dev)». No se editan imágenes.
2. **Nada «pendiente» en la redacción**: usar siguiente versión, riesgo aceptado o roadmap. **Límite acordado:** lo que no se hizo no se reporta como hecho (CA-07, CTRL-07 Keystore y biometría en la app, HAL-16).
3. **Decisión pendiente de Daniel:** implementar de verdad (a) el inicio de sesión con Cognito (PKCE y MFA) y los tokens en Keystore, con CA-07 repetido en el emulador (unos 2 o 3 días), y (b) una prueba de saturación más larga para HAL-16. Si dice que no, queda como roadmap y riesgo aceptado.
4. **Capturas que Daniel va a tomar** (tapar cuenta, ARN y correo). GitHub: (1) ejecución de devsecops en verde en main; (2) comentario «DevSecOps» del PR #60; (3) Security → Code scanning con 0 alertas; (4) resumen de ZAP en el issue «Evidencias Pentest»; (5) comentario «Revisión estática» del PR #60 con Checkov 282/0. AWS us-east-1: (6) Cognito MFA obligatorio TOTP; (7) API Gateway con TLS 1.3; (8) KMS `alias/qwallet-datos` con rotación; (9) DynamoDB cifrado con la CMK; (10) CloudWatch alarmas `qwallet-*`; (11) panel `qwallet-seguridad`. Van a 3.4, 3.5, 4.2, 4.5, 5.3 y 5.4 con `bloque6_capturas.py`, como las de la app (EVD-6-xx).

## Lo que le toca a Daniel
1. Merge del PR #60 y aprobar el despliegue en `dev` (el plan del despliegue debe salir sin destrucciones ni reemplazos). Después cerrar los PR #53 a #57 si Dependabot no los cierra solo.
2. Merge del PR de cierre del bloque 6.
3. Abrir el Word final en Word, clic derecho en el índice → Actualizar campo → Toda la tabla, y leerlo completo.
4. Resolver los dos `[VERIFICAR]` que quedan en el Word: costo de CloudWatch en la factura de noviembre (sección 5.3) y origen de `files/tcb` (Tabla 45). Si no se pueden verificar, se dejan marcados.
5. Exportar cada presentación como PDF de respaldo y ensayar con cronómetro.

## Pendientes que pasan al roadmap (sección 6.3)
Expo SDK 58 (vence la excepción el 31-ene-2027); HAL-16 (prueba de saturación más larga); inicio de sesión con Cognito en la app; WAF permanente; dominio propio (HAL-09); Play App Signing; IAM Identity Center en vez de root; Wazuh.

## Recursos AWS
Cuenta de Daniel, us-east-1: toda la arquitectura, SIEM y alarmas desplegados; WAF apagado. Gasto esperado ~US$2–3 al mes [VERIFICAR en la factura]; el WAF ~US$9 al mes solo encendido. Antes de cerrar la cuenta o borrar recursos después del curso: preguntar y respaldar (regla de borrado).
