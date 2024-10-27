terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.18" 
    }
  }
}


provider "kubernetes" {
  config_path    = "./kubeconfig"            
  config_context = "kind-hive-box-cluster"  
}
