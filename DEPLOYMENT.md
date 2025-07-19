# Cloud Run Deployment Guide

This guide explains how to deploy the Document Automation MCP Server to Google Cloud Run.

## Prerequisites

1. Google Cloud Project with billing enabled
2. Google Cloud SDK installed locally
3. Docker installed (optional, for local testing)

## Setup Steps

### 1. Authenticate with Google Cloud

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 2. Enable Required APIs

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 3. Build and Deploy

#### Option A: Using Cloud Build (Recommended)

```bash
# Submit build to Cloud Build
gcloud builds submit --config cloudbuild.yaml .
```

#### Option B: Manual Deployment

```bash
# Build the Docker image
docker build -t gcr.io/YOUR_PROJECT_ID/document-automation-mcp .

# Push to Container Registry
docker push gcr.io/YOUR_PROJECT_ID/document-automation-mcp

# Deploy to Cloud Run
gcloud run deploy document-automation-mcp \
  --image gcr.io/YOUR_PROJECT_ID/document-automation-mcp \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10
```

### 4. Test the Deployment

After deployment, you'll receive a URL like:
```
https://document-automation-mcp-xxxxx-uc.a.run.app
```

Test the API:
```bash
# Check health
curl https://document-automation-mcp-xxxxx-uc.a.run.app/

# Test analysis endpoint
curl -X POST https://document-automation-mcp-xxxxx-uc.a.run.app/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "path": "https://github.com/user/repo",
    "type": "github"
  }'
```

## Environment Variables

Set these in Cloud Run if needed:

- `LOG_LEVEL`: Set to `DEBUG` for verbose logging
- `MAX_WORKERS`: Number of worker processes (default: 4)

## Security Considerations

1. **Authentication**: By default, the service is publicly accessible. For production:
   ```bash
   gcloud run deploy document-automation-mcp \
     --no-allow-unauthenticated
   ```

2. **API Keys**: Implement API key authentication in the FastAPI app

3. **Rate Limiting**: Add rate limiting middleware to prevent abuse

## Monitoring

View logs:
```bash
gcloud run services logs read document-automation-mcp
```

View metrics in Cloud Console:
- CPU utilization
- Memory usage
- Request count
- Response latency

## Cost Optimization

1. Set appropriate min/max instances
2. Use Cloud Run's automatic scaling
3. Optimize container size (current: ~200MB)
4. Set reasonable timeout values

## Troubleshooting

### Common Issues

1. **Memory errors**: Increase memory allocation
2. **Timeout errors**: Increase timeout or optimize code
3. **Cold starts**: Set min-instances > 0

### Debug Mode

Deploy with debug logging:
```bash
gcloud run deploy document-automation-mcp \
  --set-env-vars LOG_LEVEL=DEBUG
```