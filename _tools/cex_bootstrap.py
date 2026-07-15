# -*- coding: utf-8 -*-
"""cex_bootstrap.py -- First-run brand setup for CEX instances.

When a user first clones/installs CEX, this script:
1. Detects if .cex/brand/brand_config.yaml has real values (not template)
2. If not -> launches interactive Brand Discovery (N06)
3. Validates the filled config
4. Propagates brand to all nuclei
5. Generates branded CLAUDE.md header
6. Audits brand consistency

The X in CEX is YOUR brand. This script fills it.

Usage:
    python _tools/cex_bootstrap.py                  # interactive first-run
    python _tools/cex_bootstrap.py --check           # just check if bootstrapped
    python _tools/cex_bootstrap.py --from-file input.yaml  # non-interactive
    python _tools/cex_bootstrap.py --reset           # clear brand (re-bootstrap)

Multi-tenant (HYBRID isolation -- p08_adr_multitenant_hybrid):
    python _tools/cex_bootstrap.py --tenant acme --from-file acme.yaml   # bootstrap tenant 'acme'
    python _tools/cex_bootstrap.py --tenant acme --check                 # check tenant 'acme'
    python _tools/cex_bootstrap.py --list-tenants                        # list bootstrapped tenants
    # Default (no --tenant, CEX_TENANT_ID unset) == single-tenant global, identical to before.
"""
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Do NOT auto-fetch PyYAML at import time (audit R11): an unpinned ``pip install``
# inside a governance-path tool is a supply-chain hazard (network fetch + arbitrary
# install-time code, no integrity pin). Fail with a clear, actionable message and let
# the operator install it explicitly.
try:
    import yaml
except ImportError as exc:
    raise ImportError(
        "cex_bootstrap requires PyYAML, which is not installed. Install it "
        "explicitly: 'pip install pyyaml' (or 'python -m pip install pyyaml'). It is "
        "NOT auto-fetched (no unpinned network install in a governance-path tool)."
    ) from exc

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "_tools"))

BRAND_DIR = ROOT / ".cex" / "brand"
BRAND_CONFIG = BRAND_DIR / "brand_config.yaml"
BRAND_TEMPLATE = BRAND_DIR / "brand_config_template.yaml"
BRAND_LOCK = BRAND_DIR / ".bootstrapped"
CLAUDE_MD = ROOT / "CLAUDE.md"
OSS_DEFAULTS = ROOT / ".cex" / "config" / "oss_defaults.yaml"
TENANTS_DIR = ROOT / ".cex" / "tenants"


# ---------------------------------------------------------------------------
# Brand-name resolution (shape-tolerant) + repo-root redirection.
#   A "sovereign brain" must never report its own brand-status as 'unknown' under a plausible
#   invocation. Two hardening primitives:
#     1. resolve_brand_name -- read the name from ALL three config shapes the repo has shipped
#        (nested identity.BRAND_NAME, apps/tenant brand.name, legacy TOP-LEVEL BRAND_NAME) and,
#        as a last resort, the .bootstrapped lock's `brand:` line.
#     2. _redirect_root -- re-point the path globals at a DIFFERENT repo so a central checkout's
#        cex_bootstrap can --check the repo the operator cd'd into (cwd-aware), not the factory's.
# ---------------------------------------------------------------------------
def _brand_name_from_config(config) -> str:
    """The brand name from a loaded brand_config dict, tolerant of all three shapes: the nested
    ``identity.BRAND_NAME`` (canonical reader), the apps/tenant ``brand.name``, and the legacy
    TOP-LEVEL ``BRAND_NAME`` (the central config). Returns "" when none is present (a "{{...}}"
    template placeholder counts as absent). PURE -- never raises."""
    if not isinstance(config, dict):
        return ""
    ident = config.get("identity")
    if isinstance(ident, dict):
        v = ident.get("BRAND_NAME")
        if v and not str(v).startswith("{{"):
            return str(v)
    brand = config.get("brand")
    if isinstance(brand, dict):
        v = brand.get("name")
        if v and not str(v).startswith("{{"):
            return str(v)
    v = config.get("BRAND_NAME")
    if v and not str(v).startswith("{{"):
        return str(v)
    return ""


def _brand_name_from_lock(lock_path) -> str:
    """Last-resort name read: the ``brand:`` line of a ``.bootstrapped`` lock, so a repo that IS
    bootstrapped (the lock exists) never reports 'unknown' even if its brand_config is malformed or
    uses an unexpected shape. PURE -- degrade-never (missing/garbled lock -> "")."""
    try:
        for line in Path(lock_path).read_text(encoding="utf-8").splitlines():
            if line.strip().lower().startswith("brand:"):
                val = line.split(":", 1)[1].strip()
                if val and val.lower() != "unknown" and not val.startswith("{{"):
                    return val
    except Exception:
        pass
    return ""


def resolve_brand_name(config, lock_path=None, fallback="unknown") -> str:
    """The single robust name resolver: the config shapes first, then the .bootstrapped lock, then
    `fallback`. A bootstrapped repo therefore never prints 'unknown' under any shipped config shape."""
    name = _brand_name_from_config(config)
    if name:
        return name
    if lock_path is not None:
        name = _brand_name_from_lock(lock_path)
        if name:
            return name
    return fallback


def _redirect_root(new_root) -> None:
    """Re-point ALL repo-relative path globals at `new_root`. Used by --root and the CWD auto-detect
    so a central checkout's cex_bootstrap can --check/--status a DIFFERENT repo (e.g. a distilled
    sovereign tenant the operator cd'd into) instead of always resolving its own script-relative root.
    BRAND_TEMPLATE is repointed too so a --root bootstrap seeds from the target repo's template."""
    global ROOT, BRAND_DIR, BRAND_CONFIG, BRAND_TEMPLATE, BRAND_LOCK, CLAUDE_MD, OSS_DEFAULTS, TENANTS_DIR
    ROOT = Path(new_root).resolve()
    BRAND_DIR = ROOT / ".cex" / "brand"
    BRAND_CONFIG = BRAND_DIR / "brand_config.yaml"
    BRAND_TEMPLATE = BRAND_DIR / "brand_config_template.yaml"
    BRAND_LOCK = BRAND_DIR / ".bootstrapped"
    CLAUDE_MD = ROOT / "CLAUDE.md"
    OSS_DEFAULTS = ROOT / ".cex" / "config" / "oss_defaults.yaml"
    TENANTS_DIR = ROOT / ".cex" / "tenants"


# ---------------------------------------------------------------------------
# Multi-tenant HYBRID isolation (p08_adr_multitenant_hybrid, decision D1)
#   SHARED: code/taxonomy/runtimes/rules (global, untouched).
#   ISOLATED per tenant_id: brand_config + runtime + memory + secrets under
#   .cex/tenants/<tid>/ . Single-tenant default (no tenant) == legacy global paths.
# ---------------------------------------------------------------------------
def _safe_tenant_id(tenant_id: str) -> str:
    """Resolution guard (isolation mechanism #3): sanitize a tenant id so a path
    can NEVER escape the tenant root. Allowed: [a-z0-9_-], 1-64 chars, leading
    alphanumeric. Rejects path separators, '..', empty -> hard fail (fail-closed)."""
    tid = (tenant_id or "").strip().lower()
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", tid):
        raise SystemExit(
            "ERROR: invalid tenant id %r -- allowed [a-z0-9_-], 1-64 chars, "
            "leading alphanumeric, no path separators or '..'" % tenant_id
        )
    return tid


def tenant_root(tenant_id: str) -> Path:
    """The HYBRID isolation root for a tenant: .cex/tenants/<tid>/ (guarded)."""
    return TENANTS_DIR / _safe_tenant_id(tenant_id)


def _activate_tenant(tenant_id: str) -> Path:
    """Redirect the brand path globals to the tenant root + scaffold the isolated
    surfaces (brand/runtime/secrets). Called once in main() so EVERY downstream
    function (is_bootstrapped, --check, --status, --reset, run_bootstrap) becomes
    tenant-scoped with no further plumbing. BRAND_TEMPLATE is intentionally NOT
    redirected -- it is the shared seed that ships with the repo."""
    global BRAND_DIR, BRAND_CONFIG, BRAND_LOCK
    root = tenant_root(tenant_id)
    BRAND_DIR = root / "brand"
    BRAND_CONFIG = BRAND_DIR / "brand_config.yaml"
    BRAND_LOCK = BRAND_DIR / ".bootstrapped"
    for sub in ("brand", "runtime", "secrets"):
        (root / sub).mkdir(parents=True, exist_ok=True)
    return root


def list_tenants() -> list:
    """All bootstrapped tenant ids under .cex/tenants/ (each has a brand/ dir)."""
    if not TENANTS_DIR.exists():
        return []
    return sorted(
        p.name for p in TENANTS_DIR.iterdir()
        if p.is_dir() and (p / "brand").exists()
    )


def _tenant_lifecycle_audit(event: str, tenant_id: str, **fields) -> None:
    """Append a destructive-lifecycle audit record to the GLOBAL append-only sink
    (.cex/runtime/signals/tenant_lifecycle.log). Teardown removes the tenant's OWN runtime,
    so the trail must live at the global orchestration level, not inside the deleted root.
    Fail-open: never raises -- an audit-write failure must not abort a teardown that was
    already authorized + confirmed (the destructive act has happened; losing the log line is
    a WARN, not a crash). One compact JSON object per line, ASCII-only."""
    import json
    rec = {"ts": datetime.now(timezone.utc).isoformat(), "event": event,
           "tenant": tenant_id, "pid": os.getpid()}
    rec.update(fields)
    try:
        sink = ROOT / ".cex" / "runtime" / "signals"
        sink.mkdir(parents=True, exist_ok=True)
        with open(sink / "tenant_lifecycle.log", "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=True, sort_keys=True) + "\n")
    except Exception as exc:  # fail-open
        print("  [teardown] WARN: lifecycle audit not written: %s" % exc, file=sys.stderr)


def _teardown_tenant(tenant_id: str, assume_yes: bool = False) -> None:
    """Deprovision a tenant: REMOVE .cex/tenants/<tid>/ in full (brand + runtime + secrets +
    memory). The destructive counterpart to --tenant provisioning -- the missing lifecycle
    half. Fail-closed + gated at every step:

      - id guard:   _safe_tenant_id rejects any traversal/escape, so rmtree can never reach
                    outside the tenants root (REUSED -- the same fail-closed guard as A2).
      - existence:  an unknown tenant is a hard error (exit 1), never a silent no-op.
      - RBAC:       when a principal/session is bound (CEX_PRINCIPAL set), teardown requires
                    the OWNER role (delete is owner-only) AND the bound tenant must match the
                    target -- a cross-tenant teardown is CRITICAL-denied + audited via
                    enforce_audited. NO principal bound == legacy default-allow (the
                    behavior-preserving invariant; single-tenant operators are unaffected).
      - confirm:    --yes proceeds; otherwise an interactive TTY must re-type the id; a
                    NON-interactive run without --yes REFUSES (exit 2) -- never delete
                    unattended. This is the 'confirm' gate the debt sweep calls for.
      - audit:      the destructive op is recorded to the append-only global lifecycle log.

    Exit codes: 0 removed; 1 unknown tenant; 2 not confirmed; SystemExit(msg) on RBAC deny."""
    tid = _safe_tenant_id(tenant_id)               # fail-closed id guard (raises on escape)
    root = tenant_root(tid)
    if not root.exists():
        print("ERROR: no such tenant %r (.cex/tenants/%s/ does not exist)" % (tid, tid),
              file=sys.stderr)
        sys.exit(1)

    # RBAC gate (owner-only delete; cross-tenant denied + audited). Deferred import keeps
    # load-time acyclic: cex_rbac / cex_rbac_audit import cex_bootstrap, never the reverse.
    try:
        from cex_rbac import active_principal, Resource
        from cex_rbac_audit import enforce_audited
        principal = active_principal()
        if principal is not None:
            # enforce_audited HALTS (SystemExit) + logs the violation on deny; allows owner.
            enforce_audited(principal, "delete", Resource(name="tenant:" + tid, tenant_id=tid))
    except ImportError:
        pass  # degrade-never: RBAC tier absent -> legacy default-allow

    # Confirmation gate (the 'confirm' in teardown-confirm). Robust against ALL
    # non-interactive stdin shapes: a non-TTY, an empty pipe, or a closed/DEVNULL stream
    # (input() -> EOFError) all REFUSE -> exit 2. We never delete unattended; only --yes or
    # an interactive operator who re-types the id may proceed.
    if not assume_yes:
        no_tty = sys.stdin is None or not sys.stdin.isatty()
        try:
            if no_tty:
                raise EOFError  # treat any non-interactive stream as 'no confirmation'
            typed = input("This DELETES tenant %r and ALL its data. Type the id to confirm: "
                          % tid)
        except EOFError:
            print("REFUSED: teardown of tenant %r needs confirmation. Re-run with --yes for "
                  "non-interactive use, or confirm from a terminal." % tid, file=sys.stderr)
            sys.exit(2)
        if typed.strip() != tid:
            print("ABORTED: confirmation %r did not match %r." % (typed.strip(), tid),
                  file=sys.stderr)
            sys.exit(2)

    # Count files for the report, then remove the whole tenant root.
    n_files = sum(1 for f in root.rglob("*") if f.is_file())
    shutil.rmtree(root)
    _tenant_lifecycle_audit("tenant_teardown", tid, files_removed=n_files,
                            confirmed=("yes-flag" if assume_yes else "interactive"))
    print("  [teardown] removed tenant %r (%d files) from %s" % (tid, n_files, root))


def load_oss_defaults() -> dict:
    """Load OSS defaults that ship with the repo.

    These are the universal, non-brand-specific values used as fallback when
    a user has not bootstrapped yet. Any field missing from the user's
    brand_config.yaml resolves through this layer before built-in defaults.
    """
    if not OSS_DEFAULTS.exists():
        return {}
    try:
        with open(OSS_DEFAULTS, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def merge_with_oss_defaults(config: dict) -> dict:
    """Overlay user brand_config on oss_defaults.yaml. User wins per key."""
    defaults = load_oss_defaults()
    if not defaults:
        return config
    # Shallow merge -- only top-level keys absent in user config get the
    # default. Nested values are user-controlled.
    merged = dict(defaults)
    for k, v in (config or {}).items():
        merged[k] = v
    return merged


def is_bootstrapped() -> bool:
    """Check if CEX instance has been bootstrapped with a real brand."""
    if not BRAND_CONFIG.exists():
        return False
    if BRAND_LOCK.exists():
        return True
    # Check if config has real values (not template placeholders), tolerant of all config shapes
    # (identity.BRAND_NAME / brand.name / top-level BRAND_NAME) so a non-canonical-but-real config
    # is still recognized as bootstrapped.
    try:
        with open(BRAND_CONFIG, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
        return bool(_brand_name_from_config(config))
    except Exception:
        return False


def count_placeholders(config: dict) -> int:
    """Count remaining {{...}} placeholders in config."""
    text = yaml.dump(config, default_flow_style=False)
    return len(re.findall(r"\{\{[A-Z_]+\}\}", text))


def count_filled(config: dict) -> int:
    """Count non-placeholder, non-empty values."""
    text = yaml.dump(config, default_flow_style=False)
    total_values = len(re.findall(r": .+", text))
    placeholders = len(re.findall(r"\{\{[A-Z_]+\}\}", text))
    return total_values - placeholders


def inject_brand_header(config: dict) -> None:
    """Inject brand identity into CLAUDE.md header."""
    if not CLAUDE_MD.exists():
        return

    content = CLAUDE_MD.read_text(encoding="utf-8")
    name = config.get("identity", {}).get("BRAND_NAME", "CEX")
    tagline = config.get("identity", {}).get("BRAND_TAGLINE", "")
    archetype = config.get("archetype", {}).get("BRAND_ARCHETYPE", "")

    # Build brand header block (f-string: substitute name/tagline/archetype/date)
    brand_block = f"""## Brand Identity (bootstrapped)

| Key | Value |
|-----|-------|
| **Brand** | {name} |
| **Tagline** | {tagline} |
| **Archetype** | {archetype} |
| **Config** | `.cex/brand/brand_config.yaml` |
| **Bootstrapped** | {datetime.now().strftime('%Y-%m-%d')} |

> All nuclei auto-inject brand context from `brand_config.yaml` into every prompt.
> To re-bootstrap: `python _tools/cex_bootstrap.py --reset`
"""

    # Insert after first heading, before "## Who Am I?"
    marker = "## Who Am I?"
    if marker in content:
        # Remove existing brand block if present
        content = re.sub(
            r"## Brand Identity \(bootstrapped\).*?(?=## Who Am I\?)",
            "",
            content,
            flags=re.DOTALL,
        )
        content = content.replace(marker, brand_block + "\n" + marker)
    else:
        # Fallback: insert after first line
        lines = content.split("\n", 2)
        if len(lines) >= 3:
            content = lines[0] + "\n" + lines[1] + "\n\n" + brand_block + "\n" + lines[2]

    CLAUDE_MD.write_text(content, encoding="utf-8")


def update_boot_titles(config: dict) -> None:
    """Update boot/*.ps1 window titles with brand name."""
    name = config.get("identity", {}).get("BRAND_NAME", "")
    if not name or name.startswith("{{"):
        return

    boot_dir = ROOT / "boot"
    for ps1_file in boot_dir.glob("*.ps1"):
        try:
            content = ps1_file.read_text(encoding="utf-8")
            # Replace sin-aware title prefix -- `$t = "N07 ...` or `$t = "N0X ...`
            content = re.sub(
                r'(\$t\s*=\s*"N0\d+ )',
                lambda m: m.group(1).replace('"N0', f'"{name} N0'),
                content,
            )
            ps1_file.write_text(content, encoding="utf-8")
        except Exception:
            continue


def bootstrap_interactive(config: dict) -> dict:
    """Interactive brand setup -- minimal questions for quick bootstrap."""
    print("\n" + "=" * 60)
    print("  CEX BOOTSTRAP -- The X is YOUR brand")
    print("=" * 60)
    print()
    print("  CEX is a generic AI brain. This bootstrap makes it YOURS.")
    print("  Answer a few questions to fill brand_config.yaml.")
    print("  For full Brand Discovery, run N06 after bootstrap.")
    print()

    identity = config.get("identity", {})
    archetype_sec = config.get("archetype", {})
    voice = config.get("voice", {})
    audience = config.get("audience", {})
    positioning = config.get("positioning", {})
    monetization = config.get("monetization", {})
    visual = config.get("visual", {})

    def ask(prompt, current="", required=True):
        default = f" [{current}]" if current and not str(current).startswith("{{") else ""
        while True:
            answer = input(f"  {prompt}{default}: ").strip()
            if not answer and current and not str(current).startswith("{{"):
                return current
            if answer:
                return answer
            if not required:
                return current
            print("    (required -- please enter a value)")

    # Phase 1: Identity (required)
    print("--- IDENTITY ---")
    identity["BRAND_NAME"] = ask("Brand/company name", identity.get("BRAND_NAME", ""))
    identity["BRAND_TAGLINE"] = ask("Tagline (10-100 chars)", identity.get("BRAND_TAGLINE", ""))
    identity["BRAND_MISSION"] = ask("Mission (why you exist)", identity.get("BRAND_MISSION", ""))

    values_raw = ask("3-5 core values (comma-separated)", ", ".join(identity.get("BRAND_VALUES", [])))
    identity["BRAND_VALUES"] = [v.strip() for v in values_raw.split(",") if v.strip()]

    # Phase 2: Archetype (required)
    print("\n--- ARCHETYPE ---")
    archetypes = "creator|hero|sage|explorer|rebel|magician|lover|caregiver|jester|ruler|innocent|everyman"
    print(f"    Options: {archetypes}")
    archetype_sec["BRAND_ARCHETYPE"] = ask("Primary archetype", archetype_sec.get("BRAND_ARCHETYPE", "")).lower()

    # Phase 3: Voice (required)
    print("\n--- VOICE ---")
    voice["BRAND_VOICE_TONE"] = ask("Voice tone (e.g. 'direct, technical, warm')", voice.get("BRAND_VOICE_TONE", ""))
    try:
        voice["BRAND_VOICE_FORMALITY"] = int(ask("Formality 1-5 (1=casual 5=formal)", str(voice.get("BRAND_VOICE_FORMALITY", 3))))
    except ValueError:
        voice["BRAND_VOICE_FORMALITY"] = 3
    voice["BRAND_LANGUAGE"] = ask("Language (e.g. pt-BR, en-US)", voice.get("BRAND_LANGUAGE", "pt-BR"), required=False)

    # Phase 4: Audience (required)
    print("\n--- AUDIENCE ---")
    audience["BRAND_ICP"] = ask("Ideal customer (20+ chars)", audience.get("BRAND_ICP", ""))
    audience["BRAND_TRANSFORMATION"] = ask("Transformation: From X to Y through Z", audience.get("BRAND_TRANSFORMATION", ""))

    # Phase 5: Positioning (required)
    print("\n--- POSITIONING ---")
    positioning["BRAND_CATEGORY"] = ask("Category (what market)", positioning.get("BRAND_CATEGORY", ""))
    positioning["BRAND_UVP"] = ask("UVP (unique value proposition, 20+ chars)", positioning.get("BRAND_UVP", ""))

    # Phase 6: Monetization (required)
    print("\n--- MONETIZATION ---")
    models = "subscription|one-time|credits|freemium|marketplace|hybrid"
    print(f"    Options: {models}")
    monetization["BRAND_PRICING_MODEL"] = ask("Pricing model", monetization.get("BRAND_PRICING_MODEL", "subscription"))
    monetization["BRAND_CURRENCY"] = ask("Currency (BRL, USD, EUR)", monetization.get("BRAND_CURRENCY", "BRL")).upper()

    # Phase 7: Visual (required -- brand_validate needs 3 HEX colors). R-285:
    # this section used to be skipped entirely, so any run starting from a
    # config without a seeded `visual` block failed validation with
    # "Missing section: visual". Degrade-never: Enter on an unset color falls
    # back to a neutral gray PLACEHOLDER hex (documented below) so the
    # produced config always validates; N06 Brand Discovery replaces them.
    print("\n--- VISUAL ---")
    print("    3 brand colors as HEX #RRGGBB. Enter accepts the [default];")
    print("    unset colors default to neutral gray PLACEHOLDERS (#333333 /")
    print("    #666666 / #999999) until N06 Brand Discovery fills the real palette.")

    hex_pattern = re.compile(r"^#[0-9a-fA-F]{6}$")

    def ask_hex(prompt, current, fallback):
        # Enter -> current when it is already a real hex, else the neutral
        # placeholder fallback. A non-empty invalid answer re-prompts (format
        # gate), mirroring ask()'s required-field re-prompt loop.
        default = current if isinstance(current, str) and hex_pattern.match(current) else fallback
        while True:
            answer = input(f"  {prompt} [{default}]: ").strip()
            if not answer:
                return default
            if hex_pattern.match(answer):
                return answer
            print("    (format: #RRGGBB hex, e.g. #1A2B3C -- Enter keeps the default)")

    colors = visual.get("BRAND_COLORS")
    if not isinstance(colors, dict):
        colors = {}
    colors["primary"] = ask_hex("Primary color", colors.get("primary"), "#333333")
    colors["secondary"] = ask_hex("Secondary color", colors.get("secondary"), "#666666")
    colors["accent"] = ask_hex("Accent color", colors.get("accent"), "#999999")
    visual["BRAND_COLORS"] = colors
    visual["BRAND_LOGO_URL"] = ask("Logo URL/path (optional)", visual.get("BRAND_LOGO_URL", ""), required=False)

    config["identity"] = identity
    config["archetype"] = archetype_sec
    config["voice"] = voice
    config["audience"] = audience
    config["positioning"] = positioning
    config["monetization"] = monetization
    config["visual"] = visual

    return config


def record_assimilation(config: dict, brain_dir: str) -> dict:
    """Wave D (Gap#5) extension: fold an assembled vertical brain INTO the brand config.

    When `/init` runs the assimilation pipeline (cex_init_pipeline.py), Stage 3 produces a
    12-pillar agent_package brain BEFORE Stage 4 (this bootstrap). This records a pointer to
    that brain in brand_config so the brand and its assimilated knowledge stay linked. Pure
    metadata + degrade-never: a missing/partial brain dir is noted, never fatal. Returns the
    assimilation block (also merged into `config`)."""
    bdir = Path(brain_dir)
    block = {
        "brain_dir": bdir.as_posix(),
        "recorded_at": datetime.now().isoformat(),
        "status": "linked" if bdir.exists() else "missing",
    }
    manifest = bdir / "manifest.yaml"
    if manifest.exists():
        try:
            from cex_shared import parse_frontmatter  # type: ignore
            fm = parse_frontmatter(manifest.read_text(encoding="utf-8")) or {}
            block["agent_package"] = fm.get("id")
            block["vertical"] = fm.get("domain")
            block["tier"] = fm.get("tier")
        except Exception:
            block["note"] = "manifest present; frontmatter not parsed"
    else:
        block["note"] = "no manifest.yaml at brain_dir (degraded: pointer only)"
    config["assimilation"] = block
    return block


def run_bootstrap(config: dict, interactive: bool = True, assimilated_brain: str = None,
                  tenant_id: str = None, manifest_axes: dict = None) -> bool:
    """Execute the full bootstrap pipeline.

    `assimilated_brain` (optional, Wave D): path to a brain produced by the assimilation
    pipeline. When given, its pointer is recorded in brand_config + the lock file so the
    brand and its assimilated knowledge are linked. Absent -> identical to the brand-only flow.

    `tenant_id` (optional, WS2 multi-tenant): when set, the brand path globals are already
    redirected to .cex/tenants/<tenant_id>/ by _activate_tenant(), and the SHARED-state
    steps (propagate to nucleus dirs, CLAUDE.md header, boot titles) are SKIPPED -- writing
    them would bleed this tenant's brand into shared code. The per-tenant brand is a runtime
    contract nuclei read via CEX_TENANT_ID, never baked into shared files.

    `manifest_axes` (optional, T6 INSTANCE MANIFEST / convergence C10): when a dict is given AND
    a tenant_id is set, ADDITIVELY write the 3-axis instance manifest+lock under the tenant root
    AFTER the brand bootstrap completes (so the brand audit_score folds into the overlay node).
    None/absent -> the manifest step is a complete no-op and bootstrap is byte-identical to
    before. The manifest is NEW state written alongside .bootstrapped, never replacing it."""
    from brand_audit import audit
    from brand_propagate import propagate
    from brand_validate import validate

    # 1. Fill config
    if interactive:
        config = bootstrap_interactive(config)

    # 1b. Fold in the assimilated brain pointer (Wave D) BEFORE the config is persisted.
    assimilation = None
    if assimilated_brain:
        assimilation = record_assimilation(config, assimilated_brain)

    # 2. Save config
    BRAND_DIR.mkdir(parents=True, exist_ok=True)
    with open(BRAND_CONFIG, "w", encoding="utf-8") as f:
        f.write("# .cex/brand/brand_config.yaml\n")
        f.write(f"# Bootstrapped: {datetime.now().isoformat()}\n")
        f.write(f"# Brand: {config.get('identity', {}).get('BRAND_NAME', 'unknown')}\n\n")
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    # 3. Validate
    result = validate(config)
    if not result["valid"]:
        print(f"\n  WARNING: Validation found {len(result['errors'])} errors:")
        for e in result["errors"][:5]:
            print(f"    - {e}")
        print("  Config saved but may need fixes. Run N06 Brand Discovery for full setup.")
    else:
        print(f"\n  OK: Validation passed ({result['required_fields_filled']}/13 required fields)")

    # 4-6. SHARED-state mutations -- ONLY in single-tenant (global) mode. In tenant
    # mode these would bleed one tenant's brand into shared code (nucleus dirs,
    # CLAUDE.md, boot scripts), violating the isolation invariant.
    if tenant_id is None:
        # 4. Propagate
        prop_results = propagate(config, dry_run=False)
        propagated = [n for n, r in prop_results.items() if r["status"] == "propagated"]
        print(f"  OK: Brand propagated to {len(propagated)} nuclei: {', '.join(propagated)}")

        # 5. Inject into CLAUDE.md
        inject_brand_header(config)
        print("  OK: CLAUDE.md updated with brand identity")

        # 6. Update boot titles
        update_boot_titles(config)
        print("  OK: Boot scripts updated with brand name")
    else:
        print(f"  TENANT[{tenant_id}]: shared-state propagation SKIPPED "
              "(per-tenant brand is a runtime contract; zero cross-tenant/global bleed)")

    # 7. Audit
    audit_result = audit(config)
    print(f"  OK: Brand audit score: {audit_result['overall_score']:.3f} ({audit_result['rating']})")

    # 8. Write lock file (records the assimilated brain pointer when present)
    lock_text = (
        f"bootstrapped: {datetime.now().isoformat()}\n"
        f"brand: {config.get('identity', {}).get('BRAND_NAME', '')}\n"
        f"audit_score: {audit_result['overall_score']}\n"
    )
    if assimilation:
        lock_text += (
            f"assimilated_brain: {assimilation['brain_dir']}\n"
            f"assimilation_status: {assimilation['status']}\n"
        )
    BRAND_LOCK.write_text(lock_text, encoding="utf-8")
    if assimilation:
        print(f"  OK: Assimilated brain linked ({assimilation['status']}): {assimilation['brain_dir']}")

    # 9. T6 INSTANCE MANIFEST (ADDITIVE -- convergence C10). ONLY when manifest axes were
    #    supplied AND a tenant is active. This writes NEW state (.cex/tenants/<tid>/instance.yaml
    #    + instance.lock) ALONGSIDE .bootstrapped -- it never touches .bootstrapped, brand_config,
    #    or any shared file. Omitting manifest_axes => this whole block is skipped => bootstrap is
    #    byte-identical to before. The bind binds 3 axes: framework + tenant_overlay + fabric.
    if manifest_axes and tenant_id is not None:
        try:
            from cex_instance_manifest import write_instance_manifest
            _m, _l = write_instance_manifest(
                tenant_id,
                framework_version=manifest_axes.get("framework_version"),
                tenant_overlay_ref=manifest_axes.get("tenant_overlay_ref"),
                fabric_endpoint=manifest_axes.get("fabric_endpoint"),
                brand_audit_score=audit_result.get("overall_score"),
            )
            fwv = _l["lock"]["nodes"]["framework"]["resolved_version"]
            fab_on = _l["lock"]["nodes"]["fabric_endpoint"].get("enabled", False)
            print("  OK: Instance manifest bound (framework@%s + tenant_overlay[%s] + fabric=%s); "
                  "lock status=%s" % (fwv, tenant_id, "on" if fab_on else "off",
                                      _l["lock"]["status"]))
        except Exception as exc:
            # Fail-LOUD but NON-FATAL to the brand bootstrap: the brand bind already succeeded
            # and was committed above; an incompatible/failed manifest must not unwind it. The
            # operator re-binds with corrected axes (the manifest is additive, retry-safe).
            print("  WARN: instance manifest NOT bound: %s" % exc, file=sys.stderr)

    brand_name = config.get("identity", {}).get("BRAND_NAME", "CEX")
    print("\n  BOOTSTRAP COMPLETE")
    print(f"  CEX is now the brain of: {brand_name}")
    print("  For full Brand Discovery: boot/n06.ps1")
    print("  To re-bootstrap: python _tools/cex_bootstrap.py --reset")
    return True


# ---------------------------------------------------------------------------
# Re-exports: the canonical repo-wide tenant resolvers live in cex_tenant_paths
# (the ONE source of truth -- closes the A3 resolution-guard + secret gaps). They
# are surfaced here too so a caller already holding cex_bootstrap keeps one import.
# The import is DEFERRED (function body, not module top) so cex_bootstrap and
# cex_tenant_paths stay acyclic: cex_tenant_paths imports _safe_tenant_id FROM this
# module at load time; this module never imports it at load time.
# ---------------------------------------------------------------------------
def resolve_tenant_path(*parts, **kwargs):
    """Re-export -> cex_tenant_paths.resolve_tenant_path (the repo-wide path guard)."""
    from cex_tenant_paths import resolve_tenant_path as _impl
    return _impl(*parts, **kwargs)


def load_tenant_secrets(*args, **kwargs):
    """Re-export -> cex_tenant_paths.load_tenant_secrets (per-tenant .env loader)."""
    from cex_tenant_paths import load_tenant_secrets as _impl
    return _impl(*args, **kwargs)


# RBAC enforcement tier (principal/session/role matrix) lives in cex_rbac. Re-exported
# here -- same deferred-import discipline -- so a caller holding cex_bootstrap keeps one
# import for the whole tenant+RBAC surface. cex_rbac imports FROM cex_tenant_paths (which
# imports _safe_tenant_id from this module), so the deferred body keeps the graph acyclic.
def authorize(*args, **kwargs):
    """Re-export -> cex_rbac.authorize (deny-by-default role-matrix predicate)."""
    from cex_rbac import authorize as _impl
    return _impl(*args, **kwargs)


def active_principal(*args, **kwargs):
    """Re-export -> cex_rbac.active_principal (the session model: CEX_PRINCIPAL/CEX_ROLE)."""
    from cex_rbac import active_principal as _impl
    return _impl(*args, **kwargs)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="CEX Bootstrap -- fill the X with YOUR brand")
    parser.add_argument("--check", action="store_true", help="Check if bootstrapped")
    parser.add_argument("--from-file", help="Non-interactive: load brand values from YAML file")
    parser.add_argument("--reset", action="store_true", help="Clear brand and re-bootstrap")
    parser.add_argument("--status", action="store_true", help="Show current brand status")
    parser.add_argument("--assimilated-brain", dest="assimilated_brain",
                        help="Path to an assembled vertical brain (cex_init_pipeline.py Stage 3) "
                             "to link into the brand config + lock (assimilation -> bootstrap)")
    parser.add_argument("--root", help="Operate on the CEX/distilled repo at this path instead of "
                        "the script-relative root. For --check/--status, the current working "
                        "directory is auto-detected when it is itself a CEX repo (a sovereign tenant "
                        "the operator cd'd into), so the brand reported is that repo's -- never the "
                        "factory's, never 'unknown'.")
    parser.add_argument("--tenant", help="Operate on tenant <id> (HYBRID isolation under "
                        ".cex/tenants/<id>/). Default: CEX_TENANT_ID env, else single-tenant global.")
    parser.add_argument("--list-tenants", action="store_true",
                        help="List bootstrapped tenants and exit")
    parser.add_argument("--teardown", metavar="TID",
                        help="Deprovision (DELETE) tenant <id>: remove .cex/tenants/<id>/ in "
                             "full. Destructive + gated -- needs --yes (or an interactive "
                             "confirm) and, when a principal is bound, the owner role.")
    parser.add_argument("--yes", action="store_true",
                        help="Skip the interactive confirmation for --teardown (for "
                             "non-interactive/automation use).")
    # T6 INSTANCE MANIFEST (additive): bind the 3-axis manifest+lock alongside the brand
    # bootstrap. ALL optional -- omitting every axis flag leaves bootstrap byte-identical.
    parser.add_argument("--bind-manifest", action="store_true",
                        help="ALSO write the T6 instance manifest+lock (3 axes: framework + "
                             "tenant_overlay + fabric_endpoint) under the tenant root. Additive; "
                             "needs --tenant (or CEX_TENANT_ID). Auto-on when any axis flag below "
                             "is supplied.")
    parser.add_argument("--framework-version",
                        help="Axis 1 override (default: archetypes/VERSION.yaml::cex_version).")
    parser.add_argument("--overlay-version",
                        help="Axis 2: the tenant_overlay package version (default 0.1.0).")
    parser.add_argument("--fabric-endpoint",
                        help="Axis 3: the vendor_fabric fabric base_url (OpenAI-compat :8080). "
                             "Supplying it enables the fabric axis.")
    parser.add_argument("--fabric-contract-version",
                        help="Axis 3: the cex-fabric contract version to bind (required when "
                             "--fabric-endpoint is given).")
    parser.add_argument("--manifest-status", metavar="TID",
                        help="Print the drift report for tenant <TID>'s instance lock and exit "
                             "(read-only: not_bound | no_drift | drift_detected | incompatible).")
    args = parser.parse_args()

    if args.list_tenants:
        tenants = list_tenants()
        if tenants:
            # Optional manifest-bound column (degrade-never: if the manifest module is
            # unavailable, fall back to the plain list -- never break --list-tenants).
            try:
                from cex_instance_manifest import is_manifest_bound
            except Exception:
                is_manifest_bound = None
            print("Tenants (%d):" % len(tenants))
            for t in tenants:
                tag = ""
                if is_manifest_bound is not None:
                    tag = " [manifest-bound]" if is_manifest_bound(t) else " [brand-only]"
                print("  - %s%s" % (t, tag))
        else:
            print("No tenants bootstrapped (.cex/tenants/ empty). Single-tenant (global) mode.")
        sys.exit(0)

    if args.manifest_status:
        # Read-only drift report for a tenant's instance lock (Part B boot-time re-check). Runs
        # before tenant activation (target is named explicitly), parallel to --list-tenants.
        from cex_instance_manifest import verify_instance_lock
        tid = _safe_tenant_id(args.manifest_status)
        report = verify_instance_lock(tid)
        print("Instance manifest status for tenant %r: %s" % (tid, report["status"]))
        if report["status"] == "not_bound":
            print("  (no instance.yaml/instance.lock -- tenant is brand-bootstrapped only)")
        for d in report.get("drift", []):
            print("  DRIFT: axis=%s locked=%s current=%s"
                  % (d["axis"], d["locked_hash"], d["current_hash"]))
        for r in report.get("reasons", []):
            print("  INCOMPATIBLE: %s" % r)
        # fail-closed exit: incompatible -> 2, drift -> 3, clean/not_bound -> 0
        sys.exit(2 if report["incompatible"] else (3 if report["drifted"] else 0))

    if args.teardown:
        # Deprovision an explicit target tenant. Independent of --tenant/CEX_TENANT_ID (which
        # select the tenant to OPERATE WITHIN); teardown's target is named explicitly. Runs
        # BEFORE active-tenant activation so we never scaffold a tenant we are about to delete.
        _teardown_tenant(args.teardown, assume_yes=args.yes)
        sys.exit(0)

    # Root resolution (BEFORE tenant activation). An explicit --root always wins. For the READ-ONLY
    # status checks (--check / --status), additionally be CWD-AWARE: when NOT operating on a tenant
    # and the current working directory is itself a CEX/distilled repo (it has .cex/brand/) DISTINCT
    # from this script's root, report THAT repo's brand. This is what lets
    #   cd <distilled-tenant> && python <central>/_tools/cex_bootstrap.py --check
    # report the tenant's brand (never the factory's, never 'unknown'). Mutating commands keep the
    # script-relative root unless --root is given explicitly.
    _explicit_tenant = bool(args.tenant or os.environ.get("CEX_TENANT_ID"))
    if args.root:
        _redirect_root(args.root)
    elif (args.check or args.status) and not _explicit_tenant:
        _cwd = Path.cwd()
        _cwd_brand = _cwd / ".cex" / "brand"
        if (_cwd.resolve() != ROOT.resolve() and _cwd_brand.is_dir()
                and ((_cwd_brand / "brand_config.yaml").exists()
                     or (_cwd_brand / ".bootstrapped").exists())):
            _redirect_root(_cwd)

    # Resolve the active tenant: --tenant arg > CEX_TENANT_ID env > None (single-tenant global).
    # When set, redirect the brand path globals so ALL branches below are tenant-scoped.
    active_tenant = args.tenant or os.environ.get("CEX_TENANT_ID")
    if active_tenant:
        active_tenant = _safe_tenant_id(active_tenant)
        _activate_tenant(active_tenant)
        # stderr so we never pollute --check/--status stdout that hooks parse
        print("  [tenant] active: %s -> %s" % (active_tenant, BRAND_CONFIG.parent),
              file=sys.stderr)

    if args.check:
        if is_bootstrapped():
            try:
                with open(BRAND_CONFIG, "r", encoding="utf-8") as f:
                    c = yaml.safe_load(f) or {}
            except Exception:
                c = {}
            # Shape-tolerant + lock-backed: a bootstrapped repo never reports 'unknown'.
            name = resolve_brand_name(c, BRAND_LOCK)
            print(f"BOOTSTRAPPED: {name}")
            sys.exit(0)
        else:
            print("NOT BOOTSTRAPPED: run python _tools/cex_bootstrap.py")
            sys.exit(1)

    if args.status:
        if not BRAND_CONFIG.exists():
            print("Status: NOT BOOTSTRAPPED")
            print("  Run: python _tools/cex_bootstrap.py")
            sys.exit(0)
        with open(BRAND_CONFIG, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
        filled = count_filled(config)
        placeholders = count_placeholders(config)
        name = resolve_brand_name(config, BRAND_LOCK)
        print(f"Status: {'BOOTSTRAPPED' if is_bootstrapped() else 'PARTIAL'}")
        print(f"  Brand: {name}")
        print(f"  Filled values: {filled}")
        print(f"  Placeholders remaining: {placeholders}")
        if BRAND_LOCK.exists():
            print(f"  Lock: {BRAND_LOCK.read_text(encoding='utf-8').strip()}")
        sys.exit(0)

    if args.reset:
        if BRAND_LOCK.exists():
            BRAND_LOCK.unlink()
        if BRAND_CONFIG.exists():
            backup = BRAND_CONFIG.with_suffix(".yaml.bak")
            shutil.copy2(BRAND_CONFIG, backup)
            print(f"  Backup saved: {backup}")
        # Copy template back
        if BRAND_TEMPLATE.exists():
            shutil.copy2(BRAND_TEMPLATE, BRAND_CONFIG)
        print("  Brand reset. Run bootstrap again.")
        sys.exit(0)

    # Assemble the optional T6 manifest axes from CLI flags (additive). The manifest binds
    # ONLY when --bind-manifest is set OR any axis flag is supplied, AND a tenant is active.
    # When nothing is supplied, manifest_axes stays None -> the manifest step is a no-op and
    # bootstrap is byte-identical to before.
    manifest_axes = None
    want_manifest = bool(args.bind_manifest or args.framework_version or args.overlay_version
                         or args.fabric_endpoint or args.fabric_contract_version)
    if want_manifest:
        if not active_tenant:
            print("ERROR: --bind-manifest / axis flags require --tenant <id> (or CEX_TENANT_ID). "
                  "The instance manifest is bound under a tenant root.", file=sys.stderr)
            sys.exit(1)
        manifest_axes = {
            "framework_version": args.framework_version,   # None -> deterministic repo source
            "tenant_overlay_ref": args.overlay_version,     # None -> default overlay version
            "fabric_endpoint": (
                {"enabled": True, "base_url": args.fabric_endpoint,
                 "contract_version": args.fabric_contract_version}
                if args.fabric_endpoint else None),         # None -> fabric disabled (local-only)
        }

    # Load existing config or template
    if args.from_file:
        with open(args.from_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
        run_bootstrap(config, interactive=False, assimilated_brain=args.assimilated_brain,
                      tenant_id=active_tenant, manifest_axes=manifest_axes)
    else:
        if BRAND_CONFIG.exists():
            with open(BRAND_CONFIG, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
        elif BRAND_TEMPLATE.exists():
            with open(BRAND_TEMPLATE, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
        else:
            config = {}
        run_bootstrap(config, interactive=True, assimilated_brain=args.assimilated_brain,
                      tenant_id=active_tenant, manifest_axes=manifest_axes)


if __name__ == "__main__":
    try:
        from cex_agent_io import wrap_main

        def _main_wrapper(argv):
            sys.argv = [sys.argv[0]] + argv
            main()
            return 0

        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_bootstrap"))
    except ImportError:
        main()
