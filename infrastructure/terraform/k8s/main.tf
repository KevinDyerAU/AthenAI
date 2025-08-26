terraform {
  required_version = ">= 1.5.0"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.26.0"
    }
  }
}

provider "kubernetes" {
  config_path    = var.kubeconfig
  config_context = var.kubecontext
}

resource "kubernetes_namespace" "neov3" {
  metadata {
    name = var.namespace
    labels = {
      "app.kubernetes.io/name" = var.namespace
    }
  }
}

resource "kubernetes_config_map" "neov3_config" {
  metadata {
    name      = "neov3-config"
    namespace = kubernetes_namespace.neov3.metadata[0].name
    labels = {
      "app.kubernetes.io/name" = var.namespace
    }
  }
  data = {
    FLASK_ENV                    = var.flask_env
    PORT                         = "8080"
    LOG_LEVEL                    = var.log_level
    COMPLIANCE_PERSIST_DISABLED  = tostring(var.compliance_persist_disabled)
    INCIDENT_PERSIST_DISABLED    = tostring(var.incident_persist_disabled)
    FORCE_TLS                    = tostring(var.force_tls)
    ENCRYPTION_AT_REST           = tostring(var.encryption_at_rest)
    KEY_ROTATION_DAYS            = tostring(var.key_rotation_days)
    RBAC_POLICY_PATH             = "/app/policies/policies.yaml"
  }
}
