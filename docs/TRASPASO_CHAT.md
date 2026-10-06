# TRASPASO — Q-Wallet (estado al 03-oct-2026)

> Pegar el **Prompt de arranque** (al final) en un chat nuevo del proyecto de Claude.
> Adjuntar también `docs/CONTEXTO.md` y `docs/BITACORA.md` actualizados desde el repo.

---

## 1. Estado actual

| Ítem | Estado |
|---|---|
| Proyecto | Opción A, app móvil Fintech **Q-Wallet**, seguro desde el diseño (indicación del catedrático) |
| Ponderación | 4 × 5 puntos |
| Entrega 1 | **Sábado 17-oct-2026**: secciones 0, 1 y 2. **No iniciada** |
| Repo local | `C:\dev\q-wallet`, rama `main`, último commit `04799fd docs: cierre de sesión autónoma` |
| Repo remoto | `https://github.com/dbarrios95/q-wallet.git` (push **por confirmar**) |
| App | Expo SDK 57 con UI completa y datos simulados (8 pantallas, 9 componentes, tokens de diseño). `tsc`, `eslint` y `expo install --check` limpios |
| Backend / AWS | Sin iniciar. **Cuenta AWS aún no creada** |

### Entorno instalado

| Herramienta | Versión | Nota |
|---|---|---|
| Node.js | 24.21.0 | MSI en `C:\Program Files\nodejs` |
| Terraform | 1.16.5 | Manual en `C:\tools\terraform`, con SHA256 verificado |
| JDK | Temurin 17 instalado + Temurin 21 (por defecto del sistema) | `scripts/dev-env.ps1` activa el 17 solo en la sesión |
| AWS CLI | 2.15.33 | |
| Docker | 29.1.3 | |
| Antigravity CLI (`agy`) | 1.2.16 | Gemini CLI fue descontinuado para cuentas personales |
| Android Studio | **Pendiente** | |

---

## 2. Lecciones aprendidas (no repetir errores)

- **Antigravity CLI:** `agy` se ejecuta **desde PowerShell**, nunca escribiendo el comando dentro de la sesión de agy.
- **Modo autónomo:** `agy --dangerously-skip-permissions --effort high -i "..."`. Para retomar una sesión: `agy --dangerously-skip-permissions -c`.
- **Prompts largos:** guardarlos en un `.md` dentro de `docs/` y pedirle a agy que lo lea. Pegarlos en la terminal puede cortarlos.
- **Comandos interactivos:** `create-expo-app` (y cualquier comando que pregunte algo) se cuelga en modo autónomo. Hay que exigir flags no interactivos (`--yes`, `CI=1`).
- **npm audit:** **nunca** usar `npm audit fix` ni `--force`, porque rompe la alineación con el SDK 57. Las vulnerabilidades se documentan en la fase de SCA.
- **Red inestable:** `expo install --check` puede fallar con error de TLS. Funciona reintentando o usando `$env:EXPO_OFFLINE="1"`.
- **winget:** no tiene las versiones recién publicadas. En ese caso se instala manualmente y se verifica el hash.
- **Rutas de PowerShell:** `PS C:\...>` en las instrucciones es solo la ubicación, no un comando.

---

## 3. Lo que sigue (en orden)

### 3.1 Verificar el JDK 17 (PowerShell normal)

```powershell
Get-ChildItem "C:\Program Files\Eclipse Adoptium"
cd C:\dev\q-wallet
. .\scripts\dev-env.ps1
java -version
```

`java -version` debe mostrar **17** solo en esta ventana.

### 3.2 Corregir el ID de la evidencia y subir el repo

```powershell
cd C:\dev\q-wallet
Get-ChildItem docs\evidencias
```

Si existe `EVD-3-01_npm-audit-mobile.txt`, renombrarlo:

```powershell
git mv docs/evidencias/EVD-3-01_npm-audit-mobile.txt docs/evidencias/EVD-3-00_npm-audit-mobile.txt
git commit -m "docs: corrige ID de evidencia npm audit"
```

Si existe un duplicado `EVD-3-00_npm-audit-plantilla.txt`, borrarlo con `git rm` o `Remove-Item`.

Subir el repo:

```powershell
git remote add origin https://github.com/dbarrios95/q-wallet.git
git push -u origin main
```

Si `git remote add` dice que el remoto ya existe, correr solo `git push -u origin main`.

### 3.3 Configurar la seguridad de GitHub (navegador)

- **Settings → Branches / Rulesets** sobre `main`:
  - Require a pull request.
  - Block force pushes.
  - **No** marcar *Require approvals* (trabajo individual).
- **Settings → Advanced Security / Code security**, activar:
  - Dependabot alerts.
  - Dependabot security updates.
  - Secret scanning.
  - Push protection.
  - Private vulnerability reporting.
- Captura de pantalla → `docs\evidencias\EVD-1-04_github-seguridad.png`.

### 3.4 Android Studio (PowerShell como administrador)

```powershell
winget install --id Google.AndroidStudio -e
```

Luego, en la interfaz de Android Studio:

1. Instalación **Standard**.
2. **More Actions → SDK Manager → SDK Tools**, marcar:
   - Android SDK Platform-Tools.
   - Android SDK Command-line Tools (latest).
3. **Virtual Device Manager → Create device**: Pixel 8 con imagen **Google APIs** (no Google Play).
4. Iniciar el emulador y dejarlo abierto.

### 3.5 Primer build (PowerShell normal)

```powershell
cd C:\dev\q-wallet
. .\scripts\dev-env.ps1
cd mobile
npx expo run:android
```

- El primer build tarda de 10 a 20 minutos.
- Si funciona: guardar una captura de la app en el emulador como `EVD-1-05_app-emulador.png`.
- Si falla: copiar las últimas 30 líneas del error.

### 3.6 Cuenta AWS (navegador, INICIO.md Paso 2)

1. Crear la cuenta en **Free Plan**, región `us-east-1`.
2. Activar MFA en el usuario root.
3. Crear un usuario en IAM Identity Center con MFA.
4. Configurar un presupuesto de US$5 con alertas al 50/80/100 %.
   - Captura → `EVD-1-03`.
5. Verificar que el Free Plan permita **WAF** y **ECR**. Anotar el resultado en la bitácora.

### 3.7 Entrega 1 (PRIORIDAD; quedan 13 días)

1. Crear la Gem en gemini.google.com:
   - Instrucciones: el texto de `INSTRUCCIONES.md`.
   - Conocimiento: `CONTEXTO.md`, `PLAN_FASES.md`, `REGISTRO_RIESGOS.md`, `CHECKLIST_EVIDENCIAS.md`, `BITACORA.md`, el enunciado y la rúbrica.
2. Ejecutar los prompts **P1 a P5** de `PLAN_FASES.md`, uno por conversación.
3. Instalar OWASP Threat Dragon 2.6.2 para el DFD y STRIDE (sección 2.3).

### 3.8 Cierre de cada sesión

- Actualizar `CONTEXTO.md` §11 y `BITACORA.md`, luego hacer commit y push.
- Volver a subir ambos archivos al proyecto de Claude y a la Gem.

---

## 4. Pendientes por responder

- [ ] ¿El proyecto completo lo hace **una sola persona** o solo la instalación? Si es una sola, hay que recalcular el calendario de la Entrega 1.
- [ ] Nombres de los integrantes y sus roles.
- [ ] Fecha de la entrega final y de las entregas parciales.
- [ ] ¿Existe plantilla oficial UMG de portada o Word?
- [ ] ¿El Free Plan de AWS permite WAF y ECR?

---

## Prompt de arranque (pegar en el chat nuevo)

```
Continúo el proyecto final de Seguridad en Aplicaciones (UMG): app móvil Fintech "Q-Wallet" (Opción A), segura desde el diseño. Adjunto TRASPASO_CHAT.md, CONTEXTO.md y BITACORA.md: léelos completos antes de responder; CONTEXTO.md es la fuente de verdad.

Estoy en Windows con PowerShell. Dame siempre los comandos exactos y en orden, indicando si van en PowerShell normal o como administrador, y qué resultado debo esperar de cada uno.

Situación: voy por la sección 3 de TRASPASO_CHAT.md. [Indica aquí el último paso completado y pega la salida o error, si hay.]

Respóndeme breve y directo. Si detectas algo mal planteado, dímelo sin suavizar.
```
