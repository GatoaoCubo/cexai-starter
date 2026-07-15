#!/usr/bin/env python3
"""cex_secretariat: Configurable pre-flight intelligence tier.

Runs BEFORE every nucleus dispatch. Resolves intent, ranks ISOs, selects
context -- using the cheapest available model from a fallback chain.

Provider chain (first healthy wins):
  cex-student (ollama) > qwen3:8b (ollama) > haiku (anthropic) > flash (google) > regex (local)

Usage:
    python _tools/cex_secretariat.py --probe
    python _tools/cex_secretariat.py --classify "build a landing page for my SaaS"
    python _tools/cex_secretariat.py --rank-isos circuit_breaker "payment timeout protection"
    python _tools/cex_secretariat.py --select-context knowledge_card "RAG chunking strategies"

Env:
    CEX_SECRETARIAT_DISABLE  truthy (1|true|yes|on) -> kill-switch: every
        live-LLM entry point (classify_intent / rank_isos / select_context)
        short-circuits to its offline shape at the source -- no network, no
        subprocess, no spend (T9, FT_STRESS). The test suite sets it by default.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

log = logging.getLogger("cex.secretariat")

_WARNED_STUDENT = False
_CONFIG_CACHE: dict[str, Any] | None = None

# --- Kill-switch (T9, FT_STRESS) -------------------------------------------
#
# The secretariat is the only tier here that fires a LIVE LLM. classify_intent
# is reached by cex_intent_resolver's phase-2.5 escalation for intents the
# 0-token heuristic cannot resolve; under fuzz (or just on a box where ollama
# is served) that path can burn quota or hang. CEX_SECRETARIAT_DISABLE=1 is the
# kill-switch: when set, EVERY public entry point short-circuits to its
# documented offline shape at the SOURCE -- before resolve_provider probes any
# provider -- so there is no network call, no subprocess, no spend. The test
# suite forces it on by default (root conftest.py); a test that wants the live
# path opts in with monkeypatch.delenv. Read per call (never cached) so it can
# be flipped at runtime.
_DISABLE_TRUTHY = frozenset({"1", "true", "yes", "on"})


def _secretariat_disabled() -> bool:
    """True iff env CEX_SECRETARIAT_DISABLE is truthy (1|true|yes|on)."""
    return os.environ.get(
        "CEX_SECRETARIAT_DISABLE", "").strip().lower() in _DISABLE_TRUTHY


def _unresolved_intent() -> dict[str, Any]:
    """The documented 'unresolved' classify shape (kind=None, not escalated).

    Mirrors the no-provider / error returns in classify_intent, with
    provider='disabled' so telemetry can tell a kill-switched run apart. The
    cex_intent_resolver phase-2.5 path only accepts a result that has BOTH a
    kind AND escalated=True, so this cleanly makes the resolver fall through to
    its documented no-match contract -- no live LLM is ever fired.
    """
    return {"kind": None, "pillar": None, "nucleus": None, "verb": None,
            "confidence": 0.0, "provider": "disabled", "escalated": False}


def _load_config() -> dict[str, Any]:
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE
    cfg_path = ROOT / ".cex" / "config" / "nucleus_models.yaml"
    if not cfg_path.exists():
        return {"enabled": False, "fallback_chain": [], "targets": {}}
    with open(cfg_path, "r", encoding="utf-8") as f:
        full = yaml.safe_load(f) or {}
    _CONFIG_CACHE = full.get("secretariat", {})
    return _CONFIG_CACHE


def _probe_ollama(model: str, timeout: int = 5) -> bool:
    try:
        resp = requests.post(
            "http://localhost:11434/api/show",
            json={"name": model},
            timeout=timeout,
        )
        return resp.status_code == 200
    except Exception:
        return False


def _probe_anthropic() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY", "").strip())


def _probe_google() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY", "").strip())


def probe_providers() -> list[dict]:
    """Return all providers with health status."""
    cfg = _load_config()
    chain = cfg.get("fallback_chain", [])
    results = []
    for entry in chain:
        provider = entry.get("provider", "")
        model = entry.get("model", "")
        status = "unknown"
        if provider == "ollama":
            status = "healthy" if _probe_ollama(model) else "unavailable"
        elif provider == "anthropic":
            status = "healthy" if _probe_anthropic() else "no_api_key"
        elif provider == "google":
            status = "healthy" if _probe_google() else "no_api_key"
        elif provider == "local":
            status = "healthy"
        results.append({
            "provider": provider,
            "model": model,
            "cost": entry.get("cost", "unknown"),
            "status": status,
            "capabilities": entry.get("capabilities", []),
        })
    return results


def resolve_provider(capability: str = "intent") -> dict[str, Any]:
    """Pick best available provider from fallback chain for given capability."""
    global _WARNED_STUDENT
    cfg = _load_config()
    chain = cfg.get("fallback_chain", [])

    for i, entry in enumerate(chain):
        caps = entry.get("capabilities", [])
        if capability not in caps:
            continue

        provider = entry.get("provider", "")
        model = entry.get("model", "")

        if provider == "ollama":
            if _probe_ollama(model):
                return {"provider": provider, "model": model, "index": i}
            if model.startswith("cex-student") and not _WARNED_STUDENT:
                log.warning(
                    "[secretariat] cex-student not available; "
                    "falling back to next provider. "
                    "Install: ollama pull cex-student"
                )
                _WARNED_STUDENT = True
        elif provider == "anthropic":
            if _probe_anthropic():
                return {"provider": provider, "model": model, "index": i}
        elif provider == "google":
            if _probe_google():
                return {"provider": provider, "model": model, "index": i}
        elif provider == "local":
            return {"provider": provider, "model": model, "index": i}

    return {"provider": "local", "model": "cex_intent_resolver", "index": -1,
            "degraded": True}


def _call_ollama(model: str, prompt: str, timeout: int = 30) -> str:
    resp = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 300},
        },
        timeout=timeout,
    )
    return resp.json().get("message", {}).get("content", "")


def _call_anthropic(model: str, prompt: str, timeout: int = 30) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": model,
            "max_tokens": 300,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=timeout,
    )
    data = resp.json()
    blocks = data.get("content", [])
    return blocks[0].get("text", "") if blocks else ""


def _call_google(model: str, prompt: str, timeout: int = 30) -> str:
    key = os.environ.get("GEMINI_API_KEY", "")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "%s:generateContent?key=%s" % (model, key)
    )
    resp = requests.post(
        url,
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=timeout,
    )
    data = resp.json()
    candidates = data.get("candidates", [])
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        return parts[0].get("text", "") if parts else ""
    return ""


def _call_provider(prov: dict, prompt: str, timeout: int = 30) -> str:
    provider = prov["provider"]
    model = prov["model"]
    if provider == "ollama":
        return _call_ollama(model, prompt, timeout)
    if provider == "anthropic":
        return _call_anthropic(model, prompt, timeout)
    if provider == "google":
        return _call_google(model, prompt, timeout)
    return ""


def _parse_json_from_text(text: str) -> dict:
    """Extract first JSON object from LLM response text."""
    import re
    match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return {}


def _load_intent_resolver():
    try:
        from cex_intent_resolver import resolve_intent
        return resolve_intent
    except ImportError:
        return None


INTENT_PROMPT = (
    "Classify this user request into the CEX taxonomy.\n"
    "Request: \"%s\"\n\n"
    "Return ONLY a JSON object with these fields:\n"
    '{"kind": "snake_case_kind", "pillar": "P0X", '
    '"nucleus": "N0X", "verb": "create|improve|analyze|validate|deploy|configure"}\n\n'
    "Use kinds from the 300-kind CEX registry. "
    "If unsure, set kind to null."
)


def classify_intent(text: str) -> dict[str, Any]:
    """Resolve user text to {kind, pillar, nucleus, verb, confidence, provider}.

    Strategy: regex first (0 tokens). If confidence < threshold, escalate to LLM.

    Kill-switch (T9): CEX_SECRETARIAT_DISABLE=1 returns the documented
    'unresolved' shape immediately -- no network, no subprocess, no LLM.
    """
    if _secretariat_disabled():
        return _unresolved_intent()

    cfg = _load_config()
    threshold = cfg.get("intent_confidence_threshold", 0.60)

    resolver = _load_intent_resolver()
    if resolver:
        result = resolver(text)
        if result and result.get("confidence", 0) >= threshold:
            result["provider"] = "local/regex"
            result["escalated"] = False
            return result

    prov = resolve_provider("intent")
    if prov["provider"] == "local":
        if resolver:
            result = resolver(text)
            result["provider"] = "local/regex"
            result["escalated"] = False
            return result
        return {"kind": None, "pillar": None, "nucleus": None, "verb": None,
                "confidence": 0.0, "provider": "none", "escalated": False}

    timeout = cfg.get("timeout_seconds", 30)
    try:
        raw = _call_provider(prov, INTENT_PROMPT % text, timeout)
        parsed = _parse_json_from_text(raw)
        return {
            "kind": parsed.get("kind"),
            "pillar": parsed.get("pillar"),
            "nucleus": parsed.get("nucleus"),
            "verb": parsed.get("verb"),
            "confidence": 0.85,
            "provider": "%s/%s" % (prov["provider"], prov["model"]),
            "escalated": True,
        }
    except Exception as e:
        log.warning("[secretariat] LLM classify failed: %s", e)
        if resolver:
            result = resolver(text)
            result["provider"] = "local/regex+fallback"
            result["escalated"] = False
            return result
        return {"kind": None, "pillar": None, "nucleus": None, "verb": None,
                "confidence": 0.0, "provider": "error", "escalated": False}


ISO_RANK_PROMPT = (
    "You are ranking builder ISOs for the CEX typed knowledge system.\n"
    "Kind: %s\n"
    "Task: %s\n\n"
    "The 12 ISOs (1 per pillar) are:\n"
    "bld_knowledge, bld_model, bld_prompt, bld_tools, bld_output, bld_schema, "
    "bld_eval, bld_architecture, bld_config, bld_memory, bld_feedback, bld_orchestration\n\n"
    "Return ONLY a JSON array of the top 5 most relevant ISOs for this task, "
    "ordered by relevance:\n"
    '[{"iso": "bld_model", "relevance": 0.95}, ...]'
)


def rank_isos(kind: str, task_text: str) -> list[dict]:
    """Return top-N ISOs ranked by relevance. Fallback: default stage filter."""
    default_top5 = [
        {"iso": "bld_model", "relevance": 0.9},
        {"iso": "bld_prompt", "relevance": 0.85},
        {"iso": "bld_schema", "relevance": 0.8},
        {"iso": "bld_architecture", "relevance": 0.75},
        {"iso": "bld_knowledge", "relevance": 0.7},
    ]

    if _secretariat_disabled():
        return default_top5

    prov = resolve_provider("iso_ranking")
    if prov["provider"] == "local":
        return default_top5

    cfg = _load_config()
    timeout = cfg.get("timeout_seconds", 30)
    try:
        raw = _call_provider(prov, ISO_RANK_PROMPT % (kind, task_text), timeout)
        import re
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, list) and len(parsed) >= 3:
                return [{"iso": e.get("iso", ""), "relevance": e.get("relevance", 0.5),
                         "provider": "%s/%s" % (prov["provider"], prov["model"])}
                        for e in parsed[:5]]
    except Exception as e:
        log.warning("[secretariat] ISO ranking failed: %s", e)

    return default_top5


CONTEXT_PROMPT = (
    "You are selecting context for a CEX builder.\n"
    "Kind: %s\n"
    "Task: %s\n\n"
    "Available context types:\n"
    "- knowledge_card (kc_*.md in P01_knowledge/library/kind/)\n"
    "- example artifacts (examples/ or compiled/)\n"
    "- brand config (.cex/brand/brand_config.yaml)\n"
    "- memory (.cex/memory/)\n\n"
    "Return ONLY a JSON array of the top 3 most relevant context paths "
    "this builder needs:\n"
    '[{"type": "knowledge_card", "path": "kc_%s.md", "relevance": 0.95}, ...]'
)


def select_context(kind: str, task_text: str) -> list[dict]:
    """Return top-N context items ranked by relevance. Fallback: TF-IDF."""
    default = [
        {"type": "knowledge_card", "path": "kc_%s.md" % kind, "relevance": 0.9},
        {"type": "schema", "path": "_schema.yaml", "relevance": 0.8},
    ]

    if _secretariat_disabled():
        return default

    try:
        from cex_retriever import search as tfidf_search
        tfidf_results = tfidf_search(task_text, top_k=3)
        if tfidf_results:
            default = [{"type": "tfidf", "path": r.get("path", ""),
                        "relevance": r.get("score", 0.5)} for r in tfidf_results]
    except Exception:
        pass

    prov = resolve_provider("context_selection")
    if prov["provider"] == "local":
        return default

    cfg = _load_config()
    timeout = cfg.get("timeout_seconds", 30)
    try:
        raw = _call_provider(prov, CONTEXT_PROMPT % (kind, task_text, kind), timeout)
        import re
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, list) and len(parsed) >= 2:
                return [{"type": e.get("type", ""), "path": e.get("path", ""),
                         "relevance": e.get("relevance", 0.5),
                         "provider": "%s/%s" % (prov["provider"], prov["model"])}
                        for e in parsed[:5]]
    except Exception as e:
        log.warning("[secretariat] context selection failed: %s", e)

    return default


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    p = argparse.ArgumentParser(description="CEX Secretariat: pre-flight intelligence tier")
    p.add_argument("--probe", action="store_true", help="Show available providers")
    p.add_argument("--classify", metavar="TEXT", help="Classify intent from text")
    p.add_argument("--rank-isos", nargs=2, metavar=("KIND", "TASK"),
                   help="Rank ISOs for kind + task")
    p.add_argument("--select-context", nargs=2, metavar=("KIND", "TASK"),
                   help="Select context for kind + task")
    p.add_argument("--json", action="store_true", help="JSON output")
    args = p.parse_args()

    if args.probe:
        providers = probe_providers()
        if args.json:
            print(json.dumps(providers, indent=2))
        else:
            print("Secretariat providers:")
            print("-" * 60)
            for pr in providers:
                tag = "[OK]" if pr["status"] == "healthy" else "[--]"
                print("  %s %-12s %-30s %s" % (
                    tag, pr["provider"], pr["model"], pr["cost"]))
            healthy = sum(1 for pr in providers if pr["status"] == "healthy")
            print("-" * 60)
            print("  %d/%d providers available" % (healthy, len(providers)))
        return 0

    if args.classify:
        t0 = time.time()
        result = classify_intent(args.classify)
        elapsed = time.time() - t0
        result["elapsed_ms"] = round(elapsed * 1000)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("kind:       %s" % result.get("kind"))
            print("pillar:     %s" % result.get("pillar"))
            print("nucleus:    %s" % result.get("nucleus"))
            print("verb:       %s" % result.get("verb"))
            print("confidence: %.2f" % result.get("confidence", 0))
            print("provider:   %s" % result.get("provider"))
            print("escalated:  %s" % result.get("escalated"))
            print("elapsed:    %dms" % result["elapsed_ms"])
        return 0

    if args.rank_isos:
        kind, task = args.rank_isos
        t0 = time.time()
        results = rank_isos(kind, task)
        elapsed = time.time() - t0
        if args.json:
            print(json.dumps({"isos": results, "elapsed_ms": round(elapsed * 1000)}, indent=2))
        else:
            print("Top ISOs for %s:" % kind)
            for r in results:
                print("  %.2f  %s" % (r.get("relevance", 0), r.get("iso", "")))
            print("elapsed: %dms" % round(elapsed * 1000))
        return 0

    if args.select_context:
        kind, task = args.select_context
        t0 = time.time()
        results = select_context(kind, task)
        elapsed = time.time() - t0
        if args.json:
            print(json.dumps({"context": results, "elapsed_ms": round(elapsed * 1000)}, indent=2))
        else:
            print("Top context for %s:" % kind)
            for r in results:
                print("  %.2f  [%s] %s" % (
                    r.get("relevance", 0), r.get("type", ""), r.get("path", "")))
            print("elapsed: %dms" % round(elapsed * 1000))
        return 0

    p.print_help()
    return 1


if __name__ == "__main__":
    try:
        from cex_agent_io import wrap_main

        def _main_wrapper(argv):
            sys.argv = [sys.argv[0]] + argv
            return main()

        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_secretariat"))
    except ImportError:
        sys.exit(main())
