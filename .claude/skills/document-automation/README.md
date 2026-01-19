# Document Automation Skill

A Claude Code skill for intelligent codebase analysis and professional documentation generation.

## Overview

This skill enables Claude to:
- **Analyze** any codebase (GitHub repos or local directories)
- **Generate** comprehensive, professional documentation
- **Create** architecture diagrams (Mermaid format)
- **Document** APIs, dependencies, and project structure
- **Export** to multiple formats (Markdown, HTML, PDF)

## Installation

### Prerequisites

- Python 3.8+
- Git
- GitHub CLI (optional, for PR integration)

### Setup

```bash
# Clone the Document Automation project
git clone https://github.com/vedantparmar12/Document-Automation.git
cd Document-Automation

# Install dependencies
pip install -r requirements.txt

# (Optional) Set GitHub token for private repos
export GITHUB_TOKEN=ghp_your_personal_access_token
```

### Configure Claude Desktop

Add to your `claude_desktop_config.json`:

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

## Quick Start

### Analyze a GitHub Repository

```
"Analyze the codebase at https://github.com/facebook/react"
```

### Analyze a Local Directory

```
"Analyze my project at /home/user/projects/myapp"
```

### Generate Documentation

```
"Generate comprehensive documentation for this project"
```

### Create API Documentation

```
"Document all API endpoints in my FastAPI project"
```

## Features

### Intelligent Analysis

| Feature | Description |
|---------|-------------|
| Structure Analysis | Parse directory hierarchy and file organization |
| Framework Detection | Auto-detect Django, Flask, FastAPI, React, Vue, etc. |
| Dependency Parsing | Extract from requirements.txt, package.json, etc. |
| Code Extraction | Find classes, functions, APIs, and models |
| Workflow Mapping | Understand data flow and component interactions |

### Documentation Generation

| Format | Use Case |
|--------|----------|
| Markdown | GitHub READMEs, wikis |
| HTML | Standalone documentation sites |
| PDF | Printable documentation |
| RST | Sphinx-compatible docs |

### Architecture Diagrams

- Component diagrams
- Data flow diagrams
- Class diagrams
- Sequence diagrams

## Usage Examples

### Basic Analysis

```python
from src.analyzers.codebase_analyzer import CodebaseAnalyzer

analyzer = CodebaseAnalyzer()
result = analyzer.analyze('/path/to/project', source_type='local')
print(result.project_name)
print(result.frameworks)
print(result.dependencies)
```

### Generate Documentation

```python
from src.generators.professional_doc_generator import ProfessionalDocumentationGenerator

generator = ProfessionalDocumentationGenerator()
docs = generator.generate(analysis_result, {
    'format': 'markdown',
    'include_diagrams': True,
    'include_api_docs': True
})
print(docs.content)
```

### Extract API Endpoints

```python
from src.analyzers.framework_detector import FrameworkDetector

detector = FrameworkDetector()
endpoints = detector.extract_endpoints('/path/to/project')
for endpoint in endpoints:
    print(f"{endpoint.method} {endpoint.path}")
```

## MCP Tools

The skill provides these MCP tools:

1. **analyze_codebase** - Full project analysis
2. **generate_documentation** - Create formatted docs
3. **list_project_structure** - Get file hierarchy
4. **extract_api_endpoints** - Find API routes
5. **analyze_dependencies** - Parse dependencies

## File Structure

```
.claude/skills/document-automation/
├── SKILL.md           # Main skill definition
├── README.md          # This file
├── EXAMPLES.md        # Usage examples
├── MCP-TOOLS.md       # Tool reference
├── QUICKSTART.md      # Quick start guide
└── scripts/
    ├── analyze-repo.py    # Repository analyzer
    ├── generate-docs.py   # Documentation generator
    └── verify-install.sh  # Installation checker
```

## Troubleshooting

### "Module not found" Error

```bash
# Ensure you're in the correct directory
cd Document-Automation

# Install in development mode
pip install -e .
```

### GitHub Rate Limit

```bash
# Set personal access token
export GITHUB_TOKEN=ghp_your_token

# Check rate limit
gh api rate_limit
```

### Large Repository Timeout

```bash
# Use shallow analysis
python scripts/analyze-repo.py repo_url --shallow --max-depth 2
```

## Support

- **Issues**: [GitHub Issues](https://github.com/vedantparmar12/Document-Automation/issues)
- **Docs**: See README.md in the main project

## License

MIT License - see [LICENSE](../../../LICENSE)
