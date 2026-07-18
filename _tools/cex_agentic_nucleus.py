#!/usr/bin/env python3
"""cex_agentic_nucleus.py: Minimal ReAct loop for free agentic nuclei.

Runs a single nucleus task via a local Ollama model with native tool calling.
Default model is qwen2.5-coder:7b (tool-capable, no <think> pollution, deeper
reports); llama3.1:8b stays available as a fallback via --model.
Tools: list_dir, read_file, grep, done.

Usage:
    python _tools/cex_agentic_nucleus.py \\
        --nucleus n01 \\
        --handoff .cex/runtime/handoffs/LEVERAGE_MAP_n01.md \\
        --output .cex/runtime/out/leverage_map_n01.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib import request

ROOT = Path(__file__).resolve().parent.parent
MAX_READ_BYTES = 8000
MAX_GREP_LINES = 40

try:  # shared R-056/R-141 resolver: canonical OLLAMA_HOST + legacy aliases
    from cex_ollama_env import resolve_ollama_host
except ImportError:  # package-style import path
    from _tools.cex_ollama_env import resolve_ollama_host

OLLAMA_CHAT_URL = resolve_ollama_host() + "/api/chat"


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List entries in a directory (files + subdirs). Path relative to repo root.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": f"Read a text file (capped at {MAX_READ_BYTES} bytes). Path relative to repo root.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep",
            "description": f"Search for a pattern in files under a directory. Returns up to {MAX_GREP_LINES} matching lines.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                    "path": {"type": "string"},
                },
                "required": ["pattern", "path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "done",
            "description": "Submit the final markdown report. Call this ONLY when analysis is complete.",
            "parameters": {
                "type": "object",
                "properties": {"report": {"type": "string"}},
                "required": ["report"],
            },
        },
    },
]


def safe_path(p: str) -> Path:
    """Resolve path and ensure it stays inside repo root."""
    candidate = (ROOT / p).resolve() if not Path(p).is_absolute() else Path(p).resolve()
    if ROOT not in candidate.parents and candidate != ROOT:
        raise ValueError(f"path escape: {p}")
    return candidate


def tool_list_dir(path: str) -> str:
    p = safe_path(path)
    if not p.exists():
        return f"ERROR: path does not exist: {path}"
    if not p.is_dir():
        return f"ERROR: not a directory: {path}"
    entries = []
    for e in sorted(p.iterdir())[:80]:
        kind = "d" if e.is_dir() else ""
        entries.append(f"{kind} {e.name}")
    return json.dumps(entries)


def tool_read_file(path: str) -> str:
    p = safe_path(path)
    if not p.exists():
        return f"ERROR: file does not exist: {path}"
    if p.is_dir():
        return f"ERROR: is a directory: {path}"
    try:
        data = p.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"ERROR: {e}"
    if len(data) > MAX_READ_BYTES:
        data = data[:MAX_READ_BYTES] + f"\n... [truncated, total {len(data)} bytes]"
    return data


def tool_grep(pattern: str, path: str) -> str:
    p = safe_path(path)
    if not p.exists():
        return f"ERROR: path does not exist: {path}"
    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        return f"ERROR: bad regex: {e}"
    matches = []
    targets = [p] if p.is_file() else list(p.rglob("*.md")) + list(p.rglob("*.py")) + list(p.rglob("*.yaml"))
    for f in targets[:200]:
        try:
            for i, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if regex.search(line):
                    rel = f.relative_to(ROOT).as_posix()
                    matches.append(f"{rel}:{i}: {line[:200]}")
                    if len(matches) >= MAX_GREP_LINES:
                        return "\n".join(matches) + f"\n... [capped at {MAX_GREP_LINES}]"
        except Exception:
            continue
    if not matches:
        return "NO_MATCHES"
    return "\n".join(matches)


def execute_tool(name: str, args: dict) -> str:
    try:
        if name == "list_dir":
            return tool_list_dir(args["path"])
        if name == "read_file":
            return tool_read_file(args["path"])
        if name == "grep":
            return tool_grep(args["pattern"], args["path"])
        return f"ERROR: unknown tool {name}"
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {e}"


def call_ollama(model: str, messages: list, tools: list, timeout: int = 180,
                num_predict: int = 1500) -> dict:
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "tools": tools,
        "options": {"num_predict": num_predict, "temperature": 0.3},
    }
    data = json.dumps(payload).encode()
    req = request.Request(
        OLLAMA_CHAT_URL,
        data=data, headers={"Content-Type": "application/json"},
    )
    with request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode())
    return body.get("message", {})


def forced_synthesis(model: str, messages: list, reads_performed: int,
                     verbose: bool = True, num_predict: int = 2048,
                     min_report_bytes: int = 0) -> str:
    """Final call with tools DISABLED so the model must emit its report.

    Local models such as llama3.1:8b keep making tool calls every iteration and
    never call done(). When the ReAct loop exhausts max_iters this would return
    a 9-byte "MAX_ITERS" stub. Instead we make ONE extra call with an empty
    tools list and an explicit instruction to output the complete report now.
    With no tools available the model cannot make another tool call, so it
    produces a usable markdown report from the evidence already gathered.

    Anti-shallow (when min_report_bytes > 0): if that forced report is still
    thinner than min_report_bytes, make exactly ONE more bounded expansion call
    and keep whichever result is longer. This mirrors the done()-path guard for
    the max_iters branch (the proven failure is done(), but a thin forced report
    on the no-done() path deserves the same one-shot push for depth).

    Bounded: at most two calls under the existing urlopen timeout. No done() path
    is involved, so the anti-fabrication guard never blocks this synthesis (the
    required reads already happened during the loop).
    """
    if verbose:
        print(f"  [SYNTHESIS] max_iters reached after {reads_performed} read/grep "
              "call(s). Forcing final report (tools disabled).", flush=True)
    synth_messages = messages + [{
        "role": "user",
        "content": (
            f"You have gathered enough evidence ({reads_performed} read/grep "
            "call(s)). STOP calling tools -- do NOT request any more files. "
            "Output your COMPLETE final markdown report NOW, including ALL "
            "required sections from the handoff (for example: Verification, "
            "New Wired Tools, Still Missing, Next Iteration). Base every claim "
            "only on evidence you already gathered above; if a section has no "
            "evidence, write 'None observed'. Do not fabricate. Begin the "
            "report now."
        ),
    }]
    try:
        msg = call_ollama(model, synth_messages, tools=[], num_predict=num_predict)
    except Exception as e:
        if verbose:
            print(f"  [SYNTHESIS] call failed: {type(e).__name__}: {e}", flush=True)
        return ""
    report = msg.get("content", "") or ""
    # Anti-shallow: one bounded expansion retry if the forced report is thin.
    if min_report_bytes and len(report.strip()) < min_report_bytes:
        if verbose:
            print(f"  [SYNTHESIS] thin ({len(report)}B < {min_report_bytes}). "
                  "One expansion retry.", flush=True)
        expand_messages = synth_messages + [
            {"role": "assistant", "content": report},
            {"role": "user", "content": (
                f"That report is only {len(report)} bytes -- too thin. Expand EVERY "
                "required section using the specific evidence you already gathered "
                "(file paths, names, counts you actually saw above). Do NOT fabricate. "
                "Re-output the COMPLETE report now, longer and more detailed.")},
        ]
        try:
            msg2 = call_ollama(model, expand_messages, tools=[], num_predict=num_predict)
            report2 = msg2.get("content", "") or ""
            if len(report2.strip()) > len(report.strip()):
                report = report2
        except Exception as e:
            if verbose:
                print(f"  [SYNTHESIS] expansion failed: {type(e).__name__}: {e}", flush=True)
    return report


def agentic_loop(model: str, system: str, task: str, max_iters: int = 15,
                 verbose: bool = True, min_iters: int = 4,
                 history: list | None = None,
                 require_reads_before_done: int = 2,
                 min_report_bytes: int = 1100) -> dict:
    """Run ReAct loop. If history is passed, append to it (REPL continuation).

    Anti-fabrication: done() is rejected if fewer than
    `require_reads_before_done` read_file/grep calls happened first.

    Anti-shallow: done() is rejected if the report is thinner than
    `min_report_bytes`, up to MAX_SHALLOW_REJECTIONS times, so the model gathers
    more evidence and resubmits a COMPLETE report. The final allowed attempt is
    accepted as-is (bounded -- never infinite-loops). This catches the early
    thin done() (e.g. a 286-byte report) that the size-blind anti-fab guard let
    through. Set min_report_bytes=0 to disable.
    """
    if history is None:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": task},
        ]
    else:
        messages = history
        messages.append({"role": "user", "content": task})
    trace = []
    t0 = time.time()
    nudges_used = 0
    MAX_NUDGES = 2
    reads_performed = 0
    fabrication_rejections = 0
    MAX_FABRICATION_REJECTIONS = 2
    shallow_rejections = 0
    MAX_SHALLOW_REJECTIONS = 2
    for i in range(max_iters):
        if verbose:
            print(f"[iter {i+1}/{max_iters}]", flush=True)
        msg = call_ollama(model, messages, TOOLS)
        content = msg.get("content", "")
        tool_calls = msg.get("tool_calls", [])

        if not tool_calls:
            parsed = parse_text_tool_call(content)
            if parsed:
                tool_calls = parsed
                if verbose:
                    print(f"  [fallback parse] {tool_calls[0]['function']['name']}", flush=True)

        if not tool_calls:
            # Stop guard: nudge up to MAX_NUDGES times if shallow (iters too low OR content thin)
            shallow = (i + 1) < min_iters or len(content) < 1500
            if nudges_used < MAX_NUDGES and shallow:
                nudges_used += 1
                if verbose:
                    print(f"  [GUARD {nudges_used}/{MAX_NUDGES}] iters={i+1} content={len(content)}B. Nudging.", flush=True)
                messages.append({"role": "assistant", "content": content})
                messages.append({"role": "user", "content":
                    f"You stopped after {i+1} tool uses with only {len(content)} bytes of output. "
                    "That is not enough. The handoff requires a complete report with ALL required "
                    "sections (Verification, New Wired Tools, Still Missing, Next Iteration). "
                    "Use list_dir/read_file/grep to gather more evidence. When ready, call "
                    "done(report=<full markdown>) to submit."})
                continue
            # Nudges exhausted (or non-shallow stop). If the parting content is
            # still under the depth floor, route it through ONE forced synthesis
            # pass (tools disabled + bounded expansion) so a no-tool-call stop
            # cannot return a sub-min report -- mirrors the max_iters path. This
            # closes the n06-style 257B no_tool_call miss.
            if len(content) < min_report_bytes:
                synth = forced_synthesis(model, messages, reads_performed, verbose,
                                         min_report_bytes=min_report_bytes)
                if len(synth.strip()) > len(content.strip()):
                    trace.append({"iter": i + 1, "type": "forced_synthesis",
                                  "bytes": len(synth), "reads": reads_performed})
                    if verbose:
                        print(f"  -> no_tool_call thin ({len(content)}B); "
                              f"forced_synthesis {len(synth)}B", flush=True)
                    messages.append({"role": "assistant", "content": synth})
                    return {"ok": True, "final": synth, "iters": i + 1,
                            "wall": round(time.time() - t0, 1), "trace": trace,
                            "reason": "forced_synthesis", "history": messages}
            trace.append({"iter": i + 1, "type": "text_only", "content": content[:300]})
            if verbose:
                print(f"  -> no tool_calls, stopping. Final: {content[:200]}", flush=True)
            return {"ok": True, "final": content, "iters": i + 1,
                    "wall": round(time.time() - t0, 1), "trace": trace,
                    "reason": "no_tool_call", "history": messages}

        messages.append({"role": "assistant", "content": content, "tool_calls": tool_calls})

        for tc in tool_calls:
            name = tc.get("function", {}).get("name", "")
            args = tc.get("function", {}).get("arguments", {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except Exception:
                    args = {}

            if verbose:
                arg_preview = json.dumps(args)[:120]
                print(f"  tool: {name}({arg_preview})", flush=True)

            if name == "done":
                report = args.get("report", "")
                # Anti-fabrication guard: require evidence-gathering first
                if reads_performed < require_reads_before_done and \
                   fabrication_rejections < MAX_FABRICATION_REJECTIONS:
                    fabrication_rejections += 1
                    if verbose:
                        print(f"  [ANTI-FAB {fabrication_rejections}/{MAX_FABRICATION_REJECTIONS}] "
                              f"done() with only {reads_performed} reads < {require_reads_before_done}. "
                              "Rejecting.", flush=True)
                    trace.append({"iter": i + 1, "type": "done_rejected",
                                  "reads": reads_performed, "bytes": len(report)})
                    messages.append({"role": "tool", "content":
                        f"REJECTED: done() called with only {reads_performed} read_file/grep "
                        "call(s). You must gather evidence by reading at least "
                        f"{require_reads_before_done} files/grep results before submitting. "
                        "Do NOT fabricate numbers or claims. Call list_dir, read_file, or grep "
                        "to gather real evidence from the repo, THEN call done()."})
                    continue
                # Anti-shallow guard: a too-thin report is rejected so the model
                # gathers more evidence and resubmits a COMPLETE one. Mirrors the
                # anti-fabrication pattern above; bounded by MAX_SHALLOW_REJECTIONS
                # so the final allowed attempt is always accepted (never loops).
                if len(report) < min_report_bytes and \
                   shallow_rejections < MAX_SHALLOW_REJECTIONS:
                    shallow_rejections += 1
                    if verbose:
                        print(f"  [ANTI-SHALLOW {shallow_rejections}/{MAX_SHALLOW_REJECTIONS}] "
                              f"done() report {len(report)}B < {min_report_bytes}. "
                              "Rejecting.", flush=True)
                    trace.append({"iter": i + 1, "type": "done_shallow_rejected",
                                  "reads": reads_performed, "bytes": len(report)})
                    messages.append({"role": "tool", "content":
                        f"REJECTED: your report is only {len(report)} bytes -- too thin. "
                        "Gather more evidence (read/grep the specific tools and files the "
                        "handoff names) and submit a COMPLETE report with ALL required "
                        "sections, each with real detail (file paths, names, counts you "
                        "actually saw). Do NOT fabricate. Then call done()."})
                    continue
                trace.append({"iter": i + 1, "type": "done", "bytes": len(report),
                              "reads": reads_performed})
                return {"ok": True, "final": report, "iters": i + 1,
                        "wall": round(time.time() - t0, 1), "trace": trace,
                        "reason": "done_called", "history": messages}

            result = execute_tool(name, args)
            if name in ("read_file", "grep"):
                reads_performed += 1
            trace.append({"iter": i + 1, "tool": name, "args": args,
                          "result_bytes": len(result), "reads_so_far": reads_performed})
            if verbose:
                print(f"    -> {len(result)} bytes (reads={reads_performed})", flush=True)
            messages.append({"role": "tool", "content": result[:4000]})

    # Loop exhausted max_iters without done() or a no-tool-call stop. The model
    # kept calling tools. FIX B: force ONE final synthesis call (tools disabled)
    # so it emits a real report instead of the old 9-byte "MAX_ITERS" stub.
    final = forced_synthesis(model, messages, reads_performed, verbose,
                             min_report_bytes=min_report_bytes)
    if final.strip():
        trace.append({"iter": max_iters, "type": "forced_synthesis",
                      "bytes": len(final), "reads": reads_performed})
        if verbose:
            print(f"  -> forced_synthesis: {len(final)} bytes", flush=True)
        messages.append({"role": "assistant", "content": final})
        return {"ok": True, "final": final, "iters": max_iters,
                "wall": round(time.time() - t0, 1), "trace": trace,
                "reason": "forced_synthesis", "history": messages}
    # Synthesis returned nothing usable -- last resort, keep the honest stub.
    trace.append({"iter": max_iters, "type": "max_iters_no_synthesis"})
    return {"ok": False, "final": "MAX_ITERS", "iters": max_iters,
            "wall": round(time.time() - t0, 1), "trace": trace,
            "reason": "max_iters", "history": messages}


SYSTEM_PROMPT = """You are a CEX nucleus agent running inside the CEX repository on Windows.

REPO ROOT: {ROOT}
OS: Windows (paths use forward slashes, relative to repo root).
ALL PATHS MUST BE RELATIVE. Examples: "_tools", "N01_intelligence", "archetypes/builders".
FORBIDDEN: "/home/user/...", "/tmp/...", "C:\\\\Users\\\\..." -- those do not exist here.
FORBIDDEN: glob patterns in paths ("N06_*", "_tools/*.py") -- use exact paths or use grep instead.

Available tools (invoke via tool_calls, NOT JSON in content):
- list_dir(path)      -- list entries under a relative path
- read_file(path)     -- read a file (UTF-8, capped at 8KB)
- grep(pattern, path) -- regex search under a dir or file
- done(report)        -- submit final markdown report (ends the loop)

========================================
MANDATORY: 8F PIPELINE (every task, every time)
========================================
You do NOT just call tools and write a report. You execute the 8F reasoning pipeline:

F1 CONSTRAIN: Read .cex/kinds_meta.json (grep for the kind you care about).
              Identify pillar, naming rule, max_bytes.
F2 BECOME:    Read archetypes/builders/{{kind}}-builder/bld_model_{{kind}}.md
              and bld_prompt_{{kind}}.md. Load your identity.
F3 INJECT:    Read P01_knowledge/library/kind/kc_{{kind}}.md for the knowledge card.
              grep for similar artifacts (e.g., compiled/, N0x/). Collect 2-3 examples.
F4 REASON:    Plan your report: which sections, what claims, what evidence for each.
F5 CALL:      Any remaining tool calls needed to fill evidence gaps.
F6 PRODUCE:   Draft the report with ALL required sections from the handoff.
F7 GOVERN:    Self-check: does every claim cite a file you read? are all required
              sections present? are any numbers fabricated?
F8 COLLABORATE: Call done(report=<full markdown>).

ANTI-FABRICATION RULES:
1. Every numeric claim ("N builders", "X files") MUST come from a tool result.
   If you did not read/grep for it, DO NOT state it.
2. Every file path you reference MUST exist (you saw it via list_dir or read_file).
3. If the handoff lists required sections, include them ALL -- even if empty ("None observed").
4. Do NOT drift: stay on the tool/artifact the handoff asks about. Do not pivot to
   "comprehensive vocabulary atlas" or other tangents.

DISCIPLINE:
- Minimum 4-6 tool calls BEFORE done(). The runner will reject premature done() calls.
- Target >= 1500 bytes in your final report. Thin reports get nudged.
- If a required section has no evidence yet, go gather it -- do not guess.

If the user asks a conversational question (no file to read), answer briefly
without inventing paths."""


JSON_CALL_RE = re.compile(r'\{\s*"name"\s*:\s*"([^"]+)"\s*,\s*"(?:parameters|arguments)"\s*:\s*(\{[^{}]*\})\s*\}', re.DOTALL)


def parse_text_tool_call(content: str):
    """Fallback: parse JSON-in-text tool calls emitted by llama3.1."""
    m = JSON_CALL_RE.search(content)
    if not m:
        return None
    name = m.group(1)
    try:
        args = json.loads(m.group(2))
    except Exception:
        return None
    return [{"function": {"name": name, "arguments": args}}]


def auto_commit(nucleus: str, output_path: Path, mission: str,
                model: str = "qwen2.5-coder:7b") -> None:
    """Stage output + commit with nucleus attribution -- gitignore-aware.

    The agentic report often lands under .cex/runtime/ (gitignored), so a naive
    `git add + git commit` either errored or printed "nothing to commit" while
    this function still reported a commit. safe_artifact_commit partitions a
    gitignored path out (kept on disk; NEVER force-added) and reports honestly.
    """
    sys.path.insert(0, str(ROOT / "_tools"))
    try:
        from cex_git_safe import safe_artifact_commit
    except ImportError as e:
        print(f"[{nucleus}] commit skipped (helper missing): {e}", flush=True)
        return
    msg = f"[{nucleus.upper()}] {mission}: agentic report via {model}"
    res = safe_artifact_commit([output_path], msg, cwd=ROOT)
    if output_path.is_relative_to(ROOT):
        rel = output_path.relative_to(ROOT).as_posix()
    else:
        rel = str(output_path)
    if res.get("committed"):
        print(f"[{nucleus}] committed {rel}", flush=True)
    elif res.get("skipped_ignored"):
        print(f"[{nucleus}] not committed (gitignored, on disk): {rel}", flush=True)
    else:
        print(f"[{nucleus}] not committed: {res.get('reason', '')}", flush=True)


def interactive_repl(nucleus: str, model: str, last_result: dict, output_path: Path) -> None:
    """Drop into REPL so user can ask follow-ups or approve commit."""
    print("\n" + "=" * 60, flush=True)
    print(f"  {nucleus.upper()} READY - interactive mode", flush=True)
    print("  Commands:", flush=True)
    print("    <type a task>  -> run another agentic loop", flush=True)
    print("    :show          -> show last output", flush=True)
    print("    :commit        -> git commit the output", flush=True)
    print("    :quit          -> exit window", flush=True)
    print("=" * 60, flush=True)

    system = SYSTEM_PROMPT + f"\n\nYou are nucleus {nucleus.upper()}."
    # Carry history from the initial loop so REPL keeps mission context
    history = last_result.get("history")
    if history is None:
        history = [{"role": "system", "content": system}]
    repl_turn = 0

    while True:
        try:
            user_input = input(f"\n[{nucleus}]> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            break

        if not user_input:
            continue
        if user_input == ":quit":
            break
        if user_input == ":show":
            print(last_result.get("final", ""))
            continue
        if user_input == ":commit":
            auto_commit(nucleus, output_path, "INTERACTIVE", model)
            continue
        if user_input == ":reset":
            history = [{"role": "system", "content": system}]
            print(f"[{nucleus}] history reset", flush=True)
            continue

        # run new agentic task, preserve history, write to separate file
        repl_turn += 1
        result = agentic_loop(model, system, user_input, max_iters=10,
                              verbose=True, history=history)
        history = result.get("history", history)
        repl_out = output_path.with_name(f"{output_path.stem}.repl{repl_turn}.md")
        repl_out.write_text(result["final"], encoding="utf-8")
        last_result = result
        print(f"\n[{nucleus}] done: {result['reason']}, {result['iters']} iters, "
              f"{result['wall']}s, saved {repl_out.name}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--nucleus", required=True, help="nucleus id (n01..n06)")
    p.add_argument("--handoff", required=True, help="path to handoff .md file")
    p.add_argument("--output", required=True, help="where to write the final report")
    p.add_argument("--model", default="qwen2.5-coder:7b")
    p.add_argument("--max-iters", type=int, default=15)
    p.add_argument("--require-reads", type=int, default=2,
                   help="Minimum read_file/grep calls before done() accepted (anti-fabrication)")
    p.add_argument("--min-report-bytes", type=int, default=1100,
                   help="Reject done() reports thinner than this (anti-shallow); "
                        "bounded retries, then accept. 0 disables.")
    p.add_argument("--quiet", action="store_true")
    p.add_argument("--interactive", action="store_true", help="drop into REPL after loop")
    p.add_argument("--auto-commit", action="store_true", help="git commit output after loop")
    p.add_argument("--mission", default="TASK", help="mission tag for commit messages")
    args = p.parse_args()

    handoff_path = Path(args.handoff)
    if not handoff_path.exists():
        print(f"ERROR: handoff not found: {args.handoff}", file=sys.stderr)
        return 1
    task = handoff_path.read_text(encoding="utf-8")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    system = SYSTEM_PROMPT + f"\n\nYou are nucleus {args.nucleus.upper()}. Your directory is N0{args.nucleus[-1]}_*/"

    print("=" * 60, flush=True)
    print(f"  {args.nucleus.upper()} - {args.mission} - {args.model}", flush=True)
    print("=" * 60, flush=True)
    print(f"Handoff: {args.handoff}", flush=True)
    print(f"Output:  {args.output}", flush=True)
    print("", flush=True)

    result = agentic_loop(args.model, system, task,
                          max_iters=args.max_iters, verbose=not args.quiet,
                          require_reads_before_done=args.require_reads,
                          min_report_bytes=args.min_report_bytes)

    output_path.write_text(result["final"], encoding="utf-8")
    trace_path = output_path.with_suffix(".trace.json")
    trace_path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")

    print("\n" + "=" * 60, flush=True)
    print(f"[{args.nucleus}] COMPLETE: {result['reason']}, {result['iters']} iters, "
          f"{result['wall']}s, {len(result['final'])} bytes", flush=True)
    print(f"[{args.nucleus}] Output: {output_path}", flush=True)
    print("=" * 60, flush=True)

    if args.auto_commit:
        auto_commit(args.nucleus, output_path, args.mission, args.model)

    if args.interactive:
        interactive_repl(args.nucleus, args.model, result, output_path)

    return 0 if result["ok"] else 2


if __name__ == "__main__":
    try:
        from cex_agent_io import wrap_main

        def _main_wrapper(argv):
            sys.argv = [sys.argv[0]] + argv
            return main()

        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_agentic_nucleus"))
    except ImportError:
        sys.exit(main())
