"""State - Runtime state management for brain execution."""

from __future__ import annotations

import json
import uuid
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from copy import deepcopy

from .graph import Stage


@dataclass
class AuditEvent:
    """An event in the audit trail."""
    timestamp: datetime
    node_id: str
    stage: str
    action: str
    summary: str
    signals: Dict[str, Any] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ts": self.timestamp.isoformat(),
            "node_id": self.node_id,
            "stage": self.stage,
            "action": self.action,
            "summary": self.summary,
            "signals": self.signals,
            "details": self.details,
        }


@dataclass
class Counters:
    """Counters for loop control and statistics."""
    total_steps: int = 0
    node_visits: Dict[str, int] = field(default_factory=dict)
    retries: Dict[str, int] = field(default_factory=dict)
    total_retries: int = 0
    memory_writes: int = 0
    parallel_tasks_spawned: int = 0
    parallel_tasks_completed: int = 0
    skills_invoked: int = 0

    def visit_node(self, node_id: str) -> int:
        """Record a node visit, return visit count."""
        self.total_steps += 1
        current = self.node_visits.get(node_id, 0)
        self.node_visits[node_id] = current + 1
        return current + 1

    def add_retry(self, edge_id: str) -> int:
        """Record a retry on an edge, return retry count."""
        current = self.retries.get(edge_id, 0)
        self.retries[edge_id] = current + 1
        self.total_retries += 1
        return current + 1

    def get_retries(self, edge_id: str) -> int:
        """Get current retry count for an edge."""
        return self.retries.get(edge_id, 0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_steps": self.total_steps,
            "node_visits": self.node_visits,
            "retries": self.retries,
            "total_retries": self.total_retries,
            "memory_writes": self.memory_writes,
            "parallel_tasks_spawned": self.parallel_tasks_spawned,
            "parallel_tasks_completed": self.parallel_tasks_completed,
            "skills_invoked": self.skills_invoked,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Counters:
        return cls(
            total_steps=data.get("total_steps", 0),
            node_visits=data.get("node_visits", {}),
            retries=data.get("retries", {}),
            total_retries=data.get("total_retries", 0),
            memory_writes=data.get("memory_writes", 0),
            parallel_tasks_spawned=data.get("parallel_tasks_spawned", 0),
            parallel_tasks_completed=data.get("parallel_tasks_completed", 0),
            skills_invoked=data.get("skills_invoked", 0),
        )


@dataclass
class ParallelTask:
    """A parallel task being tracked."""
    task_id: str
    skill: str
    instruction: str
    status: str = "pending"  # pending, running, completed, failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class ParallelState:
    """State for parallel task tracking."""
    active_tasks: List[ParallelTask] = field(default_factory=list)
    completed_tasks: List[ParallelTask] = field(default_factory=list)
    failed_tasks: List[ParallelTask] = field(default_factory=list)

    def spawn_task(self, task_id: str, skill: str, instruction: str) -> ParallelTask:
        """Create and track a new parallel task."""
        task = ParallelTask(
            task_id=task_id,
            skill=skill,
            instruction=instruction,
            status="pending",
        )
        self.active_tasks.append(task)
        return task

    def start_task(self, task_id: str) -> None:
        """Mark a task as started."""
        for task in self.active_tasks:
            if task.task_id == task_id:
                task.status = "running"
                task.started_at = datetime.utcnow()
                break

    def complete_task(self, task_id: str, result: Any) -> None:
        """Mark a task as completed."""
        for i, task in enumerate(self.active_tasks):
            if task.task_id == task_id:
                task.status = "completed"
                task.completed_at = datetime.utcnow()
                task.result = result
                self.completed_tasks.append(task)
                self.active_tasks.pop(i)
                break

    def fail_task(self, task_id: str, error: str) -> None:
        """Mark a task as failed."""
        for i, task in enumerate(self.active_tasks):
            if task.task_id == task_id:
                task.status = "failed"
                task.completed_at = datetime.utcnow()
                task.error = error
                self.failed_tasks.append(task)
                self.active_tasks.pop(i)
                break

    def has_active(self) -> bool:
        """Check if there are active tasks."""
        return len(self.active_tasks) > 0

    def all_completed(self) -> bool:
        """Check if all spawned tasks are completed."""
        return len(self.active_tasks) == 0

    def to_dict(self) -> Dict[str, Any]:
        def task_to_dict(t: ParallelTask) -> Dict[str, Any]:
            return {
                "task_id": t.task_id,
                "skill": t.skill,
                "instruction": t.instruction,
                "status": t.status,
                "started_at": t.started_at.isoformat() if t.started_at else None,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
                "result": t.result,
                "error": t.error,
            }

        return {
            "active_tasks": [task_to_dict(t) for t in self.active_tasks],
            "completed_tasks": [task_to_dict(t) for t in self.completed_tasks],
            "failed_tasks": [task_to_dict(t) for t in self.failed_tasks],
        }


@dataclass
class LearningSignals:
    """Signals collected during execution for learning."""
    successes: List[Dict[str, Any]] = field(default_factory=list)
    failures: List[Dict[str, Any]] = field(default_factory=list)
    improvements: List[Dict[str, Any]] = field(default_factory=list)
    observations: List[Dict[str, Any]] = field(default_factory=list)

    def record_success(self, node_id: str, edge_id: str, details: Dict[str, Any] = None) -> None:
        """Record a successful transition."""
        self.successes.append({
            "timestamp": datetime.utcnow().isoformat(),
            "node_id": node_id,
            "edge_id": edge_id,
            "details": details or {},
        })

    def record_failure(self, node_id: str, reason: str, details: Dict[str, Any] = None) -> None:
        """Record a failure."""
        self.failures.append({
            "timestamp": datetime.utcnow().isoformat(),
            "node_id": node_id,
            "reason": reason,
            "details": details or {},
        })

    def record_improvement(self, suggestion: str, context: Dict[str, Any] = None) -> None:
        """Record a potential improvement."""
        self.improvements.append({
            "timestamp": datetime.utcnow().isoformat(),
            "suggestion": suggestion,
            "context": context or {},
        })

    def record_observation(self, observation: str, data: Dict[str, Any] = None) -> None:
        """Record a general observation."""
        self.observations.append({
            "timestamp": datetime.utcnow().isoformat(),
            "observation": observation,
            "data": data or {},
        })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "successes": self.successes,
            "failures": self.failures,
            "improvements": self.improvements,
            "observations": self.observations,
        }


class State:
    """Complete runtime state for a brain execution."""

    def __init__(
        self,
        brain_id: str,
        run_id: Optional[str] = None,
        user_request: str = "",
    ):
        self.brain_id = brain_id
        self.run_id = run_id or str(uuid.uuid4())
        self.started_at = datetime.utcnow()
        self.ended_at: Optional[datetime] = None

        # Current position
        self.current_node: Optional[str] = None
        self.stage: Stage = Stage.INTAKE

        # User input
        self.user_request = user_request

        # Working data - this is the scratchpad
        self.data: Dict[str, Any] = {}

        # Counters
        self.counters = Counters()

        # Parallel state
        self.parallel = ParallelState()

        # Audit trail
        self.audit: List[AuditEvent] = []

        # Learning signals
        self.signals = LearningSignals()

        # Brain reference (loaded separately)
        self.brain: Optional[Dict[str, Any]] = None

    def set(self, path: str, value: Any) -> None:
        """Set a value at a dot-notation path in data."""
        parts = path.split(".")
        target = self.data

        for part in parts[:-1]:
            if part not in target:
                target[part] = {}
            target = target[part]

        target[parts[-1]] = value

    def get(self, path: str, default: Any = None) -> Any:
        """Get a value from a dot-notation path in data."""
        parts = path.split(".")
        target = self.data

        for part in parts:
            if isinstance(target, dict) and part in target:
                target = target[part]
            else:
                return default

        return target

    def apply_patch(self, patch: Dict[str, Any]) -> None:
        """Apply a patch to the data, merging deeply."""
        def deep_merge(base: Dict, updates: Dict) -> Dict:
            result = deepcopy(base)
            for key, value in updates.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = deepcopy(value)
            return result

        self.data = deep_merge(self.data, patch)

    def add_audit(
        self,
        node_id: str,
        action: str,
        summary: str,
        signals: Dict[str, Any] = None,
        details: Dict[str, Any] = None,
    ) -> None:
        """Add an audit event."""
        self.audit.append(AuditEvent(
            timestamp=datetime.utcnow(),
            node_id=node_id,
            stage=self.stage.value,
            action=action,
            summary=summary,
            signals=signals or {},
            details=details or {},
        ))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "brain_id": self.brain_id,
            "run_id": self.run_id,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "current_node": self.current_node,
            "stage": self.stage.value,
            "user_request": self.user_request,
            "data": self.data,
            "counters": self.counters.to_dict(),
            "parallel": self.parallel.to_dict(),
            "signals": self.signals.to_dict(),
        }

    def to_context(self) -> Dict[str, Any]:
        """Create a context dict for template rendering / guard evaluation."""
        return {
            "brain_id": self.brain_id,
            "run_id": self.run_id,
            "current_node": self.current_node,
            "stage": self.stage.value,
            "user_request": self.user_request,
            "data": self.data,
            "counters": self.counters.to_dict(),
            "brain": self.brain or {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> State:
        """Load from dictionary."""
        state = cls(
            brain_id=data.get("brain_id", ""),
            run_id=data.get("run_id"),
            user_request=data.get("user_request", ""),
        )

        state.started_at = datetime.fromisoformat(data.get("started_at", datetime.utcnow().isoformat()))
        if data.get("ended_at"):
            state.ended_at = datetime.fromisoformat(data["ended_at"])

        state.current_node = data.get("current_node")
        state.stage = Stage(data.get("stage", "intake"))
        state.data = data.get("data", {})
        state.counters = Counters.from_dict(data.get("counters", {}))

        return state

    def save(self, path: Path) -> None:
        """Save state to JSON file."""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def save_audit(self, path: Path) -> None:
        """Append audit events to JSONL file."""
        with open(path, "a") as f:
            for event in self.audit:
                f.write(json.dumps(event.to_dict()) + "\n")
        self.audit = []  # Clear after saving

    @classmethod
    def load(cls, path: Path) -> State:
        """Load state from JSON file."""
        with open(path) as f:
            data = json.load(f)
        return cls.from_dict(data)
