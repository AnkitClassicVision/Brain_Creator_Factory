# Comprehensive Comparison: 4 Website Transition Processes

## Executive Summary

All 4 processes share the same goal: **SEO-safe WordPress → Vercel migration**. However, they differ significantly in architecture, granularity, validation gates, and operational approach.

| Aspect | Claude Brain | Codex Brain | Learning Procedural | Learning CC |
|--------|--------------|-------------|---------------------|-------------|
| **Type** | Execution Brain | Execution Brain | Knowledge Map | Knowledge Map |
| **Phases** | 9 (with Phase 0) | 8 | 9 (Phase 0-8) | 8 (Phase 1-8) |
| **Total Nodes** | ~50 | 12 | 40 | 35 |
| **Explicit Gates** | 8 gate nodes | 0 (inline) | 0 (implicit) | 0 (implicit) |
| **Deliverables** | 7 required | 13 required | 3 defined | 4 (Master Sheet key) |
| **Parallel Support** | Tributary nodes | Edge config | N/A | N/A |
| **Terminal States** | 3 | 3 | N/A | N/A |

---

## 1. ARCHITECTURAL DIFFERENCES

### Claude Brain Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    CLAUDE BRAIN                             │
│              (Granular, Gate-Heavy)                         │
├─────────────────────────────────────────────────────────────┤
│  Node Types:                                                │
│  • prime (1) - Entry point                                  │
│  • flow (~35) - Sequential processing                       │
│  • gate (8) - Explicit validation checkpoints               │
│  • tributary (4) - Parallel data collection                 │
│  • terminal (3) - Exit points                               │
├─────────────────────────────────────────────────────────────┤
│  Phase Structure:                                           │
│  Each phase = 4-6 sub-nodes + validation gate               │
│  Example Phase 1:                                           │
│    keyword_build_universe → keyword_competitor_check        │
│    → keyword_page_map → keyword_scoring                     │
│    → keyword_validation_gate (GATE)                         │
└─────────────────────────────────────────────────────────────┘
```

### Codex Brain Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    CODEX BRAIN                              │
│              (Compact, Monolithic Phases)                   │
├─────────────────────────────────────────────────────────────┤
│  Node Types:                                                │
│  • prime (1) - Entry point                                  │
│  • flow (9) - One per phase (monolithic)                    │
│  • terminal (3) - Exit points                               │
├─────────────────────────────────────────────────────────────┤
│  Phase Structure:                                           │
│  Each phase = 1 large node with all sub-tasks inline        │
│  Retry logic built into edge configuration                  │
│  No explicit gate nodes - validation is internal            │
└─────────────────────────────────────────────────────────────┘
```

### Learning Procedural Map Architecture
```
┌─────────────────────────────────────────────────────────────┐
│               LEARNING PROCEDURAL MAP                       │
│              (Knowledge-Centric, Detailed)                  │
├─────────────────────────────────────────────────────────────┤
│  Node Types:                                                │
│  • Root node with trunk phases                              │
│  • Phase nodes (Phase 0-8)                                  │
│  • Sub-task nodes (3-4 per phase)                           │
│  • Cross-cutting: Guardrails, Artifacts, Tools              │
├─────────────────────────────────────────────────────────────┤
│  Edge Types:                                                │
│  • precedes (is_trunk: true) - Main flow                    │
│  • part_of (is_trunk: false) - Sub-tasks                    │
│  Every edge has WHY + HOW documentation                     │
└─────────────────────────────────────────────────────────────┘
```

### Learning CC Map Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                  LEARNING CC MAP                            │
│              (Execution-Focused, Streamlined)               │
├─────────────────────────────────────────────────────────────┤
│  Node Types:                                                │
│  • Root: Migration Workflow                                 │
│  • Phase nodes (Phase 1-8, no Phase 0)                      │
│  • Sub-task nodes (3 per phase)                             │
│  • Cross-cutting: Key Assets only                           │
├─────────────────────────────────────────────────────────────┤
│  Key Difference: No Phase 0 (Lock Decisions)                │
│  Starts directly with Keyword Strategy                      │
│  More operational, less conceptual depth                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. VALIDATION GATES / TOLLGATES

### Claude Brain - Explicit Gate Nodes (8 Gates)

| Gate | Location | Criteria | On Fail |
|------|----------|----------|---------|
| `keyword_validation_gate` | After Phase 1 | keywords mapped, ≥4 buckets covered | Retry keyword_build_universe |
| `mapping_validation_gate` | After Phase 2 | all URLs with traffic/backlinks mapped | Retry mapping |
| `arch_validation_gate` | After Phase 3 | redirect plan verified, no chains | Retry architecture |
| `build_validation_gate` | After Phase 4 | staging deployed, accessible | Retry build |
| `techseo_validation_gate` | After Phase 5 | H1/meta/schema valid | Retry tech SEO |
| `cwv_validation_gate` | After Phase 6 | LCP ≤2.5s, INP ≤200ms, CLS ≤0.1 | Retry optimizations |
| `qa_validation_gate` | After Phase 7 | all QA checks pass | Retry QA |
| `launch_validation_gate` | After Phase 8 | DNS propagated, site live | Handle failure |

**Retry Policy:** max_retries: 2-3 per gate

### Codex Brain - Inline Validation

- No explicit gate nodes
- Validation criteria embedded in phase prompts
- Retry logic in edge configuration between phases
- `phase_status: "complete|needs_input|blocked"` determines flow

### Learning Maps - Implicit Validation

- No formal gates
- Validation through deliverable completion
- "Done when" criteria in node definitions
- Human judgment required for progression

---

## 3. CONSTRAINTS / REQUIREMENTS

### Must-Do Rules (All 4 Processes Share Core Rules)

| Rule | Claude | Codex | Learning | Learning CC |
|------|--------|-------|----------|-------------|
| Keep same URLs for money pages | ✓ | ✓ | ✓ | ✓ |
| Pull GSC data before decisions | ✓ | ✓ | ✓ | ✓ |
| Every URL with traffic gets outcome | ✓ | ✓ | ✓ | ✓ |
| One-to-one redirects preferred | ✓ | ✓ | ✓ | ✓ |
| Noindex staging/preview | ✓ | ✓ | ✓ | ✓ |
| Canonical on every page | ✓ | ✓ | ✓ | ✓ |
| LocalBusiness schema site-wide | ✓ | ✓ | ✓ | ✓ |
| CWV targets (LCP/INP/CLS) | ✓ | ✓ | ✓ | ✓ |
| Freeze WP before launch | ✓ | ✓ | ✓ | ✓ |

### Must-Not Rules

| Rule | Claude | Codex | Learning | Learning CC |
|------|--------|-------|----------|-------------|
| Don't redirect all to homepage | ✓ | ✓ | ✓ | ✓ |
| Don't change URLs without redirects | ✓ | ✓ | ✓ | ✓ |
| Don't launch with big rewrites | ✓ | ✓ | ✓ | ✓ |
| Don't ignore WP ghost URLs | ✓ | ✓ | ✓ | ✓ |
| Don't ship heavy client hydration | ✓ | ✓ | ✓ | ✓ |
| Don't add INP-killing scripts | ✓ | ✓ | ✓ | ✓ |

### Unique Constraints

| Process | Unique Constraint |
|---------|-------------------|
| **Claude** | "Break NAP consistency with call tracking numbers" |
| **Codex** | "Consolidate pages with mismatched search intent" explicitly forbidden |
| **Learning** | "Accessibility + Conversion Regression" as explicit pitfall |
| **Learning CC** | "Non-negotiable: Master URL Sheet" emphasized |

---

## 4. DELIVERABLES COMPARISON

### Claude Brain (7 Required)

```
1. keyword_universe.csv       - Keyword clusters with scoring
2. master_url_sheet.csv       - Complete URL inventory with actions
3. redirect_map.json          - Vercel redirect configuration
4. technical_seo_audit.json   - H1, meta, schema audit results
5. cwv_report.json            - Core Web Vitals baseline/targets
6. qa_checklist.json          - Pre-launch QA results
7. launch_manifest.json       - Launch config and rollback plan
```

### Codex Brain (13 Required)

```
1. keyword_universe.csv       - Keyword universe + clustering + scoring
2. keyword_page_map.csv       - Keyword cluster → target page mapping
3. current_url_inventory.csv  - Full crawl export
4. master_url_sheet.csv       - URL-by-URL action plan
5. redirect_map.csv           - old_url → new_url mapping
6. redirects_config.json      - Vercel/Next.js redirect config
7. sitemap_plan.csv           - Future sitemap aligned to keywords
8. robots_and_sitemaps.json   - Robots rules + sitemap locations
9. technical_seo_audit.json   - Metadata/canonical/schema checks
10. cwv_report.json           - Baseline, budgets, targets
11. qa_crawl_report.json      - Broken links, canonicals, redirects
12. launch_runbook.md         - Cutover checklist + rollback
13. post_launch_monitoring.md - 30-day monitoring plan (optional)
```

### Learning Procedural (3 Defined)

```
1. Keyword Clusters + Page Map   - Strategy deliverable
2. Master URL Sheet              - Mapping deliverable
3. QA + Monitoring Checklist     - Launch deliverable
```

### Learning CC (4 Key Artifacts)

```
1. Keyword Universe              - All keywords by intent bucket
2. Page Map                      - Every keyword → page mapping
3. Master URL Sheet              - NON-NEGOTIABLE artifact
4. Redirect Map                  - old → new for every URL change
```

---

## 5. POTENTIAL OUTCOMES

### Success Outcomes

| Outcome | Claude | Codex | Learning | Learning CC |
|---------|--------|-------|----------|-------------|
| **SUCCESS** terminal | ✓ | ✓ | Implicit | Implicit |
| Rankings preserved | ✓ | ✓ | ✓ | ✓ |
| Backlinks transferred | ✓ | ✓ | ✓ | ✓ |
| CWV targets met | ✓ | ✓ | ✓ | ✓ |
| Site live and indexable | ✓ | ✓ | ✓ | ✓ |

### Failure Outcomes

| Outcome | Claude | Codex | Learning | Learning CC |
|---------|--------|-------|----------|-------------|
| **FAILURE** terminal | ✓ | ✓ | N/A | N/A |
| Max retries exceeded | ✓ | ✓ | N/A | N/A |
| Critical error | ✓ | ✓ | N/A | N/A |

### Escalation Outcomes

| Outcome | Claude | Codex | Learning | Learning CC |
|---------|--------|-------|----------|-------------|
| **ESCALATE** terminal | ✓ | ✓ | N/A | N/A |
| Human input required | ✓ | ✓ | Always human | Always human |
| Blocking issue | ✓ | ✓ | N/A | N/A |

### Risk Outcomes (Partial Failure Modes)

| Risk | Mitigation |
|------|------------|
| Ranking drops | URL stability, 1:1 redirects, monitoring |
| Soft-404 spam | Avoid homepage sink pattern |
| Index bloat | noindex staging, handle WP ghost URLs |
| Performance regression | CWV budgets, baseline comparison |
| Conversion regression | Track GA4, test CTAs, accessibility |
| Stagnation | CMS for non-technical editors |

---

## 6. PHASE-BY-PHASE COMPARISON

### Phase 0: Lock Key Decisions

| Process | Included? | Content |
|---------|-----------|---------|
| Claude | ✓ (Intake) | Domain, city, business type, lead pages |
| Codex | ✓ (Intake) | Domain, business type, CMS need, target stack |
| Learning | ✓ (Phase 0) | URL Policy, Editing Workflow, Launch Scope |
| Learning CC | ✗ | Starts at Phase 1 (no explicit decision locking) |

### Phase 1: Keyword Strategy

| Process | Sub-Tasks |
|---------|-----------|
| Claude | build_universe → competitor_check → page_map → scoring → gate |
| Codex | Single node: universe + competitor + cluster + page map + priorities |
| Learning | Build Universe → Competitor Check → Page Map + Scoring |
| Learning CC | Build Universe → Competitor Check → Create Page Map |

### Phase 2: URL Mapping

| Process | Sub-Tasks |
|---------|-----------|
| Claude | crawl (parallel) + gsc (parallel) + backlinks (parallel) → master_sheet → gate |
| Codex | Single node: crawl + GSC + backlinks + classify + ghost URLs + master sheet |
| Learning | Crawl + Authority Signals → Master Sheet |
| Learning CC | Crawl + Export → GSC Export → Master URL Sheet |

### Phase 3: Future State Architecture

| Process | Sub-Tasks |
|---------|-----------|
| Claude | url_structure → consolidations → vercel_redirects → ghost_urls → gate |
| Codex | Single node: URL structure + consolidation + redirect map + ghost URLs + media |
| Learning | Define Sitemap → Redirect Map → Vercel Implementation |
| Learning CC | URL Decisions → Redirect Map → Handle WP Ghost URLs |

### Phase 4: Build

| Process | Sub-Tasks |
|---------|-----------|
| Claude | repo_setup → cms_decision → content_migrate → staging_deploy → gate |
| Codex | Single node: repo + branches + CMS + staging + content parity |
| Learning | Repo + Branching → Content System → Content Parity |
| Learning CC | GitHub Repo → Next.js Build → Content System |

### Phase 5: Technical SEO

| Process | Sub-Tasks |
|---------|-----------|
| Claude | headings_audit → metadata_audit → schema_impl → gate |
| Codex | Single node: H1 + titles/meta + canonicals + robots/sitemap + schema |
| Learning | Metadata + Canonicals → Schema → Sitemaps/Robots |
| Learning CC | Metadata → Canonicals → Schema |

### Phase 6: Performance / CWV

| Process | Sub-Tasks | Targets |
|---------|-----------|---------|
| Claude | baseline → budget → optimizations → staging_test → gate (retry) | LCP ≤2.5s, INP ≤200ms, CLS ≤0.1 |
| Codex | Single node: baseline + budgets + tactics | Same |
| Learning | Baseline → Budget → Tactics | Same |
| Learning CC | Baseline → Budgets → Image/LCP Optimization | Same |

### Phase 7: QA + Launch

| Process | Sub-Tasks |
|---------|-----------|
| Claude | seo_crawl (parallel) + redirects_test (parallel) + tracking_verify (parallel) → gate → wp_freeze → push_redirects → dns_swap → validation → sitemap_submit |
| Codex | Single node: SEO QA + redirect validation + tracking QA + launch runbook |
| Learning | SEO QA → Tracking QA → Cutover + Monitoring |
| Learning CC | SEO QA → Verify Redirects → Launch Cutover |

### Phase 8: Post-Launch

| Process | Sub-Tasks |
|---------|-----------|
| Claude | new_pages → internal_links → local_trust → monitoring |
| Codex | Single node: GSC monitoring + internal linking + content pipeline |
| Learning | Missing Pages → Internal Links → Local Trust + Ongoing Ops |
| Learning CC | Missing Pages → Internal Linking → Local Trust Blocks |

---

## 7. NUANCED DIFFERENCES

### 1. Decision Locking

| Process | Approach |
|---------|----------|
| **Claude** | Implicit in Intake node - gathers info but doesn't explicitly "lock" |
| **Codex** | Implicit in Intake - captures CMS need and target stack early |
| **Learning** | **Explicit Phase 0** with 3 decisions: URL Policy, Editing Workflow, Launch Scope |
| **Learning CC** | **No Phase 0** - assumes decisions are pre-made or handled inline |

### 2. WP Ghost URL Handling

| Process | Approach |
|---------|----------|
| **Claude** | Must_not: "Ignore WordPress ghost URLs" |
| **Codex** | Explicit policy in Phase 3: "noindex/redirect/removal policy" |
| **Learning** | "Pitfall: WordPress Ghost URLs" as explicit edge case |
| **Learning CC** | Phase 3 sub-task: "Handle WordPress Ghost URLs" with options |

### 3. Media/Asset URL Preservation

| Process | Explicit? |
|---------|-----------|
| **Claude** | Not explicitly mentioned |
| **Codex** | ✓ "Preserve or redirect indexed media URLs (especially `/wp-content/uploads/...`)" |
| **Learning** | ✓ "Pitfall: Media URL Preservation" as explicit risk |
| **Learning CC** | Not explicitly mentioned |

### 4. Accessibility + Conversion

| Process | Explicit? |
|---------|-----------|
| **Claude** | Not explicitly mentioned |
| **Codex** | Mentioned in tracking QA |
| **Learning** | ✓ "Pitfall: Accessibility + Conversion Regression" |
| **Learning CC** | "Trust Blocks" cover conversion but not accessibility |

### 5. Rollback Planning

| Process | Explicit? |
|---------|-----------|
| **Claude** | ✓ launch_manifest.json includes rollback plan |
| **Codex** | ✓ launch_runbook.md with rollback plan |
| **Learning** | Implicit in cutover sequence |
| **Learning CC** | Not explicitly mentioned |

### 6. Post-Launch Monitoring Duration

| Process | Specification |
|---------|---------------|
| **Claude** | Not specified |
| **Codex** | ✓ "30-day monitoring + triage plan" |
| **Learning** | "Monitor crawl errors and index coverage" |
| **Learning CC** | Not specified |

---

## 8. WHEN TO USE EACH PROCESS

### Use Claude Brain When:
- You need **automated execution** with explicit validation gates
- You want **granular control** over each sub-task
- You have **parallel data collection** needs (tributary nodes)
- You need **retry logic** at each validation point
- The workflow should **fail fast** with clear escalation paths

### Use Codex Brain When:
- You prefer **compact, phase-level** organization
- You want **more deliverables** documented upfront
- You need **inline flexibility** within phases
- The team is comfortable with **less explicit gates**
- You want a **simpler node structure** to maintain

### Use Learning Procedural Map When:
- You're **training or onboarding** team members
- You need **deep "why" documentation** for every step
- You want to understand **conceptual dependencies**
- The process requires **human judgment** at each step
- You're building **organizational knowledge**

### Use Learning CC Map When:
- You need a **streamlined execution checklist**
- The team already knows the decisions (no Phase 0 needed)
- You want **operational focus** over conceptual depth
- The **Master URL Sheet** is your primary artifact
- You prefer **fewer nodes** to track

---

## 9. SUMMARY MATRIX

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PROCESS SELECTION MATRIX                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  AUTOMATION LEVEL                                                           │
│  ════════════════                                                           │
│  High ◄─────────────────────────────────────────────────────────────► Low   │
│       │         │              │              │                             │
│       ▼         ▼              ▼              ▼                             │
│    Claude    Codex         Learning        Learning                         │
│    Brain     Brain         Procedural      CC                               │
│                                                                             │
│  GRANULARITY                                                                │
│  ═══════════                                                                │
│  Fine ◄─────────────────────────────────────────────────────────────► Coarse│
│       │         │              │              │                             │
│       ▼         ▼              ▼              ▼                             │
│    Claude    Learning       Learning       Codex                            │
│    Brain     Procedural     CC             Brain                            │
│                                                                             │
│  DOCUMENTATION DEPTH                                                        │
│  ══════════════════                                                         │
│  Deep ◄─────────────────────────────────────────────────────────────► Light │
│       │         │              │              │                             │
│       ▼         ▼              ▼              ▼                             │
│    Learning  Learning       Codex          Claude                           │
│    Concept   Procedural     Brain          Brain                            │
│                                                                             │
│  EXPLICIT VALIDATION                                                        │
│  ═══════════════════                                                        │
│  Many Gates ◄────────────────────────────────────────────────────► No Gates │
│       │         │              │              │                             │
│       ▼         ▼              ▼              ▼                             │
│    Claude    Codex         Learning        Learning                         │
│    Brain     Brain (inline) Procedural     CC                               │
│    (8 gates)                                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. RECOMMENDATION

**For Automated Agent Execution:** Use **Claude Brain** (most gates, clearest failure paths)

**For Comprehensive Documentation:** Use **Codex Brain** (most deliverables, inline flexibility)

**For Team Knowledge Building:** Use **Learning Procedural Map** (deepest why/how documentation)

**For Quick Operational Reference:** Use **Learning CC Map** (streamlined, action-focused)

**Best Practice:** Use Learning maps for training → Convert to Brain format for automation
