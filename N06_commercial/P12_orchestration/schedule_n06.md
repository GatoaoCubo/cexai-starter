---
id: schedule_n06
kind: schedule
pillar: P12
nucleus: n06
title: "Schedule N06: Sales Cadence (Follow-up / Renewal / QBR)"
version: 1.0.0
quality: null
tags: [n06, commercial, schedule, cadence, renewal, qbr, follow_up]
tldr: "N06 sales cadence schedules: outbound follow-up sequences, renewal windows, and QBR timing -- all ROI-justified"
density_score: 0.9
related:
  - nucleus_def_n06
  - renewal_workflow_n06
  - p11_cm_content_monetization_n06
updated: "2026-07-20"
---

# Schedule N06: Sales Cadence

## Cadence Registry

| Cadence | Type | Frequency | Revenue Impact (industry pattern) | Cost Model |
|---------|------|-----------|------------------------------------|------------|
| outbound_followup | lead nurture | Day 1/3/7/14/21/30 | higher reply rate vs. no sequence | $0 marginal (rep time) |
| renewal_window | retention | 90d/60d/30d before expiry | lower churn vs. no proactive renewal | rep time + discount budget |
| qbr | expansion | Quarterly | expansion MRR lift per account | rep time per account |

The percentages cited below (SalesLoft 2024, etc.) are external industry
citations, not a promise of your own results -- replace with your own
measured deltas once you have cadence-level data.

---

## Cadence 1: Outbound Follow-up Sequence

**Purpose**: Multi-touch lead nurture from first contact to meeting booked. No single-touch abandonment.

**Revenue Impact**: 6-touch sequences yield meaningfully higher reply rate and more meetings vs. 1-touch (SalesLoft 2024).
**Conversion Target**: `{{REPLY_RATE_TARGET}}` reply rate, `{{MEETING_BOOKED_RATE_TARGET}}` meeting-booked rate per sequence launched.
**Cost Model**: Rep time only -- no paid media; amortized over pipeline value.

### Schedule Definition
```yaml
id: "cadence_outbound_followup_n06"
name: "Outbound Follow-up Sequence"
type: event_triggered
trigger: new_lead_assigned OR sql_created
timezone: "{{TIMEZONE}}"
enabled: true
```

### Touch Schedule
| Day | Channel | Message Type | Goal |
|-----|---------|--------------|------|
| 0 | Email | Value intro -- pain hypothesis | Open rate above your baseline |
| 1 | LinkedIn | Connection request + brief | Connect rate above your baseline |
| 3 | Email | Case study -- same segment | Reply rate above your baseline |
| 7 | Phone | Direct call -- decision maker | Connect rate above your baseline |
| 14 | Email | ROI calculator attached | Reply rate above your baseline |
| 21 | LinkedIn | Comment on their content | Warm signal |
| 30 | Email | Break-up / final value offer | Reply or disqualify |

### Task Configuration (planned, not implemented)
```yaml
task:
  command: "python _tools/cex_cadence_runner.py --cadence outbound_followup"
  working_dir: "N06_commercial/"
  timeout_s: 120
  env:
    CEX_NUCLEUS: "n06"
  on_success: log_crm_activity
  on_failure: alert_rep
```

---

## Cadence 2: Renewal Window

**Purpose**: Proactive renewal outreach to prevent churn and lock multi-period commitments before expiry.

**Revenue Impact**: Proactive renewal outreach at 90d tends to reduce churn; multi-year commit offers at 60d tend to see a meaningful take rate.
**Conversion Target**: `{{RENEWAL_RATE_TARGET}}` renewal rate; `{{UPGRADE_AT_RENEWAL_TARGET}}` upgrade-at-renewal rate; `{{MULTIYEAR_LOCK_TARGET}}` multi-year lock rate.
**Cost Model**: Discount budget capped per your own margin floor; ROI positive above your retention-period threshold.

### Schedule Definition
```yaml
id: "cadence_renewal_window_n06"
name: "Renewal Window Sequence"
type: date_relative
reference: contract_expiry_date
timezone: "{{TIMEZONE}}"
enabled: true
```

### Renewal Touch Schedule
| Days to Expiry | Action | Owner | Goal |
|----------------|--------|-------|------|
| -90 | QBR + renewal preview | CSM | Health score check; flag at-risk |
| -60 | Renewal proposal sent | AE | Lock pricing; present multi-year option |
| -45 | Follow-up: legal/finance loop | AE | Paper process started |
| -30 | Executive sponsor call | AE + CSM | Remove blockers; confirm intent |
| -14 | Final terms sent | AE | Signature in this window |
| -7 | Urgent: deadline communication | AE | Close or escalate |
| -1 | Last call / escalation | AE + Manager | Auto-renewal or deal save |
| +1 | Post-close: kickoff or offboard | CSM | Ensure transition is clean |

### Task Configuration (planned, not implemented)
```yaml
task:
  command: "python _tools/cex_renewal_monitor.py --days-ahead 90"
  cron: "0 8 * * 1"  # Every Monday 8AM
  working_dir: "N06_commercial/"
  timeout_s: 300
  env:
    CEX_NUCLEUS: "n06"
  on_success: update_renewal_dashboard
  on_failure: alert_revenue_ops
```

---

## Cadence 3: Quarterly Business Review (QBR)

**Purpose**: Structured account review to demonstrate ROI, uncover expansion opportunities, and reinforce retention.

**Revenue Impact**: Accounts with regular QBRs tend to show higher expansion MRR and lower churn vs. reactive support-only accounts.
**Conversion Target**: `{{QBR_ACCEPTANCE_TARGET}}` QBR acceptance rate; `{{QBR_EXPANSION_TARGET}}` of QBRs generate an expansion opportunity.
**Cost Model**: Rep/CSM time per account; prioritize the top ARR band (usually covers most of the expansion opportunity).

### Schedule Definition
```yaml
id: "cadence_qbr_n06"
name: "Quarterly Business Review"
cron: "0 9 1 1,4,7,10 *"  # 1st of Jan/Apr/Jul/Oct at 9AM
timezone: "{{TIMEZONE}}"
enabled: true
```

### QBR Agenda Template
| Section | Duration | Owner | Revenue Signal |
|---------|----------|-------|---------------|
| ROI recap (last quarter) | 10m | CSM | Justify renewal; anchor expansion |
| Usage analytics | 10m | CSM | High usage = upgrade trigger |
| Business goals (next quarter) | 15m | Customer | Uncover new pain = new deal |
| Product roadmap preview | 10m | AE | Land expansion seeds |
| Expansion proposal (if fit) | 10m | AE | Present if usage/goals indicate fit |
| Action items + next QBR date | 5m | CSM | Lock next touchpoint |

### Monitoring
- **QBR acceptance rate**: track against `{{QBR_ACCEPTANCE_TARGET}}`
- **Expansion pipeline from QBRs**: track against `{{QBR_PIPELINE_TARGET}}`
- **NPS delta post-QBR**: track directionally, positive is the only acceptable trend
- **Alert on**: 2+ QBRs missed for top-ARR-band accounts

## Retry Policy (all cadences)
| Attempt | Delay | Action |
|---------|-------|--------|
| 1st failure | 60s | Retry automatically |
| 2nd failure | 300s | Retry + alert revenue ops |
| 3rd failure | -- | Skip + create manual CRM task |

## Quality Gate
- [x] All cron expressions validated
- [x] Timezone explicitly set via `{{TIMEZONE}}`
- [x] Revenue impact framed as industry citation, not a guaranteed target
- [x] Conversion targets are `{{open_vars}}`, not hardcoded numbers
- [x] Cost model documented

## Related Artifacts
| Artifact | Relationship |
|----------|-------------|
| [[nucleus_def_n06]] | upstream |
| [[renewal_workflow_n06]] | sibling (Cadence 2 is this schedule's timing layer for that workflow) |
| [[p11_cm_content_monetization_n06]] | related |
