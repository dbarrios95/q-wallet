# CTRL-12: un rol IAM de menor privilegio por Lambda.
# Cada rol solo puede usar las acciones y tablas que su servicio necesita
# (sin comodines de acción ni de tabla). Todos llevan el límite de permisos
# qwallet-limite-permisos, creado en el bootstrap: aunque alguien edite una
# política, el rol nunca puede pasar de ese techo.

locals {
  limite_permisos_arn = "arn:${local.particion}:iam::${local.cuenta}:policy/${local.prefijo}-limite-permisos"

  # Matriz de acceso a datos (se documenta en la sección 4.2 del informe).
  acceso_tablas = {
    "svc-profile" = [
      { tabla = "perfiles", acciones = ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:UpdateItem"], indice = null },
      { tabla = "perfiles", acciones = ["dynamodb:Query"], indice = "por-telefono" },
      { tabla = "pin", acciones = ["dynamodb:PutItem", "dynamodb:UpdateItem"], indice = null },
      # Bloque 3: al crear el perfil se crea en la misma transacción la cuenta con el saldo
      # simulado y su movimiento inicial. Solo escritura (PutItem), sin lectura ni borrado.
      { tabla = "cuentas", acciones = ["dynamodb:PutItem"], indice = null },
      { tabla = "movimientos", acciones = ["dynamodb:PutItem"], indice = null },
      { tabla = "auditoria", acciones = ["dynamodb:PutItem"], indice = null },
    ]
    "svc-accounts" = [
      { tabla = "cuentas", acciones = ["dynamodb:GetItem", "dynamodb:Query"], indice = null },
      { tabla = "movimientos", acciones = ["dynamodb:Query"], indice = null },
    ]
    "svc-transfers" = [
      { tabla = "perfiles", acciones = ["dynamodb:Query"], indice = "por-telefono" },
      { tabla = "pin", acciones = ["dynamodb:GetItem", "dynamodb:UpdateItem"], indice = null },
      { tabla = "cuentas", acciones = ["dynamodb:GetItem", "dynamodb:Query", "dynamodb:UpdateItem", "dynamodb:ConditionCheckItem"], indice = null },
      { tabla = "movimientos", acciones = ["dynamodb:PutItem"], indice = null },
      { tabla = "transferencias", acciones = ["dynamodb:GetItem", "dynamodb:PutItem"], indice = null },
      { tabla = "beneficiarios", acciones = ["dynamodb:Query", "dynamodb:PutItem", "dynamodb:DeleteItem"], indice = null },
      { tabla = "auditoria", acciones = ["dynamodb:PutItem"], indice = null },
    ]
    "svc-budgets" = [
      { tabla = "presupuestos", acciones = ["dynamodb:GetItem", "dynamodb:Query", "dynamodb:PutItem", "dynamodb:UpdateItem"], indice = null },
      { tabla = "cuentas", acciones = ["dynamodb:Query"], indice = null },
      { tabla = "movimientos", acciones = ["dynamodb:Query"], indice = null },
    ]
    "svc-admin" = [
      { tabla = "auditoria", acciones = ["dynamodb:Query", "dynamodb:PutItem"], indice = null },
    ]
  }

  # Acciones de Cognito que solo svc-admin puede usar (bloquear y listar usuarios, F7).
  acceso_cognito = {
    "svc-admin" = ["cognito-idp:ListUsers", "cognito-idp:AdminDisableUser", "cognito-idp:AdminUserGlobalSignOut", "cognito-idp:AdminListGroupsForUser"]
  }
}

data "aws_iam_policy_document" "confianza_lambda" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [local.cuenta]
    }
  }
}

resource "aws_iam_role" "lambda" {
  for_each = toset(local.servicios)

  name                 = "${local.prefijo}-${each.key}"
  description          = "Rol de ejecucion de ${each.key} (menor privilegio)"
  assume_role_policy   = data.aws_iam_policy_document.confianza_lambda.json
  permissions_boundary = local.limite_permisos_arn
}

data "aws_iam_policy_document" "lambda" {
  for_each = toset(local.servicios)

  # Datos: solo las tablas (o el índice) de su matriz de acceso.
  dynamic "statement" {
    for_each = local.acceso_tablas[each.key]
    content {
      sid     = "Dynamo${replace(title(statement.value.tabla), "-", "")}${statement.value.indice == null ? "" : "Indice"}"
      actions = statement.value.acciones
      resources = [
        statement.value.indice == null
        ? aws_dynamodb_table.tabla[statement.value.tabla].arn
        : "${aws_dynamodb_table.tabla[statement.value.tabla].arn}/index/${statement.value.indice}"
      ]
    }
  }

  # Llave KMS: solo a través de DynamoDB (tablas) y de Lambda (variables de entorno).
  statement {
    sid       = "KmsViaDynamoDB"
    actions   = ["kms:Decrypt", "kms:Encrypt", "kms:GenerateDataKey", "kms:DescribeKey"]
    resources = [aws_kms_key.datos.arn]
    condition {
      test     = "StringEquals"
      variable = "kms:ViaService"
      values   = ["dynamodb.${local.region}.amazonaws.com"]
    }
  }

  statement {
    sid       = "KmsVariablesEntorno"
    actions   = ["kms:Decrypt"]
    resources = [aws_kms_key.datos.arn]
    condition {
      test     = "StringEquals"
      variable = "kms:EncryptionContext:LambdaFunctionName"
      values   = ["${local.prefijo}-${each.key}"]
    }
  }

  # Logs: solo su propio grupo de log.
  statement {
    sid       = "LogsPropios"
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["${aws_cloudwatch_log_group.lambda[each.key].arn}:*"]
  }

  # Trazas de X-Ray (estas acciones no admiten un recurso específico).
  statement {
    sid       = "TrazasXRay"
    actions   = ["xray:PutTraceSegments", "xray:PutTelemetryRecords"]
    resources = ["*"]
  }

  # Secretos: solo su propia ruta en SSM Parameter Store (CTRL-16).
  statement {
    sid       = "ParametrosPropios"
    actions   = ["ssm:GetParameter"]
    resources = ["arn:${local.particion}:ssm:${local.region}:${local.cuenta}:parameter/${local.prefijo}/${each.key}/*"]
  }

  dynamic "statement" {
    for_each = contains(keys(local.acceso_cognito), each.key) ? [1] : []
    content {
      sid       = "CognitoAdministracion"
      actions   = local.acceso_cognito[each.key]
      resources = [aws_cognito_user_pool.usuarios.arn]
    }
  }
}

resource "aws_iam_role_policy" "lambda" {
  for_each = toset(local.servicios)

  name   = "${local.prefijo}-${each.key}-acceso"
  role   = aws_iam_role.lambda[each.key].id
  policy = data.aws_iam_policy_document.lambda[each.key].json
}

# Rol de cuenta para que API Gateway escriba sus logs de acceso en CloudWatch.
data "aws_iam_policy_document" "confianza_apigateway" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["apigateway.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [local.cuenta]
    }
  }
}

resource "aws_iam_role" "apigateway_logs" {
  name                 = "${local.prefijo}-apigateway-logs"
  description          = "API Gateway escribe logs de acceso en CloudWatch"
  assume_role_policy   = data.aws_iam_policy_document.confianza_apigateway.json
  permissions_boundary = local.limite_permisos_arn
}

resource "aws_iam_role_policy_attachment" "apigateway_logs" {
  role       = aws_iam_role.apigateway_logs.name
  policy_arn = "arn:${local.particion}:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
}

resource "aws_api_gateway_account" "cuenta" {
  cloudwatch_role_arn = aws_iam_role.apigateway_logs.arn
  depends_on          = [aws_iam_role_policy_attachment.apigateway_logs]
}
