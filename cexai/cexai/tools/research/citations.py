"""Citation completeness helpers (cexai-specs/11_welib US P2 / SC-002 / WL3).

A derived artifact that reuses welib content verbatim (or as a >= 50-word
paraphrase) MUST carry the originating ``Citation`` (US P2 / V11-F2). The quality
gate measures that as completeness: of the references attached to an artifact, the
fraction that are attribution-usable. These pure functions are the measurement
seam -- they do NOT raise (the ``MissingCitationError`` HARD-FAIL lives in the
governance quality gate, US P2 acceptance #2); a caller folds ``missing_fields``
into that verdict.

Completeness bar: ``title``, ``authors``, ``url``, ``accessed_at`` (the locating
fields + the FR-006 audit anchor). ``year`` and ``isbn_or_doi`` are legitimately
optional on the frozen ``Citation`` (``None`` when unknown / unavailable -- e.g. an
arXiv preprint with no DOI), so they are NOT required for completeness.

absorbs: 11_welib
"""

from __future__ import annotations

from collections.abc import Iterable

from cexai.tools._shared.types import Citation

__all__ = [
    "REQUIRED_FIELDS",
    "missing_fields",
    "is_complete",
    "completeness_ratio",
]

# The minimum fields an attribution-usable Citation must carry. Order is the order
# ``missing_fields`` reports them in.
REQUIRED_FIELDS: tuple[str, ...] = ("title", "authors", "url", "accessed_at")


def missing_fields(citation: Citation) -> tuple[str, ...]:
    """Return the names of the REQUIRED_FIELDS that are empty / absent on
    ``citation`` (empty tuple => complete). ``authors`` counts as present when the
    tuple holds at least one author; the string fields count as present when
    non-empty."""
    missing: list[str] = []
    if not citation.title:
        missing.append("title")
    if not citation.authors:
        missing.append("authors")
    if not citation.url:
        missing.append("url")
    if not citation.accessed_at:
        missing.append("accessed_at")
    return tuple(missing)


def is_complete(citation: Citation) -> bool:
    """True when ``citation`` carries every REQUIRED_FIELD (attribution-usable)."""
    return not missing_fields(citation)


def completeness_ratio(citations: Iterable[Citation]) -> float:
    """The fraction of ``citations`` that are complete, in ``[0.0, 1.0]`` (SC-002
    targets 1.0 on direct-reuse cases). An empty input is vacuously complete
    (``1.0``): there is nothing to attribute, so nothing is missing."""
    items = tuple(citations)
    if not items:
        return 1.0
    complete = sum(1 for c in items if is_complete(c))
    return complete / len(items)
