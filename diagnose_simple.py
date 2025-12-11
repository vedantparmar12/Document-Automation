#!/usr/bin/env python3
"""
Simple diagnostic: Run the minimal server and send an initialize request.
Capture the raw bytes to a file for inspection.
"""
import subprocess
import sys
import os
import json
import time

PYTHON_EXE = r"C:\Users\vedan\Desktop\mcp-rag\Document Automation\.venv\Scripts\python.exe"
SERVER_SCRIPT = r"C:\Users\vedan\Desktop\mcp-rag\Document Automation\src\server_minimal.py"
OUTPUT_FILE = r"C:\Users\vedan\Desktop\mcp-rag\Document Automation\raw_output.bin"

# MCP Initialize Request with Content-Length header (LSP-style)
init_request = {
    "jsonrpc": "2.0",
    "method": "initialize",
    "id": 1,
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "diagnosis", "version": "1.0"}
    }
}

json_body = json.dumps(init_request)
# MCP uses Content-Length headers like LSP
message = f"Content-Length: {len(json_body)}\r\n\r\n{json_body}"

print(f"Starting server: {SERVER_SCRIPT}")
print(f"Sending message ({len(message)} bytes):\n{message[:200]}...")

# Run with PYTHONUNBUFFERED
env = os.environ.copy()
env["PYTHONUNBUFFERED"] = "1"

process = subprocess.Popen(
    [PYTHON_EXE, SERVER_SCRIPT],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env=env
)

# Send the message
process.stdin.write(message.encode('utf-8'))
process.stdin.flush()

print("Message sent. Waiting for response...")
time.sleep(3)

# Read whatever is available
stdout_data = b""
stderr_data = b""

try:
    # Non-blocking read
    import select
    if sys.platform == "win32":
        # Windows doesn't support select on pipes, so we use poll
        if process.poll() is not None:
            stdout_data = process.stdout.read()
            stderr_data = process.stderr.read()
        else:
            # Process still running, try to read some data
            import threading
            def read_stdout():
                global stdout_data
                stdout_data = process.stdout.read(4096)
            
            t = threading.Thread(target=read_stdout)
            t.daemon = True
            t.start()
            t.join(timeout=2)
            
            stderr_data = process.stderr.read()
except Exception as e:
    print(f"Error reading: {e}")

# Write raw output to file
with open(OUTPUT_FILE, "wb") as f:
    f.write(stdout_data)

print(f"\n--- STDOUT ({len(stdout_data)} bytes) ---")
print(f"Hex: {stdout_data[:200].hex()}")
print(f"Text: {stdout_data[:500].decode('utf-8', errors='replace')}")

print(f"\n--- STDERR ({len(stderr_data)} bytes) ---")
print(stderr_data.decode('utf-8', errors='replace')[:1000])

print(f"\nRaw output saved to: {OUTPUT_FILE}")

process.terminate()
