# Error Handling & Workflow Control

## Overview

This document defines error handling, recovery procedures, and user interaction checkpoints for the Phone Analysis Pipeline.

---

## Error Classification

### Critical Errors (STOP - Cannot Continue)

These errors halt the workflow and require user intervention:

| Error | When | User Action Required |
|-------|------|---------------------|
| No data file found | Phase 1 | "No CSV/XLSX files found. Please add a data file to this directory." |
| Cannot parse file | Phase 2 | "Cannot read file format. Is this a valid CSV/XLSX?" |
| No timestamp column | Phase 2 | "Cannot identify timestamp column. Which column contains call times?" |
| No inbound calls | Phase 3 | "No inbound calls detected. Check direction column or confirm this is call data." |
| Template file missing | Phase 7 | "Template not found at templates/presentation_template.md" |
| Zero valid records | Phase 2 | "No valid records after filtering. Check data quality." |

### Non-Critical Errors (CONTINUE with Warning)

These errors allow the workflow to continue with degraded output:

| Error | When | Fallback |
|-------|------|----------|
| Website scraping fails | Phase 1 | Ask user for business hours, timezone manually |
| Chart generation fails | Phase 6 | Use placeholder image |
| Marp CLI not installed | Phase 7 | Output .md file only (no HTML) |
| Location column missing | Phase 2 | Treat as single location |
| Disposition column missing | Phase 2 | Infer from duration |
| High unknown rate | Phase 2 | Continue with warning in output |

---

## User Interaction Checkpoints

### Phase 1: Discovery

**STOP AND ASK:**

1. **Multiple data files found:**
   ```
   Found multiple data files:
   1. calls_jan.csv (2.3 MB)
   2. calls_feb.csv (1.8 MB)
   3. all_calls.xlsx (5.1 MB)

   Which file(s) should I analyze?
   ```

2. **Website scraping failed:**
   ```
   I couldn't access the website. Please provide:
   - Business Hours (e.g., Mon-Fri 8am-5pm, Sat 9am-1pm)
   - Timezone (e.g., America/Chicago)
   - Location address(es)
   ```

3. **Business hours not found:**
   ```
   I couldn't find business hours on the website.
   What are the office hours? (e.g., Mon-Fri 8am-5pm)
   ```

4. **Timezone unclear:**
   ```
   I couldn't determine the timezone. Options:
   - America/New_York (Eastern)
   - America/Chicago (Central)
   - America/Denver (Mountain)
   - America/Los_Angeles (Pacific)

   Which timezone?
   ```

5. **Multiple locations detected:**
   ```
   Found multiple locations:
   1. Main Office - 123 Main St
   2. Branch - 456 Oak Ave

   Should I include all locations or specific ones?
   ```

### Phase 2: Data Ingestion

**STOP AND ASK:**

1. **Multiple sheets in XLSX:**
   ```
   This Excel file has multiple sheets:
   1. Sheet1 (5,234 rows)
   2. Call Log (12,456 rows)
   3. Summary

   Which sheet contains the call data?
   ```

2. **Column mapping ambiguous:**
   ```
   Multiple columns could be the timestamp:
   - "Created At"
   - "Call Time"
   - "Start"

   Which column is the call start time?
   ```

3. **High unknown disposition rate:**
   ```
   [!] Data Quality Issue:
   {X}% of calls have unknown disposition.

   This may affect accuracy. Continue anyway? (Y/N)
   ```

4. **Direction column missing:**
   ```
   No direction column found.
   Should I assume all calls are inbound? (Y/N)

   Or specify which column indicates direction:
   ```

5. **Date range looks wrong:**
   ```
   Date range detected: Jan 1, 2020 to Dec 31, 2025

   This seems unusual. Is this correct? (Y/N)
   ```

### Phase 3: Analysis (No User Interaction)

Analysis phase runs automatically. Only stops on critical errors.

### Phase 4: Concurrency (No User Interaction)

Concurrency phase runs automatically. Only stops on critical errors.

### Phase 5: Pricing (No User Interaction)

Pricing phase runs automatically using standard rates.

### Phase 6: Charts (No User Interaction)

Chart generation runs automatically. Failed charts use placeholders.

### Phase 7: Presentation

**STOP AND ASK:**

1. **Marp CLI not available:**
   ```
   Marp CLI is not installed. Output options:
   1. Continue with .md file only (can open in VS Code)
   2. Stop and install Marp (npm install -g @marp-team/marp-cli)

   Choice?
   ```

### Phase 8: Deliverables

**PRESENT TO USER:**

Final summary is always presented. User reviews output files.

---

## Error Recovery Procedures

### Retry Logic

For transient errors (network, file locks), attempt up to 3 retries:

```python
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

def with_retry(func, *args, **kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except TransientError as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            raise e
```

### Website Scraping Fallback

```python
def get_business_info(website_url):
    try:
        # Attempt scraping
        info = scrape_website(website_url)
        return info
    except ScrapeError:
        # Fallback: ask user
        return ask_user_for_business_info()
```

### Chart Generation Fallback

```python
def generate_chart_with_fallback(chart_func, output_path):
    try:
        chart_func(output_path)
        return True
    except ChartError as e:
        print(f"Warning: Chart failed - {e}")
        create_placeholder_image(output_path)
        return False
```

### Division by Zero Protection

```python
# Always protect division operations
def safe_divide(numerator, denominator, default=0):
    if denominator == 0:
        return default
    return numerator / denominator

# Example usage
MISS_RATE = safe_divide(missed_count, total_count, default=0) * 100
MISS_RATIO = "N/A" if MISS_RATE == 0 else round(100 / MISS_RATE)
```

---

## Edge Case Handling

### Zero Missed Calls

```python
if total_missed == 0:
    # Great performance!
    MISS_RATE = 0
    MISS_RATIO = "N/A"
    WORST_HOUR_1 = "None - Great performance!"
    WORST_HOUR_1_RATE = 0
    PROCESS_MISS_PCT = 0
    CAPACITY_MISS_PCT = 0

    # Add positive note
    add_insight("Excellent! No missed calls detected during analysis period.")
```

### Very Low Volume (<50 calls)

```python
if TOTAL_INBOUND < 50:
    LOW_VOLUME_WARNING = True
    add_warning("Low call volume - results may not be statistically significant.")

    # Still proceed but caveat results
    if TOTAL_INBOUND < 10:
        add_warning("Very low volume (<10 calls). Consider longer date range.")
```

### Very High Volume (>50,000 calls)

```python
if TOTAL_INBOUND > 50000:
    HIGH_VOLUME_NOTE = True
    add_note("Large dataset - some calculations may take longer.")

    # Consider sampling for concurrency analysis
    # Or use optimized algorithms
```

### Short Date Range (<7 days)

```python
if DAYS_IN_RANGE < 7:
    SHORT_RANGE_WARNING = True
    add_warning("Short date range - weekly projections may not be representative.")

    # Adjust projections
    # Use daily averages instead of weekly
```

### 24/7 Operations

```python
if TOTAL_WEEKLY_HOURS >= 168:  # 24 * 7
    IS_24_7 = True

    # All calls are during "open hours"
    CLOSED_TOTAL = 0
    OPEN_TOTAL = TOTAL_INBOUND

    # OT calculation changes
    # May need shift-based analysis instead
    add_note("24/7 operation detected. Consider shift-based analysis.")
```

### Multiple Timezones (Multi-Location)

```python
if len(set(location_timezones)) > 1:
    MULTI_TZ_WARNING = True
    add_warning("Multiple timezones detected. Using primary location timezone.")

    # Use most common or ask user
    PRIMARY_TIMEZONE = get_most_common_timezone(location_timezones)
```

---

## Validation Functions

### Validate Data Quality

```python
def validate_data_quality(df):
    """
    Validate data quality and return warnings/errors.
    """
    issues = []

    # Check for required columns
    required = ['start_time_local', 'direction', 'duration_seconds']
    for col in required:
        if col not in df.columns:
            issues.append(('CRITICAL', f"Missing required column: {col}"))

    # Check for empty data
    if len(df) == 0:
        issues.append(('CRITICAL', "No records in dataset"))

    # Check for high unknown rates
    if 'disposition_normalized' in df.columns:
        unknown_pct = (df['disposition_normalized'] == 'unknown').mean() * 100
        if unknown_pct > 25:
            issues.append(('WARNING', f"{unknown_pct:.1f}% unknown dispositions"))
        elif unknown_pct > 10:
            issues.append(('NOTICE', f"{unknown_pct:.1f}% unknown dispositions"))

    # Check for suspicious values
    if df['duration_seconds'].max() > 7200:  # > 2 hours
        issues.append(('NOTICE', "Some calls exceed 2 hours - verify data"))

    if df['duration_seconds'].min() < 0:
        issues.append(('WARNING', "Negative durations detected - data issue"))

    return issues
```

### Validate Pricing Outputs

```python
def validate_pricing(pricing_vars):
    """
    Validate pricing calculations are reasonable.
    """
    issues = []

    # Check for negative values
    for var in ['INBOUND_WEEKLY', 'RHC_WEEKLY', 'HIRE_WEEKLY']:
        if pricing_vars[var] < 0:
            issues.append(('CRITICAL', f"{var} is negative"))

    # Check for unrealistic values
    if pricing_vars['INBOUND_WEEKLY'] > 10000:
        issues.append(('WARNING', "Inbound weekly cost exceeds $10,000 - verify"))

    # Check ordering makes sense
    if pricing_vars['INBOUND_WEEKLY'] > pricing_vars['HIRE_WEEKLY']:
        issues.append(('WARNING', "Inbound more expensive than In-House - verify"))

    return issues
```

---

## Logging

### Log Levels

| Level | Use |
|-------|-----|
| INFO | Normal progress messages |
| WARNING | Non-critical issues that don't stop workflow |
| ERROR | Critical issues that stop workflow |
| DEBUG | Detailed diagnostic info (optional) |

### Log Format

```
[PHASE X] [LEVEL] Message
[DATA   ] [WARNING] 15.2% unknown dispositions - results may be conservative
[CHART  ] [ERROR] Failed to generate pain_windows_heatmap.png - using placeholder
[PRICING] [INFO] Calculated: Inbound $1,800/mo, RHC $2,700/mo, In-House $3,200/mo
```

---

## Summary: When to Stop vs Continue

### ALWAYS STOP:
- No data file
- Cannot parse file
- No timestamp column
- No inbound calls
- Zero valid records
- Template missing

### STOP AND ASK:
- Multiple files found
- Column mapping ambiguous
- Website scrape failed
- Multiple sheets in XLSX
- High unknown rate (>20%)
- Timezone unclear

### CONTINUE WITH WARNING:
- Chart generation failed
- Marp not installed
- Low call volume
- Short date range
- High unknown rate (10-20%)
- Location column missing

### CONTINUE SILENTLY:
- Minor data quality issues
- Duration outliers
- A few duplicate records
