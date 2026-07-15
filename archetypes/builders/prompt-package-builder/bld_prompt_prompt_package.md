---
id: p03_ins_prompt_package
kind: instruction
pillar: P03
version: 1.0.0
created: "2026-07-03"
updated: "2026-07-03"
author: builder
title: Prompt Package Builder Instructions
target: "prompt-package-builder agent"
phases_count: 4
prerequisites:
  - "Caller has already run F1 CONSTRAIN, F2 BECOME, F3 INJECT, F4 REASON for the TARGET kind"
  - "Target kind exists in .cex/kinds_meta.json (Stage 2 MUST NOT consume an unregistered target_kind)"
  - "A cheap-tier model (Haiku/Flash/Ollama) is the intended Stage-2 consumer"
validation_method: checklist
domain: prompt_package
quality: null
tags: [instruction, prompt-package, P03, decompose, mode-b]
idempotent: false
atomic: false
rollback: "Delete the produced pp_*.md under .cex/runtime/packages/. No side effects until Stage 2 consumes it."
dependencies: [prompt_template, system_prompt, prompt_compiler]
logging: true
tldr: "Harvest F1-F4 state, classify against P03 siblings, compose the 4-section package, validate against p06_if_prompt_package.md before handoff."
8f: "F6_produce"
keywords: [prompt package builder instructions, harvest F1-F4 state, mode b, decompose, stage 1, stage 2, cex_decompose.py, cex_8f_runner.py]
density_score: 0.90
llm_function: REASON
related:
  - prompt-package-builder
  - bld_knowledge_card_prompt_package
  - bld_orchestration_prompt_package
  - schema_prompt_package_builder
  - bld_memory_prompt_package
---
## Context

A **prompt_package** is a frozen handoff: the F1-F4 output of a reasoning-capable model (Stage 1,
"THINK"), written to disk so a cheap generation-only model (Stage 2, "GENERATE") can execute F6
PRODUCE without re-running F1-F4 and without live tools. This builder operates at the prompt
layer (P03), same as `prompt_template`/`system_prompt`/`prompt_compiler` -- its 3 `depends_on`
entries per `.cex/kinds_meta.json`.

**Inputs**

| Field | Type | Description |
|---|---|---|
| `f1_constraints` | object | Kind, pillar, max_bytes, id_pattern, frontmatter_required, boundary (F1 CONSTRAIN output) |
| `f2_identity` | string | Builder persona / system_prompt text the Stage-2 model must adopt (F2 BECOME output) |
| `f3_context` | object | Injected knowledge: builder KC excerpt, up to 3 domain KCs, any pre-resolved external context (F3 INJECT output) |
| `f4_plan` | string | Section list, approach, density target (F4 REASON output) |
| `target_kind` | string | The kind Stage 2 must produce -- MUST resolve in `.cex/kinds_meta.json` |

**Output**

A single `.md` file conforming to `N00_genesis/P06_schema/p06_if_prompt_package.md`. YAML
frontmatter (8 required fields minimum) + 4 mandatory body sections: IDENTITY, CONTEXT, PLAN,
TEMPLATE. Real reference implementation: `_tools/cex_8f_runner.py::_write_prompt_package`
(lines 2001-2101) assembles exactly this shape from `self.state.{constraints,identity,knowledge,reasoning}`.

**Boundary rules**

- If the input defines a REUSABLE `{{variable}}` mold with no specific target build -> it is a
  `prompt_template`. Route there.
- If the input defines a fixed agent identity/persona with no F1-F4 state to freeze -> it is a
  `system_prompt`. Route there.
- If the input is about DECIDING which kind/pillar/nucleus to build (not yet decided) -> it is
  `prompt_compiler` territory (intent resolution). Route there first; compile the package only
  after `target_kind` is resolved.

## Phases

### Phase 1: Harvest -- Freeze F1-F4 State

Pull the 4 stage outputs from the calling model's own reasoning, not from a fresh guess.

```
F1_CONSTRAINTS  <- kind, pillar, max_bytes, id_pattern, frontmatter_required, boundary text
F2_IDENTITY     <- builder system_prompt / persona text (<= 2000 chars per real writer)
F3_CONTEXT      <- builder KC excerpt (<=1500 chars) + up to 3 domain KCs (<=1000 chars each)
                   + any pre-resolved external context (<=1500 chars) -- NEVER a live MCP call
F4_PLAN         <- section list + approach + density target (<=2000 chars)
IF any of F1-F4 is missing or unresolved:
  RETURN error: "Cannot compile a prompt_package before F1-F4 complete for the target kind."
```
Deliverable: 4 populated blocks, each within the real writer's own truncation budget.

### Phase 2: Classify -- Boundary Check

Confirm the artifact is `prompt_package` and not a sibling P03 kind.

```
IF input has {{variables}} for repeated future invocation, no fixed target build:
  RETURN "This is a prompt_template -- route to prompt-template-builder."
IF input defines agent identity/persona with no F1-F4 state to freeze:
  RETURN "This is a system_prompt -- route to system-prompt-builder."
IF input is about WHICH kind/pillar/nucleus to build (undecided):
  RETURN "This is prompt_compiler territory -- resolve intent first."
IF F1-F4 state exists AND a target_kind is already resolved AND a cheap model must consume it:
  PROCEED as prompt_package
```
Deliverable: confirmed `kind: prompt_package` with one-line justification.

### Phase 3: Compose -- Build the Artifact

Assemble frontmatter + 4 body sections using `bld_output_prompt_package.md` as the structural guide.

```
ID generation:
  Real convention observed on disk: id = "pp_" + target_kind + "_" + session_id
    (matches _write_prompt_package's pkg_filename: "pp_%s_%s.md" % (kind, session_id))
  Registered convention (.cex/kinds_meta.json naming field): "p03_pp_{{task_id}}.md"
  GAP (report honestly, do not silently pick one): the two do not match today -- neither
  N00_genesis/P03_prompt/examples/stress_decompose_packages/ (pp_T05_*.md ... pp_T09_*.md)
  nor .cex/runtime/packages/ (pp_agent_N04_auto_*.md, dozens found on disk) use the
  registered "p03_pp_" prefix. Follow the REAL convention (pp_{target_kind}_{id}.md) for
  interoperability with cex_decompose.py's _find_latest_package glob ("pp_*.md"); flag the
  registry mismatch rather than silently resolving it.
Frontmatter (8 required fields minimum, per p06_if_prompt_package.md):
  package_type (= "f6_prompt_package"), target_kind, target_pillar, target_path,
  builder_isos_loaded, context_sources, density_target (0.80-1.00), max_bytes (<=32768,
  and <= the target kind's own registered max_bytes)
  Plus: id, kind (= prompt_package), pillar (= P03), title, version, quality (= null), tags
Body sections (in this exact order):
  ## IDENTITY (from F2 BECOME)
    Builder persona the Stage-2 model adopts; sin lens; builder contract (frontmatter +
    N sections + M tables + K wikilinks + density floor).
  ## CONTEXT (from F3 INJECT)
    Domain knowledge facts + related artifacts (wikilinks) + any pre-resolved external
    context. This REPLACES the cheap model's need for MCP or retrieval -- resolve first.
  ## PLAN (from F4 REASON)
    Section list, approach (template|hybrid|fresh), density target, estimated bytes/sections.
  ## TEMPLATE (generate this artifact)
    The target kind's own bld_output ISO content, frontmatter-stripped, embedded verbatim
    (mirrors _write_prompt_package's load_iso(bdir, "bld_output", kind_slug) call).
```
Deliverable: complete `.md` file with frontmatter + 4 body sections, written to
`.cex/runtime/packages/`.

### Phase 4: Validate -- Gate Check

Run all quality gates from `bld_eval_prompt_package.md` before handoff to Stage 2.

```
HARD gates (all must pass -- fix before handoff):
  H01: frontmatter parses as valid YAML
  H02: package_type == "f6_prompt_package"
  H03: target_kind resolves in .cex/kinds_meta.json
  H04: all 4 body sections present (IDENTITY, CONTEXT, PLAN, TEMPLATE)
  H05: TEMPLATE section contains at least one fill-marker ({{...}} OR [FILL: ...] --
       both conventions are attested on disk; p06_if_prompt_package.md specifies
       "[FILL: ...]" but the real template tpl_prompt_package.md + the real generator
       both use Mustache {{...}} -- accept either, do not invent a false resolution)
  H06: max_bytes field is a positive integer <= 32768 AND <= the target kind's own cap
  H07: quality is null at authoring time
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[prompt-package-builder]] | related | 0.48 |
| [[bld_knowledge_card_prompt_package]] | upstream | 0.47 |
| [[bld_orchestration_prompt_package]] | related | 0.47 |
| [[schema_prompt_package_builder]] | downstream | 0.45 |
| [[bld_memory_prompt_package]] | downstream | 0.39 |
