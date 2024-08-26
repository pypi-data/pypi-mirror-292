terraform {
  required_providers {
    github = {
      source  = "integrations/github"
    }
  }
}

locals {
  module_name = coalesce(var.module_name, substr(basename(path.module), 9, length(basename(path.module)) - 9))
}
