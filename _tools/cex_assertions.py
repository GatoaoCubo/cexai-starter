#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CEX Declarative Assertion Engine -- typed checks over YAML specs (R-173).

version: 0.1.0
provenance: clean-room mechanic transplant (concepts only, no source code
  copied) from guardrails-ai/guardrails (Apache-2.0, register_validator ->
  validators_registry dispatch pattern) + promptfoo/promptfoo (license
  reused from prior dossier, ASSERTION_HANDLERS dispatch pattern) +
  confident-ai/deepeval (license reused from prior dossier, assert_test()
  re-execution discipline). Full license gate + mechanic citations:
  N01_intelligence/P01_knowledge/kc_oss_guardrails.md. Lineage record:
  N01_intelligence/P01_knowledge/p01_lin_eval_assertions_r173.md.

Mechanic transplant (clean-room, concepts only -- see
N01_intelligence/P01_knowledge/kc_oss_guardrails.md +
N01_intelligence/P01_knowledge/kc_oss_promptfoo.md):

  - Typed assertion REGISTRY, one handler per assertion `type`, dispatched via
    a single lookup map (guardrails-ai `register_validator` -> `validators_registry`
    pattern; promptfoo `ASSERTION_HANDLERS` pattern -- both cited in the KCs above).
  - Every handler is RE-EXECUTED against the real target, never a trusted status
    string (DeepEval `assert_test()` mechanic, cited in kc_oss_deepeval.md).
  - Verdict JSON always carries a REQUIRED boolean `pass` field at both the
    per-assertion AND the aggregate level -- this is the concrete fix-shape for
    R-173 (cex_score.py's H01-H0N hard-gate parsing is 100% regex/string-parsing
    against quality_gate PROSE, no live re-derivation -- see
    _tools/cex_score.py:324 `_parse_hard_gates`, confirmed by direct Read) and
    the sibling concern in R-174 (cex_council.py's judge-output regex has no
    required `pass` field -- see _tools/cex_judge_schema.py, the companion
    module this engine composes with).

WHAT THIS IS NOT:
  - Not a replacement for cex_score.py / cex_doctor.py / cex_council.py.
    Those load-bearing tools are untouched by this transplant (per working
    discipline: never edit load-bearing tools in a research-cell build).
  - Not constrained decoding / logit-level validation (that is Outlines/
    Guidance's mechanic, out of scope here -- see WHITEPAPER Section 2,
    Instructor/Outlines/Guidance row).
  - Not a live LLM judge call. Assertions here are deterministic, local,
    offline checks over already-materialized text/frontmatter/structure.

CLI:
  python _tools/cex_assertions.py --spec <spec.yaml> --target <artifact.md>
  python _tools/cex_assertions.py --spec <spec.yaml> --target <artifact.md> --json

Registering a new assertion type (extension point, mirrors guardrails-ai's
`register_validator` decorator):

  from cex_assertions import register_assertion

  @register_assertion("my_check")
  def _assert_my_check(spec, context):
      return {"pass": True, "message": "..."}
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

try:
    import yaml
except ImportError:  # degrade-never: spec-from-dict callers still work
    yaml = None


# ================================================================
# REGISTRY (guardrails-ai `register_validator` / promptfoo
# `ASSERTION_HANDLERS` mechanic -- type -> handler lookup map)
# ================================================================

ASSERTION_HANDLERS: Dict[str, Callable[[dict, dict], dict]] = {}


def register_assertion(name: str) -> Callable[[Callable], Callable]:
    """Register a handler for an assertion `type`. One file/function per type;
    adding assertion #N+1 never touches run_assertions() or any existing
    handler -- the registry-dispatch discipline this transplant exists to
    demonstrate (guardrails-ai `register_validator`, kc_oss_guardrails.md M1)."""

    def decorator(fn: Callable[[dict, dict], dict]) -> Callable[[dict, dict], dict]:
        ASSERTION_HANDLERS[name] = fn
        return fn

    return decorator


# ================================================================
# Independent markdown/frontmatter loader.
# Deliberately NOT importing cex_score.py / cex_shared.py -- this tool must
# stay reversible and decoupled from load-bearing parsers per working
# discipline (never edit/depend-tightly-on cex_doctor.py / cex_score.py /
# cex_distill.py from a research-cell build).
# ================================================================

_FM_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)


def load_markdown_context(path: str) -> Dict[str, Any]:
    """Load a .md artifact into an assertion context: {frontmatter, body, raw, path}.

    frontmatter is parsed as a flat `key: value` map (line-anchored, values
    left as raw strings -- this engine's assertions compare strings/regex, it
    does not need full YAML-typed frontmatter values).
    """
    text = Path(path).read_text(encoding="utf-8")
    m = _FM_RE.match(text)
    frontmatter: Dict[str, str] = {}
    body = text
    if m:
        fm_block = m.group(1)
        body = text[m.end():]
        for line in fm_block.splitlines():
            line_m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
            if line_m:
                key = line_m.group(1)
                val = line_m.group(2).strip()
                # only set on first occurrence (top-level scalar keys) --
                # nested block values (lists/dicts) are intentionally left
                # out of this flat map; use `body`/`raw` for structured reads.
                if key not in frontmatter:
                    frontmatter[key] = val
    return {"frontmatter": frontmatter, "body": body, "raw": text, "path": path}


def _get_field(context: dict, field: str) -> Optional[str]:
    """Resolve a dotted field path: 'frontmatter.quality' / 'body' / 'raw'."""
    if field in ("body", "raw", "path"):
        return context.get(field)
    if field.startswith("frontmatter."):
        return context.get("frontmatter", {}).get(field.split(".", 1)[1])
    return context.get("frontmatter", {}).get(field)


# ================================================================
# BUILT-IN ASSERTION TYPES
# ================================================================

@register_assertion("contains")
def _assert_contains(spec: dict, context: dict) -> dict:
    field = spec.get("field", "body")
    value = spec.get("value", "")
    text = _get_field(context, field) or ""
    ok = value in text
    return {"pass": ok, "message": f"'{value}' {'found' if ok else 'NOT found'} in {field}"}


@register_assertion("not_contains")
def _assert_not_contains(spec: dict, context: dict) -> dict:
    field = spec.get("field", "body")
    value = spec.get("value", "")
    text = _get_field(context, field) or ""
    ok = value not in text
    return {"pass": ok, "message": f"'{value}' {'absent (ok)' if ok else 'FOUND (should be absent)'} in {field}"}


@register_assertion("regex")
def _assert_regex(spec: dict, context: dict) -> dict:
    field = spec.get("field", "body")
    pattern = spec.get("pattern", "")
    text = _get_field(context, field) or ""
    flags = re.MULTILINE | (re.IGNORECASE if spec.get("ignore_case") else 0)
    m = re.search(pattern, text, flags)
    ok = m is not None
    return {"pass": ok, "message": f"pattern /{pattern}/ {'matched' if ok else 'did NOT match'} {field}"}


@register_assertion("field_equals")
def _assert_field_equals(spec: dict, context: dict) -> dict:
    field = spec.get("field", "")
    expected = spec.get("value")
    actual = _get_field(context, field)
    ok = actual == expected
    return {"pass": ok, "message": f"{field}={actual!r} expected={expected!r}", "actual": actual}


@register_assertion("field_exists")
def _assert_field_exists(spec: dict, context: dict) -> dict:
    field = spec.get("field", "")
    actual = _get_field(context, field)
    ok = actual is not None and str(actual).strip() != ""
    return {"pass": ok, "message": f"{field} {'present' if ok else 'MISSING or empty'}"}


@register_assertion("threshold")
def _assert_threshold(spec: dict, context: dict) -> dict:
    """Numeric compare: field <op> value. op in {>=, <=, ==, >, <, !=}."""
    field = spec.get("field", "")
    op = spec.get("op", ">=")
    value = spec.get("value")
    raw = _get_field(context, field)
    try:
        actual = float(raw)
        target = float(value)
    except (TypeError, ValueError):
        return {"pass": False, "message": f"non-numeric compare: {field}={raw!r} vs {value!r}"}
    ops = {
        ">=": actual >= target, "<=": actual <= target, "==": actual == target,
        ">": actual > target, "<": actual < target, "!=": actual != target,
    }
    if op not in ops:
        return {"pass": False, "message": f"unknown operator '{op}'"}
    ok = ops[op]
    return {"pass": ok, "message": f"{field}={actual} {op} {target} -> {ok}", "actual": actual}


_HARD_GATE_ROW_RE = re.compile(
    r"^\|\s*(H\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|", re.MULTILINE
)


@register_assertion("hard_gate_table")
def _assert_hard_gate_table(spec: dict, context: dict) -> dict:
    """RE-DERIVES the artifact's own hard-gate table from its body text (does
    not trust any stored/summarized count). Independently re-implements the
    same `| H01 | check | fail_cond |` row shape cex_score.py's
    `_parse_hard_gates()` targets (_tools/cex_score.py:324, confirmed by
    direct Read) -- kept as a SEPARATE re-derivation on purpose: two
    independent parsers agreeing is stronger evidence than one parser's
    self-report (the exact anti-self-certification posture FASE H asks for,
    per kc_oss_deepeval.md / kc_oss_promptfoo.md).

    spec: {type: hard_gate_table, min_gates: int, field: body (default)}
    """
    field = spec.get("field", "body")
    min_gates = int(spec.get("min_gates", 1))
    text = _get_field(context, field) or ""
    rows = _HARD_GATE_ROW_RE.findall(text)
    gate_ids = [r[0] for r in rows]
    unique_ids = set(gate_ids)
    duplicates = [g for g in unique_ids if gate_ids.count(g) > 1]
    ok = len(rows) >= min_gates and not duplicates
    message = (
        f"found {len(rows)} hard-gate rows ({sorted(unique_ids)}), "
        f"min_gates={min_gates}, duplicates={duplicates or 'none'}"
    )
    return {"pass": ok, "message": message, "gate_count": len(rows), "gate_ids": sorted(unique_ids)}


@register_assertion("json_schema")
def _assert_json_schema(spec: dict, context: dict) -> dict:
    """Validate a JSON-decodable field/value against an inline JSON Schema.
    Used by cex_judge_schema.py to validate judge verdict payloads against
    the REAL Verdict Schema embedded in N05_operations/P07_evals/p07_jc_*.md
    (confirmed by direct Read: p07_jc_bleed.md, p07_jc_grounding.md -- both
    ship the identical {judge, verdict, blockers, warnings, evidence} block).
    """
    schema = spec.get("schema")
    instance = spec.get("instance")
    if schema is None or instance is None:
        return {"pass": False, "message": "json_schema assertion requires 'schema' and 'instance'"}
    try:
        import jsonschema  # already a transitive dep in this venv (guardrails/etc use it)
    except ImportError:
        return {"pass": False, "message": "jsonschema package not available (degrade-never: cannot validate)"}
    try:
        jsonschema.validate(instance=instance, schema=schema)
        return {"pass": True, "message": "instance conforms to schema"}
    except jsonschema.ValidationError as e:
        return {"pass": False, "message": f"schema validation FAILED: {e.message}"}


# ================================================================
# RUNNER
# ================================================================

def run_assertions(spec_list: List[dict], context: dict) -> dict:
    """Execute every assertion spec against `context`. Returns a JSON-shaped
    verdict with a REQUIRED `pass` boolean at both the per-item and aggregate
    level (the R-173/R-174 fix-shape this whole module demonstrates)."""
    results = []
    for i, spec in enumerate(spec_list):
        assertion_id = spec.get("id", f"a{i}")
        atype = spec.get("type")
        handler = ASSERTION_HANDLERS.get(atype)
        if handler is None:
            results.append({
                "id": assertion_id, "type": atype, "pass": False,
                "message": f"unknown assertion type '{atype}' (known: {sorted(ASSERTION_HANDLERS)})",
                "required": spec.get("required", True),
            })
            continue
        try:
            r = handler(spec, context)
        except Exception as e:  # a raising handler is a FAIL, never a silent skip
            r = {"pass": False, "message": f"assertion raised {type(e).__name__}: {e}"}
        r.setdefault("pass", False)
        r["id"] = assertion_id
        r["type"] = atype
        r["required"] = spec.get("required", True)
        results.append(r)

    required_results = [r for r in results if r.get("required", True)]
    overall_pass = all(r["pass"] for r in required_results) if required_results else True
    passed = sum(1 for r in results if r["pass"])
    return {
        "pass": overall_pass,
        "ok": overall_pass,  # alias -- some callers (cex_distill.py verify_repo
                              # shape) read `ok`, others read `pass`; both are
                              # the SAME required boolean, never string prose.
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "results": results,
    }


def run_assertions_from_files(spec_path: str, target_path: str) -> dict:
    """CLI entry: load a YAML assertion spec + a target markdown artifact,
    run, return the verdict dict."""
    if yaml is None:
        raise RuntimeError("pyyaml is required for --spec (pip install pyyaml)")
    spec_doc = yaml.safe_load(Path(spec_path).read_text(encoding="utf-8"))
    assertions = spec_doc.get("assertions", spec_doc if isinstance(spec_doc, list) else [])
    context = load_markdown_context(target_path)
    return run_assertions(assertions, context)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="CEX declarative assertion engine (R-173)")
    parser.add_argument("--spec", required=True, help="YAML assertion spec path")
    parser.add_argument("--target", required=True, help="target markdown artifact path")
    parser.add_argument("--json", action="store_true", help="print raw JSON verdict")
    args = parser.parse_args(argv)

    verdict = run_assertions_from_files(args.spec, args.target)

    if args.json:
        print(json.dumps(verdict, indent=2))
    else:
        status = "PASS" if verdict["pass"] else "FAIL"
        print(f"[{status}] {args.target} -- {verdict['passed']}/{verdict['total']} assertions passed")
        for r in verdict["results"]:
            mark = "OK" if r["pass"] else "FAIL"
            print(f"  [{mark}] {r['id']} ({r['type']}): {r.get('message', '')}")

    return 0 if verdict["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
