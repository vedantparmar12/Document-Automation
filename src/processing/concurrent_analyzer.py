"""
Concurrent file analysis system for processing multiple files in parallel.

This module provides concurrent analysis capabilities with proper resource
management and result aggregation.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Callable, Awaitable, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import aiofiles
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Result of analyzing a single file or component."""
    file_path: str
    analysis_type: str
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_time: float = 0.0
    file_size: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def size_mb(self) -> float:
        """Get file size in MB."""
        return self.file_size / (1024 * 1024)


@dataclass
class BatchAnalysisResult:
    """Result of analyzing a batch of files."""
    total_files: int
    successful: int
    failed: int
    results: List[AnalysisResult]
    execution_time: float
    errors: List[str] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.total_files == 0:
            return 100.0
        return (self.successful / self.total_files) * 100


class ConcurrentAnalyzer:
    """
    Concurrent analyzer for processing multiple files in parallel.
    
    Provides controlled parallelism with resource management and
    progress tracking for large codebases.
    """
    
    def __init__(
        self,
        max_concurrent_files: int = 8,
        max_file_size_mb: int = 10,
        timeout_per_file: float = 30.0,
        memory_limit_mb: Optional[int] = None
    ):
        self.max_concurrent_files = max_concurrent_files
        self.max_file_size_mb = max_file_size_mb
        self.timeout_per_file = timeout_per_file
        self.memory_limit_mb = memory_limit_mb
        
        # Resource management
        self.semaphore = asyncio.Semaphore(max_concurrent_files)
        self.thread_executor = ThreadPoolExecutor(max_workers=max_concurrent_files)
        
        # Analysis handlers
        self.file_analyzers: Dict[str, Callable] = {}
        self.content_analyzers: Dict[str, Callable] = {}
        
        # Progress tracking
        self.progress_callbacks: List[Callable[[str, float, Dict[str, Any]], None]] = []
        
        # Statistics
        self.stats = {
            'files_processed': 0,
            'total_processing_time': 0.0,
            'average_file_time': 0.0,
            'files_skipped': 0,
            'errors': 0
        }
    
    def register_file_analyzer(
        self, 
        file_extension: str, 
        analyzer: Callable[[str, str], Awaitable[Dict[str, Any]]]
    ) -> None:
        """
        Register an analyzer for specific file types.
        
        Args:
            file_extension: File extension (e.g., '.py', '.js')
            analyzer: Async function that analyzes file content
        """
        self.file_analyzers[file_extension.lower()] = analyzer
        logger.info(f"Registered analyzer for {file_extension} files")
    
    def register_content_analyzer(
        self,
        content_type: str,
        analyzer: Callable[[str, Dict[str, Any]], Awaitable[Dict[str, Any]]]
    ) -> None:
        """
        Register an analyzer for specific content types.
        
        Args:
            content_type: Content type identifier
            analyzer: Async function that analyzes content
        """
        self.content_analyzers[content_type] = analyzer
        logger.info(f"Registered content analyzer for {content_type}")
    
    def add_progress_callback(
        self, 
        callback: Callable[[str, float, Dict[str, Any]], None]
    ) -> None:
        """Add progress callback function."""
        self.progress_callbacks.append(callback)
    
    async def analyze_files(
        self,
        file_paths: List[str],
        analysis_types: Optional[List[str]] = None,
        batch_size: Optional[int] = None,
        progress_callback: Optional[Callable[[str, float, Dict[str, Any]], None]] = None
    ) -> BatchAnalysisResult:
        """
        Analyze multiple files concurrently.
        
        Args:
            file_paths: List of file paths to analyze
            analysis_types: Optional list of analysis types to perform
            batch_size: Size of batches for processing
            progress_callback: Optional progress callback
            
        Returns:
            BatchAnalysisResult with aggregated results
        """
        start_time = time.time()
        
        if progress_callback:
            self.add_progress_callback(progress_callback)
        
        # Filter and validate files
        valid_files = await self._filter_valid_files(file_paths)
        logger.info(f"Analyzing {len(valid_files)} files (filtered from {len(file_paths)})")
        
        if not valid_files:
            return BatchAnalysisResult(
                total_files=len(file_paths),
                successful=0,
                failed=0,
                results=[],
                execution_time=time.time() - start_time,
                errors=["No valid files to analyze"]
            )
        
        # Process files in batches if specified
        if batch_size:
            results = await self._analyze_in_batches(valid_files, batch_size, analysis_types)
        else:
            results = await self._analyze_concurrent(valid_files, analysis_types)
        
        # Aggregate results
        successful = len([r for r in results if r.success])
        failed = len([r for r in results if not r.success])
        errors = [r.error for r in results if r.error]
        
        execution_time = time.time() - start_time
        
        # Update stats
        self.stats['files_processed'] += len(results)
        self.stats['total_processing_time'] += execution_time
        self.stats['average_file_time'] = (
            self.stats['total_processing_time'] / self.stats['files_processed']
            if self.stats['files_processed'] > 0 else 0
        )
        self.stats['errors'] += failed
        
        batch_result = BatchAnalysisResult(
            total_files=len(file_paths),
            successful=successful,
            failed=failed,
            results=results,
            execution_time=execution_time,
            errors=errors
        )
        
        logger.info(
            f"Batch analysis completed: {successful} successful, {failed} failed, "
            f"{execution_time:.2f}s total"
        )
        
        return batch_result
    
    async def analyze_single_file(
        self,
        file_path: str,
        analysis_types: Optional[List[str]] = None
    ) -> AnalysisResult:
        """
        Analyze a single file.
        
        Args:
            file_path: Path to file to analyze
            analysis_types: Optional list of analysis types
            
        Returns:
            AnalysisResult for the file
        """
        async with self.semaphore:
            return await self._analyze_file_internal(file_path, analysis_types)
    
    async def _analyze_concurrent(
        self,
        file_paths: List[str],
        analysis_types: Optional[List[str]] = None
    ) -> List[AnalysisResult]:
        """Analyze files with controlled concurrency."""
        tasks = []
        
        for file_path in file_paths:
            task = asyncio.create_task(
                self.analyze_single_file(file_path, analysis_types)
            )
            tasks.append(task)
        
        # Process with progress updates
        results = []
        completed = 0
        total = len(tasks)
        
        for coro in asyncio.as_completed(tasks):
            try:
                result = await coro
                results.append(result)
                completed += 1
                
                # Update progress
                progress = completed / total
                await self._notify_progress(
                    f"Processed {completed}/{total} files",
                    progress,
                    {
                        'completed': completed,
                        'total': total,
                        'current_file': result.file_path,
                        'success': result.success
                    }
                )
                
            except Exception as e:
                logger.error(f"Failed to process file: {e}")
                # Create error result
                error_result = AnalysisResult(
                    file_path="unknown",
                    analysis_type="error",
                    success=False,
                    error=str(e)
                )
                results.append(error_result)
                completed += 1
        
        return results
    
    async def _analyze_in_batches(
        self,
        file_paths: List[str],
        batch_size: int,
        analysis_types: Optional[List[str]] = None
    ) -> List[AnalysisResult]:
        """Analyze files in batches to manage memory usage."""
        all_results = []
        total_files = len(file_paths)
        
        for i in range(0, total_files, batch_size):
            batch = file_paths[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_files + batch_size - 1) // batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} files)")
            
            # Process batch
            batch_results = await self._analyze_concurrent(batch, analysis_types)
            all_results.extend(batch_results)
            
            # Update progress
            progress = len(all_results) / total_files
            await self._notify_progress(
                f"Completed batch {batch_num}/{total_batches}",
                progress,
                {
                    'batch': batch_num,
                    'total_batches': total_batches,
                    'files_completed': len(all_results),
                    'total_files': total_files
                }
            )
            
            # Optional memory cleanup between batches
            if batch_num < total_batches:
                await asyncio.sleep(0.1)  # Brief pause
        
        return all_results
    
    async def _analyze_file_internal(
        self,
        file_path: str,
        analysis_types: Optional[List[str]] = None
    ) -> AnalysisResult:
        """Internal file analysis with timeout and error handling."""
        start_time = time.time()
        
        try:
            # Check file size
            try:
                file_size = Path(file_path).stat().st_size
            except Exception:
                file_size = 0
            
            if file_size > self.max_file_size_mb * 1024 * 1024:
                return AnalysisResult(
                    file_path=file_path,
                    analysis_type="size_check",
                    success=False,
                    error=f"File too large: {file_size / 1024 / 1024:.1f}MB > {self.max_file_size_mb}MB",
                    file_size=file_size
                )
            
            # Read file content
            try:
                content = await self._read_file_safe(file_path)
            except Exception as e:
                return AnalysisResult(
                    file_path=file_path,
                    analysis_type="file_read",
                    success=False,
                    error=f"Failed to read file: {str(e)}",
                    file_size=file_size
                )
            
            # Perform analysis
            analysis_result = await asyncio.wait_for(
                self._perform_analysis(file_path, content, analysis_types),
                timeout=self.timeout_per_file
            )
            
            execution_time = time.time() - start_time
            
            return AnalysisResult(
                file_path=file_path,
                analysis_type="complete",
                success=True,
                data=analysis_result,
                execution_time=execution_time,
                file_size=file_size
            )
            
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            return AnalysisResult(
                file_path=file_path,
                analysis_type="timeout",
                success=False,
                error=f"Analysis timed out after {self.timeout_per_file}s",
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return AnalysisResult(
                file_path=file_path,
                analysis_type="error",
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    async def _read_file_safe(self, file_path: str) -> str:
        """Safely read file content with encoding detection."""
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                async with aiofiles.open(file_path, 'r', encoding=encoding) as f:
                    return await f.read()
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.warning(f"Failed to read {file_path} with {encoding}: {e}")
                continue
        
        # Last resort: read as binary and decode with errors='ignore'
        try:
            async with aiofiles.open(file_path, 'rb') as f:
                content_bytes = await f.read()
                return content_bytes.decode('utf-8', errors='ignore')
        except Exception as e:
            raise Exception(f"Unable to read file with any encoding: {e}")
    
    async def _perform_analysis(
        self,
        file_path: str,
        content: str,
        analysis_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Perform analysis on file content."""
        results = {}
        
        # Get file extension
        file_ext = Path(file_path).suffix.lower()
        
        # File-specific analysis
        if file_ext in self.file_analyzers:
            analyzer = self.file_analyzers[file_ext]
            try:
                file_analysis = await analyzer(file_path, content)
                results['file_analysis'] = file_analysis
            except Exception as e:
                logger.error(f"File analyzer failed for {file_path}: {e}")
                results['file_analysis_error'] = str(e)
        
        # Content-based analysis
        if analysis_types:
            for analysis_type in analysis_types:
                if analysis_type in self.content_analyzers:
                    analyzer = self.content_analyzers[analysis_type]
                    try:
                        content_analysis = await analyzer(content, {'file_path': file_path})
                        results[analysis_type] = content_analysis
                    except Exception as e:
                        logger.error(f"Content analyzer {analysis_type} failed for {file_path}: {e}")
                        results[f"{analysis_type}_error"] = str(e)
        
        # Basic analysis if no specific analyzers
        if not results:
            results = await self._basic_analysis(file_path, content)
        
        return results
    
    async def _basic_analysis(self, file_path: str, content: str) -> Dict[str, Any]:
        """Perform basic analysis on any file."""
        lines = content.split('\n')
        
        return {
            'line_count': len(lines),
            'char_count': len(content),
            'empty_lines': len([line for line in lines if not line.strip()]),
            'file_type': Path(file_path).suffix.lower() or 'unknown',
            'estimated_tokens': len(content) // 4,  # Rough estimate
        }
    
    async def _filter_valid_files(self, file_paths: List[str]) -> List[str]:
        """Filter out invalid or inaccessible files."""
        valid_files = []
        
        for file_path in file_paths:
            try:
                path = Path(file_path)
                if path.is_file() and path.stat().st_size > 0:
                    valid_files.append(file_path)
                else:
                    self.stats['files_skipped'] += 1
            except Exception:
                self.stats['files_skipped'] += 1
                continue
        
        return valid_files
    
    async def _notify_progress(
        self, 
        message: str, 
        progress: float, 
        details: Dict[str, Any]
    ) -> None:
        """Notify all progress callbacks."""
        for callback in self.progress_callbacks:
            try:
                callback(message, progress, details)
            except Exception as e:
                logger.error(f"Progress callback failed: {e}")
    
    async def shutdown(self) -> None:
        """Shutdown the analyzer and cleanup resources."""
        logger.info("Shutting down concurrent analyzer")
        
        # Shutdown thread executor
        self.thread_executor.shutdown(wait=True)
        
        # Clear callbacks
        self.progress_callbacks.clear()
        
        logger.info("Concurrent analyzer shutdown complete")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get analyzer statistics."""
        return {
            **self.stats,
            'max_concurrent_files': self.max_concurrent_files,
            'max_file_size_mb': self.max_file_size_mb,
            'timeout_per_file': self.timeout_per_file,
            'registered_file_analyzers': list(self.file_analyzers.keys()),
            'registered_content_analyzers': list(self.content_analyzers.keys())
        }


# Convenience functions for common analysis tasks

async def analyze_python_file(file_path: str, content: str) -> Dict[str, Any]:
    """Analyze Python file structure."""
    import re
    
    # Find classes and functions
    classes = re.findall(r'^\s*class\s+(\w+).*?:', content, re.MULTILINE)
    functions = re.findall(r'^\s*def\s+(\w+).*?:', content, re.MULTILINE)
    imports = re.findall(r'^\s*(?:import|from)\s+([^\s]+)', content, re.MULTILINE)
    
    return {
        'classes': classes,
        'functions': functions,
        'imports': imports,
        'has_main': '__main__' in content,
        'is_test': any(keyword in file_path.lower() for keyword in ['test', 'spec']),
    }


async def analyze_javascript_file(file_path: str, content: str) -> Dict[str, Any]:
    """Analyze JavaScript file structure."""
    import re
    
    # Find functions, classes, and imports
    functions = re.findall(r'function\s+(\w+)\s*\(', content)
    arrow_functions = re.findall(r'(?:const|let|var)\s+(\w+)\s*=\s*(?:\([^)]*\)|[^=\s]+)\s*=>', content)
    classes = re.findall(r'class\s+(\w+)', content)
    imports = re.findall(r'import.*?from\s+[\'"]([^\'"]+)[\'"]', content)
    requires = re.findall(r'require\([\'"]([^\'"]+)[\'"]\)', content)
    
    return {
        'functions': functions,
        'arrow_functions': arrow_functions,
        'classes': classes,
        'imports': imports,
        'requires': requires,
        'has_exports': 'export' in content or 'module.exports' in content,
        'is_react': 'React' in content or 'jsx' in Path(file_path).suffix.lower(),
    }


# Global analyzer instance
_analyzer: Optional[ConcurrentAnalyzer] = None


def get_concurrent_analyzer() -> ConcurrentAnalyzer:
    """Get global concurrent analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = ConcurrentAnalyzer()
        
        # Register default analyzers
        _analyzer.register_file_analyzer('.py', analyze_python_file)
        _analyzer.register_file_analyzer('.js', analyze_javascript_file)
        _analyzer.register_file_analyzer('.jsx', analyze_javascript_file)
        _analyzer.register_file_analyzer('.ts', analyze_javascript_file)
        _analyzer.register_file_analyzer('.tsx', analyze_javascript_file)
        
    return _analyzer
