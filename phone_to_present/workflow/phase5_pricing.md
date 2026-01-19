# Phase 5: Pricing & Cost Comparison

## Overview

This phase calculates costs for four options:
1. **MyBCAT Inbound** - Phone answering service only (phones-only)
2. **MyBCAT RHC** - Remote Hospitality Center (full service)
3. **MyBCAT RHC+ Growth** - RHC plus monthly growth consulting (add-on)
4. **In-House Hire** - Traditional employee hire

---

## Step 5.1 - Pricing Inputs

### Base Rates (Weekly)

| Option | Weekly Base | Hourly Equiv | OT Rate | Weekend Premium |
|--------|-------------|--------------|---------|-----------------|
| Inbound | $480/week | $10/hr × 1.2 | $18/hr | $25 × BASE_FTE per day |
| RHC | $480/week | $10/hr × 1.2 | $18/hr | $25 × BASE_FTE per day |
| In-House | $960/week | $20/hr × 1.2 | $36/hr | $25 × BASE_FTE per day |

**Rate Breakdown:**
- MyBCAT (Inbound/RHC): $10/hr × 40 hrs × 1.2 burden = **$480/week**
- In-House: $20/hr × 40 hrs × 1.2 burden = **$960/week**

### FTE Used by Option

| Option | FTE Multiplier | Description |
|--------|----------------|-------------|
| **In-House** | SHRINKAGE_FTE | Covers 90%+ with shrinkage buffer |
| **Inbound** | BASE_FTE | Phones-only coverage (call-time staffing) |
| **RHC** | SHRINKAGE_FTE | Full-service coverage with shrinkage buffer |
| **RHC+ Growth** | SHRINKAGE_FTE | RHC staffing plus growth consulting add-on |

### RHC+ Growth Add-On
- Includes **1x/month consulting** (growth plan + KPI review)
- Add-on price: **+$500/week** (flat) on top of RHC pricing

### Hours Input (from Phase 1)

```python
# From Phase 1 calculations
TOTAL_WEEKLY_HOURS   # Total hours office is open per week
OT_HOURS = max(TOTAL_WEEKLY_HOURS - 40, 0)  # Hours over 40
HOURS_FOR_CALCULATION = max(TOTAL_WEEKLY_HOURS, 40)  # Minimum 40 hours
SATURDAY_HOURS       # Hours on Saturday (0 if closed)
SUNDAY_HOURS         # Hours on Sunday (0 if closed)
HAS_SATURDAY         # True/False
HAS_SUNDAY           # True/False

# FTE values from Phase 4
BASE_FTE             # CDF at 90% coverage (ignore level 0)
SHRINKAGE_FTE        # BASE_FTE / 0.80
```

---

## Step 5.2 - MyBCAT Inbound Pricing

Inbound pricing uses **BASE_FTE** for base rate, OT, and weekend (phones-only).

```python
# ═══════════════════════════════════════════════════════════════════
# MYBCAT INBOUND PRICING
# ═══════════════════════════════════════════════════════════════════

# Base rates
MYBCAT_WEEKLY_RATE = 480  # $10/hr × 40 hrs × 1.2 burden
MYBCAT_OT_HOURLY = 18     # $10 × 1.2 × 1.5

# Base cost: $480/week × BASE_FTE
INBOUND_BASE = MYBCAT_WEEKLY_RATE * BASE_FTE

# OT cost: $18/hr × BASE_FTE × OT hours
# Note: OT uses BASE_FTE, not SHRINKAGE_FTE
INBOUND_OT = MYBCAT_OT_HOURLY * BASE_FTE * OT_HOURS

# Weekend premiums: $25 × BASE_FTE per weekend day
INBOUND_WEEKEND = 0
if HAS_SATURDAY:
    INBOUND_WEEKEND += 25 * BASE_FTE
if HAS_SUNDAY:
    INBOUND_WEEKEND += 25 * BASE_FTE

# Weekly total
INBOUND_WEEKLY = round(INBOUND_BASE + INBOUND_OT + INBOUND_WEEKEND, 2)

# Monthly (4.33 weeks/month)
INBOUND_MONTHLY = round(INBOUND_WEEKLY * 4.33)

# Annual
INBOUND_ANNUAL = INBOUND_MONTHLY * 12
```

**Store:** `INBOUND_WEEKLY`, `INBOUND_MONTHLY`, `INBOUND_ANNUAL`

---

## Step 5.3 - MyBCAT RHC Pricing

RHC pricing uses **SHRINKAGE_FTE** for base rate (includes shrinkage buffer). OT/weekend scale with `BASE_FTE`.

```python
# ═══════════════════════════════════════════════════════════════════
# MYBCAT RHC PRICING
# ═══════════════════════════════════════════════════════════════════

# Base rates (same as Inbound)
MYBCAT_WEEKLY_RATE = 480  # $10/hr × 40 hrs × 1.2 burden
MYBCAT_OT_HOURLY = 18     # $10 × 1.2 × 1.5

# Base cost: $480/week × SHRINKAGE_FTE
RHC_BASE = MYBCAT_WEEKLY_RATE * SHRINKAGE_FTE

# OT cost: $18/hr × BASE_FTE × OT hours
# Note: OT uses BASE_FTE (call-time staffing), not SHRINKAGE_FTE
RHC_OT = MYBCAT_OT_HOURLY * BASE_FTE * OT_HOURS

# Weekend premiums: $25 × BASE_FTE per weekend day
RHC_WEEKEND = 0
if HAS_SATURDAY:
    RHC_WEEKEND += 25 * BASE_FTE
if HAS_SUNDAY:
    RHC_WEEKEND += 25 * BASE_FTE

# Weekly total
RHC_WEEKLY = round(RHC_BASE + RHC_OT + RHC_WEEKEND, 2)

# Monthly (4.33 weeks/month)
RHC_MONTHLY = round(RHC_WEEKLY * 4.33)

# Annual
RHC_ANNUAL = RHC_MONTHLY * 12
```

**Store:** `RHC_WEEKLY`, `RHC_MONTHLY`, `RHC_ANNUAL`

---

## Step 5.3b - MyBCAT RHC+ Growth (Add-On)

RHC+ Growth is **RHC + a flat $500/week add-on** and includes **1x/month consulting**.

```python
RHC_GROWTH_ADDON_WEEKLY = 500
RHC_GROWTH_WEEKLY = round(RHC_WEEKLY + RHC_GROWTH_ADDON_WEEKLY, 2)
RHC_GROWTH_MONTHLY = round(RHC_GROWTH_WEEKLY * 4.33)
RHC_GROWTH_ANNUAL = RHC_GROWTH_MONTHLY * 12
```

**Store:** `RHC_GROWTH_WEEKLY`, `RHC_GROWTH_MONTHLY`, `RHC_GROWTH_ANNUAL`

---

## Step 5.4 - In-House Hire Pricing

In-House uses **SHRINKAGE_FTE** for base rate and **BASE_FTE** for OT/weekend. Higher rates than MyBCAT.

```python
# ═══════════════════════════════════════════════════════════════════
# IN-HOUSE PRICING
# ═══════════════════════════════════════════════════════════════════

# Base rates (loaded = wages + benefits + taxes + overhead)
INHOUSE_WEEKLY_RATE = 960  # $20/hr × 40 hrs × 1.2 burden
INHOUSE_OT_HOURLY = 36     # $20 × 1.2 × 1.5

# Base cost: $960/week × SHRINKAGE_FTE
HIRE_BASE = INHOUSE_WEEKLY_RATE * SHRINKAGE_FTE

# OT cost: $36/hr × BASE_FTE × OT hours
# Note: OT uses BASE_FTE, not SHRINKAGE_FTE
HIRE_OT = INHOUSE_OT_HOURLY * BASE_FTE * OT_HOURS

# Weekend premiums: $25 × BASE_FTE per weekend day
HIRE_WEEKEND = 0
if HAS_SATURDAY:
    HIRE_WEEKEND += 25 * BASE_FTE
if HAS_SUNDAY:
    HIRE_WEEKEND += 25 * BASE_FTE

# Weekly total
HIRE_WEEKLY = round(HIRE_BASE + HIRE_OT + HIRE_WEEKEND, 2)

# Monthly (4.33 weeks/month)
HIRE_MONTHLY = round(HIRE_WEEKLY * 4.33)

# Annual
HIRE_ANNUAL = HIRE_MONTHLY * 12
```

**Store:** `HIRE_WEEKLY`, `HIRE_MONTHLY`, `HIRE_ANNUAL`

---

## Step 5.4b - Optional Pilot Program (Inbound Answering Only)

If offering a pilot, choose:
- a **Base HC level** (integer), and
- a **calculation basis** for pricing:
  - `base` = price off Base HC
  - `shrinkage` = price off Shrinkage HC (Base HC adjusted with shrinkage buffer)

Use the staffing ladder (Base HC → Shrinkage HC → arrival-coverage “answer rate”) to pick a pilot level and show the expected answer-rate for that level.

If a pilot is included in the deck:
- Add a **Pilot Program (Inbound Answering)** row to the “Your Investment Options” table.
- Add a “World Class Answer Rate” line under the **Inbound Answering** answer-rate cell only (never on Pilot/RHC/RHC+).
If no pilot: omit both.

Pilot pricing (matches `scripts/run_pipeline.py`):

```python
MYBCAT_WEEKLY_RATE = 480
MYBCAT_OT_HOURLY = 18
WEEKEND_PREMIUM_PER_DAY = 25
SHRINK_FACTOR = 0.80  # shrinkage_pct=20%

weekend_days = int(HAS_SATURDAY) + int(HAS_SUNDAY)

# PILOT_LEVEL = Base HC integer (staffing level chosen from ladder)
# PILOT_CALCULATION = "base" or "shrinkage"
PILOT_FTE_TOTAL = PILOT_LEVEL if PILOT_CALCULATION == "base" else max(PILOT_LEVEL / SHRINK_FACTOR, 1.25)

PILOT_BASE = MYBCAT_WEEKLY_RATE * PILOT_FTE_TOTAL
PILOT_OT = MYBCAT_OT_HOURLY * PILOT_LEVEL * OT_HOURS
PILOT_WEEKEND = WEEKEND_PREMIUM_PER_DAY * PILOT_LEVEL * weekend_days

PILOT_WEEKLY = PILOT_BASE + PILOT_OT + PILOT_WEEKEND
PILOT_MONTHLY = PILOT_WEEKLY * 4.33
PILOT_ANNUAL = PILOT_MONTHLY * 12
```

---

## Step 5.5 - Revenue Leak Estimate

Estimate potential revenue lost due to missed calls.

```python
# Conservative assumptions (defaults; override per client if known)
# NOTE: These are multiplicative to keep the estimate conservative.
APPT_SEEKING_PCT = 60     # % of missed calls that were appointment-seeking
NEW_PATIENT_PCT = 35      # % of appointment-seeking calls that are new patients
CONVERSION_PCT = 15       # % that would book if answered (high-intent)
AVG_APPT_VALUE = 500      # First-visit average value ($)

# Weekly revenue leak (open-hours only)
MISSED_CALLS_WEEK = OPEN_MISSED / WEEKS_IN_RANGE
REVENUE_LEAK_WEEKLY = (
    MISSED_CALLS_WEEK
    * (APPT_SEEKING_PCT / 100.0)
    * (NEW_PATIENT_PCT / 100.0)
    * (CONVERSION_PCT / 100.0)
    * AVG_APPT_VALUE
)

# Monthly and annual
REVENUE_LEAK_MONTHLY = REVENUE_LEAK_WEEKLY * 4.33
REVENUE_LEAK_ANNUAL = REVENUE_LEAK_MONTHLY * 12
```

**Store:** `REVENUE_LEAK_WEEKLY`, `REVENUE_LEAK_MONTHLY`, `REVENUE_LEAK_ANNUAL`
**Also store (for deck transparency):** `APPT_SEEKING_PCT`, `NEW_PATIENT_PCT`, `CONVERSION_PCT`, `AVG_APPT_VALUE`

---

## Step 5.6 - ROI Calculation

Calculate return on investment for each option.

```python
def calculate_roi(cost_annual, revenue_leak_annual):
    """
    ROI = (Revenue Captured - Cost) / Cost × 100

    Assumes 100% of revenue leak can be captured with better coverage.
    """
    if cost_annual == 0:
        return 0

    net_benefit = revenue_leak_annual - cost_annual

    if net_benefit > 0:
        roi = round((net_benefit / cost_annual) * 100, 1)
    else:
        roi = round((net_benefit / cost_annual) * 100, 1)  # Will be negative

    return roi

INBOUND_ROI = calculate_roi(INBOUND_ANNUAL, REVENUE_LEAK_ANNUAL)
RHC_ROI = calculate_roi(RHC_ANNUAL, REVENUE_LEAK_ANNUAL)
HIRE_ROI = calculate_roi(HIRE_ANNUAL, REVENUE_LEAK_ANNUAL)
```

**Store:** `INBOUND_ROI`, `RHC_ROI`, `HIRE_ROI`

---

## Step 5.7 - Client-Facing Options Table (4 Options)

Build the client-facing options table (this must appear consistently across the deck: pricing slide, options slide, and next steps).

| Option | Weekly | Monthly | Expected Answer Rate | Notes |
|---|---:|---:|---:|---|
| **Inbound Answering** | **${{INBOUND_WEEKLY}}** | **${{INBOUND_MONTHLY}}** | **90%+** | Phones-only coverage |
| **RHC** | **${{RHC_WEEKLY}}** | **${{RHC_MONTHLY}}** | **90%+** | Full service (includes outbound + scheduling) |
| **RHC+ Growth** | **${{RHC_GROWTH_WEEKLY}}** | **${{RHC_GROWTH_MONTHLY}}** | **90%+** | Capture ${{MONTHLY_LEAK}}/mo + monthly consulting |
| **In-House Hire** | **${{HIRE_WEEKLY}}** | **${{HIRE_MONTHLY}}** | **Varies** | Hiring + training + PTO/sick coverage |

Rules:
- Phones-only (Inbound Answering) is based on `BASE_FTE`.
- RHC and In-House are based on `SHRINKAGE_FTE`.
- RHC+ Growth = RHC + $500/week add-on + 1x/month consulting session.

---

## Step 5.8 - Savings Calculation

Calculate savings vs in-house hiring.

```python
# Inbound savings vs In-House
INBOUND_SAVINGS_WEEKLY = HIRE_WEEKLY - INBOUND_WEEKLY
INBOUND_SAVINGS_MONTHLY = HIRE_MONTHLY - INBOUND_MONTHLY
INBOUND_SAVINGS_ANNUAL = HIRE_ANNUAL - INBOUND_ANNUAL
INBOUND_SAVINGS_PCT = round((INBOUND_SAVINGS_ANNUAL / HIRE_ANNUAL) * 100, 1) if HIRE_ANNUAL > 0 else 0

# RHC savings vs In-House
RHC_SAVINGS_WEEKLY = HIRE_WEEKLY - RHC_WEEKLY
RHC_SAVINGS_MONTHLY = HIRE_MONTHLY - RHC_MONTHLY
RHC_SAVINGS_ANNUAL = HIRE_ANNUAL - RHC_ANNUAL
RHC_SAVINGS_PCT = round((RHC_SAVINGS_ANNUAL / HIRE_ANNUAL) * 100, 1) if HIRE_ANNUAL > 0 else 0
```

**Store:** `INBOUND_SAVINGS_WEEKLY`, `INBOUND_SAVINGS_MONTHLY`, `INBOUND_SAVINGS_ANNUAL`, `INBOUND_SAVINGS_PCT`, `RHC_SAVINGS_WEEKLY`, `RHC_SAVINGS_MONTHLY`, `RHC_SAVINGS_ANNUAL`, `RHC_SAVINGS_PCT`

---

## Step 5.9 - Breakeven Calculation

Calculate how many converted patients needed to cover MyBCAT cost.

```python
# Breakeven = Annual Cost / Average Patient Value
INBOUND_BREAKEVEN = round(INBOUND_ANNUAL / AVG_PATIENT_VALUE)
RHC_BREAKEVEN = round(RHC_ANNUAL / AVG_PATIENT_VALUE)

# As percentage of missed calls
if MISSED_CALLS_WEEK * 52 > 0:
    INBOUND_BREAKEVEN_PCT = round((INBOUND_BREAKEVEN / (MISSED_CALLS_WEEK * 52)) * 100, 1)
    RHC_BREAKEVEN_PCT = round((RHC_BREAKEVEN / (MISSED_CALLS_WEEK * 52)) * 100, 1)
else:
    INBOUND_BREAKEVEN_PCT = 0
    RHC_BREAKEVEN_PCT = 0
```

**Store:** `INBOUND_BREAKEVEN`, `RHC_BREAKEVEN`, `INBOUND_BREAKEVEN_PCT`, `RHC_BREAKEVEN_PCT`

---

## Step 5.9b - Pricing Verification (Checks & Balances)

Before charts/presentation, verify pricing outputs are internally consistent and match the formulas.

### Required Inputs
- `BASE_FTE`, `SHRINKAGE_FTE`
- `TOTAL_WEEKLY_HOURS`, `OT_HOURS`, `HAS_SATURDAY`, `HAS_SUNDAY`

### Recompute + Compare (Internal Audit)

```python
def pricing_audit():
    issues = []

    # Basic validity
    for name, value in [
        ("BASE_FTE", BASE_FTE),
        ("SHRINKAGE_FTE", SHRINKAGE_FTE),
        ("OT_HOURS", OT_HOURS),
        ("INBOUND_WEEKLY", INBOUND_WEEKLY),
        ("RHC_WEEKLY", RHC_WEEKLY),
        ("RHC_GROWTH_WEEKLY", RHC_GROWTH_WEEKLY),
        ("HIRE_WEEKLY", HIRE_WEEKLY),
    ]:
        if value is None:
            issues.append(("CRITICAL", f"{name} is missing"))
        elif isinstance(value, (int, float)) and value < 0:
            issues.append(("CRITICAL", f"{name} is negative: {value}"))

    # Sanity expectations (flag exceptions)
    if RHC_WEEKLY < INBOUND_WEEKLY:
        issues.append(("WARNING", "RHC is cheaper than Inbound. Verify FTE multipliers and rounding."))
    if RHC_GROWTH_WEEKLY < RHC_WEEKLY:
        issues.append(("WARNING", "RHC+ Growth is cheaper than RHC. Verify addon amount."))
    if HIRE_WEEKLY < INBOUND_WEEKLY:
        issues.append(("WARNING", "In-house is cheaper than Inbound. Verify base/OT rates and hours."))

    # Shrinkage rule check
    expected_shrinkage = max(BASE_FTE / 0.80, 1.25)
    if abs(SHRINKAGE_FTE - expected_shrinkage) > 0.05:
        issues.append(("WARNING", f"SHRINKAGE_FTE mismatch. Expected ~{expected_shrinkage:.2f}, got {SHRINKAGE_FTE:.2f}."))

    return issues

PRICING_AUDIT_ISSUES = pricing_audit()
PRICING_AUDIT_PASS = not any(level == "CRITICAL" for level, _ in PRICING_AUDIT_ISSUES)
```

**Store:** `PRICING_AUDIT_ISSUES`, `PRICING_AUDIT_PASS`

If `PRICING_AUDIT_PASS` is false, stop and resolve before proceeding.

---

## IMPORTANT: Presentation Display Guidelines

### Value-Based Pricing Display

**CRITICAL:** Never show FTE, hours, or rate calculations next to prices in the presentation. Clients should buy on VALUE, not do mental math on pricing.

**DO show in presentation:**
- Final weekly/monthly/annual prices (flat numbers)
- Services included in each option
- Value comparison (what you get)
- Savings vs in-house
- ROI and breakeven

**DO NOT show in presentation:**
- FTE numbers next to prices
- Hourly rates
- "× FTE × hours" calculations
- Rate breakdowns

**Acceptable FTE mention (separate from pricing):**
```
"Based on your call patterns, you need coverage equivalent to
approximately X staff members to answer 90% of calls."
```

**NOT acceptable:**
```
"$480/week × 1.25 FTE = $600/week"  ← Never show this
"$18/hr × 5 OT hours"              ← Never show this
```

### How to Present FTE (If Needed)

FTE can be mentioned in the **analysis section** (not pricing section):
- "Your call volume requires approximately X dedicated agents"
- "To reach 90% answer rate, you need X coverage"

Keep FTE discussion **separate** from the pricing slides.

---

## Internal Pricing Calculations (NOT for Client Display)

These formulas are for internal calculation only:

```
INTERNAL CALCULATION (do not show client):
- BASE_FTE: CDF at 90% coverage (ignore level 0)
- SHRINKAGE_FTE: BASE_FTE / 0.80

Rate structure:
- MyBCAT: $480/week base, $18/hr OT
- In-House: $960/week base, $36/hr OT
- Weekend: $25 × BASE_FTE per day
```

---

## Revenue Leak Assumptions

```
- Conversion rate: 15% of missed calls would convert
- Average patient value: $500 (first visit)
- Only counts missed calls during open hours
```

---

## Variables Output from Phase 5

```
# Inbound pricing
INBOUND_WEEKLY
INBOUND_MONTHLY
INBOUND_ANNUAL
INBOUND_ROI
INBOUND_SAVINGS_WEEKLY
INBOUND_SAVINGS_MONTHLY
INBOUND_SAVINGS_ANNUAL
INBOUND_SAVINGS_PCT
INBOUND_BREAKEVEN
INBOUND_BREAKEVEN_PCT

# RHC pricing
RHC_WEEKLY
RHC_MONTHLY
RHC_ANNUAL
RHC_ROI
RHC_SAVINGS_WEEKLY
RHC_SAVINGS_MONTHLY
RHC_SAVINGS_ANNUAL
RHC_SAVINGS_PCT
RHC_BREAKEVEN
RHC_BREAKEVEN_PCT

# In-House pricing
HIRE_WEEKLY
HIRE_MONTHLY
HIRE_ANNUAL
HIRE_ROI

# Revenue leak
REVENUE_LEAK_WEEKLY
REVENUE_LEAK_MONTHLY
REVENUE_LEAK_ANNUAL
```
