#!/usr/bin/env bash
# SIEM en CloudWatch de punta a punta (bloque 5, secciones 5.3 y 5.4). Lo corre waf-siem.yml.
# Uso: bash infra/pruebas/siem.sh <subcomando> <carpeta-de-salida> [args]
#   reglas            EVD-5-06a  cada regla de correlación contra una muestra de ataque y una normal
#   denegaciones      genera 6 llamadas reales negadas por IAM (iam:ListUsers) para la regla CIS 4.1
#   esperar <seg> <alarma>...  espera a que las alarmas pasen a ALARM (o se acabe el tiempo)
#   alarmas           EVD-5-06b  estado e historial de las alarmas (incluye el envío a SNS)
#   consultas         EVD-5-06c  consultas de correlación sobre la última hora
#   waf               EVD-5-02b  qué regla del WAF bloqueó cada caso de la prueba
#   graficas          EVD-5-07   imágenes del tablero (GetMetricWidgetImage)
set -uo pipefail

CMD="$1"; OUT="$2"; shift 2
mkdir -p "$OUT"
R=us-east-1
NS="QWallet/Seguridad"
FECHA() { date -u '+%Y-%m-%d %H:%M:%S UTC'; }

consulta() { # grupo minutos consulta -> tabla de texto
  local grupo="$1" min="$2" q="$3" id estado
  id=$(aws logs start-query --log-group-name "$grupo" --start-time $(( $(date +%s) - min * 60 )) \
    --end-time "$(date +%s)" --query-string "$q" --query queryId --output text 2>&1) || { echo "   (error: $id)"; return; }
  for _ in $(seq 1 30); do
    estado=$(aws logs get-query-results --query-id "$id" --query status --output text)
    [ "$estado" = "Complete" ] && break; sleep 2
  done
  aws logs get-query-results --query-id "$id" --output json | python3 -c '
import json, sys
r = json.load(sys.stdin)["results"]
if not r:
    print("   (sin resultados)")
for fila in r:
    print("   " + " | ".join(f"{c[\"field\"]}={c[\"value\"]}" for c in fila if not c["field"].startswith("@ptr")))'
}

case "$CMD" in
reglas)
  {
    echo "EVD-5-06a Reglas de correlación del SIEM probadas contra muestras (aws logs test-metric-filter)"
    echo "Fecha: $(FECHA)"
    echo "Cada regla debe coincidir con la muestra de ataque y NO con la muestra normal."
    echo
    probar() { # nombre patrón ataque normal
      local a n
      a=$(aws logs test-metric-filter --cli-input-json "$(jq -nc --arg p "$2" --arg m "$3" '{filterPattern:$p, logEventMessages:[$m]}')" --query 'length(matches)' --output text)
      n=$(aws logs test-metric-filter --cli-input-json "$(jq -nc --arg p "$2" --arg m "$4" '{filterPattern:$p, logEventMessages:[$m]}')" --query 'length(matches)' --output text)
      local r="FALLA"; [ "$a" = "1" ] && [ "$n" = "0" ] && r="OK"
      printf '   %-26s ataque=%s normal=%s  %s\n' "$1" "$a" "$n" "$r"
    }
    aws logs describe-metric-filters --log-group-name /aws/lambda/qwallet-svc-transfers \
      --query 'metricFilters[].[metricTransformations[0].metricName, filterPattern]' --output text > /tmp/f_lambda.txt
    aws logs describe-metric-filters --log-group-name /aws/apigateway/qwallet-api \
      --query 'metricFilters[].[metricTransformations[0].metricName, filterPattern]' --output text > /tmp/f_api.txt
    aws logs describe-metric-filters --log-group-name /aws/cloudtrail/qwallet-auditoria \
      --query 'metricFilters[].[metricTransformations[0].metricName, filterPattern]' --output text > /tmp/f_trail.txt
    pat() { awk -F'\t' -v m="$2" '$1==m{print $2}' "$1"; }
    L='{"nivel":"aviso","evento":"solicitud_rechazada","servicio":"svc-transfers","correlationId":"c-1","ruta":"POST /transfers","status":%s,"codigo":"%s"}'
    OKL='{"nivel":"info","evento":"solicitud","servicio":"svc-transfers","correlationId":"c-2","ruta":"GET /transfers/{id}","status":200}'
    echo "Logs de las Lambdas (formato de services/comun/src/registro.ts):"
    probar pin_bloqueado "$(pat /tmp/f_lambda.txt pin_bloqueado)" "$(printf "$L" 423 pin_bloqueado)" "$OKL"
    probar pin_incorrecto "$(pat /tmp/f_lambda.txt pin_incorrecto)" "$(printf "$L" 403 pin_incorrecto)" "$OKL"
    probar acceso_prohibido "$(pat /tmp/f_lambda.txt acceso_prohibido)" "$(printf "$L" 403 prohibido)" "$OKL"
    probar entrada_invalida "$(pat /tmp/f_lambda.txt entrada_invalida)" "$(printf "$L" 400 solicitud_invalida)" "$OKL"
    probar error_no_controlado "$(pat /tmp/f_lambda.txt error_no_controlado)" \
      '{"nivel":"error","evento":"error_no_controlado","servicio":"svc-transfers","ruta":"POST /transfers","tipo":"TypeError"}' "$OKL"
    echo
    A='{"requestId":"r-1","ip":"203.0.113.7","usuario":"-","metodo":"GET","ruta":"/me","estado":"%s","error":"-","waf":"%s"}'
    echo "Log de acceso de API Gateway:"
    probar api_no_autenticado "$(pat /tmp/f_api.txt api_no_autenticado)" "$(printf "$A" 401 -)" "$(printf "$A" 200 -)"
    probar api_limite "$(pat /tmp/f_api.txt api_limite)" "$(printf "$A" 429 -)" "$(printf "$A" 200 -)"
    probar api_bloqueo_waf "$(pat /tmp/f_api.txt api_bloqueo_waf)" "$(printf "$A" 403 403)" "$(printf "$A" 200 200)"
    echo
    echo "CloudTrail (eventos reales de AWS, recortados):"
    probar trail_no_autorizado "$(pat /tmp/f_trail.txt trail_no_autorizado)" \
      '{"eventSource":"iam.amazonaws.com","eventName":"ListUsers","errorCode":"AccessDenied","userIdentity":{"type":"AssumedRole","sessionContext":{"sessionIssuer":{"userName":"qwallet-gha-despliegue"}}}}' \
      '{"eventSource":"iam.amazonaws.com","eventName":"ListUsers","errorCode":"AccessDenied","userIdentity":{"type":"AssumedRole","sessionContext":{"sessionIssuer":{"userName":"qwallet-gha-pentest"}}}}'
    probar trail_uso_root "$(pat /tmp/f_trail.txt trail_uso_root)" \
      '{"eventName":"GetAccountSummary","eventType":"AwsApiCall","userIdentity":{"type":"Root"}}' \
      '{"eventName":"GetAccountSummary","eventType":"AwsApiCall","userIdentity":{"type":"AssumedRole"}}'
    probar trail_consola_sin_mfa "$(pat /tmp/f_trail.txt trail_consola_sin_mfa)" \
      '{"eventName":"ConsoleLogin","additionalEventData":{"MFAUsed":"No"},"responseElements":{"ConsoleLogin":"Success"}}' \
      '{"eventName":"ConsoleLogin","additionalEventData":{"MFAUsed":"Yes"},"responseElements":{"ConsoleLogin":"Success"}}'
    probar trail_auditoria_y_llaves "$(pat /tmp/f_trail.txt trail_auditoria_y_llaves)" \
      '{"eventSource":"cloudtrail.amazonaws.com","eventName":"StopLogging"}' '{"eventSource":"cloudtrail.amazonaws.com","eventName":"LookupEvents"}'
    probar trail_cambios_iam "$(pat /tmp/f_trail.txt trail_cambios_iam)" \
      '{"eventSource":"iam.amazonaws.com","eventName":"PutRolePolicy"}' '{"eventSource":"iam.amazonaws.com","eventName":"GetRole"}'
    probar trail_admin_cognito "$(pat /tmp/f_trail.txt trail_admin_cognito)" \
      '{"eventSource":"cognito-idp.amazonaws.com","eventName":"AdminDisableUser"}' '{"eventSource":"cognito-idp.amazonaws.com","eventName":"ListUsers"}'
  } > "$OUT/EVD-5-06a_reglas_correlacion.txt" 2>&1
  cat "$OUT/EVD-5-06a_reglas_correlacion.txt"
  ;;

denegaciones)
  echo "Generando 6 llamadas que IAM debe negar (iam:ListUsers no está en el rol de despliegue):"
  for i in 1 2 3 4 5 6; do
    aws iam list-users --max-items 1 >/dev/null 2>&1 && echo "   $i: PERMITIDA (inesperado)" || echo "   $i: negada"
    sleep 2
  done
  echo "$(FECHA)" > "$OUT/.denegaciones_desde"
  ;;

esperar)
  max="$1"; shift
  t0=$(date +%s)
  while [ $(( $(date +%s) - t0 )) -lt "$max" ]; do
    pendientes=0
    for a in "$@"; do
      s=$(aws cloudwatch describe-alarms --alarm-names "$a" --query 'MetricAlarms[0].StateValue' --output text)
      [ "$s" = "ALARM" ] || pendientes=$((pendientes + 1))
    done
    [ "$pendientes" -eq 0 ] && { echo "Todas en ALARM tras $(( $(date +%s) - t0 )) s"; exit 0; }
    sleep 30
  done
  echo "Tiempo agotado (${max} s); se registra el estado tal cual."
  ;;

alarmas)
  {
    echo "EVD-5-06b Alarmas de seguridad: estado y disparos reales (CTRL-20)"
    echo "Fecha: $(FECHA)"
    echo
    echo "Estado actual:"
    aws cloudwatch describe-alarms --alarm-name-prefix qwallet- \
      --query 'MetricAlarms[].[AlarmName, StateValue, StateUpdatedTimestamp]' --output text | sed 's/^/   /'
    echo
    echo "Historial de las últimas 2 horas (cambios de estado y envío del aviso a SNS):"
    aws cloudwatch describe-alarm-history --alarm-name-prefix qwallet- \
      --start-date "$(date -u -d '-2 hours' '+%Y-%m-%dT%H:%M:%SZ')" --max-records 60 \
      --query 'AlarmHistoryItems[].[Timestamp, AlarmName, HistoryItemType, HistorySummary]' --output text \
      | sed -E 's/arn:aws:sns:[^ ]*/[tema SNS qwallet-alertas]/g; s/^/   /'
  } > "$OUT/EVD-5-06b_alarmas.txt" 2>&1
  cat "$OUT/EVD-5-06b_alarmas.txt"
  ;;

consultas)
  {
    echo "EVD-5-06c Correlación de eventos entre fuentes (Logs Insights, última hora)"
    echo "Fecha: $(FECHA)"
    echo
    echo "1) IPs sospechosas en el perímetro (401 + 403 + 429 por IP; log de acceso de API Gateway):"
    consulta /aws/apigateway/qwallet-api 60 'filter estado = "401" or estado = "429" or waf = "403" | stats count(*) as eventos by ip, estado, waf | filter eventos >= 10 | sort eventos desc | limit 10'
    echo
    echo "2) Llamadas a AWS negadas por IAM, por rol (CloudTrail):"
    consulta /aws/cloudtrail/qwallet-auditoria 90 'filter errorCode like /AccessDenied|Unauthorized/ | stats count(*) as negadas by userIdentity.sessionContext.sessionIssuer.userName as rol, eventName | sort negadas desc | limit 10'
    echo
    echo "3) Cambios de configuración de seguridad hechos por el despliegue (CloudTrail):"
    consulta /aws/cloudtrail/qwallet-auditoria 90 'filter eventSource in ["wafv2.amazonaws.com","cloudtrail.amazonaws.com","kms.amazonaws.com"] and readOnly = 0 | stats count(*) as cambios by eventSource, eventName | sort cambios desc | limit 10'
    echo
    echo "4) Rechazos de la aplicación por regla (logs JSON de las Lambdas, 24 h):"
    consulta /aws/lambda/qwallet-svc-transfers 1440 'filter evento = "solicitud_rechazada" | stats count(*) as rechazos by codigo | sort rechazos desc'
  } > "$OUT/EVD-5-06c_correlacion.txt" 2>&1
  sed -i -E 's/arn:aws:[a-z0-9-]+:[a-z0-9-]*:[0-9*]{12}:[^ |]*/[ARN]/g' "$OUT/EVD-5-06c_correlacion.txt"
  cat "$OUT/EVD-5-06c_correlacion.txt"
  ;;

waf)
  {
    echo "EVD-5-02b Logs del WAF: regla que decidió cada caso (CTRL-17)"
    echo "Fecha: $(FECHA)"
    echo "Fuente: grupo aws-waf-logs-qwallet (la cabecera Authorization se redacta)."
    echo
    consulta aws-waf-logs-qwallet 60 'parse httpRequest.args /caso=(?<caso>C[0-9]+)/ | filter ispresent(caso) | stats count(*) as solicitudes, latest(action) as accion by caso, terminatingRuleId, terminatingRuleType | sort caso asc'
    echo
    echo "Reglas administradas: sub-regla exacta que coincidió en los bloqueos:"
    consulta aws-waf-logs-qwallet 60 'filter action = "BLOCK" | parse httpRequest.args /caso=(?<caso>C[0-9]+)/ | stats count(*) by caso, terminatingRuleId, ruleGroupList.0.terminatingRule.ruleId | sort caso asc'
  } > "$OUT/EVD-5-02b_waf_logs.txt" 2>&1
  cat "$OUT/EVD-5-02b_waf_logs.txt"
  ;;

graficas)
  inicio="-PT2H"
  img() { # archivo json-del-widget
    aws cloudwatch get-metric-widget-image --metric-widget "$2" --output-format png --query MetricWidgetImage --output text \
      | base64 -d > "$OUT/$1" && echo "   $1: $(du -h "$OUT/$1" | cut -f1)"
  }
  echo "Gráficas del tablero qwallet-seguridad:"
  img EVD-5-07a_perimetro.png "{\"title\":\"Perímetro: 401, 429 y bloqueos del WAF (API Gateway)\",\"width\":900,\"height\":360,\"start\":\"$inicio\",\"period\":60,\"stat\":\"Sum\",\"metrics\":[[\"$NS\",\"api_no_autenticado\",{\"label\":\"401 sin token\"}],[\"$NS\",\"api_limite\",{\"label\":\"429 throttling\"}],[\"$NS\",\"api_bloqueo_waf\",{\"label\":\"403 WAF\"}]]}"
  img EVD-5-07b_cuenta.png "{\"title\":\"Cuenta AWS: eventos de CloudTrail por regla\",\"width\":900,\"height\":360,\"start\":\"$inicio\",\"period\":60,\"stat\":\"Sum\",\"metrics\":[[\"$NS\",\"trail_no_autorizado\",{\"label\":\"Llamadas negadas por IAM\"}],[\"$NS\",\"trail_cambios_iam\",{\"label\":\"Cambios IAM\"}],[\"$NS\",\"trail_auditoria_y_llaves\",{\"label\":\"Cambios a auditoría/KMS\"}]]}"
  if [ "${1:-}" = "waf" ]; then
    img EVD-5-02c_waf_metricas.png "{\"title\":\"AWS WAF: solicitudes permitidas y bloqueadas\",\"width\":900,\"height\":360,\"start\":\"-PT1H\",\"period\":60,\"stat\":\"Sum\",\"metrics\":[[\"AWS/WAFV2\",\"BlockedRequests\",\"WebACL\",\"qwallet-api\",\"Region\",\"$R\",\"Rule\",\"ALL\",{\"label\":\"Bloqueadas\",\"color\":\"#EF4444\"}],[\"AWS/WAFV2\",\"AllowedRequests\",\"WebACL\",\"qwallet-api\",\"Region\",\"$R\",\"Rule\",\"ALL\",{\"label\":\"Permitidas\",\"color\":\"#10B981\"}]]}"
  fi
  ;;
*)
  echo "Subcomando desconocido: $CMD"; exit 2 ;;
esac
