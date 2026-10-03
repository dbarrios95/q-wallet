# CHECKLIST DE EVIDENCIAS

Como no hay demo en vivo, toda afirmación técnica del informe necesita una evidencia.

## Reglas de captura
- Nombre de archivo: `EVD-<fase>-<nn>_<desc>.png`.
- Debe verse la fecha/hora cuando sea posible.
- Antes de capturar, ocultar: ID de cuenta AWS, correos y tokens.
- Para ataques, grabar además un video corto (OBS) por caso: sirve para la presentación.

## Entrega 1

| ✔ | EVD | Qué debe verse | Herramienta | Sección |
|---|---|---|---|---|
| ☐ | EVD-1-01 | Diagrama de arquitectura con controles y fronteras de confianza | draw.io | 1.5 |
| ☐ | EVD-1-02 | Repositorio con estructura de carpetas | GitHub | 1.5 |
| ☐ | EVD-1-03 | Cuenta AWS: MFA en root + presupuesto con alerta | AWS Console | 1.5 / capa 7 |
| ☐ | EVD-2-01 | DFD nivel 0 | Threat Dragon | 2.3 |
| ☐ | EVD-2-02 | DFD nivel 1 con fronteras TB1–TB6 | Threat Dragon | 2.3 |
| ☐ | EVD-2-03 | Amenazas STRIDE sobre elementos del DFD | Threat Dragon | 2.3 |
| ☐ | EVD-2-04 | Reporte PDF exportado de Threat Dragon | Threat Dragon | Anexo |
| ☐ | EVD-2-05 | Heatmap de riesgo inicial ("antes") | Excel | 2.5 |
| ☐ | EVD-2-06 | (Opcional) Árbol de ataque | draw.io | Anexo |

## Entrega final

### Arquitectura y DevSecOps (sección 3 y 4.6)

| ✔ | EVD | Qué debe verse |
|---|---|---|
| ☐ | EVD-3-01 | Pipeline de GitHub Actions con todos los jobs |
| ☐ | EVD-3-02 | Semgrep: resultado del escaneo |
| ☐ | EVD-3-03 | CodeQL / SonarQube Cloud: dashboard (quality gate) |
| ☐ | EVD-3-04 | Dependency-Check / Snyk: reporte SCA |
| ☐ | EVD-3-05 | Trivy: imagen de contenedor |
| ☐ | EVD-3-06 | Checkov sobre Terraform y Dockerfile |
| ☐ | EVD-3-07 | MobSF: reporte del APK de release |
| ☐ | EVD-3-08 | Diagrama de arquitectura de seguridad (API Gateway, IAM, Cognito, WAF, KMS) |
| ☐ | EVD-3-09 | gitleaks + Prowler: resultado |
| ☐ | EVD-3-10 | Pipeline bloqueando un PR con una dependencia vulnerable (demostración del gate) |

### Ciberdefensa (sección 3)

| ✔ | EVD | Qué debe verse |
|---|---|---|
| ☐ | EVD-4-01 | Nmap / mapeo de superficie expuesta |
| ☐ | EVD-4-02 | ZAP: escaneo de API con OpenAPI importado |
| ☐ | EVD-4-03 | CA-01 BOLA bloqueado (403/404) |
| ☐ | EVD-4-04 | CA-02 fuerza bruta del PIN bloqueada |
| ☐ | EVD-4-05 | CA-03 datos enmascarados + CA-04 mass assignment rechazado |
| ☐ | EVD-4-06 | CA-05 paginación limitada |
| ☐ | EVD-4-07 | CA-06 concurrencia: una sola transferencia aplicada |
| ☐ | EVD-4-08 | CA-07 tokens no extraíbles + CA-08 MITM rechazado por pinning |
| ☐ | EVD-4-09 | CA-09 `/admin` rechazado para cliente |
| ☐ | EVD-4-10 | CA-10 freeRASP detectando Frida/root |
| ☐ | EVD-4-11 | CA-11 APK sin secretos + CA-13 token alterado rechazado |

### Ciberseguridad y operación (secciones 4 y 5)

| ✔ | EVD | Qué debe verse |
|---|---|---|
| ☐ | EVD-5-01 | AWS WAF: reglas configuradas |
| ☐ | EVD-5-02 | WAF bloqueando un ataque (muestras de solicitudes) |
| ☐ | EVD-5-03 | freeRASP detectando root/hook |
| ☐ | EVD-5-04 | KMS CMK y DynamoDB cifrado |
| ☐ | EVD-5-05 | Wazuh: ingesta de CloudTrail |
| ☐ | EVD-5-06 | Wazuh: alerta por fuerza bruta / BOLA |
| ☐ | EVD-5-07 | Dashboard de seguridad |
| ☐ | EVD-5-08 | Re-test de cada HAL real (una por hallazgo) |
| ☐ | EVD-5-09 | Heatmap residual ("después") |
