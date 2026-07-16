---
kind: quality_gate
id: p11_qg_computer_use
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of computer_use artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: computer_use"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, computer-use, P04, gui, screen-control, automation]
tldr: "Pass/fail gate for computer_use artifacts: action listing, resolution format, coordinate system, safety constraints, and screenshot policy."
domain: "GUI control interfaces enabling LLMs to interact with graphical environments via screenshots and coordinate-based actions"
created: "2026-03-28"
updated: "2026-03-28"
8f: "F7_govern"
keywords: [action listing, resolution format, coordinate system, safety constraints, and screenshot policy, quality-gate, computer-use]
density_score: 0.90
related:
  - computer-use-builder
---
## Quality Gate

# Gate: computer_use

This ISO governs computer use: screen capture, mouse, and keyboard actions taken on behalf of the agent.
## Definition
| Field | Value |
|---|---|
| metric | computer_use artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: computer_use` |
## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^p04_cu_[a-z][a-z0-9_]+$` | ID contains uppercase, hyphens, or no p04_cu_ prefix |
| H03 | ID equals filename stem | ID does not match filename |
| H04 | Kind equals literal `computer_use` | `kind: tool` or `kind: gui` or any other value |
| H05 | Quality field is null | `quality: 9.0` or any non-null value |
| H06 | All required fields present | Missing `target`, `resolution`, or `actions_supported` |
## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Action documentation | 1.5 | Each action has parameters with types documented |
| Coordinate system clarity | 1.0 | Origin, direction, units, and resolution explicitly stated |
| Safety constraints | 1.0 | No-credential policy, sandbox requirement documented |
| Screenshot policy | 1.0 | screenshot_mode defined with rationale |
| Resolution justification | 0.5 | Resolution apownte for target with cost consideration |
| Observe-act loop | 0.5 | Loop described in overview |
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
| conditions | Internal testing tool for automation development |
| approver | Author self-certification with test-only scope comment |
| audit_trail | Bypass note in frontmatter with expiry date |
| expiry | 14d — test tools must be promoted or removed |
| never_bypass | H01 (unparseable YAML), H05 (self-scored gates), H08 (no actions = no tool) |

## Examples

# Examples: computer-use-builder

This ISO governs computer use: screen capture, mouse, and keyboard actions taken on behalf of the agent.
## Golden Example
INPUT: "Create computer use tool for browser automation via screenshot-based control"
OUTPUT:
```yaml
id: p04_cu_browser_control
kind: computer_use
pillar: P04
version: "1.0.0"
created: "2026-03-28"
updated: "2026-03-28"
author: "builder_agent"
name: "Browser Screen Control"
target: browser
resolution: "1024x768"
actions_supported:
  - click
  - type
  - scroll
  - key_press
coordinate_system: absolute
screenshot_mode: before_action
safety_constraints:
  - "No credential or password entry"
  - "Sandbox environment only"
  - "No access to banking or payment sites"
quality: 8.8
tags: [computer_use, browser, screen-control, automation, P04]
tldr: "Browser screen control: 6 actions, 1024x768, absolute coords, screenshot before each action"
description: "LLM-driven browser control via screenshots and coordinate-based mouse/keyboard actions"
```
## Overview
Controls a browser window via screenshot capture and coordinate-based actions.
Implements observe-act loop: capture screenshot, LLM interprets visual content, LLM issues action command, repeat.
## Actions
### click
Parameters: x (int), y (int), button (left|right, default: left)
Behavior: moves cursor to (x, y) and clicks specified button
### type
Parameters: text (string)
Behavior: types text at current cursor/focus position
### scroll
Parameters: direction (up|down), amount (int, pixels)
Behavior: scrolls viewport in specified direction
### key_press
Parameters: key (string, e.g., "Enter", "Tab", "Escape")
Behavior: presses specified key
### screenshot
Parameters: none
Returns: base64 PNG image of current viewport
### double_click
Parameters: x (int), y (int)
Behavior: double-clicks at (x, y)
## Coordinate System
Origin: top-left corner (0, 0)
Direction: x increases rightward, y increases downward
Units: pixels
Resolution: 1024x768 — all coordinates must fall within this space
## Safety
- No credential or password entry — LLM must never type passwords
- Sandbox environment only — no bare-metal browser access
- No access to banking, payment, or authentication-sensitive sites
- Screenshot frequency prevents blind actions
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p04_cu_ pattern (H02 pass)
- kind: computer_use (H04 pass)
- target: browser (valid enum, H06 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
