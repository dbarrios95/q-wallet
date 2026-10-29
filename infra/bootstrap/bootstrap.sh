#!/usr/bin/env bash
# Bootstrap de Q-Wallet: lo único que se crea a mano, una sola vez, desde AWS CloudShell
# (us-east-1) con un usuario administrador. Todo lo demás lo crea Terraform desde
# GitHub Actions con OIDC (CTRL-21), sin llaves de acceso guardadas.
#
# Crea:
#   1. Bucket S3 del estado de Terraform (ACT-09): Block Public Access, versionado,
#      SSE-KMS, solo TLS. Bloqueo nativo de S3 (use_lockfile), sin DynamoDB.
#   2. Proveedor OIDC de GitHub Actions.
#   3. Política qwallet-limite-permisos: techo de permisos de todo rol que cree Terraform.
#   4. Rol qwallet-gha-plan: solo lectura, solo para pull requests de este repo.
#   5. Rol qwallet-gha-despliegue: solo para el entorno "dev" de GitHub (rama main).
#
# Se puede correr más de una vez: si algo ya existe, lo deja y actualiza las políticas.
# No borra nada.
set -euo pipefail

REGION="us-east-1"
REPO_RAW="https://raw.githubusercontent.com/dbarrios95/q-wallet/main/infra/bootstrap/politicas"
DIR="$(mktemp -d)"
trap 'rm -rf "$DIR"' EXIT

CUENTA="$(aws sts get-caller-identity --query Account --output text)"
BUCKET="qwallet-tfstate-${CUENTA}"
echo "Cuenta: ****${CUENTA: -4}  Región: ${REGION}"

# Descarga las políticas del repo y pone el número de cuenta.
for f in limite-permisos confianza-plan confianza-despliegue lectura-plan despliegue-a despliegue-b; do
  curl -fsSL "${REPO_RAW}/${f}.json" | sed "s/__CUENTA__/${CUENTA}/g" > "${DIR}/${f}.json"
done

echo "== 1. Bucket del estado de Terraform"
if aws s3api head-bucket --bucket "$BUCKET" 2>/dev/null; then
  echo "   ya existe"
else
  aws s3api create-bucket --bucket "$BUCKET" --region "$REGION" >/dev/null
  echo "   creado"
fi
aws s3api put-public-access-block --bucket "$BUCKET" --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
aws s3api put-bucket-versioning --bucket "$BUCKET" --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption --bucket "$BUCKET" --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"aws:kms"},"BucketKeyEnabled":true}]}'
aws s3api put-bucket-policy --bucket "$BUCKET" --policy "{
  \"Version\":\"2012-10-17\",
  \"Statement\":[{\"Sid\":\"SoloTLS\",\"Effect\":\"Deny\",\"Principal\":\"*\",\"Action\":\"s3:*\",
    \"Resource\":[\"arn:aws:s3:::${BUCKET}\",\"arn:aws:s3:::${BUCKET}/*\"],
    \"Condition\":{\"Bool\":{\"aws:SecureTransport\":\"false\"}}}]}"
aws s3api put-bucket-tagging --bucket "$BUCKET" --tagging 'TagSet=[{Key=Project,Value=qwallet},{Key=Env,Value=dev}]'

echo "== 2. Proveedor OIDC de GitHub"
OIDC_ARN="arn:aws:iam::${CUENTA}:oidc-provider/token.actions.githubusercontent.com"
if aws iam get-open-id-connect-provider --open-id-connect-provider-arn "$OIDC_ARN" >/dev/null 2>&1; then
  echo "   ya existe"
else
  aws iam create-open-id-connect-provider --url https://token.actions.githubusercontent.com \
    --client-id-list sts.amazonaws.com >/dev/null
  echo "   creado"
fi

# Crea una política administrada o, si existe, publica una versión nueva
# (borra la versión más vieja que no esté en uso cuando ya hay 5: límite de AWS).
politica() {
  local nombre="$1" archivo="$2" arn="arn:aws:iam::${CUENTA}:policy/$1"
  if aws iam get-policy --policy-arn "$arn" >/dev/null 2>&1; then
    local n
    n=$(aws iam list-policy-versions --policy-arn "$arn" --query 'length(Versions)' --output text)
    if [ "$n" -ge 5 ]; then
      local vieja
      vieja=$(aws iam list-policy-versions --policy-arn "$arn" \
        --query 'Versions[?IsDefaultVersion==`false`]|sort_by(@,&CreateDate)[0].VersionId' --output text)
      aws iam delete-policy-version --policy-arn "$arn" --version-id "$vieja"
    fi
    aws iam create-policy-version --policy-arn "$arn" --policy-document "file://${archivo}" --set-as-default >/dev/null
    echo "   ${nombre}: actualizada"
  else
    aws iam create-policy --policy-name "$nombre" --policy-document "file://${archivo}" \
      --tags Key=Project,Value=qwallet Key=Env,Value=dev >/dev/null
    echo "   ${nombre}: creada"
  fi
}

# Crea un rol o actualiza su confianza.
rol() {
  local nombre="$1" confianza="$2" descripcion="$3"
  if aws iam get-role --role-name "$nombre" >/dev/null 2>&1; then
    aws iam update-assume-role-policy --role-name "$nombre" --policy-document "file://${confianza}"
    echo "   ${nombre}: confianza actualizada"
  else
    aws iam create-role --role-name "$nombre" --assume-role-policy-document "file://${confianza}" \
      --description "$descripcion" --max-session-duration 3600 \
      --tags Key=Project,Value=qwallet Key=Env,Value=dev >/dev/null
    echo "   ${nombre}: creado"
  fi
}

echo "== 3. Límite de permisos"
politica qwallet-limite-permisos "${DIR}/limite-permisos.json"

echo "== 4. Rol de plan (solo lectura, pull requests)"
politica qwallet-gha-plan-lectura "${DIR}/lectura-plan.json"
rol qwallet-gha-plan "${DIR}/confianza-plan.json" "GitHub Actions: terraform plan en PR (solo lectura)"
aws iam attach-role-policy --role-name qwallet-gha-plan \
  --policy-arn "arn:aws:iam::${CUENTA}:policy/qwallet-gha-plan-lectura"

echo "== 5. Rol de despliegue (entorno dev, rama main)"
politica qwallet-gha-despliegue-a "${DIR}/despliegue-a.json"
politica qwallet-gha-despliegue-b "${DIR}/despliegue-b.json"
rol qwallet-gha-despliegue "${DIR}/confianza-despliegue.json" "GitHub Actions: terraform apply en main (entorno dev)"
for p in qwallet-gha-despliegue-a qwallet-gha-despliegue-b; do
  aws iam attach-role-policy --role-name qwallet-gha-despliegue \
    --policy-arn "arn:aws:iam::${CUENTA}:policy/${p}"
done

echo
echo "Listo. Falta un paso en GitHub: crear el secreto AWS_ACCOUNT_ID con este valor."
echo "Cópielo de aquí y no lo pegue en el chat ni en el repo:"
echo
echo "    ${CUENTA}"
