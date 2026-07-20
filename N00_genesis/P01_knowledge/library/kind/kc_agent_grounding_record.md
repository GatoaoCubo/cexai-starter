---
id: kc_agent_grounding_record
kind: knowledge_card
8f: F3_inject
title: Agent Grounding Record
version: 1.0.0
quality: null
pillar: P01
tldr: "Structured provenance record of tool calls, RAG chunks, model version, and output hash per inference"
when_to_use: "When you need reproducibility, auditability, or regulatory traceability for agent outputs"
keywords: [tool calls, retrieval augmented generation, model signature, output hash, traceability, otel, c2pa, inference execution, artifact versioning, lineage tracking]
density_score: 0.92
related:
  - bld_manifest_agent_grounding_record
  - bld_instruction_agent_grounding_record
  - bld_knowledge_card_agent_grounding_record
  - bld_collaboration_agent_grounding_record
  - bld_memory_agent_grounding_record
---

# Agent Grounding Record

A structured provenance record for each inference execution, containing:

1. **Tool Calls** - Full execution history of invoked tools (including parameters)
2. **RAG Chunks** - Contextual documents used for retrieval-augmented generation
3. **Model Signature** - Exact model version and configuration used
4. **Output Hash** - Cryptographic hash of the final output artifact
5. **Traceability** - OTel/C2PA headers for end-to-end auditability

This record enables:
- Reproducibility of inference results
- Debugging of decision-making processes
- Compliance with regulatory traceability requirements
- Artifact versioning and lineage tracking

The record is automatically generated for every inference operation and stored in the `.cex/grounding` directory with a timestamp-based filename.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_manifest_agent_grounding_record]] | downstream | 0.33 |
| [[bld_instruction_agent_grounding_record]] | downstream | 0.30 |
| [[bld_knowledge_card_agent_grounding_record]] | sibling | 0.28 |
| [[bld_collaboration_agent_grounding_record]] | downstream | 0.26 |
| [[bld_memory_agent_grounding_record]] | downstream | 0.23 |
