resource "google_artifact_registry_repository" "my_bot_name_repository" {
  location      = var.region
  repository_id = "${var.project_id}-repository"
  description   = "Docker repository for chat service with cleanup policies"
  format        = "DOCKER"

  cleanup_policies {
    id     = "delete-old-images"
    action = "DELETE"
    condition {
      tag_state  = "ANY"
      older_than = "172800s" # 48 ore
    }
  }

  cleanup_policies {
    id     = "keep-minimum-history-of-images"
    action = "KEEP"
    most_recent_versions {
      keep_count = 5
    }
  }

  depends_on = [time_sleep.wait_for_apis]
}