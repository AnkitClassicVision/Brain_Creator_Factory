# Phone Analysis Template

A complete workflow for analyzing phone call data and generating client-ready sales presentations with FTE-based pricing.

## Quick Start

1. Place your CSV/XLSX phone data file in this folder
2. Say **"start"** to Claude
3. Follow the guided workflow
4. Before delivery, run verification gates (see `workflow/verification_checklist.md`)

---

## CLI (Deterministic) Run

From `phone_to_present/`:
```bash
python scripts/run_pipeline.py \
  --input "<path/to/Call History.csv>" \
  --config "<path/to/config.json>" \
  --out "output/<client_slug>"
```

Interactive mode (prints Base HC / Shrinkage HC / coverage ladder and prompts for pilot option settings):
```bash
python scripts/run_pipeline.py \
  --interactive \
  --input "<path/to/Call History.csv>" \
  --config "<path/to/config.json>" \
  --out "output/<client_slug>"
```

Multi-location exports:
- Set `analysis.location_mode="by_location"` to write `output/<client_slug>/locations/<location_slug>/...` plus `output/<client_slug>/rollup_manifest.json`.
- Or run a single site with `--location "Exact Location Name"`.

For internal testing only, bypass confirmation gates with `--allow-unconfirmed` (the deck will be marked low-confidence and caveated).

---

## Config File (`config.json`)

Top-level keys used by the deterministic runner (`scripts/run_pipeline.py`):
- `client`: `client_name`, `specialty`, `timezone` (IANA), optional `website_url`/`client_tagline`
- `business_hours`: day → `["HH:MM","HH:MM"]` or `null` (closed)
- `confirmations`: `timezone`, `business_hours`, `closures`, `disposition_mapping` (`confirmed`/`assumed`/`unconfirmed`)
- `closures` (optional): `["YYYY-MM-DD", ...]` (global closure calendar)
- `location_overrides` (optional): per `location_name` overrides for `timezone`, `business_hours`, `closures`, `confirmations`
- `pilot` (optional): `enabled` (bool), `level` (int Base HC), `calculation` (`base` or `shrinkage`) — controls optional pilot row in the deck
- `analysis` (optional): quality gates + modeling controls:
  - confirmation gates: `require_confirmed_metadata` (default `true`), `require_disposition_mapping_confirmation` (default `true`)
  - mapping thresholds: `max_unknown_disposition_pct`, `max_unknown_direction_pct`, `max_low_conf_disposition_pct`, `max_redirected_pct`, `stop_on_low_confidence`
  - multi-location: `location_mode` = `single` or `by_location`
  - Monte Carlo: `num_simulations`, `mc_duration_model` = `bootstrap_answered` / `bootstrap_all_open` / `exponential`
  - reconciliation: `fte_reconcile_tolerance` (fails if `abs(MC_FTE_90 - BASE_FTE)` exceeds this)

---

## Folder Structure

```
Phone_analysis_template/
├── CLAUDE.md                    # Master workflow (triggered by "start")
├── README.md                    # This file
├── templates/
│   ├── presentation_template.md # Marp slide template with placeholders
│   └── slide_structure_guide.html # Visual guide to slide flow
├── assets/
│   └── mybcat_logo.png          # Company logo (place here)
└── output/
    └── <client_slug>/
        ├── gold_calls.csv             # Normalized “gold” table (audit)
        ├── analysis_manifest.json     # Audit manifest + computed variables
        ├── presentation.md            # Populated Marp markdown (source of truth)
        ├── presentation.html          # Rendered HTML slides (from `.md`)
        ├── presentation.pptx          # Rendered PowerPoint deck (from `.md`)
        ├── presentation.render_manifest.json  # Render QA + hashes + slide count
        └── charts/                    # Template-referenced chart PNGs
```

---

## Workflow Phases

| Phase | Description | Output |
|-------|-------------|--------|
| 1. Discovery | Find data files, gather client metadata, pull website info | Client profile |
| 2. Ingestion | Standardize columns, normalize dispositions, quality checks | Cleaned dataset |
| 3. Core Analysis | Calculate answer rates, segment by time/location/hour | Summary tables |
| 4. Concurrency & FTE | Triggered + time-weighted analysis, FTE calculation | FTE requirements |
| 5. Pricing | FTE-based pricing with shrinkage, in-house comparison | Pricing table |
| 6. Charts | Generate all required visualizations | PNG images |
| 7. Presentation | Populate template, render to HTML | Final deck |
| 8. Deliverables | Package all outputs | Complete folder |

---

## FTE Pricing Reference

### Rates (Internal Calculation Only)
| Service | Weekly Base per 1.0 FTE | Notes |
|---------|--------------------------|-------|
| Inbound Answering | $480/week | MyBCAT internal base rate |
| In-House Hire | $960/week | Fully-loaded wage model (wages + burden) |

**RHC pricing model:** RHC uses the MyBCAT base rate with shrinkage buffer:
- `RHC_WEEKLY_BASE = SHRINKAGE_FTE × $480/week`

**RHC+ Growth:** RHC plus monthly growth consulting:
- add-on: **+$500/week** (flat) on top of RHC

### Shrinkage & Minimums
- **Shrinkage**: 20% (breaks, training, admin, PTO)
- **Minimum Adjusted FTE**: 1.25 (floor due to shrinkage)
- **Formula**: `Adjusted FTE = max(Raw FTE / 0.80, 1.25)`

### In-House Cost Comparison
- Base wage: $20/hr
- Burden: 20% (taxes, benefits)
- Fully loaded: $24/hr
- Weekly (40 hrs): $960/week per FTE

### ROI Calculation
```
Inbound Weekly Cost = Raw FTE (BASE_FTE) × $480
RHC Weekly Cost = Adjusted FTE (SHRINKAGE_FTE) × $480
RHC+ Growth Weekly Cost = RHC Weekly Cost + $500
In-House Weekly Cost = Adjusted FTE × $960
Weekly Savings = In-House - MyBCAT
Annual Savings = Weekly Savings × 52
```

---

## Template Variables

The authoritative placeholder + asset contract is generated from the template:
- Contract: `workflow/template_contract.md`
- Regenerate: `python scripts/generate_template_contract.py`

For delivery quality, the deck must explicitly surface the metadata assumptions used for open/closed classification:
- `{{TIMEZONE_DESC}}` + `{{TIMEZONE_RATIONALE}}`
- `{{BUSINESS_HOURS_DESC}}` + `{{BUSINESS_HOURS_RATIONALE}}`
- `{{CLOSURES_DESC}}` + `{{CLOSURES_RATIONALE}}`

---

## Chart Requirements

The template-referenced chart list is in `workflow/template_contract.md`.

| Chart | Filename | Purpose |
|-------|----------|---------|
| Answer Rate Gauge | `answer_rate_gauge.png` | Visual grade (A-F) |
| Pain Windows Heatmap | `pain_windows_heatmap.png` | Hour × Day missed calls |
| Process vs Capacity | `miss_distribution.png` | Pie chart of miss causes |
| Hourly Volume | `hourly_volume.png` | Calls by hour |
| Daily Pattern | `daily_pattern.png` | Calls by day of week |
| FTE Coverage | `fte_coverage.png` | Time-weighted concurrency + 90% coverage |

---

## Presentation Modes

### Short Presentation (15-20 min)
Use slides 1-19 (Core Deck):
- OPENING: Slides 1-3
- DIAGNOSIS: Slides 4-9
- PROGNOSIS: Slides 10-13
- TREATMENT: Slides 14-19

### Extended Presentation (30-45 min)
Include Extended Data section (slides 20-28):
- Detailed hourly/daily breakdowns
- Concurrency deep dive
- Month-over-month trends

### Leave-Behind
Include Appendix (slides 29+):
- Methodology details
- All assumptions
- Data integrity notes

---

## Timezone Reference

| Region | IANA Timezone |
|--------|---------------|
| Eastern | America/New_York |
| Central | America/Chicago |
| Mountain | America/Denver |
| Pacific | America/Los_Angeles |
| Arizona | America/Phoenix |
| Alaska | America/Anchorage |
| Hawaii | Pacific/Honolulu |
| Atlantic | America/Puerto_Rico |
| Guam | Pacific/Guam |

---

## Rendering Presentations

### Using Marp CLI
```bash
# Install Marp CLI
npm install -g @marp-team/marp-cli

# Render to HTML
marp output/<client_slug>/presentation.md -o output/<client_slug>/presentation.html --no-stdin

# Render to PDF
marp output/<client_slug>/presentation.md -o output/<client_slug>/presentation.pdf --no-stdin --pdf

# Render to PowerPoint
marp output/<client_slug>/presentation.md -o output/<client_slug>/presentation.pptx --no-stdin
```

### Deterministic Render + Verification (Recommended)

From `phone_to_present/`:
```bash
python scripts/render_verify.py output/<client_slug>/presentation.md
```
This fails fast if variables are unreplaced or images are missing, then renders HTML + PPTX from the `.md` and writes a render manifest.

### Using Marp for VS Code
1. Install "Marp for VS Code" extension
2. Open the .md file
3. Click "Open Preview" or export from command palette

---

## Customization Guide

### Adding New Slides
1. Copy a similar slide from the template
2. Use consistent Marp directives (`<!-- _class: -->`)
3. Add `[REQUIRED]`, `[CONDITIONAL]`, or `[OPTIONAL]` marker
4. Update the slide_structure_guide.html

### Modifying Pricing
Update both the documentation and the implementation:
- Docs: `workflow/phase5_pricing.md`
- Implementation: `scripts/run_pipeline.py` (pricing constants + formulas)
- Verification: `scripts/verify_financials.py` (must stay in sync)

### Adding Client Types
The template supports different client types with conditional slides:
- Single vs Multi-location
- With/without RHC needs
- With/without detailed data requests

---

## Troubleshooting

### "Unknown disposition" rate is high
- Check the raw disposition column values
- Add new mappings to the normalization dictionary in CLAUDE.md
- Mark disposition_confidence = "Inferred" if using duration-based inference

### Charts not rendering
- Ensure matplotlib/seaborn are available
- Check that `output/<client_slug>/charts/` (or your configured output folder) exists
- Verify image paths in presentation use relative paths

### FTE seems too low
- Check if concurrency analysis captured peak hours
- Verify shrinkage is being applied (20%)
- Minimum should be 1.25 adjusted FTE

### Presentation layout issues
- Ensure Marp CLI is installed
- Use `--no-stdin` flag to avoid hanging
- Check image paths are correct relative to .md file

---

## Support

For questions about:
- **Workflow issues**: Check CLAUDE.md for detailed instructions
- **Template customization**: See templates/presentation_template.md
- **Slide flow decisions**: See templates/slide_structure_guide.html
