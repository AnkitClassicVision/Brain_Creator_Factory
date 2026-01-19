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
├── claude.md            # ORCHESTRATOR - Entry point, thin flow control
├── brain.yaml           # Manifest: rules, constraints, config
├── graph.yaml           # Execution graph: nodes, edges, gates
├── state.yaml           # Runtime state template
├── memory.jsonl         # Long-term memory (starts empty)
├── config/              # Business constants
│   └── constants.yaml   # Thresholds, minimums, critical items
├── references/          # Required specs and templates
├── scripts/             # Validation scripts (Python)
├── skills/              # Brain-specific skills
│   └── _index.yaml      # Skill registry
├── runs/                # Execution history
└── evolution/           # Learning and changes
    ├── proposals.jsonl  # Proposed changes
    └── applied.jsonl    # Applied changes
```

### 2.1.1 claude.md - The Orchestrator (REQUIRED)

Every brain MUST have a `claude.md` file that serves as the thin orchestration layer:

**Purpose:**
- Entry point for the LLM (trigger: "start")
- Flow control only - no implementation details
- References other files for specifics
- Directs LLM to write code when computation is needed

**Structure:**
```markdown
# {Brain Name} - Orchestrator

## TRIGGER
Say **"start"** to begin.

## Architecture
[Diagram showing file relationships]

## Execution Model
You write code. You run code. You verify results.

## Phases
[Table: Phase | Purpose | Instructions | Gate]

## Stop Rules
[Reference to brain.yaml constraints]

## Checkpoints
[How to update state.yaml at each gate]

## Code Execution Pattern
[When/how to write and execute scripts]

## File Outputs
[Expected deliverables]
```

**Key Principles:**
- **Thin**: Only orchestration, no implementation details
- **Reference-based**: Points to other files for specifics
- **Code-directed**: Tells LLM to write code for computations
- **Gate-aware**: Tracks progress via state.yaml

### 2.2 Brain Manifest (brain.yaml)

```yaml
brain:
  id: "<uuid>"
  name: "<brain_name>"
  version: "1.0.0"
  created_at: "<timestamp>"
  updated_at: "<timestamp>"
  purpose: "<from discovery>"

objectives:
  primary_goal: "<from discovery>"
  objectives: []
  deliverables: []

constraints:
  must_do: []
  must_not: []

learning:
  enabled: true
  mode: "auto_safe"
  auto_update:
    edge_priorities: true
    relationship_weights: true
    guard_thresholds: false
    node_prompts: false
    add_nodes: false
    remove_nodes: false
    add_edges: false
    remove_edges: false
  requires_approval:
    - "structural_changes"
    - "new_skills"
    - "constraint_changes"
  feedback_sources:
    - "outcome"
    - "user_feedback"
    - "quality_scores"

execution:
  max_steps: 100
  max_parallel: 5
  timeout_seconds: 3600
  max_retries: 3

skills:
  available: []
  auto_discover: true

metadata:
  tags: []
  notes: ""
```

### 2.3 LLM Enforcement Logic (CRITICAL - Required for All Brains)

LLMs have systematic blind spots that cause workflow failures. Every brain MUST include enforcement logic to prevent these failures.

#### 2.3.1 The 7 LLM Blind Spots

Understand WHY enforcement is necessary:

| Blind Spot | Description | Prevention |
|------------|-------------|------------|
| **Helpfulness Bias** | LLM improvises when blocked instead of stopping | STOP rules with explicit halt conditions |
| **Format Blindness** | LLM simplifies complex structures (HTML→markdown) | Forbidden patterns list, format validation |
| **Partial Completion** | LLM declares "done" when "good enough" | Explicit deliverable checklists, zero-tolerance |
| **Business Rule Ignorance** | LLM applies pure math without business constraints | Business constants file, minimum enforcement |
| **Implicit Assumptions** | LLM accepts unusual values without questioning | Threshold validation, STOP on anomalies |
| **Output Trust** | LLM assumes exit code 0 = valid output | File existence + size verification |
| **Equal Treatment** | LLM treats all items equally, misses critical ones | Critical item marking, explicit priority |

#### 2.3.2 Required STOP Rules (constraints.stop_rules)

Every brain MUST define explicit STOP conditions. The LLM MUST halt and ask the user when these conditions are met:

```yaml
constraints:
  # STOP RULES - When to halt and ask user (CRITICAL)
  stop_rules:
    # === TEMPLATE/DEPENDENCY STOP RULES ===
    - condition: "Required template/reference file is missing"
      action: "STOP and ask user - DO NOT generate from scratch"
      reason: "Generated content lacks tested styling/structure"

    - condition: "Template does not match required specification"
      action: "STOP and ask user - template must be updated"
      reason: "Wrong structure causes rendering/format errors"

    # === DATA QUALITY STOP RULES ===
    - condition: "Unknown/unclassified data exceeds threshold (e.g., >10%)"
      action: "STOP and ask user - data quality issue"
      reason: "High unknowns indicate mapping or data problems"

    - condition: "Calculated values fall below business minimums"
      action: "STOP and apply minimum, then confirm with user"
      reason: "Business minimums are non-negotiable requirements"

    - condition: "Values are outside expected range (anomaly detection)"
      action: "STOP and ask user - verify input data"
      reason: "Unusual values may indicate data entry errors"

    # === VALIDATION STOP RULES ===
    - condition: "Two independent calculations disagree beyond tolerance"
      action: "STOP and reconcile - calculation error likely"
      reason: "Methods should agree within defined tolerance"

    - condition: "Any output file size is 0 bytes"
      action: "STOP and escalate - generation failed"
      reason: "Empty outputs will break downstream processes"

    - condition: "Quality grade below acceptable threshold"
      action: "STOP and ask user before proceeding"
      reason: "Poor grade may require special handling"
```

#### 2.3.3 Required DO NOT Rules (constraints.must_not)

Every brain MUST define forbidden actions with explicit consequences:

```yaml
constraints:
  must_not:
    # === NEVER IMPROVISE ===
    - "Generate content from scratch when template/reference is missing - ALWAYS stop and ask"
    - "Use simplified format when complex format is required (e.g., markdown table when HTML required)"
    - "Skip any validation or verification step"
    - "Proceed with template/reference that doesn't match specification"
    - "Guess or assume values for missing data - always ask user"
    - "Mark a phase complete if validation fails - FIX first"

    # === BUSINESS RULES ===
    - "Use values below defined minimums without explicit user approval"
    - "Calculate outputs for inputs below required thresholds"
    - "Show internal formulas, rates, or breakdowns in client-facing output"

    # === DATA QUALITY ===
    - "Proceed with ambiguous data semantics without confirmation"
    - "Proceed with quality metrics below acceptable thresholds without user confirmation"

    # === OUTPUT RULES ===
    - "Skip visual/manual verification of critical outputs"
    - "Deliver output with unreplaced template variables ({{PLACEHOLDER}} tokens)"
    - "Trust command exit code without verifying output files exist and have size > 0"
    - "Skip any QA step - all QA is mandatory"
```

#### 2.3.4 Required MUST DO Rules (constraints.must_do)

Every brain MUST define mandatory actions:

```yaml
constraints:
  must_do:
    # === PRE-FLIGHT CHECKS ===
    - "Run pre-flight checks before starting main workflow"
    - "STOP and ask user if required templates/references are missing"
    - "Verify templates match required specification before proceeding"
    - "Load business constants config and validate all values present"

    # === DURING EXECUTION ===
    - "Apply business minimums and log any enforcement: 'Applied minimum: calculated $X, set to $Y'"
    - "Run deterministic validation checks before output generation"
    - "Verify all dependent files exist and have size > 0"

    # === QA (mandatory - never skip) ===
    - "Run visual verification on all critical outputs before marking complete"
    - "Perform automated + manual QA before delivery"
    - "Verify zero unreplaced {{PLACEHOLDER}} tokens after template population"
    - "Verify all image/file paths resolve to existing files"
```

#### 2.3.5 Required Business Constants (config/ directory)

Every brain that involves business logic MUST have a config file with defined constants:

```yaml
# config/<workflow>_constants.yaml
# Example structure

# Business Minimums - values that cannot go below these thresholds
minimums:
  SOME_MINIMUM: 100        # With comment explaining what this is

# Thresholds - quality and validation thresholds
thresholds:
  UNKNOWN_DATA_MAX_PCT: 10      # STOP if unknown data > 10%
  RECONCILIATION_TOLERANCE: 1.0  # Max allowed diff between methods

# Required Outputs - files that must be generated
required_outputs:
  - "output_file_1.ext"
  - "output_file_2.ext"

# Critical Items - items requiring extra validation
critical_items:
  - item: 1
    name: "Item Name"
    required_fields: ["field1", "field2"]
    validation: ["validation rule 1", "validation rule 2"]
```

#### 2.3.6 Brain Creation Checklist

When creating ANY brain, verify these requirements:

```markdown
## Brain Creation Checklist

### Orchestrator (claude.md) - REQUIRED
- [ ] Has trigger instruction ("start")
- [ ] Has architecture diagram showing file relationships
- [ ] Has execution model (code execution directive)
- [ ] Has phase table with gates
- [ ] References brain.yaml for constraints
- [ ] References state.yaml for tracking
- [ ] Is THIN - only orchestration, no implementation

### Manifest (brain.yaml)
- [ ] Has `constraints.stop_rules` section with explicit halt conditions
- [ ] Has `constraints.must_not` section with forbidden actions
- [ ] Has `constraints.must_do` section with mandatory actions
- [ ] Has `config` section referencing business constants
- [ ] Critical items are explicitly listed
- [ ] Stop rule semantics are clear (HALT/CONFIRM/LOG)

### Graph (graph.yaml)
- [ ] Has Phase 0: Pre-flight validation nodes
- [ ] Pre-flight checks template/reference existence
- [ ] Pre-flight validates template/reference structure
- [ ] Pre-flight loads and validates business constants
- [ ] Pre-flight has BLOCKED terminal for failed validation
- [ ] All phases have validation gates before completion
- [ ] Every phase transition has explicit guard condition
- [ ] Toll gates prevent phase skipping

### State (state.yaml)
- [ ] Has `preflight` section tracking validation status
- [ ] Has `validation` section tracking what's been verified
- [ ] Has `config_loaded` tracking business constants load status
- [ ] Critical items have individual validation flags
- [ ] Each phase has completion tracking fields

### Config Directory
- [ ] Has `config/constants.yaml` with all business rules
- [ ] Constants include minimums, thresholds, required outputs
- [ ] Constants include critical item definitions
- [ ] All values have explanatory comments

### Red Team Validation - REQUIRED
- [ ] Red team analysis completed
- [ ] All CRITICAL findings fixed
- [ ] All HIGH findings fixed
- [ ] Toll gates verified at every phase boundary
- [ ] Sign-off documented in evolution/red_team.md
```

### 2.4 Execution Graph (graph.yaml)

```yaml
graph:
  name: "<brain_name>"
  version: "1.0.0"

# Entry and exit - MUST start with pre-flight validation
start_node: "preflight_check"
terminal_nodes: ["success", "failure", "escalate", "preflight_blocked"]
```

#### 2.4.1 Required Pre-flight Phase (Phase 0)

Every brain MUST include a pre-flight validation phase that runs BEFORE the main workflow:

```yaml
# === PHASE 0: PRE-FLIGHT VALIDATION ===
# These nodes run BEFORE any main workflow processing

nodes:
  # Check that required templates/references exist
  - id: "preflight_check"
    type: "gate"
    stage: "preflight"
    purpose: "Verify all required templates and references exist"
    gate_config:
      criteria:
        - name: "templates_exist"
          check: "all required templates exist on filesystem"
        - name: "references_exist"
          check: "all required references exist on filesystem"
      on_pass: "preflight_validate"
      on_fail: "preflight_missing"

  # Validate structure of templates/references
  - id: "preflight_validate"
    type: "gate"
    stage: "preflight"
    purpose: "Verify templates match required specification"
    gate_config:
      criteria:
        - name: "template_structure"
          check: "template contains required elements/patterns"
        - name: "no_forbidden_patterns"
          check: "template does not contain forbidden patterns"
      on_pass: "preflight_config"
      on_fail: "preflight_invalid"

  # Load and validate business constants
  - id: "preflight_config"
    type: "tributary"
    stage: "preflight"
    purpose: "Load business constants and validate completeness"
    skill: "file_read"
    parameters:
      path: "config/<workflow>_constants.yaml"
    state_writes:
      - path: "config"
        from: "output"
      - path: "config_loaded"
        value: true

  # Pre-flight gate - all checks must pass
  - id: "preflight_gate"
    type: "gate"
    stage: "preflight"
    purpose: "Final pre-flight validation before main workflow"
    gate_config:
      criteria:
        - name: "all_preflight_passed"
          check: "state.preflight.all_valid == true"
        - name: "config_loaded"
          check: "state.config_loaded == true"
      on_pass: "intake"  # Proceed to main workflow
      on_fail: "preflight_blocked"

  # Terminal: Missing dependencies
  - id: "preflight_missing"
    type: "terminal"
    stage: "preflight"
    purpose: "STOP - Required dependencies missing"
    terminal_config:
      outcome: "blocked"
      reason: "missing_dependencies"
      message: "Required templates or references are missing. DO NOT proceed without them."
      action: "ask_user"

  # Terminal: Invalid structure
  - id: "preflight_invalid"
    type: "terminal"
    stage: "preflight"
    purpose: "STOP - Template/reference structure invalid"
    terminal_config:
      outcome: "blocked"
      reason: "invalid_structure"
      message: "Template does not match required specification. DO NOT use wrong structure."
      action: "ask_user"

  # Terminal: Pre-flight blocked
  - id: "preflight_blocked"
    type: "terminal"
    stage: "preflight"
    purpose: "STOP - Pre-flight validation failed"
    terminal_config:
      outcome: "blocked"
      reason: "preflight_failed"
      message: "Pre-flight validation failed. Review and fix before proceeding."
      action: "ask_user"

edges:
  # Pre-flight flow
  - id: "e_preflight_check_validate"
    from: "preflight_check"
    to: "preflight_validate"
    type: "laminar"
    guard: "state.preflight.dependencies_exist == true"
    priority: 1

  - id: "e_preflight_check_missing"
    from: "preflight_check"
    to: "preflight_missing"
    type: "laminar"
    guard: "state.preflight.dependencies_exist == false"
    priority: 2

  - id: "e_preflight_validate_config"
    from: "preflight_validate"
    to: "preflight_config"
    type: "laminar"
    guard: "state.preflight.structure_valid == true"
    priority: 1

  - id: "e_preflight_validate_invalid"
    from: "preflight_validate"
    to: "preflight_invalid"
    type: "laminar"
    guard: "state.preflight.structure_valid == false"
    priority: 2

  - id: "e_preflight_config_gate"
    from: "preflight_config"
    to: "preflight_gate"
    type: "laminar"
    guard: "state.config_loaded == true"
    priority: 1

  - id: "e_preflight_gate_intake"
    from: "preflight_gate"
    to: "intake"
    type: "laminar"
    guard: "state.preflight.all_valid == true"
    priority: 1

  - id: "e_preflight_gate_blocked"
    from: "preflight_gate"
    to: "preflight_blocked"
    type: "laminar"
    guard: "state.preflight.all_valid == false"
    priority: 2
```

#### 2.4.2 Main Workflow Nodes

After pre-flight, the main workflow begins:

```yaml
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
      - path: "understood_request"
        from: "output.understood_request"
      - path: "approach"
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

### 2.5 State Template (state.yaml)

Every brain state MUST include preflight tracking and validation sections:

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

  # ═══════════════════════════════════════════════════════════════════
  # PRE-FLIGHT VALIDATION STATE (REQUIRED)
  # ═══════════════════════════════════════════════════════════════════
  preflight:
    # Track dependency checks
    dependencies_exist: false
    missing_dependencies: []

    # Track structure validation
    structure_valid: false
    structure_errors: []
    has_forbidden_patterns: false
    forbidden_patterns_found: []

    # Overall preflight status
    all_valid: false

  # ═══════════════════════════════════════════════════════════════════
  # BUSINESS CONSTANTS (loaded from config file)
  # ═══════════════════════════════════════════════════════════════════
  config_loaded: false
  config: {}

  # ═══════════════════════════════════════════════════════════════════
  # VALIDATION TRACKING (REQUIRED)
  # Track what has been validated to prevent skipping
  # ═══════════════════════════════════════════════════════════════════
  validation:
    # Track minimums enforcement
    minimums_applied: {}

    # Track output verification
    outputs_verified: {}

    # Track critical items (customize per brain)
    critical_items_validated: {}

    # Track QA completion
    qa_completed:
      automated: false
      visual: false

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

#### 2.5.1 State Validation Requirements

Every brain state MUST track:

| Section | Purpose | Why Required |
|---------|---------|--------------|
| `preflight` | Pre-flight validation status | Prevents starting work with invalid dependencies |
| `config_loaded` | Business constants load status | Ensures rules are loaded before calculations |
| `config` | Loaded business constants | Provides runtime access to thresholds/minimums |
| `validation.minimums_applied` | Which minimums were enforced | Audit trail for business rule enforcement |
| `validation.outputs_verified` | Which outputs were verified | Prevents trusting exit codes without file checks |
| `validation.critical_items_validated` | Critical item validation flags | Ensures extra validation on high-priority items |
| `validation.qa_completed` | QA completion status | Prevents skipping mandatory QA steps |

---

## Phase 2.5: Red Team Validation (REQUIRED)

After creating a brain, RED TEAM it to find failure points before deployment.

### 2.5.1 Purpose

LLMs have systematic blind spots that cause workflow failures. Red teaming identifies:
- Ambiguous instructions that could be misinterpreted
- Complex multi-step tasks where steps might be skipped
- Edge cases not covered by instructions
- Places where the LLM might hallucinate or make assumptions
- Validation gaps where errors could propagate
- Missing toll gates between phases

### 2.5.2 Red Team Process

Run the `/agent-team` skill or equivalent multi-AI analysis on the brain:

```
Red team the process in brains/<brain_name>/ - analyze where an LLM might fail to follow directions.

Look at claude.md, brain.yaml, graph.yaml, state.yaml, and any workflow files to identify:
1. Ambiguous instructions that could be misinterpreted
2. Complex multi-step tasks where the LLM might skip steps
3. Edge cases not covered by instructions
4. Places where the LLM might hallucinate or make assumptions
5. Validation gaps where errors could propagate
```

### 2.5.3 Red Team Checklist

After red teaming, verify and fix:

```markdown
## Red Team Validation Checklist

### Ambiguity Check
- [ ] All STOP conditions have clear semantics (HALT vs CONFIRM vs LOG)
- [ ] All instructions use specific, measurable criteria
- [ ] No "as needed" or "if appropriate" language
- [ ] Code execution requirements are explicit (write code, don't calculate in-context)

### Step Completeness
- [ ] Each phase has a gate that blocks progression until complete
- [ ] Multi-step tasks have individual checkpoints
- [ ] Dependencies are explicitly tracked in state.yaml
- [ ] No phase can be skipped without failing a gate

### Edge Cases
- [ ] Zero/empty input handling defined
- [ ] Error recovery paths exist
- [ ] Threshold boundary behavior specified (> vs >=)
- [ ] Multi-location/multi-input aggregation logic defined

### Hallucination Prevention
- [ ] All computations directed to code execution
- [ ] Business constants loaded from config (not hardcoded)
- [ ] Quality grades have explicit thresholds
- [ ] No "approximately" or "around" language

### Validation Gates
- [ ] Pre-flight validates all dependencies exist
- [ ] Each phase has entry and exit gates
- [ ] Output files verified for existence AND size
- [ ] Placeholders verified as zero remaining
- [ ] Critical items have explicit validation flags

### Toll Gates (Phase Boundaries)
- [ ] Gate between discovery and ingestion
- [ ] Gate between analysis and computation
- [ ] Gate between computation and output generation
- [ ] Gate between output and delivery
- [ ] All gates update state.yaml before allowing progression
```

### 2.5.4 Fixing Red Team Findings

For each finding, update the appropriate file:

| Finding Type | Fix Location |
|--------------|--------------|
| Ambiguous instruction | `claude.md` or phase instructions |
| Missing gate | `graph.yaml` edges with guards |
| Missing validation | `state.yaml` tracking fields |
| Business logic gap | `config/constants.yaml` |
| Stop condition unclear | `brain.yaml` stop_rules |

### 2.5.5 Red Team Sign-Off

A brain is NOT ready for deployment until:

1. Red team analysis completed
2. All HIGH severity findings fixed
3. All toll gates verified present
4. State tracking covers all validation points
5. Code execution patterns documented

Document findings in `brains/<brain_name>/evolution/red_team.md`:

```markdown
# Red Team Analysis - {Brain Name}

## Date: {date}
## Analyst: {who ran the analysis}

## Findings Summary
| Severity | Count | Fixed |
|----------|-------|-------|
| CRITICAL | X | X |
| HIGH | X | X |
| MEDIUM | X | X |
| LOW | X | X |

## Critical Findings
1. {Finding} - {Fix applied}

## High Findings
1. {Finding} - {Fix applied}

## Toll Gate Verification
- [ ] Phase 0 → Phase 1: {gate description}
- [ ] Phase 1 → Phase 2: {gate description}
...

## Sign-Off
Brain ready for deployment: YES/NO
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
"state.data.get('ready', False) == True"
"state.data.get('quality_score', 0) >= 0.8"

# List operations
"len(state.data.get('errors', [])) == 0"
"'critical' not in state.data.get('error_types', [])"

# Counter checks
"state.counters.retries.get('verify', 0) < 3"

# Complex conditions
"state.data.get('research_complete', False) == True and len(state.data.get('open_questions', [])) == 0"
```

---

## Quick Start

When a user says "create a brain for X", follow this flow:

1. **Interview**: Ask the discovery questions, adapt based on responses
2. **Extract**: Identify objectives, constraints, workflow, success criteria
3. **Confirm**: Present the extracted understanding, get approval
4. **Create**: Generate brain folder with all files INCLUDING claude.md orchestrator
5. **Red Team**: Run red team analysis to find failure points (REQUIRED)
6. **Fix**: Address all CRITICAL and HIGH findings from red team
7. **Verify Gates**: Confirm toll gates exist at every phase boundary
8. **Test**: Run a simple test case
9. **Refine**: Adjust based on test results
10. **Sign-Off**: Document red team findings and verification in evolution/red_team.md
11. **Deploy**: Brain is ready for use

### Brain Files Creation Order

1. `brain.yaml` - Define constraints, rules, objectives
2. `state.yaml` - Define all tracking fields
3. `graph.yaml` - Define nodes, edges, gates
4. `config/constants.yaml` - Define business constants
5. `claude.md` - Create thin orchestration layer (LAST - references all above)
6. **RED TEAM** - Analyze for failure points
7. Fix findings and verify gates

Remember: The brain should be SELF-IMPROVING. After each run:
- Analyze what worked and what didn't
- Propose changes to the graph
- Apply safe changes automatically
- Queue risky changes for approval
- Update relationships and weights
- Write learnings to memory
