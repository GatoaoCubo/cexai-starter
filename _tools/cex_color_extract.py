#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI color extractor -- dominant-palette tool for the any-media input contract.

THE GAP (mission BRANDBOOK, Cell A): a tenant gives the dashboard a brand image (a logo,
a product photo, a moodboard). A capability that builds a brandbook needs the DOMINANT
COLORS of that image to visualize a palette. No PNG->palette tool existed; this is it.

THE SEAM: ``extract_palette(image_bytes) -> [{hex, rgb, name, weight}]`` -- the input
resolver (cex_run_capability) calls this when a typed input field of type ``file`` carries
an uploaded IMAGE (a data: URI), and hands the result to the generator as
``inputs[<key>_palette]`` (see _docs/specs/spec_input_contract.md). The list is sorted by
``weight`` (the fraction of the image that color covers), most-dominant first.

PURE + TOTAL + DEGRADE-NEVER:
  * No network, no disk (operates on in-memory bytes); the CLI is the only file reader.
  * Pillow (PIL) is the ONLY heavy dep and it is imported LAZILY. If Pillow is absent, or
    the bytes are empty / not a decodable image, ``extract_palette`` returns ``[]`` and
    NEVER raises -- the caller surfaces an honest empty palette, never a crash. Use
    ``palette_note(image_bytes)`` for a human one-line reason when the list is empty.

ASCII-only per .claude/rules/ascii-code-rule.md (color NAMES are a fixed ASCII anchor set).
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

__all__ = [
    "extract_palette",
    "palette_note",
    "pillow_available",
    "PILLOW_AVAILABLE",
]

# How small we shrink the image before quantizing (speed; the palette is unaffected by a
# down-sample for dominant-color purposes). Square cap -- the thumbnail keeps the aspect.
_THUMB_MAX = 128

# Default number of palette swatches to return. A brandbook rarely needs more than ~6.
_DEFAULT_MAX_COLORS = 6

# Fixed ASCII color-name anchors. extract_palette names each swatch by the nearest anchor
# (squared-RGB distance). A coarse, human-friendly label -- NOT a precise color science
# name; the ``hex``/``rgb`` are the exact values, ``name`` is just a readable hint.
_NAMED_ANCHORS: Tuple[Tuple[str, Tuple[int, int, int]], ...] = (
    ("black", (0, 0, 0)),
    ("white", (255, 255, 255)),
    ("gray", (128, 128, 128)),
    ("silver", (200, 200, 200)),
    ("red", (220, 20, 20)),
    ("maroon", (128, 0, 0)),
    ("orange", (255, 140, 0)),
    ("brown", (139, 69, 19)),
    ("beige", (245, 222, 179)),
    ("yellow", (240, 220, 20)),
    ("olive", (128, 128, 0)),
    ("lime", (60, 205, 60)),
    ("green", (0, 128, 0)),
    ("teal", (0, 128, 128)),
    ("cyan", (0, 200, 200)),
    ("blue", (40, 70, 210)),
    ("navy", (0, 0, 128)),
    ("purple", (128, 0, 128)),
    ("magenta", (220, 20, 220)),
    ("pink", (255, 150, 180)),
)


def pillow_available() -> bool:
    """True iff Pillow (PIL) can be imported. Lazy -- the import is attempted on call."""
    try:
        import PIL  # type: ignore[import]  # noqa: F401

        return True
    except Exception:
        return False


# Module-level convenience flag (resolved once at import; ``pillow_available()`` re-checks).
PILLOW_AVAILABLE: bool = pillow_available()


def _color_name(rgb: Tuple[int, int, int]) -> str:
    """Nearest ASCII anchor name for an RGB triple (squared-distance). TOTAL."""
    r, g, b = rgb
    best_name = "gray"
    best_dist = -1
    for name, (ar, ag, ab) in _NAMED_ANCHORS:
        dist = (r - ar) ** 2 + (g - ag) ** 2 + (b - ab) ** 2
        if best_dist < 0 or dist < best_dist:
            best_dist = dist
            best_name = name
    return best_name


def _hex(rgb: Tuple[int, int, int]) -> str:
    """#rrggbb (lowercase) for an RGB triple, clamped to 0..255. TOTAL."""
    r, g, b = (max(0, min(255, int(c))) for c in rgb)
    return "#%02x%02x%02x" % (r, g, b)


def extract_palette(
    image_bytes: bytes,
    max_colors: int = _DEFAULT_MAX_COLORS,
) -> List[Dict[str, object]]:
    """Dominant colors of an image as ``[{hex, rgb, name, weight}]``, weight-sorted desc.

    ``weight`` is the fraction (0..1, 4dp) of the down-sampled image that swatch covers; the
    list is most-dominant first. ``rgb`` is ``[r, g, b]`` (ints 0..255); ``name`` is the
    nearest ASCII anchor (a readable hint, not exact).

    DEGRADE-NEVER + TOTAL: returns ``[]`` (never raises) when Pillow is absent, the bytes are
    empty, or they do not decode as an image. Use ``palette_note`` for the human reason.
    """
    if not image_bytes:
        return []
    try:
        n = int(max_colors)
    except (TypeError, ValueError):
        n = _DEFAULT_MAX_COLORS
    if n < 1:
        n = 1
    if n > 64:
        n = 64

    try:
        from io import BytesIO
        from PIL import Image  # type: ignore[import]
    except Exception:
        return []

    try:
        img = Image.open(BytesIO(image_bytes))
        # RGBA/P/LA/CMYK -> RGB so the palette math is over 3 channels (alpha is dropped --
        # dominant color is about the visible pixels; a transparent PNG still yields its inks).
        img = img.convert("RGB")
        # Down-sample for speed; the dominant palette is stable under a thumbnail.
        img.thumbnail((_THUMB_MAX, _THUMB_MAX))
        # Median-cut quantize to <= n representative colors, then count pixels per swatch.
        quant = img.quantize(colors=n, method=Image.MEDIANCUT)
        flat_palette = quant.getpalette() or []
        counts = quant.getcolors() or []  # [(pixel_count, palette_index), ...]
    except Exception:
        return []

    total = 0
    for count, _idx in counts:
        total += int(count)
    if total <= 0:
        return []

    out: List[Dict[str, object]] = []
    for count, idx in sorted(counts, key=lambda c: c[0], reverse=True):
        base = int(idx) * 3
        if base + 2 >= len(flat_palette):
            continue
        rgb = (
            int(flat_palette[base]),
            int(flat_palette[base + 1]),
            int(flat_palette[base + 2]),
        )
        out.append(
            {
                "hex": _hex(rgb),
                "rgb": [rgb[0], rgb[1], rgb[2]],
                "name": _color_name(rgb),
                "weight": round(int(count) / total, 4),
            }
        )
        if len(out) >= n:
            break
    return out


def palette_note(image_bytes: bytes) -> Optional[str]:
    """A one-line HONEST reason a palette is empty, or None when extraction should work.

    Lets the caller surface "no palette: Pillow not installed" / "...not a decodable image"
    instead of a silent empty list. Returns None when Pillow is present and the bytes are a
    non-empty image candidate (extraction is expected to succeed)."""
    if not image_bytes:
        return "no palette: empty image payload"
    if not pillow_available():
        return "no palette: Pillow (PIL) is not installed in this runtime"
    if not extract_palette(image_bytes):
        return "no palette: the payload did not decode as an image"
    return None


# --------------------------------------------------------------------------- #
# CLI -- ``python cex_color_extract.py <image_path> [max_colors]`` prints JSON. #
# --------------------------------------------------------------------------- #
def _main(argv: List[str]) -> int:
    import json

    if not argv:
        print("usage: cex_color_extract.py <image_path> [max_colors]")
        return 2
    path = argv[0]
    max_colors = _DEFAULT_MAX_COLORS
    if len(argv) > 1:
        try:
            max_colors = int(argv[1])
        except ValueError:
            pass
    try:
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError as exc:
        print("cannot read %r: %s" % (path, exc))
        return 1
    palette = extract_palette(data, max_colors=max_colors)
    if not palette:
        note = palette_note(data) or "no palette"
        print(json.dumps({"palette": [], "note": note}, ensure_ascii=True))
        return 0
    print(json.dumps({"palette": palette}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(_main(sys.argv[1:]))
