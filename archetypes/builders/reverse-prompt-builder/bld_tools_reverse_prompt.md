---
id: tools_reverse_prompt_builder
kind: tools
pillar: P04
llm_function: CALL
domain: reverse_prompt
version: 1.0.0
created: "2026-07-03"
updated: "2026-07-03"
author: builder
tags:
  - "tools"
  - "reverse-prompt"
  - "P03"
  - "data-sources"
quality: null
title: "Tools Reverse Prompt"
tldr: "Real tool touchpoints for reverse_prompt: the canonical GitReverseSynthesizer mechanism (read-only reference) plus the standard FS toolset for builder-authored drafts."
8f: "F5_call"
keywords:
  - "tools reverse prompt"
  - "tools"
  - "reverse-prompt"
  - "data-sources"
  - "reverse_prompt"
  - "GitReverseSynthesizer"
  - "license_gate"
  - "tool registry"
  - "tool descriptions"
density_score: 0.90
related:
  - reverse-prompt-builder
  - bld_architecture_reverse_prompt
  - bld_eval_reverse_prompt
---

# Tools -- reverse-prompt-builder
## Tool Registry
| Tool | Status | Tag | Purpose |
|---|---|---|---|
| Read | ACTIVE | [FS] | Read `kc_reverse_prompt.md`, `synthesizer.py`, `kind_manifest_n00.md`, sibling drafts |
| Glob | ACTIVE | [FS] | Find existing `p03_rp_*` pool drafts + (read-only) real `.cex/runtime/artifacts/reverse_prompts/*.md` instances |
| Grep | ACTIVE | [FS] | Search for `kind: reverse_prompt` instances; check open_vars naming collisions |
| Write | ACTIVE | [FS] | Produce the builder-authored draft artifact (pool path only) |
| Edit | ACTIVE | [FS] | Patch frontmatter/body during VALIDATE or `repair` mode |
| Bash | CONDITIONAL | [FS] | `python -m pytest cexai/tests/tools/reposynth/test_synthesizer.py -q` -- confirm the canonical tool's health before documenting it |
## Real Mechanism Touchpoints (read-only reference; NEVER invoked to author drafts)
| Module | Role |
|---|---|
| `cexai.tools.reposynth.synthesizer.GitReverseSynthesizer` | The canonical, deterministic producer (`extract` / `synthesize` / `_project`) |
| `cexai.tools.reposynth.license_gate` | `detect_license_spdx` / `has_license_file` / `check_license_compatibility` -- SPDX rank matrix |
| `cexai.tools._shared.types.RepoExtract` / `.ReversePrompt` | Frozen runtime dataclasses the synthesizer projects |
| `cexai.tools._shared.errors` | `LicenseCompatibilityError` / `LicenseUnknownWarning` / `ReverseSynthError` |
| `cexai.foundation.llm.call` | The LLM seam the synthesizer dispatches through at `temperature=0.0` |
| CLI `cexai repo_synthesizer create <url>` | How a caller gets a REAL instance -- route here, never hand-author a substitute |
## Data Sources
| Source | Content | When to use |
|---|---|---|
| `bld_schema_reverse_prompt.md` | Field definitions, ID pattern, the two-path distinction | Every production run |
| `bld_output_template_reverse_prompt.md` | Exact frontmatter + body structure | Every production run |
| `bld_eval_reverse_prompt.md` | H01-H10 + rubric C1-C5 | Every validation run |
| `kc_reverse_prompt.md` | Kind boundary, fields, lifecycle | Boundary disputes |
| `rubric_reverse_prompt_equivalence.md` | 5-criteria cross-runtime equivalence + worked examples | `calibration_pair` mode |
| `cexai/tests/tools/reposynth/test_synthesizer.py` | 29 passing tests -- ground truth for real mechanics | Documenting/reviewing a real instance |
## Tool Permissions
| Category | Tools | Status |
|----------|-------|--------|
| ALLOWED | Read, Write, Edit, Bash, Glob, Grep | Explicitly permitted |
| DENIED | Live invocation of `GitReverseSynthesizer.synthesize` | Out of builder scope -- route to the CLI instead |
| EFFECTIVE | Bash, Edit, Glob, Grep, Read, Write | ALLOWED minus DENIED |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[reverse-prompt-builder]] | sibling | 0.61 |
| [[bld_architecture_reverse_prompt]] | sibling | 0.58 |
| [[bld_eval_reverse_prompt]] | sibling | 0.56 |
