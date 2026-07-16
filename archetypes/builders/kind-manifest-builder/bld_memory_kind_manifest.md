---
id: p10_lr_kind_manifest_builder
kind: learning_record
pillar: P10
version: 1.0.0
created: 2026-07-10
updated: 2026-07-10
author: builder_agent
observation: "INAUGURAL record -- no prior kind_manifest BUILDER existed before this hotfix (R-310 registered the kind and authored ISO 2 only, same day). Lessons extracted from the R-310 re-typing itself plus this scaffold's own direct read of 3 real instances and a fresh 294-file count, not from N accumulated review cycles. Flagged honestly, not presented as review-derived statistics."
pattern: "Three findings, verified against the live corpus (not inferred): (1) the R-310 re-typing was byte-scoped -- only the kind: field flipped from knowledge_card to kind_manifest across 294 files, ids/filenames/related webs untouched; (2) this corpus has ZERO id-naming drift, unlike output_template's 3-way split -- 294/294 already match n00_{kind}_manifest; (3) the filename is INVARIANT (kind_manifest_n00.md) while directory + id vary -- the opposite convention from most kinds, which template the filename instead."
evidence: "Extracted from bld_schema_kind_manifest.md (authored the same day, R-310) plus direct reads of 3 real instances (n00_knowledge_card_manifest.md, n00_output_template_manifest.md, n00_agent_manifest.md) and a fresh Glob count confirming 294 kind_manifest_n00.md files on disk. No live builder-review history exists yet."
confidence: 0.60
outcome: SUCCESS
domain: kind_manifest
tags: [kind-manifest, r-310, per-kind-identity, fixed-filename-axis, inaugural]
tldr: "Inaugural record (no prior builder yet): the R-310 re-typing was byte-scoped (kind: field only), this corpus has zero id-naming drift unlike output_template, and the filename is invariant while directory+id vary -- verify any instance count fresh rather than citing a prior figure."
impact_score: 6.5
decay_rate: 0.08
agent_group: edison
keywords: [kind_manifest, r_310, per_kind_identity, fixed_filename_axis, n00_manifest_pattern, inaugural]
memory_scope: project
observation_types: [reference, project]
quality: null
title: "Memory Kind Manifest"
8f: "F3_inject"
density_score: 0.87
llm_function: INJECT
related:
  - bld_knowledge_card_kind_manifest
  - bld_instruction_kind_manifest
  - bld_output_template_kind_manifest
  - bld_schema_kind_manifest
  - p10_lr_output_template_builder
---
## Summary
kind_manifest artifacts document ONE registered kind's identity each, and this family's builder is ITSELF inaugural today -- R-310 registered the kind and authored the schema ISO only, same day this record was written. Since there is no accumulated review history yet, this record captures the landmines the R-310 re-typing and this scaffold's own corpus read already paid for.
## Pattern
Three landmine categories (all three verified against the real corpus, not inferred):
1. **The R-310 re-typing was byte-scoped, not a rewrite** -- only the `kind:` field flipped from `knowledge_card` to `kind_manifest` across all 294 real instances. Ids, filenames, and the mutual `related:` cross-reference web were left BYTE-UNCHANGED -- renaming any of those would have rewritten ~294 files' worth of inbound wikilinks in one pass, the exact trap a prior register row (R-289) named and avoided for a different corpus.
2. **This corpus carries ZERO id-naming drift** -- unlike `output_template` (3 conventions, 0/18 matching canonical) or other recently-scaffolded kinds, `kind_manifest`'s 294/294 real instances already match `^n00_[a-z][a-z0-9_]+_manifest$` exactly. The only field that was ever wrong was `kind:`, never `id:`. Do not import output_template's drift-disclosure playbook here by habit -- there is no drift to disclose for this kind's naming.
3. **Filename is INVARIANT; directory and id are what vary** -- `kind_manifest_n00.md` never changes; only the parent `kind_{{kind}}/` directory and the `id:` field track the documented kind. This is the OPPOSITE of most kinds (which template the FILENAME on a slug and hold structure fixed). A builder that assumes filename varies (like almost everything else in this repo) will propose an incorrect naming scheme.
Additional real, source-documented behavior worth carrying into every kind_manifest this builder produces: `depends_on` is fixed EMPTY (`[]`) -- a manifest may CITE any kind in its "Related kinds" prose, but declares no formal dependency edge. `nucleus: n00` (lowercase) is fixed inside every real instance's OWN frontmatter, distinct from `kinds_meta.json`'s separate owning-nucleus field (`N03`) -- do not conflate the two when authoring or reading either.
## Anti-Pattern
1. Renaming the fixed `kind_manifest_n00.md` filename "for consistency" with the rest of the taxonomy -- this kind's naming IS the exception, not a defect.
2. Assuming id-naming drift exists here by analogy with `output_template` -- this corpus has none; disclosing a non-existent drift is as wrong as hiding a real one.
3. Fabricating a builder pointer for a documented kind that has none yet -- the honest "Builder -- honest status (register row R-XXX, OPEN)" callout is the correct move (this kind's own manifest ecosystem already models it: `n00_output_template_manifest.md` did exactly this for `output_template` until R-299 closed it).
4. Citing "294" (or any other corpus count) without a fresh re-verification -- a newly-registered kind changes the count the moment its manifest lands.
5. Adding a `depends_on` entry "for completeness" -- fixed empty by design.
## Context

## Builder Context

This ISO operates within the `kind-manifest-builder` stack, one of the 300+
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
id: p10_lr_kind_manifest_builder
pipeline: 8F
scoring: hybrid_3_layer
target: 9.0
```

```bash
python _tools/cex_score.py --apply --verbose p10_lr_kind_manifest_builder.md
```

## Properties

| Property | Value |
|----------|-------|
| Kind | `learning_record` |
| Pillar | P10 |
| Domain | kind_manifest |
| Pipeline | 8F |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Target | 9.0+ |
| Density | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_card_kind_manifest]] | upstream | 0.38 |
| [[bld_instruction_kind_manifest]] | upstream | 0.36 |
| [[bld_output_template_kind_manifest]] | upstream | 0.32 |
| [[bld_schema_kind_manifest]] | upstream | 0.30 |
| [[p10_lr_output_template_builder]] | sibling (same resolution shape) | 0.28 |
