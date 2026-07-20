---
id: kc_agents_md
kind: knowledge_card
8f: F3_inject
title: Agents.md Project-Root Manifest
version: 1.0.0
quality: null
pillar: P01
description: |
  Project-root manifest for AAIF/OpenAI AGENTS.md: setup/test/lint commands, PR format, deploy rules, coding-agent conventions
tldr: "Project-root manifest declaring setup, test, lint commands, PR format, and coding-agent conventions"
when_to_use: "When a repo needs a machine-readable AGENTS.md for coding agents to follow project conventions"
keywords: [npm install, npm test, eslint, prettier, api endpoints, type annotations, error handling, github actions, nixpacks, buildpacks]
density_score: 1.0
related:
  - bld_output_template_agents_md
  - p01_kc_nixpacks_buildpacks
  - p02_qg_agents_md
  - agents-md-builder
  - bld_instruction_agents_md
---

## Setup/Testing/Linting
- `npm install` - Install dependencies
- `npm test` - Run unit tests
- `npm lint` - Lint code with ESLint
- `npm format` - Format code with Prettier

## PR Format
- Title: `[TYPE]: brief description` (e.g., `feat: add agent registry`)
- Description: 
  1. Motivation
  2. Proposed solution
  3. Testing instructions
  4. Related issues

## Deploy Rules
- Staging: `npm run deploy:staging`
- Production: `npm run deploy:production`
- Requires 2 approvals for production deploys

## Coding-Agent Conventions
- Use `// TODO` for pending tasks
- Document API endpoints in `docs/api.md`
- Follow 2-space indentation
- Add type annotations to all functions
- Include error handling for all API calls
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_output_template_agents_md]] | downstream | 0.27 |
| [[p02_qg_agents_md]] | downstream | 0.20 |
| [[agents-md-builder]] | downstream | 0.18 |
| [[bld_instruction_agents_md]] | downstream | 0.18 |
