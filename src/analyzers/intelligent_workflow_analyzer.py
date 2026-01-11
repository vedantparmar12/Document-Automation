"""
Intelligent Workflow Analyzer

Understands the COMPLETE project workflow by analyzing:
- Entry points and main execution flow
- Data flow between components
- User interaction patterns
- External service integrations
- Background processes and workers
"""

import os
import ast
import re
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


class IntelligentWorkflowAnalyzer:
    """Analyzes and understands complete project workflow."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.entry_points = []
        self.workflows = []
        self.data_flows = []
        self.user_journeys = []

    def analyze_complete_workflow(self) -> Dict[str, Any]:
        """Perform comprehensive workflow analysis."""
        logger.info(f"Analyzing workflow for: {self.project_root}")

        workflow_analysis = {
            'project_purpose': self._understand_project_purpose(),
            'execution_flow': self._analyze_execution_flow(),
            'data_flow': self._analyze_data_flow(),
            'user_journey': self._analyze_user_journey(),
            'integrations': self._analyze_integrations(),
            'workflows': self._extract_workflows(),
            'key_processes': self._identify_key_processes(),
        }

        return workflow_analysis

    def _understand_project_purpose(self) -> Dict[str, Any]:
        """Understand the main purpose of the project."""
        purpose = {
            'type': 'unknown',
            'primary_function': '',
            'target_users': [],
            'problem_solved': '',
            'key_value': ''
        }

        # Analyze README for purpose
        readme_files = ['README.md', 'README.rst', 'README.txt']
        for readme in readme_files:
            readme_path = self.project_root / readme
            if readme_path.exists():
                content = readme_path.read_text(encoding='utf-8', errors='ignore')

                # Extract first meaningful paragraph
                lines = content.split('\n')
                for i, line in enumerate(lines[:30]):
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('![') and len(line) > 50:
                        purpose['problem_solved'] = line[:300]
                        break

                # Detect project type from content
                content_lower = content.lower()
                if any(word in content_lower for word in ['api', 'rest', 'endpoint', 'server']):
                    purpose['type'] = 'API Service'
                elif any(word in content_lower for word in ['web app', 'website', 'frontend']):
                    purpose['type'] = 'Web Application'
                elif any(word in content_lower for word in ['cli', 'command', 'terminal']):
                    purpose['type'] = 'CLI Tool'
                elif any(word in content_lower for word in ['library', 'package', 'sdk']):
                    purpose['type'] = 'Library/Package'
                elif any(word in content_lower for word in ['automation', 'bot', 'script']):
                    purpose['type'] = 'Automation Tool'
                elif any(word in content_lower for word in ['mcp', 'model context protocol']):
                    purpose['type'] = 'MCP Server'

        # Analyze code structure for purpose
        if purpose['type'] == 'unknown':
            has_main = any((self.project_root / f).exists() for f in ['main.py', 'app.py', '__main__.py'])
            has_routes = any((self.project_root / d).exists() for d in ['routes', 'api', 'endpoints'])
            has_cli = any((self.project_root / f).exists() for f in ['cli.py', 'commands.py'])

            if has_routes:
                purpose['type'] = 'API Service'
            elif has_cli:
                purpose['type'] = 'CLI Tool'
            elif has_main:
                purpose['type'] = 'Application'

        return purpose

    def _analyze_execution_flow(self) -> List[Dict[str, Any]]:
        """Analyze the main execution flow of the application."""
        flows = []

        # Find entry points
        entry_candidates = [
            'main.py', 'app.py', '__main__.py', 'server.py', 'run.py',
            'cli.py', 'manage.py', 'index.js', 'index.ts', 'main.go'
        ]

        for candidate in entry_candidates:
            entry_path = self.project_root / candidate
            if entry_path.exists():
                flow = self._trace_execution_from_entry(entry_path)
                if flow:
                    flows.append(flow)

        # Also check for if __name__ == "__main__" blocks
        for py_file in self.project_root.rglob('*.py'):
            if self._should_skip_path(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                if 'if __name__ == "__main__"' in content:
                    flow = self._trace_execution_from_entry(py_file)
                    if flow and flow not in flows:
                        flows.append(flow)
            except:
                continue

        return flows[:5]  # Top 5 execution flows

    def _trace_execution_from_entry(self, entry_file: Path) -> Optional[Dict[str, Any]]:
        """Trace execution flow from an entry point."""
        try:
            content = entry_file.read_text(encoding='utf-8', errors='ignore')

            flow = {
                'entry_point': str(entry_file.relative_to(self.project_root)),
                'steps': [],
                'calls': [],
                'imports': []
            }

            # Parse AST
            tree = ast.parse(content)

            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        flow['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        flow['imports'].append(node.module)

            # Find main execution
            for node in ast.walk(tree):
                # Look for if __name__ == "__main__" block
                if isinstance(node, ast.If):
                    # Check if it's the main block
                    if self._is_main_block(node):
                        # Extract function calls in main block
                        for item in node.body:
                            if isinstance(item, ast.Expr) and isinstance(item.value, ast.Call):
                                func_name = self._get_call_name(item.value)
                                if func_name:
                                    flow['steps'].append(f"Call {func_name}")
                                    flow['calls'].append(func_name)

            # If no main block, look for top-level function calls
            if not flow['steps']:
                for node in ast.iter_child_nodes(tree):
                    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                        func_name = self._get_call_name(node.value)
                        if func_name:
                            flow['steps'].append(f"Initialize {func_name}")
                            flow['calls'].append(func_name)

            return flow if (flow['steps'] or flow['calls']) else None

        except Exception as e:
            logger.debug(f"Could not trace execution from {entry_file}: {e}")
            return None

    def _analyze_data_flow(self) -> List[Dict[str, Any]]:
        """Analyze how data flows through the system."""
        data_flows = []

        # Look for database operations
        db_operations = self._find_database_operations()
        if db_operations:
            data_flows.append({
                'type': 'Database',
                'description': 'Data persistence and retrieval',
                'operations': db_operations
            })

        # Look for API calls
        api_calls = self._find_api_calls()
        if api_calls:
            data_flows.append({
                'type': 'External APIs',
                'description': 'External service integrations',
                'operations': api_calls
            })

        # Look for file operations
        file_ops = self._find_file_operations()
        if file_ops:
            data_flows.append({
                'type': 'File System',
                'description': 'File reading and writing',
                'operations': file_ops
            })

        # Look for message queues/events
        queue_ops = self._find_queue_operations()
        if queue_ops:
            data_flows.append({
                'type': 'Message Queue',
                'description': 'Asynchronous message processing',
                'operations': queue_ops
            })

        return data_flows

    def _analyze_user_journey(self) -> List[Dict[str, Any]]:
        """Analyze typical user journeys through the system."""
        journeys = []

        # For web apps, analyze routes
        routes = self._find_routes()
        if routes:
            web_journey = {
                'type': 'Web User Journey',
                'steps': [],
                'endpoints': routes
            }

            # Organize routes into logical journey
            grouped_routes = defaultdict(list)
            for route in routes:
                path = route.get('path', '')
                # Group by first path segment
                if '/' in path[1:]:
                    group = path.split('/')[1]
                    grouped_routes[group].append(route)
                else:
                    grouped_routes['root'].append(route)

            for group, group_routes in grouped_routes.items():
                web_journey['steps'].append({
                    'area': group.title(),
                    'endpoints': len(group_routes),
                    'actions': [r.get('method', 'GET') for r in group_routes]
                })

            journeys.append(web_journey)

        # For CLI apps, analyze commands
        commands = self._find_cli_commands()
        if commands:
            cli_journey = {
                'type': 'CLI User Journey',
                'steps': [],
                'commands': commands
            }
            journeys.append(cli_journey)

        return journeys

    def _analyze_integrations(self) -> List[Dict[str, Any]]:
        """Analyze external service integrations."""
        integrations = []

        # Look for common integration patterns in imports and code
        integration_patterns = {
            'AWS': ['boto3', 'botocore', 'aws'],
            'Google Cloud': ['google-cloud', 'google.cloud', 'gcp'],
            'Azure': ['azure', 'azure-'],
            'Database': ['sqlalchemy', 'psycopg2', 'pymongo', 'redis', 'mysql'],
            'Email': ['sendgrid', 'mailgun', 'smtp', 'email'],
            'Payment': ['stripe', 'paypal', 'braintree'],
            'Authentication': ['oauth', 'auth0', 'jwt', 'passport'],
            'Storage': ['s3', 'gcs', 'azure-storage'],
            'Monitoring': ['sentry', 'datadog', 'newrelic'],
            'Analytics': ['analytics', 'mixpanel', 'amplitude'],
        }

        # Scan dependencies and imports
        all_imports = set()
        for py_file in self.project_root.rglob('*.py'):
            if self._should_skip_path(py_file):
                continue
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                imports = re.findall(r'(?:from|import)\s+([\w\.\-]+)', content)
                all_imports.update(imports)
            except:
                continue

        # Match patterns
        for service, patterns in integration_patterns.items():
            matched = [p for p in patterns if any(p in imp.lower() for imp in all_imports)]
            if matched:
                integrations.append({
                    'service': service,
                    'libraries': matched[:3],
                    'type': 'External Service'
                })

        return integrations

    def _extract_workflows(self) -> List[Dict[str, Any]]:
        """Extract specific workflows from the code."""
        workflows = []

        # Look for workflow-related classes
        workflow_keywords = ['workflow', 'pipeline', 'process', 'handler', 'executor', 'task']

        for py_file in self.project_root.rglob('*.py'):
            if self._should_skip_path(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        name_lower = node.name.lower()
                        if any(kw in name_lower for kw in workflow_keywords):
                            methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef) and not m.name.startswith('_')]

                            workflows.append({
                                'name': node.name,
                                'file': str(py_file.relative_to(self.project_root)),
                                'methods': methods[:10],
                                'type': 'Workflow Class',
                                'docstring': ast.get_docstring(node) or ''
                            })
            except:
                continue

        return workflows[:10]

    def _identify_key_processes(self) -> List[Dict[str, Any]]:
        """Identify key business processes in the system."""
        processes = []

        # Look for process-indicating function names
        process_verbs = [
            'create', 'generate', 'process', 'handle', 'execute',
            'validate', 'transform', 'calculate', 'analyze', 'send',
            'fetch', 'update', 'delete', 'sync', 'export', 'import'
        ]

        process_functions = defaultdict(list)

        for py_file in self.project_root.rglob('*.py'):
            if self._should_skip_path(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        name_lower = node.name.lower()
                        for verb in process_verbs:
                            if name_lower.startswith(verb) and not name_lower.startswith('_'):
                                process_functions[verb].append({
                                    'function': node.name,
                                    'file': str(py_file.relative_to(self.project_root)),
                                    'params': [arg.arg for arg in node.args.args]
                                })
                                break
            except:
                continue

        # Group by verb to identify processes
        for verb, functions in process_functions.items():
            if functions:
                processes.append({
                    'process': f"{verb.title()} Operations",
                    'functions': functions[:5],
                    'count': len(functions)
                })

        return processes[:15]

    # Helper methods

    def _find_database_operations(self) -> List[str]:
        """Find database operation patterns."""
        operations = []
        db_patterns = [
            r'\.query\(',
            r'\.filter\(',
            r'\.insert\(',
            r'\.update\(',
            r'\.delete\(',
            r'\.save\(',
            r'\.commit\(',
            r'cursor\.',
            r'execute\(',
        ]

        for py_file in self.project_root.rglob('*.py'):
            if self._should_skip_path(py_file):
                continue
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                for pattern in db_patterns:
                    if re.search(pattern, content):
                        operations.append(pattern.replace('\\', '').replace('(', ''))
                        if len(operations) >= 10:
                            return list(set(operations))
            except:
                continue

        return list(set(operations))

    def _find_api_calls(self) -> List[str]:
        """Find API call patterns."""
        calls = []
        api_patterns = [
            r'requests\.(get|post|put|delete)',
            r'httpx\.(get|post|put|delete)',
            r'fetch\(',
            r'axios\.',
            r'urllib\.request',
        ]

        for py_file in self.project_root.rglob('*.py'):
            if self._should_skip_path(py_file):
                continue
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                for pattern in api_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        calls.extend(matches if isinstance(matches[0], str) else [m[0] for m in matches])
            except:
                continue

        return list(set(calls))[:10]

    def _find_file_operations(self) -> List[str]:
        """Find file operation patterns."""
        operations = []
        file_patterns = [
            r'open\(',
            r'\.read\(',
            r'\.write\(',
            r'Path\(',
            r'os\.path',
            r'shutil\.',
        ]

        for py_file in self.project_root.rglob('*.py'):
            if self._should_skip_path(py_file):
                continue
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                for pattern in file_patterns:
                    if re.search(pattern, content):
                        operations.append(pattern.replace('\\', '').replace('(', ''))
            except:
                continue

        return list(set(operations))[:8]

    def _find_queue_operations(self) -> List[str]:
        """Find message queue operation patterns."""
        operations = []
        queue_patterns = [
            r'celery',
            r'rabbitmq',
            r'kafka',
            r'redis\..*publish',
            r'task\(',
            r'@app\.task',
        ]

        for py_file in self.project_root.rglob('*.py'):
            if self._should_skip_path(py_file):
                continue
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                for pattern in queue_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        operations.append(pattern)
            except:
                continue

        return list(set(operations))[:5]

    def _find_routes(self) -> List[Dict[str, Any]]:
        """Find web routes."""
        routes = []
        route_patterns = [
            (r'@app\.route\(["\']([^"\']+)["\']', 'Flask'),
            (r'@router\.(get|post|put|delete)\(["\']([^"\']+)["\']', 'FastAPI'),
            (r'path\(["\']([^"\']+)["\']', 'Django'),
        ]

        for py_file in self.project_root.rglob('*.py'):
            if self._should_skip_path(py_file):
                continue
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                for pattern, framework in route_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if isinstance(match, tuple):
                            routes.append({'path': match[-1], 'framework': framework, 'method': match[0] if len(match) > 1 else 'GET'})
                        else:
                            routes.append({'path': match, 'framework': framework})
            except:
                continue

        return routes[:30]

    def _find_cli_commands(self) -> List[Dict[str, Any]]:
        """Find CLI commands."""
        commands = []
        cli_patterns = [
            r'@click\.command\(\)',
            r'argparse\.',
            r'parser\.add_argument',
        ]

        for py_file in self.project_root.rglob('*.py'):
            if self._should_skip_path(py_file):
                continue
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                for pattern in cli_patterns:
                    if re.search(pattern, content):
                        # Try to extract command names
                        cmd_names = re.findall(r'def\s+(\w+)\s*\(', content)
                        commands.extend([{'name': name, 'file': str(py_file.relative_to(self.project_root))} for name in cmd_names[:5]])
            except:
                continue

        return commands[:15]

    def _is_main_block(self, node: ast.If) -> bool:
        """Check if an If node is the __main__ block."""
        try:
            if isinstance(node.test, ast.Compare):
                left = node.test.left
                if isinstance(left, ast.Name) and left.id == '__name__':
                    for comp in node.test.comparators:
                        if isinstance(comp, ast.Constant) and comp.value == '__main__':
                            return True
        except:
            pass
        return False

    def _get_call_name(self, call_node: ast.Call) -> Optional[str]:
        """Extract function name from Call node."""
        try:
            if isinstance(call_node.func, ast.Name):
                return call_node.func.id
            elif isinstance(call_node.func, ast.Attribute):
                return call_node.func.attr
        except:
            pass
        return None

    def _should_skip_path(self, path: Path) -> bool:
        """Check if path should be skipped."""
        skip_patterns = {
            '__pycache__', '.git', 'node_modules', 'venv', '.venv',
            'env', 'dist', 'build', '.pytest_cache', '.mypy_cache'
        }
        return any(skip in path.parts for skip in skip_patterns)
