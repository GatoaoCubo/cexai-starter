---
id: p05_oval_health_readiness
kind: output_validator
8f: F6_produce
pillar: P05
title: "Health + Readiness Endpoint Template (FastAPI)"
version: "1.0.0"
created: "2026-07-20"
updated: "2026-07-20"
author: n05_operations
domain: infrastructure
quality: null
tags: [output, template, health, fastapi, monitoring, P05]
tldr: "Copy-paste FastAPI health endpoints -- /health and /ready -- with real Pydantic models, generic across any {{deploy_target}} that health-checks a service before routing traffic to it."
keywords: [health endpoint template, readiness probe, fastapi health endpoints, output_validator, deploy_target, uptime, database pool check]
density_score: 0.95
related:
  - p06_is_health_response_n05
  - output-validator-builder
  - p09_env_n05
  - nucleus_def_n05
---

# Health + Readiness Endpoint Template

## Purpose
Production-ready health check endpoints for a FastAPI service, portable to any
`{{deploy_target}}` (container platform, PaaS, or bare VM) that polls `/health` before
routing traffic and uses `/ready` to gate load-balancer registration. Validates against
the sibling schema [[p06_is_health_response_n05]] in P06.

---

## Complete Python Implementation

```python
"""Health check endpoints -- copy-paste ready for FastAPI."""
from datetime import datetime, timezone
from time import time
from typing import Optional

from fastapi import APIRouter, Response
from pydantic import BaseModel

router = APIRouter(tags=["health"])

_start_time = time()


class ServiceStatus(BaseModel):
    status: str  # "healthy" | "unhealthy"
    connected: bool
    latency_ms: Optional[float] = None
    pool_size: Optional[int] = None


class HealthResponse(BaseModel):
    status: str  # "healthy" | "degraded" | "unhealthy"
    version: str
    timestamp: str
    uptime_seconds: float
    environment: str
    database: ServiceStatus
    cache: ServiceStatus


async def check_database() -> ServiceStatus:
    """Check the async connection pool."""
    from app.database import get_pool  # adjust import
    try:
        pool = get_pool()
        start = time()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        latency = (time() - start) * 1000
        return ServiceStatus(
            status="healthy", connected=True,
            latency_ms=round(latency, 2), pool_size=pool.get_size(),
        )
    except Exception:
        return ServiceStatus(status="unhealthy", connected=False)


async def check_cache() -> ServiceStatus:
    """Check cache connectivity (Redis or equivalent)."""
    from app.cache import get_cache_client  # adjust import
    try:
        cache = get_cache_client()
        if cache is None:
            return ServiceStatus(status="healthy", connected=False)  # in-memory fallback
        start = time()
        await cache.ping()
        latency = (time() - start) * 1000
        return ServiceStatus(status="healthy", connected=True, latency_ms=round(latency, 2))
    except Exception:
        return ServiceStatus(status="unhealthy", connected=False)


@router.get("/health", response_model=HealthResponse)
async def health_check(response: Response):
    """
    Main health endpoint. No auth required.
    {{deploy_target}} polls this for deploy health checks and restart decisions.

    Returns:
        - healthy: all services OK
        - degraded: a dependency is unhealthy but the app is still serving
        - unhealthy: critical failure
    """
    import os
    from app import __version__  # adjust import

    db = await check_database()
    cache = await check_cache()

    if db.status == "unhealthy":
        overall = "degraded"
        response.status_code = 200  # many platforms want 200 even when degraded
    else:
        overall = "healthy"

    return HealthResponse(
        status=overall,
        version=__version__,
        timestamp=datetime.now(timezone.utc).isoformat(),
        uptime_seconds=round(time() - _start_time, 2),
        environment=os.getenv("ENV", "development"),
        database=db,
        cache=cache,
    )


@router.get("/ready")
async def readiness_check():
    """
    Readiness probe -- returns 200 only when fully initialized.
    Use for load-balancer / traffic-routing decisions, distinct from /health.
    """
    db = await check_database()
    if db.status == "unhealthy":
        return Response(status_code=503, content='{"status": "not ready"}',
                        media_type="application/json")
    return {"status": "ready"}
```

## Response Examples

### Healthy
```json
{
  "status": "healthy",
  "version": "2.1.0",
  "timestamp": "2026-07-20T12:00:00.000Z",
  "uptime_seconds": 3642.51,
  "environment": "production",
  "database": {"status": "healthy", "connected": true, "latency_ms": 1.23, "pool_size": 5},
  "cache": {"status": "healthy", "connected": true, "latency_ms": 0.45, "pool_size": null}
}
```

### Degraded
```json
{
  "status": "degraded",
  "version": "2.1.0",
  "database": {"status": "unhealthy", "connected": false},
  "cache": {"status": "healthy", "connected": true}
}
```

## Integration

```python
# In main.py
from app.health import router as health_router
app.include_router(health_router)
```

## Why /health and /ready are separate
`/health` answers "is this instance broken" (drives restart decisions). `/ready` answers
"can this instance take traffic right now" (drives load-balancer registration). Conflating
them causes a cold-starting-but-healthy instance to either get killed (too strict) or take
traffic before its pool is warm (too loose). Keep both, keep them distinct.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p06_is_health_response_n05]] | sibling | 0.42 |
| [[output-validator-builder]] | upstream | 0.30 |
| [[p09_env_n05]] | related | 0.24 |
| [[nucleus_def_n05]] | upstream | 0.22 |
