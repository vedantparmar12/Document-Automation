# Deploying MCP Server to Cloudflare Workers

This guide explains how to deploy an MCP (Model Context Protocol) server to Cloudflare Workers using Wrangler.

## Important Considerations

**MCP servers are traditionally designed to run as local processes with stdio communication**, which doesn't directly translate to Cloudflare Workers' serverless environment. This implementation provides HTTP and WebSocket adapters for MCP communication.

## Prerequisites

1. **Cloudflare Account**: Sign up at [dash.cloudflare.com](https://dash.cloudflare.com)
2. **Node.js**: Version 18 or higher
3. **Wrangler CLI**: Installed globally or as dev dependency

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Wrangler

Update `wrangler.toml` with your specific settings:

```toml
name = "your-mcp-server-name"
# Update database_id if using D1
# Update bucket_name if using R2
```

### 3. Login to Cloudflare

```bash
npx wrangler login
```

### 4. Create Required Resources (Optional)

If using D1 Database:
```bash
npx wrangler d1 create mcp-server-db
```

If using R2 Storage:
```bash
npx wrangler r2 bucket create mcp-documents
```

### 5. Deploy the Server

Development:
```bash
npm run dev
# or
npx wrangler dev
```

Production:
```bash
npm run deploy
# or
npx wrangler deploy
```

## Architecture Differences

### Traditional MCP Server (Python)
- Runs as a local process
- Uses stdio for communication
- Direct filesystem access
- Can analyze local codebases

### Cloudflare Workers MCP Server
- Runs as serverless functions
- Uses HTTP/WebSocket for communication
- No filesystem access (use R2 or external URLs)
- Limited to web-accessible resources

## API Endpoints

### Health Check
```
GET https://your-worker.workers.dev/health
```

### MCP HTTP Endpoint
```
POST https://your-worker.workers.dev/mcp
Content-Type: application/json

{
  "method": "tools/list",
  "params": {}
}
```

### WebSocket Endpoint
```
wss://your-worker.workers.dev/ws
```

## Limitations

1. **No Local File Access**: Cloudflare Workers can't access local filesystems. You'll need to:
   - Use URLs for code analysis
   - Store files in R2
   - Fetch from GitHub repositories

2. **Python to JavaScript Migration**: The original Python tools need to be rewritten in TypeScript/JavaScript.

3. **Execution Time Limits**: Workers have a 30-second CPU time limit (or 15 minutes for Durable Objects).

4. **Memory Constraints**: Limited to 128MB of memory.

## Alternative Approaches

### 1. Python Workers (Beta)
Cloudflare has Python Workers in beta, but MCP SDK support would need verification.

### 2. Container Deployment
Consider using:
- **Google Cloud Run** (already configured in your repo)
- **AWS Lambda** with container support
- **Fly.io** for containerized apps
- **Railway** or **Render** for easy deployments

### 3. Hybrid Approach
- Deploy core MCP server elsewhere
- Use Cloudflare Workers as a proxy/gateway
- Leverage Workers for caching and edge computing

## Next Steps

To fully implement this MCP server on Cloudflare Workers, you would need to:

1. **Port Python Tools**: Rewrite all Python-based analysis tools in TypeScript
2. **Implement Transport Adapter**: Create a proper HTTP/WebSocket transport for MCP protocol
3. **Handle Storage**: Implement R2 or external storage for file operations
4. **Add Authentication**: Secure your endpoints with Cloudflare Access or API keys
5. **Test Integration**: Verify compatibility with Claude Desktop/other MCP clients

## Recommendation

Given the significant architectural differences and the need to rewrite your Python codebase, **I recommend sticking with your existing Google Cloud Run deployment** or using a container-based platform that supports Python directly. This will allow you to maintain your current codebase without a complete rewrite.

If you specifically need Cloudflare's edge computing capabilities, consider using Workers as a proxy layer in front of your containerized MCP server.