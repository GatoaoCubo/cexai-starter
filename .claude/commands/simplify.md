---
id: simplify
kind: instruction
pillar: P08
title: "Simplify"
description: "Review and fix changed code for reuse, quality, efficiency. Usage: /simplify [path]"
version: "1.0.0"
author: cexai
quality: null
tags: [command, audit, refactor, lean, solo]
tldr: "Three-lens audit (reuse / quality / efficiency) over your diff or a path, with mechanical verification."
domain: "tenant CEXAI"
related:
  - build
  - validate
---

# /simplify -- audit & fix changed code

Review what changed and make it leaner, without changing behaviour. Solo
operator: the audit runs in-session, scoped to your diff or a given path.

## Usage
1. `/simplify` -- audit `git diff HEAD` (staged + unstaged).
2. `/simplify path/to/file.py` -- audit one file or directory.
3. `/simplify --since "1 hour ago"` -- audit recent commits.

## Three-lens audit
1. **Reuse** -- is an existing helper being bypassed? Replace ad-hoc code with the canonical call.
2. **Quality** -- dead code, duplicate blocks, needless nesting.
3. **Efficiency** -- O(n^2) over lists, redundant I/O, repeated serialization.

## Boundaries
- Stay inside the diff/path given. No speculative abstractions (YAGNI).
- No new comments unless the WHY is non-obvious.
- Do not change a public API without explicit authorization.
- Code must stay ASCII-only (`.claude/rules/ascii-code-rule.md`).

## Verify after each fix
1. Type-check if available (`mypy`, `tsc`, `pyright`).
2. Run the affected tests.
3. If you touched a CEXAI artifact (.md with frontmatter), run the brain health check:
   ```bash
   python _tools/cex_doctor.py
   ```
4. Report: `N fixes, M lines removed, 0 behaviour changes`.

## Output
One bullet per fix:
`path:line -- what changed, why it is simpler`
