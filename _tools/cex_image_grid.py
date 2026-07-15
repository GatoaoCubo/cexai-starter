#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI 2x2 generate-then-crop image pipeline -- cex_image_grid (mission CAPABILITY_LAYER, W2).

THE image cost lever (plan S4.2 / S1.2 module #4 / n03 S3): ONE generation call produces ONE
square 2x2 grid image; a PURE-PIL crop slices it into 4 equal product-scene tiles. 1 API call
-> 4 usable assets (vs 9 calls for the full 9-scene grid) = 4x cost reduction (plan S4.2).

THE FLOW:
  1. GENERATE  call a ``generator`` SEAM (the founder-gated live image API -- Gemini/Imagen;
               left as an injectable stub, NOT wired to live credentials here) to get ONE
               square 2x2 composite (PIL Image or a path). Default unbound -> a stub that
               errors CLEARLY (never a crash, never a fabricated image).
  2. CROP      PURE PIL: slice the square WxW composite at the 50/50 lines into 4 equal tiles
               (optional inner-gutter trim if the model drew separator lines -- n03 S3.6 risk).
               Non-square beyond tolerance -> ValueError (never silently distort).
  3. NAME      deterministic ``{base}_scene{1..4}.png`` under a per-tenant out_dir.
  4. MANIFEST  a small manifest: the per-tile scene label (HERO / MARKETPLACE / IN_CONTEXT /
               BENEFIT -- plan S4.2 the best-4 cells) + ONE C2PA-style provenance note for the
               master generation (ai_generated:true -- plan S4.2; the dashboard surfaces a
               visible "AI-generated image" label).

THE QUADRANT -> SCENE MAP (plan S4.2 "Best 4 scenes"; cells 1+9 mandatory):
  top-left  (scene1) = HERO TRUST       (highest conversion; always required)
  top-right (scene2) = MARKETPLACE READY (compliance shot, pure white; immutable)
  bot-left  (scene3) = IN CONTEXT        (lifestyle; top engagement)
  bot-right (scene4) = BENEFIT MACRO      (proof anchor)

PURE PIL (Pillow already installed). ASCII-only per .claude/rules/ascii-code-rule.md. The crop
is lazy-imported (the lazy-Pillow pattern from cex_motion_render.py:42) so this module imports
in an env without Pillow; the crop itself raises an ACTIONABLE message if Pillow is missing.

DEGRADE-NEVER (n05 -- never a crash):
  * generator unbound -> a clear ImageGridError ("no generator bound") BEFORE any PIL work --
    never a silent empty list, never a fabricated tile.
  * generator returns a non-square / too-small composite -> ValueError (do NOT distort).
  * Pillow absent -> an ImageGridError naming the missing dep (actionable), never an ImportError
    deep in a call stack.

The generator + the real image API are the FOUNDER-GATED live seam (n05 S5.1: no enabled image
MCP today). This module binds NO live credentials -- ``generator`` is an injected callable.
Signature: generator(prompt, *, size, tenant_id) -> (a PIL.Image.Image OR a path str). Tests
pass a fake generator that returns a real in-memory 2x2 PIL image.

Spec: plan_capability_layer_FINAL_2026-06-18.md (S4.2 2x2 crop technique, S1.2 module #4) +
n03_brief.md (S3 the 2x2 crop seam + TenantImageStore). Pure PIL; NO network; NO live key.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# --------------------------------------------------------------------------- #
# Module constants.
# --------------------------------------------------------------------------- #
# The default master generation size (plan S4.2: 2048x2048; Amazon wants 4000 for >=2000/crop).
DEFAULT_MASTER_SIZE = 2048

# The crop tolerance: a near-square composite (W//2 loses 1px on an odd dim) is fine; a
# composite whose sides differ by more than this fraction is rejected (n03 S3.6 risk #3).
MAX_NON_SQUARE_PCT = 2.0

# The quadrant -> scene label map (plan S4.2 the best-4 cells). Index order = TL, TR, BL, BR.
SCENE_LABELS: Tuple[str, str, str, str] = (
    "HERO_TRUST",        # top-left  -- highest conversion (cell 1; mandatory)
    "MARKETPLACE_READY",  # top-right -- compliance, pure white #FFFFFF (cell 9; immutable)
    "IN_CONTEXT",        # bot-left  -- lifestyle (cell 5)
    "BENEFIT_MACRO",      # bot-right -- proof anchor (cell 6)
)

# The default 2x2 generation prompt scaffold (plan S4.2). The caller's product prompt is woven
# in; the negative-prompt guidance reduces gutter/separator lines (the crop's #1 risk).
_PROMPT_SCAFFOLD = (
    "A 2x2 grid, each cell a SEPARATE product scene, seamless, NO borders, NO grid lines, NO "
    "separator lines, NO text, equal-sized cells. All 4 cells show the EXACT same product. "
    "Top-right cell ONLY: pure white #FFFFFF background, 85%% product fill (marketplace-ready). "
    "Product: %s"
)


# --------------------------------------------------------------------------- #
# Errors.
# --------------------------------------------------------------------------- #
class ImageGridError(RuntimeError):
    """Raised when the 2x2 pipeline cannot proceed (no generator bound / Pillow missing /
    a generator failure). FAIL-CLOSED + ACTIONABLE: the message says exactly what to fix. NEVER
    a fabricated image, NEVER a silent empty result."""


# --------------------------------------------------------------------------- #
# THE entry: generate ONE 2x2 -> crop into 4 tiles -> names + manifest.
# --------------------------------------------------------------------------- #
def generate_and_crop(
    prompt: str,
    *,
    generator: Optional[Callable[..., Any]],
    out_dir: str,
    base_name: str,
    tenant_id: str,
    master_size: int = DEFAULT_MASTER_SIZE,
    gutter_px: int = 0,
    scene_labels: Tuple[str, str, str, str] = SCENE_LABELS,
) -> List[str]:
    """Generate ONE square 2x2 composite and crop it into 4 tile paths (plan S4.2). See module
    docstring.

    Args:
      prompt       -- the product/scene prompt (woven into the 2x2 grid scaffold).
      generator    -- the INJECTED image-generation seam (founder-gated; None -> ImageGridError).
                      Signature: generator(prompt, *, size, tenant_id) -> PIL.Image | path str.
      out_dir      -- the per-tenant output directory (created if absent).
      base_name    -- the tile basename: tiles are ``{base_name}_scene{1..4}.png``.
      tenant_id    -- EXPLICIT tenant id (passed to the generator; never inferred from ambient).
      master_size  -- the square master generation size (default 2048; plan S4.2).
      gutter_px    -- optional inner-gutter trim per tile (if the model drew separators; n03 S3.6).
      scene_labels -- the 4 quadrant scene labels (TL, TR, BL, BR).

    Returns the 4 tile paths (absolute, as strings), in TL, TR, BL, BR order. ALSO writes a
    ``{base_name}_manifest.json`` next to the tiles (the per-tile scene labels + the C2PA-style
    provenance note for the master generation).

    FAIL-CLOSED: generator None -> ImageGridError. DEGRADE-NEVER: a non-square / too-small
    composite -> ValueError (never distort); Pillow missing -> ImageGridError (actionable)."""
    tid = (tenant_id or "").strip()
    if not tid:
        raise ImageGridError("tenant_id is required (explicit, never ambient) for image generation.")
    if generator is None:
        raise ImageGridError(
            "no image generator bound: generate_and_crop needs an injected ``generator`` "
            "(the founder-gated live image API seam). Bind one to enable image generation; "
            "no fabricated image is ever produced."
        )

    Image = _load_pillow()  # ImageGridError if Pillow is absent (actionable).
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    base = _safe_base(base_name)

    full_prompt = _PROMPT_SCAFFOLD % (prompt or "").strip()

    # -- STEP 1 GENERATE: call the injected seam (founder-gated; no live key here). --------
    composite = _invoke_generator(generator, full_prompt, master_size, tid, Image)

    # -- STEP 2-3 CROP + NAME: 4 equal quadrant tiles at the 50/50 lines, saved as PNG. ----
    tile_paths = crop_2x2(composite, str(out), base, gutter_px=gutter_px)

    # -- STEP 4 MANIFEST: per-tile scene labels + the C2PA-style provenance note. ----------
    manifest = _build_manifest(tile_paths, scene_labels, tid, full_prompt, composite)
    manifest_path = out / ("%s_manifest.json" % base)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="ascii")

    return tile_paths


# --------------------------------------------------------------------------- #
# THE crop (PURE PIL): square WxW 2x2 -> [TL, TR, BL, BR] at the 50/50 lines.
# --------------------------------------------------------------------------- #
def crop_2x2(
    composite: Any,
    out_dir: str,
    base_name: str,
    *,
    gutter_px: int = 0,
    fmt: str = "PNG",
) -> List[str]:
    """Crop ONE square 2x2 composite into 4 equal tiles (plan S4.2 the Python crop). PURE PIL.

    Accepts a PIL.Image.Image OR a path str (loaded lazily). Slices at the 50/50 lines:
      tl=(0,0,half,half)  tr=(half,0,W,half)  bl=(0,half,H... )  br=(half,half,W,H)
    Saves ``{base_name}_scene{1..4}.{ext}`` under out_dir; returns the 4 paths (TL,TR,BL,BR).

    gutter_px>0 trims an inner gutter from each tile (if the model drew separator lines between
    cells -- n03 S3.6 risk #1). A non-square composite (sides differ > MAX_NON_SQUARE_PCT) ->
    ValueError (NEVER silently distort -- n03 S3.6 risk #3). DEGRADE-NEVER: Pillow absent ->
    ImageGridError (actionable, not a deep ImportError)."""
    Image = _load_pillow()
    img = _as_image(composite, Image)

    w, h = img.size
    if w <= 1 or h <= 1:
        raise ValueError("2x2 composite too small to crop: size=%sx%s" % (w, h))
    # Square check (a 1px odd-dim loss is fine; a real non-square is rejected).
    longer, shorter = (max(w, h), min(w, h))
    if shorter == 0 or ((longer - shorter) / float(shorter)) * 100.0 > MAX_NON_SQUARE_PCT:
        raise ValueError(
            "2x2 composite is not square (got %sx%s, tolerance %.1f%%); a 2x2 grid MUST be "
            "square so the 50/50 crop yields equal tiles -- refusing to distort." % (w, h, MAX_NON_SQUARE_PCT)
        )

    half_w = w // 2
    half_h = h // 2
    g = max(0, int(gutter_px))
    # The 4 quadrant boxes (gutter trims INWARD from the shared edges -- n03 S3.6 gutter trim).
    boxes = [
        (0 + g, 0 + g, half_w - g, half_h - g),         # TL
        (half_w + g, 0 + g, w - g, half_h - g),          # TR
        (0 + g, half_h + g, half_w - g, h - g),          # BL
        (half_w + g, half_h + g, w - g, h - g),          # BR
    ]

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    base = _safe_base(base_name)
    ext = _ext_for_fmt(fmt)

    paths: List[str] = []
    for idx, box in enumerate(boxes, start=1):
        tile = img.crop(box)
        tile_path = out / ("%s_scene%d.%s" % (base, idx, ext))
        tile.save(str(tile_path), fmt)
        paths.append(str(tile_path.resolve()))
    return paths


# --------------------------------------------------------------------------- #
# GENERATE -- invoke the injected seam, normalize to a PIL Image.
# --------------------------------------------------------------------------- #
def _invoke_generator(
    generator: Callable[..., Any],
    prompt: str,
    master_size: int,
    tenant_id: str,
    Image: Any,
) -> Any:
    """Call the injected generator (founder-gated) and normalize the return to a PIL Image.

    Signature contract: generator(prompt, *, size, tenant_id) -> PIL.Image.Image | path str.
    DEGRADE-NEVER: a generator that raises -> ImageGridError (the run never crashes opaquely);
    a generator returning None / an empty path -> ImageGridError (never a fabricated image)."""
    try:
        produced = generator(prompt, size=master_size, tenant_id=tenant_id)
    except TypeError:
        # A generator with a simpler signature (prompt only) is still honored (degrade-never).
        produced = generator(prompt)
    except Exception as exc:
        raise ImageGridError("image generator failed: %s: %s" % (type(exc).__name__, exc))

    if produced is None:
        raise ImageGridError("image generator returned nothing (no image produced; not fabricating one).")
    return _as_image(produced, Image)


# --------------------------------------------------------------------------- #
# MANIFEST -- per-tile scene labels + ONE C2PA-style provenance note (plan S4.2).
# --------------------------------------------------------------------------- #
def _build_manifest(
    tile_paths: List[str],
    scene_labels: Tuple[str, str, str, str],
    tenant_id: str,
    prompt: str,
    composite: Any,
) -> Dict[str, Any]:
    """Build the small manifest: each tile's scene label + a single C2PA-style provenance note
    for the MASTER generation (ai_generated:true). The dashboard surfaces the AI-image label
    from this (plan S4.2 / n03 S3). NEVER carries a secret."""
    try:
        w, h = composite.size
        master_dims = "%sx%s" % (w, h)
    except Exception:
        master_dims = ""
    tiles = []
    for idx, path in enumerate(tile_paths):
        label = scene_labels[idx] if idx < len(scene_labels) else ("scene%d" % (idx + 1))
        tiles.append({"index": idx + 1, "scene": label, "path": path})
    return {
        "tenant_id": tenant_id,
        "technique": "2x2_generate_then_crop",
        "tile_count": len(tile_paths),
        "tiles": tiles,
        # ONE C2PA-style provenance note for the master generation (plan S4.2: ai_generated_flag
        # + c2pa_manifest; the visible "AI-generated image" label is derived from this).
        "provenance": {
            "ai_generated": True,
            "c2pa_action": "c2pa.created",
            "generator": "founder_gated_image_seam",
            "master_size": master_dims,
            "prompt_excerpt": _ascii_excerpt(prompt, 200),
            "label": "AI-generated image",
        },
    }


# --------------------------------------------------------------------------- #
# Pillow loading + image coercion (lazy, degrade-never).
# --------------------------------------------------------------------------- #
def _load_pillow() -> Any:
    """Lazy-import PIL.Image (the cex_motion_render.py:42 pattern). ImageGridError (ACTIONABLE)
    if Pillow is absent -- never a deep ImportError."""
    try:
        from PIL import Image  # type: ignore[import]

        return Image
    except Exception as exc:
        raise ImageGridError(
            "Pillow is required for the 2x2 crop but is not importable (%s). Install it: "
            "pip install Pillow>=10.0" % exc
        )


def _as_image(value: Any, Image: Any) -> Any:
    """Coerce a generator return (a PIL Image OR a path str) into a loaded PIL Image. TOTAL:
    a missing path -> ImageGridError (actionable)."""
    # A PIL Image duck-types via .crop + .size; accept it directly.
    if hasattr(value, "crop") and hasattr(value, "size"):
        return value
    if isinstance(value, (str, Path)):
        p = Path(value)
        if not p.is_file():
            raise ImageGridError("2x2 composite path does not exist: %s" % p)
        try:
            img = Image.open(str(p))
            img.load()  # force-read so a later crop does not hit a lazy-load error.
            return img
        except Exception as exc:
            raise ImageGridError("could not open 2x2 composite %s: %s" % (p, exc))
    raise ImageGridError(
        "generator must return a PIL.Image.Image or a path str; got %s" % type(value).__name__
    )


# --------------------------------------------------------------------------- #
# Small helpers (PURE).
# --------------------------------------------------------------------------- #
def _safe_base(base_name: str) -> str:
    """A filesystem-safe basename (alnum + - _); defaults to 'image' if empty."""
    cleaned = "".join(c for c in str(base_name or "") if c.isalnum() or c in "-_")
    return cleaned or "image"


def _ext_for_fmt(fmt: str) -> str:
    f = (fmt or "PNG").upper()
    if f in ("JPG", "JPEG"):
        return "jpg"
    if f == "PNG":
        return "png"
    return f.lower()


def _ascii_excerpt(text: str, limit: int) -> str:
    s = str(text or "").encode("ascii", "ignore").decode("ascii")
    s = " ".join(s.split())
    return s[:limit]


__all__ = [
    "generate_and_crop",
    "crop_2x2",
    "ImageGridError",
    "SCENE_LABELS",
    "DEFAULT_MASTER_SIZE",
    "MAX_NON_SQUARE_PCT",
]
