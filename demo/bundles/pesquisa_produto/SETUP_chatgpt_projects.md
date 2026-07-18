# SETUP -- ChatGPT (Custom GPT e Projects)

Setup do bundle `pesquisa_produto` no ChatGPT. Este bundle é o formato
"12 ISO" da CEXAI -- 12 arquivos de pillar (P01-P12) + a instrução da
capacidade -- e funciona tanto como um Custom GPT (ChatGPT Plus) quanto
dentro de um ChatGPT Project (qualquer plano). Nenhuma Action ou chave de
API é necessária: o agente usa o navegador/pesquisa nativo do modelo (se
habilitado) e a sua própria base de conhecimento para pesquisar o produto,
e usa os 12 arquivos de pillar só para estruturar a saída. ~10 minutos.

## Pré-requisitos

- Conta ChatGPT (Custom GPT exige ChatGPT Plus/Team; Projects funciona no
  plano free).
- ZERO chaves de API necessárias.

## Opção A -- Custom GPT (recomendado se você tem ChatGPT Plus)

### 1. Crie o GPT

1. Acesse **chatgpt.com** -> **Explore GPTs** -> **Create** -> aba **Configure**.
2. Nome sugerido: cole o campo `name` de `customgpt_instructions.json`
   (ou substitua `[fornecer: nome da marca]` pelo nome da sua marca antes).

### 2. Cole as Instructions

1. Abra `customgpt_instructions.json` neste bundle.
2. Copie o valor do campo `instructions` (a string toda, já com as quebras
   de linha).
3. Cole na caixa **Instructions** do GPT.
4. (Opcional) Cole o campo `description` na descrição do GPT, e o item de
   `conversation_starters` como um dos Conversation starters.

### 3. Suba os 12 arquivos como Knowledge

Em **Knowledge**, suba os 12 arquivos `P0X_*.md` deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

### 4. Capabilities

- **Web Browsing**: habilite se disponível -- melhora muito a qualidade da
  pesquisa de preço/concorrentes (sem isso, o modelo depende só do que já
  sabe, que pode estar desatualizado).
- **Code Interpreter**: opcional, útil para consolidar tabelas de benchmark.
- **DALL-E**: não é necessário para esta capacidade.

### 5. Teste

Inicie uma conversa com o GPT:

> `Pesquise carregador portátil 20000mAh -- preço de mercado, concorrentes, lacunas e palavras-chave`

O agente deve:
1. Confirmar o produto e, se fizer sentido, perguntar a categoria/marketplaces.
2. Pesquisar (via Web Browsing, se habilitado, ou seu próprio conhecimento).
3. Entregar um artifact `knowledge_card` estruturado nos moldes dos 12
   pillars (frontmatter + corpo denso, tabelas, referências).
4. Marcar qualquer dado que não conseguiu confirmar como `[A CONFIRMAR: ...]`
   ou `[fornecer: ...]` -- nunca inventar preço, nome de concorrente, ou métrica.

## Opção B -- ChatGPT Projects (funciona no plano free)

### 1. Crie o Project

1. Acesse **chatgpt.com** -> menu lateral -> **Projects** -> **+ New project**.
2. Nome sugerido: `Pesquisa de Produto (pesquisa_produto)`.

### 2. Cole as Instructions

1. Abra o projeto -> **Instructions** (ícone de engrenagem).
2. Cole o conteúdo de `system_instruction.md` deste bundle.

### 3. Suba os 12 arquivos em Files

Em **Files** do projeto, suba os 12 arquivos `P0X_*.md` deste bundle.

### 4. Modelo

Selecione um modelo com **web search/browsing** habilitado (ex.: GPT-4o)
para melhorar a qualidade da pesquisa de mercado.

### 5. Teste

Dentro do projeto:

> `Pesquise carregador portátil 20000mAh -- preço de mercado, concorrentes, lacunas e palavras-chave`

Mesmo comportamento esperado da Opção A.

## Fidelidade declarada

Este bundle é o contrato de **estrutura e disciplina de saída** (os 12
ISOs do kind `knowledge_card`) -- ele NÃO embute um scraper de marketplace
próprio nem uma base de preços em tempo real. A qualidade da pesquisa em
si depende do que o modelo já sabe e/ou do que ele consegue navegar. O
valor deste bundle é garantir que a saída seja **densa, estruturada, e
honesta** (nunca inventa dado que não tem), não que ele tenha acesso a
dado privilegiado de mercado.

## Solução de problemas

- **"Ele inventou um preço ou concorrente"** -> reforce nas Instructions:
  "todo número precisa de origem (busca/conhecimento do modelo); sem dado
  confirmado, use `[A CONFIRMAR]`". Isso já está nos GUARDRAILS da
  instrução, mas modelos podem precisar de reforço pontual.
- **Sem Web Browsing, a pesquisa fica genérica** -> habilite Web Browsing
  (Custom GPT) ou escolha um modelo com busca (Projects); sem isso, o
  agente usa só conhecimento de treinamento, que pode estar desatualizado.
- **A saída não parece um `knowledge_card`** -> confirme que os 12
  arquivos `P0X_*.md` foram todos enviados como Knowledge/Files -- eles
  são o contrato de estrutura (schema, template, gates) que o agente segue.
- **Quero uma pesquisa com scraper real de marketplace** -> esse é um
  bundle diferente (mais avançado, com Actions/TIERs); este aqui é o
  formato de ensino "12 ISO" do curso.
