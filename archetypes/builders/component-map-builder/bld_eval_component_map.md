---
pillar: P11
id: p11_qg_component_map
kind: quality_gate
parent: component-map-builder
version: "1.0.0"
quality: null
title: "Gate: component_map"
author: "builder_agent"
tags: [quality-gate, component-map, P08, inventory, architecture, dependency-mapping]
tldr: "Pass/fail gate for component_map artifacts: component completeness, connection accuracy, interface boundary documentation, and inventory scope."
domain: "system component inventory — structured catalogs of components, connections, dependencies, and data flows"
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
density_score: 0.90
llm_function: GOVERN
related:
  - bld_instruction_component_map
  - p11_qg_instruction
  - p11_qg_diagram
  - p11_qg_knowledge_index
  - p11_qg_quality_gate
---
## Quality Gate

# Gate: component_map
## Definition
| Field | Value |
|---|---|
| metric | component_map artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: component_map` |
## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^[a-z][a-z0-9_-]+$` | ID contains uppercase, spaces, or invalid chars |
| H03 | ID equals filename stem | `id: my_map` but file is `other_map.md` |
| H04 | Kind equals literal `component_map` | `kind: diagram` or `kind: architecture` or any other value |
| H05 | Quality field is null | `quality: 8.5` or any non-null value |
| H06 | All required fields present | Missing `components`, `connections`, or `scope` |
## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Component completeness | 1.0 | All components within the declared scope boundary are inventoried |
| Connection accuracy | 1.0 | Connections reflect actual data or control flow; direction (A->B vs B->A) correct |
| Interface boundary clarity | 1.0 | Each component's public interface (API surface, events, data contracts) documented |
| Dependency direction | 1.0 | Dependency edges are directional and semanticslly labeled (calls, subscribes, reads) |
| Ownership documentation | 0.5 | Each component has an owner (team, service, person) assigned |
| Health status inclusion | 0.5 | Component health or operational status noted where known |
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
| conditions | Map created during active system migration where component inventory is in flux |
| approver | Architecture owner acknowledgment with migration ticket reference |
| audit_trail | Bypass reason, migration ticket ID, and expected stable date in frontmatter comment |
| expiry | 21d — map must reach >= 7.0 or be updated once migration phase complete |
| never_bypass | H01 (unparseable YAML breaks all tooling), H05 (self-scored gates corrupt quality metrics) |

## Examples

# Examples — component-map-builder
## Golden Example
INPUT: "Map the CEX brain infrastructure components and connections"
OUTPUT (complete, 19+ fields):
```yaml
id: p08_cmap_brain_infrastructure
kind: component_map
pillar: P08
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder"
domain: "infrastructure"
quality: null
tags: [component-map, brain, infrastructure, search, knowledge]
tldr: "Structured inventory of Brain search infrastructure: BM25, FAISS, Ollama, and 1957 pool artifacts"
scope: "CEX Brain search infrastructure — indexing, embedding, retrieval"
component_count: 6
connection_count: 8
components:
  - {name: "BM25 Index", role: "keyword search", owner: "knowledge-engine", status: "active"}
  - {name: "FAISS Index", role: "vector similarity search", owner: "knowledge-engine", status: "active"}
  - {name: "Ollama", role: "local embedding generation", owner: "system", status: "active"}
  - {name: "Pool", role: "artifact storage (1957 items)", owner: "system", status: "active"}
connections:
  - {from: "Pool", to: "build_indexes_ollama.py", type: "data_flow"}
  - {from: "build_indexes_ollama.py", to: "BM25 Index", type: "produces"}
  - {from: "build_indexes_ollama.py", to: "FAISS Index", type: "produces"}
  - {from: "Ollama", to: "build_indexes_ollama.py", type: "dependency"}
keywords: [brain, search, bm25, faiss, ollama, knowledge, retrieval]
## Scope
CEX Brain search infrastructure: all components involved in indexing, embedding, and retrieving knowledge artifacts. Excludes individual artifact content, agent_group internals, and API deployment.
## Components
| Component | Role | Owner | Status | Version |
|-----------|------|-------|--------|---------|
| BM25 Index | Keyword search (lexical) | knowledge-engine | active | - |
| FAISS Index | Vector similarity (semantic) | knowledge-engine | active | 140MB gitignored |
| Ollama | Local embedding (nomic-embed-text) | system | active | auto-start |
| Pool | Artifact storage | system | active | 1957 items |
| brain_query API | Hybrid search endpoint | knowledge-engine | active | ~88% accuracy |
| build_indexes_ollama.py | Index rebuilder | knowledge-engine | active | ~20 min full rebuild |

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
