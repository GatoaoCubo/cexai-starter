---
name: simplify
description: Review changed code for reuse, quality, and efficiency, then fix any issues found. Use when user says "simplify", "/simplify", "clean this up", or "reduce complexity".
nucleus: all
related:
  - simplify
  - bld_tools_diff_strategy
  - p02_agent_code_review
  - p03_ins_code_review
  - bld_knowledge_card_diff_strategy
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_xxx. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

# simplify — reuse, quality, efficiency audit

Review code the user just changed (or a specified path), find simplifications, apply them.

## Scope

Default target: `git diff HEAD` (staged + unstaged). If user gives a path, target that.

## Three-lens audit

1. **Reuse**: Is there an existing helper/pattern being bypassed?
   - `Grep` for similar function signatures.
   - Check `_tools/`, `cex_sdk/`, nearest utility module.
   - Replace ad-hoc code with the canonical helper.
2. **Quality**: Is logic clearer than necessary?
   - Delete unused variables, dead branches, speculative try/except.
   - Merge duplicate blocks.
   - Flatten nested conditionals where early-return wins.
3. **Efficiency**: Hot path correct?
   - O(n²) over lists that should be sets/dicts.
   - Repeated I/O where batching is trivial.
   - Unnecessary serialization round-trips.

## Boundaries

- Do NOT refactor beyond the diff's scope unless user asks.
- Do NOT add abstractions "for the future" — YAGNI is the rule.
- Do NOT add comments explaining WHAT — only WHY when non-obvious.
- Preserve public API unless user authorized a breaking change.

## Verification

After each fix:
- Type-check if repo supports it (`mypy _tools/cex_xxx.py` etc.).  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
- Run affected tests.
- Report: N fixes applied, M lines removed, 0 behavior changes.

## Output

Bulleted diff summary. Each bullet: `path:line — what changed, why simpler`.


## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[simplify]] | related | 0.38 |
| bld_tools_diff_strategy | related | 0.21 |
| p02_agent_code_review | related | 0.20 |
| p03_ins_code_review | related | 0.18 |
| bld_knowledge_card_diff_strategy | related | 0.18 |
