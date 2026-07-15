---
id: p01_kc_gstack_attribution_ledger
kind: knowledge_card
pillar: P01
nucleus: n01
domain: license-compliance
version: 1.0.0
created: 2026-06-14
quality: null
source_attribution: "Methodology assimilated from gstack (garrytan/gstack, MIT, commit 14fc0866d9) -- adapted to CEX taxonomy."
tags: [gstack, attribution, MIT, license-compliance, GSTACK_ASSIM]
8f: "F3_inject"
keywords: [MIT license, attribution, gstack, capability assimilation, license ledger, garrytan]
related:
  - p01_kc_gstack_cex_gap_analysis
  - kc_repo_assimilation_pipeline
---

> N01 license-compliance record. Every capability assimilated from gstack carries a row here.
> This is the on-disk audit trail required by the MIT license (attribution) and by
> kc_repo_assimilation_pipeline (provenance mandate).

---

## Source Metadata

| Field | Value |
|-------|-------|
| Repository | `garrytan/gstack` |
| URL | https://github.com/garrytan/gstack |
| License | MIT |
| License obligations | Attribution required in derivative works; no copyleft; no restrictions on commercial use |
| Source commit SHA | `14fc0866d9ac9d09d25adcac7b4437c0a235902b` |
| Fetched | 2026-06-14 |
| Fetched by | N07 via MCP fetch gateway (SOURCE_PACK.md pre-compilation) |
| Author | Garry Tan (YC) |
| Assimilation type | Methodology -> typed-kind instances (no source code vendored) |
| Zero-copy guarantee | No gstack .sh, .md, or .json files committed to this repo |

**Standard attribution line** (embedded in every assimilated artifact):
`Methodology assimilated from gstack (garrytan/gstack, MIT, commit 14fc0866d9) -- adapted to CEX taxonomy.`

---

## MIT License Text (abridged)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions: The above copyright notice and this
permission notice shall be included in all copies or substantial portions of the Software.

CEX compliance: the above copyright notice is reproduced in this ledger. No gstack source is
vendored; CEX assimilates METHODOLOGY (ideas expressed as CEX kinds), not copyrightable code.

---

## Per-Capability Attribution Ledger

Only NET-NEW and meaningful PARTIAL assimilations require attribution rows. OVERLAP capabilities
require no attribution (CEX independently implements equivalent functionality).

### Wave 1 Assimilations (in-flight, built by N03/N05/N04)

| Row | gstack capability | What was lifted | CEX kind produced | Pillar | Built by | Notes |
|-----|---|---|---|---|---|---|
| A1 | design-shotgun | Generate-many -> rank-by-learned-preference -> converge methodology; structured feedback collection loop | `pattern` (shotgun+taste loop) | P08 | N03 | Generalized beyond design: applicable to any swarm-variant kind |
| A2 | gstack-taste-update | Per-project preference record with 5%/week recency decay, approve/reject signal log, feed-back-into-generation contract | `user_model` (taste profile) | P10 | N03 | Decay rate and approval_log are novel fields on existing kind |
| A3 | cso | LLM-agent skill supply-chain scan methodology; zero-noise protocol (8/10 confidence gate, 17 FP exclusions, concrete exploit scenario requirement) | `guardrail` (layered injection defense) + `threat_model` (LLM-agent attack surface) | P11 | N05 | Specifically the supply-chain-scan methodology and zero-noise verification protocol |
| A4 | careful + freeze + guard | Destructive-command gate (warn before rm -rf, DROP TABLE, force-push); scope-lock (directory freeze); always-on guard mode | `guardrail` layers 4-5 | P11 | N05 | Contributes to layers 4 and 5 of the 6-layer guardrail artifact |
| A5 | domain-skills (quarantine) | Graduated trust: 3-use quarantine before a learned behavior activates; cross-project promotion is an explicit gate | `guardrail` layer 4 (graduated-trust quarantine) | P11 | N05 | The quarantine-before-trust protocol is the novel contribution |
| A6 | document-generate | Diataxis framework applied to doc generation: research-first, then classify output into tutorial/how-to/reference/explanation quadrants | `pattern` (Diataxis-for-CEX generation method) | P08 | N04 | Diataxis (Divio AG, CC-BY) is an external framework; gstack's IMPLEMENTATION methodology is what was lifted |
| A7 | document-release | Diataxis coverage-map method: enumerate existing docs -> bucket into 4 quadrants -> report empty quadrants as gaps; surface in PR body | `pattern` (Diataxis-for-CEX coverage-map method) | P08 | N04 | Coverage-map method is the distinct contribution; Diataxis quadrant taxonomy credited to Divio |

### Wave 2 Assimilations (candidates -- build conditional on Wave 1 gate pass)

| Row | gstack capability | What was lifted | CEX kind | Pillar | Priority | Notes |
|-----|---|---|---|---|---|---|
| B1 | continuous-checkpoint-mode | Auto-WIP commit body structure: decisions/remaining-work/failed-approaches fields; /context-restore session rebuild from checkpoint body | `checkpoint` enrichment | P10 | HIGH | Body structure (the 3 structured fields) is the novel contribution; checkpoint kind exists |
| B2 | investigate (Iron Law) | "No fixes without root-cause investigation" mandate; hypothesis-test sequence; hard stop after 3 failed fixes | `reasoning_strategy` instance | P08 | MEDIUM | The Iron Law constraint + forced-stop heuristic is the novel contribution |
| B3 | office-hours (10-star forcing) | Pre-session "imagine the 10-star version" mental model + structured forcing questions to elicit true vision | `discovery_questions` instance | P06/P01 | MEDIUM | The 10-star vision-elicitation technique is the novel contribution |

---

## Diataxis Co-Attribution Note

The Diataxis framework referenced in rows A6 and A7 was created by Divio AG and is licensed
under Creative Commons Attribution (CC-BY). gstack's implementation of Diataxis is MIT-licensed.
CEX's `pattern` artifact for Diataxis-for-CEX must carry both attributions:
- Framework: Diataxis by Divio AG (CC-BY) -- https://diataxis.fr
- Implementation methodology: gstack (garrytan/gstack, MIT, commit 14fc0866d9)

---

## Assimilation Protocol Compliance

| Check | Status |
|-------|--------|
| MIT attribution in every produced artifact frontmatter (`source_attribution` field) | REQUIRED |
| MIT attribution in body of every produced artifact | REQUIRED |
| No gstack source code committed to this repo | VERIFIED -- methodology only |
| Zero-copy: no .sh / .md / .json files from gstack vendored | VERIFIED |
| This ledger on disk before any artifact is committed | SATISFIED (this file) |
| Ledger updated when Wave 2 artifacts are built | PENDING (update rows B1-B3 on build) |

---

## Future Maintenance

When Wave 2 artifacts are built:
1. Move rows B1-B3 from "Wave 2 candidates" to a new "Wave 2 Assimilations" section
2. Fill in the "Built by" and commit SHA columns
3. Run `python _tools/cex_compile.py N01_intelligence/P01_knowledge/kc_gstack_attribution_ledger.md`
4. Commit with message `[N01][GSTACK_ASSIM] attribution ledger Wave 2 update`
