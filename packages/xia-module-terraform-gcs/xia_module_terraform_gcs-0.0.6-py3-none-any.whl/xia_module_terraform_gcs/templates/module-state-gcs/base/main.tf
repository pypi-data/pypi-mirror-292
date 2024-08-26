module "module_state_gcs" {
  source = "../../modules/module-state-gcs"

  config_file = "../../../config/core/tfstate.yaml"
  landscape = local.landscape
  applications = local.applications
  modules = local.modules
  environment_dict = local.environment_dict
  app_env_config = local.app_env_config
  module_app_to_activate = local.module_app_to_activate

  gcp_projects = module.gcp_module_project.gcp_projects
  github_provider_sa_dict = module.gcp_module_project.github_provider_sa
  depends_on = [module.gcp_module_project]
}