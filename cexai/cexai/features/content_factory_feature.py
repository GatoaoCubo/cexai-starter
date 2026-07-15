"""content_factory feature -- fill the open_vars, plan the render (activation wave).

A thin wrapper exposing the faceless short-social video factory
(``cexai.content_factory``) through both invocation interfaces: the library API
(``run_feature("content-factory", ...)``) and the CLI (``cexai content-factory ...``).
It fills the six brand open_var slots (``open_vars.fill`` -> the validation_schema
gate) and delegates to the existing ``content_factory.run`` entrypoint, returning the
produced ``{brand}_{slug}.mp4`` path. By default -- and offline -- it PLANS the render
(pure, no MoneyPrinterTurbo / Chatterbox / ffmpeg); a live engine render is opt-in via
the ``CEXAI_LIVE_RENDER`` flag / a supplied ``CFEnv`` (Article XIV).

Public contract (keep EXACT):
    make_video(brand, niche, topic, *, brand_voice=None, video_style="educational",
               language="pt-BR", env=None) -> str
        ``brand`` / ``niche`` / ``topic`` -- the three REQUIRED open_var slots; a missing
                         one is a precise pre-render HARD FAIL (OpenVarValidationError).
        ``brand_voice`` -- reference-audio path (>=5s) for the voice clone; None -> a
                         neutral voice (no crash).
        ``video_style`` -- one of educational / narrative / listicle (enum-gated).
        ``language``    -- BCP-47 narration locale (default pt-BR).
        ``env``         -- optional ``CFEnv`` override (output dir, presets, live_render);
                         None plans offline by default.
        Returns the output ``.mp4`` path (offline planned path by default).

Invocation: registered at import as the feature ``"content-factory"`` so it runs via
both the library API and the CLI (Article II / FR-006). The CLI / library only see the
feature once ``cexai.features`` is imported (the registration is a module side effect).

absorbs: 20_content_factory
"""

from __future__ import annotations

from cexai.content_factory import fill, run
from cexai.content_factory._shared.types import CFEnv
from cexai.foundation.invocation import register_feature

__all__ = ["make_video"]


def make_video(
    brand: str,
    niche: str,
    topic: str,
    *,
    brand_voice: str | None = None,
    video_style: str = "educational",
    language: str = "pt-BR",
    env: CFEnv | None = None,
) -> str:
    """Fill the six brand open_vars and run the factory, returning the output ``.mp4``
    path. Offline (plan-only) by default; a live engine render is opt-in via
    ``CEXAI_LIVE_RENDER`` / a supplied ``env``. Delegates to ``content_factory.fill`` +
    ``content_factory.run`` -- the wrapper adds no rendering logic of its own."""
    profile = fill(
        {
            "brand": brand,
            "niche": niche,
            "topic": topic,
            "brand_voice": brand_voice,
            "video_style": video_style,
            "language": language,
        }
    )
    return run(profile, env)


# Module side effect: expose the feature to both invocation interfaces.
register_feature("content-factory", make_video)
