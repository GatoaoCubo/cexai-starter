"""CEXAI content_factory -- the v0.6 faceless short-social video factory.

A typed ``{brand}``-fillable open_var wrapper over two OSS engines: MoneyPrinterTurbo
(Apache-2.0, the topic->mp4 pipeline) and Chatterbox TTS (MIT, the zero-shot voice
clone that replaces MPT's paid Azure default). The ONE net-new layer is the six-slot
open_var contract (``open_vars.fill`` -> ``BrandProfile``) -- everything else is
wrapped. A brand fills ``{brand, brand_voice, niche, video_style, language, topic}``
and gets its own branded vertical short with ZERO code change (SC-008).

  open_vars   the six-slot contract (REUSE input_schema + validation_schema)  -- the product
  pipeline    the 7-stage workflow over MoneyPrinterTurbo (REUSE workflow)
  tts         Chatterbox swap + fallback chain (REUSE tts_provider + fallback_chain)
  content_factory  the CLI entry point (fill -> render -> .mp4)

Engines are LAZY (Article VIII / XIV): importing this package touches NO
moneyprinterturbo / chatterbox / ffmpeg; the offline path plans without them and the
live render is opt-in (``CEXAI_LIVE_RENDER``). Attribution for both wrapped engines
is in ``ATTRIBUTION.md`` (SC-006 ownership).

TAXONOMY NOTE (founder rule, taxonomy-neutral milestone): the types here are Python
CODE. This milestone registers ZERO kinds and does NOT touch ``.cex/kinds_meta.json``
(see cexai/docs/adr_v06_content_factory_taxonomy.md). The five Key Entities each
REUSE an existing kind: BrandProfile -> input_schema + validation_schema; CFPipeline
-> workflow; ChatterboxProvider -> tts_provider; TtsFallback -> fallback_chain; CFEnv
-> env_config.

Spec provenance: cexai-specs/20_content_factory/spec.md (US P1/P2/P3 + FR-001..012 +
SC-001..009 + Key Entities).

absorbs: 20_content_factory
"""

from cexai.content_factory._shared.errors import (
    ContentFactoryError,
    OpenVarValidationError,
    RenderEngineUnavailableError,
    TtsUnavailableError,
)
from cexai.content_factory._shared.types import (
    CF_STAGES,
    OPEN_VAR_SLOTS,
    BrandProfile,
    CFEnv,
    CFPipelineSpec,
    ChatterboxConfig,
    ContentFactory,
    TtsFallbackChain,
    TtsResult,
    TtsSynthesizer,
)
from cexai.content_factory.content_factory import (
    ContentFactoryRunner,
    build_factory,
    main,
    run,
)
from cexai.content_factory.open_vars import declarations, fill
from cexai.content_factory.pipeline import CFPipeline, MptBackend, build_pipeline
from cexai.content_factory.tts import ChatterboxProvider, EdgeProvider, TtsFallback, build_tts

__all__ = [
    # value contracts
    "BrandProfile",
    "CFPipelineSpec",
    "ChatterboxConfig",
    "TtsFallbackChain",
    "TtsResult",
    "CFEnv",
    "OPEN_VAR_SLOTS",
    "CF_STAGES",
    # protocols
    "ContentFactory",
    "TtsSynthesizer",
    "MptBackend",
    # open_var layer (the product)
    "fill",
    "declarations",
    # pipeline
    "CFPipeline",
    "build_pipeline",
    # tts
    "ChatterboxProvider",
    "EdgeProvider",
    "TtsFallback",
    "build_tts",
    # entry point
    "ContentFactoryRunner",
    "run",
    "build_factory",
    "main",
    # errors
    "ContentFactoryError",
    "OpenVarValidationError",
    "TtsUnavailableError",
    "RenderEngineUnavailableError",
]
