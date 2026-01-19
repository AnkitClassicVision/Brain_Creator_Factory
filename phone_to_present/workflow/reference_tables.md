# Reference Tables

## IANA Timezones (US)

| Region | Timezone | UTC Offset | DST |
|--------|----------|------------|-----|
| Eastern | America/New_York | -5 | Yes |
| Central | America/Chicago | -6 | Yes |
| Mountain | America/Denver | -7 | Yes |
| Mountain (AZ) | America/Phoenix | -7 | No |
| Pacific | America/Los_Angeles | -8 | Yes |
| Alaska | America/Anchorage | -9 | Yes |
| Hawaii | Pacific/Honolulu | -10 | No |

### State to Timezone Quick Reference

| States | Timezone |
|--------|----------|
| CT, DE, FL, GA, IN (most), KY (east), MA, MD, ME, MI, NC, NH, NJ, NY, OH, PA, RI, SC, TN (east), VA, VT, WV | America/New_York |
| AL, AR, IA, IL, IN (some), KS (most), KY (west), LA, MN, MO, MS, ND, NE (east), OK, SD (east), TN (west), TX (most), WI | America/Chicago |
| AZ | America/Phoenix |
| CO, ID (south), KS (west), MT, NM, SD (west), NE (west), TX (west), UT, WY | America/Denver |
| CA, ID (north), NV, OR, WA | America/Los_Angeles |
| AK | America/Anchorage |
| HI | Pacific/Honolulu |

---

## Grade Thresholds

| Grade | Answer Rate | Description | Display Color |
|-------|-------------|-------------|---------------|
| A | 95%+ | Excellent - Industry leader | GREEN |
| B | 90-94% | Good - Meets benchmark | ORANGE |
| C | 80-89% | Needs Improvement | ORANGE |
| D | 70-79% | Poor - Significant issues | RED |
| F | <70% | Critical - Immediate action needed | RED |

**Color Logic:** Only A grade is highlighted in green. B and C show orange (room for improvement). D and F show red (critical).

---

## Pricing Rate Tables (INTERNAL USE ONLY)

**IMPORTANT:** These tables are for internal pricing calculations. Never show rates, FTE, or hourly breakdowns to clients. Present final prices only.

### Internal Rate Structure

| Service | Weekly Base | OT Rate | Notes |
|---------|-------------|---------|-------|
| MyBCAT (Inbound/RHC) | $480/week | $18/hr | Internal calculation only |
| In-House | $960/week | $36/hr | Internal calculation only |

### Weekend Premiums (Internal)

| Day | Premium |
|-----|---------|
| Saturday | $25 × BASE_FTE |
| Sunday | $25 × BASE_FTE |

### FTE Calculations (Internal)

| Variable | Formula | Minimum |
|----------|---------|---------|
| BASE_FTE | CDF at 90% coverage (ignore level 0) | 1.0 |
| SHRINKAGE_FTE | BASE_FTE / 0.80 | 1.25 |

### FTE by Option (Internal)

| Option | FTE Used |
|--------|----------|
| Inbound (phones-only) | BASE_FTE |
| RHC | SHRINKAGE_FTE |
| RHC+ Growth | SHRINKAGE_FTE |
| In-House | SHRINKAGE_FTE |

**Shrinkage Factor (20%)** accounts for: breaks, training, admin, PTO

---

## Client-Facing FTE Statement (Optional)

If FTE needs to be mentioned, present it **separately from pricing**:

```
"Based on your call patterns, you need coverage equivalent to
approximately [SHRINKAGE_FTE] dedicated staff to answer 90%+ of calls."
```

**Never say:** "$X per FTE" or show calculation breakdowns

---

## Revenue Leak Assumptions

| Parameter | Default Value | Notes |
|-----------|---------------|-------|
| Appointment-Seeking % | 60% | % of missed calls that were appointment-seeking (conservative) |
| New Patient % | 35% | % of appointment-seeking calls that are new patients |
| Conversion Rate | 15% | % that would book if answered (high-intent) |
| Average Appointment Value | $500 | First-visit revenue |
| Only Count | Open Hours | Closed hours misses excluded |

### Revenue Leak Formula

```
Weekly Revenue Leak =
  (Missed Calls During Open Hours / Weeks)
  × Appointment-Seeking %
  × New Patient %
  × Conversion Rate
  × Average Appointment Value

Monthly = Weekly × 4.33
Annual = Monthly × 12
```

---

## Disposition Mapping

### Standard Categories

| Normalized | Meaning |
|------------|---------|
| answered | Call was picked up and conversation occurred |
| missed | Call rang but was not answered |
| voicemail | Caller left a voicemail message |
| abandoned | Caller hung up before answer (usually <10 sec) |
| redirected | Call was forwarded/transferred |
| unknown | Could not determine disposition |

### Common Raw Values → Normalized

| Raw Value (contains) | → Normalized |
|---------------------|--------------|
| answered, completed, connected, talking, success | answered |
| missed, no answer, unanswered, ring no answer, rna | missed |
| voicemail, vm, left message, voice mail | voicemail |
| abandoned, hang up, hungup, caller hung up | abandoned |
| redirect, forwarded, transferred, post redirect | redirected |
| (blank), null, unknown | unknown |

### Duration-Based Fallback

When disposition column is missing:

| Duration | → Inferred Disposition | Confidence |
|----------|----------------------|------------|
| ≤ 0 sec | missed | 0.7 |
| 1-30 sec | missed | 0.6 |
| > 30 sec | answered | 0.7 |

---

## Specialty Reference

Common healthcare specialties for client metadata:

| Category | Specialties |
|----------|-------------|
| Eye Care | Optometry, Ophthalmology |
| Dental | General Dentistry, Orthodontics, Oral Surgery, Periodontics |
| Medical | Family Medicine, Internal Medicine, Pediatrics |
| Surgical | Orthopedics, Plastic Surgery, General Surgery |
| Mental Health | Psychology, Psychiatry, Counseling |
| Therapy | Physical Therapy, Occupational Therapy, Speech Therapy |
| Specialty | Dermatology, Cardiology, Gastroenterology, Neurology |
| Women's Health | OB/GYN, Fertility |
| Other | Chiropractic, Podiatry, Audiology |

---

## Phone System Export Formats

### Common Column Patterns by Format Type

| Format Type | Key Columns | Notes |
|-------------|-------------|-------|
| Standard | `Direction`, `Result`, `Duration` | Most common format |
| Detailed | `Call Direction`, `Call Result`, `Talk Time` | Title case columns |
| Technical | `call_type`, `state`, `duration_ms` | Lowercase, milliseconds |
| Basic | `Status`, `Duration`, phone numbers | Minimal fields |
| Legacy | `Type`, `Status`, `Duration` | Older systems |
| Enterprise | `CallType`, `Result`, `TalkTime` | CamelCase format |
| Generic CSV | Basic timestamp, duration, phone fields | Manual export |

---

## Chart Color Codes

### Primary Palette

| Name | Hex | RGB | Use |
|------|-----|-----|-----|
| Brand Teal | #006064 | 0, 96, 100 | Primary brand, headers |
| Success Green | #10B981 | 16, 185, 129 | Answered, positive |
| Warning Yellow | #EAB308 | 234, 179, 8 | Caution, capacity |
| Danger Red | #E63946 | 230, 57, 70 | Missed, process |
| Gray | #6B7280 | 107, 114, 128 | Neutral, secondary |

### Light Variants (for backgrounds)

| Name | Hex | RGB | Use |
|------|-----|-----|-----|
| Light Green | #D1FAE5 | 209, 250, 229 | Low miss rate zones |
| Light Yellow | #FEF3C7 | 254, 243, 199 | Medium miss rate zones |
| Light Red | #FEE2E2 | 254, 226, 226 | High miss rate zones |
| Light Gray | #F3F4F6 | 243, 244, 246 | Backgrounds |

---

## Business Hours Parsing

### Standard Formats

| Input Format | Parsed |
|--------------|--------|
| "Mon-Fri 8am-5pm" | Mon-Fri: 8:00-17:00 |
| "M-F 8:00 AM - 5:00 PM" | Mon-Fri: 8:00-17:00 |
| "Monday through Friday, 8am to 5pm" | Mon-Fri: 8:00-17:00 |
| "8-5 weekdays" | Mon-Fri: 8:00-17:00 |
| "9:00-17:00" | 9:00-17:00 (assume weekdays) |

### Day Abbreviations

| Full | Abbreviation |
|------|--------------|
| Monday | Mon, M |
| Tuesday | Tue, Tu, T |
| Wednesday | Wed, W |
| Thursday | Thu, Th, R |
| Friday | Fri, F |
| Saturday | Sat, S |
| Sunday | Sun, Su |

### Weekly Hours Calculation

```python
# Example: Mon-Fri 8am-5pm, Sat 9am-1pm
hours_per_day = {
    'Mon': 9,  # 8am-5pm = 9 hours
    'Tue': 9,
    'Wed': 9,
    'Thu': 9,
    'Fri': 9,
    'Sat': 4,  # 9am-1pm = 4 hours
    'Sun': 0
}

WEEKDAY_HOURS = sum(hours_per_day[d] for d in ['Mon','Tue','Wed','Thu','Fri'])  # 45
SATURDAY_HOURS = hours_per_day['Sat']  # 4
SUNDAY_HOURS = hours_per_day['Sun']  # 0
TOTAL_WEEKLY_HOURS = WEEKDAY_HOURS + SATURDAY_HOURS + SUNDAY_HOURS  # 49

REGULAR_HOURS = min(TOTAL_WEEKLY_HOURS, 40)  # 40
OT_HOURS = max(TOTAL_WEEKLY_HOURS - 40, 0)  # 9

HAS_SATURDAY = SATURDAY_HOURS > 0  # True
HAS_SUNDAY = SUNDAY_HOURS > 0  # False
```

---

## Pricing Options Table (CLIENT-FACING)

Show only final weekly/monthly prices + what the option includes. Do not show FTE, hourly rates, or pricing math in client decks.

| Option | Weekly | Monthly | Expected Answer Rate | Notes |
|---|---:|---:|---:|---|
| **Inbound Answering** | **${{INBOUND_WEEKLY}}** | **${{INBOUND_MONTHLY}}** | **90%+** | Phones-only coverage |
| **RHC** | **${{RHC_WEEKLY}}** | **${{RHC_MONTHLY}}** | **90%+** | Full service (includes outbound + scheduling) |
| **RHC+ Growth** | **${{RHC_GROWTH_WEEKLY}}** | **${{RHC_GROWTH_MONTHLY}}** | **90%+** | Capture ${{MONTHLY_LEAK}}/mo + monthly consulting |
| **In-House Hire** | **${{HIRE_WEEKLY}}** | **${{HIRE_MONTHLY}}** | **Varies** | Hiring + training + PTO/sick coverage |

Rules:
- Inbound Answering uses `BASE_FTE`.
- RHC + In-House use `SHRINKAGE_FTE`.
- RHC+ Growth = RHC + $500/week add-on + 1x/month consulting session.
