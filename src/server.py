import asyncio
import argparse
import logging
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.lowlevel.server import NotificationOptions
from mcp.types import TextContent, Tool, JSONRPCError, INTERNAL_ERROR
from pydantic import BaseModel, Field

print(f"[DEBUG] Starting server from: {__file__}", file=sys.stderr)
print(f"[DEBUG] Python path: {sys.path}", file=sys.stderr)

try:
    from src.tools.documentation_tools import DocumentationTools
    from src.analyzers.codebase_analyzer import CodebaseAnalyzer
    from src.generators.documentation_generator import DocumentationGenerator
    print("[DEBUG] Successfully imported all modules", file=sys.stderr)
except Exception as e:
    print(f"[DEBUG] Import error: {e}", file=sys.stderr)
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
        self.documentation_tools = DocumentationTools()
        self.setup_handlers()
        logger.info("[DEBUG] Server initialization complete")

    def setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            logger.info("[DEBUG] handle_list_tools called")
            tools = [
                Tool(
                    name="analyze_codebase",
                    description="Analyze a codebase (local folder or GitHub repository) and extract its structure, dependencies, and key components.",
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
                            }
                        },
                        "required": ["path", "source_type"]
                    }
                ),
                Tool(
                    name="generate_documentation",
                    description="Generate comprehensive documentation from analyzed codebase structure.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "analysis_id": {
                                "type": "string",
                                "description": "ID of the previously analyzed codebase"
                            },
                            "format": {
                                "type": "string",
                                "enum": ["markdown", "html", "rst", "pdf"],
                                "default": "markdown",
                                "description": "Output format for documentation"
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
                            }
                        },
                        "required": ["analysis_id"]
                    }
                ),
                Tool(
                    name="list_project_structure",
                    description="Get a detailed project structure with file types and sizes.",
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
                            "max_depth": {
                                "type": "integer",
                                "default": 5,
                                "description": "Maximum depth to traverse"
                            }
                        },
                        "required": ["path", "source_type"]
                    }
                ),
                Tool(
                    name="extract_api_endpoints",
                    description="Extract and document API endpoints from web frameworks.",
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
                            "framework": {
                                "type": "string",
                                "enum": ["auto", "fastapi", "flask", "django", "express", "spring"],
                                "default": "auto",
                                "description": "Web framework to analyze"
                            }
                        },
                        "required": ["path", "source_type"]
                    }
                ),
                Tool(
                    name="analyze_dependencies",
                    description="Analyze project dependencies and generate dependency documentation.",
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
                            "include_dev_dependencies": {
                                "type": "boolean",
                                "default": False,
                                "description": "Whether to include development dependencies"
                            }
                        },
                        "required": ["path", "source_type"]
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
                        include_dependencies=arguments.get("include_dependencies", True)
                    )
                elif name == "generate_documentation":
                    return await self.documentation_tools.generate_documentation(
                        analysis_id=arguments["analysis_id"],
                        format=arguments.get("format", "markdown"),
                        include_api_docs=arguments.get("include_api_docs", True),
                        include_examples=arguments.get("include_examples", True),
                        include_architecture=arguments.get("include_architecture", True)
                    )
                elif name == "list_project_structure":
                    return await self.documentation_tools.list_project_structure(
                        path=arguments["path"],
                        source_type=arguments["source_type"],
                        max_depth=arguments.get("max_depth", 5)
                    )
                elif name == "extract_api_endpoints":
                    return await self.documentation_tools.extract_api_endpoints(
                        path=arguments["path"],
                        source_type=arguments["source_type"],
                        framework=arguments.get("framework", "auto")
                    )
                elif name == "analyze_dependencies":
                    return await self.documentation_tools.analyze_dependencies(
                        path=arguments["path"],
                        source_type=arguments["source_type"],
                        include_dev_dependencies=arguments.get("include_dev_dependencies", False)
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
