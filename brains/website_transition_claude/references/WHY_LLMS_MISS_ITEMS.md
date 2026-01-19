# Why LLMs Miss Critical Workflow Items

## Analysis Based on Casey Optical Too Run

This document explains the cognitive patterns that cause LLMs to miss critical validation steps, business rules, and quality gates.

---

## Error Pattern 1: Helpfulness Bias (Template Generation)

**What Happened:** LLM generated presentation from scratch instead of stopping when template was missing.

**Why LLMs Do This:**
```
LLM Internal Logic:
├── User wants: Presentation
├── Template missing: True
├── Can I complete the task? → Yes, I can generate one
├── Should I stop and ask? → NOT EXPLICITLY TOLD TO
└── Decision: Generate from scratch (be helpful!)
```

**Root Cause:** LLMs are trained to be helpful and complete tasks. Without explicit "STOP" instructions, they will improvise solutions rather than halt.

**The Fix Pattern:**
```yaml
# EXPLICIT STOP RULE
must_do:
  - "STOP and ask user if [required file] is missing - DO NOT generate/improvise"
```

**Website Migration Analog:**
- Missing `master_url_sheet.csv` → LLM might invent redirect rules
- Missing GSC data → LLM might guess traffic patterns
- Missing crawl data → LLM might assume URL structure

---

## Error Pattern 2: Format Blindness (Template Version Mismatch)

**What Happened:** Used markdown table instead of v4 HTML structure for Slide 18.

**Why LLMs Do This:**
```
LLM Internal Logic:
├── Task: Populate Slide 18 with pricing
├── I see a table structure needed
├── Markdown tables are simpler and valid
├── HTML structure is "extra complexity"
└── Decision: Use markdown (simpler is better!)
```

**Root Cause:** LLMs don't inherently understand that specific HTML structures have semantic/styling importance. They optimize for "correctness" not "format compliance."

**The Fix Pattern:**
```yaml
# EXPLICIT FORMAT REQUIREMENT
must_do:
  - "Slide 18 MUST use v4 HTML pf-table structure - verify class='pf-table' exists"

must_not:
  - "Use markdown table for Slide 18 - MUST use v4 HTML structure"
```

**Website Migration Analog:**
- Vercel redirects must be JSON, not YAML
- Schema must be JSON-LD, not Microdata
- Sitemap must be XML, not plain text list

---

## Error Pattern 3: Partial Completion (Incomplete Data Population)

**What Happened:** Pilot row added but missing data in some columns.

**Why LLMs Do This:**
```
LLM Internal Logic:
├── Task: Add Pilot row to pricing table
├── Main columns populated: ✓
├── Are ALL columns required? → Not explicitly stated
├── Is "mostly complete" acceptable? → Implicit yes
└── Decision: Move on (task "done enough")
```

**Root Cause:** LLMs satisfy the "spirit" of instructions without exhaustive completeness checks. They don't automatically validate row-by-row, cell-by-cell.

**The Fix Pattern:**
```yaml
# EXPLICIT COMPLETENESS VALIDATION
must_do:
  - "Verify ALL cells in ALL rows are populated - no empty cells allowed"
  - "After any table population, run completeness check"
```

**Website Migration Analog:**
- Master URL sheet with missing "action" column values
- Redirect map with empty "destination" fields
- Technical SEO audit with gaps

---

## Error Pattern 4: Business Rule Ignorance (Pricing Minimum)

**What Happened:** Calculated $570/week when minimum is $600.

**Why LLMs Do This:**
```
LLM Internal Logic:
├── Task: Calculate Pilot pricing
├── Formula: base_fte × rate = $570
├── Is $570 mathematically correct? → Yes
├── Is there a business minimum? → NOT IN MY CONTEXT
└── Decision: Use calculated value (math is right!)
```

**Root Cause:** Business rules (minimums, floors, caps) are domain knowledge, not mathematical. LLMs execute formulas correctly but don't know business constraints unless explicitly provided.

**The Fix Pattern:**
```yaml
# EXPLICIT BUSINESS CONSTRAINTS
config:
  pricing_minimums:
    PILOT_WEEKLY_MIN: 600
    INBOUND_WEEKLY_MIN: 480

must_do:
  - "Apply pricing minimum: final_price = max(calculated, minimum)"
  - "Log any minimum enforcement: 'Applied minimum: calculated $X, set to $Y'"
```

**Website Migration Analog:**
- CWV targets are business constraints (LCP ≤ 2.5s is a rule, not a calculation)
- Redirect chain length maximum (≤2 hops)
- Maximum acceptable 404 rate post-launch

---

## Error Pattern 5: Implicit Assumptions (FTE Minimum Hours)

**What Happened:** FTE calculated for <40 hours without flagging.

**Why LLMs Do This:**
```
LLM Internal Logic:
├── Task: Calculate FTE from hours
├── Hours provided: 35
├── FTE = hours / 40 = 0.875
├── Is 0.875 FTE valid? → Mathematically yes
├── Is there a minimum hours rule? → NOT STATED
└── Decision: Use 0.875 (calculation correct!)
```

**Root Cause:** LLMs don't flag "unusual" values unless given explicit boundaries. What seems "obviously wrong" to humans (a business open <40 hours/week) isn't obvious to an LLM.

**The Fix Pattern:**
```yaml
# EXPLICIT SANITY CHECKS
must_do:
  - "STOP and ask user if weekly hours < 40"
  - "Validate all inputs against expected ranges before processing"
```

**Website Migration Analog:**
- URL count < 10 (suspiciously small site)
- 0 backlinks found (likely data issue)
- 100% miss rate on redirects (config error)

---

## Error Pattern 6: Output Trust (Chart Verification Skipped)

**What Happened:** Charts generated but not verified to render correctly.

**Why LLMs Do This:**
```
LLM Internal Logic:
├── Task: Generate charts
├── Command executed: python generate_charts.py
├── Exit code: 0 (success)
├── Files created? → YES (according to command)
├── Are files valid? → ASSUMED from exit code
└── Decision: Move on (generation "succeeded")
```

**Root Cause:** LLMs trust that successful command execution = valid output. They don't verify that generated files are actually usable (non-zero size, valid format, correct content).

**The Fix Pattern:**
```yaml
# EXPLICIT OUTPUT VERIFICATION
must_do:
  - "After generating charts, verify: file exists, size > 0, valid format"
  - "STOP if any chart file is 0 bytes or missing"
```

**Website Migration Analog:**
- Sitemap generated but empty
- Redirect config JSON but invalid syntax
- Schema markup generated but fails validation

---

## Error Pattern 7: Equal Treatment (Critical Slides Not Prioritized)

**What Happened:** Slide 8 had issues but wasn't specifically validated.

**Why LLMs Do This:**
```
LLM Internal Logic:
├── Task: Validate presentation
├── Number of slides: 20
├── Validate all equally? → Yes (no priority given)
├── Slide 8 special? → NOT MARKED AS CRITICAL
└── Decision: Generic validation (treat all same)
```

**Root Cause:** Without explicit marking of "critical" items, LLMs apply uniform attention. They don't know that some slides/pages/URLs are more important than others.

**The Fix Pattern:**
```yaml
# EXPLICIT CRITICAL ITEM MARKING
must_do:
  - "Apply EXTRA validation to critical slides: 1, 5, 8, 18"
  - "Critical URLs require individual verification: homepage, service pages, top-traffic pages"
```

**Website Migration Analog:**
- Money pages need extra redirect verification
- Top-traffic URLs need individual smoke tests
- High-backlink pages need explicit destination validation

---

## Summary: The 7 LLM Blind Spots

| # | Blind Spot | LLM Behavior | Fix Pattern |
|---|------------|--------------|-------------|
| 1 | Helpfulness Bias | Improvises when blocked | Explicit STOP rules |
| 2 | Format Blindness | Simplifies structure | Format verification gates |
| 3 | Partial Completion | "Good enough" mentality | Completeness validation |
| 4 | Business Rule Ignorance | Pure math, no constraints | Explicit minimums/maximums |
| 5 | Implicit Assumptions | Accepts unusual values | Sanity check gates |
| 6 | Output Trust | Assumes success = valid | Output verification |
| 7 | Equal Treatment | No prioritization | Critical item marking |

---

## How to Prevent These in Workflows

### 1. Make STOP Conditions Explicit
```yaml
must_do:
  - "STOP and ask user if [condition] - DO NOT [alternative]"
```

### 2. Add Verification Gates
```yaml
gate_config:
  criteria:
    - name: "file_valid"
      check: "file_exists AND file_size > 0"
```

### 3. Define Business Constants
```yaml
config:
  minimums:
    X_MIN: 100
  validation:
    TOLERANCE: 0.1
```

### 4. Mark Critical Items
```yaml
critical_items:
  urls: ["/", "/services", "/contact"]
  extra_validation: true
```

### 5. Use Output Schemas
```yaml
output_schema:
  type: "object"
  required: ["all", "fields", "must", "exist"]
```

---

## Application to Website Transition Brain

These patterns directly apply:

| Casey Optical Error | Website Migration Equivalent |
|---------------------|------------------------------|
| Missing template | Missing master URL sheet |
| Wrong table format | Wrong redirect config format |
| Incomplete pricing rows | Incomplete redirect mappings |
| Below-minimum pricing | CWV below targets |
| Invalid FTE hours | Invalid URL patterns |
| Unverified charts | Unverified schema markup |
| Missed critical slide | Missed critical URL |
