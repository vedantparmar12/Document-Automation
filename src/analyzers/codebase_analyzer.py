"""
Codebase analyzer for different programming languages

This module provides specific analysis functions for extracting the structure,
dependencies, and components of a codebase in different programming languages.
"""

import os
import logging
import json
import re
from typing import List, Dict, Any

from src.analyzers.base_analyzer import BaseAnalyzer
from src.schemas import AnalysisOperationResult

logger = logging.getLogger(__name__)

class CodebaseAnalyzer(BaseAnalyzer):
    """
    Codebase analyzer implementation for different languages.
    
    Inherits from `BaseAnalyzer` to provide specific analysis implementation.
    """
    
    async def _analyze_dependencies(self) -> List[str]:
        """Analyze project dependencies."""
        logger.info(f"Analyzing dependencies for {self.path}")
        dependencies = []
        
        # Python dependencies
        requirements_files = ['requirements.txt', 'requirements.pip', 'requirements-dev.txt']
        for req_file in requirements_files:
            req_path = os.path.join(self.working_path, req_file)
            if os.path.exists(req_path):
                try:
                    with open(req_path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                # Extract package name (remove version specifiers)
                                pkg = line.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].strip()
                                if pkg:
                                    dependencies.append(pkg)
                except Exception as e:
                    logger.warning(f"Error reading {req_file}: {e}")
        
        # Check setup.py for dependencies
        setup_py = os.path.join(self.working_path, 'setup.py')
        if os.path.exists(setup_py):
            try:
                with open(setup_py, 'r') as f:
                    content = f.read()
                    # Basic parsing for install_requires
                    if 'install_requires' in content:
                        # This is a simple approach - could be improved with AST parsing
                        import re
                        pattern = r'install_requires\s*=\s*\[(.*?)\]'
                        match = re.search(pattern, content, re.DOTALL)
                        if match:
                            requires = match.group(1)
                            for line in requires.split(','):
                                line = line.strip().strip('"').strip("'")
                                if line:
                                    pkg = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                                    if pkg and pkg not in dependencies:
                                        dependencies.append(pkg)
            except Exception as e:
                logger.warning(f"Error reading setup.py: {e}")
        
        # Node.js dependencies
        package_json = os.path.join(self.working_path, 'package.json')
        if os.path.exists(package_json):
            try:
                import json
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    for dep_type in ['dependencies', 'devDependencies']:
                        if dep_type in data:
                            dependencies.extend(list(data[dep_type].keys()))
            except Exception as e:
                logger.warning(f"Error reading package.json: {e}")
        
        # Remove duplicates and return
        return list(set(dependencies))

    async def _extract_api_endpoints(self) -> List[Dict[str, Any]]:
        """Extract API endpoints."""
        # Placeholder for API extraction logic
        logger.info(f"Extracting API endpoints for {self.path}")
        return []

    async def _analyze_architecture(self) -> Dict[str, Any]:
        """Analyze architecture."""
        # Placeholder for architecture analysis
        logger.info(f"Analyzing architecture for {self.path}")
        return {}

    async def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate code metrics."""
        logger.info(f"Calculating metrics for {self.path}")
        
        metrics = {
            'total_files': 0,
            'total_lines': 0,
            'file_types': {},
            'largest_file': None,
            'languages': {}
        }
        
        # Count files and lines
        def analyze_directory(path):
            try:
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    
                    if os.path.isfile(item_path):
                        metrics['total_files'] += 1
                        
                        # Get file extension
                        _, ext = os.path.splitext(item_path)
                        if ext:
                            metrics['file_types'][ext] = metrics['file_types'].get(ext, 0) + 1
                        
                        # Count lines in text files
                        try:
                            with open(item_path, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = len(f.readlines())
                                metrics['total_lines'] += lines
                                
                                # Track largest file
                                if not metrics['largest_file'] or lines > metrics['largest_file']['lines']:
                                    metrics['largest_file'] = {
                                        'path': item_path.replace(self.working_path, ''),
                                        'lines': lines
                                    }
                        except:
                            pass
                    
                    elif os.path.isdir(item_path) and not item.startswith('.'):
                        # Recursively analyze subdirectories
                        analyze_directory(item_path)
            except Exception as e:
                logger.warning(f"Error analyzing directory {path}: {e}")
        
        analyze_directory(self.working_path)
        
        # Determine primary language based on file extensions
        language_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.cpp': 'C++',
            '.c': 'C',
            '.rb': 'Ruby',
            '.php': 'PHP'
        }
        
        for ext, count in metrics['file_types'].items():
            if ext in language_extensions:
                lang = language_extensions[ext]
                metrics['languages'][lang] = metrics['languages'].get(lang, 0) + count
        
        return metrics
    
    # Additional methods required by documentation_tools.py
    
    async def analyze_with_pagination(self) -> AnalysisOperationResult:
        """Analyze codebase with pagination support."""
        logger.info(f"Analyzing with pagination for {self.path}")
        
        # For now, just delegate to the regular analyze method
        # In a full implementation, this would handle chunking and pagination
        return await self.analyze()
    
    async def _detect_frameworks(self) -> List[Dict[str, Any]]:
        """Detect frameworks and technology stack."""
        logger.info(f"Detecting frameworks for {self.path}")
        
        frameworks = []
        
        # Check for Python frameworks
        requirements_files = ['requirements.txt', 'setup.py', 'pyproject.toml']
        for req_file in requirements_files:
            req_path = os.path.join(self.working_path, req_file)
            if os.path.exists(req_path):
                try:
                    with open(req_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        
                        # Check for common Python frameworks
                        if 'fastapi' in content:
                            frameworks.append({
                                'name': 'FastAPI',
                                'category': 'web_framework',
                                'confidence': 0.9,
                                'description': 'Modern, fast web framework for building APIs'
                            })
                        if 'flask' in content:
                            frameworks.append({
                                'name': 'Flask',
                                'category': 'web_framework',
                                'confidence': 0.9,
                                'description': 'Lightweight WSGI web application framework'
                            })
                        if 'django' in content:
                            frameworks.append({
                                'name': 'Django',
                                'category': 'web_framework',
                                'confidence': 0.9,
                                'description': 'High-level Python Web framework'
                            })
                        if 'streamlit' in content:
                            frameworks.append({
                                'name': 'Streamlit',
                                'category': 'ui_framework',
                                'confidence': 0.8,
                                'description': 'Framework for creating data apps'
                            })
                        if 'langchain' in content:
                            frameworks.append({
                                'name': 'LangChain',
                                'category': 'ai_framework',
                                'confidence': 0.8,
                                'description': 'Framework for developing LLM applications'
                            })
                except Exception as e:
                    logger.warning(f"Error reading {req_file}: {e}")
        
        # Check for Node.js frameworks
        package_json = os.path.join(self.working_path, 'package.json')
        if os.path.exists(package_json):
            try:
                with open(package_json, 'r', encoding='utf-8', errors='ignore') as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    
                    if 'react' in deps:
                        frameworks.append({
                            'name': 'React',
                            'category': 'frontend_framework',
                            'confidence': 0.9,
                            'description': 'JavaScript library for building user interfaces'
                        })
                    if 'express' in deps:
                        frameworks.append({
                            'name': 'Express.js',
                            'category': 'web_framework',
                            'confidence': 0.9,
                            'description': 'Fast, unopinionated web framework for Node.js'
                        })
                    if 'next' in deps:
                        frameworks.append({
                            'name': 'Next.js',
                            'category': 'fullstack_framework',
                            'confidence': 0.9,
                            'description': 'React framework for production'
                        })
            except Exception as e:
                logger.warning(f"Error reading package.json: {e}")
        
        return frameworks
    
    async def _analyze_database_schemas(self) -> List[Dict[str, Any]]:
        """Analyze database schemas from various sources."""
        logger.info(f"Analyzing database schemas for {self.path}")
        
        schemas = []
        
        # Look for SQL files
        sql_files = []
        for root, dirs, files in os.walk(self.working_path):
            for file in files:
                if file.endswith(('.sql', '.ddl')):
                    sql_files.append(os.path.join(root, file))
        
        # Analyze SQL files
        for sql_file in sql_files:
            try:
                with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Basic SQL parsing for CREATE TABLE statements
                    tables = self._parse_sql_tables(content)
                    if tables:
                        schemas.append({
                            'source': sql_file.replace(self.working_path, ''),
                            'type': 'sql',
                            'tables': tables
                        })
            except Exception as e:
                logger.warning(f"Error reading SQL file {sql_file}: {e}")
        
        # Look for Python ORM models (SQLAlchemy, Django, etc.)
        python_files = []
        for root, dirs, files in os.walk(self.working_path):
            for file in files:
                if file.endswith('.py') and ('model' in file.lower() or 'schema' in file.lower()):
                    python_files.append(os.path.join(root, file))
        
        # Analyze Python model files
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Look for ORM patterns
                    if any(pattern in content for pattern in ['class', 'Model', 'Table', 'Column']):
                        models = self._parse_python_models(content)
                        if models:
                            schemas.append({
                                'source': py_file.replace(self.working_path, ''),
                                'type': 'orm',
                                'models': models
                            })
            except Exception as e:
                logger.warning(f"Error reading Python file {py_file}: {e}")
        
        return schemas
    
    async def _parse_code_ast(self) -> List[Dict[str, Any]]:
        """Parse code using AST for detailed analysis."""
        logger.info(f"Parsing AST for {self.path}")
        
        ast_data = []
        
        # Look for Python files
        python_files = []
        for root, dirs, files in os.walk(self.working_path):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        # Analyze Python files with AST
        for py_file in python_files[:20]:  # Limit to first 20 files for performance
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Basic AST analysis
                    import ast as python_ast
                    try:
                        tree = python_ast.parse(content)
                        
                        classes = []
                        functions = []
                        imports = []
                        
                        for node in python_ast.walk(tree):
                            if isinstance(node, python_ast.ClassDef):
                                classes.append({
                                    'name': node.name,
                                    'line': node.lineno,
                                    'methods': [method.name for method in node.body if isinstance(method, python_ast.FunctionDef)]
                                })
                            elif isinstance(node, python_ast.FunctionDef):
                                if not any(node.lineno >= cls.lineno for cls in python_ast.walk(tree) if isinstance(cls, python_ast.ClassDef)):
                                    functions.append({
                                        'name': node.name,
                                        'line': node.lineno,
                                        'args': len(node.args.args)
                                    })
                            elif isinstance(node, (python_ast.Import, python_ast.ImportFrom)):
                                if isinstance(node, python_ast.Import):
                                    for name in node.names:
                                        imports.append(name.name)
                                else:
                                    imports.append(node.module or 'relative')
                        
                        ast_data.append({
                            'file': py_file.replace(self.working_path, ''),
                            'language': 'python',
                            'classes': classes,
                            'functions': functions,
                            'imports': list(set(imports)),
                            'lines': len(content.split('\n'))
                        })
                    except SyntaxError as e:
                        logger.warning(f"Syntax error in {py_file}: {e}")
            except Exception as e:
                logger.warning(f"Error analyzing {py_file}: {e}")
        
        return ast_data
    
    def _parse_sql_tables(self, sql_content: str) -> List[Dict[str, Any]]:
        """Parse SQL content to extract table definitions."""
        tables = []
        
        # Simple regex to find CREATE TABLE statements
        import re
        table_pattern = re.compile(r'CREATE\s+TABLE\s+(\w+)\s*\((.*?)\)', re.IGNORECASE | re.DOTALL)
        matches = table_pattern.findall(sql_content)
        
        for table_name, columns_str in matches:
            columns = []
            column_lines = [line.strip() for line in columns_str.split(',') if line.strip()]
            
            for column_line in column_lines:
                parts = column_line.split()
                if len(parts) >= 2:
                    columns.append({
                        'name': parts[0].strip(),
                        'type': parts[1].strip(),
                        'nullable': 'NOT NULL' not in column_line.upper()
                    })
            
            if columns:
                tables.append({
                    'name': table_name,
                    'columns': columns
                })
        
        return tables
    
    def _parse_python_models(self, content: str) -> List[Dict[str, Any]]:
        """Parse Python content to extract model definitions."""
        models = []
        
        # Look for class definitions that might be models
        import re
        class_pattern = re.compile(r'class\s+(\w+)\s*\([^)]*\):', re.MULTILINE)
        matches = class_pattern.findall(content)
        
        for class_name in matches:
            # This is a simplified parser - in reality you'd want proper AST parsing
            if any(keyword in content for keyword in ['Column', 'Field', 'models.', 'db.']):
                models.append({
                    'name': class_name,
                    'type': 'model',
                    'fields': []  # Would need more sophisticated parsing for actual fields
                })
        
        return models


