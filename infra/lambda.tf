# Cinco microservicios en Lambda, empaquetados como imagen de contenedor (ECR).
# Sin VPC: las Lambdas solo hablan con servicios administrados por sus endpoints
# públicos con TLS y permisos IAM; una VPC con salida a internet exigiría NAT
# Gateway (prohibido por costo). La segmentación es lógica, por rol IAM (capa 4).

resource "aws_cloudwatch_log_group" "lambda" {
  for_each = toset(local.servicios)

  name              = "/aws/lambda/${local.prefijo}-${each.key}"
  retention_in_days = var.retencion_logs_dias
  kms_key_id        = aws_kms_key.datos.arn
}

resource "aws_lambda_function" "servicio" {
  for_each = toset(local.servicios)

  #checkov:skip=CKV_AWS_117:Sin VPC a propósito: una VPC con salida exigiría NAT Gateway (prohibido por costo). Segmentación por rol IAM (capa 4).
  #checkov:skip=CKV_AWS_116:Invocación síncrona desde API Gateway: el error vuelve al cliente; una cola de mensajes fallidos no aplica.
  #checkov:skip=CKV_AWS_115:La cuenta nueva tiene un límite de 10 ejecuciones simultáneas; reservar concurrencia por función no es posible. El límite lo pone el throttling de API Gateway.
  #checkov:skip=CKV_AWS_272:La firma de código de Lambda no aplica a imágenes de contenedor; la integridad la da la etiqueta inmutable de ECR.

  function_name = "${local.prefijo}-${each.key}"
  description   = "Q-Wallet ${each.key}"
  role          = aws_iam_role.lambda[each.key].arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.servicio[each.key].repository_url}:${var.image_tag}"
  architectures = ["x86_64"]
  memory_size   = 256
  timeout       = 10
  kms_key_arn   = aws_kms_key.datos.arn

  environment {
    variables = {
      SERVICIO             = each.key
      TABLA_PERFILES       = aws_dynamodb_table.tabla["perfiles"].name
      TABLA_PIN            = aws_dynamodb_table.tabla["pin"].name
      TABLA_CUENTAS        = aws_dynamodb_table.tabla["cuentas"].name
      TABLA_MOVIMIENTOS    = aws_dynamodb_table.tabla["movimientos"].name
      TABLA_TRANSFERENCIAS = aws_dynamodb_table.tabla["transferencias"].name
      TABLA_BENEFICIARIOS  = aws_dynamodb_table.tabla["beneficiarios"].name
      TABLA_PRESUPUESTOS   = aws_dynamodb_table.tabla["presupuestos"].name
      TABLA_AUDITORIA      = aws_dynamodb_table.tabla["auditoria"].name
      USER_POOL_ID         = aws_cognito_user_pool.usuarios.id

      # La Lambda vuelve a verificar el access token (firma, cliente y scope): CTRL-18.
      COGNITO_CLIENT_ID = aws_cognito_user_pool_client.app_android.id
      API_SCOPE         = "${aws_cognito_resource_server.api.identifier}/api"
    }
  }

  tracing_config {
    mode = "Active"
  }

  logging_config {
    log_format = "JSON"
    log_group  = aws_cloudwatch_log_group.lambda[each.key].name
  }

  depends_on = [aws_iam_role_policy.lambda, aws_ecr_repository_policy.servicio]
}

# API Gateway solo puede invocar cada función desde la etapa v1 de esta API.
resource "aws_lambda_permission" "apigateway" {
  for_each = toset(local.servicios)

  statement_id  = "PermitirApiGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.servicio[each.key].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/${local.etapa}/*/*"
}
