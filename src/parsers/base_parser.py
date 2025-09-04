"""
Base parser interface for AST parsing across different languages.

This module provides the base classes and interfaces for implementing
language-specific AST parsers.
"""

import ast
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Types of AST nodes we track."""
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    VARIABLE = "variable"
    IMPORT = "import"
    DECORATOR = "decorator"
    COMMENT = "comment"
    DOCSTRING = "docstring"
    CONTROL_FLOW = "control_flow"
    EXPRESSION = "expression"
    STATEMENT = "statement"
    UNKNOWN = "unknown"


@dataclass
class ASTNode:
    """Representation of an AST node."""
    node_type: NodeType
    name: str
    line_start: int
    line_end: int
    column_start: int = 0
    column_end: int = 0
    parent: Optional['ASTNode'] = None
    children: List['ASTNode'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_node: Any = None  # Original AST node for reference
    
    @property
    def line_count(self) -> int:
        """Get number of lines this node spans."""
        return max(1, self.line_end - self.line_start + 1)
    
    @property
    def full_name(self) -> str:
        """Get full qualified name including parent context."""
        if self.parent and self.parent.node_type != NodeType.MODULE:
            return f"{self.parent.full_name}.{self.name}"
        return self.name
    
    def get_children_by_type(self, node_type: NodeType) -> List['ASTNode']:
        """Get all children of a specific type."""
        return [child for child in self.children if child.node_type == node_type]
    
    def get_all_descendants(self, node_type: Optional[NodeType] = None) -> List['ASTNode']:
        """Get all descendants, optionally filtered by type."""
        descendants = []
        for child in self.children:
            if node_type is None or child.node_type == node_type:
                descendants.append(child)
            descendants.extend(child.get_all_descendants(node_type))
        return descendants
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'node_type': self.node_type.value,
            'name': self.name,
            'full_name': self.full_name,
            'line_start': self.line_start,
            'line_end': self.line_end,
            'column_start': self.column_start,
            'column_end': self.column_end,
            'line_count': self.line_count,
            'children_count': len(self.children),
            'children': [child.to_dict() for child in self.children],
            'metadata': self.metadata
        }


@dataclass
class ParseResult:
    """Result of parsing a source file."""
    file_path: str
    language: str
    success: bool
    root_node: Optional[ASTNode] = None
    parse_time: float = 0.0
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def all_nodes(self) -> List[ASTNode]:
        """Get all nodes in the AST."""
        if not self.root_node:
            return []
        return [self.root_node] + self.root_node.get_all_descendants()
    
    def get_nodes_by_type(self, node_type: NodeType) -> List[ASTNode]:
        """Get all nodes of a specific type."""
        return [node for node in self.all_nodes if node.node_type == node_type]
    
    def get_functions(self) -> List[ASTNode]:
        """Get all function/method nodes."""
        return self.get_nodes_by_type(NodeType.FUNCTION) + self.get_nodes_by_type(NodeType.METHOD)
    
    def get_classes(self) -> List[ASTNode]:
        """Get all class nodes."""
        return self.get_nodes_by_type(NodeType.CLASS)
    
    def get_imports(self) -> List[ASTNode]:
        """Get all import nodes."""
        return self.get_nodes_by_type(NodeType.IMPORT)
    
    def get_complexity_estimate(self) -> int:
        """Get rough cyclomatic complexity estimate."""
        control_flow_nodes = self.get_nodes_by_type(NodeType.CONTROL_FLOW)
        return len(control_flow_nodes) + 1  # Base complexity of 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'file_path': self.file_path,
            'language': self.language,
            'success': self.success,
            'parse_time': self.parse_time,
            'error': self.error,
            'warnings': self.warnings,
            'metadata': self.metadata,
            'root_node': self.root_node.to_dict() if self.root_node else None,
            'statistics': {
                'total_nodes': len(self.all_nodes),
                'functions': len(self.get_functions()),
                'classes': len(self.get_classes()),
                'imports': len(self.get_imports()),
                'complexity_estimate': self.get_complexity_estimate()
            }
        }


class BaseParser(ABC):
    """
    Base class for language-specific AST parsers.
    
    Each language parser should inherit from this class and implement
    the abstract methods.
    """
    
    def __init__(self, language: str):
        self.language = language
        self.supported_extensions: Set[str] = set()
        self.node_visitors: Dict[str, callable] = {}
        
    @abstractmethod
    def parse_file(self, file_path: str, content: str) -> ParseResult:
        """
        Parse a file and return AST structure.
        
        Args:
            file_path: Path to the file being parsed
            content: File content as string
            
        Returns:
            ParseResult with AST structure
        """
        pass
    
    @abstractmethod
    def parse_string(self, content: str, filename: str = "<string>") -> ParseResult:
        """
        Parse string content and return AST structure.
        
        Args:
            content: Source code as string
            filename: Optional filename for error reporting
            
        Returns:
            ParseResult with AST structure
        """
        pass
    
    def supports_file(self, file_path: str) -> bool:
        """Check if this parser supports the given file."""
        extension = Path(file_path).suffix.lower()
        return extension in self.supported_extensions
    
    def _create_ast_node(
        self,
        node_type: NodeType,
        name: str,
        line_start: int,
        line_end: int,
        column_start: int = 0,
        column_end: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
        raw_node: Any = None
    ) -> ASTNode:
        """Helper method to create AST nodes."""
        return ASTNode(
            node_type=node_type,
            name=name,
            line_start=line_start,
            line_end=line_end,
            column_start=column_start,
            column_end=column_end,
            metadata=metadata or {},
            raw_node=raw_node
        )
    
    def _add_child_node(self, parent: ASTNode, child: ASTNode) -> None:
        """Add a child node to a parent."""
        child.parent = parent
        parent.children.append(child)
    
    def _extract_docstring(self, node: Any) -> Optional[str]:
        """Extract docstring from AST node (override in subclasses)."""
        return None
    
    def _get_node_location(self, node: Any) -> Tuple[int, int, int, int]:
        """Get node location (line_start, line_end, col_start, col_end)."""
        # Default implementation - override in subclasses
        return (0, 0, 0, 0)
    
    def _is_control_flow_node(self, node: Any) -> bool:
        """Check if node is a control flow construct."""
        # Override in subclasses
        return False
    
    def _extract_decorators(self, node: Any) -> List[str]:
        """Extract decorator names from a node."""
        # Override in subclasses
        return []
    
    def _extract_function_signature(self, node: Any) -> Dict[str, Any]:
        """Extract function signature information."""
        # Override in subclasses
        return {
            'parameters': [],
            'return_type': None,
            'is_async': False,
            'is_generator': False
        }
    
    def _extract_class_info(self, node: Any) -> Dict[str, Any]:
        """Extract class information."""
        # Override in subclasses
        return {
            'base_classes': [],
            'methods': [],
            'properties': [],
            'class_variables': []
        }
    
    def _extract_import_info(self, node: Any) -> Dict[str, Any]:
        """Extract import information."""
        # Override in subclasses
        return {
            'module': '',
            'names': [],
            'alias': None,
            'is_from_import': False
        }
    
    def get_supported_extensions(self) -> Set[str]:
        """Get set of supported file extensions."""
        return self.supported_extensions.copy()
    
    def get_language(self) -> str:
        """Get the language this parser handles."""
        return self.language
    
    def validate_syntax(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        Validate syntax without full parsing.
        
        Args:
            content: Source code to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            result = self.parse_string(content)
            return result.success, result.error
        except Exception as e:
            return False, str(e)
    
    def extract_structure_summary(self, parse_result: ParseResult) -> Dict[str, Any]:
        """Extract high-level structure summary from parse result."""
        if not parse_result.success or not parse_result.root_node:
            return {'error': 'Parse failed or no root node'}
        
        functions = parse_result.get_functions()
        classes = parse_result.get_classes()
        imports = parse_result.get_imports()
        
        return {
            'language': self.language,
            'total_lines': parse_result.metadata.get('total_lines', 0),
            'functions': {
                'count': len(functions),
                'names': [f.name for f in functions],
                'average_length': (
                    sum(f.line_count for f in functions) / len(functions)
                    if functions else 0
                )
            },
            'classes': {
                'count': len(classes),
                'names': [c.name for c in classes],
                'average_methods': (
                    sum(len(c.get_children_by_type(NodeType.METHOD)) for c in classes) / len(classes)
                    if classes else 0
                )
            },
            'imports': {
                'count': len(imports),
                'modules': [i.metadata.get('module', i.name) for i in imports]
            },
            'complexity': {
                'estimate': parse_result.get_complexity_estimate(),
                'control_flow_nodes': len(parse_result.get_nodes_by_type(NodeType.CONTROL_FLOW))
            }
        }
    
    def find_patterns(self, parse_result: ParseResult, patterns: List[str]) -> Dict[str, List[ASTNode]]:
        """
        Find nodes matching specific patterns.
        
        Args:
            parse_result: Parse result to search in
            patterns: List of patterns to search for
            
        Returns:
            Dictionary mapping patterns to matching nodes
        """
        matches = {pattern: [] for pattern in patterns}
        
        if not parse_result.success:
            return matches
        
        for node in parse_result.all_nodes:
            for pattern in patterns:
                if self._matches_pattern(node, pattern):
                    matches[pattern].append(node)
        
        return matches
    
    def _matches_pattern(self, node: ASTNode, pattern: str) -> bool:
        """Check if a node matches a given pattern."""
        # Simple pattern matching - can be extended
        pattern_lower = pattern.lower()
        
        # Check node name
        if pattern_lower in node.name.lower():
            return True
        
        # Check metadata
        for key, value in node.metadata.items():
            if isinstance(value, str) and pattern_lower in value.lower():
                return True
        
        return False
    
    def get_statistics(self, parse_result: ParseResult) -> Dict[str, Any]:
        """Get detailed statistics about the parsed code."""
        if not parse_result.success:
            return {'error': 'Parse failed'}
        
        all_nodes = parse_result.all_nodes
        
        # Count nodes by type
        type_counts = {}
        for node_type in NodeType:
            count = len([n for n in all_nodes if n.node_type == node_type])
            if count > 0:
                type_counts[node_type.value] = count
        
        # Depth analysis
        max_depth = 0
        avg_depth = 0
        if all_nodes:
            depths = []
            for node in all_nodes:
                depth = 0
                current = node.parent
                while current:
                    depth += 1
                    current = current.parent
                depths.append(depth)
            
            max_depth = max(depths) if depths else 0
            avg_depth = sum(depths) / len(depths) if depths else 0
        
        return {
            'total_nodes': len(all_nodes),
            'node_type_counts': type_counts,
            'depth': {
                'max': max_depth,
                'average': avg_depth
            },
            'complexity': parse_result.get_complexity_estimate(),
            'parse_time': parse_result.parse_time,
            'warnings': len(parse_result.warnings)
        }
