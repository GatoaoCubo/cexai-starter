---
kind: config
id: bld_config_output_template
pillar: P09
llm_function: CONSTRAIN
purpose: Naming conventions, file paths, size limits, operational constraints
pattern: CONFIG restricts SCHEMA, never contradicts it
effort: low
max_turns: 15
disallowed_tools: []
fork_context: null
hooks:
  pre_build: null
  post_build: null
  on_error: null
  on_quality_fail: null
permission_scope: nucleus
quality: null
title: "Config Output Template"
version: "1.0.0"
author: n03_builder
tags: [output_template, builder, examples]
tldr: "Golden and anti-examples for output_template construction, demonstrating the reflexive-vs-broader usage split and the 3-way naming drift resolution."
domain: "output_template construction"
created: "2026-07-07"
updated: "2026-07-07"
8f: "F1_constrain"
keywords: [naming conventions, file paths, size limits, operational constraints, output_template construction, config output template, output_template, builder, examples, "bld_output_template_{{kind}}.md"]
density_score: 0.87
related:
  - bld_schema_output_template
  - bld_config_kind
  - bld_config_prompt_template
  - bld_output_template_output_template
  - bld_config_field_manifest
---
# Config: output_template Production Rules
## Naming Convention
| Scope | Convention | Example | Status |
|-------|-----------|---------|--------|
| Artifact id (reflexive usage, NEW) | `bld_output_template_{{kind}}` | `bld_output_template_field_manifest` | CANONICAL -- per kinds_meta.json |
| Artifact id (broader usage, real corpus, Convention A) | `p05_out_{{slug}}` | `p05_out_cf_actions_and_distribution` | DRIFT -- 1/18 real instances |
| Artifact id (broader usage, real corpus, Convention B) | `{{nucleus}}_output_{{slug}}` | `n06_output_brand_config` | DRIFT -- 13/18 real instances |
| Artifact id (broader usage, real corpus, Convention C) | `{{nucleus}}_{{slug}}` (no "output" marker) | `n02_readme_hero` | DRIFT -- 4/18 real instances, all `*_readme_*` |
| Artifact filename (real corpus, 18/18 consistent) | `output_{{slug}}.md` (no nucleus/pillar prefix) | `output_brand_config.md` | UNIVERSAL, but != id stem in every case |
| Builder directory | kebab-case | `output-template-builder/` | this scaffold |
| Frontmatter fields | snake_case | `depends_on`, `primary_8f` | universal |
Rule: id MUST equal filename stem -- **NOT enforced for this kind** (0/18 real instances
comply; see `bld_schema_output_template.md` "Filename vs id" section for the full evidence).
This is a deliberate, evidence-based deviation from the field_manifest/approval_request
precedent (both of which DO enforce id == filename stem), not an oversight.
## File Paths
1. Reflexive usage (new kind-builder ISO#9): `archetypes/builders/{{kind}}-builder/bld_output_{{kind}}.md`
2. Broader usage (recurring output document): `N0X_{{nucleus}}/P05_output/output_{{slug}}.md`
   (matches all 18 real instances' actual location convention)
3. Compiled: `{{nucleus_dir}}/compiled/output_{{slug}}.yaml` (via `cex_compile.py`)
4. Reference corpus (read-only grounding, not an output path):
   `N00_genesis/P05_output/kind_output_template/kind_manifest_n00.md` (R-298 manifest)
## Size Limits (aligned with SCHEMA -- per kinds_meta.json)
1. Body: max 8192 bytes
2. Total: ~9000 bytes including frontmatter
3. Density: >= 0.80
## depends_on (fixed by kinds_meta.json -- do not vary per-instance)
`[]` -- EMPTY. output_template is the ONE kind among its 2026-07-03-scaffolded siblings
(field_manifest, approval_request, canonical_product, content_factory, content_library,
fabrication_manifest, prompt_package, reverse_prompt, tenant_voice_profile -- all of which
declare 1-3 upstream dependencies) that depends on NOTHING. Never add an entry without a
`.cex/kinds_meta.json` edit, which is explicitly out of scope for this builder.
## Usage Declaration Policy (this kind's own operational quirk)
1. Every produced instance MUST state, in its body (not just an internal author note),
   whether it is REFLEXIVE (a kind-builder's own ISO#9) or BROADER (a recurring output
   document) -- the two have different consumers and different shapes
2. A BROADER instance MUST disclose which of Convention A/B/C its id follows if it does
   not use the canonical pattern (most broader instances will not, per the corpus evidence)
3. A REFLEXIVE instance MUST use the canonical `bld_output_template_{{kind}}` id --
   this is the one sub-case where the corpus (all 317 kind-builders' ISO#9 files) and
   the canonical pattern already agree
## Naming Convention for pillar (a minor, secondary drift axis)
`pillar: P05` always for NEW instances. 1/18 real instances
(`n07_output_orchestration_audit.md`) drifted to `pillar: P12` (matching its DOMAIN,
orchestration, rather than its KIND's own registered pillar). Not repeated going forward;
disclosed, not silently normalized away.

## Metadata

```yaml
id: bld_config_output_template
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply bld-config-output-template.md
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_output_template]] | upstream | 0.42 |
| bld_config_kind | sibling (reflexive-case source) | 0.38 |
| bld_config_prompt_template | sibling (contrast) | 0.36 |
| [[bld_output_template_output_template]] | upstream | 0.33 |
| bld_config_field_manifest | sibling | 0.30 |
