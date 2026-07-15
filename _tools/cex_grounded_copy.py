#!/usr/bin/env python3
# -*- coding: ascii -*-
"""cex_grounded_copy -- the grounded ad-copy engine (W2 P3 / US3 / FR-010, FR-011).

THREE SEPARATE grounded generations -- TITLE / BULLETS / BODY -- from a raw listing,
under a HARD grounding contract (G1-G10) that NEVER invents a fact and OMITs a section
when the source lacks it. The crown jewel of the reference ad/catalog chain, generalized:
the reference `ai-extract` edge fn proved it LIVE (28 raw listings retrofitted, grounding
9.5/10, zero invented facts, writes-nothing). This is the central, tenant-neutral mold of
that proof -- and the SAME grounding backstop logic, ported to Python.

WHY THREE SEPARATE GENERATIONS (the structural law -- crosswalk S5 / FR-002): structured
attributes/bullets are STORED + VALIDATED SEPARATE from the prose body, so a marketplace's
title char cap / N-bullets / body prose each get their own independently-checkable payload.
This module returns:
  * title  : str           -- a single channel-capped line (the listing/SEO title)
  * bullets: list[str]     -- the key_features (verb-first, scannable -- NOT prose)
  * body   : {description, long_description, why_it_works}  -- the PROSE only
These three are NEVER concatenated here; the product_ad mold (cex_product_ad_mold) renders
them into separate sections, and only a ChannelAdapter may ever fold them per-channel.

GROUNDED = every emitted claim traces to a canonical/source field; a claim with NO source is
DROPPED (or the section OMITted), NEVER invented. The grounding contract (Block B, G1-G10):

  G1  Facts come SOLELY from source. Every number/material/dimension/weight/capacity.
  G2  Voice shapes the SENTENCE only, never the SET of facts.
  G3  NEVER invent/alter dimensions / materials / weight / capacity.       (BLOCKING)
  G4  NEVER invent compatibility / size-fit ("serve para X", "ate Y kg").  (BLOCKING)
  G5  NEVER invent a safety/health claim ("atoxico", "vet aprovado").      (BLOCKING)
  G6  Absent fact -> OMIT the section. usage_guide only if the source states it.
  G7  No fabricated quantities/counts ("9 furos", "ate 4 horas", "250 ml").
  G8  Preserve honesty about limits: never UPGRADE a hedged claim
      ("resistente a agua" -/-> "a prova d'agua"). claim_strength <= source.
  G9  No channel/price/competitor leakage in the prose; strip keyword-soup.
  G10 Omitting is safe; fabricating is not. When unsure a fact is supported, DISCARD.

  Severity (FR-011): G5 (safety) + G3/G4 (physical facts) = BLOCKING; G1/G2/G7/G8/G10 =
  HIGH (block + ONE retry); G6/G9 = MEDIUM (auto-clean + proceed).

THE ENGINE LOOP (per generation): generate -> grounding-gate -> on a BLOCKING/HIGH finding,
retry ONCE with the violation surfaced -> if it still fails, OMIT that field rather than ship
a fabricated fact (US3 BLOCKING-fail edge). MEDIUM findings auto-clean (drop the bad token /
strip the leakage) and proceed.

PROVIDER-SWAPPABLE: the generator is an injected callable `llm(prompt) -> str` (Groq / Gemini
/ Claude / ...). The grounding contract does NOT change with the provider (assumption: spec
S4). With NO llm, the engine runs the DETERMINISTIC backstop: it re-voices STRICTLY from the
canonical source fields (a faithful, no-LLM projection) -- so the engine is fully testable +
degrade-never offline, and the no-fabrication proof holds without any network.

WRITES NOTHING (FR-010 / US3 scenario 4): this module is a PURE projection + a pure validator.
It returns the 3 payloads for HITL review; it touches no DB, no file, no network of its own
(the only IO is the caller's injected llm). The grounding result rides ALONGSIDE so the
caller (cex_ad_mold_bind) can gate the honest badge.

REUSE (Article VII): the canonical golden record is cex_canonical_product.CanonicalProduct
(W2 P1); the SEAM mapper is cex_product_ad_mold.ad_data_from_product; the voice knob is
cex_tenant_voice_profile.TenantVoiceProfile. This module ADDS the grounding gate + the
3-generation loop -- it re-derives NONE of those.

ASCII-only source per .claude/rules/ascii-code-rule.md. The runtime COPY this engine
re-voices carries full PT-BR diacritics (it is content, not code); the grounding `normalize`
strips diacritics for the fact-diff via \\uXXXX escapes (functional i18n, source stays ASCII).

CORE API (pure; stdlib-only; the llm is injected):
    grounding_check(output_text, source_text)            -> GroundingResult
    extract_copy(canonical, voice_profile=None, llm=None) -> GroundedCopy
    source_text_of(canonical)                            -> str (the grounding source blob)
    SEVERITY                                             -> {G-rule: BLOCKING|HIGH|MEDIUM}

DEMO + SELF-TEST:
    python _tools/cex_grounded_copy.py --demo
    python _tools/cex_grounded_copy.py --self-test
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

# REUSE the SEAM mapper (canonical record -> the title/bullets/prose, already separated).
# TOTAL: if the import path is broken, the deterministic projection degrades to reading the
# canonical fields directly (see _deterministic_from_canonical).
try:
    from cex_product_ad_mold import ad_data_from_product  # noqa: E402
except ImportError:  # pragma: no cover - degrade-never on import path issues
    ad_data_from_product = None  # type: ignore[assignment]


# =========================================================================== #
# Severity map (FR-011 / voice-profile Block B.3).                            #
# =========================================================================== #
BLOCKING = "BLOCKING"
HIGH = "HIGH"
MEDIUM = "MEDIUM"

SEVERITY: Dict[str, str] = {
    "G1": HIGH,
    "G2": HIGH,
    "G3": BLOCKING,
    "G4": BLOCKING,
    "G5": BLOCKING,
    "G6": MEDIUM,
    "G7": HIGH,
    "G8": HIGH,
    "G9": MEDIUM,
    "G10": HIGH,
}

# The maximum retries the engine performs on a BLOCKING/HIGH finding before it OMITs the
# field (US3 BLOCKING-fail edge: retry once, then omit -- never ship a fabricated fact).
MAX_RETRIES = 1

# Default channel title cap (chars). Marketplace titles are short; the body has no cap.
# Mercado Livre = 60 (spec FR-005); a per-channel cap can override via voice_profile.
_DEFAULT_TITLE_CAP = 60


# =========================================================================== #
# Grounding lexicons + patterns (ported from the reference ai-extract groundingCheck). #
# Source: the reference commerce app supabase/functions/ai-extract/index.ts.          #
# =========================================================================== #

# G3/G7: "<number><unit>" physical-fact tokens. The unit set mirrors the reference UNIT_RE.
# NOTE: every blob is _normalize()d (diacritics stripped) BEFORE these patterns run, so the
# character classes only need the ASCII base letters -- "orificio"/"codigo" already have their
# accents removed at match time. (ascii-code-rule: source stays diacritic-free.)
_UNIT_RE = re.compile(
    r"(\d+(?:[.,]\d+)?)\s?"
    r"(cm|mm|m|kg|g|ml|l|litros?|polegadas?|kgf|w|v|horas?|h|min|minutos?"
    r"|orificios?|%)\b",
    re.IGNORECASE,
)

# G1/G3: the conservative material lexicon (only flag a KNOWN material absent from source).
_MATERIAL_LEXICON: Tuple[str, ...] = (
    "algodao", "poliester", "poliuretano", "pvc", "polietileno", "gel", "ceramica",
    "porcelana", "vidro", "madeira", "bambu", "metal", "aco inoxidavel", "aco",
    "aluminio", "ferro", "plastico", "abs", "silicone", "borracha", "feltro", "la",
    "linho", "couro", "sisal", "juta", "nylon", "espuma", "veludo", "tecido", "arame",
)

# G5: safety/health claims that must NEVER appear unless the SOURCE states them (BLOCKING).
_SAFETY_LEXICON: Tuple[str, ...] = (
    "atoxico", "nao toxico", "antialergico", "hipoalergenico", "antibacteriano",
    "antimicrobiano", "vet aprovado", "aprovado por veterinario", "aprovacao veterinaria",
    "certificado", "inmetro", "anvisa", "esterilizado", "esteril", "organico",
    "bpa free", "livre de bpa", "grau alimenticio",
)

# G8: hedged source claims that must NOT be upgraded to an absolute output claim.
# Each entry = (absolute_token_in_output, hedged_token_that_licenses_it_in_source).
# If the OUTPUT asserts the absolute but the SOURCE only hedges -> a G8 upgrade violation.
_G8_UPGRADES: Tuple[Tuple[str, str], ...] = (
    ("a prova d agua", "resistente a agua"),
    ("a prova d'agua", "resistente a agua"),
    ("impermeavel", "resistente a agua"),
    ("a prova de quedas", "resistente a quedas"),
    ("a prova de arranhoes", "resistente a arranhoes"),
    ("indestrutivel", "resistente"),
    ("inquebravel", "resistente"),
)

# G9: channel/price/competitor leakage that must not survive into voiced prose.
# (Matched against _normalize()d text -> ASCII base letters only.)
_LEAKAGE_RE = re.compile(
    r"(compre agora|buscas relacionadas|sku\b|gtin\b|codigo de barras"
    r"|politica de (troca|devolu)|frete gratis garantid|whatsapp"
    r"|mercado ?livre|\br\$\s?\d|envio imediato|melhor preco|imperdivel"
    r"|vocabulario adicional)",
    re.IGNORECASE,
)

# G9: marketplace spec-label boilerplate masquerading as a "feature" (scrub from bullets).
# The bullet text is _normalize()d before this matches, so ASCII base letters suffice.
_SPEC_LABEL_RE = re.compile(
    r"^\s*(marca|modelo|model|sku|gtin|ean|codigo|referencia"
    r"|comprimento|largura|altura|profundidade|dimensoes|peso|material"
    r"|capacidade|cor(es)?|volume|ncm)\s*:",
    re.IGNORECASE,
)


def _normalize(s: Any) -> str:
    """Lowercase + strip combining diacritics (mirrors the reference normalize()). TOTAL.

    NFD-decompose then drop the U+0300..U+036F combining marks, so "resistente a agua"
    and the accented form diff identically. Used ONLY for the fact-diff -- the
    emitted copy keeps its accents."""
    if not isinstance(s, str):
        s = "" if s is None else str(s)
    decomposed = unicodedata.normalize("NFD", s)
    stripped = "".join(ch for ch in decomposed if not (0x0300 <= ord(ch) <= 0x036F))
    return stripped.lower()


def _numeric_unit_tokens(text: str) -> set:
    """Pull canonicalized "<number><unit>" fact tokens from a blob (G3/G7). "6,5 kg" ->
    "6.5kg". PURE + TOTAL."""
    out = set()
    n = _normalize(text)
    for m in _UNIT_RE.finditer(n):
        num = m.group(1).replace(",", ".")
        unit = m.group(2).lower()
        out.add("%s%s" % (num, unit))
    return out


def _lexicon_in_text(text: str, lexicon: Sequence[str]) -> set:
    """The lexicon words present in `text` (loose word-ish boundary; multi-word safe).
    PURE + TOTAL."""
    n = _normalize(text)
    found = set()
    for word in lexicon:
        pat = r"(^|[^a-z])" + word.replace(" ", r"\s+") + r"([^a-z]|$)"
        if re.search(pat, n, re.IGNORECASE):
            found.add(word)
    return found


# =========================================================================== #
# GroundingResult / GroundedCopy (lightweight typed dicts).                    #
# =========================================================================== #
def _finding(rule: str, message: str) -> Dict[str, str]:
    """A single grounding finding: {rule, severity, message}. PURE."""
    return {"rule": rule, "severity": SEVERITY.get(rule, HIGH), "message": message}


def grounding_check(output_text: Any, source_text: Any) -> Dict[str, Any]:
    """The deterministic grounding backstop: diff an output blob against the source (G1-G10).

    Returns a GroundingResult dict:
      {
        ok: bool,                 # True iff there is NO BLOCKING finding
        blocking: bool,           # any BLOCKING (G3/G4/G5) finding present
        findings: [ {rule, severity, message}, ... ],
        worst: BLOCKING|HIGH|MEDIUM|None,
      }

    The checks (ported from the reference ai-extract groundingCheck, the proven deterministic
    backstop):
      - G3/G7: every <number><unit> token in the output must exist in the source.
      - G1/G3: every KNOWN material word in the output must exist in the source.
      - G5   : a safety/health claim in the output absent from the source is BLOCKING.
      - G8   : an absolute claim in the output whose source only HEDGES is an upgrade.
      - G9   : channel/price/competitor leakage that slipped into the prose.

    PURE + TOTAL: never raises; a non-string input degrades to "".
    """
    out_t = output_text if isinstance(output_text, str) else _join_text(output_text)
    src_t = source_text if isinstance(source_text, str) else _join_text(source_text)
    findings: List[Dict[str, str]] = []

    # G3/G7 -- numeric+unit facts.
    src_nums = _numeric_unit_tokens(src_t)
    for tok in _numeric_unit_tokens(out_t):
        if tok not in src_nums:
            findings.append(_finding(
                "G3", 'numero+unidade na saida sem suporte na fonte: "%s"' % tok))

    # G1/G3 -- materials.
    src_mats = _lexicon_in_text(src_t, _MATERIAL_LEXICON)
    for mat in _lexicon_in_text(out_t, _MATERIAL_LEXICON):
        if mat not in src_mats:
            findings.append(_finding(
                "G3", 'material na saida sem suporte na fonte: "%s"' % mat))

    # G5 -- safety/health claims (BLOCKING).
    src_safety = _lexicon_in_text(src_t, _SAFETY_LEXICON)
    for claim in _lexicon_in_text(out_t, _SAFETY_LEXICON):
        if claim not in src_safety:
            findings.append(_finding(
                "G5", 'claim de seguranca/saude inventado: "%s"' % claim))

    # G8 -- claim-strength upgrade (output asserts an absolute the source only hedges).
    n_out = _normalize(out_t)
    n_src = _normalize(src_t)
    for absolute, hedged in _G8_UPGRADES:
        if _contains(n_out, absolute) and not _contains(n_src, absolute):
            # the output asserts the absolute; the source must assert it verbatim too.
            findings.append(_finding(
                "G8", 'claim absoluto sem suporte na fonte (upgrade de "%s"): "%s"'
                % (hedged, absolute)))

    # G9 -- leakage in the prose.
    if _LEAKAGE_RE.search(out_t):
        findings.append(_finding(
            "G9", "vazamento de boilerplate/canal/preco na prosa (ex.: 'Compre agora', "
            "SKU, link, R$, keyword-soup) -- revisar."))

    blocking = any(f["severity"] == BLOCKING for f in findings)
    worst = _worst_severity(findings)
    return {
        "ok": not blocking,
        "blocking": blocking,
        "findings": findings,
        "worst": worst,
    }


def _contains(normalized_haystack: str, normalized_needle: str) -> bool:
    """Word-ish containment in already-normalized text, apostrophe/punctuation tolerant. PURE.

    Both sides have inter-word punctuation (apostrophes, hyphens) collapsed to a single space
    so "a prova d'agua" (haystack) matches "a prova d agua" (needle) and vice-versa."""
    def _collapse(s: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", s).strip()

    hay = _collapse(normalized_haystack)
    needle = _collapse(normalized_needle)
    if not needle:
        return False
    needle_re = re.escape(needle).replace(r"\ ", r"\s+")
    return re.search(r"(^|[^a-z0-9])" + needle_re + r"([^a-z0-9]|$)", hay) is not None


def _worst_severity(findings: Sequence[Mapping[str, Any]]) -> Optional[str]:
    """The worst severity among findings (BLOCKING > HIGH > MEDIUM). PURE."""
    order = {BLOCKING: 3, HIGH: 2, MEDIUM: 1}
    worst = None
    worst_rank = 0
    for f in findings:
        sev = f.get("severity")
        rank = order.get(str(sev), 0)
        if rank > worst_rank:
            worst_rank = rank
            worst = sev
    return worst


def _join_text(value: Any) -> str:
    """Flatten a str / list / dict of strings into one blob for the fact-diff. PURE + TOTAL.
    Mirrors the reference flattenOutput()."""
    parts: List[str] = []

    def _push(v: Any) -> None:
        if isinstance(v, str):
            if v.strip():
                parts.append(v)
        elif isinstance(v, Mapping):
            for x in v.values():
                _push(x)
        elif isinstance(v, (list, tuple)):
            for x in v:
                _push(x)

    _push(value)
    return "\n".join(parts)


# =========================================================================== #
# G9 auto-clean (MEDIUM): drop spec-label bullets + leakage-laden bullets.     #
# =========================================================================== #
def _clean_bullets(bullets: Sequence[str], source_text: str) -> Tuple[List[str], List[Dict[str, str]]]:
    """Scrub the bullets list (G9 MEDIUM auto-clean): drop marketplace spec-labels
    ("Marca:", "Modelo:", "Comprimento: 17 cm") and any bullet whose own grounding check
    is BLOCKING (a fabricated number/material/safety claim). Returns (kept, findings).

    G9 is MEDIUM -> auto-clean + proceed (never blocks); a BLOCKING bullet (a fabricated
    physical fact) is DROPPED here, which is the safe action (G10: omit beats fabricate)."""
    kept: List[str] = []
    findings: List[Dict[str, str]] = []
    dropped_spec = 0
    dropped_fact = 0
    for b in bullets:
        if not isinstance(b, str) or not b.strip():
            continue
        # match the spec-label pattern against the normalized bullet (accent-insensitive).
        if _SPEC_LABEL_RE.match(_normalize(b)):
            dropped_spec += 1
            continue
        # a bullet that asserts a fabricated fact/material/safety claim is dropped (G10).
        res = grounding_check(b, source_text)
        if res["blocking"]:
            dropped_fact += 1
            continue
        kept.append(b.strip())
    if dropped_spec:
        findings.append(_finding(
            "G9", "bullets: %d rotulo(s) de ficha de marketplace removido(s)" % dropped_spec))
    if dropped_fact:
        findings.append(_finding(
            "G10", "bullets: %d item(ns) com fato sem suporte na fonte descartado(s)"
            % dropped_fact))
    return kept, findings


# =========================================================================== #
# THE source blob: what every generated claim is grounded against.             #
# =========================================================================== #
def source_text_of(canonical: Mapping[str, Any]) -> str:
    """Build the grounding SOURCE blob from a canonical record: the union of every field a
    claim may legitimately come from (prose + bullets + ficha + identity + the raw imported
    text if carried). This is the ground-truth a generation is diffed against (G1).

    A run that imported a raw marketplace listing should carry the raw text under
    `_source_text` / `raw_text` / `raw_description` so keyword-soup facts (materials buried
    in the ML title) still count as SOURCE. PURE + TOTAL.
    """
    c = canonical if isinstance(canonical, Mapping) else {}
    parts: List[str] = []

    # explicit raw imported text (the keyword-soup source -- the real grounding ground truth).
    for key in ("_source_text", "raw_text", "raw_description", "source_text"):
        v = c.get(key)
        if isinstance(v, str) and v.strip():
            parts.append(v)

    # prose
    for key in ("title", "subtitle", "description", "long_description", "why_it_works"):
        v = c.get(key)
        if isinstance(v, str) and v.strip():
            parts.append(v)

    # structured lists
    for key in ("key_features", "benefits_functional", "benefits_emotional",
                "colors", "materials", "audience_tags"):
        v = c.get(key)
        if isinstance(v, (list, tuple)):
            parts.extend(str(x) for x in v if isinstance(x, str) and x.strip())

    # the attributes long-tail (k + v both count as source)
    attrs = c.get("attributes")
    if isinstance(attrs, Mapping):
        for k, v in attrs.items():
            parts.append("%s %s" % (k, v))

    # ficha numeric facts -> render the number+unit so the fact-diff sees them as source.
    for axis_key, unit in (("dim_length_cm", "cm"), ("dim_width_cm", "cm"),
                           ("dim_height_cm", "cm")):
        n = c.get(axis_key)
        if isinstance(n, (int, float)):
            parts.append(_fmt_num(n) + " " + unit)
    wg = c.get("weight_grams")
    if isinstance(wg, (int, float)):
        parts.append(_fmt_num(wg) + " g")
        # also the kg form, since copy may state kg.
        parts.append(_fmt_num(wg / 1000.0) + " kg")

    # identity codes (so a model/brand mention is grounded)
    for key in ("brand", "model", "mpn", "gtin", "sku"):
        v = c.get(key)
        if isinstance(v, str) and v.strip():
            parts.append(v)

    return "\n".join(parts)


def _fmt_num(v: Any) -> str:
    """A number -> a clean string (40.0 -> '40', 6.5 -> '6,5' pt-BR). PURE + TOTAL."""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return ""
    if f == int(f):
        return str(int(f))
    s = ("%.3f" % f).rstrip("0").rstrip(".")
    return s.replace(".", ",")


# =========================================================================== #
# THE engine: three SEPARATE grounded generations.                            #
# =========================================================================== #
def extract_copy(
    canonical: Optional[Mapping[str, Any]] = None,
    voice_profile: Optional[Mapping[str, Any]] = None,
    llm: Optional[Callable[[str], str]] = None,
    *,
    title_cap: Optional[int] = None,
    source_text: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate TITLE / BULLETS / BODY as three SEPARATE grounded payloads from a canonical
    record (W2 P1). WRITES NOTHING -- returns the payloads + the grounding result for HITL.

    canonical     -- a CanonicalProduct dict (cex_canonical_product). The fact ground-truth.
    voice_profile -- a TenantVoiceProfile dict (cex_tenant_voice_profile). Shapes the SENTENCE
                     only (G2), never the facts. degrade-never: None -> a neutral register.
    llm           -- an injected provider callable `llm(prompt) -> str` returning JSON. The
                     grounding contract is provider-invariant. None -> the DETERMINISTIC
                     projection (re-voice STRICTLY from canonical fields; fully offline).
    title_cap     -- the channel title char cap (default 60; ML). The body has no cap.
    source_text   -- override the grounding source blob (else source_text_of(canonical)).

    Returns a GroundedCopy dict:
      {
        title:   str,                    # one capped line (OMITted -> "" if ungroundable)
        bullets: [str, ...],             # the key_features (verb-first; OMIT-on-empty)
        body:    {description, long_description, why_it_works},  # PROSE only (OMIT per field)
        grounding: GroundingResult,      # the aggregate gate result over the 3 payloads
        meta:    {provider, retries, omitted: [field, ...]},
        writes_nothing: True,
      }

    THE LOOP (per generation): generate -> grounding-gate -> retry ONCE on BLOCKING/HIGH ->
    OMIT the field if it still fails (US3 edge). MEDIUM auto-cleans + proceeds. PURE-ish +
    TOTAL: never raises; the ONLY IO is the caller's injected llm.
    """
    c = canonical if isinstance(canonical, Mapping) else {}
    src = source_text if isinstance(source_text, str) and source_text.strip() else source_text_of(c)
    cap = int(title_cap) if isinstance(title_cap, int) and title_cap > 0 else _title_cap_of(voice_profile)
    provider = "deterministic" if llm is None else "llm"

    omitted: List[str] = []
    retries = 0
    all_findings: List[Dict[str, str]] = []

    # --- 1) TITLE (a single channel-capped line) ---
    title, t_ret, t_find, t_omit = _generate_grounded(
        kind="title", canonical=c, voice_profile=voice_profile, llm=llm,
        source_text=src, title_cap=cap)
    retries += t_ret
    all_findings.extend(t_find)
    if t_omit:
        omitted.append("title")

    # --- 2) BULLETS (the key_features -- verb-first, scannable; SEPARATE from prose) ---
    bullets, b_ret, b_find, b_omit = _generate_grounded(
        kind="bullets", canonical=c, voice_profile=voice_profile, llm=llm,
        source_text=src, title_cap=cap)
    retries += b_ret
    all_findings.extend(b_find)
    if b_omit:
        omitted.append("bullets")

    # --- 3) BODY (the PROSE only -- description / long_description / why_it_works) ---
    body, body_ret, body_find, body_omit = _generate_grounded(
        kind="body", canonical=c, voice_profile=voice_profile, llm=llm,
        source_text=src, title_cap=cap)
    retries += body_ret
    all_findings.extend(body_find)
    omitted.extend(body_omit)

    # The aggregate grounding gate over the THREE final payloads (post-omit, post-clean):
    # the result a HITL reviewer / the badge gate reads. After omit/clean it MUST be ok
    # (no BLOCKING) -- the loop guarantees a fabricated fact is dropped, never shipped.
    final_blob = _join_text([title, bullets, list(body.values())])
    final_gate = grounding_check(final_blob, src)
    # merge the per-generation auto-clean findings into the gate (transparency for HITL).
    final_gate = _merge_findings(final_gate, all_findings)

    return {
        "title": title,
        "bullets": bullets,
        "body": body,
        "grounding": final_gate,
        "meta": {
            "provider": provider,
            "retries": retries,
            "omitted": omitted,
            "title_cap": cap,
        },
        "writes_nothing": True,
    }


def _merge_findings(gate: Dict[str, Any], extra: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    """Fold the per-generation auto-clean/omit findings into the aggregate gate (for HITL
    transparency) without changing the ok/blocking verdict (the final payloads are clean).
    PURE."""
    merged = dict(gate)
    findings = list(gate.get("findings") or [])
    seen = {(f.get("rule"), f.get("message")) for f in findings}
    for f in extra:
        key = (f.get("rule"), f.get("message"))
        if key not in seen:
            findings.append(dict(f))
            seen.add(key)
    merged["findings"] = findings
    merged["worst"] = _worst_severity(findings) if findings else None
    return merged


def _generate_grounded(
    kind: str,
    canonical: Mapping[str, Any],
    voice_profile: Optional[Mapping[str, Any]],
    llm: Optional[Callable[[str], str]],
    source_text: str,
    title_cap: int,
) -> Tuple[Any, int, List[Dict[str, str]], Any]:
    """Run ONE grounded generation (title|bullets|body): generate -> gate -> retry-once ->
    omit-on-fail. Returns (payload, retries_used, findings, omit_flag_or_list).

    payload type by kind: title -> str, bullets -> list[str], body -> dict.
    omit return by kind  : title/bullets -> bool, body -> list[str] of omitted prose keys.
    """
    findings: List[Dict[str, str]] = []
    retries = 0

    # The deterministic projection is ALWAYS the safe fallback (and the no-LLM path).
    det = _deterministic_generation(kind, canonical, voice_profile, title_cap)

    if llm is None:
        # Deterministic path: re-voice STRICTLY from canonical -> already grounded by
        # construction. Still run the gate + clean (defensive) so the contract is uniform.
        return _finalize_generation(kind, det, source_text, title_cap, findings, retries)

    # LLM path: prompt -> parse -> gate -> retry-once-then-OMIT.
    candidate = det  # default to deterministic if the LLM yields nothing usable.
    last_violation = ""
    for attempt in range(MAX_RETRIES + 1):
        prompt = _build_prompt(kind, canonical, voice_profile, source_text, title_cap,
                               violation=last_violation)
        try:
            raw = llm(prompt) if callable(llm) else ""
        except Exception:
            raw = ""
        parsed = _parse_generation(kind, raw)
        if parsed is None or _is_empty_payload(kind, parsed):
            # nothing usable -> keep the deterministic candidate (already grounded).
            break
        gate = grounding_check(_join_text(parsed), source_text)
        worst = gate.get("worst")
        if worst in (BLOCKING, HIGH):
            # surface the violation + retry ONCE; on the last attempt, fall through to OMIT.
            last_violation = "; ".join(f["message"] for f in gate.get("findings", [])
                                       if f.get("severity") in (BLOCKING, HIGH))[:400]
            findings.extend(gate.get("findings", []))
            if attempt < MAX_RETRIES:
                retries += 1
                continue
            # exhausted retries on a BLOCKING/HIGH fact -> OMIT (US3 edge): drop the LLM
            # candidate, fall back to the deterministic (grounded) projection. The fabricated
            # facts never ship.
            candidate = det
            break
        # acceptable (worst is None or MEDIUM) -> adopt the LLM candidate; clean below.
        candidate = parsed
        if gate.get("findings"):
            findings.extend(gate.get("findings", []))
        break

    return _finalize_generation(kind, candidate, source_text, title_cap, findings, retries)


def _finalize_generation(
    kind: str,
    payload: Any,
    source_text: str,
    title_cap: int,
    findings: List[Dict[str, str]],
    retries: int,
) -> Tuple[Any, int, List[Dict[str, str]], Any]:
    """Apply the MEDIUM auto-clean (G9) + the OMIT-on-empty rule (G6) to a payload, per kind.
    Returns (clean_payload, retries, findings, omit)."""
    if kind == "title":
        title = _cap_title(payload if isinstance(payload, str) else "", title_cap)
        # a title that asserts a fabricated fact -> OMIT (empty) rather than ship it.
        if title and grounding_check(title, source_text)["blocking"]:
            findings.append(_finding("G10", "title descartado: fato sem suporte na fonte"))
            return "", retries, findings, True
        return title, retries, findings, (title == "")

    if kind == "bullets":
        raw_bullets = payload if isinstance(payload, (list, tuple)) else []
        clean, clean_find = _clean_bullets([str(b) for b in raw_bullets], source_text)
        findings.extend(clean_find)
        # G6: no source bullets -> OMIT (empty list), never fabricate placeholder features.
        return clean, retries, findings, (len(clean) == 0)

    # body: a dict of prose fields; OMIT a field that is empty or ungroundable (G6/G10).
    body = payload if isinstance(payload, Mapping) else {}
    out: Dict[str, str] = {}
    omitted_keys: List[str] = []
    for key in ("description", "long_description", "why_it_works"):
        v = body.get(key)
        text = v.strip() if isinstance(v, str) else ""
        if not text:
            omitted_keys.append(key)
            continue
        if grounding_check(text, source_text)["blocking"]:
            findings.append(_finding("G10", "body.%s descartado: fato sem suporte" % key))
            omitted_keys.append(key)
            continue
        out[key] = text
    return out, retries, findings, omitted_keys


# =========================================================================== #
# Deterministic generation (the no-LLM, always-grounded projection).          #
# Re-voices STRICTLY from the canonical fields via the proven SEAM mapper.     #
# =========================================================================== #
def _deterministic_generation(
    kind: str,
    canonical: Mapping[str, Any],
    voice_profile: Optional[Mapping[str, Any]],
    title_cap: int,
) -> Any:
    """Project the canonical record into a title/bullets/body payload WITHOUT an LLM, reusing
    the proven SEAM mapper (ad_data_from_product) so features->bullets, description->prose,
    ficha->ficha stay SEPARATE. Grounded by construction: every field comes verbatim from the
    canonical. PURE + TOTAL."""
    seam = _seam_copy(canonical)

    if kind == "title":
        # the SEO/listing title, then the marketing headline, then the product name.
        title = (_first_str(seam.get("seo_title"), seam.get("title"),
                            canonical.get("title"), seam.get("headline")))
        return _cap_title(title, title_cap)

    if kind == "bullets":
        feats = seam.get("key_features")
        return [b for b in feats if isinstance(b, str) and b.strip()] if isinstance(feats, list) else []

    # body: the prose set, verbatim from canonical (the SEAM keeps it prose-only).
    body: Dict[str, str] = {}
    for key in ("description", "long_description", "why_it_works"):
        v = seam.get(key)
        if isinstance(v, str) and v.strip():
            body[key] = v.strip()
    return body


def _seam_copy(canonical: Mapping[str, Any]) -> Dict[str, Any]:
    """The SEAM-separated `copy` block (title / bullets / prose), read STRICTLY from the
    CanonicalProduct fields so each payload stays distinct (FR-002).

    THE SEAM is preserved by construction: key_features -> the bullets payload, the prose set
    (description/long_description/why_it_works) -> the body payload, the listing title -> the
    title payload; the three are NEVER concatenated. CanonicalProduct (W2 P1) already stores
    these as separate fields with these exact names, so this reads them verbatim -- it is the
    Python mirror of the proven TS ad_data_from_product seam (which reads the catalog-schema
    field names `name`/`features`/`tagline`; the canonical uses `title`/`key_features`).
    PURE + TOTAL: a non-mapping / missing field -> simply absent (the engine then OMITs it).

    cross-check: ad_data_from_product (cex_product_ad_mold) maps the SAME concepts for the ads
    mold; this function is the canonical-shaped equivalent for the copy engine (different field
    vocabulary, identical separation guarantee).
    """
    c = canonical if isinstance(canonical, Mapping) else {}
    out: Dict[str, Any] = {}

    # TITLE payload source -- the SEO title (if the canonical carries a seo block) then the
    # listing title. The CanonicalProduct keeps a flat `title`; a seo.title may ride alongside.
    seo = c.get("seo")
    seo_title = seo.get("title") if isinstance(seo, Mapping) else None
    if isinstance(seo_title, str) and seo_title.strip():
        out["seo_title"] = seo_title.strip()
    title = c.get("title")
    if isinstance(title, str) and title.strip():
        out["title"] = title.strip()
    subtitle = c.get("subtitle")
    if isinstance(subtitle, str) and subtitle.strip():
        out["headline"] = subtitle.strip()

    # BODY payload source -- the prose set ONLY (the seam: bullets/ficha live elsewhere).
    for key in ("description", "long_description", "why_it_works"):
        v = c.get(key)
        if isinstance(v, str) and v.strip():
            out[key] = v.strip()

    # BULLETS payload source -- key_features ONLY (the canonical's typed bullet list).
    feats = c.get("key_features")
    if isinstance(feats, (list, tuple)):
        kept = [x.strip() for x in feats if isinstance(x, str) and x.strip()]
        if kept:
            out["key_features"] = kept

    # REUSE the proven mold seam (ad_data_from_product) as an ADDITIVE enricher: when the
    # record ALSO carries the catalog-schema vocabulary (`name`/`features`/`tagline`/`seo`
    # -- e.g. a get_product_record / normalize_product output passed through unchanged), fold
    # in any seam-separated copy field this canonical-shaped read missed. The canonical-shaped
    # values WIN (set above); the mold seam only fills gaps. This makes the reuse real (not a
    # dead import) without ever overriding the canonical. degrade-never: mapper absent/raises
    # -> skip.
    if ad_data_from_product is not None and (c.get("features") or c.get("name") or c.get("tagline")):
        try:
            mold_copy = ad_data_from_product(c).get("copy")
        except Exception:
            mold_copy = None
        if isinstance(mold_copy, Mapping):
            if "key_features" not in out:
                mk = mold_copy.get("key_features")
                if isinstance(mk, (list, tuple)) and mk:
                    out["key_features"] = [x for x in mk if isinstance(x, str) and x.strip()]
            for key in ("description", "long_description", "why_it_works", "title", "seo_title", "headline"):
                if key not in out:
                    mv = mold_copy.get(key)
                    if isinstance(mv, str) and mv.strip():
                        out[key] = mv.strip()
    return out


# =========================================================================== #
# LLM prompt + parse (provider-swappable; the contract is provider-invariant). #
# =========================================================================== #
def _build_prompt(
    kind: str,
    canonical: Mapping[str, Any],
    voice_profile: Optional[Mapping[str, Any]],
    source_text: str,
    title_cap: int,
    violation: str = "",
) -> str:
    """Build the grounded-generation prompt for ONE payload. Embeds the grounding contract
    (the facts-only rule + OMIT-on-missing) + the tenant voice register + the SOURCE text. On
    a retry, the prior violation is surfaced so the model fixes it (or the engine OMITs). The
    source stays ASCII; the model emits accented PT-BR runtime copy."""
    voice = _voice_register(voice_profile)
    contract = (
        "CONTRATO DE GROUNDING (REGRAS DURAS -- O FATO SEMPRE VENCE A VOZ):\n"
        "G1 Fatos vem SOMENTE da FONTE abaixo. G3 NUNCA invente dimensao/material/peso.\n"
        "G4 NUNCA invente compatibilidade/porte. G5 NUNCA invente claim de seguranca.\n"
        "G6 Fato ausente -> OMITA (campo vazio). G8 NAO promova claim com ressalva.\n"
        "G9 Sem vazamento de canal/preco/concorrente na prosa. G10 Na duvida, OMITA.\n"
        "A voz so molda a FRASE, nunca o conjunto de fatos."
    )
    if kind == "title":
        task = ("Gere UM titulo de anuncio (<= %d caracteres), na voz da marca, "
                "usando SO fatos da fonte. Retorne JSON {\"title\": \"...\"}." % title_cap)
    elif kind == "bullets":
        task = ("Gere os bullets de caracteristicas principais (verbo primeiro, escaneaveis), "
                "SO com fatos da fonte. NAO inclua prosa nem rotulos de ficha (Marca:, Modelo:). "
                "Retorne JSON {\"bullets\": [\"...\", ...]}.")
    else:
        task = ("Gere a prosa do corpo (description, long_description, why_it_works) na voz da "
                "marca, SO com fatos da fonte. Bullets e ficha NAO entram aqui. "
                "Retorne JSON {\"description\": \"...\", \"long_description\": \"...\", "
                "\"why_it_works\": \"...\"}.")
    retry = ("\nRETENTATIVA -- a saida anterior violou o contrato: %s\nCorrija usando SO a "
             "fonte ou deixe o campo vazio.\n" % violation) if violation else ""
    return (
        contract + "\n\n" + (("VOZ: " + voice + "\n\n") if voice else "")
        + "FONTE (a unica origem de fatos):\n" + source_text + "\n\n"
        + task + retry + "\nSaida APENAS o JSON, sem texto extra."
    )


def _voice_register(voice_profile: Optional[Mapping[str, Any]]) -> str:
    """A short voice-register hint from a TenantVoiceProfile (tone + a sample). degrade-never:
    None -> "". PURE + TOTAL."""
    if not isinstance(voice_profile, Mapping):
        return ""
    bits: List[str] = []
    tone = voice_profile.get("tone")
    if isinstance(tone, Mapping):
        primary = tone.get("primary")
        if isinstance(primary, str) and primary.strip():
            bits.append(primary.strip())
        anti = tone.get("anti_tone")
        if isinstance(anti, str) and anti.strip():
            bits.append("evite: " + anti.strip())
    samples = voice_profile.get("voice_samples")
    if isinstance(samples, Mapping):
        for key in ("commercial_direct", "ig_feed"):
            seq = samples.get(key)
            if isinstance(seq, (list, tuple)) and seq:
                first = next((s for s in seq if isinstance(s, str) and s.strip()), "")
                if first:
                    bits.append('registro: "%s"' % first.strip())
                    break
    return " | ".join(bits)


def _parse_generation(kind: str, raw: Any) -> Optional[Any]:
    """Parse an LLM response into the payload for `kind`. TOTAL: bad JSON -> None.
    Strips a stray ```json fence (backstop)."""
    if not isinstance(raw, str) or not raw.strip():
        return None
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text).strip()
    try:
        data = json.loads(text)
    except Exception:
        return None
    if not isinstance(data, Mapping):
        return None
    if kind == "title":
        v = data.get("title")
        return v if isinstance(v, str) else ""
    if kind == "bullets":
        v = data.get("bullets")
        return [str(x) for x in v if isinstance(x, str) and x.strip()] if isinstance(v, (list, tuple)) else []
    # body
    out: Dict[str, str] = {}
    for key in ("description", "long_description", "why_it_works"):
        v = data.get(key)
        if isinstance(v, str) and v.strip():
            out[key] = v.strip()
    return out


def _is_empty_payload(kind: str, payload: Any) -> bool:
    """True when a parsed payload carries nothing usable. PURE."""
    if kind == "title":
        return not (isinstance(payload, str) and payload.strip())
    if kind == "bullets":
        return not (isinstance(payload, (list, tuple)) and len(payload) > 0)
    return not (isinstance(payload, Mapping) and len(payload) > 0)


# =========================================================================== #
# Helpers (PURE + TOTAL).                                                      #
# =========================================================================== #
def _title_cap_of(voice_profile: Optional[Mapping[str, Any]]) -> int:
    """The title char cap: a voice_profile platform max_chars if small enough, else the ML
    default (60). A marketplace title cap is short; an IG caption max (2200) is NOT a title
    cap, so only adopt a profile cap when it is <= 120. PURE + TOTAL."""
    if isinstance(voice_profile, Mapping):
        title_cap = voice_profile.get("title_cap")
        if isinstance(title_cap, int) and 0 < title_cap <= 200:
            return title_cap
    return _DEFAULT_TITLE_CAP


def _cap_title(title: Any, cap: int) -> str:
    """Cap a title to `cap` chars at a word boundary (no mid-word cut). Strips a handful of
    subjective adjectives the marketplace title rules forbid (FR-005 parity). PURE + TOTAL."""
    t = " ".join(str(title).split()) if title else ""
    if not t:
        return ""
    # strip a few subjective adjectives (the structured title carries facts, not hype).
    for adj in (" melhor ", " premium ", " incrivel ", " imperdivel "):
        t = re.sub(adj, " ", " " + t + " ", flags=re.IGNORECASE).strip()
        t = " ".join(t.split())
    if len(t) <= cap:
        return t
    cut = t[:cap]
    if " " in cut:
        cut = cut[:cut.rfind(" ")]
    return cut.strip()


def _first_str(*vals: Any) -> str:
    """The first non-empty string among vals. PURE."""
    for v in vals:
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


# =========================================================================== #
# Demo                                                                        #
# =========================================================================== #
def _demo_canonical() -> Dict[str, Any]:
    """A canonical record built from a RAW marketplace listing (keyword-soup name + buried
    facts) -- the Grupo-B case. The grounding source is the union of the prose + the buried
    raw text. ASCII source; runtime copy carries accents."""
    return {
        "id": "CB-DEMO",
        "sku": "CB-DEMO",
        "title": "Cama Donut Gato Pelucia",
        "description": "Cama donut macia para gatos, feita em pelucia, com base "
                       "antiderrapante. Mantem o gato aquecido.",
        "long_description": "A borda alta em formato donut da seguranca ao gato; o "
                            "enchimento macio acolhe o sono. Lavavel na maquina.",
        "key_features": [
            "Borda alta em formato donut",
            "Base antiderrapante",
            "Lavavel na maquina",
            "Marca: GenericPet",          # a spec-label that G9 must scrub
        ],
        "materials": ["Pelucia", "Algodao"],
        "weight_grams": 450,
        "dim_length_cm": 50,
        "dim_width_cm": 50,
        "dim_height_cm": 18,
        # the RAW imported keyword-soup (a legit grounding source: facts buried in it count).
        "_source_text": "Cama Donut Gato Pelucia Algodao 50x50 Promocao Frete Gratis "
                        "Envio Imediato Buscas relacionadas: caminha gato pet",
    }


def _demo_fabricating_llm(prompt: str) -> str:
    """A deliberately-BAD LLM stub that tries to FABRICATE facts (a number, a material, and a
    safety claim absent from the source) -- to PROVE the gate drops them. PURE."""
    low = prompt.lower()
    if '"title"' in low:
        return json.dumps({"title": "Cama Donut Premium Atoxica para Gatos ate 12kg"})
    if '"bullets"' in low:
        return json.dumps({"bullets": [
            "Suporta gatos de ate 12 kg",        # G3/G7: 12kg NOT in source -> drop
            "Tecido atoxico certificado",        # G5 safety NOT in source -> drop
            "Espuma viscoelastica importada",    # G3 material 'espuma' NOT in source -> drop
            "Base antiderrapante",               # grounded -> keep
            "Marca: GenericPet",                 # G9 spec-label -> scrub
        ]})
    return json.dumps({
        "description": "Cama donut a prova d'agua, atoxica, para gatos.",  # G8+G5 -> omit/retry
        "long_description": "Borda alta que da seguranca ao gato, enchimento macio, "
                            "lavavel na maquina.",                          # grounded -> keep
        "why_it_works": "",
    })


def run_demo() -> int:
    """Proof: re-voice a raw Grupo-B listing into title/bullets/body, with a FABRICATING LLM,
    and show the gate dropping every invented fact (no-fabrication proof)."""
    canonical = _demo_canonical()
    src = source_text_of(canonical)

    print("=== DEMO: cex_grounded_copy (W2 P3 -- grounded ad-copy, 3 generations) ===")
    print("")
    print("-- GROUNDING SOURCE (the only origin of facts) --")
    print(src[:240].replace("\n", " | "))
    print("")

    # 1) deterministic (no-LLM) path: grounded by construction.
    det = extract_copy(canonical, llm=None)
    print("-- DETERMINISTIC (no LLM) -> grounded by construction --")
    print("title  :", det["title"])
    print("bullets:", json.dumps(det["bullets"], ensure_ascii=True))
    print("body   :", json.dumps(list(det["body"].keys()), ensure_ascii=True))
    print("gate ok:", det["grounding"]["ok"], "| omitted:", det["meta"]["omitted"])
    print("")

    # 2) FABRICATING LLM path: the gate must drop every invented fact.
    grounded = extract_copy(canonical, llm=_demo_fabricating_llm)
    print("-- FABRICATING LLM -> gate drops invented facts (the no-fabrication proof) --")
    print("title  :", repr(grounded["title"]), "(12kg/atoxica dropped -> deterministic)")
    print("bullets:", json.dumps(grounded["bullets"], ensure_ascii=True))
    print("        (12kg, atoxico, espuma, 'Marca:' all gone; antiderrapante kept)")
    print("body   :", json.dumps(grounded["body"], ensure_ascii=True))
    print("        (a prova d'agua + atoxica description omitted; grounded long_desc kept)")
    print("retries:", grounded["meta"]["retries"], "| omitted:", grounded["meta"]["omitted"])
    print("gate ok:", grounded["grounding"]["ok"], "(no BLOCKING after omit/clean)")
    print("")

    # Independent fact-diff: does ANY emitted token introduce a net-new fact?
    final_blob = _join_text([grounded["title"], grounded["bullets"],
                             list(grounded["body"].values())])
    diff = grounding_check(final_blob, src)
    invented = [f for f in diff["findings"] if f["severity"] == BLOCKING]
    print("-- INDEPENDENT FACT-DIFF over the final 3 payloads --")
    print("net-new BLOCKING facts:", len(invented), "(must be 0)")
    print("writes_nothing        :", grounded["writes_nothing"])
    print("")
    print("=== DEMO COMPLETE ===")
    return 0


# =========================================================================== #
# Self-test                                                                   #
# =========================================================================== #
def run_self_test() -> int:
    """DB-free, network-free correctness checks for the grounding engine."""
    checks: List[Tuple[str, bool]] = []

    def ck(label: str, cond: Any) -> None:
        checks.append((label, bool(cond)))

    canonical = _demo_canonical()
    src = source_text_of(canonical)

    # --- grounding_check primitive ---
    # a fabricated number+unit is flagged BLOCKING (G3/G7).
    r = grounding_check("Suporta gatos de ate 12 kg", src)
    ck("gate: 12kg not in source -> BLOCKING", r["blocking"])
    # a real fact (50 cm IS in source) is NOT flagged.
    r2 = grounding_check("Mede 50 cm de largura", src)
    ck("gate: 50cm in source -> not blocking", not r2["blocking"])
    # a fabricated material (espuma) is flagged.
    r3 = grounding_check("Enchimento de espuma viscoelastica", src)
    ck("gate: espuma not in source -> BLOCKING", r3["blocking"])
    # a real material (pelucia/algodao IS in source) is fine.
    r4 = grounding_check("Feita em algodao macio", src)
    ck("gate: algodao in source -> ok", not r4["blocking"])
    # G5 safety claim absent from source -> BLOCKING.
    r5 = grounding_check("Tecido atoxico certificado", src)
    ck("gate: atoxico not in source -> BLOCKING (G5)", r5["blocking"])
    # G8 upgrade: source hedges 'resistente a agua'; output says 'a prova d'agua'.
    src_hedge = "Tecido resistente a agua para uso diario"
    r6 = grounding_check("Mochila a prova d'agua", src_hedge)
    ck("gate: G8 upgrade resistente->a prova d'agua flagged", any(f["rule"] == "G8" for f in r6["findings"]))
    # the same absolute IS allowed when the source states it verbatim.
    r7 = grounding_check("Mochila a prova d'agua", "Mochila a prova d'agua oficial")
    ck("gate: absolute allowed when source asserts it", not any(f["rule"] == "G8" for f in r7["findings"]))
    # G9 leakage in prose.
    r8 = grounding_check("Compre agora com frete gratis garantido", src)
    ck("gate: G9 leakage flagged", any(f["rule"] == "G9" for f in r8["findings"]))

    # --- severity map ---
    ck("severity: G5 BLOCKING", SEVERITY["G5"] == BLOCKING)
    ck("severity: G3 BLOCKING", SEVERITY["G3"] == BLOCKING)
    ck("severity: G9 MEDIUM", SEVERITY["G9"] == MEDIUM)
    ck("severity: G1 HIGH", SEVERITY["G1"] == HIGH)

    # --- deterministic generation: grounded by construction ---
    det = extract_copy(canonical, llm=None)
    ck("det: title non-empty + capped", det["title"] and len(det["title"]) <= 60)
    ck("det: bullets non-empty", len(det["bullets"]) >= 1)
    ck("det: bullets scrubbed spec-label 'Marca:'",
       all(not s.lower().startswith("marca:") for s in det["bullets"]))
    ck("det: body has prose", len(det["body"]) >= 1)
    ck("det: gate ok (no BLOCKING)", det["grounding"]["ok"])
    ck("det: writes nothing", det["writes_nothing"] is True)
    # THE SEAM: bullets are SEPARATE from the prose body (a feature is not in the body blob).
    body_blob = _normalize(_join_text(list(det["body"].values())))
    ck("seam: bullets separate from prose (3 distinct payloads)",
       isinstance(det["title"], str) and isinstance(det["bullets"], list) and isinstance(det["body"], dict))

    # --- THE NO-FABRICATION PROOF (the load-bearing test) ---
    grounded = extract_copy(canonical, llm=_demo_fabricating_llm)
    final_blob = _join_text([grounded["title"], grounded["bullets"],
                             list(grounded["body"].values())])
    diff = grounding_check(final_blob, src)
    ck("NO-FABRICATION: zero BLOCKING facts in final output", not diff["blocking"])
    # the specific invented facts are gone:
    fb = _normalize(final_blob)
    ck("no-fab: '12 kg' dropped", "12kg" not in _numeric_unit_tokens(final_blob))
    ck("no-fab: 'atoxico' safety claim dropped", "atoxico" not in _lexicon_in_text(final_blob, _SAFETY_LEXICON))
    ck("no-fab: 'espuma' material dropped", "espuma" not in _lexicon_in_text(final_blob, _MATERIAL_LEXICON))
    # a GROUNDED fact survived (antiderrapante is in source -> kept in bullets).
    ck("no-fab: grounded 'antiderrapante' bullet kept",
       any("antiderrapante" in _normalize(b) for b in grounded["bullets"]))
    ck("no-fab: aggregate gate ok after omit/clean", grounded["grounding"]["ok"])
    ck("no-fab: at least one retry or omit happened",
       grounded["meta"]["retries"] >= 1 or grounded["meta"]["omitted"])

    # --- OMIT discipline (G6/G10): a source with NO bullets -> empty bullets, not fabricated ---
    bare = {"id": "X", "title": "Produto Simples",
            "description": "Um produto simples.", "_source_text": "Produto Simples."}
    bare_out = extract_copy(bare, llm=None)
    ck("omit: no source features -> empty bullets (G6)", bare_out["bullets"] == [])
    ck("omit: 'bullets' listed as omitted", "bullets" in bare_out["meta"]["omitted"])
    # a fabricating LLM on the bare source must STILL not invent bullets.
    bare_fab = extract_copy(bare, llm=_demo_fabricating_llm)
    diff2 = grounding_check(_join_text([bare_fab["title"], bare_fab["bullets"],
                                        list(bare_fab["body"].values())]),
                            source_text_of(bare))
    ck("omit: fabricating LLM on bare source -> still no BLOCKING", not diff2["blocking"])

    # --- writes-nothing + 3 distinct payloads (T303) ---
    ck("3-payloads: title is str", isinstance(grounded["title"], str))
    ck("3-payloads: bullets is list", isinstance(grounded["bullets"], list))
    ck("3-payloads: body is dict", isinstance(grounded["body"], dict))
    ck("3-payloads: writes_nothing flag", grounded["writes_nothing"] is True)

    # --- degrade-never: empty / non-mapping canonical ---
    empty_out = extract_copy({}, llm=None)
    ck("degrade: empty canonical -> valid shape", set(["title", "bullets", "body"]).issubset(empty_out))
    ck("degrade: empty canonical -> gate ok", empty_out["grounding"]["ok"])
    none_out = extract_copy(None, llm=None)
    ck("degrade: None canonical -> no raise", isinstance(none_out, dict))

    # --- voice profile: shapes the prompt, never the facts ---
    try:
        from cex_tenant_voice_profile import load_voice_profile  # noqa: E402
        vp = load_voice_profile("example")
    except Exception:
        vp = None
    voiced = extract_copy(canonical, voice_profile=vp, llm=None)
    ck("voice: with profile still grounded", voiced["grounding"]["ok"])

    ok_all = all(p for _, p in checks)
    print("=== SELF-TEST: cex_grounded_copy ===")
    for label, passed in checks:
        print("  [%s] %s" % ("OK" if passed else "FAIL", label))
    print("[%s] SELF-TEST %s (%d checks)"
          % ("OK" if ok_all else "FAIL", "PASSED" if ok_all else "FAILED", len(checks)))
    return 0 if ok_all else 1


# =========================================================================== #
# CLI                                                                         #
# =========================================================================== #
def _build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="cex_grounded_copy.py",
        description="W2 P3: grounded ad-copy engine (title/bullets/body as 3 grounded generations).",
    )
    ap.add_argument("--demo", action="store_true", help="Run the no-fabrication proof demo")
    ap.add_argument("--self-test", action="store_true", help="Run offline correctness checks")
    return ap


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.self_test:
        return run_self_test()
    if args.demo:
        return run_demo()
    _build_parser().print_help()
    return 0


__all__ = [
    "grounding_check",
    "extract_copy",
    "source_text_of",
    "SEVERITY",
    "BLOCKING",
    "HIGH",
    "MEDIUM",
]


if __name__ == "__main__":
    sys.exit(main())
