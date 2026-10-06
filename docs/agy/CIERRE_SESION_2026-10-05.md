# Tarea para agy — Cierre de sesión 2026-10-05

Lee este archivo completo antes de actuar. Ejecuta los pasos en orden.
**Solo documentación y `.gitignore`.** No modifiques código de la app, no instales ni actualices dependencias, no ejecutes `npm install`, `npm audit fix` ni builds.

## Reglas

- La fuente de verdad es `docs/CONTEXTO.md`. Respeta su estructura y numeración.
- Escribe en español y conserva el estilo de los archivos existentes.
- Usa **solo** los datos de este archivo. No inventes versiones, IDs ni evidencias.
- Si algo no cuadra con el estado real del repo, **no lo corrijas por tu cuenta**: anótalo en la bitácora en "Problemas / bloqueos".

## Paso 1 — Verificar el estado real

Ejecuta lo siguiente y usa los resultados en los pasos siguientes:

```powershell
cd C:\dev\q-wallet
git status
git log --oneline -5
cd mobile
npm ls babel-preset-expo freerasp-react-native expo-screen-capture expo-build-properties
Get-Content app.json
Get-Content babel.config.js
Get-Content .gitignore
cd ..
Get-ChildItem docs\evidencias
```

Comprueba que:

- `app.json` → `expo.plugins` **no** contiene `expo-screen-capture` y **sí** contiene `["freerasp-react-native", { "android": {} }]`.
- `babel.config.js` **no** tiene `plugins`, solo los presets `babel-preset-expo` (con `jsxImportSource: "nativewind"`) y `nativewind/babel`.
- `babel-preset-expo@57.0.13` aparece como dependencia directa de `mobile`.

## Paso 2 — `.gitignore` de `/mobile`

El proyecto usa Continuous Native Generation (CNG): `android/` e `ios/` se regeneran desde `app.json` y no se versionan.

Si `mobile/.gitignore` no contiene las líneas `/android` y `/ios`, agrégalas bajo un comentario `# Native (CNG)`. Si `mobile/android/` ya está rastreado en git, ejecuta `git rm -r --cached mobile/android`.

## Paso 3 — `docs/CONTEXTO.md`

- **§3.1 (versiones):**
  - Agrega `babel-preset-expo` `~57.0.13`, instalado con `npx expo install babel-preset-expo -- --legacy-peer-deps`.
  - Agrega o actualiza la sección del entorno Android:
    - Android SDK en `%LOCALAPPDATA%\Android\Sdk`.
    - Platform 36, Build-Tools 36.0.0, NDK 27.1.12297006.
    - AVD `Pixel_8_API_36`: Google APIs, x86_64, **sin Google Play**.
    - ADB 1.0.41.
    - Temurin JDK 17.0.20.1.
  - Agrega o actualiza la sección del build resuelto por Expo:
    - compileSdk 36, targetSdk 36, minSdk 24.
    - Kotlin 2.1.20.
    - Gradle 9.3.1.
    - Metro 0.84.5.
- **Configuración de `app.json` (donde corresponda en CONTEXTO):**
  - Lista de plugins vigente: `expo-router`, `expo-build-properties`, `expo-secure-store`, `expo-local-authentication`, `expo-font`, `expo-splash-screen`, `["freerasp-react-native", { "android": {} }]`.
  - Aclara que `expo-screen-capture` **no** es un config plugin: FLAG_SECURE se aplica en runtime en `transfer`, `unlock` y `profile`.
  - Aclara que `expo-build-properties` está registrado **sin opciones**. Es un pendiente de endurecimiento.
- **§11 (estado vigente):**
  - Primer build nativo Android exitoso el 2026-10-05. La app carga en el emulador.
  - Pendientes:
    - push y seguridad de GitHub;
    - corregir los textos falsos de la UI (ver Paso 4);
    - configurar `expo-build-properties`;
    - cuenta AWS;
    - Entrega 1 (17-oct-2026).

## Paso 4 — `docs/BITACORA.md`

Inserta **arriba** (debajo del separador `---` que sigue a la plantilla) esta entrada, completando solo lo marcado con `[...]` con los resultados del Paso 1:

```
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
- Archivos creados o modificados: `scripts/dev-env.ps1`, `mobile/app.json`, `mobile/babel.config.js`, `mobile/package.json`, `mobile/package-lock.json`, `mobile/.gitignore` [indicar si se modificó], `docs/CONTEXTO.md`, `docs/BITACORA.md`, `docs/INICIO.md`.
- Decisiones tomadas (y por qué):
  - `android/` e `ios/` fuera de git (CNG): se regeneran desde `app.json`, y versionarlos desincroniza la configuración.
  - Imagen Google APIs en lugar de Google Play, para permitir el pentest dinámico.
  - Sin override de R8 en freeRASP: el override solo hace falta con versiones antiguas del Android Gradle Plugin, y el proyecto usa Gradle 9.3.1.
- Cambios de versión: + `babel-preset-expo` ~57.0.13.
- Evidencias generadas (EVD-): EVD-1-05_app-emulador.png [indicar si existe en docs/evidencias].
- IDs nuevos: ninguno.
- Hallazgos para el informe:
  - El andamiaje autónomo de la sesión 2026-10-03 (4) se validó solo con `tsc` y `eslint`, y tenía 4 errores de configuración que solo aparecieron con el build nativo. Desde ahora, todo cambio se valida con build.
  - `--legacy-peer-deps` puede ocultar dependencias faltantes. Se debe revisar con `npm ls` en la fase de SCA.
  - `expo-build-properties` está registrado sin opciones, por lo que no aplica endurecimiento.
  - La pantalla Welcome afirma "Cifrado de extremo a extremo" y "Cumplimiento JM-104-2021". Ninguna de las dos afirmaciones es sostenible: la arquitectura no es E2E y no hay auditoría de cumplimiento. Pendiente de corrección.
- Problemas / bloqueos: [anotar cualquier discrepancia del Paso 1; si no hay, "ninguno"].
- Siguiente paso: push y seguridad de GitHub; corrección de textos de la UI; cuenta AWS; Entrega 1 (17-oct-2026).
```

## Paso 5 — `docs/INICIO.md`

Agrega una sección **"Arranque diario de la app"** con el siguiente contenido.

**Ventana 1:**

```powershell
cd C:\dev\q-wallet
. .\scripts\dev-env.ps1
emulator -avd Pixel_8_API_36
```

**Ventana 2:**

```powershell
cd C:\dev\q-wallet
. .\scripts\dev-env.ps1
adb devices
cd mobile
npx expo start
```

Luego presionar `a`.

Agrega también estas notas:

- `npx expo run:android` solo se usa si cambian `app.json`, los plugins o las dependencias nativas.
- Toda ventana nueva de PowerShell debe ejecutar primero `dev-env.ps1`.

## Paso 6 — Commit (sin push)

```powershell
cd C:\dev\q-wallet
git add docs/CONTEXTO.md docs/BITACORA.md docs/INICIO.md mobile/.gitignore mobile/app.json mobile/babel.config.js mobile/package.json mobile/package-lock.json
git status
git commit -m "fix(mobile): primer build nativo Android y cierre de sesión 2026-10-05"
```

Si `git status` muestra archivos inesperados en staging, **no hagas commit**. Repórtalos.

## Paso 7 — Reporte final

Imprime:

- Los resultados del Paso 1.
- Las secciones modificadas de cada archivo.
- El hash del commit.
- Cualquier discrepancia encontrada.
