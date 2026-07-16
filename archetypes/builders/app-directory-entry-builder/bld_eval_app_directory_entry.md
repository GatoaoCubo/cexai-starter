---
kind: quality_gate
id: p05_qg_app_directory_entry
pillar: P11
llm_function: GOVERN
purpose: Quality gate with HARD and SOFT scoring for app_directory_entry
quality: null
title: "Quality Gate App Directory Entry"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [app_directory_entry, builder, quality_gate]
tldr: "Quality gate with HARD and SOFT scoring for app_directory_entry"
domain: "app_directory_entry construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F7_govern"
keywords: [app_directory_entry construction, app_directory_entry, builder, quality_gate, ## anti-example 1: missing key sections, ## why it fails
omits critical sections like, quality gate, fail condition, scoring guide, senior manager]
density_score: 0.85
---
## Quality Gate

## Definition
| metric | threshold | operator | scope |
|---|---|---|---|
| Required fields | 100% | must be present | tagline, screenshots, install steps, demo link |

## HARD Gates
| ID | Check | Fail Condition |
|---|---|---|
| H01 | YAML frontmatter valid | invalid YAML syntax |
| H02 | ID matches pattern | ID does not match ^p05_ade_[a-z][a-z0-9_]+.md$ |
| H03 | kind field matches 'app_directory_entry' | kind != 'app_directory_entry' |
| H04 | tagline present | tagline field missing or empty |
| H05 | screenshots >= 3 | fewer than 3 screenshots provided |
| H06 | install steps >= 2 | fewer than 2 install steps listed |
| H07 | demo link functional | demo link invalid or unreachable |
| H08 | app name present | app name field missing |

## SOFT Scoring
| Dim | Dimension | Weight | Scoring Guide |
|---|---|---|---|
| D01 | Tagline clarity | 0.10 | 0.0–1.0 based on conciseness |
| D02 | Screenshot quality | 0.15 | 0.0–1.0 based on relevance |
| D03 | Install steps completeness | 0.15 | 0.0–1.0 based on detail |
| D04 | Demo link usability | 0.10 | 0.0–1.0 based on accessibility |
| D05 | App name accuracy | 0.10 | 0.0–1.0 based on correctness |
| D06 | Category alignment | 0.10 | 0.0–1.0 based on relevance |
| D07 | Description completeness | 0.15 | 0.0–1.0 based on detail |
| D08 | UX consistency | 0.15 | 0.0–1.0 based on design |

## Actions
| Score | Action |
|---|---|
| GOLDEN (>=9.5) | Auto-publish |
| PUBLISH (>=8.0) | Approved |
| REVIEW (>=7.0) | Manual check |
| REJECT (<7.0) | Fix required |

## Bypass
| conditions | approver | audit trail |
|---|---|---|
| Critical bug in demo link | Senior Manager | Jira ticket # |
| Legal compliance override | Legal Team | Contract reference |
| Emergency release | CTO | Slack channel log |

## Examples

## Golden Example
```yaml
kind: app_directory_entry
name: Supabase
tagline: "Open source backend for modern apps, free tier included"
screenshots:
  - https://supabase.io/static/images/hero.png
  - https://supabase.io/static/images/dashboard.png
install_steps:
  - "Visit https://supabase.io"
  - "Sign up for a free account"
  - "Use CLI: `npm install -g supabase`"
demo_link: https://supabase.io/demo
description: "Supabase provides a free tier with PostgreSQL, Auth, and Realtime features. Ideal for startups and developers."
```

## Anti-Example 1: Missing Key Sections
```yaml
kind: app_directory_entry
name: ExampleApp
tagline: "A great app for everything"
screenshots: []
install_steps: []
demo_link: https://example.com
```
## Why it fails
Omits critical sections like `description` and lacks screenshots/install steps, making it incomplete for discovery.

## Anti-Example 2: Placeholder Names
```yaml
kind: app_directory_entry
name: ProviderA's App
tagline: "Example solution for hypothetical use cases"
screenshots:
  - https://providera.com/placeholder.png
install_steps:
  - "Download from ProviderA's site"
demo_link: https://providera.com
description: "This is a placeholder example for demonstration purposes only."
```
## Why it fails
Uses generic names like "ProviderA" and "ExampleApp" instead of real tools/vendors, reducing credibility and discoverability.

### H_RELATED: Cross-Reference Check (HARD)
- [ ] `related:` frontmatter field populated (min 3 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream or sibling reference
- Gate: REJECT if < 3 entries (auto-populated by cex_wikilink.py at F6.5)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
