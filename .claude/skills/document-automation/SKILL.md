---
name: document-automation
description: Automatically analyze codebases and generate comprehensive, professional documentation. Use when analyzing projects, generating README files, creating API docs, or understanding codebase architecture. Works with GitHub repos and local directories.
allowed-tools:
  - Read
  - Bash(python:*)
  - Bash(pip:*)
  - Bash(git:*)
  - Bash(gh:*)
  - Grep
  - Glob
  - Write
  - Edit
  - WebFetch
user-invocable: true
---

# Document Automation Skill

Enables intelligent codebase analysis and professional documentation generation directly from Claude CLI. This skill analyzes project structure, extracts real features from code, and generates comprehensive documentation with architecture diagrams.

## Core Capabilities

1. **Codebase Analysis**: Deep analysis of project structure, dependencies, and patterns
2. **Documentation Generation**: Multi-format output (Markdown, HTML, PDF)
3. **Architecture Diagrams**: Generate Mermaid diagrams for workflows and components
4. **API Discovery**: Automatically find and document API endpoints
5. **Framework Detection**: Identify frameworks, libraries, and tech stack

## Prerequisites

Before using this skill, ensure:

```bash
# Python 3.8+ installed
python --version

# Clone the Document Automation repository
git clone https://github.com/vedantparmar12/Document-Automation.git

# Install dependencies
cd Document-Automation
pip install -r requirements.txt

# Set GitHub token for private repos (optional)
export GITHUB_TOKEN=ghp_your_token_here
```

## Quick Start

### 1. Analyzing a GitHub Repository

```bash
# Using the analyze script
python scripts/analyze-repo.py https://github.com/user/repo

# Or directly with the MCP server
python -c "
from src.analyzers.codebase_analyzer import CodebaseAnalyzer
analyzer = CodebaseAnalyzer()
result = analyzer.analyze('https://github.com/user/repo', source_type='github')
print(result)
"
```

I will automatically:
- Clone/fetch the repository
- Parse project structure and file hierarchy
- Detect frameworks and languages
- Extract dependencies and versions
- Identify API endpoints
- Map data flow and architecture

### 2. Analyzing a Local Directory

```bash
# Analyze local project
python scripts/analyze-repo.py /path/to/project --local

# Or using Python directly
python -c "
from src.analyzers.codebase_analyzer import CodebaseAnalyzer
analyzer = CodebaseAnalyzer()
result = analyzer.analyze('/path/to/project', source_type='local')
print(result)
"
```

### 3. Generating Documentation

```bash
# Generate Markdown documentation
python scripts/generate-docs.py /path/to/project --format markdown

# Generate HTML documentation
python scripts/generate-docs.py /path/to/project --format html --output docs/

# Generate PDF documentation
python scripts/generate-docs.py /path/to/project --format pdf --output output.pdf
```

### 4. Quick Analysis Commands

```bash
# List project structure
python -c "
from src.analyzers.codebase_analyzer import CodebaseAnalyzer
analyzer = CodebaseAnalyzer()
structure = analyzer.get_structure('/path/to/project')
for item in structure:
    print(item)
"

# Extract API endpoints
python -c "
from src.analyzers.framework_detector import FrameworkDetector
detector = FrameworkDetector()
endpoints = detector.extract_endpoints('/path/to/project')
for ep in endpoints:
    print(f'{ep.method} {ep.path}')
"
```

## Analysis Features

### Project Structure Analysis

I analyze:
- Directory hierarchy and organization
- File types and distribution
- Module dependencies
- Entry points and main files

### Framework Detection

Automatically detects:
- **Python**: Django, Flask, FastAPI, Pyramid
- **JavaScript**: React, Vue, Angular, Express, Next.js
- **TypeScript**: Nest.js, Deno
- **Others**: Spring Boot, Laravel, Rails

### Dependency Analysis

Parses and documents:
- `requirements.txt`, `pyproject.toml` (Python)
- `package.json` (Node.js)
- `Cargo.toml` (Rust)
- `go.mod` (Go)
- `pom.xml`, `build.gradle` (Java)

### Code Extraction

Extracts real code elements:
- Classes and their methods
- Functions and signatures
- API endpoints with parameters
- Database models and schemas
- Configuration options

## Documentation Output

### Generated Sections

1. **Project Overview**
   - Title with badges
   - Description and purpose
   - Key features list

2. **Architecture**
   - Component diagram (Mermaid)
   - Directory structure
   - Data flow diagram

3. **Installation**
   - Prerequisites
   - Step-by-step setup
   - Configuration options

4. **Usage**
   - Quick start examples
   - API reference
   - Code samples from project

5. **API Documentation**
   - Endpoints with methods
   - Request/response formats
   - Authentication requirements

6. **Development**
   - Project structure
   - Testing instructions
   - Contributing guidelines

### Output Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| Markdown | `.md` | GitHub-compatible documentation |
| HTML | `.html` | Styled web documentation |
| PDF | `.pdf` | Printable documentation |
| RST | `.rst` | Sphinx-compatible format |

## Working with Large Codebases

### Strategy 1: Incremental Analysis

```bash
# Analyze specific directories
python scripts/analyze-repo.py /project/src/api --local

# Then analyze another part
python scripts/analyze-repo.py /project/src/models --local
```

### Strategy 2: Filtered Analysis

```bash
# Only Python files
python scripts/analyze-repo.py /project --include "*.py"

# Exclude tests
python scripts/analyze-repo.py /project --exclude "**/test*"
```

### Strategy 3: Depth-Limited Analysis

```bash
# Limit directory depth
python scripts/analyze-repo.py /project --max-depth 3
```

## MCP Server Integration

### Starting the Server

```bash
# Start MCP server
python src/main.py

# Or with uvicorn
uvicorn src.server:app --host 0.0.0.0 --port 8000
```

### MCP Tools Available

1. **analyze_codebase**
   - Input: path, source_type, include_dependencies
   - Output: Full project analysis

2. **generate_documentation**
   - Input: analysis_id, format, include_api_docs
   - Output: Formatted documentation

3. **list_project_structure**
   - Input: path, source_type, max_depth
   - Output: File hierarchy

4. **extract_api_endpoints**
   - Input: path, source_type, framework
   - Output: API endpoint list

5. **analyze_dependencies**
   - Input: path, source_type, include_dev_dependencies
   - Output: Dependency analysis

### Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "document-automation": {
      "command": "python",
      "args": ["/path/to/Document-Automation/src/main.py"],
      "env": {
        "GITHUB_TOKEN": "your_token_here"
      }
    }
  }
}
```

### Cursor IDE Configuration

Add to MCP settings:

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

## Common Workflows

### Workflow 1: Quick Project Overview

```
User: "Analyze https://github.com/facebook/react"

Claude will:
1. Clone the repository
2. Analyze structure and dependencies
3. Detect React framework patterns
4. Generate summary with key findings
```

### Workflow 2: Generate Full Documentation

```
User: "Generate comprehensive documentation for my project at /home/user/myapp"

Claude will:
1. Perform deep analysis
2. Extract all code elements
3. Generate architecture diagrams
4. Create full documentation with all sections
```

### Workflow 3: API Documentation Only

```
User: "Document the API endpoints in my FastAPI project"

Claude will:
1. Detect FastAPI framework
2. Parse route decorators
3. Extract request/response schemas
4. Generate API reference documentation
```

### Workflow 4: Update Existing README

```
User: "Update the README for this project based on current code"

Claude will:
1. Read existing README
2. Analyze current codebase
3. Identify outdated sections
4. Generate updated content
```

## Best Practices

### 1. Provide Context

- Mention the project type (web app, CLI tool, library)
- Specify target audience (developers, end-users)
- Indicate desired documentation depth

### 2. Review Generated Content

- Verify code examples work
- Check links and references
- Add project-specific details

### 3. Iterate and Refine

- Generate initial documentation
- Request specific sections expanded
- Fine-tune formatting and structure

### 4. Keep Documentation Updated

- Re-run analysis after major changes
- Use version control for docs
- Link docs to code via line references

## Error Handling

### Common Issues

1. **Repository Not Found**
   ```bash
   # Verify URL is accessible
   gh repo view user/repo
   ```

2. **Permission Denied (Private Repo)**
   ```bash
   # Set GitHub token
   export GITHUB_TOKEN=ghp_your_token
   ```

3. **Large Repository Timeout**
   ```bash
   # Use shallow clone
   python scripts/analyze-repo.py repo_url --shallow
   ```

4. **Missing Dependencies**
   ```bash
   # Install requirements
   pip install -r requirements.txt
   ```

## Integration Examples

### With Git Hooks

```bash
# Add to .git/hooks/pre-commit
python scripts/generate-docs.py . --format markdown --output README.md
```

### With CI/CD

```yaml
# GitHub Actions
- name: Generate Documentation
  run: |
    python scripts/generate-docs.py . --format html --output docs/

- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./docs
```

### With Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: generate-docs
        name: Generate Documentation
        entry: python scripts/generate-docs.py
        language: system
        files: \.(py|js|ts)$
```

## Advanced Features

### Custom Templates

```python
from src.generators.professional_doc_generator import ProfessionalDocumentationGenerator

generator = ProfessionalDocumentationGenerator()
generator.set_template('custom_template.md')
result = generator.generate(analysis)
```

### Diagram Customization

```python
from src.diagrams.mermaid_generator import MermaidGenerator

generator = MermaidGenerator()
diagram = generator.generate_flowchart(
    analysis,
    theme='dark',
    direction='TB'
)
```

### Export Options

```python
# HTML with custom CSS
generator.generate(analysis, {
    'format': 'html',
    'css': 'custom.css',
    'include_toc': True
})

# PDF with custom styling
generator.generate(analysis, {
    'format': 'pdf',
    'page_size': 'A4',
    'margins': '1in'
})
```

## Summary

This skill enables you to:
- Analyze any codebase (local or GitHub)
- Generate professional, comprehensive documentation
- Create architecture diagrams automatically
- Document APIs with full detail
- Export to multiple formats (MD, HTML, PDF)
- Integrate with CI/CD and development workflows

Simply ask me to analyze a project or generate documentation, and I'll handle all the complexity of code analysis, extraction, and formatting.

## References

- [README.md](../../../README.md) - Full project documentation
- [QUICK_START.md](../../../QUICK_START.md) - Getting started guide
- [MCP Tools Reference](MCP-TOOLS.md) - Detailed tool documentation
- [Examples](EXAMPLES.md) - Real-world usage examples
