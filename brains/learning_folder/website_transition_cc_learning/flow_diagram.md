# Website Transition CC Learning Flow - Procedural Map

## Overview
WordPress to GitHub/Vercel migration with SEO equity protection.

**Source:** `/mnt/d_drive/repos/learning/knowledge_repo/concepts/website_transition_cc`

**Core Principle:** "If you change URLs without a perfect redirect plan, you will lose rankings."

## Architecture: Dual Map System

This knowledge system uses two interconnected maps:
1. **Concept Flow Map** - Sense-making / logic trunk (why)
2. **Procedural Flow Map** - Execution / steps (how)

## High-Level Procedural Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│              WEBSITE TRANSITION CC - PROCEDURAL FLOW MAP                        │
│                  WordPress → GitHub/Vercel Migration                            │
│                                                                                 │
│   Core Principle: "If you change URLs without a perfect redirect plan,         │
│                    you will lose rankings."                                     │
└─────────────────────────────────────────────────────────────────────────────────┘

                                    ┌─────────────────────┐
                                    │        ROOT         │
                                    │  Migration Workflow │
                                    │                     │
                                    │ Entry point for all │
                                    │ execution phases    │
                                    └──────────┬──────────┘
                                               │
                        ┌──────────────────────┴──────────────────────┐
                        │                                             │
                        ▼                                             │
               ┌────────────────┐                                     │
               │  KEY ASSETS &  │                                     │
               │   RESOURCES    │                                     │
               │  (cross-cut)   │                                     │
               │                │                                     │
               │ Pointers to    │                                     │
               │ tools & files  │                                     │
               └────────────────┘                                     │
                                                                      │
                                                                      ▼
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │               PHASE 1: KEYWORD STRATEGY VALIDATION                          │
    │                                                                             │
    │  PURPOSE: Validate keyword targets and page map before migration            │
    │  WHY: Determines whether current structure serves business goals            │
    │                                                                             │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
    │  │ Build Keyword    │  │ Competitor       │  │ Create Page      │          │
    │  │ Universe         │──▶ Reality Check   │──▶│ Map              │          │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
    │         │                      │                      │                     │
    │         ▼                      ▼                      ▼                     │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
    │  │ Intent Buckets:  │  │ "You want truth, │  │ "Every target    │          │
    │  │ • Service+city   │  │  not hope"       │  │  keyword gets    │          │
    │  │ • Near me        │  │                  │  │  a page"         │          │
    │  │ • Problem-based  │  │ See what winners │  │                  │          │
    │  │ • Price/insurance│  │ have that you    │  │ Keep/build       │          │
    │  │ • Brand/compare  │  │ lack             │  │ decisions        │          │
    │  │ • Location mods  │  │                  │  │                  │          │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
    └─────────────────────────────────────────────────────────────────────────────┤
                                                                                  │
                                                                                  ▼
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │               PHASE 2: CURRENT-STATE SEO + LINK MAPPING                     │
    │                                                                             │
    │  PURPOSE: Inventory all URLs, traffic, backlinks, and internal links        │
    │  WHY: "Cannot protect what you don't know"                                  │
    │                                                                             │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
    │  │ Crawl + Export   │  │ Export GSC       │  │ Build Master     │          │
    │  │ Inventory        │──▶ Data            │──▶│ URL Sheet        │          │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
    │         │                      │                      │                     │
    │         ▼                      ▼                      ▼                     │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
    │  │ Screaming Frog   │  │ • Top pages      │  │ NON-NEGOTIABLE   │          │
    │  │ • Status codes   │  │ • Queries/page   │  │ ARTIFACT         │          │
    │  │ • Titles, H1s    │  │ • External links │  │                  │          │
    │  │ • Canonicals     │  │                  │  │ old_url | type   │          │
    │  │ • Internal links │  │ Real traffic     │  │ traffic | backlinks        │
    │  │   in/out         │  │ data for         │  │ new_url | action │          │
    │  │                  │  │ prioritization   │  │ redirect_type    │          │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
    └─────────────────────────────────────────────────────────────────────────────┤
                                                                                  │
                                                                                  ▼
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │               PHASE 3: FUTURE-STATE ARCHITECTURE                            │
    │                                                                             │
    │  PURPOSE: Design new sitemap, consolidations, and redirect map              │
    │  WHY: Balances SEO preservation with structural improvements                │
    │                                                                             │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
    │  │ Make URL         │  │ Create Redirect  │  │ Handle WP        │          │
    │  │ Decisions        │──▶ Map             │──▶│ Ghost URLs       │          │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
    │         │                      │                      │                     │
    │         ▼                      ▼                      ▼                     │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
    │  │ For each URL:    │  │ REDIRECT RULES:  │  │ Tag/author/date  │          │
    │  │ • Keep           │  │ • 1:1 is best    │  │ archives,        │          │
    │  │ • Redirect       │  │ • NEVER redirect │  │ attachment pages │          │
    │  │ • Consolidate    │  │   everything to  │  │                  │          │
    │  │ • Remove         │  │   homepage       │  │ Options:         │          │
    │  │                  │  │ • Document       │  │ • noindex        │          │
    │  │ Keep money pages │  │   old → new      │  │ • redirect       │          │
    │  │ stable!          │  │                  │  │ • remove         │          │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
    └─────────────────────────────────────────────────────────────────────────────┤
                                                                                  │
                                                                                  ▼
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │               PHASE 4: BUILD IN GITHUB                                      │
    │                                                                             │
    │  PURPOSE: Rebuild site cleanly in Next.js with content system               │
    │  WHY: Implements technical stack and content management approach            │
    │                                                                             │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
    │  │ Set Up GitHub    │  │ Build Next.js    │  │ Choose Content   │          │
    │  │ Repo             │──▶ Site            │──▶│ System           │          │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
    │         │                      │                      │                     │
    │         ▼                      ▼                      ▼                     │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
    │  │ BRANCHING:       │  │ "Next.js is the  │  │ OPTIONS:         │          │
    │  │                  │  │  default safe    │  │ • Markdown in    │          │
    │  │ main = prod      │  │  choice for      │  │   repo           │          │
    │  │ staging = QA     │  │  Vercel"         │  │ • Git-backed CMS │          │
    │  │ feature branches │  │                  │  │ • Headless CMS   │          │
    │  │                  │  │ Build pages      │  │                  │          │
    │  │ Clean branching  │  │ matching planned │  │ "If non-tech     │          │
    │  │ enables safe     │  │ sitemap          │  │  people edit,    │          │
    │  │ deployments      │  │                  │  │  they need CMS"  │          │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
    └─────────────────────────────────────────────────────────────────────────────┤
                                                                                  │
                                                                                  ▼
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │               PHASE 5: TECHNICAL SEO IMPLEMENTATION                         │
    │                                                                             │
    │  PURPOSE: Implement metadata, canonicals, schema, sitemaps, robots          │
    │  WHY: Preserves and improves SEO signals in the new platform                │
    │                                                                             │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
    │  │ Implement        │  │ Implement        │  │ Implement        │          │
    │  │ Metadata         │──▶ Canonicals      │──▶│ Schema           │          │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
    │         │                      │                      │                     │
    │         ▼                      ▼                      ▼                     │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
    │  │ "Titles are      │  │ • Canonical tag  │  │ SITE-WIDE:       │          │
    │  │  major ranking   │  │   on EVERY page  │  │ • LocalBusiness  │          │
    │  │  factor"         │  │ • Handle params  │  │ • Organization   │          │
    │  │                  │  │ • Faceted nav    │  │                  │          │
    │  │ • Titles match   │  │                  │  │ PAGE-LEVEL:      │          │
    │  │   intent+location│  │ Prevents         │  │ • Service schema │          │
    │  │ • Meta desc      │  │ duplicate        │  │   on service     │          │
    │  │   sells click    │  │ content issues   │  │   pages          │          │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
    └─────────────────────────────────────────────────────────────────────────────┤
                                                                                  │
                                                                                  ▼
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │               PHASE 6: PERFORMANCE + CWV                                    │
    │                                                                             │
    │  PURPOSE: Optimize for Core Web Vitals targets                              │
    │  WHY: "Performance is a ranking factor. New platform must not regress."     │
    │                                                                             │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
    │  │ Establish        │  │ Set Performance  │  │ Optimize Images  │          │
    │  │ Baseline         │──▶ Budgets         │──▶│ + LCP            │          │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
    │         │                      │                      │                     │
    │         ▼                      ▼                      ▼                     │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
    │  │ Pull PSI/        │  │ "Budgets prevent │  │ "Images often    │          │
    │  │ Lighthouse       │  │  regression"     │  │  determine LCP"  │          │
    │  │ BEFORE migration │  │                  │  │                  │          │
    │  │                  │  │ • JS per page    │  │ • AVIF/WebP      │          │
    │  │ "Cannot measure  │  │ • Image formats  │  │ • Preload hero   │          │
    │  │  improvement     │  │ • Font weights   │  │ • Reserve space  │          │
    │  │  without         │  │ • Third-party    │  │   (CLS)          │          │
    │  │  baseline"       │  │   scripts        │  │                  │          │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
    │                                                                             │
    │  ┌─────────────────────────────────────────────────────────────────────┐    │
    │  │                      CWV TARGETS                                   │    │
    │  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐               │    │
    │  │  │ LCP ≤ 2.5s  │   │ INP ≤ 200ms │   │ CLS ≤ 0.1   │               │    │
    │  │  └─────────────┘   └─────────────┘   └─────────────┘               │    │
    │  └─────────────────────────────────────────────────────────────────────┘    │
    └─────────────────────────────────────────────────────────────────────────────┤
                                                                                  │
                                                                                  ▼
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │               PHASE 7: QA + LAUNCH + MONITORING                             │
    │                                                                             │
    │  PURPOSE: Final verification and production cutover                         │
    │  WHY: "Prevents surprises and enables fast response to issues"              │
    │                                                                             │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
    │  │ SEO QA           │  │ Verify           │  │ Launch           │          │
    │  │ Checklist        │──▶ Redirects       │──▶│ Cutover          │          │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
    │         │                      │                      │                     │
    │         ▼                      ▼                      ▼                     │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
    │  │ CRAWL STAGING:   │  │ "Broken          │  │ CUTOVER          │          │
    │  │ □ No broken      │  │  redirects cause │  │ SEQUENCE:        │          │
    │  │   links          │  │  ranking drops"  │  │                  │          │
    │  │ □ Correct        │  │                  │  │ 1. Freeze WP     │          │
    │  │   canonicals     │  │ • Test top 20    │  │ 2. Push          │          │
    │  │ □ Schema         │  │   legacy URLs    │  │    redirects     │          │
    │  │   validates      │  │ • No redirect    │  │ 3. Swap DNS      │          │
    │  │                  │  │   chains         │  │ 4. Submit        │          │
    │  │ "Catch issues    │  │                  │  │    sitemap       │          │
    │  │  before prod"    │  │                  │  │                  │          │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
    └─────────────────────────────────────────────────────────────────────────────┤
                                                                                  │
                                                                                  ▼
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │               PHASE 8: POST-LAUNCH ITERATION                                │
    │                                                                             │
    │  PURPOSE: Build missing pages and strengthen internal linking               │
    │  WHY: "Converts traffic into leads and grows organic presence"              │
    │                                                                             │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
    │  │ Build Missing    │  │ Strengthen       │  │ Add Local        │          │
    │  │ Pages            │──▶ Internal Linking│──▶│ Trust Blocks     │          │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
    │         │                      │                      │                     │
    │         ▼                      ▼                      ▼                     │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
    │  │ From keyword     │  │ "Internal links  │  │ TRUST ELEMENTS:  │          │
    │  │ map:             │  │  distribute      │  │ • Service area   │          │
    │  │ • FAQ pages      │  │  equity"         │  │ • FAQs           │          │
    │  │ • Problem        │  │                  │  │ • Testimonials   │          │
    │  │   content        │  │ Every service    │  │ • Directions/    │          │
    │  │                  │  │ page linked from:│  │   parking        │          │
    │  │ "Long-tail pages │  │ • Nav            │  │                  │          │
    │  │  drive traffic   │  │ • Homepage       │  │ "Improves        │          │
    │  │  and feed        │  │ • Related FAQs   │  │  conversions and │          │
    │  │  internal links" │  │                  │  │  local relevance"│          │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
    └─────────────────────────────────────────────────────────────────────────────┘
```

## Node Summary

| Phase | Name | Sub-Tasks |
|-------|------|-----------|
| 1 | Keyword Strategy Validation | Build Universe, Competitor Check, Create Page Map |
| 2 | Current-State SEO + Link Mapping | Crawl + Export, GSC Data, Master URL Sheet |
| 3 | Future-State Architecture | URL Decisions, Redirect Map, Handle WP Ghost URLs |
| 4 | Build in GitHub | Repo Setup, Next.js Build, Content System |
| 5 | Technical SEO | Metadata, Canonicals, Schema |
| 6 | Performance + CWV | Baseline, Budgets, Image/LCP Optimization |
| 7 | QA + Launch + Monitoring | SEO QA, Verify Redirects, Cutover |
| 8 | Post-Launch Iteration | Missing Pages, Internal Linking, Local Trust |

## Key Artifacts

| Artifact | Purpose |
|----------|---------|
| **Keyword Universe** | All relevant keywords by intent bucket |
| **Page Map** | Every keyword cluster mapped to a page |
| **Master URL Sheet** | Single source of truth for all URL outcomes |
| **Redirect Map** | Old → new for every changing URL |

## Core Rules

1. **URL Stability** - Keep money pages stable, consolidate only when intent matches
2. **Redirect Quality** - 1:1 is best, NEVER redirect everything to homepage
3. **Master Sheet** - Non-negotiable artifact, every URL gets deliberate outcome
4. **CMS Decision** - If non-technical people edit, they need a CMS or site stagnates
5. **Baseline First** - Cannot measure improvement without baseline

## Edge Types

- **precedes** (trunk) - Sequential phase progression
- **part_of** - Sub-tasks within a phase

## Total Nodes: 35

- 1 Root node
- 8 Phase nodes (trunk)
- 1 Cross-cutting node (Key Assets)
- 25 Sub-task nodes

## Source Files

- `knowledge/exports/latest.rivermap.json` - Full procedural map
- `website_transition_cc_concept_map/knowledge/exports/latest.rivermap.json` - Concept map
- `CONTROL_STATE.json` - Status and flags
