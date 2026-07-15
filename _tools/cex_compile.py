#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CEX Compiler: converts .md examples to compiled YAML/JSON for LLM consumption."""

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cex_shared import split_frontmatter as _shared_split_frontmatter


class CEXEncoder(json.JSONEncoder):
    """JSON encoder that handles date/datetime from YAML frontmatter."""

    def default(self, o):
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        return super().default(o)


CEX_ROOT = Path(__file__).resolve().parent.parent

# R-073: dynamically globbed (was a hardcoded 12-entry list) -- mirrors the technique
# _tools/cex_8f_runner.py already uses for the SAME job (PILLAR_DIRS, ~lines 222-227), so a 13th
# pillar added under N00_genesis needs zero code changes here (the old hardcoded list was a
# drift risk: nothing kept it in sync if a pillar were ever added/renamed). A/B-verified equal to
# the prior hardcoded list for today's 12 pillars (docs/IMPROVEMENT_REGISTER.md R-073).
LP_DIRS = [
    "N00_genesis/" + d.name
    for d in sorted((CEX_ROOT / "N00_genesis").glob("P[0-9][0-9]_*"))
    if d.is_dir()
]


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body from markdown text."""
    return _shared_split_frontmatter(text)


def load_schema(lp_dir: Path) -> dict:
    """Load _schema.yaml and return type -> machine_format mapping."""
    schema_path = lp_dir / "_schema.yaml"
    if not schema_path.exists():
        return {}
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = yaml.safe_load(f)
    if not schema or "kinds" not in schema:
        return {}
    result = {}
    for type_name, type_def in schema["kinds"].items():
        if isinstance(type_def, dict) and "machine_format" in type_def:
            result[type_name] = type_def["machine_format"]
    return result


def strip_markdown_decoration(text: str) -> str:
    """Remove bold, italic, links -- keep the text content."""
    # Links: [text](url) -> text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Bold+italic: ***text*** or ___text___
    text = re.sub(r"\*{3}(.+?)\*{3}", r"\1", text)
    text = re.sub(r"_{3}(.+?)_{3}", r"\1", text)
    # Bold: **text** or __text__
    text = re.sub(r"\*{2}(.+?)\*{2}", r"\1", text)
    text = re.sub(r"_{2}(.+?)_{2}", r"\1", text)
    # Italic: *text* or _text_ (careful not to match mid-word underscores)
    text = re.sub(r"(?<!\w)\*(.+?)\*(?!\w)", r"\1", text)
    text = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"\1", text)
    return text


def normalize_key(header: str) -> str:
    """Convert markdown header text to a YAML key."""
    # Remove markdown decoration
    header = strip_markdown_decoration(header)
    # Lowercase, strip, replace spaces/special with underscore
    key = header.strip().lower()
    key = re.sub(r"[^a-z0-9]+", "_", key)
    key = key.strip("_")
    return key


def parse_body_sections(body: str) -> dict:
    """Parse markdown body into structured sections keyed by header."""
    sections = {}
    current_key = None
    current_lines = []
    in_code_block = False
    first_h1_skipped = False

    for line in body.split("\n"):
        stripped = line.strip()

        # Track code blocks -- don't parse headers inside them
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            current_lines.append(line)
            continue

        if in_code_block:
            current_lines.append(line)
            continue

        # Match ## or ### headers (content sections)
        header_match = re.match(r"^(#{1,3})\s+(.+)$", line)
        if header_match:
            level = len(header_match.group(1))
            # Skip the first # header (document title, duplicates frontmatter)
            if level == 1 and not first_h1_skipped:
                first_h1_skipped = True
                continue
            # Save previous section
            if current_key is not None:
                sections[current_key] = process_section_content("\n".join(current_lines))
            current_key = normalize_key(header_match.group(2))
            current_lines = []
        else:
            current_lines.append(line)

    # Save last section
    if current_key is not None:
        sections[current_key] = process_section_content("\n".join(current_lines))

    return sections


def process_section_content(content: str) -> object:
    """Process a section's content -- detect lists, code blocks, or plain text."""
    content = content.strip()
    if not content:
        return ""

    content = strip_markdown_decoration(content)

    # Check if content is primarily a numbered or bulleted list
    lines = content.split("\n")
    list_lines = []
    non_list_lines = []
    in_code_block = False
    code_block_lines = []
    has_code_block = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_code_block:
                in_code_block = False
                has_code_block = True
            else:
                in_code_block = True
                code_block_lines = []
            continue
        if in_code_block:
            code_block_lines.append(line)
            continue

        if re.match(r"^[-*]\s+", stripped):
            # Bullet list item -- strip the marker
            item = re.sub(r"^[-*]\s+", "", stripped)
            list_lines.append(item)
        elif re.match(r"^\d+\.\s+", stripped):
            # Numbered list item -- strip the number
            item = re.sub(r"^\d+\.\s+", "", stripped)
            list_lines.append(item)
        elif stripped:
            non_list_lines.append(stripped)

    # If it's purely a code block, return as multiline string
    if has_code_block and not list_lines and not non_list_lines:
        return "\n".join(code_block_lines)

    # If it's purely a list, return as list
    if list_lines and not non_list_lines:
        return list_lines

    # If it's a mix or table, return as multiline text
    if has_code_block:
        # Re-assemble without markdown fences
        result_lines = []
        in_cb = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("```"):
                in_cb = not in_cb
                continue
            result_lines.append(line)
        return "\n".join(result_lines).strip()

    # If it has a table, keep as-is (multiline)
    if any("|" in line and "---" not in line for line in lines):
        return content

    # Mixed content or plain prose
    if list_lines and non_list_lines:
        # Return everything as multiline
        return content

    # Plain text -- join into single string if short
    text = " ".join(non_list_lines)
    return text


def compile_md(md_path: Path, schema_formats: dict) -> tuple[dict, str, str]:
    """Compile a single .md file to structured data.

    Returns: (compiled_data, format_ext, error_or_none)
    """
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()

    fm, body = parse_frontmatter(text)
    if not fm:
        return {}, "", f"No frontmatter found in {md_path}"

    artifact_type = fm.get("kind", "")
    machine_format = schema_formats.get(artifact_type, "yaml")

    # Build compiled output
    compiled = {}

    # Add key frontmatter fields (skip decorative ones like title, lp for compiled)
    for key, val in fm.items():
        compiled[key] = val

    # Parse body sections
    sections = parse_body_sections(body)

    # Merge body sections into compiled output
    for key, val in sections.items():
        if not key:
            continue
        compiled[key] = val

    ext = "json" if machine_format == "json" else "yaml"
    return compiled, ext, None


# R-330 (docs/IMPROVEMENT_REGISTER.md): 3 stems used, BY DESIGN, by more than one sibling
# pillar of the SAME nucleus, for a source living DIRECTLY in the pillar dir (not examples/
# or kind_{X}/ -- only ONE level below the pillar). For that shape, compile_file()'s
# `lp_dir = md_path.parent.parent` resolves to the NUCLEUS ROOT (`md_path.parent` IS the
# pillar dir), so every sibling pillar of that nucleus shares ONE compiled/ dir -- same
# stem collapses N sources onto one output, exactly the R-311 disease, a different variant
# (compiled_name_doctor's 1st live corpus scan, 2536 typed sources: kind_index.md x12 across
# every N00_genesis pillar, rag_source_intelligence.md x2 in N01, quality_gate_knowledge.md
# x2 in N04 -- all 3 confirmed live-collided on disk, single last-write-wins survivor each).
#
# Corpus-wide verified 2026-07-12: these 3 stems are the ONLY ones that collide today, and
# each is used EXCLUSIVELY by its colliding group (0 other tracked files anywhere share these
# exact stems) -- a closed, measured set, same shape as the kind_manifest branch below.
# Deliberately NOT a general "every direct-in-pillar file gets a pillar suffix" rule: the
# nucleus-root compiled/ dir this shape writes to already holds hundreds of ALREADY-unique,
# ALREADY-consumed direct-in-pillar outputs (e.g. `tpl_{kind}.yaml`, read unsuffixed by
# cex_sdk/agent/context_loader.py at the exact path `N00_genesis/compiled/tpl_{kind}.yaml`;
# also agent_card_n00.yaml, nucleus_def_n00.yaml, component_map_n00.yaml and ~45 ex_*.yaml
# siblings) -- a blanket suffix rule would rename all of them and break that live reader,
# a regression, not a fix. See _tools/tests/test_compile_r311.py for the before/after
# name-map proof (both the R-311 kind_manifest case and this R-330 direct-in-pillar case).
_DIRECT_IN_PILLAR_COLLISION_STEMS = frozenset(
    {"kind_index", "rag_source_intelligence", "quality_gate_knowledge"}
)
_PILLAR_DIR_NAME_RE = re.compile(r"^P\d{2}_")


def derive_out_name(md_path: Path, kind: str | None, ext: str) -> str:
    """Derive the compiled output filename for md_path (R-311/R-330 naming seam).

    Default rule (every kind/stem not special-cased below): the source filename's own
    stem already disambiguates it within its LP -- `out_name = stem + "." + ext`.

    R-311 fix: `kind_manifest` sources use an INVARIANT filename
    (`kind_manifest_n00.md`) that varies ONLY by parent directory
    (`kind_{kind}/kind_manifest_n00.md` -- see
    archetypes/builders/kind-manifest-builder/bld_config_kind_manifest.md and
    .cex/kinds_meta.json's own `naming: "kind_{{kind}}/kind_manifest_n00.md"`).
    Because `compile_file()`'s naming seam only ever looked at `md_path.stem`,
    every one of the ~294 kind_manifest sources under an LP derived the SAME
    stem ("kind_manifest_n00"), so N sources collapsed onto ONE compiled
    output -- only the last-compiled survived on disk, N-1 silently vanished
    (docs/IMPROVEMENT_REGISTER.md R-311, live-verified: 12 collision points,
    one per N00_genesis/P0X_*/compiled/kind_manifest_n00.yaml).

    Fix: for THIS kind only, fold the parent directory's `kind_{X}` suffix
    into the stem (`kind_manifest_n00` -> `kind_manifest_{X}_n00`), which is
    exactly the disambiguating signal the source layout already encodes
    structurally (live-verified 0/294 mismatches between the parent-dir
    suffix and the id's own `n00_{kind}_manifest` middle token). Every other
    kind's stem is already unique within its LP, so this branch never fires
    for them -- out_name is byte-identical to before (proved by the R-311
    fix's before/after name-map diff over >=5 non-kind_manifest kinds, see
    _tools/tests/test_compile_r311.py).

    R-330 fix (see the module-level comment above `_DIRECT_IN_PILLAR_COLLISION_STEMS`
    for the full rationale): for the 3 measured, direct-in-pillar colliding stems only,
    fold the parent pillar's lowercased code into the stem (`kind_index` in `P03_prompt/`
    -> `kind_index_p03`). Every other direct-in-pillar file's stem is untouched -- this
    branch never fires for them.
    """
    stem = md_path.stem
    if (
        kind == "kind_manifest"
        and stem == "kind_manifest_n00"
        and md_path.parent.name.startswith("kind_")
    ):
        disambiguator = md_path.parent.name[len("kind_"):]
        stem = "kind_manifest_%s_n00" % disambiguator
    elif stem in _DIRECT_IN_PILLAR_COLLISION_STEMS and _PILLAR_DIR_NAME_RE.match(md_path.parent.name):
        disambiguator = md_path.parent.name.split("_", 1)[0].lower()
        stem = "%s_%s" % (stem, disambiguator)
    return stem + "." + ext


def get_lp_dir_for_lp(lp_code: str) -> Path | None:
    """Find LP directory matching code like 'P03'."""
    for lp_dir_name in LP_DIRS:
        # lp_dir_name is e.g. "N00_genesis/P03_prompt"; basename starts with pillar code
        basename = lp_dir_name.split("/")[-1]
        if basename.startswith(lp_code + "_") or basename == lp_code:
            return CEX_ROOT / lp_dir_name
    return None


def compile_file(md_path: Path) -> bool:
    """Compile a single markdown file. Returns True on success."""
    md_path = md_path.resolve()

    # Determine LP from path
    lp_dir = md_path.parent.parent
    schema_formats = load_schema(lp_dir)

    compiled, ext, error = compile_md(md_path, schema_formats)
    if error:
        print(f"  SKIP: {error}")
        return False

    # Output path
    compiled_dir = lp_dir / "compiled"
    compiled_dir.mkdir(exist_ok=True)
    out_name = derive_out_name(md_path, compiled.get("kind"), ext)
    out_path = compiled_dir / out_name

    # Write
    with open(out_path, "w", encoding="utf-8") as f:
        if ext == "json":
            json.dump(compiled, f, indent=2, ensure_ascii=False, cls=CEXEncoder)
            f.write("\n")
        else:
            yaml.dump(
                compiled,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                width=120,
            )

    # Validate output
    with open(out_path, "r", encoding="utf-8") as f:
        content = f.read()
    try:
        if ext == "json":
            json.loads(content)
        else:
            yaml.safe_load(content)
    except Exception as e:
        print(f"  ERROR: Invalid {ext} output for {out_path}: {e}")
        return False

    # Inject structural_score into compiled YAML (8F_DECOMPOSE integration)
    try:
        import importlib.util
        _spec = importlib.util.spec_from_file_location(
            "cex_score", Path(__file__).parent / "cex_score.py")
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        ss = _mod.compute_structural_score(str(md_path), skip_compile=True)
        existing = open(out_path, 'r', encoding='utf-8').read()
        cleaned = "\n".join(
            l for l in existing.split("\n")
            if not l.startswith("structural_score:")
        )
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(cleaned.rstrip("\n") + "\n")
            f.write("structural_score: %d\n" % ss['total'])
    except Exception:
        pass  # scoring is advisory, never blocks compile

    print(f"  OK: {md_path.name} -> compiled/{out_name}")
    return True


def find_examples(lp_dir: Path) -> list[Path]:
    """Find all .md example files in an LP directory."""
    examples_dir = lp_dir / "examples"
    if not examples_dir.exists():
        return []
    return sorted(examples_dir.glob("*.md"))


## ---------------------------------------------------------------------------
## T10: Reverse-path renderers (CEX artifacts -> target format)
## ---------------------------------------------------------------------------

REVERSE_TARGETS = ["claude-md", "cursorrules", "customgpt", "mcp"]


def _load_compiled_artifacts(pillars=None):
    """Load all compiled YAML artifacts from specified pillars.

    Applies a quality floor: artifacts with quality < 7.0 are skipped
    to prevent low-quality content from being injected into reverse
    compile targets (CLAUDE.md, .cursorrules, customgpt).
    """
    if pillars is None:
        pillars = ["P03", "P04", "P08", "P11"]
    artifacts = []
    skipped = 0
    for lp_name in LP_DIRS:
        code = lp_name.split("/")[-1].split("_")[0]
        if code not in pillars:
            continue
        compiled_dir = CEX_ROOT / lp_name / "compiled"
        if not compiled_dir.exists():
            continue
        for f in sorted(compiled_dir.glob("*.yaml")):
            try:
                data = yaml.safe_load(f.read_text(encoding="utf-8"))
                if data and isinstance(data, dict):
                    # Quality floor: skip artifacts scored below 7.0
                    quality = data.get("quality")
                    if quality is not None and isinstance(quality, (int, float)) and quality < 7.0:
                        skipped += 1
                        continue
                    data["_source"] = str(f.relative_to(CEX_ROOT))
                    artifacts.append(data)
            except Exception:
                pass
    if skipped:
        print(f"  [WARN] Skipped {skipped} artifact(s) with quality < 7.0")
    return artifacts


def _load_brand_context():
    """Load brand config if available."""
    brand_path = CEX_ROOT / ".cex" / "brand" / "brand_config.yaml"
    if not brand_path.exists():
        return {}
    try:
        return yaml.safe_load(brand_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def render_claude_md(output_path=None):
    """T10: Render CEX artifacts into a CLAUDE.md project context file."""
    artifacts = _load_compiled_artifacts()
    brand = _load_brand_context()

    sections = []
    sections.append("# Project Context (auto-generated by CEX)")
    sections.append(f"# Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    sections.append("")

    # Brand section
    if brand:
        sections.append("## Brand Identity")
        for k, v in brand.items():
            if isinstance(v, str):
                sections.append(f"- **{k}**: {v}")
        sections.append("")

    # Group artifacts by kind
    by_kind = {}
    for a in artifacts:
        kind = a.get("kind", "unknown")
        by_kind.setdefault(kind, []).append(a)

    # System prompts first
    for kind in ["system_prompt", "instruction", "skill", "guardrail", "agent_card", "pattern"]:
        items = by_kind.pop(kind, [])
        if not items:
            continue
        sections.append(f"## {kind.replace('_', ' ').title()}s")
        for item in items:
            title = item.get("title", item.get("id", "untitled"))
            sections.append(f"### {title}")
            # Include key content fields
            for field in ["purpose", "tldr", "description", "content",
                          "when_to_use", "steps", "rules", "checks"]:
                val = item.get(field)
                if val:
                    if isinstance(val, list):
                        sections.append(f"**{field}**:")
                        for v in val:
                            sections.append(f"- {v}")
                    else:
                        sections.append(f"**{field}**: {val}")
            sections.append("")

    # Remaining kinds
    for kind, items in sorted(by_kind.items()):
        sections.append(f"## {kind.replace('_', ' ').title()}s")
        for item in items:
            title = item.get("title", item.get("id", "untitled"))
            sections.append(f"### {title}")
            tldr = item.get("tldr", "")
            if tldr:
                sections.append(f"> {tldr}")
            sections.append("")

    output = "\n".join(sections)
    out = Path(output_path) if output_path else CEX_ROOT / "CLAUDE_GENERATED.md"
    out.write_text(output, encoding="utf-8")
    print(f"  [OK] Rendered {len(artifacts)} artifacts -> {out} ({len(output)} bytes)")
    return str(out)


def render_cursorrules(output_path=None):
    """T10: Render CEX artifacts into a .cursorrules file."""
    artifacts = _load_compiled_artifacts(["P03", "P11"])
    brand = _load_brand_context()

    lines = []
    lines.append("# Project Rules (auto-generated by CEX)")
    lines.append("")

    if brand:
        lines.append(f"Brand: {brand.get('brand_name', 'Unknown')}")
        lines.append(f"Voice: {brand.get('brand_voice', '')}")
        lines.append("")

    for a in artifacts:
        kind = a.get("kind", "")
        title = a.get("title", a.get("id", ""))
        if kind == "guardrail":
            lines.append(f"## RULE: {title}")
            for field in ["checks", "rules", "content"]:
                val = a.get(field)
                if isinstance(val, list):
                    for v in val:
                        lines.append(f"- {v}")
                elif val:
                    lines.append(str(val))
            lines.append("")
        elif kind in ("system_prompt", "instruction"):
            lines.append(f"## {title}")
            content = a.get("content", a.get("tldr", ""))
            if content:
                lines.append(str(content))
            lines.append("")

    output = "\n".join(lines)
    out = Path(output_path) if output_path else CEX_ROOT / ".cursorrules"
    out.write_text(output, encoding="utf-8")
    print(f"  [OK] Rendered {len(artifacts)} artifacts -> {out}")
    return str(out)


def render_customgpt(output_path=None):
    """T10: Render CEX artifacts into CustomGPT instruction JSON."""
    artifacts = _load_compiled_artifacts()
    brand = _load_brand_context()

    instructions = []
    if brand:
        instructions.append(f"You are {brand.get('brand_name', 'an assistant')}.")
        voice = brand.get("brand_voice", "")
        if voice:
            instructions.append(f"Voice: {voice}")

    for a in artifacts:
        kind = a.get("kind", "")
        title = a.get("title", a.get("id", ""))
        tldr = a.get("tldr", "")
        if kind in ("system_prompt", "instruction", "guardrail"):
            instructions.append(f"[{kind}] {title}: {tldr}")

    payload = {
        "name": brand.get("brand_name", "CEX Agent"),
        "instructions": "\n".join(instructions),
        "artifact_count": len(artifacts),
    }

    out = Path(output_path) if output_path else CEX_ROOT / "customgpt_instructions.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False, cls=CEXEncoder), encoding="utf-8")
    print(f"  [OK] Rendered {len(artifacts)} artifacts -> {out}")
    return str(out)


TARGET_RENDERERS = {
    "claude-md": render_claude_md,
    "cursorrules": render_cursorrules,
    "customgpt": render_customgpt,
}


def main():
    parser = argparse.ArgumentParser(description="CEX Compiler: .md -> compiled YAML/JSON | reverse: compiled -> target format")
    parser.add_argument("file", nargs="?", help="Single .md file to compile")
    parser.add_argument("--all", action="store_true", help="Compile all examples in all LPs")
    parser.add_argument("--lp", help="Compile all examples in a specific LP (e.g., P03)")
    parser.add_argument("--target", choices=REVERSE_TARGETS, help="Reverse compile: render to target format")
    parser.add_argument("--output", "-o", help="Output path for --target")
    args = parser.parse_args()

    # --- T10: Reverse compilation ---
    if args.target:
        renderer = TARGET_RENDERERS.get(args.target)
        if not renderer:
            print(f"ERROR: Unknown target '{args.target}'. Available: {', '.join(REVERSE_TARGETS)}")
            sys.exit(1)
        renderer(args.output)
        sys.exit(0)

    if not args.file and not args.all and not args.lp:
        parser.print_help()
        sys.exit(1)

    total = 0
    success = 0

    if args.file:
        md_path = Path(args.file).resolve()
        if not md_path.exists():
            print(f"ERROR: File not found: {md_path}")
            sys.exit(1)
        total = 1
        if compile_file(md_path):
            success = 1

    elif args.lp:
        lp_dir = get_lp_dir_for_lp(args.lp)
        if not lp_dir or not lp_dir.exists():
            print(f"ERROR: LP directory not found for {args.lp}")
            sys.exit(1)
        print(f"Compiling {args.lp}...")
        for md_path in find_examples(lp_dir):
            total += 1
            if compile_file(md_path):
                success += 1

    elif args.all:
        for lp_dir_name in LP_DIRS:
            lp_dir = CEX_ROOT / lp_dir_name
            if not lp_dir.exists():
                continue
            examples = find_examples(lp_dir)
            if not examples:
                continue
            lp_code = lp_dir_name.split("/")[-1].split("_")[0]
            print(f"\n=== {lp_code} ({len(examples)} examples) ===")
            for md_path in examples:
                total += 1
                if compile_file(md_path):
                    success += 1

    print(f"\n--- Results: {success}/{total} compiled successfully ---")
    if success < total:
        sys.exit(1)


if __name__ == "__main__":
    try:
        from cex_agent_io import wrap_main

        def _main_wrapper(argv):
            sys.argv = [sys.argv[0]] + argv
            main()
            return 0

        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_compile"))
    except ImportError:
        main()
