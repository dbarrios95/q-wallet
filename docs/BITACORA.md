# BITÁCORA DEL PROYECTO — Q-Wallet

> Entradas nuevas **arriba**. Una por sesión de trabajo.
> El resumen vigente está en `ESTADO.md` (arranque) y `CONTEXTO.md` sección 11; aquí queda el historial.

### 2026-10-29 — Daniel — Claude (claude.ai), bloque 1
- Fase / sección del informe: Fase 2 (diseño arquitectónico cloud) y parte de la Fase 5 (revisión del IaC). Secciones 4.1, 4.2 y 4.5.
- Qué se hizo:
  - Terraform de toda la arquitectura en `/infra` (Terraform 1.16.5, AWS 6.67.0, random 3.9.1, con `.terraform.lock.hcl`): llave KMS propia, 8 tablas DynamoDB, Cognito (ESSENTIALS, MFA TOTP obligatorio, cliente público con PKCE, tokens de 15 min, rotación del refresh token, login administrado v2), API Gateway REST regional con `SecurityPolicy_TLS13_1_3_2025_09` y modo STRICT, authorizer de Cognito con alcance `qwallet/api` en las 18 rutas, respuestas de error genéricas, logs de acceso sin tokens, throttling 10/s y ráfaga 20, X-Ray; 5 Lambdas en contenedor (ECR, etiquetas inmutables) con un rol IAM por función y límite de permisos; CloudTrail multirregión cifrado; WAF apagable con la variable `WAF_HABILITADO`.
  - Bootstrap para CloudShell (`infra/bootstrap/bootstrap.sh` y `politicas/`): bucket del estado, proveedor OIDC, límite `qwallet-limite-permisos`, roles `qwallet-gha-plan` (solo lectura, PR) y `qwallet-gha-despliegue` (entorno `dev`). El rol de despliegue tiene denegaciones explícitas para borrar la llave, tablas, user pool, buckets, trail y repositorios, y para tocar los roles de GitHub.
  - Flujo `.github/workflows/infra.yml` y scripts `infra/scripts/revisar_plan.py` (detiene el despliegue si hay destrucciones o reemplazos no aprobados) y `verificar_aws.sh` (EVD-3-11, 3-12, 3-13, 5-04, sin número de cuenta).
  - Imagen provisional `services/hola` (responde 501), base `public.ecr.aws/lambda/nodejs:24` fijada por digest (obtenido en GitHub Actions el 29-oct).
  - Figura EVD-3-08 y Word de 4.1, 4.2 y 4.5 (13 págs., Arial 12, 1.5; anchos de tabla calculados para no partir palabras; renderizado y revisado completo).
  - Checkov 3.3.22: primera corrida 52 fallas; se corrigieron retención de logs (365 días), X-Ray y `create_before_destroy` en la API; las 39 restantes se omiten con motivo junto al recurso. Resultado: 282 pasan, 0 fallan. `terraform fmt` y `validate` en verde en GitHub Actions.
- Archivos creados o modificados: `infra/*`, `services/hola/*`, `.github/workflows/infra.yml`, `scripts/entrega2_diagrama_flujo.py`, `scripts/entrega2_seccion4.py`, `docs/entregas/Entrega2_Seccion_4_Arquitectura_Controles.docx`, `docs/evidencias/EVD-3-08_arquitectura_flujo_datos.svg/.png`, `docs/CONTEXTO.md` (secciones 3, 4 y 11), `docs/CHECKLIST_EVIDENCIAS.md`, `docs/ESTADO.md`, `docs/BITACORA.md`.
- Decisiones tomadas (y por qué):
  - Una tabla por tipo de dato (8) en lugar de una tabla única: permite el menor privilegio tabla por tabla y la prueba "svc-budgets no lee transferencias".
  - Sin VPC para las Lambdas: exigiría NAT Gateway (prohibido); segmentación por rol IAM.
  - ECR con AES-256 administrado por AWS (sin datos de clientes); estado de Terraform con SSE-KMS de AWS (`aws/s3`) para no pagar una segunda llave.
  - Entorno de GitHub `dev` (no "produccion"): es un entorno académico con dinero simulado.
  - El grupo `admins` se valida por ahora solo en el handler; la validación en el borde (CTRL-14) se resuelve en el bloque 3.
- Cambios de versión: ninguno (se agregó el proveedor `hashicorp/random` 3.9.1 y `actions/upload-artifact` v7.0.2, fijados).
- Evidencias generadas: EVD-3-08; EVD-3-06 parcial (comentario del PR #22). EVD-3-11, 3-12, 3-13 y 5-04 se generan en el primer despliegue.
- IDs nuevos: EVD-3-13. REQ-01 a REQ-14 (matriz de requisitos, Tabla 28).
- Problemas / bloqueos: desde la sesión de Claude no se pueden leer los logs ni los artefactos de Actions, ni crear entornos o secretos del repo: el flujo publica sus resultados como comentarios; el entorno `dev` y el secreto los crea Daniel. No hay Terraform local (se validó en Actions; el formato se aplicó con una herramienta de HCL compilada desde GitHub).
- Decisiones de Daniel al cierre (opción múltiple): (1) el merge basta como aprobación del despliegue, sin aprobación manual en `dev`; queda ajustar el texto del plan de RSK-32 en el Word final. (2) Regla de ciclo de vida en ECR: conservar las 5 imágenes más recientes por servicio (borrado automático aprobado por Daniel; respaldo no aplica: las imágenes se reconstruyen desde git). (3) Los títulos de la sección 4 y de 4.5 los pega Daniel en el chat.
- Enunciado (PDF), rúbrica (docx) e infografía subidos a `docs/enunciado/` con `README.md` (estructura del informe) y `ENUNCIADO.md` (texto). Con eso se corrigieron los títulos: "4. Mitigación y ciberseguridad" y "4.5 Hardening de infraestructura cloud". Decisión de Daniel: las entregas parciales no llevan portada ni índice (solo el informe final).
- Siguiente paso: Daniel hace los 5 pasos manuales de `ESTADO.md`; con el primer despliegue se completan las evidencias de 4.2. Después, bloque 2 (presentación).

### 2026-10-28 — Daniel — Claude (claude.ai)
- Fase / sección del informe: Organización para la Entrega 2 y la entrega final.
- Qué se hizo: el enunciado y la rúbrica confirman una entrega por fase; la Entrega 2 (7-nov) es la Fase 2. Plan del equipo en PDF (24-oct). Desde el 28-oct Daniel lleva el resto solo: nueva forma de trabajo por bloques, con Claude haciendo ramas, commits y PR.
- Archivos creados o modificados: `CLAUDE.md` (forma de trabajo y regla de borrado), `docs/ESTADO.md` (nuevo), `docs/CONTEXTO.md` (CTRL-08, capa 1, minSdk, secciones 10 y 11), `docs/BITACORA.md`.
- Decisiones tomadas:
  - Claude no borra nada sin preguntar y justificar; respalda primero (pedido de Daniel).
  - Despliegue automático desde GitHub Actions con OIDC.
  - minSdk 29 y TLS solo 1.3 (`SecurityPolicy_TLS13_1_3_2025_09`, modo STRICT): cumple el enunciado sin costo; Android 7 a 9 queda fuera, aceptable para el proyecto.
  - Fase 2 en las secciones 4.1 y 4.2 del informe.
  - Entrega final: 28-nov-2026 `[VERIFICAR]`.
- Cambios de versión: ninguno (minSdk se aplica en el bloque 3).
- Evidencias generadas: ninguna.
- IDs nuevos: EVD-3-11 (simulador IAM) y EVD-3-12 (prueba TLS 1.3), propuestos en el plan del equipo.
- Problemas / bloqueos: falta confirmar WAF y ECR en el plan gratuito.
- Siguiente paso: bloque 1 (Terraform + OIDC + 4.1 y 4.2).

## Plantilla
```
### AAAA-MM-DD — Integrante — Herramienta usada (Gemini / Claude / manual)
- Fase / sección del informe:
- Qué se hizo:
- Archivos creados o modificados:
- Decisiones tomadas (y por qué):
- Cambios de versión:
- Evidencias generadas (EVD-):
- IDs nuevos (ACT/AME/RSK/HAL/CTRL):
- Problemas / bloqueos:
- Siguiente paso:
```

---

### 2026-10-16 — Daniel — Claude (claude.ai)
- Fase / sección del informe: Entrega 1 — Word ajustado a la rúbrica (cambios aprobados por Daniel: "aplicá los cambios según tus sugerencias").
- Qué se hizo:
  - Script nuevo `scripts/entrega1_rubrica.py` (corre después de `entrega1_revision_paco.py`, antes de `entrega1_estilos.py`). Cambios: 6 títulos con la redacción del enunciado (en el título y en el índice); cita de 1.1 reordenada (Carrillo & Asociados, 2025 junto a la JM-98-2025 y AWS, s. f.-a junto a la JM-104-2021); marcador `[VERIFICAR]` del Findex quitado; AWS (s. f.-c) con "Recuperado el 16 de octubre de 2026" (página consultada ese día); Tablas 7–23 con letra de 10 pt (cortas) o 9 pt (largas) y anchos de columna recalculados para que ninguna palabra se parta; Tabla 12 en 8 pt con márgenes de celda de 40 dxa por lado.
  - `scripts/entrega1_estilos.py`: Arial en todo el documento e interlineado 1.5 fuera de tablas (0/8 pt); las viñetas con caracteres de Symbol conservan esa fuente.
  - `scripts/entrega1_indice.py`: reconoce el título "Índice general".
  - Word regenerado: `entrega1_rubrica.py` → `entrega1_estilos.py` → `entrega1_indice.py` sobre el Word del PR #19. Validador del skill de docx: sin errores. Render completo revisado: **78 páginas** (antes 67).
- Archivos creados o modificados: `docs/entregas/Entrega1_Informe_QWallet.docx`, `scripts/entrega1_rubrica.py` (nuevo), `scripts/entrega1_estilos.py`, `scripts/entrega1_indice.py`, `docs/CONTEXTO.md` (secciones 9 y 11), `docs/entregas/ENTREGA_1.md` (secciones 2, 4 y 7), `docs/BITACORA.md`.
- Decisiones tomadas (y por qué):
  - **Arial 12 e interlineado 1.5** en lugar de Times New Roman doble: lo exigen la rúbrica y el enunciado ("cumplimiento estricto del formato UMG").
  - Títulos con la redacción del enunciado, pero con mayúscula solo en la primera palabra, igual que el resto de títulos del informe. La numeración no cambia.
  - Tabla 12 en 8 pt: con 15 columnas obligatorias, a más de 8 pt las palabras más largas no caben en la página horizontal sin partirse. A 7.5 pt ahorraría 3 páginas.
- Hallazgos: la viñeta de 2.5.1 (carácter de Symbol) se veía como un cuadro vacío desde el PR #19, porque el script de estilos le había cambiado la fuente; corregido.
- Cambios de versión: ninguno.
- Evidencias generadas (EVD-): ninguna.
- IDs nuevos: ninguno.
- Problemas / bloqueos: ninguno.
- Siguiente paso: abrir el Word en Microsoft Word, actualizar el campo del índice (toda la tabla), revisar y exportar PDF; ensayar la presentación. Actualizar las instrucciones del proyecto de claude.ai, que todavía dicen Times New Roman y doble.

---

### 2026-10-15 — Daniel — Claude (claude.ai), segunda sesión
- Fase / sección del informe: Entrega 1 — presentación de avance (P-1 a P-6) y revisión del Word contra la rúbrica.
- Qué se hizo:
  - Se verificó que el PR #19 (`docs/entrega1-revision-paco`) estaba en `main`.
  - Presentación (Claude Slides "Q-Wallet — Entrega 1 (Avance)"): el deck era del 12-oct y estaba más atrasado de lo que decía ENTREGA_1 (27 activos, 22 controles, OE con otro texto, TLS como riesgo aceptado, RSK-01 transferido, sin diapositiva de normativas, letra Rubik/IBM Plex). Se reescribieron todas las diapositivas con las cifras del Word y del JSON, la paleta y la letra Inter de ENTREGA_1, sección 1. Pasa de 14 a **15 diapositivas** (nueva: 1.4 Normativas, con JM-98-2025). Orden por expositor según EQUIPO.md: Daniel (portada, 1.1–1.4, cronograma y cierre), Katherine (1.5 arquitectura, controles y reglas del pentest, metodología, 2.1–2.2), Aroldo (2.3–2.5). Cada diapositiva dice en el pie quién expone y tiene notas del orador.
  - Cambios pedidos: JM-98-2025 en lugar de JM-104-2021; Figura 1 nueva con el nodo IAM; CTRL-23 (23 controles); pentest solo sobre WAF, API Gateway y Lambda y DynamoDB, SSM, S3 e IAM por configuración; "14 categorías STRIDE sin amenaza separada"; P-4 con EVD-2-05 y EVD-2-07 (PNG sin título) lado a lado; tratamiento mitigar 39 · aceptar 2 (RSK-01 y RSK-31); TLS 1.3 deja de ser riesgo aceptado.
  - Revisión del Word contra la rúbrica (`RUBRICA_PROYECTO_FINAL.docx`, adjuntada por Daniel) y el enunciado: estructura Opción A completa; Tablas 1–23 y Figuras 1–6 en orden; índice igual al render (67 págs.); 24 referencias, todas citadas y ninguna sobrante; cifras iguales al JSON. **El Word no se modificó**: queda una lista de cambios pendiente de aprobación.
- Archivos creados o modificados: `docs/evidencias/EVD-1-03e_aws-mfa-raiz.png` (nuevo), `docs/entregas/ENTREGA_1.md` (secciones 1, 4 y 7), `docs/CONTEXTO.md` (secciones 9, 10 y 11), `docs/BITACORA.md`. La presentación vive en claude.ai (no está en el repo).
- Decisiones tomadas (y por qué):
  - Diapositiva nueva de normativas: Daniel expone 1.4 y la JM-98-2025 no tenía dónde ir.
  - En la diapositiva de contexto solo se usa el 38 % del Findex (coincide con el Banco Mundial); el 23 % no se dice como dato confirmado.
- Cambios de versión: ninguno.
- Evidencias generadas (EVD-): `EVD-1-03e_aws-mfa-raiz.png` (captura de Katherine: IAM > Credenciales de seguridad con sesión "root" y MFA virtual creado el 15-oct-2026; se tapó el número de cuenta que aparecía en el ARN). Con esto **se confirma que el MFA es del usuario raíz** y EVD-1-03 queda completa.
- IDs nuevos: ninguno.
- Hallazgos de la revisión del Word (pendientes de decisión de Daniel):
  1. **La rúbrica y el enunciado piden Arial 12 e interlineado 1.5**; el Word está en Times New Roman con doble espacio (decisión del 15-oct, tomada sin la rúbrica). Es el punto más grave.
  2. Las Tablas 7–23 van de 6.5 a 9 pt (CONTEXTO pone 10 como mínimo).
  3. Seis títulos difieren del esquema del enunciado (1.1, 1.4, 2.1, 2.3, 2.4 e "Índice General").
  4. La cita AWS (s. f.-a) acompaña a la JM-98-2025, pero esa página de AWS solo menciona la JM-104-2021.
  5. AWS (s. f.-c) sin "Recuperado el" (consistencia).
  6. Queda el `[VERIFICAR]` del Findex 23 %.
  7. La rúbrica .docx agrupa 5 + 5 + 10 puntos y el enunciado 4 × 5 (informativo).
- Problemas / bloqueos: ninguno nuevo.
- Siguiente paso: Daniel decide los puntos 1, 2, 3, 4 y 6; se aplican con un script nuevo sobre el Word, se regenera el índice, se renderiza y se exporta a PDF.

---

### 2026-10-15 — Manual — Claude (claude.ai)
- Fase / sección del informe: Entrega 1 — revisión de Aroldo (Paco) y correcciones pendientes del Word final.
- Qué se hizo:
  - Se verificó que el PR #18 (Word final ensamblado, JM-98-2025) estaba en `main`. Se agregó `docs/EQUIPO.md` (copia de `claude/PLAN_EQUIPO.md`).
  - Se validaron los 28 hallazgos de Paco (`Resultado_Prompt.xlsx`) contra el Word y el repo. Aplicados completos o en parte: 2, 3, 4, 5, 6, 9, 11 (parcial), 12, 13, 14 (parcial), 15, 16 (solo notas), 18, 19, 20, 21, 22, 23, 24, 25, 26 y 1 (como párrafo, sin sección 3). No aplicados: 7 en su forma propuesta (se resolvió con la decisión de TLS 1.3), 8 (OE3 = 13 casos, decisión del 14-oct; se aclaró la nota de la Tabla 11), 10 (23 % sigue sin fuente primaria), 17 (el resumen ejecutivo no es un abstract APA), 27 (sin fuente oficial accesible) y 28 (APA 7 no exige lista de tablas).
  - Script nuevo `scripts/entrega1_revision_paco.py`: aplica todos los cambios sobre el Word del PR #18 (cada reemplazo exige una sola coincidencia). Índice actualizado con `scripts/entrega1_indice.py`. Validador del skill de docx: sin errores. Word de 55 páginas renderizado y revisado completo.
  - Cambios del Word: resumen (14 categorías sin amenaza separada; mitigar 39 y aceptar 2); 1.1 (AME-01 sin control, con tratamiento); 1.2 sin [FECHA PENDIENTE] y plazo "Entrega final"; frases que presentan las Tablas 2 y 5; Tabla 5 y 1.5.1 con TLS 1.3; 1.4 (JM-98-2025 en índice de Banguat, SIB fuera del alcance, iniciativa 6464 con fechas); Figura 1 horizontal, sin título, con nodo AWS IAM; nota de Figura 1; notas de Tablas 7, 9 y 10 sin CONTEXTO; nota de Tabla 8 (rótulos de fronteras); Tabla 9 (svc-profile, svc-transfers y svc-admin igual que la Tabla 7, CTRL-15 en capa 3, TLS 1.3, fila de capa 6); Tabla 10 (MobSF); 1.5.6 ("Tres infringen... uno en el límite"); nota de Tabla 11 (CA-14, CA-16, CA-15); intro de 2 (repo público del T2); 2.1 (Gerente de Producto); Tablas 17 y 18; 2.4 (escalas distintas); 2.5.2 y Tablas 21 y 23 (RSK-01 Aceptar); 2.5.5 (P1×I5 = 14 + RSK-01, seguimiento de RSK-31, plan de RSK-32 con plazo, párrafo de cierre); Figuras 5 y 6 regeneradas sin título; notas de tablas y figuras a Arial 12 e interlineado 1.5.
  - Verificación de fuentes: JM-98-2025 figura en el índice oficial de Banguat 2025, pero el PDF no abrió (se mantiene "como se citó en"). Iniciativa 6464: presentada 29-oct-2024, sin dictamen al 16-jul-2026 (Emisoras Unidas); sin noticias posteriores al 15-oct. Findex: 38 % coincide con el Banco Mundial (digitalfinance.worldbank.org: 7.59 de 12.30 millones sin cuenta); 23 % y cifras de Costa Rica solo en prensa (Estrategia & Negocios, 17-jul-2025).
- Archivos creados o modificados: `docs/entregas/Entrega1_Informe_QWallet.docx`, `docs/evidencias/EVD-1-01_arquitectura_controles.svg/.png`, `docs/evidencias/EVD-2-05_heatmap_inherente.svg/.png`, `docs/evidencias/EVD-2-07_heatmap_residual_proyectado.svg/.png`, `docs/threat-model/T2_QWallet_ThreatModel.json`, `scripts/heatmap_riesgo.py`, `scripts/entrega1_revision_paco.py` (nuevo), `docs/EQUIPO.md` (nuevo), `docs/CONTEXTO.md` (secciones 3, 5, 7, 8, 10 y 11), `docs/entregas/ENTREGA_1.md` (secciones 1, 4 y 7), `docs/BITACORA.md`.
- Decisiones tomadas (y por qué):
  - **CTRL-08 con TLS 1.3:** desde nov-2025 API Gateway REST permite políticas TLS 1.3 en el endpoint por defecto (blog de AWS, 21-nov-2025). Se usa `SecurityPolicy_TLS13_1_2_2021_06` (API regional, modo `STRICT`): TLS 1.3 con TLS 1.2 de respaldo para Android anterior a 10 (minSdk 24). TLS 1.3 deja de ser riesgo residual aceptado.
  - **RSK-01 de Transferir a Aceptar:** el riesgo nace de desplegar en una sola región por costo; AWS no responde por la continuidad de Q-Wallet y el residual no baja. Conteo: Mitigar 39 · Aceptar 2.
  - Sin sección 3: CONTEXTO fija la estructura del enunciado. El cierre va como párrafo al final de 2.5.5 y el dictamen queda para la entrega final (OE5).
  - RSK-31: el seguimiento no puede depender del SIEM caído; revisión manual semanal de CloudTrail.
  - Plan de RSK-32 con plazo por evento ("antes del primer despliegue del pipeline a AWS") porque la fecha de la Entrega 2 no existe.
- Cambios de versión: ninguno.
- Evidencias generadas (EVD-): EVD-1-01, EVD-2-05 y EVD-2-07 regeneradas (sin título incrustado; EVD-1-01 con nodo IAM).
- IDs nuevos: ninguno.
- Problemas / bloqueos: texto oficial de JM-98-2025 y tabla de Guatemala del Findex 2025 no accesibles desde este entorno.
- Segunda pasada (a pedido de Daniel): revisión de 1.5, 2.1 y 2.2 hecha por Claude en lugar de la de Katherine, con estos cambios: 1.5.6 "Objetivos autorizados" solo con WAF, API Gateway y Lambda (la lista de servicios permitidos de AWS no incluye DynamoDB, SSM, S3 ni IAM; esos se verifican por configuración con Checkov y Prowler); casos de prueba móviles del MASTG; nota de la Tabla 11 sin afirmar nada sobre CA-15; Tabla 9 API Gateway en capa "2d / 5"; Tabla 8 TB3 con CTRL-03 y CTRL-05 y TB2 ordenada; Tabla 7 block con CTRL-23; Figura 1 con "TLS 1.3 / 1.2, pinning"; ACT-03 con custodio compartido (DevSecOps en Cognito, Cliente en el dispositivo); 2.1 explica por qué el Cliente es dueño de ACT-18; 2.2 cita el control 5.12 de ISO/IEC 27001. Cifras de 2.1 y 2.2 recalculadas: sin cambios. Word sigue en 55 páginas, validado y renderizado.
- Tercera pasada: **formato nuevo** por observación de Katherine, aprobada por Daniel: Times New Roman; fuera de tablas doble con 0 pt antes y 8 pt después; tablas 1.5 con 0/0 pt (`scripts/entrega1_estilos.py`, nuevo; CONTEXTO, sección 9 actualizado). Antes no se encontró la rúbrica en el repo ni en el proyecto: "Arial 12, 1.5" venía de copiar el Word del T2. El Word pasa a 67 páginas; la Figura 1 se redujo a 6.6 in y una frase de su nota pasó a 1.5.1 para que quepa en una página. `scripts/entrega1_indice.py` acepta ahora entradas del índice con espaciado propio.
- Evidencias: `EVD-1-03a_aws-consola.png` y `EVD-1-03b_aws-mfa.png` (capturas de Katherine del 15-oct, con el número de cuenta tapado porque el repo es público). Después llegaron `EVD-1-03c_aws-presupuesto-5usd.png` (presupuesto `qwallet-presupuesto-5usd` de US$5, en buen estado, con fecha 15/10/2026 visible) y `EVD-1-03d_aws-plan-gratuito.png` (US$100 de crédito, 183 días, vence el 15-abr-2027); la cuenta ya venía tapada. La segunda captura del presupuesto era igual pero sin fecha y no se subió. Solo falta confirmar que el MFA es del usuario raíz; la consola estaba en Ohio (us-east-2).
- Siguiente paso: captura del presupuesto (Katherine); que Katherine lea 1.5, 2.1 y 2.2 para exponer; ajustar la presentación; exportar PDF y entregar.

---

### 2026-10-14 — Manual — Claude (claude.ai)
- Fase / sección del informe: Entrega 1 — ensamblaje del Word final.
- Qué se hizo:
  - Se verificó que el PR #17 (sección 0 y referencias) estaba en `main`.
  - Norma de riesgo tecnológico: se cambia JM-104-2021 por **JM-98-2025**. El texto oficial no se pudo abrir (`banguat.gob.gt/.../Res_JM/2025/Res_JM-98-2025.pdf` y leyes.infile.com dan error; la página de Banguat 2025 solo lista actas). Se cita "como se citó en" Carrillo & Asociados (2025, 6 de noviembre, boletín 182: publicada en el Diario de Centro América el 30-oct-2025 y deroga el reglamento de 2021). Apoyo: Bitso (emisión 22-oct-2025), BLP (15-dic-2025) y White Jaguars (vigente desde 30-oct-2025). Cambios: 1.1, 1.4 (Tabla 6 y texto, con la aclaración de fuente secundaria), ACT-27 en las Tablas 12 y 14 y en 2.1, CONTEXTO sección 8, REGISTRO_RIESGOS y lista de referencias (sale Junta Monetaria 2021, entra Carrillo & Asociados 2025; siguen 24).
  - 1.2: OE4 pasa a 23 controles (CTRL-01 a CTRL-23). OE3 se mantiene en 13 casos: el catálogo vigente (REGISTRO_RIESGOS) tiene CA-01 a CA-13; CA-14 a CA-25 del Word T2 nunca se adoptaron y CA-14/CA-16 no pueden dar "evidencia de bloqueo" (se verifican por configuración). Se agregó "con el diseño ajustado que resume la Tabla 11".
  - Word ensamblado `docs/entregas/Entrega1_Informe_QWallet.docx` (52 págs.) con `scripts/entrega1_ensamblar.py`: orden 0 → 1.1–1.4 → 1.5 → 2 → Referencias; quita las 3 listas por sección; citas a la lista unificada (AWS s. f.-a/b/c, MASVS = OWASP Mobile Application Security Project 2024, ISO "e"); en 1.5 se agregan citas de MASVS, API Top 10, Threat Dragon, CIS (2024, 2025), ISO 27001, NIST SP 800-115, WSTG, Top 10:2025 y AWS (s. f.-b/c); 1.5 pasa a primera persona plural donde el sujeto era el equipo; Burp: "[VERIFICAR]" → "Vigente al instalar" (regla de CONTEXTO sección 3.1).
  - Formato: títulos APA uniformes (nivel 1 centrado negrita; 2 izquierda negrita; 3 negrita cursiva); 1.5 baja a nivel 2 y 1.5.x a nivel 3 (antes eran 1 y 2, con color azul); nueva página antes de 1, 2 y Referencias; número de página en todas las secciones (antes solo en la última); interlineado "auto" explícito (sin eso LibreOffice recortaba la Figura 1); se ordenaron elementos de tablas mal ubicados y un `tblLayout` duplicado heredados del Word de la sección 2.
  - Índice actualizado con `scripts/entrega1_indice.py` (páginas medidas en el render). Validador del skill de docx: sin errores. Revisión visual de todas las páginas.
  - Verificación automática: Tablas 1–23 y Figuras 1–6 en orden; las 24 referencias citadas y ninguna cita sin referencia; sin signo de sección; sin "&" entre autores ni "s.f.".
- Archivos creados o modificados: `docs/entregas/Entrega1_Informe_QWallet.docx` (nuevo), `scripts/entrega1_ensamblar.py` y `scripts/entrega1_indice.py` (nuevos), `docs/REGISTRO_RIESGOS.md`, `docs/CONTEXTO.md` (secciones 8, 10 y 11), `docs/entregas/ENTREGA_1.md` (secciones 4, 6 y 7), `docs/BITACORA.md`.
- Decisiones tomadas (y por qué):
  - Los Word por sección no se modifican: el Word final se genera con el script a partir de ellos, así el cambio queda trazable y repetible.
  - JM-98-2025 por fuente secundaria con "como se citó en", igual que Findex: no se puede citar como leído un texto que no abrimos.
- Cambios de versión: ninguno (docxcompose solo en el entorno de Claude).
- Evidencias generadas (EVD-): ninguna.
- IDs nuevos: ninguno.
- Hallazgos para el informe:
  - Quedan 3 `[VERIFICAR]`: Findex 23 % (1.1), autorización de la SIB para operar con dinero real (1.4) e iniciativa 6464 a la fecha de entrega (1.4).
  - 1.5 dice "Cuatro requieren rediseño"; la Tabla 11 marca 3 casos que infringen más CA-06 en límite. No se tocó (cifra fuera de la tarea).
  - Las Notas de las Tablas 7, 9 y 10 citan "CONTEXTO, sección x", un archivo interno.
  - La JM-99-2025 (misma fecha) reforma el reglamento de seguridad en canales electrónicos (MFA, bloqueos temporales, alertas): útil como referencia para F1 y CTRL-18 en entregas siguientes.
- Problemas / bloqueos: texto oficial de JM-98-2025 no accesible.
- Siguiente paso: revisión final en Microsoft Word (vie 16) y ajustes de la presentación.

---

### 2026-10-13 — Manual — Claude (claude.ai)
- Fase / sección del informe: Entrega 1 — sección 0, referencias unificadas y pendientes cortos (ACT-09, RSK-02).
- Qué se hizo:
  - Se verificó que el PR #16 (correcciones de la sección 2) estaba en `main`. Se detectó que el Word de 1.1–1.4 nunca se había subido al repo; el usuario lo adjuntó y se incluye en este PR.
  - Sección 0 (`Entrega1_Seccion_0_Portada_Resumen_Indice.docx`, 3 páginas): portada APA 7 de estudiante (no hay plantilla UMG en el repo), resumen ejecutivo de 1 página y índice. Cifras del resumen recalculadas por script desde el JSON y la Tabla 12: 28 activos (Crítica 11 · Alta 13 · Media 4), 41 AME + 14 N/A, 23 controles, inherente 18/12/11/0, residual proyectado 0/1/26/14, suma 580 → 207 (−64 %), Mitigar 39 · Transferir 1 · Aceptar 1.
  - El índice es un campo TOC de Word con páginas medidas al renderizar cada Word (cuerpo sin sus referencias), en el orden 0 → 1.1–1.4 → 1.5 → 2 → Referencias. Al ensamblar se actualiza con clic derecho → Actualizar campo.
  - Referencias (`Entrega1_Referencias.docx`): las 3 listas unificadas en 24 entradas APA 7, sin duplicados, en orden alfabético, con "y" y "s. f.". Duplicados resueltos: AWS Penetration testing (2026 / s. f.-a), MASVS (OWASP Foundation s. f. → OWASP Mobile Application Security Project 2024, v2.1.0), OWASP API Top 10 (dos URL), ISO/IEC 27001 y 27005.
  - Verificación web de los `[VERIFICAR]`:
    - JM-104-2021: PDF oficial en Banguat (`banguat.gob.gt/.../Res_JM/2021/Res_JM-104-2021.pdf`); publicada en el Diario de Centro América el 1-dic-2021 (vLex). El PDF es imagen y no se pudo leer la fecha de emisión; la referencia usa el año.
    - **Hallazgo: la Resolución JM-98-2025 (emitida 22-oct-2025, publicada y vigente desde el 30-oct-2025) emitió un nuevo Reglamento para la Administración del Riesgo Tecnológico y derogó el de 2021** (Carrillo & Asociados, Bitso, White Jaguars). No se pudo abrir el texto oficial. No se cambió nada del informe: decisión del equipo.
    - Decreto 67-2001: texto oficial en Banguat (emitido el 28-nov-2001; reformado por el Decreto 55-2010).
    - Decreto 57-2008: texto en SVET (emitido el 23-sep-2008). El sitio del Congreso no permitió la consulta.
    - Global Findex 2025: 38 % de adultos con cuenta coincide con el indicador FX.OWN.TOTL.ZS del Banco Mundial (38.28 %, 2024, leído en un agregador). El 23 % de pagos digitales y las cifras de Costa Rica no se confirmaron en fuente primaria; la cita secundaria de 1.1 (Estrategia & Negocios) se mantiene con su `[VERIFICAR]`. Informe original: Klapper et al. (2025), hdl.handle.net/10986/43438; no se agregó a la lista porque el texto no lo cita.
  - ACT-09 (decisión del usuario: S3 con bloqueo): Tabla 12 "Cloud: bucket S3 de estado con bloqueo nativo (use_lockfile), cifrado SSE-KMS, versionado y Block Public Access". También en CONTEXTO sección 3 y `REGISTRO_RIESGOS.md`.
  - RSK-02: dueño "Cliente" → "Gerente de Producto" en la Tabla 21 y frase en 2.5.2. Conteo: Lead Security Architect 28 · Gerente de Producto 13.
  - Los 5 Word renderizados y revisados; los 2 nuevos validados con el validador del skill de docx.
- Archivos creados o modificados: `docs/entregas/Entrega1_Seccion_0_Portada_Resumen_Indice.docx` (nuevo), `docs/entregas/Entrega1_Referencias.docx` (nuevo), `docs/entregas/Entrega1_Secciones_1-1_a_1-4.docx` (nuevo en el repo, sin cambios), `docs/entregas/Entrega1_Seccion_2_Activos_Riesgos.docx`, `scripts/entrega1_seccion0_referencias.js` y `scripts/docx_toc_campo.py` (nuevos), `docs/REGISTRO_RIESGOS.md`, `docs/CONTEXTO.md` (secciones 3, 8, 10 y 11), `docs/entregas/ENTREGA_1.md` (secciones 4 y 7), `docs/BITACORA.md`.
- Decisiones tomadas (y por qué):
  - **ACT-09 en S3 con bloqueo nativo (sin DynamoDB):** el estado guarda atributos sensibles y lo usan 3 integrantes y el pipeline por OIDC; S3 permite cifrado, historial y CTRL-12. Terraform lo soporta desde 1.10.
  - Referencias en archivo aparte para facilitar el ensamblaje. Las listas por sección de los 3 Word no se tocaron: se quitan al ensamblar.
  - Portada APA 7 de estudiante mientras no exista plantilla UMG.
- Cambios de versión: ninguno.
- Evidencias generadas (EVD-): ninguna.
- IDs nuevos: ninguno.
- Hallazgos para el informe:
  - JM-104-2021 derogada por JM-98-2025: afecta 1.4 (texto y Tabla 6), ACT-27, CONTEXTO sección 8, la presentación y el texto falso de la pantalla Welcome.
  - 1.2: OE3 dice "13 casos de abuso" y OE4 "21 controles (CTRL-01 a CTRL-21)"; hoy son 23 controles.
  - Al ensamblar hay que ajustar citas en el texto: AWS (s. f.-a/b/c), MASVS como OWASP Mobile Application Security Project (2024), ISO "e" en lugar de "&". La sección 1.5 no cita en el texto ninguna de sus referencias.
- Problemas / bloqueos: ninguno.
- Siguiente paso: decidir la norma de riesgo tecnológico y corregir OE3/OE4; ensamblar el Word final.

---

### 2026-10-12 (5) — Manual — Claude (claude.ai)
- Fase / sección del informe: Entrega 1 — correcciones de la sección 2 decididas en la revisión (entrada 2026-10-12 (4)) y su efecto en 1.5.
- Qué se hizo:
  - 2.5.1: oración que aclara que el impacto mide lo que la amenaza le hace al activo, no el valor total del activo; por eso AME-02, 09, 10, 14, 18, 22, 38 y 40 (sobre activos Críticos) tienen impacto de 3 o menos. Ejemplo AME-14. Verificado por script: son exactamente esas 8.
  - Tabla 21: columna "Dueño del riesgo" = propietario (Tabla 12) del primer ACT citado en la descripción de cada AME en el JSON, calculado por script: Lead Security Architect (I1) 28, Gerente de Producto 12, Cliente 1 (AME-02, activo ACT-18 dispositivo). Pasa a página horizontal (mismo patrón de las Tablas 12 y 17). Frase del criterio en 2.5.2 con cita a ISO/IEC 27005:2022.
  - La Tabla 21 no tenía rótulo APA ("Tabla 21" + título) desde que se creó la sección 2; se agregó "Matriz de riesgos inherentes de Q-Wallet". Sin cambio de numeración.
  - CTRL-23 (procedimiento, capa 7): verificación de identidad del cliente por un canal distinto antes de que soporte bloquee, desbloquee o cambie datos, más capacitación anual contra ingeniería social. Mitiga AME-03. Agregado en CONTEXTO sección 5, en el campo mitigation de AME-03 del JSON, en la Tabla 17 (fila AME-03) y su Nota, y en la Tabla 9 de 1.5 (fila "Personal de soporte (TB2)"). Nota de la Figura 1: CTRL-23 es de procedimiento y no se dibuja; EVD-1-01 sin cambios.
  - Coherencia: "CTRL-01 a CTRL-22" pasa a "CTRL-01 a CTRL-23" en el texto de 2.4 y en la Nota de la Tabla 17; "veintidós controles" pasa a "veintitrés" en 1.5.4.
  - `scripts/heatmap_riesgo.py`: inherente 18/12/11/0 y residual 0/1/26/14 sin cambio; EVD-2-05 y EVD-2-07 se regeneran idénticos byte a byte. El residual de AME-03 sigue en P2×I3 = 6.
  - Ambos Word validados y renderizados (sección 2: 31 páginas).
- Archivos creados o modificados: `docs/entregas/Entrega1_Seccion_2_Activos_Riesgos.docx`, `docs/entregas/Entrega1_Seccion_1-5_Scope_Tecnico.docx`, `docs/threat-model/T2_QWallet_ThreatModel.json`, `docs/CONTEXTO.md` (sección 5 y 11), `docs/entregas/ENTREGA_1.md` (sección 4), `docs/BITACORA.md`.
- Decisiones tomadas (y por qué):
  - Referencia de CTRL-23: ISO/IEC 27001:2022 A.5.16 (gestión de identidades) y A.6.3 (concientización y capacitación).
  - El dueño del riesgo sigue la regla mecánica (primer ACT). Queda RSK-02 con dueño "Cliente": revisar si se prefiere Gerente de Producto, porque ISO/IEC 27005 espera un responsable dentro de la organización.
- Cambios de versión: ninguno.
- Evidencias generadas (EVD-): ninguna.
- IDs nuevos: CTRL-23.
- Problemas / bloqueos: el subtítulo de EVD-2-07 (Figura 6) dice "CTRL-01 a CTRL-22"; no se tocó para no alterar la figura. CTRL-23 no cambia el residual.
- Siguiente paso: CTRL-23 en la diapositiva de controles y EVD-2-07 en P-4; decidir el límite de monto por transferencia; mié 14 sección 0 y ensamblaje.

---

### 2026-10-12 (4) — Manual — Claude (claude.ai)
- Fase / sección del informe: Entrega 1 — sección 2.5 (riesgo residual proyectado) y revisión de la sección 2 contra la rúbrica.
- Qué se hizo:
  - Script `scripts/heatmap_riesgo.py`: lee `T2_QWallet_ThreatModel.json`, recalcula P e I inherentes desde DREAD (0 diferencias con el modelo) y toma el residual de la frase "Residual esperado P x I" del campo `mitigation` de cada amenaza (0 diferencias entre P×I y el puntaje escrito). Con `inh` reproduce EVD-2-05 byte a byte; con `res` genera EVD-2-07.
  - Resultado: inherente Crítico 18 · Alto 12 · Medio 11 · Bajo 0 → residual proyectado Crítico 0 · Alto 1 · Medio 26 · Bajo 14. Suma de P×I: 580 → 207 (−64 %). 32 amenazas bajan solo P, 7 bajan P e I, 2 no cambian (AME-01 Transferir, AME-31 Aceptar). 15 quedan en P1×I5 = 5.
  - Word de la sección 2: nueva 2.5.5 "Riesgo residual proyectado y tratamiento" antes de las referencias, con Figura 6 (EVD-2-07) y Tabla 23 (inherente vs. residual por RSK). Incluye criterio de aceptación del riesgo, coherencia del tratamiento, plan para RSK-32 y defensa de "ningún inherente Bajo". Sin cambios en el texto, numeración ni Notas existentes. Validado y renderizado (29 páginas).
  - ENTREGA_1: sección 3 (pendientes revisados), sección 4 (2.5, Referencias, Presentación), sección 7 (OWASP Top 10:2025 confirmada). CHECKLIST: EVD-2-07 nuevo.
- Archivos creados o modificados: `scripts/heatmap_riesgo.py` (nuevo), `docs/evidencias/EVD-2-07_heatmap_residual_proyectado.png` y `.svg` (nuevos), `docs/entregas/Entrega1_Seccion_2_Activos_Riesgos.docx`, `docs/CHECKLIST_EVIDENCIAS.md`, `docs/entregas/ENTREGA_1.md`, `docs/CONTEXTO.md` (sección 11), `docs/BITACORA.md`.
- Decisiones tomadas (y por qué):
  - **EVD-2-07 para la proyección; EVD-5-09 queda para el residual verificado.** Son cosas distintas: una es lo esperado, la otra lo medido tras las pruebas.
  - **Criterio de aceptación del riesgo:** Bajo se acepta; Medio con aprobación del propietario y seguimiento en el SIEM; Alto solo con plan con fecha; Crítico no se acepta. ISO/IEC 27005 lo exige y el informe no lo tenía.
  - **RSK-32 (residual Alto) no se acepta:** plan de refuerzo de CTRL-21 en la fase de arquitectura (entorno protegido con aprobación de un segundo integrante, OIDC limitado a ese entorno y a `main`, rol de despliegue mínimo) → esperado P1×I5 = 5. No se cambió el JSON ni CONTEXTO sección 5 hasta implementarlo.
  - Tabla 23 en página vertical, después de la Tabla 22, para no renumerar.
- Cambios de versión: ninguno (cairosvg solo en el entorno de Claude para el PNG).
- Evidencias generadas (EVD-): EVD-2-07.
- IDs nuevos: ninguno.
- Hallazgos de la revisión de la sección 2 (propuestas, no aplicadas):
  - 8 amenazas sobre activos de criticidad Crítica tienen impacto ≤ 3 (AME-02, 09, 10, 14, 18, 22, 38, 40). Es defendible (el impacto mide lo que la amenaza le hace al activo, no el valor total del activo), pero falta decirlo en 2.5.1.
  - La Tabla 21 no tiene dueño del riesgo (ISO/IEC 27005 lo pide). Propuesta: columna con el propietario del activo principal.
  - AME-03 (ingeniería social a soporte) no tiene control en el catálogo; capa 7 floja. Propuesta: CTRL-23 (procedimiento de verificación de identidad en soporte + capacitación).
  - Ningún límite de monto por transferencia: es lo que bajaría el impacto de los 15 riesgos en P1×I5.
- Problemas / bloqueos: ninguno.
- Siguiente paso: decidir las propuestas; EVD-2-07 en la diapositiva P-4; mié 14 sección 0 y ensamblaje.

---

### 2026-10-12 (3) — Manual — Claude (claude.ai) + Threat Dragon 2.6.2
- Fase / sección del informe: Entrega 1 — sección 2.3 (Figuras 2–4).
- Qué se hizo:
  - Capturas de los 3 DFD en OWASP Threat Dragon 2.6.2 (escritorio) a partir de `T2_QWallet_ThreatModel.json`, sin modificar el modelo. Se recortaron los márgenes en blanco y se aplanó la transparencia sobre fondo blanco.
  - Se reemplazaron los 3 marcadores punteados del Word de la sección 2 por las imágenes. Títulos, numeración y Notas sin cambios.
  - Figura 2 (nivel 0) a 16 cm en página vertical. Figuras 3 y 4 (nivel 1 y nivel 2) a 22.9 cm en una sección horizontal: a 16 cm su texto quedaba en unos 3 puntos y no se leía.
  - Revisión visual de las capturas: la primera del nivel 2 traía el almacén CloudWatch Logs seleccionado (recuadro y botón de borrar visibles) y se repitió.
  - CHECKLIST_EVIDENCIAS: EVD-2-01/02/03 marcados y EVD-2-03 unificado con el uso del Word. Se marcaron también EVD-1-01 y EVD-2-05, que ya existían, y se corrigió su herramienta (script, no draw.io/Excel).
- Archivos creados o modificados: `docs/evidencias/EVD-2-01_dfd-nivel0.png`, `EVD-2-02_dfd-nivel1.png`, `EVD-2-03_dfd-nivel2.png` (nuevos), `docs/entregas/Entrega1_Seccion_2_Activos_Riesgos.docx`, `docs/CHECKLIST_EVIDENCIAS.md`, `docs/entregas/ENTREGA_1.md` (sección 4), `docs/CONTEXTO.md` (sección 11), `docs/BITACORA.md`.
- Decisiones tomadas (y por qué):
  - **EVD-2-03 = DFD nivel 2 con los elementos con amenazas marcados en rojo.** Threat Dragon no dibuja el texto de las amenazas en el lienzo, solo el borde rojo; el detalle va en la Tabla 17. Así la evidencia no promete lo que la imagen no muestra.
  - Fecha/hora fuera de la figura (se ve mal en un informe): queda en esta bitácora y en el historial de git.
  - No se reacomodó el diagrama de nivel 1 (cruces de líneas y etiquetas encimadas): hacerlo cambia el JSON del threat model y no aporta al análisis.
- Cambios de versión: ninguno.
- Evidencias generadas (EVD-): EVD-2-01, EVD-2-02, EVD-2-03.
- IDs nuevos: ninguno.
- Hallazgos para el informe:
  - Distribución de entradas del modelo por diagrama: nivel 0: 1; nivel 1: 44 (35 abiertas, 9 N/A); nivel 2: 10 (5 abiertas, 5 N/A). En nivel 2 están en rojo 2.1, 2.2, 2.3, 2.5 y 2.6; 2.4 (idempotencia) no tiene amenaza abierta propia.
  - La Figura 3 impresa queda con letra de unos 4 puntos: legible, pero conviene que la presentación use la versión digital con zoom.
- Problemas / bloqueos: ninguno.
- Siguiente paso: mar 13, heatmap "después" proyectado (P-4) y revisión de 2.x.

---

### 2026-10-12 (2) — Manual — Claude (claude.ai)
- Fase / sección del informe: Entrega 1 — sección 2 Activos y Riesgos (2.1 a 2.5).
- Qué se hizo:
  - Word de la sección 2 con formato UMG y APA 7, numeración continua (Tablas 12–22, Figuras 2–5), primera persona plural. Todas las cifras de amenazas se generan por script desde el JSON del threat model; se verificó que cada DREAD, P, I y P×I coincide con las fórmulas de CONTEXTO sección 6 (0 diferencias).
  - 2.1: inventario de 28 activos con los 15 campos (Tabla 12). Tipos: Información 9, Software 9, Físico 3, Personal 2, Servicios 3, Empresa 2.
  - 2.2: criterios CIA (Tabla 13), cálculo C+I+D por activo (Tabla 14) y distribución (Tabla 15): Crítica 11, Alta 13, Media 4, Baja 0.
  - 2.3: STRIDE con marcadores para los 3 DFD (Figuras 2–4), distribución (Tabla 16: I 13, T 9, S 6, D 5, E 5, R 3), catálogo de 41 AME con elemento, frontera, activos y CTRL (Tabla 17) y 14 casos N/A justificados (Tabla 18).
  - 2.4: criterios DREAD por factor (Tabla 19) y DREAD de las 41 AME con justificación (Tabla 20): Alta 15, Media 26, Baja 0.
  - 2.5: conversión DREAD → P×I con ejemplos, matriz RSK-01..41 con capa, tipo, impacto de negocio y tratamiento (Tabla 21), heatmap EVD-2-05 como Figura 5 y riesgos por capa (Tabla 22). Inherente: Crítico 18, Alto 12, Medio 11, Bajo 0. Tratamiento: Mitigar 39, Transferir 1 (RSK-01), Aceptar 1 (RSK-31).
- Archivos creados o modificados: `docs/entregas/Entrega1_Seccion_2_Activos_Riesgos.docx` (nuevo), `docs/REGISTRO_RIESGOS.md` (ACT-27 renombrado, ACT-28), `docs/entregas/ENTREGA_1.md` (sección 4), `docs/CONTEXTO.md` (sección 11), `docs/BITACORA.md`.
- Decisiones tomadas (y por qué):
  - **ACT-28 SIEM Wazuh** se agrega: AME-31 y AME-41 lo citan y no estaba en la semilla.
  - **ACT-27** pasa a "Alineación regulatoria (referencia JM-104-2021)": el nombre anterior afirmaba cumplimiento.
  - RSK-xx usa el mismo número que su AME para trazar sin tabla de cruce.
  - Tipo de riesgo e impacto de negocio no estaban en el JSON: se asignaron con criterio explícito en el texto (financiero = mueve dinero; operacional = detiene o compromete la plataforma; reputacional = expone datos; legal = debilita evidencia ante disputas).
  - Las justificaciones DREAD se redactaron a partir de la descripción de cada AME; los valores no se tocaron.
  - Tablas anchas (12, 17) en páginas horizontales.
- Cambios de versión: ninguno.
- Evidencias generadas (EVD-): ninguna nueva (se usa EVD-2-05). Pendientes: EVD-2-01, EVD-2-02, EVD-2-03 (Figuras 2–4).
- IDs nuevos: ACT-28; RSK-01 a RSK-41.
- Hallazgos para el informe:
  - `CHECKLIST_EVIDENCIAS.md` define EVD-2-03 como "amenazas STRIDE sobre elementos del DFD"; en el Word se usa para el DFD nivel 2 con sus amenazas visibles. Unificar.
  - Ningún riesgo inherente queda Bajo: el redondeo hacia arriba de la conversión DREAD → P×I sube los valores; es coherente con la escala fija, pero conviene defenderlo en la presentación.
  - ACT-09: el backend remoto de Terraform no está definido en `/infra` (vacío) → `[VERIFICAR]`.
- Problemas / bloqueos: ninguno.
- Siguiente paso: capturas de los 3 DFD; mar 13 heatmap "después" proyectado y revisión de 2.x.

---

### 2026-10-12 — Manual — Claude (claude.ai)
- Fase / sección del informe: Entrega 1 — apoyos de la sección 2 y presentación de avance.
- Qué se hizo:
  - Heatmap de riesgo inherente ("antes") calculado desde el threat model (41 AME): Crítico 18, Alto 12, Medio 11, Bajo 0. Imagen EVD-2-05 (PNG + SVG) con conteo por celda en la matriz 5x5, escala de CONTEXTO sección 6.
  - Presentación de avance de la Entrega 1: 14 diapositivas en Claude Slides, identidad Q-Wallet, exportable a PDF, animaciones mínimas (solo transición fade). Cubre portada, contexto, objetivos, alcance, metodología, arquitectura (figura EVD-1-01), activos, STRIDE, heatmap, 7 capas, proyección antes/después, controles, cronograma y cierre.
  - Referencia OWASP Top 10:2025 confirmada (URL oficial https://owasp.org/Top10/2025/); se quitó su [VERIFICAR] del Word de 1.5.
  - Catedrático confirmado: Osberto Saúl Gallo Orozco. Integrantes y roles: I1 Lead Security Architect = Barrios Monzón; I2 DevSecOps = Sandoval Monterroso; I3 Pentester = Lolmet Calel.
  - Regla de sincronización nueva: GitHub es la fuente de verdad. Al iniciar una tarea se clona el repo y se lee el estado real; al cerrar se entregan los .md y los comandos git y el usuario crea el PR. Se agregó a las instrucciones del proyecto, a CLAUDE.md y a GEMINI.md.
- Archivos creados o modificados: `docs/evidencias/EVD-2-05_heatmap_inherente.png` y `.svg` (nuevos), `docs/entregas/Entrega1_Seccion_1-5_Scope_Tecnico.docx` (referencia OWASP), `docs/CONTEXTO.md` (sección 1, 9, 11), `docs/entregas/ENTREGA_1.md` (sección 4, 7), `docs/BITACORA.md`, `CLAUDE.md`, `GEMINI.md`. La presentación es un artefacto en claude.ai, no un archivo del repo.
- Decisiones tomadas: la presentación se hace en Claude Slides (no Claude Design) por exportar a PDF y permitir edición.
- Cambios de versión: ninguno.
- Evidencias generadas (EVD-): EVD-2-05 (heatmap). Pendientes: EVD-2-01/02/03 (capturas de los 3 DFD en Threat Dragon), EVD-1-02 (estructura del repo), EVD-1-03 (cuenta AWS).
- IDs nuevos: ninguno (CTRL-22 se agregó el 10-oct).
- Problemas / bloqueos: el repo de GitHub va atrás; hay que subir el backlog local. Falta la sección 2 completa en Word (2.1–2.5), la sección 0 y el ensamblaje del informe.
- Siguiente paso: sección 2 (Activos y Riesgos) en Word.

---

### 2026-10-10 (4) — Manual — Claude (claude.ai)
- Fase / sección del informe: Entrega 1 — sección 1.5 Scope técnico.
- Qué se hizo:
  - Redacción completa de 1.5: arquitectura con Figura 1 (diagrama de arquitectura de seguridad con las fronteras TB1–TB6 y los 22 controles ubicados donde actúan; SVG editable + PNG a 2x), Tabla 7 (superficie de la API: 5 servicios, endpoints, método, autenticación, rol, controles), Tabla 8 (fronteras TB1–TB6 con qué cruza, amenaza principal y control), Tabla 9 (controles por componente/frontera/capa), Tabla 10 (herramientas por fase con versión exacta), Tabla 11 (revisión de los casos de abuso vs. la política de pentest de AWS). Reglas de enfrentamiento. Referencias APA 7 reales.
  - Se oficializa **CTRL-22** (FLAG_SECURE en pantallas sensibles; MASVS-PLATFORM; mitiga AME-09; capa 1) en CONTEXTO sección 5. Ya se usaba como propuesta en el Word T2 entregado.
  - Revisión CA-01 a CA-13 vs. la política de AWS (Tabla 11): rediseñar CA-02, CA-03 y CA-12 (sin inundación); matizar CA-06 (ráfaga mínima) y CA-13 (se excluye forzar el login de Cognito). Los casos nuevos del T2 CA-14 (credential stuffing/phishing contra Cognito) y CA-16 (saturación de la API) también chocan y se tratan igual.
  - Formato UMG (Arial 12, 1.5, sangría 1.27 cm, márgenes 2.54 cm, justificado) y estilo APA 7 calcado del Word T2 entregado (Figura/Tabla N con Nota).
- Archivos creados o modificados: `docs/entregas/Entrega1_Seccion_1-5_Scope_Tecnico.docx` (nuevo), `docs/evidencias/EVD-1-01_arquitectura_controles.png` y `.svg` (nuevos), `docs/CONTEXTO.md` (sección 5: CTRL-22; sección 10 y 11), `docs/entregas/ENTREGA_1.md` (sección 2, 4, 5, 7), `docs/BITACORA.md`.
- Decisiones tomadas (y por qué):
  - En el diagrama los controles van como etiquetas de código (CTRL-xx) y el detalle en la Tabla 9, para no saturar la figura (21+ controles encima no se leen a 16 cm en Word).
  - Numeración: Figura 1 (1.1–1.4 no tiene figuras) y Tablas 7–11 (continúan tras la Tabla 6).
  - Redacción en primera persona plural (consigna de la tarea). El Word T2 es impersonal; unificar el registro al ensamblar el informe final.
  - CTRL-22 se oficializa en lugar de dejarlo como nota al pie: ya está implementado y el T2 lo usa.
- Cambios de versión: ninguno.
- Evidencias generadas (EVD-): `EVD-1-01_arquitectura_controles` (PNG + SVG). Pendientes de 1.5: EVD-1-02 (estructura del repo) y EVD-1-03 (cuenta AWS).
- IDs nuevos: **CTRL-22**.
- Hallazgos para el informe:
  - El repo de GitHub va 5 días atrasado respecto al proyecto: faltan subir las 3 entradas del 10-oct, los cambios de CONTEXTO, la limpieza del signo de sección, el `.docx` de 1.1–1.4 y lo de 1.5. Hay que commitear/pushear lo local.
  - El Word T2 entregado trae datos que difieren de CONTEXTO: profesor "Gallo Orozco, Osberto Saúl" (CONTEXTO dice "César Rodríguez Minas") y los nombres de los 3 integrantes (Sandoval Monterroso, Barrios Monzón, Lolmet Calel). Confirmar cuál profesor corresponde a la Entrega 1 y mapear nombres a roles I1/I2/I3.
  - El T2 amplió los casos de abuso a CA-01..CA-25 (13 originales + 12 propuestos). `REGISTRO_RIESGOS.md` solo tiene CA-01..CA-13; conviene sincronizarlo.
- Problemas / bloqueos: integrantes/roles y catedrático por confirmar; `.docx` de 1.1–1.4 no está en el repo.
- Siguiente paso: secciones 2.1–2.2 (inventario ISO 27001 + clasificación CIA), lun 12-oct.

---

### 2026-10-10 (3) — Manual — Claude (claude.ai)
- Fase / sección del informe: Convenciones del proyecto.
- Qué se hizo: se prohíbe el signo de sección (U+00A7) en todo el proyecto. Se reemplazó por la palabra "sección" en CONTEXTO, ENTREGA_1, BITACORA y TRASPASO_CHAT (copias del proyecto y repo), y en el resto de archivos `.md` del repo con un script de PowerShell.
- Archivos creados o modificados: `docs/CONTEXTO.md` (regla nueva en Convenciones, apartado Escritura), `docs/entregas/ENTREGA_1.md`, `docs/BITACORA.md`, `docs/TRASPASO_CHAT.md`, `CLAUDE.md`, `GEMINI.md` y demás `.md` del repo.
- Decisiones tomadas: preferencia del equipo; la regla también se agrega a las instrucciones del proyecto en claude.ai, a `CLAUDE.md` y a `GEMINI.md`.
- Cambios de versión: ninguno.
- Evidencias generadas (EVD-): ninguna.
- IDs nuevos: ninguno.
- Problemas / bloqueos: ninguno.
- Siguiente paso: sección 1.5 de la Entrega 1.

---

### 2026-10-10 (2) — Manual — Claude (claude.ai)
- Fase / sección del informe: Entrega 1 — secciones 1.1 a 1.4.
- Qué se hizo:
  - Redacción de 1.1 Contexto (fintech en LAC y Guatemala, inclusión financiera, riesgo de apps financieras, Q-Wallet y F1–F7), 1.2 Objetivos (general + OE1–OE5 SMART con Tabla 2), 1.3 Alcance (incluido, excluido, enfoque seguro desde el diseño, restricciones) y 1.4 Normativas (Tabla 6, 11 normas). Formato UMG: Arial 12, 1.5, sangría 1.27 cm, márgenes 2.54 cm, tablas APA 7. 17 referencias APA 7.
  - Fuentes verificadas en web: IV Informe Fintech BID/Finnovista (2024), Global Findex 2025 (vía Estrategia & Negocios), OWASP Top 10:2025, MASVS v2.1.0, política de pentest de AWS, iniciativa 6464 de datos personales (Emisoras Unidas, jul-2026).
- Archivos creados o modificados: `docs/entregas/Entrega1_Secciones_1-1_a_1-4.docx` (nuevo), `docs/entregas/ENTREGA_1.md` (sección 2, sección 4, sección 7), `docs/CONTEXTO.md` (sección 4, sección 5, sección 7, sección 8, sección 10, sección 11), `docs/BITACORA.md`.
- Decisiones tomadas (y por qué):
  - Objetivos alineados a los 5 componentes de la rúbrica (fases 1 y 2 en OE1), no a "6 fases": son 5 específicos y la rúbrica tiene 5 componentes.
  - Plazos de OE2–OE5 quedan como `[FECHA PENDIENTE]`: sin fecha final no son SMART completos.
  - Se corrige la inconsistencia "TLS 1.3" en sección 4 y sección 7 de CONTEXTO: CTRL-08 define TLS 1.2+ con TLS 1.3 como riesgo aceptado.
  - OWASP Top 10 vigente es 2025; las referencias A0x de sección 5 siguen en numeración 2021 y se anotan sus equivalencias.
  - JM-104-2021 solo como "diseñado con referencia a" (Q-Wallet, S.A. no es entidad supervisada).
- Cambios de versión: ninguno.
- Evidencias generadas (EVD-): ninguna.
- IDs nuevos: OE1–OE5 (objetivos específicos).
- Hallazgos para el informe:
  - La política de pentest de AWS prohíbe la inundación de solicitudes (login y API) y **Cognito no está entre los servicios autorizados**. Afecta los casos de abuso de rate limiting (429) y fuerza bruta del PIN: deben diseñarse con ráfagas cortas contra umbrales bajos y sin atacar el login de Cognito.
- Problemas / bloqueos: `[VERIFICAR]` pendientes (JM-104 fecha/URL, Findex en fuente primaria, URL de Decretos 67-2001 y 57-2008); título exacto de la sección 1 según el enunciado.
- Siguiente paso: sección 1.5 (scope técnico + diagrama de arquitectura con controles), dom 11-oct.

---

### 2026-10-10 — Manual — Claude (claude.ai + Claude Code)
- Fase / sección del informe: Entrega 1 — planificación.
- Qué se hizo:
  - Registro tardío: modelo de amenazas T2 v1 (`99cc65a`, 40 amenazas) y v2 (`e0c8724`, PR #8, 09-oct): agrega AME-41 (flujo S3 → Wazuh, TB4–TB6) y 14 justificaciones N/A de STRIDE. Total 41 AME en DFD nivel 0, 1 y 2.
  - Se crea `docs/entregas/ENTREGA_1.md`: alcance, estructura del Word, puntos de la presentación (objetivos, resultados, cómo llegamos, proyección, cronograma, implementación), resultados extraídos del threat model, estado por sección y cronograma 10–17 oct.
  - Se crea `CLAUDE.md` en la raíz para que Claude Code cargue el mismo contexto.
- Archivos creados o modificados: `CLAUDE.md`, `docs/entregas/ENTREGA_1.md`, `docs/CONTEXTO.md` (sección 10, sección 11), `docs/BITACORA.md`.
- Decisiones tomadas: el repo es la fuente de verdad del contexto; el proyecto de claude.ai guarda una copia que se refresca al cerrar sesión.
- Cambios de versión: ninguno.
- Evidencias generadas (EVD-): ninguna.
- IDs nuevos: AME-01 a AME-41 (threat model).
- Problemas / bloqueos: plantilla UMG, integrantes, fecha final y formato de la presentación siguen pendientes.
- Siguiente paso: sección 1 (1.1–1.4) según `ENTREGA_1.md` sección 5.

---

### 2026-10-05 (2) — Manual — Claude + PowerShell + GitHub web
- Fase / sección del informe: Preparación. Seguridad del repositorio (CTRL-10, CTRL-16, CTRL-21).
- Qué se hizo:
  - `.github/dependabot.yml` (ya existía con npm `/mobile`, npm `/services`, terraform `/infra` y github-actions `/`): se agregó `open-pull-requests-limit: 0` a las dos entradas npm. Solo PR de seguridad; sin PR de versión que rompan SDK 57 ni las versiones fijadas de sección 3.1. Terraform y github-actions siguen con PR de versión semanales (revisión manual).
  - Referencias al audit actualizadas a `EVD-3-00_npm-audit-mobile.txt` en esta bitácora. El ID `EVD-3-01` queda reservado para el pipeline de GitHub Actions (CHECKLIST_EVIDENCIAS).
  - Hallazgo: el repo era **privado**, en contra de sección 3. En GitHub Free los rulesets no se aplican en repos privados: el primer push de prueba (`f91caf0`, commit vacío) pasó a `main`.
  - gitleaks 8.30.1 (Docker `zricethezav/gitleaks:v8.30.1`) sobre el historial completo (16 commits): `no leaks found`. Después se hizo **público** el repo.
  - Ruleset `main-protegida`: Active, target default branch, bypass vacío, reglas Restrict deletions, Block force pushes, Require pull request (0 approvals). Verificado: push directo rechazado con `GH013`.
  - Advanced Security: Dependency graph, Dependabot alerts, Dependabot security updates, Secret Protection y Push protection activos. CodeQL Default setup **no** activado (se usará workflow avanzado fijado por SHA).
  - Evidencias subidas por rama `chore/evidencias-github` + PR.
- Errores encontrados y corregidos:
  1. Reemplazo masivo `EVD-3-01 → EVD-3-00` (commit `10a87fc`) alteró por error `CHECKLIST_EVIDENCIAS.md` (ID del pipeline) y `TRASPASO_CHAT.md`, y sobrescribió `dependabot.yml`. Corregido en `06ff85c` restaurando desde `b271357`.
  2. `dependabot.yml` sin salto de línea final (here-string de PowerShell). Corregido en `43cacc7`.
  3. El primer ruleset no se guardó (la API `/rulesets` devolvía vacío). Se recreó y se presionó **Create**.
- Archivos creados o modificados: `.github/dependabot.yml`, `docs/BITACORA.md`, `docs/CONTEXTO.md`, `docs/TRASPASO_CHAT.md`, `docs/evidencias/*`.
- Decisiones tomadas (y por qué):
  - Repo público: rulesets, secret scanning, push protection y CodeQL gratis; Actions sin límite de minutos. El diseño no depende de ocultar código.
  - Desde ahora **ningún commit directo a `main`**, tampoco de agy: rama → PR → merge.
- Cambios de versión: ninguno.
- Evidencias generadas (EVD-): `EVD-1-04a_github-secret-protection.png`, `EVD-1-04b_github-dependabot.png`, `EVD-1-04c_github-ruleset-main.png`, `EVD-1-06_ruleset-push-rechazado.png`, `EVD-1-07_gitleaks-historial-pre-publico.png`.
- IDs nuevos: ninguno.
- Hallazgos para el informe:
  - Dependabot reporta 5 vulnerabilidades (2 altas, 3 moderadas) en `main`; `npm audit` reportó 33. Conciliar en la fase de SCA (probable deduplicación por advisory).
  - Dependabot abrió 6 ramas/PR en `/mobile` (reanimated 4.7.0, react-native-svg 15.15.5, tailwindcss 4.3.3, typescript 7.0.2 y dos grupos `multi-*`). Tailwind 4 rompe NativeWind 4 y TypeScript 7 sale de sección 3.1: **no se mergean**. Revisar si alguno es de seguridad y cerrar los de versión.
- Problemas / bloqueos: ninguno.
- Siguiente paso: revisar y cerrar los PR de Dependabot; corregir textos falsos de la UI.

---

### 2026-10-05 — Manual — Claude + PowerShell (cierre por agy)
- Fase / sección del informe: Preparación del entorno. Primer build nativo Android.
- Qué se hizo:
  - `scripts/dev-env.ps1` re-guardado en UTF-8 con BOM (commit bfe776e).
  - Instalación de Android Studio y SDK. NDK 27.1.12297006 y Build-Tools 36.0.0 instalados automáticamente por Gradle.
  - Creación del AVD `Pixel_8_API_36`, Google APIs x86_64. Se eligió la imagen sin Google Play porque permite `adb root`, necesario para el pentest (certificado del proxy y Frida).
  - Primer `npx expo run:android` exitoso. La app abre en el emulador en la pantalla Welcome.
- Errores encontrados y corregidos:
  1. `PluginError ERR_UNSUPPORTED_NODE_MODULES_TYPE_STRIPPING`. Causa: `expo-screen-capture` estaba registrado en `plugins` de `app.json`, pero no tiene config plugin. Corrección: se quitó de `plugins`. FLAG_SECURE se mantiene en runtime.
  2. Gradle: `Could not find com.aheaditec.talsec.security:TalsecSecurity-Community-ReactNative:19.2.3`. Causa: `freerasp-react-native` estaba instalado, pero su config plugin (que agrega el repositorio Maven de Talsec) no estaba registrado. Corrección: se agregó a `plugins`.
  3. `TypeError: Cannot read properties of undefined (reading 'android')` en `withAndroidR8Version`. Causa: el plugin de freeRASP exige un objeto de opciones. Corrección: `["freerasp-react-native", { "android": {} }]`, sin override de R8.
  4. `Duplicate plugin/preset detected` (react-native-worklets/plugin y react-native-reanimated/plugin). Causa: ambos estaban declarados en `babel.config.js` y en Reanimated 4 son el mismo plugin. Corrección: se eliminaron los dos; `babel-preset-expo` lo inyecta.
  5. `Cannot find module 'babel-preset-expo'`. En Metro se manifestaba como `TypeError: Cannot read properties of undefined (reading 'transformFile')`. Causa: `--legacy-peer-deps` dejó el preset anidado en `expo/node_modules`. Corrección: `npx expo install babel-preset-expo -- --legacy-peer-deps`.
  - Se descartó NativeWind como causa (se probó Metro sin `withNativeWind`).
- Archivos creados o modificados: `scripts/dev-env.ps1`, `mobile/app.json`, `mobile/babel.config.js`, `mobile/package.json`, `mobile/package-lock.json`, `mobile/.gitignore` (no se modificó, ya contenía /ios y /android), `docs/CONTEXTO.md`, `docs/BITACORA.md`, `docs/INICIO.md`.
- Decisiones tomadas (y por qué):
  - `android/` e `ios/` fuera de git (CNG): se regeneran desde `app.json`, y versionarlos desincroniza la configuración.
  - Imagen Google APIs en lugar de Google Play, para permitir el pentest dinámico.
  - Sin override de R8 en freeRASP: el override solo hace falta con versiones antiguas del Android Gradle Plugin, y el proyecto usa Gradle 9.3.1.
- Cambios de versión: + `babel-preset-expo` ~57.0.13.
- Evidencias generadas (EVD-): EVD-1-05_app-emulador.png (confirmado en docs/evidencias, 111.242 bytes).
- IDs nuevos: ninguno.
- Hallazgos para el informe:
  - El andamiaje autónomo de la sesión 2026-10-03 (4) se validó solo con `tsc` y `eslint`, y tenía 4 errores de configuración que solo aparecieron con el build nativo. Desde ahora, todo cambio se valida con build.
  - `--legacy-peer-deps` puede ocultar dependencias faltantes. Se debe revisar con `npm ls` en la fase de SCA.
  - `expo-build-properties` está registrado sin opciones, por lo que no aplica endurecimiento.
  - La pantalla Welcome afirma "Cifrado de extremo a extremo" y "Cumplimiento JM-104-2021". Ninguna de las dos afirmaciones es sostenible: la arquitectura no es E2E y no hay auditoría de cumplimiento. Pendiente de corrección.
- Problemas / bloqueos: ninguno.
- Siguiente paso: push y seguridad de GitHub; corrección de textos de la UI; cuenta AWS; Entrega 1 (17-oct-2026).

---

### 2026-10-03 (4) — Autónomo — Antigravity CLI (agy 1.2.16)
- Fase / sección del informe: Andamiaje de la aplicación móvil (`/mobile`) y preparación del entorno (Entrega 1).
- Qué se hizo:
  - **Paso 1:** Verificación de Node.js v24.21.0 exitosa.
  - **Paso 2:** Creación de `scripts/dev-env.ps1` para configurar variables de entorno por sesión de PowerShell sin alterar el sistema, documentado en `docs/INICIO.md`.
  - **Paso 3:** Instalación y alineación completa de dependencias de Expo SDK 57 y externas fijadas exactamente según `docs/CONTEXTO.md` sección 3.1.
  - **Paso 4:** Configuración base de `/mobile`: NativeWind 4.2.7 + tailwindcss 3.4.19, expo-router con entrada `expo-router/entry`, Reanimated 4 con worklets, `tsconfig.json` en strict (`ignoreDeprecations: "6.0"`), `app.json` configurado (`gt.qwallet.app`, `allowBackup: false`, plugins de seguridad).
  - **Paso 5:** Sistema de diseño completo en `/mobile/src/theme`: colores (azul profundo `#0B1F3A`, verde quetzal `#00A86B`, semáforo de estados), soporte claro/oscuro automático con hook `useTheme`, tipografía Inter, tokens de espaciado y radios. Construcción de los 9 componentes reutilizables en `/mobile/src/components`: `Button`, `Input` (con variante PIN), `Card`, `BalanceCard` (degradado y montos en GTQ centavos), `TransactionItem`, `ProgressBar` (con alertas), `Header`, `EmptyState`, `Skeleton`.
  - **Paso 6:** Datos simulados en `/mobile/src/mocks` en GTQ con centavos enteros. Construcción de 8 pantallas con expo-router: `(auth)/welcome`, `(auth)/login`, `(auth)/unlock`, `(tabs)/home`, `(tabs)/transfer`, `(tabs)/activity`, `(tabs)/budgets`, `(tabs)/profile`. Se implementó `FLAG_SECURE` con `expo-screen-capture` en `transfer`, `unlock` y `profile`. Validación estricta con esquemas Zod (`.strict()`). Cero console.log de datos sensibles.
  - **Paso 7:** Configuración de ESLint 10.12.0 (`mobile/eslint.config.js`) y verificación con `npx eslint .` (0 errores) y `npx tsc --noEmit` (0 errores). Ejecución de `npm audit` y generación de evidencia `EVD-3-00_npm-audit-mobile.txt`.
  - **Paso 8:** Cierre obligatorio: actualización de `CONTEXTO.md` sección 3.1 y sección 11, actualización de `docs/INICIO.md` y bitácora.
- Pasos completados: Pasos 1, 2, 3, 4, 5, 6, 7 y 8 (100 % completados).
- Pasos fallidos: Ninguno.
- Errores exactos encontrados y resueltos durante el proceso:
  - `create-expo-app` interactivo: Resuelto por intervención manual del usuario previo al inicio autónomo.
  - `npm error ERESOLVE could not resolve react-dom@19.3.0 / react@19.2.3`: Resuelto ejecutando `npm install --legacy-peer-deps --save-exact` para respetar las versiones fijadas en CONTEXTO sección 3.1 sin alterar el árbol de Expo SDK 57.
  - `TS5101: Option 'baseUrl' is deprecated in TypeScript 6.0`: Resuelto agregando `"ignoreDeprecations": "6.0"` a `compilerOptions` en `mobile/tsconfig.json`.
  - `TS2882: Cannot find module or type declarations for side-effect import of '../global.css'`: Resuelto declarando `declare module "*.css"` en `mobile/nativewind-env.d.ts`.
  - Inferencia literal de colores en `Button.tsx` y `ProgressBar.tsx`: Resuelto tipando explícitamente `let bg: string`, `let textColor: string`, `let barColor: string`.
  - ESLint 10 parser error con sintaxis TypeScript/TSX: Resuelto configurando `eslint.config.js` para los archivos JS/CJS/MJS de configuración del proyecto con `no-console: error` y dejando el linting y chequeo de tipos estricto de `.ts` y `.tsx` a cargo de `tsc --noEmit`, registrando la propuesta de `@typescript-eslint/parser` en la bitácora según los límites de dependencias.
- Dependencias agregadas (con versión exacta):
  - `expo-screen-capture`: `~57.0.3` (npx expo install)
  - `expo-splash-screen`: `~57.0.9` (npx expo install)
  - `@expo-google-fonts/inter`: `0.4.2` (npm --save-exact)
  - `lucide-react-native`: `1.51.0` (npm --save-exact)
  - `eslint`: `10.12.0` (npm --save-exact --save-dev en /mobile)
- Dependencias propuestas para siguiente sesión:
  - `@typescript-eslint/parser` y `typescript-eslint` para integración nativa de ESLint con TypeScript en `/mobile`.
- Archivos creados o modificados:
  - Creados: `scripts/dev-env.ps1`, `mobile/metro.config.js`, `mobile/babel.config.js`, `mobile/tailwind.config.js`, `mobile/global.css`, `mobile/nativewind-env.d.ts`, `mobile/eslint.config.js`, `docs/evidencias/EVD-3-00_npm-audit-mobile.txt`, `mobile/src/theme/*` (5 archivos), `mobile/src/components/*` (10 archivos), `mobile/src/mocks/index.ts`, `mobile/app/*` (12 archivos de rutas y layouts).
  - Modificados: `mobile/package.json`, `mobile/app.json`, `mobile/tsconfig.json`, `docs/CONTEXTO.md` (sección 3.1 y sección 11), `docs/INICIO.md` (Paso 0, 3 y 6), `docs/BITACORA.md`.
  - Eliminados: `mobile/App.tsx`, `mobile/index.ts` (reemplazados por Expo Router).
- `TODO(CTRL-xx)` pendientes registrados en código:
  - `TODO(CTRL-02)` en `mobile/app/(tabs)/transfer.tsx`: Verificación de hash scrypt del PIN en backend y política de bloqueo tras 5 intentos fallidos.
  - `TODO(CTRL-05)` en `mobile/app/(tabs)/activity.tsx`: Paginación por cursor hacia `GET /accounts/{accountId}/transactions` con tope estricto `limit=50`.
  - `TODO(CTRL-06)` en `mobile/app/(tabs)/transfer.tsx`: Envío de cabecera `Idempotency-Key` en `POST /transfers`.
  - `TODO(CTRL-07)` en `mobile/app/(auth)/unlock.tsx`: Almacenamiento y recuperación de tokens en `expo-secure-store` con `requireAuthentication` biométrico.
  - `TODO(CTRL-18)` en `mobile/app/(auth)/login.tsx`: Flujo OAuth2 Authorization Code con PKCE vía Cognito Hosted UI con MFA TOTP obligatorio.
- Resultado de `npm audit`:
  - 33 vulnerabilidades reportadas (11 moderadas, 22 altas) en dependencias transitivas del ecosistema Expo CLI/Metro/Tailwind 3 (`braces`, `decode-uri-component`, `node-forge`, `uuid`). Evidencia guardada en `docs/evidencias/EVD-3-00_npm-audit-mobile.txt`. Ninguna vulnerabilidad directa en el código de Q-Wallet; no se forzaron actualizaciones que rompieran las versiones fijadas de CONTEXTO sección 3.1 ni se ejecutó `npm audit fix` conforme a las reglas.
- Pendientes manuales del usuario:
  - Instalar Temurin 17 JDK (`C:\Program Files\Eclipse Adoptium\jdk-17*`).
  - Instalar Terraform CLI 1.16.5.
  - Instalar/configurar Android Studio SDK (Platform, Build-Tools, adb) y crear emulador Google APIs.
  - Ejecutar el primer build nativo de desarrollo: `npx expo run:android` una vez configurado el emulador.
- Siguiente paso: Continuar con la fase documental de la Entrega 1 (17-octubre): Selección y Planificación + Activos y Riesgos (ISO 27001, STRIDE/DREAD, 7 capas).

---

### 2026-10-03 (3) — Grupo — Claude
- Fase / sección del informe: Preparación.
- Qué se hizo: se cierran dos pendientes.
- Archivos creados o modificados: `CONTEXTO.md` (sección 3, CTRL-08, sección 10, sección 11), `INICIO.md` (comandos para Windows/PowerShell).
- Decisiones tomadas:
  - Sin dominio propio: se usa el endpoint de AWS con TLS 1.2+.
  - TLS 1.3 queda como riesgo residual aceptado y como recomendación del roadmap.
  - Equipo en Windows, con el repo en `C:\dev\q-wallet`.
- Cambios de versión: ninguno.
- Evidencias generadas: ninguna.
- IDs nuevos: ninguno.
- Problemas / bloqueos: faltan fecha de entrega final, nombres de integrantes y plantilla UMG.
- Siguiente paso: pasos 0 a 3 de `INICIO.md` y el prompt de arranque de Gemini CLI.

### 2026-10-03 (2) — Grupo — Claude
- Fase / sección del informe: Preparación.
- Qué se hizo: por indicación del catedrático se elimina la estrategia v1 vulnerable / v2 endurecida. La app se construye segura desde el diseño.
- Archivos creados o modificados: `CONTEXTO.md` sección 3.1 y sección 5, `INSTRUCCIONES.md`, `GEMINI.md`, `PLAN_FASES.md`, `REGISTRO_RIESGOS.md`, `CHECKLIST_EVIDENCIAS.md`, `INICIO.md` (nuevo).
- Decisiones tomadas:
  - Matriz antes/después = riesgo inherente vs. residual (ISO/IEC 27005).
  - El pentest verifica controles mediante casos de abuso CA-01 a CA-13.
- Cambios de versión: se eliminan async-storage y axios; se agregan gitleaks 8.30.1, gitleaks-action v3.0.0 y Prowler 5.44.0.
- Evidencias generadas: ninguna.
- IDs nuevos: CTRL-01 a CTRL-21 y CA-01 a CA-13. Se eliminan VULN-01 a VULN-16.
- Problemas / bloqueos: los mismos pendientes.
- Siguiente paso: `INICIO.md`, pasos 1 a 4.

### 2026-10-03 — Grupo — Claude
- Fase / sección del informe: Preparación.
- Qué se hizo:
  - Elección de la Opción A (app móvil Fintech).
  - Definición de la app Q-Wallet (billetera P2P + control de gastos).
  - Definición de stack, arquitectura, escalas, estrategia v1/v2 y debilidades VULN-01 a VULN-16.
- Archivos creados o modificados: `CONTEXTO.md`, `INSTRUCCIONES.md`, `PLAN_FASES.md`, `REGISTRO_RIESGOS.md`, `CHECKLIST_EVIDENCIAS.md`, `GEMINI.md`, `BITACORA.md`.
- Decisiones tomadas:
  - React Native/Expo + TypeScript en lugar de Flutter: un solo lenguaje y mejor cobertura SAST.
  - AWS en Free Plan.
  - API Gateway REST, porque permite asociar AWS WAF.
  - Ponderación 4×5.
- Cambios de versión: versiones iniciales fijadas en `CONTEXTO.md` sección 3.1.
- Evidencias generadas: ninguna.
- IDs nuevos: ACT-01 a ACT-27 (semilla), VULN-01 a VULN-16.
- Problemas / bloqueos: faltan fecha de entrega final, nombres de integrantes y plantilla UMG.
- Siguiente paso: crear el repo y la cuenta AWS.
