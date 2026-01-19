"""
Chunked Codebase Analyzer

This module provides a wrapper around the base analyzer that adds intelligent
chunking support for analyzing large codebases efficiently.

Features:
- Smart file chunking for large files
- Progressive analysis with token management
- Context preservation across chunks
- Support for both local and GitHub repositories
"""

import os
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Iterator
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

from src.pagination.chunker import FileChunker, ChunkStrategy, FileChunk
from src.pagination.token_estimator import TokenEstimator, ModelType
from src.pagination.strategies import (
    FilePaginationStrategy,
    ContentPaginationStrategy,
    MixedPaginationStrategy,
    PagedResult
)
from src.pagination.context import ContextManager, PaginationContext
from src.schemas import AnalysisOperationResult

logger = logging.getLogger(__name__)


@dataclass
class ChunkedAnalysisConfig:
    """Configuration for chunked analysis."""
    max_tokens_per_chunk: int = 4000
    max_file_size_bytes: int = 10 * 1024 * 1024  # 10MB
    overlap_lines: int = 5
    chunk_strategy: ChunkStrategy = ChunkStrategy.SMART
    preserve_structure: bool = True
    max_files_per_batch: int = 50
    skip_binary_files: bool = True
    skip_large_files: bool = True
    model_type: ModelType = ModelType.CLAUDE


class ChunkedCodebaseAnalyzer:
    """
    Analyzer that handles large codebases through intelligent chunking.

    This wrapper adds chunking capabilities to the standard analyzer,
    allowing it to process very large repositories without running
    into memory or context window limits.
    """

    # Directories to always skip
    SKIP_DIRS = {
        '.git', '__pycache__', 'node_modules', 'venv', '.venv', 'env',
        '.env', 'dist', 'build', '.next', '.nuxt', 'coverage', '.coverage',
        '.pytest_cache', '.mypy_cache', '.tox', 'eggs', '*.egg-info',
        '.idea', '.vscode', '.vs', 'vendor', 'bower_components'
    }

    # File extensions to skip
    SKIP_EXTENSIONS = {
        '.pyc', '.pyo', '.so', '.dll', '.dylib', '.exe', '.bin',
        '.jpg', '.jpeg', '.png', '.gif', '.ico', '.svg', '.webp',
        '.mp3', '.mp4', '.wav', '.avi', '.mov', '.mkv',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.zip', '.tar', '.gz', '.rar', '.7z', '.bz2',
        '.woff', '.woff2', '.ttf', '.eot', '.otf',
        '.lock', '.min.js', '.min.css', '.map'
    }

    # File extensions that are code
    CODE_EXTENSIONS = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c',
        '.h', '.hpp', '.cs', '.go', '.rs', '.rb', '.php', '.swift',
        '.kt', '.scala', '.vue', '.svelte', '.elm', '.clj', '.ex',
        '.exs', '.erl', '.hs', '.ml', '.fs', '.r', '.jl', '.lua',
        '.pl', '.pm', '.sh', '.bash', '.zsh', '.fish', '.ps1',
        '.sql', '.graphql', '.proto'
    }

    def __init__(self, config: Optional[ChunkedAnalysisConfig] = None):
        """Initialize the chunked analyzer."""
        self.config = config or ChunkedAnalysisConfig()
        self.token_estimator = TokenEstimator(self.config.model_type)
        self.file_chunker = FileChunker(self.token_estimator)
        self.context_manager = ContextManager()

        # Pagination strategies
        self.file_strategy = FilePaginationStrategy(
            self.file_chunker, self.token_estimator, self.context_manager
        )
        self.content_strategy = ContentPaginationStrategy(
            self.file_chunker, self.token_estimator, self.context_manager
        )
        self.mixed_strategy = MixedPaginationStrategy(
            self.file_chunker, self.token_estimator, self.context_manager
        )

        # Analysis state
        self.analysis_id = None
        self.total_files = 0
        self.processed_files = 0
        self.skipped_files = 0
        self.chunked_files = 0

    def should_skip_file(self, file_path: str) -> bool:
        """Determine if a file should be skipped."""
        path = Path(file_path)

        # Check extension
        if path.suffix.lower() in self.SKIP_EXTENSIONS:
            return True

        # Check if in skip directory
        for part in path.parts:
            if part in self.SKIP_DIRS:
                return True
            # Handle wildcard patterns
            for skip_dir in self.SKIP_DIRS:
                if '*' in skip_dir and part.endswith(skip_dir.replace('*', '')):
                    return True

        return False

    def is_code_file(self, file_path: str) -> bool:
        """Check if file is a code file."""
        return Path(file_path).suffix.lower() in self.CODE_EXTENSIONS

    def get_file_priority(self, file_path: str) -> int:
        """
        Get priority for file analysis (lower = higher priority).

        Priority order:
        1. Entry points (main.py, index.js, etc.)
        2. Configuration files
        3. Source code in src/
        4. Other code files
        5. Documentation
        6. Tests
        """
        path = Path(file_path)
        name = path.name.lower()

        # Entry points - highest priority
        entry_points = {'main.py', 'app.py', 'index.js', 'index.ts', 'server.py', 'server.js'}
        if name in entry_points:
            return 1

        # Configuration files
        config_files = {'package.json', 'requirements.txt', 'pyproject.toml', 'setup.py',
                       'cargo.toml', 'go.mod', 'pom.xml', 'build.gradle'}
        if name in config_files:
            return 2

        # Source code in src directory
        if 'src' in path.parts or 'lib' in path.parts:
            return 3

        # Test files
        if 'test' in str(path).lower() or name.startswith('test_'):
            return 6

        # Documentation
        if path.suffix.lower() in {'.md', '.rst', '.txt'}:
            return 5

        # Other code files
        if self.is_code_file(file_path):
            return 4

        return 7

    def collect_files(
        self,
        root_path: str,
        max_files: Optional[int] = None
    ) -> List[Tuple[str, int]]:
        """
        Collect all relevant files from a directory with priorities.

        Returns:
            List of (file_path, priority) tuples, sorted by priority
        """
        files = []

        for root, dirs, filenames in os.walk(root_path):
            # Filter directories
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS and not d.startswith('.')]

            for filename in filenames:
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, root_path)

                # Skip if should be skipped
                if self.should_skip_file(rel_path):
                    self.skipped_files += 1
                    continue

                # Check file size
                try:
                    file_size = os.path.getsize(file_path)
                    if self.config.skip_large_files and file_size > self.config.max_file_size_bytes:
                        logger.debug(f"Skipping large file: {rel_path} ({file_size} bytes)")
                        self.skipped_files += 1
                        continue
                except OSError:
                    continue

                priority = self.get_file_priority(rel_path)
                files.append((rel_path, priority))

        # Sort by priority
        files.sort(key=lambda x: x[1])

        # Limit if specified
        if max_files:
            files = files[:max_files]

        self.total_files = len(files)
        logger.info(f"Collected {self.total_files} files for analysis (skipped {self.skipped_files})")

        return files

    def read_file_content(self, root_path: str, rel_path: str) -> Optional[str]:
        """Safely read file content."""
        file_path = os.path.join(root_path, rel_path)

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            logger.debug(f"Could not read {rel_path}: {e}")
            return None

    def chunk_file_content(
        self,
        file_path: str,
        content: str
    ) -> List[FileChunk]:
        """
        Chunk a file's content if it's too large.

        Returns:
            List of FileChunk objects
        """
        # Estimate tokens
        tokens = self.token_estimator.estimate_tokens(content, 'code')

        if tokens <= self.config.max_tokens_per_chunk:
            # File fits in one chunk
            return [FileChunk(
                content=content,
                metadata=type('Metadata', (), {
                    'chunk_id': 'chunk_0001',
                    'file_path': file_path,
                    'start_line': 1,
                    'end_line': len(content.split('\n')),
                    'token_count': tokens,
                    'content_type': 'code',
                    'chunk_strategy': ChunkStrategy.SMART
                })()
            )]

        # File needs chunking
        self.chunked_files += 1
        logger.debug(f"Chunking large file: {file_path} ({tokens} tokens)")

        return self.file_chunker.chunk_file(
            file_path=file_path,
            content=content,
            strategy=self.config.chunk_strategy,
            max_tokens_per_chunk=self.config.max_tokens_per_chunk,
            overlap_lines=self.config.overlap_lines,
            preserve_structure=self.config.preserve_structure
        )

    def analyze_files_in_batches(
        self,
        root_path: str,
        files: List[Tuple[str, int]],
        batch_size: Optional[int] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Analyze files in batches, yielding results progressively.

        Args:
            root_path: Root directory path
            files: List of (file_path, priority) tuples
            batch_size: Number of files per batch

        Yields:
            Dict with batch analysis results
        """
        batch_size = batch_size or self.config.max_files_per_batch

        for i in range(0, len(files), batch_size):
            batch = files[i:i + batch_size]
            batch_results = {
                'batch_number': i // batch_size + 1,
                'files': [],
                'total_tokens': 0,
                'chunks': []
            }

            for rel_path, priority in batch:
                content = self.read_file_content(root_path, rel_path)
                if content is None:
                    continue

                # Chunk if necessary
                chunks = self.chunk_file_content(rel_path, content)

                file_result = {
                    'path': rel_path,
                    'priority': priority,
                    'total_chunks': len(chunks),
                    'total_tokens': sum(
                        getattr(c.metadata, 'token_count', 0) for c in chunks
                    )
                }

                batch_results['files'].append(file_result)
                batch_results['total_tokens'] += file_result['total_tokens']

                for chunk in chunks:
                    batch_results['chunks'].append({
                        'file': rel_path,
                        'content': chunk.content,
                        'start_line': getattr(chunk.metadata, 'start_line', 1),
                        'end_line': getattr(chunk.metadata, 'end_line', 0),
                        'tokens': getattr(chunk.metadata, 'token_count', 0)
                    })

                self.processed_files += 1

            yield batch_results

    async def analyze_with_chunking(
        self,
        root_path: str,
        source_type: str = 'local',
        max_files: Optional[int] = None
    ) -> AnalysisOperationResult:
        """
        Analyze a codebase with full chunking support.

        Args:
            root_path: Path to the codebase
            source_type: 'local' or 'github'
            max_files: Maximum number of files to analyze

        Returns:
            AnalysisOperationResult with chunked analysis data
        """
        from datetime import datetime

        self.analysis_id = f"chunked_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()

        logger.info(f"Starting chunked analysis of {root_path}")

        try:
            # Collect files
            files = self.collect_files(root_path, max_files)

            if not files:
                return AnalysisOperationResult(
                    success=False,
                    message="No files found to analyze",
                    data={}
                )

            # Analyze in batches
            all_results = {
                'project_name': os.path.basename(root_path),
                'analysis_id': self.analysis_id,
                'source_type': source_type,
                'total_files': self.total_files,
                'skipped_files': self.skipped_files,
                'chunked_files': 0,
                'batches': [],
                'file_contents': {},
                'chunks_by_file': {},
                'analysis_summary': {}
            }

            for batch_result in self.analyze_files_in_batches(root_path, files):
                all_results['batches'].append({
                    'batch_number': batch_result['batch_number'],
                    'files_count': len(batch_result['files']),
                    'total_tokens': batch_result['total_tokens']
                })

                # Store file contents for analysis
                for chunk_data in batch_result['chunks']:
                    file_path = chunk_data['file']
                    if file_path not in all_results['file_contents']:
                        all_results['file_contents'][file_path] = []
                    all_results['file_contents'][file_path].append(chunk_data['content'])

                    # Track chunks by file
                    if file_path not in all_results['chunks_by_file']:
                        all_results['chunks_by_file'][file_path] = []
                    all_results['chunks_by_file'][file_path].append({
                        'start_line': chunk_data['start_line'],
                        'end_line': chunk_data['end_line'],
                        'tokens': chunk_data['tokens']
                    })

            all_results['chunked_files'] = self.chunked_files

            # Calculate summary
            total_tokens = sum(b['total_tokens'] for b in all_results['batches'])
            all_results['analysis_summary'] = {
                'total_files_analyzed': self.processed_files,
                'total_files_skipped': self.skipped_files,
                'total_files_chunked': self.chunked_files,
                'total_batches': len(all_results['batches']),
                'total_tokens_estimated': total_tokens,
                'analysis_duration_seconds': (datetime.now() - start_time).total_seconds()
            }

            logger.info(f"Chunked analysis complete: {self.processed_files} files, "
                       f"{self.chunked_files} chunked, {total_tokens} total tokens")

            return AnalysisOperationResult(
                success=True,
                message=f"Successfully analyzed {self.processed_files} files with chunking",
                data=all_results
            )

        except Exception as e:
            logger.error(f"Chunked analysis failed: {e}")
            return AnalysisOperationResult(
                success=False,
                message=f"Analysis failed: {str(e)}",
                data={'error': str(e)}
            )

    def get_paginated_content(
        self,
        root_path: str,
        file_path: str,
        context_token: Optional[str] = None
    ) -> PagedResult:
        """
        Get paginated content for a specific file.

        Args:
            root_path: Root directory path
            file_path: Relative path to file
            context_token: Token from previous pagination (for continuation)

        Returns:
            PagedResult with current chunk and pagination info
        """
        content = self.read_file_content(root_path, file_path)
        if content is None:
            return PagedResult(
                content='',
                pagination_info={'error': 'File not found'},
                context_token=None
            )

        return self.content_strategy.paginate(
            file_path=file_path,
            content=content,
            context_token=context_token,
            chunk_strategy=self.config.chunk_strategy,
            max_tokens_per_chunk=self.config.max_tokens_per_chunk
        )


# Convenience function for quick analysis
async def analyze_codebase_with_chunking(
    path: str,
    source_type: str = 'local',
    max_tokens_per_chunk: int = 4000,
    max_files: Optional[int] = None
) -> AnalysisOperationResult:
    """
    Convenience function to analyze a codebase with chunking.

    Args:
        path: Path to codebase (local path or GitHub URL)
        source_type: 'local' or 'github'
        max_tokens_per_chunk: Maximum tokens per chunk
        max_files: Maximum files to analyze

    Returns:
        AnalysisOperationResult with analysis data
    """
    config = ChunkedAnalysisConfig(max_tokens_per_chunk=max_tokens_per_chunk)
    analyzer = ChunkedCodebaseAnalyzer(config)

    return await analyzer.analyze_with_chunking(
        root_path=path,
        source_type=source_type,
        max_files=max_files
    )
