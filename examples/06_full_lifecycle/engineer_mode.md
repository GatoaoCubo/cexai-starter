---
id: ex_lifecycle_engineer_mode
kind: reasoning_trace
pillar: P03
title: "Engineer Mode -- Full 8F Trace with Payloads"
version: 1.0.0
created: 2026-04-27
quality: null
density_score: 0.92
tags: [example, reasoning_trace, 8f, engineer]
related:
  - ex_full_lifecycle
  - 8f-reasoning
---

# Engineer Mode -- Full 8F Trace

User input: `"I want to teach my team about prompt caching"`

Nucleus: N04 (Knowledge Gluttony)

## Pre-8F: Intent Resolution

```json
{
  "raw_input": "I want to teach my team about prompt caching",
  "resolver": "cex_intent_resolver.py",
  "result": {
    "kind": "knowledge_card",
    "pillar": "P01",
    "nucleus": "N04",
    "verb": "document",
    "confidence": 0.94,
    "match_rule": "teach.*about -> document, caching -> P01 knowledge domain"
  },
  "gdp_required": false
}
```

Confidence 94% exceeds the 60% threshold. No GDP decision points needed.

### F1 CONSTRAIN

```
F1: kind=knowledge_card, pillar=P01, max_bytes=5120, naming=p01_kc_prompt_caching.md
```

Lookup from `.cex/kinds_meta.json`:

```json
{
  "knowledge_card": {
    "pillar": "P01",
    "llm_function": "INJECT",
    "max_bytes": 5120,
    "naming": "p01_kc_{{topic}}.md + .yaml",
    "core": true,
    "depends_on": ["citation"],
    "requires_external_context": true,
    "primary_8f": "F3_inject"
  }
}
```

Schema loaded from `N00_genesis/P01_knowledge/_schema.yaml`. Constraints set:
density >= 0.80, frontmatter required (id, kind, pillar, title, version, quality: null, tags).

### F2 BECOME

```
F2: knowledge-card-builder loaded (12 ISOs, 12-pillar). Identity: Knowledge Gluttony
```

Builder ISOs read from `archetypes/builders/knowledge-card-builder/`:

| ISO | Pillar | Function |
|-----|--------|----------|
| bld_model_knowledge_card.md | P02 | BECOME -- builder identity + sin lens |
| bld_prompt_knowledge_card.md | P03 | PRODUCE -- generation instructions |
| bld_schema_knowledge_card.md | P06 | CONSTRAIN -- frontmatter schema |
| bld_eval_knowledge_card.md | P07 | GOVERN -- scoring rubric |
| bld_architecture_knowledge_card.md | P08 | CONSTRAIN -- structural rules |
| bld_feedback_knowledge_card.md | P11 | GOVERN -- quality gate config |
| bld_orchestration_knowledge_card.md | P12 | COLLABORATE -- handoff protocol |
| ... | ... | (12 total, one per pillar) |

Sin lens injected: **Knowledge Gluttony** -- ingest every source, maximize
density, leave no fact behind.

### F2b SPEAK

```
F2b: Vocabulary loaded (47 terms). Drift prevention: active.
```

Loaded `N04_knowledge/P01_knowledge/kc_knowledge_vocabulary.md`. Key enforced
terms: "knowledge_card" (never "research card"), "density_score" (never
"info ratio"), "citation" (never "source link").

### F3 INJECT

```
F3: Injected 4 knowledge sources. Template-First match: 78%
```

| Source | Path | Relevance |
|--------|------|-----------|
| Kind KC | `N00_genesis/P01_knowledge/library/kind/kc_knowledge_card.md` | 0.95 |
| Similar KC | `P01_knowledge/kc_context_window_optimization.md` | 0.72 |
| Similar KC | `P01_knowledge/kc_api_rate_limiting.md` | 0.68 |
| Brand context | `.cex/config/brand_config.yaml` | 0.50 |

Template-First score 78% (above 60% threshold): adapt from
`kc_context_window_optimization.md` structure rather than writing from scratch.

### F4 REASON

```
F4: Plan -- 5 sections, approach: template (adapt from 78% match)
```

Planned sections:

| # | Section | Est. bytes | Density target |
|---|---------|-----------|---------------|
| 1 | Summary (tldr) | 200 | 0.90 |
| 2 | Core Concepts | 1200 | 0.88 |
| 3 | Implementation | 1000 | 0.85 |
| 4 | Anti-Patterns | 600 | 0.90 |
| 5 | Cross-Framework References | 400 | 0.85 |

Total estimated: 3,400 bytes (within 5,120 max). Density target: 0.87 overall.

### F5 CALL

```
F5: Tools ready. 3 similar artifacts found.
```

Tools available for post-production:
- `cex_compile.py` -- .md to .yaml compilation
- `cex_doctor.py` -- frontmatter + size + density validation
- `cex_index.py` -- wikilink + cross-reference indexing
- `signal_writer.py` -- completion signal to N07

3 similar knowledge_cards found via `cex_retriever.py` TF-IDF scan.
Reuse: section headings from template match; original content for prompt
caching specifics.

### F6 PRODUCE

```
F6: Draft generated (3,840 bytes, 5 sections, density=0.89)
```

Generated artifact (abbreviated):

```yaml
---
id: p01_kc_prompt_caching
kind: knowledge_card
pillar: P01
nucleus: n04
title: "Prompt Caching -- Reduce Latency and Cost via Prefix Reuse"
version: "1.0.0"
created: 2026-04-27
quality: null
tags: [prompt-caching, latency, cost, anthropic, openai]
density_score: 0.89
related:
  - p01_kc_context_window_optimization
  - p01_kc_api_rate_limiting
---

# Prompt Caching

## Summary
Prompt caching stores the KV-cache of a static prefix so subsequent
requests sharing that prefix skip re-computation. Anthropic charges
90% less for cached input tokens; OpenAI applies automatic caching
after 1024-token prefixes. The technique reduces P50 latency 40-60%
on system-prompt-heavy workloads.

## Core Concepts
...

## Anti-Patterns
| Pattern | Why it fails |
|---------|-------------|
| Timestamp in system prompt | Busts cache every request |
| Randomized few-shot order | Prefix diverges after first example |
| Per-user preamble before static block | Static block never reaches cache threshold |

## Cross-Framework References
| Provider | Mechanism |
|----------|-----------|
| Anthropic | cache_control: {"type": "ephemeral"} on message block |
| OpenAI | Automatic after 1024-token prefix match |
| Google | Context caching API (explicit create + TTL) |
```

### F7 GOVERN

```
F7: Score 9.1/10. Gates: 7/7. 12LP: 12/12
```

**Hard gates (H01-H07):**

| Gate | Check | Result |
|------|-------|--------|
| H01 | Frontmatter present + valid YAML | PASS |
| H02 | id matches naming convention (p01_kc_*) | PASS |
| H03 | kind field matches kinds_meta entry | PASS |
| H04 | quality: null (never self-scored) | PASS |
| H05 | Size <= max_bytes (3,840 <= 5,120) | PASS |
| H06 | Density >= 0.80 (actual: 0.89) | PASS |
| H07 | No non-ASCII in code blocks | PASS |

**5D scoring:**

| Dimension | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| D1 Accuracy | 0.25 | 9.2 | 2.30 |
| D2 Density | 0.25 | 8.9 | 2.23 |
| D3 Structure | 0.20 | 9.3 | 1.86 |
| D4 Actionability | 0.15 | 9.0 | 1.35 |
| D5 Cross-reference | 0.15 | 9.1 | 1.37 |
| **Total** | **1.00** | | **9.10** |

Score 9.1 exceeds the 8.0 floor. No retry needed.

**12LP checklist:** 12/12 pass (one check per pillar -- knowledge present,
model aligned, prompt coherent, tools declared, output formatted, schema
valid, eval scored, architecture compliant, config defaults set, memory
referenced, feedback loop wired, orchestration signaled).

### F8 COLLABORATE

```
F8: Saved P01_knowledge/kc_prompt_caching.md. Compiled. Committed. Signal sent.
```

Actions executed:

```bash
# Save
write P01_knowledge/kc_prompt_caching.md

# Compile
python _tools/cex_compile.py P01_knowledge/kc_prompt_caching.md
# Output: compiled/P01_knowledge/kc_prompt_caching.yaml (OK)

# Index
python _tools/cex_index.py
# Output: 2 new wikilinks indexed

# Commit
git add P01_knowledge/kc_prompt_caching.md compiled/
git commit -m "[N04] knowledge_card: prompt caching (density 0.89, 9.1/10)"

# Signal
python -c "from _tools.signal_writer import write_signal; write_signal('n04', 'complete', 9.1)"
```

Signal payload written to `.cex/runtime/signals/`:

```json
{
  "nucleus": "n04",
  "status": "complete",
  "score": 9.1,
  "artifact": "P01_knowledge/kc_prompt_caching.md",
  "kind": "knowledge_card",
  "bytes": 3840,
  "timestamp": "2026-04-27T14:23:07Z"
}
```

N07 picks up the signal, verifies the commit, and marks N04's task complete.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[ex_full_lifecycle]] | parent | 1.00 |
| 8f-reasoning | reference | 0.90 |
| [[kc_knowledge_card]] | template | 0.85 |
| [[ex_lifecycle_business_mode]] | sibling | 0.95 |
