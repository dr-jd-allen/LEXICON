#!/bin/bash

# Pre-build check script for LEXICON
# This ensures all GCP resources and secrets are properly configured

set -e

PROJECT_ID=${GCP_PROJECT_ID:-"spinwheel-464709"}
REGION=${GCP_REGION:-"us-central1"}

echo "🔍 LEXICON Pre-Build Check"
echo "=========================="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Check if user is authenticated
echo "1. Checking authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &>/dev/null; then
    echo "❌ Not authenticated. Please run: gcloud auth login"
    exit 1
fi
echo "✅ Authenticated"

# Check project
echo ""
echo "2. Checking project configuration..."
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
    echo "⚠️  Current project is $CURRENT_PROJECT, switching to $PROJECT_ID..."
    gcloud config set project $PROJECT_ID
fi
echo "✅ Project set to $PROJECT_ID"

# Check APIs
echo ""
echo "3. Checking required APIs..."
REQUIRED_APIS=(
    "run.googleapis.com"
    "cloudbuild.googleapis.com"
    "secretmanager.googleapis.com"
    "sqladmin.googleapis.com"
    "redis.googleapis.com"
    "storage-api.googleapis.com"
    "aiplatform.googleapis.com"
    "firestore.googleapis.com"
)

for api in "${REQUIRED_APIS[@]}"; do
    if gcloud services list --enabled --filter="name:$api" --format="value(name)" | grep -q "$api"; then
        echo "  ✅ $api"
    else
        echo "  ⚠️  Enabling $api..."
        gcloud services enable $api --project=$PROJECT_ID
    fi
done

# Check secrets
echo ""
echo "4. Checking required secrets..."
REQUIRED_SECRETS=(
    "openai-api-key"
    "anthropic-api-key"
    "tavily-api-key"
    "lexis-nexis-api-key"
    "database-password"
    "redis-password"
)

MISSING_SECRETS=()
for secret in "${REQUIRED_SECRETS[@]}"; do
    if gcloud secrets describe $secret --project=$PROJECT_ID &>/dev/null; then
        echo "  ✅ $secret"
    else
        echo "  ❌ $secret (missing)"
        MISSING_SECRETS+=("$secret")
    fi
done

if [ ${#MISSING_SECRETS[@]} -ne 0 ]; then
    echo ""
    echo "❌ Missing secrets detected!"
    echo ""
    echo "Run the following to set up secrets:"
    echo "  ./gcp_config/setup_secrets.sh"
    echo ""
    echo "Or manually create each secret:"
    for secret in "${MISSING_SECRETS[@]}"; do
        echo "  echo -n 'your-value' | gcloud secrets versions add $secret --data-file=- --project=$PROJECT_ID"
    done
    exit 1
fi

# Check service account
echo ""
echo "5. Checking service account..."
SA_EMAIL="lexicon-sa@$PROJECT_ID.iam.gserviceaccount.com"
if gcloud iam service-accounts describe $SA_EMAIL --project=$PROJECT_ID &>/dev/null; then
    echo "✅ Service account exists: $SA_EMAIL"
else
    echo "❌ Service account missing. Run: ./gcp_config/setup_gcp_resources.sh"
    exit 1
fi

# Check Cloud SQL instance
echo ""
echo "6. Checking Cloud SQL instance..."
if gcloud sql instances describe lexicon-db --project=$PROJECT_ID &>/dev/null; then
    echo "✅ Cloud SQL instance 'lexicon-db' exists"
else
    echo "⚠️  Cloud SQL instance missing. Run: ./gcp_config/setup_gcp_resources.sh"
fi

# Check Storage bucket
echo ""
echo "7. Checking Storage bucket..."
BUCKET_NAME="lexicon-documents"
if gsutil ls -b gs://$BUCKET_NAME &>/dev/null; then
    echo "✅ Storage bucket 'gs://$BUCKET_NAME' exists"
else
    echo "⚠️  Storage bucket missing. Creating..."
    gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BUCKET_NAME/
fi

echo ""
echo "================================"
echo "✅ Pre-build check complete!"
echo ""
echo "You can now run:"
echo "  gcloud builds submit --config=cloudbuild.yaml"
echo ""