---
id: kc_webinar_script
kind: knowledge_card
8f: F3_inject
title: Webinar Script Template
version: 1.0.0
quality: null
pillar: P01
language: English
tldr: "Timed webinar script template -- intro, agenda, segments, Q&A, CTA, with speaker notes and slides"
when_to_use: "When producing a structured script for a live or recorded webinar presentation"
keywords: [webinar script, speaker notes, slide cues, interactive element, call to action, agenda preview, data visualization, case study example, poll question]
density_score: 1.0
related:
  - bld_instruction_webinar_script
  - bld_output_template_pitch_deck
  - webinar-script-builder
  - bld_collaboration_webinar_script
  - p01_kc_slide_generation
---

# Webinar Script Format Guide

## Structure
1. **Intro (0:00-5:00)**
   - Welcome slide + host introduction
   - Webinar objective statement
   - Agenda preview

2. **Agenda (5:00-7:00)**
   - 3-5 key topics with time allocations
   - Interactive element preview
   - Q&A session reminder

3. **Segments (7:00-95:00)** -- one row per topic:

| Segment | Subheading slot | Key points | Visual cue |
|---------|-----------------|-----------|-----------|
| Topic 1 | `<TOPIC_1>` | 3-5 bullets | `<SLIDE_N>` |
| Topic 2 | `<TOPIC_2>` | 3-5 bullets | `<SLIDE_N>` |
| Topic 3 | `<TOPIC_3>` | 3-5 bullets | `<SLIDE_N>` |

4. **Q&A (95:00-105:00)**
   - Moderated questions
   - Live chat integration
   - Poll question: [Topic]

5. **CTA (105:00-110:00)**
   - Call to action statement
   - Registration link + deadline
   - Social media hashtag

## Speaker Notes
- Use bold for key terms
- Include timing cues
- Add visual references
- Note interactive elements

### How to use

```text
ROLE: you are the webinar-script-builder producing a timed live/recorded script.
1. Load this template; copy the five-segment skeleton (Intro, Agenda, Segments, Q&A, CTA).
2. Fill each <TOPIC_N> and <SLIDE_N> slot from the brief; keep the timing cues.
3. Run the Customization Guide checklist; verify every timing cue sums to the runtime.
4. Hand the filled script to slide generation (p01_kc_slide_generation) for deck cues.
Primary 8F verb: PRODUCE (this artifact is the output skeleton an agent fills at act-time).
```

## Slide Cues

| Slide | Content |
|-------|---------|
| 1 | Title slide with date |
| 2 | Agenda overview |
| 3 | Topic 1 summary |
| 4 | Data visualization |
| 5 | Case study example |
| 6 | Interactive poll |
| 7 | Q&A instructions |
| 8 | Final CTA |

### Customization Guide
1. Replace bracketed text with specific details
2. Use bold for key terms in speaker notes
3. Maintain 10-15 word count per slide title
4. Include 3-5 key points per topic
5. Add 2-3 interactive elements
6. Verify all timing cues
7. Include 1-2 polls/questions
8. Add social media integration

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_instruction_webinar_script]] | downstream | 0.44 |
| [[bld_output_template_pitch_deck]] | downstream | 0.40 |
| [[webinar-script-builder]] | downstream | 0.37 |
| [[bld_collaboration_webinar_script]] | downstream | 0.37 |
