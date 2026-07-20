---
id: curation_nudge_n04
kind: curation_nudge
8f: F6_produce
nucleus: n04
pillar: P11
title: "Curation Nudge -- N04 Knowledge Persistence Prompts"
mirror_version: 1.0.0
promoted_from: null
overrides:
 tone: archival, dense, citation-thick
 voice: third-person encyclopedic
 sin_lens: Knowledge Gluttony
 required_fields:
 - sources
 - retrieval_method
 - freshness
 quality_threshold: 9.2
 density_target: 0.92
 example_corpus: "3+ examples with source manifest"
ownership: canonical
trigger:
 type: density_threshold
 threshold: 10 # unconfirmed knowledge items triggers nudge
cadence:
 min_interval_turns: 5
 max_per_session: 3
version: 1.0.0
quality: null
tags:
  - "n04"
  - "knowledge"
  - "curation_nudge"
  - "memory"
  - "P11"
keywords:
  - "knowledge"
  - "curation_nudge"
  - "memory"
  - "taught-terms registry nudge"
  - "knowledge corpus expansion nudge"
related:
 - agent_card_n04
 - p01_kc_memory_scope
 - memory-scope-builder
 - bld_manifest_memory_type
 - bld_knowledge_card_memory_scope
 - p10_em_n04_knowledge
when_to_use: "Load when working on curation_nudge in P11. Consult for how to act on this curation_nudge."
slots:
  queue_item: "<the artifact nudged for curation>"
  action: "<accept, revise, or discard>"
---

## Override Rationale

The knowledge nucleus **owns** the `curation_nudge` kind. Knowledge Gluttony
means the system must proactively prompt the user to persist any valuable
insight surfaced during the session. This nudge is specialised: it targets
memory-file persistence, taught-terms registry updates, and knowledge corpus
expansions -- the canonical memory destinations for this nucleus.

## Trigger Configuration

| Parameter | Value | Notes |
|-----------|-------|-------|
| Trigger type | density_threshold | Fire when unconfirmed knowledge count >= threshold |
| Threshold | 10 | Items accumulated without explicit persistence decision |
| Min interval | 5 turns | Don't interrupt rapid-fire exchanges |
| Max per session | 3 | Avoid nudge fatigue; escalate to user after 3rd |
| Observation source | retrieval_history + taught_terms | What to surface for confirmation |

## Prompt Templates

### Memory persistence nudge
```
Detected {{n}} unpersisted insights this session (taught_terms: {{tt}}, KCs: {{kc}}).
Persist to the project memory file? [Y/N]
Confirmed -> writes to {{destination}} and appends pointer to index.
```

### Taught-terms registry nudge
```
Taught {{n}} new terms: {{term_list}}.
Register in the taught-terms registry? [Y/N]
```

### Knowledge corpus expansion nudge
```
Corpus '{{corpus_id}}' grew by {{n}} docs this session.
Update the knowledge corpus record? [Y/N]
```

## Target Memory Destinations

| Destination | Kind | Trigger Condition |
|-------------|------|-------------------|
| project memory file | index | Any confirmed insight |
| taught-terms registry | entity_memory | Term metaphor->industry mapping confirmed |
| `N04_knowledge/P10_memory/entity_memory_n04.md` | entity_memory | Entity fact confirmed |

## Auto-write Behavior

When a peer confirms a nudge:
1. The nucleus writes directly to the destination artifact (no extra confirmation)
2. Appends a pointer to the memory index if not already present
3. Stamps `freshness: {{YYYY-MM-DD}}` on the new entry
4. Never overwrites a prior confirmed entry in place -- versions it instead

### How to use

```text
You are the consuming agent that acts on this curation_nudge under F6 PRODUCE.
- Resolve the open slots (queue_item, action) from the caller request.
- Honor every constraint and field contract declared above.
- Emit the result in the shape this curation_nudge defines; never improvise the schema.
```

### Procedure

```text
1. Load this artifact and read its contract under F6 PRODUCE.
2. Bind queue_item and action from the incoming request.
3. Validate the inputs against the constraints declared above.
4. Execute the curation_nudge behavior; resolve each open slot at act-time.
5. Verify the output shape, then signal completion to the orchestrator.
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[agent_card_n04]] | upstream | 0.32 |
| [[p01_kc_memory_scope]] | upstream | 0.28 |
| [[memory-scope-builder]] | upstream | 0.27 |
| [[bld_manifest_memory_type]] | upstream | 0.27 |
| [[bld_knowledge_card_memory_scope]] | upstream | 0.26 |
| [[p10_em_n04_knowledge]] | downstream | 0.30 |
