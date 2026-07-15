"""Browser subsystem -- policy-gated browser automation (impl: v0.4 impl wave).

Playwright-backed persistent sessions with encrypted-at-rest auth-profile reuse, a
policy engine that classifies actions read/write against a host allowlist, an
approval queue that gates write-capable actions (raising ``ApprovalPendingError``
to the caller), and noVNC human takeover for stuck challenges (cexai-specs/
15_auto-browser FR-001..015). Exposed via the vertical-08 MCP gateway. Write
gating and audit COMPOSE with the v0.3 ``cexai.governance`` HITL ApprovalGate +
audit subsystems -- this subsystem references them, it does not reimplement them.
The frozen ``BrowserAction`` / ``BrowserActionResult`` / ``BrowserSession`` /
``AuthProfile`` / ``BrowserController`` contracts live in ``cexai.tools._shared.
types``.

absorbs: 15_auto-browser
"""

from cexai.tools.browser.auth_profile import AuthProfileStore, Cipher
from cexai.tools.browser.controller import (
    BrowserBackend,
    HostWritePolicy,
    PlaywrightBrowserController,
    UnconfiguredWritePolicyWarning,
    WritePolicy,
)
from cexai.tools.browser.session import close, pause, resume, start_session

__all__ = [
    # controller (the frozen BrowserController seam + policy/backend seams)
    "PlaywrightBrowserController",
    "BrowserBackend",
    "WritePolicy",
    "HostWritePolicy",
    "UnconfiguredWritePolicyWarning",
    # auth-profile persistence (encrypted at rest)
    "AuthProfileStore",
    "Cipher",
    # session lifecycle
    "start_session",
    "pause",
    "resume",
    "close",
]
