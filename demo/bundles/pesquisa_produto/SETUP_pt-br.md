# SETUP -- pesquisa_produto -- guia combinado PT-BR

Guia geral do bundle `pesquisa_produto`. Para o passo a passo detalhado
por plataforma, veja os arquivos específicos:

- **ChatGPT (Custom GPT ou Projects)** -> `SETUP_chatgpt_projects.md`
- **Claude Projects** -> `SETUP_claude_projects.md`
- **Gemini Gems** -> `SETUP_gemini_gems.md`

> **O que é este bundle**: o formato "12 ISO" da CEXAI para o kind
> `knowledge_card` -- um arquivo de especificação por pillar (P01-P12),
> mais a instrução da capacidade `pesquisa_produto` (pesquisa de mercado
> pelos marketplaces ML/Shopee/Amazon/Magalu, virando um card de 30
> campos pronto para virar anúncio). Sem Actions, sem chave de API, sem
> MCP -- só os 12 arquivos + uma instrução para colar.

## Arquivos do bundle (overview)

```
pesquisa_produto/
  P01_knowledge.md ... P12_orchestration.md  <- os 12 ISOs de pillar (SUBA como Knowledge/Files)
  customgpt_instructions.json                <- config do Custom GPT (nome, descrição, instructions)
  system_instruction.md                      <- a mesma instrução em formato de prompt de sistema
  README.md                                  <- visão geral + índice de arquivos
  SETUP_chatgpt_projects.md                  <- passo a passo ChatGPT (este arquivo aponta pra ele)
  SETUP_claude_projects.md                   <- passo a passo Claude Projects
  SETUP_gemini_gems.md                       <- passo a passo Gemini Gems
  SETUP_pt-br.md                             <- este arquivo (guia combinado)
```

## Opção A -- ChatGPT (Custom GPT ou Projects)

Veja `SETUP_chatgpt_projects.md` para o passo a passo completo.

Resumo:
1. Custom GPT: Explore GPTs -> Create -> Configure. Cole o campo
   `instructions` de `customgpt_instructions.json`. Suba os 12 arquivos
   `P0X_*.md` como Knowledge.
2. Ou ChatGPT Projects: crie um Project, cole `system_instruction.md` nas
   Instructions do projeto, suba os 12 arquivos como Files.
3. Habilite Web Browsing (ou escolha um modelo com busca) para melhorar a
   qualidade da pesquisa de mercado.
4. Teste com: `Pesquise carregador portátil 20000mAh -- preço de
   mercado, concorrentes, lacunas e palavras-chave`.

## Opção B -- Claude Projects

Veja `SETUP_claude_projects.md` para o passo a passo completo.

Resumo:
1. Crie um Project em claude.ai.
2. Cole `system_instruction.md` nas Project Instructions.
3. Anexe os 12 arquivos `P0X_*.md` ao project knowledge.
4. Teste com o mesmo prompt de exemplo acima.

## Opção C -- Gemini Gems

Veja `SETUP_gemini_gems.md` para o passo a passo completo.

Resumo:
1. Crie um Gem em gemini.google.com.
2. Cole `system_instruction.md` nas Instructions do Gem.
3. Suba os 12 arquivos `P0X_*.md` como knowledge do Gem.
4. (Opcional) habilite a extensão Google Search.
5. Teste com o mesmo prompt de exemplo acima.

## Opção D -- Qualquer outra IA

Qualquer assistente que aceite (a) um system prompt/instruction em texto
e (b) anexos de arquivo como contexto funciona:
1. Cole `system_instruction.md` como o prompt de sistema (ou no campo
   equivalente da plataforma).
2. Anexe os 12 arquivos `P0X_*.md` como contexto/conhecimento, se a
   plataforma suportar upload de arquivos. Se não suportar, cole o
   conteúdo dos 12 arquivos direto na conversa antes do primeiro pedido.

## Capabilities recomendadas por plataforma

| Capability | Custom GPT | ChatGPT Projects | Claude Projects | Gemini Gems |
|------------|-----------|-------------------|------------------|-------------|
| Busca/Web Browsing | opcional, recomendado | modelo com web habilitado | nativo em alguns planos | extensão Google Search |
| Code Interpreter | opcional | opcional | não aplicável | parcial |
| Actions/plugins | não usado por este bundle | não usado | não usado | não usado |
| Limite de arquivos de conhecimento | 20 | 20 | sem limite de arquivos (limite por tamanho) | varia |

## Como o agente pesquisa o produto (honestidade)

Este bundle NÃO inclui um scraper de marketplace próprio, nem uma base de
preços em tempo real, nem um sistema de TIERs -- ele é o contrato de **12
pillars** (schema, template, gates de qualidade) que ensina o modelo a
estruturar a saída como um `knowledge_card` denso e honesto. A pesquisa em
si depende de:

1. O conhecimento próprio do modelo (pode estar desatualizado).
2. Busca na web nativa da plataforma, quando disponível e habilitada.

Em ambos os casos, os guardrails da instrução (ver `system_instruction.md`,
seção GUARDRAILS) proíbem fabricar preço, nome de concorrente, ou métrica
-- qualquer dado não confirmado deve virar um placeholder explícito
(`[A CONFIRMAR: ...]` ou `[fornecer: ...]`), nunca um número inventado.

## Como usar (fluxo típico)

1. Diga o produto: `Pesquise carregador portátil 20000mAh -- preço de
   mercado, concorrentes, lacunas e palavras-chave`.
2. O agente confirma o produto (e categoria/marketplaces, se relevante).
3. Ele pesquisa (via busca nativa, se disponível, ou conhecimento próprio).
4. Ele entrega o artifact `knowledge_card`: frontmatter completo + corpo
   denso, seguindo a estrutura definida nos 12 pillars deste bundle.
5. Qualquer dado sem confirmação aparece como `[A CONFIRMAR]` -- nunca
   como número inventado.

## Solução de problemas

- **"Ele inventou preços ou concorrentes"** -> reforce na conversa: "todo
  número precisa de origem real (busca ou conhecimento verificável); sem
  isso, use `[A CONFIRMAR]`". Já está nos GUARDRAILS, mas reforçar ajuda.
- **A pesquisa parece genérica/desatualizada** -> habilite busca na web
  na plataforma escolhida (Web Browsing no Custom GPT, modelo com web em
  Projects, Google Search no Gemini). Sem isso, o modelo usa só o que já
  sabe.
- **A saída não parece um `knowledge_card`** -> confirme que os 12
  arquivos `P0X_*.md` foram todos enviados como Knowledge/Files/anexo --
  eles são o contrato de estrutura que o agente segue.
- **Quero um agente com scraper real de marketplace e TIERs** -> este
  bundle é o formato de ensino "12 ISO" do curso CEXAI; bundles de
  produção mais avançados (com Actions/MCP para scraping real) existem
  como pacotes separados.
