# SETUP -- Gemini Gems

Setup do bundle **Construtor de Email** (`email_builder`) em Gemini Gems.
Sem Actions, sem chave de API, sem extension necessária. ~5 minutos.

## Pré-requisitos

- Conta Google com acesso a **gemini.google.com**.
- ZERO integrações externas necessárias.

## Passo a passo

### 1. Crie o Gem

1. Acesse **gemini.google.com**.
2. Vá em **Gems** -> **+ Create new Gem**.
3. Nome: `Construtor de Email (email_builder)`.
4. Descrição: `Gera prompt templates de email HTML responsivo -- assunto, preheader e corpo, alinhados à marca.`

### 2. Cole as Instructions

1. Abra `system_instruction.md` deste bundle.
2. Copie TODO o conteúdo.
3. Cole no campo Instructions do Gem.

### 3. Suba a Knowledge

Em **Knowledge** do Gem, suba os 12 arquivos de pillar:

- `P01_knowledge.md` ... `P12_orchestration.md`

Gemini Gems aceita múltiplos arquivos de knowledge; os 12 arquivos de texto
deste bundle ficam bem abaixo de qualquer limite de tamanho.

### 4. Capabilities

Nenhuma extension é necessária. Este agente não busca dado na web nem
executa código -- ele produz texto (o prompt template de email) a partir da
sua base de conhecimento. Deixe as Extensions desligadas, se preferir manter
o Gem mais enxuto.

### 5. Preencha a sua marca

Antes do primeiro teste, edite as Instructions e substitua os marcadores
`[fornecer: ...]`:
- `[fornecer: nome da marca]` -> o nome do seu negócio.
- `[fornecer: tom de voz da marca]` -> ex.: "acolhedor, objetivo, com bom humor".
- `[fornecer: valores da marca]` -> ex.: "proximidade com o cliente, transparência".

### 6. Teste

Em uma conversa do Gem:

> `Escreva um email de marketing para o lançamento do produto X -- assunto, preheader, corpo`

O Gem deve:
1. Entender a campanha/público a partir do seu pedido.
2. Entregar um **prompt template** de email (com slots de variável), não um
   email já finalizado.
3. Cobrir linhas de assunto (com variações), preheader e blocos de corpo.
4. Marcar com `[fornecer: ...]` qualquer dado sem confirmação real, em vez
   de inventar.

## Fidelidade declarada: FULL

Este bundle não depende de Actions nem de tiers de coleta de dado externo --
os mesmos 12 pillars usados no Custom GPT e no Claude Project rodam aqui,
com o mesmo comportamento.

## Vantagens do Gemini para este bundle

- **Janela de contexto grande** (mais de 1M tokens nos modelos recentes) --
  útil se você quiser anexar muitos exemplos de emails anteriores como
  knowledge extra.
- **Multi-modal nativo**: se você quiser que o Gem avalie o visual de um
  email já montado (print de tela, mockup), pode anexar a imagem direto na
  conversa.
- **Zero configuração de integração**: como este agente não usa Actions,
  Gemini Gems é tão completo quanto ChatGPT ou Claude para este caso de uso.

## Como usar (fluxo típico)

1. Diga a campanha: `Preciso de um email para recuperação de carrinho abandonado`.
2. O Gem gera o prompt template: variações de assunto, preheader, estrutura
   de corpo (saudação, corpo principal, CTA, rodapé), com os campos
   variáveis explícitos.
3. Você preenche os `{{slots}}` com os dados reais da campanha (ou pede ao
   próprio Gem para renderizar um exemplo preenchido).
4. Você leva o template renderizado para a sua ferramenta de envio de email.

## Solução de problemas

- **"Ele inventou um dado (preço, prazo, nome de produto)"** -> reforce:
  "nunca fabrique fatos; sem dado real, emita `[fornecer: ...]`".
- **Resposta veio em inglês** -> confirme que colou `system_instruction.md`
  completo (ele já fixa `Idioma: pt-BR`) e peça explicitamente "responda em
  português do Brasil".
- **Quer só um email pronto, não um template** -> peça: "renderize um
  exemplo completo do template acima, preenchido para <produto/campanha
  específica>".
- **Upload de knowledge falhou** -> confirme que está subindo os arquivos
  `.md` (texto puro); Gemini Gems não precisa de nenhuma conversão especial
  para este bundle.
