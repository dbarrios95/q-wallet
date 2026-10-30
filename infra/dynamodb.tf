# Datos de negocio: una tabla por tipo de dato, para que cada Lambda reciba
# permiso solo sobre las tablas que usa (menor privilegio, CTRL-12).
# Todas: cifradas con la CMK propia (AES-256, CTRL-19), PITR activo,
# protección contra borrado y cobro por solicitud (sin capacidad reservada).

locals {
  tablas = {
    perfiles = {
      hash_key  = "userId"
      range_key = null
      gsi       = { nombre = "por-telefono", hash_key = "telefonoHash" }
      ttl       = null
      atributos = { userId = "S", telefonoHash = "S" }
    }
    pin = {
      hash_key  = "userId"
      range_key = null
      gsi       = null
      ttl       = null
      atributos = { userId = "S" }
    }
    cuentas = {
      hash_key  = "userId"
      range_key = "accountId"
      gsi       = null
      ttl       = null
      atributos = { userId = "S", accountId = "S" }
    }
    movimientos = {
      hash_key  = "accountId"
      range_key = "fechaId"
      gsi       = null
      ttl       = null
      atributos = { accountId = "S", fechaId = "S" }
    }
    transferencias = {
      hash_key  = "pk"
      range_key = null
      gsi       = null
      ttl       = "expiraEn" # registros de Idempotency-Key (CTRL-06)
      atributos = { pk = "S" }
    }
    beneficiarios = {
      hash_key  = "userId"
      range_key = "beneficiarioId"
      gsi       = null
      ttl       = null
      atributos = { userId = "S", beneficiarioId = "S" }
    }
    presupuestos = {
      hash_key  = "userId"
      range_key = "mesCategoria"
      gsi       = null
      ttl       = null
      atributos = { userId = "S", mesCategoria = "S" }
    }
    auditoria = {
      hash_key  = "dia"
      range_key = "tsId"
      gsi       = null
      ttl       = null
      atributos = { dia = "S", tsId = "S" }
    }
  }
}

resource "aws_dynamodb_table" "tabla" {
  for_each = local.tablas

  name                        = "${local.prefijo}-${each.key}"
  billing_mode                = "PAY_PER_REQUEST"
  hash_key                    = each.value.hash_key
  range_key                   = each.value.range_key
  deletion_protection_enabled = true

  dynamic "attribute" {
    for_each = each.value.atributos
    content {
      name = attribute.key
      type = attribute.value
    }
  }

  dynamic "global_secondary_index" {
    for_each = each.value.gsi == null ? [] : [each.value.gsi]
    content {
      name            = global_secondary_index.value.nombre
      hash_key        = global_secondary_index.value.hash_key
      projection_type = "KEYS_ONLY"
    }
  }

  dynamic "ttl" {
    for_each = each.value.ttl == null ? [] : [each.value.ttl]
    content {
      attribute_name = ttl.value
      enabled        = true
    }
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.datos.arn
  }

  point_in_time_recovery {
    enabled = true
  }

  lifecycle {
    prevent_destroy = true
  }
}
