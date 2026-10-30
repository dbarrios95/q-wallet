terraform {
  required_version = "= 1.16.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 6.67.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "= 3.9.1"
    }
  }

  # Estado remoto (ACT-09, CTRL-12): bucket S3 creado por infra/bootstrap/bootstrap.sh,
  # con Block Public Access, versionado y SSE-KMS. Bloqueo nativo de S3 (sin DynamoDB).
  # El nombre del bucket lleva el número de cuenta, por eso se pasa en `terraform init`
  # con -backend-config="bucket=..." desde GitHub Actions (el repo es público).
  backend "s3" {
    key          = "qwallet/infra.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project = var.proyecto
      Env     = var.entorno
    }
  }
}

data "aws_caller_identity" "actual" {}
data "aws_partition" "actual" {}
data "aws_region" "actual" {}
