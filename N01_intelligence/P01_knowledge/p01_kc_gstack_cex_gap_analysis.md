---
id: p01_kc_gstack_cex_gap_analysis
kind: knowledge_card
pillar: P01
nucleus: n01
domain: capability-intelligence
version: 1.0.0
created: 2026-06-14
quality: null
source_attribution: "Methodology assimilated from gstack (garrytan/gstack, MIT, commit 14fc0866d9) -- adapted to CEX taxonomy."
tags: [gstack, gap-analysis, capability-map, assimilation, GSTACK_ASSIM]
8f: "F3_inject"
keywords: [design-shotgun, taste-profile, prompt-injection-defense, diataxis, continuous-checkpoint, capability-gap, gstack, assimilation]
related:
  - p01_kc_gstack_attribution_ledger
  - kc_repo_assimilation_pipeline
  - p01_kc_competitive_agent_frameworks
  - p01_kc_competitor_openclaw
---

> N01 Analytical Envy lens: every gstack capability vs. at least 2 CEX alternatives -- verdict must
> justify EVERY skip and EVERY build. This is the on-disk map that prevents duplicate work and
> surfaces Wave-2 candidates.

---

## Ground Truth

| Field | Value |
|-------|-------|
| Source | `garrytan/gstack` (MIT, commit `14fc0866d9`) |
| Fetched | 2026-06-14 by N07 via MCP fetch |
| Total capabilities audited | 52 (30 sprint + 15 power tools + 7 binaries/features) |
| GSTACK_ASSIM Wave 1 | design-shotgun/taste, injection-defense, Diataxis (pre-built by N03/N05/N04) |
| Verdict tally | 33 OVERLAP / 13 PARTIAL / 6 NET-NEW |

gstack turns Claude Code into a virtual engineering team: specialist slash-commands run as a
sprint Think->Plan->Build->Review->Test->Ship->Reflect. Each skill writes an artifact the next
reads. CEX already has the orchestration spine (8F, dispatch/grid/swarm/crews, quality gates,
cross-provider council, cybersec vertical, spec-kit). This KC maps every gstack capability to
CEX taxonomy -- skip list, build list, and second-tier candidates.

---

## Full Capability Roster -- Verdict Table

### Sprint Specialists (30)

| gstack capability | What it does (1 line) | CEX equivalent (artifact / tool) | Verdict | CEX kind mapping (net-new only) |
|---|---|---|---|---|
| office-hours | Pre-session forcing questions; "10-star" mental model to elicit true vision before any work | GDP (`guided-decisions.md`) + `discovery_questions` kind; lacks structured 10-star forcing ritual | PARTIAL | `discovery_questions` instance (Wave 2) |
| plan-ceo-review | Write structured plan for CEO-level strategic review (business impact, alignment) | `decision_record` + F7c COUNCIL + scoring_rubric (CEO role lens) | OVERLAP | -- |
| plan-eng-review | Engineering review checklist and plan | `quality_gate` + N05 `/code-review` skill + F7c COUNCIL | OVERLAP | -- |
| plan-design-review | Design review checklist and criteria | `quality_gate` + `scoring_rubric` (design lens) | OVERLAP | -- |
| plan-devex-review | Developer-experience review against DX heuristics | `quality_gate` + `scoring_rubric` (DX lens) | OVERLAP | -- |
| design-consultation | Design intake/consultation before any build (elicit constraints + preferences) | GDP + `discovery_questions`; design-intake framing absent | PARTIAL | `discovery_questions` (design-intake variant) |
| review | General artifact/code review | `quality_gate` + `scoring_rubric` + `/code-review` skill + F7c COUNCIL | OVERLAP | -- |
| investigate | Root-cause investigation Iron Law: trace data flow, test hypotheses, STOP after 3 failed fixes | `bugloop` automates fix loops but has no "no-fix-without-investigation-first" Iron Law or hypothesis-test sequence | PARTIAL | `reasoning_strategy` instance (Wave 2) |
| design-review | Review a specific design artifact | `quality_gate` + `scoring_rubric` | OVERLAP | -- |
| devex-review | Developer-experience audit (DX-specific quality gate) | `quality_gate` + `scoring_rubric` (DX lens) | OVERLAP | -- |
| design-shotgun | Generate 4-6 UI variants, open comparison board, collect structured feedback, iterate | CEX `swarm` generates N variants but has NO persistent taste profile + feedback-loop | NET-NEW | `pattern` (shotgun+taste loop, P08) -- Wave 1, pre-built by N03 |
| design-html | Convert approved mockup to working HTML | `landing_page` builder + `frontend-design` skill | OVERLAP | -- |
| qa | Quality-assurance testing (run + report + fix) | `smoke_eval` + `e2e_eval` + `unit_eval` + N05 testing pipeline | OVERLAP | -- |
| qa-only | QA testing without fixes (report only) | `smoke_eval` + `e2e_eval` in report-only mode | OVERLAP | -- |
| pair-agent | Collaborative pair-programming between agent and developer | N03 dispatch + grid (two agents on same codebase) | OVERLAP | -- |
| cso | Chief Security Officer scan: LLM-agent skill supply-chain audit, zero-noise (8/10 gate, concrete exploit scenarios) | Constitution VII + cybersec vertical covers generic OWASP/STRIDE; agent-specific supply-chain scan is absent | NET-NEW | `guardrail` (P11) + `threat_model` (P11) -- Wave 1, pre-built by N05 |
| ship | Deploy and ship completed work | N05 deployment pipeline + `deployment_manifest` | OVERLAP | -- |
| land-and-deploy | Deploy + verify landing (post-deploy smoke check) | N05 + `deployment_manifest` + `canary_config` | OVERLAP | -- |
| canary | Canary deployment with graduated traffic shift | `canary_config` kind (P09) | OVERLAP | -- |
| benchmark | Performance benchmarking of agent/system | `benchmark` kind + `benchmark_suite` + `cex_router_v2.py` multi-model bench | OVERLAP | -- |
| document-release | Build Diataxis coverage map; surface doc gaps in PR body | CEX has doc kinds but no Diataxis quadrant classification or coverage-map method | NET-NEW | `pattern` (Diataxis-for-CEX, P08) -- Wave 1, pre-built by N04 |
| document-generate | Research codebase then generate Diataxis-classified docs | CEX has doc kinds (context_doc, api_reference, quickstart_guide) but no Diataxis generation protocol | NET-NEW | `pattern` (Diataxis-for-CEX, P08) -- Wave 1, pre-built by N04 |
| retro | Retrospective; extract lessons-learned from completed sprint | `evolve` (AutoResearch loop) + `learning_record` | OVERLAP | -- |
| browse | Browser navigation for research or end-to-end testing | Playwright MCP + Chrome CDP + `browser_tool` kind | OVERLAP | -- |
| setup-browser-cookies | Configure browser authentication cookies for a session | Chrome CDP (`boot/chrome_cdp.ps1`) + browser_tool config | OVERLAP | -- |
| autoplan | Auto-generate sprint plan from intent description | N07 8F F4 REASON + `/plan` skill + the Task tool | OVERLAP | -- |
| spec | Write detailed technical spec from a plan | `/spec` skill + cexai spec-kit (decision_manifest + handoff templates) | OVERLAP | -- |
| learn | Extract session learnings into persistent domain skills with per-site quarantine | `learning_record` (P10) captures learnings; quarantine-before-trust activation protocol absent | PARTIAL | `learning_record` instance (content); domain-skills quarantine feeds into `guardrail` |
| make-pdf | Convert documents to PDF | `markitdown-mcp` (PDF conversion) + `document_loader` pipeline | OVERLAP | -- |
| diagram | Generate architecture / flow diagrams | `diagram` kind (P08) + diagram-builder | OVERLAP | -- |

### Power Tools (15)

| gstack capability | What it does (1 line) | CEX equivalent (artifact / tool) | Verdict | CEX kind mapping (net-new only) |
|---|---|---|---|---|
| codex | Route tasks to Codex/OpenAI runtime | Multi-runtime dispatch (codex boot scripts + `nucleus_models.yaml` fallback chain) | OVERLAP | -- |
| careful | Warn user before destructive commands (rm -rf, DROP TABLE, force-push) | Constitution VIII (gate irreversible behind human approval -- policy); no concrete pre-command warning hook | PARTIAL | Contributes to `guardrail` layer 5 (Wave 1, pre-built by N05) |
| freeze | Lock a directory against edits for the session duration | No CEX directory-locking mechanism | PARTIAL | Contributes to `guardrail` layer 5 (scope-lock component, Wave 1, pre-built by N05) |
| guard | Always-on version of careful (persistent destructive-command gate) | Constitution VIII (policy) but no always-on pre-execution guard implementation | PARTIAL | Contributes to `guardrail` layer 5 (Wave 1, pre-built by N05) |
| unfreeze | Reverse a freeze lock | Tied to freeze concept; no standalone equivalent | PARTIAL | Contributes to `guardrail` freeze/unfreeze lifecycle (Wave 1, pre-built by N05) |
| open-gstack-browser | Open browser with gstack auth and cookie config | Chrome CDP + Playwright MCP | OVERLAP | -- |
| setup-deploy | Set up deployment environment and credentials | `env_config` + `deployment_manifest` + N05 operations | OVERLAP | -- |
| setup-gbrain | Initialize gbrain semantic memory subsystem | RAG stack: `rag_source` + `retriever_config` + `embedding_config` + `cex_retriever.py`; mechanism differs (TF-IDF vs. semantic) | PARTIAL | `rag_source` + `retriever_config` (concept covered, implementation differs) |
| sync-gbrain | Sync gbrain memory with current project state | `cex_memory_update.py` + `cex_index.py` re-indexing; same purpose, different mechanism | PARTIAL | `knowledge_index` update cycle (P10 memory) |
| gstack-upgrade | Self-upgrade gstack skills | `cex_evolve.py` (AutoResearch loop) + `/evolve` skill + `self_improvement_loop` kind | OVERLAP | -- |
| ios-qa | iOS app quality assurance testing | `smoke_eval` + `e2e_eval` (platform-agnostic); iOS-specific config absent but same kinds apply | PARTIAL | `e2e_eval` + `smoke_eval` (mobile=ios config, not a new kind) |
| ios-fix | Fix iOS bugs | `bugloop` + N05 debug pipeline | OVERLAP | -- |
| ios-design-review | Review iOS UI design against platform guidelines | `quality_gate` + `scoring_rubric` (mobile UI lens) | OVERLAP | -- |
| ios-clean | Clean iOS project build artifacts | N05 hygiene + `cex_hygiene.py` | OVERLAP | -- |
| ios-sync | Sync iOS project dependencies and certificates | N05 operations + `env_config` | OVERLAP | -- |

### Binaries / Features (7)

| gstack capability | What it does (1 line) | CEX equivalent (artifact / tool) | Verdict | CEX kind mapping (net-new only) |
|---|---|---|---|---|
| gstack-model-benchmark | Benchmark LLM models for task-specific fitness | `benchmark_suite` + `cex_router_v2.py` multi-model bench + `model_card` kind | OVERLAP | -- |
| gstack-taste-update | Write approved/rejected designs into persistent taste profile with 5%/week recency decay | No CEX preference-decay memory with approve/reject signal log | NET-NEW | `user_model` (P10, taste profile) -- Wave 1, pre-built by N03 |
| gstack-ios-qa-daemon | Continuous iOS QA daemon (persistent background testing) | `daemon` kind (P02/P12) + N05 continuous testing | OVERLAP | -- |
| gstack-ios-qa-mint | Fresh iOS QA environment provisioning | `sandbox_config` + `sandbox_spec` + N05 | OVERLAP | -- |
| continuous-checkpoint-mode | Auto-WIP commits with structured [gstack-context] body: decisions / remaining-work / failed-approaches; /context-restore rebuilds session state | CEX has n07_task.md self-handoff but NO auto WIP-checkpoint commits with structured body or context-restore | NET-NEW | `checkpoint` (P10) -- Wave 2 candidate |
| domain-skills | Per-site/domain learned behaviors; 3-use quarantine before activation; cross-project promotion is explicit gate | `learning_record` captures behaviors but lacks quarantine-before-trust activation protocol | PARTIAL | Contributes to `guardrail` graduated-trust layer (Wave 1, N05); `learning_record` covers content side |
| gbrain | Persistent semantic memory subsystem (search over agent memories) | P10 memory stack (entity_memory, knowledge_index, learning_record) + P01 RAG stack (rag_source, retriever_config, embedding_config) | PARTIAL | P01 + P10 stack (concept covered; CEX=TF-IDF/vector, gbrain=semantic agent memory) |

---

## Verdict Tally

| Verdict | Count | Pct |
|---------|------:|----:|
| OVERLAP | 33 | 63% |
| PARTIAL | 13 | 25% |
| NET-NEW | 6 | 12% |
| **Total** | **52** | **100%** |

---

## Net-New Ranked

### Wave 1 (in flight -- built by N03/N05/N04)

| Rank | gstack capability | CEX kind(s) | Assigned to | Why high priority |
|------|---|---|---|---|
| 1 | design-shotgun + gstack-taste-update | `pattern` (shotgun+taste loop) + `user_model` (taste profile, 5%/wk decay) | N03 | Uniquely novel: learning loop (approve/reject -> weighted profile -> better variants) absent anywhere in CEX |
| 2 | cso + careful + freeze + guard + domain-skills | `guardrail` (6-layer injection defense) + `threat_model` (attack surface map) | N05 | LLM-agent prompt-injection defense is the most critical unaddressed security surface; feeds into constitution VII concretely |
| 3 | document-release + document-generate | `pattern` (Diataxis-for-CEX + coverage-map method) | N04 | Framework gap: CEX has 8+ doc kinds with no unifying classification; coverage-map reveals gaps instantly |

### Wave 2 (conditional -- build if Wave 1 passes gate)

| Rank | gstack capability | CEX kind | Why |
|------|---|---|---|
| 1 | continuous-checkpoint-mode | `checkpoint` enrichment | HIGH VALUE: auto-WIP commits with structured body solve the overnight-reboot data-loss risk documented in memory; n07_task.md handoff is manual; this automates it |
| 2 | investigate Iron Law | `reasoning_strategy` instance | Addresses the root cause of "fix before understanding" anti-pattern; complements `bugloop` at the reasoning layer |
| 3 | office-hours (10-star) | `discovery_questions` instance | Strong GDP entry-point; forces vision clarity before any work; CEX GDP is close but lacks the 10-star ritual |

---

## Why Not a New Kind (5-Question Taxonomy Test)

For each NET-NEW capability: does it NEED a new CEX kind or does an existing kind cover it?
All 6 pass the existing-kind test -- no new taxonomy required.

### design-shotgun -> `pattern` (existing P08)

| Question | Answer | Verdict |
|----------|--------|---------|
| 1. Unique creation ritual (distinct from all existing builders)? | No -- pattern-builder covers "reusable methodology with preconditions, steps, and outputs" | Existing kind |
| 2. Schema fields that no existing kind has? | No -- pattern frontmatter (process_steps, preconditions, postconditions) already captures the shotgun loop | Existing kind |
| 3. Produces a standalone artifact? | Yes, but so does `pattern` | No new kind |
| 4. Domain-specific in a way no builder serves? | No -- the methodology is general-purpose (any swarm-variant kind) | Existing kind |
| 5. Existing builder produces wrong output? | No -- pattern-builder guided by shotgun context yields the right artifact | Existing kind |
| **Verdict** | 0/5 new-kind criteria met | **Use `pattern`** |

### gstack-taste-update -> `user_model` (existing P10)

| Question | Answer | Verdict |
|----------|--------|---------|
| 1. Unique creation ritual? | No -- user-model-builder captures "per-user preference model"; taste profile IS a user_model variant | Existing kind |
| 2. Novel schema fields? | No -- user_model can carry `preference_weights`, `decay_rate`, `approval_log` as extensions | Existing kind |
| 3. Standalone artifact? | Yes, but user_model is already standalone | No new kind |
| 4. Domain-specific gap? | No -- user_model is domain-agnostic; taste = design preference domain of user_model | Existing kind |
| 5. Builder produces wrong output? | No -- user-model-builder with taste-profile context produces correct artifact | Existing kind |
| **Verdict** | 0/5 criteria met | **Use `user_model`** |

### cso / careful / freeze / guard / domain-skills -> `guardrail` + `threat_model` (existing P11)

| Question | Answer | Verdict |
|----------|--------|---------|
| 1. Unique creation ritual? | No -- guardrail-builder covers "defense mechanisms with detect/action per layer"; threat-model-builder covers "attack vectors and mitigations" | Existing kinds |
| 2. Novel schema? | No -- guardrail has layers[], each with detect/action; threat_model has vectors[] + STRIDE mapping | Existing kinds |
| 3. Standalone? | Yes, but both guardrail and threat_model are already standalone | No new kind |
| 4. LLM-agent domain gap? | LLM-agent DOMAIN is new to these kinds but the kind schema serves it without modification | Existing kinds |
| 5. Wrong builder output? | No -- guardrail-builder with prompt-injection context yields the correct 6-layer artifact | Existing kinds |
| **Verdict** | 0/5 criteria met | **Use `guardrail` + `threat_model`** |

### document-release + document-generate -> `pattern` (existing P08)

| Question | Answer | Verdict |
|----------|--------|---------|
| 1. Unique creation ritual? | No -- Diataxis is a classification FRAMEWORK (methodology = pattern); the doc kinds it classifies already exist | Existing kind |
| 2. Novel schema? | No -- pattern frontmatter captures a framework with classification rules | Existing kind |
| 3. Standalone? | Yes, but `pattern` is already standalone | No new kind |
| 4. Domain gap? | No -- Diataxis applies universally; it classifies CEX's existing doc kinds, does not need a new one | Existing kind |
| 5. Builder produces wrong output? | No -- pattern-builder with Diataxis context yields quadrant-map artifact | Existing kind |
| **Verdict** | 0/5 criteria met | **Use `pattern`** |

### continuous-checkpoint-mode -> `checkpoint` (existing P10)

| Question | Answer | Verdict |
|----------|--------|---------|
| 1. Unique creation ritual? | No -- checkpoint-builder covers "session state snapshots for resume"; gstack's body structure is content, not a schema category | Existing kind |
| 2. Novel schema? | No -- checkpoint kind carries decisions/remaining/failed as body sections; no new frontmatter fields needed | Existing kind |
| 3. Standalone? | Yes, but `checkpoint` is already standalone | No new kind |
| 4. Domain gap? | The auto-commit mechanism is a tool behavior, not a kind schema gap | Existing kind |
| 5. Builder produces wrong output? | No -- checkpoint-builder with gstack-context body template yields correct artifact | Existing kind |
| **Verdict** | 0/5 criteria met | **Use `checkpoint`** |

---

## Do-Not-Rebuild Summary (Overlaps by Category)

| Category | gstack capabilities | CEX coverage |
|----------|-------------------|--------------|
| Orchestration / sprint | autoplan, spec, retro, ship, land-and-deploy | 8F+dispatch+swarm+crews+/spec+/evolve |
| Code review / quality | review, plan-ceo-review, plan-eng-review, plan-design-review, plan-devex-review, design-review, devex-review | quality_gate+scoring_rubric+F7c COUNCIL+/code-review |
| Generic security | (see cybersec vertical) | N01 cybersec 80 skills -- OWASP/STRIDE covered |
| Browser / MCP | browse, setup-browser-cookies, open-gstack-browser | Playwright MCP + Chrome CDP + browser_tool |
| Model routing | codex, gstack-model-benchmark, gstack-upgrade | cex_router_v2.py + benchmark_suite + evolve |
| iOS testing | ios-qa, ios-fix, ios-design-review, ios-clean, ios-sync, gstack-ios-qa-daemon, gstack-ios-qa-mint | smoke_eval+e2e_eval+bugloop+daemon+sandbox_config |
| Spec authoring | spec, diagram, make-pdf | /spec skill + diagram kind + markitdown-mcp |
| Learning / memory | retro, gstack-upgrade | learning_record + cex_evolve + self_improvement_loop |
| Deployment | ship, land-and-deploy, canary, setup-deploy | deployment_manifest + canary_config + N05 |
| Pair/QA | pair-agent, qa, qa-only | grid dispatch + smoke_eval + e2e_eval |

---

## Attribution

Methodology assimilated from gstack (garrytan/gstack, MIT, commit 14fc0866d9) -- adapted to CEX taxonomy.
No gstack source code vendored. This is an assimilation (methodology -> typed-kind instances).
See companion artifact [[p01_kc_gstack_attribution_ledger]] for per-capability license record.
