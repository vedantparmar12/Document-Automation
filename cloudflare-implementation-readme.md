# Cloudflare Workers Deployment Guide for Document Automation MCP Server

This guide provides step-by-step instructions for deploying the Document Automation MCP Server on Cloudflare Workers.

## Prerequisites

- Cloudflare account (free tier is sufficient)
- Node.js and npm installed
- Wrangler CLI (`npm install -g wrangler`)

## Setup Steps

### 1. Authenticate with Cloudflare

```bash
npx wrangler login
```

This opens your browser for authentication. Complete the login process.

### 2. Enable Required Cloudflare Services

#### Workers Subdomain
1. Visit [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Click **Workers & Pages** in the sidebar
3. This automatically creates your workers.dev subdomain

#### R2 Storage
1. Click **R2** in the dashboard sidebar
2. Click **Enable R2**
3. Accept terms if prompted

#### D1 Database
1. Click **D1** in the dashboard sidebar
2. Click **Create database**
3. Name it: `mcp-server-db`
4. Copy the database ID shown after creation

### 3. Create R2 Bucket

In your terminal:
```bash
npx wrangler r2 bucket create mcp-documents
```

Or via dashboard:
1. Go to **R2** section
2. Click **Create bucket**
3. Name: `mcp-documents`
4. Location: Automatic

### 4. Configure wrangler.toml

Create or update `wrangler.toml` in your project root:

```toml
name = "document-automation-mcp-server"
main = "src/index.ts"
compatibility_date = "2024-01-01"

[vars]
MCP_SERVER_NAME = "document-automation-server"
MCP_SERVER_VERSION = "1.0.0"

# D1 Database binding
[[d1_databases]]
binding = "DB"
database_name = "mcp-server-db"
database_id = "YOUR_DATABASE_ID_HERE"  # Replace with your actual D1 database ID

# R2 Bucket binding
[[r2_buckets]]
binding = "BUCKET"
bucket_name = "mcp-documents"

# AI binding
[ai]
binding = "AI"

# Durable Objects binding
[[durable_objects.bindings]]
name = "MCP_SESSION"
class_name = "MCPSession"

# Migrations - IMPORTANT: Use new_sqlite_classes for free tier
[[migrations]]
tag = "v1"
new_sqlite_classes = ["MCPSession"]
```

### 5. Deploy to Cloudflare

```bash
npx wrangler deploy
```

Successful deployment shows:
```
Published document-automation-mcp-server
  https://document-automation-mcp-server.<your-subdomain>.workers.dev
Current Deployment ID: xxxx-xxxx-xxxx
```

## Configuration for AI Assistants

### Claude Desktop

Update your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "document-automation": {
      "url": "https://document-automation-mcp-server.<your-subdomain>.workers.dev",
      "type": "http"
    }
  }
}
```

### Cursor IDE

Update your MCP configuration:

```json
{
  "mcpServers": {
    "document-automation": {
      "url": "https://document-automation-mcp-server.<your-subdomain>.workers.dev",
      "type": "http"
    }
  }
}
```

## Troubleshooting

### Authentication Errors
- Run `npx wrangler logout` then `npx wrangler login`
- Ensure you're using the correct account

### Durable Objects Error (Code 10061)
- Ensure migrations section uses `new_sqlite_classes` not `new_classes`
- This is required for free tier accounts

### R2 Bucket Not Found
- Create the bucket before deploying
- Verify the bucket name matches exactly in wrangler.toml

### Workers Subdomain Missing
- Visit Workers & Pages section in dashboard
- This creates your subdomain automatically

## Resource Limits (Free Tier)

- **Requests:** 100,000/day
- **CPU Time:** 10ms per request
- **Memory:** 128MB
- **Durable Object Storage:** 10GB
- **R2 Storage:** 10GB/month

## Monitoring

View logs and metrics:
```bash
npx wrangler tail
```

Or use the Cloudflare dashboard:
1. Go to **Workers & Pages**
2. Click your worker
3. View **Analytics** and **Logs** tabs

## Updating Your Deployment

After making changes:
```bash
npx wrangler deploy
```

This automatically updates your worker with zero downtime.

## Environment Variables

Additional environment variables can be added in wrangler.toml:

```toml
[vars]
MCP_SERVER_NAME = "document-automation-server"
MCP_SERVER_VERSION = "1.0.0"
CUSTOM_VAR = "your-value"
```

For secrets:
```bash
npx wrangler secret put SECRET_NAME
```

## Support

- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [Wrangler CLI Documentation](https://developers.cloudflare.com/workers/wrangler/)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)