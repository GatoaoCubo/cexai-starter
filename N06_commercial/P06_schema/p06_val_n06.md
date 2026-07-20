---
id: p06_val_n06
kind: validator
pillar: P06
nucleus: n06
title: Revenue Integrity Validator
version: 1.0.0
quality: null
tags:
  - "schema"
  - "validator"
  - "quality"
  - "pricing"
  - "revenue"
density_score: 1.0
related:
  - p06_td_n06
  - p06_enum_pricing_tiers_n06
  - p07_sr_commercial_n06
updated: "2026-07-20"
---

# Revenue Integrity Validator

## Purpose

| Field | Value |
|-------|-------|
| Goal | Define the pre-commit and quality-gate rule set that blocks commercially weak or structurally unsafe N06 artifacts |
| Business Lens | Strategic Greed tolerates aggressive monetization, but never sloppy accounting, hidden leakage, or vague offer logic |
| Primary Use | Validate schema and config artifacts before they influence pricing, funnel, or billing behavior |
| Failure Prevented | broken pricing assumptions, fake revenue metrics, under-protected premium flows, low-density boilerplate |
| Trigger | pre-commit, review gate, compile-time audit |
| Outcome | pass, warn, or block with corrective action |

## Schema

| Property | Type | Required | Constraint | Commercial Intent |
|----------|------|----------|------------|-------------------|
| validator_name | string | yes | `revenue_integrity_validator` | stable reference |
| scope | string | yes | `N06_commercial/{schemas,config}` | bounded enforcement |
| rule_type | string | yes | structural plus semantic | catches both form and business weakness |
| severity | string | yes | `error` default | poor monetization contracts must block |
| on_fail | string | yes | `block` | prevents bad config from shipping |
| checks | array | yes | 9 named checks | one validator, many atomic checks |
| bypass_policy | table | yes | explicit approver path | no silent bypass for commercial gates |
| evidence | table | yes | file,line,reason | auditability for review |

## Checks

| Check ID | Condition | Pass Rule | On Fail | Strategic Greed Reason |
|----------|-----------|-----------|---------|------------------------|
| RV01 | frontmatter completeness | required keys present and `quality: null` | block | prevents governance drift |
| RV02 | section completeness | Purpose, Schema or Values, Rationale, Example exist | block | forces usable commercial docs |
| RV03 | line density | file has >= 80 lines and table-heavy structure | block | rejects lazy filler that hides weak thinking |
| RV04 | ASCII discipline | identifiers and code blocks remain ASCII-only | block | avoids runtime and parsing risk |
| RV05 | monetization specificity | each artifact names pricing, revenue, funnel, margin, retention, or upsell logic | block | generic config is commercially useless |
| RV06 | enum and type consistency | references match declared N06 artifacts | block | avoids broken joins across pricing systems |
| RV07 | value realism | money, limits, and paths cannot be null without rationale | warn | greed needs explicit constraints |
| RV08 | premium defense | enterprise, scale, paid, or secret flows cannot use wildcard access or unlimited defaults | block | premium surfaces deserve tighter controls |
| RV09 | example validity | example must align with artifact rules | block | documentation must be executable in spirit |

## Evaluation Order

| Step | Check Group | Reason |
|------|-------------|--------|
| 1 | RV01 and RV02 | stop immediately if structure is broken |
| 2 | RV03 and RV04 | prevent low-quality or unsafe syntax from continuing |
| 3 | RV05 and RV06 | verify commercial meaning and cross-artifact integrity |
| 4 | RV07 to RV09 | catch realism, premium defense, and example accuracy |

## Bypass Policy

| Field | Rule |
|-------|------|
| Allowed Bypass | no for pre-commit, yes for emergency hotfix review only |
| Approver | orchestrator plus N06 owner together |
| Evidence Required | incident id, rollback plan, revenue impact estimate |
| Time Limit | 24 hours before full fix |
| Audit Record | mandatory in review note |

## Rationale

| Design Choice | Why It Exists | Strategic Greed Impact |
|---------------|---------------|------------------------|
| Error-first severity | Weak commercial contracts are expensive | blocks revenue mistakes early |
| Density check | Short fluffy docs hide missing constraints | pushes artifacts toward actionability |
| Premium defense rule | High-value accounts deserve stronger rules | protects enterprise margin |
| Example validity | teams copy examples into implementation | reduces monetization misfires |
| Realism warning | some values may vary by environment | still forces declared intent |
| No silent bypass | greed likes speed, but only with traceable risk | keeps aggressive execution auditable |

## Example

| File | Result | Reason |
|------|--------|--------|
| `p06_td_n06.md` | pass | has required sections, clear revenue fields, valid example |
| `p09_rl_n06.md` | pass | scoped profiles and budget rules protect premium resources |
| `draft_config.md` | block | missing rationale section and uses wildcard permissions |

```yaml
validator_name: revenue_integrity_validator
scope:
  - N06_commercial/schemas
  - N06_commercial/config
severity: error
on_fail: block
checks:
  - RV01
  - RV02
  - RV03
  - RV04
  - RV05
  - RV06
  - RV07
  - RV08
  - RV09
```

## Related Artifacts
| Artifact | Relationship |
|----------|-------------|
| [[p06_td_n06]] | sibling (this validator enforces that type's field rules) |
| [[p06_enum_pricing_tiers_n06]] | sibling (RV06 checks against this enum) |
| [[p07_sr_commercial_n06]] | related (scoring rubric is the human-facing counterpart of this gate) |
