---
id: p03_rs_investigate_first
kind: reasoning_strategy
8f: F4_reason
pillar: P03
title: "Reasoning Strategy: Investigate-First / 3-Strike Debugging"
version: "1.0.0"
created: "2026-07-20"
updated: "2026-07-20"
author: n05_operations
domain: "root-cause debugging discipline"
quality: null
reasoning_type: abductive
strategy_depth: 4
source_attribution: "Methodology assimilated from gstack (garrytan/gstack, MIT, commit 14fc0866d9) -- adapted to CEX taxonomy."
when_to_use: "Before ANY fix to a failing build, test, gate, or deploy. Gate the bugloop FIX phase: no fix is queued until this protocol confirms a root cause. Consult for 'am I allowed to apply this fix yet, and when do I stop trying?'"
primary_8f: REASON
density_score: 0.92
tags: [reasoning-strategy, debugging, root-cause, iron-law, anti-thrash, 3-strike, bugloop-gate, N05, P03]
tldr: "The Iron Law of debugging: no fix without investigation. Reproduce -> trace data flow -> hypothesize -> test -> confirm root cause -> only then fix. STOP and escalate after 3 failed fixes on one hypothesis -- never thrash."
keywords: [iron law, root cause, data flow trace, hypothesis test, three strike stop, escalate not thrash, abductive inference, fix gate, bugloop entry gate, anti-thrash]
related:
  - kc_reasoning_strategy
  - bld_schema_bugloop
  - reasoning-strategy-builder
  - nucleus_def_n05
---

# Reasoning Strategy: Investigate-First / 3-Strike Debugging

## The Iron Law

**No fix without investigation.** A fix applied before the root cause is confirmed is a
guess; a guess that merely silences a symptom is worse than no fix -- it hides the defect
and burns a cycle. Debugging is **abductive reasoning**: from symptoms, infer the *best
explanation*, then test it. The fix is the LAST step, never the first.

N05's Gating Wrath applies inward here: the Iron Law is itself a gate. It does not
negotiate. Until the protocol below confirms a root cause, the fix is BLOCKED.

> Assimilation note: the investigate-first discipline and the 3-strike stop rule are
> methodology lifted from gstack's `/investigate` (garrytan/gstack, MIT, commit
> 14fc0866d9). No gstack source is vendored; the idea is re-expressed over CEX's own
> `bugloop` gate (kind: `bugloop`, pillar P11) and general anti-shortcut discipline.

## The Investigation Protocol (ordered -- no skipping)

| # | Step | Question answered | Exit condition |
|---|------|-------------------|----------------|
| 1 | Reproduce | Does the failure happen on demand? | A deterministic command that re-triggers it |
| 2 | Trace data flow | Where does the bad value enter and travel? | The input -> transform -> output path is named |
| 3 | Hypothesize | What is the single most likely cause? | ONE falsifiable root-cause claim |
| 4 | Test the hypothesis | Is the claim true? | A check that would FALSIFY it if wrong |
| 5 | Confirm root cause | Did the test confirm, not just correlate? | Cause -> effect link is proven, not assumed |
| 6 | Fix | Only now: change the confirmed cause | Re-run step 1; the reproduction is gone |

Steps 1-5 are investigation. Step 6 is the only step that mutates code. A symptom with
two plausible causes is NOT confirmed -- return to step 3 and disambiguate before fixing.

## The 3-Strike Stop Rule (anti-thrash)

A fix attempt FAILS when step 6's re-run still reproduces the failure. Count failures
**per root-cause hypothesis**:

- **Strike 1-2:** the hypothesis may be right with a wrong fix. Refine the fix, retry.
- **Strike 3:** the hypothesis is wrong. **STOP.** Do not attempt a 4th fix on it.
  Escalate: record the reproduction, the trace, all 3 attempts, and why each failed.

Thrashing -- fix after fix with no new hypothesis -- is forbidden. Three strikes means the
*investigation* was incomplete: escalation returns to step 3 or to a human, never a blind
4th attempt.

## Composition

### Gates the bugloop pattern
This strategy is the DISCIPLINE; the bugloop is the AUTOMATION. A `bugloop` (kind:
`bugloop`, pillar P11 -- N05's own automated fix loop) may queue a fix only after steps
1-5 confirm a root cause -- investigate before loop. The 3-strike STOP maps onto a
bugloop's `max_attempts: 3` + `escalation_target`: strike 3 is the escalation trigger, not
a silent retry.

### Enforces anti-shortcut discipline
Investigate-first is the anti-shortcut for the debugging path -- reason through the full
cause BEFORE producing the fix, and escalate rather than thrashing toward a hasty,
possibly irreversible bad fix (force-push, migration). See `.claude/rules/8f-reasoning.md`
for the wider 8F reasoning protocol this strategy plugs into at F4 REASON.

## Worked Example

Symptom: after a build batch, `cex_doctor.py` flags a builder FAIL on density.

| Step | Action | Finding |
|------|--------|---------|
| 1 Reproduce | `python _tools/cex_doctor.py --file <artifact>` | FAIL reproduces deterministically |
| 2 Trace | Where does density come from? doctor reads the `density_score` frontmatter field | The value flows from frontmatter, NOT recomputed from body |
| 3 Hypothesize | Field is absent -> doctor defaults density to 0 (vs. content genuinely sparse) | ONE claim: missing field, not sparse content |
| 4 Test | `grep '^density_score:' <artifact>` | No match -- field absent |
| 5 Confirm | Absent field => default 0 => FAIL. Cause proven | Root cause: missing field |
| 6 Fix | Add `density_score: 0.90`; re-run step 1 | FAIL gone |

The thrash path (banned) -- "rewrite it denser" -- spends a full production pass on the
wrong cause while the FAIL persists. Investigation split two causes sharing one symptom;
the cheap fix was right only *because* it was confirmed.

## Anti-Patterns (Blocked)

| Anti-pattern | Why blocked |
|--------------|-------------|
| Fix before reproduce | Cannot verify the fix worked; symptom may be intermittent |
| "Obvious" fix, no trace | The obvious cause and the real cause share symptoms (see example) |
| Two live hypotheses, one fix | Fixing an unconfirmed cause hides the real one |
| 4th attempt after 3 strikes | Thrashing; the investigation, not the fix, is the gap |
| Silence the symptom (try/except, skip test) | Defect persists under a green light -- worse than visible |

## Validation Criteria

- A confirmed root cause (steps 1-5) is in the trace BEFORE any step-6 mutation, and every
  fix re-runs the step-1 reproduction.
- No more than 3 fix attempts per hypothesis; strike 3 produces an escalation record.
- The trace is auditable: reproduction command, data-flow path, hypothesis, falsifying test.

## References

- Methodology source: gstack `/investigate` (garrytan/gstack, MIT, commit 14fc0866d9).
- CEX 8F reasoning protocol (F4 REASON): `.claude/rules/8f-reasoning.md`.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_reasoning_strategy]] | upstream | 0.35 |
| [[bld_schema_bugloop]] | related | 0.32 |
| [[reasoning-strategy-builder]] | upstream | 0.30 |
| [[nucleus_def_n05]] | upstream | 0.24 |
