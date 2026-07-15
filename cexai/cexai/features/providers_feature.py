"""Provider discovery feature -- expose the registered LLM providers (activation wave).

A thin, offline feature that surfaces ``cexai.foundation.llm.available_providers()``
through both invocation interfaces: the library API (``run_feature("providers")``) and
the CLI (``cexai providers``). It lists the provider names callable right now -- the 4
lazy built-ins (anthropic / google / ollama / openai) plus any explicitly registered
adapter -- WITHOUT building an SDK client or needing a credential (Article XIV); naming
a provider does not instantiate it.

Public contract (keep EXACT):
    list_providers() -> tuple[str, ...]
        The sorted, de-duplicated provider names available at dispatch time.

Invocation: registered at import as the feature ``"providers"`` so it runs via both the
library API and the CLI (Article II / FR-006). The CLI / library only see the feature
once ``cexai.features`` is imported (the registration is a module side effect).

absorbs: 08_goose/provider-abstraction
"""

from __future__ import annotations

from cexai.foundation.invocation import register_feature
from cexai.foundation.llm import available_providers

__all__ = ["list_providers"]


def list_providers() -> tuple[str, ...]:
    """Return the LLM provider names callable right now (the 4 built-ins plus any
    explicitly registered), sorted and de-duplicated. Pure + offline -- delegates to
    ``cexai.foundation.llm.available_providers`` and instantiates nothing."""
    return available_providers()


# Module side effect: expose the feature to both invocation interfaces.
register_feature("providers", list_providers)
