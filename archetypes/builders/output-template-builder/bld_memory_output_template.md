---
id: p10_lr_output_template_builder
kind: learning_record
pillar: P10
version: 1.0.0
created: 2026-07-07
updated: 2026-07-07
author: builder_agent
observation: "INAUGURAL record -- no prior output_template BUILDER exists (R-299, the first). Lessons extracted from the R-298 investigation (kind_manifest_n00.md) plus this scaffold's own direct full-corpus read of all 18 real instances, not from N accumulated review cycles. Flagged honestly, not presented as review-derived statistics."
pattern: "Three findings, verified against the live corpus (not inferred): (1) kinds_meta.json's naming field matches 0/18 real instances (3 conventions instead: p05_out_, {nucleus}_output_, and an R-298-undocumented {nucleus}_{name} no-marker variant, all 4 *_readme_*-titled); (2) 18/18 filenames are bare output_{{slug}}.md while every id adds a prefix -- id==filename-stem is FALSE 18/18 times, by corpus design; (3) real usage is NOT structurally uniform -- output_brand_config.md is a blank scaffold, output_orchestration_audit.md is a completed post-mortem, so 'template' is aspirational for about half the corpus."
evidence: "Extracted from kind_manifest_n00.md (Schema table's 'two conventions' claim -- found incomplete by this scaffold's own read, which found a 3rd), and direct reads of all 18 files matching kind: output_template under N0[2-7]_*/P05_output/ plus one false-positive (p08_cd_pubtriage_n06.md, kind: context_doc, confirmed by frontmatter read not grep alone). No live builder-review history exists yet."
confidence: 0.60
outcome: SUCCESS
domain: output_template
tags: [output-template, naming-drift, reflexive-iso9, iso-pattern-h02, inaugural]
tldr: "Inaugural record (no prior builder yet): kinds_meta's registered naming matches 0/18 real instances (3-way id drift + a 4th filename-vs-id mismatch axis), and roughly half the corpus is completed reports, not blank templates -- verify the usage before assuming either shape."
impact_score: 6.5
decay_rate: 0.08
agent_group: edison
keywords: [output_template, naming_drift, h02_id_pattern, reflexive_iso9, kinds_meta_registered_naming, filename_vs_id]
memory_scope: project
observation_types: [reference, project]
quality: null
title: "Memory Output Template"
8f: "F3_inject"
density_score: 0.87
llm_function: INJECT
related:
  - bld_schema_output_template
---
## Summary
output_template artifacts describe TWO distinct usages under one kind name, and the
kind's own OFFICIAL naming registration only covers the narrower of the two. Since this
is the FIRST output_template builder scaffold, there is no accumulated review history --
this record captures the landmines the R-298 investigation and this scaffold's own
corpus read already paid for, so future builds do not have to re-discover them empirically.
## Pattern
Three landmine categories (all three verified against real corpus files, not inferred):
1. **Registered naming covers only the reflexive case** -- `kinds_meta.json`'s `naming`
   field (`bld_output_template_{{kind}}.md`) is a perfect match for every kind-builder's
   own ISO#9 file (`bld_output_{{kind}}.md` carries `id: bld_output_template_{{kind}}`
   internally, confirmed across all 9 most-recently-scaffolded builders). It is a 0%
   match for the 18 real canonical-pillar instances, which use 3 further conventions
   instead. Adopting the registered pattern as canonical (per this builder's explicit
   mandate, register row R-299) means the H02 gate is intentionally FORWARD-ONLY: it
   governs new production, not a retroactive sweep of the 18 pre-existing files.
2. **id != filename-stem is the corpus NORM, not a defect, for this kind** -- 0/18 real
   instances have id equal to their filename stem (all filenames are bare
   `output_{{slug}}.md`; all ids add a nucleus or pillar prefix, or reorder tokens
   entirely). This is the OPPOSITE of field_manifest/approval_request, which both
   enforce id == filename stem as a hard rule. Do not import that rule here by habit --
   it would flag 18/18 real files as broken, which is not a meaningful signal.
3. **"Template" is aspirational, not descriptive, for about half the corpus** --
   `output_brand_config.md` is genuinely blank (every value is `""` or a placeholder
   default, meant to be filled). `output_orchestration_audit.md` and
   `output_cf_actions_and_distribution.md` are COMPLETED reports narrating what was
   already produced, with real dates and real counts -- not blank at all. A builder that
   assumes every output_template instance must contain `{{var}}` markers will
   misjudge roughly half the real corpus as malformed.
Additional real, source-documented behavior worth carrying into every output_template
this builder produces: `depends_on` is fixed EMPTY (`[]`) per kinds_meta.json -- this
is the one kind among its recently-scaffolded 2026-07-03 siblings (field_manifest,
approval_request, canonical_product, etc., all of which declare 1-3 dependencies) that
depends on NOTHING upstream. This should be preserved, not "improved" by inventing a
dependency this kind was never meant to carry.
## Anti-Pattern
1. Silently picking Convention B (`{nucleus}_output_{name}`, the 13/18 majority) and
   presenting it as "the" standard because it is most common -- this is EXACTLY the
   "silently bless the drift" failure mode register row R-299 explicitly warns against.
2. Enforcing "id MUST equal filename stem" on output_template by analogy with
   field_manifest/approval_request -- the corpus evidence says the opposite is true here.
3. Assuming a new output_template instance must be a blank `{{var}}`-filled scaffold --
   check whether the requesting nucleus actually wants a completed-report shape instead
   (both are real, both appear in the corpus, ask which one is wanted).
4. Adding a `depends_on` entry "for completeness" -- fixed empty by design; this would
   require an out-of-scope kinds_meta.json edit and contradicts the kind's own registration.
5. Treating the R-298 manifest's "two conventions" claim as exhaustive -- this scaffold's
   own direct read found a 3rd (Convention C, the `*_readme_*` no-marker variant);
   always re-verify a prior investigation's corpus claim against a fresh full read
   rather than citing it as closed.
## Context

## Builder Context

This ISO operates within the `output-template-builder` stack, one of the 300+
specialized builders in the CEX architecture. Each builder has 12 ISOs
covering model, prompt, knowledge, tools, output, schema, eval, architecture,
config, memory, feedback, and orchestration.

The builder loads ISOs via `cex_skill_loader.py` at pipeline stage F3
(Compose), merges them with relevant memory from `cex_memory_select.py`,
and produces artifacts that must pass the quality gate at F7 (Govern).

| Component | Purpose |
|-----------|---------|
| System prompt (model) | Identity and behavioral rules |
| Instruction (prompt) | Step-by-step procedure |
| Output template | Structural scaffold |
| Quality gate (eval) | Scoring rubric |
| Knowledge | Domain background + real mechanics |

## Reference

```yaml
id: p10_lr_output_template_builder
pipeline: 8F
scoring: hybrid_3_layer
target: 9.0
```

```bash
python _tools/cex_score.py --apply --verbose p10_lr_output_template_builder.md
```

## Properties

| Property | Value |
|----------|-------|
| Kind | `learning_record` |
| Pillar | P10 |
| Domain | output_template |
| Pipeline | 8F |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Target | 9.0+ |
| Density | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_output_template]] | upstream | 0.38 |
| [[bld_prompt_output_template]] | upstream | 0.36 |
| [[bld_schema_output_template]] | upstream | 0.30 |
| n00_output_template_manifest | sibling (source investigation) | 0.28 |
