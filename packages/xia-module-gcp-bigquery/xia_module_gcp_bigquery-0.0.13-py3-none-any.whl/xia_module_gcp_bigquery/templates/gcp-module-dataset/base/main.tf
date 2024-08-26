provider "google" {
  alias = "google-dataset"
}

module "gcp_module_dataset" {
  providers = {
    google = google.google-dataset
  }

  source = "../../modules/gcp-module-dataset"

  content = "../../content/datasets.yaml"

}
