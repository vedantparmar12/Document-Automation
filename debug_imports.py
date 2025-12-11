import sys
import io
import os

# Capture stdout
captured_output = io.StringIO()
sys.stdout = captured_output

print("CAPTURING START", file=sys.stderr)

try:
    # Add parent dir to path just like server.py does
    from pathlib import Path
    sys.path.insert(0, str(Path("c:/Users/vedan/Desktop/mcp-rag/Document Automation")))
    
    # Import the server module
    import src.server
    print("IMPORT COMPLETE", file=sys.stderr)
except Exception as e:
    print(f"IMPORT FAILED: {e}", file=sys.stderr)

# Restore stdout
sys.stdout = sys.__stdout__

# Check if anything was captured
output = captured_output.getvalue()
if output:
    print(f"STDOUT POLLUTION DETECTED:\n---START---\n{output}\n---END---", file=sys.stderr)
else:
    print("No stdout pollution detected during import.", file=sys.stderr)
