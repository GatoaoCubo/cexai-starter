#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI B2B firmographics enrichment -- cex_cnpj_enrich (research-universe B2B lane).

THE CNPJ Enrichment Pass. CEXAI's research universe (memory:
reference_research_universe_taxonomy) flags B2B firmographics as a GREEN, ownable Brazilian
edge: official government registry data, no key, no scraping. This module enriches ONE (or a
list of) Brazilian company CNPJ via the BrasilAPI CNPJ endpoint -- a thin, honest read of the
Receita Federal cadastro: razao social, situacao cadastral, CNAE (primary + secondary),
natureza juridica, porte, capital social, address, the QSA partner roster, and contacts.

  GET https://brasilapi.com.br/api/cnpj/v1/{cnpj}   (no key, 30s timeout)

  Fallback (NOT required, documented for the operator): BrasilAPI proxies the open-source
  "minha-receita" project (https://github.com/cuducos/minha-receita). A self-host of that
  service exposes the SAME shape at POST {your_host}/{cnpj}. This module does NOT call it and
  does NOT depend on it -- it is recorded here only so a future operator knows the swap path
  (set CEX_CNPJ_BASE to a self-host base to point this tool at it).

CARDINAL RULE -- NEVER fabricate. Every field is captured-AND-real or an honest ``null`` with
provenance. We map ONLY the fields BrasilAPI actually returns (shape live-verified 2026-06-19
against CNPJ 00.000.000/0001-91 Banco do Brasil); an absent/empty field is None, NEVER a guessed
CNAE, NEVER an invented partner. enrich_cnpj is TOTAL: it NEVER raises -- a malformed CNPJ, a 404
(CNPJ not found), a timeout, or a blocked/garbled body all yield a complete dict with honest nulls
+ a recorded ``endpoint_status`` (the failure reason is the EXCEPTION TYPE NAME only -- the
response body is NEVER echoed, so a sensitive/garbled payload can never leak into a log or error).

SECURITY -- CNPJ format-validated BEFORE the URL is built (anti-injection). The CNPJ is the ONLY
caller-controlled value interpolated into the request path. It is stripped to digits and must be
EXACTLY 14 digits (re.fullmatch) BEFORE ``_CNPJ_BASE + "/" + cnpj`` is assembled. A value that
fails validation (13 digits, alpha, '123/../x') is REJECTED -- the HTTP seam is NEVER called and
the record is an honest 'invalid_cnpj' status. This is the cybersec lesson (memory:
project_cybersec_extraction_harness): never interpolate an unvalidated value into a URL.

ASCII-only (.claude/rules/ascii-code-rule.md). Fully type-hinted. Pure/total; modifies nothing.

Live proof (the orchestrator runs this -- real network, GREEN open data, no key):
  python _tools/cex_cnpj_enrich.py 00.000.000/0001-91
  python _tools/cex_cnpj_enrich.py 00000000000191
"""

from __future__ import annotations

import json
import os
import re as _re
import sys
from typing import Any, Dict, List, Mapping, Optional

# The BrasilAPI CNPJ base (GREEN: official Receita cadastro via the open minha-receita proxy, no
# key). Overridable via CEX_CNPJ_BASE for a self-host of minha-receita (documented above); the
# default is the public BrasilAPI host. The CNPJ (14 validated digits) is appended as the path
# segment AFTER validation -- never before.
_CNPJ_BASE = (os.environ.get("CEX_CNPJ_BASE") or "https://brasilapi.com.br/api/cnpj/v1").rstrip("/")

# The degrade-never HTTP ceiling (per the spec: 30s). A slow/hung registry must not hang the run.
_HTTP_TIMEOUT = 30

# SECURITY (anti-injection): a CNPJ is EXACTLY 14 digits. This strict full-match gate runs on the
# digits-only form BEFORE the value is interpolated into the request path. Compiled once (ASCII).
_RE_CNPJ_14 = _re.compile(r"\d{14}")

# A reusable error reason for the rejected-format case (no body, no value echoed).
_INVALID_REASON = "invalid_cnpj: expected 14 digits after stripping non-digits"


# --------------------------------------------------------------------------- #
# Errors / status sentinels (NO response body ever carried -- only a type name).
# --------------------------------------------------------------------------- #
class CnpjUnavailable(RuntimeError):
    """Raised INTERNALLY by _cnpj_get on an HTTP/transport error so enrich_cnpj can record an
    honest per-call failure. enrich_cnpj catches it (degrade-never) -> all fields stay null.
    Carries NO secret and NO response body -- only the failing exception TYPE NAME string."""


# --------------------------------------------------------------------------- #
# CNPJ normalization + the anti-injection validator.
# --------------------------------------------------------------------------- #
def normalize_cnpj(value: Any) -> Optional[str]:
    """Strip a CNPJ to its 14 digits and validate the format, or return None. PURE + TOTAL.

    Accepts the common human forms ('00.000.000/0001-91', '00000000000191', with stray spaces)
    by removing EVERY non-digit, then requires the result to be EXACTLY 14 digits (re.fullmatch).
    A 13-digit value, an alpha string, an injection like '123/../x', a non-string, or None ->
    None (the caller then records 'invalid_cnpj' and NEVER builds the URL). This is the
    anti-injection gate: nothing but a clean 14-digit id can ever reach the request path."""
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        return None
    digits = _re.sub(r"\D", "", str(value))
    return digits if _RE_CNPJ_14.fullmatch(digits) else None


# --------------------------------------------------------------------------- #
# THE HTTP seam (the single place a test monkeypatches). Lazy requests import.
# --------------------------------------------------------------------------- #
def _cnpj_get(cnpj14: str) -> Any:
    """GET the BrasilAPI CNPJ body for a PRE-VALIDATED 14-digit CNPJ; return the parsed JSON.

    PRECONDITION: cnpj14 is exactly 14 digits (the caller validated it via normalize_cnpj BEFORE
    calling here -- this function does NOT re-fetch-or-trust an unvalidated value). The id is
    interpolated into the path only after that gate.

    RAISES CnpjUnavailable on ANY HTTP / transport error (a 404 'CNPJ nao encontrado', a 429, a
    5xx, a timeout, a network drop) so the caller records an honest failure and degrades to null
    fields. The error message is the EXCEPTION TYPE NAME only -- the response body is NEVER read
    into the message (a garbled/sensitive payload can never leak). NEVER fabricates a body."""
    import requests  # type: ignore[import]  # lazy (keeps import-time offline-friendly)

    url = "%s/%s" % (_CNPJ_BASE, cnpj14)
    try:
        resp = requests.get(
            url,
            headers={"Accept": "application/json", "User-Agent": "cexai-cnpj-enrich/1.0"},
            timeout=_HTTP_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        # NEVER echo the response body or the full URL with the id -- only the error TYPE name.
        raise CnpjUnavailable(type(exc).__name__) from exc


# --------------------------------------------------------------------------- #
# THE entry -- enrich ONE CNPJ.
# --------------------------------------------------------------------------- #
def enrich_cnpj(cnpj: Any, now: Optional[str] = None) -> Dict[str, Any]:
    """Enrich ONE Brazilian company CNPJ via BrasilAPI. TOTAL: NEVER raises, NEVER fabricates.

    Flow: validate the CNPJ format (anti-injection) -> GET BrasilAPI -> map ONLY the fields the
    API actually returns onto the firmographics contract. A bad format, a 404, a timeout, or a
    non-mapping body -> every field stays an honest ``null`` and the failure is recorded in
    ``endpoint_status`` (reason = exception type name; the body is never echoed).

    Args:
      cnpj: a CNPJ in any common form ('00.000.000/0001-91' or '00000000000191'); stripped to
        digits and format-validated BEFORE any URL is built.
      now: an OPTIONAL caller-supplied ISO-8601 timestamp for ``fetched_at`` provenance. When
        None it is left None (this function does NOT call the clock -- the caller stamps it so the
        result is deterministic/testable). NEVER a fabricated time.

    Returns a dict with the contract fields (all honest-null when unavailable):
      cnpj, razao_social, nome_fantasia,
      situacao_cadastral (the human label, e.g. 'ATIVA'), situacao_cadastral_codigo (the raw code),
      cnae_principal (+ cnae_principal_descricao), cnaes_secundarios (list of {codigo, descricao}),
      natureza_juridica, porte, capital_social, data_inicio_atividade,
      endereco ({logradouro, numero, municipio, uf, cep}),
      socios (list of {nome, qualificacao}), telefones (list), email,
      data_sources (provenance), endpoint_status (ok|invalid_cnpj|failed:<type>), fetched_at,
      mock (ALWAYS False -- real API data or an explicit null, never a simulated value)."""
    rec = _empty_record(now)

    cnpj14 = normalize_cnpj(cnpj)
    if cnpj14 is None:
        # Anti-injection gate tripped: the value never reaches the URL. Honest rejection.
        rec["endpoint_status"]["cnpj"] = _INVALID_REASON
        return rec
    rec["cnpj"] = cnpj14  # the validated, digits-only id (echoed; the input punctuation is dropped)

    try:
        body = _cnpj_get(cnpj14)
    except CnpjUnavailable as exc:
        # Degrade-never: a 404 (CNPJ not found) / timeout / 5xx -> all fields stay null; record the
        # reason as the exception type name only (NEVER the response body).
        rec["endpoint_status"]["cnpj"] = "failed: %s" % (str(exc) or "unavailable")
        return rec
    except Exception as exc:  # defensive: nothing from the seam may crash the record.
        rec["endpoint_status"]["cnpj"] = "failed: %s" % type(exc).__name__
        return rec

    if not isinstance(body, Mapping):
        # A 200 with a non-object body (unexpected) -> honest null, never coerced.
        rec["endpoint_status"]["cnpj"] = "failed: non_mapping_body"
        return rec

    _apply_body(rec, body)
    rec["endpoint_status"]["cnpj"] = "ok"
    rec["data_sources"]["cnpj"] = "brasilapi:cnpj"
    return rec


def enrich_cnpjs(cnpjs: Any, now: Optional[str] = None) -> List[Dict[str, Any]]:
    """Enrich a LIST of CNPJs (each via enrich_cnpj). TOTAL: a non-iterable / empty input -> [];
    every element is enriched independently (one bad id never aborts the batch). NEVER raises.

    The same ``now`` provenance stamp is applied to every record (a single batch read). Each
    element is honest-null + status-recorded on its own; ordering follows the input."""
    if isinstance(cnpjs, (str, bytes)) or not _is_iterable(cnpjs):
        return []
    out: List[Dict[str, Any]] = []
    for item in cnpjs:
        out.append(enrich_cnpj(item, now=now))
    return out


# --------------------------------------------------------------------------- #
# Body -> contract mapper. PURE (NEVER fabricate; absent/empty -> None).
# --------------------------------------------------------------------------- #
def _apply_body(rec: Dict[str, Any], body: Mapping[str, Any]) -> None:
    """Map a BrasilAPI CNPJ body onto the firmographics contract. Reads ONLY documented fields
    (shape live-verified). Each absent/blank field stays None (honest). NEVER fabricates.

    Field map (BrasilAPI key -> contract field):
      razao_social            -> razao_social
      nome_fantasia           -> nome_fantasia
      descricao_situacao_cadastral -> situacao_cadastral (human label, e.g. 'ATIVA')
      situacao_cadastral      -> situacao_cadastral_codigo (the raw numeric/string code)
      cnae_fiscal             -> cnae_principal
      cnae_fiscal_descricao   -> cnae_principal_descricao
      cnaes_secundarios[]     -> cnaes_secundarios (each {codigo, descricao})
      natureza_juridica       -> natureza_juridica
      porte                   -> porte
      capital_social          -> capital_social (numeric passthrough; never re-derived)
      data_inicio_atividade   -> data_inicio_atividade
      logradouro/numero/municipio/uf/cep -> endereco{...}
      qsa[]                   -> socios (each {nome: nome_socio, qualificacao: qualificacao_socio})
      ddd_telefone_1/_2       -> telefones[] (blank dropped -- never a fabricated number)
      email                   -> email
    """
    rec["razao_social"] = _opt_str(body.get("razao_social"))
    rec["nome_fantasia"] = _opt_str(body.get("nome_fantasia"))

    # situacao: the human label is descricao_situacao_cadastral ('ATIVA'); the raw code is
    # situacao_cadastral (e.g. 2). Capture BOTH honestly -- the contract field is the label.
    rec["situacao_cadastral"] = _opt_str(body.get("descricao_situacao_cadastral"))
    rec["situacao_cadastral_codigo"] = _opt_str(body.get("situacao_cadastral"))

    rec["cnae_principal"] = _opt_str(body.get("cnae_fiscal"))
    rec["cnae_principal_descricao"] = _opt_str(body.get("cnae_fiscal_descricao"))
    rec["cnaes_secundarios"] = _cnaes_list(body.get("cnaes_secundarios"))

    rec["natureza_juridica"] = _opt_str(body.get("natureza_juridica"))
    rec["porte"] = _opt_str(body.get("porte"))
    rec["capital_social"] = _opt_number(body.get("capital_social"))
    rec["data_inicio_atividade"] = _opt_str(body.get("data_inicio_atividade"))

    rec["endereco"] = {
        "logradouro": _opt_str(body.get("logradouro")),
        "numero": _opt_str(body.get("numero")),
        "municipio": _opt_str(body.get("municipio")),
        "uf": _opt_str(body.get("uf")),
        "cep": _opt_str(body.get("cep")),
    }

    rec["socios"] = _socios_list(body.get("qsa"))
    rec["telefones"] = _telefones_list(body)
    rec["email"] = _opt_str(body.get("email"))


# --------------------------------------------------------------------------- #
# PURE list normalizers (TOTAL -- non-list / junk -> []; NEVER fabricate an entry).
# --------------------------------------------------------------------------- #
def _cnaes_list(value: Any) -> List[Dict[str, Any]]:
    """Normalize cnaes_secundarios[] into a list of {codigo, descricao}. A non-list -> []. An
    entry with neither a code nor a description is dropped (never fabricated). BrasilAPI sometimes
    emits a single placeholder {codigo: -1, descricao: 'Nao informada'} -> that is dropped (it is
    an explicit no-data marker, not a real secondary CNAE)."""
    if not isinstance(value, list):
        return []
    out: List[Dict[str, Any]] = []
    for e in value:
        if not isinstance(e, Mapping):
            continue
        codigo = _opt_number(e.get("codigo"))
        descricao = _opt_str(e.get("descricao"))
        if codigo is None and descricao is None:
            continue
        # Drop the BrasilAPI "no secondary CNAE" placeholder (codigo -1) -- it is not a real entry.
        if codigo == -1:
            continue
        out.append({"codigo": codigo, "descricao": descricao})
    return out


def _socios_list(value: Any) -> List[Dict[str, Any]]:
    """Normalize the QSA (quadro de socios e administradores) into [{nome, qualificacao}]. A
    non-list -> []. The name key is 'nome_socio'; the role key is 'qualificacao_socio'. An entry
    with no name is dropped (a partner with no name is never fabricated). We intentionally do NOT
    surface the masked CPF/CNPJ field -- it is PII and not needed for firmographics."""
    if not isinstance(value, list):
        return []
    out: List[Dict[str, Any]] = []
    for e in value:
        if not isinstance(e, Mapping):
            continue
        nome = _opt_str(e.get("nome_socio")) or _opt_str(e.get("nome"))
        if nome is None:
            continue  # no name -> drop (never invent a partner).
        qualificacao = _opt_str(e.get("qualificacao_socio")) or _opt_str(e.get("qualificacao"))
        out.append({"nome": nome, "qualificacao": qualificacao})
    return out


def _telefones_list(body: Mapping[str, Any]) -> List[str]:
    """Collect the registry phone numbers (ddd_telefone_1, ddd_telefone_2) into a de-duped list.
    BrasilAPI returns these as digit strings already DDD-prefixed (e.g. '6134939002'); a blank/''
    value (common for the 2nd line) is dropped -- never a fabricated number. Absent -> []."""
    out: List[str] = []
    for key in ("ddd_telefone_1", "ddd_telefone_2"):
        tel = _opt_str(body.get(key))
        if tel is not None and tel not in out:
            out.append(tel)
    return out


# --------------------------------------------------------------------------- #
# PURE scalar helpers (TOTAL -- absent/garbage -> None; NEVER fabricate).
# --------------------------------------------------------------------------- #
def _opt_str(value: Any) -> Optional[str]:
    """A non-empty stripped string, or None. An int/float (e.g. cnae_fiscal=6422100,
    situacao_cadastral=2) is stringified so it surfaces honestly. A bool is NOT a string here.
    An empty/whitespace string -> None (the blank ddd_telefone_2 / email='' cases). TOTAL."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, str):
        s = value.strip()
        return s or None
    if isinstance(value, (int, float)):
        return str(value)
    return None


def _opt_number(value: Any) -> Optional[float]:
    """A real numeric value (int/float), or None. Used for capital_social + the CNAE codigo. A
    bool is excluded (isinstance(True, int) is True -- a crafted bool must not become 1). A numeric
    STRING ('120000000000') is parsed; anything non-numeric -> None (never a fabricated number).
    An integral float is returned as an int so the JSON is clean ('120000000000' not '1.2e11')."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else value
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        try:
            f = float(s)
        except (TypeError, ValueError):
            return None
        return int(f) if f.is_integer() else f
    return None


def _is_iterable(value: Any) -> bool:
    """True if value can be iterated (list/tuple/set/generator), else False. TOTAL."""
    try:
        iter(value)
        return True
    except TypeError:
        return False


def _empty_record(now: Optional[str]) -> Dict[str, Any]:
    """The all-null firmographics record skeleton (every contract field present, honest null).
    fetched_at is the caller-supplied ``now`` (or None -- this module never calls the clock). mock
    is ALWAYS False -- this record is real API data or an explicit null, never a simulated value."""
    return {
        "cnpj": None,
        "razao_social": None,
        "nome_fantasia": None,
        "situacao_cadastral": None,
        "situacao_cadastral_codigo": None,
        "cnae_principal": None,
        "cnae_principal_descricao": None,
        "cnaes_secundarios": [],
        "natureza_juridica": None,
        "porte": None,
        "capital_social": None,
        "data_inicio_atividade": None,
        "endereco": {
            "logradouro": None,
            "numero": None,
            "municipio": None,
            "uf": None,
            "cep": None,
        },
        "socios": [],
        "telefones": [],
        "email": None,
        "data_sources": {},
        "endpoint_status": {},
        "fetched_at": now if isinstance(now, str) and now.strip() else None,
        "mock": False,
    }


__all__ = [
    "enrich_cnpj",
    "enrich_cnpjs",
    "normalize_cnpj",
    "CnpjUnavailable",
]


# --------------------------------------------------------------------------- #
# CLI -- the orchestrator runs this LIVE (real network; GREEN open gov data, no key).
# --------------------------------------------------------------------------- #
def _main(argv: List[str]) -> int:
    if not argv:
        print("CEXAI CNPJ firmographics enrichment (B2B research lane). Usage:")
        print("  python _tools/cex_cnpj_enrich.py <cnpj>   "
              "(e.g. 00.000.000/0001-91 OR 00000000000191 -- BrasilAPI, no key)")
        print("  Prints the firmographics JSON. Invalid format / 404 / timeout -> honest-null "
              "record + endpoint_status (never fabricated).")
        return 0

    # The clock is stamped HERE (the CLI boundary), not inside enrich_cnpj -- the library stays
    # deterministic; only the executable touches wall-time. ASCII ISO-8601 (UTC, 'Z').
    import datetime as _dt

    now = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    raw = argv[0]
    rec = enrich_cnpj(raw, now=now)
    # JSON to stdout (ensure_ascii=True keeps the .claude ASCII rule even for accented gov names).
    print(json.dumps(rec, ensure_ascii=True, indent=2, sort_keys=True))
    # Exit 0 even on an honest-null (a 404 / invalid CNPJ is a VALID, recorded result -- not a tool
    # crash). The status lives in the JSON's endpoint_status for the caller to read.
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
