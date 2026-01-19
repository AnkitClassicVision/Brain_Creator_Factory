# Phase 7b: Presentation QA & Visual Verification

## Overview

After generating the presentation, perform quality assurance checks on both the .md source and rendered .html output. This ensures design consistency, readability, and proper layout.

---

## Step 7b.1 - Open and Review HTML Presentation

**REQUIRED:** Open the generated HTML file in a browser and visually inspect each slide.

```bash
# Open the HTML presentation
open output/<client_slug>/presentation.html

# Or on Linux:
xdg-open output/<client_slug>/presentation.html
```

---

## Step 7b.1b - Open and Review PPTX (REQUIRED)

**REQUIRED:** Open the generated PowerPoint file and spot-check slides.

Why: PPTX rendering can differ from HTML (fonts, sizing, table wrapping, image scaling). Catch issues before the client sees them.

Checklist (minimum):
- Title slide renders correctly (no overflow)
- Section divider slides have correct background colors (no white-on-white)
- Tables are not truncated
- Images/charts appear on the correct slides and are readable

---

## Step 7b.2 - Visual Verification Checklist

### For EACH Slide, Check:

| Check | Pass | Fail Action |
|-------|------|-------------|
| **White Space** | Content has padding on all 4 sides | Reduce content or use side-by-side layout |
| **No Text Cut-Off** | All text fully visible | Shrink font, split slide, or restructure |
| **No White-on-White** | All text readable against background | Fix contrast (see Section 7b.3) |
| **No Emojis** | No emoji characters in any slide | Remove emojis; keep copy professional and text-only |
| **Images Load** | Charts/images display correctly | Check file paths |
| **Alignment** | Content properly aligned | Adjust CSS or markdown |
| **Overflow** | Nothing extends beyond slide edges | Reduce content or change layout |

---

## Step 7b.3 - White-on-White Text Fix

### Problem Slides (Common Issues)

Section divider slides often have white text that becomes invisible on white backgrounds.

**Typical Problem Areas:**
- "PART 1: THE DATA" section headers
- "PART 2: THE IMPACT" section headers
- "PART 3: THE SOLUTION" section headers
- Any slide with `class: invert` or dark backgrounds

### Fix: Ensure Background Colors Apply

In the Marp template, section dividers should have explicit backgrounds:

```markdown
<!-- _class: lead invert -->
<!-- _backgroundColor: #006064 -->

# PART 1
## THE DATA
```

### Verification

For each section divider slide:
1. Check that background color is visible (not white)
2. Check that text contrasts against background
3. If white-on-white: add `<!-- _backgroundColor: #006064 -->` directive

---

## Step 7b.4 - Layout Verification

### Stacking vs Side-by-Side Rules

| Content Type | Layout | When to Change |
|--------------|--------|----------------|
| 2-3 stat cards | Side-by-side | If stacked causes overflow |
| Comparison tables | Full width | If columns cut off, reduce columns |
| Chart + text | Side-by-side (50/50) | If stacked, chart too small |
| Long lists | 2 columns | If >6 items and causes overflow |
| Single chart | Centered, 60-70% width | If too large, scale down |

### Two-Column Layout Template

When content overflows vertically, convert to side-by-side:

```markdown
<div class="columns">
<div class="column">

### Left Content
- Item 1
- Item 2
- Item 3

</div>
<div class="column">

### Right Content
- Item 4
- Item 5
- Item 6

</div>
</div>
```

### CSS for Two-Column Layout

Ensure this CSS is in the Marp theme or slide header:

```css
<style>
.columns {
  display: flex;
  gap: 2rem;
}
.column {
  flex: 1;
}
</style>
```

---

## Step 7b.5 - Slide-by-Slide QA Checklist

### Opening Section (Slides 1-3)

| Slide | Check | Issue | Fix |
|-------|-------|-------|-----|
| Title | Client name visible, tagline readable | Text overflow | Shorten tagline |
| Title | Date range shows correctly | Missing variable | Check {{DATE_RANGE}} |
| Who We Are | Logo loads | 404 error | Check assets/mybcat_logo.png |
| The Question | Text has dramatic impact | Too cluttered | Reduce text, add whitespace |

### Diagnosis Section (Slides 4-8)

| Slide | Check | Issue | Fix |
|-------|-------|-------|-----|
| Section Divider | "PART 1" visible (not white-on-white) | White text on white BG | Add backgroundColor directive |
| Executive Summary | 4 stat cards fit | Overflow | Use 2x2 grid or reduce size |
| The Grade | Gauge chart loads | Missing image | Check charts/ path |
| Root Cause | Pie chart centered | Off-center | Add alignment CSS |
| Pain Windows | Heatmap readable | Too small | Increase size or remove legend |
| Worst Hours | 3 cards visible | Cut off | Use horizontal layout |

### Prognosis Section (Slides 9-11)

| Slide | Check | Issue | Fix |
|-------|-------|-------|-----|
| Section Divider | "PART 2" visible | White-on-white | Add backgroundColor |
| Revenue Impact | Numbers formatted | Raw numbers | Check currency formatting |
| 3 Paths | Table columns fit | Overflow | Reduce column widths |

### Treatment Section (Slides 12-15)

| Slide | Check | Issue | Fix |
|-------|-------|-------|-----|
| Section Divider | "PART 3" visible | White-on-white | Add backgroundColor |
| Services Table | All rows visible | Cut off | Split into 2 slides or shrink |
| FTE Coverage | Chart loads and is legible | Missing | Check charts/fte_coverage.png |
| Next Steps | CTA prominent | Buried in text | Add visual emphasis |

### Appendix

| Slide | Check | Issue | Fix |
|-------|-------|-------|-----|
| Assumptions | Text readable | Too small | Increase font or split |
| Data Integrity | Table fits | Overflow | Use scrollable or split |

---

## Step 7b.6 - Common Fixes

### Fix 1: Content Overflow (Vertical)

**Problem:** Content extends below slide bottom

**Solutions (in order of preference):**
1. Convert to two-column layout
2. Reduce font size (minimum 14pt)
3. Split into two slides
4. Remove less critical content

### Fix 2: White-on-White Text

**Problem:** White text invisible on white background

**Solution:** Add explicit background color directive:

```markdown
<!-- _backgroundColor: #006064 -->
<!-- _color: #ffffff -->

# Section Title
```

### Fix 3: Image Too Large

**Problem:** Chart/image overflows or crowds text

**Solution:** Add size constraints:

```markdown
![Chart](charts/example.png)
<!-- Use HTML for size control -->
<img src="charts/example.png" width="600" />
```

### Fix 4: Table Too Wide

**Problem:** Table columns cut off on right side

**Solutions:**
1. Reduce column count
2. Abbreviate headers
3. Use smaller font: `<small>table content</small>`
4. Split into multiple tables

### Fix 5: Cards Not Aligned

**Problem:** Stat cards or boxes misaligned

**Solution:** Use flexbox grid:

```markdown
<div style="display: flex; justify-content: space-around; gap: 1rem;">
  <div class="card">Card 1</div>
  <div class="card">Card 2</div>
  <div class="card">Card 3</div>
</div>
```

---

## Step 7b.7 - Automated Checks

Run these automated checks before visual review:

### Check 1: Unreplaced Variables

```bash
# Find any {{VARIABLE}} still in the output
grep -o '{{[A-Z_]*}}' output/*.md | sort | uniq
```

If any output: variable replacement failed. Check Phase 7 variable dictionary.

### Check 2: Missing Images

```bash
# Extract image references from markdown
grep -oP '!\[.*?\]\(\K[^)]+' output/*.md | while read img; do
  if [ ! -f "output/$img" ]; then
    echo "MISSING: $img"
  fi
done
```

### Check 2b: PPTX Exists + Has Slides

```bash
ls -lh output/*.pptx
```

Optional: use the deterministic renderer (recommended):
```bash
python scripts/render_verify.py output/<client_slug>/presentation.md
```
This also runs:
- an automated slide-by-slide whitespace check on the PPTX export (fails if content is too close to any edge)
- an emoji scan (fails if any emoji characters exist in the `.md`)
See `presentation.render_manifest.json` for per-slide margins.

### Check 3: Marp Directives Valid

```bash
# Check for malformed directives
grep -n '<!-- _' output/*.md | grep -v 'class:\|backgroundColor:\|color:\|paginate:'
```

---

## Step 7b.8 - Visual Verification with Screenshot

**RECOMMENDED:** Use visual verification agent to capture and review each slide.

```
For each slide in the presentation:
1. Navigate to slide
2. Capture screenshot
3. Check for:
   - Text readability (no white-on-white)
   - Content within bounds (whitespace on all sides)
   - Images loading correctly
   - Proper alignment
4. Flag any issues
```

### Visual Verification Criteria

| Criterion | Pass | Fail |
|-----------|------|------|
| Top margin | >20px whitespace | Content touches top |
| Bottom margin | >20px whitespace | Content touches bottom |
| Left margin | >40px whitespace | Content touches left |
| Right margin | >40px whitespace | Content touches right |
| Text contrast | >4.5:1 ratio | Low contrast or invisible |
| Image clarity | Sharp, not pixelated | Blurry or broken |
| Font size | >12pt body, >18pt headers | Too small to read |

---

## Step 7b.8b - Red Team Review (Accuracy + Flow)

After you believe the deck is ready, run a final red-team pass focused on:
- **Math correctness** (FTE, pricing totals, weekly→monthly conversions)
- **Consistency** (terminology, option names, numbers match tables/summary)
- **Look & flow** (clean story arc, no clutter, whitespace on all sides)
- **Client-safe copy** (no emojis, no internal math, no jargon overload)

If you have an `agent-team` review capability, use it here; otherwise have a second reviewer do this pass before delivery.

---

## Step 7b.9 - QA Sign-Off

After completing all checks, confirm:

```
═══════════════════════════════════════════════════════════════════
                    PRESENTATION QA COMPLETE
═══════════════════════════════════════════════════════════════════

Slides Reviewed: XX / XX
Issues Found: X
Issues Fixed: X

Visual Checks:
  [OK] All text readable (no white-on-white)
  [OK] Whitespace on all slide edges
  [OK] All images loading
  [OK] No content overflow
  [OK] Section dividers have colored backgrounds

Ready for client presentation: YES / NO

═══════════════════════════════════════════════════════════════════
```

---

## STOP AND FIX IF:

- **Any slide has white-on-white text** → Add backgroundColor directive
- **Any slide has content touching edges** → Restructure layout or reduce content
- **Any emoji characters appear anywhere** → Remove them (no emojis in client decks)
- **Any chart/image missing** → Regenerate or check paths
- **Any {{VARIABLE}} unreplaced** → Fix variable mapping in Phase 7
- **Table columns cut off** → Restructure table or split slide

---

## Output

After QA, the following should be confirmed:

```
[OK] output/<client_slug>/presentation.md   - Variables replaced, no issues
[OK] output/<client_slug>/presentation.html - Renders correctly, all slides pass QA
[OK] All 6 template charts loading in presentation
[OK] All section dividers have colored backgrounds (not white)
[OK] All slides have adequate whitespace margins
```
