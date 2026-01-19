# Phase 3: Core Analysis

## IMPORTANT: Open Hours = Primary Analysis

**All main metrics (answer rate, miss rate, grade, missed calls/week) are calculated using OPEN HOURS data only.**

Closed hours data is tracked separately for reference but is NOT included in the primary performance metrics.

---

## Step 3.1 - Filter to Inbound Calls & Separate Open/Closed

The primary analysis focuses on **inbound calls during OPEN HOURS**.

```python
# Filter to inbound only
inbound_df = gold_df[gold_df['direction'] == 'inbound'].copy()

TOTAL_INBOUND_ALL = len(inbound_df)
TOTAL_OUTBOUND = len(gold_df[gold_df['direction'] == 'outbound'])
TOTAL_INTERNAL = len(gold_df[gold_df['direction'] == 'internal'])

# Validate we have inbound calls
if TOTAL_INBOUND_ALL == 0:
    # CRITICAL ERROR - cannot proceed
    raise ValueError("No inbound calls detected. Check direction column mapping.")

# ═══════════════════════════════════════════════════════════════════
# CRITICAL: Separate Open Hours vs Closed Hours
# ═══════════════════════════════════════════════════════════════════

# Open hours = PRIMARY analysis dataset
open_hours_df = inbound_df[inbound_df['is_open_hours'] == True].copy()
TOTAL_INBOUND = len(open_hours_df)  # This is the main metric

# Closed hours = SECONDARY dataset (for reference only)
closed_hours_df = inbound_df[inbound_df['is_open_hours'] == False].copy()
TOTAL_CLOSED = len(closed_hours_df)

# Percentage split
OPEN_PCT = round((TOTAL_INBOUND / TOTAL_INBOUND_ALL) * 100, 1) if TOTAL_INBOUND_ALL > 0 else 0
CLOSED_PCT = round((TOTAL_CLOSED / TOTAL_INBOUND_ALL) * 100, 1) if TOTAL_INBOUND_ALL > 0 else 0
```

**Store:** `TOTAL_INBOUND` (open hours only), `TOTAL_INBOUND_ALL`, `TOTAL_CLOSED`, `OPEN_PCT`, `CLOSED_PCT`

---

## Step 3.2 - Primary Metrics (OPEN HOURS ONLY)

**All main performance metrics are calculated from OPEN HOURS data only.**

```python
# ═══════════════════════════════════════════════════════════════════
# PRIMARY METRICS - OPEN HOURS ONLY
# ═══════════════════════════════════════════════════════════════════

# Count by disposition (OPEN HOURS)
answered = len(open_hours_df[open_hours_df['disposition_normalized'] == 'answered'])
missed = len(open_hours_df[open_hours_df['disposition_normalized'] == 'missed'])
voicemail = len(open_hours_df[open_hours_df['disposition_normalized'] == 'voicemail'])
abandoned = len(open_hours_df[open_hours_df['disposition_normalized'] == 'abandoned'])
redirected = len(open_hours_df[open_hours_df['disposition_normalized'] == 'redirected'])
unknown = len(open_hours_df[open_hours_df['disposition_normalized'] == 'unknown'])

# Calculate rates (exclude unknown from denominator for accuracy)
known_calls = TOTAL_INBOUND - unknown
if known_calls > 0:
    ANSWER_RATE = round((answered / known_calls) * 100, 1)
    MISS_RATE = round(((missed + abandoned) / known_calls) * 100, 1)
    VOICEMAIL_RATE = round((voicemail / known_calls) * 100, 1)
else:
    ANSWER_RATE = round((answered / TOTAL_INBOUND) * 100, 1) if TOTAL_INBOUND > 0 else 0
    MISS_RATE = round(((missed + abandoned) / TOTAL_INBOUND) * 100, 1) if TOTAL_INBOUND > 0 else 0
    VOICEMAIL_RATE = round((voicemail / TOTAL_INBOUND) * 100, 1) if TOTAL_INBOUND > 0 else 0

# Miss ratio (1 in X calls missed) - OPEN HOURS
if MISS_RATE > 0:
    MISS_RATIO = round(100 / MISS_RATE)
else:
    MISS_RATIO = "N/A"  # No missed calls

# Weekly metrics - OPEN HOURS ONLY
MISSED_CALLS_WEEK = round((missed + abandoned) / WEEKS_IN_RANGE)
ANSWERED_CALLS_WEEK = round(answered / WEEKS_IN_RANGE)
INBOUND_CALLS_WEEK = round(TOTAL_INBOUND / WEEKS_IN_RANGE)

# Store open hours counts
OPEN_ANSWERED = answered
OPEN_MISSED = missed + abandoned
OPEN_VOICEMAIL = voicemail
```

**Store:** `ANSWER_RATE`, `MISS_RATE`, `VOICEMAIL_RATE`, `MISS_RATIO`, `MISSED_CALLS_WEEK`, `ANSWERED_CALLS_WEEK`, `INBOUND_CALLS_WEEK`, `OPEN_ANSWERED`, `OPEN_MISSED`, `OPEN_VOICEMAIL`

**NOTE:** These are the PRIMARY metrics shown in the presentation. They represent performance during business hours when staff should be available to answer.

---

## Step 3.3 - Grade Assignment (Based on OPEN HOURS)

Assign letter grade based on **open hours answer rate**.

```python
def assign_grade(answer_rate):
    """
    Grade thresholds (based on OPEN HOURS performance):
    A: 95%+   - Excellent
    B: 90-94% - Good
    C: 80-89% - Needs Improvement
    D: 70-79% - Poor
    F: <70%   - Critical
    """
    if answer_rate >= 95:
        return 'A', 'Excellent'
    elif answer_rate >= 90:
        return 'B', 'Good'
    elif answer_rate >= 80:
        return 'C', 'Needs Improvement'
    elif answer_rate >= 70:
        return 'D', 'Poor'
    else:
        return 'F', 'Critical'

# Grade is based on OPEN HOURS answer rate
GRADE, GRADE_DESCRIPTION = assign_grade(ANSWER_RATE)

# ═══════════════════════════════════════════════════════════════════
# GRADE COLORS - Only A is green, B/C orange, D/F red
# ═══════════════════════════════════════════════════════════════════

def get_grade_colors(grade):
    """
    Assign colors for grade display.

    A grade (95%+) - GREEN (exceptional)
    B grade (90-94%) - ORANGE (needs attention)
    C grade (80-89%) - ORANGE (needs attention)
    D grade (70-79%) - RED (critical)
    F grade (<70%) - RED (critical)
    """
    if grade == 'A':
        return '#10B981', '#FFFFFF'  # Green background, white text
    elif grade in ['B', 'C']:
        return '#F97316', '#FFFFFF'  # Orange background, white text
    else:  # D or F
        return '#E63946', '#FFFFFF'  # Red background, white text

GRADE_BG_COLOR, GRADE_TEXT_COLOR = get_grade_colors(GRADE)
```

**Store:** `GRADE`, `GRADE_DESCRIPTION`, `GRADE_BG_COLOR`, `GRADE_TEXT_COLOR`

---

## Step 3.4 - Closed Hours Analysis (Secondary/Reference)

Track closed hours separately for context. **These metrics are NOT the primary focus.**

```python
# ═══════════════════════════════════════════════════════════════════
# SECONDARY METRICS - CLOSED HOURS (for reference only)
# ═══════════════════════════════════════════════════════════════════

# Closed hours metrics
CLOSED_ANSWERED = len(closed_hours_df[closed_hours_df['disposition_normalized'] == 'answered'])
CLOSED_MISSED = len(closed_hours_df[closed_hours_df['disposition_normalized'].isin(['missed', 'abandoned'])])
CLOSED_VOICEMAIL = len(closed_hours_df[closed_hours_df['disposition_normalized'] == 'voicemail'])

if TOTAL_CLOSED > 0:
    CLOSED_ANSWER_RATE = round((CLOSED_ANSWERED / TOTAL_CLOSED) * 100, 1)
    CLOSED_MISS_RATE = round((CLOSED_MISSED / TOTAL_CLOSED) * 100, 1)
else:
    CLOSED_ANSWER_RATE = 0
    CLOSED_MISS_RATE = 0
```

**Store:** `CLOSED_ANSWERED`, `CLOSED_MISSED`, `CLOSED_VOICEMAIL`, `CLOSED_ANSWER_RATE`, `CLOSED_MISS_RATE`

**NOTE:** Closed hours metrics are shown separately in the presentation but are NOT included in the main grade or primary metrics. Missed calls during closed hours are expected behavior (no staff available).

---

## Step 3.5 - Duration Statistics (OPEN HOURS)

Calculate call duration metrics from **open hours answered calls only**.

```python
# ═══════════════════════════════════════════════════════════════════
# DURATION STATS - OPEN HOURS ONLY
# ═══════════════════════════════════════════════════════════════════

# Filter to answered calls during OPEN HOURS with valid duration
answered_calls = open_hours_df[
    (open_hours_df['disposition_normalized'] == 'answered') &
    (open_hours_df['duration_seconds'] > 0)
]

if len(answered_calls) > 0:
    AVG_DURATION_SECONDS = round(answered_calls['duration_seconds'].mean())
    MEDIAN_DURATION_SECONDS = round(answered_calls['duration_seconds'].median())
    AVG_DURATION_MINUTES = round(AVG_DURATION_SECONDS / 60, 1)
    MEDIAN_DURATION_MINUTES = round(MEDIAN_DURATION_SECONDS / 60, 1)

    # AHT for Monte Carlo (minimum 3.5 minutes)
    AHT_USED = max(AVG_DURATION_MINUTES, 3.5)
else:
    AVG_DURATION_SECONDS = 0
    MEDIAN_DURATION_SECONDS = 0
    AVG_DURATION_MINUTES = 0
    MEDIAN_DURATION_MINUTES = 0
    AHT_USED = 3.5  # Default
```

**Store:** `AVG_DURATION_SECONDS`, `MEDIAN_DURATION_SECONDS`, `AVG_DURATION_MINUTES`, `MEDIAN_DURATION_MINUTES`, `AHT_USED`

---

## Step 3.6 - Daily Volume Analysis (OPEN HOURS)

Analyze call patterns by day of week using **open hours data only**.

```python
# ═══════════════════════════════════════════════════════════════════
# DAILY ANALYSIS - OPEN HOURS ONLY
# ═══════════════════════════════════════════════════════════════════

# Group by day of week (OPEN HOURS)
day_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
daily_stats = open_hours_df.groupby('day_of_week').agg({
    'disposition_normalized': 'count',  # Total calls
}).rename(columns={'disposition_normalized': 'total'})

# Add answered/missed counts (OPEN HOURS)
daily_answered = open_hours_df[open_hours_df['disposition_normalized'] == 'answered'].groupby('day_of_week').size()
daily_missed = open_hours_df[open_hours_df['disposition_normalized'].isin(['missed', 'abandoned'])].groupby('day_of_week').size()

daily_stats['answered'] = daily_answered
daily_stats['missed'] = daily_missed
daily_stats = daily_stats.fillna(0)

# Calculate daily miss rates
daily_stats['miss_rate'] = round((daily_stats['missed'] / daily_stats['total']) * 100, 1)

# Reorder by day of week
daily_stats = daily_stats.reindex(day_order)

# Find worst day
WORST_DAY = daily_stats['miss_rate'].idxmax()
WORST_DAY_RATE = daily_stats.loc[WORST_DAY, 'miss_rate']

# Store as dictionary for charts
DAILY_VOLUME = daily_stats['total'].to_dict()
DAILY_MISS_RATE = daily_stats['miss_rate'].to_dict()
```

**Store:** `DAILY_VOLUME`, `DAILY_MISS_RATE`, `WORST_DAY`, `WORST_DAY_RATE`

---

## Step 3.7 - Hourly Volume Analysis (OPEN HOURS)

Analyze call patterns by hour of day using **open hours data only**.

```python
# ═══════════════════════════════════════════════════════════════════
# HOURLY ANALYSIS - OPEN HOURS ONLY
# ═══════════════════════════════════════════════════════════════════

# Group by hour (OPEN HOURS)
hourly_stats = open_hours_df.groupby('hour_local').agg({
    'disposition_normalized': 'count'
}).rename(columns={'disposition_normalized': 'total'})

# Add answered/missed counts (OPEN HOURS)
hourly_answered = open_hours_df[open_hours_df['disposition_normalized'] == 'answered'].groupby('hour_local').size()
hourly_missed = open_hours_df[open_hours_df['disposition_normalized'].isin(['missed', 'abandoned'])].groupby('hour_local').size()

hourly_stats['answered'] = hourly_answered
hourly_stats['missed'] = hourly_missed
hourly_stats = hourly_stats.fillna(0)

# Calculate hourly miss rates
hourly_stats['miss_rate'] = round((hourly_stats['missed'] / hourly_stats['total']) * 100, 1)

# Store as dictionary for charts
HOURLY_VOLUME = hourly_stats['total'].to_dict()
HOURLY_MISS_RATE = hourly_stats['miss_rate'].to_dict()

# Find peak hour
PEAK_HOUR = hourly_stats['total'].idxmax()
PEAK_HOUR_VOLUME = int(hourly_stats.loc[PEAK_HOUR, 'total'])
```

**Store:** `HOURLY_VOLUME`, `HOURLY_MISS_RATE`, `PEAK_HOUR`, `PEAK_HOUR_VOLUME`

---

## Step 3.8 - 2D Pain Windows Matrix (OPEN HOURS)

Build hour × day matrix for heatmap visualization using **open hours data only**.

```python
# ═══════════════════════════════════════════════════════════════════
# PAIN WINDOWS - OPEN HOURS ONLY
# ═══════════════════════════════════════════════════════════════════

# Create 2D pivot table: rows = hours, columns = days (OPEN HOURS)
pain_matrix = open_hours_df.pivot_table(
    values='disposition_normalized',
    index='hour_local',
    columns='day_of_week',
    aggfunc='count',
    fill_value=0
)

# Create miss count matrix (OPEN HOURS)
miss_matrix = open_hours_df[
    open_hours_df['disposition_normalized'].isin(['missed', 'abandoned'])
].pivot_table(
    values='disposition_normalized',
    index='hour_local',
    columns='day_of_week',
    aggfunc='count',
    fill_value=0
)

# Calculate miss rate matrix (percentage)
miss_rate_matrix = (miss_matrix / pain_matrix * 100).fillna(0).round(1)

# Reorder columns
day_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
existing_days = [d for d in day_order if d in miss_rate_matrix.columns]
miss_rate_matrix = miss_rate_matrix[existing_days]

# Filter to business hours (typically 8am-6pm)
business_hours_range = range(8, 18)
miss_rate_matrix = miss_rate_matrix.loc[
    miss_rate_matrix.index.isin(business_hours_range)
]

# Store for heatmap
PAIN_WINDOWS_MATRIX = miss_rate_matrix.to_dict()
```

**Store:** `PAIN_WINDOWS_MATRIX`

---

## Step 3.9 - Identify Worst Hours

Find the 3 worst performing time slots.

### Minimum Volume Threshold

To avoid flagging low-volume hours with misleading high miss rates, apply a minimum volume threshold.

```python
MIN_CALLS_FOR_WORST = 5  # Minimum calls to be considered "worst"

# Flatten hour × day combinations
worst_windows = []
for hour in miss_rate_matrix.index:
    for day in miss_rate_matrix.columns:
        total = pain_matrix.loc[hour, day] if hour in pain_matrix.index and day in pain_matrix.columns else 0
        miss_rate = miss_rate_matrix.loc[hour, day]

        # Only include if meets minimum volume
        if total >= MIN_CALLS_FOR_WORST and miss_rate > 0:
            worst_windows.append({
                'day': day,
                'hour': hour,
                'hour_label': f"{hour}:00-{hour+1}:00",
                'total_calls': int(total),
                'miss_rate': miss_rate
            })

# Sort by miss rate descending
worst_windows.sort(key=lambda x: x['miss_rate'], reverse=True)

# Take top 3
if len(worst_windows) >= 3:
    WORST_HOUR_1 = f"{worst_windows[0]['day']} {worst_windows[0]['hour_label']}"
    WORST_HOUR_1_RATE = worst_windows[0]['miss_rate']
    WORST_HOUR_2 = f"{worst_windows[1]['day']} {worst_windows[1]['hour_label']}"
    WORST_HOUR_2_RATE = worst_windows[1]['miss_rate']
    WORST_HOUR_3 = f"{worst_windows[2]['day']} {worst_windows[2]['hour_label']}"
    WORST_HOUR_3_RATE = worst_windows[2]['miss_rate']
elif len(worst_windows) == 2:
    WORST_HOUR_1 = f"{worst_windows[0]['day']} {worst_windows[0]['hour_label']}"
    WORST_HOUR_1_RATE = worst_windows[0]['miss_rate']
    WORST_HOUR_2 = f"{worst_windows[1]['day']} {worst_windows[1]['hour_label']}"
    WORST_HOUR_2_RATE = worst_windows[1]['miss_rate']
    WORST_HOUR_3 = "N/A"
    WORST_HOUR_3_RATE = 0
elif len(worst_windows) == 1:
    WORST_HOUR_1 = f"{worst_windows[0]['day']} {worst_windows[0]['hour_label']}"
    WORST_HOUR_1_RATE = worst_windows[0]['miss_rate']
    WORST_HOUR_2 = "N/A"
    WORST_HOUR_2_RATE = 0
    WORST_HOUR_3 = "N/A"
    WORST_HOUR_3_RATE = 0
else:
    # No missed calls - great!
    WORST_HOUR_1 = "None - Great performance!"
    WORST_HOUR_1_RATE = 0
    WORST_HOUR_2 = "N/A"
    WORST_HOUR_2_RATE = 0
    WORST_HOUR_3 = "N/A"
    WORST_HOUR_3_RATE = 0
```

**Store:** `WORST_HOUR_1`, `WORST_HOUR_1_RATE`, `WORST_HOUR_2`, `WORST_HOUR_2_RATE`, `WORST_HOUR_3`, `WORST_HOUR_3_RATE`

---

## Step 3.10 - Location Analysis (If Multi-Location, OPEN HOURS)

```python
# ═══════════════════════════════════════════════════════════════════
# LOCATION ANALYSIS - OPEN HOURS ONLY
# ═══════════════════════════════════════════════════════════════════

if LOCATION_COUNT > 1:
    location_stats = open_hours_df.groupby('location_id').agg({
        'disposition_normalized': 'count'
    }).rename(columns={'disposition_normalized': 'total'})

    location_answered = open_hours_df[
        open_hours_df['disposition_normalized'] == 'answered'
    ].groupby('location_id').size()

    location_stats['answered'] = location_answered
    location_stats['answer_rate'] = round(
        (location_stats['answered'] / location_stats['total']) * 100, 1
    )

    LOCATION_STATS = location_stats.to_dict()
else:
    LOCATION_STATS = None
```

**Store:** `LOCATION_STATS` (if applicable)

---

## Edge Case Handling

### Zero Missed Calls

If the practice has no missed calls:
- Set `MISS_RATE = 0`
- Set `MISS_RATIO = "N/A"`
- Skip pain windows analysis
- Note: "Excellent performance - no missed calls detected"

### Low Volume (<50 calls total)

If total inbound calls < 50:
- Add warning flag: `LOW_VOLUME_WARNING = True`
- Note: "Limited data - results may not be statistically significant"
- Still proceed with analysis but caveat results

### Short Date Range (<7 days)

If data spans less than 7 days:
- Avoid weekly projections
- Use daily averages instead
- Add warning: "Short date range - weekly projections adjusted"

---

## Variables Output from Phase 3

```
TOTAL_INBOUND
TOTAL_OUTBOUND
TOTAL_INTERNAL
ANSWER_RATE
MISS_RATE
VOICEMAIL_RATE
MISS_RATIO
MISSED_CALLS_WEEK
ANSWERED_CALLS_WEEK
INBOUND_CALLS_WEEK
GRADE
GRADE_DESCRIPTION
GRADE_BG_COLOR
GRADE_TEXT_COLOR
OPEN_TOTAL
OPEN_ANSWERED
OPEN_MISSED
OPEN_ANSWER_RATE
OPEN_MISS_RATE
CLOSED_TOTAL
CLOSED_ANSWERED
CLOSED_MISSED
CLOSED_ANSWER_RATE
CLOSED_MISS_RATE
OPEN_PCT
CLOSED_PCT
AVG_DURATION_SECONDS
MEDIAN_DURATION_SECONDS
AVG_DURATION_MINUTES
MEDIAN_DURATION_MINUTES
AHT_USED
DAILY_VOLUME
DAILY_MISS_RATE
WORST_DAY
WORST_DAY_RATE
HOURLY_VOLUME
HOURLY_MISS_RATE
PEAK_HOUR
PEAK_HOUR_VOLUME
PAIN_WINDOWS_MATRIX
WORST_HOUR_1
WORST_HOUR_1_RATE
WORST_HOUR_2
WORST_HOUR_2_RATE
WORST_HOUR_3
WORST_HOUR_3_RATE
LOCATION_STATS (if multi-location)
LOW_VOLUME_WARNING (if applicable)
```
