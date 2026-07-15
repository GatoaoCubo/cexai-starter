#!/usr/bin/env python3
# -*- coding: ascii -*-
"""cex_moldgen_emit -- white-label MOLD generator (MOLDGEN W1).

Mints a tenant's `brand.config.ts` overlay from a brand spec, validated against
the PROVEN reference storefront contract. The storefront reskins entirely from ONE
file: applyBrandTheme(brand) pushes the 24 brand tokens to :root CSS vars at
boot, so every shadcn component + Tailwind utility re-themes with ZERO component
edits. This tool is the EMITTER + VALIDATOR for that one file.

Single source of truth for the contract lives HERE (TOKEN_TO_CSSVAR +
SYSTEM_DENYLIST); the `white_label_config` artifact documents it and the golden
test proves the emitter reproduces a known-good reference tenant overlay.

Contract source (read-only): the reference commerce app's src/brand/brand.config.ts,
applyBrandTheme.ts, index.css, docs/design_system.md, docs/mold_handoff.md.

Design laws baked in: degrade-never (missing OPTIONAL fields warn, never fail),
fail-closed (anything not in the 24-token contract is rejected), never-fabricate
(values come from the caller's spec, never invented), no-secrets (the brand
overlay carries brand data only; capability/data/secret matrix is N04's
deliverable -- cross-ref, never emitted here).

CLI:
  python _tools/cex_moldgen_emit.py --spec brand.json --out .cex/runtime/moldgen
  python _tools/cex_moldgen_emit.py --validate brand.json
  python _tools/cex_moldgen_emit.py --self-check        # contract self-consistency

Importable API: emit(spec), validate_spec(spec), validate_emitted(ts_text),
parse_overlay_ts(text), derive_cssvar(key).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# THE CONTRACT (single source of truth) -- mirrors the reference applyBrandTheme.ts
# ---------------------------------------------------------------------------

# The 24 BrandTokens in canonical order, each mapped to its --css-var.
# 23 are HSL triplets "H S% L%"; `radius` is a CSS length (e.g. "0.75rem").
TOKEN_TO_CSSVAR: List[Tuple[str, str]] = [
    ("background", "--background"),
    ("foreground", "--foreground"),
    ("card", "--card"),
    ("cardForeground", "--card-foreground"),
    ("popover", "--popover"),
    ("popoverForeground", "--popover-foreground"),
    ("primary", "--primary"),
    ("primaryForeground", "--primary-foreground"),
    ("secondary", "--secondary"),
    ("secondaryForeground", "--secondary-foreground"),
    ("muted", "--muted"),
    ("mutedForeground", "--muted-foreground"),
    ("accent", "--accent"),
    ("accentForeground", "--accent-foreground"),
    ("border", "--border"),
    ("input", "--input"),
    ("ring", "--ring"),
    ("brand", "--brand"),
    ("brandForeground", "--brand-foreground"),
    ("brandMuted", "--brand-muted"),
    ("highlight", "--highlight"),
    ("highlightForeground", "--highlight-foreground"),
    ("highlightMuted", "--highlight-muted"),
    ("radius", "--radius"),
]
TOKEN_KEYS: List[str] = [k for k, _ in TOKEN_TO_CSSVAR]
TOKEN_KEY_SET = set(TOKEN_KEYS)
RADIUS_KEY = "radius"

# SYSTEM-LEVEL CSS vars the generator must NEVER emit/override. Enumerated from
# the reference index.css :root + docs/design_system.md S1 (status/motion/type/shadow/
# z-index/gradient/overlay). The brand overlay touches ONLY the 24 tokens above;
# everything below is inherited unchanged by every tenant. (--font-family-base is
# brand-controlled via brand.font.family and is NOT in this denylist.)
SYSTEM_DENYLIST = frozenset([
    # status
    "--success", "--success-foreground",
    "--warning", "--warning-foreground",
    "--info", "--info-foreground",
    "--destructive", "--destructive-foreground",
    # motion
    "--duration-fast", "--duration-base", "--duration-slow",
    "--ease-emphasized", "--ease-standard",
    "--transition-base", "--transition-fast",
    # type scale
    "--font-size-display", "--font-size-h1", "--font-size-h2", "--font-size-h3",
    "--font-size-base", "--font-size-lg", "--font-size-sm",
    "--tracking-tight", "--tracking-normal", "--tracking-wide",
    "--leading-tight", "--leading-normal", "--leading-relaxed",
    "--font-weight-display", "--font-weight-h1", "--font-weight-h2",
    "--font-weight-h3", "--font-weight-body",
    # shadows
    "--shadow-sm", "--shadow-md", "--shadow-lg", "--shadow-gold", "--shadow-glow",
    # z-index
    "--z-base", "--z-dropdown", "--z-sticky", "--z-fixed",
    "--z-modal-backdrop", "--z-modal", "--z-popover", "--z-tooltip",
    # gradients
    "--gradient-brand", "--gradient-highlight", "--gradient-overlay",
    "--gradient-gold", "--gradient-dark", "--gradient-hero",
    "--gradient-card", "--gradient-border",
    # overlay
    "--overlay", "--overlay-opacity-light", "--overlay-opacity-heavy",
    "--overlay-gradient",
])

# BrandConfig field requirements (mirrors brand.config.ts BrandConfig interface).
REQUIRED_BRAND_FIELDS = ["name", "nameHtml", "logo", "logoAlt", "domain"]
OPTIONAL_BRAND_FIELDS = ["tagline"]  # font.googleHref handled separately
ALLOWED_TOP_KEYS = frozenset(
    REQUIRED_BRAND_FIELDS + OPTIONAL_BRAND_FIELDS + ["font", "tokens", "capabilities"]
)

# value formats
_HSL_RE = re.compile(r"^\s*(\d{1,3})\s+(\d{1,3})%\s+(\d{1,3})%\s*$")
_RADIUS_RE = re.compile(r"^(0|\d*\.?\d+(px|rem|em|%))$")


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def derive_cssvar(key: str) -> str:
    """camelCase BrandTokens key -> --kebab-case CSS var (matches applyBrandTheme).

    background -> --background ; cardForeground -> --card-foreground.
    """
    kebab = re.sub(r"([A-Z])", r"-\1", key).lower()
    return "--" + kebab


def is_hsl_triplet(value: Any) -> bool:
    """True if value is a valid 'H S% L%' triplet with H<=360, S/L<=100."""
    if not isinstance(value, str):
        return False
    m = _HSL_RE.match(value)
    if not m:
        return False
    h, s, lum = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return h <= 360 and s <= 100 and lum <= 100


def is_css_length(value: Any) -> bool:
    """True if value is a CSS length usable for --radius (e.g. '0.75rem')."""
    return isinstance(value, str) and bool(_RADIUS_RE.match(value.strip()))


class ValidationResult:
    """Structured validate() result. ok=False when any error is present."""

    def __init__(self, errors: Optional[List[str]] = None,
                 warnings: Optional[List[str]] = None) -> None:
        self.errors: List[str] = errors or []
        self.warnings: List[str] = warnings or []

    @property
    def ok(self) -> bool:
        return not self.errors

    def as_dict(self) -> Dict[str, Any]:
        return {"ok": self.ok, "errors": self.errors, "warnings": self.warnings}

    def __repr__(self) -> str:
        return "ValidationResult(ok=%s, errors=%d, warnings=%d)" % (
            self.ok, len(self.errors), len(self.warnings))


# ---------------------------------------------------------------------------
# VALIDATOR (fail-closed do-not-touch guard + contract conformance)
# ---------------------------------------------------------------------------

def validate_spec(spec: Dict[str, Any]) -> ValidationResult:
    """Validate a brand spec against the mold contract. Fail-closed.

    (a) all 24 tokens present + each a valid HSL triplet (radius excepted);
    (b) all required BrandConfig fields present;
    (c) FAIL-CLOSED on ANY system-level denylist var (the do-not-touch guard) or
        any key outside the exact 24-token / allowed-field contract;
    (d) radius is a CSS length.
    degrade-never: missing OPTIONAL (tagline / font.googleHref) = warn, not fail.
    """
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(spec, dict):
        return ValidationResult(["spec must be a dict/object"])

    # (c) fail-closed on unknown top-level keys (blocks secret/system bleed).
    for k in spec:
        if k not in ALLOWED_TOP_KEYS:
            errors.append("unknown top-level key (fail-closed): %r" % k)

    # (b) required BrandConfig fields.
    for field in REQUIRED_BRAND_FIELDS:
        if not spec.get(field):
            errors.append("missing required BrandConfig field: %s" % field)

    font = spec.get("font") or {}
    if not isinstance(font, dict) or not font.get("family"):
        errors.append("missing required field: font.family")
    if not font.get("googleHref"):
        warnings.append("optional font.googleHref absent (degrade-never)")
    for fk in font if isinstance(font, dict) else []:
        if fk not in ("family", "googleHref"):
            errors.append("unknown font key (fail-closed): %r" % fk)

    # degrade-never on optional brand fields.
    if not spec.get("tagline"):
        warnings.append("optional tagline absent (degrade-never)")

    # capabilities flag is accepted for forward-compat but NEVER emitted here --
    # the capability/data/secret matrix is N04's deliverable (cross-ref).
    if "capabilities" in spec:
        warnings.append(
            "capabilities present: accepted but NOT emitted to brand.config.ts "
            "(per-tenant capability matrix is N04-owned)")

    # tokens block.
    tokens = spec.get("tokens")
    if not isinstance(tokens, dict):
        errors.append("missing required field: tokens (must be an object)")
        return ValidationResult(errors, warnings)

    # (c) fail-closed: any token key outside the 24. If it maps to a denylisted
    # system var, name it explicitly as a do-not-touch intrusion.
    for k in tokens:
        if k not in TOKEN_KEY_SET:
            cssvar = derive_cssvar(k)
            if cssvar in SYSTEM_DENYLIST:
                errors.append(
                    "system-level var intrusion (do-not-touch): token %r -> %s"
                    % (k, cssvar))
            else:
                errors.append(
                    "unknown token key (fail-closed, contract is exactly 24): %r" % k)

    # (a)/(d) every contract token present + correctly typed.
    for k in TOKEN_KEYS:
        if k not in tokens:
            errors.append("missing token: %s" % k)
            continue
        v = tokens[k]
        if k == RADIUS_KEY:
            if not is_css_length(v):
                errors.append("radius is not a CSS length: %r" % v)
        elif not is_hsl_triplet(v):
            errors.append("token %s is not a valid HSL triplet 'H S%% L%%': %r" % (k, v))

    # (c) value-level guard: a token value must never smuggle a raw CSS var ref.
    for k, v in tokens.items():
        if isinstance(v, str) and "--" in v:
            errors.append("token %s value contains a raw CSS var ref (fail-closed): %r"
                          % (k, v))

    return ValidationResult(errors, warnings)


def validate_emitted(ts_text: str) -> ValidationResult:
    """Parse an emitted/existing overlay .ts and validate it against the contract."""
    try:
        spec = parse_overlay_ts(ts_text)
    except Exception as exc:  # noqa: BLE001 -- kill-safe: never raise to caller
        return ValidationResult(["could not parse overlay .ts: %s" % exc])
    return validate_spec(spec)


# ---------------------------------------------------------------------------
# PARSER (read a brand.config overlay .ts back into a spec dict)
# ---------------------------------------------------------------------------

def _find_str(text: str, field: str) -> Optional[str]:
    """Extract a `field: "value"` string literal (line-anchored, comment-safe)."""
    m = re.search(r'(?m)^\s*%s\s*:\s*"((?:[^"\\]|\\.)*)"' % re.escape(field), text)
    return m.group(1) if m else None


def parse_overlay_ts(text: str) -> Dict[str, Any]:
    """Parse a brand.config overlay .ts into a spec dict.

    Robust to inline comments, the `logo,` shorthand, and a one- OR two-line
    googleHref. Extracts BrandConfig fields + the 24 tokens. Used by the golden
    test to compare an emitted overlay against the proven reference file semantically.
    """
    spec: Dict[str, Any] = {}

    # logo comes from the import statement (object uses `logo,` shorthand).
    m_logo = re.search(r'import\s+logo\s+from\s+"([^"]+)"', text)
    if m_logo:
        spec["logo"] = m_logo.group(1)

    for field in ("name", "nameHtml", "tagline", "logoAlt", "domain"):
        val = _find_str(text, field)
        if val is not None:
            spec[field] = val

    font: Dict[str, str] = {}
    fam = _find_str(text, "family")
    if fam is not None:
        font["family"] = fam
    # googleHref value may sit on the next line: \s* spans the newline.
    m_href = re.search(r'googleHref\s*:\s*"([^"]+)"', text)
    if m_href:
        font["googleHref"] = m_href.group(1)
    if font:
        spec["font"] = font

    # tokens block: from `tokens: {` to its closing `},`.
    m_block = re.search(r"tokens\s*:\s*\{(.*?)\n\s*\},", text, re.S)
    tokens: Dict[str, str] = {}
    if m_block:
        block = m_block.group(1)
        for k in TOKEN_KEYS:
            mt = re.search(r'(?m)^\s*%s\s*:\s*"([^"]*)"' % re.escape(k), block)
            if mt:
                tokens[k] = mt.group(1)
    spec["tokens"] = tokens
    return spec


# ---------------------------------------------------------------------------
# EMITTER (spec -> brand.config.ts overlay string)
# ---------------------------------------------------------------------------

_HEADER = (
    "// ============================================================================="
    "\n// GENERATED TENANT OVERLAY -- %(name)s"
    "\n//"
    "\n// Emitted by _tools/cex_moldgen_emit.py from a validated brand spec. This is"
    "\n// the SINGLE source of truth for everything brand-specific: point main.tsx"
    "\n// here -> applyBrandTheme(brand) pushes these 24 tokens to :root at boot and"
    "\n// the whole storefront reskins with ZERO component edits. System-level tokens"
    "\n// (status/motion/type/spacing/a11y/shadows/z-index/gradients) are inherited"
    "\n// unchanged -- this file NEVER sets them."
    "\n// ============================================================================="
)


def _ts_str(value: str) -> str:
    r"""Render a Python str as a TS double-quoted literal (escape \\ and ")."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def emit(spec: Dict[str, Any], strict: bool = True) -> str:
    """Emit a brand.config.ts overlay STRING from a brand spec.

    strict=True (default) validates first and refuses to emit an invalid spec
    (fail-closed). The returned string is byte-faithful to the storefront overlay
    shape (same imports / interface import / `export const brand: BrandConfig`).
    Tenant brand strings (e.g. nameHtml) may be non-ASCII; the returned `str`
    carries them faithfully -- write it with encoding='utf-8'.
    """
    if strict:
        res = validate_spec(spec)
        if not res.ok:
            raise ValueError("invalid brand spec (fail-closed): " + "; ".join(res.errors))

    name = spec["name"]
    lines: List[str] = []
    lines.append(_HEADER % {"name": name})
    lines.append("")
    lines.append('import logo from %s;' % _ts_str(spec["logo"]))
    lines.append('import type { BrandConfig } from "./brand.config";')
    lines.append("")
    lines.append("export const brand: BrandConfig = {")
    lines.append("  name: %s," % _ts_str(spec["name"]))
    lines.append("  nameHtml: %s," % _ts_str(spec["nameHtml"]))
    if spec.get("tagline"):
        lines.append("  tagline: %s," % _ts_str(spec["tagline"]))
    lines.append("  logo,")
    lines.append("  logoAlt: %s," % _ts_str(spec["logoAlt"]))
    lines.append("  domain: %s," % _ts_str(spec["domain"]))

    font = spec.get("font") or {}
    lines.append("  font: {")
    lines.append("    family: %s," % _ts_str(font["family"]))
    if font.get("googleHref"):
        lines.append("    googleHref: %s," % _ts_str(font["googleHref"]))
    lines.append("  },")

    tokens = spec["tokens"]
    lines.append("  tokens: {")
    for k in TOKEN_KEYS:
        lines.append("    %s: %s," % (k, _ts_str(str(tokens[k]))))
    lines.append("  },")

    lines.append("};")
    lines.append("")
    lines.append("export default brand;")
    lines.append("")
    return "\n".join(lines)


def emit_to_file(spec: Dict[str, Any], out_dir: str,
                 tenant: Optional[str] = None, strict: bool = True) -> str:
    """Emit and write `<out_dir>/<tenant>/brand.config.ts`. Returns the path.

    Writes into a cex output dir ONLY -- never into the gato repo.
    """
    text = emit(spec, strict=strict)
    slug = tenant or _slug(spec.get("name", "tenant"))
    dest_dir = os.path.join(out_dir, slug)
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(dest_dir, "brand.config.ts")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return path


def _slug(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", str(name).lower()).strip("_")
    return s or "tenant"


# ---------------------------------------------------------------------------
# self-check: the contract must be internally consistent
# ---------------------------------------------------------------------------

def self_check() -> ValidationResult:
    """Assert the contract is internally consistent (derive == declared, no
    token maps into the denylist). A cheap invariant guard for CI."""
    errors: List[str] = []
    if len(TOKEN_TO_CSSVAR) != 24:
        errors.append("expected exactly 24 tokens, found %d" % len(TOKEN_TO_CSSVAR))
    for key, declared in TOKEN_TO_CSSVAR:
        derived = derive_cssvar(key)
        if derived != declared:
            errors.append("css-var mismatch: %s -> derived %s != declared %s"
                          % (key, derived, declared))
        if declared in SYSTEM_DENYLIST:
            errors.append("brand token %s collides with system denylist %s"
                          % (key, declared))
    return ValidationResult(errors)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _load_spec(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="MOLDGEN white-label brand.config.ts emitter")
    ap.add_argument("--spec", help="path to a brand spec JSON; emits the overlay")
    ap.add_argument("--out", default=os.path.join(".cex", "runtime", "moldgen"),
                    help="output root dir (default .cex/runtime/moldgen)")
    ap.add_argument("--tenant", help="tenant slug (default: slug of spec.name)")
    ap.add_argument("--validate", metavar="SPEC",
                    help="validate a brand spec JSON and exit (no emit)")
    ap.add_argument("--self-check", action="store_true",
                    help="verify the contract is internally consistent")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    if args.self_check:
        res = self_check()
        _report("self-check", res, args.json)
        return 0 if res.ok else 1

    if args.validate:
        spec = _load_spec(args.validate)
        res = validate_spec(spec)
        _report("validate", res, args.json)
        return 0 if res.ok else 1

    if args.spec:
        spec = _load_spec(args.spec)
        res = validate_spec(spec)
        if not res.ok:
            _report("validate", res, args.json)
            return 1
        path = emit_to_file(spec, args.out, tenant=args.tenant)
        if args.json:
            print(json.dumps({"ok": True, "path": path, "warnings": res.warnings}))
        else:
            print("[OK] emitted %s" % path)
            for w in res.warnings:
                print("  [warn] %s" % w)
        return 0

    ap.print_help()
    return 2


def _report(label: str, res: ValidationResult, as_json: bool) -> None:
    if as_json:
        print(json.dumps({"label": label, **res.as_dict()}))
        return
    tag = "[OK]" if res.ok else "[FAIL]"
    print("%s %s: %d error(s), %d warning(s)" % (tag, label, len(res.errors), len(res.warnings)))
    for e in res.errors:
        print("  [error] %s" % e)
    for w in res.warnings:
        print("  [warn] %s" % w)


if __name__ == "__main__":
    raise SystemExit(main())
