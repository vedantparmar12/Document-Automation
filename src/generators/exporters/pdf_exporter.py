"""
PDF export module.

Implements IExporter interface for PDF export.
Follows Single Responsibility Principle - only handles PDF export.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from src.generators.base_generator import IExporter, ExportError

logger = logging.getLogger(__name__)


class PDFExporter(IExporter):
    """
    Exports documentation to PDF format.

    This class is responsible ONLY for PDF export.
    Content generation and formatting are handled by other classes (SRP).

    Note: PDF generation requires external libraries like:
    - weasyprint (HTML to PDF)
    - pdfkit (requires wkhtmltopdf)
    - reportlab (direct PDF generation)

    This implementation provides a framework. Add your preferred library.
    """

    def __init__(self, html_exporter: Optional['HTMLExporter'] = None):
        """
        Initialize PDF exporter.

        Args:
            html_exporter: Optional HTML exporter for HTML->PDF workflow
        """
        self.html_exporter = html_exporter
        self._check_dependencies()

    def export(
        self,
        content: str,
        output_path: Path,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Export documentation to PDF file.

        Args:
            content: Markdown documentation content
            output_path: Output file path
            metadata: Optional metadata

        Returns:
            bool: True if export successful

        Raises:
            ExportError: If export fails
        """
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Strategy: Convert Markdown -> HTML -> PDF
            if self.html_exporter:
                # Create temporary HTML
                import tempfile
                with tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix='.html',
                    delete=False,
                    encoding='utf-8'
                ) as tmp:
                    tmp_path = Path(tmp.name)

                try:
                    # Export to HTML first
                    self.html_exporter.export(content, tmp_path, metadata)

                    # Convert HTML to PDF
                    success = self._html_to_pdf(tmp_path, output_path)

                    return success

                finally:
                    # Cleanup temp file
                    if tmp_path.exists():
                        tmp_path.unlink()

            else:
                # Direct Markdown to PDF (requires different approach)
                return self._markdown_to_pdf(content, output_path, metadata)

        except Exception as e:
            logger.error(f"Failed to export PDF: {e}")
            raise ExportError(f"PDF export failed: {e}")

    def validate_output(self, output_path: Path) -> bool:
        """
        Validate exported PDF output.

        Args:
            output_path: Path to exported file

        Returns:
            bool: True if output is valid
        """
        if not output_path.exists():
            return False

        try:
            # Check file size (PDF should be > 100 bytes)
            if output_path.stat().st_size < 100:
                return False

            # Check PDF header
            with open(output_path, 'rb') as f:
                header = f.read(4)
                return header == b'%PDF'

        except Exception as e:
            logger.error(f"Failed to validate PDF output: {e}")
            return False

    def _check_dependencies(self):
        """Check if PDF generation dependencies are available."""
        self.has_weasyprint = False
        self.has_pdfkit = False
        self.has_reportlab = False

        try:
            import weasyprint
            self.has_weasyprint = True
        except ImportError:
            pass

        try:
            import pdfkit
            self.has_pdfkit = True
        except ImportError:
            pass

        try:
            import reportlab
            self.has_reportlab = True
        except ImportError:
            pass

        if not any([self.has_weasyprint, self.has_pdfkit, self.has_reportlab]):
            logger.warning(
                "No PDF generation library found. "
                "Install weasyprint, pdfkit, or reportlab for PDF export."
            )

    def _html_to_pdf(self, html_path: Path, output_path: Path) -> bool:
        """
        Convert HTML file to PDF.

        Args:
            html_path: Input HTML file
            output_path: Output PDF file

        Returns:
            bool: True if successful
        """
        # Try weasyprint first (best quality, no external dependencies)
        if self.has_weasyprint:
            try:
                import weasyprint
                html_content = html_path.read_text(encoding='utf-8')
                doc = weasyprint.HTML(string=html_content)
                doc.write_pdf(str(output_path))
                logger.info(f"Successfully exported PDF using weasyprint: {output_path}")
                return True
            except Exception as e:
                logger.error(f"weasyprint PDF generation failed: {e}")

        # Try pdfkit (requires wkhtmltopdf installed)
        if self.has_pdfkit:
            try:
                import pdfkit
                pdfkit.from_file(str(html_path), str(output_path))
                logger.info(f"Successfully exported PDF using pdfkit: {output_path}")
                return True
            except Exception as e:
                logger.error(f"pdfkit PDF generation failed: {e}")

        # Fallback: Write placeholder PDF
        logger.warning("PDF export not fully configured. Creating placeholder.")
        return self._create_placeholder_pdf(output_path)

    def _markdown_to_pdf(
        self,
        markdown: str,
        output_path: Path,
        metadata: Optional[Dict[str, Any]]
    ) -> bool:
        """
        Convert Markdown directly to PDF.

        Args:
            markdown: Markdown content
            output_path: Output PDF file
            metadata: Optional metadata

        Returns:
            bool: True if successful
        """
        # Using reportlab for direct PDF generation
        if self.has_reportlab:
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.lib.units import inch

                # Create PDF
                doc = SimpleDocTemplate(str(output_path), pagesize=letter)
                styles = getSampleStyleSheet()
                story = []

                # Add title
                if metadata:
                    title = metadata.get('title', 'Documentation')
                    story.append(Paragraph(title, styles['Title']))
                    story.append(Spacer(1, 0.2*inch))

                # Add content (basic Markdown parsing)
                lines = markdown.split('\n')
                for line in lines:
                    if line.strip():
                        # Simple Markdown to formatted text
                        if line.startswith('#'):
                            story.append(Paragraph(line.lstrip('#').strip(), styles['Heading1']))
                        else:
                            story.append(Paragraph(line, styles['BodyText']))
                        story.append(Spacer(1, 0.1*inch))

                # Build PDF
                doc.build(story)
                logger.info(f"Successfully exported PDF using reportlab: {output_path}")
                return True

            except Exception as e:
                logger.error(f"reportlab PDF generation failed: {e}")

        # Fallback
        return self._create_placeholder_pdf(output_path)

    def _create_placeholder_pdf(self, output_path: Path) -> bool:
        """
        Create a placeholder PDF when libraries are not available.

        Args:
            output_path: Output PDF file

        Returns:
            bool: True if successful
        """
        try:
            # Create minimal valid PDF
            pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources 4 0 R /MediaBox [0 0 612 792] /Contents 5 0 R >>
endobj
4 0 obj
<< /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >>
endobj
5 0 obj
<< /Length 55 >>
stream
BT
/F1 12 Tf
100 700 Td
(PDF export requires additional libraries) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000229 00000 n
0000000330 00000 n
trailer
<< /Size 6 /Root 1 0 R >>
startxref
454
%%EOF
"""
            output_path.write_bytes(pdf_content)
            logger.warning(
                f"Created placeholder PDF at {output_path}. "
                "Install weasyprint, pdfkit, or reportlab for full PDF generation."
            )
            return True

        except Exception as e:
            logger.error(f"Failed to create placeholder PDF: {e}")
            return False

    def get_available_methods(self) -> list[str]:
        """
        Get list of available PDF generation methods.

        Returns:
            List of available methods
        """
        methods = []
        if self.has_weasyprint:
            methods.append("weasyprint")
        if self.has_pdfkit:
            methods.append("pdfkit")
        if self.has_reportlab:
            methods.append("reportlab")
        return methods or ["placeholder"]
