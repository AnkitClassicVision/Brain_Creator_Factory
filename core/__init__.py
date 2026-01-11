"""CC Brain Factory - Core Modules

A self-contained, self-learning brain factory for creating deterministic AI workflows.

This module implements the Brain Factory specification with the following components:

Node Types (NodeType enum):
    - PRIME: Initialize ontology and task bounds (Intake Node)
    - FLOW: Main reasoning engine (Task Node)
    - TRIBUTARY: Sandboxed tool execution (Action Node)
    - DELTA: Merge parallel results
    - SEDIMENT: Verified fact storage (Memory Node)
    - GATE: Quality control validator (Evaluation Node)
    - DECISION: Pure routing logic (Router Node) - NO LLM calls
    - TERMINAL: End state

Edge Types (EdgeType enum):
    - LAMINAR: Standard smooth transition (Next Step)
    - TURBULENT: Retry loop with bounds (Correction Loop)
    - DREDGING: Memory retrieval
    - PERMEABLE: Cross-agent state read
    - DECOMPOSES_INTO: Goal -> Task decomposition (Chunking)
    - DEPENDS_ON: Blocking dependency

Data Formats:
    - TOON: Token-Oriented Object Notation for compact LLM context
"""

from .brain import Brain, BrainManifest
from .graph import (
    Graph, Node, Edge, Guard,
    NodeType, EdgeType, Stage, RelationType,
    GateConfig, DecisionConfig, DependencyConfig, DecompositionConfig,
    MemoryOperation, ParallelConfig, OutputSchema, StateWrite,
)
from .state import State, Counters, ParallelState, LearningSignals, AuditEvent
from .memory import MemoryStore, Fact, MemoryQuery
from .controller import BrainController, RunResult, RunOutcome, NodeResult
from .learning import LearningEngine, Proposal, Change
from .evolution import EvolutionEngine
from .parallel import ParallelExecutor, Task, TaskResult
from .skills import SkillRegistry, Skill
from .toon import (
    encode as toon_encode,
    decode as toon_decode,
    encode_compact as toon_encode_compact,
    decode_compact as toon_decode_compact,
    state_to_toon,
)

__all__ = [
    # Brain
    "Brain",
    "BrainManifest",

    # Graph - Core
    "Graph",
    "Node",
    "Edge",
    "Guard",

    # Graph - Types (Enums)
    "NodeType",
    "EdgeType",
    "Stage",
    "RelationType",

    # Graph - Configs
    "GateConfig",
    "DecisionConfig",
    "DependencyConfig",
    "DecompositionConfig",
    "MemoryOperation",
    "ParallelConfig",
    "OutputSchema",
    "StateWrite",

    # State
    "State",
    "Counters",
    "ParallelState",
    "LearningSignals",
    "AuditEvent",

    # Memory
    "MemoryStore",
    "Fact",
    "MemoryQuery",

    # Controller
    "BrainController",
    "RunResult",
    "RunOutcome",
    "NodeResult",

    # Learning
    "LearningEngine",
    "Proposal",
    "Change",
    "EvolutionEngine",

    # Parallel
    "ParallelExecutor",
    "Task",
    "TaskResult",

    # Skills
    "SkillRegistry",
    "Skill",

    # TOON (Token-Oriented Object Notation)
    "toon_encode",
    "toon_decode",
    "toon_encode_compact",
    "toon_decode_compact",
    "state_to_toon",
]

__version__ = "1.0.0"
