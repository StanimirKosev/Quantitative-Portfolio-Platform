# GitHub Actions Setup

## Required Secrets

Add these secrets to your GitHub repository (Settings > Secrets and variables > Actions):

### `GCP_PROJECT_ID`
Your Google Cloud Project ID (e.g., `my-quantitative-project`)

### `GCP_SA_KEY`
Service account key JSON for deployment. Create one with these steps:

```bash
# Create service account
gcloud iam service-accounts create github-actions \
  --description="GitHub Actions deployment" \
  --display-name="GitHub Actions"

# Grant necessary permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Create and download key
gcloud iam service-accounts keys create key.json \
  --iam-account=github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Copy the entire content of key.json as the GCP_SA_KEY secret
```

### `FRED_API_KEY`
Federal Reserve Economic Data API key from https://fred.stlouisfed.org/docs/api/api_key.html

## Pre-deployment Setup

Before the first deployment, create the Artifact Registry repository (if not already exists):

```bash
gcloud artifacts repositories create mc \
  --repository-format=docker \
  --location=europe-west1
```

**Note**: If you get "ALREADY_EXISTS" error, the repository is already set up - you can proceed.

## Pipeline Features

- **Backend Testing**: Poetry dependency management, pytest for all modules
- **Frontend Testing**: npm ci, ESLint, production build verification  
- **Code Quality**: Black formatting check, Python syntax validation
- **Automated Deployment**: Docker builds with SHA tagging, Cloud Run deployment
- **Environment Configuration**: Automatic backend URL injection into frontend build
- **Resource Management**: Optimized CPU/memory allocation for each service