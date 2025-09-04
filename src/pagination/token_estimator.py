"""
Token estimation for LLM context window management.

This module provides utilities for estimating token counts to ensure responses
stay within LLM context limits.
"""

import re
import logging
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Supported LLM model types with different tokenization characteristics."""
    GPT_3_5 = "gpt-3.5"
    GPT_4 = "gpt-4"
    CLAUDE = "claude"
    GENERIC = "generic"


@dataclass
class TokenLimits:
    """Token limits for different contexts."""
    max_input_tokens: int
    max_output_tokens: int
    safety_margin: int = 500  # Buffer to prevent hitting exact limits
    
    @property
    def safe_input_limit(self) -> int:
        return self.max_input_tokens - self.safety_margin


class TokenEstimator:
    """
    Estimates token counts for different types of content and models.
    
    Uses approximation algorithms that are fast but reasonably accurate
    for chunking decisions.
    """
    
    # Token estimation ratios for different content types
    CONTENT_RATIOS = {
        'code': 3.2,      # Code has more special characters
        'markdown': 3.8,   # Markdown has formatting symbols
        'plain_text': 4.0, # Plain text is most efficient
        'json': 3.0,      # JSON is dense with symbols
        'yaml': 3.5,      # YAML has structure but readable
        'xml': 2.8,       # XML has lots of tags
    }
    
    # Model-specific token limits
    MODEL_LIMITS = {
        ModelType.GPT_3_5: TokenLimits(4096, 4096),
        ModelType.GPT_4: TokenLimits(8192, 8192),
        ModelType.CLAUDE: TokenLimits(100000, 4096),
        ModelType.GENERIC: TokenLimits(4000, 1000),
    }
    
    def __init__(self, model_type: ModelType = ModelType.GENERIC):
        self.model_type = model_type
        self.token_limits = self.MODEL_LIMITS[model_type]
        
    def estimate_tokens(
        self, 
        content: str, 
        content_type: str = 'plain_text'
    ) -> int:
        """
        Estimate token count for given content.
        
        Args:
            content: The text content to estimate
            content_type: Type of content ('code', 'markdown', etc.)
            
        Returns:
            Estimated token count
        """
        if not content:
            return 0
            
        # Get the appropriate ratio for content type
        ratio = self.CONTENT_RATIOS.get(content_type, 4.0)
        
        # Basic character count
        char_count = len(content)
        
        # Adjust for special characters and formatting
        special_chars = len(re.findall(r'[{}()\[\];,."\'`\-_=+*&^%$#@!~<>/?\\|]', content))
        whitespace = len(re.findall(r'\s', content))
        
        # Calculate base tokens
        base_tokens = char_count / ratio
        
        # Add penalties for special characters (they often become separate tokens)
        special_penalty = special_chars * 0.3
        
        # Whitespace is usually merged with adjacent tokens
        whitespace_bonus = whitespace * 0.1
        
        estimated = int(base_tokens + special_penalty - whitespace_bonus)
        
        # Ensure minimum of 1 token for non-empty content
        return max(1, estimated)
    
    def estimate_tokens_by_lines(
        self, 
        lines: List[str], 
        content_type: str = 'code'
    ) -> List[int]:
        """
        Estimate tokens for each line in a list.
        
        Args:
            lines: List of text lines
            content_type: Type of content
            
        Returns:
            List of token counts for each line
        """
        return [self.estimate_tokens(line, content_type) for line in lines]
    
    def can_fit_in_context(
        self, 
        content: Union[str, List[str]], 
        content_type: str = 'plain_text',
        reserve_tokens: int = 0
    ) -> bool:
        """
        Check if content fits within model's context window.
        
        Args:
            content: Content to check (string or list of strings)
            content_type: Type of content
            reserve_tokens: Additional tokens to reserve (e.g., for prompts)
            
        Returns:
            True if content fits, False otherwise
        """
        if isinstance(content, list):
            total_tokens = sum(self.estimate_tokens(item, content_type) for item in content)
        else:
            total_tokens = self.estimate_tokens(content, content_type)
        
        available_tokens = self.token_limits.safe_input_limit - reserve_tokens
        return total_tokens <= available_tokens
    
    def get_max_chunk_size(
        self, 
        content_type: str = 'code',
        reserve_tokens: int = 1000
    ) -> int:
        """
        Get maximum characters that can fit in a chunk.
        
        Args:
            content_type: Type of content
            reserve_tokens: Tokens to reserve for prompts/overhead
            
        Returns:
            Maximum characters per chunk
        """
        available_tokens = self.token_limits.safe_input_limit - reserve_tokens
        ratio = self.CONTENT_RATIOS.get(content_type, 4.0)
        
        # Conservative estimate
        max_chars = int(available_tokens * ratio * 0.8)  # 20% safety buffer
        return max(1000, max_chars)  # Minimum reasonable chunk size
    
    def split_by_token_limit(
        self,
        content: str,
        content_type: str = 'code',
        max_tokens_per_chunk: Optional[int] = None,
        overlap_tokens: int = 100
    ) -> List[str]:
        """
        Split content into chunks based on token limits.
        
        Args:
            content: Content to split
            content_type: Type of content
            max_tokens_per_chunk: Maximum tokens per chunk (uses model limit if None)
            overlap_tokens: Tokens to overlap between chunks for context
            
        Returns:
            List of content chunks
        """
        if not content:
            return []
        
        if max_tokens_per_chunk is None:
            max_tokens_per_chunk = self.token_limits.safe_input_limit // 2
        
        # If content fits in one chunk, return as-is
        if self.estimate_tokens(content, content_type) <= max_tokens_per_chunk:
            return [content]
        
        chunks = []
        lines = content.split('\n')
        current_chunk = []
        current_tokens = 0
        
        for line in lines:
            line_tokens = self.estimate_tokens(line, content_type)
            
            # If adding this line would exceed limit, start new chunk
            if current_tokens + line_tokens > max_tokens_per_chunk and current_chunk:
                # Add overlap from previous chunk
                chunk_content = '\n'.join(current_chunk)
                chunks.append(chunk_content)
                
                # Start new chunk with overlap
                overlap_lines = self._get_overlap_lines(current_chunk, overlap_tokens, content_type)
                current_chunk = overlap_lines + [line]
                current_tokens = sum(self.estimate_tokens(l, content_type) for l in current_chunk)
            else:
                current_chunk.append(line)
                current_tokens += line_tokens
        
        # Add final chunk
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    
    def _get_overlap_lines(
        self, 
        lines: List[str], 
        overlap_tokens: int,
        content_type: str
    ) -> List[str]:
        """Get lines from end of chunk to use as overlap in next chunk."""
        if not lines:
            return []
        
        overlap_lines = []
        current_tokens = 0
        
        # Work backwards from end of lines
        for line in reversed(lines):
            line_tokens = self.estimate_tokens(line, content_type)
            if current_tokens + line_tokens <= overlap_tokens:
                overlap_lines.insert(0, line)
                current_tokens += line_tokens
            else:
                break
        
        return overlap_lines
    
    def estimate_processing_time(
        self, 
        content_size_chars: int,
        content_type: str = 'code'
    ) -> float:
        """
        Estimate processing time in seconds for given content size.
        
        Args:
            content_size_chars: Size of content in characters
            content_type: Type of content
            
        Returns:
            Estimated processing time in seconds
        """
        # Base processing rate (characters per second)
        base_rate = 10000  # Adjust based on actual performance
        
        # Different content types have different processing complexities
        complexity_multipliers = {
            'code': 1.5,
            'markdown': 1.2,
            'plain_text': 1.0,
            'json': 1.3,
            'yaml': 1.1,
            'xml': 1.4
        }
        
        multiplier = complexity_multipliers.get(content_type, 1.0)
        adjusted_rate = base_rate / multiplier
        
        return content_size_chars / adjusted_rate
    
    def get_chunking_strategy(
        self, 
        total_size: int,
        content_type: str = 'code'
    ) -> Dict[str, Union[int, str]]:
        """
        Recommend chunking strategy based on content size.
        
        Args:
            total_size: Total size in characters
            content_type: Type of content
            
        Returns:
            Dictionary with recommended chunking parameters
        """
        tokens_estimate = self.estimate_tokens('x' * total_size, content_type)
        max_chunk_tokens = self.token_limits.safe_input_limit // 3  # Conservative
        
        if tokens_estimate <= max_chunk_tokens:
            return {
                'strategy': 'single',
                'chunks_needed': 1,
                'max_chunk_size': total_size
            }
        
        chunks_needed = (tokens_estimate + max_chunk_tokens - 1) // max_chunk_tokens
        max_chunk_chars = self.get_max_chunk_size(content_type, reserve_tokens=1000)
        
        return {
            'strategy': 'chunked',
            'chunks_needed': chunks_needed,
            'max_chunk_size': max_chunk_chars,
            'overlap_size': max_chunk_chars // 10,  # 10% overlap
            'estimated_tokens': tokens_estimate
        }


# Singleton instance for global use
default_estimator = TokenEstimator()


def estimate_tokens(content: str, content_type: str = 'plain_text') -> int:
    """Convenience function using default estimator."""
    return default_estimator.estimate_tokens(content, content_type)


def can_fit_in_context(content: str, content_type: str = 'plain_text') -> bool:
    """Convenience function using default estimator."""
    return default_estimator.can_fit_in_context(content, content_type)
