# Slide 18 (Paths Forward) v4.0 Reference

Source of truth: `phone_to_present/workflow/phase7_presentation.md` (section: “Slide 18: Paths Forward — Construction Guide (v4.0)”).

This is copied into the brain folder so Slide 18 requirements remain self-contained even when working only from `brains/phone_to_present/*`.

---

## Key Rules (v4.0)

- No markdown table: Slide 18 must use HTML `<table class="pf-table">` inside `<div class="pf-container">`.
- No separate title: the table fills the slide.
- Optional Pilot column is inserted between DIY and Inbound when Pilot is included.

## Required CSS (add to Marp `style:` block)

```css
/* Paths Forward Container - centers table on slide */
.pf-container {
  font-family: 'Inter', -apple-system, sans-serif;
  padding: 0;
  margin: 0 auto;
  display: table;
}

/* Icon base styles */
.pf-icon {
  width: 16px;
  height: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

/* Icon variants */
.pf-icon-check {
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
  color: #059669;
}
.pf-icon-warn {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  color: #d97706;
}
.pf-icon-x {
  background: #f1f5f9;
  color: #94a3b8;
}

/* Table base */
.pf-table {
  border-collapse: collapse;
  font-size: 0.38em;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* Header cells */
.pf-table th {
  padding: 8px 12px;
  text-align: center;
  font-weight: 700;
  border-bottom: 3px solid rgba(0,0,0,0.1);
  background: #1e293b;
  color: #f8fafc;
  white-space: nowrap;
}
.pf-table th:first-child {
  text-align: left;
  padding-left: 12px;
}

/* RHC column header - teal gradient */
.pf-table th.pf-rhc {
  background: linear-gradient(135deg, #0d9488, #0f766e);
}

/* Pilot column header */
.pf-table th.pf-pilot {
  background: #1e293b;
}

/* Data cells */
.pf-table td {
  padding: 6px 10px;
  text-align: center;
  border-bottom: 1px solid #e2e8f0;
  line-height: 1.35;
}
.pf-table td:first-child {
  text-align: left;
  padding-left: 14px;
  font-weight: 600;
  color: #1e293b;
}

/* RHC column cells - light teal tint */
.pf-table td.pf-rhc {
  background: rgba(13,148,136,0.06);
}

/* Zebra striping */
.pf-table tr:nth-child(even) td {
  background: #f8fafc;
}
.pf-table tr:nth-child(even) td.pf-rhc {
  background: rgba(13,148,136,0.10);
}

/* "MOST POPULAR" badge - gold/amber */
.pf-badge {
  display: inline-block;
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  color: #1e293b;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.65em;
  font-weight: 800;
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* SLA badges */
.pf-sla-badge {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 0.6em;
  font-weight: 700;
  margin-bottom: 3px;
}
.pf-sla-yellow {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  color: #92400e;
}
.pf-sla-green {
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
  color: #065f46;
}

/* Header text */
.pf-header-title {
  font-weight: 700;
  color: #f8fafc;
  font-size: 1em;
}
.pf-header-sub {
  font-size: 0.7em;
  color: rgba(255,255,255,0.7);
  font-weight: 400;
  margin-top: 2px;
}

/* Pricing rows */
.pf-price-row td {
  padding: 8px 10px !important;
  background: #f1f5f9 !important;
  border-top: 3px solid #cbd5e1;
}
.pf-price-row td.pf-rhc {
  background: rgba(13,148,136,0.12) !important;
}
.pf-price {
  font-weight: 800;
  font-size: 1.3em;
}
.pf-price-diy {
  color: #9ca3af;
  text-decoration: line-through;
}
.pf-price-rhc {
  color: #0d9488;
  font-size: 1.4em;
}

/* Savings display */
.pf-savings {
  color: #059669;
  font-weight: 700;
}
.pf-savings-badge {
  background: linear-gradient(135deg, #059669, #10b981);
  color: white;
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 800;
  box-shadow: 0 2px 4px rgba(5,150,105,0.3);
}
```

---

## SVG Icons (use these exact blocks)

**Checkmark (Green — “We handle it”)**
```html
<span class="pf-icon pf-icon-check">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" width="14" height="14">
    <polyline points="20 6 9 17 4 12"></polyline>
  </svg>
</span>
```

**Warning (Amber — “You manage”)**
```html
<span class="pf-icon pf-icon-warn">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="14" height="14">
    <circle cx="12" cy="12" r="10"></circle>
    <line x1="12" y1="8" x2="12" y2="12"></line>
    <line x1="12" y1="16" x2="12.01" y2="16"></line>
  </svg>
</span>
```

**X Mark (Gray — “Not included”)**
```html
<span class="pf-icon pf-icon-x">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" width="14" height="14">
    <line x1="18" y1="6" x2="6" y2="18"></line>
    <line x1="6" y1="6" x2="18" y2="18"></line>
  </svg>
</span>
```

---

## HTML Scaffold (standard 4-column)

```html
<div class="pf-container">
<table class="pf-table">
<thead>
<tr>
  <th>
    <div class="pf-header-title">Feature</div>
    <div class="pf-header-sub">What's included</div>
  </th>
  <th>
    <div class="pf-header-title" style="color:#94a3b8;">DIY Staffing</div>
    <div class="pf-header-sub" style="color:#64748b;">You handle it</div>
  </th>
  <th>
    <div class="pf-header-title">Inbound Answering</div>
    <div class="pf-header-sub">Basic coverage</div>
  </th>
  <th class="pf-rhc">
    <div class="pf-badge">★ Most Popular</div>
    <div class="pf-header-title">Remote Hospitality Center</div>
    <div class="pf-header-sub">Full patient ops</div>
  </th>
  <th>
    <div class="pf-header-title">RHC + Growth</div>
    <div class="pf-header-sub">Scale & consult</div>
  </th>
</tr>
</thead>
<tbody>
  <!-- Feature rows (see mapping below) -->
  <!-- Pricing rows -->
  <tr class="pf-price-row">
    <td><strong>Weekly Investment</strong></td>
    <td><span class="pf-price pf-price-diy">${{HIRE_WEEKLY}}</span>/wk</td>
    <td><span class="pf-price" style="color:#5a7a84;">${{INBOUND_WEEKLY}}</span>/wk</td>
    <td class="pf-rhc"><span class="pf-price pf-price-rhc">${{RHC_WEEKLY}}</span>/wk</td>
    <td><span class="pf-price" style="color:#5a7a84;">${{RHC_GROWTH_WEEKLY}}</span>/wk</td>
  </tr>
  <tr class="pf-price-row">
    <td><strong>vs. DIY Staffing</strong></td>
    <td style="color:#8a9a9e;">—</td>
    <td><span class="pf-savings">Save $&lt;HIRE_WEEKLY - INBOUND_WEEKLY&gt;/wk</span></td>
    <td class="pf-rhc"><span class="pf-savings-badge">Save $&lt;HIRE_WEEKLY - RHC_WEEKLY&gt;/wk</span></td>
    <td><span class="pf-savings">Save $&lt;HIRE_WEEKLY - RHC_GROWTH_WEEKLY&gt;/wk</span></td>
  </tr>
</tbody>
</table>
</div>
```

---

## Optional: Pilot column header (5-column variant)

From the v4.0 guide (“Adding Pilot Column (5-Column)”):

```html
<th class="pf-pilot">
  <div class="pf-sla-badge pf-sla-yellow">90% SLA</div>
  <div class="pf-header-title">Pilot Program</div>
  <div class="pf-header-sub">Base coverage</div>
</th>
```

Use this 5-column variant only when the Pilot Program is included; otherwise use the standard layout.

When Pilot is included:
- Add corresponding `<td>` cells after the DIY column in every row.
- Feature rows: Pilot mapping matches **Inbound Answering** (Pilot is inbound answering only).
- Pricing rows: show Pilot weekly (`PILOT_WEEKLY`) and Pilot savings vs DIY (`HIRE_WEEKLY - PILOT_WEEKLY`).

---

## Feature row mapping (standard set)

| Feature | DIY | Inbound | RHC | RHC+ |
|---------|-----|---------|-----|------|
| Live Inbound Calls | warn | check | check | check |
| Text Messaging | warn | check | check | check |
| Appointment Requests | warn | check | check | check |
| AI Overflow/After-Hours | x | check | check | check |
| Insurance Verification | warn | x | check | check |
| Appointment Confirmations | warn | x | check | check |
| Recalls & Reactivations | warn | x | check | check |
| Waitlist Management | warn | x | check | check |
| Real-Time Dashboard | x | x | check | check |
| Monthly Consulting | x | x | x | check |
| Recruiting & Training | warn | check | check | check |
| PTO & Turnover | warn | check | check | check |

Icon meanings:
- `check` = Green checkmark (MyBCAT handles)
- `warn` = Amber warning (You manage)
- `x` = Gray X (Not included)
