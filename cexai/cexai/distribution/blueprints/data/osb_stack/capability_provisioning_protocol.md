---
kind: workflow
id: capability_provisioning_protocol
title: Capability Provisioning Protocol (OSB-distilled)
version: 1.0.0
quality: null
pillar: P12
nucleus: N03
vertical: 19_osb_stack
mode: protocol
reuses_kinds: [openapi_spec, interface, pattern, capability_registry, workflow]
open_vars: []
source:
  upstream: openservicebrokerapi/servicebroker
  release: v2.17
  license: Apache-2.0
  distilled_from: cexai-specs/19_osb_stack/_meta/inventory_baseline.md
tags: [provisioning, capability_registry, osb, lifecycle, broker]
---

# Capability Provisioning Protocol

A CEX-native distillation of the Open Service Broker (OSB) API v2.17 lifecycle. OSB
is the industry-standard formalization of "advertise a capability, hand out an
instance, wire a consumer to it, tear it down." CEX already does this ad hoc
(`Task tool: dispatch` / handoffs / signals); this protocol names it as a typed lifecycle
bound to the existing `capability_registry` kind.

> **Zero new kinds.** This artifact is a `workflow` instance. Its parts decompose
> entirely into kinds CEX already has: `capability_registry` (the catalog),
> `interface` + `pattern` (the lifecycle contract), `openapi_spec` (the wire shape),
> and `workflow` (this orchestration). It is a PROTOCOL, not an apply-able template
> stack -- `cexai blueprint show osb_stack` renders it; `apply` is intentionally
> rejected.

---

## Lifecycle (the five phases)

| Phase | OSB operation | CEX binding | Idempotent? |
|-------|---------------|-------------|-------------|
| catalog | `GET /v2/catalog` | read `capability_registry`: the services + plans on offer | yes (pure read) |
| provision | `PUT /v2/service_instances/:id` | create an instance of a (service, plan) selection; record it | yes (same id + params -> same instance) |
| bind | `PUT /v2/service_instances/:id/service_bindings/:bid` | issue credentials/endpoint that let a consumer use the instance | yes (same bid -> same binding) |
| unbind | `DELETE .../service_bindings/:bid` | revoke a previously issued binding | yes (gone -> 410 Gone) |
| deprovision | `DELETE /v2/service_instances/:id` | destroy the instance, release its resources | yes (gone -> 410 Gone) |

The phases form a partial order: `catalog -> provision -> bind` going up, and
`unbind -> deprovision` coming down. A binding cannot exist without its instance;
deprovision MUST be refused while live bindings remain (or cascade, per policy).

---

## State machine

```
                 provision                 bind
   [absent] ----------------> [provisioned] ----------------> [bound]
      ^                            |   ^                          |
      |        deprovision         |   |         unbind           |
      +----------------------------+   +--------------------------+
                              (no live bindings)
```

| From | Event | To | Guard |
|------|-------|----|-------|
| absent | provision | provisioned | (service, plan) exist in catalog |
| provisioned | bind | bound | instance ready |
| bound | bind | bound | additional binding (N bindings per instance allowed) |
| bound | unbind | provisioned/bound | one binding removed; `bound` while others remain |
| provisioned | deprovision | absent | zero live bindings (else 409 Conflict or cascade) |

---

## Binding to `capability_registry`

The OSB catalog IS a `capability_registry` projection. A registry entry advertises a
capability the way OSB advertises a service:

```yaml
# capability_registry entry (existing kind) viewed as an OSB service
service_id: <capability id in the registry>
name: <capability name>
plans:                       # OSB plans == capability tiers / variants
  - plan_id: <variant id>
    name: <variant name>
    free: <bool>
bindable: <bool>             # can a consumer bind, or is it provision-only?
```

`provision` allocates a concrete instance of a registry capability; `bind` is how a
CEX nucleus (or external consumer) receives the handle to call it. This is the typed
form of what `Task tool: dispatch` does informally when it spawns a nucleus against a
capability.

---

## Contract semantics (the `interface` + `pattern` reused here)

- **Asynchronous operations**: long-running provision/deprovision return `202
  Accepted` + a `last_operation` poll handle. Synchronous brokers complete inline.
- **Idempotency**: every mutating operation keys on its id; a retry with identical
  parameters is a no-op that returns the existing state (the OSB reliability
  guarantee). This maps to CEX signal-replay safety.
- **Orphan mitigation**: if a consumer is unsure whether provision succeeded (network
  cut after the request), it retries the SAME provision; the broker reconciles.
- **Conflict**: provisioning an existing id with DIFFERENT parameters is `409
  Conflict`; the protocol never silently mutates a live instance.
- **Gone**: unbind/deprovision of an already-absent resource is `410 Gone`, not an
  error -- so cleanup is safely re-runnable.

---

## Why distilled, not absorbed wholesale

Per the vertical-19 recon (`inventory_baseline.md`, ADR 003 Mode D), the OSB repo is
pure specification (markdown + OpenAPI YAML, zero runtime). Its OpenAPI definition is
an `openapi_spec`; its lifecycle contract is an `interface` + `pattern`; its catalog
is a `capability_registry`; its orchestration is this `workflow`. Nothing in OSB
required a new CEX kind. The deliverable is therefore this single distilled protocol
artifact -- the smallest faithful representation that binds the OSB lifecycle to CEX's
existing capability vocabulary.

---

## Attribution

Distilled from the Open Service Broker API (`openservicebrokerapi/servicebroker`,
release v2.17, Apache-2.0). No upstream code was vendored; only the lifecycle
contract was re-expressed in CEX kinds. See
`cexai-specs/19_osb_stack/_meta/inventory_baseline.md` for the full recon.
