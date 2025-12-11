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

from src.schemas import DocumentationResult, DocumentationFormat, CodeAnalysisResult
from src.diagrams.architecture_diagrams import ArchitectureDiagramGenerator, ArchitecturePattern
from src.diagrams.mermaid_generator import MermaidGenerator

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
        self.arch_generator = ArchitectureDiagramGenerator()
        self.mermaid_generator = MermaidGenerator()
    
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
        
        # 1. Title and Header
        project_name = getattr(analysis_result, 'project_name', 'Unnamed Project')
        # If project_name is missing or default, try to infer from project structure root
        if project_name == 'Unnamed Project' and analysis_result.project_structure:
            project_name = analysis_result.project_structure.name.replace('_', ' ').title()

        content.append(f"# {project_name}")
        content.append("")
        content.append(f"**Documentation Generated:** {datetime.now().strftime('%Y-%m-%d')}")
        content.append("")
        
        # 2. Executive Summary / Overview
        content.append("## Overview")
        content.append("")
        content.append("Welcome to the developer documentation! This guide is designed to help new developers understand the codebase, set up their environment, and start contributing.")
        content.append("")
        
        # Add tech stack summary if available
        if include_architecture and analysis_result.architecture_info:
            tech_stack = analysis_result.architecture_info.get('tech_stack', [])
            if tech_stack:
                content.append("### Key Technologies")
                content.append("")
                content.append(f"The project is built using: **{', '.join(tech_stack)}**.")
                content.append("")

        # 3. Quick Start (Placeholder - encouraged to fill)
        content.append("## Getting Started")
        content.append("")
        content.append("> **Note to New Developers:** This section should be updated with specific setup instructions (e.g., `npm install`, `pip install -r requirements.txt`).")
        content.append("")
        content.append("### Prerequisites")
        content.append("- [ ] Check `README.md` for specific version requirements.")
        content.append("")
        content.append("### Installation")
        content.append("```bash")
        content.append("# Example installation steps")
        content.append("git clone <repository-url>")
        content.append("cd <project-folder>")
        content.append("# Install dependencies here")
        content.append("```")
        content.append("")

        # 4. High-Level Project Structure (Summarized)
        content.append("## Key Components")
        content.append("")
        content.append("The codebase is organized as follows:")
        content.append("")
        # Use summarized structure instead of full tree
        content.append(self._format_directory_structure_summary(analysis_result.project_structure))
        content.append("")
        
        # 5. Architecture & Patterns
        if include_architecture and analysis_result.architecture_info:
            content.append("## Architecture")
            content.append("")
            content.append(self._format_architecture_markdown(analysis_result.architecture_info))
            content.append("")

        # 6. Core Dependencies
        if analysis_result.dependencies:
            content.append("## Core Dependencies")
            content.append("")
            # Limit to top 15 dependencies to avoid clutter
            deps = analysis_result.dependencies[:15]
            for dep in deps:
                content.append(f"- {dep}")
            if len(analysis_result.dependencies) > 15:
                content.append(f"- ...and {len(analysis_result.dependencies) - 15} more.")
            content.append("")
        
        # 7. API Reference (Collapsed/Linkable if large)
        if include_api_docs and analysis_result.api_endpoints:
            content.append("## API Reference")
            content.append("")
            # Just list endpoints concisely
            for endpoint in analysis_result.api_endpoints:
                method = endpoint.get('method', 'GET')
                path = endpoint.get('path', '')
                desc = endpoint.get('description', 'No description')
                content.append(f"- **{method}** `{path}`: {desc}")
            content.append("")

        return "\n".join(content)

    def _format_directory_structure_summary(self, directory_info) -> str:
        """Format directory structure summary, showing only top-level folders and key files."""
        def format_summary(dir_info, level=0):
            if level > 1: # Only go 2 levels deep for summary
                return []
            
            indent = "  " * level
            result = [f"{indent}- **{dir_info.name}/**"]
            
            # Show key files (README, config, etc.) or all files if count is low
            key_files = ['README.md', 'package.json', 'requirements.txt', 'Dockerfile', 'docker-compose.yml', 'tsconfig.json', 'pyproject.toml']
            for file_info in dir_info.files:
                if file_info.name in key_files or level == 0:
                     file_indent = "  " * (level + 1)
                     result.append(f"{file_indent}- {file_info.name}")
            
            # Recurse for subdirectories
            for subdir in dir_info.subdirectories:
                result.extend(format_summary(subdir, level + 1))
            
            return result
        
        return "\n".join(format_summary(directory_info))
    
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
        """
        Generate 'Manager View' PDF-optimized HTML.
        
        This generates a clean, diagram-focused view specifically designed for
        printing to PDF for non-technical stakeholders.
        """
        project_name = getattr(analysis_result, 'project_name', 'System Architecture')
        if project_name == 'Unnamed Project' and analysis_result.project_structure:
            project_name = analysis_result.project_structure.name.replace('_', ' ').title()

        # Generate the core architecture diagram
        # Convert CodeAnalysisResult to dict for compatibility with generator
        analysis_dict = {
            'frameworks': analysis_result.project_structure.dict().get('frameworks', []) if hasattr(analysis_result.project_structure, 'dict') else [],
            'file_structure': str(analysis_result.project_structure),
            'services': [], # TODO: Extract actual services if microservices
            'classification': getattr(analysis_result, 'classification', {})
        }
        
        mermaid_diagram = self.arch_generator.generate_system_architecture(analysis_dict)
        
        # Detect Tech Stack for Badges
        tech_stack = []
        if analysis_result.architecture_info:
             tech_stack = analysis_result.architecture_info.get('tech_stack', [])

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{project_name} - Executive Summary</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({{startOnLoad:true, theme: 'neutral'}});</script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
        
        body {{
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1000px;
            margin: 0 auto;
            padding: 40px;
            background: #fff;
        }}
        
        /* Print Optimization */
        @media print {{
            body {{ padding: 0; }}
            .no-print {{ display: none; }}
            .page-break {{ page-break-before: always; }}
        }}
        
        header {{
            text-align: center;
            margin-bottom: 60px;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 20px;
        }}
        
        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            color: #1a1a1a;
        }}
        
        .subtitle {{
            color: #666;
            font-size: 1.2em;
        }}
        
        .section {{
            margin-bottom: 50px;
        }}
        
        .diagram-container {{
            background: #fcfcfc;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            margin: 30px 0;
            text-align: center;
        }}
        
        .tech-badges {{
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        
        .badge {{
            padding: 6px 16px;
            background: #f0f2f5;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 500;
            color: #444;
            border: 1px solid #e0e0e0;
        }}
        
        .explanation-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }}
        
        .explanation-card {{
            padding: 20px;
            background: #fff;
            border-left: 4px solid #3b82f6;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        
        .explanation-card h3 {{
            margin-top: 0;
            color: #1a1a1a;
        }}
        
        .explanation-card p {{
            color: #555;
            font-size: 0.95em;
            margin-bottom: 0;
        }}

        .print-btn {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: #3b82f6;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
            font-weight: bold;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: background 0.2s;
        }}
        .print-btn:hover {{ background: #2563eb; }}
    </style>
</head>
<body>
    <a href="javascript:window.print()" class="print-btn no-print">🖨️ Save as PDF</a>

    <header>
        <h1>{project_name}</h1>
        <div class="subtitle">System Architecture & Workflow Overview</div>
        <div class="tech-badges">
            {''.join([f'<span class="badge">{t}</span>' for t in tech_stack])}
        </div>
    </header>

    <div class="section">
        <h2>System Architecture</h2>
        <p>The following diagram illustrates the high-level components of the system and how they interact to deliver functionality.</p>
        
        <div class="diagram-container">
            <div class="mermaid">
{mermaid_diagram}
            </div>
        </div>
    </div>

    <div class="section">
        <h2>How It Works (Workflow)</h2>
        <div class="explanation-grid">
            <div class="explanation-card">
                <h3>1. User Interaction</h3>
                <p>Users interact with the <strong>Presentation Layer</strong> (User Interface). This is the visual part of the application that runs in the browser or mobile device, handling all user inputs and displaying information.</p>
            </div>
            <div class="explanation-card">
                <h3>2. Request Processing</h3>
                <p>Requests are sent to the <strong>API/Controller Layer</strong>. This acts as the "traffic cop," receiving instructions from the user, validating them, and deciding which business rules to apply.</p>
            </div>
            <div class="explanation-card">
                <h3>3. Business Logic</h3>
                <p>The core intelligence resides in the <strong>Business Layer</strong> ('Services'). This is where the actual work happens—calculations, rules, and decision-making logic are executed here.</p>
            </div>
            <div class="explanation-card">
                <h3>4. Data Management</h3>
                <p>The <strong>Data Access Layer</strong> communicates with the <strong>Database</strong> to save or retrieve information carefully, ensuring data integrity and security.</p>
            </div>
        </div>
    </div>

    <div class="section page-break">
        <h2>Key Technologies</h2>
        <p>The system is built using the following core technologies, chosen for performance and scalability:</p>
        <ul>
            {''.join([f'<li><strong>{t}</strong></li>' for t in tech_stack])}
        </ul>
    </div>

    <footer style="text-align: center; margin-top: 50px; color: #888; font-size: 0.8em;">
        Generated on {datetime.now().strftime('%Y-%m-%d')} for {project_name}
    </footer>
</body>
</html>
        """
        return html_content
    
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

