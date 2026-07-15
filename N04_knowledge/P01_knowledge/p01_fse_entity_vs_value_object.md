---
id: p01_fse_entity_vs_value_object
kind: few_shot_example
pillar: P01
version: "1.0.0"
created: "2026-06-03"
updated: "2026-06-03"
author: n03_builder
domain: ddd_tactical_patterns
difficulty: medium
edge_case: true
format: "entity vs value_object DDD classification with 1-line rationale"
quality: null
input: "Classify the domain concept 'Customer' as ENTITY or VALUE OBJECT and give a 1-line rationale."
output: "ENTITY -- A Customer has a persistent identity (customer_id) that survives attribute changes: the same customer remains 'themselves' even after changing address, name, or email."
tags: [few-shot, ddd, entity, value-object, domain-driven-design, classification]
tldr: "5-7 I/O pairs teaching LLM to classify a domain concept as DDD ENTITY or VALUE OBJECT with a 1-line rationale. Evans 2003 + Vernon 2013."
keywords: [entity, value-object, ddd, aggregate, identity, immutability, classification]
related:
  - p01_kc_clean_arch_ddd_in_cex
  - value_object
  - aggregate_root
primary_8f: INJECT
when_to_use: "Load when working on few_shot_example in P01. Consult for how to act on this few_shot_example."
slots:
  new_input: "<the case the consuming LLM generalizes to>"
  expected_shape: "<the output contract>"
---

# Few-Shot Example -- Entity vs Value Object (DDD Tactical)

> Source grounding: Evans 2003 "Domain-Driven Design", Vernon 2013 "Implementing DDD".
> All examples are CEX-original; no verbatim reproduction of book text.

## Explanation

Teaches the SINGLE most-asked DDD tactical question: is this concept an ENTITY (identity + continuity) or a VALUE OBJECT (attributes-only, immutable, replaceable)?

**Classification rule (Evans):**
- ENTITY: has a unique identity that persists through attribute change. Two entities with identical attributes are still different objects.
- VALUE OBJECT: defined entirely by its attributes. Two value objects with identical attributes ARE the same. Immutable. Replaceable.

An LLM learning this pair learns to: (1) spot identity markers (IDs, lifecycle, mutation), (2) spot value markers (equality by content, immutability, no meaningful history).

## Input/Output Pairs

### Pair 1 -- Baseline ENTITY
```
Input: Classify 'Order' in an e-commerce system.
Output: ENTITY -- An Order has an order_id and a lifecycle (placed, paid, shipped, cancelled); the same order transitions through states while remaining the same order.
```

### Pair 2 -- Baseline VALUE OBJECT
```
Input: Classify 'Money' (amount + currency) in a payment system.
Output: VALUE OBJECT -- Money is defined solely by amount + currency. USD 50.00 == USD 50.00 regardless of which Money instance it is; replacing one with another of equal value is always safe.
```

### Pair 3 -- Medium: Address
```
Input: Classify 'Address' in a shipping system where addresses can be corrected.
Output: VALUE OBJECT -- An address is a snapshot of location attributes (street, city, zip). Correcting a typo replaces the whole value; there is no meaningful identity to track across changes.
```

### Pair 4 -- Medium: Employee
```
Input: Classify 'Employee' in an HR system.
Output: ENTITY -- An Employee has an employee_id and a continuous history (hire date, role changes, salary history). Two people named "Ana Lima" at the same address are still two different employees.
```

### Pair 5 -- Edge case: DateRange
```
Input: Classify 'DateRange' (start_date, end_date) in a booking system.
Output: VALUE OBJECT -- DateRange carries no identity; 2026-06-01..2026-06-07 == 2026-06-01..2026-06-07 for any two instances. Booking itself is the ENTITY; its occupancy window is a value.
```

### Pair 6 -- Edge case: Product vs ProductDescription
```
Input: Classify 'ProductDescription' (name, SKU text, images) vs 'Product' (product_id) in a catalog.
Output: Product = ENTITY (product_id persists; a product survives a description update). ProductDescription = VALUE OBJECT (replacing the whole description when any attribute changes is correct; two descriptions with identical fields are interchangeable).
```

### Pair 7 -- Hard: Quantity
```
Input: Classify 'Quantity' (amount, unit) in an inventory system.
Output: VALUE OBJECT -- Quantity(5, "kg") equals any other Quantity(5, "kg"); there is no identity to preserve. Inventory Line Item that HOLDS the quantity is the ENTITY. Common error: treating Quantity as ENTITY inflates aggregate complexity.
```

## Edge Cases Covered

| Pair | Edge | Key Teaching |
|------|------|-------------|
| Pair 3 | Address is often misclassified as ENTITY | Correction replaces value, not mutates identity |
| Pair 5 | DateRange embedded in an ENTITY aggregate | Container is ENTITY; window is VALUE |
| Pair 6 | Same concept at two levels of granularity | Decompose: stable ID=ENTITY, mutable description=VALUE |
| Pair 7 | Value held inside Entity | Holding relationship != identity |


### How to use

```text
You are the consuming agent that acts on this few_shot_example under F3 INJECT.
- Resolve the open slots (new_input, expected_shape) from the caller request.
- Honor every constraint and field contract declared above.
- Emit the result in the shape this few_shot_example defines; never improvise the schema.
```

### Procedure

```text
1. Load this artifact and read its contract under F3 INJECT.
2. Bind new_input and expected_shape from the incoming request.
3. Validate the inputs against the constraints declared above.
4. Execute the few_shot_example behavior; resolve each open slot at act-time.
5. Verify the output shape, then signal completion to the orchestrator.
```

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_clean_arch_ddd_in_cex]] | upstream domain KC | 0.91 |
| value_object | kind being classified | 0.88 |
| aggregate_root | parent kind (entities are often aggregate roots) | 0.85 |
