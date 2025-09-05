#!/usr/bin/env python3
"""
Server runner script that bypasses UV and runs directly.
This script ensures the MCP server runs with the correct Python environment.
"""
import os
import sys
import subprocess
from pathlib import Path

# Get the absolute path to this script's directory
script_dir = Path(__file__).parent.absolute()

# Set up the environment
env = os.environ.copy()
env['PYTHONPATH'] = str(script_dir)
env['PATH'] = '/home/vedan/.local/bin:' + env.get('PATH', '')

# Path to the actual server
server_script = script_dir / 'src' / 'server.py'

# Arguments to pass
args = [sys.executable, str(server_script)] + sys.argv[1:]

print(f"[DEBUG] Running: {' '.join(args)}", file=sys.stderr)
print(f"[DEBUG] PYTHONPATH: {env.get('PYTHONPATH')}", file=sys.stderr)
print(f"[DEBUG] Python executable: {sys.executable}", file=sys.stderr)

# Execute the server
try:
    os.execvpe(sys.executable, args, env)
except Exception as e:
    print(f"[ERROR] Failed to start server: {e}", file=sys.stderr)
    sys.exit(1)