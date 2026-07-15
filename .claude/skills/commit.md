---
name: commit
description: Stage changes, write conventional commit grouped by nucleus, run pre-commit hooks. Use when user says "commit", "/commit", or explicitly asks to save changes to git.
nucleus: all
related:
  - p01_kc_git_hooks_ci
  - p11_qg_handoff
  - bld_orchestration_default
  - p04_hook_pre_commit_qa
  - p03_ins_action_protocol
---

# commit — CEX-aware git commit

Write a commit that fits this repo's conventions and survives hooks.

## Protocol

1. Inspect state in parallel:
   - `git status -s` (never `-uall`)
   - `git diff --stat`
   - `git log --oneline -5` (match house style)
2. Group staged files by nucleus prefix: `N01_*`, `N02_*`, ..., `_tools/*`, `.claude/*`.
3. Compose message:
   - Subject: `[N0x] <verb> <noun>` (≤70 chars). If touches multiple nuclei, use `[N07]` + scope names in body.
   - Body: 1-3 bullets on WHY, not WHAT.
   - Trailer: `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`
4. Stage specific files (no `git add -A` unless user explicit). Reject `.env`, `credentials*`, large binaries.
5. Run `git commit` via HEREDOC for multiline safety.
6. If pre-commit hook fails: fix underlying issue (NEVER `--no-verify`), re-stage, create a NEW commit (NEVER `--amend`).
7. `git status` after to confirm clean.

## Mandatory refusals

- No `--no-verify`, no `--no-gpg-sign`, no `--amend` of published commits.
- No force-push, no destructive ops without explicit user request.
- Do not commit secrets. If a secret sneaked in, warn loudly.

## Output

Report: commit SHA, files changed, hook results. Under 3 lines.


## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| p01_kc_git_hooks_ci | related | 0.43 |
| p11_qg_handoff | related | 0.34 |
| [[bld_orchestration_default]] | related | 0.32 |
| p04_hook_pre_commit_qa | related | 0.31 |
| p03_ins_action_protocol | related | 0.30 |
