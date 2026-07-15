---
id: bld_output_domain_vocabulary
kind: output_template
pillar: P05
llm_function: PRODUCE
version: 1.0.0
quality: null
tags: [domain_vocabulary, template, output]
title: "Output Template: domain_vocabulary"
author: builder
tldr: "Domain Vocabulary prompt: output template, formatting rules, and structure"
8f: "F6_produce"
keywords: [output template, domain vocabulary prompt, formatting rules, and structure, domain_vocabulary, template, output, domain vocabulary, deprecated terms, old term]
density_score: 1.0
created: "2026-04-17"
updated: "2026-04-17"
related:
  - p01_kc_domain_vocabulary
  - bld_schema_domain_vocabulary
  - bld_qg_domain_vocabulary
  - domain-vocabulary-builder
  - bld_instruction_domain_vocabulary
---
# Output Template: domain_vocabulary
```markdown
---
id: dv_{{bounded_context_snake}}_vocabulary
kind: domain_vocabulary
pillar: P01
title: "{{BoundedContext}} Domain Vocabulary"
version: 1.0.0
quality: null
bounded_context: {{bounded_context}}
governed_agents: [{{agent_id_1}}, {{agent_id_2}}]
term_count: {{N}}
tags: [{{bounded_context}}, vocabulary, ubiquitous-language]
---

# {{BoundedContext}} Domain Vocabulary

## Overview
{{One sentence: what domain this vocabulary governs and why it exists.}}

## Terms

### {{TermName}}
| Field | Value |
|-------|-------|
| definition | {{canonical one-sentence definition}} |
| industry_standard | {{Evans DDD / NIST / ISO ref / "CEX-internal"}} |
| anti_patterns | [{{wrong_name_1}}, {{wrong_name_2}}] |
| status | active |
| replaces | null |

### {{TermName2}}
| Field | Value |
|-------|-------|
| definition | {{canonical definition}} |
| industry_standard | {{reference}} |
| anti_patterns | [{{wrong_names}}] |
| status | active |
| replaces | null |

## Deprecated Terms
| Old Term | Replaced By | Deprecated Date |
|----------|------------|-----------------|
| {{old}} | {{new}} | {{YYYY-MM-DD}} |

## Loading Instructions
Load this vocabulary at F2b SPEAK before producing any artifact in
the {{bounded_context}} bounded context.
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_domain_vocabulary]] | upstream | 0.47 |
| [[bld_schema_domain_vocabulary]] | downstream | 0.46 |
| [[bld_qg_domain_vocabulary]] | downstream | 0.45 |
| [[domain-vocabulary-builder]] | upstream | 0.45 |
| [[bld_prompt_domain_vocabulary]] | related | 0.43 |
