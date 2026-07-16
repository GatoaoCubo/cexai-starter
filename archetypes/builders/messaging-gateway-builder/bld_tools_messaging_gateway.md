---
kind: tools
id: bld_tools_messaging_gateway
pillar: P04
llm_function: CALL
purpose: P04 tools available to the messaging_gateway builder at F5 CALL
pattern: Tools used to research, validate, and produce messaging_gateway artifacts
quality: null
title: "Tools: messaging_gateway"
version: "1.0.0"
author: n03_builder
tags: [messaging_gateway, builder, tools, p04, hermes_origin]
tldr: "Builder tools: cex_query (find similar gateways), cex_doctor (validate), cex_compile (yaml), kinds_meta check. No live platform tools (DP5 stub)."
domain: "messaging gateway construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F5_call"
keywords: [messaging gateway construction, builder tools, find similar gateways, kinds_meta check, no live platform tools, messaging_gateway, builder, tools, hermes_origin, cex_query.py]
density_score: 0.89
related:
  - bld_tools_terminal_backend
  - p11_tools_revision_loop_policy
  - bld_tools_personality
  - bld_collaboration_messaging_gateway
  - messaging-gateway-builder
---
# Tools: messaging_gateway Builder

## F5 CALL Tool Inventory
| Tool | Purpose | When to Use |
|------|---------|-------------|
| `cex_query.py` | TF-IDF discovery of existing messaging_gateway artifacts | Before building -- check for duplicates |
| `cex_doctor.py` | Builder health check | After producing -- validate schema compliance |
| `cex_compile.py {path}` | Compile .md -> .yaml | After writing artifact |
| `cex_retriever.py` | Semantic similarity search for related artifacts | Find similar webhook/api_client neighbors |
| `python -m json.tool .cex/kinds_meta.json` | Validate JSON after adding kind entry | After patching kinds_meta.json |
| `cex_score.py --apply {file}` | Apply quality score | After F7 GOVERN check |

## Discovery Commands
```bash
# Check for existing gateway artifacts
python _tools/cex_query.py "messaging gateway telegram"

# Find similar P04 tools for reference
python _tools/cex_retriever.py "multi-platform bot webhook api"

# Verify kinds_meta.json has messaging_gateway entry
python -c "import json; d=json.load(open('.cex/kinds_meta.json')); print('messaging_gateway' in d)"

# Check builder health after producing ISOs
python _tools/cex_doctor.py
```

## Compilation Commands
```bash
# Compile single artifact
python _tools/cex_compile.py N00_genesis/P04_tools/tpl_messaging_gateway.md

# Compile all after bulk build
python _tools/cex_compile.py --all
```

## CLI Reference (NOT CEX tools -- external)
These are the activation commands AFTER stub is specified:
```bash
messaging gateway setup    # configure platform credentials
messaging gateway start    # run gateway process
```
These run OUTSIDE CEX. They are not invoked by the builder.

## Tools NOT Used (boundary enforcement)
| Tool | Why not used |
|------|-------------|
| Telegram Bot API | DP5 stub -- no live platform calls |
| Discord.py / discord.js | DP5 stub -- no live platform calls |
| slack_sdk | DP5 stub -- no live platform calls |
| Any platform SDK | DP5 stub -- spec only, no implementation |

## F8 COLLABORATE Tools
```bash
# After all ISOs produced
python _tools/cex_compile.py --all
python _tools/cex_doctor.py
git add archetypes/builders/messaging-gateway-builder/ N00_genesis/ .claude/agents/ .cex/kinds_meta.json
git commit -m "[N03] messaging_gateway archetype"
python -c "from _tools.signal_writer import write_signal; write_signal('n03', 'complete', 9.0, mission='builder_example')"
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_terminal_backend]] | sibling | 0.48 |
| [[p11_tools_revision_loop_policy]] | related | 0.40 |
| [[bld_tools_personality]] | related | 0.38 |
| [[bld_collaboration_messaging_gateway]] | downstream | 0.36 |
| [[messaging-gateway-builder]] | related | 0.34 |
