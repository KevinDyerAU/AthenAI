variable "project" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "name" {
  description = "GKE cluster name"
  type        = string
  default     = "neov3-gke"
}

variable "subnet_cidr" {
  description = "Subnet CIDR"
  type        = string
  default     = "10.50.0.0/24"
}

variable "machine_type" {
  description = "Node machine type"
  type        = string
  default     = "e2-standard-4"
}
