"""Parallel - Parallel task execution for brain workflows."""

from __future__ import annotations

import uuid
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class TaskStatus(str, Enum):
    """Status of a parallel task."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """A task to be executed in parallel."""
    task_id: str
    skill: str
    instruction: str
    context: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    timeout: float = 60.0
    wait: bool = True

    # Execution state
    status: TaskStatus = TaskStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None

    # Merge configuration
    merge_to: Optional[str] = None
    on_complete: Optional[str] = None
    on_fail: str = "log_and_continue"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "skill": self.skill,
            "instruction": self.instruction,
            "context": self.context,
            "priority": self.priority,
            "timeout": self.timeout,
            "wait": self.wait,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
            "merge_to": self.merge_to,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Task:
        return cls(
            task_id=data.get("task_id", str(uuid.uuid4())),
            skill=data.get("skill", ""),
            instruction=data.get("instruction", ""),
            context=data.get("context", {}),
            priority=data.get("priority", 1),
            timeout=data.get("timeout", 60.0),
            wait=data.get("wait", True),
            status=TaskStatus(data.get("status", "pending")),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            result=data.get("result"),
            error=data.get("error"),
            merge_to=data.get("merge_to"),
        )


@dataclass
class TaskResult:
    """Result of a parallel task execution."""
    task_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    duration_seconds: float = 0.0


class ParallelExecutor:
    """
    Executor for parallel tasks in brain workflows.

    Supports:
    - Concurrent skill execution
    - Result merging
    - Timeout handling
    - Priority-based scheduling
    """

    def __init__(
        self,
        skill_executor: Callable[[str, str, Dict[str, Any]], Dict[str, Any]],
        max_workers: int = 5,
    ):
        self.skill_executor = skill_executor
        self.max_workers = max_workers
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def execute_tasks(
        self,
        tasks: List[Task],
        wait_for_all: bool = True,
        timeout: Optional[float] = None,
    ) -> List[TaskResult]:
        """
        Execute multiple tasks in parallel.

        Args:
            tasks: List of tasks to execute
            wait_for_all: If True, wait for all tasks to complete
            timeout: Overall timeout for all tasks

        Returns:
            List of task results
        """
        # Sort by priority (lower number = higher priority)
        sorted_tasks = sorted(tasks, key=lambda t: t.priority)

        # Submit all tasks
        futures = {}
        for task in sorted_tasks:
            future = self._executor.submit(self._execute_single, task)
            futures[future] = task

        # Collect results
        results = []
        completed_count = 0

        try:
            for future in as_completed(futures, timeout=timeout):
                task = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    completed_count += 1
                except Exception as e:
                    results.append(TaskResult(
                        task_id=task.task_id,
                        success=False,
                        error=str(e),
                    ))
                    completed_count += 1

                # If not waiting for all, return as soon as blocking tasks complete
                if not wait_for_all:
                    blocking_tasks = [t for t in sorted_tasks if t.wait]
                    blocking_completed = sum(
                        1 for r in results
                        if r.task_id in [t.task_id for t in blocking_tasks]
                    )
                    if blocking_completed >= len(blocking_tasks):
                        break

        except TimeoutError:
            # Add timeout results for incomplete tasks
            for future, task in futures.items():
                if not future.done():
                    future.cancel()
                    results.append(TaskResult(
                        task_id=task.task_id,
                        success=False,
                        error="Task timed out",
                    ))

        return results

    def _execute_single(self, task: Task) -> TaskResult:
        """Execute a single task."""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        start_time = datetime.utcnow()

        try:
            # Execute the skill
            result = self.skill_executor(
                task.skill,
                task.instruction,
                task.context,
            )

            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = result

            duration = (task.completed_at - start_time).total_seconds()

            return TaskResult(
                task_id=task.task_id,
                success=True,
                result=result,
                duration_seconds=duration,
            )

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            task.error = str(e)

            duration = (task.completed_at - start_time).total_seconds()

            return TaskResult(
                task_id=task.task_id,
                success=False,
                error=str(e),
                duration_seconds=duration,
            )

    def execute_single(self, task: Task) -> TaskResult:
        """Execute a single task synchronously."""
        return self._execute_single(task)

    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the executor."""
        self._executor.shutdown(wait=wait)


def merge_results(
    results: List[TaskResult],
    strategy: str = "collect"
) -> Dict[str, Any]:
    """
    Merge parallel task results.

    Strategies:
    - collect: Collect all results into a list
    - merge_dicts: Merge all dict results
    - first_success: Use first successful result
    - best_confidence: Use result with highest confidence
    """
    if strategy == "collect":
        return {
            "results": [r.result for r in results if r.success],
            "errors": [{"task_id": r.task_id, "error": r.error} for r in results if not r.success],
            "success_count": sum(1 for r in results if r.success),
            "failure_count": sum(1 for r in results if not r.success),
        }

    elif strategy == "merge_dicts":
        merged = {}
        for result in results:
            if result.success and isinstance(result.result, dict):
                merged.update(result.result)
        return merged

    elif strategy == "first_success":
        for result in results:
            if result.success:
                return {"result": result.result}
        return {"error": "No successful results"}

    elif strategy == "best_confidence":
        best = None
        best_confidence = -1
        for result in results:
            if result.success and isinstance(result.result, dict):
                confidence = result.result.get("confidence", 0)
                if confidence > best_confidence:
                    best = result.result
                    best_confidence = confidence
        return {"result": best} if best else {"error": "No results with confidence"}

    else:
        return {"results": [r.result for r in results]}


class AsyncParallelExecutor:
    """
    Async version of parallel executor for use in async contexts.
    """

    def __init__(
        self,
        skill_executor: Callable[[str, str, Dict[str, Any]], Dict[str, Any]],
        max_concurrent: int = 5,
    ):
        self.skill_executor = skill_executor
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def execute_tasks(
        self,
        tasks: List[Task],
        timeout: Optional[float] = None,
    ) -> List[TaskResult]:
        """Execute tasks concurrently using asyncio."""

        async def execute_with_semaphore(task: Task) -> TaskResult:
            async with self._semaphore:
                return await self._execute_single_async(task)

        # Create coroutines for all tasks
        coroutines = [execute_with_semaphore(task) for task in tasks]

        # Execute with optional timeout
        if timeout:
            try:
                results = await asyncio.wait_for(
                    asyncio.gather(*coroutines, return_exceptions=True),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                results = [
                    TaskResult(task_id=t.task_id, success=False, error="Timeout")
                    for t in tasks
                ]
        else:
            results = await asyncio.gather(*coroutines, return_exceptions=True)

        # Convert exceptions to TaskResults
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(TaskResult(
                    task_id=tasks[i].task_id,
                    success=False,
                    error=str(result),
                ))
            elif isinstance(result, TaskResult):
                final_results.append(result)
            else:
                final_results.append(TaskResult(
                    task_id=tasks[i].task_id,
                    success=True,
                    result=result,
                ))

        return final_results

    async def _execute_single_async(self, task: Task) -> TaskResult:
        """Execute a single task asynchronously."""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        start_time = datetime.utcnow()

        try:
            # Run skill executor in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.skill_executor,
                task.skill,
                task.instruction,
                task.context,
            )

            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = result

            duration = (task.completed_at - start_time).total_seconds()

            return TaskResult(
                task_id=task.task_id,
                success=True,
                result=result,
                duration_seconds=duration,
            )

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            task.error = str(e)

            duration = (task.completed_at - start_time).total_seconds()

            return TaskResult(
                task_id=task.task_id,
                success=False,
                error=str(e),
                duration_seconds=duration,
            )
