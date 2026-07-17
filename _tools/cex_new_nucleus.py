#!/usr/bin/env python3
# -*- coding: ascii -*-
"""cex_new_nucleus -- CANONICAL scaffolder for community vertical nuclei.

This is the SINGLE SOURCE OF TRUTH for nucleus scaffolding (N08+). The
legacy `cex_new_nucleus_scaffold.py` is now a thin deprecation shim that
delegates here.

The OSS extensibility kit for CEXAI: any user can add N08, N09, N10... in one
command. The tool generates the 12-pillar fractal + 9 required assets per
.claude/rules/new-nucleus-bootstrap.md, ready for content.

Usage:
    python _tools/cex_new_nucleus.py 08 healthcare gluttony
    python _tools/cex_new_nucleus.py 09 fintech greed --dry-run
    python _tools/cex_new_nucleus.py 10 edtech pride --json

Positional args:
    nucleus_num : 08-99 (validated as 2-digit, > 07)
    domain      : snake_case slug (healthcare, fintech, edtech)
    sin         : one of envy/lust/pride/gluttony/wrath/greed/sloth (case-insensitive)

Exit codes:
    0 -- success (apply or dry-run)
    1 -- validation failure (bad args, target exists)
    2 -- runtime error (filesystem, doctor)

Constraints:
    - ASCII-only source (Windows cp1252 safe)
    - Cross-platform via pathlib (no shell calls except cex_doctor.py)
    - Does NOT auto-commit (user reviews + commits)
    - Does NOT actually create N08 in this repo when run with default args -- it's a TOOL
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Repo root resolution -- no hardcoded paths
# ---------------------------------------------------------------------------

def find_repo_root() -> Path:
    for var in ("CLAUDE_PROJECT_DIR", "CEX_ROOT"):
        val = os.environ.get(var)
        if val and Path(val).is_dir():
            return Path(val).resolve()
    return Path(__file__).resolve().parent.parent


REPO = find_repo_root()

# ---------------------------------------------------------------------------
# Sin lens registry -- maps the 7 deadly sins to optimization bias
# Aligned with .claude/rules/new-nucleus-bootstrap.md and the existing 7 nuclei.
# ---------------------------------------------------------------------------

SIN_LENS = {
    "envy":     {"label": "Comparative Envy",   "bias": "competitive analysis, benchmarking",        "best_for": "research, intelligence"},
    "lust":     {"label": "Creative Lust",      "bias": "creative output, aesthetic",                 "best_for": "marketing, design"},
    "pride":    {"label": "Inventive Pride",    "bias": "technical excellence, precision",            "best_for": "engineering, code"},
    "gluttony": {"label": "Knowledge Gluttony", "bias": "data completeness, depth, volume",           "best_for": "knowledge, documentation"},
    "wrath":    {"label": "Gating Wrath",       "bias": "quality gating, enforcement, regulation",    "best_for": "operations, testing, compliance"},
    "greed":    {"label": "Strategic Greed",    "bias": "revenue, monetization, optimization",        "best_for": "commercial, sales"},
    "sloth":    {"label": "Orchestrating Sloth","bias": "delegation, efficiency, automation",         "best_for": "orchestration"},
}

PILLARS = [
    ("P01", "knowledge"),
    ("P02", "model"),
    ("P03", "prompt"),
    ("P04", "tools"),
    ("P05", "output"),
    ("P06", "schema"),
    ("P07", "evals"),
    ("P08", "architecture"),
    ("P09", "config"),
    ("P10", "memory"),
    ("P11", "feedback"),
    ("P12", "orchestration"),
]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_args(num: str, domain: str, sin: str) -> tuple[str, str, str, list[str]]:
    """Return (nuc_id, domain, sin_key, errors). nuc_id is 'n08'."""
    errors: list[str] = []

    # Nucleus number: 2-digit, 08-99
    if not re.match(r"^\d{2}$", num):
        errors.append(f"nucleus_num must be 2 digits (got '{num}')")
    else:
        n = int(num)
        if n < 8:
            errors.append(f"nucleus_num must be >= 08 (N00-N07 reserved, got '{num}')")
        if n > 99:
            errors.append(f"nucleus_num must be <= 99 (got '{num}')")

    # Domain: snake_case slug
    if not re.match(r"^[a-z][a-z0-9_]{1,40}$", domain):
        errors.append(f"domain must be lowercase snake_case (got '{domain}')")

    # Sin: must be one of the seven
    sin_key = sin.lower().strip()
    if sin_key not in SIN_LENS:
        errors.append(f"sin must be one of {sorted(SIN_LENS)} (got '{sin}')")

    nuc_id = f"n{num}" if not errors else ""
    return nuc_id, domain, sin_key, errors


def check_collision(nuc_id: str, domain: str) -> list[str]:
    """Return list of paths that already exist (collision errors)."""
    collisions: list[str] = []
    target_dir = REPO / f"N{nuc_id[1:]}_{domain}"
    if target_dir.exists():
        collisions.append(f"target dir already exists: {target_dir.relative_to(REPO)}")
    boot_main = REPO / "boot" / f"{nuc_id}.ps1"
    if boot_main.exists():
        collisions.append(f"boot script already exists: {boot_main.relative_to(REPO)}")
    settings = REPO / ".claude" / "nucleus-settings" / f"{nuc_id}.json"
    if settings.exists():
        collisions.append(f"nucleus settings already exists: {settings.relative_to(REPO)}")
    return collisions


# ---------------------------------------------------------------------------
# Asset templates (9 required assets per new-nucleus-bootstrap.md)
# ---------------------------------------------------------------------------

def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


# ---------------------------------------------------------------------------
# Shared frontmatter scaffolding (R-129 de-dup: drift-risk reduction)
# ---------------------------------------------------------------------------
# These 3 literal tokens + the created/updated pair were repeated verbatim
# across all 5 markdown-asset render_* functions below (rule file /
# nucleus_def / agent_card / vocabulary KC / component_map). Centralizing them
# means a future convention change (default author, the quality sentinel, the
# starting version) updates in ONE place instead of drifting silently across
# renderers -- this is the actual drift risk R-129 names.
#
# Canonical narrative template on disk: N00_genesis/n00_nucleus_template.md.
# NOT wired in as a runtime read source (deliberately, not an oversight): that
# doc still teaches the pre-2026-07-05 8-asset / P08_architecture-nucleus_def
# convention (nucleus_def filed under P08_architecture; no vocabulary KC,
# component_map, Claude subagent, or scoped-permissions asset at all) -- the
# convention this tool + the CURRENT `.claude/rules/new-nucleus-bootstrap.md`
# 9-asset table implement moved nucleus_def to P02_model on 2026-07-05
# (register rows R-023/R-025/R-026/R-288). Reading n00_nucleus_template.md
# verbatim at runtime today would silently regress every new nucleus back to
# the superseded P08 convention. Left as an explicit REMAINDER (register
# R-129) for whoever reconciles that template doc to the current convention;
# until then, these constants are this tool's own single source of truth.
# ---------------------------------------------------------------------------

_FRONTMATTER_AUTHOR = "cex_new_nucleus"
_FRONTMATTER_QUALITY = "null"
_FRONTMATTER_VERSION_DEFAULT = "1.0.0"


def _created_updated_lines() -> str:
    """The created/updated frontmatter pair, stamped from ONE _today() call so
    both lines always share the identical date (previously two independent
    _today() calls per renderer -- same practical result, one call site now)."""
    d = _today()
    return f'created: "{d}"\nupdated: "{d}"'


def render_rule_file(nuc_id: str, domain: str, sin_key: str) -> str:
    """Asset 1: N{XX}_{domain}/rules/n{xx}-{domain}.md"""
    s = SIN_LENS[sin_key]
    nuc_upper = nuc_id.upper()
    return f"""---
id: {nuc_id}_{domain}
kind: instruction
pillar: P08
glob: "N{nuc_id[1:]}_{domain}/**"
description: "{nuc_upper} {domain.title()} Nucleus -- {s['label']}"
title: "{nuc_upper}-{domain.title()}"
version: "{_FRONTMATTER_VERSION_DEFAULT}"
author: {_FRONTMATTER_AUTHOR}
quality: {_FRONTMATTER_QUALITY}
tags: [nucleus-rules, {nuc_id}, {domain}, {sin_key}]
tldr: "{nuc_upper} ({domain}) identity + 8F customizations under {s['label']} sin lens. Optimization bias: {s['bias']}."
domain: "{domain}"
{_created_updated_lines()}
8f: "F2_become"
---

# {nuc_upper} {domain.title()} Rules

## Identity

1. **Role**: {domain.title()} Nucleus
2. **CLI**: claude (configurable via `.cex/config/nucleus_models.yaml`)
3. **Domain**: {domain} -- {s['best_for']}
4. **Sin Lens**: {s['label']} ({sin_key} family)

## When You Are {nuc_upper}

1. Your artifacts live in `N{nuc_id[1:]}_{domain}/`
2. You operate ONLY inside your nucleus directory
3. You inherit the universal 8F protocol from N00_genesis
4. Your output is shaped by **{s['label']}**: {s['bias']}

## Build Rules

- 8F is your reasoning protocol (see `.claude/rules/8f-reasoning.md`).
  Every task -- research, build, evaluate -- runs F1->F8.
- All artifacts MUST have domain-specific content about {domain}
- `quality: null` (NEVER self-score)
- Compile after save: `python _tools/cex_compile.py {{path}}`
- Vocabulary: load `N{nuc_id[1:]}_{domain}/P01_knowledge/kc_{domain}_vocabulary.md` at F2b SPEAK

## Sin Lens: {s['label']}

Every {nuc_upper} output is shaped by **{s['label']}** -- {s['bias']}.

| Behavior | How {s['label']} Manifests |
|----------|---------------------------|
| F4 REASON tie-break | Trade-offs that favor {sin_key}-aligned outcomes win |
| Output bias | Optimize for: {s['bias']} |
| Domain priority | {s['best_for']} |

## Routing

| Route TO {nuc_upper} | Route AWAY from {nuc_upper} |
|---------------------|-----------------------------|
| {domain}-specific tasks | Build artifacts (N03) |
| Domain knowledge cards | Marketing copy (N02) |
| {domain.title()} workflows | Deploy/test code (N05) |

## Scope

I operate ONLY inside `N{nuc_id[1:]}_{domain}/`. I never modify N00-N07 nuclei
or shared system files (`.claude/settings.json`, `.cex/kinds_meta.json`,
`CLAUDE.md`, `.cex/config/nucleus_models.yaml` outside my own entry).

## Properties

| Property | Value |
|----------|-------|
| Kind | instruction |
| Pillar | P08 |
| Domain | {domain} |
| Pipeline | 8F (F1-F8) |
| Sin family | {sin_key} |
| Quality target | 9.0+ (system default) |
| Density target | 0.85+ |
"""


def render_nucleus_def(nuc_id: str, domain: str, sin_key: str) -> str:
    """Asset 2: N{XX}_{domain}/P02_model/nucleus_def_n{xx}.md"""
    s = SIN_LENS[sin_key]
    nuc_upper = nuc_id.upper()
    return f"""---
id: nucleus_def_{nuc_id}
kind: nucleus_def
pillar: P02
nucleus: {nuc_id}
title: "{nuc_upper} {domain.title()} Nucleus -- Identity"
version: {_FRONTMATTER_VERSION_DEFAULT}
{_created_updated_lines()}
author: {_FRONTMATTER_AUTHOR}
quality: {_FRONTMATTER_QUALITY}
tags: [nucleus_def, {nuc_id}, {domain}, vertical]
tldr: "{nuc_upper} community vertical for {domain}. Sin lens: {s['label']} ({sin_key})."
8f: "F2_become"
---

## Identity

| Field | Value |
|-------|-------|
| Nucleus ID | {nuc_upper} |
| Role | {domain} |
| Sin Lens | {s['label']} ({sin_key}) |
| CLI Binding | claude |
| Model Tier | configurable (see `.cex/config/nucleus_models.yaml`) |
| Context | 200K tokens (default) |
| Boot Script | `boot/{nuc_id}.ps1` |
| Agent Card | `N{nuc_id[1:]}_{domain}/P08_architecture/agent_card_{nuc_id}.md` |

## Pillars Owned

| Pillar | Domain | Sample Kinds (TODO: customize) |
|--------|--------|-------------------------------|
| P01 | knowledge | knowledge_card, glossary_entry |
| P03 | prompt | system_prompt, prompt_template |
| P08 | architecture | agent_card, component_map |

## Domain Scope

{nuc_upper} owns the **{domain}** vertical. It applies the **{s['label']}**
optimization bias ({s['bias']}) to its 8F runs.

## Capabilities

- Builds artifacts in the {domain} domain.
- Inherits the universal 8F protocol from N00_genesis.
- Holds a controlled vocabulary KC at
  `N{nuc_id[1:]}_{domain}/P01_knowledge/kc_{domain}_vocabulary.md`.

## Boundaries

- Does NOT duplicate kinds already covered by N01-N06.
- Does NOT redefine canonical 8F or pillar terms.
- Operates under scoped permissions via
  `.claude/nucleus-settings/{nuc_id}.json`.

## 8F Customizations

The {sin_key} sin lens biases F4 REASON toward {sin_key}-flavored trade-offs.
Otherwise the pipeline is identical to N00_genesis.

## Boot Contract

- Boot file: `boot/{nuc_id}.ps1`
- Task source: `.cex/runtime/handoffs/{nuc_id}_task.md`
- Signal: `write_signal('{nuc_id}', 'complete', {{score}})`
- Signal path: `.cex/runtime/signals/signal_{nuc_id}_*.json`

## Composability

| Direction | Nucleus | What Flows |
|-----------|---------|-----------|
| outbound | N04 | new domain knowledge cards |
| outbound | N07 | task completion signals |
| inbound | N07 | dispatch handoffs |
| inbound | N01 | research findings on {domain} domain |
"""


def render_agent_card(nuc_id: str, domain: str, sin_key: str) -> str:
    """Asset 3: N{XX}_{domain}/P08_architecture/agent_card_n{xx}.md"""
    s = SIN_LENS[sin_key]
    nuc_upper = nuc_id.upper()
    return f"""---
id: agent_card_{nuc_id}
kind: agent_card
pillar: P08
nucleus: {nuc_id}
title: "{nuc_upper} {domain.title()} -- Agent Card"
version: {_FRONTMATTER_VERSION_DEFAULT}
{_created_updated_lines()}
author: {_FRONTMATTER_AUTHOR}
quality: {_FRONTMATTER_QUALITY}
tags: [agent_card, {nuc_id}, {domain}, {sin_key}]
tldr: "Capability declaration for {nuc_upper} ({domain}, sin: {s['label']})."
8f: "F2_become"
---

# {nuc_upper} {domain.title()} -- Agent Card

## Routing

- **Priority**: 5 (default; tune per workload)
- **Keywords**: {domain}, TODO add domain-specific triggers
- **Dispatch**: `bash _spawn/dispatch.sh solo {nuc_id} "task"`

## Identity

| Field | Value |
|-------|-------|
| Nucleus | {nuc_upper} -- {domain.title()} |
| Sin | {s['label']} |
| Domain | {domain} -- {s['best_for']} |
| Optimization bias | {s['bias']} |
| Artifacts dir | `N{nuc_id[1:]}_{domain}/` |
| Routing IN | {domain}-specific tasks |
| Routing OUT | Build (N03), marketing (N02), deploy (N05) |

8F is the reasoning protocol for every task. F1-F8 mandatory.

## Capabilities

- Runs the 8F pipeline for {domain} kinds.
- Reads from `N{nuc_id[1:]}_{domain}/`.
- Writes scoped artifacts only inside `N{nuc_id[1:]}_{domain}/`.

## Tools

Default `_tools/cex_*.py` allowlist. See
`.claude/nucleus-settings/{nuc_id}.json` for scoped permissions.

## Handoff Format

`.cex/runtime/handoffs/{nuc_id}_task.md` -- mandatory frontmatter
(`task: dispatch`, `mission`, `nucleus`, `deliverables`, `quality_floor`).

## Anti-Patterns (Route AWAY)

| Don't Use For | Route To Instead | Why |
|---------------|------------------|-----|
| Build generic artifacts | N03 | {nuc_upper} is domain-scoped |
| Marketing copy | N02 | Creative writing, not {domain} |
| Deploy/test code | N05 | Technical operations |
| Research outside {domain} | N01 | Cross-domain research |

## Inter-Nucleus Handoffs

| From | To {nuc_upper} | What |
|------|---------------|------|
| N07 | dispatch | "Execute {domain} task" |
| N01 | research handoff | "Domain context for {domain}" |

| From {nuc_upper} | To | What |
|------------------|-----|------|
| Domain artifact complete | N04 | New KC for ingestion |
| Task complete | N07 | Signal + summary |
"""


def render_vocabulary_kc(nuc_id: str, domain: str, sin_key: str) -> str:
    """Asset 4: N{XX}_{domain}/P01_knowledge/kc_{domain}_vocabulary.md"""
    s = SIN_LENS[sin_key]
    nuc_upper = nuc_id.upper()
    return f"""---
id: kc_{domain}_vocabulary
kind: knowledge_card
pillar: P01
nucleus: {nuc_id}
domain: {domain}
type: controlled_vocabulary
title: "{nuc_upper} {domain.title()} Domain Controlled Vocabulary"
version: {_FRONTMATTER_VERSION_DEFAULT}
{_created_updated_lines()}
author: {_FRONTMATTER_AUTHOR}
quality: {_FRONTMATTER_QUALITY}
tags: [knowledge_card, controlled_vocabulary, ubiquitous_language, {nuc_id}, {domain}]
tldr: "Canonical vocabulary for {nuc_upper} ({domain}). Loaded at F2b SPEAK to prevent semantic drift across the nucleus."
8f: "F3_inject"
---

## Purpose

This KC implements the Ubiquitous Language Protocol
(`.claude/rules/ubiquitous-language.md`) for the {nuc_upper} {domain} domain.

Loading this KC at F2b SPEAK ensures that:
- All {nuc_upper} outputs use canonical {domain} terminology
- Cross-nucleus communication is unambiguous (LLM-to-LLM interoperability)
- Vocabulary drift is prevented over time

## Canonical Terms (TODO: replace placeholders with real domain vocabulary)

| Term | Industry Definition | {nuc_upper} Domain Application | Anti-Pattern (Never Use) |
|------|--------------------|-------------------------------|--------------------------|
| _term_one_ | _industry definition_ | _how {nuc_upper} uses it_ | _what NOT to say_ |
| _term_two_ | _industry definition_ | _how {nuc_upper} uses it_ | _what NOT to say_ |

## Cross-Nucleus Shared Terms (DO NOT REDEFINE)

These terms are defined in N00_genesis and must NOT be redefined here:

| Term | Definition Source | {nuc_upper} Application |
|------|-------------------|------------------------|
| 8F pipeline | `.claude/rules/8f-reasoning.md` | {nuc_upper} follows F1-F8 for every task |
| kind | `.cex/kinds_meta.json` | {nuc_upper} produces kinds: knowledge_card, ... |
| pillar | N00_genesis P01-P12 | {nuc_upper} primary pillar: P01 (and others) |
| quality_gate | P07 definition | {nuc_upper} quality_gate implements for {domain} |
| signal | F8 COLLABORATE | `write_signal('{nuc_id}', 'complete', score)` |

## Domain-Specific Extensions

Add {domain}-specific terms here as the nucleus matures. Always cite the
industry standard in the second column. Never invent synonyms for terms that
already exist in the 300-kind taxonomy.

## Sin Lens: {s['label']}

The {sin_key} bias affects how {nuc_upper} interprets vocabulary:
- {s['bias']}
- Domain priority: {s['best_for']}

## Vocabulary Load Protocol

At F2b SPEAK:
```
load: N{nuc_id[1:]}_{domain}/P01_knowledge/kc_{domain}_vocabulary.md
load: _docs/specs/spec_metaphor_dictionary.md (Industry term column)
activate: drift_prevention = True
```

All subsequent F3-F8 output must use terms from this KC.
"""


def render_component_map(nuc_id: str, domain: str, sin_key: str) -> str:
    """Asset 5: N{XX}_{domain}/P08_architecture/component_map_n{xx}.md"""
    s = SIN_LENS[sin_key]
    nuc_upper = nuc_id.upper()
    return f"""---
id: component_map_{nuc_id}
kind: component_map
pillar: P08
nucleus: {nuc_id}
title: "{nuc_upper} {domain.title()} -- Component Map"
version: {_FRONTMATTER_VERSION_DEFAULT}
{_created_updated_lines()}
author: {_FRONTMATTER_AUTHOR}
quality: {_FRONTMATTER_QUALITY}
tags: [component_map, {nuc_id}, {domain}, architecture]
tldr: "What {nuc_upper} builds, how components relate, inter-nucleus data flows."
8f: "F4_reason"
---

# {nuc_upper} {domain.title()} -- Component Map

## System Overview

{nuc_upper} is the {domain} nucleus. Its primary function is producing
{domain}-specific artifacts via the 8F pipeline. All output passes
F1->F2->F2b->F3->F4->F5->F6->F7->F8.

**Sin Lens**: {s['label']} -- {s['bias']}.

## Component Inventory

| Component | Type | Path | Role |
|-----------|------|------|------|
| KC Library | knowledge store | `N{nuc_id[1:]}_{domain}/P01_knowledge/` | Domain knowledge cards |
| Vocabulary KC | language layer | `N{nuc_id[1:]}_{domain}/P01_knowledge/kc_{domain}_vocabulary.md` | Controlled vocabulary |
| Tool Pipeline | tool layer | `N{nuc_id[1:]}_{domain}/P04_tools/` | Domain tools (TODO) |
| Eval Stack | quality layer | `N{nuc_id[1:]}_{domain}/P07_evals/` | Quality gates (TODO) |
| Prompt Layer | prompt layer | `N{nuc_id[1:]}_{domain}/P03_prompt/` | Domain templates (TODO) |
| Agent Card | routing | `N{nuc_id[1:]}_{domain}/P08_architecture/agent_card_{nuc_id}.md` | Capability contract |
| Nucleus Def | identity | `N{nuc_id[1:]}_{domain}/P02_model/nucleus_def_{nuc_id}.md` | Machine-readable identity |
| Signal Bus | I/O | `.cex/runtime/signals/signal_{nuc_id}_*.json` | Completion signals |
| Handoff Reader | I/O | `.cex/runtime/handoffs/{nuc_id}_task.md` | Receives tasks from N07 |

## Components

- TODO: list kinds this nucleus produces.
- TODO: list dependencies on N00-N06 kinds.
- TODO: declare any new {domain}-specific kinds (must pass taxonomy hygiene).

## Inter-Nucleus Data Flows

| From | To {nuc_upper} | Trigger | What Arrives |
|------|---------------|---------|--------------|
| N07 | inbound | handoff written | Task + scope + decision manifest |
| N01 | inbound | research result | Domain context for {domain} |

| From {nuc_upper} | To | Trigger | What Flows |
|------------------|-----|---------|------------|
| KC complete | N04 | signal | New {domain} KC for ingestion |
| Task complete | N07 | signal | Completion + score |

## Constraints

| Constraint | Value | Source |
|------------|-------|--------|
| Context window | 200K tokens (default) | nucleus_models.yaml |
| Quality target | 9.0 | quality_gate |
| ASCII-only code | YES | `.claude/rules/ascii-code-rule.md` |
| GDP before subjective | YES | guided-decisions rule |
| Signal on complete | YES | 8F F8 protocol |
| Sin lens bias | {s['label']} | nucleus_def |
"""


def render_subagent(nuc_id: str, domain: str, sin_key: str) -> str:
    """Asset 6: .claude/agents/n{xx}-{domain}.md"""
    s = SIN_LENS[sin_key]
    nuc_upper = nuc_id.upper()
    return f"""---
name: {nuc_id}-{domain}
description: "{nuc_upper} {domain.title()} nucleus sub-agent. Sin lens: {s['label']}. Operates inside N{nuc_id[1:]}_{domain}/. Runs 8F pipeline."
model: sonnet
tools: Read, Write, Edit, Bash, Glob, Grep
---

# {nuc_id}-{domain} Sub-Agent

You are **{nuc_upper}**, the {domain} nucleus.

## Identity

- Sin lens: **{s['label']}** ({sin_key} family)
- Optimization bias: {s['bias']}
- Domain scope: {domain} -- {s['best_for']}
- Artifacts dir: `N{nuc_id[1:]}_{domain}/`

## How You Work

1. Read the handoff at `.cex/runtime/handoffs/{nuc_id}_task.md`
2. Load your rule file: `N{nuc_id[1:]}_{domain}/rules/{nuc_id}-{domain}.md`
3. Load your vocabulary KC: `N{nuc_id[1:]}_{domain}/P01_knowledge/kc_{domain}_vocabulary.md`
4. Execute the 8F pipeline F1->F8 for the requested artifact
5. Save outputs ONLY inside `N{nuc_id[1:]}_{domain}/`
6. Compile: `python _tools/cex_compile.py {{path}}`
7. Signal complete: `python -c "from _tools.signal_writer import write_signal; write_signal('{nuc_id}', 'complete', 9.0)"`

## Rules

- `quality: null` ALWAYS -- never self-score
- Frontmatter MUST parse as valid YAML
- Body MUST stay under the kind's max_bytes
- Follow the kind's naming pattern from `.cex/kinds_meta.json`
- Sin lens bias applies to F4 REASON tie-breaks: prefer {sin_key}-aligned outcomes

## Sin Lens: {s['label']}

Every output you produce is shaped by **{s['label']}**: {s['bias']}.
This is your decision heuristic under ambiguity.
"""


def render_boot_ps1(nuc_id: str, domain: str, sin_key: str) -> str:
    """Asset 7: boot/n{xx}.ps1 (Claude/Windows)"""
    s = SIN_LENS[sin_key]
    nuc_upper = nuc_id.upper()
    return f"""# CEX {nuc_upper} -- CEX-{nuc_upper}-{domain.upper()}
# Auto-generated by cex_new_nucleus.py
# Sin: {s['label']} ({sin_key})
# CLI: claude | Model: resolved at runtime via .cex/config/nucleus_models.yaml

. $PSScriptRoot/_shared/vt_enable.ps1
. $PSScriptRoot/_shared/fix_pathext.ps1
$cexRoot = Split-Path -Parent $PSScriptRoot
$nucleus = "{nuc_id}"
. $PSScriptRoot/_shared/theme.ps1

# Dynamic model resolution (reads nucleus_models.yaml at runtime)
. "$PSScriptRoot\\_shared\\resolve_model.ps1"
$resolved = Resolve-NucleusModel -Nucleus $nucleus -CexRoot $cexRoot

$sinName = "{s['label']}"
$modelShort = $resolved.model -replace "claude-", ""

# Detect mission from handoff file
$mission = ""
$handoff = "$cexRoot\\.cex\\runtime\\handoffs\\${{nucleus}}_task.md"
if (Test-Path $handoff) {{
    $content = Get-Content $handoff -Head 10 -EA SilentlyContinue
    foreach ($line in $content) {{
        if ($line -match "^mission:\\s*(.+)$") {{
            $mission = $Matches[1].Trim()
            break
        }}
    }}
}}

function Set-CexTitle($status) {{
    $t = "{nuc_upper} $sinName"
    if ($mission) {{ $t += " [$mission]" }}
    $t += " -- $status"
    $Host.UI.RawUI.WindowTitle = $t
}}

Set-CexTitle "BOOTING"

try {{
    $Host.UI.RawUI.BackgroundColor = "DarkBlue"
    $Host.UI.RawUI.ForegroundColor = "White"
    Clear-Host
}} catch {{}}

Write-Host ""
Write-Host "  [*] {nuc_upper} $sinName - {domain.title()}" -ForegroundColor Cyan
Write-Host "  ==================================================" -ForegroundColor DarkGray
Write-Host "  Domain: {domain} | Sin: $sinName" -ForegroundColor DarkGray
$ctxK = [math]::Floor($resolved.context / 1000)
Write-Host "  $($resolved.model)  |  ${{ctxK}}K context  |  8F pipeline" -ForegroundColor DarkGray
if ($mission) {{ Write-Host "  Mission: $mission" -ForegroundColor Cyan }}
Write-Host ""

# --- Environment ---
$env:CEX_NUCLEUS = "{nuc_upper}"
$env:CEX_ROOT = $cexRoot
$env:CLAUDE_CODE_USE_POWERSHELL_TOOL = "1"
Set-Location $env:CEX_ROOT

. "$PSScriptRoot\\_shared\\load_dotenv.ps1"

$sysPrompt = @'
You are driven by {s['label']} -- {s['bias']}.
You are {nuc_upper} of CEX. Domain: {domain}.
Read CLAUDE.md, then N{nuc_id[1:]}_{domain}/rules/{nuc_id}-{domain}.md.
IF .cex/runtime/handoffs/{nuc_id}_task.md EXISTS, READ AND EXECUTE IMMEDIATELY.
'@

$initialMsg = @'
Read .cex/runtime/handoffs/{nuc_id}_task.md and execute. If no handoff, report ready.
'@

$cliArgs = @()
foreach ($f in ($resolved.flags -split '\\s+')) {{ if ($f) {{ $cliArgs += $f }} }}
$cliArgs += "--model", $resolved.model, "--name", "CEX-{nuc_upper}"
$cliArgs += "--append-system-prompt", "N{nuc_id[1:]}_{domain}/P08_architecture/agent_card_{nuc_id}.md"
$cliArgs += "--append-system-prompt", $sysPrompt
if ($resolved.settings) {{ $cliArgs += "--settings", "$cexRoot\\$($resolved.settings)" }}
$cliArgs += $initialMsg

Set-CexTitle "RUNNING"
& claude @cliArgs
Set-CexTitle "DONE"

exit 0
"""


def render_boot_alt(nuc_id: str, domain: str, sin_key: str, runtime: str) -> str:
    """Assets 8: boot/n{xx}_{runtime}.ps1 (codex/gemini/ollama stub)"""
    s = SIN_LENS[sin_key]
    nuc_upper = nuc_id.upper()
    runtime_upper = runtime.upper()
    return f"""# CEX {nuc_upper} -- {runtime_upper} runtime
# Auto-generated by cex_new_nucleus.py
# Sin: {s['label']} ({sin_key}) | Domain: {domain}

. $PSScriptRoot/_shared/vt_enable.ps1
. $PSScriptRoot/_shared/fix_pathext.ps1
$cexRoot = Split-Path -Parent $PSScriptRoot
$nucleus = "{nuc_id}"

$env:CEX_NUCLEUS = "{nuc_upper}"
$env:CEX_ROOT = $cexRoot
$env:CEX_CLI = "{runtime}"
Set-Location $env:CEX_ROOT

. "$PSScriptRoot\\_shared\\load_dotenv.ps1"

# Detect handoff (per-runtime suffix or main)
$handoff = "$cexRoot\\.cex\\runtime\\handoffs\\${{nucleus}}_task_{runtime}.md"
if (-not (Test-Path $handoff)) {{
    $handoff = "$cexRoot\\.cex\\runtime\\handoffs\\${{nucleus}}_task.md"
}}

$handoffBody = "(no handoff -- report ready and exit)"
if (Test-Path $handoff) {{
    $handoffBody = Get-Content -Raw -LiteralPath $handoff
}}

$sysPrompt = @'
You are driven by {s['label']}. {s['bias']}.
You are {nuc_upper} of CEX (running via {runtime_upper} CLI).
Domain: {domain}.
Rules: .claude/rules/n07-orchestrator.md + N{nuc_id[1:]}_{domain}/rules/{nuc_id}-{domain}.md
+ .claude/rules/8f-reasoning.md + .claude/rules/ascii-code-rule.md
Agent card: N{nuc_id[1:]}_{domain}/P08_architecture/agent_card_{nuc_id}.md
Follow 8F pipeline F1->F8. Save output, compile, commit, signal on complete.
'@

$initialMsg = @"
Execute the task in the embedded handoff below.

=== HANDOFF BEGIN ===
$handoffBody
=== HANDOFF END ===

SYSTEM CONTEXT:
$sysPrompt
"@

# Launch the chosen runtime CLI; user must have it installed.
# This is a stub -- customize flags / model per your runtime config.
switch ("{runtime}") {{
    "codex"  {{
        $cliArgs = @("--dangerously-bypass-approvals-and-sandbox", "-c", "model_reasoning_effort=high", "-C", $cexRoot)
        $initialMsg | & codex exec @cliArgs -
    }}
    "gemini" {{
        $cliArgs = @("--yolo", "--model", "gemini-2.5-flash-lite", "--include-directories", $cexRoot)
        & gemini @cliArgs $initialMsg
    }}
    "ollama" {{
        $model = if ($env:OLLAMA_MODEL) {{ $env:OLLAMA_MODEL }} else {{ "qwen3:8b" }}
        & python "$cexRoot\\_tools\\ollama_nucleus.py" --nucleus {nuc_upper} --model $model --task-file $handoff
    }}
}}

exit 0
"""


def render_permissions(nuc_id: str, domain: str) -> str:
    """Asset 9: .claude/nucleus-settings/n{xx}.json (scoped permissions)"""
    template_path = REPO / ".claude" / "nucleus-settings" / "_template.json"
    if template_path.is_file():
        # Customize template by replacing N{XX}_* with the actual nucleus dir
        text = template_path.read_text(encoding="utf-8")
        return text.replace("N{XX}_*", f"N{nuc_id[1:]}_*")
    # Fallback minimal template (if _template.json is missing)
    return json.dumps({
        "$schema": "https://json.schemastore.org/claude-settings",
        "comment": f"Scoped permissions for {nuc_id} ({domain}). Generated by cex_new_nucleus.",
        "permissions": {
            "allow": [
                "Read(**)",
                "Grep(**)",
                "Glob(**)",
                f"Write(N{nuc_id[1:]}_*/**)",
                f"Edit(N{nuc_id[1:]}_*/**)",
                "Bash(python _tools/cex_*:*)",
                "Bash(python -c:*)",
                "Bash(git status:*)",
                "Bash(git log:*)",
                "Bash(git diff:*)",
                "Bash(git add:*)",
                "Bash(git commit:*)",
                "Bash(ls:*)",
                "Bash(bash _spawn/dispatch.sh status:*)",
            ],
            "deny": [
                "Bash(rm -rf:*)",
                "Bash(git push --force:*)",
                "Bash(git reset --hard:*)",
                "Write(CLAUDE.md)",
                "Write(.cex/kinds_meta.json)",
                "Write(.claude/settings.json)",
            ],
        },
        "hooks": {
            "Stop": [{"hooks": [{"type": "command", "command": "python _tools/cex_hooks_native.py stop", "timeout": 10}]}],
        },
    }, indent=2) + "\n"


def render_yaml_block(nuc_id: str, domain: str, sin_key: str) -> str:
    """nucleus_models.yaml entry (appended, not overwritten)"""
    s = SIN_LENS[sin_key]
    return f"""

# --- {nuc_id.upper()}: {domain.title()} Vertical (community-added, sin: {s['label']}) ---
{nuc_id}:
  cli: claude
  model: sonnet
  flags: "--dangerously-skip-permissions --permission-mode bypassPermissions --no-chrome"
  context: 200000
  domain: {domain}
  tier: full_8f
  default_mode: A
  mcps: ""
  settings: ".claude/nucleus-settings/{nuc_id}.json"
  fallback_chain:
    - {{cli: gemini, model: gemini-2.5-flash-lite, flags: "--yolo", tier: f6_generation}}
    - {{cli: codex,  model: gpt-5,             flags: "--dangerously-bypass-approvals-and-sandbox", tier: preflight_aux}}
    - {{cli: ollama, model: qwen3:8b,         flags: "", tier: unsupported}}
  fallback:
    cli: gemini
    model: gemini-2.5-flash-lite
    flags: "--yolo"
  fallback_local:
    cli: ollama
    model: qwen3:8b
  notes: "Auto-scaffolded by cex_new_nucleus.py. Adjust model/fallback per workload."
"""


# ---------------------------------------------------------------------------
# Plan + Apply
# ---------------------------------------------------------------------------

def build_plan(nuc_id: str, domain: str, sin_key: str) -> list[dict]:
    """Build the action plan for scaffolding a new nucleus."""
    target = REPO / f"N{nuc_id[1:]}_{domain}"
    plan: list[dict] = []

    # 1. Pillar dirs + rules + compiled + crews
    for code, label in PILLARS:
        plan.append({"action": "mkdir", "path": str(target / f"{code}_{label}")})
    plan.append({"action": "mkdir", "path": str(target / "rules")})
    plan.append({"action": "mkdir", "path": str(target / "compiled")})
    plan.append({"action": "mkdir", "path": str(target / "P12_orchestration" / "crews")})

    # 2. Asset 1: rule file
    plan.append({"action": "write",
                 "path": str(target / "rules" / f"{nuc_id}-{domain}.md"),
                 "content": render_rule_file(nuc_id, domain, sin_key)})

    # 3. Asset 2: nucleus_def
    plan.append({"action": "write",
                 "path": str(target / "P02_model" / f"nucleus_def_{nuc_id}.md"),
                 "content": render_nucleus_def(nuc_id, domain, sin_key)})

    # 4. Asset 3: agent_card (canonical P08 path per CEXAI naming)
    plan.append({"action": "write",
                 "path": str(target / "P08_architecture" / f"agent_card_{nuc_id}.md"),
                 "content": render_agent_card(nuc_id, domain, sin_key)})

    # 5. Asset 4: vocabulary KC
    plan.append({"action": "write",
                 "path": str(target / "P01_knowledge" / f"kc_{domain}_vocabulary.md"),
                 "content": render_vocabulary_kc(nuc_id, domain, sin_key)})

    # 6. Asset 5: component_map
    plan.append({"action": "write",
                 "path": str(target / "P08_architecture" / f"component_map_{nuc_id}.md"),
                 "content": render_component_map(nuc_id, domain, sin_key)})

    # 7. Asset 6: Claude Code sub-agent
    plan.append({"action": "write",
                 "path": str(REPO / ".claude" / "agents" / f"{nuc_id}-{domain}.md"),
                 "content": render_subagent(nuc_id, domain, sin_key)})

    # 8. Asset 7: boot/n{xx}.ps1
    plan.append({"action": "write",
                 "path": str(REPO / "boot" / f"{nuc_id}.ps1"),
                 "content": render_boot_ps1(nuc_id, domain, sin_key)})

    # 9. Asset 8: boot/n{xx}_{codex,gemini,ollama}.ps1
    for runtime in ("codex", "gemini", "ollama"):
        plan.append({"action": "write",
                     "path": str(REPO / "boot" / f"{nuc_id}_{runtime}.ps1"),
                     "content": render_boot_alt(nuc_id, domain, sin_key, runtime)})

    # 10. Asset 9: scoped permissions
    plan.append({"action": "write",
                 "path": str(REPO / ".claude" / "nucleus-settings" / f"{nuc_id}.json"),
                 "content": render_permissions(nuc_id, domain)})

    # 11. nucleus_models.yaml append
    plan.append({"action": "append",
                 "path": str(REPO / ".cex" / "config" / "nucleus_models.yaml"),
                 "content": render_yaml_block(nuc_id, domain, sin_key)})

    return plan


def apply_plan(plan: list[dict]) -> dict:
    """Execute the plan. Returns counts."""
    written: list[str] = []
    appended: list[str] = []
    mkdirs: list[str] = []
    for step in plan:
        path = Path(step["path"])
        if step["action"] == "mkdir":
            path.mkdir(parents=True, exist_ok=True)
            mkdirs.append(str(path))
        elif step["action"] == "write":
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(step["content"], encoding="utf-8")
            written.append(str(path))
        elif step["action"] == "append":
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as f:
                f.write(step["content"])
            appended.append(str(path))
    return {"mkdirs": len(mkdirs), "written": len(written), "appended": len(appended)}


def run_doctor() -> tuple[int, str]:
    """Run cex_doctor.py and return (exit_code, last_summary_line)."""
    doctor = REPO / "_tools" / "cex_doctor.py"
    if not doctor.is_file():
        return (-1, "cex_doctor.py not found")
    try:
        result = subprocess.run(
            [sys.executable, str(doctor)],
            cwd=str(REPO), capture_output=True, text=True, timeout=120,
        )
        # Last meaningful line (summary)
        out = (result.stdout + result.stderr).strip().splitlines()
        last = out[-1] if out else "(no output)"
        return (result.returncode, last)
    except subprocess.TimeoutExpired:
        return (-2, "doctor timed out")
    except Exception as e:  # noqa: BLE001
        return (-3, f"doctor failed: {e}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def render_text_summary(nuc_id: str, domain: str, sin_key: str,
                        plan: list[dict], applied: bool, counts: dict | None,
                        doctor_result: tuple[int, str] | None) -> str:
    s = SIN_LENS[sin_key]
    lines: list[str] = []
    title = "Applied" if applied else "Dry Run -- Preview"
    lines.append(f"=== cex_new_nucleus: {title} ===")
    lines.append(f"Nucleus: {nuc_id.upper()} ({nuc_id})")
    lines.append(f"Domain:  {domain}")
    lines.append(f"Sin:     {s['label']} ({sin_key}) -- {s['bias']}")
    lines.append("")

    # Action breakdown
    by_action: dict[str, int] = {}
    for step in plan:
        by_action[step["action"]] = by_action.get(step["action"], 0) + 1
    lines.append(f"Plan: {len(plan)} actions ({by_action})")
    lines.append("")

    # File list (grouped)
    lines.append("Files to create:")
    for step in plan:
        if step["action"] in ("write", "append"):
            try:
                rel = Path(step["path"]).relative_to(REPO)
            except ValueError:
                rel = Path(step["path"])
            tag = "[append]" if step["action"] == "append" else "[write]"
            lines.append(f"  {tag} {rel}")
    lines.append("")
    lines.append("Directories to create:")
    for step in plan:
        if step["action"] == "mkdir":
            try:
                rel = Path(step["path"]).relative_to(REPO)
            except ValueError:
                rel = Path(step["path"])
            lines.append(f"  [mkdir] {rel}")
    lines.append("")

    if applied and counts:
        lines.append(f"Created: {counts['mkdirs']} dirs, {counts['written']} files, "
                     f"{counts['appended']} appended")
        lines.append("")
        if doctor_result:
            code, last = doctor_result
            label = "[OK]" if code == 0 else "[WARN]" if code > 0 else "[SKIP]"
            lines.append(f"cex_doctor.py: {label} {last}")
        lines.append("")
        lines.append("Next steps:")
        lines.append(f"  1. Edit N{nuc_id[1:]}_{domain}/rules/{nuc_id}-{domain}.md (customize identity)")
        lines.append(f"  2. Replace TODOs in N{nuc_id[1:]}_{domain}/P01_knowledge/kc_{domain}_vocabulary.md")
        lines.append("  3. python _tools/cex_doctor.py")
        lines.append(f"  4. git add N{nuc_id[1:]}_{domain}/ boot/{nuc_id}*.ps1 .claude/agents/{nuc_id}-{domain}.md .claude/nucleus-settings/{nuc_id}.json .cex/config/nucleus_models.yaml")
        lines.append(f"  5. git commit -m \"[{nuc_id}] scaffold {domain} nucleus ({s['label']})\"")
    else:
        lines.append("Run again WITHOUT --dry-run to apply.")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold a new community vertical nucleus (N08+).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python _tools/cex_new_nucleus.py 08 healthcare gluttony
  python _tools/cex_new_nucleus.py 09 fintech greed --dry-run
  python _tools/cex_new_nucleus.py 10 edtech pride --json
""",
    )
    parser.add_argument("nucleus_num", help="2-digit nucleus number (08-99, > 07)")
    parser.add_argument("domain", help="Lowercase snake_case domain slug (healthcare, fintech, ...)")
    parser.add_argument("sin", help="Sin lens (envy/lust/pride/gluttony/wrath/greed/sloth, case-insensitive)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview the plan without writing any files")
    parser.add_argument("--json", action="store_true",
                        help="Emit JSON output (for scripting)")
    parser.add_argument("--no-doctor", action="store_true",
                        help="Skip cex_doctor.py validation after applying")

    args = parser.parse_args(argv)

    # Validate args
    nuc_id, domain, sin_key, errors = validate_args(args.nucleus_num, args.domain, args.sin)
    if errors:
        if args.json:
            print(json.dumps({"status": "error", "errors": errors}))
        else:
            for e in errors:
                print(f"ERROR: {e}", file=sys.stderr)
        return 1

    # Check collisions
    collisions = check_collision(nuc_id, domain)
    if collisions:
        if args.json:
            print(json.dumps({"status": "error", "errors": collisions}))
        else:
            for c in collisions:
                print(f"ERROR: {c}", file=sys.stderr)
        return 1

    # Build plan
    try:
        plan = build_plan(nuc_id, domain, sin_key)
    except Exception as e:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "error", "errors": [f"plan failed: {e}"]}))
        else:
            print(f"ERROR: plan failed: {e}", file=sys.stderr)
        return 2

    if args.dry_run:
        if args.json:
            payload = {
                "status": "dry_run",
                "nucleus": nuc_id,
                "domain": domain,
                "sin": sin_key,
                "sin_label": SIN_LENS[sin_key]["label"],
                "actions": len(plan),
                "files": [str(Path(p["path"]).relative_to(REPO))
                          for p in plan if p["action"] in ("write", "append")],
                "dirs": [str(Path(p["path"]).relative_to(REPO))
                         for p in plan if p["action"] == "mkdir"],
            }
            print(json.dumps(payload, indent=2))
        else:
            print(render_text_summary(nuc_id, domain, sin_key, plan, applied=False,
                                       counts=None, doctor_result=None))
        return 0

    # Apply
    try:
        counts = apply_plan(plan)
    except Exception as e:  # noqa: BLE001
        if args.json:
            print(json.dumps({"status": "error", "errors": [f"apply failed: {e}"]}))
        else:
            print(f"ERROR: apply failed: {e}", file=sys.stderr)
        return 2

    # Run doctor (unless skipped)
    doctor_result: tuple[int, str] | None = None
    if not args.no_doctor:
        doctor_result = run_doctor()

    if args.json:
        payload = {
            "status": "applied",
            "nucleus": nuc_id,
            "domain": domain,
            "sin": sin_key,
            "sin_label": SIN_LENS[sin_key]["label"],
            "counts": counts,
            "doctor": {
                "exit_code": doctor_result[0] if doctor_result else None,
                "summary": doctor_result[1] if doctor_result else None,
            },
        }
        print(json.dumps(payload, indent=2))
    else:
        print(render_text_summary(nuc_id, domain, sin_key, plan, applied=True,
                                   counts=counts, doctor_result=doctor_result))

    return 0


if __name__ == "__main__":
    try:
        from cex_agent_io import wrap_main
        def _wrapper(argv):
            sys.argv = [sys.argv[0]] + argv
            return main()
        sys.exit(wrap_main(_wrapper, sys.argv[1:], label="cex_new_nucleus"))
    except ImportError:
        sys.exit(main())
