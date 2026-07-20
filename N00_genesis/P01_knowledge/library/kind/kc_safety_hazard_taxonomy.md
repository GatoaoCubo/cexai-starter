---
id: kc_safety_hazard_taxonomy
kind: knowledge_card
8f: F3_inject
title: Safety Hazard Taxonomy
version: 1.0.0
quality: null
pillar: P01
tldr: "12-category AI safety hazard classification with severity levels and response templates per category"
when_to_use: "When building content moderation or safety filters that classify and respond to harmful content"
keywords: [cbrn, deepfakes, malware distribution, phishing, exploitation, system compromise]
density_score: 1.0
related:
  - kc_c2pa_manifest
  - bld_collaboration_content_filter
  - p05_output_validator
  - bld_knowledge_card_content_filter
  - n00_content_filter_manifest
---

# Safety Hazard Taxonomy

## Hazard Categories (12)
1. Violence
2. Sexual Content
3. CBRN (Chemical, Biological, Radiological, Nuclear)
4. Hate Speech
5. Illegal Activities
6. Privacy Violations
7. Misinformation
8. Deepfakes
9. Malware Distribution
10. Phishing
11. Exploitation
12. System Compromise

## Severity Levels
- **Low**: Minimal risk, no immediate action required
- **Medium**: Potential risk, requires monitoring
- **High**: Immediate action needed to prevent harm
- **Critical**: Severe threat requiring emergency response

## Response Templates
- **Violence**: "This content contains explicit violent material. Please review our safety guidelines."
- **Sexual Content**: "This content includes explicit sexual material. Consider reviewing our content policies."
- **CBRN**: "This content may pose physical harm risks. Immediate containment is recommended."
- **Hate Speech**: "This content promotes hate speech. Please review our community standards."
- **Illegal Activities**: "This content involves illegal activities. Reporting is advised."
- **Privacy Violations**: "This content violates privacy norms. Please review data protection policies."
- **Misinformation**: "This content contains misleading information. Verify sources before sharing."
- **Deepfakes**: "This content may be synthetic media. Verify authenticity before engagement."
- **Malware Distribution**: "This content distributes malicious software. Immediate system scan recommended."
- **Phishing**: "This content may be a phishing attempt. Do not click suspicious links."
- **Exploitation**: "This content may involve exploitation. Report to authorities immediately."
- **System Compromise**: "This content may compromise system security. Disconnect and investigate immediately."

## How to use

You are a content-moderation or safety-filter builder. Load this taxonomy at F3 INJECT
to give a classifier its label set. Use the 12 categories as the canonical output classes,
the Severity Levels to route the action, and the Response Templates as the user-facing
message. Set your block/allow boundary at `{{SEVERITY_THRESHOLD}}` (e.g. block >= High).

## Procedure

1. Run the candidate content through the classifier to get a category + severity.
2. If severity < `{{SEVERITY_THRESHOLD}}`, allow with monitoring; else proceed.
3. Select the matching Response Template for the detected category.
4. Apply the routed action (warn -> review -> block -> emergency) per the Severity Levels.
5. Log the decision (category, severity, action) to the audit trail for later review.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_c2pa_manifest]] | sibling | 0.27 |
| [[bld_collaboration_content_filter]] | downstream | 0.27 |
| [[bld_knowledge_card_content_filter]] | sibling | 0.22 |
