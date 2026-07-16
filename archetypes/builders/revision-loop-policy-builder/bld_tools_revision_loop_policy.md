---
id: p11_tools_revision_loop_policy
kind: toolkit
pillar: P04
llm_function: CALL
purpose: P04 tools available to the revision-loop-policy-builder
quality: null
title: "Tools: Revision Loop Policy Builder"
version: "1.0.0"
author: n03_builder
tags: [tools, revision_loop_policy, builder, p04, p11]
domain: "revision_loop_policy construction"
created: "2026-04-18"
updated: "2026-04-18"
tldr: "P04 tools available to the revision-loop-policy-builder"
8f: "F5_call"
keywords: [revision_loop_policy construction, revision loop policy builder, tools, revision_loop_policy, builder, "python _tools/cex_compile.py {path}", python _tools/cex_doctor.py, python _tools/cex_sanitize.py --check, "python _tools/cex_score.py --apply {path}", python -m json.tool.cex/kinds_meta.json]
density_score: 0.86
related:
 - bld_tools_terminal_backend
 - bld_tools_personality
 - bld_tools_kind
 - bld_tools_domain_vocabulary
 - bld_tools_event_schema
---
## Available Tools (F5 CALL)

### Core Build Tools

| Tool | Command | Purpose |
|------|---------|---------|
| Compile | `python _tools/cex_compile.py {path}` | Convert.md ->.yaml |
| Doctor | `python _tools/cex_doctor.py` | Health check all artifacts |
| Sanitize | `python _tools/cex_sanitize.py --check` | Verify ASCII compliance |
| Score | `python _tools/cex_score.py --apply {path}` | Peer-review scoring |

### Validation Tools

| Tool | Command | Purpose |
|------|---------|---------|
| JSON validate | `python -m json.tool.cex/kinds_meta.json` | Verify kinds_meta is valid JSON |
| YAML validate | `python -c "import yaml; yaml.safe_load(open('{path}'))"` | Verify frontmatter parses |

### Discovery Tools

| Tool | Command | Purpose |
|------|---------|---------|
| Query | `python _tools/cex_query.py revision_loop_policy` | Find similar artifacts |
| Retriever | `python _tools/cex_retriever.py "revision loop"` | TF-IDF similarity search |
| Kind meta | `python -c "import json; d=json.load(open('.cex/kinds_meta.json')); print(d.get('revision_loop_policy'))"` | Check kind registration |

### Reference Files (read before building)

| File | Purpose |
|------|---------|
| `archetypes/builders/revision-loop-policy-builder/bld_schema_revision_loop_policy.md` | HARD gates + schema |
| `N00_genesis/P11_feedback/tpl_revision_loop_policy.md` | Canonical template |
| `N00_genesis/P01_knowledge/library/kind/kc_revision_loop_policy.md` | Domain KC |
| `archetypes/builders/revision-loop-policy-builder/bld_examples_revision_loop_policy.md` | 3 golden + 3 anti-examples |

### File Operations

| Operation | Tool |
|-----------|------|
| Read files | Read (not cat) |
| Write new artifact | Write |
| Edit existing | Edit |
| Find similar | Glob + Grep |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_terminal_backend]] | related | 0.47 |
| [[bld_tools_personality]] | related | 0.38 |
| [[bld_tools_kind]] | related | 0.38 |
| [[bld_tools_domain_vocabulary]] | upstream | 0.36 |
| [[bld_tools_event_schema]] | related | 0.36 |
