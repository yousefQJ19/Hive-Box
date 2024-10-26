terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"  # Adjust based on the provider version on your device
    }
  }
}

provider "kubernetes" {
  config_path = "${path.module}/./kubeconfig.yaml" 
}

resource "kubernetes_manifest" "deployment" {
  manifest = file("${path.module}/manifests/deployment.yaml")
}

resource "kubernetes_manifest" "service" {
  manifest = file("${path.module}/manifests/service.yaml")
}

resource "kubernetes_manifest" "ingress" {
  manifest = file("${path.module}/manifests/ingress.yaml")
}

resource "kubernetes_manifest" "configmap" {
  manifest = file("${path.module}/manifests/configmap.yaml")
}
