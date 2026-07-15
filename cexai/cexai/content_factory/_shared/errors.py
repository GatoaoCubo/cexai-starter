"""CEXAI content_factory exception hierarchy (open_var fill + TTS + render).

Rooted at the foundation's ``CexaiError`` so a caller can still catch the whole
package with one ``except CexaiError``. ``ContentFactoryError`` is the v0.6
(content factory) subtree root; the leaves below map to the specific failure modes
the 20_content_factory spec names, with the spec-named signatures encoded as
structured attributes so callers and tests branch on fields (``.missing_fields``,
``.slot``, ``.providers``, ``.engine``) rather than parsing messages -- mirroring
``ToolsError`` (v0.4) and ``DistributionError`` (v0.5).

Spec provenance:
  * OpenVarValidationError      -> 20 US P3 #2 / FR-003 / Article XIX -- a required
                                   open_var slot is missing, or a filled value fails
                                   its type / enum gate (the ``{video_style}``
                                   allowed_values gate). HARD FAIL pre-render.
                                   OpenVarValidationError(reason, missing_fields=...).
  * TtsUnavailableError         -> 20 US P2 / FR-007 -- every provider in the TTS
                                   fallback chain (Chatterbox -> F5-TTS -> Edge-TTS)
                                   failed, so no narration could be produced.
                                   TtsUnavailableError(providers).
  * RenderEngineUnavailableError-> 20 FR-011 -- a hard render dependency
                                   (MoneyPrinterTurbo / ffmpeg) is absent at
                                   preflight; fail fast with an actionable message
                                   BEFORE starting a render, never mid-render.
                                   RenderEngineUnavailableError(engine, reason).

absorbs: 20_content_factory
"""

from __future__ import annotations

from cexai.foundation._shared.errors import CexaiError

__all__ = [
    "ContentFactoryError",
    "OpenVarValidationError",
    "TtsUnavailableError",
    "RenderEngineUnavailableError",
]


class ContentFactoryError(CexaiError):
    """Root of the content_factory subtree -- an open_var fill, TTS, or render
    failure. Subclasses ``CexaiError`` so a single ``except CexaiError`` covers it."""


class OpenVarValidationError(ContentFactoryError):
    """A filled ``BrandProfile`` failed the open_var contract (20 US P3 #2 / FR-003 /
    Article XIX HARD FAIL). Either a REQUIRED slot (``brand`` / ``niche`` / ``topic``)
    is missing, or a present value failed its type / enum gate (the ``{video_style}``
    allowed_values gate) -- both abort pre-render with a precise message naming the
    offending slot. ``reason`` is the human-readable cause; ``missing_fields`` is the
    ordered tuple of absent required slots (empty when the failure is an invalid
    value rather than a missing slot), surfaced so the operator fixes the exact slot."""

    def __init__(self, reason: str, *, missing_fields: tuple[str, ...] = ()) -> None:
        self.reason = reason
        self.missing_fields = tuple(missing_fields)
        super().__init__(reason)


class TtsUnavailableError(ContentFactoryError):
    """Every provider in the TTS fallback chain failed (20 US P2 / FR-007). The
    chain (Chatterbox -> F5-TTS -> Edge-TTS) is meant to degrade, never abort -- this
    is raised only when even the neutral Edge-TTS terminal could not synthesize, so no
    narration track exists. ``providers`` is the ordered tuple of provider ids that
    were attempted and failed, surfaced for the diagnostic log."""

    def __init__(self, providers: tuple[str, ...]) -> None:
        self.providers = tuple(providers)
        super().__init__(
            f"all TTS providers failed: {list(self.providers)!r}"
        )


class RenderEngineUnavailableError(ContentFactoryError):
    """A hard render dependency is absent at preflight (20 FR-011). MoneyPrinterTurbo,
    ffmpeg, or another required engine is not installed/resolvable, so a live render
    cannot start. This FAILS FAST with an actionable message BEFORE the render begins
    (never mid-render). Offline planning does NOT raise this -- only an opt-in live
    render does. ``engine`` is the missing dependency and ``reason`` is the actionable
    remediation, surfaced to the operator."""

    def __init__(self, engine: str, reason: str) -> None:
        self.engine = engine
        self.reason = reason
        super().__init__(f"render engine {engine!r} unavailable: {reason}")
