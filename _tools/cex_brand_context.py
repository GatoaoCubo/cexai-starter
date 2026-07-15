#!/usr/bin/env python3
# -*- coding: ascii -*-
"""cex_brand_context -- the BRAND-MUSTACHE FOUNDATION (mission BRAND_MUSTACHE).

THE FOUNDER'S DIRECTIVE: the brand is NEVER hardcoded in a capability template. It is an
OPEN MUSTACHE VARIABLE -- {{brand_name}} / {{brand_tagline}} / {{brand_archetype}} /
{{brand_tokens.<key>}} / {{brand_voice.<key>}} / {{brand_palette}} -- diffused through ALL
capabilities, filled PER-TENANT from the brand config. The SAME template, filled with
tenant X's brand context, produces tenant-X-aligned output. Any given tenant's RESOLVED
values are just ONE tenant's, NEVER a literal in a template.

This module is the seam that (1) UNIFIES the three existing brand sources into ONE context
dict, and (2) RENDERS {{brand_*}} mustache placeholders from that dict.

THE THREE SOURCES it unifies (build-on, never reinvent):
  1. IDENTITY  -- .cex/brand/brand_config.yaml (brand_inject.load_brand_config): BRAND_NAME,
                  BRAND_DESCRIPTION, BRAND_VALUES, BRAND_PERSONALITY, IDEAL_CUSTOMER.
  2. TOKENS    -- the tenant's moldgen overlay .cex/runtime/moldgen/<tid>/brand.config.ts
                  (cex_moldgen_emit.parse_overlay_ts), the 24 canonical design tokens. No
                  overlay -> the NEUTRAL baseline (the SAME _NEUTRAL_TOKENS the product_ad
                  mold uses -- imported, never re-keyed).
  3. VOICE     -- the tenant voice profile (cex_tenant_voice_profile.load_voice_profile):
                  register/strategy/tone/archetype. No profile -> a neutral voice.

THE CONTEXT SHAPE (resolve_brand_context return):
  {
    brand_name:        str          -- display name (identity OR overlay name OR voice name)
    brand_tagline:     str          -- tagline (overlay tagline; "" if none)
    brand_archetype:   str          -- Jungian archetype (voice profile; "" if none)
    brand_description: str          -- one-line description (identity; "" if none)
    brand_values:      list[str]    -- core values (identity; [] if none)
    brand_tokens:      dict[24]     -- the 24 design tokens (overlay-validated OR neutral)
    brand_voice:       dict         -- {register, strategy, primary, secondary, anti_tone, essence}
    brand_palette:     list[str]    -- the brand color roles as HSL strings (from tokens/voice)
    brand_logo:        str          -- logo ref (overlay logo; "" if none)
  }

DEGRADE-NEVER (the universal-seam contract): a tenant with NO moldgen overlay -> the NEUTRAL
baseline tokens; NO voice profile -> a neutral voice; MISSING identity -> empty strings. The
resolver NEVER raises and NEVER fabricates a brand value. It NEVER hardcodes any ONE tenant's
brand -- a tenant's real values appear only when THAT tenant's own sources resolve to them.

render_brand(template, ctx): a small dependency-free ASCII mustache resolver. Replaces
{{brand_*}} placeholders (incl. dotted paths {{brand_tokens.primary}}, {{brand_voice.register}})
from ctx. PURE + TOTAL: an unknown/missing placeholder -> honest empty string (consistent +
documented), never a crash. No external mustache lib.

Kill-switch (read by the run path, not here): CEX_BRAND_DIFFUSE=0 disables diffusion into the
run path -> byte-identical to the pre-mustache behaviour (zero-regression rollback lever).

ASCII-only source (.claude/rules/ascii-code-rule.md). Runtime VALUES (a tenant's accented
brand strings) may carry diacritics; this module's OWN constants stay diacritic-free.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

# The 24 canonical token keys + the overlay parser + the HSL/length validators -- the ONE
# design-token contract (single source: cex_moldgen_emit). Imported, never re-declared.
from cex_moldgen_emit import (  # noqa: E402
    RADIUS_KEY,
    TOKEN_KEYS,
    is_css_length,
    is_hsl_triplet,
    parse_overlay_ts,
)

# THE neutral baseline -- the degrade-never design-system, the SAME table the product_ad mold
# overlays a tenant's tokens onto. Imported from the ONE canonical source (cex_neutral_tokens)
# so there is no SECOND hand-kept neutral source: a tenant with no overlay gets EXACTLY the
# canonical neutral look (council MEDIUM dedup -- the three former literal copies collapsed onto
# this one tiny, dependency-free sibling module, imported the same bare way as cex_moldgen_emit).
from cex_neutral_tokens import _NEUTRAL_TOKENS  # noqa: E402

# The default tenant moldgen overlay root (mirrors cex_moldgen_emit's CLI default + the proven
# .cex/runtime/moldgen/<tid>/brand.config.ts layout). Overridable per-call via profile_dir.
_REPO_ROOT = Path(_HERE).resolve().parent
_DEFAULT_MOLDGEN_ROOT = _REPO_ROOT / ".cex" / "runtime" / "moldgen"


# --------------------------------------------------------------------------- #
# CANONICAL TENANT KEY (council wave-0.5 A1) -- ONE key for every per-tenant lookup.
#
# THE BUG A1 FIXES: the old in-module ``_slug`` STRIPPED hyphens ('a-b-c' -> 'abc'), but the
# capability overlay + every other tenant surface key on the canonical ``_safe_tenant_id``
# (cex_bootstrap), whose regex [a-z0-9][a-z0-9_-]{0,63} PRESERVES hyphens. So a real UUID-form
# tenant ('550e8400-e29b-41d4-...') resolved to a DIFFERENT directory key than its overlay ->
# the brand silently fell back to NEUTRAL. The fix UNIFIES on the canonical guard: this is the
# SAME normalization the overlay/voice/identity dirs use, so a UUID tenant resolves the SAME
# brand its capability overlay does. The 3 duplicate ``_slug`` copies (here,
# cex_brand_writeback, cex_tenant_voice_profile) are collapsed onto this one canonical key.
#
# TOTAL wrapper: ``_safe_tenant_id`` RAISES SystemExit on a malformed id (fail-closed -- correct
# for a path WRITE), but the brand resolver is degrade-never (it must NEVER crash a run). So
# ``_tenant_key`` calls the canonical guard and degrades a rejected id to "" (a fully-neutral
# context), preserving the resolver's TOTAL contract while keying on the SAME normalization.
try:
    from cex_bootstrap import _safe_tenant_id as _canonical_tenant_id  # noqa: E402
except Exception:  # pragma: no cover - stripped runtime: fall back to an inline equivalent
    import re as _re_fallback

    def _canonical_tenant_id(tenant_id: str) -> str:  # type: ignore[misc]
        tid = (tenant_id or "").strip().lower()
        if not _re_fallback.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", tid):
            raise SystemExit("invalid tenant id %r" % tenant_id)
        return tid


def _tenant_key(value: str) -> str:
    """The canonical per-tenant directory key (council A1): the SAME normalization the
    capability overlay + every tenant surface use (cex_bootstrap._safe_tenant_id) -- hyphens
    PRESERVED so a UUID tenant resolves the same brand its overlay does. TOTAL: a malformed /
    rejected id degrades to "" (a neutral context) instead of raising (degrade-never)."""
    if not isinstance(value, str) or not value.strip():
        return ""
    try:
        return _canonical_tenant_id(value)
    except SystemExit:
        return ""
    except Exception:
        return ""

# The kill-switch the RUN PATH reads (documented here, enforced in cex_run_capability). The
# mustache diffusion is ON by default; CEX_BRAND_DIFFUSE in {0,false,no,off} disables it.
ENV_BRAND_DIFFUSE = "CEX_BRAND_DIFFUSE"
_FALSY = frozenset({"0", "false", "no", "off"})

# The reserved key the run path stamps the resolved context under in a generator's ``inputs``.
# A generator reads inputs[BRAND_CONTEXT_KEY] to brand-frame its output; the run path strips it
# from the typed FORM payload so it never leaks as a user-facing field.
BRAND_CONTEXT_KEY = "brand_context"

# The mustache placeholder grammar: {{ name }} or {{ a.b.c }}. Dotted paths index nested dicts
# / lists in the context. Whitespace inside the braces is tolerated. ASCII identifier segments.
_MUSTACHE_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)*)\s*\}\}")


# --------------------------------------------------------------------------- #
# Public: brand diffusion kill-switch (read by the run path).
# --------------------------------------------------------------------------- #
def brand_diffuse_enabled() -> bool:
    """True unless CEX_BRAND_DIFFUSE is a falsy flag (default ON). The run path's rollback
    lever -- off -> the run path does NOT diffuse brand context (byte-identical pre-mustache).
    TOTAL: a malformed value -> ON (the default-on posture)."""
    raw = os.environ.get(ENV_BRAND_DIFFUSE)
    if raw is None:
        return True
    return raw.strip().lower() not in _FALSY


# --------------------------------------------------------------------------- #
# Public: unify the 3 sources into ONE brand context dict.
# --------------------------------------------------------------------------- #
def resolve_brand_context(
    tenant_id: str,
    *,
    profile_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Unify identity + tokens + voice into ONE brand context dict for ``tenant_id``.

    See the module docstring for the returned shape. DEGRADE-NEVER + TOTAL: every source is
    optional; a missing source contributes its neutral/empty default and NEVER raises. NEVER
    fabricates a brand value; NEVER hardcodes any ONE tenant's real brand.

    ``profile_dir`` (optional) overrides BOTH the moldgen overlay root AND the voice profile
    dir (it is forwarded to load_voice_profile) -- so a test can point the whole resolver at a
    fixture tree. ``tenant_id`` empty/blank -> a fully neutral context (no identity, neutral
    tokens, neutral voice) rather than an error (the run path enforces tenant presence itself).
    """
    tid = (tenant_id or "").strip()

    identity = _load_identity(tid, profile_dir)
    tokens = _resolve_tokens(tid, profile_dir)
    overlay = _load_overlay_meta(tid, profile_dir)
    voice = _resolve_voice(tid, profile_dir)

    # brand_name precedence -- the TENANT-SPECIFIC source wins so white-label holds. The
    # moldgen overlay is per-tenant (.cex/runtime/moldgen/<tid>/) so its ``name`` is THIS
    # tenant's name; the voice profile is also tenant-keyed. The identity (A2) is now ALSO
    # per-tenant first (.cex/tenants/<tid>/brand/brand_config.yaml via resolve_tenant_path);
    # the repo-global .cex/brand/brand_config.yaml is an OPT-IN DEFAULT used ONLY when there is
    # no active/explicit tenant. So a tenant with its OWN identity resolves to ITS name, and a
    # tenant with NO identity degrades to "" (NOT the repo-global brand's real identity) -- the
    # global brand never bleeds across tenants. This is the founder's directive made concrete.
    brand_name = (
        _nonempty(overlay.get("name"))
        or _nonempty(_voice_brand_name(tid, profile_dir))
        or _nonempty(identity.get("BRAND_NAME"))
        or ""
    )
    brand_tagline = _nonempty(overlay.get("tagline")) or ""
    brand_archetype = _nonempty(voice.get("archetype")) or ""
    brand_description = _nonempty(identity.get("BRAND_DESCRIPTION")) or ""
    brand_values = _as_str_list(identity.get("BRAND_VALUES"))
    brand_logo = _nonempty(overlay.get("logo")) or ""
    brand_palette = _derive_palette(tokens, voice)

    return {
        "brand_name": brand_name,
        "brand_tagline": brand_tagline,
        "brand_archetype": brand_archetype,
        "brand_description": brand_description,
        "brand_values": brand_values,
        "brand_tokens": tokens,
        "brand_voice": voice,
        "brand_palette": brand_palette,
        "brand_logo": brand_logo,
    }


# --------------------------------------------------------------------------- #
# Public: the dependency-free mustache renderer.
# --------------------------------------------------------------------------- #
def render_brand(
    template: str,
    ctx: Mapping[str, Any],
    *,
    keep_unknown: bool = False,
) -> str:
    """Replace {{brand_*}} mustache placeholders in ``template`` from ``ctx``. PURE + TOTAL.

    Supports dotted paths: {{brand_tokens.primary}} -> ctx['brand_tokens']['primary'];
    {{brand_voice.register}} -> ctx['brand_voice']['register']; a list index path
    {{brand_palette.0}} -> ctx['brand_palette'][0]. A value that resolves to a list/dict is
    rendered as a comma-joined / readable string (so a template never leaks a Python repr).

    MISSING / UNKNOWN placeholder (default ``keep_unknown=False``): replaced with an honest
    EMPTY string (consistent + documented) -- a template can reference a placeholder a given
    tenant has no value for and it simply vanishes, never crashes. Pass keep_unknown=True to
    leave the literal ``{{...}}`` in place instead (useful when chaining renders).

    ``template`` not a str / ``ctx`` not a mapping -> returns the template unchanged (TOTAL)."""
    if not isinstance(template, str) or "{{" not in template:
        return template if isinstance(template, str) else ""
    context: Mapping[str, Any] = ctx if isinstance(ctx, Mapping) else {}

    def _sub(match: "re.Match[str]") -> str:
        path = match.group(1)
        found, value = _lookup_path(context, path)
        if not found:
            return match.group(0) if keep_unknown else ""
        return _stringify(value)

    return _MUSTACHE_RE.sub(_sub, template)


# --------------------------------------------------------------------------- #
# Internal: source loaders (each TOTAL + degrade-never).
# --------------------------------------------------------------------------- #
def _load_identity(tid: str, profile_dir: Optional[str]) -> Dict[str, Any]:
    """The brand IDENTITY dict (BRAND_NAME / BRAND_DESCRIPTION / BRAND_VALUES ...), PER-TENANT
    FIRST (council wave-0.5 A2).

    THE BUG A2 FIXES: identity used to come ONLY from the repo-global .cex/brand/brand_config.yaml
    (a single real tenant's identity today) -> that tenant's description/values/name BLED onto
    every other tenant. The fix routes identity through the per-tenant brand surface FIRST:
    .cex/tenants/<tid>/brand/brand_config.yaml (resolved via the fail-closed cex_tenant_paths guard,
    surface='brand'). The repo-global config is an OPT-IN DEFAULT used ONLY when there is NO tenant
    (single-tenant / explicit central). A tenant WITH a per-tenant identity gets ITS values; a
    tenant with NONE degrades to {} (EMPTY description/values/name -- neutral), NEVER the
    repo-global identity.

    The per-tenant config is the NESTED bootstrap shape (identity: {BRAND_NAME, ...}); it is
    FLATTENED (brand_inject.flatten) so the top-level BRAND_* keys this module reads resolve from
    either shape. TOTAL + degrade-never: any import/read/parse failure -> {} (empty identity)."""
    # 1. PER-TENANT identity first (the A2 fix). Only attempted for a real tenant key.
    key = _tenant_key(tid)
    if key:
        per_tenant = _load_tenant_identity(key, profile_dir)
        if per_tenant:
            return per_tenant
        # A real tenant with NO per-tenant identity -> EMPTY identity (neutral). The global
        # brand_config is the DEFAULT ONLY when there is no tenant -- it must NOT bleed here.
        return {}
    # 2. NO tenant (single-tenant / explicit central) -> the repo-global brand_config DEFAULT.
    try:
        import brand_inject  # type: ignore[import]

        cfg = brand_inject.load_brand_config()
        return _flatten_identity(cfg) if isinstance(cfg, dict) else {}
    except Exception:
        return {}


def _load_tenant_identity(key: str, profile_dir: Optional[str]) -> Dict[str, Any]:
    """The per-tenant brand_config.yaml identity for the canonical tenant ``key``, FLATTENED,
    or {} when absent/unreadable. Resolved via the fail-closed cex_tenant_paths guard
    (surface='brand') so the path can never escape the tenant root. TOTAL -- never raises.

    ``profile_dir`` (a test override) points the tenant brand dir at a fixture tree:
    <profile_dir>/<key>/brand/brand_config.yaml (mirrors the .cex/tenants/<tid>/brand layout)."""
    try:
        if profile_dir:
            path = Path(profile_dir) / key / "brand" / "brand_config.yaml"
        else:
            tools_dir = str(_HERE)
            if tools_dir not in sys.path:
                sys.path.insert(0, tools_dir)
            import cex_tenant_paths as _tp  # type: ignore[import]

            path = _tp.resolve_tenant_path(
                "brand_config.yaml", surface="brand", tenant_id=key)
        if not path.is_file():
            return {}
        import brand_inject  # type: ignore[import]

        cfg = brand_inject.load_brand_config(path)
        return _flatten_identity(cfg) if isinstance(cfg, dict) else {}
    except (Exception, SystemExit):
        # SystemExit included: the tenant-path guard fails CLOSED on a hostile key; the brand
        # resolver degrades to an empty (neutral) identity rather than crashing a run.
        return {}


def _flatten_identity(cfg: Mapping[str, Any]) -> Dict[str, Any]:
    """Normalize a brand_config dict to TOP-LEVEL BRAND_* keys, handling BOTH the global FLAT
    shape (BRAND_NAME at top) and the per-tenant NESTED bootstrap shape (identity: {BRAND_NAME}).
    Uses brand_inject.flatten when available (it surfaces nested section keys at the top level);
    degrades to the raw dict otherwise. TOTAL: never raises."""
    if not isinstance(cfg, Mapping):
        return {}
    try:
        import brand_inject  # type: ignore[import]

        flat = brand_inject.flatten(dict(cfg))
        return flat if isinstance(flat, dict) else dict(cfg)
    except Exception:
        return dict(cfg)


def _resolve_tokens(tid: str, profile_dir: Optional[str]) -> Dict[str, str]:
    """The 24 design tokens for ``tid``: the tenant overlay's VALIDATED tokens layered on the
    NEUTRAL baseline (a malformed/absent token -> the neutral value, never a broken color).
    Always returns a COMPLETE 24-key dict (the mold's degrade-never contract). TOTAL."""
    resolved: Dict[str, str] = dict(_NEUTRAL_TOKENS)
    overlay = _load_overlay_spec(tid, profile_dir)
    overlay_tokens = overlay.get("tokens") if isinstance(overlay, dict) else None
    if isinstance(overlay_tokens, Mapping):
        for key in TOKEN_KEYS:
            val = overlay_tokens.get(key)
            if not isinstance(val, str) or not val.strip():
                continue
            ok = is_css_length(val) if key == RADIUS_KEY else is_hsl_triplet(val)
            if ok:
                resolved[key] = val  # validated tenant value wins
            # else: keep the neutral baseline (degrade-never; never a broken token)
    return resolved


def _load_overlay_meta(tid: str, profile_dir: Optional[str]) -> Dict[str, str]:
    """The overlay's BRAND-META fields (name / tagline / logo / domain), or {} when no overlay.
    Separate from _resolve_tokens so the token path always returns 24 keys. TOTAL."""
    overlay = _load_overlay_spec(tid, profile_dir)
    if not isinstance(overlay, dict):
        return {}
    out: Dict[str, str] = {}
    for k in ("name", "tagline", "logo", "logoAlt", "domain", "nameHtml"):
        v = overlay.get(k)
        if isinstance(v, str) and v.strip():
            out[k] = v
    return out


def _load_overlay_spec(tid: str, profile_dir: Optional[str]) -> Dict[str, Any]:
    """Parse the tenant moldgen overlay .ts into a spec dict (cex_moldgen_emit.parse_overlay_ts),
    or {} when the file is absent/unreadable. TOTAL -- never raises. The overlay path mirrors the
    proven layout: <root>/<tid_slug>/brand.config.ts (root = profile_dir override OR the moldgen
    default). Tries the raw tid and its slug (so a mixed-case tenant id and its lowercase slug
    both resolve)."""
    if not tid:
        return {}
    root = Path(profile_dir) if profile_dir else _DEFAULT_MOLDGEN_ROOT
    candidates = []
    seen = set()
    # The CANONICAL key first (the overlay dir is named by _safe_tenant_id -- A1), then the raw
    # tid as a belt-and-braces fallback for a legacy dir. A UUID tenant now hits its real dir.
    for name in (_tenant_key(tid), tid):
        if name and name not in seen:
            seen.add(name)
            candidates.append(name)
    for name in candidates:
        path = root / name / "brand.config.ts"
        try:
            if path.is_file():
                text = path.read_text(encoding="utf-8")
                spec = parse_overlay_ts(text)
                return spec if isinstance(spec, dict) else {}
        except Exception:
            continue
    return {}


def _resolve_voice(tid: str, profile_dir: Optional[str]) -> Dict[str, Any]:
    """The tenant voice as a FLAT, mustache-friendly dict: {register, strategy, primary,
    secondary, anti_tone, essence}. Distilled from cex_tenant_voice_profile.load_voice_profile.
    NO profile -> a NEUTRAL voice (every field ""), never fabricated. TOTAL."""
    neutral = {
        "register": "",
        "strategy": "",
        "primary": "",
        "secondary": "",
        "anti_tone": "",
        "essence": "",
    }
    try:
        import cex_tenant_voice_profile as vp  # type: ignore[import]

        profile = vp.load_voice_profile(tid, profile_dir=profile_dir)
    except Exception:
        return neutral
    if not isinstance(profile, dict):
        return neutral

    tone = profile.get("tone") if isinstance(profile.get("tone"), Mapping) else {}
    primary = _nonempty(tone.get("primary")) or ""
    secondary = _nonempty(tone.get("secondary")) or ""
    anti_tone = _nonempty(tone.get("anti_tone")) or ""
    # ``register`` is the headline voice register -- the primary tone IS that register; ``strategy``
    # summarises the secondary posture. Honest mapping of the existing profile fields (no new data).
    return {
        "register": primary,
        "strategy": secondary,
        "primary": primary,
        "secondary": secondary,
        "anti_tone": anti_tone,
        "essence": _nonempty(profile.get("essence")) or "",
    }


def _voice_brand_name(tid: str, profile_dir: Optional[str]) -> Optional[str]:
    """The tenant voice profile's ``brand_name`` (a tenant-keyed source), or None. Used in the
    brand_name precedence so a tenant with a voice profile but no overlay still resolves to ITS
    own name (not the global brand_config). TOTAL: any failure -> None."""
    try:
        import cex_tenant_voice_profile as vp  # type: ignore[import]

        profile = vp.load_voice_profile(tid, profile_dir=profile_dir)
    except Exception:
        return None
    if isinstance(profile, dict):
        name = profile.get("brand_name")
        if isinstance(name, str) and name.strip():
            return name.strip()
    return None


def _derive_palette(tokens: Mapping[str, Any], voice: Mapping[str, Any]) -> List[str]:
    """The brand color roles as a short HSL-string list (for {{brand_palette}} / a swatch row).
    Derived from the resolved tokens' identity roles (primary / brand / accent / highlight) --
    the colors a brand-aware output would key off. NEVER fabricates: a missing role is skipped.
    TOTAL."""
    palette: List[str] = []
    for key in ("primary", "brand", "accent", "highlight"):
        v = tokens.get(key) if isinstance(tokens, Mapping) else None
        if isinstance(v, str) and v.strip():
            palette.append(v.strip())
    return palette


# --------------------------------------------------------------------------- #
# Internal: mustache path lookup + value stringify.
# --------------------------------------------------------------------------- #
def _lookup_path(context: Mapping[str, Any], path: str) -> "tuple[bool, Any]":
    """Resolve a dotted ``path`` against ``context``. Returns (found, value). A dict key OR a
    list index (numeric segment) is supported. TOTAL: any miss -> (False, None)."""
    cur: Any = context
    for seg in path.split("."):
        if isinstance(cur, Mapping):
            if seg in cur:
                cur = cur[seg]
                continue
            return False, None
        if isinstance(cur, (list, tuple)):
            if seg.isdigit():
                idx = int(seg)
                if 0 <= idx < len(cur):
                    cur = cur[idx]
                    continue
            return False, None
        return False, None
    return True, cur


def _stringify(value: Any) -> str:
    """Render a resolved value as a clean string for substitution (never a Python repr). A
    list -> comma-joined; a dict -> 'k: v' pairs comma-joined; None -> ''. TOTAL."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (list, tuple)):
        return ", ".join(_stringify(v) for v in value if v is not None and str(v).strip() != "")
    if isinstance(value, Mapping):
        return ", ".join(
            "%s: %s" % (k, _stringify(v)) for k, v in value.items()
            if v is not None and str(v).strip() != ""
        )
    return str(value)


# --------------------------------------------------------------------------- #
# Internal: small helpers.
# --------------------------------------------------------------------------- #
def _nonempty(value: Any) -> Optional[str]:
    """The stripped string if it is a non-empty, non-placeholder string; else None. TOTAL.
    Rejects the bootstrap placeholder shapes brand_inject also screens ({{...}}, VALUE_*)."""
    if not isinstance(value, str):
        return None
    s = value.strip()
    if not s or s.startswith("{{") or s.startswith("VALUE_") or s.startswith("TRAIT_"):
        return None
    return s


def _as_str_list(value: Any) -> List[str]:
    """Coerce BRAND_VALUES (a YAML list OR a newline/comma string) into a clean str list. TOTAL."""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(v).strip() for v in value if v is not None and str(v).strip()]
    if isinstance(value, str):
        parts = re.split(r"[\n,;]+", value)
        return [p.strip() for p in parts if p.strip()]
    return []


# NOTE (council A1): the legacy in-module ``_slug`` (which STRIPPED hyphens) was removed -- the
# per-tenant key is now the canonical ``_tenant_key`` (= cex_bootstrap._safe_tenant_id), the SAME
# key the capability overlay + every tenant surface use. See _tenant_key above.


__all__ = [
    "resolve_brand_context",
    "render_brand",
    "brand_diffuse_enabled",
    "BRAND_CONTEXT_KEY",
    "ENV_BRAND_DIFFUSE",
]
