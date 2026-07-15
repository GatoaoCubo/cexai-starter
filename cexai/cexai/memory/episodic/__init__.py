"""Episodic subsystem -- capture -> compress -> inject session memory (v0.2-W2).

Implements the ``EpisodicStore`` protocol from ``cexai.memory._shared.types``,
satisfying cexai-specs/07_claude-mem/spec.md US P1 (FR-001..003). Session events
are captured to an append-only, hash-chained log (FR-011 tamper detection);
sessions compress into BOTH structured + narrative outputs (FR-012); relevant
compressed sessions auto-inject within a token budget, emitting nothing when no
candidate clears the similarity floor (FR-003/FR-014). ``forget`` performs
retroactive deletion of a session and its derivatives (FR-015).

Relevance ranking reuses the vector subsystem's ``Embedder`` (W1). The offline
path -- ``DeterministicCompressor`` + ``FakeEmbedder`` -- makes the whole
subsystem testable without a live LLM or embedding model (Article XIV).

Public surface:
  * ``EpisodicMemory`` -- the ``EpisodicStore`` implementation.
  * ``mem_app``        -- the ``mem`` typer sub-app (search / forget / audit);
                          W3 mounts it under the main ``cexai`` CLI.
  * ``chain_event`` / ``compute_event_hash`` -- build/verify hash-chained events.

Scope note: P1 (persistent episodic memory) + the mem CLI ship here. P2 (session
-> KC distillation, FR-006), P3 (cross-session patterns, FR-007), FR-009 redaction
+ FR-013 topic-drift split are v0.2-W2-stretch and flagged with TODOs in-code.

absorbs: 07_claude-mem/episodic
"""

from cexai.memory.episodic.cli import mem_app
from cexai.memory.episodic.store import (
    EpisodicMemory,
    chain_event,
    compute_event_hash,
)

__all__ = [
    "EpisodicMemory",
    "mem_app",
    "chain_event",
    "compute_event_hash",
]
