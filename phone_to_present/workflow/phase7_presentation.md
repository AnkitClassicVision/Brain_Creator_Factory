# Phase 7: Presentation Generation

## Overview

Generate the final presentation by populating the Marp template with calculated variables and generated charts.

---

## CRITICAL: Slide 18 Requires Manual HTML Build

⚠️ **DO NOT use the markdown table from the template for Slide 18 (Paths Forward).**

The template contains a placeholder table. You MUST replace it with the v4.0 HTML structure.

### Required Steps for Slide 18:

1. **Add the Paths Forward CSS** to the Marp style block (see Section "Slide 18: Paths Forward — Construction Guide" below for full CSS)

2. **Build the HTML table** using the v4.0 column structure:
   - Standard layout: **Feature**, **DIY Staffing**, **Inbound Answering**, **RHC**, **RHC + Growth**
   - Optional (if Pilot is enabled): insert a **Pilot Program** column **between DIY and Inbound** with the yellow SLA badge (see “Adding Pilot Column (5-Column)” below)

3. **Use SVG icons** for feature rows:
   - Green checkmark (`pf-icon-check`) = MyBCAT handles
   - Amber warning (`pf-icon-warn`) = You manage
   - Gray X (`pf-icon-x`) = Not included

4. **Include pricing rows** at bottom:
   - Weekly Investment row (DIY price with strikethrough)
   - "vs. DIY Staffing" savings row (green badge on RHC column)

### Quick Check:
If Slide 18 contains `|---|---|---|` markdown table syntax, **it's wrong**.
It should contain `<table class="pf-table">` HTML.

---

## Step 7.1 - Load Template

```python
# Load the presentation template
template_path = "templates/presentation_template.md"

with open(template_path, 'r') as f:
    template_content = f.read()
```

---

## Step 7.2 - Variable Replacement

Replace all `{{VARIABLE}}` placeholders with calculated values.

**Source of truth**
- The required placeholder set is defined by `templates/presentation_template.md`.
- Extract placeholders from the template and ensure your variables dict covers **all** of them (fail fast if not).

**Formatting rule (important)**
- The template includes `$` and `%` around many placeholders (for consistent slide typography).
- Provide variables as deterministic, pre-formatted strings (commas/rounding) **without** adding currency/percent symbols unless the template expects them.

To print the current placeholder list:
```bash
python scripts/generate_template_contract.py
cat workflow/template_contract.md
```

---

## Step 7.3 - Variable Replacement Function

```python
import re

PLACEHOLDER_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def extract_placeholders(text: str) -> list[str]:
    return sorted(set(PLACEHOLDER_RE.findall(text)))


def apply_template(template_text: str, variables: dict[str, str]) -> str:
    """
    Replace all {{VARIABLE}} placeholders in template_text using variables.

    IMPORTANT:
    - variables values should already be pre-formatted strings.
    - do not auto-add '$' or '%' here (the template controls symbols for consistency).
    """
    placeholders = extract_placeholders(template_text)
    missing = [p for p in placeholders if p not in variables]
    if missing:
        raise ValueError("Missing template variables:\\n" + "\\n".join(f"- {m}" for m in missing))

    out = template_text
    for k, v in variables.items():
        out = out.replace(f"{{{{{k}}}}}", v)

    leftover = extract_placeholders(out)
    if leftover:
        raise ValueError("Unreplaced template variables remain:\\n" + "\\n".join(f"- {m}" for m in leftover))

    return out
```

---

## Step 7.4 - Build Variables Dictionary

```python
# Build a dict for every placeholder found in the template (values are strings).
# Keep formatting deterministic (commas/rounding) and let the template control '$' and '%'.
placeholders = extract_placeholders(template_content)

variables: dict[str, str] = {
    # Example:
    # "CLIENT_NAME": client_name,
    # "ANSWER_RATE": f"{answer_rate:.1f}",
}

populated_content = apply_template(template_content, variables)
```

---

## Step 7.5 - Update Chart Paths

Ensure chart image paths are correct in the populated template.

The template expects chart references as **relative paths** like `charts/answer_rate_gauge.png`.

To keep paths simple and deterministic:
- write the populated deck to `output/<client_slug>/presentation.md`
- write charts to `output/<client_slug>/charts/*.png`

Then image paths resolve naturally in both HTML and PPTX exports.

---

## Step 7.6 - Save Populated Markdown

```python
# Save the populated markdown
client_slug = CLIENT_NAME.replace(" ", "_")
output_md_path = f"output/{client_slug}/presentation.md"

with open(output_md_path, 'w') as f:
    f.write(populated_content)

print(f"[OK] Saved: {output_md_path}")
```

**IMPORTANT:** From this point forward, the populated `.md` is the **source of truth** for the presentation. Generate HTML/PPTX/PDF only from this file (not from the template).

---

## Step 7.7 - Generate HTML via Marp

Convert Markdown to HTML using Marp CLI.

```bash
# Check if Marp is installed
marp --version

# If not installed, skip HTML generation with warning
# "Marp CLI not installed. Output is .md only."

# Generate HTML
marp {output_md_path} -o {output_html_path} --html --allow-local-files
```

### Marp Command Options

| Option | Purpose |
|--------|---------|
| `--html` | Enable HTML tags in markdown |
| `--allow-local-files` | Allow local image files |
| `--theme` | Use custom theme (optional) |
| `--pdf` | Generate PDF (optional) |

```python
import subprocess
import shutil

def generate_html(md_path, html_path):
    """
    Generate HTML presentation using Marp CLI.
    """
    # Check if Marp is installed
    if not shutil.which('marp'):
        print("WARNING: Marp CLI not installed. Output is .md only.")
        print("Install with: npm install -g @marp-team/marp-cli")
        return False

    try:
        result = subprocess.run(
            ['marp', md_path, '-o', html_path, '--html', '--allow-local-files'],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print(f"[OK] Generated HTML: {html_path}")
            return True
        else:
            print(f"[FAIL] Marp error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("[FAIL] Marp timed out")
        return False
    except Exception as e:
        print(f"[FAIL] Marp failed: {e}")
        return False

# Generate HTML
output_html_path = output_md_path.replace('.md', '.html')
html_success = generate_html(output_md_path, output_html_path)
```

---

## Step 7.8 - Generate PPTX via Marp (Required)

Use the populated `.md` as the source of truth and export a PowerPoint deck.

```bash
# Generate PPTX (from the populated markdown)
marp {output_md_path} -o {output_pptx_path} --allow-local-files
```

```python
def generate_pptx(md_path, pptx_path):
    """
    Generate PPTX presentation using Marp CLI.
    """
    if not shutil.which('marp'):
        print("WARNING: Marp CLI not installed. Output is .md only.")
        return False

    try:
        result = subprocess.run(
            ['marp', md_path, '-o', pptx_path, '--allow-local-files'],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            print(f"[OK] Generated PPTX: {pptx_path}")
            return True
        else:
            print(f"[FAIL] PPTX generation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"[FAIL] PPTX generation failed: {e}")
        return False

output_pptx_path = output_md_path.replace('.md', '.pptx')
pptx_success = generate_pptx(output_md_path, output_pptx_path)
```

---

## Step 7.9 - Generate PDF (Optional)

```python
def generate_pdf(md_path, pdf_path):
    """
    Generate PDF presentation using Marp CLI.
    Requires Chrome/Chromium for PDF generation.
    """
    if not shutil.which('marp'):
        return False

    try:
        result = subprocess.run(
            ['marp', md_path, '-o', pdf_path, '--html', '--allow-local-files', '--pdf'],
            capture_output=True,
            text=True,
            timeout=120  # PDF takes longer
        )

        if result.returncode == 0:
            print(f"[OK] Generated PDF: {pdf_path}")
            return True
        else:
            print(f"[FAIL] PDF generation failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"[FAIL] PDF generation failed: {e}")
        return False

# Optionally generate PDF
output_pdf_path = output_md_path.replace('.md', '.pdf')
# pdf_success = generate_pdf(output_md_path, output_pdf_path)
```

---

## Step 7.10 - Verify Output Files

```python
import os

def verify_outputs(client_name):
    """
    Verify all expected output files exist.
    """
    expected_files = [
        f"output/{client_name}/presentation.md",
        f"output/{client_name}/presentation.html",
        f"output/{client_name}/presentation.pptx",
        f"output/{client_name}/charts/answer_rate_gauge.png",
        f"output/{client_name}/charts/pain_windows_heatmap.png",
        f"output/{client_name}/charts/miss_distribution.png",
        f"output/{client_name}/charts/hourly_volume.png",
        f"output/{client_name}/charts/daily_pattern.png",
        f"output/{client_name}/charts/fte_coverage.png",
    ]

    results = {}
    for filepath in expected_files:
        exists = os.path.exists(filepath)
        results[filepath] = exists
        status = "[OK]" if exists else "[FAIL]"
        print(f"{status} {filepath}")

    return results

verify_outputs(CLIENT_NAME.replace(' ', '_'))
```

### Deterministic Render + Verification (Recommended)

From the `phone_to_present/` directory:
```bash
python scripts/render_verify.py output/<client_slug>/presentation.md
```
This fails fast on missing images / unreplaced variables and writes a render manifest (hashes + slide count).

---

## Output Files from Phase 7

```
output/
└── <client_slug>/
    ├── presentation.md    # Populated Marp markdown
    ├── presentation.html  # Generated HTML (if Marp installed)
    ├── presentation.pptx  # Generated PPTX (if Marp installed)
    ├── presentation.pdf   # Generated PDF (optional)
    └── charts/
        ├── answer_rate_gauge.png
        ├── pain_windows_heatmap.png
        ├── miss_distribution.png
        ├── hourly_volume.png
        ├── daily_pattern.png
        └── fte_coverage.png
```

---

## Troubleshooting

### Marp Not Installed

```
WARNING: Marp CLI not installed. Output is .md only.
Install with: npm install -g @marp-team/marp-cli
```

The .md file can still be viewed in any Marp-compatible viewer or VS Code with Marp extension.

### Unreplaced Variables

If you see `{{VARIABLE}}` in the output, check:
1. Variable name spelling matches exactly
2. Variable was calculated in the correct phase
3. Variable was added to `all_variables` dictionary

### Chart Images Not Showing

1. Verify charts exist in `output/<client_slug>/charts/` (or your configured output folder)
2. Check image paths are relative to the .md file
3. For HTML, ensure `--allow-local-files` flag was used

---

## Slide 18: Paths Forward — Construction Guide (v4.0)

Slide 18 is the "Paths Forward" comparison table. This slide requires special HTML/CSS construction for optimal rendering in Marp.

### Design Philosophy

The v4.0 design maximizes table readability by:

1. **No separate title** — Table fills the entire slide
2. **Header subtitles** — Column headers include descriptive subtitles explaining each option
3. **Centered table** — Natural width with gray slide background on both sides
4. **Icon-based status** — Visual checkmarks, warnings, and X marks
5. **Prominent recommendation** — "★ MOST POPULAR" gold badge on RHC column
6. **Clear pricing** — Bottom rows show weekly investment and savings vs DIY

---

### Column Layout (Standard 4-Column)

| Column | Header Title | Subtitle | Background |
|--------|--------------|----------|------------|
| Feature | Feature | What's included | Navy `#1e293b` |
| DIY Staffing | DIY Staffing | You handle it | Navy (grayed text) |
| Inbound Answering | Inbound Answering | Basic coverage | Navy `#1e293b` |
| **RHC** | Remote Hospitality Center | Full patient ops | **Teal gradient** `#0d9488` |
| RHC + Growth | RHC + Growth | Scale & consult | Navy `#1e293b` |

---

### Optional 5-Column Layout (with Pilot)

When including a Pilot program, add a column between DIY and Inbound:

| Column | Header Title | Subtitle | Badge |
|--------|--------------|----------|-------|
| Feature | Feature | What's included | — |
| DIY Staffing | DIY Staffing | You handle it | — |
| **Pilot** | Pilot Program | Base coverage | **Yellow "SLA" badge** |
| Inbound Answering | Inbound Answering | Basic coverage | Green checkmark (SLA met) |
| **RHC** | Remote Hospitality Center | Full patient ops | **"★ MOST POPULAR"** |
| RHC + Growth | RHC + Growth | Scale & consult | Green checkmark (SLA met) |

**SLA Badge Logic:**
- **Yellow/Amber badge** = SLA target (e.g., 90% answer rate) — shown on Pilot column
- **Green checkmark** = SLA exceeded — shown on Inbound, RHC, RHC+ columns
- RHC remains the **preferred/recommended** option regardless of Pilot column

---

### Required CSS (add to Marp style block)

```css
/* Paths Forward Container - centers table on slide */
.pf-container {
  font-family: 'Inter', -apple-system, sans-serif;
  padding: 0;
  margin: 0 auto;
  display: table;
}

/* Icon base styles */
.pf-icon {
  width: 16px;
  height: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

/* Icon variants */
.pf-icon-check {
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
  color: #059669;
}
.pf-icon-warn {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  color: #d97706;
}
.pf-icon-x {
  background: #f1f5f9;
  color: #94a3b8;
}

/* Table base */
.pf-table {
  border-collapse: collapse;
  font-size: 0.38em;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* Header cells */
.pf-table th {
  padding: 8px 12px;
  text-align: center;
  font-weight: 700;
  border-bottom: 3px solid rgba(0,0,0,0.1);
  background: #1e293b;
  color: #f8fafc;
  white-space: nowrap;
}
.pf-table th:first-child {
  text-align: left;
  padding-left: 12px;
}

/* RHC column header - teal gradient */
.pf-table th.pf-rhc {
  background: linear-gradient(135deg, #0d9488, #0f766e);
}

/* Pilot column header */
.pf-table th.pf-pilot {
  background: #1e293b;
}

/* Data cells */
.pf-table td {
  padding: 6px 10px;
  text-align: center;
  border-bottom: 1px solid #e2e8f0;
  line-height: 1.35;
}
.pf-table td:first-child {
  text-align: left;
  padding-left: 14px;
  font-weight: 600;
  color: #1e293b;
}

/* RHC column cells - light teal tint */
.pf-table td.pf-rhc {
  background: rgba(13,148,136,0.06);
}

/* Zebra striping */
.pf-table tr:nth-child(even) td {
  background: #f8fafc;
}
.pf-table tr:nth-child(even) td.pf-rhc {
  background: rgba(13,148,136,0.10);
}

/* "MOST POPULAR" badge - gold/amber */
.pf-badge {
  display: inline-block;
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  color: #1e293b;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.65em;
  font-weight: 800;
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* SLA badges */
.pf-sla-badge {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 0.6em;
  font-weight: 700;
  margin-bottom: 3px;
}
.pf-sla-yellow {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  color: #92400e;
}
.pf-sla-green {
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
  color: #065f46;
}

/* Header text */
.pf-header-title {
  font-weight: 700;
  color: #f8fafc;
  font-size: 1em;
}
.pf-header-sub {
  font-size: 0.7em;
  color: rgba(255,255,255,0.7);
  font-weight: 400;
  margin-top: 2px;
}

/* Pricing rows */
.pf-price-row td {
  padding: 8px 10px !important;
  background: #f1f5f9 !important;
  border-top: 3px solid #cbd5e1;
}
.pf-price-row td.pf-rhc {
  background: rgba(13,148,136,0.12) !important;
}
.pf-price {
  font-weight: 800;
  font-size: 1.3em;
}
.pf-price-diy {
  color: #9ca3af;
  text-decoration: line-through;
}
.pf-price-rhc {
  color: #0d9488;
  font-size: 1.4em;
}

/* Savings display */
.pf-savings {
  color: #059669;
  font-weight: 700;
}
.pf-savings-badge {
  background: linear-gradient(135deg, #059669, #10b981);
  color: white;
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 800;
  box-shadow: 0 2px 4px rgba(5,150,105,0.3);
}
```

---

### SVG Icons

**Checkmark (Green — "We handle it"):**
```html
<span class="pf-icon pf-icon-check">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" width="14" height="14">
    <polyline points="20 6 9 17 4 12"></polyline>
  </svg>
</span>
```

**Warning (Amber — "You manage"):**
```html
<span class="pf-icon pf-icon-warn">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="14" height="14">
    <circle cx="12" cy="12" r="10"></circle>
    <line x1="12" y1="8" x2="12" y2="12"></line>
    <line x1="12" y1="16" x2="12.01" y2="16"></line>
  </svg>
</span>
```

**X Mark (Gray — "Not included"):**
```html
<span class="pf-icon pf-icon-x">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" width="14" height="14">
    <line x1="18" y1="6" x2="6" y2="18"></line>
    <line x1="6" y1="6" x2="18" y2="18"></line>
  </svg>
</span>
```

---

### HTML Structure (Standard 4-Column)

```html
<div class="pf-container">
<table class="pf-table">
<thead>
<tr>
  <th>
    <div class="pf-header-title">Feature</div>
    <div class="pf-header-sub">What's included</div>
  </th>
  <th>
    <div class="pf-header-title" style="color:#94a3b8;">DIY Staffing</div>
    <div class="pf-header-sub" style="color:#64748b;">You handle it</div>
  </th>
  <th>
    <div class="pf-header-title">Inbound Answering</div>
    <div class="pf-header-sub">Basic coverage</div>
  </th>
  <th class="pf-rhc">
    <div class="pf-badge">★ Most Popular</div>
    <div class="pf-header-title">Remote Hospitality Center</div>
    <div class="pf-header-sub">Full patient ops</div>
  </th>
  <th>
    <div class="pf-header-title">RHC + Growth</div>
    <div class="pf-header-sub">Scale & consult</div>
  </th>
</tr>
</thead>
<tbody>
  <!-- Feature rows -->
  <tr>
    <td>Live Inbound Calls</td>
    <td><span class="pf-icon pf-icon-warn"><!-- warning SVG --></span></td>
    <td><span class="pf-icon pf-icon-check"><!-- check SVG --></span></td>
    <td class="pf-rhc"><span class="pf-icon pf-icon-check"><!-- check SVG --></span></td>
    <td><span class="pf-icon pf-icon-check"><!-- check SVG --></span></td>
  </tr>
  <!-- ... additional feature rows ... -->

  <!-- Pricing rows -->
  <tr class="pf-price-row">
    <td><strong>Weekly Investment</strong></td>
    <td><span class="pf-price pf-price-diy">${{HIRE_WEEKLY}}</span>/wk</td>
    <td><span class="pf-price" style="color:#5a7a84;">${{INBOUND_WEEKLY}}</span>/wk</td>
    <td class="pf-rhc"><span class="pf-price pf-price-rhc">${{RHC_WEEKLY}}</span>/wk</td>
    <td><span class="pf-price" style="color:#5a7a84;">${{RHC_GROWTH_WEEKLY}}</span>/wk</td>
  </tr>
  <tr class="pf-price-row">
    <td><strong>vs. DIY Staffing</strong></td>
    <td style="color:#8a9a9e;">—</td>
    <td><span class="pf-savings">Save $&lt;HIRE_WEEKLY - INBOUND_WEEKLY&gt;/wk</span></td>
    <td class="pf-rhc"><span class="pf-savings-badge">Save $&lt;HIRE_WEEKLY - RHC_WEEKLY&gt;/wk</span></td>
    <td><span class="pf-savings">Save $&lt;HIRE_WEEKLY - RHC_GROWTH_WEEKLY&gt;/wk</span></td>
  </tr>
</tbody>
</table>
</div>
```

---

### Adding Pilot Column (5-Column)

Insert this column header after DIY Staffing:

```html
<th class="pf-pilot">
  <div class="pf-sla-badge pf-sla-yellow">90% SLA</div>
  <div class="pf-header-title">Pilot Program</div>
  <div class="pf-header-sub">Base coverage</div>
</th>
```

Add corresponding `<td>` cells in each row after the DIY column.

When Pilot is included:
- Feature rows: Pilot mapping matches **Inbound Answering** (Pilot is inbound answering only).
- Pricing rows: show Pilot weekly (`PILOT_WEEKLY`) and Pilot savings vs DIY (`HIRE_WEEKLY - PILOT_WEEKLY`).

---

### Feature Row Reference (Standard Features)

| Feature | DIY | Inbound | RHC | RHC+ |
|---------|-----|---------|-----|------|
| Live Inbound Calls | warn | check | check | check |
| Text Messaging | warn | check | check | check |
| Appointment Requests | warn | check | check | check |
| AI Overflow/After-Hours | x | check | check | check |
| Insurance Verification | warn | x | check | check |
| Appointment Confirmations | warn | x | check | check |
| Recalls & Reactivations | warn | x | check | check |
| Waitlist Management | warn | x | check | check |
| Real-Time Dashboard | x | x | check | check |
| Monthly Consulting | x | x | x | check |
| Recruiting & Training | warn | check | check | check |
| PTO & Turnover | warn | check | check | check |

**Icon meanings:**
- `check` = Green checkmark (MyBCAT handles)
- `warn` = Amber warning (You manage)
- `x` = Gray X (Not included)

---

### Pre-Flight Checklist (Slide 18)

Before finalizing:
- [ ] Table is centered with gray background visible on both sides
- [ ] No extra white space extending beyond table edges
- [ ] All feature rows visible (12 features + pricing + savings)
- [ ] Bottom margin exists (not touching slide edge)
- [ ] RHC column has teal header gradient
- [ ] "★ MOST POPULAR" badge visible on RHC
- [ ] DIY column text is grayed out
- [ ] DIY price has strikethrough
- [ ] RHC savings has green badge with shadow
- [ ] All icons render correctly (check, warning, X)
- [ ] Header subtitles visible under each column title
- [ ] If Pilot column included: yellow SLA badge shows on Pilot header

---

### Color Reference (Slide 18)

| Element | Hex Code | Usage |
|---------|----------|-------|
| Navy (headers) | `#1e293b` | Header backgrounds, primary text |
| Teal (RHC) | `#0d9488` | RHC column, checkmarks, savings |
| Teal Dark | `#0f766e` | RHC gradient end |
| Gold/Amber | `#fbbf24` | "Most Popular" badge |
| Amber (warning) | `#d97706` | Warning icon stroke |
| Green (success) | `#059669` | Checkmark icon, savings text |
| Gray (muted) | `#94a3b8` | X icons, DIY text |
| Light Gray | `#f8fafc` | Zebra stripe, backgrounds |
| Border Gray | `#e2e8f0` | Row borders |
| Price Row BG | `#f1f5f9` | Pricing row background |
