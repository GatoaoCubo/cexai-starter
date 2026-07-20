---
id: kc_consolidation_policy
kind: knowledge_card
8f: F3_inject
title: Consolidation Policy
version: 1.0.0
quality: null
pillar: P01
tldr: "Memory lifecycle policy governing creation, retention, pruning, and deletion of stored data"
when_to_use: "When defining automated rules for data retention, deduplication, and time-based archival"
keywords: [metadata tagging, data retention, automatic pruning, data archiving, user-defined retention rules, duplicate entries, obsolete formats, audit trail, consolidation command, manual reviews]
density_score: 0.95
related:
  - kc_test_consolidate_loop
  - bld_knowledge_card_consolidation_policy
  - consolidation-policy-builder
---

# Consolidation Policy

This policy governs memory lifecycle management through three stages:

1. **Creation**  
   - New data is stored in volatile memory  
   - Metadata is automatically tagged with timestamp and priority

2. **Retention**  
   - Data is retained based on:  
     - Frequency of access (last 7 days)  
     - Criticality flags  
     - User-defined retention rules  
   - Automatic pruning occurs daily at 2:00 AM

3. **Deletion**  
   - Data older than 90 days is archived  
   - Data with zero access in 30 days is deleted  
   - User confirmation required for sensitive data

## Consolidation Guidelines
- Consolidate redundant data weekly
- Prioritize consolidation of:  
  - Duplicate entries  
  - Obsolete formats  
  - Low-value metadata
- Maintain 30-day audit trail for all deletions
- Use the `/consolidate` command for manual reviews
- Automatic consolidation runs nightly with 15% buffer
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_card_consolidation_policy]] | sibling | 0.23 |
| [[consolidation-policy-builder]] | downstream | 0.22 |
