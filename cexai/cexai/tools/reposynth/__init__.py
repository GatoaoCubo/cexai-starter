"""Reposynth subsystem -- public repo -> reusable reverse_prompt (v0.4-W1 impl).

Converts a public source repo into a single typed ``reverse_prompt`` projection:
read-only extraction (metadata + sorted file tree + README + <= 10 entry files,
truncated at the 5,000-path budget), deterministic LLM synthesis at temperature
0.0, a fail-closed LICENSE-compatibility gate (Article XVII), and a triangulation
source returning a ``TriangulationBriefFragment`` for auto-research
(cexai-specs/14_gitreverse FR-001..015). The emitted ``reverse_prompt`` KIND is
registered by the N04 taxonomy cell (NOT here); the frozen ``RepoExtract`` /
``ReversePrompt`` / ``TriangulationBriefFragment`` / ``RepoSynthesizer`` contracts
live in ``cexai.tools._shared.types``.

LLM seam: synthesis dispatches through ``cexai.foundation.llm.call`` at
temperature 0.0 (the provider-agnostic facade) -- the W0 docstrings' name
``cexai.foundation.invocation.router.dispatch`` does not exist; ``invocation`` is
the dual-invocation feature registry, not an LLM router. See ``synthesizer`` for
the full rationale.

``RepoPromptSynthesizer`` is an alias of ``GitReverseSynthesizer`` kept so the
frozen W0 contract seam (``tests/tools/contract/test_tools_contracts.py``
``test_repo_synthesizer_projects_reverse_prompt``) can be un-skipped in a later
wave without editing that file. This mirrors the ``memory.vector.
InMemoryVectorStore`` and ``orchestration.topology.DefaultTopologyInterpreter``
alias pattern.

absorbs: 14_gitreverse
"""

from cexai.tools.reposynth.synthesizer import (
    GitReverseSynthesizer,
    RepoSource,
    synthesize_for_triangulation,
)

# Alias for the frozen contract seam (test_repo_synthesizer_projects_reverse_prompt).
RepoPromptSynthesizer = GitReverseSynthesizer

__all__ = [
    "GitReverseSynthesizer",
    "RepoPromptSynthesizer",
    "RepoSource",
    "synthesize_for_triangulation",
]
