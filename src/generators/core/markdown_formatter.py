"""
Markdown formatting module.

Implements IFormatter interface for Markdown formatting.
Follows Single Responsibility Principle - only handles formatting.
"""

import re
from typing import List, Optional

from src.generators.base_generator import IFormatter


class MarkdownFormatter(IFormatter):
    """
    Formats content into Markdown markup.

    This class is responsible ONLY for formatting content into Markdown.
    Content generation is handled by ContentGenerator (SRP).
    """

    def format_heading(self, text: str, level: int = 1) -> str:
        """
        Format a heading at the specified level.

        Args:
            text: Heading text
            level: Heading level (1-6)

        Returns:
            str: Formatted Markdown heading
        """
        level = max(1, min(6, level))  # Clamp between 1-6
        return f"{'#' * level} {text}\n"

    def format_paragraph(self, text: str) -> str:
        """
        Format a paragraph of text.

        Args:
            text: Paragraph content

        Returns:
            str: Formatted paragraph
        """
        return f"{text}\n\n"

    def format_code_block(self, code: str, language: Optional[str] = None) -> str:
        """
        Format a code block with optional syntax highlighting.

        Args:
            code: Code content
            language: Programming language for syntax highlighting

        Returns:
            str: Formatted code block
        """
        lang = language or ""
        return f"```{lang}\n{code}\n```\n"

    def format_list(self, items: List[str], ordered: bool = False) -> str:
        """
        Format a list of items.

        Args:
            items: List items
            ordered: Whether the list should be ordered (numbered)

        Returns:
            str: Formatted list
        """
        if not items:
            return ""

        formatted_items = []
        for i, item in enumerate(items, 1):
            if ordered:
                formatted_items.append(f"{i}. {item}")
            else:
                formatted_items.append(f"- {item}")

        return "\n".join(formatted_items) + "\n"

    def format_table(self, headers: List[str], rows: List[List[str]]) -> str:
        """
        Format a table with headers and rows.

        Args:
            headers: Table header labels
            rows: Table row data

        Returns:
            str: Formatted Markdown table
        """
        if not headers or not rows:
            return ""

        lines = []

        # Header row
        lines.append("| " + " | ".join(headers) + " |")

        # Separator row
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

        # Data rows
        for row in rows:
            # Pad row if it's shorter than headers
            padded_row = row + [""] * (len(headers) - len(row))
            lines.append("| " + " | ".join(padded_row[:len(headers)]) + " |")

        return "\n".join(lines) + "\n"

    def format_link(self, text: str, url: str) -> str:
        """
        Format a hyperlink.

        Args:
            text: Link text
            url: Link URL

        Returns:
            str: Formatted link
        """
        return f"[{text}]({url})"

    def format_bold(self, text: str) -> str:
        """
        Format text as bold.

        Args:
            text: Text to format

        Returns:
            str: Bold formatted text
        """
        return f"**{text}**"

    def format_italic(self, text: str) -> str:
        """
        Format text as italic.

        Args:
            text: Text to format

        Returns:
            str: Italic formatted text
        """
        return f"*{text}*"

    def format_inline_code(self, text: str) -> str:
        """
        Format text as inline code.

        Args:
            text: Text to format

        Returns:
            str: Inline code formatted text
        """
        return f"`{text}`"

    def format_blockquote(self, text: str) -> str:
        """
        Format text as a blockquote.

        Args:
            text: Text to format

        Returns:
            str: Blockquote formatted text
        """
        lines = text.split("\n")
        return "\n".join(f"> {line}" for line in lines) + "\n"

    def format_horizontal_rule(self) -> str:
        """
        Format a horizontal rule.

        Returns:
            str: Horizontal rule
        """
        return "---\n"

    def format_badge(self, label: str, message: str, color: str = "blue") -> str:
        """
        Format a shields.io badge.

        Args:
            label: Badge label
            message: Badge message
            color: Badge color

        Returns:
            str: Badge markdown
        """
        # URL encode label and message
        label_encoded = label.replace(" ", "%20").replace("-", "--")
        message_encoded = message.replace(" ", "%20").replace("-", "--")

        badge_url = f"https://img.shields.io/badge/{label_encoded}-{message_encoded}-{color}"
        return f"![{label}]({badge_url})"

    def format_toc_entry(self, text: str, level: int = 1) -> str:
        """
        Format a table of contents entry.

        Args:
            text: Entry text
            level: Heading level

        Returns:
            str: TOC entry
        """
        # Convert heading to anchor
        anchor = text.lower()
        anchor = re.sub(r'[^\w\s-]', '', anchor)
        anchor = re.sub(r'[-\s]+', '-', anchor)

        indent = "  " * (level - 1)
        return f"{indent}- [{text}](#{anchor})"

    def escape_markdown(self, text: str) -> str:
        """
        Escape special Markdown characters.

        Args:
            text: Text to escape

        Returns:
            str: Escaped text
        """
        special_chars = ['\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '#', '+', '-', '.', '!']
        for char in special_chars:
            text = text.replace(char, f"\\{char}")
        return text

    def create_document(
        self,
        title: str,
        sections: List[tuple[str, str]],
        author: Optional[str] = None,
        date: Optional[str] = None
    ) -> str:
        """
        Create a complete Markdown document.

        Args:
            title: Document title
            sections: List of (heading, content) tuples
            author: Optional author name
            date: Optional date string

        Returns:
            str: Complete Markdown document
        """
        doc = []

        # Title
        doc.append(self.format_heading(title, 1))

        # Metadata
        if author or date:
            metadata = []
            if author:
                metadata.append(f"**Author:** {author}")
            if date:
                metadata.append(f"**Date:** {date}")
            doc.append(self.format_paragraph("\n".join(metadata)))
            doc.append(self.format_horizontal_rule())

        # Sections
        for heading, content in sections:
            doc.append(self.format_heading(heading, 2))
            doc.append(self.format_paragraph(content))

        return "".join(doc)
