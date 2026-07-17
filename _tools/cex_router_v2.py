#!/usr/bin/env python3
"""cex_router_v2: Hybrid Claude/Ollama routing based on task + kind metadata.

Two routing layers:
  1. Kind-based (from kinds_meta.json): requires_live_tools -> Claude-only,
     requires_external_context -> any runtime after N07 pre-flight.
  2. Signature-based (heuristic): production_kc, structural_scaffold, etc.

Kind routing takes precedence when --kind is provided. Signature routing is
the fallback for legacy callers and handoff-inferred tasks.

Usage:
    python _tools/cex_router_v2.py --kind browser_tool
    python _tools/cex_router_v2.py --kind knowledge_card --task handoff.md
    python _tools/cex_router_v2.py --task .cex/runtime/handoffs/n01_task.md
    python _tools/cex_router_v2.py --signature production_kc --grid-size 6

Signatures:
    production_kc        -> citation-sensitive, no fabrication allowed
    structural_scaffold  -> frontmatter + skeleton, cex-student preferred
    intent_classification -> kind/pillar/nucleus resolution, cex-student preferred
    evolve_loop          -> high volume, must be free
    smoke_test           -> trivial output verification, cex-student preferred
    brand_copy           -> voice-critical
    grid_parallel        -> multiple nuclei concurrent
    unknown              -> default free tier
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Backend aliases (resolved from nucleus_models.yaml via cex_model_resolver)
try:
    from cex_model_resolver import get_ollama_config as _get_ollama
    from cex_model_resolver import resolve_model_for_tool as _resolve_tool
    _ollama_cfg = _get_ollama()
    BACKEND_OLLAMA_SMALL = "ollama/" + _ollama_cfg["models"].get("light", "qwen3:8b")
    BACKEND_OLLAMA_LARGE = "ollama/" + _ollama_cfg["models"].get("heavy", "qwen3:14b")
    BACKEND_OLLAMA_STUDENT = "ollama/" + _ollama_cfg["models"].get("student", "cex-student")
    BACKEND_CLAUDE_SONNET = _resolve_tool("cex_router_v2", "standard")["model"]
    BACKEND_CLAUDE_OPUS = _resolve_tool("cex_router_v2", "heavy")["model"]
    BACKEND_CLAUDE_HAIKU = _resolve_tool("cex_router_v2", "light")["model"]
except Exception:
    # Resolver unavailable -- bare shorthands (the CLI + downstream resolvers
    # expand them). No full slug literal keeps the cex_doctor --models gate green.
    BACKEND_OLLAMA_SMALL = "ollama/qwen3:8b"
    BACKEND_OLLAMA_LARGE = "ollama/qwen3:14b"
    BACKEND_OLLAMA_STUDENT = "ollama/cex-student"
    BACKEND_CLAUDE_SONNET = "sonnet"
    BACKEND_CLAUDE_OPUS = "opus"
    BACKEND_CLAUDE_HAIKU = "haiku"

# Batch-cohesion primitives: REUSE cex_retriever TF-IDF (no re-invented
# embeddings). We deliberately reuse the low-level primitives (tokenize,
# strip_frontmatter, cosine_similarity) rather than build_tfidf -- see
# _batch_cohesion for why the corpus-tuned vectorizer is unsuitable here.
try:
    from cex_retriever import cosine_similarity as _bc_cosine
    from cex_retriever import strip_frontmatter as _bc_strip_fm
    from cex_retriever import tokenize as _bc_tokenize
    _RETRIEVER_OK = True
except Exception:  # pragma: no cover - same-dir import, should always resolve
    _RETRIEVER_OK = False

# Amortization guard (Benchmark-2 finding F1): decompose is only cheaper when
# ONE Stage-1 think-plan amortizes across N SIMILAR artifacts. Below this
# average pairwise TF-IDF cosine the batch is heterogeneous -> Mode A.
BATCH_COHESION_THRESHOLD = 0.65


def anthropic_credit_ok() -> bool:
    """Quick check: does Anthropic API key exist AND credit > 0?

    Returns False if ANTHROPIC_API_KEY missing or last known status was 400.
    Checks cached quota state from cex_quota_check.py if present.
    """
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        return False

    cache = ROOT / ".cex" / "runtime" / "quota_state.json"
    if cache.exists():
        try:
            state = json.loads(cache.read_text())
            anthropic = state.get("anthropic", {})
            if anthropic.get("last_error_code") == 400:
                return False
            if anthropic.get("credit_exhausted"):
                return False
        except Exception:
            pass
    return True


def gemini_key_ok() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY", "").strip())


# ---------------------------------------------------------------------------
# Kind metadata routing (W4: PREFLIGHT_EXPANSION)
# ---------------------------------------------------------------------------

KINDS_META_PATH = ROOT / ".cex" / "kinds_meta.json"

_kinds_meta_cache: dict[str, Any] | None = None


def _load_kinds_meta() -> dict[str, Any]:
    """Load kinds_meta.json with single-load cache."""
    global _kinds_meta_cache
    if _kinds_meta_cache is not None:
        return _kinds_meta_cache
    if not KINDS_META_PATH.exists():
        return {}
    try:
        _kinds_meta_cache = json.loads(
            KINDS_META_PATH.read_text(encoding="utf-8"))
        return _kinds_meta_cache
    except Exception:
        return {}


def get_kind_metadata(kind: str) -> dict[str, Any]:
    """Return metadata dict for a kind, or empty dict if unknown."""
    if not kind:
        return {}
    meta = _load_kinds_meta()
    return meta.get(kind, {})


def route_by_kind(
    kind: str,
    grid_size: int = 1,
    signature: str = "",
) -> dict[str, Any] | None:
    """Kind-based routing decision tree (spec W4).

    Returns a routing dict if the kind triggers a rule, or None to fall
    through to signature-based routing.

    Decision tree:
      1. requires_live_tools=True  -> Claude-only (MCP needed at runtime)
      2. requires_external_context -> note in metadata (pre-flight handles it)
      3. Otherwise                 -> None (fall through to pick_backend)
    """
    km = get_kind_metadata(kind)
    if not km:
        return None

    credit = anthropic_credit_ok()

    # Rule 1: live tools required -> Claude-only
    if km.get("requires_live_tools", False):
        if credit:
            return {
                "backend": BACKEND_CLAUDE_OPUS,
                "reason": "kind=%s requires live MCP tools; Claude-only" % kind,
                "fallback": BACKEND_CLAUDE_SONNET,
                "kind_rule": "requires_live_tools",
                "preflight_needed": False,
            }
        return {
            "backend": BACKEND_CLAUDE_SONNET,
            "reason": "kind=%s requires live MCP tools; Claude-only (no Opus credit)" % kind,
            "fallback": "none (live tools mandatory)",
            "kind_rule": "requires_live_tools",
            "preflight_needed": False,
        }

    # Rule 2: external context -> any runtime OK after N07 pre-flight
    if km.get("requires_external_context", False):
        # Flag that pre-flight MCP gather should run before dispatch
        sig_decision = pick_backend(
            signature or "unknown", grid_size=grid_size
        )
        sig_decision["kind_rule"] = "requires_external_context"
        sig_decision["preflight_needed"] = True
        sig_decision["reason"] = (
            "kind=%s needs external context; "
            "N07 pre-flight gathers it, then %s handles generation"
            % (kind, sig_decision["backend"])
        )
        return sig_decision

    # No kind-level override -> fall through
    return None


def infer_kind_from_handoff(handoff_path: Path) -> str:
    """Extract kind from handoff frontmatter or body.

    R-196: prefers the real frontmatter `kind:` field (cex_shared.parse_frontmatter's
    line-anchored close-fence scan) over the raw whole-text regex below, which could
    match a decoy "kind:"/"kind=" mention inside another field's value (or earlier body
    prose) BEFORE reaching the artifact's real kind. Falls back to the original raw-text
    scan when there is no frontmatter (or no `kind` key) -- a handoff that only mentions
    kind in body prose (the documented "or body" case) keeps resolving exactly as before.
    """
    if not handoff_path.exists():
        return ""
    try:
        text = handoff_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
    from cex_shared import parse_frontmatter
    fm = parse_frontmatter(text)
    if fm and fm.get("kind"):
        return str(fm["kind"]).strip()
    match = re.search(r"kind[=:]\s*(\w+)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""


def pick_backend(signature: str, grid_size: int = 1, require_accuracy: bool = False) -> dict:
    """Return {backend, reason, fallback} for given task characteristics."""
    credit = anthropic_credit_ok()

    if signature == "production_kc" or require_accuracy:
        if credit:
            return {
                "backend": BACKEND_CLAUDE_OPUS,
                "reason": "citation-sensitive; fabrication = bug",
                "fallback": BACKEND_OLLAMA_LARGE + " + human_review",
            }
        return {
            "backend": BACKEND_OLLAMA_LARGE,
            "reason": "no Anthropic credit; fabrication risk accepted with human review",
            "fallback": "human_only",
        }

    if signature == "structural_scaffold":
        return {
            "backend": BACKEND_OLLAMA_STUDENT,
            "reason": "cex-student fine-tuned for frontmatter generation (+40% vs base)",
            "fallback": BACKEND_OLLAMA_SMALL,
        }

    if signature == "intent_classification":
        return {
            "backend": BACKEND_OLLAMA_STUDENT,
            "reason": "cex-student trained on 300-kind taxonomy; 100% kind accuracy",
            "fallback": BACKEND_OLLAMA_SMALL,
        }

    if signature == "evolve_loop":
        return {
            "backend": BACKEND_OLLAMA_LARGE,
            "reason": "high-volume iteration; cost forbids paid API",
            "fallback": BACKEND_OLLAMA_SMALL,
        }

    if signature == "smoke_test":
        return {
            "backend": BACKEND_OLLAMA_STUDENT,
            "reason": "cex-student knows correct CEX structure; best for validation",
            "fallback": BACKEND_OLLAMA_SMALL,
        }

    if signature == "brand_copy":
        if credit:
            return {
                "backend": BACKEND_CLAUDE_SONNET,
                "reason": "voice-critical; Sonnet sufficient for copy",
                "fallback": BACKEND_OLLAMA_LARGE + " + N02_polish",
            }
        return {
            "backend": BACKEND_OLLAMA_LARGE,
            "reason": "no credit; voice may drift",
            "fallback": "human_only",
        }

    if signature == "grid_parallel" or grid_size >= 4:
        if credit:
            return {
                "backend": BACKEND_CLAUDE_SONNET,
                "reason": f"grid_size={grid_size}; paid API gives real parallelism",
                "fallback": BACKEND_OLLAMA_LARGE + " (serialized on GPU)",
            }
        return {
            "backend": BACKEND_OLLAMA_LARGE,
            "reason": f"grid_size={grid_size}; serialized on single GPU, ~{grid_size * 40}s",
            "fallback": BACKEND_OLLAMA_SMALL,
        }

    if credit:
        return {
            "backend": BACKEND_CLAUDE_HAIKU,
            "reason": "default paid tier; Haiku 9/9 Mode A per STRESS_TEST_DECOMPOSE",
            "fallback": BACKEND_OLLAMA_LARGE,
        }
    return {
        "backend": BACKEND_OLLAMA_LARGE,
        "reason": "default free tier; no Anthropic credit",
        "fallback": BACKEND_OLLAMA_SMALL,
    }


def infer_signature_from_handoff(handoff_path: Path) -> str:
    """Heuristic: parse handoff text for signature clues.

    R-196: the two kind-keyed branches below check the REAL frontmatter `kind:`
    field first (cex_shared.parse_frontmatter) -- immune to a decoy "kind: ..."
    substring living in another field's value, and correctly handles a quoted
    kind value (e.g. `kind: "knowledge_card"`) that the old raw-substring check
    below would miss entirely. Falls through to the original whole-text
    substring heuristics (unchanged) for every other signature and for
    handoffs that declare kind only in body prose (no frontmatter kind field).
    """
    if not handoff_path.exists():
        return "unknown"
    raw = handoff_path.read_text(encoding="utf-8", errors="ignore")
    from cex_shared import parse_frontmatter
    fm = parse_frontmatter(raw)
    fm_kind = str(fm.get("kind", "")).strip().lower() if fm else ""
    if fm_kind in ("knowledge_card", "decision_record"):
        return "production_kc"
    if fm_kind in ("tagline", "landing_page"):
        return "brand_copy"

    text = raw.lower()
    if "kind: knowledge_card" in text or "kind: decision_record" in text:
        return "production_kc"
    if "intent" in text and ("classif" in text or "resolv" in text or "route" in text):
        return "intent_classification"
    if "smoke" in text or "trivial" in text:
        return "smoke_test"
    if "/evolve" in text or "cycle" in text:
        return "evolve_loop"
    if "kind: tagline" in text or "kind: landing_page" in text or "brand" in text:
        return "brand_copy"
    if "frontmatter only" in text or "scaffold" in text:
        return "structural_scaffold"
    return "unknown"


def _batch_cohesion(batch_artifacts: list[Path]) -> float:
    """Average pairwise TF-IDF cosine similarity across a batch of artifacts.

    Reuses cex_retriever primitives (tokenize, strip_frontmatter,
    cosine_similarity). A cohesion-appropriate smoothed IDF is used on purpose:
    retriever.build_tfidf is corpus-tuned (its max_df=0.9 cap and positive-only
    filter DROP terms shared across the batch) -- but batch-shared terms ARE the
    cohesion signal. Smoothed IDF (log((n+1)/(df+1)) + 1) stays positive so
    shared terms keep weight, and only terms shared by >= 2 docs enter the
    vocabulary (a singleton term carries no cohesion).

    Returns 0.0 when cohesion cannot be computed (degrade-never -> Mode A).
    """
    if not _RETRIEVER_OK:
        return 0.0
    docs: list[list[str]] = []
    for p in batch_artifacts:
        try:
            text = Path(p).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        toks = _bc_tokenize(_bc_strip_fm(text))
        if toks:
            docs.append(toks)
    n = len(docs)
    if n < 2:
        return 0.0

    df: Counter = Counter()
    for toks in docs:
        for w in set(toks):
            df[w] += 1
    vocab = {w for w, c in df.items() if c >= 2}
    if not vocab:
        return 0.0
    idf = {w: math.log((n + 1) / (df[w] + 1)) + 1.0 for w in vocab}

    vectors: list[dict[str, float]] = []
    for toks in docs:
        tf = Counter(toks)
        total = len(toks) or 1
        vectors.append(
            {w: (c / total) * idf[w] for w, c in tf.items() if w in vocab}
        )

    sims: list[float] = []
    for i in range(n):
        for j in range(i + 1, n):
            sims.append(_bc_cosine(vectors[i], vectors[j]))
    if not sims:
        return 0.0
    return sum(sims) / len(sims)


def _amortization_guard(
    batch_artifacts: list[Path],
    min_batch_for_decompose: int,
    kind: str,
) -> tuple[dict[str, Any] | None, str]:
    """Decide whether a batch should be force-routed to decompose.

    Returns (decompose_decision | None, rationale). Decompose is chosen ONLY
    when the batch is large enough AND cohesive enough that one Stage-1 think
    amortizes across N artifacts (Benchmark-2 F1: decompose is NOT cheaper for a
    small or heterogeneous batch -- the Stage-1 think repeats per artifact
    without reuse, so it costs ~Mode A with no payoff).
    """
    n = len(batch_artifacts)
    if n < min_batch_for_decompose:
        return None, (
            "mode_a: batch N=%d < min_batch_for_decompose=%d -- too few to "
            "amortize the Stage-1 think-plan (Benchmark-2 F1)"
            % (n, min_batch_for_decompose)
        )
    cohesion = _batch_cohesion(batch_artifacts)
    if cohesion >= BATCH_COHESION_THRESHOLD:
        rationale = (
            "batch_decompose: N=%d >= %d AND cohesion=%.2f >= %.2f -- one Opus "
            "Stage-1 think-plan amortizes across N similar artifacts; Stage-2 "
            "generation runs on the cheap tier"
            % (n, min_batch_for_decompose, cohesion, BATCH_COHESION_THRESHOLD)
        )
        decision: dict[str, Any] = {
            "backend": BACKEND_CLAUDE_HAIKU,
            "reason": rationale,
            "fallback": BACKEND_OLLAMA_LARGE,
            "signature": "batch_decompose",
            "kind": kind,
            "kind_rule": "none",
            "preflight_needed": False,
            "mode": "B",
            "stage1_backend": BACKEND_CLAUDE_OPUS,
            "batch_size": n,
            "batch_cohesion": round(cohesion, 4),
            "rationale": rationale,
            "anthropic_credit_ok": anthropic_credit_ok(),
            "gemini_key_ok": gemini_key_ok(),
        }
        return decision, rationale
    return None, (
        "mode_a: batch N=%d >= %d BUT cohesion=%.2f < %.2f -- heterogeneous "
        "batch, Stage-1 think repeats per artifact (no amortization, "
        "Benchmark-2 F1)"
        % (n, min_batch_for_decompose, cohesion, BATCH_COHESION_THRESHOLD)
    )


# ---------------------------------------------------------------------------
# W4 WIRE_DORMANT: per-runtime capability matrix feature-filter
# ---------------------------------------------------------------------------
# Route ONLY to runtimes that support a REQUESTED feature (OpenRouter
# require_parameters-style: fail-closed, no emulation). Two safety rails:
#   - degrade-never: a runtime that does NOT declare a capability is treated as
#     UNKNOWN and KEPT (missing data != declared-unsupported). Only an EXPLICIT
#     false (or 0 for an int field) excludes a candidate from a request that
#     requires that capability.
#   - kill-switch: CEX_CAPABILITY_FILTER=0 -> the filter is a no-op (routing is
#     byte-identical to pre-W4). Default ON.
# Capability data is seeded per-runtime in
# nucleus_models.yaml:runtime_capabilities and mirrors the model_provider kind's
# `capabilities:` schema block (N00_genesis/P02_model/_schema.yaml).

CAPABILITY_KEYS = frozenset({
    "tool_calling", "structured_output", "vision", "streaming",
    "json_mode", "parallel_tool_calls", "context_window", "max_output_tokens",
})

_runtime_caps_cache: dict[str, dict[str, Any]] | None = None


def capability_filter_enabled() -> bool:
    """Kill-switch: CEX_CAPABILITY_FILTER=0 disables the W4 feature-filter."""
    return os.environ.get("CEX_CAPABILITY_FILTER", "1") != "0"


def _load_runtime_capabilities() -> dict[str, dict[str, Any]]:
    """Load per-runtime capability seeds from nucleus_models.yaml.

    Returns ``{runtime: {capability: value}}``. degrade-never: any error or a
    missing ``runtime_capabilities`` block -> ``{}`` (so no candidate is ever
    excluded on unknown data). Cached after first load.
    """
    global _runtime_caps_cache
    if _runtime_caps_cache is not None:
        return _runtime_caps_cache
    cfg_path = ROOT / ".cex" / "config" / "nucleus_models.yaml"
    caps: dict[str, dict[str, Any]] = {}
    if cfg_path.exists():
        try:
            import yaml
            with open(cfg_path, encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            raw = cfg.get("runtime_capabilities", {}) or {}
            if isinstance(raw, dict):
                for rt, d in raw.items():
                    if isinstance(d, dict):
                        caps[str(rt)] = dict(d)
        except Exception:
            caps = {}
    _runtime_caps_cache = caps
    return caps


def _runtime_of(backend: str) -> str:
    """Map a backend/model string to a runtime key (claude|gemini|codex|ollama).

    Mirrors the nucleus_models.yaml ``cli:`` runtimes. An unrecognized string ->
    '' (an unknown runtime, which degrade-never keeps). A bare runtime key
    passed in (e.g. 'ollama') is returned as-is.
    """
    if not backend:
        return ""
    b = backend.lower()
    if b in ("claude", "gemini", "codex", "ollama"):
        return b
    if b.startswith("ollama/") or any(t in b for t in (
            "qwen", "gemma", "llama", "cex-student", "mistral", "ollama")):
        return "ollama"
    if "gemini" in b or "google" in b:
        return "gemini"
    if "gpt" in b or "codex" in b or "openai" in b:
        return "codex"
    if "claude" in b or "anthropic" in b or b in ("opus", "sonnet", "haiku", "fable"):
        return "claude"
    return ""


def runtime_supports(
    backend: str,
    capability: str,
    caps_map: dict[str, dict[str, Any]] | None = None,
) -> bool | None:
    """Tri-state capability check for a backend/runtime.

    Returns True (declared-capable), False (declared-incapable), or None
    (unknown -- runtime or capability not declared). Booleans map directly;
    integer caps (context_window/max_output_tokens) are 'supported' when present
    and > 0. None / unknown never excludes a candidate (degrade-never).
    """
    caps_map = _load_runtime_capabilities() if caps_map is None else caps_map
    rt = _runtime_of(backend)
    d = caps_map.get(rt) if rt else None
    if not isinstance(d, dict) or capability not in d:
        return None
    val = d[capability]
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val > 0
    if val is None:
        return None
    return bool(val)


def filter_backends_by_capabilities(
    candidates: list[str],
    required_capabilities: list[str] | None,
    caps_map: dict[str, dict[str, Any]] | None = None,
) -> list[str]:
    """Return the candidate backends that satisfy ALL required capabilities.

    Contract (OpenRouter require_parameters-style, fail-closed):
      - kill-switch ``CEX_CAPABILITY_FILTER=0`` -> return candidates unchanged.
      - empty / None ``required_capabilities`` -> return candidates unchanged.
      - EXCLUDE a candidate iff, for some required capability, its runtime
        EXPLICITLY declares it unsupported (False / 0). No emulation is
        attempted (a structured_output request must NOT reach a
        structured_output:false runtime).
      - degrade-never: a candidate whose runtime does NOT declare the capability
        (unknown) is KEPT -- missing data != declared-unsupported.
    Input order is preserved.
    """
    if not required_capabilities or not capability_filter_enabled():
        return list(candidates)
    caps_map = _load_runtime_capabilities() if caps_map is None else caps_map
    out: list[str] = []
    for cand in candidates:
        if any(runtime_supports(cand, cap, caps_map) is False
               for cap in required_capabilities):
            continue
        out.append(cand)
    return out


def _apply_capability_filter(
    decision: dict[str, Any],
    required_capabilities: list[str] | None,
    caps_map: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Apply the W4 capability feature-filter to a routing decision.

    INERT (returns the decision unchanged, adds NO keys) when the kill-switch is
    set OR no ``required_capabilities`` are given -- so legacy routing stays
    byte-identical. Otherwise it validates the chosen backend, promotes a capable
    fallback when the primary is EXPLICITLY incapable, and annotates the decision
    with ``required_capabilities`` + ``capability_filter``. degrade-never: if no
    candidate is known-capable, the primary is kept and flagged (routing is never
    broken).
    """
    if not required_capabilities or not capability_filter_enabled():
        return decision
    caps_map = _load_runtime_capabilities() if caps_map is None else caps_map
    primary = decision.get("backend", "")
    decision["required_capabilities"] = list(required_capabilities)
    primary_excluded = any(
        runtime_supports(primary, cap, caps_map) is False
        for cap in required_capabilities
    )
    if not primary_excluded:
        decision["capability_filter"] = "ok"
        return decision
    # fail-closed: the primary explicitly declares a required capability
    # unsupported -> try to promote the fallback if it is capable.
    fb = decision.get("fallback", "")
    fb_excluded = (not fb) or any(
        runtime_supports(fb, cap, caps_map) is False
        for cap in required_capabilities
    )
    decision["capability_excluded"] = [primary]
    caps_str = ",".join(required_capabilities)
    if fb and not fb_excluded:
        decision["backend"] = fb
        decision["fallback"] = "none (capability-filtered)"
        decision["capability_filter"] = "swapped_to_fallback"
        decision["reason"] = (
            "%s | W4: primary lacks [%s]; promoted capable fallback"
            % (decision.get("reason", ""), caps_str)
        )
    else:
        # degrade-never: nothing is known-capable. Never return an empty/blocked
        # decision -- keep the primary and flag it for the caller.
        decision["capability_filter"] = "no_capable_candidate"
        decision["reason"] = (
            "%s | W4 WARN: no candidate declares [%s] capable; kept primary "
            "(degrade-never)" % (decision.get("reason", ""), caps_str)
        )
    return decision


def route_task(
    kind: str = "",
    signature: str = "",
    grid_size: int = 1,
    require_accuracy: bool = False,
    handoff_path: Path | None = None,
    batch_artifacts: list[Path] | None = None,
    min_batch_for_decompose: int = 10,
    required_capabilities: list[str] | None = None,
) -> dict[str, Any]:
    """Unified entry point: kind routing -> signature routing -> default.

    Callers can provide any combination of kind, signature, or handoff path.
    The function resolves missing values from the handoff and applies the
    decision tree in priority order.

    Amortization guard (optional, backward-compatible): when ``batch_artifacts``
    is supplied, the batch is force-routed to decompose ONLY if it is large
    (``len >= min_batch_for_decompose``) AND cohesive (avg pairwise TF-IDF
    cosine >= BATCH_COHESION_THRESHOLD). Otherwise routing falls through to the
    normal decision (Mode A) with the reason recorded in ``decision["rationale"]``.
    When ``batch_artifacts`` is None the guard is inert -- behavior is identical
    to legacy callers.

    Capability feature-filter (W4, optional, backward-compatible): when
    ``required_capabilities`` is supplied, the chosen backend is validated
    against the per-runtime capability matrix (a capable fallback is promoted if
    the primary EXPLICITLY lacks a required feature). degrade-never + fail-closed
    + kill-switch ``CEX_CAPABILITY_FILTER=0``. When ``required_capabilities`` is
    None (every legacy caller) the filter adds no keys -- output is identical.
    """
    # Resolve from handoff if needed
    if handoff_path and not kind:
        kind = infer_kind_from_handoff(handoff_path)
    if handoff_path and not signature:
        signature = infer_signature_from_handoff(handoff_path)
    if not signature:
        signature = "unknown"

    # Amortization guard (Benchmark-2 F1). Runs only when a batch is provided;
    # forces decompose for a large+cohesive batch, else records why we stay in
    # Mode A and falls through to the normal decision below.
    batch_rationale: str | None = None
    if batch_artifacts is not None:
        decompose_decision, batch_rationale = _amortization_guard(
            batch_artifacts, min_batch_for_decompose, kind
        )
        if decompose_decision is not None:
            return _apply_capability_filter(
                decompose_decision, required_capabilities)

    # Layer 1: kind-based routing (highest priority)
    if kind:
        kind_decision = route_by_kind(kind, grid_size=grid_size, signature=signature)
        if kind_decision:
            kind_decision.setdefault("signature", signature)
            kind_decision.setdefault("kind", kind)
            kind_decision["anthropic_credit_ok"] = anthropic_credit_ok()
            kind_decision["gemini_key_ok"] = gemini_key_ok()
            if batch_rationale:
                kind_decision["rationale"] = batch_rationale
            return _apply_capability_filter(kind_decision, required_capabilities)

    # Layer 2: signature-based routing (fallback)
    decision = pick_backend(signature, grid_size=grid_size, require_accuracy=require_accuracy)
    decision["signature"] = signature
    decision["kind"] = kind
    decision["kind_rule"] = "none"
    decision["preflight_needed"] = False
    decision["anthropic_credit_ok"] = anthropic_credit_ok()
    decision["gemini_key_ok"] = gemini_key_ok()
    if batch_rationale:
        decision["rationale"] = batch_rationale
    return _apply_capability_filter(decision, required_capabilities)


def route_dispatch_topology(
    batch_artifacts: list[Path] | None = None,
    kind: str = "",
    min_batch_for_swarm: int = 10,
) -> dict[str, Any]:
    """P2.3 INTEGRATION: choose the DEFAULT dispatch topology (make leverage automatic).

    A bulk-similar batch (N >= min_batch_for_swarm AND avg pairwise TF-IDF cohesion
    >= BATCH_COHESION_THRESHOLD) auto-routes to the GATED mentor-student swarm
    (cex_mentor_swarm -- W3 wikilink gate + W5 escalation ladder). A single or
    heterogeneous request stays Mode A (the current solo / interactive path).
    This is what makes the leverage the DEFAULT without rewriting the existing
    dispatch modes (solo / grid / decompose / swarm stay byte-for-byte unchanged).

    Reuses the W4 amortization guard (_amortization_guard / _batch_cohesion) so the
    bulk-similar decision is IDENTICAL to the decompose guard's threshold -- only the
    chosen executor differs (gated swarm instead of plain decompose; the swarm is
    strictly safer because it adds the W2 gate + mentor review on the cheap tier).

    Returns a decision dict with at least:
      topology       -- 'swarm' (bulk-similar) | 'mode_a' (single / heterogeneous)
      tool           -- 'cex_mentor_swarm' | 'solo'
      gated          -- True for the swarm path (W2 gate + W5 ladder), else False
      batch_size, batch_cohesion, min_batch_for_swarm, kind, reason

    Inert by construction: an empty / None batch -> mode_a (a single request is
    never bulk-similar), so a legacy single dispatch always stays Mode A.
    """
    arts = list(batch_artifacts or [])
    decision, rationale = _amortization_guard(arts, min_batch_for_swarm, kind)
    cohesion = round(_batch_cohesion(arts), 4) if len(arts) >= 2 else None
    if decision is not None:
        # Bulk-similar: the amortization guard fired -> route to the GATED swarm.
        reason = rationale.replace("batch_decompose:", "gated_swarm:")
        return {
            "topology": "swarm",
            "tool": "cex_mentor_swarm",
            "gated": True,
            "batch_size": len(arts),
            "batch_cohesion": decision.get("batch_cohesion", cohesion),
            "min_batch_for_swarm": min_batch_for_swarm,
            "kind": kind,
            "reason": reason,
            "rationale": reason,
        }
    return {
        "topology": "mode_a",
        "tool": "solo",
        "gated": False,
        "batch_size": len(arts),
        "batch_cohesion": cohesion,
        "min_batch_for_swarm": min_batch_for_swarm,
        "kind": kind,
        "reason": rationale,
        "rationale": rationale,
    }


# ---------------------------------------------------------------------------
# A2 AUTOROUTE: single-artifact execution-path resolver (LEVERAGE_A2)
# ---------------------------------------------------------------------------
# Picks the CHEAPEST COMPETENT execution path for ONE artifact, by complexity:
#
#   decompose    -> Opus F1-F4 -> cheap F6 -> tools   (structured / template-first)
#   sonnet_solo  -> Mode-A Sonnet full 8F             (mid structural work)
#   mode_a_opus  -> Mode-A Opus full 8F               (complex / uncertain -- the SAFE default)
#
# Design contract (mirrors the handoff + decision_manifest_autonomous_leverage):
#   - CONSERVATIVE: any uncertainty resolves to mode_a_opus (the strong path),
#     NEVER the cheap one. Unknown kind, multi-kind intent, live-MCP, missing
#     metadata -> Opus.
#   - HARD vs SOFT complexity. Hard-complex (live MCP / browser / computer-use /
#     unknown / multi-kind) is IMMOVABLE -- it stays Opus even under Opus-budget
#     pressure (it literally cannot run on the cheap path). Soft-complex (heavy
#     but Sonnet-capable) MAY downshift Opus->Sonnet when the rate-limit guard
#     reports the Opus budget is tight (composes with LEVERAGE_A1).
#   - DETERMINISTIC + offline. Classification is driven by kinds_meta.json
#     (requires_live_tools, max_bytes, depends_on) + small curated allow/deny
#     sets -- no network, no Ollama, no LLM in the dispatch hot path. This is the
#     always-available successor to the Ollama-based cex_preflight_classifier
#     experiment (which needed a live local model); the metadata signal is the
#     same difficulty proxy without the runtime dependency.
#   - FAIL-OPEN: any internal error -> mode_a_opus + a recorded reason. A
#     resolver bug must never block, and must never silently pick a path too weak.

EXEC_PATH_DECOMPOSE = "decompose"
EXEC_PATH_SONNET = "sonnet_solo"
EXEC_PATH_OPUS = "mode_a_opus"

# IMMOVABLE Opus: kinds that need live MCP tools at GENERATION time (the cheap
# Stage-2 producer holds no MCP). requires_live_tools in kinds_meta is the source
# of truth; this set is belt-and-braces for when the metadata file is missing.
LIVE_COMPLEX_KINDS = frozenset({
    "browser_tool", "computer_use", "db_connector", "interactive_demo",
    "mcp_server",
})

# SOFT complex: heavy multi-step reasoning / composition kinds. Opus by default,
# but Sonnet-capable -- so they MAY downshift to Sonnet under Opus-budget
# pressure (they are NOT hard-pinned to Opus the way live-MCP kinds are).
HEAVY_KINDS = frozenset({
    "voice_pipeline", "realtime_session", "agentic_rag", "research_pipeline",
    "graph_rag_config", "self_improvement_loop", "dual_loop_architecture",
    "memory_architecture", "model_architecture", "supervisor", "saga",
    "aggregate_root", "crew_template", "agent_package",
})

# FORCE decompose: template-first / schema-shaped kinds where Opus-Stage-1
# reasoning + cheap-Stage-2 fill is the right economics, even when their
# max_bytes is large (knowledge_card=5120, prompt_template=8192). This allowlist
# overrides the size band for the canonical structured kinds the handoff names.
STRUCTURED_ALLOW = frozenset({
    "knowledge_card", "prompt_template", "faq_entry", "glossary_entry",
    "citation", "changelog", "enum_def", "type_def", "env_config",
    "naming_rule", "few_shot_example", "response_format", "input_schema",
    "validation_schema", "event_schema", "domain_vocabulary", "model_card",
})

# Size bands from the corpus max_bytes distribution (median 4096, p75 5120,
# p90 6144). structured = small + few deps; mid = medium; else complex.
_STRUCTURED_MAX_BYTES = 4096
_STRUCTURED_MAX_DEPS = 1
_MID_MAX_BYTES = 5120
_MID_MAX_DEPS = 3

_MULTI_KIND_RE = re.compile(
    r"\b(crew|swarm)\b|\b\d+\s+(artifacts?|kinds?|files?|builders?)\b",
    re.IGNORECASE,
)


def _is_multi_kind_intent(intent: str) -> bool:
    """High-precision multi-artifact detector (a single decompose run = 1 kind).

    Deliberately low-recall: only explicit multi-signals (crew / swarm / 'N
    artifacts' / two `kind=` tokens) trip it. A miss is harmless -- the handoff
    frontmatter carries a single authoritative kind -- and over-tripping would
    push everything to Opus, defeating the cheap-path default.
    """
    if not intent:
        return False
    if _MULTI_KIND_RE.search(intent):
        return True
    if len(re.findall(r"\bkind\s*[=:]", intent, re.IGNORECASE)) >= 2:
        return True
    return False


# Path strength ladder (cheap -> strong). The classifier refinement and the cap
# downshift both move along this single ranking.
_PATH_RANK = {EXEC_PATH_DECOMPOSE: 0, EXEC_PATH_SONNET: 1, EXEC_PATH_OPUS: 2}
_RANK_PATH = {0: EXEC_PATH_DECOMPOSE, 1: EXEC_PATH_SONNET, 2: EXEC_PATH_OPUS}
# cex_preflight_classifier tier -> minimum path rank it implies (and the inverse).
_TIER_FLOOR = {"free": 0, "mid": 1, "premium": 2}
_FLOOR_TIER = {0: "free", 1: "mid", 2: "premium"}


def _classifier_floor(kind: str, intent: str) -> int | None:
    """OPT-IN refinement: ask cex_preflight_classifier for a difficulty tier.

    Reuses the Ollama-based classifier (cex_preflight_classifier.classify_task)
    as a STRENGTHEN-ONLY signal -- it can only push the deterministic decision to
    a stronger path, never to a cheaper one, so a flaky local model can never
    downgrade a safe decision into an unsafe cheap one. Returns a minimum path
    rank in {0,1,2}, or None when the classifier is unavailable / returns
    'unknown'. Fail-open / degrade-never: never raises, never blocks.
    """
    try:
        import cex_preflight_classifier as cpc
        task = {
            "task_id": "autoroute",
            "target_kind": kind,
            "complexity": "",
            "task_description": intent or kind,
        }
        res = cpc.classify_task(task) or {}
        return _TIER_FLOOR.get(res.get("predicted_tier", "unknown"))
    except Exception:
        return None


def _near_opus_cap() -> bool:
    """True when the rate-limit guard reports the Opus/5h budget is tight.

    Composes with LEVERAGE_A1: reads cex_ratelimit_guard.headroom() (itself
    fail-open) and treats warn/over on either window as cap pressure. Degrade-
    never: guard absent / error -> False (no downshift -> the conservative
    strong path stands).
    """
    try:
        import cex_ratelimit_guard
        hr = cex_ratelimit_guard.headroom()
        if not hr.get("ok", True):
            return False
        return hr.get("overall_status", "green") in ("warn", "over")
    except Exception:
        return False


def _classify_complexity(kind: str, intent: str) -> tuple[str, bool, str]:
    """Return (band, hard, reason). band in {structured, mid, complex}.

    `hard` marks an IMMOVABLE Opus decision (never downshifted under cap).
    """
    if _is_multi_kind_intent(intent):
        return "complex", True, "multi-kind/multi-artifact intent (decompose is single-artifact)"
    km = get_kind_metadata(kind)
    if not kind or not km:
        return "complex", True, "unknown kind '%s' -> SAFE Opus (conservative)" % (kind or "")
    if km.get("requires_live_tools") or kind in LIVE_COMPLEX_KINDS:
        return "complex", True, "requires_live_tools (live MCP at generation time)"
    if kind in STRUCTURED_ALLOW:
        return "structured", False, "structured allowlist (template-first; Opus-Stage-1 + cheap-Stage-2)"
    if kind in HEAVY_KINDS:
        return "complex", False, "heavy multi-step reasoning/composition kind"
    mb = int(km.get("max_bytes") or 0)
    ndeps = len(km.get("depends_on") or [])
    if mb and mb <= _STRUCTURED_MAX_BYTES and ndeps <= _STRUCTURED_MAX_DEPS:
        return "structured", False, "max_bytes=%d<=%d deps=%d<=%d (small structural)" % (
            mb, _STRUCTURED_MAX_BYTES, ndeps, _STRUCTURED_MAX_DEPS)
    if mb and mb <= _MID_MAX_BYTES and ndeps <= _MID_MAX_DEPS:
        return "mid", False, "max_bytes=%d<=%d deps=%d<=%d (mid structural)" % (
            mb, _MID_MAX_BYTES, ndeps, _MID_MAX_DEPS)
    return "complex", False, "max_bytes=%s deps=%d above mid band -> Opus" % (mb or "none", ndeps)


def resolve_exec_path(
    kind: str = "",
    intent: str = "",
    near_opus_cap: bool | None = None,
    handoff_path: Path | None = None,
    use_classifier: bool | None = None,
) -> dict[str, Any]:
    """A2 LEVERAGE: pick the cheapest competent execution path for ONE artifact.

    Args:
      kind: CEX kind (resolved from ``handoff_path`` frontmatter if omitted).
      intent: natural-language task text (multi-kind detection only).
      near_opus_cap: None = auto-detect via the rate-limit guard; True/False
        override (tests pass explicit values).
      handoff_path: optional handoff to infer ``kind`` from.
      use_classifier: None = read CEX_AUTOROUTE_CLASSIFIER env; True/False force
        the opt-in cex_preflight_classifier strengthen-only refinement.

    Returns a dict the dispatcher acts on directly:
      path          -- decompose | sonnet_solo | mode_a_opus
      dispatch_mode -- 'decompose' | 'solo'  (the dispatch.sh verb)
      model         -- '' (decompose) | 'sonnet' | 'opus'
      band, hard, near_opus_cap, cap_downshift, classifier_tier,
      classifier_applied, kind, reason
    """
    try:
        if handoff_path is not None and not kind:
            kind = infer_kind_from_handoff(handoff_path)
        kind = (kind or "").strip()
        if near_opus_cap is None:
            near_opus_cap = _near_opus_cap()

        band, hard, reason = _classify_complexity(kind, intent)
        path = {
            "structured": EXEC_PATH_DECOMPOSE,
            "mid": EXEC_PATH_SONNET,
            "complex": EXEC_PATH_OPUS,
        }[band]

        # Cap composition (A1): when the Opus budget is tight, a SOFT Opus
        # decision runs full Sonnet instead (zero Opus calls). Hard-complex
        # stays Opus -- it cannot run cheaper -- and structured already runs the
        # minimal-Opus decompose path, so neither is touched.
        cap_downshift = False
        if near_opus_cap and not hard and path == EXEC_PATH_OPUS:
            path = EXEC_PATH_SONNET
            cap_downshift = True
            reason += " | near Opus budget -> downshift Opus->Sonnet (0 Opus calls)"

        # OPT-IN classifier refinement (CEX_AUTOROUTE_CLASSIFIER=1). Reuses the
        # Ollama-based cex_preflight_classifier as a STRENGTHEN-ONLY signal: it can
        # push a soft decision to a stronger path (catching a structurally-simple-
        # looking kind that is actually hard) but never to a cheaper one. Default
        # OFF -> the hot path stays deterministic + offline.
        if use_classifier is None:
            use_classifier = os.environ.get("CEX_AUTOROUTE_CLASSIFIER", "0") == "1"
        classifier_tier = None
        classifier_applied = False
        if use_classifier and not hard and _PATH_RANK[path] < 2:
            floor = _classifier_floor(kind, intent)
            if floor is not None:
                classifier_tier = _FLOOR_TIER[floor]
                if floor > _PATH_RANK[path]:
                    path = _RANK_PATH[floor]
                    classifier_applied = True
                    reason += " | classifier(%s) -> strengthen to %s" % (
                        classifier_tier, path)

        if path == EXEC_PATH_DECOMPOSE:
            dispatch_mode, model = "decompose", ""
        elif path == EXEC_PATH_SONNET:
            dispatch_mode, model = "solo", "sonnet"
        else:
            dispatch_mode, model = "solo", "opus"

        return {
            "path": path,
            "dispatch_mode": dispatch_mode,
            "model": model,
            "kind": kind,
            "band": band,
            "hard": hard,
            "near_opus_cap": bool(near_opus_cap),
            "cap_downshift": cap_downshift,
            "classifier_tier": classifier_tier,
            "classifier_applied": classifier_applied,
            "reason": reason,
            "anthropic_credit_ok": anthropic_credit_ok(),
        }
    except Exception as exc:  # degrade-never: fail to the SAFE strong path
        return {
            "path": EXEC_PATH_OPUS,
            "dispatch_mode": "solo",
            "model": "opus",
            "kind": kind,
            "band": "complex",
            "hard": True,
            "near_opus_cap": bool(near_opus_cap) if near_opus_cap is not None else False,
            "cap_downshift": False,
            "classifier_tier": None,
            "classifier_applied": False,
            "reason": "resolver error (fail-open -> Mode-A Opus): %s" % (str(exc)[:160]),
            "error": str(exc)[:200],
        }


def _gather_batch_paths(spec: str) -> list[Path]:
    """Resolve a CLI --batch-dir spec to a list of .md paths.

    Accepts a directory (every .md under it, skipping infra dirs) OR a glob
    pattern (e.g. 'N04_knowledge/**/kc_*.md'). Degrade-never: returns [] when the
    spec resolves to nothing, so an auto dispatch with no batch stays Mode A.
    """
    if not spec:
        return []
    p = Path(spec)
    if p.is_dir():
        skip = {".git", ".obsidian", "__pycache__", "node_modules",
                ".pytest_cache", ".mypy_cache", "compiled"}
        out: list[Path] = []
        for dirpath, dirnames, filenames in os.walk(p):
            dirnames[:] = [d for d in dirnames if d not in skip]
            for fn in filenames:
                if fn.endswith(".md"):
                    out.append(Path(dirpath) / fn)
        return out
    # Glob pattern (supports ** via Path.glob on the repo root or a relative base).
    base = ROOT if not p.is_absolute() else Path(p.anchor)
    pattern = str(p) if p.is_absolute() else spec
    try:
        return [q for q in base.glob(pattern) if q.suffix == ".md"]
    except (ValueError, OSError):
        return []


class UnsupportedTierError(RuntimeError):
    """Raised by get_mode() when a model resolves to a tier that is
    explicitly BLOCKED (``mode: null`` in nucleus_models.yaml -- currently
    only the 'unsupported' tier: raw Ollama qwen3/gemma4, "BLOCKED per
    STRESS_TEST evidence. Do not dispatch.").

    R-011 (audit gap #8 / D5.4): ``mode: null`` is falsy in Python, so the
    old ``tier_def.get("mode", "A") or "A"`` silently converted the block
    signal into "proceed in Mode A". This exception makes the block
    explicit and fail-closed. Callers MUST NOT swallow it into a silent
    Mode A fallback the way a bare ``except Exception`` would -- catch it
    by name (and let it propagate, or otherwise refuse to dispatch).
    """


class UnregisteredModelError(UnsupportedTierError):
    """Raised by get_mode()/get_tier() (R-337, register row R-337/R-344)
    when a model id matches NO tier's ``models:`` list in
    nucleus_models.yaml at all -- distinct from the parent
    ``UnsupportedTierError``'s original meaning (a tier that DOES match but
    is explicitly ``mode: null`` / BLOCKED).

    Before this fix, get_mode()/get_tier() silently returned "A"/"full_8f"
    (the STRONGEST, costliest tier) for ANY id absent from every tier's
    models list -- live-proved to affect 3 real box models (glm-local,
    glm-serverside-flash, arena-model) plus any typo'd/unregistered id.
    "Silently strongest" is the opposite of safe: an unrecognized id got
    the MOST capable treatment instead of being refused. This exception
    makes that refusal explicit and loud instead.

    Deliberately subclasses UnsupportedTierError (not a fresh RuntimeError)
    so every EXISTING caller that already does ``except UnsupportedTierError:
    raise`` (the R-011 fail-closed contract -- e.g. cex_8f_runner.py's
    EightFRunner.__init__) automatically re-raises this too, with ZERO
    caller-side edits: Python's ``except`` matches subclasses by isinstance.
    A caller that instead has only a bare ``except Exception: <swallow>``
    (or no handler at all covering this) keeps its pre-existing behavior for
    THIS exception exactly as it did for the old silent-full_8f default (a
    swallow stays a swallow; an uncaught propagation is new and, for an
    unregistered id, the intended fail-loud outcome) -- see the R-337
    blast-radius audit in docs/PROJECT_BACKLOG.md for the full caller
    table this router change was checked against.
    """


# ---------------------------------------------------------------------------
# R-205: boundary-aware model -> tier matching (get_mode / get_tier)
# ---------------------------------------------------------------------------
# SHOKUNIN (docs/SHOKUNIN_SECOND_HOUSE_2026_07_03.md, finding R-205): the old
# match was bidirectional RAW substring containment (`m in model_name or
# model_name in m`), which matches on ANY character range with no regard for
# token boundaries. Confirmed pathological: model_name="ma4:2" raw-matched
# configured model "gemma4:26b" (a nonsense mid-token infix) and silently
# routed a garbage id into the BLOCKED 'unsupported' tier; "index-cex-
# studentx" raw-matched "cex-student" (local_f6); "super-gpt-59-turbo"
# raw-matched "gpt-5" (f6_generation) -- each is an unrelated model id that
# happened to contain another tier's model string as an infix.
#
# Fix (documented rule): normalized EXACT match first; otherwise tokenize
# both strings on non-alphanumeric separators (-, :, /, ., _) and require the
# SHORTER token sequence to appear as a CONTIGUOUS, token-ALIGNED run inside
# the longer one. This still resolves the two real shorthand patterns this
# router depends on (a bare alias like "haiku"/"sonnet"/"opus" embedded
# inside a versioned id like "claude-sonnet-4-6" -- `cex_run.py --model
# haiku`; a runtime-namespaced id like "ollama/qwen3:8b" embedded around a
# bare configured id "qwen3:8b") while refusing any match that crosses a
# token boundary (the R-205 hole). Known residual: a bare single-token
# numeric alias, e.g. "5", would still whole-token-match "claude-fable-5" --
# narrower than the old raw-substring bug (which matched ANY character
# range) and not exercised by any current caller (grep-verified against
# cex_8f_runner.py / cex_run.py / docs); out of scope for this fix.
_MODEL_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _model_tokens(model_id: str) -> tuple[str, ...]:
    """Lowercase + split a model id into alnum tokens on any run of
    non-alphanumeric separators. Used only by ``_model_id_matches`` (R-205).
    """
    return tuple(_MODEL_TOKEN_RE.findall(model_id.lower()))


def _model_id_matches(model_name: str, configured: str) -> bool:
    """True if caller-supplied ``model_name`` resolves to ``configured``
    (a ``models:`` list entry from nucleus_models.yaml).

    Match rule (R-205, exact-first then boundary-bounded -- see the block
    comment above): normalized exact equality, else a token-aligned
    contiguous-subsequence match. Never raw substring containment.

    R-344(1) tightening: a contiguous-subsequence match starting at position
    0 of the longer token sequence is REJECTED when the two sequences have
    different token counts. Position 0 with leftover trailing tokens means
    the shorter id is a bare, unqualified PREFIX of the longer one -- e.g.
    query "glm-5.2" (tokens glm,5,2) used to prefix-match configured
    "glm-5.2-fast" (tokens glm,5,2,fast) purely because "glm-5.2-fast"
    starts with "glm-5.2", even though DP1 (decision_manifest_glm_bench_
    2026_07_12.yaml) deliberately excluded bare "glm-5.2" from every tier's
    models list and cex_intent.execute_prompt('glm-5.2') raises a dedicated
    ValueError for it -- the two GLM-aware layers disagreed on the same id.
    The symmetric hole (a short configured id like "gpt-5" prefix-matching
    a longer, unrelated query "gpt-5-something") is closed the same way.

    Every legitimate shorthand this router depends on keeps working because
    it always has a token of CONTEXT before the match, never a bare prefix:
    a bare alias ("sonnet" -> "claude-sonnet-4-6") is embedded after the
    "claude-" brand token; a runtime-namespaced id ("ollama/qwen3:8b" ->
    configured "qwen3:8b") is embedded after the "ollama" namespace token.
    See TestModelIdMatchesR344 (test_router_r337_r344.py) for the
    full regression matrix proving this excludes zero real aliases.
    """
    a = (model_name or "").strip().lower()
    b = (configured or "").strip().lower()
    if not a or not b:
        return False
    if a == b:
        return True
    ta, tb = _model_tokens(a), _model_tokens(b)
    if not ta or not tb:
        return False
    shorter, longer = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    n, m = len(shorter), len(longer)
    if n == m:
        # Equal token counts: the only possible "run" is the whole sequence
        # -- either identical (a separator-only spelling difference the
        # a==b string check above didn't catch) or genuinely different ids.
        # No partial-prefix ambiguity is possible at equal length.
        return longer == shorter
    # n < m: `shorter` must be embedded in `longer` with at least one token
    # of context BEFORE it (start > 0) -- start == 0 is the R-344(1) bare-
    # prefix bug excluded above.
    for start in range(1, m - n + 1):
        if longer[start:start + n] == shorter:
            return True
    return False


def get_mode(model_name: str) -> str:
    """Return 8F mode for a model: 'A' (full_8f) or 'B' (decomposed).

    Reads tiers from nucleus_models.yaml. If the model appears in a tier's
    model list, returns that tier's mode.

    Raises:
        UnsupportedTierError: the model's tier has ``mode: null`` in the
            YAML (an explicitly BLOCKED tier, e.g. 'unsupported') -- this
            is a fail-closed signal, not a resolvable default. See R-011.
        UnregisteredModelError (R-337, subclass of UnsupportedTierError):
            the model id does not appear in ANY tier's models list at all.
            Before this fix, an unregistered id silently returned 'A' (the
            strongest/costliest tier) -- live-proved to affect 3 real box
            models (glm-local, glm-serverside-flash, arena-model). Config
            LOAD failures (missing file, unparsable YAML) are a different,
            unchanged degrade-never case -- those still return 'A'.

    R-205: matching is exact-or-token-bounded via ``_model_id_matches``
    (never raw substring containment) -- see the block comment above
    ``_model_id_matches`` for the documented rule.
    """
    cfg_path = ROOT / ".cex" / "config" / "nucleus_models.yaml"
    if not cfg_path.exists():
        return "A"
    try:
        import yaml
        with open(cfg_path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        tiers = cfg.get("tiers", {})
        for tier_name, tier_def in tiers.items():
            models = tier_def.get("models", [])
            for m in models:
                if _model_id_matches(model_name, m):
                    tier_mode = tier_def.get("mode")
                    if tier_mode is None:
                        raise UnsupportedTierError(
                            "model '%s' resolves to tier '%s' which is "
                            "explicitly BLOCKED (mode: null in "
                            "nucleus_models.yaml): %s"
                            % (model_name, tier_name,
                               tier_def.get("description", "do not dispatch"))
                        )
                    return tier_mode
        # R-337: the for-loop above completed with NO match in ANY tier's
        # models list -- fail closed instead of silently returning "A" (see
        # UnregisteredModelError's docstring). Raised INSIDE the try block
        # so the `except UnsupportedTierError: raise` clause immediately
        # below re-raises it (UnregisteredModelError IS-A
        # UnsupportedTierError) instead of the generic `except Exception:
        # pass` swallowing it into the old "A" default.
        raise UnregisteredModelError(
            "model '%s' does not appear in ANY tier's models list in "
            "nucleus_models.yaml -- refusing to silently default to the "
            "strongest tier (full_8f / Mode A). Register it in the "
            "appropriate tiers.<name>.models list, or pass a recognized "
            "alias/id." % model_name
        )
    except UnsupportedTierError:
        raise
    except Exception:
        pass
    return "A"


def get_tier(model_name: str) -> str:
    """Return tier name for a model (full_8f, f6_generation, etc.).

    Raises:
        UnregisteredModelError (R-337, subclass of UnsupportedTierError):
            the model id does not appear in ANY tier's models list at all
            -- see get_mode()'s docstring for the full rationale. A model
            that DOES match a tier (even a BLOCKED one like 'unsupported')
            still returns that tier's plain name, unchanged from before
            this fix -- only genuinely unmatched ids now raise. Config LOAD
            failures (missing file, unparsable YAML) are unchanged and
            still return 'full_8f'.

    R-205: matching is exact-or-token-bounded via ``_model_id_matches``
    (never raw substring containment) -- see the block comment above
    ``_model_id_matches`` for the documented rule.
    """
    cfg_path = ROOT / ".cex" / "config" / "nucleus_models.yaml"
    if not cfg_path.exists():
        return "full_8f"
    try:
        import yaml
        with open(cfg_path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        tiers = cfg.get("tiers", {})
        for tier_name, tier_def in tiers.items():
            models = tier_def.get("models", [])
            for m in models:
                if _model_id_matches(model_name, m):
                    return tier_name
        # R-337: no match in ANY tier -- fail closed (see get_mode's twin
        # comment + UnregisteredModelError's docstring).
        raise UnregisteredModelError(
            "model '%s' does not appear in ANY tier's models list in "
            "nucleus_models.yaml -- refusing to silently report the "
            "strongest tier (full_8f). Register it in the appropriate "
            "tiers.<name>.models list, or pass a recognized alias/id."
            % model_name
        )
    except UnsupportedTierError:
        raise
    except Exception:
        pass
    return "full_8f"


def main() -> int:
    p = argparse.ArgumentParser(
        description="CEX Router v2: kind-based + signature-based backend routing"
    )
    p.add_argument("--task", help="Path to handoff file for inference")
    p.add_argument("--kind", default=None, help="CEX kind (e.g., knowledge_card, browser_tool)")
    p.add_argument("--signature", default=None)
    p.add_argument("--grid-size", type=int, default=1)
    p.add_argument("--require-accuracy", action="store_true")
    p.add_argument("--required-capabilities", default="",
                   help="W4: comma-separated capabilities the runtime MUST support "
                        "(e.g. structured_output,tool_calling,vision). Routes only to "
                        "capable runtimes (fail-closed; degrade-never on unknowns; "
                        "kill-switch CEX_CAPABILITY_FILTER=0).")
    p.add_argument("--json", action="store_true", help="Emit raw JSON")
    p.add_argument("--check-kind", metavar="KIND",
                   help="Check kind metadata and exit (requires_external_context, requires_live_tools)")
    p.add_argument("--dispatch-auto", action="store_true",
                   help="P2.3: decide the DEFAULT dispatch topology (swarm vs mode_a) "
                        "for a batch. Bulk-similar (N>=min-batch AND cohesive) -> gated "
                        "swarm; single/heterogeneous -> Mode A. Consulted by "
                        "`dispatch.sh auto`.")
    p.add_argument("--batch-dir", default="",
                   help="(--dispatch-auto) directory or glob of existing similar .md "
                        "whose cohesion decides swarm vs Mode A")
    p.add_argument("--min-batch", type=int, default=10,
                   help="(--dispatch-auto) min batch size to route to the gated swarm")
    p.add_argument("--exec-path", action="store_true",
                   help="A2 LEVERAGE_A2: resolve the single-artifact execution path "
                        "(decompose | sonnet_solo | mode_a_opus) by kind complexity. "
                        "Consulted by `dispatch.sh autoroute` / CEX_AUTOROUTE=1.")
    p.add_argument("--intent", default="",
                   help="(--exec-path) natural-language task text (multi-kind detection)")
    p.add_argument("--near-opus-cap", default="auto", choices=["auto", "yes", "no"],
                   help="(--exec-path) Opus-budget pressure: auto=consult the rate-limit "
                        "guard (LEVERAGE_A1); yes/no force it")
    p.add_argument("--use-classifier", action="store_const", const=True, default=None,
                   help="(--exec-path) opt-in: consult cex_preflight_classifier (Ollama) "
                        "as a strengthen-only refinement (default: CEX_AUTOROUTE_CLASSIFIER env)")
    args = p.parse_args()

    # A2 exec-path mode: emit the single-artifact path decision and exit.
    if args.exec_path:
        kind = args.kind or ""
        if not kind and args.task:
            kind = infer_kind_from_handoff(Path(args.task))
        cap = {"auto": None, "yes": True, "no": False}[args.near_opus_cap]
        dec = resolve_exec_path(kind=kind, intent=args.intent or "", near_opus_cap=cap,
                                use_classifier=args.use_classifier)
        if args.json:
            print(json.dumps(dec, indent=2))
        else:
            print("path:          %s" % dec["path"])
            print("dispatch_mode: %s" % dec["dispatch_mode"])
            print("model:         %s" % (dec["model"] or "(decompose tier)"))
            print("kind:          %s" % (dec.get("kind") or "(unknown)"))
            print("band:          %s (hard=%s)" % (dec.get("band"), dec.get("hard")))
            print("near_opus_cap: %s (cap_downshift=%s)" % (
                dec.get("near_opus_cap"), dec.get("cap_downshift")))
            print("reason:        %s" % dec["reason"])
        return 0

    # P2.3 dispatch-auto mode: emit the DEFAULT-path topology decision and exit.
    if args.dispatch_auto:
        arts = _gather_batch_paths(args.batch_dir)
        dec = route_dispatch_topology(
            arts, kind=args.kind or "", min_batch_for_swarm=args.min_batch)
        if args.json:
            print(json.dumps(dec, indent=2))
        else:
            print("topology:  %s" % dec["topology"])
            print("tool:      %s" % dec["tool"])
            print("gated:     %s" % dec["gated"])
            print("batch:     %s (cohesion=%s, min=%s)"
                  % (dec["batch_size"], dec["batch_cohesion"], dec["min_batch_for_swarm"]))
            print("reason:    %s" % dec["reason"])
        return 0

    # Quick metadata check mode
    if args.check_kind:
        km = get_kind_metadata(args.check_kind)
        info = {
            "kind": args.check_kind,
            "requires_external_context": km.get("requires_external_context", False),
            "requires_live_tools": km.get("requires_live_tools", False),
            "found": bool(km),
        }
        if args.json:
            print(json.dumps(info, indent=2))
        else:
            for k, v in info.items():
                print("%s: %s" % (k, v))
        return 0

    handoff = Path(args.task) if args.task else None
    req_caps = [c.strip() for c in args.required_capabilities.split(",") if c.strip()]
    decision = route_task(
        kind=args.kind or "",
        signature=args.signature or "",
        grid_size=args.grid_size,
        require_accuracy=args.require_accuracy,
        handoff_path=handoff,
        required_capabilities=req_caps or None,
    )

    if args.json:
        print(json.dumps(decision, indent=2))
    else:
        print("kind:      %s" % decision.get("kind", ""))
        print("kind_rule: %s" % decision.get("kind_rule", "none"))
        print("preflight: %s" % decision.get("preflight_needed", False))
        print("signature: %s" % decision.get("signature", ""))
        print("backend:   %s" % decision["backend"])
        print("reason:    %s" % decision["reason"])
        print("fallback:  %s" % decision["fallback"])
        if "capability_filter" in decision:
            print("required_capabilities: %s"
                  % ",".join(decision.get("required_capabilities", [])))
            print("capability_filter:     %s" % decision["capability_filter"])
        print("anthropic_credit_ok: %s" % decision["anthropic_credit_ok"])
        print("gemini_key_ok:       %s" % decision["gemini_key_ok"])
    return 0


if __name__ == "__main__":
    try:
        from cex_agent_io import wrap_main

        def _main_wrapper(argv):
            sys.argv = [sys.argv[0]] + argv
            return main()

        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_router_v2"))
    except ImportError:
        sys.exit(main())
