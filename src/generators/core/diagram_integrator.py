"""
Diagram integration module.

Implements IDiagramIntegrator interface for diagram generation and embedding.
Follows Single Responsibility Principle - only handles diagrams.
"""

import logging
from typing import Optional

from src.generators.base_generator import IDiagramIntegrator
from src.schemas import CodeAnalysisResult
from src.diagrams.mermaid_generator import MermaidGenerator
from src.diagrams.architecture_diagrams import ArchitectureDiagramGenerator

logger = logging.getLogger(__name__)


class DiagramIntegrator(IDiagramIntegrator):
    """
    Integrates diagram generation into documentation.

    This class is responsible ONLY for diagram operations.
    Content generation and formatting are handled by other classes (SRP).
    """

    def __init__(self):
        """Initialize diagram generators."""
        try:
            self.mermaid_generator = MermaidGenerator()
            self.arch_generator = ArchitectureDiagramGenerator()
        except Exception as e:
            logger.warning(f"Failed to initialize diagram generators: {e}")
            self.mermaid_generator = None
            self.arch_generator = None

    def generate_architecture_diagram(
        self, analysis: CodeAnalysisResult, format: str = "mermaid"
    ) -> str:
        """
        Generate architecture diagram.

        Args:
            analysis: Code analysis results
            format: Diagram format (mermaid, plantuml, etc.)

        Returns:
            str: Diagram content
        """
        if format != "mermaid" or not self.mermaid_generator:
            return ""

        try:
            # Create a simple architecture diagram based on analysis
            diagram = "graph TD\n"

            # Add main components
            if analysis.frameworks:
                for i, framework in enumerate(analysis.frameworks[:5]):
                    diagram += f"    {chr(65 + i)}[{framework}]\n"

            # Add database if present
            if analysis.database_info:
                db_info = analysis.database_info
                db_type = db_info.get('type', 'Database') if isinstance(db_info, dict) else 'Database'
                diagram += f"    DB[(Base}]]\n"
                diagram += f"    A --> DB\n"

            # Add API layer if present
            if analysis.api_endpoints:
                diagram += f"    API[API Layer]\n"
                diagram += f"    A --> API\n"

            return diagram

        except Exception as e:
            logger.error(f"Failed to generate architecture diagram: {e}")
            return ""

    def generate_database_diagram(
        self, analysis: CodeAnalysisResult, format: str = "mermaid"
    ) -> str:
        """
        Generate database schema diagram.

        Args:
            analysis: Code analysis results
            format: Diagram format

        Returns:
            str: Diagram content
        """
        if format != "mermaid" or not self.mermaid_generator:
            return ""

        if not analysis.database_info:
            return ""

        try:
            db_info = analysis.database_info
            if not isinstance(db_info, dict):
                return ""

            diagram = "erDiagram\n"

            # Add tables if available
            tables = db_info.get('tables', [])
            for table in tables[:10]:  # Limit to 10 tables
                if isinstance(table, str):
                    diagram += f"    {table} {{\n"
                    diagram += f"        int id\n"
                    diagram += f"        string name\n"
                    diagram += f"    }}\n"
                elif isinstance(table, dict):
                    table_name = table.get('name', 'Unknown')
                    diagram += f"    {table_name} {{\n"
                    columns = table.get('columns', [])
                    for col in columns[:5]:  # Limit columns
                        if isinstance(col, dict):
                            col_name = col.get('name', 'column')
                            col_type = col.get('type', 'string')
                            diagram += f"        {col_type} {col_name}\n"
                    diagram += f"    }}\n"

            return diagram

        except Exception as e:
            logger.error(f"Failed to generate database diagram: {e}")
            return ""

    def generate_workflow_diagram(self, analysis: CodeAnalysisResult) -> str:
        """
        Generate workflow/sequence diagram.

        Args:
            analysis: Code analysis results

        Returns:
            str: Diagram content
        """
        if not self.mermaid_generator:
            return ""

        try:
            diagram = "sequenceDiagram\n"
            diagram += "    participant User\n"
            diagram += "    participant App\n"

            if analysis.database_info:
                diagram += "    participant DB\n"

            if analysis.api_endpoints:
                diagram += "    participant API\n"
                diagram += "    User->>API: Request\n"
                diagram += "    API->>App: Process\n"
                if analysis.database_info:
                    diagram += "    App->>DB: Query\n"
                    diagram += "    DB-->>App: Result\n"
                diagram += "    App-->>API: Response\n"
                diagram += "    API-->>User: Data\n"
            else:
                diagram += "    User->>App: Interaction\n"
                if analysis.database_info:
                    diagram += "    App->>DB: Query\n"
                    diagram += "    DB-->>App: Data\n"
                diagram += "    App-->>User: Response\n"

            return diagram

        except Exception as e:
            logger.error(f"Failed to generate workflow diagram: {e}")
            return ""

    def embed_diagram(self, diagram_content: str, caption: Optional[str] = None) -> str:
        """
        Embed diagram into documentation.

        Args:
            diagram_content: Diagram content (Mermaid code)
            caption: Optional diagram caption

        Returns:
            str: Embedded diagram markup
        """
        if not diagram_content:
            return ""

        parts = []

        # Add caption if provided
        if caption:
            parts.append(f"**{caption}**\n")

        # Embed Mermaid diagram
        parts.append("```mermaid")
        parts.append(diagram_content)
        parts.append("```\n")

        return "\n".join(parts)

    def create_flowchart(
        self,
        title: str,
        nodes: list[tuple[str, str]],
        edges: list[tuple[str, str]]
    ) -> str:
        """
        Create a flowchart diagram.

        Args:
            title: Flowchart title
            nodes: List of (id, label) tuples
            edges: List of (from_id, to_id) tuples

        Returns:
            str: Mermaid flowchart code
        """
        diagram = ["graph TD"]

        # Add nodes
        for node_id, label in nodes:
            diagram.append(f"    {node_id}[{label}]")

        # Add edges
        for from_id, to_id in edges:
            diagram.append(f"    {from_id} --> {to_id}")

        return "\n".join(diagram)

    def is_available(self) -> bool:
        """
        Check if diagram generation is available.

        Returns:
            bool: True if diagram generators are initialized
        """
        return self.mermaid_generator is not None or self.arch_generator is not None
