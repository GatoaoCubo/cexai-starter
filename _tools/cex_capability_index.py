"""cex_capability_index.py -- build the capability_registry for composable crews.

Scans the full CEX agent pool (3 sources) and emits a single registry JSON
that any nucleus can query to assemble a crew:

  1. .claude/P02_model/*.md            Claude Code-spawnable sub-agents (builders)
  2. N0{1..7}_*/P02_model/*.md         Nucleus domain agents (non-builder)
  3. N0{1..7}_*/agent_card_*.md     Nucleus-level agent cards (A2A)

Output: .cex/P09_config/capability_registry.json

Fields per entry:
  - id: canonical ID
  - name: display name
  - source: "builder_subagent" | "domain_agent" | "nucleus_card"
  - path: relative path from repo root
  - nucleus: owning nucleus (n01..n07) or null
  - kind: artifact kind (for builders: the kind they build)
  - domain: capability domain
  - capabilities: list[str] (from frontmatter or body)
  - tools_allowed: list[str]
  - model_tier: "opus" | "sonnet" | "haiku" | "local" | null
  - description: one-liner

Usage:
  python _tools/cex_capability_index.py            # build + write
  python _tools/cex_capability_index.py --dry-run  # print counts
  python _tools/cex_capability_index.py --query kw # filter by keyword
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / ".cex" / "config" / "capability_registry.json"
# Catalog bridge (T3): graduates emitted by cex_catalog_promote.py land here.
PROMOTION_MANIFEST_PATH = ROOT / ".cex" / "runtime" / "catalog" / "promotion_manifest.json"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def parse_fm(text: str) -> dict:
    """Minimal YAML frontmatter parser (no external dep)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm: dict = {}
    key = None
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - ") and key:
            val = line[4:].strip().strip('"').strip("'")
            fm.setdefault(key, []).append(val) if isinstance(
                fm.get(key), list
            ) else fm.update({key: [val]})
        elif ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            k, v = k.strip(), v.strip()
            key = k
            if not v:
                fm[k] = []
            else:
                fm[k] = v.strip('"').strip("'")
    return fm


def scan_builder_subagents() -> list[dict]:
    """Parse .claude/P02_model/*.md (builder sub-agents)."""
    entries: list[dict] = []
    for p in sorted((ROOT / ".claude" / "agents").glob("*.md")):
        text = p.read_text(encoding="utf-8", errors="replace")
        fm = parse_fm(text)
        name = fm.get("name", p.stem)
        kind = name.replace("-builder", "").replace("-", "_") if name.endswith(
            "-builder"
        ) else None
        tools = fm.get("tools", "")
        tools_list = [t.strip() for t in tools.split(",")] if isinstance(
            tools, str
        ) else tools if isinstance(tools, list) else []
        entries.append({
            "id": p.stem,
            "name": name,
            "source": "builder_subagent",
            "path": str(p.relative_to(ROOT)).replace("\\", "/"),
            "nucleus": None,
            "kind": kind,
            "domain": "artifact-generation",
            "capabilities": [f"builds {kind}"] if kind else [],
            "tools_allowed": tools_list,
            "model_tier": fm.get("model", "sonnet"),
            "description": fm.get("description", ""),
        })
    return entries


def scan_domain_agents() -> list[dict]:
    """Parse N0x_*/P02_model/agent_*.md (nucleus domain agents, non-builder).

    Convention fix (register row R-306): this scan used to glob
    ``N0x_*/agents/agent_*.md`` -- a directory convention ("agents/") that has
    never existed on disk for any nucleus (verified repo-wide 2026-07-08:
    ``ls -d N0*_*/agents`` matches zero directories). Every real agent-kind
    file lives under ``P02_model/`` instead, alongside sibling kinds
    (agent_package, agent_profile, nucleus_def) that also start with
    "agent_" in their filename. The old glob therefore returned [] since
    birth -- domain_agent has been silently 0 in every capability_registry.json
    ever generated (root cause of R-145's phantom-declaration gap going
    unnoticed: nothing was ever there to notice).

    Two exclusions, both evidence-based (confirmed by a repo-wide frontmatter
    grep across all 25 N0*_*/P02_model/agent_*.md files on disk, not guessed):

      1. ``kind != "agent"`` -- P02_model/ also holds ``agent_package``
         (``agent_package_n03.md``, kind=agent_package) and ``agent_profile``
         (``agent_profile_n04.md``, kind=agent_profile). Same filename
         prefix, different kind -- not a domain agent.

      2. Nucleus-identity mirrors (``agent_n01.md`` .. ``agent_n07.md``, one
         per nucleus, all 7 confirmed present). Frontmatter carries BOTH an
         explicit ``nucleus:`` field AND a ``mirrors:`` key -- they are the
         abstract kind_agent/tpl_agent template mirrored per-nucleus (the
         nucleus BECOMING its own sin-lensed identity, F2_become: tone,
         voice, sin_lens, required_fields overrides), not a specialized
         sub-agent that performs domain work. Structurally they lack the
         title/domain/capabilities/tools fields every genuine domain agent
         carries. No genuine domain agent declares a top-level ``nucleus:``
         of its own (nucleus is always inferred from the directory instead)
         -- confirmed repo-wide: exactly 7 files have both keys, and they are
         exactly the 7 mirrors, 1:1 with n01..n07. Excluding them avoids
         double-counting nucleus identity, which is already represented via
         ``scan_nucleus_defs`` (nucleus_def) and ``scan_nucleus_cards``
         (nucleus_card).

    Degrade-never: a file that cannot be read or whose frontmatter cannot be
    parsed is SKIPPED, not fatal -- the scan continues over the remaining
    files (mirrors the fail-open posture used elsewhere in this module, e.g.
    scan_promoted_catalog).
    """
    entries: list[dict] = []
    for p in sorted(ROOT.glob("N0*_*/P02_model/agent_*.md")):
        nucleus = p.parents[1].name[:3].lower()  # N01_intelligence -> n01
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
            fm = parse_fm(text)
        except Exception:
            continue  # degrade-never: unreadable/unparseable file is skipped, not fatal
        if fm.get("kind") != "agent":
            continue  # sibling kind sharing the "agent_" filename prefix (agent_package, agent_profile, ...)
        if "nucleus" in fm and "mirrors" in fm:
            continue  # nucleus-identity mirror (agent_n0X.md) -- see docstring
        caps = fm.get("capabilities", [])
        if isinstance(caps, str):
            caps = [caps]
        tools = fm.get("tools", [])
        if isinstance(tools, str):
            tools = [t.strip() for t in tools.split(",")]
        entries.append({
            "id": fm.get("id", p.stem),
            "name": fm.get("title", p.stem),
            "source": "domain_agent",
            "path": str(p.relative_to(ROOT)).replace("\\", "/"),
            "nucleus": nucleus,
            "kind": fm.get("kind", "agent"),
            "domain": fm.get("domain", "unknown"),
            "capabilities": caps,
            "tools_allowed": tools,
            "model_tier": fm.get("model_tier", None),
            "description": fm.get("title", ""),
        })
    return entries


def scan_nucleus_cards() -> list[dict]:
    """Parse N0x/agent_card_*.md (nucleus-level agent cards)."""
    entries: list[dict] = []
    seen: set[str] = set()
    for p in sorted(ROOT.glob("N0*_*/agent_card_n*.md")):
        # Prefer canonical agent_card_n0X over architecture duplicates
        key = p.name
        if key in seen:
            continue
        seen.add(key)
        text = p.read_text(encoding="utf-8", errors="replace")
        fm = parse_fm(text)
        nuc_match = re.search(r"agent_card_(n0\d)", p.stem)
        nucleus = nuc_match.group(1) if nuc_match else None
        caps = fm.get("capabilities", [])
        if isinstance(caps, str):
            caps = [caps]
        entries.append({
            "id": fm.get("id", p.stem),
            "name": fm.get("title", p.stem),
            "source": "nucleus_card",
            "path": str(p.relative_to(ROOT)).replace("\\", "/"),
            "nucleus": nucleus,
            "kind": "agent_card",
            "domain": fm.get("domain", nucleus or "unknown"),
            "capabilities": caps,
            "tools_allowed": [],
            "model_tier": fm.get("model_tier", None),
            "description": fm.get("tldr", fm.get("title", "")),
        })
    return entries


def scan_role_assignments() -> list[dict]:
    """Parse N0*/P12_orchestration/p02_ra_*.md (role_assignment bindings for composable crews)."""
    entries: list[dict] = []
    for p in sorted(ROOT.glob("N0*_*/P12_orchestration/p02_ra_*.md")):
        text = p.read_text(encoding="utf-8", errors="replace")
        fm = parse_fm(text)
        nucleus = p.parents[1].name[:3].lower()
        entries.append({
            "id": fm.get("id", p.stem),
            "name": fm.get("title", p.stem),
            "source": "role_assignment",
            "path": str(p.relative_to(ROOT)).replace("\\", "/"),
            "nucleus": nucleus,
            "kind": "role_assignment",
            "domain": fm.get("role_name", "unknown"),
            "capabilities": [fm.get("goal", "")],
            "tools_allowed": fm.get("tools", []) if isinstance(fm.get("tools"), list) else [],
            "agent_id": fm.get("agent_id", ""),
            "description": fm.get("goal", fm.get("title", "")),
        })
    return entries


def scan_crew_templates() -> list[dict]:
    """Parse N0*/P12_orchestration/p12_ct_*.md (crew_template recipes)."""
    entries: list[dict] = []
    for p in sorted(ROOT.glob("N0*_*/P12_orchestration/p12_ct_*.md")):
        text = p.read_text(encoding="utf-8", errors="replace")
        fm = parse_fm(text)
        nucleus = p.parents[1].name[:3].lower()
        entries.append({
            "id": fm.get("id", p.stem),
            "name": fm.get("title", p.stem),
            "source": "crew_template",
            "path": str(p.relative_to(ROOT)).replace("\\", "/"),
            "nucleus": nucleus,
            "kind": "crew_template",
            "domain": fm.get("crew_name", p.stem),
            "capabilities": [fm.get("purpose", "")],
            "tools_allowed": [],
            "process": fm.get("process", "sequential"),
            "description": fm.get("purpose", fm.get("tldr", "")),
        })
    return entries


def scan_nucleus_defs() -> list[dict]:
    """Parse nucleus_def_*.md (machine-readable nucleus identities). Checks
    P08_architecture first (legacy genesis location, still real for nuclei not yet
    migrated), then falls back to P02_model per nucleus (the documented canonical
    home -- .claude/rules/new-nucleus-bootstrap.md's 9-asset table + the
    cex_new_nucleus.py scaffolder both write new nucleus_def_*.md to P02_model).
    The identity-dedup fix for register rows R-023/R-026/R-027/R-029 (2026-07-05)
    removed the P08_architecture copy for n00/n01/n02/n04/n05 (merged into their
    P02_model copy) -- this fallback keeps them from silently dropping out of the
    registry. Nuclei whose P08_architecture copy still exists (unchanged by that
    fix) resolve exactly as before -- zero behavior change for them."""
    entries: list[dict] = []
    seen_nuclei: set[str] = set()
    paths = sorted(ROOT.glob("N0*_*/P08_architecture/nucleus_def_*.md"))
    for p in paths:
        nuc = p.stem.split("_")[-1].lower()  # nucleus_def_n05 -> n05
        seen_nuclei.add(nuc)
    for p in sorted(ROOT.glob("N0*_*/P02_model/nucleus_def_*.md")):
        nuc = p.stem.split("_")[-1].lower()
        if nuc not in seen_nuclei:
            paths.append(p)
            seen_nuclei.add(nuc)
    paths.sort()
    for p in paths:
        text = p.read_text(encoding="utf-8", errors="replace")
        fm = parse_fm(text)
        nucleus_id = fm.get("nucleus_id", "").lower() or p.stem[-3:].lower()
        entries.append({
            "id": fm.get("id", p.stem),
            "name": fm.get("title", p.stem),
            "source": "nucleus_de",
            "path": str(p.relative_to(ROOT)).replace("\\", "/"),
            "nucleus": nucleus_id,
            "kind": "nucleus_de",
            "domain": fm.get("role", "unknown"),
            "capabilities": fm.get("crew_templates_exposed", []),
            "tools_allowed": [],
            "model_tier": fm.get("model_tier"),
            "sin_lens": fm.get("sin_lens", ""),
            "description": fm.get("tldr", fm.get("title", "")),
        })
    return entries


def scan_promoted_catalog(manifest_path: Path = PROMOTION_MANIFEST_PATH) -> list[dict]:
    """Read the promotion_manifest graduates -> additive registry entries.

    Each graduate flips ``nucleus`` away from ``catalog_only`` to its resolved
    owner and carries ``provenance`` + ``attribution`` (the catalog-bridge audit
    trail). Returns [] when the manifest is absent / malformed / has no graduates
    -- which is what keeps the baseline registry byte-stable (zero-regression).
    The contract is pinned by cex_catalog_promote.run_promotion.
    """
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    graduates = manifest.get("graduate") if isinstance(manifest, dict) else None
    if not isinstance(graduates, list):
        return []
    entries: list[dict] = []
    for g in graduates:
        if not isinstance(g, dict) or not g.get("id"):
            continue
        gid = str(g["id"])
        name = gid.rsplit("_", 1)[-1] if "_" in gid else gid
        stack = str(g.get("stack", ""))
        src_path = str(g.get("source_path", ""))
        entries.append({
            "id": gid,
            "name": name,
            "source": "aitmpl_catalog",
            "path": src_path,
            "nucleus": str(g.get("nucleus", "")) or None,
            "kind": str(g.get("kind", "")),
            "domain": str(g.get("domain", "")),
            "capabilities": [],
            "tools_allowed": [],
            "model_tier": None,
            "description": ("catalog-promoted %s from %s" % (g.get("kind", "item"), stack)).strip(),
            "provenance": {
                "stack": stack,
                "source_repo": str(g.get("source_repo", "")),
                "source_path": src_path,
            },
            "attribution": str(g.get("attribution", "")),
        })
    return entries


def build_registry(promoted: list[dict] | None = None) -> dict:
    builders = scan_builder_subagents()
    domains = scan_domain_agents()
    cards = scan_nucleus_cards()
    roles = scan_role_assignments()
    crews = scan_crew_templates()
    defs_ = scan_nucleus_defs()
    all_entries = builders + domains + cards + roles + crews + defs_
    # ADDITIVE + zero-regression: promoted entries (if any) append LAST so every
    # baseline entry keeps its position, and the promoted_catalog count key is
    # only present when there ARE promoted entries -> no-manifest output is
    # byte-identical to the pre-bridge registry. Pass an explicit list to include.
    promoted = list(promoted) if promoted else []
    if promoted:
        all_entries = all_entries + promoted
    # Indexes for fast lookup
    by_kind: dict[str, list[str]] = {}
    by_nucleus: dict[str, list[str]] = {}
    by_domain: dict[str, list[str]] = {}
    for e in all_entries:
        if e.get("kind"):
            by_kind.setdefault(e["kind"], []).append(e["id"])
        if e.get("nucleus"):
            by_nucleus.setdefault(e["nucleus"], []).append(e["id"])
        if e.get("domain"):
            by_domain.setdefault(e["domain"], []).append(e["id"])
    counts = {
        "total": len(all_entries),
        "builder_subagent": len(builders),
        "domain_agent": len(domains),
        "nucleus_card": len(cards),
        "role_assignment": len(roles),
        "crew_template": len(crews),
        "nucleus_def": len(defs_),
    }
    if promoted:
        counts["promoted_catalog"] = len(promoted)
    return {
        "version": "1.0",
        "generated": "cex_capability_index.py",
        "counts": counts,
        "indexes": {
            "by_kind": by_kind,
            "by_nucleus": by_nucleus,
            "by_domain": by_domain,
        },
        "agents": all_entries,
    }


# --------------------------------------------------------------------------- #
# Catalog bridge (T3): P3-HITL-gated promoted registry write
# --------------------------------------------------------------------------- #

APPROVALS_DIR = ROOT / ".cexai" / "approvals"
_GATE_OPERATION = "catalog:capability_registry:promoted_write"


def _resolve_watch(data: dict) -> str:
    """approved | denied | pending from a watch file's verdicts (a deny vetoes)."""
    verdicts = data.get("verdicts", []) or []
    if any(v.get("verdict") == "deny" for v in verdicts):
        return "denied"
    approvers = {v.get("approver") for v in verdicts if v.get("verdict") == "approve"}
    required = int((data.get("policy", {}) or {}).get("approvers_required", 1) or 1)
    return "approved" if len(approvers) >= required else "pending"


def _find_approved(approvals_dir: Path, operation: str) -> str | None:
    """request_id of an already-approved request for ``operation`` (idempotent reuse)."""
    try:
        files = sorted(approvals_dir.glob("*.json"))
    except Exception:
        return None
    for fpath in files:
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
        except Exception:
            continue
        if data.get("operation") != operation:
            continue
        if _resolve_watch(data) == "approved":
            return data.get("request_id") or fpath.stem
    return None


def _gate_promoted_write(auto_approve: bool, dry_run: bool,
                         approvals_dir: Path | None = None) -> dict:
    """P3 HITL gate for the irreversible promoted-registry write.

    Reuses cexai.governance.hitl.FileApprovalGate (the ACR P3 mechanism). Returns
    {"allowed": bool, "gate": ...}. auto_approve=True dogfoods P3 by auto-recording
    an approve (NON-BLOCKING -- await_decision is never called). auto_approve=False
    emits a pending request and DEFERS (allowed=False). cexai absent / any error ->
    fail-closed (allowed=False). Idempotent: an existing approved request is reused.
    ``approvals_dir`` resolves to the module APPROVALS_DIR at CALL time (None) so a
    test can redirect it via monkeypatch.
    """
    operation = _GATE_OPERATION
    try:
        from cexai.governance.hitl import FileApprovalGate, record_verdict
    except Exception as exc:
        return {"allowed": False, "gate": "unavailable", "operation": operation,
                "reason": "cexai HITL absent; promoted write skipped (fail-closed): %s" % exc}
    if dry_run:
        return {"allowed": False, "gate": "would-request", "operation": operation,
                "reason": "dry-run: would emit a HITL approval request (no write)"}
    try:
        adir = Path(approvals_dir) if approvals_dir is not None else APPROVALS_DIR
        existing = _find_approved(adir, operation)
        if existing:
            return {"allowed": True, "gate": "approved", "operation": operation,
                    "request_id": existing, "reason": "reused prior approval (idempotent)"}
        gate = FileApprovalGate(approvals_dir=adir)
        req = gate.request(operation, "catalog_promote")
        if auto_approve:
            record_verdict(adir, req.request_id, approver="catalog_auto_approve", verdict="approve")
            return {"allowed": True, "gate": "approved", "operation": operation,
                    "request_id": req.request_id,
                    "reason": "policy.auto_approve -> auto-recorded approve (P3 dogfood, non-blocking)"}
        return {"allowed": False, "gate": "pending", "operation": operation,
                "request_id": req.request_id,
                "reason": "emit-and-defer: human approval required; promoted write deferred"}
    except Exception as exc:
        return {"allowed": False, "gate": "unavailable", "operation": operation,
                "reason": "HITL gate error; promoted write skipped (fail-closed): %s" % exc}


def _serialize(reg: dict) -> str:
    """Canonical registry serialization (matches main()'s write -> byte-stable)."""
    return json.dumps(reg, ensure_ascii=True, indent=2)


def write_registry_with_promotion(policy: dict | None = None, *, dry_run: bool = False,
                                   manifest_path: Path = PROMOTION_MANIFEST_PATH) -> dict:
    """Gated write entry point used by cex_catalog_promote --apply.

    ALWAYS regenerates the baseline registry. Promoted graduates are appended ONLY
    when the P3 gate approves (driven by policy.auto_approve) -- otherwise the
    baseline is written alone (deferred), so zero-regression holds even when the
    gate blocks. Returns a report dict (no exception escapes the happy path)."""
    policy = policy or {}
    auto_approve = bool(policy.get("auto_approve", True))
    promoted = scan_promoted_catalog(manifest_path)
    report = {"gate": "noop", "allowed": False, "promoted_available": len(promoted)}

    if not promoted:
        reg = build_registry(promoted=[])
        report.update({"gate": "noop", "allowed": True,
                       "reason": "no graduates; baseline regenerated"})
    else:
        gate = _gate_promoted_write(auto_approve, dry_run)
        report.update(gate)
        reg = build_registry(promoted=promoted if gate.get("allowed") else [])

    report["total"] = reg["counts"]["total"]
    report["promoted_written"] = reg["counts"].get("promoted_catalog", 0)
    if not dry_run:
        REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        REGISTRY_PATH.write_text(_serialize(reg), encoding="utf-8")
    return report


def query(reg: dict, keyword: str) -> list[dict]:
    kw = keyword.lower()
    matches = []
    for a in reg["agents"]:
        hay = " ".join([
            a.get("id", ""),
            a.get("name", ""),
            a.get("domain", ""),
            str(a.get("capabilities", "")),
            a.get("description", ""),
        ]).lower()
        if kw in hay:
            matches.append(a)
    return matches


def _warn_promoted_dropped(promoted: list[dict], reason: str = "") -> None:
    """Loud, unmissable banner (register row R-303): graduates exist but this
    bare regen has no sanctioned reason to include them, so baseline-only was
    written. Names exactly which entries were dropped and the command that
    sanctions them -- the whole point is that a routine
    ``python _tools/cex_capability_index.py`` run can never SILENTLY regress an
    already human-approved promoted registry back down to baseline (it did,
    twice, before this fix)."""
    bar = "!" * 78
    print(bar)
    print(f"[WARN] R-303: {len(promoted)} promoted catalog entrie(s) DROPPED "
          f"from this bare regen -- baseline-only was written:")
    for e in promoted[:10]:
        print(f"[WARN]   - {e.get('id', '?')}")
    if len(promoted) > 10:
        print(f"[WARN]   ... and {len(promoted) - 10} more")
    if reason:
        print(f"[WARN] gate: {reason}")
    print("[WARN] To sanction + persist these graduates, run:")
    print("[WARN]     python _tools/cex_catalog_promote.py --apply")
    print(bar)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Print counts, no write")
    ap.add_argument("--query", help="Filter by keyword across all fields")
    args = ap.parse_args()

    if args.query:
        # Query reads the FULL registry (baseline + promoted graduates) so a
        # promoted catalog id surfaces with its provenance. Read-only -> no gate.
        reg = build_registry(promoted=scan_promoted_catalog())
        matches = query(reg, args.query)
        print(f"[QUERY '{args.query}'] {len(matches)} match(es):")
        for m in matches[:20]:
            prov = m.get("provenance", {})
            extra = f" src={prov.get('stack')}" if prov else ""
            print(f"  [{m['source']}] {m['id']:40s} nucleus={m['nucleus'] or '-':4s} tier={m.get('model_tier') or '-'}{extra}")
        return 0

    # Write path (R-303 fix): the baseline registry always regenerates. Promoted
    # catalog graduates are folded in ONLY when an EXISTING P3 approval already
    # sanctions this exact merge -- reused idempotently via the same lookup
    # write_registry_with_promotion's own gate uses (_find_approved). A bare run
    # NEVER mints a new approval itself (that would bypass P3 HITL): with
    # graduates awaiting approval, this stays baseline-only -- loudly disclosed,
    # never silent. No graduates at all -> byte-identical to the pre-fix path.
    promoted = scan_promoted_catalog(PROMOTION_MANIFEST_PATH)
    delegated_report: dict | None = None

    if not promoted:
        reg = build_registry()
    else:
        reused = _find_approved(APPROVALS_DIR, _GATE_OPERATION)
        if not reused:
            _warn_promoted_dropped(
                promoted, "no existing approval for %s" % _GATE_OPERATION)
            reg = build_registry()
        elif args.dry_run:
            # Preview only: show what a real run would reuse. No write, and no
            # call into write_registry_with_promotion -- its dry_run branch is
            # write-focused (always reports "would-request"), not a preview.
            reg = build_registry(promoted=promoted)
        else:
            # ONE write path: delegate to write_registry_with_promotion, which
            # independently re-derives the SAME idempotent reuse via
            # _gate_promoted_write -> _find_approved. auto_approve=False means
            # this bare path can only ever REUSE a prior approval, never mint one.
            delegated_report = write_registry_with_promotion(
                policy={"auto_approve": False}, dry_run=False,
                manifest_path=PROMOTION_MANIFEST_PATH)
            reg = build_registry(
                promoted=promoted if delegated_report.get("allowed") else [])
            if not delegated_report.get("allowed"):
                _warn_promoted_dropped(promoted, delegated_report.get("reason", ""))

    print(f"[INDEX] total={reg['counts']['total']} "
          f"builders={reg['counts']['builder_subagent']} "
          f"domains={reg['counts']['domain_agent']} "
          f"cards={reg['counts']['nucleus_card']} "
          f"roles={reg['counts'].get('role_assignment', 0)} "
          f"crews={reg['counts'].get('crew_template', 0)} "
          f"defs={reg['counts'].get('nucleus_def', 0)}")
    if "promoted_catalog" in reg["counts"]:
        print(f"[INDEX] promoted_catalog={reg['counts']['promoted_catalog']} "
              f"(reused existing P3 approval -- {_GATE_OPERATION})")
    print(f"[INDEX] kinds indexed: {len(reg['indexes']['by_kind'])}")
    print(f"[INDEX] nuclei indexed: {len(reg['indexes']['by_nucleus'])}")

    if args.dry_run:
        return 0

    if delegated_report is None:
        REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        REGISTRY_PATH.write_text(
            json.dumps(reg, ensure_ascii=True, indent=2), encoding="utf-8"
        )
    print(f"[OK] wrote {REGISTRY_PATH.relative_to(ROOT)} ({REGISTRY_PATH.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
