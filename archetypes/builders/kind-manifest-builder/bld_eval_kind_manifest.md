---
kind: quality_gate
id: p11_qg_kind_manifest
pillar: P11
llm_function: GOVERN
purpose: "Golden and anti-examples of kind_manifest artifacts"
pattern: "few-shot learning -- LLM reads these before producing"
quality: null
title: "Gate: Kind Manifest"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, kind-manifest, per-kind-identity, r-310, n00-genesis]
tldr: "Gates ensuring kind_manifest artifacts keep the fixed filename/id/pillar axes intact, never fabricate a builder pointer, and mirror the documented kind's real fields."
domain: "kind_manifest -- per-kind identity document, F3 INJECT reference"
created: "2026-07-10"
updated: "2026-07-10"
8f: "F7_govern"
keywords: [per kind identity, kind manifest, quality-gate, kind-manifest, r-310, canonical id pattern]
density_score: 0.87
related:
  - bld_schema_kind_manifest
---
## Quality Gate

# Gate: Kind Manifest
## Definition
| Field     | Value |
|-----------|-------|
| metric    | weighted soft score + all hard gates pass |
| threshold | 7.0 to publish; 8.0 for pool; 9.5 for golden |
| operator  | AND (all hard) + weighted average (soft) |
| scope     | any artifact with `kind: kind_manifest` |
## HARD Gates
All must pass. Any failure = immediate reject.
| ID  | Check | Fail Condition |
|-----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | Parse error on any field |
| H02 | ID matches `^n00_[a-z][a-z0-9_]+_manifest$` | Any other shape -- 294/294 real instances comply, zero exceptions |
| H03 | kind equals literal `kind_manifest` | Any other kind value (294/294 carried `knowledge_card` until R-310 fixed all in one pass) |
| H04 | `8f` equals `F3_inject`, `nucleus` equals `n00` | Either drifts from these fixed values |
| H05 | Quality field is `null` | Any non-null value |
| H06 | `depends_on` equals `[]` | Any populated dependency list |
| H07 | Filename equals `kind_manifest_n00.md`; directory is `kind_{{kind}}/` | Renamed filename or relocated directory |
## SOFT Scoring
Total weights sum to 100%.
| ID  | Dimension | Weight | 10 pts | 5 pts | 0 pts |
|-----|-----------|--------|--------|-------|-------|
| S01 | 10-section completeness | 1.0 | All 10 body sections present, in order | 1-2 merged or reordered | Missing sections |
| S02 | Builder-pointer honesty | 1.0 | Real path cited, OR an explicit "OPEN (register row R-XXX)" callout | Path cited but not verified | Fabricated path to a builder that does not exist |
| S03 | depends_on discipline | 0.5 | `[]`, unmodified | -- | Populated without a kinds_meta.json edit |
| S04 | Schema-table fidelity | 1.0 | Every field traces to the DOCUMENTED kind's own real schema | Mostly traced, 1-2 gaps | Invented fields with no source |
| S05 | Corpus-statistic freshness | 0.5 | Any cited count (e.g. instance total) verified by a fresh read, not copied from a stale source | Verified but not disclosed as such | Stale number presented as current |
| S06 | Examples + Related Artifacts | 1.0 | A minimal real-shaped example + Related Artifacts resolving to REAL artifacts | One present | No example; fabricated wikilinks |
**Score = sum(pts * weight) / sum(max_pts * weight) * 10**
## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | Golden | Publish to pool as golden kind_manifest contract |
| >= 8.0 | Skilled | Publish to pool + log pattern |
| >= 7.0 | Learning | Use but flag for improvement |
| < 7.0 | Rejected | Return to author with gate report |
## Bypass
| Field | Value |
|-------|-------|
| Conditions | The documented kind is itself mid-design and its own schema is not yet stable |
| Approver | Owner agent lead |
| Audit trail | `bypass_reason` + `draft: true` both required in frontmatter |
| Expiry | Draft status expires after 14 days; must reach H-gate compliance or be deprecated |

## Examples

# Examples: kind-manifest-builder
## Golden Example -- Builder Pointer Real
INPUT: "Document the newly-registered kind `sourcing_lead`, which already has a builder"
OUTPUT (frontmatter only, body omitted for length):
```yaml
id: n00_sourcing_lead_manifest
kind: kind_manifest
8f: F3_inject
pillar: P06
nucleus: n00
title: "Sourcing Lead -- Canonical Manifest"
version: 1.0
quality: null
tags: [manifest, sourcing_lead, p06, n00, archetype, template]
density_score: 1.0
```
WHY THIS IS GOLDEN:
- id matches `^n00_[a-z][a-z0-9_]+_manifest$` (H02 pass)
- kind/8f/nucleus fixed values correct (H03/H04 pass); quality: null (H05 pass)
- Builder section cites the real `archetypes/builders/sourcing-lead-builder/` path (S02 = 10pts)

## Anti-Example -- Fabricated Builder Pointer (REJECTED)
INPUT: "Document kind `X`, which has no builder yet"
BAD OUTPUT: a `## Builder` section citing `archetypes/builders/x-builder/` as if it existed, with no verification.
WHY THIS FAILS: S02 = 0pts -- this is exactly the "fabricated pointer" failure this gate exists to catch; the correct move is the honest OPEN-status callout.

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream/sibling reference
- Penalty: -0.3 if empty (does not block, encourages wiring)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_kind_manifest]] | sibling | 0.42 |
