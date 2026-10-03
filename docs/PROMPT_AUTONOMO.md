# PROMPT AUTÓNOMO — Sesión 1 (andamiaje de la app)

MODO AUTÓNOMO. El usuario no está presente. No hagas preguntas: decide según `docs/CONTEXTO.md` y registra cada decisión en `docs/BITACORA.md`.

**NOTA:** Gemini CLI fue reemplazado por **Antigravity CLI (agy) 1.2.16**. Se ejecuta con `agy --dangerously-skip-permissions`. `agy` lee `GEMINI.md` sin cambios.

## LÍMITES ESTRICTOS (no negociables)

**Alcance de trabajo**
- Trabaja SOLO dentro de `C:\dev\q-wallet`. No leas ni modifiques nada fuera de esa carpeta.

**Prohibido**
- Instalar software global: `npm -g`, `winget`, `choco`.
- Modificar variables de entorno del sistema o del usuario, o cambiar `JAVA_HOME`.
- Comandos de AWS y `terraform`.
- `git push`, borrar commits, `git reset`.
- Ejecutar `npx expo run:android`.

**Dependencias**
- Usa solo las versiones de CONTEXTO §3.1.
- Dependencias nuevas permitidas, con esta versión exacta (agrégalas a CONTEXTO §3.1):

  | Paquete | Versión | Instalación |
  |---|---|---|
  | `expo-screen-capture` | `~57.0.3` | `npx expo install` |
  | `expo-splash-screen` | `~57.0.9` | `npx expo install` |
  | `@expo-google-fonts/inter` | `0.4.2` | `npm --save-exact` |
  | `lucide-react-native` | `1.51.0` | `npm --save-exact` |

- Cualquier otra: NO la instales; anótala como propuesta en la bitácora.

**Seguridad**
- Seguro desde el diseño: aplica `GEMINI.md` y CONTEXTO §5.
- Nada de secretos, nada de datos sensibles en logs.

**Commits y errores**
- Después de CADA paso que termine bien: `git add .` y `git commit -m` con formato convencional.
- Si un paso falla 3 veces:
  - Registra el error en la bitácora.
  - Haz commit de lo que funcione.
  - Pasa al siguiente paso que no dependa de él.

## PASO 1 — Verificación mínima

Lee `GEMINI.md`, `docs/CONTEXTO.md`, `docs/INICIO.md` y `docs/BITACORA.md`.

- Verifica que `node -v` sea `v24.21.0`. Si no lo es, registra el problema en la bitácora y TERMINA la sesión.
- Java, Terraform y adb se ignoran en esta sesión: anótalos como pendientes.

## PASO 2 — Script de entorno por proyecto

Crea `scripts/dev-env.ps1`. Debe configurar estas variables SOLO para la sesión actual de PowerShell (`$env:`):

- `JAVA_HOME` apuntando al JDK 17. Búscalo en `C:\Program Files\Eclipse Adoptium\jdk-17*`; si no existe, muestra un mensaje claro de que falta instalarlo.
- `ANDROID_HOME=$env:LOCALAPPDATA\Android\Sdk`.
- Anteponer al `PATH` las carpetas `platform-tools` y `emulator`.

Al ejecutarse, el script debe imprimir las versiones de java, node y adb.

- No lo ejecutes con privilegios ni modifiques nada permanente.
- Documenta su uso en `docs/INICIO.md` (Paso 0).

## PASO 3 — Crear la app

1. Ejecuta el Paso 5 de `docs/INICIO.md` exactamente como está, sin `npx expo run:android`.
2. Ejecuta `npx expo install --check`.
3. Confirma que cada versión del `package.json` coincide con CONTEXTO §3.1.

## PASO 4 — Configuración base en `/mobile`

**Librerías**
- NativeWind 4.2.7 + tailwindcss 3.4.19 (babel, metro, `tailwind.config`, `global.css`).
- expo-router con `main: "expo-router/entry"`.
- Reanimated 4 con worklets.

**TypeScript**
- `tsconfig` en modo strict.

**app.json**
- Nombre `Q-Wallet`, slug `q-wallet`, package Android `gt.qwallet.app`.
- `allowBackup: false`.
- Plugins: `expo-build-properties`, `expo-secure-store`, `expo-local-authentication`, `expo-screen-capture`.

**Verificación**
- `npx tsc --noEmit`.

## PASO 5 — Sistema de diseño

**Tokens** en `/mobile/src/theme`:

- Colores:
  - Primario: azul profundo `#0B1F3A`.
  - Acento: verde quetzal `#00A86B`.
  - Estados: éxito, alerta, error.
- Modo claro y oscuro automático.
- Tipografía Inter.
- Espaciados y radios.

**Componentes reutilizables** en `/mobile/src/components`:

- `Button`
- `Input`, con variante enmascarada para PIN
- `Card`
- `BalanceCard`, con degradado
- `TransactionItem`
- `ProgressBar`, para presupuestos
- `Header`
- `EmptyState`
- `Skeleton`

**Estilo**

Fintech moderno, limpio y premium:
- Jerarquía tipográfica clara.
- Sombras suaves.
- Microanimaciones con Reanimated.
- Iconos de lucide.

## PASO 6 — Pantallas con datos simulados (sin backend)

**Datos simulados**

Crea `/mobile/src/mocks` con datos ficticios en GTQ:
- Montos almacenados en centavos enteros.
- Formato de visualización `Q 1,234.56`.

**Pantallas con expo-router**

- `(auth)/welcome`
- `(auth)/login`
  - Botón "Iniciar sesión" que por ahora navega al inicio.
  - `TODO(CTRL-18)` para Cognito PKCE.
- `(auth)/unlock`
  - Biometría con expo-local-authentication.
  - `TODO(CTRL-07)` para tokens en SecureStore.
- `(tabs)/home`
  - Saldo.
  - Accesos rápidos.
  - Últimos movimientos.
- `(tabs)/transfer`
  - Teléfono, monto y beneficiarios.
  - Confirmación con PIN de 6 dígitos.
- `(tabs)/activity`
  - Movimientos con filtros.
  - Paginación simulada con tope de 50 (CTRL-05).
- `(tabs)/budgets`
  - Categorías, progreso y alertas.
- `(tabs)/profile`
  - Datos enmascarados: DPI y teléfono como `****1234` (CTRL-03).
  - Cerrar sesión.

**Reglas**
- `FLAG_SECURE` con expo-screen-capture en `transfer`, `unlock` y `profile`.
- Validación de formularios con zod (`.strict()`).
- Ningún `console.log` de datos.
- `npx tsc --noEmit` después de cada pantalla.

## PASO 7 — Calidad

1. Configura ESLint 10.12.0 (`--save-exact`) para TypeScript/React Native y corrige los errores.
2. Ejecuta `npm audit` y registra el resultado. No fuerces actualizaciones fuera de §3.1.

## PASO 8 — Cierre (obligatorio, aunque los pasos anteriores hayan fallado)

**1. Actualiza CONTEXTO §3.1**
- Reemplaza la fila "Gemini CLI" por "Antigravity CLI (agy) 1.2.16".

**2. Actualiza `docs/INICIO.md`**
- Reemplaza los comandos de `gemini` por `agy --dangerously-skip-permissions`.
- Elimina la instalación de `@google/gemini-cli`.

**3. Reescribe CONTEXTO §11.**

**4. Agrega una entrada arriba en `docs/BITACORA.md`** con:
- Pasos completados y fallidos.
- Errores exactos.
- Dependencias agregadas, con su versión.
- Archivos creados.
- `TODO(CTRL-xx)` pendientes.
- Resultado de `npm audit`.
- Pendientes manuales del usuario: JDK 17, Terraform 1.16.5, Android Studio/adb y el primer `npx expo run:android`.

**5. Commit final:** `docs: cierre de sesión autónoma`.

**6. Imprime un resumen de máximo 15 líneas.**
