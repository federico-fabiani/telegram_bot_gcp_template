# resource "google_storage_bucket" "function_bucket" {
#   name     = "${var.project_id}-function-bucket"
#   location = var.region

#   depends_on = [time_sleep.wait_for_apis]
# }

# resource "google_storage_bucket_object" "function_zip" {
#   name   = "empty_function.zip"
#   bucket = google_storage_bucket.function_bucket.name
#   source = "./tmp/hello_world.zip"

#   depends_on = [google_storage_bucket.function_bucket]
# }

resource "google_storage_bucket" "manuals" {
  name     = "${var.project_id}-manuals"
  location = var.region

  depends_on = [time_sleep.wait_for_apis]
}