import sys
import io
import os

with open("debug_output.txt", "w") as f:
    f.write("DEBUG SCRIPT STARTED\n")

    # Capture stdout
    captured_output = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = captured_output

    try:
        # Add parent dir to path just like server.py does
        from pathlib import Path
        sys.path.insert(0, str(Path("c:/Users/vedan/Desktop/mcp-rag/Document Automation")))
        
        f.write("IMPORTING SERVER...\n")
        # Import the server module
        import src.server
        f.write("IMPORT COMPLETE\n")
        
        # Also try to instantiate the server class if possible, without running it
        # This might trigger __init__ prints
        try:
            f.write("INSTANTIATING SERVER...\n")
            server = src.server.DocumentAutomationServer()
            f.write("INSTANTIATION COMPLETE\n")
        except Exception as e:
            f.write(f"INSTANTIATION FAILED: {e}\n")

    except Exception as e:
        sys.stdout = original_stdout # Restore before writing error
        f.write(f"IMPORT FAILED: {e}\n")

    # Restore stdout
    sys.stdout = original_stdout

    # Check if anything was captured
    output = captured_output.getvalue()
    if output:
        f.write(f"STDOUT POLLUTION DETECTED:\n---START---\n{output}\n---END---\n")
    else:
        f.write("No stdout pollution detected during import or init.\n")
