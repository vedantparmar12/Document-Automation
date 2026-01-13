"""
Refactored Professional Documentation Generator.

This module implements a clean, SOLID-compliant documentation generator
using dependency injection and modular components.

Follows SOLID principles:
- Single Responsibility: Orchestrates generation workflow
- Open/Closed: Extensible via injected dependencies
- Liskov Substitution: Uses interface-based dependencies
- Interface Segregation: Depends on focused interfaces
- Dependency Inversion: Depends on abstractions, not concretions
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from src.generators.base_generator import (
    BaseDocumentationGenerator,
    GenerationError,
    IContentGenerator,
    IFormatter,
    IDiagramIntegrator,
    IThemeManager,
    IExporter
)
from src.generators.core import (
    ContentGenerator,
    MarkdownFormatter,
    DiagramIntegrator,
    ThemeManager
)
from src.generators.exporters import HTMLExporter, PDFExporter
from src.schemas import DocumentationResult, DocumentationFormat, CodeAnalysisResult

logger = logging.getLogger(__name__)


class ProfessionalDocumentationGenerator(BaseDocumentationGenerator):
    """
    Generates professional, comprehensive documentation.

    This refactored version follows SOLID principles and uses dependency
    injection for all components. Each component has a single responsibility:
    - ContentGenerator: Generates content sections
    - MarkdownFormatter: Formats content as Markdown
    - DiagramIntegrator: Handles diagram generation
    - ThemeManager: Manages themes and styling
    - Exporters: Handle format-specific export

    Example:
        ```python
        # With default dependencies
        generator = ProfessionalDocumentationGenerator.create_default()

        # With custom dependencies (DI)
        generator = ProfessionalDocumentationGenerator(
            content_generator=MyContentGenerator(),
            formatter=MyFormatter(),
            diagram_integrator=MyDiagramIntegrator(),
            theme_manager=MyThemeManager()
        )

        # Generate documentation
        result = generator.generate(analysis)
        ```
    """

    def __init__(
        self,
        content_generator: Optional[IContentGenerator] = None,
        formatter: Optional[IFormatter] = None,
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
        # Use provided dependencies or create defaults
        content_gen = content_generator or ContentGenerator()
        fmt = formatter or MarkdownFormatter()
        diagram_int = diagram_integrator or DiagramIntegrator()
        theme_mgr = theme_manager or ThemeManager()

        super().__init__(content_gen, fmt, diagram_int, theme_mgr)

        # Initialize exporters
        self._html_exporter = HTMLExporter()
        self._pdf_exporter = PDFExporter(html_exporter=self._html_exporter)

    @classmethod
    def create_default(cls) -> 'ProfessionalDocumentationGenerator':
        """
        Factory method to create generator with default dependencies.

        Returns:
            ProfessionalDocumentationGenerator: Generator with default config
        """
        return cls()

    def generate(
        self,
        analysis: CodeAnalysisResult,
        config: Optional[Dict[str, Any]] = None
    ) -> DocumentationResult:
        """
        Generate professional documentation from analysis results.

        Args:
            analysis: Code analysis results
            config: Optional configuration
                - format: Output format (markdown, html, pdf)
                - theme: Theme name (default, dark, minimal, github)
                - include_diagrams: Whether to include diagrams (default: True)
                - include_toc: Whether to include table of contents (default: True)
                - output_path: Optional output file path

        Returns:
            DocumentationResult: Generated documentation

        Raises:
            GenerationError: If generation fails
        """
        config = config or {}

        try:
            logger.info(f"Generating documentation for {analysis.project_name}")

            # Extract configuration
            output_format = config.get('format', 'markdown')
            theme_name = config.get('theme', 'default')
            include_diagrams = config.get('include_diagrams', True)
            include_toc = config.get('include_toc', True)
            output_path = config.get('output_path')

            # Generate content sections
            sections = self._build_documentation_sections(
                analysis,
                include_diagrams=include_diagrams,
                include_toc=include_toc
            )

            # Format as Markdown
            markdown_content = self._format_as_markdown(sections, analysis)

            # Apply theme if needed (for HTML/PDF)
            if output_format in ['html', 'pdf']:
                theme_config = self._theme_manager.load_theme(theme_name)
                markdown_content = self._theme_manager.apply_theme(
                    markdown_content,
                    theme_config
                )

            # Create result
            result = DocumentationResult(
                format=self._get_format_enum(output_format),
                content=markdown_content,
                metadata={
                    'project_name': analysis.project_name,
                    'generated_at': datetime.now().isoformat(),
                    'generator': 'ProfessionalDocumentationGenerator',
                    'theme': theme_name,
                    'version': '2.0.0'
                },
                diagrams=[]
            )

            # Export if output path provided
            if output_path:
                self._export_documentation(result, Path(output_path), theme_name)
                result.export_path = str(output_path)

            logger.info("Documentation generation completed successfully")
            return result

        except Exception as e:
            logger.error(f"Documentation generation failed: {e}")
            raise GenerationError(f"Failed to generate documentation: {e}")

    def _build_documentation_sections(
        self,
        analysis: CodeAnalysisResult,
        include_diagrams: bool = True,
        include_toc: bool = True
    ) -> List[tuple[str, str]]:
        """
        Build all documentation sections.

        Args:
            analysis: Code analysis results
            include_diagrams: Whether to include diagrams
            include_toc: Whether to include table of contents

        Returns:
            List of (heading, content) tuples
        """
        sections = []

        # Title section
        sections.append(("", self._generate_title(analysis)))

        # Table of contents (placeholder for now)
        if include_toc:
            sections.append(("Table of Contents", self._generate_toc()))

        # Overview
        overview = self._content_generator.generate_overview(analysis)
        sections.append(("Overview", overview))

        # Architecture
        if analysis.frameworks or analysis.key_features:
            architecture = self._content_generator.generate_architecture_section(analysis)
            sections.append(("Architecture", architecture))

            # Add architecture diagram
            if include_diagrams and self._diagram_integrator:
                arch_diagram = self._diagram_integrator.generate_architecture_diagram(analysis)
                if arch_diagram:
                    diagram_embedded = self._diagram_integrator.embed_diagram(
                        arch_diagram,
                        "System Architecture"
                    )
                    sections.append(("", diagram_embedded))

        # Installation
        installation = self._content_generator.generate_installation_section(analysis)
        sections.append(("Installation", installation))

        # Usage
        usage = self._content_generator.generate_usage_section(analysis)
        sections.append(("Usage", usage))

        # File Structure
        file_structure = self._content_generator.generate_file_structure(analysis)
        sections.append(("Project Structure", file_structure))

        # Code Analysis
        code_analysis = self._content_generator.generate_code_analysis(analysis)
        sections.append(("Code Analysis", code_analysis))

        # Database (if applicable)
        if analysis.database_info and include_diagrams and self._diagram_integrator:
            db_diagram = self._diagram_integrator.generate_database_diagram(analysis)
            if db_diagram:
                diagram_embedded = self._diagram_integrator.embed_diagram(
                    db_diagram,
                    "Database Schema"
                )
                sections.append(("Database", diagram_embedded))

        # Contributing
        contributing = self._content_generator.generate_contributing_section()
        sections.append(("Contributing", contributing))

        return sections

    def _format_as_markdown(
        self,
        sections: List[tuple[str, str]],
        analysis: CodeAnalysisResult
    ) -> str:
        """
        Format sections as Markdown document.

        Args:
            sections: List of (heading, content) tuples
            analysis: Code analysis results

        Returns:
            str: Formatted Markdown document
        """
        parts = []

        for heading, content in sections:
            if heading:
                # Format as h2 heading
                parts.append(self._formatter.format_heading(heading, 2))
            parts.append(content)
            parts.append("\n")

        return "\n".join(parts)

    def _generate_title(self, analysis: CodeAnalysisResult) -> str:
        """
        Generate title section.

        Args:
            analysis: Code analysis results

        Returns:
            str: Title section content
        """
        title = self._formatter.format_heading(analysis.project_name, 1)

        # Add badges
        badges = []
        for lang in analysis.languages[:3]:
            badge = self._formatter.format_badge("Language", lang, "blue")
            badges.append(badge)

        if badges:
            title += "\n".join(badges) + "\n\n"

        # Add description
        if analysis.description:
            title += self._formatter.format_paragraph(analysis.description)

        return title

    def _generate_toc(self) -> str:
        """
        Generate table of contents.

        Returns:
            str: Table of contents
        """
        # Simplified TOC
        toc_items = [
            "Overview",
            "Architecture",
            "Installation",
            "Usage",
            "Project Structure",
            "Code Analysis",
            "Contributing"
        ]

        return self._formatter.format_list(
            [f"[{item}](#{item.lower().replace(' ', '-')})" for item in toc_items]
        )

    def _export_documentation(
        self,
        result: DocumentationResult,
        output_path: Path,
        theme_name: str
    ):
        """
        Export documentation to file.

        Args:
            result: Documentation result
            output_path: Output file path
            theme_name: Theme name for styling
        """
        format_str = result.format.value

        if format_str == 'markdown' or format_str == 'md':
            # Export as Markdown
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(result.content, encoding='utf-8')
            logger.info(f"Exported Markdown to {output_path}")

        elif format_str == 'html':
            # Export as HTML
            theme_config = self._theme_manager.load_theme(theme_name)
            css = self._theme_manager.get_css(theme_config)
            html_exporter = HTMLExporter(theme_css=css)
            html_exporter.export(result.content, output_path, result.metadata)

        elif format_str == 'pdf':
            # Export as PDF
            self._pdf_exporter.export(result.content, output_path, result.metadata)

        else:
            logger.warning(f"Unknown format: {format_str}, exporting as Markdown")
            output_path.write_text(result.content, encoding='utf-8')

    def _get_format_enum(self, format_str: str) -> DocumentationFormat:
        """
        Convert format string to DocumentationFormat enum.

        Args:
            format_str: Format string

        Returns:
            DocumentationFormat enum value
        """
        format_map = {
            'markdown': DocumentationFormat.MARKDOWN,
            'md': DocumentationFormat.MARKDOWN,
            'html': DocumentationFormat.HTML,
            'pdf': DocumentationFormat.PDF,
            'rst': DocumentationFormat.RST,
        }

        return format_map.get(format_str.lower(), DocumentationFormat.MARKDOWN)

    def get_supported_formats(self) -> List[DocumentationFormat]:
        """
        Get list of supported documentation formats.

        Returns:
            List of supported formats
        """
        return [
            DocumentationFormat.MARKDOWN,
            DocumentationFormat.HTML,
            DocumentationFormat.PDF,
        ]
