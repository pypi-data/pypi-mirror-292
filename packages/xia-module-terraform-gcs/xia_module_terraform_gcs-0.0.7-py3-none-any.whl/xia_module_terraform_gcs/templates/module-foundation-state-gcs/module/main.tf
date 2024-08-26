terraform {
  required_providers {
    github = {
      source  = "integrations/github"
    }
    google = {
      source  = "hashicorp/google"
    }
  }
}

locals {
  module_name = coalesce(var.module_name, basename(path.module))
  tfstate_config = yamldecode(file(var.config_file))
  tf_bucket_name = local.tfstate_config["tf_bucket"]
}

resource "google_storage_bucket_iam_member" "tfstate_bucket_list" {
  for_each = var.foundations
  bucket = local.tf_bucket_name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${var.foundation_admin_sa[each.key].email}"
}

resource "google_storage_bucket_iam_member" "tfstate_bucket_modify" {
  for_each = var.foundations
  bucket = local.tf_bucket_name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.foundation_admin_sa[each.key].email}"

  condition {
    title       = "PrefixCondition"
    description = "Grants access to objects of foundation directory"
    expression  = "resource.name.startsWith('projects/_/buckets/${local.tf_bucket_name}/objects/${each.value.parent}/_/${each.value.name}/_/')"
  }
}