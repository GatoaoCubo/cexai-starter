"""BrowserSession lifecycle helpers (15 US P1 / P3).

The frozen ``BrowserSession`` (``cexai.tools._shared.types``) is an immutable
dataclass -- a session's lifecycle is therefore a sequence of NEW instances, each
preserving the stable ``session_id`` that threads the audit trail (SC-001).
``start_session`` opens an ``active`` session; ``pause`` (awaiting a noVNC human
takeover, US P3), ``resume`` (post-takeover), and ``close`` return successor
sessions with the updated ``status``. No live browser is started here -- this is
the typed handle the controller + MCP gateway carry; backend attachment is the
injected ``BrowserBackend``'s concern.

Offline (Article XIV): ``session_id`` and ``started_at`` are generated locally
(uuid + UTC clock) and are injectable for deterministic tests.

absorbs: 15_auto-browser
"""

from __future__ import annotations

import uuid
from dataclasses import replace
from datetime import datetime, timezone

from cexai.tools._shared.types import BrowserSession

__all__ = ["start_session", "pause", "resume", "close"]


def _now_iso() -> str:
    """Current UTC instant (tz-aware) as ISO-8601 -- the session start stamp."""
    return datetime.now(timezone.utc).isoformat()


def start_session(
    target: str,
    *,
    profile: str | None = None,
    session_id: str | None = None,
    started_at: str | None = None,
) -> BrowserSession:
    """Open a new ``active`` session for ``target``. ``profile`` is the optional
    ``AuthProfile`` name whose encrypted auth-state will be loaded (``None`` for an
    anonymous session); ``session_id`` / ``started_at`` are generated when omitted."""
    return BrowserSession(
        session_id=session_id if session_id is not None else "sess-" + uuid.uuid4().hex[:12],
        profile=profile,
        target=target,
        status="active",
        started_at=started_at if started_at is not None else _now_iso(),
    )


def pause(session: BrowserSession) -> BrowserSession:
    """Return a ``paused`` successor (awaiting a noVNC human takeover, US P3) --
    the original session is unchanged (frozen)."""
    return replace(session, status="paused")


def resume(session: BrowserSession) -> BrowserSession:
    """Return an ``active`` successor (control returned to the agent post-takeover)."""
    return replace(session, status="active")


def close(session: BrowserSession) -> BrowserSession:
    """Return a ``closed`` successor (the session is terminated)."""
    return replace(session, status="closed")
