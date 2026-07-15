"""CEXAI governance EXCHANGE lane -- the signed, license-bearing, multi-component
exchange unit (the "X" in CEX). CONVERGENCE T7, checkpoint C5.

This is a NEW governance subpackage, a SIBLING of ``cexai.governance.rbac`` rather
than a member of it. The distinction is deliberate and load-bearing:

  * ``rbac`` is the TRUST FOUNDATION (CONVERGENCE T8): identity (C1
    principal_signing), per-tenant keys + the inference deny-surface (C2),
    the signed-model allow-list (C3), and the tamper-evident transparency log +
    StatusList2021 revocation (C4). It answers "who may act, and is this artifact
    authentic / un-revoked".
  * ``exchange`` is the EXCHANGE AXIS (CONVERGENCE T7). It answers "what travels
    between sovereign instances, and how does a RECEIVER verify it without trusting
    the sender". It does NOT re-implement crypto -- it COMPOSES the rbac primitives
    (C1's Ed25519 key + did:key, C4's MerkleLog + StatusList) into a DSSE-style
    envelope that wraps an exchangeable asset's Bill of Materials.

Design source: N04_knowledge/P08_architecture/p08_adr_knowledge_bom_exchange_unit.md
(T7 design) + N07_admin/P08_architecture/p08_adr_convergence_master.md (Section 6
council corrections + Section 9.2 open questions).

What lives here (v1): ``knowledge_bom`` -- the functional envelope. This subpackage
registers ZERO taxonomy kinds and does NOT touch ``.cex/kinds_meta.json`` (a
knowledge_bom kind registration is a separately-gated step). It is the WORKING
module + tests only.

ASCII-only per .claude/rules/ascii-code-rule.md.

absorbs: convergence/t7-knowledge-bom (checkpoint C5 -- the exchange unit)
"""

from __future__ import annotations

__all__: list = []
