---
kind: tools
id: bld_tools_output_template
pillar: P04
llm_function: CALL
purpose: Tools and APIs available for output_template production
quality: null
title: "Tools Output Template"
version: "1.0.0"
author: n03_builder
tags: [output_template, builder, examples]
tldr: "Golden and anti-examples for output_template construction, demonstrating the reflexive-vs-broader usage split and the 3-way naming drift resolution."
domain: "output_template construction"
created: "2026-07-07"
updated: "2026-07-07"
8f: "F5_call"
keywords: [output_template construction, tools output template, output_template, builder, examples, production tools, data sources, tool permissions, interim validation, related artifacts]
density_score: 0.87
related:
  - bld_tools_kind
  - bld_tools_prompt_template
  - bld_tools_response_format
  - bld_tools_formatter
  - bld_schema_output_template
---

# Tools: output-template-builder
## Production Tools
| Tool | Purpose | When | Status |
|------|---------|------|--------|
| brain_query [MCP] | Search existing output_templates in pool | Phase 1 (check duplicates) | CONDITIONAL |
| Grep / Glob | Search `N0X_*/P05_output/` for prior art in the target domain | Phase 1 | ACTIVE |
| cex_compile.py | .md -> .yaml/.json compilation of the produced artifact | F8 COLLABORATE | REGISTERED (`.cex/kind_tool_supplement.json` -- kind-specific bucket) |
| cex_schema_hydrate.py | Schema hydration pass over the artifact's frontmatter | Phase 3 | REGISTERED (same bucket) |
| cex_8f_runner.py | Full 8F pipeline runner; also the tool whose H02 gate reads this builder's `bld_schema_output_template.md` ID Pattern section | F1-F8 | REGISTERED (same bucket) |
| cex_materialize.py | Materializes `.claude/agents/{kind}-builder.md` sub-agent files from `kinds_meta.json` -- NOT a producer of output_template ARTIFACTS themselves (a common miscue: this tool generates the SUB-AGENT MIRROR, not a `bld_output_{{kind}}.md` ISO nor a broader-usage instance) | One-time, per new kind-builder | REGISTERED (same bucket) |
## Real Implementation Touchpoints (grounding, not production tools)
These are the REAL files a output_template artifact's own SCHEMA/CONFIG describe -- read
them to verify naming/usage claims before producing, but do not treat them as CLI tools
this builder invokes:
| Module | Role |
|--------|------|
| `N00_genesis/P05_output/kind_output_template/kind_manifest_n00.md` | R-298: the honest naming-drift investigation this builder resolves (not silently blesses) |
| `.cex/kinds_meta.json` (`output_template` entry) | boundary, REGISTERED naming, max_bytes, depends_on=[], core=true |
| `N06_commercial/P05_output/output_brand_config.md` | Reference genuine BLANK template (Mustache-style, 41 vars, 7 sections) |
| `N07_admin/P05_output/output_orchestration_audit.md` | Reference COMPLETED-REPORT usage (not blank -- proves the dual-usage split) |
| `_tools/cex_8f_runner.py` (lines ~340-368, `extract_id_pattern`/`extract_id_pattern_section`) | The LIVE H02 extractor this schema's `## ID Pattern` section feeds |
| `_tools/cex_wave_validator.py` (`ID_PATTERN_RE`, `check_h02_id_pattern`) | The pre-commit ISO gate; requires a backtick `` `^...$` `` pattern anywhere in `bld_schema_output_template.md` |
## Data Sources
| Source | Path/URL | Data |
|--------|----------|------|
| CEX Schema | P05_output/_schema.yaml (via N00_genesis pillar schemas) | Field definitions for output_template |
| kinds_meta.json | `.cex/kinds_meta.json` (output_template entry) | boundary, naming, max_bytes, depends_on, core, nucleus |
| kind_tool_supplement.json | `.cex/kind_tool_supplement.json` | `kind_to_tools["output_template"]` = [cex_compile.py, cex_schema_hydrate.py, cex_8f_runner.py, cex_materialize.py] -- a kind-SPECIFIC bucket (not the generic 4-tool bucket shared by field_manifest/approval_request) |
| Real corpus | `N0[2-7]_*/P05_output/output_*.md` (18 real instances) | Both usages: blank templates and completed reports |
| R-298 manifest | `N00_genesis/P05_output/kind_output_template/kind_manifest_n00.md` | The naming-drift investigation + this builder's own missing-status admission |
## Tool Permissions

| Category | Tools | Status |
|----------|-------|--------|
| ALLOWED | Read, Write, Edit, Bash, Glob, Grep | Explicitly permitted |
| DENIED | (none) | Explicitly blocked |
| EFFECTIVE | Bash, Edit, Glob, Grep, Read, Write | ALLOWED minus DENIED |

## Interim Validation
No dedicated automated validator exists yet for output_template beyond the generic
7-check `cex_wave_validator.py` (ISO-level) and `cex_8f_runner.py`'s H01-H0N gates
(artifact-level, per `bld_eval_output_template.md`). Manually check each gate:
1. [ ] YAML parses without error
2. [ ] kind == output_template, pillar == P05
3. [ ] depends_on == [] (never populated)
4. [ ] quality is null
5. [ ] id matches the canonical `bld_output_template_{{kind}}` pattern for NEW reflexive-usage work (forward-only gate; the 18 pre-existing broader-usage instances are not retroactively checked against it)
6. [ ] the artifact states explicitly which usage it is (reflexive ISO#9 vs broader recurring-document) and, if broader, which of the 3 documented drift conventions its id follows

## Honesty Note
`cex_materialize.py --dry-run --kind output_template` was evaluated as a candidate
generator for the `.claude/agents/output-template-builder.md` sub-agent mirror during
this scaffold. Its output is a GENERIC skeleton (name/description/model/tools/Kind
Definition table/How You Work/Rules/8F Trace only) -- it does NOT include the `related:`
frontmatter, the "Producer Rail (constitution)" section, or kind-specific custom Rules
that EVERY one of the 9 most-recently-scaffolded sibling sub-agent files carries (verified
by direct read of `field-manifest-builder.md`, `approval-request-builder.md`,
`canonical-product-builder.md`). This builder's own sub-agent mirror was therefore
HAND-AUTHORED to match the sibling convention exactly, per this task's explicit
instruction, rather than accepting the thinner mechanical output -- disclosed here so a
future reader does not assume `cex_materialize.py` was silently skipped by oversight.

## Metadata

```yaml
id: bld_tools_output_template
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply bld-tools-output-template.md
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_tools_kind | sibling (reflexive-case source) | 0.50 |
| bld_tools_prompt_template | sibling (contrast) | 0.40 |
| [[bld_tools_response_format]] | sibling (contrast) | 0.36 |
| [[bld_tools_formatter]] | sibling (contrast) | 0.34 |
| [[bld_schema_output_template]] | upstream | 0.32 |
