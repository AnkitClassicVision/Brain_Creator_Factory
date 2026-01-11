"""Brain - The main brain entity and manifest."""

from __future__ import annotations

import json
import uuid
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional
from dataclasses import dataclass, field
from enum import Enum


class LearningMode(str, Enum):
    """Learning modes for auto-application."""
    OFF = "off"
    SUGGEST_ONLY = "suggest_only"
    AUTO_SAFE = "auto_safe"
    AUTO_ALL = "auto_all"


@dataclass
class Objective:
    """A brain objective with measurable criteria."""
    description: str
    success_criteria: List[str] = field(default_factory=list)
    priority: int = 1


@dataclass
class Deliverable:
    """Expected output from the brain."""
    name: str
    format: str
    schema: Optional[Dict[str, Any]] = None
    required: bool = True


@dataclass
class Constraint:
    """Hard constraint on brain behavior."""
    type: Literal["must_do", "must_not"]
    description: str
    enforcement: Literal["hard", "soft"] = "hard"


@dataclass
class LearningPolicy:
    """Policy for learning and auto-updates."""
    enabled: bool = True
    mode: LearningMode = LearningMode.AUTO_SAFE

    # What can be auto-updated
    auto_update: Dict[str, bool] = field(default_factory=lambda: {
        "edge_priorities": True,
        "relationship_weights": True,
        "guard_thresholds": False,
        "node_prompts": False,
        "add_nodes": False,
        "remove_nodes": False,
        "add_edges": False,
        "remove_edges": False,
    })

    # What requires approval
    requires_approval: List[str] = field(default_factory=lambda: [
        "structural_changes",
        "constraint_changes",
        "new_skills",
    ])

    # Feedback sources
    feedback_sources: List[str] = field(default_factory=lambda: [
        "outcome",
        "user_feedback",
        "quality_scores",
    ])


@dataclass
class ExecutionConfig:
    """Configuration for brain execution."""
    max_steps: int = 100
    max_parallel: int = 5
    timeout_seconds: int = 3600
    max_retries: int = 3
    retry_backoff: float = 1.5


@dataclass
class BrainManifest:
    """Complete brain manifest."""
    id: str
    name: str
    version: str
    created_at: datetime
    updated_at: datetime

    # Purpose and objectives
    purpose: str
    primary_goal: str
    objectives: List[Objective] = field(default_factory=list)
    deliverables: List[Deliverable] = field(default_factory=list)

    # Constraints
    constraints: List[Constraint] = field(default_factory=list)

    # Configuration
    learning: LearningPolicy = field(default_factory=LearningPolicy)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)

    # Skills
    skills: List[str] = field(default_factory=list)
    auto_discover_skills: bool = True

    # Metadata
    tags: List[str] = field(default_factory=list)
    notes: str = ""

    @classmethod
    def create(
        cls,
        name: str,
        purpose: str,
        primary_goal: str,
        **kwargs
    ) -> BrainManifest:
        """Create a new brain manifest."""
        now = datetime.utcnow()
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            version="1.0.0",
            created_at=now,
            updated_at=now,
            purpose=purpose,
            primary_goal=primary_goal,
            **kwargs
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "brain": {
                "id": self.id,
                "name": self.name,
                "version": self.version,
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
                "purpose": self.purpose,
            },
            "objectives": {
                "primary_goal": self.primary_goal,
                "objectives": [
                    {"description": o.description, "success_criteria": o.success_criteria, "priority": o.priority}
                    for o in self.objectives
                ],
                "deliverables": [
                    {"name": d.name, "format": d.format, "schema": d.schema, "required": d.required}
                    for d in self.deliverables
                ],
            },
            "constraints": {
                "must_do": [c.description for c in self.constraints if c.type == "must_do"],
                "must_not": [c.description for c in self.constraints if c.type == "must_not"],
            },
            "learning": {
                "enabled": self.learning.enabled,
                "mode": self.learning.mode.value,
                "auto_update": self.learning.auto_update,
                "requires_approval": self.learning.requires_approval,
                "feedback_sources": self.learning.feedback_sources,
            },
            "execution": {
                "max_steps": self.execution.max_steps,
                "max_parallel": self.execution.max_parallel,
                "timeout_seconds": self.execution.timeout_seconds,
                "max_retries": self.execution.max_retries,
            },
            "skills": {
                "available": self.skills,
                "auto_discover": self.auto_discover_skills,
            },
            "metadata": {
                "tags": self.tags,
                "notes": self.notes,
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BrainManifest:
        """Load from dictionary."""
        brain = data.get("brain", {})
        objectives = data.get("objectives", {})
        constraints_data = data.get("constraints", {})
        learning_data = data.get("learning", {})
        execution_data = data.get("execution", {})
        skills_data = data.get("skills", {})
        metadata = data.get("metadata", {})

        return cls(
            id=brain.get("id", str(uuid.uuid4())),
            name=brain.get("name", "unnamed"),
            version=brain.get("version", "1.0.0"),
            created_at=datetime.fromisoformat(brain.get("created_at", datetime.utcnow().isoformat())),
            updated_at=datetime.fromisoformat(brain.get("updated_at", datetime.utcnow().isoformat())),
            purpose=brain.get("purpose", ""),
            primary_goal=objectives.get("primary_goal", ""),
            objectives=[
                Objective(
                    description=o.get("description", ""),
                    success_criteria=o.get("success_criteria", []),
                    priority=o.get("priority", 1)
                )
                for o in objectives.get("objectives", [])
            ],
            deliverables=[
                Deliverable(
                    name=d.get("name", ""),
                    format=d.get("format", ""),
                    schema=d.get("schema"),
                    required=d.get("required", True)
                )
                for d in objectives.get("deliverables", [])
            ],
            constraints=[
                Constraint(type="must_do", description=c)
                for c in constraints_data.get("must_do", [])
            ] + [
                Constraint(type="must_not", description=c)
                for c in constraints_data.get("must_not", [])
            ],
            learning=LearningPolicy(
                enabled=learning_data.get("enabled", True),
                mode=LearningMode(learning_data.get("mode", "auto_safe")),
                auto_update=learning_data.get("auto_update", {}),
                requires_approval=learning_data.get("requires_approval", []),
                feedback_sources=learning_data.get("feedback_sources", []),
            ),
            execution=ExecutionConfig(
                max_steps=execution_data.get("max_steps", 100),
                max_parallel=execution_data.get("max_parallel", 5),
                timeout_seconds=execution_data.get("timeout_seconds", 3600),
                max_retries=execution_data.get("max_retries", 3),
            ),
            skills=skills_data.get("available", []),
            auto_discover_skills=skills_data.get("auto_discover", True),
            tags=metadata.get("tags", []),
            notes=metadata.get("notes", ""),
        )


class Brain:
    """A complete brain instance with all components."""

    def __init__(self, path: Path):
        self.path = path
        self.manifest: Optional[BrainManifest] = None
        self._loaded = False

    @classmethod
    def create(cls, base_path: Path, name: str, manifest: BrainManifest) -> Brain:
        """Create a new brain at the specified path."""
        brain_path = base_path / name
        brain_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (brain_path / "skills").mkdir(exist_ok=True)
        (brain_path / "runs").mkdir(exist_ok=True)
        (brain_path / "evolution").mkdir(exist_ok=True)

        # Save manifest
        manifest_path = brain_path / "brain.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump(manifest.to_dict(), f, default_flow_style=False, sort_keys=False)

        # Create empty memory file
        (brain_path / "memory.jsonl").touch()

        # Create skill index
        skill_index = {"skills": [], "version": "1.0.0"}
        with open(brain_path / "skills" / "_index.yaml", "w") as f:
            yaml.dump(skill_index, f)

        # Create evolution tracking files
        (brain_path / "evolution" / "proposals.jsonl").touch()
        (brain_path / "evolution" / "applied.jsonl").touch()

        brain = cls(brain_path)
        brain.manifest = manifest
        brain._loaded = True

        return brain

    def load(self) -> Brain:
        """Load the brain from disk."""
        if self._loaded:
            return self

        manifest_path = self.path / "brain.yaml"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Brain manifest not found at {manifest_path}")

        with open(manifest_path) as f:
            data = yaml.safe_load(f)

        self.manifest = BrainManifest.from_dict(data)
        self._loaded = True

        return self

    def save(self) -> None:
        """Save the brain manifest to disk."""
        if not self.manifest:
            raise ValueError("No manifest to save")

        self.manifest.updated_at = datetime.utcnow()

        manifest_path = self.path / "brain.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump(self.manifest.to_dict(), f, default_flow_style=False, sort_keys=False)

    @property
    def graph_path(self) -> Path:
        return self.path / "graph.yaml"

    @property
    def memory_path(self) -> Path:
        return self.path / "memory.jsonl"

    @property
    def runs_path(self) -> Path:
        return self.path / "runs"

    @property
    def evolution_path(self) -> Path:
        return self.path / "evolution"

    @property
    def skills_path(self) -> Path:
        return self.path / "skills"
