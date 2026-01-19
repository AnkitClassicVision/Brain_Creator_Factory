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
