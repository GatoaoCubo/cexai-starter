# -*- coding: utf-8 -*-
"""cex_rls_drift_check.py -- RLS drift-check + live-RLS linter (mission MULTITENANT_DATA_PLANE, T4).

Operationalizes spec_multitenant_data_plane_v1.md section C.2 (drift-check logic +
the exact catalog queries) and C.3 (CI gate). It compares the DECLARED schema
(parsed from supabase/migrations/*.sql) against a LIVE catalog snapshot and FAILS
(exit 1) on any divergence -- doubling as a linter for the tenant-isolation bypass
class found live on 2026-06-16 (the `produtos` bug: a PERMISSIVE "Service role full
access" USING(true) policy on role public OR-combined with -- and so nullified --
the correct RESTRICTIVE tenant-boundary policy).

WHAT IT CHECKS (C.2 FAIL conditions, spec lines 483-491):
  - a LIVE table absent from DECLARED            -> Dashboard-applied drift
  - a DECLARED table absent from LIVE            -> un-pushed migration
  - a tenant table with rls=false (ENABLE)      -> AR4 (rows globally readable)
  - a tenant DATA table with FORCE RLS missing   -> AR4 FORCE (owner-bypass: ENABLE
    alone exempts the table OWNER; FORCE makes the boundary apply to the owner too).
    Checked DECLARED-side (relrowsecurity column had no FORCE: flag tenant_scoped AND
    NOT forced) AND LIVE-side (relforcerowsecurity=false). The repo convention is
    ENABLE + FORCE on every tenant table. EXEMPT: storage.objects -- a platform-owned
    catalog table the tenant role never owns, so FORCE is moot there.
  - storage.objects with relrowsecurity=false on the LIVE snapshot -> AR_STORAGE
    (the tenant_boundary prefix-match policy is INERT -> every tenant's FT objects
    globally readable). Dedicated check: storage.objects is in the `storage` schema,
    which the public-scoped LIVE_TABLES_SQL does not return, so it applies only when
    the snapshot explicitly carries a storage.objects row (absent => SKIP, never a
    false PASS).
  - any policy PERMISSIVE on role public/authenticated with qual='true'
                                                 -> AR1 (the produtos bug -- a 2nd
                                                    permissive USING(true) OR-grants)
  - a tenant table with NO permissive policy for public/authenticated (only
    RESTRICTIVE policies) -> AR2 (the RESTRICTIVE-only 0-rows trap: in PG RLS a row
    is visible iff (>=1 PERMISSIVE passes) AND (all RESTRICTIVE pass); with NO
    permissive grant the boundary denies EVERY row, even the caller's own tenant.
    Proven on live `produtos` 2026-06-16: a SINGLE PERMISSIVE tenant-match policy
    isolates correctly. The boundary must be a PERMISSIVE tenant-match, NOT
    RESTRICTIVE-only.)
  - a write-capable policy (FOR ALL/INSERT/UPDATE) lacking with_check
                                                 -> AR3

USAGE:
    # CI mode -- no DB needed; feed a catalog snapshot as JSON (file or stdin):
    python _tools/cex_rls_drift_check.py --live-json snapshot.json
    cat snapshot.json | python _tools/cex_rls_drift_check.py --live-json -

    # point at a non-default migrations dir:
    python _tools/cex_rls_drift_check.py --migrations supabase/migrations --live-json snap.json

    # self-test (no DB, no files): proves the detectors flag the produtos-style AR1
    # pair, the AR2 0-rows trap, an AR4 FORCE-missing tenant table, and a storage.objects
    # with RLS off (AR_STORAGE):
    python _tools/cex_rls_drift_check.py --self-test

    # OPTIONAL live fetch via the Supabase Management API (NOT exercised in T4 build;
    # requests is lazily imported only inside this path):
    #   SUPABASE_ACCESS_TOKEN=sbp_... \
    #   python _tools/cex_rls_drift_check.py --migrations supabase/migrations \
    #       --supabase-ref <project_ref>

LIVE-JSON SNAPSHOT SHAPE (what --live-json expects; what the Management API yields):
    {
      "tables":   [{"name": "tenant_memory", "rls": true, "forced": true}, ...],
      "policies": [{"table": "tenant_memory", "name": "...", "permissive": "RESTRICTIVE",
                    "roles": ["authenticated"], "cmd": "SELECT",
                    "qual": "...", "with_check": null}, ...]
    }
  - `rls`: pg_class.relrowsecurity (ENABLE); also accepts key 'relrowsecurity'.
  - `forced` (optional): pg_class.relforcerowsecurity (FORCE); also accepts key
     'relforcerowsecurity'. Absent => treated as false (FORCE not asserted). To
     check storage.objects RLS, include a "storage.objects" row in `tables`.
  - `permissive`: "PERMISSIVE" | "RESTRICTIVE" (pg_policies.permissive text); also
     accepts a bool (true=PERMISSIVE) for hand-written snapshots.
  - `roles`: list (pg_policies.roles array) OR a brace string "{public}".
  - `qual` / `with_check`: SQL expression text, or null.

ASCII-only per .claude/rules/ascii-code-rule.md. stdlib only (requests/psycopg are
optional + lazily imported and are NOT touched by --self-test or --live-json).
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MIGRATIONS = ROOT / "supabase" / "migrations"

# Roles that, when a PERMISSIVE USING(true) policy targets them on a tenant table,
# create the produtos bypass (AR1). service_role is the SANCTIONED escape (B.2 step 3).
BROAD_ROLES = {"public", "authenticated"}

# cmd values that imply a write capability (need WITH CHECK -- AR3).
WRITE_CMDS = {"ALL", "INSERT", "UPDATE"}

# The platform-owned Storage catalog table (storage.objects). The DECLARED-side
# parser strips the schema qualifier, so it appears as 'objects'. The live catalog
# query (LIVE_TABLES_SQL) scopes to the public schema and so does NOT return
# storage.objects -- the live storage-RLS AR check reads it from a 'storage.objects'
# OR 'objects' entry the snapshot author supplied (a Supabase live fetch must add a
# storage-schema row for this check to apply; absent => the check is skipped, never
# a false PASS). FORCE is intentionally moot for this table (tenant role is never
# its owner), so it is exempt from the FORCE assertion.
STORAGE_OBJECTS_NAMES = {"storage.objects", "objects"}


# =========================================================================== #
# (1) DECLARED-SIDE PARSER -- supabase/migrations/*.sql                        #
# --------------------------------------------------------------------------- #
# A pragmatic line/regex parser for the forms this repo emits (spec B.2):      #
#   CREATE TABLE [IF NOT EXISTS] <t> ( ... tenant_id ... );                    #
#   ALTER TABLE <t> ENABLE  ROW LEVEL SECURITY;                                #
#   ALTER TABLE <t> FORCE   ROW LEVEL SECURITY;                                #
#   CREATE POLICY <p> ON <t> [AS RESTRICTIVE|PERMISSIVE] FOR <cmd>             #
#       TO <roles> USING (<qual>) [WITH CHECK (<check>)];                      #
# Not a full SQL grammar -- deliberately tolerant; comments + strings stripped #
# enough to find the statement keywords reliably.                              #
# =========================================================================== #

_IDENT = r'(?:"[^"]+"|[A-Za-z_][A-Za-z0-9_$]*)'
_QUALIFIED = rf'(?:{_IDENT}\.)?{_IDENT}'


def _unquote_ident(tok):
    """Normalize a SQL identifier: strip double-quotes + any schema qualifier,
    lowercase an unquoted name (Postgres folds unquoted idents to lowercase)."""
    tok = tok.strip()
    if "." in tok and not tok.startswith('"'):
        # take the last dotted segment (table name), drop schema qualifier
        tok = tok.split(".")[-1]
    if tok.startswith('"') and tok.endswith('"'):
        return tok[1:-1]
    return tok.lower()


def _strip_sql_comments(sql):
    """Remove -- line comments and /* */ block comments so keyword scans are clean.
    String literals are left intact (we only key off SQL keywords, not literals)."""
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    out_lines = []
    for line in sql.splitlines():
        # drop a -- comment, but not inside a single-quoted string
        in_str = False
        cut = None
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == "'":
                in_str = not in_str
            elif ch == "-" and i + 1 < len(line) and line[i + 1] == "-" and not in_str:
                cut = i
                break
            i += 1
        out_lines.append(line if cut is None else line[:cut])
    return "\n".join(out_lines)


def _split_statements(sql):
    """Split on semicolons that are NOT inside single-quoted strings or
    dollar-quoted blocks ($$ ... $$ / $tag$ ... $tag$). Good enough for the
    migration forms here (which include SECURITY DEFINER function bodies)."""
    stmts = []
    buf = []
    i = 0
    n = len(sql)
    in_str = False
    dollar_tag = None
    while i < n:
        ch = sql[i]
        if dollar_tag is not None:
            buf.append(ch)
            if sql.startswith(dollar_tag, i):
                buf.append(sql[i + 1:i + len(dollar_tag)])
                i += len(dollar_tag)
                dollar_tag = None
            i += 1
            continue
        if in_str:
            buf.append(ch)
            if ch == "'":
                in_str = False
            i += 1
            continue
        if ch == "'":
            in_str = True
            buf.append(ch)
            i += 1
            continue
        m = re.match(r"\$[A-Za-z0-9_]*\$", sql[i:])
        if m:
            dollar_tag = m.group(0)
            buf.append(dollar_tag)
            i += len(dollar_tag)
            continue
        if ch == ";":
            stmts.append("".join(buf))
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    if "".join(buf).strip():
        stmts.append("".join(buf))
    return stmts


def _find_balanced(text, start):
    """Given text and the index of an opening '(', return (inner, end_index_after_close).
    Tracks single-quoted strings so parens inside literals do not unbalance."""
    assert text[start] == "("
    depth = 0
    in_str = False
    i = start
    while i < len(text):
        ch = text[i]
        if in_str:
            if ch == "'":
                in_str = False
        elif ch == "'":
            in_str = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return text[start + 1:i], i + 1
        i += 1
    return text[start + 1:], len(text)  # unbalanced -- return what we have


def _normalize_expr(expr):
    """Collapse whitespace in a USING/WITH CHECK expression to a single line so
    qual comparisons (e.g. detecting the literal 'true') are stable."""
    if expr is None:
        return None
    return re.sub(r"\s+", " ", expr).strip()


def _is_true_qual(qual):
    """True iff the qual expression is the unconditional literal `true` -- the
    AR1 fingerprint. Tolerates wrapping parens / whitespace / case."""
    if qual is None:
        return False
    q = _normalize_expr(qual)
    while q.startswith("(") and q.endswith(")"):
        q = q[1:-1].strip()
    return q.lower() == "true"


def _parse_roles(clause):
    """Parse a `TO a, b, c` role list (declared SQL side) into a lowercased list."""
    roles = [r.strip().lower() for r in clause.split(",") if r.strip()]
    return [_unquote_ident(r) for r in roles]


def parse_create_table(stmt):
    """Return (table_name, has_tenant_id) for a CREATE TABLE stmt, else None."""
    m = re.match(
        rf"\s*CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?({_QUALIFIED})\s*\(",
        stmt, flags=re.IGNORECASE)
    if not m:
        return None
    table = _unquote_ident(m.group(1))
    paren_start = stmt.index("(", m.end() - 1)
    body, _ = _find_balanced(stmt, paren_start)
    # a column line beginning with tenant_id (optionally quoted) => tenant-scoped
    has_tenant = bool(re.search(r'(^|,)\s*"?tenant_id"?\s', body, flags=re.IGNORECASE))
    return table, has_tenant


def parse_alter_rls(stmt):
    """Return (table, mode) where mode in {'enable','force'} for
    ALTER TABLE ... ENABLE|FORCE ROW LEVEL SECURITY, else None."""
    m = re.match(
        rf"\s*ALTER\s+TABLE\s+(?:IF\s+EXISTS\s+)?(?:ONLY\s+)?({_QUALIFIED})\s+"
        r"(ENABLE|FORCE)\s+ROW\s+LEVEL\s+SECURITY",
        stmt, flags=re.IGNORECASE)
    if not m:
        return None
    return _unquote_ident(m.group(1)), m.group(2).lower()


def parse_create_policy(stmt):
    """Parse CREATE POLICY into a dict {name, table, permissive, roles, cmd, qual,
    with_check}; return None if not a CREATE POLICY. `permissive` is 'PERMISSIVE'
    or 'RESTRICTIVE' (PG default when AS is omitted is PERMISSIVE)."""
    m = re.match(
        rf"\s*CREATE\s+POLICY\s+({_IDENT})\s+ON\s+({_QUALIFIED})\b",
        stmt, flags=re.IGNORECASE)
    if not m:
        return None
    name = _unquote_ident(m.group(1))
    table = _unquote_ident(m.group(2))
    rest = stmt[m.end():]

    # AS RESTRICTIVE | PERMISSIVE (default PERMISSIVE)
    permissive = "PERMISSIVE"
    am = re.search(r"\bAS\s+(RESTRICTIVE|PERMISSIVE)\b", rest, flags=re.IGNORECASE)
    if am:
        permissive = am.group(1).upper()

    # FOR <cmd> (default ALL)
    cmd = "ALL"
    cm = re.search(r"\bFOR\s+(ALL|SELECT|INSERT|UPDATE|DELETE)\b", rest, flags=re.IGNORECASE)
    if cm:
        cmd = cm.group(1).upper()

    # TO <role list> -- up to the next clause keyword
    roles = []
    tm = re.search(r"\bTO\s+(.+?)(?:\bUSING\b|\bWITH\s+CHECK\b|\bFOR\b|\bAS\b|$)",
                   rest, flags=re.IGNORECASE | re.DOTALL)
    if tm:
        roles = _parse_roles(tm.group(1))

    # USING ( ... )
    qual = None
    um = re.search(r"\bUSING\b", rest, flags=re.IGNORECASE)
    if um:
        p = rest.find("(", um.end())
        if p != -1:
            inner, _ = _find_balanced(rest, p)
            qual = _normalize_expr(inner)

    # WITH CHECK ( ... )
    with_check = None
    wm = re.search(r"\bWITH\s+CHECK\b", rest, flags=re.IGNORECASE)
    if wm:
        p = rest.find("(", wm.end())
        if p != -1:
            inner, _ = _find_balanced(rest, p)
            with_check = _normalize_expr(inner)

    return {
        "name": name, "table": table, "permissive": permissive,
        "roles": roles, "cmd": cmd, "qual": qual, "with_check": with_check,
    }


def parse_migrations(migrations_dir):
    """Parse every *.sql under migrations_dir into:
        {table -> {rls_enabled, forced, tenant_scoped, policies:[...]}}
    Returns ({}, []) gracefully if the dir is absent (W2 has not built T2 yet)."""
    declared = {}
    warnings = []
    mdir = Path(migrations_dir)
    if not mdir.exists():
        warnings.append(f"migrations dir not found: {mdir} (no declared schema parsed)")
        return declared, warnings

    files = sorted(mdir.glob("*.sql"))
    if not files:
        warnings.append(f"no *.sql files in {mdir}")

    def _ensure(t):
        return declared.setdefault(t, {
            "rls_enabled": False, "forced": False,
            "tenant_scoped": False, "policies": [],
        })

    for f in files:
        try:
            raw = f.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            warnings.append(f"could not read {f}: {exc}")
            continue
        clean = _strip_sql_comments(raw)
        for stmt in _split_statements(clean):
            s = stmt.strip()
            if not s:
                continue
            head = s[:13].upper()
            if head.startswith("CREATE TABLE"):
                res = parse_create_table(s)
                if res:
                    table, has_tenant = res
                    rec = _ensure(table)
                    if has_tenant:
                        rec["tenant_scoped"] = True
            elif head.startswith("ALTER TABLE"):
                res = parse_alter_rls(s)
                if res:
                    table, mode = res
                    rec = _ensure(table)
                    if mode == "enable":
                        rec["rls_enabled"] = True
                    elif mode == "force":
                        rec["forced"] = True
                        rec["rls_enabled"] = True  # FORCE implies enabled
            elif head.startswith("CREATE POLIC"):
                pol = parse_create_policy(s)
                if pol:
                    rec = _ensure(pol["table"])
                    rec["policies"].append(pol)
    return declared, warnings


# =========================================================================== #
# (2) LIVE-SIDE SNAPSHOT -- JSON in, normalized out                           #
# =========================================================================== #

def _coerce_roles(roles):
    """Accept a list (pg_policies.roles array) OR a brace string '{public,...}'."""
    if roles is None:
        return []
    if isinstance(roles, str):
        roles = roles.strip().lstrip("{").rstrip("}")
        roles = [r for r in roles.split(",") if r.strip()]
    return [str(r).strip().strip('"').lower() for r in roles if str(r).strip()]


def _coerce_permissive(val):
    """pg_policies.permissive is text 'PERMISSIVE'/'RESTRICTIVE'; also accept bool."""
    if isinstance(val, bool):
        return "PERMISSIVE" if val else "RESTRICTIVE"
    if val is None:
        return "PERMISSIVE"  # PG default
    return str(val).strip().upper()


def normalize_live(snapshot):
    """Normalize a raw snapshot dict into:
        ({table_lower -> rls_bool}, {table_lower -> forced_bool}, [policy_dict, ...])
    Each policy_dict: {table, name, permissive, roles, cmd, qual, with_check}.
    `forced` mirrors pg_class.relforcerowsecurity (accepts key 'forced' or
    'relforcerowsecurity'); absent => False (FORCE not asserted on the snapshot)."""
    tables = {}
    forced = {}
    for t in snapshot.get("tables", []) or []:
        name = _unquote_ident(str(t.get("name", "")).strip())
        if not name:
            continue
        tables[name] = bool(t.get("rls", t.get("relrowsecurity", False)))
        forced[name] = bool(t.get("forced", t.get("relforcerowsecurity", False)))

    policies = []
    for p in snapshot.get("policies", []) or []:
        table = _unquote_ident(str(p.get("table", p.get("tablename", ""))).strip())
        if not table:
            continue
        policies.append({
            "table": table,
            "name": str(p.get("name", p.get("policyname", "")) or "").strip(),
            "permissive": _coerce_permissive(p.get("permissive")),
            "roles": _coerce_roles(p.get("roles")),
            "cmd": str(p.get("cmd", "ALL") or "ALL").strip().upper(),
            "qual": p.get("qual"),
            "with_check": p.get("with_check", p.get("check")),
        })
    return tables, forced, policies


def load_live_json(arg):
    """Read the snapshot JSON from a file path, or stdin when arg == '-'."""
    if arg == "-":
        data = sys.stdin.read()
    else:
        data = Path(arg).read_text(encoding="utf-8")
    return json.loads(data)


# --- OPTIONAL Management API fetch (lazy; NOT called in the T4 build) -------- #
# The exact catalog queries are C.2 (spec lines 479-482).
LIVE_TABLES_SQL = (
    "SELECT relname AS name, relrowsecurity AS rls, "
    "relforcerowsecurity AS forced FROM pg_class "
    "WHERE relnamespace = 'public'::regnamespace AND relkind = 'r';"
)
LIVE_POLICIES_SQL = (
    "SELECT tablename AS table, policyname AS name, permissive, roles, cmd, "
    "qual, with_check FROM pg_policies WHERE schemaname = 'public';"
)


def fetch_live_via_management_api(project_ref, token=None, timeout=60):
    """Fetch a live catalog snapshot via the Supabase Management API query endpoint
    (POST /v1/projects/{ref}/database/query). `requests` is imported HERE, lazily, so
    the tool's default/CI/self-test paths stay stdlib-only. Token from arg or
    SUPABASE_ACCESS_TOKEN. This is provided for completeness and is NOT exercised in
    the T4 build (the constraints forbid touching a live DB)."""
    import requests  # lazy -- only on this path

    token = token or os.environ.get("SUPABASE_ACCESS_TOKEN") or os.environ.get("SUPABASE_PAT")
    if not token:
        raise RuntimeError("no Supabase token (set SUPABASE_ACCESS_TOKEN)")
    base = f"https://api.supabase.com/v1/projects/{project_ref}/database/query"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def _query(sql):
        resp = requests.post(base, headers=headers, json={"query": sql}, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    return {"tables": _query(LIVE_TABLES_SQL), "policies": _query(LIVE_POLICIES_SQL)}


# =========================================================================== #
# (3) COMPARE -- the FAIL conditions (C.2 + AR1-AR4)                           #
# =========================================================================== #

def _is_tenant_table(name, declared_rec, live_has_boundary):
    """Heuristic for whether a table is tenant-scoped (and thus subject to AR2-AR4):
      - declared CREATE TABLE carried a tenant_id column, OR
      - the table name starts with 'tenant_' (the spec's B.1 convention), OR
      - it carries a policy whose qual references the tenant claim (live signal)."""
    if declared_rec and declared_rec.get("tenant_scoped"):
        return True
    if name.startswith("tenant_"):
        return True
    return live_has_boundary


def _qual_references_tenant_claim(qual):
    """A boundary-style policy: its qual references the tenant claim. Used to
    recognize tenant tables live (a permissive tenant-match policy is the boundary).
    Accepts the tenant-table form (tenant_id + request.jwt.claims) OR the Storage
    form (storage.foldername prefix match against request.jwt.claims)."""
    if not qual:
        return False
    q = qual.lower()
    if "request.jwt.claims" not in q:
        return False
    return "tenant_id" in q or "foldername" in q


def _has_permissive_grant_for_broad_role(policies):
    """True iff `policies` contains at least ONE PERMISSIVE policy targeting a broad
    role (public/authenticated). This is the GRANT half of PG RLS: a row is visible
    iff (>=1 PERMISSIVE passes) AND (all RESTRICTIVE pass). With NO permissive policy
    for the broad role, the boundary denies EVERY row (the RESTRICTIVE-only 0-rows
    trap, AR2). A `service_role`-only permissive policy does NOT count -- it grants
    rows to service_role, never to authenticated/public, so it cannot rescue the
    trap for end-users/agents."""
    for p in policies:
        if p["permissive"] == "PERMISSIVE" and (set(p["roles"]) & BROAD_ROLES):
            return True
    return False


def compare(declared, live_tables, live_policies, live_forced=None):
    """Return a list of finding dicts: {severity, code, table, msg}. Empty => clean.
    severity 'FAIL' blocks; 'WARN' is advisory (does not flip exit code).
    `live_forced` (optional {table -> relforcerowsecurity bool}) enables the
    live-side FORCE check; when None only declared-side FORCE is asserted."""
    findings = []
    if live_forced is None:
        live_forced = {}

    declared_tables = set(declared.keys())
    live_table_set = set(live_tables.keys())

    # group live policies by table for the tenant-table heuristic + per-table checks
    live_pol_by_table = {}
    for p in live_policies:
        live_pol_by_table.setdefault(p["table"], []).append(p)

    def live_has_boundary(t):
        return any(_qual_references_tenant_claim(p.get("qual")) for p in live_pol_by_table.get(t, []))

    # ---- DRIFT: live vs declared table-set divergence -----------------------
    for t in sorted(live_table_set - declared_tables):
        findings.append({
            "severity": "FAIL", "code": "DRIFT_LIVE_NOT_DECLARED", "table": t,
            "msg": f"live table '{t}' is absent from declared migrations "
                   f"(Dashboard-applied drift -- migrations must be source of truth, ADR D8)",
        })
    for t in sorted(declared_tables - live_table_set):
        findings.append({
            "severity": "FAIL", "code": "DRIFT_DECLARED_NOT_LIVE", "table": t,
            "msg": f"declared table '{t}' is absent from live catalog "
                   f"(un-pushed migration -- run 'supabase db push')",
        })

    # ---- AR1: PERMISSIVE USING(true) on public/authenticated (the produtos bug)
    # Checked across ALL live policies regardless of table-classification, because
    # this is exactly the live bypass class and must never appear on a data table.
    for p in live_policies:
        roles = set(p["roles"])
        if (p["permissive"] == "PERMISSIVE"
                and roles & BROAD_ROLES
                and _is_true_qual(p["qual"])):
            findings.append({
                "severity": "FAIL", "code": "AR1_PERMISSIVE_TRUE_BROAD_ROLE",
                "table": p["table"],
                "msg": f"policy '{p['name']}' on '{p['table']}' is PERMISSIVE USING(true) "
                       f"for role(s) {sorted(roles & BROAD_ROLES)} -- this OR-combines and "
                       f"nullifies the tenant boundary (the produtos bug). Scope the "
                       f"service-role escape 'TO service_role' ONLY.",
            })

    # ---- Per tenant-table checks: AR4 (rls), AR2 (RESTRICTIVE-only 0-rows trap) -
    all_tables = declared_tables | live_table_set
    for t in sorted(all_tables):
        drec = declared.get(t)
        is_tenant = _is_tenant_table(t, drec, live_has_boundary(t))
        if not is_tenant:
            continue

        # AR4 -- tenant table with RLS off (live signal is authoritative when present)
        if t in live_tables and live_tables[t] is False:
            findings.append({
                "severity": "FAIL", "code": "AR4_RLS_DISABLED", "table": t,
                "msg": f"tenant table '{t}' has RLS disabled (relrowsecurity=false) -- "
                       f"rows are globally readable. ENABLE + FORCE ROW LEVEL SECURITY.",
            })
        # declared-side AR4: tenant_id column but no ENABLE in migrations
        if drec and drec.get("tenant_scoped") and not drec.get("rls_enabled"):
            findings.append({
                "severity": "FAIL", "code": "AR4_RLS_NOT_ENABLED_DECLARED", "table": t,
                "msg": f"declared tenant table '{t}' has a tenant_id column but no "
                       f"ENABLE ROW LEVEL SECURITY in migrations (AR4).",
            })

        # AR4b (FORCE) -- a tenant DATA table (one with a tenant_id column) must also
        # carry FORCE ROW LEVEL SECURITY. ENABLE alone exempts the TABLE OWNER from
        # RLS; FORCE makes the boundary apply even to the owner role (e.g. the
        # migration/superuser role, or any future role that owns the table), closing
        # the owner-bypass. The repo convention is ENABLE + FORCE on every tenant
        # table (tenant_memory/data/runtime/agent_runs/agent_steps/...). Declared-side:
        # flag tenant_scoped AND NOT forced. NOTE: this is keyed on `tenant_scoped`
        # (a parsed tenant_id column), so the PLATFORM-owned storage.objects -- which
        # has NO CREATE TABLE here and is recognized only via its live boundary -- is
        # NOT flagged; FORCE is correctly moot for it (tenant role is never its owner).
        if drec and drec.get("tenant_scoped") and not drec.get("forced"):
            findings.append({
                "severity": "FAIL", "code": "AR4_FORCE_NOT_SET_DECLARED", "table": t,
                "msg": f"declared tenant table '{t}' has a tenant_id column and ENABLE "
                       f"but no FORCE ROW LEVEL SECURITY -- the table OWNER is exempt "
                       f"from the boundary (owner-bypass). Add "
                       f"'ALTER TABLE {t} FORCE ROW LEVEL SECURITY;' (the repo "
                       f"convention: every tenant table is ENABLE + FORCE).",
            })
        # live-side FORCE: a live tenant table with relforcerowsecurity=false. The
        # storage.objects platform table is exempt (FORCE is moot there).
        if (t in live_forced and live_forced[t] is False
                and t not in STORAGE_OBJECTS_NAMES):
            findings.append({
                "severity": "FAIL", "code": "AR4_FORCE_DISABLED", "table": t,
                "msg": f"tenant table '{t}' has FORCE RLS off "
                       f"(relforcerowsecurity=false) -- the table OWNER bypasses the "
                       f"boundary. FORCE ROW LEVEL SECURITY.",
            })

        # AR2 -- the boundary must be a PERMISSIVE tenant-match. In PG RLS a row is
        # visible iff (>=1 PERMISSIVE passes) AND (all RESTRICTIVE pass). If a tenant
        # table has RESTRICTIVE policies for the broad role but NO permissive grant,
        # the permissive set is EMPTY -> the boundary denies EVERY row, even the
        # caller's own tenant (the RESTRICTIVE-only 0-rows trap, proven on live
        # `produtos` 2026-06-16). Flag it on whichever side carries policies.
        live_pols = live_pol_by_table.get(t, [])
        if live_pols:
            has_restr = any(p["permissive"] == "RESTRICTIVE" and (set(p["roles"]) & BROAD_ROLES)
                            for p in live_pols)
            if has_restr and not _has_permissive_grant_for_broad_role(live_pols):
                findings.append({
                    "severity": "FAIL", "code": "AR2_RESTRICTIVE_ONLY_NO_PERMISSIVE",
                    "table": t,
                    "msg": f"tenant table '{t}' has RESTRICTIVE policy(ies) for "
                           f"public/authenticated but NO permissive policy -- the "
                           f"RESTRICTIVE-only 0-rows trap (a row needs >=1 PERMISSIVE "
                           f"to pass; with none, even the caller's own tenant is "
                           f"invisible). Replace with a SINGLE PERMISSIVE tenant-match "
                           f"boundary (USING/WITH CHECK = the tenant claim).",
                })
        if drec and drec["policies"]:
            has_restr_d = any(p["permissive"] == "RESTRICTIVE" and (set(p["roles"]) & BROAD_ROLES)
                              for p in drec["policies"])
            if has_restr_d and not _has_permissive_grant_for_broad_role(drec["policies"]):
                findings.append({
                    "severity": "FAIL", "code": "AR2_RESTRICTIVE_ONLY_NO_PERMISSIVE_DECLARED",
                    "table": t,
                    "msg": f"declared tenant table '{t}' has RESTRICTIVE policy(ies) "
                           f"for public/authenticated but NO permissive policy -- the "
                           f"RESTRICTIVE-only 0-rows trap. Replace with a SINGLE "
                           f"PERMISSIVE tenant-match boundary.",
                })

    # ---- AR_STORAGE: storage.objects must have RLS ENABLED on the LIVE snapshot.
    # The tenant FT boundary (the tenant_boundary prefix-match policy in
    # 20260616000004_tenant_vault_storage.sql) is INERT unless storage.objects has
    # relrowsecurity=true; if it is off, every tenant's FT objects are globally
    # readable. This is a DEDICATED check (not the generic per-table AR4 loop)
    # because storage.objects lives in the `storage` schema -- the public-schema
    # LIVE_TABLES_SQL does NOT return it, so a live fetch must explicitly add a
    # 'storage.objects' row for this to apply. Absent => SKIP (never a false PASS:
    # the migration's own defensive ALTER ... ENABLE is the on-DB guarantee; this
    # check is the snapshot-side cross-verification when storage IS in the snapshot).
    for sname in STORAGE_OBJECTS_NAMES:
        if sname in live_tables and live_tables[sname] is False:
            findings.append({
                "severity": "FAIL", "code": "AR_STORAGE_RLS_DISABLED", "table": sname,
                "msg": f"storage.objects has RLS disabled (relrowsecurity=false) on the "
                       f"live snapshot -- the tenant_boundary prefix-match policy is "
                       f"INERT and every tenant's FT objects are globally readable. "
                       f"ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY.",
            })
            break  # one finding is enough; both names denote the same table

    # ---- AR3: write-capable policy without WITH CHECK -----------------------
    # Live side: pg_policies.with_check is NULL for a write policy lacking it.
    for p in live_policies:
        if p["cmd"] in WRITE_CMDS and not _is_true_qual_servicerole_ok(p):
            if p["with_check"] in (None, "") and _is_tenant_or_broad(p, live_pol_by_table, declared):
                findings.append({
                    "severity": "FAIL", "code": "AR3_WRITE_NO_WITH_CHECK",
                    "table": p["table"],
                    "msg": f"write-capable policy '{p['name']}' on '{p['table']}' "
                           f"(FOR {p['cmd']}) has no WITH CHECK -- a row could be written "
                           f"INTO another tenant. Every FOR ALL/INSERT/UPDATE needs WITH CHECK.",
                })
    if declared:
        for t, drec in declared.items():
            if not _is_tenant_table(t, drec, live_has_boundary(t)):
                continue
            for p in drec["policies"]:
                if p["cmd"] in WRITE_CMDS and "service_role" not in p["roles"]:
                    if p["with_check"] in (None, ""):
                        findings.append({
                            "severity": "FAIL", "code": "AR3_WRITE_NO_WITH_CHECK_DECLARED",
                            "table": t,
                            "msg": f"declared write policy '{p['name']}' on '{t}' "
                                   f"(FOR {p['cmd']}) lacks WITH CHECK (AR3).",
                        })
    return findings


def _is_true_qual_servicerole_ok(p):
    """A FOR ALL policy scoped TO service_role ONLY (the sanctioned B.2 escape) is
    exempt from the AR3 with_check requirement -- it is the audited bypass grant."""
    return p["roles"] == ["service_role"]


def _is_tenant_or_broad(p, live_pol_by_table, declared):
    """AR3 (live) applies to a write policy on a tenant table OR one that targets a
    broad role (public/authenticated) -- the cases where a missing WITH CHECK lets a
    cross-tenant write through. A service_role-only policy is exempt (handled above)."""
    if set(p["roles"]) & BROAD_ROLES:
        return True
    t = p["table"]
    if t.startswith("tenant_"):
        return True
    drec = declared.get(t)
    if drec and drec.get("tenant_scoped"):
        return True
    # boundary policy present on the table => treat as tenant table
    return any(_qual_references_tenant_claim(q.get("qual")) for q in live_pol_by_table.get(t, []))


# =========================================================================== #
# REPORTING                                                                   #
# =========================================================================== #

def render_report(findings, declared, live_tables, live_policies, warnings):
    lines = []
    lines.append("=== CEX RLS DRIFT-CHECK + LINTER ===")
    lines.append(f"declared tables: {len(declared)} | live tables: {len(live_tables)} | "
                 f"live policies: {len(live_policies)}")
    for w in warnings:
        lines.append(f"[WARN] {w}")
    fails = [f for f in findings if f["severity"] == "FAIL"]
    warns = [f for f in findings if f["severity"] == "WARN"]
    for f in warns:
        lines.append(f"[WARN] {f['code']} [{f['table']}] {f['msg']}")
    if not fails:
        lines.append("OK -- no RLS drift or tenant-isolation violations detected.")
        return "\n".join(lines), 0
    lines.append(f"[FAIL] {len(fails)} violation(s):")
    for f in fails:
        lines.append(f"  - {f['code']} [{f['table']}] {f['msg']}")
    return "\n".join(lines), 1


# =========================================================================== #
# (4) SELF-TEST                                                               #
# =========================================================================== #

def build_self_test_snapshot():
    """A synthetic LIVE snapshot reproducing the produtos pair: ONE tenant-match
    policy AND ONE PERMISSIVE 'Service role full access' USING(true) on role public.
    The AR1 detector MUST flag the second (a 2nd permissive USING(true) on a broad
    role OR-grants everything). AR2 must NOT fire here: a permissive grant for
    public DOES exist (so it is not the RESTRICTIVE-only 0-rows trap -- the bug here
    is the OPPOSITE: an over-broad permissive grant)."""
    return {
        "tables": [
            # forced:True -- a corrected tenant table is ENABLE + FORCE; this keeps the
            # live-side FORCE check (AR4_FORCE_DISABLED) quiet so CASE 1 isolates the
            # AR1 bypass alone (the bug here is an over-broad permissive, not FORCE).
            {"name": "produtos", "rls": True, "forced": True},
        ],
        "policies": [
            {
                "table": "produtos", "name": "Tenant isolation",
                "permissive": "RESTRICTIVE", "roles": ["public"], "cmd": "ALL",
                "qual": "tenant_id = current_setting('request.jwt.claims', true)"
                        "::json ->> 'tenant_id'",
                "with_check": "tenant_id = current_setting('request.jwt.claims', true)"
                              "::json ->> 'tenant_id'",
            },
            {
                "table": "produtos", "name": "Service role full access",
                "permissive": "PERMISSIVE", "roles": ["public"], "cmd": "ALL",
                "qual": "true", "with_check": "true",
            },
        ],
    }


def build_restrictive_only_snapshot():
    """A synthetic LIVE snapshot reproducing the EMPIRICAL bug fixed 2026-06-16: a
    tenant table declares RESTRICTIVE-only policies for role `authenticated`
    (tenant_boundary_select + tenant_boundary_modify) and NO permissive policy for
    authenticated. In PG RLS a row is visible iff (>=1 PERMISSIVE passes) AND (all
    RESTRICTIVE pass); with NO permissive grant the boundary denies EVERY row, even
    the caller's own tenant. The service_role_all PERMISSIVE policy targets
    service_role ONLY, so it does NOT rescue authenticated. AR2 MUST flag this.

    NOTE: the fixture table is named `tenant_legacy_fixture` -- a synthetic name, NOT
    the live `tenant_memory`. The shipped migration 20260616000001_tenant_memory.sql
    was CORRECTED to a SINGLE PERMISSIVE `tenant_boundary` (matching the sibling
    tenant_data / tenant_runtime migrations); this snapshot keeps the superseded
    RESTRICTIVE-only shape ON A NEUTRAL TABLE so the negative test stays broken (the
    AR2 trigger) without implying the drift-check expects the old tenant_memory."""
    boundary_qual = ("(tenant_id)::text = current_setting('request.jwt.claims', true)"
                     "::json ->> 'tenant_id'")
    return {
        "tables": [
            # forced:True -- isolate the AR2 trap; the live-side FORCE check stays quiet.
            {"name": "tenant_legacy_fixture", "rls": True, "forced": True},
        ],
        "policies": [
            {"table": "tenant_legacy_fixture", "name": "tenant_boundary_select",
             "permissive": "RESTRICTIVE", "roles": ["authenticated"], "cmd": "SELECT",
             "qual": boundary_qual, "with_check": None},
            {"table": "tenant_legacy_fixture", "name": "tenant_boundary_modify",
             "permissive": "RESTRICTIVE", "roles": ["authenticated"], "cmd": "ALL",
             "qual": boundary_qual, "with_check": boundary_qual},
            {"table": "tenant_legacy_fixture", "name": "service_role_all",
             "permissive": "PERMISSIVE", "roles": ["service_role"], "cmd": "ALL",
             "qual": "true", "with_check": "true"},
        ],
    }


def build_force_missing_snapshot():
    """A synthetic LIVE snapshot for a tenant table that has RLS ENABLED but FORCE
    OFF (relrowsecurity=true, relforcerowsecurity=false). ENABLE alone exempts the
    table OWNER from the boundary; FORCE closes that owner-bypass. The repo
    convention is ENABLE + FORCE on every tenant table. AR4_FORCE_DISABLED (live)
    MUST flag this; the boundary policy is otherwise correct (a single PERMISSIVE
    tenant-match), so AR1 and AR2 must NOT fire."""
    boundary_qual = ("(tenant_id)::text = current_setting('request.jwt.claims', true)"
                     "::json ->> 'tenant_id'")
    return {
        "tables": [
            {"name": "tenant_forcegap_fixture", "rls": True, "forced": False},
        ],
        "policies": [
            {"table": "tenant_forcegap_fixture", "name": "tenant_boundary",
             "permissive": "PERMISSIVE", "roles": ["authenticated"], "cmd": "ALL",
             "qual": boundary_qual, "with_check": boundary_qual},
            {"table": "tenant_forcegap_fixture", "name": "service_role_all",
             "permissive": "PERMISSIVE", "roles": ["service_role"], "cmd": "ALL",
             "qual": "true", "with_check": "true"},
        ],
    }


def build_storage_rls_off_snapshot():
    """A synthetic LIVE snapshot where storage.objects has RLS DISABLED
    (relrowsecurity=false) while the tenant_boundary prefix-match policy exists. With
    RLS off the policy is INERT -> every tenant's FT objects are globally readable.
    AR_STORAGE_RLS_DISABLED MUST flag this. The table is named 'storage.objects'
    (the storage-schema entry a live fetch must add, since LIVE_TABLES_SQL only
    scopes to public). AR1/AR2/FORCE must NOT fire (the policy shape is the correct
    permissive prefix-match; the bug is purely that RLS is OFF)."""
    boundary_qual = (
        "(storage.foldername(name))[1] = 'tenant/' || coalesce("
        "current_setting('request.jwt.claims', true)::json ->> 'tenant_id', "
        "current_setting('request.jwt.claims', true)::json -> 'app_metadata' "
        "->> 'tenant_id')")
    return {
        "tables": [
            {"name": "storage.objects", "rls": False, "forced": False},
        ],
        "policies": [
            {"table": "storage.objects", "name": "tenant_boundary",
             "permissive": "PERMISSIVE", "roles": ["authenticated"], "cmd": "ALL",
             "qual": boundary_qual, "with_check": boundary_qual},
            {"table": "storage.objects", "name": "service_role_all",
             "permissive": "PERMISSIVE", "roles": ["service_role"], "cmd": "ALL",
             "qual": "true", "with_check": "true"},
        ],
    }


def _run_self_test_case(title, snapshot, declared, *, expect_ar1, expect_ar2,
                        expect_force=False, expect_storage=False):
    """Run one self-test case (live snapshot + matching declared so table-drift does
    NOT fire) and check that the AR1 / AR2 / FORCE / storage expectations hold and the
    simulated check fails (every case here is a known-bad config -> exit must be
    nonzero). `expect_force` covers the declared/live FORCE-missing codes
    (AR4_FORCE_*); `expect_storage` covers AR_STORAGE_RLS_DISABLED. Returns True iff
    the case behaved as expected."""
    print(f"=== SELF-TEST: {title} ===")
    live_tables, live_forced, live_policies = normalize_live(snapshot)
    findings = compare(declared, live_tables, live_policies, live_forced)
    report, exit_code = render_report(findings, declared, live_tables, live_policies, [])
    print(report)
    print("--- simulated check exit code:", exit_code, "---")

    ar1 = [f for f in findings if f["code"] == "AR1_PERMISSIVE_TRUE_BROAD_ROLE"]
    ar2 = [f for f in findings if f["code"].startswith("AR2")]
    force = [f for f in findings if f["code"].startswith("AR4_FORCE")]
    storage = [f for f in findings if f["code"] == "AR_STORAGE_RLS_DISABLED"]
    ok = ((bool(ar1) == expect_ar1) and (bool(ar2) == expect_ar2)
          and (bool(force) == expect_force) and (bool(storage) == expect_storage)
          and exit_code != 0)
    if ok:
        print(f"[OK] case PASSED -- AR1={len(ar1)} (expect={expect_ar1}), "
              f"AR2={len(ar2)} (expect={expect_ar2}), FORCE={len(force)} "
              f"(expect={expect_force}), STORAGE={len(storage)} "
              f"(expect={expect_storage}), exit={exit_code}.")
    else:
        print(f"[FAIL] case FAILED -- AR1={len(ar1)} (expect={expect_ar1}), "
              f"AR2={len(ar2)} (expect={expect_ar2}), FORCE={len(force)} "
              f"(expect={expect_force}), STORAGE={len(storage)} "
              f"(expect={expect_storage}), exit={exit_code}.")
    print()
    return ok


def run_self_test():
    """Run both detector cases (no DB, no files) and assert each behaves as expected:
      CASE 1 -- the produtos USING(true) sibling -> AR1 fires, AR2 does NOT.
      CASE 2 -- the RESTRICTIVE-only-no-permissive trap (the 2026-06-16 bug) -> AR2
                fires, AR1 does NOT.
    Returns process exit code (0 = self-test PASSED, 2 = FAILED)."""
    # CASE 1: produtos AR1 bypass -- declare the SAME table so only the policy bug shows.
    produtos_declared = {
        "produtos": {
            "rls_enabled": True, "forced": True, "tenant_scoped": True,
            "policies": [
                {"name": "Tenant isolation", "table": "produtos",
                 "permissive": "RESTRICTIVE", "roles": ["public"], "cmd": "ALL",
                 "qual": "tenant_id = current_setting('request.jwt.claims', true)"
                         "::json ->> 'tenant_id'",
                 "with_check": "tenant_id = current_setting('request.jwt.claims', true)"
                               "::json ->> 'tenant_id'"},
                {"name": "Service role full access", "table": "produtos",
                 "permissive": "PERMISSIVE", "roles": ["public"], "cmd": "ALL",
                 "qual": "true", "with_check": "true"},
            ],
        }
    }
    case1 = _run_self_test_case(
        "produtos-style AR1 bypass detection (2nd permissive USING(true) on public)",
        build_self_test_snapshot(), produtos_declared,
        expect_ar1=True, expect_ar2=False)

    # CASE 2: RESTRICTIVE-only-no-permissive trap -- declare the SAME table so only the
    # policy bug shows. service_role_all is PERMISSIVE but TO service_role only -> does
    # NOT count as a grant for authenticated, so AR2 MUST fire and AR1 must NOT.
    # The table is the synthetic `tenant_legacy_fixture` (NOT the live tenant_memory,
    # whose migration was corrected to a SINGLE PERMISSIVE tenant_boundary like its
    # tenant_data / tenant_runtime siblings); the fixture keeps the superseded
    # RESTRICTIVE-only shape on a neutral name purely to drive the AR2 detector.
    boundary_qual = ("(tenant_id)::text = current_setting('request.jwt.claims', true)"
                     "::json ->> 'tenant_id'")
    restrictive_only_declared = {
        "tenant_legacy_fixture": {
            "rls_enabled": True, "forced": True, "tenant_scoped": True,
            "policies": [
                {"name": "tenant_boundary_select", "table": "tenant_legacy_fixture",
                 "permissive": "RESTRICTIVE", "roles": ["authenticated"], "cmd": "SELECT",
                 "qual": boundary_qual, "with_check": None},
                {"name": "tenant_boundary_modify", "table": "tenant_legacy_fixture",
                 "permissive": "RESTRICTIVE", "roles": ["authenticated"], "cmd": "ALL",
                 "qual": boundary_qual, "with_check": boundary_qual},
                {"name": "service_role_all", "table": "tenant_legacy_fixture",
                 "permissive": "PERMISSIVE", "roles": ["service_role"], "cmd": "ALL",
                 "qual": "true", "with_check": "true"},
            ],
        }
    }
    case2 = _run_self_test_case(
        "RESTRICTIVE-only-no-permissive 0-rows trap (the 2026-06-16 bug)",
        build_restrictive_only_snapshot(), restrictive_only_declared,
        expect_ar1=False, expect_ar2=True)

    # CASE 3: FORCE-missing -- a tenant table with ENABLE but NO FORCE. Declare the
    # SAME table (tenant_scoped + rls_enabled True but forced False) so BOTH the
    # declared-side (AR4_FORCE_NOT_SET_DECLARED) and live-side (AR4_FORCE_DISABLED)
    # FORCE checks fire and nothing else does. The boundary is a correct single
    # PERMISSIVE tenant-match, so AR1/AR2 must NOT fire.
    force_boundary_qual = ("(tenant_id)::text = current_setting('request.jwt.claims', "
                           "true)::json ->> 'tenant_id'")
    force_missing_declared = {
        "tenant_forcegap_fixture": {
            "rls_enabled": True, "forced": False, "tenant_scoped": True,
            "policies": [
                {"name": "tenant_boundary", "table": "tenant_forcegap_fixture",
                 "permissive": "PERMISSIVE", "roles": ["authenticated"], "cmd": "ALL",
                 "qual": force_boundary_qual, "with_check": force_boundary_qual},
                {"name": "service_role_all", "table": "tenant_forcegap_fixture",
                 "permissive": "PERMISSIVE", "roles": ["service_role"], "cmd": "ALL",
                 "qual": "true", "with_check": "true"},
            ],
        }
    }
    case3 = _run_self_test_case(
        "FORCE-missing on a tenant table (ENABLE but no FORCE -- owner-bypass)",
        build_force_missing_snapshot(), force_missing_declared,
        expect_ar1=False, expect_ar2=False, expect_force=True, expect_storage=False)

    # CASE 4: storage.objects RLS OFF -- the prefix-match boundary policy exists but
    # storage.objects has relrowsecurity=false, so it is INERT. AR_STORAGE_RLS_DISABLED
    # MUST fire. The DECLARED-side parser strips the schema, so storage.objects is the
    # key 'objects'; declare a matching 'objects' record (NOT tenant_scoped -- storage
    # has no tenant_id column and FORCE is moot for it) so table-set drift does NOT
    # fire and the FORCE check stays quiet. AR1/AR2/FORCE must NOT fire; only the
    # storage-RLS-off (and the generic AR4_RLS_DISABLED, which is additive) flag.
    storage_off_declared = {
        "objects": {
            "rls_enabled": True, "forced": False, "tenant_scoped": False,
            "policies": [
                {"name": "tenant_boundary", "table": "objects",
                 "permissive": "PERMISSIVE", "roles": ["authenticated"], "cmd": "ALL",
                 "qual": "(storage.foldername(name))[1] = 'tenant/' || "
                         "current_setting('request.jwt.claims', true)::json ->> 'tenant_id'",
                 "with_check": "(storage.foldername(name))[1] = 'tenant/' || "
                               "current_setting('request.jwt.claims', true)::json "
                               "->> 'tenant_id'"},
                {"name": "service_role_all", "table": "objects",
                 "permissive": "PERMISSIVE", "roles": ["service_role"], "cmd": "ALL",
                 "qual": "true", "with_check": "true"},
            ],
        }
    }
    case4 = _run_self_test_case(
        "storage.objects RLS OFF (tenant_boundary policy INERT -- FT globally readable)",
        build_storage_rls_off_snapshot(), storage_off_declared,
        expect_ar1=False, expect_ar2=False, expect_force=False, expect_storage=True)

    if case1 and case2 and case3 and case4:
        print("[OK] SELF-TEST PASSED -- all detector cases behaved as expected "
              "(AR1 produtos bypass + AR2 RESTRICTIVE-only 0-rows trap + AR4 FORCE-missing "
              "+ AR_STORAGE storage.objects RLS off).")
        return 0
    print(f"[FAIL] SELF-TEST FAILED -- case1={case1}, case2={case2}, "
          f"case3={case3}, case4={case4}.")
    return 2


# =========================================================================== #
# CLI                                                                         #
# =========================================================================== #

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="RLS drift-check + linter: declared migrations vs live catalog "
                    "(spec_multitenant_data_plane_v1 C.2/C.3).")
    ap.add_argument("--migrations", default=str(DEFAULT_MIGRATIONS),
                    help="dir of supabase/migrations/*.sql (default: supabase/migrations)")
    ap.add_argument("--live-json", metavar="FILE",
                    help="live catalog snapshot JSON ('-' for stdin)")
    ap.add_argument("--supabase-ref", metavar="REF",
                    help="OPTIONAL: fetch live via Management API for this project ref "
                         "(lazy requests import; needs SUPABASE_ACCESS_TOKEN). "
                         "NOT exercised in the T4 build.")
    ap.add_argument("--timeout", type=int, default=60,
                    help="Management API request timeout seconds (default 60)")
    ap.add_argument("--self-test", action="store_true",
                    help="run the synthetic AR detector self-test (AR1 bypass, AR2 "
                         "0-rows trap, AR4 FORCE-missing, AR_STORAGE storage RLS off) "
                         "and exit")
    ap.add_argument("--json", dest="json_out", action="store_true",
                    help="emit findings as JSON instead of a text report")
    args = ap.parse_args(argv)

    if args.self_test:
        return run_self_test()

    # Parse the declared side.
    declared, warnings = parse_migrations(args.migrations)

    # Acquire the live snapshot.
    if args.live_json:
        snapshot = load_live_json(args.live_json)
    elif args.supabase_ref:
        snapshot = fetch_live_via_management_api(
            args.supabase_ref, timeout=args.timeout)
    else:
        print("[FAIL] no live snapshot: pass --live-json FILE (or '-' for stdin), "
              "or --supabase-ref REF. (Use --self-test to validate the detector.)",
              file=sys.stderr)
        return 2

    live_tables, live_forced, live_policies = normalize_live(snapshot)
    findings = compare(declared, live_tables, live_policies, live_forced)

    if args.json_out:
        print(json.dumps({
            "declared_tables": sorted(declared.keys()),
            "live_tables": sorted(live_tables.keys()),
            "warnings": warnings,
            "findings": findings,
            "ok": not any(f["severity"] == "FAIL" for f in findings),
        }, indent=2))
        return 0 if not any(f["severity"] == "FAIL" for f in findings) else 1

    report, exit_code = render_report(findings, declared, live_tables, live_policies, warnings)
    print(report)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
