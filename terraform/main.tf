resource "kubernetes_manifest" "app_manifests" {
  for_each = fileset("./", "*.yaml") 

  manifest = yamldecode(file(each.value))
}