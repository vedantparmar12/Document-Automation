"""
File chunking system for handling large files with context preservation.

This module provides smart chunking strategies that respect code structure
and maintain context between chunks.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .token_estimator import TokenEstimator, ModelType

logger = logging.getLogger(__name__)


class ChunkStrategy(Enum):
    """Different strategies for chunking files."""
    LINE_BASED = "line_based"       # Split by lines
    FUNCTION_BASED = "function_based" # Split by functions/methods
    CLASS_BASED = "class_based"     # Split by classes
    SECTION_BASED = "section_based" # Split by logical sections
    TOKEN_BASED = "token_based"     # Split by token count only
    SMART = "smart"                 # Intelligent splitting based on content type


@dataclass
class ChunkMetadata:
    """Metadata for a content chunk."""
    chunk_id: str
    file_path: str
    start_line: int
    end_line: int
    token_count: int
    content_type: str
    chunk_strategy: ChunkStrategy
    overlap_with_previous: bool = False
    overlap_with_next: bool = False
    context_summary: Optional[str] = None


@dataclass
class FileChunk:
    """A chunk of file content with metadata."""
    content: str
    metadata: ChunkMetadata
    
    def __str__(self) -> str:
        return f"Chunk {self.metadata.chunk_id}: lines {self.metadata.start_line}-{self.metadata.end_line}"


class FileChunker:
    """
    Smart file chunker that handles different content types and preserves context.
    """
    
    # Patterns for different code structures
    FUNCTION_PATTERNS = {
        'python': [
            r'^(\s*)def\s+(\w+)\s*\(',
            r'^(\s*)async\s+def\s+(\w+)\s*\(',
            r'^(\s*)class\s+(\w+)\s*[:\(]'
        ],
        'javascript': [
            r'^\s*function\s+(\w+)\s*\(',
            r'^\s*const\s+(\w+)\s*=\s*\(',
            r'^\s*(\w+)\s*:\s*function\s*\(',
            r'^\s*class\s+(\w+)\s*\{'
        ],
        'java': [
            r'^\s*(public|private|protected)?\s*(static)?\s*\w+\s+(\w+)\s*\(',
            r'^\s*(public|private|protected)?\s*class\s+(\w+)\s*\{'
        ],
        'cpp': [
            r'^\s*\w+\s+(\w+)\s*\([^)]*\)\s*\{',
            r'^\s*class\s+(\w+)\s*\{'
        ]
    }
    
    # Logical section patterns
    SECTION_PATTERNS = {
        'markdown': [
            r'^#{1,6}\s+(.+)$',  # Headers
        ],
        'restructuredtext': [
            r'^[=\-~`#"^+*]{4,}$',  # Section underlines
        ]
    }
    
    def __init__(self, token_estimator: Optional[TokenEstimator] = None):
        self.token_estimator = token_estimator or TokenEstimator()
        self.chunk_counter = 0
    
    def chunk_file(
        self,
        file_path: str,
        content: str,
        strategy: ChunkStrategy = ChunkStrategy.SMART,
        max_tokens_per_chunk: Optional[int] = None,
        overlap_lines: int = 3,
        preserve_structure: bool = True
    ) -> List[FileChunk]:
        """
        Chunk a file's content using the specified strategy.
        
        Args:
            file_path: Path to the file being chunked
            content: File content to chunk
            strategy: Chunking strategy to use
            max_tokens_per_chunk: Maximum tokens per chunk
            overlap_lines: Number of lines to overlap between chunks
            preserve_structure: Whether to preserve code structure
            
        Returns:
            List of file chunks
        """
        if not content.strip():
            return []
        
        # Determine content type from file extension
        content_type = self._detect_content_type(file_path)
        
        # Set default max tokens if not provided
        if max_tokens_per_chunk is None:
            max_tokens_per_chunk = self.token_estimator.get_max_chunk_size(content_type) // 4
        
        # Choose strategy based on content if SMART is selected
        if strategy == ChunkStrategy.SMART:
            strategy = self._choose_smart_strategy(content, content_type)
        
        # Chunk based on strategy
        if strategy == ChunkStrategy.LINE_BASED:
            return self._chunk_by_lines(
                file_path, content, content_type, max_tokens_per_chunk, overlap_lines
            )
        elif strategy == ChunkStrategy.FUNCTION_BASED:
            return self._chunk_by_functions(
                file_path, content, content_type, max_tokens_per_chunk, preserve_structure
            )
        elif strategy == ChunkStrategy.CLASS_BASED:
            return self._chunk_by_classes(
                file_path, content, content_type, max_tokens_per_chunk, preserve_structure
            )
        elif strategy == ChunkStrategy.SECTION_BASED:
            return self._chunk_by_sections(
                file_path, content, content_type, max_tokens_per_chunk, overlap_lines
            )
        else:  # TOKEN_BASED
            return self._chunk_by_tokens(
                file_path, content, content_type, max_tokens_per_chunk, overlap_lines
            )
    
    def _detect_content_type(self, file_path: str) -> str:
        """Detect content type from file extension."""
        suffix = Path(file_path).suffix.lower()
        
        type_mapping = {
            '.py': 'code',
            '.js': 'code', 
            '.ts': 'code',
            '.jsx': 'code',
            '.tsx': 'code',
            '.java': 'code',
            '.cpp': 'code',
            '.c': 'code',
            '.h': 'code',
            '.cs': 'code',
            '.php': 'code',
            '.rb': 'code',
            '.go': 'code',
            '.rs': 'code',
            '.swift': 'code',
            '.kt': 'code',
            '.md': 'markdown',
            '.rst': 'markdown',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.xml': 'xml',
            '.html': 'xml',
            '.css': 'code',
            '.scss': 'code',
            '.less': 'code'
        }
        
        return type_mapping.get(suffix, 'plain_text')
    
    def _choose_smart_strategy(self, content: str, content_type: str) -> ChunkStrategy:
        """Choose the best chunking strategy based on content analysis."""
        lines = content.split('\n')
        
        if content_type == 'markdown':
            return ChunkStrategy.SECTION_BASED
        
        if content_type == 'code':
            # Check for class definitions
            if self._has_classes(content):
                return ChunkStrategy.CLASS_BASED
            # Check for function definitions  
            elif self._has_functions(content):
                return ChunkStrategy.FUNCTION_BASED
            else:
                return ChunkStrategy.LINE_BASED
        
        return ChunkStrategy.TOKEN_BASED
    
    def _has_classes(self, content: str) -> bool:
        """Check if content contains class definitions."""
        class_patterns = [
            r'^\s*class\s+\w+',
            r'^\s*(public|private|protected)?\s*class\s+\w+'
        ]
        return any(re.search(pattern, content, re.MULTILINE) for pattern in class_patterns)
    
    def _has_functions(self, content: str) -> bool:
        """Check if content contains function definitions."""
        function_patterns = [
            r'^\s*def\s+\w+\s*\(',
            r'^\s*function\s+\w+\s*\(',
            r'^\s*(public|private|protected)?\s*\w+\s+\w+\s*\('
        ]
        return any(re.search(pattern, content, re.MULTILINE) for pattern in function_patterns)
    
    def _chunk_by_lines(
        self,
        file_path: str,
        content: str,
        content_type: str,
        max_tokens: int,
        overlap_lines: int
    ) -> List[FileChunk]:
        """Chunk content by lines with token limits."""
        lines = content.split('\n')
        chunks = []
        current_lines = []
        current_tokens = 0
        start_line = 1
        
        for i, line in enumerate(lines):
            line_tokens = self.token_estimator.estimate_tokens(line, content_type)
            
            if current_tokens + line_tokens > max_tokens and current_lines:
                # Create chunk
                chunk_content = '\n'.join(current_lines)
                chunk = self._create_chunk(
                    chunk_content, file_path, start_line, start_line + len(current_lines) - 1,
                    current_tokens, content_type, ChunkStrategy.LINE_BASED
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_start = max(0, len(current_lines) - overlap_lines)
                current_lines = current_lines[overlap_start:] + [line]
                start_line = start_line + overlap_start
                current_tokens = sum(
                    self.token_estimator.estimate_tokens(l, content_type) 
                    for l in current_lines
                )
            else:
                current_lines.append(line)
                current_tokens += line_tokens
        
        # Add final chunk
        if current_lines:
            chunk_content = '\n'.join(current_lines)
            chunk = self._create_chunk(
                chunk_content, file_path, start_line, start_line + len(current_lines) - 1,
                current_tokens, content_type, ChunkStrategy.LINE_BASED
            )
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_by_functions(
        self,
        file_path: str,
        content: str,
        content_type: str,
        max_tokens: int,
        preserve_structure: bool
    ) -> List[FileChunk]:
        """Chunk content by functions/methods."""
        lines = content.split('\n')
        functions = self._find_functions(lines, content_type)
        
        if not functions:
            # Fallback to line-based chunking
            return self._chunk_by_lines(file_path, content, content_type, max_tokens, 3)
        
        chunks = []
        current_functions = []
        current_tokens = 0
        
        for func_info in functions:
            func_lines = lines[func_info['start']:func_info['end']]
            func_content = '\n'.join(func_lines)
            func_tokens = self.token_estimator.estimate_tokens(func_content, content_type)
            
            if current_tokens + func_tokens > max_tokens and current_functions:
                # Create chunk from current functions
                chunk_content = self._combine_functions(current_functions, lines)
                start_line = current_functions[0]['start'] + 1
                end_line = current_functions[-1]['end']
                
                chunk = self._create_chunk(
                    chunk_content, file_path, start_line, end_line,
                    current_tokens, content_type, ChunkStrategy.FUNCTION_BASED
                )
                chunks.append(chunk)
                
                current_functions = [func_info]
                current_tokens = func_tokens
            else:
                current_functions.append(func_info)
                current_tokens += func_tokens
        
        # Add final chunk
        if current_functions:
            chunk_content = self._combine_functions(current_functions, lines)
            start_line = current_functions[0]['start'] + 1
            end_line = current_functions[-1]['end']
            
            chunk = self._create_chunk(
                chunk_content, file_path, start_line, end_line,
                current_tokens, content_type, ChunkStrategy.FUNCTION_BASED
            )
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_by_classes(
        self,
        file_path: str,
        content: str,
        content_type: str,
        max_tokens: int,
        preserve_structure: bool
    ) -> List[FileChunk]:
        """Chunk content by classes."""
        lines = content.split('\n')
        classes = self._find_classes(lines, content_type)
        
        if not classes:
            # Fallback to function-based chunking
            return self._chunk_by_functions(file_path, content, content_type, max_tokens, preserve_structure)
        
        chunks = []
        
        for class_info in classes:
            class_lines = lines[class_info['start']:class_info['end']]
            class_content = '\n'.join(class_lines)
            class_tokens = self.token_estimator.estimate_tokens(class_content, content_type)
            
            if class_tokens <= max_tokens:
                # Class fits in one chunk
                chunk = self._create_chunk(
                    class_content, file_path, class_info['start'] + 1, class_info['end'],
                    class_tokens, content_type, ChunkStrategy.CLASS_BASED
                )
                chunks.append(chunk)
            else:
                # Split class by methods
                method_chunks = self._chunk_by_functions(
                    file_path, class_content, content_type, max_tokens, preserve_structure
                )
                chunks.extend(method_chunks)
        
        return chunks
    
    def _chunk_by_sections(
        self,
        file_path: str,
        content: str,
        content_type: str,
        max_tokens: int,
        overlap_lines: int
    ) -> List[FileChunk]:
        """Chunk content by logical sections (e.g., markdown headers)."""
        lines = content.split('\n')
        sections = self._find_sections(lines, content_type)
        
        if not sections:
            # Fallback to line-based chunking
            return self._chunk_by_lines(file_path, content, content_type, max_tokens, overlap_lines)
        
        chunks = []
        current_sections = []
        current_tokens = 0
        
        for section_info in sections:
            section_lines = lines[section_info['start']:section_info['end']]
            section_content = '\n'.join(section_lines)
            section_tokens = self.token_estimator.estimate_tokens(section_content, content_type)
            
            if current_tokens + section_tokens > max_tokens and current_sections:
                # Create chunk from current sections
                chunk_content = self._combine_sections(current_sections, lines)
                start_line = current_sections[0]['start'] + 1
                end_line = current_sections[-1]['end']
                
                chunk = self._create_chunk(
                    chunk_content, file_path, start_line, end_line,
                    current_tokens, content_type, ChunkStrategy.SECTION_BASED
                )
                chunks.append(chunk)
                
                current_sections = [section_info]
                current_tokens = section_tokens
            else:
                current_sections.append(section_info)
                current_tokens += section_tokens
        
        # Add final chunk
        if current_sections:
            chunk_content = self._combine_sections(current_sections, lines)
            start_line = current_sections[0]['start'] + 1
            end_line = current_sections[-1]['end']
            
            chunk = self._create_chunk(
                chunk_content, file_path, start_line, end_line,
                current_tokens, content_type, ChunkStrategy.SECTION_BASED
            )
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_by_tokens(
        self,
        file_path: str,
        content: str,
        content_type: str,
        max_tokens: int,
        overlap_lines: int
    ) -> List[FileChunk]:
        """Chunk content purely by token count."""
        token_chunks = self.token_estimator.split_by_token_limit(
            content, content_type, max_tokens, overlap_lines * 20  # Approximate overlap
        )
        
        chunks = []
        current_line = 1
        
        for i, chunk_content in enumerate(token_chunks):
            chunk_lines = len(chunk_content.split('\n'))
            chunk_tokens = self.token_estimator.estimate_tokens(chunk_content, content_type)
            
            chunk = self._create_chunk(
                chunk_content, file_path, current_line, current_line + chunk_lines - 1,
                chunk_tokens, content_type, ChunkStrategy.TOKEN_BASED
            )
            chunks.append(chunk)
            current_line += chunk_lines
        
        return chunks
    
    def _find_functions(self, lines: List[str], content_type: str) -> List[Dict[str, Any]]:
        """Find function boundaries in code."""
        functions = []
        
        # Get language-specific patterns
        lang = self._get_language_from_content_type(content_type)
        patterns = self.FUNCTION_PATTERNS.get(lang, [])
        
        for i, line in enumerate(lines):
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    # Find end of function by indentation or braces
                    end_line = self._find_block_end(lines, i, lang)
                    functions.append({
                        'name': match.group(-1),  # Last capture group is usually function name
                        'start': i,
                        'end': end_line,
                        'type': 'function'
                    })
                    break
        
        return functions
    
    def _find_classes(self, lines: List[str], content_type: str) -> List[Dict[str, Any]]:
        """Find class boundaries in code."""
        classes = []
        
        lang = self._get_language_from_content_type(content_type)
        class_patterns = [
            r'^\s*class\s+(\w+)',
            r'^\s*(public|private|protected)?\s*class\s+(\w+)'
        ]
        
        for i, line in enumerate(lines):
            for pattern in class_patterns:
                match = re.match(pattern, line)
                if match:
                    end_line = self._find_block_end(lines, i, lang)
                    classes.append({
                        'name': match.group(-1),
                        'start': i,
                        'end': end_line,
                        'type': 'class'
                    })
                    break
        
        return classes
    
    def _find_sections(self, lines: List[str], content_type: str) -> List[Dict[str, Any]]:
        """Find logical sections (e.g., markdown headers)."""
        sections = []
        
        if content_type == 'markdown':
            current_section = None
            
            for i, line in enumerate(lines):
                header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
                if header_match:
                    # End previous section
                    if current_section:
                        current_section['end'] = i
                        sections.append(current_section)
                    
                    # Start new section
                    current_section = {
                        'name': header_match.group(2),
                        'level': len(header_match.group(1)),
                        'start': i,
                        'end': len(lines)  # Will be updated when next section starts
                    }
            
            # Add final section
            if current_section:
                sections.append(current_section)
        
        return sections
    
    def _find_block_end(self, lines: List[str], start_line: int, language: str) -> int:
        """Find the end of a code block (function, class, etc.)."""
        if language == 'python':
            return self._find_python_block_end(lines, start_line)
        else:
            return self._find_brace_block_end(lines, start_line)
    
    def _find_python_block_end(self, lines: List[str], start_line: int) -> int:
        """Find end of Python block based on indentation."""
        if start_line >= len(lines):
            return len(lines)
        
        start_line_content = lines[start_line].lstrip()
        base_indent = len(lines[start_line]) - len(start_line_content)
        
        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            if line.strip():  # Skip empty lines
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= base_indent:
                    return i
        
        return len(lines)
    
    def _find_brace_block_end(self, lines: List[str], start_line: int) -> int:
        """Find end of block based on braces."""
        brace_count = 0
        found_opening = False
        
        for i in range(start_line, len(lines)):
            line = lines[i]
            for char in line:
                if char == '{':
                    brace_count += 1
                    found_opening = True
                elif char == '}':
                    brace_count -= 1
                    if found_opening and brace_count == 0:
                        return i + 1
        
        return len(lines)
    
    def _get_language_from_content_type(self, content_type: str) -> str:
        """Get programming language identifier from content type."""
        # This is a simplified mapping - could be enhanced
        return 'python'  # Default to Python for now
    
    def _combine_functions(self, functions: List[Dict[str, Any]], lines: List[str]) -> str:
        """Combine multiple functions into a single content block."""
        combined_lines = []
        
        for func_info in functions:
            func_lines = lines[func_info['start']:func_info['end']]
            combined_lines.extend(func_lines)
            combined_lines.append('')  # Add separator
        
        return '\n'.join(combined_lines)
    
    def _combine_sections(self, sections: List[Dict[str, Any]], lines: List[str]) -> str:
        """Combine multiple sections into a single content block."""
        combined_lines = []
        
        for section_info in sections:
            section_lines = lines[section_info['start']:section_info['end']]
            combined_lines.extend(section_lines)
        
        return '\n'.join(combined_lines)
    
    def _create_chunk(
        self,
        content: str,
        file_path: str,
        start_line: int,
        end_line: int,
        token_count: int,
        content_type: str,
        strategy: ChunkStrategy
    ) -> FileChunk:
        """Create a FileChunk with metadata."""
        self.chunk_counter += 1
        
        metadata = ChunkMetadata(
            chunk_id=f"chunk_{self.chunk_counter:04d}",
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            token_count=token_count,
            content_type=content_type,
            chunk_strategy=strategy
        )
        
        return FileChunk(content=content, metadata=metadata)
