"""Graph - Execution graph structures for brain workflows."""

from __future__ import annotations

import json
import uuid
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Set, Union
from dataclasses import dataclass, field
from enum import Enum

from .context import build_eval_env


class NodeType(str, Enum):
    """Types of nodes in the execution graph.

    Node Taxonomy (from Brain Factory specification):
    - PRIME: The source. Initializes ontology and task bounds.
    - FLOW: Main reasoning engine in the "Mainstream". Plans and reasons.
    - TRIBUTARY: Sandboxed execution for tools. Does dirty work in isolation.
    - DELTA: Merges parallel results back to mainstream.
    - SEDIMENT: Storage unit for verified facts. Future nodes "dredge" from here.
    - GATE: Quality control gate. Checks artifacts against constraints.
    - DECISION: Pure logic gate. Evaluates data against rules for routing.
                Never generates text; creates determinism by removing "vibe-based" choices.
    - TERMINAL: End state (success, failure, escalate).
    """
    PRIME = "prime"           # Initialize, set context (Intake Node)
    FLOW = "flow"             # Main LLM reasoning (Task Node)
    TRIBUTARY = "tributary"   # Tool/skill execution (Action Node)
    DELTA = "delta"           # Merge parallel results
    SEDIMENT = "sediment"     # Write to memory (Memory Node)
    GATE = "gate"             # Quality gate / validator (Evaluation Node)
    DECISION = "decision"     # Pure routing logic (Router Node) - NO LLM call
    TERMINAL = "terminal"     # End state


class EdgeType(str, Enum):
    """Types of edges connecting nodes.

    Edge Taxonomy (from Brain Factory specification):
    - LAMINAR: Standard smooth transition. Used when everything goes right.
    - TURBULENT: Emergency correction loop triggered by failure. Forces retry.
    - DREDGING: Pulls data from SEDIMENT nodes into FLOW nodes.
    - PERMEABLE: Cross-agent state read.
    - DECOMPOSES_INTO: Hierarchical link breaking Goal into Tasks (chunking).
    - DEPENDS_ON: Blocking link. Target node blocked until source completes.
    """
    LAMINAR = "laminar"             # Happy path, no retry (Next Step)
    TURBULENT = "turbulent"         # Retry loop with bounds (Correction Loop)
    DREDGING = "dredging"           # Memory retrieval
    PERMEABLE = "permeable"         # Cross-agent state read
    DECOMPOSES_INTO = "decomposes"  # Hierarchical: Goal -> Tasks (chunking)
    DEPENDS_ON = "depends"          # Blocking dependency link


class Stage(str, Enum):
    """Workflow stages."""
    INTAKE = "intake"
    RESEARCH = "research"
    PLANNING = "planning"
    EXECUTION = "execution"
    VERIFICATION = "verification"
    FINALIZATION = "finalization"
    COMPLETE = "complete"
    ESCALATED = "escalated"


class RelationType(str, Enum):
    """Types of relationships for learning."""
    INFORMS = "informs"
    GROUNDS = "grounds"
    ENABLES = "enables"
    BLOCKS = "blocks"
    CORRELATES = "correlates"
    INDICATES = "indicates"


@dataclass
class MemoryOperation:
    """Memory operations for a node."""
    dredge: List[Dict[str, Any]] = field(default_factory=list)
    write: bool = False
    source: Optional[str] = None
    require_triplets: bool = False
    conflict_action: Literal["flag", "overwrite", "ask"] = "flag"


@dataclass
class ParallelConfig:
    """Parallel execution configuration for a node."""
    spawn: bool = False
    max_concurrent: int = 3
    strategy: Literal["all", "by_step", "adaptive"] = "all"
    wait_for_all: bool = True


@dataclass
class GateConfig:
    """Configuration for gate nodes (EVALUATION nodes).

    Gate nodes check artifacts against constraints. If check fails,
    triggers a Turbulent Edge (retry loop).
    """
    criteria: List[Dict[str, str]] = field(default_factory=list)
    on_pass: str = ""
    on_fail: str = ""
    max_retries: int = 3


@dataclass
class DecisionConfig:
    """Configuration for decision nodes (ROUTER nodes).

    Decision nodes are pure logic gates that NEVER generate text.
    They evaluate data against rules to choose the next path deterministically.
    This creates determinism by removing "vibe-based" LLM routing decisions.

    Example:
        DecisionConfig(
            variable="state.data.confidence",
            rules=[
                {"condition": "> 0.8", "target": "execute"},
                {"condition": "> 0.5", "target": "research_more"},
                {"condition": "default", "target": "escalate"},
            ]
        )
    """
    # The variable/path to evaluate (e.g., "state.data.confidence")
    variable: str = ""

    # Rules to evaluate in order. Each rule has:
    # - condition: expression like "> 0.8", "== 'ready'", "in ['a','b']", "default"
    # - target: node_id to route to if condition matches
    rules: List[Dict[str, str]] = field(default_factory=list)

    # Optional: expression that must be true for any rule to apply
    # If false, falls through to default edge
    precondition: Optional[str] = None

    # Metadata for learning/debugging
    description: str = ""


@dataclass
class DependencyConfig:
    """Configuration for dependency edges (DEPENDS_ON edges).

    When an edge has type DEPENDS_ON, the target node is physically blocked
    from starting until the source node is complete. This prevents the agent
    from skipping steps.
    """
    # List of node_ids that must be completed before this edge can be taken
    required_nodes: List[str] = field(default_factory=list)

    # If true, ALL required nodes must complete. If false, ANY one is sufficient.
    require_all: bool = True

    # Optional: specific state values that must be present
    required_state: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecompositionConfig:
    """Configuration for decomposition edges (DECOMPOSES_INTO edges).

    Decomposes_Into is a hierarchical link that breaks a big Goal into
    smaller Tasks. This enforces "Chunking" (breaking work into 3-4 item
    groups) to keep the LLM focused.
    """
    # The parent goal/task being decomposed
    parent_id: str = ""

    # The type of decomposition
    decomposition_type: Literal["sequential", "parallel", "conditional"] = "sequential"

    # Maximum number of children (enforces chunking limit)
    max_children: int = 4

    # If true, all children must complete for parent to be considered done
    require_all_children: bool = True


@dataclass
class OutputSchema:
    """JSON schema for node output."""
    type: str = "object"
    required: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StateWrite:
    """A state write operation."""
    path: str
    from_: str  # Note: 'from' is reserved, using 'from_'
    transform: Optional[str] = None


@dataclass
class Node:
    """A node in the execution graph."""
    id: str
    type: NodeType
    stage: Stage
    purpose: str

    # LLM configuration
    prompt: str = ""
    output_schema: Optional[OutputSchema] = None

    # Tool/skill for tributary nodes
    skill_name: Optional[str] = None
    skill_config: Dict[str, Any] = field(default_factory=dict)

    # State operations
    state_writes: List[StateWrite] = field(default_factory=list)

    # Memory operations
    memory: MemoryOperation = field(default_factory=MemoryOperation)

    # Parallel configuration
    parallel: ParallelConfig = field(default_factory=ParallelConfig)

    # Gate configuration (for gate nodes)
    gate: Optional[GateConfig] = None

    # Decision configuration (for decision/router nodes)
    decision: Optional[DecisionConfig] = None

    # Terminal actions (for terminal nodes)
    on_reach: List[Dict[str, Any]] = field(default_factory=list)

    # Metadata
    version: str = "1.0.0"
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "id": self.id,
            "type": self.type.value,
            "stage": self.stage.value,
            "purpose": self.purpose,
        }

        if self.prompt:
            result["prompt"] = self.prompt

        if self.output_schema:
            result["output_schema"] = {
                "type": self.output_schema.type,
                "required": self.output_schema.required,
                "properties": self.output_schema.properties,
            }

        if self.skill_name:
            result["skill_name"] = self.skill_name
            result["skill_config"] = self.skill_config

        if self.state_writes:
            result["state_writes"] = [
                {"path": sw.path, "from": sw.from_, "transform": sw.transform}
                for sw in self.state_writes
            ]

        result["memory"] = {
            "dredge": self.memory.dredge,
            "write": self.memory.write,
            "source": self.memory.source,
            "conflict_action": self.memory.conflict_action,
        }

        result["parallel"] = {
            "spawn": self.parallel.spawn,
            "max_concurrent": self.parallel.max_concurrent,
            "strategy": self.parallel.strategy,
        }

        if self.gate:
            result["gate_config"] = {
                "criteria": self.gate.criteria,
                "on_pass": self.gate.on_pass,
                "on_fail": self.gate.on_fail,
                "max_retries": self.gate.max_retries,
            }

        if self.decision:
            result["decision_config"] = {
                "variable": self.decision.variable,
                "rules": self.decision.rules,
                "precondition": self.decision.precondition,
                "description": self.decision.description,
            }

        if self.on_reach:
            result["on_reach"] = self.on_reach

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Node:
        """Create from dictionary."""
        stage_value = data.get("stage", "execution")
        try:
            stage = Stage(stage_value)
        except Exception:
            stage = Stage.EXECUTION

        output_schema = None
        if "output_schema" in data:
            os_data = data["output_schema"]
            output_schema = OutputSchema(
                type=os_data.get("type", "object"),
                required=os_data.get("required", []),
                properties=os_data.get("properties", {}),
            )

        memory_data = data.get("memory", {})
        memory = MemoryOperation(
            dredge=memory_data.get("dredge", []),
            write=memory_data.get("write", False),
            source=memory_data.get("source"),
            conflict_action=memory_data.get("conflict_action", "flag"),
        )

        parallel_data = data.get("parallel", {})
        parallel = ParallelConfig(
            spawn=parallel_data.get("spawn", False),
            max_concurrent=parallel_data.get("max_concurrent", 3),
            strategy=parallel_data.get("strategy", "all"),
        )

        gate = None
        if "gate_config" in data:
            gc = data["gate_config"]
            gate = GateConfig(
                criteria=gc.get("criteria", []),
                on_pass=gc.get("on_pass", ""),
                on_fail=gc.get("on_fail", ""),
                max_retries=gc.get("max_retries", 3),
            )

        decision = None
        if "decision_config" in data:
            dc = data["decision_config"]
            decision = DecisionConfig(
                variable=dc.get("variable", ""),
                rules=dc.get("rules", []),
                precondition=dc.get("precondition"),
                description=dc.get("description", ""),
            )

        state_writes = []
        for sw in data.get("state_writes", []):
            state_writes.append(StateWrite(
                path=sw.get("path", ""),
                from_=sw.get("from", ""),
                transform=sw.get("transform"),
            ))

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            type=NodeType(data.get("type", "flow")),
            stage=stage,
            purpose=data.get("purpose", ""),
            prompt=data.get("prompt", ""),
            output_schema=output_schema,
            skill_name=data.get("skill_name") or data.get("skill"),
            skill_config=data.get("skill_config", {}),
            state_writes=state_writes,
            memory=memory,
            parallel=parallel,
            gate=gate,
            decision=decision,
            on_reach=data.get("on_reach", []),
        )


@dataclass
class EdgeAction:
    """Action to perform when traversing an edge."""
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Guard:
    """Guard condition for an edge."""
    expression: str
    description: Optional[str] = None

    def evaluate(self, state: Dict[str, Any]) -> bool:
        """Evaluate the guard expression against state."""
        # Safe evaluation with limited builtins
        allowed_builtins = {
            "len": len,
            "any": any,
            "all": all,
            "min": min,
            "max": max,
            "sum": sum,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "True": True,
            "False": False,
            "None": None,
        }

        try:
            env = build_eval_env(state)
            return bool(eval(self.expression, {"__builtins__": allowed_builtins}, env))
        except Exception as e:
            # Log error and return False on evaluation failure
            print(f"Guard evaluation error: {e}")
            return False


@dataclass
class Edge:
    """An edge connecting two nodes.

    Edges are the "Pipes" or "Sluice Gates" that connect nodes.
    The LLM cannot move between nodes unless an edge exists.
    """
    id: str
    from_node: str      # Node ID or "*" for any
    to_node: str        # Node ID
    type: EdgeType
    guard: Guard
    priority: int = 1

    # Turbulent edge configuration (for retry loops)
    max_retries: Optional[int] = None

    # Dependency configuration (for DEPENDS_ON edges)
    dependency: Optional[DependencyConfig] = None

    # Decomposition configuration (for DECOMPOSES_INTO edges)
    decomposition: Optional[DecompositionConfig] = None

    # Actions to perform on traverse
    on_traverse: List[EdgeAction] = field(default_factory=list)

    # Learning metadata
    success_count: int = 0
    failure_count: int = 0
    weight: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "id": self.id,
            "from": self.from_node,
            "to": self.to_node,
            "type": self.type.value,
            "guard": self.guard.expression,
            "priority": self.priority,
        }

        if self.max_retries is not None:
            result["max_retries"] = self.max_retries

        if self.dependency:
            result["dependency_config"] = {
                "required_nodes": self.dependency.required_nodes,
                "require_all": self.dependency.require_all,
                "required_state": self.dependency.required_state,
            }

        if self.decomposition:
            result["decomposition_config"] = {
                "parent_id": self.decomposition.parent_id,
                "decomposition_type": self.decomposition.decomposition_type,
                "max_children": self.decomposition.max_children,
                "require_all_children": self.decomposition.require_all_children,
            }

        if self.on_traverse:
            result["on_traverse"] = [
                {"action": a.action, **a.parameters}
                for a in self.on_traverse
            ]

        # Include learning metadata
        result["_learning"] = {
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "weight": self.weight,
        }

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Edge:
        """Create from dictionary."""
        learning = data.get("_learning", {})

        on_traverse = []
        for action_data in data.get("on_traverse", []):
            action_copy = dict(action_data)  # Don't modify original
            action = action_copy.pop("action", "unknown")
            on_traverse.append(EdgeAction(action=action, parameters=action_copy))

        # Load dependency config if present
        dependency = None
        if "dependency_config" in data:
            dc = data["dependency_config"]
            dependency = DependencyConfig(
                required_nodes=dc.get("required_nodes", []),
                require_all=dc.get("require_all", True),
                required_state=dc.get("required_state", {}),
            )

        # Load decomposition config if present
        decomposition = None
        if "decomposition_config" in data:
            dec = data["decomposition_config"]
            decomposition = DecompositionConfig(
                parent_id=dec.get("parent_id", ""),
                decomposition_type=dec.get("decomposition_type", "sequential"),
                max_children=dec.get("max_children", 4),
                require_all_children=dec.get("require_all_children", True),
            )

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            from_node=data.get("from", ""),
            to_node=data.get("to", ""),
            type=EdgeType(data.get("type", "laminar")),
            guard=Guard(expression=data.get("guard", "True")),
            priority=data.get("priority", 1),
            max_retries=data.get("max_retries"),
            dependency=dependency,
            decomposition=decomposition,
            on_traverse=on_traverse,
            success_count=learning.get("success_count", 0),
            failure_count=learning.get("failure_count", 0),
            weight=learning.get("weight", 1.0),
        )


@dataclass
class Relationship:
    """A learned relationship between concepts."""
    id: str
    from_concept: str
    to_concept: str
    type: RelationType
    weight: float = 1.0
    observations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def update_weight(self, delta: float, observation: str) -> None:
        """Update the relationship weight with a new observation."""
        self.weight = max(0.0, min(2.0, self.weight + delta))
        self.observations.append(observation)
        self.updated_at = datetime.utcnow()


class Graph:
    """The execution graph for a brain."""

    def __init__(self):
        self.name: str = ""
        self.version: str = "1.0.0"
        self.start_node: str = ""
        self.terminal_nodes: List[str] = []
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.relationships: List[Relationship] = []

    def add_node(self, node: Node) -> None:
        """Add a node to the graph."""
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the graph."""
        self.edges.append(edge)

    def add_relationship(self, relationship: Relationship) -> None:
        """Add a relationship to the graph."""
        self.relationships.append(relationship)

    def get_outgoing_edges(self, node_id: str) -> List[Edge]:
        """Get all edges leaving a node, sorted by priority."""
        edges = [e for e in self.edges if e.from_node == node_id or e.from_node == "*"]
        return sorted(edges, key=lambda e: e.priority)

    def find_valid_edge(self, node_id: str, state: Dict[str, Any]) -> Optional[Edge]:
        """Find the first valid edge from a node given current state."""
        for edge in self.get_outgoing_edges(node_id):
            if edge.guard.evaluate(state):
                return edge
        return None

    def validate(self) -> List[str]:
        """Validate the graph structure. Returns list of errors."""
        errors = []

        # Check start node exists
        if self.start_node not in self.nodes:
            errors.append(f"Start node '{self.start_node}' not found in nodes")

        # Check terminal nodes exist
        for term in self.terminal_nodes:
            if term not in self.nodes:
                errors.append(f"Terminal node '{term}' not found in nodes")

        # Check edges reference valid nodes
        for edge in self.edges:
            if edge.from_node != "*" and edge.from_node not in self.nodes:
                errors.append(f"Edge '{edge.id}' references unknown from_node '{edge.from_node}'")
            if edge.to_node not in self.nodes:
                errors.append(f"Edge '{edge.id}' references unknown to_node '{edge.to_node}'")

        # Check turbulent edges have max_retries
        for edge in self.edges:
            if edge.type == EdgeType.TURBULENT and edge.max_retries is None:
                errors.append(f"Turbulent edge '{edge.id}' missing max_retries")

        # Check all non-terminal nodes have at least one outgoing edge
        node_set = set(self.nodes.keys())
        terminal_set = set(self.terminal_nodes)
        for node_id in node_set - terminal_set:
            outgoing = self.get_outgoing_edges(node_id)
            if not outgoing:
                errors.append(f"Node '{node_id}' has no outgoing edges")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "graph": {
                "name": self.name,
                "version": self.version,
            },
            "start_node": self.start_node,
            "terminal_nodes": self.terminal_nodes,
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges],
            "relationships": [
                {
                    "id": r.id,
                    "from": r.from_concept,
                    "to": r.to_concept,
                    "type": r.type.value,
                    "weight": r.weight,
                    "observations": r.observations,
                }
                for r in self.relationships
            ],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Graph:
        """Load from dictionary."""
        graph = cls()

        graph_meta = data.get("graph", {})
        graph.name = graph_meta.get("name", "")
        graph.version = graph_meta.get("version", "1.0.0")

        graph.start_node = data.get("start_node", "") or graph_meta.get("start_node", "")
        graph.terminal_nodes = data.get("terminal_nodes", []) or graph_meta.get("terminal_nodes", [])

        for node_data in data.get("nodes", []):
            node = Node.from_dict(node_data)
            graph.nodes[node.id] = node

        for edge_data in data.get("edges", []):
            edge = Edge.from_dict(edge_data)
            graph.edges.append(edge)

        for rel_data in data.get("relationships", []):
            graph.relationships.append(Relationship(
                id=rel_data.get("id", str(uuid.uuid4())),
                from_concept=rel_data.get("from", ""),
                to_concept=rel_data.get("to", ""),
                type=RelationType(rel_data.get("type", "correlates")),
                weight=rel_data.get("weight", 1.0),
                observations=rel_data.get("observations", []),
            ))

        return graph

    def save(self, path: Path) -> None:
        """Save graph to YAML file."""
        with open(path, "w") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)

    @classmethod
    def load(cls, path: Path) -> Graph:
        """Load graph from YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)

    def update_edge_stats(self, edge_id: str, success: bool) -> None:
        """Update edge statistics after traversal."""
        for edge in self.edges:
            if edge.id == edge_id:
                if success:
                    edge.success_count += 1
                else:
                    edge.failure_count += 1
                break

    def update_relationship_weight(
        self,
        from_concept: str,
        to_concept: str,
        delta: float,
        observation: str
    ) -> None:
        """Update a relationship weight based on observation."""
        for rel in self.relationships:
            if rel.from_concept == from_concept and rel.to_concept == to_concept:
                rel.update_weight(delta, observation)
                return

        # Create new relationship if not found
        self.relationships.append(Relationship(
            id=str(uuid.uuid4()),
            from_concept=from_concept,
            to_concept=to_concept,
            type=RelationType.CORRELATES,
            weight=1.0 + delta,
            observations=[observation],
        ))
