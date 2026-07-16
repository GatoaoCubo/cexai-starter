---
id: p01_kc_eval2_ambiguity_doctrine
kind: knowledge_card
kc_type: meta_kc
pillar: P01
version: 1.0.0
created: 2026-06-12
updated: 2026-06-12
title: "Eval2 Labeling Ambiguity Doctrine -- 12 Classes"
domain: "intent-routing"
subdomain: "label-council disambiguation"
tags: [eval2, ambiguity, intent-routing, label-doctrine, ft-dataset]
quality: null
axioms:
  - "ALWAYS: kinds_meta.json pillar beats compiler table; compiler supplies nucleus."
  - "ALWAYS: explicit N0X: pin overrides all routing (except N07-never-builds)."
  - "IF 0 artifact nouns + status/dispatch context -> resolvable:false, kind=null."
  - "NEVER: split same-pillar bundle; pick umbrella kind + note alternates."
  - "IF FT config -> N03; FT curation -> N04; FT eval output -> N05."
keywords: [ambiguity-doctrine, label-council, multi-valid, disambiguation, eval2]
long_tails: [eval2 ambiguity classes, kind assignment doctrine, CEX intent routing ambiguity]
tldr: "12 classes cover all 49 ambiguous eval2 rows (35 raw patterns consolidated); each has a single-pick rule and multi-valid exception condition."
related:
  - p03_pc_cex_universal
---

## The 12 Ambiguity Classes

| ID | Class | Single-Pick Rule | Multi-Valid When |
|----|-------|-----------------|-----------------|
| AC-01 | Unresolvable | 0 artifact nouns + status/shell/dispatch -> resolvable:false, kind=null | Commit msg names typed deliverable -> route that kind |
| AC-02 | Cross-pillar bundle | >=2 pillars -> N07 grid, kind=null, note dominant kinds | Composite commits with cross-pillar kinds -> dual rows |
| AC-03 | Same-pillar bundle | 1 pillar -> umbrella kind; 1 row; alternates in notes | Never multi-valid -- pick and note |
| AC-04 | Bare noun/no verb | Compiler V column default; fallback: noun=create, 'set up'=configure, eval phrasing=test | -- |
| AC-05 | N03 vs N05 | Kind doctrine beats domain pull; construction->N03; op/test/deploy/P09->N05 | Distinct P07/P11 deliverable also present |
| AC-06 | N02 vs N06 | Authorship/creative->N02; product/revenue/GTM->N06 | Both ownership types present (e.g. course narration + launch) |
| AC-07 | N04 vs N01/N03 | Research+analyze intent->N01; docs hardening->N04; artifact build->N03 | Ext repo assimilation: KC output(N04) + artifact output(N03) both valid |
| AC-08 | Pillar drift | kinds_meta pillar wins; compiler supplies nucleus; dedicated kind beats generic | -- |
| AC-09 | Nucleus pin | 'Task for N0X' / 'N0X:' prefix pins nucleus; accept unless N07-never-builds | -- |
| AC-10 | FT/data pipeline | FT config->N03; curation->N04; eval pairs->N05 | Parameterized teacher target (N01..N06) -> list all |
| AC-11 | Meta/archetype | bld_*->subject kind+N03; 'create kind_X'->artifact-of-X; self-describing->N03 | -- |
| AC-12 | Sin-lens audit | No named kind -> knowledge_card findings; nucleus from sin lens; verb=audit | No sin named -> N01 |

## Anti-Patterns

- AC-03: splitting same-pillar bundles -- pick umbrella, note alternates in 1 row
- AC-05: routing construction via domain nucleus over kind doctrine
- AC-08: treating compiler pillar as ground truth when kinds_meta disagrees
- AC-10: single-pick on parameterized teacher-distill targets (>=2 -> multi-valid)

## W2 Council Protocol

1. Match intent to AC-01..AC-12; apply single-pick rule
2. >=2 defensible tuples by doctrine -> multi-valid, ambiguous:true
3. AC-01 conditions -> resolvable:false, valid_set:[]

## References

- Raw sources: `_data/ft/eval2/_ambiguity_patterns.json` (35 patterns)
- JSONL: `_data/ft/eval2/eval2_taxonomy_notes.jsonl` (430 rows, 49 ambiguous)
- [[p03_pc_cex_universal]] -- canonical routing authority
- plan_better_eval_2026_06_12 -- parent mission plan
- Intent labeling standard: https://rasa.com/docs/rasa/training-data-format/
