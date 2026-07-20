---
id: kc_prompt_technique
kind: knowledge_card
8f: F3_inject
title: Prompt Technique Patterns
version: 1.0.0
quality: null
pillar: P01
tldr: "Catalog of structured prompting methods like CoT, ToT, few-shot, and self-consistency for LLMs"
when_to_use: "When selecting or combining prompting patterns to improve LLM reasoning on a specific task"
keywords: [role-playing, chain-of-thought, tree-of-thought, few-shot learning, self-consistency, iterative refinement, constraint satisfaction, metacognitive prompts]
density_score: 0.78
related:
  - kc_reasoning_strategy
  - p01_kc_prompt_engineering_best_practices
  - p01_kc_chain_of_thought
  - p01_kc_pillar_brief_p03_prompt_en
  - p01_kc_prompt_engineering_taxonomy
---

# Prompt Technique Patterns

Prompt techniques are structured methods to elicit specific responses from AI systems. Key patterns include:

1. **Role-Playing**  
   "You are a cybersecurity expert analyzing this breach..."  
   *Encourages specialized thinking through character assumption*

2. **Chain-of-Thought (CoT)**  
   "Let's work through this step-by-step..."  
   *Prompts systematic reasoning processes*

3. **Tree-of-Thought (ToT)**  
   "Consider these alternative approaches..."  
   *Encourages parallel reasoning paths*

4. **Few-Shot Learning**  
   "Here are 3 examples of similar problems..."  
   *Uses pattern recognition for new tasks*

5. **Self-Consistency**  
   "Can you verify this answer with different reasoning paths?"  
   *Detects contradictions in responses*

6. **Iterative Refinement**  
   "Let's improve this draft with these changes..."  
   *Guides progressive content enhancement*

7. **Constraint Satisfaction**  
   "Generate a solution that meets these 5 criteria..."  
   *Focuses on specific requirements*

8. **Metacognitive Prompts**  
   "How would you approach this problem differently?"  
   *Encourages reflection and adaptation*

These techniques optimize output quality by shaping the AI's reasoning process through structured guidance.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_reasoning_strategy]] | sibling | 0.33 |
| [[p01_kc_prompt_engineering_taxonomy]] | sibling | 0.27 |
