# Enable necessary APIs
resource "google_project_service" "resource_manager_api" {
  project = var.project_id # or a hardcoded project ID
  service = "cloudresourcemanager.googleapis.com"
}
resource "google_project_service" "iam" {
  project = var.project_id
  service = "iam.googleapis.com"
}

resource "google_project_service" "cloud_resource_manager_api" {
  service            = "cloudresourcemanager.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloud_build_api" {
  service            = "cloudbuild.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "artifact_registry_api" {
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloud_run_api" {
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "firestore_api" {
  service            = "firestore.googleapis.com"
  disable_on_destroy = false
}

# Abilita l'API di Secret Manager
resource "google_project_service" "secretmanager_api" {
  service            = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

# Abilita l'API di Cloud Storage
resource "google_project_service" "storage_api" {
  service            = "storage-component.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "vertex_ai_api" {
  service            = "aiplatform.googleapis.com"
  disable_on_destroy = false
}

# Wait for APIs to be enabled
resource "time_sleep" "wait_for_apis" {
  depends_on = [
    google_project_service.cloud_resource_manager_api,
    google_project_service.artifact_registry_api,
    google_project_service.cloud_run_api,
    google_project_service.cloud_build_api,
    google_project_service.firestore_api,
    google_project_service.secretmanager_api,
    google_project_service.storage_api,
    google_project_service.vertex_ai_api,
  ]

  create_duration = "30s"
}