# Document Automation

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/Protocol-MCP-purple.svg)](https://modelcontextprotocol.io/)
[![Cloudflare Workers](https://img.shields.io/badge/Deploy-Cloudflare%20Workers-orange.svg)](https://workers.cloudflare.com/)
[![GitHub](https://img.shields.io/badge/GitHub-vedantparmar12%2FDocument--Automation-black.svg)](https://github.com/vedantparmar12/Document-Automation)

> **A sophisticated Model Context Protocol (MCP) server that enables AI assistants to automatically analyze codebases and generate comprehensive, professional documentation.**

## Overview

Document Automation is an intelligent documentation generation system that bridges the gap between AI assistants and code documentation workflows. By implementing the Model Context Protocol (MCP), it allows AI assistants like Claude to seamlessly analyze project structures, extract insights, and generate professional-grade documentation automatically.

### Key Features

- **Intelligent Codebase Analysis** - Deep project structure and dependency analysis
- **Professional Documentation Generation** - Multi-format output (Markdown, HTML, RST, PDF)
- **AI Assistant Integration** - Native Claude Desktop and Cursor IDE support
- **Multi-Platform Deployment** - Local, Docker, Google Cloud Run, and **Cloudflare Workers**
- **Advanced MCP Tools** - 5 specialized analysis and generation tools
- **Security-First Design** - Built-in validation and safety measures
- **Edge Computing Ready** - Deployed globally via Cloudflare's edge network

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Assistant (Claude)                    │
│  ┌─────────────────┐    ┌─────────────────┐               │
│  │  Claude Desktop │    │   Cursor IDE    │               │
│  └─────────────────┘    └─────────────────┘               │
└─────────────────────────┬───────────────────────────────────┘
                              │ MCP Protocol
┌─────────────────────────────▼───────────────────────────────┐
│          Document Automation Server (Cloudflare Edge)       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Analyzers  │  │ Generators  │  │    Tools    │        │
│  │             │  │             │  │             │        │
│  │ • Base      │  │ • Standard  │  │ • MCP       │        │
│  │ • Codebase  │  │ • Professional│ │ • Registry  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐                    ┌─────────────┐        │
│  │  Security   │                    │    Types    │        │
│  └─────────────┘                    └─────────────┘        │
│                                                             │
│  Cloudflare Services:                                       │
│  • Workers (Edge Computing)                                 │
│  • D1 Database (Distributed SQLite)                         │
│  • R2 Storage (Object Storage)                              │
│  • AI (LLM Integration)                                     │
│  • Durable Objects (Stateful Sessions)                      │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- **Python 3.8+** (for local development)
- **Git**
- **Claude Desktop** or **Cursor IDE** (for AI integration)
- **Cloudflare Account** (for deployment - free tier available)
- **Wrangler CLI** (for Cloudflare deployment)

### Installation

```bash
# Clone the repository
git clone https://github.com/vedantparmar12/Document-Automation.git
cd Document-Automation

# Install dependencies
pip install -r requirements.txt

# Run setup (choose your platform)
# Windows
setup_claude_desktop.bat

# Unix/Linux/macOS
chmod +x setup_claude_desktop.sh
./setup_claude_desktop.sh
```

### Basic Usage

Once installed, you can use the system through your AI assistant:

```
"Analyze the codebase at /path/to/my/project and generate comprehensive documentation"
```

The system will automatically:
1. **Analyze** the project structure and dependencies
2. **Extract** key architectural insights
3. **Generate** professional documentation
4. **Format** the output in your preferred style

## Deployment Options

### Cloudflare Workers (Recommended for Production)

#### Prerequisites
1. **Cloudflare Account** - Sign up at [dash.cloudflare.com](https://dash.cloudflare.com)
2. **Wrangler CLI** - Install with `npm install -g wrangler`

#### Deployment Steps

1. **Authenticate with Cloudflare:**
```bash
npx wrangler login
```

2. **Create required resources:**
```bash
# Create D1 Database
npx wrangler d1 create mcp-server-db

# Note the database ID returned - you'll need it for wrangler.toml
```

3. **Configure wrangler.toml:**
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
database_id = "YOUR_DATABASE_ID_HERE"  # Replace with your actual ID

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

# Migrations for free tier
[[migrations]]
tag = "v1"
new_sqlite_classes = ["MCPSession"]  # Use new_sqlite_classes for free tier
```

4. **Enable required services in Cloudflare Dashboard:**
   - Navigate to **Workers & Pages** to create workers.dev subdomain
   - Enable **R2** storage service
   - Create R2 bucket named `mcp-documents`

5. **Deploy to Cloudflare:**
```bash
npx wrangler deploy
```

Your MCP server will be available at:
```
https://document-automation-mcp-server.<your-subdomain>.workers.dev
```

#### Cloudflare Resources Used
- **Workers**: Edge computing for MCP server
- **D1 Database**: Stores analysis results and metadata
- **R2 Storage**: Stores generated documentation
- **AI**: Powers intelligent analysis features
- **Durable Objects**: Maintains MCP session state

### Local Development
```bash
# Start the MCP server
python src/main.py

# Server will be available for MCP clients
```

### Docker Deployment
```bash
# Build container
docker build -t document-automation .

# Run container
docker run -p 8000:8000 document-automation

# Or use docker-compose
docker-compose up
```

### Google Cloud Run
```bash
# Deploy to Cloud Run
gcloud run deploy document-automation \
  --source . \
  --platform managed \
  --region us-central1
```

## MCP Tools Reference

### analyze_codebase
Performs comprehensive codebase analysis and structure extraction.

**Parameters:**
- `path` (string): Local folder path or GitHub repository URL
- `source_type` (enum): `"local"` | `"github"`
- `include_dependencies` (boolean): Include dependency analysis (default: true)

**Returns:**
- Project structure with file hierarchy
- Dependencies and versions
- Codebase metrics and statistics
- Language distribution analysis

**Example:**
```json
{
  "tool": "analyze_codebase",
  "parameters": {
    "path": "https://github.com/user/repo",
    "source_type": "github",
    "include_dependencies": true
  }
}
```

### generate_documentation
Creates comprehensive documentation from analyzed codebase.

**Parameters:**
- `analysis_id` (string): ID from previous analyze_codebase call
- `format` (enum): `"markdown"` | `"html"` | `"rst"` | `"pdf"` (default: "markdown")
- `include_api_docs` (boolean): Include API documentation (default: true)
- `include_architecture` (boolean): Include architecture diagrams (default: true)
- `include_examples` (boolean): Include code examples (default: true)

**Returns:**
- Formatted documentation content
- Generation metadata
- Word count and statistics

### list_project_structure
Provides detailed project structure with file information.

**Parameters:**
- `path` (string): Project path
- `source_type` (enum): `"local"` | `"github"`
- `max_depth` (integer): Maximum traversal depth (default: 5)

**Returns:**
- Hierarchical file structure
- File sizes and types
- Last modification timestamps

### extract_api_endpoints
Discovers and documents API endpoints from web frameworks.

**Parameters:**
- `path` (string): Project path
- `source_type` (enum): `"local"` | `"github"`
- `framework` (enum): `"auto"` | `"fastapi"` | `"flask"` | `"django"` | `"express"` | `"spring"`

**Returns:**
- List of discovered endpoints
- HTTP methods and paths
- Parameter documentation

### analyze_dependencies
Analyzes project dependencies and generates dependency documentation.

**Parameters:**
- `path` (string): Project path
- `source_type` (enum): `"local"` | `"github"`
- `include_dev_dependencies` (boolean): Include development dependencies (default: false)

**Returns:**
- Dependency list with versions
- Security analysis
- Update recommendations

## Configuration

### Claude Desktop Integration

1. **Configure your `claude_desktop_config.json`:**

```json
{
  "mcpServers": {
    "document-automation": {
      "command": "python",
      "args": [
        "C:\\Users\\YourUser\\Projects\\Document-Automation\\src\\server.py"
      ],
      "env": {
        "PYTHONPATH": "C:\\Users\\YourUser\\Projects\\Document-Automation"
      }
    }
  }
}
```

2. **For Cloudflare deployment, use:**

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

3. **Restart Claude Desktop**

### Cursor IDE Integration

1. **Update your MCP settings:**

```json
{
  "mcpServers": {
    "document-automation": {
      "command": "python",
      "args": ["src/main.py"]
    }
  }
}
```

2. **Follow the detailed setup guide in `CURSOR_MCP_SETUP_GUIDE.md`**

## Project Structure

```
Document-Automation/
├── Configuration
│   ├── claude_desktop_config.json      # Claude Desktop setup
│   ├── cursor_mcp_config.json          # Cursor IDE integration
│   ├── docker-compose.yml              # Container orchestration
│   ├── cloudbuild.yaml                 # Google Cloud Build
│   ├── wrangler.toml                   # Cloudflare Workers config
│   └── requirements.txt                # Python dependencies
│
├── Documentation
│   ├── README.md                       # Project overview
│   ├── SETUP.md                       # Installation guide
│   ├── DEPLOYMENT.md                   # Deployment instructions
│   ├── MCP_CLIENT_SETUP.md            # MCP client setup
│   ├── CURSOR_MCP_SETUP_GUIDE.md      # Cursor IDE guide
│   └── QUICK_SETUP.md                 # Quick start guide
│
├── Scripts
│   ├── setup_claude_desktop.bat       # Windows setup
│   └── setup_claude_desktop.sh        # Unix/Linux setup
│
├── Testing
│   ├── test_mcp.py                     # MCP protocol tests
│   └── test_mcp_simple.py             # Basic functionality tests
│
├── Source Code
│   ├── src/
│   │   ├── main.py                    # Application entry point
│   │   ├── server.py                  # MCP server implementation
│   │   ├── index.ts                   # Cloudflare Worker entry
│   │   ├── types.py                   # Data models and schemas
│   │   │
│   │   ├── analyzers/                 # Analysis components
│   │   │   ├── base_analyzer.py       # Base analysis framework
│   │   │   └── codebase_analyzer.py   # Codebase analysis logic
│   │   │
│   │   ├── generators/                # Documentation generators
│   │   │   ├── documentation_generator.py   # Standard documentation
│   │   │   └── professional_doc_generator.py # Professional formatting
│   │   │
│   │   ├── security/                  # Security layer
│   │   │   └── validation.py          # Input validation & safety
│   │   │
│   │   └── tools/                     # MCP tools implementation
│   │       ├── documentation_tools.py # Tool implementations
│   │       └── register_tools.py      # Tool registration system
│   │
│   └── tests/                         # Test suite
│       ├── conftest.py               # Test configuration
│       ├── test_analyzer.py          # Analyzer tests
│       └── __init__.py
│
└── docs/                              # Generated documentation
    └── *.md                           # Auto-generated analysis reports
```

## Core Components

### MCP Server Infrastructure
The server implementation spans multiple files including `server.py`, `main.py`, and `index.ts` for Cloudflare Workers integration. This core infrastructure handles:
- Tool registration and discovery
- Request/response handling  
- Error management and validation
- Async operation support
- Cloudflare Workers integration

### Analyzers Module
The analyzers directory contains two main components:

**Base Analyzer** (`base_analyzer.py`) provides the foundation for all analysis operations with common patterns, utilities, and file system traversal capabilities.

**Codebase Analyzer** (`codebase_analyzer.py`) specializes in project structure analysis, dependency extraction, language detection, and Git repository integration.

### Documentation Generators
The generators module includes:

**Standard Generator** (`documentation_generator.py`) for basic documentation generation with multiple output format support and template-based rendering.

**Professional Generator** (`professional_doc_generator.py`) - the most comprehensive component in the project - handles advanced formatting, enterprise-grade documentation, and architecture diagram generation.

### MCP Tools
The tools directory implements the MCP protocol:

**Documentation Tools** (`documentation_tools.py`) contains all MCP tool implementations with parameter validation and response formatting.

**Tool Registration** (`register_tools.py`) manages dynamic tool discovery and maintains MCP protocol compliance.

### Security Layer
The **Validation Module** (`validation.py`) ensures input sanitization, prevents path traversal attacks, and enforces security policies throughout the system.

### Type System
The `types.py` file defines Pydantic data models, request/response schemas, and enforces type safety across the application.

## Dependencies

### Core Framework Dependencies
- **mcp** - Model Context Protocol implementation
- **fastapi** - Modern async web framework
- **uvicorn[standard]** - ASGI server with standard extensions
- **pydantic** - Data validation and serialization

### Documentation & Template Engine
- **jinja2** - Template engine for documentation generation
- **markdown** - Markdown processing and rendering
- **pygments** - Syntax highlighting for code blocks

### File & Data Processing
- **aiofiles** - Async file operations
- **toml** - TOML configuration file parsing
- **PyYAML** - YAML file processing
- **python-dotenv** - Environment variable management

### External Communication
- **httpx** - Modern async HTTP client
- **requests** - Traditional HTTP library for compatibility
- **gitpython** - Git repository analysis and manipulation

### Development Support
- **typing-extensions** - Extended type hints for better IDE support

### Cloudflare Dependencies
- **wrangler** - Cloudflare Workers CLI
- **@cloudflare/workers-types** - TypeScript types for Workers
- **@cloudflare/ai** - Cloudflare AI integration

**Total Dependencies:** 15 production packages + Cloudflare tools

## Usage Examples

### Basic Codebase Analysis
Ask your AI assistant:
```
"Analyze the codebase at https://github.com/user/repo"
```

This triggers:
1. analyze_codebase tool call
2. Automatic structure analysis
3. Dependency extraction
4. Metrics calculation

### Generate Documentation
Ask your AI assistant:
```
"Generate comprehensive documentation for the analyzed codebase"
```

This triggers:
1. generate_documentation tool call
2. Professional formatting
3. Multiple output formats
4. Architecture diagrams

### API Endpoint Discovery
Ask your AI assistant:
```
"Extract all API endpoints from my FastAPI project"
```

This triggers:
1. extract_api_endpoints tool call
2. Framework detection
3. Endpoint documentation
4. Parameter extraction

## Development & Testing

### Testing Framework
- **Unit Tests:** tests/test_analyzer.py
- **Integration Tests:** test_mcp.py, test_mcp_simple.py
- **Configuration:** tests/conftest.py

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run MCP integration tests
python test_mcp_simple.py

# Run with coverage
python -m pytest tests/ --cov=src/
```

### Development Setup
```bash
# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements.txt

# Run in development mode
python src/main.py

# For Cloudflare development
npx wrangler dev
```

## Performance & Scalability

### Cloudflare Edge Deployment Benefits
- **Global Distribution:** Deployed to 300+ edge locations worldwide
- **Low Latency:** Sub-50ms response times globally
- **Auto-scaling:** Handles millions of requests without configuration
- **DDoS Protection:** Built-in enterprise-grade protection
- **Zero Cold Starts:** Always-warm edge computing

### Resource Limits (Cloudflare Free Tier)
- **100,000 requests/day**
- **10ms CPU time per request**
- **1MB request/response size**
- **Unlimited bandwidth**

## Project Metrics

- **Total Files:** 134
- **Total Lines of Code:** Over 13,000
- **Python Files:** 20 core functionality files
- **Documentation Files:** 13 comprehensive markdown guides
- **Configuration Files:** Multiple JSON, YAML, and TOML files

### Core Components Distribution
- Primary implementation in Python for analysis and generation
- TypeScript for Cloudflare Worker integration
- Comprehensive documentation suite
- Multiple deployment configurations
- Automated setup scripts for different platforms

The Professional Documentation Generator represents the most extensive component, containing over 1,200 lines of sophisticated formatting and visualization logic.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions, issues, or feature requests:
- Open an issue on [GitHub](https://github.com/vedantparmar12/Document-Automation/issues)
- Check the documentation in the `docs/` folder
- Review the setup guides for your specific use case

## Acknowledgments

- Built on the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- Integrates with [Claude](https://claude.ai/) and [Cursor IDE](https://cursor.sh/)
- Deployed on [Cloudflare Workers](https://workers.cloudflare.com/)
- Uses modern Python async frameworks for optimal performance
- Leverages Cloudflare's global edge network for worldwide availability