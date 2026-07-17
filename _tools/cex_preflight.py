#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CEX Preflight -- Hybrid local/cloud context pre-compiler for token budget optimization.

Pre-compiles minimal, surgical context BEFORE nucleus boot using cheap/local
models (Ollama qwen3:8b/14b or Claude Haiku). Reduces token consumption on
the main model (Sonnet/Opus) by 60-70%.

Architecture:
  Phase 1 (LOCAL, $0): TF-IDF ranking + file scanning via Ollama
  Phase 2 (CLOUD, cheap): Haiku semantic rerank (only if local uncertain)

Config: .cex/config/nucleus_models.yaml -> preflight: section
Output: .cex/cache/preflight/{nucleus}_{task_hash}.json

Usage:
    python _tools/cex_preflight.py --nucleus n03 --task "build agent for sales"
    python _tools/cex_preflight.py --handoff .cex/runtime/handoffs/MISSION_n03.md
    python _tools/cex_preflight.py --mission PREFLIGHT
    python _tools/cex_preflight.py --stats
    python _tools/cex_preflight.py --clean
    python _tools/cex_preflight.py --nucleus n03 --task "build agent" --dry-run
    python _tools/cex_preflight.py --compress-boot --dry-run
    python _tools/cex_preflight.py --compress-boot --in-place --ratio 0.7

Exit codes: 0 = success, 1 = error, 2 = cache stale
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cex_shared import (CEX_ROOT, ensure_dir, find_builder_dir, load_all_isos,
                        load_yaml, parse_frontmatter, strip_frontmatter)

try:
    from cex_secretariat import resolve_provider as _secretariat_resolve
    _SECRETARIAT_AVAILABLE = True
except ImportError:
    _SECRETARIAT_AVAILABLE = False

# W1 WIRE_DORMANT: tag external (repo-derived) content as DATA before it enters
# Layer-1 assembly. degrade-never: identity wrap if the helper is absent.
try:
    from cex_untrusted_wrap import wrap_untrusted
except Exception:  # pragma: no cover - defensive
    def wrap_untrusted(chunk: str, src: str = "source"):  # type: ignore[misc]
        return chunk, []

# R-247 consumer half: OPT-IN cross-builder ISO lane for rank_isos(), reading
# the L2 sub-document index cex_total_index.py builds (see its module
# docstring: .cex/total_index/l2_subdocuments.json). Lazy/optional import,
# module-level like the other optional tools above -- degrade-never: if the
# module is unavailable the cross-builder lane silently contributes nothing
# and rank_isos() behaves exactly as it did before this lane existed.
try:
    import cex_total_index as _total_index
    _TOTAL_INDEX_AVAILABLE = True
except ImportError:
    _TOTAL_INDEX_AVAILABLE = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CONFIG_PATH = CEX_ROOT / ".cex" / "config" / "nucleus_models.yaml"
CACHE_DIR = CEX_ROOT / ".cex" / "cache" / "preflight"
# A2.x tenant-path migration: route the handoffs surface through the ONE canonical resolver
# (cex_tenant_paths). CEX_TENANT_ID unset -> tenant_runtime_dir() returns the legacy global path ==
# byte-identical for single-tenant; a bound tenant scopes under .cex/tenants/<tid>/runtime.
# Degrade-never fallback keeps single-tenant safe (_tools already on sys.path above).
try:
    from cex_tenant_paths import tenant_runtime_dir as _tenant_runtime_dir
    HANDOFFS_DIR = _tenant_runtime_dir() / "handoffs"
except Exception:
    HANDOFFS_DIR = CEX_ROOT / ".cex" / "runtime" / "handoffs"
KC_DIR = CEX_ROOT / "N00_genesis" / "P01_knowledge" / "library" / "kind"

# TF-IDF stopwords (EN minimal set for ranking)
_STOPWORDS = frozenset([
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "shall",
    "should", "may", "might", "can", "could", "and", "or", "but", "i",
    "then", "else", "when", "where", "which", "that", "this", "these",
    "those", "it", "its", "in", "on", "at", "to", "for", "from", "by",
    "with", "o", "as", "not", "no", "all", "each", "every", "any",
])

_WORD_RE = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]{2,}")

# A recognizable public-repo URL (github / gitlab / bitbucket), the trigger for the
# reposynth 4th triangulation source (cexai-specs/14_gitreverse US P2 / FR-007).
_REPO_URL_RE = re.compile(
    r"https?://(?:www\.)?(?:github\.com|gitlab\.com|bitbucket\.org)/[\w.-]+/[\w.-]+",
    re.IGNORECASE,
)

# Char budget for the reposynth fragment folded into Layer-1 context (SC-003: the
# enrichment is bounded, returns empty within budget, never raises).
_TRIANGULATION_BUDGET_CHARS = 4000


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_preflight_config() -> dict[str, Any]:
    """Load preflight config from nucleus_models.yaml."""
    if not CONFIG_PATH.exists():
        return _default_config()
    cfg = load_yaml(CONFIG_PATH)
    return cfg.get("preflight", _default_config())


def _get_preflight_cloud_model() -> str:
    """Resolve preflight cloud model via secretariat tier, then resolver fallback."""
    if _SECRETARIAT_AVAILABLE:
        try:
            prov = _secretariat_resolve("intent")
            if prov.get("provider") in ("anthropic", "google"):
                return prov["model"]
        except Exception:
            pass
    try:
        from _tools.cex_model_resolver import get_preflight_model
        return get_preflight_model("cloud").get("model", "claude-haiku-4-5-20251001")
    except Exception:
        return "claude-haiku-4-5-20251001"


def _get_preflight_local_model() -> str:
    """Resolve preflight local model via secretariat tier."""
    if _SECRETARIAT_AVAILABLE:
        try:
            prov = _secretariat_resolve("intent")
            if prov.get("provider") == "ollama":
                return prov["model"]
        except Exception:
            pass
    return "qwen3:14b"


def _default_config() -> dict[str, Any]:
    """Fallback config when YAML is missing."""
    return {
        "enabled": True,
        "strategy": "local",
        "local": {
            "cli": "ollama",
            "model": _get_preflight_local_model(),
            "fallback_model": "qwen3:8b",
            "base_url": "http://localhost:11434/v1",
            "timeout_seconds": 30,
        },
        "cloud": {
            "cli": "claude",
            "model": _get_preflight_cloud_model(),
        },
        "cloud_token_budget": 4000,
        "cache_dir": ".cex/cache/preflight",
        "targets": {
            "max_isos_per_build": 5,
            "max_kcs_per_build": 3,
            "max_context_tokens": 15000,
            "original_avg_tokens": 50000,
        },
    }


# ---------------------------------------------------------------------------
# Tokenization (TF-IDF, no deps)
# ---------------------------------------------------------------------------

def tokenize(text: str) -> list[str]:
    """Extract lowercase tokens, no stopwords."""
    return [w for w in _WORD_RE.findall(text.lower()) if w not in _STOPWORDS]


def tfidf_similarity(query_tokens: list[str], doc_tokens: list[str]) -> float:
    """Compute cosine similarity between query and document using TF-IDF-like scoring."""
    if not query_tokens or not doc_tokens:
        return 0.0
    q_counts = Counter(query_tokens)
    d_counts = Counter(doc_tokens)
    # Intersection terms
    common = set(q_counts.keys()) & set(d_counts.keys())
    if not common:
        return 0.0
    # Simple TF dot product normalized by vector magnitudes
    dot = sum(q_counts[t] * d_counts[t] for t in common)
    mag_q = math.sqrt(sum(v * v for v in q_counts.values()))
    mag_d = math.sqrt(sum(v * v for v in d_counts.values()))
    if mag_q == 0 or mag_d == 0:
        return 0.0
    return dot / (mag_q * mag_d)


# ---------------------------------------------------------------------------
# Token counting (lightweight, no tiktoken required)
# ---------------------------------------------------------------------------

def count_tokens(text: str) -> int:
    """Count tokens. Uses tiktoken if available, else word-based estimate."""
    try:
        from cex_token_budget import count_tokens as _ct
        return _ct(text)
    except Exception:
        # Fallback: ~1.3 tokens per word
        return int(len(text.split()) * 1.3)


# ---------------------------------------------------------------------------
# Phase 1: LOCAL (TF-IDF + optional Ollama)
# ---------------------------------------------------------------------------

def extract_task_info(handoff_text: str) -> dict[str, str]:
    """Extract kind, pillar, domain, and task description from handoff text."""
    info: dict[str, str] = {"kind": "", "pillar": "", "domain": "", "task": ""}

    # Try frontmatter first
    fm = parse_frontmatter(handoff_text)
    if fm:
        info["kind"] = fm.get("kind", "")
        info["pillar"] = fm.get("pillar", "")
        info["domain"] = fm.get("domain", "")
        info["task"] = fm.get("task", "")

    # Extract from body if frontmatter incomplete
    body = strip_frontmatter(handoff_text) if handoff_text.startswith("---") else handoff_text

    if not info["kind"]:
        # Look for kind= or kind: patterns
        m = re.search(r"kind[=:]\s*(\w+)", body, re.IGNORECASE)
        if m:
            info["kind"] = m.group(1)

    if not info["task"]:
        # Use first non-empty, non-header line as task summary
        for line in body.split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("---"):
                info["task"] = line[:200]
                break

    return info


def _cross_builder_isos(
    task_text: str, exclude_kind: str, k: int = 3,
) -> list[dict[str, Any]]:
    """OPT-IN cross-builder ISO lane consumer (R-247 -- see cex_total_index.py's
    module docstring for the L2 sub-document index this reads).

    Surfaces up to `k` ISOs from builders OTHER than `exclude_kind`'s own,
    ranked by relevance to `task_text` via the L2 index's TF-IDF vectors. One
    result per distinct builder (mirrors cex_total_index's own CLI
    `--cross-builder` grouping in `_cmd_query_iso`), highest score first.
    Every returned dict carries `cross_builder=True` so callers can
    distinguish these from the kind-local ISOs `rank_isos` already returns.

    Degrade-never (mission: "Absent index -> exactly current behavior"):
    returns [] -- NEVER raises -- when cex_total_index is not importable, the
    L2 index has not been built yet (.cex/total_index/l2_subdocuments.json
    absent), or the query has no scorable terms against the L2 vocabulary.
    Callers must treat [] as "lane unavailable", exactly like the lane never
    having been consulted -- this is what makes `cross_builder=True` on a
    repo with no total index behave identically to `cross_builder=False`.
    """
    if not _TOTAL_INDEX_AVAILABLE:
        return []
    try:
        payload = _total_index._load_l2_payload()
        if not payload or not payload.get("vectors"):
            return []
        qvec = _total_index._build_query_vector(
            task_text, payload["vocab"], payload["n_docs"] or 1)
        if not qvec:
            return []
        query_tokens = set(_total_index._tokenize(task_text))
        ranked = _total_index._rank_by_vector(
            qvec, payload["isos"], payload["vectors"],
            top_k=len(payload["isos"]) or 1, query_tokens=query_tokens)
    except Exception:
        return []

    exclude_norm = (exclude_kind or "").replace("-", "_")
    by_builder: dict[str, dict[str, Any]] = {}
    for r in ranked:
        if r.get("score", 0) <= 0 or r.get("kind") == exclude_norm:
            continue
        builder = r.get("builder", "?")
        if builder not in by_builder:
            by_builder[builder] = r
    distinct = sorted(by_builder.values(), key=lambda x: x["score"], reverse=True)[:k]
    return [dict(r, cross_builder=True) for r in distinct]


def rank_isos(
    kind: str, task_text: str, max_isos: int = 5,
    cross_builder: bool = False, cross_builder_k: int = 3,
) -> list[dict[str, Any]]:
    """Rank builder ISOs by TF-IDF relevance to task. Returns top-K with scores.

    OPT-IN cross-builder lane (R-247 consumer half; default OFF, so every
    EXISTING caller is byte-identical to before this lane existed -- see
    `_cross_builder_isos`). When `cross_builder=True` and the total-index L2
    layer has been built, up to `cross_builder_k` additional ISOs from OTHER
    builders matching `task_text` are appended, each tagged
    `cross_builder=True`. This fires even when `kind` itself has no local
    builder (the two early-return paths below), since cross-builder
    suggestions are exactly the kind of context a builder-less kind needs.
    Absent index / import failure -> the lane silently contributes nothing
    (degrade-never); the base kind-local ranking is unaffected either way.
    """
    builder_dir = find_builder_dir(kind)
    if not builder_dir:
        return _cross_builder_isos(task_text, kind, cross_builder_k) if cross_builder else []

    all_isos = load_all_isos(builder_dir, kind.replace("-", "_"))
    if not all_isos:
        return _cross_builder_isos(task_text, kind, cross_builder_k) if cross_builder else []

    query_tokens = tokenize(task_text + " " + kind)
    scored = []

    for prefix, content in all_isos.items():
        doc_tokens = tokenize(content)
        score = tfidf_similarity(query_tokens, doc_tokens)
        # Boost critical ISOs (manifest, instruction, system_prompt always relevant)
        if prefix in ("manifest", "instruction", "system"):
            score = max(score, 0.5)  # Floor at 0.5 for essential ISOs
        scored.append({
            "prefix": prefix,
            "filename": f"bld_{prefix}_{kind.replace('-', '_')}.md",
            "score": round(score, 4),
            "tokens": count_tokens(content),
            "path": str(builder_dir / f"bld_{prefix}_{kind.replace('-', '_')}.md"),
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    top = scored[:max_isos]
    if cross_builder:
        top = top + _cross_builder_isos(task_text, kind, cross_builder_k)
    return top


def select_kcs(kind: str, task_text: str, max_kcs: int = 3) -> list[dict[str, Any]]:
    """Select most relevant Knowledge Cards using TF-IDF similarity."""
    results = []

    # Always include the kind's own KC if it exists
    kind_kc = KC_DIR / f"kc_{kind.replace('-', '_')}.md"
    if kind_kc.exists():
        content = kind_kc.read_text(encoding="utf-8")
        results.append({
            "path": str(kind_kc),
            "name": kind_kc.name,
            "score": 1.0,  # Own KC always top relevance
            "tokens": count_tokens(content),
        })

    # Scan for additional relevant KCs
    if KC_DIR.exists():
        query_tokens = tokenize(task_text + " " + kind)
        for kc_file in KC_DIR.glob("kc_*.md"):
            if kc_file == kind_kc:
                continue
            try:
                content = kc_file.read_text(encoding="utf-8")
                doc_tokens = tokenize(content[:2000])  # First 2K chars for speed
                score = tfidf_similarity(query_tokens, doc_tokens)
                if score > 0.1:  # Minimum relevance threshold
                    results.append({
                        "path": str(kc_file),
                        "name": kc_file.name,
                        "score": round(score, 4),
                        "tokens": count_tokens(content),
                    })
            except Exception:
                continue

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:max_kcs]


def dedup_context(texts: list[str]) -> str:
    """Remove redundant content across assembled context pieces."""
    if not texts:
        return ""
    # Simple line-level dedup preserving order
    seen_lines: set[str] = set()
    deduped: list[str] = []
    for text in texts:
        for line in text.split("\n"):
            normalized = line.strip().lower()
            # Skip empty lines and very short lines (headers are fine to repeat)
            if len(normalized) < 10 or normalized not in seen_lines:
                deduped.append(line)
                if len(normalized) >= 10:
                    seen_lines.add(normalized)
    return "\n".join(deduped)


# --- FT glue-brain instrumentation (B1): log preflight + inject decisions (fail-open) ---
try:
    from cex_glue_logger import log_glue as _glue_log
except Exception:  # logger absent/broken -> no-op; preflight must never break
    def _glue_log(*_a, **_k):
        return None


def run_local_phase(
    task_info: dict[str, str],
    config: dict[str, Any],
    dry_run: bool = False,
) -> dict[str, Any]:
    """Phase 1: Local TF-IDF ranking. Zero cost."""
    targets = config.get("targets", {})
    max_isos = targets.get("max_isos_per_build", 5)
    max_kcs = targets.get("max_kcs_per_build", 3)
    max_tokens = targets.get("max_context_tokens", 15000)

    kind = task_info.get("kind", "")
    task = task_info.get("task", "")

    # Rank ISOs
    ranked_isos = rank_isos(kind, task, max_isos) if kind else []

    # Select KCs
    selected_kcs = select_kcs(kind, task, max_kcs) if kind else []

    # Load selected ISO content
    iso_contents = []
    for iso in ranked_isos:
        p = Path(iso["path"])
        if p.exists():
            iso_contents.append(p.read_text(encoding="utf-8"))

    # Load selected KC content
    kc_contents = []
    for kc in selected_kcs:
        p = Path(kc["path"])
        if p.exists():
            kc_contents.append(p.read_text(encoding="utf-8"))

    # Dedup and assemble
    all_content = iso_contents + kc_contents
    compiled = dedup_context(all_content) if not dry_run else ""
    compiled_tokens = count_tokens(compiled) if compiled else sum(
        i.get("tokens", 0) for i in ranked_isos
    ) + sum(k.get("tokens", 0) for k in selected_kcs)

    # Estimate original tokens (all 13 ISOs + all KCs)
    original_tokens = targets.get("original_avg_tokens", 50000)
    if kind:
        builder_dir = find_builder_dir(kind)
        if builder_dir:
            all_iso_data = load_all_isos(builder_dir, kind.replace("-", "_"))
            original_tokens = sum(count_tokens(v) for v in all_iso_data.values())
            # Add estimated KC tokens
            if KC_DIR.exists():
                kc_file = KC_DIR / f"kc_{kind.replace('-', '_')}.md"
                if kc_file.exists():
                    original_tokens += count_tokens(kc_file.read_text(encoding="utf-8"))

    # Confidence: high if TF-IDF scores are clearly separated
    confidence = 0.0
    if ranked_isos:
        top_score = ranked_isos[0]["score"]
        if len(ranked_isos) > 1:
            gap = top_score - ranked_isos[-1]["score"]
            confidence = min(1.0, top_score * 0.6 + gap * 0.4)
        else:
            confidence = top_score * 0.7

    result = {
        "selected_isos": [i["filename"] for i in ranked_isos],
        "iso_details": ranked_isos,
        "selected_kcs": [k["name"] for k in selected_kcs],
        "kc_details": selected_kcs,
        "compiled_prompt": compiled,
        "context_tokens": compiled_tokens,
        "original_tokens": original_tokens,
        "confidence": round(confidence, 3),
        "strategy_used": "local",
        "needs_cloud": confidence < 0.7,
    }

    # FT glue-brain (B1): two distinct pairs from one assembly --
    # preflight = WHAT context + compression decision ; injetar = the final assembled manifest.
    compression = round(1.0 - (compiled_tokens / original_tokens), 3) if original_tokens else 0.0
    _glue_log(
        "preflight",
        {"kind": kind, "task": task, "max_tokens": max_tokens},
        {
            "selected_isos": result["selected_isos"],
            "selected_kcs": result["selected_kcs"],
            "context_tokens": compiled_tokens,
            "original_tokens": original_tokens,
            "needs_cloud": result["needs_cloud"],
        },
        source="heuristic",
        confidence=result["confidence"],
    )
    _glue_log(
        "injetar",
        {"kind": kind, "task": task, "candidates": len(ranked_isos) + len(selected_kcs)},
        {
            "injected_sources": result["selected_isos"] + result["selected_kcs"],
            "context_tokens": compiled_tokens,
            "compression": compression,
        },
        source="heuristic",
        confidence=result["confidence"],
    )
    return result


# ---------------------------------------------------------------------------
# Phase 2: CLOUD (Haiku semantic rerank -- only when confidence < 0.7)
# ---------------------------------------------------------------------------

def _track_preflight_call(provider: str, model: str, prompt: str,
                          response_text: str,
                          input_tokens: int = 0,
                          output_tokens: int = 0) -> None:
    """Best-effort cost tracking for preflight calls (Phase 2 / Phase 3)."""
    if os.environ.get("CEX_TRACK_COST", "1") == "0":
        return
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from cex_cost_tracker import record as _cost_record  # type: ignore
        if input_tokens <= 0:
            input_tokens = max(1, len(prompt) // 4)  # char/4 fallback
        if output_tokens <= 0:
            output_tokens = max(1, len(response_text or "") // 4)
        ctx = os.environ.get("CEX_COST_CONTEXT", "preflight")
        _cost_record(
            provider=provider,
            model=model,
            input_tokens=int(input_tokens),
            output_tokens=int(output_tokens),
            mission=os.environ.get("CEX_MISSION", "") or ctx,
            nucleus=os.environ.get("CEX_NUCLEUS", "n07"),
            preflight_used=True,
        )
    except Exception:
        pass


def call_ollama(prompt: str, config: dict[str, Any]) -> str | None:
    """Call Ollama via OpenAI-compatible API. Returns response text or None.

    Emits cost_log.jsonl event on success (Ollama is free, but the call is
    still measured for ROI rollups in cex_cost_tracker).
    """
    local_cfg = config.get("local", {})
    base_url = local_cfg.get("base_url", "http://localhost:11434/v1")
    model = local_cfg.get("model", "qwen3:14b")
    timeout = local_cfg.get("timeout_seconds", 30)

    try:
        from openai import OpenAI
        client = OpenAI(base_url=base_url, api_key="ollama")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            timeout=timeout,
        )
        text = response.choices[0].message.content
        # Best-effort: real tokens if SDK exposes usage
        usage = getattr(response, "usage", None)
        in_tok = int(getattr(usage, "prompt_tokens", 0) or 0) if usage else 0
        out_tok = int(getattr(usage, "completion_tokens", 0) or 0) if usage else 0
        _track_preflight_call(
            provider="ollama",
            model=f"ollama/{model}",
            prompt=prompt,
            response_text=text or "",
            input_tokens=in_tok,
            output_tokens=out_tok,
        )
        return text
    except Exception:
        # Try fallback model
        fallback = local_cfg.get("fallback_model")
        if fallback and fallback != model:
            try:
                client = OpenAI(base_url=base_url, api_key="ollama")
                response = client.chat.completions.create(
                    model=fallback,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    timeout=timeout,
                )
                text = response.choices[0].message.content
                usage = getattr(response, "usage", None)
                in_tok = int(getattr(usage, "prompt_tokens", 0) or 0) if usage else 0
                out_tok = int(getattr(usage, "completion_tokens", 0) or 0) if usage else 0
                _track_preflight_call(
                    provider="ollama",
                    model=f"ollama/{fallback}",
                    prompt=prompt,
                    response_text=text or "",
                    input_tokens=in_tok,
                    output_tokens=out_tok,
                )
                return text
            except Exception:
                pass
    return None


def call_haiku(prompt: str, config: dict[str, Any]) -> str | None:
    """Call Claude Haiku for semantic reranking. Returns response text or None.

    Emits cost_log.jsonl event with char/4 fallback tokens (chat() does not
    return usage). Tagged provider='claude-cli' to match _CHARS_PER_TOKEN.
    """
    cloud_cfg = config.get("cloud", {})
    model = cloud_cfg.get("model", _get_preflight_cloud_model())

    try:
        from cex_sdk.models.chat import chat
        text = chat(prompt, model=model, max_tokens=1024)
        if text:
            _track_preflight_call(
                provider="claude-cli",
                model=model,
                prompt=prompt,
                response_text=text,
            )
        return text
    except Exception:
        return None


def run_cloud_phase(
    local_result: dict[str, Any],
    task_info: dict[str, str],
    config: dict[str, Any],
) -> dict[str, Any]:
    """Phase 2: Semantic rerank via Haiku (only if local confidence < 0.7)."""
    if not local_result.get("needs_cloud", False):
        return local_result

    strategy = config.get("strategy", "hybrid")
    if strategy == "local":
        # User configured local-only, skip cloud
        return local_result

    task = task_info.get("task", "")
    kind = task_info.get("kind", "")
    iso_names = local_result.get("selected_isos", [])

    # Build reranking prompt
    rerank_prompt = (
        "You are a context relevance scorer for an LLM agent build system.\n"
        "Task: %s\n"
        "Kind: %s\n\n"
        "Rate each builder ISO file 0-1 for relevance to this task.\n"
        "Return ONLY a JSON object mapping filename to score.\n"
        "Files:\n%s"
    ) % (task, kind, "\n".join(f"- {n}" for n in iso_names))

    # Try Ollama first (free), then Haiku (cheap)
    response = None
    if strategy in ("hybrid", "local"):
        response = call_ollama(rerank_prompt, config)

    if response is None and strategy in ("hybrid", "cloud"):
        response = call_haiku(rerank_prompt, config)

    if response is None:
        # Both failed -- return local result as-is
        local_result["strategy_used"] = "local_fallback"
        return local_result

    # Parse reranked scores
    try:
        # Extract JSON from response (may have surrounding text)
        json_match = re.search(r"\{[^}]+\}", response)
        if json_match:
            scores = json.loads(json_match.group())
            # Re-sort ISOs by cloud scores
            for iso in local_result.get("iso_details", []):
                cloud_score = scores.get(iso["filename"], iso["score"])
                if isinstance(cloud_score, (int, float)):
                    iso["score"] = round(float(cloud_score), 4)
            local_result["iso_details"].sort(key=lambda x: x["score"], reverse=True)
            local_result["selected_isos"] = [
                i["filename"] for i in local_result["iso_details"]
            ]
            local_result["strategy_used"] = "hybrid" if strategy == "hybrid" else "cloud"
            local_result["confidence"] = 0.85  # Cloud rerank boosts confidence
    except (json.JSONDecodeError, ValueError):
        local_result["strategy_used"] = "local_fallback"

    return local_result


# ---------------------------------------------------------------------------
# Phase 1b: reposynth triangulation (cexai-specs/14_gitreverse US P2 / FR-007)
# ---------------------------------------------------------------------------

def _extract_repo_url(text: str) -> str | None:
    """Return the first recognizable public-repo URL in ``text`` (github / gitlab /
    bitbucket), or ``None``. The trigger for the reposynth 4th source."""
    if not text:
        return None
    m = _REPO_URL_RE.search(text)
    return m.group(0) if m else None


def reposynth_triangulation(
    task: str,
    *,
    source: Any = None,
    provider: str | None = None,
    budget_chars: int = _TRIANGULATION_BUDGET_CHARS,
) -> str:
    """The reposynth 4th triangulation source for Layer-1 context assembly.

    cexai-specs/14_gitreverse US P2 / FR-007: when a research intent names a
    recognizable repo URL, enrich Layer-1 context with the repo's reverse_prompt
    fragment (a 4th source alongside scrapling / claude-mem / welib). Returns a
    markdown fragment string, or ``""`` when there is nothing to add.

    ADDITIVE + non-blocking + never-raises (SC-003): returns ``""`` -- leaving the
    assembly byte-identical -- when (a) the task names no repo URL, (b) the cexai
    package is absent, or (c) the source is unavailable. The cexai
    ``synthesize_for_triangulation`` already swallows every failure to ``None`` (US
    P2 acceptance #5); the production default has no RepoSource wired and so returns
    ``None`` (no untested live-network path is shipped) -- offline callers / tests
    inject a deterministic ``source`` to exercise the enrichment path."""
    repo_url = _extract_repo_url(task)
    if not repo_url:
        return ""
    try:
        from cexai.tools.reposynth import synthesize_for_triangulation
    except ImportError:
        return ""  # cexai absent -> assembly unchanged (non-blocking)
    try:
        fragment = synthesize_for_triangulation(
            repo_url, source=source, provider=provider
        )
    except Exception:
        return ""  # defense-in-depth: never break preflight (the entrypoint is
        # already resilient, but a future wiring change must not regress this)
    if fragment is None or not getattr(fragment, "body", ""):
        return ""
    body = fragment.body[:budget_chars]
    # W1 WIRE_DORMANT: the repo-derived fragment is EXTERNAL content -- tag it as
    # DATA (guard markers + delimiter defense + injection scan). degrade-never:
    # CEX_UNTRUSTED_WRAP=0 -> body emitted unchanged (assembly byte-identical).
    wrapped, warns = wrap_untrusted(body, src=repo_url)
    if warns:
        sys.stderr.write(
            "[WARN] cex_preflight: %d planted-instruction signal(s) in repo-synth "
            "fragment (tagged as data, NOT obeyed): %s\n"
            % (len(warns), "; ".join(warns[:5]))
        )
    return (
        f"## Triangulation source: {fragment.source} "
        f"(confidence={fragment.confidence})\n\n{wrapped}"
    )


# ---------------------------------------------------------------------------
# Cache I/O
# ---------------------------------------------------------------------------

def task_hash(nucleus: str, task: str) -> str:
    """Generate deterministic hash for cache key."""
    h = hashlib.sha256(f"{nucleus}:{task}".encode()).hexdigest()[:12]
    return h


def write_cache(nucleus: str, result: dict[str, Any], config: dict[str, Any]) -> Path:
    """Write preflight result to cache."""
    cache_dir = CEX_ROOT / config.get("cache_dir", ".cex/cache/preflight")
    ensure_dir(cache_dir)

    t_hash = task_hash(nucleus, result.get("task", ""))
    cache_path = cache_dir / f"{nucleus}_{t_hash}.json"

    cache_data = {
        "nucleus": nucleus,
        "kind": result.get("kind", ""),
        "task_hash": t_hash,
        "compiled_at": datetime.now(timezone.utc).isoformat(),
        "selected_isos": result.get("selected_isos", []),
        "selected_kcs": result.get("selected_kcs", []),
        "context_tokens": result.get("context_tokens", 0),
        "original_tokens": result.get("original_tokens", 0),
        "reduction_pct": round(
            (1 - result.get("context_tokens", 0) / max(result.get("original_tokens", 1), 1)) * 100,
            1,
        ),
        "strategy_used": result.get("strategy_used", "local"),
        "confidence": result.get("confidence", 0.0),
        "compiled_prompt": result.get("compiled_prompt", ""),
    }

    cache_path.write_text(json.dumps(cache_data, indent=2, ensure_ascii=True), encoding="utf-8")
    return cache_path


def read_cache(nucleus: str, task: str, config: dict[str, Any]) -> dict[str, Any] | None:
    """Read preflight cache if fresh. Returns None if stale or missing."""
    cache_dir = CEX_ROOT / config.get("cache_dir", ".cex/cache/preflight")
    t_hash = task_hash(nucleus, task)
    cache_path = cache_dir / f"{nucleus}_{t_hash}.json"

    if not cache_path.exists():
        return None

    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None

    # Check staleness: if any selected ISO has mtime > compiled_at
    compiled_at = data.get("compiled_at", "")
    if not compiled_at:
        return None

    try:
        compiled_ts = datetime.fromisoformat(compiled_at).timestamp()
    except ValueError:
        return None

    kind = data.get("kind", "")
    if kind:
        builder_dir = find_builder_dir(kind)
        if builder_dir:
            for iso_file in builder_dir.glob("bld_*.md"):
                if iso_file.stat().st_mtime > compiled_ts:
                    return None  # Stale

    return data


# ---------------------------------------------------------------------------
# Cache Stats
# ---------------------------------------------------------------------------

def cache_stats() -> dict[str, Any]:
    """Compute cache statistics."""
    if not CACHE_DIR.exists():
        return {"total": 0, "total_bytes": 0, "entries": []}

    entries = []
    total_bytes = 0
    for f in sorted(CACHE_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            size = f.stat().st_size
            total_bytes += size
            entries.append({
                "file": f.name,
                "nucleus": data.get("nucleus", "?"),
                "kind": data.get("kind", "?"),
                "tokens": data.get("context_tokens", 0),
                "original": data.get("original_tokens", 0),
                "reduction": data.get("reduction_pct", 0),
                "strategy": data.get("strategy_used", "?"),
                "compiled_at": data.get("compiled_at", "?"),
                "bytes": size,
            })
        except Exception:
            continue

    return {
        "total": len(entries),
        "total_bytes": total_bytes,
        "entries": entries,
    }


# ---------------------------------------------------------------------------
# Main Preflight Pipeline
# ---------------------------------------------------------------------------

def preflight(
    nucleus: str,
    task: str,
    config: dict[str, Any] | None = None,
    dry_run: bool = False,
    force: bool = False,
    phase0: bool = False,
) -> dict[str, Any]:
    """Run full preflight pipeline for a nucleus task.

    Args:
        nucleus: Nucleus ID (e.g., 'n03')
        task: Task description
        config: Preflight config (loaded from YAML if None)
        dry_run: If True, skip LLM calls and prompt assembly
        force: If True, ignore cache
        phase0: If True, run Phase 0 MCP external context gather (N07 only)

    Returns:
        Preflight result dict (also written to cache)
    """
    if config is None:
        config = load_preflight_config()

    if not config.get("enabled", True):
        return {"skipped": True, "reason": "preflight disabled in config"}

    # Check cache first
    if not force and not dry_run:
        cached = read_cache(nucleus, task, config)
        if cached:
            cached["cache_hit"] = True
            return cached

    # Extract task info
    task_info = extract_task_info(task)
    if not task_info.get("task"):
        task_info["task"] = task

    # Phase 0: External MCP context gather (N07 only, opt-in via phase0=True)
    external_ctx: dict[str, Any] = {}
    external_context_md = ""
    if phase0 and not dry_run:
        try:
            from cex_preflight_mcp import \
                gather_external_context as _mcp_gather
            external_ctx = _mcp_gather(
                nucleus=nucleus,
                kind=task_info.get("kind", ""),
                task=task,
                domain=task_info.get("domain", ""),
                force=force,
            )
            if not external_ctx.get("skipped") and external_ctx.get("has_context"):
                external_context_md = external_ctx.get("context_md", "")
        except ImportError:
            external_ctx = {"skipped": True, "skipped_reason": "cex_preflight_mcp not installed"}
        except Exception as exc:
            external_ctx = {"skipped": True, "skipped_reason": "phase0 error: %s" % exc}

    # Phase 1: Local TF-IDF ranking
    result = run_local_phase(task_info, config, dry_run=dry_run)
    result["task"] = task
    result["kind"] = task_info.get("kind", "")
    result["nucleus"] = nucleus

    # Phase 2: Cloud rerank (only if needed and not dry-run)
    if not dry_run and result.get("needs_cloud", False):
        result = run_cloud_phase(result, task_info, config)

    # Phase 1b: reposynth triangulation (cexai-specs/14_gitreverse US P2 / FR-007).
    # ADDITIVE 4th Layer-1 source: when the task names a recognizable repo URL and
    # cexai is present, fold the repo's reverse_prompt fragment into compiled_prompt.
    # Returns "" (assembly byte-identical) when cexai is absent, no repo URL is named,
    # or the source is unavailable -- never raises (SC-003).
    if not dry_run:
        _frag = reposynth_triangulation(task)
        if _frag:
            base = result.get("compiled_prompt", "")
            result["compiled_prompt"] = (base + "\n\n" + _frag) if base else _frag
            result["context_tokens"] = count_tokens(result["compiled_prompt"])
            result["triangulation_sources"] = result.get(
                "triangulation_sources", []
            ) + ["repo_synthesizer"]

    # Phase 3: Merge external context (Phase 0) with local context
    if external_context_md:
        merged = external_context_md + "\n\n" + result.get("compiled_prompt", "")
        result["compiled_prompt"] = merged
        result["context_tokens"] = count_tokens(merged)
        result["phase0_tokens"] = external_ctx.get("tokens_used", 0)
        result["phase0_sources"] = external_ctx.get("sources_used", [])
        result["phase0_queries"] = external_ctx.get("queries", [])
        result["phase0_result_count"] = external_ctx.get("result_count", 0)
    elif phase0:
        result["phase0_skipped"] = external_ctx.get("skipped_reason", "no context gathered")

    # Write cache (unless dry-run)
    if not dry_run:
        cache_path = write_cache(nucleus, result, config)
        result["cache_path"] = str(cache_path)

    result["cache_hit"] = False
    return result


def preflight_from_handoff(handoff_path: str | Path, config: dict[str, Any] | None = None,
                           dry_run: bool = False) -> dict[str, Any]:
    """Run preflight from a handoff file."""
    path = Path(handoff_path)
    if not path.exists():
        return {"error": f"Handoff not found: {path}"}

    content = path.read_text(encoding="utf-8")

    # Extract nucleus from filename (e.g., MISSION_n03.md -> n03)
    nucleus = "n00"
    name = path.stem.lower()
    for nuc in ["n01", "n02", "n03", "n04", "n05", "n06", "n07"]:
        if nuc in name:
            nucleus = nuc
            break

    # Also check frontmatter
    fm = parse_frontmatter(content)
    if fm and fm.get("nucleus"):
        nucleus = fm["nucleus"].lower()

    return preflight(nucleus, content, config=config, dry_run=dry_run)


def preflight_mission(mission_name: str, config: dict[str, Any] | None = None,
                      dry_run: bool = False) -> list[dict[str, Any]]:
    """Run preflight for all handoffs in a mission."""
    results = []
    pattern = f"{mission_name}_n*.md"
    for handoff in sorted(HANDOFFS_DIR.glob(pattern)):
        result = preflight_from_handoff(handoff, config=config, dry_run=dry_run)
        results.append(result)

    # Also check n0X_task.md files in root
    if not results:
        for nuc in ["n01", "n02", "n03", "n04", "n05", "n06"]:
            task_file = CEX_ROOT / f"{nuc}_task.md"
            if task_file.exists():
                result = preflight_from_handoff(task_file, config=config, dry_run=dry_run)
                results.append(result)

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_result(result: dict[str, Any]) -> None:
    """Pretty-print a preflight result."""
    if result.get("skipped"):
        print("[SKIP] Preflight disabled: %s" % result.get("reason", ""))
        return
    if result.get("error"):
        print("[FAIL] %s" % result["error"])
        return

    nucleus = result.get("nucleus", "?")
    kind = result.get("kind", "?")
    strategy = result.get("strategy_used", "?")
    ctx_tokens = result.get("context_tokens", 0)
    orig_tokens = result.get("original_tokens", 0)
    reduction = round((1 - ctx_tokens / max(orig_tokens, 1)) * 100, 1)
    confidence = result.get("confidence", 0)
    cache_hit = result.get("cache_hit", False)

    print("=" * 60)
    print("  CEX Preflight Result")
    print("=" * 60)
    print("  Nucleus:     %s" % nucleus)
    print("  Kind:        %s" % kind)
    print("  Strategy:    %s" % strategy)
    print("  Cache hit:   %s" % cache_hit)
    print("  Confidence:  %.1f%%" % (confidence * 100))
    print("")
    print("  Token Budget:")
    print("    Original:  %s tokens" % f"{orig_tokens:,}")
    print("    Compiled:  %s tokens" % f"{ctx_tokens:,}")
    print("    Reduction: %.1f%%" % reduction)
    print("")

    isos = result.get("iso_details", [])
    if isos:
        print("  Selected ISOs (%d):" % len(isos))
        for iso in isos:
            print("    [%.3f] %s (%d tok)" % (iso["score"], iso["filename"], iso.get("tokens", 0)))

    kcs = result.get("kc_details", [])
    if kcs:
        print("")
        print("  Selected KCs (%d):" % len(kcs))
        for kc in kcs:
            print("    [%.3f] %s (%d tok)" % (kc["score"], kc["name"], kc.get("tokens", 0)))

    # Phase 0 summary (if run)
    if result.get("phase0_tokens") is not None:
        print("")
        print("  Phase 0 (MCP external):")
        print("    tokens:  %d" % result.get("phase0_tokens", 0))
        print("    sources: %s" % ", ".join(result.get("phase0_sources", [])))
        print("    results: %d" % result.get("phase0_result_count", 0))
    elif result.get("phase0_skipped"):
        print("")
        print("  Phase 0: skipped (%s)" % result["phase0_skipped"])

    if result.get("cache_path"):
        print("")
        print("  Cache: %s" % result["cache_path"])
    print("=" * 60)


def _print_stats() -> None:
    """Print cache statistics."""
    stats = cache_stats()
    print("=" * 60)
    print("  CEX Preflight Cache Stats")
    print("=" * 60)
    print("  Total entries: %d" % stats["total"])
    print("  Total size:    %s bytes" % f"{stats['total_bytes']:,}")
    print("")

    if stats["entries"]:
        print("  %-10s %-20s %8s %8s %7s %-8s" % (
            "Nucleus", "Kind", "Tokens", "Original", "Reduce", "Strategy"))
        print("  " + "-" * 65)
        total_saved = 0
        for e in stats["entries"]:
            saved = e["original"] - e["tokens"]
            total_saved += saved
            print("  %-10s %-20s %8s %8s %6.1f%% %-8s" % (
                e["nucleus"], e["kind"][:20],
                f"{e['tokens']:,}", f"{e['original']:,}",
                e["reduction"], e["strategy"],
            ))
        print("")
        print("  Total tokens saved: %s" % f"{total_saved:,}")
    print("=" * 60)


def main() -> int:
    VERB_HELP = {
        "stats":   "Read-only cache statistics: total entries, total size, "
                   "freshness. Suitable for SessionStart hook (fast, no LLM "
                   "calls). Replaces the v1.0.0-broken --quick flag.",
        "clean":   "Clear preflight cache. Destructive but bounded -- only "
                   "removes .cex/cache/preflight/. Use --dry-run to preview.",
        "compile": "LLMLingua-2 boot context compression. Pass --ratio FLOAT "
                   "(default 0.7, lower = more aggressive). --in-place rewrites "
                   "source files (DESTRUCTIVE -- review diff first).",
        "phase0":  "N07-only Phase 0 MCP external context gather. Run before "
                   "dispatching to non-Claude runtimes. Requires --kind and "
                   "--task. Output: external context block injected in handoff.",
    }
    try:
        from cex_agent_io import maybe_print_verb_help
        if maybe_print_verb_help(sys.argv[1:], VERB_HELP):
            return 0
    except ImportError:
        pass

    parser = argparse.ArgumentParser(
        description="CEX Preflight -- hybrid local/cloud context pre-compiler"
    )
    # Positional verb (v1.2.0+ canonical form). Flag form preserved.
    parser.add_argument("verb", nargs="?", default=None,
                        choices=("stats", "clean", "compile", "phase0"),
                        help="Subcommand. Try `tool <verb> --help`.")
    parser.add_argument("--nucleus", "-n", help="Nucleus ID (e.g., n03)")
    parser.add_argument("--task", "-t", help="Task description")
    parser.add_argument("--kind", "-k", help="CEX kind (e.g., agent, knowledge_card)")
    parser.add_argument("--handoff", help="Path to handoff file")
    parser.add_argument("--mission", help="Mission name (pre-compiles all handoffs)")
    parser.add_argument("--stats", action="store_true", help="Show cache statistics")
    parser.add_argument("--clean", action="store_true", help="Clear preflight cache")
    parser.add_argument("--dry-run", action="store_true", help="Show selections without LLM calls")
    parser.add_argument("--force", action="store_true", help="Ignore cache, recompute")
    parser.add_argument("--phase0", action="store_true",
                        help="Run Phase 0 MCP external context gather before local ranking (N07 only)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--compress-boot", action="store_true",
                        help="Run LLMLingua-2 on boot context (CLAUDE.md + .claude/rules/*.md) via cex_compress.py")
    parser.add_argument("--ratio", type=float, default=0.7,
                        help="Compression ratio for --compress-boot (default 0.7, lower = more aggressive)")
    parser.add_argument("--in-place", action="store_true",
                        help="With --compress-boot: rewrite source files (DESTRUCTIVE)")
    args = parser.parse_args()

    # Positional verb -> activate equivalent flag.
    if args.verb == "stats":
        args.stats = True
    elif args.verb == "clean":
        args.clean = True
    elif args.verb == "compile":
        args.compress_boot = True
    elif args.verb == "phase0":
        args.phase0 = True

    # Compress-boot mode: thin pass-through to cex_compress.py
    if args.compress_boot:
        cmd = [sys.executable, str(Path(__file__).resolve().parent / "cex_compress.py"),
               "--target", "boot", "--ratio", str(args.ratio)]
        if args.dry_run:
            cmd.append("--dry-run")
        if args.in_place:
            cmd.append("--in-place")
        print("[preflight] delegating to cex_compress: %s" % " ".join(cmd[1:]))
        return subprocess.run(cmd, check=False).returncode

    # Stats mode
    if args.stats:
        if args.json:
            print(json.dumps(cache_stats(), indent=2))
        else:
            _print_stats()
        return 0

    # Clean mode
    if args.clean:
        if CACHE_DIR.exists():
            count = 0
            for f in CACHE_DIR.glob("*.json"):
                f.unlink()
                count += 1
            print("[OK] Cleaned %d preflight cache entries" % count)
        else:
            print("[OK] No cache to clean")
        return 0

    # Mission mode
    if args.mission:
        config = load_preflight_config()
        results = preflight_mission(args.mission, config=config, dry_run=args.dry_run)
        if not results:
            print("[WARN] No handoffs found for mission: %s" % args.mission)
            return 1
        for r in results:
            if args.json:
                # Strip compiled_prompt for readable JSON output
                r_copy = {k: v for k, v in r.items() if k != "compiled_prompt"}
                print(json.dumps(r_copy, indent=2))
            else:
                _print_result(r)
        return 0

    # Handoff mode
    if args.handoff:
        config = load_preflight_config()
        result = preflight_from_handoff(args.handoff, config=config, dry_run=args.dry_run)
        if args.json:
            r_copy = {k: v for k, v in result.items() if k != "compiled_prompt"}
            print(json.dumps(r_copy, indent=2))
        else:
            _print_result(result)
        return 0 if not result.get("error") else 1

    # Direct mode
    if args.nucleus and args.task:
        config = load_preflight_config()
        task_text = args.task
        if args.kind and "kind=" not in task_text and "kind:" not in task_text:
            task_text = "kind=%s %s" % (args.kind, task_text)
        result = preflight(
            args.nucleus, task_text,
            config=config, dry_run=args.dry_run, force=args.force,
            phase0=getattr(args, "phase0", False),
        )
        if args.json:
            r_copy = {k: v for k, v in result.items() if k != "compiled_prompt"}
            print(json.dumps(r_copy, indent=2))
        else:
            _print_result(result)
        return 0 if not result.get("error") else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    try:
        from cex_agent_io import wrap_main

        def _main_wrapper(argv):
            sys.argv = [sys.argv[0]] + argv
            return main()

        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_preflight"))
    except ImportError:
        sys.exit(main())
