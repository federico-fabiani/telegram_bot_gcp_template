resource "google_cloud_run_v2_service" "my_bot_name" {
  name     = "${var.project_id}-backend"
  location = var.region
  project  = var.project_id
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    scaling {
      max_instance_count = 1
    }

    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello"
      resources {
        limits = {
          cpu    = "2"
          memory = "1024Mi"
        }
        cpu_idle = true
      }

    }
    timeout                          = "10s"
    max_instance_request_concurrency = 200
    service_account                  = google_service_account.my_bot_name_sa.email
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
    ]
  }
  depends_on = [time_sleep.wait_for_apis, google_service_account.my_bot_name_sa]
}

resource "google_service_account" "my_bot_name_sa" {
  account_id   = "my_bot_name-sa"
  display_name = "Chat Service Account"
  depends_on   = [time_sleep.wait_for_apis]
}


resource "google_storage_bucket_iam_member" "my_bot_name_sa_manuals_reader" {
  bucket = google_storage_bucket.manuals.name
  role   = "roles/storage.admin"
  member = "serviceAccount:${google_service_account.my_bot_name_sa.email}"
}

# # Rendi pubblicamente accessibile il servizio Cloud Run
# resource "google_cloud_run_service_iam_member" "my_bot_name_public_invoker" {
#   service  = google_cloud_run_v2_service.my_bot_name.name
#   location = var.region
#   role     = "roles/run.invoker"
#   member   = "allUsers"
# }
