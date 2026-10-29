# API Gateway REST regional (WAF solo se asocia a REST).
# CTRL-08: solo TLS 1.3 en el endpoint por defecto (política mejorada, modo STRICT).
# CTRL-18: authorizer de Cognito con scope propio en cada método.
# CTRL-05 / CTRL-17: throttling por etapa y por método.
# CTRL-13: respuestas de error genéricas con cabeceras de seguridad.

locals {
  etapa = "v1"

  # Árbol de recursos por nivel (la API no permite referenciar un for_each a sí mismo).
  recursos_n1 = toset(["me", "users", "pin", "accounts", "transfers", "beneficiaries", "categories", "budgets", "admin"])
  recursos_n2 = {
    "users/search"          = { padre = "users", parte = "search" }
    "accounts/{accountId}"  = { padre = "accounts", parte = "{accountId}" }
    "transfers/{id}"        = { padre = "transfers", parte = "{id}" }
    "admin/users"           = { padre = "admin", parte = "users" }
    "admin/audit"           = { padre = "admin", parte = "audit" }
  }
  recursos_n3 = {
    "accounts/{accountId}/transactions" = { padre = "accounts/{accountId}", parte = "transactions" }
    "admin/users/{id}"                  = { padre = "admin/users", parte = "{id}" }
  }
  recursos_n4 = {
    "admin/users/{id}/block" = { padre = "admin/users/{id}", parte = "block" }
  }

  # Superficie de la API (CONTEXTO, sección 4; Tabla 7 del informe).
  rutas = {
    "GET /me"                                = { servicio = "svc-profile", recurso = "me", parametros = {} }
    "PATCH /me"                              = { servicio = "svc-profile", recurso = "me", parametros = {} }
    "GET /users/search"                      = { servicio = "svc-profile", recurso = "users/search", parametros = { "method.request.querystring.phone" = true } }
    "POST /pin"                              = { servicio = "svc-profile", recurso = "pin", parametros = {} }
    "GET /accounts"                          = { servicio = "svc-accounts", recurso = "accounts", parametros = {} }
    "GET /accounts/{accountId}/transactions" = { servicio = "svc-accounts", recurso = "accounts/{accountId}/transactions", parametros = { "method.request.path.accountId" = true } }
    "POST /transfers"                        = { servicio = "svc-transfers", recurso = "transfers", parametros = { "method.request.header.Idempotency-Key" = true } }
    "GET /transfers/{id}"                    = { servicio = "svc-transfers", recurso = "transfers/{id}", parametros = { "method.request.path.id" = true } }
    "GET /beneficiaries"                     = { servicio = "svc-transfers", recurso = "beneficiaries", parametros = {} }
    "POST /beneficiaries"                    = { servicio = "svc-transfers", recurso = "beneficiaries", parametros = {} }
    "DELETE /beneficiaries"                  = { servicio = "svc-transfers", recurso = "beneficiaries", parametros = {} }
    "GET /categories"                        = { servicio = "svc-budgets", recurso = "categories", parametros = {} }
    "GET /budgets"                           = { servicio = "svc-budgets", recurso = "budgets", parametros = {} }
    "POST /budgets"                          = { servicio = "svc-budgets", recurso = "budgets", parametros = {} }
    "PUT /budgets"                           = { servicio = "svc-budgets", recurso = "budgets", parametros = {} }
    "GET /admin/users"                       = { servicio = "svc-admin", recurso = "admin/users", parametros = {} }
    "POST /admin/users/{id}/block"           = { servicio = "svc-admin", recurso = "admin/users/{id}/block", parametros = { "method.request.path.id" = true } }
    "GET /admin/audit"                       = { servicio = "svc-admin", recurso = "admin/audit", parametros = {} }
  }
}

resource "aws_api_gateway_rest_api" "api" {
  lifecycle {
    create_before_destroy = true
  }

  name                         = "${local.prefijo}-api"
  description                  = "API de Q-Wallet"
  security_policy              = "SecurityPolicy_TLS13_1_3_2025_09"
  endpoint_access_mode         = "STRICT"
  disable_execute_api_endpoint = false

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_resource" "n1" {
  for_each    = local.recursos_n1
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = each.key
}

resource "aws_api_gateway_resource" "n2" {
  for_each    = local.recursos_n2
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.n1[each.value.padre].id
  path_part   = each.value.parte
}

resource "aws_api_gateway_resource" "n3" {
  for_each    = local.recursos_n3
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.n2[each.value.padre].id
  path_part   = each.value.parte
}

resource "aws_api_gateway_resource" "n4" {
  for_each    = local.recursos_n4
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.n3[each.value.padre].id
  path_part   = each.value.parte
}

locals {
  id_recurso = merge(
    { for k, r in aws_api_gateway_resource.n1 : k => r.id },
    { for k, r in aws_api_gateway_resource.n2 : k => r.id },
    { for k, r in aws_api_gateway_resource.n3 : k => r.id },
    { for k, r in aws_api_gateway_resource.n4 : k => r.id },
  )
}

resource "aws_api_gateway_authorizer" "cognito" {
  name                   = "${local.prefijo}-cognito"
  rest_api_id            = aws_api_gateway_rest_api.api.id
  type                   = "COGNITO_USER_POOLS"
  provider_arns          = [aws_cognito_user_pool.usuarios.arn]
  identity_source        = "method.request.header.Authorization"
  authorizer_result_ttl_in_seconds = 0
}

resource "aws_api_gateway_request_validator" "parametros" {
  name                        = "${local.prefijo}-parametros-y-cuerpo"
  rest_api_id                 = aws_api_gateway_rest_api.api.id
  validate_request_body       = true
  validate_request_parameters = true
}

resource "aws_api_gateway_method" "ruta" {
  for_each = local.rutas

  rest_api_id          = aws_api_gateway_rest_api.api.id
  resource_id          = local.id_recurso[each.value.recurso]
  http_method          = split(" ", each.key)[0]
  authorization        = "COGNITO_USER_POOLS"
  authorizer_id        = aws_api_gateway_authorizer.cognito.id
  authorization_scopes = ["${aws_cognito_resource_server.api.identifier}/api"]
  request_validator_id = aws_api_gateway_request_validator.parametros.id
  request_parameters   = each.value.parametros
}

resource "aws_api_gateway_integration" "ruta" {
  for_each = local.rutas

  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = local.id_recurso[each.value.recurso]
  http_method             = aws_api_gateway_method.ruta[each.key].http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.servicio[each.value.servicio].invoke_arn
}

# CTRL-13: errores del propio API Gateway (401, 403, 429, 5xx) con cuerpo
# genérico y cabeceras de seguridad; nunca detalles internos.
locals {
  cabeceras_seguridad = {
    "gatewayresponse.header.Strict-Transport-Security" = "'max-age=31536000; includeSubDomains'"
    "gatewayresponse.header.X-Content-Type-Options"    = "'nosniff'"
    "gatewayresponse.header.Cache-Control"             = "'no-store'"
    "gatewayresponse.header.X-Frame-Options"           = "'DENY'"
  }
}

resource "aws_api_gateway_gateway_response" "generica" {
  for_each = toset(["DEFAULT_4XX", "DEFAULT_5XX"])

  rest_api_id         = aws_api_gateway_rest_api.api.id
  response_type       = each.key
  response_parameters = local.cabeceras_seguridad
  response_templates = {
    "application/json" = "{\"error\":\"solicitud rechazada\",\"correlationId\":\"$context.requestId\"}"
  }
}

resource "aws_api_gateway_deployment" "api" {
  rest_api_id = aws_api_gateway_rest_api.api.id

  triggers = {
    redespliegue = sha1(jsonencode([
      local.rutas,
      [for m in aws_api_gateway_method.ruta : m.id],
      [for i in aws_api_gateway_integration.ruta : i.uri],
      [for g in aws_api_gateway_gateway_response.generica : g.response_templates],
      aws_api_gateway_authorizer.cognito.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [aws_api_gateway_integration.ruta, aws_api_gateway_gateway_response.generica]
}

resource "aws_cloudwatch_log_group" "apigateway" {
  name              = "/aws/apigateway/${local.prefijo}-api"
  retention_in_days = var.retencion_logs_dias
  kms_key_id        = aws_kms_key.datos.arn
}

resource "aws_api_gateway_stage" "v1" {
  #checkov:skip=CKV_AWS_120:Sin caché: las respuestas tienen datos de un solo cliente y la caché tiene costo por hora.
  #checkov:skip=CKV2_AWS_4:Log de ejecución apagado a propósito: puede copiar cuerpos con datos personales (CTRL-09). Se usa el log de acceso.
  #checkov:skip=CKV2_AWS_51:Certificado de cliente para un backend HTTP; aquí el backend es Lambda por integración AWS_PROXY firmada por IAM.
  #checkov:skip=CKV2_AWS_29:El WAF (CTRL-17) se asocia con waf_habilitado = true solo para pruebas, por costo.
  #checkov:skip=CKV2_AWS_77:El WAF incluye AWSManagedRulesKnownBadInputsRuleSet (Log4j) cuando está encendido; Checkov no lo ve por ser condicional.
  xray_tracing_enabled = true

  rest_api_id   = aws_api_gateway_rest_api.api.id
  deployment_id = aws_api_gateway_deployment.api.id
  stage_name    = local.etapa

  # Logs de acceso sin tokens ni cuerpos (CTRL-09): solo metadatos y el sub del usuario.
  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.apigateway.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      usuario        = "$context.authorizer.claims.sub"
      metodo         = "$context.httpMethod"
      ruta           = "$context.resourcePath"
      estado         = "$context.status"
      error          = "$context.error.responseType"
      latenciaMs     = "$context.responseLatency"
      tiempo         = "$context.requestTime"
      waf            = "$context.wafResponseCode"
    })
  }

  depends_on = [aws_api_gateway_account.cuenta]
}

resource "aws_api_gateway_method_settings" "todas" {
  #checkov:skip=CKV_AWS_225:Sin caché (ver la etapa v1).
  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = aws_api_gateway_stage.v1.stage_name
  method_path = "*/*"

  settings {
    throttling_burst_limit = 20
    throttling_rate_limit  = 10
    metrics_enabled        = false
    logging_level          = "OFF" # el log de ejecución puede copiar cuerpos con datos personales
    data_trace_enabled     = false
    caching_enabled        = false
  }
}
