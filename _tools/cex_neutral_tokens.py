#!/usr/bin/env python3
# -*- coding: ascii -*-
"""cex_neutral_tokens -- the ONE canonical NEUTRAL design-token baseline (council MEDIUM debt).

THE single source of truth for the 24-token NEUTRAL baseline -- the degrade-never look every
tenant surface falls back to when a brand token is absent or malformed. Before this module the
full 24-token literal was COPIED into three places (cex_product_ad_mold, cex_brand_context,
cex_brand_writeback); the council flagged the triplication. They now all IMPORT _NEUTRAL_TOKENS
from here, so the baseline is defined exactly ONCE.

The values are keyed by the SAME 24 token keys as the moldgen token contract
(cex_moldgen_emit.TOKEN_KEYS / TOKEN_TO_CSSVAR): 23 HSL triplets "H S% L%" + ``radius`` a CSS
length. They are the values the former hand-maintained fallbacks shipped -- byte-identical, so
this dedup is a ZERO behavior change (the importers resolve the same 24 tokens they did before).

PURE + side-effect-free: a single frozen-by-convention dict literal, no IO / no clock / no import
of anything heavy. ASCII-only per .claude/rules/ascii-code-rule.md (the values are HSL/length
strings -- no diacritics).
"""
from __future__ import annotations

from typing import Dict

# THE neutral baseline -- the degrade-never design-system. Keyed by the 24 moldgen token keys
# (cex_moldgen_emit.TOKEN_TO_CSSVAR). A resolver (the product_ad mold's _resolve_brand_tokens,
# cex_brand_context._resolve_tokens, cex_brand_writeback._tokens_from_palette) overlays a
# tenant's VALIDATED tokens on top of these and always emits a COMPLETE 24-key set. With no
# tenant tokens the surface renders in exactly this neutral look (unchanged).
#
# Treat as READ-ONLY: importers do ``dict(_NEUTRAL_TOKENS)`` before mutating so this canonical
# table is never aliased/mutated.
_NEUTRAL_TOKENS: Dict[str, str] = {
    "background": "0 0% 100%",
    "foreground": "213 47% 12%",
    "card": "0 0% 98%",
    "cardForeground": "213 47% 12%",
    "popover": "0 0% 100%",
    "popoverForeground": "213 47% 12%",
    "primary": "174 68% 40%",
    "primaryForeground": "0 0% 100%",
    "secondary": "213 35% 18%",
    "secondaryForeground": "0 0% 100%",
    "muted": "210 20% 96%",
    "mutedForeground": "213 15% 45%",
    "accent": "174 68% 40%",
    "accentForeground": "0 0% 100%",
    "border": "210 20% 88%",
    "input": "210 20% 88%",
    "ring": "174 68% 40%",
    "brand": "174 68% 40%",
    "brandForeground": "0 0% 100%",
    "brandMuted": "174 30% 92%",
    "highlight": "42 100% 50%",
    "highlightForeground": "0 0% 10%",
    "highlightMuted": "42 80% 93%",
    "radius": "0.625rem",
}

__all__ = ["_NEUTRAL_TOKENS"]
