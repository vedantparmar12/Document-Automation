"""Content filter for blocking sensitive data in documentation."""

import re
import logging
from typing import List, Dict, Any, Optional, Set
from pathlib import Path

logger = logging.getLogger(__name__)


class ContentFilter:
    """Filters sensitive content from documentation output."""
    
    SENSITIVE_FILE_PATTERNS = {
        '.env', '.env.local', '.env.development', '.env.production', '.env.test', '.env.staging',
        '*.pem', '*.key', '*.crt', '*.cer', '*.p12', '*.pfx', '*.jks', '*.keystore',
        '*secret*', '*credential*', '*password*', '*token*', 'credentials.json',
        'aws_credentials', '.aws/credentials', '.gcp/credentials.json',
        'id_rsa', 'id_dsa', 'id_ecdsa', 'id_ed25519', '*.ppk',
        '*.sqlite', '*.sqlite3', '*.db', '.htpasswd', '.htaccess'
    }
    
    EXCLUDED_FOLDERS = {
        '__pycache__', 'node_modules', '.git', '.svn', '.hg', 'venv', '.venv', 'env',
        '.idea', '.vscode', '.vs', 'dist', 'build', 'target', 'out',
        '.pytest_cache', '.mypy_cache', '.tox', 'htmlcov', 'coverage', '.eggs'
    }
    
    SENSITIVE_CONTENT_PATTERNS = [
        r'(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*[=:]\s*["\']?[\w\-]{16,}["\']?',
        r'AKIA[0-9A-Z]{16}',
        r'(?i)(database[_-]?url|db[_-]?url)\s*[=:]\s*["\']?[^"\'\s]+["\']?',
        r'(?i)(postgres|mysql|mongodb)(\+srv)?://[^\s"\']+',
        r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']?[^\s"\']{4,}["\']?',
        r'-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----',
        r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*',
        r'(?i)(client[_-]?secret|private[_-]?key)\s*[=:]\s*["\']?[\w\-]{16,}["\']?'
    ]
    
    FILE_DESCRIPTIONS = {
        '.py': 'Python source', '.js': 'JavaScript source', '.ts': 'TypeScript source',
        '.jsx': 'React component', '.tsx': 'React TS component', '.json': 'JSON config',
        '.yaml': 'YAML config', '.yml': 'YAML config', '.md': 'Markdown doc',
        '.html': 'HTML template', '.css': 'CSS stylesheet', '.sql': 'SQL script',
        '.sh': 'Shell script', '.toml': 'TOML config', '.xml': 'XML file'
    }
    
    def __init__(self, custom_patterns: Optional[List[str]] = None,
                 custom_folders: Optional[Set[str]] = None,
                 custom_files: Optional[Set[str]] = None):
        self.sensitive_patterns = self.SENSITIVE_CONTENT_PATTERNS + (custom_patterns or [])
        self.excluded_folders = self.EXCLUDED_FOLDERS | (custom_folders or set())
        self.sensitive_files = self.SENSITIVE_FILE_PATTERNS | (custom_files or set())
        
        # Pre-compute lowercase sets for O(1) lookups
        self._exact_files = {p.lower() for p in self.sensitive_files if not p.startswith('*')}
        self._wildcard_patterns = [p[1:].lower() for p in self.sensitive_files if p.startswith('*')]
        self._folder_set = {f.lower() for f in self.excluded_folders}
        self._compiled_patterns = [re.compile(p) for p in self.sensitive_patterns]
    
    def is_sensitive_file(self, filepath: str) -> bool:
        """Check if file should be excluded due to sensitivity."""
        path = Path(filepath)
        filename = path.name.lower()
        
        # O(1) exact match check
        if filename in self._exact_files:
            return True
        
        # Wildcard pattern check using string methods
        if any(filename.endswith(w) or w in filename for w in self._wildcard_patterns):
            return True
        
        # Check if in excluded folder - O(1) per part
        return any(part.lower() in self._folder_set for part in path.parts)
    
    def is_excluded_folder(self, folder_path: str) -> bool:
        """Check if folder should be excluded from documentation."""
        folder_name = Path(folder_path).name.lower()
        if folder_name in self._folder_set:
            return True
        return any(folder_name.endswith(p[1:].lower()) for p in self.excluded_folders if p.startswith('*'))
    
    def contains_sensitive_content(self, content: str) -> bool:
        """Check if content contains sensitive data."""
        return any(p.search(content) for p in self._compiled_patterns)
    
    def sanitize_content(self, content: str, replacement: str = "[REDACTED]") -> str:
        """Remove or mask sensitive content from text."""
        result = content
        for pattern in self._compiled_patterns:
            result = pattern.sub(replacement, result)
        return result
    
    def filter_project_structure(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Filter sensitive files and folders from project structure."""
        if not structure:
            return structure
        
        filtered = {}
        for key, value in structure.items():
            if key == 'files' and isinstance(value, list):
                filtered['files'] = [f for f in value if not self.is_sensitive_file(
                    f.get('path', f) if isinstance(f, dict) else f)]
            elif key in ('directories', 'children'):
                if isinstance(value, list):
                    filtered[key] = [
                        self.filter_project_structure(d) if isinstance(d, dict) else d
                        for d in value
                        if not self.is_excluded_folder(d.get('name', d.get('path', '')) if isinstance(d, dict) else d)
                    ]
                elif isinstance(value, dict):
                    filtered[key] = {
                        k: self.filter_project_structure(v) if isinstance(v, dict) else v
                        for k, v in value.items() if not self.is_excluded_folder(k)
                    }
                else:
                    filtered[key] = value
            elif isinstance(value, dict):
                filtered[key] = self.filter_project_structure(value)
            else:
                filtered[key] = value
        return filtered
    
    def get_safe_file_description(self, filepath: str) -> str:
        """Get safe description of file without leaking content."""
        ext = Path(filepath).suffix.lower()
        return self.FILE_DESCRIPTIONS.get(ext, f'{ext[1:].upper()} file' if ext else 'File')
    
    def should_include_in_docs(self, filepath: str) -> bool:
        """Determine if file should be included in documentation."""
        if self.is_sensitive_file(filepath):
            return False
        ext = Path(filepath).suffix.lower()
        allowed = {'.md', '.rst', '.txt', '.json', '.yaml', '.yml', '.toml', '.py', '.js', '.ts'}
        return ext in allowed or True


def create_content_filter(strict_mode: bool = False) -> ContentFilter:
    """Factory function to create ContentFilter with preset configurations."""
    if strict_mode:
        return ContentFilter(
            custom_patterns=[r'(?i)(token|key|secret|password)[\w\-]*\s*[=:]\s*["\']?[\w\-]{8,}["\']?'],
            custom_folders={'logs', 'tmp', 'temp', 'cache'}
        )
    return ContentFilter()
