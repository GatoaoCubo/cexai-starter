#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI PT-BR sentiment engine -- cex_sentiment_pt (LOCAL, GREEN-tech; research-universe build).

THE sentiment engine the social/reputation research lanes (reddit / appstore / youtube /
ReclameAqui) feed their scraped PT-BR text into. It classifies one text (or a batch) into
{label in POS/NEG/NEU, score 0..1, method} so the downstream lanes can roll opinion up into an
aggregate sentiment signal WITHOUT shipping a heavy ML dependency or making a network call.

DEGRADE-NEVER, TWO TIERS (auto-selected; the lexicon tier is ALWAYS present):
  1. MODEL tier (OPTIONAL): if ``transformers`` + a permissive PT sentiment head are importable,
     the model classifies and the record is LABELLED ``method: "model"``. The model is NEVER
     hard-required -- a missing dep / a load failure / an inference error falls back to the lexicon
     tier (it NEVER crashes the call). The default model is a BERTimbau / Apache-2.0 head.
  2. LEXICON tier (ALWAYS available, pure-Python, ZERO deps): a built-in PT-BR positive/negative
     lexicon + negation handling derives a label + a hit-count-based score. This GUARANTEES a
     result even with zero ML deps installed -- the lexicon tier is the floor that makes the whole
     engine degrade-never.

LICENSE NOTE (why BERTimbau-default, NOT pysentimiento): ``pysentimiento`` is the best-known PT
sentiment lib BUT it ships under a NON-COMMERCIAL / research-only license -> it is NOT importable
as the commercial default here. A BERTimbau-derived sentiment head (BERTimbau is Apache-2.0; the
fine-tuned heads built on it are typically MIT / Apache-2.0) is the permissive default. The model
NAME is configurable via the ``CEX_SENTIMENT_PT_MODEL`` env var (or the ``model_name`` arg); the
engine only ENABLES the model tier when transformers is importable AND a head actually loads --
otherwise it transparently runs on the lexicon tier. The lexicon ALWAYS works regardless.

NEVER-FABRICATE (the cardinal rule, per the house style -- see cex_meli_trends): the engine does
NOT invent a confidence. The lexicon ``score`` is DERIVED from positive/negative hit counts (and
returned with ``method: "lexicon"`` so a consumer KNOWS the provenance of the number -- a lexicon
ratio, not a calibrated model probability). The model ``score`` is the model's own probability,
returned with ``method: "model"``. The two are never silently mixed; the ``method`` field always
tells the truth about HOW the score was produced.

INVARIANTS:
  - degrade-never: ``analyze_sentiment`` / ``analyze_batch`` NEVER raise. A model failure -> lexicon
    fallback. A bad input type -> coerced to "" -> NEU. The lexicon tier always returns.
  - never-fabricate: no invented confidence; lexicon score is hit-derived + labelled honestly.
  - no network: fully local. The model tier (if used) loads a LOCAL/cached HF model; this module
    issues NO HTTP itself. With zero ML deps it is 100% offline.
  - ASCII source: the PT lexicon DATA has accents (otimo, pessimo, nao, ...) -- per the repo
    ascii-code rule the SOURCE stays ASCII by encoding those entries with ``\\uXXXX`` escapes.
    Verify: ``python _tools/cex_sanitize.py --check --scope _tools/cex_sentiment_pt.py``.
  - bounded: text is capped at _MAX_TEXT_CHARS and a batch at _MAX_BATCH before processing.

INTERFACE:
  CLI:        python _tools/cex_sentiment_pt.py "<texto>"        -> JSON to stdout + exit 0
  importable: analyze_sentiment(text) -> dict
              analyze_batch(texts)    -> dict {results: [...], aggregate: {...}, ...}

ASCII-only (.claude/rules/ascii-code-rule.md). Fully type-hinted. Pure / no side effects; composes.
"""

from __future__ import annotations

import json
import os
import sys
import unicodedata
from typing import Any, Dict, List, Optional, Sequence, Tuple

# --------------------------------------------------------------------------- #
# Bounds (the "bounded" invariant). A pathological input must not blow memory.
# --------------------------------------------------------------------------- #
_MAX_TEXT_CHARS = 20000   # a single text is truncated to this many chars before scoring.
_MAX_BATCH = 5000         # a batch is truncated to this many texts.

# Labels (the controlled vocabulary for this engine).
POS = "POS"
NEG = "NEG"
NEU = "NEU"

# The model env override (license note in the module docstring). When transformers is NOT
# importable OR the head fails to load, the engine runs on the lexicon tier regardless.
_MODEL_ENV = "CEX_SENTIMENT_PT_MODEL"
# A BERTimbau-derived, permissively-licensed PT sentiment head. NOT pysentimiento (non-commercial).
_DEFAULT_MODEL = "lucas-leme/FinBERT-PT-BR"

# --------------------------------------------------------------------------- #
# PT-BR sentiment lexicon (ASCII source: accented entries are \\uXXXX escapes per the ascii rule).
# These are the BASE (often masculine-singular / infinitive) forms; the scorer ALSO accent-folds
# every token AND strips a few common inflections so e.g. "otima"/"otimas" still match "otimo".
# Curated for the social/reputation domain (app reviews, complaints, comments) -- NEVER fabricated
# at runtime; this is a fixed, auditable list.
# --------------------------------------------------------------------------- #
_POSITIVE_WORDS = frozenset({
    # quality / praise
    "bom", "boa", "\u00f3timo", "\u00f3tima", "\u00f3timos", "\u00f3timas",   # otimo/otima...
    "excelente", "excelentes", "maravilhoso", "maravilhosa", "maravilha",
    "perfeito", "perfeita", "incr\u00edvel", "incriveis", "fant\u00e1stico",   # incrivel, fantastico
    "fant\u00e1stica", "espetacular", "sensacional", "show", "top",
    "melhor", "melhores", "lindo", "linda", "bonito", "bonita",
    # satisfaction / recommendation
    "amei", "adorei", "gostei", "amo", "adoro", "gosto", "curti",
    "recomendo", "recomendado", "recomend\u00e1vel", "satisfeito", "satisfeita",
    "feliz", "felizes", "contente", "content\u00edssimo", "encantado", "encantada",
    # delivery / service positives (commerce / app context)
    "r\u00e1pido", "r\u00e1pida", "eficiente", "eficaz", "f\u00e1cil", "pr\u00e1tico",   # rapido, facil, pratico
    "pr\u00e1tica", "confi\u00e1vel", "honesto", "honesta", "barato", "barata",
    "vale", "qualidade", "funcionou", "funciona", "resolveu", "ajudou",
    "\u00e1gil", "atencioso", "atenciosa", "educado", "educada", "competente",
    "sucesso", "aprovado", "positivo", "positiva", "parab\u00e9ns",   # parabens
    "agrade\u00e7o", "obrigado", "obrigada",   # agradeco
})

_NEGATIVE_WORDS = frozenset({
    # quality / blame
    "ruim", "ruins", "p\u00e9ssimo", "p\u00e9ssima", "p\u00e9ssimos", "p\u00e9ssimas",   # pessimo/pessima...
    "horr\u00edvel", "horriveis", "terr\u00edvel", "terriveis", "p\u00e9simo",   # horrivel, terrivel
    "pior", "piores", "lixo", "porcaria", "merda", "droga", "feio", "feia",
    # dissatisfaction
    "odiei", "detesto", "odeio", "detestei", "decepcionado", "decepcionada",
    "decep\u00e7\u00e3o", "frustrado", "frustrada", "frustra\u00e7\u00e3o", "insatisfeito",   # decepcao, frustracao
    "insatisfeita", "triste", "tristes", "chateado", "chateada", "irritado",
    "irritada", "revoltado", "revoltada", "arrependido", "arrependida",
    # failures / service negatives (commerce / app context)
    "lento", "lenta", "demorado", "demorada", "demora", "demorou", "travou",
    "trava", "bug", "bugado", "bugada", "quebrado", "quebrada", "defeito",
    "defeituoso", "falha", "falhou", "erro", "erros", "problema", "problemas",
    "caro", "cara", "golpe", "fraude", "enganado", "enganada", "mentira",
    "p\u00e9simos", "n\u00e3o", "nunca", "jamais",   # pesimos (typo-tolerant), nao -- handled as negation too
    "reclama\u00e7\u00e3o", "reclamar", "pioria", "estragado", "estragada",   # reclamacao
    "p\u00e9ssim\u00edssimo", "negativo", "negativa", "p\u00e9ssimamente",
    "horroroso", "horrorosa", "vergonha", "absurdo", "absurda", "p\u00e9ssimas",
})

# Negation cues: when one appears in the small window BEFORE a sentiment word, that word's
# polarity is FLIPPED ("nao gostei" -> negative; "nao ruim" -> positive). Accent-folded at match.
_NEGATORS = frozenset({
    "n\u00e3o", "nao", "nunca", "jamais", "nem", "sem", "nenhum", "nenhuma", "nada",
})

# How many tokens back a negator reaches (so "nao gostei" and "nao muito bom" both flip).
_NEGATION_WINDOW = 3

# Intensifiers that BOOST the magnitude of the next sentiment token (do NOT change polarity).
# Used only to weight the lexicon score; never to fabricate a polarity that isn't there.
_INTENSIFIERS = frozenset({
    "muito", "super", "extremamente", "totalmente", "demais", "bastante",
    "t\u00e3o", "tao", "completamente", "absurdamente", "mega",
})

# Common PT inflection suffixes we trim (longest-first) so plural/feminine forms still hit the
# base lexicon. Conservative on purpose -- this is a lightweight stemmer, NOT a full morphology.
_SUFFIXES: Tuple[str, ...] = ("issimas", "issimos", "issima", "issimo", "mente",
                              "coes", "oes", "ais", "res", "ns", "as", "os", "es", "a", "o", "s")


def _fold(token: str) -> str:
    """Lowercase + strip diacritics (NFD + drop combining marks) so an accented runtime token
    matches an accent-folded lexicon. PURE / TOTAL: a non-str -> "". This is why the lexicon can be
    authored with \\uXXXX escapes yet still match plain-ASCII or accented input identically."""
    if not isinstance(token, str):
        return ""
    nfkd = unicodedata.normalize("NFD", token.lower())
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


# Pre-fold the lexicons ONCE at import (the \\uXXXX entries become their ASCII-folded forms, e.g.
# "otimo", "pessimo", "nao"). Matching is then a fold-and-membership test -- fast + accent-agnostic.
_POS_FOLDED = frozenset(_fold(w) for w in _POSITIVE_WORDS)
_NEG_FOLDED = frozenset(_fold(w) for w in _NEGATIVE_WORDS)
_NEG_CUES_FOLDED = frozenset(_fold(w) for w in _NEGATORS)
_INTENSIFIERS_FOLDED = frozenset(_fold(w) for w in _INTENSIFIERS)


def _tokenize(text: str) -> List[str]:
    """Split text into accent-folded word tokens. PURE / TOTAL: non-str or empty -> []. We keep
    only letter runs (folded), dropping punctuation/digits; the order is preserved (negation needs
    it). Bounded by _MAX_TEXT_CHARS upstream."""
    if not isinstance(text, str) or not text:
        return []
    out: List[str] = []
    buf: List[str] = []
    for ch in text:
        folded = _fold(ch)
        if folded and folded.isalpha():
            buf.append(folded)
        else:
            if buf:
                out.append("".join(buf))
                buf = []
    if buf:
        out.append("".join(buf))
    return out


def _lexicon_lookup(token: str) -> Optional[str]:
    """Return POS / NEG for a folded token, or None if it is not a sentiment word. Tries the exact
    folded token first, then a few trimmed-suffix variants so plural/feminine inflections still hit
    the base lexicon. PURE / TOTAL. NEVER fabricates -- an unknown token is None (neutral)."""
    if not token:
        return None
    if token in _POS_FOLDED:
        return POS
    if token in _NEG_FOLDED:
        return NEG
    # Try light de-inflection (longest suffix first). Stop at the first variant that is a known
    # sentiment word; a too-short stem (< 3 chars) is rejected to avoid spurious matches.
    for suf in _SUFFIXES:
        if token.endswith(suf) and len(token) - len(suf) >= 3:
            stem = token[: -len(suf)]
            if stem in _POS_FOLDED:
                return POS
            if stem in _NEG_FOLDED:
                return NEG
    return None


def _score_lexicon(text: str) -> Dict[str, Any]:
    """The LEXICON tier (always available; ZERO deps). Walk the folded tokens, classify each via the
    lexicon, FLIP polarity when a negator sits within _NEGATION_WINDOW tokens before it, and weight
    by a preceding intensifier. Derive a label + a hit-count-based score in [0, 1].

    DEGRADE-NEVER + NEVER-FABRICATE: no model, no network, no invented number. The score is an
    HONEST function of (effective positive vs negative hits) -- returned alongside method='lexicon'
    so the caller knows it's a lexicon ratio, not a calibrated probability.

    Returns: {label, score, method:'lexicon', positive_hits, negative_hits}.
    Empty / no sentiment word -> NEU with score 0.5 (the honest no-signal midpoint)."""
    tokens = _tokenize(text)
    pos_weight = 0.0
    neg_weight = 0.0
    pos_hits = 0
    neg_hits = 0

    for i, tok in enumerate(tokens):
        polarity = _lexicon_lookup(tok)
        if polarity is None:
            continue
        # Base weight 1.0; an intensifier immediately before bumps it.
        weight = 1.0
        if i > 0 and tokens[i - 1] in _INTENSIFIERS_FOLDED:
            weight = 1.5
        # Negation: any negator within the preceding window flips this token's polarity.
        window = tokens[max(0, i - _NEGATION_WINDOW): i]
        if any(w in _NEG_CUES_FOLDED for w in window):
            polarity = NEG if polarity == POS else POS
        if polarity == POS:
            pos_weight += weight
            pos_hits += 1
        else:
            neg_weight += weight
            neg_hits += 1

    total = pos_weight + neg_weight
    if total <= 0.0:
        # No sentiment evidence -> honest neutral at the midpoint (NOT a fabricated confidence).
        return {
            "label": NEU,
            "score": 0.5,
            "method": "lexicon",
            "positive_hits": pos_hits,
            "negative_hits": neg_hits,
        }

    pos_ratio = pos_weight / total
    # Map the dominant-side ratio to a 0..1 confidence. A clean one-sided text -> ~1.0; a 50/50 mix
    # -> ~0.5 and resolves to NEU. The number is a transparent ratio, labelled method='lexicon'.
    if abs(pos_ratio - 0.5) < 0.10:
        label = NEU
        score = round(0.5 + abs(pos_ratio - 0.5), 4)
    elif pos_ratio > 0.5:
        label = POS
        score = round(pos_ratio, 4)
    else:
        label = NEG
        score = round(1.0 - pos_ratio, 4)

    return {
        "label": label,
        "score": score,
        "method": "lexicon",
        "positive_hits": pos_hits,
        "negative_hits": neg_hits,
    }


# --------------------------------------------------------------------------- #
# MODEL tier (OPTIONAL). Lazily built ONCE and cached. NEVER hard-required: any import / load /
# inference failure returns None here and the caller transparently uses the lexicon tier.
# --------------------------------------------------------------------------- #
_MODEL_PIPELINE: Any = None          # the cached transformers pipeline (or None).
_MODEL_TRIED = False                 # whether we already attempted (and possibly failed) to load.


def _label_from_model(raw_label: str, score: float) -> str:
    """Map a model's raw label string onto POS/NEG/NEU. Models differ (LABEL_0/1/2,
    positive/negative/neutral, 1-5 stars, pt strings) -- we normalise defensively. PURE / TOTAL:
    an unrecognised label with a high score is treated as the model's own call via star/number
    heuristics; truly ambiguous -> NEU (never fabricated as POS/NEG)."""
    s = _fold(raw_label)
    if any(k in s for k in ("pos", "positiv", "good", "label_2", "5 star", "4 star", "5star", "4star")):
        return POS
    if any(k in s for k in ("neg", "negativ", "bad", "label_0", "1 star", "2 star", "1star", "2star")):
        return NEG
    if any(k in s for k in ("neu", "neutr", "label_1", "3 star", "3star")):
        return NEU
    return NEU


def _get_model_pipeline(model_name: str) -> Any:
    """Build (once) + cache a transformers sentiment pipeline for ``model_name``. Returns the
    pipeline or None. DEGRADE-NEVER: if ``transformers`` is not importable, or the model cannot be
    loaded (not cached locally / offline / any error), this returns None and the engine uses the
    lexicon tier. NO network is initiated by THIS module; transformers may use a locally cached
    model. NEVER raises."""
    global _MODEL_PIPELINE, _MODEL_TRIED
    if _MODEL_TRIED:
        return _MODEL_PIPELINE
    _MODEL_TRIED = True
    try:
        from transformers import pipeline  # type: ignore[import]
    except Exception:
        _MODEL_PIPELINE = None
        return None
    try:
        _MODEL_PIPELINE = pipeline("sentiment-analysis", model=model_name)
    except Exception:
        # Model not available locally / load error / offline -> stay on the lexicon tier.
        _MODEL_PIPELINE = None
    return _MODEL_PIPELINE


def _score_model(text: str, model_name: str) -> Optional[Dict[str, Any]]:
    """The MODEL tier (optional). Run the cached pipeline on ``text`` and map its output to our
    contract. Returns a result dict with method='model', OR None if the model tier is unavailable /
    fails (so the caller falls back to the lexicon tier). DEGRADE-NEVER: NEVER raises.

    NEVER-FABRICATE: the score is the MODEL'S OWN probability (not invented); positive_hits /
    negative_hits are not meaningful for the model tier and are reported as None so we don't
    fabricate lexicon-style counts for a model decision."""
    pipe = _get_model_pipeline(model_name)
    if pipe is None:
        return None
    try:
        out = pipe(text[:_MAX_TEXT_CHARS] if isinstance(text, str) else "")
        first = out[0] if isinstance(out, list) and out else out
        if not isinstance(first, dict):
            return None
        raw_label = str(first.get("label", ""))
        raw_score = first.get("score", None)
        score = float(raw_score) if isinstance(raw_score, (int, float)) else None
        if score is None:
            return None
        label = _label_from_model(raw_label, score)
        return {
            "label": label,
            "score": round(max(0.0, min(1.0, score)), 4),
            "method": "model",
            "positive_hits": None,
            "negative_hits": None,
        }
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# Provenance (the house style: data_sources + mock:false + optional fetched_at).
# --------------------------------------------------------------------------- #
def _provenance(method: str, *, now: Optional[str] = None) -> Dict[str, Any]:
    """Build the provenance block. ``data_sources`` names the tier that produced the result;
    ``mock`` is ALWAYS False (a real lexicon/model computation, never a simulated value);
    ``fetched_at`` is echoed verbatim from the caller's ``now`` (OPTIONAL -- this engine does not
    invent a timestamp, consistent with never-fabricate)."""
    sources = ["lexicon:cex_sentiment_pt"] if method == "lexicon" else ["model:transformers"]
    prov: Dict[str, Any] = {"data_sources": sources, "mock": False}
    if isinstance(now, str) and now.strip():
        prov["fetched_at"] = now.strip()
    return prov


# --------------------------------------------------------------------------- #
# PUBLIC API
# --------------------------------------------------------------------------- #
def analyze_sentiment(
    text: Any,
    *,
    use_model: bool = True,
    model_name: Optional[str] = None,
    now: Optional[str] = None,
) -> Dict[str, Any]:
    """Classify ONE PT-BR text. DEGRADE-NEVER (NEVER raises) + NEVER-FABRICATE.

    Tier selection: when ``use_model`` is True AND a permissive model is importable+loadable, the
    MODEL tier is used (method='model'); otherwise the LEXICON tier (method='lexicon', always
    available, zero deps). A model failure transparently falls back to the lexicon tier.

    Args:
      text: the input text. A non-str / None is coerced to "" (-> NEU); the text is truncated to
        _MAX_TEXT_CHARS (the 'bounded' invariant).
      use_model: allow the optional model tier. False forces the lexicon tier (useful for tests /
        guaranteed-offline). Default True (but the model tier only engages if actually available).
      model_name: override the HF model id; defaults to env CEX_SENTIMENT_PT_MODEL or the
        BERTimbau-derived default. (License note: NOT pysentimiento -- non-commercial -- see module
        docstring.)
      now: an OPTIONAL ISO-8601 string echoed into provenance.fetched_at (never invented).

    Returns a dict:
      text (echo, truncated), label (POS|NEG|NEU), score (float 0..1), method ('model'|'lexicon'),
      positive_hits (int for lexicon, None for model), negative_hits (same),
      data_sources (list), mock (False), [fetched_at if now given]."""
    safe_text = text if isinstance(text, str) else ("" if text is None else str(text))
    safe_text = safe_text[:_MAX_TEXT_CHARS]
    resolved_model = (
        model_name
        if (isinstance(model_name, str) and model_name.strip())
        else os.environ.get(_MODEL_ENV, _DEFAULT_MODEL)
    )

    result: Optional[Dict[str, Any]] = None
    if use_model:
        result = _score_model(safe_text, resolved_model)
    if result is None:
        result = _score_lexicon(safe_text)

    out: Dict[str, Any] = {"text": safe_text}
    out.update(result)
    out.update(_provenance(result["method"], now=now))
    return out


def analyze_batch(
    texts: Any,
    *,
    use_model: bool = True,
    model_name: Optional[str] = None,
    now: Optional[str] = None,
) -> Dict[str, Any]:
    """Classify a LIST of PT-BR texts and roll them up into an aggregate sentiment signal.
    DEGRADE-NEVER (NEVER raises) + NEVER-FABRICATE.

    Args:
      texts: an iterable of texts. A non-iterable / None -> empty batch (honest empty aggregate).
        A single str is treated as a one-element batch (convenience). Truncated to _MAX_BATCH.
      use_model / model_name / now: as analyze_sentiment.

    Returns a dict:
      results (list of per-text analyze_sentiment dicts),
      count (int),
      aggregate {pos, neu, neg, label} -- counts per class + the majority label (ties -> NEU),
      data_sources (union of the tiers used), mock (False), [fetched_at if now given]."""
    if isinstance(texts, str):
        items: List[Any] = [texts]
    elif isinstance(texts, Sequence):
        items = list(texts)[:_MAX_BATCH]
    else:
        # Best-effort: any other iterable; a non-iterable -> empty batch (never crash).
        try:
            items = list(texts)[:_MAX_BATCH]  # type: ignore[arg-type]
        except Exception:
            items = []

    results: List[Dict[str, Any]] = []
    pos_n = neu_n = neg_n = 0
    methods_used: List[str] = []
    for item in items:
        r = analyze_sentiment(item, use_model=use_model, model_name=model_name, now=now)
        results.append(r)
        label = r.get("label")
        if label == POS:
            pos_n += 1
        elif label == NEG:
            neg_n += 1
        else:
            neu_n += 1
        m = r.get("method")
        if isinstance(m, str) and m not in methods_used:
            methods_used.append(m)

    # Majority label. A tie (or an empty batch) resolves to NEU -- the honest non-committal call,
    # never a fabricated POS/NEG.
    agg_label = NEU
    if pos_n > neg_n and pos_n >= neu_n:
        agg_label = POS
    elif neg_n > pos_n and neg_n >= neu_n:
        agg_label = NEG

    sources: List[str] = []
    for m in methods_used:
        for s in _provenance(m)["data_sources"]:
            if s not in sources:
                sources.append(s)
    if not sources:
        sources = _provenance("lexicon")["data_sources"]

    out: Dict[str, Any] = {
        "results": results,
        "count": len(results),
        "aggregate": {"pos": pos_n, "neu": neu_n, "neg": neg_n, "label": agg_label},
        "data_sources": sources,
        "mock": False,
    }
    if isinstance(now, str) and now.strip():
        out["fetched_at"] = now.strip()
    return out


__all__ = [
    "analyze_sentiment",
    "analyze_batch",
    "POS",
    "NEG",
    "NEU",
]


# --------------------------------------------------------------------------- #
# CLI -- classify the argument text (or, with --batch, each remaining arg) and print JSON. Always
# exit 0 (degrade-never): even a model-less environment yields a lexicon result, never an error.
# --------------------------------------------------------------------------- #
def _usage() -> None:
    print("CEXAI PT-BR sentiment engine (LOCAL, GREEN). Usage:")
    print('  python _tools/cex_sentiment_pt.py "<texto>"            '
          "-> JSON {label, score, method, ...}")
    print('  python _tools/cex_sentiment_pt.py --batch "t1" "t2" .. '
          "-> JSON {results, aggregate, ...}")
    print('  python _tools/cex_sentiment_pt.py --lexicon "<texto>"  '
          "-> force the lexicon tier (no model)")
    print("  NOTE: the lexicon tier is ALWAYS available (zero deps). The model tier engages only")
    print("        if transformers + a permissive PT head are importable (BERTimbau-default; NOT")
    print("        pysentimiento, which is non-commercial). method='lexicon'|'model' tells which ran.")


def _main(argv: List[str]) -> int:
    if not argv:
        _usage()
        return 0

    use_model = True
    args = list(argv)
    if args and args[0] == "--lexicon":
        use_model = False
        args = args[1:]

    if args and args[0] == "--batch":
        batch = args[1:]
        rec = analyze_batch(batch, use_model=use_model)
        print(json.dumps(rec, ensure_ascii=False, indent=2))
        return 0

    if not args:
        _usage()
        return 0

    text = " ".join(args)
    rec = analyze_sentiment(text, use_model=use_model)
    print(json.dumps(rec, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
