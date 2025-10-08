"""
MCP Documentation Generator

Specialized generator for Model Context Protocol (MCP) server documentation.
Creates detailed documentation with tool references, client configs, and examples.
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class MCPDocumentationGenerator:
    """Generator for MCP server documentation."""
    
    def __init__(self):
        pass
    
    def generate(
        self,
        mcp_info: Dict[str, Any],
        project_name: str,
        project_root: str
    ) -> str:
        """
        Generate comprehensive MCP server documentation.
        
        Args:
            mcp_info: MCPServerInfo.to_dict() output
            project_name: Project name
            project_root: Project root path
            
        Returns:
            Markdown documentation string
        """
        sections = []
        
        # Title and Overview
        sections.append(self._generate_title(project_name, mcp_info))
        
        # Table of Contents
        sections.append(self._generate_toc(mcp_info))
        
        # Overview
        sections.append(self._generate_overview(project_name, mcp_info))
        
        # Available Tools
        if mcp_info.get('tools'):
            sections.append(self._generate_tools_section(mcp_info['tools']))
        
        # Setup & Configuration
        sections.append(self._generate_setup_section(project_name, mcp_info, project_root))
        
        # Client Configuration
        sections.append(self._generate_client_config_section(mcp_info))
        
        # Usage Examples
        if mcp_info.get('tools'):
            sections.append(self._generate_usage_examples(mcp_info['tools']))
        
        # Integrations
        if mcp_info.get('integrations'):
            sections.append(self._generate_integrations_section(mcp_info['integrations']))
        
        # Environment Variables
        if mcp_info.get('env_variables'):
            sections.append(self._generate_env_section(mcp_info['env_variables']))
        
        return '\n\n'.join(sections)
    
    def _generate_title(self, project_name: str, mcp_info: Dict[str, Any]) -> str:
        """Generate title section."""
        server_name = mcp_info.get('server_name', project_name)
        
        return f"""# {server_name} - MCP Server Documentation

![MCP](https://img.shields.io/badge/MCP-Server-blue)
![Transport](https://img.shields.io/badge/Transport-{mcp_info.get('transport', 'stdio')}-green)
![Tools](https://img.shields.io/badge/Tools-{len(mcp_info.get('tools', []))}-orange)

> Model Context Protocol (MCP) server providing AI assistants with structured tools and resources."""
    
    def _generate_toc(self, mcp_info: Dict[str, Any]) -> str:
        """Generate table of contents."""
        toc_items = [
            "- [Overview](#overview)",
            "- [Available Tools](#available-tools)",
            "- [Setup & Installation](#setup--installation)",
            "- [Client Configuration](#client-configuration)",
            "  - [Claude Desktop](#claude-desktop)",
            "  - [Cursor IDE](#cursor-ide)",
            "- [Usage Examples](#usage-examples)",
        ]
        
        if mcp_info.get('integrations'):
            toc_items.append("- [External Integrations](#external-integrations)")
        
        if mcp_info.get('env_variables'):
            toc_items.append("- [Environment Variables](#environment-variables)")
        
        toc_items.extend([
            "- [Troubleshooting](#troubleshooting)",
            "- [Contributing](#contributing)"
        ])
        
        return "## 📋 Table of Contents\n\n" + '\n'.join(toc_items)
    
    def _generate_overview(self, project_name: str, mcp_info: Dict[str, Any]) -> str:
        """Generate overview section."""
        tools_count = len(mcp_info.get('tools', []))
        transport = mcp_info.get('transport', 'stdio')
        
        return f"""## 🎯 Overview

This MCP server exposes **{tools_count} tools** that AI assistants can use to interact with your services.

### What is MCP?

The Model Context Protocol (MCP) is an open protocol that enables seamless integration between LLM applications and external data sources and tools. This server implements MCP to provide AI assistants like Claude with structured access to specific functionality.

### Key Features

- 🛠️ **{tools_count} Available Tools**: Rich set of tools for AI assistant interactions
- 🔄 **{transport.upper()} Transport**: Uses {transport} for communication
- 🔌 **Easy Integration**: Works with Claude Desktop, Cursor, and other MCP clients
- 📡 **Structured Data**: Type-safe tool schemas and validation
- 🚀 **Production Ready**: Built with error handling and logging"""
    
    def _generate_tools_section(self, tools: List[Dict[str, Any]]) -> str:
        """Generate tools documentation."""
        section = "## 🛠️ Available Tools\n\n"
        
        for i, tool in enumerate(tools, 1):
            section += self._format_tool(tool, i)
            section += "\n\n"
        
        return section
    
    def _format_tool(self, tool: Dict[str, Any], index: int) -> str:
        """Format a single tool's documentation."""
        name = tool.get('name', 'unknown')
        description = tool.get('description', 'No description available')
        schema = tool.get('input_schema', {})
        required_params = tool.get('required_params', [])
        optional_params = tool.get('optional_params', [])
        
        doc = f"### {index}. `{name}`\n\n"
        doc += f"{description}\n\n"
        
        # Parameters section
        if required_params or optional_params:
            doc += "**Parameters:**\n\n"
            
            properties = schema.get('properties', {})
            
            # Required parameters
            if required_params:
                doc += "Required:\n"
                for param in required_params:
                    param_info = properties.get(param, {})
                    param_type = param_info.get('type', 'any')
                    param_desc = param_info.get('description', '')
                    doc += f"- `{param}` ({param_type}): {param_desc}\n"
                doc += "\n"
            
            # Optional parameters
            if optional_params:
                doc += "Optional:\n"
                for param in optional_params:
                    param_info = properties.get(param, {})
                    param_type = param_info.get('type', 'any')
                    param_desc = param_info.get('description', '')
                    default = param_info.get('default', '')
                    default_str = f" (default: {default})" if default else ""
                    doc += f"- `{param}` ({param_type}): {param_desc}{default_str}\n"
                doc += "\n"
        
        # Example JSON
        doc += "**Example Request:**\n\n"
        doc += "```json\n"
        doc += "{\n"
        doc += f'  "tool": "{name}",\n'
        doc += '  "arguments": {\n'
        
        # Generate example arguments
        example_args = []
        properties = schema.get('properties', {})
        for param in required_params[:2]:  # Show first 2 required params
            param_info = properties.get(param, {})
            param_type = param_info.get('type', 'string')
            if param_type == 'string':
                example_args.append(f'    "{param}": "example_value"')
            elif param_type == 'number' or param_type == 'integer':
                example_args.append(f'    "{param}": 123')
            elif param_type == 'boolean':
                example_args.append(f'    "{param}": true')
        
        doc += ',\n'.join(example_args)
        doc += "\n  }\n"
        doc += "}\n"
        doc += "```\n"
        
        return doc
    
    def _generate_setup_section(
        self,
        project_name: str,
        mcp_info: Dict[str, Any],
        project_root: str
    ) -> str:
        """Generate setup and installation section."""
        return f"""## 🚀 Setup & Installation

### Prerequisites

- Python 3.8 or higher
- pip or uv package manager
- Git

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd {Path(project_root).name}
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\\Scripts\\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   
   Create a `.env` file in the project root:
   ```env
   # Add your API keys and configuration
   API_KEY=your_api_key_here
   ```

5. **Test the server:**
   ```bash
   python server.py
   ```

You should see: `MCP Server running on {mcp_info.get('transport', 'stdio')} transport`"""
    
    def _generate_client_config_section(self, mcp_info: Dict[str, Any]) -> str:
        """Generate client configuration section."""
        configs = mcp_info.get('client_configs', {})
        
        section = "## ⚙️ Client Configuration\n\n"
        section += "Configure your MCP client to connect to this server.\n\n"
        
        # Claude Desktop
        section += "### Claude Desktop\n\n"
        section += "Add to your Claude Desktop configuration file:\n\n"
        section += "**Location:**\n"
        section += "- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`\n"
        section += "- Windows: `%APPDATA%\\Claude\\claude_desktop_config.json`\n\n"
        section += "**Configuration:**\n\n"
        section += "```json\n"
        section += configs.get('claude_desktop', '{  }')
        section += "\n```\n\n"
        
        # Cursor
        section += "### Cursor IDE\n\n"
        section += "Add to your Cursor MCP settings:\n\n"
        section += "```json\n"
        section += configs.get('cursor', '{  }')
        section += "\n```\n\n"
        
        # Generic MCP Client
        section += "### Other MCP Clients\n\n"
        section += "For other MCP clients, use these connection details:\n\n"
        section += f"- **Transport**: {mcp_info.get('transport', 'stdio')}\n"
        section += "- **Command**: `python server.py`\n"
        section += "- **Working Directory**: Project root\n\n"
        
        return section
    
    def _generate_usage_examples(self, tools: List[Dict[str, Any]]) -> str:
        """Generate usage examples section."""
        section = "## 💡 Usage Examples\n\n"
        section += "Here are some examples of how to use the tools with an MCP client:\n\n"
        
        # Show examples for first 3 tools
        for tool in tools[:3]:
            name = tool.get('name', 'unknown')
            description = tool.get('description', '')
            
            section += f"### Example: {name}\n\n"
            section += f"**Scenario:** {description}\n\n"
            section += "**Voice/Text Command:**\n"
            section += f'```\n"Use {name} to [describe task]"\n```\n\n'
            section += "**What Happens:**\n"
            section += "1. Claude receives your request\n"
            section += f"2. Claude calls the `{name}` tool with appropriate parameters\n"
            section += "3. The MCP server processes the request\n"
            section += "4. Results are returned to Claude\n"
            section += "5. Claude presents the information to you\n\n"
        
        return section
    
    def _generate_integrations_section(self, integrations: List[str]) -> str:
        """Generate external integrations section."""
        section = "## 🔌 External Integrations\n\n"
        section += "This MCP server integrates with the following external services:\n\n"
        
        for integration in integrations:
            section += f"### {integration}\n\n"
            
            # Add specific info for known services
            if integration == 'RapidAPI':
                section += "This server uses RapidAPI for external API access.\n\n"
                section += "**Setup:**\n"
                section += "1. Sign up at [RapidAPI](https://rapidapi.com)\n"
                section += "2. Subscribe to the required API\n"
                section += "3. Add your API key to `.env`:\n"
                section += "   ```\n   RAPIDAPI_KEY=your_key_here\n   ```\n\n"
            elif integration == 'OpenAI':
                section += "Uses OpenAI's API for language model capabilities.\n\n"
                section += "**Setup:**\n"
                section += "1. Get API key from [OpenAI](https://platform.openai.com/api-keys)\n"
                section += "2. Add to `.env`:\n"
                section += "   ```\n   OPENAI_API_KEY=your_key_here\n   ```\n\n"
            else:
                section += f"Requires {integration} API credentials.\n\n"
        
        return section
    
    def _generate_env_section(self, env_vars: List[Dict[str, str]]) -> str:
        """Generate environment variables section."""
        section = "## 🔐 Environment Variables\n\n"
        section += "Required and optional environment variables:\n\n"
        section += "| Variable | Required | Description |\n"
        section += "|----------|----------|-------------|\n"
        
        for var in env_vars:
            name = var.get('name', '')
            required = '✅ Yes' if var.get('required') else '⚠️ Optional'
            description = var.get('description', 'No description')
            section += f"| `{name}` | {required} | {description} |\n"
        
        section += "\n"
        return section


def generate_mcp_documentation(
    mcp_info: Dict[str, Any],
    project_name: str,
    project_root: str
) -> str:
    """
    Convenience function to generate MCP documentation.
    
    Args:
        mcp_info: MCPServerInfo dictionary
        project_name: Name of the project
        project_root: Root path of the project
        
    Returns:
        Complete markdown documentation
    """
    generator = MCPDocumentationGenerator()
    return generator.generate(mcp_info, project_name, project_root)
