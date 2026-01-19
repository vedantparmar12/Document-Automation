# MCP Tools Reference

Complete reference for all MCP tools provided by Document Automation.

## Tools Overview

| Tool | Description | Input | Output |
|------|-------------|-------|--------|
| `analyze_codebase` | Full project analysis | path, source_type | Analysis result |
| `generate_documentation` | Create documentation | analysis_id, format | Formatted docs |
| `list_project_structure` | Get file hierarchy | path, max_depth | File tree |
| `extract_api_endpoints` | Find API routes | path, framework | Endpoint list |
| `analyze_dependencies` | Parse dependencies | path, include_dev | Dependency list |

---

## analyze_codebase

Performs comprehensive codebase analysis including structure, dependencies, frameworks, and patterns.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | string | Yes | - | Local path or GitHub URL |
| `source_type` | enum | No | auto | `"local"` or `"github"` |
| `include_dependencies` | boolean | No | true | Analyze dependencies |
| `max_depth` | integer | No | 5 | Max directory depth |
| `include_patterns` | array | No | [] | File patterns to include |
| `exclude_patterns` | array | No | [] | File patterns to exclude |

### Example Request

```json
{
  "tool": "analyze_codebase",
  "parameters": {
    "path": "https://github.com/tiangolo/fastapi",
    "source_type": "github",
    "include_dependencies": true,
    "max_depth": 4
  }
}
```

### Example Response

```json
{
  "project_name": "fastapi",
  "project_type": "Python Library",
  "description": "FastAPI framework, high performance, easy to learn",
  "languages": ["Python"],
  "frameworks": ["FastAPI", "Starlette", "Pydantic"],
  "dependencies": {
    "starlette": ">=0.27.0",
    "pydantic": ">=2.0",
    "typing-extensions": ">=4.8.0"
  },
  "file_structure": {
    "total_files": 156,
    "total_directories": 23,
    "tree": "..."
  },
  "key_features": {
    "API": ["Async support", "OpenAPI generation"],
    "Validation": ["Pydantic models", "Type hints"]
  },
  "analysis_id": "abc123"
}
```

---

## generate_documentation

Creates formatted documentation from a previous analysis result.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `analysis_id` | string | Yes* | - | ID from analyze_codebase |
| `path` | string | Yes* | - | Alternative: direct path |
| `format` | enum | No | markdown | Output format |
| `include_api_docs` | boolean | No | true | Include API documentation |
| `include_architecture` | boolean | No | true | Include diagrams |
| `include_examples` | boolean | No | true | Include code examples |
| `theme` | enum | No | professional | Styling theme |
| `output_path` | string | No | - | Save to file path |

*Either `analysis_id` or `path` required

### Format Options

| Format | Description | Extension |
|--------|-------------|-----------|
| `markdown` | GitHub-compatible Markdown | .md |
| `html` | Styled HTML with CSS | .html |
| `pdf` | Printable PDF document | .pdf |
| `rst` | ReStructuredText (Sphinx) | .rst |

### Example Request

```json
{
  "tool": "generate_documentation",
  "parameters": {
    "analysis_id": "abc123",
    "format": "markdown",
    "include_api_docs": true,
    "include_architecture": true,
    "theme": "professional"
  }
}
```

### Example Response

```json
{
  "content": "# FastAPI\n\n> FastAPI framework...\n\n## Features...",
  "format": "markdown",
  "metadata": {
    "word_count": 2500,
    "sections": 12,
    "diagrams": 3,
    "generation_time": "1.2s"
  }
}
```

---

## list_project_structure

Returns detailed project file structure with metadata.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | string | Yes | - | Project path or URL |
| `source_type` | enum | No | auto | `"local"` or `"github"` |
| `max_depth` | integer | No | 5 | Maximum traversal depth |
| `include_hidden` | boolean | No | false | Include hidden files |
| `include_sizes` | boolean | No | true | Include file sizes |

### Example Request

```json
{
  "tool": "list_project_structure",
  "parameters": {
    "path": "/home/user/myproject",
    "source_type": "local",
    "max_depth": 3
  }
}
```

### Example Response

```json
{
  "structure": {
    "name": "myproject",
    "type": "directory",
    "children": [
      {
        "name": "src",
        "type": "directory",
        "children": [
          {"name": "main.py", "type": "file", "size": 2048},
          {"name": "utils.py", "type": "file", "size": 1024}
        ]
      },
      {"name": "README.md", "type": "file", "size": 3072}
    ]
  },
  "summary": {
    "total_files": 25,
    "total_directories": 8,
    "total_size": 125000
  },
  "tree_view": "myproject/\n├── src/\n│   ├── main.py\n│   └── utils.py\n└── README.md"
}
```

---

## extract_api_endpoints

Discovers and documents API endpoints from web frameworks.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | string | Yes | - | Project path or URL |
| `source_type` | enum | No | auto | `"local"` or `"github"` |
| `framework` | enum | No | auto | Framework to detect |

### Supported Frameworks

| Framework | Detection |
|-----------|-----------|
| `fastapi` | `@app.get`, `@router.post`, etc. |
| `flask` | `@app.route`, `@blueprint.route` |
| `django` | `urlpatterns`, `path()`, `re_path()` |
| `express` | `app.get()`, `router.post()`, etc. |
| `spring` | `@GetMapping`, `@PostMapping`, etc. |
| `auto` | Auto-detect framework |

### Example Request

```json
{
  "tool": "extract_api_endpoints",
  "parameters": {
    "path": "/home/user/flask-app",
    "source_type": "local",
    "framework": "flask"
  }
}
```

### Example Response

```json
{
  "framework": "flask",
  "endpoints": [
    {
      "method": "GET",
      "path": "/api/users",
      "handler": "list_users",
      "file": "routes/users.py",
      "line": 15,
      "parameters": [],
      "description": "List all users"
    },
    {
      "method": "POST",
      "path": "/api/users",
      "handler": "create_user",
      "file": "routes/users.py",
      "line": 25,
      "parameters": ["name", "email"],
      "description": "Create new user"
    },
    {
      "method": "GET",
      "path": "/api/users/<int:id>",
      "handler": "get_user",
      "file": "routes/users.py",
      "line": 40,
      "parameters": ["id"],
      "description": "Get user by ID"
    }
  ],
  "total_endpoints": 3
}
```

---

## analyze_dependencies

Analyzes project dependencies and generates dependency documentation.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | string | Yes | - | Project path or URL |
| `source_type` | enum | No | auto | `"local"` or `"github"` |
| `include_dev_dependencies` | boolean | No | false | Include dev deps |
| `check_security` | boolean | No | false | Run security scan |
| `check_updates` | boolean | No | false | Check for updates |

### Supported Dependency Files

| File | Language/Tool |
|------|---------------|
| `requirements.txt` | Python (pip) |
| `pyproject.toml` | Python (poetry/pip) |
| `Pipfile` | Python (pipenv) |
| `package.json` | JavaScript/Node.js |
| `yarn.lock` | JavaScript (yarn) |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `pom.xml` | Java (Maven) |
| `build.gradle` | Java (Gradle) |
| `Gemfile` | Ruby |

### Example Request

```json
{
  "tool": "analyze_dependencies",
  "parameters": {
    "path": "/home/user/node-app",
    "source_type": "local",
    "include_dev_dependencies": true,
    "check_updates": true
  }
}
```

### Example Response

```json
{
  "package_manager": "npm",
  "dependency_file": "package.json",
  "dependencies": {
    "express": {
      "version": "^4.18.0",
      "type": "production",
      "latest": "4.18.2",
      "update_available": true
    },
    "mongoose": {
      "version": "^7.0.0",
      "type": "production",
      "latest": "7.0.0",
      "update_available": false
    }
  },
  "dev_dependencies": {
    "jest": {
      "version": "^29.0.0",
      "type": "development"
    }
  },
  "summary": {
    "total": 15,
    "production": 10,
    "development": 5,
    "updates_available": 3
  }
}
```

---

## Error Responses

All tools return errors in a consistent format:

```json
{
  "error": {
    "code": "REPOSITORY_NOT_FOUND",
    "message": "Could not find or access the repository",
    "details": "404 Not Found: https://github.com/user/nonexistent"
  }
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `REPOSITORY_NOT_FOUND` | Cannot find the specified repository |
| `PERMISSION_DENIED` | No access to private repository |
| `INVALID_PATH` | Path does not exist or is invalid |
| `RATE_LIMITED` | GitHub API rate limit exceeded |
| `ANALYSIS_FAILED` | Error during analysis process |
| `INVALID_FORMAT` | Unsupported output format |
| `TIMEOUT` | Operation timed out |

---

## Best Practices

### 1. Start with Analysis
Always run `analyze_codebase` first to get a complete picture before generating documentation.

### 2. Use Appropriate Depth
For large repositories, limit `max_depth` to avoid long processing times.

### 3. Cache Analysis Results
Use the `analysis_id` from `analyze_codebase` to generate multiple documentation formats without re-analyzing.

### 4. Set GitHub Token
For private repositories or to avoid rate limits:
```bash
export GITHUB_TOKEN=ghp_your_token_here
```

### 5. Filter When Needed
Use `include_patterns` and `exclude_patterns` to focus on relevant files.
