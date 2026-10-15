# EQUIPO — reglas, tareas y exposición (Entrega 1, sábado 17-oct-2026)

> Copia en el repo de `claude/PLAN_EQUIPO.md` del proyecto de claude.ai (15-oct-2026). Si cambia, se actualiza aquí y se anota en BITÁCORA.

Acordado el 14-oct-2026 y compartido por WhatsApp (PDF "Q-Wallet_plan_del_equipo.pdf").

## Reglas
1. Un dueño por archivo: el Word del informe, CONTEXTO, BITÁCORA y ENTREGA_1 solo los cambia Daniel (con Claude).
2. Nadie edita, todos proponen: observaciones con formato "Página o tabla | Qué está mal | Texto propuesto". Daniel las aplica.
3. Las IA de Aroldo y Katherine no actualizan CONTEXTO ni BITÁCORA aunque CLAUDE.md o GEMINI.md lo pidan, y no hacen commits.
4. Nada directo a main: rama propia, PR y Daniel revisa.
5. Cero datos inventados: lo no confirmado va como [VERIFICAR].

## Tareas hasta el sábado
| Integrante | Herramienta | Tareas | Plazo |
|---|---|---|---|
| Daniel (I1, Lead Security Architect) | Claude | Corregir el Word (texto de 1.5 "Cuatro requieren rediseño" vs. Tabla 11; notas de las Tablas 7, 9 y 10 que citan "CONTEXTO, sección x"; 3 [VERIFICAR]); presentación (JM-98-2025, EVD-2-07 en P-4, CTRL-23); integrar observaciones; exportar PDF y entregar | Vie 16 |
| Katherine (I2, DevSecOps) | Gemini | Revisar 1.5, 2.1 y 2.2 y mandar lista; crear cuenta AWS (MFA en raíz, presupuesto US$5, sin recursos) y captura EVD-1-03 con fecha; preparar su exposición | Jue 15 noche |
| Aroldo "Paco" (I3, Pentester / Analista de Riesgos) | Claude Code | Revisión independiente del informe completo contra la rúbrica (sin editar); verificar fuentes oficiales: JM-98-2025, Global Findex pagos digitales (23 %), iniciativa 6464; preparar su exposición | Jue 15 noche |

## Quién expone qué
| Integrante | Secciones |
|---|---|
| Daniel | 0, 1.1 a 1.4 y cierre |
| Katherine | 1.5, 2.1 y 2.2 |
| Aroldo | 2.3, 2.4 y 2.5 |

## Después del sábado (propuesta): un carril por carpeta
| Integrante | Carpeta | Trabajo |
|---|---|---|
| Katherine | /infra, .github/workflows | Terraform (estado en S3 con bloqueo) y pipeline SAST/SCA/IaC |
| Aroldo | /services, docs/evidencias | Microservicios y pentest (ZAP, Burp, MobSF, casos de abuso) |
| Daniel | /mobile, docs | App Android, informe, integración y revisión de PR |
