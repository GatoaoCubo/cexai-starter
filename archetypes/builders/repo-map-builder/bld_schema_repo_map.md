---
kind: schema
id: bld_schema_repo_map
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema -- SINGLE SOURCE OF TRUTH for repo_map
quality: null
title: "Schema Repo Map"
version: "1.0.0"
author: wave1_builder_gen
tags: [repo_map, builder, schema]
tldr: "Formal schema -- SINGLE SOURCE OF TRUTH for repo_map"
domain: "repo_map construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F1_constrain"
keywords: [repo_map construction, schema repo map, repo_map, builder, schema, "p01_rm_{{name}}.md", repository_url, version, tags, frontmatter fields]
density_score: 0.85
related:
  - bld_schema_usage_report
  - bld_schema_dataset_card
  - bld_schema_search_strategy
  - bld_schema_voice_pipeline
  - bld_schema_quickstart_guide
---

## Frontmatter Fields  
### Required  
| Field      | Type   | Required | Default | Notes                          |  
|------------|--------|----------|---------|--------------------------------|  
| id         | string | yes      | -       | Unique identifier              |  
| kind       | string | yes      | "repo_map" | CEX kind type               |  
| pillar     | string | yes      | "P01"   | Pillar classification          |  
| title      | string | yes      | -       | Repository name                |  
| version    | string | yes      | "1.0"   | Schema version                 |  
| created    | date   | yes      | -       | Creation timestamp             |  
| updated    | date   | yes      | -       | Last update timestamp          |  
| author     | string | yes      | -       | Owner/creator                  |  
| domain     | string | yes      | -       | Repository domain (e.g., GitHub) |  
| quality    | string | yes      | "draft" | Quality status                 |  
| tags       | list   | yes      | []      | Keywords                       |  
| tldr       | string | yes      | -       | Summary                        |  
| token_budget | int | yes | 1024 | Max tokens for this map |
| symbol_count | int | yes | - | Total symbols extracted |
| file_count | int | yes | - | Files included in map |
| extraction_method | string | yes | "tree-sitter" | tree-sitter \| ctags \| hybrid \| ast+pagerank |  

> **Enum reconciliation (R-304, 2026-07-11).** `_tools/cex_repo_map.py` (R-292,
> the repo's real, on-disk repo-map producer) is a clean-room Python
> implementation over the stdlib `ast` module + pure-Python PageRank -- it
> never uses tree-sitter or ctags, so it correctly reports its own
> `extraction_method` as `"ast+pagerank"`, a value the original 3-item enum
> above did not cover (the enum predates the tool; it was written against
> the generic aider-style archetype scaffold this builder's other ISOs still
> describe). Rather than force-fit that honest value into `hybrid` (a
> previous build of this kind correctly refused to do that -- see the w8e
> judge flag this row was spun from) or add an open-ended `other:` escape
> hatch (which would defeat the point of a closed enum), the minimal fix is
> to add the tool's real value as a 4th literal. `p01_rm_cex.md` (the
> pre-existing hand-curated repo map, `extraction_method: "manual"`) is a
> SEPARATE, PRE-EXISTING gap this row does not touch -- noted here for
> transparency, not fixed (out of this row's scope, which is reconciling
> specifically with cex_repo_map.py's value).

### Recommended  
| Field         | Type   | Notes                  |  
|---------------|--------|------------------------|  
| license_type  | string | License information    |  
| contributor_count | int  | Number of contributors |  

## ID Pattern  
^p01_rm_[a-zA-Z0-9_]+\.md$  

## Body Structure  
1. **Repository Overview**  
   - Description, purpose, and scope.  
2. **Mapping Details**  
   - Key-value pairs linking repository components.  
3. **Quality Assessment**  
   - Evaluation criteria and scores.  
4. **Domain-Specific Metadata**  
   - Additional fields for repository context.  
5. **Version History**  
   - Changes and updates over time.  

## Constraints  
- ID must follow `p01_rm_{{name}}.md` regex.  
- Required fields must be present and valid.  
- File size must not exceed 5120 bytes.  
- `repository_url` must be a valid URI.  
- `version` must use semantic versioning (e.g., "1.2.3").  
- `tags` must be unique and lowercase.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_usage_report]] | sibling | 0.64 |
| [[bld_schema_dataset_card]] | sibling | 0.64 |
| [[bld_schema_search_strategy]] | sibling | 0.62 |
| [[bld_schema_voice_pipeline]] | sibling | 0.61 |
| [[bld_schema_quickstart_guide]] | sibling | 0.61 |
