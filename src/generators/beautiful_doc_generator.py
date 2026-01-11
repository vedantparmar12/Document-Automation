"""
Beautiful Documentation Generator

Creates comprehensive, well-structured, beautiful documentation
that fully explains the project workflow and architecture.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from src.analyzers.project_info_detector import ProjectInfoDetector
from src.analyzers.realcode_extractor import RealCodeExtractor
from src.analyzers.intelligent_workflow_analyzer import IntelligentWorkflowAnalyzer

logger = logging.getLogger(__name__)


class BeautifulDocumentationGenerator:
    """
    Generates beautiful, comprehensive documentation that:
    - Fully explains project purpose and workflow
    - Shows clear data flow and architecture
    - Includes visual diagrams
    - Provides real examples
    - Is easy to read and understand
    """

    def __init__(self):
        pass

    def generate(
        self,
        analysis_result: Dict[str, Any],
        project_root: str,
        output_path: str,
        repo_url: str
    ) -> str:
        """Generate beautiful, comprehensive documentation."""
        logger.info(f"🎨 Generating beautiful documentation for: {project_root}")

        # Run all analyzers
        detected_info = {}
        real_characteristics = {}
        workflow_analysis = {}

        if project_root and os.path.exists(project_root):
            try:
                # Get metadata
                detector = ProjectInfoDetector(project_root)
                detected_info = detector.detect_all()

                # Extract real code
                extractor = RealCodeExtractor(project_root)
                real_characteristics = extractor.extract_all_characteristics()

                # Analyze workflow
                workflow_analyzer = IntelligentWorkflowAnalyzer(project_root)
                workflow_analysis = workflow_analyzer.analyze_complete_workflow()

                logger.info(f"✅ Analysis complete: {detected_info.get('name', 'Project')}")
            except Exception as e:
                logger.warning(f"Analysis failed: {e}")

        # Build beautiful documentation
        sections = []

        # 1. Hero Section - Project name and description
        sections.append(self._generate_hero_section(detected_info, real_characteristics, workflow_analysis))

        # 2. Quick Overview - What is this project?
        sections.append(self._generate_quick_overview(detected_info, workflow_analysis))

        # 3. Table of Contents
        sections.append(self._generate_toc())

        # 4. Why This Project? - Value proposition
        sections.append(self._generate_why_section(detected_info, workflow_analysis))

        # 5. How It Works - Complete workflow explanation
        sections.append(self._generate_how_it_works(workflow_analysis, real_characteristics))

        # 6. Architecture Overview - Visual architecture
        sections.append(self._generate_architecture_overview(real_characteristics, workflow_analysis))

        # 7. Key Features - Real features from code
        sections.append(self._generate_features_section(real_characteristics, detected_info))

        # 8. Getting Started - Installation & setup
        sections.append(self._generate_getting_started(detected_info, real_characteristics, repo_url))

        # 9. Usage Guide - How to use
        sections.append(self._generate_usage_guide(real_characteristics, workflow_analysis, detected_info))

        # 10. API Documentation - If APIs exist
        if real_characteristics.get('real_apis'):
            sections.append(self._generate_api_documentation(real_characteristics))

        # 11. Configuration - Settings and options
        sections.append(self._generate_configuration_guide(real_characteristics))

        # 12. Project Structure - File organization
        sections.append(self._generate_project_structure(analysis_result, real_characteristics))

        # 13. Development Guide - For contributors
        sections.append(self._generate_development_guide(detected_info, real_characteristics))

        # 14. Troubleshooting - Common issues
        sections.append(self._generate_troubleshooting())

        # 15. Technology Stack - What's used
        sections.append(self._generate_tech_stack(detected_info, analysis_result))

        # 16. Contributing
        sections.append(self._generate_contributing())

        # 17. License & Credits
        sections.append(self._generate_license_section(detected_info))

        # Build final document
        doc_content = "\n\n".join(sections)

        # Save
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            logger.info(f"✅ Beautiful documentation saved: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save documentation: {e}")

        return doc_content

    def _generate_hero_section(self, detected_info: Dict, real_characteristics: Dict, workflow_analysis: Dict) -> str:
        """Generate hero section with project name and tagline."""
        project_name = detected_info.get('name', 'Project')
        version = detected_info.get('version', '1.0.0')
        license_name = detected_info.get('license', 'MIT')
        language = detected_info.get('language', 'Python')

        # Get description from README or detected info
        readme = real_characteristics.get('readme_content', {})
        description = readme.get('description', detected_info.get('description', f'A {language} project'))

        # Get project purpose
        purpose = workflow_analysis.get('project_purpose', {})
        project_type = purpose.get('type', 'Application')

        hero = f"""<div align="center">

# 🚀 {project_name}

### {description}

[![Version](https://img.shields.io/badge/version-{version}-blue.svg)](https://github.com)
[![{language}](https://img.shields.io/badge/{language.replace(' ', '_')}-{self._get_language_version(language)}-green.svg)]()
[![License](https://img.shields.io/badge/license-{license_name}-yellow.svg)]()
[![Maintained](https://img.shields.io/badge/Maintained-Yes-brightgreen.svg)]()

**{project_type}** | **{language}** | **Production Ready**

</div>

---
"""

        # Add frameworks badges
        frameworks = detected_info.get('frameworks', [])
        if frameworks:
            hero += "\n<div align=\"center\">\n\n"
            for fw in frameworks[:6]:
                fw_name = fw.get('name', 'Framework')
                hero += f"![{fw_name}](https://img.shields.io/badge/-{fw_name.replace(' ', '_')}-orange?style=flat-square) "
            hero += "\n\n</div>\n"

        return hero

    def _generate_quick_overview(self, detected_info: Dict, workflow_analysis: Dict) -> str:
        """Generate quick overview section."""
        purpose = workflow_analysis.get('project_purpose', {})
        problem_solved = purpose.get('problem_solved', '')

        overview = """## 📖 What is This?

"""

        if problem_solved:
            overview += f"{problem_solved}\n\n"

        overview += f"""### At a Glance

- **Type**: {purpose.get('type', 'Application')}
- **Language**: {detected_info.get('language', 'Python')} {detected_info.get('version', '')}
- **License**: {detected_info.get('license', 'MIT')}
"""

        # Add key stats
        if detected_info.get('has_tests'):
            overview += "- ✅ **Tested**: Includes comprehensive test suite\n"

        if detected_info.get('has_docker'):
            overview += "- 🐳 **Dockerized**: Ready for containerized deployment\n"

        ci_info = detected_info.get('has_ci', {})
        active_ci = [k for k, v in ci_info.items() if v]
        if active_ci:
            overview += f"- 🔄 **CI/CD**: {', '.join(active_ci).replace('_', ' ').title()}\n"

        # Add integrations
        integrations = workflow_analysis.get('integrations', [])
        if integrations:
            overview += f"\n### 🔌 Integrates With\n\n"
            for integration in integrations[:5]:
                service = integration.get('service', 'Service')
                overview += f"- **{service}**: {', '.join(integration.get('libraries', [])[:2])}\n"

        return overview

    def _generate_toc(self) -> str:
        """Generate table of contents."""
        return """## 📑 Table of Contents

- [Why This Project?](#-why-this-project)
- [How It Works](#-how-it-works)
- [Architecture Overview](#-architecture-overview)
- [Key Features](#-key-features)
- [Getting Started](#-getting-started)
- [Usage Guide](#-usage-guide)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)
- [Project Structure](#-project-structure)
- [Development Guide](#-development-guide)
- [Troubleshooting](#-troubleshooting)
- [Technology Stack](#-technology-stack)
- [Contributing](#-contributing)
- [License](#-license)

---"""

    def _generate_why_section(self, detected_info: Dict, workflow_analysis: Dict) -> str:
        """Generate 'Why this project?' section."""
        purpose = workflow_analysis.get('project_purpose', {})

        why = f"""## 💡 Why This Project?

{purpose.get('problem_solved', 'This project provides valuable functionality for your use case.')}

### Benefits

"""

        # Infer benefits based on project type
        project_type = purpose.get('type', 'Application')

        if 'API' in project_type:
            why += """- 🚀 **Fast**: High-performance API endpoints
- 🔒 **Secure**: Built-in authentication and validation
- 📚 **Well-Documented**: Complete API documentation
- 🔄 **Scalable**: Ready for production workloads
"""
        elif 'CLI' in project_type:
            why += """- ⚡ **Efficient**: Command-line interface for quick operations
- 🛠️ **Flexible**: Rich set of commands and options
- 🤖 **Automatable**: Easy to integrate into scripts
- 📦 **Portable**: Works across different platforms
"""
        elif 'Library' in project_type or 'Package' in project_type:
            why += """- 📦 **Easy Integration**: Simple to add to your project
- 🎯 **Focused**: Does one thing really well
- 🔧 **Customizable**: Flexible API for your needs
- 📖 **Well-Documented**: Clear examples and guides
"""
        else:
            why += """- ⚡ **Efficient**: Optimized for performance
- 🎯 **Reliable**: Tested and production-ready
- 🛠️ **Maintainable**: Clean, well-organized code
- 📚 **Documented**: Comprehensive documentation
"""

        return why

    def _generate_how_it_works(self, workflow_analysis: Dict, real_characteristics: Dict) -> str:
        """Generate comprehensive 'How It Works' section."""
        how = """## 🔄 How It Works

### Complete Workflow

"""

        # Get execution flows
        execution_flows = workflow_analysis.get('execution_flow', [])

        if execution_flows:
            how += "The application follows this execution flow:\n\n"

            for i, flow in enumerate(execution_flows[:3], 1):
                entry_point = flow.get('entry_point', 'main.py')
                steps = flow.get('steps', [])
                calls = flow.get('calls', [])

                how += f"#### Flow {i}: {entry_point}\n\n"

                if steps:
                    for j, step in enumerate(steps[:8], 1):
                        how += f"{j}. {step}\n"
                    how += "\n"
                elif calls:
                    how += "**Key Function Calls:**\n\n"
                    for call in calls[:8]:
                        how += f"- `{call}()`\n"
                    how += "\n"

        # Add workflow diagram
        how += self._generate_workflow_diagram(workflow_analysis)

        # Add data flow explanation
        data_flows = workflow_analysis.get('data_flow', [])
        if data_flows:
            how += "\n### 📊 Data Flow\n\n"
            how += "Data flows through the system as follows:\n\n"

            for flow in data_flows:
                flow_type = flow.get('type', 'Unknown')
                description = flow.get('description', '')
                operations = flow.get('operations', [])

                how += f"**{flow_type}**: {description}\n"
                if operations:
                    how += f"- Operations: {', '.join(operations[:5])}\n"
                how += "\n"

        # Add key processes
        key_processes = workflow_analysis.get('key_processes', [])
        if key_processes:
            how += "\n### ⚙️ Key Processes\n\n"
            for process in key_processes[:8]:
                process_name = process.get('process', 'Process')
                count = process.get('count', 0)
                how += f"- **{process_name}**: {count} operations\n"

        return how

    def _generate_workflow_diagram(self, workflow_analysis: Dict) -> str:
        """Generate workflow diagram."""
        diagram = "\n### Workflow Diagram\n\n```mermaid\ngraph TB\n"

        # Create simple workflow based on analysis
        diagram += '    Start["🚀 Application Start"]\n'

        execution_flows = workflow_analysis.get('execution_flow', [])
        if execution_flows:
            flow = execution_flows[0]
            calls = flow.get('calls', [])

            for i, call in enumerate(calls[:6]):
                node_id = f"step{i+1}"
                diagram += f'    {node_id}["{call}"]\n'

            # Connect nodes
            diagram += "    Start --> step1\n"
            for i in range(len(calls[:6]) - 1):
                diagram += f"    step{i+1} --> step{i+2}\n"

        diagram += '    End["✅ Complete"]\n'
        if execution_flows:
            diagram += f"    step{len(calls[:6])} --> End\n"

        diagram += "\n    style Start fill:#90EE90\n"
        diagram += "    style End fill:#FFB6C1\n"
        diagram += "```\n"

        return diagram

    def _generate_architecture_overview(self, real_characteristics: Dict, workflow_analysis: Dict) -> str:
        """Generate architecture overview."""
        arch = """## 🏗️ Architecture Overview

### System Components

"""

        # Get real architecture components
        arch_components = real_characteristics.get('architecture_components', {})

        if arch_components:
            arch += "The system is organized into the following components:\n\n"

            for component_type, components in arch_components.items():
                arch += f"#### {component_type}\n\n"
                for comp in components:
                    directory = comp.get('directory', 'unknown')
                    file_count = comp.get('file_count', 0)
                    files = comp.get('files', [])

                    arch += f"**`{directory}/`** ({file_count} files)\n"
                    if files:
                        arch += f"- Key files: {', '.join(files[:3])}\n"
                    arch += "\n"

        # Add component interaction diagram
        arch += self._generate_component_diagram(arch_components, workflow_analysis)

        return arch

    def _generate_component_diagram(self, arch_components: Dict, workflow_analysis: Dict) -> str:
        """Generate component interaction diagram."""
        diagram = "### Component Interaction\n\n```mermaid\ngraph LR\n"

        # Create nodes for each component
        node_ids = {}
        node_id = 0

        for comp_type, components in list(arch_components.items())[:6]:
            for comp in components[:2]:
                directory = comp.get('directory', 'comp')
                safe_id = f"node{node_id}"
                node_ids[directory] = safe_id
                diagram += f'    {safe_id}["{directory}/"]\n'
                node_id += 1

        # Add simple connections (in sequence)
        node_list = list(node_ids.values())
        for i in range(len(node_list) - 1):
            diagram += f"    {node_list[i]} --> {node_list[i+1]}\n"

        diagram += "```\n"

        return diagram

    def _generate_features_section(self, real_characteristics: Dict, detected_info: Dict) -> str:
        """Generate features section with real features."""
        features = """## ✨ Key Features

"""

        # Get real features
        real_features = real_characteristics.get('real_features', [])

        if real_features:
            features += "### Core Capabilities\n\n"

            for i, feature in enumerate(real_features[:12], 1):
                name = feature.get('name', 'Feature')
                purpose = feature.get('purpose', '')
                feature_type = feature.get('type', '')

                icon = "🎯"
                if 'api' in name.lower() or 'endpoint' in name.lower():
                    icon = "🌐"
                elif 'data' in name.lower() or 'database' in name.lower():
                    icon = "💾"
                elif 'process' in name.lower() or 'handler' in name.lower():
                    icon = "⚙️"
                elif 'validate' in name.lower():
                    icon = "✅"

                features += f"{i}. {icon} **{name}**"
                if purpose:
                    features += f": {purpose}"
                features += "\n"

        # Add testing features
        if detected_info.get('has_tests'):
            features += "\n### Quality Assurance\n\n"
            features += "- ✅ **Comprehensive Testing**: Full test coverage\n"
            features += "- 🔍 **Quality Checks**: Automated testing pipeline\n"

        return features

    def _generate_getting_started(self, detected_info: Dict, real_characteristics: Dict, repo_url: str) -> str:
        """Generate getting started section."""
        language = detected_info.get('language', 'Python')
        pkg_mgr = detected_info.get('package_manager', 'pip')
        project_name = detected_info.get('name', 'project')
        repo_name = os.path.basename(repo_url).replace('.git', '') if repo_url else project_name.lower().replace(' ', '-')

        getting_started = f"""## 🚀 Getting Started

### Prerequisites

"""

        # Language-specific prereqs
        if language == "Python":
            getting_started += "- Python 3.8 or higher\n"
            getting_started += f"- {pkg_mgr}\n"
        elif language in ["JavaScript", "TypeScript"]:
            getting_started += "- Node.js 14.x or higher\n"
            getting_started += f"- {pkg_mgr}\n"

        getting_started += f"""- Git

### Quick Install

```bash
# 1. Clone the repository
git clone {repo_url if repo_url and repo_url.startswith('http') else 'https://github.com/username/' + repo_name}
cd {repo_name}

"""

        # Installation steps based on package manager
        if language == "Python":
            if pkg_mgr == "poetry":
                getting_started += """# 2. Install with Poetry
poetry install
poetry shell
```
"""
            elif pkg_mgr == "pipenv":
                getting_started += """# 2. Install with Pipenv
pipenv install
pipenv shell
```
"""
            else:
                getting_started += """# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
source venv/bin/activate  # On macOS/Linux
venv\\Scripts\\activate  # On Windows

# 4. Install dependencies
pip install -r requirements.txt
```
"""
        elif language in ["JavaScript", "TypeScript"]:
            if pkg_mgr == "yarn":
                getting_started += """# 2. Install dependencies
yarn install
```
"""
            elif pkg_mgr == "pnpm":
                getting_started += """# 2. Install dependencies
pnpm install
```
"""
            else:
                getting_started += """# 2. Install dependencies
npm install
```
"""

        # Add configuration step if env vars exist
        env_vars = real_characteristics.get('real_configs', {}).get('env_vars', [])
        if env_vars:
            getting_started += f"\n### ⚙️ Configuration\n\n"
            getting_started += "Create a `.env` file:\n\n```bash\n"
            for var in env_vars[:10]:
                getting_started += f"{var}=your_value_here\n"
            getting_started += "```\n"

        # Add run instructions
        entry_points = detected_info.get('entry_points', [])
        if entry_points:
            getting_started += "\n### 🎯 Run the Application\n\n```bash\n"
            first_entry = entry_points[0]
            if first_entry.endswith('.py'):
                getting_started += f"python {first_entry}\n"
            elif first_entry.endswith(('.js', '.ts')):
                getting_started += f"node {first_entry}\n"
            getting_started += "```\n"

        return getting_started

    def _generate_usage_guide(self, real_characteristics: Dict, workflow_analysis: Dict, detected_info: Dict) -> str:
        """Generate usage guide."""
        usage = """## 📘 Usage Guide

### Basic Usage

"""

        # Get code examples
        code_examples = real_characteristics.get('code_examples', [])
        if code_examples:
            for i, example in enumerate(code_examples[:3], 1):
                example_file = example.get('file', 'example.py')
                example_code = example.get('code', '')

                if example_code:
                    # Detect language
                    if example_file.endswith('.py'):
                        lang = 'python'
                    elif example_file.endswith(('.js', '.jsx')):
                        lang = 'javascript'
                    elif example_file.endswith(('.ts', '.tsx')):
                        lang = 'typescript'
                    else:
                        lang = ''

                    usage += f"**Example {i}**: {example_file}\n\n```{lang}\n{example_code[:400]}\n```\n\n"

        # Add user journey if available
        user_journeys = workflow_analysis.get('user_journey', [])
        if user_journeys:
            usage += "### User Journey\n\n"
            for journey in user_journeys:
                journey_type = journey.get('type', 'User Journey')
                steps = journey.get('steps', [])

                usage += f"**{journey_type}**:\n\n"
                for i, step in enumerate(steps[:5], 1):
                    if isinstance(step, dict):
                        area = step.get('area', 'Step')
                        usage += f"{i}. {area}\n"
                    else:
                        usage += f"{i}. {step}\n"
                usage += "\n"

        return usage

    def _generate_api_documentation(self, real_characteristics: Dict) -> str:
        """Generate API documentation."""
        api_doc = """## 🌐 API Documentation

### Available Endpoints

"""

        real_apis = real_characteristics.get('real_apis', [])

        # Group by method
        from collections import defaultdict
        by_method = defaultdict(list)
        for api in real_apis:
            method = api.get('method', 'GET')
            by_method[str(method).upper()].append(api)

        # Document each endpoint
        for method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
            endpoints = by_method.get(method, [])
            if endpoints:
                api_doc += f"\n#### {method} Endpoints\n\n"
                for endpoint in endpoints:
                    path = endpoint.get('path', '/')
                    framework = endpoint.get('framework', '')
                    file_path = endpoint.get('file', '')

                    api_doc += f"**`{method} {path}`**\n\n"
                    api_doc += f"- Framework: {framework}\n"
                    api_doc += f"- Location: `{file_path}`\n\n"

        # Add example request
        if real_apis:
            first_api = real_apis[0]
            api_doc += "### Example Request\n\n```bash\n"
            api_doc += f"curl -X {first_api.get('method', 'GET')} \\\n"
            api_doc += f"  http://localhost:8000{first_api.get('path', '/')} \\\n"
            api_doc += "  -H 'Content-Type: application/json'\n"
            api_doc += "```\n"

        return api_doc

    def _generate_configuration_guide(self, real_characteristics: Dict) -> str:
        """Generate configuration guide."""
        config = """## ⚙️ Configuration

### Environment Variables

"""

        config_info = real_characteristics.get('real_configs', {})
        env_vars = config_info.get('env_vars', [])

        if env_vars:
            config += "The following environment variables are used:\n\n"
            config += "| Variable | Description |\n"
            config += "|----------|-------------|\n"

            for var in env_vars[:20]:
                # Infer description from variable name
                desc = self._infer_env_var_description(var)
                config += f"| `{var}` | {desc} |\n"

            config += "\n"
        else:
            config += "Configuration is handled through config files or command-line arguments.\n\n"

        # List config files
        config_files = config_info.get('config_files', [])
        if config_files:
            config += "### Configuration Files\n\n"
            for file in config_files:
                config += f"- `{file}`\n"
            config += "\n"

        return config

    def _generate_project_structure(self, analysis_result: Dict, real_characteristics: Dict) -> str:
        """Generate project structure."""
        structure = """## 📂 Project Structure

```
"""

        # Get directory structure
        project_structure = analysis_result.get('project_structure', {})

        if project_structure:
            structure += self._format_tree(project_structure, '', 3)

        structure += "```\n\n"

        # Add component descriptions
        arch_components = real_characteristics.get('architecture_components', {})
        if arch_components:
            structure += "### Directory Descriptions\n\n"

            for comp_type, components in arch_components.items():
                for comp in components:
                    directory = comp.get('directory', 'unknown')
                    file_count = comp.get('file_count', 0)
                    structure += f"- **`{directory}/`**: {comp_type} ({file_count} files)\n"

        return structure

    def _format_tree(self, node: Dict, prefix: str, max_depth: int, current_depth: int = 0) -> str:
        """Format directory tree."""
        if current_depth >= max_depth:
            return ""

        result = ""
        name = node.get('name', 'root')

        if current_depth == 0:
            result += f"{name}/\n"

        files = node.get('files', [])
        subdirs = node.get('subdirectories', [])

        # Show files
        for i, file_info in enumerate(files[:5]):
            file_name = file_info.get('name', 'file')
            is_last = (i == len(files[:5]) - 1) and not subdirs
            connector = "└── " if is_last else "├── "
            result += f"{prefix}{connector}{file_name}\n"

        # Show subdirs
        for i, subdir in enumerate(subdirs[:8]):
            is_last = i == len(subdirs[:8]) - 1
            connector = "└── " if is_last else "├── "
            extension = "    " if is_last else "│   "

            subdir_name = subdir.get('name', 'dir')
            result += f"{prefix}{connector}{subdir_name}/\n"
            result += self._format_tree(subdir, prefix + extension, max_depth, current_depth + 1)

        return result

    def _generate_development_guide(self, detected_info: Dict, real_characteristics: Dict) -> str:
        """Generate development guide."""
        dev = """## 👨‍💻 Development Guide

### Setting Up Development Environment

"""

        if detected_info.get('has_tests'):
            dev += """### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.
```

"""

        dev += """### Code Style

Follow the existing code style in the project. Use linters and formatters:

```bash
# Format code
black .

# Check linting
flake8 .
```

"""

        if detected_info.get('has_ci'):
            dev += "### Continuous Integration\n\n"
            dev += "All pull requests are automatically tested via CI/CD pipeline.\n\n"

        return dev

    def _generate_troubleshooting(self) -> str:
        """Generate troubleshooting section."""
        return """## 🔧 Troubleshooting

### Common Issues

**Issue**: Installation fails
- **Solution**: Ensure you have the correct version of Python/Node.js installed
- Check that all system dependencies are available

**Issue**: Application won't start
- **Solution**: Verify environment variables are set correctly
- Check that all required services (database, cache, etc.) are running

**Issue**: Tests failing
- **Solution**: Make sure you're in a virtual environment
- Run `pip install -e .` to install in development mode

### Getting Help

- Check the [Issues](https://github.com) page for known problems
- Open a new issue if you encounter a bug
- Join our community chat for support

"""

    def _generate_tech_stack(self, detected_info: Dict, analysis_result: Dict) -> str:
        """Generate technology stack."""
        stack = """## 💻 Technology Stack

"""

        # Languages
        languages = detected_info.get('languages', {})
        if languages:
            stack += "### Languages\n\n"
            for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
                stack += f"- **{lang}** ({count} files)\n"
            stack += "\n"

        # Frameworks
        frameworks = detected_info.get('frameworks', [])
        if frameworks:
            stack += "### Frameworks & Libraries\n\n"
            for fw in frameworks:
                stack += f"- **{fw.get('name')}** - {fw.get('type', 'library').title()}\n"
            stack += "\n"

        # Dependencies
        deps = analysis_result.get('dependencies', [])
        if deps:
            stack += "### Key Dependencies\n\n"
            for dep in deps[:15]:
                if isinstance(dep, dict):
                    name = dep.get('name', '')
                    version = dep.get('version', '')
                    stack += f"- {name} {version}\n"
                else:
                    stack += f"- {dep}\n"

        return stack

    def _generate_contributing(self) -> str:
        """Generate contributing section."""
        return """## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Guidelines

- Write clear, concise commit messages
- Add tests for new features
- Update documentation as needed
- Follow the existing code style
- Be respectful and constructive

"""

    def _generate_license_section(self, detected_info: Dict) -> str:
        """Generate license section."""
        license_name = detected_info.get('license', 'MIT')
        author = detected_info.get('author', {})

        license_section = f"""## 📄 License

This project is licensed under the **{license_name} License**.

"""

        if author.get('name'):
            license_section += f"**Created by**: {author.get('name')}"
            if author.get('email'):
                license_section += f" ({author.get('email')})"
            license_section += "\n\n"

        license_section += """---

<div align="center">

**⭐ If you find this project useful, please consider giving it a star! ⭐**

Made with ❤️ by the community

</div>
"""

        return license_section

    # Helper methods

    def _get_language_version(self, language: str) -> str:
        """Get typical version for language."""
        versions = {
            'Python': '3.8+',
            'JavaScript': 'ES6+',
            'TypeScript': '4.0+',
            'Java': '11+',
            'Go': '1.18+',
            'Rust': '1.60+',
        }
        return versions.get(language, 'latest')

    def _infer_env_var_description(self, var_name: str) -> str:
        """Infer description from environment variable name."""
        var_lower = var_name.lower()

        if 'api' in var_lower and 'key' in var_lower:
            return "API authentication key"
        elif 'secret' in var_lower:
            return "Secret key for encryption"
        elif 'database' in var_lower or 'db' in var_lower:
            return "Database connection string"
        elif 'port' in var_lower:
            return "Application port number"
        elif 'host' in var_lower:
            return "Host address"
        elif 'url' in var_lower:
            return "Service URL"
        elif 'token' in var_lower:
            return "Authentication token"
        elif 'email' in var_lower:
            return "Email configuration"
        elif 'debug' in var_lower:
            return "Debug mode flag"
        else:
            return "Configuration setting"
