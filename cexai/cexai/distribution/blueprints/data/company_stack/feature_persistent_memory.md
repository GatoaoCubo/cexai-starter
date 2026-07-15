---
kind: feature_template
feature_name: persistent_memory
vertical: 16_company_stack
round_added: 23
pillars: [P10]
adr_019_packages: [memory/]
feature_dependencies: []
brand_niche_constraints: null
open_vars:
  - name: brand_name
    type: str
    description: "Brand display in memory artifact metadata."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    context_hints: [brand_config.brand_name]
    constraints: {min_length: 1, max_length: 80}
    default_filler_strategy: use_first_context_hint
    required: true
    default_value: null
    rebind_allowed: true
  - name: brand_niche
    type: str
    description: "Drives default memory taxonomy."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    context_hints: [brand_config.brand_niche]
    constraints: {min_length: 1, max_length: 200}
    default_filler_strategy: use_first_context_hint
    required: true
    default_value: null
    rebind_allowed: true
  - name: target_audience
    type: str
    description: "Audience descriptor for memory-driven context injection."
    filler_role: n02
    filler_stage: F3_INJECT
    context_hints: [brand_config.target_audience]
    constraints: {min_length: 3, max_length: 150}
    default_filler_strategy: use_first_context_hint
    required: true
    default_value: null
    rebind_allowed: true
  - name: primary_language
    type: enum
    description: "Primary memory artifact language."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    allowed_values: ["PT-BR", "EN", "ES", "FR", "DE", "IT", "JA", "ZH"]
    context_hints: [brand_config.primary_language]
    constraints: {}
    default_filler_strategy: use_first_context_hint
    required: false
    default_value: "EN"
    rebind_allowed: true
  - name: memory_categories
    type: list[str]
    description: "Categories of persistent memory artifacts (e.g., ['project_status', 'user_preferences', 'integrations', 'gotchas'])."
    filler_role: user
    filler_stage: F4_REASON
    context_hints: [brand_config.memory_categories]
    constraints: {min_items: 1}
    default_filler_strategy: use_default_value
    required: false
    default_value: ["project_status", "user_preferences", "integrations", "gotchas", "references"]
    rebind_allowed: true
  - name: memory_freshness_days
    type: int
    description: "Maximum age (days) before a memory artifact requires re-verification."
    filler_role: n04
    filler_stage: F3_INJECT
    context_hints: [brand_config.memory_freshness_days]
    constraints: {minimum: 1, maximum: 365}
    default_filler_strategy: use_default_value
    required: false
    default_value: 90
    rebind_allowed: true
---

# Feature Template: Persistent Memory

**Purpose**: a structured pattern for persisting CEXAI-deployer-level memory artifacts that survive across sessions. The artifacts capture "what is true about this deployment" so future sessions don't re-discover.

---

## Architecture

```
<deployer_root>/memory/
  MEMORY.md                # index; lists all memory artifacts with one-line hooks
  project_<area>.md        # project memories (current state of an initiative)
  user_<role>.md           # user memories (preferences, knowledge, role)
  feedback_<topic>.md      # feedback memories (corrections + validated approaches)
  reference_<system>.md    # external system pointers (Linear, Slack channels, dashboards)
```

Each memory file follows the pattern from `~/.claude/projects/.../memory/` (the CEX deployer's own).

---

## Memory file frontmatter

```yaml
---
name: <short-kebab-case-slug>
description: <one-line summary>
metadata:
  type: project | user | feedback | reference
  freshness_check_at: <iso_date>
---

<memory body content>
```

The `type` field maps to one of 4 categories. The `freshness_check_at` field tracks when the artifact was last re-verified.

---

## Lifecycle

| Stage | Action |
|-------|--------|
| **Create** | A new fact is learned; CEXAI writes a memory file under the matching category. |
| **Update** | The fact changes (project status advances, system pointer changes); CEXAI edits in place. |
| **Verify** | Periodic check: is this memory still true? Re-verification updates `freshness_check_at`. |
| **Decay** | After `memory_freshness_days` without verification, the memory is marked stale; next session reads with a freshness caveat. |
| **Forget** | A memory is wrong or no longer relevant; CEXAI deletes the file + removes the MEMORY.md entry. |

---

## What to persist (when to write a memory)

- **User** memory: role, preferences, knowledge depth, communication style.
- **Project** memory: current state of an initiative, who's doing what, deadlines, blockers.
- **Feedback** memory: rules the user gave (corrections) + non-obvious approaches that worked.
- **Reference** memory: where to find external information (URLs, dashboards, channels).

## What NOT to persist (memory anti-patterns)

- Code patterns, conventions, architecture, file paths -- these are derivable from current project state.
- Git history, recent commits, who-changed-what -- `git log` / `git blame` are authoritative.
- Debugging fix recipes -- the fix is in the code; the commit message has the context.
- Anything already in CLAUDE.md or the deployer's other long-lived docs.
- Ephemeral task details: in-progress work, current conversation context.

These exclusions apply even when explicitly asked to save -- ask what was SURPRISING or NON-OBVIOUS about it first.

---

## Memory and other persistence forms

- **Memory** vs **Plan**: a plan is for the CURRENT conversation's task; memory is for FUTURE conversations.
- **Memory** vs **Task list**: tasks track in-conversation progress; memory is durable across conversations.
- **Memory** vs **KCs in CEXAI taxonomy**: KCs are GLOBAL CEXAI knowledge (shared across deployers); memory is PER-DEPLOYER.

---

## Integration contracts

- Provides to: any CEXAI nucleus / session that accesses `~/.claude/projects/.../memory/`.
- Provides to: `feature_persistent_memory.md` MEMORY.md index drives auto-load on session start.
- Indexed by: future `cexai discovery` query API (per ADR 022 D-022-03) when memory artifacts become searchable.

---

## Freshness verification

When CEXAI reads a memory artifact whose `freshness_check_at + memory_freshness_days < today`:
1. Surface a freshness caveat to the user ("This memory was last verified 90+ days ago; some facts may be stale.")
2. Optionally trigger an active re-verification (e.g., grep the codebase for the named file path; re-fetch the named URL).
3. After verification, update `freshness_check_at`.

---

## Audit

Memory creates/updates/deletes MAY emit `audit_event` (event_type: `memory_*`). This is OPTIONAL in v1 -- the file system itself is the audit (git log + filesystem stat). v1.5 may formalize.

---

## Out of scope

- Cross-deployer memory federation (memories are per-deployer).
- Semantic search across memory (R24+ via embeddings).
- Memory compression (summarize older memories into condensed summaries) -- deferred.
- Encryption of memory at rest -- deployer concern; recommended for sensitive memories.
