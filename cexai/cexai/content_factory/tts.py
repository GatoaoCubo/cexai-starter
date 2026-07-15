"""The TTS swap + fallback chain (cexai-specs/20_content_factory US P2 / S 3.1/3.4).

MoneyPrinterTurbo defaults to paid Azure TTS. cexai swaps in Chatterbox (MIT, local,
zero-shot voice clone) so every brand carries its own narrated voice at zero API
cost, and wraps it in an ordered fallback chain so a TTS failure DEGRADES rather than
aborts the render (FR-007).

  * ``ChatterboxProvider`` -- the concrete ``TtsSynthesizer`` (REUSE ``tts_provider``):
    clones ``{brand_voice}`` via ``ChatterboxTTS.from_pretrained(device="cpu")``
    (FR-005 / FR-009). chatterbox + its audio saver are LAZY-imported inside
    ``synthesize`` (Article VIII -- import-light); when absent it raises
    ``TtsUnavailableError`` so the chain degrades. Backend seams (``model_loader`` /
    ``saver``) are injectable for the offline tests.
  * ``EdgeProvider`` -- the neutral Edge-TTS terminal: free cloud PT-BR voices, NO
    clone (``cloned=False``). Lazy-imported; raises ``TtsUnavailableError`` when
    edge-tts is absent.
  * ``TtsFallback`` -- the ordered chain (REUSE ``fallback_chain``): tries each
    provider in ``TtsFallbackChain.providers`` (default Chatterbox -> F5-TTS ->
    Edge-TTS), degrading on any provider failure; only when EVERY attempted provider
    fails does it raise ``TtsUnavailableError``. The provider map is injectable; the
    default wires Chatterbox + the neutral Edge terminal (the handoff's "Chatterbox
    -> neutral" path). The ``f5_tts`` link is reserved -- unwired here, so the chain
    falls through it to the neutral terminal; a later wave wires the F5-TTS provider.

Because Chatterbox emits NO word-level timestamps, downstream subtitles come from
MPT's faster-whisper path transcribing the generated audio (FR-006) -- that wiring
lives in ``pipeline`` (``subtitle_provider="whisper"``), not here.

absorbs: 20_content_factory
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from typing import Any

from cexai.content_factory._shared.errors import TtsUnavailableError
from cexai.content_factory._shared.types import (
    ChatterboxConfig,
    TtsFallbackChain,
    TtsResult,
    TtsSynthesizer,
)

__all__ = [
    "ChatterboxProvider",
    "EdgeProvider",
    "TtsFallback",
    "build_tts",
]

_LOG = logging.getLogger("cexai.content_factory.tts")


# --------------------------------------------------------------------------- #
# Concrete providers -- each lazy-imports its engine inside synthesize.         #
# --------------------------------------------------------------------------- #
class ChatterboxProvider:
    """The Chatterbox TTS provider (the ``tts_provider`` swap). Clones ``{brand_voice}``
    from a >=5s reference clip. ``model_loader`` is an injectable ``device -> model``
    seam (default: lazy ``ChatterboxTTS.from_pretrained``); ``saver`` is an injectable
    ``(wav, sample_rate) -> path`` seam (default: lazy soundfile/torchaudio write).
    Both engine imports are deferred to ``synthesize`` so importing this module stays
    light; an absent engine surfaces as ``TtsUnavailableError`` (the chain degrades)."""

    def __init__(
        self,
        *,
        model_loader: Callable[[str], Any] | None = None,
        saver: Callable[[Any, int], str] | None = None,
    ) -> None:
        self._model_loader = model_loader
        self._saver = saver

    def synthesize(self, text: str, config: ChatterboxConfig) -> TtsResult:
        loader = self._model_loader or _load_chatterbox_model
        model = loader(config.device)  # raises TtsUnavailableError if the engine is absent
        wav = model.generate(
            text,
            audio_prompt_path=config.reference_audio,
            exaggeration=config.exaggeration,
        )
        saver = self._saver or _save_wav
        wav_path = saver(wav, getattr(model, "sr", 24000))
        return TtsResult(
            provider="chatterbox",
            wav_path=wav_path,
            cloned=bool(config.reference_audio),
        )


class EdgeProvider:
    """The neutral Edge-TTS terminal -- free cloud PT-BR voices, NO clone. ``backend``
    is an injectable ``(text, language) -> wav_path`` seam (default: lazy edge-tts).
    Lazy-imported; an absent edge-tts surfaces as ``TtsUnavailableError``."""

    def __init__(self, *, backend: Callable[[str, str], str] | None = None) -> None:
        self._backend = backend

    def synthesize(self, text: str, config: ChatterboxConfig) -> TtsResult:
        backend = self._backend or _edge_synthesize
        wav_path = backend(text, config.language)
        return TtsResult(provider="edge_tts", wav_path=wav_path, cloned=False)


# --------------------------------------------------------------------------- #
# The ordered fallback chain.                                                   #
# --------------------------------------------------------------------------- #
class TtsFallback:
    """The ordered TTS fallback chain (``fallback_chain`` reuse). Tries each provider
    in ``chain.providers`` in turn; a provider that raises (model load / OOM / engine
    absent) is logged and the chain degrades to the next link (FR-007). A chain link
    with no wired provider is skipped. ``TtsUnavailableError`` is raised only when
    EVERY attempted provider failed. ``providers`` maps a ``TtsProviderId`` to a
    ``TtsSynthesizer``; when omitted, the default wiring (Chatterbox + neutral Edge)
    is used -- the ``f5_tts`` link is reserved (unwired) and falls through."""

    def __init__(
        self,
        chain: TtsFallbackChain | None = None,
        *,
        providers: Mapping[str, TtsSynthesizer] | None = None,
    ) -> None:
        self._chain = chain if chain is not None else TtsFallbackChain()
        self._providers = dict(providers) if providers is not None else None

    def synthesize(self, text: str, config: ChatterboxConfig) -> TtsResult:
        attempted: list[str] = []
        for provider_id in self._chain.providers:
            provider = self._provider(provider_id)
            if provider is None:
                continue  # reserved/unwired link -> fall through
            attempted.append(provider_id)
            try:
                return provider.synthesize(text, config)
            except TtsUnavailableError as exc:
                # A genuine, declared "engine absent / model unavailable" signal --
                # the expected degrade path (FR-007). Observable at WARNING (not
                # silent DEBUG) so an operator can see the chain is degrading.
                _LOG.warning("tts provider %s unavailable, degrading: %s", provider_id, exc)
                continue
            except Exception:  # noqa: BLE001 - R-241: unexpected != unavailable
                # Anything else (bad kwarg, AttributeError, etc.) is likely a real
                # coding bug in the provider, not an environment gap -- surface the
                # full traceback so it is not masked as "engine not installed". The
                # chain still degrades to the next provider (FR-007: never abort),
                # but the failure is no longer indistinguishable from a genuine
                # unavailability signal in the logs.
                _LOG.exception("tts provider %s raised an unexpected error, degrading", provider_id)
                continue
        raise TtsUnavailableError(tuple(attempted))

    def _provider(self, provider_id: str) -> TtsSynthesizer | None:
        providers = self._providers if self._providers is not None else _default_providers()
        return providers.get(provider_id)


def build_tts(
    chain: TtsFallbackChain | None = None,
    *,
    providers: Mapping[str, TtsSynthesizer] | None = None,
) -> TtsFallback:
    """Convenience constructor mirroring the package's other ``build_*`` helpers."""
    return TtsFallback(chain, providers=providers)


# --------------------------------------------------------------------------- #
# Lazy engine seams -- never imported at module load (Article VIII / XIV).      #
# --------------------------------------------------------------------------- #
def _default_providers() -> dict[str, TtsSynthesizer]:
    """The default chain wiring: Chatterbox (primary clone) + the neutral Edge
    terminal. ``f5_tts`` is intentionally absent (reserved for a later wave); the
    chain falls through it to Edge. Constructed lazily so the engines are not touched
    until a synthesis actually runs."""
    return {"chatterbox": ChatterboxProvider(), "edge_tts": EdgeProvider()}


def _load_chatterbox_model(device: str) -> Any:
    """Lazily load the Chatterbox model. chatterbox is an optional heavy dep imported
    only here; when it is absent the provider is unavailable and the chain degrades."""
    try:
        from chatterbox.tts import ChatterboxTTS  # type: ignore
    except Exception as exc:  # noqa: BLE001 - any import/load failure means unavailable
        raise TtsUnavailableError(("chatterbox",)) from exc
    return ChatterboxTTS.from_pretrained(device=device)


def _save_wav(wav: Any, sample_rate: int) -> str:
    """Lazily persist a generated waveform to a wav file, returning its path. soundfile
    is imported only here; absent -> the provider is unavailable (chain degrades)."""
    try:
        import tempfile

        import soundfile  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise TtsUnavailableError(("chatterbox",)) from exc
    handle = tempfile.NamedTemporaryFile(prefix="cexai_tts_", suffix=".wav", delete=False)
    handle.close()
    soundfile.write(handle.name, wav, sample_rate)
    return handle.name


def _edge_synthesize(text: str, language: str) -> str:
    """Lazily synthesize neutral narration via edge-tts, returning the wav path.
    edge-tts is imported only here; absent -> the terminal is unavailable."""
    try:
        import asyncio
        import tempfile

        import edge_tts  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise TtsUnavailableError(("edge_tts",)) from exc
    voice = "pt-BR-FranciscaNeural" if language.lower().startswith("pt") else "en-US-AriaNeural"
    handle = tempfile.NamedTemporaryFile(prefix="cexai_edge_", suffix=".mp3", delete=False)
    handle.close()

    async def _run() -> None:
        await edge_tts.Communicate(text, voice).save(handle.name)

    asyncio.run(_run())
    return handle.name
