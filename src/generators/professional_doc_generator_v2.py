"""
Professional Documentation Generator V2 - Uses REAL code data

This version extracts and uses ACTUAL characteristics from the codebase
instead of using generic templates and hardcoded patterns.
"""

import os
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from src.diagrams.architecture_diagrams import ArchitectureDiagramGenerator
from src.diagrams.mermaid_generator import MermaidGenerator
from src.analyzers.project_info_detector import ProjectInfoDetector
from src.analyzers.realcode_extractor import RealCodeExtractor

logger = logging.getLogger(__name__)


class ProfessionalDocumentationGeneratorV2:
    """Generates truly unique, project-specific professional documentation."""

    def __init__(self):
        self.arch_generator = ArchitectureDiagramGenerator()
        self.mermaid_generator = MermaidGenerator()

    def generate_documentation(
        self,
        analysis_result: Dict[str, Any],
        project_root: str,
        output_path: str,
        repo_url: str
    ) -> str:
        """Generate professional documentation using REAL project data."""
        logger.info(f"Generating custom documentation for: {output_path}")

        # Extract REAL project information
        detected_info = {}
        real_characteristics = {}

        if project_root and os.path.exists(project_root):
            try:
                # Get detected metadata
                detector = ProjectInfoDetector(project_root)
                detected_info = detector.detect_all()
                logger.info(f"Detected: {detected_info.get('name')} v{detected_info.get('version')}")

                # Extract REAL code characteristics
                extractor = RealCodeExtractor(project_root)
                real_characteristics = extractor.extract_all_characteristics()
                logger.info(f"Extracted {len(real_characteristics.get('real_features', []))} real features")
            except Exception as e:
                logger.warning(f"Real data extraction failed: {e}")

        # Extract project name
        project_name = detected_info.get('name') or self._extract_project_name(repo_url, project_root)

        # Build documentation sections using REAL data
        sections = []

        # Title and Description (using real README content)
        sections.append(self._generate_title_section(project_name, detected_info, real_characteristics))

        # Table of Contents
        sections.append(self._generate_toc())

        # Overview (using real description and features)
        sections.append(self._generate_overview(project_name, detected_info, real_characteristics, analysis_result))

        # Features (using REAL extracted features)
        sections.append(self._generate_features(project_name, real_characteristics, detected_info))

        # Architecture (using REAL component structure)
        sections.append(self._generate_architecture(project_name, real_characteristics, analysis_result))

        # Technology Stack (using REAL detected technologies)
        sections.append(self._generate_technology_stack(detected_info, analysis_result))

        # Prerequisites (based on REAL dependencies)
        sections.append(self._generate_prerequisites(detected_info, analysis_result))

        # Installation (customized for actual package manager)
        sections.append(self._generate_installation(project_name, repo_url, detected_info, real_characteristics))

        # Configuration (using REAL env vars and configs)
        sections.append(self._generate_configuration(project_name, real_characteristics))

        # Usage (with REAL code examples)
        sections.append(self._generate_usage(project_name, real_characteristics, detected_info))

        # API Reference (using REAL extracted endpoints)
        if real_characteristics.get('real_apis'):
            sections.append(self._generate_api_reference(project_name, real_characteristics))

        # Project Structure (using REAL file tree)
        sections.append(self._generate_project_structure(analysis_result, real_characteristics))

        # Code Examples (using REAL code from the project)
        if real_characteristics.get('code_examples'):
            sections.append(self._generate_code_examples(real_characteristics))

        # Contributing
        sections.append(self._generate_contributing())

        # License
        sections.append(self._generate_license(detected_info))

        # Build final document
        doc_content = "\n\n".join(sections)

        # Save the document
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            logger.info(f"Custom documentation saved to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save documentation: {e}")

        return doc_content

    def _extract_project_name(self, repo_url: str, project_root: str) -> str:
        """Extract a clean project name."""
        if repo_url and repo_url.startswith('http'):
            name = os.path.basename(repo_url).replace('.git', '')
        else:
            name = os.path.basename(project_root) if project_root else 'Project'

        return name.replace('-', ' ').replace('_', ' ').title()

    def _generate_title_section(self, project_name: str, detected_info: Dict, real_characteristics: Dict) -> str:
        """Generate title with REAL project information."""
        version = detected_info.get('version', '1.0.0')
        license_name = detected_info.get('license', 'MIT')
        language = detected_info.get('language', 'Python')

        # Use REAL description from README or detected
        readme = real_characteristics.get('readme_content', {})
        description = readme.get('description', detected_info.get('description', f'A {language} project'))

        # Generate accurate badges
        title = f"""# {project_name}

{description}

![Version](https://img.shields.io/badge/version-{version.replace('-', '--')}-blue)
![{language}](https://img.shields.io/badge/{language.replace(' ', '_')}-{self._get_language_version(language)}-green)
![License](https://img.shields.io/badge/license-{license_name.replace('-', '_')}-yellow)
![Build](https://img.shields.io/badge/build-passing-brightgreen)
"""

        # Add framework badges based on REAL detected frameworks
        frameworks = detected_info.get('frameworks', [])
        if frameworks:
            title += "\n"
            for fw in frameworks[:5]:
                fw_name = fw.get('name', 'Framework')
                title += f"![{fw_name}](https://img.shields.io/badge/{fw_name.replace(' ', '_')}-framework-orange)\n"

        return title

    def _get_language_version(self, language: str) -> str:
        """Get typical version requirement for a language."""
        versions = {
            'Python': '3.8+',
            'JavaScript': 'ES6+',
            'TypeScript': '4.0+',
            'Java': '11+',
            'Go': '1.18+',
            'Rust': '1.60+',
            'Ruby': '3.0+',
            'PHP': '8.0+',
        }
        return versions.get(language, 'latest')

    def _generate_toc(self) -> str:
        """Generate table of contents."""
        return """## 📑 Table of Contents

- [Overview](#overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [Project Structure](#-project-structure)
- [Code Examples](#-code-examples)
- [Contributing](#-contributing)
- [License](#-license)

---"""

    def _generate_overview(self, project_name: str, detected_info: Dict, real_characteristics: Dict, analysis_result: Dict) -> str:
        """Generate overview using REAL project description."""
        readme = real_characteristics.get('readme_content', {})
        language = detected_info.get('language', 'Python')

        # Use actual description from README
        description = readme.get('description', detected_info.get('description', ''))

        overview = f"""## Overview

{project_name} is a {language} project. {description}

### Key Information

- **Primary Language**: {language}
- **Version**: {detected_info.get('version', '1.0.0')}
- **License**: {detected_info.get('license', 'Unknown')}
"""

        # Add detected entry points
        entry_points = detected_info.get('entry_points', [])
        if entry_points:
            overview += f"- **Entry Points**: {', '.join(entry_points[:3])}\n"

        # Add package manager
        pkg_mgr = detected_info.get('package_manager', 'unknown')
        if pkg_mgr != 'unknown':
            overview += f"- **Package Manager**: {pkg_mgr}\n"

        # Add CI/CD info if available
        ci_info = detected_info.get('has_ci', {})
        active_ci = [k for k, v in ci_info.items() if v]
        if active_ci:
            overview += f"- **CI/CD**: {', '.join(active_ci)}\n"

        # Add Docker info
        if detected_info.get('has_docker'):
            overview += "- **Containerization**: Docker support included\n"

        # Add real statistics
        metrics = analysis_result.get('metrics', {})
        if metrics:
            overview += f"\n### Project Statistics\n\n"
            if 'total_files' in metrics:
                overview += f"- **Total Files**: {metrics['total_files']}\n"
            if 'total_lines' in metrics:
                overview += f"- **Lines of Code**: {metrics['total_lines']:,}\n"
            if 'languages' in metrics:
                overview += f"- **Languages Used**: {', '.join(list(metrics['languages'].keys())[:5])}\n"

        return overview

    def _generate_features(self, project_name: str, real_characteristics: Dict, detected_info: Dict) -> str:
        """Generate features using REAL extracted features."""
        features_section = """## ✨ Features

### Core Capabilities

"""

        # Use REAL extracted features
        real_features = real_characteristics.get('real_features', [])

        if real_features:
            for i, feature in enumerate(real_features[:15], 1):
                name = feature.get('name', 'Feature')
                purpose = feature.get('purpose', 'Provides functionality')
                feature_type = feature.get('type', 'feature')

                # Create descriptive feature entry
                if purpose:
                    features_section += f"{i}. **{name}**: {purpose}\n"
                else:
                    features_section += f"{i}. **{name}**\n"
        else:
            # Fallback to framework-based features
            frameworks = detected_info.get('frameworks', [])
            for fw in frameworks:
                fw_name = fw.get('name')
                fw_type = fw.get('type')
                features_section += f"- **{fw_name}**: {fw_type.title()} framework integration\n"

        # Add detected tests
        if detected_info.get('has_tests'):
            features_section += "\n### Testing\n\n"
            features_section += "- **Automated Testing**: Comprehensive test suite included\n"

        # Add CI/CD features
        ci_info = detected_info.get('has_ci', {})
        active_ci = [k for k, v in ci_info.items() if v]
        if active_ci:
            features_section += "\n### Continuous Integration\n\n"
            for ci in active_ci:
                features_section += f"- **{ci.replace('_', ' ').title()}**: Automated CI/CD pipeline\n"

        return features_section

    def _generate_architecture(self, project_name: str, real_characteristics: Dict, analysis_result: Dict) -> str:
        """Generate architecture using REAL component structure."""
        arch = f"""## 🏗️ Architecture

### System Components

The {project_name} system is composed of the following actual components found in the codebase:

"""

        # Use REAL architecture components
        arch_components = real_characteristics.get('architecture_components', {})

        if arch_components:
            for component_type, components in arch_components.items():
                arch += f"\n#### {component_type}\n\n"
                for comp in components:
                    directory = comp.get('directory', 'unknown')
                    file_count = comp.get('file_count', 0)
                    arch += f"- **{directory}/**: {file_count} files\n"

                    # List some files
                    files = comp.get('files', [])
                    if files:
                        arch += f"  - Key files: {', '.join(files[:3])}\n"

        # Add real class information
        real_classes = real_characteristics.get('real_classes', [])
        if real_classes:
            arch += f"\n### Main Classes\n\n"
            arch += "The project includes the following key classes:\n\n"

            for cls in real_classes[:10]:
                class_name = cls.get('name')
                docstring = cls.get('docstring', '')
                file_path = cls.get('file', '')

                # Get first line of docstring
                doc_first_line = docstring.split('\n')[0] if docstring else 'Core class'

                arch += f"- **{class_name}** (`{file_path}`): {doc_first_line}\n"

        # Generate Mermaid diagram based on REAL components
        if arch_components:
            arch += "\n### Component Diagram\n\n```mermaid\ngraph TB\n"

            # Create nodes for each component
            node_id = 0
            for comp_type, components in arch_components.items():
                for comp in components[:3]:  # Limit to avoid cluttered diagram
                    dir_name = comp.get('directory', 'comp')
                    safe_id = f"node{node_id}"
                    arch += f"    {safe_id}[\"{dir_name}/\"]\n"
                    node_id += 1

            arch += "```\n"

        return arch

    def _generate_technology_stack(self, detected_info: Dict, analysis_result: Dict) -> str:
        """Generate technology stack using REAL detected technologies."""
        stack = """## 💻 Technology Stack

### Languages

"""

        # Real languages with percentages
        languages = detected_info.get('languages', {})
        if languages:
            total_files = sum(languages.values())
            for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_files * 100) if total_files > 0 else 0
                stack += f"- **{lang}**: {count} files ({percentage:.1f}%)\n"
        else:
            stack += f"- **{detected_info.get('language', 'Python')}**: Primary language\n"

        # Real frameworks
        frameworks = detected_info.get('frameworks', [])
        if frameworks:
            stack += "\n### Frameworks & Libraries\n\n"
            for fw in frameworks:
                fw_name = fw.get('name')
                fw_type = fw.get('type')
                fw_lang = fw.get('language')
                stack += f"- **{fw_name}** ({fw_lang}): {fw_type.title()} framework\n"

        # Real dependencies
        deps = analysis_result.get('dependencies', [])
        if deps:
            stack += "\n### Key Dependencies\n\n"

            # Group by type if available
            python_deps = [d for d in deps if isinstance(d, dict) and d.get('type') == 'python']
            js_deps = [d for d in deps if isinstance(d, dict) and d.get('type') == 'javascript']

            if python_deps:
                stack += "**Python Packages:**\n"
                for dep in python_deps[:15]:
                    name = dep.get('name', '')
                    version = dep.get('version', 'latest')
                    stack += f"- {name} ({version})\n"

            if js_deps:
                stack += "\n**JavaScript Packages:**\n"
                for dep in js_deps[:15]:
                    name = dep.get('name', '')
                    version = dep.get('version', 'latest')
                    stack += f"- {name} ({version})\n"

        # Package manager
        pkg_mgr = detected_info.get('package_manager', 'unknown')
        if pkg_mgr != 'unknown':
            stack += f"\n### Package Management\n\n- **Package Manager**: {pkg_mgr}\n"

        return stack

    def _generate_prerequisites(self, detected_info: Dict, analysis_result: Dict) -> str:
        """Generate prerequisites based on REAL requirements."""
        language = detected_info.get('language', 'Python')

        prereq = """## 📋 Prerequisites

Before installation, ensure you have:

"""

        # Language-specific requirements
        if language == "Python":
            prereq += "- Python 3.8 or higher\n"
            prereq += "- pip (Python package manager)\n"
        elif language in ["JavaScript", "TypeScript"]:
            prereq += "- Node.js 14.x or higher\n"
            prereq += "- npm or yarn\n"
        elif language == "Go":
            prereq += "- Go 1.18 or higher\n"
        elif language == "Rust":
            prereq += "- Rust 1.60 or higher\n"
            prereq += "- Cargo\n"
        elif language == "Java":
            prereq += "- JDK 11 or higher\n"
            prereq += "- Maven or Gradle\n"

        prereq += "- Git\n"

        # Database requirements
        deps = analysis_result.get('dependencies', [])
        dep_names = [d.get('name', d) if isinstance(d, dict) else d for d in deps]
        dep_names_lower = [str(d).lower() for d in dep_names]

        if any('postgres' in d or 'psycopg' in d for d in dep_names_lower):
            prereq += "- PostgreSQL database\n"
        elif any('mysql' in d for d in dep_names_lower):
            prereq += "- MySQL database\n"
        elif any('mongo' in d for d in dep_names_lower):
            prereq += "- MongoDB\n"
        elif any('redis' in d for d in dep_names_lower):
            prereq += "- Redis\n"

        # Docker requirement
        if detected_info.get('has_docker'):
            prereq += "- Docker and Docker Compose (optional, for containerized deployment)\n"

        return prereq

    def _generate_installation(self, project_name: str, repo_url: str, detected_info: Dict, real_characteristics: Dict) -> str:
        """Generate installation using REAL package manager and setup."""
        language = detected_info.get('language', 'Python')
        pkg_mgr = detected_info.get('package_manager', 'pip')
        repo_name = os.path.basename(repo_url).replace('.git', '') if repo_url else project_name.lower().replace(' ', '-')

        install = f"""## 🚀 Installation

### Clone the Repository

```bash
git clone {repo_url if repo_url and repo_url.startswith('http') else 'https://github.com/username/' + repo_name}
cd {repo_name}
```

"""

        # Language and package manager specific installation
        if language == "Python":
            if pkg_mgr == "poetry":
                install += """### Install Dependencies with Poetry

```bash
# Install poetry if you haven't
pip install poetry

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```
"""
            elif pkg_mgr == "pipenv":
                install += """### Install Dependencies with Pipenv

```bash
# Install pipenv if you haven't
pip install pipenv

# Install dependencies
pipenv install

# Activate virtual environment
pipenv shell
```
"""
            else:  # pip
                install += """### Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\\Scripts\\activate

# On macOS/Linux:
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```
"""

        elif language in ["JavaScript", "TypeScript"]:
            if pkg_mgr == "yarn":
                install += """### Install Dependencies

```bash
yarn install
```
"""
            elif pkg_mgr == "pnpm":
                install += """### Install Dependencies

```bash
pnpm install
```
"""
            else:  # npm
                install += """### Install Dependencies

```bash
npm install
```
"""

        elif language == "Go":
            install += """### Install Dependencies

```bash
go mod download
```
"""

        elif language == "Rust":
            install += """### Build the Project

```bash
cargo build --release
```
"""

        # Add environment setup if config files are detected
        config_info = real_characteristics.get('real_configs', {})
        env_vars = config_info.get('env_vars', [])

        if env_vars:
            install += "\n### Configure Environment Variables\n\n"
            install += "Create a `.env` file in the project root:\n\n```env\n"

            for env_var in env_vars[:15]:
                install += f"{env_var}=your_value_here\n"

            install += "```\n"

        return install

    def _generate_configuration(self, project_name: str, real_characteristics: Dict) -> str:
        """Generate configuration using REAL detected config patterns."""
        config_section = """## ⚙️ Configuration

"""

        config_info = real_characteristics.get('real_configs', {})
        env_vars = config_info.get('env_vars', [])
        config_files = config_info.get('config_files', [])

        if env_vars:
            config_section += "### Environment Variables\n\n"
            config_section += f"The project uses the following environment variables:\n\n"

            for env_var in env_vars[:20]:
                config_section += f"- `{env_var}`: Configuration setting\n"

        if config_files:
            config_section += "\n### Configuration Files\n\n"
            config_section += "The project includes the following configuration files:\n\n"

            for config_file in config_files:
                config_section += f"- `{config_file}`\n"

        if not env_vars and not config_files:
            config_section += "Configuration options can be set via environment variables or config files.\n"

        return config_section

    def _generate_usage(self, project_name: str, real_characteristics: Dict, detected_info: Dict) -> str:
        """Generate usage section with REAL code examples."""
        usage = """## 🎯 Usage

"""

        # Get entry points
        entry_points = detected_info.get('entry_points', [])

        if entry_points:
            usage += "### Running the Application\n\n"

            for entry_point in entry_points[:3]:
                if entry_point.endswith('.py'):
                    usage += f"```bash\npython {entry_point}\n```\n\n"
                elif entry_point.endswith('.js') or entry_point.endswith('.ts'):
                    usage += f"```bash\nnode {entry_point}\n```\n\n"

        # Include real code examples
        code_examples = real_characteristics.get('code_examples', [])
        if code_examples:
            usage += "### Code Examples\n\n"

            for i, example in enumerate(code_examples[:3], 1):
                example_file = example.get('file', 'example.py')
                example_code = example.get('code', '')

                if example_code:
                    usage += f"**Example {i}** (from `{example_file}`):\n\n"
                    usage += f"```python\n{example_code}\n```\n\n"

        # Add API usage if APIs are detected
        real_apis = real_characteristics.get('real_apis', [])
        if real_apis:
            usage += "### API Usage\n\n"
            usage += f"The project exposes {len(real_apis)} API endpoints. See the [API Reference](#-api-reference) section for details.\n"

        return usage

    def _generate_api_reference(self, project_name: str, real_characteristics: Dict) -> str:
        """Generate API reference using REAL extracted endpoints."""
        api_section = """## 📡 API Reference

### Available Endpoints

"""

        real_apis = real_characteristics.get('real_apis', [])

        # Group by method
        endpoints_by_method = {}
        for api in real_apis:
            method = api.get('method', 'GET')
            if method not in endpoints_by_method:
                endpoints_by_method[method] = []
            endpoints_by_method[method].append(api)

        # Generate documentation for each endpoint
        for method, endpoints in sorted(endpoints_by_method.items()):
            api_section += f"\n#### {method} Requests\n\n"

            for endpoint in endpoints:
                path = endpoint.get('path', '/')
                framework = endpoint.get('framework', 'API')
                file_path = endpoint.get('file', '')

                api_section += f"**`{method} {path}`**\n\n"
                api_section += f"- Framework: {framework}\n"
                api_section += f"- Defined in: `{file_path}`\n\n"

        # Add usage example
        if real_apis:
            first_api = real_apis[0]
            api_section += "\n### Example Request\n\n"
            api_section += f"```bash\ncurl -X {first_api.get('method', 'GET')} http://localhost:8000{first_api.get('path', '/')}\n```\n"

        return api_section

    def _generate_project_structure(self, analysis_result: Dict, real_characteristics: Dict) -> str:
        """Generate project structure using REAL file tree."""
        structure = """## 📂 Project Structure

"""

        # Get real directory structure
        project_structure = analysis_result.get('project_structure', {})

        if project_structure:
            structure += "```\n"
            structure += self._format_directory_tree(project_structure, '', max_depth=3)
            structure += "```\n"

        # Add component descriptions based on real components
        arch_components = real_characteristics.get('architecture_components', {})
        if arch_components:
            structure += "\n### Directory Descriptions\n\n"

            for comp_type, components in arch_components.items():
                for comp in components:
                    directory = comp.get('directory', 'unknown')
                    file_count = comp.get('file_count', 0)
                    structure += f"- **{directory}/**: {comp_type} ({file_count} files)\n"

        return structure

    def _format_directory_tree(self, node: Dict, prefix: str, max_depth: int, current_depth: int = 0) -> str:
        """Format directory tree structure."""
        if current_depth >= max_depth:
            return ""

        result = ""
        name = node.get('name', 'root')

        if current_depth == 0:
            result += f"{name}/\n"

        files = node.get('files', [])
        subdirs = node.get('subdirectories', [])

        # Show some files
        for i, file_info in enumerate(files[:5]):
            file_name = file_info.get('name', 'file')
            is_last = (i == len(files[:5]) - 1) and not subdirs
            connector = "└── " if is_last else "├── "
            result += f"{prefix}{connector}{file_name}\n"

        # Show subdirectories
        for i, subdir in enumerate(subdirs[:10]):
            is_last = i == len(subdirs[:10]) - 1
            connector = "└── " if is_last else "├── "
            extension = "    " if is_last else "│   "

            subdir_name = subdir.get('name', 'dir')
            result += f"{prefix}{connector}{subdir_name}/\n"
            result += self._format_directory_tree(subdir, prefix + extension, max_depth, current_depth + 1)

        return result

    def _generate_code_examples(self, real_characteristics: Dict) -> str:
        """Generate code examples section using REAL code."""
        examples_section = """## 💡 Code Examples

### Real Examples from the Codebase

"""

        code_examples = real_characteristics.get('code_examples', [])

        for i, example in enumerate(code_examples[:5], 1):
            example_file = example.get('file', 'example.py')
            example_code = example.get('code', '')
            example_type = example.get('type', 'example')

            if example_code:
                examples_section += f"\n#### Example {i}: From `{example_file}`\n\n"

                # Determine language for syntax highlighting
                if example_file.endswith('.py'):
                    lang = 'python'
                elif example_file.endswith(('.js', '.jsx')):
                    lang = 'javascript'
                elif example_file.endswith(('.ts', '.tsx')):
                    lang = 'typescript'
                else:
                    lang = ''

                examples_section += f"```{lang}\n{example_code}\n```\n"

        return examples_section

    def _generate_contributing(self) -> str:
        """Generate contributing section."""
        return """## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Write clear, readable code
- Add tests for new features
- Update documentation as needed
- Follow the existing code style
"""

    def _generate_license(self, detected_info: Dict) -> str:
        """Generate license section using REAL detected license."""
        license_name = detected_info.get('license', 'MIT')

        license_section = f"""## 📄 License

This project is licensed under the {license_name} License.
"""

        if license_name == 'MIT':
            license_section += "\nSee the LICENSE file for details."

        # Add author information if available
        author = detected_info.get('author', {})
        if author.get('name'):
            license_section += f"\n\n**Author**: {author.get('name')}"
            if author.get('email'):
                license_section += f" ({author.get('email')})"

        return license_section
