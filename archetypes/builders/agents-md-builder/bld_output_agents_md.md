---
kind: output_template
id: bld_output_template_agents_md
pillar: P05
llm_function: PRODUCE
purpose: Template with vars for agents_md production
quality: null
title: "Output Template Agents Md"
version: "1.0.0"
author: wave7_n03_dev_manifests
tags:
  - "agents_md"
  - "builder"
  - "output_template"
tldr: "Template with vars for AGENTS.md production"
domain: "agents_md construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords:
  - "agents_md construction"
  - "output template agents md"
  - "md production"
  - "agents_md"
  - "builder"
  - "output_template"
  - "## test commands"
  - "## lint commands"
  - "conventional commits"
  - "related artifacts"
density_score: 0.85
related:
  - bld_schema_agents_md
  - agents-md-builder
---
```markdown
---
id: p02_am_{{name}}.md
kind: agents_md
pillar: P05
project_root: {{project_root}}      <!-- repo absolute path -->
primary_stack: {{primary_stack}}    <!-- 'node' | 'python' | 'rust' | 'go' -->
quality: null
---

# AGENTS.md -- {{project_name}}

{{one_paragraph_repo_summary}}

## Setup commands
```bash
`{{setup_command}}`                   <!-- e.g., npm install  /  pip install -e . -->
```

## Test commands
```bash
`{{test_command}}`                    <!-- e.g., npm test  /  pytest -q -->
```

## Lint commands
```bash
`{{lint_command}}`                    <!-- e.g., npm run lint  /  ruff check . -->
```

## PR format
- Commit grammar: {{commit_grammar}}   <!-- e.g., Conventional Commits -->
- Branch prefix: {{branch_prefix}}     <!-- e.g., feat/, fix/, chore/ -->
- Review: {{review_rule}}              <!-- e.g., 1 approval + CI green -->

## Deploy rules
- Approver: {{deploy_approver}}
- Rollback: {{rollback_command}}

## Security rules
- NEVER force-push to {{protected_branch}}
- NEVER delete protected branches
- NEVER rewrite published history
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p02_qg_agents_md]] | downstream | 0.37 |
| [[kc_agents_md]] | upstream | 0.34 |
| [[bld_instruction_agents_md]] | upstream | 0.31 |
| [[bld_schema_agents_md]] | downstream | 0.29 |
| [[agents-md-builder]] | related | 0.25 |
