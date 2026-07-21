## Context Self-Selection Protocol (G8)

When you receive a task (via handoff or interactive), automatically discover and load relevant context BEFORE producing output.

> **[DISTILL ANNOTATION]** Adapted from Central's `.cex/P09_config/context_self_select.md`
> for this tenant's actual shipped paths/tools. Three adaptations: the kind-KC library and
> pillar schemas live only under `N00_genesis/` here (not duplicated per operational
> nucleus); this tenant's example library is one full walkthrough
> (`examples/06_full_lifecycle/`), not a per-kind `P01_knowledge/examples/ex_{kind}_*.md`
> set; and the Central-only `cex_handoff_composer.py` auto-discovery composer is not
> shipped here -- `cex_retriever.py --query` is the equivalent lookup. Everything else
> matches Central exactly.

### Priority Order

1. **Handoff file**: If `.cex/runtime/handoffs/{nucleus}_task.md` has `auto_composed: true`
   frontmatter, context is pre-resolved. Load the paths listed in its "Context
   (auto-discovered)" section. This tenant is solo-operator (see `AGENTS.md`) -- there is
   no multi-tenant handoff path variant to resolve here.

2. **Manual scan**: If no auto-composed handoff, identify the artifact kinds in your task, then load:
   - **Knowledge Card**: `N00_genesis/P01_knowledge/library/kind/kc_{kind}.md` -- definitions, boundaries, naming
   - **Builder ISOs**: `archetypes/builders/{kind}-builder/bld_*.md` -- instructions, templates, examples, scoring
   - **Pillar schema**: `N00_genesis/P{XX}_*/_schema.yaml` -- required frontmatter fields
   - **Examples**: `examples/` -- currently one full walkthrough (`examples/06_full_lifecycle/`).
     Check the builder ISO's own worked example first if you need a per-kind reference.

3. **Programmatic discovery**: For complex or multi-kind tasks, run:
   ```
   python _tools/cex_retriever.py --query "<your task>" --top-k 5
   ```
   TF-IDF semantic search over every artifact's frontmatter + body preview. Narrow with
   `--kind <kind>` or `--pillar <PXX>`; `--examples <kind>` finds gold-standard references
   for one kind. Build the index once with `--build` (see `QUICKSTART.md`) -- until then
   this returns empty results, not an error.

### Rules

- **Load before produce**: Never generate an artifact without first reading its KC + at least the builder instruction ISO.
- **Kind registry**: `.cex/kinds_meta.json` maps every kind to its pillar, description, and naming convention.
- **Decision manifest**: `.cex/runtime/decisions/decision_manifest.yaml` contains user decisions. Do NOT re-ask what's already decided.
- **Frontmatter is mandatory**: Every artifact must have YAML frontmatter matching the pillar schema.
- **8F applies**: The kind you resolve feeds F1 CONSTRAIN; the context you load feeds F3 INJECT. Skip nothing.

### Prompt Compiler (Intent Resolution)
Source of truth: `N00_genesis/P03_prompt/layers/p03_pc_cex_universal.md`
Always resolve intent through this artifact before acting. It maps natural language (EN-first, community languages extensible) to `{kind, pillar, nucleus, verb}` tuples for all 300+ CEX kinds.
