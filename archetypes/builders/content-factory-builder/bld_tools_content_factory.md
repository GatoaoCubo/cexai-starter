---
kind: tools
id: bld_tools_content_factory
pillar: P04
llm_function: CALL
purpose: Tools and modules available for content_factory production and runtime
quality: null
title: "Tools Content Factory"
version: "1.0.0"
author: n03_builder
tags: [content_factory, builder, content-fabric]
tldr: "Golden and anti-examples for content_factory construction, demonstrating the brief -> N-row fan-out and common pitfalls."
domain: "content factory construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F5_call"
keywords: [content factory construction, tools content factory, content_factory, builder, content-fabric, "python _tools/cex_content_factory.py --demo", "python _tools/cex_content_factory.py --self-test", make_brief, produce_content_bundle, build_library_rows]
density_score: 0.90
related:
  - bld_tools_social_publisher
  - bld_knowledge_card_content_factory
  - bld_architecture_content_factory
  - p01_kc_content_factory
  - content-factory-builder
---
# Tools: content-factory-builder

## Reference Implementation (this kind's real runtime; PRODUCE only)
| Module | Purpose | Core API |
|--------|---------|----------|
| `_tools/cex_content_factory.py` | THE producer -- brief -> grounded multi-channel bundle | `make_brief()`, `default_channel_matrix()`, `brief_source()`, `produce_content_bundle()`, `build_library_rows()`, `run_factory()` (alias) |

## Reused Downstream Modules (this kind's `depends_on`: social_publisher, supabase_data_layer)
| Module | Role | Core API |
|--------|------|----------|
| `_tools/cex_content_review.py` | REVIEW -- the approved-list HITL gate | `ReviewQueue()`, `.submit()`, `.approve(post_id, by=)`, `.revoke(post_id)`, `.edit(post_id, channel, **fields)`, `.approved_for_publish()`, `.pending_review()`, `gate_to_publish_seam(queue, post_id=)` |
| `_tools/cex_channel_publisher.py` | PUBLISH-SEAM -- vendor-agnostic, fail-closed | `NoOpPublisher`, `PublishResult`, `channel_to_platform()`, `clamp_hashtags(tags, platform)`, `get_publisher(channel)`, `build_publish_readiness()` |

## Reused Upstream Engines (imported by cex_content_factory.py; degrade-never on ImportError)
| Module | Role | Core API |
|--------|------|----------|
| `_tools/cex_grounded_copy.py` | The no-fabrication engine (W2 P3, G1-G10 gate) | `extract_copy()`, `grounding_check()`, `source_text_of()` |
| `_tools/cex_tenant_voice_profile.py` | The voice knob (optional, passed as `voice_profile=`) | `load_voice_profile()` |
| `_tools/cex_canonical_product.py` | Canonical product enrichment (optional, `brief["canonical"]`) | `CanonicalProduct` shape (consumed via `source_text_of()`) |

## CLI Entry Points (offline, network-free)
| Command | Purpose |
|---------|---------|
| `python _tools/cex_content_factory.py --demo` | Runs the brief -> grounded bundle demo (deterministic + a fabricating-LLM proof) |
| `python _tools/cex_content_factory.py --self-test` | Network-free, DB-free correctness checks for the producer |
| `python _tools/cex_content_review.py --self-test` | Correctness checks for the review queue / approval triad |
| `python _tools/cex_channel_publisher.py --self-test` | Correctness checks for the publish seam (fail-closed proof) |
| `python -m pytest tests/test_content_fabric.py -q` | The end-to-end produce -> review -> publish integration suite (14 tests) |

## Production Tools (CEX internal)
| Tool | Purpose | When |
|------|---------|------|
| cex_compile.py | Compile artifact .md -> .yaml | After artifact creation |
| cex_hooks.py | Validate frontmatter | Pre-save |
| cex_doctor.py | Check builder health (7-column report) | Post-build audit |
| cex_score.py | Assign quality score | Peer review |
| cex_kind_tool_map.py | Generic kind -> tool bucket (shared boilerplate) | Resolver fallback |
| cex_8f_runner.py | Full 8F pipeline runner | `--mode A\|B\|auto` builds |

## Data Sources for Builder
| Source | Path | Data |
|--------|------|------|
| P04 schema | `N00_genesis/P04_tools/_schema.yaml` | Field definitions for the tools pillar |
| Kind-KC | `N00_genesis/P01_knowledge/library/kind/kc_content_factory.md` | content_factory domain knowledge (already exists; do not recreate) |
| Sibling KC | `N00_genesis/P01_knowledge/library/kind/kc_social_publisher.md` | The publish-seam contract this kind hands off to |
| Sibling KC | `N00_genesis/P01_knowledge/library/kind/kc_content_library.md` | The row shape this kind's output mirrors |

## Tool Permissions

| Category | Tools | Status |
|----------|-------|--------|
| ALLOWED | Read, Write, Edit, Bash, Glob, Grep | Explicitly permitted |
| DENIED | (none) | Explicitly blocked |
| EFFECTIVE | Bash, Edit, Glob, Grep, Read, Write | ALLOWED minus DENIED |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_social_publisher]] | sibling | 0.36 |
| [[bld_knowledge_card_content_factory]] | upstream | 0.34 |
| [[bld_architecture_content_factory]] | downstream | 0.31 |
| [[p01_kc_content_factory]] | upstream | 0.31 |
| [[content-factory-builder]] | upstream | 0.29 |
