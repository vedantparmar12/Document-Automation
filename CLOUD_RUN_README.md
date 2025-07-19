# Document Automation MCP Server - Cloud Run Deployment

## Overview

This repository contains a Document Automation MCP (Model Context Protocol) Server that can analyze codebases and generate professional documentation. It's configured for deployment on Google Cloud Run.

## What's Included

### Core Components
- **FastAPI HTTP Server** (`src/main.py`) - REST API for document automation
- **MCP Server** (`src/server.py`) - Model Context Protocol implementation
- **Professional Documentation Generator** - Creates comprehensive, detailed documentation
- **Codebase Analyzer** - Analyzes local directories and GitHub repositories

### Deployment Files
- `Dockerfile` - Container configuration for Cloud Run
- `cloudbuild.yaml` - Automated CI/CD pipeline
- `.dockerignore` - Optimized container builds
- `.gcloudignore` - Excludes unnecessary files from Cloud Build
- `docker-compose.yml` - Local testing configuration

### Cleaned Structure
```
document-automation/
├── src/
│   ├── analyzers/         # Code analysis logic
│   ├── generators/        # Documentation generators
│   ├── security/          # Security validation
│   ├── tools/             # MCP tool implementations
│   ├── main.py           # FastAPI server
│   ├── server.py         # MCP server
│   └── types.py          # Type definitions
├── tests/                 # Test suite
├── Dockerfile            # Container definition
├── requirements.txt      # Python dependencies
└── DEPLOYMENT.md         # Deployment guide
```

## Quick Deployment

1. **Prerequisites**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud builds submit --config cloudbuild.yaml .
   ```

3. **Access the Service**
   - Your service URL will be displayed after deployment
   - Format: `https://document-automation-mcp-xxxxx-uc.a.run.app`

## API Endpoints

- `GET /` - Health check
- `POST /analyze` - Analyze a codebase
  ```json
  {
    "path": "https://github.com/user/repo",
    "type": "github"
  }
  ```

## Features

- ✅ Analyzes GitHub repositories and local directories
- ✅ Generates professional documentation without external dependencies
- ✅ Detects programming languages and project types
- ✅ Extracts dependencies and project structure
- ✅ Creates comprehensive markdown documentation
- ✅ Supports both HTTP API and MCP protocol

## Security

- Input validation on all requests
- Sanitized error messages
- No gitignore or external service dependencies
- Configurable authentication (see DEPLOYMENT.md)

## Local Testing

```bash
# Build locally
docker build -t doc-automation .

# Run with docker-compose
docker-compose up

# Test the API
curl http://localhost:8080/
```

## Support

For detailed deployment instructions, see `DEPLOYMENT.md`.

## License

MIT License - see LICENSE file