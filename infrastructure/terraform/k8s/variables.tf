variable "kubeconfig" {
  description = "Path to kubeconfig file"
  type        = string
  default     = "~/.kube/config"
}

variable "kubecontext" {
  description = "Kube context to use"
  type        = string
  default     = null
}

variable "namespace" {
  description = "Target namespace"
  type        = string
  default     = "neov3"
}

variable "flask_env" {
  description = "FLASK_ENV value"
  type        = string
  default     = "production"
}

variable "log_level" {
  description = "LOG_LEVEL value"
  type        = string
  default     = "INFO"
}

variable "compliance_persist_disabled" {
  description = "Disable compliance persistence"
  type        = bool
  default     = true
}

variable "incident_persist_disabled" {
  description = "Disable incident persistence"
  type        = bool
  default     = true
}

variable "force_tls" {
  description = "Enforce TLS"
  type        = bool
  default     = true
}

variable "encryption_at_rest" {
  description = "Encryption at rest enabled"
  type        = bool
  default     = true
}

variable "key_rotation_days" {
  description = "Key rotation period"
  type        = number
  default     = 90
}
