#!/usr/bin/env python3
"""
MCP Server with Windows CRLF fix using io.open wrapper.
Based on documented fix for Antigravity MCP on Windows.
"""
import sys
import os
import io

# CRITICAL FIX FOR WINDOWS ANTIGRAVITY:
# Replace sys.stdout with a wrapper that forces LF-only line endings
# This prevents Windows from converting \n to \r\n
if sys.platform == "win32":
    # Set binary mode first
    import msvcrt
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    
    # Wrap stdout with io.open to control line endings
    sys.stdout = io.TextIOWrapper(
        sys.stdout.detach(),
        encoding='utf-8',
        newline='\n',  # Force LF only, never CRLF
        write_through=True  # No buffering
    )
    
    # Also wrap stdin
    sys.stdin = io.TextIOWrapper(
        sys.stdin.detach(),
        encoding='utf-8',
        newline='\n'
    )

from mcp.server.fastmcp import FastMCP

# Create server using FastMCP
mcp = FastMCP("document-automation")

@mcp.tool()
def test_echo(message: str) -> str:
    """A simple test tool that echoes the input message."""
    return f"Echo: {message}"

@mcp.tool()
def get_server_info() -> str:
    """Returns information about this MCP server."""
    return "Document Automation MCP Server v1.0"

if __name__ == "__main__":
    mcp.run()
