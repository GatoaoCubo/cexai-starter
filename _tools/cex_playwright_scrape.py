#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI standalone Playwright marketplace scraper -- runs in a CHILD PROCESS.

WHY a separate module / a child process (the thread-safety fix):
  Playwright's SYNC API cannot run in a non-main thread / a thread without its own event
  loop -- it raises the classic "Playwright Sync API inside asyncio loop" / greenlet error.
  The STORM fan-out (cex_run_research) runs each source lane inside a ThreadPoolExecutor
  worker thread, so calling sync_playwright() THERE crashes the lane ("lane failures:
  playwright_scrape"). The fix: cex_tool_resolver_live invokes THIS module via subprocess.run.
  A child process has its OWN main thread, so sync_playwright() is safe regardless of which
  thread the parent called the lane from. This is thread-safe by construction.

WHAT it does (the PROVEN extraction -- verified live: real Mercado Livre cards, zero block):
  __main__ reads a JSON arg {query, marketplace, limit, cdp_url} (argv[1] or, if absent, stdin)
  -> runs sync_playwright() on ITS OWN main thread -> acquires a browser by strategy
  (degrade-never order):
    (1) chromium.connect_over_cdp(cdp_url or env CEX_CDP_URL or http://localhost:9222)
        -- reuse a RUNNING real Chrome (this is what worked live; 0 install, real session);
    (2) else chromium.launch(headless=True, args=[anti-bot flags]) with a realistic user_agent
        + viewport on the CONTEXT (reduces headless anti-bot detection).
  -> page.goto(url, wait_until='domcontentloaded', 30s) -> wait ~2.5s for the grid to hydrate
  -> page.evaluate(the PROVEN JS) -> raw cards -> normalize + dedup (by title+price)
  -> print JSON {"status":"ok|empty|unavailable","listings":[...]} to stdout.

DEGRADE-NEVER + NEVER FABRICATE: __main__ NEVER raises -- any failure (no browser, nav error,
playwright not importable, bad arg) prints {"status":"unavailable","error":"<type>"} and exits 0.
A reached-but-empty page (anti-bot / no grid) prints {"status":"empty","listings":[]}. No card is
ever invented: a slot with no title is skipped, an unparseable price is left null.

The listing shape is the SAME firecrawl/tavily page shape the STORM engine reads -- it is produced
by the SHARED normalizers in cex_tool_resolver_live (single source of truth):
  {title, url, origin, snippet, price(float|null), rating, reviews, seller, marketplace, mock:false}
plus sold_quantity (null -- not in the proven DOM extraction).

ASCII-only (.claude/rules/ascii-code-rule.md). NO secret is read/printed (the lane needs no key).

CLI contract (used by cex_tool_resolver_live._playwright_marketplace_scrape via subprocess.run):
  python _tools/cex_playwright_scrape.py '{"query":"comedouro automatico gatos inox",
      "marketplace":"mercadolivre","limit":20,"cdp_url":"http://localhost:9222"}'
  -> stdout: {"status":"ok","listings":[{...}, ...]}
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Reuse the PURE normalizers + the marketplace target table from the live resolver (single source
# of truth for the listing shape, the slug, and the search URL). That module is import-light (no
# driver/key/browser is touched at import), so importing it in this child process is cheap + safe.
_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

import cex_tool_resolver_live as _live  # type: ignore[import]

# A module-level seam for the playwright sync API so a unit test can monkeypatch it (the scraper
# reads it THROUGH the module). Left None so the real playwright.sync_api.sync_playwright is
# imported lazily on first use (offline-import friendly; no browser is touched at import time).
sync_playwright = None  # type: ignore[assignment]

# Per-call browser timeouts (mirror the proven live values; the parent's subprocess timeout is the
# OUTER budget). page.goto uses 30s; the hydrate settle is the proven 2.5s.
_GOTO_TIMEOUT_MS = _live._PLAYWRIGHT_GOTO_TIMEOUT_MS
_HYDRATE_MS = _live._PLAYWRIGHT_HYDRATE_MS
_DEFAULT_CDP_URL = _live._DEFAULT_CDP_URL
_DEFAULT_LIMIT = _live._DEFAULT_PLAYWRIGHT_LIMIT
_DEFAULT_MARKETPLACE = _live._DEFAULT_PLAYWRIGHT_MARKETPLACE

# A realistic desktop Chrome UA + viewport on the launched-browser context -- reduces the headless
# anti-bot detection that blocks a bare headless chromium (the CDP-reuse path already presents a
# real session). NOT a secret; safe to hardcode.
_LAUNCH_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--no-sandbox",
]
_REALISTIC_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
_REALISTIC_VIEWPORT = {"width": 1366, "height": 900}

# ---------------------------------------------------------------------------
# STEALTH HARDENING (the LAUNCHED-headless fallback ONLY -- the CDP-reuse path is a real Chrome
# session and needs none). Reuses the posture of the marketplace browser_tool
# (N03_engineering/P04_tools/ex_browser_tool_marketplace_scrap.md: "rotating user agents over 10+
# real UA strings"): a small pool of REAL desktop-Chrome UAs + the standard playwright-stealth
# evasions. LEGITIMACY: these make a real-DOM reader survive bot-DETECTION on a server -- the page
# is the SAME public results grid any shopper sees (exploits nothing, bypasses no auth). Each UA in
# the pool maps to a matching sec-ch-ua / sec-ch-ua-platform Client-Hint so the headers are
# self-consistent (a mismatched UA is itself a bot tell). The init-script removes navigator.webdriver
# and spoofs languages/plugins/hardwareConcurrency + light canvas/WebGL noise. All randomness flows
# through _rng (a module seam) so a unit test injects a deterministic RNG and asserts the chosen UA +
# the consistent hints + the init-script presence.
_DESKTOP_UA_POOL = [
    # (UA, sec-ch-ua brand list, sec-ch-ua-platform). All REAL desktop-Chrome strings.
    ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
     "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
     '"Chromium";v="124", "Google Chrome";v="124", "Not.A/Brand";v="99"', '"Windows"'),
    ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
     "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
     '"Chromium";v="123", "Google Chrome";v="123", "Not.A/Brand";v="99"', '"Windows"'),
    ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
     "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
     '"Chromium";v="124", "Google Chrome";v="124", "Not.A/Brand";v="99"', '"macOS"'),
    ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
     "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
     '"Chromium";v="123", "Google Chrome";v="123", "Not.A/Brand";v="99"', '"Linux"'),
    ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
     "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
     '"Chromium";v="122", "Google Chrome";v="122", "Not.A/Brand";v="99"', '"Windows"'),
]

# A small pool of believable Accept-Language headers (PT-BR first -- the ML target is Brazilian).
_ACCEPT_LANGUAGE_POOL = [
    "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "pt-BR,pt;q=0.9,en;q=0.8",
]
# The navigator.languages each Accept-Language should spoof (kept consistent with the header).
_NAV_LANGUAGES = ["pt-BR", "pt", "en-US", "en"]

# Human-like jitter bounds (ms) for the pre-extract settle + the extra micro-pause. Small + bounded
# so a unit test stays fast; the RNG seam makes the exact value deterministic under test.
_JITTER_MIN_MS = 400
_JITTER_MAX_MS = 1200

# A module-level RNG seam so a unit test can inject a deterministic random.Random(seed). Left None
# so the real ``random`` module is used at call time (no import-time side effect).
_rng = None  # type: ignore[assignment]

# The standard playwright-stealth init-script: runs in EVERY new document BEFORE page scripts. It
# only patches navigator/WebGL/canvas surfaces a headless Chromium leaves as bot tells -- it reads
# NOTHING private and changes NO page content. %(languages)s / %(cores)s are filled per launch.
_STEALTH_INIT_JS = r"""
(() => {
  try {
    // 1. navigator.webdriver -- the #1 headless tell. Make it undefined.
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
  } catch (e) {}
  try {
    // 2. navigator.languages -- a bare headless reports a thin/empty list.
    Object.defineProperty(navigator, 'languages', { get: () => %(languages)s });
  } catch (e) {}
  try {
    // 3. navigator.plugins -- headless reports zero plugins. Present a small believable set.
    const fake = [
      { name: 'Chrome PDF Plugin' },
      { name: 'Chrome PDF Viewer' },
      { name: 'Native Client' },
    ];
    Object.defineProperty(navigator, 'plugins', { get: () => fake });
  } catch (e) {}
  try {
    // 4. navigator.hardwareConcurrency -- spoof a common core count.
    Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => %(cores)s });
  } catch (e) {}
  try {
    // 5. WebGL vendor/renderer -- headless SwiftShader is a tell; report a common GPU pair.
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function (p) {
      if (p === 37445) { return 'Intel Inc.'; }            // UNMASKED_VENDOR_WEBGL
      if (p === 37446) { return 'Intel Iris OpenGL Engine'; } // UNMASKED_RENDERER_WEBGL
      return getParameter.call(this, p);
    };
  } catch (e) {}
  try {
    // 6. Canvas fingerprint -- add light deterministic-per-document noise to one channel so a
    //    canvas hash is not a stable headless signature (does NOT alter visible rendering).
    const toDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function () {
      try {
        const ctx = this.getContext('2d');
        if (ctx && this.width && this.height) {
          const img = ctx.getImageData(0, 0, this.width, this.height);
          if (img && img.data && img.data.length > 4) { img.data[0] = img.data[0] ^ 1; }
        }
      } catch (e) {}
      return toDataURL.apply(this, arguments);
    };
  } catch (e) {}
})();
"""


# --------------------------------------------------------------------------- #
# SELECTOR PROFILES -- the SAME real-browser path generalized across marketplaces.
#
# Each profile binds a marketplace to (a) the DOM-extraction JS that page.evaluate runs and
# (b) the search-URL hints. The extraction code reads the ACTIVE profile by marketplace so the
# ONE proven browser path (acquire browser -> goto -> hydrate -> evaluate -> normalize) serves
# Mercado Livre, Shopee, and Amazon without a fork.
#
# MERCADOLIVRE is the PROVEN profile (verified live: 180 real cards, zero block). Its
# ``extract_js`` is the EXISTING extraction JS, kept as the live resolver's single source of
# truth (_live._PLAYWRIGHT_EXTRACT_JS) so the default ML path is BYTE-IDENTICAL to before this
# change -- the existing scraper tests are unaffected. The ML selectors
# (li.ui-search-layout__item / poly-component__title / money-amount__fraction) are PRESERVED
# verbatim in that JS.
#
# SHOPEE + AMAZON are PROVISIONAL profiles: best-effort PUBLIC selectors, NOT live-proven this
# pass (the ML account is rate-cooling -- no live marketplace hit was made). They are marked
# PROVISIONAL and MUST be validated by a live pass with ban-safety ON before they are trusted.
# Each provisional JS returns the SAME {cards:[...], jsonld:[...]} shape the ML JS returns, so
# the shared python normalizer (_live._playwright_normalize_cards) consumes them unchanged. It
# NEVER fabricates: a card with no title is skipped; an absent field stays empty -> null.
# --------------------------------------------------------------------------- #

# PROVISIONAL Shopee extraction JS. Public Shopee search cards (a[data-sqe="link"] anchors with
# a title line + a price node). NOT live-proven -- Shopee is heavily client-rendered + anti-bot;
# these selectors are a best-effort starting point a live ban-safe pass must verify. Returns the
# {cards, jsonld} shape; invents nothing.
_SHOPEE_EXTRACT_JS = r"""
() => {
  const cards = document.querySelectorAll(
    'div.shopee-search-item-result__item, li.shopee-search-item-result__item, a[data-sqe="link"]'
  );
  const pick = (root, sel) => {
    const el = root.querySelector(sel);
    return el ? (el.textContent || '').trim() : '';
  };
  const out = [];
  cards.forEach((card) => {
    const title = pick(card, '[data-sqe="name"], .ie3A\\+n, div._10Wbs-, .yQmmFK');
    const price = pick(card, '[class*="price"], .ZEgDH9, ._3c5u7X');
    const seller = pick(card, '[class*="shop-name"], [class*="seller"]');
    let url = '';
    const link = card.matches && card.matches('a[href]') ? card : card.querySelector('a[href]');
    if (link) { url = link.getAttribute('href') || ''; }
    if (title || price) {
      out.push({
        title: title, price: price, seller: seller, url: url,
        rating: '', reviews: '', sold: '', badges: []
      });
    }
  });
  const jsonld = [];
  document.querySelectorAll('script[type="application/ld+json"]').forEach((s) => {
    const raw = (s.textContent || '').trim();
    if (raw) { jsonld.push(raw); }
  });
  return { cards: out, jsonld: jsonld };
}
"""

# PROVISIONAL Amazon BR extraction JS. Public Amazon search rows
# (div[data-component-type="s-search-result"]) with the h2 title, a price (.a-price
# .a-offscreen / .a-price-whole + .a-price-fraction), and the rating/reviews widgets. NOT
# live-proven this pass -- Amazon's markup shifts + anti-bot challenges; a live ban-safe pass must
# verify. Returns the {cards, jsonld} shape; invents nothing.
#
# BR PRICE (the 100x-inflation fix): Amazon BR renders the price as TWO spans --
# span.a-price-whole (the reais, e.g. "23", may carry a BR thousands dot "1.234" + a trailing
# decimal mark) + span.a-price-fraction (the centavos, e.g. "99"). The OLD JS combined the
# textContent into "2399" (whole+fraction with NO decimal), and the shared integer-reais price
# parser then read 2399.0 for R$ 23,99 (100x too high). The fix emits the two spans SEPARATELY
# (price_whole / price_fraction) + the .a-offscreen string (which already carries the BR decimal,
# e.g. "R$ 23,99"); the Python helper _normalize_amazon_br_price re-assembles a CORRECT float
# BEFORE the shared normalizer runs. ``price`` keeps the .a-offscreen string (best single source);
# whole/fraction are the structured fallback. NEVER fabricates: no price node -> all empty -> null.
_AMAZON_EXTRACT_JS = r"""
() => {
  const cards = document.querySelectorAll(
    'div[data-component-type="s-search-result"], div.s-result-item[data-asin]'
  );
  const pick = (root, sel) => {
    const el = root.querySelector(sel);
    return el ? (el.textContent || '').trim() : '';
  };
  const out = [];
  cards.forEach((card) => {
    const title = pick(card, 'h2 a span, h2 span, .a-size-medium.a-text-normal');
    // BR price: the .a-offscreen string carries the FULL price WITH the decimal ("R$ 23,99");
    // a-price-whole / a-price-fraction are the structured reais/centavos fallback.
    const priceOffscreen = pick(card, '.a-price .a-offscreen');
    const priceWhole = pick(card, '.a-price-whole');
    const priceFraction = pick(card, '.a-price-fraction');
    const rating = pick(card, '.a-icon-alt');
    const reviews = pick(card, '[class*="s-underline-text"], .a-size-base.s-underline-text');
    let url = '';
    const link = card.querySelector('h2 a, a.a-link-normal[href]');
    if (link) { url = link.getAttribute('href') || ''; }
    if (title || priceOffscreen || priceWhole) {
      out.push({
        // ``price`` = the .a-offscreen string (already has the BR decimal); the python helper
        // re-assembles from whole/fraction when offscreen is absent.
        title: title, price: priceOffscreen, seller: '', url: url,
        price_whole: priceWhole, price_fraction: priceFraction,
        rating: rating, reviews: reviews, sold: '', badges: []
      });
    }
  });
  const jsonld = [];
  document.querySelectorAll('script[type="application/ld+json"]').forEach((s) => {
    const raw = (s.textContent || '').trim();
    if (raw) { jsonld.push(raw); }
  });
  return { cards: out, jsonld: jsonld };
}
"""

# The profile table. ``status`` is 'proven' (live-verified) or 'provisional' (best-effort,
# needs a live ban-safe pass). ``extract_js`` is the page.evaluate script for that marketplace.
# Mercado Livre reuses the live resolver's JS verbatim (single source of truth -> byte-identical
# default behavior). Keys mirror the _live._PLAYWRIGHT_MARKETPLACES table.
SELECTOR_PROFILES: Dict[str, Dict[str, Any]] = {
    "mercadolivre": {
        "status": "proven",
        # PRESERVED verbatim: the single source of truth in the live resolver (the existing,
        # live-verified ML extraction with the ui-search-layout / poly-component / money-amount
        # selectors). Referenced (not copied) so it can NEVER drift from the proven JS.
        "extract_js": _live._PLAYWRIGHT_EXTRACT_JS,
    },
    "shopee": {
        "status": "provisional",
        "extract_js": _SHOPEE_EXTRACT_JS,
    },
    "amazon_br": {
        "status": "provisional",
        "extract_js": _AMAZON_EXTRACT_JS,
    },
}


def _resolve_selector_profile(marketplace: str) -> Dict[str, Any]:
    """Pick the SELECTOR_PROFILES entry for a marketplace key. TOTAL -> always returns a usable
    profile (falls back to the proven Mercado Livre profile for an unknown key). The default
    marketplace stays 'mercadolivre' so the ML path is byte-identical to before profiles existed."""
    name = (marketplace or "").strip().lower() or _DEFAULT_MARKETPLACE
    return SELECTOR_PROFILES.get(name, SELECTOR_PROFILES[_DEFAULT_MARKETPLACE])


def _profile_extract_js(marketplace: str) -> str:
    """Return the DOM-extraction JS for a marketplace's active profile. TOTAL -> the proven ML
    JS when the profile lacks a usable script (degrade-never; never an empty evaluate)."""
    profile = _resolve_selector_profile(marketplace)
    js = profile.get("extract_js")
    if isinstance(js, str) and js.strip():
        return js
    return _live._PLAYWRIGHT_EXTRACT_JS


# --------------------------------------------------------------------------- #
# The browser run -- ALWAYS on this process's main thread (the whole point).
# --------------------------------------------------------------------------- #
def scrape(
    query: str,
    *,
    marketplace: str = _DEFAULT_MARKETPLACE,
    limit: int = _DEFAULT_LIMIT,
    cdp_url: str = "",
) -> Dict[str, Any]:
    """Drive a real browser to the marketplace search page + read the live DOM into STRUCTURED
    listings. Returns a result dict {"status": "ok"|"empty"|"unavailable", "listings": [...]}
    (+ "url" and, on failure, "error"). DEGRADE-NEVER + TOTAL: NEVER raises, NEVER fabricates.

    Status semantics:
      ok          -- the page rendered AND at least one listing was extracted.
      empty       -- the page was REACHED but yielded zero listings (anti-bot / no grid) -- honest.
      unavailable -- the lane could NOT execute (no browser, nav error, playwright missing).
    The parent (cex_tool_resolver_live) maps empty/unavailable to its degrade-never note."""
    target = _live._resolve_playwright_target(marketplace)
    search_url = _live._playwright_search_url(target, query)
    if not search_url:
        return {"status": "unavailable", "listings": [], "url": "", "error": "no_search_url"}

    sp_ctx = _import_sync_playwright()
    if sp_ctx is None:
        # playwright not importable -> the lane cannot run (no browser to drive). HONEST unavailable.
        return {"status": "unavailable", "listings": [], "url": search_url,
                "error": "playwright_not_importable"}

    raw_cards: List[Any] = []
    raw_jsonld: List[Any] = []
    reached = False
    browser_ok = False
    try:
        with sp_ctx as p:
            browser, owns_browser = _acquire_browser(p, cdp_url)
            if browser is None:
                return {"status": "unavailable", "listings": [], "url": search_url,
                        "error": "no_browser"}
            browser_ok = True
            context = None
            try:
                context = _new_context(browser, owns_browser)
                page = context.new_page()
                page.goto(search_url, wait_until="domcontentloaded", timeout=_GOTO_TIMEOUT_MS)
                page.wait_for_timeout(_HYDRATE_MS)
                # Stealth: a light human-like settle + mouse move + scroll before the read (only
                # meaningful on the launched-headless path; harmless on a real Chrome). It NEVER
                # changes the public page -- it just reads it less like an instant headless bot.
                if owns_browser:
                    _humanize_before_extract(page)
                reached = True
                # Read the ACTIVE marketplace profile's extraction JS (the SAME proven path,
                # generalized). Mercado Livre resolves to the live resolver's JS verbatim, so the
                # default ML behavior is byte-identical; Shopee/Amazon use their (provisional) JS.
                evaluated = page.evaluate(_profile_extract_js(marketplace))
                # The extraction JS now returns {cards:[...], jsonld:[...]} (richer extraction).
                # Tolerate the legacy bare-list shape too (backward-compatible). _split_extract
                # separates the two so the normalizer can merge JSON-LD over the CSS cards.
                raw_cards, raw_jsonld = _split_extract(evaluated)
            except Exception:
                # A nav / evaluate error -> no listings (caught here; the parent degrades).
                raw_cards = []
                raw_jsonld = []
            finally:
                _release(context, browser, owns_browser)
    except Exception as exc:
        # Any unexpected error (e.g. the context manager itself failing) -> honest unavailable.
        return {"status": "unavailable", "listings": [], "url": search_url,
                "error": type(exc).__name__}

    # Per-profile card fixups BEFORE normalizing. The amazon_br profile re-assembles the correct
    # BR price (reais,centavos -> a float) so the shared integer-reais parser does not 100x-inflate
    # it; ML/Shopee cards pass through unchanged. NEVER fabricates (unparseable price -> None).
    raw_cards = _postprocess_cards(marketplace, raw_cards)
    # Merge the JSON-LD structured data over the CSS-extracted cards (JSON-LD wins per field when
    # present); the shared normalizer dedups + caps + maps to the STORM listing shape.
    listings = _live._playwright_normalize_cards(raw_cards, target, limit, jsonld=raw_jsonld)
    if listings:
        return {"status": "ok", "listings": listings, "url": search_url}
    # Reached-but-empty is the honest anti-bot / no-grid signal; could-not-reach is unavailable.
    status = "empty" if (reached and browser_ok) else "unavailable"
    return {"status": status, "listings": [], "url": search_url}


def _split_extract(evaluated: Any) -> Tuple[List[Any], List[Any]]:
    """Split the page.evaluate result into (cards, jsonld). The richer extraction JS returns
    {cards:[...], jsonld:[...]}; the LEGACY JS returned a bare list of cards. TOTAL -- tolerates
    both shapes (and anything unexpected -> ([], [])). NEVER raises, NEVER fabricates."""
    if isinstance(evaluated, list):
        return list(evaluated), []  # legacy bare-list shape -> no JSON-LD.
    if isinstance(evaluated, dict):
        cards = evaluated.get("cards")
        jsonld = evaluated.get("jsonld")
        return (
            list(cards) if isinstance(cards, list) else [],
            list(jsonld) if isinstance(jsonld, list) else [],
        )
    return [], []


# --------------------------------------------------------------------------- #
# BR price normalization (the 100x-inflation fix for the amazon_br profile).
#
# Amazon BR splits the price into span.a-price-whole (reais; may carry a BR thousands dot like
# "1.234" and a trailing decimal mark) + span.a-price-fraction (centavos, e.g. "99"). The shared
# integer-reais parser (_live._playwright_parse_price) strips ALL non-digits, so "R$ 23,99" became
# 2399.0 (100x). This helper re-assembles a CORRECT float from the whole/fraction split (or from
# the .a-offscreen string that already carries the BR decimal) -- and the amazon_br post-processor
# writes that FLOAT back onto the card so the shared parser passes it through untouched (its
# int/float branch returns float(value) as-is). ML/Shopee never call this -> byte-unchanged.
# --------------------------------------------------------------------------- #
def _br_money_to_float(text: str) -> Optional[float]:
    """Parse a Brazilian money STRING (e.g. 'R$ 23,99', 'R$ 1.234,56', 'R$ 89') into a float.
    BR convention: '.' is the THOUSANDS separator, ',' is the DECIMAL mark. Strategy: keep only
    digits + separators, drop every '.', then treat ',' as the decimal point. A value with no ','
    is whole reais ('R$ 89' -> 89.0; '1.234' -> 1234.0). PURE / TOTAL: no digit -> None (NEVER a
    fabricated price)."""
    s = str(text or "").strip()
    if not s:
        return None
    # Keep only the numeric run (digits + BR separators); discard currency symbols / spaces / text.
    kept = "".join(ch for ch in s if ch.isdigit() or ch in ".,")
    if not any(ch.isdigit() for ch in kept):
        return None
    # BR: '.' = thousands (drop it), ',' = decimal (-> '.'). If no comma, the dots were thousands.
    if "," in kept:
        kept = kept.replace(".", "").replace(",", ".")
    else:
        kept = kept.replace(".", "")
    try:
        return float(kept)
    except (ValueError, TypeError):
        return None


def _normalize_amazon_br_price(card: Dict[str, Any]) -> Optional[float]:
    """Re-assemble the CORRECT Amazon BR price (in reais) as a float from one card.

    Order (degrade-never):
      1. ``price`` = the .a-offscreen string ('R$ 23,99') -- it already carries the BR decimal.
      2. else combine ``price_whole`` (reais, may have a BR thousands dot) + ``price_fraction``
         (centavos): "23" + "99" -> 23.99; "1.234" + "56" -> 1234.56; whole only -> 89.0.
    PURE / TOTAL: nothing parseable -> None (NEVER a fabricated/guessed price)."""
    # 1. The .a-offscreen string is the cleanest single source (it has the decimal already).
    offscreen = _br_money_to_float(card.get("price"))
    if offscreen is not None:
        return offscreen
    # 2. Combine the structured whole + fraction spans.
    whole_raw = str(card.get("price_whole") or "").strip()
    # Whole reais: strip BR thousands dots + any trailing decimal mark / non-digits.
    whole_digits = "".join(ch for ch in whole_raw if ch.isdigit())
    if not whole_digits:
        return None  # no reais -> no usable price (centavos alone is not a price).
    frac_raw = str(card.get("price_fraction") or "").strip()
    frac_digits = "".join(ch for ch in frac_raw if ch.isdigit())
    combined = whole_digits
    if frac_digits:
        # Centavos: pad/trim to 2 places so "9" -> "09" reads as 0.09, not 0.9.
        combined = whole_digits + "." + (frac_digits + "00")[:2]
    try:
        return float(combined)
    except (ValueError, TypeError):
        return None


def _postprocess_cards(marketplace: str, raw_cards: List[Any]) -> List[Any]:
    """Per-profile card fixups BEFORE the shared normalizer runs. Currently only the amazon_br
    profile needs one: rewrite each card's ``price`` to the re-assembled BR FLOAT (so the shared
    integer-reais parser passes it through untouched instead of dropping the decimal). ML/Shopee
    (and any other marketplace) are returned UNCHANGED -> their price logic stays byte-identical.
    TOTAL: a non-dict card / an unparseable price is left/set safely; NEVER raises, NEVER fabricates."""
    name = (marketplace or "").strip().lower()
    if name != "amazon_br":
        return raw_cards  # ML / Shopee / unknown -> untouched (byte-identical behavior).
    fixed: List[Any] = []
    for card in raw_cards:
        if isinstance(card, dict):
            price = _normalize_amazon_br_price(card)
            # Write the FLOAT (or None) back: the shared parser returns float(value) as-is for a
            # numeric, and None stays None (honest unparseable). NEVER a fabricated guess.
            card = dict(card)
            card["price"] = price
        fixed.append(card)
    return fixed


def _import_sync_playwright() -> Optional[Any]:
    """Return ``sync_playwright()`` (the context manager), or None when playwright is not
    importable (DEGRADE-NEVER). Read THROUGH the module so a test that monkeypatches
    cex_playwright_scrape.sync_playwright is honored (no real browser is touched)."""
    fn = globals().get("sync_playwright")
    if fn is None:
        try:
            from playwright.sync_api import sync_playwright as fn  # type: ignore[import]
        except Exception:
            return None
    try:
        return fn()
    except Exception:
        return None


def _acquire_browser(p: Any, cdp_url: str) -> Tuple[Optional[Any], bool]:
    """Acquire a browser from the playwright handle, trying the strategies in order:
      (a) connect_over_cdp(cdp_url | env CEX_CDP_URL | default) -- reuse a RUNNING real Chrome
          (we do NOT own it -> we must NOT close it, only our context);
      (b) chromium.launch(headless=True, args=[anti-bot flags]) -- our OWN browser (we own it).
    Returns (browser, owns_browser). (None, False) when NEITHER works (lane unavailable).
    DEGRADE-NEVER: every step is wrapped; a failure falls through to the next / to None."""
    url = (cdp_url or "").strip() or os.environ.get("CEX_CDP_URL") or _DEFAULT_CDP_URL
    chromium = getattr(p, "chromium", None)
    if chromium is None:
        return None, False
    # (a) reuse a running real Chrome over CDP (0 install, real session -- the PROVEN path).
    try:
        browser = chromium.connect_over_cdp(url)
        if browser is not None:
            return browser, False  # we do NOT own a CDP-attached browser.
    except Exception:
        pass
    # (b) launch our own headless chromium with anti-bot flags.
    try:
        browser = chromium.launch(headless=True, args=list(_LAUNCH_ARGS))
        if browser is not None:
            return browser, True
    except Exception:
        pass
    return None, False


def _get_rng() -> Any:
    """Return the RNG to use. Honors the module seam (_rng) so a unit test injects a deterministic
    random.Random(seed); else lazily imports the real ``random`` module. TOTAL (never raises)."""
    seam = globals().get("_rng")
    if seam is not None:
        return seam
    import random
    return random


def _choose_ua_profile() -> Tuple[str, str, str]:
    """Pick ONE (UA, sec-ch-ua, sec-ch-ua-platform) profile from the pool via the RNG seam. Rotating
    over a small pool of REAL desktop-Chrome UAs mirrors the marketplace browser_tool's UA rotation
    posture. Deterministic under an injected RNG. TOTAL -> falls back to the first profile."""
    try:
        return _get_rng().choice(_DESKTOP_UA_POOL)
    except Exception:
        return _DESKTOP_UA_POOL[0]


def _choose_accept_language() -> str:
    try:
        return _get_rng().choice(_ACCEPT_LANGUAGE_POOL)
    except Exception:
        return _ACCEPT_LANGUAGE_POOL[0]


def _stealth_init_script(languages: List[str], cores: int) -> str:
    """Render the stealth init-script with the (consistent) navigator.languages + core count. PURE.
    Reads/exploits nothing -- it only patches headless-Chromium bot tells (webdriver/plugins/WebGL/
    canvas) so a real-DOM reader survives bot DETECTION on the SAME public page a shopper loads."""
    langs_js = "[" + ", ".join('"%s"' % str(s) for s in (languages or [])) + "]"
    return _STEALTH_INIT_JS % {"languages": langs_js, "cores": int(cores)}


def _build_stealth_context_options() -> Dict[str, Any]:
    """Compose the context kwargs for an OWNED (launched headless) browser: a rotated REAL UA, a
    matching viewport, the matching Accept-Language header + sec-ch-ua Client-Hints consistent with
    the chosen UA (a mismatched UA/hint pair is itself a bot tell). Returns the kwargs dict AND the
    chosen profile so the caller can apply the matching init-script. TOTAL."""
    ua, sec_ch_ua, sec_ch_ua_platform = _choose_ua_profile()
    accept_language = _choose_accept_language()
    extra_headers = {
        "Accept-Language": accept_language,
        # UA-Client-Hints consistent with the chosen UA (self-consistent fingerprint).
        "sec-ch-ua": sec_ch_ua,
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": sec_ch_ua_platform,
    }
    return {
        "user_agent": ua,
        "viewport": dict(_REALISTIC_VIEWPORT),
        "locale": "pt-BR",
        "extra_http_headers": extra_headers,
        "_ua": ua,  # internal: the caller pops these before new_context.
        "_sec_ch_ua": sec_ch_ua,
    }


def _apply_init_script(context: Any) -> None:
    """Install the stealth init-script on a context (runs in every new document before page JS).
    DEGRADE-NEVER: a driver that lacks add_init_script (or rejects it) is tolerated -- the launch
    still proceeds (the script is an enhancement, not a hard dependency)."""
    fn = getattr(context, "add_init_script", None)
    if fn is None:
        return
    cores = 0
    try:
        cores = _get_rng().choice([4, 8, 12, 16])
    except Exception:
        cores = 8
    try:
        fn(_stealth_init_script(_NAV_LANGUAGES, cores))
    except Exception:
        pass


def _new_context(browser: Any, owns_browser: bool) -> Any:
    """Open a new browser context.

    For an OWNED (launched headless) browser, apply the FULL stealth posture: a rotated REAL UA +
    matching viewport + matching Accept-Language + sec-ch-ua Client-Hints, PLUS the stealth
    init-script (removes navigator.webdriver, spoofs languages/plugins/hardwareConcurrency, light
    canvas/WebGL noise). These only defeat bot DETECTION on a public page (exploit nothing).

    For a CDP-attached real Chrome, use a PLAIN context (the real session already presents a
    believable fingerprint -- no stealth needed, and overriding it could DEGRADE a good profile).

    DEGRADE-NEVER: if the rich-context call is rejected by the driver, fall back to the legacy
    realistic context, then to a plain new_context()."""
    if owns_browser:
        opts = _build_stealth_context_options()
        opts.pop("_ua", None)
        opts.pop("_sec_ch_ua", None)
        try:
            context = browser.new_context(**opts)
            _apply_init_script(context)
            return context
        except Exception:
            pass
        # Fallback A: the legacy realistic context (UA + viewport only).
        try:
            context = browser.new_context(
                user_agent=_REALISTIC_UA, viewport=dict(_REALISTIC_VIEWPORT))
            _apply_init_script(context)
            return context
        except Exception:
            pass
    return browser.new_context()


def _humanize_before_extract(page: Any) -> None:
    """A light human-like interaction before reading the DOM: a randomized micro-pause + a mouse
    move + a small scroll. This reduces "instant headless read" bot heuristics WITHOUT changing the
    page (it scrolls/moves like a shopper would). DEGRADE-NEVER: every step is wrapped -- a driver
    that lacks mouse/evaluate still extracts (the humanize is an enhancement, not a dependency).
    Deterministic jitter under the injected RNG."""
    try:
        jitter = _get_rng().randint(_JITTER_MIN_MS, _JITTER_MAX_MS)
    except Exception:
        jitter = _JITTER_MIN_MS
    try:
        wait = getattr(page, "wait_for_timeout", None)
        if wait is not None:
            wait(jitter)
    except Exception:
        pass
    try:
        mouse = getattr(page, "mouse", None)
        if mouse is not None and getattr(mouse, "move", None) is not None:
            mouse.move(_get_rng().randint(50, 600), _get_rng().randint(50, 400))
    except Exception:
        pass
    try:
        evaluate = getattr(page, "evaluate", None)
        if evaluate is not None:
            evaluate("() => { try { window.scrollBy(0, 400); } catch (e) {} }")
    except Exception:
        pass


def _release(context: Any, browser: Any, owns_browser: bool) -> None:
    """Close the context always; close the browser ONLY when we own it (a CDP-attached real Chrome
    must be left running). TOTAL -- every close is wrapped (a teardown error never propagates)."""
    try:
        if context is not None:
            context.close()
    except Exception:
        pass
    if owns_browser and browser is not None:
        try:
            browser.close()
        except Exception:
            pass


# --------------------------------------------------------------------------- #
# Arg parsing -- the JSON contract (argv[1] or stdin). TOTAL -- never raises.
# --------------------------------------------------------------------------- #
def _parse_request(argv: List[str], stdin_text: str = "") -> Dict[str, Any]:
    """Parse the request JSON from argv[1], else from stdin. TOTAL -> {} on any failure (the
    caller then treats a missing query as unavailable). Coerces the known fields to safe types."""
    raw = ""
    if argv:
        raw = (argv[0] or "").strip()
    if not raw:
        raw = (stdin_text or "").strip()
    if not raw:
        return {}
    try:
        obj = json.loads(raw)
    except Exception:
        return {}
    if not isinstance(obj, dict):
        return {}
    return obj


def _request_query(req: Dict[str, Any]) -> str:
    v = req.get("query")
    return v.strip() if isinstance(v, str) and v.strip() else ""


def _request_marketplace(req: Dict[str, Any]) -> str:
    v = req.get("marketplace")
    return v.strip() if isinstance(v, str) and v.strip() else _DEFAULT_MARKETPLACE


def _request_limit(req: Dict[str, Any]) -> int:
    v = req.get("limit")
    if isinstance(v, bool):
        return _DEFAULT_LIMIT
    if isinstance(v, (int, float)):
        return max(1, int(v))
    if isinstance(v, str):
        try:
            return max(1, int(v.strip()))
        except (ValueError, TypeError):
            return _DEFAULT_LIMIT
    return _DEFAULT_LIMIT


def _request_cdp_url(req: Dict[str, Any]) -> str:
    v = req.get("cdp_url")
    return v.strip() if isinstance(v, str) and v.strip() else ""


# --------------------------------------------------------------------------- #
# __main__ -- read JSON, run the browser, print JSON. NEVER raises out.
# --------------------------------------------------------------------------- #
def _run(argv: List[str], stdin_text: str = "") -> Dict[str, Any]:
    """The full child flow as a pure function (testable): parse -> scrape -> result dict. TOTAL --
    NEVER raises (a missing query / any error -> an 'unavailable' result dict)."""
    req = _parse_request(argv, stdin_text)
    query = _request_query(req)
    if not query:
        return {"status": "unavailable", "listings": [], "error": "no_query"}
    try:
        return scrape(
            query,
            marketplace=_request_marketplace(req),
            limit=_request_limit(req),
            cdp_url=_request_cdp_url(req),
        )
    except Exception as exc:  # belt-and-suspenders -- scrape() is already TOTAL.
        return {"status": "unavailable", "listings": [], "error": type(exc).__name__}


def main(argv: List[str]) -> int:
    """Read the request JSON (argv[1] or stdin), run the scrape, print the result JSON to stdout.
    ALWAYS exits 0 with a JSON line (degrade-never -- the parent parses stdout, never the rc).
    NEVER raises (a print failure is the only uncaught path, which the OS would surface)."""
    stdin_text = ""
    if not argv:
        try:
            if not sys.stdin.isatty():
                stdin_text = sys.stdin.read()
        except Exception:
            stdin_text = ""
    result = _run(argv, stdin_text)
    try:
        sys.stdout.write(json.dumps(result))
        sys.stdout.flush()
    except Exception:
        # Last-resort: emit a minimal unavailable line (no secret was ever in the payload).
        sys.stdout.write('{"status":"unavailable","listings":[]}')
    return 0


__all__ = [
    "scrape",
    "main",
    "SELECTOR_PROFILES",
    "_resolve_selector_profile",
    "_profile_extract_js",
    "_build_stealth_context_options",
    "_stealth_init_script",
    "_choose_ua_profile",
    "_humanize_before_extract",
    "_new_context",
    "_br_money_to_float",
    "_normalize_amazon_br_price",
    "_postprocess_cards",
]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
