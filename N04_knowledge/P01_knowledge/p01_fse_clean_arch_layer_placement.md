---
id: p01_fse_clean_arch_layer_placement
kind: few_shot_example
pillar: P01
version: "1.0.0"
created: "2026-06-03"
updated: "2026-06-03"
author: n03_builder
domain: clean_architecture_layer_placement
difficulty: hard
edge_case: true
format: "Clean Architecture layer classification with LABEL -- 1-line rationale"
quality: null
input: "Classify 'EF Core DbContext' into the correct Clean Architecture layer and give a 1-line rationale."
output: "Infrastructure -- DbContext is a framework/persistence detail (EF Core); the Dependency Rule forbids Core/Domain from importing it."
tags: [few-shot, clean-architecture, layer-placement, ddd, classification]
tldr: "6-7 I/O pairs teaching LLM to classify any class/concern into the correct Clean Architecture layer with a 1-line rationale. ardalis/CleanArchitecture (MIT)."
keywords: [clean-architecture, layer, domain, infrastructure, application, use-case, dependency-rule, classification]
source: "github.com/ardalis/CleanArchitecture"
source_author: "Steve Smith (ardalis)"
source_license: "MIT"
related:
  - p01_kc_clean_arch_ddd_in_cex
  - p01_fse_entity_vs_value_object
  - p01_kc_repo_assimilation_candidates
---

# Few-Shot Example -- Clean Architecture Layer Placement

> Source: ardalis/CleanArchitecture (github.com/ardalis/CleanArchitecture, MIT, Steve Smith).
> All examples are CEX-original; no verbatim reproduction of source code.
> Layer taxonomy: Martin 2017 "Clean Architecture" + ardalis implementation pattern.

## Explanation

Teaches the primary Clean Architecture question: which layer does a given class or concern belong in?

**Layer taxonomy (Martin 2017 / ardalis):**

| Layer | What lives here | Dependency Rule |
|-------|-----------------|-----------------|
| Core / Domain | Aggregates, Entities, Value Objects, Domain Events, domain Interfaces | Depends on nothing |
| UseCases / Application | Handlers, Commands, Queries, Application Services, Validators | Depends on Core only |
| Infrastructure | DbContext, Repository impls, external API clients | Depends on Core; Core never imports it |
| Web / UI | Controllers, API endpoints, route handlers | Depends on UseCases + Core |

**Rule:** owns domain logic -> Core. Orchestrates use case -> UseCases. Talks to DB/FS/external -> Infrastructure. HTTP in/out -> Web/UI.

An LLM learning these pairs learns to: (1) spot framework imports (Infrastructure), (2) spot handler/command patterns (UseCases), (3) spot aggregate/entity identity (Core), (4) spot HTTP/controller signals (Web), (5) resolve edge cases where a concept DECLARES in one layer but IMPLEMENTS in another.

## Input/Output Pairs

### Pair 1 -- Baseline: Infrastructure (EF Core DbContext)
```
Input: Classify 'EF Core DbContext' (e.g., AppDbContext : DbContext).
Output: Infrastructure -- DbContext is a framework/persistence detail; Core/Domain must never import EF Core (Dependency Rule violation if it does).
```

### Pair 2 -- Baseline: Core/Domain (Order aggregate)
```
Input: Classify 'Order' -- an aggregate root with OrderId, status lifecycle, and domain rules enforcing valid transitions.
Output: Core/Domain -- Order is an enterprise entity (aggregate root) with identity and domain logic; it depends on nothing outside Core.
```

### Pair 3 -- Baseline: UseCases/Application (CreateOrderHandler)
```
Input: Classify 'CreateOrderHandler' -- a MediatR IRequestHandler that validates input, calls the Order factory, and persists via IOrderRepository.
Output: UseCases/Application -- CreateOrderHandler orchestrates one use case; it calls a domain Interface (IOrderRepository) without knowing the persistence implementation.
```

### Pair 4 -- Baseline: Web/UI (OrdersController)
```
Input: Classify 'OrdersController : ControllerBase' -- receives HTTP POST, maps the request DTO to a MediatR Command, dispatches it, and returns IActionResult.
Output: Web/UI -- OrdersController is a delivery mechanism (Interface Adapter); it knows HTTP and MediatR but contains no domain or application logic.
```

### Pair 5 -- Edge case: domain Interface vs Infrastructure implementation
```
Input: Classify 'IOrderRepository' (interface in Core) vs 'EfOrderRepository' (implements it via DbContext, in Infrastructure).
Output: IOrderRepository = Core/Domain -- contract owned by domain; Core may depend on it freely. EfOrderRepository = Infrastructure -- EF Core implementation detail; injected via DI, never imported by Core directly.
```

### Pair 6 -- Edge case: CQRS Query handler
```
Input: Classify 'GetOrderByIdQueryHandler' -- reads a lightweight OrderSummaryDto directly from the database for display purposes, bypassing the Order aggregate.
Output: UseCases/Application -- a read-side handler is still an application-layer concern even when it skips the aggregate; it orchestrates the query and owns the DTO shape, while the data access call belongs to Infrastructure.
```

### Pair 7 -- Hard: Application Validator (FluentValidation)
```
Input: Classify 'CreateOrderCommandValidator : AbstractValidator<CreateOrderCommand>' -- validates OrderItems non-empty and quantities positive.
Output: UseCases/Application -- command validators enforce application-level input rules, not domain invariants; they live alongside their Command. FluentValidation is a library but the validator owns application logic, not Infrastructure.
```

## Edge Cases Covered

| Pair | Edge | Key Teaching |
|------|------|-------------|
| Pair 5 | Interface in Core, impl in Infrastructure | DECLARE the contract in the layer that needs it; IMPLEMENT in the detail layer |
| Pair 6 | Read-side handler bypasses aggregate | Read-path shortcut stays in Application, not Infrastructure |
| Pair 7 | Library dependency vs layer ownership | A class that uses a framework library is NOT automatically Infrastructure; layer = what concern it owns |

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_clean_arch_ddd_in_cex]] | upstream domain KC | 0.94 |
| [[p01_fse_entity_vs_value_object]] | sibling few_shot (same wave) | 0.88 |
| p08_pat_clean_architecture_project_structure | structural pattern companion | 0.85 |
| [[p01_kc_repo_assimilation_candidates]] | mission context | 0.72 |
| few_shot_entity_vs_value_object | sibling | 0.70 |
