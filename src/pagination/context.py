"""
Context preservation and pagination state management.

This module handles maintaining context between paginated requests and
preserving state for large analysis operations.
"""

import json
import base64
import time
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import hashlib
import os

logger = logging.getLogger(__name__)


@dataclass
class PaginationContext:
    """Context information for paginated requests."""
    session_id: str
    analysis_id: str
    current_file_index: int
    current_chunk_index: int
    total_files: int
    total_chunks: int
    file_path: str
    chunk_strategy: str
    created_at: float
    ttl_minutes: int = 30
    metadata: Optional[Dict[str, Any]] = None
    
    @property
    def is_expired(self) -> bool:
        """Check if context has expired."""
        expiry_time = self.created_at + (self.ttl_minutes * 60)
        return time.time() > expiry_time
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.total_chunks == 0:
            return 100.0
        
        completed_chunks = (self.current_file_index * self.total_chunks) + self.current_chunk_index
        total_chunks = self.total_files * self.total_chunks
        
        return min(100.0, (completed_chunks / total_chunks) * 100)


@dataclass
class AnalysisSession:
    """Session information for long-running analysis operations."""
    session_id: str
    analysis_type: str
    source_path: str
    source_type: str
    started_at: float
    status: str  # 'running', 'completed', 'failed', 'cancelled'
    progress: Dict[str, Any]
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    @property
    def duration_seconds(self) -> float:
        """Get duration in seconds."""
        return time.time() - self.started_at
    
    @property
    def is_running(self) -> bool:
        """Check if analysis is still running."""
        return self.status == 'running'


class ContextManager:
    """
    Manages pagination context and analysis sessions.
    
    Handles encryption/decryption of context tokens and session persistence.
    """
    
    def __init__(self, encryption_key: Optional[bytes] = None):
        """
        Initialize context manager.
        
        Args:
            encryption_key: Key for encrypting context tokens. If None, generates one.
        """
        if encryption_key is None:
            encryption_key = self._generate_key()
        
        self.cipher = Fernet(encryption_key)
        self.contexts: Dict[str, PaginationContext] = {}
        self.sessions: Dict[str, AnalysisSession] = {}
        self._cleanup_interval = 300  # 5 minutes
        self._last_cleanup = time.time()
    
    def _generate_key(self) -> bytes:
        """Generate encryption key from environment or create new one."""
        env_key = os.getenv('PAGINATION_ENCRYPTION_KEY')
        if env_key:
            # Use hash of environment key for consistency
            return base64.urlsafe_b64encode(
                hashlib.sha256(env_key.encode()).digest()
            )
        else:
            # Generate new key (will be different each restart)
            return Fernet.generate_key()
    
    def create_context(
        self,
        analysis_id: str,
        file_path: str,
        total_files: int,
        total_chunks: int,
        chunk_strategy: str,
        current_file_index: int = 0,
        current_chunk_index: int = 0,
        ttl_minutes: int = 30,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaginationContext:
        """
        Create a new pagination context.
        
        Args:
            analysis_id: Unique analysis identifier
            file_path: Current file path
            total_files: Total number of files to process
            total_chunks: Total chunks in current file
            chunk_strategy: Strategy used for chunking
            current_file_index: Current file index (0-based)
            current_chunk_index: Current chunk index (0-based)
            ttl_minutes: Time-to-live in minutes
            metadata: Additional metadata
            
        Returns:
            New PaginationContext
        """
        session_id = self._generate_session_id(analysis_id, file_path)
        
        context = PaginationContext(
            session_id=session_id,
            analysis_id=analysis_id,
            current_file_index=current_file_index,
            current_chunk_index=current_chunk_index,
            total_files=total_files,
            total_chunks=total_chunks,
            file_path=file_path,
            chunk_strategy=chunk_strategy,
            created_at=time.time(),
            ttl_minutes=ttl_minutes,
            metadata=metadata or {}
        )
        
        self.contexts[session_id] = context
        self._cleanup_expired_contexts()
        
        return context
    
    def update_context(
        self,
        session_id: str,
        current_file_index: Optional[int] = None,
        current_chunk_index: Optional[int] = None,
        file_path: Optional[str] = None,
        total_chunks: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[PaginationContext]:
        """
        Update an existing pagination context.
        
        Args:
            session_id: Session identifier
            current_file_index: New file index
            current_chunk_index: New chunk index
            file_path: New file path
            total_chunks: New total chunks
            metadata: Updated metadata
            
        Returns:
            Updated context or None if not found
        """
        context = self.contexts.get(session_id)
        if not context or context.is_expired:
            return None
        
        if current_file_index is not None:
            context.current_file_index = current_file_index
        if current_chunk_index is not None:
            context.current_chunk_index = current_chunk_index
        if file_path is not None:
            context.file_path = file_path
        if total_chunks is not None:
            context.total_chunks = total_chunks
        if metadata is not None:
            context.metadata.update(metadata)
        
        return context
    
    def get_context(self, session_id: str) -> Optional[PaginationContext]:
        """Get context by session ID."""
        context = self.contexts.get(session_id)
        if context and context.is_expired:
            del self.contexts[session_id]
            return None
        return context
    
    def encrypt_context_token(self, context: PaginationContext) -> str:
        """
        Encrypt context into a token string.
        
        Args:
            context: Context to encrypt
            
        Returns:
            Encrypted token string
        """
        context_dict = asdict(context)
        context_json = json.dumps(context_dict, separators=(',', ':'))
        encrypted_bytes = self.cipher.encrypt(context_json.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted_bytes).decode('ascii')
    
    def decrypt_context_token(self, token: str) -> Optional[PaginationContext]:
        """
        Decrypt context from token string.
        
        Args:
            token: Encrypted token string
            
        Returns:
            Decrypted context or None if invalid/expired
        """
        try:
            encrypted_bytes = base64.urlsafe_b64decode(token.encode('ascii'))
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            context_dict = json.loads(decrypted_bytes.decode('utf-8'))
            
            context = PaginationContext(**context_dict)
            
            if context.is_expired:
                logger.warning(f"Context token expired: {context.session_id}")
                return None
            
            # Re-add to contexts if not present
            if context.session_id not in self.contexts:
                self.contexts[context.session_id] = context
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to decrypt context token: {e}")
            return None
    
    def create_session(
        self,
        analysis_type: str,
        source_path: str,
        source_type: str,
        session_id: Optional[str] = None
    ) -> AnalysisSession:
        """
        Create a new analysis session.
        
        Args:
            analysis_type: Type of analysis being performed
            source_path: Path being analyzed
            source_type: Type of source (local/github)
            session_id: Optional session ID (generates if None)
            
        Returns:
            New AnalysisSession
        """
        if session_id is None:
            session_id = self._generate_session_id(analysis_type, source_path)
        
        session = AnalysisSession(
            session_id=session_id,
            analysis_type=analysis_type,
            source_path=source_path,
            source_type=source_type,
            started_at=time.time(),
            status='running',
            progress={
                'files_processed': 0,
                'total_files': 0,
                'current_file': '',
                'percentage': 0.0
            }
        )
        
        self.sessions[session_id] = session
        return session
    
    def update_session(
        self,
        session_id: str,
        status: Optional[str] = None,
        progress: Optional[Dict[str, Any]] = None,
        results: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> Optional[AnalysisSession]:
        """
        Update analysis session.
        
        Args:
            session_id: Session identifier
            status: New status
            progress: Progress update
            results: Analysis results
            error: Error message if failed
            
        Returns:
            Updated session or None if not found
        """
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        if status is not None:
            session.status = status
        if progress is not None:
            session.progress.update(progress)
        if results is not None:
            session.results = results
        if error is not None:
            session.error = error
        
        return session
    
    def get_session(self, session_id: str) -> Optional[AnalysisSession]:
        """Get analysis session by ID."""
        return self.sessions.get(session_id)
    
    def list_active_sessions(self) -> List[AnalysisSession]:
        """Get all active analysis sessions."""
        return [s for s in self.sessions.values() if s.is_running]
    
    def cleanup_session(self, session_id: str) -> bool:
        """Remove session and associated contexts."""
        session_removed = session_id in self.sessions
        if session_removed:
            del self.sessions[session_id]
        
        # Remove associated contexts
        contexts_removed = 0
        for ctx_id in list(self.contexts.keys()):
            context = self.contexts[ctx_id]
            if context.analysis_id == session_id:
                del self.contexts[ctx_id]
                contexts_removed += 1
        
        logger.info(f"Cleaned up session {session_id}: removed session={session_removed}, contexts={contexts_removed}")
        return session_removed
    
    def _generate_session_id(self, *components: str) -> str:
        """Generate unique session ID from components."""
        content = ':'.join(components) + f':{time.time()}'
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _cleanup_expired_contexts(self):
        """Remove expired contexts and old sessions."""
        current_time = time.time()
        
        # Only cleanup periodically to avoid overhead
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        # Remove expired contexts
        expired_contexts = [
            ctx_id for ctx_id, ctx in self.contexts.items() 
            if ctx.is_expired
        ]
        
        for ctx_id in expired_contexts:
            del self.contexts[ctx_id]
        
        # Remove old completed/failed sessions (older than 1 hour)
        old_sessions = [
            session_id for session_id, session in self.sessions.items()
            if not session.is_running and current_time - session.started_at > 3600
        ]
        
        for session_id in old_sessions:
            del self.sessions[session_id]
        
        if expired_contexts or old_sessions:
            logger.info(f"Cleaned up {len(expired_contexts)} expired contexts and {len(old_sessions)} old sessions")
        
        self._last_cleanup = current_time
    
    def get_context_summary(self, context: PaginationContext) -> Dict[str, Any]:
        """Get summary information about pagination context."""
        return {
            'session_id': context.session_id,
            'analysis_id': context.analysis_id,
            'current_position': {
                'file_index': context.current_file_index,
                'chunk_index': context.current_chunk_index,
                'file_path': context.file_path
            },
            'totals': {
                'files': context.total_files,
                'chunks': context.total_chunks
            },
            'progress': {
                'percentage': context.progress_percentage,
                'files_remaining': context.total_files - context.current_file_index,
                'chunks_remaining': context.total_chunks - context.current_chunk_index
            },
            'timing': {
                'created_at': datetime.fromtimestamp(context.created_at).isoformat(),
                'expires_at': datetime.fromtimestamp(
                    context.created_at + context.ttl_minutes * 60
                ).isoformat(),
                'time_remaining_minutes': max(0, context.ttl_minutes - (time.time() - context.created_at) / 60)
            },
            'strategy': context.chunk_strategy,
            'metadata': context.metadata
        }


# Global context manager instance
_context_manager: Optional[ContextManager] = None


def get_context_manager() -> ContextManager:
    """Get global context manager instance."""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager


def create_context_token(context: PaginationContext) -> str:
    """Convenience function to create context token."""
    return get_context_manager().encrypt_context_token(context)


def get_context_from_token(token: str) -> Optional[PaginationContext]:
    """Convenience function to get context from token."""
    return get_context_manager().decrypt_context_token(token)
