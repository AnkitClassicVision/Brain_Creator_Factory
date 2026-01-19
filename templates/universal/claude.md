# {{brain_name}} - Orchestrator

## TRIGGER
Say **"start"** to begin.

---

## Architecture

```
claude.md          <- YOU ARE HERE (orchestration only)
    |
    v
brain.yaml         <- Rules: stop_rules, must_do, must_not, config
    |
    v
state.yaml         <- Progress tracking (update as you go)
    |
    v
graph.yaml         <- Traversal logic (phases, gates, edges)
    |
    v
config/            <- Business constants, thresholds
```

---

## Execution Model

**You write code. You run code. You verify results.**

When a phase requires computation:
1. Write a Python script to `scripts/`
2. Execute it
3. Capture output to state
4. Verify against constraints

Do NOT attempt complex calculations in-context. Write code.

---

## Phases

| Phase | Purpose | Instructions | Gate |
|-------|---------|--------------|------|
| 0 | Pre-flight | Validate dependencies exist | `preflight.all_checks_passed` |
| 1 | {{phase_1_name}} | {{phase_1_purpose}} | `{{phase_1_gate}}` |
| 2 | {{phase_2_name}} | {{phase_2_purpose}} | `{{phase_2_gate}}` |
| 3 | {{phase_3_name}} | {{phase_3_purpose}} | `{{phase_3_gate}}` |
| ... | ... | ... | ... |
| N | Deliverables | Output summary, list files | `deliverables.complete` |

**Detailed instructions**: Reference `graph.yaml` nodes or external workflow files.

---

## Stop Rules

Read `brain.yaml` -> `constraints.stop_rules` before each phase.

If any condition is true: **STOP and ask user**.

Key stops (customize per brain):
- Template/reference missing -> STOP (do not generate)
- Values below business minimums -> apply minimum, confirm with user
- Validation methods disagree -> reconcile before proceeding
- Data quality issues -> ask user before proceeding
- Output file size = 0 -> regenerate

---

## Toll Gates (Phase Boundaries)

At each phase boundary, verify the gate condition before proceeding:

```yaml
# Phase N -> Phase N+1 requires:
state.phase_N.gate_field == true

# Update state.yaml BEFORE attempting transition
state:
  current_node: "phase_N"
  phase_N:
    gate_field: true  # Only set when phase truly complete
```

Do NOT proceed to next phase until gate condition is true.

---

## Checkpoints

At each phase boundary, update `state.yaml`:

```yaml
# Example after Phase 1
state:
  current_node: "phase_1"
  stage: "phase_1_complete"
  phase_1:
    # ... phase-specific fields
    gate_field: true
```

---

## Code Execution Pattern

For computational phases:

```python
# 1. Write script to file
scripts/calculate_{{phase}}.py

# 2. Execute
python scripts/calculate_{{phase}}.py --input data.csv --output manifest.json

# 3. Verify output
- File exists
- Size > 0
- Values within expected ranges

# 4. Update state
state.{{phase}}.computed = true
```

---

## Validation Requirements

Before marking any phase complete:

1. **File outputs exist** - Check file presence
2. **File outputs valid** - Check size > minimum threshold
3. **Values in range** - Check against config/constants.yaml
4. **Dependencies met** - Previous gates all passed
5. **State updated** - All tracking fields set

---

## File Outputs

All outputs to `output/<run_id>/`:

```
output/<run_id>/
  # Customize per brain
  data_output.csv         # Processed data
  manifest.json           # Computed values
  deliverable.ext         # Final output
```

---

## Quick Reference

### Constraints Location
- Stop rules: `brain.yaml` -> `constraints.stop_rules`
- Must do: `brain.yaml` -> `constraints.must_do`
- Must not: `brain.yaml` -> `constraints.must_not`
- Business constants: `config/constants.yaml`

### State Tracking
- Current position: `state.yaml` -> `current_node`, `stage`
- Phase progress: `state.yaml` -> `{phase}.{field}`
- Validation flags: `state.yaml` -> `validation.*`

### References
- Graph traversal: `graph.yaml`
- Business constants: `config/constants.yaml`

---

## Error Handling

- Critical failure -> STOP, report, wait for user
- Recoverable error -> retry with adjusted approach (max 3 retries)
- Data quality issue -> flag, ask user to confirm

---

## Flow Summary

```
start
  |
  v
[0] Pre-flight ──[fail]──> STOP (ask user)
  |
  [pass]
  v
[1] Phase 1 ──[gate]──> [2] Phase 2
  |                          |
  v                          v
[3] Phase 3 ──[gate]──> ... ──> [N] Deliverables
  |
  v
DONE
```
