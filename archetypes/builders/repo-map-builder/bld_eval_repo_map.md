---
kind: quality_gate
id: p01_qg_repo_map
pillar: P11
llm_function: GOVERN
purpose: Quality gate with HARD and SOFT scoring for repo_map
quality: null
title: "Quality Gate Repo Map"
version: "1.0.0"
author: wave1_builder_gen
tags:
  - "repo_map"
  - "builder"
  - "quality_gate"
tldr: "Quality gate with HARD and SOFT scoring for repo_map"
domain: "repo_map construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F7_govern"
keywords:
  - "repo_map construction"
  - "quality gate repo map"
  - "repo_map"
  - "builder"
  - "quality_gate"
  - "^p01_rm_[a-za-z0-9_]+$"
  - "token_budget"
density_score: 0.85
related:
  - spec_05_skills_runtime
  - bld_instruction_repo_map
  - bld_knowledge_card_repo_map
  - bld_output_template_repo_map
  - p01_kc_pydantic_patterns
---
## Quality Gate
## Definition  
| metric | threshold | operator | scope |  
|---|---|---|---|  
| Repo Map Completeness | 90% | ≥ | All repositories |  
## HARD Gates  
| ID | Check | Fail Condition |  
|---|---|---|  
| H01 | YAML valid | Invalid YAML syntax |  
| H02 | ID matches pattern | ID does not match `^p01_rm_[a-zA-Z0-9_]+$` (schema pattern) |
| H03 | kind matches | kind != `repo_map` |
| H04 | Token budget defined | Missing `token_budget` field |  
| H05 | Symbol table present | No function/class signatures in body |
| H06 | Token budget defined | Missing token_budget field |
## SOFT Scoring
| Dim | Dimension | Weight | Scoring Guide |
|-----|-----------|--------|---------------|
| D01 | Symbol Extraction | 0.25 | tree-sitter signatures present=1.0; file paths only=0.3 |
| D02 | Token Budget Compliance | 0.20 | tokens_used <= budget=1.0; exceeded=0.0 |
| D03 | PageRank Ranking | 0.20 | scores shown, personalization applied=1.0; no ranking=0.3 |
| D04 | File Selection Heuristics | 0.15 | all 4 rules documented=1.0; none documented=0.4 |
| D05 | Structural Completeness | 0.20 | all template sections present=1.0; missing sections=0.5 |
**Weight sum: 0.25+0.20+0.20+0.15+0.20 = 1.00**  
## Actions  
| Score | Action |  
|---|---|  
| ≥9.5 | GOLDEN: Auto-approve and promote |  
| ≥8.0 | PUBLISH: Merge and notify stakeholders |  
| ≥7.0 | REVIEW: Flag for manual inspection |  
| <7.0 | REJECT: Block and require fixes |  
## Bypass  
| conditions | approver | audit trail |  
|---|---|---|  
| Critical bug fix | Lead Architect | Change request #12345 |  
| Legacy system migration | CTO | Emergency ticket #67890 |  
| External dependency update | DevOps Manager | Dependency ticket #54321 |
## Examples
## Golden Example: Aider-Style Repo Map (Symbol Table + PageRank)
```markdown
---
id: p01_rm_cex_sdk
kind: repo_map
pillar: P01
title: "CEX SDK -- Repository Context Map"
version: "1.0.0"
token_budget: 1024
symbol_count: 847
file_count: 18
extraction_method: tree-sitter
---
## File Ranking (PageRank, alpha=0.85)
| Rank | File | Score | Tokens | Reason |
|------|------|-------|--------|--------|
| 1 | cex_sdk/cex_8f_motor.py | 0.142 | 87 | 12 files import this |
| 2 | cex_sdk/cex_compile.py | 0.098 | 64 | Entry point; high in-degree |
| 3 | cex_sdk/cex_score.py | 0.087 | 71 | Referenced in 9 builder ISOs |
## Symbol Table (tree-sitter extracted)
cex_sdk/cex_8f_motor.py:
  class EightFMotor:
    def run(self, intent: str, nucleus: str) -> dict
    def classify_intent(self, text: str) -> str
    def fan_out(self, plan: list) -> list
  def parse_intent(raw: str) -> Intent
cex_sdk/cex_compile.py:
  def compile_artifact(path: str) -> dict
  def compile_all(pillar: str) -> list
  class CompileError(Exception):
cex_sdk/cex_score.py:
  class HybridScorer:
    def score(self, artifact: dict) -> float
    def apply_score(self, path: str, score: float) -> None
Token budget used: 987 / 1024 (96%)
```
**Why it passes:** Contains ranked symbol table (not file tree). tree-sitter extracted
specific function signatures. PageRank scores shown. Token budget tracked. 18 files fit
in 1024 token budget via PageRank pruning.
---
## Golden Example 2: repo_map for Microservices (with Reference Graph)
```markdown
---
id: p01_rm_microservices_demo
kind: repo_map
pillar: P01
title: "Microservices Demo -- Repo Context Map"
token_budget: 2048
file_count: 23
extraction_method: tree-sitter
---
## Symbol Table
api/auth_service.py:
  class AuthService:
    def authenticate(self, token: str) -> User
    def refresh(self, refresh_token: str) -> dict
  def verify_jwt(token: str) -> Claims
api/data_service.py:
  class DataService:
    def query(self, sql: str, params: dict) -> list
    def cache_get(self, key: str) -> Optional[bytes]
services/event_bus.py:
  class EventBus:
    def publish(self, topic: str, message: dict) -> None
    def subscribe(self, topic: str, handler: Callable) -> None
## Reference Graph (top connections)
auth_service -> [data_service (2), event_bus (1)]
data_service -> [event_bus (3)]
event_bus -> []  # sink node
```
---
## Anti-Example 1: Flat File Tree (Wrong -- This Is NOT a Repo Map)
```markdown
## Repository Structure
- api/
  - auth_service.py
  - data_service.py
- services/
```
**Why it fails:** H04 FAIL -- no `token_budget` field. No symbol extraction (just file paths).
No PageRank ranking. No function signatures. This is a directory listing, not a repo map.
An LLM receiving this cannot determine which files are most relevant to the current task.
---
## Anti-Example 2: Token Budget Exceeded
```yaml
---
id: p01_rm_giant_monorepo
kind: repo_map
pillar: P01
token_budget: 1024
file_count: 2847    # FAIL: 2847 files, 1024 token budget -- impossible
---
# [Lists all 2847 files with full signatures -- 48,000 tokens]
```
**Why it fails:** Token budget (1024) vs actual content (48,000 tokens) -- budget not enforced.
The map should use PageRank to select the top ~15-20 most relevant files fitting within 1024 tokens.
Fix: apply PageRank ranking, truncate to budget, include only top-ranked symbols.
---

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
