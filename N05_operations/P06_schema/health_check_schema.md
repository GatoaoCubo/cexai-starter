---
id: p06_is_health_response_n05
kind: input_schema
pillar: P06
title: "Health Check Response Schema"
version: 1.0.0
created: "2026-07-20"
updated: "2026-07-20"
author: n05_operations
domain: backend-operations
quality: null
tags: [schema, health, response, monitoring, api]
tldr: "Schema for HealthResponse JSON validation covering status, version, uptime, database, and cache health indicators."
schema_type: json_response
validation_level: strict
related:
  - KC_N05_API_HEALTH_MONITORING
  - p11_schema_curation_nudge
  - p11_schema_revision_loop_policy
  - p07_bm_ops_pipeline
---

# Health Check Response Schema

## Purpose

Validates `/health` endpoint JSON responses for any backend API service, so
monitoring, alerting, and deploy gates all read the same shape.

## Schema Definition

```yaml
health_response:
  required: true
  properties:
    status:
      type: string
      enum: ["healthy", "degraded", "unhealthy"]
      required: true
    version:
      type: string
      pattern: "^\\d+\\.\\d+\\.\\d+"
      required: true
    timestamp:
      type: string
      format: iso8601
      required: true
    uptime_seconds:
      type: integer
      minimum: 0
      required: true
    environment:
      type: string
      enum: ["development", "staging", "production"]
      required: true
    database:
      type: object
      required: true
      properties:
        status: {type: string, enum: ["connected", "disconnected", "error"]}
        pool_size: {type: integer, minimum: 0}
        active_connections: {type: integer, minimum: 0}
        ssl_enabled: {type: boolean}
    cache:
      type: object
      required: false
      properties:
        status: {type: string, enum: ["connected", "disconnected", "fallback"]}
        hit_rate: {type: number, minimum: 0, maximum: 1}
        memory_usage_mb: {type: number, minimum: 0}
```

## Validation Rules

- status must indicate current service health level
- version must follow semantic versioning format
- uptime_seconds tracks service restart cycles
- database status required whenever a relational store backs the service
- cache status optional for in-memory cache / fallback scenarios

## Example Valid Response

```json
{
  "status": "healthy",
  "version": "1.2.3",
  "timestamp": "2026-07-20T12:00:00Z",
  "uptime_seconds": 3600,
  "environment": "production",
  "database": {
    "status": "connected",
    "pool_size": 20,
    "active_connections": 5,
    "ssl_enabled": true
  },
  "cache": {
    "status": "connected",
    "hit_rate": 0.85,
    "memory_usage_mb": 128
  }
}
```

## Health Check Implementation

Health check endpoints follow a standardized response format:

- **Response time**: health endpoint must respond within 500ms under normal load
- **Dependency cascading**: check reports status of each downstream dependency individually
- **Degraded state**: partial failures reported as DEGRADED, not DOWN, with detail
- **History retention**: recent health check results stored for trend analysis

### Endpoint Specification

```yaml
# Health check response schema
health:
  status: UP | DEGRADED | DOWN
  timestamp: ISO8601
  version: semver
  checks:
    - name: database
      status: UP
      latency_ms: 12
    - name: cache
      status: UP
      latency_ms: 3
  uptime_seconds: 86400
```

| Status | Meaning | Alert Level |
|--------|---------|-------------|
| UP | All checks pass | None |
| DEGRADED | Non-critical check failed | Warning |
| DOWN | Critical check failed | Critical |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[KC_N05_API_HEALTH_MONITORING]] | upstream | 0.40 |
| [[p11_schema_curation_nudge]] | downstream | 0.34 |
| [[p11_schema_revision_loop_policy]] | downstream | 0.31 |
| [[p07_bm_ops_pipeline]] | related | 0.27 |
