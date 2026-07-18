---
kind: quality_gate
id: p03_qg_multimodal_prompt
pillar: P11
llm_function: GOVERN
purpose: Gate de qualidade com pontuação HARD e SOFT para multimodal_prompt
quality: null
title: "Quality Gate Multimodal Prompt"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [multimodal_prompt, builder, quality_gate]
tldr: "Gate de qualidade com pontuação HARD e SOFT para multimodal_prompt"
domain: "construção de multimodal_prompt"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F7_govern"
keywords: [construção de multimodal_prompt, quality gate multimodal prompt, multimodal_prompt, builder, quality_gate, gate de qualidade, condição de falha, guia de pontuação, limiar de métrica, operador de limiar]
density_score: 0.85
related:
  - multimodal-prompt-builder
---
## Gate de Qualidade

## Definição
(Tabela: métrica, limiar, operador, escopo)
| métrica         | limiar | operador | escopo          |
|----------------|-----------|----------|----------------|
| modalities     | 2         | >=       | cada prompt    |
| cross_ref      | 1         | >=       | metadados      |

## Gates HARD
(Tabela: ID | Verificação | Condição de Falha)
| ID         | Verificação                          | Condição de Falha                                      |
|------------|--------------------------------|-----------------------------------------------------|
| H01        | Frontmatter YAML válido         | Sintaxe YAML inválida ou campos ausentes               |
| H02        | ID corresponde a ^p03_mmp_[a-z][a-z0-9_]+.md$ | Formato de ID inválido ou padrão de schema ausente        |
| H03        | Campo kind corresponde a 'multimodal_prompt' | Kind incompatível ou campo ausente                     |
| H04        | Pelo menos 2 modalidades presentes  | Apenas 1 modalidade ou nenhuma especificada                   |
| H05        | Sem instruções conflitantes    | Comandos contraditórios entre modalidades          |
| H06        | Metadados incluem 'modality_type' | Campo de metadado obrigatório ausente                   |
| H07        | Prompt não vazio               | Conteúdo de texto/áudio/visão vazio                     |

## Pontuação SOFT
(Tabela: Dim | Dimensão | Peso | Guia de Pontuação)
| Dim | Dimensão         | Peso | Guia de Pontuação                                      |
|-----|-------------------|--------|----------------------------------------------------|
| D1  | Coerência         | 0.15   | 1.0: Perfeita; 0.5: Pequenas lacunas; 0.0: Incoerente    |
| D2  | Completude      | 0.15   | 1.0: Todas as modalidades cobertas; 0.5: Falta 1 modalidade |
| D3  | Clareza           | 0.12   | 1.0: Inequívoco; 0.5: Ambíguo; 0.0: Confuso   |
| D4  | Alinhamento cross-modal | 0.18 | 1.0: Alinhamento perfeito; 0.5: Parcial; 0.0: Nenhum    |
| D5  | Equilíbrio de modalidade  | 0.10   | 1.0: Distribuição uniforme; 0.5: Desequilibrado; 0.0: Sobrecarregado |
| D6  | Criatividade        | 0.10   | 1.0: Original; 0.5: Padrão; 0.0: Sem graça                |
| D7  | Precisão técnica| 0.10   | 1.0: Correto; 0.5: Pequenos erros; 0.0: Falhas graves   |
| D8  | Intenção do usuário       | 0.10   | 1.0: Propósito claro; 0.5: Vago; 0.0: Desalinhado    |

## Ações
(Tabela: Pontuação | Ação)
| Pontuação     | Ação         |
|-----------|----------------|
| >=9.5     | GOLDEN         |
| >=8.0     | PUBLISH        |
| >=7.0     | REVIEW         |
| <7.0      | REJECT         |

## Bypass
(Tabela: condições, aprovador, trilha de auditoria)
| condições              | aprovador         | trilha de auditoria                          |
|-------------------------|------------------|--------------------------------------|
| Correção emergencial necessária  | Engenheiro Sênior  | Bypass registrado com motivo e aprovador |

## Exemplos

## Exemplo Golden
```yaml
model: "Salesforce/blip"
modalities: [image, text, audio]
task: "Generate a caption for an image and describe the corresponding audio"
prompt: |
  [Image: A cat sitting on a windowsill]
  [Audio: Meowing sound]
  Describe this scene and the audio in detail.
```

## Anti-Exemplo 1: Prompt somente-texto
```yaml
model: "Salesforce/blip"
modalities: [text]
task: "Generate a caption"
prompt: "Describe this image of a cat on a windowsill"
```
## Por que falha
Exclui as modalidades não-texto obrigatórias (imagem/áudio) apesar de afirmar ser multimodal. Não integra elementos cross-modais.

## Anti-Exemplo 2: Configuração de modelo
```yaml
model: "Salesforce/blip"
modalities: [image, text]
task: "Generate caption"
prompt: |
  [Image: Cat on windowsill]
  max_tokens: 50
  temperature: 0.7
```
## Por que falha
Inclui parâmetros de modelo (max_tokens, temperature) que pertencem ao multi_modal_config, não ao conteúdo real do multimodal prompt.

### H_RELATED: Checagem de Referência Cruzada (HARD)
- [ ] Campo de frontmatter `related:` preenchido (mín. 3 entradas)
- [ ] Seção `## Related Artifacts` presente no corpo do artefato
- [ ] Ao menos 1 referência upstream e 1 downstream ou sibling
- Gate: REJECT se < 3 entradas (auto-preenchido por cex_wikilink.py no F6.5)

### S_RELATED: Checagem de Referência Cruzada (SOFT)
- [ ] Campo de frontmatter `related:` preenchido (3-15 entradas)
- [ ] Seção `## Related Artifacts` presente no corpo do artefato
- [ ] Ao menos 1 referência upstream e 1 downstream
- Penalidade: -0.3 se vazio (não bloqueia, incentiva a interligação)
