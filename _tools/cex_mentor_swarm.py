#!/usr/bin/env python3
# -*- coding: ascii -*-
"""cex_mentor_swarm.py -- first-class GATED mentor-student swarm executor (W3).

WHY (measured 2026-06-08, .cex/runtime/decisions/bench2/BENCHMARK2_REPORT.md):
  Arm C (mentor-student: N Haiku producers in parallel + a Sonnet/Opus mentor
  review) was the CHEAPEST (~$0.04/KC) and FASTEST (~85s for 3, parallel) of the
  three topologies. BUT all 3 rail-governed Haiku producers fabricated wikilinks
  (7/7 = zero id-decls on disk). Conclusion: the producer-rail (prompt layer) is
  necessary but NOT sufficient -- the cheap tier needs a MECHANICAL tool gate
  between produce and commit. W2 shipped that gate (cex_wikilink_gate). This W3
  tool makes mentor-student a first-class, GATED execution mode.

WHAT (the pipeline):
  mentor plan (F1-F4, Opus/Sonnet) -> N student producers (F6, Haiku) in PARALLEL
  -> W2 wikilink gate on EACH output (the safety floor) -> mentor review (g3
  semantic, sampled) -> assemble (gate-clean set) -> ONE completion signal.

  The gate is the hard invariant: NO artifact with a fabricated wikilink can enter
  the assembled set. That is what this tool guarantees, and what the integration
  test asserts.

COMPOSE (reuse, do not reinvent) -- every heavy lift is an existing CEX tool:
  * mentor plan      -> cex_decompose.stage_1 (Opus F1-F4 -> prompt_package)
  * student produce  -> cex_intent.execute_prompt (the SAME F6 primitive the 8F
                        runner calls). We call it directly rather than
                        cex_decompose.stage_2 ON PURPOSE: stage_2 routes through
                        the runner's F8, which git-commits + rebuilds the index +
                        signals -- corpus side effects a sandbox swarm must NOT
                        trigger. The swarm owns gate -> review -> assemble -> one
                        signal itself, with full control over where output lands.
  * the GATE (W2)    -> cex_wikilink_gate.gate / repair_file (per artifact)
  * review (g3)      -> cex_score_python.score_fast (zero-LLM pre-filter) then
                        cex_score.score_hybrid(force_semantic=True) for flagged
  * council (opt)    -> cex_council.run_council (high-stakes sample)
  * signal           -> signal_writer.write_signal (once, at the end)
  * models           -> cex_model_resolver.resolve_shorthand + tiers.decompose
                        (provider-agnostic: no hardcoded "claude")

SANDBOX: producer output lands under .cex/runtime/swarm/<run_id>/ which is fully
  gitignored (.gitignore: ".cex/runtime/"). The corpus is never touched. Use
  --sandbox to override.

W5 (smart escalation + per-producer cost) -- IMPLEMENTED here:
  A gate-clean artifact scoring below its tier floor is RE-PRODUCED at a stronger
  tier (the ESCALATION_LADDER: haiku <7 -> sonnet <8 -> opus terminal), re-gated
  (W2) and re-scored at EACH tier. CHEAP-BY-DEFAULT: a producer at/above its tier
  floor stays on Haiku with zero re-run. Escalation is strictly SERIAL (the
  rate-limit/cadence) and records per-tier cost via cex_cost_tracker.record with
  subagent_id="<producer>#<tier>". The re-produce uses the SAME in-sandbox F6
  primitive as the bulk producers (cex_intent.execute_prompt with a stronger
  model_override) -- this IS "Stage-2 F6 at a higher tier" (cf.
  cex_decompose.stage_2) kept in-sandbox ON PURPOSE: stage_2 routes through the
  runner's F8 (git/index/signal corpus side effects) which a sandbox swarm must
  NOT trigger (see the COMPOSE note above). The gate stays absolute at every tier:
  an escalated re-produce that fabricates a link is NOT adopted.

CLI:
  python _tools/cex_mentor_swarm.py --nucleus n04 --task "..." --n 3
  python _tools/cex_mentor_swarm.py --nucleus n04 --task "..." --n 3 --mock-producer
  python _tools/cex_mentor_swarm.py --nucleus n04 --task "..." --n 3 --on-fail drop
  python _tools/cex_mentor_swarm.py --nucleus n04 --task "..." --n 3 --dry-run --json

Programmatic:
  from cex_mentor_swarm import run_swarm
  report = run_swarm("n04", "create kc_x", n=3, mock=True)
  assert report.blocked_fabricated >= 0

Exit codes:
  0 -- swarm ran; at least one artifact assembled OR dry-run
  1 -- input error (bad nucleus, empty task, n < 1)
  2 -- swarm ran but assembled NOTHING (every producer blocked or failed)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SWARM_ROOT = ROOT / ".cex" / "runtime" / "swarm"
sys.path.insert(0, str(ROOT / "_tools"))

VALID_NUCLEI = {"n01", "n02", "n03", "n04", "n05", "n06", "n07"}

EXIT_OK = 0
EXIT_INPUT = 1
EXIT_EMPTY = 2

DEFAULT_CONCURRENCY = 3   # rate-limit guard for Max (handoff: ~3-5 at a time)
QUALITY_FLOOR = 8.0       # spec W3 guardrail


# ===========================================================================
# Records (the per-run audit trail)
# ===========================================================================

@dataclass
class ProducerOutput:
    """Result of one student producer's F6 generation (pre-gate)."""
    index: int
    path: str | None
    ok: bool                 # generation succeeded + wrote a file
    tokens_in: int = 0
    tokens_out: int = 0
    wall_ms: float = 0.0
    error: str = ""


@dataclass
class GateResult:
    """Result of the W2 wikilink gate on one artifact."""
    ok: bool                 # no fabricated link survives (after policy)
    fabricated: list = field(default_factory=list)
    dropped: list = field(default_factory=list)
    policy: str = "reject"


@dataclass
class ReviewResult:
    """Result of the g3 mentor review on one artifact."""
    score: float | None = None
    mode: str = "skip"       # fast | hybrid | council | skip
    needs_llm: bool = False
    weakest: str = ""


@dataclass
class ProducerRecord:
    """The full lifecycle of one producer: produce -> gate -> review -> verdict."""
    index: int
    path: str | None
    gen: ProducerOutput
    gate: GateResult
    review: ReviewResult
    assembled: bool          # == gate.ok ; the hard safety invariant
    escalated: bool = False  # W5: climbed >= 1 tier (gate-clean but below floor)
    escalation_tier: str = "haiku"     # W5: FINAL tier reached (haiku|sonnet|opus)
    escalation_path: list = field(default_factory=list)  # W5: tiers visited, in order
    reason: str = ""


@dataclass
class SwarmReport:
    """Per-run report (cost / quality / sins), the BENCHMARK2-style byproduct."""
    run_id: str
    nucleus: str
    task: str
    n: int
    sandbox: str
    mentor_model: str
    producer_model: str
    on_fail: str
    dry_run: bool
    mock: bool
    records: list = field(default_factory=list)
    assembled_paths: list = field(default_factory=list)
    blocked_fabricated: int = 0       # producers blocked by the gate
    failed_producers: int = 0         # producers that errored before the gate
    escalated_count: int = 0          # W5: producers that climbed >= 1 tier
    by_escalation_tier: dict = field(default_factory=dict)  # W5: {tier: count}
    escalation_usd: float = 0.0       # W5: USD attributed to escalation re-runs
    total_tokens_in: int = 0
    total_tokens_out: int = 0
    est_usd: float = 0.0
    wall_ms: float = 0.0
    mean_score: float | None = None
    winner_path: str | None = None
    winner_score: float | None = None
    warnings: list = field(default_factory=list)
    signal_path: str | None = None

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


# ===========================================================================
# Model resolution (provider-agnostic -- no hardcoded "claude")
# ===========================================================================

def _load_decompose_tier() -> dict:
    """Read tiers.decompose from nucleus_models.yaml (stage_1/stage_2 defaults)."""
    cfg = ROOT / ".cex" / "config" / "nucleus_models.yaml"
    if not cfg.exists():
        return {}
    try:
        import yaml
        data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    return (data.get("tiers", {}) or {}).get("decompose", {}) or {}


def resolve_models(mentor: str = "", producer: str = "") -> tuple[str, str]:
    """Resolve (mentor_model, producer_model) with precedence:
       explicit arg > tiers.decompose (stage_1/stage_2) > alias shorthand.

    Mentor defaults to the Opus reasoning tier; producer to the Haiku F6 tier.
    All resolution flows through the alias map so a pin/bump in
    nucleus_models.yaml::model_aliases follows automatically.
    """
    tier = _load_decompose_tier()
    try:
        from cex_model_resolver import resolve_shorthand as _rs
    except Exception:
        def _rs(x):  # degrade: bare shorthand if resolver missing
            return x
    mentor_model = mentor or tier.get("stage_1", "") or _rs("opus")
    producer_model = producer or tier.get("stage_2", "") or _rs("haiku")
    return mentor_model, producer_model


# ===========================================================================
# LLM output cleaning (mirror of EightFRunner._clean_llm_output, standalone)
# ===========================================================================

def _clean_llm_output(text: str) -> str:
    """Strip preamble / code fences so output starts at the YAML frontmatter."""
    t = text.strip()
    idx = t.find("---\n")
    if idx > 0:
        t = t[idx:]
    elif idx < 0 and not t.startswith("---"):
        for marker in ("---\r\n", "---\n", "\n---"):
            pos = t.find(marker)
            if pos >= 0:
                t = t[pos:].lstrip("\n\r")
                break
    bt = chr(96) * 3
    if t.startswith(bt):
        nl = t.find(chr(10))
        if nl > 0:
            t = t[nl + 1:]
        close = t.rfind(bt)
        if close > 0:
            t = t[:close].strip()
    if not t.startswith("---"):
        t = "---\n" + t
    return t


def _est_tokens(text: str) -> int:
    """Cheap token estimate (word-count * 1.3). Used for the cost report only."""
    return int(len(text.split()) * 1.3) if text else 0


# ===========================================================================
# Planning (mentor F1-F4)
# ===========================================================================

def default_planner(nucleus: str, task: str, mentor_model: str,
                    sandbox: Path, dry_run: bool) -> Path | None:
    """Mentor plan via cex_decompose.stage_1 (Opus F1-F4 -> prompt_package).

    Returns the prompt_package path (under .cex/runtime/packages, gitignored), or
    None on failure / dry-run. The package is the shared plan every student reads.
    """
    try:
        from cex_decompose import stage_1 as decompose_stage_1
    except Exception as exc:
        print("[swarm] WARN: cex_decompose unavailable (%s); using stub plan" % exc,
              file=sys.stderr)
        return stub_planner(nucleus, task, mentor_model, sandbox, dry_run)
    # track_cost=False: the mentor plan is part of a sandbox swarm, keep it out of
    # the production cost_log.
    code, pkg = decompose_stage_1(nucleus, task, mentor_model, dry_run,
                                  track_cost=False)
    if dry_run:
        return None
    if code != 0 or pkg is None:
        print("[swarm] WARN: mentor plan (stage_1) failed (code=%s); stub plan" % code,
              file=sys.stderr)
        return stub_planner(nucleus, task, mentor_model, sandbox, dry_run)
    return pkg


def stub_planner(nucleus: str, task: str, mentor_model: str,
                 sandbox: Path, dry_run: bool) -> Path | None:
    """Zero-LLM planner: write a minimal prompt_package into the sandbox.

    Used by --mock-producer runs and as a degrade path. The body after the second
    `---` fence is what producers consume as their F6 prompt (matches the Mode B
    prompt_package contract).
    """
    if dry_run:
        return None
    sandbox.mkdir(parents=True, exist_ok=True)
    pkg = sandbox / "plan_package.md"
    content = (
        "---\n"
        "package_type: f6_prompt_package\n"
        "target_kind: knowledge_card\n"
        "target_nucleus: %s\n"
        "stage: 1\n"
        "mode: B\n"
        "---\n\n"
        "## TASK\n\n"
        "**Intent**: %s\n"
        "**Quality**: set quality: null (NEVER self-score).\n\n"
        "## CRITICAL OUTPUT RULES\n"
        "1. Output ONLY the artifact (frontmatter + body). No preamble.\n"
        "2. Start with `---` on line 1; close frontmatter with `---`.\n"
        "3. Ground every [[wikilink]]: only link ids that exist on disk.\n"
        % (nucleus, task)
    )
    pkg.write_text(content, encoding="ascii", errors="replace")
    return pkg


def _package_prompt(pkg_path: Path) -> str:
    """Extract the F6 prompt (body after the second '---') from a prompt_package."""
    text = pkg_path.read_text(encoding="utf-8", errors="replace")
    body_start = text.find("---", 3)
    if body_start > 0:
        return text[body_start + 3:].strip()
    return text


def augment_directive(original_text: str) -> str:
    """Build the P2.8 AUGMENT-in-place directive appended to the shared producer prompt.

    The apex daemon improves EXISTING corpus artifacts. Without this, the producer reads
    only the task STRING and REGENERATES the artifact from scratch -- the proven destructive
    failure (commit 7076ccf28, reverted): mentor_context.md regenerated 504->88 lines,
    dropping whole sections, yet scoring 8.1 (the density ruler rewards compression). This
    directive injects the FULL original artifact + an explicit preserve-and-extend contract,
    so the producer EXTENDS it: every existing heading and paragraph is echoed, and new
    depth/examples/sections are ADDED. The daemon's content-preservation guard
    (cex_apex_daemon.content_preserved) is the mechanical backstop that REJECTS any output
    which still drops a section -- this directive is the prompt-layer half of the same fix.
    """
    original_text = (original_text or "").strip()
    return (
        "## AUGMENT-IN-PLACE (MANDATORY -- this is an UPDATE, not a new artifact)\n\n"
        "You are IMPROVING the existing artifact shown in full below. You MUST EXTEND it;\n"
        "never regenerate it from scratch. Hard rules:\n"
        "1. PRESERVE every existing heading and paragraph -- copy them through verbatim.\n"
        "2. NEVER delete a section, shorten prose, or 'summarize' -- only ADD.\n"
        "3. ADD depth: new examples, new sub-sections, sharper detail, grounded links.\n"
        "4. The output body MUST be LONGER than the original and keep ALL original headings.\n"
        "5. Keep the same kind/topic and identity. Set quality: null.\n"
        "6. Ground every [[wikilink]]: only link ids that exist on disk.\n\n"
        "### EXISTING ARTIFACT (preserve all of this, then extend it)\n\n"
        + original_text + "\n"
    )


# ===========================================================================
# Production (student F6, parallel)
# ===========================================================================

def default_producer(index: int, pkg_path: Path, out_path: Path,
                     producer_model: str, track_cost: bool = False) -> ProducerOutput:
    """One student: read the package prompt, call F6 (execute_prompt), write output.

    Calls cex_intent.execute_prompt -- the SAME generation primitive the 8F runner
    uses for F6 -- with model_override=producer_model. No git / index / signal:
    the swarm owns those. Output lands at out_path (sandbox).
    """
    t0 = time.perf_counter()
    prompt = _package_prompt(pkg_path)
    # Light per-student nudge so N parallel students do not return byte-identical
    # text (deterministic label, not randomness).
    prompt = prompt + ("\n\n## VARIANT\nProducer #%d. Be concise and self-grounding."
                       % index)
    prev_track = os.environ.get("CEX_TRACK_COST")
    if not track_cost:
        os.environ["CEX_TRACK_COST"] = "0"
    try:
        from cex_intent import execute_prompt
        response = execute_prompt(prompt, model_override=producer_model)
    except Exception as exc:
        return ProducerOutput(index=index, path=None, ok=False,
                              wall_ms=(time.perf_counter() - t0) * 1000,
                              error="execute_prompt failed: %s" % exc)
    finally:
        if not track_cost:
            if prev_track is None:
                os.environ.pop("CEX_TRACK_COST", None)
            else:
                os.environ["CEX_TRACK_COST"] = prev_track
    art = _clean_llm_output(response)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(art, encoding="utf-8", errors="replace")
    return ProducerOutput(
        index=index, path=str(out_path), ok=True,
        tokens_in=_est_tokens(prompt), tokens_out=_est_tokens(art),
        wall_ms=(time.perf_counter() - t0) * 1000,
    )


def mock_producer(index: int, pkg_path: Path, out_path: Path,
                  producer_model: str, track_cost: bool = False) -> ProducerOutput:
    """Deterministic zero-LLM student for smoke / CI.

    Producer #0 deliberately FABRICATES a wikilink ([[Cmd_I_ground_or_abstain]],
    the exact bench2 Arm-C failure) so the smoke proves the gate catches it. All
    other producers emit clean, gate-passing throwaway KCs (no fabricated links).
    This makes the end-to-end pipeline reproducible without any model call.
    """
    t0 = time.perf_counter()
    fabricate = (index == 0)
    link_line = (
        "It builds on [[Cmd_I_ground_or_abstain]] for grounding discipline."
        if fabricate else
        "It documents the mentor-student swarm topology for the cheap tier."
    )
    body = (
        "---\n"
        "id: kc_swarm_smoke_%d\n"
        "kind: knowledge_card\n"
        "pillar: P01\n"
        "title: \"Swarm Smoke KC %d\"\n"
        "version: 1.0.0\n"
        "quality: null\n"
        "tags: [swarm, smoke, throwaway]\n"
        "tldr: \"Throwaway KC produced by mock student #%d for the W3 smoke run.\"\n"
        "---\n\n"
        "# Swarm Smoke KC %d\n\n"
        "## Summary\n\n"
        "This is a THROWAWAY knowledge_card emitted by mock student #%d to exercise\n"
        "the gated mentor-student swarm end to end (plan -> produce -> gate ->\n"
        "review -> assemble). %s\n\n"
        "## Detail\n\n"
        "The swarm runs N students in parallel, gates each output against the\n"
        "wikilink grounding authority, lets the mentor review the survivors, and\n"
        "assembles only the gate-clean set. The cheap tier produces; the tool gate\n"
        "guarantees no fabricated link can ship.\n"
        % (index, index, index, index, index, link_line)
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(body, encoding="ascii", errors="replace")
    return ProducerOutput(
        index=index, path=str(out_path), ok=True,
        tokens_in=_est_tokens(_package_prompt(pkg_path)) if pkg_path.exists() else 120,
        tokens_out=_est_tokens(body),
        wall_ms=(time.perf_counter() - t0) * 1000,
    )


# ===========================================================================
# The W2 gate (the safety floor) + g3 review
# ===========================================================================

def gate_artifact(path: str, on_fail: str = "reject") -> GateResult:
    """Run the W2 wikilink gate on one artifact. Policy:
       reject   -- fabrication blocks the artifact (gate.ok=False).
       escalate -- same block, but flag for mentor (gate.ok=False).
       drop     -- strip fabricated [[X]] -> plain text, then PASS (gate.ok=True).
    """
    try:
        from cex_wikilink_gate import gate as wl_gate
        from cex_wikilink_gate import repair_file
    except Exception as exc:
        # Fail CLOSED: if the gate is unavailable we cannot prove grounding, so we
        # block. A safety gate that silently passes on import error is worse than
        # useless.
        return GateResult(ok=False, fabricated=["<gate-unavailable: %s>" % exc],
                          policy=on_fail)
    ok, fabricated = wl_gate(path)
    if ok:
        return GateResult(ok=True, fabricated=[], policy=on_fail)
    if on_fail == "drop":
        dropped = repair_file(path, fabricated)
        # Re-gate to confirm the repair actually grounded the artifact.
        ok2, fab2 = wl_gate(path)
        return GateResult(ok=ok2, fabricated=fab2, dropped=dropped, policy=on_fail)
    return GateResult(ok=False, fabricated=fabricated, policy=on_fail)


def _fast_review(path: str) -> ReviewResult:
    """Zero-LLM mentor pre-filter: cex_score_python.score_fast (L1+L2)."""
    try:
        from cex_score_python import score_fast
    except Exception:
        return ReviewResult(score=None, mode="skip")
    fast = score_fast(path)
    note = ""
    notes = fast.get("notes") or []
    if notes:
        note = str(notes[0])
    return ReviewResult(score=fast.get("score"), mode="fast",
                        needs_llm=bool(fast.get("needs_llm")), weakest=note)


def _semantic_review(path: str) -> ReviewResult:
    """LLM-backed mentor deep-review: score_hybrid(force_semantic=True). One call.

    Used only on the SAMPLE the swarm selects (handoff g3: full for high-stakes,
    sample for bulk). On any failure it returns mode='skip' so the caller keeps
    the fast score.
    """
    try:
        from cex_score import score_hybrid
        hyb = score_hybrid(path, force_semantic=True)
        return ReviewResult(score=hyb.get("score"), mode=hyb.get("mode", "hybrid"),
                            weakest=str(hyb.get("weakest", "")))
    except Exception:
        return ReviewResult(score=None, mode="skip")


def _council_review(path: str, rubric_path: str = "") -> ReviewResult:
    """Cross-provider council deep-review (cex_council). Used on a high-stakes sample."""
    try:
        from cex_council import parse_crew_output, run_council
        out = run_council(path, rubric_path or None, ["anthropic", "google", "openai"])
        judges = parse_crew_output(out) if out else []
        if judges:
            cscore = sum(j["score"] for j in judges) / len(judges)
            return ReviewResult(score=round(cscore, 2), mode="council")
    except Exception:
        pass
    return ReviewResult(score=None, mode="skip")


def _review_pass(records: list, mode: str, council: bool) -> None:
    """Mentor g3 review over the gate-clean (assembled) records, in place.

    Sampling policy (handoff item 3 -- "full for high-stakes, sample for bulk"):
      none -- no scoring at all (gate-only run).
      fast -- score_fast on ALL assembled (zero LLM). DEFAULT; keeps the cheap
              tier cheap. The gate already guarantees grounding; this adds a
              structural/rubric quality signal at no token cost.
      auto -- fast on ALL + ONE LLM deep-review (score_hybrid force_semantic, or
              council) on the single best fast candidate (the mentor spot-check).
              Ranking stays on the fast scores for a consistent scale.
      full -- LLM deep-review on EVERY assembled artifact (high-stakes; ranking
              on the deep scores).
    """
    assembled = [r for r in records if r.assembled]
    if mode == "none" or not assembled:
        return
    for r in assembled:
        r.review = _fast_review(r.path)
    if mode == "fast":
        return
    if mode == "full":
        sample = assembled
    else:  # auto: spot-check the single best fast candidate
        sample = [max(assembled, key=lambda r: r.review.score or 0.0)]
    for r in sample:
        deep = _council_review(r.path) if council else _semantic_review(r.path)
        if deep.score is not None:
            r.review = deep


# ===========================================================================
# W5 escalation (smart, cheap-by-default) + per-producer/per-tier cost
# ===========================================================================

# The DEFAULT (Claude) escalation ladder. Each step: (tier_name, model_alias,
#   stop_score). A gate-clean artifact whose score is BELOW its tier's stop_score
#   is re-produced at the NEXT (stronger) tier. The last step is terminal
#   (stop_score=None -> accept whatever it produces). Thresholds are the
#   handoff's: Haiku <7 -> Sonnet; Sonnet <8 -> Opus.
# W6 (provider-agnostic): this constant is the Claude default; the cross-provider
#   ladders (google flash-lite>flash>pro, openai gpt_mini>gpt, ollama light>heavy)
#   live in nucleus_models.yaml::tiers.escalation_ladders and are selected per
#   producer by load_escalation_ladder(). aliases resolve via model_aliases, so
#   no full model slug (and no "if claude") is hardcoded in the decision flow.
ESCALATION_LADDER = (
    ("haiku", "haiku", 7.0),
    ("sonnet", "sonnet", 8.0),
    ("opus", "opus", None),
)

# Cadence: escalation is strictly serial (one producer, one tier at a time) --
# that IS the rate-limit. An optional inter-tier pause throttles real premium
# calls without slowing CI (default 0.0 -> no sleep).
ESCALATION_PAUSE_S = 0.0


def _provider_for_model(model: str) -> str:
    """Best-effort provider label from a resolved model id (cost_log dimension)."""
    m = (model or "").lower()
    if m.startswith("ollama") or "/" in m:
        return "ollama"
    if "gpt" in m or m.startswith(("o1", "o3", "o4")):
        return "openai"
    if "gemini" in m:
        return "google"
    return "claude"


def _resolve_alias(alias: str) -> str:
    """Resolve a shorthand (haiku/sonnet/opus/gemini_*/gpt*) to a concrete model
    id; identity if the resolver is unavailable (so the ladder still names a
    usable model)."""
    try:
        from cex_model_resolver import resolve_shorthand as _rs
        return _rs(alias) or alias
    except Exception:
        return alias


_LADDER_PROVIDERS = ("claude", "google", "openai", "ollama")


def _provider_ladders_from_config() -> dict:
    """Read tiers.escalation_ladders from nucleus_models.yaml (W6).

    Returns {provider: ((tier_name, model_alias, stop_score|None), ...)} -- the
    same (name, alias, stop) shape as ESCALATION_LADDER, one ladder per provider.
    Returns {} on any error so the caller degrades to the built-in Claude ladder.
    """
    cfg = ROOT / ".cex" / "config" / "nucleus_models.yaml"
    if not cfg.exists():
        return {}
    try:
        import yaml
        data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    raw = ((data.get("tiers", {}) or {}).get("escalation_ladders", {}) or {})
    out: dict = {}
    for provider, steps in raw.items():
        if not isinstance(steps, list):
            continue
        ladder: list = []
        for step in steps:
            if not isinstance(step, dict):
                continue
            name = str(step.get("tier", "")).strip()
            alias = str(step.get("alias", "")).strip()
            floor = step.get("floor", None)
            if floor is not None:
                try:
                    floor = float(floor)
                except (TypeError, ValueError):
                    floor = None
            if name and alias:
                ladder.append((name, alias, floor))
        if ladder:
            out[str(provider).strip()] = tuple(ladder)
    return out


def load_escalation_ladder(provider_or_model: str = "claude") -> tuple:
    """Return the cheap->...->premium escalation ladder for a provider (W6).

    `provider_or_model` may be a provider label (claude/google/openai/ollama) OR
    a model id / alias (e.g. "gemini_flash", or a resolved haiku/opus id) -- in
    the latter case the provider is inferred from the resolved model id. Reads
    tiers.escalation_ladders[provider] from nucleus_models.yaml; falls back to
    the built-in Claude ladder (ESCALATION_LADDER) when config is missing or the
    provider has no ladder. This keeps the Claude default byte-identical to the
    pre-W6 hardcoded constant (backward-compat) while letting a non-Claude
    producer escalate along ITS OWN provider's tiers -- no hardcoded "if claude".
    """
    label = (provider_or_model or "claude").strip()
    if label in _LADDER_PROVIDERS:
        provider = label
    else:
        provider = _provider_for_model(_resolve_alias(label))
    ladders = _provider_ladders_from_config()
    return ladders.get(provider) or ladders.get("claude") or ESCALATION_LADDER


def _ladder_start_index(producer_model: str, ladder=ESCALATION_LADDER) -> int:
    """Where on the (provider-specific) ladder the bulk producer already sits.
    Matches the resolved producer model against the given ladder; defaults to 0
    (the cheap tier).

    An empty/unknown producer model maps to index 0 -- the documented cheap
    producer tier. (Do NOT resolve "" through the alias map: an empty shorthand
    resolves to the Opus default, which would wrongly start at the terminal tier
    and suppress all escalation.)
    """
    if not producer_model:
        return 0
    resolved = _resolve_alias(producer_model).lower()
    for i, (name, alias, _stop) in enumerate(ladder):
        if name in resolved or _resolve_alias(alias).lower() == resolved:
            return i
    return 0


def default_escalator(index: int, pkg_path: Path, out_path: Path,
                      tier_model: str, track_cost: bool = False) -> ProducerOutput:
    """Re-produce one artifact at a stronger tier (the REAL escalation producer).

    This is the SAME in-sandbox F6 primitive as default_producer
    (cex_intent.execute_prompt with model_override=tier_model) -- i.e. "Stage-2 F6
    at a higher tier" (cf. cex_decompose.stage_2) kept in-sandbox ON PURPOSE so
    escalation never triggers the runner's F8 corpus side effects (git/index/
    signal). See the module docstring's W5 + COMPOSE notes.
    """
    return default_producer(index, pkg_path, out_path, tier_model,
                            track_cost=track_cost)


def mock_escalator(index: int, pkg_path: Path, out_path: Path,
                   tier_model: str, track_cost: bool = False) -> ProducerOutput:
    """Deterministic zero-LLM escalation re-producer (smoke / mock swarm runs).

    Writes a CLEAN (no-wikilink) throwaway KC so the W2 re-gate passes at every
    tier. Score is NOT decided here -- the caller's review_fn re-scores the file;
    tests inject a scripted review_fn to drive the ladder deterministically.
    """
    t0 = time.perf_counter()
    body = (
        "---\n"
        "id: kc_swarm_escalated_%d\n"
        "kind: knowledge_card\n"
        "pillar: P01\n"
        "title: \"Swarm Escalated KC %d (%s)\"\n"
        "version: 1.0.0\n"
        "quality: null\n"
        "tags: [swarm, escalation, throwaway]\n"
        "tldr: \"Re-produced by the W5 escalation ladder at tier %s.\"\n"
        "---\n\n"
        "# Swarm Escalated KC %d\n\n"
        "## Summary\n\n"
        "Re-produced at the %s tier by the W5 escalation ladder. This throwaway\n"
        "knowledge_card carries no wikilinks, so the W2 gate re-passes cleanly at\n"
        "every tier. The mentor-student swarm escalates only on failure.\n"
        % (index, index, tier_model, tier_model, index, tier_model)
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(body, encoding="ascii", errors="replace")
    return ProducerOutput(
        index=index, path=str(out_path), ok=True,
        tokens_in=_est_tokens(_package_prompt(pkg_path)) if pkg_path.exists() else 120,
        tokens_out=_est_tokens(body),
        wall_ms=(time.perf_counter() - t0) * 1000,
    )


def escalate_record(rec: ProducerRecord, sandbox_dir: Path, pkg_path: Path,
                    *, producer_model: str = "", escalator_fn=None,
                    gate_fn=None, review_fn=None, cost_record_fn=None,
                    on_fail: str = "reject", mission: str = "",
                    session: str | None = None, nucleus: str = "",
                    task: str = "",
                    ladder=ESCALATION_LADDER,
                    pause_s: float = ESCALATION_PAUSE_S) -> float:
    """W5 REAL escalation for ONE gate-clean record. Walks the tier ladder:
    re-produce (F6 at the next model) -> re-gate (W2) -> re-score, climbing while
    the current tier's score is below its stop_score. Mutates `rec` in place:
      rec.review            -> the best (final-tier) review
      rec.path              -> the adopted (gate-clean) escalated artifact
      rec.escalation_path   -> tiers visited, e.g. ["haiku","sonnet","opus"]
      rec.escalation_tier   -> final tier reached
      rec.escalated         -> True iff it climbed >= 1 tier

    Per-tier cost is recorded via cost_record_fn(provider, model, in, out, usd,
    subagent_id="producer_<i>#<tier>") -- but ONLY when escalation actually occurs
    (a producer that stays on Haiku incurs NO cost_log entry: cheap-by-default).

    Seams (escalator_fn / gate_fn / review_fn / cost_record_fn) default to the
    real implementations; tests inject deterministic fixtures. Returns the USD
    attributed to this record's escalation (0.0 if it stayed put).
    """
    if escalator_fn is None:
        escalator_fn = default_escalator
    if gate_fn is None:
        gate_fn = gate_artifact
    if review_fn is None:
        review_fn = _fast_review
    if cost_record_fn is None:
        try:
            from cex_cost_tracker import record as cost_record_fn  # type: ignore
        except Exception:
            cost_record_fn = None

    start = _ladder_start_index(producer_model, ladder)
    cur = start
    score = rec.review.score
    if score is None:
        return 0.0  # no signal to escalate against (review=none)

    # W3 WIRE_DORMANT: snapshot the STUDENT (start-tier) signal before climbing so
    # that, on a successful teacher fix, we can distill the corrective procedure.
    _student_start_score = score
    _student_weakest = getattr(rec.review, "weakest", "") or ""
    _student_floor = ladder[start][2] if ladder[start][2] is not None else None

    # Lazily-built ledger so a non-escalating producer writes NOTHING.
    tiers_visited = [ladder[start][0]]
    tier_costs: list[tuple] = [(
        ladder[start][0], _resolve_alias(producer_model or ladder[start][1]),
        rec.gen.tokens_in, rec.gen.tokens_out)]

    while cur < len(ladder):
        name, _alias, stop = ladder[cur]
        if stop is None or score is None or score >= stop:
            break  # tier floor satisfied (or terminal) -> stop climbing
        nxt = cur + 1
        if nxt >= len(ladder):
            break
        if pause_s:
            time.sleep(pause_s)
        n_name, n_alias, _n_stop = ladder[nxt]
        n_model = _resolve_alias(n_alias)
        out_path = sandbox_dir / ("producer_%d__%s.md" % (rec.index, n_name))
        gen = escalator_fn(rec.index, pkg_path, out_path, n_model)
        if not gen.ok or not gen.path:
            rec.reason += "; ESCALATE %s->%s FAILED: %s" % (
                name, n_name, gen.error or "no output")
            break
        gate = gate_fn(gen.path, on_fail)
        # Cost is incurred regardless of the gate outcome (the call was made).
        tiers_visited.append(n_name)
        tier_costs.append((n_name, n_model, gen.tokens_in, gen.tokens_out))
        if not gate.ok:
            # The gate is ABSOLUTE: a fabricated link at this tier is NOT adopted.
            # Keep the last gate-clean artifact + its score; stop climbing.
            rec.reason += "; ESCALATE %s->%s GATE_BLOCK: %s (kept prior)" % (
                name, n_name, gate.fabricated)
            break
        new_review = review_fn(gen.path)
        # Adopt the escalated, gate-clean artifact.
        rec.path = gen.path
        rec.gate = gate
        rec.review = new_review
        score = new_review.score
        cur = nxt

    rec.escalation_path = tiers_visited
    rec.escalation_tier = ladder[cur][0]
    rec.escalated = cur > start

    # W3 WIRE_DORMANT: a TEACHER tier fixed what the STUDENT tier failed -> distill
    # the corrective procedure into a recallable learning_record (GATED on the
    # teacher's self-eval passing inside distill_on_escalation). degrade-never:
    # kill-switch CEX_DISTILL_WRITEBACK=0 or any error -> no-op; the swarm is
    # unaffected. No escalation (student already SOTA) -> not entered.
    if rec.escalated and rec.gate is not None and rec.gate.ok:
        try:
            from cex_distill_writeback import distill_on_escalation

            distill_on_escalation(
                task=task,
                nucleus=nucleus,
                student_model=_resolve_alias(producer_model or ladder[start][1]),
                student_score=_student_start_score,
                teacher_model=_resolve_alias(ladder[cur][1]),
                teacher_score=score,
                gate_ok=bool(rec.gate.ok),
                floor=(_student_floor if _student_floor is not None else 8.0),
                escalation_path=list(tiers_visited),
                student_weakest=_student_weakest,
            )
        except Exception:
            pass  # distillation is best-effort; never break the swarm

    # Record cost ONLY for an escalated record (cheap-by-default: a producer that
    # never climbed leaves the cost_log untouched, per the sandbox contract).
    spent = 0.0
    if rec.escalated and cost_record_fn is not None:
        for tier_name, tier_model, tin, tout in tier_costs:
            usd = _estimate_cost(tier_model, tin, tout)
            spent += usd
            try:
                cost_record_fn(
                    _provider_for_model(tier_model), tier_model, tin, tout,
                    usd=usd, session=session, mission=mission, nucleus=nucleus,
                    subagent_id="producer_%d#%s" % (rec.index, tier_name))
            except Exception as exc:  # cost logging must never break the swarm
                rec.reason += "; cost-record failed: %s" % exc
                break
    if rec.escalated:
        rec.reason += "; ESCALATED %s (path %s)" % (
            rec.escalation_tier, "->".join(tiers_visited))
    return round(spent, 6)


# ===========================================================================
# The swarm
# ===========================================================================

def run_swarm(nucleus: str, task: str, n: int = 3, sandbox: str | Path | None = None,
              mentor_model: str = "", producer_model: str = "",
              on_fail: str = "reject", review: str = "fast", council: bool = False,
              dry_run: bool = False, mock: bool = False,
              concurrency: int = DEFAULT_CONCURRENCY, quality_floor: float = QUALITY_FLOOR,
              planner_fn=None, producer_fn=None, escalator_fn=None,
              escalate: bool = True, mission: str = "",
              do_signal: bool = True, run_id: str = "",
              augment_path: str | None = None) -> SwarmReport:
    """Run the gated mentor-student swarm. Returns a SwarmReport.

    planner_fn / producer_fn / escalator_fn are injectable seams (the test
    substitutes fixtures for zero-LLM determinism). Defaults are chosen from `mock`:
      mock=False -> default_planner (Opus stage_1) + default_producer (Haiku F6)
                    + default_escalator (execute_prompt at the escalated tier)
      mock=True  -> stub_planner (no LLM) + mock_producer + mock_escalator (all
                    deterministic)
    escalate=False disables the W5 escalation pass entirely (gate+review only).

    augment_path (P2.8): path to an EXISTING corpus artifact this run is improving. When
    set, the original artifact + a preserve-and-extend directive (augment_directive) are
    injected into the shared producer package, so producers EXTEND the artifact instead of
    regenerating it from scratch (the destructive 504->88 gut-job). Unset -> a from-scratch
    create (the original swarm behaviour). The injection mutates only the gitignored package.
    """
    t0 = time.perf_counter()
    nucleus = nucleus.lower()
    if not run_id:
        # No Date.now() footgun here (plain Python); derive a stable-ish id.
        run_id = "swarm_%s_%d" % (nucleus, int(time.time()))
    sandbox_dir = Path(sandbox) if sandbox else (SWARM_ROOT / run_id)

    m_model, p_model = resolve_models(mentor_model, producer_model)

    report = SwarmReport(
        run_id=run_id, nucleus=nucleus, task=task, n=n,
        sandbox=str(sandbox_dir), mentor_model=m_model, producer_model=p_model,
        on_fail=on_fail, dry_run=dry_run, mock=mock,
    )

    # --- W4 amortization guard (spec W3 item 3): warn, do not hard-refuse. ---
    if n < 2:
        report.warnings.append(
            "n=%d: a single producer is not a swarm. For one-off premium / "
            "live-tool / zero-fabrication-tolerance work prefer Mode A (solo). "
            "Proceeding anyway." % n)

    if planner_fn is None:
        planner_fn = stub_planner if mock else default_planner
    if producer_fn is None:
        producer_fn = mock_producer if mock else default_producer

    # --- Plan (mentor F1-F4) ---
    pkg_path = planner_fn(nucleus, task, m_model, sandbox_dir, dry_run)
    if dry_run:
        report.warnings.append("dry-run: planned only, no producers spawned.")
        report.wall_ms = (time.perf_counter() - t0) * 1000
        return report
    if pkg_path is None:
        report.warnings.append("planner returned no package; aborting.")
        report.wall_ms = (time.perf_counter() - t0) * 1000
        return report

    sandbox_dir.mkdir(parents=True, exist_ok=True)

    # --- P2.8 AUGMENT: improving a REAL corpus artifact -> inject the original body + a
    #     preserve-and-extend directive into the shared package so EVERY producer (and the
    #     escalator, which re-reads the same package) EXTENDS the artifact instead of
    #     regenerating it from scratch. Off when augment_path is unset (a from-scratch
    #     create). Mutates only the gitignored package file. ---
    if augment_path:
        try:
            original_text = Path(augment_path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            original_text = ""
        if original_text.strip():
            try:
                cur = pkg_path.read_text(encoding="utf-8", errors="replace")
                pkg_path.write_text(
                    cur.rstrip() + "\n\n" + augment_directive(original_text) + "\n",
                    encoding="utf-8", errors="replace")
                print("[swarm] AUGMENT: extending %s (%d chars) in-place; producers "
                      "must preserve all sections" % (Path(augment_path).name,
                                                      len(original_text)),
                      file=sys.stderr)
            except OSError as exc:
                report.warnings.append("augment inject failed: %s" % exc)

    # --- Produce (N students, parallel, cadenced) ---
    outputs: dict[int, ProducerOutput] = {}
    workers = max(1, min(concurrency, n))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = {
            pool.submit(producer_fn, i, pkg_path,
                        sandbox_dir / ("producer_%d.md" % i), p_model): i
            for i in range(n)
        }
        for fut in as_completed(futs):
            i = futs[fut]
            try:
                outputs[i] = fut.result()
            except Exception as exc:
                outputs[i] = ProducerOutput(index=i, path=None, ok=False,
                                            error="producer raised: %s" % exc)

    # --- Gate + verdict (per artifact, in index order). The GATE is the hard
    #     safety floor: a fabricated wikilink BLOCKS assembly, full stop. ---
    for i in range(n):
        gen = outputs.get(i) or ProducerOutput(index=i, path=None, ok=False,
                                               error="no output")
        report.total_tokens_in += gen.tokens_in
        report.total_tokens_out += gen.tokens_out

        if not gen.ok or not gen.path:
            report.failed_producers += 1
            report.records.append(ProducerRecord(
                index=i, path=gen.path, gen=gen,
                gate=GateResult(ok=False, fabricated=[], policy=on_fail),
                review=ReviewResult(), assembled=False,
                reason="producer_failed: %s" % (gen.error or "unknown")))
            continue

        gate = gate_artifact(gen.path, on_fail=on_fail)
        if not gate.ok:
            report.blocked_fabricated += 1
            report.records.append(ProducerRecord(
                index=i, path=gen.path, gen=gen, gate=gate, review=ReviewResult(),
                assembled=False,
                reason="GATE_BLOCK: fabricated %s" % gate.fabricated))
            continue

        report.records.append(ProducerRecord(
            index=i, path=gen.path, gen=gen, gate=gate, review=ReviewResult(),
            assembled=True,
            reason="assembled (gate-clean)%s"
                   % ("; dropped %s" % gate.dropped if gate.dropped else "")))
        report.assembled_paths.append(gen.path)

    # --- Mentor g3 review (sampled) over the gate-clean set ---
    _review_pass(report.records, review, council)

    # --- W5 escalation (smart, cheap-by-default; serial = the rate-limit) ---
    # A gate-clean artifact below its tier floor is re-produced at a stronger tier
    # (cheap<floor -> mid<floor -> premium), re-gated, re-scored. A producer
    # at/above its floor stays on the cheap tier with zero re-run and zero
    # cost_log entry.
    # W6 (provider-agnostic): the ladder is selected from the producer model's
    # provider (load_escalation_ladder) -- claude climbs haiku>sonnet>opus, a
    # gemini producer climbs flash-lite>flash>pro, etc. No hardcoded "if claude".
    if escalator_fn is None:
        escalator_fn = mock_escalator if mock else default_escalator
    ladder = load_escalation_ladder(p_model)
    if escalate:
        for rec in report.records:
            if not rec.assembled or rec.review.score is None:
                continue
            report.escalation_usd += escalate_record(
                rec, sandbox_dir, pkg_path,
                producer_model=p_model, escalator_fn=escalator_fn,
                on_fail=on_fail, mission=mission, nucleus=nucleus,
                task=task, ladder=ladder)
            if rec.escalated:
                report.escalated_count += 1
            report.by_escalation_tier[rec.escalation_tier] = \
                report.by_escalation_tier.get(rec.escalation_tier, 0) + 1
        report.escalation_usd = round(report.escalation_usd, 6)

    # --- Scores + winner (computed AFTER escalation so escalated scores win;
    #     assembled_paths rebuilt to follow any escalation re-point of rec.path) ---
    report.assembled_paths = [r.path for r in report.records
                              if r.assembled and r.path]
    scores = [r.review.score for r in report.records
              if r.assembled and r.review.score is not None]
    if scores:
        report.mean_score = round(sum(scores) / len(scores), 2)
        best = max((r for r in report.records
                    if r.assembled and r.review.score is not None),
                   key=lambda r: r.review.score, default=None)
        if best is not None:
            report.winner_path = best.path
            report.winner_score = best.review.score

    # Surface any assembled artifact STILL below the quality floor after the
    # escalation ladder is exhausted (e.g. stuck at Opus) -- human-in-the-loop.
    below = [r for r in report.records
             if r.assembled and r.review.score is not None
             and r.review.score < quality_floor]
    if below:
        report.warnings.append(
            "%d assembled artifact(s) below quality floor %.1f after escalation: "
            "%s -- human review." % (
                len(below), quality_floor,
                ", ".join("#%d=%.1f@%s" % (r.index, r.review.score, r.escalation_tier)
                          for r in below)))

    # Cost estimate (clearly an estimate; tokens are word-count derived).
    report.est_usd = _estimate_cost(p_model, report.total_tokens_in,
                                    report.total_tokens_out)
    report.wall_ms = (time.perf_counter() - t0) * 1000

    # --- Signal (ONCE, at the end) ---
    if do_signal and not dry_run:
        report.signal_path = _emit_signal(report)

    # Persist the report next to the artifacts (gitignored sandbox).
    try:
        (sandbox_dir / "swarm_report.json").write_text(
            json.dumps(report.to_dict(), indent=2), encoding="utf-8")
        (sandbox_dir / "swarm_report.md").write_text(
            render_report_md(report), encoding="utf-8")
    except Exception:
        pass

    return report


def _estimate_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    """USD estimate via cex_cost_tracker.estimate_usd; 0.0 if unavailable."""
    try:
        from cex_cost_tracker import estimate_usd
        return round(estimate_usd(model, tokens_in, tokens_out), 6)
    except Exception:
        return 0.0


def _emit_signal(report: SwarmReport) -> str | None:
    """Emit ONE completion signal for the whole swarm run."""
    try:
        from signal_writer import write_signal
    except Exception:
        return None
    status = "complete" if report.assembled_paths else "partial"
    score = report.mean_score if report.mean_score is not None else (
        9.0 if report.assembled_paths else 0.0)
    try:
        return write_signal(
            report.nucleus, status, float(score),
            mock=report.mock, run_id=report.run_id,
            assembled=len(report.assembled_paths),
            blocked_fabricated=report.blocked_fabricated,
        )
    except Exception as exc:
        print("[swarm] WARN: signal failed: %s" % exc, file=sys.stderr)
        return None


# ===========================================================================
# Reporting
# ===========================================================================

def render_report_md(r: SwarmReport) -> str:
    """BENCHMARK2-style per-run report (cost / quality / sins)."""
    lines = [
        "# Mentor-Student Swarm Run -- %s" % r.run_id,
        "",
        "> nucleus=%s n=%d mentor=%s producer=%s on-fail=%s%s"
        % (r.nucleus.upper(), r.n, r.mentor_model, r.producer_model, r.on_fail,
           " [MOCK]" if r.mock else ""),
        "",
        "## Task",
        r.task,
        "",
        "## Outcome",
        "| Metric | Value |",
        "|--------|-------|",
        "| Producers | %d |" % r.n,
        "| Assembled (gate-clean) | %d |" % len(r.assembled_paths),
        "| **Blocked by gate (fabrication)** | **%d** |" % r.blocked_fabricated,
        "| Failed before gate | %d |" % r.failed_producers,
        "| Escalated (climbed >= 1 tier, W5) | %d |" % r.escalated_count,
        "| Final tier distribution | %s |" % (
            ", ".join("%s:%d" % (t, c) for t, c in sorted(r.by_escalation_tier.items()))
            if r.by_escalation_tier else "n/a"),
        "| Escalation cost (USD) | $%.4f |" % r.escalation_usd,
        "| Mean score | %s |" % (r.mean_score if r.mean_score is not None else "n/a"),
        "| Winner | %s (%s) |" % (
            Path(r.winner_path).name if r.winner_path else "none",
            r.winner_score if r.winner_score is not None else "n/a"),
        "| Est tokens (in/out) | %d / %d |" % (r.total_tokens_in, r.total_tokens_out),
        "| Est cost (USD) | $%.4f |" % r.est_usd,
        "| Wall-clock | %.0f ms |" % r.wall_ms,
        "",
        "## Per-producer",
        "| # | verdict | gate | score | tier | path |",
        "|---|---------|------|-------|------|------|",
    ]
    for rec in r.records:
        verdict = "ASSEMBLE" if rec.assembled else "BLOCK"
        gate = "clean" if rec.gate.ok else ("FAB:%s" % ",".join(rec.gate.fabricated))
        score = rec.review.score if rec.review.score is not None else "-"
        name = Path(rec.path).name if rec.path else "-"
        tier = "->".join(rec.escalation_path) if rec.escalation_path else rec.escalation_tier
        lines.append("| %d | %s | %s | %s | %s | %s |"
                     % (rec.index, verdict, gate, score, tier, name))
    if r.warnings:
        lines += ["", "## Warnings"] + ["- %s" % w for w in r.warnings]
    lines += [
        "",
        "## Invariant",
        "**0 fabricated wikilinks in the assembled set** -- the W2 gate runs on "
        "every producer output before assembly. Blocked: %d." % r.blocked_fabricated,
        "",
    ]
    return "\n".join(lines)


def print_report(r: SwarmReport) -> None:
    print(render_report_md(r))


# ===========================================================================
# CLI
# ===========================================================================

def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="cex_mentor_swarm -- gated mentor-student swarm executor (W3)")
    ap.add_argument("--nucleus", required=True, help="Target nucleus (n01..n07)")
    ap.add_argument("--task", required=True, help="Natural-language intent")
    ap.add_argument("--n", type=int, default=3, help="Number of student producers")
    ap.add_argument("--sandbox", default="", help="Output dir (default: .cex/runtime/swarm/<run>)")
    ap.add_argument("--mentor-model", default="", help="Override mentor model (alias/id)")
    ap.add_argument("--producer-model", default="", help="Override producer model (alias/id)")
    ap.add_argument("--on-fail", choices=["reject", "drop", "escalate"], default="reject",
                    help="Gate policy on fabrication (default: reject)")
    ap.add_argument("--review", choices=["fast", "auto", "full", "none"], default="fast",
                    help="Mentor review depth: fast=score_fast all (zero LLM, default); "
                         "auto=fast + 1 sampled semantic deep-review; full=semantic all; "
                         "none=gate-only")
    ap.add_argument("--council", action="store_true", help="Cross-provider council (high-stakes)")
    ap.add_argument("--mock-producer", action="store_true", dest="mock",
                    help="Deterministic zero-LLM producers (smoke / CI); #0 fabricates")
    ap.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                    help="Max parallel producers (rate-limit guard; default 3)")
    ap.add_argument("--mission", default="", help="Tag escalation cost entries with this mission")
    ap.add_argument("--no-escalate", action="store_true",
                    help="Disable the W5 escalation pass (gate + review only)")
    ap.add_argument("--no-signal", action="store_true", help="Do not emit a completion signal")
    ap.add_argument("--dry-run", action="store_true", help="Plan only; spawn no producers")
    ap.add_argument("--json", action="store_true", help="Emit the report as JSON")
    args = ap.parse_args(argv)

    nucleus = args.nucleus.lower()
    if nucleus not in VALID_NUCLEI:
        print("[swarm] FAIL: unknown nucleus %s (need n01..n07)" % nucleus, file=sys.stderr)
        return EXIT_INPUT
    if not args.task.strip():
        print("[swarm] FAIL: empty --task", file=sys.stderr)
        return EXIT_INPUT
    if args.n < 1:
        print("[swarm] FAIL: --n must be >= 1", file=sys.stderr)
        return EXIT_INPUT

    report = run_swarm(
        nucleus=nucleus, task=args.task, n=args.n,
        sandbox=args.sandbox or None,
        mentor_model=args.mentor_model, producer_model=args.producer_model,
        on_fail=args.on_fail, review=args.review, council=args.council,
        dry_run=args.dry_run, mock=args.mock, concurrency=args.concurrency,
        escalate=not args.no_escalate, mission=args.mission,
        do_signal=not args.no_signal,
    )

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print_report(report)

    if args.dry_run:
        return EXIT_OK
    if not report.assembled_paths:
        print("[swarm] no artifact assembled (all blocked or failed).", file=sys.stderr)
        return EXIT_EMPTY
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
