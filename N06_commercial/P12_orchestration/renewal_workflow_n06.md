---
id: renewal_workflow_n06
kind: renewal_workflow
pillar: P12
nucleus: n06
title: "Renewal Workflow -- Automated Renewal and Retention Orchestration"
version: 1.0.0
quality: null
tags:
  - "renewal"
  - "workflow"
  - "retention"
  - "orchestration"
  - "commercial"
  - "automated"
density_score: 1.0
related:
  - subscription_tier_n06
  - p12_ct_pricing_sprint
updated: "2026-07-20"
---

# Renewal Workflow: Automated Renewal and Retention Orchestration

## Purpose

Automates the full renewal lifecycle: from early signal detection through
close or win-back. Renewals are NOT passive events -- they are actively
managed revenue moments with defined trigger sequences, escalation
protocols, and success criteria.

## Workflow Architecture

```
DETECT: renewal_date - 30 days
    |
    v
ASSESS: pull customer entity -> health_score, churn_risk, expansion_potential
    |
    +-- health >= 70, risk low -> STANDARD track
    |
    +-- health 40-70, risk medium -> ENGAGEMENT track
    |
    +-- health < 40, risk high -> SAVE track
    |
    v
EXECUTE track-specific sequence
    |
    v
MEASURE outcome: renewed | upgraded | downgraded | churned
    |
    v
UPDATE entity + signal + log
```

## Track: STANDARD (health >= 70, risk: low)

```
Day -30: Renewal value email
  Subject: "Your [tier] renewal is coming up -- here's what you've built"
  Content: usage recap + value delivered + annual-upgrade offer
  CTA: [Renew annual] | [Keep monthly]

Day -7: Renewal reminder
  Subject: "Your renewal is in 7 days"
  Content: brief reminder + annual offer still available
  CTA: [Manage subscription]

Day 0: Auto-charge (no action if payment succeeds)

Day +1: Success confirmation
  Subject: "You're all set for another [period]"
  Content: what's coming next for the account
```

## Track: ENGAGEMENT (health 40-70, risk: medium)

```
Day -30: Personalized reactivation email
  Subject: "We noticed you haven't used [underutilized feature]"
  Content: specific usage gap + tutorial or quick-win for that feature
  CTA: [Book 15-min session] | [Watch tutorial]

Day -14: CSM review
  Action: CSM reviews entity, decides: book a call / let renew untouched / proactive outreach

Day -7: Save offer (if engagement gap unresolved)
  Subject: "We want to make sure this is working for you"
  Content: acknowledge possible under-usage + a paid-value session offered free
  CTA: [Book session + claim credit]

Day -3: Final renewal reminder + feature highlight
Day 0: Auto-renewal

Day +1-7: Activation check -- monitor usage for 14 days; no improvement escalates to SAVE track next cycle
```

## Track: SAVE (health < 40, risk: high)

```
Day -30: CSM priority assignment within 24h of detection
  CSM brief: full entity dump (health, churn signals, usage history) + recommended save offer

Day -21: CSM outreach call
  Script: "We noticed your usage has changed -- are we still solving the right problem for you?"
  Listen for: project ended | team change | budget cut | competitor switch
  Respond with: the matching save play from the churn-prevention playbook

Day -14: Save offer deployed, based on stated reason:
  - Budget: annual discount + bonus free period
  - Project ended: pause option (reduced rate)
  - Missing feature: roadmap commitment + free upgrade if feature lands
  - Competitor: competitive objection handling

Day -7: Follow-up if offer not accepted
  Options: escalate to exec sponsor | downgrade to lower tier (preserve revenue) | accept churn gracefully + set win-back sequence

Day 0: Outcome logged
```

## Outcome Measurement

```yaml
renewal_outcomes:
  renewed_same_tier:
    outcome: base
    nrr_impact: 100% (neutral)
    follow_up: annual upgrade offer at day 60

  renewed_upgraded:
    outcome: expansion
    nrr_impact: ">100% (positive)"
    follow_up: activation check for new tier features

  renewed_downgraded:
    outcome: contraction
    nrr_impact: "<100% (negative, better than churn)"
    follow_up: engagement track for next renewal

  churned:
    outcome: lost
    nrr_impact: "0% (fully negative)"
    follow_up: win-back sequence at 30, 60, 90 days
```

## Win-Back Sequence (Post-Churn)

```
Day 30 post-churn: "here's what's new since you left" (no direct sales push)
Day 60: special reactivation offer, time-limited
Day 90: final win-back, reactivate at prior tier pricing
Day 180: archive + remove from active sequences
```

## Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| Gross revenue retention | (MRR_renewed) / (MRR_up_for_renewal) | >90% |
| Net revenue retention | (renewed + expansion - contraction) / MRR_up | >110% |
| Renewal rate | accounts_renewed / accounts_up | >85% |
| Save rate | accounts_saved / save_attempts | >40% |
| Win-back rate | accounts_reactivated / churned | >10% |

## Related Artifacts
| Artifact | Relationship |
|----------|-------------|
| [[subscription_tier_n06]] | upstream (renewal tracks reference the tier a customer sits on) |
| [[p12_ct_pricing_sprint]] | related (sibling revenue-motion crew) |
