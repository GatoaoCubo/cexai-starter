#!/usr/bin/env python3
# -*- coding: ascii -*-
"""capability_generators -- the structured-output generator REGISTRY + auto-discovery.

THE SEAM (mission MOLDED_REAL_SEAM, Wave 0). The dashboard runtime
(cex_run_capability.run_capability) asks ``get_generator(kind)`` for a registered
generator BEFORE the generic CEXAgent.build; when one exists, the capability emits a
REAL ``structured`` payload (replacing the static mock mold) and the renderer shows it.

CONFLICT-FREE BY CONSTRUCTION (why the 6-nucleus grid that follows is safe): on import
this package AUTO-DISCOVERS every sibling ``*.py`` module and imports it, so each
generator's ``@register(kind)`` runs and self-registers. Adding a generator is therefore
a NEW FILE -- never an edit to this file. Six nuclei can each drop one file in parallel
with zero merge conflict.

DEGRADE-NEVER: a module that fails to import is SKIPPED with a logged warning -- one bad
generator never breaks discovery of the others, and never crashes the import of this
package (so the runtime that imports it is never taken down by a regressed generator).

Public surface (what the runtime + tests use):
  * ``get_generator(kind) -> Callable | None`` -- the lookup the seam calls.
  * ``STRUCTURED_GENERATORS: dict[str, Callable]`` -- the live registry (kind -> build).
  * ``register`` + the section helpers -- re-exported from ``_base`` for generators.
"""

from __future__ import annotations

import importlib
import logging
import pkgutil
from pathlib import Path
from typing import Any, Callable, Dict, List

# Re-export the contract surface from _base so generators import from the package root
# (``from capability_generators import register, table_section``) OR relatively
# (``from ._base import register``) -- both reach the SAME registry dict.
from ._base import (  # noqa: F401
    GeneratorKeyCollision,
    StructuredOutput,
    assert_no_key_collisions,
    fields_section,
    get_generator,
    list_section,
    register,
    resolve_media,
    structured_output,
    table_section,
)
from ._base import _REGISTRY as STRUCTURED_GENERATORS  # the live slug -> build map

_LOG = logging.getLogger(__name__)

# Modules that are NOT generators (skipped by discovery). ``test_*`` is also skipped so a
# co-located test file never self-imports as a generator.
_SKIP_MODULES = frozenset({"__init__", "_base"})


def _discover() -> List[str]:
    """Import every sibling generator module so its ``@register`` runs. Returns the list
    of module names successfully imported (for diagnostics/tests).

    DEGRADE-NEVER: an import error in one module is logged + skipped; discovery continues.
    """
    loaded: List[str] = []
    pkg_dir = Path(__file__).resolve().parent
    for mod in pkgutil.iter_modules([str(pkg_dir)]):
        name = mod.name
        if name in _SKIP_MODULES or name.startswith("_") or name.startswith("test_"):
            continue
        try:
            importlib.import_module("%s.%s" % (__name__, name))
            loaded.append(name)
        except GeneratorKeyCollision:
            # Council A4 invariant: a genuine slug/key COLLISION is a HARD import-time failure --
            # it must NOT be swallowed like a one-off bad-generator skip, or the wrong generator
            # would silently serve a capability. Propagate so it surfaces loudly at import.
            raise
        except Exception as exc:  # one bad generator must NOT break the others
            _LOG.warning("capability_generators: skipped module %r on import: %s: %s",
                         name, type(exc).__name__, exc)
    return loaded


# Run discovery at import time so the registry is populated for the first get_generator.
DISCOVERED: List[str] = _discover()


def reload_discovery() -> List[str]:
    """Re-run auto-discovery (idempotent re-registration). Useful in tests that drop a
    generator file at runtime. Returns the freshly-loaded module names."""
    global DISCOVERED
    DISCOVERED = _discover()
    return DISCOVERED


__all__ = [
    "get_generator",
    "STRUCTURED_GENERATORS",
    "register",
    "resolve_media",
    "StructuredOutput",
    "structured_output",
    "fields_section",
    "table_section",
    "list_section",
    "reload_discovery",
    "DISCOVERED",
    # Council A4: the slug-is-the-sole-key collision guard.
    "GeneratorKeyCollision",
    "assert_no_key_collisions",
]
