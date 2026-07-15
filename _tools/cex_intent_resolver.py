#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CEX Intent Resolver -- Python-first kind resolution with ZERO LLM tokens.

Resolves user intent to {kind, pillar, nucleus, verb} using:
  1. Exact match: verb table + kind pattern dict (instant, 0 tokens)
  2. TF-IDF fallback: similarity search over kinds_meta.json descriptions (~10ms)
  3. Returns None if confidence < 60% (caller should use LLM)

Usage (CLI):
    python _tools/cex_intent_resolver.py "criar um agente de pesquisa"
    python _tools/cex_intent_resolver.py "something very vague"
    python _tools/cex_intent_resolver.py --json "improve test coverage"

Usage (import):
    from cex_intent_resolver import resolve_intent
    result = resolve_intent("quero melhorar os testes")
    if result["confidence"] >= 0.6:
        kind, pillar, nucleus = result["kind"], result["pillar"], result["nucleus"]

Exit code: 0 if resolved (confidence >= 0.6), 1 if needs LLM.
"""

import argparse
import json
import math
import os
import re
import sys
import threading
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
KINDS_META_PATH = ROOT / ".cex" / "kinds_meta.json"

# Confidence threshold -- below this, recommend LLM fallback
CONFIDENCE_THRESHOLD = 0.60

# ---------------------------------------------------------------------------
# Normalization (ASCII-safe, no external deps)
# ---------------------------------------------------------------------------

# Accent map using unicode escapes (ASCII-safe source)
_ACCENT_MAP = {
    "\u00e1": "a", "\u00e0": "a", "\u00e3": "a", "\u00e2": "a",
    "\u00e9": "e", "\u00ea": "e", "\u00ed": "i",
    "\u00f3": "o", "\u00f4": "o", "\u00f5": "o",
    "\u00fa": "u", "\u00fc": "u", "\u00e7": "c",
    "\u00e1": "a", "\u00e9": "e", "\u00ed": "i", "\u00f3": "o", "\u00fa": "u",
    "\u00f1": "n",
}

# Stop words (PT + EN) -- common words that add no signal
STOP_WORDS = frozenset({
    "a", "o", "e", "de", "do", "da", "para", "com", "em", "um", "uma",
    "os", "as", "no", "na", "nos", "nas", "que", "se", "por", "mais",
    "como", "sobre", "este", "quero", "preciso", "me", "meu", "minha",
    "the", "a", "an", "and", "or", "o", "to", "in", "for", "with",
    "on", "is", "it", "this", "that", "from", "by", "at", "be", "as",
    "are", "was", "will", "has", "i", "my", "want", "need",
})


def normalize(text: str) -> str:
    """Lowercase, strip accents, remove punctuation."""
    text = text.lower().strip()
    for src, dst in _ACCENT_MAP.items():
        text = text.replace(src, dst)
    text = re.sub(r"[-_]", " ", text)
    text = re.sub(r"[^a-z0-9 ]", "", text)
    return text


def tokenize(text: str) -> list[str]:
    """Normalize, split, remove stop words."""
    words = normalize(text).split()
    return [w for w in words if w not in STOP_WORDS and len(w) >= 2]


# ---------------------------------------------------------------------------
# Boundary-safe pattern matching primitive (R-197, 2026-07-03)
# ---------------------------------------------------------------------------
#
# THE DISEASE: the old matcher did `pattern in norm_text` -- a raw Python
# substring test on the space-joined normalized string. That matches a
# pattern anywhere, including INSIDE a longer, unrelated word:
#   "storage"  contains "rag" (sto-RAG-e)        -> false rag_source hit
#   "quadrant" contains "adr" (qu-ADR-ant)        -> false decision_record hit
#   "bookclub" contains "kc"  (boo-KC-lub)        -> false knowledge_card hit
#
# THE FIX: match on whole, whitespace-delimited TOKENS, never on raw
# characters. A pattern (one or more words, e.g. "landing page") matches
# iff its token sequence occurs as a CONTIGUOUS run inside the text's token
# sequence. This is the single primitive every substring-style matcher in
# this module (and the upcoming generated L0 pattern table) should call, so
# "does this pattern occur here" has exactly one definition.


def pattern_matches_boundary(pattern: str, norm_text: str) -> bool:
    """True iff `pattern` occurs in `norm_text` as a contiguous run of whole
    tokens (word-boundary match) -- never as a substring inside a longer token.

    Both arguments MUST already be `normalize()`-d (lowercase, accents
    stripped, punctuation removed); this primitive only splits on whitespace,
    it does not normalize. Callers that test many patterns against the SAME
    input (e.g. the KIND_PATTERNS resolve loop) should normalize the text
    once and reuse it across calls rather than re-normalizing per pattern.

    Multi-word patterns are supported: "landing page" matches "a landing
    page for it" (2-token contiguous run) but not "landing pages" (the text
    token "pages" != the pattern token "page" -- no partial-word credit).

    Length-floor discipline (short patterns like "rag", "adr", "kc", all
    <= 3 chars) falls out of the SAME rule with no extra code: a single-token
    pattern is just the m=1 case of "contiguous run of whole tokens", so it
    can only match a token that is EXACTLY equal to it -- "rag" can never
    match the token "storage", regardless of pattern length. Word-boundary
    and length-floor are one mechanism here, not two.

    Returns False for an empty pattern or empty text (nothing to match).
    """
    text_tokens = norm_text.split()
    pattern_tokens = pattern.split()
    if not pattern_tokens or not text_tokens:
        return False
    n, m = len(text_tokens), len(pattern_tokens)
    if m > n:
        return False
    for start in range(n - m + 1):
        if text_tokens[start:start + m] == pattern_tokens:
            return True
    return False


# ---------------------------------------------------------------------------
# Verb Resolution Table (PT + EN -> canonical verb)
# ---------------------------------------------------------------------------

VERB_TABLE = {
    # PT verbs
    "criar": "create", "crie": "create", "cria": "create",
    "construir": "create", "construa": "create",
    "fazer": "create", "faca": "create",
    "melhorar": "improve", "melhore": "improve",
    "evoluir": "improve", "evolua": "improve",
    "analisar": "analyze", "analise": "analyze",
    "revisar": "analyze", "revise": "analyze",
    "validar": "validate", "valide": "validate",
    "verificar": "validate", "verifique": "validate",
    "documentar": "document", "documente": "document",
    "testar": "test", "teste": "test",
    "deployar": "deploy", "implantar": "deploy", "implante": "deploy",
    "configurar": "configure", "configure": "configure",
    "otimizar": "optimize", "otimize": "optimize",
    "pesquisar": "research", "pesquise": "research",
    "investigar": "research", "investigue": "research",
    "monitorar": "monitor", "monitore": "monitor",
    "agendar": "schedule", "agende": "schedule",
    "corrigir": "fix", "corrija": "fix", "consertar": "fix",
    "auditar": "audit", "audite": "audit",
    # EN verbs
    "create": "create", "build": "create", "make": "create",
    "add": "create", "new": "create", "generate": "create",
    "improve": "improve", "enhance": "improve", "evolve": "improve",
    "upgrade": "improve", "refactor": "improve",
    "analyze": "analyze", "review": "analyze", "audit": "audit",
    "inspect": "analyze", "examine": "analyze",
    "validate": "validate", "verify": "validate", "check": "validate",
    "document": "document", "describe": "document", "write": "create",
    "test": "test", "evaluate": "test", "benchmark": "test",
    "deploy": "deploy", "ship": "deploy", "release": "deploy",
    "configure": "configure", "setup": "configure", "config": "configure",
    "optimize": "optimize", "tune": "optimize",
    "research": "research", "investigate": "research", "study": "research",
    "monitor": "monitor", "watch": "monitor", "observe": "monitor",
    "schedule": "schedule", "plan": "schedule", "cron": "schedule",
    "fix": "fix", "debug": "fix", "repair": "fix",
}

# ---------------------------------------------------------------------------
# Kind Pattern Table -- direct keyword -> kind mapping
# Built from the prompt_compiler Kind Resolution Table
# ---------------------------------------------------------------------------

# Each entry: keyword_pattern -> (kind, pillar, nucleus)
# Patterns are normalized (lowercase, no accents)
KIND_PATTERNS = {
    # P01 Knowledge
    "knowledge card": ("knowledge_card", "P01", "N04"),
    "kc": ("knowledge_card", "P01", "N04"),
    "documentar": ("knowledge_card", "P01", "N04"),
    "chunking": ("chunk_strategy", "P01", "N04"),
    "chunk": ("chunk_strategy", "P01", "N04"),
    "citation": ("citation", "P01", "N04"),
    "citacao": ("citation", "P01", "N04"),
    "context doc": ("context_doc", "P01", "N04"),
    "embedding config": ("embedding_config", "P01", "N04"),
    "embedding provider": ("embedder_provider", "P01", "N04"),
    "few shot": ("few_shot_example", "P01", "N04"),
    "glossary": ("glossary_entry", "P01", "N04"),
    "glossario": ("glossary_entry", "P01", "N04"),
    "rag source": ("rag_source", "P01", "N04"),
    "rag": ("rag_source", "P01", "N04"),
    "retriever config": ("retriever_config", "P01", "N04"),
    "vector store": ("vector_store", "P01", "N04"),
    "vector db": ("vector_store", "P01", "N04"),
    # P02 Model
    "agente": ("agent", "P02", "N03"),
    "agent": ("agent", "P02", "N03"),
    "agent package": ("agent_package", "P02", "N03"),
    "axiom": ("axiom", "P02", "N03"),
    "axioma": ("axiom", "P02", "N03"),
    "boot config": ("boot_config", "P02", "N05"),
    "fallback chain": ("fallback_chain", "P02", "N03"),
    "fallback": ("fallback_chain", "P02", "N03"),
    "handoff protocol": ("handoff_protocol", "P02", "N03"),
    "lens": ("lens", "P02", "N03"),
    "lente": ("lens", "P02", "N03"),
    "memory scope": ("memory_scope", "P02", "N04"),
    "mental model": ("mental_model", "P02", "N03"),
    "model card": ("model_card", "P02", "N03"),
    "model provider": ("model_provider", "P02", "N05"),
    "router": ("router", "P02", "N03"),
    "roteador": ("router", "P02", "N03"),
    # P03 Prompt
    "action prompt": ("action_prompt", "P03", "N03"),
    "prompt template": ("prompt_template", "P03", "N03"),
    "template prompt": ("prompt_template", "P03", "N03"),
    "system prompt": ("system_prompt", "P03", "N03"),
    "prompt sistema": ("system_prompt", "P03", "N03"),
    "chain": ("chain", "P03", "N03"),
    "cadeia prompt": ("chain", "P03", "N03"),
    "constraint": ("constraint_spec", "P03", "N03"),
    "restricao": ("constraint_spec", "P03", "N03"),
    "token budget": ("context_window_config", "P03", "N03"),
    "context window": ("context_window_config", "P03", "N03"),
    "instruction": ("instruction", "P03", "N03"),
    "instrucao": ("instruction", "P03", "N03"),
    "prompt compiler": ("prompt_compiler", "P03", "N03"),
    "prompt version": ("prompt_version", "P03", "N03"),
    "reasoning trace": ("reasoning_trace", "P03", "N03"),
    # P04 Tools
    "api client": ("api_client", "P04", "N05"),
    "cliente api": ("api_client", "P04", "N05"),
    "audio tool": ("audio_tool", "P04", "N05"),
    "tts": ("audio_tool", "P04", "N05"),
    "stt": ("audio_tool", "P04", "N05"),
    "browser tool": ("browser_tool", "P04", "N05"),
    "scraper": ("browser_tool", "P04", "N05"),
    "cli tool": ("cli_tool", "P04", "N05"),
    "code executor": ("code_executor", "P04", "N05"),
    "sandbox": ("code_executor", "P04", "N05"),
    "computer use": ("computer_use", "P04", "N05"),
    "daemon": ("daemon", "P04", "N05"),
    "db connector": ("db_connector", "P04", "N05"),
    "database": ("db_connector", "P04", "N05"),
    "document loader": ("document_loader", "P04", "N05"),
    "function def": ("function_def", "P04", "N05"),
    "hook": ("hook", "P04", "N05"),
    "hook config": ("hook_config", "P04", "N05"),
    "mcp server": ("mcp_server", "P04", "N05"),
    "mcp": ("mcp_server", "P04", "N05"),
    "multimodal": ("multi_modal_config", "P04", "N05"),
    "notifier": ("notifier", "P04", "N05"),
    "notification": ("notifier", "P04", "N05"),
    "plugin": ("plugin", "P04", "N05"),
    "extension": ("plugin", "P04", "N05"),
    "research pipeline": ("research_pipeline", "P04", "N01"),
    "pesquisa profunda": ("research_pipeline", "P04", "N01"),
    "deep research": ("research_pipeline", "P04", "N01"),
    "retriever": ("retriever", "P04", "N04"),
    "search tool": ("search_tool", "P04", "N05"),
    "web search": ("search_tool", "P04", "N05"),
    "toolkit": ("toolkit", "P04", "N05"),
    "vision tool": ("vision_tool", "P04", "N05"),
    "ocr": ("vision_tool", "P04", "N05"),
    "webhook": ("webhook", "P04", "N05"),
    # P03 Prompt (curated pins from .claude/rules/n07-input-transmutation.md rows --
    # R-261 evidence: without these, generated L0 patterns shadow the authoritative
    # routing for the exact table phrases: criar slogan -> slo_definition,
    # agendar tarefa -> content_library)
    "slogan": ("tagline", "P03", "N02"),
    "agendar tarefa": ("schedule", "P12", "N07"),
    # P05 Output
    "formatter": ("formatter", "P05", "N03"),
    "landing page": ("landing_page", "P05", "N03"),
    "pagina web": ("landing_page", "P05", "N03"),
    "output validator": ("output_validator", "P05", "N03"),
    "parser": ("parser", "P05", "N03"),
    "response format": ("response_format", "P05", "N03"),
    # P06 Schema
    "enum": ("enum_def", "P06", "N03"),
    "enumeracao": ("enum_def", "P06", "N03"),
    "input schema": ("input_schema", "P06", "N03"),
    "interface": ("interface", "P06", "N03"),
    "contrato": ("interface", "P06", "N03"),
    "type def": ("type_def", "P06", "N03"),
    "custom type": ("type_def", "P06", "N03"),
    "validation schema": ("validation_schema", "P06", "N03"),
    "validator": ("validator", "P06", "N03"),
    # P07 Evaluation
    "benchmark": ("benchmark", "P07", "N05"),
    "e2e test": ("e2e_eval", "P07", "N05"),
    "integration test": ("e2e_eval", "P07", "N05"),
    "teste integracao": ("e2e_eval", "P07", "N05"),
    "eval dataset": ("eval_dataset", "P07", "N05"),
    "golden test": ("golden_test", "P07", "N05"),
    "llm judge": ("llm_judge", "P07", "N05"),
    "red team": ("red_team_eval", "P07", "N05"),
    "regression": ("regression_check", "P07", "N05"),
    "scoring rubric": ("scoring_rubric", "P07", "N05"),
    "smoke test": ("smoke_eval", "P07", "N05"),
    "trace config": ("trace_config", "P07", "N05"),
    "observability": ("trace_config", "P07", "N05"),
    "unit test": ("unit_eval", "P07", "N05"),
    "teste unitario": ("unit_eval", "P07", "N05"),
    "testes": ("unit_eval", "P07", "N05"),
    "tests": ("unit_eval", "P07", "N05"),
    # P08 Architecture
    "agent card": ("agent_card", "P08", "N03"),
    "component map": ("component_map", "P08", "N03"),
    "decision record": ("decision_record", "P08", "N03"),
    "adr": ("decision_record", "P08", "N03"),
    "diagram": ("diagram", "P08", "N03"),
    "diagrama": ("diagram", "P08", "N03"),
    "invariant": ("invariant", "P08", "N03"),
    "naming rule": ("naming_rule", "P08", "N03"),
    "naming convention": ("naming_rule", "P08", "N03"),
    "pattern": ("pattern", "P08", "N03"),
    "design pattern": ("pattern", "P08", "N03"),
    "supervisor": ("supervisor", "P08", "N03"),
    # P09 Config
    "effort profile": ("effort_profile", "P09", "N03"),
    "env config": ("env_config", "P09", "N05"),
    "environment": ("env_config", "P09", "N05"),
    "feature flag": ("feature_flag", "P09", "N05"),
    "toggle": ("feature_flag", "P09", "N05"),
    "path config": ("path_config", "P09", "N05"),
    "permission": ("permission", "P09", "N05"),
    "access control": ("permission", "P09", "N05"),
    "rate limit": ("rate_limit_config", "P09", "N05"),
    "throttle": ("rate_limit_config", "P09", "N05"),
    "runtime rule": ("runtime_rule", "P09", "N05"),
    "secret config": ("secret_config", "P09", "N05"),
    "credentials": ("secret_config", "P09", "N05"),
    "secrets": ("secret_config", "P09", "N05"),
    # P10 Memory
    "compression config": ("compression_config", "P10", "N04"),
    "entity memory": ("entity_memory", "P10", "N04"),
    "knowledge index": ("knowledge_index", "P10", "N04"),
    "search index": ("knowledge_index", "P10", "N04"),
    "learning record": ("learning_record", "P10", "N04"),
    "memory summary": ("memory_summary", "P10", "N04"),
    "memory type": ("memory_type", "P10", "N04"),
    "prompt cache": ("prompt_cache", "P10", "N05"),
    "cache": ("prompt_cache", "P10", "N05"),
    "runtime state": ("runtime_state", "P10", "N05"),
    "session backend": ("session_backend", "P10", "N05"),
    "session state": ("session_state", "P10", "N05"),
    # P11 Feedback
    "bugloop": ("bugloop", "P11", "N05"),
    "auto fix": ("bugloop", "P11", "N05"),
    "correcao automatica": ("bugloop", "P11", "N05"),
    "monetization": ("content_monetization", "P11", "N06"),
    "monetizacao": ("content_monetization", "P11", "N06"),
    "pricing": ("content_monetization", "P11", "N06"),
    "preco": ("content_monetization", "P11", "N06"),
    "guardrail": ("guardrail", "P11", "N03"),
    "safety": ("guardrail", "P11", "N03"),
    "lifecycle rule": ("lifecycle_rule", "P11", "N03"),
    "optimizer": ("optimizer", "P11", "N05"),
    "quality gate": ("quality_gate", "P11", "N03"),
    "reward signal": ("reward_signal", "P11", "N03"),
    # P12 Orchestration
    "checkpoint": ("checkpoint", "P12", "N03"),
    "dag": ("dag", "P12", "N03"),
    "dependency graph": ("dag", "P12", "N03"),
    "dispatch rule": ("dispatch_rule", "P12", "N03"),
    "handoff": ("handoff", "P12", "N07"),
    "schedule": ("schedule", "P12", "N07"),
    "cron": ("schedule", "P12", "N07"),
    "signal": ("signal", "P12", "N07"),
    "spawn config": ("spawn_config", "P12", "N05"),
    "workflow": ("workflow", "P12", "N03"),
    "workflow primitive": ("workflow_primitive", "P12", "N03"),
}


# ---------------------------------------------------------------------------
# CONVERGENCE T1: per-tenant KIND overlay (additive, FALL-THROUGH)
# ---------------------------------------------------------------------------
#
# Wires the `kinds` axis of the overlay tier (p08_adr_convergence_overlay_tier.md):
# a tenant adds/overrides intent->kind patterns WITHOUT forking this module's
# KIND_PATTERNS. The overlay is a per-tenant artifact resolved through the
# fail-closed cex_tenant_paths guard (surface="overlay"); the base table is
# never mutated.
#
# ZERO-REGRESSION CONTRACT (the bar): when CEX_TENANT_ID is unset OR the tenant
# has no kinds_overlay.yaml, _load_tenant_kind_overlay() returns {} and the
# resolver is BYTE-IDENTICAL to its pre-overlay behaviour -- no cex_tenant_paths
# import is even attempted in the no-tenant path. An overlay only ever ADDS or
# OVERRIDES on top.
#
# PRECEDENCE (resolve order in _exact_match):
#   0. tenant kind overlay  (THIS) -- checked FIRST; on a hit, returns + stops.
#   1. prefix-aware ID classifier  (unchanged)
#   2. KIND_PATTERNS substring match (unchanged)
#   3. kinds_meta token-set match  (unchanged)
# A miss at step 0 falls straight through to the existing logic untouched.
#
# FROZEN GUARD (the moat): an overlay entry whose target kind is in
# _FROZEN_KINDS is REJECTED + logged, never applied. The overlay can extend
# tenant-customizable kinds; it can NEVER re-point the 8F pipeline. This is the
# code form of the ADR's Frozen Invariant ("a tenant overlay can never alter a
# frozen asset").
#
# OVERLAY FILE FORMAT (.cex/tenants/<tid>/overlay/kinds_overlay.yaml):
#   kinds:
#     "<pattern>": ["<kind>", "<pillar>", "<nucleus>"]
#   # e.g.  "patient intake": ["acme_intake_form", "P05", "N03"]
# Same shape as a KIND_PATTERNS entry (a 3-list value). Per the ADR namespacing
# rule, a tenant kind SHOULD be id-prefixed `<tid>_<kind>`; that convention is a
# tenant responsibility -- the only hard guard here is the frozen-set rejection.
#
# DEGRADE-NEVER: a missing/malformed/unreadable overlay -> log + return {} ->
# fall through to global. A bad overlay can never crash this system-wide tool.

# The 8F moat: kinds an overlay must NEVER re-point. These embody 8F-pipeline
# reasoning + the orchestration spine; re-pointing any of them would let a
# tenant overlay how CEX *thinks*, which the ADR freezes byte-identically for
# every tenant. Documented + intentionally small (extend with care -- each
# addition tightens the moat, never loosens it).
_FROZEN_KINDS = frozenset({
    "workflow",            # 8F-as-pipeline contract (F1..F8 step graph)
    "pipeline_template",   # multi-agent pipeline spine (8F orchestration)
    "prompt_compiler",     # F1 CONSTRAIN vocabulary layer (intent->tuple SoT)
    "reasoning_trace",     # F4 REASON evidence record
    "quality_gate",        # F7 GOVERN gate (the quality floor)
    "dispatch_rule",       # F8 COLLABORATE dispatch spine
    "handoff",             # F8 COLLABORATE handoff contract
})

# Truthy set reused from the FT-resolver flag convention below (kept local so
# the overlay block is self-contained and import-order independent).
_OVERLAY_TRUTHY = frozenset({"1", "true", "yes", "on"})

# Per-tenant overlay cache: {tenant_id_or_None: {pattern: (kind, pillar, nuc)}}.
# Keyed by the *resolved* tenant id so two tenants never share a cache row and a
# flag flip at runtime re-reads (the no-tenant key is None -> always {}).
_tenant_kind_overlay_cache: dict[Any, dict[str, tuple[str, str, str]]] = {}


def _coerce_overlay_entry(value: Any) -> tuple[str, str, str] | None:
    """Validate ONE overlay value into a (kind, pillar, nucleus) tuple, or None.

    Accepts a 3-element list/tuple of strings (the KIND_PATTERNS shape) OR a
    dict with kind/pillar/nucleus keys. Anything else -> None (skipped). Pure +
    total: never raises, so a single bad row can't sink the whole overlay.
    """
    if isinstance(value, (list, tuple)) and len(value) == 3:
        k, p, n = value
        if all(isinstance(x, str) and x for x in (k, p, n)):
            return (k, p, n)
        return None
    if isinstance(value, dict):
        k = value.get("kind")
        p = value.get("pillar")
        n = value.get("nucleus")
        if all(isinstance(x, str) and x for x in (k, p, n)):
            return (k, p, n)
    return None


def _parse_overlay_text(text: str) -> dict[str, Any]:
    """Parse overlay YAML text into a raw dict, degrade-never.

    Prefers PyYAML when importable; if absent or the parse fails, returns {} so
    the caller falls through to the global table. The resolver has no hard YAML
    dependency -- a degraded environment must never break intent resolution.
    """
    try:
        import yaml  # optional dep; absence must not break resolution
        data = yaml.safe_load(text)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _load_tenant_kind_overlay(
    tenant_id: str | None = None,
) -> dict[str, tuple[str, str, str]]:
    """Load the active tenant's kind overlay map (cached), or {} (fall-through).

    Returns {pattern -> (kind, pillar, nucleus)} for the bound tenant. Returns
    an EMPTY dict (byte-identical-to-today behaviour) when:
      - CEX_TENANT_ID is unset (single-tenant default) AND no explicit tenant_id;
      - the tenant has no overlay file;
      - the overlay file is malformed/unreadable;
      - cex_tenant_paths cannot be imported (degraded env).

    The FROZEN GUARD runs here: an entry whose kind is in _FROZEN_KINDS is
    dropped with a stderr log -- it never enters the returned map, so it can
    never win at resolve time. Non-canonical kinds are left for the resolver's
    existing canonical-kind guard (a hit still flows through _enforce_canonical_kind).
    """
    # Resolve the effective tenant id WITHOUT importing cex_tenant_paths on the
    # no-tenant path (keeps the default byte-identical + import-free).
    if tenant_id is None:
        raw_tid = os.environ.get("CEX_TENANT_ID")
        if not raw_tid:
            return {}  # single-tenant default: overlay is inert, nothing loaded
    cache_key = tenant_id if tenant_id is not None else os.environ.get("CEX_TENANT_ID")
    if cache_key in _tenant_kind_overlay_cache:
        return _tenant_kind_overlay_cache[cache_key]

    overlay: dict[str, tuple[str, str, str]] = {}
    try:
        tools_dir = str(Path(__file__).resolve().parent)
        if tools_dir not in sys.path:
            sys.path.insert(0, tools_dir)
        import cex_tenant_paths as _tp
        path = _tp.resolve_tenant_path(
            "kinds_overlay.yaml", surface="overlay", tenant_id=tenant_id)
        if path.exists():
            raw = _parse_overlay_text(path.read_text(encoding="utf-8"))
            entries = raw.get("kinds", raw)  # accept top-level 'kinds:' or a bare map
            if isinstance(entries, dict):
                for pattern, value in entries.items():
                    if not isinstance(pattern, str) or not pattern.strip():
                        continue
                    tup = _coerce_overlay_entry(value)
                    if tup is None:
                        continue
                    if tup[0] in _FROZEN_KINDS:
                        # The moat holds: reject + log, never apply.
                        print(
                            "  [intent] overlay REJECTED frozen kind %r for pattern %r "
                            "(8F moat -- overlay cannot re-point a frozen kind)"
                            % (tup[0], pattern),
                            file=sys.stderr)
                        continue
                    overlay[normalize(pattern)] = tup
    except (Exception, SystemExit) as exc:  # degrade-never: ANY failure -> global
        # SystemExit is included deliberately (audit R3): active_tenant_id() ->
        # _safe_tenant_id() raises SystemExit (a BaseException, NOT Exception) on a
        # malformed CEX_TENANT_ID. A bare `except Exception` would let it escape and
        # CRASH the resolver (used by dispatch / 8F / prompt-compiler / N07 CLI)
        # instead of degrading to global resolution. Catch it here so a hostile
        # tenant id (e.g. "../etc/passwd") degrades-never rather than halting.
        print("  [intent] overlay load skipped (%s) -- falling through to global"
              % type(exc).__name__, file=sys.stderr)
        overlay = {}

    _tenant_kind_overlay_cache[cache_key] = overlay
    return overlay


def _match_tenant_overlay(text: str) -> tuple[str, str, str, float] | None:
    """Try the per-tenant kind overlay FIRST (mirrors KIND_PATTERNS matching).

    Returns (kind, pillar, nucleus, confidence) on a hit, else None (fall
    through to the existing resolver logic, unchanged). Longest pattern wins,
    same as the base matcher -- so a tenant override of a more specific
    phrase beats a shorter base pattern.

    R-197: matching goes through `pattern_matches_boundary` (word-boundary +
    length-floor safe) -- the SAME disease (naive `pattern in norm` substring
    matching) affected this loop too, and it is fixed identically here so an
    overlay pattern can never win via a mid-word collision either.
    """
    overlay = _load_tenant_kind_overlay()
    if not overlay:
        return None
    norm = normalize(text)
    for pattern in sorted(overlay.keys(), key=len, reverse=True):
        if pattern_matches_boundary(pattern, norm):
            kind, pillar, nucleus = overlay[pattern]
            ratio = len(pattern) / max(len(norm), 1)
            confidence = min(0.95, 0.70 + ratio * 0.25)
            return kind, pillar, nucleus, confidence
    return None


# ---------------------------------------------------------------------------
# Prefix-aware ID classifier (Bug C fix, 2026-05-02)
# ---------------------------------------------------------------------------
#
# CEX artifact IDs follow conventional prefixes. Substring matching can
# misclassify IDs whose suffix collides with another kind's keyword (e.g.
# `kc_decompose_smoke_test` was mapped to smoke_eval because "smoke_test"
# is a substring). The prefix map is consulted FIRST and only when an ID
# token is detected; pure prose still falls through to substring matching.
#
# PREFIX_MAP maps the FIRST 1-2 underscore-separated segments of an ID
# token to a canonical kind. Tuple value = (kind, pillar, nucleus).
#
# `bld_*` is a special case: the registry has no "builder" kind, so the
# prefix map peels `bld_<iso>_<rest>` and re-resolves the remaining tokens
# (e.g. `bld_architecture_agent` -> kind=agent). See _resolve_id_prefix.

_PREFIX_MAP: dict[str, tuple[str, str, str]] = {
    # Direct kind prefixes (single segment)
    "kc": ("knowledge_card", "P01", "N04"),
    "kind": ("knowledge_card", "P01", "N04"),  # kind library KCs (kind_*.md)
    "agent": ("agent", "P02", "N03"),
    # Multi-segment prefixes (checked before single)
    "agent_card": ("agent_card", "P08", "N03"),
    "system_prompt": ("system_prompt", "P03", "N03"),
    "dispatch_rule": ("dispatch_rule", "P12", "N03"),
    "nucleus_def": ("nucleus_def", "P02", "N03"),
    "component_map": ("component_map", "P08", "N03"),
    "skill": ("skill", "P04", "N03"),
    # Short artifact-ID codes (p0X_<code>_<name> convention)
    "sp": ("system_prompt", "P03", "N03"),
    "ag": ("agent", "P02", "N03"),
    "ac": ("agent_card", "P08", "N03"),
    "cm": ("component_map", "P08", "N03"),
    "nd": ("nucleus_def", "P02", "N03"),
    "dr": ("dispatch_rule", "P12", "N03"),
    "mc": ("model_card", "P02", "N03"),
    "wf": ("workflow", "P12", "N03"),
    "ct": ("crew_template", "P12", "N03"),
    "ra": ("role_assignment", "P02", "N03"),
    "se": ("smoke_eval", "P07", "N05"),
    "ue": ("unit_eval", "P07", "N05"),
    "ee": ("e2e_eval", "P07", "N05"),
    "gt": ("golden_test", "P07", "N05"),
    "bm": ("benchmark", "P07", "N05"),
    "pt": ("prompt_template", "P03", "N03"),
    "rs": ("rag_source", "P01", "N04"),
    "pc": ("prompt_compiler", "P03", "N03"),
}

# Pillar codes (p01..p12) -- used to peel the leading pillar segment from
# IDs like p01_kc_foo and re-resolve from the remainder.
_PILLAR_CODES: frozenset[str] = frozenset(
    "p%02d" % i for i in range(1, 13)
)


def _extract_id_token(text: str) -> str | None:
    """Return the first token that looks like a snake_case ID, else None.

    An ID token contains at least one underscore AND only alphanumerics and
    underscores. Prose words like "create" or "agent" without underscores
    are rejected so they fall through to substring matching.
    """
    norm = text.strip().lower()
    # Strip surrounding punctuation but keep underscores and dots in IDs
    for raw in re.split(r"[\s,;:]+", norm):
        # IDs are alphanumeric + underscore, must contain at least one _
        if "_" in raw and re.fullmatch(r"[a-z0-9_]+", raw):
            # Reject empty / leading-underscore noise
            if raw and not raw.startswith("_") and not raw.endswith("_"):
                return raw
    return None


def _resolve_id_prefix(id_token: str) -> tuple[str, str, str, float] | None:
    """Resolve a snake_case ID via prefix map.

    Returns (kind, pillar, nucleus, confidence) or None.

    Strategy:
      1. Peel a leading p01..p12 pillar code if present (p01_kc_foo -> kc_foo).
      2. Try the FIRST TWO segments as a compound prefix (e.g. "agent_card").
      3. Try the FIRST segment as a single prefix (e.g. "kc").
      4. Special-case "bld_*": peel bld + ISO segment, recurse on remainder
         to find the target kind (e.g. bld_architecture_agent -> agent).
    """
    if not id_token or "_" not in id_token:
        return None

    parts = id_token.split("_")

    # Peel leading pillar code: p01_kc_foo -> kc_foo
    if parts and parts[0] in _PILLAR_CODES and len(parts) >= 2:
        parts = parts[1:]

    if not parts:
        return None

    # Try compound (first two segments) prefix first -- more specific wins
    if len(parts) >= 2:
        compound = parts[0] + "_" + parts[1]
        if compound in _PREFIX_MAP:
            kind, pillar, nucleus = _PREFIX_MAP[compound]
            return kind, pillar, nucleus, 0.92

    # Try single-segment prefix
    head = parts[0]
    if head in _PREFIX_MAP:
        kind, pillar, nucleus = _PREFIX_MAP[head]
        return kind, pillar, nucleus, 0.90

    # Special case: bld_<iso>_<target_kind...> -- peel and recurse.
    # Builder ISOs follow `bld_{iso}_{kind}` (e.g. bld_architecture_agent).
    # The semantic target is the trailing kind; the artifact lives under
    # the agent-builder folder, so we resolve to that kind.
    if head == "bld" and len(parts) >= 3:
        remainder = "_".join(parts[2:])
        # Recurse on remainder as if it were a fresh ID token
        nested = _resolve_id_prefix(remainder)
        if nested:
            kind, pillar, nucleus, _ = nested
            return kind, pillar, nucleus, 0.88
        # Fall back: try the remainder as a literal kind name
        kinds_meta = _load_kinds_meta()
        if remainder in kinds_meta:
            entry = kinds_meta[remainder]
            return (
                remainder,
                entry.get("pillar", "P01"),
                _infer_nucleus(entry),
                0.88,
            )

    return None


# ---------------------------------------------------------------------------
# Kinds meta loader
# ---------------------------------------------------------------------------

_kinds_meta_cache = None


def _load_kinds_meta():
    """Load kinds_meta.json (cached)."""
    global _kinds_meta_cache
    if _kinds_meta_cache is not None:
        return _kinds_meta_cache

    if not KINDS_META_PATH.exists():
        _kinds_meta_cache = {}
        return _kinds_meta_cache

    try:
        raw = KINDS_META_PATH.read_text(encoding="utf-8")
        _kinds_meta_cache = json.loads(raw)
    except Exception:
        _kinds_meta_cache = {}

    return _kinds_meta_cache


# ---------------------------------------------------------------------------
# L0 total-index loader (R-245, 2026-07-03)
# ---------------------------------------------------------------------------
#
# _tools/cex_total_index.py generates a kind-pattern table covering EVERY
# kind in kinds_meta.json (curated KIND_PATTERNS above merged on top, always
# winning on conflict) and writes it to .cex/total_index/l0_patterns.json.
# This loader is the resolver-side half of that wiring: Phase 1 of
# _exact_match reads the MERGED table when it is present, instead of the
# bare 180-entry KIND_PATTERNS dict, using the exact same matcher, ordering,
# and confidence formula -- see _exact_match below.
#
# DEGRADE-NEVER: file absent (never built yet) -> _load_l0_table() returns
# None with NO output at all (an absent file is an expected, ordinary state,
# not a failure -- "no warning noise" per the wiring contract). File present
# but corrupt/unreadable/malformed -> ONE debug-level stderr note (mirrors
# the tenant-kind-overlay fallback convention above) + None returned. Either
# way, _exact_match's Phase 1 falls through to bare KIND_PATTERNS, byte-
# identical to this module's pre-L0 behavior. The 0-token deterministic
# contract is unchanged in both branches.
#
# Cached by (path, mtime): re-parses only when the file's mtime changes (or
# the file disappears), so a hot resolve loop pays the JSON parse once, not
# once per call, while still picking up a same-session rebuild.

_L0_TABLE_PATH = ROOT / ".cex" / "total_index" / "l0_patterns.json"
_l0_cache_key: tuple[str, float] | None = None
_l0_table_cache: dict[str, list] | None = None
_l0_sorted_keys_cache: list[str] | None = None


def _load_l0_table() -> dict[str, list] | None:
    """Return the cached merged L0 pattern table, or None (degrade to bare
    KIND_PATTERNS). See module comment above for the full contract."""
    global _l0_cache_key, _l0_table_cache, _l0_sorted_keys_cache

    if not _L0_TABLE_PATH.exists():
        _l0_cache_key = None
        _l0_table_cache = None
        return None

    try:
        mtime = _L0_TABLE_PATH.stat().st_mtime
    except OSError:
        _l0_cache_key = None
        _l0_table_cache = None
        return None

    cache_key = (str(_L0_TABLE_PATH), mtime)
    if cache_key == _l0_cache_key:
        return _l0_table_cache

    try:
        raw = json.loads(_L0_TABLE_PATH.read_text(encoding="utf-8"))
        patterns = raw.get("patterns") if isinstance(raw, dict) else None
        if not isinstance(patterns, dict) or not patterns:
            raise ValueError("l0_patterns.json has no usable 'patterns' map")
    except Exception as exc:
        print(
            "  [intent] L0 table load skipped (%s) -- falling through to "
            "bare KIND_PATTERNS" % type(exc).__name__, file=sys.stderr)
        _l0_cache_key = cache_key
        _l0_table_cache = None
        return None

    _l0_cache_key = cache_key
    _l0_table_cache = patterns
    _l0_sorted_keys_cache = sorted(patterns.keys(), key=len, reverse=True)
    return patterns


# ---------------------------------------------------------------------------
# Phase 1: Exact match (dict lookup)
# ---------------------------------------------------------------------------

def _resolve_verb(tokens):
    """Extract canonical verb from tokens."""
    for token in tokens:
        if token in VERB_TABLE:
            return VERB_TABLE[token]
    return "create"  # default


def _exact_match(text):
    """Try direct pattern match against KIND_PATTERNS.

    Returns (kind, pillar, nucleus, confidence) or None.

    Resolution order:
     -1. Per-tenant KIND overlay (CONVERGENCE T1). Checked FIRST so a tenant can
         add/override patterns without forking KIND_PATTERNS. INERT (empty map,
         instant fall-through) when CEX_TENANT_ID is unset or no overlay file
         exists -> byte-identical to pre-overlay behaviour. Frozen-kind entries
         are rejected at load time and can never win here.
      0. Prefix-aware ID classification (Bug C fix). If the input contains
         a snake_case ID token (e.g. `kc_foo`, `p03_sp_bar`), try the
         prefix map FIRST so suffix collisions don't misroute. Pure prose
         (no underscores) skips this step.
      1. Multi-word KIND_PATTERNS match, word-boundary safe (R-197: matches
         only whole, contiguous tokens -- see `pattern_matches_boundary`).
         R-245: transparently widened to the generated L0 total-index table
         (curated KIND_PATTERNS pinned on top) when `.cex/total_index/
         l0_patterns.json` exists -- see `_load_l0_table`. Absent/corrupt
         table falls through to bare KIND_PATTERNS, unchanged.
      2. Token-set match against kinds_meta keys (existing fallback).
    """
    # Phase -1: per-tenant kind overlay (additive, fall-through). On a miss this
    # is a no-op and resolution continues exactly as before.
    overlay_hit = _match_tenant_overlay(text)
    if overlay_hit:
        return overlay_hit

    # Phase 0: prefix-aware ID classification
    id_token = _extract_id_token(text)
    if id_token:
        prefix_hit = _resolve_id_prefix(id_token)
        if prefix_hit:
            return prefix_hit

    norm = normalize(text)

    # Try multi-word patterns first (longer = more specific). R-197:
    # word-boundary + length-floor safe -- see pattern_matches_boundary.
    # R-245: when the generated L0 total-index table is present, iterate
    # THAT (curated KIND_PATTERNS merged with the kinds_meta-wide generated
    # layer, curated pinned on conflict) instead of the bare curated dict --
    # same matcher, same longest-first order, same confidence formula.
    # Absent/corrupt table -> identical to pre-L0 behavior (see
    # _load_l0_table). Phases -1, 0 and 2 of this function are untouched.
    l0_table = _load_l0_table()
    if l0_table is not None:
        pattern_table = l0_table
        sorted_patterns = _l0_sorted_keys_cache
    else:
        pattern_table = KIND_PATTERNS
        sorted_patterns = sorted(KIND_PATTERNS.keys(), key=len, reverse=True)
    for pattern in sorted_patterns:
        if pattern_matches_boundary(pattern, norm):
            entry = pattern_table[pattern]
            kind, pillar, nucleus = entry[0], entry[1], entry[2]
            # Confidence based on pattern length vs input length
            ratio = len(pattern) / max(len(norm), 1)
            confidence = min(0.95, 0.70 + ratio * 0.25)
            return kind, pillar, nucleus, confidence

    # Try matching kind names directly from kinds_meta
    kinds_meta = _load_kinds_meta()
    tokens = set(tokenize(text))
    for kind_name in kinds_meta:
        # Match: "agent_card" -> tokens contain "agent" AND "card"
        kind_parts = set(kind_name.replace("_", " ").split())
        if kind_parts and kind_parts.issubset(tokens):
            entry = kinds_meta[kind_name]
            return (
                kind_name,
                entry.get("pillar", "P01"),
                _infer_nucleus(entry),
                0.85,
            )

    return None


def _infer_nucleus(kind_entry):
    """Infer nucleus from kind_entry. The explicit `nucleus` field (R-256 SoT,
    populated per docs/SPEC_R256_NUCLEUS_SOT_2026_07_04.md) wins when present.
    The llm_function map is the historical (pre-R-256) fallback, kept for any
    kind not yet populated -- degrade-never: absent field == byte-identical
    to pre-fix behavior."""
    explicit = kind_entry.get("nucleus")
    if explicit:
        return explicit
    fn = kind_entry.get("llm_function", "")
    fn_to_nucleus = {
        "BECOME": "N03",
        "INJECT": "N03",
        "CALL": "N05",
        "GOVERN": "N05",
        "PRODUCE": "N03",
    }
    return fn_to_nucleus.get(fn, "N03")


# ---------------------------------------------------------------------------
# Phase 2: TF-IDF fallback over kinds_meta descriptions
# ---------------------------------------------------------------------------

def _build_tfidf_index():
    """Build TF-IDF index from kinds_meta descriptions."""
    kinds_meta = _load_kinds_meta()
    if not kinds_meta:
        return [], {}, {}

    docs = []  # list of (kind_name, tokens)
    for kind_name, entry in kinds_meta.items():
        desc = entry.get("description", "")
        boundary = entry.get("boundary", "")
        text = "%s %s %s" % (kind_name.replace("_", " "), desc, boundary)
        tokens = tokenize(text)
        docs.append((kind_name, tokens))

    # Build IDF
    n_docs = len(docs)
    df = Counter()
    for _, tokens in docs:
        df.update(set(tokens))

    idf = {}
    for term, count in df.items():
        idf[term] = math.log(n_docs / (1.0 + count))

    return docs, idf, kinds_meta


def _tfidf_search(query_text, top_k=3):
    """Search kinds_meta using TF-IDF similarity.

    Returns list of (kind, pillar, nucleus, confidence).
    """
    docs, idf, kinds_meta = _build_tfidf_index()
    if not docs:
        return []

    query_tokens = tokenize(query_text)
    if not query_tokens:
        return []

    # Score each document
    results = []
    for kind_name, doc_tokens in docs:
        if not doc_tokens:
            continue

        doc_token_set = set(doc_tokens)
        score = 0.0
        matched = 0

        for qt in query_tokens:
            if qt in doc_token_set:
                score += idf.get(qt, 1.0)
                matched += 1
            else:
                # Partial match (substring)
                for dt in doc_token_set:
                    if len(dt) >= 3 and (qt in dt or dt in qt):
                        score += idf.get(dt, 1.0) * 0.5
                        matched += 0.5
                        break

        if score > 0:
            # Normalize to 0-1 range
            max_possible = sum(idf.get(qt, 1.0) for qt in query_tokens)
            confidence = score / max(max_possible, 0.01)
            confidence = min(confidence, 0.92)  # TF-IDF caps below exact

            entry = kinds_meta.get(kind_name, {})
            results.append((
                kind_name,
                entry.get("pillar", "P01"),
                _infer_nucleus(entry),
                round(confidence, 3),
            ))

    results.sort(key=lambda x: x[3], reverse=True)
    return results[:top_k]


# ---------------------------------------------------------------------------
# Canonical-kind guard (snap-or-fallback, 2026-06-11)
# ---------------------------------------------------------------------------
#
# Root cause fixed the same day: KIND_PATTERNS shipped with 4 kind values
# whose final character had been stripped at authoring time (function_de,
# type_de, enum_de, handof -- exactly the kinds whose canonical name ends
# in "f"). The substring matcher emitted those mutated names verbatim,
# poisoning the FT telemetry corpus with kinds absent from kinds_meta.json.
#
# This guard makes the bug class structurally impossible: ANY non-None kind
# the resolver emits is validated against kinds_meta. A near-miss that is
# the unique lost-final-char truncation of a canonical kind is snapped to
# it; anything else falls back to the documented low-confidence contract
# (kind=None + suggestion "Use LLM for resolution").


def _snap_to_canonical(kind: str) -> str | None:
    """Return a canonical kind for `kind`, or None if it cannot be repaired.

    - `kind` already a kinds_meta key -> returned unchanged.
    - `kind` + exactly ONE trailing char matches exactly one kinds_meta key
      (lost-final-char mutation, e.g. handof -> handoff) -> snapped.
    - otherwise -> None (caller must fall back, never emit the mutant).

    If kinds_meta cannot be loaded (empty registry), validation is
    impossible and the kind passes through unchanged (fail-open so a
    degraded environment never breaks resolution).
    """
    kinds_meta = _load_kinds_meta()
    if not kinds_meta:
        return kind
    if kind in kinds_meta:
        return kind
    completions = [
        k for k in kinds_meta
        if len(k) == len(kind) + 1 and k.startswith(kind)
    ]
    if len(completions) == 1:
        return completions[0]
    return None


def _is_active_overlay_kind(kind: str) -> bool:
    """True iff `kind` is a kind the active tenant's overlay declares.

    A tenant overlay (CONVERGENCE T1) intentionally registers kinds that are
    NOT in the shared kinds_meta -- that is the whole point: a tenant adds a
    vertical kind WITHOUT forking the 306-kind taxonomy. Such a kind is
    legitimate and must NOT be snapped/nuked by the canonical-kind guard. This
    helper is the single exemption seam. It is inert (returns False instantly)
    when no tenant is bound -> the canonical guard is byte-identical to today
    for the single-tenant default. Degrade-never: any failure -> False.
    """
    try:
        overlay = _load_tenant_kind_overlay()
        if not overlay:
            return False
        return any(tup[0] == kind for tup in overlay.values())
    except (Exception, SystemExit):
        # SystemExit included (audit R3): _load_tenant_kind_overlay -> active_tenant_id
        # -> _safe_tenant_id can raise SystemExit on a malformed CEX_TENANT_ID; the
        # canonical-kind guard must degrade (return False) rather than crash.
        return False


def _enforce_canonical_kind(result: dict[str, Any]) -> dict[str, Any]:
    """Final gate: guarantee result["kind"] is a kinds_meta key, a tenant-overlay
    kind, or None.

    Snaps a unique lost-final-char mutation (pillar re-read from the
    registry, nucleus and confidence preserved); otherwise returns the
    documented LLM-fallback shape. A result with kind=None passes through
    untouched. The verb is never altered.

    CONVERGENCE T1 exemption: a kind declared by the ACTIVE tenant's overlay is
    trusted as-is (it is intentionally absent from the shared kinds_meta). The
    exemption is gated on a bound tenant, so the single-tenant default path is
    unchanged -- no overlay, no exemption, byte-identical guard.
    """
    kind = result.get("kind")
    if not kind:
        return result

    # Tenant-overlay kinds are legitimate non-registry kinds: pass through.
    if _is_active_overlay_kind(kind):
        return result

    snapped = _snap_to_canonical(kind)
    if snapped == kind:
        return result

    if snapped is not None:
        entry = _load_kinds_meta().get(snapped, {})
        result["kind"] = snapped
        result["pillar"] = entry.get("pillar", result.get("pillar"))
        return result

    return {
        "kind": None,
        "pillar": None,
        "nucleus": None,
        "verb": result.get("verb", "create"),
        "confidence": 0.0,
        "method": "unknown_kind",
        "suggestion": "Use LLM for resolution",
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _resolve_intent_core(text: str) -> dict[str, Any]:
    """Resolve user intent to {kind, pillar, nucleus, verb, confidence, method}.

    Args:
        text: Natural language input (PT or EN).

    Returns:
        dict with keys: kind, pillar, nucleus, verb, confidence, method.
        If confidence < CONFIDENCE_THRESHOLD, kind will be None.

    Guarantee: a non-None "kind" is ALWAYS a key of kinds_meta.json. The
    canonical-kind guard snaps a unique lost-final-char near-miss to its
    canonical kind; anything else falls back to the documented contract
    (kind=None + suggestion "Use LLM for resolution").
    """
    return _enforce_canonical_kind(_resolve_intent_raw(text))


def _resolve_intent_raw(text: str) -> dict[str, Any]:
    """Unguarded resolution pipeline: exact -> tfidf -> secretariat -> none.

    Internal only -- all callers must go through _resolve_intent_core /
    resolve_intent so the canonical-kind guard always runs (including the
    glue-telemetry logging path).
    """
    if not text or not text.strip():
        return {
            "kind": None,
            "pillar": None,
            "nucleus": None,
            "verb": "create",
            "confidence": 0.0,
            "method": "empty",
            "suggestion": "No input provided",
        }

    tokens = tokenize(text)
    verb = _resolve_verb(tokens)

    # Phase 1: exact match
    exact = _exact_match(text)
    if exact:
        kind, pillar, nucleus, confidence = exact
        return {
            "kind": kind,
            "pillar": pillar,
            "nucleus": nucleus,
            "verb": verb,
            "confidence": round(confidence, 3),
            "method": "exact",
        }

    # Phase 2: TF-IDF fallback
    tfidf_results = _tfidf_search(text, top_k=1)
    if tfidf_results:
        kind, pillar, nucleus, confidence = tfidf_results[0]
        if confidence >= CONFIDENCE_THRESHOLD:
            return {
                "kind": kind,
                "pillar": pillar,
                "nucleus": nucleus,
                "verb": verb,
                "confidence": confidence,
                "method": "tfidf",
            }
        else:
            return {
                "kind": None,
                "pillar": None,
                "nucleus": None,
                "verb": verb,
                "confidence": confidence,
                "method": "tfidf",
                "suggestion": "Use LLM for resolution",
                "best_guess": {
                    "kind": kind,
                    "pillar": pillar,
                    "nucleus": nucleus,
                },
            }

    # Phase 2.5: LLM escalation via secretariat (if available)
    try:
        from cex_secretariat import classify_intent as _sec_classify
        llm_result = _sec_classify(text)
        if llm_result.get("kind") and llm_result.get("escalated"):
            llm_result["method"] = "secretariat_llm"
            return llm_result
    except (ImportError, Exception):
        pass

    # Phase 3: no match at all
    return {
        "kind": None,
        "pillar": None,
        "nucleus": None,
        "verb": verb,
        "confidence": 0.0,
        "method": "none",
        "suggestion": "Use LLM for resolution",
    }


# --- FT glue-brain instrumentation (B1): log every routing decision (fail-open) ---
try:
    from cex_glue_logger import log_glue as _glue_log
except Exception:  # logger absent/broken -> no-op; resolution must never break
    def _glue_log(*_a: Any, **_k: Any) -> None:
        return None


# --- FT carteiro central delegation (CEX_FT_RESOLVER, 2026-06-11) -----------
#
# ONE opt-in env flips EVERY resolve_intent() caller (dispatch.sh ACR,
# cex_8f_runner F1, prompt compiler, N07 CLI -- zero call-site edits) onto the
# carteiro chain (cex_carteiro.resolve: FT step, heuristic floor). Default OFF
# in code: unset/0 keeps this module byte-identical to pre-delegation behavior
# and never imports cex_carteiro.
#
# RECURSION GUARD -- why a thread-local flag and NOT a carteiro core-entry
# rewire: carteiro's heuristic floor calls THIS public resolve_intent (its
# documented contract: "byte-identical to resolve_intent incl. its glue log").
# The threading.local flag marks "a delegation is in flight on this thread",
# so that floor re-entry -- and ANY other resolve_intent call made inside the
# delegated dynamic extent -- is served by the core path. The cycle is ended
# structurally while cex_carteiro stays 100% untouched; a core-entry rewire
# inside carteiro would protect only that one known call site and would
# spread the feature across two modules. threading.local (not a plain bool)
# so one thread's delegation can never suppress another thread's.
#
# FAIL-OPEN: ANY delegation exception (import, resolve, anything) falls
# through to the normal heuristic path below. A route is never broken.
#
# Glue-telemetry truth table (exactly ONE row per resolution, never two):
#   flag OFF (default)            -> this wrapper logs ONE source=heuristic row
#   flag ON, delegation -> FT hit -> NO row today: neither cex_carteiro nor
#                                    cex_ft_eval logs served FT routes (eval
#                                    suppresses logging on purpose). This
#                                    wrapper MUST NOT log the FT result as
#                                    source=heuristic -- that would poison the
#                                    corpus with FT outputs labeled baseline.
#   flag ON, delegation -> floor  -> ONE source=heuristic row, written by the
#                                    floor's own re-entry into this wrapper
#                                    (guard active -> core + log)
#   flag ON, delegation raised    -> ONE source=heuristic row (fallback below)
#   batch loops (cex_glue_backfill, cex_ft_eval) -> call _resolve_intent_core
#                                    directly: never delegated, never logged
#                                    here (backfill writes source=backfill)

_FT_RESOLVER_TRUTHY = frozenset({"1", "true", "yes", "on"})
_delegation_guard = threading.local()


def _ft_resolver_enabled() -> bool:
    """True iff env CEX_FT_RESOLVER is truthy (1|true|yes|on, case-insensitive).

    Read per call (never cached at import) so the flag can be flipped at
    runtime and so test env scrubbing always wins. Unset/empty/0/off -> False.
    """
    return os.environ.get(
        "CEX_FT_RESOLVER", "").strip().lower() in _FT_RESOLVER_TRUTHY


def _delegate_to_carteiro(text: str) -> dict[str, Any]:
    """Route ONE resolution through cex_carteiro.resolve (FT-then-floor).

    Lazy import (flag-off path never pays it) + module-attribute call (so a
    monkeypatched cex_carteiro.resolve is honoured). The _tools dir is added
    to sys.path only if missing, covering package-style importers of this
    module. Exceptions propagate to resolve_intent's fail-open catch.
    """
    tools_dir = str(Path(__file__).resolve().parent)
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    import cex_carteiro
    return cex_carteiro.resolve(text)


def resolve_intent(text: str) -> dict[str, Any]:
    """Public entry: resolve intent + log the carteiro glue training pair.

    Wraps the pure resolver (_resolve_intent_core) so EVERY caller -- CLI and
    importers alike -- self-assimilates one routing pair into the FT corpus.
    The log call is fail-open and never alters the returned result.

    CEX_FT_RESOLVER truthy (opt-in, default OFF): the resolution is delegated
    to cex_carteiro.resolve (FT step + heuristic floor) so the FT carteiro
    fires on every artery without call-site changes. The thread-local guard
    keeps carteiro's floor on the core path (no recursion); any delegation
    failure falls open to the heuristic path. See the truth table above for
    who logs what per path (never two rows for one resolution).
    """
    if _ft_resolver_enabled() and not getattr(_delegation_guard, "active", False):
        _delegation_guard.active = True
        try:
            return _delegate_to_carteiro(text)
        except Exception:
            pass  # fail-open: ANY delegation failure -> heuristic path below
        finally:
            _delegation_guard.active = False
    result = _resolve_intent_core(text)
    _glue_log(
        "carteiro",
        {"intent": text},
        result,
        source="heuristic",
        confidence=result.get("confidence") if isinstance(result, dict) else None,
    )
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def resolve_intent_verbose(text: str) -> dict[str, Any]:
    """Verbose wrapper -- prints resolution trace to stderr."""
    tokens = tokenize(text)
    verb = _resolve_verb(tokens)
    print("  [intent] Input:  %s" % text, file=sys.stderr)
    print("  [intent] Tokens: %s" % tokens, file=sys.stderr)
    print("  [intent] Verb:   %s" % verb, file=sys.stderr)

    exact = _exact_match(text)
    if exact:
        kind, pillar, nucleus, confidence = exact
        print("  [intent] Exact match: %s (P=%s, N=%s, conf=%.0f%%)" % (
            kind, pillar, nucleus, confidence * 100), file=sys.stderr)
        return resolve_intent(text)

    print("  [intent] No exact match, trying TF-IDF...", file=sys.stderr)
    tfidf_results = _tfidf_search(text, top_k=3)
    if tfidf_results:
        for k, p, n, c in tfidf_results:
            print("  [intent] TF-IDF: %-22s P=%-4s N=%-3s conf=%.0f%%" % (
                k, p, n, c * 100), file=sys.stderr)
    else:
        print("  [intent] TF-IDF: no matches", file=sys.stderr)

    return resolve_intent(text)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CEX Intent Resolver -- Python-first kind resolution (0 LLM tokens)"
    )
    parser.add_argument("query", nargs="?", help="Natural language intent")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON (default for pipe)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show resolution trace on stderr")
    parser.add_argument("--batch", metavar="FILE",
                        help="Resolve intents from file (one per line)")
    parser.add_argument("--threshold", type=float, default=CONFIDENCE_THRESHOLD,
                        help="Confidence threshold (default: %.2f)" % CONFIDENCE_THRESHOLD)
    parser.add_argument("--test", action="store_true",
                        help="Run built-in self-test suite")
    args = parser.parse_args()

    # Self-test mode
    if args.test:
        print("=== CEX Intent Resolver Self-Test ===\n")
        cases = [
            ("criar um agente de pesquisa", "agent", 0.6),
            ("create agent", "agent", 0.6),
            ("MCP server para Supabase", "mcp_server", 0.6),
            ("webhook endpoint", "webhook", 0.6),
            ("landing page para meu produto", "landing_page", 0.6),
            ("configurar RAG", "rag_source", 0.6),
            ("benchmark de performance", "benchmark", 0.6),
            ("pricing strategy", "content_monetization", 0.6),
            ("system prompt do agente", "system_prompt", 0.6),
            ("quality gate", "quality_gate", 0.6),
            ("red team eval", "red_team_eval", 0.6),
            ("unit test", "unit_eval", 0.6),
            ("guardrail de seguranca", "guardrail", 0.6),
            ("workflow de deploy", "workflow", 0.6),
            ("glossario de termos", "glossary_entry", 0.6),
        ]
        passed = 0
        for user_input, expected_kind, min_conf in cases:
            result = resolve_intent(user_input)
            ok = (result.get("kind") == expected_kind
                  and result.get("confidence", 0) >= min_conf)
            tag = "[OK]" if ok else "[FAIL]"
            if ok:
                passed += 1
            print("  %s %-40s -> %-22s conf=%.0f%% method=%s" % (
                tag, '"%s"' % user_input[:36],
                result.get("kind") or "(none)",
                result.get("confidence", 0) * 100,
                result.get("method", "?"),
            ))
        print("\n  %d/%d passed" % (passed, len(cases)))
        sys.exit(0 if passed == len(cases) else 1)

    resolver = resolve_intent_verbose if args.verbose else resolve_intent

    # Batch mode
    if args.batch:
        batch_path = Path(args.batch)
        if not batch_path.exists():
            print("File not found: %s" % args.batch, file=sys.stderr)
            sys.exit(2)
        lines = [l.strip() for l in batch_path.read_text(encoding="utf-8").splitlines()
                 if l.strip() and not l.strip().startswith("#")]
        results = []
        resolved = 0
        for line in lines:
            r = resolver(line)
            r["input"] = line
            results.append(r)
            if r.get("kind"):
                resolved += 1
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            for r in results:
                tag = "[OK]" if r.get("kind") else "[??]"
                print("  %s %-35s -> %-20s %s %s (%.0f%% %s)" % (
                    tag, r["input"][:35],
                    r.get("kind") or "?",
                    r.get("pillar") or "?",
                    r.get("nucleus") or "?",
                    r["confidence"] * 100,
                    r["method"],
                ))
            print("\n  Resolved: %d/%d (%.0f%%)" % (
                resolved, len(lines),
                100 * resolved / max(1, len(lines))))
        sys.exit(0 if resolved == len(lines) else 1)

    # Single query
    if not args.query:
        parser.print_help()
        sys.exit(2)

    result = resolver(args.query)

    if args.json or not sys.stdout.isatty():
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print()
        if result["kind"]:
            print("  [OK] Resolved (method: %s, confidence: %.0f%%)" % (
                result["method"], result["confidence"] * 100))
            print("  kind:    %s" % result["kind"])
            print("  pillar:  %s" % result["pillar"])
            print("  nucleus: %s" % result["nucleus"])
            print("  verb:    %s" % result["verb"])
        else:
            print("  [--] Low confidence (%.0f%%) -- LLM fallback recommended" % (
                result["confidence"] * 100))
            print("  method:  %s" % result["method"])
            print("  verb:    %s" % result["verb"])
            if "best_guess" in result:
                bg = result["best_guess"]
                print("  guess:   %s (%s, %s)" % (
                    bg["kind"], bg["pillar"], bg["nucleus"]))
        print()

    sys.exit(0 if result["kind"] else 1)


if __name__ == "__main__":
    try:
        from cex_agent_io import wrap_main

        def _main_wrapper(argv):
            sys.argv = [sys.argv[0]] + argv
            main()
            return 0

        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_intent_resolver"))
    except ImportError:
        main()
