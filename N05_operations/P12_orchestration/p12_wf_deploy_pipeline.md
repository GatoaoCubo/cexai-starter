---
id: p12_wf_deploy_pipeline
kind: workflow
pillar: P12
version: "1.0.0"
created: "2026-07-20"
updated: "2026-07-20"
author: n05_operations
title: "Artifact Deploy Pipeline"
steps_count: 10
execution: sequential
agent_groups:
  - "n05_operations"
timeout: 1800
retry_policy: per_step
depends_on: []
signals:
  - "validate_ok"
  - "build_ok"
  - "compile_ok"
  - "test_ok"
  - "doctor_ok"
  - "sanitize_ok"
  - "score_ok"
  - "stage_ok"
  - "signal_ok"
  - "deploy_ok"
domain: deployment-pipeline
quality: null
tags: [workflow, deploy, ci-cd, n05, gating-wrath]
tldr: "10-step sequential deploy pipeline: validate->build->compile->test->doctor->sanitize->score->stage->signal->deploy. Hard gate on every step."
related:
  - p11_qg_workflow
  - p10_lr_chain_builder
  - p12_ct_release_gate
  - p07_bm_ops_pipeline
---

## Purpose

Authoritative artifact deploy pipeline. Gating Wrath: every stage is a hard
gate -- failure blocks promotion. Steps 1-6 retry max 2 then abort. Step 7
loops back to BUILD on quality < 8.0 (no cap). Steps 8-9 require manual
investigation on failure. Step 10 is human-gated -- never auto-pushed.

## Steps

| # | Name | Agent | Tool | Input | Output | Signal | On failure |
|---|------|-------|------|-------|--------|--------|------------|
| 1 | VALIDATE | n05_operations | `cex_hooks.py` | staged files | gate pass or errors | `validate_ok` | fix source, retry max 2 |
| 2 | BUILD | n05_operations | 8F pipeline (F1-F8) | intent tuple | `.md` artifact | `build_ok` | revise context, retry max 2 |
| 3 | COMPILE | n05_operations | `cex_compile.py {path}` | artifact `.md` | compiled `.yaml` | `compile_ok` | fix frontmatter, retry max 2 |
| 4 | TEST | n05_operations | `cex_system_test.py` | repo + artifact | all registered tests pass | `test_ok` | fix tests, retry max 2; escalate to the tester role |
| 5 | DOCTOR | n05_operations | `cex_doctor.py` | repo state | all builders PASS | `doctor_ok` | remediate artifact, retry max 2 |
| 6 | SANITIZE | n05_operations | `cex_sanitize.py --check` | `.py` + `.ps1` | clean exit (0) | `sanitize_ok` | `--fix` re-check, retry max 2 |
| 7 | SCORE | n05_operations | `cex_score.py {path}` | `.md` + `.yaml` | score >= 8.0 | `score_ok` | < 8.0: feedback -> return to Step 2 |
| 8 | STAGE | n05_operations | `git add` + `git commit` | artifact + score | commit with nucleus-tagged prefix | `stage_ok` | investigate conflict; manual only |
| 9 | SIGNAL | n05_operations | `signal_writer.write_signal` | nucleus, score, commit | signal in `.cex/runtime/signals/` | `signal_ok` | check permissions; write manually |
| 10 | DEPLOY | operator (human) | `git push origin main` | commit + signal | remote updated | `deploy_ok` | never auto-push; operator decides |

**Dependencies**: each step requires the prior step's signal. Step 7 failure
returns to Step 2. Step 10 requires Steps 8 and 9.

## Dependencies

1. `cex_hooks.py` registered as a pre-commit hook (`_tools/`)
2. `cex_compile.py`, `cex_system_test.py`, `cex_doctor.py`, `cex_sanitize.py`, `cex_score.py` in `_tools/`
3. `signal_writer.py` at `_tools/signal_writer.py`
4. `.cex/runtime/signals/` directory writable
5. Git repo with clean working tree before Step 8

## Signals

1. **Per step success**: named signal from frontmatter `signals` list
2. **Steps 1-6 failure**: retry max 2; emit `{step}_error` on exhaustion, abort
3. **Step 7 failure**: emit `score_fail`; loop to Step 2 with feedback; no cap
4. **Steps 8-9 failure**: emit `stage_error` / `signal_error`; manual required
5. **Step 10**: `deploy_ok` by operator only; no automated promotion

## References

1. `_tools/cex_hooks.py` -- frontmatter + encoding checks
2. `_tools/cex_compile.py` -- .md to .yaml
3. `_tools/cex_system_test.py` -- registered system tests
4. `_tools/cex_doctor.py` -- builder health checks
5. `_tools/cex_sanitize.py` -- ASCII enforcement
6. `_tools/cex_score.py` -- 3-layer scoring (structural/rubric/semantic)
7. `_tools/signal_writer.py` -- inter-nucleus signals

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p11_qg_workflow]] | related | 0.30 |
| [[p10_lr_chain_builder]] | upstream | 0.30 |
| [[p12_ct_release_gate]] | sibling | 0.32 |
| [[p07_bm_ops_pipeline]] | related | 0.28 |
