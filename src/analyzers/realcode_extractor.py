"""
Real Code Characteristics Extractor

This module extracts REAL, UNIQUE characteristics from actual codebases
to generate truly customized documentation instead of using generic templates.
"""

import os
import re
import ast
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)


class RealCodeExtractor:
    """Extracts real, unique characteristics from actual codebases."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.cache = {}

    def extract_all_characteristics(self) -> Dict[str, Any]:
        """Extract all unique characteristics from the codebase."""
        logger.info(f"Extracting real characteristics from: {self.project_root}")

        characteristics = {
            'real_features': self._extract_real_features(),
            'real_classes': self._extract_class_info(),
            'real_functions': self._extract_function_info(),
            'real_apis': self._extract_api_endpoints(),
            'real_configs': self._extract_config_patterns(),
            'real_models': self._extract_data_models(),
            'real_workflows': self._extract_workflow_patterns(),
            'code_examples': self._extract_code_examples(),
            'architecture_components': self._extract_architecture_components(),
            'unique_patterns': self._extract_unique_patterns(),
            'readme_content': self._extract_readme_content()
        }

        logger.info(f"Extracted {len(characteristics['real_classes'])} classes, "
                   f"{len(characteristics['real_functions'])} functions, "
                   f"{len(characteristics['real_features'])} features")

        return characteristics

    def _extract_readme_content(self) -> Dict[str, Any]:
        """Extract content from actual README file."""
        readme_files = ['README.md', 'README.rst', 'README.txt', 'README']

        for readme in readme_files:
            readme_path = self.project_root / readme
            if readme_path.exists():
                try:
                    content = readme_path.read_text(encoding='utf-8', errors='ignore')

                    # Extract sections
                    sections = {}
                    current_section = 'intro'
                    current_content = []

                    for line in content.split('\n'):
                        if line.strip().startswith('#'):
                            if current_content:
                                sections[current_section] = '\n'.join(current_content)
                            current_section = line.strip('#').strip().lower()
                            current_content = []
                        else:
                            current_content.append(line)

                    if current_content:
                        sections[current_section] = '\n'.join(current_content)

                    # Extract first paragraph as description
                    description = ''
                    for line in content.split('\n'):
                        line = line.strip()
                        if line and not line.startswith('#') and not line.startswith('![') and not line.startswith('[!'):
                            description = line
                            break

                    return {
                        'exists': True,
                        'description': description[:500] if description else '',
                        'sections': sections,
                        'full_content': content[:2000]  # First 2000 chars
                    }
                except Exception as e:
                    logger.warning(f"Could not parse README: {e}")

        return {'exists': False, 'description': '', 'sections': {}, 'full_content': ''}

    def _extract_real_features(self) -> List[Dict[str, Any]]:
        """Extract REAL features by analyzing actual code patterns."""
        features = []

        # Analyze Python files for actual functionality
        for py_file in self.project_root.rglob('*.py'):
            if self._should_skip_path(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                tree = ast.parse(content)

                # Extract features from class names and docstrings
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        feature = self._infer_feature_from_class(node, py_file)
                        if feature:
                            features.append(feature)
                    elif isinstance(node, ast.FunctionDef):
                        if node.name.startswith('handle_') or node.name.startswith('process_'):
                            feature = self._infer_feature_from_function(node, py_file)
                            if feature:
                                features.append(feature)
            except Exception as e:
                logger.debug(f"Could not parse {py_file}: {e}")
                continue

        # Deduplicate and rank by importance
        unique_features = self._deduplicate_features(features)
        return unique_features[:20]  # Top 20 features

    def _infer_feature_from_class(self, node: ast.ClassDef, file_path: Path) -> Optional[Dict[str, Any]]:
        """Infer feature from a class definition."""
        class_name = node.name
        docstring = ast.get_docstring(node) or ''

        # Skip base classes and internal classes
        if class_name.startswith('_') or class_name in ['Base', 'Abstract']:
            return None

        # Extract methods
        methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
        public_methods = [m for m in methods if not m.startswith('_')]

        # Infer purpose from class name and methods
        purpose = self._infer_purpose_from_name(class_name)

        if not purpose and docstring:
            purpose = docstring.split('\n')[0][:200]

        if not purpose and public_methods:
            purpose = f"Handles {', '.join(public_methods[:3])}"

        return {
            'name': self._clean_class_name(class_name),
            'type': 'class_feature',
            'purpose': purpose,
            'methods': public_methods[:5],
            'file': str(file_path.relative_to(self.project_root)),
            'confidence': 'high' if docstring else 'medium'
        }

    def _infer_feature_from_function(self, node: ast.FunctionDef, file_path: Path) -> Optional[Dict[str, Any]]:
        """Infer feature from a function definition."""
        func_name = node.name
        docstring = ast.get_docstring(node) or ''

        purpose = self._infer_purpose_from_name(func_name)
        if not purpose and docstring:
            purpose = docstring.split('\n')[0][:200]

        return {
            'name': self._clean_function_name(func_name),
            'type': 'function_feature',
            'purpose': purpose,
            'file': str(file_path.relative_to(self.project_root)),
            'confidence': 'high' if docstring else 'medium'
        }

    def _extract_class_info(self) -> List[Dict[str, Any]]:
        """Extract information about actual classes in the codebase."""
        classes = []

        for py_file in self.project_root.rglob('*.py'):
            if self._should_skip_path(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if not node.name.startswith('_'):
                            classes.append({
                                'name': node.name,
                                'docstring': ast.get_docstring(node) or '',
                                'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef) and not m.name.startswith('_')][:10],
                                'file': str(py_file.relative_to(self.project_root)),
                                'bases': [self._get_base_name(b) for b in node.bases]
                            })
            except Exception as e:
                logger.debug(f"Could not parse {py_file}: {e}")
                continue

        return classes[:50]  # Top 50 classes

    def _extract_function_info(self) -> List[Dict[str, Any]]:
        """Extract information about actual functions."""
        functions = []

        for py_file in self.project_root.rglob('*.py'):
            if self._should_skip_path(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if not node.name.startswith('_'):
                            # Get parameters
                            params = [arg.arg for arg in node.args.args]

                            functions.append({
                                'name': node.name,
                                'docstring': ast.get_docstring(node) or '',
                                'params': params,
                                'file': str(py_file.relative_to(self.project_root)),
                                'is_async': isinstance(node, ast.AsyncFunctionDef)
                            })
            except Exception as e:
                logger.debug(f"Could not parse {py_file}: {e}")
                continue

        return functions[:100]  # Top 100 functions

    def _extract_api_endpoints(self) -> List[Dict[str, Any]]:
        """Extract REAL API endpoints from actual code."""
        endpoints = []

        # Pattern matchers for different frameworks
        patterns = {
            'flask': [
                (r'@app\.route\(["\']([^"\']+)["\'](?:,\s*methods=\[([^\]]+)\])?', 'Flask'),
                (r'@bp\.route\(["\']([^"\']+)["\'](?:,\s*methods=\[([^\]]+)\])?', 'Flask Blueprint'),
            ],
            'fastapi': [
                (r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']', 'FastAPI'),
                (r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']', 'FastAPI Router'),
            ],
            'django': [
                (r'path\(["\']([^"\']+)["\'],\s*([^,]+)', 'Django URL'),
            ]
        }

        for py_file in self.project_root.rglob('*.py'):
            if self._should_skip_path(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')

                # Check each framework pattern
                for framework, framework_patterns in patterns.items():
                    for pattern, framework_name in framework_patterns:
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            if framework == 'fastapi':
                                method = match.group(1).upper()
                                path = match.group(2)
                            elif framework == 'flask':
                                path = match.group(1)
                                methods = match.group(2) if match.lastindex >= 2 else 'GET'
                                method = methods
                            else:
                                path = match.group(1)
                                method = 'GET'

                            endpoints.append({
                                'path': path,
                                'method': method,
                                'framework': framework_name,
                                'file': str(py_file.relative_to(self.project_root))
                            })
            except Exception as e:
                logger.debug(f"Could not parse {py_file}: {e}")
                continue

        return endpoints[:50]  # Top 50 endpoints

    def _extract_config_patterns(self) -> Dict[str, Any]:
        """Extract actual configuration patterns from the codebase."""
        configs = {
            'env_vars': [],
            'config_files': [],
            'settings': []
        }

        # Find .env, config files
        for config_file in ['.env.example', 'config.py', 'settings.py', 'config.json', 'config.yaml']:
            config_path = self.project_root / config_file
            if config_path.exists():
                configs['config_files'].append(config_file)

                # Extract env vars
                if config_file.endswith('.env') or 'env' in config_file:
                    try:
                        content = config_path.read_text(encoding='utf-8', errors='ignore')
                        env_vars = re.findall(r'^([A-Z_]+)=', content, re.MULTILINE)
                        configs['env_vars'].extend(env_vars)
                    except Exception:
                        pass

        # Search for os.getenv or os.environ usage
        for py_file in self.project_root.rglob('*.py'):
            if self._should_skip_path(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                env_vars = re.findall(r'os\.(?:getenv|environ\.get)\(["\']([^"\']+)["\']', content)
                configs['env_vars'].extend(env_vars)
            except Exception:
                pass

        configs['env_vars'] = list(set(configs['env_vars']))[:30]
        return configs

    def _extract_data_models(self) -> List[Dict[str, Any]]:
        """Extract actual data models and schemas."""
        models = []

        for py_file in self.project_root.rglob('*.py'):
            if self._should_skip_path(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check if it's a data model (has type hints or inherits from BaseModel)
                        has_type_hints = any(
                            isinstance(item, ast.AnnAssign)
                            for item in node.body
                        )

                        bases = [self._get_base_name(b) for b in node.bases]
                        is_model = any(
                            base in ['BaseModel', 'Model', 'DataClass', 'Schema']
                            for base in bases
                        )

                        if has_type_hints or is_model:
                            fields = []
                            for item in node.body:
                                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                                    field_name = item.target.id
                                    field_type = ast.unparse(item.annotation) if hasattr(ast, 'unparse') else 'Any'
                                    fields.append({'name': field_name, 'type': field_type})

                            models.append({
                                'name': node.name,
                                'fields': fields[:20],
                                'bases': bases,
                                'file': str(py_file.relative_to(self.project_root))
                            })
            except Exception as e:
                logger.debug(f"Could not parse {py_file}: {e}")
                continue

        return models[:30]  # Top 30 models

    def _extract_workflow_patterns(self) -> List[Dict[str, Any]]:
        """Extract actual workflow patterns from code."""
        workflows = []

        # Look for workflow-like patterns
        workflow_indicators = [
            'pipeline', 'workflow', 'process', 'handler', 'executor', 'runner', 'scheduler'
        ]

        for py_file in self.project_root.rglob('*.py'):
            if self._should_skip_path(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                        name_lower = node.name.lower()
                        if any(indicator in name_lower for indicator in workflow_indicators):
                            workflows.append({
                                'name': node.name,
                                'type': 'class' if isinstance(node, ast.ClassDef) else 'function',
                                'file': str(py_file.relative_to(self.project_root)),
                                'docstring': ast.get_docstring(node) or ''
                            })
            except Exception:
                continue

        return workflows[:20]

    def _extract_code_examples(self) -> List[Dict[str, Any]]:
        """Extract actual code snippets that can be used as examples."""
        examples = []

        # Look for main.py, app.py, example files
        example_files = []
        for pattern in ['main.py', 'app.py', '__main__.py', '*example*.py', 'demo.py']:
            example_files.extend(self.project_root.glob(f'**/{pattern}'))

        for ex_file in example_files[:5]:
            if self._should_skip_path(ex_file):
                continue

            try:
                content = ex_file.read_text(encoding='utf-8', errors='ignore')

                # Extract __main__ block or main function
                main_blocks = re.findall(
                    r'(?:if __name__ == ["\']__main__["\']:.*?$)|(?:def main\(\):.*?(?=\ndef|\nclass|\Z))',
                    content,
                    re.MULTILINE | re.DOTALL
                )

                for block in main_blocks[:2]:
                    if len(block) > 50 and len(block) < 1000:
                        examples.append({
                            'file': str(ex_file.relative_to(self.project_root)),
                            'code': block[:500],
                            'type': 'usage_example'
                        })
            except Exception:
                continue

        return examples[:5]

    def _extract_architecture_components(self) -> Dict[str, List[str]]:
        """Extract actual architectural components from directory structure."""
        components = defaultdict(list)

        # Map directory names to component types
        component_mapping = {
            'api': 'API Layer',
            'apis': 'API Layer',
            'routes': 'Routing Layer',
            'controllers': 'Controllers',
            'models': 'Data Models',
            'schemas': 'Data Schemas',
            'services': 'Services',
            'utils': 'Utilities',
            'helpers': 'Helper Functions',
            'middleware': 'Middleware',
            'auth': 'Authentication',
            'database': 'Database Layer',
            'db': 'Database Layer',
            'storage': 'Storage Layer',
            'cache': 'Caching Layer',
            'queue': 'Queue System',
            'workers': 'Background Workers',
            'tasks': 'Task Handlers',
            'processors': 'Data Processors',
            'parsers': 'Data Parsers',
            'validators': 'Validation Layer',
            'serializers': 'Serialization',
            'views': 'Views',
            'templates': 'Templates',
            'static': 'Static Assets',
            'frontend': 'Frontend',
            'backend': 'Backend',
            'core': 'Core Logic',
            'lib': 'Library',
            'plugins': 'Plugins',
            'extensions': 'Extensions',
        }

        # Scan directories
        for item in self.project_root.iterdir():
            if item.is_dir() and not item.name.startswith('.') and item.name not in ['__pycache__', 'node_modules']:
                comp_name = item.name.lower()
                if comp_name in component_mapping:
                    # List Python files in this component
                    py_files = list(item.rglob('*.py'))
                    if py_files:
                        components[component_mapping[comp_name]].append({
                            'directory': item.name,
                            'file_count': len(py_files),
                            'files': [f.name for f in py_files[:5]]
                        })

        return dict(components)

    def _extract_unique_patterns(self) -> Dict[str, Any]:
        """Extract unique patterns and characteristics specific to this codebase."""
        patterns = {
            'decorators_used': set(),
            'imports_used': Counter(),
            'naming_conventions': {},
            'code_style': {}
        }

        for py_file in self.project_root.rglob('*.py'):
            if self._should_skip_path(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')

                # Extract decorators
                decorators = re.findall(r'@(\w+)', content)
                patterns['decorators_used'].update(decorators)

                # Extract imports
                imports = re.findall(r'(?:from|import)\s+([\w.]+)', content)
                patterns['imports_used'].update(imports)

            except Exception:
                continue

        # Convert sets to lists for JSON serialization
        patterns['decorators_used'] = list(patterns['decorators_used'])[:30]
        patterns['imports_used'] = dict(patterns['imports_used'].most_common(50))

        return patterns

    # Helper methods

    def _should_skip_path(self, path: Path) -> bool:
        """Check if path should be skipped."""
        skip_patterns = {
            '__pycache__', '.git', 'node_modules', 'venv', '.venv',
            'env', 'dist', 'build', '.pytest_cache', '.mypy_cache',
            'htmlcov', '.tox', 'eggs', '.eggs'
        }

        parts = path.parts
        return any(skip in parts for skip in skip_patterns)

    def _infer_purpose_from_name(self, name: str) -> str:
        """Infer purpose from a class or function name."""
        # Convert CamelCase to words
        words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|\W|$)|\d+', name)
        words = [w.lower() for w in words]

        # Common action verbs
        actions = {
            'handler': 'handles',
            'processor': 'processes',
            'analyzer': 'analyzes',
            'generator': 'generates',
            'validator': 'validates',
            'parser': 'parses',
            'manager': 'manages',
            'controller': 'controls',
            'service': 'provides services for',
            'client': 'communicates with',
            'server': 'serves',
            'worker': 'performs background work for',
        }

        # Check for action words
        for action_word, verb in actions.items():
            if action_word in words:
                object_words = [w for w in words if w != action_word]
                if object_words:
                    return f"{verb} {' '.join(object_words)}"

        # Fallback
        if len(words) > 1:
            return f"handles {' '.join(words)}"

        return ''

    def _clean_class_name(self, name: str) -> str:
        """Convert class name to readable feature name."""
        # Remove common suffixes
        for suffix in ['Handler', 'Processor', 'Manager', 'Service', 'Controller']:
            if name.endswith(suffix):
                name = name[:-len(suffix)]

        # Convert to title case with spaces
        words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|\W|$)|\d+', name)
        return ' '.join(words).title()

    def _clean_function_name(self, name: str) -> str:
        """Convert function name to readable feature name."""
        # Remove common prefixes
        for prefix in ['handle_', 'process_', 'do_', 'run_', 'execute_']:
            if name.startswith(prefix):
                name = name[len(prefix):]

        return name.replace('_', ' ').title()

    def _get_base_name(self, node: ast.expr) -> str:
        """Get base class name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return 'object'

    def _deduplicate_features(self, features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate features and rank by importance."""
        seen_names = set()
        unique = []

        # Sort by confidence first
        features.sort(key=lambda x: (x.get('confidence', 'low') == 'high', len(x.get('purpose', ''))), reverse=True)

        for feature in features:
            name = feature['name'].lower()
            if name not in seen_names:
                seen_names.add(name)
                unique.append(feature)

        return unique
