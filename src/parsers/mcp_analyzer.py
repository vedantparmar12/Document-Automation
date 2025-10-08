"""
MCP Server Analyzer

Specialized analyzer for Model Context Protocol (MCP) servers.
Extracts tools, resources, prompts, and server configurations.
"""

import ast
import json
import logging
import re
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """Represents an MCP tool definition."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    required_params: List[str] = field(default_factory=list)
    optional_params: List[str] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    handler_function: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'input_schema': self.input_schema,
            'required_params': self.required_params,
            'optional_params': self.optional_params,
            'examples': self.examples,
            'handler_function': self.handler_function
        }


@dataclass
class MCPResource:
    """Represents an MCP resource."""
    uri: str
    name: str
    description: str
    mime_type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'uri': self.uri,
            'name': self.name,
            'description': self.description,
            'mime_type': self.mime_type
        }


@dataclass
class MCPServerInfo:
    """Complete MCP server analysis."""
    server_name: str
    server_class: str
    tools: List[MCPTool] = field(default_factory=list)
    resources: List[MCPResource] = field(default_factory=list)
    prompts: List[Dict[str, Any]] = field(default_factory=list)
    transport: str = "stdio"  # stdio, sse, http
    env_variables: List[Dict[str, str]] = field(default_factory=list)
    client_configs: Dict[str, str] = field(default_factory=dict)
    integrations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'server_name': self.server_name,
            'server_class': self.server_class,
            'tools': [t.to_dict() for t in self.tools],
            'resources': [r.to_dict() for r in self.resources],
            'prompts': self.prompts,
            'transport': self.transport,
            'env_variables': self.env_variables,
            'client_configs': self.client_configs,
            'integrations': self.integrations
        }


class MCPServerAnalyzer:
    """Analyzer for MCP server codebases."""
    
    def __init__(self):
        self.mcp_patterns = {
            'server_init': [
                r'Server\s*\(',
                r'from\s+mcp\.server\s+import\s+Server',
                r'@app\.list_tools',
                r'@app\.call_tool',
            ],
            'tool_decorator': [
                r'@.*\.list_tools\(\)',
                r'@.*\.call_tool\(\)',
            ],
            'transport': [
                r'stdio_server\(\)',
                r'sse_server\(\)',
                r'create_sse_server\(\)',
            ]
        }
    
    def analyze(self, codebase_path: str, file_contents: Dict[str, str]) -> Optional[MCPServerInfo]:
        """
        Analyze a codebase for MCP server patterns.
        
        Args:
            codebase_path: Root path of the codebase
            file_contents: Dictionary of file_path: content
            
        Returns:
            MCPServerInfo if MCP server detected, None otherwise
        """
        logger.info("Analyzing codebase for MCP server patterns...")
        
        # Find the main server file
        server_file = self._find_server_file(file_contents)
        if not server_file:
            logger.info("No MCP server file detected")
            return None
        
        logger.info(f"Found MCP server file: {server_file}")
        
        # Parse the server file
        content = file_contents[server_file]
        try:
            tree = ast.parse(content)
            # Count nodes for debugging
            function_nodes = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            logger.info(f"Parsed {server_file}: {len(function_nodes)} functions found in AST")
        except SyntaxError as e:
            logger.error(f"Failed to parse {server_file}: {e}")
            return None
        
        # Extract server information
        server_info = self._extract_server_info(tree, content, server_file)
        
        # Extract environment variables
        server_info.env_variables = self._extract_env_variables(file_contents)
        
        # Detect integrations
        server_info.integrations = self._detect_integrations(file_contents)
        
        # Generate client configs
        server_info.client_configs = self._generate_client_configs(
            codebase_path, server_info.server_name
        )
        
        return server_info
    
    def _find_server_file(self, file_contents: Dict[str, str]) -> Optional[str]:
        """Find the main MCP server file."""
        candidates = []
        
        for file_path, content in file_contents.items():
            if not file_path.endswith('.py'):
                continue
            
            score = 0
            
            # Check for MCP imports
            if 'from mcp.server import Server' in content or 'from mcp import Server' in content:
                score += 10
            
            # Check for server decorators
            if '@app.list_tools' in content or '@server.list_tools' in content:
                score += 8
            
            # Check for transport setup
            if 'stdio_server' in content or 'sse_server' in content:
                score += 5
            
            # Prefer files named 'server.py' or 'main.py'
            filename = Path(file_path).name.lower()
            if filename == 'server.py':
                score += 3
            elif filename == 'main.py':
                score += 2
            
            if score > 0:
                candidates.append((file_path, score))
        
        if not candidates:
            return None
        
        # Return the file with highest score
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]
    
    def _extract_server_info(
        self, 
        tree: ast.AST, 
        content: str,
        file_path: str
    ) -> MCPServerInfo:
        """Extract server information from AST."""
        server_name = "unknown"
        server_class = "unknown"
        tools = []
        resources = []
        prompts = []
        transport = "stdio"
        
        # Find Server initialization
        for node in ast.walk(tree):
            # Server("name")
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'Server':
                    if node.args and isinstance(node.args[0], ast.Constant):
                        server_name = node.args[0].value
        
        # Extract tools from @app.list_tools() decorator
        tools = self._extract_tools_from_decorator(tree, content)
        
        # Extract resources
        resources = self._extract_resources(tree)
        
        # Extract prompts
        prompts = self._extract_prompts(tree)
        
        # Detect transport
        if 'stdio_server' in content:
            transport = 'stdio'
        elif 'sse_server' in content or 'create_sse_server' in content:
            transport = 'sse'
        elif 'create_http_server' in content:
            transport = 'http'
        
        return MCPServerInfo(
            server_name=server_name,
            server_class=server_class,
            tools=tools,
            resources=resources,
            prompts=prompts,
            transport=transport
        )
    
    def _extract_tools_from_decorator(self, tree: ast.AST, content: str) -> List[MCPTool]:
        """Extract tool definitions from @app.list_tools() decorated functions."""
        tools = []
        function_count = 0
        decorated_count = 0
        
        for node in ast.walk(tree):
            # Check for both sync and async functions
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            
            function_count += 1
            if node.decorator_list:
                decorated_count += 1
                logger.info(f"Function '{node.name}' has {len(node.decorator_list)} decorators")
                for dec in node.decorator_list:
                    logger.info(f"  Decorator type: {type(dec)}, is_list_tools: {self._is_list_tools_decorator(dec)}")
            
            # Check if this is a list_tools handler
            has_list_tools_decorator = any(
                self._is_list_tools_decorator(dec) for dec in node.decorator_list
            )
            
            if has_list_tools_decorator:
                logger.info(f"✓ Found list_tools function: {node.name}")
                # Extract the tool definitions from the function body
                tools = self._parse_tool_definitions(node, content)
                logger.info(f"Extracted {len(tools)} tools from {node.name}")
                break
        
        logger.info(f"Scanned {function_count} functions, {decorated_count} with decorators")
        if not tools:
            logger.warning("No list_tools function found")
        
        return tools
    
    def _is_list_tools_decorator(self, decorator: ast.AST) -> bool:
        """Check if a decorator is @app.list_tools()."""
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Attribute):
                return decorator.func.attr == 'list_tools'
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr == 'list_tools'
        return False
    
    def _parse_tool_definitions(self, node: ast.FunctionDef, content: str) -> List[MCPTool]:
        """Parse tool definitions from list_tools function body."""
        tools = []
        
        # Look for return statement with list of Tool objects
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Return) and stmt.value:
                logger.info(f"Found return statement, type: {type(stmt.value)}")
                if isinstance(stmt.value, ast.List):
                    logger.info(f"Return statement is a list with {len(stmt.value.elts)} elements")
                    # Extract each Tool() or types.Tool() call
                    for i, elt in enumerate(stmt.value.elts):
                        if isinstance(elt, ast.Call):
                            # Check if it's a Tool() or types.Tool() or Type.Tool() call
                            is_tool_call = False
                            func_name = "unknown"
                            if isinstance(elt.func, ast.Name):
                                func_name = elt.func.id
                                if func_name == 'Tool':
                                    is_tool_call = True
                            elif isinstance(elt.func, ast.Attribute):
                                func_name = f"{getattr(elt.func.value, 'id', '?')}.{elt.func.attr}"
                                if elt.func.attr == 'Tool':
                                    is_tool_call = True
                            
                            logger.info(f"  Element {i}: {func_name}, is_tool_call={is_tool_call}")
                            
                            if is_tool_call:
                                tool = self._parse_tool_call(elt)
                                if tool:
                                    logger.info(f"    ✓ Parsed tool: {tool.name}")
                                    tools.append(tool)
                                else:
                                    logger.warning(f"    ✗ Failed to parse tool")
        
        return tools
    
    def _parse_tool_call(self, call: ast.Call) -> Optional[MCPTool]:
        """Parse a single Tool() call."""
        tool_data = {
            'name': None,
            'description': None,
            'inputSchema': {}
        }
        
        # Extract keyword arguments
        for keyword in call.keywords:
            if keyword.arg == 'name' and isinstance(keyword.value, ast.Constant):
                tool_data['name'] = keyword.value.value
            elif keyword.arg == 'description' and isinstance(keyword.value, ast.Constant):
                tool_data['description'] = keyword.value.value
            elif keyword.arg == 'inputSchema':
                # Parse the schema dict
                tool_data['inputSchema'] = self._parse_dict_node(keyword.value)
        
        if not tool_data['name']:
            return None
        
        # Parse schema
        schema = tool_data['inputSchema']
        required_params = schema.get('required', [])
        properties = schema.get('properties', {})
        optional_params = [p for p in properties.keys() if p not in required_params]
        
        return MCPTool(
            name=tool_data['name'],
            description=tool_data.get('description', ''),
            input_schema=schema,
            required_params=required_params,
            optional_params=optional_params
        )
    
    def _parse_dict_node(self, node: ast.AST) -> Dict[str, Any]:
        """Recursively parse an ast.Dict node into a Python dict."""
        if isinstance(node, ast.Dict):
            result = {}
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant):
                    result[key.value] = self._parse_dict_node(value)
            return result
        elif isinstance(node, ast.List):
            return [self._parse_dict_node(elt) for elt in node.elts]
        elif isinstance(node, ast.Constant):
            return node.value
        else:
            return {}
    
    def _extract_resources(self, tree: ast.AST) -> List[MCPResource]:
        """Extract resource definitions."""
        resources = []
        # Similar logic to tools, look for @app.list_resources()
        # Implementation depends on your MCP resource patterns
        return resources
    
    def _extract_prompts(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract prompt definitions."""
        prompts = []
        # Similar logic to tools, look for @app.list_prompts()
        return prompts
    
    def _extract_env_variables(self, file_contents: Dict[str, str]) -> List[Dict[str, str]]:
        """Extract environment variables from .env.example or code."""
        env_vars = []
        
        # Check .env.example
        for file_path, content in file_contents.items():
            if '.env.example' in file_path or '.env.template' in file_path:
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key = line.split('=')[0].strip()
                        # Extract comments as description
                        description = ""
                        env_vars.append({
                            'name': key,
                            'description': description,
                            'required': True
                        })
        
        # Also scan for os.getenv() calls
        for file_path, content in file_contents.items():
            if not file_path.endswith('.py'):
                continue
            
            # Find os.getenv("VAR_NAME") patterns
            matches = re.findall(r'os\.getenv\([\'"]([A-Z_]+)[\'"]', content)
            for var_name in matches:
                if not any(v['name'] == var_name for v in env_vars):
                    env_vars.append({
                        'name': var_name,
                        'description': '',
                        'required': False
                    })
        
        return env_vars
    
    def _detect_integrations(self, file_contents: Dict[str, str]) -> List[str]:
        """Detect external service integrations."""
        integrations = []
        
        integration_patterns = {
            'RapidAPI': r'rapidapi\.com|X-RapidAPI-Key',
            'OpenAI': r'openai|gpt-|OPENAI_API_KEY',
            'Anthropic': r'anthropic|claude|ANTHROPIC_API_KEY',
            'LiveKit': r'livekit|LIVEKIT_',
            'Deepgram': r'deepgram|DEEPGRAM_API_KEY',
            'Stripe': r'stripe|STRIPE_',
            'AWS': r'boto3|aws|AWS_',
            'Firebase': r'firebase|FIREBASE_',
            'Supabase': r'supabase|SUPABASE_',
        }
        
        all_content = ' '.join(file_contents.values())
        
        for service, pattern in integration_patterns.items():
            if re.search(pattern, all_content, re.IGNORECASE):
                integrations.append(service)
        
        return integrations
    
    def _generate_client_configs(self, codebase_path: str, server_name: str) -> Dict[str, str]:
        """Generate example client configurations."""
        configs = {}
        
        # Claude Desktop config
        configs['claude_desktop'] = f'''{{
  "mcpServers": {{
    "{server_name}": {{
      "command": "python",
      "args": ["path/to/{Path(codebase_path).name}/server.py"],
      "env": {{
        "API_KEY": "your_api_key_here"
      }}
    }}
  }}
}}'''
        
        # Cursor config
        configs['cursor'] = f'''{{
  "mcpServers": {{
    "{server_name}": {{
      "command": "python",
      "args": ["path/to/server.py"],
      "env": {{}}
    }}
  }}
}}'''
        
        return configs


def analyze_mcp_server(codebase_path: str, file_contents: Dict[str, str]) -> Optional[MCPServerInfo]:
    """
    Convenience function to analyze an MCP server.
    
    Args:
        codebase_path: Root path of the codebase
        file_contents: Dictionary mapping file paths to their contents
        
    Returns:
        MCPServerInfo if MCP server detected, None otherwise
    """
    analyzer = MCPServerAnalyzer()
    return analyzer.analyze(codebase_path, file_contents)
