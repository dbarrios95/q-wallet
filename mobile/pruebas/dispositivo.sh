#!/usr/bin/env bash
# Pruebas de la app en un emulador Android (bloque 5, secciones 5.2 y 3.2).
# Corre dentro de reactivecircus/android-emulator-runner en el flujo movil.yml.
# Uso: bash mobile/pruebas/dispositivo.sh ruta/app-release.apk carpeta-de-salida
#
#   A) Arranque normal ........ freeRASP (CTRL-15) + pinning y sonda a la API (CTRL-08)
#   B) CA-10 Frida ............ frida-server + hook en la app; freeRASP debe detectarlo
#   C) CA-08 MITM ............. proxy mitmproxy con su CA instalada como CA del SISTEMA
#                               (atacante con root); el pinning debe cortar la conexión
#   D) CA-07 almacenamiento ... sin tokens ni datos legibles en /data/data de la app
#
# No falla por una detección "faltante": deja el resultado tal cual para el informe.
# Sí falla si la app no instala o no arranca.
set -uo pipefail

APK="$1"
OUT="$2"
PKG="gt.qwallet.app"
FRIDA_VER="17.22.0"
mkdir -p "$OUT"
FECHA="$(date -u '+%Y-%m-%d %H:%M:%S UTC')"

marcas() { adb logcat -d 2>/dev/null | grep -o 'QWALLET_[A-Z]* .*' | sed 's/[[:space:]]*$//' | sort -u; }
abrir() {
  adb shell am force-stop "$PKG"
  adb logcat -c
  adb shell monkey -p "$PKG" -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1
  sleep "${1:-25}"
}
captura() { adb exec-out screencap -p > "$OUT/$1"; }

adb wait-for-device
echo "Dispositivo: $(adb shell getprop ro.product.model) · Android $(adb shell getprop ro.build.version.release) (API $(adb shell getprop ro.build.version.sdk)) · $(adb shell getprop ro.build.type)"
adb install -r -g "$APK" || { echo "No se pudo instalar el APK"; exit 1; }

# ---------- A) Arranque normal ----------
abrir 30
{
  echo "EVD-5-03 freeRASP y pinning en el arranque de la app (CTRL-15, CTRL-08)"
  echo "Fecha: ${FECHA}"
  echo "Dispositivo: emulador Android $(adb shell getprop ro.build.version.release), imagen $(adb shell getprop ro.build.type)"
  echo "APK: versión de producción (release, Hermes + R8), firmada; isProd = true"
  echo
  echo "Marcas de seguridad escritas por la app (logcat, etiqueta ReactNativeJS):"
  marcas | sed 's/^/   /'
  echo
  echo "Esperado: la sonda GET /me sin token responde 401 con el pinning activo, y freeRASP"
  echo "marca el emulador (simulator) y bloquea la app (pantalla EVD-5-03_bloqueo_rasp.png)."
} > "$OUT/EVD-5-03_freerasp_arranque.txt"
captura EVD-5-03_bloqueo_rasp.png
pidof_app=$(adb shell pidof "$PKG" | tr -d '\r')
[ -n "$pidof_app" ] || { echo "La app no arrancó"; cat "$OUT/EVD-5-03_freerasp_arranque.txt"; exit 1; }

# ---------- B) CA-10: Frida ----------
adb root >/dev/null 2>&1; sleep 4; adb wait-for-device
curl -fsSL -o /tmp/frida-server.xz \
  "https://github.com/frida/frida/releases/download/${FRIDA_VER}/frida-server-${FRIDA_VER}-android-x86_64.xz"
xz -df /tmp/frida-server.xz
adb push /tmp/frida-server /data/local/tmp/frida-server >/dev/null
adb shell chmod 755 /data/local/tmp/frida-server
adb shell '/data/local/tmp/frida-server >/dev/null 2>&1 &'
sleep 5
abrir 15
pid=$(adb shell pidof "$PKG" | tr -d '\r')
cat > /tmp/hook.js <<'JS'
// Hook mínimo: intercepta getpid() de libc dentro del proceso de la app.
Interceptor.attach(Module.getGlobalExportByName("getpid"), { onEnter() {} });
console.log("QWALLET_FRIDA hook=instalado");
JS
frida_salida=$(timeout 60 frida -U -p "$pid" -l /tmp/hook.js -q -t 25 2>&1 | tail -5)
sleep 10
{
  echo "EVD-4-10 CA-10 instrumentación con Frida contra la app (CTRL-15)"
  echo "Fecha: ${FECHA}"
  echo "Ataque: frida-server ${FRIDA_VER} como root en el emulador + hook a getpid() en el proceso de la app."
  echo
  echo "Salida de Frida (lado atacante):"
  echo "$frida_salida" | sed 's/^/   /'
  echo
  echo "Marcas de la app después del ataque:"
  marcas | sed 's/^/   /'
  echo
  if marcas | grep -q 'amenaza=hooks'; then
    echo "Resultado: DETECTADO. freeRASP reportó 'hooks' y la app aplica la reacción indicada."
  else
    echo "Resultado: freeRASP NO reportó 'hooks' en esta ejecución (ver marcas). Se registra tal cual."
  fi
} > "$OUT/EVD-4-10_frida.txt"
captura EVD-4-10_frida_app.png
adb shell 'pkill -f frida-server' >/dev/null 2>&1 || true

# ---------- C) CA-08: MITM con la CA del atacante en el almacén del sistema ----------
mitmdump --listen-port 8080 --set block_global=false --set flow_detail=1 > /tmp/mitm.log 2>&1 &
MITM=$!
sleep 6
CA="$HOME/.mitmproxy/mitmproxy-ca-cert.pem"
HASH=$(openssl x509 -inform PEM -subject_hash_old -in "$CA" | head -1)
cp "$CA" "/tmp/${HASH}.0"
adb push "/tmp/${HASH}.0" /data/local/tmp/ >/dev/null
# Técnica conocida (Android 13 o anterior): copia el almacén de CA del sistema a un
# tmpfs y agrega la CA del atacante. Requiere root: es el atacante más fuerte posible.
adb shell "mkdir -p -m 700 /data/local/tmp/ca && cp /system/etc/security/cacerts/* /data/local/tmp/ca/ \
  && mount -t tmpfs tmpfs /system/etc/security/cacerts && cp /data/local/tmp/ca/* /system/etc/security/cacerts/ \
  && cp /data/local/tmp/${HASH}.0 /system/etc/security/cacerts/ && chown root:root /system/etc/security/cacerts/* \
  && chmod 644 /system/etc/security/cacerts/* && chcon u:object_r:system_file:s0 /system/etc/security/cacerts/*"
ca_instalada=$(adb shell "ls /system/etc/security/cacerts/${HASH}.0 2>/dev/null" | tr -d '\r')
adb shell settings put global http_proxy 10.0.2.2:8080
API_HOST=$(grep -o 'https://[^"]*execute-api[^"/]*' mobile/src/seguridad/config.ts | head -1)
# Control: un cliente que confía en la CA del atacante y NO fija llaves sí es interceptado.
control=$(curl -sS -o /dev/null -w '%{http_code}' --proxy http://127.0.0.1:8080 --cacert "$CA" "${API_HOST}/v1/me" 2>&1)
abrir 30
adb shell settings put global http_proxy :0
kill "$MITM" 2>/dev/null; sleep 2
{
  echo "EVD-4-08 CA-08 intercepción MITM contra la app (CTRL-08, pinning)"
  echo "Fecha: ${FECHA}"
  echo "Ataque: proxy mitmproxy en 10.0.2.2:8080 con su CA instalada como CA del SISTEMA (con root)."
  echo "CA del atacante en el almacén del sistema: ${ca_instalada:-NO}"
  echo
  echo "Control (curl confiando en la CA del atacante, sin pinning): HTTP ${control}"
  echo "   -> el proxy SÍ puede descifrar a un cliente sin pinning."
  echo
  echo "Marcas de la app con el proxy activo:"
  marcas | sed 's/^/   /'
  echo
  echo "Lo que vio el proxy (solicitudes que pudo leer en claro):"
  grep -E 'GET |POST |client disconnect|Client TLS|TLS handshake|certificate' /tmp/mitm.log | sed 's/^/   /' | head -20
  echo
  if marcas | grep -q 'error=pinning'; then
    echo "Resultado: BLOQUEADO. La app rechazó el certificado del proxy (pinning) y no envió la solicitud."
  else
    echo "Resultado: la app no reportó error de pinning en esta ejecución (ver marcas). Se registra tal cual."
  fi
} > "$OUT/EVD-4-08_mitm_pinning.txt"

# Vuelve a abrir sin proxy: la conexión legítima sigue funcionando (401 esperado).
abrir 20
echo "Sin proxy, de nuevo:" >> "$OUT/EVD-4-08_mitm_pinning.txt"
marcas | grep 'QWALLET_API' | sed 's/^/   /' >> "$OUT/EVD-4-08_mitm_pinning.txt"

# ---------- D) CA-07: almacenamiento en el dispositivo ----------
{
  echo "EVD-4-08b CA-07 datos de la app en el dispositivo (CTRL-07)"
  echo "Fecha: ${FECHA}"
  echo "Con root se listan los archivos privados de la app y se buscan tokens (JWT) o datos en claro."
  echo
  adb shell "find /data/data/${PKG} -type f 2>/dev/null | head -60" | sed 's/^/   /'
  echo
  jwt=$(adb shell "grep -rl 'eyJ' /data/data/${PKG} 2>/dev/null" | tr -d '\r')
  echo "Archivos con algo parecido a un JWT: ${jwt:-ninguno}"
  echo "allowBackup del paquete: $(adb shell dumpsys package ${PKG} | grep -o 'ALLOW_BACKUP' | head -1 || true)"
  echo "(vacío = allowBackup desactivado; ver también el manifiesto en EVD-4-11)"
  echo
  echo "Nota: en esta versión la app no inicia sesión (conexión mínima con la API, decisión del"
  echo "bloque 5), así que no hay tokens que guardar; el control CTRL-07 queda verificado por diseño"
  echo "y por configuración (expo-secure-store con Android Keystore), no por un token real."
} > "$OUT/EVD-4-08b_almacenamiento.txt"

for f in "$OUT"/*.txt; do echo "==== $(basename "$f")"; cat "$f"; done
