module "activate_gh_module_application" {
  source = "../../modules/activate-gh-module-application"

  config_file = "../../../config/core/github.yaml"
  landscape = local.landscape
  foundations = local.foundations

}
