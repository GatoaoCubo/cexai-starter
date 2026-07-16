---
kind: schema
id: bld_schema_vc_credential
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema -- SINGLE SOURCE OF TRUTH for vc_credential
quality: null
title: "Schema VC Credential"
version: "1.0.0"
author: n04_wave7
tags: [vc_credential, builder, schema, w3c, vc-2.0, did]
tldr: "Formal schema -- SINGLE SOURCE OF TRUTH for vc_credential"
domain: "vc_credential construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [vc_credential construction, schema vc credential, vc_credential, builder, schema, vc-2, frontmatter fields, body structure, credential document, credential subject claims]
density_score: 0.85
related:
  - bld_schema_usage_report
  - bld_schema_pitch_deck
  - bld_schema_dataset_card
  - bld_schema_quickstart_guide
  - bld_schema_api_reference
---

## Frontmatter Fields
### Required
| Field            | Type   | Required | Default | Notes |
|------------------|--------|----------|---------|-------|
| id               | string | yes      |         | IRI format: https://issuer/credentials/uuid |
| kind             | string | yes      |         | Must be "vc_credential" |
| pillar           | string | yes      |         | P10 |
| title            | string | yes      |         | Human-readable credential name |
| version          | string | yes      |         | Semantic version |
| created          | date   | yes      |         | ISO 8601 date |
| updated          | date   | yes      |         | ISO 8601 date |
| author           | string | yes      |         | Issuing nucleus or agent |
| domain           | string | yes      |         | Credential domain (agent-identity, provenance, compliance) |
| quality          | null   | yes      | null    | Never self-score; peer review assigns |
| tags             | array  | yes      |         | Must include: W3C, verifiable-credential, DID |
| tldr             | string | yes      |         | One-line credential purpose |
| issuer_did       | string | yes      |         | DID of credential issuer |
| subject_did      | string | yes      |         | DID of credential subject |
| credential_type  | string | yes      |         | Domain type (AgentIdentityCredential, ProvenanceCredential) |
| valid_from       | string | yes      |         | ISO 8601 datetime |
| cryptosuite      | string | yes      |         | ecdsa-rdfc-2022 or eddsa-rdfc-2022 |

### Recommended
| Field             | Type   | Notes |
|-------------------|--------|-------|
| valid_until       | string | ISO 8601 expiry |
| credential_schema | string | Schema registry IRI |
| status_list_url   | string | StatusList2021 endpoint |
| refresh_service   | string | Auto-renewal endpoint |

## ID Pattern
^p10_vc_[a-z][a-z0-9_]+\.md$

## Body Structure
1. **Credential Document** - Full W3C VC 2.0 JSON-LD document
2. **Credential Subject Claims** - Attested attributes with claim definitions
3. **Proof Block** - Data integrity proof with cryptosuite and proofValue
4. **Status & Refresh** - credentialStatus + refreshService endpoints
5. **Usage Context** - When/why this credential is presented and verified
6. **Verification Guide** - How verifiers resolve DID and check proof

## Constraints
- All required fields must be present and valid.
- id must match the regex pattern exactly.
- issuer_did must be a valid DID (did: prefix).
- cryptosuite must be ecdsa-rdfc-2022 or eddsa-rdfc-2022.
- credential_type must be a recognized VC 2.0 type string.
- valid_from must precede valid_until if both are present.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_usage_report]] | sibling | 0.64 |
| [[bld_schema_pitch_deck]] | sibling | 0.62 |
| [[bld_schema_dataset_card]] | sibling | 0.61 |
| [[bld_schema_quickstart_guide]] | sibling | 0.61 |
| [[bld_schema_api_reference]] | sibling | 0.60 |
