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
| P-4 | **Proyección** | Riesgo residual esperado por amenaza (campo *mitigation* del threat model) → heatmap "después" proyectado. Qué riesgos quedan aceptados (ej. TLS 1.3) |
| P-5 | **Cronograma** | Fases A–F de `PLAN_FASES.md` con fechas (la entrega final está PENDIENTE) |
| P-6 | **Cómo lo vamos a implementar** | Arquitectura AWS (CONTEXTO sección 4), controles CTRL-01 a CTRL-22, pipeline DevSecOps, verificación con casos de abuso CA-01 a CA-13 |

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

Formato: Arial 12, interlineado 1.5, sangría 1.27 cm, márgenes 2.54 cm, justificado. Tablas y figuras numeradas APA 7.

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
| 0 Portada / resumen / índice | ☐ | |
| 1.1 Contexto | ☑ | `docs/entregas/Entrega1_Secciones_1-1_a_1-4.docx`. Cifras Findex por fuente secundaria `[VERIFICAR]` |
| 1.2 Objetivos | ☑ | OE1–OE5 + Tabla 2 SMART. Plazos OE2–OE5 = fecha final PENDIENTE |
| 1.3 Alcance | ☑ | Incluye restricciones de la política de pentest de AWS (sin DoS ni inundación; Cognito no autorizado) |
| 1.4 Normativas | ☑ | Tabla 6 (11 normas). JM-104 "con referencia a". OWASP Top 10:2025 |
| 1.5 Scope técnico | ☑ | `docs/entregas/Entrega1_Seccion_1-5_Scope_Tecnico.docx`. Figura 1 (diagrama con TB1–TB6 y 22 controles, `EVD-1-01` PNG+SVG), Tablas 7–11, reglas de enfrentamiento y revisión CA vs política AWS. Falta EVD-1-02 (estructura del repo) y EVD-1-03 (cuenta AWS). **12-oct (revisión):** Tabla 9 con fila CTRL-23 (personal de soporte, capa 7); Nota de la Figura 1 aclara que CTRL-23 es de procedimiento y no se dibuja; texto de 1.5.4 dice "veintitrés controles" |
| 2.1 Inventario | ☑ | `docs/entregas/Entrega1_Seccion_2_Activos_Riesgos.docx`. Tabla 12: 28 activos (semilla 27 + ACT-28 SIEM Wazuh), 6 tipos, 15 campos. ACT-27 renombrado "Alineación regulatoria (referencia JM-104-2021)". ACT-09 con `[VERIFICAR]` (backend de Terraform no definido) |
| 2.2 CIA y criticidad | ☑ | Tablas 13–15: criterios, cálculo C+I+D por activo y distribución. Crítica 11 · Alta 13 · Media 4 · Baja 0 |
| 2.3 STRIDE | ☑ | Tablas 16–18 (distribución STRIDE, catálogo de 41 AME, 14 N/A justificadas). Figuras 2–4 con las capturas EVD-2-01/02/03 (Threat Dragon 2.6.2); Figuras 3 y 4 en página horizontal por legibilidad. AME-03 con CTRL-23 en la Tabla 17 y su Nota (CTRL-01 a CTRL-23) |
| 2.4 DREAD | ☑ | Tablas 19–20 (criterios por factor y DREAD de 41 AME con justificación). Alta 15 · Media 26 · Baja 0 |
| 2.5 Matriz + heatmap + capas | ☑ | Tabla 21 (RSK-01..41 con P, I, nivel, capa, tipo, impacto, tratamiento), Figura 5 (EVD-2-05), Tabla 22 (riesgos por capa, las 10 capas cubiertas). Mitigar 39 · Transferir 1 · Aceptar 1. **2.5.5 nueva:** Figura 6 (EVD-2-07, residual proyectado: Alto 1 · Medio 26 · Bajo 14), Tabla 23 (inherente vs. residual por RSK, suma 580 → 207), criterio de aceptación del riesgo, plan para RSK-32 y defensa de "ningún inherente Bajo". **Correcciones de la revisión:** 2.5.1 explica que el impacto mide lo que la amenaza le hace al activo (8 AME sobre activos Críticos con I ≤ 3, ejemplo AME-14); Tabla 21 con rótulo APA (faltaba), página horizontal y columna "Dueño del riesgo" (Lead Security Architect 28 · Gerente de Producto 12 · Cliente 1), criterio en 2.5.2 |
| Referencias APA | ◐ | 17 referencias de 1.1–1.4 + referencias nuevas de 1.5 (reales). 3 con `[VERIFICAR]` (JM-104, Decretos). OWASP Top 10:2025 en 1.5 confirmada el 12-oct. Sección 2: 9 referencias reales, sin `[VERIFICAR]` |
| Presentación P-1 a P-6 | ◐ | Presentación de avance en Claude Slides (14 diapositivas, exportable a PDF). Cubre P-1 a P-6. Falta poner EVD-2-07 en la diapositiva de proyección (P-4) junto a EVD-2-05. Diapositiva de controles: agregar CTRL-23 |

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
- No afirmar "cumplimiento" de JM-104-2021: usar "diseñado con referencia a".
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
- [ ] **Sincronizar el repo de GitHub con el proyecto:** el repo va en 05-oct; faltan subir las entradas del 10-oct, los cambios de CONTEXTO, el `.docx` de 1.1–1.4 y los de 1.5.
- [ ] Verificar en fuente primaria: fecha y URL de JM-104-2021 (SIB), cifras Global Findex 2025 de Guatemala (38 % / 23 %), URL oficial de los Decretos 67-2001 y 57-2008. (OWASP Top 10:2025 en 1.5: confirmada el 12-oct.)
- [ ] Confirmar el título exacto de la sección 1 en el enunciado (se usó "1. Selección y Planificación").
