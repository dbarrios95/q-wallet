# scripts/dev-env.ps1
# Configuración del entorno de desarrollo para la sesión actual de PowerShell de Q-Wallet

Write-Host "=== Configurando entorno de desarrollo Q-Wallet ===" -ForegroundColor Cyan

# 1. JAVA_HOME (JDK 17)
$jdk17 = Get-ChildItem "C:\Program Files\Eclipse Adoptium\jdk-17*" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($jdk17) {
    $env:JAVA_HOME = $jdk17.FullName
    $env:PATH = "$env:JAVA_HOME\bin;$env:PATH"
    Write-Host "[OK] JAVA_HOME configurado en: $env:JAVA_HOME" -ForegroundColor Green
} else {
    Write-Warning "[AVISO] No se encontró JDK 17 en 'C:\Program Files\Eclipse Adoptium\jdk-17*'. Falta instalar Temurin 17 JDK."
}

# 2. ANDROID_HOME
$env:ANDROID_HOME = "$env:LOCALAPPDATA\Android\Sdk"
Write-Host "[OK] ANDROID_HOME configurado en: $env:ANDROID_HOME" -ForegroundColor Green

# 3. Anteponer platform-tools y emulator al PATH
$platformTools = "$env:ANDROID_HOME\platform-tools"
$emulator = "$env:ANDROID_HOME\emulator"

if (Test-Path $platformTools) {
    $env:PATH = "$platformTools;$env:PATH"
}
if (Test-Path $emulator) {
    $env:PATH = "$emulator;$env:PATH"
}

# 4. Imprimir versiones
Write-Host "`n--- Versiones de herramientas en sesión ---" -ForegroundColor Cyan

# Node
try {
    $nodeVer = & node -v 2>$null
    Write-Host "Node.js: $nodeVer"
} catch {
    Write-Host "Node.js: No encontrado" -ForegroundColor Yellow
}

# Java
try {
    $javaVer = & java -version 2>&1 | Select-Object -First 1
    Write-Host "Java: $javaVer"
} catch {
    Write-Host "Java: No disponible o no instalado" -ForegroundColor Yellow
}

# ADB
try {
    $adbVer = & adb version 2>&1 | Select-Object -First 1
    Write-Host "ADB: $adbVer"
} catch {
    Write-Host "ADB: No encontrado en PATH / no instalado" -ForegroundColor Yellow
}

Write-Host "============================================`n" -ForegroundColor Cyan
