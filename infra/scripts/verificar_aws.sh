#!/usr/bin/env bash
# Verificación de los controles de la Fase 2 sobre lo desplegado en AWS.
# Corre en GitHub Actions después de `terraform apply`, con el rol de despliegue.
# Deja la evidencia en texto en $SALIDA (sin número de cuenta: se reemplaza).
#   EVD-3-11  Simulador de políticas IAM: matriz rol x tabla (menor privilegio)
#   EVD-3-12  Prueba de TLS: 1.3 aceptado, 1.2 rechazado (CTRL-08)
#   EVD-5-04  Cifrado en reposo: DynamoDB con la CMK, rotación de la llave (CTRL-19)
#   EVD-3-13  Configuración de identidad, API y auditoría (Cognito, API Gateway, CloudTrail)
set -uo pipefail

SALIDA="${SALIDA:-evidencias}"
REGION="us-east-1"
mkdir -p "$SALIDA"
CUENTA="$(aws sts get-caller-identity --query Account --output text)"
FECHA="$(date -u '+%Y-%m-%d %H:%M:%S UTC')"
API_HOST="$(terraform -chdir=infra output -raw api_host)"
API_URL="$(terraform -chdir=infra output -raw api_url)"
API_ID="${API_HOST%%.*}"
FALLAS=0

encabezado() { printf '%s\nFecha: %s\nRegión: %s\n\n' "$1" "$FECHA" "$REGION"; }
falla() { echo "FALLA: $1"; FALLAS=$((FALLAS + 1)); }

# ---------- EVD-3-12: TLS ----------
{
  encabezado "EVD-3-12 Prueba de TLS contra el endpoint de API Gateway (CTRL-08)"
  echo "Host: ${API_HOST}"
  echo "Cliente: $(openssl version)"
  echo
  echo "1) Conexión forzando TLS 1.3 (debe funcionar):"
  if r=$(echo | timeout 20 openssl s_client -connect "${API_HOST}:443" -servername "$API_HOST" -tls1_3 2>&1); then
    echo "$r" | grep -E "^(New|Protocol|    Protocol|    Cipher)|Verification" | sed 's/^/   /'
    echo "$r" | grep -q "TLSv1.3" && echo "   Resultado: ACEPTADA con TLSv1.3" || falla "no se negoció TLS 1.3"
  else
    echo "$r" | tail -3 | sed 's/^/   /'; falla "TLS 1.3 rechazado"
  fi
  echo
  echo "2) Conexión forzando TLS 1.2 (debe ser rechazada):"
  # openssl puede terminar sin error aunque el servidor rechace el saludo; lo que cuenta
  # es si se acordó un cifrado ("Cipher is (NONE)" = no hubo conexión TLS).
  r=$(echo | timeout 20 openssl s_client -connect "${API_HOST}:443" -servername "$API_HOST" -tls1_2 2>&1)
  echo "$r" | grep -E "^New,|alert|handshake failure" | head -3 | sed 's/^/   /'
  if echo "$r" | grep -qE "^New, TLSv1\.2, Cipher is [A-Z0-9]"; then
    falla "el endpoint aceptó TLS 1.2"
  else
    echo "   Resultado: RECHAZADA (no se acordó ningún cifrado; correcto)"
  fi
  echo
  echo "3) Política de seguridad configurada en la API:"
  aws apigateway get-rest-api --rest-api-id "$API_ID" \
    --query '{politica:securityPolicy,modo:endpointAccessMode,tipo:endpointConfiguration.types}' --output json | sed 's/^/   /'
  echo
  echo "4) Solicitud sin token (debe responder 401 del authorizer de Cognito):"
  # x-amzn-ErrorType dice quién rechazó: UnauthorizedException = authorizer de Cognito;
  # MissingAuthenticationTokenException = la ruta no existe en la etapa.
  for ruta in /me /ruta-que-no-existe; do
    cab=$(curl -s -o /dev/null -D - --tlsv1.3 "${API_URL}${ruta}")
    codigo=$(echo "$cab" | awk 'NR==1{print $2}')
    tipo=$(echo "$cab" | grep -i '^x-amzn-errortype' | cut -d: -f2- | tr -d ' \r')
    echo "   GET ${ruta} sin Authorization -> HTTP ${codigo} (${tipo:-sin tipo})"
    [ "$ruta" = "/me" ] && { [ "$codigo" = "401" ] || falla "GET /me sin token respondió ${codigo} (${tipo:-sin tipo})"; }
  done
  echo "   URL de la etapa: ${API_URL}" | sed "s#https://[^.]*\.#https://<api>.#"
} > "$SALIDA/EVD-3-12_tls13.txt" 2>&1

# ---------- EVD-3-11: menor privilegio ----------
{
  encabezado "EVD-3-11 Simulador de políticas IAM: qué puede hacer cada rol de Lambda en cada tabla (CTRL-12)"
  echo "Acciones probadas: dynamodb:GetItem, dynamodb:Query, dynamodb:PutItem, dynamodb:Scan"
  echo "allowed = permitido · implicitDeny = denegado (no hay permiso)"
  echo
  printf '%-15s' "rol \\ tabla"
  TABLAS="perfiles pin cuentas movimientos transferencias beneficiarios presupuestos auditoria"
  for t in $TABLAS; do printf '%-16s' "$t"; done; echo
  for s in svc-profile svc-accounts svc-transfers svc-budgets svc-admin; do
    printf '%-15s' "$s"
    for t in $TABLAS; do
      dec=$(aws iam simulate-principal-policy \
        --policy-source-arn "arn:aws:iam::${CUENTA}:role/qwallet-${s}" \
        --action-names dynamodb:GetItem dynamodb:Query dynamodb:PutItem dynamodb:Scan \
        --resource-arns "arn:aws:dynamodb:${REGION}:${CUENTA}:table/qwallet-${t}" \
        --query 'EvaluationResults[].[EvalActionName,EvalDecision]' --output text)
      cel=""
      while read -r accion decision; do
        [ "$decision" = "allowed" ] && cel="${cel}${accion#dynamodb:} "
      done <<< "$dec"
      [ -z "$cel" ] && cel="(nada)"
      printf '%-16s' "$(echo "$cel" | sed 's/GetItem/G/;s/Query/Q/;s/PutItem/P/;s/Scan/S/' | tr -d ' ')"
    done
    echo
  done
  echo
  echo "Leyenda: G = GetItem, Q = Query, P = PutItem, S = Scan, (nada) = todo denegado"
  echo
  echo "Caso del plan de pruebas: svc-budgets intenta leer la tabla de transferencias"
  aws iam simulate-principal-policy \
    --policy-source-arn "arn:aws:iam::${CUENTA}:role/qwallet-svc-budgets" \
    --action-names dynamodb:GetItem dynamodb:Query dynamodb:Scan \
    --resource-arns "arn:aws:dynamodb:${REGION}:${CUENTA}:table/qwallet-transferencias" \
    --query 'EvaluationResults[].{accion:EvalActionName,decision:EvalDecision}' --output table
  n=$(aws iam simulate-principal-policy \
    --policy-source-arn "arn:aws:iam::${CUENTA}:role/qwallet-svc-budgets" \
    --action-names dynamodb:GetItem dynamodb:Query dynamodb:Scan \
    --resource-arns "arn:aws:dynamodb:${REGION}:${CUENTA}:table/qwallet-transferencias" \
    --query "length(EvaluationResults[?EvalDecision=='allowed'])" --output text)
  [ "$n" = "0" ] || falla "svc-budgets puede leer transferencias"
  echo
  echo "Ninguna Lambda tiene dynamodb:Scan (exfiltración masiva, CTRL-05):"
  for s in svc-profile svc-accounts svc-transfers svc-budgets svc-admin; do
    d=$(aws iam simulate-principal-policy --policy-source-arn "arn:aws:iam::${CUENTA}:role/qwallet-${s}" \
      --action-names dynamodb:Scan --resource-arns "arn:aws:dynamodb:${REGION}:${CUENTA}:table/*" \
      --query 'EvaluationResults[0].EvalDecision' --output text)
    echo "   ${s}: ${d}"
    [ "$d" = "allowed" ] && falla "${s} tiene Scan"
  done
  echo
  echo "Límite de permisos asignado a cada rol:"
  for s in svc-profile svc-accounts svc-transfers svc-budgets svc-admin; do
    echo "   qwallet-${s}: $(aws iam get-role --role-name "qwallet-${s}" --query 'Role.PermissionsBoundary.PermissionsBoundaryArn' --output text)"
  done
} > "$SALIDA/EVD-3-11_iam_menor_privilegio.txt" 2>&1

# ---------- EVD-5-04: cifrado en reposo ----------
{
  encabezado "EVD-5-04 Cifrado en reposo con la llave propia (CTRL-19)"
  LLAVE=$(aws kms describe-key --key-id alias/qwallet-datos --query 'KeyMetadata.Arn' --output text)
  echo "Llave alias/qwallet-datos:"
  aws kms describe-key --key-id "$LLAVE" \
    --query 'KeyMetadata.{tipo:KeySpec,uso:KeyUsage,algoritmos:EncryptionAlgorithms,origen:Origin,administrador:KeyManager,estado:KeyState}' --output json | sed 's/^/   /'
  echo "   Nota: SYMMETRIC_DEFAULT = AES-256 en modo GCM (documentación de AWS KMS)."
  echo
  echo "Rotación automática:"
  aws kms get-key-rotation-status --key-id "$LLAVE" --output json | sed 's/^/   /'
  echo
  echo "Tablas de DynamoDB (tipo de cifrado y llave):"
  for t in perfiles pin cuentas movimientos transferencias beneficiarios presupuestos auditoria; do
    r=$(aws dynamodb describe-table --table-name "qwallet-${t}" \
      --query 'Table.SSEDescription.[Status,SSEType,KMSMasterKeyArn]' --output text)
    echo "   qwallet-${t}: ${r}"
    echo "$r" | grep -q "$LLAVE" || falla "qwallet-${t} no usa la CMK"
    pitr=$(aws dynamodb describe-continuous-backups --table-name "qwallet-${t}" \
      --query 'ContinuousBackupsDescription.PointInTimeRecoveryDescription.PointInTimeRecoveryStatus' --output text)
    echo "      recuperación a un punto en el tiempo: ${pitr}"
  done
  echo
  echo "Grupos de log de CloudWatch y su llave:"
  aws logs describe-log-groups --log-group-name-prefix /aws/lambda/qwallet- \
    --query 'logGroups[].[logGroupName,kmsKeyId,retentionInDays]' --output text | sed 's/^/   /'
  aws logs describe-log-groups --log-group-name-prefix /aws/apigateway/qwallet- \
    --query 'logGroups[].[logGroupName,kmsKeyId,retentionInDays]' --output text | sed 's/^/   /'
} > "$SALIDA/EVD-5-04_cifrado_reposo.txt" 2>&1

# ---------- EVD-3-13: identidad, API y auditoría ----------
{
  encabezado "EVD-3-13 Configuración desplegada: Cognito, API Gateway y CloudTrail (CTRL-18, CTRL-20)"
  POOL=$(aws cognito-idp list-user-pools --max-results 20 --query "UserPools[?Name=='qwallet-usuarios'].Id" --output text)
  echo "Cognito (user pool qwallet-usuarios):"
  aws cognito-idp describe-user-pool --user-pool-id "$POOL" \
    --query 'UserPool.{mfa:MfaConfiguration,plan:UserPoolTier,proteccionBorrado:DeletionProtection,largoMinimoClave:Policies.PasswordPolicy.MinimumLength}' --output json | sed 's/^/   /'
  CLIENTE=$(aws cognito-idp list-user-pool-clients --user-pool-id "$POOL" --query "UserPoolClients[?ClientName=='qwallet-app-android'].ClientId" --output text)
  aws cognito-idp describe-user-pool-client --user-pool-id "$POOL" --client-id "$CLIENTE" \
    --query 'UserPoolClient.{flujos:AllowedOAuthFlows,alcances:AllowedOAuthScopes,tieneSecreto:ClientSecret!=null,accessTokenMin:AccessTokenValidity,refreshHoras:RefreshTokenValidity,rotacionRefresh:RefreshTokenRotation.Feature,revocacion:EnableTokenRevocation}' \
    --output json | sed 's/^/   /'
  echo
  echo "API Gateway: métodos y su autorización"
  aws apigateway get-resources --rest-api-id "$API_ID" --embed methods --limit 100 \
    --query 'items[].[path, resourceMethods && join(`,`, keys(resourceMethods))]' --output text | sort | sed 's/^/   /'
  echo
  echo "   Métodos sin autorización (debe estar vacío):"
  for rid in $(aws apigateway get-resources --rest-api-id "$API_ID" --limit 100 --query 'items[].id' --output text); do
    for m in $(aws apigateway get-resources --rest-api-id "$API_ID" --limit 100 \
        --query "items[?id=='${rid}'].resourceMethods | [0] | keys(@)" --output text 2>/dev/null); do
      [ "$m" = "None" ] && continue
      a=$(aws apigateway get-method --rest-api-id "$API_ID" --resource-id "$rid" --http-method "$m" --query authorizationType --output text)
      [ "$a" != "COGNITO_USER_POOLS" ] && { echo "   ${m} ${rid}: ${a}"; falla "método sin Cognito"; }
    done
  done
  echo
  echo "Throttling de la etapa v1:"
  aws apigateway get-stage --rest-api-id "$API_ID" --stage-name v1 \
    --query 'methodSettings."*/*".{rafaga:throttlingBurstLimit,porSegundo:throttlingRateLimit,logEjecucion:loggingLevel}' --output json | sed 's/^/   /'
  echo
  echo "CloudTrail:"
  aws cloudtrail get-trail --name qwallet-auditoria \
    --query 'Trail.{multiregion:IsMultiRegionTrail,validacionIntegridad:LogFileValidationEnabled,cifrado:KmsKeyId!=null}' --output json | sed 's/^/   /'
  aws cloudtrail get-trail-status --name qwallet-auditoria --query '{registrando:IsLogging}' --output json | sed 's/^/   /'
} > "$SALIDA/EVD-3-13_identidad_api_auditoria.txt" 2>&1

# Quita el número de cuenta de toda la evidencia (el repo es público).
for f in "$SALIDA"/*.txt; do
  sed -i "s/${CUENTA}/************/g" "$f"
done

grep -h "FALLA:" "$SALIDA"/*.txt || true
echo "Verificación terminada. Fallas: ${FALLAS}"
[ "$FALLAS" -eq 0 ]
