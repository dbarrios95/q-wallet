output "api_url" {
  description = "URL de la etapa v1 de la API (endpoint execute-api, solo TLS 1.3)."
  value       = aws_api_gateway_stage.v1.invoke_url
}

output "api_host" {
  description = "Host del endpoint, para la prueba de TLS."
  value       = "${aws_api_gateway_rest_api.api.id}.execute-api.${local.region}.amazonaws.com"
}

output "cognito_dominio" {
  description = "Dominio del login administrado de Cognito."
  value       = "https://${aws_cognito_user_pool_domain.login.domain}.auth.${local.region}.amazoncognito.com"
}

output "cognito_client_id" {
  description = "ID del cliente público de la app (no es secreto)."
  value       = aws_cognito_user_pool_client.app_android.id
}

output "tablas" {
  description = "Nombres de las tablas de DynamoDB."
  value       = { for k, t in aws_dynamodb_table.tabla : k => t.name }
}

output "roles_lambda" {
  description = "Nombres de los roles de ejecución (para el simulador de políticas)."
  value       = { for k, r in aws_iam_role.lambda : k => r.name }
}

output "repositorios_ecr" {
  description = "Repositorios de imágenes por servicio."
  value       = { for k, r in aws_ecr_repository.servicio : k => r.name }
}

output "waf_habilitado" {
  value = var.waf_habilitado
}
