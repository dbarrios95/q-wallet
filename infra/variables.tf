variable "region" {
  description = "Región de AWS (CONTEXTO, sección 3)."
  type        = string
  default     = "us-east-1"
}

variable "proyecto" {
  description = "Prefijo de nombres y valor de la etiqueta Project. El rol de despliegue solo puede tocar recursos con este prefijo."
  type        = string
  default     = "qwallet"
}

variable "entorno" {
  description = "Valor de la etiqueta Env."
  type        = string
  default     = "dev"
}

variable "image_tag" {
  description = "Etiqueta de la imagen de contenedor de las Lambdas (hash del árbol de /services, lo calcula GitHub Actions)."
  type        = string
  default     = "sin-imagen"
}

variable "waf_habilitado" {
  description = "Crea y asocia el AWS WAF (CTRL-17). Cuesta unos US$8 al mes mientras existe: se enciende solo para pruebas y capturas."
  type        = bool
  default     = false
}

variable "callback_urls" {
  description = "URL de retorno del login administrado (esquema propio de la app Android)."
  type        = list(string)
  default     = ["qwallet://auth/callback"]
}

variable "logout_urls" {
  description = "URL de retorno al cerrar sesión."
  type        = list(string)
  default     = ["qwallet://auth/logout"]
}

variable "retencion_logs_dias" {
  description = "Días que se conservan los logs de CloudWatch."
  type        = number
  default     = 365
}

variable "correo_alertas" {
  description = "Correo que recibe las alarmas de seguridad (secreto ALERTAS_CORREO de GitHub; no va en el repo)."
  type        = string
  default     = ""
  sensitive   = true
}
