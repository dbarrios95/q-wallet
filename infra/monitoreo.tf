# Bloque 5 (sección 5.3 y 5.4): SIEM con servicios nativos de AWS.
# Decisión de Daniel (31-oct-2026): CloudWatch como SIEM. Wazuh pide 4 GB+ de RAM
# y no cabe en el presupuesto de US$5; queda en el roadmap (sección 6.3).
#
#   Fuentes: CloudTrail (auditoría de la cuenta) + logs de acceso de API Gateway +
#            logs JSON de las 5 Lambdas + logs del WAF (cuando está encendido).
#   Reglas:  filtros de métrica (una regla = un patrón de ataque) y consultas
#            guardadas de Logs Insights que cruzan fuentes por correlationId y por usuario.
#   Alertas: alarmas de CloudWatch -> tema SNS cifrado con la CMK -> correo.
#   Tablero: qwallet-seguridad.
#
# Costo: los filtros de métrica no tienen default_value, así que solo publican
# datos cuando hay una coincidencia (no se cobra la métrica en horas sin eventos).
# Se usan 10 alarmas o menos (capa gratuita de CloudWatch).

locals {
  ns_seguridad = "QWallet/Seguridad"

  # Reglas sobre los logs JSON de las Lambdas (services/comun/src/registro.ts).
  reglas_lambda = {
    pin_bloqueado = {
      patron      = "{ $.codigo = \"pin_bloqueado\" }"
      descripcion = "PIN de transacción bloqueado tras 5 intentos (fuerza bruta, CTRL-02)"
    }
    pin_incorrecto = {
      patron      = "{ $.codigo = \"pin_incorrecto\" }"
      descripcion = "PIN de transacción incorrecto (intento de autorizar una transferencia)"
    }
    acceso_prohibido = {
      patron      = "{ $.codigo = \"prohibido\" }"
      descripcion = "Acceso prohibido a una función o un objeto (BFLA/BOLA, CTRL-01 y CTRL-14)"
    }
    entrada_invalida = {
      patron      = "{ $.codigo = \"solicitud_invalida\" || $.codigo = \"cuerpo_muy_grande\" }"
      descripcion = "Entrada rechazada por la validación estricta (inyección, mass assignment, CTRL-04)"
    }
    error_no_controlado = {
      patron      = "{ $.evento = \"error_no_controlado\" }"
      descripcion = "Error no controlado en una Lambda (posible abuso o falla)"
    }
  }

  # Reglas sobre el log de acceso de API Gateway (formato en apigateway.tf).
  reglas_api = {
    api_no_autenticado = {
      patron      = "{ $.estado = \"401\" }"
      descripcion = "Solicitud sin token o con token inválido (CTRL-18)"
    }
    api_limite = {
      patron      = "{ $.estado = \"429\" }"
      descripcion = "Throttling de API Gateway (CTRL-05)"
    }
    api_bloqueo_waf = {
      patron      = "{ $.waf = \"403\" }"
      descripcion = "Solicitud bloqueada por el WAF (CTRL-17)"
    }
  }

  # Reglas sobre CloudTrail (basadas en CIS AWS Foundations, sección de monitoreo).
  # Se excluye el rol de pentest: Prowler hace cientos de lecturas autorizadas que
  # AWS niega por diseño (rol de solo lectura) y saturarían la alerta.
  reglas_trail = {
    trail_no_autorizado = {
      patron      = "{ ($.errorCode = \"*UnauthorizedOperation\" || $.errorCode = \"AccessDenied*\") && $.userIdentity.sessionContext.sessionIssuer.userName != \"qwallet-gha-pentest\" }"
      descripcion = "Llamadas a la API de AWS negadas por IAM (CIS 4.1)"
    }
    trail_uso_root = {
      patron      = "{ $.userIdentity.type = \"Root\" && $.userIdentity.invokedBy NOT EXISTS && $.eventType != \"AwsServiceEvent\" }"
      descripcion = "Uso del usuario raíz (CIS 4.3)"
    }
    trail_consola_sin_mfa = {
      patron      = "{ $.eventName = \"ConsoleLogin\" && $.additionalEventData.MFAUsed != \"Yes\" && $.responseElements.ConsoleLogin = \"Success\" }"
      descripcion = "Inicio de sesión en la consola sin MFA (CIS 4.2)"
    }
    trail_auditoria_y_llaves = {
      patron      = "{ $.eventName = \"StopLogging\" || $.eventName = \"DeleteTrail\" || $.eventName = \"UpdateTrail\" || $.eventName = \"PutEventSelectors\" || $.eventName = \"DisableKey\" || $.eventName = \"ScheduleKeyDeletion\" || $.eventName = \"PutKeyPolicy\" || $.eventName = \"DeleteUserPool\" || $.eventName = \"DeleteTable\" || $.eventName = \"DeleteAlarms\" || $.eventName = \"DisableAlarmActions\" || $.eventName = \"DeleteMetricFilter\" || $.eventName = \"DeleteLogGroup\" || $.eventName = \"DeleteTopic\" || $.eventName = \"Unsubscribe\" }"
      descripcion = "Cambios a la auditoría o al propio SIEM, a la llave KMS o borrado de datos (CIS 4.5 y 4.7, AME-31)"
    }
    trail_cambios_iam = {
      patron      = "{ $.eventSource = \"iam.amazonaws.com\" && ($.eventName = \"PutRolePolicy\" || $.eventName = \"PutUserPolicy\" || $.eventName = \"AttachRolePolicy\" || $.eventName = \"AttachUserPolicy\" || $.eventName = \"DetachRolePolicy\" || $.eventName = \"DetachUserPolicy\" || $.eventName = \"DeleteRolePolicy\" || $.eventName = \"CreatePolicyVersion\" || $.eventName = \"CreateRole\" || $.eventName = \"DeleteRole\" || $.eventName = \"UpdateAssumeRolePolicy\") }"
      descripcion = "Cambios de permisos IAM (CIS 4.4). Solo tablero: cada despliegue los produce"
    }
    trail_admin_cognito = {
      patron      = "{ $.eventSource = \"cognito-idp.amazonaws.com\" && ($.eventName = \"AdminDisableUser\" || $.eventName = \"AdminEnableUser\" || $.eventName = \"AdminUserGlobalSignOut\" || $.eventName = \"SetUserPoolMfaConfig\" || $.eventName = \"UpdateUserPool\") }"
      descripcion = "Acciones administrativas sobre usuarios o la configuración de Cognito (AME-03, AME-06)"
    }
  }
}

# ---------- Fuente 1: CloudTrail -> CloudWatch Logs ----------

resource "aws_cloudwatch_log_group" "cloudtrail" {
  name              = "/aws/cloudtrail/${local.prefijo}-auditoria"
  retention_in_days = var.retencion_logs_dias
  kms_key_id        = aws_kms_key.datos.arn
}

data "aws_iam_policy_document" "cloudtrail_confianza" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:SourceArn"
      values   = [local.arn_trail]
    }
  }
}

# Rol que usa CloudTrail para escribir en su grupo de logs. Solo puede crear
# flujos y escribir eventos en ese grupo; además queda bajo el límite de permisos.
resource "aws_iam_role" "cloudtrail_logs" {
  name                 = "${local.prefijo}-cloudtrail-logs"
  assume_role_policy   = data.aws_iam_policy_document.cloudtrail_confianza.json
  permissions_boundary = local.limite_permisos_arn
}

data "aws_iam_policy_document" "cloudtrail_logs" {
  statement {
    sid       = "EscribirEnSuGrupo"
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["${aws_cloudwatch_log_group.cloudtrail.arn}:log-stream:*"]
  }
}

resource "aws_iam_role_policy" "cloudtrail_logs" {
  name   = "escribir-logs"
  role   = aws_iam_role.cloudtrail_logs.id
  policy = data.aws_iam_policy_document.cloudtrail_logs.json
}

# ---------- Reglas de correlación (filtros de métrica) ----------

resource "aws_cloudwatch_log_metric_filter" "lambda" {
  # Una regla por servicio y patrón; todas publican en la misma métrica por regla.
  for_each = {
    for par in setproduct(keys(local.reglas_lambda), local.servicios) :
    "${par[0]}/${par[1]}" => { regla = par[0], servicio = par[1] }
  }

  name           = "${local.prefijo}-${replace(each.key, "/", "-")}"
  log_group_name = aws_cloudwatch_log_group.lambda[each.value.servicio].name
  pattern        = local.reglas_lambda[each.value.regla].patron

  metric_transformation {
    name      = each.value.regla
    namespace = local.ns_seguridad
    value     = "1"
    unit      = "Count"
  }
}

resource "aws_cloudwatch_log_metric_filter" "api" {
  for_each = local.reglas_api

  name           = "${local.prefijo}-${each.key}"
  log_group_name = aws_cloudwatch_log_group.apigateway.name
  pattern        = each.value.patron

  metric_transformation {
    name      = each.key
    namespace = local.ns_seguridad
    value     = "1"
    unit      = "Count"
  }
}

resource "aws_cloudwatch_log_metric_filter" "trail" {
  for_each = local.reglas_trail

  name           = "${local.prefijo}-${each.key}"
  log_group_name = aws_cloudwatch_log_group.cloudtrail.name
  pattern        = each.value.patron

  metric_transformation {
    name      = each.key
    namespace = local.ns_seguridad
    value     = "1"
    unit      = "Count"
  }
}

# ---------- Consultas de correlación entre fuentes (Logs Insights) ----------

resource "aws_cloudwatch_query_definition" "por_correlation_id" {
  name = "${local.prefijo}/correlacion/por-correlationId"
  log_group_names = concat(
    [for s in local.servicios : aws_cloudwatch_log_group.lambda[s].name],
    [aws_cloudwatch_log_group.apigateway.name],
  )
  # Reemplace el valor por el correlationId que devuelve la respuesta de error.
  query_string = <<-EOT
    fields @timestamp, @logStream, coalesce(correlationId, requestId) as id, evento, codigo, ruta, estado, servicio, usuario
    | filter correlationId = "REEMPLAZAR" or requestId = "REEMPLAZAR"
    | sort @timestamp asc
  EOT
}

resource "aws_cloudwatch_query_definition" "rechazos_por_usuario" {
  name            = "${local.prefijo}/correlacion/rechazos-por-usuario"
  log_group_names = [aws_cloudwatch_log_group.apigateway.name]
  # Usuarios autenticados con muchas respuestas 4xx en poco tiempo: enumeración de
  # objetos ajenos (BOLA), fuerza bruta del PIN o pruebas de validación.
  query_string = <<-EOT
    filter estado like /^4\d\d$/ and ispresent(usuario) and usuario != "-"
    | stats count(*) as rechazos, count_distinct(ruta) as rutas, min(@timestamp) as desde, max(@timestamp) as hasta by usuario, ip
    | filter rechazos >= 5
    | sort rechazos desc
  EOT
}

resource "aws_cloudwatch_query_definition" "ips_sospechosas" {
  name            = "${local.prefijo}/correlacion/ips-sospechosas"
  log_group_names = [aws_cloudwatch_log_group.apigateway.name]
  query_string    = <<-EOT
    filter estado = "401" or estado = "429" or waf = "403"
    | stats count(*) as eventos by ip, estado, waf
    | filter eventos >= 10
    | sort eventos desc
  EOT
}

resource "aws_cloudwatch_query_definition" "denegaciones_aws" {
  name            = "${local.prefijo}/correlacion/denegaciones-aws"
  log_group_names = [aws_cloudwatch_log_group.cloudtrail.name]
  query_string    = <<-EOT
    filter errorCode like /AccessDenied|Unauthorized/
    | stats count(*) as negadas by userIdentity.sessionContext.sessionIssuer.userName as rol, eventSource, eventName
    | sort negadas desc
    | limit 50
  EOT
}

resource "aws_cloudwatch_query_definition" "waf_bloqueos" {
  name            = "${local.prefijo}/correlacion/waf-bloqueos"
  log_group_names = [aws_cloudwatch_log_group.waf.name]
  query_string    = <<-EOT
    filter action = "BLOCK"
    | stats count(*) as bloqueos by terminatingRuleId, httpRequest.clientIp
    | sort bloqueos desc
  EOT
}

# ---------- Alertas: SNS cifrado + correo ----------

resource "aws_sns_topic" "alertas" {
  name              = "${local.prefijo}-alertas"
  kms_master_key_id = aws_kms_key.datos.id
}

data "aws_iam_policy_document" "sns_alertas" {
  statement {
    sid     = "SoloAlarmasDeEstaCuenta"
    actions = ["sns:Publish"]
    principals {
      type        = "Service"
      identifiers = ["cloudwatch.amazonaws.com"]
    }
    resources = [aws_sns_topic.alertas.arn]
    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = ["arn:${local.particion}:cloudwatch:${local.region}:${local.cuenta}:alarm:${local.prefijo}-*"]
    }
  }

  statement {
    sid     = "SoloTLS"
    effect  = "Deny"
    actions = ["sns:Publish"]
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    resources = [aws_sns_topic.alertas.arn]
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}

resource "aws_sns_topic_policy" "alertas" {
  arn    = aws_sns_topic.alertas.arn
  policy = data.aws_iam_policy_document.sns_alertas.json
}

# El correo no va en el repo (es público): llega por el secreto ALERTAS_CORREO.
# La suscripción queda "pendiente" hasta que Daniel da clic en el correo de AWS.
resource "aws_sns_topic_subscription" "correo" {
  count     = var.correo_alertas == "" ? 0 : 1
  topic_arn = aws_sns_topic.alertas.arn
  protocol  = "email"
  endpoint  = var.correo_alertas
}

locals {
  # nombre => [métrica, umbral, periodo en segundos, descripción, severidad]
  alarmas = {
    pin-bloqueado         = ["pin_bloqueado", 1, 300, "Un PIN de transacción se bloqueó (5 intentos fallidos). Posible fuerza bruta del PIN (CA-04).", "Alta"]
    acceso-prohibido      = ["acceso_prohibido", 5, 300, "5 o más accesos prohibidos en 5 minutos. Posible enumeración de objetos ajenos o escalada (CA-01, CA-09).", "Alta"]
    error-no-controlado   = ["error_no_controlado", 1, 300, "Una Lambda tuvo un error no controlado.", "Media"]
    rafaga-401            = ["api_no_autenticado", 50, 300, "50 o más solicitudes sin token válido en 5 minutos. Posible reutilización o fuerza bruta de tokens.", "Media"]
    throttling            = ["api_limite", 20, 300, "20 o más respuestas 429 en 5 minutos. Ráfaga contra la API (CA-06).", "Media"]
    aws-no-autorizado     = ["trail_no_autorizado", 5, 300, "5 o más llamadas a AWS negadas por IAM en 5 minutos (CIS 4.1).", "Alta"]
    uso-root              = ["trail_uso_root", 1, 300, "Se usó el usuario raíz de la cuenta (CIS 4.3).", "Crítica"]
    consola-sin-mfa       = ["trail_consola_sin_mfa", 1, 300, "Inicio de sesión en la consola sin MFA (CIS 4.2).", "Crítica"]
    auditoria-y-llaves    = ["trail_auditoria_y_llaves", 1, 300, "Cambio a CloudTrail o al SIEM (alarmas, filtros, logs, avisos), a la llave KMS o borrado de datos (CIS 4.5, 4.7).", "Crítica"]
  }
}

resource "aws_cloudwatch_metric_alarm" "seguridad" {
  for_each = local.alarmas

  alarm_name          = "${local.prefijo}-${each.key}"
  alarm_description   = "[${each.value[4]}] ${each.value[3]}"
  namespace           = local.ns_seguridad
  metric_name         = each.value[0]
  statistic           = "Sum"
  period              = each.value[2]
  evaluation_periods  = 1
  threshold           = each.value[1]
  comparison_operator = "GreaterThanOrEqualToThreshold"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [aws_sns_topic.alertas.arn]
  ok_actions          = [aws_sns_topic.alertas.arn]
}

# Bloqueos del WAF: solo existe mientras el WAF está encendido.
resource "aws_cloudwatch_metric_alarm" "waf_bloqueos" {
  for_each = local.waf

  alarm_name          = "${local.prefijo}-waf-bloqueos"
  alarm_description   = "[Media] 10 o más solicitudes bloqueadas por el WAF en 5 minutos (CTRL-17)."
  namespace           = "AWS/WAFV2"
  metric_name         = "BlockedRequests"
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 10
  comparison_operator = "GreaterThanOrEqualToThreshold"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [aws_sns_topic.alertas.arn]
  dimensions = {
    WebACL = aws_wafv2_web_acl.api[each.key].name
    Region = local.region
    Rule   = "ALL"
  }
}

# ---------- Tablero ----------

resource "aws_cloudwatch_dashboard" "seguridad" {
  dashboard_name = "${local.prefijo}-seguridad"
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "alarm", x = 0, y = 0, width = 24, height = 4
        properties = {
          title  = "Estado de las alarmas de seguridad"
          alarms = [for a in aws_cloudwatch_metric_alarm.seguridad : a.arn]
        }
      },
      {
        type = "metric", x = 0, y = 4, width = 12, height = 6
        properties = {
          title  = "Aplicación: rechazos por regla (Lambdas)"
          region = local.region
          stat   = "Sum"
          period = 300
          view   = "timeSeries"
          metrics = [for r in keys(local.reglas_lambda) : [local.ns_seguridad, r]]
        }
      },
      {
        type = "metric", x = 12, y = 4, width = 12, height = 6
        properties = {
          title  = "Perímetro: 401, 429 y bloqueos del WAF (API Gateway)"
          region = local.region
          stat   = "Sum"
          period = 300
          view   = "timeSeries"
          metrics = [for r in keys(local.reglas_api) : [local.ns_seguridad, r]]
        }
      },
      {
        type = "metric", x = 0, y = 10, width = 12, height = 6
        properties = {
          title  = "Cuenta AWS: eventos de CloudTrail por regla"
          region = local.region
          stat   = "Sum"
          period = 300
          view   = "timeSeries"
          metrics = [for r in keys(local.reglas_trail) : [local.ns_seguridad, r]]
        }
      },
      {
        type = "metric", x = 12, y = 10, width = 12, height = 6
        properties = {
          title  = "API Gateway: tráfico y errores (etapa v1)"
          region = local.region
          stat   = "Sum"
          period = 300
          view   = "timeSeries"
          metrics = [
            ["AWS/ApiGateway", "Count", "ApiName", aws_api_gateway_rest_api.api.name, "Stage", local.etapa],
            [".", "4XXError", ".", ".", ".", "."],
            [".", "5XXError", ".", ".", ".", "."],
          ]
        }
      },
      {
        type = "log", x = 0, y = 16, width = 24, height = 6
        properties = {
          title  = "Usuarios con 5 o más rechazos (correlación por usuario e IP)"
          region = local.region
          view   = "table"
          query  = "SOURCE '${aws_cloudwatch_log_group.apigateway.name}' | filter estado like /^4\\d\\d$/ and ispresent(usuario) and usuario != \"-\" | stats count(*) as rechazos, count_distinct(ruta) as rutas by usuario, ip | filter rechazos >= 5 | sort rechazos desc"
        }
      },
    ]
  })
}
