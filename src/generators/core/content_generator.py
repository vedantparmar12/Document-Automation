"""
Content generation module for documentation.

Implements IContentGenerator interface for structured content generation.
Follows Single Responsibility Principle - focused only on content generation.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.generators.base_generator import IContentGenerator
from src.schemas import CodeAnalysisResult

logger = logging.getLogger(__name__)


class ContentGenerator(IContentGenerator):
    """
    Generates structured documentation content from code analysis results.

    This class is responsible ONLY for generating content sections.
    Formatting, diagrams, and export are handled by other classes (SRP).
    """

    def __init__(self):
        """Initialize content generator."""
        self.project_patterns = self._load_project_patterns()

    def generate_overview(self, analysis: CodeAnalysisResult) -> str:
        """
        Generate project overview section.

        Args:
            analysis: Code analysis results

        Returns:
            str: Overview content (unformatted)
        """
        sections = []

        # Project description
        if analysis.description:
            sections.append(analysis.description)
        else:
            sections.append(f"A {analysis.project_type} project.")

        # Key information
        info_lines = []
        if analysis.languages:
            info_lines.append(f"**Languages:** {', '.join(analysis.languages)}")

        if analysis.frameworks:
            info_lines.append(f"**Frameworks:** {', '.join(analysis.frameworks[:5])}")

        if analysis.dependencies:
            dep_count = len(analysis.dependencies)
            info_lines.append(f"**Dependencies:** {dep_count} packages")

        if info_lines:
            sections.append("\n\n" + "\n".join(info_lines))

        return "\n\n".join(sections)

    def generate_architecture_section(self, analysis: CodeAnalysisResult) -> str:
        """
        Generate architecture description section.

        Args:
            analysis: Code analysis results

        Returns:
            str: Architecture content
        """
        sections = []

        # Architecture overview
        if analysis.frameworks:
            framework_list = ', '.join(analysis.frameworks[:3])
            sections.append(
                f"This project is built with {framework_list}, following modern best practices."
            )

        # Component description
        if analysis.key_features:
            sections.append("\n**Key Components:**\n")
            for feature, details in list(analysis.key_features.items())[:5]:
                if isinstance(details, dict) and 'description' in details:
                    sections.append(f"- **{feature}**: {details['description']}")
                else:
                    sections.append(f"- **{feature}**")

        # Database info
        if analysis.database_info:
            db_info = analysis.database_info
            if isinstance(db_info, dict):
                db_type = db_info.get('type', 'Database')
                sections.append(f"\n**Database:** {db_type}")
                if 'tables' in db_info:
                    table_count = len(db_info['tables'])
                    sections.append(f"- {table_count} tables")

        return "\n".join(sections)

    def generate_file_structure(self, analysis: CodeAnalysisResult) -> str:
        """
        Generate file structure documentation.

        Args:
            analysis: Code analysis results

        Returns:
            str: File structure content
        """
        if not analysis.file_structure:
            return "File structure information not available."

        sections = []
        sections.append("```")

        # Convert file_structure dict to tree format
        for directory, files in sorted(analysis.file_structure.items()):
            sections.append(f"{directory}")
            if isinstance(files, list):
                for file in sorted(files)[:10]:  # Limit to 10 files per directory
                    sections.append(f"├── {file}")
                if len(files) > 10:
                    sections.append(f"└── ... and {len(files) - 10} more files")

        sections.append("```")

        return "\n".join(sections)

    def generate_code_analysis(self, analysis: CodeAnalysisResult) -> str:
        """
        Generate code analysis section.

        Args:
            analysis: Code analysis results

        Returns:
            str: Code analysis content
        """
        sections = []

        # API endpoints
        if analysis.api_endpoints:
            sections.append("**API Endpoints:**\n")
            for endpoint in analysis.api_endpoints[:10]:
                if isinstance(endpoint, dict):
                    method = endpoint.get('method', 'GET')
                    path = endpoint.get('path', '/')
                    sections.append(f"- `{method} {path}`")

        # Security features
        if analysis.security_features:
            sections.append("\n**Security Features:**\n")
            for feature in analysis.security_features[:5]:
                sections.append(f"- {feature}")

        # Code metrics
        if analysis.key_features:
            sections.append("\n**Code Metrics:**\n")
            feature_count = len(analysis.key_features)
            sections.append(f"- Features implemented: {feature_count}")

        if not sections:
            sections.append("Detailed code analysis available in the codebase.")

        return "\n".join(sections)

    def generate_installation_section(self, analysis: CodeAnalysisResult) -> str:
        """
        Generate installation instructions.

        Args:
            analysis: Code analysis results

        Returns:
            str: Installation instructions
        """
        sections = []

        # Prerequisites
        if analysis.languages:
            primary_lang = analysis.languages[0]
            sections.append(f"**Prerequisites:**\n- {primary_lang}")

        # Installation steps
        sections.append("\n**Installation:**\n")
        sections.append("```bash")
        sections.append("# Clone the repository")
        sections.append("git clone <repository-url>")
        sections.append("cd <project-directory>")

        # Language-specific install
        if 'Python' in analysis.languages:
            sections.append("\n# Install dependencies")
            sections.append("pip install -r requirements.txt")
        elif 'JavaScript' in analysis.languages or 'TypeScript' in analysis.languages:
            sections.append("\n# Install dependencies")
            sections.append("npm install")
        elif 'Java' in analysis.languages:
            sections.append("\n# Build project")
            sections.append("mvn install")

        sections.append("```")

        return "\n".join(sections)

    def generate_usage_section(self, analysis: CodeAnalysisResult) -> str:
        """
        Generate usage examples.

        Args:
            analysis: Code analysis results

        Returns:
            str: Usage examples
        """
        sections = []
        sections.append("**Basic Usage:**\n")

        # Language-specific usage
        if 'Python' in analysis.languages:
            sections.append("```python")
            sections.append("# Example usage")
            sections.append("from main import app")
            sections.append("\n# Run the application")
            sections.append("app.run()")
            sections.append("```")
        elif 'JavaScript' in analysis.languages or 'TypeScript' in analysis.languages:
            sections.append("```javascript")
            sections.append("// Example usage")
            sections.append("const app = require('./app');")
            sections.append("\n// Start the application")
            sections.append("app.start();")
            sections.append("```")

        # API usage if applicable
        if analysis.api_endpoints:
            sections.append("\n**API Usage:**\n")
            sections.append("```bash")
            sections.append("# Example API call")
            endpoint = analysis.api_endpoints[0] if analysis.api_endpoints else {}
            method = endpoint.get('method', 'GET') if isinstance(endpoint, dict) else 'GET'
            path = endpoint.get('path', '/') if isinstance(endpoint, dict) else '/'
            sections.append(f"curl -X {method} http://localhost:8000{path}")
            sections.append("```")

        return "\n".join(sections)

    def generate_contributing_section(self) -> str:
        """
        Generate contributing guidelines.

        Returns:
            str: Contributing guidelines
        """
        sections = []
        sections.append("We welcome contributions! Please follow these guidelines:\n")
        sections.append("1. Fork the repository")
        sections.append("2. Create a feature branch")
        sections.append("3. Make your changes")
        sections.append("4. Write or update tests")
        sections.append("5. Submit a pull request\n")
        sections.append("**Code Style:**\n")
        sections.append("- Follow the existing code style")
        sections.append("- Add comments for complex logic")
        sections.append("- Update documentation as needed")

        return "\n".join(sections)

    def _load_project_patterns(self) -> Dict[str, Dict[str, Any]]:
        """
        Load common project patterns.

        Returns:
            dict: Project patterns
        """
        return {
            'api': {
                'type': 'API Service',
                'features': [
                    'RESTful endpoints',
                    'Authentication',
                    'Rate limiting'
                ]
            },
            'web_app': {
                'type': 'Web Application',
                'features': [
                    'User interface',
                    'Data persistence',
                    'User authentication'
                ]
            },
            'library': {
                'type': 'Library',
                'features': [
                    'Reusable components',
                    'Well-documented API',
                    'Tested modules'
                ]
            },
            'cli_tool': {
                'type': 'CLI Tool',
                'features': [
                    'Command-line interface',
                    'Configuration options',
                    'Help documentation'
                ]
            }
        }
