"""
Enhanced framework detection for various programming languages and frameworks.

This module provides comprehensive detection of frameworks, libraries,
and technology stacks across different programming languages.
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class FrameworkInfo:
    """Information about a detected framework."""
    name: str
    category: str  # web, testing, orm, ui, etc.
    confidence: float  # 0.0 to 1.0
    version: Optional[str] = None
    evidence: List[str] = field(default_factory=list)
    files: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TechnologyStack:
    """Complete technology stack information."""
    language: str
    frameworks: List[FrameworkInfo]
    architecture_patterns: List[str] = field(default_factory=list)
    deployment_targets: List[str] = field(default_factory=list)
    database_systems: List[str] = field(default_factory=list)
    testing_frameworks: List[str] = field(default_factory=list)
    build_tools: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'language': self.language,
            'frameworks': [
                {
                    'name': f.name,
                    'category': f.category,
                    'confidence': f.confidence,
                    'version': f.version,
                    'evidence': f.evidence,
                    'files': f.files,
                    'metadata': f.metadata
                }
                for f in self.frameworks
            ],
            'architecture_patterns': self.architecture_patterns,
            'deployment_targets': self.deployment_targets,
            'database_systems': self.database_systems,
            'testing_frameworks': self.testing_frameworks,
            'build_tools': self.build_tools
        }


class FrameworkDetector:
    """
    Enhanced framework detector supporting multiple languages and ecosystems.
    
    Detects frameworks based on:
    - Package dependencies
    - Import statements
    - Configuration files
    - File structures and naming patterns
    - Code patterns and signatures
    """
    
    def __init__(self):
        self.detection_rules = self._load_detection_rules()
        self.pattern_cache: Dict[str, re.Pattern] = {}
    
    def _load_detection_rules(self) -> Dict[str, Any]:
        """Load framework detection rules."""
        return {
            'python': {
                'web_frameworks': {
                    'django': {
                        'imports': ['django', 'django.conf', 'django.db'],
                        'files': ['manage.py', 'settings.py', 'urls.py'],
                        'patterns': [r'from django', r'import django'],
                        'config_files': ['requirements.txt', 'Pipfile'],
                        'confidence_base': 0.9
                    },
                    'flask': {
                        'imports': ['flask', 'Flask'],
                        'patterns': [r'from flask import', r'app = Flask\('],
                        'config_files': ['requirements.txt'],
                        'confidence_base': 0.85
                    },
                    'fastapi': {
                        'imports': ['fastapi', 'FastAPI'],
                        'patterns': [r'from fastapi import', r'app = FastAPI\('],
                        'config_files': ['requirements.txt'],
                        'confidence_base': 0.85
                    },
                    'pyramid': {
                        'imports': ['pyramid'],
                        'patterns': [r'from pyramid'],
                        'confidence_base': 0.8
                    },
                    'tornado': {
                        'imports': ['tornado'],
                        'patterns': [r'import tornado', r'from tornado'],
                        'confidence_base': 0.8
                    }
                },
                'testing_frameworks': {
                    'pytest': {
                        'imports': ['pytest'],
                        'files': ['pytest.ini', 'conftest.py'],
                        'patterns': [r'def test_', r'import pytest'],
                        'confidence_base': 0.9
                    },
                    'unittest': {
                        'imports': ['unittest'],
                        'patterns': [r'import unittest', r'class.*TestCase'],
                        'confidence_base': 0.8
                    },
                    'nose': {
                        'imports': ['nose'],
                        'patterns': [r'import nose'],
                        'confidence_base': 0.7
                    }
                },
                'data_science': {
                    'pandas': {
                        'imports': ['pandas'],
                        'patterns': [r'import pandas', r'pd\.'],
                        'confidence_base': 0.9
                    },
                    'numpy': {
                        'imports': ['numpy'],
                        'patterns': [r'import numpy', r'np\.'],
                        'confidence_base': 0.9
                    },
                    'scikit-learn': {
                        'imports': ['sklearn'],
                        'patterns': [r'from sklearn'],
                        'confidence_base': 0.9
                    },
                    'tensorflow': {
                        'imports': ['tensorflow'],
                        'patterns': [r'import tensorflow', r'tf\.'],
                        'confidence_base': 0.9
                    },
                    'pytorch': {
                        'imports': ['torch'],
                        'patterns': [r'import torch', r'torch\.'],
                        'confidence_base': 0.9
                    }
                },
                'orm': {
                    'sqlalchemy': {
                        'imports': ['sqlalchemy'],
                        'patterns': [r'from sqlalchemy'],
                        'confidence_base': 0.85
                    },
                    'peewee': {
                        'imports': ['peewee'],
                        'patterns': [r'from peewee'],
                        'confidence_base': 0.8
                    }
                }
            },
            'javascript': {
                'frontend_frameworks': {
                    'react': {
                        'dependencies': ['react', 'react-dom'],
                        'imports': ['React'],
                        'files': ['.jsx', '.tsx'],
                        'patterns': [r'import React', r'from [\'"]react[\'"]', r'<\w+.*>'],
                        'confidence_base': 0.9
                    },
                    'vue': {
                        'dependencies': ['vue'],
                        'imports': ['Vue'],
                        'files': ['.vue'],
                        'patterns': [r'import Vue', r'new Vue\(', r'<template>'],
                        'confidence_base': 0.9
                    },
                    'angular': {
                        'dependencies': ['@angular/core'],
                        'imports': ['@angular'],
                        'patterns': [r'import.*@angular', r'@Component', r'@Injectable'],
                        'files': ['angular.json'],
                        'confidence_base': 0.9
                    },
                    'svelte': {
                        'dependencies': ['svelte'],
                        'files': ['.svelte'],
                        'patterns': [r'<script.*svelte'],
                        'confidence_base': 0.85
                    }
                },
                'backend_frameworks': {
                    'express': {
                        'dependencies': ['express'],
                        'patterns': [r'require\([\'"]express[\'"]\)', r'app\.get\(', r'app\.post\('],
                        'confidence_base': 0.9
                    },
                    'koa': {
                        'dependencies': ['koa'],
                        'patterns': [r'require\([\'"]koa[\'"]\)', r'const Koa'],
                        'confidence_base': 0.85
                    },
                    'fastify': {
                        'dependencies': ['fastify'],
                        'patterns': [r'require\([\'"]fastify[\'"]\)'],
                        'confidence_base': 0.8
                    },
                    'nestjs': {
                        'dependencies': ['@nestjs/core'],
                        'patterns': [r'import.*@nestjs', r'@Controller', r'@Module'],
                        'confidence_base': 0.9
                    }
                },
                'testing_frameworks': {
                    'jest': {
                        'dependencies': ['jest'],
                        'files': ['jest.config.js'],
                        'patterns': [r'describe\(', r'it\(', r'test\('],
                        'confidence_base': 0.9
                    },
                    'mocha': {
                        'dependencies': ['mocha'],
                        'patterns': [r'describe\(', r'it\('],
                        'confidence_base': 0.8
                    },
                    'cypress': {
                        'dependencies': ['cypress'],
                        'patterns': [r'cy\.', r'cypress'],
                        'confidence_base': 0.9
                    }
                },
                'build_tools': {
                    'webpack': {
                        'dependencies': ['webpack'],
                        'files': ['webpack.config.js'],
                        'confidence_base': 0.9
                    },
                    'vite': {
                        'dependencies': ['vite'],
                        'files': ['vite.config.js'],
                        'confidence_base': 0.9
                    },
                    'rollup': {
                        'dependencies': ['rollup'],
                        'files': ['rollup.config.js'],
                        'confidence_base': 0.8
                    }
                }
            },
            'java': {
                'frameworks': {
                    'spring': {
                        'imports': ['org.springframework'],
                        'annotations': ['@SpringBootApplication', '@Controller', '@Service'],
                        'files': ['pom.xml', 'application.properties'],
                        'confidence_base': 0.9
                    },
                    'hibernate': {
                        'imports': ['org.hibernate'],
                        'annotations': ['@Entity', '@Table'],
                        'confidence_base': 0.85
                    }
                }
            }
        }
    
    def detect_frameworks(
        self,
        project_path: str,
        file_contents: Dict[str, str],
        language: str
    ) -> TechnologyStack:
        """
        Detect frameworks and technology stack for a project.
        
        Args:
            project_path: Path to project root
            file_contents: Dictionary of file_path -> content
            language: Primary programming language
            
        Returns:
            TechnologyStack with detected frameworks and tools
        """
        detected_frameworks = []
        
        # Get language-specific rules
        lang_rules = self.detection_rules.get(language.lower(), {})
        
        # Analyze package dependencies
        dependencies = self._extract_dependencies(project_path, file_contents, language)
        
        # Analyze imports and code patterns
        imports = self._extract_imports(file_contents, language)
        
        # Analyze file structure
        file_structure = self._analyze_file_structure(file_contents)
        
        # Detect frameworks for each category
        for category, frameworks in lang_rules.items():
            for framework_name, rules in frameworks.items():
                framework_info = self._detect_single_framework(
                    framework_name,
                    category,
                    rules,
                    dependencies,
                    imports,
                    file_structure,
                    file_contents
                )
                
                if framework_info and framework_info.confidence > 0.3:
                    detected_frameworks.append(framework_info)
        
        # Additional analysis
        architecture_patterns = self._detect_architecture_patterns(file_contents, language)
        deployment_targets = self._detect_deployment_targets(file_contents, dependencies)
        database_systems = self._detect_database_systems(dependencies, imports)
        testing_frameworks = [f.name for f in detected_frameworks if f.category == 'testing_frameworks']
        build_tools = [f.name for f in detected_frameworks if f.category == 'build_tools']
        
        return TechnologyStack(
            language=language,
            frameworks=detected_frameworks,
            architecture_patterns=architecture_patterns,
            deployment_targets=deployment_targets,
            database_systems=database_systems,
            testing_frameworks=testing_frameworks,
            build_tools=build_tools
        )
    
    def _detect_single_framework(
        self,
        framework_name: str,
        category: str,
        rules: Dict[str, Any],
        dependencies: Set[str],
        imports: Set[str],
        file_structure: Dict[str, Any],
        file_contents: Dict[str, str]
    ) -> Optional[FrameworkInfo]:
        """Detect a single framework based on rules."""
        evidence = []
        confidence = 0.0
        files_found = []
        
        # Check dependencies
        framework_deps = set(rules.get('dependencies', []))
        if framework_deps.intersection(dependencies):
            evidence.append("Found in dependencies")
            confidence += 0.4
            
        # Check imports
        framework_imports = set(rules.get('imports', []))
        if framework_imports.intersection(imports):
            evidence.append("Found in imports")
            confidence += 0.3
        
        # Check specific files
        required_files = rules.get('files', [])
        for req_file in required_files:
            if any(req_file in file_path for file_path in file_structure['files']):
                evidence.append(f"Found {req_file}")
                confidence += 0.2
                files_found.append(req_file)
        
        # Check code patterns
        patterns = rules.get('patterns', [])
        for pattern in patterns:
            compiled_pattern = self._get_compiled_pattern(pattern)
            for file_path, content in file_contents.items():
                if compiled_pattern.search(content):
                    evidence.append(f"Pattern '{pattern}' found in {Path(file_path).name}")
                    confidence += 0.1
                    break
        
        # Check annotations (for Java, etc.)
        annotations = rules.get('annotations', [])
        for annotation in annotations:
            pattern = re.compile(rf'{re.escape(annotation)}', re.MULTILINE)
            for file_path, content in file_contents.items():
                if pattern.search(content):
                    evidence.append(f"Annotation {annotation} found")
                    confidence += 0.2
                    break
        
        # Apply base confidence
        base_confidence = rules.get('confidence_base', 0.5)
        confidence = min(1.0, confidence * base_confidence)
        
        if confidence > 0:
            # Try to extract version information
            version = self._extract_framework_version(
                framework_name, dependencies, file_contents
            )
            
            return FrameworkInfo(
                name=framework_name,
                category=category,
                confidence=confidence,
                version=version,
                evidence=evidence,
                files=files_found,
                metadata={
                    'detection_method': 'rules_based',
                    'matched_rules': len(evidence)
                }
            )
        
        return None
    
    def _extract_dependencies(
        self, 
        project_path: str, 
        file_contents: Dict[str, str], 
        language: str
    ) -> Set[str]:
        """Extract project dependencies from configuration files."""
        dependencies = set()
        
        if language.lower() == 'python':
            # requirements.txt
            for file_path, content in file_contents.items():
                if 'requirements' in Path(file_path).name.lower():
                    for line in content.split('\n'):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Extract package name
                            pkg = re.split(r'[>=<!\[;]', line)[0].strip()
                            if pkg:
                                dependencies.add(pkg)
            
            # setup.py, pyproject.toml
            for file_path, content in file_contents.items():
                if Path(file_path).name in ['setup.py', 'pyproject.toml']:
                    # Extract dependencies from setup.py or pyproject.toml
                    deps = self._extract_python_setup_deps(content)
                    dependencies.update(deps)
        
        elif language.lower() in ['javascript', 'typescript']:
            # package.json
            for file_path, content in file_contents.items():
                if Path(file_path).name == 'package.json':
                    try:
                        package_data = json.loads(content)
                        deps = package_data.get('dependencies', {})
                        dev_deps = package_data.get('devDependencies', {})
                        dependencies.update(deps.keys())
                        dependencies.update(dev_deps.keys())
                    except json.JSONDecodeError:
                        pass
        
        elif language.lower() == 'java':
            # pom.xml, build.gradle
            for file_path, content in file_contents.items():
                file_name = Path(file_path).name
                if file_name == 'pom.xml':
                    deps = self._extract_maven_deps(content)
                    dependencies.update(deps)
                elif file_name in ['build.gradle', 'build.gradle.kts']:
                    deps = self._extract_gradle_deps(content)
                    dependencies.update(deps)
        
        return dependencies
    
    def _extract_imports(self, file_contents: Dict[str, str], language: str) -> Set[str]:
        """Extract import statements from source files."""
        imports = set()
        
        for file_path, content in file_contents.items():
            file_ext = Path(file_path).suffix.lower()
            
            if language.lower() == 'python' and file_ext == '.py':
                # Python imports
                import_patterns = [
                    r'^\s*import\s+([^\s#]+)',
                    r'^\s*from\s+([^\s#]+)\s+import'
                ]
                for pattern in import_patterns:
                    matches = re.findall(pattern, content, re.MULTILINE)
                    for match in matches:
                        # Get top-level module
                        top_module = match.split('.')[0]
                        imports.add(top_module)
            
            elif language.lower() in ['javascript', 'typescript'] and file_ext in ['.js', '.ts', '.jsx', '.tsx']:
                # JavaScript/TypeScript imports
                import_patterns = [
                    r'import.*from\s+[\'"]([^\'"]+)[\'"]',
                    r'require\([\'"]([^\'"]+)[\'"]\)'
                ]
                for pattern in import_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        # Get package name (handle scoped packages)
                        if match.startswith('@'):
                            pkg = '/'.join(match.split('/')[:2])
                        else:
                            pkg = match.split('/')[0]
                        imports.add(pkg)
            
            elif language.lower() == 'java' and file_ext == '.java':
                # Java imports
                pattern = r'^\s*import\s+([^;]+);'
                matches = re.findall(pattern, content, re.MULTILINE)
                for match in matches:
                    # Get package root
                    parts = match.split('.')
                    if len(parts) >= 2:
                        imports.add(f"{parts[0]}.{parts[1]}")
        
        return imports
    
    def _analyze_file_structure(self, file_contents: Dict[str, str]) -> Dict[str, Any]:
        """Analyze project file structure."""
        files = list(file_contents.keys())
        
        structure = {
            'files': files,
            'directories': set(),
            'extensions': defaultdict(int),
            'config_files': [],
            'special_files': []
        }
        
        for file_path in files:
            path = Path(file_path)
            
            # Count directories
            for parent in path.parents:
                if str(parent) != '.':
                    structure['directories'].add(str(parent))
            
            # Count extensions
            if path.suffix:
                structure['extensions'][path.suffix.lower()] += 1
            
            # Identify special files
            file_name = path.name.lower()
            config_patterns = [
                'config', 'settings', 'env', 'properties',
                '.json', '.yml', '.yaml', '.toml', '.ini'
            ]
            
            if any(pattern in file_name for pattern in config_patterns):
                structure['config_files'].append(file_path)
            
            special_files = [
                'dockerfile', 'makefile', 'readme', 'license',
                'gitignore', 'requirements.txt', 'package.json'
            ]
            
            if any(special in file_name for special in special_files):
                structure['special_files'].append(file_path)
        
        return structure
    
    def _detect_architecture_patterns(
        self, 
        file_contents: Dict[str, str], 
        language: str
    ) -> List[str]:
        """Detect architectural patterns from code structure."""
        patterns = []
        
        # Analyze directory structure
        directories = set()
        for file_path in file_contents.keys():
            path = Path(file_path)
            for parent in path.parents:
                if str(parent) != '.':
                    directories.add(str(parent).lower())
        
        # Common patterns
        if any(d in directories for d in ['models', 'views', 'controllers']):
            patterns.append('MVC')
        
        if any(d in directories for d in ['components', 'containers']):
            patterns.append('Component-based')
        
        if any(d in directories for d in ['services', 'repositories']):
            patterns.append('Service Layer')
        
        if any(d in directories for d in ['domain', 'application', 'infrastructure']):
            patterns.append('Clean Architecture')
        
        if 'microservices' in str(directories) or len([d for d in directories if 'service' in d]) > 2:
            patterns.append('Microservices')
        
        return patterns
    
    def _detect_deployment_targets(
        self, 
        file_contents: Dict[str, str], 
        dependencies: Set[str]
    ) -> List[str]:
        """Detect deployment targets and platforms."""
        targets = []
        
        # Check for deployment files
        for file_path in file_contents.keys():
            file_name = Path(file_path).name.lower()
            
            if file_name == 'dockerfile':
                targets.append('Docker')
            elif file_name in ['docker-compose.yml', 'docker-compose.yaml']:
                targets.append('Docker Compose')
            elif file_name in ['serverless.yml', 'serverless.yaml']:
                targets.append('Serverless')
            elif file_name == 'vercel.json':
                targets.append('Vercel')
            elif file_name in ['netlify.toml', '_redirects']:
                targets.append('Netlify')
            elif '.github' in file_path and 'workflows' in file_path:
                targets.append('GitHub Actions')
            elif file_name in ['azure-pipelines.yml', 'azure-pipelines.yaml']:
                targets.append('Azure DevOps')
            elif file_name == 'cloudbuild.yaml':
                targets.append('Google Cloud Build')
        
        # Check dependencies for platform-specific packages
        cloud_deps = {
            'boto3': 'AWS',
            'google-cloud': 'Google Cloud',
            'azure': 'Azure',
            'kubernetes': 'Kubernetes',
            'heroku': 'Heroku'
        }
        
        for dep, platform in cloud_deps.items():
            if any(dep in d for d in dependencies):
                targets.append(platform)
        
        return targets
    
    def _detect_database_systems(
        self, 
        dependencies: Set[str], 
        imports: Set[str]
    ) -> List[str]:
        """Detect database systems in use."""
        databases = []
        
        db_patterns = {
            'postgresql': ['psycopg2', 'pg', 'postgres'],
            'mysql': ['mysql', 'pymysql', 'mysqlclient'],
            'sqlite': ['sqlite3', 'sqlite'],
            'mongodb': ['pymongo', 'mongoose', 'mongodb'],
            'redis': ['redis', 'ioredis'],
            'elasticsearch': ['elasticsearch'],
            'cassandra': ['cassandra'],
            'neo4j': ['neo4j']
        }
        
        all_deps = dependencies.union(imports)
        
        for db_name, patterns in db_patterns.items():
            if any(pattern in dep.lower() for dep in all_deps for pattern in patterns):
                databases.append(db_name)
        
        return databases
    
    def _get_compiled_pattern(self, pattern: str) -> re.Pattern:
        """Get compiled regex pattern with caching."""
        if pattern not in self.pattern_cache:
            self.pattern_cache[pattern] = re.compile(pattern, re.MULTILINE | re.IGNORECASE)
        return self.pattern_cache[pattern]
    
    def _extract_framework_version(
        self, 
        framework_name: str, 
        dependencies: Set[str], 
        file_contents: Dict[str, str]
    ) -> Optional[str]:
        """Try to extract framework version."""
        # This is a simplified version extraction
        # In practice, you'd need to parse package files more carefully
        
        for file_path, content in file_contents.items():
            file_name = Path(file_path).name
            
            if file_name == 'package.json':
                try:
                    data = json.loads(content)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    if framework_name in deps:
                        return deps[framework_name].strip('^~>=<')
                except:
                    pass
        
        return None
    
    def _extract_python_setup_deps(self, content: str) -> Set[str]:
        """Extract dependencies from setup.py or pyproject.toml."""
        deps = set()
        
        # This is a simplified extraction
        # Real implementation would need proper parsing
        
        # Look for install_requires in setup.py
        install_requires_match = re.search(r'install_requires\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if install_requires_match:
            deps_str = install_requires_match.group(1)
            for line in deps_str.split(','):
                line = line.strip().strip('"\'')
                if line:
                    pkg = re.split(r'[>=<!\[]', line)[0].strip()
                    if pkg:
                        deps.add(pkg)
        
        return deps
    
    def _extract_maven_deps(self, content: str) -> Set[str]:
        """Extract dependencies from pom.xml."""
        deps = set()
        
        # Find dependency blocks
        pattern = r'<dependency>.*?<groupId>(.*?)</groupId>.*?<artifactId>(.*?)</artifactId>.*?</dependency>'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for group_id, artifact_id in matches:
            deps.add(f"{group_id.strip()}:{artifact_id.strip()}")
        
        return deps
    
    def _extract_gradle_deps(self, content: str) -> Set[str]:
        """Extract dependencies from build.gradle."""
        deps = set()
        
        # Look for implementation, compile, etc.
        patterns = [
            r"(?:implementation|compile|api|testImplementation)\s+['\"]([^'\"]+)['\"]",
            r"(?:implementation|compile|api|testImplementation)\s+group:\s*['\"]([^'\"]+)['\"],\s*name:\s*['\"]([^'\"]+)['\"]"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) == 2:
                        deps.add(f"{match[0]}:{match[1]}")
                else:
                    deps.add(match)
        
        return deps
    
    def get_framework_recommendations(
        self, 
        detected_stack: TechnologyStack
    ) -> List[Dict[str, Any]]:
        """Get recommendations based on detected stack."""
        recommendations = []
        
        # Missing testing framework
        if not detected_stack.testing_frameworks:
            if detected_stack.language.lower() == 'python':
                recommendations.append({
                    'type': 'missing_tool',
                    'category': 'testing',
                    'suggestion': 'Consider adding pytest for testing',
                    'priority': 'medium'
                })
            elif detected_stack.language.lower() in ['javascript', 'typescript']:
                recommendations.append({
                    'type': 'missing_tool',
                    'category': 'testing',
                    'suggestion': 'Consider adding Jest or Mocha for testing',
                    'priority': 'medium'
                })
        
        # Missing build tools for frontend projects
        frontend_frameworks = ['react', 'vue', 'angular']
        has_frontend = any(
            f.name.lower() in frontend_frameworks 
            for f in detected_stack.frameworks
        )
        
        if has_frontend and not detected_stack.build_tools:
            recommendations.append({
                'type': 'missing_tool',
                'category': 'build',
                'suggestion': 'Consider adding a build tool like Webpack or Vite',
                'priority': 'high'
            })
        
        # Security recommendations
        web_frameworks = ['django', 'flask', 'express', 'fastapi']
        has_web = any(
            f.name.lower() in web_frameworks 
            for f in detected_stack.frameworks
        )
        
        if has_web:
            recommendations.append({
                'type': 'security',
                'category': 'web_security',
                'suggestion': 'Ensure proper security headers and input validation',
                'priority': 'high'
            })
        
        return recommendations
