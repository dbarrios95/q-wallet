# Un repositorio de imágenes por microservicio (CTRL-11). Etiquetas inmutables
# y escaneo al subir. Sin datos de clientes: cifrado AES-256 administrado por ECR.

locals {
  servicios = ["svc-profile", "svc-accounts", "svc-transfers", "svc-budgets", "svc-admin"]
}

resource "aws_ecr_repository" "servicio" {
  for_each = toset(local.servicios)

  #checkov:skip=CKV_AWS_136:Las imágenes no guardan datos de clientes ni secretos (CTRL-16); cifrado AES-256 administrado por ECR.
  name                 = "${local.prefijo}/${each.key}"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }
}

# Solo el servicio Lambda de esta cuenta puede descargar las imágenes.
data "aws_iam_policy_document" "ecr_lambda" {
  statement {
    sid     = "LambdaDescargaImagen"
    actions = ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    condition {
      test     = "StringLike"
      variable = "aws:sourceArn"
      values   = ["arn:${local.particion}:lambda:${local.region}:${local.cuenta}:function:${local.prefijo}-*"]
    }
  }
}

resource "aws_ecr_repository_policy" "servicio" {
  for_each   = aws_ecr_repository.servicio
  repository = each.value.name
  policy     = data.aws_iam_policy_document.ecr_lambda.json
}
