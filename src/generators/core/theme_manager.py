"""
Theme management module.

Implements IThemeManager interface for theming and styling.
Follows Single Responsibility Principle - only handles themes/styling.
"""

import logging
from typing import Dict, Any

from src.generators.base_generator import IThemeManager

logger = logging.getLogger(__name__)


class ThemeManager(IThemeManager):
    """
    Manages themes and styling for documentation.

    This class is responsible ONLY for theme management.
    Content generation and formatting are handled by other classes (SRP).
    """

    def __init__(self):
        """Initialize theme manager with built-in themes."""
        self.themes = self._load_builtin_themes()

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
        if theme_name not in self.themes:
            logger.warning(f"Theme '{theme_name}' not found, using default")
            theme_name = "default"

        return self.themes.get(theme_name, self.themes["default"])

    def apply_theme(self, content: str, theme_config: Dict[str, Any]) -> str:
        """
        Apply theme styling to content.

        For Markdown, this primarily affects HTML export.
        For pure Markdown, theme application is minimal.

        Args:
            content: Content to style
            theme_config: Theme configuration

        Returns:
            str: Styled content
        """
        # For Markdown, we don't modify the content much
        # Theme is primarily applied during HTML/PDF export
        return content

    def get_css(self, theme_config: Dict[str, Any]) -> str:
        """
        Get CSS stylesheet for theme.

        Args:
            theme_config: Theme configuration

        Returns:
            str: CSS content
        """
        colors = theme_config.get("colors", {})
        fonts = theme_config.get("fonts", {})

        css = f"""
/* Theme: {theme_config.get('name', 'default')} */

:root {{
    --primary-color: {colors.get('primary', '#3498db')};
    --secondary-color: {colors.get('secondary', '#2ecc71')};
    --background-color: {colors.get('background', '#ffffff')};
    --text-color: {colors.get('text', '#333333')};
    --code-background: {colors.get('code_background', '#f5f5f5')};
    --link-color: {colors.get('link', '#3498db')};

    --font-family: {fonts.get('body', "'Segoe UI', Tahoma, sans-serif")};
    --font-family-code: {fonts.get('code', "'Courier New', monospace")};
    --font-size-base: {fonts.get('size_base', '16px')};
}}

body {{
    font-family: var(--font-family);
    font-size: var(--font-size-base);
    line-height: 1.6;
    color: var(--text-color);
    background-color: var(--background-color);
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}}

h1, h2, h3, h4, h5, h6 {{
    color: var(--primary-color);
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}}

h1 {{
    font-size: 2.5em;
    border-bottom: 2px solid var(--primary-color);
    padding-bottom: 0.3em;
}}

h2 {{
    font-size: 2em;
    border-bottom: 1px solid #eee;
    padding-bottom: 0.3em;
}}

code {{
    background-color: var(--code-background);
    padding: 2px 6px;
    border-radius: 3px;
    font-family: var(--font-family-code);
    font-size: 0.9em;
}}

pre {{
    background-color: var(--code-background);
    padding: 15px;
    border-radius: 5px;
    overflow-x: auto;
}}

pre code {{
    background-color: transparent;
    padding: 0;
}}

a {{
    color: var(--link-color);
    text-decoration: none;
}}

a:hover {{
    text-decoration: underline;
}}

table {{
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}}

th, td {{
    border: 1px solid #ddd;
    padding: 12px;
    text-align: left;
}}

th {{
    background-color: var(--primary-color);
    color: white;
}}

tr:nth-child(even) {{
    background-color: #f9f9f9;
}}

blockquote {{
    border-left: 4px solid var(--primary-color);
    padding-left: 20px;
    margin-left: 0;
    color: #666;
}}

img {{
    max-width: 100%;
    height: auto;
}}
"""
        return css

    def get_available_themes(self) -> list[str]:
        """
        Get list of available theme names.

        Returns:
            List of theme names
        """
        return list(self.themes.keys())

    def _load_builtin_themes(self) -> Dict[str, Dict[str, Any]]:
        """
        Load built-in themes.

        Returns:
            dict: Theme configurations
        """
        return {
            "default": {
                "name": "Default",
                "description": "Clean, professional default theme",
                "colors": {
                    "primary": "#3498db",
                    "secondary": "#2ecc71",
                    "background": "#ffffff",
                    "text": "#333333",
                    "code_background": "#f5f5f5",
                    "link": "#3498db",
                },
                "fonts": {
                    "body": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
                    "code": "'Courier New', Courier, monospace",
                    "size_base": "16px",
                },
            },
            "dark": {
                "name": "Dark",
                "description": "Dark theme for reduced eye strain",
                "colors": {
                    "primary": "#61dafb",
                    "secondary": "#98c379",
                    "background": "#282c34",
                    "text": "#abb2bf",
                    "code_background": "#1e2227",
                    "link": "#61dafb",
                },
                "fonts": {
                    "body": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
                    "code": "'Fira Code', 'Courier New', monospace",
                    "size_base": "16px",
                },
            },
            "minimal": {
                "name": "Minimal",
                "description": "Minimalist black and white theme",
                "colors": {
                    "primary": "#000000",
                    "secondary": "#666666",
                    "background": "#ffffff",
                    "text": "#000000",
                    "code_background": "#f8f8f8",
                    "link": "#000000",
                },
                "fonts": {
                    "body": "Georgia, serif",
                    "code": "'Courier New', monospace",
                    "size_base": "18px",
                },
            },
            "github": {
                "name": "GitHub",
                "description": "GitHub-style documentation theme",
                "colors": {
                    "primary": "#0366d6",
                    "secondary": "#28a745",
                    "background": "#ffffff",
                    "text": "#24292e",
                    "code_background": "#f6f8fa",
                    "link": "#0366d6",
                },
                "fonts": {
                    "body": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif",
                    "code": "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace",
                    "size_base": "16px",
                },
            },
        }

    def create_custom_theme(
        self,
        name: str,
        colors: Dict[str, str],
        fonts: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a custom theme.

        Args:
            name: Theme name
            colors: Color configuration
            fonts: Optional font configuration

        Returns:
            dict: Theme configuration
        """
        theme = {
            "name": name,
            "description": f"Custom theme: {name}",
            "colors": colors,
            "fonts": fonts or self.themes["default"]["fonts"],
        }

        self.themes[name] = theme
        return theme
