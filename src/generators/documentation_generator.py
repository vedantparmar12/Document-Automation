"""
Documentation generator for converting analysis results to various documentation formats

This module provides functionality to generate comprehensive documentation from
analyzed codebase structure in multiple formats (Markdown, HTML, RST, PDF).
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from src.schemas import DocumentationResult, DocumentationFormat, CodeAnalysisResult

logger = logging.getLogger(__name__)

class DocumentationGenerator:
    """
    Documentation generator for creating comprehensive documentation from analysis results.
    
    Supports multiple output formats and customizable content sections.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the documentation generator.
        
        Args:
            config: Optional configuration parameters
        """
        self.config = config or {}
        self.output_dir = self.config.get('output_dir', 'docs')
        self.include_toc = self.config.get('include_toc', True)
        self.include_code_examples = self.config.get('include_code_examples', True)
        self.include_diagrams = self.config.get('include_diagrams', True)
    
    async def generate_documentation(
        self,
        analysis_result: CodeAnalysisResult,
        format: DocumentationFormat = DocumentationFormat.MARKDOWN,
        include_api_docs: bool = True,
        include_examples: bool = True,
        include_architecture: bool = True
    ) -> DocumentationResult:
        """
        Generate documentation from analysis results.
        
        Args:
            analysis_result: The analysis result to generate documentation from
            format: Output format for documentation
            include_api_docs: Whether to include API documentation
            include_examples: Whether to include code examples
            include_architecture: Whether to include architecture diagrams
            
        Returns:
            DocumentationResult with generated content
        """
        logger.info(f"Generating {format.value} documentation")
        
        try:
            # Generate content based on format
            if format == DocumentationFormat.MARKDOWN:
                content = await self._generate_markdown(
                    analysis_result, include_api_docs, include_examples, include_architecture
                )
            elif format == DocumentationFormat.HTML:
                content = await self._generate_html(
                    analysis_result, include_api_docs, include_examples, include_architecture
                )
            elif format == DocumentationFormat.RST:
                content = await self._generate_rst(
                    analysis_result, include_api_docs, include_examples, include_architecture
                )
            elif format == DocumentationFormat.PDF:
                content = await self._generate_pdf(
                    analysis_result, include_api_docs, include_examples, include_architecture
                )
            else:
                raise ValueError(f"Unsupported documentation format: {format}")
            
            # Create metadata
            metadata = {
                'format': format.value,
                'generated_at': datetime.now().isoformat(),
                'includes_api_docs': include_api_docs,
                'includes_examples': include_examples,
                'includes_architecture': include_architecture,
                'word_count': len(content.split()) if isinstance(content, str) else 0
            }
            
            return DocumentationResult(
                content=content,
                format=format,
                metadata=metadata,
                generated_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Failed to generate documentation: {str(e)}")
            raise
    
    async def _generate_markdown(
        self,
        analysis_result: CodeAnalysisResult,
        include_api_docs: bool,
        include_examples: bool,
        include_architecture: bool
    ) -> str:
        """Generate Markdown documentation."""
        content = []
        
        # Title and introduction
        content.append("# Project Documentation")
        content.append("")
        content.append("This documentation was automatically generated from codebase analysis.")
        content.append("")
        content.append(f"**Generated at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("")
        
        # Table of Contents
        if self.include_toc:
            content.append("## Table of Contents")
            content.append("")
            content.append("- [Project Structure](#project-structure)")
            if analysis_result.dependencies:
                content.append("- [Dependencies](#dependencies)")
            if include_api_docs and analysis_result.api_endpoints:
                content.append("- [API Endpoints](#api-endpoints)")
            if include_architecture and analysis_result.architecture_info:
                content.append("- [Architecture](#architecture)")
            if analysis_result.metrics:
                content.append("- [Metrics](#metrics)")
            content.append("")
        
        # Project Structure
        content.append("## Project Structure")
        content.append("")
        content.append(self._format_directory_structure_markdown(analysis_result.project_structure))
        content.append("")
        
        # Dependencies
        if analysis_result.dependencies:
            content.append("## Dependencies")
            content.append("")
            for dep in analysis_result.dependencies:
                content.append(f"- {dep}")
            content.append("")
        
        # API Endpoints
        if include_api_docs and analysis_result.api_endpoints:
            content.append("## API Endpoints")
            content.append("")
            for endpoint in analysis_result.api_endpoints:
                content.append(f"### {endpoint.get('method', 'GET')} {endpoint.get('path', '')}")
                content.append("")
                if endpoint.get('description'):
                    content.append(f"**Description:** {endpoint['description']}")
                    content.append("")
                if endpoint.get('parameters'):
                    content.append("**Parameters:**")
                    for param in endpoint['parameters']:
                        content.append(f"- `{param.get('name', '')}` ({param.get('type', '')}) - {param.get('description', '')}")
                    content.append("")
                content.append("")
        
        # Architecture
        if include_architecture and analysis_result.architecture_info:
            content.append("## Architecture")
            content.append("")
            content.append(self._format_architecture_markdown(analysis_result.architecture_info))
            content.append("")
        
        # Metrics
        if analysis_result.metrics:
            content.append("## Metrics")
            content.append("")
            for key, value in analysis_result.metrics.items():
                content.append(f"- **{key}:** {value}")
            content.append("")
        
        return "\n".join(content)
    
    async def _generate_html(
        self,
        analysis_result: CodeAnalysisResult,
        include_api_docs: bool,
        include_examples: bool,
        include_architecture: bool
    ) -> str:
        """Generate HTML documentation."""
        # First generate markdown, then convert to HTML
        markdown_content = await self._generate_markdown(
            analysis_result, include_api_docs, include_examples, include_architecture
        )
        
        # Basic HTML conversion (can be enhanced with proper markdown to HTML converter)
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Documentation</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3 {{
            color: #333;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="content">
        {self._markdown_to_html(markdown_content)}
    </div>
</body>
</html>
        """
        
        return html_content
    
    async def _generate_rst(
        self,
        analysis_result: CodeAnalysisResult,
        include_api_docs: bool,
        include_examples: bool,
        include_architecture: bool
    ) -> str:
        """Generate reStructuredText documentation."""
        content = []
        
        # Title
        content.append("Project Documentation")
        content.append("=" * 20)
        content.append("")
        
        # Introduction
        content.append("This documentation was automatically generated from codebase analysis.")
        content.append("")
        content.append(f"**Generated at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("")
        
        # Project Structure
        content.append("Project Structure")
        content.append("-" * 17)
        content.append("")
        content.append(self._format_directory_structure_rst(analysis_result.project_structure))
        content.append("")
        
        # Dependencies
        if analysis_result.dependencies:
            content.append("Dependencies")
            content.append("-" * 12)
            content.append("")
            for dep in analysis_result.dependencies:
                content.append(f"- {dep}")
            content.append("")
        
        return "\n".join(content)
    
    async def _generate_pdf(
        self,
        analysis_result: CodeAnalysisResult,
        include_api_docs: bool,
        include_examples: bool,
        include_architecture: bool
    ) -> str:
        """Generate PDF documentation."""
        # For now, return HTML content that can be converted to PDF
        # In a full implementation, you would use libraries like ReportLab or WeasyPrint
        return await self._generate_html(
            analysis_result, include_api_docs, include_examples, include_architecture
        )
    
    def _format_directory_structure_markdown(self, directory_info) -> str:
        """Format directory structure for Markdown."""
        def format_directory(dir_info, level=0):
            indent = "  " * level
            result = [f"{indent}- [FOLDER] **{dir_info.name}/**"]
            
            # Add files
            for file_info in dir_info.files:
                file_indent = "  " * (level + 1)
                file_icon = self._get_file_icon(file_info.type)
                result.append(f"{file_indent}- {file_icon} {file_info.name} ({file_info.size} bytes)")
            
            # Add subdirectories
            for subdir in dir_info.subdirectories:
                result.extend(format_directory(subdir, level + 1))
            
            return result
        
        return "\n".join(format_directory(directory_info))
    
    def _format_directory_structure_rst(self, directory_info) -> str:
        """Format directory structure for reStructuredText."""
        def format_directory(dir_info, level=0):
            indent = "  " * level
            result = [f"{indent}- {dir_info.name}/"]
            
            # Add files
            for file_info in dir_info.files:
                file_indent = "  " * (level + 1)
                result.append(f"{file_indent}- {file_info.name} ({file_info.size} bytes)")
            
            # Add subdirectories
            for subdir in dir_info.subdirectories:
                result.extend(format_directory(subdir, level + 1))
            
            return result
        
        return "\n".join(format_directory(directory_info))
    
    def _format_architecture_markdown(self, architecture_info: Dict[str, Any]) -> str:
        """Format architecture information for Markdown."""
        content = []
        
        for key, value in architecture_info.items():
            content.append(f"### {key.replace('_', ' ').title()}")
            content.append("")
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    content.append(f"- **{subkey}:** {subvalue}")
            else:
                content.append(f"{value}")
            content.append("")
        
        return "\n".join(content)
    
    def _get_file_icon(self, file_type: str) -> str:
        """Get appropriate emoji icon for file type."""
        icons = {
            'python': '[PY]',
            'javascript': '[JS]',
            'typescript': '[TS]',
            'java': '[JAVA]',
            'cpp': '[CPP]',
            'c': '[C]',
            'go': '[GO]',
            'rust': '[RUST]',
            'ruby': '[RUBY]',
            'php': '[PHP]',
            'html': '[HTML]',
            'css': '[CSS]',
            'json': '[JSON]',
            'yaml': '[YAML]',
            'markdown': '[MD]',
            'text': '[TXT]',
            'sql': '[SQL]',
            'dockerfile': '[DOCKER]',
            'shell': '[SHELL]',
            'unknown': '[FILE]'
        }
        return icons.get(file_type, '[FILE]')
    
    def _markdown_to_html(self, markdown_content: str) -> str:
        """Basic Markdown to HTML conversion."""
        # This is a simplified conversion. In production, use a proper markdown library
        html_content = markdown_content
        
        # Headers
        html_content = html_content.replace('# ', '<h1>').replace('\n', '</h1>\n', 1)
        html_content = html_content.replace('## ', '<h2>').replace('\n', '</h2>\n', 1)
        html_content = html_content.replace('### ', '<h3>').replace('\n', '</h3>\n', 1)
        
        # Bold text
        html_content = html_content.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
        
        # Lists
        lines = html_content.split('\n')
        in_list = False
        result_lines = []
        
        for line in lines:
            if line.strip().startswith('- '):
                if not in_list:
                    result_lines.append('<ul>')
                    in_list = True
                result_lines.append(f'<li>{line.strip()[2:]}</li>')
            else:
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                result_lines.append(line)
        
        if in_list:
            result_lines.append('</ul>')
        
        return '\n'.join(result_lines)

