---
marp: true
title: "{{CLIENT_NAME}} | Phone Analysis Report"
description: "{{DATE_RANGE}} | {{TOTAL_INBOUND}} inbound calls analyzed"
theme: default
size: 16:9
paginate: true
style: |
  @import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700;900&display=swap');

  /* =========================================================
     BRAND + GLOBALS
     - Edit only these variables to re-brand the whole deck.
     ========================================================= */
  :root {
    --brand-navy: #27343C;
    --brand-teal: #006064;
    --brand-pop: #4DD0E1;
    --brand-gold: #D3AF5E;

    --bg-color: #F4F6F8;
    --text-main: #27343C;

    --alert-red: #E63946;
    --warning-amber: #EAB308;
    --success-green: #2D6A4F;

    --card-shadow: 0 4px 15px rgba(0,0,0,0.08);
    --radius: 10px;
  }

  section {
    font-family: 'Lato', sans-serif;
    color: var(--text-main);
    background-color: var(--bg-color);
    background-image: linear-gradient(135deg, #fff 0%, var(--bg-color) 100%);
    font-size: 24px;
    padding: 48px;
  }

  /* Keep pagination inside the slide safe area (prevents bottom-edge bleed). */
  section::after {
    right: 60px !important;
    bottom: 40px !important;
    color: rgba(39, 52, 60, 0.45);
    font-size: 0.6em;
  }

  section.title::after,
  section.section-divider::after {
    color: rgba(255, 255, 255, 0.75);
  }

  h1, h2, h3 {
    font-family: 'Lato', sans-serif;
    font-weight: 900;
    color: var(--brand-navy);
    margin-top: 0;
    letter-spacing: -0.02em;
  }

  h1 { font-size: 2.8em; line-height: 1.1; }
  h2 { font-size: 1.8em; border-bottom: none; }
  strong { color: var(--brand-teal); font-weight: 900; }

  .muted { color: rgba(0,0,0,0.55); }
  .small { font-size: 0.85em; }
  .center { text-align: center; }

  /* =========================================================
     SLIDE TYPES
     ========================================================= */
  section.title {
    background-color: var(--brand-navy);
    color: white;
    background-image: radial-gradient(circle at 100% 0%, #00838f, transparent 50%);
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  section.title h1 { color: white; margin-bottom: 20px; }
  section.title h2 {
    color: var(--brand-pop);
    font-size: 1.2em;
    text-transform: uppercase;
    letter-spacing: 3px;
    font-weight: 700;
  }
  section.title p { color: rgba(255,255,255,0.8); font-size: 0.9em; }

  section.section-divider {
    background-color: var(--brand-teal);
    color: white;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  section.section-divider h1 { color: white; }
  section.section-divider h2 { color: var(--brand-pop); }

  section.impact {
    background-color: var(--brand-navy);
    background-image: none;
    color: white;
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: center;
  }
  section.impact h1 { color: white; font-size: 4em; margin-bottom: 10px; }
  section.impact h2 { color: var(--brand-pop); font-size: 1.4em; }
  section.impact p  { color: rgba(255,255,255,0.9); font-size: 1.2em; margin-top: 30px; }

  /* =========================================================
     LISTS + TABLES
     ========================================================= */
  ul { list-style: none; padding: 0; margin: 0; }
  li { margin-bottom: 14px; padding-left: 32px; position: relative; font-size: 0.95em; }
  li::before { content: "•"; position: absolute; left: 0; color: var(--brand-pop); font-weight: 900; font-size: 1.1em; }

  table { width: 100%; border-collapse: collapse; font-size: 0.8em; }
  th { background: var(--brand-navy); color: white; padding: 10px; text-align: left; }
  td { padding: 8px 10px; border-bottom: 1px solid #E5E7EB; }
  tr:nth-child(even) { background: white; }

  .tight-table { font-size: 0.54em; }
  .tight-table th { padding: 6px 8px; }
  .tight-table td { padding: 5px 8px; }

  /* =========================================================
     COMPONENTS
     ========================================================= */
  .card {
    background: white;
    padding: 22px 24px;
    border-radius: var(--radius);
    box-shadow: var(--card-shadow);
  }

  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
    margin-top: 20px;
  }
  .kpi-card { background: white; padding: 18px; border-radius: var(--radius); box-shadow: var(--card-shadow); }
  .kpi-number { font-size: 1.6em; font-weight: 900; color: var(--brand-teal); margin-bottom: 6px; }
  .kpi-label { font-size: 0.85em; color: rgba(0,0,0,0.55); font-weight: 700; }

  .grade-box {
    padding: 18px 22px;
    border-radius: var(--radius);
    text-align: center;
    margin-top: 20px;
    color: white;
    font-weight: 900;
  }
  .grade-box.danger { background: linear-gradient(135deg, var(--alert-red) 0%, #c1121f 100%); }
  .grade-box.success { background: linear-gradient(135deg, var(--success-green) 0%, #1B4332 100%); }
  .grade-box .sub { display:block; font-weight: 700; opacity: 0.9; font-size: 0.85em; margin-top: 6px; }

  .insight {
    background: linear-gradient(135deg, #fff8e1 0%, #fff3cd 100%);
    border-left: 4px solid var(--brand-gold);
    padding: 15px 20px;
    margin: 15px 0;
    border-radius: 0 8px 8px 0;
  }

  .aha-box {
    background: linear-gradient(135deg, var(--brand-teal) 0%, #00838f 100%);
    color: white;
    padding: 25px 30px;
    border-radius: 12px;
    margin: 20px 0;
    text-align: center;
  }
  .aha-box.tight { padding: 18px 22px; margin: 10px 0; }

  .callout {
    background: white;
    padding: 15px 20px;
    border-radius: 8px;
    margin: 12px 0;
  }
  .callout.danger  { border-left: 4px solid var(--alert-red); }
  .callout.warn    { border-left: 4px solid var(--warning-amber); }
  .callout.success { background: #E8F5E9; }

  .split { display:flex; gap: 30px; align-items:center; }
  .col { flex: 1; }
  .col.fixed-350 { flex: 0 0 350px; }
  .col.fixed-320 { flex: 0 0 320px; }

  .danger-box {
    background: linear-gradient(135deg, var(--alert-red) 0%, #c1121f 100%);
    color: white;
    padding: 12px;
    border-radius: 8px;
    text-align: center;
    margin-bottom: 10px;
  }
  .danger-box.big .time { font-size: 1.1em; font-weight: 900; }
  .danger-box.big .pct  { font-size: 1.8em; font-weight: 900; }

  .feature-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 25px;
    margin-top: 30px;
  }
  .feature-card {
    background: white;
    padding: 25px;
    border-radius: var(--radius);
    text-align: center;
    box-shadow: var(--card-shadow);
  }
  .feature-kicker { font-size: 0.9em; margin-bottom: 10px; color: var(--brand-teal); font-weight: 900; }
  .feature-title  { font-size: 1.1em; font-weight: 900; }
  .feature-desc   { font-size: 0.85em; color: rgba(0,0,0,0.55); margin-top: 10px; }

  .options { display:flex; gap: 15px; margin-top: 15px; }
  .option-card {
    flex: 1;
    background: white;
    padding: 20px;
    border-radius: var(--radius);
    border-top: 4px solid var(--brand-teal);
    box-shadow: var(--card-shadow);
    position: relative;
  }
  .option-tier { font-weight: 900; font-size: 0.9em; color: rgba(0,0,0,0.6); }
  .option-name { font-size: 1.2em; font-weight: 900; margin-top: 6px; }
  .option-price { font-size: 2.0em; font-weight: 900; color: var(--brand-teal); margin: 8px 0 2px; }
  .option-per { font-size: 0.9em; color: rgba(0,0,0,0.6); margin-bottom: 10px; }

  .recommended { border: 3px solid var(--brand-gold); }
  .recommended::before {
    content: "RECOMMENDED";
    position: absolute;
    top: -12px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--brand-gold);
    color: white;
    padding: 4px 15px;
    border-radius: 20px;
    font-size: 0.7em;
    font-weight: 900;
  }
---

<!-- ═══════════════════════════════════════════════════════════════════════════
     CORE DECK: 19 Slides (~15-20 min presentation)
     Template Variables: Replace placeholders (e.g., {{CLIENT_NAME}}) with calculated values
═══════════════════════════════════════════════════════════════════════════ -->

<!-- _class: title -->

## Phone Analysis Report
# {{CLIENT_NAME}}
**{{DATE_RANGE}} | {{TOTAL_RECORDS}} Records | {{LOCATION_COUNT}} Location(s)**

*Data-driven insights to improve patient access and capture revenue*

---

# What happens when patients can't reach you?

<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px; margin-top: 40px;">
<div style="text-align: center; padding: 20px; background: #FEE2E2; border-radius: 10px;">
<span style="font-size: 2em; font-weight: 900; color: #E63946;">1</span><br>
<strong>They call back</strong><br>
<span style="color: #666; font-size: 0.85em;">Creating callback burden on your staff</span>
</div>
<div style="text-align: center; padding: 20px; background: #FEF3C7; border-radius: 10px;">
<span style="font-size: 2em; font-weight: 900; color: #EAB308;">2</span><br>
<strong>They try someone else</strong><br>
<span style="color: #666; font-size: 0.85em;">Your competitor down the street</span>
</div>
<div style="text-align: center; padding: 20px; background: #F3F4F6; border-radius: 10px;">
<span style="font-size: 2em; font-weight: 900; color: #6B7280;">3</span><br>
<strong>They give up</strong><br>
<span style="color: #666; font-size: 0.85em;">Delayed care, potential emergencies</span>
</div>
</div>

<div class="insight" style="margin-top: 40px;">
<strong>The phone is your revenue gate.</strong> Every marketing dollar, every referral, every loyal patient starts with a call that gets answered.
</div>

---

# Who We Are

<div style="display: flex; gap: 30px; align-items: center;">
<div style="flex: 1;">

**My Business Care Team (MyBCAT)**

We're not an answering service. We're a **Remote Hospitality Center** staffed by trained specialists who sound like part of your team.

**What makes us different:**
- Trained in {{SPECIALTY}} workflows and terminology
- Your protocols + scheduling system + voice
- HIPAA compliant with real-time dashboard visibility

</div>
<div style="flex: 0 0 280px; text-align: center;">

<div style="background: #f0f0f0; padding: 24px; border-radius: 10px;">
<strong style="font-size: 1.5em; color: #006064;">MyBCAT</strong>
</div>

<div style="margin-top: 12px; font-size: 0.75em; color: #666;">
<strong>Test us yourself:</strong><br>
Live: 770.499.2020<br>
AI Demo: 470.523.7693
</div>

</div>
</div>

<div style="background: #E8F5E9; padding: 8px 12px; border-radius: 8px; margin-top: 10px; font-size: 0.75em;">
<strong>Compliance:</strong> HIPAA | BAA | 90-day retention | Audit trails | Encrypted data.
</div>

---

<!-- _class: section-divider -->
<!-- _backgroundColor: #006064 -->
<!-- _color: #ffffff -->

# DIAGNOSIS
## What {{DAYS_ANALYZED}} Days of Phone Data Reveals

---

# Executive Summary

<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 20px;">
<div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.08);">
<span style="font-size: 2.5em; font-weight: 900; color: #27343C;">{{TOTAL_INBOUND}}</span><br>
<span style="color: #666; font-size: 0.8em;">Inbound Calls</span>
</div>
<div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.08);">
<span style="font-size: 2.5em; font-weight: 900; color: {{ANSWER_RATE_COLOR}};">{{ANSWER_RATE}}%</span><br>
<span style="color: #666; font-size: 0.8em;">Answer Rate (Open Hours)</span>
</div>
<div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.08);">
<span style="font-size: 2.5em; font-weight: 900; color: #E63946;">{{MISSED_OPEN_HOURS}}</span><br>
<span style="color: #666; font-size: 0.8em;">Missed (Business Hours)</span>
</div>
<div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.08);">
<span style="font-size: 2.5em; font-weight: 900; color: #E63946;">~${{ANNUAL_LEAK}}</span><br>
<span style="color: #666; font-size: 0.8em;">Est. Annual Revenue Leak</span>
</div>
</div>

**Analysis Period:** {{DATE_RANGE}} ({{DAYS_ANALYZED}} days)
**Locations:** {{LOCATION_LIST}}
**Data Source:** {{DATA_SOURCE}}

---

# Your Answer Rate: {{ANSWER_RATE}}%

<div style="display: flex; gap: 24px; align-items: center;">
<div style="flex: 1;">

![w:320](charts/answer_rate_gauge.png)

</div>
<div style="flex: 1; font-size: 0.75em;">

**The Grading Scale:**

| Grade | Range | Meaning |
|-------|-------|---------|
| A | 95%+ | Excellent - Rare misses |
| B | 90-94% | Good - Minor gaps |
| **C** | **80-89%** | **Needs attention** |
| D | 70-79% | Problem - Losing patients |
| F | <70% | Critical - Major leakage |

<div style="background: {{GRADE_BG_COLOR}}; color: {{GRADE_TEXT_COLOR}}; padding: 10px; border-radius: 8px; text-align: center; margin-top: 10px;">
<span style="font-size: 1.7em; font-weight: 900;">Grade: {{GRADE}}</span>
</div>

</div>
</div>

<div style="margin-top: 4px; font-size: 0.8em;">
At {{ANSWER_RATE}}%, roughly 1 in {{MISS_RATIO}} callers during business hours don't get through.
</div>

---

<!-- IMPORTANT: Slide 7 (Aha moment) - Spend 2+ minutes here -->

# The Root Cause Discovery

<div style="display: flex; gap: 18px; align-items: flex-start;">
<div style="flex: 0 0 260px;">

![w:220](charts/miss_distribution.png)

</div>
<div style="flex: 1;">

<div class="aha-box tight">
<span style="font-size: 1.05em; font-weight: 900;">{{PROCESS_MISS_PCT}}% of missed calls happened when only 1 line was ringing.</span>
</div>

**What this means:**

<div style="background: white; padding: 8px 10px; border-radius: 10px; border-left: 4px solid #E63946; margin: 4px 0;">
<strong style="font-size: 1.0em;">{{PROCESS_MISS_PCT}}% = Process Issue</strong><br>
<span style="font-size: 0.82em;">Staff was available but occupied elsewhere (front desk, paperwork, back room)</span>
</div>

<div style="background: white; padding: 8px 10px; border-radius: 10px; border-left: 4px solid #EAB308; margin: 4px 0;">
<strong style="font-size: 1.0em;">{{CAPACITY_MISS_PCT}}% = Capacity Issue</strong><br>
<span style="font-size: 0.82em;">Multiple lines ringing, genuinely overwhelmed</span>
</div>

</div>
</div>

---

# When Are You Missing Calls?

<div style="display: flex; gap: 20px;">
<div style="flex: 1;">

![w:420](charts/pain_windows_heatmap.png)

</div>
<div style="flex: 0 0 350px;">

**Your 3 Worst Hours:**

<div style="background: linear-gradient(135deg, #E63946 0%, #c1121f 100%); color: white; padding: 14px; border-radius: 10px; text-align: center; margin-bottom: 10px;">
<span style="font-size: 1.4em; font-weight: 900;">{{WORST_HOUR_1}}</span><br>
<span style="font-size: 1.6em; font-weight: 900;">{{WORST_HOUR_1_RATE}}%</span> miss rate<br>
<span style="font-size: 0.8em;">{{WORST_HOUR_1_COUNT}} calls missed</span>
</div>

<div style="background: linear-gradient(135deg, #E63946 0%, #c1121f 100%); color: white; padding: 12px; border-radius: 10px; text-align: center; margin-bottom: 8px;">
<strong>{{WORST_HOUR_2}}</strong> - {{WORST_HOUR_2_RATE}}% ({{WORST_HOUR_2_COUNT}} missed)
</div>

<div style="background: linear-gradient(135deg, #E63946 0%, #c1121f 100%); color: white; padding: 12px; border-radius: 10px; text-align: center;">
<strong>{{WORST_HOUR_3}}</strong> - {{WORST_HOUR_3_RATE}}% ({{WORST_HOUR_3_COUNT}} missed)
</div>

</div>
</div>

---

# {{MISSED_PER_WEEK}} People Per Week Don't Get Through

<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 30px;">
<div style="background: white; padding: 25px; border-radius: 10px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.08);">
<span style="font-size: 3em; font-weight: 900; color: #E63946;">{{MISSED_OPEN_HOURS}}</span><br>
<span style="font-size: 0.9em; color: #666;">Total missed over {{DAYS_ANALYZED}} days</span><br>
<span style="font-size: 0.8em; color: #999;">(during business hours)</span>
</div>
<div style="background: white; padding: 25px; border-radius: 10px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.08);">
<span style="font-size: 3em; font-weight: 900; color: #E63946;">{{MISSED_PER_WEEK}}</span><br>
<span style="font-size: 0.9em; color: #666;">Average missed per week</span>
</div>
<div style="background: white; padding: 25px; border-radius: 10px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.08);">
<span style="font-size: 3em; font-weight: 900; color: #E63946;">{{MISSED_PER_DAY}}</span><br>
<span style="font-size: 0.9em; color: #666;">Missed per day (weekdays)</span>
</div>
</div>

<div style="margin-top: 30px; font-size: 1.1em;">

**That's {{MISSED_PER_WEEK}} people per week who expected to reach you and didn't.**

Some will call back. Some won't. Some will call your competitor.

</div>

---

<!-- _class: section-divider -->
<!-- _backgroundColor: #006064 -->
<!-- _color: #ffffff -->

# PROGNOSIS
## What This Costs Your Practice

---

# Conservative Revenue Impact

**Our methodology (transparent assumptions):**

| Assumption | Value | Rationale |
|------------|-------|-----------|
| Missed calls/week | {{MISSED_PER_WEEK}} | From your data |
| Appointment-seeking | {{APPT_SEEKING_PCT}}% | Conservative estimate |
| New patients | {{NEW_PATIENT_PCT}}% of above | Industry benchmark |
| Would book if answered | {{CONVERSION_PCT}}% | High-intent callers |
| Average appointment value | ${{AVG_APPT_VALUE}} | {{SPECIALTY}} benchmark |

<div style="display: flex; gap: 30px; margin-top: 20px;">
<div style="flex: 1; background: linear-gradient(135deg, #E63946 0%, #c1121f 100%); color: white; padding: 25px; border-radius: 10px; text-align: center;">
<span style="font-size: 0.9em;">Weekly Revenue Leak</span><br>
<span style="font-size: 2.5em; font-weight: 900;">${{WEEKLY_LEAK}}</span>
</div>
<div style="flex: 1; background: linear-gradient(135deg, #E63946 0%, #c1121f 100%); color: white; padding: 25px; border-radius: 10px; text-align: center;">
<span style="font-size: 0.9em;">Annual Impact</span><br>
<span style="font-size: 2.5em; font-weight: 900;">${{ANNUAL_LEAK}}</span>
</div>
</div>

*This is conservative. It doesn't include lifetime patient value, referrals, or reputation effects.*

---

# Beyond Dollars: The Ripple Effect

<div style="font-size: 0.8em;">

| Factor | Impact | Long-term Effect |
|--------|--------|------------------|
| **First Impressions** | {{MISSED_PER_WEEK}} people/week hit voicemail | Brand perception erodes |
| **Online Reviews** | Frustrated callers leave 1-star reviews | SEO & reputation damage |
| **Referral Hesitation** | "They never answer" spreads | Growth ceiling |
| **Staff Stress** | Callback pile builds daily | Burnout, turnover risk |
| **Competitive Loss** | Caller tries next {{SPECIALTY}} practice | Market share erosion |

</div>

<div class="insight" style="margin-top: 20px;">
<strong>The ${{ANNUAL_LEAK}}/year is just the direct measurable loss.</strong> The reputation and competitive effects compound over time - and they're much harder to reverse.
</div>

---

# Three Paths Forward

<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 20px; font-size: 0.8em;">

<div style="background: #FEE2E2; padding: 20px; border-radius: 10px; border-top: 4px solid #E63946;">
<h3 style="margin: 0 0 15px 0; font-size: 1.1em;">Option 1: Do Nothing</h3>
<p><strong>Cost:</strong> ${{ANNUAL_LEAK}}/year in leaked revenue</p>
<p><strong>Effort:</strong> None</p>
<p><strong>Result:</strong> Problem continues, {{MISSED_PER_WEEK}} missed/week</p>
<p style="color: #E63946; font-weight: bold;">NOT RECOMMENDED</p>
</div>

<div style="background: #FEF3C7; padding: 20px; border-radius: 10px; border-top: 4px solid #EAB308;">
<h3 style="margin: 0 0 15px 0; font-size: 1.1em;">Option 2: Hire Staff</h3>
<p><strong>Cost:</strong> ${{HIRE_WEEKLY}}/wk (${{HIRE_COST_ANNUAL}}/yr)</p>
<p><strong>Effort:</strong> Recruiting, training, managing, PTO coverage</p>
<p><strong>Result:</strong> May help, same architecture problem</p>
<p style="color: #EAB308; font-weight: bold;">PARTIAL SOLUTION</p>
</div>

<div style="background: #D1FAE5; padding: 20px; border-radius: 10px; border-top: 4px solid #059669;">
<h3 style="margin: 0 0 15px 0; font-size: 1.1em;">Option 3: Fix the Process</h3>
<p><strong>Cost:</strong> Inbound: ${{INBOUND_WEEKLY}}/wk • RHC: ${{RHC_WEEKLY}}/wk • RHC+ Growth: ${{RHC_GROWTH_WEEKLY}}/wk</p>
<p><strong>Effort:</strong> 30-day pilot, we handle onboarding</p>
<p><strong>Result:</strong> Dedicated phone resource, 90%+ answer rate</p>
<p style="color: #059669; font-weight: bold;">RECOMMENDED</p>
</div>

</div>

---

<!-- _class: section-divider -->
<!-- _backgroundColor: #006064 -->
<!-- _color: #ffffff -->

# TREATMENT
## How We Solve This

---

# What MyBCAT Provides

<div style="display: flex; gap: 18px;">
<div style="flex: 1; font-size: 0.75em;">

| Service | What You Get |
|---------|--------------|
| **Inbound Calls** | Trained {{SPECIALTY}} specialists answering your lines |
| **Insurance Verification** | Verify benefits before visits, reduce no-shows |
| **Recalls & Confirmations** | Fill your schedule proactively |
| **Waitlist Management** | Fill cancellations fast |
| **AI After-Hours** | Auto-handle calls when you're closed |
| **Real-Time Dashboard** | See performance metrics anytime |

</div>
<div style="flex: 0 0 280px;">

<div style="background: white; padding: 12px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); font-size: 0.95em;">
<strong>Not an answering service.</strong>

A Remote Hospitality Center that uses your protocols, speaks {{SPECIALTY}} language, and books directly in your system.
</div>

</div>
</div>

<div style="background: #E8F5E9; padding: 6px 8px; border-radius: 8px; margin-top: 2px; font-size: 0.7em;">
<strong>Compliance:</strong> HIPAA | BAA provided | Call recordings available | Secure data
</div>

---

# Proof Points

<div style="font-size: 0.95em;">

**Typical Results:**
- Answer rate improvement: 70s% → **90%+**
- Missed calls reduced by **70%+**
- Go-live in **4 weeks** from onboarding

**Compliance & Quality:**
- HIPAA Compliant (BAA provided)
- Call recordings accessible to you
- Your scheduling system integrated

<div class="callout success" style="margin-top: 18px; font-size: 0.9em;">
<strong>Test us:</strong> Live: 770.499.2020 | After-hours AI: 470.523.7693
</div>

</div>

---

# Your Investment Options

<div style="font-size: 0.7em;">

| Option | Weekly Cost | Monthly Cost | Answer Rate | Revenue Impact |
|--------|-------------|--------------|-------------|----------------|
| **Do Nothing** | $0 | $0 | {{ANSWER_RATE}}% | **-${{MONTHLY_LEAK}}/mo lost** |
| **Hire In-House** | ${{HIRE_WEEKLY}} | ${{HIRE_MONTHLY}} | Variable | + recruiting, training, PTO, turnover |{{PILOT_INVESTMENT_ROW}}
| **Inbound Answering** | **${{INBOUND_WEEKLY}}** | **${{INBOUND_MONTHLY}}** | **90%+**{{WORLD_CLASS_ANSWER_RATE_LINE}} | **Capture ${{MONTHLY_LEAK}}/mo** |
| **Remote Hospitality (RHC)** | **${{RHC_WEEKLY}}** | **${{RHC_MONTHLY}}** | **90%+** | **Capture ${{MONTHLY_LEAK}}/mo** |
| **RHC+ Growth** | **${{RHC_GROWTH_WEEKLY}}** | **${{RHC_GROWTH_MONTHLY}}** | **90%+** | **Capture ${{MONTHLY_LEAK}}/mo + monthly consulting** |

</div>

<div style="background: #E8F5E9; padding: 15px 20px; border-radius: 8px; margin-top: 15px; font-size: 0.85em;">
<strong>The business case:</strong> You're currently losing ~${{MONTHLY_LEAK}}/month in missed patient revenue. Our service pays for itself when you convert just a fraction of those missed calls into appointments.
</div>

---

# Paths Forward

<div class="tight-table">

| Feature | Hire In-House | Inbound Answering | Remote Hospitality Center | RHC+ Growth |
|---------|:-------------:|:-----------------:|:-------------------------:|:----------:|
| **Live Inbound Calls** | You manage | MyBCAT | MyBCAT | MyBCAT |
| **Text Messaging** | You manage | MyBCAT | MyBCAT | MyBCAT |
| **Appointment Requests** | You manage | MyBCAT | MyBCAT | MyBCAT |
| **AI Overflow/After-Hours** | Not included | MyBCAT | MyBCAT | MyBCAT |
| **Insurance Verification** | You manage | Not included | MyBCAT | MyBCAT |
| **Appointment Confirmations** | You manage | Not included | MyBCAT | MyBCAT |
| **Recalls & Reactivations** | You manage | Not included | MyBCAT | MyBCAT |
| **Waitlist Management** | You manage | Not included | MyBCAT | MyBCAT |
| **Real-Time Dashboard** | Not included | Not included | MyBCAT | MyBCAT |
| **Monthly Consulting** | Not included | Not included | Not included | Included (1x/month) |
| **Recruiting & Training** | Your cost | Included | Included | Included |
| **PTO & Turnover** | Your cost | Included | Included | Included |
| **Weekly Cost** | ${{HIRE_WEEKLY}} | **${{INBOUND_WEEKLY}}** | **${{RHC_WEEKLY}}** | **${{RHC_GROWTH_WEEKLY}}** |

</div>

---

# Your Options

<div style="display: flex; gap: 12px; margin-top: 18px; font-size: 0.56em;">

<div style="flex: 1; background: white; padding: 12px; border-radius: 10px; border-top: 4px solid #006064;">
<h2 style="margin-top: 0; font-size: 1.15em;">Inbound Answering</h2>
<p>90%+ answer rate + AI after-hours</p>
<p style="font-size: 1.4em; font-weight: 900; color: #D3AF5E;">${{INBOUND_WEEKLY}}/week</p>
<p style="font-size: 0.8em; color: #666;">Coverage based on your call volume</p>

<div style="font-size: 0.85em; margin-top: 4px;">
<strong>Includes:</strong>
<ul style="columns: 2; column-gap: 14px;">
  <li>Trained inbound specialists</li>
  <li>Text message handling</li>
  <li>Appointment requests</li>
  <li>AI after-hours &amp; overflow</li>
</ul>
</div>
</div>

<div style="flex: 1; background: white; padding: 12px; border-radius: 10px; border-top: 4px solid #D3AF5E;">
<h2 style="margin-top: 0; font-size: 1.15em;">Remote Hospitality Center</h2>
<p>Full-service phone operations</p>
<p style="font-size: 1.4em; font-weight: 900; color: #D3AF5E;">${{RHC_WEEKLY}}/week</p>
<p style="font-size: 0.8em; color: #666;">Full-service coverage for your practice</p>

<div style="font-size: 0.85em; margin-top: 4px;">
<strong>Includes everything above PLUS:</strong>
<ul style="columns: 2; column-gap: 14px;">
  <li>Insurance verification</li>
  <li>Recalls &amp; confirmations</li>
  <li>Waitlist management</li>
  <li>Real-time dashboard</li>
</ul>
</div>
</div>

<div style="flex: 1; background: white; padding: 12px; border-radius: 10px; border-top: 4px solid #27343C;">
<h2 style="margin-top: 0; font-size: 1.15em;">RHC+ Growth</h2>
<p>RHC + monthly growth consulting</p>
<p style="font-size: 1.4em; font-weight: 900; color: #D3AF5E;">${{RHC_GROWTH_WEEKLY}}/week</p>
<p style="font-size: 0.8em; color: #666;">Includes everything in RHC, plus growth support</p>

<div style="font-size: 0.85em; margin-top: 4px;">
<strong>Includes RHC PLUS:</strong>
<ul style="columns: 2; column-gap: 14px;">
  <li>Monthly consulting session (1x/month)</li>
  <li>Growth playbook + KPI review</li>
  <li>Outbound growth campaigns (recall/reactivation)</li>
  <li>Monthly optimization plan</li>
</ul>
</div>
</div>

</div>

<div style="text-align: center; margin-top: 2px; font-size: 0.65em;">
<strong>30-Day Pilot</strong> | No long-term contract | Cancel anytime (7 days notice) | Setup: $750
</div>

---

# Next Steps

<div style="font-size: 1.3em; margin-top: 40px;">

**Two questions:**

1. **Which option fits {{CLIENT_NAME}} better?**
   - Inbound Answering (${{INBOUND_WEEKLY}}/week)
   - Remote Hospitality Center (${{RHC_WEEKLY}}/week)
   - RHC+ Growth (${{RHC_GROWTH_WEEKLY}}/week)

2. **When would you like to start?**
   - Go-live in 4 weeks from today

</div>

<div style="margin-top: 50px; text-align: center;">

**Ankit Patel** | 615.779.3629 | ankit@mybcat.com

</div>

---

<!-- ═══════════════════════════════════════════════════════════════════════════
     EXTENDED DATA SECTION (Optional - for 30+ min presentations)
═══════════════════════════════════════════════════════════════════════════ -->

<!-- _class: section-divider -->
<!-- _backgroundColor: #006064 -->
<!-- _color: #ffffff -->

# EXTENDED ANALYSIS
## Detailed Data for the Curious
*Skip in short presentations*

---

# Data Source & Methodology

<div style="font-size: 0.85em;">

| Parameter | Value |
|-----------|-------|
| **Source System** | {{DATA_SOURCE}} |
| **Date Range** | {{DATE_RANGE}} |
| **Days Analyzed** | {{DAYS_ANALYZED}} days |
| **Total Records** | {{TOTAL_RECORDS}} |
| **Inbound Calls** | {{TOTAL_INBOUND}} ({{INBOUND_PCT}}% of total) |
| **Outbound Calls** | {{TOTAL_OUTBOUND}} ({{OUTBOUND_PCT}}% of total) |

</div>

<div style="margin-top: 8px; font-size: 0.7em;">
<strong>Disposition Classification:</strong><br>
{{DISPOSITION_METHOD}}
</div>

<div style="margin-top: 8px; font-size: 0.65em; color: #666;">
{{METHODOLOGY_CAVEAT}}
</div>

---

# Call Volume Analysis

<div style="font-size: 0.85em;">
<div style="font-weight: 900; margin: 0 0 6px 0;">Total Activity Breakdown</div>

| Metric | Count | % of Total |
|--------|-------|------------|
| Total Records | {{TOTAL_RECORDS}} | 100% |
| Inbound Calls | {{TOTAL_INBOUND}} | {{INBOUND_PCT}}% |
| Outbound Calls | {{TOTAL_OUTBOUND}} | {{OUTBOUND_PCT}}% |
| Answered (Inbound) | {{ANSWERED_COUNT}} | {{ANSWERED_PCT}}% |
| Missed (Inbound) | {{MISSED_COUNT}} | {{MISSED_PCT}}% |
</div>

---

# Call Volume Analysis (Daily Averages)

<div style="font-size: 0.85em;">
<div style="font-weight: 900; margin: 0 0 6px 0;">Daily Averages</div>

| Metric | Value |
|--------|-------|
| Avg Calls/Day | {{AVG_CALLS_DAY}} |
| Avg Inbound/Day | {{AVG_INBOUND_DAY}} |
| Avg Answered/Day | {{AVG_ANSWERED_DAY}} |
| Avg Missed/Day | {{MISSED_PER_DAY}} |
| Peak Day | {{PEAK_DAY}} |
</div>

---

# Hourly Call Distribution

![w:950](charts/hourly_volume.png)

---

# Daily Call Pattern

![w:950](charts/daily_pattern.png)

---

# FTE Coverage Analysis

<div style="display: flex; gap: 24px;">
<div style="flex: 1;">

![w:380](charts/fte_coverage.png)

</div>
<div style="flex: 1; font-size: 0.8em;">

**Your Staffing Requirement:**

| | Base | With Buffer (+{{SHRINKAGE_PCT}}%) |
|--|------|-----------------------------------|
| **To answer 90%+ of calls** | {{BASE_FTE}} | **{{SHRINKAGE_FTE}}** |

<div style="background: #E8F5E9; padding: 8px 12px; border-radius: 6px; margin-top: 6px; font-size: 0.85em;">
<strong>Bottom line:</strong><br>
Phones-only coverage: {{BASE_FTE}} agents.<br>
Full-service (RHC) or in-house staffing: {{SHRINKAGE_FTE}} FTE (includes shrinkage buffer).
</div>

</div>
</div>

---

# Concurrency Analysis

<div style="display: flex; gap: 40px;">
<div style="flex: 1;">

**How many calls ring at once?**

| Concurrent Calls | Frequency | % of Arrivals |
|-----------------|-----------|-----------|
| 1 (single line) | {{CONC_1_COUNT}} | **{{CONC_1_PCT}}%** |
| 2 (overlap) | {{CONC_2_COUNT}} | {{CONC_2_PCT}}% |
| 3 (busy) | {{CONC_3_COUNT}} | {{CONC_3_PCT}}% |
| 4+ (overwhelmed) | {{CONC_4PLUS_COUNT}} | {{CONC_4PLUS_PCT}}% |

</div>
<div style="flex: 1;">

**What this tells us:**

Over **{{CONC_1_PCT}}% of call arrivals** happen when only 1 line is ringing.

Yet you still miss {{MISS_RATE}}% of calls.

**This reinforces the process issue finding: dedicated phone coverage solves this.**

</div>
</div>

---

<!-- _class: section-divider -->
<!-- _backgroundColor: #006064 -->
<!-- _color: #ffffff -->

# APPENDIX
## Reference Material

---

# Full Model Assumptions (1/2)

<div style="font-size: 0.65em;">

| Assumption | Value | Rationale |
|------------|-------|-----------|
| Disposition method | {{DISPOSITION_METHOD}} | From phone export |
| Timezone | {{TIMEZONE_DESC}} | {{TIMEZONE_RATIONALE}} |
| Business hours | {{BUSINESS_HOURS_DESC}} | {{BUSINESS_HOURS_RATIONALE}} |
| Closure calendar | {{CLOSURES_DESC}} | {{CLOSURES_RATIONALE}} |
| Coverage target | 90%+ of calls answered | Industry benchmark |
| Shrinkage factor | {{SHRINKAGE_PCT}}% | Breaks, training, admin |

</div>

---

# Full Model Assumptions (2/2)

<div style="font-size: 0.65em;">

| Assumption | Value | Rationale |
|------------|-------|-----------|
| Appointment-seeking calls | {{APPT_SEEKING_PCT}}% of missed | Conservative estimate |
| New patient rate | {{NEW_PATIENT_PCT}}% of above | Industry benchmark |
| Conversion rate | {{CONVERSION_PCT}}% would book | High-intent callers |
| Appointment value | ${{AVG_APPT_VALUE}} | {{SPECIALTY}} average |
| In-house burden | +20% on base wage | Benefits, taxes, overhead |

</div>

---

# Data Integrity Notes

**What we analyzed:**
- Complete {{DAYS_ANALYZED}}-day {{DATA_SOURCE}} export
- All call records with timestamps
- Duration data for every call
- Direction (inbound/outbound) flagged

**What we could not determine:**
- Individual patient identification (not included in export)
- Repeat vs. new caller distinction
- Specific reason for each missed call
- Call content/purpose

**Confidence Level:** {{CONFIDENCE_LEVEL}}

---

<!-- _class: title -->

# Thank You

**{{CLIENT_NAME}}**
*{{CLIENT_TAGLINE}}*

---

**My Business Care Team**
Ankit Patel, Founder
615.779.3629 | ankit@mybcat.com

www.mybcat.com
