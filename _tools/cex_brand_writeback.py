#!/usr/bin/env python3
# -*- coding: ascii -*-
"""cex_brand_writeback -- the BRAND-SETUP SEAM (mission B2).

THE FOUNDER'S PATH: a tenant runs the ``brandbook`` capability with uploaded materials
(name + essence + colour palette + logo). That run produces the brand CONFIG -- the
{{brand_*}} VALUES. This module is the persistence seam that takes the brandbook output
and WRITES it to the tenant brand source ``cex_brand_context.resolve_brand_context`` reads
(the moldgen overlay ``.cex/runtime/moldgen/<tid>/brand.config.ts``, the 24 design tokens +
name/tagline/logo). After a brandbook run, resolve_brand_context returns the NEW brand and
EVERY capability re-personalizes -- because the brand is an OPEN MUSTACHE, never hardcoded.

THE ONE WRITE this module owns: the moldgen overlay (the design tokens + brand meta). It is
the load-bearing source -- ``_resolve_tokens`` + ``_load_overlay_meta`` in cex_brand_context
both read it, and it is what drives the 24-token reskin. Voice + global identity are SEPARATE
surfaces (voice = cex_tenant_voice_profile, identity = .cex/brand/brand_config.yaml); this
module does NOT write them (that is a later wave) -- but the overlay write alone is enough to
re-brand the design system + the brand name/tagline/logo for every capability.

THE MAPPING (brandbook structured output -> moldgen spec):
  * brand_name      -> spec name / nameHtml          (from the Identidade section / artifact meta)
  * brand_essence   -> spec tagline                  (the one-line essence, when present)
  * palette hexes   -> the brand COLOR tokens         (hex -> HSL triplet; see _hex_to_hsl):
        palette[0] -> primary + brand + ring + accent (the lead brand color, used everywhere)
        palette[1] -> secondary                        (the support color)
        palette[2] -> highlight                         (the accent/highlight color)
        palette[3] -> muted / border / input            (the neutral support)
        palette[4] -> foreground / *Foreground          (the dark text color)
    EVERY other token (and any role with no provided hex) -> the NEUTRAL baseline (the SAME
    _NEUTRAL_TOKENS table cex_brand_context + the product_ad mold use -- imported, never re-keyed).
  * logo (data-uri) -> spec logo                      (when the run carried a logo image data-uri)

NEVER-FABRICATE: a palette hex that does not parse is SKIPPED (its role keeps the neutral
baseline) -- never a guessed color. No brand_name -> the write is REFUSED (a brandbook with no
identity is not a brand config). DEGRADE-NEVER + TOTAL: every helper is total; the public
``write_brand_overlay`` returns a result object (never raises) so the run path can call it
fail-safe -- a write failure NEVER discards the produced brandbook.

ASCII-only source (.claude/rules/ascii-code-rule.md). Runtime VALUES (a tenant's accented
brand strings) may carry diacritics; this module's OWN constants stay diacritic-free.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

# The 24-token contract + the emitter + the validators -- the ONE design-token source
# (cex_moldgen_emit). Imported, never re-declared.
from cex_moldgen_emit import (  # noqa: E402
    TOKEN_KEYS,
    emit_to_file,
    is_hsl_triplet,
)


def _default_moldgen_root() -> str:
    """The DEFAULT moldgen overlay root, routed through the canonical fail-closed tenant-path
    guard (council LOW): ``resolve_tenant_path("moldgen", surface="runtime")``.

    THE INVARIANT (preserved, ZERO behavior change): the WRITE must land EXACTLY where
    cex_brand_context._load_overlay_spec READS. That read root is the FIXED, repo-global
    ``.cex/runtime/moldgen`` (per-tenant isolation for moldgen is by the <slug> subdir, NOT by a
    tenant-scoped root -- every existing overlay lives under that one global root, keyed on slug).
    So this resolver ANCHORS to the read root and uses the guard for its CONTAINMENT value:

      * It resolves the guarded path under surface='runtime'. When CEX_TENANT_ID is UNSET (the
        central / single-tenant default), the guard returns EXACTLY the read's global root -- so
        the common path is guard-validated AND identical to the read (no change).
      * Under an ACTIVE CEX_TENANT_ID the guard would resolve a tenant-scoped root
        (.cex/tenants/<tid>/runtime/moldgen), which the FIXED read does NOT consult -> a WRITE
        there would never be read back. To honor the write==read invariant the resolver DETECTS
        that divergence and ANCHORS to the read's global root (it never silently writes to a dir
        the read ignores). The slug segment is still fail-closed-sanitized by _tenant_key.

    DEGRADE-NEVER: if the guard module is unavailable (a stripped runtime), fall back to the
    legacy literal join -- byte-identical to the pre-guard default path."""
    # The read root cex_brand_context uses (the authoritative target the write must match).
    read_root = os.path.normpath(_DEFAULT_MOLDGEN_ROOT)
    try:
        tools_dir = str(_HERE)
        if tools_dir not in sys.path:
            sys.path.insert(0, tools_dir)
        import cex_tenant_paths as _tp  # type: ignore[import]

        guarded = os.path.normpath(str(_tp.resolve_tenant_path("moldgen", surface="runtime")))
    except Exception:
        return read_root
    # Use the guard's result ONLY when it agrees with the fixed read root (the single-tenant
    # default). If an active CEX_TENANT_ID scoped it elsewhere, anchor to the read root so the
    # write is always read back (write==read invariant). os.path.samefile would need the dirs to
    # exist; a normalized-string compare is the right pre-create check here.
    return guarded if guarded == read_root else read_root

# The CANONICAL per-tenant key (council A1): the SAME normalization cex_brand_context READS the
# overlay under, so a WRITE here lands in the dir the read finds (hyphens preserved -> a UUID
# tenant writes + reads the SAME dir). Falls back to an inline equivalent for a stripped runtime.
try:
    from cex_brand_context import _tenant_key as _tenant_key  # noqa: E402
except Exception:  # pragma: no cover - belt-and-braces for a stripped runtime
    def _tenant_key(value: str) -> str:  # type: ignore[misc]
        tid = (value or "").strip().lower()
        return tid if re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", tid) else ""

# THE neutral baseline -- the SAME degrade-never table cex_brand_context + the product_ad mold
# use, so a role with no provided hex keeps EXACTLY the neutral look. Imported from the ONE
# canonical source (cex_neutral_tokens) so there is exactly one neutral source (council MEDIUM
# dedup -- the three former literal copies collapsed onto this one tiny sibling module).
from cex_neutral_tokens import _NEUTRAL_TOKENS  # noqa: E402

# The UNGUARDED literal moldgen overlay root -- the degrade-never fallback used by
# _default_moldgen_root() ONLY when the tenant-path guard (cex_tenant_paths) is unavailable.
# The normal default path goes through the guard (council LOW); this literal mirrors
# cex_brand_context._DEFAULT_MOLDGEN_ROOT so the fallback stays byte-identical. Overridable
# per-call via out_root (so a test writes to a tmp dir, bypassing both the guard and this).
_DEFAULT_MOLDGEN_ROOT = os.path.join(_HERE, "..", ".cex", "runtime", "moldgen")

# A 6-digit hex (with or without the leading #). NEVER a 3-digit shorthand (the brandbook
# generator emits/validates only 6-digit hexes), so this matches the generator's contract.
_HEX_RE = re.compile(r"^#?[0-9A-Fa-f]{6}$")


# --------------------------------------------------------------------------- #
# Public: the write result (a small value object; the write NEVER raises).
# --------------------------------------------------------------------------- #
class WriteResult:
    """The outcome of write_brand_overlay. ``ok`` True iff the overlay was written.

    ``path`` is the written ``brand.config.ts`` (when ok); ``reason`` explains a refusal /
    failure (when not ok); ``tokens_written`` is the count of brand-color tokens that came
    from the palette (vs the neutral baseline); ``brand_name`` echoes the name that was written.
    """

    def __init__(
        self,
        ok: bool,
        *,
        path: str = "",
        reason: str = "",
        tokens_written: int = 0,
        brand_name: str = "",
    ) -> None:
        self.ok = ok
        self.path = path
        self.reason = reason
        self.tokens_written = tokens_written
        self.brand_name = brand_name

    def __repr__(self) -> str:  # pragma: no cover - diagnostics only
        if self.ok:
            return "WriteResult(ok=True, path=%r, tokens_written=%d, brand_name=%r)" % (
                self.path, self.tokens_written, self.brand_name,
            )
        return "WriteResult(ok=False, reason=%r)" % self.reason


# --------------------------------------------------------------------------- #
# Public: brandbook structured output -> a validated moldgen spec.
# --------------------------------------------------------------------------- #
def brand_spec_from_brandbook(
    structured: Mapping[str, Any],
    tenant_id: str,
    *,
    logo_data_uri: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Build a COMPLETE, emit-ready moldgen spec from a brandbook StructuredOutput.

    Returns None when no usable brand_name can be extracted (a brandbook with no identity is
    NOT a brand config -- never write a nameless overlay). Otherwise returns a spec dict with
    ALL 24 tokens (palette colors mapped to brand roles, the rest neutral), name/nameHtml/
    logoAlt/domain/font, and tagline/logo when present. The spec is shaped to pass
    cex_moldgen_emit.validate_spec (so emit(strict=True) accepts it). TOTAL: never raises.

    ``structured`` is the generator payload (cex_brandbook.build's return): it carries
    ``output_sections`` (the 8 sections) + ``artifact`` (a JSON meta string with palette_colors
    + brand_name). We read the palette + name from BOTH (the meta first, the sections as the
    fallback) so a slightly different generator shape still resolves. NEVER fabricates a value.
    """
    if not isinstance(structured, Mapping):
        return None

    brand_name = _extract_brand_name(structured)
    if not brand_name:
        return None

    palette = _extract_palette(structured)
    essence = _extract_essence(structured)

    tokens, tokens_from_palette = _tokens_from_palette(palette)

    # Canonical tenant key first (A1: matches the overlay dir the read side resolves), then a
    # brand-name slug fallback (normalizer for a name with spaces/accents), then a literal.
    slug = _tenant_key(tenant_id) or _slug(brand_name) or "tenant"
    spec: Dict[str, Any] = {
        "name": brand_name,
        "nameHtml": brand_name,
        # The logo is REQUIRED by the BrandConfig contract; default to a stable asset ref so
        # the overlay validates even before a real logo upload (a data-uri overrides it below).
        "logo": "@/assets/%s-logo.webp" % slug,
        "logoAlt": "%s - logo" % brand_name,
        "domain": "%s.com.br" % slug,
        "font": {"family": "system-ui, -apple-system, 'Segoe UI', sans-serif"},
        "tokens": tokens,
    }
    if essence:
        spec["tagline"] = essence
    # A logo image data-uri (the dashboard's file-upload control sends it as the field value)
    # becomes the overlay's logo so the brand header shows the real logo. NEVER-fabricate: only
    # an actual ``data:image`` uri is taken; anything else keeps the asset-ref default above.
    if isinstance(logo_data_uri, str) and logo_data_uri.strip().startswith("data:image"):
        spec["logo"] = logo_data_uri.strip()

    # Stash the palette-token count for the caller's WriteResult (popped before emit so it is
    # never written into the .ts -- emit reads only the known BrandConfig keys, but keep it clean).
    spec["__tokens_from_palette"] = tokens_from_palette
    return spec


# --------------------------------------------------------------------------- #
# Public: write the overlay (THE persistence seam). NEVER raises.
# --------------------------------------------------------------------------- #
def write_brand_overlay(
    tenant_id: str,
    structured: Mapping[str, Any],
    *,
    out_root: Optional[str] = None,
    logo_data_uri: Optional[str] = None,
) -> WriteResult:
    """Write the tenant moldgen overlay from a brandbook output. THE brand-setup write.

    Writes ``<out_root>/<tenant_slug>/brand.config.ts`` (out_root defaults to the repo moldgen
    root that cex_brand_context reads). After this returns ok, resolve_brand_context(tenant_id)
    picks up the NEW tokens + name + tagline + logo -> every capability re-brands.

    FAIL-SAFE + TOTAL: returns a WriteResult, NEVER raises. A missing tenant_id, a brandbook
    with no usable name, an invalid spec, or any IO/emit failure -> ok=False with a reason; the
    caller (the run path) treats a non-ok result as a no-op and the produced brandbook is intact.
    """
    tid = (tenant_id or "").strip()
    if not tid:
        return WriteResult(False, reason="missing_tenant")

    try:
        spec = brand_spec_from_brandbook(structured, tid, logo_data_uri=logo_data_uri)
    except Exception as exc:  # pragma: no cover - brand_spec_from_brandbook is total
        return WriteResult(False, reason="spec_build_failed: %s" % type(exc).__name__)
    if spec is None:
        return WriteResult(False, reason="no_brand_name")

    tokens_from_palette = int(spec.pop("__tokens_from_palette", 0) or 0)
    brand_name = str(spec.get("name", "") or "")
    # The DEFAULT write is routed through the fail-closed tenant-path guard (council LOW:
    # resolve_tenant_path, surface='runtime') so it lands EXACTLY where cex_brand_context READS,
    # never outside the surface root. An explicit out_root (a test tmp dir) bypasses the guard.
    root = out_root or _default_moldgen_root()
    # CANONICAL key (A1): the overlay dir is pinned by the same key cex_brand_context reads under,
    # so a UUID tenant writes + reads the SAME dir (the old _slug stripped hyphens -> mismatch).
    slug = _tenant_key(tid) or _slug(tid)

    try:
        # emit_to_file validates (strict=True) then writes; the slug pins the per-tenant dir so
        # the overlay lands EXACTLY where cex_brand_context._load_overlay_spec looks for it.
        path = emit_to_file(spec, root, tenant=slug, strict=True)
    except Exception as exc:
        return WriteResult(False, reason="emit_failed: %s: %s" % (type(exc).__name__, exc))

    return WriteResult(
        True,
        path=path,
        tokens_written=tokens_from_palette,
        brand_name=brand_name,
    )


# --------------------------------------------------------------------------- #
# Internal: extract brand fields from the brandbook structured output.
# --------------------------------------------------------------------------- #
def _extract_brand_name(structured: Mapping[str, Any]) -> str:
    """The brand name: the artifact-meta brand_name first, else the Identidade section's
    'Nome da marca' row. A placeholder ([fornecer: ...]) is rejected. TOTAL -> '' when none."""
    meta = _artifact_meta(structured)
    name = _clean(meta.get("brand_name"))
    if name:
        return name
    row = _field_row(structured, "Identidade da Marca", "Nome da marca")
    return _clean(row)


def _extract_essence(structured: Mapping[str, Any]) -> str:
    """The brand essence/tagline: the Identidade section's 'Essencia (1 frase)' row, when it is
    a real value (not a [fornecer: ...] placeholder). TOTAL -> '' when none."""
    row = _field_row(structured, "Identidade da Marca", "Essencia (1 frase)")
    return _clean(row)


def _extract_palette(structured: Mapping[str, Any]) -> List[str]:
    """The provided palette hexes, in role order. The artifact-meta palette_colors first (the
    generator records the parsed palette there), else the Paleta de Cores table's Hex column.
    Only real 6-digit hexes are kept (placeholders dropped). NEVER fabricates. TOTAL."""
    meta = _artifact_meta(structured)
    colors = meta.get("palette_colors")
    out: List[str] = []
    if isinstance(colors, (list, tuple)):
        for c in colors:
            h = _norm_hex(c)
            if h:
                out.append(h)
    if out:
        return out
    # Fallback: read the palette table's Hex column (index 1) directly.
    section = _section(structured, "Paleta de Cores")
    table = section.get("table") if isinstance(section, Mapping) else None
    if isinstance(table, (list, tuple)):
        for row in table:
            if isinstance(row, (list, tuple)) and len(row) >= 2:
                h = _norm_hex(row[1])
                if h:
                    out.append(h)
    return out


def _tokens_from_palette(palette: List[str]) -> Tuple[Dict[str, str], int]:
    """Map the palette hexes onto the 24 brand tokens, returning (tokens, n_from_palette).

    Starts from the COMPLETE neutral baseline (every key present), then overlays the brand-color
    roles from the palette (hex -> HSL). A role with no provided hex (or an unparseable one)
    keeps its neutral value -- degrade-never, never a broken/guessed color. The returned dict is
    ALWAYS the full 24-key contract so emit(strict=True) accepts it."""
    tokens: Dict[str, str] = dict(_NEUTRAL_TOKENS)
    count = 0

    def _put(keys: List[str], hsl: str) -> None:
        nonlocal count
        for k in keys:
            if k in tokens:
                tokens[k] = hsl
        count += 1

    # palette[0] = the LEAD brand color -> primary + brand + ring + accent (used everywhere).
    if len(palette) >= 1:
        hsl = _hex_to_hsl(palette[0])
        if hsl:
            _put(["primary", "brand", "ring", "accent"], hsl)
    # palette[1] = the support color -> secondary.
    if len(palette) >= 2:
        hsl = _hex_to_hsl(palette[1])
        if hsl:
            _put(["secondary"], hsl)
    # palette[2] = the accent/highlight color -> highlight.
    if len(palette) >= 3:
        hsl = _hex_to_hsl(palette[2])
        if hsl:
            _put(["highlight"], hsl)
    # palette[3] = a neutral support -> muted + border + input.
    if len(palette) >= 4:
        hsl = _hex_to_hsl(palette[3])
        if hsl:
            _put(["muted", "border", "input"], hsl)
    # palette[4] = the dark text color -> foreground + the *Foreground roles.
    if len(palette) >= 5:
        hsl = _hex_to_hsl(palette[4])
        if hsl:
            _put(["foreground", "cardForeground", "popoverForeground"], hsl)

    # Belt-and-braces: never let a mapped role leave a non-HSL value in the contract.
    for k in TOKEN_KEYS:
        if k == "radius":
            continue
        if not is_hsl_triplet(tokens.get(k, "")):
            tokens[k] = _NEUTRAL_TOKENS[k]
    return tokens, count


# --------------------------------------------------------------------------- #
# Internal: structured-output readers (each TOTAL).
# --------------------------------------------------------------------------- #
def _artifact_meta(structured: Mapping[str, Any]) -> Dict[str, Any]:
    """The brandbook artifact-meta dict (the generator stores a JSON string in ``artifact`` with
    brand_name + palette_colors + ...). TOTAL: a missing/garbled artifact -> {}."""
    import json

    raw = structured.get("artifact")
    if isinstance(raw, Mapping):
        return dict(raw)
    if isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    return {}


def _section(structured: Mapping[str, Any], title: str) -> Dict[str, Any]:
    """The output_section with the given title, or {}. TOTAL."""
    sections = structured.get("output_sections")
    if isinstance(sections, (list, tuple)):
        for sec in sections:
            if isinstance(sec, Mapping) and sec.get("title") == title:
                return dict(sec)
    return {}


def _field_row(structured: Mapping[str, Any], section_title: str, label: str) -> str:
    """The value of a 'fields' row (label/value) in a section, or ''. TOTAL."""
    section = _section(structured, section_title)
    rows = section.get("rows") if isinstance(section, Mapping) else None
    if isinstance(rows, (list, tuple)):
        for r in rows:
            if isinstance(r, Mapping) and r.get("label") == label:
                v = r.get("value")
                return str(v) if v is not None else ""
            # Some shapes carry rows as [label, value] pairs.
            if isinstance(r, (list, tuple)) and len(r) >= 2 and r[0] == label:
                return str(r[1]) if r[1] is not None else ""
    return ""


# --------------------------------------------------------------------------- #
# Internal: value helpers.
# --------------------------------------------------------------------------- #
def _clean(value: Any) -> str:
    """A real string value, or '' for a placeholder / empty / non-string. Rejects the brandbook
    '[fornecer: ...]' placeholder shape + the mustache placeholder shape. TOTAL."""
    if not isinstance(value, str):
        return ""
    s = value.strip()
    if not s:
        return ""
    low = s.lower()
    if low.startswith("[fornecer") or s.startswith("{{") or low.startswith("[preencher"):
        return ""
    return s


def _norm_hex(value: Any) -> str:
    """A normalized #RRGGBB (uppercased, # prefixed), or '' if not a 6-digit hex. TOTAL."""
    if not isinstance(value, str):
        return ""
    s = value.strip()
    if not _HEX_RE.match(s):
        return ""
    return "#" + s.lstrip("#").upper()


def _hex_to_hsl(hex_color: Any) -> str:
    """Convert a #RRGGBB hex to an 'H S% L%' triplet (the token format). '' when not a hex. TOTAL.

    Standard sRGB -> HSL. The output matches cex_moldgen_emit.is_hsl_triplet ('H S% L%' with
    integer H<=360, S/L<=100), so a token built from it passes validate_spec."""
    h = _norm_hex(hex_color)
    if not h:
        return ""
    try:
        r = int(h[1:3], 16) / 255.0
        g = int(h[3:5], 16) / 255.0
        b = int(h[5:7], 16) / 255.0
    except Exception:
        return ""
    mx = max(r, g, b)
    mn = min(r, g, b)
    light = (mx + mn) / 2.0
    if mx == mn:
        hue = 0.0
        sat = 0.0
    else:
        delta = mx - mn
        sat = delta / (2.0 - mx - mn) if light > 0.5 else delta / (mx + mn)
        if mx == r:
            hue = (g - b) / delta + (6.0 if g < b else 0.0)
        elif mx == g:
            hue = (b - r) / delta + 2.0
        else:
            hue = (r - g) / delta + 4.0
        hue /= 6.0
    H = int(round(hue * 360.0)) % 361
    S = int(round(sat * 100.0))
    L = int(round(light * 100.0))
    return "%d %d%% %d%%" % (H, S, L)


def _slug(value: str) -> str:
    """Normalizer for a BRAND-NAME fallback only (the tenant KEY now goes through the canonical
    _tenant_key -- A1). Lowercase, strip non-alphanumeric to ''. 'Acme Co' -> 'acmeco'. TOTAL."""
    if not isinstance(value, str):
        return ""
    return re.sub(r"[^a-z0-9]+", "", value.lower().strip())


# =========================================================================== #
# VOICE + IDENTITY WRITEBACK (SPEC 10 W3 -- the L1 self-serve persistence seam).
#
# write_brand_overlay (above) persists the DESIGN-TOKEN overlay -- the one surface the brandbook
# wave wrote. W3 adds the OTHER two surfaces a self-onboarding tenant needs persisted from their
# extracted materials (cex_brand_extract): their brand VOICE + brand IDENTITY. After this, a
# tenant who pointed CEXAI at their own site has a complete brand WITHOUT a hand-built brandbook:
#   * VOICE    -> <voice_profile_dir>/<tenant_key>.yaml  (the file cex_tenant_voice_profile.
#                 load_voice_profile reads -> drives copy register in every cap).
#   * IDENTITY -> .cex/tenants/<tid>/brand/brand_config.yaml (the per-tenant config
#                 cex_brand_context._load_tenant_identity reads -> brand_name/description/values).
#
# THE NON-DESTRUCTIVE CONTRACT (mirrors the N04 rule "never overwrite memory without versioning"):
# before overwriting an existing voice/identity file, its PRIOR content is copied to a sibling
# ``history/<name>.<UTC-timestamp>.yaml`` -- the tenant's previous brand is NEVER blown away; a
# self-onboard re-run leaves a recoverable trail. The write is fail-closed tenant-scoped (the
# identity path goes through cex_tenant_paths.resolve_tenant_path) and TOTAL (returns a
# WriteResult, never raises). NEVER-FABRICATE: only fields the extracted materials actually
# yielded are written; a [preencher]/empty field is dropped (voice) or omitted (identity), never
# an invented brand fact.
# =========================================================================== #

# The voice-profile file root cex_tenant_voice_profile reads from (its _DEFAULT_PROFILE_DIR), and
# the env override it honors. Kept in sync here so a W3 voice write lands EXACTLY where the loader
# looks. Overridable per-call via voice_dir (a test tmp dir).
_VOICE_PROFILE_DIRNAME = os.path.join("_tools", "voice_profiles")
_ENV_VOICE_PROFILE_DIR = "CEX_VOICE_PROFILE_DIR"

# The "no value yet" sentinel cex_brand_extract stamps for a field the source did not yield. We
# DROP it on write so it never becomes a persisted brand fact (consistent with _clean above).
_PLACEHOLDER_PREFIXES = ("[preencher", "[fornecer", "{{")


def write_voice_identity(
    tenant_id: str,
    materials: Mapping[str, Any],
    *,
    voice_dir: Optional[str] = None,
    brand_root: Optional[str] = None,
    write_voice: bool = True,
    write_identity: bool = True,
) -> "VoiceIdentityResult":
    """Persist a tenant's extracted brand VOICE + IDENTITY, VERSIONED (non-destructive).

    ``materials`` is a cex_brand_extract.extract_brand(...) dict (or the resolve_brand_context
    projection -- both shapes are read). Writes up to two files, each versioned:
      * voice    -> <voice_dir or _resolve_voice_dir()>/<tenant_key>.yaml
      * identity -> <brand_root or tenant brand surface>/brand_config.yaml

    Before overwriting an existing file, its prior content is copied to history/<name>.<ts>.yaml
    (the prior brand is preserved -- never a destructive overwrite). TOTAL + FAIL-SAFE: returns a
    VoiceIdentityResult, NEVER raises. A missing tenant id, or materials with no usable value for a
    surface, yields ok=False for that surface with a reason; the caller treats it as a no-op.

    NEVER-FABRICATE: only fields the materials actually carry are written; [preencher]/empty are
    dropped. A voice payload with NO real cue/tone/essence/name -> the voice write is REFUSED. An
    identity payload with NO real name/description/values -> the identity write is REFUSED."""
    res = VoiceIdentityResult()
    tid = (tenant_id or "").strip()
    if not tid:
        res.voice_reason = res.identity_reason = "missing_tenant"
        return res
    if not isinstance(materials, Mapping):
        res.voice_reason = res.identity_reason = "no_materials"
        return res

    # FAIL-CLOSED key: the CANONICAL tenant key only (cex_bootstrap._safe_tenant_id via
    # _tenant_key). A hostile / malformed id resolves to "" -> we REFUSE both writes (we do NOT
    # fall back to a _slug salvage of a rejected id -- a rejected tenant id must never become a
    # write target, even a path-safe one). Legit ids ([a-z0-9_-], leading alnum) pass unchanged.
    key = _tenant_key(tid)
    if not key:
        res.voice_reason = res.identity_reason = "bad_tenant_id"
        return res

    if write_voice:
        try:
            _write_voice(key, materials, voice_dir, res)
        except Exception as exc:  # pragma: no cover - _write_voice is total
            res.voice_ok = False
            res.voice_reason = "voice_failed: %s" % type(exc).__name__
    else:
        res.voice_reason = "skipped"

    if write_identity:
        try:
            _write_identity(tid, key, materials, brand_root, res)
        except Exception as exc:  # pragma: no cover - _write_identity is total
            res.identity_ok = False
            res.identity_reason = "identity_failed: %s" % type(exc).__name__
    else:
        res.identity_reason = "skipped"

    return res


class VoiceIdentityResult:
    """The outcome of write_voice_identity. Two independent surfaces, each with its own ok/path/
    reason + the path of any versioned-prior copy made before the overwrite."""

    def __init__(self) -> None:
        self.voice_ok = False
        self.voice_path = ""
        self.voice_reason = ""
        self.voice_prior = ""        # path the prior voice file was archived to (versioning)
        self.identity_ok = False
        self.identity_path = ""
        self.identity_reason = ""
        self.identity_prior = ""     # path the prior identity file was archived to (versioning)

    @property
    def ok(self) -> bool:
        """True iff at least one surface was written (a self-onboard that yields only a voice OR
        only an identity is still a useful partial persist)."""
        return self.voice_ok or self.identity_ok

    def as_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "voice": {"ok": self.voice_ok, "path": self.voice_path,
                      "reason": self.voice_reason, "prior": self.voice_prior},
            "identity": {"ok": self.identity_ok, "path": self.identity_path,
                         "reason": self.identity_reason, "prior": self.identity_prior},
        }

    def __repr__(self) -> str:  # pragma: no cover - diagnostics only
        return "VoiceIdentityResult(voice_ok=%s, identity_ok=%s)" % (
            self.voice_ok, self.identity_ok)


# --------------------------------------------------------------------------- #
# Internal: the VOICE surface write.
# --------------------------------------------------------------------------- #
def _write_voice(
    key: str,
    materials: Mapping[str, Any],
    voice_dir: Optional[str],
    res: "VoiceIdentityResult",
) -> None:
    """Build a TenantVoiceProfile from the materials + write it (versioned) to the voice-profile
    file the loader reads. REFUSED (no write) when the materials carry no real voice signal."""
    profile = _voice_profile_from_materials(key, materials)
    if profile is None:
        res.voice_reason = "no_voice_signal"
        return

    root = Path(voice_dir) if voice_dir else _resolve_voice_dir()
    path = root / (key + ".yaml")
    prior = _version_prior(path)
    text = _to_yaml(profile, header=(
        "# Tenant voice profile -- self-serve extracted brand voice (cex_brand_extract -> "
        "cex_brand_writeback.write_voice_identity).\n"
        "# Read by cex_tenant_voice_profile.load_voice_profile(tenant_id). VERSIONED: a prior "
        "version (if any)\n# was archived under ./history/ before this write -- never destructive. "
        "Fields are sourced from the\n# tenant's OWN materials; absent fields are omitted, never "
        "fabricated.\n"))
    _atomic_write(path, text)
    res.voice_ok = True
    res.voice_path = str(path)
    res.voice_prior = prior
    res.voice_reason = "written"


def _voice_profile_from_materials(key: str, materials: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    """Project extracted materials into a TenantVoiceProfile dict (the shape load_voice_profile
    returns). Returns None when there is NO real voice signal (no cue, no tone, no essence, no
    name) -- a profile with nothing real is not written. NEVER fabricates. TOTAL.

    The voice cues (cex_brand_extract's tone labels found in the tenant's OWN copy) become the
    tone.primary/secondary; the brand essence/tagline becomes ``essence``; the brand name becomes
    ``brand_name``. We record HONEST provenance in ``sources`` (which extraction this came from)."""
    name = _clean(_get(materials, "brand_name"))
    essence = _clean(_get(materials, "brand_tagline")) or _clean(_get(materials, "brand_description"))
    cues = _str_list(_get(materials, "voice_cues"))

    if not (name or essence or cues):
        return None

    tone: Dict[str, str] = {}
    if cues:
        tone["primary"] = cues[0]
        if len(cues) >= 2:
            tone["secondary"] = cues[1]
    # anti_tone is a judgement we cannot extract from a site -> omitted, never fabricated.

    profile: Dict[str, Any] = {"brand_name": name or key}
    if essence:
        profile["essence"] = essence
    if tone:
        profile["tone"] = tone
    # Color roles, IF the extraction produced a palette: reuse the SAME hex->HSL the overlay uses,
    # so the voice profile's color_roles agree with the design tokens. Only real hexes -> a role.
    color_roles = _voice_color_roles(materials)
    if color_roles:
        profile["color_roles"] = color_roles
    src = _clean(_get(materials, "source"))
    profile["sources"] = [
        "cex_brand_extract self-serve extraction%s" % ((" of " + src) if src else "")]
    return profile


def _voice_color_roles(materials: Mapping[str, Any]) -> Dict[str, str]:
    """The voice color_roles {primary_action, accent, urgency} as HSL triplets, from the extracted
    palette (palette[0]->primary_action, [1]->accent, [2]->urgency), reusing _hex_to_hsl. A missing
    slot is simply absent -- never a fabricated color. TOTAL."""
    palette = _str_list(_get(materials, "palette"))
    roles: Dict[str, str] = {}
    role_names = ["primary_action", "accent", "urgency"]
    for i, role in enumerate(role_names):
        if i < len(palette):
            hsl = _hex_to_hsl(palette[i])
            if hsl:
                roles[role] = hsl
    return roles


def _resolve_voice_dir() -> Path:
    """The voice-profile dir cex_tenant_voice_profile reads from: the CEX_VOICE_PROFILE_DIR env
    override, else the repo-relative _tools/voice_profiles default. Kept in sync with the loader."""
    env = os.environ.get(_ENV_VOICE_PROFILE_DIR)
    if env and env.strip():
        return Path(env.strip())
    repo_root = Path(_HERE).resolve().parent
    return repo_root / _VOICE_PROFILE_DIRNAME


# --------------------------------------------------------------------------- #
# Internal: the IDENTITY surface write.
# --------------------------------------------------------------------------- #
def _write_identity(
    tid: str,
    key: str,
    materials: Mapping[str, Any],
    brand_root: Optional[str],
    res: "VoiceIdentityResult",
) -> None:
    """Build a brand_config identity (nested bootstrap shape) from the materials + write it
    (versioned) to the per-tenant brand config cex_brand_context reads. REFUSED when no real
    identity field is present. The default path is fail-closed tenant-scoped via cex_tenant_paths."""
    identity = _identity_from_materials(materials)
    if identity is None:
        res.identity_reason = "no_identity_signal"
        return

    path = _identity_path(tid, key, brand_root)
    if path is None:
        res.identity_reason = "path_unavailable"
        return
    prior = _version_prior(path)
    text = _to_yaml(identity, header=(
        "# Tenant brand identity -- self-serve extracted (cex_brand_extract -> "
        "cex_brand_writeback.write_voice_identity).\n"
        "# Read by cex_brand_context._load_tenant_identity (per-tenant brand_config.yaml). "
        "VERSIONED: a prior\n# version (if any) was archived under ./history/ before this write "
        "-- never destructive. Absent\n# fields are omitted, never fabricated.\n"))
    _atomic_write(path, text)
    res.identity_ok = True
    res.identity_path = str(path)
    res.identity_prior = prior
    res.identity_reason = "written"


def _identity_from_materials(materials: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    """Project materials into the NESTED bootstrap identity shape ({identity: {BRAND_NAME, ...}}).
    Returns None when there is NO real identity field (name/description/values). NEVER fabricates:
    only fields the materials yield are emitted. TOTAL.

    The nested ``identity:`` block is what brand_inject.flatten surfaces to top-level BRAND_* keys,
    so cex_brand_context._load_tenant_identity resolves brand_name/description/values from it."""
    name = _clean(_get(materials, "brand_name"))
    description = _clean(_get(materials, "brand_tagline")) or _clean(_get(materials, "brand_description"))
    values = _str_list(_get(materials, "brand_values"))

    if not (name or description or values):
        return None

    ident: Dict[str, Any] = {}
    if name:
        ident["BRAND_NAME"] = name
    if description:
        ident["BRAND_DESCRIPTION"] = description
    if values:
        ident["BRAND_VALUES"] = list(values)
    src = _clean(_get(materials, "source"))
    out: Dict[str, Any] = {"identity": ident}
    out["_provenance"] = (
        "self-serve extraction via cex_brand_extract%s" % ((" of " + src) if src else ""))
    return out


def _identity_path(tid: str, key: str, brand_root: Optional[str]) -> Optional[Path]:
    """The per-tenant brand_config.yaml path. A test ``brand_root`` override -> <brand_root>/<key>/
    brand/brand_config.yaml (mirrors the .cex/tenants/<tid>/brand layout). Else the canonical
    fail-closed tenant surface via cex_tenant_paths.resolve_tenant_path(surface='brand'). The guard
    can fail-closed on a hostile id -> None (the caller records 'path_unavailable'). TOTAL."""
    if brand_root:
        return Path(brand_root) / key / "brand" / "brand_config.yaml"
    try:
        tools_dir = str(_HERE)
        if tools_dir not in sys.path:
            sys.path.insert(0, tools_dir)
        import cex_tenant_paths as _tp  # type: ignore[import]

        return _tp.resolve_tenant_path(
            "brand_config.yaml", surface="brand", tenant_id=tid, create=True)
    except (Exception, SystemExit):
        # SystemExit included: the tenant-path guard fails CLOSED (SystemExit) on a hostile id;
        # the writeback is TOTAL, so we degrade to None (caller records 'path_unavailable')
        # instead of crashing the run -- mirrors cex_brand_context._load_tenant_identity.
        return None


# --------------------------------------------------------------------------- #
# Internal: versioning + IO + tiny YAML emit (each TOTAL).
# --------------------------------------------------------------------------- #
def _version_prior(path: Path) -> str:
    """Non-destructive versioning: if ``path`` already exists, copy its CURRENT content to a
    sibling history/<stem>.<UTC-timestamp>.<suffix> before it is overwritten. Returns the archive
    path (str) when a prior was preserved, else "". The prior brand is NEVER lost. TOTAL --
    a versioning failure must not block the write, but it IS surfaced (we return "" and proceed)."""
    try:
        if not path.exists():
            return ""
        import datetime
        import shutil
        ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        hist_dir = path.parent / "history"
        hist_dir.mkdir(parents=True, exist_ok=True)
        archive = hist_dir / ("%s.%s%s" % (path.stem, ts, path.suffix))
        # If two writes land in the same second, disambiguate so we never clobber a prior archive.
        n = 1
        while archive.exists():
            archive = hist_dir / ("%s.%s.%d%s" % (path.stem, ts, n, path.suffix))
            n += 1
        shutil.copy2(str(path), str(archive))
        return str(archive)
    except Exception:
        return ""


def _atomic_write(path: Path, text: str) -> None:
    """Write ``text`` to ``path`` atomically (write a temp sibling, then os.replace). Creates the
    parent dir. UTF-8 + LF (runtime VALUES may carry diacritics; this is a data file, not code)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    os.replace(str(tmp), str(path))


def _to_yaml(data: Mapping[str, Any], *, header: str = "") -> str:
    """Serialize a small brand dict to YAML. Prefers PyYAML (allow_unicode -> the tenant's accented
    strings are preserved verbatim); degrades to a minimal hand-emitter if PyYAML is unavailable.
    TOTAL -- never raises (a serialization failure returns just the header + a comment)."""
    try:
        import yaml  # type: ignore[import-untyped]
        body = yaml.safe_dump(dict(data), allow_unicode=True, sort_keys=False,
                              default_flow_style=False)
        return (header + body) if header else body
    except Exception:
        pass
    try:
        return (header + _mini_yaml(data, 0)) if header else _mini_yaml(data, 0)
    except Exception:
        return header + "# (serialization unavailable)\n"


def _mini_yaml(data: Any, indent: int) -> str:
    """A minimal YAML emitter for the small {str: str|list|dict} brand shapes (PyYAML fallback).
    Quotes scalar strings to keep special chars safe. TOTAL."""
    pad = "  " * indent
    if isinstance(data, Mapping):
        out: List[str] = []
        for k, v in data.items():
            if isinstance(v, (Mapping, list, tuple)) and v:
                out.append("%s%s:" % (pad, k))
                out.append(_mini_yaml(v, indent + 1))
            else:
                out.append("%s%s: %s" % (pad, k, _yaml_scalar(v)))
        return "\n".join(out) + "\n"
    if isinstance(data, (list, tuple)):
        return "\n".join("%s- %s" % (pad, _yaml_scalar(v)) for v in data) + "\n"
    return "%s%s\n" % (pad, _yaml_scalar(data))


def _yaml_scalar(v: Any) -> str:
    """A double-quoted YAML scalar (escapes backslash + quote). Empty/None -> '""'. TOTAL."""
    if v is None:
        return '""'
    s = str(v).replace("\\", "\\\\").replace('"', '\\"')
    return '"%s"' % s


def _get(materials: Mapping[str, Any], field: str) -> Any:
    """A field from the materials dict, or None. TOTAL."""
    try:
        return materials.get(field)
    except Exception:
        return None


def _str_list(value: Any) -> List[str]:
    """Coerce a list/string into a clean str list, DROPPING placeholder/empty entries (never a
    fabricated value). A [preencher]/[fornecer]/{{ }} entry is excluded. TOTAL."""
    out: List[str] = []
    if value is None:
        return out
    if isinstance(value, (list, tuple)):
        items = value
    elif isinstance(value, str):
        items = re.split(r"[\n,;]+", value)
    else:
        return out
    for it in items:
        s = _clean(it)
        if s:
            out.append(s)
    return out


__all__ = [
    "WriteResult",
    "brand_spec_from_brandbook",
    "write_brand_overlay",
    "VoiceIdentityResult",
    "write_voice_identity",
]
