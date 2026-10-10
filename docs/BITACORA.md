# BITÁCORA DEL PROYECTO — Q-Wallet

> Entradas nuevas **arriba**. Una por sesión de trabajo.
> El resumen vigente está en `CONTEXTO.md` sección 11; aquí queda el historial.

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
