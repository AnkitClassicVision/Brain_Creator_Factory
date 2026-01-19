# Phase 1: Discovery & Setup

## Step 1.1 - Find Data Files

```
Search current directory for:
- .csv files
- .xlsx files

List found files with:
- Filename
- Size
- Modification date

Ask user: "Which file(s) should I analyze?"
```

---

## Step 1.2 - Gather Client Metadata

Ask these questions (can be combined):

| Question | Variable | Example |
|----------|----------|---------|
| Office/Client Name? | `CLIENT_NAME` | Griebenow Eyecare |
| Website URL? | `WEBSITE_URL` | griebenoweyecare.com |
| Specialty? | `SPECIALTY` | Optometry |
| Single or multi-location? | `LOCATION_COUNT` | 2 |
| Client tagline (optional)? | `CLIENT_TAGLINE` | Serving the Fox Valley since 1979 |

---

## Step 1.3 - Pull Website Information

Using the provided website URL, extract:

| Data Point | Variable | Format |
|------------|----------|--------|
| Business Hours | `BUSINESS_HOURS` | Mon-Fri 8am-5pm |
| Business Hours (detailed) | `BUSINESS_HOURS_DESC` | Monday-Friday 8:00 AM - 5:00 PM |
| Timezone | `TIMEZONE` | America/Chicago |
| Location addresses | `LOCATION_LIST` | Clintonville & New London |
| Phone numbers | `PHONE_NUMBERS` | (715) 823-5112, (920) 982-3711 |
| Lunch hours | `LUNCH_HOURS` | Unknown (if not listed) |

---

## Step 1.3b - Closures & Exceptions (Ask Explicitly)

Website hours often omit holiday/temporary closures. Ask:
- "Do you have any holiday closures or temporary closure dates in this period?"
- "Do any locations have different hours or a different timezone?"

**Store (if provided):**
- `CLOSURES = ['YYYY-MM-DD', ...]` (dates in the location’s local calendar)
- If multi-location: `LOCATION_OVERRIDES[location_name] = { business_hours, timezone, closures }`

**Important:** Closures should be treated as **closed hours** even if they fall during normal business hours.

---

## Step 1.4 - Calculate Weekly Coverage Hours

**Parse business hours to calculate:**

```python
# Example: Mon-Fri 8am-5pm, Sat 9am-1pm
# Calculate hours per day and total weekly hours

HOURS_PER_DAY = {}  # e.g., {"Mon": 9, "Tue": 9, "Wed": 9, "Thu": 9, "Fri": 9, "Sat": 4}

# Weekly totals
WEEKDAY_HOURS = sum of Mon-Fri hours
SATURDAY_HOURS = hours on Saturday (0 if closed)
SUNDAY_HOURS = hours on Sunday (0 if closed)
TOTAL_WEEKLY_HOURS = WEEKDAY_HOURS + SATURDAY_HOURS + SUNDAY_HOURS

# Coverage flags
HAS_SATURDAY = SATURDAY_HOURS > 0
HAS_SUNDAY = SUNDAY_HOURS > 0
HAS_OVERTIME = TOTAL_WEEKLY_HOURS > 40

# Calculate OT hours (anything over 40)
REGULAR_HOURS = min(TOTAL_WEEKLY_HOURS, 40)
OT_HOURS = max(TOTAL_WEEKLY_HOURS - 40, 0)

# Lunch deduction (if known)
if LUNCH_HOURS != "Unknown":
    LUNCH_MINUTES_PER_DAY = parse lunch duration
    TOTAL_WEEKLY_HOURS -= (LUNCH_MINUTES_PER_DAY / 60) * number_of_days
```

**Store coverage variables:**
```
TOTAL_WEEKLY_HOURS = Total hours office is open per week
REGULAR_HOURS = Hours up to 40 (standard coverage)
OT_HOURS = Hours over 40 (overtime coverage)
HAS_SATURDAY = True/False
HAS_SUNDAY = True/False
SATURDAY_HOURS = Hours on Saturday
SUNDAY_HOURS = Hours on Sunday
```

**Present extracted metadata to user for confirmation before proceeding.**

---

## Step 1.5 - Client Confirmation Gate (Required)

Before moving to ingestion/analysis, explicitly confirm:
- timezone
- business hours (and per-location overrides if applicable)
- closure calendar (or confirm “none”)

Record confirmations:
```
confirmations.timezone = confirmed|assumed
confirmations.business_hours = confirmed|assumed
confirmations.closures = confirmed|unconfirmed
confirmations.location_schedules = confirmed|assumed
```

---

## STOP AND ASK USER IF:

- **Multiple CSV/XLSX files found** → "Which file(s) should I analyze?"
- **Website scraping fails** → "I couldn't access the website. Please provide: Business Hours, Timezone, Location(s)"
- **Business hours not found on website** → "What are your business hours? (e.g., Mon-Fri 8am-5pm)"
- **Multiple locations detected** → "Which location(s) should I include in the analysis?"
- **Timezone unclear from address** → "What timezone is this office in?" (Show IANA options from reference_tables.md)

---

## Variables Output from Phase 1

```
CLIENT_NAME
CLIENT_TAGLINE
WEBSITE_URL
SPECIALTY
LOCATION_COUNT
LOCATION_LIST
PHONE_NUMBERS
BUSINESS_HOURS
BUSINESS_HOURS_DESC
TIMEZONE
CONFIRMATIONS (timezone/business_hours/closures/location_schedules)
CLOSURES (optional)
LOCATION_OVERRIDES (optional)
LUNCH_HOURS
TOTAL_WEEKLY_HOURS
REGULAR_HOURS
OT_HOURS
HAS_SATURDAY
HAS_SUNDAY
SATURDAY_HOURS
SUNDAY_HOURS
```
