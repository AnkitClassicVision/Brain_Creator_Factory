# Phase 4: Concurrency & FTE Analysis

## Overview

This phase calculates how many simultaneous calls occur (concurrency) and determines staffing requirements (FTE) using Monte Carlo simulation.

**IMPORTANT: All concurrency and FTE analysis uses OPEN HOURS data only.**

**Two concurrency perspectives:**
1. **Triggered Concurrency** - Measured at call arrival moments (pricing perspective)
2. **Time-Weighted Concurrency** - Measured across all time (operations perspective)

---

## Step 4.1 - Triggered Concurrency Analysis (OPEN HOURS)

Triggered concurrency measures overlapping calls at the moment each new call arrives. This is the **pricing lens** because it asks: "When a call comes in, how many agents are needed?"

**Uses OPEN HOURS data only** - we only need to staff during business hours.

```python
# ═══════════════════════════════════════════════════════════════════
# CONCURRENCY ANALYSIS - OPEN HOURS ONLY
# ═══════════════════════════════════════════════════════════════════

def calculate_triggered_concurrency(calls_df):
    """
    For each call arrival, count how many other calls are active.

    SCALABILITY NOTE: This is O(n²). For datasets > 50,000 calls,
    consider using interval tree or sweep-line optimization.

    Args:
        calls_df: DataFrame with 'start_time_local' and 'end_time_local'

    Returns:
        dict: {level: count} where level is concurrency and count is arrivals at that level
    """
    calls = calls_df.sort_values('start_time_local').reset_index(drop=True)
    concurrency_at_arrival = []

    for i, call in calls.iterrows():
        arrival_time = call['start_time_local']

        # Count calls active at this arrival time
        # A call is active if: start <= arrival_time < end
        active = calls[
            (calls['start_time_local'] <= arrival_time) &
            (calls['end_time_local'] > arrival_time)
        ]

        # Concurrency = number of active calls (including this one)
        concurrency_at_arrival.append(len(active))

    # Build distribution
    triggered_dist = {}
    for level in concurrency_at_arrival:
        triggered_dist[level] = triggered_dist.get(level, 0) + 1

    return triggered_dist

# Use OPEN HOURS data only for concurrency
TRIGGERED_CONCURRENCY = calculate_triggered_concurrency(open_hours_df)
```

**Store:** `TRIGGERED_CONCURRENCY` (dict: {level: count})

---

## Step 4.2 - Time-Weighted Concurrency Analysis (OPEN HOURS)

Time-weighted concurrency measures how much TIME is spent at each concurrency level. This is the **operations lens** because it shows actual staffing utilization.

**Uses OPEN HOURS data only.**

```python
def calculate_time_weighted_concurrency(calls_df):
    """
    Sweep-line algorithm to calculate time spent at each concurrency level.

    Algorithm:
    1. Create events: +1 at call start, -1 at call end
    2. Sort by time (tie-break: process -1 before +1)
    3. Walk through events, tracking current level
    4. Accumulate time at each level

    Args:
        calls_df: DataFrame with 'start_time_local' and 'end_time_local'

    Returns:
        dict: {level: seconds} time spent at each concurrency level
    """
    events = []

    for _, call in calls_df.iterrows():
        # +1 at start (type=1 for sorting)
        events.append((call['start_time_local'], 1, +1))
        # -1 at end (type=0 for sorting, processed first)
        events.append((call['end_time_local'], 0, -1))

    # Sort: by time, then by type (0 before 1 = ends before starts)
    events.sort(key=lambda x: (x[0], x[1]))

    # Walk through events
    time_at_level = {}
    current_level = 0
    last_time = events[0][0] if events else None

    for time, _, delta in events:
        if last_time is not None and time > last_time:
            # Accumulate time at current level
            duration = (time - last_time).total_seconds()
            time_at_level[current_level] = time_at_level.get(current_level, 0) + duration

        current_level += delta
        last_time = time

    return time_at_level

# Use OPEN HOURS data only
TIME_WEIGHTED_CONCURRENCY = calculate_time_weighted_concurrency(open_hours_df)
```

**Store:** `TIME_WEIGHTED_CONCURRENCY` (dict: {level: seconds})

---

## Step 4.3 - Concurrency Summary Statistics

```python
# Calculate summary stats from triggered concurrency
total_arrivals = sum(TRIGGERED_CONCURRENCY.values())

# Max concurrency observed
MAX_CONCURRENCY = max(TRIGGERED_CONCURRENCY.keys())

# Average concurrency at arrival
AVG_CONCURRENCY = sum(k * v for k, v in TRIGGERED_CONCURRENCY.items()) / total_arrivals

# 90th percentile concurrency (key for FTE)
cumulative = 0
for level in sorted(TRIGGERED_CONCURRENCY.keys()):
    cumulative += TRIGGERED_CONCURRENCY[level]
    if cumulative / total_arrivals >= 0.90:
        PERCENTILE_90_CONCURRENCY = level
        break

# Time utilization (% time with at least 1 call)
total_time = sum(TIME_WEIGHTED_CONCURRENCY.values())
time_with_calls = total_time - TIME_WEIGHTED_CONCURRENCY.get(0, 0)
UTILIZATION_PCT = round((time_with_calls / total_time) * 100, 1) if total_time > 0 else 0
```

**Store:** `MAX_CONCURRENCY`, `AVG_CONCURRENCY`, `PERCENTILE_90_CONCURRENCY`, `UTILIZATION_PCT`

---

## Step 4.4 - Monte Carlo Simulation

Run simulations to determine required FTE at 90% coverage target.

### Configuration

```python
import numpy as np
import hashlib

def stable_seed(*parts) -> int:
    """
    Derive a deterministic seed from stable inputs so identical datasets
    produce identical Monte Carlo results (right-first-time, every time).
    """
    fingerprint = "|".join(str(p) for p in parts)
    digest = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)  # 32-bit seed

# Deterministic seed (replace inputs with available stable identifiers)
MC_SEED = stable_seed(
    DATA_SOURCE,
    TOTAL_RECORDS,
    DATE_RANGE_START,
    DATE_RANGE_END,
    TOTAL_INBOUND,
    AHT_USED,
)
rng = np.random.default_rng(MC_SEED)

# Simulation parameters
NUM_SIMULATIONS = 1000
TARGET_COVERAGE = 0.90  # 90% of arrivals covered
AHT_LAMBDA = 1 / (AHT_USED * 60)  # Convert minutes to rate parameter (per second)
```

### Simulation Function

```python
def run_monte_carlo_simulation(calls_df, num_sims, aht_lambda, target_coverage, rng):
    """
    Monte Carlo simulation for FTE requirements.

    Method: Duration-only simulation
    - Keep real arrival times from data
    - Simulate durations from exponential distribution
    - Calculate concurrency for each simulation
    - Find FTE that covers target % of arrivals

    Args:
        calls_df: DataFrame with call data
        num_sims: Number of simulation runs
        aht_lambda: Rate parameter for exponential distribution (1/AHT in seconds)
        target_coverage: Target coverage percentage (e.g., 0.90)

    Returns:
        dict with simulation results
    """
    fte_results = []

    for sim in range(num_sims):
        # Copy calls and simulate durations
        sim_calls = calls_df.copy()

        # Generate exponential durations: T = -ln(U) / lambda
        u = rng.random(len(sim_calls))
        u = np.clip(u, 1e-12, 1 - 1e-12)  # protect against log(0)
        sim_durations = -np.log(u) / aht_lambda  # In seconds

        # Assign simulated durations
        sim_calls['sim_duration'] = sim_durations
        sim_calls['sim_end_time'] = sim_calls['start_time_local'] + \
            pd.to_timedelta(sim_calls['sim_duration'], unit='s')

        # Calculate time-weighted concurrency for this simulation
        def time_weighted_concurrency_sim(df):
            events = []
            for _, call in df.iterrows():
                events.append((call['start_time_local'], 1, +1))
                events.append((call['sim_end_time'], 0, -1))

            events.sort(key=lambda x: (x[0], x[1]))

            time_at_level = {}
            current_level = 0
            last_time = events[0][0] if events else None

            for time, _, delta in events:
                if last_time is not None and time > last_time:
                    duration = (time - last_time).total_seconds()
                    time_at_level[current_level] = time_at_level.get(current_level, 0) + duration
                current_level += delta
                last_time = time

            return time_at_level

        sim_concurrency = time_weighted_concurrency_sim(sim_calls)

        # Find FTE that covers target % of time (excluding level 0)
        total_time = sum(sim_concurrency.values())
        time_excluding_zero = total_time - sim_concurrency.get(0, 0)

        cumulative_time = 0
        for level in sorted(sim_concurrency.keys()):
            if level == 0:
                continue
            cumulative_time += sim_concurrency[level]
            coverage = cumulative_time / time_excluding_zero if time_excluding_zero > 0 else 1
            if coverage >= target_coverage:
                fte_results.append(level)
                break
        else:
            # If loop completes without break, use max level
            fte_results.append(max(sim_concurrency.keys()))

    return {
        'fte_distribution': fte_results,
        'fte_mean': np.mean(fte_results),
        'fte_median': np.median(fte_results),
        'fte_90th': np.percentile(fte_results, 90),
        'fte_max': max(fte_results)
    }

# Run simulation using OPEN HOURS data only
MC_RESULTS = run_monte_carlo_simulation(
    open_hours_df,
    NUM_SIMULATIONS,
    AHT_LAMBDA,
    TARGET_COVERAGE,
    rng
)
```

**Store:** `MC_RESULTS`, `MC_SEED`, `NUM_SIMULATIONS`, `TARGET_COVERAGE`

---

## Step 4.5 - FTE Calculation (CDF-Based)

Calculate BASE_FTE using the Cumulative Distribution Function (CDF) from time-weighted concurrency. This finds the concurrency level where 90%+ of call time is covered (ignoring level 0).

```python
# ═══════════════════════════════════════════════════════════════════
# BASE_FTE CALCULATION - CDF at 90% coverage (ignore level 0)
# ═══════════════════════════════════════════════════════════════════

def calculate_base_fte(time_weighted_concurrency, target_coverage=0.90):
    """
    Calculate BASE_FTE using CDF from time-weighted concurrency.

    Method:
    1. Exclude level 0 (no calls = no staffing needed)
    2. Build CDF of time spent at each concurrency level
    3. Find the level where cumulative coverage >= target

    Args:
        time_weighted_concurrency: dict {level: seconds}
        target_coverage: Target coverage percentage (default 0.90)

    Returns:
        int: BASE_FTE (minimum agents to cover target % of call time)
    """
    # Get levels > 0, sorted
    levels = sorted([k for k in time_weighted_concurrency.keys() if k > 0])

    if not levels:
        return 1  # Minimum BASE_FTE

    # Total time with at least 1 call (excluding level 0)
    total_time_with_calls = sum(time_weighted_concurrency[k] for k in levels)

    if total_time_with_calls == 0:
        return 1  # Minimum BASE_FTE

    # Build CDF and find target level
    cumulative = 0
    for level in levels:
        cumulative += time_weighted_concurrency[level]
        coverage = cumulative / total_time_with_calls
        if coverage >= target_coverage:
            return level

    # If loop completes, return max level
    return max(levels)

# Calculate BASE_FTE from actual time-weighted concurrency
BASE_FTE_RAW = calculate_base_fte(TIME_WEIGHTED_CONCURRENCY, TARGET_COVERAGE)

# Apply minimum (at least 1 FTE)
BASE_FTE = max(BASE_FTE_RAW, 1)

# ═══════════════════════════════════════════════════════════════════
# SHRINKAGE_FTE CALCULATION
# ═══════════════════════════════════════════════════════════════════

# 20% shrinkage accounts for: breaks, training, admin, PTO
SHRINKAGE_FACTOR = 0.80  # 80% productive time
SHRINKAGE_FTE_RAW = BASE_FTE / SHRINKAGE_FACTOR

# Apply minimum with shrinkage (at least 1.25 FTE)
SHRINKAGE_FTE = max(SHRINKAGE_FTE_RAW, 1.25)

# Round to 2 decimal places
BASE_FTE = round(BASE_FTE, 2)
SHRINKAGE_FTE = round(SHRINKAGE_FTE, 2)
```

### FTE Definitions

| Variable | Definition | Example (if BASE_FTE=1) |
|----------|------------|------------------------|
| `BASE_FTE` | CDF at 90% coverage (ignore level 0) | 1.0 |
| `SHRINKAGE_FTE` | BASE_FTE / 0.80 (adds 20% shrinkage) | 1.25 |

### Usage in Pricing

| Pricing Option | FTE Used | Description |
|----------------|----------|-------------|
| **Inbound (phones-only)** | BASE_FTE | Call-time coverage requirement (no shrinkage multiplier) |
| **RHC** | SHRINKAGE_FTE | Full-service coverage with shrinkage buffer |
| **RHC+ Growth** | SHRINKAGE_FTE | RHC staffing plus growth consulting add-on |
| **In-House** | SHRINKAGE_FTE | Hiring plan should include shrinkage buffer |

**Store:** `BASE_FTE`, `SHRINKAGE_FTE`

---

## Step 4.5b - FTE Verification & Reconciliation (Checks & Balances)

Before using FTE values for pricing, reconcile the two independent estimates:
- `BASE_FTE` (CDF @ 90% from time-weighted concurrency; ignores level 0)
- `MC_RESULTS['fte_90th']` (Monte Carlo duration simulation; deterministic seed)

```python
MC_FTE_90 = round(float(MC_RESULTS['fte_90th']), 2)
FTE_DIFF = round(abs(MC_FTE_90 - BASE_FTE), 2)

FTE_VERIFICATION_PASS = FTE_DIFF <= 1.0
if not FTE_VERIFICATION_PASS:
    FTE_VERIFICATION_NOTE = (
        f"Monte Carlo FTE ({MC_FTE_90}) differs from CDF FTE ({BASE_FTE}) by {FTE_DIFF}. "
        "Re-check business hours/timezone, AHT_USED, and duration parsing."
    )
else:
    FTE_VERIFICATION_NOTE = "Monte Carlo and CDF-based FTE reconcile."
```

**Store:** `MC_FTE_90`, `FTE_DIFF`, `FTE_VERIFICATION_PASS`, `FTE_VERIFICATION_NOTE`

If this fails, resolve before proceeding to pricing (see `workflow/verification_checklist.md`).

---

## Step 4.6 - Process vs Capacity Analysis

Determine root cause of missed calls: process issues vs capacity issues.

```python
def analyze_miss_causes(open_hours_df, triggered_concurrency):
    """
    Categorize missed calls by likely cause (OPEN HOURS ONLY):
    - Process: Missed when concurrency = 1 (single call, no excuse)
    - Capacity: Missed when concurrency > 1 (multiple calls, overwhelmed)

    This is a KEY INSIGHT for the presentation.
    Uses OPEN HOURS data only.
    """
    missed_calls = open_hours_df[
        open_hours_df['disposition_normalized'].isin(['missed', 'abandoned'])
    ].copy()

    process_misses = 0
    capacity_misses = 0

    for _, call in missed_calls.iterrows():
        arrival_time = call['start_time_local']

        # Count concurrent calls at this arrival (OPEN HOURS)
        active = open_hours_df[
            (open_hours_df['start_time_local'] <= arrival_time) &
            (open_hours_df['end_time_local'] > arrival_time)
        ]

        if len(active) <= 1:
            process_misses += 1  # Only 1 call - should have answered
        else:
            capacity_misses += 1  # Multiple calls - capacity issue

    total_misses = process_misses + capacity_misses

    if total_misses > 0:
        PROCESS_MISS_PCT = round((process_misses / total_misses) * 100, 1)
        CAPACITY_MISS_PCT = round((capacity_misses / total_misses) * 100, 1)
    else:
        PROCESS_MISS_PCT = 0
        CAPACITY_MISS_PCT = 0

    return {
        'process_misses': process_misses,
        'capacity_misses': capacity_misses,
        'process_pct': PROCESS_MISS_PCT,
        'capacity_pct': CAPACITY_MISS_PCT
    }

# Use OPEN HOURS data only for miss cause analysis
MISS_CAUSES = analyze_miss_causes(open_hours_df, TRIGGERED_CONCURRENCY)
PROCESS_MISS_PCT = MISS_CAUSES['process_pct']
CAPACITY_MISS_PCT = MISS_CAUSES['capacity_pct']
```

**Store:** `PROCESS_MISS_PCT`, `CAPACITY_MISS_PCT`

---

## Edge Case Handling

### Very Low Volume (<10 calls/day)

```python
avg_calls_per_day = TOTAL_INBOUND / DAYS_IN_RANGE

if avg_calls_per_day < 10:
    # Low volume - CDF calculation may be unreliable
    LOW_VOLUME_WARNING = True
    # Use minimum FTE values
    BASE_FTE = 1.0
    SHRINKAGE_FTE = 1.25
    # Note in output
    FTE_NOTE = "Low call volume - using minimum staffing"
```

### Zero Missed Calls

```python
if MISS_RATE == 0:
    # Perfect performance - still calculate FTE for growth capacity
    PROCESS_MISS_PCT = 0
    CAPACITY_MISS_PCT = 0
    FTE_NOTE = "No missed calls - FTE represents growth capacity"
```

### High Concurrency (>5 simultaneous)

```python
if MAX_CONCURRENCY > 5:
    HIGH_CONCURRENCY_WARNING = True
    # May indicate data quality issues or very high volume
    # Verify with user
```

---

## Variables Output from Phase 4

```
TRIGGERED_CONCURRENCY
TIME_WEIGHTED_CONCURRENCY
MAX_CONCURRENCY
AVG_CONCURRENCY
PERCENTILE_90_CONCURRENCY
UTILIZATION_PCT
MC_RESULTS
BASE_FTE
SHRINKAGE_FTE
PROCESS_MISS_PCT
CAPACITY_MISS_PCT
```
