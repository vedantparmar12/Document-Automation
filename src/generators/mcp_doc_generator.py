"""MCP Documentation Generator - Creates documentation for MCP servers."""

import logging
from typing import Dict, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class MCPDocumentationGenerator:
    """Generator for MCP server documentation with architecture and flow diagrams."""
    
    def generate(self, mcp_info: Dict[str, Any], project_name: str, project_root: str) -> str:
        """Generate comprehensive MCP server documentation."""
        tools = mcp_info.get('tools', [])
        sections = [
            self._generate_title(project_name, mcp_info),
            self._generate_toc(mcp_info),
            self._generate_overview(project_name, mcp_info),
            self._generate_architecture_diagram(project_name, len(tools)),
            self._generate_flow_diagram(),
        ]
        
        if tools:
            sections.append(self._generate_tools_section(tools))
        
        sections.extend([
            self._generate_setup_section(project_name, mcp_info, project_root),
            self._generate_client_config_section(mcp_info),
        ])
        
        if tools:
            sections.append(self._generate_usage_examples(tools))
        if mcp_info.get('integrations'):
            sections.append(self._generate_integrations_section(mcp_info['integrations']))
        if mcp_info.get('env_variables'):
            sections.append(self._generate_env_section(mcp_info['env_variables']))
        
        sections.extend([self._generate_troubleshooting(), self._generate_contributing()])
        return '\n\n'.join(sections)
    
    def _generate_title(self, project_name: str, mcp_info: Dict[str, Any]) -> str:
        name = mcp_info.get('server_name', project_name)
        transport = mcp_info.get('transport', 'stdio')
        tools_count = len(mcp_info.get('tools', []))
        return f"""# {name} - MCP Server Documentation

![MCP](https://img.shields.io/badge/MCP-Server-blue)
![Transport](https://img.shields.io/badge/Transport-{transport}-green)
![Tools](https://img.shields.io/badge/Tools-{tools_count}-orange)

> Model Context Protocol (MCP) server providing AI assistants with structured tools."""
    
    def _generate_toc(self, mcp_info: Dict[str, Any]) -> str:
        items = [
            "- [Overview](#overview)", "- [Architecture](#architecture)",
            "- [How It Works](#how-it-works)", "- [Available Tools](#available-tools)",
            "- [Setup & Installation](#setup--installation)",
            "- [Client Configuration](#client-configuration)",
            "- [Usage Examples](#usage-examples)"
        ]
        if mcp_info.get('integrations'):
            items.append("- [External Integrations](#external-integrations)")
        if mcp_info.get('env_variables'):
            items.append("- [Environment Variables](#environment-variables)")
        items.extend(["- [Troubleshooting](#troubleshooting)", "- [Contributing](#contributing)"])
        return "## 📋 Table of Contents\n\n" + '\n'.join(items)
    
    def _generate_overview(self, project_name: str, mcp_info: Dict[str, Any]) -> str:
        tools_count = len(mcp_info.get('tools', []))
        transport = mcp_info.get('transport', 'stdio').upper()
        return f"""## 🎯 Overview

This MCP server exposes **{tools_count} tools** for AI assistant interactions.

### Key Features
- 🛠️ **{tools_count} Tools**: Rich toolset for AI interactions
- 🔄 **{transport} Transport**: Communication protocol
- 🔌 **Easy Integration**: Works with Claude Desktop, Cursor, other MCP clients
-  **Production Ready**: Built with error handling and logging"""
    
    def _generate_tools_section(self, tools: List[Dict[str, Any]]) -> str:
        section = "## 🛠️ Available Tools\n\n"
        for i, tool in enumerate(tools, 1):
            section += self._format_tool(tool, i) + "\n\n"
        return section
    
    def _format_tool(self, tool: Dict[str, Any], index: int) -> str:
        name, desc = tool.get('name', 'unknown'), tool.get('description', 'No description')
        schema = tool.get('input_schema', {})
        required = tool.get('required_params', [])
        optional = tool.get('optional_params', [])
        props = schema.get('properties', {})
        
        doc = f"### {index}. `{name}`\n\n{desc}\n\n"
        
        if required or optional:
            doc += "**Parameters:**\n\n"
            if required:
                doc += "Required:\n" + ''.join(
                    f"- `{p}` ({props.get(p, {}).get('type', 'any')}): {props.get(p, {}).get('description', '')}\n"
                    for p in required) + "\n"
            if optional:
                doc += "Optional:\n" + ''.join(
                    f"- `{p}` ({props.get(p, {}).get('type', 'any')}): {props.get(p, {}).get('description', '')}\n"
                    for p in optional) + "\n"
        
        # Example JSON
        type_examples = {'string': '"example"', 'number': '123', 'integer': '123', 'boolean': 'true'}
        args = [f'    "{p}": {type_examples.get(props.get(p, {}).get("type", "string"), "\"value\"")}'
                for p in required[:2]]
        doc += f'**Example:**\n\n```json\n{{\n  "tool": "{name}",\n  "arguments": {{\n{chr(44).join(args)}\n  }}\n}}\n```\n'
        return doc
    
    def _generate_setup_section(self, project_name: str, mcp_info: Dict[str, Any], project_root: str) -> str:
        folder = Path(project_root).name
        transport = mcp_info.get('transport', 'stdio')
        return f"""## 🚀 Setup & Installation

### Prerequisites
- Python 3.8+, pip/uv, Git

### Installation
```bash
git clone <repository-url>
cd {folder}
python -m venv venv && source venv/bin/activate  # or venv\\Scripts\\activate on Windows
pip install -r requirements.txt
```

### Test Server
```bash
python server.py
```
Expected: `MCP Server running on {transport} transport`"""
    
    def _generate_client_config_section(self, mcp_info: Dict[str, Any]) -> str:
        configs = mcp_info.get('client_configs', {})
        return f"""## ⚙️ Client Configuration

### Claude Desktop
Add to `claude_desktop_config.json`:
```json
{configs.get('claude_desktop', '{ }')}
```

### Cursor IDE
```json
{configs.get('cursor', '{ }')}
```

### Connection Details
- **Transport**: {mcp_info.get('transport', 'stdio')}
- **Command**: `python server.py`"""
    
    def _generate_usage_examples(self, tools: List[Dict[str, Any]]) -> str:
        section = "## 💡 Usage Examples\n\n"
        for tool in tools[:3]:
            name, desc = tool.get('name', ''), tool.get('description', '')
            section += f'### {name}\n**Scenario:** {desc}\n```\n"Use {name} to [task]"\n```\n\n'
        return section
    
    def _generate_integrations_section(self, integrations: List[str]) -> str:
        section = "## 🔌 External Integrations\n\n"
        for integration in integrations:
            section += f"### {integration}\nRequires {integration} API credentials.\n\n"
        return section
    
    def _generate_env_section(self, env_vars: List[Dict[str, str]]) -> str:
        rows = '\n'.join(
            f"| `{v.get('name', '')}` | {'✅' if v.get('required') else '⚠️'} | {v.get('description', '')} |"
            for v in env_vars)
        return f"""## 🔐 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
{rows}

> ⚠️ Never commit `.env` to version control."""
    
    def _generate_architecture_diagram(self, project_name: str, tools_count: int) -> str:
        return f"""## 🏗️ Architecture

```mermaid
flowchart TB
    subgraph Clients["🖥️ MCP Clients"]
        Claude[Claude Desktop]
        Cursor[Cursor IDE]
    end
    subgraph Server["{project_name}"]
        MCP[Protocol Handler]
        Tools[Tool Registry - {tools_count} tools]
        Core[Core Logic]
    end
    subgraph External["🌐 External"]
        APIs[APIs]
        Data[(Data)]
    end
    Claude --> MCP
    Cursor --> MCP
    MCP --> Tools --> Core --> APIs
    Core --> Data
```

| Component | Description |
|-----------|-------------|
| **Protocol Handler** | MCP communication |
| **Tool Registry** | Available tools |
| **Core Logic** | Business logic |"""
    
    def _generate_flow_diagram(self) -> str:
        return """## 🔄 How It Works

```mermaid
sequenceDiagram
    User->>AI: Request
    AI->>MCP: Call tool
    MCP->>Tool: Execute
    Tool-->>MCP: Result
    MCP-->>AI: Response
    AI-->>User: Answer
```

1. User makes request → 2. AI selects tool → 3. MCP executes → 4. Result returned"""
    
    def _generate_troubleshooting(self) -> str:
        return """## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Server not starting | Check dependencies, activate venv |
| Connection failed | Verify path in client config |
| Tool not found | Ensure tool registered, restart server |

Debug: `python server.py --log-level DEBUG`"""
    
    def _generate_contributing(self) -> str:
        return """## 🤝 Contributing

1. Fork → 2. Clone → 3. Branch → 4. Changes → 5. PR

## 📄 License
MIT License"""


def generate_mcp_documentation(mcp_info: Dict[str, Any], project_name: str, project_root: str) -> str:
    """Factory function to generate MCP documentation."""
    return MCPDocumentationGenerator().generate(mcp_info, project_name, project_root)
