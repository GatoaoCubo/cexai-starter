---
kind: quality_gate
id: p11_qg_reasoning_trace
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of reasoning_trace artifacts
pattern: few-shot learning for structured decision audit records
quality: null
title: 'Gate: Reasoning Trace'
version: 1.0.0
author: builder
tags:
- eval
- P11
- quality_gate
- examples
tldr: Gates ensuring reasoning traces define complete step-evidence-confidence chains,
  record rejected alternatives, calibrate confidence scores, and contain no execution
  instructions.
domain: reasoning_trace
created: '2026-04-06'
updated: '2026-04-06'
8f: "F7_govern"
keywords:
  - "reasoning trace"
  - "p03_rt_{agent}_{timestamp}"
  - "reasoning_trace"
  - "quality"
  - "agent"
  - "intent"
  - "steps"
density_score: 0.85
related:
  - p03_ins_reasoning_trace_builder
  - bld_knowledge_card_reasoning_trace
  - bld_schema_reasoning_trace
  - reasoning-trace-builder
  - bld_memory_reasoning_trace
---
## Quality Gate

## Definition
A reasoning_trace is a structured decision record capturing WHY an agent chose a particular path. It passes this gate when every step has concrete evidence, confidence is calibrated to the 0.0-1.0 scale, at least one alternative is rejected with an evidence-based reason, the conclusion references the strongest evidence, and the trace contains no execution instructions or workflow logic.
## HARD Gates
Failure on any HARD gate = immediate REJECT regardless of score.
| ID  | Check | Rationale |
|-----|-------|-----------|
| H01 | Frontmatter parses as valid YAML with no syntax errors | Unparseable file cannot be indexed or validated |
| H02 | `id` matches pattern `p03_rt_{agent}_{timestamp}` | Mismatched IDs cause routing failures |
| H03 | `kind` is exactly `reasoning_trace` (literal match) | Kind drives the loader; wrong literal silently misroutes |
| H04 | `quality` field is `null` (not filled by author) | Quality is assigned by this gate, not self-reported |
| H05 | `agent` field is non-empty string | Traces without agent attribution cannot be audited |
| H06 | `intent` field is non-empty string | Traces without intent have no decision context |
## SOFT Scoring
Dimensions are weighted; total normalized weight = 100%.
| # | Dimension | Weight | 1 (Poor) | 5 (Good) | 10 (Excellent) |
|---|-----------|--------|----------|----------|----------------|
| 1 | density >= 0.80 (content per token ratio) | 1.0 | Padded with filler prose | Mostly substantive | No filler; every sentence carries information |
| 2 | Evidence concreteness (references specific data, files, metrics vs vague claims) | 1.5 | Vague assertions ("it seemed better") | Some references ("benchmark showed improvement") | All steps cite specific metrics, files, or data points |
| 3 | Confidence calibration (scores match evidence strength, not over/under-confident) | 1.5 | All steps 0.9+ regardless of evidence | Most steps reasonably calibrated | Confidence clearly tracks evidence strength; low evidence = low confidence |
| 4 | Alternatives rejected with reasons (at least 1 rejected path with evidence-based reason) | 1.0 | No alternatives listed | Alternatives listed without reasons | Each alternative has specific evidence-based rejection reason |
| 5 | Conclusion references evidence (final decision cites strongest supporting data) | 1.0 | Conclusion is unsupported opinion | Conclusion mentions evidence vaguely | Conclusion directly references specific step evidence |
| 6 | Step ordering is logical (chronological or logical progression, no jumps) | 0.5 | Steps in random order | Mostly ordered | Clear logical/chronological progression |

## Examples

# Examples: reasoning-trace-builder
## Golden Example
INPUT: "Record why research-agent selected ada-002 over cohere-embed-v3 for P01 retriever"
OUTPUT (`p03_rt_research_agent_20260406T143000.yaml`):
```yaml
agent: research-agent
intent: select embedding model for P01 retriever
steps:
  - step: 1
    thought: OpenAI ada-002 is the most widely deployed embedding model with extensive documentation
    evidence: "MTEB benchmark: 63.4% average, 8191 token limit, $0.0001/1K tokens, 1536 dimensions"
    confidence: 0.8
  - step: 2
```
WHY THIS IS GOLDEN:
- filename follows `p03_rt_{agent}_{timestamp}.yaml`
- all required fields present: agent, intent, steps, conclusion, confidence, timestamp
- each step has thought + concrete evidence + calibrated confidence
- alternatives_rejected has evidence-based rejection reasons
## Golden Low-Confidence Example
OUTPUT (`p03_rt_build_sat_20260406T160000.yaml`):
```yaml
agent: build-sat
intent: determine if kc_toolkit.md needs restructuring
steps:
  - step: 1
    thought: Current KC has 3 sections but toolkit kind has expanded to cover MCP mapping
    evidence: "kc_toolkit.md last updated 2026-02-15; toolkit-builder added MCP fields 2026-03-20"
    confidence: 0.7
  - step: 2
```
WHY THIS PASSES:
- low confidence (0.46) correctly reflects weak evidence at step 2
- conclusion honestly states insufficient evidence
- step 2 confidence capped at 0.3 due to absence-of-evidence reasoning
- would trigger memory feedback loop (confidence < 0.5)
## Anti-Example
BAD OUTPUT (`p03_rt_agent.md`):
```markdown
# Reasoning Trace
The agent decided to use ada-002 because it's a good model.
We considered other options but ada-002 seemed best.
Confidence: high.
```
FAILURES:
1. wrong format: markdown prose instead of structured YAML
2. wrong extension: `.md` instead of `.yaml`
3. no `agent` field — who reasoned?
4. no `steps` list — no chain-of-thought structure
5. no `evidence` — "it's a good model" is assertion, not reasoning
6. confidence is string "high" instead of numeric 0.0-1.0
7. no `alternatives_rejected` — what else was considered?
8. no `timestamp` — when was this decided?
9. no concrete data -- unauditable

### S_RELATED
-0.3 if `related:` < 3 or body lacks Related Artifacts

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p03_ins_reasoning_trace_builder]] | upstream | 0.57 |
| [[bld_knowledge_card_reasoning_trace]] | upstream | 0.54 |
| [[bld_schema_reasoning_trace]] | upstream | 0.51 |
| [[reasoning-trace-builder]] | upstream | 0.46 |
| [[bld_memory_reasoning_trace]] | upstream | 0.43 |
