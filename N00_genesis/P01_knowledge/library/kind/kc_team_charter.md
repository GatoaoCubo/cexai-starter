---
id: kc_team_charter
kind: knowledge_card
8f: F3_inject
title: Team Charter
version: 1.0.0
quality: null
pillar: P01
tldr: "Mission contract defining purpose, deliverables, budget, deadline, and quality gate for a crew"
when_to_use: "When instantiating a composable crew and need to bind mission scope to a crew template"
keywords: [crew template, charter_id, deliverables, success_metrics, quality_gate, escalation_protocol, termination_criteria, kubernetes, docker, cloud foundry, team_charter, mission_statement]
long_tails:
  - "how do I bind a crew template to a concrete mission contract"
  - "how do I set budget deadline and quality gate for a crew"
primary_8f: F8_collaborate
slots:
  CHARTER_ID: "unique charter instance id"
  CREW_TEMPLATE_REF: "crew template instantiated"
  MISSION_STATEMENT: "one-line crew purpose"
  DELIVERABLES: "outputs the crew ships"
  QUALITY_GATE: "minimum deliverable score"
density_score: 1.0
related:
  - team-charter-builder
  - bld_tools_team_charter
  - n00_team_charter_manifest
  - bld_knowledge_card_team_charter
  - bld_collaboration_team_charter
updated: "2026-05-27"
---

# Team Charter

## Description
A team charter is a mission contract that defines the purpose, scope, and operational parameters for a crew instance. It bridges GDP decisions (WHAT) to autonomous execution (HOW) by establishing clear expectations, roles, and success criteria.

## Structure
```yaml
kind: team_charter
pillar: P12
llm_function: COLLABORATE
max_bytes: 4096
naming: p12_team_charter_<NAME>.md + .yaml
core: true
```

## Key Parameters
| Field | Type | Description |
|-------|------|-------------|
| charter_id | string | Unique identifier for this charter instance |
| crew_template_ref | string | Reference to the crew template used as foundation |
| mission_statement | string | Clear, concise definition of the crew's purpose |
| deliverables | array | Specific outputs the crew is expected to produce |
| success_metrics | object | Quantifiable benchmarks for measuring achievement |
| budget | number | Financial resources allocated for the mission |
| deadline | datetime | Final date by which all deliverables must be completed |
| stakeholders | array | Key individuals/organizations with vested interest |
| quality_gate | number | Minimum quality threshold for deliverables |
| escalation_protocol | string | Process for resolving conflicts or issues |
| termination_criteria | string | Conditions under which the charter will end |

## Operational Semantics
- **Discovery**: Resolved via crew template matching
- **Validation**: Requires quality gate verification
- **Rotation**: Automatic charter renewal mechanism
- **Monitoring**: Health checks for deliverable progress

## Cross-Platform Compatibility
| System | Support | Notes |
|--------|--------|-------|
| Kubernetes | ✅ | Crew scheduling integration |
| Docker | ✅ | Containerized crew execution |
| Cloud Foundry | ⚠ | Requires adapter implementation |
| OpenStack | ⚠ | Needs custom scheduler |
| AWS | ✅ | ECS/Fargate support |
| Azure | ✅ | Container Instances integration |

## Security Considerations
- TLS 1.3+ encryption for charter exchange
- Access control via role-based permissions
- Audit logging for charter modifications
- Rate limiting for charter creation

### How to use
```text
Role: you are the COLLABORATE agent at 8F step F8 instantiating a crew.
Load this card to bind a crew_template to one concrete mission contract.
- Set CHARTER_ID and reference the CREW_TEMPLATE_REF you are instantiating.
- Write a one-line MISSION_STATEMENT; list the DELIVERABLES the crew must ship.
- Fix BUDGET, DEADLINE, and the QUALITY_GATE threshold the output must clear.
- Declare ESCALATION_PROTOCOL and TERMINATION_CRITERIA before dispatch.
```

### Procedure
```text
1. Pick the CREW_TEMPLATE_REF the charter instantiates.
2. Assign CHARTER_ID and write the one-line MISSION_STATEMENT.
3. Enumerate DELIVERABLES and SUCCESS_METRICS the crew is accountable for.
4. Bind BUDGET, DEADLINE, and the QUALITY_GATE minimum score.
5. Define ESCALATION_PROTOCOL and TERMINATION_CRITERIA.
6. Hand the charter to the crew runner to begin autonomous execution.
```

### Slots
```text
CHARTER_ID        = <CHARTER_ID>         # unique charter instance id
CREW_TEMPLATE_REF = <CREW_TEMPLATE_REF>  # crew template instantiated
MISSION_STATEMENT = <MISSION_STATEMENT>  # one-line crew purpose
DELIVERABLES      = <DELIVERABLES>       # outputs the crew ships
QUALITY_GATE      = <QUALITY_GATE>       # minimum deliverable score
DEADLINE          = <DEADLINE>           # completion date
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[team-charter-builder]] | downstream | 0.45 |
| [[bld_tools_team_charter]] | downstream | 0.40 |
| n00_team_charter_manifest | sibling | 0.39 |
| [[bld_knowledge_card_team_charter]] | sibling | 0.38 |
| [[bld_collaboration_team_charter]] | downstream | 0.33 |
