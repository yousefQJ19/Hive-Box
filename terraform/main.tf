resource "kubernetes_manifest" "app_manifests" {
  for_each = fileset("./manifests", "*.yaml")  # Adjust the path if your manifests are in a different folder

  manifest = yamldecode(file(each.value))
}