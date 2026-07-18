#!/usr/bin/env python3
"""cex_ollama_env.py: ONE canonical resolver for the Ollama base URL.

Register rows R-056 + R-141 (docs/IMPROVEMENT_REGISTER.md): before this module
the repo read the SAME daemon's base URL from 4+ different env vars
(OLLAMA_HOST, OLLAMA_URL, CEX_OLLAMA_HOST, CEX_CARTEIRO_OLLAMA_HOST) plus six
hardcoded module constants that read no env at all. This module is the single
seam: every in-repo reader resolves through resolve_ollama_host().

Canonical env var: OLLAMA_HOST
  - the MAJORITY reader in live code at unification time (4 readers:
    cex_ollama.py, cex_structural_validator_daemon.py, cex_chaos_ollama.py,
    cexai ollama_provider.py -- vs 1 each for every alias);
  - ollama's own upstream convention;
  - already what deploy/helm/cexai (values.yaml + configmap) and the
    _bundles .mcp.json set.

Precedence (first non-empty wins; the canonical ALWAYS wins):
  1. OLLAMA_HOST                     canonical
  2. caller extra_aliases, in order  tool-scoped legacy names (e.g. the
                                     carteiro's CEX_CARTEIRO_OLLAMA_HOST) --
                                     consulted before the generic aliases so
                                     per-tool intent survives when the
                                     canonical is absent
  3. OLLAMA_URL                      legacy alias (cex_sdk convention)
  4. CEX_OLLAMA_HOST                 legacy alias (cex_embedder convention)
  5. the caller's default            degrade-never: with no env set, behavior
                                     is byte-identical to pre-unification

Legacy aliases keep working; using one emits a single deprecation warning per
process per alias, on STDERR only (stdout stays clean for JSON-emitting tools).

Deliberately NOT an alias: OLLAMA_API_BASE. That is the aider/LiteLLM child
convention exported by _spawn/*.sh, which now DERIVE it from OLLAMA_HOST
instead of the reverse. Also unchanged: the YAML config lane
(.cex/config/nucleus_models.yaml ollama_api.base_url, read by
cex_model_resolver.get_ollama_config) is config-not-env and stays separate.

Normalization matches the pre-existing cex_chaos_ollama idiom (the only alias
chain in the repo before this module): a bare host:port is upgraded to
http://, trailing slashes are trimmed.
"""
from __future__ import annotations

import os
import sys

CANONICAL_ENV = "OLLAMA_HOST"
LEGACY_ALIASES = ("OLLAMA_URL", "CEX_OLLAMA_HOST")
DEFAULT_HOST = "http://localhost:11434"

_warned_aliases: set = set()


def _normalize(url: str) -> str:
    """Upgrade a bare host:port to http:// and trim trailing slashes."""
    url = url.strip()
    if url and "://" not in url:
        url = "http://" + url
    return url.rstrip("/")


def _warn_once(alias: str) -> None:
    """One deprecation line per process per alias, stderr only."""
    if alias in _warned_aliases:
        return
    _warned_aliases.add(alias)
    sys.stderr.write(
        f"[WARN] Ollama base URL read from legacy alias {alias}; "
        f"set {CANONICAL_ENV} instead (canonical, R-056/R-141).\n")


def resolve_ollama_host(default: str = DEFAULT_HOST,
                        extra_aliases: tuple = ()) -> str:
    """Resolve the Ollama daemon base URL (module docstring has the precedence).

    default: returned when no env var is set. Callers pass their
        pre-unification default so absent-all-vars behavior never changes.
    extra_aliases: tool-scoped legacy env names, consulted after the canonical
        but before the generic legacy aliases.
    """
    val = os.environ.get(CANONICAL_ENV, "").strip()
    if val:
        return _normalize(val)
    for alias in tuple(extra_aliases) + LEGACY_ALIASES:
        val = os.environ.get(alias, "").strip()
        if val:
            _warn_once(alias)
            return _normalize(val)
    return _normalize(default) if default else default
