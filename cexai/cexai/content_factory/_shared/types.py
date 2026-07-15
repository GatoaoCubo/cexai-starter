"""Frozen type contracts for the CEXAI content_factory layer -- the v0.6 freeze.

These names and shapes are FROZEN for the whole v0.6 (content factory) milestone.
Every v0.6 surface -- the open_var layer, the MoneyPrinterTurbo pipeline wrap, the
Chatterbox TTS swap, the CLI entry point -- imports these symbols and MUST NOT
change their names or fields. If a shape must evolve, that is a versioned,
peer-reviewed change, not an in-flight edit. This mirrors the v0.1 foundation,
v0.2 memory, v0.3 orchestration + governance, v0.4 tools, and v0.5 distribution
freeze discipline in ``cexai.{foundation,memory,orchestration,governance,tools,
distribution}._shared.types``.

Design constraints (Article VIII -- Anti-Abstraction):
  * stdlib typing only -- NO pydantic, NO moneyprinterturbo / chatterbox / torch /
    ffmpeg in this contract. The heavy engines land lazily in the impl modules
    (``pipeline`` lazy-imports MoneyPrinterTurbo, ``tts`` lazy-imports Chatterbox);
    the freeze stays import-light. ``open_vars`` is the one module that imports the
    already-frozen foundation open_vars validator (pydantic, an existing hard dep)
    -- this freeze does not.
  * every value type is an immutable ``@dataclass(frozen=True, slots=True)``.
  * collection fields are tuples / read-only mappings so instances are safely
    shareable across threads, nuclei, and providers without defensive copying.

One subsystem, one vocabulary here (cexai-specs/20_content_factory):
  * BrandProfile        -- the six filled open_var slots (the product's net-new layer).
  * CFPipelineSpec      -- the resolved 7-stage render plan over MoneyPrinterTurbo.
  * ChatterboxConfig    -- the Chatterbox TTS swap parameters.
  * TtsFallbackChain    -- the ordered Chatterbox -> F5-TTS -> Edge-TTS chain.
  * TtsResult           -- the typed outcome of a narration synthesis.
  * CFEnv               -- keys + render presets (Pexels, script LLM, aspect, duration).
  * ContentFactory / TtsSynthesizer -- the two seams the impl modules implement.

These COMPOSE with -- they do NOT replace -- the wrapped engines. The pipeline calls
MoneyPrinterTurbo as a library/subprocess and NEVER forks or rewrites it (boundary
rule, spec S 2); the TTS layer swaps Chatterbox in as MPT's narration provider and
degrades through the fallback chain. This module references that boundary; it does
not duplicate either engine's vocabulary.

TAXONOMY NOTE (founder rule, taxonomy-neutral milestone): these are Python CODE
types. Per N07's locked v0.6 decision this milestone registers ZERO kinds and does
NOT touch ``.cex/kinds_meta.json`` (the full disposition lives in
``cexai/docs/adr_v06_content_factory_taxonomy.md``). The spec's five Key Entities
each REUSE an existing kind -- they are RUNTIME PROJECTIONS, not kinds (precedent:
FetchResult, Span, TopologyRun, AuthToken, SkillManifest, Lockfile):
  * ``BrandProfile``  -> REUSE ``input_schema`` (the six-slot typed shape) +
    ``validation_schema`` (the required-slot + enum gate). Filling/validation is the
    foundation open_vars validator (Article XIX), not a new schema kind.
  * ``CFPipelineSpec``-> REUSE ``workflow`` (the 7-stage topic->...->mp4 contract).
  * ``ChatterboxConfig`` -> REUSE ``tts_provider`` (the Chatterbox swap config).
  * ``TtsFallbackChain`` -> REUSE ``fallback_chain`` (Chatterbox -> F5-TTS -> Edge-TTS).
  * ``CFEnv``         -> REUSE ``env_config`` (Pexels key + script LLM + presets).
  TtsResult is transient runtime data with no persisted-artifact form.

Spec provenance:
  * cexai-specs/20_content_factory/spec.md -- US P1/P2/P3 + FR-001..012 +
        SC-001..009 + Key Entities (BrandProfile / CFPipeline / ChatterboxProvider /
        TtsFallback / CFEnv, all USE-existing) + Section 3.3 open_var mapping.

absorbs: 20_content_factory
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Protocol, runtime_checkable

__all__ = [
    # closed-vocabulary tokens
    "VideoStyle",
    "TtsProviderId",
    "OPEN_VAR_SLOTS",
    "CF_STAGES",
    # value contracts
    "BrandProfile",
    "ChatterboxConfig",
    "TtsFallbackChain",
    "TtsResult",
    "CFPipelineSpec",
    "CFEnv",
    # protocols (the seams the impl modules implement)
    "TtsSynthesizer",
    "ContentFactory",
]

# The script tone + subtitle/font preset + clip-concat mode (spec open_var
# ``video_style`` / Section 3.3). Enum-gated by the validation_schema reuse; kept
# ``str`` on ``BrandProfile`` for headroom, this Literal is the canonical set.
VideoStyle = Literal["educational", "narrative", "listicle"]

# The ordered TTS provider ids of the fallback chain (spec Section 3.4): Chatterbox
# (MIT, local, voice clone) -> F5-TTS (MIT, local) -> Edge-TTS (free, cloud, neutral
# PT-BR). Kept ``str`` on the wire for headroom; this Literal is the canonical three.
TtsProviderId = Literal["chatterbox", "f5_tts", "edge_tts"]

# The six open_var slot names, in the spec's frontmatter order. This IS the
# input_schema shape (the typed contract a brand fills); the validation_schema gate
# (required slots + the video_style enum) is applied by ``open_vars.fill``.
OPEN_VAR_SLOTS: tuple[str, ...] = (
    "brand",
    "brand_voice",
    "niche",
    "video_style",
    "language",
    "topic",
)

# The seven pipeline stages wrapped over MoneyPrinterTurbo (spec S 2 architecture):
# topic -> script (LLM) -> TTS (Chatterbox swap) -> B-roll (Pexels) -> subtitles
# (faster-whisper on the generated audio) -> music (bgm) -> assemble (ffmpeg -> mp4).
CF_STAGES: tuple[str, ...] = (
    "topic",
    "script",
    "tts",
    "broll",
    "subtitles",
    "music",
    "assemble",
)


@dataclass(frozen=True, slots=True)
class BrandProfile:
    """The six filled open_var slots -- the factory's net-new layer (spec US P3 /
    Key Entities: BrandProfile). RUNTIME DATA, not a kind -- the persisted contract
    REUSES ``input_schema`` (shape) + ``validation_schema`` (gate) (see module
    TAXONOMY NOTE); this is its in-memory shape after ``open_vars.fill``. ``brand``
    (the brand identity injected into the script prompt + endcard overlay),
    ``niche`` (content domain; filters script topic + seeds Pexels terms), and
    ``topic`` (the single MPT ``video_subject``) are the three REQUIRED slots.
    ``brand_voice`` is the reference-audio path (>= 5s) for the Chatterbox zero-shot
    clone -- ``None`` selects a neutral voice (no crash, US P1 #2). ``video_style``
    is one of ``VideoStyle`` (enum-gated, default ``educational``). ``language`` is
    the BCP-47 narration/script locale (default ``pt-BR``, compiler-filled). A second
    BrandProfile drives a correspondingly different video with ZERO code change
    (SC-008) -- this layer is what makes that true."""

    brand: str
    niche: str
    topic: str
    brand_voice: str | None = None
    video_style: str = "educational"
    language: str = "pt-BR"


@dataclass(frozen=True, slots=True)
class ChatterboxConfig:
    """The Chatterbox TTS swap parameters (spec US P2 / Section 3.1 / Key Entities:
    ChatterboxProvider). RUNTIME DATA, not a kind -- REUSES the ``tts_provider`` kind
    (see module TAXONOMY NOTE). ``reference_audio`` is the ``{brand_voice}`` clip
    Chatterbox clones from (``audio_prompt_path``); ``None`` -> neutral voice.
    ``language`` is the narration locale (default ``pt-BR``); ``exaggeration`` is the
    emotion/expressiveness control in ``[0.0, 1.0]`` (default 0.5, per kc_chatterbox);
    ``device`` is the compute target -- ``cpu`` by default (FR-009: CPU-only, GPU
    MAY accelerate but MUST NOT be required)."""

    reference_audio: str | None = None
    language: str = "pt-BR"
    exaggeration: float = 0.5
    device: str = "cpu"


@dataclass(frozen=True, slots=True)
class TtsFallbackChain:
    """The ordered TTS provider chain (spec Section 3.4 / Key Entities: TtsFallback).
    RUNTIME DATA, not a kind -- REUSES the ``fallback_chain`` kind (see module
    TAXONOMY NOTE). ``providers`` is the ordered tuple of ``TtsProviderId`` tried in
    turn (default Chatterbox -> F5-TTS -> Edge-TTS, FR-007): a provider failure
    (model load / OOM) degrades to the next so a render NEVER aborts on TTS;
    ``{brand_voice}`` is honored by Chatterbox/F5-TTS and dropped to a neutral voice
    at the Edge-TTS terminal. The chosen provider is surfaced in ``TtsResult``."""

    providers: tuple[str, ...] = ("chatterbox", "f5_tts", "edge_tts")


@dataclass(frozen=True, slots=True)
class TtsResult:
    """The typed outcome of one narration synthesis (spec US P2). RUNTIME DATA, not a
    kind. ``provider`` is the ``TtsProviderId`` that actually produced the audio (the
    chosen fallback-chain link, logged per FR-007); ``wav_path`` is the generated
    narration track consumed by the subtitle (faster-whisper) + assembly stages;
    ``cloned`` is ``True`` when the brand voice was honored (Chatterbox / F5-TTS with
    a ``reference_audio``) and ``False`` for the neutral Edge-TTS terminal."""

    provider: str
    wav_path: str
    cloned: bool


@dataclass(frozen=True, slots=True)
class CFPipelineSpec:
    """The resolved 7-stage render plan over MoneyPrinterTurbo (spec S 2 / Key
    Entities: CFPipeline). RUNTIME DATA, not a kind -- REUSES the ``workflow`` kind
    (see module TAXONOMY NOTE); produced by ``pipeline.CFPipeline.plan`` from a
    ``BrandProfile`` + ``CFEnv`` BEFORE any render, so the plan is inspectable and the
    open_var swap is observable offline. ``brand`` / ``niche`` / ``topic`` /
    ``video_style`` / ``language`` carry the resolved open_vars; ``tts`` is the
    ``ChatterboxConfig`` derived from ``{brand_voice}`` + ``{language}``;
    ``output_path`` is the destination ``{output_dir}/{brand}_{slug}.mp4`` (FR-010).
    The fixed render presets (render config, NOT brand identity -- spec S 3.3) are
    ``aspect`` (9:16 vertical), ``duration_seconds`` (target 30, SC-002 band 25-35),
    ``subtitles_enabled`` + ``subtitle_provider`` (``whisper`` -- the critical
    integration detail: faster-whisper transcribes the Chatterbox audio because
    Chatterbox emits no word boundaries, FR-006), ``music_enabled`` (a bgm bed mixed
    below narration, SC-005), and ``watermark`` (``False`` -- the brand owns the
    output, SC-006). ``stages`` is ``CF_STAGES``. Two specs from two different
    BrandProfiles differ field-by-field with ZERO code change (SC-008)."""

    brand: str
    niche: str
    topic: str
    video_style: str
    language: str
    tts: ChatterboxConfig
    output_path: str
    aspect: str = "9:16"
    duration_seconds: int = 30
    subtitles_enabled: bool = True
    subtitle_provider: str = "whisper"
    music_enabled: bool = True
    watermark: bool = False
    stages: tuple[str, ...] = field(default=CF_STAGES)


@dataclass(frozen=True, slots=True)
class CFEnv:
    """Keys + render presets (spec S 2 / Section 3.3 / 3.5 / Key Entities: CFEnv).
    RUNTIME DATA, not a kind -- REUSES the ``env_config`` kind (see module TAXONOMY
    NOTE). ``pexels_api_key`` is read from the environment for B-roll (FR-008, never
    hardcoded; ``None`` defers the preflight check to live render); ``script_llm`` is
    the MPT script-generation backend (``ollama`` default / ``haiku`` / ``prewritten``
    -- infra, NOT a brand open_var, spec S 3.5); ``output_dir`` is the render
    destination directory; ``aspect`` (9:16) and ``duration_seconds`` (30) are the
    platform presets (render config, not brand identity); ``live_render`` gates the
    actual engine invocation -- ``False`` (default) plans offline (Article XIV), and
    the CLI flips it from the ``CEXAI_LIVE_RENDER`` env flag (opt-in)."""

    pexels_api_key: str | None = None
    script_llm: str = "ollama"
    output_dir: str = "output"
    aspect: str = "9:16"
    duration_seconds: int = 30
    live_render: bool = False


# --------------------------------------------------------------------------- #
# Protocols -- the seams the impl modules implement. Structural (no base class   #
# required); runtime_checkable allows isinstance smoke checks.                   #
# --------------------------------------------------------------------------- #
@runtime_checkable
class TtsSynthesizer(Protocol):
    """The narration-synthesis seam (spec US P2 / FR-004/005). ``synthesize`` turns
    ``text`` into a narration track per a ``ChatterboxConfig`` and returns a typed
    ``TtsResult`` (the provider used + the wav path + whether the brand voice was
    cloned). A provider that cannot run (model load error / OOM / engine absent)
    raises so the fallback chain (``tts.TtsFallback``) can degrade to the next link
    (FR-007). The impl ships the concrete Chatterbox provider behind a lazy import;
    the offline tests inject a fake."""

    def synthesize(self, text: str, config: ChatterboxConfig) -> TtsResult:
        """Synthesize ``text`` to a narration ``TtsResult`` per ``config``."""
        ...


@runtime_checkable
class ContentFactory(Protocol):
    """The end-to-end factory seam (spec US P1 / FR-001/010). ``render`` consumes a
    filled ``BrandProfile`` and returns the absolute path of the produced
    ``{brand}_{slug}.mp4`` (exit 0 on PASS). The live render is opt-in (the
    ``CEXAI_LIVE_RENDER`` flag / ``CFEnv.live_render``); the default offline path
    plans the render and returns the planned output path without invoking the engine
    (Article XIV). The impl wraps MoneyPrinterTurbo behind a lazy import; the offline
    tests inject a fake MPT backend."""

    def render(self, profile: BrandProfile) -> str:
        """Render ``profile`` and return the output ``.mp4`` path."""
        ...
