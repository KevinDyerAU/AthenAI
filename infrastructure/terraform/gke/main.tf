terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
}

module "vpc" {
  source  = "terraform-google-modules/network/google"
  version = "~> 9.0"

  project_id   = var.project
  network_name = "${var.name}-vpc"
  subnets = [
    {
      subnet_name   = "${var.name}-subnet"
      subnet_ip     = var.subnet_cidr
      subnet_region = var.region
    }
  ]
}

module "gke" {
  source  = "terraform-google-modules/kubernetes-engine/google"
  version = "~> 34.0"

  project_id        = var.project
  name              = var.name
  region            = var.region
  network           = module.vpc.network_name
  subnetwork        = module.vpc.subnets_names[0]
  ip_range_pods     = null
  ip_range_services = null

  release_channel = "REGULAR"

  node_pools = [
    {
      name         = "default-pool"
      machine_type = var.machine_type
      min_count    = 1
      max_count    = 5
      local_ssd_count = 0
      disk_size_gb = 50
      disk_type    = "pd-standard"
      image_type   = "COS_CONTAINERD"
      auto_repair  = true
      auto_upgrade = true
    }
  ]
}

output "cluster_name" {
  value = module.gke.name
}

output "kubeconfig" {
  description = "How to get kubeconfig"
  value       = "gcloud container clusters get-credentials ${module.gke.name} --region ${var.region} --project ${var.project}"
}
