---
kind: knowledge_card
id: bld_knowledge_card_action_prompt
pillar: P01
llm_function: INJECT
purpose: Domain knowledge for action_prompt production
sources: OpenAI Chat API, Anthropic prompt guide, DSPy signatures, LangChain templates
quality: null
title: "Knowledge Card Action Prompt"
version: "1.0.0"
author: n03_builder
tags: [action_prompt, builder, examples]
tldr: "Golden and anti-examples for action prompt construction, demonstrating ideal structure and common pitfalls."
domain: "action prompt construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F3_inject"
keywords: [action prompt construction, knowledge card action prompt, action_prompt, builder, examples, domain knowledge, executive summary
action, anthropic human, py signatures, spec table]
density_score: 0.90
related:
  - action-prompt-builder
  - p01_kc_action_prompt
  - bld_instruction_action_prompt
  - bld_collaboration_action_prompt
  - bld_architecture_action_prompt
---
# Domain Knowledge: action_prompt
## Executive Summary
Action prompts are task-focused messages injected at runtime that specify WHAT an LLM should do with defined input and WHAT output to produce. They function as typed function calls: input contract in, structured result out. The concept maps to OpenAI user messages, Anthropic Human turns, and DSPy Signatures.
## Spec Table
| Property | Value |
|----------|-------|
| Pillar | P03 (prompts) |
| llm_function | BECOME (builder identity) |
| Core pattern | Verb-first task + typed I/O + validation criteria |
| Max steps | 3-7 (concise task, not detailed runbook) |
| Required sections | purpose, input_required, output_expected, edge_cases |
| Frontmatter fields | 21 |
| Quality gates | 8 HARD + 12 SOFT |
## Patterns
- **Verb-first framing**: "Extract metrics from log" not "Log metric extraction" — imperative voice activates task execution
- **Typed I/O contracts**: specify data types explicitly (list[string], JSON object) rather than vague descriptions
- **Structured output definition**: define format (JSON, table, markdown) with concrete example showing expected shape
- **Edge case enumeration**: minimum 2 known failure modes with handling guidance per action prompt
- **Validation criteria**: verifiable checks ("output contains >= 3 rows") not subjective ("output is good")
- **Purpose linkage**: every action_prompt states WHY it exists, connecting task to business reason
- **No identity mixing**: action_prompt assumes the agent already has identity from system_prompt
## Anti-Patterns
| Anti-Pattern | Why it fails |
|-------------|-------------|
| Vague input ("some data") | LLM guesses types; outputs are unpredictable |
| Missing output format | Every run produces different structure |
| Subjective validation ("good quality") | Cannot be automatically verified |
| Identity instructions in action_prompt | Conflicts with system_prompt; role confusion |
| 10+ execution steps | That is an instruction (recipe), not an action prompt |
| No edge cases listed | First unusual input causes hallucination |
## Application
1. Start with the verb: what action does the LLM perform?
2. Define input_required with explicit types and examples
3. Define output_expected with format and concrete example
4. List 2+ edge cases with handling strategies
5. Add validation criteria that a script could verify
6. Confirm: is this a single task (action_prompt) or a multi-step recipe (instruction)?
## References
- OpenAI: Chat Completions API — user message best forctices
- Anthropic: Prompt engineering guide — Human turn design
- DSPy: Signatures — typed input/output contracts for LLM calls
- Zamfirescu-Pereira et al. 2023: "Why Johnny Can't Prompt"

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[action-prompt-builder]] | downstream | 0.49 |
| [[kc_action_prompt]] | sibling | 0.40 |
| [[bld_prompt_action_prompt]] | downstream | 0.38 |
| [[bld_orchestration_action_prompt]] | downstream | 0.37 |
| [[bld_architecture_action_prompt]] | downstream | 0.34 |
