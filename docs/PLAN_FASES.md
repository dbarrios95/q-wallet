# PLAN POR FASES

Integrantes:
- **I1** — Lead Security Architect
- **I2** — DevSecOps Engineer
- **I3** — Pentester / Analista de Riesgos

Asignar nombres en `CONTEXTO.md`.

---

## ENTREGA 1 — sábado 17-oct-2026

Cubre la hoja de ruta **1. Selección y Planificación** (target, threat modeling, scope) y **2. Activos y Riesgos** (inventario, valor, riesgos ISO 27001, STRIDE/DREAD).
Corresponde a las secciones **0, 1 y 2** del informe Opción A y al criterio de rúbrica **"Análisis de Riesgos y Activos"**.

### Contenido del Word de la Entrega 1

| Sección | Contenido | Resp. |
|---|---|---|
| 0 | Portada UMG, resumen ejecutivo (parcial), índice | I1 |
| 1.1 | Contexto de la aplicación: Q-Wallet, mercado fintech en Guatemala, funciones F1–F7 | I1 |
| 1.2 | Objetivo general + 4–5 específicos (SMART) | I1 |
| 1.3 | Alcance: incluido/excluido, entornos, enfoque seguro desde el diseño, restricciones | I1 |
| 1.4 | Normativas y estándares (CONTEXTO §8), con aplicación concreta de cada uno | I1 |
| 1.5 | Scope técnico: arquitectura, endpoints, fronteras de confianza, herramientas, reglas de enfrentamiento del pentest | I2 |
| 2.1 | Inventario de activos ISO 27001 (todos los campos obligatorios) | I2 |
| 2.2 | Clasificación CIA y criticidad (con cálculo) | I2 |
| 2.3 | Modelado STRIDE sobre el DFD (Threat Dragon), por elemento y frontera | I3 |
| 2.4 | DREAD por amenaza (con cálculo) | I3 |
| 2.5 | Matriz de riesgos inicial: P×I, **capa 1–7**, tipo e impacto de negocio + **heatmap "antes"** | I3 |
| — | Referencias APA 7 | I1 |

**Las 7 capas no tienen sección propia en la estructura del informe.** Se cubren dentro de 2.5 con:
- Una columna "Capa" en la matriz de riesgos.
- Una tabla resumen "riesgos por capa" que tenga al menos un riesgo en **cada** capa. Esto es explícito en la rúbrica.

### Calendario

| Fecha | I1 | I2 | I3 |
|---|---|---|---|
| Sáb 3 – Dom 4 | Repo GitHub + subir docs; consultar al catedrático los pendientes | Cuenta AWS (Free Plan), MFA en root, usuario IAM Identity Center, presupuesto US$5; verificar WAF/ECR | Instalar Threat Dragon; leer STRIDE/DREAD y CONTEXTO §5–6 |
| Lun 5 – Mié 7 | Secciones 1.1–1.4 | Borrador de 2.1 (inventario) + 1.5 | DFD nivel 0 y nivel 1 en Threat Dragon |
| Jue 8 – Sáb 10 | Diagrama de arquitectura con controles (draw.io) para 1.5 | 2.2 (CIA y criticidad) | 2.3 STRIDE en Threat Dragon |
| Dom 11 – Mar 13 | Referencias APA; plantilla Word UMG | Revisión cruzada de 2.3 | 2.4 DREAD + 2.5 matriz + heatmap |
| Mié 14 – Jue 15 | Portada, resumen ejecutivo, índice, ensamblar Word | Revisión cruzada de 1.x | Revisión cruzada de 2.1–2.2 |
| Vie 16 | Una sola revisión con Claude (rúbrica vs. documento); correcciones | ← | ← |
| **Sáb 17** | **Entrega** | | |

### Prompts para Gemini (Gem con INSTRUCCIONES + CONTEXTO)

**P1 — Sección 1**
> Redacta las secciones 1.1 a 1.4 del informe según CONTEXTO.md. 1.1 debe incluir el contexto del sector fintech en Guatemala con fuentes reales (marca [VERIFICAR] si no estás seguro). 1.2: objetivo general y 5 específicos SMART alineados a las 6 fases del enunciado. 1.3: alcance incluido/excluido. 1.4: tabla Norma | Qué regula | Cómo la aplicamos en Q-Wallet.

**P2 — Scope técnico**
> Redacta 1.5 Definición del Scope Técnico: componentes en alcance, endpoints (tabla), fronteras de confianza TB1–TB6, entornos, herramientas por fase y reglas de enfrentamiento (horarios, objetivos permitidos, prohibiciones, contacto).

**P3 — Inventario**
> Genera 2.1: inventario ISO 27001 con columnas ID | Nombre | Proceso asociado | Descripción | Tipo | Ubicación | C | I | D | Valor | Criticidad | Justificación | Propietario | Custodio | Usuarios con acceso. Mínimo 25 activos y los 6 tipos del enunciado. Usa las escalas de CONTEXTO §6.

**P4 — STRIDE**
> Con base en el DFD (elementos: [pegar lista de Threat Dragon]), genera 2.3: tabla AME-ID | Elemento/flujo del DFD | Frontera | Categoría STRIDE | Descripción de la amenaza | Activos afectados (ACT-) | CTRL que la mitiga (CONTEXTO §5). Cubre las 6 categorías STRIDE, todas las amenazas que mitigan CTRL-01 a CTRL-21, más amenazas adicionales de arquitectura (mínimo 30). Valora DREAD **sin controles** (riesgo inherente).

**P5 — DREAD y matriz**
> Para cada AME genera 2.4: D, R, E, A, Di (1–10) con justificación breve y puntaje. Luego 2.5: RSK-ID | AME | P | I | P×I (inherente) | Nivel | Capa (1–7) | Tipo | Impacto de negocio | Tratamiento propuesto preliminar. Agrega la tabla "riesgos por capa" y los datos para el heatmap 5×5 (conteo por celda).

**Regla:** un prompt por conversación. Pegar la salida en el Word y guardar la versión en `/docs/entrega1/`.

### Valor agregado

Opcional, solo si las secciones obligatorias ya están completas:
- **Árbol de ataque** de "transferencia fraudulenta" (va en el anexo de 2.3).
- **Mapeo AME → CAPEC / MITRE ATT&CK Mobile** (columna adicional).
- **Matriz de requisitos de seguridad**: mapeo de amenaza → requisito MASVS v2 (prepara la Fase 2).

---

## ENTREGAS SIGUIENTES (fechas PENDIENTES)

| Fase | Hoja de ruta | Secciones | Trabajo | Herramientas | Terminado cuando |
|---|---|---|---|---|---|
| A. Construcción segura | 2 | 1.5, 4.1–4.5 | App Expo, 5 Lambdas y Terraform con CTRL-01 a CTRL-21 | Gemini CLI, Terraform | La app funciona contra AWS y cada CTRL tiene su prueba unitaria |
| B. DevSecOps | 3 | 3.4, 3.5, 4.6 | Pipeline con SAST, SCA, IaC y contenedores | Semgrep, CodeQL, SonarQube Cloud, Dependency-Check, Snyk, Trivy, Checkov | Pipeline en verde; los hallazgos reales se registran como HAL |
| C. Evaluación | 3 | 3.1–3.3, 3.6 | Caja negra y caja gris/blanca: ejecutar cada caso de abuso contra los controles, más OWASP API Top 10 y mapeo del perímetro | ZAP, Burp CE, Postman, Nmap, MobSF, Frida/objection, Prowler | Cada caso de abuso con evidencia de bloqueo; HAL reales registrados |
| D. Corrección | 4 | 4.2, 4.6 | Corregir HAL reales y hacer re-test | Todas | Cada HAL cerrado con evidencia |
| E. Operación | 5 | 5.1–5.6 | WAF activo, freeRASP, Wazuh con alertas y dashboard, heatmap residual ("después"), tratamiento | AWS WAF, freeRASP, Wazuh | Ataques de C bloqueados o alertados |
| F. Cierre | 6 | 6.1–6.6, 0 | Dictamen, roadmap, lecciones, anexos, presentación | Word, PowerPoint | Informe completo |
