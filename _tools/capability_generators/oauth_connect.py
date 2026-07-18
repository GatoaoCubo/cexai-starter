#!/usr/bin/env python3
# -*- coding: ascii -*-
"""oauth_connect -- typed OAuth app config generator (capability #12, owned by N03).

KIND = "oauth_app_config" (capability slug "oauth_connect"). A DETERMINISTIC typed-config
lane (Inventive Pride): 3 typed inputs -> 5 frozen output sections, PURE (no LLM, no
network, no clock). Ignores ``credential``.

CONTRACT BINDINGS (capability_contracts_v1.0.md section 12 + molds.ts MOLD_OAUTH_CONNECT):
  INPUT (input_contract):
    provider      : enum {mercadolivre, amazon, shopee, google}, required
    scopes        : enum[] {read, write, offline_access}, required
    redirect_uris : url[], required (prod MUST be https; localhost http only for dev)
  OUTPUT (output_sections, FROZEN order + layout):
    1. "Identidade do app"        fields  provider + client_id/secret as <SLOT: NAME> + Vault + grant_type
    2. "Invariantes de segredo"   fields  secret-never-rendered + legal slot form + Vault custody
    3. "Endpoints"                table   cols [Endpoint, URL], column_types [string, url], key_col_index 0
    4. "Token handling"           fields  access TTL/Bearer + refresh rotation + storage + revocation
    5. "Escopos"                  list    requested permissions (read / write / offline_access)

THE HARD INVARIANT (n03_validation -- the F7 gate). EVERY credential appears ONLY as a
<SLOT: NAME> token matching ^<SLOT: [A-Z0-9_]+>$ -- never a real value (Vault-per-tenant
custody). Endpoints are the provider's PUBLIC URLs (not secrets), resolved from a small
per-provider map. ``provider``/``scopes`` are CLOSED enums; a prod ``redirect_uri`` MUST
be https (http allowed only for localhost dev). contract_version 1.0.0.

For the canonical default input (mercadolivre + all scopes + the 2 example URIs) the
output is BYTE-EQUAL in shape AND data to molds.ts MOLD_OAUTH_CONNECT -- real config,
identical SHAPE.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Mapping, Optional, Tuple
from urllib.parse import urlsplit

from ._base import (
    StructuredOutput,
    brand_frame_note,
    brand_name_of,
    effective_kind,
    fields_section,
    list_section,
    register,
    structured_output,
    table_section,
)

KIND = "oauth_app_config"
CAPABILITY = "oauth_connect"  # council A4: the generator registers by SLUG, not KIND
CONTRACT_VERSION = "1.0.0"

# The legal form of a rendered secret (n03_validation secret-slot invariant). A credential
# VALUE must fullmatch this -- the real value is NEVER rendered (Vault-per-tenant custody).
_SLOT_RE = re.compile(r"^<SLOT: [A-Z0-9_]+>$")

# Closed provider enum -> public OAuth facts (NOT secrets): the slot prefix for this
# provider's credentials, the public authorization/token endpoints, and the documented
# access_token TTL. Endpoints + TTL are well-known PUBLIC values, resolved offline from
# this map (no network); they are not credentials and never carry a real secret.
_PROVIDERS: Dict[str, Dict[str, Any]] = {
    "mercadolivre": {
        "slot_prefix": "ML",
        "auth_url": "https://auth.mercadolivre.com.br/authorization",
        "token_url": "https://api.mercadolibre.com/oauth/token",
        "access_ttl_h": 6,
        "access_ttl_s": 21600,
    },
    "amazon": {
        "slot_prefix": "AMZN",
        "auth_url": "https://www.amazon.com/ap/oa",
        "token_url": "https://api.amazon.com/auth/o2/token",
        "access_ttl_h": 1,
        "access_ttl_s": 3600,
    },
    "shopee": {
        "slot_prefix": "SHOPEE",
        "auth_url": "https://partner.shopeemobile.com/api/v2/shop/auth_partner",
        "token_url": "https://partner.shopeemobile.com/api/v2/auth/token/get",
        "access_ttl_h": 4,
        "access_ttl_s": 14400,
    },
    "google": {
        "slot_prefix": "GOOGLE",
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "access_ttl_h": 1,
        "access_ttl_s": 3600,
    },
}
_PROVIDER_ENUM: Tuple[str, ...] = ("mercadolivre", "amazon", "shopee", "google")
_DEFAULT_PROVIDER = "mercadolivre"

# Closed scope enum -> the chip text rendered in the Escopos list section.
_SCOPE_ENUM: Tuple[str, ...] = ("read", "write", "offline_access")
_SCOPE_DESC: Dict[str, str] = {
    "read": "read -- ler anuncios, pedidos e perguntas",
    "write": "write -- criar/editar anuncios",
    "offline_access": "offline_access -- emite refresh_token (sessao longa)",
}

# Contract default redirect_uris (used when the caller supplies none) -- the example pair:
# one https prod callback + one http localhost dev callback. Tenant-neutral by design (this
# module is FROZEN_TOOLS_CORE, vendored byte-identical into every distilled tenant) -- the
# prod placeholder must never be any ONE real tenant's actual domain.
_DEFAULT_REDIRECT_URIS: List[str] = [
    "https://app.example.com/oauth/callback",
    "http://localhost:3000/oauth/callback",
]

# The single OAuth grant type this generator ever emits (n03_validation -- flow rule). Read
# by BOTH build() (identity section + artifact JSON) and domain_contract() below -- single
# source of truth, never a re-typed literal in either place.
_GRANT_TYPE = "authorization_code"

# The "Identidade do app" section note -- generic (no per-run data), so domain_contract()
# below reuses it verbatim as the credential-resolution LAW description. Read by BOTH build()
# and domain_contract() -- single source of truth.
_CLIENT_CREDENTIAL_CUSTODY_NOTE = (
    "client_id e client_secret sao <SLOT: NAME> resolvidos do Vault por tenant -- "
    "nenhum segredo real e gravado aqui nem no repo."
)

# The 2 STATIC (non-templated) "Invariantes de segredo" rows -- (label, value) pairs. The row
# NOT here (the slot-form example) is per-provider templated in build() with the resolved
# slot_secret; domain_contract() below exposes the GENERIC slot pattern for that one instead
# (_SLOT_RE.pattern) rather than duplicating one provider's worked example. Read by BOTH
# build() and domain_contract() below -- single source of truth, never a re-typed literal.
_SECRET_INVARIANT_STATIC_ROWS: Tuple[Tuple[str, str], ...] = (
    ("client_secret nunca renderizado",
     "Apenas a forma <SLOT: NAME> aparece -- o valor real nunca e exibido nem logado."),
    ("custodia",
     "Vault por tenant -- resolvido em runtime, fora do contrato e fora do cliente."),
)


def _resolve_provider(raw: Any) -> Tuple[str, bool, bool]:
    """Return (provider, was_absent, is_invalid).

    Absent/empty -> the contract default (degrade-never; the scaffold still renders). A
    PRESENT value outside the closed enum is a HARD rejection (is_invalid True) but still
    renders a scaffold under the default provider so build() never crashes."""
    val = str(raw).strip().lower() if raw is not None else ""
    if val == "":
        return _DEFAULT_PROVIDER, True, False
    if val in _PROVIDERS:
        return val, False, False
    return _DEFAULT_PROVIDER, False, True


def _coerce_str_list(raw: Any) -> List[str]:
    """Normalise a list-or-delimited-string input to an ordered list of non-empty strings.

    Accepts a list/tuple OR a comma/newline-separated string (free-text fallback).
    DEGRADE-NEVER: never raises on a malformed value (returns [])."""
    if isinstance(raw, (list, tuple)):
        return [str(x).strip() for x in raw if str(x).strip()]
    if isinstance(raw, str) and raw.strip():
        return [p.strip() for p in raw.replace("\n", ",").split(",") if p.strip()]
    return []


def _resolve_scopes(raw: Any) -> Tuple[List[str], List[str], bool]:
    """Return (valid_scopes_in_canonical_order, invalid_scopes, was_absent).

    Absent -> the full closed set (degrade-never). PRESENT elements outside the enum are
    reported (the caller fails the gate) and dropped from the rendered set. The valid set
    is emitted in canonical enum order for a deterministic, stable output."""
    supplied = _coerce_str_list(raw)
    if not supplied:
        return list(_SCOPE_ENUM), [], True
    sset = {s.lower() for s in supplied}
    valid = [s for s in _SCOPE_ENUM if s in sset]
    invalid = [s for s in supplied if s.lower() not in _SCOPE_ENUM]
    return valid, invalid, False


def _classify_uri(uri: Any) -> Tuple[str, bool, str]:
    """Classify a redirect URI -> (kind, valid, reason). Pure/offline (urlsplit, no network).

    kind in {"prod","dev","invalid"}. Rule (n03_validation url-validity): scheme in
    {http,https} AND non-empty host; https => prod (ok); http => ok ONLY for localhost
    (dev); http on a non-localhost host => invalid (production MUST be https)."""
    s = str(uri).strip()
    if s == "":
        return "invalid", False, "URI vazia"
    try:
        parts = urlsplit(s)
    except Exception:
        return "invalid", False, "URL malformada"
    scheme = (parts.scheme or "").lower()
    try:
        host = (parts.hostname or "").lower()
    except Exception:
        return "invalid", False, "host invalido"
    if scheme not in ("http", "https") or host == "":
        return "invalid", False, "esquema deve ser http/https com host nao-vazio"
    is_localhost = host == "localhost" or host == "127.0.0.1" or host.endswith(".localhost")
    if scheme == "https":
        return "prod", True, ""
    if is_localhost:
        return "dev", True, ""
    return "invalid", False, "http nao-localhost: producao DEVE ser https"


def _resolve_redirects(raw: Any) -> Tuple[List[Tuple[str, str]], List[str], bool]:
    """Return (valid_rows, rejected_notes, was_absent).

    valid_rows = [(label, url), ...] for the Endpoints table -- only VALID absolute URLs,
    so every url cell conforms to column_types[1]=="url". Labels mirror the mock: a prod
    entry -> "redirect_uri (prod)", a dev entry -> "redirect_uri (dev)", disambiguated by
    an index when there is more than one of a kind. Rejected URIs are reported, NOT placed
    in the table (keeping the url column conformant)."""
    uris = _coerce_str_list(raw)
    was_absent = not uris
    if was_absent:
        uris = list(_DEFAULT_REDIRECT_URIS)
    valid_rows: List[Tuple[str, str]] = []
    rejected: List[str] = []
    prod_n = 0
    dev_n = 0
    for u in uris:
        kind, ok, reason = _classify_uri(u)
        if not ok:
            rejected.append("%s (%s)" % (u, reason))
            continue
        if kind == "prod":
            prod_n += 1
            label = "redirect_uri (prod)" if prod_n == 1 else "redirect_uri (prod %d)" % prod_n
        else:
            dev_n += 1
            label = "redirect_uri (dev)" if dev_n == 1 else "redirect_uri (dev %d)" % dev_n
        valid_rows.append((label, u))
    return valid_rows, rejected, was_absent


def _slot(prefix: str, suffix: str) -> str:
    """Build a credential SLOT token (never a real value): ``<SLOT: PREFIX_SUFFIX>``."""
    return "<SLOT: %s_%s>" % (prefix, suffix)


def _table_conformant(columns: List[str], column_types: List[str],
                      key_col_index: int, rows: List[List[Any]]) -> bool:
    """n03_validation sec.4 + 5b: column_types 1:1 with columns, key_col in range, every
    row has columns.length cells, row[0] is a string, row[1] is a valid absolute URL."""
    if len(column_types) != len(columns):
        return False
    if not (0 <= key_col_index < len(columns)):
        return False
    for row in rows:
        if len(row) != len(columns):
            return False
        if not isinstance(row[0], str):
            return False
        _, ok, _ = _classify_uri(row[1])
        if not ok:
            return False
    return True


def _artifact(provider: str, scopes: List[str], redirect_rows: List[Tuple[str, str]],
              prov: Dict[str, Any], slot_id: str, slot_secret: str, kind: str = KIND) -> str:
    """A compact, ASCII-safe JSON projection of the produced config (for persist/results).

    Carries the secrets ONLY as their SLOT tokens -- never a real value."""
    projection = {
        "kind": kind,
        "contract_version": CONTRACT_VERSION,
        "provider": provider,
        "scopes": list(scopes),
        "redirect_uris": [u for (_, u) in redirect_rows],
        "endpoints": {"auth_url": prov["auth_url"], "token_url": prov["token_url"]},
        "client_id_slot": slot_id,
        "client_secret_slot": slot_secret,
        "grant_type": _GRANT_TYPE,
    }
    try:
        return json.dumps(projection, ensure_ascii=True, sort_keys=True)
    except Exception:
        return "{}"


@register(CAPABILITY)  # council A4: SLUG is the sole generator key (was KIND=oauth_app_config)
def build(
    inputs: Mapping[str, Any], *, credential: "Optional[Any]" = None,
    resolved_kind: Optional[str] = None,
) -> "StructuredOutput":
    """Produce the REAL oauth_app_config structured output (deterministic; ignores credential).

    Reads provider / scopes / redirect_uris from ``inputs`` (defaulting absent required
    fields from the contract); emits the 5 frozen output sections with REAL data computed
    from the inputs + the per-provider public endpoint map; self-checks the secret-SLOT
    invariant, table conformance and enum/url validity in F7. Never raises (degrade-never).

    ``resolved_kind`` (mission R-333): the PER-TENANT RESOLVED kind the caller
    (cex_run_capability) already holds, embedded verbatim into the artifact JSON
    self-description instead of the module KIND constant. None/blank falls back to KIND."""
    notes: List[str] = []
    _kind = effective_kind(resolved_kind, KIND)
    violations = 0  # each present-but-invalid enum/url is a HARD gate failure (passed=False)

    # BRAND_MUSTACHE: frame the OAuth config for THIS tenant from the brand context the run path
    # injected. The secret-SLOT invariant + every row VALUE stay UNTOUCHED (the F7 gate +
    # test_capgen_n03 assert exact row values like client_id_origem=="Vault por tenant"); the
    # brand rides ONLY an ADDITIVE clause appended to the "Identidade do app" section NOTE.
    # Un-branded -> no note delta (byte-identical; degrade-never). NEVER hardcodes the brand.
    brand_name = brand_name_of(inputs)  # noqa: F841  (reserved for future row-level framing)
    _bnote = brand_frame_note(inputs)
    if _bnote:
        notes.append(_bnote)

    # -- F1 parse + validate inputs (default absent REQUIRED fields from the contract). ----
    provider, prov_absent, prov_invalid = _resolve_provider(inputs.get("provider"))
    if prov_absent:
        notes.append("provider ausente; usando o default '%s'" % _DEFAULT_PROVIDER)
    if prov_invalid:
        violations += 1
        notes.append(
            "provider '%s' nao e membro de %s; rejeitado (scaffold sob '%s')"
            % (str(inputs.get("provider")).strip(), list(_PROVIDER_ENUM), _DEFAULT_PROVIDER)
        )
    prov = _PROVIDERS[provider]
    prefix = prov["slot_prefix"]
    slot_id = _slot(prefix, "CLIENT_ID")
    slot_secret = _slot(prefix, "CLIENT_SECRET")

    scopes, invalid_scopes, scopes_absent = _resolve_scopes(inputs.get("scopes"))
    if scopes_absent:
        notes.append("scopes ausente; usando o default %s" % list(_SCOPE_ENUM))
    if invalid_scopes:
        violations += 1
        notes.append("scopes fora do enum %s: %s (rejeitados)"
                     % (list(_SCOPE_ENUM), invalid_scopes))
    if not scopes:
        scopes = list(_SCOPE_ENUM)
        notes.append("nenhum scope valido; usando o default %s para o scaffold"
                     % list(_SCOPE_ENUM))

    redirect_rows, rejected_uris, uris_absent = _resolve_redirects(inputs.get("redirect_uris"))
    if uris_absent:
        notes.append("redirect_uris ausente; usando o default (1 prod https + 1 dev localhost)")
    if rejected_uris:
        violations += 1
        for r in rejected_uris:
            notes.append("redirect_uri rejeitada -- %s" % r)
    has_offline = "offline_access" in scopes

    # -- F6 produce: the 5 frozen sections, REAL data from inputs + the per-provider map. --
    _identity_note = _CLIENT_CREDENTIAL_CUSTODY_NOTE
    if _bnote:
        _identity_note = "%s %s" % (_identity_note, _bnote)
    sec_identity = fields_section(
        "Identidade do app",
        [
            ("provider", provider),
            ("client_id", slot_id),
            ("client_secret", slot_secret),
            ("client_id_origem", "Vault por tenant"),
            ("client_secret_origem", "Vault por tenant"),
            ("grant_type", _GRANT_TYPE),
        ],
        note=_identity_note,
    )
    sec_secret = fields_section(
        "Invariantes de segredo",
        [
            _SECRET_INVARIANT_STATIC_ROWS[0],
            ("forma legal de um segredo",
             "Tem que casar %s (ex.: %s)." % (_SLOT_RE.pattern, slot_secret)),
            _SECRET_INVARIANT_STATIC_ROWS[1],
        ],
        note="Contrato de seguranca explicito: o que pode e o que nunca pode aparecer renderizado.",
    )
    endpoint_columns = ["Endpoint", "URL"]
    endpoint_types = ["string", "url"]
    endpoint_rows: List[List[Any]] = [
        ["auth_url", prov["auth_url"]],
        ["token_url", prov["token_url"]],
    ]
    for (label, url) in redirect_rows:
        endpoint_rows.append([label, url])
    sec_endpoints = table_section(
        "Endpoints",
        endpoint_columns,
        endpoint_rows,
        column_types=endpoint_types,
        key_col_index=0,
        note="URLs publicas do provedor (%s) -- nao sao segredos. Coluna URL e do tipo url "
             "(absoluta)." % provider,
    )
    if has_offline:
        refresh_text = ("Rotacionado a cada uso; requer scope offline_access; o token anterior "
                        "e invalidado na troca.")
    else:
        refresh_text = "Indisponivel -- requer o scope offline_access (nao solicitado)."
    sec_token = fields_section(
        "Token handling",
        [
            ("access_token", "TTL ~%dh (%d s); Bearer no header Authorization."
             % (prov["access_ttl_h"], prov["access_ttl_s"])),
            ("refresh_token", refresh_text),
            ("storage", "Vault por tenant -- nunca no cliente, nunca no repo."),
            ("revocation",
             "Revogar limpa os <SLOT: NAME> do Vault do tenant e invalida access+refresh."),
        ],
        note="Ciclo de vida tipado do token -- ttl, rotacao, armazenamento e revogacao.",
    )
    sec_scopes = list_section(
        "Escopos",
        [_SCOPE_DESC[s] for s in scopes],
        note="Permissoes solicitadas ao provedor (conjunto fechado read/write/offline_access).",
    )
    output_sections = [sec_identity, sec_secret, sec_endpoints, sec_token, sec_scopes]

    # -- F7 govern: secret-slot invariant + table conformance + enum/url validity. ----------
    slot_ok = bool(_SLOT_RE.fullmatch(slot_id)) and bool(_SLOT_RE.fullmatch(slot_secret))
    table_ok = _table_conformant(endpoint_columns, endpoint_types, 0, endpoint_rows)
    sections_ok = all(
        bool(s.get("rows") or s.get("table") or s.get("items")) for s in output_sections
    )
    if not slot_ok:
        violations += 1
        notes.append("INVARIANTE quebrada: um segredo nao casa ^<SLOT: [A-Z0-9_]+>$")
    if not table_ok:
        violations += 1
        notes.append("Endpoints fora de conformidade (column_types / url / largura de linha)")
    notes.append("endpoints + token TTL resolvidos do mapa publico por provedor (nao segredos)")
    notes.append("invariante de segredo: client_id/secret apenas como <SLOT: NAME> (Vault por tenant)")

    score = 1.0 - 0.2 * violations
    if score < 0.0:
        score = 0.0
    passed = bool(violations == 0 and slot_ok and table_ok and sections_ok and score >= 0.8)

    return structured_output(
        KIND,
        output_sections,
        passed=passed,
        score=score,
        artifact=_artifact(provider, scopes, redirect_rows, prov, slot_id, slot_secret, kind=_kind),
        real=True,
        notes=notes,
    )


# --------------------------------------------------------------------------- #
# Domain contract (Missao A / MOLDED_REAL_SEAM export-deepening) -- the REAL domain law
# this generator enforces, exposed for cex_export_agent.py to bake into an exported agent
# package (system_instruction GROUNDING + a new knowledge/domain_contract.md bundle file)
# instead of a generic ISO-scaffold. Discovered via capability_generators._base.
# get_domain_contract (module-level convention -- see that function's docstring).
#
# SINGLE SOURCE OF TRUTH: every value below is a REFERENCE to the SAME module constant (or,
# for the redirect-URI rule, the SAME function's own docstring) build() reads/documents
# above -- never a re-typed literal -- so an exported bundle can never drift from what
# build() actually enforces at runtime. Only the CONTAINER shape changes (e.g. the
# _PROVIDERS dict-of-dicts becomes a list of per-provider row dicts) so the generic
# markdown renderer in cex_export_agent.py (_render_domain_contract_body) produces a clean
# table -- the leaf values themselves are never retyped.
#
# LAW vs SCAFFOLD (founder policy 2026-07-18): every key below is either real domain LAW
# (enforced on every real run, degrade-never) or this generator's own deterministic
# SCAFFOLD content (the fallback used only when the caller omits an optional input) -- the
# `default_*_when_unspecified` keys are scaffold, everything else is law. NO secret VALUE is
# ever exposed here -- only the RULE (e.g. the slot-form regex); client_id/client_secret
# never appear as anything but the <SLOT: NAME> form even in build()'s own output, and this
# contract carries no per-run slot example at all (just the generic pattern).
# --------------------------------------------------------------------------- #
def domain_contract() -> dict:
    """The REAL domain law oauth_connect.py enforces on every generated oauth_app_config
    (Missao A). Returns a structured, JSON-serialisable dict -- never {} for THIS generator
    (oauth_connect DOES declare domain law: the closed provider/scope enums + each
    provider's public OAuth endpoints/TTL, the single grant type, the secret-slot rendering
    invariant + its 2 static security rules, the credential-custody rule, and the
    redirect-URI security rule; {} is only the _base.py no-op default for a generator with
    none)."""
    return {
        "contract_version": CONTRACT_VERSION,
        "supported_providers": [
            {
                "provider": name,
                "slot_prefix": prov["slot_prefix"],
                "auth_url": prov["auth_url"],
                "token_url": prov["token_url"],
                "access_ttl_h": prov["access_ttl_h"],
                "access_ttl_s": prov["access_ttl_s"],
            }
            for name, prov in _PROVIDERS.items()
        ],
        "enums": {
            "provider": list(_PROVIDER_ENUM),
            "scope": list(_SCOPE_ENUM),
        },
        "scope_descriptions": dict(_SCOPE_DESC),
        "grant_type": _GRANT_TYPE,
        "secret_slot_pattern": _SLOT_RE.pattern,
        "secret_invariant_rules": [
            {"rule": label, "detail": detail}
            for (label, detail) in _SECRET_INVARIANT_STATIC_ROWS
        ],
        "credential_resolution_note": _CLIENT_CREDENTIAL_CUSTODY_NOTE,
        "redirect_uri_security_rule": " ".join((_classify_uri.__doc__ or "").split()),
        "default_provider_when_unspecified": _DEFAULT_PROVIDER,
        "default_redirect_uris_when_unspecified": list(_DEFAULT_REDIRECT_URIS),
    }


__all__ = [
    "KIND",
    "CAPABILITY",
    "CONTRACT_VERSION",
    "build",
    # Missao A / MOLDED_REAL_SEAM: the real domain-law contract (cex_export_agent.py).
    "domain_contract",
]
