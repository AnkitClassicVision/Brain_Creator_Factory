# Phase 6: Chart Generation

## Overview

Generate the charts referenced by the Marp template. The current `templates/presentation_template.md` expects **6 required charts** in `<out_dir>/charts/` (for example: `output/<client_slug>/charts/`).

**Source of truth:** `workflow/template_contract.md` (generated from the template via `python scripts/generate_template_contract.py`).

**Required chart filenames (template-referenced)**
- `answer_rate_gauge.png`
- `pain_windows_heatmap.png`
- `miss_distribution.png`
- `hourly_volume.png`
- `daily_pattern.png`
- `fte_coverage.png`

Optional charts (only generate if your deck references them) are listed at the bottom.

---

## Global Chart Specifications

### Dimensions & Format

| Property | Value |
|----------|-------|
| Default Width | 1000px |
| Default Height | 700px |
| Format | PNG |
| DPI | 150 |
| Background | White (#FFFFFF) |

### Color Palette

| Name | Hex Code | Use For |
|------|----------|---------|
| Brand Teal | #006064 | Primary/positive |
| Success Green | #10B981 | Answered, good metrics |
| Warning Yellow | #EAB308 | Caution, medium risk |
| Danger Red | #E63946 | Missed, high risk |
| Light Green | #D1FAE5 | Low miss rate zones |
| Light Yellow | #FEF3C7 | Medium miss rate zones |
| Light Red | #FEE2E2 | High miss rate zones |
| Gray | #6B7280 | Secondary, labels |
| Light Gray | #F3F4F6 | Backgrounds, gridlines |

### Typography

| Element | Font | Size |
|---------|------|------|
| Title | Lato Bold | 24pt |
| Subtitle | Lato | 18pt |
| Axis Labels | Lato | 14pt |
| Tick Labels | Lato | 12pt |
| Annotations | Lato | 12pt |
| Legend | Lato | 12pt |

---

## Chart 1: Answer Rate Gauge

**Filename:** `answer_rate_gauge.png`

**Purpose:** Visual grade representation of overall answer rate.

### Specifications

```python
# Gauge chart showing answer rate as percentage
# Zones:
# - Green (95-100%): Grade A
# - Light Green (90-95%): Grade B
# - Yellow (80-90%): Grade C
# - Orange (70-80%): Grade D
# - Red (0-70%): Grade F

gauge_zones = [
    {'range': [0, 70], 'color': '#FEE2E2'},    # Red - F
    {'range': [70, 80], 'color': '#FED7AA'},   # Orange - D
    {'range': [80, 90], 'color': '#FEF3C7'},   # Yellow - C
    {'range': [90, 95], 'color': '#D1FAE5'},   # Light Green - B
    {'range': [95, 100], 'color': '#10B981'}   # Green - A
]

# Needle points to ANSWER_RATE
# Center text shows: "{ANSWER_RATE}%" and "Grade: {GRADE}"
```

### Layout

```
┌─────────────────────────────────────┐
│         Answer Rate Performance      │
│                                      │
│           ┌─────────────┐            │
│        ╱                   ╲         │
│      ╱    F   D  C  B   A   ╲        │
│     │   ◀────────┼──────────│        │
│      ╲         ▲            ╱        │
│        ╲      │           ╱          │
│           └───┼───────┘              │
│               │                      │
│          {ANSWER_RATE}%              │
│          Grade: {GRADE}              │
│                                      │
│    Industry benchmark: 90%+          │
└─────────────────────────────────────┘
```

---

## Chart 2: Pain Windows Heatmap

**Filename:** `pain_windows_heatmap.png`

**Purpose:** Show miss rate by hour and day of week.

### Specifications

```python
# 2D heatmap: X = Day of Week, Y = Hour of Day
# Color scale: Green (low) → Yellow (medium) → Red (high)
# Data source: PAIN_WINDOWS_MATRIX

heatmap_config = {
    'x_axis': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    'y_axis': range(8, 18),  # 8am-5pm
    'color_scale': {
        0: '#D1FAE5',      # 0-5% miss rate
        5: '#D1FAE5',
        10: '#FEF3C7',     # 5-15% miss rate
        15: '#FEE2E2',     # 15%+ miss rate
        100: '#E63946'     # Max
    },
    'annotations': True,   # Show miss rate in each cell
    'highlight_worst': True  # Bold border on worst 3 cells
}
```

### Layout

```
┌─────────────────────────────────────────────────┐
│            Pain Windows: Miss Rate by Hour       │
│                                                  │
│       Mon   Tue   Wed   Thu   Fri   Sat   Sun   │
│  8am  [5%]  [3%]  [4%]  [2%]  [6%]  [8%]  [-]   │
│  9am  [12%] [8%]  [7%]  [9%]  [15%] [5%]  [-]   │
│ 10am  [4%]  [5%]  [3%]  [4%]  [5%]  [4%]  [-]   │
│ 11am  [6%]  [7%]  [8%]  [5%]  [9%]  [6%]  [-]   │
│ 12pm  [18%] [15%] [20%] [17%] [22%] [-]   [-]   │
│  1pm  [14%] [12%] [16%] [11%] [18%] [-]   [-]   │
│  2pm  [5%]  [6%]  [4%]  [7%]  [8%]  [-]   [-]   │
│  3pm  [4%]  [5%]  [3%]  [4%]  [6%]  [-]   [-]   │
│  4pm  [7%]  [8%]  [6%]  [5%]  [9%]  [-]   [-]   │
│  5pm  [10%] [9%]  [8%]  [7%]  [12%] [-]   [-]   │
│                                                  │
│  Legend: ■ 0-5%  ■ 5-15%  ■ 15%+                │
└─────────────────────────────────────────────────┘
```

---

## Chart 3: Process vs Capacity Pie

**Filename:** `miss_distribution.png`

**Purpose:** Show root cause breakdown of missed calls (THE AHA MOMENT).

### Specifications

```python
# Pie chart with 2 segments:
# - Process Issues (red): Missed when concurrency = 1
# - Capacity Issues (yellow): Missed when concurrency > 1

pie_config = {
    'segments': [
        {
            'label': 'Process Issues',
            'value': PROCESS_MISS_PCT,
            'color': '#E63946',
            'description': 'Missed when only 1 call active'
        },
        {
            'label': 'Capacity Issues',
            'value': CAPACITY_MISS_PCT,
            'color': '#EAB308',
            'description': 'Missed when multiple calls active'
        }
    ],
    'center_text': f"{TOTAL_MISSED} missed calls",
    'explode': [0.05, 0]  # Slightly separate process slice
}
```

### Layout

```
┌─────────────────────────────────────┐
│      Why Calls Are Being Missed      │
│                                      │
│           ┌─────────────┐            │
│        ╱                   ╲         │
│      ╱      Process         ╲        │
│     │       Issues           │       │
│     │        59%             │       │
│      ╲                      ╱        │
│        ╲    Capacity      ╱          │
│           └──Issues ─────┘           │
│              41%                     │
│                                      │
│  Process = Staff didn't answer       │
│  Capacity = Too many calls at once   │
└─────────────────────────────────────┘
```

---

## Chart 4: Hourly Volume Bar Chart

**Filename:** `hourly_volume.png`

**Purpose:** Show call volume distribution across hours.

### Specifications

```python
# Stacked bar chart: Answered (green) + Missed (red)
# X-axis: Hour (8am - 6pm typically)
# Y-axis: Number of calls

bar_config = {
    'x_axis': list(range(8, 18)),  # Business hours
    'series': [
        {
            'name': 'Answered',
            'data': HOURLY_ANSWERED,  # Dict by hour
            'color': '#10B981'
        },
        {
            'name': 'Missed',
            'data': HOURLY_MISSED,  # Dict by hour
            'color': '#E63946'
        }
    ],
    'show_totals': True,
    'highlight_peak': PEAK_HOUR
}
```

### Layout

```
┌─────────────────────────────────────────────────┐
│            Hourly Call Distribution              │
│                                                  │
│  150 ┤                                          │
│      │                   ████                   │
│  100 ┤        ████ ████ ████ ████               │
│      │   ████ ████ ████ ████ ████ ████          │
│   50 ┤   ████ ████ ████ ████ ████ ████ ████     │
│      │   ████ ████ ████ ████ ████ ████ ████ ████│
│    0 └───8am──9am─10am─11am─12pm──1pm──2pm──3pm─│
│                                                  │
│  Legend: ■ Answered  ■ Missed                   │
│  Peak hour: 11am with {PEAK_HOUR_VOLUME} calls  │
└─────────────────────────────────────────────────┘
```

---

## Chart 5: Daily Pattern Chart

**Filename:** `daily_pattern.png`

**Purpose:** Show call volume by day of week.

### Specifications

```python
# Grouped bar chart: Total calls per day
# With miss rate overlay line

daily_config = {
    'x_axis': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    'bars': {
        'data': DAILY_VOLUME,
        'color': '#006064'
    },
    'line': {
        'data': DAILY_MISS_RATE,
        'color': '#E63946',
        'label': 'Miss Rate %'
    },
    'dual_axis': True  # Volume on left, rate on right
}
```

### Layout

```
┌─────────────────────────────────────────────────┐
│              Weekly Call Pattern                 │
│                                                  │
│  Calls                              Miss Rate %  │
│  500 ┤                                     │ 25% │
│      │  ████                               │     │
│  400 ┤  ████ ████                          │ 20% │
│      │  ████ ████ ████ ████ ████          │     │
│  300 ┤  ████ ████ ████ ████ ████          │ 15% │
│      │  ████ ████ ████ ████ ████ ████     │     │
│  200 ┤  ████ ████ ████ ████ ████ ████     │ 10% │
│      │  ████ ████ ████ ████ ████ ████ ████│     │
│  100 ┤  ████ ████ ████ ████ ████ ████ ████│  5% │
│    0 └──Mon──Tue──Wed──Thu──Fri──Sat──Sun─│  0% │
│                                                  │
│  ■ Call Volume  ── Miss Rate                    │
└─────────────────────────────────────────────────┘
```

---

## Chart 6: FTE Coverage (Time-Weighted Concurrency)

**Filename:** `fte_coverage.png`

**Purpose:** Show time-weighted concurrency levels plus the CDF curve used to select `BASE_FTE` at the target coverage threshold (e.g., 90%).

### Specifications

```python
# Bars: % of time spent at each concurrency level (includes level 0)
# Line: CDF% excluding level 0
# Markers:
# - horizontal line at TARGET_COVERAGE (e.g., 90%)
# - vertical line at BASE_FTE (chosen from CDF)

levels = sorted(TIME_WEIGHTED_CONCURRENCY.keys())  # {level: seconds}
time_pct = seconds_at_level / total_seconds * 100

cdf_levels = [l for l in levels if l > 0]
cdf = cumsum(seconds_at_level[l]) / sum(seconds_at_level[l>0]) * 100
```

### Layout

```
┌─────────────────────────────────────────────────┐
│     Time-Weighted Concurrency (Open Hours)      │
│                                                  │
│  % of Time (bars) + CDF% (line)                 │
│                                                  │
│  40% ┤ ████                                     │
│      │ ████   ███                              │
│  20% ┤ ████   ███   ██                         │
│      │                                       ───│  CDF%
│   0% └─0──1──2──3──4──5──6──7──8──> level      │
│         ▲ BASE_FTE          ── 90% line         │
└─────────────────────────────────────────────────┘
```

---

## Chart Generation Workflow

```python
def generate_all_charts(output_dir="output/<client_slug>/charts/"):
    """
    Generate all required charts referenced by the template.
    Returns dict of {filename: success_bool}
    """
    import os
    os.makedirs(output_dir, exist_ok=True)

    results = {}

    charts = [
        ('answer_rate_gauge.png', generate_gauge_chart),
        ('pain_windows_heatmap.png', generate_heatmap),
        ('miss_distribution.png', generate_pie_chart),
        ('hourly_volume.png', generate_hourly_bars),
        ('daily_pattern.png', generate_daily_chart),
        ('fte_coverage.png', generate_fte_coverage)
    ]

    for filename, generator_func in charts:
        try:
            filepath = os.path.join(output_dir, filename)
            generator_func(filepath)
            results[filename] = True
            print(f"[OK] Generated {filename}")
        except Exception as e:
            results[filename] = False
            print(f"[FAIL] Failed {filename}: {e}")
            # Create placeholder
            create_placeholder(filepath, filename)

    return results
```

---

## Placeholder Generation

If a chart fails to generate, create a placeholder image.

```python
def create_placeholder(filepath, chart_name):
    """
    Create a simple placeholder image when chart generation fails.
    """
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new('RGB', (1000, 700), 'white')
    draw = ImageDraw.Draw(img)

    # Draw border
    draw.rectangle([10, 10, 990, 690], outline='#CCCCCC', width=2)

    # Draw text
    draw.text(
        (500, 350),
        f"Chart: {chart_name}\n[Generation Failed]",
        fill='#666666',
        anchor='mm'
    )

    img.save(filepath)
```

---

## Variables Required from Previous Phases

```
From Phase 3:
- ANSWER_RATE, GRADE
- PAIN_WINDOWS_MATRIX
- HOURLY_VOLUME, HOURLY_MISS_RATE
- DAILY_VOLUME, DAILY_MISS_RATE
- PEAK_HOUR, PEAK_HOUR_VOLUME

From Phase 4:
- PROCESS_MISS_PCT, CAPACITY_MISS_PCT
- TOTAL_MISSED
- TIME_WEIGHTED_CONCURRENCY (seconds by level), TARGET_COVERAGE, BASE_FTE

Optional (only if your deck uses optional cost/leak charts):
- HIRE_MONTHLY, RHC_MONTHLY, INBOUND_MONTHLY
- REVENUE_LEAK_MONTHLY, REVENUE_LEAK_ANNUAL
- INBOUND_SAVINGS_MONTHLY, RHC_SAVINGS_MONTHLY
```

---

## Output Files

All charts saved to `<out_dir>/charts/` (for example: `output/<client_slug>/charts/`):

```
output/
└── charts/
    ├── answer_rate_gauge.png
    ├── pain_windows_heatmap.png
    ├── miss_distribution.png
    ├── hourly_volume.png
    ├── daily_pattern.png
    └── fte_coverage.png
```

---

## Appendix: Optional Charts (Only If Added to Deck)

These are not referenced by the current template but can be added as optional slides.

### Optional Chart A: Cost Comparison Bar Chart
**Filename:** `cost_comparison.png`

### Optional Chart B: Revenue Leak Timeline
**Filename:** `revenue_leak.png`
