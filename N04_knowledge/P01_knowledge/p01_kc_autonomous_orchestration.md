---
id: p01_kc_autonomous_orchestration
kind: knowledge_card
pillar: P01
nucleus: N04
title: "Autonomous Orchestration -- The 6-Layer Autowire System"
version: 1.0.0
created: 2026-04-27
updated: 2026-04-27
author: n04_knowledge
domain: "autonomous orchestration, hook fan-out, 8F enforcement, boot pipeline, cron workflows, cost tracking"
quality: null
density_score: 0.92
status: PUBLISHED
mission: REFINE_v1.1
tags:
  - autonomous
  - autowire
  - hooks
  - 8f_enforcement
  - boot_pipeline
  - cron
  - cost_tracking
  - council
  - anti_sycophancy
related:
  - doc_autonomous_flow
  - showcase_quickstart_guide_cexai
  - p11_tools_revision_loop_policy
  - p02_ap_n04_knowledge
  - bld_tools_terminal_backend
  - cex_doctor_command
  - bld_tools_personality
  - p01_rm_cex
  - p05_cg_cex
tldr: "Autonomous orchestration is the wiring layer that turns 154 typed-knowledge tools and the 8F pipeline from manual ceremony into mechanical reflexes. Six layers (PreSession, Boot, PreToolUse, PostToolUse, Stop, Skills) fan a single user intent into intent resolution, model routing, quality scoring, indexing, council review, and cost rollup -- without the user typing any tool name. The 8F pipeline becomes a measured metric, not an LLM-discipline rule."
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_boot_pipeline, cex_cost_tracker. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

# Autonomous Orchestration -- The 6-Layer Autowire System

> **What this card does for you**: explains every reflex the system performs without being asked. Read it once to understand the levers; consult it again any time something fires that you did not expect, or fails to fire when it should.

CEX is a typed-knowledge AI brain. It owns 154 Python tools across 12 pillars and 8 nuclei. Before autowire, only 19 of those tools (12%) ran without a human invoking them by name. The other 135 sat as latent capability -- documented, tested, and unused. The 8F reasoning pipeline (8f-reasoning) was likewise documented as mandatory, but actual LLM compliance hovered around 30% because nothing in the runtime forced the markers. Autonomous orchestration closes that gap by wiring **every tool to a layer that fires it automatically**, and by promoting 8F from "rule the LLM should follow" to "metric the system measures and reports".

This knowledge_card is the canonical reference for that system. It maps the six layers, names every tool by its trigger, and shows how a single Write call fans out into six concurrent operations. It also documents three cron workflows for periodic maintenance, the cost tracker that verifies the README's "~70% cheaper via preflight" claim, and the anti-sycophancy council auto-trigger that prevents within-model score inflation.

## 1. Problem -- Why CEX Needed Autowire

The architecture review surfaced three structural gaps that no amount of LLM coaching could close.

### Gap 1: Tool fragmentation

A deep-scan of all 154 tools (`_docs/TOOLS_INVENTORY.md`) placed each one in a wiring bucket. Eighty-four (55%) had zero references in operational layers -- no hook called them, no boot script chained them, no skill suggested them. They could only be invoked by name on the CLI. A new contributor cloning the repo got 154 tools but only 19 fired automatically. The remaining 135 looked like dead code to anyone reading the runtime trace, even though every one was tested and documented. Theory said "CEX compounds across runtimes". Practice said "CEX runs whatever the human remembers to type". The gap between those two sentences was the entire problem.

### Gap 2: 8F is documented but not enforced

The 8F pipeline (F1 CONSTRAIN -> F2 BECOME -> F3 INJECT -> F4 REASON -> F5 CALL -> F6 PRODUCE -> F7 GOVERN -> F8 COLLABORATE) is the canonical reasoning protocol for every nucleus and every task, defined in 8f-reasoning and reinforced in `CLAUDE.md`. But it was a rule, not a mechanism. An LLM that skipped F1 (kind resolution), F3 (knowledge injection), or F8 (signal) faced no consequence -- the artifact still landed, the commit still went through, and no log noticed the omission. Compliance audits ran by reading transcripts after the fact. The result was predictable: F6 PRODUCE always fired (the artifact had to exist), F7 GOVERN sometimes fired (only when the LLM remembered the gate), and F1, F2, F8 fired about 30% of the time on average. Sessions that needed deep context injection (F3 INJECT) routinely shipped without it because nothing made the LLM stop and look.

### Gap 3: Boot path is hardcoded

The boot scripts that launch each nucleus (`boot/n07.ps1`, `boot/n01.ps1`, ...) were originally written with hardcoded model strings (`--model claude-opus-4-7`). The yaml-driven router (n07-orchestrator) existed but was bypassed for N07. Pre-flight tools -- intent resolver, secretariat compression, MCP preflight, router v2 -- existed but never ran in the boot path. So even when a nucleus had perfect runtime hooks, its launch was opaque: a fixed model, no context compression, no quota check, no router resolution. Whatever quota the user had on Claude Opus, that was what every spawn consumed, regardless of whether the task needed it.

These three gaps share a root: the system **knew how to do the right thing but never did it without being asked**. Autowire is the answer.

## 2. Solution -- The 6-Layer Autowire

The autowire system places every one of the 154 tools onto exactly one of six layers. Each layer fires automatically on a specific trigger; the user types intent, and the layers fan out the work.

| Layer | Name | Trigger | Hook host |
|------:|------|---------|-----------|
| 1 | PreSession (SessionStart) | Once per Claude/Codex/Gemini session | `.claude/settings.json` SessionStart -> `cex_hooks_native.py session-start` |
| 2 | Boot pipeline | Per nucleus boot, before CLI launches | `_tools/cex_boot_pipeline.py --nucleus n0X` |  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
| 3 | PreToolUse | Before Bash / Write / WebFetch | `cex_hooks_native.py pre-tool-use` |
| 4 | PostToolUse | After Write / Edit | `cex_hooks_native.py post-tool-use` |
| 5 | Stop / Cron | Session stop + GitHub Actions schedule | `cex_hooks_native.py stop` + `.github/workflows/cron_*.yml` |
| 6 | Skills auto-fire | LLM-side conditional rules in `.claude/skills/` | Loaded by Claude Code on context match |

The contract: a user types one sentence, and the layers cooperate to deliver a typed, scored, indexed, and signaled artifact -- without that user invoking any tool by name. The full sequence diagram for each of the four boot scenarios lives in doc_autonomous_flow; this card is the layer-by-layer reference.

The wiring is non-coercive. Every layer can be opted out via an environment variable (`CEX_AUTOWIRE=0` disables all of them; the more granular `CEX_AUTOWIRE_POST=0`, `CEX_AUTOWIRE_PRE=0`, `CEX_AUTOWIRE_SKILLS=0`, `CEX_AUTOWIRE_PREFLIGHT=0`, `CEX_AUTOWIRE_CRON=0` toggle individual layers). The default is balanced: layers 1, 4, 5, 6 fire by default; layer 2 (boot pipeline) runs whenever a nucleus is dispatched; layer 3 (PreToolUse) is selective by matcher (Bash, WebFetch, Write).

## 3. Tool Taxonomy by Layer

Every tool referenced in this card sits at exactly one layer. The table below names the highest-leverage members; the full inventory across all 154 tools is in `_docs/TOOLS_INVENTORY.md`.

| Tool | Layer | Trigger | Output |
|------|------:|---------|--------|
| `cex_bootstrap --check` | 1 | SessionStart | exit 0/1 (brand configured?) |
| `cex_intent_resolver --warmup` | 1 | SessionStart | TF-IDF index hot in memory |
| `cex_capability_index --refresh` | 1 | SessionStart | `.cex/runtime/capability_index.json` |
| `cex_template_init` | 1 | SessionStart, when `.cex/brand/.bootstrapped` missing | first-run brand prompts |
| `cex_intent_resolver` | 2 | Boot pipeline step 1 | `{kind, pillar, nucleus, verb, confidence}` |
| `cex_secretariat` | 2 | Boot pipeline step 2 (opt-in) | compressed prior session |
| `cex_preflight_mcp` | 2 | Boot pipeline step 3 (kinds with `requires_external_context`) | external context block |
| `cex_router_v2` | 2 | Boot pipeline step 4 | resolved CLI + model + flags |
| `cex_quota_check` | 3 | Before `Task tool: dispatch grid` | exhausted-provider list |
| `cex_audit_security_brand` | 3 | Before WebFetch | block / allow |
| `cex_validator` | 3 | Before Write to artifact | frontmatter check |
| `cex_council` | 3 | Within-model score >= 9.5 | consensus + divergence + dissent |
| `cex_sanitize` | 4 | After Write/Edit on .py / .ps1 / .sh | non-ASCII stripped |
| `cex_compile` | 4 | After Write/Edit on .md | `.compiled.yaml` twin |
| `cex_score_python` | 4 | After Write/Edit on artifact .md | quality 0-10 |
| `cex_index` | 4 | After Write/Edit on artifact .md | global TF-IDF refresh |
| `cex_wikilink` | 4 | After Write/Edit on artifact .md | related-artifacts table |
| `cex_semantic_lint` | 4 | After Write/Edit on artifact .md | drift warnings |
| `cex_doctor --partial` | 4 | After Write/Edit on `bld_*.md` | builder ISO health |
| `cex_kind_register --validate` | 4 | After Write/Edit on `kinds_meta.json` | registry check |
| `cex_evolve` | 5 | Stop + nightly cron | re-build below-floor artifacts |
| `cex_hygiene scan` | 5 | Weekly cron | R01-R12 drift report |
| `cex_taxonomy_scout` | 5 | Weekly cron | new-kind candidates from arXiv/IETF/W3C |
| `cex_cost_tracker --aggregate-30d` | 5 | Stop + on-demand | per-mission USD rollup |
| `intent_resolution.md` | 6 | Free-form input with kind-noun | calls `cex_intent_resolver` |
| `quota_aware_dispatch.md` | 6 | About to call `Task tool: dispatch grid` | calls `cex_quota_check --all` |
| `council_on_high_score.md` | 6 | Within-model score >= 9.5 | calls `cex_council --auto` |
| `evolve_on_low_quality.md` | 6 | Score < 8.0 detected | suggests `cex_evolve` (no auto-fire) |
| `compress_on_huge_context.md` | 6 | Prompt > 20K tokens | calls `cex_compress` |
| `crew_on_multi_role.md` | 6 | Phrases "team", "crew", "multiple agents" | calls `cex_crew run` |
| `mission_on_multi_artifact.md` | 6 | Plan with >= 3 artifacts | calls `cex_mission_runner` |
| `gdp_on_subjective.md` | 6 | Tone / audience / style decision | invokes `/guide` skill |
| `taxonomy_check_before_new_kind.md` | 6 | "let's create a new kind" | runs 5-question test |
| `preflight_external_context.md` | 6 | Kind has `requires_external_context: true` | calls `cex_preflight_mcp` |
| `bootstrap_on_first_run.md` | 6 | `brand_config.yaml` missing | runs interactive `cex_bootstrap` |
| `consolidate_on_grid_complete.md` | 6 | All wave nuclei signaled | runs `Task tool: dispatch stop` + score apply |

The taxonomy is **hermetic**: any tool added in v1.2.0 or later must declare its layer in its module docstring. If a tool has no layer, it cannot enter the autowire by accident; conversely, if a layer fires a tool, that tool is by contract recorded in this taxonomy.

## 4. Hook Fan-Out -- How One Write Triggers Six Tools

The PostToolUse layer is where a single LLM action becomes six measurable side effects. Consider an artifact landing at `N04_knowledge/P01_knowledge/kc_x.md`:

```
LLM action: Write(path="N04_knowledge/P01_knowledge/kc_x.md", content=...)
                                     |
                                     v
.claude/settings.json PostToolUse[matcher=Write] -> cex_hooks_native.py post-tool-use
                                     |
                                     v  (fan-out by file type / path)
        +-----------+-----------+----+----+-----------+--------------+
        |           |           |        |           |              |
        v           v           v        v           v              v
  cex_sanitize  cex_compile  cex_score_python  cex_index   cex_wikilink   cex_semantic_lint
   (ASCII)      (.md->.yaml)  (quality 0-10)   (TF-IDF)    (related table) (drift check)
        |           |           |        |           |              |
        +-----------+-----------+----+----+-----------+--------------+
                                     |
                                     v
              .cex/runtime/hook_log.jsonl  (one line per tool)
```

Each tool runs with its own timeout; expensive operations (`cex_score_python`, `cex_index`) execute in background where appropriate so the user-perceived latency stays below 200ms. The fan-out is deterministic: re-running the same Write produces the same six log entries. Failures are non-fatal -- the hook host catches each subprocess error, logs it as `exit: nonzero`, and continues with the remaining tools so a single broken tool cannot stall the artifact pipeline.

The dispatch logic inside `cex_hooks_native.py` keys off four signals: file extension (`.py`, `.ps1`, `.sh`, `.md`), pillar prefix (`P01_..` through `P12_..`), filename prefix (`bld_`, `kc_`, `tpl_`, `spec_`), and frontmatter `kind:` field. Different combinations route to different sub-fan-outs; for example, a Write to `archetypes/builders/agent-builder/bld_*.md` triggers `cex_doctor --partial` plus `cex_iso_hydrate --check`, while a Write to `kinds_meta.json` triggers only `cex_kind_register --validate`. This keeps the cost of the fan-out proportional to what the artifact actually needs.

## 5. 8F Mechanical Enforcement

The 8F pipeline gets demoted from "rule" to "mechanism" through three coordinated artifacts. The principle is **measure, do not gate**: the enforcer logs what fired, never blocks publication. Compliance trends become visible; sessions that skip stages are flagged for attention; the LLM is gently nudged via SessionStart context injection on the next session.

### Marker protocol

Every nucleus that runs the 8F pipeline emits stage markers to stdout:

```
=== F1 CONSTRAIN ===
=== F2 BECOME ===
=== F3 INJECT ===
=== F4 REASON ===
=== F5 CALL ===
=== F6 PRODUCE ===
=== F7 GOVERN ===
=== F8 COLLABORATE ===
```

The marker is a literal string the LLM is prompted to output once per stage. It costs ~5 tokens per marker, total ~40 tokens per session -- negligible against the artifact body.

### Enforcer (`cex_8f_enforcer.py`)

The enforcer (~200 lines, runs at `_tools/cex_8f_enforcer.py`) maintains a per-session state file at `.cex/runtime/8f_state/{session_id}.json`. On `--mark F3 --kind agent`, it records that F3 fired for that session/kind. On `--check`, it returns whether all eight markers were observed. On `--report --days 7`, it aggregates compliance % over the last week. Daemon mode (`--watch`) tails session transcripts in real time.

### Compliance log

`.cex/runtime/8f_compliance.log` is a JSONL ledger; each line is one session:

```json
{"ts":"2026-04-27T16:42:18Z","session":"abc123","compliance_pct":100,
 "stages_fired":["F1","F2","F3","F4","F5","F6","F7","F8"],"missing":[]}
```

Target compliance is >= 80% sessions hitting all eight markers. The current baseline (pre-autowire) sits near 30% per the architecture review; the enforcer's first month is expected to show monotonic improvement as the LLM internalizes the marker habit.

### Why log not gate

Gating publication on full-marker compliance would slow legitimate work without proportional benefit -- some tasks genuinely don't need F3 INJECT (a one-line sanitize fix, for example). Logging makes the gap visible, lets the team decide which marker omissions are real anti-patterns, and avoids the false-positive cost of hard blocking. The dispatch-depth principle (dispatch-depth) and the ubiquitous-language rule (`.claude/rules/ubiquitous-language.md`) both follow the same logic: measurement first, enforcement second, only on signals that reliably indicate harm.

## 6. Boot Pipeline -- Eight Phases

The boot pipeline is the layer-2 orchestrator that runs **before** the LLM CLI launches. It replaces hardcoded model strings with a yaml-driven, cache-aware, fallback-tolerant resolution. The implementation lives in `_tools/cex_boot_pipeline.py` and is consumed by every `boot/n0X.ps1` script and the cross-platform `boot/cex_nucleus.sh`.  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->

| Phase | Step | What it does | Skipped when |
|------:|------|--------------|--------------|
| 1 | Resolve-NucleusModel | Read `.cex/config/nucleus_models.yaml` for the target nucleus | never |
| 2 | Intent resolver | `cex_intent_resolver` on the task text -> `{kind, pillar, nucleus, verb, confidence}` | task is empty |
| 3 | Preflight (compress) | `cex_secretariat` reduces context if > 20K tokens | `CEX_AUTOWIRE_PREFLIGHT=0` |
| 4 | Preflight (MCP) | `cex_preflight_mcp` for kinds with `requires_external_context: true` | kind doesn't require it |
| 5 | Router | `cex_router_v2` picks CLI + model + fallback chain via probes + quotas | quota cache fresh |
| 6 | 8F init | Create `.cex/runtime/8f_state/{session_id}.json` and emit F1 marker | session already initialized |
| 7 | Hooks register | Confirm `.claude/settings.json` hook entries are present | not applicable |
| 8 | Agent_card compile + launch | Merge resolved env, launch `claude.exe` (or alternate CLI) with the resolved arguments | dry-run mode |

The pipeline caches its decision at `.cex/cache/boot/{nucleus}.json` with a 5-minute TTL so repeated dispatches do not re-probe quotas. Decisions are also appended to `.cex/runtime/boot_log.jsonl` so the user can audit which model handled which mission. On any error, the pipeline degrades gracefully: it falls back to a direct yaml read and emits a warning rather than blocking the boot.

The pipeline is the answer to Gap 3. Every boot script now starts with:

```powershell
# boot/n07.ps1 (after refactor)
$resolved = python _tools/cex_boot_pipeline.py --nucleus n07 --task $taskPath --json  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
$cli      = $resolved.cli
$model    = $resolved.model
$flags    = $resolved.flags
```

instead of hardcoding `--model claude-opus-4-7`. The same pattern applies to all seven nucleus boot scripts; the diff is a net negative in lines because the boilerplate moves to one orchestrator.

## 7. Cron Workflows -- Periodic Maintenance

Three GitHub Actions workflows give CEX continuous maintenance without a human attending. They live in `.github/workflows/cron_*.yml` and run on the GitHub-hosted clock; locally, the same scripts can be triggered manually with `python _tools/<tool>.py`.

| Workflow | Schedule (UTC) | What it does |
|----------|---------------|--------------|
| `cron_evolve.yml` | Nightly at 03:00 | `cex_evolve sweep --target 8.5 --max-rounds 2` on artifacts updated in the last 24 hours; opens a PR if changes apply |
| `cron_hygiene.yml` | Weekly Mon 12:00 | `cex_hygiene scan --json`; opens an issue if violations exceed threshold |
| `cron_taxonomy.yml` | Weekly Sun 06:00 | `cex_taxonomy_scout` discovers new-kind candidates from arXiv / IETF / W3C; opens a PR with confidence-scored proposals |

Each workflow uses the built-in `GITHUB_TOKEN`, declares minimal permissions (`contents: read`, `issues: write` or `contents: write` + `pull-requests: write` only where required), and times out at 15-60 minutes. The scope is intentionally conservative: workflows emit issues and PRs rather than self-merging, so a human reviews before changes land. The `CEX_AUTOWIRE_CRON=0` env var disables them on PRs without affecting the local clock.

The motivation is compounding work. A repository that depends on someone remembering to run quality sweeps weekly will quietly drift. A repository with cron sweeps cannot drift without leaving a paper trail in the issues tab. The autowire principle holds at all scales: take recurring chores out of human memory, place them in scheduled mechanisms, surface anomalies as work items.

## 8. Cost Tracking -- `cex_cost_tracker`

The README claims a "~70% cost reduction via preflight". That number is a hypothesis until measured. `cex_cost_tracker.py` is the measurement tool.

### Data source

Every call routed through `cex_router_v2` appends one line to `.cex/runtime/cost_log.jsonl`:

```json
{"ts":"2026-04-27T16:42:18Z","session":"abc123","mission":"REFINE_v1.1",
 "nucleus":"n04","provider":"anthropic","model":"claude-opus-4-7",
 "input_tokens":12450,"output_tokens":3120,"usd":0.4671,"preflight_used":true}
```

### Aggregations

The CLI surfaces three views:

```bash
python _tools/cex_cost_tracker.py --session abc123          # one session rollup  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
python _tools/cex_cost_tracker.py --mission REFINE_v1.1     # all sessions in a mission  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
python _tools/cex_cost_tracker.py --aggregate-30d --json    # 30-day cost trend  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
```

The `--aggregate-30d` view groups by `preflight_used` (true/false) and shows the delta in mean USD per artifact. If the preflight branch is consistently >= 60% cheaper than the no-preflight branch on equivalent kinds, the README claim holds. If not, the autowire is failing its cost contract and the boot pipeline needs investigation.

### Why this matters for OSS

The autowire makes the system more capable, but capability without a cost ledger is irresponsible. Users adopting CEX in production need to know: does autowire cost me more (because more tools fire) or less (because preflight compression reduces token spend)? The cost tracker answers that question with measured data, not marketing copy. The output feeds back into the autonomous-tool-wiring spec (`_docs/specs/spec_autonomous_tool_wiring.md`) risk analysis -- if hook fan-out adds non-trivial cost, the spec's "Risk 1" mitigation (20s timeouts, async backgrounding) gets revisited.

## 9. Anti-Sycophancy -- Council Auto-Trigger

The 8F F7 GOVERN stage scores artifacts on five dimensions and assigns a within-model quality 0-10. Single-model scores have a known failure mode: **sycophancy**. An LLM scoring its own output drifts upward; a same-family judge inherits the same blind spots. When the within-model score reports >= 9.5, that signal is suspect.

### Auto-trigger condition

The skill `council_on_high_score.md` (Layer 6) fires when F7 reports a within-model score >= 9.5. The PreToolUse hook in Layer 3 also wires the same trigger so non-Claude runtimes (Codex, Gemini, Ollama) get the council pass without depending on Claude-specific skills.

### `cex_council --auto`

The council runs an instance of the `cross_provider_council` crew_template (per the composable-crew protocol at `.claude/rules/composable-crew.md`). Each judge is a different LLM provider scoring against the same scoring_rubric independently. The output is three numbers:

| Metric | Meaning | Threshold |
|--------|---------|-----------|
| `consensus_score` | Mean of N provider scores | informational |
| `divergence_score` | Stddev of N provider scores | block publish if > 0.3 |
| `dissent_count` | Judges with score >= 1.0 below mean | always surfaced |

Dissenting judges are **never auto-suppressed**. Lone outliers are often the correct dissent -- the model that catches the flaw the others missed. The council's job is to make the disagreement visible and let a human (or a meta-judge) read the rationales.

### Cost guardrail

Each council run costs `N x token_budget` where N is the number of providers (default 3, premium 4). Artifact frontmatter `council_budget_tokens` overrides the default. Without a cap, council runs on every >= 9.5 artifact would dominate the cost-tracker rollup; with the cap and the auto-trigger threshold, they fire only on the artifacts that most need the second opinion.

### Why this completes the autowire

The autowire's purpose is to make CEX trustworthy without supervision. A trust contract that ends at the LLM's self-score is too fragile: the same LLM that wrote the artifact cannot be the only judge of whether it is good. Council fan-out injects cross-provider review at exactly the moment when the within-model signal is least reliable. The autowire then does what only autowires can: it makes the right thing happen by default, without asking the user to remember the council exists. The system measures itself, surfaces dissent, and lets the human decide on real disagreements rather than ceremonial ones.

## What This Replaces

| Before autowire | After autowire |
|-----------------|----------------|
| User memorizes tool names | User types intent |
| 84/154 tools (55%) sit unused | All 154 tools have a layer assignment |
| Boot hardcodes `--model claude-opus-4-7` | Boot pipeline reads `nucleus_models.yaml` |
| 8F is a rule LLMs may skip | 8F is a tracked metric in `.cex/runtime/8f_compliance.log` |
| Quality gate fires sometimes | Fires on every Write/Edit |
| 4 skills auto-fire | 16 skills auto-fire (4 existing + 12 new) |
| Cost is hypothesized | Cost is measured by `cex_cost_tracker --aggregate-30d` |
| Within-model score is the final word | Council fan-out at >= 9.5 surfaces cross-provider dissent |
| Maintenance is manual | 3 cron workflows (evolve / hygiene / taxonomy) |

## Verifying the System

Three commands tell you whether the autowire is healthy:

```bash
# 1. Hook fan-out -- distinct tools called via PostToolUse in last session
python -c "import json; lines=[json.loads(l) for l in open('.cex/runtime/hook_log.jsonl')]; print(sorted(set(l['tool'] for l in lines if l['event']=='post-tool-use')))"

# 2. 8F compliance -- % of sessions hitting all F1-F8 markers
python _tools/cex_8f_enforcer.py --report --days 7 --json

# 3. Cost trend -- 30-day rollup with preflight delta
python _tools/cex_cost_tracker.py --aggregate-30d --json  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
```

If the first command returns fewer than 6 distinct tools, the PostToolUse fan-out is broken. If the second command's compliance % drops below 80%, the marker protocol is being skipped. If the third command's preflight branch is not materially cheaper than the non-preflight branch, the boot pipeline's preflight steps are not delivering. Each finding maps to a specific layer to investigate; the wiring is mechanical, so a missing reflex always traces to a specific hook entry, boot script, or skill file.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| doc_autonomous_flow | sibling | 0.90 |
| 8f-reasoning | upstream | 0.85 |
| n07-orchestrator | sibling | 0.78 |
| guided-decisions | related | 0.55 |
| dispatch-depth | related | 0.48 |
| [[brand_bootstrap]] | related | 0.40 |
| `_docs/specs/spec_autonomous_tool_wiring.md` | upstream (no-id) | 0.95 |
| `_docs/TOOLS_INVENTORY.md` | upstream (no-id) | 0.88 |
| `CLAUDE.md` | upstream (no-id) | 0.75 |
| `.claude/rules/composable-crew.md` | related (no-id) | 0.55 |
| `.claude/rules/ubiquitous-language.md` | related (no-id) | 0.50 |
| showcase_quickstart_guide_cexai | downstream | 0.26 |
| p11_tools_revision_loop_policy | downstream | 0.25 |
| p02_ap_n04_knowledge | downstream | 0.25 |
| bld_tools_terminal_backend | downstream | 0.25 |
| cex_doctor_command | downstream | 0.24 |
| [[bld_tools_personality]] | downstream | 0.23 |
| p01_rm_cex | related | 0.23 |
| [[p05_cg_cex]] | downstream | 0.23 |
