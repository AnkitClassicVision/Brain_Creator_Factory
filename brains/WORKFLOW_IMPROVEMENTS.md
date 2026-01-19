# Workflow Improvement Recommendations - Comprehensive Guide

This document provides actionable instructions for updating the phone_to_present_cc workflow to prevent errors encountered during the Casey Optical Too run.

---

## Part 1: Errors Encountered in This Run

### Error 1: Missing Template File - Generated from Scratch
**What happened:** The repo didn't have `templates/presentation_template.md`. Instead of stopping and asking the user, the agent generated an entire presentation from scratch with untested CSS/HTML.

**Impact:**
- Presentation looked unprofessional with inconsistent styling
- Complex HTML structures that weren't tested
- Wasted time debugging rendering issues
- Required multiple correction cycles

**Root Cause:** No pre-flight check for template existence; no explicit "STOP" instruction when template missing.

---

### Error 2: Template Version Mismatch (Slide 18)
**What happened:** When template was copied from `urban_optics`, it used a markdown table for Slide 18 instead of the v4 HTML table structure specified in `references/slide18_paths_forward_v4.md`.

**Impact:**
- Slide 18 rendered as plain markdown table (no styling)
- Missing SVG icons for check/warn/x
- Missing "MOST POPULAR" badge on RHC column
- No visual differentiation between service options

**Root Cause:** Template validation didn't verify v4 HTML structure compliance.

---

### Error 3: Incomplete Data Population (Pilot Row)
**What happened:** The Pilot Program pricing row was added but lacked complete data in some columns.

**Impact:** Incomplete presentation data; unprofessional appearance.

**Root Cause:** No row-by-row completeness validation after template population.

---

### Error 4: Pricing Minimum Not Enforced
**What happened:** Calculated Pilot pricing at $570/week when the minimum is $600.

**Impact:** Incorrect pricing presented to client.

**Root Cause:** Pricing minimums not documented in workflow or enforced programmatically.

---

### Error 5: FTE Minimum Hours Not Enforced
**What happened:** FTE calculations didn't enforce a minimum of 40 hours.

**Impact:** Potential underpricing; incorrect staffing recommendations.

**Root Cause:** Minimum constraints not specified in pricing phase.

---

### Error 6: Chart Verification Skipped
**What happened:** Charts were generated but not verified to render correctly in the final HTML output.

**Impact:** Potential missing or broken graphics in slides.

**Root Cause:** No render verification step in charts phase.

---

### Error 7: Slide 8 Data/Graphic Issues
**What happened:** Slide 8 (Process vs Capacity analysis) may have had missing or incorrect data display.

**Impact:** Key insight slide not rendering correctly.

**Root Cause:** No slide-specific validation for critical slides.

---

## Part 2: STOP Rules - When to Halt and Ask User

Add these explicit STOP conditions to `brain.yaml` under `constraints.must_do`:

```yaml
must_do:
  # === STOP RULES ===
  - "STOP and ask user if templates/presentation_template.md is missing - DO NOT generate from scratch"
  - "STOP and ask user if template does NOT contain class='pf-table' (v4 Paths Forward HTML)"
  - "STOP and ask user if any required reference file is missing"
  - "STOP and ask user if FTE calculation results in less than 40 hours weekly coverage"
  - "STOP and ask user if calculated pricing falls below minimums (Pilot: $600, others: $480)"
  - "STOP and ask user if disposition unknown_pct > 10%"
  - "STOP and ask user if Monte Carlo FTE differs from CDF FTE by more than 1.0"
  - "STOP and escalate if any chart file size is 0 bytes"
  - "STOP and ask user before proceeding if quality grade is D or F"
```

---

## Part 3: DO NOT Rules - Actions That Are Forbidden

Add these to `brain.yaml` under `constraints.must_not`:

```yaml
must_not:
  # === NEVER IMPROVISE ===
  - "Generate presentation content from scratch when template is missing - ALWAYS stop and ask"
  - "Use a markdown table for Slide 18 - MUST use v4 HTML pf-table structure"
  - "Skip the template validation step"
  - "Proceed with a template that doesn't match the slide18_paths_forward_v4.md specification"
  - "Skip visual verification of rendered HTML before marking complete"
  - "Use pricing below minimums (Pilot: $600/week, Inbound/RHC/RHC+Growth: calculated, Hire: calculated)"
  - "Calculate FTE for less than 40 weekly hours"
  - "Show FTE numbers adjacent to prices in client-facing materials"
  - "Guess or assume values for missing data - always ask user"
  - "Deliver presentation with any unreplaced {{PLACEHOLDER}} tokens"
  - "Include emojis in client-facing materials"
  - "Skip any QA step - all QA is mandatory"
```

---

## Part 4: Configuration Constants to Add

Create a new file `config/pricing_constants.yaml`:

```yaml
# Pricing Constants - DO NOT MODIFY without approval
pricing:
  minimums:
    PILOT_WEEKLY_MIN: 600          # $600/week minimum for pilot
    INBOUND_WEEKLY_MIN: 480        # $480/week minimum (1 FTE)
    RHC_WEEKLY_MIN: 480            # $480/week minimum (1 FTE)
    RHC_GROWTH_WEEKLY_MIN: 980     # $480 + $500 add-on minimum
    HIRE_WEEKLY_MIN: 960           # $960/week minimum (1 FTE)

  rates:
    MYBCAT_WEEKLY_RATE: 480        # $/week per FTE
    MYBCAT_OT_HOURLY: 18           # $/hour overtime
    HIRE_WEEKLY_RATE: 960          # $/week per FTE in-house
    HIRE_OT_HOURLY: 36             # $/hour overtime in-house
    WEEKEND_PREMIUM_PER_DAY: 25    # $/FTE per weekend day
    RHC_GROWTH_ADDON: 500          # $/week growth add-on

coverage:
  minimums:
    WEEKLY_HOURS_MIN: 40           # Minimum weekly hours for any calculation
    FTE_MIN: 1.0                   # Minimum FTE (1 full-time equivalent)
    SHRINKAGE_FTE_MIN: 1.25        # Minimum shrinkage-adjusted FTE

  shrinkage:
    SHRINKAGE_PCT: 20              # 20% shrinkage for breaks/PTO/training
    SHRINK_FACTOR: 0.80            # 1 - (SHRINKAGE_PCT / 100)

monte_carlo:
  NUM_SIMULATIONS: 1000
  TARGET_COVERAGE: 0.90
  FTE_RECONCILIATION_TOLERANCE: 1.0  # Max allowed diff between CDF and MC
```

---

## Part 5: Phase-by-Phase Workflow Updates

### Phase 0: Pre-flight Checks (NEW PHASE)

Add to `graph.yaml` before intake:

```yaml
# ═══════════════════════════════════════════════════════════════════
# PHASE 0: PRE-FLIGHT CHECKS
# ═══════════════════════════════════════════════════════════════════
- id: "preflight_template_check"
  type: "gate"
  stage: "preflight"
  purpose: "Verify presentation template exists"

  gate_config:
    criteria:
      - name: "template_exists"
        check: "file_exists('templates/presentation_template.md')"
    on_pass: "preflight_template_validate"
    on_fail: "preflight_missing_template"
    max_retries: 0

- id: "preflight_missing_template"
  type: "flow"
  stage: "preflight"
  purpose: "STOP - template missing"

  prompt: |
    CRITICAL: templates/presentation_template.md is MISSING.

    DO NOT proceed. DO NOT generate from scratch.

    Ask user:
    "The presentation template is missing. Please provide the template file or specify a source repo to copy from (e.g., urban_optics, coastal_vision)."

    WAIT for user response before continuing.

  on_complete:
    - action: "stop"
      reason: "Template missing - requires user input"

- id: "preflight_template_validate"
  type: "flow"
  stage: "preflight"
  purpose: "Validate template has v4 Paths Forward HTML"

  prompt: |
    Read templates/presentation_template.md and verify it contains:

    1. REQUIRED: class="pf-table" (v4 Paths Forward HTML structure)
    2. REQUIRED: class="pf-container"
    3. REQUIRED: class="pf-icon-check", class="pf-icon-warn", class="pf-icon-x"
    4. REQUIRED: class="pf-rhc" (RHC column styling)
    5. REQUIRED: class="pf-badge" (MOST POPULAR badge)
    6. REQUIRED: All {{PLACEHOLDER}} variables from template contract

    If ANY are missing:
    - Log which components are missing
    - Set template_valid = false
    - Proceed to preflight_template_invalid

    If ALL present:
    - Set template_valid = true
    - Proceed to preflight_references_check

  output_schema:
    type: "object"
    required: ["template_valid", "missing_components"]
    properties:
      template_valid: { type: "boolean" }
      missing_components: { type: "array" }

- id: "preflight_template_invalid"
  type: "flow"
  stage: "preflight"
  purpose: "STOP - template doesn't meet v4 spec"

  prompt: |
    CRITICAL: Template validation FAILED.

    Missing components: {{state.data.missing_components}}

    DO NOT proceed with this template.

    Ask user:
    "The template is missing required v4 components: {{state.data.missing_components}}

    Options:
    1. Update the template to include missing components
    2. Copy a known-good template from another repo
    3. Provide a different template file

    Which would you like to do?"

    WAIT for user response.

  on_complete:
    - action: "stop"
      reason: "Template invalid - requires user input"

- id: "preflight_references_check"
  type: "gate"
  stage: "preflight"
  purpose: "Verify reference files exist"

  gate_config:
    criteria:
      - name: "slide18_ref_exists"
        check: "file_exists('references/slide18_paths_forward_v4.md')"
    on_pass: "preflight_config_check"
    on_fail: "preflight_missing_references"
    max_retries: 0

- id: "preflight_missing_references"
  type: "flow"
  stage: "preflight"
  purpose: "STOP - reference files missing"

  prompt: |
    CRITICAL: Required reference files are missing.

    Missing: references/slide18_paths_forward_v4.md

    Ask user:
    "The Slide 18 v4 reference specification is missing. This is required to validate the Paths Forward table. Please provide this file or copy from a sibling repo."

- id: "preflight_config_check"
  type: "flow"
  stage: "preflight"
  purpose: "Load and validate configuration"

  prompt: |
    Load config/pricing_constants.yaml and validate:

    1. All minimum values are present
    2. All rate values are present
    3. Monte Carlo parameters are present

    Store in state for use in pricing phase.

  on_complete:
    - action: "proceed"
      next: "intake"
```

---

### Phase 1: Discovery Updates

Add to discovery phase:

```yaml
- id: "discovery_pilot_decision"
  type: "flow"
  stage: "discovery"
  purpose: "Explicitly ask about Pilot Program inclusion"

  prompt: |
    Ask user explicitly:

    "Should we include a Pilot Program option in the presentation?

    The Pilot Program is a lower-commitment entry option with:
    - Inbound answering only (no recalls, confirmations, etc.)
    - Lower staffing level
    - Minimum $600/week pricing

    Include Pilot? (Yes/No)"

    If Yes, also ask:
    "What staffing level should the Pilot use? (Recommend: Base HC at 90% arrival coverage)"

    Store:
    - pilot.enabled: true/false
    - pilot.level: selected level (if enabled)
    - pilot.calculation: "base" (default)

  on_complete:
    - action: "ask_user"
      questions:
        - "Include Pilot Program option? (Yes/No)"
        - "If yes, what staffing level?"
```

---

### Phase 5: Pricing Updates

Add minimum enforcement:

```yaml
- id: "pricing_apply_minimums"
  type: "flow"
  stage: "pricing"
  purpose: "Apply minimum pricing constraints"

  prompt: |
    BEFORE finalizing pricing, apply minimums:

    1. PILOT_WEEKLY = max(calculated_pilot, 600)
    2. INBOUND_WEEKLY = max(calculated_inbound, 480)
    3. RHC_WEEKLY = max(calculated_rhc, 480)
    4. RHC_GROWTH_WEEKLY = max(calculated_rhc_growth, 980)
    5. HIRE_WEEKLY = max(calculated_hire, 960)

    If ANY calculated value was below minimum, log:
    "Applied minimum pricing: [option] calculated at $X, set to minimum $Y"

    Store final pricing with applied minimums.

- id: "pricing_hours_validation"
  type: "gate"
  stage: "pricing"
  purpose: "Verify minimum hours constraint"

  gate_config:
    criteria:
      - name: "min_hours_met"
        check: "state.data.coverage.total_weekly_hours >= 40"
    on_pass: "pricing_summary"
    on_fail: "pricing_hours_escalate"
    max_retries: 0

- id: "pricing_hours_escalate"
  type: "flow"
  stage: "pricing"
  purpose: "STOP - hours below minimum"

  prompt: |
    CRITICAL: Weekly hours ({{state.data.coverage.total_weekly_hours}}) is below minimum (40).

    This shouldn't happen for a normal business. Check:
    1. Business hours were entered correctly
    2. Timezone is correct
    3. Open days are correct

    Ask user:
    "Weekly coverage hours calculated as {{state.data.coverage.total_weekly_hours}}.
    This is below the 40-hour minimum. Please verify business hours are correct."
```

---

### Phase 6: Charts Updates

Add chart verification:

```yaml
- id: "charts_verify_files"
  type: "flow"
  stage: "charts"
  purpose: "Verify all chart files exist and are valid"

  prompt: |
    Verify each generated chart:

    REQUIRED CHARTS:
    1. charts/miss_distribution.png
    2. charts/daily_volume.png
    3. charts/hourly_volume.png
    4. charts/heatmap.png
    5. charts/concurrency_cdf.png
    6. charts/grade_badge.png

    For each chart, verify:
    - File exists
    - File size > 0 bytes
    - File is valid PNG (check magic bytes or use image library)

    If ANY chart fails:
    - Log which charts failed
    - STOP and report: "Chart generation failed for: [list]"
    - Attempt to regenerate failed charts

    Do NOT proceed to presentation phase until all charts are verified.

  output_schema:
    type: "object"
    required: ["charts_valid", "failed_charts"]
    properties:
      charts_valid: { type: "boolean" }
      failed_charts: { type: "array" }
```

---

### Phase 7: Presentation Updates

Add comprehensive validation:

```yaml
- id: "presentation_load_template"
  type: "flow"
  stage: "presentation"
  purpose: "Load and prepare template for population"

  prompt: |
    Load templates/presentation_template.md.

    CRITICAL CHECKS before population:
    1. Verify template contains class="pf-table" (Slide 18 v4 HTML)
       - If NOT found: STOP - "Template missing v4 Paths Forward HTML"
    2. Count {{PLACEHOLDER}} tokens - store count for verification
    3. Verify all required sections exist (by slide markers)

    DO NOT modify the template structure.
    ONLY replace {{PLACEHOLDER}} tokens with calculated values.

- id: "presentation_populate_slide18"
  type: "flow"
  stage: "presentation"
  purpose: "Populate Slide 18 Paths Forward table"

  prompt: |
    Slide 18 MUST use v4 HTML structure from references/slide18_paths_forward_v4.md.

    STEPS:
    1. Locate the pf-table in the template
    2. Verify 5-column structure if Pilot enabled, 4-column if not
    3. Replace pricing placeholders:
       - {{HIRE_WEEKLY}} with formatted number (e.g., "4,140")
       - {{INBOUND_WEEKLY}} with formatted number
       - {{RHC_WEEKLY}} with formatted number
       - {{RHC_GROWTH_WEEKLY}} with formatted number
       - {{PILOT_WEEKLY}} if pilot enabled
    4. Calculate and insert savings values:
       - INBOUND_SAVINGS = HIRE_WEEKLY - INBOUND_WEEKLY
       - RHC_SAVINGS = HIRE_WEEKLY - RHC_WEEKLY
       - etc.
    5. Verify ALL cells in ALL rows are populated

    DO NOT use markdown table format.
    DO NOT remove or modify the HTML structure.

- id: "presentation_validate_all_placeholders"
  type: "flow"
  stage: "presentation"
  purpose: "Verify zero unreplaced placeholders remain"

  prompt: |
    After population, search for remaining {{...}} tokens.

    grep -o '{{[^}]*}}' presentation.md | sort | uniq

    If ANY tokens remain:
    - Log which placeholders are unreplaced
    - STOP: "Unreplaced placeholders found: [list]"
    - Do NOT proceed to rendering

    If zero remain: proceed to next step.

- id: "presentation_validate_critical_slides"
  type: "flow"
  stage: "presentation"
  purpose: "Validate content of critical slides"

  prompt: |
    Validate these specific slides:

    SLIDE 1 (Title):
    - {{CLIENT_NAME}} replaced
    - {{WEBSITE_URL}} replaced
    - {{SPECIALTY}} replaced

    SLIDE 5 (Primary KPIs):
    - {{ANSWER_RATE}} is a valid percentage
    - {{MISS_RATE}} is a valid percentage
    - {{GRADE}} is A/B/C/D/F

    SLIDE 8 (Process vs Capacity):
    - {{PROCESS_MISS_PCT}} is a valid percentage
    - {{CAPACITY_MISS_PCT}} is a valid percentage
    - Image reference: ![](charts/miss_distribution.png) present

    SLIDE 18 (Paths Forward):
    - Contains class="pf-table" (NOT markdown |---|)
    - Contains class="pf-icon-check"
    - All pricing cells populated
    - All savings cells populated
    - If Pilot enabled: Pilot column present

    Log validation results for each slide.
    STOP if any critical slide fails validation.
```

---

### Phase 7b: QA Updates

Add mandatory QA steps:

```yaml
- id: "qa_render_html"
  type: "flow"
  stage: "qa"
  purpose: "Render HTML and verify output"

  prompt: |
    Run: marp presentation.md --html --allow-local-files -o presentation.html

    After rendering, verify:
    1. presentation.html exists
    2. File size > 50KB (reasonable minimum for full deck)
    3. Contains expected slide count (check <section> tags)

    If ANY fail: STOP and report rendering issues.

- id: "qa_check_images_embedded"
  type: "flow"
  stage: "qa"
  purpose: "Verify all images are accessible in HTML"

  prompt: |
    In presentation.html, verify all image references resolve:

    1. Extract all <img src="..."> paths
    2. For each path, verify file exists
    3. If any missing: log and report

    ALSO check that no broken image placeholders appear.

- id: "qa_slide18_html_check"
  type: "flow"
  stage: "qa"
  purpose: "Verify Slide 18 uses HTML table in rendered output"

  prompt: |
    In presentation.html, find the Paths Forward slide and verify:

    1. Contains <table class="pf-table"> (NOT markdown table)
    2. Contains SVG icons (check for <svg viewBox)
    3. Contains pricing rows with actual numbers (not placeholders)
    4. Contains .pf-rhc class on RHC column
    5. Contains .pf-badge for "MOST POPULAR"

    If using markdown table (|---|): FAIL
    "Slide 18 rendered as markdown table instead of v4 HTML. Fix template and re-render."

- id: "qa_visual_verification"
  type: "tributary"
  stage: "qa"
  purpose: "Visual verification of critical slides"

  skill_name: "visual_verification"
  skill_config:
    slides_to_capture: [1, 5, 8, 18]
    checks:
      - name: "images_visible"
        description: "All chart images load and display"
      - name: "tables_complete"
        description: "No empty cells in tables"
      - name: "no_placeholder_text"
        description: "No {{...}} visible in rendered slides"
      - name: "slide18_styled"
        description: "Slide 18 shows styled HTML table, not plain markdown"
    on_fail: "qa_visual_failed"

- id: "qa_visual_failed"
  type: "flow"
  stage: "qa"
  purpose: "Handle visual verification failures"

  prompt: |
    Visual verification failed. Issues found:
    {{state.data.visual_issues}}

    DO NOT mark QA complete.

    Attempt to fix issues:
    1. If images missing: verify chart files exist
    2. If placeholders visible: re-run template population
    3. If Slide 18 not styled: verify v4 HTML in source

    After fixes, re-render and re-verify.
```

---

## Part 6: Template Contract

Create `references/template_contract.md`:

```markdown
# Presentation Template Variable Contract

All templates MUST support these placeholders:

## Client Information
- {{CLIENT_NAME}} - Full client/practice name
- {{CLIENT_SLUG}} - URL-safe lowercase name
- {{WEBSITE_URL}} - Client website
- {{SPECIALTY}} - e.g., "Optometry"
- {{TAGLINE}} - Optional client tagline

## Date & Period
- {{ANALYSIS_DATE}} - Date of analysis
- {{DATA_PERIOD_START}} - Start of data range
- {{DATA_PERIOD_END}} - End of data range
- {{WEEKS_ANALYZED}} - Number of weeks in data

## Primary KPIs
- {{ANSWER_RATE}} - Open hours answer rate (e.g., "92.9%")
- {{MISS_RATE}} - Open hours miss rate
- {{GRADE}} - Letter grade (A/B/C/D/F)
- {{GRADE_BG_COLOR}} - Background color for grade
- {{MISSED_CALLS_WEEK}} - Average missed calls per week

## Analysis Details
- {{WORST_DAY}} - Worst performing day
- {{WORST_DAY_RATE}} - Miss rate on worst day
- {{WORST_HOUR_1}} - Worst time slot (e.g., "Thursday 9am")
- {{WORST_HOUR_1_RATE}} - Miss rate at worst time
- {{PROCESS_MISS_PCT}} - Percentage of misses due to process
- {{CAPACITY_MISS_PCT}} - Percentage due to capacity

## Staffing
- {{BASE_FTE}} - Base FTE requirement
- {{SHRINKAGE_FTE}} - Shrinkage-adjusted FTE

## Pricing (weekly)
- {{HIRE_WEEKLY}} - In-house hiring cost
- {{INBOUND_WEEKLY}} - MyBCAT Inbound
- {{RHC_WEEKLY}} - MyBCAT RHC
- {{RHC_GROWTH_WEEKLY}} - MyBCAT RHC + Growth
- {{PILOT_WEEKLY}} - Pilot program (if enabled)

## Pricing (monthly)
- {{HIRE_MONTHLY}}, {{INBOUND_MONTHLY}}, {{RHC_MONTHLY}}, etc.

## Pricing (annual)
- {{HIRE_ANNUAL}}, {{INBOUND_ANNUAL}}, {{RHC_ANNUAL}}, etc.

## Savings
- {{INBOUND_SAVINGS_WEEKLY}} - HIRE_WEEKLY - INBOUND_WEEKLY
- {{RHC_SAVINGS_WEEKLY}} - HIRE_WEEKLY - RHC_WEEKLY
- {{RHC_GROWTH_SAVINGS_WEEKLY}} - HIRE_WEEKLY - RHC_GROWTH_WEEKLY
- {{PILOT_SAVINGS_WEEKLY}} - HIRE_WEEKLY - PILOT_WEEKLY (if enabled)

## Conditional
- {{#PILOT_ENABLED}} ... {{/PILOT_ENABLED}} - Only include if Pilot active
```

---

## Part 7: Repository Structure Requirements

Each client repo MUST have this structure:

```
<client_repo>/
├── brain.yaml                           # Workflow brain definition
├── graph.yaml                           # Workflow graph definition
├── config/
│   └── pricing_constants.yaml           # Pricing rates and minimums
├── templates/
│   ├── presentation_template.md         # REQUIRED - Marp template with v4 Slide 18
│   └── slide18_v4.html                  # Reference HTML for Slide 18
├── references/
│   ├── slide18_paths_forward_v4.md      # REQUIRED - v4 specification
│   └── template_contract.md             # Variable definitions
├── data/
│   └── *.xlsx or *.csv                  # Input data files
├── output/
│   └── <client_slug>/
│       ├── gold_calls.csv               # Standardized call data
│       ├── analysis.json                # Computed metrics
│       ├── concurrency.json             # FTE calculations
│       ├── pricing.json                 # Final pricing
│       ├── presentation.md              # Populated template
│       ├── presentation.html            # Rendered HTML
│       ├── presentation.pptx            # Rendered PPTX (optional)
│       └── charts/
│           ├── miss_distribution.png
│           ├── daily_volume.png
│           ├── hourly_volume.png
│           ├── heatmap.png
│           ├── concurrency_cdf.png
│           └── grade_badge.png
└── scripts/
    ├── validate_template.py             # Pre-flight validation
    └── verify_presentation.py           # Post-generation validation
```

---

## Part 8: Validation Scripts

### validate_template.py

```python
#!/usr/bin/env python3
"""Pre-flight template validation script"""
import sys
import re
from pathlib import Path

def validate_template(template_path: str) -> dict:
    """Validate template has all required components"""

    issues = []
    template = Path(template_path)

    if not template.exists():
        return {"valid": False, "issues": ["Template file not found"]}

    content = template.read_text()

    # Check for v4 Paths Forward HTML
    required_classes = [
        ('pf-table', 'v4 Paths Forward table'),
        ('pf-container', 'Paths Forward container'),
        ('pf-icon-check', 'Check icon class'),
        ('pf-icon-warn', 'Warning icon class'),
        ('pf-icon-x', 'X icon class'),
        ('pf-rhc', 'RHC column styling'),
        ('pf-badge', 'MOST POPULAR badge'),
    ]

    for class_name, description in required_classes:
        if f'class="{class_name}"' not in content and f"class='{class_name}'" not in content:
            issues.append(f"Missing {description} (class='{class_name}')")

    # Check for markdown table in Slide 18 (BAD)
    if '| Feature |' in content and '|--' in content:
        # Check if this is inside the Paths Forward section
        if 'Paths Forward' in content:
            issues.append("Slide 18 uses markdown table instead of v4 HTML")

    # Check for required placeholders
    required_placeholders = [
        '{{CLIENT_NAME}}', '{{ANSWER_RATE}}', '{{GRADE}}',
        '{{HIRE_WEEKLY}}', '{{RHC_WEEKLY}}', '{{INBOUND_WEEKLY}}'
    ]

    for placeholder in required_placeholders:
        if placeholder not in content:
            issues.append(f"Missing placeholder: {placeholder}")

    return {
        "valid": len(issues) == 0,
        "issues": issues
    }

if __name__ == "__main__":
    template_path = sys.argv[1] if len(sys.argv) > 1 else "templates/presentation_template.md"
    result = validate_template(template_path)

    if result["valid"]:
        print("✓ Template validation PASSED")
        sys.exit(0)
    else:
        print("✗ Template validation FAILED")
        for issue in result["issues"]:
            print(f"  - {issue}")
        sys.exit(1)
```

### verify_presentation.py

```python
#!/usr/bin/env python3
"""Post-generation presentation verification script"""
import sys
import re
from pathlib import Path

def verify_presentation(md_path: str, html_path: str) -> dict:
    """Verify generated presentation meets requirements"""

    issues = []

    # Check markdown source
    md_file = Path(md_path)
    if not md_file.exists():
        return {"valid": False, "issues": ["presentation.md not found"]}

    md_content = md_file.read_text()

    # Check for unreplaced placeholders
    placeholders = re.findall(r'\{\{[^}]+\}\}', md_content)
    if placeholders:
        issues.append(f"Unreplaced placeholders: {', '.join(set(placeholders))}")

    # Check Slide 18 structure
    if 'class="pf-table"' not in md_content:
        issues.append("Slide 18 missing v4 HTML (no pf-table class)")

    # Check HTML output
    html_file = Path(html_path)
    if html_file.exists():
        html_content = html_file.read_text()

        # Verify HTML size is reasonable
        if len(html_content) < 50000:
            issues.append(f"HTML file suspiciously small: {len(html_content)} bytes")

        # Verify images referenced
        img_refs = re.findall(r'src="([^"]+\.png)"', html_content)
        for img in img_refs:
            img_path = Path(md_file.parent) / img
            if not img_path.exists():
                issues.append(f"Missing image: {img}")
    else:
        issues.append("presentation.html not found")

    return {
        "valid": len(issues) == 0,
        "issues": issues
    }

if __name__ == "__main__":
    md_path = sys.argv[1] if len(sys.argv) > 1 else "output/client/presentation.md"
    html_path = sys.argv[2] if len(sys.argv) > 2 else md_path.replace('.md', '.html')

    result = verify_presentation(md_path, html_path)

    if result["valid"]:
        print("✓ Presentation verification PASSED")
        sys.exit(0)
    else:
        print("✗ Presentation verification FAILED")
        for issue in result["issues"]:
            print(f"  - {issue}")
        sys.exit(1)
```

---

## Part 9: Checklist for Human Operators

### Before Starting Workflow

- [ ] `templates/presentation_template.md` exists in repo
- [ ] Template contains `class="pf-table"` (v4 Paths Forward HTML)
- [ ] Template contains all CSS classes: pf-container, pf-icon-check, pf-icon-warn, pf-icon-x, pf-rhc, pf-badge
- [ ] `references/slide18_paths_forward_v4.md` exists
- [ ] `config/pricing_constants.yaml` exists with minimums defined
- [ ] Data files are in `data/` directory

### During Discovery Phase

- [ ] Client name, website, specialty confirmed
- [ ] Timezone confirmed (not assumed)
- [ ] Business hours confirmed
- [ ] Closures/holidays documented
- [ ] Pilot program decision made explicitly (Yes/No)

### During Pricing Phase

- [ ] Weekly hours >= 40 (minimum)
- [ ] PILOT_WEEKLY >= $600 (if enabled)
- [ ] All pricing uses correct FTE (BASE for Inbound, SHRINKAGE for RHC)
- [ ] Monte Carlo FTE reconciles with CDF FTE (within 1.0)

### During Charts Phase

- [ ] All 6 chart files generated
- [ ] All chart files have size > 0 bytes
- [ ] Chart dimensions are 1000x700 (or as specified)

### During Presentation Phase

- [ ] Template loaded (NOT generated from scratch)
- [ ] Slide 18 uses v4 HTML (pf-table class present)
- [ ] Zero unreplaced `{{PLACEHOLDER}}` tokens
- [ ] All image paths resolve to existing files

### During QA Phase

- [ ] HTML renders successfully
- [ ] Open presentation.html in browser
- [ ] Visually verify Slide 1 (title, client name)
- [ ] Visually verify Slide 5 (KPIs, grade)
- [ ] Visually verify Slide 8 (chart visible, process/capacity data)
- [ ] Visually verify Slide 18 (styled table, NOT markdown, all prices populated)
- [ ] All charts display correctly (no broken images)

---

## Part 10: Error Recovery Procedures

### If Template Is Missing

1. STOP - do not proceed
2. Check sibling repos for a known-good template
3. Copy template: `cp ../urban_optics/templates/presentation_template.md templates/`
4. Run `python scripts/validate_template.py`
5. If validation fails, manually add missing components from `references/slide18_paths_forward_v4.md`
6. Re-run validation
7. Only proceed when validation passes

### If Slide 18 Uses Markdown Table

1. STOP - do not deliver
2. Open `references/slide18_paths_forward_v4.md`
3. Copy the v4 HTML scaffold
4. Replace the markdown table in the template with the HTML scaffold
5. Add required CSS to template's style block
6. Re-populate placeholders
7. Re-render and verify

### If Pricing Is Below Minimums

1. Review calculated pricing vs. minimums
2. Apply minimum: `FINAL_PRICE = max(calculated, minimum)`
3. Log adjustment: "Applied minimum pricing for [option]"
4. Update pricing.json with final values
5. Re-populate template with corrected values

### If Charts Fail to Generate

1. Check chart generation errors in logs
2. Verify Python/matplotlib dependencies installed
3. Try regenerating one chart at a time
4. If persistent failure, check data validity
5. As fallback: generate placeholder images and note in QA

### If Visual Verification Fails

1. Identify which slides failed
2. Check specific failure reason (image, placeholder, styling)
3. Fix root cause in source files
4. Re-render: `marp presentation.md --html --allow-local-files -o presentation.html`
5. Re-verify visually
6. Only mark complete when all slides pass

---

## Part 11: Summary of Changes to brain.yaml

```yaml
# ADD to constraints.must_do:
- "Run pre-flight checks before starting workflow"
- "STOP and ask user if templates/presentation_template.md is missing - DO NOT generate from scratch"
- "Verify template includes v4 Paths Forward HTML (pf-table class) before proceeding"
- "Apply pricing minimums: Pilot >= $600, others as calculated but >= 1 FTE minimum"
- "Enforce minimum 40 weekly hours for FTE calculation"
- "Validate all chart files exist and have size > 0 before presentation phase"
- "Verify zero unreplaced {{PLACEHOLDER}} tokens after template population"
- "Run visual verification on slides 1, 5, 8, 18 before marking complete"
- "If Slide 18 uses markdown table, STOP and fix to use v4 HTML"

# ADD to constraints.must_not:
- "Generate presentation from scratch when template is missing"
- "Use markdown table for Slide 18 - MUST use v4 HTML pf-table"
- "Proceed with pricing below minimums without explicit user approval"
- "Skip any QA or verification step"
- "Deliver presentation with unreplaced placeholders"
- "Assume values when uncertain - always ask user"
- "Mark a phase complete if validation fails"
```

---

## Part 12: Quick Reference Card

### The 5 Golden Rules

1. **NEVER generate from scratch** - Always use the template
2. **ALWAYS validate before proceeding** - Check files, structure, values
3. **ALWAYS apply minimums** - Pricing and hours have floors
4. **NEVER skip QA** - Visual verification is mandatory
5. **ALWAYS STOP when uncertain** - Ask user, don't guess

### Pricing Minimums Quick Reference

| Option | Weekly Minimum |
|--------|----------------|
| Pilot Program | $600 |
| Inbound Answering | $480 (1 FTE) |
| RHC | $480 (1 FTE) |
| RHC + Growth | $980 ($480 + $500) |
| In-House | $960 (1 FTE) |

### Critical File Paths

- Template: `templates/presentation_template.md`
- Slide 18 Spec: `references/slide18_paths_forward_v4.md`
- Output: `output/<client_slug>/presentation.md`
- Charts: `output/<client_slug>/charts/*.png`

### v4 Slide 18 Detection

```bash
# Should find matches (GOOD):
grep -c 'class="pf-table"' templates/presentation_template.md

# Should find 0 matches (GOOD):
grep -c '| Feature |' templates/presentation_template.md
```

---

*Document Version: 1.0*
*Created: 2026-01-15*
*Based on: Casey Optical Too workflow run errors*
