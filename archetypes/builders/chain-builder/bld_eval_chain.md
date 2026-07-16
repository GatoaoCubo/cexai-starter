---
kind: quality_gate
id: p11_qg_chain
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of chain artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: chain"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, chain, P03, prompt-pipeline, sequential, data-flow]
tldr: "Pass/fail gate for chain artifacts: step atomicity, typed data flow, error handling strategy, and pipeline completeness."
domain: "prompt pipeline design — sequential LLM call chains with typed data flow between steps"
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
keywords: [prompt pipeline design, step atomicity, typed data flow, error handling strategy, and pipeline completeness, quality-gate, chain]
density_score: 0.91
related:
  - p10_lr_chain_builder
  - bld_architecture_chain
  - p01_kc_chain
  - chain-builder
  - bld_instruction_chain
---
## Quality Gate

# Gate: chain
## Definition
| Field | Value |
|---|---|
| metric | chain artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: chain` |
## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^[a-z][a-z0-9_-]+$` | ID contains uppercase, spaces, or invalid chars |
| H03 | ID equals filename stem | `id: my_chain` but file is `other_chain.md` |
| H04 | Kind equals literal `chain` | `kind: workflow` or `kind: pipeline` or any other value |
| H05 | Quality field is null | `quality: 8.0` or any non-null value |
| H06 | All required fields present | Missing `steps`, `input_schema`, or `output_schema` |
## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Step atomicity | 1.0 | Each step is one LLM call; no compound logic bundled in a single step |
| Data flow explicitness | 1.0 | Each step declares which prior step's output it consumes |
| Type coverage | 1.0 | All input/output types are concrete (string, number, list[string], not `any`) |
| Error handling granularity | 1.0 | Error strategy defined per-step or with justified global default |
| Context passing efficiency | 0.5 | Passes only required fields to each step, not entire prior context |
| Step naming clarity | 0.5 | Step names describe the LLM task (extract_entities not step_2) |
## Actions
| Score | Tier | Action |
|---|---|---|
| >= 9.5 | Golden | Publish to pool as golden reference |
| >= 8.0 | Publish | Publish to pool, add to routing index |
| >= 7.0 | Review | Flag for improvement before publish |
| < 7.0 | Reject | Return to author with specific gate failures |
## Bypass
| Field | Value |
|---|---|
| conditions | Proof-of-concept chain during active research spike, not intended for production use |
| approver | Lead author acknowledgment in artifact comment block |
| audit_trail | Bypass reason and spike ticket ID recorded in frontmatter comment |
| expiry | 48h — spike chains must either reach >= 7.0 or be deleted |
| never_bypass | H01 (unparseable YAML breaks all tooling), H05 (self-scored gates corrupt quality metrics) |

## Examples

# Examples: chain-builder
## Golden Example
INPUT: "Create a prompt chain for research-to-knowledge-card pipeline"
OUTPUT:
```yaml
id: p03_ch_research_to_kc
kind: chain
pillar: P03
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder_agent"
title: "Research to Knowledge Card Pipeline"
steps_count: 3
flow: sequential
input_format: "topic name + domain string"
output_format: "knowledge_card markdown artifact"
context_passing: filtered
error_strategy: fail_fast
domain: "knowledge"
quality: null
tags: [chain, knowledge, research, distillation]
tldr: "3-step chain: gather sources, extract facts, compose KC with density >= 0.80"
density_score: 0.88
```
## Purpose
Transforms a raw topic into a production-ready knowledge_card by chaining three
prompt steps: source gathering, fact extraction, and KC composition. Each step
narrows scope — from broad research to atomic distilled facts.
## Steps
### Step 1: Gather Sources
- **Input**: topic name (string), domain (string)
- **Prompt**: Search for authoritative sources on `{{topic}}` in `{{domain}}`. Return 3-5 URLs with one-line summaries.
- **Output**: list of {url, summary} objects (JSON)
### Step 2: Extract Facts
- **Input**: list of {url, summary} from Step 1
- **Prompt**: For each source, extract 5-10 atomic facts as bullets <= 80 chars. Remove opinions and filler.
- **Output**: deduplicated fact list (markdown bullets)
### Step 3: Compose KC
- **Input**: fact list from Step 2, original topic/domain
- **Prompt**: Compose a knowledge_card following P01 schema. Fill all required fields. density >= 0.80.
- **Output**: complete knowledge_card artifact (YAML frontmatter + markdown body)
## Data Flow
```text
[topic, domain] --string--> Gather --JSON--> Extract --bullets--> Compose --KC.md-->
```
Context passing: filtered — each step receives only its direct input, not full history.
## Error Handling
- **Strategy**: fail_fast
- **On failure at step N**: halt chain, return partial output with error context
- **Retry policy**: none (source quality issues require human intervention)
## Anti-Example
INPUT: "Create a chain for content processing"
BAD OUTPUT:
```yaml
id: content_chain
kind: prompt
pillar: prompt
title: Content Chain
steps_count: 5
quality: 9.0
tags: [content]
```
This chain processes content through multiple steps. First, we gather the content.
Then we process it. Finally, we output the result.

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
