#!/bin/bash
# MCP Server Starter Script
# This script starts the Document Automation MCP server with proper environment

# Set up environment
export PYTHONPATH="/mnt/c/Users/vedan/Desktop/mcp-rag/Document Automation"
export PATH="/home/vedan/.local/bin:$PATH"
export PYTHONUNBUFFERED=1

# Change to project directory
cd "/mnt/c/Users/vedan/Desktop/mcp-rag/Document Automation"

# Debug info
echo "[DEBUG] Starting MCP Server..." >&2
echo "[DEBUG] Python version: $(python3 --version)" >&2
echo "[DEBUG] MCP location: $(python3 -c 'import mcp; print(mcp.__file__)' 2>/dev/null || echo 'MCP not found')" >&2
echo "[DEBUG] Working directory: $(pwd)" >&2

# Start the server
exec python3 src/server.py "$@"