"""
JavaScript/TypeScript AST parser implementation.

This module provides AST parsing for JavaScript and TypeScript source code
using regex-based parsing since full AST parsing would require additional
dependencies.
"""

import re
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Set, Tuple

from .base_parser import BaseParser, ParseResult, ASTNode, NodeType

logger = logging.getLogger(__name__)


class JavaScriptParser(BaseParser):
    """
    JavaScript/TypeScript parser using regex-based parsing.
    
    Note: This is a simplified parser. For production use,
    consider using a proper JavaScript AST parser like Babel or ESTree.
    """
    
    def __init__(self):
        super().__init__("javascript")
        self.supported_extensions = {'.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'}
        
        # Regex patterns for different constructs
        self.patterns = {
            'function_declaration': re.compile(
                r'^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\([^)]*\)\s*\{',
                re.MULTILINE
            ),
            'arrow_function': re.compile(
                r'^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>\s*\{?',
                re.MULTILINE
            ),
            'method': re.compile(
                r'^\s*(?:async\s+)?(\w+)\s*\([^)]*\)\s*\{',
                re.MULTILINE
            ),
            'class': re.compile(
                r'^\s*(?:export\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{',
                re.MULTILINE
            ),
            'import': re.compile(
                r'^\s*import\s+(.+?)\s+from\s+[\'"]([^\'"]+)[\'"]',
                re.MULTILINE
            ),
            'require': re.compile(
                r'^\s*(?:const|let|var)\s+(.+?)\s*=\s*require\([\'"]([^\'"]+)[\'"]\)',
                re.MULTILINE
            ),
            'export': re.compile(
                r'^\s*export\s+(?:default\s+)?(?:class|function|const|let|var)\s+(\w+)',
                re.MULTILINE
            ),
            'control_flow': re.compile(
                r'^\s*(if|for|while|switch|try|catch|finally)\s*[\(\{]',
                re.MULTILINE
            ),
            'variable': re.compile(
                r'^\s*(const|let|var)\s+(\w+)(?:\s*:\s*[\w<>\[\]]+)?\s*=',
                re.MULTILINE
            ),
            'interface': re.compile(
                r'^\s*(?:export\s+)?interface\s+(\w+)(?:\s+extends\s+[\w,\s]+)?\s*\{',
                re.MULTILINE
            ),
            'type': re.compile(
                r'^\s*(?:export\s+)?type\s+(\w+)(?:<[^>]*>)?\s*=',
                re.MULTILINE
            ),
            'enum': re.compile(
                r'^\s*(?:export\s+)?enum\s+(\w+)\s*\{',
                re.MULTILINE
            ),
        }
        
        # Comment patterns
        self.comment_patterns = {
            'single_line': re.compile(r'//.*$', re.MULTILINE),
            'multi_line': re.compile(r'/\*.*?\*/', re.DOTALL),
            'jsdoc': re.compile(r'/\*\*.*?\*/', re.DOTALL)
        }
    
    def parse_file(self, file_path: str, content: str) -> ParseResult:
        """Parse a JavaScript/TypeScript file."""
        start_time = time.time()
        
        try:
            lines = content.split('\n')
            
            # Create root module node
            root_node = self._create_ast_node(
                NodeType.MODULE,
                Path(file_path).stem,
                1,
                len(lines),
                metadata={'file_path': file_path}
            )
            
            # Parse different constructs
            self._parse_imports(content, root_node, lines)
            self._parse_classes(content, root_node, lines)
            self._parse_functions(content, root_node, lines)
            self._parse_variables(content, root_node, lines)
            self._parse_types_and_interfaces(content, root_node, lines)
            
            parse_time = time.time() - start_time
            
            # Determine if it's TypeScript
            is_typescript = (
                Path(file_path).suffix in {'.ts', '.tsx'} or
                'interface' in content or
                'type ' in content or
                ': ' in content  # Type annotations
            )
            
            return ParseResult(
                file_path=file_path,
                language="typescript" if is_typescript else "javascript",
                success=True,
                root_node=root_node,
                parse_time=parse_time,
                metadata={
                    'total_lines': len(lines),
                    'is_typescript': is_typescript,
                    'is_react': self._is_react_file(content, file_path),
                    'is_node': self._is_node_file(content),
                    'has_jsx': self._has_jsx(content)
                }
            )
            
        except Exception as e:
            parse_time = time.time() - start_time
            return ParseResult(
                file_path=file_path,
                language=self.language,
                success=False,
                parse_time=parse_time,
                error=f"Parse error: {str(e)}"
            )
    
    def parse_string(self, content: str, filename: str = "<string>") -> ParseResult:
        """Parse JavaScript/TypeScript string content."""
        return self.parse_file(filename, content)
    
    def _parse_imports(self, content: str, root_node: ASTNode, lines: List[str]) -> None:
        """Parse import and require statements."""
        # ES6 imports
        for match in self.patterns['import'].finditer(content):
            import_spec = match.group(1).strip()
            module = match.group(2)
            line_num = content[:match.start()].count('\n') + 1
            
            import_node = self._create_ast_node(
                NodeType.IMPORT,
                f"import {import_spec} from '{module}'",
                line_num,
                line_num,
                metadata={
                    'type': 'es6_import',
                    'module': module,
                    'import_spec': import_spec,
                    'is_default': not ('{' in import_spec or '*' in import_spec)
                }
            )
            self._add_child_node(root_node, import_node)
        
        # CommonJS requires
        for match in self.patterns['require'].finditer(content):
            var_name = match.group(1).strip()
            module = match.group(2)
            line_num = content[:match.start()].count('\n') + 1
            
            import_node = self._create_ast_node(
                NodeType.IMPORT,
                f"const {var_name} = require('{module}')",
                line_num,
                line_num,
                metadata={
                    'type': 'commonjs_require',
                    'module': module,
                    'var_name': var_name
                }
            )
            self._add_child_node(root_node, import_node)
    
    def _parse_classes(self, content: str, root_node: ASTNode, lines: List[str]) -> None:
        """Parse class definitions."""
        for match in self.patterns['class'].finditer(content):
            class_name = match.group(1)
            base_class = match.group(2) if match.group(2) else None
            line_start = content[:match.start()].count('\n') + 1
            
            # Find class end by counting braces
            class_start = match.end()
            brace_count = 1
            pos = class_start
            
            while pos < len(content) and brace_count > 0:
                if content[pos] == '{':
                    brace_count += 1
                elif content[pos] == '}':
                    brace_count -= 1
                pos += 1
            
            line_end = content[:pos].count('\n') + 1
            class_body = content[class_start:pos-1]
            
            # Extract class metadata
            methods = self._extract_class_methods(class_body)
            constructors = [m for m in methods if m['name'] == 'constructor']
            
            class_node = self._create_ast_node(
                NodeType.CLASS,
                class_name,
                line_start,
                line_end,
                metadata={
                    'base_class': base_class,
                    'methods': [m['name'] for m in methods],
                    'has_constructor': len(constructors) > 0,
                    'is_exported': 'export' in content[max(0, match.start()-20):match.start()]
                }
            )
            
            # Add method nodes
            for method_info in methods:
                method_node = self._create_ast_node(
                    NodeType.METHOD,
                    method_info['name'],
                    line_start + method_info['line_offset'],
                    line_start + method_info['line_offset'] + method_info.get('line_count', 1),
                    metadata={
                        'is_constructor': method_info['name'] == 'constructor',
                        'is_static': method_info.get('is_static', False),
                        'is_async': method_info.get('is_async', False),
                        'parameters': method_info.get('parameters', [])
                    }
                )
                self._add_child_node(class_node, method_node)
            
            self._add_child_node(root_node, class_node)
    
    def _parse_functions(self, content: str, root_node: ASTNode, lines: List[str]) -> None:
        """Parse function declarations and arrow functions."""
        # Function declarations
        for match in self.patterns['function_declaration'].finditer(content):
            func_name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            
            # Estimate function end (simplified)
            line_end = self._estimate_function_end(content, match.start(), lines)
            
            func_node = self._create_ast_node(
                NodeType.FUNCTION,
                func_name,
                line_num,
                line_end,
                metadata={
                    'type': 'function_declaration',
                    'is_async': 'async' in match.group(0),
                    'is_exported': 'export' in match.group(0),
                    'parameters': self._extract_function_params(match.group(0))
                }
            )
            self._add_child_node(root_node, func_node)
        
        # Arrow functions
        for match in self.patterns['arrow_function'].finditer(content):
            func_name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            
            line_end = self._estimate_function_end(content, match.start(), lines)
            
            func_node = self._create_ast_node(
                NodeType.FUNCTION,
                func_name,
                line_num,
                line_end,
                metadata={
                    'type': 'arrow_function',
                    'is_async': 'async' in match.group(0),
                    'is_exported': 'export' in match.group(0),
                    'parameters': self._extract_function_params(match.group(0))
                }
            )
            self._add_child_node(root_node, func_node)
    
    def _parse_variables(self, content: str, root_node: ASTNode, lines: List[str]) -> None:
        """Parse variable declarations."""
        for match in self.patterns['variable'].finditer(content):
            var_type = match.group(1)  # const, let, var
            var_name = match.group(2)
            line_num = content[:match.start()].count('\n') + 1
            
            var_node = self._create_ast_node(
                NodeType.VARIABLE,
                var_name,
                line_num,
                line_num,
                metadata={
                    'declaration_type': var_type,
                    'is_const': var_type == 'const'
                }
            )
            self._add_child_node(root_node, var_node)
    
    def _parse_types_and_interfaces(self, content: str, root_node: ASTNode, lines: List[str]) -> None:
        """Parse TypeScript interfaces, types, and enums."""
        # Interfaces
        for match in self.patterns['interface'].finditer(content):
            interface_name = match.group(1)
            line_start = content[:match.start()].count('\n') + 1
            
            # Find interface end
            interface_end = self._find_block_end(content, match.end() - 1)
            line_end = content[:interface_end].count('\n') + 1
            
            interface_node = self._create_ast_node(
                NodeType.CLASS,  # Treat interfaces like classes for now
                interface_name,
                line_start,
                line_end,
                metadata={
                    'type': 'interface',
                    'is_exported': 'export' in content[max(0, match.start()-20):match.start()]
                }
            )
            self._add_child_node(root_node, interface_node)
        
        # Type aliases
        for match in self.patterns['type'].finditer(content):
            type_name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            
            type_node = self._create_ast_node(
                NodeType.VARIABLE,  # Treat types as variables for now
                type_name,
                line_num,
                line_num,
                metadata={
                    'type': 'type_alias',
                    'is_exported': 'export' in content[max(0, match.start()-20):match.start()]
                }
            )
            self._add_child_node(root_node, type_node)
        
        # Enums
        for match in self.patterns['enum'].finditer(content):
            enum_name = match.group(1)
            line_start = content[:match.start()].count('\n') + 1
            
            enum_end = self._find_block_end(content, match.end() - 1)
            line_end = content[:enum_end].count('\n') + 1
            
            enum_node = self._create_ast_node(
                NodeType.CLASS,  # Treat enums like classes
                enum_name,
                line_start,
                line_end,
                metadata={
                    'type': 'enum',
                    'is_exported': 'export' in content[max(0, match.start()-20):match.start()]
                }
            )
            self._add_child_node(root_node, enum_node)
    
    def _extract_class_methods(self, class_body: str) -> List[Dict[str, Any]]:
        """Extract method information from class body."""
        methods = []
        lines = class_body.split('\n')
        
        for i, line in enumerate(lines):
            # Method pattern: optional async, method name, parameters
            method_match = re.match(r'^\s*(static\s+)?(async\s+)?(\w+)\s*\([^)]*\)\s*\{?', line)
            if method_match:
                is_static = bool(method_match.group(1))
                is_async = bool(method_match.group(2))
                method_name = method_match.group(3)
                
                # Skip if it looks like a property
                if '=' in line and not line.strip().endswith('{'):
                    continue
                
                methods.append({
                    'name': method_name,
                    'line_offset': i,
                    'is_static': is_static,
                    'is_async': is_async,
                    'parameters': self._extract_function_params(line)
                })
        
        return methods
    
    def _extract_function_params(self, func_signature: str) -> List[str]:
        """Extract parameter names from function signature."""
        # Find parameter list
        paren_start = func_signature.find('(')
        paren_end = func_signature.find(')', paren_start)
        
        if paren_start == -1 or paren_end == -1:
            return []
        
        params_str = func_signature[paren_start + 1:paren_end].strip()
        if not params_str:
            return []
        
        # Split by comma and clean up
        params = []
        for param in params_str.split(','):
            param = param.strip()
            # Remove type annotations (TypeScript)
            if ':' in param:
                param = param.split(':')[0].strip()
            # Remove default values
            if '=' in param:
                param = param.split('=')[0].strip()
            if param:
                params.append(param)
        
        return params
    
    def _estimate_function_end(self, content: str, func_start: int, lines: List[str]) -> int:
        """Estimate where a function ends (simplified approach)."""
        func_line = content[:func_start].count('\n') + 1
        
        # Look for opening brace
        brace_pos = content.find('{', func_start)
        if brace_pos == -1:
            return func_line  # Arrow function without braces
        
        # Count braces to find end
        brace_count = 1
        pos = brace_pos + 1
        
        while pos < len(content) and brace_count > 0:
            if content[pos] == '{':
                brace_count += 1
            elif content[pos] == '}':
                brace_count -= 1
            pos += 1
        
        return content[:pos].count('\n') + 1
    
    def _find_block_end(self, content: str, start_pos: int) -> int:
        """Find the end of a block starting with {."""
        brace_count = 1
        pos = start_pos + 1
        
        while pos < len(content) and brace_count > 0:
            if content[pos] == '{':
                brace_count += 1
            elif content[pos] == '}':
                brace_count -= 1
            pos += 1
        
        return pos
    
    def _is_react_file(self, content: str, file_path: str) -> bool:
        """Check if file is a React component."""
        react_indicators = [
            'import React',
            'from \'react\'',
            'from "react"',
            '.jsx',
            '.tsx',
            '</',  # JSX tags
            'React.Component',
            'useEffect',
            'useState'
        ]
        
        return (
            any(indicator in content for indicator in react_indicators) or
            Path(file_path).suffix in {'.jsx', '.tsx'}
        )
    
    def _is_node_file(self, content: str) -> bool:
        """Check if file is a Node.js file."""
        node_indicators = [
            'require(',
            'module.exports',
            'process.env',
            '__dirname',
            '__filename',
            'fs.readFile',
            'path.join'
        ]
        
        return any(indicator in content for indicator in node_indicators)
    
    def _has_jsx(self, content: str) -> bool:
        """Check if file contains JSX."""
        jsx_patterns = [
            r'<[A-Z]\w*',  # Component tags
            r'<\w+.*>.*</\w+>',  # HTML-like tags
            r'<.*className=',  # className attribute
            r'<.*jsx',  # JSX-specific attributes
        ]
        
        return any(re.search(pattern, content) for pattern in jsx_patterns)
    
    # Helper methods for extracting specific information
    
    def extract_dependencies(self, content: str) -> Dict[str, List[str]]:
        """Extract dependencies from imports and requires."""
        dependencies = {
            'imports': [],
            'requires': [],
            'peer_dependencies': []
        }
        
        # ES6 imports
        for match in self.patterns['import'].finditer(content):
            module = match.group(2)
            dependencies['imports'].append(module)
        
        # CommonJS requires
        for match in self.patterns['require'].finditer(content):
            module = match.group(2)
            dependencies['requires'].append(module)
        
        return dependencies
    
    def extract_exports(self, content: str) -> List[Dict[str, Any]]:
        """Extract export information."""
        exports = []
        
        # Named exports
        export_patterns = [
            r'export\s+(?:const|let|var|function|class)\s+(\w+)',
            r'export\s+\{\s*([^}]+)\s*\}',
            r'export\s+default\s+(?:class\s+)?(\w+)',
        ]
        
        for pattern in export_patterns:
            for match in re.finditer(pattern, content):
                exports.append({
                    'name': match.group(1),
                    'line': content[:match.start()].count('\n') + 1,
                    'type': 'named' if 'default' not in match.group(0) else 'default'
                })
        
        return exports
