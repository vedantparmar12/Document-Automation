"""
Project Information Detector

Smart detection of project metadata from various sources:
- Version from package.json, pyproject.toml, setup.py, Cargo.toml, etc.
- License from LICENSE, LICENSE.md, package.json
- Description from README, package.json, pyproject.toml
- Author info from git config, package.json, pyproject.toml
- Repository URL from git remote, package.json
- Technology stack from file extensions and dependencies
"""

import os
import re
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

# Files/directories to completely ignore during analysis
IGNORE_PATTERNS = {
    # Directories
    '.git', '.svn', '.hg', '.bzr',
    'node_modules', '__pycache__', '.pytest_cache', '.mypy_cache',
    'venv', '.venv', 'env', '.env', 'virtualenv',
    'dist', 'build', 'target', 'out', 'bin', 'obj',
    '.idea', '.vscode', '.vs', '.eclipse',
    'coverage', '.coverage', 'htmlcov', '.nyc_output',
    '.tox', '.nox', 'eggs', '*.egg-info',
    '.sass-cache', '.parcel-cache', '.cache',
    'vendor', 'bower_components',
    '.terraform', '.serverless',
    'logs', 'log', 'tmp', 'temp',
    
    # Files
    '.DS_Store', 'Thumbs.db', 'desktop.ini',
    '.env', '.env.local', '.env.*.local',
    '*.pyc', '*.pyo', '*.pyd',
    '*.so', '*.dylib', '*.dll', '*.exe',
    '*.class', '*.jar', '*.war',
    '*.log', '*.lock', '*.pid',
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
    'Pipfile.lock', 'poetry.lock', 'uv.lock',
    '*.min.js', '*.min.css', '*.map',
}

# Important files for project detection (priority order)
IMPORTANT_FILES = [
    'README.md', 'README.rst', 'README.txt', 'README',
    'package.json', 'pyproject.toml', 'setup.py', 'setup.cfg',
    'Cargo.toml', 'go.mod', 'pom.xml', 'build.gradle', 'build.gradle.kts',
    'composer.json', 'Gemfile', 'mix.exs', 'pubspec.yaml',
    'requirements.txt', 'requirements.in',
    'LICENSE', 'LICENSE.md', 'LICENSE.txt', 'COPYING',
    'CHANGELOG.md', 'HISTORY.md', 'CHANGES.md',
    'CONTRIBUTING.md', 'CODE_OF_CONDUCT.md',
    'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
    '.github/workflows', 'Makefile', 'Taskfile.yml',
    'tsconfig.json', 'jsconfig.json', '.eslintrc.js', '.prettierrc',
]

# License detection patterns
LICENSE_PATTERNS = {
    'MIT': [r'MIT License', r'Permission is hereby granted, free of charge'],
    'Apache-2.0': [r'Apache License.*Version 2\.0', r'Licensed under the Apache License'],
    'GPL-3.0': [r'GNU GENERAL PUBLIC LICENSE.*Version 3', r'GPL-3\.0'],
    'GPL-2.0': [r'GNU GENERAL PUBLIC LICENSE.*Version 2', r'GPL-2\.0'],
    'BSD-3-Clause': [r'BSD 3-Clause', r'Redistribution and use in source and binary forms'],
    'BSD-2-Clause': [r'BSD 2-Clause', r'Simplified BSD License'],
    'ISC': [r'ISC License', r'ISC'],
    'Unlicense': [r'This is free and unencumbered software', r'Unlicense'],
    'AGPL-3.0': [r'GNU AFFERO GENERAL PUBLIC LICENSE', r'AGPL-3\.0'],
    'LGPL-3.0': [r'GNU LESSER GENERAL PUBLIC LICENSE.*Version 3', r'LGPL-3\.0'],
    'MPL-2.0': [r'Mozilla Public License.*2\.0', r'MPL-2\.0'],
    'CC0-1.0': [r'Creative Commons.*CC0', r'Public Domain'],
}


class ProjectInfoDetector:
    """Detects real project information from codebase."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.cache = {}
        
    def detect_all(self) -> Dict[str, Any]:
        """Detect all available project information."""
        logger.info(f"Detecting project info for: {self.project_root}")
        
        info = {
            'name': self._detect_name(),
            'version': self._detect_version(),
            'description': self._detect_description(),
            'license': self._detect_license(),
            'author': self._detect_author(),
            'repository_url': self._detect_repo_url(),
            'homepage': self._detect_homepage(),
            'keywords': self._detect_keywords(),
            'language': self._detect_primary_language(),
            'languages': self._detect_all_languages(),
            'frameworks': self._detect_frameworks(),
            'package_manager': self._detect_package_manager(),
            'has_tests': self._detect_tests(),
            'has_ci': self._detect_ci(),
            'has_docker': self._detect_docker(),
            'entry_points': self._detect_entry_points(),
        }
        
        logger.info(f"Detected project info: {info['name']} v{info['version']} ({info['license']})")
        return info
    
    def _read_file_safe(self, filepath: Path) -> Optional[str]:
        """Safely read a file, returning None if it fails."""
        try:
            if filepath.exists() and filepath.is_file():
                return filepath.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            logger.debug(f"Could not read {filepath}: {e}")
        return None
    
    def _parse_json_safe(self, content: str) -> Optional[Dict]:
        """Safely parse JSON content."""
        try:
            return json.loads(content)
        except:
            return None
    
    def _detect_name(self) -> str:
        """Detect project name from various sources."""
        # 1. Try package.json
        if content := self._read_file_safe(self.project_root / 'package.json'):
            if data := self._parse_json_safe(content):
                if name := data.get('name'):
                    return name
        
        # 2. Try pyproject.toml
        if content := self._read_file_safe(self.project_root / 'pyproject.toml'):
            if match := re.search(r'^name\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE):
                return match.group(1)
        
        # 3. Try setup.py
        if content := self._read_file_safe(self.project_root / 'setup.py'):
            if match := re.search(r'name\s*=\s*["\']([^"\']+)["\']', content):
                return match.group(1)
        
        # 4. Try Cargo.toml
        if content := self._read_file_safe(self.project_root / 'Cargo.toml'):
            if match := re.search(r'^name\s*=\s*"([^"]+)"', content, re.MULTILINE):
                return match.group(1)
        
        # 5. Try go.mod
        if content := self._read_file_safe(self.project_root / 'go.mod'):
            if match := re.search(r'^module\s+(\S+)', content, re.MULTILINE):
                return match.group(1).split('/')[-1]
        
        # 6. Fallback to directory name
        return self.project_root.name.replace('-', ' ').replace('_', ' ').title()
    
    def _detect_version(self) -> str:
        """Detect project version from various sources."""
        # 1. Try package.json
        if content := self._read_file_safe(self.project_root / 'package.json'):
            if data := self._parse_json_safe(content):
                if version := data.get('version'):
                    return version
        
        # 2. Try pyproject.toml
        if content := self._read_file_safe(self.project_root / 'pyproject.toml'):
            if match := re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE):
                return match.group(1)
        
        # 3. Try setup.py
        if content := self._read_file_safe(self.project_root / 'setup.py'):
            if match := re.search(r'version\s*=\s*["\']([^"\']+)["\']', content):
                return match.group(1)
        
        # 4. Try Cargo.toml
        if content := self._read_file_safe(self.project_root / 'Cargo.toml'):
            if match := re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE):
                return match.group(1)
        
        # 5. Try VERSION file
        if content := self._read_file_safe(self.project_root / 'VERSION'):
            return content.strip()
        
        # 6. Try __version__ in Python
        for init_file in ['__init__.py', 'src/__init__.py', 'lib/__init__.py']:
            if content := self._read_file_safe(self.project_root / init_file):
                if match := re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content):
                    return match.group(1)
        
        return "0.1.0"  # Default version
    
    def _detect_description(self) -> str:
        """Detect project description from various sources."""
        # 1. Try package.json
        if content := self._read_file_safe(self.project_root / 'package.json'):
            if data := self._parse_json_safe(content):
                if desc := data.get('description'):
                    return desc
        
        # 2. Try pyproject.toml
        if content := self._read_file_safe(self.project_root / 'pyproject.toml'):
            if match := re.search(r'^description\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE):
                return match.group(1)
        
        # 3. Try setup.py
        if content := self._read_file_safe(self.project_root / 'setup.py'):
            if match := re.search(r'description\s*=\s*["\']([^"\']+)["\']', content):
                return match.group(1)
        
        # 4. Try README first line (after title)
        for readme in ['README.md', 'README.rst', 'README.txt', 'README']:
            if content := self._read_file_safe(self.project_root / readme):
                lines = content.split('\n')
                for line in lines[1:10]:  # Check first 10 lines after title
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('=') and len(line) > 20:
                        # Remove markdown links/badges
                        clean = re.sub(r'\[!\[.*?\]\(.*?\)\]\(.*?\)', '', line)
                        clean = re.sub(r'!\[.*?\]\(.*?\)', '', clean)
                        clean = re.sub(r'\[.*?\]\(.*?\)', '', clean)
                        clean = clean.strip()
                        if len(clean) > 20:
                            return clean[:200]  # Limit length
        
        return f"A software project"
    
    def _detect_license(self) -> str:
        """Detect license from LICENSE file or package manifests."""
        # 1. Check LICENSE file
        for license_file in ['LICENSE', 'LICENSE.md', 'LICENSE.txt', 'COPYING', 'LICENSE-MIT', 'LICENSE-APACHE']:
            if content := self._read_file_safe(self.project_root / license_file):
                for license_name, patterns in LICENSE_PATTERNS.items():
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            return license_name
        
        # 2. Try package.json
        if content := self._read_file_safe(self.project_root / 'package.json'):
            if data := self._parse_json_safe(content):
                if lic := data.get('license'):
                    return lic
        
        # 3. Try pyproject.toml
        if content := self._read_file_safe(self.project_root / 'pyproject.toml'):
            if match := re.search(r'^license\s*=\s*["\']?([^"\'}\s]+)', content, re.MULTILINE):
                return match.group(1)
        
        # 4. Try Cargo.toml
        if content := self._read_file_safe(self.project_root / 'Cargo.toml'):
            if match := re.search(r'^license\s*=\s*"([^"]+)"', content, re.MULTILINE):
                return match.group(1)
        
        return "Unknown"
    
    def _detect_author(self) -> Dict[str, str]:
        """Detect author information."""
        author = {'name': '', 'email': '', 'url': ''}
        
        # 1. Try package.json
        if content := self._read_file_safe(self.project_root / 'package.json'):
            if data := self._parse_json_safe(content):
                if auth := data.get('author'):
                    if isinstance(auth, str):
                        # Parse "Name <email> (url)" format
                        if match := re.match(r'^([^<(]+?)(?:\s*<([^>]+)>)?(?:\s*\(([^)]+)\))?$', auth.strip()):
                            author['name'] = match.group(1).strip()
                            if match.group(2): author['email'] = match.group(2)
                            if match.group(3): author['url'] = match.group(3)
                    elif isinstance(auth, dict):
                        author['name'] = auth.get('name', '')
                        author['email'] = auth.get('email', '')
                        author['url'] = auth.get('url', '')
        
        # 2. Try pyproject.toml
        if not author['name']:
            if content := self._read_file_safe(self.project_root / 'pyproject.toml'):
                if match := re.search(r'^authors\s*=\s*\[\s*["\']([^"\']+)["\']', content, re.MULTILINE):
                    author['name'] = match.group(1)
        
        return author
    
    def _detect_repo_url(self) -> str:
        """Detect repository URL."""
        # 1. Try .git/config
        git_config = self.project_root / '.git' / 'config'
        if content := self._read_file_safe(git_config):
            if match := re.search(r'url\s*=\s*(\S+)', content):
                url = match.group(1)
                # Convert SSH to HTTPS
                if url.startswith('git@github.com:'):
                    url = url.replace('git@github.com:', 'https://github.com/')
                return url.rstrip('.git')
        
        # 2. Try package.json
        if content := self._read_file_safe(self.project_root / 'package.json'):
            if data := self._parse_json_safe(content):
                if repo := data.get('repository'):
                    if isinstance(repo, str):
                        return repo
                    elif isinstance(repo, dict):
                        return repo.get('url', '')
        
        return ""
    
    def _detect_homepage(self) -> str:
        """Detect project homepage."""
        # 1. Try package.json
        if content := self._read_file_safe(self.project_root / 'package.json'):
            if data := self._parse_json_safe(content):
                if homepage := data.get('homepage'):
                    return homepage
        
        # Fallback to repo URL
        return self._detect_repo_url()
    
    def _detect_keywords(self) -> List[str]:
        """Detect project keywords/tags."""
        keywords = []
        
        # 1. Try package.json
        if content := self._read_file_safe(self.project_root / 'package.json'):
            if data := self._parse_json_safe(content):
                if kw := data.get('keywords'):
                    keywords.extend(kw)
        
        # 2. Try pyproject.toml
        if content := self._read_file_safe(self.project_root / 'pyproject.toml'):
            if match := re.search(r'^keywords\s*=\s*\[(.*?)\]', content, re.MULTILINE | re.DOTALL):
                kw_str = match.group(1)
                keywords.extend(re.findall(r'["\']([^"\']+)["\']', kw_str))
        
        return list(set(keywords))
    
    def _detect_primary_language(self) -> str:
        """Detect primary programming language."""
        language_counts = self._count_files_by_extension()
        
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'JavaScript',
            '.tsx': 'TypeScript',
            '.java': 'Java',
            '.kt': 'Kotlin',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.cs': 'C#',
            '.cpp': 'C++',
            '.c': 'C',
            '.swift': 'Swift',
            '.scala': 'Scala',
            '.r': 'R',
        }
        
        best_lang = 'Unknown'
        best_count = 0
        
        for ext, count in language_counts.items():
            if ext in language_map and count > best_count:
                best_count = count
                best_lang = language_map[ext]
        
        return best_lang
    
    def _detect_all_languages(self) -> Dict[str, int]:
        """Detect all languages with file counts."""
        counts = self._count_files_by_extension()
        
        language_map = {
            '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
            '.jsx': 'JavaScript', '.tsx': 'TypeScript', '.java': 'Java',
            '.kt': 'Kotlin', '.go': 'Go', '.rs': 'Rust', '.rb': 'Ruby',
            '.php': 'PHP', '.cs': 'C#', '.cpp': 'C++', '.c': 'C',
        }
        
        result = {}
        for ext, count in counts.items():
            if ext in language_map:
                lang = language_map[ext]
                result[lang] = result.get(lang, 0) + count
        
        return result
    
    def _count_files_by_extension(self) -> Dict[str, int]:
        """Count files by extension, ignoring excluded paths."""
        counts = {}
        
        for root, dirs, files in os.walk(self.project_root):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORE_PATTERNS and not d.startswith('.')]
            
            for file in files:
                if file in IGNORE_PATTERNS or file.startswith('.'):
                    continue
                ext = Path(file).suffix.lower()
                if ext:
                    counts[ext] = counts.get(ext, 0) + 1
        
        return counts
    
    def _detect_frameworks(self) -> List[Dict[str, Any]]:
        """Detect frameworks and libraries used."""
        frameworks = []
        
        # Check for Python frameworks
        if content := self._read_file_safe(self.project_root / 'requirements.txt'):
            if 'django' in content.lower():
                frameworks.append({'name': 'Django', 'type': 'backend', 'language': 'Python'})
            if 'flask' in content.lower():
                frameworks.append({'name': 'Flask', 'type': 'backend', 'language': 'Python'})
            if 'fastapi' in content.lower():
                frameworks.append({'name': 'FastAPI', 'type': 'backend', 'language': 'Python'})
            if 'mcp' in content.lower():
                frameworks.append({'name': 'MCP', 'type': 'protocol', 'language': 'Python'})
        
        # Check for Node.js frameworks
        if content := self._read_file_safe(self.project_root / 'package.json'):
            if data := self._parse_json_safe(content):
                deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                if 'react' in deps:
                    frameworks.append({'name': 'React', 'type': 'frontend', 'language': 'JavaScript'})
                if 'vue' in deps:
                    frameworks.append({'name': 'Vue.js', 'type': 'frontend', 'language': 'JavaScript'})
                if 'express' in deps:
                    frameworks.append({'name': 'Express', 'type': 'backend', 'language': 'JavaScript'})
                if 'next' in deps:
                    frameworks.append({'name': 'Next.js', 'type': 'fullstack', 'language': 'JavaScript'})
                if '@modelcontextprotocol/sdk' in deps:
                    frameworks.append({'name': 'MCP SDK', 'type': 'protocol', 'language': 'TypeScript'})
        
        return frameworks
    
    def _detect_package_manager(self) -> str:
        """Detect package manager used."""
        if (self.project_root / 'poetry.lock').exists():
            return 'poetry'
        if (self.project_root / 'Pipfile.lock').exists():
            return 'pipenv'
        if (self.project_root / 'uv.lock').exists():
            return 'uv'
        if (self.project_root / 'requirements.txt').exists():
            return 'pip'
        if (self.project_root / 'yarn.lock').exists():
            return 'yarn'
        if (self.project_root / 'pnpm-lock.yaml').exists():
            return 'pnpm'
        if (self.project_root / 'package-lock.json').exists():
            return 'npm'
        if (self.project_root / 'Cargo.lock').exists():
            return 'cargo'
        if (self.project_root / 'go.sum').exists():
            return 'go mod'
        return 'unknown'
    
    def _detect_tests(self) -> bool:
        """Detect if project has tests."""
        test_patterns = ['test', 'tests', 'spec', 'specs', '__tests__', 'test_', '_test.py']
        for item in os.listdir(self.project_root):
            if any(p in item.lower() for p in test_patterns):
                return True
        return False
    
    def _detect_ci(self) -> Dict[str, bool]:
        """Detect CI/CD configurations."""
        return {
            'github_actions': (self.project_root / '.github' / 'workflows').exists(),
            'gitlab_ci': (self.project_root / '.gitlab-ci.yml').exists(),
            'travis': (self.project_root / '.travis.yml').exists(),
            'circle_ci': (self.project_root / '.circleci').exists(),
            'jenkins': (self.project_root / 'Jenkinsfile').exists(),
        }
    
    def _detect_docker(self) -> bool:
        """Detect if project uses Docker."""
        return (self.project_root / 'Dockerfile').exists() or (self.project_root / 'docker-compose.yml').exists()
    
    def _detect_entry_points(self) -> List[str]:
        """Detect main entry points."""
        entry_points = []
        candidates = ['main.py', 'app.py', 'server.py', 'index.js', 'index.ts', 'main.go', 'main.rs', 'src/main.py', 'src/index.ts']
        
        for candidate in candidates:
            if (self.project_root / candidate).exists():
                entry_points.append(candidate)
        
        return entry_points


def should_ignore_path(path: str) -> bool:
    """Check if a path should be ignored during analysis."""
    path_obj = Path(path)
    
    # Check each part of the path
    for part in path_obj.parts:
        if part in IGNORE_PATTERNS:
            return True
        # Check glob patterns
        for pattern in IGNORE_PATTERNS:
            if '*' in pattern:
                import fnmatch
                if fnmatch.fnmatch(part, pattern):
                    return True
    
    return False


def get_important_files(project_root: str) -> List[str]:
    """Get list of important files in priority order."""
    root = Path(project_root)
    found = []
    
    for important in IMPORTANT_FILES:
        path = root / important
        if path.exists():
            found.append(str(path))
    
    return found
