---
id: p01_kc_git_workflow_for_agents
kind: knowledge_card
8f: F3_inject
title: "Git Workflow for Autonomous Agents"
version: 1.0.0
quality: null
tldr: "Defensive knowledge card derived from the kc-git-workflow-for-agents skill -- typed for unclassified detection, scoped to authorized use, framework-aligned to its NIST CSF controls."
when_to_use: "Consult to understand the unclassified control defensively before you build, configure, or audit it."
long_tails:
  - "what is the kc-git-workflow-for-agents defensive control"
  - "how does kc-git-workflow-for-agents detection work"
  - "reference card for the kc-git-workflow-for-agents skill"
primary_8f: INJECT
slots:
  AUTHORIZED_SCOPE: "<authorized asset/log source under analysis>"
  CONTROL_FOCUS: "<NIST CSF control to prioritize this run>"
  TIME_WINDOW: "<bounded analysis window>"
pillar: P01
language: en
keywords:
  - "[auto] <timestamp>"
  - "origin/feature/<hash>"
  - "git checkout -b feature/<purpose>"
  - "git push --set-upstream origin feature/<purpose>"
  - "git merge --no-ff feature/<purpose>"
  - "git merge --no-ff"
  - "git merge --no-ff -x recursive"
  - "git mergetool"
  - "git workflow"
  - "autonomous agents"
related:
  - p01_kc_git_worktree_isolation
  - p01_kc_git_hooks_ci
  - bld_output_template_contributor_guide
  - p01_kc_aider_integration_patterns
  - p11_qg_tdd_compliance
  - p12_wf_auto_ship
  - p03_ins_action_protocol
  - p04_hook_pre_commit_qa
---

# Git Workflow for Autonomous Agents

## Auto-Commits
Autonomous agents should auto-commit changes with:
- Timestamp-based commit messages (`[AUTO] <timestamp>`)
- Hash-based branch tracking (`origin/feature/<hash>`)
- Automatic staging of all modified files

## Branch Strategies
Use feature branches for isolated development:
1. `git checkout -b feature/<purpose>`
2. `git push --set-upstream origin feature/<purpose>`
3. Merge with `git merge --no-ff feature/<purpose>`

## Conflict Resolution
Resolve conflicts using:
1. `git merge --no-ff` for linear history
2. `git merge --no-ff -X recursive` for complex merges
3. Manual resolution with `git mergetool`

## Commit Message Conventions
Follow conventional commits:
```
<type>(<scope>): <description>
<type>: <description>
```
Types: feat, fix, docs, style, refactor, test, chore

## Pre-Commit Hooks
Implement pre-commit checks with:
1. Linting: `husky pre-commit` with ESLint/Prettier
2. Testing: `npm test` integration
3. Type checking: `tsc --noEmit`
4. Code formatting: `prettier --write .`

## Best Practices
1. Use `git rebase -i` for history cleanup (e.g., squashing 5 commits into a single atomic change)
2. Enable `core.autocrlf=true` for cross-platform consistency (Windows vs Linux line endings)
3. Configure `user.name` and `user.email` for audit trails (e.g., "agent-001@company.com")
4. Use `git diff` before committing to verify changes (especially for binary files)
5. Implement `git commit --amend` for last-commit fixes (avoid rewriting history after push)

## Comparison of Git Workflows for Autonomous Agents

| Workflow Type         | Branching Strategy       | Merge Method               | Commit Message Style       | Use Case                          |
|-----------------------|--------------------------|----------------------------|----------------------------|-----------------------------------|
| GitFlow               | Feature + Release branches | Merge with squash        | Conventional Commits       | Long-term feature development     |
| Trunk-Based           | No long-lived branches   | Rebase + Merge             | Semantic Commits           | Continuous delivery pipelines     |
| Feature Branch        | Per-feature branches     | Merge --no-ff            | Conventional Commits       | Isolated experimentation          |
| Trunk-Based (GitOps)  | No branches              | Merge with rebase        | GitOps-specific format     | Infrastructure-as-code workflows  |
| Autonomous Agent      | Hash-based branches      | Auto-merge with CI       | Timestamp + Hash           | Self-contained agent development  |

## Boundary
Static, versioned knowledge distilled from operational patterns. Not a configuration template, instruction manual, or deployment spec.

## Related Kinds
- **knowledge_card_ci_cd_integration**: Defines how Git workflows interface with CI/CD pipelines
- **knowledge_card_code_review_checklist**: Specifies agent-specific code review criteria for merged branches
- **knowledge_card_version_control_strategies**: Covers broader VCS patterns including Git, Mercurial, and DAG-based systems
- **knowledge_card_automated_testing**: Describes test suite requirements for auto-commit validation
- **knowledge_card_devops_tools**: Lists tooling requirements for agent workflow automation

## 8F Pipeline Function
Primary function: **INJECT**


Canonical baseline: the source skill bundle. The 8F verb is **INJECT** (F3): this
card injects defensive domain knowledge into downstream reasoning. Specific framework
controls are taken from the source bundle, not invented here.

### How to use
```text
8F verb: INJECT (F3). Read this card into context before acting on the control.
Use it to fix the vocabulary and the in-scope controls, not as an attack guide.
Verify any framework control you cite appears in the source bundle (anti-fab).
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p01_kc_git_worktree_isolation | sibling | 0.35 |
| p01_kc_git_hooks_ci | sibling | 0.33 |
| bld_output_template_contributor_guide | downstream | 0.28 |
| [[p01_kc_aider_integration_patterns]] | sibling | 0.27 |
| p11_qg_tdd_compliance | downstream | 0.26 |
| p12_wf_auto_ship | downstream | 0.24 |
| p03_ins_action_protocol | downstream | 0.22 |
| p04_hook_pre_commit_qa | downstream | 0.21 |