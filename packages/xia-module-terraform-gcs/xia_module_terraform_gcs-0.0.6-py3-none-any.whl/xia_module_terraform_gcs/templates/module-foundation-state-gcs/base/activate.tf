module "activate_module_state_gcs" {
  source = "../../modules/activate-module-foundation-state-gcs"

  landscape = local.landscape
  modules   = local.modules
}

