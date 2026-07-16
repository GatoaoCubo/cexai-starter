# N04 Knowledge / P03 Prompt

Prompt templates, system prompts, and the reasoning chains that drive this nucleus's LLM calls.

## Example kinds (in P03, this checkout)
- `action_prompt` -- Task prompt sent by human/orchestrator to the agent
- `chain` -- Chained prompt sequence (output A -> input B)
- `churn_prevention_playbook` -- Churn prevention playbook: signal detection, intervention triggers, save-the-account scripts

## Schema
See [N00_genesis/P03_prompt/_schema.yaml](../../N00_genesis/P03_prompt/_schema.yaml) for this pillar's field contract.

---
This pillar is empty by design -- it fills the first time one of your builds writes here. See [HOME -> Anatomy](../../HOME.md#anatomy-why-nuclei-look-incomplete).
