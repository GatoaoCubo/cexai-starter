---
id: p01_fse_scalability_bottleneck
kind: few_shot_example
pillar: P01
version: "1.0.0"
created: "2026-06-03"
updated: "2026-06-03"
author: n03_builder
domain: system_design_scalability
difficulty: hard
edge_case: true
format: "Scaling symptom -> BOTTLENECK TYPE -- 1-line fix"
quality: null
input: "Map scaling symptom 'reads slow as traffic grows, DB CPU pegged at 100%' to the likely bottleneck type and first fix."
output: "READ BOTTLENECK -- add read-through cache (Redis) + read replicas; route SELECT traffic off the primary."
tags: [few-shot, system-design, scalability, bottleneck, distributed-systems]
tldr: "7 I/O pairs teaching symptom->bottleneck->fix mapping for scaled systems. Source: donnemartin/system-design-primer (CC-BY-4.0)."
keywords: [scalability, bottleneck, cache, sharding, load-balancer, backpressure, read-replica, system-design]
source: "github.com/donnemartin/system-design-primer"
source_author: "Donne Martin"
source_license: "CC-BY-4.0"
related:
  - p01_kc_repo_assimilation_candidates
  - p01_fse_clean_arch_layer_placement
  - p01_kc_concept_graph
primary_8f: INJECT
when_to_use: "Load when working on few_shot_example in P01. Consult for how to act on this few_shot_example."
slots:
  new_input: "<the case the consuming LLM generalizes to>"
  expected_shape: "<the output contract>"
---

# Few-Shot Example -- Scalability Bottleneck Diagnosis

> Source: donnemartin/system-design-primer (github.com/donnemartin/system-design-primer, CC-BY-4.0, Donne Martin).
> All examples are CEX-original; no verbatim reproduction of source material.
> Bottleneck taxonomy: horizontal/vertical scale, read/write contention, backpressure, cache failure modes.

## Explanation

Teaches: given an observable symptom, which bottleneck class applies and what is the first fix?

| Class | Symptom signal | First fix |
|-------|---------------|-----------|
| READ BOTTLENECK | DB CPU high, reads slow | Cache + read replicas |
| WRITE HOTSPOT | Lock contention on one row | Shard / redesign partition key |
| NO HORIZONTAL SCALE | Single server saturated | Load balancer + stateless app |
| NO BACKPRESSURE | Tail latency spikes under burst | Queue + rate limit |
| PREMATURE SHARDING | Complexity, no throughput gain | Merge back; profile first |
| CACHE STAMPEDE | DB hammered after cache flush | Probabilistic expiry + mutex |
| THUNDERING HERD | Crash on reconnect storm | Jitter + exponential backoff |

An LLM learning these pairs learns to: (1) distinguish read vs write pressure, (2) recognize stateful bottlenecks blocking horizontal scale, (3) identify missing backpressure, (4) spot premature optimization, (5) separate failure-mode cache patterns from steady-state read bottlenecks.

## Input/Output Pairs

### Pair 1 -- Baseline: Read Bottleneck
```
Input:  "Reads slow as traffic grows, DB CPU pegged at 100%, writes unaffected."
Output: READ BOTTLENECK -- add read-through cache (Redis/Memcached) + read replicas; route SELECT traffic off the primary.
```

### Pair 2 -- Baseline: Write Hotspot
```
Input:  "Write throughput degrades when many users update their profile view-count simultaneously; deadlock errors in logs."
Output: WRITE HOTSPOT -- shard the hot row or redesign partition key; use counter aggregation or async increment to avoid row-level lock contention.
```

### Pair 3 -- Baseline: No Horizontal Scale
```
Input:  "Single web server CPU/RAM maxed; adding more app instances doesn't help because sessions are stored in-process."
Output: NO HORIZONTAL SCALE -- move session state to external store (Redis); add load balancer; app tier becomes stateless and horizontally scalable.
```

### Pair 4 -- Baseline: No Backpressure
```
Input:  "P99 latency spikes 10x during traffic bursts; service eventually recovers but drops requests in the meantime."
Output: NO BACKPRESSURE -- introduce async queue (SQS/Kafka) between ingestion and processing; add rate limiter + circuit breaker to shed load gracefully before queue overflows.
```

### Pair 5 -- Edge case: Premature Sharding
```
Input:  "Team sharded the DB across 8 nodes at 10k users; cross-shard queries are slow, migrations take days, and throughput is no better than before."
Output: PREMATURE SHARDING -- merge back to a single node or small replica set; profile actual hotspots under real load before re-sharding; complexity cost exceeded benefit at this scale.
```

### Pair 6 -- Edge case: Cache Stampede
```
Input:  "After a cache expiry (TTL hit or cold restart), DB is hammered by thousands of simultaneous cache-miss reads for the same key."
Output: CACHE STAMPEDE -- apply probabilistic early expiry (XFetch algorithm) to refresh hot keys before TTL; or use a mutex/lock so only one requester rebuilds the cache entry while others wait or serve stale.
```

### Pair 7 -- Hard: Thundering Herd
```
Input:  "After a 5-minute outage, all clients reconnect simultaneously; server crashes again immediately even though load was fine pre-outage."
Output: THUNDERING HERD -- add jitter to client reconnect delay (e.g. sleep = base + random(0, base)); use exponential backoff with cap; server-side: token bucket rate limiter on new connections to absorb the reconnect storm gradually.
```

## Edge Cases Covered

| Pair | Pattern | Key distinction |
|------|---------|----------------|
| Pair 5 | Premature sharding | Complexity cost > throughput gain at low scale; profile before sharding |
| Pair 6 | Cache stampede | Cold-start/TTL-expiry failure mode -- fix is probabilistic expiry, NOT more replicas |
| Pair 7 | Thundering herd | Temporal burst on reconnect, not steady-state load -- jitter + backoff, not scaling |


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
| [[p01_kc_repo_assimilation_candidates]] | mission context | 0.91 |
| p08_pat_caching_strategy | downstream pattern | 0.88 |
| skill_design_scalable_system | downstream skill | 0.85 |
| [[p01_fse_clean_arch_layer_placement]] | sibling few_shot (same wave) | 0.72 |
| [[p01_kc_concept_graph]] | graph entry | 0.55 |
