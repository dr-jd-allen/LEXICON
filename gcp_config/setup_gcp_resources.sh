#!/bin/bash

# Script to set up GCP resources for LEXICON deployment

set -e

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"spinwheel-464709"}
REGION=${GCP_REGION:-"us-central1"}
SERVICE_ACCOUNT_NAME="lexicon-sa"
CLOUD_SQL_INSTANCE="lexicon-db"
REDIS_INSTANCE="lexicon-redis"
STORAGE_BUCKET="lexicon-documents"

echo "Setting up GCP resources for LEXICON in project: $PROJECT_ID"

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable \
    run.googleapis.com \
    sql-component.googleapis.com \
    sqladmin.googleapis.com \
    redis.googleapis.com \
    storage-api.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    --project=$PROJECT_ID

# Create service account
echo "Creating service account..."
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
    --display-name="LEXICON Service Account" \
    --project=$PROJECT_ID || echo "Service account already exists"

# Grant necessary permissions
echo "Granting IAM permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/redis.editor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Create Cloud SQL instance
echo "Creating Cloud SQL PostgreSQL instance..."
gcloud sql instances create $CLOUD_SQL_INSTANCE \
    --database-version=POSTGRES_15 \
    --tier=db-n1-standard-2 \
    --region=$REGION \
    --network=default \
    --no-assign-ip \
    --backup \
    --backup-start-time=03:00 \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=03 \
    --project=$PROJECT_ID || echo "Cloud SQL instance already exists"

# Create database
echo "Creating database..."
gcloud sql databases create dify \
    --instance=$CLOUD_SQL_INSTANCE \
    --project=$PROJECT_ID || echo "Database already exists"

# Set root password
echo "Setting database password..."
gcloud sql users set-password postgres \
    --instance=$CLOUD_SQL_INSTANCE \
    --password="$(openssl rand -base64 32)" \
    --project=$PROJECT_ID

# Create Memorystore Redis instance
echo "Creating Memorystore Redis instance..."
gcloud redis instances create $REDIS_INSTANCE \
    --size=1 \
    --region=$REGION \
    --redis-version=redis_6_x \
    --tier=standard \
    --project=$PROJECT_ID || echo "Redis instance already exists"

# Create Cloud Storage bucket
echo "Creating Cloud Storage bucket..."
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$STORAGE_BUCKET/ || echo "Bucket already exists"

# Set bucket permissions
gsutil iam ch serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com:objectAdmin gs://$STORAGE_BUCKET

# Create secrets in Secret Manager
echo "Creating secrets..."
gcloud secrets create dify-secret-key \
    --data-file=- \
    --project=$PROJECT_ID <<< "$(openssl rand -base64 32)" || echo "Secret already exists"

gcloud secrets create database-password \
    --data-file=- \
    --project=$PROJECT_ID <<< "$(openssl rand -base64 32)" || echo "Secret already exists"

gcloud secrets create redis-password \
    --data-file=- \
    --project=$PROJECT_ID <<< "$(openssl rand -base64 32)" || echo "Secret already exists"

# Output connection details
echo ""
echo "=== GCP Resources Created ==="
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service Account: $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"
echo "Cloud SQL Instance: $CLOUD_SQL_INSTANCE"
echo "Redis Instance: $REDIS_INSTANCE"
echo "Storage Bucket: gs://$STORAGE_BUCKET"
echo ""
echo "Next steps:"
echo "1. Update .env.gcp with the connection details"
echo "2. Run: gcloud auth configure-docker"
echo "3. Build and deploy: gcloud builds submit --config=cloudbuild.yaml"