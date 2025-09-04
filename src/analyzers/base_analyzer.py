"""
Base analyzer class for code analysis

This module provides the foundation for analyzing different types of codebases
and extracting their structure, dependencies, and metadata.
"""

import os
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import json
import git
import requests
import shutil
import time
import stat
import errno
from datetime import datetime

from src.schemas import (
    CodeAnalysisResult,
    DirectoryInfo,
    FileInfo,
    SourceType,
    AnalysisOperationResult
)
from src.security.validation import (
    validate_analysis_request,
    validate_file_extension,
    validate_file_size,
    sanitize_error_message
)

# Set up a logger for this module to record events and errors.
logger = logging.getLogger(__name__)


def _handle_remove_readonly(func, path, exc):
    """
    Error handler for shutil.rmtree.

    If the error is due to a read-only file, it attempts to change
    the file's permissions and then retries the deletion.
    """
    excvalue = exc[1]
    if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise

class BaseAnalyzer(ABC):
    """
    Base class for all code analyzers.
    
    Provides common functionality for analyzing codebases from different sources
    (local directories, GitHub repositories, etc.). This is an abstract class
    and is meant to be inherited by more specific analyzer implementations.
    """

    def __init__(self, path: str, source_type: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the analyzer.
        
        Args:
            path: The file system path or URL to analyze (e.g., a local directory or a GitHub URL).
            source_type: The type of source, which must be 'local' or 'github'.
            config: An optional dictionary for configuration parameters.
        """
        self.path = path
        self.source_type = SourceType(source_type)
        self.config = config or {}
        self.analysis_id = self._generate_analysis_id()
        self.temp_dir = None  # This will store the path to a temporary directory if one is created.

        # Set default configuration values, allowing them to be overridden by the config dictionary.
        self.max_file_size = self.config.get('max_file_size', 10 * 1024 * 1024)  # 10MB
        self.max_depth = self.config.get('max_depth', 10)
        self.include_hidden = self.config.get('include_hidden', False)
        self.timeout = self.config.get('timeout', 300)  # 5 minutes

    def _generate_analysis_id(self) -> str:
        """Generate a unique ID for each analysis session."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        path_hash = abs(hash(self.path)) % 10000
        return f"analysis_{timestamp}_{path_hash}"

    async def analyze(self) -> AnalysisOperationResult:
        """
        Main analysis method that orchestrates the entire analysis process.
        
        Returns:
            An AnalysisOperationResult object containing the analysis data or error information.
        """
        start_time = datetime.now()

        try:
            # First, validate the request to ensure it's safe and well-formed.
            validation_result = validate_analysis_request(self.path, self.source_type.value)
            if not validation_result.is_valid:
                return AnalysisOperationResult(
                    success=False,
                    error=f"Validation failed: {validation_result.error}"
                )

            logger.info(f"Starting analysis {self.analysis_id} for {self.source_type.value}: {self.path}")

            # Prepare the codebase, which includes cloning from GitHub if necessary.
            await self._prepare_codebase()

            # Perform the different stages of analysis.
            project_structure = await self._analyze_structure()
            dependencies = await self._analyze_dependencies()
            api_endpoints = await self._extract_api_endpoints()
            architecture_info = await self._analyze_architecture()
            metrics = await self._calculate_metrics()

            # Consolidate the results into a single object.
            analysis_result = CodeAnalysisResult(
                project_structure=project_structure,
                dependencies=dependencies,
                api_endpoints=api_endpoints,
                architecture_info=architecture_info,
                metrics=metrics
            )

            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Analysis {self.analysis_id} completed in {duration:.2f}s")

            return AnalysisOperationResult(
                success=True,
                data=analysis_result.dict(),
                duration=duration
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_msg = sanitize_error_message(e)
            logger.error(f"Analysis {self.analysis_id} failed after {duration:.2f}s: {error_msg}")

            return AnalysisOperationResult(
                success=False,
                error=error_msg,
                duration=duration
            )

        finally:
            # Always attempt to clean up temporary resources, regardless of success or failure.
            await self._cleanup()

    async def _prepare_codebase(self):
        """Prepare the codebase for analysis (e.g., download from GitHub if needed)."""
        if self.source_type == SourceType.GITHUB:
            await self._clone_github_repo()
        elif self.source_type == SourceType.LOCAL:
            await self._validate_local_path()

    async def _clone_github_repo(self):
        """Clone a GitHub repository to a temporary directory."""
        import tempfile

        # Create a unique temporary directory for the cloned repository.
        self.temp_dir = tempfile.mkdtemp(prefix=f"analysis_{self.analysis_id}_")

        try:
            github_url = self.path
            if not github_url.endswith('.git'):
                github_url += '.git'

            logger.info(f"Cloning repository: {github_url}")

            # Clone the repository into the temporary directory.
            repo = git.Repo.clone_from(github_url, self.temp_dir)

            # Set the working path to the temporary directory for subsequent analysis.
            self.working_path = self.temp_dir

            logger.info(f"Repository cloned to: {self.temp_dir}")

        except Exception as e:
            # If cloning fails, clean up the partially created directory.
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, onerror=_handle_remove_readonly)
            raise Exception(f"Failed to clone repository: {str(e)}")

    async def _validate_local_path(self):
        """Validate and set up a local path for analysis."""
        if not os.path.exists(self.path):
            raise Exception(f"Local path does not exist: {self.path}")

        if not os.path.isdir(self.path):
            raise Exception(f"Path is not a directory: {self.path}")

        self.working_path = self.path

    async def _analyze_structure(self) -> DirectoryInfo:
        """Analyze the project structure and return directory information."""
        return await self._scan_directory(self.working_path, max_depth=self.max_depth)

    async def _scan_directory(self, directory_path: str, current_depth: int = 0, max_depth: int = 10) -> DirectoryInfo:
        """
        Recursively scan a directory to map its structure.
        
        Args:
            directory_path: The path of the directory to scan.
            current_depth: The current recursion depth.
            max_depth: The maximum recursion depth to prevent infinite loops.
            
        Returns:
            A DirectoryInfo object representing the scanned directory.
        """
        if current_depth > max_depth:
            logger.warning(f"Maximum depth {max_depth} reached for {directory_path}")
            return DirectoryInfo(
                name=os.path.basename(directory_path),
                path=directory_path,
                files=[],
                subdirectories=[]
            )

        files = []
        subdirectories = []

        try:
            for item in os.listdir(directory_path):
                if not self.include_hidden and item.startswith('.'):
                    continue

                item_path = os.path.join(directory_path, item)

                if os.path.isfile(item_path):
                    # Validate file extension and size before including it in the results.
                    if validate_file_extension(item_path):
                        size_validation = validate_file_size(item_path)
                        if size_validation.is_valid:
                            stat_result = os.stat(item_path)
                            files.append(FileInfo(
                                name=item,
                                path=item_path,
                                size=stat_result.st_size,
                                type=self._get_file_type(item_path),
                                last_modified=datetime.fromtimestamp(stat_result.st_mtime).isoformat()
                            ))
                        else:
                            logger.warning(f"Skipping file {item_path}: {size_validation.error}")

                elif os.path.isdir(item_path):
                    # Recursively call this function for subdirectories.
                    subdir_info = await self._scan_directory(
                        item_path,
                        current_depth + 1,
                        max_depth
                    )
                    subdirectories.append(subdir_info)

        except PermissionError as e:
            logger.warning(f"Permission denied accessing {directory_path}: {str(e)}")
        except Exception as e:
            logger.error(f"Error scanning {directory_path}: {str(e)}")

        return DirectoryInfo(
            name=os.path.basename(directory_path),
            path=directory_path,
            files=files,
            subdirectories=subdirectories
        )

    def _get_file_type(self, file_path: str) -> str:
        """Determine the file type based on its extension."""
        _, ext = os.path.splitext(file_path.lower())

        type_mapping = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript', '.tsx': 'typescript',
            '.jsx': 'javascript', '.java': 'java', '.cpp': 'cpp', '.c': 'c', '.h': 'c_header',
            '.hpp': 'cpp_header', '.cs': 'csharp', '.go': 'go', '.rs': 'rust', '.rb': 'ruby',
            '.php': 'php', '.swift': 'swift', '.kt': 'kotlin', '.scala': 'scala', '.r': 'r',
            '.json': 'json', '.yaml': 'yaml', '.yml': 'yaml', '.xml': 'xml', '.toml': 'toml',
            '.ini': 'ini', '.cfg': 'config', '.conf': 'config', '.md': 'markdown', '.txt': 'text',
            '.rst': 'restructuredtext', '.html': 'html', '.css': 'css', '.scss': 'scss',
            '.sass': 'sass', '.less': 'less', '.sql': 'sql', '.dockerfile': 'dockerfile',
            '.makefile': 'makefile', '.sh': 'shell', '.bat': 'batch', '.ps1': 'powershell'
        }

        return type_mapping.get(ext, 'unknown')

    @abstractmethod
    async def _analyze_dependencies(self) -> List[str]:
        """Analyze project dependencies. This must be implemented by subclasses."""
        pass

    @abstractmethod
    async def _extract_api_endpoints(self) -> List[Dict[str, Any]]:
        """Extract API endpoints. This must be implemented by subclasses."""
        pass

    @abstractmethod
    async def _analyze_architecture(self) -> Dict[str, Any]:
        """Analyze the project's architecture. This must be implemented by subclasses."""
        pass

    @abstractmethod
    async def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate code metrics. This must be implemented by subclasses."""
        pass

    async def _cleanup(self):
        """Clean up temporary resources, like the cloned repository directory."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            # A retry mechanism to handle lingering process locks, common on Windows.
            retries = 3
            for i in range(retries):
                try:
                    # Use the onerror handler to deal with read-only file issues.
                    shutil.rmtree(self.temp_dir, onerror=_handle_remove_readonly)
                    logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
                    return  # Exit the function if cleanup is successful.
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary directory (attempt {i+1}/{retries}): {self.temp_dir}: {str(e)}")
                    time.sleep(2)  # Increased sleep time to 2 seconds before retrying.

    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get a summary of the analysis configuration."""
        return {
            'analysis_id': self.analysis_id,
            'path': self.path,
            'source_type': self.source_type.value,
            'config': self.config,
            'max_file_size': self.max_file_size,
            'max_depth': self.max_depth,
            'include_hidden': self.include_hidden,
            'timeout': self.timeout
        }
