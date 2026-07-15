"""Citation gate -- the F7 GOVERN enforcement seam for welib direct-reuse.

cexai-specs/11_welib US P2 / SC-002 / V11-F2: a derived artifact that reuses welib
content VERBATIM (or as a >= 50-word paraphrase) MUST carry the originating
``Citation``. ``citations.py`` is the per-reference COMPLETENESS measurement; this
module is the per-ARTIFACT enforcement decision the CEX 8F engine's F7 GOVERN step
consults: given an artifact's frontmatter + body, decide whether it exhibits an
uncited welib direct-reuse and must therefore HARD-FAIL the quality gate.

Design (mirrors the W1 ``citations.py`` discipline -- Article VIII, stdlib only):
  * Pure + deterministic. No yaml dep: the engine passes its already-parsed
    frontmatter dict; ``evaluate_text`` ships a tiny line parser for standalone use
    (demos / benches).
  * CONSERVATIVE by construction -- the gate APPLIES only when the artifact
    EXPLICITLY signals welib provenance (a frontmatter reuse marker, a
    ``source_type: welib`` / welib source URL, AND -- for the content path -- a
    quoted passage at or above the paraphrase threshold). The 301 existing CEX
    kinds carry none of these, so ``applies`` is ``False`` for every one of them and
    F7 behaves byte-identically. This is the zero-regression contract: the gate can
    only ever ADD a failure to an artifact that declared it reused welib content.
  * The >= 50-word rule (V11-F2) is honored by the content path's verbatim-block
    word count; the explicit frontmatter markers cover the declared-reuse case.

This module does NOT raise -- it returns a verdict (the ``MissingCitationError``
HARD-FAIL semantics live in the F7 gate that folds this verdict in, exactly as
``citations.py`` documents for the completeness path).

absorbs: 11_welib/citation-gate
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

__all__ = [
    "PARAPHRASE_WORD_THRESHOLD",
    "WELIB_REUSE_MARKERS",
    "REQUIRES_CITATION_MARKERS",
    "CitationGateResult",
    "declares_welib_reuse",
    "requires_citation",
    "has_citation",
    "evaluate",
    "evaluate_general",
    "evaluate_text",
]

# 11 V11-F2: reuse is "verbatim OR a >= 50-word paraphrase". The content path
# treats a quoted passage of at least this many words as direct reuse.
PARAPHRASE_WORD_THRESHOLD = 50

# Frontmatter keys whose truthy value DECLARES the artifact reused welib content.
# An artifact built from welib references sets one of these; the 301 existing kinds
# never do (zero-false-positive primary signal).
WELIB_REUSE_MARKERS = (
    "welib_reuse",
    "reuses_welib_content",
    "welib_direct_reuse",
)

# A welib provenance token in the body / a frontmatter source field. Matched only
# as a supporting signal alongside a >= 50-word quoted passage (content path).
_WELIB_TOKEN_RE = re.compile(r"\bwelib(?:\.org)?\b", re.IGNORECASE)

# A markdown blockquote line ("> ...") -- the verbatim-reuse carrier we word-count.
_BLOCKQUOTE_RE = re.compile(r"^\s{0,3}>\s?(.*)$")

# A citations heading in the body (References / Citations / Sources / Bibliography).
_CITATION_HEADING_RE = re.compile(
    r"^\s{0,3}#{1,6}\s+(references|citations|sources|bibliography)\b",
    re.IGNORECASE | re.MULTILINE,
)

# A bare http(s) URL -- the locating field of an attribution-usable reference.
_URL_RE = re.compile(r"https?://\S+")

# A wikilink whose target names a citation artifact ([[...citation...]]).
_CITATION_WIKILINK_RE = re.compile(r"\[\[[^\]]*citation[^\]]*\]\]", re.IGNORECASE)

_TRUTHY_STRINGS = frozenset(("true", "yes", "1", "on", "verbatim", "paraphrase"))


@dataclass(frozen=True, slots=True)
class CitationGateResult:
    """The F7 citation-gate verdict for one artifact.

    ``applies`` is ``True`` when the welib direct-reuse signal is present (the gate
    is in scope for this artifact); ``fails`` is ``True`` only when it ``applies``
    AND no attribution-usable ``Citation`` is present -- the uncited-direct-reuse
    HARD-FAIL. ``reason`` is the human-readable cause surfaced into the F7 feedback.
    When ``applies`` is ``False`` the gate is a NO-OP (``fails`` is ``False``) and the
    engine adds no gate at all, so existing artifacts are unaffected."""

    applies: bool
    fails: bool
    reason: str

    @property
    def passed(self) -> bool:
        """``True`` when the gate does not fail (out of scope, or cited)."""
        return not self.fails


def _is_truthy(value: Any) -> bool:
    """Whether a frontmatter scalar counts as a truthy reuse marker."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in _TRUTHY_STRINGS
    return False


def _source_mentions_welib(frontmatter: Mapping[str, Any]) -> bool:
    """Whether a frontmatter source field names welib (``source_type: welib``,
    ``rag_source``/``sources`` containing a welib token)."""
    for key in ("source_type", "rag_source", "reuse_source"):
        val = frontmatter.get(key)
        if isinstance(val, str) and _WELIB_TOKEN_RE.search(val):
            return True
    for key in ("sources", "rag_sources"):
        val = frontmatter.get(key)
        if isinstance(val, (list, tuple)):
            if any(isinstance(v, str) and _WELIB_TOKEN_RE.search(v) for v in val):
                return True
        elif isinstance(val, str) and _WELIB_TOKEN_RE.search(val):
            return True
    return False


def _longest_blockquote_words(body: str) -> int:
    """The word count of the longest contiguous markdown blockquote in ``body``.
    A verbatim welib passage is pasted as a ``>`` blockquote; this measures it
    against ``PARAPHRASE_WORD_THRESHOLD`` (the >= 50-word direct-reuse rule)."""
    best = 0
    run: list[str] = []
    for line in body.splitlines():
        m = _BLOCKQUOTE_RE.match(line)
        if m:
            run.append(m.group(1))
            continue
        if run:
            best = max(best, len(" ".join(run).split()))
            run = []
    if run:
        best = max(best, len(" ".join(run).split()))
    return best


def declares_welib_reuse(frontmatter: Mapping[str, Any], body: str) -> bool:
    """Whether the artifact signals welib direct-reuse (the gate is in scope).

    Two independent signals (either suffices):
      1. EXPLICIT -- a truthy ``WELIB_REUSE_MARKERS`` frontmatter key (the
         zero-false-positive primary signal the welib build path sets).
      2. CONTENT  -- a welib provenance token (body or source field) AND a verbatim
         blockquote of at least ``PARAPHRASE_WORD_THRESHOLD`` words (V11-F2)."""
    if any(_is_truthy(frontmatter.get(k)) for k in WELIB_REUSE_MARKERS):
        return True
    welib_present = _source_mentions_welib(frontmatter) or bool(
        _WELIB_TOKEN_RE.search(body)
    )
    if welib_present and _longest_blockquote_words(body) >= PARAPHRASE_WORD_THRESHOLD:
        return True
    return False


def has_citation(frontmatter: Mapping[str, Any], body: str) -> bool:
    """Whether the artifact carries an attribution-usable citation.

    Broad on purpose -- the gate only FAILS an artifact that ``declares_welib_reuse``
    AND lacks ANY of these, so a generous citation detector minimizes false fails:
      * a non-empty frontmatter ``citations`` list (the canonical CEX shape), or a
        truthy ``citation`` / ``cited`` field;
      * a References / Citations / Sources / Bibliography heading followed by a URL;
      * a wikilink to a ``citation`` kind artifact."""
    for key in ("citations", "references"):
        val = frontmatter.get(key)
        if isinstance(val, (list, tuple)) and any(str(v).strip() for v in val):
            return True
        if isinstance(val, str) and val.strip():
            return True
    for key in ("citation", "cited", "cites"):
        if _is_truthy(frontmatter.get(key)):
            return True
    if _CITATION_WIKILINK_RE.search(body):
        return True
    heading = _CITATION_HEADING_RE.search(body)
    if heading and _URL_RE.search(body[heading.start():]):
        return True
    return False


# -- general (spec-agnostic) scope --------------------------------------------
# Generalizes the gate beyond welib direct-reuse to ANY output that declares a
# citation / grounding requirement (knowledge_card, research output, ...). These
# markers are the explicit opt-in; the 301 existing CEX kinds carry none of them,
# so the general path is a NO-OP for the whole corpus (the same zero-regression
# contract the welib path keeps). Marker-based ONLY -- it deliberately does NOT
# fold in the welib content heuristic, so a caller (e.g. the constitution's
# Commandment I) can consult ``requires_citation`` for SCOPE without dragging in
# the verbatim-blockquote inference. ``evaluate_general`` is the gate that unions
# the general markers with the welib special case.
REQUIRES_CITATION_MARKERS = (
    "requires_citation",
    "citation_required",
    "requires_grounding",
    "grounding_required",
    "factual_claims",
)
_REQUIRES_CITATION_TURN_RE = re.compile(
    r"<!--\s*(?:requires_citation|citation_required|requires_grounding)\s*-->",
    re.IGNORECASE,
)


def requires_citation(frontmatter: Mapping[str, Any], body: str) -> bool:
    """Whether the artifact declares a general citation requirement (gate in scope).

    The spec-agnostic generalization of ``declares_welib_reuse``: a truthy
    ``REQUIRES_CITATION_MARKERS`` frontmatter key or a ``<!-- requires_citation -->``
    turn marker. Marker-based only (no content inference), so it is safe for an
    external SCOPE consumer; existing kinds set none of these -> always ``False``."""
    if any(_is_truthy(frontmatter.get(k)) for k in REQUIRES_CITATION_MARKERS):
        return True
    return _REQUIRES_CITATION_TURN_RE.search(body) is not None


def evaluate(frontmatter: Mapping[str, Any] | None, body: str) -> CitationGateResult:
    """The F7 GOVERN decision for an artifact given its parsed frontmatter + body.

    Returns ``applies=False`` (a NO-OP) when there is no welib direct-reuse signal --
    the byte-identical path for the 301 existing kinds. When the signal IS present,
    ``fails`` is ``True`` iff no attribution-usable ``Citation`` accompanies it."""
    fm: Mapping[str, Any] = frontmatter or {}
    if not declares_welib_reuse(fm, body):
        return CitationGateResult(False, False, "no welib direct-reuse signal")
    if has_citation(fm, body):
        return CitationGateResult(True, False, "welib direct-reuse carries a Citation")
    return CitationGateResult(
        True, True, "uncited welib direct-reuse (verbatim or >= 50-word paraphrase)"
    )


def evaluate_general(frontmatter: Mapping[str, Any] | None, body: str) -> CitationGateResult:
    """The GENERAL F7 citation decision -- generalizes ``evaluate`` beyond welib.

    In scope when the artifact requires a citation by EITHER the general markers
    (``requires_citation``) OR the welib direct-reuse special case, so it subsumes
    ``evaluate``. OUT OF SCOPE (a NO-OP) for any artifact that declares neither --
    the byte-identical path for the 301 existing kinds. In scope, ``fails`` is True
    iff no attribution-usable ``Citation`` accompanies the grounded output."""
    fm: Mapping[str, Any] = frontmatter or {}
    if not (requires_citation(fm, body) or declares_welib_reuse(fm, body)):
        return CitationGateResult(False, False, "no citation-required signal")
    if has_citation(fm, body):
        return CitationGateResult(True, False, "citation-required output carries a Citation")
    return CitationGateResult(
        True, True, "citation-required output carries no Citation -- ground or abstain"
    )


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Minimal stdlib frontmatter splitter for ``evaluate_text`` (no yaml dep).

    Handles the gate-relevant subset: ``key: scalar``, inline ``[a, b]`` lists, and
    ``- item`` block lists. Not a general YAML parser -- the engine passes a real
    parsed dict to ``evaluate`` directly; this exists for standalone demos/benches."""
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, text
    fm: dict[str, Any] = {}
    cur_key: str | None = None
    for raw in lines[1:end]:
        if not raw.strip():
            continue
        stripped = raw.lstrip()
        if stripped.startswith("- ") and cur_key is not None:
            bucket = fm.setdefault(cur_key, [])
            if isinstance(bucket, list):
                bucket.append(stripped[2:].strip().strip("\"'"))
            continue
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", raw)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        cur_key = key
        if val == "":
            fm[key] = []
        elif val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            fm[key] = [x.strip().strip("\"'") for x in inner.split(",")] if inner else []
        elif val.lower() in ("null", "none", "~"):
            fm[key] = None
        else:
            fm[key] = val.strip().strip("\"'")
    return fm, "\n".join(lines[end + 1:])


def evaluate_text(text: str) -> CitationGateResult:
    """Convenience wrapper: split frontmatter from ``text`` and ``evaluate``. For
    standalone callers (demos, benches); the engine uses ``evaluate`` with its own
    parsed frontmatter."""
    fm, body = _parse_frontmatter(text)
    return evaluate(fm, body)
