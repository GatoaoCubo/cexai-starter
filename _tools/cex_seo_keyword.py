#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI SEO / keyword research lane -- cex_seo_keyword (GREEN/YELLOW; research-universe build).

THE SEO/keyword lane. The "build the extraction logic, RENT the volume" approach: this module
OWNS two cheap-or-free capabilities -- (1) keyword DISCOVERY off Google Autocomplete (keyless,
YELLOW-tolerant) and (2) keyphrase EXTRACTION from a text/corpus (a degrade-never tier stack that
ALWAYS works, even with zero ML deps). It does NOT own keyword VOLUME (monthly search counts):
that is an Ahrefs/SEMrush BUY -- so ``volume`` is left an honest documented ``null`` stub and is
NEVER invented (see ``_VOLUME_NOTE`` + the volume field on every record).

TWO FUNCTIONS:
  1. autocomplete(seed)        -- ranked Google Autocomplete suggestions for a seed, PLUS an
     ``alphabet_soup`` expansion (seed + each a-z -> more suggestions, BOUNDED) and ``questions``
     (PT question prefixes "como/o que/qual/quanto/onde" + seed -> their suggestions). Keyless,
     YELLOW-tolerant: on ANY fetch failure the affected branch is an HONEST empty list + a recorded
     'blocked' status -- it NEVER fabricates a suggestion.
  2. extract_keyphrases(text)  -- ranked keyphrases from free text. DEGRADE-NEVER TIERS:
     KeyBERT (if importable) -> else YAKE (if importable) -> else a pure-Python statistical
     fallback (RAKE-ish: PT stopword removal + candidate n-grams scored by word degree/frequency).
     The statistical tier is the FLOOR that guarantees a ranked result with ZERO ML deps. The
     ``method`` field on every record (keybert|yake|statistical) tells the truth about which ran.

NEVER-FABRICATE (the cardinal rule, per the house style -- see cex_meli_trends / cex_sentiment_pt):
  * autocomplete returns ONLY real suggestions the endpoint actually served; a blocked/empty
    fetch yields an empty list + a recorded status, never a guessed term.
  * extraction returns ONLY keyphrases DERIVED from the input text; it never invents a phrase that
    is not present, and never attaches a search ``volume`` number (volume is a BUY -> honest null).

INVARIANTS:
  * degrade-never: autocomplete NEVER raises (a fetch failure -> honest-null/blocked branch);
    extract_keyphrases NEVER raises and ALWAYS returns a ranked list via the pure statistical
    fallback even when KeyBERT and YAKE are both absent.
  * never-fabricate: only real suggestions / text-derived keyphrases; volume stays null.
  * secrets-never-logged: this lane is keyless (no token); nothing sensitive is printed -- and the
    HTTP seam logs no headers regardless.
  * seed validated BEFORE URL-build: the seed is trimmed + length-capped + whitespace-normalised so
    a pathological/seed-injection string can never malform the request (requests percent-encodes it).
  * ASCII source: PT stopwords + question prefixes carry accents (o que / nao / voce) -- per the
    repo ascii-code rule the SOURCE stays ASCII by encoding those with ``\\uXXXX`` escapes; they are
    accent-FOLDED at match time so plain-ASCII and accented input behave identically.
  * HTTP timeout: every fetch uses _HTTP_TIMEOUT (no unbounded socket wait).
  * bounded: the alphabet-soup expansion, the question set, and every suggestion list are capped.

INTERFACE:
  CLI:        python _tools/cex_seo_keyword.py "<seed>"            -> autocomplete JSON + exit 0
              python _tools/cex_seo_keyword.py --extract "<text>"  -> keyphrases JSON + exit 0
  importable: autocomplete(seed, now=None) -> dict
              extract_keyphrases(text, top_k=20) -> dict

ASCII-only (.claude/rules/ascii-code-rule.md). Fully type-hinted. Composes; no global side effects.

Live proof (the orchestrator runs this -- real network for autocomplete; the endpoint is keyless
but YELLOW: if Google rate-limits/blocks it the branch is an honest 'blocked', never fabricated):
  python _tools/cex_seo_keyword.py "comedouro gato"
  python _tools/cex_seo_keyword.py --extract "comedouro de gato em inox com fonte de agua ..."
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from typing import Any, Dict, List, Optional, Tuple

# requests is the repo's HTTP client (used across _tools); the autocomplete fetch goes through the
# single _http_get_json seam below so a test can monkeypatch it with ZERO network.
try:
    import requests  # type: ignore[import]
except Exception:  # pragma: no cover - requests is a hard repo dep; defended for total-safety only.
    requests = None  # type: ignore[assignment]


# --------------------------------------------------------------------------- #
# Constants / bounds (the "bounded" + "HTTP timeout" invariants).
# --------------------------------------------------------------------------- #
# Google Autocomplete (the keyless suggest endpoint). client=firefox returns a clean JSON array
# [seed, [suggestions...]]; hl=pt + gl=br bias to Brazilian Portuguese. NO API key. YELLOW: Google
# may rate-limit/block -> we then record an honest 'blocked', never a fabricated suggestion.
_AUTOCOMPLETE_URL = "https://suggestqueries.google.com/complete/search"
_AUTOCOMPLETE_PARAMS = {"client": "firefox", "hl": "pt", "gl": "br"}

_HTTP_TIMEOUT = 12  # seconds -- no unbounded socket wait (degrade-never ceiling).

# A browser-ish UA: the bare python-requests UA is the one most likely to draw a YELLOW block.
_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CEXAI-seo-keyword/1.0"

_MAX_SEED_CHARS = 120        # a seed longer than this is truncated BEFORE URL-build (bounded).
_MAX_SUGGESTIONS = 25        # cap on the primary suggestion list.
_MAX_SOUP_LETTERS = 26       # a-z (bounded by construction); each letter adds <= _MAX_SOUP_PER.
_MAX_SOUP_PER = 8            # suggestions kept per alphabet-soup letter.
_MAX_SOUP_TOTAL = 120        # hard cap on the combined alphabet_soup list.
_MAX_QUESTION_PER = 8        # suggestions kept per question prefix.
_MAX_RELATED = 25            # cap on the de-duplicated 'related' roll-up.

# PT question prefixes (the "questions" expansion). ASCII source: the accented "o que e'" prefix is
# a \uXXXX escape (e-acute) per the ascii-code rule; Google tolerates either accented form.
_QUESTION_PREFIXES: Tuple[str, ...] = (
    "como",
    "o que \u00e9",      # "o que e" -- e-acute as a \uXXXX escape (ASCII source).
    "qual",
    "qual o melhor",
    "quanto custa",
    "onde comprar",
    "por que",
)

# The documented VOLUME stub. Keyword search VOLUME (monthly counts) is an Ahrefs/SEMrush BUY; this
# lane does NOT own it. Every record carries volume=None + this note so a consumer KNOWS the number
# was deliberately not produced (and was NOT fabricated). Wire a paid provider here to fill it.
_VOLUME_NOTE = (
    "volume (monthly search count) is a paid signal (Ahrefs/SEMrush/Keyword Planner) -- "
    "NOT owned by this GREEN/YELLOW lane; left null on purpose, never fabricated."
)


# --------------------------------------------------------------------------- #
# PT stopwords for the statistical extraction fallback. ASCII source: accented forms are \uXXXX
# escapes per the ascii-code rule; they are accent-FOLDED at match so the accented and plain-ASCII
# spellings both stop. This is a fixed, auditable list -- NEVER generated at runtime.
# --------------------------------------------------------------------------- #
_PT_STOPWORDS = frozenset({
    # articles / contractions
    "a", "o", "as", "os", "um", "uma", "uns", "umas", "ao", "aos",
    "\u00e0", "\u00e0s",                                                  # a (a-grave) / as
    "do", "da", "dos", "das", "no", "na", "nos", "nas", "pelo", "pela", "pelos", "pelas",
    "num", "numa", "dum", "duma",
    # prepositions / conjunctions
    "de", "em", "por", "para", "pra", "com", "sem", "sob", "sobre", "entre",
    "ate", "at\u00e9",                                                    # ate (a-acute)
    "\u00e9", "e", "ou", "mas", "que", "se", "como", "quando", "onde", "porque",  # e (e-acute)
    "porem", "por\u00e9m", "pois", "logo", "entao", "ent\u00e3o", "assim",
    "tambem", "tamb\u00e9m", "nem",                                       # porem/entao/tambem
    # pronouns
    "eu", "tu", "ele", "ela", "nos", "vos", "eles", "elas",
    "voce", "voc\u00ea", "voces", "voc\u00eas",                          # voce/voces (c-cedilla word)
    "me", "te", "lhe", "lhes", "meu", "minha", "seu", "sua", "seus", "suas",
    "este", "esta", "esse", "essa", "isto", "isso", "aquele", "aquela", "aquilo",
    "aqui", "ali", "la", "l\u00e1", "ca", "c\u00e1",                     # la/ca (a-acute)
    # common verbs / fillers
    "ser", "estar", "ter", "haver", "fazer", "ir", "foi", "sao", "s\u00e3o",
    "era", "sera", "ser\u00e1",                                          # sao/sera
    "tem", "muito", "muita", "muitos", "muitas", "mais", "menos",
    "ja", "j\u00e1", "nao", "n\u00e3o",                                  # ja/nao
    "sim", "talvez", "todo", "toda", "todos", "todas", "cada", "qualquer", "algum",
    "alguma", "nenhum", "nenhuma", "outro", "outra", "outros", "outras", "mesmo",
    "tao", "t\u00e3o", "bem", "mal", "so", "s\u00f3", "apenas",          # tao/so
    "ainda", "depois", "antes", "agora",
})

# How many words a candidate keyphrase may span (statistical tier). >1 captures real PT phrases.
_MAX_PHRASE_WORDS = 4
_MIN_WORD_CHARS = 2  # a candidate word shorter than this is dropped (drops stray letters/digits).

# Word-character class for the statistical splitter: ASCII letters/digits PLUS the Latin-1/Latin-A
# accented range (U+00C0..U+024F) so accented PT words are kept intact, then folded. \uXXXX escaped
# to keep this source ASCII per the ascii-code rule.
_WORD_SPLIT_RE = re.compile("[^0-9A-Za-z\u00c0-\u024f]+")


# --------------------------------------------------------------------------- #
# HTTP seam -- the SINGLE place autocomplete touches the network. Tests monkeypatch THIS.
# --------------------------------------------------------------------------- #
def _http_get_json(url: str, params: Dict[str, str]) -> Optional[Any]:
    """GET ``url`` with ``params`` and return the parsed JSON body, or None on ANY failure.

    The ONE network seam for this module (autocomplete). DEGRADE-NEVER / YELLOW-tolerant: a missing
    requests, a transport error, a non-200 status, or a non-JSON body ALL return None -- the caller
    then records an honest 'blocked'/empty branch. NEVER raises, NEVER fabricates a body. Logs no
    headers (the lane is keyless, but this keeps the seam secret-safe by construction)."""
    if requests is None:
        return None
    try:
        resp = requests.get(
            url, params=params, timeout=_HTTP_TIMEOUT, headers={"User-Agent": _UA}
        )
    except Exception:
        return None
    try:
        if getattr(resp, "status_code", 0) != 200:
            return None
        return resp.json()
    except Exception:
        # Non-JSON / parse error / a YELLOW HTML block page -> honest None (never a guess).
        return None


def _suggest(query: str) -> Tuple[List[str], bool]:
    """Fetch raw Google Autocomplete suggestions for ONE query string. Returns
    ``(suggestions, ok)``: ``ok`` is False when the fetch failed/blocked (YELLOW) so the caller can
    record provenance honestly. The endpoint returns ``[echo, [s1, s2, ...], ...]``; we take the
    second element. NEVER raises; NEVER fabricates -- a failure is ([], False)."""
    params = dict(_AUTOCOMPLETE_PARAMS)
    params["q"] = query  # caller has ALREADY validated the seed; requests percent-encodes it safely.
    body = _http_get_json(_AUTOCOMPLETE_URL, params)
    if body is None:
        return [], False
    # Expected shape: [query_echo, [suggestion strings], ...]. Be defensive about anything else.
    if isinstance(body, list) and len(body) >= 2 and isinstance(body[1], list):
        out: List[str] = []
        for item in body[1]:
            s = _clean_text(item)
            if s:
                out.append(s)
        return out, True
    # A 200 with an unexpected shape is still an HONEST empty (not a fabrication), but the fetch
    # itself succeeded -> ok=True so we don't mislabel it 'blocked'.
    return [], True


# --------------------------------------------------------------------------- #
# Seed validation (the "seed validated BEFORE URL-build" invariant).
# --------------------------------------------------------------------------- #
def _validate_seed(seed: Any) -> Optional[str]:
    """Coerce + sanitize a seed BEFORE any URL is built. Trims, collapses internal whitespace, and
    truncates to _MAX_SEED_CHARS. Returns the cleaned seed, or None when it is empty/non-str. PURE /
    TOTAL. (requests performs the actual percent-encoding at request time; this guarantees the value
    we hand it is bounded + whitespace-normalised so a pathological seed cannot malform the call.)"""
    if not isinstance(seed, str):
        if seed is None:
            return None
        seed = str(seed)
    cleaned = re.sub(r"\s+", " ", seed).strip()
    if not cleaned:
        return None
    return cleaned[:_MAX_SEED_CHARS]


# --------------------------------------------------------------------------- #
# Function 1 -- Google Autocomplete (suggestions + alphabet_soup + questions + related).
# --------------------------------------------------------------------------- #
def autocomplete(seed: Any, now: Optional[str] = None) -> Dict[str, Any]:
    """Discover keywords off Google Autocomplete for ``seed``. DEGRADE-NEVER (NEVER raises) +
    NEVER-FABRICATE + YELLOW-tolerant (a blocked fetch -> honest empty branch + 'blocked' status).

    Args:
      seed: the seed keyword. Validated (trim + collapse ws + cap length) BEFORE URL-build; a
        non-str is coerced, an empty/whitespace seed yields an honest empty record (mock False).
      now: an OPTIONAL ISO-8601 string echoed verbatim into ``fetched_at`` (never invented).

    Returns a dict (honest-null throughout):
      seed (cleaned echo),
      suggestions (ranked list of real Autocomplete strings; [] when blocked/none),
      alphabet_soup (list of {letter, suggestions} -- seed + 'a'..'z', BOUNDED; only letters that
        returned at least one suggestion are kept),
      questions (list of {prefix, suggestions} -- PT question heads + seed),
      related (de-duplicated roll-up of all discovered terms, capped),
      volume (ALWAYS None -- a paid BUY, never fabricated; see volume_note),
      volume_note (why volume is null),
      data_sources (provenance), endpoint_status (ok|blocked|skipped per branch),
      mock (ALWAYS False -- real API or an honest null, never simulated),
      [fetched_at if now given]."""
    rec = _empty_autocomplete(now=now)
    cleaned = _validate_seed(seed)
    if cleaned is None:
        rec["endpoint_status"]["suggestions"] = "skipped: empty seed"
        rec["endpoint_status"]["alphabet_soup"] = "skipped: empty seed"
        rec["endpoint_status"]["questions"] = "skipped: empty seed"
        return rec
    rec["seed"] = cleaned

    # --- primary suggestions ---------------------------------------------------
    suggestions, ok = _suggest(cleaned)
    if ok:
        rec["suggestions"] = suggestions[:_MAX_SUGGESTIONS]
        rec["endpoint_status"]["suggestions"] = "ok"
        rec["data_sources"]["suggestions"] = "google:autocomplete"
    else:
        rec["endpoint_status"]["suggestions"] = "blocked: autocomplete fetch failed (YELLOW)"

    # --- alphabet soup: seed + each a-z (BOUNDED) ------------------------------
    soup: List[Dict[str, Any]] = []
    soup_total = 0
    soup_blocked = 0
    for code in range(ord("a"), ord("a") + _MAX_SOUP_LETTERS):
        if soup_total >= _MAX_SOUP_TOTAL:
            break
        letter = chr(code)
        terms, ok_l = _suggest("%s %s" % (cleaned, letter))
        if not ok_l:
            soup_blocked += 1
            continue
        kept = terms[:_MAX_SOUP_PER]
        if not kept:
            continue
        remaining = _MAX_SOUP_TOTAL - soup_total
        kept = kept[:remaining]
        soup.append({"letter": letter, "suggestions": kept})
        soup_total += len(kept)
    rec["alphabet_soup"] = soup
    if soup:
        rec["endpoint_status"]["alphabet_soup"] = "ok (%d terms)" % soup_total
        rec["data_sources"]["alphabet_soup"] = "google:autocomplete"
    elif soup_blocked >= _MAX_SOUP_LETTERS:
        rec["endpoint_status"]["alphabet_soup"] = "blocked: all alphabet fetches failed (YELLOW)"
    else:
        rec["endpoint_status"]["alphabet_soup"] = "ok (0 terms)"

    # --- questions: PT question heads + seed -----------------------------------
    questions: List[Dict[str, Any]] = []
    q_blocked = 0
    for prefix in _QUESTION_PREFIXES:
        terms, ok_q = _suggest("%s %s" % (prefix, cleaned))
        if not ok_q:
            q_blocked += 1
            continue
        kept = terms[:_MAX_QUESTION_PER]
        if not kept:
            continue
        questions.append({"prefix": prefix, "suggestions": kept})
    rec["questions"] = questions
    if questions:
        rec["endpoint_status"]["questions"] = "ok"
        rec["data_sources"]["questions"] = "google:autocomplete"
    elif q_blocked >= len(_QUESTION_PREFIXES):
        rec["endpoint_status"]["questions"] = "blocked: all question fetches failed (YELLOW)"
    else:
        rec["endpoint_status"]["questions"] = "ok (0 terms)"

    # --- related: de-duplicated roll-up of everything discovered ---------------
    rec["related"] = _roll_up_related(rec)
    return rec


def _roll_up_related(rec: Dict[str, Any]) -> List[str]:
    """Build a de-duplicated, order-preserving roll-up of every real term discovered across the
    suggestions / alphabet_soup / questions branches, capped at _MAX_RELATED. PURE; NEVER
    fabricates -- it only re-collects strings the endpoint already served."""
    seen: Dict[str, bool] = {}
    out: List[str] = []

    def _add(term: str) -> None:
        key = _fold(term)
        if not key or key in seen:
            return
        seen[key] = True
        out.append(term)

    for s in rec.get("suggestions", []) or []:
        _add(s)
    for block in rec.get("alphabet_soup", []) or []:
        for s in block.get("suggestions", []) or []:
            _add(s)
    for block in rec.get("questions", []) or []:
        for s in block.get("suggestions", []) or []:
            _add(s)
    return out[:_MAX_RELATED]


def _empty_autocomplete(now: Optional[str] = None) -> Dict[str, Any]:
    """The all-null autocomplete record skeleton. ``volume`` is ALWAYS None (a BUY -- never
    fabricated) and ``mock`` is ALWAYS False (real API data or an explicit null)."""
    rec: Dict[str, Any] = {
        "seed": None,
        "suggestions": [],
        "alphabet_soup": [],
        "questions": [],
        "related": [],
        "volume": None,             # paid signal -- NEVER fabricated (see volume_note).
        "volume_note": _VOLUME_NOTE,
        "data_sources": {},
        "endpoint_status": {},
        "mock": False,
    }
    if isinstance(now, str) and now.strip():
        rec["fetched_at"] = now.strip()
    return rec


# --------------------------------------------------------------------------- #
# Function 2 -- keyphrase extraction (degrade-never tiers: KeyBERT -> YAKE -> statistical).
# --------------------------------------------------------------------------- #
def extract_keyphrases(text: Any, top_k: int = 20) -> Dict[str, Any]:
    """Extract ranked keyphrases from ``text``. DEGRADE-NEVER (NEVER raises) + NEVER-FABRICATE.

    TIER SELECTION (auto, best-available first; each falls back on import/runtime failure):
      1. KeyBERT  (method='keybert')     -- if ``keybert`` is importable.
      2. YAKE     (method='yake')        -- else if ``yake`` is importable.
      3. statistical (method='statistical') -- the ALWAYS-available pure-Python floor (PT stopword
         removal + candidate n-grams scored by per-word degree/frequency, RAKE-style). This
         guarantees a ranked result with ZERO ML deps installed.

    Args:
      text: the input text/corpus. A non-str/None is coerced to "" (-> empty keyphrases, honest).
      top_k: how many ranked keyphrases to return (bounded 1..100).

    Returns a dict:
      keyphrases (ranked list of {phrase, score, method}); [] only for empty/word-less input,
      method (the tier that actually ran: keybert|yake|statistical),
      count (int),
      volume (ALWAYS None -- per-keyphrase search volume is a paid BUY; never fabricated),
      volume_note,
      data_sources (the tier), mock (False)."""
    safe_text = text if isinstance(text, str) else ("" if text is None else str(text))
    try:
        k = int(top_k)
    except Exception:
        k = 20
    k = max(1, min(100, k))

    method = "statistical"
    phrases: List[Dict[str, Any]] = []

    # Tier 1+2 are OPTIONAL and only engage if their dep imports AND a run succeeds; ANY failure
    # transparently falls through to the next tier (degrade-never). The statistical tier never fails.
    if safe_text.strip():
        kb = _extract_keybert(safe_text, k)
        if kb is not None:
            method, phrases = "keybert", kb
        else:
            yk = _extract_yake(safe_text, k)
            if yk is not None:
                method, phrases = "yake", yk
            else:
                method, phrases = "statistical", _extract_statistical(safe_text, k)

    return {
        "keyphrases": phrases,
        "method": method,
        "count": len(phrases),
        "volume": None,             # per-keyphrase volume is a BUY -- never fabricated.
        "volume_note": _VOLUME_NOTE,
        "data_sources": ["extract:%s" % method],
        "mock": False,
    }


def _extract_keybert(text: str, top_k: int) -> Optional[List[Dict[str, Any]]]:
    """The KeyBERT tier (OPTIONAL). Returns ranked [{phrase, score, method:'keybert'}] or None if
    keybert is not importable / the model can't load / inference fails. DEGRADE-NEVER: NEVER raises.
    NEVER-FABRICATE: phrases + scores are KeyBERT's own output, mapped verbatim."""
    try:
        from keybert import KeyBERT  # type: ignore[import]
    except Exception:
        return None
    try:
        kw = KeyBERT()
        pairs = kw.extract_keywords(
            text,
            keyphrase_ngram_range=(1, _MAX_PHRASE_WORDS),
            stop_words=None,            # PT handled by the model; we do not pass an EN stoplist.
            top_n=top_k,
        )
    except Exception:
        return None
    out: List[Dict[str, Any]] = []
    for item in pairs or []:
        try:
            phrase, score = item[0], item[1]
        except Exception:
            continue
        p = _clean_text(phrase)
        if not p:
            continue
        out.append({
            "phrase": p,
            "score": round(float(score), 4) if isinstance(score, (int, float)) else None,
            "method": "keybert",
        })
    return out


def _extract_yake(text: str, top_k: int) -> Optional[List[Dict[str, Any]]]:
    """The YAKE tier (OPTIONAL). Returns ranked [{phrase, score, method:'yake'}] or None if yake is
    not importable / extraction fails. DEGRADE-NEVER: NEVER raises.

    YAKE scores are a RELEVANCE measure where LOWER is better; we sort ascending (best first) but
    return YAKE's raw score verbatim (never inverted into a fake confidence) -- the ``method='yake'``
    label tells the consumer the score's polarity. NEVER-FABRICATE."""
    try:
        import yake  # type: ignore[import]
    except Exception:
        return None
    try:
        extractor = yake.KeywordExtractor(
            lan="pt", n=_MAX_PHRASE_WORDS, top=top_k,
        )
        pairs = extractor.extract_keywords(text)
    except Exception:
        return None
    rows: List[Tuple[str, float]] = []
    for item in pairs or []:
        try:
            phrase, score = item[0], item[1]
        except Exception:
            continue
        p = _clean_text(phrase)
        if not p or not isinstance(score, (int, float)):
            continue
        rows.append((p, float(score)))
    rows.sort(key=lambda r: r[1])  # YAKE: lower score = more relevant.
    return [
        {"phrase": p, "score": round(s, 4), "method": "yake"}
        for p, s in rows[:top_k]
    ]


def _extract_statistical(text: str, top_k: int) -> List[Dict[str, Any]]:
    """The STATISTICAL tier (ALWAYS available; ZERO deps) -- a RAKE-style extractor. Splits the text
    on PT stopwords + punctuation into candidate phrases, then scores each candidate word by
    degree/frequency (deg = co-occurrence span, freq = count) and sums word scores per phrase.

    DEGRADE-NEVER + NEVER-FABRICATE: pure-Python, no model, no network; every phrase is a literal
    contiguous run from the input (never invented), normalised to a 0..1 score (max-normalised so
    the strongest phrase is ~1.0). This is the floor that makes extraction degrade-never.

    Returns ranked [{phrase, score, method:'statistical'}]."""
    candidates = _candidate_phrases(text)
    if not candidates:
        return []

    # RAKE word scoring: freq[w] = occurrences; degree[w] = sum of phrase lengths it appears in
    # (so a word in longer phrases scores higher). word_score = degree / freq.
    freq: Dict[str, int] = {}
    degree: Dict[str, int] = {}
    for words in candidates:
        span = len(words)  # RAKE counts degree including the word itself (degree += span).
        for w in words:
            freq[w] = freq.get(w, 0) + 1
            degree[w] = degree.get(w, 0) + span

    word_score: Dict[str, float] = {}
    for w in freq:
        word_score[w] = degree[w] / float(freq[w]) if freq[w] else 0.0

    # Score each DISTINCT candidate phrase = sum of its word scores. Keep the first surface form.
    phrase_score: Dict[str, float] = {}
    phrase_surface: Dict[str, str] = {}
    for words in candidates:
        key = " ".join(words)
        if not key:
            continue
        score = sum(word_score.get(w, 0.0) for w in words)
        # Keep the BEST score for a repeated phrase (do not double-count occurrences as a fake boost).
        if key not in phrase_score or score > phrase_score[key]:
            phrase_score[key] = score
        phrase_surface.setdefault(key, key)

    if not phrase_score:
        return []
    max_score = max(phrase_score.values()) or 1.0

    ranked = sorted(phrase_score.items(), key=lambda kv: (-kv[1], kv[0]))
    out: List[Dict[str, Any]] = []
    for key, score in ranked[:top_k]:
        out.append({
            "phrase": phrase_surface.get(key, key),
            "score": round(score / max_score, 4),  # max-normalised to 0..1.
            "method": "statistical",
        })
    return out


def _candidate_phrases(text: str) -> List[List[str]]:
    """Split ``text`` into RAKE candidate phrases: contiguous runs of content words delimited by PT
    stopwords or punctuation. Each candidate is a list of accent-FOLDED words; runs longer than
    _MAX_PHRASE_WORDS are truncated, too-short words are dropped. PURE / TOTAL -> [] for empty."""
    if not isinstance(text, str) or not text:
        return []
    candidates: List[List[str]] = []
    current: List[str] = []
    # Tokenize into words (folded) vs separators. A non-letter char or a stopword breaks a phrase.
    for raw in _WORD_SPLIT_RE.split(text):
        if not raw:
            # punctuation boundary -> close the current phrase.
            if current:
                candidates.append(current[:_MAX_PHRASE_WORDS])
                current = []
            continue
        folded = _fold(raw)
        if (not folded) or folded in _PT_STOPWORDS or len(folded) < _MIN_WORD_CHARS \
                or folded.isdigit():
            if current:
                candidates.append(current[:_MAX_PHRASE_WORDS])
                current = []
            continue
        current.append(folded)
    if current:
        candidates.append(current[:_MAX_PHRASE_WORDS])
    return [c for c in candidates if c]


# --------------------------------------------------------------------------- #
# PURE helpers (TOTAL -- garbage in -> safe out; NEVER fabricate).
# --------------------------------------------------------------------------- #
def _fold(token: Any) -> str:
    """Lowercase + strip diacritics (NFD + drop combining marks). PURE / TOTAL: a non-str -> "".
    This is why the PT stopwords can be authored with \\uXXXX escapes yet still match plain-ASCII or
    accented input identically (e.g. the accented "nao" and plain "nao" both fold to "nao")."""
    if not isinstance(token, str):
        return ""
    nfkd = unicodedata.normalize("NFD", token.lower())
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def _clean_text(value: Any) -> Optional[str]:
    """A non-empty, whitespace-collapsed string, or None. PURE / TOTAL. Used to sanitize endpoint
    suggestions + extracted phrases (drops blanks; never fabricates)."""
    if not isinstance(value, str):
        if value is None or isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            value = str(value)
        else:
            return None
    s = re.sub(r"\s+", " ", value).strip()
    return s or None


__all__ = [
    "autocomplete",
    "extract_keyphrases",
]


# --------------------------------------------------------------------------- #
# CLI -- autocomplete (default) or --extract. Always exit 0 (degrade-never): a blocked autocomplete
# yields an honest 'blocked' record, and extraction always yields a statistical result at worst.
# --------------------------------------------------------------------------- #
def _usage() -> None:
    print("CEXAI SEO / keyword research lane (GREEN/YELLOW). Usage:")
    print('  python _tools/cex_seo_keyword.py "<seed>"            '
          "-> Google Autocomplete JSON {suggestions, alphabet_soup, questions, related}")
    print('  python _tools/cex_seo_keyword.py --extract "<text>"  '
          "-> keyphrases JSON {keyphrases:[{phrase,score,method}], ...}")
    print("  NOTE: autocomplete is KEYLESS but YELLOW -- a Google block yields an honest 'blocked'")
    print("        status, never a fabricated suggestion. Keyphrase tiers: KeyBERT -> YAKE ->")
    print("        statistical (the always-available zero-dep floor). 'method' tells which ran.")
    print("        Keyword VOLUME is a paid BUY -> 'volume' is null on purpose (never fabricated).")


def _main(argv: List[str]) -> int:
    if not argv:
        _usage()
        return 0

    if argv[0] == "--extract":
        text = " ".join(argv[1:])
        if not text.strip():
            print("--extract requires text. " + _VOLUME_NOTE)
            return 0
        rec = extract_keyphrases(text)
        print(json.dumps(rec, ensure_ascii=False, indent=2))
        return 0

    if argv[0] in ("-h", "--help"):
        _usage()
        return 0

    seed = " ".join(argv)
    rec = autocomplete(seed)
    print(json.dumps(rec, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
