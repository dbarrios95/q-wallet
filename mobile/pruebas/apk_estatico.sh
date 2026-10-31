#!/usr/bin/env bash
# Análisis estático del APK de producción (bloque 5).
# Uso: bash mobile/pruebas/apk_estatico.sh ruta/app-release.apk carpeta-de-salida
#   EVD-4-11  CA-11: el APK no trae secretos (gitleaks + patrones) y el manifiesto está endurecido
#   EVD-5-11  Ofuscación y firma: Hermes bytecode, R8 y certificado de firma (CTRL-15)
set -uo pipefail

APK="$1"
OUT="$2"
mkdir -p "$OUT"
FECHA="$(date -u '+%Y-%m-%d %H:%M:%S UTC')"
BT="$(ls -d "$ANDROID_HOME"/build-tools/* | sort -V | tail -1)"
TMP="$(mktemp -d)"
unzip -qo "$APK" -d "$TMP/apk"
FALLAS=0
falla() { echo "FALLA: $1"; FALLAS=$((FALLAS + 1)); }

{
  echo "EVD-4-11 CA-11 secretos en el APK y manifiesto (CTRL-16)"
  echo "Fecha: ${FECHA}"
  echo "APK: $(basename "$APK"), $(du -h "$APK" | cut -f1)"
  echo
  echo "1) gitleaks 8.30.1 sobre el contenido del APK descomprimido:"
  mkdir -p "$TMP/gl"; chmod 777 "$TMP/gl"
  docker run --rm -v "$TMP/apk:/apk:ro" -v "$TMP/gl:/out" zricethezav/gitleaks:v8.30.1 dir /apk --no-banner --redact \
    --exit-code 0 --report-format json --report-path /out/gitleaks.json > "$TMP/gl/salida.txt" 2>&1
  n=$(python3 -c "import json;print(len(json.load(open('$TMP/gl/gitleaks.json'))))" 2>/dev/null || echo "?")
  [ "$n" = "?" ] && sed 's/^/   /' "$TMP/gl/salida.txt" | tail -5
  echo "   Hallazgos: ${n}"
  [ "$n" = "0" ] || falla "gitleaks encontró ${n} posibles secretos"
  echo
  echo "2) Patrones de secretos en el código (classes*.dex y el bundle de Hermes):"
  for p in 'AKIA[0-9A-Z]{16}' 'ASIA[0-9A-Z]{16}' '-----BEGIN (RSA |EC |)PRIVATE KEY' 'aws_secret_access_key' \
           'client_secret' 'sk_live_[0-9a-zA-Z]{20,}' 'xox[baprs]-[0-9A-Za-z-]{10,}' 'ghp_[0-9A-Za-z]{36}'; do
    c=$(cat "$TMP"/apk/classes*.dex "$TMP"/apk/assets/index.android.bundle 2>/dev/null | grep -a -E -c -- "$p" || true)
    printf '   %-40s %s coincidencias\n' "$p" "$c"
    [ "$c" = "0" ] || falla "patrón ${p}"
  done
  echo
  echo "3) Datos públicos que la app sí lleva (no son secretos):"
  for p in 'execute-api.us-east-1.amazonaws.com' 'gt.qwallet.app'; do
    c=$(grep -a -c -- "$p" "$TMP"/apk/assets/index.android.bundle 2>/dev/null || echo 0)
    printf '   %-40s %s\n' "$p" "$c"
  done
  echo
  echo "4) Manifiesto (aapt2):"
  "$BT/aapt2" dump xmltree "$APK" --file AndroidManifest.xml > "$TMP/manifest.txt"
  for a in allowBackup debuggable usesCleartextTraffic networkSecurityConfig minSdkVersion targetSdkVersion; do
    v=$(grep -m1 "android:${a}" "$TMP/manifest.txt" | sed -E 's/.*=//' | tr -d ' ')
    printf '   %-24s %s\n' "$a" "${v:-(no declarado)}"
  done
  grep -q 'android:debuggable.*0xffffffff' "$TMP/manifest.txt" && falla "APK depurable"
  grep -q 'android:allowBackup.*0xffffffff' "$TMP/manifest.txt" && falla "allowBackup activo"
  grep -q 'android:usesCleartextTraffic.*0xffffffff' "$TMP/manifest.txt" && falla "tráfico en claro permitido"
  echo
  echo "   Permisos solicitados:"
  grep -A1 'uses-permission' "$TMP/manifest.txt" | grep -o '"android.permission[^"]*"\|"[a-z][^"]*permission[^"]*"' | sort -u | sed 's/^/     /'
  echo
  echo "Fallas: ${FALLAS}"
} > "$OUT/EVD-4-11_apk_secretos_manifiesto.txt" 2>&1

{
  echo "EVD-5-11 Ofuscación, bytecode y firma del APK (CTRL-15, MASVS-RESILIENCE)"
  echo "Fecha: ${FECHA}"
  echo
  magia=$(xxd -p -l 8 "$TMP/apk/assets/index.android.bundle" 2>/dev/null)
  echo "1) Bundle de JavaScript: cabecera ${magia}"
  if [ "$magia" = "c61fbc03c103191f" ]; then
    echo "   -> Hermes bytecode (el código JS no va como texto legible)"
  else
    echo "   -> NO es Hermes bytecode"
  fi
  echo
  echo "2) R8: archivo de mapeo de la compilación (nombre original -> nombre ofuscado)"
  MAPA="${MAPA_R8:-}"
  if [ -n "$MAPA" ] && [ -f "$MAPA" ]; then
    clases=$(grep -c -E '^[^ #].* -> .*:$' "$MAPA" || true)
    renombradas=$(grep -E '^[^ #].* -> .*:$' "$MAPA" | awk '{n=$1; o=$3; sub(/:$/,"",o); if (n!=o) c++} END{print c+0}')
    echo "   Clases en el mapeo: ${clases}; renombradas por R8: ${renombradas}"
    echo "   Ejemplos:"; grep -E '^[^ #].* -> .*:$' "$MAPA" | awk '{o=$3; sub(/:$/,"",o); if ($1!=o) print "     " $1 " -> " o}' | grep -v '^     android\.' | head -5
  else
    echo "   (no se encontró mapping.txt: R8 no corrió)"
  fi
  echo
  echo "3) Firma (apksigner):"
  "$BT/apksigner" verify --verbose --print-certs "$APK" 2>&1 | grep -E 'Verified using|Signer #1 certificate (DN|SHA-256)' | sed 's/^/   /'
  echo
  echo "Nota: el APK de prueba se firma con el certificado de depuración de la plantilla de Expo."
  echo "En producción se firmaría con el certificado de Google Play (Play App Signing) y freeRASP"
  echo "llevaría esa huella; la lógica de detección de re-firmado (appIntegrity) es la misma."
} > "$OUT/EVD-5-11_ofuscacion_firma.txt" 2>&1

cat "$OUT/EVD-4-11_apk_secretos_manifiesto.txt" "$OUT/EVD-5-11_ofuscacion_firma.txt"
rm -rf "$TMP"
[ "$FALLAS" -eq 0 ]
