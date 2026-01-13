"""
Base generator module defining interfaces for all documentation generators.

This module implements the Strategy and Template Method patterns to provide
a flexible, extensible documentation generation system following SOLID principles.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pathlib import Path

from src.schemas import DocumentationResult, DocumentationFormat, CodeAnalysisResult


class IContentGenerator(ABC):
    """
    Interface for content generation.

    Implementations generate structured documentation content from analysis results.
    Follows Interface Segregation Principle - focused on content generation only.
    """

    @abstractmethod
    def generate_overview(self, analysis: CodeAnalysisResult) -> str:
        """
        Generate project overview section.

        Args:
            analysis: Code analysis results

        Returns:
            str: Formatted overview content
        """
        pass

    @abstractmethod
    def generate_architecture_section(self, analysis: CodeAnalysisResult) -> str:
        """
        Generate architecture description section.

        Args:
            analysis: Code analysis results

        Returns:
            str: Formatted architecture content
        """
        pass

    @abstractmethod
    def generate_file_structure(self, analysis: CodeAnalysisResult) -> str:
        """
        Generate file structure documentation.

        Args:
            analysis: Code analysis results

        Returns:
            str: Formatted file structure content
        """
        pass

    @abstractmethod
    def generate_code_analysis(self, analysis: CodeAnalysisResult) -> str:
        """
        Generate code analysis section.

        Args:
            analysis: Code analysis results

        Returns:
            str: Formatted code analysis content
        """
        pass


class IFormatter(ABC):
    """
    Interface for content formatting.

    Implementations format content into specific markup languages.
    Follows Open/Closed Principle - new formatters can be added without modification.
    """

    @abstractmethod
    def format_heading(self, text: str, level: int = 1) -> str:
        """
        Format a heading at the specified level.

        Args:
            text: Heading text
            level: Heading level (1-6)

        Returns:
            str: Formatted heading
        """
        pass

    @abstractmethod
    def format_paragraph(self, text: str) -> str:
        """
        Format a paragraph of text.

        Args:
            text: Paragraph content

        Returns:
            str: Formatted paragraph
        """
        pass

    @abstractmethod
    def format_code_block(self, code: str, language: Optional[str] = None) -> str:
        """
        Format a code block with optional syntax highlighting.

        Args:
            code: Code content
            language: Programming language for syntax highlighting

        Returns:
            str: Formatted code block
        """
        pass

    @abstractmethod
    def format_list(self, items: List[str], ordered: bool = False) -> str:
        """
        Format a list of items.

        Args:
            items: List items
            ordered: Whether the list should be ordered (numbered)

        Returns:
            str: Formatted list
        """
        pass

    @abstractmethod
    def format_table(self, headers: List[str], rows: List[List[str]]) -> str:
        """
        Format a table with headers and rows.

        Args:
            headers: Table header labels
            rows: Table row data

        Returns:
            str: Formatted table
        """
        pass


class IDiagramIntegrator(ABC):
    """
    Interface for diagram integration.

    Implementations generate and embed diagrams into documentation.
    Follows Single Responsibility Principle - handles only diagram operations.
    """

    @abstractmethod
    def generate_architecture_diagram(
        self, analysis: CodeAnalysisResult, format: str = "mermaid"
    ) -> str:
        """
        Generate architecture diagram.

        Args:
            analysis: Code analysis results
            format: Diagram format (mermaid, plantuml, etc.)

        Returns:
            str: Diagram content or path
        """
        pass

    @abstractmethod
    def generate_database_diagram(
        self, analysis: CodeAnalysisResult, format: str = "mermaid"
    ) -> str:
        """
        Generate database schema diagram.

        Args:
            analysis: Code analysis results
            format: Diagram format

        Returns:
            str: Diagram content or path
        """
        pass

    @abstractmethod
    def embed_diagram(self, diagram_content: str, caption: Optional[str] = None) -> str:
        """
        Embed diagram into documentation.

        Args:
            diagram_content: Diagram content or path
            caption: Optional diagram caption

        Returns:
            str: Embedded diagram markup
        """
        pass


class IThemeManager(ABC):
    """
    Interface for theme management.

    Implementations provide theming and styling capabilities.
    Follows Liskov Substitution Principle - all themes are interchangeable.
    """

    @abstractmethod
    def load_theme(self, theme_name: str) -> Dict[str, Any]:
        """
        Load theme configuration.

        Args:
            theme_name: Name of the theme to load

        Returns:
            dict: Theme configuration

        Raises:
            ValueError: If theme not found
        """
        pass

    @abstractmethod
    def apply_theme(self, content: str, theme_config: Dict[str, Any]) -> str:
        """
        Apply theme styling to content.

        Args:
            content: Content to style
            theme_config: Theme configuration

        Returns:
            str: Styled content
        """
        pass

    @abstractmethod
    def get_css(self, theme_config: Dict[str, Any]) -> str:
        """
        Get CSS stylesheet for theme.

        Args:
            theme_config: Theme configuration

        Returns:
            str: CSS content
        """
        pass


class IExporter(ABC):
    """
    Interface for documentation exporters.

    Implementations export documentation to various formats.
    Follows Dependency Inversion Principle - depend on abstraction, not concretions.
    """

    @abstractmethod
    def export(
        self,
        content: str,
        output_path: Path,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Export content to file.

        Args:
            content: Documentation content
            output_path: Output file path
            metadata: Optional metadata for export

        Returns:
            bool: True if export successful

        Raises:
            ExportError: If export fails
        """
        pass

    @abstractmethod
    def validate_output(self, output_path: Path) -> bool:
        """
        Validate exported output.

        Args:
            output_path: Path to exported file

        Returns:
            bool: True if output is valid
        """
        pass


class BaseDocumentationGenerator(ABC):
    """
    Abstract base class for all documentation generators.

    This class implements the Template Method pattern, defining the skeleton
    of the documentation generation algorithm while allowing subclasses to
    override specific steps.

    Follows SOLID principles:
    - Single Responsibility: Coordinates generation workflow
    - Open/Closed: Open for extension via abstract methods, closed for modification
    - Liskov Substitution: Subclasses can be used interchangeably
    - Interface Segregation: Depends on focused interfaces (I*)
    - Dependency Inversion: Depends on abstractions (interfaces), not concretions

    Attributes:
        content_generator: Content generation implementation
        formatter: Formatting implementation
        diagram_integrator: Diagram integration implementation (optional)
        theme_manager: Theme management implementation (optional)
    """

    def __init__(
        self,
        content_generator: IContentGenerator,
        formatter: IFormatter,
        diagram_integrator: Optional[IDiagramIntegrator] = None,
        theme_manager: Optional[IThemeManager] = None,
    ):
        """
        Initialize generator with dependencies via dependency injection.

        Args:
            content_generator: Content generation implementation
            formatter: Formatting implementation
            diagram_integrator: Optional diagram integration
            theme_manager: Optional theme management
        """
        self._content_generator = content_generator
        self._formatter = formatter
        self._diagram_integrator = diagram_integrator
        self._theme_manager = theme_manager

    @abstractmethod
    def generate(
        self,
        analysis: CodeAnalysisResult,
        config: Optional[Dict[str, Any]] = None
    ) -> DocumentationResult:
        """
        Generate documentation from analysis results.

        Template method that defines the overall generation workflow.
        Subclasses should implement specific generation logic.

        Args:
            analysis: Code analysis results
            config: Optional configuration

        Returns:
            DocumentationResult: Generated documentation

        Raises:
            GenerationError: If generation fails
        """
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[DocumentationFormat]:
        """
        Get list of supported documentation formats.

        Returns:
            List of supported formats
        """
        pass

    def _generate_sections(self, analysis: CodeAnalysisResult) -> List[str]:
        """
        Generate all documentation sections.

        Template method step that can be overridden by subclasses.

        Args:
            analysis: Code analysis results

        Returns:
            List of generated sections
        """
        sections = []

        # Generate core sections using content generator
        sections.append(self._content_generator.generate_overview(analysis))
        sections.append(self._content_generator.generate_architecture_section(analysis))
        sections.append(self._content_generator.generate_file_structure(analysis))
        sections.append(self._content_generator.generate_code_analysis(analysis))

        return sections

    def _integrate_diagrams(self, analysis: CodeAnalysisResult) -> List[str]:
        """
        Integrate diagrams into documentation.

        Args:
            analysis: Code analysis results

        Returns:
            List of diagram content
        """
        if not self._diagram_integrator:
            return []

        diagrams = []

        # Generate architecture diagram if applicable
        if analysis.frameworks or analysis.key_features:
            arch_diagram = self._diagram_integrator.generate_architecture_diagram(analysis)
            diagrams.append(self._diagram_integrator.embed_diagram(
                arch_diagram,
                caption="Project Architecture"
            ))

        # Generate database diagram if applicable
        if analysis.database_info:
            db_diagram = self._diagram_integrator.generate_database_diagram(analysis)
            diagrams.append(self._diagram_integrator.embed_diagram(
                db_diagram,
                caption="Database Schema"
            ))

        return diagrams

    def _apply_styling(
        self,
        content: str,
        theme_name: Optional[str] = "default"
    ) -> str:
        """
        Apply theme styling to content.

        Args:
            content: Content to style
            theme_name: Theme name

        Returns:
            Styled content
        """
        if not self._theme_manager:
            return content

        theme_config = self._theme_manager.load_theme(theme_name)
        return self._theme_manager.apply_theme(content, theme_config)


class GenerationError(Exception):
    """Exception raised when documentation generation fails."""

    pass


class ExportError(Exception):
    """Exception raised when documentation export fails."""

    pass
