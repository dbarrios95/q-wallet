# Entrega 2 — Presentación (sábado 14-nov-2026)

> Formato pedido: 5 minutos, cámara abierta, resumen ejecutivo, sin generalidades.
> Presentación: Claude Slides "Q-Wallet — Entrega 2 (Fase 2)" en claude.ai (privada; se descarga como PDF o PowerPoint desde el menú de la presentación). No vive en el repo.
> Todas las cifras salen del Word `Entrega2_Seccion_4_Arquitectura_Controles.docx` (Tablas 24 a 29) y del Terraform de `/infra`.

## Diapositivas y tiempo

| # | Diapositiva | Qué pide el enunciado (Fase 2) | De dónde sale | Tiempo |
|---|---|---|---|---|
| 1 | Portada y resumen ejecutivo: Terraform, OIDC, Checkov 282 / 0 | — | 4.1, 4.5 | ~50 s |
| 2 | Flujo de datos en 9 pasos (Figura 7, EVD-3-08) | Diagrama: flujo cliente → base de datos, API Gateway, identidad, WAF, almacenamiento cifrado | 4.1.1, Tabla 24 | ~70 s |
| 3 | Zero Trust y matriz de menor privilegio (8 tablas × 5 roles) | Menor privilegio en roles IAM | 4.1.2, 4.2.1, Tabla 26 | ~70 s |
| 4 | Cifrado: AES-256 en reposo, TLS 1.3 en tránsito | Estrategia de cifrado (AES-256 en BD, TLS 1.3 en tránsito) | 4.2.2, Tabla 27 | ~60 s |
| 5 | Cómo lo comprobamos: resultados | — | 4.2.3, 4.5, Tablas 28 y 29; EVD-3-11, 3-12, 5-04, 4-03, 4-04, 4-08 | ~70 s |

Total: ~5 min 20 s. Si hay que recortar, se acorta la diapositiva 2 (decir solo los cuatro grupos de pasos).

## Cifras usadas (verificadas contra el Word)

- Checkov 3.3.22: 282 pasan, 0 fallan, 39 omitidas con motivo (Tabla 29).
- 18 rutas con authorizer de Cognito; token de acceso de 15 min; throttling 10/s, ráfaga 20; WAF 100 solicitudes por IP en 5 min (Tabla 24).
- 8 tablas DynamoDB, 5 roles de Lambda; L/E de la matriz = Get/Query (lee) y Put/Update/Delete/ConditionCheck (escribe), según la Tabla 26.
- Llave `alias/qwallet-datos`, SYMMETRIC_DEFAULT (AES-256-GCM), rotación 365 días; `SecurityPolicy_TLS13_1_3_2025_09` en modo STRICT; minSdk 29 (Tabla 27).
- 14 requisitos (Tabla 28): 11 cumplidos en la infraestructura (REQ-02, 03, 06, 07, 08, 09, 10, 11, 12, 13, 14) y, desde los bloques 3 a 5, los 3 del código también cumplidos y probados: REQ-01 pinning (MITM rechazado, EVD-4-08, tras HAL-13), REQ-04 PIN (bloqueo al 5.º intento con 423, CA-02, EVD-4-04) y REQ-05 dueño del recurso (404/403, CA-01, EVD-4-03).
- Pruebas del despliegue: EVD-3-11, 3-12 y 5-04 pasaron (ejecución 41094572066, ver BITÁCORA).

## Antes de presentar

1. La diapositiva 5 ya dice los resultados (actualizada el 10-nov-2026, bloque 6).
2. Ensayar con cronómetro una vez. Notas del orador en cada diapositiva.
3. Descargar como PDF de respaldo por si falla la conexión (menú de la presentación › Exportar).
