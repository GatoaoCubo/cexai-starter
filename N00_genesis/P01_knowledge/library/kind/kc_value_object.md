---
id: kc_value_object
kind: knowledge_card
8f: F3_inject
pillar: P01
nucleus: n00
domain: kind-taxonomy
quality: null
title: "Knowledge Card: value_object -- Immutable Domain Type by Structural Equality"
tags: [kind, taxonomy, value_object, ddd, P06]
long_tails:
  - "when do I use a value_object versus an entity in CEX"
  - "how do I model an immutable domain type with validation"
tldr: "Immutable domain type without identity, defined by structural equality -- Money, Email, DateRange"
when_to_use: "When modeling a domain concept defined entirely by its attributes with no tracking identity"
keywords: [domain-driven design, immutable, structural equality, invariants, validation rules, hashability, transformations]
density_score: 0.93
updated: "2026-04-17"
related:
  - bld_knowledge_card_value_object
  - bld_manifest_value_object
  - bld_architecture_value_object
  - bld_quality_gate_value_object
  - bld_memory_value_object
---
# Knowledge Card: value_object

## How to use

You are a value-object-builder. Load this card at **F3 INJECT** before modeling
any immutable domain type, then apply the contract below.

- Decide identity FIRST: if the concept is tracked over time, use `entity` instead.
- Enforce every invariant in the constructor; make invalid state unconstructable.
- Return NEW instances from transformations; never expose a setter.
- Keep it small (<= 5 attributes); more usually means decompose.
- Place the artifact in P06 with id `p06_vo_{slug}`; serves the **CONSTRAIN** verb.

## Definition
A `value_object` is an immutable domain type without identity, defined entirely by its attributes
and structural equality. Coined by Eric Evans in Domain-Driven Design (2003). Two value_object
instances are equal if and only if all their attributes are equal -- there is no notion of
"this specific instance" vs "that specific instance."

## When to Use
- A domain concept is defined entirely by its data (Money, Email, Address, Coordinates)
- Two instances with identical attributes are interchangeable (no tracking needed)
- The type has domain-level validation rules that must be enforced at construction
- The type participates in rich transformations (add, scale, convert) that produce new values

## When NOT to Use
- The object needs to be tracked over time with a persistent identity: use `entity` or `aggregate_root`
- The type is a fixed set of constants: use `enum_def`
- The type is a simple alias with no domain semantics: use `type_def`
- You are validating raw external input (pre-domain): use `input_schema`
- You are wrapping a foreign aggregate key: value_object is still correct (e.g., OrderId wraps UUID)

## Structure
Every `value_object` defines:
1. **Attributes**: typed fields with precise constraints (no identity fields like id/uuid/pk)
2. **Equality**: structural -- instances are equal iff all attributes are equal
3. **Validation**: invariants checked at construction (invalid instances cannot be created)
4. **Transformations**: methods that return NEW instances; no mutation methods (no setters)
5. **Hashability**: whether the value can be used as a dict key or set member

## The Whole Value Pattern
A well-designed value_object makes invalid state unrepresentable:
- `Money(-5, "USD")` should raise at construction, not silently create an invalid Money
- `Email("")` should raise at construction, not silently create an empty email
The constructor is the only validation gate. After construction, the instance is always valid.

## Immutability Contract
Transformations NEVER mutate the instance. They return new instances:
- CORRECT: `money.add(other)` returns `new Money(this.amount + other.amount, this.currency)`
- WRONG: `money.setAmount(50)` mutates the instance

## Use Cases
1. **Money(amount, currency)**: financial calculations with currency safety, used in Order and Invoice aggregates
2. **Email(address)**: RFC 5322 validated address, used in UserAccount and ContactInfo entities
3. **DateRange(start, end)**: invariant `start <= end`, transformations `overlaps()`, `contains()`, `duration()`

## Relationships to Other Kinds
| Kind | Relationship |
|------|-------------|
| `aggregate_root` | contains value_objects as typed attributes within its cluster |
| `type_def` | generic type alias without DDD immutability or equality contracts |
| `enum_def` | fixed-set constants (subset of value object concept, but distinct) |
| `input_schema` | validates raw input BEFORE constructing value objects from it |

## Anti-Patterns
- **Mutable value object**: any setter breaks the immutability guarantee -- use entity instead
- **Value object with identity**: if you add an `id` field, you created an entity
- **Oversized value object**: more than 5 attributes usually signals decomposition needed
- **Skipping validation**: a value object that can hold invalid state is worse than no type at all

## CEX Metadata
| Property | Value |
|----------|-------|
| Pillar | P06 (Schema) |
| ID pattern | `p06_vo_{slug}` |
| max_bytes | 2048 |
| llm_function | CONSTRAIN |
| Builder | value-object-builder (13 ISOs) |
| Nucleus | N03 (Engineering) |
| Pattern source | Evans DDD (2003), Vernon IDDD (2013) |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_card_value_object]] | sibling | 0.55 |
| [[bld_manifest_value_object]] | sibling | 0.53 |
| [[bld_architecture_value_object]] | sibling | 0.48 |
| [[bld_quality_gate_value_object]] | downstream | 0.46 |
| [[bld_memory_value_object]] | sibling | 0.45 |
