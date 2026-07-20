---
id: self_improvement_loop_n02
kind: self_improvement_loop
8f: F7_govern
pillar: P11
nucleus: n02
title: "N02 Autonomous Copy Quality Evolution Loop"
version: 1.0.0
quality: null
tags: [self_improvement_loop, copy_quality, autonomous_evolution, P11, n02_marketing]
domain: campaign-feedback
status: active
keywords: [campaign_complete, threshold_breach, explicit_invoke, weekly_cron, ab_test_concluded, performance_signal, asset_id, ctr, conversion_rate, engagement_rate]
density_score: 1.0
related:
  - p06_vs_content_spec_n02
  - p10_em_n02
---

# N02 Autonomous Copy Quality Evolution Loop

## The Premise

Copy that doesn't evolve dies. Every campaign is a lesson. Every lesson that
isn't captured is wasted. This loop exists to get better with every brief
processed -- not through human review alone, but through systematic,
autonomous quality evolution.

## Loop Architecture

```
TRIGGER
  |
  v
COLLECT -- harvest performance signals from deployed campaigns
  |
  v
SCORE -- apply 5D quality model to copy assets
  |
  v
ANALYZE -- identify patterns in high/low performers
  |
  v
HYPOTHESIZE -- form improvement rules
  |
  v
TEST -- apply rules to next brief (controlled)
  |
  v
MEASURE -- compare treated vs. control
  |
  v
COMMIT -- winning rules -> brand vocabulary + validation schema
  |
  v
DISCARD -- losing rules -> archive (never delete, learn from failure)
  |
  [LOOP]
```

## Trigger Conditions

| Trigger | Condition | Minimum Data Required |
|---------|-----------|----------------------|
| `campaign_complete` | Campaign end_date reached | 1 campaign, 7+ days live |
| `threshold_breach` | CTR < 0.5% or conversion_rate < 1% | 100+ impressions |
| `explicit_invoke` | User runs the improve/evolve command | Any deployed copy |
| `weekly_cron` | Every 7 days (automated) | Any accumulated signal |
| `ab_test_concluded` | Winner declared in an A/B test config | Both variants min 1000 impressions |

## Signal Collection Schema

```yaml
performance_signal:
  campaign_id: string
  asset_id: string
  platform: instagram|linkedin|x|meta|email
  format: post|story|reel|carousel|email|ad
  metrics:
    impressions: integer
    clicks: integer
    ctr: float              # clicks / impressions
    conversions: integer
    conversion_rate: float  # conversions / clicks
    cost_per_click: float   # nullable (paid only)
    cost_per_acquisition: float  # nullable
    engagement_rate: float  # (likes + comments + shares) / impressions
    save_rate: float        # saves / impressions (Instagram)
  copy_features:
    word_count: integer
    has_emoji: boolean
    emoji_count: integer
    has_question: boolean
    has_number: boolean
    cta_verb: string
    urgency_trigger: none|deadline|scarcity|social_proof
    brand_voice: string
    hook_type: pain|curiosity|authority|social_proof|data
    funnel_stage: TOFU|MOFU|BOFU
```

## Scoring Model (5D)

| Dimension | Weight | Metric |
|-----------|--------|--------|
| D1 Conversion | 35% | conversion_rate vs. platform benchmark |
| D2 Engagement | 25% | engagement_rate vs. campaign average |
| D3 Brand Voice | 20% | compliance score from the validation schema |
| D4 Efficiency | 15% | CPA vs. campaign budget target |
| D5 Longevity | 5% | Performance decay rate over campaign lifetime |

**Benchmark Targets (update quarterly, replace with your own measured baseline):**

| Platform | Format | CTR Benchmark | Engagement Benchmark |
|----------|--------|--------------|---------------------|
| Instagram | Post | 0.9% | 3.0% |
| Instagram | Reel | 1.2% | 5.0% |
| LinkedIn | Post | 0.5% | 2.0% |
| Meta Ads | Feed | 1.5% | 1.0% |
| Email | Standard | 2.5% CTR | 20% open rate |

## Pattern Analysis Rules

```yaml
patterns_to_extract:
  - copy_feature vs performance_delta
  - hook_type distribution in top 20% performers
  - cta_verb frequency in conversion rate leaders
  - emoji_count optimal range per platform
  - word_count sweet spots per format
  - urgency_trigger lift per funnel_stage

min_sample_for_rule: 10 assets
confidence_threshold: 0.75  # above = adopt rule; below = flag for human review
```

## Hypothesis & Test Protocol

```yaml
hypothesis_format:
  id: hyp_{date}_{sequence}
  statement: "Using [feature] in [context] increases [metric] by ~[delta]%"
  based_on: array[signal_ids]
  confidence: float
  test_design:
    control: copy without feature
    treatment: copy with feature
    min_impressions: 1000
    significance_level: 0.95
    max_runtime_days: 14
```

## Commit Gate (Rule Promotion)

A hypothesis becomes a rule only when:

1. Statistical significance >= 95% (p < 0.05)
2. Effect size > 10% improvement on primary metric
3. Replicated on >= 2 different campaigns or platforms
4. No violation of the content validation schema's constraints

## Failure Archive Protocol

Every losing hypothesis is logged:
```yaml
discard_log:
  hyp_id: string
  hypothesis: string
  outcome: string
  why_failed: string  # data-driven explanation
  retest_conditions: string  # under what conditions to retry
```

Failures are not deleted. They prevent re-learning the same wrong lesson.

## Loop Metrics (Self-Evaluation)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Rules promoted per month | >= 2 | Count of committed rules |
| Hypothesis cycle time | <= 14 days | trigger -> commit |
| Average score improvement | >= 5% per quarter | 5D model delta |
| False positive rate | < 20% | Promoted rules that underperform on retest |
| Signal coverage | >= 80% of campaigns | Campaigns with collected signals |

## Integration

- Consumes: A/B test results (winner data)
- Produces to: the brand vocabulary knowledge card (promoted rules)
- Produces to: `p06_vs_content_spec_n02.md` (new validation gates)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p06_vs_content_spec_n02]] | related | 0.30 |
| [[p10_em_n02]] | upstream | 0.28 |
