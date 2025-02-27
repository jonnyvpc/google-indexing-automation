# 🛠️ Setup Guide

This guide walks you through setting up the Google Indexing API automation for your Webflow site.

## Prerequisites

1. **Google Cloud Account**
   - Active billing account
   - Owner or Editor role on the project

2. **Webflow Account**
   - Business plan or higher (for webhook access)
   - Collection with blog posts

3. **Development Environment**
   - Python 3.9+
   - Google Cloud CLI
   - Docker (optional)

## Step-by-Step Setup

### 1. Google Cloud Project Setup

```bash
# Create new project
gcloud projects create [PROJECT_ID]

# Set project as active
gcloud config set project [PROJECT_ID]

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  containerregistry.googleapis.com
```

### 2. Workload Identity Federation Setup

```bash
# Create identity pool
gcloud iam workload-identity-pools create [POOL_NAME] \
  --location="global" \
  --display-name="[DISPLAY_NAME]"

# Create provider
gcloud iam workload-identity-pools providers create-oidc [PROVIDER_NAME] \
  --location="global" \
  --workload-identity-pool=[POOL_NAME] \
  --issuer-uri="https://accounts.google.com" \
  --allowed-audiences="https://accounts.google.com"
```

### 3. Service Account Setup

```bash
# Create service account
gcloud iam service-accounts create [SA_NAME] \
  --display-name="[DISPLAY_NAME]"

# Grant necessary roles
gcloud projects add-iam-policy-binding [PROJECT_ID] \
  --member="serviceAccount:[SA_NAME]@[PROJECT_ID].iam.gserviceaccount.com" \
  --role="roles/iam.workloadIdentityUser"

gcloud projects add-iam-policy-binding [PROJECT_ID] \
  --member="serviceAccount:[SA_NAME]@[PROJECT_ID].iam.gserviceaccount.com" \
  --role="roles/searchindexing.indexer"
```

### 4. Local Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/google-indexing-automation.git
cd google-indexing-automation

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Unix
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 5. Deploy to Cloud Run

```bash
# Deploy service
gcloud run deploy webhook-listener \
  --source . \
  --platform managed \
  --region [REGION] \
  --service-account [SA_NAME]@[PROJECT_ID].iam.gserviceaccount.com \
  --allow-unauthenticated
```

### 6. Webflow Configuration

1. Go to Webflow Project Settings
2. Navigate to Integrations > Webhooks
3. Add new webhook:
   - Trigger: Collection Item Published
   - URL: `https://[YOUR-CLOUD-RUN-URL]/webhook`
   - Method: POST
   - Content Type: application/json

## Verification

Test your setup:

```bash
# Test webhook
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"slug": "test-post"}' \
  https://[YOUR-CLOUD-RUN-URL]/webhook

# Check logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=webhook-listener" --limit=5
```

## Troubleshooting

### Common Issues

1. **403 Permission Denied**
   - Check IAM roles
   - Verify Workload Identity Federation setup
   - Ensure APIs are enabled

2. **Webhook Not Triggering**
   - Verify Webflow webhook configuration
   - Check Cloud Run logs for request receipt
   - Confirm URL format matches expected pattern

3. **Deployment Failures**
   - Check billing is enabled
   - Verify service account permissions
   - Review Cloud Build logs

## Next Steps

1. Set up monitoring alerts
2. Configure error reporting
3. Implement rate limiting
4. Add custom metrics

## Support

For additional help:
- Create an issue on GitHub
- Check Cloud Run documentation
- Contact support team
