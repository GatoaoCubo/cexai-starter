---
kind: tools
id: bld_tools_llm_evaluation_scenario
pillar: P04
llm_function: CALL
purpose: Tools available for llm_evaluation_scenario production
quality: null
title: "Tools LLM Evaluation Scenario"
version: "1.0.0"
author: n06_wave7
tags: [llm_evaluation_scenario, builder, tools, helm]
tldr: "Tools available for llm_evaluation_scenario production"
domain: "llm_evaluation_scenario construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [llm_evaluation_scenario construction, tools llm evaluation scenario, llm_evaluation_scenario, builder, tools, helm, github.com/stanford-crfm/helm, github.com/foundation-model-stack/fms-fmeval, crfm.stanford.edu/helm/latest/, production tools]
density_score: 0.85
related:
  - bld_knowledge_card_llm_evaluation_scenario
  - llm-evaluation-scenario-builder
  - n00_llm_evaluation_scenario_manifest
  - bld_instruction_llm_evaluation_scenario
  - bld_collaboration_llm_evaluation_scenario
---
## Production Tools
| Tool                 | Purpose                                    | When                        |
|----------------------|--------------------------------------------|-----------------------------|
| cex_compile.py       | Compile scenario YAML from Markdown        | After F6 PRODUCE            |
| cex_score.py         | Peer-review quality scoring                | F7 GOVERN                   |
| cex_retriever.py     | Find similar existing scenarios            | F3 INJECT / duplicate check |
| cex_doctor.py        | Builder health diagnostics                 | Pre-build validation        |
| cex_doctor.py     | Schema compliance check (H01-H08 gates)    | F7 GOVERN                   |
| cex_query.py         | TF-IDF discovery of related eval kinds     | F5 CALL                     |

## Validation Tools
| Tool                   | Purpose                                 | When                     |
|------------------------|-----------------------------------------|--------------------------|
| helm_validate.py       | HELM-spec compliance (canonical check)  | Post-compose             |
| canonicalization_test  | Verify normalization function on 10 samples | Before F8 COLLABORATE |
| dataset_license_check  | Validate upstream dataset license       | Phase 1 RESEARCH         |
| token_cost_estimate    | Compute prompt + completion token budget | Phase 2 COMPOSE         |

## External References
- HELM Python library: `github.com/stanford-crfm/helm` (scenario runner, adapter, metrics)
- IBM fms-fmeval: `github.com/foundation-model-stack/fms-fmeval` (enterprise extensions)
- HELM leaderboard API: `crfm.stanford.edu/helm/latest/` (scenario registry, run results)
- MLCommons AILuminate runner: compatible HELM runner for safety scenarios
- BigBench data loader: 204-task JSON format, compatible with HELM adapter

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_card_llm_evaluation_scenario]] | upstream | 0.54 |
| [[llm-evaluation-scenario-builder]] | downstream | 0.45 |
| [[n00_llm_evaluation_scenario_manifest]] | downstream | 0.41 |
| [[bld_instruction_llm_evaluation_scenario]] | upstream | 0.37 |
| [[bld_collaboration_llm_evaluation_scenario]] | downstream | 0.32 |
