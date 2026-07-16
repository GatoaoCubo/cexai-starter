---
kind: learning_record
id: p10_lr_c2pa_manifest_builder
pillar: P10
llm_function: INJECT
purpose: Learned patterns and pitfalls for c2pa_manifest construction
quality: null
title: "Learning Record C2PA Manifest"
version: "1.0.0"
author: n04_wave7
tags: [c2pa_manifest, builder, learning_record, C2PA, content-credential, AI-ML-generator, Adobe, provenance]
tldr: "Learned patterns and pitfalls for c2pa_manifest construction"
domain: "c2pa_manifest construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F7_govern"
keywords: [pa_manifest construction, learning record c, pa manifest, c2pa_manifest, builder, learning_record, c2pa, content-credential, ai-ml-generator, adobe]
density_score: 0.85
related:
  - bld_knowledge_card_c2pa_manifest
  - c2pa-manifest-builder
  - bld_tools_c2pa_manifest
  - bld_instruction_c2pa_manifest
  - p10_qg_c2pa_manifest
---
## Observation
C2PA 2.2+ introduced explicit AI-ML generator guidance that was absent in 1.x. Teams using earlier spec versions omit the c2pa.ai_generator assertion entirely, producing manifests that lack attribution for AI-generated content. Adobe Firefly, Nikon, and Microsoft all use C2PA 2.3 natively; artifacts built for these platforms must conform to 2.3.

## Pattern
Always include c2pa.ai_generator assertion with digitalSourceType for AI-generated content. Use IANA MIME types (image/jpeg, not jpg). Embed manifest BEFORE final compression to prevent hash invalidation.

## Evidence
C2PA 2.3 spec released 2025. Adobe Firefly native integration confirmed. CAI verification portal (verify.contentauthenticity.org) validates live manifests. C2PA 2.4 adds AI watermarking hooks (announced 2025).

## Recommendations
- Include c2pa.ai_generator assertion for ALL AI-generated content (required by C2PA 2.2+).
- Use trainedAlgorithmicMedia for pure AI generation; compositeSynthetic for AI-composited media.
- Always include ingredient content hashes to enable provenance chain verification.
- Embed manifest before JPEG compression (hash must match final bytes).
- Reference c2pa-rs SDK (Rust, open source) or CAI SDK (JavaScript) for signing implementation.
- Test manifests at verify.contentauthenticity.org before deployment.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_card_c2pa_manifest]] | upstream | 0.63 |
| [[c2pa-manifest-builder]] | related | 0.61 |
| [[bld_tools_c2pa_manifest]] | upstream | 0.59 |
| [[bld_instruction_c2pa_manifest]] | upstream | 0.50 |
| [[p10_qg_c2pa_manifest]] | downstream | 0.49 |
