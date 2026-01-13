"""
HTML export module.

Implements IExporter interface for HTML export.
Follows Single Responsibility Principle - only handles HTML export.
"""

import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional

from src.generators.base_generator import IExporter, ExportError

logger = logging.getLogger(__name__)


class HTMLExporter(IExporter):
    """
    Exports documentation to HTML format.

    This class is responsible ONLY for HTML export.
    Content generation and formatting are handled by other classes (SRP).
    """

    def __init__(self, theme_css: Optional[str] = None):
        """
        Initialize HTML exporter.

        Args:
            theme_css: Optional CSS stylesheet content
        """
        self.theme_css = theme_css or self._get_default_css()

    def export(
        self,
        content: str,
        output_path: Path,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Export Markdown content to HTML file.

        Args:
            content: Markdown documentation content
            output_path: Output file path
            metadata: Optional metadata (title, author, etc.)

        Returns:
            bool: True if export successful

        Raises:
            ExportError: If export fails
        """
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert Markdown to HTML
            html_content = self._markdown_to_html(content)

            # Wrap in HTML template
            full_html = self._create_html_document(
                html_content,
                metadata or {}
            )

            # Write to file
            output_path.write_text(full_html, encoding='utf-8')

            logger.info(f"Successfully exported HTML to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export HTML: {e}")
            raise ExportError(f"HTML export failed: {e}")

    def validate_output(self, output_path: Path) -> bool:
        """
        Validate exported HTML output.

        Args:
            output_path: Path to exported file

        Returns:
            bool: True if output is valid
        """
        if not output_path.exists():
            return False

        try:
            content = output_path.read_text(encoding='utf-8')

            # Basic HTML validation
            has_html_tags = '<html' in content.lower() and '</html>' in content.lower()
            has_body = '<body' in content.lower() and '</body>' in content.lower()
            has_content = len(content.strip()) > 100

            return has_html_tags and has_body and has_content

        except Exception as e:
            logger.error(f"Failed to validate HTML output: {e}")
            return False

    def _markdown_to_html(self, markdown: str) -> str:
        """
        Convert Markdown to HTML (basic implementation).

        For production use, consider using a library like markdown or mistune.

        Args:
            markdown: Markdown content

        Returns:
            str: HTML content
        """
        html = markdown

        # Convert headers
        for i in range(6, 0, -1):
            pattern = rf'^{"#" * i}\s+(.+)$'
            html = re.sub(pattern, rf'<h{i}>\1</h{i}>', html, flags=re.MULTILINE)

        # Convert code blocks
        html = re.sub(
            r'```(\w+)?\n(.*?)\n```',
            r'<pre><code class="language-\1">\2</code></pre>',
            html,
            flags=re.DOTALL
        )

        # Convert inline code
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

        # Convert bold
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

        # Convert italic
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

        # Convert links
        html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html)

        # Convert unordered lists
        html = re.sub(r'^\- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)

        # Convert ordered lists
        html = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

        # Convert paragraphs (double newlines)
        paragraphs = html.split('\n\n')
        html_paragraphs = []
        for para in paragraphs:
            para = para.strip()
            if para and not para.startswith('<'):
                para = f'<p>{para}</p>'
            html_paragraphs.append(para)

        html = '\n'.join(html_paragraphs)

        # Convert line breaks
        html = html.replace('\n', '<br>\n')

        return html

    def _create_html_document(
        self,
        content: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Create complete HTML document with template.

        Args:
            content: HTML content
            metadata: Document metadata

        Returns:
            str: Complete HTML document
        """
        title = metadata.get('title', 'Documentation')
        author = metadata.get('author', '')
        date = metadata.get('date', '')
        description = metadata.get('description', '')

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {f'<meta name="author" content="{author}">' if author else ''}
    {f'<meta name="description" content="{description}">' if description else ''}
    <style>
{self.theme_css}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
            {f'<p class="meta">By {author}</p>' if author else ''}
            {f'<p class="meta">{date}</p>' if date else ''}
        </header>
        <main>
{content}
        </main>
        <footer>
            <p>Generated on {date or 'unknown date'}</p>
        </footer>
    </div>
</body>
</html>"""

        return html

    def _get_default_css(self) -> str:
        """
        Get default CSS stylesheet.

        Returns:
            str: CSS content
        """
        return """
/* Default Documentation Styles */
* {
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #fff;
    margin: 0;
    padding: 0;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    border-bottom: 2px solid #3498db;
    margin-bottom: 30px;
    padding-bottom: 20px;
}

header h1 {
    color: #3498db;
    margin: 0 0 10px 0;
    font-size: 2.5em;
}

.meta {
    color: #666;
    margin: 5px 0;
    font-size: 0.9em;
}

main {
    margin-bottom: 50px;
}

h1, h2, h3, h4, h5, h6 {
    color: #2c3e50;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    font-weight: 600;
}

h1 { font-size: 2.5em; }
h2 { font-size: 2em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }
h3 { font-size: 1.75em; }
h4 { font-size: 1.5em; }
h5 { font-size: 1.25em; }
h6 { font-size: 1em; }

p {
    margin: 1em 0;
}

code {
    background-color: #f5f5f5;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', Courier, monospace;
    font-size: 0.9em;
}

pre {
    background-color: #f5f5f5;
    padding: 15px;
    border-radius: 5px;
    overflow-x: auto;
    margin: 1em 0;
}

pre code {
    background-color: transparent;
    padding: 0;
}

a {
    color: #3498db;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

ul, ol {
    padding-left: 30px;
    margin: 1em 0;
}

li {
    margin: 0.5em 0;
}

blockquote {
    border-left: 4px solid #3498db;
    padding-left: 20px;
    margin-left: 0;
    color: #666;
    font-style: italic;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}

th, td {
    border: 1px solid #ddd;
    padding: 12px;
    text-align: left;
}

th {
    background-color: #3498db;
    color: white;
    font-weight: 600;
}

tr:nth-child(even) {
    background-color: #f9f9f9;
}

img {
    max-width: 100%;
    height: auto;
}

footer {
    border-top: 1px solid #eee;
    padding-top: 20px;
    text-align: center;
    color: #666;
    font-size: 0.9em;
}

@media (max-width: 768px) {
    .container {
        padding: 10px;
    }

    header h1 {
        font-size: 2em;
    }

    h2 { font-size: 1.75em; }
    h3 { font-size: 1.5em; }
}
"""
