---
kind: output_template
id: bld_output_template_action_paradigm
pillar: P05
llm_function: PRODUCE
purpose: Template with vars for action_paradigm production
quality: null
title: "Output Template Action Paradigm"
version: "1.1.0"
author: n01_polish
tags: [action_paradigm, builder, output_template]
tldr: "Template with vars for action_paradigm production -- includes field guide, constraints, and filled example"
domain: "action_paradigm construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F6_produce"
keywords: [action_paradigm construction, output template action paradigm, and filled example, action_paradigm, builder, output_template, frontmatter template]
density_score: null
related:
  - bld_memory_action_paradigm
  - action-paradigm-builder
---
## Frontmatter Template
```yaml
---
id: p04_act_{{slug}}
kind: action_paradigm
title: "{{title}}"
paradigm_type: {{paradigm_type}}
version: {{version}}
tags: {{tags}}
domain: {{domain}}
quality: null
---
```
## Frontmatter Field Guide
| Field | Type | Constraints | Example Value |
|-------|------|------------|--------------|
| id | string | pattern: p04_act_{slug}, slug = snake_case | p04_act_nav_obstacle_avoidance |
| kind | string | fixed: action_paradigm | action_paradigm |
| title | string | max 80 chars, verb-noun-context | "Reactive Obstacle Avoidance for Mobile Robot" |
| paradigm_type | enum | reactive / deliberative / hybrid / hierarchical | reactive |
| version | semver | major.minor.patch, start at 1.0.0 | 1.0.0 |
| tags | list | >=3 tags, include paradigm_type and domain | [reactive, navigation, robotics] |
---
## Body Sections (All Required)
### Section 1: Paradigm Overview
```markdown
## Paradigm Overview
{{paradigm_type}} paradigm for {{domain}}.
Decision cycle: {{decision_cycle_ms}}ms. Priority model: {{priority_model}}.
{{one_sentence_behavioral_summary}}
```
**Guidance**: State paradigm_type, cycle time in ms, and priority model (priority-order/mutex/round-robin).
Prose max 3 sentences. Do not embed implementation details (those go in steps).
---
### Section 2: State-Action Table (Required, >= 4 rows)
```markdown
## State-Action Table
| State | Precondition | Action | Postcondition | Priority |
|-------|-------------|--------|--------------|----------|
| {{state_1}} | {{precondition_1}} | {{action_1}} | {{postcondition_1}} | {{priority_1}} |
| {{state_2}} | {{precondition_2}} | {{action_2}} | {{postcondition_2}} | {{priority_2}} |
| {{state_3}} | {{precondition_3}} | {{action_3}} | {{postcondition_3}} | {{priority_3}} |
| {{state_4}} | {{precondition_4}} | {{action_4}} | {{postcondition_4}} | {{priority_4}} |
```
**Field constraints for State-Action Table**
| Column | Constraint | Bad Example | Good Example |
|--------|-----------|------------|-------------|
| State | Noun phrase, present tense | "doing navigation" | obstacle_detected |
| Precondition | Boolean-evaluable condition | "when needed" | distance < 0.5m AND sensor_ok=true |
| Action | Verb_noun, no transport verbs | "send POST /move" | execute_avoidance_maneuver |
| Postcondition | State assertion after action | "done" | velocity = 0.0, alert_log.append(event) |
| Priority | Integer 0-9, lower = higher priority | "high" | 0 (safety), 1 (efficiency) |
---
### Section 3: Concurrency Model (Required)
```markdown
## Concurrency Model
Conflict resolution: {{conflict_policy}}.
{{resource_lock_description}}
{{preemption_rules}}
```
**Guidance for concurrency policy options**
| Policy | When to Use | Example Statement |
|--------|------------|-----------------|
| Priority-order | Multiple parallel actions possible | Lower priority number wins; ties go to shorter estimated duration |
| Mutex per resource | Single shared resource | motor_controller locked for duration of any movement action |
| Round-robin | Equal-priority concurrent actions | Actions in same priority tier execute in FIFO submission order |
| Preemptive | Safety-critical interruption | P0 actions interrupt all lower-priority actions immediately |
---
### Section 4: Failure Recovery Table (Required, >= 3 rows)
```markdown
## Failure Recovery
| Failure Mode | Detection Signal | Recovery Action | Timeout | Max Retries |
|-------------|-----------------|----------------|---------|-------------|
| {{failure_1}} | {{detection_1}} | {{recovery_1}} | {{timeout_1}} | {{retries_1}} |
| {{failure_2}} | {{detection_2}} | {{recovery_2}} | {{timeout_2}} | {{retries_2}} |
| {{failure_3}} | {{detection_3}} | {{recovery_3}} | {{timeout_3}} | {{retries_3}} |
```
**Field constraints for Failure Recovery**
| Column | Constraint | Minimum |
|--------|-----------|---------|
| Failure Mode | Named failure, not "error" | 3 distinct failure modes |
| Detection Signal | Observable symptom, measurable | Threshold or event, not "when it breaks" |
| Recovery Action | Named action from state-action table or new action | Must be executable, not "fix it" |
| Timeout | Duration in ms/s before escalation | Always specified; "none" only for immediate recovery |
| Max Retries | Integer or 0 for no retry | 0, 1, or 3; no unbounded retries |
---
### Section 5: Environment Interface (Required)
```markdown
## Environment Interface
| Interface | Type | Direction | Description |
|-----------|------|-----------|-------------|
| {{interface_1}} | {{type_1}} | input/output | {{desc_1}} |
| {{interface_2}} | {{type_2}} | input/output | {{desc_2}} |
| {{interface_3}} | {{type_3}} | input/output | {{desc_3}} |
```
**Guidance**: List all external interfaces the paradigm reads from (inputs) or writes to (outputs).
Do NOT embed transport protocols here -- reference agent_computer_interface artifacts instead.
---

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_memory_action_paradigm]] | downstream | 0.38 |
| [[action-paradigm-builder]] | upstream | 0.33 |
