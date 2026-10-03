# INICIO — Dónde va cada archivo y cómo arrancar Q-Wallet

> Prioridad: la **Entrega 1 (17-oct) es documental**. El código empieza en paralelo, pero sin quitarle tiempo a las secciones 1 y 2.

---

## 1. Dónde va cada archivo

```
C:\dev\q-wallet\              ← raíz del repo (GitHub, público). Ruta corta a propósito: Android falla con rutas largas en Windows
├── GEMINI.md                  ← Gemini CLI lo lee automáticamente
├── README.md
├── SECURITY.md                ← política de seguridad (evidencia capa 7)
├── .gitignore                 ← bloquea .env, keystores, tfstate, android/
├── .editorconfig
├── .nvmrc                     ← 24.21.0
├── .github/
│   ├── dependabot.yml         ← CTRL-10
│   ├── pull_request_template.md
│   └── workflows/             ← pipelines DevSecOps (fase B)
├── docs/
│   ├── CONTEXTO.md            ← fuente de verdad
│   ├── INSTRUCCIONES.md       ← prompt de sistema (Claude / Gem)
│   ├── PLAN_FASES.md
│   ├── REGISTRO_RIESGOS.md
│   ├── CHECKLIST_EVIDENCIAS.md
│   ├── BITACORA.md
│   ├── INICIO.md              ← este archivo
│   ├── threat-model/          ← .json de Threat Dragon
│   ├── diagramas/             ← .drawio y .png
│   ├── evidencias/            ← EVD-*.png (censuradas)
│   └── entregas/              ← Word/PDF de cada entrega
├── mobile/                    ← app Expo (paso 5)
├── services/                  ← 5 Lambdas (después del 17-oct)
└── infra/                     ← Terraform (después del 17-oct)
```

El zip `q-wallet-repo.zip` ya trae esta estructura con todos los archivos en su lugar.

**Fuera del repo:**

| Dónde | Qué subir |
|---|---|
| Proyecto de Claude | Instrucciones = texto de `INSTRUCCIONES.md`. Conocimiento = `CONTEXTO.md`, `BITACORA.md`, `PLAN_FASES.md`, `REGISTRO_RIESGOS.md`, `CHECKLIST_EVIDENCIAS.md`, enunciado y rúbrica |
| Gem de Gemini | Lo mismo que el proyecto de Claude |
| Gemini CLI | Nada: lee `GEMINI.md` y `docs/` del repo |

Cada vez que cambien `CONTEXTO.md` o `BITACORA.md`, vuelvan a subirlos al proyecto de Claude y a la Gem.

---

## 2. Paso a paso

### Paso 0 — Instalar herramientas (cada integrante)

Windows 10/11, **PowerShell como administrador**.

```powershell
winget install --id Git.Git -e
winget install --id CoreyButler.NVMforWindows -e
winget install --id EclipseAdoptium.Temurin.17.JDK -e
winget install --id Google.AndroidStudio -e
winget install --id Docker.DockerDesktop -e        # requiere WSL2: wsl --install
winget install --id Hashicorp.Terraform -e --version 1.16.5
winget install --id Amazon.AWSCLI -e
```

Cerrar y abrir PowerShell, luego:

```powershell
nvm install 24.21.0
nvm use 24.21.0
node -v                                   # debe decir v24.21.0
npm install -g @google/gemini-cli@0.62.0
git config --global core.longpaths true
git config --global core.autocrlf input   # respeta LF del .editorconfig
```

**Variables de entorno** (Panel de control → Variables de entorno de usuario):
- `JAVA_HOME` = carpeta del JDK 17, por ejemplo `C:\Program Files\Eclipse Adoptium\jdk-17...`
- `ANDROID_HOME` = `%LOCALAPPDATA%\Android\Sdk`
- Agregar a `Path`:
  - `%ANDROID_HOME%\platform-tools`
  - `%ANDROID_HOME%\emulator`

**Android Studio:**
- **SDK Manager:** instalar SDK Platform, Build-Tools y Command-line Tools. Anotar sus versiones en la bitácora.
- **Device Manager:** crear un emulador con imagen **Google APIs**, sin Play Store, para poder rootearlo en las pruebas de freeRASP/Frida.

Anotar en `BITACORA.md` las versiones instaladas de Git, Android Studio, Docker y AWS CLI.

### Paso 1 — Repo (I1)

1. Crear el repo **público** `q-wallet` en GitHub e invitar a I2 e I3.
2. Descomprimir `q-wallet-repo.zip` en `C:\dev\`, de modo que quede `C:\dev\q-wallet\`. Luego:
   ```powershell
   cd C:\dev\q-wallet
   git init -b main
   git add .
   git commit -m "chore: estructura inicial"
   git remote add origin https://github.com/<usuario>/q-wallet.git
   git push -u origin main
   ```
3. En **Settings**:
   - **Branches:** proteger `main` (requiere PR + 1 aprobación, sin push directo).
   - **Code security:**
     - Activar Dependabot alerts.
     - Activar Secret scanning + **Push protection**.
     - Activar Private vulnerability reporting.
4. Captura de pantalla de la estructura del repo → `EVD-1-02`.

### Paso 2 — Cuenta AWS (I2)

1. Crear la cuenta en **Free Plan**, región `us-east-1`.
2. Asegurar la cuenta:
   - MFA en el usuario root.
   - Guardar las credenciales de root y no volver a usarlas.
3. IAM Identity Center: crear un usuario por integrante con MFA.
4. Billing:
   - Crear un presupuesto de US$5 con alertas al 50 %, 80 % y 100 %.
   - Captura de pantalla → `EVD-1-03`.
5. Verificar que el Free Plan permita **AWS WAF** y **ECR**. Anotar el resultado en la bitácora.
6. **No crear recursos desde la consola.** Todo se crea con Terraform después del 17-oct.

### Paso 3 — Asistentes (I1)

1. Crear el proyecto de Claude y la Gem de Gemini con los archivos de la tabla anterior.
2. Instalar Gemini CLI y ejecutar `gemini` en la raíz del repo para verificar que lee `GEMINI.md`.

### Paso 4 — Primera sesión de la Entrega 1

Empezar con los prompts P1 a P5 de `PLAN_FASES.md` según el calendario.

### Paso 5 — Crear la app (I2, en paralelo a la Entrega 1)

```powershell
# desde C:\dev\q-wallet
Remove-Item -Recurse -Force mobile
npx create-expo-app@5.0.0 mobile --template blank-typescript@sdk-57
cd mobile

# dependencias del SDK 57 (expo install alinea versiones)
npx expo install expo-dev-client expo-router expo-linking expo-constants expo-status-bar `
  expo-auth-session expo-web-browser expo-crypto expo-secure-store expo-local-authentication `
  expo-build-properties expo-image expo-linear-gradient expo-blur expo-haptics expo-font `
  react-native-reanimated react-native-worklets react-native-safe-area-context `
  react-native-screens react-native-svg

# fuera del SDK: versión exacta
npm install --save-exact nativewind@4.2.7 react-native-ssl-public-key-pinning@1.2.6 `
  freerasp-react-native@5.2.2 zod@4.6.5
npm install --save-exact --save-dev tailwindcss@3.4.19

# verificar que todo esté alineado al SDK
npx expo install --check

# primer build nativo en el emulador (development build, no Expo Go)
npx expo run:android
```

- **Por qué un development build:** freeRASP, el pinning y el Keystore biométrico no funcionan en Expo Go.
- **Carpeta `android/`:** está en `.gitignore`. La configuración nativa se hace con plugins en `app.json` (Continuous Native Generation).

Commit al terminar: `chore(mobile): inicializa Expo SDK 57 con dependencias fijadas`.

### Paso 6 — Primer prompt para Gemini CLI (dentro de `mobile/`)

> Lee GEMINI.md y docs/CONTEXTO.md. Configura en /mobile: NativeWind 4.2.7 con tailwindcss 3.4.19, expo-router con entrada `expo-router/entry` y Reanimated 4 con worklets.
>
> **Sistema de diseño:**
> - Paleta: azul profundo `#0B1F3A` + acento verde quetzal `#00A86B`.
> - Modo claro y oscuro.
> - Tipografía Inter.
> - Tarjetas con bordes redondeados y degradados sutiles.
>
> **Pantallas** (datos simulados, sin backend todavía): bienvenida, login (botón que abrirá Cognito), desbloqueo biométrico, inicio (saldo + últimos movimientos), transferir (teléfono, monto, confirmación con PIN), movimientos, presupuestos por categoría, perfil.
>
> **Reglas de seguridad:**
> - Nada sensible en logs.
> - Ningún secreto en el código.
> - Pantallas sensibles con FLAG_SECURE: plugin o `expo-screen-capture` (si agregas una dependencia, dime cuál y su versión para anotarla en CONTEXTO §3.1).
>
> No instales otras versiones distintas a las de CONTEXTO §3.1.

### Paso 7 — Cerrar la sesión

Seguir las instrucciones de `GEMINI.md`, sección "Al cerrar cada sesión": actualizar `CONTEXTO.md` §11 y `BITACORA.md`.

---

## 3. Orden de construcción después del 17-oct

1. Terraform base:
   - Backend de estado en S3 con `use_lockfile = true`, cifrado KMS y bloqueo público.
   - KMS CMK.
   - Rol OIDC para GitHub.
2. Cognito: User Pool con MFA TOTP obligatorio, app client público con PKCE y grupo `admins`.
3. DynamoDB + `svc-profile` + API Gateway REST con authorizer de Cognito.
4. Conectar el login de la app (CTRL-07, CTRL-18).
5. `svc-accounts`, `svc-transfers` (CTRL-01, 02, 06), `svc-budgets`, `svc-admin` (CTRL-14).
6. Pipeline DevSecOps completo (fase B), luego WAF, freeRASP y pinning en el dominio final.
