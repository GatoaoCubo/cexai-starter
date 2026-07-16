---
kind: tools
id: bld_tools_agent_grounding_record
pillar: P04
llm_function: CALL
purpose: Tool inventory for grounding record production -- hash verification, OTel validation, compile pipeline, external references
quality: 9.2
title: "Agent Grounding Record Builder -- Tools"
version: "1.0.0"
author: wave7_n05
tags: [agent_grounding_record, builder, tools]
tldr: "Production: cex_compile + cex_score + cex_retriever. Validation: hash-verify + span-validator. External: OTel semconv + C2PA v2.3 spec."
domain: "agent_grounding_record construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [otel validation, compile pipeline, external references, agent_grounding_record construction, otel semconv, agent_grounding_record, builder]
density_score: 0.85
related:
  - bld_config_agent_grounding_record
  - bld_architecture_agent_grounding_record
---
# Agent Grounding Record Builder -- Tools

## Production Tools (CEX Core)

| Tool                   | Command                                                                 | 8F Stage | Purpose                                                  |
|------------------------|-------------------------------------------------------------------------|----------|----------------------------------------------------------|
| cex_compile.py         | `python _tools/cex_compile.py P10_memory/grounding/p10_gr_`{{prefix}}`.md` | F8     | Compile .md to .yaml, check frontmatter, validate size   |
| cex_score.py           | `python _tools/cex_score.py --apply P10_memory/grounding/p10_gr_`{{prefix}}`.md` | F7 | Run 3-layer scoring (structural + rubric + semantic) |
| cex_retriever.py       | `python _tools/cex_retriever.py --query "grounding provenance OTel"` | F3      | Find similar grounding records for context injection     |
| cex_doctor.py          | `python _tools/cex_doctor.py --pillar P10`                             | F8       | Health check on all P10 memory artifacts                 |
| cex_compile.py --all   | `python _tools/cex_compile.py --all`                                   | F8       | Recompile entire artifact library after batch production |

### cex_compile.py -- Grounding Record Specific Checks

When run against an agent_grounding_record artifact, cex_compile.py performs:
1. YAML frontmatter parse check
2. ID naming regex validation: ^p10_gr_[a-z0-9_]+\.md$
3. kind field = "agent_grounding_record" check
4. Byte size <= 4096 check
5. output_hash format check (64 hex chars)
6. otel_span_id format check (16 hex chars)

## Validation Tools

### Hash Verification Tool

Verifies that output_hash, content_hash, and tool I/O hashes are valid SHA-256 hex strings.

```bash
# Verify all hashes in a grounding record
python _tools/cex_compile.py P10_memory/grounding/p10_gr_{{prefix}}.md --verify-hash
# Compute output_hash from raw output file
python -c "
import hashlib
with open('raw_output.txt', 'rb') as f:
    raw = f.read()
print(hashlib.sha256(raw).hexdigest())
```

Hash validation rules enforced:
- Length: exactly 64 characters
- Charset: lowercase hexadecimal [0-9a-f] only
- Algorithm: SHA-256 only (no MD5, no SHA-1, no SHA-512)
- Source: raw bytes before any post-processing

### OTel Span ID Validator

Validates that otel_span_id conforms to W3C Trace Context format.

```bash
# Validate span ID format (W3C: 16 lowercase hex chars)
python -c "
import re, sys
span_id = sys.argv[1]
pattern = re.compile(r'^[0-9a-f]{16}$')
if pattern.match(span_id):
    print('[OK] Valid W3C span ID: ' + span_id)
else:
```

Common span ID format errors:

| Error Pattern           | Example              | Fix                                      |
|-------------------------|----------------------|------------------------------------------|
| 32 chars (trace ID)     | 4bf92f3577b34da6...  | Use the span ID (16 chars), not trace ID |
| Uppercase letters       | 4BF92F3577B34DA6     | Convert to lowercase                     |
| Hyphens (UUID format)   | 4bf9-2f35-77b3-4da6  | Remove hyphens                           |
| Shorter than 16 chars   | 4bf92f35            | Retrieve correct span ID from OTel SDK   |

### UUID Validator (inference_id)

```bash
# Validate UUIDv4 format
python -c "
import re, sys
uuid = sys.argv[1]
pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')
if pattern.match(uuid):
    print('[OK] Valid UUIDv4: ' + uuid)
else:
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_agent_grounding_record]] | downstream | 0.47 |
| [[bld_architecture_agent_grounding_record]] | downstream | 0.33 |
