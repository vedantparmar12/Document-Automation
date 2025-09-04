#!/usr/bin/env python3
import asyncio
import argparse
import logging
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager
import os
import sys
from pathlib import Path

# Add the parent directory to Python path so imports work correctly
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.lowlevel.server import NotificationOptions
from mcp.types import TextContent, Tool, JSONRPCError, INTERNAL_ERROR
from pydantic import BaseModel, Field

# Add debug print
print(f"[DEBUG] Starting server from: {__file__}", file=sys.stderr)
print(f"[DEBUG] Python path: {sys.path}", file=sys.stderr)

try:
    from src.tools.consolidated_documentation_tools import ConsolidatedDocumentationTools
    from src.analyzers.codebase_analyzer import CodebaseAnalyzer
    from src.generators.documentation_generator import DocumentationGenerator
    print("[DEBUG] Successfully imported all modules", file=sys.stderr)
except Exception as e:
    print(f"[DEBUG] Import error: {e}", file=sys.stderr)
    # Create dummy classes to allow server to start
    class DocumentationTools:
        async def analyze_codebase(self, **kwargs):
            return [TextContent(text="analyze_codebase not implemented")]
        async def generate_documentation(self, **kwargs):
            return [TextContent(text="generate_documentation not implemented")]
        async def list_project_structure(self, **kwargs):
            return [TextContent(text="list_project_structure not implemented")]
        async def extract_api_endpoints(self, **kwargs):
            return [TextContent(text="extract_api_endpoints not implemented")]
        async def analyze_dependencies(self, **kwargs):
            return [TextContent(text="analyze_dependencies not implemented")]

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentAutomationServer:
    def __init__(self):
        logger.info("[DEBUG] Initializing DocumentAutomationServer")
        self.server = Server("document-automation-server")
        self.documentation_tools = ConsolidatedDocumentationTools()
        self.setup_handlers()
        logger.info("[DEBUG] Server initialization complete")

    def setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            logger.info("[DEBUG] handle_list_tools called")
            tools = [
                Tool(
                    name="analyze_codebase",
                    description="Complete codebase analysis with ALL features built-in: AST parsing, framework detection, database analysis, mermaid diagrams, pagination, security analysis, API endpoints, dependencies, and more. This single tool replaces multiple separate calls with intelligent built-in processing.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Local folder path or GitHub repository URL"
                            },
                            "source_type": {
                                "type": "string",
                                "enum": ["local", "github"],
                                "description": "Type of source to analyze"
                            },
                            "include_dependencies": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to analyze dependencies"
                            },
                            "include_ast_analysis": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to perform detailed AST parsing"
                            },
                            "include_framework_detection": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to detect frameworks and tech stack"
                            },
                            "include_database_analysis": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to analyze database schemas"
                            },
                            "include_mermaid_diagrams": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to generate mermaid diagrams"
                            },
                            "include_security_analysis": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to perform security analysis"
                            },
                            "include_api_endpoints": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to extract API endpoints"
                            },
                            "pagination_strategy": {
                                "type": "string",
                                "enum": ["auto", "file_by_file", "chunk_by_chunk", "smart"],
                                "default": "auto",
                                "description": "Pagination strategy for large repositories"
                            },
                            "max_files": {
                                "type": "integer",
                                "default": 1000,
                                "description": "Maximum number of files to analyze"
                            },
                            "max_tokens_per_chunk": {
                                "type": "integer",
                                "default": 4000,
                                "description": "Maximum tokens per response chunk"
                            },
                            "context_token": {
                                "type": "string",
                                "description": "Pagination context token for continuing large analysis"
                            }
                        },
                        "required": ["path", "source_type"]
                    }
                ),
                Tool(
                    name="generate_documentation",
                    description="Generate comprehensive professional documentation with ALL features built-in: multiple formats (HTML, PDF, Markdown, etc.), themes, interactive elements, search, navigation, code highlighting, multi-language support, auto-export, accessibility compliance, responsive design, and more. Single comprehensive tool for all documentation needs.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "analysis_id": {
                                "type": "string",
                                "description": "ID of the previously analyzed codebase"
                            },
                            "format": {
                                "type": "string",
                                "enum": ["markdown", "html", "rst", "pdf", "interactive", "confluence", "notion", "docx", "epub", "json"],
                                "default": "interactive",
                                "description": "Primary output format for documentation"
                            },
                            "theme": {
                                "type": "string",
                                "enum": ["default", "modern", "minimal", "dark", "corporate", "github", "material"],
                                "default": "modern",
                                "description": "Documentation theme"
                            },
                            "title": {
                                "type": "string",
                                "description": "Custom title for documentation"
                            },
                            "include_api_docs": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to include API documentation"
                            },
                            "include_examples": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to include code examples"
                            },
                            "include_architecture": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to include architecture diagrams"
                            },
                            "include_mermaid_diagrams": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to include mermaid diagrams"
                            },
                            "include_search": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to include search functionality"
                            },
                            "include_navigation": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to include navigation sidebar"
                            },
                            "include_toc": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to include table of contents"
                            },
                            "auto_export_formats": {
                                "type": "array",
                                "items": {"type": "string", "enum": ["html", "pdf", "docx", "markdown", "confluence", "notion", "json", "epub"]},
                                "description": "Additional formats to auto-export alongside primary format"
                            },
                            "custom_css": {
                                "type": "string",
                                "description": "Custom CSS to apply"
                            },
                            "accessibility_compliance": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to ensure accessibility compliance"
                            },
                            "multi_language_support": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to include multi-language support"
                            }
                        },
                        "required": ["analysis_id"]
                    }
                ),
                Tool(
                    name="export_documentation",
                    description="Export documentation to multiple formats with ALL advanced features built-in: quality optimization, accessibility compliance, multi-language support, custom branding, responsive design, search functionality, interactive diagrams, print-friendly styles, archive generation, batch processing, and more. Single comprehensive export tool for all needs.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "analysis_id": {
                                "type": "string",
                                "description": "ID of previously completed analysis"
                            },
                            "formats": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["html", "pdf", "docx", "markdown", "confluence", "notion", "json", "epub", "latex", "rtf", "odt"]
                                },
                                "default": ["html", "pdf"],
                                "description": "Export formats - can export multiple formats simultaneously"
                            },
                            "theme": {
                                "type": "string",
                                "enum": ["default", "modern", "minimal", "dark", "corporate", "github", "material", "bootstrap", "academic"],
                                "default": "modern",
                                "description": "Theme to use for all formats"
                            },
                            "title": {
                                "type": "string",
                                "description": "Custom title for documentation"
                            },
                            "include_toc": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to include table of contents"
                            },
                            "include_diagrams": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to include interactive diagrams"
                            },
                            "include_search": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to include search functionality"
                            },
                            "include_navigation": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to include navigation sidebar"
                            },
                            "accessibility_compliance": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to ensure WCAG 2.1 AA compliance"
                            },
                            "multi_language_support": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to include multi-language support"
                            },
                            "responsive_design": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to use responsive design"
                            },
                            "print_friendly": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to include print-friendly styles"
                            },
                            "custom_css": {
                                "type": "string",
                                "description": "Custom CSS to apply"
                            },
                            "custom_branding": {
                                "type": "object",
                                "properties": {
                                    "logo_url": {"type": "string"},
                                    "company_name": {"type": "string"},
                                    "primary_color": {"type": "string"},
                                    "secondary_color": {"type": "string"}
                                },
                                "description": "Custom branding options"
                            },
                            "output_directory": {
                                "type": "string",
                                "description": "Directory to save exported files"
                            },
                            "archive_formats": {
                                "type": "array",
                                "items": {"type": "string", "enum": ["zip", "tar", "tar.gz"]},
                                "description": "Create archives of exported documentation"
                            },
                            "quality_optimization": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to optimize images and compress output"
                            },
                            "include_metadata": {
                                "type": "boolean",
                                "default": True,
                                "description": "Whether to include document metadata"
                            }
                        },
                        "required": ["analysis_id"]
                    }
                )
            ]
            logger.info(f"[DEBUG] Returning {len(tools)} tools")
            print(f"[DEBUG] Returning {len(tools)} tools", file=sys.stderr)
            return tools

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"[DEBUG] handle_call_tool called with name: {name}")
            try:
                if name == "analyze_codebase":
                    return await self.documentation_tools.analyze_codebase(
                        path=arguments["path"],
                        source_type=arguments["source_type"],
                        include_dependencies=arguments.get("include_dependencies", True),
                        include_ast_analysis=arguments.get("include_ast_analysis", True),
                        include_framework_detection=arguments.get("include_framework_detection", True),
                        include_database_analysis=arguments.get("include_database_analysis", True),
                        include_mermaid_diagrams=arguments.get("include_mermaid_diagrams", True),
                        include_security_analysis=arguments.get("include_security_analysis", True),
                        include_api_endpoints=arguments.get("include_api_endpoints", True),
                        pagination_strategy=arguments.get("pagination_strategy", "auto"),
                        max_files=arguments.get("max_files", 1000),
                        max_tokens_per_chunk=arguments.get("max_tokens_per_chunk", 4000),
                        context_token=arguments.get("context_token")
                    )
                elif name == "generate_documentation":
                    return await self.documentation_tools.generate_documentation(
                        analysis_id=arguments["analysis_id"],
                        format=arguments.get("format", "interactive"),
                        theme=arguments.get("theme", "modern"),
                        title=arguments.get("title"),
                        include_api_docs=arguments.get("include_api_docs", True),
                        include_examples=arguments.get("include_examples", True),
                        include_architecture=arguments.get("include_architecture", True),
                        include_mermaid_diagrams=arguments.get("include_mermaid_diagrams", True),
                        include_search=arguments.get("include_search", True),
                        include_navigation=arguments.get("include_navigation", True),
                        include_toc=arguments.get("include_toc", True),
                        auto_export_formats=arguments.get("auto_export_formats", []),
                        custom_css=arguments.get("custom_css"),
                        accessibility_compliance=arguments.get("accessibility_compliance", True),
                        multi_language_support=arguments.get("multi_language_support", True)
                    )
                elif name == "export_documentation":
                    return await self.documentation_tools.export_documentation(
                        analysis_id=arguments["analysis_id"],
                        formats=arguments.get("formats", ["html", "pdf"]),
                        theme=arguments.get("theme", "modern"),
                        title=arguments.get("title"),
                        include_toc=arguments.get("include_toc", True),
                        include_diagrams=arguments.get("include_diagrams", True),
                        include_search=arguments.get("include_search", True),
                        include_navigation=arguments.get("include_navigation", True),
                        accessibility_compliance=arguments.get("accessibility_compliance", True),
                        multi_language_support=arguments.get("multi_language_support", True),
                        responsive_design=arguments.get("responsive_design", True),
                        print_friendly=arguments.get("print_friendly", True),
                        custom_css=arguments.get("custom_css"),
                        custom_branding=arguments.get("custom_branding"),
                        output_directory=arguments.get("output_directory"),
                        archive_formats=arguments.get("archive_formats"),
                        quality_optimization=arguments.get("quality_optimization", True),
                        include_metadata=arguments.get("include_metadata", True)
                    )
                else:
                    raise JSONRPCError(INTERNAL_ERROR, f"Unknown tool: {name}")

            except Exception as e:
                logger.error(f"Error in tool {name}: {str(e)}")
                raise JSONRPCError(INTERNAL_ERROR, f"Tool execution failed: {str(e)}")

    async def run(self):
        logger.info("[DEBUG] Starting server run")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="document-automation-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )

def main():
    print("[DEBUG] Main function started", file=sys.stderr)
    parser = argparse.ArgumentParser(description="Document Automation MCP Server")
    parser.add_argument("--log-level", default="DEBUG", help="Set the logging level")
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper()))

    server = DocumentAutomationServer()
    print("[DEBUG] About to run server", file=sys.stderr)
    asyncio.run(server.run())

if __name__ == "__main__":
    main()


















