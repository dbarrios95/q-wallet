# TRASPASO — Q-Wallet (estado al 05-oct-2026)

> Pegar el **Prompt de arranque** (al final) en un chat nuevo del proyecto de Claude.
> Adjuntar también `docs/CONTEXTO.md` y `docs/BITACORA.md` **ya actualizados por agy** (ver `docs/agy/CIERRE_SESION_2026-10-05.md`).

---

## 1. Estado actual

| Ítem | Estado |
|---|---|
| Proyecto | Opción A, app móvil Fintech **Q-Wallet**, segura desde el diseño |
| Ponderación | 4 × 5 puntos |
| Entrega 1 | **Sábado 17-oct-2026** (secciones 0, 1 y 2). **No iniciada.** Quedan 12 días |
| Repo local | `C:\dev\q-wallet`, rama `main` |
| Repo remoto | `https://github.com/dbarrios95/q-wallet.git` (push **por confirmar**) |
| App | **Primer build nativo Android exitoso.** La app carga en el emulador (pantalla Welcome). 8 pantallas, 9 componentes, datos simulados |
| Backend / AWS | Sin iniciar. **Cuenta AWS aún no creada** |

### Entorno instalado

| Herramienta | Versión | Nota |
|---|---|---|
| Node.js | 24.21.0 | |
| JDK | Temurin 17.0.20.1 (sesión) + Temurin 21 (sistema) | `scripts/dev-env.ps1` activa el 17 |
| Android SDK | `C:\Users\dbarr\AppData\Local\Android\Sdk` | Platform 36, Build-Tools 36.0.0, NDK 27.1.12297006 (lo instaló Gradle) |
| AVD | `Pixel_8_API_36` | Google APIs x86_64 (sin Play, para permitir `adb root` en el pentest) |
| ADB | 1.0.41 (37.0.1) | |
| Terraform | 1.16.5 | `C:\tools\terraform` |
| AWS CLI | 2.15.33 | |
| Docker | 29.1.3 | |
| Antigravity CLI (`agy`) | 1.2.16 | |

### Build Android que funciona

Versiones que resolvió Expo: compileSdk 36, targetSdk 36, minSdk 24, Kotlin 2.1.20, Gradle 9.3.1, Metro 0.84.5.

---

## 2. Correcciones de esta sesión (05-oct)

El andamiaje del agente solo se había validado con `tsc` y `eslint`, nunca con un build nativo. Al compilar aparecieron cinco errores:

| # | Síntoma | Causa | Corrección |
|---|---|---|---|
| 1 | `ERR_UNSUPPORTED_NODE_MODULES_TYPE_STRIPPING` | `expo-screen-capture` registrado en `plugins` de `app.json`, pero no tiene config plugin | Se quitó de `plugins`. FLAG_SECURE sigue activo con el hook en runtime |
| 2 | Gradle: `Could not find TalsecSecurity-Community-ReactNative:19.2.3` | `freerasp-react-native` instalado, pero sin registrar su plugin (que agrega el repositorio Maven de Talsec) | Se agregó a `plugins` |
| 3 | `Cannot read properties of undefined (reading 'android')` en `withAndroidR8Version` | El plugin de freeRASP exige un objeto de opciones | `["freerasp-react-native", { "android": {} }]` (sin override de R8) |
| 4 | `Duplicate plugin/preset detected` (worklets) | `babel.config.js` declaraba `react-native-worklets/plugin` y `react-native-reanimated/plugin`, que en Reanimated 4 son el mismo | Se quitaron los dos. `babel-preset-expo` ya lo inyecta |
| 5 | `Cannot find module 'babel-preset-expo'` (en Metro se ve como `reading 'transformFile'`) | `--legacy-peer-deps` dejó el preset anidado en `expo/node_modules` | `npx expo install babel-preset-expo -- --legacy-peer-deps` → 57.0.13 en la raíz |

Además se corrigió `dev-env.ps1` a UTF-8 con BOM (commit `bfe776e`).

---

## 3. Lecciones aprendidas (acumuladas)

- `agy` se ejecuta **desde PowerShell**, nunca dentro de la sesión de agy.
- Modo autónomo: `agy --dangerously-skip-permissions --effort high -i "..."`. Para retomar: `agy --dangerously-skip-permissions -c`.
- Prompts largos: guardarlos en `docs/agy/*.md` y pedirle a agy que los lea.
- Hay que exigir flags no interactivos (`--yes`, `CI=1`). Los comandos interactivos cuelgan a agy.
- **Nunca** usar `npm audit fix` ni `--force`.
- **Toda ventana nueva de PowerShell**: primero `cd C:\dev\q-wallet` y luego `. .\scripts\dev-env.ps1`. Sin eso no existen `adb`, `emulator` ni el JDK 17.
- **Cada cambio de agy en la app se valida con build nativo** (`npx expo run:android` o `npx expo start --clear` + `a`), no solo con `tsc`/`eslint`.
- Un paquete agregado a `plugins` de `app.json` debe tener `app.plugin.js`. Algunos plugins exigen objeto de opciones.
- Ante un error de Metro, el error real está **arriba** (`Failed to construct transformer`). Prueba rápida de Babel:
  ```powershell
  node -e "try{require('@babel/core').transformFileSync('app/_layout.tsx',{caller:{name:'metro',bundler:'metro',platform:'android'}});console.log('BABEL OK')}catch(e){console.log(e.message)}"
  ```
- `--legacy-peer-deps` puede dejar dependencias necesarias anidadas. Revisar con `npm ls <paquete>`.
- Imagen del emulador: siempre **Google APIs**, nunca Google Play.

---

## 4. Arranque diario de la app

**Ventana 1** (emulador):

```powershell
cd C:\dev\q-wallet
. .\scripts\dev-env.ps1
emulator -avd Pixel_8_API_36
```

**Ventana 2** (Metro):

```powershell
cd C:\dev\q-wallet
. .\scripts\dev-env.ps1
adb devices
cd mobile
npx expo start
```

Luego presionar `a`. Usar `npx expo run:android` (build nativo) **solo** si se cambia `app.json`, plugins o dependencias nativas.

---

## 5. Lo que sigue (en orden)

1. **Cierre de sesión con agy:** ejecutar `docs/agy/CIERRE_SESION_2026-10-05.md` (actualiza CONTEXTO, BITÁCORA, INICIO y `.gitignore`, y hace commit).
2. **Push y seguridad de GitHub:** pasos 3.2 y 3.3 del traspaso anterior (renombrar `EVD-3-01` a `EVD-3-00`, push, rulesets, Dependabot, secret scanning, push protection). Captura `EVD-1-04`.
3. **Corregir textos falsos de la UI** (ver §6). Antes de cualquier captura para el informe.
4. **Configurar `expo-build-properties`**: hoy está registrado sin opciones, así que no aplica ningún endurecimiento.
5. **Cuenta AWS**: Free Plan en `us-east-1`, MFA root, IAM Identity Center, presupuesto de US$5 (`EVD-1-03`). Verificar WAF y ECR.
6. **Entrega 1 (PRIORIDAD):** Gem en Gemini, prompts P1 a P5 de `PLAN_FASES.md`, Threat Dragon 2.6.2 para DFD/STRIDE.

---

## 6. Problemas detectados en la app (pendientes)

- **Textos de la pantalla Welcome con afirmaciones falsas:**
  - "Cifrado de extremo a extremo": una billetera P2P no es E2E, porque el backend debe leer las transacciones. Lo correcto es "cifrado en tránsito (TLS 1.2+) y en reposo".
  - "Cumplimiento JM-104-2021" y "estándares bancarios": no se puede afirmar cumplimiento sin auditoría. En un curso de seguridad lo van a señalar. Opciones: quitarlo o redactarlo como "diseñado con referencia a JM-104-2021".
- **`expo-build-properties` sin opciones.**
- **Badge bajo "Q-Wallet" con contraste bajo** (texto verde sobre verde, ilegible).
- **33 vulnerabilidades transitivas** en `npm audit`. Se documentan en la fase de SCA.

---

## 7. Pendientes por responder

- [ ] ¿El proyecto completo lo hace una sola persona? Si es así, recalcular el calendario de la Entrega 1.
- [ ] Nombres de los integrantes y sus roles.
- [ ] Fechas de las entregas parciales y final.
- [ ] ¿Existe plantilla oficial UMG?
- [ ] ¿El Free Plan de AWS permite WAF y ECR?
- [ ] ¿Se hizo el push a GitHub?

---

## Prompt de arranque (pegar en el chat nuevo)

```
Continúo el proyecto final de Seguridad en Aplicaciones (UMG): app móvil Fintech "Q-Wallet" (Opción A), segura desde el diseño. Adjunto TRASPASO_CHAT.md, CONTEXTO.md y BITACORA.md: léelos completos antes de responder; CONTEXTO.md es la fuente de verdad.

Estoy en Windows con PowerShell. Dame siempre los comandos exactos y en orden, indicando si van en PowerShell normal o como administrador, y qué resultado debo esperar de cada uno.

Situación: voy por la sección 5 de TRASPASO_CHAT.md. [Indica aquí el último paso completado y pega la salida o error, si hay.]

Respóndeme breve y directo. Si detectas algo mal planteado, dímelo sin suavizar.
```
