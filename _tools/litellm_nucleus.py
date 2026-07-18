#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LiteLLM Nucleus Runner -- routes nucleus task through local LiteLLM proxy.

Drops in next to ollama_nucleus.py. Same shape (read handoff -> call LLM ->
write file -> compile -> signal) but instead of hitting Ollama directly it
talks to the LiteLLM proxy on http://localhost:4000 using the OpenAI-compatible
/v1/chat/completions endpoint and the cex-n0X virtual model alias.

This means:
- Routing decisions live in .cex/config/litellm_config.yaml (single source).
- Fallback chains (Anthropic -> Gemini -> Ollama gemma4:26b -> qwen3:14b) are
  enforced by the proxy, not duplicated in spawn scripts.
- Every call can be logged for QLoRA fine-tuning later (LiteLLM callbacks).

Usage (from boot/n0X_litellm.ps1):
    python _tools/litellm_nucleus.py --nucleus N01
    python _tools/litellm_nucleus.py --nucleus N03 --model glm-5.2-fast

Model resolution (R-345 -- highest wins):
    1. CEX_MODEL_OVERRIDE env var (orchestrator channel; spawn_solo/grid -Model)
    2. --model CLI flag
    3. cex-{nucleus} virtual alias (legacy default; byte-identical when 1+2 absent)

Env:
    LITELLM_BASE_URL    default http://localhost:4000
    LITELLM_MASTER_KEY  required (read from .env or shell)
    CEX_TASK_FILE       override handoff path
    CEX_MODEL_OVERRIDE  model override (beats --model; see resolution order)

Exit codes:
    0  ok -- structural gate PASS, signal status=complete
    1  task file missing or empty
    2  proxy HTTP/connection error
    3  empty or malformed completion
    4  LITELLM_MASTER_KEY missing
    5  structural gate FAIL -- signal status=failed, no fabricated score (R-345)
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import requests

ROOT = Path(__file__).resolve().parent.parent

NUCLEUS_ROLES = {
    "N01": ("Intelligence", "research, analysis, competitive intel, papers, benchmarks"),
    "N02": ("Marketing", "copy, ads, campaigns, brand voice, CTAs"),
    "N03": ("Builder", "artifact construction via 8F pipeline, builders, ISOs"),
    "N04": ("Knowledge", "RAG, knowledge cards, embeddings, indexing, taxonomy"),
    "N05": ("Operations", "code review, testing, CI/CD, deployment"),
    "N06": ("Commercial", "pricing, courses, sales funnels, monetization"),
    "N07": ("Orchestrator", "dispatch, grid, consolidate, orchestration"),
}

SYS_TEMPLATE = """You are {nuc_id} {role} of CEX.
Domain: {domain}.
You produce CEX artifacts with valid YAML frontmatter (---...---) including:
id, kind, pillar, title, version: 1.0.0, quality: null (never self-score).

WHEN ASKED TO CREATE A FILE:
1. Output the COMPLETE file contents as raw markdown.
2. Do NOT wrap in code fences (no ```markdown).
3. Do NOT add preamble like "Here is the file:".
4. Start directly with --- (frontmatter opening).
5. End with the last line of markdown body.

Your response will be written verbatim to the target file path."""


def load_master_key() -> Optional[str]:
    """Read LITELLM_MASTER_KEY from env or .env file."""
    key = os.environ.get("LITELLM_MASTER_KEY")
    if key:
        return key
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line.startswith("LITELLM_MASTER_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def call_litellm(model: str, system: str, prompt: str, base_url: str, api_key: str,
                 max_tokens: int = 4096, temperature: float = 0.3) -> dict:
    """Single chat-completion request to LiteLLM proxy."""
    t0 = time.time()
    r = requests.post(
        f"{base_url.rstrip('/')}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        },
        timeout=600,
    )
    r.raise_for_status()
    data = r.json()
    data["_wall_s"] = round(time.time() - t0, 1)
    return data


def resolve_model(nucleus: str, cli_model: Optional[str] = None,
                  env: Optional[dict] = None) -> "tuple[str, str]":
    """Resolve the model alias sent to the proxy (R-345).

    Precedence (highest wins):
        1. CEX_MODEL_OVERRIDE env var (orchestrator channel; spawn_solo/grid -Model)
        2. cli_model (--model flag)
        3. cex-{nucleus} virtual alias (legacy default -- byte-identical when 1+2 absent)

    Returns (model, source) where source is one of
    "env:CEX_MODEL_OVERRIDE" | "flag:--model" | "default".
    """
    env_map = os.environ if env is None else env
    env_val = (env_map.get("CEX_MODEL_OVERRIDE") or "").strip()
    if env_val:
        return env_val, "env:CEX_MODEL_OVERRIDE"
    if cli_model and cli_model.strip():
        return cli_model.strip(), "flag:--model"
    return f"cex-{nucleus.lower()}", "default"


GATE_CHECKS = ("frontmatter_parses", "id_present", "kind_present", "body_non_empty")


def _fallback_parse_frontmatter(content: str) -> Optional[dict]:
    """Minimal line-anchored frontmatter parse, used only when cex_shared is
    not importable. Conservative: returns None (-> gate check FAILS) on any
    doubt. Fail-closed by design -- an unevaluable gate must not pass."""
    text = content.strip()
    if not text.startswith("---"):
        return None
    m = re.search(r"^---\s*$", text[3:], flags=re.MULTILINE)
    if not m:
        return None
    try:
        import yaml
        data = yaml.safe_load(text[3:3 + m.start()])
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _body_after_frontmatter(content: str) -> str:
    """Text after the closing frontmatter fence. No opening fence -> the whole
    text is body; unterminated fence -> no body."""
    text = content.strip()
    if not text.startswith("---"):
        return text
    m = re.search(r"^---\s*$", text[3:], flags=re.MULTILINE)
    if not m:
        return ""
    return text[3 + m.end():]


def structural_gate(content: str) -> dict:
    """F7 GOVERN structural gate on the generated output (R-345).

    Checks: frontmatter parses (canonical cex_shared.parse_frontmatter when
    importable, fail-closed fallback otherwise) + id present + kind present +
    non-empty body. Returns {passed, score, checks, parser} where score is the
    REAL check fraction scaled to 0-10 -- never a fabricated constant.
    """
    parser = "cex_shared"
    try:
        try:
            from cex_shared import parse_frontmatter
        except ImportError:
            from _tools.cex_shared import parse_frontmatter
        fm = parse_frontmatter(content)
    except Exception:
        parser = "fallback"
        fm = _fallback_parse_frontmatter(content)
    fm_map = fm if isinstance(fm, dict) else {}
    checks = {
        "frontmatter_parses": isinstance(fm, dict),
        "id_present": bool(str(fm_map.get("id") or "").strip()),
        "kind_present": bool(str(fm_map.get("kind") or "").strip()),
        "body_non_empty": bool(_body_after_frontmatter(content).strip()),
    }
    passed_n = sum(1 for v in checks.values() if v)
    return {
        "passed": passed_n == len(GATE_CHECKS),
        "score": round(10.0 * passed_n / len(GATE_CHECKS), 1),
        "checks": checks,
        "parser": parser,
    }


def _emit_signal(nucleus_lower: str, status: str, score: float, **extra) -> bool:
    """Write an honest completion signal via the canonical signal_writer.
    status vocabulary: signal_writer accepts ^[a-z_]+$ ('complete'/'failed' ok).
    Never raises -- signal transport failure must not mask the run's exit code."""
    try:
        try:
            from signal_writer import write_signal
        except ImportError:
            from _tools.signal_writer import write_signal
        write_signal(nucleus_lower, status, score, **extra)
        return True
    except Exception as e:
        print(f"[{nucleus_lower.upper()}] Signal skipped: {e}")
        return False


def clean_frontmatter(content: str) -> str:
    """Strip code fences and trailing whitespace per line."""
    content = content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        content = "\n".join(lines)
    return "\n".join(line.rstrip() for line in content.split("\n")) + "\n"


def parse_target_path(task_text: str) -> Optional[Path]:
    """Find target file path in task description."""
    patterns = [
        r"[Cc]reate(?:\s+a\s+file\s+at)?:\s*([\w./\\-]+\.md)",
        r"[Ff]ile\s*:\s*([\w./\\-]+\.md)",
        r"[Pp]ath\s*:\s*([\w./\\-]+\.md)",
        r"([\w./\\-]+/[\w./\\-]+\.md)",
    ]
    for pat in patterns:
        m = re.search(pat, task_text)
        if m:
            return Path(m.group(1).replace("\\", "/"))
    return None


def log_for_finetune(nuc_id: str, system: str, user_prompt: str,
                     completion: str, model_used: str) -> None:
    """Append JSONL row consumable by QLoRA. One file per nucleus."""
    ft_dir = ROOT / ".cex" / "runtime" / "ft_data"
    ft_dir.mkdir(parents=True, exist_ok=True)
    out = ft_dir / f"{nuc_id.lower()}.jsonl"
    row = {
        "nucleus": nuc_id,
        "ts": int(time.time()),
        "model": model_used,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": completion},
        ],
    }
    with out.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def run_nucleus(nucleus: str, task_file: Path, base_url: str, api_key: str,
                max_tokens: int, no_log: bool, cli_model: Optional[str] = None) -> int:
    nuc_id = nucleus.upper()
    role, domain = NUCLEUS_ROLES.get(nuc_id, (nuc_id, "generic"))
    system = SYS_TEMPLATE.format(nuc_id=nuc_id, role=role, domain=domain)
    model, model_source = resolve_model(nuc_id, cli_model)

    if not task_file.exists():
        print(f"[FAIL] Task file not found: {task_file}")
        return 1
    task_text = task_file.read_text(encoding="utf-8", errors="replace")
    if not task_text.strip():
        print(f"[FAIL] Task file is empty: {task_file}")
        return 1

    print(f"[{nuc_id}] Model alias: {model} (proxy decides backend)")
    if model_source != "default":
        print(f"[{nuc_id}] Model override active ({model_source})")
    print(f"[{nuc_id}] Domain: {domain}")
    print(f"[{nuc_id}] Task file: {task_file} ({len(task_text)}B)")
    print(f"[{nuc_id}] Calling LiteLLM @ {base_url}...")

    try:
        data = call_litellm(model, system, task_text, base_url, api_key, max_tokens)
    except requests.exceptions.HTTPError as e:
        print(f"[FAIL] LiteLLM HTTP {e.response.status_code}: {e.response.text[:300]}")
        return 2
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] LiteLLM connection error: {e}")
        return 2

    choices = data.get("choices") or []
    if not choices:
        print(f"[FAIL] No choices in response: {json.dumps(data)[:300]}")
        return 3
    content = (choices[0].get("message") or {}).get("content", "") or ""
    usage = data.get("usage") or {}
    model_used = data.get("model", model)
    wall = data.get("_wall_s", 0)
    print(f"[{nuc_id}] backend={model_used} prompt={usage.get('prompt_tokens', '?')}T "
          f"completion={usage.get('completion_tokens', '?')}T wall={wall}s")

    if not content.strip():
        print("[FAIL] Empty response content")
        return 3

    # Determine target path
    target = parse_target_path(task_text)
    if target is None:
        print(f"[WARN] No target path parsed. Writing to .cex/runtime/out/{nuc_id.lower()}_output.md")
        target = Path(".cex/runtime/out") / f"{nuc_id.lower()}_output.md"
    if not target.is_absolute():
        target = ROOT / target
    target.parent.mkdir(parents=True, exist_ok=True)

    cleaned = clean_frontmatter(content)
    target.write_text(cleaned, encoding="utf-8")
    print(f"[{nuc_id}] Wrote {len(cleaned)}B -> {target.relative_to(ROOT)}")

    # FT logging (cheap, append-only). Skip if --no-log or task is trivial smoke.
    if not no_log:
        try:
            log_for_finetune(nuc_id, system, task_text, content, model_used)
            print(f"[{nuc_id}] FT row appended -> .cex/runtime/ft_data/{nuc_id.lower()}.jsonl")
        except Exception as e:
            print(f"[{nuc_id}] FT log skipped: {e}")

    # Compile if it looks like a CEX artifact
    if cleaned.lstrip().startswith("---") and target.suffix == ".md":
        try:
            subprocess.run(
                [sys.executable, "_tools/cex_compile.py", str(target.relative_to(ROOT))],
                cwd=ROOT, capture_output=True, text=True, timeout=30,
            )
            print(f"[{nuc_id}] Compiled")
        except Exception as e:
            print(f"[{nuc_id}] Compile skipped: {e}")

    # F7 GOVERN structural gate, then an HONEST signal (R-345): the score is
    # the gate's real check fraction, never a hardcoded constant.
    gate = structural_gate(cleaned)
    checks_str = " ".join(
        f"{name}={'PASS' if ok else 'FAIL'}" for name, ok in gate["checks"].items())
    print(f"[{nuc_id}] Gate ({gate['parser']}): {checks_str} -> score {gate['score']}")
    if gate["passed"]:
        _emit_signal(nuc_id.lower(), "complete", gate["score"],
                     score_kind="structural", gate_checks=gate["checks"],
                     gate_parser=gate["parser"], artifact_path=str(target))
        print(f"[{nuc_id}] DONE")
        return 0
    _emit_signal(nuc_id.lower(), "failed", gate["score"],
                 score_kind="structural", gate_checks=gate["checks"],
                 gate_parser=gate["parser"])
    print(f"[{nuc_id}] GATE FAIL -- output kept at {target} for diagnosis; "
          f"signal status=failed")
    return 5


def main():
    p = argparse.ArgumentParser(description="LiteLLM Nucleus Runner (proxy-routed)")
    p.add_argument("--nucleus", required=True, help="N01..N07")
    p.add_argument("--task-file", default=None, help="Override task file path")
    p.add_argument("--base-url", default=None, help="LiteLLM base URL (default env or http://localhost:4000)")
    p.add_argument("--model", default=None,
                   help="Model alias sent to the proxy. Resolution order (highest wins): "
                        "CEX_MODEL_OVERRIDE env var > --model > cex-{nucleus} default.")
    p.add_argument("--max-tokens", type=int, default=4096)
    p.add_argument("--no-log", action="store_true", help="Skip FT JSONL append")
    args = p.parse_args()

    base_url = args.base_url or os.environ.get("LITELLM_BASE_URL", "http://localhost:4000")
    api_key = load_master_key()
    if not api_key:
        print("[FAIL] LITELLM_MASTER_KEY missing. Set it in .env or shell env.")
        return 4

    nuc_lower = args.nucleus.lower()
    if args.task_file:
        task = Path(args.task_file)
    else:
        env_task = os.environ.get("CEX_TASK_FILE")
        if env_task:
            task = Path(env_task)
        else:
            task = ROOT / ".cex" / "runtime" / "handoffs" / f"{nuc_lower}_task.md"
            if not task.exists():
                task = ROOT / f"{nuc_lower}_task.md"

    return run_nucleus(args.nucleus, task, base_url, api_key, args.max_tokens,
                       args.no_log, cli_model=args.model)


if __name__ == "__main__":
    sys.exit(main())
