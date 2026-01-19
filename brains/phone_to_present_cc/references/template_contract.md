# Presentation Template Variable Contract

All templates MUST support these placeholders. This contract defines the required variables for presentation templates used in the phone_to_present workflow.

---

## Client Information

| Variable | Description | Example |
|----------|-------------|---------|
| `{{CLIENT_NAME}}` | Full client/practice name | "Casey Optical Too" |
| `{{CLIENT_SLUG}}` | URL-safe lowercase name | "casey_optical_too" |
| `{{WEBSITE_URL}}` | Client website | "https://caseyoptical.com" |
| `{{SPECIALTY}}` | Business specialty | "Optometry" |
| `{{TAGLINE}}` | Optional client tagline | "Your vision, our priority" |
| `{{LOCATION_COUNT}}` | Number of locations | "1" |
| `{{LOCATION_LIST}}` | Comma-separated locations | "Main Office, Downtown" |

---

## Date & Period

| Variable | Description | Example |
|----------|-------------|---------|
| `{{ANALYSIS_DATE}}` | Date of analysis | "2026-01-15" |
| `{{DATA_PERIOD_START}}` | Start of data range | "2025-11-01" |
| `{{DATA_PERIOD_END}}` | End of data range | "2026-01-10" |
| `{{WEEKS_ANALYZED}}` | Number of weeks in data | "10" |
| `{{DATE_RANGE}}` | Formatted date range | "Nov 1, 2025 - Jan 10, 2026" |
| `{{DAYS_ANALYZED}}` | Number of days | "71" |

---

## Primary KPIs (Open Hours Only)

| Variable | Description | Example |
|----------|-------------|---------|
| `{{ANSWER_RATE}}` | Open hours answer rate | "92.9%" |
| `{{MISS_RATE}}` | Open hours miss rate | "7.1%" |
| `{{GRADE}}` | Letter grade (A/B/C/D/F) | "B" |
| `{{GRADE_BG_COLOR}}` | Background color for grade | "#F97316" |
| `{{GRADE_TEXT_COLOR}}` | Text color for grade | "#FFFFFF" |
| `{{MISSED_CALLS_WEEK}}` | Average missed calls per week | "14.2" |
| `{{MISSED_PER_DAY}}` | Average missed calls per day | "2.0" |
| `{{MISS_RATIO}}` | Inverse of miss rate | "1 in 14" |

---

## Volume & Distribution

| Variable | Description | Example |
|----------|-------------|---------|
| `{{TOTAL_INBOUND}}` | Total open hours inbound calls | "1,423" |
| `{{TOTAL_RECORDS}}` | Total records in dataset | "2,156" |
| `{{ANSWERED_COUNT}}` | Total answered calls | "1,322" |
| `{{MISSED_COUNT}}` | Total missed calls | "101" |
| `{{ANSWERED_PCT}}` | Answered percentage | "92.9%" |
| `{{MISSED_PCT}}` | Missed percentage | "7.1%" |

---

## Process vs Capacity Analysis (Slide 8)

| Variable | Description | Example |
|----------|-------------|---------|
| `{{PROCESS_MISS_PCT}}` | Percentage of misses due to process | "68%" |
| `{{CAPACITY_MISS_PCT}}` | Percentage due to capacity | "32%" |

---

## Worst Windows (Pain Points)

| Variable | Description | Example |
|----------|-------------|---------|
| `{{WORST_HOUR_1}}` | Worst time slot | "Thursday 9am" |
| `{{WORST_HOUR_1_RATE}}` | Miss rate at worst time | "23.5%" |
| `{{WORST_HOUR_1_COUNT}}` | Call count at worst time | "17" |
| `{{WORST_HOUR_2}}` | Second worst time slot | "Monday 2pm" |
| `{{WORST_HOUR_2_RATE}}` | Miss rate at second worst | "18.2%" |
| `{{WORST_HOUR_3}}` | Third worst time slot | "Friday 10am" |
| `{{WORST_HOUR_3_RATE}}` | Miss rate at third worst | "15.8%" |

---

## Staffing (FTE)

| Variable | Description | Example |
|----------|-------------|---------|
| `{{BASE_FTE}}` | Base FTE requirement | "2.15" |
| `{{SHRINKAGE_FTE}}` | Shrinkage-adjusted FTE | "2.69" |
| `{{SHRINKAGE_PCT}}` | Shrinkage percentage | "20" |

---

## Pricing - Weekly (Slide 18)

Template already includes `$` symbol - provide numeric values formatted with commas.

| Variable | Description | Example |
|----------|-------------|---------|
| `{{HIRE_WEEKLY}}` | In-house hiring cost | "4,140" |
| `{{INBOUND_WEEKLY}}` | MyBCAT Inbound | "1,032" |
| `{{RHC_WEEKLY}}` | MyBCAT RHC | "1,292" |
| `{{RHC_GROWTH_WEEKLY}}` | MyBCAT RHC + Growth | "1,792" |
| `{{PILOT_WEEKLY}}` | Pilot program (if enabled) | "600" |

---

## Pricing - Monthly

| Variable | Description | Example |
|----------|-------------|---------|
| `{{HIRE_MONTHLY}}` | In-house monthly | "17,926" |
| `{{INBOUND_MONTHLY}}` | MyBCAT Inbound monthly | "4,469" |
| `{{RHC_MONTHLY}}` | MyBCAT RHC monthly | "5,594" |
| `{{RHC_GROWTH_MONTHLY}}` | MyBCAT RHC + Growth monthly | "7,761" |
| `{{PILOT_MONTHLY}}` | Pilot monthly (if enabled) | "2,598" |

---

## Pricing - Annual

| Variable | Description | Example |
|----------|-------------|---------|
| `{{HIRE_ANNUAL}}` | In-house annual | "215,112" |
| `{{INBOUND_ANNUAL}}` | MyBCAT Inbound annual | "53,628" |
| `{{RHC_ANNUAL}}` | MyBCAT RHC annual | "67,128" |
| `{{RHC_GROWTH_ANNUAL}}` | MyBCAT RHC + Growth annual | "93,132" |
| `{{PILOT_ANNUAL}}` | Pilot annual (if enabled) | "31,176" |

---

## Savings vs DIY Staffing

| Variable | Description | Example |
|----------|-------------|---------|
| `{{INBOUND_SAVINGS_WEEKLY}}` | HIRE_WEEKLY - INBOUND_WEEKLY | "3,108" |
| `{{RHC_SAVINGS_WEEKLY}}` | HIRE_WEEKLY - RHC_WEEKLY | "2,848" |
| `{{RHC_GROWTH_SAVINGS_WEEKLY}}` | HIRE_WEEKLY - RHC_GROWTH_WEEKLY | "2,348" |
| `{{PILOT_SAVINGS_WEEKLY}}` | HIRE_WEEKLY - PILOT_WEEKLY (if enabled) | "3,540" |
| `{{INBOUND_SAVINGS_PCT}}` | Savings percentage vs hire | "75%" |
| `{{RHC_SAVINGS_PCT}}` | Savings percentage vs hire | "69%" |

---

## Revenue Leak

| Variable | Description | Example |
|----------|-------------|---------|
| `{{WEEKLY_LEAK}}` | Weekly revenue leak estimate | "1,575" |
| `{{MONTHLY_LEAK}}` | Monthly revenue leak | "6,820" |
| `{{ANNUAL_LEAK}}` | Annual revenue leak | "81,840" |
| `{{APPT_SEEKING_PCT}}` | Appointment seeking percentage | "60" |
| `{{NEW_PATIENT_PCT}}` | New patient percentage | "35" |
| `{{CONVERSION_PCT}}` | Conversion percentage | "15" |
| `{{AVG_APPT_VALUE}}` | Average appointment value | "500" |

---

## Pilot Program Injection (Optional)

These are used when Pilot Program is enabled:

| Variable | Description | Usage |
|----------|-------------|-------|
| `{{PILOT_INVESTMENT_ROW}}` | Full HTML row for pilot pricing | Injected into investment table |
| `{{WORLD_CLASS_ANSWER_RATE_LINE}}` | Pilot answer rate line | Under Inbound column |

When pilot is NOT enabled, these must be empty strings `""`.

---

## Conditional Blocks

Templates may use conditional sections:

```markdown
{{#PILOT_ENABLED}}
  <!-- Content shown only when Pilot is active -->
{{/PILOT_ENABLED}}
```

---

## Metadata & Methodology

| Variable | Description | Example |
|----------|-------------|---------|
| `{{DATA_SOURCE}}` | Data source description | "Phone Provider Export" |
| `{{CONFIDENCE_LEVEL}}` | Data confidence | "High" |
| `{{DISPOSITION_METHOD}}` | How disposition was determined | "Direct mapping" |
| `{{METHODOLOGY_CAVEAT}}` | Any data caveats | "" |
| `{{TIMEZONE_DESC}}` | Timezone description | "America/Chicago" |
| `{{TIMEZONE_RATIONALE}}` | How timezone was determined | "Confirmed by user" |
| `{{BUSINESS_HOURS_DESC}}` | Business hours description | "Mon-Fri 8am-5pm, Sat 9am-1pm" |
| `{{BUSINESS_HOURS_RATIONALE}}` | How hours were determined | "Scraped from website" |

---

## Critical Requirements

### Slide 18 (Paths Forward) MUST:
1. Use v4 HTML structure with `class="pf-table"` (NOT markdown table)
2. Include all required CSS classes:
   - `pf-container`
   - `pf-icon-check`, `pf-icon-warn`, `pf-icon-x`
   - `pf-rhc`
   - `pf-badge`
3. Include SVG icons for feature checkmarks
4. Show "MOST POPULAR" badge on RHC column

### Forbidden in Templates:
- Markdown tables (`| --- |`) for Slide 18
- Unreplaced `{{PLACEHOLDER}}` tokens in output
- Emojis in client-facing content
- FTE numbers adjacent to pricing

---

*Contract Version: 1.0*
*Last Updated: 2026-01-15*
*Based on: phone_to_present workflow and WORKFLOW_IMPROVEMENTS.md*
