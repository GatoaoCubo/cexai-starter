---
id: p04_cli_kc_validator_n04
kind: cli_tool
8f: F5_call
pillar: P04
title: "KC Validator -- Knowledge Card Quality Gate"
version: 1.1.0
created: 2026-04-07
updated: "2026-07-20"
author: n04_knowledge
domain: knowledge-quality
quality: null
tags: [tool, n04, kc-validator, quality, frontmatter, density, validation]
tldr: "CLI tool to validate knowledge cards: frontmatter completeness, density scoring, size limits, cross-ref verification, structural compliance. Pre-commit + CI-pipeline gate."
keywords: [kc validator, knowledge card quality gate, frontmatter completeness, density scoring, size limits, cross-ref verification, structural compliance, tool, kc-validator, quality, anti-pattern, filler-detection]
density_score: null
related:
  - validate
  - p05_cg_cex
  - p11_fb_path_config
slots:
  command: "<the subcommand to run>"
  args: "<the CLI arguments>"
---

# KC Validator Tool

> **Status: proposed specification (not yet implemented).** This artifact documents
> the DESIGN of a dedicated CLI tool (`_tools/kc_validator.py` -- proposed, not yet
> implemented) that does not exist in this repository today -- no command on this
> page runs. Treat the content below as a blueprint for a future implementation,
> not as a manual for a tool already in production. For validation that DOES run
> today over frontmatter, density, size, and wikilinks (repo-wide, not restricted
> to knowledge cards), see `_tools/cex_doctor.py`.

## Purpose

Validates knowledge cards against the KC Structure Contract before they enter the knowledge graph. Catches defects at creation time, not during audits.

## Usage (proposed CLI -- not yet implemented)

```bash
# PROPOSED spec below -- _tools/kc_validator.py does not exist on disk today.
# Validate single KC
python _tools/kc_validator.py validate path/to/kc.md  # proposed, not yet implemented

# Validate all KCs in a directory
python _tools/kc_validator.py validate P01_knowledge/library/kind/ --recursive  # proposed, not yet implemented

# Density-only check (fast)
python _tools/kc_validator.py density path/to/kc.md  # proposed, not yet implemented

# Generate validation report
python _tools/kc_validator.py report --output N04_knowledge/P05_output/kc_validation_report.md  # proposed, not yet implemented
```

## Checks Performed

| Check | Rule | Severity |
|-------|------|----------|
| **Frontmatter completeness** | All 14 required fields present | Critical |
| **Kind validity** | `kind` exists in `.cex/kinds_meta.json` | Critical |
| **Pillar validity** | `pillar` matches `P{01-12}` pattern | Critical |
| **Tag format** | `lowercase-kebab-case`, 3-10 tags | Major |
| **Size limit** | <=2KB focused, <=4KB comprehensive | Major |
| **Section order** | H1 -> Core -> Tables -> Integration | Minor |
| **Density score** | >=0.8 (filler ratio < 20%) | Major |
| **Cross-ref validity** | All `see:` and `related:` links resolve | Major |
| **Code syntax** | Code blocks parse without errors | Minor |
| **quality: null** | New KCs must have `quality: null` | Critical |

## Filler Detection Patterns

| Pattern | Category |
|---------|----------|
| `In this KC we will discuss...` | Meta-commentary |
| `As mentioned above...` | Self-reference |
| `It is important to note that...` | Hedging |
| `This powerful/amazing/great...` | Self-promotion |
| `Let's take a look at...` | Conversational filler |
| Repeated adjectives | Redundancy |

## Output Format

```
[PASS] path/to/good_kc.md (density: 0.93, size: 1.8KB)
[FAIL] path/to/bad_kc.md
  [X] CRITICAL: missing frontmatter field 'tldr'
  [X] MAJOR: density 0.71 (below 0.80 threshold)
  [X] MINOR: section order violation (Tables before Core)

Summary: 45/50 PASS, 5 FAIL (3 critical, 4 major, 2 minor)
```

## Severity Mapping

| Severity | Doctor state | Effect | Examples |
|----------|--------------|--------|----------|
| CRITICAL | FAIL (BLOCKING) | Halt build; no publication | missing kind, broken YAML, quality not null |
| MAJOR | FAIL (HIGH) | Block + retry F6 once | density < 0.80, broken wikilink |
| MINOR | WARN (MEDIUM) | Log + proceed | section order, missing optional field |
| INFO | PASS (OBSERVATION) | Style suggestion | could be denser |

Mapping rule: aligns with `.claude/rules/8f-reasoning.md` Severity Matrix.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All KCs passed |
| 1 | One or more CRITICAL failures (blocks commit / CI) |
| 2 | One or more MAJOR failures (gates publish) |
| 3 | Only MINOR failures (warning, non-blocking) |

## Integration

| Hook | Trigger | Action |
|------|---------|--------|
| Pre-commit | `git add *.md` | Auto-validate staged KCs |
| 8F F7 gate | `cex_score.py --dry-run` | Block publish below threshold |
| CI pipeline | PR merge to main | Validate all changed KCs |
| Batch audit | `cex_evolve.py` loop | Feed defects to AutoResearch |
| Daily cron | overnight evolve | Refresh stale + low-density KCs |

## Configuration

Default config can be overridden via `--config` flag or `.cex/kc_validator.yaml`:

```yaml
density_min: 0.80
density_target: 0.85
size_focused_max_kb: 2
size_comprehensive_max_kb: 4
size_hard_cap_kb: 8
required_fields:
  - id
  - kind
  - pillar
  - title
  - version
  - created
  - author
  - domain
  - quality
  - tags
  - tldr
  - keywords
filler_patterns:
  - "in this kc"
  - "as mentioned"
  - "it is important"
  - "let's take a look"
sectioning:
  enforce_h1_match_title: true
  enforce_section_order: true
```

## Anti-Patterns Detected

| Anti-pattern | Severity | Auto-fixable? |
|--------------|----------|----------------|
| `quality: 8.5` on creation | CRITICAL | YES (set to null) |
| Two `quality:` keys in frontmatter | CRITICAL | YES (collapse to null) |
| Missing `tldr` | CRITICAL | NO (manual write) |
| Density < 0.80 | MAJOR | NO (manual rewrite) |
| Tag duplicates kind/pillar | MINOR | YES (auto-strip) |
| Section ordering | MINOR | NO (manual move) |
| Wikilink target missing | MAJOR | NO (manual fix or `cex_index.py` proposal) |
| Non-ASCII in code blocks | MAJOR | YES (`cex_sanitize.py --fix`) |

### Procedure

```text
1. Load this artifact and read its contract under F5 CALL.
2. Bind command and args from the incoming request.
3. Validate the inputs against the constraints declared above.
4. Execute the cli_tool behavior; resolve each open slot at act-time.
5. Verify the output shape, then signal completion to the orchestrator.
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[validate]] | downstream | 0.28 |
| [[p05_cg_cex]] | downstream | 0.25 |
| [[p11_fb_path_config]] | downstream | 0.22 |
