---
name: compress-on-huge-context
description: Compress assembled context via cex_compress when the prompt exceeds 20K tokens to protect provider budgets and recall quality.
when:
  - Building a prompt whose injected context (F3) exceeds 20K tokens.
  - Approaching a provider context window cap (e.g. 200K Sonnet, 1M Opus, 128K Codex).
  - Repeated F3 passes accumulate stale or duplicate sources.
kind: skill
pillar: P04
nucleus: all
quality: null
version: 1.0.0
created: 2026-04-27
updated: 2026-04-27
multi_runtime: true
runtimes: [claude, codex, gemini, ollama]
density_score: 0.86
tags: [skill, autofire, compression, context, autowire, layer3]
related:
  - 8f-reasoning
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_compress. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

# Compress on Huge Context

## When this fires
- F3 INJECT assembles context whose token count is >= 20,000.
- Total prompt tokens are within 20% of the active provider's context cap.
- A long-running session has accumulated prior turns that exceed 50% of remaining budget.

## What to do
1. Run `python _tools/cex_compress.py --target <prompt_or_path> --budget 16000` BEFORE the LLM call fires.  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
2. Prefer `cex_secretariat.py` for full-session compression when the user runs interactively (it preserves task state).
3. Cache compressed bundles in `.cex/cache/preflight/` so identical contexts do not re-compress.
4. Always preserve: user message, system prompt, the resolved kind/pillar/nucleus tuple, and the F1 CONSTRAIN block.
5. Compress aggressively: knowledge_card bodies, retrieved chunks, prior tool outputs.
6. If compression cuts more than 60% of tokens, log a warning -- the F3 retriever may be over-fetching; review `retriever_config`.

## Example
- N04 retrieves 12 KCs for an injection (~30K tokens). Skill fires compressor with budget=16K. Output retains F1 block + top-5 KCs (re-ranked). Final prompt fits in 17K, leaves 3K headroom inside the model's context window.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| 8f-reasoning | upstream | 0.50 |
