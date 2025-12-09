"""
Background task management utilities
"""

import asyncio
import uuid
from typing import Any, Dict, Optional
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enum"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskInfo:
    """
    Information about a background task
    """

    def __init__(self, task_id: str, task_type: str):
        self.task_id = task_id
        self.task_type = task_type
        self.status = TaskStatus.PENDING
        self.progress = 0.0
        self.message = "Task initialized"
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None


class TaskManager:
    """
    Manages background tasks
    """

    def __init__(self):
        # Store task information by task ID
        self.tasks: Dict[str, TaskInfo] = {}
        # Store asyncio tasks for cancellation
        self.running_tasks: Dict[str, asyncio.Task] = {}

    def create_task(self, task_type: str, task_id: Optional[str] = None) -> str:
        """
        Create a new task

        Args:
            task_type: Type of task (evaluation, analysis, etc.)
            task_id: Optional custom task ID

        Returns:
            str: Task ID
        """
        if task_id is None:
            task_id = str(uuid.uuid4())

        task_info = TaskInfo(task_id, task_type)
        self.tasks[task_id] = task_info

        return task_id

    def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """
        Get task information

        Args:
            task_id: Task ID

        Returns:
            TaskInfo or None
        """
        return self.tasks.get(task_id)

    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        progress: Optional[float] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
    ):
        """
        Update task status

        Args:
            task_id: Task ID
            status: New status
            progress: Progress percentage (0-100)
            message: Status message
            error: Error message if failed
        """
        task = self.tasks.get(task_id)
        if not task:
            return

        task.status = status

        if progress is not None:
            task.progress = progress

        if message is not None:
            task.message = message

        if error is not None:
            task.error = error

        # Update timestamps
        if status == TaskStatus.RUNNING and task.started_at is None:
            task.started_at = datetime.now()

        if status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            task.completed_at = datetime.now()

    def set_task_result(self, task_id: str, result: Any):
        """
        Set task result

        Args:
            task_id: Task ID
            result: Task result
        """
        task = self.tasks.get(task_id)
        if task:
            task.result = result

    def register_running_task(self, task_id: str, asyncio_task: asyncio.Task):
        """
        Register an asyncio task for later cancellation

        Args:
            task_id: Task ID
            asyncio_task: Asyncio task
        """
        self.running_tasks[task_id] = asyncio_task

    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running task

        Args:
            task_id: Task ID

        Returns:
            bool: True if cancelled, False if not found or already finished
        """
        if task_id not in self.running_tasks:
            return False

        asyncio_task = self.running_tasks[task_id]

        if not asyncio_task.done():
            asyncio_task.cancel()
            self.update_task_status(task_id, TaskStatus.CANCELLED, message="Task cancelled by user")
            return True

        return False

    def cleanup_task(self, task_id: str):
        """
        Clean up task after completion

        Args:
            task_id: Task ID
        """
        if task_id in self.running_tasks:
            del self.running_tasks[task_id]


# Global task manager instance
task_manager = TaskManager()
