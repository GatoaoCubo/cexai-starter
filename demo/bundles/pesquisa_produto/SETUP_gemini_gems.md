# SETUP -- Gemini Gems

Setup do bundle `pesquisa_produto` em Gemini Gems. Formato "12 ISO" da
CEXAI -- 12 arquivos de pillar (P01-P12) + a instrução da capacidade.
Nenhuma Action ou chave de API é necessária. ~5 minutos.

## Pré-requisitos

- Conta Google + acesso a **gemini.google.com**.
- (Opcional) a extensão **Google Search** habilitada no Gem, para melhorar
  a pesquisa de mercado com dado mais atual.

## Passo a passo

### 1. Crie o Gem

1. Acesse **gemini.google.com**.
2. Vá em **Gems** -> **+ Create new Gem** (ou **Gem manager**).
3. Nome sugerido: `Pesquisa de Produto (pesquisa_produto)`.
4. Description: cole (ou adapte) o campo `description` de
   `customgpt_instructions.json`.

### 2. Cole as Instructions

1. Abra `system_instruction.md` deste bundle.
2. Copie TODO o conteúdo.
3. Cole no campo **Instructions** do Gem.

### 3. Suba os 12 arquivos como Knowledge do Gem

Em **Knowledge** do Gem, suba os 12 arquivos deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

### 4. (Opcional) Habilite extensions

Em **Extensions** do Gem:
- **Google Search** -- deixa a pesquisa de mercado mais atual (o Gem pode
  buscar preço/concorrentes em vez de depender só do conhecimento de
  treinamento).

### 5. Teste

Em uma conversa com o Gem:

> `Pesquise carregador portátil 20000mAh -- preço de mercado, concorrentes, lacunas e palavras-chave`

O Gem deve:
1. Confirmar o produto (e categoria/marketplaces, se relevante).
2. Pesquisar via Google Search (se habilitado) ou seu próprio conhecimento.
3. Entregar um artifact `knowledge_card` estruturado conforme os 12
   pillars deste bundle (frontmatter + corpo denso + tabelas).
4. Marcar qualquer dado não confirmado como `[A CONFIRMAR: ...]` ou
   `[fornecer: ...]` -- nunca inventar número, nome, ou métrica.

## Vantagens do Gemini

- **Janela de contexto grande** (>1M tokens em modelos recentes) -- cabem
  os 12 arquivos de pillar com folga, mesmo em conversas longas.
- **Google Search nativo** ajuda bastante na pesquisa de preço/mercado se
  a extensão estiver habilitada.
- **Multi-modal nativo**: se você quiser analisar uma imagem de um
  concorrente (ex.: foto de um anúncio), pode anexar a imagem no chat.

## Limitações

- **Sem Actions/OpenAPI nativas** neste runtime -- este bundle já não usa
  Actions, então isso não é uma limitação prática aqui.
- **MCP não é suportado** em Gemini Gems no momento -- também não é
  necessário para este bundle.

## Solução de problemas

- **"Ele inventou um preço ou concorrente"** -> reforce: "todo número
  precisa vir de busca real ou do seu conhecimento; sem confirmação, use
  `[A CONFIRMAR]`" -- já está nos GUARDRAILS de `system_instruction.md`.
- **Busca não retorna nada específico para o produto** -> tente uma
  descrição mais específica do produto (com marca, tamanho, ou atributo)
  em vez de um termo muito genérico.
- **A saída não parece um `knowledge_card`** -> confirme que os 12
  arquivos `P0X_*.md` foram enviados como Knowledge do Gem.
- **Quero pesquisa com scraper real de marketplace** -> este bundle é o
  formato de ensino "12 ISO"; um bundle de produção completo é um pacote
  diferente e mais avançado.
