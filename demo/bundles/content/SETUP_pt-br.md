# SETUP -- content (agent de knowledge_card) -- guia combinado PT-BR

Guia geral do bundle `content`. Para o passo a passo detalhado por runtime,
veja os arquivos especificos:

- **ChatGPT (Custom GPT ou Projects)** -> `SETUP_chatgpt_projects.md`
- **Claude Projects** -> `SETUP_claude_projects.md`
- **Gemini Gems** -> `SETUP_gemini_gems.md`

> **Fidelidade**: `completa` em qualquer runtime. Este bundle nao usa tiers
> de coleta, Actions, MCP, nem chaves de API -- os 12 arquivos de pilar
> (P01-P12) mais a instrucao de sistema SAO o agent inteiro, em qualquer IA
> que aceite upload de Knowledge/Files e um campo de Instructions.

## O que este bundle e

O bundle `content` e o contrato de 12 pilares (a forma "12 ISO" da CEXAI)
para o kind `knowledge_card` -- nucleus N04, pillar P01, verb `document`.
Suba os 12 arquivos como Knowledge em qualquer assistente, cole a instrucao,
e ele vira um agent funcional de captura de conhecimento: voce descreve um
processo ou topico, e ele entrega um `knowledge_card` completo -- fatos
atomicos, densos, pesquisaveis, prontos para RAG.

## Arquivos do bundle (15 no total)

```
content/
  P01_knowledge.md            <- conhecimento de dominio sobre o kind knowledge_card
  P02_model.md                <- identidade e persona do builder
  P03_prompt.md                <- instrucoes passo a passo de producao
  P04_tools.md                 <- ferramentas e validadores
  P05_output.md                <- template de saida (o card final)
  P06_schema.md                <- schema formal -- fonte da verdade dos campos
  P07_evals.md                 <- portoes de qualidade + exemplos-modelo
  P08_architecture.md          <- mapa de componentes e dependencias
  P09_config.md                <- convencoes de nome, caminhos, limites
  P10_memory.md                <- licoes aprendidas (learning record)
  P11_feedback.md              <- anti-padroes + protocolo de correcao
  P12_orchestration.md         <- papel do builder em crews multi-agent
  customgpt_instructions.json  <- config pronta para Custom GPT (nome, instructions, starters)
  system_instruction.md        <- a mesma instrucao, em formato de prompt de sistema
  README.md                    <- visao geral + passo a passo de upload
  SETUP_*.md                   <- guias de setup (este + 3 especificos)
```

## Antes de subir: preencha os placeholders

Todo campo `[fornecer: ...]` em `system_instruction.md` e em
`customgpt_instructions.json` marca um dado real que falta -- o nome da sua
marca, o tom de voz, os valores. Preencha esses campos ANTES de subir o
bundle. Sem isso o agent funciona, mas fala de forma generica, nao na voz da
sua marca.

## Opcao A -- ChatGPT (Custom GPT ou Projects)

Veja `SETUP_chatgpt_projects.md` para o passo a passo completo. Resumo:
1. Custom GPT (Plus): cole o campo `instructions` de
   `customgpt_instructions.json` e suba os 12 arquivos como Knowledge.
2. Projects (qualquer plano): cole `system_instruction.md` e suba os 12
   arquivos como Files.

## Opcao B -- Claude Projects

Veja `SETUP_claude_projects.md` para o passo a passo completo. Resumo:
1. Crie um Project.
2. Cole `system_instruction.md` nas Project Instructions.
3. Suba os 12 arquivos como Knowledge.

## Opcao C -- Gemini Gems

Veja `SETUP_gemini_gems.md` para o passo a passo completo. Resumo:
1. Crie um Gem.
2. Cole `system_instruction.md` nas Instructions.
3. Suba os 12 arquivos como Knowledge.

## Como usar (fluxo tipico, em qualquer runtime)

1. Diga o que quer documentar: `Documentar o processo de integracao de
   novos funcionarios como um knowledge card`.
2. O agent confirma o topico e classifica como `domain_kc` (conhecimento
   externo) ou `meta_kc` (interno a sua empresa) -- regra em `P09_config.md`.
3. Ele produz o `knowledge_card` completo: frontmatter (14 campos
   obrigatorios + 5 estendidos) mais corpo estruturado -- Referencia Rapida,
   Conceitos-Chave, Fases da Estrategia, Regras de Ouro, Fluxo, Comparativo,
   Referencias (ou a estrutura meta_kc, quando aplicavel).
4. Ele se autovalida contra os portoes HARD antes de entregar (ver
   `P07_evals.md`).
5. Onde faltar dado real, ele emite `[fornecer: ...]` em vez de inventar.

## Solucao de problemas

- **"O agent inventou um dado que eu nao dei"** -> as SALVAGUARDAS de
  `system_instruction.md` proibem isso explicitamente; reforce na conversa:
  "nunca fabrique -- onde faltar dado, use `[fornecer: ...]`".
- **O card saiu raso, pouco denso** -> peca: "aumente a densidade seguindo
  P01_knowledge.md -- tabelas e bullets antes de prosa".
- **Quero mudar a estrutura do card (domain_kc vs meta_kc)** -> peca
  explicitamente a classificacao; a regra de selecao esta em `P09_config.md`.
- **Resposta generica, nao soa como a minha marca** -> confirme que os
  campos `[fornecer: ...]` de `system_instruction.md` foram preenchidos com
  dados reais ANTES de colar as Instructions no runtime escolhido.
- **Quero trocar de runtime depois (ex.: ChatGPT -> Claude)** -> os mesmos
  12 arquivos servem para os tres; so muda onde a instrucao e colada.

## Manutencao

Este bundle e gerado a partir dos artefatos tipados da CEXAI
(`archetypes/builders/knowledge-card-builder/`). Para mudar o comportamento
do agent de forma permanente, edite a fonte no repositorio CEXAI e regenere
o bundle -- evite editar so os 12 arquivos aqui se voce mantem mais de uma
copia deste bundle.

## Creditos

Arquitetura: CEXAI (300+ kinds, 12 pillars, 8 nuclei, pipeline 8F). Este
bundle e a forma "12 ISO" do kind `knowledge_card`, o mesmo formato usado
pelos demais capability bundles do catalogo publico.
