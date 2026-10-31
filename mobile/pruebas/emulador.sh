#!/usr/bin/env bash
# Arranca un emulador Android 13 (API 33, Google APIs, x86_64) sin ventana, con KVM.
# Uso: bash mobile/pruebas/emulador.sh carpeta-de-salida
# Deja un registro de cada paso en <salida>/registro_emulador.txt (se publica como evidencia).
set -uo pipefail

OUT="$1"
mkdir -p "$OUT"
exec > >(tee -a "$OUT/registro_emulador.txt") 2>&1

SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-/usr/local/lib/android/sdk}}"
SM="$SDK/cmdline-tools/latest/bin/sdkmanager"
AM="$SDK/cmdline-tools/latest/bin/avdmanager"
IMAGEN="system-images;android-33;google_apis;x86_64"
paso() { echo "[$(date -u '+%H:%M:%S')] $*"; }

paso "SDK: $SDK · KVM: $(ls -l /dev/kvm 2>&1)"
paso "Licencias e imagen ${IMAGEN}"
yes | "$SM" --licenses > /dev/null 2>&1 || true
"$SM" --install "$IMAGEN" "emulator" "platform-tools" > /tmp/sdkmanager.log 2>&1 || { tail -20 /tmp/sdkmanager.log; exit 1; }
tail -2 /tmp/sdkmanager.log

paso "Crear el dispositivo virtual"
echo no | "$AM" create avd -n qwallet-prueba -k "$IMAGEN" -d pixel_6 --force || exit 1

paso "Arrancar el emulador"
nohup "$SDK/emulator/emulator" -avd qwallet-prueba -no-window -gpu swiftshader_indirect -no-snapshot \
  -noaudio -no-boot-anim -camera-back none -camera-front none -memory 3072 > /tmp/emulador.log 2>&1 &
export PATH="$SDK/platform-tools:$PATH"
timeout 120 adb wait-for-device || { paso "El emulador no aparece en adb"; tail -30 /tmp/emulador.log; exit 1; }

t0=$(date +%s)
until [ "$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" = "1" ]; do
  if [ $(( $(date +%s) - t0 )) -gt 600 ]; then
    paso "No terminó de arrancar en 10 minutos"; tail -30 /tmp/emulador.log; exit 1
  fi
  sleep 5
done
paso "Arrancó en $(( $(date +%s) - t0 )) s: Android $(adb shell getprop ro.build.version.release | tr -d '\r'), $(adb shell getprop ro.build.type | tr -d '\r')"
for s in window_animation_scale transition_animation_scale animator_duration_scale; do
  adb shell settings put global "$s" 0
done
adb shell input keyevent 82 || true
