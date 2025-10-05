#!/bin/bash

# Embiggen Your Eyes - Google Cloud Deployment Script
# This script deploys both backend and frontend to Google Cloud Run

set -e  # Exit on error

echo "=================================="
echo "Embiggen Your Eyes - GCP Deployment"
echo "=================================="
echo ""

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-embiggen-your-eyes}"
REGION="${GCP_REGION:-us-central1}"
BACKEND_SERVICE="embiggen-backend"
FRONTEND_SERVICE="embiggen-frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed.${NC}"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not authenticated with gcloud.${NC}"
    echo "Running: gcloud auth login"
    gcloud auth login
fi

# Prompt for project ID if not set
if [ -z "$GCP_PROJECT_ID" ]; then
    echo -e "${YELLOW}Enter your GCP Project ID:${NC}"
    read -r PROJECT_ID
fi

# Set the project
echo "📦 Setting GCP project to: $PROJECT_ID"
gcloud config set project "$PROJECT_ID"

# Enable required APIs
echo ""
echo "🔧 Enabling required Google Cloud APIs..."
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    storage-api.googleapis.com

# Create Cloud Storage bucket for tiles (if it doesn't exist)
BUCKET_NAME="${PROJECT_ID}-tiles"
if ! gsutil ls -b "gs://${BUCKET_NAME}" &> /dev/null; then
    echo ""
    echo "📦 Creating Cloud Storage bucket for tiles..."
    gsutil mb -l "$REGION" "gs://${BUCKET_NAME}"
    gsutil uniformbucketlevelaccess set on "gs://${BUCKET_NAME}"
fi

# Deploy Backend
echo ""
echo "🚀 Deploying Backend to Cloud Run..."
cd backend
gcloud run deploy "$BACKEND_SERVICE" \
    --source . \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --memory 8Gi \
    --cpu 4 \
    --timeout 600 \
    --max-instances 10 \
    --set-env-vars "TILES_BUCKET=gs://${BUCKET_NAME}" \
    --quiet

# Get backend URL
BACKEND_URL=$(gcloud run services describe "$BACKEND_SERVICE" --region "$REGION" --format="value(status.url)")
echo -e "${GREEN}✅ Backend deployed at: $BACKEND_URL${NC}"

cd ..

# Update frontend configuration with backend URL
echo ""
echo "🔧 Updating frontend configuration..."
sed -i.bak "s|http://localhost:8000|$BACKEND_URL|g" frontend/app.js
rm -f frontend/app.js.bak

# Deploy Frontend
echo ""
echo "🚀 Deploying Frontend to Cloud Run..."
cd frontend
gcloud run deploy "$FRONTEND_SERVICE" \
    --source . \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --quiet

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe "$FRONTEND_SERVICE" --region "$REGION" --format="value(status.url)")
echo -e "${GREEN}✅ Frontend deployed at: $FRONTEND_URL${NC}"

cd ..

# Restore frontend configuration
git checkout frontend/app.js 2>/dev/null || true

# Summary
echo ""
echo "=================================="
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "=================================="
echo ""
echo "🌐 Frontend URL: $FRONTEND_URL"
echo "🔧 Backend API:  $BACKEND_URL"
echo "📚 API Docs:     $BACKEND_URL/docs"
echo "📦 Tiles Bucket: gs://${BUCKET_NAME}"
echo ""
echo "To view logs:"
echo "  Backend:  gcloud run logs tail $BACKEND_SERVICE --region $REGION"
echo "  Frontend: gcloud run logs tail $FRONTEND_SERVICE --region $REGION"
echo ""
echo "To delete services:"
echo "  gcloud run services delete $BACKEND_SERVICE --region $REGION"
echo "  gcloud run services delete $FRONTEND_SERVICE --region $REGION"
echo ""
