# Phone Log Analysis Pipeline v2.0

## TRIGGER
When the user says **"start"**, execute this complete workflow from data discovery through final presentation.

---

## WORKFLOW OVERVIEW

This pipeline analyzes phone call logs and generates sales presentations. It has 9 phases:

| Phase | Name | Instructions File | Purpose |
|-------|------|-------------------|---------|
| 1 | Discovery & Setup | `workflow/phase1_discovery.md` | Find data files, gather client info, scrape website |
| 2 | Data Ingestion | `workflow/phase2_ingestion.md` | Standardize columns, normalize data, quality checks |
| 3 | Core Analysis | `workflow/phase3_analysis.md` | Calculate stats, pain windows, answer rates |
| 4 | Concurrency & FTE | `workflow/phase4_concurrency.md` | Monte Carlo simulation, FTE requirements |
| 5 | Pricing | `workflow/phase5_pricing.md` | Calculate costs for all 4 options |
| 6 | Chart Generation | `workflow/phase6_charts.md` | Generate required charts (template-referenced) |
| 7 | Presentation | `workflow/phase7_presentation.md` | Populate template, generate HTML/PPTX |
| 7b | **Presentation QA** | `workflow/phase7b_presentation_qa.md` | Visual verification, fix layout/contrast issues |
| 8 | Deliverables | `workflow/phase8_deliverables.md` | Summary and file output |

**Reference Files:**
- `workflow/reference_tables.md` - Timezones, pricing tables, specialty values
- `workflow/error_handling.md` - Error recovery, stop conditions, retry logic
- `workflow/verification_checklist.md` - Deterministic checks & balances (FTE/pricing/metrics + Marp HTML/PPTX verification)

---

## EXECUTION FLOW

### Phase 1: Discovery
**Read:** `workflow/phase1_discovery.md`
1. Search for CSV/XLSX files
2. Ask user for client name, website, specialty
3. Scrape website for business hours, timezone
4. Ask explicitly about holiday/temporary closures and per-location schedule/timezone differences
5. Calculate weekly coverage hours (regular, OT, weekends)

**CHECKPOINT:** Confirm metadata with user before proceeding.

---

### Phase 2: Data Ingestion
**Read:** `workflow/phase2_ingestion.md`
1. Identify phone system format
2. Map columns to standard schema
3. Normalize dispositions (Answered/Missed/Voicemail)
4. Review raw disposition values and confirm mapping semantics (especially transferred/forwarded/redirected)
5. Add business context flags
6. Run quality checks

**CHECKPOINT:** Report data quality, ask user if issues found.

---

### Phase 3: Core Analysis
**Read:** `workflow/phase3_analysis.md`
1. Separate inbound calls into OPEN HOURS vs CLOSED HOURS
2. **PRIMARY METRICS (OPEN HOURS ONLY):** answer rate, miss rate, grade (A-F)
3. Build 2D pain windows matrix (day × hour) - OPEN HOURS ONLY
4. Identify worst 3 hours - OPEN HOURS ONLY
5. Track closed hours separately as reference data

**IMPORTANT:** All main metrics (answer rate, missed calls/week, grade) are based on OPEN HOURS only.

**CHECKPOINT:** Store key metrics for presentation.

---

### Phase 4: Concurrency & FTE
**Read:** `workflow/phase4_concurrency.md`
1. Calculate triggered concurrency
2. Calculate time-weighted concurrency
3. Calculate BASE_FTE using CDF at 90% coverage (ignore level 0)
4. Calculate SHRINKAGE_FTE = BASE_FTE / 0.80

**CHECKPOINT:** Store FTE values for pricing.
**CHECKS & BALANCES:** Run deterministic Monte Carlo + reconcile FTE results (see `workflow/verification_checklist.md`).

---

### Pilot Program (Optional)
After Phase 4 (once concurrency + `BASE_FTE`/`SHRINKAGE_FTE` are known), show a staffing ladder:
- **Base HC** (integer staffing level)
- **Shrinkage HC** (Base HC adjusted with shrinkage buffer)
- **Answer Rate** (arrival-coverage at that level)

Then ask the user:
1. Should we include a **Pilot Program (Inbound Answering)** option in the presentation?
2. If yes: which staffing **level** (Base HC) and which **calculation basis** (base vs shrinkage) should the pilot pricing use?

If a pilot is included:
- Add a pilot row to the deck’s “Your Investment Options” table.
- Add a “World Class Answer Rate” line under the **Inbound Answering** answer-rate cell only (never on Pilot/RHC/RHC+).
If no pilot: omit both.

---

### Phase 5: Pricing
**Read:** `workflow/phase5_pricing.md`
1. Calculate MyBCAT Inbound pricing (uses BASE_FTE × $480/week)
2. Calculate MyBCAT RHC pricing (uses SHRINKAGE_FTE × $480/week)
3. Calculate MyBCAT RHC+ Growth (RHC + $500/week add-on + 1x/month consulting)
4. Calculate In-House hiring cost (uses SHRINKAGE_FTE × $960/week)
5. Calculate revenue leak estimate

**CHECKPOINT:** Store all pricing variables.
**CHECKS & BALANCES:** Verify costs match formulas + sanity checks before charts/deck (see `workflow/verification_checklist.md`).

---

### Phase 6: Charts
**Read:** `workflow/phase6_charts.md`
1. Generate the charts referenced by the Marp template (currently 6) to `output/<client_slug>/charts/` (or your configured output folder)
2. Use placeholder if any chart fails

**CHECKPOINT:** Verify charts exist.

---

### Phase 7: Presentation
**Read:** `workflow/phase7_presentation.md`
1. Load `templates/presentation_template.md`
2. Replace all `{{VARIABLES}}`
3. Save populated markdown (this `.md` becomes the **source of truth**)
4. Generate HTML + PPTX via Marp CLI **from the populated `.md`**
5. Optionally generate PDF

**CHECKPOINT:** Verify output files created.

---

### Phase 7b: Presentation QA (REQUIRED)
**Read:** `workflow/phase7b_presentation_qa.md`
1. Open HTML in browser and review each slide visually
2. Check for white-on-white text (especially section dividers)
3. Verify whitespace margins on all 4 sides of each slide
4. Fix layout issues (stack → side-by-side if overflow)
5. Verify all charts/images load correctly
6. Run automated render + whitespace checks (`scripts/render_verify.py`) and fix any failing slides
7. Run automated checks for unreplaced variables

**CHECKPOINT:** All slides pass visual verification before proceeding.
**CHECKS & BALANCES:** Verify PPTX export renders correctly (not just HTML).

**CRITICAL CHECKS:**
- Section dividers ("PART 1", "PART 2", "PART 3") must have colored backgrounds, NOT white
- No content should touch slide edges - require padding on all sides
- If content overflows, restructure to side-by-side layout or split slide

---

### Phase 8: Deliverables
**Read:** `workflow/phase8_deliverables.md`
1. Present summary to user
2. List all generated files
3. Provide key insights

**COMPLETE:** Workflow finished.

---

## QUICK REFERENCE (In-Memory)

### Open Hours = Primary Data
```
All main metrics are calculated from OPEN HOURS data only:
- Answer Rate, Miss Rate, Grade
- Missed Calls/Week
- Pain Windows, Worst Hours
- Daily/Hourly patterns

Closed hours tracked separately for reference only.
```

### Grade Thresholds (Open Hours)
```
A: 95%+ answer rate
B: 90-94%
C: 80-89%
D: 70-79%
F: <70%
```

### FTE Calculations
```
BASE_FTE = CDF at 90% coverage from time-weighted concurrency (ignore level 0)
SHRINKAGE_FTE = BASE_FTE / 0.80 (adds 20% shrinkage)
MIN_BASE_FTE = 1.0
MIN_SHRINKAGE_FTE = 1.25
```

### Pricing (Internal Calculation Only)
```
Internal rates - NEVER show to clients:
- MyBCAT: $480/week base, $18/hr OT
- In-House: $960/week base, $36/hr OT
- Weekend: $25 × BASE_FTE per day
```

### VALUE-BASED PRICING DISPLAY (Critical)
```
NEVER show in presentation:
- FTE numbers next to prices
- Hourly rates or rate breakdowns
- "× FTE × hours" calculations
- Emojis or decorative icons

ALWAYS show:
- Final weekly/monthly/annual prices only
- Services included per option
- Savings vs in-house

FTE mention (separate from pricing):
"Your call volume requires approximately X dedicated
staff to answer 90%+ of calls."
```

---

## ERROR HANDLING

**Read:** `workflow/error_handling.md` for full details.

### Critical Failures (STOP)
- No data file found
- Cannot parse file format
- No timestamp column
- No inbound calls detected
- Template file missing

### Non-Critical (CONTINUE)
- Website scraping failed → Ask user manually
- Chart generation failed → Use placeholder
- Marp CLI not installed → Output .md only

---

## USER INTERACTION POINTS

| Step | User Does |
|------|-----------|
| Start | Says "start" |
| Phase 1 | Answers 4-5 metadata questions |
| Phase 1 | Confirms website data is correct |
| Phase 2 | Clarifies column mapping (if ambiguous) |
| Phase 2 | Approves data quality (if issues found) |
| Phase 7b | Reviews visual QA results, approves fixes |
| Phase 8 | Reviews deliverables, opens presentation |

**Total user interaction: ~3-5 minutes** (includes visual QA review)

---

## FILES STRUCTURE

```
Phone_Analysis_Template/
├── CLAUDE.md                       ← This controller file
├── workflow/
│   ├── phase1_discovery.md         ← Discovery instructions
│   ├── phase2_ingestion.md         ← Data standardization
│   ├── phase3_analysis.md          ← Core analysis
│   ├── phase4_concurrency.md       ← FTE calculation
│   ├── phase5_pricing.md           ← Cost comparison
│   ├── phase6_charts.md            ← Chart specs
│   ├── phase7_presentation.md      ← Template population
│   ├── phase7b_presentation_qa.md  ← Visual QA & fixes
│   ├── phase8_deliverables.md      ← Output summary
│   ├── reference_tables.md         ← Lookup tables
│   └── error_handling.md           ← Error recovery
├── templates/
│   └── presentation_template.md    ← Marp slide deck
├── output/                         ← Generated files go here
└── assets/                         ← Client logos (optional)
```
