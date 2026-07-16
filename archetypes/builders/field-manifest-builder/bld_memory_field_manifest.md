---
id: p10_lr_field_manifest_builder
kind: learning_record
pillar: P10
version: 1.0.0
created: 2026-07-03
updated: 2026-07-03
author: builder_agent
observation: "This is the INAUGURAL learning record for field_manifest -- no prior field_manifest artifacts exist to review (this builder is being scaffolded for the first time). The lessons below are extracted directly from the reference implementation's OWN documented landmines and design decisions (source-code comments in apps/dashboard_web/lib/field-manifest/), not from N accumulated builder-review cycles. Flagged honestly rather than presented as review-derived statistics."
pattern: "Three real landmines the reference code documents explicitly: (1) the superRefine-before-partial order dependency in buildSchema.ts -- baseSchema.superRefine() produces a ZodEffects that has lost .partial()/.extend(), so updateSchema MUST derive from baseSchema directly, never from the gated schema; (2) FieldKind is a closed, exhaustiveness-guarded union -- coreTypeFor() throws on an unmapped kind rather than silently accepting 'any', so a new kind is a two-file change (buildSchema.ts + renderers.tsx), never a one-file addition; (3) renderers.tsx's own header notes a FIXED latent bug from the reference app it was ported from (getManifestField/ManifestField used ProductManifest without importing it) -- a reminder that 'ported from the reference implementation' code can carry forward real defects, and each port is a chance to fix or repeat them."
evidence: "Extracted from apps/dashboard_web/lib/field-manifest/buildSchema.ts (header comment, lines 13-17: 'Base-vs-refined split (CRITICAL -- the superRefine landmine)'), types.ts (lines 13-17: FieldKind docstring naming the exhaustiveness guard), renderers.tsx (lines 14-21: adaptation notes including the fixed latent bug), and handlers.ts (lines 1-16: the inert-by-default registry as the safety mechanism for zero-tenant-behavior mounts). No live builder-review history exists yet -- this record will accumulate real review evidence as field_manifest artifacts are produced and scored."
confidence: 0.55
outcome: SUCCESS
domain: field_manifest
tags: [field-manifest, schema-to-form, publish-gate, superrefine, exhaustiveness-guard, inaugural]
tldr: "Inaugural record (no prior builds yet): superRefine must follow .partial() derivation, FieldKind is closed+exhaustiveness-guarded, and ported code can carry forward real bugs -- verify, don't assume."
impact_score: 6.0
decay_rate: 0.08
agent_group: edison
keywords: [field_manifest, superrefine, partial, exhaustiveness_guard, handler_registry, tenantparam]
memory_scope: project
observation_types: [reference, project]
quality: null
title: "Memory Field Manifest"
8f: "F3_inject"
density_score: 0.86
llm_function: INJECT
related:
  - bld_knowledge_card_field_manifest
  - bld_instruction_field_manifest
  - bld_output_template_field_manifest
  - bld_schema_field_manifest
  - p10_lr_input_schema_builder
---
## Summary
field_manifest artifacts describe a schema-to-form DERIVATION, not three independent
artifacts. The reference implementation's own comments document exactly where that
derivation is fragile: the order zod combinators are applied in, the closed
vocabulary of field kinds, and the fact that "ported from the reference
implementation" code can silently carry a bug forward into the port. Since this is
the FIRST field_manifest builder scaffold, there is no accumulated review history --
this record captures the landmines the SOURCE code already paid for, so the builder
does not have to re-discover them empirically.
## Pattern
Three landmine categories (all three verified against real source comments, not inferred):
1. **Zod combinator order** -- `baseSchema.superRefine(gate)` returns a `ZodEffects`,
   which has NO `.partial()`/`.extend()`. `updateSchema` must always be derived from
   `baseSchema` (the plain `ZodObject`), never from the gated `schema`. Describing a
   field_manifest's derivation without naming this order is an incomplete contract.
2. **Closed, exhaustiveness-guarded FieldKind** -- 14 values today (text, textarea,
   number, slug, price, tags, stringArray, orderedArray, faq, images, mediaKit,
   select, keyValue, boolean). A 15th kind is a two-file change (the zod mapping AND
   the renderer registry); the reference code enforces this at build/type-check time
   via a `_never: never` exhaustiveness check that throws on drift.
3. **Ported code can carry forward real bugs** -- the reference `renderers.tsx`
   documents fixing a latent import bug ("`getManifestField`/`ManifestField` use
   `ProductManifest` but the source never imported it") during the port to this
   Central repo. A field_manifest description should not assume the reference
   implementation is bug-free just because it is the "proving ground" -- each
   consuming surface is a chance to re-verify, not just copy.
Additional real, source-documented behavior worth carrying into every field_manifest
this builder produces: the default `HandlerRegistry` (`inertHandlerRegistry`) returns
`undefined` for every `(kind, tenant)` pair, so a manifest with ZERO bound behavior
still renders and validates correctly -- controls degrade to inert no-ops, not
crashes. This "safe when unbound" property is a design goal, not an accident, and
should be preserved in every new manifest's Handler Seam section (documenting NEED,
never assuming an implementation exists).
## Anti-Pattern
1. Deriving `updateSchema` from the gated `schema` instead of the plain `baseSchema` --
   silently strips `.partial()`, breaking partial updates.
2. Adding a field `kind` value outside the 14-member closed set without also
   extending the zod mapping and the renderer registry in the same change.
3. Assuming a "ported from reference" module is correct because it is the proving
   ground -- the reference app itself has shipped at least one documented latent bug
   that required a fix during porting.
4. Hardcoding a `HandlerRegistry` implementation inline in the manifest description --
   the registry is a separate, swappable seam; describing behavior inside the
   manifest breaks the tenant-agnostic core.
5. Treating `tenantParam: true` as something that changes validation or rendering --
   it is a documentation flag for a future distiller ONLY.
## Context

## Builder Context

This ISO operates within the `field-manifest-builder` stack, one of the 300+
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
id: p10_lr_field_manifest_builder
pipeline: 8F
scoring: hybrid_3_layer
target: 9.0
```

```bash
python _tools/cex_score.py --apply --verbose p10_lr_field_manifest_builder.md
```

## Properties

| Property | Value |
|----------|-------|
| Kind | `learning_record` |
| Pillar | P10 |
| Domain | field_manifest |
| Pipeline | 8F |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Target | 9.0+ |
| Density | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_card_field_manifest]] | upstream | 0.38 |
| [[bld_instruction_field_manifest]] | upstream | 0.36 |
| [[bld_output_template_field_manifest]] | upstream | 0.32 |
| [[bld_schema_field_manifest]] | upstream | 0.30 |
| [[p10_lr_input_schema_builder]] | sibling | 0.28 |
