"""CEXAI tools exception hierarchy (ingestion + research + reposynth + browser).

Rooted at the foundation's ``CexaiError`` so a caller can still catch the whole
package with one ``except CexaiError``. ``ToolsError`` is the v0.4 (tools) subtree
root; the leaves below map to the specific failure modes the four tool specs
name, with the spec-named signatures encoded as structured attributes so callers
and contract tests branch on fields (``.url``, ``.requested``, ``.upstream_license``,
...) rather than parsing messages -- mirroring ``ProviderConfigError`` in the
foundation and ``RbacForbiddenError`` in governance.

Impl waves MAY add more leaves under ``ToolsError`` in their own lanes (e.g. a
``PrivateRepoNotSupportedError`` for 14 FR-015, an ``AuthProfileExpiredError`` for
15 E1, or a ``PolicyConfigError`` for 15 E2); the names defined here are FROZEN
for v0.4. ``LicenseUnknownWarning`` is a ``Warning`` (a non-fatal advisory, E3),
NOT a ``ToolsError`` -- synthesis proceeds after it is emitted.

Spec provenance:
  * RobotsBlockedError        -> 09 US P1 acceptance #4 / SC-004 -- robots.txt
                                 forbids the fetch and no override artifact is
                                 present. RobotsBlockedError(url, robots_rule).
  * BulkDownloadRefusedError  -> 11 FR-004 / SC-003 / Principle WL2 -- a query
                                 requests >= the bulk threshold of references.
                                 BulkDownloadRefusedError(requested, threshold).
  * LicenseCompatibilityError -> 14 E2 / SC-005 / FR-008 -- the upstream repo
                                 LICENSE is incompatible with the declared
                                 downstream use; fail-closed, no artifact written.
                                 LicenseCompatibilityError(upstream_license,
                                 downstream_license).
  * LicenseUnknownWarning     -> 14 E3 / SC-006 -- the target repo has no LICENSE;
                                 synthesis proceeds with a documentation-only
                                 marker. LicenseUnknownWarning(source_url). (Warning.)
  * ReverseSynthError         -> 14 US P1 -- synthesis failed (extraction or LLM
                                 projection). ReverseSynthError(source_url, reason).
  * BrowserActionError        -> 15 US P2 -- a browser action failed at runtime.
                                 BrowserActionError(action_id, reason).
  * ApprovalPendingError      -> 15 US P2 / SC-002 -- a write-class action was
                                 enqueued for human approval; the caller must
                                 retry once resolved. ApprovalPendingError(
                                 request_id, operation).

absorbs: 09_scrapling + 11_welib + 14_gitreverse + 15_auto-browser
"""

from __future__ import annotations

from cexai.foundation._shared.errors import CexaiError

__all__ = [
    "ToolsError",
    "RobotsBlockedError",
    "BulkDownloadRefusedError",
    "LicenseCompatibilityError",
    "LicenseUnknownWarning",
    "ReverseSynthError",
    "BrowserActionError",
    "ApprovalPendingError",
]


class ToolsError(CexaiError):
    """Root of the tools subtree -- an ingestion, research, reposynth, or browser
    failure. Subclasses ``CexaiError`` so a single ``except CexaiError`` covers it."""


# --------------------------------------------------------------------------- #
# Ingestion (cexai-specs/09_scrapling US P1)                                   #
# --------------------------------------------------------------------------- #
class RobotsBlockedError(ToolsError):
    """A fetch was refused because robots.txt disallows it and no ``robots_override``
    artifact is present (09 US P1 acceptance #4 / SC-004). This is the one fetch
    failure that RAISES (ordinary network / HTTP failures ride in
    ``FetchResult.errors`` per FR-007). ``url`` is the blocked target and
    ``robots_rule`` is the matched disallow directive, surfaced for the audit
    entry."""

    def __init__(self, url: str, robots_rule: str) -> None:
        self.url = url
        self.robots_rule = robots_rule
        super().__init__(f"robots.txt blocks {url!r} (rule {robots_rule!r})")


# --------------------------------------------------------------------------- #
# Research (cexai-specs/11_welib US P1/P2)                                     #
# --------------------------------------------------------------------------- #
class BulkDownloadRefusedError(ToolsError):
    """A welib query requested at or above the bulk threshold of references (11
    FR-004 / SC-003, default N=10) and was refused per ethical-use Principle WL2.
    ``requested`` is the count the query asked for and ``threshold`` is the
    configured ceiling; both are surfaced so the caller can re-issue a narrower
    query."""

    def __init__(self, requested: int, threshold: int) -> None:
        self.requested = requested
        self.threshold = threshold
        super().__init__(
            f"bulk download refused: {requested} references requested "
            f"(threshold {threshold})"
        )


# --------------------------------------------------------------------------- #
# Reposynth (cexai-specs/14_gitreverse E2/E3/US P1)                            #
# --------------------------------------------------------------------------- #
class LicenseCompatibilityError(ToolsError):
    """The upstream repo LICENSE is incompatible with the declared downstream use
    (14 E2 / SC-005 / FR-008). This is a fail-closed legal-hygiene gate
    (Article XVII): synthesis does NOT run and no artifact is written.
    ``upstream_license`` and ``downstream_license`` are the conflicting SPDX
    identifiers, surfaced so the caller can explain the incompatibility."""

    def __init__(self, upstream_license: str, downstream_license: str) -> None:
        self.upstream_license = upstream_license
        self.downstream_license = downstream_license
        super().__init__(
            f"upstream license {upstream_license!r} incompatible with declared "
            f"downstream {downstream_license!r}"
        )


class LicenseUnknownWarning(Warning):
    """The target repo has no LICENSE (14 E3 / SC-006). NON-FATAL: synthesis
    proceeds and the emitted artifact carries ``derived_from_unlicensed_source:
    true`` in its frontmatter -- the downstream consumer owns the legal evaluation.
    Subclasses ``Warning`` (NOT ``ToolsError``) because it does not abort the call.
    ``source_url`` identifies the unlicensed repo."""

    def __init__(self, source_url: str) -> None:
        self.source_url = source_url
        super().__init__(
            f"repo {source_url!r} has no LICENSE; synthesizing with "
            f"derived_from_unlicensed_source marker"
        )


class ReverseSynthError(ToolsError):
    """Synthesis of a ``reverse_prompt`` failed (14 US P1) -- extraction could not
    complete or the LLM projection was unusable. ``source_url`` is the repo and
    ``reason`` is the human-readable cause, surfaced for the reasoning_trace
    (FR-009)."""

    def __init__(self, source_url: str, reason: str) -> None:
        self.source_url = source_url
        self.reason = reason
        super().__init__(f"reverse-prompt synthesis failed for {source_url!r}: {reason}")


# --------------------------------------------------------------------------- #
# Browser (cexai-specs/15_auto-browser US P2)                                  #
# --------------------------------------------------------------------------- #
class BrowserActionError(ToolsError):
    """A browser action failed at runtime (15 US P2) -- e.g. the selector / form
    was not found or the underlying Playwright call errored. ``action_id`` links
    back to the originating ``BrowserAction`` and ``reason`` is the cause, surfaced
    for the ``events.jsonl`` audit entry (FR-006)."""

    def __init__(self, action_id: str, reason: str) -> None:
        self.action_id = action_id
        self.reason = reason
        super().__init__(f"browser action {action_id!r} failed: {reason}")


class ApprovalPendingError(ToolsError):
    """A write-class browser action was enqueued for human approval and has not yet
    been resolved (15 US P2 / SC-002). The calling agent receives this and must
    retry once a human operator approves; a denial or timeout aborts the action
    via the v0.3 governance gate. This is a tools-LOCAL leaf -- distinct from the
    governance terminal verdicts (``ApprovalDeniedError`` / ``ApprovalTimeoutError``):
    it signals the still-PENDING, not-yet-terminal state specific to the browser
    action queue, while the gating MECHANISM reuses the governance ApprovalGate.
    ``request_id`` identifies the queued ``ApprovalRequest`` and ``operation`` is
    the gated action."""

    def __init__(self, request_id: str, operation: str) -> None:
        self.request_id = request_id
        self.operation = operation
        super().__init__(
            f"browser action {operation!r} pending approval "
            f"(request {request_id!r})"
        )
