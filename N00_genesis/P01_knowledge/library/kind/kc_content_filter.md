---
id: kc_content_filter
kind: knowledge_card
8f: F3_inject
title: Content Filter Pipeline Configuration
version: 1.0.0
quality: null
pillar: P01
tldr: "Three-stage pipeline config for content moderation: preprocessing, NSFW/toxicity filtering, and scoring"
when_to_use: "When configuring automated content moderation with pass/block/flag decisions and confidence thresholds"
keywords: [text normalization, tokenization, nsfw content detection, toxicity score, policy rule matching, contextual risk assessment, automated moderation recommendations, confidence score, filter decision, detected patterns]
density_score: 1.0
related:
  - p03_ch_kc_to_notebooklm
  - p11_schema_curation_nudge
  - p11_schema_revision_loop_policy
  - p03_ch_content_pipeline
  - content-filter-builder
---

# Content Filter Pipeline Configuration

This knowledge card defines the configuration schema for content filtering pipelines. The pipeline operates in three stages:

1. **Preprocessing**  
   - Text normalization (lowercasing, tokenization)
   - Special character removal
   - HTML entity decoding

2. **Filtering**  
   - NSFW content detection (using ML model)
   - Toxicity score calculation
   - Policy rule matching

3. **Post-processing**  
   - Result categorization (safe/unsafe/unknown)
   - Contextual risk assessment
   - Automated moderation recommendations

The pipeline accepts raw text input and produces structured output containing:
- Filter decision (pass/block/flag)
- Confidence score (0.0-1.0)
- Detected patterns
- Suggested mitigation actions

Configuration parameters include:
- `threshold`: Minimum confidence for blocking (default 0.85)
- `ruleset`: Policy rules to apply (default "community_guidelines")
- `language`: Text language code (auto-detected if empty)
- `context_window`: Maximum input length (default 1024 tokens)

```yaml
pipeline:
  stages:
    - name: preprocessing
      enabled: true
    - name: filtering
      enabled: true
    - name: post-processing
      enabled: true
```

```json
output_schema:
  type: object
  properties:
    decision: {type: string, enum: ["pass", "block", "flag"]}
    confidence: {type: number, minimum: 0, maximum: 1}
    patterns: {type: array, items: {type: string}}
    recommendations: {type: array, items: {type: string}}
```
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p03_ch_kc_to_notebooklm | downstream | 0.25 |
| p11_schema_curation_nudge | downstream | 0.25 |
| p11_schema_revision_loop_policy | downstream | 0.24 |
| p03_ch_content_pipeline | downstream | 0.24 |
| [[content-filter-builder]] | downstream | 0.24 |
