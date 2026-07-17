#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cex_crew_runner.py -- Crew Runner: Lightweight DAG Executor for CEX

LangGraph-inspired state machine that executes CEX builder plans produced
by Motor 8F. Zero external deps beyond PyYAML (optional).

Design principles (from CREW_PATTERNS_RESEARCH.md Section 5):
  - Explicit DAG (not full LangGraph/CrewAI)
  - Typed state flow (BuilderOutput, RunState)
  - JSON plan as input (Motor 8F output)
  - Fixed token budget per builder (~7500 tokens for specs)
  - Graceful degradation: score >= 7.0 -> advance, < 7.0 -> retry, exhausted -> degrade

Modes:
  --dry-run  (DEFAULT): Generate prompts, save to files. No LLM calls.
  --execute:            Call LLM via claude CLI (subscription), apply quality gates.

Usage:
  python cex_crew_runner.py --plan plan.json --output-dir out/
  python cex_crew_runner.py --plan plan.json --step 2 --output-dir out/
  python cex_crew_runner.py --plan plan.json --execute --output-dir out/

Full pipeline:
  python cex_8f_motor.py --intent "cria agente de vendas" --output /tmp/plan.json
  python cex_crew_runner.py --plan /tmp/plan.json --output-dir /tmp/crew_out/
"""

import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"): sys.stderr.reconfigure(encoding="utf-8")

import argparse
import json
import os
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, NamedTuple

try:
    import yaml  # noqa: F401 -- optional, for future config loading
except ImportError:
    yaml = None

try:
    from cex_secretariat import select_context as _secretariat_context
    _SECRETARIAT_AVAILABLE = True
except ImportError:
    _SECRETARIAT_AVAILABLE = False


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CEX_ROOT = Path(__file__).resolve().parent.parent
ROOT = CEX_ROOT  # alias used by fork/inline execution paths
BUILDER_DIR = CEX_ROOT / "archetypes" / "builders"
BUILDER_MAX_BYTES = 30 * 1024  # 30KB total budget for builder spec injection
DEFAULT_QUALITY_GATE = 7.0
MAX_RETRIES = 2
# Short alias = subscription auth. Full ID = API credits (may be depleted).
LLM_MODEL = "sonnet"
LLM_MAX_TOKENS = 8000
FORK_OUTPUT_DIR = CEX_ROOT / ".cex" / "temp" / "fork_outputs"

# R-196: fallback-only now (see _parse_md_frontmatter) -- the primary path uses
# cex_shared's line-anchored close-fence scan. Kept as the degrade path so this
# module still parses frontmatter in a bare environment where cex_shared cannot
# be imported (e.g. PyYAML missing; cex_shared.py hard-imports yaml at module
# level, unlike this file's own optional top-level `try: import yaml` above).
_FM_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def _track_crew_call(provider: str, model: str, prompt: str,
                     response_text: str, builder_id: str = "",
                     input_tokens: int = 0, output_tokens: int = 0) -> None:
    """Best-effort cost tracking for crew fork calls (Bug D fix).

    Char/4 fallback when usage is not surfaced. Honors CEX_TRACK_COST=0.
    """
    if os.environ.get("CEX_TRACK_COST", "1") == "0":
        return
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from cex_cost_tracker import record as _cost_record  # type: ignore
        if input_tokens <= 0:
            input_tokens = max(1, len(prompt) // 4)
        if output_tokens <= 0:
            output_tokens = max(1, len(response_text or "") // 4)
        ctx = os.environ.get("CEX_COST_CONTEXT", "crew") or "crew"
        if builder_id:
            ctx = f"crew:{builder_id}"
        _cost_record(
            provider=provider,
            model=model,
            input_tokens=int(input_tokens),
            output_tokens=int(output_tokens),
            mission=os.environ.get("CEX_MISSION", "") or ctx,
            nucleus=os.environ.get("CEX_NUCLEUS", "n07"),
            preflight_used=False,
        )
    except Exception:
        pass


def _parse_md_frontmatter(text: str) -> dict:
    """YAML frontmatter parser.

    Prefers PyYAML when available (handles nested mappings like budget: {tokens, usd}).
    Falls back to a minimal parser (scalar keys + simple lists only) when PyYAML
    is missing, so callers never crash in bare environments.

    R-196: the frontmatter span is found via cex_shared's line-anchored
    close-fence scan (_frontmatter_close_index) -- immune to a '---' that
    shows up as a SUBSTRING inside a quoted value or a markdown table divider,
    which the old non-greedy `(.*?)\\n---` regex (_FM_RE) mistook for the
    close. Degrades to that original regex ONLY if cex_shared itself cannot
    be imported (e.g. PyYAML missing) -- this function keeps working in a
    bare, PyYAML-less environment either way.
    """
    if not text.startswith("---"):
        return {}
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from cex_shared import _frontmatter_close_index
        end = _frontmatter_close_index(text)
        if end < 0:
            return {}
        raw = text[3:end]
    except Exception:
        m = _FM_RE.match(text)
        if not m:
            return {}
        raw = m.group(1)
    try:
        import yaml  # type: ignore
        loaded = yaml.safe_load(raw)
        return loaded if isinstance(loaded, dict) else {}
    except Exception:
        pass
    fm: dict = {}
    key = None
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line.startswith("  - ") and key:
            val = line[4:].strip().strip('"').strip("'")
            if not isinstance(fm.get(key), list):
                fm[key] = []
            fm[key].append(val)
        elif ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            k = k.strip()
            v = v.strip()
            key = k
            if not v:
                fm[k] = []
            else:
                fm[k] = v.strip('"').strip("'")
    return fm


_SELF_ASSESS_RE = re.compile(r"(?:quality|score)[\s:]*(\d+\.?\d*)")


def _parse_self_assessed_quality(content: str) -> tuple:
    """Parse a builder's free-text self-assessment for a `quality: X.X` /
    `score: X.X` line. Returns (score, parsed).

    R-193 (SHOKUNIN, BLOCKING) fix: the prior code at both call sites defaulted
    an UNMATCHED self-assessment to 7.0 -- which equals DEFAULT_QUALITY_GATE, so
    a builder that never emitted a parseable quality line SILENTLY PASSED the
    quality gate. This is the third file-instance of the exact self-certification
    disease already killed in cex_score.py/cex_council.py (R-173/R-174): a bare
    regex over an LLM's own free-text self-report, with no-match treated as a
    pass. The fix: no-match returns parsed=False and an explicit NON-PASSING
    score (0.0, below any realistic gate) so the caller's existing retry/degrade
    accounting (score < gate -> retry -> degrade after MAX_RETRIES) takes over
    instead of the run being silently waved through. Callers should also record
    `parsed` in metadata so a downstream consumer can tell "genuinely scored 0.0"
    apart from "self-assessment missing".
    """
    m = _SELF_ASSESS_RE.search(content.lower())
    if m:
        return float(m.group(1)), True
    return 0.0, False


def _kill_tree(pid: int) -> None:
    """Kill a process and ALL its descendants (Windows: taskkill /T; POSIX: killpg).

    R-198 (SHOKUNIN) fix: ported verbatim (same house pattern) from
    cex_intent.py's `_kill_tree` / cex_quota_check._kill_tree. Without this, a
    `claude -p` call that outlives its subprocess timeout leaves an orphaned
    agentic session (plus its node.exe/MCP children on Windows) running in the
    background -- free to keep writing to disk minutes after the caller has
    already reported failure and moved on. Same root-cause class as R-156.
    """
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)],
                            capture_output=True, timeout=10)
        else:
            import signal as _signal
            os.killpg(os.getpgid(pid), _signal.SIGKILL)
    except Exception:
        pass


def _run_claude_cli(args: list, prompt: str, timeout: int = 120, cwd: str = None):
    """Run a `claude -p ...` subprocess with FAIL-CLOSED tree-kill on timeout.

    R-198 (SHOKUNIN) fix: ported verbatim (same house pattern) from
    cex_intent.py's `_run_claude_cli`. Plain `subprocess.run(..., timeout=N)`
    only signals the immediate child -- on Windows that child is `claude.cmd`,
    which has already forked its own node.exe (+ MCP) descendants by the time
    the timeout fires. `process.kill()` on TimeoutExpired never reaches those
    descendants, so they keep running as an orphaned agentic session with live
    filesystem write access. This runs the CLI in its own process group
    (Windows: CREATE_NEW_PROCESS_GROUP; POSIX: setsid) so `_kill_tree` can reap
    the WHOLE tree the instant the timeout fires.

    Returns a `subprocess.CompletedProcess`-shaped object (returncode/stdout/
    stderr) -- a drop-in replacement for the prior `subprocess.run(...)` call
    sites. Re-raises `subprocess.TimeoutExpired` AFTER the tree is dead, so
    existing `except Exception` callers keep working unchanged.
    """
    creationflags = 0
    preexec_fn = None
    if sys.platform == "win32":
        creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    else:
        preexec_fn = os.setsid
    popen_kwargs = dict(
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", creationflags=creationflags,
    )
    if cwd is not None:
        popen_kwargs["cwd"] = cwd
    if preexec_fn is not None:
        popen_kwargs["preexec_fn"] = preexec_fn
    proc = subprocess.Popen(args, **popen_kwargs)
    try:
        stdout, stderr = proc.communicate(input=prompt, timeout=timeout)
        return subprocess.CompletedProcess(args, proc.returncode, stdout, stderr)
    except subprocess.TimeoutExpired:
        _kill_tree(proc.pid)
        try:
            proc.communicate(timeout=5)
        except Exception:
            pass
        raise


# ---------------------------------------------------------------------------
# Prompt Layers (compiled artifacts from pillar directories)
# ---------------------------------------------------------------------------
_prompt_layers = None


def _get_prompt_layers():
    """Get PromptLayers singleton (lazy import)."""
    global _prompt_layers
    if _prompt_layers is None:
        try:
            from cex_prompt_layers import get_layers
            _prompt_layers = get_layers()
        except ImportError:
            _prompt_layers = None
    return _prompt_layers


# 8F functions that receive guardrails (write-capable phases)
_GUARDRAIL_FUNCTIONS = {"CALL", "PRODUCE", "COLLABORATE"}
# 8F functions that receive verification protocol (quality gate)
_VERIFICATION_FUNCTIONS = {"GOVERN"}

# Compaction and memory extract thresholds
COMPACT_TRIGGER_RATIO = 0.85  # trigger compaction at 85% context budget
MEMORY_EXTRACT_INTERVAL = 5   # extract memories every N builder executions
_execution_counter = 0


# ---------------------------------------------------------------------------
# Wire 6: Context Compaction Trigger
# ---------------------------------------------------------------------------


def check_compaction_needed(prompt_text: str, max_tokens: int = 8192) -> dict:
    """Check if context compaction should be triggered.

    Returns: {"needed": bool, "usage_ratio": float, "skill_body": str}
    The caller decides whether to compact; this just checks and provides the skill.
    """
    try:
        from cex_token_budget import count_tokens
        current_tokens = count_tokens(prompt_text)
    except ImportError:
        # Fallback: ~1.3 tokens per word
        current_tokens = int(len(prompt_text.split()) * 1.3)

    ratio = current_tokens / max_tokens if max_tokens > 0 else 0

    result = {"needed": False, "usage_ratio": ratio, "skill_body": ""}

    if ratio >= COMPACT_TRIGGER_RATIO:
        result["needed"] = True
        layers = _get_prompt_layers()
        if layers:
            result["skill_body"] = layers.get("p04_skill_compact")

    return result


# ---------------------------------------------------------------------------
# Wire 7: Memory Extract Trigger
# ---------------------------------------------------------------------------


def check_memory_extract_needed() -> dict:
    """Check if background memory extraction should run.

    Returns: {"needed": bool, "skill_body": str, "counter": int}
    Called after each builder execution. Triggers every N executions.
    """
    global _execution_counter
    _execution_counter += 1

    result = {
        "needed": False,
        "skill_body": "",
        "counter": _execution_counter,
    }

    if _execution_counter % MEMORY_EXTRACT_INTERVAL == 0:
        result["needed"] = True
        layers = _get_prompt_layers()
        if layers:
            result["skill_body"] = layers.get("p04_skill_memory_extract")

    return result


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------


@dataclass
class BuilderOutput:
    """Result of a single builder execution."""

    builder_id: str
    content: str = ""
    quality_score: float = 0.0
    metadata: dict = field(default_factory=dict)
    status: str = "pending"  # pending | complete | degraded | failed


@dataclass
class RunState:
    """Mutable state that flows through the execution pipeline."""

    intent: str
    plan: dict
    outputs: dict = field(default_factory=dict)  # builder_id -> BuilderOutput
    current_step: int = 0
    retry_counts: dict = field(default_factory=dict)  # builder_id -> int
    warnings: list = field(default_factory=list)
    started_at: str = ""
    completed_at: str = ""


# ---------------------------------------------------------------------------
# Builder Context Loader
# ---------------------------------------------------------------------------

# Priority order for builder spec file types within a builder directory
_SPEC_PRIORITY = [
    "manifest",
    "instruction",
    "knowledge",
    "quality",
    "schema",
    "example",
    "config",
    "template",
]


def _iso_sort_key(filepath: Path) -> int:
    """Sort builder spec files by content priority (manifest first, examples last)."""
    name = filepath.name.lower()
    for i, kw in enumerate(_SPEC_PRIORITY):
        if kw in name:
            return i
    return len(_SPEC_PRIORITY)


def load_builder_context(builder_id: str, builder_dir: Path = BUILDER_DIR) -> str:
    """Load builder spec files (bld_*.md) for a builder.

    Strategy: Try SkillLoader first (handles sort, shared skills, conditionals).
    Fallback: manual glob (original behavior).
    Budget: 30KB max.
    """
    # --- T01: SkillLoader path (preferred) ---
    try:
        from cex_skill_loader import SkillLoader
        sl = SkillLoader()
        kind = builder_id.replace("-builder", "")
        isos = sl.load_builder(kind)
        if isos:
            sections = []
            total_bytes = 0
            for iso in isos:
                block = iso.get_prompt()
                block_bytes = len(block.encode("utf-8"))
                if total_bytes + block_bytes > BUILDER_MAX_BYTES:
                    sections.append(f"\n[... truncated at {BUILDER_MAX_BYTES // 1024}KB budget ...]")
                    break
                sections.append(f"### {iso.name}")
                sections.append(block.strip())
                sections.append("")
                total_bytes += block_bytes
            if sections:
                return "\n".join(sections)
    except Exception:
        pass  # D1: graceful fallback

    # --- Fallback: manual glob (original) ---
    builder_path = builder_dir / builder_id
    if not builder_path.exists():
        return f"[Builder '{builder_id}' not found at {builder_path}]"

    md_files = sorted(builder_path.glob("bld_*.md"), key=_iso_sort_key)
    if not md_files:
        md_files = sorted(builder_path.glob("*.md"), key=_iso_sort_key)

    if not md_files:
        return f"[No builder spec files found for builder '{builder_id}']"

    sections = []
    total_bytes = 0

    for f in md_files:
        try:
            content = f.read_text(encoding="utf-8")
        except Exception:
            continue

        content_bytes = len(content.encode("utf-8"))
        if total_bytes + content_bytes > BUILDER_MAX_BYTES:
            sections.append(f"\n[... truncated at {BUILDER_MAX_BYTES // 1024}KB budget ...]")
            break

        sections.append(f"### {f.name}")
        sections.append(content.strip())
        sections.append("")
        total_bytes += content_bytes

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Prompt Composer
# ---------------------------------------------------------------------------


def _load_builder_memories(builder_id: str, intent: str) -> str:
    """Load relevant memories for a builder.

    T07: Enriched with memory type labels + freshness caveats.
    """
    try:
        from cex_memory import scan_builder_memories
        from cex_memory_select import (format_memory_injection,
                                       select_relevant_memories)

        headers = scan_builder_memories(builder_id)
        if not headers:
            return ""

        selected = select_relevant_memories(
            query=intent,
            memories=headers,
            builder_id=builder_id,
            top_k=5,
            use_cache=True,
        )
        if not selected:
            return ""

        base = format_memory_injection(selected, total_observations=len(headers))

        # --- T07: Enrich with type + freshness ---
        try:
            from cex_memory_age import memory_freshness_tag
            enrichments = []
            for s in selected:
                tags = []
                if hasattr(s, "type") and s.type:
                    tags.append(f"type={s.type}")
                if hasattr(s, "path") and s.path:
                    import os
                    try:
                        tag = memory_freshness_tag(os.path.getmtime(s.path))
                        tags.append(tag)
                    except Exception:
                        pass
                if tags:
                    enrichments.append(f"  [{', '.join(tags)}]")
            if enrichments:
                base += "\n" + "\n".join(enrichments)
        except Exception:
            pass  # enrichment is optional

        return base
    except Exception:
        return ""


def _load_relevant_kcs(intent: str, parsed: dict) -> str:
    """Load KCs relevant to the current intent via pure Python (local TF-IDF).

    Uses two strategies (zero external dependencies):
    1. feeds_kinds: find KCs that explicitly feed the target kind (motor KC library)
    2. semantic search: TF-IDF similarity via cex_retriever (local index)

    Falls back gracefully if retriever index not built.
    Returns formatted injection block or empty string.
    """
    kcs = []

    # Strategy 1: KCs that feed this kind (explicit link via motor KC library)
    target_kind = ""
    if isinstance(parsed.get("object"), list):
        target_kind = parsed["object"][0] if parsed["object"] else ""
    elif isinstance(parsed.get("object"), str):
        target_kind = parsed["object"]
    target_kind = target_kind.replace("-", "_")

    if target_kind:
        try:
            from cex_8f_motor import load_kc_library, lookup_kcs_for_kind
            kc_library = load_kc_library()
            pillar = parsed.get("pillar", "P01")
            matches = lookup_kcs_for_kind(kc_library, target_kind, pillar)
            for m in matches[:3]:
                kcs.append({
                    "id": m.get("id", ""),
                    "title": m.get("title", m.get("id", "?")),
                    "file_path": m.get("path", ""),
                    "domain": "",
                    "tldr": "",
                    "similarity": 0,
                })
        except Exception:
            pass

    # Strategy 2: TF-IDF semantic search (pure Python, no external services)
    try:
        from cex_retriever import find_similar
        from cex_retriever import load_index as load_retriever_index
        idx = load_retriever_index()
        if idx:
            results = find_similar(intent, index=idx, top_k=3)
            seen_ids = {kc["id"] for kc in kcs}
            for r in results:
                rid = r.get("id", "")
                if rid and rid not in seen_ids:
                    seen_ids.add(rid)
                    kcs.append({
                        "id": rid,
                        "title": r.get("title", r.get("id", "?")),
                        "file_path": r.get("path", ""),
                        "domain": r.get("kind", ""),
                        "tldr": r.get("tldr", ""),
                        "similarity": r.get("score", 0),
                    })
    except Exception:
        pass

    if not kcs:
        return ""

    # Format injection block (cap at 5 KCs, ~2K tokens total)
    parts = ["## Relevant Knowledge Cards (auto-retrieved, pure Python TF-IDF)"]
    parts.append("Use these as domain context. Cite specific facts when relevant.\n")

    for kc in kcs[:5]:
        title = kc.get("title", kc.get("id", "?"))
        tldr = kc.get("tldr", "")
        domain = kc.get("domain", "")
        sim = kc.get("similarity", 0)
        path = kc.get("file_path", "")
        sim_str = f" (sim={sim:.2f})" if sim else ""

        parts.append(f"### KC: {title}{sim_str}")
        if domain:
            parts.append(f"Domain: {domain}")
        if tldr:
            parts.append(f"TLDR: {tldr}")

        # Load actual KC body (truncated) for rich context
        try:
            full_path = Path(__file__).resolve().parent.parent / path
            if full_path.exists():
                content = full_path.read_text(encoding="utf-8")
                # Extract body after frontmatter
                fm_end = content.find("---", 3)
                if fm_end > 0:
                    body = content[fm_end + 3:].strip()[:800]
                    parts.append(body)
        except Exception:
            pass

        parts.append("")

    return "\n".join(parts)


def compose_prompt(
    builder_id: str,
    function_name: str,
    intent: str,
    parsed: dict,
    quality_target: float,
    state: RunState,
    builder_dir: Path = BUILDER_DIR,
    retry_feedback: str = "",
) -> str:
    """Compose full prompt for a builder: specs + intent + prior outputs.

    Each builder gets:
    1. Header with execution context
    2. Builder spec files (capped at 30KB)
    3. Relevant prior outputs (from earlier pipeline steps)
    4. Retry feedback (if retrying after quality gate failure)
    5. Execution instructions
    6. Sin lens injection (identity lens from nucleus_sins.yaml)
    """
    parts = []

    # --- Sin Lens Injection (from nucleus_sins.yaml) ---
    try:
        from cex_theme import get_prompt_injection
        nucleus = os.environ.get("CEX_NUCLEUS", "n03").lower()
        sin_injection = get_prompt_injection(nucleus)
        if sin_injection:
            parts.append("## Your Identity Lens")
            parts.append(sin_injection)
            parts.append("")
    except Exception:
        pass  # sin injection is additive, never blocks

    # --- Prompt Layers (Wire 1-4: identity + behavioral + action + guardrails) ---
    layers = _get_prompt_layers()
    if layers:
        # Wire 1: Core identity (loaded FIRST, before everything)
        identity_body = layers.get("p03_sp_cex_core_identity")
        if identity_body:
            # Resolve {{INCLUDE}} directives
            for inc_id in ["p03_ins_doing_tasks", "p03_ins_action_protocol"]:
                inc_body = layers.get(inc_id)
                if inc_body:
                    identity_body = identity_body.replace(
                        "{{INCLUDE " + inc_id + "}}", inc_body
                    )
            # Strip remaining unresolved {{...}} placeholders
            identity_body = re.sub(r"\{\{[A-Z_]+\}\}", "[runtime]", identity_body)
            parts.append("## CEX Agent Identity")
            parts.append(identity_body)
            parts.append("")

        # Wire 4: Guardrails (for write-capable functions)
        if function_name.upper() in _GUARDRAIL_FUNCTIONS:
            guardrail_ids = layers.by_kind("guardrail")
            if guardrail_ids:
                parts.append("## Safety Guardrails (auto-injected)")
                for gid in guardrail_ids:
                    g_body = layers.get(gid)
                    g_meta = layers.get_meta(gid)
                    if g_body:
                        title = g_meta.get("title", gid)
                        severity = g_meta.get("severity", "?")
                        enforcement = g_meta.get("enforcement", "?")
                        parts.append(f"### {title} [severity={severity}, enforcement={enforcement}]")
                        parts.append(g_body)
                        parts.append("")

        # Wire 5: Verification protocol (for GOVERN function)
        if function_name.upper() in _VERIFICATION_FUNCTIONS:
            verify_body = layers.get("p03_sp_verification_agent")
            if verify_body:
                parts.append("## Verification Protocol (F7 GOVERN)")
                parts.append(verify_body)
                parts.append("")
            verify_skill = layers.get("p04_skill_verify")
            if verify_skill:
                parts.append("## Verification Skill")
                parts.append(verify_skill)
                parts.append("")

    # --- Wire: Prompt Compiler (F1 CONSTRAIN injection) ---
    if layers and function_name.upper() == "CONSTRAIN":
        pc_body = layers.get("p03_pc_cex_universal")
        if pc_body:
            parts.append("## Prompt Compiler (Intent Resolution -- F1 CONSTRAIN)")
            parts.append(pc_body)
            parts.append("")

    # --- Header ---
    parts.append("# CEX Crew Runner -- Builder Execution")
    parts.append(f"**Builder**: `{builder_id}`")
    parts.append(f"**Function**: {function_name}")
    parts.append(f"**Intent**: {intent}")
    parts.append(f"**Quality Target**: >= {quality_target}")
    parts.append(f"**Timestamp**: {datetime.now().isoformat()}")
    parts.append("")

    # --- Intent Context ---
    parts.append("## Intent Context")
    parts.append(f"- **Verb**: {parsed.get('verb', 'N/A')}")
    obj = parsed.get("object", "N/A")
    if isinstance(obj, list):
        parts.append(f"- **Objects**: {', '.join(obj)}")
    else:
        parts.append(f"- **Object**: {obj}")
    parts.append(f"- **Domain**: {parsed.get('domain', 'N/A')}")
    parts.append(f"- **Multi-object**: {parsed.get('multi_object', False)}")
    parts.append("")

    # --- Builder Spec Context ---
    parts.append("## Builder Context (Spec Files)")
    context = load_builder_context(builder_id, builder_dir)
    parts.append(context)
    parts.append("")

    # --- Brand Context Injection ---
    # If brand_config.yaml exists, inject relevant brand variables
    brand_config_path = CEX_ROOT / ".cex" / "brand" / "brand_config.yaml"
    if brand_config_path.exists():
        try:
            from brand_inject import flatten, load_brand_config
            brand_cfg = load_brand_config(brand_config_path)
            if brand_cfg:
                flat = flatten(brand_cfg)
                # Filter out placeholders (still {{...}})
                real = {k: v for k, v in flat.items()
                        if not str(v).startswith("{{") and v}
                if real:
                    parts.append("## Brand Context (auto-injected from .cex/brand/brand_config.yaml)")
                    for k, v in sorted(real.items()):
                        if not k.startswith(("identity.", "archetype.", "voice.",
                                             "audience.", "visual.", "positioning.",
                                             "monetization.")):
                            parts.append(f"- {k}: {v}")
                    parts.append("")
        except ImportError:
            pass  # brand_inject not available, skip silently

    # ================================================================
    # F3 INJECT: Synapse 8-Layer Context Envelope (A1 pattern)
    #
    # Canonical ordering ensures deterministic prompt structure:
    #   L0 Rules     -- .claude/rules/ (already injected above via Wire 1)
    #   L1 Global    -- brand config, nucleus identity (already injected above)
    #   L2 Agent     -- builder specs (already injected above)
    #   L3 Workflow   -- prior outputs from earlier pipeline steps
    #   L4 Task      -- intent context, retry feedback
    #   L5 (reserved) -- user session context (future)
    #   L6 Retrieval -- KCs, memory, auto-retrieved context
    #   L7 Commands  -- execution instructions (injected below)
    # ================================================================

    # --- L6 Retrieval: Knowledge Cards ---
    kc_block = _load_relevant_kcs(intent, parsed)
    if kc_block:
        parts.append("## [L6] Knowledge Card Context")
        parts.append(kc_block)

    # --- L6 Retrieval: Secretariat Context (LLM-ranked) ---
    if _SECRETARIAT_AVAILABLE:
        try:
            kind = parsed.get("object", "")
            if isinstance(kind, list):
                kind = kind[0] if kind else ""
            kind = kind.replace("-", "_")
            if kind:
                sec_ctx = _secretariat_context(kind, intent)
                if sec_ctx:
                    parts.append("## [L6] Secretariat Context (ranked by relevance)")
                    for item in sec_ctx[:3]:
                        parts.append("- %s: %s (relevance: %.2f)" % (
                            item.get("type", "unknown"),
                            item.get("path", ""),
                            item.get("relevance", 0)))
                    parts.append("")
        except Exception:
            pass

    # --- L6 Retrieval: Builder Memory ---
    memory_block = _load_builder_memories(builder_id, intent)
    if memory_block:
        parts.append("## [L6] Builder Memory")
        parts.append(memory_block)

    # --- L6 Retrieval: Auto-Retrieved Context (F5 CALL outputs) ---
    if hasattr(state, "tool_results") and state.tool_results.get("enrichment_text"):
        parts.append("## [L6] Auto-Retrieved Context (F5 CALL)")
        parts.append(state.tool_results["enrichment_text"])
        parts.append("")

    # --- L3 Workflow: Prior Outputs ---
    # Only inject outputs from completed earlier steps (not current function)
    prior = {
        bid: out
        for bid, out in state.outputs.items()
        if out.status in ("complete", "degraded")
        and out.content
        and not out.content.startswith("[DRY-RUN]")
    }
    if prior:
        parts.append("## [L3] Prior Builder Outputs")
        parts.append("These outputs were produced by earlier pipeline steps.")
        parts.append("Use them as context -- do not repeat their work.")
        parts.append("")
        for bid, out in prior.items():
            parts.append(f"### {bid} (score: {out.quality_score:.1f})")
            content = out.content
            if len(content) > 2000:
                content = content[:2000] + "\n\n[... truncated to 2KB ...]"
            parts.append(content)
            parts.append("")

    # --- L4 Task: Retry Feedback ---
    if retry_feedback:
        parts.append("## [L4] Retry Feedback")
        parts.append("Your previous attempt did not pass the quality gate.")
        parts.append(retry_feedback)
        parts.append("")

    # --- L7 Commands: Execution Instructions ---
    parts.append("## [L7] Execution Instructions")
    parts.append(
        f"1. You are executing builder `{builder_id}` for pipeline function `{function_name}`."
    )
    parts.append("2. Follow the builder's spec instructions precisely.")
    parts.append("3. Generate the complete output artifact.")
    parts.append(
        f"4. Quality target: >= {quality_target} (no filler, no repetition, no platitudes)."
    )
    parts.append("5. At the end, self-assess with: `quality: X.X`")
    parts.append("")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Crew Runner
# ---------------------------------------------------------------------------


class CrewRunner:
    """Lightweight DAG executor for CEX builder plans."""

    def __init__(self, plan: dict, cex_root: Path = CEX_ROOT):
        self.plan = plan
        self.cex_root = cex_root
        self.builder_dir = cex_root / "archetypes" / "builders"
        self.intent = plan.get("intent", "")
        self.parsed = plan.get("parsed", {})
        self.functions = plan.get("functions", [])
        self.quality_target = self.parsed.get("quality", 9.0)

    # ------------------------------------------------------------------
    # Composable-crew loader (Phase 2 of crew-wiring mini-wave)
    # ------------------------------------------------------------------
    @classmethod
    def load_from_crew_template(
        cls,
        crew_path: Path,
        charter_path: Path | None = None,
        cex_root: Path = CEX_ROOT,
    ) -> dict:
        """Parse a crew_template.md + optional team_charter.md into a runnable plan.

        crew_template.md shape (from archetypes/builders/crew-template-builder):
          frontmatter: crew_name, purpose, process, handoff_protocol_id, ...
          body `## Roles` table: | Role | Role Assignment ID | Reason |

        Each `Role Assignment ID` (e.g. `p02_ra_researcher.md`) is resolved by:
          1. sibling dir of crew file (e.g. N02_marketing/P12_orchestration/)
          2. cex_root glob N0*/P12_orchestration/<id>
          3. cex_root glob N0*/P02_model/<id>
          4. cex_root glob P02_*/**/<id>

        The role_assignment's frontmatter `agent_id` points to a builder
        or nucleus agent -- that becomes a builder entry in the plan.

        Returns a plan dict compatible with CrewRunner.run().
        """
        import re as _re

        # --- 1. Parse crew_template ---
        text = crew_path.read_text(encoding="utf-8", errors="replace")
        fm = _parse_md_frontmatter(text)
        body = text.split("---", 2)[-1] if text.startswith("---") else text

        crew_name = fm.get("crew_name", crew_path.stem)
        process = (fm.get("process") or "sequential").strip().lower()
        purpose = fm.get("purpose", f"Execute crew {crew_name}")
        handoff_proto = fm.get("handoff_protocol_id", "a2a-task")

        # R-172 (optional, additive): a crew_template MAY declare a named
        # speaker_selection strategy and/or a composable termination tree --
        # see the CONDITION_TABLE/STRATEGY_TABLE module comment further down
        # this file (just above CrewControlPlaneRunner) for the full shape and
        # the degrade-never contract. Read here as raw dicts; validated and
        # consumed by CrewControlPlaneRunner. Stored into crew_meta ONLY when
        # present AND dict-shaped (never a None placeholder) -- see step 5
        # below: this is what keeps a crew_template lacking these blocks
        # byte-identical to the pre-R-172 plan shape.
        speaker_selection_fm = fm.get("speaker_selection")
        termination_fm = fm.get("termination")

        # --- 2. Parse `## Roles` table ---
        roles: list[dict] = []
        in_roles = False
        for line in body.splitlines():
            low = line.strip().lower()
            if low.startswith("## "):
                in_roles = low.startswith("## roles")
                continue
            if not in_roles:
                continue
            if not line.strip().startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 3:
                continue
            # skip header + separator rows
            if cells[0].lower() in ("role", "---", ":---"):
                continue
            if _re.match(r"^[-: ]+$", cells[0]):
                continue
            roles.append(
                {"role_name": cells[0], "assignment_id": cells[1], "reason": cells[2]}
            )

        if not roles:
            raise ValueError(
                f"crew_template {crew_path.name} has no `## Roles` rows -- "
                "cannot build plan"
            )

        # --- 3. Resolve each role_assignment.md ---
        resolved: list[dict] = []
        search_dirs = [
            crew_path.parent,
            *sorted((cex_root).glob("N0*/crews")),
            *sorted((cex_root / "N00_genesis").glob("P02_*")),
        ]
        for role in roles:
            aid = role["assignment_id"].strip()
            # strip template placeholder braces if any
            aid = _re.sub(r"\{\{.*?\}\}", "", aid).strip()
            if not aid or aid.startswith("<!--"):
                continue
            ra_path = None
            for d in search_dirs:
                candidate = d / aid
                if candidate.exists():
                    ra_path = candidate
                    break
                # glob fallback for pillar subdirs
                matches = list(d.rglob(aid)) if d.is_dir() else []
                if matches:
                    ra_path = matches[0]
                    break
            ra_fm: dict = {}
            agent_id = None
            if ra_path and ra_path.exists():
                ra_text = ra_path.read_text(encoding="utf-8", errors="replace")
                ra_fm = _parse_md_frontmatter(ra_text)
                agent_id = ra_fm.get("agent_id")
            # fallback: derive agent from role_name
            if not agent_id:
                agent_id = (
                    ra_fm.get("role_name", role["role_name"])
                    .lower()
                    .replace(" ", "-")
                    + "-builder"
                )
            resolved.append(
                {
                    "role_name": role["role_name"],
                    "assignment_id": aid,
                    "assignment_path": str(ra_path.resolve().relative_to(cex_root.resolve()))
                    if ra_path
                    else None,
                    "agent_id": agent_id,
                    "goal": ra_fm.get("goal", ""),
                    "backstory": ra_fm.get("backstory", ""),
                    "tools": ra_fm.get("tools", []),
                }
            )

        # --- 4. Optional charter merge ---
        charter_fm: dict = {}
        if charter_path and charter_path.exists():
            charter_fm = _parse_md_frontmatter(
                charter_path.read_text(encoding="utf-8", errors="replace")
            )

        # --- 5. Build plan.functions ---
        # sequential -> one step per role (ordered)
        # hierarchical -> one step, manager first then workers parallel
        # consensus -> one step, all parallel
        parallel = process != "sequential"
        builders = []
        for i, r in enumerate(resolved):
            agent_slug = (
                r["agent_id"]
                .replace(".md", "")
                .split("/")[-1]
            )
            builders.append(
                {
                    "id": agent_slug,
                    "tier": "primary",
                    "active": True,
                    "reason": f"role '{r['role_name']}' bound via {r['assignment_id']}",
                    "role_name": r["role_name"],
                    "order": i,
                    "goal": r["goal"],
                    "backstory": r["backstory"],
                }
            )

        function_entry = {
            "name": "CREW",
            "position": 6,  # PRODUCE slot
            "builders": builders,
            "deps": [],
            "parallel": parallel,
            "estimated_tokens": 4096 * len(builders),
            "process": process,
        }

        crew_meta = {
            "crew_name": crew_name,
            "process": process,
            "handoff_protocol": handoff_proto,
            "roles": resolved,
            "charter": {
                "mission": charter_fm.get("mission_statement", ""),
                "deliverables": charter_fm.get("deliverables", []),
                "deadline": charter_fm.get("deadline", ""),
                "budget": charter_fm.get("budget", {}),
            }
            if charter_fm
            else None,
            "source_template": str(crew_path.resolve().relative_to(cex_root.resolve())),
        }
        # R-172: conditional insertion (never a None placeholder) -- a
        # crew_template that does not declare these blocks (every instance on
        # disk today) produces a crew_meta dict with the EXACT SAME keys, in
        # the EXACT SAME order, as pre-R-172 -- the absent-blocks parity
        # contract proved by tests/test_crew_r172_topology.py's A/B harness.
        if isinstance(speaker_selection_fm, dict):
            crew_meta["speaker_selection"] = speaker_selection_fm
        if isinstance(termination_fm, dict):
            crew_meta["termination"] = termination_fm

        plan = {
            "intent": purpose,
            "parsed": {
                "verb": "execute",
                "object": crew_name,
                "domain": "crew",
                "quality": charter_fm.get("quality_gate", 9.0),
                "multi_object": False,
            },
            "classified_kinds": [],
            "functions": [function_entry],
            "total_builders": len(builders),
            "estimated_tokens": 4096 * len(builders),
            "turn_budgets": {b["id"]: 25 for b in builders},
            "warnings": [],
            "crew_meta": crew_meta,
        }
        return plan

    def _get_active_builders(self, step: dict) -> list[dict]:
        """Filter to only active builders in a step."""
        return [b for b in step.get("builders", []) if b.get("active")]

    def _resolve_fork_context(self, builder: dict) -> str:
        """Determine execution mode for a builder based on fork_context.

        Returns: "fork" | "inline"
        """
        fc = builder.get("fork_context")
        if fc == "fork":
            return "fork"
        if fc == "inline" or fc is None:
            return "inline"
        # null -> runtime decides based on complexity
        return "inline"  # default to inline

    def _resolve_model(self, builder: dict) -> tuple[str, int]:
        """Resolve LLM model and max_tokens. Builder-explicit > Router > default.

        Priority:
          1. Builder-explicit model (set in plan by motor)
          2. Router nucleus config (reads nucleus_models.yaml)
          3. LLM_MODEL constant (fallback)

        Returns: (model_id, max_tokens)
        """
        # --- 1. Builder-explicit model (highest priority) ---
        if builder.get("model"):
            return builder["model"], builder.get("model_max_tokens", LLM_MAX_TOKENS)

        # --- 2. Router path (CexRouter + nucleus_models.yaml) ---
        try:
            from cex_router import CexRouter, get_router, resolve_model_for
            nucleus = os.environ.get("CEX_NUCLEUS", "n03")
            # Try CexRouter provider-aware routing first
            router = get_router()
            if isinstance(router, CexRouter) and router.providers:
                try:
                    route = router.resolve_nucleus(nucleus)
                    if route.get("model"):
                        return route["model"], LLM_MAX_TOKENS
                except RuntimeError:
                    pass  # No healthy provider -- fall through to static
            # Fallback: static nucleus_models.yaml resolution
            model = resolve_model_for(nucleus, fallback="")
            if model:
                return model, LLM_MAX_TOKENS
        except Exception:
            pass  # D1: graceful fallback

        # --- 3. Default constant ---
        return LLM_MODEL, LLM_MAX_TOKENS

    def _check_max_turns(self, builder_id: str, state: RunState) -> tuple[bool, int]:
        """Check if builder has exceeded max_turns. Returns (allowed, turns_used)."""
        turns_key = f"_turns_{builder_id}"
        turns_used = state.retry_counts.get(turns_key, 0)
        # Find max_turns from plan's builder entries
        max_turns = None
        for fn in self.functions:
            for b in fn.get("builders", []):
                if b["id"] == builder_id and b.get("max_turns"):
                    max_turns = b["max_turns"]
                    break
        if max_turns and turns_used >= max_turns:
            return False, turns_used
        # Increment
        state.retry_counts[turns_key] = turns_used + 1
        return True, turns_used + 1

    def _check_tool_allowed(self, tool_name: str, builder: dict) -> tuple[bool, str]:
        """Check if a tool is allowed for a builder."""
        denied = builder.get("denied_tools", [])
        if not denied:
            return True, "no deny list"
        if tool_name.lower() in [d.lower() for d in denied]:
            return False, f"tool '{tool_name}' is denied for builder '{builder['id']}'"
        return True, "allowed"

    def _execute_forked(
        self, builder: dict, prompt: str, model: str, max_tokens: int, output_dir: Path | None
    ) -> BuilderOutput:
        """Execute a builder in a forked sub-process (isolated context).

        The forked builder:
        - Inherits: builder specs + selected memory + query context
        - Does NOT inherit: context of other builders in the crew
        - Result returns via output file
        """
        bid = builder["id"]
        FORK_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        fork_file = FORK_OUTPUT_DIR / f"fork_{bid}_{datetime.now().strftime('%H%M%S')}.md"
        prompt_file = FORK_OUTPUT_DIR / f"fork_{bid}_prompt.md"

        # Write prompt to file for subprocess
        prompt_file.write_text(prompt, encoding="utf-8")

        try:
            # --- [1] Claude CLI first (uses subscription, zero cost) ---
            content = None
            try:
                result = _run_claude_cli(
                    ["claude", "-p", "--model", model], prompt,
                    timeout=120, cwd=str(ROOT),
                )
                if result.returncode == 0 and result.stdout.strip():
                    content = result.stdout
                    _track_crew_call(
                        provider="claude-cli",
                        model=model,
                        prompt=prompt,
                        response_text=content,
                        builder_id=bid,
                    )
            except FileNotFoundError:
                pass  # CLI not available, try SDK

            # --- [2] SDK fallback (only if CLI failed AND CEX_USE_API=1) ---
            if not content and os.environ.get("CEX_USE_API", "0") == "1":
                try:
                    sdk_root = str(Path(__file__).resolve().parent.parent)
                    if sdk_root not in sys.path:
                        sys.path.insert(0, sdk_root)
                    from cex_sdk.models.message import Message as SDKMessage
                    from cex_sdk.models.providers.anthropic import \
                        Claude as SDKClaude
                    sdk_model = SDKClaude(id=model, max_tokens=max_tokens)
                    response = sdk_model.invoke([SDKMessage(role="user", content=prompt)])
                    if response.content:
                        content = response.content
                        usage = response.response_usage
                        if usage:
                            print(f"  [SDK-API] {bid}: in={usage.input_tokens} out={usage.output_tokens}", file=sys.stderr)
                        in_tok = int(getattr(usage, "input_tokens", 0) or 0) if usage else 0
                        out_tok = int(getattr(usage, "output_tokens", 0) or 0) if usage else 0
                        _track_crew_call(
                            provider="anthropic-api",
                            model=model,
                            prompt=prompt,
                            response_text=content,
                            builder_id=bid,
                            input_tokens=in_tok,
                            output_tokens=out_tok,
                        )
                except Exception:
                    pass

            if not content:
                raise RuntimeError("No LLM provider available (CLI failed, API disabled)")
            fork_file.write_text(content, encoding="utf-8")

            score, self_assessed = _parse_self_assessed_quality(content)

            return BuilderOutput(
                builder_id=bid,
                content=content,
                quality_score=score,
                metadata={
                    "mode": "fork-cli",
                    "model": model,
                    "fork_output": str(fork_file),
                    "self_assessment_parsed": self_assessed,
                },
                status="complete",
            )
        except FileNotFoundError:
            # claude CLI not in PATH -- dry-run fallback
            fork_file.write_text(f"[FORK-DRY-RUN] {bid}\n{prompt[:500]}", encoding="utf-8")
            return BuilderOutput(
                builder_id=bid,
                content=f"[FORK-DRY-RUN] claude CLI not found. Prompt saved to {fork_file}",
                quality_score=0.0,
                metadata={"mode": "fork-dry-run", "fork_output": str(fork_file)},
                status="complete",
            )
        except Exception as e:
            return BuilderOutput(
                builder_id=bid,
                content=f"[FORK-ERROR] {e}",
                quality_score=0.0,
                metadata={"mode": "fork", "error": str(e)},
                status="failed",
            )

    # --- Dry-Run Execution ---

    def execute_step_dry_run(
        self,
        step: dict,
        state: RunState,
        output_dir: Path | None = None,
    ) -> list[BuilderOutput]:
        """Generate prompts without calling LLM."""
        fn_name = step.get("name", f"step_{step.get('position', '?')}")
        position = step.get("position", 0)
        active = self._get_active_builders(step)
        results = []

        for builder in active:
            bid = builder["id"]
            prompt = compose_prompt(
                bid,
                fn_name,
                self.intent,
                self.parsed,
                self.quality_target,
                state,
                self.builder_dir,
            )
            prompt_bytes = len(prompt.encode("utf-8"))

            if output_dir:
                fname = f"{position:02d}_{fn_name}_{bid}.prompt.md"
                (output_dir / fname).write_text(prompt, encoding="utf-8")
                print(f"  [{fn_name}] {bid} -> {fname} ({prompt_bytes / 1024:.1f}KB)")

            out = BuilderOutput(
                builder_id=bid,
                content=f"[DRY-RUN] Prompt generated for {bid} ({prompt_bytes} bytes)",
                quality_score=0.0,
                metadata={
                    "function": fn_name,
                    "position": position,
                    "tier": builder["tier"],
                    "prompt_bytes": prompt_bytes,
                    "mode": "dry-run",
                },
                status="complete",
            )
            results.append(out)

        return results

    # --- Real Execution ---

    def execute_step_real(
        self,
        step: dict,
        state: RunState,
        output_dir: Path | None = None,
    ) -> list[BuilderOutput]:
        """Execute builders via claude CLI (subscription auth)."""
        fn_name = step.get("name", f"step_{step.get('position', '?')}")
        position = step.get("position", 0)
        active = self._get_active_builders(step)
        results = []

        # Verify claude CLI is available
        try:
            subprocess.run(["claude", "--version"], capture_output=True, timeout=5)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print("WARN: claude CLI not found. Falling back to dry-run.", file=sys.stderr)
            return self.execute_step_dry_run(step, state, output_dir)

        for builder in active:
            bid = builder["id"]

            # Max turns check
            allowed, turns = self._check_max_turns(bid, state)
            if not allowed:
                out = BuilderOutput(
                    builder_id=bid,
                    content=f"[MAX-TURNS] Builder '{bid}' reached max_turns limit ({turns})",
                    quality_score=0.0,
                    metadata={"turns_used": turns, "max_turns_exceeded": True},
                    status="degraded",
                )
                state.warnings.append(f"{bid}: max_turns exceeded ({turns})")
                results.append(out)
                continue

            retries = state.retry_counts.get(bid, 0)
            retry_feedback = ""
            out = None

            # Resolve model from effort config
            model, max_tokens = self._resolve_model(builder)

            # Check fork context
            fork_mode = self._resolve_fork_context(builder)

            while retries <= MAX_RETRIES:
                prompt = compose_prompt(
                    bid,
                    fn_name,
                    self.intent,
                    self.parsed,
                    self.quality_target,
                    state,
                    self.builder_dir,
                    retry_feedback=retry_feedback,
                )

                # Fork execution path
                if fork_mode == "fork":
                    out = self._execute_forked(builder, prompt, model, max_tokens, output_dir)
                    if out.quality_score >= DEFAULT_QUALITY_GATE or out.status == "failed":
                        break
                    retries += 1
                    state.retry_counts[bid] = retries
                    retry_feedback = f"Fork score {out.quality_score:.1f} < gate. Retry {retries + 1}."
                    if retries > MAX_RETRIES:
                        out.status = "degraded"
                    continue

                # Inline execution path (original)
                try:
                    cli_result = _run_claude_cli(
                        ["claude", "-p", "--model", model], prompt,
                        timeout=120, cwd=str(ROOT),
                    )
                    if cli_result.returncode != 0:
                        raise RuntimeError(f"claude -p exit {cli_result.returncode}")
                    content = cli_result.stdout

                    # Extract self-assessed quality score
                    score, self_assessed = _parse_self_assessed_quality(content)

                    out = BuilderOutput(
                        builder_id=bid,
                        content=content,
                        quality_score=score,
                        metadata={
                            "function": fn_name,
                            "position": position,
                            "tier": builder["tier"],
                            "retries": retries,
                            "model": LLM_MODEL,
                            "mode": "execute",
                            "self_assessment_parsed": self_assessed,
                        },
                        status="complete",
                    )

                    if score >= DEFAULT_QUALITY_GATE:
                        break

                    retries += 1
                    state.retry_counts[bid] = retries
                    retry_feedback = (
                        f"Score {score:.1f} < gate {DEFAULT_QUALITY_GATE}. "
                        "Improve quality. "
                        f"Attempt {retries + 1}/{MAX_RETRIES + 1}."
                    )

                    if retries > MAX_RETRIES:
                        out.status = "degraded"
                        state.warnings.append(
                            f"{bid}: degraded after {MAX_RETRIES + 1} attempts (score: {score:.1f})"
                        )
                        break

                except Exception as e:
                    out = BuilderOutput(
                        builder_id=bid,
                        content=f"[ERROR] {e}",
                        quality_score=0.0,
                        metadata={"error": str(e), "retries": retries},
                        status="failed",
                    )
                    state.warnings.append(f"{bid}: failed -- {e}")
                    break

            if out is None:
                out = BuilderOutput(
                    builder_id=bid,
                    content="[ERROR] No output produced",
                    status="failed",
                )

            # Save output file
            if output_dir and out.content:
                ext = "error.md" if out.status == "failed" else "output.md"
                fname = f"{position:02d}_{fn_name}_{bid}.{ext}"
                (output_dir / fname).write_text(out.content, encoding="utf-8")
                print(
                    f"  [{fn_name}] {bid} -> {fname} "
                    f"(score: {out.quality_score:.1f}, "
                    f"status: {out.status})"
                )

            # Wire 6: Check if context compaction is needed
            prompt_so_far = " ".join(
                o.content for o in state.outputs.values()
                if o.content and not o.content.startswith("[")
            )
            compact_check = check_compaction_needed(prompt_so_far)
            if compact_check["needed"]:
                state.warnings.append(
                    f"[COMPACT] Context at {compact_check['usage_ratio']:.0%} capacity. "
                    "Compaction skill available: p04_skill_compact"
                )

            # Wire 7: Check if memory extraction should run
            mem_check = check_memory_extract_needed()
            if mem_check["needed"]:
                state.warnings.append(
                    f"[MEMORY] Extraction trigger at execution #{mem_check['counter']}. "
                    "Memory skill available: p04_skill_memory_extract"
                )

            results.append(out)

        return results

    # --- Main Run Loop ---

    def run(
        self,
        dry_run: bool = True,
        output_dir: Path | None = None,
        step_filter: int | None = None,
    ) -> RunState:
        """Execute the full plan (or a single step).

        Args:
            dry_run: If True, generate prompts only. If False, call LLM.
            output_dir: Directory for output files. Created if needed.
            step_filter: If set, only execute the function at this position.

        Returns:
            RunState with all outputs and metadata.
        """
        state = RunState(
            intent=self.intent,
            plan=self.plan,
            started_at=datetime.now().isoformat(),
        )

        # Sort functions by pipeline position
        functions = sorted(self.functions, key=lambda f: f.get("position", 99))

        if step_filter is not None:
            functions = [f for f in functions if f.get("position") == step_filter]
            if not functions:
                print(f"WARN: No function at position {step_filter}", file=sys.stderr)

        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)

        mode_str = "DRY-RUN" if dry_run else "EXECUTE"
        total_active = sum(len(self._get_active_builders(fn)) for fn in functions)

        # --- Banner ---
        print(f"\n{'=' * 60}")
        print(f"CEX Crew Runner -- {mode_str}")
        print(f"Intent: {self.intent}")
        print(f"Functions: {len(functions)} | Active builders: {total_active}")
        print(f"Quality target: {self.quality_target}")
        if output_dir:
            print(f"Output: {output_dir}")
        print(f"{'=' * 60}\n")

        # --- Execute each function in order ---
        for fn in functions:
            fn_name = fn.get("name", "?")
            position = fn.get("position", 0)
            active_count = len(self._get_active_builders(fn))

            if active_count == 0:
                print(f"[{position}] {fn_name}: skipped (0 active builders)")
                continue

            print(f"[{position}] {fn_name}: {active_count} builder(s)")
            state.current_step = position

            if dry_run:
                outputs = self.execute_step_dry_run(fn, state, output_dir)
            else:
                outputs = self.execute_step_real(fn, state, output_dir)

            for out in outputs:
                state.outputs[out.builder_id] = out

        state.completed_at = datetime.now().isoformat()

        # --- Summary ---
        completed = sum(1 for o in state.outputs.values() if o.status == "complete")
        degraded = sum(1 for o in state.outputs.values() if o.status == "degraded")
        failed = sum(1 for o in state.outputs.values() if o.status == "failed")

        print(f"\n{'=' * 60}")
        print(f"COMPLETE -- {mode_str}")
        print(f"Builders: {completed} complete, {degraded} degraded, {failed} failed")

        if state.warnings:
            print(f"\nWarnings ({len(state.warnings)}):")
            for w in state.warnings:
                print(f"  - {w}")

        # --- Save run state ---
        if output_dir:
            state_dict = {
                "intent": state.intent,
                "mode": mode_str.lower().replace("-", "_"),
                "started_at": state.started_at,
                "completed_at": state.completed_at,
                "current_step": state.current_step,
                "quality_target": self.quality_target,
                "builders": {
                    bid: {
                        "status": out.status,
                        "quality_score": out.quality_score,
                        "metadata": out.metadata,
                    }
                    for bid, out in state.outputs.items()
                },
                "warnings": state.warnings,
                "summary": {
                    "total": len(state.outputs),
                    "complete": completed,
                    "degraded": degraded,
                    "failed": failed,
                },
            }

            state_file = output_dir / "_run_state.json"
            state_file.write_text(
                json.dumps(state_dict, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"\nRun state: {state_file}")

            # Also save a manifest of all generated files
            manifest = {
                "generated_at": state.completed_at,
                "mode": mode_str.lower(),
                "intent": state.intent,
                "files": sorted(
                    f.name for f in output_dir.glob("*.md") if not f.name.startswith("_")
                ),
                "total_files": len(list(output_dir.glob("*.md"))),
                "total_bytes": sum(f.stat().st_size for f in output_dir.glob("*.md")),
            }
            manifest_file = output_dir / "_manifest.json"
            manifest_file.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        print(f"{'=' * 60}\n")
        return state


# ===========================================================================
# Crew Control Plane (Phase D RUN) -- the REAL, OFFLINE-TESTABLE runner.
#
# The CrewRunner above is the prompt-generation / fork lane (dry-run default;
# the existing offline tests + the dashboard read surface depend on it -- it is
# the SAFE fallback, kept verbatim). The control plane below is the next layer:
# it EXECUTES each crew role by COMPOSING cex_agent_loop.run_agent_multistep
# (one agent run per role) and honors the crew TOPOLOGY (sequential /
# hierarchical / consensus) with the handoff protocol (role N receives role
# N-1's artifact as F3 INJECT augmentation). It persists runs/steps via the
# SAME audited writer seam cex_agent_loop already uses (degrade-never if no DB),
# runs a charter-level F7 GOVERN gate after all roles complete, and keeps the
# live tool_resolver UNBOUND by default (the founder-gated seam -- a declared
# tool records a call but performs NO live side effect).
#
# DEGRADE-NEVER: cex_agent_loop absent -> the role falls back to the dry-run
# lane (still offline). No DB writer -> in-process ledger only (LocalOnlyWriter).
# ASCII-only per .claude/rules/ascii-code-rule.md.
# ===========================================================================


@dataclass
class RoleResult:
    """Outcome of ONE crew role executed by the control plane.

    Mirrors the BuilderOutput shape (so the CrewRunState summary reads the same
    way as a CrewRunner run) and ADDS the role binding + the run handle + the
    plan/act/observe step ledger lifted from the agent loop. NEVER carries a
    secret (the agent run result is credential-free by construction)."""

    role_name: str
    agent_id: str
    artifact: str = ""
    score: float = 0.0
    passed: bool = False
    status: str = "pending"            # completed | failed | refused | budget_exceeded | degraded
    run_id: str = ""
    steps: int = 0
    steps_log: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class CrewRunState:
    """The full control-plane run state: per-role results + the charter gate.

    ``gate`` is the charter-level F7 GOVERN verdict computed AFTER every role
    completes (passed/score/threshold/reason). ``process`` echoes the topology
    actually executed."""

    crew_name: str
    process: str
    intent: str
    roles: dict = field(default_factory=dict)   # role_name -> RoleResult
    order: list = field(default_factory=list)   # role_name execution order
    started_at: str = ""
    completed_at: str = ""
    gate: dict = field(default_factory=dict)
    warnings: list = field(default_factory=list)


# A team_charter-style default quality gate (mirrors DEFAULT_QUALITY_GATE; the
# charter may override via crew_meta.charter or an explicit threshold arg).
DEFAULT_CHARTER_GATE = 9.0

# The default budget the control plane gives each role's agent loop when the
# charter declares none. Bounded so an offline run can never spin (the loop's
# own _DEFAULT_MAX_STEPS backstop also applies).
DEFAULT_ROLE_MAX_STEPS = 6

# _TOOLS_DIR for the lazy agent-loop import (this file lives in <root>/_tools).
_TOOLS_DIR = Path(__file__).resolve().parent


def _default_agent_runner(
    tenant_id: str,
    agent_id: str,
    inputs: dict,
    credential,
    *,
    db=None,
    options=None,
    run_key=None,
):
    """The DEFAULT per-role executor: compose cex_agent_loop.run_agent_multistep.

    A crew ROLE = one multi-step agent run (plan/act/observe over the role's
    declared tools, budgeted + HITL-gated + persisted). This thin wrapper is the
    seam the control plane calls; tests inject a fake to stay fully offline
    WITHOUT faking the deep loop. Lazy import so this module imports in a
    degraded env; raises ImportError to the caller (which degrades to dry-run).
    """
    if str(_TOOLS_DIR) not in sys.path:
        sys.path.insert(0, str(_TOOLS_DIR))
    import cex_agent_loop as _loop  # type: ignore[import]

    return _loop.run_agent_multistep(
        tenant_id,
        agent_id,
        inputs,
        credential,
        db=db,
        options=options,
        run_key=run_key,
    )


def _offline_credential():
    """Build a SAFE offline credential for the control plane's own default run.

    The control plane never invents a live key. When a caller does not pass a
    credential, we construct a byo_api_key credential carrying a SENTINEL key so
    the loop's credential shape-check passes; with the unbound tool_resolver +
    the offline CEXAgent seam, no live call is made. A real run passes a real
    credential IN (the founder-gated path). Returns None if the Credential type
    cannot be imported (the caller then must pass one)."""
    try:
        if str(_TOOLS_DIR) not in sys.path:
            sys.path.insert(0, str(_TOOLS_DIR))
        import cex_run_capability as _rc  # type: ignore[import]

        return _rc.Credential(
            mode=_rc.MODE_BYO_API_KEY, provider="anthropic", api_key="unbound-offline"
        )
    except Exception:
        return None


# ===========================================================================
# GATED LIVE tool_resolver binding (spec 06 P4 -- the founder-gated lane).
#
# The crew control plane runs OFFLINE by default: cex_agent_loop.tool_resolver
# is UNBOUND (None), so a declared tool RECORDS the call and OBSERVES the honest
# "tool_unbound" note -- no live side effect (the 31 offline tests + the dry-run
# path depend on this; it is byte-identical to pre-P4). The LIVE lane binds the
# loop's tool_resolver to cex_run_capability.run_capability so a crew role can
# actually invoke a capability -- but ONLY behind the CEX_CREW_LIVE kill-switch.
#
# FAIL-CLOSED (the whole point): bind_live_tool_resolver is a NO-OP (returns
# False, leaves the resolver UNBOUND) unless CEX_CREW_LIVE is truthy. So the
# default import + the default run NEVER touch the live seam (zero regression).
# When bound, the agent loop's EXISTING HITL gate (_tool_needs_approval +
# _emit_approval via cexai.governance.hitl.FileApprovalGate) still fires for an
# irreversible role tool (publish/deploy/send/...): emit-and-defer, NON-BLOCKING,
# so the tool is SKIPPED until a human records an `approve` verdict -- the binding
# does NOT bypass it. ASCII-only per .claude/rules/ascii-code-rule.md.
# ===========================================================================

# The kill-switch env var. UNSET (or falsy) -> the live resolver stays UNBOUND.
CEX_CREW_LIVE_ENV = "CEX_CREW_LIVE"
_TRUTHY = frozenset({"1", "true", "yes", "on"})


def crew_live_enabled() -> bool:
    """True iff the CEX_CREW_LIVE kill-switch is set to a truthy value.

    This is the SINGLE gate for the live crew tool lane. Default (env unset or
    falsy) -> False -> the resolver stays UNBOUND (offline-safe). A real run sets
    CEX_CREW_LIVE=1 IN ADDITION to the per-charter HITL gate already in the loop.
    PURE: reads only the environment, never mutates state."""
    return os.environ.get(CEX_CREW_LIVE_ENV, "").strip().lower() in _TRUTHY


def _make_run_capability_resolver(run_capability_fn=None, *, credential=None):
    """Build the LIVE tool_resolver: a function the agent loop calls per tool.

    Signature matches cex_agent_loop's contract exactly:
        resolver(tool_name, args, *, tenant_id, agent_id) -> (result_str, meta)

    It REUSES cex_run_capability.run_capability (lazy default import; a test
    injects a FAKE via ``run_capability_fn`` to stay fully offline -- NO real
    LLM). The tool_name is treated as the capability to dispatch; ``args`` is
    folded into the run inputs; ``intent`` is derived from the args (or the tool
    name). DEGRADE-NEVER: a CapabilityRefused or any error is returned as an
    observation note (never raised) so the loop records it and keeps going.

    NOTE: this resolver is reached ONLY for a tool the loop did NOT gate through
    HITL. An irreversible tool is intercepted upstream by _tool_needs_approval +
    _emit_approval (emit-and-defer) and SKIPPED before the resolver is called --
    the binding cannot bypass that gate."""

    def _resolver(tool_name, args, *, tenant_id, agent_id):
        fn = run_capability_fn
        cred = credential
        if fn is None:
            # Lazy default: the real capability dispatch (the founder-gated seam).
            if str(_TOOLS_DIR) not in sys.path:
                sys.path.insert(0, str(_TOOLS_DIR))
            import cex_run_capability as _rc  # type: ignore[import]

            fn = _rc.run_capability
            if cred is None:
                cred = _offline_credential()
        if cred is None:
            cred = _offline_credential()
        # Derive a free-text intent for the capability dispatch from the tool args.
        intent = ""
        if isinstance(args, dict):
            for k in ("intent", "query", "prompt", "task", "text"):
                v = args.get(k)
                if isinstance(v, str) and v.strip():
                    intent = v.strip()
                    break
        if not intent:
            intent = "crew tool: %s" % tool_name
        try:
            result = fn(
                tenant_id,
                tool_name,
                intent,
                cred,
                inputs=dict(args) if isinstance(args, dict) else None,
            )
        except Exception as exc:
            reason = getattr(exc, "reason", None) or type(exc).__name__
            return (
                "tool_capability_refused: %s: %s" % (reason, exc),
                {"tool": tool_name, "status": "refused"},
            )
        status = str(getattr(result, "status", "") or "")
        score = float(getattr(result, "score", 0.0) or 0.0)
        artifact = str(getattr(result, "artifact", "") or "")
        observation = "tool_capability_ran: %s status=%s score=%.1f\n%s" % (
            tool_name,
            status or "?",
            score,
            artifact[:1500],
        )
        return observation, {"tool": tool_name, "status": status, "score": score}

    return _resolver


def bind_live_tool_resolver(
    *, run_capability_fn=None, credential=None, force=False
):
    """GATE + bind the live crew tool_resolver on cex_agent_loop. FAIL-CLOSED.

    Returns ``True`` iff the live resolver was bound; ``False`` (a NO-OP) otherwise.

    The gate: bind ONLY when ``crew_live_enabled()`` (CEX_CREW_LIVE truthy) OR an
    explicit ``force=True`` (tests use force to exercise the live path WITHOUT
    flipping the process env). With the flag UNSET and force=False this returns
    False and leaves cex_agent_loop.tool_resolver EXACTLY as it was (UNBOUND by
    default) -- so the default crew run is byte-identical to pre-P4 (zero
    regression), and a missing/half-set flag can NEVER produce a silent live run.

    When it binds, it REUSES cex_run_capability.run_capability (or the injected
    fake) via _make_run_capability_resolver. The irreversible-role HITL gate in
    the loop is untouched -- it still fires before the resolver for a gated tool.
    DEGRADE-NEVER: if cex_agent_loop cannot be imported, returns False."""
    if not (force or crew_live_enabled()):
        return False
    try:
        if str(_TOOLS_DIR) not in sys.path:
            sys.path.insert(0, str(_TOOLS_DIR))
        import cex_agent_loop as _loop  # type: ignore[import]
    except Exception:
        return False
    _loop.tool_resolver = _make_run_capability_resolver(
        run_capability_fn=run_capability_fn, credential=credential
    )
    return True


def unbind_live_tool_resolver():
    """Reset cex_agent_loop.tool_resolver to UNBOUND (None). Test/teardown hygiene
    so a bound live resolver never leaks across runs. DEGRADE-NEVER (no loop ->
    no-op)."""
    try:
        if str(_TOOLS_DIR) not in sys.path:
            sys.path.insert(0, str(_TOOLS_DIR))
        import cex_agent_loop as _loop  # type: ignore[import]

        _loop.tool_resolver = None
    except Exception:
        pass


# ---------------------------------------------------------------------------
# R-172 -- composable TERMINATION conditions + a named-strategy SPEAKER
# SELECTION dispatch table (kc_oss_autogen.md M2+M3+M5; register row R-172).
#
# Before this section, `process:` was crew_template's ONLY topology knob -- one
# hardcoded string (sequential | hierarchical | consensus), read by
# CrewControlPlaneRunner.run()'s if/elif ladder and by _charter_gate's
# if/else. AutoGen/AG2's own group-chat substrate splits that into TWO
# independent, swappable pieces (kc_oss_autogen.md M2): a composable (AND/OR)
# TerminationCondition family, and a per-Team "who speaks next" strategy --
# five swappable Team subclasses in AutoGen, three named strategies here
# (round_robin | manager_delegates | vote), with room to add more WITHOUT
# growing an enum.
#
# Two new OPTIONAL crew_template frontmatter blocks (documented in
# .claude/rules/composable-crew.md and archetypes/builders/crew-template-
# builder/bld_schema_crew_template.md):
#
#   speaker_selection:
#     strategy: round_robin | manager_delegates | vote
#
#   termination:
#     any_of: [<condition>, ...]   # OR -- fires when ANY child is true
#     all_of: [<condition>, ...]   # AND -- fires only when ALL children true
#
# <condition> is EITHER a nested {any_of:[...]} / {all_of:[...]} node
# (arbitrary depth -- true operator-composable AND/OR, matching AutoGen's
# `__or__`/`__and__` TerminationCondition overloads) OR a LEAF
# `{type: <name>, ...params}` dispatched through CONDITION_TABLE below. Four
# named leaf types ship today: max_rounds, artifact_produced,
# quality_gate_passed, budget_exhausted.
#
# DEGRADE-NEVER / ABSENT-BLOCKS CONTRACT: load_from_crew_template only writes
# crew_meta["speaker_selection"] / crew_meta["termination"] into the plan when
# the frontmatter ACTUALLY has a dict-shaped block -- never a None
# placeholder (see step 5 of that method). So a crew_template with neither
# block (every instance on disk today) produces a byte-identical plan to
# pre-R-172; self.speaker_selection / self.termination resolve to None;
# _resolve_strategy() falls through to PROCESS_TO_STRATEGY (the exact legacy
# process -> topology-function mapping); and _run_round_robin (bound to
# "round_robin") delegates straight to the untouched _run_sequential body.
# Every existing crew_template instance is therefore unaffected byte-for-byte
# (proved by _tools/tests/test_crew_r172_topology.py's A/B harness against
# git HEAD, mirroring the R-189 ACTION_TABLE precedent in
# _tools/cex_capability_router.py).
#
# SCOPED LIMIT (documented, not silently overreached): only the round_robin
# strategy consumes `termination` today -- it is the one strategy with a
# natural per-turn loop (AutoGen's own RoundRobinGroupChat +
# TerminationCondition pairing). manager_delegates/vote keep their existing
# fixed-shape run: a `termination` block on a hierarchical/consensus
# crew_template is parsed and rendered by `show`, but not yet consumed by the
# runner -- a future lane's generalization, not this one's overreach.
# _charter_gate is UNCHANGED: it still keys off self.process (not the
# resolved strategy) -- see the rule doc for the one documented edge case (an
# explicit speaker_selection.strategy that diverges from what `process`
# implies).
# ---------------------------------------------------------------------------


class _TerminationCtx(NamedTuple):
    """Snapshot passed to every termination leaf-condition evaluator. Built
    fresh after each round of the round_robin strategy's loop -- PURE data,
    no live handles (offline-testable with synthetic values)."""

    round_num: int              # 1-indexed count of role-turns completed so far
    roles_done: tuple           # RoleResult tuple, in execution order
    last_result: Any            # RoleResult of the just-completed turn, or None
    tokens_used_estimate: int   # cumulative char/4 estimate (same convention
                                 # as _track_crew_call's fallback, this file's
                                 # top-of-file cost-tracking helper)
    charter_gate: float         # the crew's charter_gate threshold (default
                                 # fallback for quality_gate_passed when a spec
                                 # omits its own `threshold`)


def _cond_max_rounds(spec: dict, ctx: _TerminationCtx) -> bool:
    """True once ctx.round_num reaches the spec's `rounds` (accepts `rounds`
    or `value` for author convenience)."""
    n = _coerce_float(spec.get("rounds", spec.get("value")))
    return n is not None and ctx.round_num >= n


def _cond_artifact_produced(spec: dict, ctx: _TerminationCtx) -> bool:
    """True when the relevant RoleResult has a non-empty artifact. Defaults to
    the just-completed turn; an optional `role` param scopes it to a specific
    role name anywhere in the rounds run so far."""
    role_filter = spec.get("role")
    target = ctx.last_result
    if role_filter:
        target = next(
            (r for r in reversed(ctx.roles_done)
             if getattr(r, "role_name", None) == role_filter),
            None,
        )
    return bool(target is not None and getattr(target, "artifact", ""))


def _cond_quality_gate_passed(spec: dict, ctx: _TerminationCtx) -> bool:
    """True when the just-completed turn's score clears `threshold` (falls
    back to the crew's own charter_gate when the spec omits one)."""
    threshold = _coerce_float(spec.get("threshold"))
    if threshold is None:
        threshold = ctx.charter_gate
    return bool(ctx.last_result is not None and ctx.last_result.score >= threshold)


def _cond_budget_exhausted(spec: dict, ctx: _TerminationCtx) -> bool:
    """True once the cumulative token estimate reaches the spec's `tokens`."""
    tokens = _coerce_float(spec.get("tokens"))
    return tokens is not None and ctx.tokens_used_estimate >= tokens


# condition type name -> pure evaluator(spec, ctx) -> bool. Adding a 5th leaf
# type is one function + one row here -- no other call site needs to change.
CONDITION_TABLE: dict[str, Callable[[dict, _TerminationCtx], bool]] = {
    "max_rounds": _cond_max_rounds,
    "artifact_produced": _cond_artifact_produced,
    "quality_gate_passed": _cond_quality_gate_passed,
    "budget_exhausted": _cond_budget_exhausted,
}


def _evaluate_termination(node: Any, ctx: _TerminationCtx) -> bool:
    """Recursively evaluate a termination condition tree. PURE + TOTAL: never
    raises -- a malformed/unrecognized node evaluates to False (never-
    terminate is always the SAFE default; the round_robin loop's own hard
    safety cap is the real backstop against a tree that never fires). A
    leaf's `type` key wins if present (even alongside a stray any_of/all_of on
    the same dict); otherwise `any_of` is tried, then `all_of`; an
    empty/absent/malformed node is False."""
    if not isinstance(node, dict):
        return False
    if "type" in node:
        fn = CONDITION_TABLE.get(str(node.get("type")))
        if fn is None:
            return False
        try:
            return bool(fn(node, ctx))
        except Exception:
            return False
    if "any_of" in node:
        children = node.get("any_of") or []
        return any(_evaluate_termination(c, ctx) for c in children)
    if "all_of" in node:
        children = node.get("all_of") or []
        return bool(children) and all(_evaluate_termination(c, ctx) for c in children)
    return False


class _StrategyCtx(NamedTuple):
    """Uniform call context for a STRATEGY_TABLE entry: the runner instance
    (so a strategy function can call its _run_* primitive + read
    self.termination/self.roles/etc.), the resolved writer, and the in-flight
    CrewRunState to mutate."""

    runner: "CrewControlPlaneRunner"
    writer: Any
    state: "CrewRunState"


def _strategy_round_robin(ctx: _StrategyCtx) -> None:
    ctx.runner._run_round_robin(ctx.writer, ctx.state)


def _strategy_manager_delegates(ctx: _StrategyCtx) -> None:
    ctx.runner._run_hierarchical(ctx.writer, ctx.state)


def _strategy_vote(ctx: _StrategyCtx) -> None:
    ctx.runner._run_consensus(ctx.writer, ctx.state)


# strategy name -> runner(ctx). Each wrapper calls its _run_*() reflex BY NAME
# on ctx.runner (not a captured bound method), so `monkeypatch.setattr(cp,
# "_run_hierarchical", fake)` on an instance keeps working exactly like the
# pre-R-172 if/elif ladder (Python resolves ctx.runner._run_hierarchical
# against the instance at CALL time, same rationale as R-189's ACTION_TABLE
# in _tools/cex_capability_router.py).
STRATEGY_TABLE: dict[str, Callable[[_StrategyCtx], None]] = {
    "round_robin": _strategy_round_robin,
    "manager_delegates": _strategy_manager_delegates,
    "vote": _strategy_vote,
}

# The legacy process -> strategy mapping. This IS the pre-R-172 if/elif
# ladder's own logic, restated as data: "consensus" -> vote, "hierarchical" ->
# manager_delegates, anything else (including "sequential" and any
# unrecognized string) -> round_robin -- exactly the old
# `else: self._run_sequential(...)` catch-all.
PROCESS_TO_STRATEGY: dict[str, str] = {
    "sequential": "round_robin",
    "hierarchical": "manager_delegates",
    "consensus": "vote",
}

# Hard safety cap for the round_robin termination loop: this many FULL
# rotations through every role, max, even if `termination` never fires. Real
# agent-loop turns cost real budget -- a malformed/never-satisfied tree must
# never spin forever.
_ROUND_ROBIN_SAFETY_MULTIPLE = 3


class CrewControlPlaneRunner:
    """The crew RUN control plane: execute roles by composing the agent loop.

    Plugs into ``cex_crew.run`` as the REAL runner (vs. the dry-run CrewRunner).
    Consumes the SAME plan dict CrewRunner.load_from_crew_template produces
    (crew_meta.roles + the function_entry.process topology). For each role it
    runs ONE agent loop (the role_assignment's agent_id + goal/backstory/tools),
    threads the handoff per the topology, persists via the writer seam, and runs
    the charter gate at the end.

    OFFLINE-TESTABLE: inject ``agent_runner`` (a fake) + leave the live
    tool_resolver UNBOUND. tenant_id is ALWAYS explicit.
    """

    def __init__(
        self,
        plan: dict,
        *,
        tenant_id: str = "00000000-0000-0000-0000-000000000000",
        credential=None,
        db=None,
        agent_runner=None,
        charter_gate: float | None = None,
        cex_root: Path = CEX_ROOT,
    ):
        self.plan = plan
        self.cex_root = cex_root
        self.tenant_id = (tenant_id or "").strip() or "00000000-0000-0000-0000-000000000000"
        self.credential = credential  # None -> a safe offline sentinel is used per role
        self.db = db                  # None -> LocalOnlyWriter (degrade-never)
        # The per-role executor seam. Default composes run_agent_multistep; a test
        # injects a fake. NEVER None at call time (resolved to the default lazily).
        self.agent_runner = agent_runner or _default_agent_runner

        meta = plan.get("crew_meta", {}) if isinstance(plan, dict) else {}
        self.crew_name = str(meta.get("crew_name") or plan.get("intent") or "crew")
        self.process = str(meta.get("process") or "sequential").strip().lower()
        self.intent = str(plan.get("intent") or "")
        self.roles = meta.get("roles") or []  # resolved role dicts (role_name/agent_id/...)
        self.handoff_protocol = str(meta.get("handoff_protocol") or "a2a-task")

        # R-172 (optional, additive) -- see the CONDITION_TABLE/STRATEGY_TABLE
        # module comment above this class. A non-dict value (or absent key)
        # resolves to None, which is what keeps every existing crew_template
        # (none of which set these blocks) on the exact legacy path.
        sel = meta.get("speaker_selection") if isinstance(meta, dict) else None
        self.speaker_selection = sel if isinstance(sel, dict) else None
        term = meta.get("termination") if isinstance(meta, dict) else None
        self.termination = term if isinstance(term, dict) else None

        # The charter gate threshold: explicit arg > charter quality_gate > parsed
        # plan quality > default.
        charter = meta.get("charter") if isinstance(meta, dict) else None
        parsed = plan.get("parsed", {}) if isinstance(plan, dict) else {}
        if charter_gate is not None:
            self.charter_gate = float(charter_gate)
        elif isinstance(charter, dict) and _coerce_float(charter.get("quality_gate")) is not None:
            self.charter_gate = float(_coerce_float(charter.get("quality_gate")))
        elif _coerce_float(parsed.get("quality")) is not None:
            self.charter_gate = float(_coerce_float(parsed.get("quality")))
        else:
            self.charter_gate = DEFAULT_CHARTER_GATE

    # ------------------------------------------------------------------
    # Writer seam (degrade-never).
    # ------------------------------------------------------------------
    def _resolve_writer(self):
        """Resolve the persistence writer. An injected db wins; else a
        LocalOnlyWriter (no central creds -> in-process ledger only). NEVER
        raises -- a missing runtime-sync module degrades to None (the loop then
        keeps its ledger in memory)."""
        if self.db is not None:
            return self.db
        try:
            if str(_TOOLS_DIR) not in sys.path:
                sys.path.insert(0, str(_TOOLS_DIR))
            import cex_runtime_sync as _sync  # type: ignore[import]

            return _sync.make_runtime_sync_writer(None)  # LocalOnlyWriter
        except Exception:
            return None

    # ------------------------------------------------------------------
    # One role -> one agent run (the F3 INJECT handoff is in ``upstream``).
    # ------------------------------------------------------------------
    def _run_role(
        self,
        role: dict,
        upstream: list,
        writer,
        *,
        coordinator: bool = False,
        role_name_override: str | None = None,
    ) -> RoleResult:
        """Execute ONE role by composing the agent loop, with the upstream
        artifact(s) folded into the run inputs (F3 INJECT augmentation -- the
        handoff protocol). ``coordinator`` flags the hierarchical manager role
        (it receives the worker roster as context). ``role_name_override`` lets a
        caller label the RoleResult / run_key under a distinct name while reusing
        the same role binding (used by the hierarchical manager's synthesize pass
        so it does not collide with its first result). DEGRADE-NEVER: if the agent
        runner cannot be composed (cex_agent_loop absent) the role falls back to
        an offline dry-run stub so the crew still completes."""
        role_name = role_name_override or str(role.get("role_name") or "role")
        agent_id = str(role.get("agent_id") or "").replace(".md", "").split("/")[-1]
        goal = str(role.get("goal") or "")
        backstory = str(role.get("backstory") or "")
        tools = role.get("tools") or []

        # Build the run inputs: the role's goal/backstory + the handoff payload.
        inputs: dict = {
            "intent": self._role_intent(role_name, goal, coordinator),
            "role_name": role_name,
            "crew": self.crew_name,
        }
        if backstory:
            inputs["backstory"] = backstory
        handoff_text = self._format_handoff(upstream)
        if handoff_text:
            inputs["upstream_artifact"] = handoff_text
        if coordinator:
            inputs["workers"] = ", ".join(
                str(r.get("role_name") or "") for r in self.roles if r is not role
            )

        # Per-role budget + the role's declared tool grants (so the loop's Toolkit
        # is scoped to them; the live resolver stays UNBOUND by default).
        options: dict = {
            "budget": {"max_steps": DEFAULT_ROLE_MAX_STEPS},
            "meta": {
                "crew": self.crew_name,
                "role": role_name,
                "process": self.process,
            },
        }

        credential = self.credential or _offline_credential()
        run_key = f"{self.crew_name}:{role_name}".replace(" ", "_")[:120]

        try:
            result = self.agent_runner(
                self.tenant_id,
                agent_id,
                inputs,
                credential,
                db=writer,
                options=options,
                run_key=run_key,
            )
        except Exception as exc:
            # The role runner failed to compose (e.g. cex_agent_loop absent, or a
            # refusal). Surface it as a degraded role, NEVER crash the crew. A
            # CapabilityRefused carries a reason; a generic error carries its repr.
            reason = getattr(exc, "reason", None) or type(exc).__name__
            return RoleResult(
                role_name=role_name,
                agent_id=agent_id,
                status="refused" if getattr(exc, "reason", None) else "degraded",
                errors=[f"role_run_failed: {reason}: {exc}"],
                metadata={"tools": list(tools), "coordinator": coordinator},
            )

        return RoleResult(
            role_name=role_name,
            agent_id=agent_id,
            artifact=str(getattr(result, "artifact", "") or ""),
            score=float(getattr(result, "score", 0.0) or 0.0),
            passed=bool(getattr(result, "passed", False)),
            status=str(getattr(result, "status", "completed") or "completed"),
            run_id=str(getattr(result, "run_id", "") or ""),
            steps=int(getattr(result, "steps", 0) or 0),
            steps_log=list(getattr(result, "steps_log", []) or []),
            errors=list(getattr(result, "errors", []) or []),
            metadata={
                "tools": list(tools),
                "coordinator": coordinator,
                "model_used": str(getattr(result, "model_used", "") or ""),
            },
        )

    def _role_intent(self, role_name: str, goal: str, coordinator: bool) -> str:
        """The human-readable F5 intent for a role's agent run."""
        base = goal or f"Execute the '{role_name}' role for crew {self.crew_name}"
        if coordinator:
            return f"[MANAGER] Coordinate the crew. {base}"
        return base

    def _format_handoff(self, upstream: list) -> str:
        """Render upstream role artifacts as the F3 INJECT handoff block (bounded).

        The handoff protocol: each downstream role receives the prior role's
        produced artifact as context. Truncated per artifact so a large upstream
        artifact cannot blow the next role's prompt."""
        if not upstream:
            return ""
        parts: list = []
        for r in upstream:
            if not isinstance(r, RoleResult) or not r.artifact:
                continue
            art = r.artifact
            if len(art) > 2000:
                art = art[:2000] + "\n[... truncated to 2KB ...]"
            parts.append(f"### Upstream role: {r.role_name} (score {r.score:.1f})\n{art}")
        return "\n\n".join(parts)

    # ------------------------------------------------------------------
    # Topology drivers.
    # ------------------------------------------------------------------
    def _run_sequential(self, writer, state: CrewRunState) -> None:
        """sequential: role N waits for role N-1; pass N-1's artifact into N's
        F3 INJECT context (the handoff protocol)."""
        last: RoleResult | None = None
        for role in self.roles:
            upstream = [last] if last is not None else []
            res = self._run_role(role, upstream, writer)
            state.roles[res.role_name] = res
            state.order.append(res.role_name)
            last = res

    # ------------------------------------------------------------------
    # R-172: speaker-selection strategy resolution + the round_robin
    # strategy's termination-aware loop.
    # ------------------------------------------------------------------
    def _resolve_strategy(self) -> str:
        """Resolve the effective speaker-selection strategy name (R-172).

        An explicit `speaker_selection.strategy` naming a KNOWN STRATEGY_TABLE
        entry wins. Otherwise (absent block, unknown name, or non-dict block)
        falls back to PROCESS_TO_STRATEGY[self.process] -- the exact legacy
        mapping, so a crew_template with NO speaker_selection block always
        resolves to the SAME strategy (and therefore the same runner
        function) it always has. NEVER raises."""
        sel = self.speaker_selection or {}
        explicit = str(sel.get("strategy") or "").strip().lower()
        if explicit and explicit in STRATEGY_TABLE:
            return explicit
        return PROCESS_TO_STRATEGY.get(self.process, "round_robin")

    def _run_round_robin(self, writer, state: CrewRunState) -> None:
        """round_robin strategy (R-172): AutoGen RoundRobinGroupChat semantics
        -- rotate through self.roles by index, checking the composable
        `termination` tree after every turn.

        ABSENT `termination` -> delegates straight to the untouched
        `_run_sequential` (byte-identical to pre-R-172: every role runs
        exactly once, in order). PRESENT `termination` -> loops role-by-role
        (same handoff semantics as _run_sequential: each turn receives only
        the immediately prior turn's artifact), evaluating the tree after
        each turn; stops the moment it is satisfied. A hard safety cap
        (len(roles) * _ROUND_ROBIN_SAFETY_MULTIPLE turns) guarantees this
        NEVER infinite-loops real agent-loop calls even if the tree is
        malformed or never fires -- hitting the cap is recorded as a warning,
        never an exception."""
        if not self.termination:
            self._run_sequential(writer, state)
            return
        if not self.roles:
            return
        n = len(self.roles)
        cap = n * _ROUND_ROBIN_SAFETY_MULTIPLE
        roles_done: list = []
        tokens_used = 0
        last: RoleResult | None = None
        round_num = 0
        for turn in range(cap):
            role = self.roles[turn % n]
            upstream = [last] if last is not None else []
            res = self._run_role(role, upstream, writer)
            state.roles[res.role_name] = res
            state.order.append(res.role_name)
            roles_done.append(res)
            tokens_used += max(1, len(res.artifact or "") // 4)
            last = res
            round_num += 1
            ctx = _TerminationCtx(
                round_num=round_num,
                roles_done=tuple(roles_done),
                last_result=last,
                tokens_used_estimate=tokens_used,
                charter_gate=self.charter_gate,
            )
            if _evaluate_termination(self.termination, ctx):
                state.warnings.append(
                    "R-172 termination satisfied after round %d (role '%s')"
                    % (round_num, role.get("role_name", "?"))
                )
                return
        state.warnings.append(
            "R-172 termination never satisfied -- stopped at the safety cap "
            "(%d rounds = %d roles x %d)" % (cap, n, _ROUND_ROBIN_SAFETY_MULTIPLE)
        )

    def _run_consensus(self, writer, state: CrewRunState) -> None:
        """consensus: all roles run independently (no handoff), then a merge step
        combines them into a consensus verdict (mean score + a merged artifact +
        a divergence measure). Offline-deterministic (no live vote)."""
        results: list = []
        for role in self.roles:
            res = self._run_role(role, [], writer)  # parallel-semantics: no upstream
            state.roles[res.role_name] = res
            state.order.append(res.role_name)
            results.append(res)
        state.gate.setdefault("_consensus", self._merge_consensus(results))

    def _run_hierarchical(self, writer, state: CrewRunState) -> None:
        """hierarchical: a MANAGER role coordinates WORKERS, then RE-PLANS.

        Bounded, offline-deterministic, ONE re-plan pass (no recursion):
          1. manager runs first (coordinator) with the worker roster as context;
          2. each worker runs with the manager's artifact as its F3 INJECT handoff;
          3. the manager runs a SECOND time (the synthesize / re-plan pass) with
             the workers' artifacts folded in as its upstream, producing a final
             synthesis artifact. The synthesis is keyed under a distinct
             "<manager> (synthesize)" role so it does NOT overwrite the manager's
             first result and is naturally counted by the F7 package gate (the
             weakest-link rule consumes every role in state.roles).
        The wire format of a RoleResult is unchanged; this only adds one more
        result to state.roles + state.order."""
        if not self.roles:
            return
        manager_role = self.roles[0]
        manager = self._run_role(manager_role, [], writer, coordinator=True)
        state.roles[manager.role_name] = manager
        state.order.append(manager.role_name)
        workers: list = []
        for role in self.roles[1:]:
            res = self._run_role(role, [manager], writer)
            state.roles[res.role_name] = res
            state.order.append(res.role_name)
            workers.append(res)
        # RE-PLAN: the manager synthesizes over the workers' artifacts (exactly
        # one pass -- bounded, no recursion). Persisted via the same _run_role ->
        # writer seam. Distinct role_name so it never collides with pass 1.
        synthesis = self._run_role(
            manager_role, workers, writer, coordinator=True,
            role_name_override=f"{manager.role_name} (synthesize)",
        )
        state.roles[synthesis.role_name] = synthesis
        state.order.append(synthesis.role_name)

    def _merge_consensus(self, results: list) -> dict:
        """Combine N parallel role results into a consensus verdict: mean score,
        a divergence (stddev) measure, and the count that passed. Mirrors the
        F7c COUNCIL consensus/divergence shape (offline)."""
        scored = [r.score for r in results if isinstance(r, RoleResult)]
        n = len(scored)
        if n == 0:
            return {"consensus_score": 0.0, "divergence": 0.0, "passed_count": 0, "n": 0}
        mean = sum(scored) / n
        var = sum((s - mean) ** 2 for s in scored) / n
        divergence = var ** 0.5
        passed_count = sum(1 for r in results if isinstance(r, RoleResult) and r.passed)
        return {
            "consensus_score": round(mean, 3),
            "divergence": round(divergence, 3),
            "passed_count": passed_count,
            "n": n,
        }

    # ------------------------------------------------------------------
    # Charter gate (F7 GOVERN coordination -- runs AFTER all roles).
    # ------------------------------------------------------------------
    def _charter_gate(self, state: CrewRunState) -> dict:
        """The charter-level F7 GOVERN gate: after every role completes, decide
        whether the crew package passes. For sequential/hierarchical the verdict
        is the MIN role score vs the threshold AND every role passed; for
        consensus it is the consensus mean vs the threshold. This is the hook the
        ADR calls for -- offline it is a threshold check; a live charter could
        swap in a cross-provider council here. NEVER raises."""
        roles = list(state.roles.values())
        if not roles:
            return {
                "passed": False,
                "score": 0.0,
                "threshold": self.charter_gate,
                "reason": "no roles executed",
                "process": self.process,
            }
        if self.process == "consensus":
            con = state.gate.get("_consensus") or self._merge_consensus(roles)
            score = float(con.get("consensus_score", 0.0))
            passed = score >= self.charter_gate and con.get("passed_count", 0) > 0
            reason = (
                f"consensus mean {score:.2f} vs gate {self.charter_gate:.2f}; "
                f"{con.get('passed_count', 0)}/{con.get('n', 0)} roles passed; "
                f"divergence {con.get('divergence', 0.0):.2f}"
            )
            return {
                "passed": bool(passed),
                "score": round(score, 3),
                "threshold": self.charter_gate,
                "reason": reason,
                "process": self.process,
                "consensus": con,
            }
        # sequential / hierarchical: the weakest link governs the package.
        # R-208 (SHOKUNIN) fix: "produced_unpersisted" is a documented terminal
        # status (cex_agent_loop.py:154 MultiStepResult.status contract -- the
        # role produced a passing artifact but its DB write failed/skipped) --
        # it was missing from this whitelist, so a role that legitimately
        # PASSED was wrongly treated as "not completed" and failed the whole
        # charter package. Vocabulary now matches the documented contract.
        min_score = min(r.score for r in roles)
        all_passed = all(r.passed for r in roles)
        completed = all(
            r.status in ("completed", "persisted", "produced", "produced_unpersisted")
            for r in roles
        )
        passed = all_passed and completed and min_score >= self.charter_gate
        reason = (
            f"min role score {min_score:.2f} vs gate {self.charter_gate:.2f}; "
            f"all_roles_passed={all_passed}; all_completed={completed}"
        )
        return {
            "passed": bool(passed),
            "score": round(min_score, 3),
            "threshold": self.charter_gate,
            "reason": reason,
            "process": self.process,
        }

    # ------------------------------------------------------------------
    # Main run.
    # ------------------------------------------------------------------
    def run(self, output_dir: Path | None = None) -> CrewRunState:
        """Execute the crew via the control plane. Dispatches the topology, runs
        the charter gate, optionally writes a run-state JSON, and returns the
        CrewRunState. NEVER raises for a role failure (a failed role is recorded
        as degraded/refused; the gate then fails the package honestly)."""
        state = CrewRunState(
            crew_name=self.crew_name,
            process=self.process,
            intent=self.intent,
            started_at=datetime.now().isoformat(),
        )

        if not self.roles:
            state.warnings.append("crew has no resolved roles -- nothing to run")
            state.completed_at = datetime.now().isoformat()
            state.gate = self._charter_gate(state)
            return state

        writer = self._resolve_writer()

        # R-172: resolve the effective strategy up front -- used both by the
        # (conditional, additive) banner line below and by the dispatch.
        strategy = self._resolve_strategy()

        print(f"\n{'=' * 60}")
        print(f"CEX Crew Control Plane -- {self.crew_name}")
        print(f"Process: {self.process} | Roles: {len(self.roles)} | Gate: {self.charter_gate}")
        if self.speaker_selection or self.termination:
            # Only ever printed for a crew_template that actually declares one
            # of the new R-172 blocks -- every existing crew_template's
            # console output is therefore untouched.
            print(
                "Strategy: %s%s"
                % (strategy, " | Termination: configured" if self.termination else "")
            )
        print(f"Tool resolver: {'BOUND' if self._live_tools_bound() else 'UNBOUND (offline-safe)'}")
        print(f"{'=' * 60}\n")

        # R-172: STRATEGY_TABLE dispatch replaces the old if/elif ladder (no
        # behavior change for any existing crew_template -- see the R-172
        # module comment above CONDITION_TABLE for the exact parity argument;
        # PROCESS_TO_STRATEGY restates the old ladder's own mapping as data).
        strategy_fn = STRATEGY_TABLE.get(strategy, _strategy_round_robin)
        strategy_fn(_StrategyCtx(self, writer, state))

        state.completed_at = datetime.now().isoformat()
        state.gate = self._charter_gate(state)

        # Console summary (mirrors the CrewRunner banner shape).
        for name in state.order:
            r = state.roles[name]
            print(
                f"  [{name}] {r.agent_id} -> status={r.status} "
                f"score={r.score:.1f} steps={r.steps} passed={r.passed}"
            )
        verdict = "PASS" if state.gate.get("passed") else "FAIL"
        print(f"\nCharter gate: {verdict} -- {state.gate.get('reason', '')}")

        if output_dir:
            self._write_state(state, output_dir)

        print(f"{'=' * 60}\n")
        return state

    def _live_tools_bound(self) -> bool:
        """True iff a LIVE tool resolver is bound on the agent loop module (the
        founder-gated seam). Default: UNBOUND (None) -> offline-safe. Best-effort
        -- a missing module reads as unbound."""
        try:
            if str(_TOOLS_DIR) not in sys.path:
                sys.path.insert(0, str(_TOOLS_DIR))
            import cex_agent_loop as _loop  # type: ignore[import]

            return getattr(_loop, "tool_resolver", None) is not None
        except Exception:
            return False

    def _write_state(self, state: CrewRunState, output_dir: Path) -> None:
        """Persist the control-plane run state to a JSON file (offline artifact)."""
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            return
        state_dict = {
            "crew_name": state.crew_name,
            "process": state.process,
            "intent": state.intent,
            "started_at": state.started_at,
            "completed_at": state.completed_at,
            "handoff_protocol": self.handoff_protocol,
            "charter_gate": self.charter_gate,
            "gate": state.gate,
            "order": state.order,
            "roles": {
                name: {
                    "agent_id": r.agent_id,
                    "status": r.status,
                    "score": r.score,
                    "passed": r.passed,
                    "run_id": r.run_id,
                    "steps": r.steps,
                    "errors": r.errors,
                    "metadata": r.metadata,
                }
                for name, r in state.roles.items()
            },
            "warnings": state.warnings,
        }
        try:
            (output_dir / "_control_plane_state.json").write_text(
                json.dumps(state_dict, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"\nControl-plane state: {output_dir / '_control_plane_state.json'}")
        except Exception:
            pass


def _coerce_float(value):
    """Coerce a scalar to a float, or None (a bool / non-number -> None). PURE."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except (ValueError, AttributeError):
            return None
    return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="CEX Crew Runner -- Lightweight DAG Executor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run (default) -- generate prompts:
  python cex_crew_runner.py --plan plan.json --output-dir out/

  # Single step only:
  python cex_crew_runner.py --plan plan.json --step 2 --output-dir out/

  # Real execution (calls LLM):
  python cex_crew_runner.py --plan plan.json --execute --output-dir out/

  # Full pipeline:
  python cex_8f_motor.py --intent "cria agente" --output /tmp/plan.json
  python cex_crew_runner.py --plan /tmp/plan.json --output-dir /tmp/crew/
        """,
    )
    parser.add_argument("--plan", help="Path to Motor 8F plan JSON")
    parser.add_argument(
        "--crew",
        help="Path to crew_template.md (alternative to --plan; parses roles into plan dict)",
    )
    parser.add_argument(
        "--charter",
        help="Optional team_charter.md path -- merged as mission/deliverables into the plan",
    )
    parser.add_argument("--output-dir", help="Output directory for prompts/outputs")
    parser.add_argument("--step", type=int, help="Execute only this step (by position 1-8)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Generate prompts without LLM calls (DEFAULT)",
    )
    parser.add_argument(
        "--execute", action="store_true", help="Real execution -- calls LLM via claude CLI (subscription)"
    )

    args = parser.parse_args()

    # Load plan (either from JSON or by compiling a crew_template.md)
    if not args.plan and not args.crew:
        print("ERROR: provide --plan <json> OR --crew <crew_template.md>", file=sys.stderr)
        sys.exit(1)

    if args.crew:
        crew_path = Path(args.crew)
        if not crew_path.exists():
            print(f"ERROR: crew_template not found: {crew_path}", file=sys.stderr)
            sys.exit(1)
        charter_path = Path(args.charter) if args.charter else None
        plan = CrewRunner.load_from_crew_template(crew_path, charter_path=charter_path)
        print(
            f"[CREW] loaded {crew_path.name}: "
            f"process={plan['crew_meta']['process']}, "
            f"roles={len(plan['crew_meta']['roles'])}, "
            f"active_builders={plan['total_builders']}"
        )
    else:
        plan_path = Path(args.plan)
        if not plan_path.exists():
            print(f"ERROR: Plan file not found: {plan_path}", file=sys.stderr)
            sys.exit(1)
        with open(plan_path, "r", encoding="utf-8") as f:
            plan = json.load(f)

    # Validate plan has expected structure
    if "functions" not in plan:
        print(
            "ERROR: Plan JSON missing 'functions' key. Is this a Motor 8F output?", file=sys.stderr
        )
        sys.exit(1)

    dry_run = not args.execute
    output_dir = Path(args.output_dir) if args.output_dir else None

    runner = CrewRunner(plan)
    state = runner.run(
        dry_run=dry_run,
        output_dir=output_dir,
        step_filter=args.step,
    )

    # Exit code: 1 if any builder failed
    failed = sum(1 for o in state.outputs.values() if o.status == "failed")
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    try:
        from cex_agent_io import wrap_main

        def _main_wrapper(argv):
            sys.argv = [sys.argv[0]] + argv
            main()
            return 0

        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_crew_runner"))
    except ImportError:
        main()
