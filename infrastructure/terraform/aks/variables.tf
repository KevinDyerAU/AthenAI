variable "location" {
  description = "Azure location"
  type        = string
  default     = "eastus"
}

variable "name" {
  description = "AKS prefix/name"
  type        = string
  default     = "neov3-aks"
}

variable "kubernetes_version" {
  description = "AKS Kubernetes version"
  type        = string
  default     = "1.29.0"
}

variable "agents_count" {
  description = "Default agent count"
  type        = number
  default     = 2
}

variable "agents_size" {
  description = "Agent VM size"
  type        = string
  default     = "Standard_DS3_v2"
}
