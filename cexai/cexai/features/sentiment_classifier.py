"""Sentiment classifier -- the canonical cross-provider parity probe (W5).

A deliberately TRIVIAL feature (spec cexai-specs/08_goose/spec.md User Story P1):
given text, return one of {positive, negative, neutral}. It is the SC-001 probe --
the same classification must hold across Anthropic / OpenAI / Ollama (>= 95%
pairwise agreement). The feature itself does NOT classify; it delegates to the
configured provider via ``cexai.foundation.llm.call`` and normalizes the reply,
so swapping providers needs zero code change (FR-001, Article XIV).

Public contract (documented by the W5 tutorial -- keep EXACT):
    classify(text: str, *, provider: str | None = None) -> str
        Returns one of {"positive", "negative", "neutral"}.
        ``provider`` overrides the configured default for this call.

Invocation: registered at import as the feature ``"sentiment-classifier"`` so it
runs via both the library API and the CLI (Article II / FR-006):
    from cexai.features.sentiment_classifier import classify; classify("I love this")
    cexai sentiment-classifier "I love this"
The CLI / library only see the feature once ``cexai.features`` is imported (the
registration is a module side effect). A live run also needs ``CEXAI_PROVIDER`` +
credentials, and ``CEXAI_MODEL`` set to a model that provider serves; offline
tests inject fake providers instead.

absorbs: 08_goose/sentiment-parity-probe
"""

from __future__ import annotations

import os
import re
import string

from cexai.foundation._shared.types import LlmRequest, Message
from cexai.foundation.invocation import register_feature
from cexai.foundation.llm import call

__all__ = ["classify"]

# The three canonical labels, in scan precedence order. "neutral" is also the
# safe default when a reply matches none of them.
_LABELS: tuple[str, ...] = ("positive", "negative", "neutral")
_LABEL_SET = frozenset(_LABELS)
_WORD_PATTERNS = {label: re.compile(rf"\b{label}\b") for label in _LABELS}

# A tight, deterministic instruction: one word out, nothing else. Low temperature
# keeps the label stable across calls.
_SYSTEM_PROMPT = (
    "Classify the sentiment of the user's message. "
    "Reply with exactly one word: positive, negative, or neutral."
)
_DEFAULT_MODEL = "default"
_STRIP_CHARS = string.punctuation + string.whitespace


def _model() -> str:
    """Model id for the request. Provider-neutral default; live runs set
    ``CEXAI_MODEL`` to a model their ``CEXAI_PROVIDER`` actually serves. Fake
    providers ignore it, so the offline benchmark needs no configuration."""
    return os.environ.get("CEXAI_MODEL", _DEFAULT_MODEL)


def _normalize_label(text: str) -> str:
    """Map an arbitrary provider reply to one canonical label.

    Tolerant of the surface variance the spec calls acceptable (capitalization,
    surrounding whitespace, trailing punctuation): first try an exact match on
    the cleaned token, then look for a label word anywhere in the reply, and
    finally fall back to the safe default ``"neutral"``."""
    cleaned = text.strip().lower().strip(_STRIP_CHARS)
    if cleaned in _LABEL_SET:
        return cleaned
    low = text.lower()
    for label in _LABELS:
        if _WORD_PATTERNS[label].search(low):
            return label
    return "neutral"


def classify(text: str, *, provider: str | None = None) -> str:
    """Return the sentiment of ``text`` as ``"positive"``, ``"negative"``, or
    ``"neutral"``. Dispatches to ``provider`` (or the configured default) through
    the unified llm facade and normalizes the reply. Unrecognized replies map to
    ``"neutral"`` (safe default)."""
    request = LlmRequest(
        model=_model(),
        messages=(Message("system", _SYSTEM_PROMPT), Message("user", text)),
        temperature=0.0,
        max_tokens=8,
    )
    response = call(request, provider=provider)
    return _normalize_label(response.text)


# Module side effect: expose the feature to both invocation interfaces (W3).
register_feature("sentiment-classifier", classify)
