"""README Template Generator - Creates professional README files."""

import logging
from typing import Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)


class ReadmeTemplate:
    """Structured README template generator with Mermaid diagrams."""
    
    EXT_TO_LANG = {'.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript', '.java': 'Java', '.go': 'Go'}
    FOLDER_DESC = {
        'src': 'Source code', 'lib': 'Library code', 'tests': 'Test files', 'docs': 'Documentation',
        'config': 'Configuration', 'api': 'API routes', 'models': 'Data models', 'services': 'Business services',
        'components': 'UI components', 'analyzers': 'Analysis modules', 'generators': 'Generation modules',
        'security': 'Security modules', 'tools': 'Tool implementations', 'utils': 'Utility functions'
    }
    
    def __init__(self, project_name: str, project_type: str = "Application"):
        self.project_name = project_name
        self.project_type = project_type
        self.sections: List[str] = []
    
    def generate(self, analysis_data: Dict[str, Any]) -> str:
        """Generate complete README from analysis data."""
        self.sections = []
        self._add_header(analysis_data)
        self._add_badges(analysis_data)
        self._add_overview(analysis_data)
        self._add_toc()
        self._add_features(analysis_data)
        self._add_architecture(analysis_data)
        self._add_project_structure(analysis_data)
        self._add_flow(analysis_data)
        self._add_getting_started(analysis_data)
        self._add_usage(analysis_data)
        self._add_api_reference(analysis_data)
        self._add_config()
        self._add_contributing()
        self._add_license()
        return "\n\n".join(self.sections)
    
    def _add_header(self, data: Dict[str, Any]) -> None:
        desc = data.get('classification', {}).get('description') or f"A {self.project_type.lower()}"
        self.sections.append(f"# {self.project_name}\n\n> {desc}")
    
    def _add_badges(self, data: Dict[str, Any]) -> None:
        lang = self._detect_language(data)
        badges = ["![Version](https://img.shields.io/badge/version-1.0.0-blue)"]
        if lang == "Python":
            badges.append("![Python](https://img.shields.io/badge/python-3.8+-green)")
        elif lang in ("JavaScript", "TypeScript"):
            badges.append(f"![{lang}](https://img.shields.io/badge/{lang.lower()}-blue)")
        if "mcp" in self.project_type.lower():
            badges.append("![MCP](https://img.shields.io/badge/MCP-Server-purple)")
        badges.append("![License](https://img.shields.io/badge/license-MIT-yellow)")
        self.sections.append(" ".join(badges))
    
    def _add_overview(self, data: Dict[str, Any]) -> None:
        features = self._extract_features(data)[:5]
        items = '\n'.join(f"- **{f['name']}**: {f['description']}" for f in features)
        self.sections.append(f"## Overview\n\n{self.project_name} provides:\n\n{items}")
    
    def _add_toc(self) -> None:
        self.sections.append("""## Table of Contents
- [Overview](#overview) | [Features](#features) | [Architecture](#architecture)
- [Project Structure](#project-structure) | [Getting Started](#getting-started)
- [Usage](#usage) | [API Reference](#api-reference) | [Contributing](#contributing)""")
    
    def _add_features(self, data: Dict[str, Any]) -> None:
        features = self._extract_features(data)
        items = '\n'.join(f"- ✅ **{f['name']}** - {f['description']}" for f in features)
        self.sections.append(f"## Features\n\n{items}")
    
    def _add_architecture(self, data: Dict[str, Any]) -> None:
        comps = self._detect_components(data)
        diagram = f'```mermaid\nflowchart TB\n    subgraph "{self.project_name}"\n'
        if comps['api']:
            diagram += '        API[API Layer]\n'
        diagram += '        Core[Core Logic]\n'
        if comps['db']:
            diagram += '        DB[(Database)]\n'
        diagram += '    end\n    User([User]) --> Core\n'
        if comps['api']:
            diagram += '    Core --> API\n'
        if comps['db']:
            diagram += '    Core --> DB\n'
        diagram += '```'
        self.sections.append(f"## Architecture\n\n{diagram}")
    
    def _add_project_structure(self, data: Dict[str, Any]) -> None:
        folders = self._get_main_folders(data)
        tree = '\n'.join(f"├── {f}/" for f in sorted(folders))
        if tree:
            tree = tree[:-1].replace('├──', '└──', 1)  # Last item
        desc = '\n'.join(f"- **`{f}/`** - {self.FOLDER_DESC.get(f.lower(), f.title() + ' module')}" 
                         for f in sorted(folders))
        self.sections.append(f"## Project Structure\n\n```\n{self.project_name}/\n{tree}\n```\n\n{desc}")
    
    def _add_flow(self, data: Dict[str, Any]) -> None:
        flow_type = "mcp" if data.get('mcp_server_info') else "api" if data.get('api_endpoints') else "basic"
        diagrams = {
            "mcp": "User->>App: Command\nApp->>MCP: Request\nMCP-->>App: Response\nApp-->>User: Result",
            "api": "User->>API: Request\nAPI->>DB: Query\nDB-->>API: Data\nAPI-->>User: Response",
            "basic": "User->>App: Input\nApp->>Core: Process\nCore-->>App: Result\nApp-->>User: Output"
        }
        self.sections.append(f"## How It Works\n\n```mermaid\nsequenceDiagram\n{diagrams[flow_type]}\n```")
    
    def _add_getting_started(self, data: Dict[str, Any]) -> None:
        lang = self._detect_language(data)
        slug = self.project_name.lower().replace(' ', '-')
        if lang == "Python":
            content = f"""## Getting Started

### Prerequisites
- Python 3.8+, pip, Git

### Installation
```bash
git clone <repository-url> && cd {slug}
python -m venv venv && source venv/bin/activate  # or venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env  # Configure your variables
```"""
        else:
            content = f"""## Getting Started

### Prerequisites
- Node.js 16+, npm/yarn, Git

### Installation
```bash
git clone <repository-url> && cd {slug}
npm install
cp .env.example .env
```"""
        self.sections.append(content)
    
    def _add_usage(self, data: Dict[str, Any]) -> None:
        lang = self._detect_language(data)
        cmd = "python main.py" if lang == "Python" else "npm start"
        self.sections.append(f"## Usage\n\n```bash\n{cmd}\n```\n\n| Command | Description |\n|---------|-------------|\n| start | Start app |\n| test | Run tests |")
    
    def _add_api_reference(self, data: Dict[str, Any]) -> None:
        endpoints = data.get('api_endpoints', [])[:10]
        if not endpoints:
            return
        rows = '\n'.join(f"| `{e.get('methods', 'GET')}` | `{e.get('path', '/')}` |"
                         for e in endpoints)
        self.sections.append(f"## API Reference\n\n| Method | Endpoint |\n|--------|----------|\n{rows}")
    
    def _add_config(self) -> None:
        self.sections.append("""## Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `APP_ENV` | Environment | Yes |
| `LOG_LEVEL` | Log level | No |

> ⚠️ Never commit `.env` to version control.""")
    
    def _add_contributing(self) -> None:
        self.sections.append("## Contributing\n\n1. Fork → 2. Branch → 3. Commit → 4. Push → 5. PR")
    
    def _add_license(self) -> None:
        self.sections.append("## License\n\nMIT License - see [LICENSE](LICENSE)")
    
    # Helper methods
    def _detect_language(self, data: Dict[str, Any]) -> str:
        files = data.get('project_structure', {}).get('files', [])
        counts = {}
        for f in files:
            path = f.get('path', f) if isinstance(f, dict) else f
            ext = Path(path).suffix.lower()
            if ext in self.EXT_TO_LANG:
                lang = self.EXT_TO_LANG[ext]
                counts[lang] = counts.get(lang, 0) + 1
        return max(counts, key=counts.get) if counts else "Python"
    
    def _extract_features(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        features = []
        for f in data.get('classification', {}).get('features', []):
            features.append(f if isinstance(f, dict) else {'name': f, 'description': ''})
        if data.get('api_endpoints'):
            features.append({'name': 'REST API', 'description': 'API access'})
        if data.get('mcp_server_info'):
            features.append({'name': 'MCP Support', 'description': 'MCP integration'})
        return features or [{'name': 'Core', 'description': 'Main features'}]
    
    def _detect_components(self, data: Dict[str, Any]) -> Dict[str, bool]:
        files = data.get('project_structure', {}).get('files', [])
        paths = ' '.join(f.get('path', f) if isinstance(f, dict) else f for f in files).lower()
        return {
            'api': any(x in paths for x in ['api/', 'routes/', 'server.py']) or bool(data.get('api_endpoints')),
            'db': any(x in paths for x in ['models/', 'database/', '.sql']) or bool(data.get('database_schemas'))
        }
    
    def _get_main_folders(self, data: Dict[str, Any]) -> set:
        files = data.get('project_structure', {}).get('files', [])
        folders = set()
        for f in files:
            path = f.get('path', f) if isinstance(f, dict) else f
            parts = Path(path).parts
            if len(parts) > 1 and not parts[0].startswith(('.', '__')):
                folders.add(parts[0])
        return folders


def generate_readme(project_name: str, analysis_data: Dict[str, Any], project_type: str = "Application") -> str:
    """Factory function to generate README."""
    return ReadmeTemplate(project_name, project_type).generate(analysis_data)
