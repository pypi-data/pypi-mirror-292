module "activate_module_state_gcs" {
  source = "../../modules/activate-module-state-gcs"

  landscape = local.landscape
  modules   = local.modules
}

