"""
AST analyzer for extracting high-level structure and insights from parsed code.

This module provides analysis capabilities that work with parsed AST structures
to extract patterns, calculate metrics, and generate insights.
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, Counter

from .base_parser import ParseResult, ASTNode, NodeType

logger = logging.getLogger(__name__)


@dataclass
class StructureAnalysis:
    """High-level structure analysis of parsed code."""
    file_path: str
    language: str
    total_nodes: int
    complexity_score: int
    maintainability_score: float
    
    # Counts by type
    classes: int = 0
    functions: int = 0
    methods: int = 0
    imports: int = 0
    variables: int = 0
    
    # Detailed information
    class_info: List[Dict[str, Any]] = field(default_factory=list)
    function_info: List[Dict[str, Any]] = field(default_factory=list)
    import_info: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metrics
    average_function_length: float = 0.0
    max_function_length: int = 0
    average_class_size: float = 0.0
    max_class_size: int = 0
    nesting_depth: int = 0
    
    # Dependencies and relationships
    internal_dependencies: Set[str] = field(default_factory=set)
    external_dependencies: Set[str] = field(default_factory=set)
    
    # Quality indicators
    has_docstrings: bool = False
    docstring_coverage: float = 0.0
    has_type_hints: bool = False
    type_hint_coverage: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'file_path': self.file_path,
            'language': self.language,
            'total_nodes': self.total_nodes,
            'complexity_score': self.complexity_score,
            'maintainability_score': self.maintainability_score,
            'counts': {
                'classes': self.classes,
                'functions': self.functions,
                'methods': self.methods,
                'imports': self.imports,
                'variables': self.variables
            },
            'metrics': {
                'average_function_length': self.average_function_length,
                'max_function_length': self.max_function_length,
                'average_class_size': self.average_class_size,
                'max_class_size': self.max_class_size,
                'nesting_depth': self.nesting_depth
            },
            'quality': {
                'has_docstrings': self.has_docstrings,
                'docstring_coverage': self.docstring_coverage,
                'has_type_hints': self.has_type_hints,
                'type_hint_coverage': self.type_hint_coverage
            },
            'dependencies': {
                'internal': list(self.internal_dependencies),
                'external': list(self.external_dependencies)
            },
            'details': {
                'classes': self.class_info,
                'functions': self.function_info,
                'imports': self.import_info
            }
        }


class ASTAnalyzer:
    """
    Analyzer for extracting insights from AST structures.
    
    Provides various analysis methods for code quality, structure,
    complexity, and maintainability assessment.
    """
    
    def __init__(self):
        self.analysis_cache: Dict[str, StructureAnalysis] = {}
    
    def analyze_structure(self, parse_result: ParseResult) -> StructureAnalysis:
        """
        Perform comprehensive structure analysis.
        
        Args:
            parse_result: Parsed AST structure
            
        Returns:
            StructureAnalysis with detailed insights
        """
        if not parse_result.success or not parse_result.root_node:
            return StructureAnalysis(
                file_path=parse_result.file_path,
                language=parse_result.language,
                total_nodes=0,
                complexity_score=0,
                maintainability_score=0.0
            )
        
        # Get all nodes for analysis
        all_nodes = parse_result.all_nodes
        
        # Basic counts
        node_counts = self._count_nodes_by_type(all_nodes)
        
        # Analyze classes
        classes = parse_result.get_classes()
        class_info = [self._analyze_class(cls) for cls in classes]
        
        # Analyze functions
        functions = parse_result.get_functions()
        function_info = [self._analyze_function(func) for func in functions]
        
        # Analyze imports
        imports = parse_result.get_imports()
        import_info = [self._analyze_import(imp) for imp in imports]
        
        # Calculate metrics
        complexity_score = self._calculate_complexity(all_nodes)
        maintainability_score = self._calculate_maintainability(
            all_nodes, function_info, class_info
        )
        
        # Function metrics
        function_lengths = [f['line_count'] for f in function_info]
        avg_function_length = sum(function_lengths) / len(function_lengths) if function_lengths else 0
        max_function_length = max(function_lengths) if function_lengths else 0
        
        # Class metrics
        class_sizes = [c['method_count'] for c in class_info]
        avg_class_size = sum(class_sizes) / len(class_sizes) if class_sizes else 0
        max_class_size = max(class_sizes) if class_sizes else 0
        
        # Nesting depth
        nesting_depth = self._calculate_max_nesting_depth(all_nodes)
        
        # Dependencies
        internal_deps, external_deps = self._extract_dependencies(import_info)
        
        # Quality indicators
        docstring_info = self._analyze_docstring_coverage(all_nodes)
        type_hint_info = self._analyze_type_hint_coverage(all_nodes, parse_result.language)
        
        return StructureAnalysis(
            file_path=parse_result.file_path,
            language=parse_result.language,
            total_nodes=len(all_nodes),
            complexity_score=complexity_score,
            maintainability_score=maintainability_score,
            classes=node_counts.get(NodeType.CLASS, 0),
            functions=node_counts.get(NodeType.FUNCTION, 0),
            methods=node_counts.get(NodeType.METHOD, 0),
            imports=node_counts.get(NodeType.IMPORT, 0),
            variables=node_counts.get(NodeType.VARIABLE, 0),
            class_info=class_info,
            function_info=function_info,
            import_info=import_info,
            average_function_length=avg_function_length,
            max_function_length=max_function_length,
            average_class_size=avg_class_size,
            max_class_size=max_class_size,
            nesting_depth=nesting_depth,
            internal_dependencies=internal_deps,
            external_dependencies=external_deps,
            **docstring_info,
            **type_hint_info
        )
    
    def _count_nodes_by_type(self, nodes: List[ASTNode]) -> Dict[NodeType, int]:
        """Count nodes by type."""
        return Counter(node.node_type for node in nodes)
    
    def _analyze_class(self, class_node: ASTNode) -> Dict[str, Any]:
        """Analyze a class node."""
        methods = class_node.get_children_by_type(NodeType.METHOD)
        variables = class_node.get_children_by_type(NodeType.VARIABLE)
        
        return {
            'name': class_node.name,
            'line_start': class_node.line_start,
            'line_end': class_node.line_end,
            'line_count': class_node.line_count,
            'method_count': len(methods),
            'variable_count': len(variables),
            'methods': [m.name for m in methods],
            'base_classes': class_node.metadata.get('base_classes', []),
            'decorators': class_node.metadata.get('decorators', []),
            'has_docstring': bool(class_node.metadata.get('docstring')),
            'is_exported': class_node.metadata.get('is_exported', False)
        }
    
    def _analyze_function(self, func_node: ASTNode) -> Dict[str, Any]:
        """Analyze a function/method node."""
        return {
            'name': func_node.name,
            'full_name': func_node.full_name,
            'line_start': func_node.line_start,
            'line_end': func_node.line_end,
            'line_count': func_node.line_count,
            'is_method': func_node.node_type == NodeType.METHOD,
            'is_async': func_node.metadata.get('is_async', False),
            'is_generator': func_node.metadata.get('is_generator', False),
            'parameters': func_node.metadata.get('parameters', []),
            'parameter_count': len(func_node.metadata.get('parameters', [])),
            'decorators': func_node.metadata.get('decorators', []),
            'has_docstring': bool(func_node.metadata.get('docstring')),
            'complexity': func_node.metadata.get('complexity', 1),
            'return_annotation': func_node.metadata.get('return_annotation'),
            'is_exported': func_node.metadata.get('is_exported', False)
        }
    
    def _analyze_import(self, import_node: ASTNode) -> Dict[str, Any]:
        """Analyze an import node."""
        return {
            'name': import_node.name,
            'line': import_node.line_start,
            'type': import_node.metadata.get('type', 'import'),
            'module': import_node.metadata.get('module'),
            'names': import_node.metadata.get('names', []),
            'is_from_import': import_node.metadata.get('type') == 'from_import',
            'is_relative': import_node.metadata.get('level', 0) > 0
        }
    
    def _calculate_complexity(self, nodes: List[ASTNode]) -> int:
        """Calculate overall complexity score."""
        complexity = 1  # Base complexity
        
        for node in nodes:
            # Add complexity for control flow
            if node.node_type == NodeType.CONTROL_FLOW:
                complexity += 1
            
            # Add complexity from function metadata
            elif node.node_type in (NodeType.FUNCTION, NodeType.METHOD):
                func_complexity = node.metadata.get('complexity', 1)
                complexity += func_complexity - 1  # Subtract base complexity
        
        return complexity
    
    def _calculate_maintainability(
        self,
        nodes: List[ASTNode],
        function_info: List[Dict[str, Any]],
        class_info: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate maintainability score (0-100).
        
        Based on various factors including:
        - Function/method length
        - Complexity
        - Documentation coverage
        - Naming conventions
        """
        if not nodes:
            return 100.0
        
        score = 100.0
        
        # Penalize long functions
        long_functions = [f for f in function_info if f['line_count'] > 50]
        score -= len(long_functions) * 5
        
        # Penalize high complexity functions
        complex_functions = [f for f in function_info if f['complexity'] > 10]
        score -= len(complex_functions) * 10
        
        # Reward documentation
        documented_functions = [f for f in function_info if f['has_docstring']]
        if function_info:
            doc_ratio = len(documented_functions) / len(function_info)
            score += doc_ratio * 10
        
        # Penalize large classes
        large_classes = [c for c in class_info if c['method_count'] > 20]
        score -= len(large_classes) * 5
        
        # Ensure score stays within bounds
        return max(0.0, min(100.0, score))
    
    def _calculate_max_nesting_depth(self, nodes: List[ASTNode]) -> int:
        """Calculate maximum nesting depth."""
        max_depth = 0
        
        for node in nodes:
            depth = 0
            current = node.parent
            while current and current.node_type != NodeType.MODULE:
                depth += 1
                current = current.parent
            max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _extract_dependencies(self, import_info: List[Dict[str, Any]]) -> Tuple[Set[str], Set[str]]:
        """Extract internal and external dependencies."""
        internal_deps = set()
        external_deps = set()
        
        for imp in import_info:
            module = imp.get('module', '')
            
            # Heuristic: modules starting with '.' or containing project-specific terms are internal
            if imp.get('is_relative') or not module:
                continue
            
            # Common external packages
            external_patterns = [
                'numpy', 'pandas', 'matplotlib', 'requests', 'django', 'flask',
                'react', 'vue', 'angular', 'lodash', 'axios', 'express'
            ]
            
            is_external = any(pattern in module.lower() for pattern in external_patterns)
            
            if is_external:
                external_deps.add(module.split('.')[0])  # Get root module
            else:
                internal_deps.add(module)
        
        return internal_deps, external_deps
    
    def _analyze_docstring_coverage(self, nodes: List[ASTNode]) -> Dict[str, Any]:
        """Analyze docstring coverage."""
        documentable_nodes = [
            node for node in nodes
            if node.node_type in (NodeType.CLASS, NodeType.FUNCTION, NodeType.METHOD)
        ]
        
        if not documentable_nodes:
            return {
                'has_docstrings': False,
                'docstring_coverage': 0.0
            }
        
        documented_nodes = [
            node for node in documentable_nodes
            if node.metadata.get('docstring')
        ]
        
        coverage = len(documented_nodes) / len(documentable_nodes)
        
        return {
            'has_docstrings': len(documented_nodes) > 0,
            'docstring_coverage': coverage
        }
    
    def _analyze_type_hint_coverage(self, nodes: List[ASTNode], language: str) -> Dict[str, Any]:
        """Analyze type hint coverage (primarily for Python and TypeScript)."""
        if language not in ['python', 'typescript']:
            return {
                'has_type_hints': False,
                'type_hint_coverage': 0.0
            }
        
        functions = [
            node for node in nodes
            if node.node_type in (NodeType.FUNCTION, NodeType.METHOD)
        ]
        
        if not functions:
            return {
                'has_type_hints': False,
                'type_hint_coverage': 0.0
            }
        
        type_hinted_functions = []
        for func in functions:
            params = func.metadata.get('parameters', [])
            has_return_annotation = bool(func.metadata.get('return_annotation'))
            has_param_annotations = any(p.get('annotation') for p in params if isinstance(p, dict))
            
            if has_return_annotation or has_param_annotations:
                type_hinted_functions.append(func)
        
        coverage = len(type_hinted_functions) / len(functions)
        
        return {
            'has_type_hints': len(type_hinted_functions) > 0,
            'type_hint_coverage': coverage
        }
    
    def find_code_smells(self, analysis: StructureAnalysis) -> List[Dict[str, Any]]:
        """
        Identify potential code smells and issues.
        
        Args:
            analysis: Structure analysis result
            
        Returns:
            List of identified code smells
        """
        smells = []
        
        # Long functions
        long_functions = [f for f in analysis.function_info if f['line_count'] > 50]
        for func in long_functions:
            smells.append({
                'type': 'long_function',
                'severity': 'medium',
                'message': f"Function '{func['name']}' is {func['line_count']} lines long",
                'location': f"Line {func['line_start']}",
                'suggestion': "Consider breaking this function into smaller, more focused functions"
            })
        
        # High complexity functions
        complex_functions = [f for f in analysis.function_info if f['complexity'] > 10]
        for func in complex_functions:
            smells.append({
                'type': 'high_complexity',
                'severity': 'high',
                'message': f"Function '{func['name']}' has complexity {func['complexity']}",
                'location': f"Line {func['line_start']}",
                'suggestion': "Reduce complexity by extracting logic into separate functions"
            })
        
        # Large classes
        large_classes = [c for c in analysis.class_info if c['method_count'] > 20]
        for cls in large_classes:
            smells.append({
                'type': 'large_class',
                'severity': 'medium',
                'message': f"Class '{cls['name']}' has {cls['method_count']} methods",
                'location': f"Line {cls['line_start']}",
                'suggestion': "Consider splitting this class following Single Responsibility Principle"
            })
        
        # Functions with many parameters
        parameter_heavy = [f for f in analysis.function_info if f['parameter_count'] > 6]
        for func in parameter_heavy:
            smells.append({
                'type': 'too_many_parameters',
                'severity': 'medium',
                'message': f"Function '{func['name']}' has {func['parameter_count']} parameters",
                'location': f"Line {func['line_start']}",
                'suggestion': "Consider using objects or data structures to group related parameters"
            })
        
        # Low documentation coverage
        if analysis.docstring_coverage < 0.5 and analysis.docstring_coverage > 0:
            smells.append({
                'type': 'poor_documentation',
                'severity': 'low',
                'message': f"Low documentation coverage: {analysis.docstring_coverage:.1%}",
                'location': "File level",
                'suggestion': "Add docstrings to classes and functions"
            })
        
        return smells
    
    def generate_summary(self, analysis: StructureAnalysis) -> Dict[str, Any]:
        """Generate a summary of the analysis."""
        return {
            'overview': {
                'file': analysis.file_path,
                'language': analysis.language,
                'total_lines': analysis.function_info[-1]['line_end'] if analysis.function_info else 0,
                'total_nodes': analysis.total_nodes
            },
            'structure': {
                'classes': analysis.classes,
                'functions': analysis.functions,
                'methods': analysis.methods,
                'imports': analysis.imports
            },
            'quality_metrics': {
                'complexity_score': analysis.complexity_score,
                'maintainability_score': analysis.maintainability_score,
                'docstring_coverage': f"{analysis.docstring_coverage:.1%}",
                'type_hint_coverage': f"{analysis.type_hint_coverage:.1%}"
            },
            'size_metrics': {
                'average_function_length': f"{analysis.average_function_length:.1f} lines",
                'max_function_length': f"{analysis.max_function_length} lines",
                'average_class_size': f"{analysis.average_class_size:.1f} methods",
                'nesting_depth': analysis.nesting_depth
            },
            'dependencies': {
                'internal_count': len(analysis.internal_dependencies),
                'external_count': len(analysis.external_dependencies)
            }
        }
