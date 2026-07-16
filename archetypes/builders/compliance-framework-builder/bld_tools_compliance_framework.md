---
kind: tools
id: bld_tools_compliance_framework
pillar: P04
llm_function: CALL
purpose: Tools available for compliance_framework production
quality: null
title: "Tools Compliance Framework"
version: "1.1.0"
author: n05_ops
tags: [compliance_framework, builder, tools]
tldr: "Tools available for compliance_framework production"
domain: "compliance_framework construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F5_call"
keywords: [compliance_framework construction, tools compliance framework, compliance_framework, builder, tools, production tools, validation tools, external references, management systems, international association]
density_score: 0.85
related:
  - bld_knowledge_card_compliance_framework
  - bld_tools_vad_config
  - bld_tools_edit_format
  - bld_tools_search_strategy
  - kc_compliance_framework
---
## Production Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_compile.py | Compiles compliance policies into executable rules | During framework deployment |
| cex_score.py | Scores compliance against regulatory benchmarks | Post-policy evaluation |
| cex_retriever.py | Fetches external regulatory data | When updating policy databases |
| cex_doctor.py | Diagnoses policy conflicts and errors | During policy drafting |
| cex_8f_runner.py | Automates template creation for compliance documents | On-demand |
| cex_retriever.py | Analyzes risk exposure based on policy gaps | Quarterly audits |

## Validation Tools
| Tool | Purpose | When |
|------|---------|------|
| val_checker.py | Validates input data formats | Pre-processing |
| val_mapper.py | Maps internal policies to external standards | During alignment checks |
| val_reporter.py | Generates validation discrepancy reports | Post-validation |
| val_simulator.py | Simulates compliance scenarios | Testing phases |

## External References
- EU AI Act text: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689
- GDPR text: https://gdpr.eu/tag/gdpr/
- NIST AI RMF: https://airc.nist.gov/Home
- ISO/IEC 42001:2023 AI Management Systems standard
- OneTrust / TrustArc: GRC platforms for automated compliance mapping
- IAPP: International Association of Privacy Professionals -- regulatory guidance

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_card_compliance_framework]] | upstream | 0.32 |
| [[bld_tools_vad_config]] | sibling | 0.30 |
| [[bld_tools_edit_format]] | sibling | 0.30 |
| [[bld_tools_search_strategy]] | sibling | 0.29 |
| [[kc_compliance_framework]] | upstream | 0.29 |
