#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEX Boot Pipeline -- runs BEFORE the CLI launches.

Resolves CLI + model + flags + env vars for a nucleus by chaining
optional pre-flight steps (intent resolver -> secretariat -> preflight ->
router). Output is JSON consumed by boot/n0X.ps1 and boot/cex_nucleus.sh.

Behaviors (DP1 Balanced default):
  - Layer 1 (intent resolver) and final yaml resolution always run
  - Layer 2 (secretariat / preflight) opt-in via CEX_AUTOWIRE_PREFLIGHT=1
    or --preflight CLI flag
  - Cache resolved env in .cex/cache/boot/{nucleus}.json with 5-min TTL
  - On any error, fall back to direct nucleus_models.yaml read
  - Append decision log to .cex/runtime/boot_log.jsonl

Usage:
  python _tools/cex_boot_pipeline.py --nucleus n07 --json
  python _tools/cex_boot_pipeline.py --nucleus n03 --task /path/handoff.md --preflight
  python _tools/cex_boot_pipeline.py --nucleus n07 --no-cache --json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / ".cex" / "config" / "nucleus_models.yaml"
CACHE_DIR = ROOT / ".cex" / "cache" / "boot"
BOOT_LOG = ROOT / ".cex" / "runtime" / "boot_log.jsonl"
TTL_SECONDS = 300  # 5 minutes

VALID_NUCLEI = {"n01", "n02", "n03", "n04", "n05", "n06", "n07"}

# DP1 background model-discovery probe. Boot reads the CURRENT discovery cache
# instantly (via cex_model_resolver); if that cache is missing or >= 24h old we
# fire cex_model_updater.py --discover in the BACKGROUND (fire-and-forget) to
# refresh it for the NEXT boot. Boot NEVER waits on the probe (DP1). Writer = N05.
DISCOVERY_CACHE = ROOT / ".cex" / "cache" / "model_discovery.json"
DISCOVERY_TTL_SECONDS = 24 * 3600
MODEL_UPDATER = ROOT / "_tools" / "cex_model_updater.py"

# Shorthand -> full model ID. FALLBACK ONLY. The canonical expansion lives in
# cex_model_resolver.resolve_shorthand (reads model_aliases: from YAML + the
# 24h discovery cache + CEX_OPUS_TIER). This local map is consulted only if that
# import fails, so a degraded boot still resolves instead of crashing. opus is
# pinned to the current baseline (kept in sync with cex_model_resolver
# ._BASELINE_OPUS) so even the degraded path never serves a stale version.
# Plan: opus_latest_dynamic -- this pipeline is resolve_model.ps1's PRIMARY path.
_SHORTHAND_MAP = {
    "opus": "claude-opus-4-8",
    "sonnet": "claude-sonnet-4-6",
    "haiku": "claude-haiku-4-5-20251001",
}

# Import the canonical resolver once. The boot pipeline is the PRIMARY path for
# resolve_model.ps1, so it MUST honor the same dynamic alias block + discovery
# cache + CEX_OPUS_TIER as the Python and bash resolvers -- otherwise PS boots
# would silently stay on the old version even after the YAML alias was bumped.
try:
    _tools_dir = str(ROOT / "_tools")
    if _tools_dir not in sys.path:
        sys.path.insert(0, _tools_dir)
    from cex_model_resolver import resolve_shorthand as _resolve_shorthand
except Exception:  # import must never break boot
    _resolve_shorthand = None


def _expand_model(model: str) -> str:
    """Expand a shorthand to a full model id via the canonical resolver.

    Delegates to cex_model_resolver.resolve_shorthand so this pipeline resolves
    identically to the Python/bash/PS resolvers. Degrades to the local fallback
    map only if the import is unavailable (boot must never break).
    """
    if _resolve_shorthand is not None:
        try:
            return _resolve_shorthand(model, cex_root=str(ROOT))
        except Exception:
            pass
    return _SHORTHAND_MAP.get(model, model)


def _thin_boot_on() -> bool:
    """CEX_THIN_BOOT flag (default OFF). Truthy tokens: 1/true/yes/on. When OFF,
    the entire thin-boot path is inert and the resolved payload is byte-identical
    to the pre-thin-boot pipeline (zero regression -- the IRON RULE)."""
    return os.environ.get("CEX_THIN_BOOT", "").strip().lower() in ("1", "true", "yes", "on")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_task(task: str | None) -> str:
    if not task:
        return "no-task"
    h = hashlib.sha256(task.encode("utf-8", errors="replace")).hexdigest()
    return h[:12]


def _log(event: str, payload: dict) -> None:
    """Append decision to boot_log.jsonl. Never raises."""
    try:
        BOOT_LOG.parent.mkdir(parents=True, exist_ok=True)
        line = {"ts": _now_iso(), "event": event, **payload}
        with BOOT_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(line) + "\n")
    except Exception:
        pass


def _read_yaml() -> dict:
    """Direct read of nucleus_models.yaml. Last-resort fallback path."""
    if not CONFIG.exists():
        return {}
    try:
        return yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        _log("yaml_read_error", {"error": str(exc)})
        return {}


def _cache_path(nucleus: str, task_hash: str) -> Path:
    return CACHE_DIR / f"{nucleus}_{task_hash}.json"


def _cache_load(nucleus: str, task_hash: str) -> dict | None:
    """Return cached resolution if fresh, else None."""
    path = _cache_path(nucleus, task_hash)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        ts = data.get("_cached_at", 0)
        if time.time() - ts > TTL_SECONDS:
            return None
        data.pop("_cached_at", None)
        return data
    except Exception:
        return None


def _cache_store(nucleus: str, task_hash: str, payload: dict) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        out = dict(payload)
        out["_cached_at"] = time.time()
        _cache_path(nucleus, task_hash).write_text(
            json.dumps(out, indent=2), encoding="utf-8"
        )
    except Exception as exc:
        _log("cache_write_error", {"nucleus": nucleus, "error": str(exc)})


def _run_intent_resolver(task: str) -> dict | None:
    """Call cex_intent_resolver as subprocess (Python-first, 0 tokens)."""
    try:
        result = subprocess.run(
            [sys.executable, str(ROOT / "_tools" / "cex_intent_resolver.py"),
             "--json", task],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except Exception as exc:
        _log("intent_resolver_error", {"error": str(exc)})
    return None


def _run_router(nucleus: str, task: str | None, kind: str | None) -> dict | None:
    """Call cex_router_v2 as subprocess to pick CLI + model dynamically."""
    cmd = [sys.executable, str(ROOT / "_tools" / "cex_router_v2.py"), "--json"]
    if kind:
        cmd += ["--kind", kind]
    if task:
        cmd += ["--task", task]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except Exception as exc:
        _log("router_error", {"error": str(exc)})
    return None


def _run_preflight(nucleus: str, task: str | None) -> dict | None:
    """Optional Layer 2: compress context via cex-student / Haiku."""
    if not task:
        return None
    cmd = [sys.executable, str(ROOT / "_tools" / "cex_preflight.py"),
           "--nucleus", nucleus, "--task", task, "--json"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except Exception as exc:
        _log("preflight_error", {"error": str(exc)})
    return None


def _resolve_from_yaml(nucleus: str, yaml_data: dict) -> dict:
    """Direct yaml read -> {cli, model, flags, mcps, context}. Always succeeds.

    When CEX_DECOMPOSE_STAGE env var is set ("1" or "2"), override the nucleus
    model with `tiers.decompose.stage_{N}` so the spawned process boots with
    the correct tier model. Stage 1 = Opus reasoning, Stage 2 = cheap F6 model.
    """
    block = yaml_data.get(nucleus, {})
    base = {
        "cli": block.get("cli", "claude"),
        "model": block.get("model", "opus"),
        "flags": block.get("flags", ""),
        "mcps": block.get("mcps", ""),
        "context": block.get("context", 200000),
        "domain": block.get("domain", ""),
        "settings": block.get("settings", ""),
        "tier": block.get("tier", "full_8f"),
    }
    stage = os.environ.get("CEX_DECOMPOSE_STAGE", "").strip()
    if stage in {"1", "2"}:
        tiers = (yaml_data.get("tiers", {}) or {}).get("decompose", {}) or {}
        key = "stage_1" if stage == "1" else "stage_2"
        override_model = tiers.get(key)
        if override_model:
            base["model"] = override_model
            base["tier"] = "decompose_stage_%s" % stage
            _log("decompose_stage_override",
                 {"nucleus": nucleus, "stage": stage, "model": override_model})
    return base


def resolve_boot(
    nucleus: str,
    task: str | None = None,
    use_preflight: bool = False,
    use_cache: bool = True,
) -> dict:
    """Top-level resolver. Chains pre-flight phases then yaml fallback.

    Returns dict with: cli, model, flags, args (list), env (dict),
    domain, mcps, settings, context, source (cache|pipeline|yaml_fallback).
    """
    nucleus = nucleus.lower()
    if nucleus not in VALID_NUCLEI:
        raise ValueError(f"Invalid nucleus '{nucleus}'. Must be one of: {sorted(VALID_NUCLEI)}")

    # Cache key is flag-aware: a thin-boot resolution is cached under a distinct
    # key so an OFF boot can NEVER read a thin-written entry (keeps flag-OFF
    # byte-identical even across a 5-min TTL where a prior thin run cached).
    task_hash = _hash_task(task) + ("_thin" if _thin_boot_on() else "")

    # 1. Cache check (skip if --no-cache or preflight forced)
    if use_cache and not use_preflight:
        cached = _cache_load(nucleus, task_hash)
        if cached:
            cached["source"] = "cache"
            _log("cache_hit", {"nucleus": nucleus, "task_hash": task_hash})
            return cached

    # 2. Read yaml (always, used for fallback + as base resolution)
    yaml_data = _read_yaml()
    base = _resolve_from_yaml(nucleus, yaml_data)

    # 3. Optional Layer 1 -- intent resolver (zero-token, fast)
    intent = _run_intent_resolver(task) if task else None

    # 4. Optional Layer 2 -- preflight context compression (only when opted in)
    preflight = None
    if use_preflight or os.environ.get("CEX_AUTOWIRE_PREFLIGHT") == "1":
        preflight = _run_preflight(nucleus, task)

    # 5. Router for dynamic CLI/model choice (kind-aware if intent resolved)
    kind = intent.get("kind") if intent else None
    router = _run_router(nucleus, task, kind)

    # Merge: router > yaml base. Router output may override cli/model.
    cli = base["cli"]
    model = base["model"]
    if router and isinstance(router, dict):
        if router.get("cli"):
            cli = router["cli"]
        if router.get("model"):
            model = router["model"]

    # Expand shorthand ("opus" -> "claude-opus-4-7"). Keeps YAML readable
    # while ensuring downstream callers (PS resolver, decompose, audit
    # tools) always see the canonical full slug.
    model = _expand_model(model)

    # Build env vars + CLI args
    env = {
        "CEX_NUCLEUS": nucleus.upper(),
        "CEX_ROOT": str(ROOT),
        "CEX_BOOT_PIPELINE": "1",
    }
    if intent and intent.get("kind"):
        env["CEX_INTENT_KIND"] = intent["kind"]
    if preflight and preflight.get("compiled_context_path"):
        env["CEX_PREFLIGHT_CONTEXT"] = preflight["compiled_context_path"]

    args = base["flags"].split() if base["flags"] else []

    payload = {
        "cli": cli,
        "model": model,
        "flags": base["flags"],
        "args": args,
        "env": env,
        "domain": base["domain"],
        "mcps": base["mcps"],
        "settings": base["settings"],
        "context": base["context"],
        "tier": base.get("tier", "full_8f"),
        "intent": intent,
        "preflight_used": preflight is not None,
        "router_used": router is not None,
        "source": "pipeline",
    }

    # Thin boot (CEX_THIN_BOOT, default OFF). ADDITIVE: when OFF this block does not
    # run, so the payload is byte-identical to the legacy pipeline. When ON, pre-warm
    # the cacheable stable-prefix file + key (the prompt-cache story). NOTE (Phase A.5):
    # the REALIZED boot cut is the claudeMdExcludes overlay applied in resolve_model.ps1
    # (Resolve-CexThinBootSettings) -- it de-auto-loads the N07-only rules rather than
    # appending a prefix (appending would only ADD on top of the native auto-load). The
    # fields below feed cex_prompt_cache, not the boot appends. Degrade-never: any
    # failure leaves the payload legacy-shaped.
    if _thin_boot_on():
        try:
            import cex_boot_context as _bc
            emitted = _bc.emit_files(
                nucleus, thin=True, task=task,
                kind=(intent or {}).get("kind") if intent else None,
            )
            if emitted.get("mode") == "thin":
                payload["thin_boot"] = True
                payload["cache_control"] = True
                payload["thin_boot_prefix_path"] = emitted["prefix_path"]
                payload["thin_boot_slice_path"] = emitted["slice_path"]
                payload["thin_boot_prefix_key"] = emitted["stable_prefix_key"]
                env["CEX_THIN_BOOT"] = "1"
                _log("thin_boot", {"nucleus": nucleus,
                                   "prefix_key": emitted["stable_prefix_key"][:8]})
        except Exception as exc:  # never break boot
            _log("thin_boot_error", {"nucleus": nucleus, "error": str(exc)})

    if use_cache:
        _cache_store(nucleus, task_hash, payload)

    _log("resolve", {"nucleus": nucleus, "cli": cli, "model": model,
                     "task_hash": task_hash, "preflight": preflight is not None})
    return payload


def _discovery_cache_age_seconds() -> float:
    """Age of model_discovery.json's _fetched in seconds; +inf if missing/bad.

    Pure file read + timestamp compare -- NO network, never raises. A --pin writes
    a far-future _fetched, so a pinned cache reports a negative age (always fresh).
    """
    try:
        if not DISCOVERY_CACHE.is_file():
            return float("inf")
        data = json.loads(DISCOVERY_CACHE.read_text(encoding="utf-8"))
        fetched = data.get("_fetched") if isinstance(data, dict) else None
        if not fetched:
            return float("inf")
        ts = str(fetched).strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).total_seconds()
    except Exception:
        return float("inf")


def _maybe_fire_discovery_probe() -> None:
    """DP1: fire `cex_model_updater.py --discover` in the BACKGROUND (fire-and-forget)
    iff the discovery cache is missing or >= 24h old. Boot proceeds immediately with
    the current cache; the probe only refreshes it for the NEXT boot.

    No .wait(), output -> DEVNULL, detached process group so closing the boot console
    never kills it. NEVER raises and NEVER blocks boot (DP1). A fresh-or-pinned cache
    short-circuits (the probe does not fire), so a --pin sticks (DP2).
    """
    try:
        if _discovery_cache_age_seconds() < DISCOVERY_TTL_SECONDS:
            return  # fresh (or pinned) -- nothing to do
        if not MODEL_UPDATER.is_file():
            return
        kwargs: dict = {
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
            "stdin": subprocess.DEVNULL,
            "cwd": str(ROOT),
        }
        if os.name == "nt":
            kwargs["creationflags"] = (
                getattr(subprocess, "DETACHED_PROCESS", 0)
                | getattr(subprocess, "CREATE_NO_WINDOW", 0)
            )
        else:
            kwargs["start_new_session"] = True
        subprocess.Popen([sys.executable, str(MODEL_UPDATER), "--discover"], **kwargs)
        _log("discovery_probe_fired", {"reason": "cache_missing_or_stale"})
    except Exception as exc:  # must never break boot
        _log("discovery_probe_error", {"error": str(exc)})


def _discovery_banner() -> str:
    """DP2 notify: one line iff a FRESH discovery cache advanced opus_latest above the
    YAML alias value (a prior boot's probe found a newer Opus), or a pin is active.

    Returns '' when nothing to report / cache stale / unreadable. The caller prints
    this to STDERR so it never corrupts the JSON payload on stdout (boot/*.ps1
    consume stdout; stderr shows in the console).
    """
    try:
        if _discovery_cache_age_seconds() >= DISCOVERY_TTL_SECONDS:
            return ""
        data = json.loads(DISCOVERY_CACHE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return ""
        discovered = data.get("opus_latest")
        if not discovered:
            return ""
        source = str(data.get("_source", ""))
        if source.startswith("pinned"):
            return ("[i] Opus alias PINNED: %s "
                    "(clear: python _tools/cex_model_updater.py --unpin)" % discovered)
        yaml_opus = (_read_yaml().get("model_aliases") or {}).get("opus_latest") or ""
        if yaml_opus and discovered != yaml_opus:
            return "[i] Opus alias: %s -> %s (auto-discovered)" % (yaml_opus, discovered)
    except Exception:
        return ""
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CEX Boot Pipeline -- resolve CLI/model/flags before nucleus launch.",
    )
    parser.add_argument("--nucleus", required=True, help="Nucleus id (n01..n07)")
    parser.add_argument("--task", default=None, help="Task description or handoff path")
    parser.add_argument("--preflight", action="store_true",
                        help="Force Layer 2 preflight (cex-student context compression)")
    parser.add_argument("--no-cache", action="store_true",
                        help="Bypass cache; always run full pipeline")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON (default: human-readable)")
    args = parser.parse_args()

    # DP1/DP2: surface any auto-discovered Opus bump (or active pin) on STDERR --
    # never on stdout, which carries the JSON the boot scripts parse -- then fire
    # the background refresh probe if the 24h cache is stale. Both are best-effort
    # and never block or break boot.
    try:
        banner = _discovery_banner()
        if banner:
            print(banner, file=sys.stderr)
    except Exception:
        pass
    _maybe_fire_discovery_probe()

    try:
        result = resolve_boot(
            nucleus=args.nucleus,
            task=args.task,
            use_preflight=args.preflight,
            use_cache=not args.no_cache,
        )
    except ValueError as exc:
        # Fall back to safe defaults rather than crash boot
        print(json.dumps({"error": str(exc), "cli": "claude",
                          "model": "opus", "args": [], "env": {}}))
        return 1
    except Exception as exc:  # pylint: disable=broad-except
        # Last-resort fallback: read yaml directly
        _log("pipeline_error", {"error": str(exc)})
        yaml_data = _read_yaml()
        base = _resolve_from_yaml(args.nucleus.lower(), yaml_data)
        fallback = {
            "cli": base["cli"], "model": base["model"], "flags": base["flags"],
            "args": base["flags"].split() if base["flags"] else [],
            "env": {"CEX_NUCLEUS": args.nucleus.upper(), "CEX_ROOT": str(ROOT)},
            "domain": base["domain"], "mcps": base["mcps"],
            "settings": base["settings"], "context": base["context"],
            "tier": base.get("tier", "full_8f"),
            "source": "yaml_fallback",
        }
        print(json.dumps(fallback))
        return 0

    if args.json:
        print(json.dumps(result))
    else:
        print(f"nucleus: {args.nucleus}")
        print(f"cli:     {result['cli']}")
        print(f"model:   {result['model']}")
        print(f"flags:   {result['flags']}")
        print(f"source:  {result['source']}")
        if result.get("intent"):
            print(f"intent:  kind={result['intent'].get('kind')}, "
                  f"pillar={result['intent'].get('pillar')}, "
                  f"nucleus={result['intent'].get('nucleus')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
