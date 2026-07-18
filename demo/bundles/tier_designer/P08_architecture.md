---
kind: architecture
id: bld_architecture_subscription_tier
pillar: P08
llm_function: CONSTRAIN
purpose: "Mapa de componentes de subscription_tier -- inventário, dependências"
quality: null
title: "Architecture Subscription Tier"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [subscription_tier, builder, architecture]
tldr: "Mapa de componentes de subscription_tier -- inventário, dependências"
domain: "construção de subscription_tier"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [construção de subscription_tier, architecture subscription tier, subscription_tier, builder, architecture, inventário de componentes, compartilhamento de conhecimento, posição arquitetural, related artifacts]
density_score: 0.85
related:
  - bld_architecture_self_improvement_loop
  - bld_architecture_compliance_checklist
  - bld_architecture_ab_test_config
  - bld_architecture_enterprise_sla
  - bld_architecture_audit_log
---

## Inventário de Componentes
| Nome da ISO          | Papel                          | Pillar | Status |
|----------------------|-------------------------------|--------|--------|
| bld_manifest         | Definição da configuração principal | P11    | Ativo |
| bld_instruction      | Lógica de geração de instruções | P03    | Ativo |
| bld_system_prompt    | Orientação em nível de sistema | P03    | Ativo |
| bld_schema           | Validação da estrutura de dados | P06    | Ativo |
| bld_quality_gate     | Verificações de garantia de qualidade | P11    | Ativo |
| bld_output_template  | Formatação de saída | P05    | Ativo |
| bld_examples         | Fornecimento de dados de exemplo | P11    | Ativo |
| bld_knowledge_card   | Gestão de conhecimento | P01    | Ativo |
| bld_architecture     | Desenho estrutural | P08    | Ativo |
| bld_collaboration    | Coordenação de equipe | P12    | Ativo |
| bld_config           | Gestão de configuração | P09    | Ativo |
| bld_memory           | Retenção de dados | P10    | Ativo |
| bld_tools            | Integração de ferramentas | P04    | Ativo |

## Dependências
| De             | Para             | Tipo         |
|----------------|------------------|--------------|
| bld_config     | bld_manifest     | Configuração |
| bld_quality_gate | bld_schema     | Validação    |
| bld_output_template | bld_instruction | Formatação   |
| bld_tools      | bld_memory       | Armazenamento |
| bld_collaboration | bld_knowledge_card | Compartilhamento de Conhecimento |

## Posição Arquitetural
subscription_tier é um componente fundamental no pillar P11 do CEX, orquestrando configurações específicas de tier, garantindo consistência, qualidade e colaboração entre níveis de assinatura através de ferramentas integradas, sistemas de memória e validação de schema.

## Related Artifacts
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| bld_architecture_self_improvement_loop | sibling | 0.79 |
| bld_architecture_compliance_checklist | sibling | 0.78 |
| bld_architecture_ab_test_config | sibling | 0.75 |
| bld_architecture_enterprise_sla | sibling | 0.72 |
| bld_architecture_audit_log | sibling | 0.71 |
