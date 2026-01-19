# Verification Checklist (Deterministic Checks & Balances)

This file defines the required checks that make the workflow:
- correct (numbers reconcile)
- repeatable (Monte Carlo is deterministic)
- shippable (Marp HTML + PPTX render from the final `.md` without surprises)

Use this as a gate before client delivery.

---

## 0) Metadata Confirmation (Phase 1)

### 0.1 Timezone + business hours are client-confirmed
- Confirm the timezone and business hours you used are **client-confirmed** (or explicitly marked “assumed” for internal testing only).
- For multi-location clients, confirm hours/timezone **per location** if they differ.

### 0.2 Closure calendar (holidays/closures) is explicit
- Confirm closure dates are provided (or explicitly “none”) and recorded.
- If closures are provided, verify calls on closure dates are treated as **closed** (not open hours).

### 0.3 Multi-location mode is explicit
- If `location_name` has multiple values, choose one:
  - run per-location (`analysis.location_mode=by_location`) OR
  - filter to a single location (`--location`) OR
  - explicitly accept combined analysis (document the limitation in the deck caveat).

---

## A) Metrics Integrity (Phases 2–3)

### A0. Direction/disposition mapping is reviewed (Phase 2)
- Review raw `call_status`/`disposition` values and confirm the mapping to answered/missed/abandoned/redirected.
- Confirm mapping confidence is within thresholds:
  - unknown disposition % and unknown direction % below configured limits
  - low-confidence mappings are acceptable and documented
- If many calls are `redirected/forwarded/transferred`, confirm whether the phone system semantics mean “answered then routed” (otherwise answer rate may be understated).

### A1. Inbound + Open/Closed splits reconcile
- Confirm `TOTAL_INBOUND_ALL = TOTAL_INBOUND (open) + TOTAL_CLOSED (closed)`.
- Confirm primary KPIs and grade are based on **open hours only**.

### A2. Missed calls definitions are consistent
- Define: `OPEN_MISSED = missed + abandoned` during open hours.
- Confirm all “miss rate” and “missed/week” use `OPEN_MISSED`, not closed-hours misses.

### A3. Weekly math is sound
- `WEEKS_IN_RANGE > 0` and matches `(DATE_RANGE_END - DATE_RANGE_START) / 7`.
- `MISSED_CALLS_WEEK = OPEN_MISSED / WEEKS_IN_RANGE` (rounding policy consistent).

---

## B) Deterministic Monte Carlo + FTE Verification (Phase 4)

### B1. Monte Carlo must be deterministic
Set a stable seed derived from the dataset so the same input produces the same output.

Recommended approach:
1. Build a stable “fingerprint” string from:
   - source filename
   - row count
   - min/max local timestamps
   - `AHT_USED`, `TARGET_COVERAGE`, `NUM_SIMULATIONS`
2. Hash the fingerprint (sha256), take an integer slice as `MC_SEED`.
3. Use `np.random.default_rng(MC_SEED)` for all randomness.

**Store in output:** `MC_SEED`, `NUM_SIMULATIONS`, `TARGET_COVERAGE`, and a summary of `MC_RESULTS`.
Also store:
- duration model used (`bootstrap_*` vs `exponential`)
- duration pool size (if bootstrap)

### B2. FTE reconciliation (must pass before pricing)
You should have two independent estimates:
- `BASE_FTE` from time-weighted concurrency CDF @ 90% (ignore level 0)
- `MC_FTE_90` from Monte Carlo results (e.g., median/90th of simulated FTE distribution)

Checks:
- `BASE_FTE >= 1.0`
- `SHRINKAGE_FTE = max(BASE_FTE / 0.80, 1.25)` (rounding policy defined)
- `abs(MC_FTE_90 - BASE_FTE)` should be “small” (flag if > 1.0 without a clear reason)

If reconciliation fails, review:
- open-hours flags (wrong business hours/timezone)
- duration handling and AHT default/minimum
- extreme outliers or timestamp parsing issues

### B3. Optional automated check (recommended)
If you save your computed variables to a JSON manifest (example: `output/<client_slug>/analysis_manifest.json`), run:
```bash
python scripts/verify_financials.py output/<client_slug>/analysis_manifest.json
```
This verifies shrinkage FTE and key pricing formulas deterministically.

---

## C) Pricing Verification (Phase 5)

### C1. Recompute all four options from the same inputs
Inputs:
- `BASE_FTE`, `SHRINKAGE_FTE`
- `OT_HOURS`, `HAS_SATURDAY`, `HAS_SUNDAY`

Recompute and compare:
- Inbound (MyBCAT): base + OT + weekend
- RHC: base uses `SHRINKAGE_FTE` + OT + weekend
- RHC+ Growth: `RHC_WEEKLY + $500/week` add-on
- In-house: base + OT + weekend (higher base and OT rates)
If using the pipeline manifest, also confirm the component breakdown sums correctly:
- `pricing.<option>.base + ot + weekend == pricing.<option>.weekly` (Inbound / RHC / In-house)
- `pricing.rhc_growth.base + ot + weekend + growth_addon_weekly == pricing.rhc_growth.weekly`

### C2. Sanity checks (flag exceptions)
- `RHC_WEEKLY >= INBOUND_WEEKLY` (RHC includes additional coverage/services)
- `RHC_GROWTH_WEEKLY >= RHC_WEEKLY` (Growth is an add-on)
- Usually `HIRE_WEEKLY >= INBOUND_WEEKLY` (in-house base rate is higher)
- No negative totals; OT and weekend charges only apply when the corresponding flags/hours are non-zero.

### C3. Client-facing display rule (enforce)
- Deck must show final weekly/monthly/annual numbers only.
- Do **not** show “rate × FTE” or any hourly breakdown in client-facing slides.

### C4. Revenue leak arithmetic (if used)
If the deck includes revenue leak numbers, recompute and compare:
- `weekly_leak = MISSED_CALLS_WEEK × appt_seeking% × new_patient% × conversion% × avg_value`
- monthly = weekly × 4.33; annual = monthly × 12

---

## D) Deck Integrity Gate (Phases 7–7b)

### D1. The `.md` deck is the source of truth
After variable replacement, `output/<client_slug>/presentation.md` is canonical.

All renders must be created from that file:
- HTML: `output/<client_slug>/presentation.html`
- PPTX: `output/<client_slug>/presentation.pptx`

### D2. Automated pre-render checks (must pass)
- No unreplaced `{{VARIABLE}}` tokens remain in the `.md`.
- Every referenced local image exists relative to the `.md` location (charts, logos).
- No emoji characters appear in the `.md` (client decks must be emoji-free).
- `workflow/template_contract.md` matches the current template (regenerate with `python scripts/generate_template_contract.py` after template edits).

### D3. Deterministic render + verification
Run (from `phone_to_present/`):
```bash
python scripts/render_verify.py output/<client_slug>/presentation.md
```

This should:
- render HTML and PPTX from the `.md` using Marp
- fail fast if variables are unreplaced or images are missing
- assert PPTX slide count matches markdown slide separators
- run slide-by-slide whitespace QA on the PPTX export (fails if content touches edges)
- normalize PPTX timestamps for deterministic bytes (same `.md` → same `.pptx` file hash)
- write a render manifest (hashes, slide count, Marp version)

### D4. Visual QA (required)
Even with automated checks, do a slide-by-slide visual review in:
- the generated HTML
- the generated PPTX (PowerPoint/Keynote)

Look for: overflow, white-on-white, missing images, broken layouts, table truncation.
