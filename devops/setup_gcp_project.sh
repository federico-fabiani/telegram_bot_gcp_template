#!/usr/bin/env bash
# filepath: setup_gcp_project.sh

# Exit on error
set -e

# Check for gcloud installation
if ! command -v gcloud &> /dev/null; then
    echo "gcloud CLI not found. Please install Google Cloud SDK first."
    exit 1
fi

# Check for GitHub CLI if on Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    if ! command -v gh &> /dev/null; then
        echo "GitHub CLI not found. Please install GitHub CLI first."
        exit 1
    fi
fi

# Configuration variables - replace these
PROJECT_ID="my-telegram-bot-project"  # Must be globally unique
PROJECT_NAME="Telegram Bot Project"
BILLING_ACCOUNT="XXXXXX-XXXXXX-XXXXXX"  # Your billing account ID
SA_NAME="devops-service-account"
SA_DISPLAY_NAME="DevOps Service Account"
KEY_FILE="devops-sa-key.json"

# Login to gcloud if not already logged in
gcloud auth login --quiet

# Create new project
echo "Creating new GCP project: ${PROJECT_NAME} (${PROJECT_ID})..."
gcloud projects create ${PROJECT_ID} --name="${PROJECT_NAME}"

# Link project to billing account
echo "Linking project to billing account..."
gcloud billing projects link ${PROJECT_ID} --billing-account=${BILLING_ACCOUNT}

# Set as active project
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable iam.googleapis.com cloudresourcemanager.googleapis.com

# Create service account
echo "Creating service account: ${SA_NAME}..."
gcloud iam service-accounts create ${SA_NAME} \
    --display-name="${SA_DISPLAY_NAME}" \
    --project=${PROJECT_ID}

# Get the full service account email
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant owner role to service account
echo "Granting owner role to service account..."
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/owner"

# Create and download the key
echo "Creating and downloading service account key..."
gcloud iam service-accounts keys create ${KEY_FILE} \
    --iam-account=${SA_EMAIL}

# Encode the key in base64
echo "Encoding key in base64..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    # Windows - use PowerShell for more reliable base64 encoding
    BASE64_KEY=$(powershell -Command "[convert]::ToBase64String([IO.File]::ReadAllBytes(\"$PWD\\$KEY_FILE\"))" > ${KEY_FILE}.b64)
    echo "Base64 encoded key saved to: ${KEY_FILE}.b64"
else
    # Linux/MacOS
    BASE64_KEY=$(base64 -w 0 ${KEY_FILE} > ${KEY_FILE}.b64)
    echo "Base64 encoded key saved to: ${KEY_FILE}.b64"
fi

echo "Setup complete!"
echo "Project ID: ${PROJECT_ID}"
echo "Service Account: ${SA_EMAIL}"
echo "Service account key saved to: ${KEY_FILE}"

# Setting GitHub secrets with proper Windows handling
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    # Windows - read file content correctly
    echo "Setting GitHub secrets and variables..."
    gh secret set GCP_SA_KEY --body "$(cat "${KEY_FILE}")"
    gh variable set GCP_PROJECT_ID --body "${PROJECT_ID}"
    gh variable set GCP_REGION --body "europe-west1"
else
    # Linux/MacOS
    gh secret set GCP_SA_KEY --body "$(cat ${KEY_FILE})"
    gh variable set GCP_PROJECT_ID --body "${PROJECT_ID}"
    gh variable set GCP_REGION --body "europe-west1"
fi