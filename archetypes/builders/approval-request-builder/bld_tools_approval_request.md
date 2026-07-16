---
kind: tools
id: bld_tools_approval_request
pillar: P04
llm_function: CALL
purpose: Tools and APIs available for approval_request production
quality: null
title: "Tools Approval Request"
version: "1.0.0"
author: n03_builder
tags: [approval_request, builder, tools, P11]
tldr: "Tools for approval_request production: read the real watch file for audit transcription, validate YAML, compile artifact, check size."
domain: "approval_request construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F5_call"
keywords: [approval_request construction, tools approval request, tools for approval_request production, read watch file, validate yaml, compile artifact, check size, approval_request, builder, tools]
density_score: 0.88
related:
  - bld_tools_hitl_config
  - bld_architecture_approval_request
  - bld_config_approval_request
  - bld_schema_approval_request
  - adr_v03_governance_taxonomy
---

# Tools: approval-request-builder
## Production Tools
| Tool | Purpose | When | Status |
|------|---------|------|--------|
| brain_query [MCP] | Search existing approval_request artifacts in pool | Phase 1 (check duplicates) | CONDITIONAL |
| cex_compile.py | Compile .md to .yaml frontmatter | Phase 3 (F8) | AVAILABLE |
| cex_score.py --apply | Run quality gate scoring | Phase 3 (F7) | AVAILABLE |
| cex_retriever.py | Find similar approval_request artifacts for reference | Phase 1 | AVAILABLE |
| validate_artifact.py | Generic artifact validator | Phase 3 | [PLANNED] |
## Real Runtime Touchpoints (READ-ONLY reference for audit transcription -- never write here)
| Touchpoint | Path | Use |
|------------|------|-----|
| Live watch file | `.cexai/approvals/{request_id}.json` (gitignored) | Read to transcribe a real request's exact fields when authoring an AUDIT record |
| `FileApprovalGate` | `cexai/cexai/governance/hitl/file_gate.py` | Ground-truth shape of `request`/`policy`/`verdicts` -- read, never invoke from a builder pass |
| `record_verdict()` | `cexai/cexai/governance/hitl/approver.py` | Ground-truth shape of one verdict entry (`approver`, `verdict`, optional `token`) |
| `ApprovalRequest` dataclass | `cexai/cexai/governance/_shared/types.py:154-167` | The 5 frozen fields this artifact's Request Detail table must mirror |
| Governance test suite | `cexai/tests/governance/hitl/test_file_approval_gate.py` | Re-runnable ground truth for lifecycle/M-of-N behavior (31 passed, re-run 2026-07-03) |
## Data Sources
| Source | Path | Data |
|--------|------|------|
| CEX Schema | P11_feedback/_schema.yaml | Field definitions, approval_request kind |
| CEX Examples | P11_feedback/examples/ | Real approval_request artifacts |
| Kind KC | P01_knowledge/library/kind/kc_approval_request.md | Domain knowledge, boundary, lifecycle |
| Kind manifest | P11_feedback/kind_approval_request/kind_manifest_n00.md | Canonical archetype example |
| kinds_meta | .cex/kinds_meta.json | max_bytes (2048), naming, llm_function, depends_on |
| ADR | cexai/docs/adr_v03_governance_taxonomy.md | Scope decision + re-evaluation trigger for this builder's existence |
## Tool Permissions

| Category | Tools | Status |
|----------|-------|--------|
| ALLOWED | Read, Write, Edit, Bash, Glob, Grep | Explicitly permitted |
| DENIED | Write/Edit to `.cexai/approvals/**` | The live watch-file path is Python-owned, never builder-owned |
| EFFECTIVE | Bash, Edit, Glob, Grep, Read, Write (scoped to P11_feedback/examples + compiled) | ALLOWED minus DENIED |

## Validation Checklist (manual until automated validator exists)
Run in order at Phase 3:
1. YAML frontmatter parses: `python -c "import yaml; yaml.safe_load(open('FILE').read().split('---')[1])"`
2. id pattern: `^p11_ar_[a-z][a-z0-9_]+$`
3. status in [pending, approved, denied, timeout]
4. request_id, operation, requester are non-empty strings
5. expires_at is valid ISO-8601
6. quality == null
7. Body <= 2048 bytes: `python -c "print(len(open('FILE','rb').read()))"`
8. Scope Disclaimer section present (fixture vs audit-transcription)

## Pipeline Integration

1. Created via 8F pipeline from F1-Focus through F8-Furnish
2. Scored by cex_score across three structural layers
3. Compiled by cex_compile for structural validation
4. Retrieved by cex_retriever for context injection
5. Evolved by cex_evolve when quality regresses below target

## Metadata

```yaml
id: bld_tools_approval_request
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply bld-tools-approval-request.md
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_hitl_config]] | sibling (emitting-policy builder's tools) | 0.56 |
| [[bld_architecture_approval_request]] | sibling | 0.52 |
| [[bld_config_approval_request]] | sibling | 0.50 |
| [[bld_schema_approval_request]] | sibling | 0.48 |
| [[adr_v03_governance_taxonomy]] | related (scope-defining ADR) | 0.40 |
