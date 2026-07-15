"""The content_factory entry point (cexai-specs/20 US P1 / FR-001/010).

The single seam a brand operator drives: fill the six open_vars -> run the pipeline
-> get a finished ``.mp4`` path. ``ContentFactoryRunner`` is the concrete
``ContentFactory``; ``run`` is the one-call convenience; ``main`` is the CLI
mirroring the spec's acceptance command (Section 5).

The live render is OPT-IN (Article XIV). By default -- and in every test -- the
runner PLANS the render (pure, offline) and returns the deterministic
``{brand}_{slug}.mp4`` path WITHOUT invoking MoneyPrinterTurbo / Chatterbox / ffmpeg.
A live render fires only when ``CFEnv.live_render`` is set or the ``CEXAI_LIVE_RENDER``
environment flag is truthy; then ``CFPipeline.render`` runs the real engine (and
fails fast at preflight if it is absent, FR-011).

absorbs: 20_content_factory
"""

from __future__ import annotations

import argparse
import os
from collections.abc import Sequence

from cexai.content_factory._shared.types import BrandProfile, CFEnv
from cexai.content_factory.open_vars import fill
from cexai.content_factory.pipeline import CFPipeline

__all__ = [
    "ContentFactoryRunner",
    "run",
    "build_factory",
    "main",
    "live_render_requested",
]

_LIVE_RENDER_ENV = "CEXAI_LIVE_RENDER"


def live_render_requested(env: CFEnv) -> bool:
    """True when a live engine render is opt-in: ``env.live_render`` or a truthy
    ``CEXAI_LIVE_RENDER`` flag. Everything else plans offline (Article XIV)."""
    if env.live_render:
        return True
    flag = os.environ.get(_LIVE_RENDER_ENV, "")
    return flag.strip().lower() not in ("", "0", "false", "no")


class ContentFactoryRunner:
    """The concrete ``ContentFactory``. ``pipeline`` is the injected ``CFPipeline``
    (default: a fresh one with the lazily-resolved MPT backend + TTS chain); ``env``
    is the default ``CFEnv`` (default: offline). ``render`` returns the output
    ``.mp4`` path -- a live engine render when opt-in, otherwise the planned path."""

    def __init__(self, *, pipeline: CFPipeline | None = None, env: CFEnv | None = None) -> None:
        self._pipeline = pipeline if pipeline is not None else CFPipeline()
        self._env = env if env is not None else CFEnv()

    def render(self, profile: BrandProfile) -> str:
        """Render ``profile`` (US P1). Live engine render when opt-in (``live_render`` /
        ``CEXAI_LIVE_RENDER``); otherwise the offline planned ``{brand}_{slug}.mp4``
        path with no engine call."""
        if live_render_requested(self._env):
            return self._pipeline.render(profile, self._env)
        return self._pipeline.plan(profile, self._env).output_path


def build_factory(
    *, pipeline: CFPipeline | None = None, env: CFEnv | None = None
) -> ContentFactoryRunner:
    """Convenience constructor mirroring the package's other ``build_*`` helpers."""
    return ContentFactoryRunner(pipeline=pipeline, env=env)


def run(
    profile: BrandProfile,
    env: CFEnv | None = None,
    *,
    pipeline: CFPipeline | None = None,
) -> str:
    """Fill-to-mp4 in one call: render ``profile`` and return the output ``.mp4`` path
    (offline plan by default; live engine when opt-in)."""
    return ContentFactoryRunner(pipeline=pipeline, env=env).render(profile)


# --------------------------------------------------------------------------- #
# CLI -- mirrors the spec acceptance command (Section 5). stdlib argparse only. #
# --------------------------------------------------------------------------- #
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="content_factory",
        description="Faceless short-social video factory: fill six brand open_vars -> one branded .mp4.",
    )
    parser.add_argument("--brand", required=True, help="Brand identity (required open_var).")
    parser.add_argument("--niche", required=True, help="Content domain (required open_var).")
    parser.add_argument("--topic", required=True, help="The single video subject (required open_var).")
    parser.add_argument("--voice", default=None, help="Reference audio path (>=5s) for the voice clone; omit for a neutral voice.")
    parser.add_argument("--language", default="pt-BR", help="Narration/script locale (BCP-47).")
    parser.add_argument("--style", default="educational", choices=["educational", "narrative", "listicle"], help="Video style preset.")
    parser.add_argument("--aspect", default="9:16", help="Aspect ratio preset (render config, not a brand open_var).")
    parser.add_argument("--duration", type=int, default=30, help="Target duration in seconds (render config).")
    parser.add_argument("--output-dir", default="output", help="Directory for the produced .mp4.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry: parse the acceptance-command flags, fill the open_vars, run the
    factory, and print the output path. Returns 0 on success (FR-010). Offline by
    default; set CEXAI_LIVE_RENDER for an actual engine render."""
    args = _build_parser().parse_args(argv)
    profile = fill(
        {
            "brand": args.brand,
            "niche": args.niche,
            "topic": args.topic,
            "brand_voice": args.voice,
            "language": args.language,
            "video_style": args.style,
        }
    )
    env = CFEnv(
        output_dir=args.output_dir,
        aspect=args.aspect,
        duration_seconds=args.duration,
        pexels_api_key=os.environ.get("PEXELS_API_KEY"),
        live_render=live_render_requested(CFEnv()),
    )
    output_path = run(profile, env)
    print(output_path)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI shim
    raise SystemExit(main())
