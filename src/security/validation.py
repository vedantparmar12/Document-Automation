import re
import os
import logging
from typing import Set, List, Optional
from urllib.parse import urlparse
from src.schemas import SecurityValidationResult, UserProps

logger = logging.getLogger(__name__)

# Allowed GitHub usernames for write operations (similar to original)
ALLOWED_USERNAMES: Set[str] = {
    # Add GitHub usernames of users who should have access to write operations
    # For example: 'yourusername', 'coworkerusername'
    'coleam00'  # Replace with actual usernames
}

# Dangerous path patterns to block
DANGEROUS_PATHS = [
    r'\.\./',  # Path traversal
    r'\.\.\\\\',  # Windows path traversal
    r'/etc/',  # System directories
    r'C:\\\\Windows',  # Windows system directories
    r'/usr/bin/',  # System binaries
    r'/root/',  # Root directory
    r'~/',  # Home directory shortcuts
]

# Allowed file extensions for analysis
ALLOWED_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp',
    '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala', '.r',
    '.json', '.yaml', '.yml', '.xml', '.toml', '.ini', '.cfg', '.conf',
    '.md', '.txt', '.rst', '.html', '.css', '.scss', '.sass', '.less',
    '.sql', '.dockerfile', '.makefile', '.sh', '.bat', '.ps1'
}

# Maximum file size for analysis (in bytes)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_path(path: str) -> SecurityValidationResult:
    """
    Validate if a path is safe for analysis.
    
    Args:
        path: The path to validate
        
    Returns:
        SecurityValidationResult with validation status
    """
    if not path:
        return SecurityValidationResult(
            is_valid=False,
            error="Path cannot be empty"
        )
    
    # Check for dangerous path patterns
    for pattern in DANGEROUS_PATHS:
        if re.search(pattern, path, re.IGNORECASE):
            return SecurityValidationResult(
                is_valid=False,
                error=f"Path contains potentially dangerous pattern: {pattern}"
            )
    
    # Validate absolute paths
    if os.path.isabs(path):
        # Check if it's trying to access system directories
        normalized_path = os.path.normpath(path)
        if any(normalized_path.startswith(danger) for danger in ['/etc', '/usr/bin', '/root', 'C:\\Windows']):
            return SecurityValidationResult(
                is_valid=False,
                error="Access to system directories is not allowed"
            )
    
    return SecurityValidationResult(is_valid=True)

def validate_github_url(url: str) -> SecurityValidationResult:
    """
    Validate if a GitHub URL is safe and properly formatted.
    
    Args:
        url: The GitHub URL to validate
        
    Returns:
        SecurityValidationResult with validation status
    """
    if not url:
        return SecurityValidationResult(
            is_valid=False,
            error="GitHub URL cannot be empty"
        )
    
    try:
        parsed = urlparse(url)
        
        # Must be GitHub
        if parsed.netloc.lower() not in ['github.com', 'www.github.com']:
            return SecurityValidationResult(
                is_valid=False,
                error="Only GitHub URLs are allowed"
            )
        
        # Must be HTTPS
        if parsed.scheme != 'https':
            return SecurityValidationResult(
                is_valid=False,
                error="Only HTTPS URLs are allowed"
            )
        
        # Basic path validation
        if not parsed.path or parsed.path == '/':
            return SecurityValidationResult(
                is_valid=False,
                error="GitHub URL must point to a specific repository"
            )
        
        # Check for valid repository path format
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) < 2:
            return SecurityValidationResult(
                is_valid=False,
                error="GitHub URL must be in format: https://github.com/owner/repo"
            )
        
        return SecurityValidationResult(is_valid=True)
    
    except Exception as e:
        return SecurityValidationResult(
            is_valid=False,
            error=f"Invalid URL format: {str(e)}"
        )

def validate_file_extension(file_path: str) -> bool:
    """
    Check if a file extension is allowed for analysis.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if extension is allowed, False otherwise
    """
    _, ext = os.path.splitext(file_path.lower())
    return ext in ALLOWED_EXTENSIONS

def validate_file_size(file_path: str) -> SecurityValidationResult:
    """
    Validate if a file size is within allowed limits.
    
    Args:
        file_path: Path to the file
        
    Returns:
        SecurityValidationResult with validation status
    """
    try:
        if not os.path.exists(file_path):
            return SecurityValidationResult(
                is_valid=False,
                error="File does not exist"
            )
        
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            return SecurityValidationResult(
                is_valid=False,
                error=f"File size ({file_size} bytes) exceeds maximum allowed size ({MAX_FILE_SIZE} bytes)"
            )
        
        return SecurityValidationResult(is_valid=True)
    
    except Exception as e:
        return SecurityValidationResult(
            is_valid=False,
            error=f"Error checking file size: {str(e)}"
        )

def has_write_permissions(user_props: UserProps) -> bool:
    """
    Check if a user has write permissions (similar to original ALLOWED_USERNAMES check).
    
    Args:
        user_props: User properties from OAuth
        
    Returns:
        True if user has write permissions, False otherwise
    """
    return user_props.login in ALLOWED_USERNAMES

def sanitize_error_message(error: Exception) -> str:
    """
    Sanitize error messages to prevent information disclosure.
    
    Args:
        error: The exception to sanitize
        
    Returns:
        Sanitized error message
    """
    error_str = str(error)
    
    # Remove sensitive information
    sanitized = re.sub(r'[A-Za-z0-9+/]{20,}', '[REDACTED]', error_str)  # API keys/tokens
    sanitized = re.sub(r'password[=:]\s*\S+', 'password=[REDACTED]', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'token[=:]\s*\S+', 'token=[REDACTED]', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'secret[=:]\s*\S+', 'secret=[REDACTED]', sanitized, flags=re.IGNORECASE)
    
    return sanitized

def validate_analysis_request(path: str, source_type: str) -> SecurityValidationResult:
    """
    Comprehensive validation for analysis requests.
    
    Args:
        path: The path or URL to validate
        source_type: Type of source ('local' or 'github')
        
    Returns:
        SecurityValidationResult with validation status
    """
    if source_type == 'local':
        return validate_path(path)
    elif source_type == 'github':
        return validate_github_url(path)
    else:
        return SecurityValidationResult(
            is_valid=False,
            error=f"Invalid source type: {source_type}. Must be 'local' or 'github'"
        )

def log_security_event(event_type: str, details: str, user_props: Optional[UserProps] = None):
    """
    Log security-related events for monitoring.
    
    Args:
        event_type: Type of security event
        details: Details of the event
        user_props: User properties if available
    """
    user_info = f"user={user_props.login}" if user_props else "user=anonymous"
    logger.warning(f"SECURITY_EVENT: {event_type} | {details} | {user_info}")

