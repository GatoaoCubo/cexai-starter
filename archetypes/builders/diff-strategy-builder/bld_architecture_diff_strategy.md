---
kind: architecture
id: bld_architecture_diff_strategy
pillar: P08
llm_function: CONSTRAIN
purpose: Component map of diff_strategy -- inventory, dependencies
quality: null
title: "Architecture Diff Strategy"
version: "1.1.0"
author: n06_audit_hybrid_review2
tags: [diff_strategy, builder, architecture]
tldr: "Component map of code diff pipeline: algorithm core, hunk parser, patch applier, conflict detector"
domain: "diff_strategy construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F1_constrain"
keywords: [diff_strategy construction, architecture diff strategy, algorithm core, hunk parser, patch applier, conflict detector, diff_strategy, builder, architecture, component inventory]
density_score: 0.90
related:
  - diff-strategy-builder
  - p04_qg_diff_strategy
  - bld_knowledge_card_diff_strategy
  - bld_architecture_edit_format
  - edit-format-builder
---
## Component Inventory
| Name             | Role                                              | Implementation            | Status |
|:-----------------|:--------------------------------------------------|:--------------------------|:-------|
| Algorithm Core   | Computes minimal edit script (SES)                | Myers/patience/histogram  | Active |
| Hunk Parser      | Parses unified diff output into structured hunks  | Python difflib / libxdiff | Active |
| Patch Applier    | Applies hunks to target file with offset tracking | git apply / patch POSIX   | Active |
| Conflict Detector| Three-way merge; flags overlapping hunks          | git merge-file / libgit2  | Active |
| Cache Layer      | Memoizes LCS for repeated comparison requests     | In-memory LRU             | Active |
| Format Bridge    | Converts internal delta to edit_format output     | Aider whole/diff/udiff    | Active |

## Dependencies
| From            | To                      | Direction | Notes                             |
|:----------------|:------------------------|:----------|:----------------------------------|
| Tokenizer/Parser| Algorithm Core          | Inbound   | Provides line or token sequence   |
| Algorithm Core  | Hunk Parser             | Internal  | Emits raw edit script             |
| Hunk Parser     | Patch Applier           | Internal  | Structured hunk list              |
| Patch Applier   | Conflict Detector       | Internal  | Detects apply failures            |
| Format Bridge   | edit_format-builder     | Outbound  | Final serialization for LLM       |
| Cache Layer     | Algorithm Core          | Support   | Speeds repeated large-file diffs  |

## Architectural Position
diff_strategy sits between the text/AST tokenizer (upstream) and the
edit_format serializer (downstream) in the LLM code-agent edit pipeline.

```
[Source File] --> [Tokenizer] --> [diff_strategy] --> [edit_format] --> [LLM output]
                                       |
                           Algorithm: Myers | patience |
                           histogram | Ratcliff-Obershelp
```

Reference implementations: Python difflib (stdlib), libxdiff (git internal),
Aider edit formats (whole, diff, udiff-simple, diff-fenced).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[diff-strategy-builder]] | upstream | 0.40 |
| [[p04_qg_diff_strategy]] | downstream | 0.40 |
| [[bld_knowledge_card_diff_strategy]] | upstream | 0.40 |
| [[bld_architecture_edit_format]] | sibling | 0.39 |
| [[edit-format-builder]] | upstream | 0.38 |
