"""
Interactive documentation generator for creating dynamic, searchable documentation.

This module creates interactive HTML documentation with features like:
- Searchable content
- Collapsible sections
- Interactive code examples
- Live diagrams
- Cross-references and navigation
"""

import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import html

logger = logging.getLogger(__name__)


class InteractiveDocumentationGenerator:
    """
    Generate interactive HTML documentation with search, navigation, and dynamic content.
    """
    
    def __init__(self):
        self.templates = self._load_templates()
        
    def generate_interactive_docs(
        self,
        analysis_data: Dict[str, Any],
        title: str = "Project Documentation",
        theme: str = "default",
        include_search: bool = True,
        include_navigation: bool = True,
        include_live_diagrams: bool = True
    ) -> str:
        """
        Generate comprehensive interactive documentation.
        
        Args:
            analysis_data: Complete analysis data from codebase analysis
            title: Documentation title
            theme: Theme to use (default, dark, minimal)
            include_search: Whether to include search functionality
            include_navigation: Whether to include navigation sidebar
            include_live_diagrams: Whether to include interactive diagrams
            
        Returns:
            Complete HTML documentation as string
        """
        try:
            # Extract sections from analysis data
            sections = self._extract_documentation_sections(analysis_data)
            
            # Generate HTML components
            html_content = self._build_html_document(
                title=title,
                sections=sections,
                theme=theme,
                include_search=include_search,
                include_navigation=include_navigation,
                include_live_diagrams=include_live_diagrams
            )
            
            logger.info(f"Generated interactive documentation with {len(sections)} sections")
            return html_content
            
        except Exception as e:
            logger.error(f"Error generating interactive documentation: {e}")
            return self._generate_error_page(str(e))
    
    def generate_searchable_api_docs(
        self,
        api_endpoints: List[Dict[str, Any]],
        title: str = "API Documentation"
    ) -> str:
        """Generate interactive API documentation with search and filtering."""
        try:
            api_html = self._build_api_documentation(api_endpoints, title)
            return api_html
        except Exception as e:
            logger.error(f"Error generating API documentation: {e}")
            return self._generate_error_page(str(e))
    
    def generate_component_explorer(
        self,
        components: List[Dict[str, Any]],
        title: str = "Component Explorer"
    ) -> str:
        """Generate interactive component explorer with live examples."""
        try:
            component_html = self._build_component_explorer(components, title)
            return component_html
        except Exception as e:
            logger.error(f"Error generating component explorer: {e}")
            return self._generate_error_page(str(e))
    
    def _extract_documentation_sections(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and organize sections from analysis data."""
        sections = []
        
        # Overview section
        sections.append({
            'id': 'overview',
            'title': 'Project Overview',
            'content': self._generate_overview_section(analysis_data),
            'type': 'overview'
        })
        
        # Architecture section
        if 'technology_stack' in analysis_data:
            sections.append({
                'id': 'architecture',
                'title': 'Architecture & Technology Stack',
                'content': self._generate_architecture_section(analysis_data['technology_stack']),
                'type': 'architecture'
            })
        
        # File structure section
        if 'file_structure' in analysis_data:
            sections.append({
                'id': 'structure',
                'title': 'Project Structure',
                'content': self._generate_structure_section(analysis_data['file_structure']),
                'type': 'structure'
            })
        
        # API endpoints section
        if analysis_data.get('api_endpoints'):
            sections.append({
                'id': 'api',
                'title': 'API Endpoints',
                'content': self._generate_api_section(analysis_data['api_endpoints']),
                'type': 'api'
            })
        
        # Database schema section
        if analysis_data.get('database_schemas'):
            sections.append({
                'id': 'database',
                'title': 'Database Schemas',
                'content': self._generate_database_section(analysis_data['database_schemas']),
                'type': 'database'
            })
        
        # Dependencies section
        if analysis_data.get('dependencies'):
            sections.append({
                'id': 'dependencies',
                'title': 'Dependencies',
                'content': self._generate_dependencies_section(analysis_data['dependencies']),
                'type': 'dependencies'
            })
        
        # Code analysis section
        if analysis_data.get('ast_analysis'):
            sections.append({
                'id': 'code',
                'title': 'Code Analysis',
                'content': self._generate_code_analysis_section(analysis_data['ast_analysis']),
                'type': 'code'
            })
        
        return sections
    
    def _build_html_document(
        self,
        title: str,
        sections: List[Dict[str, Any]],
        theme: str,
        include_search: bool,
        include_navigation: bool,
        include_live_diagrams: bool
    ) -> str:
        """Build the complete HTML document."""
        html_parts = []
        
        # HTML head
        html_parts.append(self._generate_html_head(title, theme))
        
        # Body start
        html_parts.append('<body>')
        
        # Header
        html_parts.append(self._generate_header(title, include_search))
        
        # Main container
        html_parts.append('<div class="container">')
        
        # Navigation sidebar
        if include_navigation:
            html_parts.append(self._generate_navigation(sections))
        
        # Main content area
        content_class = "main-content" if include_navigation else "main-content full-width"
        html_parts.append(f'<main class="{content_class}">')
        
        # Generate sections
        for section in sections:
            html_parts.append(self._generate_section_html(section, include_live_diagrams))
        
        html_parts.append('</main>')
        html_parts.append('</div>')
        
        # Footer
        html_parts.append(self._generate_footer())
        
        # JavaScript
        html_parts.append(self._generate_javascript(include_search, include_live_diagrams))
        
        html_parts.append('</body></html>')
        
        return '\n'.join(html_parts)
    
    def _generate_html_head(self, title: str, theme: str) -> str:
        """Generate HTML head section with styles."""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    <style>
        {self._get_css_styles(theme)}
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/github.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
</head>'''
    
    def _generate_header(self, title: str, include_search: bool) -> str:
        """Generate header with optional search."""
        search_html = ''
        if include_search:
            search_html = '''
            <div class="search-container">
                <input type="text" id="searchInput" placeholder="Search documentation..." class="search-input">
                <div id="searchResults" class="search-results"></div>
            </div>'''
        
        return f'''
        <header class="header">
            <div class="header-content">
                <h1 class="header-title">{html.escape(title)}</h1>
                {search_html}
            </div>
        </header>'''
    
    def _generate_navigation(self, sections: List[Dict[str, Any]]) -> str:
        """Generate navigation sidebar."""
        nav_items = []
        
        for section in sections:
            nav_items.append(f'''
                <li class="nav-item">
                    <a href="#{section['id']}" class="nav-link" data-section="{section['id']}">
                        <span class="nav-icon">{self._get_section_icon(section['type'])}</span>
                        {html.escape(section['title'])}
                    </a>
                </li>''')
        
        return f'''
        <nav class="sidebar">
            <div class="nav-header">Contents</div>
            <ul class="nav-list">
                {''.join(nav_items)}
            </ul>
        </nav>'''
    
    def _generate_section_html(self, section: Dict[str, Any], include_live_diagrams: bool) -> str:
        """Generate HTML for a documentation section."""
        return f'''
        <section id="{section['id']}" class="doc-section" data-section-type="{section['type']}">
            <h2 class="section-title">
                <span class="section-icon">{self._get_section_icon(section['type'])}</span>
                {html.escape(section['title'])}
            </h2>
            <div class="section-content">
                {section['content']}
            </div>
        </section>'''
    
    def _get_section_icon(self, section_type: str) -> str:
        """Get icon for section type."""
        icons = {
            'overview': '📋',
            'architecture': '🏗️',
            'structure': '📁',
            'api': '🔌',
            'database': '🗄️',
            'dependencies': '📦',
            'code': '💻'
        }
        return icons.get(section_type, '📄')
    
    def _generate_overview_section(self, analysis_data: Dict[str, Any]) -> str:
        """Generate overview section content."""
        total_files = analysis_data.get('total_files', 'N/A')
        analyzed_files = analysis_data.get('analyzed_files', 'N/A')
        
        content = f'''
        <div class="overview-stats">
            <div class="stat-card">
                <h3>Files Analyzed</h3>
                <div class="stat-value">{analyzed_files} / {total_files}</div>
            </div>
        </div>
        
        <div class="overview-description">
            <p>This documentation was automatically generated from codebase analysis. 
            It includes architectural insights, API documentation, database schemas, and code structure analysis.</p>
        </div>'''
        
        return content
    
    def _generate_architecture_section(self, tech_stack: Dict[str, Any]) -> str:
        """Generate architecture section with technology stack."""
        content = '<div class="tech-stack">'
        
        for category, items in tech_stack.items():
            if items and category != 'confidence_scores':
                if isinstance(items, list):
                    items_html = ', '.join([f'<span class="tech-item">{item}</span>' for item in items])
                else:
                    items_html = f'<span class="tech-item">{items}</span>'
                
                content += f'''
                <div class="tech-category">
                    <h4>{category.replace('_', ' ').title()}</h4>
                    <div class="tech-items">{items_html}</div>
                </div>'''
        
        content += '</div>'
        return content
    
    def _generate_structure_section(self, file_structure: Dict[str, Any]) -> str:
        """Generate project structure section."""
        content = f'''
        <div class="structure-overview">
            <div class="structure-stats">
                <span class="stat">Total Lines: <strong>{file_structure.get('total_lines', 0):,}</strong></span>
                <span class="stat">File Types: <strong>{len(file_structure.get('file_types', {}))}</strong></span>
            </div>
        </div>
        
        <div class="file-types">
            <h4>File Type Distribution</h4>
            <div class="file-type-list">'''
        
        for ext, count in file_structure.get('file_types', {}).items():
            content += f'<span class="file-type-badge">{ext or "no extension"}: {count}</span>'
        
        content += '</div></div>'
        
        # Add largest files
        if file_structure.get('largest_files'):
            content += '''<div class="largest-files">
                <h4>Largest Files</h4>
                <ul class="file-list">'''
            
            for file_path, lines, size in file_structure['largest_files'][:5]:
                size_kb = size / 1024
                content += f'''<li class="file-item">
                    <code>{html.escape(file_path)}</code>
                    <span class="file-stats">{lines:,} lines, {size_kb:.1f}KB</span>
                </li>'''
            
            content += '</ul></div>'
        
        return content
    
    def _generate_api_section(self, endpoints: List[Dict[str, Any]]) -> str:
        """Generate API endpoints section."""
        content = f'''
        <div class="api-overview">
            <p>Found <strong>{len(endpoints)}</strong> API endpoints</p>
        </div>
        
        <div class="endpoints-list">'''
        
        for endpoint in endpoints[:20]:  # Limit display
            methods = ', '.join(endpoint.get('methods', ['GET']))
            content += f'''
            <div class="endpoint-card">
                <div class="endpoint-header">
                    <span class="endpoint-methods">{methods}</span>
                    <code class="endpoint-path">{html.escape(endpoint.get('path', ''))}</code>
                </div>
                <div class="endpoint-meta">
                    <span class="endpoint-file">{html.escape(endpoint.get('file', ''))}</span>
                    <span class="endpoint-framework">{endpoint.get('framework', 'unknown')}</span>
                </div>
            </div>'''
        
        content += '</div>'
        return content
    
    def _generate_database_section(self, schemas: List[Dict[str, Any]]) -> str:
        """Generate database schemas section."""
        content = f'<div class="db-overview"><p>Found <strong>{len(schemas)}</strong> database schemas</p></div>'
        
        for i, schema in enumerate(schemas):
            tables = schema.get('tables', [])
            content += f'''
            <div class="schema-card">
                <h4>Schema {i + 1}</h4>
                <div class="schema-meta">
                    <span>Type: <strong>{schema.get('schema_type', 'Unknown')}</strong></span>
                    <span>Tables: <strong>{len(tables)}</strong></span>
                </div>
                <div class="tables-list">
                    {', '.join([f'<code>{table}</code>' for table in tables[:10]])}
                    {f'... and {len(tables) - 10} more' if len(tables) > 10 else ''}
                </div>
            </div>'''
        
        return content
    
    def _generate_dependencies_section(self, dependencies: Dict[str, Any]) -> str:
        """Generate dependencies section."""
        content = '<div class="dependencies-overview">'
        
        package_managers = dependencies.get('package_managers', [])
        if package_managers:
            content += f'<p>Package managers: <strong>{", ".join(package_managers)}</strong></p>'
        
        deps = dependencies.get('dependencies', {})
        if deps:
            content += f'''
            <div class="deps-section">
                <h4>Dependencies ({len(deps)})</h4>
                <div class="deps-list">'''
            
            for dep, version in list(deps.items())[:15]:
                content += f'<span class="dep-item"><code>{dep}</code>: {version}</span>'
            
            if len(deps) > 15:
                content += f'<span class="more-deps">... and {len(deps) - 15} more</span>'
            
            content += '</div></div>'
        
        content += '</div>'
        return content
    
    def _generate_code_analysis_section(self, ast_analysis: Dict[str, Any]) -> str:
        """Generate code analysis section."""
        successful_parses = sum(1 for result in ast_analysis.values() if result.get('success'))
        total_classes = sum(result.get('classes', 0) for result in ast_analysis.values() if result.get('success'))
        total_functions = sum(result.get('functions', 0) for result in ast_analysis.values() if result.get('success'))
        
        content = f'''
        <div class="code-stats">
            <div class="stat-grid">
                <div class="stat-item">
                    <h4>Parsed Files</h4>
                    <div class="stat-value">{successful_parses} / {len(ast_analysis)}</div>
                </div>
                <div class="stat-item">
                    <h4>Classes</h4>
                    <div class="stat-value">{total_classes}</div>
                </div>
                <div class="stat-item">
                    <h4>Functions</h4>
                    <div class="stat-value">{total_functions}</div>
                </div>
            </div>
        </div>
        
        <div class="file-analysis">
            <h4>File Analysis Results</h4>
            <div class="analysis-results">'''
        
        for file_path, result in list(ast_analysis.items())[:10]:
            status = "✅" if result.get('success') else "❌"
            classes = result.get('classes', 0)
            functions = result.get('functions', 0)
            
            content += f'''
            <div class="analysis-item">
                <div class="analysis-header">
                    <span class="analysis-status">{status}</span>
                    <code class="analysis-file">{html.escape(Path(file_path).name)}</code>
                </div>
                <div class="analysis-stats">
                    <span>Classes: {classes}</span>
                    <span>Functions: {functions}</span>
                </div>
            </div>'''
        
        content += '</div></div>'
        return content
    
    def _get_css_styles(self, theme: str) -> str:
        """Get CSS styles for the documentation."""
        base_styles = '''
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }
        
        .header {
            background: #fff;
            border-bottom: 1px solid #e9ecef;
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .header-title {
            font-size: 1.5rem;
            color: #2c3e50;
        }
        
        .search-container {
            position: relative;
        }
        
        .search-input {
            padding: 0.5rem 1rem;
            border: 1px solid #ddd;
            border-radius: 6px;
            width: 300px;
            font-size: 14px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            min-height: calc(100vh - 80px);
        }
        
        .sidebar {
            width: 250px;
            background: #fff;
            border-right: 1px solid #e9ecef;
            padding: 1rem 0;
            position: sticky;
            top: 80px;
            height: fit-content;
        }
        
        .nav-header {
            padding: 0 1rem;
            font-weight: 600;
            color: #6c757d;
            margin-bottom: 1rem;
        }
        
        .nav-list {
            list-style: none;
        }
        
        .nav-item {
            margin-bottom: 0.25rem;
        }
        
        .nav-link {
            display: flex;
            align-items: center;
            padding: 0.5rem 1rem;
            color: #495057;
            text-decoration: none;
            transition: all 0.2s;
        }
        
        .nav-link:hover {
            background: #f8f9fa;
            color: #007bff;
        }
        
        .nav-icon {
            margin-right: 0.5rem;
        }
        
        .main-content {
            flex: 1;
            padding: 2rem;
            background: #fff;
            margin-left: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .main-content.full-width {
            margin-left: 0;
        }
        
        .doc-section {
            margin-bottom: 3rem;
            padding-bottom: 2rem;
            border-bottom: 1px solid #e9ecef;
        }
        
        .section-title {
            display: flex;
            align-items: center;
            margin-bottom: 1.5rem;
            color: #2c3e50;
        }
        
        .section-icon {
            margin-right: 0.5rem;
            font-size: 1.2em;
        }
        
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }
        
        .stat-item {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 6px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 1.5rem;
            font-weight: 600;
            color: #007bff;
        }
        
        .tech-stack .tech-category {
            margin-bottom: 1rem;
        }
        
        .tech-items .tech-item {
            display: inline-block;
            background: #e3f2fd;
            color: #1976d2;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            margin-right: 0.5rem;
            margin-bottom: 0.25rem;
            font-size: 0.875rem;
        }
        
        .endpoint-card {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        .endpoint-header {
            display: flex;
            align-items: center;
            margin-bottom: 0.5rem;
        }
        
        .endpoint-methods {
            background: #28a745;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            margin-right: 1rem;
        }
        
        .endpoint-path {
            font-family: 'Monaco', 'Consolas', monospace;
            background: #f1f3f4;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
        }
        
        .file-type-badge {
            display: inline-block;
            background: #6f42c1;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            margin: 0.25rem;
            font-size: 0.875rem;
        }
        
        code {
            background: #f1f3f4;
            padding: 0.125rem 0.25rem;
            border-radius: 3px;
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 0.875rem;
        }
        '''
        
        if theme == "dark":
            base_styles += '''
            body { background-color: #1a1a1a; color: #e4e4e7; }
            .header { background: #2a2a2a; border-bottom-color: #404040; }
            .sidebar { background: #2a2a2a; border-right-color: #404040; }
            .main-content { background: #2a2a2a; }
            .nav-link:hover { background: #3a3a3a; }
            '''
        
        return base_styles
    
    def _generate_footer(self) -> str:
        """Generate footer."""
        return '''
        <footer class="footer">
            <div class="footer-content">
                <p>Documentation generated automatically by MCP Document Automation</p>
            </div>
        </footer>'''
    
    def _generate_javascript(self, include_search: bool, include_live_diagrams: bool) -> str:
        """Generate JavaScript for interactivity."""
        js = '''
        <script>
            // Initialize syntax highlighting
            hljs.highlightAll();
            
            // Initialize Mermaid
            mermaid.initialize({ startOnLoad: true });
            
            // Smooth scrolling for navigation
            document.querySelectorAll('.nav-link').forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {
                        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                });
            });
        '''
        
        if include_search:
            js += '''
            // Simple search functionality
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.addEventListener('input', function() {
                    const query = this.value.toLowerCase();
                    const sections = document.querySelectorAll('.doc-section');
                    
                    sections.forEach(section => {
                        const text = section.textContent.toLowerCase();
                        if (query === '' || text.includes(query)) {
                            section.style.display = 'block';
                        } else {
                            section.style.display = 'none';
                        }
                    });
                });
            }
            '''
        
        js += '''
        </script>'''
        
        return js
    
    def _generate_error_page(self, error_message: str) -> str:
        """Generate error page."""
        return f'''<!DOCTYPE html>
        <html>
        <head><title>Documentation Error</title></head>
        <body>
            <h1>Documentation Generation Error</h1>
            <p>An error occurred while generating the documentation:</p>
            <pre>{html.escape(error_message)}</pre>
        </body>
        </html>'''
    
    def _load_templates(self) -> Dict[str, str]:
        """Load HTML templates."""
        return {
            'base': 'base template',
            'section': 'section template'
        }
    
    def _build_api_documentation(self, api_endpoints: List[Dict[str, Any]], title: str) -> str:
        """Build API documentation (placeholder for now)."""
        return f"<h1>{title}</h1><p>API documentation would be generated here</p>"
    
    def _build_component_explorer(self, components: List[Dict[str, Any]], title: str) -> str:
        """Build component explorer (placeholder for now)."""
        return f"<h1>{title}</h1><p>Component explorer would be generated here</p>"
