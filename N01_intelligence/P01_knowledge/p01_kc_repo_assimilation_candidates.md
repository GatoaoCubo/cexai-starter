---
id: p01_kc_repo_assimilation_candidates
kind: knowledge_card
kc_type: domain_kc
pillar: P01
nucleus: N01
title: "REPO_ASSIMILATION Candidate Catalog -- Architecture/DDD + AI-Engineering (2026-06-03)"
version: "1.0.0"
created: "2026-06-03"
updated: "2026-06-03"
author: "n01_intelligence"
domain: "repo_assimilation"
quality: null
tags: [repo_assimilation, architecture, ddd, ai_engineering, discovery]
tldr: "14 public GitHub repos ranked by assimilability across architecture/DDD + AI-eng; top 6 are MIT/Apache-2.0 (provisional). LGPL excluded from Wave 3. Licenses unverified -- Wave 2 compliance_checklist is HARD GATE before assimilation."
when_to_use: "Load when selecting repos for Wave 2 (license gate) or Wave 3 (assimilation). Source of truth for candidate ranking in REPO_ASSIMILATION mission."
keywords: [repo_assimilation, clean_architecture, DDD, prompt_engineering, llm_course]
long_tails:
  - "which github repos can CEX legally assimilate for clean architecture and DDD patterns"
  - "public ai engineering repositories with permissive licenses for knowledge distillation"
axioms:
  - "NEVER assimilate a repo whose license is not confirmed GREEN (MIT/Apache-2.0/BSD/CC-BY) by Wave 2 compliance_checklist."
  - "ALWAYS attribute source repo + author + license in every derived artifact (field: source, attribution, license)."
  - "IF license is LGPL/GPL/AGPL -> mark RED, exclude from Wave 3; revisit only if concept-only (no code reproduction)."
linked_artifacts:
  primary: null
  related: [compliance_checklist_repo_licenses, p01_kc_clean_arch_ddd_in_cex, spec_n01_repo_assimilation]
density_score: 0.90
data_source: "firecrawl live search 2026-06-03 + decision_manifest_repo_assimilation.yaml"
related:
  - p01_kc_influencer_directory_global
  - p01_kc_kind_gap_synthesis
---

# REPO_ASSIMILATION Candidate Catalog -- Architecture/DDD + AI-Engineering

## Quick Reference

```yaml
topic: repo_assimilation_candidates
scope: "architecture/DDD + AI-engineering -- 2 domains (D2 from manifest)"
owner: n01_intelligence
criticality: high
mission: REPO_ASSIMILATION
wave: "1 of 4 (discovery)"
gathered: "2026-06-03 via firecrawl live search"
license_status: "PROVISIONAL -- Wave 2 compliance_checklist is HARD GATE"
shortlist_target: "3-5 GREEN repos for Wave 3 assimilation (D3)"
```

## Candidate Catalog (Ranked)

Assimilability = HIGH (execute Wave 3 on GREEN) | MEDIUM (verify before Wave 3) | LOW (likely excluded).
License column is PROVISIONAL. Wave 2 verifies each before any assimilation proceeds.

### Tier 1 -- HIGH Assimilability (recommend for Wave 3 shortlist)

| # | Repo | Domain | Stars | License (provisional) | Content type | Assimilability | Why assimilable |
|---|------|--------|-------|-----------------------|-------------|----------------|-----------------|
| 1 | [ardalis/CleanArchitecture](https://github.com/ardalis/CleanArchitecture) | architecture | 18.2k | MIT | template + patterns (.NET) | HIGH | Canonical Clean Arch template; direct 1:1 with CEX pillar structure; Steve Smith is cited authority |
| 2 | [Sairyss/domain-driven-hexagon](https://github.com/Sairyss/domain-driven-hexagon) | DDD | 14.7k | MIT | patterns + examples (TS) | HIGH | Best single-repo DDD reference; aggregates, value objects, events with code samples |
| 3 | [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer) | system-design | ~280k | CC-BY-4.0 | guide | HIGH | Largest public system-design guide; CC-BY = attribute only (no code restriction) |
| 4 | [dair-ai/Prompt-Engineering-Guide](https://github.com/dair-ai/Prompt-Engineering-Guide) | AI-engineering | 55k+ | MIT | guide + papers | HIGH | Definitive prompt-engineering reference; covers CoT/RAG/agents; maps to N01+N03 builders |
| 5 | [mlabonne/llm-course](https://github.com/mlabonne/llm-course) | AI-engineering | 46k+ | Apache-2.0 | course (notebooks) | HIGH | End-to-end LLM pipeline: training -> inference -> deployment; maps to N03+N05 scope |
| 6 | [ai-boost/awesome-harness-engineering](https://github.com/ai-boost/awesome-harness-engineering) | AI-engineering | -- | verify | awesome-list | HIGH | CEX-aligned: tools/evals/MCP/orchestration; mirrors CEX P04+P07+P12 pillars directly |

### Tier 2 -- MEDIUM Assimilability (verify license + scope fit)

| # | Repo | Domain | Stars | License (provisional) | Content type | Assimilability | Notes |
|---|------|--------|-------|-----------------------|-------------|----------------|-------|
| 7 | [promptslab/Awesome-Prompt-Engineering](https://github.com/promptslab/Awesome-Prompt-Engineering) | AI-engineering | -- | Apache-2.0 (verify) | awesome-list | MEDIUM | Good catalog but lower curation density than dair-ai guide |
| 8 | [heynickc/awesome-ddd](https://github.com/heynickc/awesome-ddd) | DDD | -- | verify | awesome-list (DDD/CQRS/ES) | MEDIUM | Community-curated DDD links; good as secondary source, not primary |
| 9 | [jim-schwoebel/awesome_ai_agents](https://github.com/jim-schwoebel/awesome_ai_agents) | AI-engineering | -- | MIT (verify) | awesome-list | MEDIUM | Broad coverage; overlaps CEX agent taxonomy; check maintenance date |
| 10 | [Jenqyang/Awesome-AI-Agents](https://github.com/Jenqyang/Awesome-AI-Agents) | AI-engineering | -- | verify | awesome-list | MEDIUM | Newer list; license unconfirmed; lower signal than ranked alternatives |
| 11 | [ai-boost/awesome-prompts](https://github.com/ai-boost/awesome-prompts) | AI-engineering | -- | verify | prompts | MEDIUM | Prompt collection; useful for few_shot_example extraction; verify license |
| 12 | [baratgabor/MyWarehouse](https://github.com/baratgabor/MyWarehouse) | architecture + DDD | -- | verify | sample (.NET) | MEDIUM | Clean Arch + DDD sample; smaller scope than ardalis; good for pattern cross-check |
| 13 | [TuralSuleymani/the-real-DDD-CQRS-CleanArchitecture](https://github.com/TuralSuleymani/the-real-DDD-CQRS-CleanArchitecture) | architecture + DDD | -- | verify | example (20+ patterns) | MEDIUM | High pattern density (CQRS+ES+Outbox+Saga); useful if license GREEN |

### Tier 3 -- LOW Assimilability (likely excluded from Wave 3 round 1)

| # | Repo | Domain | Stars | License (provisional) | Content type | Assimilability | Reason |
|---|------|--------|-------|-----------------------|-------------|----------------|--------|
| 14 | [abpframework/abp](https://github.com/abpframework/abp) | DDD | 14.3k | LGPL-3.0 | framework | LOW | LGPL = YELLOW/RED per D4; copyleft risk for INPI product; exclude round 1 unless concept-only |

## Domain Summary

| Domain | Tier-1 candidates | Tier-2 candidates | Tier-3 (excluded round 1) |
|--------|------------------|------------------|--------------------------|
| architecture / system-design | 2 (ardalis, donnemartin) | 2 (baratgabor, Tural) | 0 |
| DDD | 1 (Sairyss) | 1 (heynickc) | 1 (abp, LGPL) |
| AI-engineering | 3 (dair-ai, mlabonne, ai-boost/harness) | 4 (promptslab, jim-schwoebel, Jenqyang, ai-boost/prompts) | 0 |
| **Total** | **6** | **7** | **1** |

## Pipeline Notes

- Licenses are PROVISIONAL (firecrawl search 2026-06-03). Wave 2 compliance_checklist verifies
  each repo's LICENSE file directly -- do NOT assimilate code before Wave 2 GREEN verdict.
- Scope locked by manifest D2: arquitetura_ddd + ai_engineering. system-design (donnemartin)
  included as adjacent to architecture (direct overlap with DDD/hexagonal context).
- D3 profundidade: focado -- Wave 3 targets 3-5 repos GREEN from Tier 1. If >= 5 Tier-1 pass
  GREEN, prioritize by stars + content density (ardalis > Sairyss > dair-ai > mlabonne > ai-boost/harness).
- LGPL guard: abpframework/abp LGPL-3.0 -> excluded Wave 3 round 1 (D4 green_only_strict).
  Revisit only if Wave 2 confirms concept extraction (no code copy) remains safe.
- awesome-lists: lower priority than curated guides/templates; useful as secondary source for
  few_shot_example extraction in Wave 3 (N04).

## Golden Rules

- NEVER pass a repo to Wave 3 without Wave 2 compliance_checklist GREEN verdict per that repo.
- ALWAYS cite source repo + author + license in every derived artifact (field: source/attribution/license).
- IF stars == "--" and license unconfirmed -> do Wave 2 before committing to Tier ranking.
- PREFER content-type: template|patterns|guide|course over awesome-list for primary Wave 3 candidates.
- NEVER reproduce code from non-GREEN repos; concept assimilation is permissive, code is not.

## Flow

```text
[firecrawl discover] -> [rank by domain + content + stars]
         |
         v
[kc_repo_assimilation_candidates] <- THIS ARTIFACT (Wave 1)
         |
         v
[compliance_checklist_repo_licenses] (Wave 2 -- HARD GATE)
         |
    GREEN? YES -> [Wave 3: N04 assimilation per repo]
    GREEN? NO  -> [archive, exclude from Wave 3]
         |
         v
[kc_assimilated_{repo}] + [p04_skill_{repo}_*] + [pattern_{repo}_*]
```

## Comparativo -- Content Type vs Assimilation Value

| Content type | Wave 3 artifact fit | Example | Stars bias |
|-------------|---------------------|---------|------------|
| template + patterns | pattern, skill, few_shot_example | ardalis/CleanArchitecture | HIGH |
| guide + papers | knowledge_card, prompt_template | dair-ai/Prompt-Engineering-Guide | HIGH |
| course (notebooks) | skill, few_shot_example, knowledge_card | mlabonne/llm-course | HIGH |
| awesome-list | knowledge_card (catalog), few_shot_example | heynickc/awesome-ddd | MEDIUM |
| framework | pattern (concept-only) | abpframework/abp | LOW (copyleft) |
| sample | pattern, skill | baratgabor/MyWarehouse | MEDIUM |

## References

- Decision manifest: `.cex/runtime/decisions/decision_manifest_repo_assimilation.yaml`
- Mission spec: `_docs/specs/spec_n01_repo_assimilation.md`
- Wave 2 artifact (downstream): `N01_intelligence/P11_feedback/compliance_checklist_repo_licenses.md`
- ardalis/CleanArchitecture: https://github.com/ardalis/CleanArchitecture
- Sairyss/domain-driven-hexagon: https://github.com/Sairyss/domain-driven-hexagon
- donnemartin/system-design-primer: https://github.com/donnemartin/system-design-primer
- dair-ai/Prompt-Engineering-Guide: https://github.com/dair-ai/Prompt-Engineering-Guide
- mlabonne/llm-course: https://github.com/mlabonne/llm-course
- Data gathered: firecrawl live search 2026-06-03 + decision_manifest_repo_assimilation.yaml


## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| p04_browser_awesome_list | downstream | 0.32 |
| p02_agent_n03_sdk_test | downstream | 0.22 |
| p03_sp_engineering_nucleus | downstream | 0.21 |
| p12_dr_engineering | downstream | 0.21 |
| p01_kc_prompt_engineering_best_practices | sibling | 0.21 |
| [[p01_kc_influencer_directory_global]] | sibling | 0.20 |
| [[p01_kc_kind_gap_synthesis]] | sibling | 0.20 |
| research_prior_art_landscape | sibling | 0.20 |
| p02_iso_n03 | downstream | 0.19 |
| p01_kc_engineering_best_practices | sibling | 0.19 |
