"""
Python AST parser implementation.

This module provides detailed AST parsing for Python source code,
extracting classes, functions, imports, and other structural elements.
"""

import ast
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Set, Tuple

from .base_parser import BaseParser, ParseResult, ASTNode, NodeType

logger = logging.getLogger(__name__)


class PythonParser(BaseParser):
    """
    Python AST parser using Python's built-in ast module.
    
    Provides comprehensive parsing of Python source code with
    detailed extraction of structural elements.
    """
    
    def __init__(self):
        super().__init__("python")
        self.supported_extensions = {'.py', '.pyi', '.pyw'}
    
    def parse_file(self, file_path: str, content: str) -> ParseResult:
        """Parse a Python file and return AST structure."""
        start_time = time.time()
        
        try:
            # Parse the content
            tree = ast.parse(content, filename=file_path)
            
            # Create root module node
            root_node = self._create_ast_node(
                NodeType.MODULE,
                Path(file_path).stem,
                1,
                len(content.split('\n')),
                metadata={'file_path': file_path}
            )
            
            # Process the AST
            self._process_module(tree, root_node, content.split('\n'))
            
            parse_time = time.time() - start_time
            
            return ParseResult(
                file_path=file_path,
                language=self.language,
                success=True,
                root_node=root_node,
                parse_time=parse_time,
                metadata={
                    'total_lines': len(content.split('\n')),
                    'ast_node_count': self._count_ast_nodes(tree)
                }
            )
            
        except SyntaxError as e:
            parse_time = time.time() - start_time
            return ParseResult(
                file_path=file_path,
                language=self.language,
                success=False,
                parse_time=parse_time,
                error=f"Syntax error at line {e.lineno}: {e.msg}"
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
        """Parse Python string content."""
        return self.parse_file(filename, content)
    
    def _process_module(self, tree: ast.Module, root_node: ASTNode, lines: List[str]) -> None:
        """Process module-level AST nodes."""
        for node in tree.body:
            child_node = self._process_node(node, lines)
            if child_node:
                self._add_child_node(root_node, child_node)
    
    def _process_node(self, node: ast.AST, lines: List[str]) -> Optional[ASTNode]:
        """Process a single AST node and return corresponding ASTNode."""
        if isinstance(node, ast.ClassDef):
            return self._process_class(node, lines)
        elif isinstance(node, ast.FunctionDef):
            return self._process_function(node, lines, is_method=False)
        elif isinstance(node, ast.AsyncFunctionDef):
            return self._process_async_function(node, lines, is_method=False)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            return self._process_import(node, lines)
        elif isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
            return self._process_control_flow(node, lines)
        elif isinstance(node, ast.Assign):
            return self._process_assignment(node, lines)
        else:
            # Generic statement
            return self._process_generic_statement(node, lines)
    
    def _process_class(self, node: ast.ClassDef, lines: List[str]) -> ASTNode:
        """Process a class definition."""
        line_start, line_end, col_start, col_end = self._get_node_location(node)
        
        # Extract class information
        base_classes = [self._get_name(base) for base in node.bases]
        decorators = [self._get_name(dec) for dec in node.decorator_list]
        docstring = self._extract_docstring_from_body(node.body)
        
        class_node = self._create_ast_node(
            NodeType.CLASS,
            node.name,
            line_start,
            line_end,
            col_start,
            col_end,
            metadata={
                'base_classes': base_classes,
                'decorators': decorators,
                'docstring': docstring,
                'methods': [],
                'properties': [],
                'class_variables': []
            },
            raw_node=node
        )
        
        # Process class body
        for body_node in node.body:
            child_node = None
            
            if isinstance(body_node, ast.FunctionDef):
                child_node = self._process_function(body_node, lines, is_method=True)
            elif isinstance(body_node, ast.AsyncFunctionDef):
                child_node = self._process_async_function(body_node, lines, is_method=True)
            elif isinstance(body_node, ast.Assign):
                # Class variable
                child_node = self._process_assignment(body_node, lines, is_class_var=True)
            else:
                child_node = self._process_node(body_node, lines)
            
            if child_node:
                self._add_child_node(class_node, child_node)
                
                # Update class metadata
                if child_node.node_type == NodeType.METHOD:
                    class_node.metadata['methods'].append(child_node.name)
                elif child_node.node_type == NodeType.VARIABLE and child_node.metadata.get('is_class_var'):
                    class_node.metadata['class_variables'].append(child_node.name)
        
        return class_node
    
    def _process_function(self, node: ast.FunctionDef, lines: List[str], is_method: bool = False) -> ASTNode:
        """Process a function definition."""
        line_start, line_end, col_start, col_end = self._get_node_location(node)
        
        # Extract function information
        decorators = [self._get_name(dec) for dec in node.decorator_list]
        docstring = self._extract_docstring_from_body(node.body)
        params = self._extract_function_parameters(node)
        return_annotation = self._get_annotation(node.returns) if node.returns else None
        
        # Determine if it's a special method
        is_special = is_method and node.name.startswith('__') and node.name.endswith('__')
        is_property = any(dec in ['property', 'cached_property'] for dec in decorators)
        
        node_type = NodeType.METHOD if is_method else NodeType.FUNCTION
        
        func_node = self._create_ast_node(
            node_type,
            node.name,
            line_start,
            line_end,
            col_start,
            col_end,
            metadata={
                'decorators': decorators,
                'docstring': docstring,
                'parameters': params,
                'return_annotation': return_annotation,
                'is_async': False,
                'is_generator': self._is_generator(node),
                'is_method': is_method,
                'is_special_method': is_special,
                'is_property': is_property,
                'complexity': self._calculate_complexity(node)
            },
            raw_node=node
        )
        
        # Process function body for nested functions and control flow
        for body_node in node.body:
            child_node = self._process_node(body_node, lines)
            if child_node:
                self._add_child_node(func_node, child_node)
        
        return func_node
    
    def _process_async_function(self, node: ast.AsyncFunctionDef, lines: List[str], is_method: bool = False) -> ASTNode:
        """Process an async function definition."""
        # Convert to regular function node and mark as async
        func_node = self._process_function(node, lines, is_method)
        func_node.metadata['is_async'] = True
        return func_node
    
    def _process_import(self, node: Union[ast.Import, ast.ImportFrom], lines: List[str]) -> ASTNode:
        """Process import statements."""
        line_start, line_end, col_start, col_end = self._get_node_location(node)
        
        if isinstance(node, ast.Import):
            # import module1, module2 as alias2
            names = []
            for alias in node.names:
                names.append({
                    'name': alias.name,
                    'alias': alias.asname
                })
            
            import_node = self._create_ast_node(
                NodeType.IMPORT,
                ', '.join(alias.name for alias in node.names),
                line_start,
                line_end,
                col_start,
                col_end,
                metadata={
                    'type': 'import',
                    'names': names,
                    'module': None
                },
                raw_node=node
            )
            
        else:  # ast.ImportFrom
            # from module import name1, name2 as alias2
            module = node.module or ''
            level = node.level or 0
            
            names = []
            for alias in node.names:
                names.append({
                    'name': alias.name,
                    'alias': alias.asname
                })
            
            display_name = f"from {module} import {', '.join(alias.name for alias in node.names)}"
            
            import_node = self._create_ast_node(
                NodeType.IMPORT,
                display_name,
                line_start,
                line_end,
                col_start,
                col_end,
                metadata={
                    'type': 'from_import',
                    'module': module,
                    'names': names,
                    'level': level
                },
                raw_node=node
            )
        
        return import_node
    
    def _process_control_flow(self, node: ast.AST, lines: List[str]) -> ASTNode:
        """Process control flow nodes."""
        line_start, line_end, col_start, col_end = self._get_node_location(node)
        
        control_type = type(node).__name__.lower()
        
        control_node = self._create_ast_node(
            NodeType.CONTROL_FLOW,
            control_type,
            line_start,
            line_end,
            col_start,
            col_end,
            metadata={
                'control_type': control_type,
                'has_else': hasattr(node, 'orelse') and bool(node.orelse),
                'has_finally': hasattr(node, 'finalbody') and bool(node.finalbody)
            },
            raw_node=node
        )
        
        return control_node
    
    def _process_assignment(self, node: ast.Assign, lines: List[str], is_class_var: bool = False) -> Optional[ASTNode]:
        """Process assignment statements."""
        line_start, line_end, col_start, col_end = self._get_node_location(node)
        
        # Extract variable names from targets
        var_names = []
        for target in node.targets:
            names = self._extract_assignment_targets(target)
            var_names.extend(names)
        
        if not var_names:
            return None
        
        # Use first variable name as primary
        primary_name = var_names[0]
        
        var_node = self._create_ast_node(
            NodeType.VARIABLE,
            primary_name,
            line_start,
            line_end,
            col_start,
            col_end,
            metadata={
                'all_names': var_names,
                'is_class_var': is_class_var,
                'has_annotation': False,
                'annotation': None
            },
            raw_node=node
        )
        
        return var_node
    
    def _process_generic_statement(self, node: ast.AST, lines: List[str]) -> Optional[ASTNode]:
        """Process generic statements that don't fit other categories."""
        line_start, line_end, col_start, col_end = self._get_node_location(node)
        
        statement_type = type(node).__name__
        
        # Skip some statement types that aren't interesting
        skip_types = {'Pass', 'Break', 'Continue', 'Expr'}
        if statement_type in skip_types:
            return None
        
        stmt_node = self._create_ast_node(
            NodeType.STATEMENT,
            statement_type.lower(),
            line_start,
            line_end,
            col_start,
            col_end,
            metadata={
                'statement_type': statement_type
            },
            raw_node=node
        )
        
        return stmt_node
    
    def _get_node_location(self, node: ast.AST) -> Tuple[int, int, int, int]:
        """Get node location (line_start, line_end, col_start, col_end)."""
        line_start = getattr(node, 'lineno', 0)
        col_start = getattr(node, 'col_offset', 0)
        
        # Try to get end location (available in Python 3.8+)
        line_end = getattr(node, 'end_lineno', line_start)
        col_end = getattr(node, 'end_col_offset', col_start)
        
        return line_start, line_end, col_start, col_end
    
    def _extract_docstring_from_body(self, body: List[ast.AST]) -> Optional[str]:
        """Extract docstring from the beginning of a body."""
        if (body and 
            isinstance(body[0], ast.Expr) and 
            isinstance(body[0].value, ast.Constant) and 
            isinstance(body[0].value.value, str)):
            return body[0].value.value
        return None
    
    def _extract_function_parameters(self, node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """Extract function parameter information."""
        params = []
        args = node.args
        
        # Regular arguments
        for i, arg in enumerate(args.args):
            param_info = {
                'name': arg.arg,
                'annotation': self._get_annotation(arg.annotation) if arg.annotation else None,
                'default': None,
                'kind': 'positional'
            }
            
            # Check for default value
            default_offset = len(args.args) - len(args.defaults)
            if i >= default_offset:
                default_idx = i - default_offset
                param_info['default'] = self._get_default_value(args.defaults[default_idx])
            
            params.append(param_info)
        
        # *args parameter
        if args.vararg:
            params.append({
                'name': args.vararg.arg,
                'annotation': self._get_annotation(args.vararg.annotation) if args.vararg.annotation else None,
                'kind': 'var_positional'
            })
        
        # Keyword-only arguments
        for i, arg in enumerate(args.kwonlyargs):
            param_info = {
                'name': arg.arg,
                'annotation': self._get_annotation(arg.annotation) if arg.annotation else None,
                'default': None,
                'kind': 'keyword_only'
            }
            
            if i < len(args.kw_defaults) and args.kw_defaults[i]:
                param_info['default'] = self._get_default_value(args.kw_defaults[i])
            
            params.append(param_info)
        
        # **kwargs parameter
        if args.kwarg:
            params.append({
                'name': args.kwarg.arg,
                'annotation': self._get_annotation(args.kwarg.annotation) if args.kwarg.annotation else None,
                'kind': 'var_keyword'
            })
        
        return params
    
    def _get_annotation(self, annotation: ast.AST) -> str:
        """Extract type annotation as string."""
        try:
            return ast.unparse(annotation)
        except:
            return str(type(annotation).__name__)
    
    def _get_default_value(self, default: ast.AST) -> str:
        """Extract default value as string."""
        try:
            return ast.unparse(default)
        except:
            return str(type(default).__name__)
    
    def _get_name(self, node: ast.AST) -> str:
        """Get name from various AST node types."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        else:
            try:
                return ast.unparse(node)
            except:
                return str(type(node).__name__)
    
    def _extract_assignment_targets(self, target: ast.AST) -> List[str]:
        """Extract variable names from assignment targets."""
        names = []
        
        if isinstance(target, ast.Name):
            names.append(target.id)
        elif isinstance(target, ast.Tuple):
            for elt in target.elts:
                names.extend(self._extract_assignment_targets(elt))
        elif isinstance(target, ast.List):
            for elt in target.elts:
                names.extend(self._extract_assignment_targets(elt))
        elif isinstance(target, ast.Starred):
            names.extend(self._extract_assignment_targets(target.value))
        
        return names
    
    def _is_generator(self, node: ast.FunctionDef) -> bool:
        """Check if function is a generator."""
        for child_node in ast.walk(node):
            if isinstance(child_node, (ast.Yield, ast.YieldFrom)):
                return True
        return False
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity
        
        for child_node in ast.walk(node):
            if isinstance(child_node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child_node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child_node, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _count_ast_nodes(self, tree: ast.AST) -> int:
        """Count total AST nodes in tree."""
        return len(list(ast.walk(tree)))
    
    # Override base class methods with Python-specific implementations
    
    def _extract_docstring(self, node: Any) -> Optional[str]:
        """Extract docstring from AST node."""
        if hasattr(node, 'body') and node.body:
            return self._extract_docstring_from_body(node.body)
        return None
    
    def _is_control_flow_node(self, node: Any) -> bool:
        """Check if node is a control flow construct."""
        return isinstance(node, (
            ast.If, ast.While, ast.For, ast.AsyncFor, ast.Try, 
            ast.With, ast.AsyncWith, ast.Match
        ))
    
    def _extract_decorators(self, node: Any) -> List[str]:
        """Extract decorator names from a node."""
        if hasattr(node, 'decorator_list'):
            return [self._get_name(dec) for dec in node.decorator_list]
        return []
