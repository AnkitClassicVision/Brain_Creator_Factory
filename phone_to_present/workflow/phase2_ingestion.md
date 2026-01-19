# Phase 2: Data Ingestion & Standardization

## Step 2.1 - Identify Source Format

Read the selected data file and identify the phone system export format.

### Common Column Patterns

| Format Type | Identifying Features |
|-------------|---------------------|
| Standard Export | `Direction`, `Result`, `Duration` columns |
| Timestamped | `call_type`, `state`, `duration_ms` or similar |
| Detailed | `Call Direction`, `Call Result`, `Talk Time` |
| Basic | `Status`, `Duration`, phone number columns |
| Minimal | Basic timestamp, duration, phone numbers only |

**Store:** `DATA_SOURCE = "Phone Provider Export"` or `"CSV Export"`

---

## Step 2.2 - Column Mapping

Map raw columns to standard schema. Use these priority rules:

### Column Mapping Priority Rules

| Standard Column | Look For (Priority Order) | Required |
|----------------|---------------------------|----------|
| `timestamp` | 1. `start_time` 2. `date_time` 3. `call_start` 4. `timestamp` 5. First datetime column | YES |
| `direction` | 1. `direction` 2. `call_type` 3. `type` 4. Infer from phone numbers | YES |
| `duration` | 1. `duration` 2. `talk_time` 3. `length` 4. `seconds` | YES |
| `disposition` | 1. `disposition` 2. `result` 3. `status` 4. `outcome` 5. Infer from duration | NO |
| `phone_from` | 1. `from` 2. `caller` 3. `calling_number` 4. `ani` | NO |
| `phone_to` | 1. `to` 2. `called` 3. `dialed_number` 4. `dnis` | NO |
| `location` | 1. `location` 2. `office` 3. `site` 4. `branch` | NO |

### Ambiguity Handling

**IF multiple candidate columns exist for a standard field:**
1. List all candidates
2. Ask user: "Which column represents [field]? Options: A, B, C"

**IF no matching column found for required field:**
- STOP and report: "Cannot find [field] column. Please specify which column to use."

### Multi-Location Handling (If `location` Column Exists)

If `location_name` (or equivalent) exists and has multiple distinct values:
- Decide whether to analyze each location separately (recommended when hours/timezones differ).
- Or filter to a single location explicitly (avoid mixing timezones/hours in hourly/pain-window charts).

Record confirmation: `confirmations.location_schedules = confirmed`.

---

## Step 2.3 - Normalize Direction

Normalize the `direction` column to lowercase standard values.

```python
direction_raw = str(direction_raw).strip().lower()

direction_mapping = {
    'inbound': 'inbound',
    'incoming': 'inbound',
    'in': 'inbound',
    'received': 'inbound',
    'outbound': 'outbound',
    'outgoing': 'outbound',
    'out': 'outbound',
    'placed': 'outbound',
    'internal': 'internal',
    'transfer': 'internal'
}

direction_normalized = direction_mapping.get(direction_raw, 'unknown')
```

### Direction Inference (if column missing)

**IF direction column is missing, infer from phone numbers:**

```python
# Extract client phone numbers from website data
client_numbers = set(PHONE_NUMBERS)  # From Phase 1

def infer_direction(phone_from, phone_to, client_numbers):
    """
    Priority rules for direction inference:
    1. If phone_to matches client number → inbound
    2. If phone_from matches client number → outbound
    3. If neither matches → unknown (ask user)
    """
    if phone_to in client_numbers:
        return 'inbound', 0.9  # High confidence
    elif phone_from in client_numbers:
        return 'outbound', 0.9
    else:
        return 'unknown', 0.0

# Track inference confidence
DIRECTION_INFERRED = True
DIRECTION_CONFIDENCE = average of all confidence scores
```

**Store:** `DIRECTION_INFERRED = True/False`, `DIRECTION_CONFIDENCE = 0.0-1.0`

---

## Step 2.4 - Normalize Dispositions

Map raw disposition values to standard categories.

### Disposition Mapping Dictionary

```python
disposition_mapping = {
    # Answered
    'answered': 'answered',
    'completed': 'answered',
    'connected': 'answered',
    'talking': 'answered',
    'success': 'answered',

    # Missed
    'missed': 'missed',
    'no answer': 'missed',
    'unanswered': 'missed',
    'ring no answer': 'missed',
    'rna': 'missed',

    # Voicemail
    'voicemail': 'voicemail',
    'vm': 'voicemail',
    'left message': 'voicemail',
    'voice mail': 'voicemail',

    # Abandoned
    'abandoned': 'abandoned',
    'hang up': 'abandoned',
    'hungup': 'abandoned',
    'caller hung up': 'abandoned',

    # Redirected
    'redirect': 'redirected',
    'redirected': 'redirected',
    'forwarded': 'redirected',
    'transferred': 'redirected',
    'post redirect': 'redirected'
}

def normalize_disposition(raw_value):
    if raw_value is None or raw_value == '':
        return 'unknown', 0.0

    raw_lower = str(raw_value).strip().lower()

    # Check for exact match first
    if raw_lower in disposition_mapping:
        return disposition_mapping[raw_lower], 1.0

    # Check for partial match (contains)
    for key, normalized in disposition_mapping.items():
        if key in raw_lower:
            return normalized, 0.8

    return 'unknown', 0.0
```

### Step 2.4b - Disposition Mapping Review (Required)

Different phone systems use different semantics for values like `transferred`, `forwarded`, `redirected`.
In some exports these mean “answered then routed” (should count as answered), and in others they mean “missed/forwarded away”.

Before proceeding, generate a quick raw-value frequency table and review it:
```python
raw_counts = df[DISPOSITION_COL].astype(str).value_counts().head(20)
print(raw_counts)
```

**Confirm with the client (or the system owner):**
- Which raw values should count as **answered**?
- Which should count as **missed/abandoned**?
- Which should be excluded or treated as **unknown**?

**Quality gates (recommended stop conditions):**
- Unknown disposition > ~1% without explanation → stop and refine mapping
- High “redirected/transferred” share without confirmed semantics → stop and confirm mapping

Record confirmation: `confirmations.disposition_mapping = confirmed`.

### Duration-Based Fallback

**IF no disposition column exists OR disposition is 'unknown':**

```python
def infer_disposition_from_duration(duration_seconds):
    """
    Fallback inference when no disposition available.
    Conservative thresholds to avoid false positives.
    """
    if duration_seconds is None:
        return 'unknown', 0.0
    elif duration_seconds <= 0:
        return 'missed', 0.7
    elif duration_seconds <= 30:
        return 'missed', 0.6  # Short ring, likely abandoned
    else:
        return 'answered', 0.7

# Mark inferred dispositions
DISPOSITION_INFERRED = True
```

**Store:** `DISPOSITION_INFERRED = True/False`

---

## Step 2.5 - Add Business Context Flags

Using business hours from Phase 1, add context flags to each call:

```python
def add_business_context(call_time_local, business_hours, lunch_hours):
    """
    Add boolean flags for business context.
    """
    day_of_week = call_time_local.strftime('%a')  # Mon, Tue, etc.
    hour = call_time_local.hour
    minute = call_time_local.minute
    time_decimal = hour + minute / 60

    # Check if office is open
    if day_of_week in business_hours:
        open_time, close_time = business_hours[day_of_week]
        is_open = open_time <= time_decimal < close_time
    else:
        is_open = False

    # Check if during lunch
    is_lunch = False
    if lunch_hours != "Unknown":
        lunch_start, lunch_end = lunch_hours
        is_lunch = lunch_start <= time_decimal < lunch_end

    # Weekend flag
    is_weekend = day_of_week in ['Sat', 'Sun']

    # After hours = not open and not weekend
    # Closure days are treated as closed even during normal hours
    is_closure_day = date_local in CLOSURES
    is_after_hours = (not is_open) and (not is_weekend) and (not is_closure_day)

    return {
        'is_open_hours': is_open,
        'is_lunch_window': is_lunch,
        'is_after_hours': is_after_hours,
        'is_weekend': is_weekend,
        'is_closure_day': is_closure_day,
        'day_of_week': day_of_week,
        'hour_local': hour
    }
```

---

## Step 2.6 - Create Gold Table

Transform raw data into standardized gold table with these columns:

### Gold Table Schema

| Column | Type | Description |
|--------|------|-------------|
| `source_system` | string | Phone system/export type |
| `raw_call_id` | string | Original call ID if available |
| `client_id` | string | Client identifier |
| `location_id` | string | Location identifier (if multi-location) |
| `direction` | string | 'inbound', 'outbound', 'internal', 'unknown' |
| `start_time_raw` | string | Original timestamp as string |
| `start_time_utc` | datetime | Converted to UTC |
| `start_time_local` | datetime | Converted to client timezone |
| `end_time_local` | datetime | start_time + duration |
| `date_local` | date | Date portion only |
| `day_of_week` | string | Mon, Tue, Wed, Thu, Fri, Sat, Sun |
| `hour_local` | int | Hour (0-23) |
| `duration_raw` | string | Original duration value |
| `duration_seconds` | int | Duration in seconds |
| `duration_minutes` | float | Duration in minutes |
| `disposition_raw` | string | Original disposition |
| `disposition_normalized` | string | Standardized disposition |
| `disposition_confidence` | float | Confidence score (0-1) |
| `is_open_hours` | bool | Call during business hours |
| `is_lunch_window` | bool | Call during lunch (if known) |
| `is_after_hours` | bool | Call outside business hours |
| `is_weekend` | bool | Call on Saturday or Sunday |

---

## Step 2.7 - Data Quality Checks

Run quality checks and generate report.

### Quality Metrics to Calculate

```python
quality_report = {
    # Completeness
    'total_records': len(df),
    'missing_timestamp': count of null timestamps,
    'missing_direction': count of null/unknown direction,
    'missing_duration': count of null duration,
    'missing_disposition': count of null disposition,

    # Validity
    'zero_duration': count where duration = 0,
    'negative_duration': count where duration < 0,
    'excessive_duration': count where duration > 7200 (2 hours),
    'future_timestamps': count where timestamp > now,
    'ancient_timestamps': count where timestamp < 1 year ago,

    # Disposition quality
    'disposition_answered': count,
    'disposition_missed': count,
    'disposition_voicemail': count,
    'disposition_abandoned': count,
    'disposition_redirected': count,
    'disposition_unknown': count,
    'pct_unknown_disposition': percentage,

    # Direction quality
    'direction_inbound': count,
    'direction_outbound': count,
    'direction_internal': count,
    'direction_unknown': count,
    'pct_unknown_direction': percentage,

    # Location quality (if multi-location)
    'location_mapped': count,
    'location_unknown': count,
    'pct_unknown_location': percentage,

    # Duplicates
    'duplicates_found': count,
    'duplicates_removed': count,

    # Date range
    'date_min': earliest date,
    'date_max': latest date,
    'days_span': number of days,
    'weeks_span': number of weeks
}
```

### Quality Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Unknown disposition | >10% | >25% |
| Unknown direction | >5% | >15% |
| Unknown location | >5% | >10% |
| Zero duration | >5% | >15% |
| Duplicates | >1% | >5% |

---

## STOP AND ASK USER IF:

- **Multiple sheets in XLSX** → "Which sheet contains the call data? Options: [Sheet1, Sheet2, ...]"
- **Column mapping ambiguous** → "Which column represents [timestamp/direction/etc]? Options: A, B, C"
- **>20% unknown dispositions** → "Data quality issue: [X]% unknown dispositions. Continue anyway?"
- **>10% unknown direction** → "Data quality issue: [X]% unknown direction. Should I assume all calls are inbound?"
- **Required column missing** → "Cannot find [column]. Please specify which column to use."
- **Date range looks wrong** → "Date range is [X] to [Y]. Does this look correct?"

---

## Variables Output from Phase 2

```
DATA_SOURCE
DIRECTION_INFERRED
DIRECTION_CONFIDENCE
DISPOSITION_INFERRED
TOTAL_RECORDS
DATE_RANGE_START
DATE_RANGE_END
DAYS_IN_RANGE
WEEKS_IN_RANGE
PCT_UNKNOWN_DISPOSITION
PCT_UNKNOWN_DIRECTION
PCT_UNKNOWN_LOCATION
QUALITY_GRADE (A/B/C/D/F based on metrics)
```

### Quality Grade Calculation

```python
def calculate_quality_grade(quality_report):
    """
    Grade data quality based on key metrics.
    """
    deductions = 0

    # Unknown disposition penalty
    pct_unknown = quality_report['pct_unknown_disposition']
    if pct_unknown > 25:
        deductions += 2
    elif pct_unknown > 10:
        deductions += 1

    # Unknown direction penalty
    pct_dir = quality_report['pct_unknown_direction']
    if pct_dir > 15:
        deductions += 2
    elif pct_dir > 5:
        deductions += 1

    # Zero duration penalty
    pct_zero = quality_report['zero_duration'] / quality_report['total_records'] * 100
    if pct_zero > 15:
        deductions += 1
    elif pct_zero > 5:
        deductions += 0.5

    # Grade assignment
    if deductions == 0:
        return 'A'
    elif deductions <= 1:
        return 'B'
    elif deductions <= 2:
        return 'C'
    elif deductions <= 3:
        return 'D'
    else:
        return 'F'
```
