---
id: bld_kc_data_contract
kind: knowledge_card
pillar: P01
llm_function: INJECT
version: 1.0.0
quality: null
tags: [data_contract, schema, published-language, knowledge]
title: "Knowledge: Data Contract Pattern"
author: builder
tldr: "Data Contract knowledge: domain knowledge, terminology, and contextual background"
8f: "F3_inject"
keywords: [data contract pattern, data contract knowledge, domain knowledge, and contextual background, data_contract, schema, published-language, knowledge, core facts, published language]
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-17"
related:
  - p01_kc_data_contract
  - bld_memory_data_contract
  - data-contract-builder
  - bld_context_sources_data_contract
  - bld_architecture_data_contract
---
# Domain Knowledge: data_contract
## Core Facts
- DDD Published Language (Evans 2003): explicit schema shared between BCs
- Industry standard: Atlan/Monte Carlo data contracts (2022+), dbt contracts (1.5+)
- Three components: schema (structure), semantics (meaning), SLA (quality)
- Versioned independently from producer implementation (contract v1 != service v1)
- Consumer-driven contract testing: consumers define what they need, producers comply

## Framework Equivalents
| Framework | Equivalent | Notes |
|-----------|-----------|-------|
| Protobuf IDL | message definition | Binary, schema registry |
| Apache Avro | Schema + subject | Kafka ecosystem standard |
| OpenAPI | components/schemas | REST API contracts |
| dbt | model contracts (1.5+) | SQL data warehouse |
| Pact | Consumer-driven CDC | Microservices testing |

## SLA Metrics Reference
| Metric | Typical Threshold | Measurement |
|--------|------------------|-------------|
| freshness | < 15min (near-real-time) | Max age of newest record |
| availability | 99.5% - 99.9% | Uptime of data pipeline |
| latency_p99 | < 500ms (API) | 99th percentile response |
| completeness | >= 99% | Non-null rate for required fields |

## Anti-Patterns
| Anti-Pattern | Correct Approach |
|-------------|-----------------|
| Implicit schema (undocumented) | Explicit data_contract per exchange |
| Contract = implementation spec | Contract is consumer view, not internal |
| Single versioning (tied to service) | Contract versioned independently |

## Knowledge Injection Checklist

- Verify domain facts are sourced and citable
- Validate density_score >= 0.85 (no filler content)
- Cross-reference with related KCs for consistency
- Check for outdated facts that need refresh

## Injection Pattern

```yaml
# KC injection at F3
source: verified
density: 0.85+
cross_refs: checked
freshness: current
```

```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_retriever.py --query "{DOMAIN}"
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_data_contract]] | sibling | 0.44 |
| [[bld_memory_data_contract]] | downstream | 0.33 |
| [[data-contract-builder]] | downstream | 0.33 |
| [[bld_context_sources_data_contract]] | downstream | 0.30 |
| [[bld_architecture_data_contract]] | downstream | 0.29 |
