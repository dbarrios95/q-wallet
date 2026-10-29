# CTRL-17: AWS WAF delante de la etapa v1 de API Gateway.
# Se crea solo con waf_habilitado = true (cuesta unos US$8 al mes mientras existe):
# se enciende para pruebas y capturas y se apaga después (bloque 5).

locals {
  waf = var.waf_habilitado ? toset(["activo"]) : toset([])
}

resource "aws_wafv2_web_acl" "api" {
  for_each = local.waf

  name        = "${local.prefijo}-api"
  description = "WAF de la API de Q-Wallet"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  rule {
    name     = "reglas-comunes"
    priority = 10
    override_action {
      none {}
    }
    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesCommonRuleSet"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.prefijo}-reglas-comunes"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "entradas-maliciosas-conocidas"
    priority = 20
    override_action {
      none {}
    }
    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.prefijo}-entradas-maliciosas"
      sampled_requests_enabled   = true
    }
  }

  # Límite por IP: 100 solicitudes en 5 minutos. Las pruebas de 429 usan ráfagas
  # cortas contra este umbral bajo (política de pentest de AWS, sin inundación).
  rule {
    name     = "limite-por-ip"
    priority = 30
    action {
      block {}
    }
    statement {
      rate_based_statement {
        limit                 = 100
        evaluation_window_sec = 300
        aggregate_key_type    = "IP"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.prefijo}-limite-por-ip"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${local.prefijo}-waf"
    sampled_requests_enabled   = true
  }
}

resource "aws_wafv2_web_acl_association" "api" {
  for_each     = local.waf
  resource_arn = aws_api_gateway_stage.v1.arn
  web_acl_arn  = aws_wafv2_web_acl.api[each.key].arn
}

# El nombre debe empezar con aws-waf-logs-. Queda creado aunque el WAF esté
# apagado, para no perder la evidencia. La cabecera Authorization se redacta.
resource "aws_cloudwatch_log_group" "waf" {
  name              = "aws-waf-logs-${local.prefijo}"
  retention_in_days = var.retencion_logs_dias
  kms_key_id        = aws_kms_key.datos.arn
}

resource "aws_wafv2_web_acl_logging_configuration" "api" {
  for_each                = local.waf
  resource_arn            = aws_wafv2_web_acl.api[each.key].arn
  log_destination_configs = [aws_cloudwatch_log_group.waf.arn]

  redacted_fields {
    single_header {
      name = "authorization"
    }
  }
}
