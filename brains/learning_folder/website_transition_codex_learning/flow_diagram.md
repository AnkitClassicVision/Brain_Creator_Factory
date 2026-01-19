# Website Transition Learning Flow - Procedural Map

## Overview
SEO-Safe WordPress → GitHub → Vercel migration procedural flow derived from the learning knowledge repository.

**Source:** `/mnt/d_drive/repos/learning/knowledge_repo/concepts/website_transition`

## Architecture: Dual Map System

This knowledge system uses two interconnected maps:
1. **Concept Flow Map** - Sense-making / logic trunk (why)
2. **Procedural Flow Map** - Execution / steps (how)

## High-Level Procedural Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│              WEBSITE TRANSITION - PROCEDURAL FLOW MAP                           │
│                  (SEO-Safe WP → GitHub → Vercel)                                │
│                                                                                 │
│   "Plan first, map every old link, rebuild carefully, test everything,         │
│    launch safely, then improve."                                                │
└─────────────────────────────────────────────────────────────────────────────────┘

                                    ┌─────────────────────┐
                                    │        ROOT         │
                                    │  Website Transition │
                                    │   Procedural Flow   │
                                    └──────────┬──────────┘
                                               │
        ┌──────────────────┬───────────────────┼───────────────────┬──────────────────┐
        │                  │                   │                   │                  │
        ▼                  ▼                   ▼                   ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐   [TRUNK]
│  GUARDRAILS   │  │    CORE       │  │    TOOLS +    │  │   PHASE 0     │      │
│  (cross-cut)  │  │  ARTIFACTS    │  │ DATA SOURCES  │  │ Lock Key      │      │
│               │  │  (cross-cut)  │  │  (cross-cut)  │  │ Decisions     │      │
│ • URL policy  │  │               │  │               │  │               │      │
│ • No homepage │  │ • Master URL  │  │ • Screaming   │  │ ┌───────────┐ │      │
│   redirects   │  │   Sheet       │  │   Frog        │  │ │URL Policy │ │      │
│ • Noindex     │  │ • Redirect    │  │ • GSC Export  │  │ │(Keep URLs)│ │      │
│   staging     │  │   Map         │  │ • Ahrefs      │  │ └───────────┘ │      │
│ • Freeze WP   │  │ • Keyword     │  │ • Lighthouse  │  │ ┌───────────┐ │      │
│   pre-launch  │  │   Universe    │  │ • PSI         │  │ │Edit Flow  │ │      │
└───────────────┘  └───────────────┘  └───────────────┘  │ │(CMS/PRs)  │ │      │
                                                          │ └───────────┘ │      │
                                                          │ ┌───────────┐ │      │
                                                          │ │Launch     │ │      │
                                                          │ │Scope      │ │      │
                                                          │ │(Parity)   │ │      │
                                                          │ └───────────┘ │      │
                                                          └───────┬───────┘      │
                                                                  │              │
                                                                  ▼              │
    ┌─────────────────────────────────────────────────────────────────────────────┤
    │                     PHASE 1: KEYWORD STRATEGY + PAGE MAP                    │
    │  ┌─────────────────────────────────────────────────────────────────────┐    │
    │  │                     Intent Buckets to Cover:                        │    │
    │  │  • Service + City (high intent)                                     │    │
    │  │  • "Near me" queries (mobile heavy)                                 │    │
    │  │  • Problem-based (easier wins)                                      │    │
    │  │  • Price/Insurance (conversion gold)                                │    │
    │  │  • Brand/Comparison (mid-funnel)                                    │    │
    │  └─────────────────────────────────────────────────────────────────────┘    │
    │                                                                             │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
    │  │ Build Keyword    │  │ Competitor       │  │ Create Page Map  │          │
    │  │ Universe         │──▶ Reality Check   │──▶│ + Scoring Model  │          │
    │  │ (Intent Buckets) │  │ (SERP Analysis)  │  │ (Priorities)     │          │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
    └─────────────────────────────────────────────────────────────────────────────┤
                                                                                  │
                                                                                  ▼
    ┌─────────────────────────────────────────────────────────────────────────────┤
    │                     PHASE 2: CURRENT-STATE SEO INVENTORY                    │
    │                                                                             │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
    │  │ Crawl +          │  │ Pull Authority   │  │ Build Master     │          │
    │  │ Inventory Site   │──▶ Signals         │──▶│ URL Sheet        │          │
    │  │ (Screaming Frog) │  │ (GSC/Backlinks)  │  │ (Every URL)      │          │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
    │                                                                             │
    │  MASTER URL SHEET FORMAT:                                                   │
    │  ┌─────────────────────────────────────────────────────────────────────┐    │
    │  │ old_url | type | traffic | backlinks | query | new_url | action    │    │
    │  └─────────────────────────────────────────────────────────────────────┘    │
    └─────────────────────────────────────────────────────────────────────────────┤
                                                                                  │
                                                                                  ▼
    ┌─────────────────────────────────────────────────────────────────────────────┤
    │               PHASE 3: FUTURE-STATE ARCHITECTURE + REDIRECT PLAN            │
    │                                                                             │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
    │  │ Define Future    │  │ Build Redirect   │  │ Plan Vercel      │          │
    │  │ Sitemap +        │──▶ Map (Complete)  │──▶│ Redirect Impl    │          │
    │  │ Consolidation    │  │ 1:1 preferred    │  │ (Edge/Bulk)      │          │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
    │                                                                             │
    │  REDIRECT RULES:                                                            │
    │  ┌─────────────────────────────────────────────────────────────────────┐    │
    │  │ • One-to-one redirects where possible                              │    │
    │  │ • Consolidate only when intent matches                             │    │
    │  │ • NEVER redirect everything to homepage (soft-404 spam)            │    │
    │  │ • Avoid redirect chains                                            │    │
    │  └─────────────────────────────────────────────────────────────────────┘    │
    └─────────────────────────────────────────────────────────────────────────────┤
                                                                                  │
                                                                                  ▼
    ┌─────────────────────────────────────────────────────────────────────────────┤
    │                     PHASE 4: BUILD NEW SITE (GitHub → Vercel)               │
    │                                                                             │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
    │  │ Set Up Repo +    │  │ Build Content    │  │ Implement        │          │
    │  │ Branching        │──▶ System          │──▶│ Content Parity   │          │
    │  │ (main/staging)   │  │ (MD/MDX or CMS)  │  │ Pages            │          │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
    │                                                                             │
    │  BRANCHING STRATEGY:                                                        │
    │  ┌─────────────────────────────────────────────────────────────────────┐    │
    │  │ main = production   │   staging = QA   │   feature/* = PRs         │    │
    │  │     (indexable)     │   (noindex)      │   (preview deploys)       │    │
    │  └─────────────────────────────────────────────────────────────────────┘    │
    └─────────────────────────────────────────────────────────────────────────────┤
                                                                                  │
                                                                                  ▼
    ┌─────────────────────────────────────────────────────────────────────────────┤
    │                     PHASE 5: TECHNICAL SEO IMPLEMENTATION                   │
    │                                                                             │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
    │  │ Implement        │  │ Implement        │  │ Generate         │          │
    │  │ Metadata +       │──▶ Schema          │──▶│ Sitemaps +       │          │
    │  │ Canonicals       │  │ (Local+Page)     │  │ Robots           │          │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
    │                                                                             │
    │  SCHEMA TYPES:                                                              │
    │  ┌─────────────────────────────────────────────────────────────────────┐    │
    │  │ Site-Wide: Organization, LocalBusiness, WebSite, BreadcrumbList    │    │
    │  │ Page-Level: Service, FAQPage (where appropriate)                   │    │
    │  └─────────────────────────────────────────────────────────────────────┘    │
    └─────────────────────────────────────────────────────────────────────────────┤
                                                                                  │
                                                                                  ▼
    ┌─────────────────────────────────────────────────────────────────────────────┤
    │                     PHASE 6: PERFORMANCE + CORE WEB VITALS                  │
    │                                                                             │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
    │  │ Establish        │  │ Set Performance  │  │ Apply Next.js    │          │
    │  │ Baseline         │──▶ Budget          │──▶│ Performance      │          │
    │  │ (PSI/Lighthouse) │  │ (JS/Img/Fonts)   │  │ Tactics          │          │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
    │                                                                             │
    │  ┌─────────────────────────────────────────────────────────────────────┐    │
    │  │                      CWV TARGETS                                   │    │
    │  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐               │    │
    │  │  │ LCP ≤ 2.5s  │   │ INP ≤ 200ms │   │ CLS ≤ 0.1   │               │    │
    │  │  └─────────────┘   └─────────────┘   └─────────────┘               │    │
    │  └─────────────────────────────────────────────────────────────────────┘    │
    │                                                                             │
    │  TACTICS:                                                                   │
    │  • Optimize images (AVIF/WebP), reduce hydration, preload hero (LCP)        │
    │  • Reserve space for embeds (CLS), minimize third-party scripts (INP)       │
    └─────────────────────────────────────────────────────────────────────────────┤
                                                                                  │
                                                                                  ▼
    ┌─────────────────────────────────────────────────────────────────────────────┤
    │                     PHASE 7: QA + LAUNCH + MONITORING                       │
    │                                                                             │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
    │  │ SEO QA           │  │ Tracking QA      │  │ Cutover +        │          │
    │  │ (Pre-Launch)     │──▶ (Pre-Launch)    │──▶│ Monitoring       │          │
    │  │ [crawl staging]  │  │ [GA4/GSC]        │  │ [DNS swap]       │          │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
    │                                                                             │
    │  SEO QA CHECKLIST:                                                          │
    │  ┌─────────────────────────────────────────────────────────────────────┐    │
    │  │ □ No broken internal links      □ Schema validates                 │    │
    │  │ □ Correct canonicals            □ No redirect chains               │    │
    │  │ □ Sitemap matches pages         □ Legacy URLs redirect correctly   │    │
    │  └─────────────────────────────────────────────────────────────────────┘    │
    │                                                                             │
    │  CUTOVER SEQUENCE:                                                          │
    │  ┌─────────────────────────────────────────────────────────────────────┐    │
    │  │ 1. Freeze WP changes                                               │    │
    │  │ 2. Push final redirects                                            │    │
    │  │ 3. DNS swap                                                        │    │
    │  │ 4. Smoke test key pages + top legacy URLs                          │    │
    │  │ 5. Submit sitemap to GSC                                           │    │
    │  │ 6. Monitor: errors, indexing, CWV, rankings                        │    │
    │  └─────────────────────────────────────────────────────────────────────┘    │
    └─────────────────────────────────────────────────────────────────────────────┤
                                                                                  │
                                                                                  ▼
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │                     PHASE 8: POST-LAUNCH ITERATION                          │
    │                                                                             │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
    │  │ Build Missing    │  │ Improve Internal │  │ Continue Perf +  │          │
    │  │ Pages (from      │──▶ Links + Local   │──▶│ SEO Ops          │          │
    │  │ keyword map)     │  │ Trust Blocks     │  │ (Iterate)        │          │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
    │                                                                             │
    │  POST-LAUNCH PRIORITIES:                                                    │
    │  ┌─────────────────────────────────────────────────────────────────────┐    │
    │  │ • Build FAQ/problem pages from keyword gaps                        │    │
    │  │ • Strengthen internal linking                                      │    │
    │  │ • Add service area, testimonials, directions/parking               │    │
    │  │ • Mobile click-to-call, clear CTAs                                 │    │
    │  │ • Continue CWV improvements (especially INP)                       │    │
    │  │ • Audit for regressions, iterate based on GSC/rankings             │    │
    │  └─────────────────────────────────────────────────────────────────────┘    │
    └─────────────────────────────────────────────────────────────────────────────┘
```

## Node Summary

| Phase | Name | Sub-Tasks |
|-------|------|-----------|
| 0 | Lock Key Decisions | URL Policy, Editing Workflow, Launch Scope |
| 1 | Keyword Strategy | Build Universe, Competitor Check, Page Map |
| 2 | Current-State Inventory | Crawl Site, Pull Authority, Master URL Sheet |
| 3 | Future-State Architecture | Define Sitemap, Redirect Map, Vercel Implementation |
| 4 | Build New Site | Repo Setup, Content System, Parity Pages |
| 5 | Technical SEO | Metadata/Canonicals, Schema, Sitemaps/Robots |
| 6 | Performance/CWV | Baseline, Budget, Tactics |
| 7 | QA + Launch | SEO QA, Tracking QA, Cutover + Monitoring |
| 8 | Post-Launch | Missing Pages, Internal Links, Ongoing Ops |

## Cross-Cutting Elements

| Element | Purpose |
|---------|---------|
| **Guardrails** | Prevent SEO damage (URL policy, noindex staging, freeze WP) |
| **Core Artifacts** | Auditable deliverables (Master URL Sheet, Redirect Map, Keyword Universe) |
| **Tools + Data Sources** | Inputs for inventory and validation (Screaming Frog, GSC, Ahrefs, Lighthouse) |

## Key Principles

1. **URL Stability First** - Keep URLs wherever possible
2. **Content Parity at Launch** - Same key pages, then iterate
3. **Deliberate URL Outcomes** - Every URL gets explicit action
4. **1:1 Redirects** - Avoid homepage redirect sinks
5. **Growth After Stability** - Build new content post-launch

## Edge Types

- **precedes** (trunk) - Sequential phase progression
- **part_of** - Sub-tasks within a phase

## Source Files

- `knowledge/exports/latest.rivermap.json` - Full procedural map
- `website_transition_concept_map/knowledge/exports/latest.rivermap.json` - Concept map
- `CONTROL_STATE.json` - Status and flags
