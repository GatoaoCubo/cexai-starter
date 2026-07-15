---
kind: quality_gate
id: p11_qg_openapi_spec
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of openapi_spec artifacts
pattern: few-shot learning -- LLM reads these before producing
quality: null
title: "Gate: openapi_spec"
version: "1.0.0"
author: "builder_agent"
tags:
  - "quality-gate"
  - "openapi-spec"
  - "P06"
  - "oas3"
  - "api-contract"
tldr: "Pass/fail gate for openapi_spec artifacts: id pattern, oas_version, servers, paths, security scheme, error responses."
domain: "openapi spec -- machine-readable OAS 3.x API contract"
created: "2026-04-17"
updated: "2026-04-17"
8f: "F7_govern"
keywords:
  - "x api contract"
  - "id pattern"
  - "security scheme"
  - "error responses"
  - "quality-gate"
  - "openapi-spec"
  - "oas3"
density_score: 0.90
related:
  - bld_instruction_openapi_spec
  - p11_qg_quality_gate
  - p11_qg_cli_tool
  - p11_qg_kind_builder
  - p11_qg_enum_def
---
## Quality Gate
# Gate: openapi_spec
## Definition
| Field | Value |
|---|---|
| metric | openapi_spec artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: openapi_spec` |
## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^p06_oas_[a-z][a-z0-9_]+$` | ID contains uppercase, hyphens, or missing prefix |
| H03 | ID equals filename stem | id: p06_oas_foo but file is p06_oas_bar.md |
| H04 | Kind equals literal `openapi_spec` | kind: api_spec or any other value |
| H05 | Quality field is null | quality: 8.0 or any non-null value |
| H06 | oas_version present and valid | Missing or value not in ["3.0.3","3.1.0"] |
## SOFT Scoring
| Dimension | Weight | Criteria |
|---|---|---|
| Path completeness | 1.0 | All expected endpoints documented |
| Schema reuse | 1.0 | Shared schemas in components.schemas, not inline duplicated |
| Security scheme | 1.0 | securitySchemes defined and global security set |
| Error coverage | 1.0 | 400/401/404/500 defined for authenticated operations |
| operationId quality | 1.0 | All operations have camelCase operationId |
| Request/response schemas | 1.0 | All bodies have schema definitions |
## Actions
| Score | Tier | Action |
|---|---|---|
| >= 9.5 | Golden | Publish to pool as golden reference |
| >= 8.0 | Publish | Publish to pool, add to routing index |
| >= 7.0 | Review | Flag for improvement before publish |
| < 7.0 | Reject | Return to author with specific gate failures |
## Examples
# Examples: openapi-spec-builder
## Golden Example
INPUT: "Create OpenAPI spec for a User Management API with JWT auth"
WHY THIS IS GOLDEN:
- id matches `^p06_oas_[a-z][a-z0-9_]+$` -- H02 pass
- oas_version declared as 3.1.0 -- H03 pass
- servers array present -- H04 pass
- paths with at least one operation -- H05 pass
```yaml
id: p06_oas_user_management_api
kind: openapi_spec
pillar: P06
version: "1.0.0"
created: "2026-04-17"
updated: "2026-04-17"
author: "builder_agent"
api_name: "User Management API"
```
## OpenAPI Document
```yaml
openapi: "3.1.0"
info:
  title: User Management API
  version: "1.0.0"
  description: CRUD operations for user lifecycle management
servers:
  - url: https://api.example.com/v1
    description: Production
```
## Security
JWT bearer authentication. Declare `Authorization: Bearer <token>` on all requests.
Security override per-operation: `security: []` for public endpoints (e.g. /health).
## Error Responses
| Code | Meaning | Schema |
|------|---------|--------|
| 400 | Validation error | ErrorResponse |
| 401 | Missing/invalid JWT | ErrorResponse |
| 404 | Resource not found | ErrorResponse |
| 500 | Internal server error | ErrorResponse |
---

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
