# CC Brain Factory

A self-contained, self-learning system for creating deterministic AI workflow engines ("brains").

## What is a Brain?

A **brain** is a structured execution graph that:
- Guides an LLM through a deterministic workflow (not letting it decide what to do)
- Maintains state OUTSIDE the LLM context (preventing drift)
- Learns from execution and updates itself automatically
- Can spawn parallel sub-tasks
- Integrates with skills and tools
- Has clear success criteria and quality gates

## Key Innovation

Traditional LLM agents are probabilistic and drift. This system:

1. **Externalizes state** - State lives in a structured object, not LLM context
2. **Deterministic routing** - Guards (boolean expressions) control flow, not LLM decisions
3. **Bounded retries** - Turbulent edges have max_retries to prevent infinite loops
4. **Self-learning** - Analyzes runs, proposes changes, applies safe updates automatically
5. **Parallel execution** - Built-in support for spawning concurrent tasks
6. **Skill integration** - Modular skill system for tool use

## Quick Start

### 1. Create a Brain

```bash
# Use the controller.md to guide the discovery process
# Ask questions to understand the user's needs
# Generate the brain structure
```

Or programmatically:

```python
from cc_brain_factory.core import Brain, BrainManifest, Graph

# Create manifest
manifest = BrainManifest.create(
    name="my_brain",
    purpose="Research and summarize topics",
    primary_goal="Given a topic, research it and produce a summary",
)

# Create brain
brain = Brain.create(
    base_path=Path("brains"),
    name="my_brain",
    manifest=manifest,
)

# Copy template graph
import shutil
shutil.copy("templates/universal/graph.yaml", brain.graph_path)
```

### 2. Run a Brain

```python
from cc_brain_factory.core import BrainController, Brain

# Load brain
brain = Brain(Path("brains/my_brain")).load()

# Create controller with LLM client
controller = BrainController(
    brain=brain,
    llm_client=my_llm_client,
    skill_executor=my_skill_executor,
)

# Run
result = controller.run(
    user_request="Research the history of AI and summarize key milestones"
)

print(f"Outcome: {result.outcome}")
print(f"Deliverables: {result.deliverables}")
```

### 3. Learn and Evolve

```python
from cc_brain_factory.core import LearningEngine

# After running
engine = LearningEngine(
    graph=brain.graph,
    memory=brain.memory,
    evolution_path=brain.evolution_path,
)

# Analyze the run
analysis = engine.analyze_run(result, state)

# Generate proposals
proposals = engine.generate_proposals([analysis])

# Apply safe changes automatically
applied, errors = engine.auto_apply_safe_changes(proposals)

print(f"Applied {applied} changes automatically")
```

## How the Execution Graph Works

The brain's execution graph uses a **hydrology metaphor** - think of AI workflows as water flowing through channels. The graph consists of **nodes** (processing stations), **edges** (channels between nodes), and **relationships** (learned correlations).

### Execution Flow Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BRAIN EXECUTION FLOW                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   USER REQUEST                                                               │
│        │                                                                     │
│        ▼                                                                     │
│   ┌─────────┐    LAMINAR     ┌─────────┐    LAMINAR     ┌───────────┐       │
│   │  PRIME  │ ───────────▶   │  FLOW   │ ───────────▶   │ TRIBUTARY │       │
│   │ (init)  │                │(reason) │                │  (tools)  │       │
│   └─────────┘                └────┬────┘                └─────┬─────┘       │
│                                   │                           │              │
│                          TURBULENT│(retry)            DREDGING│(memory)     │
│                                   │                           │              │
│                                   ▼                           ▼              │
│                              ┌─────────┐                ┌──────────┐         │
│                              │  GATE   │◄───────────────│ SEDIMENT │         │
│                              │(verify) │                │ (store)  │         │
│                              └────┬────┘                └──────────┘         │
│                                   │                                          │
│                                   ▼                                          │
│                             ┌──────────┐     DECOMPOSES    ┌───────┐         │
│                             │ DECISION │ ─────────────────▶│ DELTA │         │
│                             │ (route)  │    (parallel)     │(merge)│         │
│                             └────┬─────┘                   └───┬───┘         │
│                                  │                             │             │
│                    ┌─────────────┼─────────────┐               │             │
│                    ▼             ▼             ▼               │             │
│              ┌─────────┐   ┌─────────┐   ┌──────────┐          │             │
│              │ SUCCESS │   │ FAILURE │   │ ESCALATE │◄─────────┘             │
│              │(terminal)   │(terminal)   │(terminal)│                        │
│              └─────────┘   └─────────┘   └──────────┘                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Node Types Table

| Node Type | Icon | LLM Call? | Purpose | When to Use | Example |
|-----------|------|-----------|---------|-------------|---------|
| **PRIME** | 🌊 | Yes | Initialize workflow, set ontology and bounds | First node - sets context, constraints, and initial understanding | Parse user request, establish scope |
| **FLOW** | 💧 | Yes | Main reasoning in the "mainstream" | Core thinking, planning, analysis, synthesis | Research planning, content generation |
| **TRIBUTARY** | 🔧 | No | Sandboxed tool/skill execution | When external tools are needed (search, API calls, calculations) | Web search, database query, file operations |
| **DELTA** | 🔀 | Optional | Merge parallel task results | After parallel work completes, combine artifacts | Merge research from multiple sources |
| **SEDIMENT** | 💎 | No | Write verified facts to long-term memory | Store important findings with provenance | Save verified research findings |
| **GATE** | ✅ | No | Quality check against criteria | Verify output meets standards before proceeding | Check confidence threshold, validate format |
| **DECISION** | 🚦 | **NO** | **Pure logic routing - NO LLM** | **Deterministic branching based on data** | Route by confidence score, check conditions |
| **TERMINAL** | 🏁 | No | End state (success/failure/escalate) | Workflow completion | Return results, report failure, escalate to human |

### Edge Types Table

| Edge Type | Symbol | Purpose | Configuration | When to Use |
|-----------|--------|---------|---------------|-------------|
| **LAMINAR** | → | Happy path, smooth transition | `guard`: condition to proceed | Normal flow between steps |
| **TURBULENT** | ↺ | Retry loop with bounds | `max_retries`: prevents infinite loops | When quality gate fails, retry previous step |
| **DREDGING** | ⬆ | Pull from long-term memory | `query`: what to retrieve | Load relevant facts from SEDIMENT |
| **PERMEABLE** | ⟷ | Cross-agent state sharing | `source_agent`: which agent | Multi-agent workflows sharing context |
| **DECOMPOSES** | ⤵ | Break goal into tasks (max 3-4) | `max_children`: chunk limit | Large goals that need sub-tasks |
| **DEPENDS** | ⏸ | Blocking dependency | `required_nodes`: what must complete | Prevent skipping prerequisites |

### Output Files Table

| Output File | Format | Purpose | Contents | Use Case |
|-------------|--------|---------|----------|----------|
| **final_state.json** | JSON | Complete session snapshot | Current node, all data, counters, metadata | Resume sessions, inspect results |
| **audit.jsonl** | JSONL | Step-by-step execution log | Timestamp, node, action, signals for each step | Debugging, compliance, learning analysis |
| **memory.jsonl** | JSONL | Verified facts with provenance | Facts, confidence scores, semantic triplets | Long-term knowledge, future runs |
| **evolution/*.json** | JSON | Learning proposals and changes | Proposed improvements, applied changes | Track brain evolution over time |

### Guard Expressions

Guards are Python-like expressions that control edge traversal:

| Pattern | Example | What It Checks |
|---------|---------|----------------|
| Data presence | `state.data.get('ready') == True` | Is 'ready' flag set? |
| Threshold | `state.data.get('confidence', 0) >= 0.8` | Is confidence high enough? |
| List check | `len(state.data.get('errors', [])) == 0` | Are there zero errors? |
| Counter check | `state.counters.retries.get('verify', 0) < 3` | Under retry limit? |
| Contains | `'critical' not in state.data.get('issues', [])` | No critical issues? |

### Decision Node Routing (The Key Innovation)

DECISION nodes eliminate "vibe-based" LLM routing with pure logic:

```yaml
- id: "confidence_router"
  type: "decision"
  purpose: "Route based on confidence - NO LLM call"
  decision_config:
    variable: "state.data.confidence"
    rules:
      - condition: ">= 0.9"
        target: "finalize"      # High confidence → finish
      - condition: ">= 0.7"
        target: "verify"        # Medium → verify more
      - condition: "default"
        target: "escalate"      # Low → ask human
```

### Why This Architecture Matters

| Traditional LLM Agent | Brain Creator Factory |
|----------------------|----------------------|
| LLM decides "what next" (probabilistic) | Graph guards decide "what next" (deterministic) |
| State hidden in context window | State externalized in structured objects |
| Drifts over long sessions | Bounded by explicit graph structure |
| Hard to debug/audit | Full JSONL audit trail |
| Can't reliably retry | TURBULENT edges with max_retries |
| No learning | Self-improving via learning engine |
| Single execution path | Parallel with DELTA merge |

## Architecture

```
cc_brain_factory/
├── controller.md              # Master orchestration guide (for Claude)
├── README.md                  # This file
│
├── core/                      # Python implementation
│   ├── brain.py              # Brain class and manifest
│   ├── graph.py              # Execution graph (nodes, edges, guards)
│   ├── state.py              # Runtime state management
│   ├── memory.py             # Long-term memory (sediment)
│   ├── controller.py         # Execution controller
│   ├── learning.py           # Learning and proposal engine
│   ├── parallel.py           # Parallel task execution
│   └── skills.py             # Skill registry and integration
│
├── discovery/                 # User interview system
│   └── questions.yaml        # Discovery questions
│
├── templates/                 # Brain templates
│   └── universal/            # Universal workflow template
│       └── graph.yaml
│
├── brains/                    # Created brains live here
│   └── <brain_name>/
│       ├── brain.yaml        # Manifest
│       ├── graph.yaml        # Execution graph
│       ├── memory.jsonl      # Long-term memory
│       ├── skills/           # Brain-specific skills
│       ├── runs/             # Execution history
│       └── evolution/        # Learning and changes
│
└── schemas/                   # JSON schemas for validation
```

## Brain Structure

Each brain is a folder with:

### brain.yaml (Manifest)
```yaml
brain:
  id: "uuid"
  name: "my_brain"
  purpose: "What this brain does"

objectives:
  primary_goal: "The main thing to accomplish"
  success_criteria: [...]
  deliverables: [...]

constraints:
  must_do: [...]
  must_not: [...]

learning:
  enabled: true
  auto_update:
    edge_priorities: true
    relationship_weights: true
    guard_thresholds: false  # Requires approval
```

### graph.yaml (Execution Graph)
```yaml
nodes:
  - id: "intake"
    type: "flow"
    prompt: "..."
    output_schema: {...}

edges:
  - id: "e_intake_research"
    from: "intake"
    to: "research"
    guard: "state.data.get('ready') == True"
    priority: 1

relationships:
  - from: "research"
    to: "plan"
    type: "informs"
    weight: 1.0
```

## Node Types

| Type | Purpose | LLM Call | Description |
|------|---------|----------|-------------|
| `prime` | Initialize workflow | Yes | Sets up ontology, context, constraints |
| `flow` | Main reasoning | Yes | Plans and reasons in the "mainstream" |
| `tributary` | Tool/skill execution | No | Sandboxed execution, isolated from main flow |
| `delta` | Merge parallel results | Optional | Combines artifacts from parallel work |
| `sediment` | Write to memory | No | Stores verified facts for future retrieval |
| `gate` | Quality check | No | Evaluates criteria, triggers retry on fail |
| `decision` | **Route (NO LLM)** | **No** | **Pure logic gate - deterministic routing** |
| `terminal` | End state | No | Success, failure, or escalate |

### DECISION Node (Router)

DECISION nodes are **pure logic gates** that NEVER call the LLM. They evaluate data against rules to choose the next path deterministically. This removes "vibe-based" LLM routing decisions.

```yaml
- id: "confidence_router"
  type: "decision"
  stage: "verification"
  purpose: "Route based on confidence - NO LLM call"
  decision_config:
    variable: "state.data.confidence"
    rules:
      - condition: ">= 0.9"
        target: "finalize"
      - condition: ">= 0.7"
        target: "verify"
      - condition: "default"
        target: "escalate"
```

## Edge Types

| Type | Purpose | Description |
|------|---------|-------------|
| `laminar` | Happy path | Standard smooth transition |
| `turbulent` | Retry loop | Correction loop with bounded max_retries |
| `dredging` | Memory retrieval | Pulls data from SEDIMENT nodes |
| `permeable` | Cross-agent read | Share state across agents |
| `decomposes` | **Goal chunking** | **Breaks goals into tasks (max 3-4 items)** |
| `depends` | **Blocking dependency** | **Target blocked until source completes** |

### DECOMPOSES_INTO Edge

Breaks a big Goal into smaller Tasks. Enforces "Chunking" (3-4 item groups) to keep the LLM focused:

```yaml
- id: "e_decompose_plan"
  type: "decomposes"
  from: "plan"
  to: "execute"
  decomposition_config:
    parent_id: "main_goal"
    decomposition_type: "sequential"
    max_children: 4
    require_all_children: true
```

### DEPENDS_ON Edge

Physically blocks the target node from starting until the source nodes are complete:

```yaml
- id: "e_execute_depends"
  type: "depends"
  from: "research"
  to: "execute"
  dependency_config:
    required_nodes: ["research", "plan"]
    require_all: true
    required_state:
      research_complete: true
```

## Output Files

When you run a brain, it produces these output files:

### `runs/<timestamp>/final_state.json` - Session State

The complete state snapshot after execution:

```json
{
  "brain_id": "research-brain-001",
  "run_id": "abc123",
  "current_node": "success",
  "stage": "complete",
  "user_request": "Research AI history",
  "data": {
    "understood_request": "Research the history of AI",
    "findings": [...],
    "verified_facts": [...],
    "final_artifact": {"summary": "...", "sources": [...]},
    "done": true
  },
  "counters": {
    "total_steps": 15,
    "node_visits": {"prime": 1, "research": 3, "verify": 2},
    "retries": {"e_verify_retry": 1},
    "memory_writes": 5
  }
}
```

### `runs/<timestamp>/audit.jsonl` - Audit Trail

Line-delimited JSON of every step (for debugging & learning):

```jsonl
{"ts": "2024-01-10T15:30:00Z", "node_id": "prime", "action": "executed_prime", "summary": "Initialized"}
{"ts": "2024-01-10T15:30:05Z", "node_id": "research", "action": "executed_flow", "signals": {"confidence": 0.85}}
{"ts": "2024-01-10T15:30:10Z", "node_id": "verify", "action": "executed_gate", "summary": "Gate passed"}
```

### `memory.jsonl` - Sediment (Long-Term Memory)

Verified facts with provenance:

```jsonl
{"fact_id": "f001", "text": "Dartmouth Conference 1956 started AI", "confidence": 0.95, "triplets": [{"subject": "Dartmouth", "predicate": "started", "object": "AI"}]}
```

## TOON Format (Token-Oriented Object Notation)

Compact encoding that saves ~40% tokens vs JSON:

```python
from cc_brain_factory.core import toon_encode, toon_decode

data = {"user": {"name": "Alice", "age": 30}, "ready": True}
encoded = toon_encode(data)
# Output:
# user.name: Alice
# user.age: 30
# ready: true

decoded = toon_decode(encoded)
# {'user': {'name': 'Alice', 'age': 30}, 'ready': True}
```

## Learning System

After each run, the learning engine:

1. **Analyzes** - Extracts patterns from execution
2. **Proposes** - Generates improvement proposals
3. **Auto-applies** - Applies safe changes (priorities, weights)
4. **Queues** - Queues risky changes for approval
5. **Writes lessons** - Persists learnings to memory

### What Can Be Auto-Updated

```yaml
auto_update:
  edge_priorities: true      # Adjust routing order
  edge_weights: true         # Update edge success weights
  relationship_weights: true # Update correlation weights
  max_retries: true         # Adjust retry limits

  # These require approval:
  guard_thresholds: false
  prompts: false
  add_nodes: false
  remove_nodes: false
```

## Parallel Execution

Nodes can spawn parallel tasks:

```yaml
# In LLM output:
{
  "parallel_tasks": [
    {
      "task_id": "search_1",
      "skill": "web_search",
      "instruction": "Search for X",
      "wait": true
    },
    {
      "task_id": "search_2",
      "skill": "web_search",
      "instruction": "Search for Y",
      "wait": true
    }
  ]
}
```

The controller:
1. Spawns tasks concurrently
2. Waits for completion (if `wait: true`)
3. Merges results into state
4. Continues execution

## Skills

Register skills for the brain to use:

```python
from cc_brain_factory.core import SkillRegistry, Skill

registry = SkillRegistry(brain.skills_path)

# Register a function as a skill
registry.register_function(
    name="web_search",
    func=my_search_function,
    description="Searches the web",
    capabilities=["search", "research"],
)

# Or register a Skill object
skill = Skill(
    name="calculator",
    description="Math calculations",
    executor=CalculatorExecutor(),
)
registry.register(skill)
```

## Memory (Sediment)

Long-term memory stores verified facts:

```python
from cc_brain_factory.core import MemoryStore, Fact, MemoryQuery

memory = MemoryStore(brain.memory_path)

# Write facts
memory.write([
    Fact(
        fact_id="fact_1",
        text="The sky is blue",
        confidence=0.95,
    )
], run_id="run_1", node_id="research")

# Query memory
result = memory.query(MemoryQuery(
    text_search="sky color",
    min_confidence=0.8,
    limit=5,
))
```

## Guard Expressions

Guards are Python-like expressions:

```python
# Simple checks
"state.data.get('ready') == True"
"state.data.get('score', 0) >= 0.8"

# List operations
"len(state.data.get('errors', [])) == 0"
"'critical' not in state.data.get('error_types', [])"

# Counter checks
"state.counters.retries.get('verify', 0) < 3"
```

## Controller.md

The `controller.md` file is the master orchestration guide. When used with Claude (or similar LLM), it:

1. **Guides discovery** - Interview questions to understand needs
2. **Creates brains** - Templates and structure generation
3. **Runs brains** - Execution flow documentation
4. **Triggers learning** - Post-run analysis

This makes the brain factory itself usable as an AI-guided tool.

## Best Practices

1. **Keep prompts focused** - Each node should do one thing well
2. **Use gates liberally** - Quality checks prevent bad outputs
3. **Bound retries** - Always set max_retries on turbulent edges
4. **Externalize state** - Don't rely on LLM remembering things
5. **Write to memory** - Persist verified facts for future runs
6. **Monitor learning** - Review proposals before approving structural changes

## Example Use Cases

- **Research workflows** - Gather, verify, synthesize information
- **Content creation** - Research → Plan → Write → Review → Publish
- **Data processing** - Intake → Validate → Transform → Output
- **Decision support** - Gather → Analyze → Recommend → Verify

## Contributing

This is a self-contained system. To extend:

1. Add new node types in `core/graph.py`
2. Add new skills in `core/skills.py`
3. Create new templates in `templates/`
4. Enhance learning in `core/learning.py`

## License

MIT
