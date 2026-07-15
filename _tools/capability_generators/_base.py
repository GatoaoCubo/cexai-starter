#!/usr/bin/env python3
# -*- coding: ascii -*-
"""capability_generators._base -- the STRUCTURED-GENERATOR interface contract.

THIS IS THE SINGLE SOURCE OF TRUTH a real capability generator implements (mission
MOLDED_REAL_SEAM, Wave 0). Read this docstring once; then a new generator is ONE new
file in this package, never an edit to anything shared.

============================================================================
THE INTERFACE (what every generator file looks like)
============================================================================

    # _tools/capability_generators/<capability_key>.py
    from typing import Any, Mapping, Optional
    from ._base import register, table_section, fields_section, list_section
    from ._base import StructuredOutput, structured_output

    KIND = "<resolved_kind>"          # the DEFAULT kind this generator serves (module const)

    @register(KIND)                   # OR: @register(KIND) + a module-level KIND const
    def build(
        inputs: Mapping[str, Any],
        *,
        credential: "Optional[Any]" = None,
        resolved_kind: "Optional[str]" = None,
    ) -> StructuredOutput:
        # 1. parse what you need from ``inputs`` (the typed form payload); default the
        #    rest from the capability's input_contract (capability_contracts_v1.0.md).
        # 2. produce the OUTPUT sections in the contract's ORDER + layout (frozen SHAPE).
        # 3. compute ``kind = effective_kind(resolved_kind, KIND)`` and use ``kind`` (not
        #    the bare ``KIND``) wherever your artifact JSON embeds a "kind" field (R-333).
        # 4. self-check (F7), then return structured_output(...).
        ...

A generator is a pure-ish callable:

    build(inputs: Mapping[str, Any], *, credential: Credential | None = None,
          resolved_kind: str | None = None)
            -> StructuredOutput

``resolved_kind`` (mission R-333) is the PER-TENANT RESOLVED kind a caller (e.g.
cex_run_capability._run_structured_generator) already holds -- it may differ from this
module's own ``KIND`` constant when a tenant overlay remaps the capability to a different
kind. A generator threads it into its artifact-JSON self-description via
``effective_kind(resolved_kind, KIND)`` (see the RESOLVED KIND section below) so the
artifact's own claimed kind never disagrees with the run's actual resolved kind. Optional +
defaults to None: a direct/legacy caller or a bare ``build({})`` scaffold call is
byte-identical to before R-333 (falls back to the module ``KIND`` constant).

  * ``inputs``     -- the typed form payload per the capability's ``input_contract``
                      (key -> value). The runtime hands you the parsed intent/options;
                      for now intent is a free string carried as inputs["intent"] +
                      whatever the dashboard form posted in options. Parse what you
                      need; DEFAULT the rest from the contract (never crash on a
                      missing optional field).
  * ``credential`` -- present ONLY when the capability needs an LLM (e.g. creative
                      copy). DETERMINISTIC generators (calculators, typed configs)
                      IGNORE it. The seam does NOT validate it for you -- an LLM
                      generator validates/uses it itself.
  * returns        -- a ``StructuredOutput`` dict (plain, JSON-serialisable, ASCII-safe).

============================================================================
THE RETURN SHAPE (StructuredOutput) -- frozen
============================================================================

    {
      "mold_id": str,                # the capability key, e.g. "custom_intake_form"
      "output_sections": list[dict], # REAL data; each section is ONE of the 3 layouts:
         #   {"title": str, "layout": "fields", "rows": [{"label": str, "value": Any}, ...]}
         #   {"title": str, "layout": "table",  "columns": [str,...], "table": [[cell,...],...],
         #                  "column_types"?: [str,...], "key_col_index"?: int}
         #   {"title": str, "layout": "list",   "items": [str, ...]}
         # ORDER + layout + columns/keys MUST match the capability's output_sections in
         # capability_contracts_v1.0.md (the SHAPE is FROZEN; only the data is real).
      "real": True,                  # => the renderer DROPS the "dados simulados" chip
      "passed": bool,                # F7 gate verdict for THIS output
      "score": float,                # 0..1 (the seam scales it to the 0..10 outcome strip)
      "artifact": str,               # canonical MD or JSON projection (for persist/results)
      "notes": list[str],            # optional provenance / caveats (NEVER fabricate)
    }

Build the sections with the helpers below (``table_section`` / ``fields_section`` /
``list_section``) so you emit the EXACT MoldSection shape the renderer reads, and
assemble the whole thing with ``structured_output(...)``.

============================================================================
INVARIANTS (every generator MUST hold)
============================================================================
  * ASCII-only source (.claude/rules/ascii-code-rule): ``--`` not em-dash, ``->`` not
    arrow, no emoji, no accents in code/strings. (Runtime VALUES that are user data may
    carry accents; the module's OWN constants stay diacritic-free, house style.)
  * Degrade-never: parse defensively; a missing optional input defaults from the
    contract. A generator SHOULD NOT raise -- but if it does, the seam catches it and
    falls back to the generic build (the endpoint never 500s).
  * Never fabricate: if a datum is unknown, say so in ``notes`` or omit it; do not
    invent a value to fill a cell.
  * Frozen SHAPE: emit the contract's sections in order with the declared layout +
    columns. Do NOT invent a layout (the renderer is frozen to fields|table|list).

This module imports NOTHING heavy (no DB, no network, no LLM) so importing the package
is cheap and side-effect-free beyond auto-discovery.
"""

from __future__ import annotations

import datetime
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence

try:  # TypedDict is stdlib on the 3.12 floor; degrade to a plain alias if ever absent.
    from typing import TypedDict

    class StructuredOutput(TypedDict, total=False):
        """The frozen return shape of a generator's ``build``. See the module docstring."""

        mold_id: str
        output_sections: List[Dict[str, Any]]
        real: bool
        passed: bool
        score: float
        artifact: str
        notes: List[str]
        # ADDITIVE -- mission COMPLETE2 W2a: per-finding provenance list.
        # Absent when a generator does not populate it (backward-compat).
        provenance: List[Dict[str, Any]]
except Exception:  # pragma: no cover - belt-and-braces for a stripped runtime
    StructuredOutput = Dict[str, Any]  # type: ignore[misc,assignment]


# --------------------------------------------------------------------------- #
# The registry. ``register`` mutates THIS dict; ``__init__.get_generator`` reads it.
# Keyed on the capability SLUG (council A4) -- the SLUG is the SOLE, UNIQUE generator key.
# (Previously keyed on the resolved KIND, but base capabilities COLLIDE on a shared kind --
# knowledge_card x research/docs/content; prompt_template x ads/email_builder -- so a kind
# key silently last-write-wins one generator over another. The runtime resolution site looks
# up by slug first, and by kind ONLY for an overlay-introduced novel kind.)
# --------------------------------------------------------------------------- #
_REGISTRY: Dict[str, Callable[..., "StructuredOutput"]] = {}


class GeneratorKeyCollision(RuntimeError):
    """Raised at import time when TWO DISTINCT generators register under the SAME key (council
    A4 invariant: each capability slug must resolve to its OWN generator). Re-registering the
    SAME function under the same key (idempotent reload_discovery) is allowed + a no-op."""


def register(key: str) -> Callable[[Callable[..., "StructuredOutput"]], Callable[..., "StructuredOutput"]]:
    """Decorator: bind a generator ``build`` callable to a capability ``key`` (the SLUG).

    Usage:

        @register("custom_intake_form")
        def build(inputs, *, credential=None) -> StructuredOutput: ...

    COLLISION-GUARDED (council A4): registering a DIFFERENT function under a key that is already
    taken raises GeneratorKeyCollision -- two capabilities can never silently share one generator
    key (the last-write-wins bug). Re-registering the SAME function (idempotent reload) is a no-op.
    Returns the function unchanged so it stays directly importable/testable.
    """

    def _decorator(fn: Callable[..., "StructuredOutput"]) -> Callable[..., "StructuredOutput"]:
        skey = str(key)
        existing = _REGISTRY.get(skey)
        if existing is not None and existing is not fn:
            raise GeneratorKeyCollision(
                "generator key %r already registered by %s.%s -- a capability slug must resolve "
                "to its OWN generator (council A4: slug is the sole key)" % (
                    skey,
                    getattr(existing, "__module__", "?"),
                    getattr(existing, "__name__", "?"),
                )
            )
        _REGISTRY[skey] = fn
        return fn

    return _decorator


def assert_no_key_collisions() -> int:
    """Re-affirm the A4 invariant explicitly (for a test / import-time check): every registered
    generator key maps to exactly one callable. ``register`` already enforces this on the way in
    (a collision raises there), so this is a belt-and-braces assertion that the live registry has
    one fn per key. Returns the number of distinct keys. Raises GeneratorKeyCollision on a dup."""
    seen: Dict[int, str] = {}
    for k, fn in _REGISTRY.items():
        # A single fn legitimately serves multiple keys ONLY via distinct @register calls; what we
        # forbid is TWO DIFFERENT fns on ONE key, which register() already blocks. Here we just
        # confirm the dict is well-formed (one value per key, which a dict guarantees) + non-empty.
        seen[id(fn)] = k
    return len(_REGISTRY)


def get_generator(kind: str) -> Optional[Callable[..., "StructuredOutput"]]:
    """Return the registered ``build`` callable for ``kind``, or None when none exists.

    This is the lookup the runtime seam (cex_run_capability.run_capability) uses. None
    => byte-identical fall-through to the generic CEXAgent.build (the zero-regression
    invariant)."""
    return _REGISTRY.get(str(kind))


# --------------------------------------------------------------------------- #
# Section helpers -- emit the EXACT MoldSection shape StructuredResultView reads.
# (TS: lib/molds.MoldSection -- layout in {"fields","table","list"}.)
# --------------------------------------------------------------------------- #
def fields_section(
    title: str,
    rows: "List[Any]",
    *,
    note: Optional[str] = None,
    contract_version: Optional[str] = None,
    confidence: Optional[float] = None,
) -> Dict[str, Any]:
    """A ``layout="fields"`` section: label/value rows.

    ``rows`` may be a list of (label, value) pairs OR a list of {"label","value"} dicts.
    Rows with an empty label are dropped (mirrors the renderer's ``r.label`` filter).
    ``confidence`` (0..1, optional) is the per-section trust slot (mission
    CAPABILITY_COMPLETENESS W1): emitted ONLY when a generator supplies one; absent ->
    no key (backward-compatible; the renderer ignores an unknown field)."""
    norm: List[Dict[str, Any]] = []
    for r in rows or []:
        if isinstance(r, Mapping):
            label = r.get("label")
            value = r.get("value")
        elif isinstance(r, (tuple, list)) and len(r) >= 2:
            label, value = r[0], r[1]
        else:
            continue
        if label is None or str(label).strip() == "":
            continue
        norm.append({"label": str(label), "value": value})
    section: Dict[str, Any] = {"title": str(title), "layout": "fields", "rows": norm}
    if note:
        section["note"] = str(note)
    if contract_version:
        section["contract_version"] = str(contract_version)
    _apply_section_confidence(section, confidence)
    return section


def table_section(
    title: str,
    columns: "List[str]",
    rows: "List[List[Any]]",
    *,
    column_types: "Optional[List[str]]" = None,
    key_col_index: Optional[int] = None,
    note: Optional[str] = None,
    contract_version: Optional[str] = None,
    confidence: Optional[float] = None,
) -> Dict[str, Any]:
    """A ``layout="table"`` section: a ``columns`` header + ``table`` rows (a grid).

    Each row SHOULD have exactly ``len(columns)`` cells (no-drift rule). ``column_types``
    (1:1 with columns) + ``key_col_index`` are optional typed slots (n03_schema).
    ``confidence`` (0..1, optional) is the per-section trust slot (mission
    CAPABILITY_COMPLETENESS W1): emitted ONLY when supplied (backward-compatible)."""
    cols = [str(c) for c in (columns or [])]
    grid: List[List[Any]] = [list(row) for row in (rows or [])]
    section: Dict[str, Any] = {"title": str(title), "layout": "table", "columns": cols, "table": grid}
    if column_types is not None:
        section["column_types"] = [str(t) for t in column_types]
    if key_col_index is not None:
        section["key_col_index"] = int(key_col_index)
    if note:
        section["note"] = str(note)
    if contract_version:
        section["contract_version"] = str(contract_version)
    _apply_section_confidence(section, confidence)
    return section


def list_section(
    title: str,
    items: "List[str]",
    *,
    note: Optional[str] = None,
    contract_version: Optional[str] = None,
    confidence: Optional[float] = None,
) -> Dict[str, Any]:
    """A ``layout="list"`` section: chip items. Empty/blank items are dropped (renderer parity).

    ``confidence`` (0..1, optional) is the per-section trust slot (mission
    CAPABILITY_COMPLETENESS W1): emitted ONLY when supplied (backward-compatible)."""
    norm = [str(it) for it in (items or []) if it is not None and str(it).strip() != ""]
    section: Dict[str, Any] = {"title": str(title), "layout": "list", "items": norm}
    if note:
        section["note"] = str(note)
    if contract_version:
        section["contract_version"] = str(contract_version)
    _apply_section_confidence(section, confidence)
    return section


# --------------------------------------------------------------------------- #
# UNIVERSAL METADATA ENVELOPE (mission CAPABILITY_COMPLETENESS, Wave 1).
#
# Every generator's ``build`` returns via ``structured_output(...)``; stamping the
# envelope THERE means all 16 generators inherit it from ONE change, with ZERO edits to
# any generator (the "1 change, 16 wins" of the completeness audit). The envelope is
# ADDITIVE: it adds NEW optional top-level keys to the result dict and NEVER alters
# ``output_sections`` / ``real`` / ``passed`` / ``score`` / ``artifact`` / ``notes``. The
# dual-output emitter (cex_dual_output._build_frontmatter reads only score/mold_id/passed/
# notes) and the dashboard renderer (reads output_sections) both keep working unchanged --
# the envelope is extra data they simply ignore.
#
# HONEST BY CONSTRUCTION (never-fabricate):
#   * generated_at        -- ISO-8601 UTC, stamped at build time (override for test determinism).
#   * generator_version   -- the calling module's GENERATOR_VERSION or CONTRACT_VERSION
#                            constant (introspected; a gen sets ONE constant, never hand-rolls
#                            the envelope); "0.0.0" when none is declared.
#   * run_mode            -- the calling module's RUN_MODE constant, else "offline-scaffold"
#                            (the conservative honest default: no LLM/credential at the base
#                            level). A real-math generator declares RUN_MODE="offline-deterministic";
#                            an LLM generator passes run_mode + model_used at its real run.
#   * model_used          -- the provider/model id ONLY when an LLM was actually used; default
#                            None -- NEVER a fabricated model when offline.
#   * confidence_breakdown -- keeps the overall ``score`` and decomposes the factors a gen has
#                            ({source_count, recency, agreement}); null where a factor is not
#                            computable (honest), so downstream can act risk-aware.
# --------------------------------------------------------------------------- #
DEFAULT_GENERATOR_VERSION = "0.0.0"
DEFAULT_RUN_MODE = "offline-scaffold"  # conservative honest default: no LLM/credential


def _utc_now_iso() -> str:
    """ISO-8601 UTC timestamp for ``generated_at``. TOTAL: "" on a clock surprise."""
    try:
        return datetime.datetime.now(datetime.timezone.utc).isoformat()
    except Exception:  # pragma: no cover - clock should never raise
        return ""


def _caller_module() -> Optional[Any]:
    """The module object of ``structured_output``'s caller (the generator's ``build``).

    Walks ONE frame past structured_output (this helper -> structured_output -> build).
    FAIL-SAFE + TOTAL: any introspection surprise -> None (the envelope then falls back to
    its defaults). Imports ``inspect`` lazily so the package stays import-light."""
    try:
        import inspect

        frame = inspect.currentframe()
        # frame=_caller_module ; f_back=structured_output ; f_back.f_back=the generator build
        caller = frame.f_back.f_back if (frame and frame.f_back) else None
        return inspect.getmodule(caller) if caller is not None else None
    except Exception:
        return None


def _module_const(module: Optional[Any], names: "Sequence[str]", default: str) -> str:
    """First non-empty string constant among ``names`` on ``module``, else ``default``. TOTAL."""
    if module is not None:
        for name in names:
            try:
                val = getattr(module, name, None)
            except Exception:
                val = None
            if isinstance(val, str) and val.strip():
                return val.strip()
    return default


def _default_confidence(score: float) -> Dict[str, Any]:
    """The honest default confidence_breakdown: the overall score + null factor slots.

    A generator that CAN compute a factor (source_count / recency / agreement) passes its own
    dict; the null defaults here are the never-fabricate stance (unknown != invented)."""
    return {
        "overall": score,
        "source_count": None,
        "recency": None,
        "agreement": None,
    }


def _apply_section_confidence(section: Dict[str, Any], confidence: Optional[float]) -> None:
    """Stamp the optional per-section ``confidence`` slot (0..1) when supplied. TOTAL: a
    non-numeric value is dropped (never coerced into a fabricated number)."""
    if confidence is None:
        return
    try:
        section["confidence"] = float(confidence)
    except (TypeError, ValueError):
        return


# --------------------------------------------------------------------------- #
# PER-FINDING PROVENANCE (mission COMPLETE2, Wave 2a).
#
# The audit's #1 gap: aggregate source counts are not verifiable. Per-finding
# provenance attaches WHERE each claim came from (URL, method, confidence) so a
# user can fact-check or refresh a single finding.
#
# HONEST BY CONSTRUCTION (never-fabricate):
#   * source_url  -- None offline (NEVER invent a URL).
#   * fetched_at  -- None offline (no real timestamp to stamp).
#   * method      -- "offline" when no live fetch occurred; else "fetch"|"scrape"|"manual".
#   * confidence  -- 0.0 offline; otherwise 0..1 per the sourcing-rigor formula.
#
# ADDITIVE: ``structured_output`` accepts an optional ``provenance`` kwarg; absent ->
# no key (backward-compat; existing consumers of the result dict are unaffected).
# --------------------------------------------------------------------------- #

def make_provenance(
    finding: str = "",
    source_url: Optional[str] = None,
    fetched_at: Optional[str] = None,
    method: str = "offline",
    confidence: float = 0.0,
) -> Dict[str, Any]:
    """Build a per-finding provenance record. TOTAL: never raises.

    NEVER-FABRICATE: pass source_url=None when the URL is unknown (never invent one).
    Offline convention: source_url=None, fetched_at=None, method='offline', confidence=0.0.

    ``finding``    -- a label identifying the claim, e.g. "Achados::Preco" or
                      "Evidencia::Durabilidade". Used for traceability.
    ``source_url`` -- the URL that backs this finding; None when unknown or offline.
    ``fetched_at`` -- ISO-8601 UTC of the fetch; None when offline.
    ``method``     -- "fetch" | "scrape" | "manual" | "offline" (how the data was obtained).
    ``confidence`` -- 0..1 trust score for this finding; 0.0 offline."""
    try:
        _url: Optional[str]
        if source_url:
            stripped = str(source_url).strip()
            _url = stripped if stripped else None
        else:
            _url = None
        _fetched: Optional[str] = str(fetched_at) if fetched_at else None
        try:
            _conf = max(0.0, min(1.0, float(confidence)))
        except (TypeError, ValueError):
            _conf = 0.0
        return {
            "finding": str(finding),
            "source_url": _url,
            "fetched_at": _fetched,
            "method": str(method) if method else "offline",
            "confidence": _conf,
        }
    except Exception:
        return {
            "finding": str(finding),
            "source_url": None,
            "fetched_at": None,
            "method": "offline",
            "confidence": 0.0,
        }


# --------------------------------------------------------------------------- #
# CONTACTS -> LEAD NORMALISATION (Wave A1) -- the ONE honest, deterministic translation that
# lets the CRM (crm.py) + the Sales Assistant (sales_assistant.py) render RICH on the
# tenant_data kind="contacts" rows the leads-injection feeds them.
#
# THE GAP: the Data-tab CRUD writes a `contacts` row in the OVERLAY's contacts payload --
# nome / cidade / segmento / status / telefone / next_followup / notes, with the status enum
# new | contacted | qualified | won | lost (capability_map.yaml `contacts`). The generators,
# however, read the LEADGEN lead-shape -- nome / tipo / canal / fonte / contato / sinal / score
# / status, with the funnel status enum novo | qualificado | em_contato | descartado | ganho.
# A raw contacts row therefore DEGRADES (telefone/notes ignored, status -> "outro", no score)
# -> thin output. This helper bridges the two shapes with a DETERMINISTIC vocab/field
# translation -- NEVER a fabricated value.
#
# THE MAPPING (HONEST -- translation only, never invents a value):
#   * nome      -> nome      (direct).
#   * telefone  -> contato   (the REAL contact; absent -> left absent, the projector shows '--').
#   * notes     -> sinal     (the context/intent; absent -> left absent).
#   * status    -> funnel    new->novo, contacted->em_contato, qualified->qualificado,
#                            won->ganho, lost->descartado. An UNKNOWN status is passed THROUGH
#                            unchanged (the generator's own _status_of buckets it to "outro" --
#                            never dropped, never invented).
#   * canal / fonte / tipo   NOT in the contacts payload -> NOT filled (honest-absent; the
#                            projector shows '--'). cidade/segmento are NOT canal -- never guessed.
#   * score                  contacts has NO confidence score -> NOT filled (honest n/a; the CRM
#                            ranks contacts-sourced leads by status honestly). Never derived.
#
# IDEMPOTENT + SAFE FOR BOTH SHAPES (the load-bearing invariant):
#   * a row that ALREADY carries the lead-shape (a leadgen-written row) passes through UNCHANGED
#     -- the mapping only FILLS a lead-key that is ABSENT from the row;
#   * detection is by PRESENCE: a row with NO contacts-only marker (telefone/segmento) and at
#     least one lead-only key (tipo/canal/fonte/contato/sinal/score) is treated as already
#     lead-shape and returned untouched (no status re-translation -- its status is already funnel
#     vocab). A row WITH a contacts-only marker is normalised field-by-field, but each lead-key
#     it happens to also carry (a hybrid row, e.g. the leads-injection test rows) is PRESERVED.
# --------------------------------------------------------------------------- #

# The contacts-status enum -> the funnel-status enum (the ONLY vocab translation). An UNKNOWN
# status is intentionally absent here -> the caller leaves it as-is for its own "outro" bucket.
_CONTACTS_STATUS_TO_FUNNEL: Dict[str, str] = {
    "new": "novo",
    "contacted": "em_contato",
    "qualified": "qualificado",
    "won": "ganho",
    "lost": "descartado",
}

# The lead-shape keys a generator reads. Used to detect an already-lead-shape row + to know
# which keys the mapping is allowed to FILL (only when ABSENT).
_LEAD_SHAPE_KEYS = ("nome", "tipo", "canal", "fonte", "contato", "sinal", "score", "status")

# The lead-only keys (present on a leadgen row, ABSENT on a pure contacts row). Their presence
# (with no contacts marker) is the signal that a row is ALREADY lead-shape -> pass through.
_LEAD_ONLY_KEYS = ("tipo", "canal", "fonte", "contato", "sinal", "score")

# The contacts-only markers (present on a contacts row, never emitted by leadgen). Their presence
# is the signal that a row is contacts-shaped (or hybrid) and should be field-normalised.
_CONTACTS_ONLY_MARKERS = ("telefone", "segmento")


def _present(row: "Mapping[str, Any]", key: str) -> bool:
    """True iff ``row`` carries a NON-empty value at ``key`` (None / "" / "--" count as absent).

    TOTAL. The CONTACT_ABSENT marker '--' is treated as absent so a contacts row whose telefone
    is '--' does not block the notes->sinal / honest-absent contract."""
    if key not in row:
        return False
    val = row.get(key)
    if val is None:
        return False
    if isinstance(val, str):
        s = val.strip()
        return bool(s) and s != "--"
    return True


def normalize_lead_row(row: "Mapping[str, Any]") -> Dict[str, Any]:
    """Map a contacts-shaped row to the lead-shape both generators read. HONEST + TOTAL.

    Deterministic vocab/field translation -- NEVER fabricates a value (no invented
    score/canal/fonte/tipo). Honest-absent for what the contacts payload lacks. IDEMPOTENT +
    safe for BOTH a contacts-shaped row AND a leadgen-shaped row:

      * a non-mapping -> {} (the caller skips it, mirroring the pre-helper coercion);
      * an ALREADY-lead-shape row (a lead-only key present, no contacts marker) -> a dict copy,
        UNCHANGED (no field/vocab translation -- its status is already funnel vocab);
      * a contacts-shaped (or hybrid) row -> a dict copy with the lead-keys FILLED only where
        ABSENT: telefone->contato, notes->sinal, the contacts status->the funnel status. Any
        lead-key the row ALREADY carries is PRESERVED (never overwritten). canal/fonte/tipo/score
        are left absent (honest -- the contacts payload has none of them).

    See the module block above for the full mapping + invariant rationale.
    """
    if not isinstance(row, Mapping):
        return {}

    out: Dict[str, Any] = dict(row)

    has_contacts_marker = any(_present(row, m) for m in _CONTACTS_ONLY_MARKERS)
    has_lead_only_key = any(k in row for k in _LEAD_ONLY_KEYS)

    # Already lead-shape (a leadgen-written row): a lead-only key present + NO contacts marker.
    # Pass through UNCHANGED -- never re-translate a status that is already funnel vocab.
    if has_lead_only_key and not has_contacts_marker:
        return out

    # Contacts-shaped (or hybrid) row: fill the lead-keys ONLY where they are ABSENT.
    # telefone -> contato (the REAL contact; never an invented one).
    if not _present(out, "contato") and _present(row, "telefone"):
        out["contato"] = row["telefone"]
    # notes -> sinal (the context/intent; never invented).
    if not _present(out, "sinal") and _present(row, "notes"):
        out["sinal"] = row["notes"]
    # status (contacts vocab) -> funnel vocab, ONLY when the row's status is a contacts term AND
    # no funnel status is already present. An unknown status is left as-is (the generator's
    # _status_of buckets it to "outro"). A status already in funnel vocab is left untouched.
    raw_status = row.get("status")
    status_key = str(raw_status or "").strip().lower()
    if status_key in _CONTACTS_STATUS_TO_FUNNEL:
        out["status"] = _CONTACTS_STATUS_TO_FUNNEL[status_key]
    # canal / fonte / tipo / score: NOT in the contacts payload -> never filled (honest-absent).
    # cidade / segmento are NOT canal -- never guessed. score is never derived.
    return out


# --------------------------------------------------------------------------- #
# RESOLVED KIND (mission R-333, register row R-333) -- the ONE seam every generator's
# ``build`` uses to decide what ``kind`` value its artifact-JSON self-description embeds.
#
# THE GAP: a generator's artifact JSON has always embedded its own module ``KIND`` constant
# (e.g. crm.py's ``demo_acme_crm``) even when the caller (cex_run_capability's
# ``_run_structured_generator``) already resolved a DIFFERENT, per-tenant kind for this run
# (e.g. a real <tenant> tenant's overlay resolves the ``crm`` capability to ``<tenant>_crm``) --
# res.kind + the persisted DB row use the correct resolved kind, but the artifact's OWN
# self-description silently disagreed. ``build`` now accepts an optional ``resolved_kind``
# keyword; a generator computes ``effective_kind(resolved_kind, KIND)`` once and threads the
# result into its artifact-JSON ``"kind"`` field instead of the bare module constant.
#
# DEGRADE-NEVER + TOTAL: a non-string or blank ``resolved_kind`` (a direct/legacy caller that
# does not thread it, a test, a ``build({})`` scaffold call) falls back to ``default`` (the
# generator's own module KIND) -- byte-identical to the pre-R-333 behavior. Nothing else about
# a generator's output (``output_sections`` / ``mold_id`` / titles / layouts) is touched.
# --------------------------------------------------------------------------- #
def effective_kind(resolved_kind: "Optional[str]", default: str) -> str:
    """The artifact-JSON ``kind`` a generator should embed (mission R-333).

    ``resolved_kind`` -- the PER-TENANT RESOLVED kind a caller already holds (threaded via
    ``build(..., resolved_kind=...)``), or None/absent.
    ``default`` -- the generator's own module ``KIND`` constant, used verbatim when
    ``resolved_kind`` is not a non-blank string.

    TOTAL: never raises. Returns ``default`` for anything that is not a non-blank string
    (None, "", whitespace-only, a non-string value)."""
    if isinstance(resolved_kind, str) and resolved_kind.strip():
        return resolved_kind.strip()
    return default


# --------------------------------------------------------------------------- #
# BRAND FRAME (mission BRAND_MUSTACHE) -- the helper every generator uses to brand-frame its
# output from the per-tenant brand context the run path injects into ``inputs``.
#
# The run path (cex_run_capability) resolves the unified brand context ONCE per run and stamps
# it onto a generator's inputs under the reserved ``brand_context`` key (the universal brand
# seam). A generator reads it via these helpers to make its titles/notes tenant-aligned -- the
# SAME generator, run for tenant X vs tenant Y, frames its output with X's vs Y's brand. The
# brand is NEVER hardcoded in a generator; it is filled per-tenant from this context.
#
# DEGRADE-NEVER + TOTAL: no brand_context (diffusion off / a neutral tenant) -> brand_name()
# returns "" and brand_frame_note()/brand_title() are no-ops that return their neutral input.
# So a generator that calls these is byte-identical for an un-branded run (zero-regression).
# --------------------------------------------------------------------------- #
def brand_context_of(inputs: "Mapping[str, Any]") -> Dict[str, Any]:
    """The per-tenant brand context dict the run path injected, or {} (TOTAL)."""
    if isinstance(inputs, Mapping):
        ctx = inputs.get("brand_context")
        if isinstance(ctx, Mapping):
            return dict(ctx)
    return {}


def brand_name_of(inputs: "Mapping[str, Any]") -> str:
    """The tenant brand name from the injected brand context, or "" (TOTAL). NEVER fabricates a
    name and NEVER hardcodes a brand -- "" means an un-branded run, and the caller stays neutral."""
    ctx = brand_context_of(inputs)
    name = ctx.get("brand_name")
    return name.strip() if isinstance(name, str) and name.strip() else ""


def brand_voice_register_of(inputs: "Mapping[str, Any]") -> str:
    """The tenant voice register from the injected brand context, or "" (TOTAL)."""
    ctx = brand_context_of(inputs)
    voice = ctx.get("brand_voice")
    if isinstance(voice, Mapping):
        reg = voice.get("register")
        if isinstance(reg, str) and reg.strip():
            return reg.strip()
    return ""


def brand_title(neutral_title: str, inputs: "Mapping[str, Any]") -> str:
    """Frame a section/output title with the tenant brand name when one is present.

    Branded   -> ``"<neutral_title> -- <brand_name>"`` (the SAME template, tenant-filled).
    Un-branded -> ``neutral_title`` unchanged (byte-identical; degrade-never).
    TOTAL: never raises; never fabricates a name."""
    name = brand_name_of(inputs)
    base = str(neutral_title)
    return "%s -- %s" % (base, name) if name else base


def brand_frame_note(inputs: "Mapping[str, Any]") -> Optional[str]:
    """An honest one-line brand-frame note for the tenant, or None when un-branded (TOTAL).

    e.g. ``"Personalizado para MARCA EXEMPLO -- voz: Comercial direto"``. Built ONLY from the injected
    context (name + optional voice register); NEVER fabricated. None -> the caller adds no note
    (byte-identical to a pre-mustache run)."""
    name = brand_name_of(inputs)
    if not name:
        return None
    register = brand_voice_register_of(inputs)
    if register:
        return "Personalizado para %s -- voz: %s" % (name, register)
    return "Personalizado para %s" % name


def structured_output(
    mold_id: str,
    output_sections: "List[Dict[str, Any]]",
    *,
    passed: bool,
    score: float,
    artifact: str = "",
    real: bool = True,
    notes: "Optional[List[str]]" = None,
    generator_version: Optional[str] = None,
    run_mode: Optional[str] = None,
    model_used: Optional[str] = None,
    confidence_breakdown: "Optional[Mapping[str, Any]]" = None,
    generated_at: Optional[str] = None,
    provenance: "Optional[List[Dict[str, Any]]]" = None,
) -> "StructuredOutput":
    """Assemble a complete StructuredOutput dict (the frozen return shape) + the universal
    metadata envelope (mission CAPABILITY_COMPLETENESS W1 -- see the block above).

    ``score`` is the generator's 0..1 self-assessment; the runtime seam scales it to the
    0..10 outcome strip. ``real=True`` makes the renderer drop the "dados simulados" chip.

    The envelope kwargs are ALL optional and default to honest, introspected values, so an
    EXISTING generator inherits the full envelope with NO call-site change. A generator MAY
    override any of them (e.g. an LLM generator passes ``run_mode`` + ``model_used`` at a real
    run; a generator that computed source agreement passes a richer ``confidence_breakdown``).
    """
    payload: Dict[str, Any] = {
        "mold_id": str(mold_id),
        "output_sections": list(output_sections or []),
        "real": bool(real),
        "passed": bool(passed),
        "score": float(score),
        "artifact": str(artifact or ""),
        "notes": [str(n) for n in (notes or [])],
    }

    # -- additive metadata envelope (NEW keys; never alters the frozen keys above) -------
    module = _caller_module()
    payload["generated_at"] = (
        str(generated_at) if generated_at is not None else _utc_now_iso()
    )
    payload["generator_version"] = (
        str(generator_version).strip()
        if generator_version
        else _module_const(module, ("GENERATOR_VERSION", "CONTRACT_VERSION"), DEFAULT_GENERATOR_VERSION)
    )
    payload["run_mode"] = (
        str(run_mode).strip()
        if run_mode
        else _module_const(module, ("RUN_MODE",), DEFAULT_RUN_MODE)
    )
    # NEVER-FABRICATE: a model id only when one was genuinely used; else null (offline).
    payload["model_used"] = str(model_used).strip() if model_used else None
    payload["confidence_breakdown"] = (
        dict(confidence_breakdown)
        if isinstance(confidence_breakdown, Mapping)
        else _default_confidence(payload["score"])
    )
    # ADDITIVE per-finding provenance (mission COMPLETE2 W2a).
    # Absent (None) -> no key stamped (backward-compat: existing consumers unchanged).
    if provenance is not None:
        try:
            payload["provenance"] = [dict(p) for p in provenance if isinstance(p, Mapping)]
        except Exception:
            payload["provenance"] = []
    return payload  # type: ignore[return-value]


# --------------------------------------------------------------------------- #
# OPTIONAL media hooks (mission DUAL2, Wave 3) -- the GENERIC media-discovery seam
# the run_capability path uses to feed cex_dual_output.to_dual_output.
#
# A generator opts into media by exposing, AT MODULE LEVEL, a pair of pure functions
# ``(inputs) -> media_requests`` and ``(inputs) -> produced_media`` (the to_dual_output
# args). This is ADDITIVE: a generator without them keeps working untouched (the run path
# falls back to one empty hero slot). No edit to any shared file is needed to add media to
# a NEW generator -- just the two functions in that generator's own file.
#
# Two naming conventions are supported (discovery is first-match-wins):
#   1. the CANONICAL unprefixed pair ``media_requests`` / ``produced_media`` (what a new
#      generator SHOULD use);
#   2. a PREFIXED pair ``<prefix>_media_requests`` / ``<prefix>_produced_media`` -- the
#      convention the two shipped generators already use (marketplace_listing's
#      ``listing_media_requests``/``listing_produced_media``; research's
#      ``research_media_requests``/``research_produced_media``).
#
# FAIL-SAFE + TOTAL: a missing module, a missing hook, a wrong-typed return, or a hook that
# RAISES degrades to None for that side -- the media layer NEVER breaks a capability run.
# --------------------------------------------------------------------------- #
_MEDIA_REQUESTS_SUFFIX = "_media_requests"
_MEDIA_PRODUCED_SUFFIX = "_produced_media"


def resolve_media(
    generator: "Callable[..., Any]",
    inputs: "Mapping[str, Any]",
) -> "tuple[Optional[List[Dict[str, Any]]], Optional[Dict[str, Any]]]":
    """Discover + invoke a generator's OPTIONAL media hooks.

    Returns ``(media_requests, produced_media)`` ready to pass to
    ``cex_dual_output.to_dual_output(cap, struct, media_requests=, produced_media=)``:
      * ``media_requests`` -- a list of slot requests {key, kind, section?, label?}, or None.
      * ``produced_media`` -- a {slot_key -> src|{"src","alt"}} map of ALREADY-produced media,
        or None. None on either side -> to_dual_output applies its own default (an empty
        upload-fallback hero slot) for that side; NEVER fabricated.

    GENERIC: no per-generator branching here -- discovery is by the naming convention above,
    keyed off the generator's own module. FAIL-SAFE + TOTAL: never raises.
    """
    mr_fn, pm_fn = _discover_media_hooks(generator)
    return _safe_call_media(mr_fn, inputs, list), _safe_call_media(pm_fn, inputs, dict)


def _discover_media_hooks(
    generator: "Callable[..., Any]",
) -> "tuple[Optional[Callable[..., Any]], Optional[Callable[..., Any]]]":
    """Find a generator module's (media_requests_fn, produced_media_fn), or (None, None).

    Order (first match wins): the canonical unprefixed pair, then a prefixed pair (scanned
    deterministically over sorted module attributes). TOTAL: any failure -> (None, None)."""
    module = _generator_module(generator)
    if module is None:
        return None, None

    # 1. canonical unprefixed hooks (what a new generator should expose).
    mr = _callable_attr(module, "media_requests")
    pm = _callable_attr(module, "produced_media")
    if mr is not None or pm is not None:
        return mr, pm

    # 2. a prefixed pair: <prefix>_media_requests / <prefix>_produced_media. Deterministic.
    try:
        names = sorted(dir(module))
    except Exception:
        return None, None
    for name in names:
        if name.endswith(_MEDIA_REQUESTS_SUFFIX):
            prefix = name[: -len(_MEDIA_REQUESTS_SUFFIX)]
            mr = _callable_attr(module, name)
            pm = _callable_attr(module, prefix + _MEDIA_PRODUCED_SUFFIX)
            if mr is not None or pm is not None:
                return mr, pm
    return None, None


def _generator_module(generator: "Callable[..., Any]") -> Optional[Any]:
    """Resolve the module object a generator callable is defined in. TOTAL: None on failure."""
    try:
        import sys

        mod_name = getattr(generator, "__module__", None)
        if mod_name and mod_name in sys.modules:
            return sys.modules[mod_name]
        import inspect

        return inspect.getmodule(generator)
    except Exception:
        return None


def _callable_attr(module: Any, name: str) -> Optional["Callable[..., Any]"]:
    """getattr(module, name) iff it is callable, else None. TOTAL."""
    try:
        fn = getattr(module, name, None)
        return fn if callable(fn) else None
    except Exception:
        return None


def _safe_call_media(
    fn: Optional["Callable[..., Any]"],
    inputs: "Mapping[str, Any]",
    expected: type,
) -> Optional[Any]:
    """Call a media hook with ``inputs`` and coerce the result to ``expected`` (list|dict).

    FAIL-SAFE: a None hook, a raising hook, or a wrong-typed return -> None (the slot side
    falls back to the to_dual_output default; never a fabricated value)."""
    if fn is None:
        return None
    try:
        result = fn(inputs)
    except Exception:
        return None
    if expected is list and isinstance(result, (list, tuple)):
        return list(result)
    if expected is dict and isinstance(result, Mapping):
        return dict(result)
    return None


__all__ = [
    "StructuredOutput",
    "register",
    "get_generator",
    "fields_section",
    "table_section",
    "list_section",
    "structured_output",
    "resolve_media",
    "make_provenance",
    "normalize_lead_row",
    # R-333: the resolved-kind helper (artifact-JSON self-description, see the block above).
    "effective_kind",
    # BRAND_MUSTACHE: the brand-frame helpers (read the per-tenant context the run path injects).
    "brand_context_of",
    "brand_name_of",
    "brand_voice_register_of",
    "brand_title",
    "brand_frame_note",
]
