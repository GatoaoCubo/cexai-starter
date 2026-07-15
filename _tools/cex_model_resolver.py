"""
cex_model_resolver.py -- Runtime model resolution from nucleus_models.yaml.

Provides a single source of truth for model strings across all Python tools.
Replaces hardcoded model references (47 instances across 23 files).

Usage:
    from _tools.cex_model_resolver import resolve_model, get_preflight_model
    cfg = resolve_model("n03")
    # cfg = {"cli": "claude", "model": "claude-opus-4-8", "context": 1000000, ...}

    haiku = get_preflight_model("cloud")
    # haiku = {"cli": "claude", "model": "claude-haiku-4-5-20251001", ...}

    tool_model = resolve_model_for_tool("cex_intent", task_tier="light")
    # tool_model = {"cli": "claude", "model": "claude-haiku-4-5-20251001", ...}

Design:
    - Reads .cex/config/nucleus_models.yaml ONCE per process (cached).
    - Auto-detects CEX_ROOT from env var or git rev-parse.
    - Graceful fallback on any error -- never crashes.
    - ASCII-only per .claude/rules/ascii-code-rule.md.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Module-level cache (one YAML parse per process)
# ---------------------------------------------------------------------------

_CACHE = {
    "config": None,
    "cex_root": None,
    "loaded": False,
    "aliases": None,
    "aliases_loaded": False,
    "discovery": None,
    "discovery_loaded": False,
}

# ---------------------------------------------------------------------------
# Dynamic model alias resolution (plan: opus_latest_dynamic)
# ---------------------------------------------------------------------------
# The single baked-in baseline. This is the ONE place a default Opus version
# is allowed to live in the Python resolver (DP4 last-resort safety net so boot
# never hard-fails). cex_model_updater.py --propagate refreshes it when a newer
# Opus ships. Everything else resolves through the model_aliases: YAML block.
_BASELINE_OPUS = "claude-opus-4-8"

# Shorthand (as written in each nucleus block, e.g. "model: opus") -> the alias
# KEY in .cex/config/nucleus_models.yaml::model_aliases. The resolver reads the
# actual version string from that YAML block (DP5: 7 families), so this map only
# needs to know the key, never the version -- that is what kills the hardcode.
_SHORTHAND_TO_ALIAS = {
    "fable": "fable_latest",
    "opus": "opus_latest",
    "sonnet": "sonnet_latest",
    "haiku": "haiku_latest",
    "gemini_pro": "gemini_pro_latest",
    "gemini_flash": "gemini_flash_latest",
    "gemini_flash_lite": "gemini_flash_lite_latest",
    "gpt": "gpt_latest",
    "gpt_mini": "gpt_mini_latest",
}

# Last-resort alias values, used ONLY when the YAML model_aliases: block is
# missing/unparseable AND no fresh discovery cache exists (DP4 deepest net).
# opus intentionally points at the single _BASELINE_OPUS const above.
_FALLBACK_ALIASES = {
    "fable_latest": "claude-fable-5",
    "opus_latest": _BASELINE_OPUS,
    "sonnet_latest": "claude-sonnet-4-6",
    "haiku_latest": "claude-haiku-4-5-20251001",
    "gemini_pro_latest": "gemini-2.5-pro",
    "gemini_flash_latest": "gemini-2.5-flash",
    "gemini_flash_lite_latest": "gemini-2.5-flash-lite",
    "gpt_latest": "gpt-5.2",
    "gpt_mini_latest": "gpt-5-mini",
}

# DP1 discovery cache (READ side only; the background probe that WRITES it is
# N05's job). Fresh (<24h) values OVERRIDE the YAML alias block. Pure file read
# + timestamp compare: NO network call, never blocks boot.
_DISCOVERY_CACHE_REL = (".cex", "cache", "model_discovery.json")
_DISCOVERY_TTL_SECONDS = 24 * 3600

# ---------------------------------------------------------------------------
# FABLE_SELF_HEAL: availability-aware fable -> opus substitution
# ---------------------------------------------------------------------------
# claude-fable-5 can be server-blocked per-account by Anthropic. The block lives
# in the user's CLI config (~/.claude.json) under
#   cachedGrowthBookFeatures.tengu-model-error-overrides
# as a `claude-fable-5` key (a block object: "Claude Fable 5 is currently
# unavailable..."). Booting a blocked model crashes the CLI at launch, so when a
# `model: fable` intent resolves to claude-fable-5 we substitute opus WHILE the
# block is present and snap straight back to fable the instant Anthropic clears
# the key -- no manual revert. Mirrors boot/_shared/resolve_model.ps1 byte-for-
# byte in DECISION (same gate, same fable->opus result).
_FABLE_MODEL_ID = "claude-fable-5"
_FABLE_OVERRIDE_GROUP = "cachedGrowthBookFeatures"
_FABLE_OVERRIDE_KEY = "tengu-model-error-overrides"
# CEX_FABLE_GATE overrides the gate file location (test seam + escape hatch);
# default is the user's ~/.claude.json (Windows: %USERPROFILE%\.claude.json).
_FABLE_GATE_ENV = "CEX_FABLE_GATE"
# CEX_FABLE_FORCE (truthy) skips the block check and uses fable as-is.
_FABLE_FORCE_ENV = "CEX_FABLE_FORCE"
_TRUTHY = ("1", "true", "yes", "on")

# Emit the "fable blocked -> opus" stderr note at most once per process.
_FABLE_NOTE_EMITTED = False

# Default fallback when YAML is missing or unparseable
_DEFAULT_NUCLEUS = {
    "cli": "claude",
    "model": _BASELINE_OPUS,
    "context": 1000000,
    "flags": "",
    "mcps": "",
    "settings": "",
    "fallback_chain": [],
}

_DEFAULT_PREFLIGHT_LOCAL = {
    "cli": "ollama",
    "model": "qwen3:14b",
    "base_url": "http://localhost:11434/v1",
    "timeout_seconds": 30,
}

_DEFAULT_PREFLIGHT_CLOUD = {
    "cli": "claude",
    "model": "claude-haiku-4-5-20251001",
}

_DEFAULT_OLLAMA = {
    "base_url": "http://localhost:11434/v1",
    "embed_url": "http://localhost:11434/api/embed",
    "models": {
        "primary": "gemma4:26b",
        "heavy": "qwen3:14b",
        "light": "qwen3:8b",
        "student": "cex-student",
    },
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _find_cex_root(cex_root=None):
    """Resolve CEX repository root directory.

    Priority:
    1. Explicit cex_root argument
    2. CEX_ROOT environment variable
    3. git rev-parse --show-toplevel
    4. Walk up from this file's location looking for .cex/ directory
    """
    if cex_root:
        return str(Path(cex_root).resolve())

    env_root = os.environ.get("CEX_ROOT")
    if env_root and os.path.isdir(env_root):
        return str(Path(env_root).resolve())

    # Try git rev-parse
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        if result.returncode == 0 and result.stdout.strip():
            return str(Path(result.stdout.strip()).resolve())
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    # Walk up from this file looking for .cex/ directory
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / ".cex").is_dir():
            return str(current)
        parent = current.parent
        if parent == current:
            break
        current = parent

    return ""


def _load_yaml(cex_root=None):
    """Load nucleus_models.yaml, caching the result."""
    if _CACHE["loaded"]:
        return _CACHE["config"] or {}

    if yaml is None:
        # pyyaml not available -- return empty, functions use defaults
        _CACHE["loaded"] = True
        _CACHE["config"] = {}
        return {}

    root = _find_cex_root(cex_root)
    if not root:
        _CACHE["loaded"] = True
        _CACHE["config"] = {}
        return {}

    _CACHE["cex_root"] = root
    yaml_path = os.path.join(root, ".cex", "config", "nucleus_models.yaml")

    if not os.path.isfile(yaml_path):
        _CACHE["loaded"] = True
        _CACHE["config"] = {}
        return {}

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        _CACHE["config"] = data if isinstance(data, dict) else {}
    except Exception:
        _CACHE["config"] = {}

    _CACHE["loaded"] = True
    return _CACHE["config"] or {}


def _invalidate_cache():
    """Force re-read on next call. Useful for tests."""
    global _FABLE_NOTE_EMITTED
    _CACHE["config"] = None
    _CACHE["cex_root"] = None
    _CACHE["loaded"] = False
    _CACHE["aliases"] = None
    _CACHE["aliases_loaded"] = False
    _CACHE["discovery"] = None
    _CACHE["discovery_loaded"] = False
    _FABLE_NOTE_EMITTED = False


def _iso_age_seconds(iso_str):
    """Return seconds between now (UTC) and an ISO-8601 timestamp.

    Returns +inf on any parse failure so a malformed timestamp is treated as
    stale (-> the resolver falls back to the YAML alias block). Never raises.
    """
    try:
        ts = str(iso_str).strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).total_seconds()
    except Exception:
        return float("inf")


def _load_discovery_cache(cex_root=None):
    """Read .cex/cache/model_discovery.json if fresh (<24h). Cached per process.

    DP1 READ side: returns {alias_key: model_id} from the last successful
    background probe, but ONLY if its `_fetched` timestamp is < 24h old.
    Returns {} on missing / stale / unparseable. Pure file read + timestamp
    compare -- NO network call, never blocks boot, never raises.
    """
    if _CACHE["discovery_loaded"]:
        return _CACHE["discovery"] or {}

    result = {}
    try:
        root = _find_cex_root(cex_root)
        if root:
            path = os.path.join(root, *_DISCOVERY_CACHE_REL)
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    fetched = data.get("_fetched")
                    if fetched and _iso_age_seconds(fetched) < _DISCOVERY_TTL_SECONDS:
                        result = {
                            k: v for k, v in data.items()
                            if not k.startswith("_") and isinstance(v, str) and v.strip()
                        }
    except Exception:
        result = {}

    _CACHE["discovery"] = result
    _CACHE["discovery_loaded"] = True
    return result


def _alias_map(cex_root=None):
    """Return the resolved alias map {alias_key: model_id}. Cached per process.

    Precedence per alias key (low -> high):
      1. baked-in _FALLBACK_ALIASES (always present; DP4 net)
      2. .cex/config/nucleus_models.yaml::model_aliases (machine source of truth)
      3. .cex/cache/model_discovery.json fresh values (DP1; OVERRIDE the YAML)

    No network call. Never raises -- any failure degrades to the layer below.
    """
    if _CACHE["aliases_loaded"]:
        return _CACHE["aliases"] or {}

    merged = dict(_FALLBACK_ALIASES)

    # Layer 2: YAML model_aliases: block
    try:
        config = _load_yaml(cex_root)
        yaml_aliases = config.get("model_aliases", {}) if isinstance(config, dict) else {}
        if isinstance(yaml_aliases, dict):
            for key, val in yaml_aliases.items():
                if isinstance(val, str) and val.strip():
                    merged[key] = val.strip()
    except Exception:
        pass

    # Layer 3: fresh discovery cache OVERRIDES the YAML alias block (DP1)
    try:
        for key, val in _load_discovery_cache(cex_root).items():
            merged[key] = val
    except Exception:
        pass

    _CACHE["aliases"] = merged
    _CACHE["aliases_loaded"] = True
    return merged


def _env_truthy(name):
    """True iff env var `name` is set to a truthy token (1/true/yes/on)."""
    return os.environ.get(name, "").strip().lower() in _TRUTHY


def _fable_gate_path():
    """Path to the availability gate. CEX_FABLE_GATE override else ~/.claude.json."""
    override = os.environ.get(_FABLE_GATE_ENV, "").strip()
    if override:
        return override
    return os.path.join(os.path.expanduser("~"), ".claude.json")


def _fable_blocked():
    """Return True iff claude-fable-5 is server-blocked for this account.

    Reads the user's ~/.claude.json and tests whether Anthropic injected a
    `claude-fable-5` key under cachedGrowthBookFeatures.tengu-model-error-overrides.

    Self-heal contract:
      - key PRESENT  -> True  (blocked  -> caller substitutes opus)
      - key ABSENT   -> False (available -> caller keeps fable; auto snap-back)
      - file missing / unreadable / unparseable
                     -> True  (FAIL-SAFE: never boot a model we cannot confirm
                               serveable; a blocked fable crashes boot)

    No network call. Never raises. Mirrors resolve_model.ps1::Test-CexFableBlocked.
    """
    try:
        with open(_fable_gate_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return True  # FAIL-SAFE: missing / unreadable / unparseable -> blocked
    try:
        group = data.get(_FABLE_OVERRIDE_GROUP) if isinstance(data, dict) else None
        overrides = group.get(_FABLE_OVERRIDE_KEY) if isinstance(group, dict) else None
        if isinstance(overrides, dict):
            return _FABLE_MODEL_ID in overrides
        return False  # gate readable, no override block recorded -> AVAILABLE
    except Exception:
        return True  # any structural surprise -> FAIL-SAFE blocked


def _emit_fable_note_once():
    """Write the fable->opus substitution note to stderr at most once per process."""
    global _FABLE_NOTE_EMITTED
    if _FABLE_NOTE_EMITTED:
        return
    _FABLE_NOTE_EMITTED = True
    try:
        sys.stderr.write(
            "[i] claude-fable-5 server-blocked -> resolving opus "
            "(set CEX_FABLE_FORCE=1 to force fable).\n"
        )
    except Exception:
        pass


def _heal_fable(resolved, cex_root=None):
    """Substitute opus for claude-fable-5 WHILE it is server-blocked.

    Triggers ONLY when `resolved` is the fable target -- opus/sonnet/haiku/etc.
    pass through byte-identical (zero behavior change for non-fable models).
    CEX_FABLE_FORCE bypasses the check. The opus substitution reuses the opus
    resolution path so CEX_OPUS_TIER / discovery-cache precedence is preserved.
    """
    if resolved != _FABLE_MODEL_ID:
        return resolved
    if _env_truthy(_FABLE_FORCE_ENV):
        return resolved  # escape hatch: force fable (test the day it returns)
    if _fable_blocked():
        _emit_fable_note_once()
        return resolve_shorthand("opus", cex_root)
    return resolved


def resolve_shorthand(name, cex_root=None):
    """Expand a model shorthand to a full model id, or pass a literal through.

    - "opus"/"sonnet"/"haiku"/"gemini_pro"/"gemini_flash"/"gpt"/"gpt_mini"
      resolve through the alias map (cache > YAML > baseline).
    - For the opus family ONLY, $CEX_OPUS_TIER pins the version when set to a
      literal model id (rollback path, DP2); "latest"/unset follows the alias.
    - "fable" resolves to claude-fable-5 ONLY while it is serveable; while
      Anthropic server-blocks it (FABLE_SELF_HEAL) it substitutes opus and snaps
      back automatically when the block clears. See _heal_fable / _fable_blocked.
    - Any value that is not a known shorthand is already a literal model id and
      is returned unchanged (a literal claude-fable-5 is still self-healed).

    This is the canonical expansion shared by every Python caller (and imported
    by cex_boot_pipeline.py) so the shorthand is resolved in exactly ONE place.
    """
    if not isinstance(name, str) or not name.strip():
        return _BASELINE_OPUS
    key = name.strip()

    alias_key = _SHORTHAND_TO_ALIAS.get(key)
    if alias_key is None:
        # Already a literal model id. Pass through -- but still self-heal a literal
        # claude-fable-5 (e.g. router- or override-supplied) so a direct fable id
        # cannot boot a blocked model.
        return _heal_fable(key, cex_root)

    # CEX_OPUS_TIER pin applies to the opus family only (env name says "opus").
    if alias_key == "opus_latest":
        tier = os.environ.get("CEX_OPUS_TIER", "").strip()
        if tier and tier.lower() != "latest":
            return tier  # explicit pin to a literal version (rollback)

    resolved = _alias_map(cex_root).get(alias_key, _BASELINE_OPUS)
    # FABLE_SELF_HEAL: opus while claude-fable-5 is server-blocked, fable when clear.
    return _heal_fable(resolved, cex_root)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_nucleus_models(cex_root=None):
    """Load and return the full nucleus_models.yaml as a dict.

    Auto-detects cex_root from CEX_ROOT env var or git root.
    Caches the result for the process lifetime (module-level cache).
    Returns {} on any error (graceful fallback).
    """
    return dict(_load_yaml(cex_root))


def resolve_model(nucleus, cex_root=None):
    """Return model config for a nucleus as a dict.

    Args:
        nucleus: Nucleus identifier (e.g. "n03", "n07")
        cex_root: Optional explicit path to CEX repo root

    Returns:
        Dict with keys: cli, model, context, flags, mcps, settings, fallback_chain
        Falls back to the baseline opus alias / 1M context if missing.
    """
    config = _load_yaml(cex_root)
    nuc_key = nucleus.lower().strip()
    nuc_cfg = config.get(nuc_key, {})

    if not nuc_cfg or not isinstance(nuc_cfg, dict):
        return dict(_DEFAULT_NUCLEUS)

    # Check for orchestrator override via env var
    override = os.environ.get("CEX_MODEL_OVERRIDE")
    if override:
        cli = "claude"
        if override.startswith("gemini"):
            cli = "gemini"
        elif override.startswith("gpt"):
            cli = "codex"
        elif any(override.startswith(p) for p in ("llama", "qwen", "gemma", "phi")):
            cli = "ollama"
        return {
            "cli": cli,
            "model": override,
            "context": nuc_cfg.get("context", 1000000),
            "flags": nuc_cfg.get("flags", ""),
            "mcps": nuc_cfg.get("mcps", ""),
            "settings": nuc_cfg.get("settings", ""),
            "fallback_chain": nuc_cfg.get("fallback_chain", []),
        }

    model_raw = nuc_cfg.get("model", "opus")
    model = resolve_shorthand(model_raw, cex_root)

    return {
        "cli": nuc_cfg.get("cli", "claude"),
        "model": model,
        "context": nuc_cfg.get("context", 1000000),
        "flags": nuc_cfg.get("flags", ""),
        "mcps": nuc_cfg.get("mcps", ""),
        "settings": nuc_cfg.get("settings", ""),
        "fallback_chain": nuc_cfg.get("fallback_chain", []),
    }


def get_preflight_model(phase="local", cex_root=None):
    """Return model config for preflight phase.

    Args:
        phase: "local" for Ollama-based preflight, "cloud" for Haiku-based
        cex_root: Optional explicit path to CEX repo root

    Returns:
        Dict with cli, model, and phase-specific fields.
        Falls back gracefully if config missing.
    """
    config = _load_yaml(cex_root)
    preflight = config.get("preflight", {})

    if phase == "local":
        local_cfg = preflight.get("local", {})
        if not local_cfg:
            return dict(_DEFAULT_PREFLIGHT_LOCAL)
        return {
            "cli": local_cfg.get("cli", "ollama"),
            "model": local_cfg.get("model", "qwen3:14b"),
            "fallback_model": local_cfg.get("fallback_model", "qwen3:8b"),
            "base_url": local_cfg.get("base_url", "http://localhost:11434/v1"),
            "timeout_seconds": local_cfg.get("timeout_seconds", 30),
            "tasks": local_cfg.get("tasks", []),
        }

    elif phase == "cloud":
        cloud_cfg = preflight.get("cloud", {})
        if not cloud_cfg:
            return dict(_DEFAULT_PREFLIGHT_CLOUD)
        return {
            "cli": cloud_cfg.get("cli", "claude"),
            "model": cloud_cfg.get("model", "claude-haiku-4-5-20251001"),
            "tasks": cloud_cfg.get("tasks", []),
        }

    # Unknown phase -- return cloud default
    return dict(_DEFAULT_PREFLIGHT_CLOUD)


def get_ollama_config(cex_root=None):
    """Return ollama_api section from nucleus_models.yaml.

    Returns:
        Dict with keys: base_url, embed_url, models (primary/heavy/light),
        plus gpu, vram, parallel if present.
        Falls back gracefully if missing.
    """
    config = _load_yaml(cex_root)
    ollama_cfg = config.get("ollama_api", {})

    if not ollama_cfg:
        return dict(_DEFAULT_OLLAMA)

    models = ollama_cfg.get("models", {})
    return {
        "base_url": ollama_cfg.get("base_url", "http://localhost:11434/v1"),
        "embed_url": ollama_cfg.get("embed_url", "http://localhost:11434/api/embed"),
        "models": {
            "primary": models.get("primary", "gemma4:26b"),
            "heavy": models.get("heavy", "qwen3:14b"),
            "light": models.get("light", "qwen3:8b"),
            "student": models.get("student", "cex-student"),
        },
        "gpu": ollama_cfg.get("gpu", ""),
        "vram": ollama_cfg.get("vram", ""),
        "parallel": ollama_cfg.get("parallel", 1),
    }


def get_fallback_chain(nucleus, cex_root=None):
    """Return the ordered fallback_chain list for a nucleus.

    Args:
        nucleus: Nucleus identifier (e.g. "n03")
        cex_root: Optional explicit path to CEX repo root

    Returns:
        List of dicts, each with keys: cli, model, flags.
        Empty list if no fallback chain configured.
    """
    config = _load_yaml(cex_root)
    nuc_key = nucleus.lower().strip()
    nuc_cfg = config.get(nuc_key, {})

    if not nuc_cfg or not isinstance(nuc_cfg, dict):
        return []

    chain = nuc_cfg.get("fallback_chain", [])
    if not isinstance(chain, list):
        return []

    # Normalize entries to ensure consistent keys
    result = []
    for entry in chain:
        if isinstance(entry, dict):
            result.append({
                "cli": entry.get("cli", "claude"),
                "model": entry.get("model", ""),
                "flags": entry.get("flags", ""),
            })
    return result


def resolve_model_for_tool(tool_name, task_tier="standard", cex_root=None):
    """Resolve model config for a Python tool based on its task tier.

    This replaces hardcoded model strings in tools like cex_intent.py,
    cex_translate.py, cex_fts5_search.py, etc.

    Args:
        tool_name: Name of the calling tool (for logging/audit, not routing)
        task_tier: One of "light", "standard", "heavy"
            - "light"    -> preflight cloud model (haiku -- cheap, fast)
            - "standard" -> N03's model (engineering tier)
            - "heavy"    -> N07's model (opus tier, max reasoning)

    Returns:
        Dict with keys: cli, model, context (minimum viable fields for tool use)
    """
    if task_tier == "light":
        cfg = get_preflight_model("cloud", cex_root=cex_root)
        return {
            "cli": cfg.get("cli", "claude"),
            "model": cfg.get("model", "claude-haiku-4-5-20251001"),
            "context": 200000,
        }

    elif task_tier == "heavy":
        cfg = resolve_model("n07", cex_root=cex_root)
        return {
            "cli": cfg.get("cli", "claude"),
            "model": cfg.get("model", _BASELINE_OPUS),
            "context": cfg.get("context", 1000000),
        }

    else:  # "standard" or any unrecognized tier
        cfg = resolve_model("n03", cex_root=cex_root)
        return {
            "cli": cfg.get("cli", "claude"),
            "model": cfg.get("model", _BASELINE_OPUS),
            "context": cfg.get("context", 1000000),
        }


def get_model_string(nucleus, cex_root=None):
    """Convenience: return just the model string for a nucleus.

    Equivalent to resolve_model(nucleus)["model"] but shorter for callers
    that only need the model identifier.
    """
    return resolve_model(nucleus, cex_root=cex_root)["model"]


def get_cli(nucleus, cex_root=None):
    """Convenience: return just the CLI name for a nucleus."""
    return resolve_model(nucleus, cex_root=cex_root)["cli"]


# ---------------------------------------------------------------------------
# __main__ -- debug utility: print resolved config for all nuclei
# ---------------------------------------------------------------------------

def _print_table():
    """Print resolved model configuration for all nuclei and special sections."""
    config = load_nucleus_models()
    if not config:
        print("[WARN] Could not load nucleus_models.yaml")
        print("  Checked: CEX_ROOT env, git root, parent walk")
        print("  All functions will return the baseline default (%s)" % _BASELINE_OPUS)
        return

    nuclei = ["n01", "n02", "n03", "n04", "n05", "n06", "n07"]

    print("=" * 72)
    print("CEX Model Resolver -- Runtime Configuration")
    print("=" * 72)
    print("")

    # Nucleus table
    print("NUCLEI:")
    print("-" * 72)
    fmt = "  {:<5} | {:<8} | {:<30} | {:>9} | fallback: {}"
    print(fmt.format("NUC", "CLI", "MODEL", "CONTEXT", "CHAIN_LEN"))
    print("  " + "-" * 68)

    for nuc in nuclei:
        cfg = resolve_model(nuc)
        chain = get_fallback_chain(nuc)
        print(fmt.format(
            nuc.upper(),
            cfg["cli"],
            cfg["model"],
            cfg["context"],
            len(chain),
        ))

    print("")

    # Preflight
    print("PREFLIGHT:")
    print("-" * 72)
    local = get_preflight_model("local")
    cloud = get_preflight_model("cloud")
    print("  local:  cli={}, model={}, url={}".format(
        local.get("cli"), local.get("model"), local.get("base_url", "n/a")))
    print("  cloud:  cli={}, model={}".format(
        cloud.get("cli"), cloud.get("model")))

    print("")

    # Ollama
    print("OLLAMA API:")
    print("-" * 72)
    ollama = get_ollama_config()
    print("  base_url:  {}".format(ollama["base_url"]))
    print("  embed_url: {}".format(ollama["embed_url"]))
    print("  primary:   {}".format(ollama["models"]["primary"]))
    print("  heavy:     {}".format(ollama["models"]["heavy"]))
    print("  light:     {}".format(ollama["models"]["light"]))
    print("  student:   {}".format(ollama["models"]["student"]))
    print("  parallel:  {}".format(ollama.get("parallel", 1)))

    print("")

    # Tool tier resolution
    print("TOOL TIERS (resolve_model_for_tool):")
    print("-" * 72)
    for tier in ("light", "standard", "heavy"):
        cfg = resolve_model_for_tool("__debug__", task_tier=tier)
        print("  {:<10} -> {} / {}".format(tier, cfg["cli"], cfg["model"]))

    print("")
    print("=" * 72)


def main():
    # Single-nucleus query mode: `cex_model_resolver.py n03` prints just the
    # resolved model id (self-test for the opus_latest_dynamic wave). Any other
    # arg falls through to the full table.
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    nuc = next((a for a in args if re.match(r"^n0[1-7]$", a.lower())), None)
    if nuc:
        print(get_model_string(nuc.lower()))
        return
    _print_table()


if __name__ == "__main__":
    def _main_wrapper(argv=None):
        import sys
        if argv:
            sys.argv = [sys.argv[0]] + argv
        main()
    try:
        from cex_agent_io import wrap_main
        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_model_resolver"))
    except ImportError:
        main()
