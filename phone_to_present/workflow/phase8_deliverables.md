# Phase 8: Deliverables & Summary

## Overview

Present the completed analysis to the user with all generated files and key insights.

---

## Step 8.1 - Summary Dashboard

Present a quick summary of the analysis results.

```
═══════════════════════════════════════════════════════════════════
                    PHONE ANALYSIS COMPLETE
═══════════════════════════════════════════════════════════════════

Client: {{CLIENT_NAME}}
Data Range: {{DATE_RANGE}}
Total Calls Analyzed: {{TOTAL_RECORDS}}

───────────────────────────────────────────────────────────────────
                         KEY METRICS
───────────────────────────────────────────────────────────────────

Answer Rate:     {{ANSWER_RATE}}%  (Grade: {{GRADE}})
Missed/Week:     {{MISSED_PER_WEEK}} calls
Revenue Leak:    ${{ANNUAL_LEAK}}/year (estimated)

───────────────────────────────────────────────────────────────────
                        ROOT CAUSE
───────────────────────────────────────────────────────────────────

Process Issues:  {{PROCESS_MISS_PCT}}%  (missed when staff available)
Capacity Issues: {{CAPACITY_MISS_PCT}}%  (missed due to volume)

───────────────────────────────────────────────────────────────────
                      WORST WINDOWS
───────────────────────────────────────────────────────────────────

#1: {{WORST_HOUR_1}}  ({{WORST_HOUR_1_RATE}}% miss rate)
#2: {{WORST_HOUR_2}}  ({{WORST_HOUR_2_RATE}}% miss rate)
#3: {{WORST_HOUR_3}}  ({{WORST_HOUR_3_RATE}}% miss rate)

───────────────────────────────────────────────────────────────────
                    PRICING OPTIONS
───────────────────────────────────────────────────────────────────

Option 1: MyBCAT Inbound    {{INBOUND_MONTHLY}}/month
Option 2: MyBCAT RHC        {{RHC_MONTHLY}}/month
Option 3: MyBCAT RHC+ Growth {{RHC_GROWTH_MONTHLY}}/month
Option 4: In-House Hire     {{HIRE_MONTHLY}}/month

═══════════════════════════════════════════════════════════════════
```

---

## Step 8.2 - List Generated Files

```
───────────────────────────────────────────────────────────────────
                      GENERATED FILES
───────────────────────────────────────────────────────────────────

Presentation Files:
  [OK] output/<client_slug>/presentation.md
  [OK] output/<client_slug>/presentation.html
  [OK] output/<client_slug>/presentation.pptx
  [--] output/<client_slug>/presentation.pdf  (optional)
  [OK] output/<client_slug>/presentation.render_manifest.json

Audit Files:
  [OK] output/<client_slug>/analysis_manifest.json
  [OK] output/<client_slug>/gold_calls.csv

Chart Images:
  [OK] output/<client_slug>/charts/answer_rate_gauge.png
  [OK] output/<client_slug>/charts/pain_windows_heatmap.png
  [OK] output/<client_slug>/charts/miss_distribution.png
  [OK] output/<client_slug>/charts/hourly_volume.png
  [OK] output/<client_slug>/charts/daily_pattern.png
  [OK] output/<client_slug>/charts/fte_coverage.png

───────────────────────────────────────────────────────────────────
```

---

## Step 8.3 - Key Insights

Generate talking points for the presentation.

### Insight Generation Logic

```python
def generate_insights(analysis_results):
    """
    Generate key insights based on analysis results.
    Returns list of insight strings.
    """
    insights = []

    # Grade-based insight
    if GRADE == 'A':
        insights.append(f"Excellent performance! {ANSWER_RATE}% answer rate exceeds industry benchmark.")
    elif GRADE == 'B':
        insights.append(f"Good performance at {ANSWER_RATE}%. Minor improvements possible.")
    elif GRADE in ['C', 'D']:
        insights.append(f"Answer rate of {ANSWER_RATE}% indicates room for improvement.")
    else:
        insights.append(f"Critical: {ANSWER_RATE}% answer rate is well below industry standard of 90%.")

    # Process vs Capacity insight
    if PROCESS_MISS_PCT > 50:
        insights.append(f"{PROCESS_MISS_PCT}% of misses occur when only one call is active - this is a process issue, not a staffing issue.")
    else:
        insights.append(f"{CAPACITY_MISS_PCT}% of misses occur during high volume - additional coverage needed.")

    # Worst hours insight
    if WORST_HOUR_1 != "None - Great performance!":
        insights.append(f"Highest risk window: {WORST_HOUR_1} with {WORST_HOUR_1_RATE}% miss rate.")

    # Revenue impact insight
    if REVENUE_LEAK_ANNUAL > 0:
        insights.append(f"Estimated ${REVENUE_LEAK_ANNUAL:,} annual revenue at risk from missed calls.")

    # Savings insight
    if INBOUND_SAVINGS_ANNUAL > 0:
        insights.append(f"MyBCAT Inbound saves ${INBOUND_SAVINGS_ANNUAL:,}/year vs in-house hire.")

    return insights

INSIGHTS = generate_insights(analysis_results)
```

### Present Insights

```
───────────────────────────────────────────────────────────────────
                       KEY INSIGHTS
───────────────────────────────────────────────────────────────────

1. {{INSIGHT_1}}

2. {{INSIGHT_2}}

3. {{INSIGHT_3}}

4. {{INSIGHT_4}}

───────────────────────────────────────────────────────────────────
```

---

## Step 8.4 - Recommended Next Steps

```
───────────────────────────────────────────────────────────────────
                     RECOMMENDED NEXT STEPS
───────────────────────────────────────────────────────────────────

1. Review the HTML presentation:
   → Open: output/<client_slug>/presentation.html

2. Customize talking points for client meeting

3. Prepare for common objections:
   - "Our staff is doing fine" → Show process vs capacity data
   - "This seems expensive" → Compare to in-house costs + revenue leak
   - "We don't trust outsourcing" → Offer 30-day pilot

4. Schedule client presentation

───────────────────────────────────────────────────────────────────
```

---

## Step 8.5 - Data Quality Notes

If any data quality issues were flagged, remind the user.

```python
def generate_quality_notes():
    """
    Generate data quality notes if any issues were flagged.
    """
    notes = []

    if PCT_UNKNOWN_DISPOSITION > 10:
        notes.append(f"[!] {PCT_UNKNOWN_DISPOSITION}% of calls have unknown disposition. Results may be conservative.")

    if DIRECTION_INFERRED:
        notes.append(f"[!] Call direction was inferred (confidence: {DIRECTION_CONFIDENCE:.0%})")

    if LOW_VOLUME_WARNING:
        notes.append("[!] Low call volume - results may not be statistically significant.")

    if len(notes) == 0:
        notes.append("[OK] Data quality is good. Results are reliable.")

    return notes
```

```
───────────────────────────────────────────────────────────────────
                     DATA QUALITY NOTES
───────────────────────────────────────────────────────────────────

{{QUALITY_NOTES}}

───────────────────────────────────────────────────────────────────
```

---

## Step 8.6 - Workflow Complete Message

```
═══════════════════════════════════════════════════════════════════
                    WORKFLOW COMPLETE
═══════════════════════════════════════════════════════════════════

Analysis completed successfully for {{CLIENT_NAME}}.

To present:
  1. Open the HTML file in your browser
  2. Press F11 for fullscreen presentation mode
  3. Use arrow keys or spacebar to navigate slides

Questions? Check workflow/reference_tables.md for additional details.

═══════════════════════════════════════════════════════════════════
```

---

## Complete Output Structure

```
output/
└── <client_slug>/
    ├── gold_calls.csv                  # Normalized “gold” table (audit)
    ├── analysis_manifest.json          # Audit manifest + computed variables
    ├── presentation.md                 # Source markdown (deck source of truth)
    ├── presentation.html               # HTML presentation
    ├── presentation.pptx               # PowerPoint deck
    ├── presentation.pdf                # PDF (optional)
    ├── presentation.render_manifest.json  # Render QA + hashes + slide count
    └── charts/
        ├── answer_rate_gauge.png       # Grade visualization
        ├── pain_windows_heatmap.png    # Hour × Day heatmap
        ├── miss_distribution.png       # Process vs Capacity pie
        ├── hourly_volume.png           # Calls by hour
        ├── daily_pattern.png           # Calls by day
        └── fte_coverage.png            # Concurrency coverage curve
```

---

## Variables Summary

There are two sets of values at completion:

### 1) Deck variables (client-facing)
- Used in `output/<client_slug>/presentation.md` via `{{PLACEHOLDER}}`
- Source of truth: `workflow/template_contract.md` (regenerate with `python scripts/generate_template_contract.py` after template edits)
- Persisted in `output/<client_slug>/analysis_manifest.json` under `deck_variables`

### 2) Audit + computed variables (internal)
Stored in `output/<client_slug>/analysis_manifest.json`:
- `metrics` (open-hours KPIs, grade, weeks in range)
- `fte` (`BASE_FTE`, `SHRINKAGE_FTE`)
- `pricing` (inbound, rhc, rhc_growth, in_house totals + breakdown)
- `quality` (mapping report, confirmation flags, caveats)
