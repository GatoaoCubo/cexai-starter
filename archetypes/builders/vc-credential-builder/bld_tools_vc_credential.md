---
kind: tools
id: bld_tools_vc_credential
pillar: P04
llm_function: CALL
purpose: Tools available for vc_credential production
quality: null
title: "Tools VC Credential"
version: "1.0.0"
author: n04_wave7
tags: [vc_credential, builder, tools, DID, data-integrity, W3C]
tldr: "Tools available for vc_credential production"
domain: "vc_credential construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [vc_credential construction, tools vc credential, vc_credential, builder, tools, data-integrity, production tools, validation tools, external references, data integrity]
density_score: 0.85
related:
  - vc-credential-builder
  - bld_tools_ontology
---
## Production Tools
| Tool             | Purpose                              | When                         |
|------------------|--------------------------------------|------------------------------|
| cex_compile.py   | Compile VC YAML to JSON-LD           | After draft produced         |
| cex_score.py     | Score VC against quality gates       | Post-production validation   |
| cex_retriever.py | Fetch similar VC examples            | During context assembly      |
| cex_doctor.py    | Validate VC structure and fields     | Pre-commit check             |
| cex_doctor.py | JSON Schema validation of claims     | credentialSchema check       |

## Validation Tools
| Tool               | Purpose                              | When                         |
|--------------------|--------------------------------------|------------------------------|
| did_resolver       | Resolve DID to DID Document          | Issuer/subject DID check     |
| vc_verifier        | Verify data-integrity proof          | Proof validation             |
| status_list_check  | Check credentialStatus revocation    | Before credential presentation|
| jsonld_processor   | Expand/compact JSON-LD document      | Context normalization        |

## External References
- W3C VC 2.0 spec: https://www.w3.org/TR/vc-data-model-2.0/
- W3C Data Integrity: https://www.w3.org/TR/vc-data-integrity/
- StatusList2021: https://www.w3.org/TR/vc-bitstring-status-list/
- DID Core 1.0: https://www.w3.org/TR/did-core/
- ecdsa-rdfc-2022 cryptosuite: https://www.w3.org/TR/vc-di-ecdsa/

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[vc-credential-builder]] | downstream | 0.28 |
| [[bld_tools_ontology]] | sibling | 0.28 |
