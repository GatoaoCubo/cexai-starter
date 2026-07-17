#!/usr/bin/env python3
"""cex_brain_assembler.py -- Stage 3 ASSEMBLE (INIT_ASSIMILATION_ENGINE, Gap#3, N03).

Map a user's PURPOSE (N06 Wave A) + DISTILLED KNOWLEDGE (N04 Wave A) + a VERTICAL
PALETTE (N06 registry) into a portable, 12-pillar vertical business brain emitted as
an `agent_package` ISO file set (the v2.0 12-pillar fractal: 00_instructions + P01..P12).

THE NET-NEW (the gap this tool closes):
  neither the agent_package builder (packages a KNOWN agent's existing files) nor
  blueprints.freeze (freezes KNOWN stack templates) auto-DERIVES the package file set
  FROM distilled knowledge + purpose. `derive_palette()` is that mapping -- it turns
  (vertical kind/nucleus palette) + (distilled KC feeds_kinds + keywords) into the
  tailored kind set that seeds each of the 12 pillars.

Consumes (matched to the REAL Wave A contracts, not just the spec):
  - N06: cex_vertical_detect.detect() -> {vertical, kind_palette, nucleus_palette,
         monetization_default, status, confidence}  (registry: vertical_templates.yaml)
  - N06: user_model_assimilation_purpose instance (purpose/vertical/source/depth collections)
  - N04: a distill OUT dir = _brain_manifest.json (ledger) + knowledge_card/ + entity_memory/
         + knowledge_index/ (+ knowledge_graph/ under deep), from cex_distill_orchestrator.py

Produces:
  <out>/<brain>/
    manifest.yaml         agent_package identity card (v2.0)
    00_instructions.md    compact <= 8000 chars, 6-section anatomy
    P01_knowledge/ .. P12_orchestration/   the 12-pillar fractal (one+ file each)

Then:
  - brain_freeze(): resolve {{BRAND_*}} open_vars against brand_config (REUSE the
    blueprints.freeze resolution + provenance mechanic); degrade to WHITELABEL offline.
  - verify_12_pillar(): REUSE cex_repo_align.scan_nucleus() to assert 12/12 pillars.

Design contract (founder D4/D5/D6): LIGHT brain by default (core spine + top vertical
kinds); DEEP adds the full palette + knowledge_graph. derive-from-purpose when the
vertical has no backing kind. Brain is LAB-ONLY (the user owns it). Offline, no API key.

A run is DRY by default (plan only). Pass --execute to write the brain.

Usage:
  # purpose -> auto-detect vertical -> assemble (dry plan)
  python _tools/cex_brain_assembler.py --purpose "custom software shop shipping MVPs" --out OUT

  # consume an N04 distill OUT dir + write
  python _tools/cex_brain_assembler.py --purpose "..." --distilled DISTILL_OUT --out OUT --execute

  # deep brain, explicit vertical, freeze against a brand_config
  python _tools/cex_brain_assembler.py --purpose "..." --vertical fintech --depth deep \
      --brand-config .cex/brand/brand_config.yaml --out OUT --execute

  python _tools/cex_brain_assembler.py --self-test
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, OrderedDict
from datetime import date, datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

# --- sibling _tools reuse (hard deps; these ship with the repo) -------------
import cex_vertical_detect as VD          # detect() + load_registry()  (N06 palette)
import cex_repo_align as ALIGN            # scan_nucleus() + SEMANTIC_TO_PILLAR (12-pillar verify)
from cex_shared import ensure_dir, parse_frontmatter, slugify  # noqa: E402

KINDS_META_PATH = ROOT / ".cex" / "kinds_meta.json"
DEFAULT_BRAND_CONFIG = ROOT / ".cex" / "brand" / "brand_config.yaml"
FROZEN_BY = "cex-brain-assembler"

# Canonical 12-pillar order, taken from the SAME source cex_repo_align verifies against,
# so a freshly assembled brain reports 12/12 by construction.
PILLAR_DIRS = sorted(ALIGN.SEMANTIC_TO_PILLAR.values())  # ["P01_knowledge", ... "P12_orchestration"]
PILLAR_BY_NUM = {p.split("_", 1)[0]: p for p in PILLAR_DIRS}  # {"P01": "P01_knowledge", ...}

# The 7 agent_package input kinds (kc_agent_package v2.0). Always seeded: the SPINE of
# any brain regardless of vertical. (kind, canonical pillar number).
SPINE = [
    ("knowledge_card", "P01"),
    ("agent", "P02"),
    ("system_prompt", "P03"),
    ("instruction", "P03"),
    ("guardrail", "P11"),
    ("boot_config", "P12"),
    ("fallback_chain", "P12"),
]

# Heuristic keyword -> kind map for the derive_from_purpose path (when the detected
# vertical has no backing kind palette). Intentionally small + high-precision.
KEYWORD_TO_KIND = {
    "pricing": "pricing_page", "price": "content_monetization", "monetize": "content_monetization",
    "subscription": "subscription_tier", "compliance": "compliance_framework",
    "regulatory": "compliance_framework", "audit": "audit_log", "contract": "compliance_framework",
    "course": "course_module", "curriculum": "curriculum_config", "segment": "customer_segment",
    "funnel": "user_journey", "onboarding": "onboarding_flow", "campaign": "competitive_matrix",
    "api": "api_reference", "sdk": "sdk_example", "repo": "repo_map", "deploy": "deployment_manifest",
    "workflow": "workflow", "pipeline": "pipeline_template", "alert": "alert_rule",
    "case study": "case_study", "roi": "roi_calculator", "pitch": "pitch_deck",
}

# When derive_from_purpose yields nothing concrete, fall back to this sane core set.
DEFAULT_DERIVED = ["knowledge_card", "workflow", "user_journey", "content_monetization", "guardrail"]

# DEEP adds these governance/graph kinds on top of the vertical palette.
DEEP_EXTRAS = ["knowledge_graph", "audit_log", "quality_gate"]

# {{BRAND_*}} token -> brand_config dotted key (mirrors brand_config_template.yaml).
BRAND_KEY_MAP = {
    "BRAND_NAME": "identity.BRAND_NAME",
    "BRAND_TAGLINE": "identity.BRAND_TAGLINE",
    "BRAND_MISSION": "identity.BRAND_MISSION",
    "BRAND_VISION": "identity.BRAND_VISION",
    "BRAND_VOICE_TONE": "voice.BRAND_VOICE_TONE",
    "BRAND_LANGUAGE": "voice.BRAND_LANGUAGE",
    "BRAND_ICP": "audience.BRAND_ICP",
    "BRAND_CATEGORY": "positioning.BRAND_CATEGORY",
}

# Per-pillar role line (from the kc_agent_package 12-pillar fractal table).
PILLAR_ROLE = {
    "P01": "Domain facts, rules, taxonomies (the distilled knowledge)",
    "P02": "Identity: persona, role, voice, expertise",
    "P03": "Generation recipes / system prompt / templates",
    "P04": "Capabilities + WHEN + manual substitute",
    "P05": "Output contracts: format + example",
    "P06": "I/O schema: inputs, validation",
    "P07": "Quality gates: rubric, self-check",
    "P08": "Pipeline: stages, decision logic, assembly provenance",
    "P09": "Parameters, limits, defaults, monetization",
    "P10": "Context, memory, handoffs, the navigable brain index",
    "P11": "Guardrails, anti-hallucination, NEVER-do (the 3 universal rules)",
    "P12": "The executable operating loop",
}

_BRAND_TOKEN_RE = re.compile(r"\{\{(BRAND_[A-Z0-9_]+)\}\}")


def _id_slug(text):
    """Underscore-only slug for agent_package ids (regex ^[a-z][a-z0-9_]+$). slugify()
    emits hyphens, which the ID gate rejects -- fold them to underscores."""
    s = slugify(text).replace("-", "_")
    s = re.sub(r"_+", "_", s).strip("_")
    if s and s[0].isdigit():
        s = "v_" + s
    return s or "vertical"


# ===========================================================================
# guarded cexai reuse -- freeze resolution + F7 GOVERN gates (degrade-never)
# ===========================================================================

def _load_freeze_api():
    """Return (load_config, lookup_dotted, now_iso, protocol_version) from the cexai
    blueprints.freeze module, or local fallbacks when cexai is absent. This is the
    REUSE of the blueprints.freeze primitive's resolution + provenance mechanic."""
    try:
        from cexai.distribution.blueprints.freeze import (  # type: ignore
            PROTOCOL_VERSION, _lookup_dotted, _now_iso, load_config)
        return load_config, _lookup_dotted, _now_iso, str(PROTOCOL_VERSION), "cexai.blueprints.freeze"
    except Exception:  # pragma: no cover - exercised only when cexai is absent
        def _local_load(path):
            import yaml  # lazy
            data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}

        def _local_lookup(cfg, dotted):
            node = cfg
            for part in dotted.split("."):
                if not isinstance(node, dict) or part not in node:
                    return False, None
                node = node[part]
            return (False, None) if node is None else (True, node)

        def _local_now():
            return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

        return _local_load, _local_lookup, _local_now, "local", "local-fallback"


def f7_gates(frontmatter, body):
    """Call the cexai F7 GOVERN gates (citation + reasoning_trace). Each is pure,
    offline, never raises. Returns a list of {gate, applies, fails, reason}. An
    `applies and fails` result is a HARD F7 fail for the caller to surface."""
    results = []
    for name, importer in (
        ("citation", "cexai.tools.research.citation_gate"),
        ("reasoning_trace", "cexai.distribution.skills.reasoning_gate"),
    ):
        try:
            mod = __import__(importer, fromlist=["evaluate"])
            r = mod.evaluate(frontmatter, body)
            results.append({"gate": name, "applies": bool(getattr(r, "applies", False)),
                            "fails": bool(getattr(r, "fails", False)),
                            "reason": str(getattr(r, "reason", ""))})
        except Exception as exc:  # degrade-never
            results.append({"gate": name, "applies": False, "fails": False,
                            "reason": "gate unavailable: %s" % exc})
    return results


# ===========================================================================
# inputs -- purpose (N06) + distilled knowledge (N04)
# ===========================================================================

def load_kinds_meta():
    try:
        data = json.loads(KINDS_META_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data.get("kinds", data) if isinstance(data, dict) else {}


def pillar_for_kind(kind, kinds_meta):
    """Resolve a kind -> canonical Pnn_name dir. Unknown kinds default to P01."""
    entry = kinds_meta.get(kind) if isinstance(kinds_meta, dict) else None
    pnum = (entry or {}).get("pillar") if isinstance(entry, dict) else None
    if isinstance(pnum, str):
        pnum = pnum.split("_", 1)[0].upper()
    return PILLAR_BY_NUM.get(pnum, "P01_knowledge")


def load_purpose(args, registry):
    """Build the purpose contract. A --purpose-model frontmatter (N06 user_model
    instance) overrides; otherwise run the heuristic vertical detector on the text.
    Returns a normalized dict the assembler reasons over."""
    purpose_text = args.purpose or ""
    model_fm = {}
    if args.purpose_model:
        raw = Path(args.purpose_model).read_text(encoding="utf-8")
        model_fm = parse_frontmatter(raw) or {}
        if not purpose_text:
            purpose_text = str(model_fm.get("tldr") or model_fm.get("title") or "")

    det = VD.detect(purpose_text, registry) if purpose_text else {
        "vertical": "derive_from_purpose", "confidence": 0.0, "committed": False,
        "status": "fallback", "kind": None, "kind_palette": [], "nucleus_palette": [],
        "monetization_default": None, "rationale": "no purpose text supplied"}

    vertical = args.vertical or det.get("vertical")
    # explicit --vertical override re-reads the registry palette directly
    if args.vertical and args.vertical in registry.get("verticals", {}):
        entry = registry["verticals"][args.vertical]
        det = dict(det, vertical=args.vertical, status=entry.get("status"),
                   kind=entry.get("kind"), kind_palette=entry.get("kind_palette", []),
                   nucleus_palette=entry.get("nucleus_palette", []),
                   monetization_default=entry.get("monetization_default"), committed=True)

    brain = args.brain or slugify(str(model_fm.get("brain_name") or "") or
                                   (vertical if vertical != "derive_from_purpose" else "") or
                                   (purpose_text[:40] if purpose_text else "vertical")) or "vertical"
    return {
        "purpose_text": purpose_text,
        "vertical": vertical,
        "status": det.get("status"),
        "backing_kind": det.get("kind"),
        "confidence": det.get("confidence", 0.0),
        "kind_palette": list(det.get("kind_palette") or []),
        "nucleus_palette": list(det.get("nucleus_palette") or []),
        "monetization_default": det.get("monetization_default"),
        "brain": brain,
        "detect_rationale": det.get("rationale", ""),
    }


def load_distilled(distilled_dir):
    """Read an N04 distill OUT dir. Returns the manifest ledger + per-source KC metas
    + the aggregate artifact ids. Degrades to an empty contract when absent/partial."""
    out = {"present": False, "dir": None, "brain": None, "vertical": None, "depth": None,
           "kc_metas": [], "kc_files": [], "entity_memory_id": None, "index_slug": None,
           "knowledge_graph_id": None, "sources": []}
    if not distilled_dir:
        return out
    ddir = Path(distilled_dir)
    manifest = ddir / "_brain_manifest.json"
    if not manifest.exists():
        out["note"] = "no _brain_manifest.json at %s (degraded: skeleton from purpose only)" % ddir.as_posix()
        return out
    ledger = json.loads(manifest.read_text(encoding="utf-8"))
    out["present"] = True
    out["dir"] = ddir
    out["brain"] = ledger.get("brain")
    out["vertical"] = ledger.get("vertical")
    out["depth"] = ledger.get("depth")
    out["index_slug"] = ledger.get("index_slug")
    out["entity_memory_id"] = ledger.get("em_id")
    for sid, rec in (ledger.get("sources") or {}).items():
        meta = rec.get("meta") or {}
        out["kc_metas"].append(meta)
        out["sources"].append({"source_id": sid, "uri": meta.get("uri", ""),
                               "kc_path": rec.get("kc_path", "")})
    # collect concrete artifact files for ingestion into P01/P10
    for sub, key in (("knowledge_card", "kc_files"),):
        d = ddir / sub
        if d.is_dir():
            out[key] = sorted(p.name for p in d.glob("*.md"))
    if (ddir / "knowledge_graph").is_dir():
        kgs = sorted((ddir / "knowledge_graph").glob("*.md"))
        if kgs:
            fm = parse_frontmatter(kgs[0].read_text(encoding="utf-8")) or {}
            out["knowledge_graph_id"] = fm.get("id")
    return out


# ===========================================================================
# THE NET-NEW: derive the tailored kind/nucleus palette from purpose + knowledge
# ===========================================================================

def derive_palette(purpose, distilled, depth):
    """purpose + distilled knowledge -> the tailored kind set that seeds the brain.

    This is the gap closed by Gap#3: a mapping from (vertical palette) + (distilled
    KC feeds_kinds + keywords) to the agent_package file set. Three layers:
      1. SPINE      -- the 7 agent_package input kinds, always present.
      2. VERTICAL   -- the N06 registry kind_palette for the detected vertical, OR
      2'. DERIVED   -- when the vertical has no backing palette (derive_from_purpose),
                       derive from distilled KC feeds_kinds + keyword hits + purpose text.
      3. DEPTH      -- LIGHT keeps the top slice; DEEP adds the full palette + graph.
    """
    rationale = []
    spine_kinds = [k for k, _ in SPINE]

    vertical_kinds = list(purpose.get("kind_palette") or [])
    nuclei = list(purpose.get("nucleus_palette") or [])

    if vertical_kinds:
        rationale.append("vertical '%s' (%s): %d kinds from N06 registry palette"
                         % (purpose["vertical"], purpose.get("status"), len(vertical_kinds)))
    else:
        # derive_from_purpose -- no backing kind palette; synthesize one.
        derived = Counter()
        for meta in distilled.get("kc_metas", []):
            for fk in meta.get("feeds_kinds", []) or []:
                derived[fk] += 2  # explicit feeds_kinds is strong signal
            for kw in meta.get("keywords", []) or []:
                hit = KEYWORD_TO_KIND.get(str(kw).lower())
                if hit:
                    derived[hit] += 1
        text_lower = (purpose.get("purpose_text") or "").lower()
        for kw, kind in KEYWORD_TO_KIND.items():
            if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
                derived[kind] += 1
        vertical_kinds = [k for k, _ in derived.most_common()] or list(DEFAULT_DERIVED)
        nuclei = nuclei or ["n04", "n03", "n01"]
        rationale.append("derive_from_purpose: synthesized %d kind(s) from distilled "
                         "feeds_kinds + keyword hits + purpose text" % len(vertical_kinds))

    if depth == "light":
        kept = vertical_kinds[:6]
        rationale.append("LIGHT: kept top %d vertical kind(s) (D4 default)" % len(kept))
        vertical_kinds = kept
    else:
        vertical_kinds = vertical_kinds + [k for k in DEEP_EXTRAS if k not in vertical_kinds]
        rationale.append("DEEP: full palette + %s" % ", ".join(DEEP_EXTRAS))

    # merge spine + vertical, dedup, preserve order
    seen, merged = set(), []
    for k in spine_kinds + vertical_kinds:
        if k not in seen:
            seen.add(k)
            merged.append(k)
    return {"kinds": merged, "nuclei": nuclei or ["n03", "n04", "n01"],
            "spine": spine_kinds, "vertical_kinds": vertical_kinds, "rationale": rationale}


def map_kinds_to_pillars(palette, kinds_meta):
    """Group the derived kinds by their canonical pillar. SPINE kinds use their fixed
    pillar (kc_agent_package); palette kinds resolve via kinds_meta."""
    spine_pillar = {k: PILLAR_BY_NUM.get(p, "P01_knowledge") for k, p in SPINE}
    by_pillar = {p: [] for p in PILLAR_DIRS}
    for kind in palette["kinds"]:
        pdir = spine_pillar.get(kind) or pillar_for_kind(kind, kinds_meta)
        if kind not in by_pillar[pdir]:
            by_pillar[pdir].append(kind)
    return by_pillar


# ===========================================================================
# compose -- the 12-pillar fractal + manifest + instructions
# ===========================================================================

def _fm_block(fm):
    out = ["---"]
    for k, v in fm.items():
        if isinstance(v, list):
            if not v:
                out.append("%s: []" % k)
            elif all(isinstance(x, str) for x in v) and sum(len(x) for x in v) < 110:
                out.append("%s: [%s]" % (k, ", ".join(v)))
            else:
                out.append("%s:" % k)
                for x in v:
                    out.append("  - %s" % x)
        elif v is None:
            out.append("%s: null" % k)
        else:
            out.append("%s: %s" % (k, v))
    out.append("---")
    out.append("")
    return "\n".join(out)


def _related_table(pairs):
    lines = ["## Related Artifacts", "", "| Artifact | Relationship | Score |",
             "|----------|-------------|-------|"]
    for art, rel, score in pairs:
        lines.append("| [[%s]] | %s | %s |" % (art, rel, score))
    lines.append("")
    return "\n".join(lines)


def compose_pillar(pnum, brain, vertical, purpose, by_pillar, distilled, today):
    """Render one pillar .md for the brain. Content is derived from the seeded kinds +
    distilled knowledge + purpose. P01 + P10 ingest the N04 artifacts by reference."""
    pdir = PILLAR_BY_NUM[pnum]
    seeded = by_pillar.get(pdir, [])
    title = "%s -- %s brain" % (pdir, brain)
    fm = OrderedDict([
        ("id", "%s_brain_%s" % (pnum.lower(), _id_slug(brain))),
        ("kind", "knowledge_card"), ("8f", "F3_inject"), ("pillar", pnum),
        ("nucleus", "n03"), ("title", title), ("version", "1.0.0"),
        ("created", today), ("updated", today), ("author", FROZEN_BY),
        ("domain", vertical), ("quality", None),
        ("tags", [pdir, "agent_package", "brain", vertical, "assimilated"]),
        ("tldr", "%s pillar of the %s vertical brain: %s." % (pnum, vertical, PILLAR_ROLE[pnum])),
    ])
    body = ["# %s" % title, "",
            "> Role: %s" % PILLAR_ROLE[pnum], ""]
    if seeded:
        body += ["## Seeded kinds (this vertical)", "",
                 "| Kind | Why seeded |", "|------|-----------|"]
        for k in seeded:
            why = "agent_package spine" if k in [s for s, _ in SPINE] else "vertical palette / derived"
            body.append("| %s | %s |" % (k, why))
        body.append("")

    if pnum == "P01":
        body += ["## Distilled knowledge (from N04)", ""]
        if distilled.get("present") and distilled.get("kc_files"):
            body += ["Ingested %d distilled knowledge_card(s):" % len(distilled["kc_files"]), ""]
            for f in distilled["kc_files"]:
                body.append("- `%s`" % f)
            body.append("")
            body.append("> Copied into this pillar at assemble time; provenance in the brain index (P10).")
        else:
            body.append("> [DEGRADED] no distilled corpus supplied -- pillar seeded from purpose only.")
        body.append("")
    elif pnum == "P02":
        body += ["## Identity", "",
                 "| Field | Value |", "|-------|-------|",
                 "| name | {{BRAND_NAME}} %s assistant |" % vertical,
                 "| role | %s |" % (purpose.get("purpose_text") or "vertical operator")[:80],
                 "| voice | {{BRAND_VOICE_TONE}} |",
                 "| expertise | %s |" % vertical,
                 "| nuclei | %s |" % ", ".join(purpose.get("nucleus_palette") or ["n03"]),
                 ""]
    elif pnum == "P03":
        body += ["## Generation recipes", "",
                 "- system_prompt: the {{BRAND_NAME}} %s operating identity (see 00_instructions)." % vertical,
                 "- instruction: step-by-step task protocol for %s deliverables." % vertical, ""]
    elif pnum == "P09":
        body += ["## Config + monetization", "",
                 "| Parameter | Value |", "|-----------|-------|",
                 "| monetization_model | %s |" % (purpose.get("monetization_default") or "[FILL]"),
                 "| depth | %s |" % distilled.get("depth", "light"),
                 "| privacy | lab_only |", ""]
    elif pnum == "P10":
        body += ["## Memory + brain index (from N04)", ""]
        if distilled.get("present"):
            body += ["| Artifact | id |", "|----------|----|"]
            if distilled.get("entity_memory_id"):
                body.append("| entity_memory | [[%s]] |" % distilled["entity_memory_id"])
            if distilled.get("index_slug"):
                body.append("| knowledge_index | [[%s]] |" % distilled["index_slug"])
            if distilled.get("knowledge_graph_id"):
                body.append("| knowledge_graph | [[%s]] |" % distilled["knowledge_graph_id"])
            body.append("")
            body.append("> The brain index is SCOPED to the assimilated source set (never the whole repo).")
        else:
            body.append("> [DEGRADED] no entity_memory / brain index -- run cex_distill_orchestrator first.")
        body.append("")
    elif pnum == "P11":
        body += ["## The 3 universal rules (NON-NEGOTIABLE)", "",
                 "1. **Anti-hallucination** -- truth = user input; never fabricate "
                 "numbers/certs/prices; gap -> ask or `[FILL]`; end with '## Assumptions to confirm'.",
                 "2. **Paste-intake** -- never assume a URL opens; ask the user to paste.",
                 "3. **Code-block output** -- every deliverable inside fenced blocks.", "",
                 "(= runtime constitution: ground_or_abstain + untrusted_input.)", ""]
    elif pnum == "P12":
        body += ["## Operating loop", "",
                 "1. Intake purpose/source (paste-first).",
                 "2. Retrieve from the scoped brain index (P10).",
                 "3. Produce the deliverable under the 3 rules (P11).",
                 "4. Self-check against the quality gate (P07).",
                 "5. boot_config + fallback_chain govern runtime + provider failover.", ""]
    else:
        body += ["## %s" % PILLAR_ROLE[pnum].split(":")[0],
                 "", "> Tailored for the %s vertical at assemble time. [FILL: domain content]" % vertical, ""]

    body.append(_related_table([
        ("p02_iso_%s_brain" % _id_slug(brain), "upstream (manifest)", "0.40"),
        ("p01_kc_agent_package", "upstream", "0.30"),
        ("spec_init_assimilation_engine", "related", "0.25"),
    ]))
    return _fm_block(fm) + "\n".join(body) + "\n"


def compose_manifest(brain, vertical, purpose, palette, by_pillar, distilled,
                     tier, files_count, freeze_status, open_vars, today):
    """The agent_package identity card (manifest.yaml-as-markdown), v2.0 fractal +
    the 5 required body sections from bld_schema_agent_package."""
    bslug = _id_slug(brain)
    fidelity = "whitelabel" if freeze_status != "frozen" else "full"
    manifest_yaml = [
        "```yaml",
        "agent: %s_brain" % bslug,
        'name: "{{BRAND_NAME}} %s brain"' % vertical,
        'description: "Portable 12-pillar %s vertical brain assembled from purpose + distilled knowledge."' % vertical,
        "domain: %s" % vertical,
        'version: "1.0.0"',
        "fidelity: %s" % fidelity,
        'fidelity_reason: "%s"' % (
            "open_vars unresolved (no brand_config) -> whitelabel late-binding"
            if freeze_status != "frozen" else "brand_config resolved at freeze"),
        "tier: %s" % tier,
        "file_count: %d" % files_count,
        "target_llms: [claude, gpt, gemini, llama]",
        "targets: [custom_gpt, chatgpt_projects, gemini_gem, claude_project, railway]",
        "monetization_model: %s" % (purpose.get("monetization_default") or "derive_from_purpose"),
        "nuclei: [%s]" % ", ".join(palette["nuclei"]),
        "kinds_seeded: [%s]" % ", ".join(palette["kinds"]),
        "variables: [%s]" % ", ".join("{{%s}}" % v for v in open_vars) if open_vars else "variables: []",
        "privacy: lab_only",
        "```",
    ]
    fm = OrderedDict([
        ("id", "p02_iso_%s_brain" % bslug), ("kind", "agent_package"), ("8f", "F2_become"),
        ("pillar", "P02"), ("title", "Agent Package -- %s vertical brain" % vertical),
        ("version", "1.0.0"), ("created", today), ("updated", today), ("author", FROZEN_BY),
        ("agent_name", "%s_brain" % bslug), ("tier", tier), ("files_count", files_count),
        ("domain", vertical), ("quality", None), ("portable", "true"), ("llm_function", "BECOME"),
        ("tags", ["agent_package", "brain", vertical, "assimilated", "iso", "portable"]),
        ("tldr", ("Portable 12-pillar %s vertical brain assembled from purpose + "
                  "distilled knowledge (%d files, tier %s)." % (vertical, files_count, tier))[:159]),
        ("related", ["p01_kc_agent_package", "spec_init_assimilation_engine",
                     "agent-package-builder", "bld_model_agent_package"]),
    ])
    body = [
        "# Agent Package: %s vertical brain" % vertical, "",
        "## manifest.yaml (identity card)", *manifest_yaml, "",
        "## Agent Identity",
        "A portable %s vertical business brain. Assembled by `cex_brain_assembler.py` from a "
        "PURPOSE (%s) + a DISTILLED knowledge set + the N06 vertical palette. Build once -> "
        "run on any LLM surface. LAB-ONLY (the user owns it)." % (
            vertical, purpose.get("status") or "derive_from_purpose"), "",
        "## File Inventory", "",
        "| File | Pillar | Tier | Status |", "|------|--------|------|--------|",
        "| manifest.yaml | P02 | minimal | present |",
        "| 00_instructions.md | P03 | minimal | present |",
    ]
    for pnum in [p.split("_", 1)[0] for p in PILLAR_DIRS]:
        body.append("| %s/ | %s | fractal | present |" % (PILLAR_BY_NUM[pnum], pnum))
    body += [
        "",
        "## Tier Compliance",
        "Declared tier: **%s**. Files present: %d. Profile: v2.0 12-pillar fractal "
        "(00_instructions + P01..P12). cex_repo_align: 12/12 pillars." % (tier, files_count), "",
        "## Portability Notes",
        "- Platform: platform_agnostic (target_llms: claude, gpt, gemini, llama).",
        "- Hardcoded paths: none (relative references only).",
        "- Open variables: %s." % (", ".join("{{%s}}" % v for v in open_vars) if open_vars
                                    else "none (frozen against brand_config)"),
        "- Freeze status: **%s**." % freeze_status, "",
        "## References",
        "- Output format: [[p01_kc_agent_package]] (v2.0 12-pillar fractal).",
        "- Vertical palette: N06 vertical_templates registry (vertical=%s)." % vertical,
        "- Distilled knowledge: N04 cex_distill_orchestrator (%s)." % (
            "present" if distilled.get("present") else "DEGRADED -- skeleton from purpose only"),
        "- Assembler: `_tools/cex_brain_assembler.py` (Stage 3 ASSEMBLE).", "",
        _related_table([
            ("p01_kc_agent_package", "upstream", "0.40"),
            ("spec_init_assimilation_engine", "upstream", "0.32"),
            ("agent-package-builder", "upstream", "0.28"),
            ("bld_model_agent_package", "related", "0.26"),
        ]),
    ]
    return _fm_block(fm) + "\n".join(body) + "\n"


def compose_instructions(brain, vertical, purpose, palette, today):
    """00_instructions.md -- compact prompt, 6-section anatomy, <= 8000 chars."""
    lines = [
        "# {{BRAND_NAME}} %s brain -- operating instructions" % vertical, "",
        "## Identity",
        "You are the {{BRAND_NAME}} %s vertical brain. Voice: {{BRAND_VOICE_TONE}}. "
        "You serve: %s." % (vertical, (purpose.get("purpose_text") or "the user's purpose")[:160]), "",
        "## Knowledge base (map P01..P12)",
    ]
    for pnum in [p.split("_", 1)[0] for p in PILLAR_DIRS]:
        lines.append("- %s: %s" % (pnum, PILLAR_ROLE[pnum]))
    lines += [
        "", "## Operating procedure",
        "Intake (paste-first) -> retrieve from the scoped brain index (P10) -> produce under "
        "the 3 rules -> self-check against the P07 gate. Full loop: P12.", "",
        "## Tools",
        "Seeded kinds: %s. Each declares WHEN to use it + a manual substitute (P04)." % (
            ", ".join(palette["kinds"][:10])), "",
        "## Unbreakable rules",
        "1. Anti-hallucination: truth = user input; never fabricate numbers/certs/prices; "
        "gap -> ask or [FILL]; always end with '## Assumptions to confirm'.",
        "2. Paste-intake: never assume a URL opens; ask the user to paste.",
        "3. Code-block output: every deliverable inside fenced blocks.", "",
        "## Output",
        "Deliverables in fenced blocks (one per unit); chatter outside; close with "
        "'## Assumptions to confirm'.", "",
    ]
    text = "\n".join(lines)
    if len(text) > 8000:
        text = text[:7980] + "\n[truncated to 8000]\n"
    return text


# ===========================================================================
# freeze (brand open_vars) + 12-pillar verify
# ===========================================================================

def collect_brand_tokens(brain_dir):
    tokens = set()
    for p in brain_dir.rglob("*"):
        if p.is_file() and p.suffix in (".md", ".yaml", ".yml"):
            for m in _BRAND_TOKEN_RE.finditer(p.read_text(encoding="utf-8", errors="replace")):
                tokens.add(m.group(1))
    return sorted(tokens)


def brain_freeze(brain_dir, brand_config_path, execute):
    """Resolve {{BRAND_*}} open_vars against brand_config and FREEZE in place. REUSES
    the blueprints.freeze resolution + provenance mechanic. Degrades to WHITELABEL
    (placeholders kept, declared in manifest.variables) when no config is present."""
    load_config, lookup_dotted, now_iso, protocol, source = _load_freeze_api()
    tokens = collect_brand_tokens(brain_dir)

    cfg, cfg_path = None, None
    for cand in (brand_config_path, DEFAULT_BRAND_CONFIG):
        if cand and Path(cand).exists():
            try:
                cfg = load_config(cand)
                cfg_path = Path(cand).as_posix()
                break
            except Exception:
                cfg = None

    filled, unresolved = {}, []
    if cfg:
        for tok in tokens:
            key = BRAND_KEY_MAP.get(tok)
            found, val = lookup_dotted(cfg, key) if key else (False, None)
            if found and not str(val).startswith("{{"):
                filled[tok] = val
            else:
                unresolved.append(tok)
    else:
        unresolved = list(tokens)

    if execute and filled:
        for p in brain_dir.rglob("*"):
            if p.is_file() and p.suffix in (".md", ".yaml", ".yml"):
                txt = p.read_text(encoding="utf-8", errors="replace")
                new = txt
                for tok, val in filled.items():
                    new = new.replace("{{%s}}" % tok, str(val))
                if new != txt:
                    p.write_text(new, encoding="utf-8", newline="\n")

    status = "frozen" if (cfg and not unresolved) else ("partial" if filled else "whitelabel")
    provenance = OrderedDict([
        ("_open_vars_frozen", status == "frozen"),
        ("_frozen_at", now_iso()),
        ("_frozen_by", FROZEN_BY),
        ("_protocol_version", protocol),
        ("_freeze_source", source),
        ("_brand_config", cfg_path),
        ("_filled_vars", filled),
        ("_open_vars_remaining", sorted(unresolved)),
    ])
    if execute:
        (brain_dir / "_freeze.json").write_text(
            json.dumps(provenance, indent=2, ensure_ascii=True), encoding="utf-8", newline="\n")
    return {"status": status, "filled": filled, "remaining": sorted(unresolved),
            "brand_config": cfg_path, "tokens": tokens}


def verify_12_pillar(brain_dir):
    """REUSE cex_repo_align.scan_nucleus to assert the brain has all 12 canonical
    pillar subdirs. Returns (ok_count, missing, wrong)."""
    res = ALIGN.scan_nucleus(brain_dir)
    return {"ok": len(res["ok"]), "missing": [m["expected"] for m in res["missing"]],
            "wrong": [w["current"] for w in res["wrong"]], "total": len(PILLAR_DIRS)}


# ===========================================================================
# orchestration
# ===========================================================================

def assemble(args):
    today = date.today().isoformat()
    registry = VD.load_registry(args.registry)
    kinds_meta = load_kinds_meta()

    purpose = load_purpose(args, registry)
    distilled = load_distilled(args.distilled)
    depth = args.depth or (distilled.get("depth") or "light")
    palette = derive_palette(purpose, distilled, depth)
    by_pillar = map_kinds_to_pillars(palette, kinds_meta)

    brain = purpose["brain"]
    vertical = purpose["vertical"]
    brain_dir = Path(args.out) / ("brain_%s" % _id_slug(brain))

    # ---- 8F trace (stderr, so --json stdout stays machine-parseable) ----
    def _t(msg):
        print(msg, file=sys.stderr)

    _t("=== BRAIN ASSEMBLER (Stage 3: ASSEMBLE) ===")
    _t("F1 CONSTRAIN: brain=%s vertical=%s depth=%s %s" % (
        brain, vertical, depth, "(dry-run)" if not args.execute else ""))
    _t("F2 BECOME:    N03 Engineering -- vertical-brain assembler (agent_package v2.0 fractal)")
    _t("F3 INJECT:    purpose=%s distilled=%s palette=%d kinds" % (
        purpose["status"], "present" if distilled["present"] else "DEGRADED", len(palette["kinds"])))
    for r in palette["rationale"]:
        _t("              - %s" % r)

    # ---- compose ----
    written = []
    pillar_nums = [p.split("_", 1)[0] for p in PILLAR_DIRS]
    if args.execute:
        ensure_dir(brain_dir)
    for pnum in pillar_nums:
        pdir = brain_dir / PILLAR_BY_NUM[pnum]
        content = compose_pillar(pnum, brain, vertical, purpose, by_pillar, distilled, today)
        if args.execute:
            ensure_dir(pdir)
            (pdir / ("%s_brain.md" % pnum.lower())).write_text(content, encoding="utf-8", newline="\n")
        written.append("%s/%s_brain.md" % (PILLAR_BY_NUM[pnum], pnum.lower()))

    # ingest distilled KCs into P01 + aggregate artifacts into P10 (copy by content)
    ingested = 0
    if args.execute and distilled.get("present") and distilled.get("dir"):
        ddir = distilled["dir"]
        p01 = brain_dir / "P01_knowledge"
        for fname in distilled.get("kc_files", []):
            src = ddir / "knowledge_card" / fname
            if src.exists():
                ensure_dir(p01)
                (p01 / fname).write_text(src.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
                ingested += 1
                written.append("P01_knowledge/%s" % fname)
        p10 = brain_dir / "P10_memory"
        for sub in ("entity_memory", "knowledge_index", "knowledge_graph"):
            sd = ddir / sub
            if sd.is_dir():
                for f in sorted(sd.glob("*.md")):
                    ensure_dir(p10)
                    (p10 / f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
                    written.append("P10_memory/%s" % f.name)

    # instructions (always) -- count toward files
    instr = compose_instructions(brain, vertical, purpose, palette, today)
    if args.execute:
        (brain_dir / "00_instructions.md").write_text(instr, encoding="utf-8", newline="\n")
    written.append("00_instructions.md")

    # ---- freeze (after all body files exist) ----
    if args.execute:
        freeze = brain_freeze(brain_dir, args.brand_config, args.execute)
    else:
        freeze = {"status": "whitelabel (dry)", "filled": {}, "remaining": sorted(BRAND_KEY_MAP),
                  "brand_config": None, "tokens": sorted(BRAND_KEY_MAP)}
    open_vars = freeze["remaining"]

    # ---- tier + files_count + manifest ----
    files_count = len(written) + 1  # + manifest.yaml itself
    if freeze["status"].startswith("whitelabel"):
        tier = "whitelabel"
    elif files_count >= 10:
        tier = "complete"
    elif files_count >= 7:
        tier = "standard"
    else:
        tier = "minimal"
    manifest = compose_manifest(brain, vertical, purpose, palette, by_pillar, distilled,
                                tier, files_count, freeze["status"], open_vars, today)
    if args.execute:
        (brain_dir / "manifest.yaml").write_text(manifest, encoding="utf-8", newline="\n")

    # ---- verify 12-pillar ----
    if args.execute:
        verify = verify_12_pillar(brain_dir)
    else:
        verify = {"ok": len(PILLAR_DIRS), "missing": [], "wrong": [], "total": len(PILLAR_DIRS),
                  "note": "dry-run: 12 pillars planned"}

    # ---- F7 gates on the manifest (citation + reasoning_trace) ----
    man_fm = parse_frontmatter(manifest) or {}
    gates = f7_gates(man_fm, manifest)
    hard_fail = [g for g in gates if g["applies"] and g["fails"]]

    _t("F4 REASON:    %d pillars planned, %d kinds mapped, tier=%s" % (
        len(PILLAR_DIRS), len(palette["kinds"]), tier))
    _t("F5 CALL:      freeze=%s (reuse blueprints.freeze) verify=cex_repo_align" % freeze["status"])
    _t("F6 PRODUCE:   %d files%s | manifest p02_iso_%s_brain" % (
        files_count, " (ingested %d distilled KC)" % ingested if ingested else "", _id_slug(brain)))
    _t("F7 GOVERN:    12-pillar %d/%d%s | F7 gates: %s" % (
        verify["ok"], verify["total"],
        "" if not verify["missing"] else " MISSING %s" % verify["missing"],
        "PASS" if not hard_fail else "HARD FAIL %s" % [g["gate"] for g in hard_fail]))
    _t("F8 SUMMARY:   brain=%s out=%s %s" % (
        brain, brain_dir.as_posix(), "WROTE" if args.execute else "(dry-run -- pass --execute)"))

    result = {
        "brain": brain, "vertical": vertical, "status": purpose["status"],
        "confidence": purpose["confidence"], "depth": depth, "tier": tier,
        "files_count": files_count, "out_dir": brain_dir.as_posix(),
        "pillars": {"ok": verify["ok"], "total": verify["total"], "missing": verify["missing"]},
        "palette": {"kinds": palette["kinds"], "nuclei": palette["nuclei"]},
        "palette_rationale": palette["rationale"],
        "distilled": {"present": distilled["present"], "kc_ingested": ingested,
                      "sources": len(distilled.get("sources", []))},
        "freeze": {"status": freeze["status"], "filled": list(freeze["filled"].keys()),
                   "open_vars": freeze["remaining"], "brand_config": freeze["brand_config"]},
        "f7_gates": gates, "f7_hard_fail": [g["gate"] for g in hard_fail],
        "files": written + ["manifest.yaml"],
        "executed": bool(args.execute),
    }
    return result


# ===========================================================================
# self-test (offline, writes under a temp dir, asserts the acceptance contract)
# ===========================================================================

def run_self_test():
    import tempfile
    samples = [
        ("We are a software agency building custom software and MVPs for client projects", "dev_shop"),
        ("a neobank with KYC and AML compliance for payments", "fintech"),
        ("something totally unclassifiable with no signals whatsoever", "derive_from_purpose"),
    ]
    print("=== cex_brain_assembler --self-test ===")
    ok = 0
    for purpose_text, expect_vertical in samples:
        with tempfile.TemporaryDirectory() as td:
            ns = argparse.Namespace(
                purpose=purpose_text, purpose_model=None, vertical=None, brain=None,
                distilled=None, out=td, depth="light", brand_config=None,
                registry=VD.DEFAULT_REGISTRY, json=True, execute=True)
            res = assemble(ns)
            pill_ok = res["pillars"]["ok"] == 12 and not res["pillars"]["missing"]
            has_spine = all(k in res["palette"]["kinds"] for k in ("agent", "system_prompt", "guardrail"))
            vmatch = res["vertical"] == expect_vertical
            good = pill_ok and has_spine and vmatch
            ok += 1 if good else 0
            print("  [%s] vertical=%-20s pillars=%d/12 spine=%s files=%d" % (
                "OK" if good else "XX", res["vertical"], res["pillars"]["ok"],
                "yes" if has_spine else "NO", res["files_count"]))
    print("-" * 60)
    print("self-test: %d/%d passed (acceptance: 3/3)" % (ok, len(samples)))
    return 0 if ok == len(samples) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="Assemble a 12-pillar vertical brain (agent_package ISO) from purpose + distilled knowledge.")
    ap.add_argument("--purpose", help="free-form purpose statement (what brain + for what)")
    ap.add_argument("--purpose-model", dest="purpose_model", help="path to a user_model_assimilation_purpose instance")
    ap.add_argument("--vertical", help="explicit vertical override (skip auto-detect)")
    ap.add_argument("--brain", help="brain name/namespace (default: derived from vertical/purpose)")
    ap.add_argument("--distilled", help="N04 distill OUT dir (_brain_manifest.json + knowledge_card/ + ...)")
    ap.add_argument("--out", help="output directory for the assembled brain")
    ap.add_argument("--depth", choices=["light", "deep"], help="light=core spine+top kinds (default); deep=+full palette+graph")
    ap.add_argument("--brand-config", dest="brand_config", help="brand_config to freeze open_vars against (default: .cex/brand/brand_config.yaml)")
    ap.add_argument("--registry", default=VD.DEFAULT_REGISTRY, help="vertical_templates.yaml")
    ap.add_argument("--json", action="store_true", help="emit the machine result as JSON")
    ap.add_argument("--execute", action="store_true", help="write the brain (default: dry-run plan)")
    ap.add_argument("--self-test", action="store_true", help="run the offline acceptance test")
    args = ap.parse_args(argv)

    if args.self_test:
        return run_self_test()
    if not args.out:
        ap.error("--out is required (or use --self-test)")
    if not (args.purpose or args.purpose_model):
        ap.error("provide --purpose or --purpose-model")

    result = assemble(args)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0 if not result["f7_hard_fail"] and not result["pillars"]["missing"] else 1


if __name__ == "__main__":
    sys.exit(main())
