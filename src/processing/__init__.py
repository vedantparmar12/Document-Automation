"""
Background processing and concurrent analysis module.

This module provides background task processing, concurrent file analysis,
and progress tracking for large codebase operations.
"""

from .background_processor import BackgroundProcessor, TaskStatus, AnalysisTask
from .concurrent_analyzer import ConcurrentAnalyzer, AnalysisResult
from .task_queue import TaskQueue, TaskPriority
from .progress_tracker import ProgressTracker, ProgressEvent

__all__ = [
    'BackgroundProcessor',
    'TaskStatus', 
    'AnalysisTask',
    'ConcurrentAnalyzer',
    'AnalysisResult',
    'TaskQueue',
    'TaskPriority',
    'ProgressTracker',
    'ProgressEvent'
]
