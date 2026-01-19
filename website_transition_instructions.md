Below is a **full, end-to-end plan** to migrate a WordPress site to a **GitHub → Vercel** workflow **without nuking SEO**, and to use the migration as an excuse to **tighten local SEO strategy + structure + speed**.

I’m going to be blunt on the core principle:

**If you change URLs without a perfect redirect plan, you will lose rankings.**
So the plan is engineered to **protect existing equity first**, then improve structure.

---

## The big decisions you must lock before touching code

| Decision                    | Strong opinion                                                                        | Why it matters                                                                                     |
| --------------------------- | ------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| **URL policy**              | **Keep the same URLs whenever possible**                                              | It’s the easiest way to preserve rankings + backlinks. Redirects are a safety net, not a strategy. |
| **Editing workflow**        | If non-technical people need to edit, **don’t go “pure markdown” without a CMS plan** | Otherwise your site becomes “developer-only” and stops getting updated (which hurts SEO).          |
| **Content scope at launch** | Launch with **content parity** (same pages), then iterate                             | Big structural rewrites during migration = hard to debug ranking drops.                            |
| **Framework**               | If you’re on Vercel, **Next.js is the default safe choice**                           | Best support + routing + SEO primitives + Vercel integration.                                      |
| **Redirect system**         | Use **Vercel edge redirects** + bulk redirect files if needed                         | Vercel processes redirects at the edge and supports bulk imports. ([Vercel][1])                    |

---

## Migration plan (high-level overview)

| Phase                               | What you’re solving                       | Output you should end with                           | “Done when…”                                              |
| ----------------------------------- | ----------------------------------------- | ---------------------------------------------------- | --------------------------------------------------------- |
| 1. Keyword strategy validation      | Make sure you’re building the right pages | Keyword clusters + page map + priorities             | Every target keyword maps to a page (existing or planned) |
| 2. Current-state SEO + link mapping | Don’t lose existing equity                | Full URL inventory + backlinks + internal link graph | You can answer “what happens to every URL?”               |
| 3. Future-state architecture        | Improve structure without SEO chaos       | New sitemap + consolidation/removals + redirect map  | Redirect map is complete + reviewed                       |
| 4. Build in GitHub (new site)       | Rebuild site cleanly + fast               | Next.js repo + content system                        | Staging deploy matches planned structure                  |
| 5. Technical SEO implementation     | Preserve + improve SEO signals            | Metadata, canonicals, schema, sitemaps, robots       | SEO tests pass; no missing canonicals                     |
| 6. Performance + CWV                | Win on speed (and keep it)                | Perf budget + Lighthouse/PSI targets                 | Passing CWV targets is realistic                          |
| 7. QA + launch + monitoring         | No surprises                              | Cutover checklist + rollback plan                    | Everything crawls clean + tracking works                  |
| 8. Post-launch iteration            | Convert traffic into leads                | Internal linking upgrades + new pages                | Rankings stabilize and conversions rise                   |

---

# 1) Keyword research FIRST (local business validation)

This phase determines whether you **keep the current structure** or **re-architect**.

### 1.1 Build a “Keyword Universe”

You’re not just collecting keywords—you’re collecting **search intent**.

**Buckets that matter for local businesses:**

1. **Service + city** (high intent): `service + {city}`
2. **Service + “near me”** (mobile heavy): `service near me`
3. **Problem-based** (often easier wins): `fix {problem}`, `{symptom} treatment`
4. **Price/insurance** (conversion gold): `cost`, `accepts {insurance}`, `same day`
5. **Brand/comparison** (mid-funnel): `{service} vs {service}`, “best” queries
6. **Location modifiers**: neighborhoods, suburbs, “downtown”, “open now”

### 1.2 Competitor reality check (you want truth, not hope)

For your top services, search in an incognito window:

* Who owns the **local pack**?
* Who owns the **top 3 organic**?
* Do the winners have:

  * Dedicated service pages?
  * Location pages?
  * FAQ content?
  * Strong reviews / GBP?

### 1.3 Turn keywords into a **Page Map** (this is the deliverable that matters)

Here’s the structure you’re aiming for:

| Cluster           | Intent      | Best page type           | Keep/Build    | Notes                                     |
| ----------------- | ----------- | ------------------------ | ------------- | ----------------------------------------- |
| “service + city”  | High        | Service page             | Keep or build | Usually 1 strong page beats 5 thin ones   |
| “near me”         | High        | Homepage + location page | Keep          | Usually ranks via overall authority + GBP |
| “problem/symptom” | Medium-high | FAQ / guide page         | Build         | Great long-tail + internal link feeder    |
| “cost/insurance”  | High        | Pricing/insurance page   | Build         | Converts well; reduces phone friction     |
| “best {service}”  | Medium      | Comparison/guide         | Optional      | Only if you can genuinely compete         |

### 1.4 Scoring model (simple but effective)

Score each keyword cluster like this:

**Priority Score = (Intent × Local relevance × Volume) ÷ Difficulty**

* Intent: 1–5
* Local relevance: 1–5
* Difficulty: 1–5 (or use tool KD)
* Volume: tool volume (or relative scale)

**Outcome:** You’ll know which pages are worth building *before* migration.

---

# 2) Current structure + mapping for links in and out

This is where most migrations fail: people “rebuild the site” but don’t rebuild the **link ecosystem**.

### 2.1 Crawl + inventory everything

Use Screaming Frog or Sitebulb and export:

* All indexable URLs (pages/posts/categories/tags)
* Status codes
* Titles, meta descriptions
* H1s
* Canonicals
* Pagination
* Images + their URLs
* Internal links in/out counts

### 2.2 Pull **real authority signals**

From Google Search Console:

* Top pages by clicks/impressions
* Top queries per page
* External links report (top linked pages)

From Ahrefs/Semrush (if you have it):

* Backlinks by page
* Anchor text distribution
* Broken backlinks

### 2.3 Build “The Master URL Sheet” (non-negotiable)

Columns I recommend:

| Column                | Why it exists                            |
| --------------------- | ---------------------------------------- |
| Old URL               | Source of truth                          |
| Type                  | Page / post / archive / attachment / etc |
| Organic traffic (GSC) | Prioritize what matters                  |
| Backlinks count       | Risk scoring                             |
| Primary query         | What it currently ranks for              |
| New URL               | Destination                              |
| Action                | Keep / Redirect / Consolidate / Remove   |
| Redirect type         | 301 / 308 / 410                          |
| Notes                 | Intent match + why                       |

**Rule:** if a URL has traffic or backlinks, it gets a deliberate outcome.

---

# 3) Future state: new structure, consolidation, removals, and mapping old links

### 3.1 The safe approach (what I recommend)

* **Keep URL structure stable** for your money pages.
* Add new pages where keyword research proves demand.
* Consolidate thin pages into stronger “pillar” pages **only when intent matches**.

**Bad consolidation:** merging unrelated intents because “fewer pages = better”.
**Good consolidation:** combining 3 weak pages that target the same intent into 1 authoritative page.

### 3.2 Redirect mapping rules (that protect rankings)

1. **One-to-one redirect is best** (old → exact equivalent)
2. If consolidating, redirect old pages → **most relevant section** (not just the homepage)
3. Never redirect everything to the homepage (Google treats it like soft-404 spam)
4. For intentionally removed content with no replacement, consider **410** (advanced; use carefully)

### 3.3 Vercel redirect implementation (practical)

Vercel supports redirects and processes them at the edge. ([Vercel][1])
If you have a lot of redirects, you can use **bulk redirects via CSV/JSON/JSONL**. ([Vercel][2])
Vercel also has CLI/project-level ways to manage redirects (useful if you want faster updates without redeploys). ([Vercel][3])

---

# 4) Website structure changes: H1, schema, technical SEO mapping

## 4.1 H1 / heading rules (simple, but most sites screw this up)

* **One H1 per page**, describing the page’s core intent
* Use H2s for major sections, H3 for subsections
* Don’t stuff cities into every heading if it reads like spam—use it where it’s natural

## 4.2 Metadata rules

* Titles should match intent + location where relevant
* Meta descriptions should sell the click (not just repeat keywords)
* Canonical tag is mandatory (especially if you have parameters, faceted nav, etc.)

## 4.3 Schema (structured data) plan

For a local business, schema is easy wins if done cleanly:

**Site-wide:**

* `Organization` or `LocalBusiness`
* `WebSite` (with search action if applicable)
* `BreadcrumbList`

**Page-level:**

* Service pages: `Service`
* FAQs: `FAQPage` (only if FAQs are visible to users)
* Reviews: only if you follow guidelines (don’t fake “aggregateRating”)

---

# 5) Page speed + Core Web Vitals plan (don’t guess—engineer it)

Google’s current Core Web Vitals are:

* **LCP** (loading) target: **≤ 2.5s**
* **INP** (responsiveness) target: **≤ 200ms**
* **CLS** (visual stability) target: **≤ 0.1** ([web.dev][4])

INP replaced FID as a Core Web Vital (rolled into CWV in March 2024). ([Google for Developers][5])

## 5.1 Performance baseline (before migration)

Pull:

* PageSpeed Insights (mobile is the main pain)
* Lighthouse
* GSC CWV report (field data groups) ([Google Help][6])

## 5.2 Performance budget (so you don’t regress later)

Set budgets like:

* JS per page (initial): keep it aggressively low
* Image formats: AVIF/WebP where possible
* Fonts: 1 family, limited weights, preload only what’s needed
* Third-party scripts: minimal (these kill INP)

## 5.3 Implementation tactics that matter on Vercel/Next

* Use image optimization properly (don’t ship 4000px images to mobile)
* Avoid massive client-side hydration when you can render statically/server-side
* Delay or eliminate chat widgets / heatmaps until after main interaction
* Preload the hero image if it’s the LCP element
* Reserve space for images/embeds (CLS killer)

---

# 6) GitHub → Vercel deployment plan (clean workflow)

## 6.1 Repo and branching structure

* `main` = production
* `staging` = pre-prod QA
* feature branches = changes

Vercel’s GitHub integration automatically creates **Preview Deployments** for branches/PRs, which is exactly what you want for SEO QA. ([Vercel][7])

## 6.2 Environments

* Preview/staging: `noindex, nofollow` (or protected access)
* Production: indexable

## 6.3 Content management options (choose one)

### Option A (simple, dev-owned):

* Pages in Markdown/MDX in GitHub
* Changes via PRs

### Option B (best if staff edits content):

* Git-backed CMS (e.g., Decap CMS) editing Markdown in GitHub
  OR
* Headless CMS (not WordPress) feeding the site

**Hard truth:** if content needs frequent updates and your team won’t do PRs, go with a CMS or the site will stagnate.

---

# 7) QA checklist (this prevents “mystery ranking drops”)

## 7.1 SEO QA (pre-launch)

* Crawl staging site:

  * No broken internal links
  * Correct canonicals
  * Correct title/H1 presence
  * Schema validates
* Verify redirect rules:

  * Old → new = 301/308 correct
  * No redirect chains (A→B→C)
* XML sitemap exists and matches intended indexable pages
* Robots.txt correct for production vs staging
* Ensure old WP URLs that matter (uploads, PDFs) still resolve or redirect

## 7.2 Tracking QA

* GA4 events firing
* Conversion tracking (forms, calls, bookings)
* GSC verification ready for domain
* Call tracking numbers (if used) don’t break NAP consistency

---

# 8) Launch plan (minimal risk cutover)

1. Freeze WP content changes (so you don’t migrate a moving target)
2. Push final redirect rules
3. Swap DNS to Vercel
4. Validate:

   * homepage loads
   * top money pages load
   * top 20 legacy URLs redirect correctly
5. Submit sitemap in GSC
6. Monitor:

   * Crawl errors
   * Index coverage
   * CWV report groups
   * Rankings for priority pages

---

# 9) Post-launch: the stuff that actually grows traffic + leads

Once stable, you do the growth work:

* Build missing pages from keyword map (especially problem/FAQ long-tail)
* Strengthen internal linking:

  * Every service page should be linked from nav, homepage, and related FAQs
* Add local trust blocks:

  * service area
  * FAQs
  * testimonials (real)
  * directions/parking (local conversion booster)
* Keep improving CWV—especially INP (third-party scripts are usually the culprit)

---

## “Anything else” most people forget (but you shouldn’t)

### A) WordPress “ghost URLs”

WordPress creates a lot of junk URLs:

* tag archives
* author archives
* date archives
* attachment pages
* search pages

You should decide which get:

* **noindex**
* **redirect**
* **removed**

### B) Media URL preservation

If old image URLs are indexed or linked, you either:

* keep the same `/wp-content/uploads/...` paths in your new site, OR
* implement redirects (painful at scale)

### C) Accessibility + conversions

Local SEO isn’t just rankings—it’s lead conversion:

* fast click-to-call on mobile
* obvious CTA above the fold
* form friction removal (short forms win)
* accessibility basics (also reduces legal risk)

---

## What I need from you (but I’ll still be useful without it)

If you share:

* your current domain
* your city/region
* what the business actually is (one-liner)
* what pages currently drive leads

…then this plan becomes a **site-specific migration spec** (keyword clusters + proposed sitemap + redirect priorities).

But even without that, the process above is the exact playbook to do this **without SEO damage**.

If you want, I can also give you a **copy-paste spreadsheet template** (URL inventory + redirect map + keyword-to-page map) in the exact column format to use with Screaming Frog + GSC exports.

[1]: https://vercel.com/docs/redirects?utm_source=chatgpt.com "Redirects"
[2]: https://vercel.com/docs/redirects/bulk-redirects/getting-started?utm_source=chatgpt.com "Getting Started"
[3]: https://vercel.com/docs/cli/redirects?utm_source=chatgpt.com "vercel redirects"
[4]: https://web.dev/articles/vitals?utm_source=chatgpt.com "Web Vitals | Articles"
[5]: https://developers.google.com/search/blog/2023/05/introducing-inp?utm_source=chatgpt.com "Introducing INP to Core Web Vitals"
[6]: https://support.google.com/webmasters/answer/9205520?hl=en&utm_source=chatgpt.com "Core Web Vitals report - Search Console Help"
[7]: https://vercel.com/docs/git/vercel-for-github?utm_source=chatgpt.com "Deploying GitHub Projects with Vercel"

---

# 10) LLM Enforcement Logic (CRITICAL FOR BRAIN GENERATION)

When generating a "brain" from these instructions, the following enforcement patterns **MUST** be included to prevent common LLM failure modes.

## 10.1 The 7 LLM Blind Spots (Why Agents Fail)

LLMs have predictable failure patterns when executing workflows. Understanding these prevents costly mistakes:

| # | Blind Spot | What Happens | Prevention Pattern |
|---|------------|--------------|-------------------|
| 1 | **Helpfulness Bias** | LLM improvises when required files are missing instead of stopping | Explicit STOP rules |
| 2 | **Format Blindness** | LLM simplifies required structures (e.g., uses markdown instead of HTML) | Format verification gates |
| 3 | **Partial Completion** | LLM treats "mostly done" as "done" (empty cells, missing rows) | Completeness validation |
| 4 | **Business Rule Ignorance** | LLM follows formulas but ignores minimums/maximums | Config constants with hard limits |
| 5 | **Implicit Assumptions** | LLM accepts unusual values without flagging | Sanity check gates |
| 6 | **Output Trust** | LLM assumes successful command = valid output | Output verification steps |
| 7 | **Equal Treatment** | LLM treats all items equally, missing critical items | Critical item marking |

---

## 10.2 STOP Rules (When to Halt and Ask User)

**Brain must include explicit STOP conditions.** Without these, LLMs will improvise solutions rather than ask for help.

### Required STOP Rules for Website Migration:

```yaml
stop_rules:
  # Data collection failures
  - condition: "GSC data export returns empty or fails"
    action: "STOP and ask user - DO NOT proceed without real traffic data"
    reason: "Redirect priorities require actual traffic data"

  - condition: "Crawl returns < 10 indexable URLs"
    action: "STOP and ask user - verify crawl configuration"
    reason: "Suspiciously small site may indicate crawl failure"

  # Completeness failures
  - condition: "Master URL sheet has any row missing 'action' column"
    action: "STOP and ask user - every URL must have explicit outcome"
    reason: "Incomplete mappings cause accidental 404s"

  - condition: "Redirect map has destination URL that doesn't exist"
    action: "STOP and ask user - verify destination pages exist"
    reason: "Redirecting to 404 wastes link equity"

  # Validation failures
  - condition: "CWV baseline shows LCP > 10s or INP > 1000ms"
    action: "STOP and ask user - verify test configuration"
    reason: "Extreme values suggest measurement error"

  - condition: "Schema validation returns errors"
    action: "STOP and fix schema - DO NOT proceed with invalid markup"
    reason: "Invalid schema can harm SERP appearance"

  # QA failures
  - condition: "Redirect test shows > 10% failure rate"
    action: "STOP and fix redirects - DO NOT proceed to launch"
    reason: "High failure rate will cause ranking drops"

  - condition: "Staging crawl finds > 5 broken internal links"
    action: "STOP and fix links - DO NOT proceed to launch"
    reason: "Broken links hurt UX and crawlability"
```

---

## 10.3 DO NOT Rules (Forbidden Actions)

**Brain must include explicit prohibitions.** LLMs need to know what's off-limits, not just what to do.

### Required DO NOT Rules:

```yaml
must_not:
  # NEVER IMPROVISE
  - "Generate redirect mappings from scratch when data is missing - ALWAYS stop and ask"
  - "Guess or assume traffic/backlink values - ALWAYS use real data"
  - "Proceed with incomplete Master URL Sheet - EVERY row must be complete"
  - "Mark a phase complete if validation fails - FIX first"

  # REDIRECT RULES
  - "Redirect everything to homepage (soft-404 spam pattern)"
  - "Create redirect chains (A→B→C) - always redirect to final destination"
  - "Use 302 for permanent moves - use 301 or 308"
  - "Skip redirect testing for any URL with traffic > 100/month"

  # OUTPUT RULES
  - "Trust command exit code without verifying output files exist"
  - "Assume generated files are valid without checking size > 0"
  - "Deliver any file with unreplaced {{PLACEHOLDER}} tokens"

  # LAUNCH RULES
  - "Launch without freezing WP content changes first"
  - "Skip any QA step - ALL QA is mandatory"
  - "Launch without rollback plan documented"
```

---

## 10.4 Pre-Flight Checks (Phase 0)

**Brain must include a pre-flight phase before work begins.** This catches missing requirements early.

### Required Pre-Flight Checks:

```yaml
preflight_checks:
  # Configuration
  - name: "config_loaded"
    check: "config/migration_constants.yaml exists and is valid"
    on_fail: "Create with defaults or STOP"

  # Tool availability
  - name: "gsc_accessible"
    check: "GSC API access OR existing GSC export file"
    on_fail: "STOP - cannot proceed without traffic data"

  - name: "crawl_capability"
    check: "Screaming Frog OR web_fetch skill available"
    on_fail: "STOP - cannot proceed without crawl capability"

  # Data inventory
  - name: "data_sources_checked"
    check: "Inventory existing crawl/GSC/backlink/keyword files"
    output: "List of available data with row counts"
```

---

## 10.5 Validation Gates (Quality Checkpoints)

**Brain must include explicit validation gates between phases.** Each gate has pass/fail criteria and retry logic.

### Required Validation Gates:

| Gate | Location | Pass Criteria | On Fail |
|------|----------|---------------|---------|
| `keyword_validation_gate` | After Phase 1 | Keywords mapped, ≥4 intent buckets covered | Retry keyword build |
| `mapping_validation_gate` | After Phase 2 | All URLs with traffic/backlinks have action | Retry mapping |
| `redirect_validation_gate` | After Phase 3 | All destinations exist, no chains | Retry redirect map |
| `build_validation_gate` | After Phase 4 | Staging deployed, accessible, noindexed | Retry build |
| `techseo_validation_gate` | After Phase 5 | H1/meta/schema valid | Retry tech SEO |
| `cwv_validation_gate` | After Phase 6 | LCP ≤2.5s, INP ≤200ms, CLS ≤0.1 | Retry optimizations |
| `qa_validation_gate` | After Phase 7 | All QA checks pass | Retry QA |
| `launch_validation_gate` | After Phase 8 | DNS propagated, site live, redirects working | Handle failure |

### Gate Implementation Pattern:

```yaml
- id: "mapping_validation_gate"
  type: "gate"
  stage: "mapping"
  purpose: "Verify all URLs have deliberate outcomes"

  gate_config:
    criteria:
      - name: "all_urls_have_action"
        check: "master_sheet.filter(row => !row.action).length == 0"
        weight: 1.0
      - name: "traffic_urls_mapped"
        check: "state.data.unmapped_traffic_urls == 0"
        weight: 1.0
      - name: "backlink_urls_mapped"
        check: "state.data.unmapped_backlink_urls == 0"
        weight: 1.0
    threshold: 1.0
    on_pass: "next_phase"
    on_fail: "retry_mapping"
    max_retries: 2
```

---

## 10.6 Business Constants (Hard Limits)

**Brain must include configuration constants for business rules.** LLMs follow formulas but ignore unstated limits.

### Required Constants:

```yaml
config:
  thresholds:
    # Minimum acceptable values
    MIN_INDEXABLE_URLS: 10              # Below = likely crawl failure
    MIN_GSC_DATA_ROWS: 1                # Must have some traffic data

    # Maximum acceptable values
    MAX_REDIRECT_FAILURE_RATE: 0.10     # 10% max failures
    MAX_BROKEN_LINKS: 5                 # Stop if more than 5
    MAX_REDIRECT_CHAIN_LENGTH: 1        # No chains (A→B only)
    MAX_HOMEPAGE_REDIRECTS_PCT: 5       # Avoid soft-404 spam

    # CWV targets (business requirements, not suggestions)
    LCP_TARGET_SECONDS: 2.5
    INP_TARGET_MS: 200
    CLS_TARGET: 0.1

    # CWV sanity checks (above = measurement error)
    LCP_SANITY_MAX: 10.0
    INP_SANITY_MAX: 1000

    # Critical item thresholds
    HIGH_TRAFFIC_MONTHLY: 100           # URLs above need individual testing
    HIGH_BACKLINKS: 10                  # URLs above are critical
```

---

## 10.7 Critical Item Marking

**Brain must mark critical items for extra validation.** LLMs treat all items equally without explicit prioritization.

### Critical Items for Website Migration:

```yaml
critical_items:
  urls:
    - "homepage"
    - "service pages (top 5 by traffic)"
    - "location pages"
    - "contact page"
    - "any page with > 10 backlinks"
    - "any page with > 100 monthly traffic"

  validation_requirements:
    - "individual redirect test (not just sample)"
    - "visual verification"
    - "schema validation"
    - "CWV measurement"
    - "manual smoke test"
```

---

## 10.8 Output Verification (Trust but Verify)

**Brain must verify outputs, not just command success.** LLMs trust exit codes without checking file validity.

### Required Output Checks:

```yaml
output_verification:
  # File existence AND validity
  - file: "redirect_map.json"
    checks:
      - "file exists"
      - "file size > 0"
      - "valid JSON syntax"
      - "all required fields present"
      - "all destinations return 200"

  - file: "sitemap.xml"
    checks:
      - "file exists"
      - "valid XML syntax"
      - "URL count matches expected"
      - "no URLs return 404"

  - file: "master_url_sheet.csv"
    checks:
      - "file exists"
      - "all required columns present"
      - "no empty cells in required columns"
      - "action column has valid values only"
```

---

## 10.9 State Tracking (Audit Trail)

**Brain must track validation state for debugging.** This enables post-mortem analysis of failures.

### Required State Fields:

```yaml
state:
  validation:
    # File checks
    files_verified:
      master_url_sheet: false
      redirect_map: false
      sitemap: false

    # Completeness checks
    completeness:
      master_url_sheet_complete: false
      redirect_map_complete: false

    # Critical item checks
    critical_items_verified:
      homepage_redirect_tested: false
      top_traffic_urls_tested: false
      high_backlink_urls_tested: false

    # Sanity checks
    sanity_checks:
      url_count_reasonable: false
      gsc_data_present: false
      cwv_values_reasonable: false

    # Stop condition history
    stop_conditions_triggered: []
    # Format: {condition, timestamp, user_response, resolution}
```

---

## 10.10 Summary: The 5 Golden Rules for LLM Workflows

When generating a brain from these instructions, ensure these rules are enforced:

1. **NEVER improvise when requirements are missing** - Always STOP and ask
2. **ALWAYS validate outputs exist AND are valid** - Don't trust exit codes
3. **ALWAYS apply business minimums/maximums** - Config constants are hard limits
4. **ALWAYS mark critical items for extra attention** - Not all URLs are equal
5. **ALWAYS track validation state** - Enable debugging of failures

---

## 10.11 Brain Generation Checklist

When creating a brain from these instructions, verify it includes:

- [ ] Pre-flight phase (Phase 0) with tool/data checks
- [ ] STOP rules for all critical failure conditions
- [ ] DO NOT rules for forbidden actions
- [ ] Validation gates between every phase
- [ ] Config file with business constants
- [ ] Critical item marking with extra validation
- [ ] Output verification (not just command success)
- [ ] State tracking for audit trail
- [ ] Three terminal nodes (SUCCESS, FAILURE, ESCALATE)
- [ ] Retry logic with max_retries limits
