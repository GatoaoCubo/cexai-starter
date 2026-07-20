---
id: p12_dr_admin_orchestration
kind: dispatch_rule
pillar: P12
title: "Dispatch Rule: Admin Orchestration"
version: "1.0.0"
quality: null
tags: [dispatch-rule, orchestration, routing, multi-cli]
8f: F8_collaborate
nucleus: n07
domain: orchestration
created: "2026-07-20"
scope: admin_orchestration
agent_group: orchestrator
priority: 9
confidence_threshold: 0.70
fallback: n03
routing_strategy: keyword_match
tldr: "Routes incoming task intent to the right specialist nucleus by domain keyword: build->N03, research->N01, marketing->N02, knowledge->N04, ops->N05, commercial->N06."
related:
  - p12_wf_admin_orchestration
  - p01_kc_orchestration
  - dispatch
---

# Dispatch Rule: Admin Orchestration

## Purpose

Master routing table for an orchestrator nucleus. Maps incoming task intent to
the correct specialist nucleus by domain keyword. Each target nucleus has a
dedicated model/CLI profile suited to its domain (see `.cex/config/nucleus_models.yaml`).

## Routing Table

| # | Keywords | Target | Priority | Mode |
|---|---|---|---|---|
| 1 | build, create, scaffold, generate, artifact, kind | N03 (Builder) | 9 | solo (grid if > 3 artifacts) |
| 2 | research, analyze, paper, market, competitor, benchmark | N01 (Research) | 8 | solo |
| 3 | marketing, copy, ad, campaign, brand, creative, slogan | N02 (Marketing) | 7 | solo |
| 4 | knowledge, document, index, rag, glossary, context | N04 (Knowledge) | 8 | solo |
| 5 | code, test, debug, deploy, ci, cd, review, fix | N05 (Operations) | 8 | solo |
| 6 | sales, pricing, course, monetize, revenue, conversion | N06 (Commercial) | 7 | solo |

## Keyword Rationale

Keywords are domain-specific action verbs/nouns; extend the table with a
community language's own variants (see the intent-transmutation rule this
nucleus follows). Each rule covers a distinct domain with no keyword overlap.
Priority breaks ties when a task touches multiple domains.

## Confidence & Fallback

| Rule | Behavior |
|---|---|
| Threshold | 0.70 keyword-match score; below it, ask the human for clarification |
| Multiple matches | Highest priority wins; equal priority prefers more keyword hits |
| No match | Log to `.cex/runtime/signals/` as `dispatch_ambiguous` and wait |
| Default fallback | `{{fallback_nucleus}}` (N03) when nothing else resolves and escalation is undesired |

## References

- Workflow this rule feeds: [[p12_wf_admin_orchestration]]
- Vocabulary source: [[p01_kc_orchestration]]
- Command surface: [[dispatch]]

## Related Artifacts

| Artifact | Relationship |
|----------|---------------|
| [[p12_wf_admin_orchestration]] | downstream -- consumes this rule's routing decision |
| [[p01_kc_orchestration]] | upstream -- the orchestration vocabulary this rule draws from |
| [[dispatch]] | related -- the /dispatch command this rule backs |
