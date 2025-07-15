#!/bin/bash

# Script to set up Secret Manager entries for LEXICON API keys

set -e

PROJECT_ID=${GCP_PROJECT_ID:-"spinwheel-464709"}

echo "Setting up Secret Manager for LEXICON API keys..."
echo "Project: $PROJECT_ID"
echo ""

# Enable Secret Manager API
echo "Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com --project=$PROJECT_ID

# Function to create or update a secret
create_secret() {
    SECRET_NAME=$1
    SECRET_DESC=$2
    
    echo ""
    echo "Setting up secret: $SECRET_NAME"
    echo "Description: $SECRET_DESC"
    
    # Check if secret exists
    if gcloud secrets describe $SECRET_NAME --project=$PROJECT_ID &>/dev/null; then
        echo "Secret $SECRET_NAME already exists."
        read -p "Do you want to add a new version? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "Enter the value for $SECRET_NAME: " SECRET_VALUE
            echo -n "$SECRET_VALUE" | gcloud secrets versions add $SECRET_NAME --data-file=- --project=$PROJECT_ID
            echo "✓ New version added for $SECRET_NAME"
        fi
    else
        # Create new secret
        gcloud secrets create $SECRET_NAME \
            --replication-policy="automatic" \
            --data-file=- \
            --project=$PROJECT_ID <<< "placeholder-value"
        
        echo "✓ Secret $SECRET_NAME created"
        echo "⚠️  Please update with actual value using:"
        echo "   echo -n 'your-actual-key' | gcloud secrets versions add $SECRET_NAME --data-file=- --project=$PROJECT_ID"
    fi
}

# Create secrets for all API keys
create_secret "openai-api-key" "OpenAI API key for GPT-4 and O1 models"
create_secret "anthropic-api-key" "Anthropic API key for Claude models"
create_secret "tavily-api-key" "Tavily API key for deep research"
create_secret "lexis-nexis-api-key" "LEXIS-NEXIS API key for legal research"
create_secret "dify-api-key" "Dify API key (if still using Dify endpoints)"
create_secret "google-vertex-api-key" "Google Vertex AI API key (optional)"

# Database passwords
create_secret "database-password" "Cloud SQL PostgreSQL password"
create_secret "redis-password" "Memorystore Redis password"

# Other credentials
create_secret "jwt-secret-key" "JWT secret key for authentication"
create_secret "encryption-key" "Encryption key for sensitive data"

# Grant access to service account
echo ""
echo "Granting Secret Manager access to service account..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:lexicon-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --condition=None

echo ""
echo "=== Secret Manager Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Update each secret with actual values:"
echo "   echo -n 'your-api-key' | gcloud secrets versions add SECRET_NAME --data-file=- --project=$PROJECT_ID"
echo ""
echo "2. Secrets can be accessed in your application using:"
echo "   - Environment variables in Cloud Run"
echo "   - Direct API calls using the Secret Manager client library"
echo ""
echo "3. View all secrets:"
echo "   gcloud secrets list --project=$PROJECT_ID"