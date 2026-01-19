# Website Transition Codex Brain - Flow Diagram

## Overview
WordPress to Vercel/Next.js migration with SEO protection. 9 phases, 12 nodes (compact architecture).

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        WEBSITE TRANSITION CODEX BRAIN                           │
│                     WordPress → Vercel Migration Pipeline                       │
│                         (Compact Phase-Based Design)                            │
└─────────────────────────────────────────────────────────────────────────────────┘

                                    ┌─────────────┐
                                    │   INTAKE    │
                                    │   (prime)   │
                                    │             │
                                    │ • Domain    │
                                    │ • Business  │
                                    │ • CMS needs │
                                    └──────┬──────┘
                                           │
                                           ▼
    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │  ┌────────────────────────────────────────────────────────────────────────┐  │
    │  │                    PHASE 1: KEYWORD RESEARCH                           │  │
    │  │                         (single flow node)                             │  │
    │  │                                                                        │  │
    │  │    ┌─────────────────────────────────────────────────────────────┐     │  │
    │  │    │  • Build keyword universe (6 intent buckets)                │     │  │
    │  │    │  • Competitor SERP analysis                                 │     │  │
    │  │    │  • Cluster by intent                                        │     │  │
    │  │    │  • Create keyword → page map                                │     │  │
    │  │    │  • Priority scoring                                         │     │  │
    │  │    └─────────────────────────────────────────────────────────────┘     │  │
    │  │                                                                        │  │
    │  │    OUTPUTS: keyword_universe_path, keyword_page_map_path               │  │
    │  └────────────────────────────────────────────────────────────────────────┘  │
    │                                      │                                       │
    │                    ┌─────────────────┴──────────────────┐                    │
    │                    │           retry on fail            │                    │
    │                    ▼                                    │                    │
    │  ┌────────────────────────────────────────────────────────────────────────┐  │
    │  │                    PHASE 2: URL MAPPING                                │  │
    │  │                         (single flow node)                             │  │
    │  │                                                                        │  │
    │  │    ┌─────────────────────────────────────────────────────────────┐     │  │
    │  │    │  • Full site crawl (Screaming Frog)                         │     │  │
    │  │    │  • GSC data export (pages, queries, backlinks)              │     │  │
    │  │    │  • Ahrefs/Semrush backlink data                             │     │  │
    │  │    │  • Classify: keep/redirect/merge/noindex/remove             │     │  │
    │  │    │  • WordPress ghost URL policy                               │     │  │
    │  │    │  • Master URL sheet generation                              │     │  │
    │  │    └─────────────────────────────────────────────────────────────┘     │  │
    │  │                                                                        │  │
    │  │    OUTPUTS: master_url_sheet_path, url_inventory_path                  │  │
    │  └────────────────────────────────────────────────────────────────────────┘  │
    │                                      │                                       │
    │                    ┌─────────────────┴──────────────────┐                    │
    │                    │           retry on fail            │                    │
    │                    ▼                                    │                    │
    │  ┌────────────────────────────────────────────────────────────────────────┐  │
    │  │                 PHASE 3: FUTURE STATE ARCHITECTURE                     │  │
    │  │                         (single flow node)                             │  │
    │  │                                                                        │  │
    │  │    ┌─────────────────────────────────────────────────────────────┐     │  │
    │  │    │  • Design URL structure (stable money pages)                │     │  │
    │  │    │  • Consolidation planning (same-intent only)                │     │  │
    │  │    │  • 1:1 redirect mapping (no homepage-everything)            │     │  │
    │  │    │  • Vercel edge redirect config                              │     │  │
    │  │    │  • Ghost URL handling plan                                  │     │  │
    │  │    └─────────────────────────────────────────────────────────────┘     │  │
    │  │                                                                        │  │
    │  │    OUTPUTS: redirect_map_path, url_structure_doc_path                  │  │
    │  └────────────────────────────────────────────────────────────────────────┘  │
    │                                      │                                       │
    │                    ┌─────────────────┴──────────────────┐                    │
    │                    │           retry on fail            │                    │
    │                    ▼                                    │                    │
    │  ┌────────────────────────────────────────────────────────────────────────┐  │
    │  │                         PHASE 4: BUILD                                 │  │
    │  │                         (single flow node)                             │  │
    │  │                                                                        │  │
    │  │    ┌─────────────────────────────────────────────────────────────┐     │  │
    │  │    │  • Create Next.js repo                                      │     │  │
    │  │    │  • CMS decision (markdown/Decap/headless)                   │     │  │
    │  │    │  • Environment setup (preview noindex, prod index)          │     │  │
    │  │    │  • Content migration                                        │     │  │
    │  │    │  • Staging deployment                                       │     │  │
    │  │    └─────────────────────────────────────────────────────────────┘     │  │
    │  │                                                                        │  │
    │  │    OUTPUTS: repo_url, staging_url, cms_config_path                     │  │
    │  └────────────────────────────────────────────────────────────────────────┘  │
    │                                      │                                       │
    │                    ┌─────────────────┴──────────────────┐                    │
    │                    │           retry on fail            │                    │
    │                    ▼                                    │                    │
    │  ┌────────────────────────────────────────────────────────────────────────┐  │
    │  │                    PHASE 5: TECHNICAL SEO                              │  │
    │  │                         (single flow node)                             │  │
    │  │                                                                        │  │
    │  │    ┌─────────────────────────────────────────────────────────────┐     │  │
    │  │    │  • H1 audit (one per page, matches intent)                  │     │  │
    │  │    │  • Title/meta audit                                         │     │  │
    │  │    │  • Canonical implementation                                 │     │  │
    │  │    │  • Schema markup:                                           │     │  │
    │  │    │    - LocalBusiness (sitewide)                               │     │  │
    │  │    │    - WebSite + SearchAction                                 │     │  │
    │  │    │    - BreadcrumbList                                         │     │  │
    │  │    │    - Service                                                │     │  │
    │  │    │    - FAQPage                                                │     │  │
    │  │    │  • Schema validation                                        │     │  │
    │  │    └─────────────────────────────────────────────────────────────┘     │  │
    │  │                                                                        │  │
    │  │    OUTPUTS: techseo_audit_path                                         │  │
    │  └────────────────────────────────────────────────────────────────────────┘  │
    │                                      │                                       │
    │                    ┌─────────────────┴──────────────────┐                    │
    │                    │           retry on fail            │                    │
    │                    ▼                                    │                    │
    │  ┌────────────────────────────────────────────────────────────────────────┐  │
    │  │                    PHASE 6: PERFORMANCE / CWV                          │  │
    │  │                         (single flow node)                             │  │
    │  │                                                                        │  │
    │  │    ┌─────────────────────────────────────────────────────────────┐     │  │
    │  │    │  TARGETS:                                                   │     │  │
    │  │    │  ┌─────────────────────────────────────────────────────┐    │     │  │
    │  │    │  │  LCP  ≤ 2.5 seconds                                 │    │     │  │
    │  │    │  │  INP  ≤ 200 milliseconds                            │    │     │  │
    │  │    │  │  CLS  ≤ 0.1                                         │    │     │  │
    │  │    │  └─────────────────────────────────────────────────────┘    │     │  │
    │  │    │                                                             │     │  │
    │  │    │  • Baseline measurement (old site)                          │     │  │
    │  │    │  • Performance budget definition                            │     │  │
    │  │    │  • Optimizations:                                           │     │  │
    │  │    │    - Image optimization (AVIF/WebP)                         │     │  │
    │  │    │    - Font optimization (1 family)                           │     │  │
    │  │    │    - JS bundle optimization                                 │     │  │
    │  │    │    - Third-party script audit                               │     │  │
    │  │    │  • Staging Lighthouse test                                  │     │  │
    │  │    └─────────────────────────────────────────────────────────────┘     │  │
    │  │                                                                        │  │
    │  │    OUTPUTS: cwv_report_path, performance_budget_path                   │  │
    │  └────────────────────────────────────────────────────────────────────────┘  │
    │                                      │                                       │
    │                    ┌─────────────────┴──────────────────┐                    │
    │                    │      retry if CWV targets fail     │                    │
    │                    ▼                                    │                    │
    │  ┌────────────────────────────────────────────────────────────────────────┐  │
    │  │                           PHASE 7: QA                                  │  │
    │  │                         (single flow node)                             │  │
    │  │                                                                        │  │
    │  │    ┌─────────────────────────────────────────────────────────────┐     │  │
    │  │    │  • SEO crawl (staging)                                      │     │  │
    │  │    │    - No broken internal links                               │     │  │
    │  │    │    - Correct canonicals                                     │     │  │
    │  │    │    - No redirect chains                                     │     │  │
    │  │    │    - Sitemap matches indexable pages                        │     │  │
    │  │    │  • Redirect testing (top legacy URLs)                       │     │  │
    │  │    │  • Robots.txt verification                                  │     │  │
    │  │    │  • Tracking verification (GA4, GSC)                         │     │  │
    │  │    └─────────────────────────────────────────────────────────────┘     │  │
    │  │                                                                        │  │
    │  │    OUTPUTS: qa_report_path                                             │  │
    │  └────────────────────────────────────────────────────────────────────────┘  │
    │                                      │                                       │
    │                    ┌─────────────────┴──────────────────┐                    │
    │                    │           retry on fail            │                    │
    │                    ▼                                    │                    │
    │  ┌────────────────────────────────────────────────────────────────────────┐  │
    │  │                         PHASE 8: LAUNCH                                │  │
    │  │                         (single flow node)                             │  │
    │  │                                                                        │  │
    │  │    ┌─────────────────────────────────────────────────────────────┐     │  │
    │  │    │  PRE-LAUNCH:                                                │     │  │
    │  │    │  • Freeze WordPress content                                 │     │  │
    │  │    │  • Final redirect verification                              │     │  │
    │  │    │  • Rollback plan ready                                      │     │  │
    │  │    │                                                             │     │  │
    │  │    │  LAUNCH:                                                    │     │  │
    │  │    │  • DNS swap                                                 │     │  │
    │  │    │  • Validation (site live, redirects working)                │     │  │
    │  │    │  • Submit sitemap to GSC                                    │     │  │
    │  │    │  • Configure monitoring                                     │     │  │
    │  │    └─────────────────────────────────────────────────────────────┘     │  │
    │  │                                                                        │  │
    │  │    OUTPUTS: launch_manifest_path, rollback_plan_path                   │  │
    │  └────────────────────────────────────────────────────────────────────────┘  │
    │                                      │                                       │
    │                    ┌─────────────────┴──────────────────┐                    │
    │                    │           retry on fail            │                    │
    │                    ▼                                    │                    │
    │  ┌────────────────────────────────────────────────────────────────────────┐  │
    │  │                      PHASE 9: POST-LAUNCH                              │  │
    │  │                         (single flow node)                             │  │
    │  │                                                                        │  │
    │  │    ┌─────────────────────────────────────────────────────────────┐     │  │
    │  │    │  NEW PAGE BUILDS (deferred to post-launch):                 │     │  │
    │  │    │  • FAQ/problem pages from keyword gaps                      │     │  │
    │  │    │  • Location/service pages                                   │     │  │
    │  │    │  • Insurance/pricing pages                                  │     │  │
    │  │    │                                                             │     │  │
    │  │    │  MONITORING:                                                │     │  │
    │  │    │  • Crawl errors (GSC)                                       │     │  │
    │  │    │  • Index coverage                                           │     │  │
    │  │    │  • Ranking changes                                          │     │  │
    │  │    │  • CWV field data                                           │     │  │
    │  │    │                                                             │     │  │
    │  │    │  TRUST BUILDING:                                            │     │  │
    │  │    │  • Internal linking improvements                            │     │  │
    │  │    │  • Local trust signals (maps, reviews, NAP)                 │     │  │
    │  │    └─────────────────────────────────────────────────────────────┘     │  │
    │  │                                                                        │  │
    │  │    OUTPUTS: post_launch_report_path                                    │  │
    │  └────────────────────────────────────────────────────────────────────────┘  │
    │                                                                              │
    └──────────────────────────────────────┬───────────────────────────────────────┘
                                           │
               ┌───────────────────────────┼───────────────────────────┐
               │                           │                           │
               ▼                           ▼                           ▼
        ┌─────────────┐             ┌─────────────┐             ┌─────────────┐
        │   SUCCESS   │             │   FAILURE   │             │  ESCALATE   │
        │  (terminal) │             │  (terminal) │             │  (terminal) │
        │             │             │             │             │             │
        │ All phases  │             │ Max retries │             │ Human input │
        │ complete    │             │ exceeded    │             │ required    │
        └─────────────┘             └─────────────┘             └─────────────┘
```

## Architecture Comparison: Codex vs Claude

| Aspect | Codex Brain | Claude Brain |
|--------|-------------|--------------|
| Total Nodes | 12 | ~50 |
| Node per Phase | 1 (monolithic) | 4-6 (granular) |
| Gate Nodes | 0 (inline) | 8 (explicit) |
| Parallel Support | Via edge config | Via tributary nodes |
| Retry Logic | Built into edges | Via gate retry loops |
| Complexity | Lower | Higher |
| Granularity | Phase-level | Task-level |

## Node Types Used

| Type | Count | Purpose |
|------|-------|---------|
| prime | 1 | Entry point (intake) |
| flow | 9 | One per phase (monolithic) |
| terminal | 3 | Exit points (success/failure/escalate) |

## Deliverables Generated

1. `keyword_universe.csv` - Keyword clusters with scoring
2. `keyword_page_map.json` - Keyword to page mapping
3. `master_url_sheet.csv` - Complete URL inventory
4. `redirect_map.json` - Vercel redirect configuration
5. `techseo_audit.json` - H1, meta, schema audit
6. `cwv_report.json` - Core Web Vitals baseline/targets
7. `qa_checklist.json` - Pre-launch QA results
8. `launch_manifest.json` - Launch config and rollback plan

## Skills Integration

- `screaming_frog` - Site crawling
- `gsc_export` - Google Search Console data
- `ahrefs_api` - Backlink data
- `vercel_cli` - Deployment management
- `lighthouse` - Performance testing
- `schema_validator` - Schema markup validation
