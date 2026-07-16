---
id: p05_coc_cex
kind: code_of_conduct
8f: F8_collaborate
pillar: P05
title: "CEX Code of Conduct"
contact_email: "{{BRAND_EMAIL}}"
enforcement_version: "2.1"
scope: "online_and_offline"
response_sla: "48h"
quality: null
version: "1.0.0"
created: "2026-04-19"
updated: "2026-04-19"
keywords: [knowledge gluttony, builders, knowledge cards, nuclei, api keys, credentials, pull request threads]
density_score: 0.85
related:
  - code-of-conduct-builder
when_to_use: "Load when working on CEX Code of Conduct in P05. Consult for how to act on this code_of_conduct."
slots:
  scenario: "<the situation under review>"
  expected_conduct: "<the required behavior>"
---

# Contributor Covenant Code of Conduct

## Our Pledge

We as members, contributors, and leaders of **CEX** pledge to make
participation in our community a harassment-free experience for everyone,
regardless of age, body size, visible or invisible disability, ethnicity, sex
characteristics, gender identity and expression, level of experience, education,
socio-economic status, nationality, personal appearance, race, caste, color,
religion, or sexual identity and orientation.

We pledge to act and interact in ways that contribute to an open, welcoming,
diverse, inclusive, and healthy community.

## Our Standards

Examples of behavior that contributes to a positive environment:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members
- Acknowledging and crediting the contributions of others
- Sharing knowledge generously -- CEX runs on Knowledge Gluttony for good reason

Examples of unacceptable behavior:

- The use of sexualized language or imagery, and sexual attention or advances
- Trolling, insulting or derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information (including API keys, credentials) without explicit permission
- Sustained disruption of community discussions, issues, or pull request threads
- Claiming credit for others' contributions to builders, knowledge cards, or nuclei
- Other conduct which could reasonably be considered inappropriate in a professional setting

## Enforcement Responsibilities

Community leaders are responsible for clarifying and enforcing our standards
and will take appropriate and fair corrective action in response to any behavior
deemed inappropriate, threatening, offensive, or harmful.

Community leaders have the right and responsibility to remove, edit, or reject
comments, commits, code, wiki edits, issues, and other contributions that are
not aligned with this Code of Conduct, and will communicate reasons for moderation
decisions when appropriate.

## Scope

This Code of Conduct applies within all community spaces -- GitHub issues, pull requests,
discussions, the wiki, and any CEX-branded event or channel -- and also applies when
an individual is officially representing the community in public spaces (online and
offline, including conferences and meetups).

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported to the community leaders responsible for enforcement at **{{BRAND_EMAIL}}**.
All complaints will be reviewed and investigated promptly and fairly within **48 hours**.

All community leaders are obligated to respect the privacy and security of the
reporter of any incident.

## Enforcement Guidelines

Community leaders will follow these guidelines in determining the consequence
for any action they deem in violation of this Code of Conduct:

**1. Correction**

Community Impact: Use of inappropriate language or other unprofessional or
unwelcome behavior in the community.

Consequence: A private, written warning from community leaders, providing
clarity around the nature of the violation and an explanation of why the
behavior was inappropriate. A public apology may be requested.

**2. Warning**

Community Impact: A violation through a single incident or series of actions.

Consequence: A warning with consequences for continued behavior. No interaction
with the people involved, including unsolicited interaction with those enforcing
the Code of Conduct, for a specified period of time. This includes avoiding
interactions in community spaces as well as external channels like social media.
Violating these terms may lead to a temporary or permanent ban.

**3. Temporary Ban**

Community Impact: A serious violation of community standards, including
sustained inappropriate behavior.

Consequence: A temporary ban from any form of interaction or public
communication with the community for a specified period of time. No public or
private interaction with the people involved, including unsolicited interaction
with those enforcing the Code of Conduct, is allowed during this period.
Violating these terms may lead to a permanent ban.

**4. Permanent Ban**

Community Impact: Demonstrating a pattern of violation of community
standards, including sustained inappropriate behavior, harassment of an
individual, or aggression toward or disparagement of classes of individuals.

Consequence: A permanent ban from any form of public interaction within
the community.

## Attribution

This Code of Conduct is adapted from the
[Contributor Covenant](https://www.contributor-covenant.org), version 2.1,
available at https://www.contributor-covenant.org/version/2/1/code_of_conduct.html

Community Impact Guidelines were inspired by
[Mozilla's code of conduct enforcement ladder](https://github.com/mozilla/diversity).

For answers to common questions about this code of conduct, see the FAQ at
https://www.contributor-covenant.org/faq. Translations are available at
https://www.contributor-covenant.org/translations.


### How to use

```text
You are the consuming agent that acts on this code_of_conduct under F8 COLLABORATE.
- Resolve the open slots (scenario, expected_conduct) from the caller request.
- Honor every constraint and field contract declared above.
- Emit the result in the shape this code_of_conduct defines; never improvise the schema.
```

### Procedure

```text
1. Load this artifact and read its contract under F8 COLLABORATE.
2. Bind scenario and expected_conduct from the incoming request.
3. Validate the inputs against the constraints declared above.
4. Execute the code_of_conduct behavior; resolve each open slot at act-time.
5. Verify the output shape, then signal completion to the orchestrator.
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_output_template_code_of_conduct | related | 0.76 |
| n00_code_of_conduct_manifest | related | 0.47 |
| p05_qg_code_of_conduct | downstream | 0.43 |
| bld_knowledge_card_code_of_conduct | upstream | 0.37 |
| code-of-conduct-builder | related | 0.34 |
