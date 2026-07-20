---
id: kc_agentic_rag
kind: knowledge_card
8f: F3_inject
title: Agentic RAG Pattern
version: 1.0.0
quality: null
pillar: P01
tldr: "RAG pattern where an agent orchestrates retrieval, context assembly, and generation in a feedback loop"
when_to_use: "When building retrieval-augmented systems that need agent-driven query routing and iterative refinement"
keywords: [retrieval augmented generation, knowledge base, generative model, retriever, feedback loop, contextual understanding, document selection, fine-tune]
density_score: 0.98
related:
  - p01_kc_model_context_protocol
  - agentic-rag-builder
  - p01_kc_academic_rag_patterns
  - p01_gl_rag
  - bld_instruction_agentic_rag
---

# Agentic RAG Pattern

## Overview
The Agentic RAG (Retrieval-Augmented Generation) pattern combines the strengths of retrieval systems and generative models to create a more effective and context-aware knowledge processing system.

## Key Components
1. **Agent**: A specialized component that manages the RAG workflow
2. **Retrieval System**: Used to fetch relevant documents from a knowledge base
3. **Generative Model**: Produces coherent and contextually appropriate responses
4. **Feedback Loop**: Enables continuous improvement through iterative refinement

## Implementation
```python
class AgenticRAG:
    def __init__(self, retriever, generator):
        self.retriever = retriever
        self.generator = generator
        
    def generate(self, query):
        retrieved_docs = self.retriever.retrieve(query)
        context = self._build_context(retrieved_docs)
        response = self.generator.generate(query, context)
        return response
    
    def _build_context(self, docs):
        # Combine retrieved documents into a coherent context
        return " ".join([doc.content for doc in docs])
```

## Benefits
- Enhanced contextual understanding
- Better handling of complex queries
- Continuous learning through feedback
- More accurate and relevant responses

## Use Cases
- Customer support systems
- Research assistants
- Content creation tools
- Educational platforms

## Best Practices
1. Use high-quality retrievers for accurate document selection
2. Fine-tune the generative model for domain-specific tasks
3. Implement robust feedback mechanisms for continuous improvement
4. Regularly update the knowledge base with new information

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_model_context_protocol]] | sibling | 0.36 |
| [[agentic-rag-builder]] | related | 0.32 |
| [[p01_gl_rag]] | related | 0.28 |
| [[bld_instruction_agentic_rag]] | downstream | 0.26 |
