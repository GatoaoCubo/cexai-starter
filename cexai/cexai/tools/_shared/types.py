"""Frozen type contracts for the CEXAI tools layer -- the v0.4-W0 freeze.

These names and shapes are FROZEN for the whole v0.4 (tools) milestone. Every
v0.4 impl cell -- web ingestion, research sources, repo synthesis, browser
automation -- imports these symbols and MUST NOT change their names or fields.
If a shape must evolve, that is a versioned, peer-reviewed change, not an
in-flight edit. This mirrors the v0.1 foundation, v0.2 memory, v0.3-W0
orchestration, and v0.3-W3a governance freeze discipline in
``cexai.{foundation,memory,orchestration,governance}._shared.types``.

Design constraints (Article VIII -- Anti-Abstraction):
  * stdlib typing only -- NO pydantic, NO scrapling / playwright / pyjwt /
    requests in this contract. The heavy deps land in the impl waves when
    actually wired; the freeze stays import-light.
  * every value type is an immutable ``@dataclass(frozen=True, slots=True)``.
  * collection fields are tuples / read-only mappings so instances are safely
    shareable across threads, nuclei, and providers without defensive copying.

Four tool subsystems share one vocabulary here:
  * ingestion (09 scrapling)   -- FetchStatus, FetchTier, FetchResult,
                                  RobotsPolicy; Fetcher.
  * research  (11 welib)       -- Citation, WelibQuery; ResearchProvider.
  * reposynth (14 gitreverse)  -- RepoExtract, ReversePrompt,
                                  TriangulationBriefFragment; RepoSynthesizer.
  * browser   (15 auto-browser)-- ActionClass, BrowserAction, BrowserActionResult,
                                  BrowserSession, AuthProfile; BrowserController.

These compose with -- they do NOT replace -- the existing substrate. Every impl
cell calls the LLM through ``cexai.foundation.invocation.router`` (14 synthesis),
emits spans through ``cexai.foundation.tracing`` (browser / audit), and gates
risky browser writes through the v0.3 ``cexai.governance`` HITL ApprovalGate +
audit subsystems (15 US P2). The browser plane does NOT duplicate the governance
approval vocabulary; it references it.

TAXONOMY NOTE (founder rule, taxonomy-neutral wave): these are Python CODE types.
Per N07's locked v0.4 decision this wave registers ZERO kinds and does NOT touch
``.cex/kinds_meta.json``.
  * ``fetch_result`` (the 09 spec CALLS it a "new kind") is RUNTIME DATA
    (url / status / content / headers / from_cache / errors) -> a frozen RUNTIME
    DATACLASS, NOT a kind (precedent: Span, TopologyRun, AuthToken). The founder
    rule OVERRIDES the spec author's "new kind" claim; it is not registered.
  * ``reverse_prompt`` (14) IS a justified NEW kind (an emitted, persisted,
    frontmatter-bearing ``.md`` artifact) -- but it is registered LATER by the
    vertical-14 impl wave's ADR cell, NOT here (exactly how ``approval_request``
    was registered in v0.3-W3b, not the W3a freeze). Here we freeze only its
    runtime PROJECTION dataclass (``ReversePrompt``).
  * impl waves REUSE existing kinds: ``checkpoint`` (crawl resumability,
    ``domain: crawl``), ``rag_source`` (welib source, ``source_type: welib``),
    ``citation`` (welib references), ``search_strategy`` (09 fetch tiers -- the
    ``tier`` rides in the artifact BODY / runtime, the kind schema is NOT
    mutated), ``browser_tool`` + ``computer_use`` (15 browser plane),
    ``hitl_config`` (15 approval gating, reusing the v0.3 governance
    ApprovalGate concept). All 7 confirmed present.

Spec provenance:
  * cexai-specs/09_scrapling/spec.md -- US P1 + FR-001/003/004/007 + Key Entities
        (fetch_result) -- ingestion.
  * cexai-specs/11_welib/spec.md -- US P1/P2 + FR-001/002/004/005 + Key Entities
        (WelibSource, Citation) -- research.
  * cexai-specs/14_gitreverse/spec.md -- US P1/P2/P3 + FR-002/004/005/007 + Key
        Entities (reverse_prompt, TriangulationBriefFragment) -- reposynth.
  * cexai-specs/15_auto-browser/spec.md -- US P1/P2 + FR-001/002/003/004/014 +
        Key Entities (auth_profile, BrowserSession, BrowserAction) -- browser.

absorbs: 09_scrapling + 11_welib + 14_gitreverse + 15_auto-browser
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Literal, Protocol, runtime_checkable

__all__ = [
    # ingestion (09 scrapling)
    "FetchStatus",
    "FetchTier",
    "FetchResult",
    "RobotsPolicy",
    # research (11 welib)
    "Citation",
    "WelibQuery",
    # reposynth (14 gitreverse)
    "RepoExtract",
    "ReversePrompt",
    "TriangulationBriefFragment",
    # browser (15 auto-browser)
    "ActionClass",
    "BrowserAction",
    "BrowserActionResult",
    "BrowserSession",
    "AuthProfile",
    # protocols (the seams the impl waves implement)
    "Fetcher",
    "ResearchProvider",
    "RepoSynthesizer",
    "BrowserController",
]

# Immutable empty mapping -- safe shared default for the optional ``headers`` /
# ``params`` / ``frontmatter`` / ``structured`` fields. A frozen dataclass cannot
# take a dict default (mutable); MappingProxyType is read-only, so one shared
# instance is correct.
_EMPTY_CONFIG: Mapping[str, Any] = MappingProxyType({})


# --------------------------------------------------------------------------- #
# Ingestion subsystem (cexai-specs/09_scrapling) -- tier-escalating web fetch.  #
# --------------------------------------------------------------------------- #
# The terminal outcome of a fetch (09 FR-007 / US P1 edge cases). A failed fetch
# returns a typed FetchResult with ``status == "error"`` rather than raising a raw
# exception -- the network / 4xx / 5xx failure rides in ``errors``. ``status``
# stays ``str`` on the dataclass for extension headroom; this Literal is the
# canonical set.
FetchStatus = Literal[
    "ok",
    "error",
]

# The three explicit fetcher tiers (09 FR-001 / US P1 acceptance #1-#3). Tier
# escalation MUST be explicit (declared, never silent -- FR-002): ``basic`` is a
# lightweight HTTP fetch with no bot-bypass overhead, ``stealthy`` adds anti-bot
# bypass (Cloudflare), ``dynamic`` drives a headless browser for JS-SPA DOMs.
# ``Fetcher.fetch`` takes one of these; kept ``str`` on the wire for headroom.
FetchTier = Literal[
    "basic",
    "stealthy",
    "dynamic",
]


@dataclass(frozen=True, slots=True)
class FetchResult:
    """The typed outcome of a single fetch (09 FR-007, Key Entities: fetch_result).
    RUNTIME DATA, not a kind (see module TAXONOMY NOTE). ``status`` is one of
    ``FetchStatus`` (kept ``str`` for headroom); ``content`` is the response body
    on success and ``None`` on error; ``headers`` is the read-only response header
    map; ``from_cache`` is ``True`` when served from the within-TTL cache (09
    FR-004 / the ``[CACHE_HIT]`` path, no network call); ``errors`` is the ordered
    tuple of failure strings (empty on success). A failed fetch is RETURNED, not
    raised (FR-007) -- the raise path is reserved for robots.txt blocks
    (``RobotsBlockedError``)."""

    url: str
    status: str
    content: str | None
    headers: Mapping[str, Any] = _EMPTY_CONFIG
    from_cache: bool = False
    errors: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RobotsPolicy:
    """The robots.txt enforcement policy for a fetch (09 FR-003 / SC-004).
    ``respect`` honors robots.txt by default; an RFC 9309 compliant parser
    enforces it, and a malformed robots.txt FAILS CLOSED (block by default, the
    ``[ROBOTS_MALFORMED]`` path) when ``fail_closed_on_malformed`` is set.
    ``allow_override`` is the single escape hatch: a present ``robots_override``
    artifact (US P1 acceptance #4) lets a declared fetch proceed past a disallow.
    A disallowed path with no override raises ``RobotsBlockedError(url,
    robots_rule)``."""

    respect: bool = True
    fail_closed_on_malformed: bool = True
    allow_override: bool = False


# --------------------------------------------------------------------------- #
# Research subsystem (cexai-specs/11_welib) -- typed academic-source retrieval.  #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class Citation:
    """A single bibliographic reference (11 US P2, Key Entities: Citation). The
    impl wave persists these via the existing ``citation`` kind; this is their
    runtime shape. ``authors`` is an ordered read-only tuple; ``year`` is the
    publication year (``None`` if unknown); ``isbn_or_doi`` is the stable
    identifier (``None`` when neither is available); ``url`` points at the source;
    ``accessed_at`` is the ISO-8601 retrieval timestamp (the audit anchor, 11
    FR-006). A derived artifact that reuses welib content verbatim or as a
    >= 50-word paraphrase (11 US P2 / V11-F2) MUST carry the originating
    ``Citation``."""

    title: str
    authors: tuple[str, ...]
    year: int | None
    isbn_or_doi: str | None
    url: str
    accessed_at: str


@dataclass(frozen=True, slots=True)
class WelibQuery:
    """A topic query against a welib ``rag_source`` (11 US P1 / FR-002). ``topic``
    is the natural-language search; ``max_results`` caps the ranked references
    returned. ``max_results >= bulk_threshold`` is the ETHICAL-USE tripwire (11
    FR-004 / Principle WL2, default N=10): a query asking for the threshold or more
    references is REFUSED with ``BulkDownloadRefusedError(requested, threshold)``
    -- welib is a metadata + excerpt channel, not a bulk-download pipe. The
    refusal is the impl layer's concern; this is a dumb typed container
    (Article VIII)."""

    topic: str
    max_results: int = 5
    bulk_threshold: int = 10


# --------------------------------------------------------------------------- #
# Reposynth subsystem (cexai-specs/14_gitreverse) -- repo -> reusable prompt.    #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class RepoExtract:
    """The read-only extraction of a public repo (14 FR-002), the input to
    synthesis. ``source_url`` is the canonical repo URL; ``tree_sha`` is the
    platform tree SHA of the default branch at fetch time (the cache + determinism
    key, FR-003/006); ``default_branch`` / ``primary_language`` / ``description``
    are the repo metadata; ``file_tree`` is the SORTED tuple of file paths (sorted
    for FR-006 byte determinism), truncated at the file-count budget when
    ``truncated`` is ``True`` (E1, default budget 5,000 paths); ``readme`` is the
    README content; ``entry_files`` is the read-only ``path -> content`` map of up
    to 10 entry-point files (e.g. ``pyproject.toml``, ``package.json``). Every
    field is read-only -- extraction never mutates the upstream repo."""

    source_url: str
    tree_sha: str
    default_branch: str
    primary_language: str
    description: str
    file_tree: tuple[str, ...]
    readme: str
    entry_files: Mapping[str, str] = _EMPTY_CONFIG
    truncated: bool = False


@dataclass(frozen=True, slots=True)
class ReversePrompt:
    """The runtime PROJECTION of a synthesized ``reverse_prompt`` artifact (14 US
    P1, Key Entities). The persisted ``.md`` artifact (kind ``reverse_prompt``,
    registered by the vertical-14 impl ADR cell -- NOT this wave) is written under
    ``.cex/runtime/artifacts/reverse_prompts/<tree_sha>.md``; this dataclass is its
    in-memory shape. ``source_url`` / ``tree_sha`` carry provenance; ``open_vars``
    is the ordered tuple of the 3 declared open-var NAMES (``target_audience``,
    ``target_runtime``, ``complexity_level`` per FR-005); ``filled_vars`` is the
    read-only resolved ``name -> value`` map (the frozen ``_filled_vars`` per ADR
    022); ``body`` is the synthesized reconstruction prompt; ``frontmatter`` is the
    read-only artifact frontmatter map. Output is deterministic for a given
    ``(tree_sha, filled_vars)`` tuple (FR-006)."""

    source_url: str
    tree_sha: str
    open_vars: tuple[str, ...]
    filled_vars: Mapping[str, str]
    body: str
    frontmatter: Mapping[str, Any] = _EMPTY_CONFIG


@dataclass(frozen=True, slots=True)
class TriangulationBriefFragment:
    """One source's contribution to auto-research triangulation (14 US P2 / FR-007).
    The ``repo_synthesizer`` acts as a 4th source alongside scrapling / claude-mem
    / welib; when a research intent names a recognizable repo URL it returns one
    of these (or empty, never an exception, if the source is unavailable -- US P2
    acceptance #5). ``source`` is the source id (e.g. ``"repo_synthesizer"``);
    ``confidence`` is the source-quality score in ``[0.0, 1.0]`` computed from
    extraction completeness (US P2 acceptance #4); ``body`` is the brief text the
    compiler folds into Layer-1 context assembly."""

    source: str
    confidence: float
    body: str


# --------------------------------------------------------------------------- #
# Browser subsystem (cexai-specs/15_auto-browser) -- policy-gated automation.    #
# --------------------------------------------------------------------------- #
# The per-action read/write classification the policy engine assigns (15 FR-003).
# ``read`` actions (GET, screenshot, OCR) run without approval on read-only
# domains; ``write`` actions (POST, form-submit, payment, account-change) on a
# write-capable domain are gated through the approval queue (FR-004) -> the caller
# receives ``ApprovalPendingError`` until a human verdict resolves it.
ActionClass = Literal[
    "read",
    "write",
]


@dataclass(frozen=True, slots=True)
class BrowserAction:
    """One requested action against a browser session (15 US P2). ``action_id`` is
    the stable id (the audit + approval-queue key); ``action_type`` is the verb
    (e.g. ``navigate``, ``submit``, ``screenshot``); ``target`` is the URL / form
    id / selector it acts on; ``action_class`` is one of ``ActionClass`` (kept
    ``str`` for headroom) -- a ``write`` on a write-capable domain trips the
    approval gate (FR-004); ``params`` is the read-only argument map. Write gating
    composes with ``cexai.governance`` HITL (an ``ApprovalRequest`` flows through
    the governance ApprovalGate); this dataclass does NOT redefine that
    vocabulary."""

    action_id: str
    action_type: str
    target: str
    action_class: str = "read"
    params: Mapping[str, Any] = _EMPTY_CONFIG


@dataclass(frozen=True, slots=True)
class BrowserActionResult:
    """The typed result of an executed ``BrowserAction`` (15 FR-014). Keeps the
    three visible planes DISTINGUISHABLE in the output schema: ``visual_ref`` is
    the Visual plane (a screenshot reference, ``None`` for headless / no-capture
    actions); ``structured`` is the Structured plane (the read-only extracted DOM /
    data map); ``action_taken`` is the Action plane (the descriptor of what was
    performed). ``action_id`` links back to the originating ``BrowserAction``."""

    action_id: str
    action_taken: str
    visual_ref: str | None = None
    structured: Mapping[str, Any] = _EMPTY_CONFIG


@dataclass(frozen=True, slots=True)
class BrowserSession:
    """A persistent, optionally authenticated browser session (15 US P1). The
    impl wave backs it with Playwright; this is its typed handle. ``session_id`` is
    the stable id threaded through every audit event (SC-001: a 5-event workflow
    shares one ``session_id``); ``profile`` is the ``AuthProfile`` name whose
    encrypted auth-state is loaded (``None`` for an anonymous session); ``target``
    is the start URL; ``status`` is the lifecycle state (e.g. ``active``,
    ``paused`` while awaiting a noVNC takeover, ``closed``); ``started_at`` is the
    ISO-8601 start timestamp."""

    session_id: str
    profile: str | None
    target: str
    status: str
    started_at: str


@dataclass(frozen=True, slots=True)
class AuthProfile:
    """A reusable, encrypted-at-rest browser auth profile (15 US P1 / FR-002).
    ``name`` is the profile handle (e.g. ``"github-bot"``); ``encrypted_at_rest``
    is the marker asserting the auth-state is stored encrypted (SC-005: a leaked
    ``auth_state/`` dir without the key cannot be replayed) -- it defaults ``True``
    and an impl wave that cannot guarantee encryption must set it ``False``
    explicitly; ``max_age_days`` is the profile freshness bound (US P1 acceptance
    #2, default 7) after which it is treated as stale; ``created_at`` is the
    ISO-8601 creation timestamp (``None`` until first persisted)."""

    name: str
    encrypted_at_rest: bool = True
    max_age_days: int = 7
    created_at: str | None = None


# --------------------------------------------------------------------------- #
# Protocols -- the seams the impl waves implement. Structural (no base class     #
# required); runtime_checkable allows isinstance smoke checks. Each maps to a    #
# contract test signature frozen in tests/tools/contract.                        #
# --------------------------------------------------------------------------- #
@runtime_checkable
class Fetcher(Protocol):
    """The tier-escalating web-fetch seam (09 US P1 / FR-001/007). ``fetch``
    retrieves ``url`` using the declared ``tier`` (one of ``FetchTier``) and
    returns a typed ``FetchResult`` -- a network / HTTP failure rides in
    ``FetchResult.errors`` with ``status == "error"`` rather than raising (FR-007);
    a robots.txt disallow with no override raises ``RobotsBlockedError``. The impl
    wave ships the concrete 3-tier fetcher (basic / stealthy / dynamic, via the
    vertical-08 MCP loader); the contract test ``test_fetcher_returns_result``
    drives it RED->GREEN."""

    def fetch(self, url: str, tier: str) -> FetchResult:
        """Fetch ``url`` at ``tier`` and return a typed ``FetchResult``."""
        ...


@runtime_checkable
class ResearchProvider(Protocol):
    """The academic-source retrieval seam (11 US P1 / FR-002). ``search`` consumes
    a ``WelibQuery`` and returns a ranked tuple of ``Citation`` (empty on no match
    -- never fabricated). A query at or above its ``bulk_threshold`` is refused
    with ``BulkDownloadRefusedError`` (FR-004); an unreachable welib falls back to
    arXiv (FR-007). The impl wave ships the concrete provider (welib over the 09
    stealthy fetcher); the contract test ``test_research_provider_cites`` drives
    it."""

    def search(self, query: WelibQuery) -> tuple[Citation, ...]:
        """Return a ranked tuple of ``Citation`` for ``query`` (empty on no match)."""
        ...


@runtime_checkable
class RepoSynthesizer(Protocol):
    """The repo -> reverse-prompt synthesis seam (14 US P1 / FR-004). ``synthesize``
    extracts ``repo_url`` (metadata + sorted file tree + README + <= 10 entry
    files), substitutes ``filled_vars`` into the prompt template, calls the LLM
    through ``cexai.foundation.invocation.router`` at temperature 0.0, and returns
    a deterministic ``ReversePrompt`` projection (FR-006). A LICENSE-incompatible
    target raises ``LicenseCompatibilityError`` (fail-closed, E2); a no-LICENSE
    target emits ``LicenseUnknownWarning`` and proceeds (E3). The impl wave ships
    the concrete synthesizer; the contract test
    ``test_repo_synthesizer_projects_reverse_prompt`` drives it."""

    def synthesize(self, repo_url: str, filled_vars: Mapping[str, str]) -> ReversePrompt:
        """Synthesize ``repo_url`` into a typed ``ReversePrompt`` projection."""
        ...


@runtime_checkable
class BrowserController(Protocol):
    """The policy-gated browser-automation seam (15 US P2 / FR-003/004). ``execute``
    runs a ``BrowserAction`` against an open session and returns a typed
    ``BrowserActionResult`` (the three Visual / Structured / Action planes, FR-014).
    A ``write``-class action on a write-capable domain is enqueued for human
    approval and raises ``ApprovalPendingError`` to the caller until resolved (US
    P2) -- the gating composes with the v0.3 ``cexai.governance`` ApprovalGate +
    audit subsystems, which this seam references rather than duplicates. The impl
    wave ships the concrete Playwright-backed controller behind the vertical-08 MCP
    gateway; the contract test ``test_browser_controller_executes`` drives it."""

    def execute(self, action: BrowserAction) -> BrowserActionResult:
        """Execute ``action`` and return its typed ``BrowserActionResult``."""
        ...
