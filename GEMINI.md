# GEMINI.md

Lee antes de cualquier tarea:
1. `docs/CONTEXTO.md` — decisiones, stack, escalas e IDs. Manda sobre todo lo demás.
2. `docs/INSTRUCCIONES.md` — reglas de trabajo.
3. `docs/PLAN_FASES.md` — fase actual y criterio de terminado.

## Reglas de código
- TypeScript `strict` en `/mobile` y `/services`. Node.js 24.21.0.
- Usar **exactamente** las versiones de `docs/CONTEXTO.md` §3.1. Instalar con `--save-exact`; en `/mobile` usar `npx expo install`. Si una versión no funciona, detenerse y reportarlo, no improvisar otra.
- Una carpeta por microservicio en `/services/svc-*`, cada una con su `Dockerfile`.
- Infraestructura solo en Terraform (`/infra`), región `us-east-1`, todos los recursos con tags `Project=qwallet` y `Env`.
- Nunca subir secretos. Usar `.env.example` y SSM Parameter Store.
- **Seguro desde el diseño.** Todo código implementa los controles CTRL-01 a CTRL-21 de `docs/CONTEXTO.md` §5 desde el primer commit. No se permite código inseguro "temporal": si falta un control, deja `TODO(CTRL-xx)` y repórtalo.
- Commits: `feat(CTRL-xx): ...` si implementan un control; `fix(HAL-xx): ...` si corrigen un hallazgo de pruebas.
- Cada endpoint nuevo requiere:
  - Esquema `zod` `.strict()`.
  - Verificación de propiedad del recurso (CTRL-01).
  - Logs con redacción de datos sensibles (CTRL-09).
  - Pruebas `vitest`, incluido el caso de acceso a un recurso ajeno, que debe responder 403/404.
- No usar servicios AWS fuera de CONTEXTO §3.

## Al cerrar cada sesión (obligatorio)
1. Reescribir `docs/CONTEXTO.md` §11 (Estado actual).
2. Agregar una entrada al inicio de `docs/BITACORA.md`.
3. Si cambió una decisión o versión: actualizar la sección correspondiente de CONTEXTO y anotarla en la bitácora.
4. Commit: `docs: actualiza estado y bitácora (AAAA-MM-DD)`.

## Tarea actual
<!-- Actualizar en cada sesión -->
Entrega 1 (17-oct): documentación. En paralelo, solo andamiaje (pasos de `docs/INICIO.md`).
