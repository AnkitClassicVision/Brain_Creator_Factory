# CC Brain Factory - Master Controller

This is the master orchestration document for creating, running, and evolving "brains" - deterministic, self-learning AI workflow systems.

---

## How This Works

A **brain** is a structured execution graph that:
- Guides an LLM through a deterministic workflow
- Maintains external state (not in LLM context)
- Learns from execution and updates itself
- Can spawn parallel sub-tasks
- Integrates skills and tools
- Has clear success criteria and quality gates

**You (Claude) are the orchestrator.** This document tells you how to:
1. Interview the user to understand their needs
2. Create a brain tailored to their problem
3. Run the brain and track state
4. Learn from runs and evolve the brain

---

## Phase 1: Discovery

When a user wants to create a new brain, conduct this interview.

### 1.1 Problem Understanding

Ask these questions (adapt based on responses):

```yaml
discovery_questions:
  - category: "Core Purpose"
    questions:
      - "What problem are you trying to solve?"
      - "What would a successful outcome look like?"
      - "Who or what will use the output?"

  - category: "Inputs & Constraints"
    questions:
      - "What inputs/data will be available?"
      - "What tools, APIs, or skills should be used?"
      - "What are the hard constraints (must do / must never do)?"
      - "Are there time, cost, or resource limits?"

  - category: "Process Understanding"
    questions:
      - "Is there an existing process or workflow?"
      - "What are the key decision points?"
      - "Where do things typically go wrong?"
      - "What needs human approval vs. can be automated?"

  - category: "Quality & Success"
    questions:
      - "How will you know if the output is good?"
      - "What quality checks should happen?"
      - "What does failure look like and how should it be handled?"

  - category: "Learning & Adaptation"
    questions:
      - "Should the brain learn from its runs?"
      - "What aspects should be able to change automatically?"
      - "What changes require human approval?"
```

### 1.2 Objective Extraction

From the interview, extract and confirm:

```yaml
brain_objectives:
  primary_goal: "<one sentence>"
  success_criteria:
    - criterion: "<what>"
      measurable: "<how to verify>"
  deliverables:
    - name: "<output name>"
      format: "<type/schema>"
  constraints:
    must_do: []
    must_not: []
  available_inputs: []
  available_skills: []
  failure_modes:
    - condition: "<when>"
      action: "<what to do>"
```

### 1.3 Workflow Mapping

Identify the workflow structure:

```yaml
workflow_analysis:
  type: "linear|branching|iterative|parallel"
  phases:
    - name: "<phase>"
      purpose: "<what it does>"
      inputs: []
      outputs: []
      can_parallelize: true|false
  decision_points:
    - after: "<phase>"
      condition: "<what to check>"
      branches: ["<option1>", "<option2>"]
  iteration_points:
    - phase: "<phase>"
      retry_condition: "<when to retry>"
      max_retries: N
```

---

## Phase 2: Brain Creation

After discovery, create the brain.

### 2.1 Brain Folder Structure

Create in `brains/<brain_name>/`:

```
brains/<brain_name>/
├── brain.yaml           # Manifest and config
├── graph.yaml           # Execution graph
├── state.yaml           # Runtime state template
├── memory.jsonl         # Long-term memory (starts empty)
├── skills/              # Brain-specific skills
│   └── _index.yaml      # Skill registry
├── runs/                # Execution history
└── evolution/           # Learning and changes
    ├── proposals.jsonl  # Proposed changes
    └── applied.jsonl    # Applied changes
```

### 2.2 Brain Manifest (brain.yaml)

```yaml
brain:
  id: "<uuid>"
  name: "<brain_name>"
  version: "1.0.0"
  created: "<timestamp>"
  purpose: "<from discovery>"

objectives:
  primary_goal: "<from discovery>"
  success_criteria: []
  deliverables: []

constraints:
  must_do: []
  must_not: []

learning:
  enabled: true
  auto_apply:
    relationships: true      # Auto-update relationship weights
    edge_priorities: true    # Auto-adjust routing priorities
    guard_thresholds: false  # Requires approval
    add_nodes: false         # Requires approval
    remove_nodes: false      # Requires approval
  approval_required:
    - "structural_changes"
    - "new_skills"
    - "constraint_changes"

execution:
  max_steps: 100
  max_parallel: 5
  timeout_seconds: 3600

skills:
  available: []
  auto_discover: true
```

### 2.3 Execution Graph (graph.yaml)

```yaml
graph:
  name: "<brain_name>"
  version: "1.0.0"

  # Entry and exit
  start_node: "intake"
  terminal_nodes: ["success", "failure", "escalate"]

nodes:
  - id: "intake"
    type: "flow"              # prime|flow|tributary|delta|sediment|gate
    stage: "intake"
    purpose: "<what this node does>"

    # Instructions for the LLM at this node
    prompt: |
      You are at the INTAKE stage.

      USER REQUEST: {{user_request}}

      Your task:
      1. Parse and understand the request
      2. Identify what information is needed
      3. Determine the approach

      Output the following JSON:
      {
        "understood_request": "<your interpretation>",
        "information_needed": ["<item1>", "<item2>"],
        "approach": "<high-level plan>",
        "ready_to_proceed": true|false,
        "clarification_questions": ["<if not ready>"]
      }

    # Expected output schema
    output_schema:
      type: "object"
      required: ["understood_request", "ready_to_proceed"]
      properties:
        understood_request: { type: "string" }
        information_needed: { type: "array", items: { type: "string" } }
        approach: { type: "string" }
        ready_to_proceed: { type: "boolean" }
        clarification_questions: { type: "array", items: { type: "string" } }

    # State updates
    state_writes:
      - path: "data.understood_request"
        from: "output.understood_request"
      - path: "data.approach"
        from: "output.approach"

    # Memory operations
    memory:
      dredge: []              # Queries to pull from memory
      write: false            # Don't write at this stage

    # Parallel operations
    parallel:
      spawn: false

  - id: "research"
    type: "flow"
    stage: "research"
    purpose: "Gather information and verify facts"

    prompt: |
      You are at the RESEARCH stage.

      APPROACH: {{state.data.approach}}
      AVAILABLE SKILLS: {{available_skills}}
      VERIFIED MEMORY: {{dredged_memory}}

      Your task:
      1. Identify what research is needed
      2. Spawn parallel research tasks if beneficial
      3. Return structured findings

      To spawn parallel tasks, include in your output:
      {
        "parallel_tasks": [
          {
            "task_id": "<unique_id>",
            "skill": "<skill_name>",
            "instruction": "<what to do>",
            "wait": true|false
          }
        ]
      }

    output_schema:
      type: "object"
      properties:
        findings: { type: "array" }
        verified_facts: { type: "array" }
        open_questions: { type: "array" }
        parallel_tasks: { type: "array" }
        research_complete: { type: "boolean" }

    memory:
      dredge:
        - query: "relevant to {{state.data.understood_request}}"
          as_key: "prior_knowledge"
      write: false

    parallel:
      spawn: true
      max_concurrent: 3

  - id: "sediment_research"
    type: "sediment"
    stage: "research"
    purpose: "Commit verified facts to long-term memory"

    memory:
      write: true
      source: "state.data.verified_facts"
      require_triplets: false
      conflict_action: "flag"  # flag|overwrite|ask

  - id: "plan"
    type: "flow"
    stage: "planning"
    purpose: "Create execution plan"

    prompt: |
      You are at the PLANNING stage.

      GOAL: {{state.brain.objectives.primary_goal}}
      RESEARCH FINDINGS: {{state.data.findings}}
      VERIFIED FACTS: {{dredged_memory}}
      CONSTRAINTS: {{state.brain.constraints}}

      Create a concrete execution plan:
      1. Break down into actionable steps
      2. Identify which skills to use
      3. Define success criteria for each step
      4. Identify risks and mitigations

    output_schema:
      type: "object"
      required: ["steps", "ready_to_execute"]
      properties:
        steps:
          type: "array"
          items:
            type: "object"
            properties:
              step_id: { type: "string" }
              action: { type: "string" }
              skill: { type: "string" }
              success_criterion: { type: "string" }
              can_parallelize: { type: "boolean" }
        risks: { type: "array" }
        ready_to_execute: { type: "boolean" }

  - id: "execute"
    type: "flow"
    stage: "execution"
    purpose: "Execute the plan"

    prompt: |
      You are at the EXECUTION stage.

      PLAN: {{state.data.steps}}
      CURRENT_STEP: {{state.data.current_step}}
      COMPLETED_STEPS: {{state.data.completed_steps}}

      Execute the current step:
      1. Call necessary skills
      2. Capture the output
      3. Verify step success criterion
      4. Prepare for next step or handle failure

    parallel:
      spawn: true
      strategy: "by_step"     # Execute parallelizable steps together

  - id: "verify"
    type: "gate"
    stage: "verification"
    purpose: "Quality gate - check against success criteria"

    gate_config:
      criteria:
        - name: "deliverables_complete"
          check: "all(state.brain.deliverables, has_output)"
        - name: "constraints_satisfied"
          check: "all(state.brain.constraints.must_do, verified)"
        - name: "quality_threshold"
          check: "state.data.quality_score >= 0.8"

      on_pass: "finalize"
      on_fail: "execute"      # Retry execution
      max_retries: 3

  - id: "finalize"
    type: "flow"
    stage: "finalization"
    purpose: "Prepare final output"

    prompt: |
      You are at the FINALIZATION stage.

      DELIVERABLES: {{state.brain.deliverables}}
      EXECUTION_RESULTS: {{state.data.execution_results}}

      Prepare the final output:
      1. Format according to deliverable specifications
      2. Include provenance and sources
      3. Add confidence scores
      4. Summarize what was accomplished

  - id: "success"
    type: "terminal"
    stage: "complete"
    purpose: "Successful completion"

    on_reach:
      - action: "trigger_learning"
        outcome: "success"
      - action: "write_memory"
        content: "successful_patterns"

  - id: "failure"
    type: "terminal"
    stage: "complete"
    purpose: "Failed - unrecoverable"

    on_reach:
      - action: "trigger_learning"
        outcome: "failure"
      - action: "log_failure_mode"

  - id: "escalate"
    type: "terminal"
    stage: "complete"
    purpose: "Needs human intervention"

    on_reach:
      - action: "notify_human"
        message: "{{state.data.escalation_reason}}"

edges:
  # Happy path
  - id: "e_intake_research"
    from: "intake"
    to: "research"
    type: "laminar"
    guard: "state.data.ready_to_proceed == true"
    priority: 1

  - id: "e_intake_clarify"
    from: "intake"
    to: "intake"
    type: "turbulent"
    guard: "state.data.ready_to_proceed == false and state.counters.intake_retries < 2"
    priority: 2
    max_retries: 2
    on_traverse:
      - action: "ask_user"
        questions: "state.data.clarification_questions"

  - id: "e_research_sediment"
    from: "research"
    to: "sediment_research"
    type: "laminar"
    guard: "len(state.data.verified_facts) > 0"
    priority: 1

  - id: "e_sediment_plan"
    from: "sediment_research"
    to: "plan"
    type: "laminar"
    guard: "state.data.research_complete == true"
    priority: 1

  - id: "e_plan_execute"
    from: "plan"
    to: "execute"
    type: "laminar"
    guard: "state.data.ready_to_execute == true"
    priority: 1

  - id: "e_execute_verify"
    from: "execute"
    to: "verify"
    type: "laminar"
    guard: "state.data.execution_complete == true"
    priority: 1

  - id: "e_verify_finalize"
    from: "verify"
    to: "finalize"
    type: "laminar"
    guard: "state.data.verification_passed == true"
    priority: 1

  - id: "e_verify_retry"
    from: "verify"
    to: "execute"
    type: "turbulent"
    guard: "state.data.verification_passed == false and state.counters.verify_retries < 3"
    priority: 2
    max_retries: 3
    on_traverse:
      - action: "analyze_failure"
      - action: "adjust_approach"

  - id: "e_finalize_success"
    from: "finalize"
    to: "success"
    type: "laminar"
    guard: "state.data.finalized == true"
    priority: 1

  # Failure paths
  - id: "e_any_escalate"
    from: "*"
    to: "escalate"
    type: "laminar"
    guard: "state.data.needs_human == true"
    priority: 100

  - id: "e_max_retries_failure"
    from: "*"
    to: "failure"
    type: "laminar"
    guard: "state.counters.total_retries >= state.brain.execution.max_retries"
    priority: 99

# Relationship tracking for learning
relationships:
  - from: "research"
    to: "plan"
    type: "informs"
    weight: 1.0

  - from: "verified_facts"
    to: "execution"
    type: "grounds"
    weight: 1.0

  - from: "failure_at_verify"
    to: "plan_quality"
    type: "indicates"
    weight: 0.5
```

### 2.4 State Template (state.yaml)

```yaml
state:
  brain_id: "{{brain.id}}"
  run_id: "<generated at runtime>"
  started_at: null

  # Current position
  current_node: null
  stage: "not_started"

  # User input
  user_request: ""

  # Working data
  data: {}

  # Counters for loop control
  counters:
    total_steps: 0
    node_visits: {}
    retries: {}
    total_retries: 0

  # Parallel task tracking
  parallel:
    active_tasks: []
    completed_tasks: []
    failed_tasks: []

  # Audit trail
  audit: []

  # Learning signals
  signals:
    successes: []
    failures: []
    improvements: []
```

---

## Phase 3: Brain Execution

When running a brain:

### 3.1 Initialization

```python
def initialize_run(brain_path: Path, user_request: str) -> State:
    brain = load_brain(brain_path)
    graph = load_graph(brain_path)

    state = State(
        brain_id=brain.id,
        run_id=generate_uuid(),
        started_at=now(),
        current_node=graph.start_node,
        stage="intake",
        user_request=user_request,
        data={},
        counters=Counters(),
        parallel=ParallelState(),
        audit=[],
        signals=Signals()
    )

    return state
```

### 3.2 Execution Loop

```
WHILE current_node NOT IN terminal_nodes AND steps < max_steps:

    1. GET node = graph.nodes[current_node]

    2. PREPARE context:
       - Dredge memory (if node.memory.dredge)
       - Gather state data
       - Inject available skills

    3. EXECUTE node by type:
       - flow: Call LLM with prompt, validate output, apply state_writes
       - tributary: Execute skill/tool
       - delta: Merge parallel results
       - sediment: Write to memory
       - gate: Evaluate criteria

    4. HANDLE parallel tasks:
       IF node.parallel.spawn AND output.parallel_tasks:
           FOR task IN output.parallel_tasks:
               spawn_parallel_task(task)
           IF any(task.wait):
               await_parallel_completion()
               merge_results()

    5. CHOOSE next edge:
       - Evaluate guards on all outgoing edges
       - Select highest priority valid edge
       - Handle turbulent retries
       - Apply on_traverse actions

    6. UPDATE state:
       - Increment counters
       - Append audit event
       - Update current_node

    7. CHECK for learning signals:
       - Record successes/failures
       - Note potential improvements

RETURN run_result
```

### 3.3 Parallel Task Execution

When a node spawns parallel tasks:

```yaml
parallel_task:
  task_id: "task_001"
  skill: "web_search"
  instruction: "Search for X"
  context:
    query: "{{state.data.search_query}}"
  wait: true
  timeout: 60
  on_complete:
    merge_to: "state.data.search_results"
  on_fail:
    action: "log_and_continue"
```

The controller:
1. Spawns each task as independent sub-agent
2. Provides context from state
3. Collects results
4. Merges into state at specified paths

### 3.4 Skill Invocation

When a node needs a skill:

```yaml
skill_call:
  skill: "hubspot"
  action: "search_contacts"
  parameters:
    query: "{{state.data.contact_query}}"
  output_to: "state.data.contacts"
  on_error: "retry_with_backoff"
```

---

## Phase 4: Learning and Evolution

After each run, trigger learning.

### 4.1 Run Analysis

Analyze the completed run:

```yaml
analysis:
  run_id: "<uuid>"
  outcome: "success|failure|escalated"

  metrics:
    total_steps: N
    time_elapsed: Ns
    retries_used: N
    parallel_tasks: N
    memory_writes: N

  patterns:
    successful_paths:
      - path: ["intake", "research", "plan", "execute", "verify", "success"]
        frequency: N
    failure_points:
      - node: "verify"
        failure_type: "quality_gate"
        frequency: N
    bottlenecks:
      - node: "research"
        avg_time: Ns

  signals:
    - type: "edge_underused"
      edge: "e_research_parallel"
      suggestion: "increase priority"
    - type: "node_overloaded"
      node: "execute"
      suggestion: "split into sub-nodes"
    - type: "guard_too_strict"
      edge: "e_verify_finalize"
      suggestion: "lower threshold"
```

### 4.2 Change Proposals

Generate proposals based on analysis:

```yaml
proposal:
  proposal_id: "<uuid>"
  created_at: "<timestamp>"
  based_on_runs: ["<run_id1>", "<run_id2>"]

  changes:
    - type: "update_edge_priority"
      target: "e_research_parallel"
      old_value: 3
      new_value: 2
      reason: "Underused but successful when taken"
      auto_apply: true

    - type: "update_guard_threshold"
      target: "e_verify_finalize"
      old_guard: "state.data.quality_score >= 0.9"
      new_guard: "state.data.quality_score >= 0.85"
      reason: "Too strict, causing unnecessary retries"
      auto_apply: false
      requires_approval: true

    - type: "add_relationship"
      from: "parallel_research"
      to: "faster_completion"
      type: "correlates_with"
      weight: 0.7
      auto_apply: true

    - type: "update_prompt"
      target: "node.execute"
      section: "instructions"
      change: "Add explicit error handling step"
      auto_apply: false
      requires_approval: true
```

### 4.3 Automatic Application

For approved auto-apply changes:

```python
def apply_changes(brain_path: Path, proposals: List[Proposal]) -> None:
    graph = load_graph(brain_path)
    applied = []

    for proposal in proposals:
        for change in proposal.changes:
            if change.auto_apply or change.approved:
                if change.type == "update_edge_priority":
                    edge = graph.edges[change.target]
                    edge.priority = change.new_value
                    applied.append(change)

                elif change.type == "add_relationship":
                    graph.relationships.append(Relationship(
                        from_=change.from,
                        to=change.to,
                        type=change.type,
                        weight=change.weight
                    ))
                    applied.append(change)

                # ... handle other change types

    save_graph(brain_path, graph)
    log_applied_changes(brain_path, applied)
```

### 4.4 Relationship Learning

Track and update relationships:

```yaml
relationship_updates:
  - relationship: "research -> plan"
    observation: "thorough_research leads to fewer plan revisions"
    weight_change: +0.1
    new_weight: 1.1

  - relationship: "parallel_tasks -> completion_time"
    observation: "3+ parallel tasks correlate with 40% faster completion"
    weight_change: +0.2
    new_weight: 0.9

  - relationship: "verify_failure -> plan_quality"
    observation: "verify failures often trace back to rushed planning"
    action: "add turbulent edge from verify back to plan (not just execute)"
```

---

## Phase 5: Brain Operation Commands

Use these commands when operating a brain:

### Create a New Brain
```
/brain create <name>
```
Triggers Phase 1 (Discovery) → Phase 2 (Creation)

### Run a Brain
```
/brain run <name> "<user_request>"
```
Triggers Phase 3 (Execution)

### View Brain Status
```
/brain status <name>
```
Shows current state, recent runs, pending proposals

### Apply Learning
```
/brain learn <name>
```
Triggers Phase 4 (Learning) on recent runs

### View Proposals
```
/brain proposals <name>
```
Shows pending change proposals needing approval

### Approve Changes
```
/brain approve <name> <proposal_id>
```
Approves and applies a pending proposal

### Evolve Brain
```
/brain evolve <name>
```
Full learning cycle: analyze → propose → apply approved

---

## Appendix: Node Type Reference

| Type | Purpose | LLM Call | State Writes | Memory | Parallel |
|------|---------|----------|--------------|--------|----------|
| `prime` | Initialize, set context | Yes | Yes | Dredge only | No |
| `flow` | Main reasoning | Yes | Yes | Dredge | Can spawn |
| `tributary` | Tool/skill execution | No | Yes | No | Isolated |
| `delta` | Merge parallel results | Optional | Yes | No | Receives |
| `sediment` | Write to memory | No | Counters only | Write | No |
| `gate` | Quality check | No | Pass/fail | No | No |
| `terminal` | End state | No | No | Final write | No |

## Appendix: Edge Type Reference

| Type | Purpose | Retries | On Traverse |
|------|---------|---------|-------------|
| `laminar` | Happy path forward | No | Optional actions |
| `turbulent` | Retry/correction loop | Yes (max_retries) | Adjust + retry |
| `dredging` | Memory retrieval | No | Inject context |
| `permeable` | Cross-agent read | No | Sync state |

## Appendix: Guard Expression Syntax

Guards are Python-like expressions evaluated against state:

```python
# Simple checks
"state.data.ready == true"
"state.data.quality_score >= 0.8"

# List operations
"len(state.data.errors) == 0"
"'critical' not in state.data.error_types"

# Counter checks
"state.counters.retries.get('verify', 0) < 3"

# Complex conditions
"state.data.research_complete and len(state.data.open_questions) == 0"
```

---

## Quick Start

When a user says "create a brain for X", follow this flow:

1. **Interview**: Ask the discovery questions, adapt based on responses
2. **Extract**: Identify objectives, constraints, workflow, success criteria
3. **Confirm**: Present the extracted understanding, get approval
4. **Create**: Generate brain folder with all files
5. **Test**: Run a simple test case
6. **Refine**: Adjust based on test results
7. **Deploy**: Brain is ready for use

Remember: The brain should be SELF-IMPROVING. After each run:
- Analyze what worked and what didn't
- Propose changes to the graph
- Apply safe changes automatically
- Queue risky changes for approval
- Update relationships and weights
- Write learnings to memory
