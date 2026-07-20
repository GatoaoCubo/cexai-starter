---
id: kc_changelog
kind: knowledge_card
8f: F3_inject
title: Changelog Entry
version: 1.0.0
quality: null
pillar: P01
tldr: "Versioned record of product changes using SemVer with features, fixes, and breaking changes sections"
when_to_use: "When tracking release history and communicating changes to users or downstream consumers"
keywords: [semantic versioning, major, minor, patch, api endpoints, json, markdown]
density_score: 1.0
related:
  - changelog-builder
  - bld_knowledge_card_changelog
  - bld_output_template_changelog
  - bld_instruction_changelog
  - p10_mem_changelog_builder
---

# Changelog Entry

A changelog documents changes to a product using semantic versioning (SemVer). It should include:

## Semantic Versioning
Use `MAJOR.MINOR.PATCH` format:
- **MAJOR**: Breaking changes (e.g., 2.0.0)
- **MINOR**: New features (e.g., 1.1.0)
- **PATCH**: Bug fixes (e.g., 1.0.1)

## Entry Structure
```markdown
## [1.2.0] - 2023-10-15
### Features
- Added dark mode support
- Improved search algorithm

### Fixes
- Fixed login timeout issue
- Resolved CSS layout bug

### Breaking Changes
- Removed deprecated API endpoints
- Changed configuration format to JSON
```

## Best Practices
1. Use clear, concise language
2. Include release dates
3. Highlight security updates
4. Mention compatibility requirements
5. Keep entries ordered by date

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[changelog-builder]] | related | 0.44 |
| [[bld_knowledge_card_changelog]] | sibling | 0.41 |
| [[bld_output_template_changelog]] | downstream | 0.40 |
| [[bld_instruction_changelog]] | downstream | 0.39 |
| [[p10_mem_changelog_builder]] | downstream | 0.34 |
