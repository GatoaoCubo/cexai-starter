---
quality: null
id: bld_orchestration_default
kind: builder_default
pillar: P12
source: shared
title: "Orchestration Default: Standard Signal + Compile + Commit Protocol"
llm_function: COLLABORATE
version: 1.1.0
quality: null
tags: [orchestration, signal, compile, commit, P12, shared, default]
tldr: "_Shared orchestration: workflow coordination, handoffs, and lifecycle management"
8f: "F8_collaborate"
keywords: [orchestration default, standard signal, commit protocol, shared orchestration, workflow coordination, and lifecycle management, orchestration, signal, compile, commit]
author: builder
density_score: 1.0
created: "2026-04-17"
updated: "2026-04-22"
related:
  - bld_eval_default
  - bld_feedback_default
  - bld_config_default
  - bld_tools_default
  - bld_architecture_default
---
# P12 Orchestration — Standard F8 Protocol

## 8F Compliance Marking

At each pipeline stage, emit the marker so the enforcer tracks compliance:
```bash
python _tools/cex_8f_enforcer.py --session $CEX_SESSION --mark F1 --kind {kind}
```
Replace F1 with the current stage (F1-F8). If `$CEX_SESSION` is unset, use
`{nucleus}_{kind}_{unix_timestamp}`. The enforcer is non-blocking and
degrades gracefully if missing.

## F8 COLLABORATE Steps (in order)

### 1. Save
Write the artifact to the correct pillar directory:
`N{nucleus}_{domain}/P{pillar_number}_{pillar_name}/{id}.md`

### 2. Compile
```bash
python _tools/cex_compile.py {artifact_path}
```
Compiles .md -> .yaml in the corresponding `compiled/` directory.
If compile fails, fix the issue before proceeding.

### 3. Index (optional, run if available)
```bash
python _tools/cex_index.py
```

### 4. Commit
```bash
git add {artifact_path} {compiled_path}
git commit -m "[N{nucleus}] {kind}: {artifact_title} (8F, quality=pending)"
```

### 5. Signal
```python
from _tools.signal_writer import write_signal
write_signal('{nucleus}', 'complete', 9.0)
```
Or via CLI:
```bash
python -c "from _tools.signal_writer import write_signal; write_signal('{nucleus}', 'complete', 9.0)"
```

## Commit Message Format

```
[N{nucleus}] {kind}: {artifact_id} -- {one_line_description}

8F pipeline complete. Quality pending peer review.
Pillar: P{XX} | Domain: {domain}
```

## Signal Protocol

| Signal | When |
|--------|------|
| `complete` | Artifact saved, compiled, committed successfully |
| `error` | Build failed after 2 retries -- include error details |
| `needs_review` | Build complete but specific gate flagged for human review |

## Multi-Artifact Batch Commit

When building 3+ artifacts in a session:
```bash
git add N{nucleus}_*/P{pillar}*/  # stage pillar outputs only
git add {compiled_paths}
git commit -m "[N{nucleus}] batch: {count} {kind} artifacts -- {session_date}"
```

## Hard Gates (H01-H07) -- ALL must pass

| Gate | Check | Fail Action |
|------|-------|-------------|
| H01 | Frontmatter present and valid YAML | Return to F6, add frontmatter |
| H02 | `quality: null` in frontmatter (never self-score) | Remove score, set null |
| H03 | Required fields: id, kind, 8f, pillar, title | Add missing fields |
| H04 | Body density >= 0.85 (content lines / total lines) | Add structured data, remove filler |
| H05 | No hallucinated sources (cited paths must exist) | Remove or verify citations |
| H06 | ASCII-only in any generated code blocks | Replace non-ASCII per cex_sanitize rules |
| H07 | Output matches pillar schema constraints | Restructure to match schema |

## Scoring Dimensions (5D)

| Dimension | Weight | Criteria |
|-----------|--------|---------|
| D1 Structural | 30% | Frontmatter complete, naming correct, file in right pillar dir |
| D2 Content | 25% | Density >= 0.85, no filler, tables preferred over prose |
| D3 Accuracy | 20% | No hallucination, sources verified, constraints respected |
| D4 Usefulness | 15% | Actionable, implementable, unambiguous |
| D5 CEX fit | 10% | Kind/pillar/nucleus alignment, 8F stage correctness |

## When to Override This Default

Create `bld_orchestration_{kind}.md` to override this default when the kind needs:
- Custom signal payload beyond the standard score
- Non-standard compile targets (e.g., HTML output needs different compilation)
- Multi-file commit grouping specific to the kind's artifact set

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_eval_default]] | sibling | 0.46 |
| [[bld_feedback_default]] | sibling | 0.42 |
| [[bld_config_default]] | sibling | 0.42 |
| [[bld_tools_default]] | sibling | 0.38 |
| [[bld_architecture_default]] | sibling | 0.35 |
