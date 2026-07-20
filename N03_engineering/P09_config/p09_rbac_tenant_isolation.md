---
id: p09_rbac_tenant_isolation
kind: rbac_policy
pillar: P09
8f: F1_constrain
title: "Multi-Tenant Isolation RBAC Policy (HYBRID)"
version: "1.0.0"
created: "2026-06-09"
updated: "2026-06-09"
author: rbac-policy-builder
domain: "multi-tenant access control"
quality: null
tenant: tenant_self
roles: [owner, admin, member, viewer]
resources: [brand_config, runtime, memory, secrets, artifacts]
actions: [read, write, delete, admin, dispatch]
tags: [rbac_policy, multi_tenant, isolation, deny_by_default, security, P09]
tldr: "Deny-by-default RBAC for HYBRID multi-tenancy: 4 roles (owner/admin/member/viewer) scoped to tenant_self across brand_config/runtime/memory/secrets/artifacts. Cross-tenant access is DENY for every role -- the bleed-prevention invariant."
references:
  - NIST SP 800-162 (ABAC/RBAC)
related:
  - p09_env_n03
  - p09_path_n03
  - p11_gr_builder_nucleus
  - bld_schema_rbac_policy
---

## Policy Overview

Scope: a single tenant root `.cex/tenants/<tid>/`. Model: **deny-by-default**; every
principal is bound to exactly one `tenant_self` (resolved from `CEX_TENANT_ID` at boot).
Lens: Gating Wrath -- cross-tenant is a hard gate; violations log and halt.
Design: a dedicated multi-tenant hybrid architecture decision record (not included in
this exemplar set).

## Roles and Permissions (within tenant_self only)

| Role | brand_config | runtime | memory | secrets | artifacts |
|---|---|---|---|---|---|
| owner | r w d a | r w d | r w d | r w d a | r w d |
| admin | r w | r w | r w | r | r w |
| member | r | r w | r | none | r w |
| viewer | r | none | none | none | r |

r=read, w=write, d=delete, a=admin (grant/revoke roles + rotate keys). All cells are
scoped to `tenant_self`; no cell references another tenant.

## Resource Scope (tenant-rooted, wildcard-free)

| Resource | Path |
|---|---|
| brand_config | `.cex/tenants/tenant_self/brand/` |
| runtime | `.cex/tenants/tenant_self/runtime/` |
| memory | memory namespace `tenant_self/` |
| secrets | `.cex/tenants/tenant_self/secrets/` |
| artifacts | `tenants/tenant_self/N0X/` |

## Deny Rules

| Rule ID | Subject | Resource | Condition | Effect |
|---|---|---|---|---|
| deny_cross_tenant | any role | any resource | tenant != tenant_self | DENY |
| deny_secret_to_member | member, viewer | secrets | always | DENY |
| deny_viewer_mutate | viewer | any | write/delete | DENY |
| deny_self_score | any role | artifacts | quality set non-null | DENY |
| deny_cross_tenant_dispatch | any role | runtime | dispatch outside tenant_self | DENY |

**Rationale:**
- `deny_cross_tenant`: THE isolation invariant -- tenant A can never touch tenant B.
- `deny_secret_to_member`: credential surface is owner/admin only (see the tenant OAuth config).
- `deny_viewer_mutate`: viewer is strictly read-only.
- `deny_self_score`: `quality: null` is a system invariant (peer review scores).
- `deny_cross_tenant_dispatch`: a handoff may only target the bound tenant's runtime.

## Audit Trail

| Event | Severity | Log |
|---|---|---|
| Cross-tenant access attempt | CRITICAL | `.cex/tenants/tenant_self/runtime/signals/rbac_violation.log` |
| Secret access by member/viewer | HIGH | same |
| Self-score attempt | HIGH | same |

Violations halt the current operation; the log is append-only and tenant-rooted. The
`admin` role is the one operationalizing role grants/revokes. This pattern mirrors the
same nucleus-isolation precedent used elsewhere in P09, generalized from nucleus to tenant.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p09_env_n03]] | sibling | 0.28 |
| [[p09_path_n03]] | sibling | 0.26 |
| [[p11_gr_builder_nucleus]] | related | 0.24 |
| [[bld_schema_rbac_policy]] | related | 0.20 |
