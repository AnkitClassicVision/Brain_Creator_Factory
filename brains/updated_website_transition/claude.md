# Website Transition Brain - Orchestrator

## TRIGGER
Say **"start"** to begin the WordPress to Vercel migration workflow.

---

## Architecture

```
claude.md (YOU ARE HERE)
    │
    ├── brain.yaml ──────────── Rules, constraints, STOP conditions
    │
    ├── graph.yaml ──────────── Execution flow, nodes, gates
    │
    ├── state.yaml ──────────── Runtime tracking (update as you go)
    │
    └── config/
        └── migration_constants.yaml ── Business thresholds
```

**Your job**: Follow the graph, respect the rules, update state, STOP when required.

---

## Execution Model

| Principle | What It Means |
|-----------|---------------|
| **You write code** | For crawls, data processing, validation - write Python scripts |
| **You run code** | Execute scripts to get deterministic results |
| **You verify results** | Check outputs exist, have content, match expectations |
| **You update state** | Mark progress in state.yaml after each step |
| **You STOP when told** | If a stop_rule triggers, HALT and ask the user |

---

## Phase Overview

| # | Phase | Purpose | Gate Requirement |
|---|-------|---------|------------------|
| 0 | Pre-flight | Verify tools & data available | GSC + crawl capability confirmed |
| 1 | Keyword Strategy | Build keyword universe & page map | >= 4 keyword clusters mapped |
| 2 | Current State Mapping | Crawl + inventory all URLs | All URLs have assigned action |
| 3 | Future Architecture | Create redirect map | No chains, < 5% homepage redirects |
| 4 | GitHub Build | Set up repo + staging | Staging deployed + noindexed |
| 5 | Technical SEO | H1, schema, sitemap, robots | Schema validates, sitemap exists |
| 6 | Performance | Meet CWV targets | LCP <= 2.5s, INP <= 200ms, CLS <= 0.1 |
| 7 | QA | Full QA checklist | All checks pass |
| 8 | Launch | DNS cutover | Site live, redirects working |
| 9 | Post-launch | Monitor for 7 days | No critical errors |

---

## STOP Rules (CRITICAL - Must Obey)

**When these conditions occur, HALT and ask the user:**

| Condition | Action |
|-----------|--------|
| GSC data empty or unavailable | STOP - cannot proceed without traffic data |
| Crawl returns < 10 URLs | STOP - likely crawl failure |
| Any URL missing action in Master Sheet | STOP - complete the sheet |
| Redirect destination doesn't exist | STOP - verify destinations |
| > 5% redirects point to homepage | STOP - likely soft-404 spam |
| Redirect failure rate > 10% | STOP - fix before launch |
| > 5 broken internal links | STOP - fix before launch |
| Schema validation errors | STOP - fix before proceeding |
| CWV values extreme (LCP > 10s) | STOP - measurement error |

**Reference**: Full stop rules in `brain.yaml > constraints.stop_rules`

---

## DO NOT Rules (CRITICAL - Never Do These)

- **NEVER** generate redirect mappings when data is missing
- **NEVER** redirect everything to homepage
- **NEVER** create redirect chains (A->B->C)
- **NEVER** use 302 for permanent moves
- **NEVER** skip QA steps
- **NEVER** launch without rollback plan
- **NEVER** trust exit codes without verifying output files

**Reference**: Full prohibitions in `brain.yaml > constraints.must_not`

---

## Checkpoints (State Updates)

After completing each phase gate, update `state.yaml`:

```yaml
# Example after Phase 1
phase1_keywords:
  started: true
  completed: true
  keyword_universe_built: true
  page_map_created: true
  gate_passed: true
```

**Rule**: Never mark `gate_passed: true` if validation failed.

---

## Code Execution Pattern

When you need to process data, crawl, or validate:

1. **Write** a Python script to `scripts/`
2. **Execute** the script with Bash
3. **Verify** output file exists and has size > 0
4. **Parse** results and update state

```python
# Example: scripts/validate_redirects.py
import json

def validate_redirects(redirect_map_path):
    with open(redirect_map_path) as f:
        redirects = json.load(f)

    chains = []
    homepage_count = 0

    for r in redirects:
        if r['destination'] == '/':
            homepage_count += 1
        # Check for chains...

    return {
        'total': len(redirects),
        'chains': chains,
        'homepage_pct': homepage_count / len(redirects) * 100
    }
```

---

## File Outputs

| Phase | Output | Location | Validation |
|-------|--------|----------|------------|
| 1 | Keyword universe | `keyword_universe.yaml` | YAML valid, >= 4 clusters |
| 1 | Page map | `page_map.csv` | CSV valid, all columns present |
| 2 | Master URL sheet | `master_url_sheet.csv` | No empty action column |
| 3 | Redirect map | `redirect_map.json` | JSON valid, no chains |
| 5 | Sitemap | `sitemap.xml` | XML valid, URLs return 200 |
| 8 | Rollback plan | `rollback_plan.md` | Not empty, has steps |

---

## Skills Available

Use these skills when needed:

| Skill | Purpose |
|-------|---------|
| `google-search-console` | Pull GSC traffic data |
| `ahrefs` | Pull backlink data |
| `dataforseo` | SERP/keyword research |
| `web_fetch` | Crawl URLs |
| `vercel` | Deploy to Vercel |
| `github-operations-manager` | Git/GitHub operations |
| `visual-verification` | Screenshot verification |

---

## Quick Reference: Phase 0 Pre-flight

Before starting, verify:

1. **GSC accessible?** (API or export file)
2. **Crawl tool available?** (Screaming Frog, web_fetch, etc.)
3. **Config loaded?** (`config/migration_constants.yaml`)

If any are missing, **STOP** and ask user.

---

## Quick Reference: Phase 2 Master URL Sheet

Required columns:

| Column | Description |
|--------|-------------|
| old_url | Current URL |
| type | page/post/archive/attachment |
| traffic | Monthly clicks from GSC |
| backlinks | Count from Ahrefs |
| primary_query | Top ranking query |
| new_url | Destination (if redirecting) |
| action | Keep/Redirect/Consolidate/Remove |
| redirect_type | 301/308/410 |
| notes | Explanation |

**Rule**: EVERY row must have an action. No exceptions.

---

## Quick Reference: Phase 3 Redirect Rules

1. **One-to-one is best** (old -> exact equivalent)
2. **No chains** (A->B only, never A->B->C)
3. **Use 301 or 308** for permanent moves
4. **Never > 5% to homepage** (soft-404 pattern)
5. **Test all high-traffic URLs** (> 100/month) individually

---

## Quick Reference: Phase 6 CWV Targets

| Metric | Target | Sanity Max |
|--------|--------|------------|
| LCP | <= 2.5s | 10s |
| INP | <= 200ms | 1000ms |
| CLS | <= 0.1 | - |

**Note**: INP replaced FID as Core Web Vital in March 2024.

---

## Quick Reference: Phase 7 QA Mandatory Checks

All of these MUST pass before launch:

- [ ] Staging crawl - no broken internal links
- [ ] All pages have canonical tags
- [ ] All pages have title and H1
- [ ] Schema validates (Rich Results Test)
- [ ] Sitemap URLs all return 200
- [ ] Robots.txt correct
- [ ] All redirects return 301/308
- [ ] No redirect chains
- [ ] GA4 tracking fires
- [ ] Conversion tracking works
- [ ] Top 20 redirects tested manually

---

## Quick Reference: Phase 8 Launch Sequence

1. **Freeze** WordPress content changes
2. **Document** rollback plan
3. **Push** final redirect rules
4. **Change** DNS to Vercel
5. **Validate** homepage loads
6. **Validate** money pages load
7. **Test** top 20 legacy redirects
8. **Submit** sitemap to GSC

---

## Error Recovery

If a gate fails:

1. Check `state.yaml` for specific failure reasons
2. Fix the issues identified
3. Re-run the phase
4. Gate will re-evaluate

**Max retries**: 3 per phase (then escalate to user)

---

## Terminal States

| State | When | What Happens |
|-------|------|--------------|
| `success` | All phases complete | Migration done |
| `failure` | Max retries exceeded | Escalate to user |
| `escalate` | Human needed | Present issue to user |
| `preflight_blocked` | Missing requirements | Cannot start |

---

## Remember

1. **Read `brain.yaml`** for full constraint details
2. **Update `state.yaml`** after every significant action
3. **STOP and ask** when stop_rules trigger
4. **Verify outputs** - don't trust exit codes
5. **Test redirects** - especially high-traffic URLs
6. **Document everything** - for debugging failures

---

## Start

Say **"start"** and I will begin with Phase 0: Pre-flight validation.
