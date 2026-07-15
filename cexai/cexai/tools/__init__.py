"""CEXAI tools layer -- the v0.4 capability plane over foundation + governance.

Four tool subsystems share one frozen vocabulary
(``cexai.tools._shared.types``):

  ingestion  tier-escalating web fetch (basic/stealthy/dynamic) + robots   -- 09_scrapling
  research   typed welib academic-source retrieval + citations             -- 11_welib
  reposynth  public repo -> reusable typed reverse_prompt projection        -- 14_gitreverse
  browser    policy-gated Playwright browser automation + auth profiles    -- 15_auto-browser

Import is intentionally light (Article VIII): this module exposes nothing at the
top level for W0. The subsystems stay addressable at ``cexai.tools.
{ingestion,research,reposynth,browser}`` once their impl-wave implementations
land. Every subsystem COMPOSES with the existing substrate -- it calls the LLM
through ``cexai.foundation.invocation.router`` (reposynth), emits spans through
``cexai.foundation.tracing`` (browser / audit), and gates risky browser writes
through the v0.3 ``cexai.governance`` HITL + audit subsystems (browser) -- and
does NOT replace any of them.

TAXONOMY NOTE (founder rule, taxonomy-neutral wave): the types frozen here are
Python CODE. Per N07's locked v0.4 decision this wave registers ZERO kinds and
does NOT touch ``.cex/kinds_meta.json``. ``fetch_result`` is a RUNTIME DATACLASS,
NOT a kind (the founder rule overrides the 09 spec's "new kind" claim; precedent:
Span / TopologyRun / AuthToken). ``reverse_prompt`` IS a justified new kind but is
registered LATER by the vertical-14 impl ADR cell -- here only its runtime
projection is frozen (precedent: ``approval_request`` registered in v0.3-W3b, not
the W3a freeze). Impl waves REUSE ``checkpoint`` / ``rag_source`` / ``citation`` /
``search_strategy`` / ``browser_tool`` / ``computer_use`` / ``hitl_config``.

Spec provenance: cexai-specs/09_scrapling, /11_welib, /14_gitreverse,
/15_auto-browser (US + FR + Key Entities per subsystem).

absorbs: 09_scrapling + 11_welib + 14_gitreverse + 15_auto-browser
"""

__all__: list = []
