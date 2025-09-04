"""
Mermaid diagram generator for various architecture and relationship diagrams.

This module provides comprehensive mermaid diagram generation capabilities
for codebases, including dependency graphs, architecture diagrams, and more.
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class DiagramType(Enum):
    """Types of mermaid diagrams that can be generated."""
    FLOWCHART = "flowchart"
    CLASS_DIAGRAM = "classDiagram"
    ENTITY_RELATIONSHIP = "erDiagram"
    SEQUENCE = "sequenceDiagram"
    GITGRAPH = "gitgraph"
    DEPENDENCY_GRAPH = "graph"
    ARCHITECTURE = "C4Context"
    USER_JOURNEY = "journey"
    GANTT = "gantt"


@dataclass
class MermaidNode:
    """Represents a node in a mermaid diagram."""
    id: str
    label: str
    shape: str = "rect"  # rect, round, circle, diamond, etc.
    style_class: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class MermaidEdge:
    """Represents an edge/relationship in a mermaid diagram."""
    from_node: str
    to_node: str
    label: str = ""
    style: str = "solid"  # solid, dashed, dotted
    arrow: str = "arrow"  # arrow, none, circle
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MermaidGenerator:
    """
    Generator for mermaid diagrams from codebase analysis data.
    
    Supports multiple diagram types including flowcharts, class diagrams,
    dependency graphs, and architecture diagrams.
    """
    
    def __init__(self):
        self.style_classes = {
            'module': 'fill:#e1f5fe,stroke:#01579b,stroke-width:2px',
            'class': 'fill:#f3e5f5,stroke:#4a148c,stroke-width:2px', 
            'function': 'fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px',
            'database': 'fill:#fff3e0,stroke:#e65100,stroke-width:2px',
            'api': 'fill:#fce4ec,stroke:#880e4f,stroke-width:2px',
            'external': 'fill:#f1f8e9,stroke:#33691e,stroke-width:2px',
            'test': 'fill:#fff8e1,stroke:#ff6f00,stroke-width:2px'
        }
    
    def generate_dependency_graph(
        self,
        dependencies: Dict[str, List[str]],
        title: str = "Dependency Graph"
    ) -> str:
        """Generate a mermaid dependency graph from dependency data."""
        
        nodes = set()
        edges = []
        
        # Collect all nodes and edges
        for module, deps in dependencies.items():
            nodes.add(module)
            for dep in deps:
                nodes.add(dep)
                edges.append(MermaidEdge(
                    from_node=self._sanitize_id(module),
                    to_node=self._sanitize_id(dep),
                    label="depends on"
                ))
        
        # Generate mermaid syntax
        lines = [
            "graph TD",
            f"    title[\"{title}\"]"
        ]
        
        # Add nodes with styling
        for node in sorted(nodes):
            node_id = self._sanitize_id(node)
            node_label = self._format_label(node)
            
            # Determine node type and styling
            if self._is_external_dependency(node):
                lines.append(f"    {node_id}[{node_label}]:::external")
            elif self._is_test_module(node):
                lines.append(f"    {node_id}[{node_label}]:::test")
            else:
                lines.append(f"    {node_id}[{node_label}]:::module")
        
        # Add edges
        for edge in edges:
            lines.append(f"    {edge.from_node} --> {edge.to_node}")
        
        # Add styling
        lines.extend([
            "",
            "    classDef external " + self.style_classes['external'],
            "    classDef module " + self.style_classes['module'],
            "    classDef test " + self.style_classes['test']
        ])
        
        return "\n".join(lines)
    
    def generate_class_diagram(
        self,
        classes: List[Dict[str, Any]],
        title: str = "Class Diagram"
    ) -> str:
        """Generate a mermaid class diagram from class analysis data."""
        
        lines = [
            "classDiagram",
            f"    title {title}"
        ]
        
        # Add classes
        for cls in classes:
            class_name = cls.get('name', 'Unknown')
            methods = cls.get('methods', [])
            fields = cls.get('fields', [])
            base_classes = cls.get('base_classes', [])
            
            # Add class definition
            lines.append(f"    class {class_name} {{")
            
            # Add fields/attributes
            for field in fields:
                field_type = field.get('data_type', 'any')
                field_name = field.get('name', 'unknown')
                visibility = '+' if field.get('public', True) else '-'
                lines.append(f"        {visibility}{field_name}: {field_type}")
            
            # Add methods
            for method in methods:
                method_name = method.get('name', 'unknown')
                params = method.get('parameters', [])
                return_type = method.get('return_type', 'void')
                visibility = '+' if method.get('public', True) else '-'
                
                param_str = ', '.join([
                    f"{p.get('name', 'param')}: {p.get('type', 'any')}"
                    for p in params if isinstance(p, dict)
                ])
                
                lines.append(f"        {visibility}{method_name}({param_str}): {return_type}")
            
            lines.append("    }")
            
            # Add inheritance relationships
            for base_class in base_classes:
                lines.append(f"    {base_class} <|-- {class_name}")
        
        return "\n".join(lines)
    
    def generate_architecture_diagram(
        self,
        components: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]],
        title: str = "Architecture Diagram"
    ) -> str:
        """Generate an architecture flowchart diagram."""
        
        lines = [
            "flowchart TB",
            f"    title[\"{title}\"]"
        ]
        
        # Add components
        for component in components:
            comp_id = self._sanitize_id(component.get('name', 'unknown'))
            comp_label = self._format_label(component.get('name', 'unknown'))
            comp_type = component.get('type', 'module')
            
            # Choose shape based on component type
            if comp_type == 'database':
                lines.append(f"    {comp_id}[(Database<br/>{comp_label})]:::database")
            elif comp_type == 'api':
                lines.append(f"    {comp_id}[API<br/>{comp_label}]:::api")
            elif comp_type == 'frontend':
                lines.append(f"    {comp_id}[Frontend<br/>{comp_label}]:::frontend")
            elif comp_type == 'service':
                lines.append(f"    {comp_id}[Service<br/>{comp_label}]:::service")
            else:
                lines.append(f"    {comp_id}[{comp_label}]:::module")
        
        # Add relationships
        for rel in relationships:
            from_comp = self._sanitize_id(rel.get('from', 'unknown'))
            to_comp = self._sanitize_id(rel.get('to', 'unknown'))
            rel_type = rel.get('type', 'depends')
            rel_label = rel.get('label', rel_type)
            
            if rel_type == 'api_call':
                lines.append(f"    {from_comp} -->|{rel_label}| {to_comp}")
            elif rel_type == 'data_flow':
                lines.append(f"    {from_comp} -.->|{rel_label}| {to_comp}")
            else:
                lines.append(f"    {from_comp} --> {to_comp}")
        
        # Add styling
        lines.extend([
            "",
            "    classDef database " + self.style_classes['database'],
            "    classDef api " + self.style_classes['api'],
            "    classDef module " + self.style_classes['module'],
            "    classDef frontend fill:#e8eaf6,stroke:#3f51b5,stroke-width:2px",
            "    classDef service fill:#e0f2f1,stroke:#00695c,stroke-width:2px"
        ])
        
        return "\n".join(lines)
    
    def generate_database_er_diagram(
        self,
        tables: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]],
        title: str = "Database Schema"
    ) -> str:
        """Generate a mermaid ER diagram from database schema."""
        
        lines = [
            "erDiagram",
            f"    title {title}"
        ]
        
        # Add tables
        for table in tables:
            table_name = table.get('name', 'unknown').upper()
            fields = table.get('fields', [])
            
            lines.append(f"    {table_name} {{")
            
            for field in fields:
                field_name = field.get('name', 'unknown')
                field_type = field.get('data_type', 'string').upper()
                
                # Add constraints
                constraints = []
                if field.get('primary_key'):
                    constraints.append('PK')
                if field.get('foreign_key'):
                    constraints.append('FK')
                if field.get('unique'):
                    constraints.append('UK')
                if not field.get('nullable', True):
                    constraints.append('NOT NULL')
                
                constraint_str = f" \"{', '.join(constraints)}\"" if constraints else ""
                lines.append(f"        {field_type} {field_name}{constraint_str}")
            
            lines.append("    }")
        
        # Add relationships
        for rel in relationships:
            from_table = rel.get('from_table', '').upper()
            to_table = rel.get('to_table', '').upper()
            rel_type = rel.get('relationship_type', 'one_to_many')
            
            if rel_type == 'one_to_one':
                lines.append(f"    {from_table} ||--|| {to_table} : has")
            elif rel_type == 'one_to_many':
                lines.append(f"    {from_table} ||--o{{ {to_table} : has")
            elif rel_type == 'many_to_many':
                lines.append(f"    {from_table} }}o--o{{ {to_table} : relates")
            else:
                lines.append(f"    {from_table} ---> {to_table} : references")
        
        return "\n".join(lines)
    
    def generate_file_structure_diagram(
        self,
        file_structure: Dict[str, Any],
        title: str = "Project Structure",
        max_depth: int = 3
    ) -> str:
        """Generate a diagram showing project file structure."""
        
        lines = [
            "flowchart TD",
            f"    title[\"{title}\"]"
        ]
        
        def add_directory(path: str, content: Dict[str, Any], depth: int = 0):
            if depth > max_depth:
                return
            
            dir_id = self._sanitize_id(path)
            dir_label = Path(path).name or "root"
            
            # Add directory node
            lines.append(f"    {dir_id}[📁 {dir_label}]:::directory")
            
            # Add files and subdirectories
            for name, item in content.items():
                item_path = f"{path}/{name}" if path != "root" else name
                item_id = self._sanitize_id(item_path)
                
                if isinstance(item, dict):
                    # Subdirectory
                    add_directory(item_path, item, depth + 1)
                    lines.append(f"    {dir_id} --> {item_id}")
                else:
                    # File
                    file_ext = Path(name).suffix
                    file_icon = self._get_file_icon(file_ext)
                    lines.append(f"    {item_id}[{file_icon} {name}]:::file")
                    lines.append(f"    {dir_id} --> {item_id}")
        
        # Process file structure
        if isinstance(file_structure, dict):
            add_directory("root", file_structure)
        
        # Add styling
        lines.extend([
            "",
            "    classDef directory fill:#e3f2fd,stroke:#0277bd,stroke-width:2px",
            "    classDef file fill:#f9fbe7,stroke:#827717,stroke-width:1px"
        ])
        
        return "\n".join(lines)
    
    def generate_api_flow_diagram(
        self,
        endpoints: List[Dict[str, Any]],
        title: str = "API Flow Diagram"
    ) -> str:
        """Generate a sequence diagram showing API interactions."""
        
        lines = [
            "sequenceDiagram",
            f"    title {title}",
            "    participant C as Client",
            "    participant API as API Server",
            "    participant DB as Database"
        ]
        
        for endpoint in endpoints:
            method = endpoint.get('method', 'GET').upper()
            path = endpoint.get('path', '/unknown')
            
            lines.extend([
                f"    C->>+API: {method} {path}",
                "    API->>+DB: Query data",
                "    DB-->>-API: Return results",
                "    API-->>-C: JSON Response"
            ])
        
        return "\n".join(lines)
    
    def generate_git_workflow_diagram(
        self,
        branches: List[str],
        title: str = "Git Workflow"
    ) -> str:
        """Generate a git graph diagram."""
        
        lines = [
            "gitgraph",
            f"    title: {title}",
            "    commit id: \"Initial commit\"",
            "    branch develop",
            "    commit id: \"Setup project\""
        ]
        
        for branch in branches:
            if branch not in ['main', 'master', 'develop']:
                lines.extend([
                    f"    branch {branch}",
                    f"    commit id: \"Feature: {branch}\"",
                    "    checkout develop",
                    f"    merge {branch}"
                ])
        
        lines.extend([
            "    checkout main",
            "    merge develop",
            "    commit id: \"Release\""
        ])
        
        return "\n".join(lines)
    
    def generate_user_journey_diagram(
        self,
        user_actions: List[Dict[str, Any]],
        title: str = "User Journey"
    ) -> str:
        """Generate a user journey diagram."""
        
        lines = [
            "journey",
            f"    title {title}",
            "    section Getting Started"
        ]
        
        for action in user_actions:
            action_name = action.get('name', 'Unknown Action')
            satisfaction = action.get('satisfaction', 3)  # 1-5 scale
            actors = action.get('actors', ['User'])
            
            actor_str = ', '.join(actors)
            lines.append(f"        {action_name}: {satisfaction}: {actor_str}")
        
        return "\n".join(lines)
    
    # Helper methods
    
    def _sanitize_id(self, name: str) -> str:
        """Sanitize name to be valid mermaid ID."""
        import re
        # Replace invalid characters with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', str(name))
        # Ensure it doesn't start with a number
        if sanitized and sanitized[0].isdigit():
            sanitized = f"_{sanitized}"
        return sanitized or "unknown"
    
    def _format_label(self, label: str) -> str:
        """Format label for display in diagrams."""
        # Truncate long labels
        if len(label) > 20:
            return f"{label[:17]}..."
        return label
    
    def _is_external_dependency(self, module_name: str) -> bool:
        """Check if a module is an external dependency."""
        external_indicators = [
            'numpy', 'pandas', 'requests', 'flask', 'django',
            'react', 'vue', 'angular', 'express', 'lodash'
        ]
        return any(indicator in module_name.lower() for indicator in external_indicators)
    
    def _is_test_module(self, module_name: str) -> bool:
        """Check if a module is a test module."""
        test_indicators = ['test', 'spec', '__tests__', '.test.', '.spec.']
        return any(indicator in module_name.lower() for indicator in test_indicators)
    
    def _get_file_icon(self, file_ext: str) -> str:
        """Get appropriate icon for file extension."""
        icon_map = {
            '.py': '🐍',
            '.js': '📜',
            '.ts': '📘',
            '.jsx': '⚛️',
            '.tsx': '⚛️',
            '.css': '🎨',
            '.html': '🌐',
            '.json': '📋',
            '.md': '📝',
            '.yml': '⚙️',
            '.yaml': '⚙️',
            '.sql': '🗃️',
            '.dockerfile': '🐳',
            '.gitignore': '🚫'
        }
        return icon_map.get(file_ext.lower(), '📄')
    
    def generate_github_repo_overview(
        self,
        repo_analysis: Dict[str, Any],
        title: Optional[str] = None
    ) -> str:
        """
        Generate a comprehensive mermaid diagram for a GitHub repository.
        
        Args:
            repo_analysis: Complete repository analysis data
            title: Optional custom title
            
        Returns:
            Mermaid diagram showing repository structure and relationships
        """
        repo_name = repo_analysis.get('name', 'Repository')
        if not title:
            title = f"{repo_name} - Repository Overview"
        
        # Extract components
        frameworks = repo_analysis.get('frameworks', [])
        dependencies = repo_analysis.get('dependencies', {})
        file_structure = repo_analysis.get('file_structure', {})
        
        # Create architecture components
        components = []
        relationships = []
        
        # Add main application component
        components.append({
            'name': repo_name,
            'type': 'application',
            'description': 'Main Application'
        })
        
        # Add framework components
        for framework in frameworks:
            framework_name = framework.get('name', 'Unknown')
            framework_type = framework.get('category', 'framework')
            
            components.append({
                'name': framework_name,
                'type': framework_type,
                'description': f"{framework_name} Framework"
            })
            
            relationships.append({
                'from': repo_name,
                'to': framework_name,
                'type': 'uses',
                'label': 'uses'
            })
        
        # Add database components
        databases = repo_analysis.get('databases', [])
        for db in databases:
            components.append({
                'name': db,
                'type': 'database',
                'description': f"{db} Database"
            })
            
            relationships.append({
                'from': repo_name,
                'to': db,
                'type': 'data_flow',
                'label': 'stores data'
            })
        
        # Add external dependencies
        external_deps = dependencies.get('external', [])[:5]  # Limit to top 5
        for dep in external_deps:
            components.append({
                'name': dep,
                'type': 'external',
                'description': f"External: {dep}"
            })
            
            relationships.append({
                'from': repo_name,
                'to': dep,
                'type': 'depends',
                'label': 'depends on'
            })
        
        return self.generate_architecture_diagram(components, relationships, title)
    
    def generate_multi_diagram_report(
        self,
        analysis_data: Dict[str, Any],
        diagrams_to_generate: List[DiagramType] = None
    ) -> Dict[str, str]:
        """
        Generate multiple types of diagrams from analysis data.
        
        Args:
            analysis_data: Complete analysis data
            diagrams_to_generate: List of diagram types to generate
            
        Returns:
            Dictionary mapping diagram type to mermaid code
        """
        if diagrams_to_generate is None:
            diagrams_to_generate = [
                DiagramType.ARCHITECTURE,
                DiagramType.DEPENDENCY_GRAPH,
                DiagramType.CLASS_DIAGRAM,
                DiagramType.ENTITY_RELATIONSHIP
            ]
        
        diagrams = {}
        
        for diagram_type in diagrams_to_generate:
            try:
                if diagram_type == DiagramType.ARCHITECTURE:
                    diagrams['architecture'] = self.generate_github_repo_overview(analysis_data)
                
                elif diagram_type == DiagramType.DEPENDENCY_GRAPH:
                    dependencies = analysis_data.get('dependencies', {})
                    if dependencies:
                        diagrams['dependencies'] = self.generate_dependency_graph(dependencies)
                
                elif diagram_type == DiagramType.CLASS_DIAGRAM:
                    classes = analysis_data.get('classes', [])
                    if classes:
                        diagrams['classes'] = self.generate_class_diagram(classes)
                
                elif diagram_type == DiagramType.ENTITY_RELATIONSHIP:
                    tables = analysis_data.get('database_tables', [])
                    relationships = analysis_data.get('database_relationships', [])
                    if tables:
                        diagrams['database'] = self.generate_database_er_diagram(tables, relationships)
                
            except Exception as e:
                logger.error(f"Failed to generate {diagram_type.value} diagram: {e}")
                diagrams[diagram_type.value] = f"```mermaid\ngraph TD\n    Error[\"Error generating {diagram_type.value}\"]\n```"
        
        return diagrams
