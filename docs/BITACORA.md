# BITÁCORA DEL PROYECTO — Q-Wallet

> Entradas nuevas **arriba**. Una por sesión de trabajo.
> El resumen vigente está en `CONTEXTO.md` §11; aquí queda el historial.

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

### 2026-10-03 (3) — Grupo — Claude
- Fase / sección del informe: Preparación.
- Qué se hizo: se cierran dos pendientes.
- Archivos creados o modificados: `CONTEXTO.md` (§3, CTRL-08, §10, §11), `INICIO.md` (comandos para Windows/PowerShell).
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
- Archivos creados o modificados: `CONTEXTO.md` §3.1 y §5, `INSTRUCCIONES.md`, `GEMINI.md`, `PLAN_FASES.md`, `REGISTRO_RIESGOS.md`, `CHECKLIST_EVIDENCIAS.md`, `INICIO.md` (nuevo).
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
- Cambios de versión: versiones iniciales fijadas en `CONTEXTO.md` §3.1.
- Evidencias generadas: ninguna.
- IDs nuevos: ACT-01 a ACT-27 (semilla), VULN-01 a VULN-16.
- Problemas / bloqueos: faltan fecha de entrega final, nombres de integrantes y plantilla UMG.
- Siguiente paso: crear el repo y la cuenta AWS.
