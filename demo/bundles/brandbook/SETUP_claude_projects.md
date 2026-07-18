# SETUP -- Claude Projects

Setup do bundle `brandbook` (Manual de Marca) em Claude Projects. ~10 minutos.
Sem Actions, sem MCP obrigatório -- só Project Instructions + Knowledge.

## Pré-requisitos

- Conta Claude (Free, Pro ou Team) com Projects habilitado.
- ZERO chaves de API necessárias.

## Passo a passo

### 1. Crie o Project

1. Acesse **claude.ai** -> **Projects** -> **+ Create project**.
2. Nome: `Manual de Marca (brandbook)`.

### 2. Cole as Project Instructions

1. Abra o projeto -> **Project Instructions** (painel lateral).
2. Copie TODO o conteúdo de `system_instruction.md` deste bundle (a primeira
   linha é um comentário HTML de proveniência -- pode manter ou remover,
   tanto faz para o funcionamento).
3. Cole nas Project Instructions.

### 3. Suba os 12 arquivos de Knowledge

Em **Knowledge** do projeto, suba os 12 arquivos deste bundle:

`P01_knowledge.md` ... `P12_orchestration.md`

Claude Projects não tem limite de 20 arquivos (o limite é por tamanho total
do Project) -- os 12 arquivos deste bundle juntos somam poucos KB, bem
dentro de qualquer limite.

### 4. (Opcional) Habilite busca na web

Se você quiser colar uma URL do site da marca em vez de texto/PDF:

1. Nas configurações do Project (ou do modelo), habilite **web search**
   se disponível no seu plano.
2. Sem isso, o agente pede que você cole o texto do site manualmente --
   funciona igualmente bem, só exige um passo a mais seu.

### 5. Teste

Em uma conversa do Project:

> `Monte o manual de marca para Café Aurora -- essência: cafeteria de bairro, aconchegante e artesanal`

O agente deve:
1. Confirmar `brand_name` e perguntar pelos campos opcionais que faltarem.
2. Produzir as 8 seções fixas (Identidade da Marca -> Faça e Não Faça).
3. Marcar com `[fornecer: ...]` qualquer campo sem dado real -- nunca
   inventar.

## Fidelidade declarada: full

Este bundle não tem tiers nem Actions para degradar -- a mesma lógica de
geração das 8 seções roda igual em Claude, ChatGPT ou Gemini. A única
variável entre runtimes é a qualidade de leitura de URL/PDF colados (via
web search nativo de cada plataforma), não a estrutura do manual de marca.

## Vantagens do Claude Projects vs Custom GPT

| Aspecto | Custom GPT | Claude Projects |
|---------|-----------|------------------|
| Limite de arquivos de Knowledge | 20 arquivos | sem limite por arquivo (limite é por tamanho total) |
| Janela de contexto | menor | maior -- útil se você colar um PDF de brandbook extenso como `brand_materials` |
| Necessário plano pago para criar | sim (Plus) | Projects funciona em planos free e pagos |
| Compartilhamento por link público | sim (Custom GPT) | limitado (Projects é mais privado/interno) |

## Como usar (fluxo típico)

1. Diga o nome da marca: `Monte o manual de marca para <nome da marca>`.
2. Cole a essência (1 frase) e qualquer material disponível (texto do site,
   paleta em hex, PDF colado como texto, descrição do logotipo).
3. Claude monta as 8 seções, preenchendo com dado real onde houver e
   `[fornecer: ...]` honesto onde não houver.
4. Peça ajustes seção por seção -- ex. "refaça a Persona da Marca com um
   tom mais informal" -- o agente regenera só aquela seção.

## Solução de problemas

- **"Ele inventou dado de marca"** -> reforce a regra Nunca-Fabricar:
  peça para ele substituir qualquer afirmação sem fonte por
  `[fornecer: ...]`.
- **Quer processar um PDF de brandbook existente** -> cole o texto extraído
  do PDF (ou anexe o PDF na conversa, se seu plano permitir upload de
  arquivo na conversa) como `brand_materials`.
- **Projeto ficou grande demais** -> os 12 arquivos deste bundle já são
  enxutos (poucos KB no total); se você anexar muitos materiais de marca
  adicionais, monitore o tamanho total do Project.
- **Quer as 8 seções em outro idioma** -> ajuste a linha `Idioma: pt-BR`
  em `system_instruction.md` antes de colar nas Project Instructions.
