"""Injection ranking + budgeting -- the relevance math of episodic recall.

Pure, dependency-free functions that turn a query embedding + a set of
``CompressedSession``s into the bounded list to inject at session start
(cexai-specs/07_claude-mem/spec.md FR-003/FR-004/FR-014):

  * ``rank_by_similarity`` -- cosine of the query against each session's
    ``topic_embedding``, keeping only those at/above the similarity floor and
    ordering best-first (deterministic id tie-break).
  * ``estimate_tokens``    -- a coarse char/4 token estimate for one compressed
    session (the budget unit; FR-004's cap is approximate by design).
  * ``select_within_budget`` -- greedily pack ranked sessions under the token
    budget, in relevance order.
  * ``inject_sessions``    -- the composed entrypoint. FR-014: when NOTHING
    clears the floor it returns ``()`` so an unrelated new session gets no noise.

absorbs: 07_claude-mem/episodic
"""

from __future__ import annotations

import json
import math
from collections.abc import Sequence

from cexai.memory._shared.types import CompressedSession

__all__ = [
    "estimate_tokens",
    "rank_by_similarity",
    "select_within_budget",
    "inject_sessions",
    "DEFAULT_SIMILARITY_FLOOR",
    "CHARS_PER_TOKEN",
]

# Topic-similarity floor (07 US P1 "topic" definition: cosine >= 0.7). Configurable
# at the EpisodicMemory level; this is the module default.
DEFAULT_SIMILARITY_FLOOR = 0.7
# Coarse token heuristic. The injection budget (FR-004) is an upper bound, not an
# exact accountant -- char/4 is the standard rough estimate and keeps this path
# dependency-free (no tokenizer import in the hot path, Article VIII).
CHARS_PER_TOKEN = 4


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    """Exact cosine similarity (higher = closer). Returns 0.0 if either side is the
    zero vector, so an empty/zero query never raises and never spuriously matches."""
    dot = 0.0
    for x, y in zip(a, b):
        dot += x * y
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def estimate_tokens(cs: CompressedSession) -> int:
    """Approximate the injected size of one compressed session: the narrative plus
    its serialized structured digest, at ``CHARS_PER_TOKEN`` chars/token (min 1)."""
    chars = len(cs.narrative) + len(
        json.dumps(dict(cs.structured), sort_keys=True, ensure_ascii=True)
    )
    return max(1, chars // CHARS_PER_TOKEN)


def rank_by_similarity(
    query_embedding: Sequence[float],
    sessions: Sequence[CompressedSession],
    *,
    floor: float,
) -> list[tuple[float, CompressedSession]]:
    """Score each session's ``topic_embedding`` against the query, keep those at or
    above ``floor``, and order best-first. Sessions with no topic embedding are
    skipped. Ties break on ``session_id`` so the ordering is stable run to run."""
    scored: list[tuple[float, CompressedSession]] = []
    for cs in sessions:
        if cs.topic_embedding is None:
            continue
        score = _cosine(query_embedding, cs.topic_embedding)
        if score >= floor:
            scored.append((score, cs))
    scored.sort(key=lambda item: (-item[0], item[1].session_id))
    return scored


def select_within_budget(
    ranked: Sequence[tuple[float, CompressedSession]], budget_tokens: int
) -> tuple[CompressedSession, ...]:
    """Pack ranked sessions under ``budget_tokens`` in relevance order. A session
    that would overflow the budget is skipped (a smaller, lower-ranked one may
    still fit), so the cap is never exceeded (FR-004)."""
    chosen: list[CompressedSession] = []
    used = 0
    for _score, cs in ranked:
        cost = estimate_tokens(cs)
        if used + cost > budget_tokens:
            continue
        chosen.append(cs)
        used += cost
    return tuple(chosen)


def inject_sessions(
    query_embedding: Sequence[float],
    sessions: Sequence[CompressedSession],
    *,
    budget_tokens: int,
    floor: float = DEFAULT_SIMILARITY_FLOOR,
) -> tuple[CompressedSession, ...]:
    """Rank + budget-pack in one call. Returns ``()`` when no session clears the
    floor (FR-014: an unrelated session start injects zero memory, no noise)."""
    ranked = rank_by_similarity(query_embedding, sessions, floor=floor)
    if not ranked:
        return ()
    return select_within_budget(ranked, budget_tokens)
