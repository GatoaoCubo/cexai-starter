#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cex_intent.py -- The Steering Wheel
Natural language intent -> governed artifact prompt.

Uses Motor 8F to classify intent, loads builder specs + KC-Domains,
and composes a GOVERNED PROMPT ready for LLM execution.

Usage:
  python cex_intent.py "cria knowledge card sobre RAG chunking"
  python cex_intent.py "cria agente de vendas para ML" --dry-run
  python cex_intent.py "melhora knowledge card de eval" --execute
  python cex_intent.py --list-kinds
  python cex_intent.py "cria agent" --kind agent --dry-run
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import argparse
import json
import os
from pathlib import Path

# Import Motor 8F
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cex_8f_motor import (CEX_ROOT, OBJECT_TO_KINDS, classify_objects, fan_out,
                          generate_output, load_builder_map, load_kc_library,
                          parse_intent)
from cex_shared import find_builder_dir

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BUILDERS_ROOT = CEX_ROOT / "archetypes" / "builders"

# Builder spec prefixes in compose_prompt order
# Order: model, prompt, KC-Domain (injected), schema, output
COMPOSE_ORDER = [
    "bld_model",
    "bld_prompt",
    # KC-Domain injection point (handled separately)
    "bld_schema",
    "bld_output",
]

# All 12 builder spec prefixes (12P ISO architecture)
ALL_ISO_PREFIXES = [
    "bld_knowledge",
    "bld_model",
    "bld_prompt",
    "bld_tools",
    "bld_output",
    "bld_schema",
    "bld_eval",
    "bld_architecture",
    "bld_config",
    "bld_memory",
    "bld_feedback",
    "bld_orchestration",
]


# find_builder_dir imported from cex_shared


def load_builder_iso(builder_dir: Path, prefix: str, kind_slug: str) -> str | None:
    """Load a single builder builder spec by prefix.

    Looks for: {prefix}_{kind_slug}.md
    Falls back to any file starting with {prefix}.
    """
    target = builder_dir / f"{prefix}_{kind_slug}.md"
    if target.exists():
        return target.read_text(encoding="utf-8")

    # Fallback: any file matching prefix
    for f in builder_dir.glob(f"{prefix}_*.md"):
        return f.read_text(encoding="utf-8")
    return None


def load_all_builder_isos(builder_dir: Path, kind: str) -> dict[str, str]:
    """Load all 12 builder specs into a dict keyed by prefix."""
    kind_slug = kind.replace("-", "_")
    isos = {}
    for prefix in ALL_ISO_PREFIXES:
        content = load_builder_iso(builder_dir, prefix, kind_slug)
        if content:
            isos[prefix] = content
    return isos


# ---------------------------------------------------------------------------
# KC-Domain Loading
# ---------------------------------------------------------------------------


def load_kc_domain_content(kc_matches: list[dict]) -> str:
    """Load KC-Domain markdown content from matched KCs."""
    parts = []
    for kc in kc_matches[:3]:  # Max 3 KCs to stay within token budget
        kc_path = CEX_ROOT / kc["path"]
        if kc_path.exists():
            text = kc_path.read_text(encoding="utf-8")
            # Strip frontmatter for prompt injection
            body = _strip_frontmatter(text)
            if body.strip():
                parts.append(f"### KC: {kc.get('title', kc.get('id', 'unknown'))}\n\n{body}")
    return "\n\n---\n\n".join(parts) if parts else ""


def _strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter from markdown."""
    if text.startswith("---"):
        end = text.find("---", 3)
        if end > 0:
            return text[end + 3 :].strip()
    return text


# ---------------------------------------------------------------------------
# Prompt Composition
# ---------------------------------------------------------------------------


def compose_prompt(
    intent: str,
    kind: str,
    builder_isos: dict[str, str],
    kc_content: str,
    parsed: dict,
    plan: dict,
) -> str:
    """Compose a GOVERNED PROMPT from builder specs + KC-Domain + intent.

    Order:
      1. bld_model  -- identity and role (P02)
      2. bld_prompt -- step-by-step production process (P03)
      3. KC-Domain content  -- domain knowledge injection
      4. bld_schema -- output schema/contract (P06)
      5. bld_output -- expected output format (P05)
      6. User intent -- the actual request
    """
    sections = []

    # -- Section 1: Model (identity)
    sp = builder_isos.get("bld_model")
    if sp:
        sections.append(f"# MODEL (Builder Identity)\n\n{_strip_frontmatter(sp)}")

    # -- Section 2: Prompt (how to produce)
    instr = builder_isos.get("bld_prompt")
    if instr:
        sections.append(f"# PROMPT (Production Process)\n\n{_strip_frontmatter(instr)}")

    # -- Section 3: KC-Domain (knowledge injection)
    if kc_content:
        sections.append(f"# DOMAIN KNOWLEDGE (KC Injection)\n\n{kc_content}")

    # -- Section 4: Schema (output contract)
    schema = builder_isos.get("bld_schema")
    if schema:
        sections.append(f"# SCHEMA (Output Contract)\n\n{_strip_frontmatter(schema)}")

    # -- Section 5: Output (expected format)
    tpl = builder_isos.get("bld_output")
    if tpl:
        sections.append(f"# OUTPUT (Expected Format)\n\n{_strip_frontmatter(tpl)}")

    # -- Section 6: User Intent (the actual task)
    intent_block = _format_intent_block(intent, kind, parsed, plan)
    sections.append(f"# USER INTENT\n\n{intent_block}")

    return "\n\n---\n\n".join(sections)


def _format_intent_block(intent: str, kind: str, parsed: dict, plan: dict) -> str:
    """Format the user intent with parsed context."""
    lines = [
        f"**Intent**: {intent}",
        f"**Kind**: {kind}",
        f"**Verb**: {parsed.get('verb', 'cria')} ({parsed.get('verb_action', 'create')})",
        f"**Domain**: {parsed.get('domain', 'generic')}",
        f"**Quality Target**: {parsed.get('quality', 9.0)}",
    ]

    # Active builders summary
    active = []
    for fn in plan.get("functions", []):
        for b in fn.get("builders", []):
            if b.get("active"):
                active.append(f"{b['id']} ({fn['name']})")
    if active:
        lines.append(f"\n**Active Builders** ({len(active)}):")
        for a in active:
            lines.append(f"  - {a}")

    # Warnings
    warnings = plan.get("warnings", [])
    if warnings:
        lines.append("\n**Warnings**:")
        for w in warnings:
            lines.append(f"  ! {w}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# List Kinds
# ---------------------------------------------------------------------------


def list_kinds():
    """Print all available kinds grouped by pillar."""
    by_pillar: dict[str, list[tuple[str, str]]] = {}
    seen = set()
    for _keyword, kinds_list in sorted(OBJECT_TO_KINDS.items()):
        for kind, pillar, fn in kinds_list:
            key = (kind, pillar)
            if key not in seen:
                seen.add(key)
                by_pillar.setdefault(pillar, []).append((kind, fn))

    print("\n=== CEX Kinds (Motor 8F) ===\n")
    for pillar in sorted(by_pillar.keys()):
        kinds = sorted(by_pillar[pillar], key=lambda x: x[0])
        print(f"\n  {pillar}:")
        for kind, fn in kinds:
            builder_dir = find_builder_dir(kind)
            has_builder = "+" if builder_dir else " "
            print(f"    {has_builder} {kind:<30s} [{fn}]")
    print(f"\n  Total: {len(seen)} kinds")
    print("  + = builder exists in archetypes/builders/\n")


# ---------------------------------------------------------------------------
# Execution (--execute)
# ---------------------------------------------------------------------------


# Approximate chars-per-token for fallback estimates (industry rule of thumb).
# Used when the provider does not return real token counts (e.g. Claude CLI,
# subprocess wraps that swallow usage). Documented in cex_cost_tracker.py.
_CHARS_PER_TOKEN = 4


def _kill_tree(pid: int) -> None:
    """Kill a process and ALL its descendants (Windows: taskkill /T; POSIX: killpg).
    Same house pattern as cex_quota_check._kill_tree. Without this, a `claude -p`
    call that outlives its subprocess timeout leaves an orphaned agentic session
    (plus its node.exe/MCP children) running in the background -- free to keep
    writing to disk (e.g. the knowledge library) minutes after the caller has
    already moved on and reported failure. That orphan is a root cause of
    R-156's fabricated self-KC content (docs/IMPROVEMENT_REGISTER.md)."""
    import subprocess as _subprocess
    try:
        if sys.platform == "win32":
            _subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)],
                            capture_output=True, timeout=10)
        else:
            import signal as _signal
            os.killpg(os.getpgid(pid), _signal.SIGKILL)
    except Exception:
        pass


def _run_claude_cli(args: list, prompt: str, timeout: int = 120):
    """Run a `claude -p ...` subprocess with FAIL-CLOSED tree-kill on timeout.

    Plain `subprocess.run(..., timeout=N)` only signals the immediate child --
    on Windows that child is `claude.cmd`, which has already forked its own
    node.exe (+ MCP) descendants by the time the timeout fires. `process.kill()`
    on TimeoutExpired never reaches those descendants, so they keep running as
    an orphaned agentic session with live filesystem write access. This runs
    the CLI in its own process group (Windows: CREATE_NEW_PROCESS_GROUP; POSIX:
    setsid) so `_kill_tree` can reap the WHOLE tree the instant the timeout
    fires -- never letting a stray "generate text" call keep mutating the repo
    after the caller has given up on it.

    Returns a `subprocess.CompletedProcess`-shaped object (returncode/stdout/
    stderr). Re-raises `subprocess.TimeoutExpired` AFTER the tree is dead, so
    existing `except Exception` callers keep working unchanged.
    """
    import subprocess as _subprocess
    creationflags = 0
    preexec_fn = None
    if sys.platform == "win32":
        creationflags = getattr(_subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    else:
        preexec_fn = os.setsid
    popen_kwargs = dict(
        stdin=_subprocess.PIPE, stdout=_subprocess.PIPE, stderr=_subprocess.PIPE,
        text=True, encoding="utf-8", creationflags=creationflags,
    )
    if preexec_fn is not None:
        popen_kwargs["preexec_fn"] = preexec_fn
    proc = _subprocess.Popen(args, **popen_kwargs)
    try:
        stdout, stderr = proc.communicate(input=prompt, timeout=timeout)
        return _subprocess.CompletedProcess(args, proc.returncode, stdout, stderr)
    except _subprocess.TimeoutExpired:
        _kill_tree(proc.pid)
        try:
            proc.communicate(timeout=5)
        except Exception:
            pass
        raise


# ---------------------------------------------------------------------------
# Tool-restriction for pure text-generation calls (R-170 defense-in-depth)
# ---------------------------------------------------------------------------
#
# _run_claude_cli spawns a real `claude -p` agentic session. Both callers in
# execute_prompt() only want TEXT back (a composed governed prompt in, a
# markdown/response string out) -- neither ever needs the model to call a
# tool. Left unrestricted, that subprocess inherits WHATEVER ambient
# permission config is active for its cwd -- and in this repo that is
# dangerous: both the project .claude/settings.json AND the user-level
# ~/.claude/settings.json set "defaultMode": "bypassPermissions", and the
# project settings additionally allow-list Bash(*)/Write(*)/Edit(*)/etc. A
# "generate some text" subprocess call therefore currently CAN mutate the
# tree -- exactly the R-170 concern.
#
# Evidence (empirical, verified against installed CLI 2.1.200; see the
# R-170 row in docs/IMPROVEMENT_REGISTER.md for the full probe transcript):
#   - --allowedTools "" alone did NOT block a live Bash call under this
#     repo's bypassPermissions config. bypassPermissions skips the
#     allow/deny permission gate entirely, so an allow-list -- even an
#     empty one -- is never consulted.
#   - --disallowedTools "Bash" alone: same result, NOT blocked. Deny-lists
#     sit at the same permission-gate layer as allow-lists; bypass skips
#     that gate regardless of what it contains.
#   - --tools "" (the built-in tool INVENTORY -- a layer BEFORE permission
#     checking) DID block the Bash call ("The bash tool is not available in
#     this environment"). This is the flag that actually enforces "no
#     tools" here; --allowedTools / --disallowedTools alone would have been
#     a false sense of security given this repo's ambient config.
#   - --tools "" alone still left ambient MCP servers connected with live
#     tool schemas (--debug api showed canva-remote + claude.ai
#     Gmail/Calendar/Drive all connecting, "hasTools":true each). Adding
#     --strict-mcp-config (with no --mcp-config passed) dropped MCP
#     connections to zero.
#   - Net: --tools "" --strict-mcp-config together = zero built-in tools,
#     zero MCP tools -- genuinely "no tools at all". Normal text output
#     (default text format, matching how execute_prompt() consumes
#     result.stdout) is unaffected -- verified with a real generation call.
#
# Simplification (deliberate, documented): the two flags are probed and
# cached as ONE atomic unit. If a future/older CLI recognizes one but not
# the other, this falls all the way back to unrestricted rather than
# applying the one that works. Today's installed CLI supports both
# together, so this is a real trade-off only for a CLI version this repo
# has not been tested against -- simplicity over a currently-hypothetical
# partial-degradation path.
#
# Degrade-never: an installed CLI too old to recognize these flags fails
# FAST on argv parsing (commander.js: exit 1, stderr
# "error: unknown option '...'"; confirmed empirically) before any network
# or model activity. We detect exactly that signature, retry WITHOUT the
# restriction flags so intent resolution never breaks, and cache the
# outcome (in-memory for this process + a small disk-persisted file keyed
# by `claude --version`, mirroring cex_provider_discovery.py's
# CACHE_PATH/discover_providers pattern) so later calls skip straight to
# whichever call shape actually works for the installed CLI.

# A2.x tenant-path migration: route the RUNTIME surface through the ONE canonical resolver
# (cex_tenant_paths). CEX_TENANT_ID unset -> tenant_runtime_dir() returns the legacy global
# .cex/runtime (byte-identical single-tenant); a tenant bound -> .cex/tenants/<tid>/runtime.
# Degrade-never: fall back to the legacy join if the resolver is not importable here (_tools
# is already on sys.path via the insert above).
try:
    from cex_tenant_paths import tenant_runtime_dir as _tenant_runtime_dir
    _TOOL_FLAGS_CACHE_PATH = _tenant_runtime_dir() / "claude_cli_flags_cache.json"
except Exception:
    _TOOL_FLAGS_CACHE_PATH = CEX_ROOT / ".cex" / "runtime" / "claude_cli_flags_cache.json"

# A pure text-generation call needs exactly zero tools: no built-in tools
# AND no MCP-server tools. This is the "narrowest allowlist" -- empty.
_NO_TOOLS_FLAGS = ["--tools", "", "--strict-mcp-config"]

_no_tools_supported_cache: bool | None = None  # in-memory, this process only
_claude_version_cache: str | None = None  # memoize the (cheap) --version probe


def _unknown_option_error(returncode: int, stderr: str) -> bool:
    """True iff a subprocess failure is the CLI rejecting an unrecognized
    flag at argv-parse time (vs. a real runtime failure: timeout, auth,
    network, quota). Signature confirmed empirically against the installed
    CLI: exit 1, stderr contains "unknown option" -- emitted before any
    network/model activity, so this never misfires for a legitimate call
    failure."""
    return returncode != 0 and "unknown option" in (stderr or "").lower()


def _get_claude_cli_version() -> str:
    """Cheap, side-effect-free version probe (no network/model call -- `-v`
    is handled before argv validation) used to key the flag-support disk
    cache so it self-invalidates the instant the CLI is upgraded/downgraded.
    Best-effort: any failure returns a sentinel so caching degrades to
    'always re-check' rather than raising."""
    global _claude_version_cache
    if _claude_version_cache is not None:
        return _claude_version_cache
    try:
        import subprocess as _subprocess
        r = _subprocess.run(["claude", "--version"], capture_output=True,
                             text=True, timeout=10)
        _claude_version_cache = (r.stdout or "").strip() or "unknown"
    except Exception:
        _claude_version_cache = "unknown"
    return _claude_version_cache


def _load_no_tools_flag_support() -> bool | None:
    """Return cached knowledge of whether the installed CLI accepts
    _NO_TOOLS_FLAGS. None = unknown (never probed this process, or the disk
    cache is stamped for a different CLI version) -- caller should
    attempt-and-detect rather than assume."""
    global _no_tools_supported_cache
    if _no_tools_supported_cache is not None:
        return _no_tools_supported_cache
    try:
        if _TOOL_FLAGS_CACHE_PATH.exists():
            cached = json.loads(_TOOL_FLAGS_CACHE_PATH.read_text(encoding="utf-8"))
            if cached.get("claude_version") == _get_claude_cli_version() \
                    and "no_tools_flags_supported" in cached:
                _no_tools_supported_cache = bool(cached["no_tools_flags_supported"])
                return _no_tools_supported_cache
    except Exception:
        pass
    return None


def _remember_no_tools_flag_support(supported: bool) -> None:
    """Persist the probe outcome so future `python cex_intent.py` processes
    (each a fresh interpreter -- the in-memory cache does not survive across
    them) skip straight to the working call shape instead of re-discovering
    it on every single invocation. Best-effort: a cache write failure never
    blocks execution (mirrors _track_call's silent-failure contract)."""
    global _no_tools_supported_cache
    _no_tools_supported_cache = supported
    try:
        _TOOL_FLAGS_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _TOOL_FLAGS_CACHE_PATH.write_text(
            json.dumps({
                "claude_version": _get_claude_cli_version(),
                "no_tools_flags_supported": supported,
            }, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass


def _run_claude_cli_no_tools(model_args: list, prompt: str, timeout: int = 120):
    """Run a `claude -p` call that must be PURE text-generation: no built-in
    tools, no MCP tools (see the R-170 comment block above this function for
    the full evidence trail). `model_args` is the invariant prefix, e.g.
    ["claude", "-p", "--model", "claude-sonnet-4-6"] -- the restriction
    flags are appended after it, never inserted in the middle (commander.js
    variadic options like --tools greedily consume subsequent bare tokens,
    so anything meant to be a separate flag must itself start with "-").

    Degrade-never: if the installed CLI does not recognize the restriction
    flags, falls back to the unrestricted call (pre-fix behavior) so intent
    resolution keeps working, and remembers the outcome so later calls do
    not pay the failed-attempt cost again for this CLI version.
    """
    supported = _load_no_tools_flag_support()
    if supported is False:
        return _run_claude_cli(model_args, prompt, timeout=timeout)

    result = _run_claude_cli(model_args + _NO_TOOLS_FLAGS, prompt, timeout=timeout)

    if _unknown_option_error(result.returncode, result.stderr):
        print(
            "WARN: installed claude CLI does not recognize --tools/"
            "--strict-mcp-config -- falling back to an unrestricted call "
            "(degrade-never). Upgrade the Claude Code CLI to close this "
            "defense-in-depth gap (see docs/IMPROVEMENT_REGISTER.md R-170).",
            file=sys.stderr,
        )
        _remember_no_tools_flag_support(False)
        return _run_claude_cli(model_args, prompt, timeout=timeout)

    if supported is None:
        _remember_no_tools_flag_support(True)
    return result


def _track_call(provider: str, model: str, prompt: str, response_text: str,
                input_tokens: int = 0, output_tokens: int = 0,
                preflight_used: bool = False, substituted_from: str = "") -> None:
    """Append a cost event to cost_log.jsonl via cex_cost_tracker.record().

    If real token counts are not provided (input_tokens=0 or output_tokens=0),
    falls back to char/4 estimate -- the documented approximation when the
    provider does not surface usage (Claude CLI subprocess is the main case).

    Tags the event with CEX_NUCLEUS, CEX_MISSION, CEX_COST_CONTEXT (decompose
    sets these to attribute Stage 1 vs Stage 2 vs solo runs).

    substituted_from (R-337 Fix 4, optional, default ""): when non-empty,
    names the model_override that was REQUESTED but failed before THIS call
    substituted it (e.g. a GLM id whose branch errored or returned empty
    content, falling through to the Claude CLI default). cex_cost_tracker.
    record() has a FIXED keyword schema (inspected: not free-form) and is
    OUTSIDE this lane's HARD FENCE, so this does not add a new cost_log.jsonl
    field.

    CORRECTED (judge-caught, post-review): an earlier version of this fix
    appended the annotation onto the `mission` value. That is UNSAFE --
    cex_cost_tracker._filter() does an EXACT-MATCH comparison on `mission`
    (`r.get("mission") != mission`), and that filter backs BOTH the
    `--mission NAME` CLI flag and mission_rollup(). Annotating `mission`
    therefore made the substituted call's row silently FAIL to match its own
    mission's exact-match filter -- the call's cost would vanish from that
    mission's total_usd/by_session/by_nucleus rollup, the functional OPPOSITE
    of this fix's honesty goal (see test_mission_rollup_still_counts_
    substituted_call_r337 in test_cex_intent_glm.py for the end-to-end
    reproduction of that regression and the proof it is now closed).

    Fixed version: the annotation is carried on the existing `subagent_id`
    field instead (optional, default "", already used by cex_mentor_swarm.py
    to tag escalation-tier producer ids like "producer_2#opus" -- but that
    writer calls cex_cost_tracker.record() directly, a wholly separate code
    path from this function, so the two uses never collide on one row).
    subagent_id is READ by no exact-match filter and GROUPED BY no
    _rollup() dimension anywhere in cex_cost_tracker.py (grep-verified) --
    it is purely additive: record()'s own `if subagent_id: entry
    ["subagent_id"] = subagent_id` means the key is simply absent from the
    emitted JSON unless this parameter is non-empty, so `mission` (and every
    filter/rollup keyed on it) is now byte-unaffected by a substitution.
    Default "" means zero change to any existing caller.
    """
    try:
        if input_tokens <= 0:
            input_tokens = max(1, len(prompt) // _CHARS_PER_TOKEN)
        if output_tokens <= 0:
            output_tokens = max(1, len(response_text) // _CHARS_PER_TOKEN)

        # Optional context tag (e.g. decompose_stage_1 / decompose_stage_2)
        context = os.environ.get("CEX_COST_CONTEXT", "")
        mission = os.environ.get("CEX_MISSION", "") or context
        nucleus = os.environ.get("CEX_NUCLEUS", "")
        # R-337 Fix 4 (corrected): subagent_id, NOT mission -- see docstring.
        subagent_id = (
            "substituted_from=%s" % substituted_from if substituted_from else ""
        )

        # Defer import to keep cex_intent independent for callers that lazy-load
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from cex_cost_tracker import record as _cost_record  # type: ignore
        _cost_record(
            provider=provider,
            model=model,
            input_tokens=int(input_tokens),
            output_tokens=int(output_tokens),
            mission=mission,
            nucleus=nucleus,
            preflight_used=preflight_used,
            subagent_id=subagent_id,
        )
    except Exception:
        # Never let tracking failures break the LLM call path.
        pass


# ---------------------------------------------------------------------------
# GLM / OpenWebUI routing (DP1+DP2, GLM_BENCH_0712_EXEC W1, R-336/R-337)
# ---------------------------------------------------------------------------
#
# DP1 (decision_manifest_glm_bench_2026_07_12.yaml) added these 4 ids to
# tiers.f6_generation.models in nucleus_models.yaml. Bare "glm-5.2" is NOT a
# member of this set -- it is the same reasoning model "glm-openwebui"
# already aliases at the litellm layer (see _load_glm_openwebui_entry
# below), so keeping it out of the DEFAULT tier avoids double-registering
# one box variant under two ids (that tier-membership question is separate
# from whether execute_prompt() itself recognizes the id -- see next
# paragraph).
#
# R-357 (2026-07-13, founder D1, decision_manifest_serving_northstar_0713
# .yaml: "usar 5.2 com alavancagem maxima + max_tokens pra harness/
# benchmark/integracoes") REVERSES the original DP1 exclusion of bare
# "glm-5.2" from execute_prompt() itself: it no longer raises there -- it is
# now a recognized OPT-IN executor (see the `model_override == "glm-5.2"`
# branch below), routed through the exact same openwebui path as
# "glm-openwebui" plus a _GLM52_REASONING_FLOOR applied to max_tokens (both
# ids alias the same reasoning-fragile model -- 0-content proven twice at
# realistic prompt sizes below the floor, see p07_bm_glm_openwebui.md Lane
# A/C). Still cloud-proxied (not local, costs real tokens/USD -- see the
# "no pricing-map entry" cost=None note on _execute_via_glm_openwebui) and
# still NOT part of the default routing tier (nucleus_models.yaml /
# cex_router_v2.py) -- that stays a separate GDP/spend-guardrail decision,
# untouched by R-357. GLM_OPENWEBUI_MODELS itself is UNCHANGED (still these
# same 4 members) -- glm-5.2-fast/glm-cpw/glm-flash keep their exact
# pre-existing behavior, no floor imposed on them.
GLM_OPENWEBUI_MODELS = frozenset({
    "glm-openwebui", "glm-5.2-fast", "glm-cpw", "glm-flash",
})

# The ONE real GLM/openwebui litellm entry lives here (model_name=
# "glm-openwebui"). Only that literal id is a model_list entry; the other 3
# GLM_OPENWEBUI_MODELS ids share its api_base/api_key (same box, same tunnel)
# but get their own "openai/<id>" model string -- the exact convention
# GLM_BENCH_0712 Lane C live-proved for glm-cpw (model_id="openai/glm-cpw",
# ok=true, see laneC_stage2_call_glmcpw.json). This is the "Membership check:
# ids present in litellm_config model_list, not a prefix guess" DP2 asked
# for: the branch below actually reads this file at call time rather than
# assuming a hardcoded prefix test like model_override.startswith("glm")
# (which would wrongly also match glm-local/glm-serverside-flash/arena-model
# -- real box models that are NOT part of DP1's approved tier list).
_LITELLM_CONFIG_PATH = CEX_ROOT / ".cex" / "config" / "litellm_config.yaml"

# ENV wins; else the gitignored staging vault, BY NAME. Never logs a value.
_GLM_VAULT_PATH = CEX_ROOT / ".cex" / "tenants" / "_cexai_staging_secrets.env"

# --- R-336 blast-radius audit (GLM_BENCH_0712_EXEC W1, step 1) -------------
# Non-"ollama/"-, non-"claude"-prefixed model_override values that LIVE,
# pre-existing (not GLM-related) callers already pass today and silently
# depend on reaching the Claude CLI default branch below. Wiring THEIR real
# routing (native Gemini/OpenAI execute_prompt branches) is out of DP2's
# scope -- this set is a documented compatibility shim, not an endorsement,
# so DP2b's "no more silent Claude fallback" does not break them. A value in
# this set still reaches the Claude CLI default exactly as before, but now
# prints a visible WARN (previously fully silent) instead of vanishing.
#
# Evidenced live call sites (grep, 2026-07-12, GLM_BENCH_0712_EXEC W1):
#   - cex_decompose.py:111,212-219  tiers.decompose.stage_2_fallback retry
#     loop: [gemini-2.5-flash-lite, qwen3:8b] passed verbatim as --model on
#     a Stage-2 retry. ("qwen3:8b" here is ALSO missing the "ollama/" prefix
#     execute_prompt requires -- a pre-existing config bug in nucleus_models
#     .yaml, independent of this fix and outside this lane's hard fence; kept
#     as passthrough, not repaired.)
#   - nucleus_models.yaml tiers.escalation_ladders.google/openai (W6
#     cross-provider escalation) -- cex_mentor_swarm.py:800 resolves these
#     via _resolve_alias() BEFORE calling execute_prompt, landing on bare
#     gemini-2.5-flash-lite/gemini-2.5-flash/gemini-2.5-pro/gpt-5-mini/
#     gpt-5.2 (model_aliases: gemini_flash_lite_latest/gemini_flash_latest/
#     gemini_pro_latest/gpt_mini_latest/gpt_latest).
#   - nucleus_models.yaml tiers.f6_generation.models pre-existing entries
#     (gpt-4.1, gpt-5) -- declared Mode B generation models with no native
#     execute_prompt branch yet (same gap class GLM had before this fix).
#
# NOTE (documented limitation): this is a hardcoded snapshot of today's
# resolved alias VALUES, not a live read of model_aliases -- if a future
# alias bump changes e.g. gpt_latest's version string, the NEW value would
# need a matching bump here or it starts raising instead of passing through.
# Accepted trade-off: a clear, fixable failure on drift beats the added
# complexity of re-deriving this set from YAML on every call.
LEGACY_PASSTHROUGH_MODELS = frozenset({
    "gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro",
    "gpt-4.1", "gpt-5", "gpt-5-mini", "gpt-5.2",
    "qwen3:8b",
})


def _load_vault_env_names(path: Path) -> dict:
    """Dotenv-style parse, NAME:value only. Tolerant of 'export ' prefixes and
    quotes. Mirrors cex_dashboard_persist_proof._parse_env_file_names_values.
    Returns {} if the file is absent/unreadable (degrade-never). Values are
    for in-process use ONLY -- never printed/logged."""
    out: dict = {}
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return out
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue
        name, _, value = line.partition("=")
        name = name.strip()
        value = value.strip().strip('"').strip("'")
        if name:
            out[name] = value
    return out


def _resolve_glm_secret(name: str) -> str:
    """Resolve ONE secret by NAME: process env wins, else the gitignored
    staging vault (.cex/tenants/_cexai_staging_secrets.env). Returns "" if
    neither has it. NEVER prints/logs the resolved value."""
    val = os.environ.get(name)
    if val is not None and val.strip():
        return val.strip()
    file_vals = _load_vault_env_names(_GLM_VAULT_PATH)
    return (file_vals.get(name) or "").strip()


def _resolve_env_ref(value: str) -> str:
    """Resolve a litellm_config.yaml-style 'os.environ/VAR' reference to its
    live value (env-first, vault-fallback via _resolve_glm_secret). A plain
    (non-'os.environ/') string passes through unchanged -- litellm_config.yaml
    uses this same convention for both api_base and api_key."""
    if isinstance(value, str) and value.startswith("os.environ/"):
        return _resolve_glm_secret(value[len("os.environ/"):])
    return value or ""


def _load_glm_openwebui_entry() -> dict:
    """Read the 'glm-openwebui' model_list entry from litellm_config.yaml --
    the real membership anchor DP2 asked for ("ids present in litellm_config
    model_list, not a prefix guess"). Raises RuntimeError (a config problem,
    distinct from the caller-facing ValueError for an unrecognized override)
    if the file or the entry is missing, so a broken/renamed config fails
    loud instead of silently degrading into yet another Claude misroute."""
    try:
        import yaml
        data = yaml.safe_load(_LITELLM_CONFIG_PATH.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        raise RuntimeError(
            "GLM routing: litellm_config.yaml failed to load (%s): %s"
            % (_LITELLM_CONFIG_PATH, exc)
        ) from exc
    for entry in data.get("model_list", []) or []:
        if isinstance(entry, dict) and entry.get("model_name") == "glm-openwebui":
            return entry
    raise RuntimeError(
        "GLM routing: no 'glm-openwebui' entry in %s model_list (config/DP1 drift)"
        % _LITELLM_CONFIG_PATH
    )


# Frugal, reasoning-budget-safe default (mission methodology: max_tokens<=800
# every call; >=300 is the documented floor below which glm-5.2-family
# reasoning consumes the whole visible-answer budget and returns empty
# content -- p07_bm_glm_openwebui.md "Reasoning-budget gotcha").
_GLM_DEFAULT_MAX_TOKENS = 800

# R-357 (2026-07-13): a STRICTER, class-specific floor for the actual
# glm-5.2 reasoning model -- 2000, not 300/800 -- because the 07-12 GLM_BENCH
# incident (0 content at max_tokens=800, cured only at 2500) proved 800 is
# still tight enough to starve this specific model's hidden-reasoning burn.
# This is a MINIMUM, not a cap: a caller asking for MORE than the floor is
# always respected as-is (see _execute_via_glm_openwebui below).
_GLM52_REASONING_FLOOR = 2000

# Exactly the 2 model ids that resolve to the glm-5.2 reasoning model at the
# litellm layer (bare "glm-5.2" itself, and "glm-openwebui" which
# _load_glm_openwebui_entry's params.get("model") aliases to
# "openai/glm-5.2"). Deliberately NOT GLM_OPENWEBUI_MODELS itself -- that
# frozenset's other members (glm-5.2-fast, glm-cpw, glm-flash) are lighter,
# non-reasoning tiers and must keep _GLM_DEFAULT_MAX_TOKENS untouched (no
# floor imposed on them).
_GLM52_REASONING_FAMILY = frozenset({"glm-5.2", "glm-openwebui"})


def _execute_via_glm_openwebui(prompt: str, model_id: str, max_tokens: int) -> tuple:
    """Call the GLM/openwebui box via the litellm SDK direct (the same seam
    GLM_BENCH_0712 Lane B/C live-proved -- NOT the litellm proxy server).

    Returns (content, cost, cost_details, input_tokens, output_tokens).
    `cost`/`cost_details` come from litellm's own _hidden_params -- Lane B
    found these are None for this box (no pricing-map entry for a custom
    api_base); the caller logs whatever comes back plainly, never swallows it.

    R-357: when `model_id` is in the reasoning family (_GLM52_REASONING_
    FAMILY -- bare 'glm-5.2' or 'glm-openwebui'), the effective max_tokens is
    floored to _GLM52_REASONING_FLOOR (2000) if the caller-requested/default
    value is lower, with a visible stderr WARN. This is a floor, not a cap --
    a caller-requested value already >= the floor passes through unchanged.
    glm-5.2-fast/glm-cpw/glm-flash are NOT in the reasoning family and are
    completely unaffected (byte-identical to pre-R-357 behavior).
    """
    import litellm

    entry = _load_glm_openwebui_entry()
    params = entry.get("litellm_params", {}) or {}
    api_base = _resolve_env_ref(params.get("api_base", ""))
    api_key = _resolve_env_ref(params.get("api_key", ""))
    if not api_base or not api_key:
        raise RuntimeError(
            "GLM routing: OPENWEBUI_API_BASE/OPENWEBUI_API_KEY did not resolve "
            "(checked process env, then the vault) -- cannot reach the box."
        )

    if model_id == "glm-openwebui":
        # The one id with a real YAML-declared model string -- use it verbatim.
        litellm_model = params.get("model") or "openai/glm-5.2"
    else:
        # Same box/api_base/api_key, different model slug -- the "openai/<id>"
        # convention Lane C live-proved for glm-cpw.
        litellm_model = "openai/%s" % model_id

    effective_max_tokens = (
        max_tokens if max_tokens and max_tokens > 0 else _GLM_DEFAULT_MAX_TOKENS
    )
    if (
        model_id in _GLM52_REASONING_FAMILY
        and effective_max_tokens < _GLM52_REASONING_FLOOR
    ):
        print(
            "[GLM-5.2] max_tokens elevado p/ 2000 -- reasoning-model precisa "
            "de folga, R-357 (pedido: %s)" % effective_max_tokens,
            file=sys.stderr,
        )
        effective_max_tokens = _GLM52_REASONING_FLOOR

    response = litellm.completion(
        model=litellm_model,
        messages=[{"role": "user", "content": prompt}],
        api_base=api_base,
        api_key=api_key,
        max_tokens=effective_max_tokens,
    )
    content = response.choices[0].message.content or ""
    cost = None
    cost_details = None
    try:
        hidden = getattr(response, "_hidden_params", None) or {}
        cost = hidden.get("response_cost")
        cost_details = hidden.get("response_cost_details")
    except Exception:
        pass
    usage = getattr(response, "usage", None)
    in_tok = int(getattr(usage, "prompt_tokens", 0) or 0) if usage else 0
    out_tok = int(getattr(usage, "completion_tokens", 0) or 0) if usage else 0
    return content, cost, cost_details, in_tok, out_tok


def execute_prompt(prompt: str, model_override: str = "", max_tokens: int = 0) -> str:
    """Send composed prompt to LLM via available provider.

    Priority: OVERRIDE > SUBSCRIPTION > LOCAL > API (pay-per-token is LAST resort).

    If model_override starts with 'ollama/', routes directly to Ollama.
    Example: model_override='ollama/qwen3:8b'

    If model_override is one of GLM_OPENWEBUI_MODELS ('glm-openwebui',
    'glm-5.2-fast', 'glm-cpw', 'glm-flash') OR the bare 'glm-5.2' reasoning
    id, routes to the GLM/openwebui box via litellm (DP1+DP2,
    GLM_BENCH_0712_EXEC; R-357, 2026-07-13 founder D1, re-admits bare
    'glm-5.2' as a recognized opt-in executor -- see the module-level
    GLM_OPENWEBUI_MODELS comment). 'glm-5.2' and 'glm-openwebui' (which
    already aliases openai/glm-5.2 at the litellm layer) both get a
    _GLM52_REASONING_FLOOR applied to max_tokens inside
    _execute_via_glm_openwebui; the other GLM_OPENWEBUI_MODELS ids do not.
    Any OTHER GLM box model that is neither in GLM_OPENWEBUI_MODELS nor bare
    'glm-5.2' (e.g. 'glm-local') remains deliberately unrecognized.

    Any OTHER non-empty model_override that matches no branch and is not in
    the documented LEGACY_PASSTHROUGH_MODELS compatibility set raises
    ValueError -- R-336 closed the prior silent fall-through to the Claude
    CLI default (see LEGACY_PASSTHROUGH_MODELS' own comment for the
    blast-radius audit that shaped which values stay silent-compatible vs.
    now raise).

    Tries (in order):
      0. Model override  -- if specified, use that provider directly
      1. Claude CLI  -- uses Max/Pro subscription, zero extra cost
      2. Ollama      -- local, free (via cex_ollama.py client)
      3. Anthropic API -- only if CEX_USE_API=1, pay-per-token
      4. OpenAI API   -- only if CEX_USE_API=1, pay-per-token

    Env vars:
      CEX_USE_API=1     -- allow paid API calls as last resort
      CEX_OLLAMA_MODEL  -- default Ollama model (default: qwen3:8b)
      CEX_FORCE_OLLAMA=1 -- skip Claude CLI, go straight to Ollama
      CEX_TRACK_COST=0  -- disable cost_log.jsonl emission (default: enabled)
      CEX_COST_CONTEXT  -- tag for cost rollups (e.g. decompose_stage_1)

    max_tokens: output token cap. 0 (default) means "unspecified" and
      preserves prior behavior exactly for the ollama/claude branches (they
      ignore it, same as before this parameter existed). The GLM branch
      applies its own documented safe default (_GLM_DEFAULT_MAX_TOKENS) when
      this is 0/falsy.

    Every return path emits a cost_log.jsonl event via _track_call() so
    cex_cost_tracker.py can roll up calls + USD across providers.

    Both Claude CLI paths (override + default) run via
    _run_claude_cli_no_tools(): this is a pure text-generation call (prompt
    in, response text out) and is invoked with zero tool access -- no
    built-in tools, no MCP tools (--tools ""/--strict-mcp-config; degrades
    to unrestricted only if the installed CLI is too old to recognize the
    flags). See the R-170 comment block above _run_claude_cli_no_tools for
    the evidence trail on why this is necessary in this repo.

    Returns the LLM response text.
    """
    errors = {}
    allow_paid_api = os.environ.get("CEX_USE_API", "0") == "1"
    force_ollama = os.environ.get("CEX_FORCE_OLLAMA", "0") == "1"
    track_cost = os.environ.get("CEX_TRACK_COST", "1") != "0"

    # --- [0] Model override (explicit routing) ---
    if model_override:
        if model_override.startswith("ollama/"):
            ollama_model = model_override[7:]  # strip "ollama/" prefix
            try:
                from cex_ollama import execute_via_ollama
                # execute_via_ollama returns text only; estimate tokens from chars
                response_text = execute_via_ollama(
                    prompt, model=ollama_model, structured=True
                )
                if track_cost:
                    _track_call(
                        provider="ollama",
                        model=f"ollama/{ollama_model}",
                        prompt=prompt,
                        response_text=response_text,
                    )
                return response_text
            except SystemExit:
                raise
            except Exception as e:
                errors["Ollama-Override"] = str(e)[:120]
                # Fall through to other providers
        elif model_override.startswith("claude"):
            # Explicit Claude model
            try:
                result = _run_claude_cli_no_tools(
                    ["claude", "-p", "--model", model_override], prompt, timeout=120)
                if result.returncode == 0 and result.stdout.strip():
                    if track_cost:
                        _track_call(
                            provider="claude-cli",
                            model=model_override,
                            prompt=prompt,
                            response_text=result.stdout,
                        )
                    return result.stdout
                errors["CLI-Claude-Override"] = f"exit {result.returncode}"
            except Exception as e:
                errors["CLI-Claude-Override"] = str(e)[:120]
        elif model_override == "glm-5.2" or model_override in GLM_OPENWEBUI_MODELS:
            # R-357 (2026-07-13, founder D1) REVERSES the prior DP1 hard
            # ValueError for bare 'glm-5.2' -- it now reaches this SAME
            # branch as the rest of GLM_OPENWEBUI_MODELS (joined via the
            # explicit `==` check above, NOT by adding it to the frozenset
            # itself -- GLM_OPENWEBUI_MODELS stays exactly its original 4
            # members). Still cloud-proxied (not local, costs real
            # tokens/USD) and still excluded from the default routing tier
            # (nucleus_models.yaml / cex_router_v2.py -- a separate
            # GDP/spend-guardrail decision, untouched here). The reasoning
            # max_tokens floor (_GLM52_REASONING_FLOOR) is applied inside
            # _execute_via_glm_openwebui for glm-5.2/glm-openwebui only --
            # glm-5.2-fast/glm-cpw/glm-flash take the exact same code path
            # below byte-identically (no floor imposed on them).
            try:
                content, cost, cost_details, in_tok, out_tok = _execute_via_glm_openwebui(
                    prompt, model_override, max_tokens
                )
                print(
                    "  [i] cost=%s cost_details=%s tokens_in=%s tokens_out=%s "
                    "(glm-openwebui box is metered; litellm has no pricing-map "
                    "entry for this custom api_base -- see p07_bm_glm_openwebui.md "
                    "Lane B)" % (cost, cost_details, in_tok, out_tok),
                    file=sys.stderr,
                )
                if content:
                    if track_cost:
                        _track_call(
                            provider="glm-openwebui",
                            model=model_override,
                            prompt=prompt,
                            response_text=content,
                            input_tokens=in_tok,
                            output_tokens=out_tok,
                        )
                    return content
                errors["GLM-Override"] = (
                    "empty content (reasoning budget exhausted at max_tokens=%s?)"
                    % (max_tokens or _GLM_DEFAULT_MAX_TOKENS)
                )
            except SystemExit:
                raise
            except Exception as e:
                errors["GLM-Override"] = str(e)[:200]
                # Fall through to other providers (same resilience shape as
                # the ollama/claude override branches above).
            if "GLM-Override" in errors:
                # R-337 Fix 4 (observability only -- no behavior change):
                # both failure paths above (empty content, or a raised
                # exception) land here without returning, and execution is
                # about to fall through to the Claude CLI default further
                # below. Previously this substitution was SILENT -- an
                # artifact "produced by glm-cpw" could actually be Sonnet,
                # discoverable only by cross-referencing cost_log.jsonl by
                # hand. Make it loud; the fallthrough itself is unchanged.
                print(
                    "[SUBSTITUTION] glm branch failed (%s) -> serving via "
                    "claude default" % errors["GLM-Override"],
                    file=sys.stderr,
                )
        elif model_override in LEGACY_PASSTHROUGH_MODELS:
            print(
                "WARN: model_override=%r has no native execute_prompt routing "
                "branch yet -- falling through to the Claude CLI default, same "
                "as before R-336's audit. Documented, known compatibility shim "
                "(see LEGACY_PASSTHROUGH_MODELS in cex_intent.py); real native "
                "routing is future work, not a new bug." % model_override,
                file=sys.stderr,
            )
        else:
            raise ValueError(
                "execute_prompt: model_override=%r is not recognized by any "
                "routing branch. Recognized: 'ollama/<model>' prefix, "
                "'claude*' prefix, GLM_OPENWEBUI_MODELS=%s, or the documented "
                "LEGACY_PASSTHROUGH_MODELS=%s compatibility set. R-336 closed "
                "the prior silent fall-through to the Claude CLI default -- if "
                "this is a new, intentional model id, add a routing branch (or "
                "extend LEGACY_PASSTHROUGH_MODELS with a documented reason) "
                "instead of relying on silent misroute."
                % (model_override, sorted(GLM_OPENWEBUI_MODELS),
                   sorted(LEGACY_PASSTHROUGH_MODELS))
            )

    # --- [1] Claude CLI (subscription -- included in Max/Pro plan) ---
    try:
        from cex_model_resolver import resolve_model_for_tool
        _cli_model = resolve_model_for_tool("cex_intent", "standard")["model"]
    except Exception:
        _cli_model = "claude-sonnet-4-6"
    if not force_ollama:
        try:
            result = _run_claude_cli_no_tools(
                ["claude", "-p", "--model", _cli_model], prompt, timeout=120)
            if result.returncode == 0 and result.stdout.strip():
                if track_cost:
                    _track_call(
                        provider="claude-cli",
                        model=_cli_model,
                        prompt=prompt,
                        response_text=result.stdout,
                        # R-337 Fix 4: annotate the cost_log entry when this
                        # Claude default call is actually substituting for a
                        # GLM override that was requested but failed above
                        # (errors["GLM-Override"] set) -- "" (no-op) for
                        # every other case (no override, ollama/claude
                        # override, or a LEGACY_PASSTHROUGH id).
                        substituted_from=(
                            model_override if "GLM-Override" in errors else ""
                        ),
                    )
                return result.stdout
            errors["CLI-Claude"] = f"exit {result.returncode}: {result.stderr[:200]}"
        except FileNotFoundError:
            errors["CLI-Claude"] = "claude CLI not in PATH"
        except Exception as e:
            errors["CLI-Claude"] = str(e)[:120]

    # --- [2] Ollama (local, free -- via cex_ollama.py) ---
    try:
        from cex_ollama import OllamaClient
        client = OllamaClient()
        if client.health():
            ollama_model = os.environ.get("CEX_OLLAMA_MODEL", "qwen3:8b")
            resp = client.generate_artifact(
                model=ollama_model,
                prompt=prompt,
            )
            if resp.success and resp.content:
                print(
                    f"  [Ollama] {ollama_model} | {resp.tokens_generated} tokens | "
                    f"{resp.tokens_per_second:.1f} tok/s",
                    file=sys.stderr,
                )
                if track_cost:
                    # Ollama returns real eval_count for output; estimate input
                    _track_call(
                        provider="ollama",
                        model=f"ollama/{ollama_model}",
                        prompt=prompt,
                        response_text=resp.content,
                        input_tokens=0,  # estimate from prompt
                        output_tokens=int(resp.tokens_generated or 0),
                    )
                return resp.content
            if not resp.success:
                errors["Ollama"] = resp.error
        else:
            errors["Ollama"] = "server not running"
    except ImportError:
        errors["Ollama"] = "cex_ollama.py not available"
    except Exception as e:
        errors["Ollama"] = str(e)[:120]

    # --- [3-4] Paid API providers (ONLY if CEX_USE_API=1) ---
    if not allow_paid_api:
        errors["API"] = "Paid APIs disabled (set CEX_USE_API=1 to allow)"
    else:
        try:
            sdk_root = str(Path(__file__).resolve().parent.parent)
            if sdk_root not in sys.path:
                sys.path.insert(0, sdk_root)
            from cex_sdk.models.message import Message as SDKMessage

            # [3] Anthropic API
            try:
                from cex_sdk.models.providers.anthropic import Claude
                model = Claude(id=_cli_model, max_tokens=8000)
                response = model.invoke([SDKMessage(role="user", content=prompt)])
                if response.content:
                    _log_sdk_metrics(response, "Anthropic-API")
                    if track_cost:
                        usage = getattr(response, "response_usage", None)
                        in_tok = int(getattr(usage, "input_tokens", 0) or 0) if usage else 0
                        out_tok = int(getattr(usage, "output_tokens", 0) or 0) if usage else 0
                        _track_call(
                            provider="anthropic-api",
                            model=_cli_model,
                            prompt=prompt,
                            response_text=response.content,
                            input_tokens=in_tok,
                            output_tokens=out_tok,
                        )
                    return response.content
            except Exception as e:
                errors["API-Anthropic"] = str(e)[:120]

            # [4] OpenAI API
            try:
                from cex_sdk.models.providers.openai import GPT
                model = GPT(id="gpt-4o", max_tokens=8000)
                response = model.invoke([SDKMessage(role="user", content=prompt)])
                if response.content:
                    _log_sdk_metrics(response, "OpenAI-API")
                    if track_cost:
                        usage = getattr(response, "response_usage", None)
                        in_tok = int(getattr(usage, "input_tokens", 0) or 0) if usage else 0
                        out_tok = int(getattr(usage, "output_tokens", 0) or 0) if usage else 0
                        _track_call(
                            provider="openai-api",
                            model="gpt-4o",
                            prompt=prompt,
                            response_text=response.content,
                            input_tokens=in_tok,
                            output_tokens=out_tok,
                        )
                    return response.content
            except Exception as e:
                errors["API-OpenAI"] = str(e)[:120]
        except ImportError:
            errors["SDK"] = "cex_sdk not available"

    print("ERROR: No LLM provider available.", file=sys.stderr)
    for provider, err in errors.items():
        print(f"  {provider}: {err}", file=sys.stderr)
    sys.exit(1)


def _log_sdk_metrics(response, provider: str) -> None:
    """Log SDK metrics to stderr (non-blocking)."""
    try:
        usage = response.response_usage
        if usage and (usage.input_tokens or usage.output_tokens):
            tokens = f"in={usage.input_tokens} out={usage.output_tokens}"
            dur = f" {usage.duration:.1f}s" if usage.duration else ""
            print(f"  [SDK {provider}] {tokens}{dur}", file=sys.stderr)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------


def run_intent(
    intent: str,
    kind_override: str | None = None,
    dry_run: bool = True,
    quality: float | None = None,
) -> dict:
    """Full pipeline: intent -> Motor 8F -> builder specs -> governed prompt."""

    # Step 1: Motor 8F -- parse + classify
    parsed = parse_intent(intent, quality_override=quality)

    if kind_override:
        # Override classification with explicit kind
        classified = classify_objects([kind_override])
    else:
        classified = classify_objects(parsed["objects"])

    # Step 2: Fan-out builders
    builder_map = load_builder_map()
    kc_library = load_kc_library()

    functions = fan_out(
        classified=classified,
        intent_lower=intent.lower(),
        quality=parsed["quality"],
        builder_map=builder_map,
        verb_action=parsed["verb_action"],
        kc_library=kc_library,
    )

    plan = generate_output(intent, parsed, classified, functions)

    # Step 3: Find primary kind and its builder
    primary_kind = classified[0]["kind"] if classified else "generic"
    builder_dir = find_builder_dir(primary_kind)

    if not builder_dir:
        print(f"WARNING: Builder not found for kind '{primary_kind}'", file=sys.stderr)
        print("  Tentando fallback: knowledge-card-builder", file=sys.stderr)
        builder_dir = find_builder_dir("knowledge_card")

    # Step 4: Load builder specs
    builder_isos = {}
    if builder_dir:
        builder_isos = load_all_builder_isos(builder_dir, primary_kind)

    # Step 5: Load KC-Domain content
    kc_content = ""
    for fn in plan.get("functions", []):
        if fn["name"] == "INJECT":
            kc_matches = fn.get("kc_injections") or []
            if kc_matches:
                kc_content = load_kc_domain_content(kc_matches)
            break

    # Step 6: Compose governed prompt
    prompt = compose_prompt(
        intent=intent,
        kind=primary_kind,
        builder_isos=builder_isos,
        kc_content=kc_content,
        parsed=parsed,
        plan=plan,
    )

    # Step 7: Execute or dry-run
    result = {
        "intent": intent,
        "kind": primary_kind,
        "builder_dir": str(builder_dir) if builder_dir else None,
        "isos_loaded": list(builder_isos.keys()),
        "kc_injected": bool(kc_content),
        "plan": plan,
        "prompt_tokens": len(prompt.split()),
        "prompt": prompt,
    }

    if not dry_run:
        print(f"\n>>> Executing prompt ({result['prompt_tokens']} words)...\n", file=sys.stderr)
        response = execute_prompt(prompt)
        result["response"] = response
        result["executed"] = True
    else:
        result["executed"] = False

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="cex_intent.py -- Natural language to governed prompt (The Steering Wheel)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cex_intent.py "cria knowledge card sobre RAG"
  python cex_intent.py "cria agente de vendas" --dry-run
  python cex_intent.py "melhora eval de qualidade" --execute
  python cex_intent.py "cria agent" --kind agent
  python cex_intent.py --list-kinds
        """,
    )
    parser.add_argument("intent", nargs="?", help="Natural language intent string")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show composed prompt without executing (default)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Send composed prompt to LLM and show response",
    )
    parser.add_argument("--kind", help="Override kind classification (e.g. agent, knowledge_card)")
    parser.add_argument("--quality", type=float, help="Quality target override (default: 9.0)")
    parser.add_argument("--list-kinds", action="store_true", help="List all available CEX kinds")
    parser.add_argument(
        "--json", action="store_true", help="Output full result as JSON (plan + prompt)"
    )
    parser.add_argument("--output", "-o", help="Write prompt to file instead of stdout")

    args = parser.parse_args()

    if args.list_kinds:
        list_kinds()
        return

    if not args.intent:
        parser.print_help()
        sys.exit(1)

    dry_run = not args.execute

    result = run_intent(
        intent=args.intent,
        kind_override=args.kind,
        dry_run=dry_run,
        quality=args.quality,
    )

    # Output
    if args.json:
        # Full JSON output (exclude prompt body for readability unless piped)
        output = {k: v for k, v in result.items() if k != "prompt"}
        output["prompt_preview"] = (
            result["prompt"][:500] + "..." if len(result["prompt"]) > 500 else result["prompt"]
        )
        print(json.dumps(output, indent=2, ensure_ascii=False, default=str))
        return

    # Header
    print(f"\n{'=' * 70}")
    print("  CEX Intent -> Governed Prompt")
    print(f"{'=' * 70}")
    print(f"  Intent:    {result['intent']}")
    print(f"  Kind:      {result['kind']}")
    print(f"  Builder:   {result['builder_dir'] or 'NONE'}")
    print(f"  specs:      {len(result['isos_loaded'])} loaded: {', '.join(result['isos_loaded'])}")
    print(f"  KC Domain: {'injected' if result['kc_injected'] else 'none matched'}")
    print(f"  Tokens:    ~{result['prompt_tokens']} words")
    print(f"  Mode:      {'EXECUTE' if result['executed'] else 'DRY-RUN'}")

    plan = result["plan"]
    print(f"  Builders:  {plan['total_builders']} active, ~{plan['estimated_tokens']} est. tokens")
    if plan.get("warnings"):
        for w in plan["warnings"]:
            print(f"  ! {w}")
    print(f"{'=' * 70}\n")

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(result["prompt"], encoding="utf-8")
        print(f"  Prompt written to: {out_path}")
    else:
        if result.get("executed") and result.get("response"):
            print("--- LLM RESPONSE ---\n")
            print(result["response"])
        else:
            print("--- GOVERNED PROMPT ---\n")
            print(result["prompt"])
            print(f"\n--- END ({result['prompt_tokens']} words) ---")


if __name__ == "__main__":
    try:
        from cex_agent_io import wrap_main

        def _main_wrapper(argv):
            sys.argv = [sys.argv[0]] + argv
            main()
            return 0

        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_intent"))
    except ImportError:
        main()
