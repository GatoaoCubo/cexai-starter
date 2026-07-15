"""cyclonedx_bom -- the CycloneDX 1.6 ML-BOM payload encoding + SPDX 3.0 export seam
for the signed exchange unit (the "X" in CEX). CONVERGENCE T7, checkpoint C7.

This is the FOUNDER-LOCKED wire format of the exchange axis (master ADR Section 7
GDP decision: ``exchange_bom_standard = cyclonedx_ml_bom_v1`` + an SPDX 3.0 export
seam). C5 (``knowledge_bom.py``) shipped the DSSE-style ENVELOPE mechanics -- PAE +
Ed25519 + did:key -- around a CEX-scoped JSON payload, and stated in its own
docstring that "CycloneDX is the v2 payload encoding -- the envelope mechanics ...
are identical regardless." THIS module is that CycloneDX payload encoding, so that
an EXTERNAL SBOM tool and a CEX verifier agree on the bytes a signature covers.

Design source:
  * N04_knowledge/P08_architecture/p08_adr_knowledge_bom_exchange_unit.md (T7 design).
  * N07_admin/P08_architecture/p08_adr_convergence_master.md Section 7 (GDP:
    cyclonedx_ml_bom_v1 wire format + spdx_3.0 export seam = the council's
    ONE-WAY, ADVISORY export) + Section 6 council corrections.

----------------------------------------------------------------------------------
WHAT C7 ADDS ON TOP OF C5 (composition, NOT modification):

  A. ``to_cyclonedx_ml_bom(...)`` -- builds a CycloneDX 1.6 ML-BOM JSON dict by hand
     (NO ``cyclonedx`` pip dependency). The model is the root ``metadata.component``
     (``type: machine-learning-model``) carrying the asset's SHA-256; each source /
     training-data input is a top-level ``component`` (``type: data``) carrying its
     own SHA-256. The SPDX license expression rides ``metadata.licenses[].expression``.
     CEX-scoped facts (the access modifier + the DSSE provenance/lineage) ride
     ``properties`` + an ``annotations`` block -- CycloneDX's documented extension
     surfaces, so a strict CycloneDX validator still accepts the doc.

  B. ``cyclonedx_to_spdx(...)`` -- the council's ONE-WAY, LOSSY, ADVISORY export to an
     SPDX 3.0-style dict (AIPackage + checksums + a single ``licenseConcluded`` +
     relationships). DOCUMENTED loss: a CycloneDX ``expression`` license that is not
     on the SPDX license list becomes a ``LicenseRef-...`` (carried, not crashed),
     and DSSE predicate granularity (the per-step lineage + the signature envelope)
     does NOT round-trip. The docstring states the council's exact finding: "SPDX
     export is ADVISORY; the CycloneDX+DSSE original is the source of truth for
     verification."

  C. ``build_signed_cyclonedx_bom(...)`` -- wraps the CycloneDX JSON in a DSSE
     envelope whose ``payloadType`` is a CycloneDX media type
     (``application/vnd.cyclonedx+json; version=1.6``) and whose payload is the
     canonical CycloneDX bytes, signed Ed25519 over the MIRRORED DSSE PAE.

  D. ``verify_signed_cyclonedx_bom(...)`` -- the receiver-side verifier: parse ->
     resolve signer in the RECEIVER-supplied ``trust_set`` -> verify Ed25519 over the
     PAE -> re-check hash-binding on the CycloneDX components -> optional C4
     ``StatusList`` revocation. Same fail-closed posture + reason codes as C5.

----------------------------------------------------------------------------------
THE MIRRORED DSSE PAE (the load-bearing interop point):

  ``_pae`` here is a BYTE-FOR-BYTE MIRROR of C5's ``knowledge_bom._pae`` (exactly as
  C2 mirrored ``deny_cross_tenant``). It is NOT imported from C5 and C5 is NOT
  modified; it is re-stated from the DSSE v1 spec so the two modules share a
  *specification*, not a *symbol*. The test ``test_pae_byte_matches_c5`` imports
  C5's ``_pae`` and asserts ``c7._pae(t, p) == c5._pae(t, p)`` for the same inputs --
  the proof that a CEX verifier and an external DSSE verifier construct the SAME
  signed bytes. Because the PAE binds the ``payloadType`` AND the length-prefixed
  payload, a CycloneDX payload signed under the CycloneDX media type cannot be
  reinterpreted under C5's CEX media type (or vice versa): same mechanism, distinct
  type binding.

----------------------------------------------------------------------------------
THE TWO ENFORCED INVARIANTS (mirrored from C5, master ADR open Q2 + Q3):

  * HASH-BINDING. Every CycloneDX ``component`` (the model component AND every data
    component) MUST carry a non-empty SHA-256 hash. A component that names a source
    but cannot bind it to bytes is unverifiable lineage -- REJECTED at BUILD and again
    at VERIFY (``CycloneDxBomError('missing_source_hash')`` / ``'missing_hash'``).

  * NAME-LEAK. A ``public`` BOM's DATA components carry NO real ``name`` -- only an
    opaque ``bom-ref`` + a SHA-256 hash. Naming an internal dataset in a public BOM
    is a membership-inference / competitive leak (council LoRA-Leak). REJECTED at
    BUILD (``CycloneDxBomError('name_leak')``). Mirrors C5's modifier normalization:
    ``protected`` collapses to ``private`` (no trust-group in v1), so in practice the
    rule fires only for a PUBLIC BOM with any named data component.

----------------------------------------------------------------------------------
HONEST CAVEATS (stated, not hidden -- the SAME posture as C5):
  * SPDX export is ADVISORY + LOSSY. The CycloneDX+DSSE original is the source of
    truth for verification; the SPDX dict is a one-way convenience for external SPDX
    tooling and is NOT signed by this module. See ``cyclonedx_to_spdx``.
  * The CycloneDX payload is the v1 WIRE FORMAT of the exchange unit. The DSSE
    envelope mechanics (PAE + Ed25519 + did:key) are identical to C5's CEX-scoped
    payload -- only the payload encoding + the ``payloadType`` differ.
  * SELF-ROOTED TOFU (v1), inherited from C1/C5. The signer DID is C1's self-rooted
    ``did:key``; the verifier trusts ONLY what the RECEIVER put in ``trust_set``.
    There is no independent root yet (the Component 5 brick). A receiving instance is
    sovereign-on-both-ends only if it actually runs this verifier offline.

Dependencies: ``cryptography`` (Ed25519) via the C1 key type + the C4 ``StatusList``
duck-typed for revocation + the local ``_b64`` helper. NO new pip dependency: the
CycloneDX + SPDX structures are hand-built dicts. Does NOT import or modify C5
(``knowledge_bom``); it MIRRORS the spec-defined PAE.

ASCII-only per .claude/rules/ascii-code-rule.md.

absorbs: convergence/t7-knowledge-bom (checkpoint C7 -- CycloneDX ML-BOM payload + SPDX export seam)
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from cexai.governance._shared.errors import GovernanceDenied
from cexai.governance.exchange._spdx_license_ids import SPDX_LICENSE_IDS
from cexai.governance.rbac._b64 import b64url_decode, b64url_encode
from cexai.governance.rbac.principal_signing import did_key as _did_key

__all__ = [
    "CycloneDxBomError",
    "CYCLONEDX_PAYLOAD_TYPE",
    "CYCLONEDX_SPEC_VERSION",
    "ACCESS_MODIFIERS",
    "PROP_ACCESS_MODIFIER",
    "PROP_SCHEMA",
    "to_cyclonedx_ml_bom",
    "cyclonedx_to_spdx",
    "build_signed_cyclonedx_bom",
    "verify_signed_cyclonedx_bom",
]

# The CycloneDX media type used as the DSSE ``payloadType``. DSSE binds this string
# into the PAE so a verifier cannot reinterpret the bytes under another type. This is
# the founder-LOCKED v1 wire format (master ADR Section 7 GDP). Distinct from C5's
# ``application/vnd.cex.knowledge-bom+json; version=1`` -- the SAME PAE mechanism,
# a DIFFERENT type binding (so the two payload encodings cannot be confused).
CYCLONEDX_PAYLOAD_TYPE = "application/vnd.cyclonedx+json; version=1.6"

# The CycloneDX spec version this module emits (1.6, the current ML-BOM line).
CYCLONEDX_SPEC_VERSION = "1.6"

# The dbt-Mesh-style access modifiers (T7 ADR). Mirrors C5 exactly: ``protected``
# collapses to ``private`` (no trust-group in v1, fail-closed); ``private`` is the
# default and the fail-closed fallback for an absent/unknown modifier.
ACCESS_MODIFIERS = ("public", "protected", "private")
_DEFAULT_MODIFIER = "private"

# CEX-scoped CycloneDX ``property`` names. CycloneDX ``properties`` are the documented
# name/value extension surface; a ``cex:`` prefix namespaces them so an external tool
# ignores what it does not understand while a CEX verifier reads them back.
PROP_ACCESS_MODIFIER = "cex:access_modifier"
PROP_SCHEMA = "cex:schema"
_PROP_SIGNER = "cex:signer"
_CEX_SCHEMA_VALUE = "cex.knowledge_bom.cyclonedx/v1"

# The hash algorithm label CycloneDX uses for SHA-256 (CycloneDX ``hash-alg`` enum).
_SHA256_ALG = "SHA-256"

# DSSE PAE constants (in-toto / DSSE v1) -- the SAME values C5 uses. Kept here as a
# MIRROR (not an import) so this module shares the DSSE *spec* with C5, not a symbol.
# The byte-equality test (test_pae_byte_matches_c5) proves the mirror is exact.
_PAE_TYPE = b"DSSEv1"
_PAE_SP = b" "


class CycloneDxBomError(GovernanceDenied):
    """A CycloneDX-BOM build / export / sign / verify operation failed
    (CONVERGENCE T7, checkpoint C7).

    Subclasses ``GovernanceDenied`` (audit R5) -- NOT ``ValueError`` -- the SAME
    security-deny posture as ``KnowledgeBomError`` (C5), ``PrincipalTokenError`` (C1),
    ``StatusListError`` (C4). A security deny must NOT be swallowed by a generic
    ``except ValueError`` upstream; catch it via ``except GovernanceDenied`` (or this
    specific type). Carries a ``reason`` token so callers and the audit log branch on
    a field, not a parsed message. ``reason`` is one of:

      * ``missing_source_hash`` -- a source/data component has no (or an empty)
        SHA-256 at BUILD. Hash-binding (master ADR open Q2): lineage that names a
        source but cannot bind it to bytes is unverifiable. REJECTED at build.
      * ``missing_hash``        -- a CycloneDX component (model or data) lacks a
        SHA-256 at VERIFY. The receiver re-checks hash-binding independently; a BOM
        that lost a hash in transit is refused even with a valid signature.
      * ``name_leak``           -- a PUBLIC BOM's data component carries a real
        internal dataset ``name``. A public BOM exposes only an opaque ``bom-ref`` +
        a hash (master ADR open Q3 / council LoRA-Leak). REJECTED at build.
      * ``malformed``           -- structurally broken input / envelope / payload
        (missing field, wrong type, non-decodable base64, bad JSON, not a CycloneDX
        doc). A clean denial, never a raw crash on hostile input.
      * ``untrusted_signer``    -- the envelope's signer did is NOT in the receiver's
        ``trust_set`` (the TOFU / receiver-root point). REJECTED at verify.
      * ``bad_signature``       -- the Ed25519 signature does not authenticate the
        PAE of the payload under the trusted signer's key (tampered payload, wrong
        key, swapped payloadType). REJECTED at verify.
      * ``revoked``             -- the signer is marked revoked in the receiver's C4
        ``StatusList``. REJECTED at verify.

    RAISED on a failed operation; NEVER on a successful build / export / sign /
    verify."""

    _REASONS = frozenset(
        {
            "missing_source_hash",
            "missing_hash",
            "name_leak",
            "malformed",
            "untrusted_signer",
            "did_key_mismatch",
            "bad_signature",
            "revoked",
            "revocation_unresolved",
        }
    )

    def __init__(self, reason: str, detail: str = "") -> None:
        self.reason = reason
        message = f"cyclonedx_bom error: {reason}"
        if detail:
            message = f"{message} -- {detail}"
        super().__init__(message)


# --------------------------------------------------------------------------- #
# DSSE Pre-Authentication Encoding -- MIRRORED from C5 (byte-for-byte identical) #
# --------------------------------------------------------------------------- #
def _pae(payload_type: str, payload: bytes) -> bytes:
    """The DSSE v1 Pre-Authentication Encoding of ``(payload_type, payload)``.

        PAE = "DSSEv1" SP len(type) SP type SP len(payload) SP payload

    All separators are a single ASCII space; the two lengths are DECIMAL ASCII (the
    byte length of the UTF-8 ``payload_type`` and of the raw ``payload`` bytes).

    THIS IS A DELIBERATE MIRROR of ``knowledge_bom._pae`` (C5) -- it MUST be
    byte-identical so that a signature produced here verifies under C5's verifier and
    under any external DSSE verifier, and vice versa. It is re-stated from the DSSE v1
    spec (NOT imported from C5, and C5 is NOT modified) exactly as C2 mirrored
    ``deny_cross_tenant``: the shared thing is the SPEC, not the symbol. The test
    ``test_pae_byte_matches_c5`` imports C5's ``_pae`` and asserts equality on the
    same inputs to prove the mirror is exact. Binding BOTH the type and the
    length-prefixed payload into the signed bytes is the DSSE answer to JSON
    canonicalization ambiguity -- bytes cannot shift between fields and a payload
    cannot be reinterpreted under a different ``payloadType``."""
    type_bytes = payload_type.encode("utf-8")
    return b"".join(
        (
            _PAE_TYPE,
            _PAE_SP,
            str(len(type_bytes)).encode("ascii"),
            _PAE_SP,
            type_bytes,
            _PAE_SP,
            str(len(payload)).encode("ascii"),
            _PAE_SP,
            payload,
        )
    )


# --------------------------------------------------------------------------- #
# Shared normalization helpers (mirror C5's posture)                            #
# --------------------------------------------------------------------------- #
def _normalize_modifier(access_modifier: str | None) -> str:
    """Resolve the requested access modifier to its FAIL-CLOSED effective value --
    IDENTICAL semantics to ``knowledge_bom._normalize_modifier`` (C5).

    ``public`` -> public; ``private`` -> private; ``protected`` -> ``private`` (no
    trust-group in v1, fail-closed); anything else, including ``None`` / empty /
    unknown -> ``private`` (deny-by-default). The returned value is always one of
    {public, private}."""
    if access_modifier is None:
        return _DEFAULT_MODIFIER
    value = str(access_modifier).strip().lower()
    if value == "public":
        return "public"
    if value == "private":
        return "private"
    if value == "protected":
        return "private"
    return _DEFAULT_MODIFIER


def _clean_str(value: Any) -> str:
    """A stripped string, or '' for None. Used to fail-closed on empty inputs."""
    return "" if value is None else str(value).strip()


def _validate_data_component(
    comp: Mapping[str, Any], i: int, *, effective_modifier: str, at: str
) -> dict[str, Any]:
    """Validate + normalize ONE source/data input into a CycloneDX ``data`` component.

    Enforces (mirror of C5's ``_validate_source_components``, per component):
      * a non-empty ``id`` -> the CycloneDX ``bom-ref`` (else 'malformed');
      * a non-empty ``sha256`` -- HASH-BINDING (else 'missing_source_hash');
      * NAME-LEAK: if ``effective_modifier`` is not 'private' (i.e. 'public') the
        component MUST NOT carry a non-empty ``name`` -- a public BOM exposes only an
        opaque bom-ref + a hash. Because protected collapses to private, this fires
        only for a public BOM with a named data component.

    Returns the CycloneDX component dict ``{type:"data", "bom-ref":id, name?:...,
    hashes:[{alg:"SHA-256", content: sha256}]}``."""
    if not isinstance(comp, Mapping):
        raise CycloneDxBomError("malformed", f"{at}: source component {i} is not a mapping")
    cid = _clean_str(comp.get("id"))
    if not cid:
        raise CycloneDxBomError("malformed", f"{at}: source component {i} has no id")
    digest = _clean_str(comp.get("sha256"))
    if not digest:
        raise CycloneDxBomError(
            "missing_source_hash", f"{at}: source component {cid!r} has no sha256"
        )
    name_raw = comp.get("name")
    name = None if name_raw is None else (_clean_str(name_raw) or None)
    if effective_modifier != "private" and name:
        raise CycloneDxBomError(
            "name_leak",
            f"{at}: {effective_modifier} BOM names internal dataset {name!r} "
            f"(use an opaque bom-ref; name a dataset only in a protected/private BOM)",
        )
    component: dict[str, Any] = {
        "type": "data",
        "bom-ref": cid,
        "hashes": [{"alg": _SHA256_ALG, "content": digest}],
    }
    if name:
        component["name"] = name
    return component


def _canonical_json_bytes(obj: Mapping[str, Any]) -> bytes:
    """Serialize a JSON object to canonical, deterministic bytes: UTF-8 JSON with
    sorted keys + compact separators + ``ensure_ascii``. The signature covers the PAE
    of THESE bytes, so determinism is what lets the producer and an independent tool
    agree on the signed bytes. The verifier checks the signature over the bytes it
    RECEIVED (decoded from the envelope ``payload``), NOT a re-serialization -- so a
    canonicalization mismatch cannot silently pass. Mirrors C5's
    ``_canonical_payload_bytes``."""
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


# --------------------------------------------------------------------------- #
# A. to_cyclonedx_ml_bom -- the hand-built CycloneDX 1.6 ML-BOM JSON dict        #
# --------------------------------------------------------------------------- #
def to_cyclonedx_ml_bom(
    asset_sha256: str,
    license_spdx: str,
    source_components: Sequence[Mapping[str, Any]],
    lineage: Sequence[Any],
    signer_did: str,
    access_modifier: str = _DEFAULT_MODIFIER,
) -> dict[str, Any]:
    """Build a CycloneDX 1.6 ML-BOM JSON dict for an exchangeable asset (the founder-
    LOCKED v1 wire format; CONVERGENCE T7, C7).

    Inputs (the C5 four mandatory fields, re-shaped into CycloneDX):
      * ``asset_sha256``      -- SHA-256 of the asset the BOM vouches for (the model /
        adapter / knowledge-pack bytes). Becomes the root ``metadata.component`` hash.
        Non-empty (else 'malformed').
      * ``license_spdx``      -- a single SPDX expression (e.g. "Apache-2.0",
        "CC-BY-4.0 AND MIT"). Rides ``metadata.licenses[].expression``. Non-empty
        (else 'malformed'); not validated against the SPDX list in v1.
      * ``source_components`` -- the source/training-data inventory; each
        ``{id, sha256, optional name}`` becomes a top-level ``data`` component.
        HASH-BINDING enforced per component; NAME-LEAK enforced for a public BOM.
      * ``lineage``           -- ordered derivation steps; transported verbatim into an
        ``annotations`` block (the DSSE provenance, CEX-scoped).
      * ``signer_did``        -- C1's ``did:key`` of the signer; recorded as a
        ``cex:signer`` property + the metadata manufacturer ref. Non-empty
        (else 'malformed').
      * ``access_modifier``   -- public | protected | private (default private).
        ``protected`` normalizes to ``private`` (fail-closed); the EFFECTIVE modifier
        is what is recorded (``cex:access_modifier`` property).

    Returns a dict shaped like a real CycloneDX 1.6 doc::

        {
          "bomFormat": "CycloneDX",
          "specVersion": "1.6",
          "metadata": {
            "licenses": [{"expression": "<SPDX expr>"}],
            "component": {
              "type": "machine-learning-model",
              "bom-ref": "asset:<sha256>",
              "name": "cex-knowledge-asset",
              "hashes": [{"alg": "SHA-256", "content": "<asset_sha256>"}]
            }
          },
          "components": [ {"type": "data", "bom-ref": "<id>", ...,
                           "hashes": [{"alg": "SHA-256", "content": "<sha256>"}]} ],
          "properties": [{"name": "cex:access_modifier", "value": "<modifier>"}, ...],
          "annotations": [ {... DSSE provenance/lineage ...} ]
        }

    Build-time enforcement (fail-closed, before returning):
      * 'malformed' for an empty asset_sha256 / license_spdx / signer_did, a
        non-list source_components / lineage, or a data component with no id.
      * 'missing_source_hash' for any data component lacking a sha256 (hash-binding).
      * 'name_leak' for a PUBLIC BOM whose data component names an internal dataset.

    This is HAND-BUILT JSON -- no ``cyclonedx`` pip dependency. The structure is a
    valid CycloneDX 1.6 ML-BOM (bomFormat/specVersion/metadata.component of type
    machine-learning-model/components of type data/SPDX license expression); CEX
    facts ride the documented ``properties`` + ``annotations`` extension surfaces."""
    asset = _clean_str(asset_sha256)
    if not asset:
        raise CycloneDxBomError("malformed", "to_cyclonedx: asset_sha256 is required")
    lic = _clean_str(license_spdx)
    if not lic:
        raise CycloneDxBomError("malformed", "to_cyclonedx: license_spdx is required")
    sd = _clean_str(signer_did)
    if not sd:
        raise CycloneDxBomError("malformed", "to_cyclonedx: signer_did is required")
    if not isinstance(source_components, (list, tuple)):
        raise CycloneDxBomError("malformed", "to_cyclonedx: source_components must be a list")
    if not isinstance(lineage, (list, tuple)):
        raise CycloneDxBomError("malformed", "to_cyclonedx: lineage must be a list")

    effective_modifier = _normalize_modifier(access_modifier)

    components = [
        _validate_data_component(
            comp, i, effective_modifier=effective_modifier, at="to_cyclonedx"
        )
        for i, comp in enumerate(source_components)
    ]

    # The ML model is the root metadata component (CycloneDX ML-BOM shape). Its
    # bom-ref is derived from the asset hash so it is stable + opaque.
    model_component: dict[str, Any] = {
        "type": "machine-learning-model",
        "bom-ref": f"asset:{asset}",
        "name": "cex-knowledge-asset",
        "hashes": [{"alg": _SHA256_ALG, "content": asset}],
    }

    bom: dict[str, Any] = {
        "bomFormat": "CycloneDX",
        "specVersion": CYCLONEDX_SPEC_VERSION,
        "metadata": {
            "licenses": [{"expression": lic}],
            "component": model_component,
        },
        "components": components,
        "properties": [
            {"name": PROP_SCHEMA, "value": _CEX_SCHEMA_VALUE},
            {"name": PROP_ACCESS_MODIFIER, "value": effective_modifier},
            {"name": _PROP_SIGNER, "value": sd},
        ],
        # The DSSE provenance/lineage rides a CycloneDX annotations block (the
        # documented free-form extension surface). It is CEX-scoped; an external
        # CycloneDX validator accepts an annotations array it does not interpret.
        "annotations": [
            {
                "subjects": [model_component["bom-ref"]],
                "annotator": {"organization": {"name": "cex", "bom-ref": sd}},
                "text": json.dumps(
                    {"cex:provenance": list(lineage)},
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=True,
                ),
            }
        ],
    }
    return bom


# --------------------------------------------------------------------------- #
# B. cyclonedx_to_spdx -- the council's ONE-WAY, LOSSY, ADVISORY SPDX 3.0 export #
# --------------------------------------------------------------------------- #
# SPDX license-list identifiers are a closed set; an arbitrary CycloneDX expression
# need not be on it. C12 vendors the FULL canonical SPDX License List (the
# ``spdx/license-list-data`` ``licenseId`` values) as a deterministic, offline ASCII
# data module (``_spdx_license_ids.SPDX_LICENSE_IDS``) -- replacing the original
# ~13-entry v1 approximation that lived inline here. Only the KNOWN-SET grows; the
# routing logic below is unchanged. Anything NOT on the list is still exported as a
# LicenseRef (carried, never dropped, never crashed). A real id the snapshot OMITS
# merely degrades to a LicenseRef (SAFE); the SPDX export remains ADVISORY/LOSSY.
_KNOWN_SPDX_IDS = SPDX_LICENSE_IDS


def _is_spdx_listed_expression(expression: str) -> bool:
    """Heuristic: is ``expression`` composed ONLY of SPDX-listed ids joined by the
    SPDX operators ``AND`` / ``OR`` / ``WITH`` (and parens)? A composite of listed
    ids ("CC-BY-4.0 AND MIT") is itself a valid ``licenseConcluded`` expression on the
    SPDX side; a single unlisted id ("FooCorp-1.0") is NOT and must become a
    LicenseRef. This is a v1 approximation -- it does not parse the full SPDX
    expression grammar -- but it correctly routes the round-trippable case (all tokens
    listed) vs the must-be-LicenseRef case (any unlisted token)."""
    tokens = (
        expression.replace("(", " ")
        .replace(")", " ")
        .replace("+", " ")
        .split()
    )
    operators = {"AND", "OR", "WITH"}
    saw_license = False
    for tok in tokens:
        if tok in operators:
            continue
        saw_license = True
        if tok not in _KNOWN_SPDX_IDS:
            return False
    return saw_license


def cyclonedx_to_spdx(cyclonedx: Mapping[str, Any]) -> dict[str, Any]:
    """Export a CycloneDX 1.6 ML-BOM dict to an SPDX 3.0-style document dict -- the
    council's ONE-WAY, ADVISORY seam (CONVERGENCE T7, C7, master ADR Section 7 GDP).

    SPDX export is ADVISORY; the CycloneDX+DSSE original is the source of truth for
    verification. (This is the council's exact finding -- it is stated here, not
    hidden, because the export drops verification-load-bearing structure.)

    WHAT ROUND-TRIPS (the fields this mapping preserves):
      * The model component -> an SPDX ``AIPackage`` (SPDX 3.0 AI profile) carrying the
        SHA-256 as a ``Hash`` ({algorithm: "sha256", hashValue: ...}).
      * Each CycloneDX ``data`` component -> an SPDX ``Package`` with its SHA-256 Hash
        and a ``CONTAINS`` (model -> data) relationship -- the provenance edges.
      * The single SPDX license expression -> ``licenseConcluded`` on the AIPackage.
      * The access modifier -> an SPDX ``annotation`` (carried as a CEX comment).

    WHAT DROPS / DEGRADES (DOCUMENTED loss -- why the export is advisory):
      * A CycloneDX ``expression`` license that is NOT entirely on the SPDX license
        list cannot be a bare ``licenseConcluded`` expression; it is exported as a
        ``LicenseRef-cexNNN`` custom-license ref (CARRIED, not dropped, not crashed)
        with the raw text in ``extractedText``. A composite of listed ids survives as
        an expression.
      * DSSE PREDICATE GRANULARITY does not round-trip: the per-step lineage in the
        CycloneDX ``annotations`` and the signature envelope itself have no faithful
        SPDX equivalent. The lineage is collapsed into a single descriptive SPDX
        annotation; the SIGNATURE is NOT exported at all (an SPDX consumer cannot
        verify the DSSE envelope -- it must use the CycloneDX original).
      * CycloneDX ``properties`` other than the access modifier are not mapped.

    Fail-closed: a non-mapping input or a doc that is not a CycloneDX BOM
    (``bomFormat != "CycloneDX"``) raises ``CycloneDxBomError('malformed')``. A
    missing model hash is 'missing_hash' (an SPDX AIPackage without its checksum would
    be a silently weaker artifact). Returns the SPDX dict; this module does NOT sign
    it."""
    if not isinstance(cyclonedx, Mapping):
        raise CycloneDxBomError("malformed", "to_spdx: input must be a mapping")
    if cyclonedx.get("bomFormat") != "CycloneDX":
        raise CycloneDxBomError("malformed", "to_spdx: not a CycloneDX document")
    metadata = cyclonedx.get("metadata")
    if not isinstance(metadata, Mapping):
        raise CycloneDxBomError("malformed", "to_spdx: missing metadata")
    model = metadata.get("component")
    if not isinstance(model, Mapping):
        raise CycloneDxBomError("malformed", "to_spdx: missing metadata.component")

    model_hash = _first_sha256(model.get("hashes"))
    if not model_hash:
        raise CycloneDxBomError("missing_hash", "to_spdx: model component has no SHA-256")

    # License: pull the first metadata expression. Route it to a bare SPDX expression
    # (if all tokens are SPDX-listed) or a LicenseRef (otherwise -- carried, not lost).
    expression = _first_license_expression(metadata.get("licenses"))
    other_licensing: list[dict[str, Any]] = []
    if expression and _is_spdx_listed_expression(expression):
        license_concluded = expression
    elif expression:
        license_ref = "LicenseRef-cex001"
        license_concluded = license_ref
        other_licensing.append(
            {
                "type": "spdx_3_0:simplelicensing_CustomLicense",
                "spdxId": license_ref,
                "name": expression,
                "extractedText": expression,
                "comment": (
                    "carried verbatim: not on the SPDX license list; advisory export"
                ),
            }
        )
    else:
        license_concluded = "NOASSERTION"

    model_spdx_id = "SPDXRef-AIPackage-asset"
    elements: list[dict[str, Any]] = []

    ai_package: dict[str, Any] = {
        "type": "spdx_3_0:ai_AIPackage",
        "spdxId": model_spdx_id,
        "name": str(model.get("name") or "cex-knowledge-asset"),
        "verifiedUsing": [{"algorithm": "sha256", "hashValue": model_hash}],
        "licenseConcluded": license_concluded,
    }
    elements.append(ai_package)

    relationships: list[dict[str, Any]] = []
    components = cyclonedx.get("components")
    data_components = components if isinstance(components, (list, tuple)) else []
    for n, comp in enumerate(data_components):
        if not isinstance(comp, Mapping):
            continue
        comp_hash = _first_sha256(comp.get("hashes"))
        spdx_pkg_id = f"SPDXRef-Package-src-{n}"
        package: dict[str, Any] = {
            "type": "spdx_3_0:software_Package",
            "spdxId": spdx_pkg_id,
            # The opaque bom-ref carries over as the SPDX name when no real name is
            # present (a public BOM has only the opaque ref).
            "name": str(comp.get("name") or comp.get("bom-ref") or f"src-{n}"),
        }
        if comp_hash:
            package["verifiedUsing"] = [{"algorithm": "sha256", "hashValue": comp_hash}]
        elements.append(package)
        relationships.append(
            {
                "type": "spdx_3_0:Relationship",
                "spdxId": f"SPDXRef-Relationship-{n}",
                "from": model_spdx_id,
                "relationshipType": "CONTAINS",
                "to": [spdx_pkg_id],
            }
        )

    # The access modifier -> an SPDX annotation (CEX comment). The DSSE lineage is
    # collapsed into a single descriptive annotation -- the documented granularity loss.
    annotations: list[dict[str, Any]] = []
    modifier = _property_value(cyclonedx.get("properties"), PROP_ACCESS_MODIFIER)
    if modifier:
        annotations.append(
            {
                "type": "spdx_3_0:Annotation",
                "subject": model_spdx_id,
                "annotationType": "OTHER",
                "statement": f"cex:access_modifier={modifier}",
            }
        )
    annotations.append(
        {
            "type": "spdx_3_0:Annotation",
            "subject": model_spdx_id,
            "annotationType": "OTHER",
            "statement": (
                "ADVISORY SPDX export of a CycloneDX+DSSE knowledge_bom. Per-step "
                "lineage + the DSSE signature do NOT round-trip; verify against the "
                "CycloneDX original (the source of truth)."
            ),
        }
    )

    spdx: dict[str, Any] = {
        "spdxVersion": "SPDX-3.0",
        "dataLicense": "CC0-1.0",
        "name": "cex-knowledge-asset-spdx-export",
        "profileConformance": ["core", "software", "ai"],
        "advisory": True,
        "sourceOfTruth": "cyclonedx+dsse",
        "rootElement": [model_spdx_id],
        "element": elements,
        "relationships": relationships,
        "annotations": annotations,
    }
    if other_licensing:
        spdx["otherLicensingInformationDetected"] = other_licensing
    return spdx


def _first_sha256(hashes: Any) -> str:
    """The first SHA-256 ``content`` in a CycloneDX ``hashes`` array, or '' if none.
    Tolerant of a missing/non-list value (returns '')."""
    if not isinstance(hashes, (list, tuple)):
        return ""
    for h in hashes:
        if isinstance(h, Mapping) and h.get("alg") == _SHA256_ALG:
            return _clean_str(h.get("content"))
    return ""


def _first_license_expression(licenses: Any) -> str:
    """The first ``expression`` in a CycloneDX ``metadata.licenses`` array, or ''.
    Tolerant of a missing/non-list value or a license object without an expression."""
    if not isinstance(licenses, (list, tuple)):
        return ""
    for lic in licenses:
        if isinstance(lic, Mapping):
            expr = _clean_str(lic.get("expression"))
            if expr:
                return expr
    return ""


def _property_value(properties: Any, name: str) -> str:
    """The value of the CycloneDX ``property`` named ``name``, or ''."""
    if not isinstance(properties, (list, tuple)):
        return ""
    for prop in properties:
        if isinstance(prop, Mapping) and prop.get("name") == name:
            return _clean_str(prop.get("value"))
    return ""


# --------------------------------------------------------------------------- #
# C. build_signed_cyclonedx_bom -- DSSE envelope around the CycloneDX payload    #
# --------------------------------------------------------------------------- #
def build_signed_cyclonedx_bom(
    privkey: Ed25519PrivateKey,
    signer_did: str,
    asset_sha256: str,
    license_spdx: str,
    source_components: Sequence[Mapping[str, Any]],
    lineage: Sequence[Any],
    access_modifier: str = _DEFAULT_MODIFIER,
) -> dict[str, Any]:
    """Build a SIGNED DSSE envelope whose payload is a CycloneDX 1.6 ML-BOM
    (CONVERGENCE T7, C7 -- the founder-LOCKED wire format, signed).

    Composes ``to_cyclonedx_ml_bom`` (build-time hash-binding + name-leak enforced
    there) with the MIRRORED DSSE PAE + C1's Ed25519 key:
      * builds the CycloneDX payload from the C5 four mandatory fields;
      * serializes it to canonical bytes;
      * signs ``_pae(CYCLONEDX_PAYLOAD_TYPE, payload_bytes)`` with ``privkey``.

    Returns the DSSE envelope dict::

        {
          "payloadType": "application/vnd.cyclonedx+json; version=1.6",
          "payload":     "<base64url of the canonical CycloneDX JSON>",
          "signatures":  [{"keyid": signer_did, "sig": "<base64url Ed25519 sig>"}],
        }

    The ``payloadType`` is a CycloneDX media type (NOT C5's CEX type), and the PAE is
    byte-identical to C5's, so the SAME signature mechanism applies -- only the payload
    encoding + the bound type differ. ``signer_did`` is C1's ``did:key`` (the signer
    identity + the signature ``keyid``); non-empty (else 'malformed').

    Build-time enforcement is inherited from ``to_cyclonedx_ml_bom``: 'malformed' /
    'missing_source_hash' / 'name_leak', all BEFORE any signing (fail-closed)."""
    sd = _clean_str(signer_did)
    if not sd:
        raise CycloneDxBomError("malformed", "build_signed: signer_did is required")

    bom = to_cyclonedx_ml_bom(
        asset_sha256,
        license_spdx,
        source_components,
        lineage,
        sd,
        access_modifier=access_modifier,
    )
    payload_bytes = _canonical_json_bytes(bom)
    signature = privkey.sign(_pae(CYCLONEDX_PAYLOAD_TYPE, payload_bytes))

    return {
        "payloadType": CYCLONEDX_PAYLOAD_TYPE,
        "payload": b64url_encode(payload_bytes),
        "signatures": [{"keyid": sd, "sig": b64url_encode(signature)}],
    }


# --------------------------------------------------------------------------- #
# D. verify_signed_cyclonedx_bom -- receiver-side, RECEIVER-supplied trust_set    #
# --------------------------------------------------------------------------- #
def _parse_envelope(envelope: Mapping[str, Any]) -> tuple[str, bytes, str, bytes]:
    """Parse + structurally validate a DSSE envelope. Returns
    ``(payload_type, payload_bytes, signer_did, signature_bytes)``. Fail-closed: any
    missing field, wrong type, non-decodable base64, or empty signatures list is a
    clean ``CycloneDxBomError('malformed')`` -- never a raw KeyError / binascii error.
    v1 reads the FIRST signature (single-signer BOM). Mirrors C5's ``_parse_envelope``
    posture."""
    if not isinstance(envelope, Mapping):
        raise CycloneDxBomError("malformed", "verify: envelope must be a mapping")
    payload_type = envelope.get("payloadType")
    if not isinstance(payload_type, str) or not payload_type:
        raise CycloneDxBomError("malformed", "verify: missing payloadType")
    payload_b64 = envelope.get("payload")
    if not isinstance(payload_b64, str) or not payload_b64:
        raise CycloneDxBomError("malformed", "verify: missing payload")
    sigs = envelope.get("signatures")
    if not isinstance(sigs, (list, tuple)) or not sigs:
        raise CycloneDxBomError("malformed", "verify: missing signatures")
    first = sigs[0]
    if not isinstance(first, Mapping):
        raise CycloneDxBomError("malformed", "verify: signature entry is not a mapping")
    keyid = first.get("keyid")
    sig_b64 = first.get("sig")
    if not isinstance(keyid, str) or not keyid:
        raise CycloneDxBomError("malformed", "verify: signature has no keyid")
    if not isinstance(sig_b64, str) or not sig_b64:
        raise CycloneDxBomError("malformed", "verify: signature has no sig")
    try:
        payload_bytes = b64url_decode(payload_b64)
    except (ValueError, TypeError) as exc:
        raise CycloneDxBomError("malformed", f"verify: payload not base64url: {exc}") from exc
    try:
        signature_bytes = b64url_decode(sig_b64)
    except (ValueError, TypeError) as exc:
        raise CycloneDxBomError("malformed", f"verify: sig not base64url: {exc}") from exc
    return payload_type, payload_bytes, keyid, signature_bytes


def _decode_cyclonedx(payload_bytes: bytes) -> dict[str, Any]:
    """Decode the CycloneDX payload JSON. Fail-closed: non-JSON, a non-object payload,
    or a doc that is not ``bomFormat: "CycloneDX"`` is 'malformed', never a raw
    JSONDecodeError."""
    try:
        payload = json.loads(payload_bytes.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise CycloneDxBomError("malformed", f"verify: payload not JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise CycloneDxBomError("malformed", "verify: payload is not a JSON object")
    if payload.get("bomFormat") != "CycloneDX":
        raise CycloneDxBomError("malformed", "verify: payload is not a CycloneDX BOM")
    return payload


def _recheck_hash_binding(payload: Mapping[str, Any]) -> None:
    """Re-enforce HASH-BINDING on a received CycloneDX doc: the model component AND
    every data component MUST carry a SHA-256 hash. A BOM that lost a hash in transit
    is unverifiable lineage and is refused EVEN with a valid signature
    ('missing_hash'). The receiver re-checks independently of the producer (mirror of
    C5's verify-side hash-binding re-check)."""
    metadata = payload.get("metadata")
    model = metadata.get("component") if isinstance(metadata, Mapping) else None
    if not isinstance(model, Mapping) or not _first_sha256(model.get("hashes")):
        raise CycloneDxBomError(
            "missing_hash", "verify: model component lacks a SHA-256 hash"
        )
    components = payload.get("components", [])
    if not isinstance(components, (list, tuple)):
        raise CycloneDxBomError("malformed", "verify: components must be a list")
    for i, comp in enumerate(components):
        if not isinstance(comp, Mapping):
            raise CycloneDxBomError("malformed", f"verify: component {i} is not a mapping")
        if not _first_sha256(comp.get("hashes")):
            ref = comp.get("bom-ref") if isinstance(comp.get("bom-ref"), str) else i
            raise CycloneDxBomError(
                "missing_hash", f"verify: data component {ref!r} lacks a SHA-256 hash"
            )


def _assert_did_key_binding(signer_did: str, pubkey: Ed25519PublicKey) -> None:
    """Assert a ``did:key:z...`` signer id re-derives from the trusted ``pubkey``
    (audit R2; mirror of C5's ``_assert_did_key_binding``). A ``did:key`` is a
    deterministic function of the key bytes, so a verifier MUST re-derive + compare;
    otherwise ``signer`` is an unbound claim. Only ``did:key:z`` ids are checked
    (their identifier IS the key); a non-did:key id is bound by ``trust_set``
    enrollment instead and is skipped. Mismatch -> 'did_key_mismatch'."""
    if not signer_did.startswith("did:key:z"):
        return
    try:
        derived = _did_key(pubkey)
    except Exception as exc:  # noqa: BLE001 -- a key that cannot derive a did is malformed
        raise CycloneDxBomError(
            "malformed", f"verify: cannot derive did:key from trusted key: {exc}"
        ) from exc
    if derived != signer_did:
        raise CycloneDxBomError(
            "did_key_mismatch",
            f"signer {signer_did!r} does not derive from its trusted key "
            f"(re-derived {derived!r}); the signer field is not bound to the key",
        )


def verify_signed_cyclonedx_bom(
    envelope: Mapping[str, Any],
    trust_set: Mapping[str, Ed25519PublicKey],
    *,
    revocation: Any | None = None,
) -> dict[str, Any]:
    """Verify a signed CycloneDX-BOM envelope against a RECEIVER-SUPPLIED ``trust_set``
    and return the validated CycloneDX payload dict (CONVERGENCE T7, C7).

    VERIFY CONTRACT (so N07 can re-run + adversarially review; mirrors C5 exactly):
      * ``envelope``   -- the dict produced by ``build_signed_cyclonedx_bom``.
      * ``trust_set``  -- a mapping ``did -> Ed25519PublicKey`` the RECEIVER chose to
        trust. THIS is the TOFU / receiver-root point: the signature is checked
        against a key the RECEIVER supplied, NOT a key the envelope asserts. v1 is
        self-rooted (C1's did:key is derived from its own key bytes).
      * ``revocation`` -- OPTIONAL. To perform a REAL check, pass the 2-tuple
        ``(status_list, {signer_did: index})`` where the index map is
        RECEIVER/ISSUER-supplied. The index is read ONLY from that receiver map --
        NEVER from the CycloneDX ``cex:status_index`` property (signer-controlled;
        audit R1). A bare ``StatusList``, or a map missing the signer, raises
        'revocation_unresolved' (fail-closed). Same hardened shapes as C5.

    Steps, FAIL-CLOSED, in order (each raises ``CycloneDxBomError`` on failure):
      1. parse + structurally validate the envelope ('malformed' on any defect).
      2. resolve the signer ``keyid`` (a did) in ``trust_set`` -> 'untrusted_signer'
         if the receiver never enrolled it. For a ``did:key`` signer, the did MUST
         re-derive from the trusted key ('did_key_mismatch' otherwise; audit R2).
      3. verify the Ed25519 signature over ``_pae(payloadType, payload_bytes)`` with
         the trusted key -> 'bad_signature' on a tampered payload / wrong key /
         swapped payloadType.
      4. decode the CycloneDX payload + re-check HASH-BINDING on the model AND every
         data component -> 'missing_hash' if any lost its SHA-256.
      5. if ``revocation`` is supplied, resolve the signer's index from the RECEIVER
         map and reject a revoked signer -> 'revoked' (unresolvable ->
         'revocation_unresolved', fail-closed; the payload index is not trusted).

    Returns the validated CycloneDX payload dict on ALLOW (it NEVER returns on a
    failed step). The returned dict is the exact CycloneDX 1.6 doc that was signed --
    an external CycloneDX tool can consume it, and (because the PAE byte-matches C5)
    an external DSSE verifier reaches the same accept/reject decision over the bytes."""
    # Step 1 -- parse the envelope (fail-closed on any structural defect).
    payload_type, payload_bytes, signer_did, signature_bytes = _parse_envelope(envelope)

    # Step 2 -- resolve the signer in the RECEIVER's trust set (TOFU / receiver-root).
    if not isinstance(trust_set, Mapping):
        raise CycloneDxBomError("malformed", "verify: trust_set must be a mapping")
    pubkey = trust_set.get(signer_did)
    if pubkey is None:
        raise CycloneDxBomError(
            "untrusted_signer",
            f"signer {signer_did!r} is not in the receiver's trust set",
        )
    if not isinstance(pubkey, Ed25519PublicKey):
        raise CycloneDxBomError(
            "malformed", f"verify: trust_set[{signer_did!r}] is not an Ed25519 public key"
        )

    # Step 2b -- did:key BINDING (audit R2). A self-rooted ``did:key`` is derived
    # purely from the key bytes; it MUST re-derive from the trusted key, else the
    # ``signer`` field is an unbound claim (a trusted did mapped to a different key).
    _assert_did_key_binding(signer_did, pubkey)

    # Step 3 -- verify the Ed25519 signature over the PAE (DSSE-style). A tampered
    # payload, a wrong key, or a swapped payloadType all break this.
    try:
        pubkey.verify(signature_bytes, _pae(payload_type, payload_bytes))
    except InvalidSignature as exc:
        raise CycloneDxBomError(
            "bad_signature", "signature does not authenticate the payload"
        ) from exc

    # Step 4 -- decode + re-check hash-binding (model + every data component).
    payload = _decode_cyclonedx(payload_bytes)
    _recheck_hash_binding(payload)

    # Step 5 -- offline revocation check (C4 StatusList), if supplied.
    _check_revocation(revocation, signer_did, payload)

    return payload


def _check_revocation(
    revocation: Any | None, signer_did: str, payload: Mapping[str, Any]
) -> None:
    """Reject a revoked signer using a C4 ``StatusList`` (offline-checkable). Mirrors
    C5's ``_check_revocation`` semantics exactly, INCLUDING the audit R1 hardening:

      * ``None``                     -- no check (caller opted out).
      * ``(status_list, index_map)`` -- the ONLY shape that performs a real check;
        the signer's index is looked up in the RECEIVER/ISSUER-supplied map. THIS IS
        THE ONLY TRUSTED SOURCE OF THE INDEX.

    REVOCATION-BYPASS HARDENING (audit R1): the revocation index MUST come from the
    RECEIVER, NEVER from the signed CycloneDX payload. The previous version fell back
    to a ``cex:status_index`` CycloneDX property -- but the signer controls the
    payload, so a revoked signer could self-assert an unrevoked index and pass. That
    payload-trust path is REMOVED:
      * a bare ``status_list`` (no index_map) -> ``CycloneDxBomError(
        'revocation_unresolved')`` (fail-closed; no receiver index to read).
      * a ``(status_list, index_map)`` with the signer absent from the map ->
        ``CycloneDxBomError('revocation_unresolved')`` (fail-closed; do NOT skip and
        do NOT read the payload).

    A ``True`` from ``status_list.is_revoked(index)`` -> ``CycloneDxBomError(
    'revoked')``. A non-int RECEIVER index (audit R10) or any structural read failure
    is 'malformed' rather than a silent pass -- fail-closed. ``payload`` is no longer
    consulted for the index (the ``cex:status_index`` property is NOT trusted)."""
    if revocation is None:
        return
    status_list: Any
    index_map: Mapping[str, int] | None
    if isinstance(revocation, tuple) and len(revocation) == 2:
        status_list, index_map = revocation
    else:
        status_list, index_map = revocation, None

    # Resolve the signer's status index from the RECEIVER-supplied index map ONLY.
    # The CycloneDX cex:status_index property is NEVER read (signer-controlled).
    if index_map is None:
        raise CycloneDxBomError(
            "revocation_unresolved",
            "verify: a real revocation check requires (status_list, index_map); a "
            "bare status_list has no receiver-supplied index (the cex:status_index "
            "property is signer-controlled and is not trusted)",
        )
    if not isinstance(index_map, Mapping):
        raise CycloneDxBomError("malformed", "verify: revocation index map must be a mapping")
    if signer_did not in index_map:
        raise CycloneDxBomError(
            "revocation_unresolved",
            f"verify: signer {signer_did!r} has no entry in the receiver's "
            f"revocation index map; fail-closed (the payload index is not trusted)",
        )
    # int() coercion of a RECEIVER-supplied index is wrapped (audit R10): a non-int
    # receiver index is 'malformed', never a raw ValueError/TypeError.
    try:
        index = int(index_map[signer_did])
    except (ValueError, TypeError) as exc:
        raise CycloneDxBomError("malformed", f"verify: bad revocation index: {exc}") from exc

    is_revoked = getattr(status_list, "is_revoked", None)
    if not callable(is_revoked):
        raise CycloneDxBomError("malformed", "verify: revocation object has no is_revoked")
    try:
        revoked = bool(is_revoked(index))
    except Exception as exc:  # noqa: BLE001 -- StatusListError or any read failure
        raise CycloneDxBomError("malformed", f"verify: revocation check failed: {exc}") from exc
    if revoked:
        raise CycloneDxBomError("revoked", f"signer {signer_did!r} is revoked")
