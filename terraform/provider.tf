terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.33.0"  # Use the correct version constraint
    }
  }
}


provider "kubernetes" {
  config_path    = "./kubeconfig"            # Adjust path if needed
  config_context = "kind-hive-box-cluster"  # Use the correct context name
}