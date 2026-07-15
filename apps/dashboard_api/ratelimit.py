# -*- coding: ascii -*-
"""Per-tenant rate limiting + concurrency capping for the dashboard API (Sec 5b HIGH gaps).

Closes the two centralized-data-plane HIGH gaps the multi-tenant review surfaced
(_output/cex_multitenant_from_zero_map.md Sec 5b):

  * "[HIGH] Sem rate-limit / quota por-tenant no data-plane" -- one compromised JWT can
    drive unlimited load/cost against the shared project.
  * "[HIGH] Pool exhaustion / noisy-neighbor" -- one tenant can exhaust the shared
    Supavisor pool and starve every other tenant.

Both are keyed on the VERIFIED tenant_id (the JWT claim resolved by auth.extract_tenant_id),
NEVER on a client-supplied body/header/query value -- the key is the same trusted identity
the rest of the API scopes on. The limiter sits AFTER auth (auth is the fail-closed
chokepoint: no/invalid token -> 401 before this code runs), so by the time we have a key it
is already a verified tenant.

TWO PRIMITIVES (both in-process, no Redis -- a single uvicorn worker; see NOTES on scale):
  1. TokenBucketLimiter -- a classic token bucket per tenant_id. Smooth refill at
     rpm/60 tokens/sec with a burst ceiling. Over the limit -> a 429 with a computed
     Retry-After (seconds until the next token). Thread-safe (one lock; the bucket math is
     O(1) under the lock). This bounds the SUSTAINED request RATE per tenant.
  2. TenantConcurrencyCap -- a per-tenant in-flight counter (a semaphore-by-count). The
     N+1th SIMULTANEOUS request for one tenant is rejected (429) rather than queued, so a
     burst of concurrent requests from one tenant cannot each grab a pooled DB connection
     and exhaust the shared pool. This bounds the CONCURRENCY per tenant (the pool guard).

DEGRADE CHOICE -- FAIL-OPEN-WITH-LOG (justified):
  A rate limiter / concurrency cap is an AVAILABILITY PROTECTION, not an authorization
  control. If the limiter's OWN bookkeeping raises (a bug, an exhausted process), DENYING
  the request would convert a guard defect into a self-inflicted outage for every tenant --
  the opposite of the gap's intent. So the dependency NEVER lets its own internal error
  crash or block a request: it logs a structured WARNING (secret-free; the tenant_id is the
  only id, and a tenant_id is not a secret) and ADMITS the request. The actual limit
  decision (over-limit -> 429) is deliberate and DOES block -- that is the feature, not a
  failure. (Auth, the security-critical layer, stays fail-CLOSED upstream; this layer
  protects availability and so fails OPEN.) The concurrency cap ALWAYS releases its slot in
  a finally, so a downstream handler error can never leak an in-flight slot.

ENABLEMENT -- SAFE-DEFAULT OFF (justified):
  Like the data-plane session factory (deps.SESSION_FACTORY_ENV is OFF by default), the
  limiter is OFF unless explicitly enabled via CEXAI_TENANT_RATE_LIMIT_ENABLED=1. Reason:
  this is the centralized control plane; turning on a limiter that can 429 legitimate
  traffic is an operational decision an operator must make deliberately (after picking an
  RPM that fits their tenants), never a silent default that could throttle a live tenant on
  deploy. When disabled, the dependency is a transparent pass-through (zero behavior change
  -- this is what keeps the existing suite byte-green). Enabling is one env var.

ASCII-only per .claude/rules/ascii-code-rule.md. Fully type-hinted. No network/secret read.
Thread-safe (threading primitives only; safe under uvicorn's threadpool for sync deps).
"""

from __future__ import annotations

import os
import sys
import threading
import time
from typing import Callable, Dict, Optional, Tuple

from fastapi.responses import JSONResponse

from .auth import AuthError

__all__ = [
    "TokenBucketLimiter",
    "TenantConcurrencyCap",
    "RateLimitExceeded",
    "ConcurrencyLimitExceeded",
    "install_tenant_guards",
    "limiter_enabled",
    "ENV_ENABLED",
    "ENV_RPM",
    "ENV_BURST",
    "ENV_MAX_INFLIGHT",
    "DEFAULT_RPM",
    "DEFAULT_MAX_INFLIGHT",
]

# --------------------------------------------------------------------------- #
# Env knobs (all server-side; none is a secret).
# --------------------------------------------------------------------------- #
# Master switch -- OFF by default (safe-default; see module docstring). Truthy values:
# "1", "true", "yes", "on" (case-insensitive).
ENV_ENABLED = "CEXAI_TENANT_RATE_LIMIT_ENABLED"
# Sustained requests/minute per tenant (the token refill rate). A sane default that
# comfortably covers an interactive dashboard user yet caps a runaway loop.
ENV_RPM = "CEXAI_TENANT_RATE_LIMIT_RPM"
# Burst ceiling (max tokens a tenant can accumulate / spend at once). Defaults to the RPM
# so a tenant may burst up to one minute's allowance, then is held to the refill rate.
ENV_BURST = "CEXAI_TENANT_RATE_LIMIT_BURST"
# Max simultaneous in-flight requests per tenant (the pool guard). Defaults to a small
# number: enough for an interactive UI's parallel fetches, low enough that one tenant
# cannot grab a large share of the shared DB pool at once.
ENV_MAX_INFLIGHT = "CEXAI_TENANT_MAX_INFLIGHT"

DEFAULT_RPM = 120  # 2 req/sec sustained per tenant
DEFAULT_MAX_INFLIGHT = 8  # simultaneous in-flight requests per tenant

_TRUTHY = frozenset({"1", "true", "yes", "on"})


def _env_truthy(name: str, *, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in _TRUTHY


def _env_int(name: str, default: int, *, minimum: int = 1) -> int:
    """Read a positive int env knob, clamped to >= minimum, default on any parse failure."""
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        value = int(raw.strip())
    except (TypeError, ValueError):
        return default
    return value if value >= minimum else minimum


def limiter_enabled() -> bool:
    """True iff the per-tenant guards are explicitly enabled (CEXAI_TENANT_RATE_LIMIT_ENABLED).

    Read live (per app build) so a deployment flips the guards with one env var, and the
    existing offline suite -- which never sets it -- sees the transparent pass-through."""
    return _env_truthy(ENV_ENABLED, default=False)


# --------------------------------------------------------------------------- #
# Exceptions (mapped to 429 by the dependencies; never escape unhandled).
# --------------------------------------------------------------------------- #
class RateLimitExceeded(Exception):
    """A tenant exceeded its sustained request rate. Carries retry_after (seconds, int>=1)."""

    def __init__(self, tenant_id: str, retry_after: int) -> None:
        self.tenant_id = tenant_id
        self.retry_after = retry_after
        super().__init__("rate limit exceeded for tenant")


class ConcurrencyLimitExceeded(Exception):
    """A tenant exceeded its max in-flight concurrency (the pool guard). retry_after=1s."""

    def __init__(self, tenant_id: str, limit: int) -> None:
        self.tenant_id = tenant_id
        self.limit = limit
        self.retry_after = 1
        super().__init__("concurrency limit exceeded for tenant")


# --------------------------------------------------------------------------- #
# Override hook -- a per-tenant limit resolver. The DEFAULT returns None (use the
# global env limits); a deployment can inject a callable to raise/lower limits per
# tenant (e.g. an enterprise tenant gets a higher RPM). The hook is pure + best-effort
# (a raising hook degrades to the global default -- never blocks a request).
# --------------------------------------------------------------------------- #
# A per-tenant override returns (rpm, burst) or None to fall back to the global env limits.
RateOverride = Callable[[str], Optional[Tuple[int, int]]]


def _no_override(_tenant_id: str) -> Optional[Tuple[int, int]]:
    return None


# --------------------------------------------------------------------------- #
# Token bucket -- per-tenant sustained-rate limiter.
# --------------------------------------------------------------------------- #
class _Bucket:
    """One tenant's token bucket: ``tokens`` available, refilled at ``rate`` tokens/sec up
    to ``capacity``. ``updated`` is the monotonic timestamp of the last refill. Plain data;
    all access is under the limiter's lock."""

    __slots__ = ("tokens", "capacity", "rate", "updated")

    def __init__(self, capacity: float, rate: float, now: float) -> None:
        self.tokens = capacity
        self.capacity = capacity
        self.rate = rate
        self.updated = now


class TokenBucketLimiter:
    """Thread-safe, in-process per-tenant token-bucket rate limiter.

    One bucket per tenant_id, created on first sight. ``check(tenant_id)`` consumes one
    token; if the bucket is empty it raises RateLimitExceeded with a Retry-After (the whole
    seconds until the next token refills). Refill is lazy (computed from elapsed time on each
    check) so there is no background thread.

    Limits come from the env (rpm + burst) unless a per-tenant override callable returns a
    (rpm, burst) pair. The bucket's capacity/rate are re-derived on each check from the
    resolved limits, so an override or env change takes effect on the next request (and a
    raised limit immediately enlarges the ceiling; a lowered one clamps tokens down).

    A monotonic clock is injectable for deterministic tests (``time_fn``)."""

    def __init__(
        self,
        *,
        rpm: int,
        burst: int,
        override: Optional[RateOverride] = None,
        time_fn: Callable[[], float] = time.monotonic,
    ) -> None:
        self._rpm = max(1, int(rpm))
        self._burst = max(1, int(burst))
        self._override = override or _no_override
        self._time = time_fn
        self._lock = threading.Lock()
        self._buckets: Dict[str, _Bucket] = {}

    def _resolve_limits(self, tenant_id: str) -> Tuple[float, float]:
        """Resolve (capacity, rate_per_sec) for a tenant: the override wins, else the env
        defaults. Best-effort: a raising/garbage override degrades to the global limits
        (never blocks a request on a bad hook)."""
        rpm, burst = self._rpm, self._burst
        try:
            ov = self._override(tenant_id)
        except Exception:
            ov = None
        if ov is not None:
            try:
                o_rpm, o_burst = ov
                rpm = max(1, int(o_rpm))
                burst = max(1, int(o_burst))
            except Exception:
                rpm, burst = self._rpm, self._burst
        return float(burst), float(rpm) / 60.0

    def check(self, tenant_id: str) -> None:
        """Consume one token for ``tenant_id`` or raise RateLimitExceeded.

        Thread-safe (the read-modify-write of the bucket is under one lock). On success,
        returns None (one token spent). On exhaustion, raises with retry_after = ceil
        seconds until >=1 token is available."""
        now = self._time()
        with self._lock:
            capacity, rate = self._resolve_limits(tenant_id)
            bucket = self._buckets.get(tenant_id)
            if bucket is None:
                bucket = _Bucket(capacity=capacity, rate=rate, now=now)
                self._buckets[tenant_id] = bucket
            else:
                # Re-derive limits (override/env may have changed) and refill by elapsed.
                bucket.capacity = capacity
                bucket.rate = rate
                elapsed = now - bucket.updated
                if elapsed > 0:
                    bucket.tokens = min(capacity, bucket.tokens + elapsed * rate)
                    bucket.updated = now
                # Clamp down if capacity shrank below the current token count.
                if bucket.tokens > capacity:
                    bucket.tokens = capacity
            if bucket.tokens >= 1.0:
                bucket.tokens -= 1.0
                return
            # Empty: compute the wait until the next whole token.
            deficit = 1.0 - bucket.tokens
            wait_s = deficit / rate if rate > 0 else 1.0
            retry_after = max(1, int(wait_s) + (1 if wait_s % 1 else 0))
        raise RateLimitExceeded(tenant_id, retry_after)


# --------------------------------------------------------------------------- #
# Concurrency cap -- per-tenant in-flight counter (the pool guard).
# --------------------------------------------------------------------------- #
class TenantConcurrencyCap:
    """Thread-safe, in-process per-tenant in-flight concurrency cap.

    Bounds how many requests for ONE tenant may be in flight (holding a request, and thus
    potentially a pooled DB connection) at the same time. ``acquire(tenant_id)`` increments
    the tenant's counter if it is below ``limit`` and returns a release callable; if the
    tenant is already at ``limit`` it raises ConcurrencyLimitExceeded (the N+1th concurrent
    request is rejected, NOT queued -- rejecting is what protects the shared pool from a
    burst). The caller MUST invoke the returned release in a finally (the dependency does).

    This is a fail-fast admission control, not a blocking semaphore: a tenant's burst of
    concurrent requests is shed (429 + Retry-After: 1) instead of all waiting on (and
    grabbing) pooled connections. Different tenants have independent counters, so one
    tenant's saturation never rejects another's request."""

    def __init__(self, *, limit: int) -> None:
        self._limit = max(1, int(limit))
        self._lock = threading.Lock()
        self._inflight: Dict[str, int] = {}

    @property
    def limit(self) -> int:
        return self._limit

    def acquire(self, tenant_id: str) -> Callable[[], None]:
        """Reserve one in-flight slot for ``tenant_id`` or raise ConcurrencyLimitExceeded.

        Returns a release callable (idempotent) the caller MUST run in a finally so the slot
        is freed even if the downstream handler raises."""
        with self._lock:
            current = self._inflight.get(tenant_id, 0)
            if current >= self._limit:
                raise ConcurrencyLimitExceeded(tenant_id, self._limit)
            self._inflight[tenant_id] = current + 1

        released = {"done": False}

        def _release() -> None:
            if released["done"]:
                return
            released["done"] = True
            with self._lock:
                n = self._inflight.get(tenant_id, 0)
                if n <= 1:
                    # Drop the key when it hits zero so the map does not grow unbounded
                    # with one entry per tenant ever seen.
                    self._inflight.pop(tenant_id, None)
                else:
                    self._inflight[tenant_id] = n - 1

        return _release


# --------------------------------------------------------------------------- #
# Structured warning (FAIL-OPEN log; secret-free).
# --------------------------------------------------------------------------- #
def _warn_guard(stage: str, tenant_id: str, detail: str) -> None:
    """Emit a one-line stderr WARNING when a guard FAILS OPEN on its own internal error.

    Secret-free: the only id is tenant_id (a UUID, not a secret) and a short detail string.
    NEVER raises -- logging must not be the thing that breaks a request."""
    try:
        sys.stderr.write(
            "[WARN] tenant-guard %s fail-open (tenant=%s): %s\n" % (stage, tenant_id, detail)
        )
    except Exception:
        pass


# --------------------------------------------------------------------------- #
# 429 response shaping (matches main.py's {"error": {type, reason, detail}} envelope).
# --------------------------------------------------------------------------- #
def _too_many_requests(reason: str, retry_after: int) -> JSONResponse:
    """A 429 with a Retry-After header, in the SAME error envelope every other failure uses
    (so the frontend's single ApiClientError path handles it). The body never names the
    tenant (defence-in-depth: do not echo the identity back) -- only the machine reason."""
    ra = max(1, int(retry_after))
    return JSONResponse(
        status_code=429,
        headers={"Retry-After": str(ra)},
        content={
            "error": {
                "type": "rate_limited",
                "reason": reason,
                "detail": "per-tenant %s; retry after %ds" % (reason, ra),
            }
        },
    )


# --------------------------------------------------------------------------- #
# The verified-tenant key resolver (THE security-critical part).
# --------------------------------------------------------------------------- #
def _verified_tenant_key(authorization: Optional[str]) -> str:
    """Resolve the rate-limit KEY from the VERIFIED JWT -- the SAME chokepoint the routes
    use (main._tenant_from_authorization), re-derived here so the limiter binds to the
    trusted claim, NEVER to a client-supplied body/header/query value.

    Imported lazily from main to avoid an import cycle (main imports this module). Raises
    AuthError on a missing/invalid token (no/invalid token -> the limiter never runs; the
    request is already 401 at the route's own auth call)."""
    from .main import _tenant_from_authorization  # lazy: avoid import cycle

    return _tenant_from_authorization(authorization)


# --------------------------------------------------------------------------- #
# The guard core -- applies BOTH guards for a request, given the raw Authorization header.
# admit() returns either a release callable (ADMIT; the caller MUST run it in a finally) OR
# a JSONResponse (DENY -> send it as-is). The whole policy lives here in ONE place; the
# middleware (install_tenant_guards) is the only caller.
# --------------------------------------------------------------------------- #
class _Guards:
    """Bundles the rate limiter + concurrency cap and applies them per request.

    ``admit(authorization)`` is the single decision point:
      * NO verified tenant (AuthError) -> ADMIT with a no-op release. Deliberate: the
        limiter is keyed on the verified tenant; with no trusted key there is nothing to
        rate-limit. An authed route still 401s via its own _tenant_from_authorization call;
        a no-auth route (e.g. /healthz) is correctly never per-tenant limited. The guard
        NEVER changes the auth outcome.
      * rate limit exceeded -> return the 429 (rate) response; no slot taken.
      * concurrency cap exceeded -> return the 429 (concurrency) response; no slot taken.
      * admit -> reserve a concurrency slot and return its release callable.
      * the guard's OWN bookkeeping error -> FAIL-OPEN: log + admit (no-op release).
    """

    def __init__(self, limiter: "TokenBucketLimiter", cap: "TenantConcurrencyCap") -> None:
        self._limiter = limiter
        self._cap = cap

    @staticmethod
    def _noop() -> None:
        return None

    def admit(self, authorization: Optional[str]):
        """Return (release_callable, None) to ADMIT, or (None, JSONResponse) to DENY."""
        try:
            tenant_id = _verified_tenant_key(authorization)
        except AuthError:
            # No verified tenant -> nothing to key on; admit (route auth handles any 401).
            return self._noop, None

        # 1. Sustained-rate token bucket (cheap; charged before holding a slot).
        try:
            self._limiter.check(tenant_id)
        except RateLimitExceeded as exc:
            return None, _too_many_requests("rate_limit_exceeded", exc.retry_after)
        except Exception as exc:  # limiter's OWN error -> FAIL-OPEN with log
            _warn_guard("rate", tenant_id, str(exc))
            return self._noop, None

        # 2. Per-tenant in-flight concurrency cap (the pool guard).
        try:
            release = self._cap.acquire(tenant_id)
        except ConcurrencyLimitExceeded as exc:
            return None, _too_many_requests("concurrency_limit_exceeded", exc.retry_after)
        except Exception as exc:  # cap's OWN error -> FAIL-OPEN with log (no slot held)
            _warn_guard("concurrency", tenant_id, str(exc))
            return self._noop, None

        # Wrap release so a release-time error can never break the response.
        def _safe_release() -> None:
            try:
                release()
            except Exception as exc:
                _warn_guard("concurrency-release", tenant_id, str(exc))

        return _safe_release, None


# --------------------------------------------------------------------------- #
# Installation -- wire the guards onto an app as HTTP MIDDLEWARE.
#
# WHY MIDDLEWARE (not router dependencies): FastAPI captures a router's `dependencies` per
# route AT REGISTRATION TIME. install_tenant_guards runs AFTER _register_routes (so its
# exception handlers / wiring sit on a fully-built app), at which point appending to
# router.dependencies is a silent no-op -- the already-registered routes never see it. An
# HTTP middleware applies to EVERY route regardless of registration order, runs after CORS,
# and lets us return the 429 directly + release the concurrency slot in a finally around
# call_next. This is the order-independent, can't-silently-drop wiring.
# --------------------------------------------------------------------------- #
def install_tenant_guards(
    application,
    *,
    override: Optional[RateOverride] = None,
    time_fn: Callable[[], float] = time.monotonic,
) -> bool:
    """Install the per-tenant rate-limit + concurrency guards on ``application`` as HTTP
    middleware.

    SAFE-DEFAULT: a NO-OP unless CEXAI_TENANT_RATE_LIMIT_ENABLED is truthy (the existing
    suite never sets it, so the app is byte-identical when disabled). When enabled, EVERY
    request flows through one middleware that:
      * resolves the VERIFIED tenant (the same JWT chokepoint the routes use) -- never a
        client value;
      * applies the token-bucket rate limit then the per-tenant concurrency cap;
      * on DENY returns a 429 + Retry-After (without calling the route);
      * on ADMIT holds a concurrency slot, calls the route, and releases the slot in a
        finally (no slot leak even if the route raises);
      * a no-auth request (no Authorization, e.g. /healthz) is admitted unguarded (liveness
        is never per-tenant limited; an authed route still 401s via its own auth).

    Limits are read from the env at install time (rpm/burst/max-inflight). ``override`` is
    the optional per-tenant limit hook; ``time_fn`` is injectable for tests.

    Returns True if installed, False if disabled (the no-op default). NEVER raises -- a guard
    wiring failure must not stop the app from booting."""
    if not limiter_enabled():
        return False

    try:
        rpm = _env_int(ENV_RPM, DEFAULT_RPM)
        burst = _env_int(ENV_BURST, rpm)  # default burst = rpm (one minute's allowance)
        max_inflight = _env_int(ENV_MAX_INFLIGHT, DEFAULT_MAX_INFLIGHT)

        limiter = TokenBucketLimiter(rpm=rpm, burst=burst, override=override, time_fn=time_fn)
        cap = TenantConcurrencyCap(limit=max_inflight)
        guards = _Guards(limiter, cap)

        @application.middleware("http")
        async def _tenant_guard_middleware(request, call_next):
            # Resolve + apply the guards from the raw Authorization header (the verified
            # tenant key is derived inside; a client body/query/other-header is never used).
            authorization = request.headers.get("authorization")
            release, denial = guards.admit(authorization)
            if denial is not None:
                return denial  # 429 -- do NOT call the route
            try:
                return await call_next(request)
            finally:
                # ALWAYS release the concurrency slot, even if the route raised (no leak).
                if release is not None:
                    release()

        # Stash the live instances on the app for introspection / tests.
        application.state.tenant_rate_limiter = limiter
        application.state.tenant_concurrency_cap = cap
        return True
    except Exception as exc:  # the installer itself must never block app boot (degrade-never)
        _warn_guard("install", "-", str(exc))
        return False
