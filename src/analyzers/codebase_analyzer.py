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
    
    async def analyze(self) -> Dict[str, Any]:
        """
        Enhanced analysis method that adds MCP detection and semantic classification.
        """
        # First run the base analysis
        base_result = await super().analyze()
        
        # If base analysis failed, return immediately
        if not base_result.success:
            return base_result
        
        try:
            logger.info("Running enhanced analysis for MCP detection and classification...")
            
            # Import enhanced analyzer
            from .enhanced_analyzer import EnhancedAnalyzer
            
            # Collect Python file contents for analysis
            file_contents = {}
            for root, dirs, files in os.walk(self.working_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                rel_path = os.path.relpath(file_path, self.working_path)
                                file_contents[rel_path] = f.read()
                        except Exception as e:
                            logger.warning(f"Could not read {file_path}: {e}")
                            continue
            
            if file_contents:
                enhanced_analyzer = EnhancedAnalyzer()
                enhanced_results = enhanced_analyzer.analyze(
                    codebase_path=self.working_path,
                    file_contents=file_contents,
                    dependencies=base_result.data.get('dependencies', []),
                    project_structure=base_result.data.get('project_structure', {})
                )
                
                # Add enhanced analysis to results
                base_result.data['classification'] = enhanced_results.get('classification')
                base_result.data['mcp_server_info'] = enhanced_results.get('mcp_server_info')
                base_result.data['specialized_analysis'] = enhanced_results.get('specialized_analysis')
                
                classification = enhanced_results.get('classification', {})
                logger.info(f"Enhanced analysis complete: {classification.get('primary_type', 'unknown')}")
        except Exception as e:
            logger.warning(f"Enhanced analysis failed: {e}, continuing with base results")
            # Continue with regular results if enhanced analysis fails
        
        return base_result
    
    async def _analyze_dependencies(self) -> List[Dict[str, Any]]:
        """Analyze project dependencies with versions."""
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
                            if line and not line.startswith('#') and not line.startswith('-'):
                                # Parse: package==1.0.0 or package>=1.0.0 or package
                                match = re.match(r'^([a-zA-Z0-9_\-\[\]]+)([>=<~!]=?)(.+)?$', line)
                                if match:
                                    name = match.group(1).strip()
                                    operator = match.group(2) if match.group(2) else None
                                    version = match.group(3).strip() if match.group(3) else None
                                    
                                    # Skip if already added
                                    if not any(d['name'] == name for d in dependencies):
                                        dependencies.append({
                                            'name': name,
                                            'version': version if version else 'latest',
                                            'operator': operator if operator else '',
                                            'source': req_file,
                                            'type': 'python'
                                        })
                except Exception as e:
                    logger.warning(f"Error reading {req_file}: {e}")
        
        # Check setup.py for dependencies
        setup_py = os.path.join(self.working_path, 'setup.py')
        if os.path.exists(setup_py):
            try:
                with open(setup_py, 'r') as f:
                    content = f.read()
                    if 'install_requires' in content:
                        pattern = r'install_requires\s*=\s*\[(.*?)\]'
                        match = re.search(pattern, content, re.DOTALL)
                        if match:
                            requires = match.group(1)
                            for line in requires.split(','):
                                line = line.strip().strip('"').strip("'")
                                if line:
                                    match = re.match(r'^([a-zA-Z0-9_\-\[\]]+)([>=<~!]=?)(.+)?$', line)
                                    if match:
                                        name = match.group(1).strip()
                                        if not any(d['name'] == name for d in dependencies):
                                            operator = match.group(2) if match.group(2) else None
                                            version = match.group(3).strip() if match.group(3) else None
                                            dependencies.append({
                                                'name': name,
                                                'version': version if version else 'latest',
                                                'operator': operator if operator else '',
                                                'source': 'setup.py',
                                                'type': 'python'
                                            })
            except Exception as e:
                logger.warning(f"Error reading setup.py: {e}")
        
        # Node.js dependencies
        package_json = os.path.join(self.working_path, 'package.json')
        if os.path.exists(package_json):
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    for dep_type in ['dependencies', 'devDependencies']:
                        if dep_type in data:
                            for name, version in data[dep_type].items():
                                if not any(d['name'] == name for d in dependencies):
                                    dependencies.append({
                                        'name': name,
                                        'version': version.lstrip('^~'),
                                        'operator': version[0] if version and version[0] in ['^', '~'] else '',
                                        'source': 'package.json',
                                        'type': 'javascript',
                                        'dev': dep_type == 'devDependencies'
                                    })
            except Exception as e:
                logger.warning(f"Error reading package.json: {e}")
        
        logger.info(f"Found {len(dependencies)} dependencies")
        
        # Go dependencies (go.mod)
        go_mod = os.path.join(self.working_path, 'go.mod')
        if os.path.exists(go_mod):
            try:
                with open(go_mod, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('require'):
                            if ' ' in line:  # Single line require
                                parts = line.split()
                                if len(parts) >= 2:
                                    dependencies.append({
                                        'name': parts[1],
                                        'version': parts[2] if len(parts) > 2 else 'latest',
                                        'source': 'go.mod',
                                        'type': 'go'
                                    })
                        elif '(' not in line and ')' not in line and len(line.split()) >= 2: # Inside require block
                             parts = line.split()
                             # Simple heuristic to avoid directives
                             if '.' in parts[0]: 
                                dependencies.append({
                                    'name': parts[0],
                                    'version': parts[1] if len(parts) > 1 else 'latest',
                                    'source': 'go.mod',
                                    'type': 'go'
                                })
            except Exception as e:
                logger.warning(f"Error reading go.mod: {e}")

        # Rust dependencies (Cargo.toml)
        cargo_toml = os.path.join(self.working_path, 'Cargo.toml')
        if os.path.exists(cargo_toml):
            try:
                import tomllib # Python 3.11+
                with open(cargo_toml, 'rb') as f:
                    data = tomllib.load(f)
                    for dep_name, dep_info in data.get('dependencies', {}).items():
                        version = dep_info if isinstance(dep_info, str) else dep_info.get('version', 'unknown')
                        dependencies.append({
                            'name': dep_name,
                            'version': version,
                            'source': 'Cargo.toml',
                            'type': 'rust'
                        })
            except ImportError:
                 # Fallback for older python or missing library - simple parsing
                 try:
                    with open(cargo_toml, 'r', encoding='utf-8', errors='ignore') as f:
                        in_deps = False
                        for line in f:
                            line = line.strip()
                            if line == '[dependencies]':
                                in_deps = True
                                continue
                            if line.startswith('['):
                                in_deps = False
                            
                            if in_deps and '=' in line:
                                name = line.split('=')[0].strip()
                                version = line.split('=')[1].strip().strip('"').strip("'")
                                dependencies.append({
                                    'name': name,
                                    'version': version,
                                    'source': 'Cargo.toml',
                                    'type': 'rust'
                                })
                 except Exception as e:
                    logger.warning(f"Error reading Cargo.toml: {e}")
            except Exception as e:
                logger.warning(f"Error reading Cargo.toml: {e}")

        # Java dependencies (pom.xml - Maven)
        pom_xml = os.path.join(self.working_path, 'pom.xml')
        if os.path.exists(pom_xml):
            try:
                with open(pom_xml, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Simple regex for dependencies - XML parsing is heavy
                    matches = re.findall(r'<dependency>[\s\S]*?<groupId>(.*?)</groupId>[\s\S]*?<artifactId>(.*?)</artifactId>[\s\S]*?(?:<version>(.*?)</version>)?', content)
                    for group_id, artifact_id, version in matches:
                         dependencies.append({
                            'name': f"{group_id}:{artifact_id}",
                            'version': version if version else 'latest',
                            'source': 'pom.xml',
                            'type': 'java'
                         })
            except Exception as e:
                logger.warning(f"Error reading pom.xml: {e}")

        # Java dependencies (build.gradle - Gradle)
        build_gradle = os.path.join(self.working_path, 'build.gradle')
        if os.path.exists(build_gradle):
            try:
                with open(build_gradle, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('implementation') or line.startswith('api') or line.startswith('compile'):
                             # implementation 'group:name:version'
                             match = re.search(r"['\"](.+?):(.+?):(.+?)['\"]", line)
                             if match:
                                dependencies.append({
                                    'name': f"{match.group(1)}:{match.group(2)}",
                                    'version': match.group(3),
                                    'source': 'build.gradle',
                                    'type': 'java'
                                })
            except Exception as e:
                logger.warning(f"Error reading build.gradle: {e}")

        return dependencies

    async def _extract_api_endpoints(self) -> List[Dict[str, Any]]:
        """Extract API endpoints from Flask, FastAPI, Django, Express."""
        logger.info(f"Extracting API endpoints for {self.path}")
        endpoints = []
        
        try:
            # Extract from Python files (Flask, FastAPI, Django)
            for root, dirs, files in os.walk(self.working_path):
                # Skip common non-code directories
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', 'venv', '.env']]
                
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                
                                # Flask: @app.route() or @bp.route()
                                flask_pattern = r'@(?:app|bp|blueprint)\.route\([\'"]([^\'"]+)[\'"](?:,\s*methods=\[([^\]]+)\])?\)'
                                for match in re.finditer(flask_pattern, content):
                                    path, methods = match.groups()
                                    endpoints.append({
                                        'path': path,
                                        'methods': methods.replace("'", "").replace('"', '').replace(' ', '') if methods else 'GET',
                                        'framework': 'Flask',
                                        'file': os.path.relpath(file_path, self.working_path)
                                    })
                                
                                # FastAPI: @app.get(), @app.post(), @router.get(), etc.
                                fastapi_pattern = r'@(?:app|router)\.(?P<method>get|post|put|delete|patch|options|head)\([\'"](?P<path>[^\'"]+)[\'"]'
                                for match in re.finditer(fastapi_pattern, content):
                                    method = match.group('method').upper()
                                    path = match.group('path')
                                    endpoints.append({
                                        'path': path,
                                        'methods': method,
                                        'framework': 'FastAPI',
                                        'file': os.path.relpath(file_path, self.working_path)
                                    })
                                
                                # Django: path() and re_path() in urls.py
                                if 'urls.py' in file:
                                    django_pattern = r'(?:path|re_path)\([\'"]([^\'"]+)[\'"]'
                                    for match in re.finditer(django_pattern, content):
                                        path = match.group(1)
                                        endpoints.append({
                                            'path': f'/{path}',
                                            'methods': 'GET,POST',
                                            'framework': 'Django',
                                            'file': os.path.relpath(file_path, self.working_path)
                                        })
                        except Exception as e:
                            logger.debug(f"Error reading {file_path}: {e}")
                    
                    # Extract from JavaScript/TypeScript files (Express)
                    elif file.endswith(('.js', '.ts')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                
                                # Express: app.get(), router.post(), etc.
                                express_pattern = r'(?:app|router)\.(?P<method>get|post|put|delete|patch|all|use)\([\'"`](?P<path>[^\'"` ]+)[\'"`]'
                                for match in re.finditer(express_pattern, content):
                                    method = match.group('method').upper()
                                    path = match.group('path')
                                    if not path.startswith('('):  # Skip middleware patterns
                                        endpoints.append({
                                            'path': path,
                                            'methods': method if method != 'USE' else 'ALL',
                                            'framework': 'Express',
                                            'file': os.path.relpath(file_path, self.working_path)
                                        })
                        except Exception as e:
                            logger.debug(f"Error reading {file_path}: {e}")

                    # Extract from Go files (Gin, Echo, Standard Lib)
                    elif file.endswith('.go'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                # Gin/Echo: r.GET("/path", handler) or e.GET("/path", handler)
                                go_pattern = r'\.(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD)\(["\']([^"\']+)["\']'
                                for match in re.finditer(go_pattern, content):
                                    method, path = match.groups()
                                    endpoints.append({
                                        'path': path,
                                        'methods': method,
                                        'framework': 'Go (Gin/Echo)',
                                        'file': os.path.relpath(file_path, self.working_path)
                                    })
                        except Exception as e:
                             logger.debug(f"Error reading {file_path}: {e}")

                    # Extract from Java files (Spring Boot)
                    elif file.endswith('.java'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                # Spring Boot: @GetMapping("/path"), @PostMapping(value = "/path")
                                spring_pattern = r'@(Get|Post|Put|Delete|Patch|Request)Mapping\(\s*(?:value\s*=\s*)?["\']([^"\']+)["\']'
                                for match in re.finditer(spring_pattern, content):
                                    method_type, path = match.groups()
                                    method = method_type.upper() if method_type != 'Request' else 'ANY'
                                    endpoints.append({
                                        'path': path,
                                        'methods': method,
                                        'framework': 'Spring Boot',
                                        'file': os.path.relpath(file_path, self.working_path)
                                    })
                        except Exception as e:
                             logger.debug(f"Error reading {file_path}: {e}")
            
            # Remove duplicates based on path and method
            seen = set()
            unique_endpoints = []
            for ep in endpoints:
                key = (ep['path'], ep['methods'])
                if key not in seen:
                    seen.add(key)
                    unique_endpoints.append(ep)
            
            logger.info(f"Found {len(unique_endpoints)} API endpoints")
            return unique_endpoints
            
        except Exception as e:
            logger.error(f"Error extracting API endpoints: {e}")
            return []

    async def _analyze_architecture(self) -> Dict[str, Any]:
        """Analyze project architecture and detect patterns."""
        logger.info(f"Analyzing architecture for {self.path}")
        
        architecture = {
            'layers': [],
            'components': [],
            'patterns': [],
            'entry_points': [],
            'directory_structure': {}
        }
        
        try:
            # Analyze directory structure to detect architectural layers
            for root, dirs, files in os.walk(self.working_path):
                # Skip common non-code directories
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', 'venv', '.env', 'dist', 'build']]
                
                rel_path = os.path.relpath(root, self.working_path)
                dir_name = os.path.basename(root)
                
                # Detect architectural layers
                layer_mappings = {
                    'controllers': 'Presentation Layer',
                    'views': 'Presentation Layer', 
                    'routes': 'API Layer',
                    'api': 'API Layer',
                    'models': 'Data Access Layer',
                    'database': 'Data Access Layer',
                    'db': 'Data Access Layer',
                    'services': 'Business Logic Layer',
                    'core': 'Business Logic Layer',
                    'business': 'Business Logic Layer',
                    'utils': 'Utility Layer',
                    'helpers': 'Utility Layer',
                    'middleware': 'Middleware Layer',
                    'config': 'Configuration Layer',
                    'tests': 'Testing Layer',
                    'migrations': 'Database Migration Layer'
                }
                
                for keyword, layer in layer_mappings.items():
                    if keyword in dir_name.lower():
                        if layer not in architecture['layers']:
                            architecture['layers'].append(layer)
                        
                        architecture['components'].append({
                            'name': dir_name,
                            'layer': layer,
                            'path': rel_path,
                            'files': len(files)
                        })
                        break
                
                # Store directory structure
                if rel_path != '.' and len(files) > 0:
                    architecture['directory_structure'][rel_path] = {
                        'files': len(files),
                        'subdirs': len(dirs)
                    }
            
            # Detect entry points
            entry_files = [
                'main.py', 'app.py', 'server.py', 'run.py', '__main__.py',
                'index.js', 'server.js', 'app.js', 'main.js',
                'index.ts', 'server.ts', 'app.ts', 'main.ts'
            ]
            
            for entry in entry_files:
                entry_path = os.path.join(self.working_path, entry)
                if os.path.exists(entry_path):
                    architecture['entry_points'].append(entry)
            
            # Detect architectural patterns
            if 'models' in str(architecture['components']) and 'views' in str(architecture['components']) and 'controllers' in str(architecture['components']):
                architecture['patterns'].append('MVC (Model-View-Controller)')
            
            if 'services' in str(architecture['components']) and 'models' in str(architecture['components']):
                architecture['patterns'].append('Service Layer Pattern')
            
            if 'api' in str(architecture['components']) or 'routes' in str(architecture['components']):
                architecture['patterns'].append('RESTful API Architecture')
            
            if 'middleware' in str(architecture['components']):
                architecture['patterns'].append('Middleware Pattern')
            
            # Detect microservices indicators
            docker_compose = os.path.join(self.working_path, 'docker-compose.yml')
            if os.path.exists(docker_compose):
                architecture['patterns'].append('Microservices Architecture')
            
            logger.info(f"Detected {len(architecture['layers'])} architectural layers and {len(architecture['patterns'])} patterns")
            return architecture
            
        except Exception as e:
            logger.error(f"Error analyzing architecture: {e}")
            return architecture

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
        """Detect frameworks and technology stack with confidence scores."""
        logger.info(f"Detecting frameworks for {self.path}")
        
        frameworks = []
        framework_indicators = {}
        
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

        # Check for Go frameworks
        go_mod = os.path.join(self.working_path, 'go.mod')
        if os.path.exists(go_mod):
            try:
                with open(go_mod, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if 'github.com/gin-gonic/gin' in content:
                        frameworks.append({'name': 'Gin', 'category': 'start_framework', 'confidence': 0.95})
                    if 'github.com/labstack/echo' in content:
                        frameworks.append({'name': 'Echo', 'category': 'web_framework', 'confidence': 0.95})
                    if 'github.com/gofiber/fiber' in content:
                        frameworks.append({'name': 'Fiber', 'category': 'web_framework', 'confidence': 0.95})
            except: pass

        # Check for Java frameworks (Maven/Gradle)
        if os.path.exists(os.path.join(self.working_path, 'pom.xml')) or os.path.exists(os.path.join(self.working_path, 'build.gradle')):
            # Read both if they exist
            content = ""
            try:
                if os.path.exists(os.path.join(self.working_path, 'pom.xml')):
                     with open(os.path.join(self.working_path, 'pom.xml'), 'r', encoding='utf-8', errors='ignore') as f: content += f.read()
                if os.path.exists(os.path.join(self.working_path, 'build.gradle')):
                     with open(os.path.join(self.working_path, 'build.gradle'), 'r', encoding='utf-8', errors='ignore') as f: content += f.read()
                
                if 'spring-boot' in content:
                     frameworks.append({'name': 'Spring Boot', 'category': 'fullstack_framework', 'confidence': 0.99})
                if 'quarkus' in content:
                     frameworks.append({'name': 'Quarkus', 'category': 'fullstack_framework', 'confidence': 0.9})
            except: pass

        # Check for Rust frameworks
        cargo_toml = os.path.join(self.working_path, 'Cargo.toml')
        if os.path.exists(cargo_toml):
            try:
                 with open(cargo_toml, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if 'actix-web' in content:
                        frameworks.append({'name': 'Actix Web', 'category': 'web_framework', 'confidence': 0.95})
                    if 'axum' in content:
                        frameworks.append({'name': 'Axum', 'category': 'web_framework', 'confidence': 0.95})
                    if 'rocket' in content:
                        frameworks.append({'name': 'Rocket', 'category': 'web_framework', 'confidence': 0.90})
                    if 'tokio' in content:
                        frameworks.append({'name': 'Tokio', 'category': 'async_runtime', 'confidence': 0.90})
            except: pass
        
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
        """Parse code using AST for detailed analysis with complexity metrics."""
        logger.info(f"Parsing AST for {self.path}")
        
        ast_data = []
        
        try:
            import ast as python_ast
            
            # Find all Python files
            for root, dirs, files in os.walk(self.working_path):
                # Skip common non-code directories
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', 'venv', '.env']]
                
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                source_code = f.read()
                                tree = python_ast.parse(source_code)
                                
                                file_analysis = {
                                    'file': os.path.relpath(file_path, self.working_path),
                                    'functions': [],
                                    'classes': [],
                                    'imports': [],
                                    'total_complexity': 0,
                                    'lines_of_code': len(source_code.splitlines()),
                                    'maintainability_index': 0
                                }
                                
                                # Extract imports
                                for node in python_ast.walk(tree):
                                    if isinstance(node, python_ast.Import):
                                        for alias in node.names:
                                            file_analysis['imports'].append(alias.name)
                                    elif isinstance(node, python_ast.ImportFrom):
                                        if node.module:
                                            file_analysis['imports'].append(node.module)
                                
                                # Analyze functions
                                for node in python_ast.walk(tree):
                                    if isinstance(node, python_ast.FunctionDef):
                                        complexity = self._calculate_cyclomatic_complexity(node)
                                        
                                        # Count parameters
                                        num_params = len(node.args.args)
                                        
                                        # Calculate lines
                                        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                                            lines = node.end_lineno - node.lineno
                                        else:
                                            lines = 0
                                        
                                        # Determine complexity rating
                                        if complexity <= 5:
                                            rating = 'Simple'
                                        elif complexity <= 10:
                                            rating = 'Moderate'
                                        elif complexity <= 20:
                                            rating = 'Complex'
                                        else:
                                            rating = 'Very Complex'
                                        
                                        function_info = {
                                            'name': node.name,
                                            'complexity': complexity,
                                            'complexity_rating': rating,
                                            'parameters': num_params,
                                            'lines': lines,
                                            'is_async': isinstance(node, python_ast.AsyncFunctionDef)
                                        }
                                        
                                        file_analysis['functions'].append(function_info)
                                        file_analysis['total_complexity'] += complexity
                                    
                                    elif isinstance(node, python_ast.ClassDef):
                                        # Analyze class
                                        methods = [n for n in node.body if isinstance(n, (python_ast.FunctionDef, python_ast.AsyncFunctionDef))]
                                        
                                        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                                            lines = node.end_lineno - node.lineno
                                        else:
                                            lines = 0
                                        
                                        class_info = {
                                            'name': node.name,
                                            'methods': len(methods),
                                            'lines': lines,
                                            'has_init': any(m.name == '__init__' for m in methods)
                                        }
                                        
                                        file_analysis['classes'].append(class_info)
                                
                                # Calculate maintainability index (simplified version)
                                # MI = 171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(LOC)
                                # Simplified: Higher is better, max 100
                                if file_analysis['lines_of_code'] > 0:
                                    import math
                                    loc = file_analysis['lines_of_code']
                                    complexity = file_analysis['total_complexity'] if file_analysis['total_complexity'] > 0 else 1
                                    
                                    mi = max(0, min(100, 
                                        171 - 5.2 * math.log(loc) - 0.23 * complexity - 16.2 * math.log(loc)
                                    ))
                                    file_analysis['maintainability_index'] = round(mi, 2)
                                
                                ast_data.append(file_analysis)
                                
                        except SyntaxError as e:
                            logger.debug(f"Syntax error in {file_path}: {e}")
                        except Exception as e:
                            logger.debug(f"Error parsing {file_path}: {e}")
            
            logger.info(f"Parsed {len(ast_data)} Python files with AST")
            return ast_data
            
        except Exception as e:
            logger.error(f"Error in AST parsing: {e}")
            return []
    
    def _calculate_cyclomatic_complexity(self, node) -> int:
        """Calculate cyclomatic complexity of a function using AST."""
        import ast as python_ast
        
        complexity = 1  # Base complexity
        
        for child in python_ast.walk(node):
            # Decision points that increase complexity
            if isinstance(child, (python_ast.If, python_ast.While, python_ast.For, 
                                 python_ast.ExceptHandler, python_ast.With)):
                complexity += 1
            elif isinstance(child, python_ast.BoolOp):
                # Each additional boolean operator (and/or)
                complexity += len(child.values) - 1
            elif isinstance(child, (python_ast.Break, python_ast.Continue)):
                complexity += 1
        
        return complexity
        
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


