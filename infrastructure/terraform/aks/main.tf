terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.100.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "${var.name}-rg"
  location = var.location
}

module "aks" {
  source  = "Azure/aks/azurerm"
  version = "~> 8.0"

  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  prefix              = var.name

  kubernetes_version = var.kubernetes_version
  agents_count       = var.agents_count
  agents_size        = var.agents_size
}

output "cluster_name" {
  value = module.aks.aks_name
}

output "kubeconfig" {
  description = "How to get kubeconfig"
  value       = "az aks get-credentials --resource-group ${azurerm_resource_group.rg.name} --name ${module.aks.aks_name}"
}
