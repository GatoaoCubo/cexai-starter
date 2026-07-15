"""RFC 9309-style robots.txt parsing + enforcement (09 scrapling FR-003 / SC-004).

A small, dependency-free parser sufficient for the fetcher's gate:

  * groups records by ``User-agent`` (consecutive agents share the following
    rules, per RFC 9309 section 2.2.1);
  * matches the most specific group (exact user-agent over ``*``);
  * picks the longest-matching path rule, with ``Allow`` winning ties
    (RFC 9309 section 2.2.2), and supports the ``*`` wildcard + ``$`` end-anchor;
  * flags a non-empty body with ZERO recognized directives as MALFORMED -- the
    fetcher fail-closes on that when the policy says so (the ``[ROBOTS_MALFORMED]``
    path). A genuinely empty robots.txt (or one that is only comments/sitemaps) is
    NOT malformed -- absence of rules means "allow all" (RFC 9309 section 2.2.3).

The fetcher owns the decision to RAISE (``RobotsBlockedError``); this module is a
pure value object -- it reports allow/deny + the matched rule and never does I/O.

absorbs: 09_scrapling
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

__all__ = ["RobotsTxt", "RobotsDecision"]

# Directive keys this parser recognizes. A robots.txt with none of these (after
# stripping comments/blanks) but with meaningful content is treated as malformed
# (e.g. an HTML error / captcha page served in place of robots.txt).
_KNOWN_KEYS = frozenset(
    {"user-agent", "allow", "disallow", "crawl-delay", "sitemap", "host", "noindex"}
)
# Keys that group rules under a user-agent record.
_RULE_KEYS = frozenset({"allow", "disallow"})


@dataclass(frozen=True, slots=True)
class RobotsDecision:
    """The outcome of an ``is_allowed`` check. ``allowed`` is the verdict;
    ``rule`` is the matched directive pattern (e.g. ``"/private"``) when a
    ``Disallow`` blocked the path, else ``None``."""

    allowed: bool
    rule: str | None = None


@dataclass(frozen=True, slots=True)
class _Group:
    agents: tuple[str, ...]
    # ordered (kind, pattern) where kind in {"allow","disallow"}
    rules: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class RobotsTxt:
    """A parsed robots.txt. ``malformed`` is ``True`` when the body had meaningful
    content but no recognized directive. Build with ``parse``; query with
    ``is_allowed``."""

    groups: tuple[_Group, ...] = field(default_factory=tuple)
    malformed: bool = False

    # -- parsing ------------------------------------------------------------- #
    @classmethod
    def parse(cls, text: str) -> RobotsTxt:
        groups: list[_Group] = []
        agents: list[str] = []
        rules: list[tuple[str, str]] = []
        seen_rule = False
        recognized = 0
        meaningful = 0

        def _flush() -> None:
            if agents:
                groups.append(_Group(agents=tuple(agents), rules=tuple(rules)))

        for raw in text.splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            meaningful += 1
            if ":" not in line:
                continue  # unrecognized non-directive line
            key, _, value = line.partition(":")
            key = key.strip().lower()
            value = value.strip()
            if key not in _KNOWN_KEYS:
                continue
            recognized += 1
            if key == "user-agent":
                # A user-agent after a rule starts a fresh group.
                if seen_rule:
                    _flush()
                    agents = []
                    rules = []
                    seen_rule = False
                agents.append(value.lower())
            elif key in _RULE_KEYS:
                # A rule before any user-agent is ignored (no group to bind to).
                if agents:
                    rules.append((key, value))
                    seen_rule = True
            # sitemap / host / crawl-delay / noindex do not affect allow decisions.
        _flush()

        malformed = meaningful > 0 and recognized == 0
        return cls(groups=tuple(groups), malformed=malformed)

    # -- enforcement --------------------------------------------------------- #
    def is_allowed(self, path: str, user_agent: str = "*") -> RobotsDecision:
        """Decide whether ``path`` may be fetched for ``user_agent``. Absence of a
        matching rule => allowed (RFC 9309 section 2.2.3)."""
        group = self._select_group(user_agent)
        if group is None:
            return RobotsDecision(allowed=True)

        best_len = -1
        best_allow = True
        best_rule: str | None = None
        for kind, pattern in group.rules:
            if not pattern:
                # An empty Disallow value means "allow everything" -- no constraint.
                continue
            if not _path_matches(pattern, path):
                continue
            specificity = len(pattern)
            # Longest match wins; on a tie Allow beats Disallow (RFC 9309 2.2.2).
            if specificity > best_len or (
                specificity == best_len and kind == "allow"
            ):
                best_len = specificity
                best_allow = kind == "allow"
                best_rule = pattern
        if best_len < 0:
            return RobotsDecision(allowed=True)
        return RobotsDecision(
            allowed=best_allow, rule=None if best_allow else best_rule
        )

    def _select_group(self, user_agent: str) -> _Group | None:
        ua = user_agent.lower()
        wildcard: _Group | None = None
        for group in self.groups:
            if ua in group.agents:
                return group  # exact match is the most specific
            if "*" in group.agents and wildcard is None:
                wildcard = group
        return wildcard


def _path_matches(pattern: str, path: str) -> bool:
    """RFC 9309 path matching: prefix match with ``*`` wildcard and optional ``$``
    end-anchor. ``/private`` matches ``/private/secret``; ``/*.pdf$`` matches a path
    ending in ``.pdf``."""
    anchored = pattern.endswith("$")
    core = pattern[:-1] if anchored else pattern
    regex = ["^"]
    for ch in core:
        regex.append(".*" if ch == "*" else re.escape(ch))
    if anchored:
        regex.append("$")
    return re.match("".join(regex), path) is not None
