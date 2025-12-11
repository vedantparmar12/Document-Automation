#!/usr/bin/env python3
"""
Minimal MCP Server - No external dependencies beyond mcp library.
Used to test if MCP protocol works correctly.
"""
import sys
import os

# CRITICAL FIX FOR WINDOWS: Set binary mode on stdin/stdout IMMEDIATELY
# This prevents Windows from converting LF to CRLF which breaks MCP protocol
if sys.platform == "win32":
    import msvcrt
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

import asyncio
import logging

# Disable all output before anything else
logging.disable(logging.CRITICAL)

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.lowlevel.server import NotificationOptions
from mcp.types import TextContent, Tool

# Create simple server
server = Server("minimal-test-server")

@server.list_tools()
async def handle_list_tools():
    """Return a single test tool."""
    return [
        Tool(
            name="test_tool",
            description="A simple test tool that echoes input",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Message to echo"
                    }
                },
                "required": ["message"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    if name == "test_tool":
        return [TextContent(type="text", text=f"Echo: {arguments.get('message', 'No message')}")]
    return [TextContent(type="text", text=f"Unknown tool: {name}")]

@server.list_prompts()
async def handle_list_prompts():
    return []

@server.list_resources()
async def handle_list_resources():
    return []

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="minimal-test-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
