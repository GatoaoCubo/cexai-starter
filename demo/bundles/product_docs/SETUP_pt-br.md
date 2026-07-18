# SETUP -- Product Docs -- guia combinado PT-BR

Guia geral do bundle `product_docs`. Para o passo a passo detalhado por
runtime, veja os arquivos específicos:

- **ChatGPT (Projects free ou Custom GPT Plus)** -> `SETUP_chatgpt_projects.md`
- **Claude Projects** -> `SETUP_claude_projects.md`
- **Gemini Gems** -> `SETUP_gemini_gems.md`

> **Fidelidade**: `FULL` em qualquer runtime. Este bundle não usa Actions,
> MCP, scraping ou nenhuma ferramenta externa -- é o formato CEXAI "12 ISO"
> (12 arquivos de pilar + uma instrução para colar). Por isso, ao contrário
> de bundles de pesquisa/scraping, não existe "tier" de capacidade perdido
> dependendo da plataforma escolhida.

## Arquivos do bundle (overview)

```
product_docs/
  P01_knowledge.md ... P12_orchestration.md  <- SUBA os 12 como Knowledge/Files
  customgpt_instructions.json                <- config pronta para Custom GPT (name, description, instructions, conversation_starters)
  system_instruction.md                      <- a mesma instrução, pronta para colar em Claude/Gemini/qualquer IA
  README.md                                  <- visão geral + passo a passo resumido
  SETUP_chatgpt_projects.md                  <- guia de setup, ChatGPT
  SETUP_claude_projects.md                   <- guia de setup, Claude
  SETUP_gemini_gems.md                       <- guia de setup, Gemini
  SETUP_pt-br.md                             <- este arquivo
```

## Opção A -- ChatGPT (Projects free ou Custom GPT Plus)

Veja `SETUP_chatgpt_projects.md` para o passo a passo completo (cobre as
duas variantes: Project no plano free e Custom GPT no plano Plus).

Resumo:
1. Crie um Project (free) ou um Custom GPT (Plus) em chatgpt.com.
2. Cole as instructions: `system_instruction.md` (Project) ou o campo
   `instructions` de `customgpt_instructions.json` (Custom GPT).
3. Suba os 12 arquivos `P0X_*.md` como Knowledge/Files.
4. Nenhuma capability especial é necessária.
5. Teste com: `Documente a funcionalidade de exportação CSV do meu produto`.

## Opção B -- Claude Projects

Veja `SETUP_claude_projects.md` para o passo a passo completo.

Resumo:
1. Crie um Claude Project.
2. Cole `system_instruction.md` nas Project Instructions.
3. Suba os 12 arquivos `P0X_*.md` como Knowledge.
4. Fidelidade: `FULL` (nenhum MCP necessário).

## Opção C -- Gemini Gems

Veja `SETUP_gemini_gems.md` para o passo a passo completo.

Resumo:
1. Crie um Gem em gemini.google.com.
2. Cole `system_instruction.md` nas Instructions do Gem.
3. Suba os 12 arquivos `P0X_*.md` como Knowledge.
4. Fidelidade: `FULL` (nenhuma extension necessária).

## Capabilities recomendadas por runtime

| Capability | Custom GPT | ChatGPT Projects | Claude | Gemini |
|------------|-----------|-------------------|--------|--------|
| Web Browsing | não necessário | não necessário | não necessário | não necessário |
| Code Interpreter | opcional | opcional | opcional | opcional |
| Actions / MCP / Extensions | não usado | não usado | não usado | não usado |
| DALL-E / geração de imagem | não | não | não | não |

Este bundle é deliberadamente enxuto em termos de ferramentas: toda a
inteligência vem da instrução mais os 12 pilares carregados como
conhecimento, não de integrações externas. Isso o torna o mais simples de
configurar entre os bundles CEXAI e o mais portátil entre plataformas.

## Como o agente produz a documentação

1. Você descreve o produto ou funcionalidade na conversa, em texto livre.
2. O agente lê os 12 pilares carregados (o contrato de construção do kind
   `knowledge_card`: schema, template de saída, gates de qualidade,
   arquitetura, etc.) para saber exatamente que estrutura e nível de
   densidade produzir.
3. Ele produz um knowledge_card: frontmatter completo + corpo denso
   (tabelas, bullets, seções como Referência Rápida, Conceitos-Chave e
   Regras de Ouro), pronto para ser indexado num sistema de RAG.
4. Qualquer campo sem dado real vira `[fornecer: ...]` ou `[A CONFIRMAR]`
   -- nunca é inventado.

## Como usar (fluxo típico)

1. Diga o que quer documentar: `Documente o fluxo de onboarding do meu app`.
2. O agente pode perguntar (ou assumir, se for óbvio pelo contexto)
   detalhes de escopo: é uma funcionalidade, um produto inteiro, um
   endpoint de API?
3. Ele gera o knowledge_card completo, seguindo os 12 pilares como
   contrato de estrutura.
4. Revise os campos `[fornecer: ...]` e preencha com dados reais da sua
   marca antes de publicar ou indexar o resultado.

## Solução de problemas

- **"Ele inventou uma funcionalidade ou um número"** -> as salvaguardas do
  `system_instruction.md` proibem isso; reforce: "todo dado sem fonte real
  vira [fornecer: ...]".
- **Resposta genérica, sem a estrutura de um knowledge_card** -> confirme
  que os 12 arquivos `P0X_*.md` foram carregados como Knowledge -- sem
  eles, o agente não conhece o contrato de 12 pilares.
- **Respondeu em inglês** -> reforce o campo `Idioma: pt-BR` das
  instructions.
- **Quero trocar de plataforma** -> os 12 arquivos `P0X_*.md` mais o
  `system_instruction.md` são portáteis entre ChatGPT, Claude e Gemini;
  basta repetir o passo "Instructions + Knowledge" na nova plataforma.

## Compatibilidade

Este bundle segue a mesma estrutura de 12 pilares (`P01_knowledge.md` até
`P12_orchestration.md`) usada em todos os bundles de capacidade CEXAI --
qualquer um que você já tenha configurado antes (pesquisa, anúncio,
imagens, etc.) usa o mesmo fluxo de setup: Instructions + Knowledge dos 12
arquivos.
