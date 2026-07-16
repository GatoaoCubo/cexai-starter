---
quality: null
quality: null
kind: tools
id: bld_tools_terminal_backend
pillar: P04
llm_function: CALL
purpose: Tools used by terminal_backend builder during 8F pipeline
title: "Tools Terminal Backend"
version: "1.0.0"
author: n03_engineering
tags: [terminal_backend, builder, tools]
tldr: "Builder tools: cex_compile, cex_doctor, kinds_meta lookup, secret_config reference checker"
domain: "terminal_backend construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F5_call"
keywords: [f pipeline, terminal_backend construction, tools terminal backend, builder tools, kinds_meta lookup, secret_config reference checker, terminal_backend, builder, tools, "python _tools/cex_compile.py {path}"]
density_score: 0.88
related:
  - p11_tools_revision_loop_policy
  - bld_tools_personality
  - bld_tools_messaging_gateway
  - bld_tools_value_object
  - bld_tools_domain_vocabulary
---
## Tools Used in Pipeline
| Tool | Phase | Purpose |
|------|-------|---------|
| `python _tools/cex_compile.py {path}` | F8 | Compile .md -> .yaml |
| `python _tools/cex_doctor.py` | F8 | Health check after build |
| `python -m json.tool .cex/kinds_meta.json` | F7 | Validate kinds_meta JSON after patch |
| `python _tools/cex_retriever.py terminal_backend` | F3 | Find similar artifacts for context |
| `grep -r "terminal_backend" archetypes/` | F3 | Check for prior examples |

## F5 Tool Checklist
```bash
# Verify kinds_meta has terminal_backend entry
python -c "import json; d=json.load(open('.cex/kinds_meta.json')); print('terminal_backend' in d)"

# Compile the new artifact
python _tools/cex_compile.py N00_genesis/P09_config/kind_terminal_backend/

# Doctor check
python _tools/cex_doctor.py --quick

# Validate schema patch
python -m json.tool .cex/kinds_meta.json > /dev/null
echo "JSON valid"
```

## Secret Config Integration
When `auth.method != none`, the builder should verify the referenced secret_config exists:

```bash
grep -r "id: {{secret_ref}}" N00_genesis/P09_config/ .cex/
```

If not found, N03 creates a stub secret_config artifact or documents the requirement.

## Signal Tool
```python
from _tools.signal_writer import write_signal
write_signal('n03', 'complete', 9.0, mission='builder_example')
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p11_tools_revision_loop_policy]] | related | 0.46 |
| [[bld_tools_personality]] | related | 0.40 |
| [[bld_tools_messaging_gateway]] | sibling | 0.39 |
| [[bld_tools_value_object]] | downstream | 0.32 |
| [[bld_tools_domain_vocabulary]] | upstream | 0.32 |
