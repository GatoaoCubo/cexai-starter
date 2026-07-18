# SETUP -- Claude Projects

Setup do bundle `pesquisa_produto` em Claude Projects. Nenhuma Action,
chave de API, ou MCP é necessária -- é o formato "12 ISO" da CEXAI: 12
arquivos de pillar (P01-P12) que ensinam o Claude a estruturar a saída
como um `knowledge_card`, mais a instrução da capacidade. ~10 minutos.

## Pré-requisitos

- Conta Claude (Free, Pro, ou Team) com Projects habilitado.
- ZERO chaves de API ou setup de MCP necessários para este bundle.

## Passo a passo

### 1. Crie o Project

1. Acesse **claude.ai** -> **Projects** -> **+ Create project**.
2. Nome sugerido: `Pesquisa de Produto (pesquisa_produto)`.

### 2. Cole as Project Instructions

1. Abra o projeto -> **Project Instructions** (no painel lateral, ou em
   **Set custom instructions**).
2. Copie TODO o conteúdo de `system_instruction.md` deste bundle.
3. Cole nas Project Instructions.

### 3. Suba os 12 arquivos de pillar como Knowledge

Em **Project knowledge**, anexe os 12 arquivos deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

Claude Projects não tem limite de 20 arquivos (o limite é por tamanho
total do project knowledge) -- os 12 arquivos deste bundle cabem com folga.

### 4. Teste

Inicie uma conversa dentro do Project:

> `Pesquise carregador portátil 20000mAh -- preço de mercado, concorrentes, lacunas e palavras-chave`

O agente deve:
1. Confirmar o produto (e categoria/marketplaces, se relevante).
2. Pesquisar usando sua própria base de conhecimento e, se disponível na
   sua conta, busca na web.
3. Entregar um artifact `knowledge_card` estruturado -- frontmatter
   completo + corpo denso, seguindo o schema/template dos 12 pillars.
4. Marcar qualquer dado não confirmado como `[A CONFIRMAR: ...]` ou
   `[fornecer: ...]` -- nunca inventar número, nome, ou métrica.

## Vantagens do Claude Projects

| Aspecto | Custom GPT | Claude Projects |
|---------|-----------|-----------------|
| Project knowledge | limite de 20 arquivos | sem limite de arquivos (limite por tamanho total) |
| Contexto | menor | maior na maioria dos planos |
| Tool calls paralelas | sequenciais | nativamente paralelas via tool_use |
| Custo | Plus (Custom GPT) | Free/Pro/Team |

## Solução de problemas

- **"Ele inventou um preço ou concorrente"** -> reforce: "todo número
  precisa vir do seu conhecimento ou de busca real; sem confirmação, use
  `[A CONFIRMAR]`" -- já está nos GUARDRAILS de `system_instruction.md`,
  mas vale reforçar pontualmente na conversa.
- **A saída não parece um `knowledge_card`** -> confirme que os 12
  arquivos `P0X_*.md` foram anexados ao Project knowledge -- eles são o
  contrato de estrutura (schema, template, gates) que o Claude segue.
- **Quero pesquisa com scraper real de marketplace** -> este bundle é o
  formato de ensino "12 ISO"; um bundle de produção completo (com
  Actions/MCP para scraping real) é um pacote diferente e mais avançado.
