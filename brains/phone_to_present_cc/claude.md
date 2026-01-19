# Phone to Present CC - Orchestrator

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
```

---

## Execution Model

**You write code. You run code. You verify results.**

When a phase requires computation (FTE, pricing, Monte Carlo):
1. Write a Python script
2. Execute it
3. Capture output to state
4. Verify against constraints

Do NOT attempt complex calculations in-context. Write code.

---

## Phases

| Phase | Purpose | Instructions | Gate |
|-------|---------|--------------|------|
| 0 | Pre-flight | Validate templates, references, config exist | `preflight.all_checks_passed` |
| 1 | Discovery | Find data, gather client info, confirm hours | `discovery.confirmed` |
| 2 | Ingestion | Standardize data, map columns, quality check | `ingestion.quality_passed` |
| 3 | Analysis | KPIs from OPEN HOURS only, grade | `analysis.kpis_computed` |
| 4 | Concurrency | CDF + Monte Carlo FTE (write code) | `concurrency.fte_reconciled` |
| 5 | Pricing | Apply formulas + minimums (write code) | `pricing.verified` |
| 6 | Charts | Generate PNGs, verify size > 0 | `charts.all_exist` |
| 7 | Presentation | Populate template, v4 HTML for Slide 18 | `presentation.placeholders_zero` |
| 7b | QA | Visual verification of critical slides | `qa.all_pass` |
| 8 | Deliverables | Output summary, list files | `deliverables.complete` |

**Detailed instructions**: `../phone_to_present/workflow/phase{N}_{name}.md`

---

## Stop Rules

Read `brain.yaml` → `constraints.stop_rules` before each phase.

If any condition is true: **STOP and ask user**.

Key stops:
- Template missing → STOP (do not generate)
- Pricing below minimum → apply minimum, confirm with user
- FTE methods differ > 1.0 → reconcile before proceeding
- Unknown disposition > 10% → data quality issue
- Grade D or F → ask before proceeding

---

## Checkpoints

At each phase boundary, update `state.yaml`:

```yaml
# Example after Phase 3
state:
  current_node: "analysis"
  stage: "analysis_complete"
  analysis:
    ANSWER_RATE: 87.5
    GRADE: "C"
    kpis_computed: true
```

Do NOT proceed to next phase until gate condition is true.

---

## Code Execution Pattern

For computational phases (4, 5, 6):

```python
# 1. Write script to file
scripts/calculate_{phase}.py

# 2. Execute
python scripts/calculate_{phase}.py --input gold_calls.csv --output manifest.json

# 3. Verify output
- File exists
- Size > 0
- Values within expected ranges

# 4. Update state
state.{phase}.computed = true
```

---

## Critical Slides

Visual verification required for: **1, 5, 8, 18**

Slide 18 (Paths Forward):
- MUST use v4 HTML (`<table class="pf-table">`)
- MUST NOT use markdown table
- Reference: `references/slide18_paths_forward_v4.md`

---

## File Outputs

All outputs to `output/<client_slug>/`:

```
output/<client_slug>/
  gold_calls.csv           # Standardized data
  analysis_manifest.json   # All computed values
  charts/                  # PNG charts
  presentation.md          # Source of truth
  presentation.html        # Rendered
  presentation.pptx        # Rendered
```

---

## Quick Reference

### Constraints Location
- Stop rules: `brain.yaml` → `constraints.stop_rules`
- Must do: `brain.yaml` → `constraints.must_do`
- Must not: `brain.yaml` → `constraints.must_not`
- Pricing minimums: `brain.yaml` → `config.pricing_minimums`

### State Tracking
- Current position: `state.yaml` → `current_node`, `stage`
- Phase progress: `state.yaml` → `{phase}.{field}`
- Validation flags: `state.yaml` → `validation.*`

### References
- Slide 18 structure: `references/slide18_paths_forward_v4.md`
- Template variables: `references/template_contract.md`
- Pricing constants: `config/pricing_constants.yaml`

---

## Error Handling

Read: `../phone_to_present/workflow/error_handling.md`

- Critical failure → STOP, report, wait for user
- Recoverable error → retry with adjusted approach
- Data quality issue → flag, ask user to confirm

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
[1] Discovery ──[confirm]──> [2] Ingestion
  |                              |
  v                              v
[3] Analysis ──[kpis]──> [4] Concurrency (write code)
  |                              |
  v                              v
[5] Pricing (write code) ──> [6] Charts (verify)
  |                              |
  v                              v
[7] Presentation ──> [7b] QA ──> [8] Deliverables
  |
  v
DONE
```
