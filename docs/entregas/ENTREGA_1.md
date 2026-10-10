# ENTREGA 1 — Selección y Planificación + Activos y Riesgos

> Archivo de trabajo de la Entrega 1. Lo leen el chat de Claude (proyecto en claude.ai) y Claude Code.
> Fuente de verdad: `docs/CONTEXTO.md`. Si algo aquí contradice CONTEXTO, manda CONTEXTO.
> Se actualiza al cerrar cada sesión (tabla §4 y §7).

---

## 1. Qué se entrega

| Campo | Valor |
|---|---|
| Fecha | **Sábado 17-oct-2026** |
| Fases de la hoja de ruta | **1. Selección y Planificación** (target, threat modeling, scope) y **2. Activos y Riesgos** (inventario, valor, riesgos ISO 27001, STRIDE/DREAD) |
| Secciones del informe | 0, 1 y 2 (Opción A) |
| Criterio de rúbrica | Análisis de Riesgos y Activos (4 pts) |
| Productos | 1) Word formato UMG + APA 7. 2) **Presentación** (sin demo en vivo) |

### Lo que la presentación debe cubrir (indicación del catedrático)

| # | Punto | De dónde sale |
|---|---|---|
| P-1 | **Objetivos** | Sección 1.2 (general + específicos SMART) |
| P-2 | **Resultados** | Secciones 2.1–2.5: inventario, amenazas STRIDE, DREAD, matriz y heatmap inherente, riesgos por capa |
| P-3 | **Cómo llegamos a ese resultado** | Metodología: ISO/IEC 27005 → inventario ISO 27001 → DFD (Threat Dragon) → STRIDE por elemento y frontera → DREAD → P×I. Escalas de CONTEXTO §6 |
| P-4 | **Proyección** | Riesgo residual esperado por amenaza (campo *mitigation* del threat model) → heatmap "después" proyectado. Qué riesgos quedan aceptados (ej. TLS 1.3) |
| P-5 | **Cronograma** | Fases A–F de `PLAN_FASES.md` con fechas (la entrega final está PENDIENTE) |
| P-6 | **Cómo lo vamos a implementar** | Arquitectura AWS (CONTEXTO §4), controles CTRL-01 a CTRL-21, pipeline DevSecOps, verificación con casos de abuso CA-01 a CA-13 |

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
- Las capturas de la app se toman **después** de corregir los textos falsos de Welcome (§6), o no se usan.

---

## 2. Estructura del Word (secciones 0–2)

| Sección | Contenido | Fuente / insumo |
|---|---|---|
| 0 | Portada UMG, resumen ejecutivo (parcial), índice | Plantilla UMG (PENDIENTE confirmar si existe) |
| 1.1 | Contexto: Q-Wallet, fintech en Guatemala, funciones F1–F7 | CONTEXTO §2 + fuentes reales |
| 1.2 | Objetivo general + 5 específicos SMART | Alineados a las 6 fases |
| 1.3 | Alcance incluido/excluido, enfoque seguro desde el diseño, restricciones | CONTEXTO §2, §5 |
| 1.4 | Normativas: tabla Norma / Qué regula / Cómo se aplica | CONTEXTO §8 |
| 1.5 | Scope técnico: arquitectura, endpoints, TB1–TB6, herramientas, reglas de enfrentamiento | CONTEXTO §3–4 |
| 2.1 | Inventario ISO 27001 (≥25 activos, 6 tipos, todos los campos) | `REGISTRO_RIESGOS.md` §A (semilla ACT-01–25) |
| 2.2 | Clasificación CIA y criticidad con cálculo | CONTEXTO §6 |
| 2.3 | STRIDE sobre el DFD, por elemento y frontera | `docs/threat-model/T2_QWallet_ThreatModel.json` |
| 2.4 | DREAD por amenaza con cálculo | Threat model (D R E A Di en cada AME) |
| 2.5 | Matriz P×I, capa 1–7, tipo, impacto de negocio, tratamiento + heatmap "antes" + tabla riesgos por capa | Threat model |
| — | Referencias APA 7 (solo fuentes reales y verificables) | |

Formato: Arial 12, interlineado 1.5, sangría 1.27 cm, márgenes 2.54 cm, justificado. Tablas y figuras numeradas APA 7.

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
| Por capa | 1: 8 · 2a: 5 · 2b: 11 · 2c: 1 · 2d: 3 · 3: 3 · 4: 2 · 5: 2 · 6: 2 · 7: 4 → **las 7 capas cubiertas** |

Pendiente de revisar: el 1 riesgo residual Alto (justificar o reforzar el control) y que ninguno sea Bajo inherente (¿está bien calibrado?).

---

## 4. Estado por sección

`☐` sin iniciar · `◐` en curso · `☑` listo · `✔` revisado

| Sección | Estado | Archivo / nota |
|---|---|---|
| 0 Portada / resumen / índice | ☐ | |
| 1.1 Contexto | ☐ | |
| 1.2 Objetivos | ☐ | |
| 1.3 Alcance | ☐ | |
| 1.4 Normativas | ☐ | |
| 1.5 Scope técnico | ☐ | Falta diagrama de arquitectura con controles |
| 2.1 Inventario | ◐ | Semilla de 25 activos sin CIA ni campos completos |
| 2.2 CIA y criticidad | ☐ | |
| 2.3 STRIDE | ☑ | Threat model v2 (41 AME). Faltan capturas EVD de los 3 DFD |
| 2.4 DREAD | ◐ | Valores en el JSON; falta pasarlos a tabla con justificación |
| 2.5 Matriz + heatmap + capas | ◐ | Datos en el JSON; falta tabla y heatmap |
| Referencias APA | ☐ | |
| Presentación P-1 a P-6 | ☐ | |

---

## 5. Cronograma (10 → 17 oct)

| Día | Tarea (una por chat) |
|---|---|
| Sáb 10 | Sección 1 completa (1.1–1.4) |
| Dom 11 | 1.5 + diagrama de arquitectura con controles |
| Lun 12 | 2.1 + 2.2 (inventario con CIA) |
| Mar 13 | 2.4 + 2.5 (tablas DREAD, matriz, heatmap antes y proyectado, riesgos por capa) + capturas de los DFD |
| Mié 14 | Ensamblar Word UMG + referencias APA |
| Jue 15 | Presentación (P-1 a P-6) |
| Vie 16 | Revisión final contra la rúbrica y correcciones |
| **Sáb 17** | **Entrega** |

---

## 6. Reglas de trabajo para esta entrega

- **Una tarea por chat.** Al cerrar: actualizar §4 de este archivo, §11 de CONTEXTO y una entrada en BITÁCORA.
- Todo cambio al repo por rama + PR (`main` protegida).
- Ningún dato inventado: cifras del mercado y normas con fuente real; si no se puede verificar, marcar `[VERIFICAR]`.
- No afirmar "cumplimiento" de JM-104-2021: usar "diseñado con referencia a".
- La pantalla Welcome de la app todavía dice "cifrado de extremo a extremo" y "cumplimiento JM-104-2021": no usar capturas de esa pantalla hasta corregirla.
- Las cifras de §3 salen del JSON, no se escriben a mano.

---

## 7. Pendientes que afectan esta entrega

- [ ] ¿Existe plantilla oficial UMG?
- [ ] Nombres de integrantes y roles (portada y tabla de responsables).
- [ ] Fecha de entrega final (necesaria para el cronograma P-5).
- [x] Formato de la presentación: sin lineamientos; se usa la paleta de la app (§1). Duración `[VERIFICAR]`.
- [ ] Registrar en BITÁCORA el threat model T2 v1/v2 (PR #8 no tiene entrada).
