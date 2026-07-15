---
kind: quality_gate
id: p11_qg_ontology
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of ontology artifacts
pattern: few-shot learning -- LLM reads these before producing
quality: null
title: "Gate: ontology"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, ontology, taxonomy, OWL, SKOS, P11]
tldr: "Gates for ontology artifacts: validates class hierarchy completeness, property constraints, axiom declarations, and schema.org mapping."
domain: "ontology -- formal taxonomy and classification definitions using OWL, SKOS, and schema.org patterns"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F7_govern"
keywords: [ontology, class hierarchy, property constraints, axiom, schema.org mapping]
density_score: 0.92
related:
  - p10_lr_ontology_builder
  - bld_output_template_ontology
  - ontology-builder
  - bld_knowledge_card_ontology
  - bld_instruction_ontology
---
## Quality Gate

# Gate: ontology
## Definition
| Field | Value |
|-------|-------|
| metric | Composite score from SOFT dimensions + all HARD gates pass |
| threshold | >= 7.0 to publish; >= 9.5 golden |
| operator | AND (all HARD) + weighted_sum (SOFT) |
| scope | All artifacts where `kind: ontology` |

## HARD Gates
All must pass. Any single failure = REJECT regardless of SOFT score.
| ID | Check | Failure message |
|----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | "Frontmatter YAML syntax error" |
| H02 | `id` matches `^p01_ont_[a-z][a-z0-9_]+$` | "ID fails ontology namespace regex" |
| H03 | `id` value equals filename stem | "ID does not match filename" |
| H04 | `kind` equals literal `"ontology"` | "Kind is not 'ontology'" |
| H05 | `quality` field is `null` | "Quality must be null at authoring time" |
| H06 | All required fields present: id, kind, pillar, domain, standard, classes, version, created, author, tags, tldr | "Missing required field(s)" |

## SOFT Scoring
Dimensions sum to 100%. Score each 0.0-10.0; multiply by weight.
| Dimension | Weight | What to assess |
|-----------|--------|----------------|
| Class hierarchy depth | 1.0 | At least 2 levels of hierarchy (root + subclass) for non-trivial domains |
| Property completeness | 1.0 | Every object property has domain, range, cardinality; datatype has xsd: type |
| Disjointness coverage | 1.0 | All sibling class pairs that are mutually exclusive declare DisjointClasses |
| Axiom quality | 1.0 | Functional/transitive/symmetric declared where semantically correct |
| Inverse properties | 0.5 | Inverse pairs declared where navigable bi-directionally |
| Schema.org alignment | 1.0 | All classes with schema.org equivalents have mapping declared |
Weight sum: 10.0 (100%)

## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | GOLDEN | Publish to pool as golden exemplar |
| >= 8.0 | PUBLISH | Publish to pool |
| >= 7.0 | REVIEW | Flag for human review before publish |
| < 7.0 | REJECT | Return to author with failure report |

## Bypass
| Field | Value |
|-------|-------|
| conditions | Rapid-prototype ontologies where full property catalog is not yet known; stub must have >= 1 class and H01-H06 pass |
| approver | Domain expert approval required (written); axiom declarations never bypassed for OWL-mode ontologies |

## Examples

# Examples: ontology-builder
## Golden Example
INPUT: "Define an ontology for an e-commerce product catalog"

OUTPUT:
```yaml
id: p01_ont_ecommerce_product
kind: ontology
pillar: P01
version: "1.0.0"
created: "2026-04-13"
updated: "2026-04-13"
author: "builder_agent"
domain: "ecommerce"
```

## Overview
Formal ontology for e-commerce product catalog classification using OWL class hierarchies
and schema.org interoperability mappings. Consumed by product search, recommendation, and
structured data systems.

## Class Hierarchy
| Class | Parent | Label | Description | schema.org Equivalent |
|-------|--------|-------|-------------|----------------------|
| Product | owl:Thing | Product | Any item offered for sale | schema:Product |
| PhysicalProduct | Product | Physical Product | Tangible item with shipping requirements | schema:Product |
| DigitalProduct | Product | Digital Product | Downloadable or streamed item, no shipping | schema:DigitalDocument |
| ProductCategory | owl:Thing | Product Category | SKOS concept for classification hierarchy | schema:Thing |
| Brand | owl:Thing | Brand | Manufacturer or label identity | schema:Brand |
| Offer | owl:Thing | Offer | Price and availability for a Product | schema:Offer |

## Properties
| Property | Type | Domain | Range | Cardinality | Axiom Flags |
|----------|------|--------|-------|-------------|-------------|
| hasBrand | object | Product | Brand | 0..1 | functional |
| hasCategory | object | Product | ProductCategory | 1..* | none |
| hasOffer | object | Product | Offer | 0..* | none |
| name | datatype | Product | xsd:string | 1..1 | functional |
| sku | datatype | Product | xsd:string | 0..1 | functional |
| price | datatype | Offer | xsd:decimal | 1..1 | functional |

## Axioms
- DisjointClasses: PhysicalProduct, DigitalProduct -- a product cannot be both physical and digital
- FunctionalProperty: hasBrand -- each product has at most one brand
- TransitiveProperty: broader -- category A broader than B, B broader than C implies A broader than C
- InverseOf: broader / narrower

## Schema.org Mapping
| Local Class/Property | schema.org URI | Notes |
|---------------------|----------------|-------|
| Product | schema:Product | Direct equivalent |
| PhysicalProduct | schema:Product | Use additionalType for physical constraint |
| DigitalProduct | schema:DigitalDocument | Approximate; schema:SoftwareApplication also relevant |
| Brand | schema:Brand | Direct equivalent |
| Offer | schema:Offer | Direct equivalent |
| hasBrand | schema:brand | Direct equivalent |

### S_RELATED
-0.3 if `related:` < 3 or body lacks Related Artifacts

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p10_lr_ontology_builder]] | upstream | 0.36 |
| [[bld_output_template_ontology]] | upstream | 0.35 |
| [[ontology-builder]] | upstream | 0.35 |
| [[bld_knowledge_ontology]] | upstream | 0.35 |
| [[bld_prompt_ontology]] | upstream | 0.34 |
