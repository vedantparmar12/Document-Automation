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

