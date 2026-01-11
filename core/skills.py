"""Skills - Skill registry and integration for brain workflows."""

from __future__ import annotations

import yaml
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Protocol
from dataclasses import dataclass, field
from datetime import datetime


class SkillExecutorProtocol(Protocol):
    """Protocol for skill execution."""

    def execute(
        self,
        instruction: str,
        context: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Execute the skill with given instruction and context."""
        ...


@dataclass
class SkillParameter:
    """A parameter for a skill."""
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None


@dataclass
class Skill:
    """A skill that can be used by a brain."""
    name: str
    description: str
    version: str = "1.0.0"

    # What this skill can do
    capabilities: List[str] = field(default_factory=list)

    # Input/output specification
    parameters: List[SkillParameter] = field(default_factory=list)
    output_schema: Dict[str, Any] = field(default_factory=dict)

    # Execution configuration
    timeout: float = 60.0
    max_retries: int = 3
    requires_context: List[str] = field(default_factory=list)

    # The actual executor
    executor: Optional[SkillExecutorProtocol] = None

    # Metadata
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Usage statistics
    invocation_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    avg_duration: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "capabilities": self.capabilities,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type,
                    "description": p.description,
                    "required": p.required,
                    "default": p.default,
                }
                for p in self.parameters
            ],
            "output_schema": self.output_schema,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "requires_context": self.requires_context,
            "tags": self.tags,
            "stats": {
                "invocation_count": self.invocation_count,
                "success_count": self.success_count,
                "failure_count": self.failure_count,
                "avg_duration": self.avg_duration,
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Skill:
        stats = data.get("stats", {})
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            capabilities=data.get("capabilities", []),
            parameters=[
                SkillParameter(
                    name=p.get("name", ""),
                    type=p.get("type", "string"),
                    description=p.get("description", ""),
                    required=p.get("required", True),
                    default=p.get("default"),
                )
                for p in data.get("parameters", [])
            ],
            output_schema=data.get("output_schema", {}),
            timeout=data.get("timeout", 60.0),
            max_retries=data.get("max_retries", 3),
            requires_context=data.get("requires_context", []),
            tags=data.get("tags", []),
            invocation_count=stats.get("invocation_count", 0),
            success_count=stats.get("success_count", 0),
            failure_count=stats.get("failure_count", 0),
            avg_duration=stats.get("avg_duration", 0.0),
        )

    def execute(
        self,
        instruction: str,
        context: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Execute this skill."""
        if not self.executor:
            raise ValueError(f"Skill {self.name} has no executor configured")

        start_time = datetime.utcnow()
        self.invocation_count += 1

        try:
            result = self.executor.execute(instruction, context, **kwargs)
            self.success_count += 1

            # Update average duration
            duration = (datetime.utcnow() - start_time).total_seconds()
            total_duration = self.avg_duration * (self.invocation_count - 1) + duration
            self.avg_duration = total_duration / self.invocation_count

            return result

        except Exception as e:
            self.failure_count += 1
            raise


class SkillRegistry:
    """
    Registry for managing skills available to brains.

    Supports:
    - Loading skills from disk
    - Registering skills programmatically
    - Finding skills by capability
    - Executing skills
    """

    def __init__(self, skills_path: Optional[Path] = None):
        self.skills_path = skills_path
        self._skills: Dict[str, Skill] = {}
        self._loaded = False

    def load(self) -> None:
        """Load skills from disk."""
        if self._loaded or not self.skills_path:
            return

        index_path = self.skills_path / "_index.yaml"
        if not index_path.exists():
            self._loaded = True
            return

        with open(index_path) as f:
            index = yaml.safe_load(f) or {}

        for skill_entry in index.get("skills", []):
            skill_name = skill_entry.get("name")
            skill_file = skill_entry.get("file")

            if skill_file:
                skill_path = self.skills_path / skill_file
                if skill_path.exists():
                    with open(skill_path) as f:
                        skill_data = yaml.safe_load(f)
                    skill = Skill.from_dict(skill_data)
                    self._skills[skill.name] = skill

        self._loaded = True

    def save(self) -> None:
        """Save skill registry to disk."""
        if not self.skills_path:
            return

        self.skills_path.mkdir(parents=True, exist_ok=True)

        # Save index
        index = {
            "version": "1.0.0",
            "skills": [
                {"name": name, "file": f"{name}.yaml"}
                for name in self._skills
            ]
        }

        with open(self.skills_path / "_index.yaml", "w") as f:
            yaml.dump(index, f)

        # Save each skill
        for name, skill in self._skills.items():
            skill_path = self.skills_path / f"{name}.yaml"
            with open(skill_path, "w") as f:
                yaml.dump(skill.to_dict(), f)

    def register(
        self,
        skill: Skill,
        executor: Optional[SkillExecutorProtocol] = None
    ) -> None:
        """Register a skill."""
        if executor:
            skill.executor = executor
        self._skills[skill.name] = skill

    def register_function(
        self,
        name: str,
        func: Callable[[str, Dict[str, Any]], Dict[str, Any]],
        description: str = "",
        capabilities: List[str] = None,
        **kwargs
    ) -> Skill:
        """Register a function as a skill."""

        class FunctionExecutor:
            def __init__(self, fn):
                self.fn = fn

            def execute(self, instruction: str, context: Dict[str, Any], **kw) -> Dict[str, Any]:
                return self.fn(instruction, context, **kw)

        skill = Skill(
            name=name,
            description=description or func.__doc__ or "",
            capabilities=capabilities or [],
            executor=FunctionExecutor(func),
            **kwargs
        )

        self._skills[name] = skill
        return skill

    def get(self, name: str) -> Optional[Skill]:
        """Get a skill by name."""
        self.load()
        return self._skills.get(name)

    def list_all(self) -> List[Skill]:
        """List all registered skills."""
        self.load()
        return list(self._skills.values())

    def list_names(self) -> List[str]:
        """List all skill names."""
        self.load()
        return list(self._skills.keys())

    def find_by_capability(self, capability: str) -> List[Skill]:
        """Find skills with a specific capability."""
        self.load()
        return [
            skill for skill in self._skills.values()
            if capability in skill.capabilities
        ]

    def find_by_tag(self, tag: str) -> List[Skill]:
        """Find skills with a specific tag."""
        self.load()
        return [
            skill for skill in self._skills.values()
            if tag in skill.tags
        ]

    def execute(
        self,
        skill_name: str,
        instruction: str,
        context: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Execute a skill by name."""
        skill = self.get(skill_name)
        if not skill:
            raise ValueError(f"Skill not found: {skill_name}")

        return skill.execute(instruction, context, **kwargs)


# Built-in skills

def create_echo_skill() -> Skill:
    """Create a simple echo skill for testing."""

    class EchoExecutor:
        def execute(self, instruction: str, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
            return {
                "echo": instruction,
                "context_keys": list(context.keys()),
                "success": True,
            }

    return Skill(
        name="echo",
        description="Echoes the instruction back. Useful for testing.",
        capabilities=["test", "debug"],
        executor=EchoExecutor(),
        tags=["builtin", "test"],
    )


def create_calculator_skill() -> Skill:
    """Create a simple calculator skill."""

    class CalculatorExecutor:
        def execute(self, instruction: str, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
            try:
                # Extract expression from instruction
                # Simple: assume instruction is the expression
                expression = instruction.strip()

                # Safe eval with limited operations
                allowed = {
                    "__builtins__": {},
                    "abs": abs, "round": round,
                    "min": min, "max": max, "sum": sum,
                    "pow": pow, "int": int, "float": float,
                }

                result = eval(expression, allowed, {})

                return {
                    "expression": expression,
                    "result": result,
                    "success": True,
                }
            except Exception as e:
                return {
                    "expression": instruction,
                    "error": str(e),
                    "success": False,
                }

    return Skill(
        name="calculator",
        description="Evaluates mathematical expressions.",
        capabilities=["math", "calculate"],
        executor=CalculatorExecutor(),
        tags=["builtin", "utility"],
    )


def create_memory_query_skill(memory_store) -> Skill:
    """Create a skill for querying memory."""

    class MemoryQueryExecutor:
        def __init__(self, memory):
            self.memory = memory

        def execute(self, instruction: str, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
            from .memory import MemoryQuery

            query = MemoryQuery(
                text_search=instruction,
                limit=kwargs.get("limit", 10),
            )

            result = self.memory.query(query)

            return {
                "query": instruction,
                "matches": len(result.records),
                "summary": result.to_summary(),
                "facts": [r.fact.to_dict() for r in result.records],
                "success": True,
            }

    return Skill(
        name="memory_query",
        description="Queries the brain's long-term memory for relevant facts.",
        capabilities=["memory", "retrieval", "search"],
        executor=MemoryQueryExecutor(memory_store),
        tags=["builtin", "memory"],
    )


def create_default_registry() -> SkillRegistry:
    """Create a registry with default built-in skills."""
    registry = SkillRegistry()
    registry.register(create_echo_skill())
    registry.register(create_calculator_skill())
    return registry
