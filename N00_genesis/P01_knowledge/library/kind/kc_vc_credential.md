---
id: kc_vc_credential
kind: knowledge_card
8f: F3_inject
title: W3C Verifiable Credential 2.0 for AI Agents
version: 1.0.0
quality: null
pillar: P01
tldr: "W3C Verifiable Credential 2.0 for AI agent identity, provenance, and cross-domain trust"
when_to_use: "When establishing cryptographic proof of agent identity or artifact provenance"
keywords: [verifiable credential, cryptographic proof, identity attestation, provenance tracking, cross-domain trust, policy enforcement, revocation support, data sovereignty]
tags: [verifiable-credential, w3c, identity, provenance, cryptographic-proof, trust, agent]
long_tails:
  - "how do I prove an AI agent's identity with a W3C verifiable credential"
  - "how do issuer, holder, and verifier roles work for agent provenance"
density_score: 0.97
related:
  - bld_knowledge_card_vc_credential
  - bld_collaboration_vc_credential
  - bld_schema_vc_credential
  - vc-credential-builder
---

A W3C Verifiable Credential 2.0 is a decentralized digital identity mechanism that establishes trust through cryptographic proofs. For AI agents, it enables:

1. **Identity attestation** - Cryptographic proof of agent existence and ownership
2. **Provenance tracking** - Immutable record of creation, modification, and validation history
3. **Cross-domain trust** - Interoperable verification across different systems and organizations
4. **Policy enforcement** - Automated validation of credential claims against defined rules
5. **Revocation support** - Mechanisms to invalidate compromised credentials
6. **Privacy preservation** - Fine-grained control over credential disclosure

Key components include:
- Holder: Entity possessing the credential
- Issuer: Entity verifying and issuing the credential
- Verifier: Entity checking the credential's validity
- Claim: Specific assertion about the holder
- Evidence: Cryptographic proof of claim validity

This standard enables secure, tamper-evident interactions between AI agents while maintaining data sovereignty and interoperability across distributed systems.

## How to use
Load this card at F3 INJECT when an agent or artifact must prove who it is or where it came from. Act on it as follows:
- Model the three roles explicitly: issuer signs claims, holder presents them, verifier checks the cryptographic proof.
- Use selective disclosure to reveal only the claims a verifier needs, preserving privacy.
- Always implement revocation so a compromised credential can be invalidated; check revocation status on every verification.
- Pair with `bld_schema_vc_credential` for the claim structure and enforce policy on the credential before trusting the agent.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_card_vc_credential]] | sibling | 0.35 |
| [[bld_collaboration_vc_credential]] | downstream | 0.28 |
| [[bld_schema_vc_credential]] | downstream | 0.26 |
| [[vc-credential-builder]] | downstream | 0.26 |
