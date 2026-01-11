# Document Automation

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/Protocol-MCP-purple.svg)](https://modelcontextprotocol.io/)
[![GitHub](https://img.shields.io/badge/GitHub-vedantparmar12%2FDocument--Automation-black.svg)](https://github.com/vedantparmar12/Document-Automation)

> **A sophisticated Model Context Protocol (MCP) server that enables AI assistants to automatically analyze codebases and generate comprehensive, professional documentation.**

## 🎯 What's New - Beautiful, Comprehensive Documentation!

**NOW PRODUCTION-READY!** The system generates **beautiful, comprehensive documentation** that works for ANY repository:

### 🎨 Beautiful Documentation Generation

✅ **Comprehensive Workflow Analysis** - Understands complete project workflow and data flow
✅ **Intelligent Project Understanding** - Explains WHY the project exists and HOW it works
✅ **Visual Diagrams** - Workflow diagrams, component interactions, data flow visualizations
✅ **Real Code Examples** - Actual code from the project with full context
✅ **Complete User Journey** - Step-by-step guide for different use cases
✅ **API Documentation** - Discovered endpoints with examples
✅ **Production-Ready** - Works for any size repository (small to massive)

### 🔍 Smart Analysis

✅ **Extracts REAL features** from actual code (classes, functions, APIs)
✅ **Uses ACTUAL project metadata** (version, license, description, author)
✅ **Generates UNIQUE architecture** based on actual directory structure
✅ **Detects integrations** (AWS, Google Cloud, databases, APIs)
✅ **Identifies workflows** (pipelines, processes, handlers)
✅ **Maps data flow** (database, APIs, file operations, queues)

### 📖 Beautiful Output

- **Clear sections** with emojis and visual hierarchy
- **Comprehensive but readable** - not overwhelming
- **Professional formatting** with badges and diagrams
- **Complete explanations** - no generic templates!
- **Works universally** - any GitHub repo or local directory

**Result**: Every project gets stunning, unique documentation that fully explains what it does and how it works!

## Overview

Document Automation is an intelligent documentation generation system that bridges the gap between AI assistants and code documentation workflows. By implementing the Model Context Protocol (MCP), it allows AI assistants like Claude to seamlessly analyze project structures, extract insights, and generate professional-grade documentation automatically.

### Key Features

- **Intelligent Codebase Analysis** - Deep project structure and dependency analysis
- **Professional Documentation Generation** - Multi-format output (Markdown, HTML, RST, PDF)
- **AI Assistant Integration** - Native Claude Desktop and Cursor IDE support
- **Multi-Platform Deployment** - Local, Docker, and Google Cloud Run ready
- **Advanced MCP Tools** - 5 specialized analysis and generation tools
- **Security-First Design** - Built-in validation and safety measures

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Assistant (Claude)                    │
│  ┌─────────────────┐    ┌─────────────────┐               │
│  │  Claude Desktop │    │   Cursor IDE    │               │
│  └─────────────────┘    └─────────────────┘               │
└─────────────────────────────┬───────────────────────────────┘
                              │ MCP Protocol
┌─────────────────────────────▼───────────────────────────────┐
│                 Document Automation Server                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Analyzers  │  │ Generators  │  │    Tools    │        │
│  │             │  │             │  │             │        │
│  │ • Base      │  │ • Standard  │  │ • MCP       │        │
│  │ • Codebase  │  │ • Professional│ │ • Registry  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐                    ┌─────────────┐        │
│  │  Security   │                    │    Types    │        │
│  └─────────────┘                    └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- **Python 3.8+**
- **Git**
- **Claude Desktop** or **Cursor IDE** (for AI integration)

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

#### Analyzing Any GitHub Repository

```
"Analyze the codebase at https://github.com/facebook/react"
```

For **private repositories**, set the `GITHUB_TOKEN` environment variable:

```bash
# Windows PowerShell
$env:GITHUB_TOKEN = "ghp_your_personal_access_token"

# Linux/macOS
export GITHUB_TOKEN=ghp_your_personal_access_token
```

Then ask your AI assistant to analyze the repo:
```
"Analyze the private repo at https://github.com/myorg/private-repo"
```

#### Analyzing Local Directories

```
"Analyze the local codebase at C:/Projects/my-app"
```

or on Unix/macOS:
```
"Analyze the local codebase at /home/user/projects/my-app"
```

#### What Happens

The system will automatically:
1. **Analyze** the project structure and dependencies
2. **Detect** frameworks and technology stack
3. **Generate** architecture diagrams (Mermaid format)
4. **Extract** API endpoints and database schemas
5. **Create** professional documentation in multiple formats

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | Personal access token for private repos | No (only for private repos) |

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
      "args": ["/path/to/Document-Automation/src/main.py"],
      "env": {}
    }
  }
}
```

2. **Restart Claude Desktop**

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

### MCP Server Infrastructure (src/server.py, src/main.py)
- **Purpose:** Core MCP protocol implementation
- **Key Features:**
  - Tool registration and discovery
  - Request/response handling
  - Error management and validation
  - Async operation support
- **Size:** 13.2KB server implementation

### Analyzers Module (src/analyzers/)
- **Base Analyzer** (base_analyzer.py, 13.9KB)
  - Abstract base class for all analysis operations
  - Common analysis patterns and utilities
  - File system traversal and parsing
  
- **Codebase Analyzer** (codebase_analyzer.py, 7.0KB)
  - Project structure analysis
  - Dependency extraction
  - Language detection and metrics
  - Git repository integration

### Documentation Generators (src/generators/)
- **Standard Generator** (documentation_generator.py, 15.5KB)
  - Basic documentation generation
  - Multiple output formats support
  - Template-based rendering
  
- **Professional Generator** (professional_doc_generator.py, 37.2KB)
  - Advanced formatting and styling
  - Enterprise-grade documentation
  - Architecture diagrams and visualizations
  - Largest file in the project (1,209 lines)

### MCP Tools (src/tools/)
- **Documentation Tools** (documentation_tools.py, 18.5KB)
  - Implementation of all MCP tools
  - Tool parameter validation
  - Response formatting
  
- **Tool Registration** (register_tools.py, 2.5KB)
  - Dynamic tool discovery
  - MCP protocol compliance
  - Tool metadata management

### Security Layer (src/security/)
- **Validation Module** (validation.py, 8.2KB)
  - Input sanitization
  - Path traversal protection
  - Security policy enforcement

### Type System (src/types.py, 5.1KB)
- Pydantic data models
- Request/response schemas
- Type safety enforcement

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

**Total Dependencies:** 15 production packages

## Deployment Options

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
```

## Project Metrics

### Scale
- **Total Files:** 134
- **Total Lines of Code:** 13,231
- **Python Files:** 20
- **Documentation Files:** 13 markdown files
- **Configuration Files:** 5 JSON + 2 YAML files

### File Type Distribution
- **Python Files:** 20 (core functionality)
- **Markdown Files:** 13 (documentation)
- **JSON Files:** 5 (configuration)
- **YAML Files:** 2 (deployment config)
- **Shell Scripts:** 2 (setup automation)

### Largest Components
1. **Professional Doc Generator:** 1,209 lines (37.2KB)
2. **Documentation Tools:** 18.5KB
3. **Documentation Generator:** 15.5KB
4. **Base Analyzer:** 13.9KB
5. **MCP Server:** 13.2KB

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
- Uses modern Python async frameworks for optimal performance
