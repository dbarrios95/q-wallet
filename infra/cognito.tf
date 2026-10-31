# CTRL-18: identidad con Amazon Cognito. OAuth2 Authorization Code + PKCE
# (cliente público, sin secreto), MFA TOTP obligatorio y tokens de corta vida.

resource "aws_cognito_user_pool" "usuarios" {
  name                = "${local.prefijo}-usuarios"
  user_pool_tier      = "ESSENTIALS"
  deletion_protection = "ACTIVE"

  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  mfa_configuration = "ON"
  software_token_mfa_configuration {
    enabled = true
  }

  password_policy {
    minimum_length                   = 14 # bloque 5: Prowler pide 14 o más
    require_lowercase                = true
    require_uppercase                = true
    require_numbers                  = true
    require_symbols                  = true
    temporary_password_validity_days = 1
    password_history_size            = 5
  }

  sign_in_policy {
    allowed_first_auth_factors = ["PASSWORD"]
  }

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  admin_create_user_config {
    allow_admin_create_user_only = false
  }

  user_attribute_update_settings {
    attributes_require_verification_before_update = ["email"]
  }

  lifecycle {
    prevent_destroy = true
  }
}

# Grupo de soporte / administración (CTRL-14). Se valida también en el handler.
resource "aws_cognito_user_group" "admins" {
  name         = "admins"
  user_pool_id = aws_cognito_user_pool.usuarios.id
  description  = "Soporte de Q-Wallet: endpoints /admin/*"
}

# Alcance propio de la API: el authorizer de API Gateway exige este scope
# en el access token, así un token de otro cliente no sirve.
resource "aws_cognito_resource_server" "api" {
  identifier   = local.prefijo
  name         = "${local.prefijo}-api"
  user_pool_id = aws_cognito_user_pool.usuarios.id

  scope {
    scope_name        = "api"
    scope_description = "Acceso a la API de Q-Wallet"
  }
}

resource "aws_cognito_user_pool_client" "app_android" {
  name         = "${local.prefijo}-app-android"
  user_pool_id = aws_cognito_user_pool.usuarios.id

  generate_secret                      = false # cliente público: PKCE en lugar de secreto
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["openid", "email", "${aws_cognito_resource_server.api.identifier}/api"]
  supported_identity_providers         = ["COGNITO"]
  callback_urls                        = var.callback_urls
  default_redirect_uri                 = var.callback_urls[0]
  logout_urls                          = var.logout_urls
  explicit_auth_flows                  = ["ALLOW_USER_SRP_AUTH"]
  prevent_user_existence_errors        = "ENABLED"
  enable_token_revocation              = true

  access_token_validity  = 15
  id_token_validity      = 15
  refresh_token_validity = 12
  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "hours"
  }

  refresh_token_rotation {
    feature                    = "ENABLED"
    retry_grace_period_seconds = 10
  }
}

# Login administrado (versión 2), con el dominio por defecto de Cognito.
resource "random_id" "dominio" {
  byte_length = 4
}

resource "aws_cognito_user_pool_domain" "login" {
  domain                = "${local.prefijo}-${random_id.dominio.hex}"
  user_pool_id          = aws_cognito_user_pool.usuarios.id
  managed_login_version = 2
}

resource "aws_cognito_managed_login_branding" "app_android" {
  client_id                   = aws_cognito_user_pool_client.app_android.id
  user_pool_id                = aws_cognito_user_pool.usuarios.id
  use_cognito_provided_values = true
}
