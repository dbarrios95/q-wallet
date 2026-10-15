# ENTREGA 1 — Selección y Planificación + Activos y Riesgos

> Archivo de trabajo de la Entrega 1. Lo leen el chat de Claude (proyecto en claude.ai) y Claude Code.
> Fuente de verdad: `docs/CONTEXTO.md`. Si algo aquí contradice CONTEXTO, manda CONTEXTO.
> Se actualiza al cerrar cada sesión (tabla de la sección 4 y la sección 7).

---

## 1. Qué se entrega

| Campo | Valor |
|---|---|
| Fecha | **Sábado 17-oct-2026** |
| Fases de la hoja de ruta | **1. Selección y Planificación** (target, threat modeling, scope) y **2. Activos y Riesgos** (inventario, valor, riesgos ISO 27001, STRIDE/DREAD) |
| Secciones del informe | 0, 1 y 2 (Opción A) |
| Criterio de rúbrica | Análisis de Riesgos y Activos (4 pts) |
| Productos | Contenido de las fases **1. Selección y Planificación** y **2. Activos y Riesgos** = secciones **0, 1 y 2** del informe. Se presenta al catedrático como **presentación de avance** (resumen explicativo para revisión); el Word de las secciones 0–2 es la base de la presentación |
| Enfoque | Primero se produce el contenido de las secciones 0–2; la presentación lo resume al final. No se trabaja nada de las fases 3 en adelante hasta el 17 |

### Lo que la presentación debe cubrir (indicación del catedrático)

| # | Punto | De dónde sale |
|---|---|---|
| P-1 | **Objetivos** | Sección 1.2 (general + específicos SMART) |
| P-2 | **Resultados** | Secciones 2.1–2.5: inventario, amenazas STRIDE, DREAD, matriz y heatmap inherente, riesgos por capa |
| P-3 | **Cómo llegamos a ese resultado** | Metodología: ISO/IEC 27005 → inventario ISO 27001 → DFD (Threat Dragon) → STRIDE por elemento y frontera → DREAD → P×I. Escalas de CONTEXTO sección 6 |
| P-4 | **Proyección** | Riesgo residual esperado por amenaza (campo *mitigation* del threat model) → heatmap "después" proyectado. Qué riesgos quedan aceptados (RSK-01 y RSK-31; desde el 15-oct TLS 1.3 ya no es riesgo aceptado) |
| P-5 | **Cronograma** | Fases A–F de `PLAN_FASES.md` con fechas (la entrega final está PENDIENTE) |
| P-6 | **Cómo lo vamos a implementar** | Arquitectura AWS (CONTEXTO sección 4), controles CTRL-01 a CTRL-23, pipeline DevSecOps, verificación con casos de abuso CA-01 a CA-13 |

Orden sugerido de diapositivas: portada → contexto Q-Wallet → objetivos → alcance → metodología → resultados → proyección → implementación → cronograma → cierre. ~12–15 diapositivas.

### Identidad visual de la presentación

No hay lineamientos del catedrático (formato, duración ni plantilla). Se usa la paleta de la app (`mobile/src/theme/colors.ts`) para que la presentación y Q-Wallet se vean como un mismo producto.

| Uso | Color | Hex |
|---|---|---|
| Fondo de portada y diapositivas de sección | Azul profundo | `#0B1F3A` |
| Fondo de diapositivas de contenido | Gris 50 | `#F8FAFC` |
| Texto principal | Gris 900 | `#0F172A` |
| Texto secundario | Gris 500 | `#64748B` |
| Acento (títulos destacados, íconos, líneas) | Verde quetzal | `#00A86B` |
| Acento sobre fondo oscuro | Verde claro | `#00D688` |
| Bordes y tablas | Gris 200 | `#E2E8F0` |

Heatmap y niveles de riesgo (semáforo de la app):

| Nivel | Hex |
|---|---|
| Bajo (1–4) | `#10B981` |
| Medio (5–9) | `#F59E0B` |
| Alto (10–14) | `#F97316` (no está en la app; se agrega solo para el heatmap) |
| Crítico (15–25) | `#EF4444` |

Reglas:
- Tipografía **Inter** (la misma de la app); si no está instalada, Arial.
- Formato 16:9. Duración asumida ~15 min `[VERIFICAR]`.
- **No poner texto blanco pequeño sobre el verde `#00A86B`**: el contraste es de aprox. 3:1 y no se lee (es el mismo problema del badge de la pantalla Welcome). El verde va en acentos o texto grande.
- En el heatmap, cada celda lleva además el número de riesgos, para que no dependa solo del color.
- Las capturas de la app se toman **después** de corregir los textos falsos de Welcome (sección 6), o no se usan.

---

## 2. Estructura del Word (secciones 0–2)

| Sección | Contenido | Fuente / insumo |
|---|---|---|
| 0 | Portada UMG, resumen ejecutivo (parcial), índice | Plantilla UMG (PENDIENTE confirmar si existe) |
| 1.1 | Contexto: Q-Wallet, fintech en Guatemala, funciones F1–F7 | CONTEXTO sección 2 + fuentes reales |
| 1.2 | Objetivo general + 5 específicos SMART | Alineados a los 5 componentes de la rúbrica (fases 1 y 2 juntas en OE1) |
| 1.3 | Alcance incluido/excluido, enfoque seguro desde el diseño, restricciones | CONTEXTO sección 2, sección 5 |
| 1.4 | Normativas: tabla Norma / Qué regula / Cómo se aplica | CONTEXTO sección 8 |
| 1.5 | Scope técnico: arquitectura (Figura 1), superficie API (Tabla 7), fronteras TB1–TB6 (Tabla 8), controles por componente (Tabla 9), herramientas (Tabla 10), reglas de enfrentamiento y revisión CA (Tabla 11) | `docs/entregas/Entrega1_Seccion_1-5_Scope_Tecnico.docx` |
| 2.1 | Inventario ISO 27001 (≥25 activos, 6 tipos, todos los campos) | `REGISTRO_RIESGOS.md` sección A (semilla ACT-01–25) |
| 2.2 | Clasificación CIA y criticidad con cálculo | CONTEXTO sección 6 |
| 2.3 | STRIDE sobre el DFD, por elemento y frontera | `docs/threat-model/T2_QWallet_ThreatModel.json` |
| 2.4 | DREAD por amenaza con cálculo | Threat model (D R E A Di en cada AME) |
| 2.5 | Matriz P×I, capa 1–7, tipo, impacto de negocio, tratamiento + heatmap "antes" + tabla riesgos por capa | Threat model |
| — | Referencias APA 7 (solo fuentes reales y verificables) | |

Formato (15-oct): Times New Roman; fuera de tablas interlineado doble, 0 pt antes y 8 pt después; en tablas 1.5, 0/0 pt; sangría 1.27 cm, márgenes 2.54 cm, justificado (CONTEXTO, sección 9; `scripts/entrega1_estilos.py`). Tablas y figuras numeradas APA 7.

Numeración en curso: 1.1–1.4 usa Tablas 1–6 (sin figuras). **1.5 usa Figura 1 y Tablas 7–11.** La numeración de 2.x continúa desde Tabla 11 / Figura 1.

---

## 3. Resultados ya disponibles (threat model T2 v2, PR #8, 09-oct)

Extraídos del JSON de Threat Dragon. Volver a calcular si el modelo cambia.

| Dato | Valor |
|---|---|
| DFD | Nivel 0 (contexto), Nivel 1 (componentes, TB1–TB6), Nivel 2 (transferencia P2P) |
| Amenazas | **41** (AME-01 a AME-41) + 14 justificaciones N/A de STRIDE por elemento |
| Por STRIDE | Information disclosure 13 · Tampering 9 · Spoofing 6 · DoS 5 · Elevation 5 · Repudiation 3 |
| Riesgo inherente | Crítico 18 · Alto 12 · Medio 11 · Bajo 0 |
| Residual esperado | Alto 1 · Medio 26 · Bajo 14 |
| Por capa | 1: 8 · 2a: 5 · 2b: 11 · 2c: 1 · 2d: 3 · 3: 3 · 4: 2 · 5: 2 · 6: 2 · 7: 4 → **las 7 capas cubiertas** (10 con la capa 2 dividida en 2a–2d) |

Revisado el 12-oct (sección 2.5.5 del Word): el residual Alto es RSK-32 (pipeline); no se acepta y tiene plan de refuerzo de CTRL-21 (entorno protegido con aprobación de un segundo integrante, OIDC limitado a ese entorno y a `main`, rol de despliegue mínimo) → esperado P1×I5 = 5. Ningún inherente Bajo no es efecto del redondeo: con redondeo al más cercano solo AME-41 sería Bajo. Residual calculado con `scripts/heatmap_riesgo.py` (EVD-2-07).

---

## 4. Estado por sección

`☐` sin iniciar · `◐` en curso · `☑` listo · `✔` revisado

| Sección | Estado | Archivo / nota |
|---|---|---|
| 0 Portada / resumen / índice | ☑ | `docs/entregas/Entrega1_Seccion_0_Portada_Resumen_Indice.docx` (3 págs.). Portada APA 7 de estudiante (no hay plantilla UMG). Resumen ejecutivo de 1 página con cifras verificadas por script. Índice como campo TOC con páginas medidas: se actualiza al ensamblar |
| 1.1 Contexto | ✔ | `docs/entregas/Entrega1_Secciones_1-1_a_1-4.docx`. Cifras Findex por fuente secundaria `[VERIFICAR]` (único marcador del Word; 23 % sin fuente primaria al 15-oct). **15-oct:** el problema dice "un control o una decisión de tratamiento justificada (AME-01)" |
| 1.2 Objetivos | ✔ | OE1–OE5 + Tabla 2 SMART. OE4 = 23 controles; OE3 = 13 casos (CA-01 a CA-13). **15-oct:** sin [FECHA PENDIENTE]; plazo de OE2–OE5 = "Entrega final" con nota; frase que presenta la Tabla 2 |
| 1.3 Alcance | ✔ | Restricciones de la política de pentest de AWS. **15-oct:** frase que presenta la Tabla 5; fila "Sin dominio propio" con TLS 1.3 (TLS 1.2 de respaldo) |
| 1.4 Normativas | ✔ | Tabla 6 (11 normas). JM-98-2025 "con referencia a", por fuente secundaria (el PDF figura en el índice de Banguat pero no abre). **15-oct:** [VERIFICAR] de la SIB → fuera del alcance; iniciativa 6464 con fechas (presentada 29-oct-2024, sin dictamen a jul-2026; nada nuevo al 15-oct) |
| 1.5 Scope técnico | ✔ | Figura 1 y Tablas 7–11. **15-oct (revisión de Paco):** Figura 1 en página horizontal, sin título incrustado, con nodo AWS IAM (CTRL-12, CTRL-21) y tildes; 1.5.1 con TLS 1.3 (`SecurityPolicy_TLS13_1_2_2021_06`); "Tres infringen... uno en el límite (CA-06)"; notas de Tablas 7, 9 y 10 sin CONTEXTO; Tabla 8 aclara rótulos de fronteras; Tabla 9 = Tabla 7 por servicio (svc-profile, svc-transfers, svc-admin), CTRL-15 en capa 3 y fila de capa 6; Tabla 10 MobSF "Análisis de la app (APK)"; nota de Tabla 11 explica CA-14/CA-16 y CA-15. Falta EVD-1-02 y EVD-1-03 **15-oct (revisión de 1.5):** objetivos del pentest solo WAF, API Gateway y Lambda; MASTG; Tabla 7 block con CTRL-23; Tabla 8 TB3 con CTRL-03/05; Tabla 9 API Gateway capa 2d/5 |
| 2.1 Inventario | ✔ | Tabla 12: 28 activos. **15-oct:** intro de 2 cita el repo público del modelo T2; Gerente de Producto aclarado como rol ficticio sin integrante |
| 2.2 CIA y criticidad | ☑ | Tablas 13–15: criterios, cálculo C+I+D por activo y distribución. Crítica 11 · Alta 13 · Media 4 · Baja 0 |
| 2.3 STRIDE | ✔ | Tablas 16–18, Figuras 2–4. **15-oct:** Tabla 17 AME-01 "— (riesgo aceptado)" y AME-31 "CTRL-20 (solo CloudTrail; riesgo aceptado)"; Tabla 18 retitulada "Categorías STRIDE revisadas sin amenaza separada", admin → AME-06 y CTRL-18, SSM → AME-27 (igual en el JSON) |
| 2.4 DREAD | ✔ | Tablas 19–20. Alta 15 · Media 26 · Baja 0. **15-oct:** aclaración de que DREAD, P×I y CIA son escalas distintas |
| 2.5 Matriz + heatmap + capas | ☑ | Tabla 21 (RSK-01..41 con P, I, nivel, capa, tipo, impacto, tratamiento), Figura 5 (EVD-2-05), Tabla 22 (riesgos por capa, las 10 capas cubiertas). Mitigar 39 · Aceptar 2 (**15-oct:** RSK-01 pasa de Transferir a Aceptar). **2.5.5 nueva:** Figura 6 (EVD-2-07, residual proyectado: Alto 1 · Medio 26 · Bajo 14), Tabla 23 (inherente vs. residual por RSK, suma 580 → 207), criterio de aceptación del riesgo, plan para RSK-32 y defensa de "ningún inherente Bajo". **Correcciones de la revisión:** 2.5.1 explica que el impacto mide lo que la amenaza le hace al activo (8 AME sobre activos Críticos con I ≤ 3, ejemplo AME-14); Tabla 21 con rótulo APA (faltaba), página horizontal y columna "Dueño del riesgo" (Lead Security Architect 28 · Gerente de Producto 13; **13-oct:** RSK-02 pasa de Cliente a Gerente de Producto y 2.5.2 lo explica), criterio en 2.5.2  **15-oct:** Figuras 5 y 6 sin título incrustado; "15 en P1×I5: 14 + RSK-01"; seguimiento de RSK-31 por revisión semanal de CloudTrail; plan de RSK-32 "antes del primer despliegue"; párrafo de cierre (conclusión provisional, sin sección 3) |
| Referencias APA | ☑ | `docs/entregas/Entrega1_Referencias.docx`: 24 referencias APA 7 unificadas (orden alfabético, "y", "s. f.", sufijos a/b/c). Resueltos los `[VERIFICAR]` de URL: JM-104-2021 y Decreto 67-2001 en Banguat, Decreto 57-2008 en SVET. **JM-104-2021 derogada por JM-98-2025 (decisión pendiente)**. Findex 23 % sin fuente primaria. Al ensamblar: AWS (s. f.-a/b/c), MASVS = OWASP Mobile Application Security Project (2024) y ISO "e" en lugar de "&" en las citas del texto; 1.5 no tiene citas en el texto |
| **Word final ensamblado** | ✔ | `docs/entregas/Entrega1_Informe_QWallet.docx` (**67 págs.** con el formato nuevo: Times New Roman, doble 0/8 pt y tablas 1.5 0/0 pt; validado y renderizado completo; índice actualizado). Generado con `scripts/entrega1_ensamblar.py` → `scripts/entrega1_revision_paco.py` → `scripts/entrega1_estilos.py` → `scripts/entrega1_indice.py`. Queda 1 `[VERIFICAR]` (Findex 23 %). El resumen ejecutivo ocupa ahora 2 páginas y el índice 2 por el interlineado doble |
| Presentación P-1 a P-6 | ◐ | Claude Slides (14 diapositivas). Faltan: JM-98-2025; EVD-2-07 en P-4 junto a EVD-2-05 (usar los PNG nuevos sin título); CTRL-23 en controles; **RSK-01 Aceptar (Mitigar 39 · Aceptar 2)**; TLS 1.3 ya no es "riesgo aceptado"; Figura 1 nueva con IAM; "14 categorías sin amenaza separada" |

---

## 5. Cronograma (10 → 17 oct)

| Día | Tarea (una por chat) |
|---|---|
| Sáb 10 | Sección 1.1–1.4: contexto, objetivos SMART, alcance, normativas. **1.5 scope técnico + diagrama (hecho el 10)** |
| Dom 11 | Holgura / revisión de 1.x |
| Lun 12 | Sección 2.1–2.2: inventario ISO 27001 con CIA y criticidad |
| Mar 13 | Sección 2.3–2.5: tablas STRIDE/DREAD, matriz, heatmap antes y proyectado, riesgos por capa + capturas de los 3 DFD |
| Mié 14 | Sección 0 (portada, resumen ejecutivo, índice) + referencias APA + ensamblar Word |
| Jue 15 | Presentación de avance (P-1 a P-6) a partir del Word, con la paleta de la app |
| Vie 16 | Revisión final contra la rúbrica y correcciones |
| **Sáb 17** | **Entrega** |

---

## 6. Reglas de trabajo para esta entrega

- **Una tarea por chat.** Al cerrar: actualizar sección 4 de este archivo, sección 11 de CONTEXTO y una entrada en BITÁCORA.
- Todo cambio al repo por rama + PR (`main` protegida).
- Ningún dato inventado: cifras del mercado y normas con fuente real; si no se puede verificar, marcar `[VERIFICAR]`.
- No afirmar "cumplimiento" de JM-98-2025 (antes JM-104-2021): usar "diseñado con referencia a".
- La pantalla Welcome de la app todavía dice "cifrado de extremo a extremo" y "cumplimiento JM-104-2021": no usar capturas de esa pantalla hasta corregirla.
- Las cifras de sección 3 salen del JSON, no se escriben a mano.

---

## 7. Pendientes que afectan esta entrega

- [ ] ¿Existe plantilla oficial UMG?
- [x] Nombres de integrantes y roles: asignados en CONTEXTO sección 1 y 9 (I1 Lead Security Architect = Barrios Monzón; I2 DevSecOps = Sandoval Monterroso; I3 Pentester = Lolmet Calel).
- [x] Catedrático: Osberto Saúl Gallo Orozco (confirmado).
- [ ] Fecha de entrega final (necesaria para el cronograma P-5).
- [x] Formato de la presentación: sin lineamientos; se usa la paleta de la app (sección 1). Duración `[VERIFICAR]`.
- [x] Registrar en BITÁCORA el threat model T2 v1/v2 (entrada 2026-10-10).
- [x] Revisar los casos de abuso CA-xx vs. la política de pentest de AWS: **hecho en 1.5 (Tabla 11)**. Rediseñar CA-02, CA-03, CA-12; matizar CA-06, CA-13; los nuevos CA-14 y CA-16 también chocan. Falta aplicarlo al ejecutar.
- [x] **Sincronizar el repo de GitHub con el proyecto:** el `.docx` de 1.1–1.4 se sube el 13-oct (rama `docs/entrega1-seccion0-referencias`).
- [~] Verificar en fuente primaria: URL de JM-104-2021 y de los Decretos 67-2001 y 57-2008 **resueltas el 13-oct**; Findex 38 % coincide con el Banco Mundial, **23 % sin confirmar**; JM-98-2025 adoptada el 14-oct; **falta su texto oficial**. (OWASP Top 10:2025 en 1.5: confirmada el 12-oct.)
- [x] 1.2: OE4 corregido a 23 controles; OE3 se mantiene en 13 casos (catálogo vigente) con el diseño de la Tabla 11 (14-oct).
- [ ] Confirmar el título exacto de la sección 1 en el enunciado (se usó "1. Selección y Planificación").
- [x] 1.5: "Cuatro requieren rediseño" corregido (15-oct).
- [x] Notas de las Tablas 7, 9 y 10 sin CONTEXTO (15-oct).
- [x] Revisión de 1.5, 2.1 y 2.2 (hecha por Claude el 15-oct a pedido de Daniel; Katherine las lee para exponer).
- [~] EVD-1-03: `EVD-1-03a` (consola), `EVD-1-03b` (MFA), `EVD-1-03c` (presupuesto `qwallet-presupuesto-5usd`, US$5, con fecha 15/10/2026) y `EVD-1-03d` (plan gratuito: US$100 de crédito, vence el 15-abr-2027). Solo falta confirmar que el MFA es del usuario raíz.
- [ ] Findex 23 %: único `[VERIFICAR]`.
