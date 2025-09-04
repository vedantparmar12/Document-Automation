# MCP Tools Reference Guide

## 🛠️ Available MCP Tools

The Document-Automation MCP server provides 5 sophisticated tools for comprehensive codebase analysis and documentation generation. Each tool is designed to work seamlessly with Claude Desktop, Cursor IDE, and other MCP-compatible clients.

---

## 📊 analyze_codebase

**The primary tool for comprehensive codebase analysis and structure extraction.**

### Purpose
Performs deep analysis of any codebase (local or remote) to extract project structure, dependencies, metrics, and architectural insights.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | string | ✅ | - | Local folder path or GitHub repository URL |
| `source_type` | enum | ✅ | - | `"local"` or `"github"` |
| `include_dependencies` | boolean | ❌ | `true` | Include dependency analysis |

### Returns

- **Project Structure**: Complete file hierarchy with metadata
- **Dependencies**: List of all project dependencies with versions
- **Code Metrics**: Lines of code, file counts, language distribution
- **Framework Detection**: Automatically detected frameworks and technologies
- **Architecture Analysis**: High-level architectural insights

### Example Usage

**Via Claude Desktop:**
```
Analyze the codebase at https://github.com/fastapi/fastapi with dependency analysis
```

**Direct JSON (for developers):**
```json
{
  "tool": "analyze_codebase",
  "parameters": {
    "path": "https://github.com/fastapi/fastapi",
    "source_type": "github",
    "include_dependencies": true
  }
}
```

### Example Output

```json
{
  "analysis_id": "analysis_20240101_120000_1234",
  "project_structure": {
    "name": "fastapi",
    "files": [
      {
        "name": "main.py",
        "path": "/fastapi/main.py",
        "size": 1024,
        "type": "python",
        "last_modified": "2024-01-01T12:00:00Z"
      }
    ],
    "subdirectories": [...]
  },
  "dependencies": [
    "starlette>=0.27.0",
    "pydantic>=1.7.4",
    "typing-extensions>=4.8.0"
  ],
  "metrics": {
    "total_files": 156,
    "total_lines": 12543,
    "languages": {
      "Python": 145,
      "JavaScript": 8,
      "HTML": 3
    }
  },
  "frameworks": ["FastAPI", "Starlette", "Pydantic"]
}
```

---

## 📝 generate_documentation

**Creates comprehensive, professional documentation from analyzed codebases.**

### Purpose
Transforms analysis results into beautifully formatted documentation with multiple output formats, architecture diagrams, and professional styling.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `analysis_id` | string | ✅ | - | ID from previous `analyze_codebase` call |
| `format` | enum | ❌ | `"markdown"` | Output format: `"markdown"`, `"html"`, `"rst"`, `"pdf"` |
| `include_api_docs` | boolean | ❌ | `true` | Include API endpoint documentation |
| `include_architecture` | boolean | ❌ | `true` | Include architecture diagrams |
| `include_examples` | boolean | ❌ | `true` | Include code examples and snippets |

### Returns

- **Formatted Documentation**: Complete documentation in requested format
- **Generation Metadata**: Statistics, word count, sections included
- **File Information**: Output file paths and sizes

### Example Usage

**Via Claude Desktop:**
```
Generate comprehensive HTML documentation for the analyzed codebase with architecture diagrams and API docs
```

**Direct JSON:**
```json
{
  "tool": "generate_documentation",
  "parameters": {
    "analysis_id": "analysis_20240101_120000_1234",
    "format": "html",
    "include_api_docs": true,
    "include_architecture": true,
    "include_examples": true
  }
}
```

### Supported Output Formats

- **Markdown** (`.md`) - GitHub-compatible, clean formatting
- **HTML** (`.html`) - Rich styling, interactive elements
- **RestructuredText** (`.rst`) - Sphinx-compatible documentation
- **PDF** (`.pdf`) - Professional print-ready format

---

## 📁 list_project_structure

**Provides detailed hierarchical view of project structure with file metadata.**

### Purpose
Creates a comprehensive tree view of the project structure with file sizes, types, and modification timestamps.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | string | ✅ | - | Local folder path or GitHub repository URL |
| `source_type` | enum | ✅ | - | `"local"` or `"github"` |
| `max_depth` | integer | ❌ | `5` | Maximum directory traversal depth |

### Returns

- **Hierarchical Structure**: Tree view of all files and directories
- **File Metadata**: Size, type, last modified date for each file
- **Directory Statistics**: File counts, total sizes per directory

### Example Usage

**Via Claude Desktop:**
```
List the project structure of https://github.com/microsoft/vscode with max depth of 3
```

**Direct JSON:**
```json
{
  "tool": "list_project_structure",
  "parameters": {
    "path": "https://github.com/microsoft/vscode",
    "source_type": "github",
    "max_depth": 3
  }
}
```

---

## 🔌 extract_api_endpoints

**Discovers and documents API endpoints from web framework codebases.**

### Purpose
Automatically detects API endpoints in popular web frameworks and generates comprehensive API documentation.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | string | ✅ | - | Local folder path or GitHub repository URL |
| `source_type` | enum | ✅ | - | `"local"` or `"github"` |
| `framework` | enum | ❌ | `"auto"` | Framework to analyze: `"auto"`, `"fastapi"`, `"flask"`, `"django"`, `"express"`, `"spring"` |

### Returns

- **Endpoint List**: All discovered API endpoints
- **HTTP Methods**: GET, POST, PUT, DELETE, etc.
- **Parameter Documentation**: Query params, path params, request bodies
- **Response Examples**: Sample responses where available

### Supported Frameworks

- **FastAPI** - Full support with automatic OpenAPI integration
- **Flask** - Route discovery and parameter extraction
- **Django** - URL pattern analysis and view documentation
- **Express.js** - Node.js route discovery
- **Spring Boot** - Java REST controller analysis
- **Auto Detection** - Automatically detects framework type

### Example Usage

**Via Claude Desktop:**
```
Extract all API endpoints from my FastAPI project at /path/to/my/project
```

**Direct JSON:**
```json
{
  "tool": "extract_api_endpoints",
  "parameters": {
    "path": "/path/to/fastapi/project",
    "source_type": "local",
    "framework": "fastapi"
  }
}
```

---

## 📦 analyze_dependencies

**Comprehensive dependency analysis with security insights and update recommendations.**

### Purpose
Analyzes project dependencies for security vulnerabilities, license compatibility, and provides update recommendations.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | string | ✅ | - | Local folder path or GitHub repository URL |
| `source_type` | enum | ✅ | - | `"local"` or `"github"` |
| `include_dev_dependencies` | boolean | ❌ | `false` | Include development dependencies |

### Returns

- **Dependency List**: All dependencies with current versions
- **Security Analysis**: Known vulnerabilities and severity levels
- **Update Recommendations**: Suggested version updates
- **License Information**: License compatibility analysis
- **Dependency Tree**: Visual representation of dependency relationships

### Example Usage

**Via Claude Desktop:**
```
Analyze dependencies for https://github.com/django/django including dev dependencies
```

**Direct JSON:**
```json
{
  "tool": "analyze_dependencies",
  "parameters": {
    "path": "https://github.com/django/django",
    "source_type": "github",
    "include_dev_dependencies": true
  }
}
```

---

## 🔄 Tool Workflow Examples

### Complete Documentation Generation Workflow

1. **Analyze the codebase:**
   ```
   Analyze the codebase at https://github.com/user/awesome-project
   ```

2. **Generate documentation:**
   ```
   Generate comprehensive documentation in HTML format for the analyzed project
   ```

3. **Extract API documentation:**
   ```
   Extract all API endpoints from the analyzed project
   ```

### Multi-Format Documentation

```
1. Analyze the codebase at /my/local/project
2. Generate markdown documentation for the project
3. Generate HTML documentation for the same project  
4. Generate PDF documentation for professional distribution
```

### Security-Focused Analysis

```
1. Analyze dependencies for https://github.com/user/security-critical-app
2. Analyze the codebase structure for security patterns
3. Generate documentation focusing on security architecture
```

---

## 🎯 Best Practices

### 1. Sequential Tool Usage

Always use `analyze_codebase` first, then use other tools with the returned analysis ID:

```
Analyze codebase → Get analysis_id → Use in generate_documentation
```

### 2. Format Selection

Choose the appropriate format based on your needs:
- **Markdown**: For GitHub repositories, collaborative editing
- **HTML**: For rich documentation websites, internal wikis
- **PDF**: For formal documentation, client deliverables
- **RST**: For Sphinx documentation, Python projects

### 3. Depth Control

Use appropriate `max_depth` values:
- **Depth 3-5**: For overview and architecture understanding
- **Depth 7-10**: For detailed analysis
- **Unlimited**: Only for small projects (performance impact)

### 4. Framework-Specific Analysis

Specify frameworks when known for better accuracy:
```
Extract API endpoints using FastAPI framework detection
```

### 5. Incremental Analysis

For large projects, consider analyzing specific directories:
```
Analyze the /src directory structure only
```

---

## 🚨 Error Handling

### Common Error Scenarios

1. **Invalid Paths**
   ```
   Error: Path '/invalid/path' does not exist or is not accessible
   ```

2. **Network Issues**
   ```
   Error: Unable to clone repository 'https://github.com/invalid/repo'
   ```

3. **Analysis ID Not Found**
   ```
   Error: Analysis ID 'invalid_id' not found. Please run analyze_codebase first.
   ```

4. **Format Not Supported**
   ```
   Error: Format 'invalid_format' not supported. Use: markdown, html, rst, pdf
   ```

### Error Recovery

1. **Check parameters** - Verify all required parameters are provided
2. **Validate paths** - Ensure paths exist and are accessible
3. **Retry analysis** - Run `analyze_codebase` again if analysis ID is missing
4. **Check permissions** - Ensure read access to local directories

---

## 🔧 Advanced Configuration

### Environment Variables

Set these environment variables for enhanced functionality:

```bash
# GitHub API token for private repositories
GITHUB_TOKEN=your_github_token

# Custom analysis timeout (seconds)
ANALYSIS_TIMEOUT=300

# Maximum file size for analysis (bytes)
MAX_FILE_SIZE=10485760
```

### Custom Templates

The system supports custom documentation templates. Place templates in:
```
src/templates/
├── markdown/
├── html/
├── rst/
└── pdf/
```

---

## 📈 Performance Considerations

### Analysis Speed

| Repository Size | Typical Analysis Time | Recommended Depth |
|----------------|---------------------|------------------|
| Small (< 100 files) | 5-15 seconds | Unlimited |
| Medium (100-1000 files) | 30-60 seconds | 5-7 levels |
| Large (1000+ files) | 2-5 minutes | 3-5 levels |

### Memory Usage

- **Local Analysis**: ~50-200MB RAM
- **GitHub Analysis**: ~100-500MB RAM (includes cloning)
- **Documentation Generation**: ~100-300MB RAM

### Optimization Tips

1. Use appropriate depth limits
2. Exclude large binary directories
3. Use specific framework detection
4. Consider analyzing subdirectories separately for very large projects

---

## 🤝 Integration Examples

### Claude Desktop Integration

```json
{
  "mcpServers": {
    "document-automation": {
      "command": "python",
      "args": ["C:\\path\\to\\Document-Automation\\src\\main.py"],
      "env": {
        "PYTHONPATH": "C:\\path\\to\\Document-Automation"
      }
    }
  }
}
```

### Cursor IDE Integration

```json
{
  "mcpServers": {
    "document-automation": {
      "command": "python",
      "args": ["src/main.py"],
      "cwd": "C:\\path\\to\\Document-Automation"
    }
  }
}
```

### API Integration

```python
import requests

# Direct HTTP API calls
response = requests.post('http://localhost:8000/analyze', json={
    'path': 'https://github.com/user/repo',
    'type': 'github'
})
```

---

## 📚 Additional Resources

- **[Setup Guide](SETUP_UV.md)** - Complete installation instructions
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment options
- **[API Reference](README.md)** - Complete API documentation
- **[Examples Repository](examples/)** - Sample usage patterns

---

**🎉 Happy documenting with MCP Document-Automation!**
