"""SPDX license-compatibility gate for repo synthesis (14_gitreverse FR-008).

A fail-closed legal-hygiene gate (Article XVII): the synthesizer consults this
module BEFORE it spends an LLM call, so an incompatible upstream LICENSE aborts
the run with ``LicenseCompatibilityError`` and no artifact is written (E2 / SC-005).
A target with no LICENSE at all is NOT an error here -- the synthesizer detects
that via ``has_license_file`` and emits the non-fatal ``LicenseUnknownWarning``
(E3 / SC-006).

The compatibility model is the small static matrix FR-008 names, deliberately
coarse (Article VIII -- this is hygiene, not a legal engine):
  * permissive upstream (MIT / Apache-2.0 / BSD / ISC / Unlicense / 0BSD) flows
    into ANY declared downstream -- always compatible.
  * copyleft upstream requires a same-or-stronger downstream, ranked
    weak (LGPL / MPL-2.0) < strong (GPL) < network (AGPL). A weaker or
    unclassifiable downstream fails closed.

License DETECTION is heuristic over the extracted LICENSE / COPYING entry-file
content (the frozen ``RepoExtract`` carries no dedicated license field, so the
text the extractor surfaced as an entry file is the signal). An unrecognised
license body yields ``None`` (present-but-unclassified) which the caller treats
distinctly from "no license file at all".

absorbs: 14_gitreverse
"""

from __future__ import annotations

from cexai.tools._shared.errors import LicenseCompatibilityError
from cexai.tools._shared.types import RepoExtract

__all__ = [
    "detect_license_spdx",
    "has_license_file",
    "is_compatible",
    "check_license_compatibility",
]

# Compatibility rank: 0 permissive, 1 weak copyleft, 2 strong copyleft, 3 network
# copyleft. A copyleft upstream needs a downstream of equal-or-higher rank
# (FR-008 "same-or-stronger"). Permissive upstream short-circuits to compatible.
_RANK: dict[str, int] = {
    "MIT": 0,
    "APACHE-2.0": 0,
    "BSD-2-CLAUSE": 0,
    "BSD-3-CLAUSE": 0,
    "ISC": 0,
    "UNLICENSE": 0,
    "0BSD": 0,
    "MPL-2.0": 1,
    "LGPL-2.1": 1,
    "LGPL-3.0": 1,
    "GPL-2.0": 2,
    "GPL-3.0": 2,
    "AGPL-3.0": 3,
}

# Surface-form aliases normalized to a canonical SPDX id before ranking.
_ALIASES: dict[str, str] = {
    "APACHE2": "APACHE-2.0",
    "APACHE-2": "APACHE-2.0",
    "APACHE 2.0": "APACHE-2.0",
    "APACHE LICENSE 2.0": "APACHE-2.0",
    "BSD": "BSD-3-CLAUSE",
    "BSD-3": "BSD-3-CLAUSE",
    "BSD-2": "BSD-2-CLAUSE",
    "GPL": "GPL-3.0",
    "GPLV3": "GPL-3.0",
    "GPL-3.0-ONLY": "GPL-3.0",
    "GPL-3.0-OR-LATER": "GPL-3.0",
    "GPLV2": "GPL-2.0",
    "GPL-2.0-ONLY": "GPL-2.0",
    "GPL-2.0-OR-LATER": "GPL-2.0",
    "LGPL": "LGPL-3.0",
    "LGPLV3": "LGPL-3.0",
    "AGPL": "AGPL-3.0",
    "AGPLV3": "AGPL-3.0",
    "AGPL-3.0-ONLY": "AGPL-3.0",
    "AGPL-3.0-OR-LATER": "AGPL-3.0",
    "MPL": "MPL-2.0",
    "MPL2": "MPL-2.0",
    "THE-UNLICENSE": "UNLICENSE",
}

# Basename prefixes that mark a file as a license text (case-insensitive).
_LICENSE_PREFIXES: tuple[str, ...] = ("license", "licence", "copying", "unlicense")


def _normalize_spdx(value: str) -> str:
    """Upper-case + trim a license id and resolve a known surface-form alias to
    its canonical SPDX identifier (e.g. ``"gplv3"`` -> ``"GPL-3.0"``)."""
    key = value.strip().upper()
    return _ALIASES.get(key, key)


def _is_license_filename(path: str) -> bool:
    """True if ``path``'s basename looks like a license file (LICENSE / LICENCE /
    COPYING / UNLICENSE, any extension)."""
    base = path.replace("\\", "/").rsplit("/", 1)[-1].lower()
    return base.startswith(_LICENSE_PREFIXES)


def _sniff_spdx(text: str) -> str | None:
    """Classify license body ``text`` to an SPDX id, or ``None`` if unrecognised.
    Ordered most-specific-first so AGPL/LGPL are not swallowed by the generic GPL
    marker."""
    low = text.lower()
    if "gnu affero general public license" in low:
        return "AGPL-3.0"
    if "gnu lesser general public license" in low:
        return "LGPL-3.0"
    if "gnu general public license" in low:
        return "GPL-2.0" if "version 2" in low else "GPL-3.0"
    if "mozilla public license" in low:
        return "MPL-2.0"
    if "apache license" in low:
        return "APACHE-2.0"
    if "mit license" in low or "permission is hereby granted, free of charge" in low:
        return "MIT"
    if "redistribution and use in source and binary forms" in low:
        return "BSD-3-CLAUSE" if "neither the name" in low else "BSD-2-CLAUSE"
    if "isc license" in low:
        return "ISC"
    if "this is free and unencumbered software released into the public domain" in low:
        return "UNLICENSE"
    return None


def has_license_file(extract: RepoExtract) -> bool:
    """True if the repo carries a license file anywhere -- as an extracted entry
    file OR as a path in the (possibly truncated) file tree. ``False`` here is the
    no-LICENSE case that drives ``LicenseUnknownWarning`` (E3 / SC-006)."""
    if any(_is_license_filename(name) for name in extract.entry_files):
        return True
    return any(_is_license_filename(path) for path in extract.file_tree)


def detect_license_spdx(extract: RepoExtract) -> str | None:
    """The upstream SPDX id sniffed from the extracted LICENSE/COPYING entry-file
    content, or ``None`` when no license text is available to classify (no license
    file, or a body the heuristic does not recognise). Entry files are scanned in
    sorted order for a deterministic result (FR-006)."""
    for name, content in sorted(extract.entry_files.items()):
        if _is_license_filename(name):
            spdx = _sniff_spdx(content)
            if spdx is not None:
                return spdx
    return None


def is_compatible(upstream_spdx: str, downstream_spdx: str) -> bool:
    """True if ``upstream_spdx`` may flow into a declared ``downstream_spdx`` use
    (FR-008). Permissive upstream is compatible with any downstream; copyleft
    upstream requires an equal-or-stronger downstream; an unclassifiable
    non-permissive relationship fails closed (returns ``False``)."""
    upstream_rank = _RANK.get(_normalize_spdx(upstream_spdx))
    if upstream_rank == 0:
        return True
    downstream_rank = _RANK.get(_normalize_spdx(downstream_spdx))
    if upstream_rank is None or downstream_rank is None:
        return False
    return downstream_rank >= upstream_rank


def check_license_compatibility(upstream_spdx: str, downstream_spdx: str) -> None:
    """Raise ``LicenseCompatibilityError(upstream, downstream)`` when the upstream
    license cannot flow into the declared downstream use (fail-closed gate, E2 /
    SC-005). Returns ``None`` (proceed) when compatible."""
    if not is_compatible(upstream_spdx, downstream_spdx):
        raise LicenseCompatibilityError(upstream_spdx, downstream_spdx)
