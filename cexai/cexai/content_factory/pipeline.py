"""The 7-stage content pipeline over MoneyPrinterTurbo (cexai-specs/20 S 2).

``CFPipeline`` wraps MoneyPrinterTurbo's end-to-end faceless-video pipeline
(topic -> script -> TTS -> B-roll -> subtitles -> music -> mp4) as a typed
``workflow`` (ZERO new kinds). The boundary rule (spec S 2) is absolute: cexai owns
the open_var mapping + the TTS swap; everything inside the workflow box is MPT,
called as a library/subprocess and NEVER forked or rewritten.

Two methods, two responsibilities:
  * ``plan(profile, env)`` is PURE + offline -- it maps the six open_vars onto a typed
    ``CFPipelineSpec`` (the resolved render plan + presets) WITHOUT touching any
    engine. This is what makes SC-008 observable: two ``BrandProfile``s yield two
    different specs with ZERO code change.
  * ``render(profile, env)`` runs the pipeline -- preflight (fail fast on a missing
    engine, FR-011), plan, synthesize narration via the injected TTS chain, then hand
    the spec + narration to the MPT backend. MoneyPrinterTurbo is LAZY-imported
    (Article VIII / XIV): the default backend resolves it at first render, and when it
    is absent ``render`` raises ``RenderEngineUnavailableError`` at preflight. The
    offline tests inject a fake backend.

absorbs: 20_content_factory
"""

from __future__ import annotations

import logging
import re
from typing import Protocol, runtime_checkable

from cexai.content_factory._shared.errors import RenderEngineUnavailableError
from cexai.content_factory._shared.types import (
    BrandProfile,
    CFEnv,
    CFPipelineSpec,
    ChatterboxConfig,
    TtsResult,
    TtsSynthesizer,
)
from cexai.content_factory.tts import TtsFallback

__all__ = ["MptBackend", "CFPipeline", "build_pipeline"]

_LOG = logging.getLogger("cexai.content_factory.pipeline")

_SLUG_MAX = 60


@runtime_checkable
class MptBackend(Protocol):
    """The MoneyPrinterTurbo execution seam. ``produce`` consumes a resolved
    ``CFPipelineSpec`` + the synthesized narration and renders the final ``.mp4``,
    returning its path. An ``available`` attribute (default ``True`` when absent)
    lets ``CFPipeline`` preflight a missing engine and fail fast (FR-011) before any
    render begins. The impl backs this with the MPT library/subprocess; the offline
    tests inject a fake."""

    def produce(self, spec: CFPipelineSpec, narration: TtsResult) -> str:
        """Render ``spec`` with ``narration`` and return the output ``.mp4`` path."""
        ...


class _UnavailableMptBackend:
    """The default backend when MoneyPrinterTurbo is not resolvable. ``available`` is
    ``False`` so ``CFPipeline`` fails fast at preflight; ``produce`` raises the same
    actionable error if ever called directly."""

    available = False
    _MESSAGE = (
        "install MoneyPrinterTurbo + ffmpeg (and set PEXELS_API_KEY) or inject a "
        "backend via CFPipeline(backend=...)"
    )

    def produce(self, spec: CFPipelineSpec, narration: TtsResult) -> str:
        raise RenderEngineUnavailableError("moneyprinterturbo", self._MESSAGE)


def _load_default_backend() -> MptBackend:
    """Lazily resolve the production MPT backend. MoneyPrinterTurbo is an optional
    heavy dep imported only here (never at module load), so importing this package
    stays light. When it is absent we fall back to ``_UnavailableMptBackend`` -- the
    concrete MPT adapter lands when the engine is vendored; offline correctness does
    not depend on it."""
    try:
        import app  # type: ignore  # MoneyPrinterTurbo's package root  # noqa: F401
    except Exception:
        return _UnavailableMptBackend()
    # The concrete MPT library/subprocess adapter is wired by a later vendoring wave;
    # until then a present-but-unadapted MPT still yields the safe preflight path.
    return _UnavailableMptBackend()


class CFPipeline:
    """The 7-stage pipeline wrapping MoneyPrinterTurbo. ``backend`` is the injected MPT
    seam (default: lazily-resolved MPT, or the offline-safe ``_UnavailableMptBackend``);
    ``tts`` is the narration chain (default: ``TtsFallback`` -- Chatterbox -> neutral);
    ``env`` is an optional default ``CFEnv`` applied when a call omits one."""

    def __init__(
        self,
        backend: MptBackend | None = None,
        *,
        tts: TtsSynthesizer | None = None,
        env: CFEnv | None = None,
    ) -> None:
        self._backend = backend if backend is not None else _load_default_backend()
        self._tts = tts if tts is not None else TtsFallback()
        self._env = env

    # -- pure planning (offline; drives SC-008) ------------------------------ #
    def plan(self, profile: BrandProfile, env: CFEnv | None = None) -> CFPipelineSpec:
        """Map the six open_vars onto a typed ``CFPipelineSpec`` (FR-002 / S 3.3).

        Pure + offline -- no engine call. ``{brand_voice}`` + ``{language}`` become the
        ``ChatterboxConfig``; ``{topic}`` slugs into the ``{output_dir}/{brand}_{slug}
        .mp4`` path (FR-010); the platform presets (9:16, target duration, whisper
        subtitles, music bed, no watermark) come from ``env`` + the spec defaults.
        """
        env = env if env is not None else (self._env if self._env is not None else CFEnv())
        slug = _slugify(profile.topic)
        output_path = f"{env.output_dir}/{profile.brand}_{slug}.mp4"
        tts = ChatterboxConfig(
            reference_audio=profile.brand_voice,
            language=profile.language,
        )
        return CFPipelineSpec(
            brand=profile.brand,
            niche=profile.niche,
            topic=profile.topic,
            video_style=profile.video_style,
            language=profile.language,
            tts=tts,
            output_path=output_path,
            aspect=env.aspect,
            duration_seconds=env.duration_seconds,
        )

    # -- render (opt-in live engine) ----------------------------------------- #
    def render(self, profile: BrandProfile, env: CFEnv | None = None) -> str:
        """Render ``profile`` to a finished ``.mp4`` and return its path (US P1).

        Order: preflight (fail fast on a missing engine, FR-011) -> plan -> synthesize
        narration via the TTS chain -> hand the spec + narration to the MPT backend.
        The TTS chain degrades through its fallbacks; a fully-failed chain raises
        ``TtsUnavailableError``.
        """
        env = env if env is not None else (self._env if self._env is not None else CFEnv())
        self._preflight(env)
        spec = self.plan(profile, env)
        narration = self._tts.synthesize(self._script(profile), spec.tts)
        return self._backend.produce(spec, narration)

    # -- internals ----------------------------------------------------------- #
    def _preflight(self, env: CFEnv) -> None:
        """FR-011 -- fail fast with an actionable message when a hard render
        dependency (the MPT engine) is unavailable, BEFORE any render begins."""
        if not getattr(self._backend, "available", True):
            raise RenderEngineUnavailableError(
                "moneyprinterturbo", _UnavailableMptBackend._MESSAGE
            )

    @staticmethod
    def _script(profile: BrandProfile) -> str:
        """The script text fed to TTS. Offline this is a deterministic placeholder; the
        live MPT stage-2 LLM (``env.script_llm``: Ollama / Haiku / pre-written, S 3.5)
        generates the real script and carries the brand voice guidelines (S 10.1). The
        text is kept UTF-8 (NEVER ASCII-flattened) so PT-BR diacritics survive to TTS
        (S 10.2)."""
        return f"{profile.brand}: {profile.topic}"


def build_pipeline(
    backend: MptBackend | None = None,
    *,
    tts: TtsSynthesizer | None = None,
    env: CFEnv | None = None,
) -> CFPipeline:
    """Convenience constructor mirroring the package's other ``build_*`` helpers."""
    return CFPipeline(backend, tts=tts, env=env)


def _slugify(text: str, max_len: int = _SLUG_MAX) -> str:
    """ASCII-safe filename slug: lowercase, non-alphanumerics -> single hyphens,
    trimmed, capped at a hyphen boundary. PT-BR diacritics survive in the narration
    text (S 10.2) -- this transliteration applies ONLY to the output filename, never
    to the spoken/caption text."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")
    if len(slug) > max_len:
        slug = slug[:max_len].rsplit("-", 1)[0]
    return slug or "video"
