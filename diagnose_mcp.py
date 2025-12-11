import subprocess
import sys
import os
import json
import time

# Config
PYTHON_EXE = r"c:\Users\vedan\Desktop\mcp-rag\Document Automation\.venv\Scripts\python.exe"
SERVER_SCRIPT = r"c:\Users\vedan\Desktop\mcp-rag\Document Automation\src\server.py"

def run_diagnosis():
    print(f"Starting diagnosis...", file=sys.stderr)
    
    # Construct command
    cmd = [PYTHON_EXE, SERVER_SCRIPT]
    print(f"Command: {cmd}", file=sys.stderr)

    # Start process
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.path.dirname(SERVER_SCRIPT)
    )

    # Prepare MCP Initialize Request
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
    
    input_str = json.dumps(init_request) + "\n"
    input_bytes = input_str.encode('utf-8')

    print(f"Sending: {input_str.strip()}", file=sys.stderr)

    try:
        # Send input and read output
        # processing communication manually to capture partial reads
        process.stdin.write(input_bytes)
        process.stdin.flush()

        # Read stdout for a bit
        time.sleep(2)
        
        # Non-blocking read attempt (or basic read)
        # We expect a JSON response.
        # Let's read whatever is there.
        if process.poll() is not None:
             print(f"Process exited prematurely with code {process.returncode}", file=sys.stderr)
             print(f"Stderr: {process.stderr.read().decode('utf-8', errors='replace')}", file=sys.stderr)
             return

        # Read line by line from stdout
        # NOTE: This might hang if server sends nothing.
        # But we want to see the "Trailing data".
        
        # Read raw bytes
        import msvcrt
        if sys.platform == "win32":
            msvcrt.setmode(process.stdout.fileno(), os.O_BINARY)
        
        raw_output = process.stdout.read1(4096) # Read up to 4k
        
        print(f"\n--- RAW STDOUT (Hex) ---\n{raw_output.hex()}", file=sys.stderr)
        print(f"\n--- RAW STDOUT (Text) ---\n{raw_output.decode('utf-8', errors='replace')}", file=sys.stderr)

        stderr_output = process.stderr.read()
        print(f"\n--- STDERR ---\n{stderr_output.decode('utf-8', errors='replace')}", file=sys.stderr)

    except Exception as e:
        print(f"Error during communication: {e}", file=sys.stderr)
    finally:
        process.terminate()

if __name__ == "__main__":
    run_diagnosis()
