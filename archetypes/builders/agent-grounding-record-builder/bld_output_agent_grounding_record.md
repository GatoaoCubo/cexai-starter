---
kind: output_template
id: bld_output_template_agent_grounding_record
pillar: P05
llm_function: PRODUCE
purpose: Canonical output structure for agent_grounding_record artifacts ready for F6 PRODUCE rendering
quality: null
title: "Agent Grounding Record -- Output Template"
version: "1.0.0"
author: wave7_n05
tags: [agent_grounding_record, builder, output_template]
tldr: "Fill-in template: frontmatter + inference block + model block + tool_calls + rag_chunks + hashes + audit summary"
domain: "agent_grounding_record construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [produce rendering, agent_grounding_record construction, fill-in template, inference block, model block, audit summary, agent_grounding_record]
density_score: 0.85
---
# Agent Grounding Record -- Output Template
## Usage
Replace every `{{PLACEHOLDER}}` with the actual value from the inference session.
Sections marked `[OPTIONAL]` may be omitted if not applicable, but MUST be explicitly
set to null rather than silently omitted for C2PA and model-signature fields.
## TEMPLATE START
```markdown
---
kind: agent_grounding_record
id: p10_gr_{{INFERENCE_ID_PREFIX}}
pillar: P10
llm_function: PRODUCE
purpose: Per-inference provenance record for {{SHORT_DESCRIPTION_OF_INFERENCE_TASK}}
quality: null
title: "Grounding Record -- {{SHORT_DESCRIPTION_OF_INFERENCE_TASK}}"
```
## TEMPLATE END
## Rendering Notes
| Element              | Guidance                                                                          |
|----------------------|-----------------------------------------------------------------------------------|
| Tool table           | Sort by timestamp ascending; one row per invocation including failed calls        |
| RAG chunk table      | Sort by retrieval_score descending; include all retrieved chunks, not just cited  |
| output_hash          | Must be computed from raw bytes BEFORE any markdown formatting or truncation      |
| grounding_coverage_pct | Compute from actual claim analysis; document methodology in Coverage note      |
| Audit Summary        | Write for a human auditor, not just a machine parser -- prose is appropriate here |
| Byte budget          | Keep total artifact under 4096 bytes; truncate tables with full_trace_log_ref if needed |
