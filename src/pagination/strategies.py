"""
Pagination strategies for different types of content and analysis operations.

This module provides different strategies for handling pagination across
files, content chunks, and analysis results.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple, Iterator
from dataclasses import dataclass
from enum import Enum

from .chunker import FileChunker, ChunkStrategy, FileChunk
from .context import PaginationContext, ContextManager
from .token_estimator import TokenEstimator

logger = logging.getLogger(__name__)


class PaginationMode(Enum):
    """Different modes of pagination."""
    FILE_BY_FILE = "file_by_file"       # Paginate through files
    CHUNK_BY_CHUNK = "chunk_by_chunk"   # Paginate through chunks within files
    MIXED = "mixed"                     # Combine file and chunk pagination
    RESULT_SET = "result_set"           # Paginate through analysis results


@dataclass
class PagedResult:
    """Result of a paginated operation."""
    content: Any
    pagination_info: Dict[str, Any]
    context_token: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @property
    def has_next_page(self) -> bool:
        """Check if there are more pages."""
        return self.pagination_info.get('has_next', False)
    
    @property
    def has_previous_page(self) -> bool:
        """Check if there are previous pages."""
        return self.pagination_info.get('has_previous', False)
    
    @property
    def current_page(self) -> int:
        """Get current page number (1-based)."""
        return self.pagination_info.get('current_page', 1)
    
    @property
    def total_pages(self) -> int:
        """Get total number of pages."""
        return self.pagination_info.get('total_pages', 1)


class PaginationStrategy(ABC):
    """Base class for pagination strategies."""
    
    def __init__(
        self,
        chunker: Optional[FileChunker] = None,
        token_estimator: Optional[TokenEstimator] = None,
        context_manager: Optional[ContextManager] = None
    ):
        self.chunker = chunker or FileChunker()
        self.token_estimator = token_estimator or TokenEstimator()
        self.context_manager = context_manager or ContextManager()
    
    @abstractmethod
    def paginate(
        self,
        data: Any,
        page_size: Optional[int] = None,
        context_token: Optional[str] = None,
        **kwargs
    ) -> PagedResult:
        """
        Paginate data according to strategy.
        
        Args:
            data: Data to paginate
            page_size: Maximum size per page
            context_token: Token from previous pagination
            **kwargs: Strategy-specific parameters
            
        Returns:
            PagedResult with current page data and pagination info
        """
        pass
    
    @abstractmethod
    def get_total_pages(self, data: Any, page_size: int, **kwargs) -> int:
        """Get total number of pages for given data."""
        pass
    
    def create_pagination_info(
        self,
        current_page: int,
        total_pages: int,
        has_next: bool,
        has_previous: bool,
        **extra_info
    ) -> Dict[str, Any]:
        """Create standardized pagination info."""
        return {
            'current_page': current_page,
            'total_pages': total_pages,
            'has_next': has_next,
            'has_previous': has_previous,
            'pagination_mode': self.__class__.__name__,
            **extra_info
        }


class FilePaginationStrategy(PaginationStrategy):
    """
    Pagination strategy that operates on files.
    
    Each page contains one or more complete files, respecting token limits.
    """
    
    def paginate(
        self,
        file_paths: List[str],
        page_size: Optional[int] = None,
        context_token: Optional[str] = None,
        file_contents: Optional[Dict[str, str]] = None,
        max_tokens_per_page: Optional[int] = None,
        **kwargs
    ) -> PagedResult:
        """
        Paginate through files.
        
        Args:
            file_paths: List of file paths to paginate
            page_size: Maximum files per page (overridden by token limits)
            context_token: Previous pagination context
            file_contents: Optional dict of file path -> content
            max_tokens_per_page: Maximum tokens per page
            
        Returns:
            PagedResult with files for current page
        """
        if not file_paths:
            return PagedResult(
                content=[],
                pagination_info=self.create_pagination_info(1, 1, False, False)
            )
        
        # Get context or create new one
        if context_token:
            context = self.context_manager.decrypt_context_token(context_token)
            if not context:
                # Invalid/expired token, start from beginning
                current_file_index = 0
            else:
                current_file_index = context.current_file_index
        else:
            current_file_index = 0
        
        # Determine page size based on token limits
        if max_tokens_per_page is None:
            max_tokens_per_page = self.token_estimator.token_limits.safe_input_limit // 2
        
        if page_size is None:
            page_size = len(file_paths)  # Will be limited by tokens below
        
        # Build current page
        page_files = []
        current_tokens = 0
        files_in_page = 0
        start_index = current_file_index
        
        for i in range(current_file_index, len(file_paths)):
            file_path = file_paths[i]
            
            # Estimate tokens for this file
            if file_contents and file_path in file_contents:
                content = file_contents[file_path]
                file_tokens = self.token_estimator.estimate_tokens(content, 'code')
            else:
                # Estimate based on file size if no content provided
                try:
                    import os
                    file_size = os.path.getsize(file_path)
                    file_tokens = file_size // 4  # Rough estimate
                except:
                    file_tokens = 1000  # Default estimate
            
            # Check if adding this file would exceed limits
            if (current_tokens + file_tokens > max_tokens_per_page and page_files) or \
               (files_in_page >= page_size and page_files):
                break
            
            page_files.append(file_path)
            current_tokens += file_tokens
            files_in_page += 1
            current_file_index = i + 1
        
        # Create pagination info
        has_next = current_file_index < len(file_paths)
        has_previous = start_index > 0
        current_page = (start_index // max(1, files_in_page)) + 1
        total_pages = (len(file_paths) + files_in_page - 1) // max(1, files_in_page)
        
        pagination_info = self.create_pagination_info(
            current_page, total_pages, has_next, has_previous,
            files_in_page=files_in_page,
            total_files=len(file_paths),
            start_file_index=start_index,
            end_file_index=current_file_index - 1,
            tokens_used=current_tokens
        )
        
        # Create new context for next request
        new_context = self.context_manager.create_context(
            analysis_id=kwargs.get('analysis_id', 'file_pagination'),
            file_path=page_files[0] if page_files else '',
            total_files=len(file_paths),
            total_chunks=1,  # Files are not chunked in this strategy
            chunk_strategy='file_based',
            current_file_index=current_file_index,
            current_chunk_index=0
        )
        
        new_context_token = self.context_manager.encrypt_context_token(new_context)
        
        return PagedResult(
            content=page_files,
            pagination_info=pagination_info,
            context_token=new_context_token if has_next else None
        )
    
    def get_total_pages(
        self,
        file_paths: List[str],
        page_size: int,
        **kwargs
    ) -> int:
        """Get total number of pages for file list."""
        if not file_paths:
            return 1
        return (len(file_paths) + page_size - 1) // page_size


class ContentPaginationStrategy(PaginationStrategy):
    """
    Pagination strategy that operates on content chunks.
    
    Files are chunked and each page contains one or more chunks.
    """
    
    def paginate(
        self,
        file_path: str,
        content: str,
        page_size: Optional[int] = None,
        context_token: Optional[str] = None,
        chunk_strategy: ChunkStrategy = ChunkStrategy.SMART,
        max_tokens_per_chunk: Optional[int] = None,
        **kwargs
    ) -> PagedResult:
        """
        Paginate through content chunks.
        
        Args:
            file_path: Path to file being chunked
            content: File content
            page_size: Chunks per page (usually 1 for large chunks)
            context_token: Previous pagination context
            chunk_strategy: Strategy for chunking content
            max_tokens_per_chunk: Maximum tokens per chunk
            
        Returns:
            PagedResult with chunk(s) for current page
        """
        if not content.strip():
            return PagedResult(
                content='',
                pagination_info=self.create_pagination_info(1, 1, False, False)
            )
        
        # Get context or create new one
        if context_token:
            context = self.context_manager.decrypt_context_token(context_token)
            if not context:
                current_chunk_index = 0
            else:
                current_chunk_index = context.current_chunk_index
        else:
            current_chunk_index = 0
        
        # Chunk the content
        chunks = self.chunker.chunk_file(
            file_path=file_path,
            content=content,
            strategy=chunk_strategy,
            max_tokens_per_chunk=max_tokens_per_chunk
        )
        
        if not chunks:
            return PagedResult(
                content='',
                pagination_info=self.create_pagination_info(1, 1, False, False)
            )
        
        # Validate chunk index
        if current_chunk_index >= len(chunks):
            current_chunk_index = len(chunks) - 1
        
        # Get current chunk(s)
        chunks_per_page = page_size or 1
        start_chunk = current_chunk_index
        end_chunk = min(start_chunk + chunks_per_page, len(chunks))
        
        page_chunks = chunks[start_chunk:end_chunk]
        
        # Create pagination info
        has_next = end_chunk < len(chunks)
        has_previous = start_chunk > 0
        current_page = (start_chunk // chunks_per_page) + 1
        total_pages = (len(chunks) + chunks_per_page - 1) // chunks_per_page
        
        pagination_info = self.create_pagination_info(
            current_page, total_pages, has_next, has_previous,
            chunks_in_page=len(page_chunks),
            total_chunks=len(chunks),
            start_chunk_index=start_chunk,
            end_chunk_index=end_chunk - 1,
            chunk_strategy=chunk_strategy.value,
            file_path=file_path
        )
        
        # Create new context for next request
        if has_next:
            new_context = self.context_manager.create_context(
                analysis_id=kwargs.get('analysis_id', 'content_pagination'),
                file_path=file_path,
                total_files=1,
                total_chunks=len(chunks),
                chunk_strategy=chunk_strategy.value,
                current_file_index=0,
                current_chunk_index=end_chunk
            )
            new_context_token = self.context_manager.encrypt_context_token(new_context)
        else:
            new_context_token = None
        
        # Format content for return
        if len(page_chunks) == 1:
            content_result = {
                'chunk': page_chunks[0].content,
                'metadata': page_chunks[0].metadata.__dict__
            }
        else:
            content_result = {
                'chunks': [
                    {
                        'chunk': chunk.content,
                        'metadata': chunk.metadata.__dict__
                    }
                    for chunk in page_chunks
                ]
            }
        
        return PagedResult(
            content=content_result,
            pagination_info=pagination_info,
            context_token=new_context_token
        )
    
    def get_total_pages(
        self,
        content: str,
        page_size: int,
        chunk_strategy: ChunkStrategy = ChunkStrategy.SMART,
        **kwargs
    ) -> int:
        """Get total number of pages for content."""
        if not content.strip():
            return 1
        
        # This requires chunking the content, which is expensive
        # For estimation, use token-based calculation
        total_tokens = self.token_estimator.estimate_tokens(content, 'code')
        max_tokens_per_chunk = kwargs.get('max_tokens_per_chunk') or (
            self.token_estimator.token_limits.safe_input_limit // 4
        )
        
        estimated_chunks = max(1, (total_tokens + max_tokens_per_chunk - 1) // max_tokens_per_chunk)
        return (estimated_chunks + page_size - 1) // page_size


class MixedPaginationStrategy(PaginationStrategy):
    """
    Mixed pagination strategy that handles both files and chunks.
    
    Automatically switches between file-level and chunk-level pagination
    based on content size and token limits.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_strategy = FilePaginationStrategy(
            self.chunker, self.token_estimator, self.context_manager
        )
        self.content_strategy = ContentPaginationStrategy(
            self.chunker, self.token_estimator, self.context_manager
        )
    
    def paginate(
        self,
        data: Dict[str, Any],
        page_size: Optional[int] = None,
        context_token: Optional[str] = None,
        **kwargs
    ) -> PagedResult:
        """
        Paginate using mixed strategy.
        
        Args:
            data: Dict with 'files' list and optional 'contents' dict
            page_size: Maximum items per page
            context_token: Previous pagination context
            
        Returns:
            PagedResult with mixed content
        """
        files = data.get('files', [])
        contents = data.get('contents', {})
        
        if not files:
            return PagedResult(
                content={},
                pagination_info=self.create_pagination_info(1, 1, False, False)
            )
        
        # Get context
        if context_token:
            context = self.context_manager.decrypt_context_token(context_token)
            if not context:
                current_file_index = 0
                current_chunk_index = 0
            else:
                current_file_index = context.current_file_index
                current_chunk_index = context.current_chunk_index
        else:
            current_file_index = 0
            current_chunk_index = 0
        
        # Determine if current file needs chunking
        if current_file_index >= len(files):
            # End of files reached
            return PagedResult(
                content={},
                pagination_info=self.create_pagination_info(1, 1, False, False)
            )
        
        current_file = files[current_file_index]
        file_content = contents.get(current_file, '')
        
        # Check if file needs chunking
        needs_chunking = not self.token_estimator.can_fit_in_context(file_content, 'code')
        
        if needs_chunking and current_chunk_index == 0:
            # Start chunking this file
            result = self.content_strategy.paginate(
                file_path=current_file,
                content=file_content,
                context_token=None,  # Start fresh for this file
                analysis_id=kwargs.get('analysis_id', 'mixed_pagination'),
                **kwargs
            )
            
            # Update context to track chunking progress
            context = self.context_manager.create_context(
                analysis_id=kwargs.get('analysis_id', 'mixed_pagination'),
                file_path=current_file,
                total_files=len(files),
                total_chunks=result.pagination_info.get('total_chunks', 1),
                chunk_strategy='mixed',
                current_file_index=current_file_index,
                current_chunk_index=1 if result.has_next_page else 0
            )
            
        elif needs_chunking and current_chunk_index > 0:
            # Continue chunking current file
            chunk_context = self.context_manager.create_context(
                analysis_id=kwargs.get('analysis_id', 'mixed_pagination'),
                file_path=current_file,
                total_files=1,
                total_chunks=1,  # Will be updated by content strategy
                chunk_strategy='mixed',
                current_chunk_index=current_chunk_index
            )
            chunk_token = self.context_manager.encrypt_context_token(chunk_context)
            
            result = self.content_strategy.paginate(
                file_path=current_file,
                content=file_content,
                context_token=chunk_token,
                **kwargs
            )
            
            # Check if file chunking is complete
            if not result.has_next_page:
                # Move to next file
                current_file_index += 1
                current_chunk_index = 0
            else:
                current_chunk_index += 1
                
        else:
            # File fits in context, return as single item
            result = PagedResult(
                content={
                    'file_path': current_file,
                    'content': file_content,
                    'type': 'complete_file'
                },
                pagination_info=self.create_pagination_info(
                    current_file_index + 1, len(files),
                    current_file_index + 1 < len(files),
                    current_file_index > 0,
                    file_path=current_file,
                    content_type='complete_file'
                )
            )
            
            current_file_index += 1
            current_chunk_index = 0
        
        # Create context token for next request
        if current_file_index < len(files) or (needs_chunking and result.has_next_page):
            new_context = self.context_manager.create_context(
                analysis_id=kwargs.get('analysis_id', 'mixed_pagination'),
                file_path=files[min(current_file_index, len(files) - 1)],
                total_files=len(files),
                total_chunks=1,
                chunk_strategy='mixed',
                current_file_index=current_file_index,
                current_chunk_index=current_chunk_index
            )
            result.context_token = self.context_manager.encrypt_context_token(new_context)
        
        return result
    
    def get_total_pages(self, data: Dict[str, Any], page_size: int, **kwargs) -> int:
        """Estimate total pages for mixed strategy."""
        files = data.get('files', [])
        contents = data.get('contents', {})
        
        total_pages = 0
        for file_path in files:
            content = contents.get(file_path, '')
            if self.token_estimator.can_fit_in_context(content, 'code'):
                total_pages += 1
            else:
                # Estimate pages needed for chunked content
                chunk_pages = self.content_strategy.get_total_pages(content, 1, **kwargs)
                total_pages += chunk_pages
        
        return max(1, total_pages)


class ResultSetPaginationStrategy(PaginationStrategy):
    """
    Pagination strategy for analysis results.
    
    Used for paginating through large result sets like dependency lists,
    API endpoints, etc.
    """
    
    def paginate(
        self,
        results: List[Dict[str, Any]],
        page_size: int = 50,
        context_token: Optional[str] = None,
        **kwargs
    ) -> PagedResult:
        """
        Paginate through result list.
        
        Args:
            results: List of result items
            page_size: Items per page
            context_token: Previous pagination context
            
        Returns:
            PagedResult with current page of results
        """
        if not results:
            return PagedResult(
                content=[],
                pagination_info=self.create_pagination_info(1, 1, False, False)
            )
        
        # Get current page from context
        if context_token:
            context = self.context_manager.decrypt_context_token(context_token)
            current_page = context.current_chunk_index if context else 1
        else:
            current_page = 1
        
        # Calculate pagination
        total_items = len(results)
        total_pages = (total_items + page_size - 1) // page_size
        
        if current_page < 1:
            current_page = 1
        elif current_page > total_pages:
            current_page = total_pages
        
        start_index = (current_page - 1) * page_size
        end_index = min(start_index + page_size, total_items)
        
        page_results = results[start_index:end_index]
        
        # Create pagination info
        has_next = current_page < total_pages
        has_previous = current_page > 1
        
        pagination_info = self.create_pagination_info(
            current_page, total_pages, has_next, has_previous,
            items_in_page=len(page_results),
            total_items=total_items,
            start_index=start_index,
            end_index=end_index - 1
        )
        
        # Create context token for next page
        if has_next:
            new_context = self.context_manager.create_context(
                analysis_id=kwargs.get('analysis_id', 'result_pagination'),
                file_path='results',
                total_files=1,
                total_chunks=total_pages,
                chunk_strategy='result_set',
                current_chunk_index=current_page + 1
            )
            new_context_token = self.context_manager.encrypt_context_token(new_context)
        else:
            new_context_token = None
        
        return PagedResult(
            content=page_results,
            pagination_info=pagination_info,
            context_token=new_context_token
        )
    
    def get_total_pages(self, results: List[Any], page_size: int, **kwargs) -> int:
        """Get total pages for result set."""
        if not results:
            return 1
        return (len(results) + page_size - 1) // page_size
