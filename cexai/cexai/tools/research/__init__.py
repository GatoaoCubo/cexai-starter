"""Research subsystem -- typed welib academic-source retrieval (impl: v0.4 impl wave).

A welib ``rag_source`` consulted during F3 INJECT: ranked reference retrieval,
rate-limit backoff, ethical-use bulk-download refusal (Principle WL2), arXiv
fallback when welib is unreachable, and automatic ``Citation`` generation on
direct content reuse (cexai-specs/11_welib FR-001..007). Queries route over the
09 ingestion stealthy tier. The frozen ``Citation`` / ``WelibQuery`` /
``ResearchProvider`` contracts live in ``cexai.tools._shared.types``; this package
will ship the concrete provider behind that seam.

absorbs: 11_welib
"""

from cexai.tools.research.welib_provider import (
    WelibBackend,
    WelibProvider,
    WelibUnreachableError,
)

__all__ = [
    "WelibProvider",
    "WelibBackend",
    "WelibUnreachableError",
]
