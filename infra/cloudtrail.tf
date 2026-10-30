# CTRL-20: CloudTrail multirregión con validación de integridad, cifrado con la
# CMK y guardado en un bucket S3 privado (Block Public Access, versionado,
# solo TLS). Es la fuente de auditoría del SIEM (bloque 5).

resource "aws_s3_bucket" "cloudtrail" {
  #checkov:skip=CKV_AWS_18:Registro de acceso al bucket: se cubre con los eventos de CloudTrail; otro bucket de logs sumaría costo sin evidencia nueva.
  #checkov:skip=CKV_AWS_144:Replicación a otra región fuera del presupuesto (RSK-01, una sola región aceptada).
  #checkov:skip=CKV2_AWS_62:Las notificaciones de eventos se evalúan con el SIEM (bloque 5).
  bucket = "${local.prefijo}-cloudtrail-${local.cuenta}"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_public_access_block" "cloudtrail" {
  bucket                  = aws_s3_bucket.cloudtrail.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "cloudtrail" {
  bucket = aws_s3_bucket.cloudtrail.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_versioning" "cloudtrail" {
  bucket = aws_s3_bucket.cloudtrail.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "cloudtrail" {
  bucket = aws_s3_bucket.cloudtrail.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.datos.arn
    }
    bucket_key_enabled = true
  }
}

# Pasados 90 días los registros bajan a una clase de almacenamiento más barata.
# No se borran: son evidencia de auditoría.
resource "aws_s3_bucket_lifecycle_configuration" "cloudtrail" {
  bucket = aws_s3_bucket.cloudtrail.id
  rule {
    id     = "archivar-registros"
    status = "Enabled"
    filter {}
    transition {
      days          = 90
      storage_class = "STANDARD_IA"
    }
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

locals {
  arn_trail = "arn:${local.particion}:cloudtrail:${local.region}:${local.cuenta}:trail/${local.prefijo}-auditoria"
}

data "aws_iam_policy_document" "cloudtrail_bucket" {
  statement {
    sid       = "CloudTrailRevisaAcl"
    actions   = ["s3:GetBucketAcl"]
    resources = [aws_s3_bucket.cloudtrail.arn]
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

  statement {
    sid       = "CloudTrailEscribe"
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.cloudtrail.arn}/AWSLogs/${local.cuenta}/*"]
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

  statement {
    sid     = "SoloTLS"
    effect  = "Deny"
    actions = ["s3:*"]
    resources = [
      aws_s3_bucket.cloudtrail.arn,
      "${aws_s3_bucket.cloudtrail.arn}/*",
    ]
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}

resource "aws_s3_bucket_policy" "cloudtrail" {
  bucket     = aws_s3_bucket.cloudtrail.id
  policy     = data.aws_iam_policy_document.cloudtrail_bucket.json
  depends_on = [aws_s3_bucket_public_access_block.cloudtrail]
}

resource "aws_cloudtrail" "auditoria" {
  #checkov:skip=CKV2_AWS_10:La integración con CloudWatch Logs y el SIEM se decide en el bloque 5 (CTRL-20).
  #checkov:skip=CKV_AWS_252:Las alertas se harán con el SIEM del bloque 5, no con un tema SNS por archivo entregado.
  name                          = "${local.prefijo}-auditoria"
  s3_bucket_name                = aws_s3_bucket.cloudtrail.id
  is_multi_region_trail         = true
  include_global_service_events = true
  enable_log_file_validation    = true
  kms_key_id                    = aws_kms_key.datos.arn

  depends_on = [aws_s3_bucket_policy.cloudtrail]
}
