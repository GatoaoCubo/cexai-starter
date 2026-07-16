---
kind: instruction
id: bld_instruction_diff_strategy
pillar: P03
llm_function: REASON
purpose: Step-by-step production process for diff_strategy
quality: null
title: "Instruction Diff Strategy"
version: "1.0.0"
author: wave1_builder_gen
tags: [diff_strategy, builder, instruction]
tldr: "Step-by-step production process for diff_strategy"
domain: "diff_strategy construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F6_produce"
keywords: [diff_strategy construction, instruction diff strategy, diff_strategy, builder, instruction, write algorithm, write patch application, write edge cases, related artifacts, aider format]
density_score: 0.85
related:
  - bld_output_template_diff_strategy
  - bld_tools_diff_strategy
  - p04_qg_diff_strategy
  - diff-strategy-builder
  - bld_knowledge_card_diff_strategy
---
## Phase 1: RESEARCH
1. Identify the target consumer: Aider format (whole/diff/udiff-simple/diff-fenced), git pipeline, or custom LLM agent.
2. Determine input granularity: line-level (default), token-level, character-level, or AST-level.
3. Select algorithm:
   - Myers: default for fast O(ND) line diffs; git's fallback algorithm
   - patience/histogram: prefer when code has many identical-looking lines (braces, blanks)
   - Ratcliff-Obershelp: gestalt matching; use when difflib.SequenceMatcher is the runtime
   - custom: AST-level structural diff (tree-sitter + GumTree) for semantic code changes
4. Benchmark against real files: small (<200 lines), medium (200-2000), large (2000+).
5. Document context: patch application tool (git apply, patch, difflib), three-way merge requirements.

## Phase 2: COMPOSE
1. Fill OUTPUT_TEMPLATE.md: algorithm_type, granularity, comparison_basis (required fields).
2. Write Algorithm section: time/space complexity, patch format (unified/context/custom).
3. Write Patch Application section: tool, --3way flag, whitespace handling, encoding normalization.
4. Write Edge Cases table: empty diff, binary, CRLF/LF, identical files, partial match (min 5 rows).
5. Reference real tools: difflib, git apply --3way, patch -p1, Aider format name.
6. Validate ID pattern: p04_ds_{{name}}.md

## Phase 3: VALIDATE
- [ ] algorithm_type in [Myers, LCS, patience, histogram, Ratcliff-Obershelp, custom]
- [ ] granularity in [line, token, character, AST, semantic]
- [ ] Edge cases table has >= 5 rows
- [ ] At least 1 real tool cited (difflib / git apply / patch / Aider format)
- [ ] No fictional tool references (no strat_backtest.py, CCXT, Backtrader, etc.)
- [ ] Patch application is idempotent (documented)
- [ ] cex_compile.py run on artifact path

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_output_template_diff_strategy]] | downstream | 0.53 |
| [[bld_tools_diff_strategy]] | downstream | 0.51 |
| [[p04_qg_diff_strategy]] | downstream | 0.49 |
| [[diff-strategy-builder]] | downstream | 0.48 |
| [[bld_knowledge_card_diff_strategy]] | upstream | 0.44 |
