---
id: p01_kc_intelligence_as_asset
kind: knowledge_card
8f: F3_inject
pillar: P01
nucleus: n06
title: "Knowledge Card -- Intelligence-as-Asset Valuation Framework"
version: 1.0.0
quality: null
tags: [valuation, intelligence-as-asset, ai-brain, balance-sheet, intangible-asset, exchange, monetization, commercial]
keywords: [intelligence as asset, ai brain valuation, intangible asset, asc 350, ias 38, dcf, market comps, cost approach, network effects, exchange marketplace]
density_score: 0.92
related:
  - p11_cm_cexai_monetization
  - p11_cm_exchange_marketplace
  - subscription_tier_n06
  - roi_calculator_n06
  - kc_brand_monetization_models
  - p01_kc_ai_saas_monetization
  - kc_competitive_positioning
updated: "2026-05-27"
---

<!-- 8F: F1=knowledge_card P01 F2=knowledge-card-builder F3=whitepaper+manifest F4=plan F5=scan F6=produce F7=gate F8=save -->

# Intelligence-as-Asset: Valuation Framework

## Thesis

A typed, governed CEXAI repository is a balance-sheet asset, not a recurring expense. Every commit is a deposit. Every artifact is equity. The repository is the AI brain. Like real estate, brand, and trained workforce, governed intelligence has a defensible value, a depreciation schedule, and a market.

This card answers: **how much is an AI brain worth?** It defines the three valuation approaches, the appreciation curve unique to typed knowledge, the accounting treatment under ASC 350 and IAS 38, and the input variables CEXAI ROI calculators use to price an instance.

---

## 1. The Three Valuation Approaches (IFRS-aligned)

The same framework appraisers use for intangibles applies to AI brains. Pick one or triangulate all three.

| Approach | Formula | Best For | Limit |
|----------|---------|----------|-------|
| **Cost approach** | Sum of replacement cost per artifact x quantity x quality multiplier | Early-stage repos, no revenue history | Floor only -- ignores compounding network effects |
| **Income approach** | NPV of decision-quality lift over useful life | Mature repos with measurable productivity delta | Requires baseline counterfactual |
| **Market approach** | Comparable transactions x size adjustment | Acquisitions, M&A, secondary sale | Few public comps yet -- early market |

A defensible appraisal triangulates all three and reports the median. Lone-method valuations are challenged in M&A diligence.

### 1.1 Cost approach

```
V_cost = Sum_kinds( N_artifacts * cost_per_artifact * quality_multiplier )

cost_per_artifact = labor_hours * blended_rate + tool_cost + review_cost
quality_multiplier = 1.0 (>= 9.0 score), 0.7 (8.0-8.9), 0.4 (< 8.0), 0.0 (failing)
```

Calibration: a CEXAI artifact built via 8F at >= 9.0 averages 2-4 hours of senior engineer time at $100-200/hr blended. Mean cost basis: $400-800 per governed artifact. A 1,000-artifact repo with 70% at >= 9.0 has cost-basis floor of $280K-560K.

### 1.2 Income approach

```
V_income = Sum_periods( (decision_lift_$ - operating_cost) / (1 + WACC)^t )

decision_lift_$ = (decisions_per_year) * (avg_decision_value) * (quality_delta)
quality_delta = (CEXAI_quality - baseline_quality) / 10
useful_life = 5-7 years (artifact decay before replacement)
```

Calibration: a 50-person org makes ~10,000 LLM-mediated decisions/year. Each decision averages $50-500 in productivity stake. A 0.20 quality delta (from 7.0 baseline to 9.0 governed) compounds to $100K-$1M annual lift. NPV at 12% WACC over 5 years: $360K-$3.6M.

### 1.3 Market approach

Comparable transactions in adjacent intangibles markets:

| Comp class | Transaction range | Multiple basis |
|-----------|-------------------|----------------|
| Premium domain names | $5K-$30M | Search volume, brand fit |
| SaaS ARR multiples | 5x-15x ARR | Revenue durability |
| Trained ML models (HuggingFace marketplace) | $50-$50K | Performance, dataset quality |
| Notion templates (premium) | $20-$2K | Reuse breadth |
| Customer data assets (CRM transfers) | $10-$200 per record | Recency, completeness |
| Patent portfolios (pharma) | $50K-$50M per | Coverage, expiry |

CEXAI Exchange comps will emerge as the marketplace matures. Early signal: vertical AI brains (healthcare, fintech) trade at 10x-30x cost basis when domain rigor is verifiable.

---

## 2. The Appreciation Curve

Software depreciates. Knowledge appreciates. This is the structural difference between a typical SaaS license and a governed AI brain.

```
Value
  |
  |                         Typed governed knowledge (CEXAI)
  |                       *
  |                     *
  |                   *
  |                 *  <-- compounding via Exchange + commits
  |               *
  |             *
  |           *
  |         *
  |       *  <-- traditional software (depreciates)
  |     *  ----.
  |   *         ----.
  | *               ----.
  +------------------------------------> Time
   T0    Y1    Y2    Y3    Y4    Y5
```

### 2.1 Why governed knowledge appreciates

| Mechanism | Effect on value |
|-----------|----------------|
| **Network effect** | Every new artifact raises retrieval quality for every existing artifact (more context = better grounding) |
| **Composability** | New kinds combine with old kinds; combinatoric expansion of usable patterns |
| **Quality ratchet** | F7 GOVERN gate enforces monotonic quality floor; bad artifacts cannot enter |
| **Provenance accrual** | Lineage and audit trail grow; auditability is monotonic |
| **Exchange access** | More artifacts = more identity capital on the marketplace |
| **Vendor portability** | LLM upgrades raise output quality without artifact rewrites |

### 2.2 Depreciation events

Even appreciating assets have decay vectors. Track and offset:

| Decay vector | Half-life | Mitigation |
|-------------|-----------|------------|
| Schema drift (kind taxonomy evolves) | 18-36 months | `cex_doctor.py` migration warnings |
| Model upgrade obsolescence | 12-24 months | Rerun affected artifacts at higher tier |
| Domain factual decay | 6-24 months (varies) | Lifecycle rules + freshness audits |
| External dependency (linked KCs) | Variable | Provenance tracking + dead-link gates |

Net effect for active repos: appreciation > depreciation for at least 5-7 years. Stale repos depreciate after year 3.

---

## 3. Accounting Treatment

For balance-sheet recognition, the AI brain qualifies as an **identifiable intangible asset** under both US GAAP (ASC 350) and IFRS (IAS 38).

### 3.1 Recognition criteria (IAS 38 paragraph 21, summarized)

| Criterion | CEXAI repo satisfies? |
|-----------|----------------------|
| Identifiable (separable or arises from contractual rights) | YES -- repo is git-portable; artifacts are discrete |
| Controlled by the entity | YES -- private repository with commit access controls |
| Future economic benefits flow to entity | YES -- decision-quality lift, automation, sale proceeds |
| Cost reliably measurable | YES -- commit-time-stamped engineering hours + tool spend |

### 3.2 Capitalization vs expensing

| Phase | Treatment |
|-------|-----------|
| Research (exploratory KCs, intent discovery) | Expensed |
| Development (artifacts that meet F7 threshold) | Capitalizable from feasibility forward |
| Maintenance (refresh, schema migration) | Expensed unless materially extending useful life |

### 3.3 Amortization

Useful life: 5-7 years (mirrors enterprise software intangibles). Method: straight-line unless income approach justifies front-loaded.

### 3.4 Impairment triggers

- Quality score regression > 20% across cohort
- Schema deprecation removes >= 1 kind class
- Domain pivot makes >= 30% of artifacts irrelevant

When triggered: write down to recoverable amount per ASC 350-30-35.

---

## 4. The Exchange Premium

A repo that participates in the CEXAI Exchange has higher value than a closed repo of identical content. This is the exchange premium.

```
V_total = V_isolated * (1 + exchange_multiplier)

exchange_multiplier = f(
  artifacts_published_to_marketplace,
  contributor_reputation_score,
  fork_count,
  citation_count_in_others_repos
)
```

Empirical proxy from adjacent markets (npm, GitHub, HuggingFace): top-decile contributors capture 3x-10x value premium versus closed-equivalents. Same logic applies to typed knowledge once liquidity arrives.

### 4.1 Exchange-driven valuation deltas

| Action on Exchange | Value impact |
|--------------------|--------------|
| Publish 1 high-rated nucleus archetype | +5-15% (reputation seed) |
| Get cited in 10+ downstream repos | +20-50% (utility-proven) |
| Sell or license to another instance | Direct revenue + market signal |
| Fork and improve another's work | +10% (composer credibility) |
| Get acquired with the host org | Valuation absorbed into transaction multiple |

---

## 5. ROI Inputs (used by `roi_calculator_n06`)

The calculator monetizes the framework above. Inputs map to lines in this card.

```yaml
inputs:
  artifact_count: int               # current repo size
  avg_quality: float                # mean F7 score across repo
  avg_build_cost_usd: float         # per-artifact cost basis (cost approach)
  decisions_per_year: int           # automatable LLM-mediated decisions
  avg_decision_value_usd: float     # productivity stake per decision
  baseline_quality: float           # quality without governance (typically 6-7)
  cexai_quality: float              # quality with governance (typically 8.5-9.5)
  wacc: float                       # discount rate, default 0.12
  useful_life_years: int            # default 5
  exchange_published: int           # artifacts on Exchange
  exchange_multiplier: float        # derived, default 0.0-0.4

outputs:
  v_cost: float                     # cost-approach valuation
  v_income: float                   # income-approach NPV
  v_market: float                   # market-approach (when comps available)
  v_blended: float                  # median of three
  appreciation_5y: float            # projected value at year 5
  payback_months: float             # time to recover deployment cost
```

---

## 6. Pricing Implications

| Pricing decision | Framework input |
|------------------|----------------|
| Enterprise tier ceiling | V_blended * acquirer_capture_share (~ 15-25%) |
| Per-seat upsell ceiling | V_income / (employees * useful_life_years) |
| Marketplace listing floor | V_cost / artifact_count for the listed bundle |
| Take rate justification | Exchange_multiplier - take_rate > 0 (positive contributor net) |
| Acquisition price (M&A) | V_blended * synergy_multiplier (~ 1.2-2.0) |

---

## 7. Anti-patterns

| Anti-pattern | Why it fails |
|-------------|--------------|
| Pricing CEXAI as a SaaS subscription only | Misses asset-appreciation upside; misframes the buying decision |
| Single-method valuations | Easily challenged in diligence; triangulate or lose credibility |
| Ignoring appreciation curve | Static valuations underprice mature repos by 5-10x |
| Treating Exchange as zero-sum | Liquidity premium is positive-sum; closed repos forfeit it |
| Mixing development and maintenance costs | Inflates cost basis; misstates capitalizable value |
| Capitalizing failing artifacts | Below-floor (< 8.0) artifacts are not capitalizable |

---

## 8. Source-of-truth links

- Whitepaper sections: `docs/WHITEPAPER_CEXAI_CAPABILITIES.md` (compounding thesis; commercial pricing + vertical TAM in the Business Case appendix)
- Monetization plan: `N06_commercial/P11_feedback/p11_cm_cexai_monetization.md`
- Exchange marketplace economics: `N06_commercial/P11_feedback/p11_cm_exchange_marketplace.md`
- ROI calculator: `N06_commercial/P11_feedback/roi_calculator_n06.md`
- Investor narrative: `N06_commercial/P05_output/pitch_deck_intelligence_as_asset.md`

---

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| p11_cm_cexai_monetization | downstream | 0.55 |
| p11_cm_exchange_marketplace | downstream | 0.50 |
| roi_calculator_n06 | downstream | 0.45 |
| subscription_tier_n06 | related | 0.40 |
| kc_brand_monetization_models | related | 0.35 |
