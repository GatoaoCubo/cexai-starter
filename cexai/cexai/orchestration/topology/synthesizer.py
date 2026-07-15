"""MoA synthesizer -- merge distinct-provider worker outputs (03 US2 acceptance #2).

The synthesizer is the second half of Mixture-of-Agents: after the executor fans
the prompt to N distinct-provider workers and gathers their outputs, the
synthesizer decides what the swarm's single answer is. Three regimes, decided by
pairwise text similarity:

  * CONVERGENCE -- every pair agrees above ``convergence_threshold`` (default
    0.95). The workers said the same thing; short-circuit and return the first
    worker's output with a ``[CONVERGED]`` note (no merge work needed).
  * DIVERGENCE  -- some pair disagrees below ``divergence_threshold`` (default
    0.7). The workers genuinely disagree; apply the ``divergence_action`` policy:
      - ``flag_human`` (default) -- refuse to silently pick; mark ``[FLAG_HUMAN]``
        for human review (high-stakes safety, the spec's conservative default).
      - ``pick_best``           -- choose the medoid (the output with the highest
        mean agreement with the others) and attach a justification.
  * MERGE       -- moderate agreement in between; combine all worker outputs into
    one ``[MERGED]`` result.

Similarity is bag-of-words cosine over whitespace tokens: pure stdlib, no numpy,
no embeddings, fully deterministic and offline (Article VIII / Article XIV). This
is deliberately simple -- a richer semantic similarity is a later, versioned
upgrade behind this same seam, not an in-flight change.

``Synthesizer`` is a CODE construct, not a new CEX kind (the founder taxonomy
rule): MoA is an existing ``topology`` variant and the synthesizer is its merge
policy, expressed in Python.

absorbs: 03_swarms/moa
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass

__all__ = [
    "cosine_similarity",
    "SynthesisOutcome",
    "Synthesizer",
]

# Policy defaults (03 US2): the thresholds the spec names and the conservative
# divergence action (refuse to auto-pick on genuine disagreement).
_CONVERGENCE_THRESHOLD = 0.95
_DIVERGENCE_THRESHOLD = 0.7
_DEFAULT_DIVERGENCE_ACTION = "flag_human"


def cosine_similarity(a: str, b: str) -> float:
    """Bag-of-words cosine similarity of two texts in ``[0.0, 1.0]``. Tokens are
    lowercased whitespace splits; two empty strings are identical (1.0) and any
    one-sided empty is fully dissimilar (0.0). Pure stdlib, deterministic."""
    va = Counter(a.lower().split())
    vb = Counter(b.lower().split())
    if not va or not vb:
        return 1.0 if va == vb else 0.0
    shared = set(va) & set(vb)
    dot = sum(va[token] * vb[token] for token in shared)
    norm_a = math.sqrt(sum(count * count for count in va.values()))
    norm_b = math.sqrt(sum(count * count for count in vb.values()))
    return dot / (norm_a * norm_b)


@dataclass(frozen=True, slots=True)
class SynthesisOutcome:
    """The synthesizer's verdict on a set of worker outputs. ``kind`` is one of
    ``converged`` | ``merged`` | ``flag_human`` | ``pick_best``; ``note`` is the
    short bracket tag (``[CONVERGED]`` ...); ``selected`` is the chosen worker id
    when a single output is returned (converge / pick_best) else ``None``;
    ``summary_ref`` is the compact audit payload-ref the executor stamps onto the
    synthesis ``CoordinationEvent``; ``detail`` is a human-readable justification
    (the agreement statistic) used for ``pick_best`` and ``flag_human``."""

    kind: str
    note: str
    selected: str | None
    summary_ref: str
    detail: str


class Synthesizer:
    """Merge policy for MoA worker outputs. Thresholds and the divergence action
    are injectable so a topology's synthesizer node-config can tune them; the
    defaults are the spec's (0.95 / 0.7 / flag_human)."""

    def __init__(
        self,
        *,
        convergence_threshold: float = _CONVERGENCE_THRESHOLD,
        divergence_threshold: float = _DIVERGENCE_THRESHOLD,
        divergence_action: str = _DEFAULT_DIVERGENCE_ACTION,
    ) -> None:
        self._convergence_threshold = convergence_threshold
        self._divergence_threshold = divergence_threshold
        self._divergence_action = divergence_action

    def synthesize(self, outputs: Mapping[str, str]) -> SynthesisOutcome:
        """Decide the swarm's single answer from ``outputs`` (worker_id -> text),
        which MUST be in declared worker order (the caller guarantees this; it
        fixes the convergence "first worker" and pick_best tie-break). Assumes
        quorum already held, so ``len(outputs) >= 1``."""
        ids = list(outputs)
        if len(ids) == 1:
            only = ids[0]
            return SynthesisOutcome(
                kind="merged",
                note="[MERGED]",
                selected=None,
                summary_ref=f"synth:[MERGED]:1:{only}",
                detail="single surviving worker",
            )

        sims = _pairwise_similarities(ids, outputs)

        if all(sim > self._convergence_threshold for sim in sims):
            first = ids[0]
            return SynthesisOutcome(
                kind="converged",
                note="[CONVERGED]",
                selected=first,
                summary_ref=f"synth:[CONVERGED]:{first}",
                detail=f"all pairs agree above {self._convergence_threshold}",
            )

        if any(sim < self._divergence_threshold for sim in sims):
            return self._on_divergence(ids, outputs, sims)

        return SynthesisOutcome(
            kind="merged",
            note="[MERGED]",
            selected=None,
            summary_ref=f"synth:[MERGED]:{len(ids)}",
            detail=f"moderate agreement (min pair {min(sims):.2f})",
        )

    def _on_divergence(
        self,
        ids: list[str],
        outputs: Mapping[str, str],
        sims: list[float],
    ) -> SynthesisOutcome:
        if self._divergence_action == "pick_best":
            medoid, mean_agreement = _medoid(ids, outputs)
            return SynthesisOutcome(
                kind="pick_best",
                note="[PICK_BEST]",
                selected=medoid,
                summary_ref=f"synth:[PICK_BEST]:{medoid}",
                detail=(
                    f"selected highest mean agreement (medoid) "
                    f"{mean_agreement:.2f}; min pair {min(sims):.2f}"
                ),
            )
        # Default: refuse to silently pick on genuine disagreement.
        return SynthesisOutcome(
            kind="flag_human",
            note="[FLAG_HUMAN]",
            selected=None,
            summary_ref="synth:[FLAG_HUMAN]",
            detail=f"workers diverged (min pair {min(sims):.2f} < {self._divergence_threshold})",
        )


def _pairwise_similarities(ids: list[str], outputs: Mapping[str, str]) -> list[float]:
    """All unordered pairwise cosine similarities over the worker outputs."""
    sims: list[float] = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            sims.append(cosine_similarity(outputs[ids[i]], outputs[ids[j]]))
    return sims


def _medoid(ids: list[str], outputs: Mapping[str, str]) -> tuple[str, float]:
    """The worker id with the highest MEAN similarity to the others (the most
    representative output), and that mean. Strict ``>`` over the declared order
    keeps the FIRST worker on a tie, so selection is deterministic."""
    best_id = ids[0]
    best_mean = -1.0
    for current in ids:
        others = [cosine_similarity(outputs[current], outputs[other]) for other in ids if other != current]
        mean_agreement = sum(others) / len(others) if others else 0.0
        if mean_agreement > best_mean:
            best_mean = mean_agreement
            best_id = current
    return best_id, best_mean
