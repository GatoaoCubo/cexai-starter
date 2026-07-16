---
kind: quality_gate
id: p11_qg_instruction
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of instruction artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: Instruction"
version: "1.0.0"
author: "builder_agent"
tags:
  - "quality-gate"
  - "instruction"
  - "steps"
  - "recipe"
  - "procedure"
  - "idempotency"
tldr: "Gates ensuring instruction artifacts decompose tasks into atomic verifiable steps with prerequisites, completion criteria, and rollback procedures."
domain: "instruction — step-by-step operational recipes for agent task execution"
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
keywords:
  - "completion criteria"
  - "and rollback procedures"
  - "quality-gate"
  - "instruction"
  - "steps"
  - "recipe"
  - "procedure"
density_score: 0.90
related:
  - instruction-builder
---
## Quality Gate

# Gate: Instruction
## Definition
| Field     | Value |
|-----------|-------|
| metric    | weighted soft score + all hard gates pass |
| threshold | 7.0 to publish; 8.0 for pool; 9.5 for golden |
| operator  | AND (all hard) + weighted average (soft) |
| scope     | any artifact with `kind: instruction` |
## HARD Gates
All must pass. Any failure = immediate reject.
| ID  | Check | Fail Condition |
|-----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | Parse error on any field |
| H02 | ID matches `^[a-z][a-z0-9_-]+$` | Uppercase, spaces, or leading digit |
| H03 | ID equals filename stem | `id: deploy_service` in file `restart_service.md` |
| H04 | Kind equals literal `instruction` | Any other kind value |
| H05 | Quality field is `null` | Any non-null value |
| H06 | All required fields present | Missing: steps, prerequisites, or completion_criteria |
## SOFT Scoring
Total weights sum to 100%.
| ID  | Dimension | Weight | 10 pts | 5 pts | 0 pts |
|-----|-----------|--------|--------|-------|-------|
| S01 | Step atomicity | 1.0 | Every step performs exactly one action and is independently verifiable | Most steps atomic; some compound | Steps are multi-action paragraphs |
| S02 | Prerequisites completeness | 1.0 | All tools, permissions, files, and env vars listed | Some prerequisites listed | No prerequisites section |
| S03 | Completion criteria | 1.0 | Each step has explicit success signal (exit code, file exists, output pattern) | Overall completion defined but not per-step | No success criteria |
| S04 | Rollback procedures | 1.0 | Undo steps defined for each destructive action | Partial rollback notes present | No rollback |
| S05 | Idempotency declaration | 0.5 | `idempotent: true/false` with explanation of why | Field present, no rationale | Field absent |
| S06 | Dependency ordering | 1.0 | Steps reference their predecessors explicitly when order matters | Steps ordered but dependencies implicit | Unordered; any sequence implied |
**Score = sum(pts * weight) / sum(max_pts * weight) * 10**
## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | Golden | Publish to pool as golden operational runbook |
| >= 8.0 | Skilled | Publish to pool + log pattern |
| >= 7.0 | Learning | Use but flag for improvement |
| < 7.0 | Rejected | Return to author with gate report |
## Bypass
| Field | Value |
|-------|-------|
| Conditions | Novel procedure being executed for the first time; rollback path not yet known |
| Approver | Task owner + one peer reviewer |
| Audit trail | `bypass_reason` required; note which gates are bypassed and why |

## Examples

# Examples: instruction-builder
## Golden Example
INPUT: "Create instruction for rebuilding the Brain FAISS index"
OUTPUT:
```yaml
id: p03_ins_rebuild_brain_faiss
kind: instruction
pillar: P03
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder"
title: "Rebuild Brain FAISS Index"
target: "knowledge-engine agent_group or human operator"
steps_count: 6
prerequisites:
  - "Ollama running locally with nomic-embed-text model"
  - "Python 3.10+ with faiss-cpu installed"
  - "At least 2GB free disk space"
validation_method: checklist
idempotent: true
atomic: false
rollback: "Delete generated .faiss files and revert to previous index backup"
dependencies:
  - "ollama"
  - "faiss-cpu"
  - "build_indexes_ollama.py"
logging: true
domain: "knowledge"
quality: null
tags: [instruction, brain, faiss, index, rebuild]
tldr: "6-step procedure to rebuild Brain FAISS+BM25 index from pool artifacts using Ollama embeddings"
density_score: 0.90
```
## Prerequisites
- Ollama running: `ollama list` shows `nomic-embed-text`
- Python deps: `python -c "import faiss; print(faiss.__version__)"`
- Disk space: `df -h .` shows >= 2GB free
## Steps
1. Backup current index — `cp records/core/brain/*.faiss records/core/brain/backup/`
2. Verify Ollama health — `ollama list | grep nomic-embed-text`
3. Run index builder — `cd records/core/brain/mcp-organization-brain && python build_indexes_ollama.py --scope all`
4. Wait for completion — process takes ~20 minutes, outputs progress to stdout
5. Verify index size — `ls -la records/core/brain/*.faiss` (expect ~140MB)
6. Test query — `python -c "from brain_search import search; print(search('test query')[:1])"`
## Validation
- [ ] New .faiss files exist and are > 100MB
- [ ] brain_query returns results for known terms
- [ ] No error output in build log
- [ ] Index timestamp matches current date
## Rollback
Restore backup: `cp records/core/brain/backup/*.faiss records/core/brain/`
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p03_ins_ pattern (H02 pass)
- kind: instruction (H04 pass)
- 20 required fields present (H06 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
