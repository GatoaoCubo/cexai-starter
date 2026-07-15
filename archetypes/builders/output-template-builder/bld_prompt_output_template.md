---
kind: instruction
id: bld_instruction_output_template
pillar: P03
llm_function: REASON
purpose: Step-by-step production process for output_template
pattern: 3-phase pipeline (research -> compose -> validate)
quality: null
title: "Instruction Output Template"
version: "1.0.0"
author: n03_builder
tags:
  - "output_template"
  - "builder"
  - "examples"
tldr: "Golden and anti-examples for output_template construction, demonstrating the reflexive-vs-broader usage split and the 3-way naming drift resolution."
domain: "output_template construction"
created: "2026-07-07"
updated: "2026-07-07"
8f: "F4_reason"
keywords:
  - "output_template construction"
  - "instruction output template"
  - "reflexive iso9"
  - "recurring output document"
  - "output_template"
  - "builder"
  - "examples"
  - "bld_output_template_[a-z][a-z0-9_]+"
  - "naming discrepancy"
  - "related artifacts"
density_score: 0.88
related:
  - bld_knowledge_card_output_template
  - bld_schema_output_template
  - p10_lr_output_template_builder
  - bld_instruction_kind
  - p11_qg_output_template
---
# Instructions: How to Produce an output_template
## Phase 1: RESEARCH
1. Identify WHICH usage this instance is: reflexive (a NEW kind-builder's own ISO#9,
   `bld_output_{{kind}}.md`) or broader (a recurring output document some nucleus will
   fill repeatedly -- README section, config template, report shell)
2. For the reflexive case: read that kind's OWN `bld_schema_{{kind}}.md` first -- every
   field in the reflexive output template MUST exist in that schema; template derives,
   never invents
3. For the broader case: identify the CONSUMING nucleus and the recurring document's
   real shape by finding a sibling instance if one exists (Grep `kind: output_template`
   under `N0X_*/P05_output/`) -- do not invent structure from nothing
4. Check whether the artifact is meant to be a genuine BLANK template (fill-in-the-blank,
   like `output_brand_config.md`) or a completed REPORT of what was produced (like
   `output_orchestration_audit.md`) -- both are real corpus usages; state which explicitly
5. Check existing output_templates via brain_query [IF MCP] or `Grep` for the same
   domain -- avoid duplicating an existing template
6. Confirm `depends_on` stays `[]` -- fixed empty per kinds_meta.json, never add a dependency
## Phase 2: COMPOSE
1. Read SCHEMA.md (`bld_schema_output_template.md`) -- source of truth for both usages
   and the 3-way naming-drift resolution (Convention A/B/C vs the canonical pattern)
2. Read OUTPUT_TEMPLATE.md (`bld_output_output_template.md`) -- fill the reflexive shape
   following SCHEMA constraints exactly
3. Fill frontmatter: id (canonical `bld_output_template_{{kind}}` for reflexive; one of
   the 3 documented conventions -- author's choice, disclosed -- for broader usage), kind,
   pillar (P05), version, created/updated, quality: null, depends_on: []
4. Write the body: for reflexive usage, a fenced `{{var}}`-filled TEMPLATE block; for
   broader usage, a `## Summary`/`## Instructions` block plus the recurring document's
   own real shape (a fenced YAML block, a table, a flow diagram -- whatever the sibling
   instances in that domain actually use)
5. Write the "How to use" / "Instructions" block: who consumes this template and when
   (mirrors the real corpus's `### How to use` ROLE/ACT convention)
6. Write the Related Artifacts section: at least 1 upstream and 1 downstream/sibling wikilink
7. Verify body is within 8192 bytes (per `kinds_meta.json` `max_bytes`)
## Phase 3: VALIDATE
1. Check QUALITY_GATES.md (`bld_eval_output_template.md`) -- apply each gate manually
2. HARD gates (all must pass):
   - YAML frontmatter parses without errors
   - kind == output_template
   - pillar == P05
   - depends_on == [] (never add without a kinds_meta.json edit -- out of scope)
   - quality == null
   - id matches canonical pattern `^bld_output_template_[a-z][a-z0-9_]+$` for
     NEW reflexive-usage artifacts (this gate is FORWARD-ONLY; it does not retroactively
     invalidate the 18 pre-existing broader-usage instances, which predate this builder)
3. SOFT gates (score each against QUALITY_GATES.md):
   - the usage (reflexive vs broader) is stated explicitly, not left ambiguous
   - a genuine blank-template instance uses `{{var}}` markers, not invented example values
   - a report-shaped instance is clearly labeled as a completed output, not a blank scaffold
   - naming convention choice (for broader usage) is disclosed against the 3 documented options, not silently picked
   - at least one Related Artifacts wikilink resolves to a REAL existing artifact
4. Cross-check scope boundaries:
   - is this truly output_template, not a prompt_template (LLM-facing prompt)?
   - not an abstract response_format (CONSTRAIN-time spec, no fill-in-the-blank body)?
   - not a formatter (GOVERN-time runtime transform of already-produced content)?
5. If score < 8.0: revise in the same pass before outputting

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_output_template]] | upstream | 0.40 |
| [[bld_schema_output_template]] | downstream | 0.38 |
| [[p10_lr_output_template_builder]] | downstream | 0.34 |
| bld_instruction_kind | sibling (reflexive-case source) | 0.32 |
| [[p11_qg_output_template]] | downstream | 0.30 |
