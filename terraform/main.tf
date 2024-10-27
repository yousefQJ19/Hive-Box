resource "kubernetes_manifest" "app_manifests" {
  for_each = fileset("./manifests", "*.yaml") 

  manifest = yamldecode(file(each.value))
}