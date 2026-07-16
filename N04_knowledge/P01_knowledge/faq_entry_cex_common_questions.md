---
id: p01_faq_cex_common_questions
kind: faq_entry
8f: F3_inject
pillar: P01
title: "CEX Common Questions for New Contributors"
version: "1.0.0"
created: "2026-04-19"
updated: "2026-04-19"
author: N04_knowledge
domain: contributor_onboarding
quality: null
tags: [faq, contributor, onboarding, cex, builders]
tldr: "12 real questions new contributors ask about CEX, builders, 8F, nuclei, and quality gates."
question: "What are the most common questions new CEX contributors ask?"
answer: "Answers to 12 questions covering setup, builders, quality, nuclei, and contribution workflow."
category: getting_started
related_topics:
  - contributor_guide_cex
  - quickstart_guide_first_builder
  - CONTRIBUTING.md
keywords: [kind, builder, iso, 8f pipeline, runtime, governance layer, typed knowledge system, quality scoring, fractal]
density_score: 0.96
related:
  - bld_architecture_kind
  - kind-builder
  - bld_schema_kind
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_materialize. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

## CEX Common Questions for New Contributors

---

### Q1: What is CEX and why is it different from a regular AI agent?

Most AI agents are a system prompt plus a few tools. CEX is typed infrastructure for LLM agents:
every piece of knowledge is a **kind**, every kind has a **builder** (12 ISO files), every builder
follows the **8F pipeline**, and eight specialized nuclei collaborate through a governance layer.

Key differences:

| Regular Agent | CEX |
|--------------|-----|
| System prompt + tools | 125 kinds, 119 builders, 1428 ISOs |
| One model | 4 runtimes (Claude, Codex, Gemini, Ollama) |
| Memory = conversation history | 12-pillar typed knowledge system |
| No quality enforcement | 3-layer quality scoring (target 9.0) |
| Bespoke | Self-assimilating, fractal, sovereign |

**Related:** [Quickstart Guide](quickstart_guide_first_builder.md)

---

### Q2: What is a builder, exactly?

A builder is 12 markdown files in `archetypes/builders/{kind}-builder/`. Each file is one ISO
(Instruction Set Object). Together they teach the LLM pipeline one job: how to produce artifacts
of a specific kind (e.g., `knowledge_card`, `agent`, `landing_page`).

The 12 ISOs map to the 8F pipeline functions (verified against
`archetypes/builders/agent-builder/`, disk-identical for every kind):

| ISO | 8F Function |
|-----|------------|
| `bld_model_{kind}.md` | F2 BECOME (identity) |
| `bld_prompt_{kind}.md` | F6 PRODUCE (persona + generation) |
| `bld_knowledge_{kind}.md` | F3 INJECT (domain knowledge) |
| `bld_feedback_{kind}.md` | F7 GOVERN (quality signals) |
| `bld_eval_{kind}.md` | F7 GOVERN (pass/fail criteria) |
| `bld_output_{kind}.md` | F6 PRODUCE (format) |
| `bld_schema_{kind}.md` | F1 CONSTRAIN (input/output schema) |
| `bld_architecture_{kind}.md` | F1 CONSTRAIN (component map) |
| `bld_orchestration_{kind}.md` | F8 COLLABORATE (dependencies) |
| `bld_memory_{kind}.md` | F3b PERSIST (session learning) |
| `bld_config_{kind}.md` | F1 CONSTRAIN (builder config) |
| `bld_tools_{kind}.md` | F5 CALL (available tools) |

---

### Q3: What is the 8F pipeline and do I need to understand it to contribute?

The 8F pipeline is CEX's universal reasoning protocol: F1 CONSTRAIN, F2 BECOME, F3 INJECT,
F4 REASON, F5 CALL, F6 PRODUCE, F7 GOVERN, F8 COLLABORATE. Every artifact passes through all 8.

**For Path 1 (New Builder):** you need to understand which ISO maps to which function (see Q2).
You do not need to implement the pipeline -- it runs automatically when an LLM uses your builder.

**For Path 2 (Knowledge Card):** you only need to know F3 INJECT -- your KC is context.

**For Path 3-4:** read `.claude/rules/8f-reasoning.md` for the full spec.

---

### Q4: What is `quality: null` and why can't I set a score myself?

`quality: null` is a mandatory frontmatter field on all new artifacts. It signals that this
artifact has not been peer-reviewed yet. CEX uses a 3-layer scoring system:

| Layer | Weight | Method |
|-------|--------|--------|
| Structural | 30% | Automated count-based checks |
| Rubric | 30% | Quality gate dimension scoring |
| Semantic | 40% | LLM evaluation (when L1+L2 >= 8.5) |

Only peer review assigns a numeric score. Self-scoring is blocked by convention (and by
the `cex_doctor.py` check in CI). If you set `quality: 9.5` yourself, the PR will fail review.

---

### Q5: What does `cex_doctor.py` check?

`cex_doctor.py` runs 118+ checks across all builders and artifacts:

| Check category | What it validates |
|---------------|-------------------|
| Frontmatter | Required fields present (id, kind, pillar, quality, version) |
| ISO completeness | All 12 files exist in every builder directory |
| Density | Body has sufficient structured content (tables, bullets) |
| Naming | snake_case filenames, ASCII only, <= 50 chars |
| Non-ASCII in code | `.py`, `.ps1`, `.sh` files are byte-clean |
| Compilation | `.md` artifacts compile to `.yaml` without errors |

Run it before every commit: `python _tools/cex_doctor.py`

---

### Q6: What is a "kind" and how many are there?

A kind is an atomic artifact type in the CEX taxonomy. Think of it as a class in OOP:
a kind defines the schema, pillar, and quality criteria for a category of artifacts.

- 125 kinds are registered in `.cex/kinds_meta.json` in this starter (verify live:
  `python -c "import json;print(len(json.load(open('.cex/kinds_meta.json'))))"`)
- 119 builders exist (1 builder per kind for most; a few kinds share variants)
- Kinds are grouped into 12 pillars (P01-P12)

Examples by pillar:

| Pillar | Example kinds |
|--------|--------------|
| P01 Knowledge | `knowledge_card`, `glossary_entry`, `citation` |
| P02 Model | `agent`, `model_provider`, `nucleus_def` |
| P03 Prompt | `prompt_template`, `system_prompt`, `chain` |
| P05 Output | `landing_page`, `contributor_guide`, `quickstart_guide` |
| P12 Orchestration | `workflow`, `schedule`, `dispatch_rule` |

---

### Q7: What is a nucleus and which one should I contribute to?

A nucleus is a domain-specialized LLM agent (N00-N07). Each has 13 subdirectories mirroring
the 12 pillars, and runs on a "sin lens" that drives its optimization bias.

| Nucleus | Domain | Sin Lens |
|---------|--------|----------|
| N01 | Intelligence / Research | Analytical Envy |
| N02 | Marketing / Copy | Creative Lust |
| N03 | Engineering / Build | Inventive Pride |
| N04 | Knowledge / Docs | Knowledge Gluttony |
| N05 | Operations / Code | Gating Wrath |
| N06 | Commercial / Revenue | Strategic Greed |
| N07 | Orchestration | Orchestrating Sloth |

**For most contributors:** place knowledge cards in `N00_genesis/P01_knowledge/library/` (shared).
Place nucleus-specific artifacts in the relevant `N0X_domain/P{XX}_*/` directory.

---

### Q8: How do I know which pillar to put my artifact in?

Match the artifact's primary function to the pillar domain:

| Your artifact is about... | Pillar |
|--------------------------|--------|
| Domain knowledge, RAG context, definitions | P01 Knowledge |
| Agent identities, model providers, personas | P02 Model |
| Prompts, templates, chains, instructions | P03 Prompt |
| External tools, APIs, browsers, MCP servers | P04 Tools |
| User-facing output (docs, pages, reports) | P05 Output |
| Schemas, data contracts, type definitions | P06 Schema |
| Evals, benchmarks, scoring rubrics | P07 Evaluation |
| Architecture diagrams, decision records | P08 Architecture |
| Config, env vars, secrets, feature flags | P09 Config |
| Memory, indexes, caches, session state | P10 Memory |
| Feedback, quality gates, bugloops | P11 Feedback |
| Workflows, dispatch rules, schedules | P12 Orchestration |

Check the pillar schema for exact field requirements: `N00_genesis/P{XX}_*/_schema.yaml`

---

### Q9: Can I contribute documentation in Portuguese?

- **Code files** (`.py`, `.ps1`, `.sh`, `.bat`): ASCII only. No Portuguese, no accents, no emoji.
- **Markdown artifacts** (`.md`): English only for any file intended for the shared library or public-facing docs. Portuguese is acceptable only in nucleus-internal notes that are never surfaced to external contributors.
- **Commit messages and PR titles**: English only.

The ASCII-only rule is enforced by a pre-commit hook. Violations are caught at commit time.
See `.claude/rules/ascii-code-rule.md` for the full replacement table.

---

### Q10: My PR has been open for 2 weeks with no review. What do I do?

1. Check that `cex_doctor.py` passes in CI (the green check must be present)
2. Comment on the PR with `@maintainers ready for review` to ping the team
3. Post in GitHub Discussions with a link to the PR
4. SLA: maintainers aim for first review within 5 business days of a passing CI run

If CI is failing, fix it first -- PRs with failing CI are not reviewed.

---

### Q11: What is the difference between a builder and a sub-agent?

| Concept | Location | Purpose |
|---------|----------|---------|
| Builder | `archetypes/builders/{kind}-builder/` | 12 ISOs that teach LLM how to produce a kind |
| Sub-agent | `.claude/agents/{kind}-builder.md` | Compiled agent definition for Claude Code |

Sub-agents are auto-generated from builders via `python _tools/cex_materialize.py`.  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
You write the builder; the system generates the sub-agent. Do not edit sub-agents manually.

---

### Q12: How do I run a single builder to test it locally?

```bash
# Dry-run: see what the builder would produce (no file written)
python _tools/cex_8f_runner.py --kind {kind} --dry-run

# Execute: produce the artifact
python _tools/cex_8f_runner.py --kind {kind} --nucleus n04 --intent "test artifact"

# Score the result
python _tools/cex_score.py {output_file_path}
```

If `cex_8f_runner.py` is not available, you can invoke the builder manually by loading its
ISOs and running the 8F pipeline as described in `.claude/rules/8f-reasoning.md`.

---

**Related:** [Quickstart Guide](quickstart_guide_first_builder.md) | [Contributor Guide](contributor_guide_cex.md)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p06_td_cex_artifact_type_n03 | downstream | 0.44 |
| bld_architecture_kind | downstream | 0.42 |
| kind-builder | downstream | 0.40 |
| bld_schema_kind | downstream | 0.36 |
| bld_instruction_kind | downstream | 0.36 |
