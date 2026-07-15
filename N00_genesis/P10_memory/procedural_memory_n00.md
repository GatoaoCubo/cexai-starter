---
id: procedural_memory_n00
kind: procedural_memory
8f: F3_inject
pillar: P10
nucleus: n00
title: "Procedural Memory -- N00 Genesis Standard Operating Procedures"
version: "1.0.0"
quality: null
tags: [procedural_memory, n00, genesis, sop, schema_evolution, kind_registration, kc_curation, prompt_compiler, P10]
domain: "genesis layer maintenance"
status: active
created: "2026-07-02"
updated: "2026-07-02"
author: n03_engineering
tldr: "How N00_genesis is maintained: schema evolution, kind registration, KC library curation, prompt-compiler updates. Written for whichever nucleus N07 dispatches to touch N00 -- N00 itself never boots or self-executes."
keywords: [genesis layer maintenance, procedural memory -- n, standard operating procedures, schema evolution, kind registration, kc library curation, prompt compiler updates, n00 genesis, distillation carry]
density_score: null
related:
  - n00_procedural_memory_manifest
  - n00_readme
  - nucleus_def_n00
  - kc_nucleus_def
  - n00_p01_kind_index
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_flywheel_audit, cex_kind_register, cex_new_nucleus. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

# Procedural Memory: N00 Genesis Standard Operating Procedures

## About This File

N00_genesis never boots and is never dispatched: `boot/n00*.ps1` is absent, `boot/cex_nucleus.sh` line 20 rejects it (`^n0[1-7]$` regex), and `Task tool: dispatch` matches nucleus tokens against the same `n0[1-7]` pattern at 3 sites. So this file is not "what N00 does when booted" -- it is the playbook for **whichever nucleus N07 dispatches to touch N00's content**. Per `.cex/P09_config/dispatch_catalog.md` L100, `N00_genesis/P*/*.md` is FORBIDDEN for N07, routed to N03 by default; N07 has also swarmed N01-N05 into per-nucleus worktrees for bulk quality passes (`.cex/runtime/archive/FLYWHEEL_N00_n01_20260621_1034.md`, mission `FLYWHEEL_N00`). Read SOP-05 before touching anything below.

## SOP-01: Schema Evolution (`N00_genesis/P{01-12}_*/_schema.yaml`)

**Trigger**: a kind's shape changes, or a new `kinds:` block is needed.

1. Exactly one schema per pillar, always under `N00_genesis/`: `cex_compile.py`'s `LP_DIRS` (lines 29-42) and `get_lp_dir_for_lp()` (lines 248-255) hardcode all 12 paths there -- no other `_schema.yaml` exists repo-wide. Every nucleus's F1 CONSTRAIN reads its pillar schema from here; an edit changes F1 for all of N01-N07 immediately.
2. **KNOWN BROKEN, verified live, unfixed**: `N00_genesis/P10_memory/_schema.yaml` is not valid YAML -- every line under `kinds:` sits at one leading space regardless of nesting, so fields that should nest under `user_model:` / `entity_memory:` read as siblings of `kinds:` itself (`ScannerError ... line 34, column 2 could not find expected ':'`). Reproduced against the real tool: `python _tools/cex_compile.py N00_genesis/P10_memory/examples/ex_axiom_lifecycle_hooks.md` crashes with this trace (`load_schema()` has no try/except). All other 11 pillar schemas parse clean. Only one commit ever touched the file (`002a8a0c6b`, "Initial Open Source Release") -- shipped broken, not a fresh regression. Blast radius is narrow: `compile_file()` sets `lp_dir = md_path.parent.parent`, so only files two levels under `P10_memory/` (`examples/`, `templates/`, `kind_*/`) trigger the parse; a file directly at `P10_memory/*.md` -- like this one -- resolves `lp_dir` to `N00_genesis`, where no schema exists, so `load_schema()` returns `{}` first and this file compiles safely.
3. Same file's `kinds:` block also has no `procedural_memory:` entry, though `kinds_meta.json` has one for this exact kind -- the two registries drift independently of the corruption. Don't assume schema/meta parity; check both.
4. To add a `kinds:` entry, match the block `cex_kind_register.py::reg_schema()` writes (lines 64-81): `description`, `boundary`, `layer`, `core`, `machine_format`, `naming`, `constraints.{max_bytes,density_min,quality_min}`, `frontmatter_required`. Validate with `python -c "import yaml; yaml.safe_load(open(path, encoding='utf-8'))"` before saving -- P10 proves this is regularly skipped.

## SOP-02: Kind Registration (the 4-file fanout)

**Trigger**: a genuinely new kind is needed (not 80% covered by an existing one -- root `CLAUDE.md` Taxonomy Hygiene Rule).

1. A kind touches 4 files: `kinds_meta.json`, the pillar `_schema.yaml` (SOP-01), `archetypes/TYPE_TO_TEMPLATE.yaml`, `cex_8f_motor.py`'s `OBJECT_TO_KINDS`. `cex_kind_register.py --kind X --pillar PXX --function FN --description "..." --boundary "..."` is meant to do all 4.
2. **Broken for the current layout**: `PILLAR_DIRS` (lines 17-19) globs `CEX_ROOT.glob("P[0-9][0-9]_*")` -- pillars at repo ROOT, pre-migration. Resolves empty today (confirmed live), so `reg_schema()` (line 58) `KeyError`s. Reproduced with `--dry-run --kind test_probe_kind --pillar P10`: kinds_meta preview prints, then traceback. `--list` / `--validate` still work (read-only).
3. UNVERIFIED, flagged (not executed, to avoid mutating `kinds_meta.json`): `reg_meta()` writes on `dry=False` before `main()`'s `sum([reg_meta(...), reg_schema(...), ...])` (lines 189-194) hits the crash -- a real run likely writes meta then dies, half-registering the kind. Treat as a real risk until `PILLAR_DIRS` is fixed.
4. **Manual fallback**: hand-edit `kinds_meta.json` (alphabetical -- `save_json()` sorts) + the pillar `_schema.yaml` block (SOP-01.4) + append to `TYPE_TO_TEMPLATE.yaml` + add to `OBJECT_TO_KINDS`. Then `--validate`.
5. Not hypothetical: `--validate` this session -> `kinds_meta: 316`, `TYPE_TO_TPL: 106`, `Motor: 127`. 200+ kinds (incl. `procedural_memory` itself) miss one or both registries. Run `--validate` before trusting a kind is fully wired.

## SOP-03: KC Library Curation (`N00_genesis/P01_knowledge/library/kind/kc_{kind}.md`)

**Trigger**: a kind has no knowledge card, or an existing one needs enrichment.

1. F3 INJECT's primary source for every 8F run, every nucleus (`cex_8f_runner.py` line 569). 320 `kc_*.md` files exist against 316 registered kinds.
2. Coverage check (read-only): diff the `kind/` dir's `kc_{x}.md` stems against `kinds_meta.json` keys. This session: 6 kinds have no KC (`field_manifest`, `marketplace_listing`, `opportunity_matrix`, `product_match`, `prompt_package`, `tenant_voice_profile`); 9 KC files are orphaned, 4 clearly stale test fixtures (`test_consolidate_loop`, `test_dispatch_pattern`, `test_ollama_wrapper`, `test_signal_flow`).
3. New KC: `python _tools/cex_8f_runner.py "document {kind}" --kind knowledge_card --execute`, or follow N04's own SOP-01 (`N04_knowledge/P10_memory/procedural_memory_n04.md`) -- N04 owns KC authorship end-to-end; N00 only owns the resting place.
4. Quality-enrichment swarm pattern (`FLYWHEEL_N00` handoff, About This File): N07 dispatches each nucleus into its own `-w` worktree against an explicit file list, never "enrich everything". Ruler: `python _tools/cex_score.py <file>` -- NEVER edit `cex_score.py` (that handoff calls it the "Goodhart guard"). Fix every dimension below 7, not just the weakest. Gate: score up AND `antislop_factor` not reduced, else `git checkout -- <file>` and report the revert. Gold exemplar: `N04_knowledge/P01_knowledge/p01_kc_clean_arch_ddd_in_cex.md`.
5. Central-only: `cex_kc_index.py` embeds the library into Supabase pgvector (`--stats` / `--search`); needs live OpenAI+Supabase creds, skip if absent -- retrieval degrades to `cex_retriever.py`'s filesystem TF-IDF.

## SOP-04: Prompt-Compiler Updates (`N00_genesis/P03_prompt/layers/p03_pc_cex_universal.md`)

**Trigger**: a kind has no row in the intent-resolution table, or a new verb/pattern is needed.

1. `.claude/rules/n07-input-transmutation.md`'s "canonical mapping artifact" -- loaded at F1 CONSTRAIN by every nucleus to map free-text input to `{kind, pillar, nucleus, verb}`.
2. Structure: one `### P{01-12} {Name}` section per pillar (confirmed at lines 41/77/104/128/168/195/212/241/259/302/328/361), each a `| Kind | N | EN | PT | V |` table. EN is base; PT-BR is the seeded community contribution.
3. To add a kind: find its pillar section, insert a row with EN pattern, PT-BR pattern, owning nucleus, canonical verb (verb list in `n07-input-transmutation.md`'s "Verb Resolution" table).
4. No automated validator for coverage -- and it drifts: frontmatter says `coverage: 300`, a same-session row count found ~304 rows, `kinds_meta.json` has 316 kinds. Reconcile by eye; no `--validate` equivalent here.
5. Its `referenced_by` frontmatter must stay honest -- currently `n07-input-transmutation.md`, `n07-technical-authority.md`, `CLAUDE.md`. Update on add/remove of a consumer.
6. Carried byte-identical into every distilled tenant (SOP-08) -- one of only two CARRIED-INVARIANT payloads. An edit here changes every future tenant bootstrap, not just Central.

## SOP-05: Deciding Who May Touch N00 Directly

**Trigger**: before ANY Write/Edit under `N00_genesis/P*/*.md`.

1. Default FORBIDDEN for N07 -- `dispatch_catalog.md` L100: `N00_genesis/P*/*.md -> N03`. N07's own "Before any Write/Edit decision" checklist (`.claude/rules/n07-orchestrator.md`) requires dispatch unless the path is N07-SAFE or the edit is mechanically surgical.
2. `dispatch_catalog.md`'s "Surgical-edit bypass" still applies inside N00: typo fix, mechanical rename, timestamp/version bump, canon-color correction, wikilink add. Anything needing authorial judgment is not surgical -- dispatch it.
3. `.claude/rules/raci-matrix.md`'s columns are N01-N07 only -- N00 has no RACI row, same absence pattern as `nucleus_models.yaml` (no `n00:` block) and `.claude/nucleus-settings/` (only `_template.json` + `n01..n07.json`, confirmed no `n00.json`).
4. This file is the worked example: lives at a FORBIDDEN path, authored under the N03 route rather than by "N00" -- which cannot author anything (see About This File).

## SOP-06: Bootstrapping a New Nucleus From the Archetype

**Trigger**: `/mission` or a user asks for N08+ ("new vertical", "healthcare nucleus").

1. Preferred: `python _tools/cex_new_nucleus.py <NN> <domain> <sin> --dry-run` first. Verified this session (`08 testdomain wrath` probe): 27 actions (15 mkdir + 11 write + 1 append), matching `.claude/rules/new-nucleus-bootstrap.md`'s "9 Required Assets".  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
2. `N00_genesis/n00_README.md`'s "How to Instantiate" (steps 1-7) is an OLDER narrative version -- its "minimum viable set" lists only 5 files, disagreeing with both the scaffolder's real output and the newer rule. Treat `--dry-run` output as ground truth (executable, just verified); treat `n00_README.md` as historical narrative only.
3. `nucleus_num must be >= 08` is enforced; N00-N07 are reserved, the scaffolder refuses to touch them.
4. The scaffolder copies NO N00_genesis file into the new nucleus -- it writes narrative strings referencing N00_genesis into the new nucleus's own rules. The nucleus reads N00_genesis at runtime (F1/F3); nothing is physically copied at creation.

## SOP-07: Verifying Genesis Integrity (read-only diagnostics)

**Trigger**: before signing off on any N00 maintenance pass.

1. `python _tools/cex_doctor.py --vocab` -- confirms N01-N07 each hold a vocabulary KC; N00 is intentionally exempt (`cex_doctor.py` line 863 comment).
2. `python _tools/cex_kind_register.py --validate` -- 3-way diff, `kinds_meta.json` / `TYPE_TO_TEMPLATE.yaml` / `cex_8f_motor.py` (SOP-02 for current gaps).  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
3. Loop `yaml.safe_load()` over all 12 `_schema.yaml` -- catches corruption the way SOP-01 found P10's. No existing gate does this; it's a gap this audit surfaced.
4. `python _tools/cex_doctor.py` (general) -- `LIBRARY_DIR` + H01-H06 gates still apply to any file inside `N00_genesis/`.
5. Large pass: `python _tools/cex_flywheel_audit.py` (doc-vs-practice, 109 checks / 7 layers).  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->

## SOP-08: Distillation Carry Rules (what ships to a sovereign tenant repo)

**Trigger**: before assuming an N00 edit will (or won't) reach tenant repos via `cex_distill.py`.

1. CARRIED-INVARIANT, byte-identical, every tenant: all 12 `_schema.yaml` (`_INVARIANT_SCHEMAS_COUNT = 12`, line 1177) + `p03_pc_cex_universal.md` (lines 2220-2222).
2. CARRIED-CONDITIONAL: `_carry_kc_library()` (line 5322) carries `kind/kc_{kind}.md` only for kinds backed by an embedded builder in the target tenant (the LEAN set, `docs/SPEC_TENANT_BRAIN_RUNNABLE.md` P1) -- not the full 320-file library.
3. Central-only, confirmed NOT carried: the 268 `kind_manifest_n00.md` files (this kind's own included), `templates/`, `examples/`, general KC library subdirs, both `nucleus_def_n00.md`, `n00_README.md`, `boot/mentor_context.md`, all `compiled/` YAML.
4. Consequence: editing a `kind_manifest_n00.md` or this file changes nothing for tenants. Editing a `_schema.yaml` or the prompt-compiler changes every future tenant bootstrap. Editing a `kc_{kind}.md` changes tenants only if that kind ships an embedded builder there.

## Procedure Update Log

| Date | Procedure | Change |
|------|-----------|--------|
| 2026-07-02 | SOP-01 to SOP-08 | Initial creation. SOP-01.2 and SOP-02.2-3 document live-verified bugs (P10 schema `ScannerError`; `PILLAR_DIRS` `KeyError`), not design notes -- re-verify both if either gets fixed later. |

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| n00_procedural_memory_manifest | upstream | 0.40 |
| n00_readme | upstream | 0.38 |
| [[nucleus_def_n00]] | sibling | 0.32 |
| [[kc_nucleus_def]] | related | 0.28 |
| [[n00_p01_kind_index]] | related | 0.25 |
