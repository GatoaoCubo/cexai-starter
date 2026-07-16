---
kind: tools
id: bld_tools_cybersec_skill
pillar: P04
llm_function: CALL
purpose: Tools available to cybersec-skill-builder during construction
pattern: what external tools this builder can invoke (Standard CEX + cybersec-specific verification)
quality: null
title: "Tools Cybersec Skill"
version: "1.0.0"
author: n03_builder
tags: [cybersec_skill, builder, tools, anti-fabrication, grep, ATT&CK]
tldr: "Tool inventory for cybersec-skill-builder: CEX standard (compile/doctor/score/index/signal) + cybersec-specific (grep-based AF gates + capability_registry lookup)."
domain: "cybersec_skill construction"
created: "2026-05-30"
updated: "2026-05-30"
8f: "F5_call"
keywords: [cybersec_skill, tools, cex_doctor, cex_compile, cex_score, signal_writer, grep, anti-fabrication, capability_registry lookup]
density_score: 0.90
related:
  - bld_tools_skill
  - bld_tools_safety_policy
  - bld_tools_ai_rmf_profile
  - cybersec-skill-builder
  - bld_eval_cybersec_skill
---

# Tools: cybersec-skill-builder

## Available Tools

| Tool | Purpose | When |
|------|---------|------|
| `cex_query.py` | Find existing cybersec_skills + similar baselines | F3 INJECT |
| `cex_compile.py` | Validate frontmatter + compile to YAML | F8 COLLABORATE |
| `cex_doctor.py` | Check builder spec completeness (12 ISOs + KC + kinds_meta) | F7 GOVERN |
| `cex_score.py` | Multi-layer scoring (structural + rubric + semantic) | F7 GOVERN |
| `cex_index.py` | Update search index | F8 COLLABORATE |
| `cex_sanitize.py` | ASCII enforcement on code blocks | F7 GOVERN |
| `signal_writer.py` | Signal completion | F8 COLLABORATE |
| `grep` (POSIX) | Anti-fabrication source-trace verification (H_AF1-H_AF3) | F7 GOVERN |
| `test -e` | source: path existence check (H_AF4) | F7 GOVERN |

## Cybersec-specific Tool Sequences

### Anti-Fabrication Verification (F7 GOVERN)

```bash
# H_AF1: T-codes
grep -oE 'T[0-9]+(\.[0-9]+)?' p03_cysk_<name>.md | sort -u > /tmp/cited_tcodes.txt
while read code; do
  grep -F "$code" "$SOURCE/references/standards.md" > /dev/null || echo "H_AF1 FAIL: $code"
done < /tmp/cited_tcodes.txt

# H_AF2: CVEs
grep -oE 'CVE-[0-9]{4}-[0-9]+' p03_cysk_<name>.md | sort -u > /tmp/cited_cves.txt

# H_AF3: framework controls
grep -oE '[A-Z]{2}\.[A-Z][A-Z]?-?[0-9]+|AML\.T[0-9]+' p03_cysk_<name>.md | sort -u

# H_AF4: source path exists
test -e "$SOURCE" || echo "H_AF4 FAIL: source missing"
```

### Capability Registry Lookup (F1 CONSTRAIN, if authorized_use_only=true)

```bash
# Find capability_registry artifact granting this skill
grep -r "registers: $SKILL_ID" archetypes/capability_registry/ N05_operations/P11_feedback/
```

## Tool Usage Pattern

```
F1 CONSTRAIN  -> cex_query.py --kind cybersec_skill          # discover existing
F3 INJECT     -> cat $SOURCE/SKILL.md + standards.md          # learn citation pool
F5 CALL       -> List tools above                              # ready
F6 PRODUCE    -> Write artifact (frontmatter + 8 sections)
F7 GOVERN     -> cex_doctor.py + cex_score.py + AF grep block + cex_sanitize.py
F8 COLLABORATE-> cex_compile.py + cex_index.py + git commit + signal_writer.py
```

## Tool Permissions

| Category | Tools | Status |
|----------|-------|--------|
| ALLOWED | Read, Write, Edit, Bash (read-only on source/), Glob, Grep | Explicitly permitted |
| ALLOWED-LIMITED | Bash with `--read-only` flag on source/ | No mutations to baseline (preserves Apache 2.0 trace) |
| DENIED | network egress | No live-call leakage of capability artifacts |
| EFFECTIVE | Bash, Edit, Glob, Grep, Read, Write | Per N05 nucleus permissions |

## Cybersec Tool Boundaries

| Tool | Used For | NEVER Used For |
|------|----------|----------------|
| grep | source-trace verification | actually fetching baseline (read whole file via Read) |
| Bash | local read + write + AF grep | live exploit execution (delegate to sandbox_spec + mcp_server) |
| cex_doctor.py | structural + 12-ISO completeness | scoring (delegate to cex_score.py) |
| cex_score.py | quality scoring (3 layers) | self-attestation (quality: null always) |

## Pipeline Integration

1. Created via 8F pipeline (F1-F8) + AF lattice (4 anti-fabrication gates)
2. Scored by cex_score across structural + rubric + semantic layers
3. Compiled by cex_compile for structural validation
4. Retrieved by cex_retriever for context injection in future cybersec_skill builds
5. Evolved by cex_evolve when quality regresses below 9.0

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_skill]] | parent | 0.65 |
| [[bld_tools_safety_policy]] | sibling | 0.50 |
| [[bld_tools_ai_rmf_profile]] | sibling | 0.50 |
| [[cybersec-skill-builder]] | upstream | 0.62 |
| [[bld_eval_cybersec_skill]] | downstream | 0.55 |
