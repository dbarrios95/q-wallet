# CTRL-19: llave KMS propia (CMK) para DynamoDB, logs de CloudWatch, CloudTrail
# y variables de entorno de las Lambdas. Llave simétrica AES-256 (SYMMETRIC_DEFAULT),
# con rotación automática anual.

locals {
  cuenta    = data.aws_caller_identity.actual.account_id
  particion = data.aws_partition.actual.partition
  region    = data.aws_region.actual.region
  prefijo   = var.proyecto
}

data "aws_iam_policy_document" "kms_datos" {
  #checkov:skip=CKV_AWS_109:En una política de llave, Resource "*" significa "esta llave"; la administración se delega a IAM de la propia cuenta.
  #checkov:skip=CKV_AWS_111:Igual que CKV_AWS_109: el permiso se limita a esta llave y a la propia cuenta.
  #checkov:skip=CKV_AWS_356:Igual que CKV_AWS_109; los servicios llevan condiciones de contexto y de origen.
  # 1. La cuenta delega en IAM: sin esto la llave queda sin administrador.
  #    Los permisos reales de cada rol están en sus políticas IAM (iam.tf).
  statement {
    sid       = "AdministracionPorIAM"
    actions   = ["kms:*"]
    resources = ["*"]
    principals {
      type        = "AWS"
      identifiers = ["arn:${local.particion}:iam::${local.cuenta}:root"]
    }
  }

  # 2. CloudWatch Logs cifra solo los grupos de log de esta cuenta y región.
  statement {
    sid = "CloudWatchLogs"
    actions = [
      "kms:Encrypt*",
      "kms:Decrypt*",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:Describe*",
    ]
    resources = ["*"]
    principals {
      type        = "Service"
      identifiers = ["logs.${local.region}.amazonaws.com"]
    }
    condition {
      test     = "ArnLike"
      variable = "kms:EncryptionContext:aws:logs:arn"
      values   = ["arn:${local.particion}:logs:${local.region}:${local.cuenta}:log-group:*"]
    }
  }

  # 3. CloudTrail cifra los registros del trail de este proyecto.
  statement {
    sid       = "CloudTrailCifra"
    actions   = ["kms:GenerateDataKey*"]
    resources = ["*"]
    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:SourceArn"
      values   = ["arn:${local.particion}:cloudtrail:${local.region}:${local.cuenta}:trail/${local.prefijo}-auditoria"]
    }
    condition {
      test     = "StringLike"
      variable = "kms:EncryptionContext:aws:cloudtrail:arn"
      values   = ["arn:${local.particion}:cloudtrail:*:${local.cuenta}:trail/*"]
    }
  }

  # 4. Las alarmas de CloudWatch publican en el tema SNS cifrado (bloque 5).
  statement {
    sid       = "AlarmasPublicanEnSns"
    actions   = ["kms:Decrypt", "kms:GenerateDataKey*"]
    resources = ["*"]
    principals {
      type        = "Service"
      identifiers = ["cloudwatch.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [local.cuenta]
    }
  }

  statement {
    sid       = "CloudTrailDescribe"
    actions   = ["kms:DescribeKey"]
    resources = ["*"]
    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }
  }
}

resource "aws_kms_key" "datos" {
  description              = "Q-Wallet: cifrado de datos en reposo (DynamoDB, logs, CloudTrail, Lambda)"
  key_usage                = "ENCRYPT_DECRYPT"
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  enable_key_rotation      = true
  rotation_period_in_days  = 365
  deletion_window_in_days  = 30
  policy                   = data.aws_iam_policy_document.kms_datos.json
}

resource "aws_kms_alias" "datos" {
  name          = "alias/${local.prefijo}-datos"
  target_key_id = aws_kms_key.datos.key_id
}
