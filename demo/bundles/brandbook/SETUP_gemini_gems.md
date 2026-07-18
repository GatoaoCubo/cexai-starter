# SETUP -- Gemini Gems

Setup do bundle `brandbook` (Manual de Marca) em Gemini Gems. ~5 minutos.
Sem Actions, sem chaves de API -- só Instructions + Knowledge.

## Pré-requisitos

- Conta Google + acesso a **gemini.google.com** com a funcionalidade Gems
  habilitada.
- ZERO chaves de API necessárias.

## Passo a passo

### 1. Crie o Gem

1. Acesse **gemini.google.com**.
2. Vá em **Gems** -> **+ Create new Gem**.
3. Nome: `Manual de Marca (brandbook)`.
4. Description: `Monta um manual de marca de 8 seções a partir de nome, essência, logotipo e paleta de cores.`

### 2. Cole as Instructions

1. Abra `system_instruction.md` deste bundle.
2. Copie TODO o conteúdo.
3. Cole no campo Instructions do Gem.

### 3. Suba a Knowledge

Em **Knowledge** do Gem, suba os 12 arquivos deste bundle:

`P01_knowledge.md` ... `P12_orchestration.md`

### 4. (Opcional) Configure extensions

Em **Extensions** do Gem:
- **Google Search** -- habilita o Gem a tentar ler uma URL de site da marca
  colada em `brand_materials`. Sem essa extension, peça ao usuário para
  colar o texto do site diretamente.

Nenhuma outra extension é necessária -- este bundle não usa Actions nem
integrações externas.

### 5. Teste

Em uma conversa do Gem:

> `Monte o manual de marca para Café Aurora -- essência: cafeteria de bairro, aconchegante e artesanal`

O Gem deve:
1. Confirmar `brand_name` e perguntar pelos campos opcionais.
2. Gerar as 8 seções fixas (Identidade da Marca -> Faça e Não Faça).
3. Emitir `[fornecer: ...]` honesto em qualquer campo sem dado -- nunca
   inventar cor, fonte, copy ou métrica.

## Fidelidade declarada: full

Este bundle não depende de Actions/tiers como outros bundles CEXAI (ex.:
pesquisa de mercado). A geração das 8 seções é idêntica em Gemini, ChatGPT
ou Claude -- a única diferença entre plataformas é o suporte a leitura de
URL colada (via Google Search aqui), não a estrutura do manual.

## Vantagens do Gemini vs outras plataformas

- **Janela de contexto grande** -- útil se você colar um brandbook antigo
  extenso ou um PDF longo como `brand_materials`.
- **Multimodal nativo** -- se você quiser que o Gem descreva um logotipo ou
  paleta a partir de uma imagem anexada, o Gemini lida bem com isso
  diretamente na conversa (mesmo sem o hook estruturado `media_requests` do
  CEXAI interno -- veja a nota de portabilidade em `P04_tools.md`).

## Limitações

- **Sem Actions nativas** -- não aplicável a este bundle de qualquer forma
  (ele não usa Actions em nenhum runtime).
- **Extension de busca é best-effort** para ler URLs -- sites com proteção
  anti-bot podem falhar; cole o texto manualmente nesse caso.

## Como usar (fluxo típico)

1. Diga o nome da marca: `Monte o manual de marca para <nome da marca>`.
2. Cole a essência e qualquer material disponível (texto, paleta em hex,
   descrição do logotipo, ou anexe uma imagem do logotipo na conversa).
3. O Gem monta as 8 seções, com `[fornecer: ...]` nos campos sem dado.
4. Peça revisões seção por seção conforme necessário.

## Solução de problemas

- **"Ele inventou uma afirmação de marca"** -> reforce a regra
  Nunca-Fabricar do `system_instruction.md`: peça para substituir por
  `[fornecer: ...]`.
- **Google Search não lê o site da marca** -> esperado em sites com
  proteção anti-bot; cole o texto manualmente.
- **Quer trocar de plataforma depois** -> as mesmas Instructions e os
  mesmos 12 arquivos funcionam em ChatGPT (`SETUP_chatgpt_projects.md`) e
  Claude (`SETUP_claude_projects.md`) sem nenhuma adaptação.
