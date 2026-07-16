---
kind: knowledge_card
id: bld_knowledge_card_edit_format
pillar: P01
llm_function: INJECT
purpose: Domain knowledge for edit_format production
quality: null
title: "Knowledge Card Edit Format"
version: "1.1.0"
author: n04_hybrid_review2
tags: [edit_format, builder, knowledge_card, aider, cursor, diff, search-replace]
tldr: "LLM-to-host file edit formats: Aider WHOLE/DIFF/UDIFF, search-replace blocks, unified diff"
domain: "edit_format construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F3_inject"
keywords: [edit_format, knowledge_card, aider, search-replace, unified diff, wire format]
density_score: 0.92
related:
  - edit-format-builder
  - bld_tools_diff_strategy
  - bld_output_template_edit_format
  - bld_knowledge_card_diff_strategy
  - n00_edit_format_manifest
---
## Domain Overview

This ISO specifies an edit format: how diffs or patches are expressed and applied.

Edit formats define the structured syntax LLMs use to communicate file modifications to
host systems (code editors, CI pipelines, auto-apply tools). The format must be: unambiguous
(the tool applies exactly what the LLM intended), resilient (handles whitespace drift, line
number changes), and parseable (simple regex/parser can extract and apply changes). Unlike
diff_strategy (which computes HOW differences are detected), edit_format defines the WIRE
FORMAT the LLM emits.

Four primary format families dominate production LLM coding tools:
1. **WHOLE file** (Aider WHOLE mode, Claude Projects file artifacts)
2. **Unified diff** (UDIFF, standard `diff -u` output)
3. **Search-replace blocks** (Aider search/replace, Cursor apply)
4. **Structured patch** (JSON Patch RFC 6902, language-server edits)

## Aider Edit Formats

| Mode | Mechanism | Pros | Cons | Use When |
|------|-----------|------|------|----------|
| WHOLE | Full file replacement | Simple, unambiguous | High token cost | Small files or major rewrites |
| DIFF | `<<<<<<< ORIGINAL` / `>>>>>>> UPDATED` markers | Explicit before/after | Needs fuzzy match on drift | Medium files, precise blocks |
| UDIFF | Standard `diff -u` with `@@` hunks | Git-compatible, minimal tokens | Line numbers drift | Small targeted changes |
| UDIFF-SIMPLE | Like UDIFF without `@@` headers | Fewest tokens | No context anchoring | Single-hunk changes |

## Search-Replace Block Format

Most resilient format for LLM edits. Uses `<<<<<<< SEARCH` / `=======` / `>>>>>>> REPLACE` markers.
- SEARCH block must match file content EXACTLY (case, whitespace, indentation)
- Not found = raise error, never skip silently
- Multiple blocks apply sequentially; empty SEARCH = prepend; empty REPLACE = delete
- Used by Aider (search/replace mode) and Cursor (apply format)

## Structured Edit Formats

- **JSON Patch (RFC 6902)**: operations `add/remove/replace/move/copy/test` for JSON/YAML
- **LSP TextEdit**: range-based edits for VS Code, Neovim, JetBrains

## Key Concepts

| Concept | Definition | Source |
|---------|-----------|--------|
| Hunk | Contiguous block of changed lines with context | Git diff format |
| Search-replace block | SEARCH/REPLACE marker pair for context-anchored edits | Aider docs |
| Unified diff | Standard `-u` diff format: --- / +++ headers + @@ hunks | POSIX diff |
| WHOLE mode | Full file replacement -- highest token cost, lowest ambiguity | Aider docs |
| Fuzzy matching | Finding SEARCH block even with minor whitespace drift | Aider core |
| JSON Patch | RFC 6902 structured operations for JSON/YAML documents | RFC 6902 |
| LSP TextEdit | Range-based in-editor modification | LSP spec v3.17 |
| Context lines | Unchanged lines surrounding a hunk -- anchor for application | diff manual |
| Conflict marker | <<<<<< / ====== / >>>>>> merge conflict syntax | Git |

## Industry Standards

| Standard | Notes |
|----------|-------|
| RFC 6902 | JSON Patch -- `add`, `remove`, `replace`, `move`, `copy`, `test` |
| POSIX diff -u | Unified diff format -- `---`, `+++`, `@@ -n,m +n,m @@` |
| LSP spec v3.17 | TextEdit, WorkspaceEdit for editor-level changes |
| Aider edit formats | WHOLE / DIFF / UDIFF / SEARCH-REPLACE (see aider.chat/docs) |
| Cursor apply | Search-replace variant with triple-backtick fencing |
| RFC 5261 | XML Patch -- analogous to JSON Patch for XML |

## Common Patterns

1. **Default to search-replace** for LLM coding agents -- no line number drift, explicit context
2. **WHOLE for new files** -- nothing to match, full content is always correct
3. **Unified diff for git integration** -- output can be piped to `git apply` directly
4. **Multiple hunks per response** -- apply sequentially top-to-bottom to avoid offset shifts
5. **Include file path in every format** -- host tool needs path to locate file

## Pitfalls

- Using line numbers as anchors -- they change with every edit and cause misapplication
- SEARCH block with loose whitespace matching -- exact match is required for reliability
- Missing file path in WHOLE mode -- host cannot determine target file
- Applying hunks out of order -- later hunks have shifted line numbers after earlier ones apply
- Confusing edit_format (wire format) with diff_strategy (algorithm) -- they are separate concerns
- Citing RFC 6943 for JSON Patch -- correct reference is RFC 6902

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[edit-format-builder]] | downstream | 0.54 |
| [[bld_tools_diff_strategy]] | downstream | 0.44 |
| [[bld_output_template_edit_format]] | downstream | 0.43 |
| [[bld_knowledge_card_diff_strategy]] | sibling | 0.38 |
| [[n00_edit_format_manifest]] | sibling | 0.37 |
