---
id: p09_path_n03
kind: path_config
8f: F1_constrain
pillar: P09
nucleus: n03
title: Engineering Path Config
version: 1.0
quality: null
tags: [config, paths, engineering, filesystem, n03, constrain]
tldr: "N03's authoritative filesystem map: where source markdown, compiled YAML, handoffs, and signals live -- so builds and validation resolve paths from one source, not hardcoded strings."
when_to_use: "Load (F1 CONSTRAIN) before any N03 read/write to resolve a canonical path. Consult for 'where does N03 put source vs compiled artifacts, and read handoffs/signals?'"
primary_8f: CONSTRAIN
keywords: [filesystem map, source markdown, compiled stage, yaml output, mission fit, artifact, orchestration, access control, handoffs]
density_score: 0.95
related:
  - p09_env_n03
---

# Engineering Path Config

### How to use

```text
8F verb: CONSTRAIN (F1). Tools resolve N03 paths through this map instead of
hardcoding strings. Fill the open slots below to retarget a nucleus's roots, then
re-derive the Values table. Source markdown and compiled output stay in separate
roots; handoffs + signals are read-only inbound surfaces.
```

```yaml
nucleus_root: {{nucleus_root}}      # e.g. N03_engineering/
source_glob: {{source_glob}}        # where authored .md live (P01..P12 subdirs)
compiled_root: {{compiled_root}}    # where the compile step writes .yaml
handoffs_path: {{handoffs_path}}    # .cex/runtime/handoffs/** (read-only)
signals_path: {{signals_path}}      # .cex/runtime/signals/** (signal write surface)
```

## Purpose

| Field | Value |
|-------|-------|
| Mission fit | Canonical filesystem map for N03 source, compiled, runtime, and signal paths |
| Pride lens | Paths are named, bounded, and separated by ownership so no artifact wanders |
| Primary use | Guide builders, validators, and orchestration around where N03 reads and writes |
| Boundary | Filesystem locations only; access control lives in `permission` |
| Base anchor | `CEX_ROOT` |
| Failure prevented | User-specific hardcoding and accidental writes into shared sources |

## Values

| Alias | Relative path | Mode | Scope | Rule |
|-------|---------------|------|-------|------|
| `n03_root` | `N03_engineering/` | read_write | all | Home boundary for nucleus-owned artifacts |
| `n03_schemas` | `N03_engineering/P06_schema/` | read_write | schema builds | Source markdown for P06 outputs |
| `n03_config` | `N03_engineering/P09_config/` | read_write | config builds | Source markdown for P09 outputs |
| `n03_compiled` | `N03_engineering/compiled/` | read_write | compile stage | Generated YAML output only |
| `n03_output` | `N03_engineering/P05_output/` | read_write | reports | Human-oriented generated reports |
| `handoff_root` | `.cex/runtime/handoffs/` | read_only | mission | Upstream task source |
| `signal_root` | `.cex/runtime/signals/` | read_write | mission | Completion signaling |
| `builder_root` | `archetypes/builders/` | read_only | context load | Builder manifests and ISOs |
| `kind_kc_root` | `P01_knowledge/library/kind/` | read_only | context load | Kind knowledge cards |
| `tool_root` | `_tools/` | read_only | compile, validate | Tooling invoked by N03 |

## Resolution Rules

| Rule ID | Statement | Why it matters |
|---------|-----------|----------------|
| `P01` | All writable aliases resolve under `CEX_ROOT` | Prevents off-repo drift |
| `P02` | Read-only aliases must never be used as output targets | Protects shared references |
| `P03` | `n03_compiled` is generated-only and should not host authored markdown | Clean source/output separation |
| `P04` | Mission execution reads handoffs from runtime paths but writes artifacts only inside N03-owned areas | Orchestrator dispatch remains upstream |
| `P05` | Absolute paths may appear only after resolution, never as stored config values | Portability first |

## Rationale

| Design choice | Why it exists |
|---------------|---------------|
| Alias-based mapping | Names carry meaning and reduce path copy errors |
| Separate source and compiled roots | Human-authored markdown and generated YAML should never blur |
| Read-only context roots | Shared knowledge and builder inputs are not casual scratch space |
| Runtime paths included | Mission work uses real handoffs and signals, not theoretical ones |
| No user-specific absolute defaults | The config should survive machine changes |

## Example

```yaml
base_dir: ${CEX_ROOT}
paths:
  n03_root: N03_engineering/
  n03_schemas: N03_engineering/P06_schema/
  n03_config: N03_engineering/P09_config/
  n03_compiled: N03_engineering/compiled/
  handoff_root: .cex/runtime/handoffs/
  signal_root: .cex/runtime/signals/
readonly:
  - archetypes/builders/
  - P01_knowledge/library/kind/
  - P06_schema/
  - P09_config/
resolution:
  absolute_allowed_at_runtime_only: true
```

## Properties

| Property | Value |
|----------|-------|
| Nucleus | `n03` |
| Pillar | `P09` |
| Kind | `path_config` |
| Aliases | `10` |
| Base anchor | `${CEX_ROOT}` |
| Lens | `Inventive Pride` |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p09_env_n03]] | related | 0.27 |
