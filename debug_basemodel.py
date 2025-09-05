#!/usr/bin/env python3
"""Debug script to reproduce BaseModel error"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Test creating the server
    print("Testing server creation...")
    from src.server import DocumentAutomationServer
    server = DocumentAutomationServer()
    print("OK Server created successfully")
    
    # Test the documentation tools
    print("Testing documentation tools...")
    tools = server.documentation_tools
    print("OK Documentation tools created successfully")
    
    # Test create dummy analysis data
    print("Testing generate_documentation call...")
    analysis_data = {
        'path': 'https://github.com/test/test',
        'comprehensive_analysis': {
            'project_structure': {'name': 'test', 'path': '/tmp/test', 'files': [], 'subdirectories': []},
            'dependencies': ['fastapi'],
            'metrics': {'total_files': 10},
            'technology_stack': {},
            'mermaid_diagrams': {'architecture': 'graph TD\n    A --> B'}
        }
    }
    
    # Add to cache
    analysis_id = "test_analysis_123"
    tools.analysis_cache[analysis_id] = analysis_data
    
    # Try to call generate_documentation
    import asyncio
    async def test_generate():
        try:
            result = await tools.generate_documentation(analysis_id=analysis_id)
            print(f"OK Documentation generated successfully: {len(result)} items")
            return result
        except Exception as e:
            print(f"ERROR in generate_documentation: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    result = asyncio.run(test_generate())
    
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()