---
kind: quality_gate
id: p11_qg_cli_tool
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of cli_tool artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: cli_tool"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, cli-tool, P04, command-line, exit-codes, output-format]
tldr: "Pass/fail gate for cli_tool artifacts: command completeness, exit code semantics, output format declaration, and flag documentation."
domain: "command-line tool definition — point-in-time executables with declared commands, flags, and exit codes"
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
keywords: [command-line tool definition, and exit codes, command completeness, exit code semantics, output format declaration, and flag documentation, quality-gate]
density_score: 0.90
---
## Quality Gate

# Gate: cli_tool
## Definition
| Field | Value |
|---|---|
| metric | cli_tool artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: cli_tool` |
## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^[a-z][a-z0-9_-]+$` | ID contains uppercase, spaces, or invalid chars |
| H03 | ID equals filename stem | `id: my_tool` but file is `other_tool.md` |
| H04 | Kind equals literal `cli_tool` | `kind: script` or `kind: skill` or any other value |
| H05 | Quality field is null | `quality: 7.5` or any non-null value |
| H06 | All required fields present | Missing `commands`, `output_format`, or `exit_codes` |
## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Command coverage | 1.0 | All meaningful operations exposed as named commands or subcommands |
| Flag documentation | 1.0 | Each flag has name, type, default, and description; no undocumented flags |
| Exit code semantics | 1.0 | Each exit code has specific meaning (not generic "error"); maps to failure category |
| Output format consistency | 0.5 | All commands produce the same declared output format |
| Config file documentation | 0.5 | Config file path and schema documented if tool supports config files |
| Env var overrides | 0.5 | Environment variable overrides listed for key settings |
## Actions
| Score | Tier | Action |
|---|---|---|
| >= 9.5 | Golden | Publish to pool as golden reference |
| >= 8.0 | Publish | Publish to pool, add to routing index |
| >= 7.0 | Review | Flag for improvement before publish |
| < 7.0 | Reject | Return to author with specific gate failures |
## Bypass
| Field | Value |
|---|---|
| conditions | Internal debug tool used only during development, never shipped to end users |
| approver | Author self-certification with comment explaining debug-only scope |
| audit_trail | Bypass note in frontmatter comment with expiry date |
| expiry | 14d — debug tools must be promoted to >= 7.0 or removed from repo |
| never_bypass | H01 (unparseable YAML breaks all tooling), H05 (self-scored gates corrupt quality metrics) |

## Examples

# Examples: cli-tool-builder
## Golden Example
INPUT: "Create CLI tool for validating CEX artifacts against their schema"
OUTPUT:
```yaml
id: p04_cli_artifact_validator
kind: cli_tool
pillar: P04
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder_agent"
name: "CEX Artifact Validator"
commands:
  - validate
  - check_schema
  - list_kinds
output_format: json
exit_codes:
  0: "all gates passed"
  1: "hard gate failure"
  2: "soft score below threshold"
  3: "file not found or unreadable"
quality: null
tags: [cli_tool, validator, artifact, P04]
tldr: "Artifact validator CLI: 3 commands, JSON output, validates HARD+SOFT gates"
description: "CLI tool validating CEX artifacts against pillar schemas with HARD/SOFT gate scoring"
config_file: ".cex/validator.yaml"
verbose: true
interactive: false
env_vars: ["CEX_ROOT", "CEX_STRICT"]
platforms: [linux, macos, windows]
```
## Overview
Validates CEX artifacts against their pillar schema definitions.
Used by builders after production and by CI pipelines for quality enforcement.
## Commands
### validate
`cex-validate validate <file> [--strict] [--verbose]`
Validates a single artifact against its kind schema.
Flags:
- `--strict`: fail on any SOFT gate below 8.0 (default: warn only)
- `--verbose`: show each gate check with pass/fail detail
Args:
- `<file>` (path, required): artifact file to validate
Returns: JSON {passed, hard_gates, soft_score, failures[]}
### check_schema
`cex-validate check-schema <kind>`
Prints the schema for a given kind.
Args:
- `<kind>` (string, required): artifact kind (e.g., "client", "mcp_server")
Returns: JSON schema definition
### list_kinds
`cex-validate list-kinds [--pillar P04]`
Lists all registered artifact kinds.
Flags:
- `--pillar` (string, optional): filter by pillar
Returns: JSON [{kind, pillar, core, max_bytes}]
## Output
- stdout: JSON results (parseable by downstream tools)
- stderr: human-readable progress and errors
- Exit codes: 0=pass, 1=hard fail, 2=soft fail, 3=file error
## Configuration
Config file: `.cex/validator.yaml` (optional overrides)
Env vars: `CEX_ROOT` (project root), `CEX_STRICT` (enable strict mode)
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p04_cli_ pattern (H02 pass)
- kind: cli_tool (H04 pass)
- 20 required+recommended fields present (H06 pass)
## Anti-Example
INPUT: "Create CLI tool for formatting code"
BAD OUTPUT:
```yaml
id: code-formatter
kind: tool
pillar: tools
name: Formatter
commands: [format]
quality: 9.0
tags: [format]
```
Formats code files.

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
