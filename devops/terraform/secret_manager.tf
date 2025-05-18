# resource "google_secret_manager_secret" "openai_api_key" {
#   secret_id = "openai_api_key"

#   replication {
#     auto {}
#   }

#   depends_on = [google_project_service.secretmanager_api]
# }

# resource "google_secret_manager_secret_version" "openai_api_key_value" {
#   secret      = google_secret_manager_secret.openai_api_key.id
#   secret_data = var.openai_api_key
# }

# resource "google_secret_manager_secret" "langchain_api_key" {
#   secret_id = "langchain_api_key"

#   replication {
#     auto {}
#   }

#   depends_on = [google_project_service.secretmanager_api]
# }

# resource "google_secret_manager_secret_version" "langchain_api_key_value" {
#   secret      = google_secret_manager_secret.langchain_api_key.id
#   secret_data = var.langchain_api_key
# }