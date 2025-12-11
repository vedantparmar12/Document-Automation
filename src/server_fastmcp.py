#!/usr/bin/env python3
"""
Clean MCP Server using FastMCP - the recommended high-level API.
No custom stdout manipulation, let the SDK handle everything.
"""
from mcp.server.fastmcp import FastMCP

# Create server using FastMCP (recommended approach)
mcp = FastMCP("document-automation")

@mcp.tool()
def test_echo(message: str) -> str:
    """A simple test tool that echoes the input message."""
    return f"Echo: {message}"

@mcp.tool()
def get_server_info() -> str:
    """Returns information about this MCP server."""
    return "Document Automation MCP Server v1.0 - Running on FastMCP"

if __name__ == "__main__":
    # Run with stdio transport (default for MCP)
    mcp.run()
