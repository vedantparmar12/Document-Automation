"""
Background task processor for long-running analysis operations.

This module handles queuing, executing, and monitoring background tasks
for codebase analysis operations that might take significant time.
"""

import asyncio
import logging
import time
import traceback
from typing import Dict, List, Any, Optional, Callable, Awaitable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status of background tasks."""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class TaskPriority(Enum):
    """Priority levels for tasks."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class TaskResult:
    """Result of a completed task."""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0
    memory_usage: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'task_id': self.task_id,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'error_details': self.error_details,
            'execution_time': self.execution_time,
            'memory_usage': self.memory_usage
        }


@dataclass
class AnalysisTask:
    """Background analysis task definition."""
    task_id: str
    task_type: str
    parameters: Dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    status: TaskStatus = TaskStatus.PENDING
    progress: Dict[str, Any] = field(default_factory=dict)
    result: Optional[TaskResult] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: Optional[float] = None
    callback: Optional[Callable[[TaskResult], Awaitable[None]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def execution_time(self) -> float:
        """Get execution time in seconds."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        elif self.started_at:
            return time.time() - self.started_at
        return 0.0
    
    @property
    def total_time(self) -> float:
        """Get total time since creation."""
        if self.completed_at:
            return self.completed_at - self.created_at
        return time.time() - self.created_at
    
    @property
    def is_terminal_state(self) -> bool:
        """Check if task is in a terminal state."""
        return self.status in {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED}
    
    def update_progress(self, **kwargs) -> None:
        """Update task progress."""
        self.progress.update(kwargs)
        self.progress['updated_at'] = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'task_id': self.task_id,
            'task_type': self.task_type,
            'parameters': self.parameters,
            'priority': self.priority.value,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'status': self.status.value,
            'progress': self.progress,
            'result': self.result.to_dict() if self.result else None,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'timeout_seconds': self.timeout_seconds,
            'execution_time': self.execution_time,
            'total_time': self.total_time,
            'metadata': self.metadata
        }


class BackgroundProcessor:
    """
    Background processor for long-running analysis tasks.
    
    Manages task queues, worker threads, and progress tracking for
    operations that exceed typical request timeouts.
    """
    
    def __init__(
        self,
        max_concurrent_tasks: int = 4,
        max_queue_size: int = 100,
        cleanup_interval: int = 3600,  # 1 hour
        task_timeout: float = 1800,    # 30 minutes default
    ):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.max_queue_size = max_queue_size
        self.cleanup_interval = cleanup_interval
        self.task_timeout = task_timeout
        
        # Task storage
        self.tasks: Dict[str, AnalysisTask] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        
        # Worker management
        self.workers: List[asyncio.Task] = []
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_tasks)
        self.running = False
        self.lock = asyncio.Lock()
        
        # Progress tracking
        self.progress_callbacks: Dict[str, List[Callable]] = {}
        
        # Cleanup
        self.last_cleanup = time.time()
        
        # Task handlers
        self.task_handlers: Dict[str, Callable] = {}
        
        # Stats
        self.stats = {
            'tasks_created': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'tasks_cancelled': 0,
            'total_execution_time': 0.0
        }
    
    def register_task_handler(
        self, 
        task_type: str, 
        handler: Callable[[AnalysisTask], Awaitable[Any]]
    ) -> None:
        """
        Register a handler for a specific task type.
        
        Args:
            task_type: Type of task to handle
            handler: Async function that processes the task
        """
        self.task_handlers[task_type] = handler
        logger.info(f"Registered handler for task type: {task_type}")
    
    async def start(self) -> None:
        """Start the background processor."""
        if self.running:
            logger.warning("Background processor already running")
            return
        
        self.running = True
        logger.info(f"Starting background processor with {self.max_concurrent_tasks} workers")
        
        # Start worker tasks
        for i in range(self.max_concurrent_tasks):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
        
        # Start cleanup task
        cleanup_task = asyncio.create_task(self._cleanup_worker())
        self.workers.append(cleanup_task)
        
        logger.info("Background processor started successfully")
    
    async def stop(self, timeout: float = 30.0) -> None:
        """Stop the background processor."""
        if not self.running:
            return
        
        logger.info("Stopping background processor...")
        self.running = False
        
        # Cancel all workers
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to finish
        try:
            await asyncio.wait_for(
                asyncio.gather(*self.workers, return_exceptions=True),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning("Workers did not stop within timeout")
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        # Cancel pending tasks
        pending_tasks = [task for task in self.tasks.values() if task.status == TaskStatus.PENDING]
        for task in pending_tasks:
            await self.cancel_task(task.task_id)
        
        logger.info("Background processor stopped")
    
    async def submit_task(
        self,
        task_type: str,
        parameters: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout_seconds: Optional[float] = None,
        callback: Optional[Callable[[TaskResult], Awaitable[None]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None
    ) -> str:
        """
        Submit a task for background processing.
        
        Args:
            task_type: Type of task to execute
            parameters: Parameters for the task
            priority: Task priority
            timeout_seconds: Task-specific timeout
            callback: Optional callback for completion
            metadata: Additional task metadata
            task_id: Optional custom task ID
            
        Returns:
            Task ID
        """
        if not self.running:
            raise RuntimeError("Background processor not running")
        
        if task_type not in self.task_handlers:
            raise ValueError(f"No handler registered for task type: {task_type}")
        
        if task_id is None:
            task_id = str(uuid.uuid4())
        
        # Check queue capacity
        if self.task_queue.qsize() >= self.max_queue_size:
            raise RuntimeError("Task queue is full")
        
        # Create task
        task = AnalysisTask(
            task_id=task_id,
            task_type=task_type,
            parameters=parameters,
            priority=priority,
            timeout_seconds=timeout_seconds or self.task_timeout,
            callback=callback,
            metadata=metadata or {}
        )
        
        async with self.lock:
            self.tasks[task_id] = task
            await self.task_queue.put(task)
            self.stats['tasks_created'] += 1
        
        logger.info(f"Submitted task {task_id} of type {task_type}")
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task."""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        return task.to_dict()
    
    async def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get result of a completed task."""
        task = self.tasks.get(task_id)
        if not task or not task.result:
            return None
        
        return task.result
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task."""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        if task.is_terminal_state:
            return False
        
        async with self.lock:
            task.status = TaskStatus.CANCELLED
            task.completed_at = time.time()
            self.stats['tasks_cancelled'] += 1
        
        logger.info(f"Cancelled task {task_id}")
        return True
    
    async def list_tasks(
        self, 
        status_filter: Optional[TaskStatus] = None,
        task_type_filter: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List tasks with optional filtering."""
        tasks = list(self.tasks.values())
        
        # Apply filters
        if status_filter:
            tasks = [t for t in tasks if t.status == status_filter]
        
        if task_type_filter:
            tasks = [t for t in tasks if t.task_type == task_type_filter]
        
        # Sort by creation time (newest first)
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        # Apply limit
        if limit:
            tasks = tasks[:limit]
        
        return [task.to_dict() for task in tasks]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get processor statistics."""
        running_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.RUNNING])
        pending_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING])
        
        return {
            **self.stats,
            'running_tasks': running_tasks,
            'pending_tasks': pending_tasks,
            'total_tasks': len(self.tasks),
            'queue_size': self.task_queue.qsize(),
            'workers': len(self.workers) - 1,  # Exclude cleanup worker
            'uptime_seconds': time.time() - (self.stats.get('start_time', time.time()))
        }
    
    def add_progress_callback(
        self, 
        task_id: str, 
        callback: Callable[[str, Dict[str, Any]], None]
    ) -> None:
        """Add progress callback for a task."""
        if task_id not in self.progress_callbacks:
            self.progress_callbacks[task_id] = []
        self.progress_callbacks[task_id].append(callback)
    
    async def _worker(self, worker_name: str) -> None:
        """Worker coroutine that processes tasks."""
        logger.info(f"Worker {worker_name} started")
        
        while self.running:
            try:
                # Get next task (with timeout to check running flag)
                try:
                    task = await asyncio.wait_for(
                        self.task_queue.get(), 
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Execute task
                await self._execute_task(task, worker_name)
                
            except asyncio.CancelledError:
                logger.info(f"Worker {worker_name} cancelled")
                break
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
                logger.debug(traceback.format_exc())
        
        logger.info(f"Worker {worker_name} stopped")
    
    async def _execute_task(self, task: AnalysisTask, worker_name: str) -> None:
        """Execute a single task."""
        logger.info(f"Worker {worker_name} executing task {task.task_id}")
        
        # Update task status
        async with self.lock:
            task.status = TaskStatus.RUNNING
            task.started_at = time.time()
        
        try:
            # Get handler
            handler = self.task_handlers[task.task_type]
            
            # Execute with timeout
            if task.timeout_seconds:
                result = await asyncio.wait_for(
                    handler(task),
                    timeout=task.timeout_seconds
                )
            else:
                result = await handler(task)
            
            # Create success result
            task_result = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                result=result,
                execution_time=task.execution_time
            )
            
            async with self.lock:
                task.status = TaskStatus.COMPLETED
                task.completed_at = time.time()
                task.result = task_result
                self.stats['tasks_completed'] += 1
                self.stats['total_execution_time'] += task.execution_time
            
            logger.info(f"Task {task.task_id} completed successfully")
            
        except asyncio.TimeoutError:
            error_msg = f"Task timed out after {task.timeout_seconds} seconds"
            await self._handle_task_error(task, error_msg, {
                'error_type': 'timeout',
                'timeout_seconds': task.timeout_seconds
            })
            
        except Exception as e:
            error_msg = f"Task execution failed: {str(e)}"
            await self._handle_task_error(task, error_msg, {
                'error_type': type(e).__name__,
                'traceback': traceback.format_exc()
            })
        
        # Execute callback if provided
        if task.callback and task.result:
            try:
                await task.callback(task.result)
            except Exception as e:
                logger.error(f"Task callback failed for {task.task_id}: {e}")
        
        # Notify progress callbacks
        await self._notify_progress_callbacks(task)
    
    async def _handle_task_error(
        self, 
        task: AnalysisTask, 
        error_msg: str,
        error_details: Dict[str, Any]
    ) -> None:
        """Handle task execution error."""
        logger.error(f"Task {task.task_id} failed: {error_msg}")
        
        task_result = TaskResult(
            task_id=task.task_id,
            status=TaskStatus.FAILED,
            error=error_msg,
            error_details=error_details,
            execution_time=task.execution_time
        )
        
        async with self.lock:
            task.status = TaskStatus.FAILED
            task.completed_at = time.time()
            task.result = task_result
            self.stats['tasks_failed'] += 1
        
        # Check if should retry
        if task.retry_count < task.max_retries:
            logger.info(f"Retrying task {task.task_id} (attempt {task.retry_count + 1})")
            task.retry_count += 1
            task.status = TaskStatus.PENDING
            task.started_at = None
            task.completed_at = None
            
            # Re-queue for retry
            await self.task_queue.put(task)
    
    async def _notify_progress_callbacks(self, task: AnalysisTask) -> None:
        """Notify progress callbacks for a task."""
        callbacks = self.progress_callbacks.get(task.task_id, [])
        for callback in callbacks:
            try:
                callback(task.task_id, task.progress)
            except Exception as e:
                logger.error(f"Progress callback failed for {task.task_id}: {e}")
    
    async def _cleanup_worker(self) -> None:
        """Cleanup worker that removes old completed tasks."""
        logger.info("Cleanup worker started")
        
        while self.running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_old_tasks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup worker error: {e}")
        
        logger.info("Cleanup worker stopped")
    
    async def _cleanup_old_tasks(self) -> None:
        """Remove old completed/failed tasks."""
        current_time = time.time()
        cutoff_time = current_time - (24 * 3600)  # 24 hours
        
        to_remove = []
        for task_id, task in self.tasks.items():
            if (task.is_terminal_state and 
                task.completed_at and 
                task.completed_at < cutoff_time):
                to_remove.append(task_id)
        
        async with self.lock:
            for task_id in to_remove:
                del self.tasks[task_id]
                # Clean up progress callbacks
                self.progress_callbacks.pop(task_id, None)
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old tasks")


# Global processor instance
_processor: Optional[BackgroundProcessor] = None


def get_background_processor() -> BackgroundProcessor:
    """Get global background processor instance."""
    global _processor
    if _processor is None:
        _processor = BackgroundProcessor()
    return _processor


async def submit_analysis_task(
    task_type: str,
    parameters: Dict[str, Any],
    **kwargs
) -> str:
    """Convenience function to submit analysis task."""
    processor = get_background_processor()
    return await processor.submit_task(task_type, parameters, **kwargs)
