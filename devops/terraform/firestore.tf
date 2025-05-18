# resource "google_firestore_database" "conversations" {
#   name        = "conversations"
#   location_id = var.region
#   type        = "FIRESTORE_NATIVE"

#   depends_on = [time_sleep.wait_for_apis]
# }