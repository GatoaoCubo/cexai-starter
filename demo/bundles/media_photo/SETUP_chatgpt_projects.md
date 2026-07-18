# SETUP -- ChatGPT Projects

Setup do bundle `media_photo` (agente Mídia e Foto) em ChatGPT Projects.
Sem Actions, sem chaves de API -- é um agente 100% colar-e-usar (cole o texto, suba os arquivos, pronto). ~5 minutos.

## Pré-requisitos

- Conta ChatGPT (o recurso Projects está disponível em planos pagos; confira
  a disponibilidade atual na sua conta).
- ZERO chaves de API necessárias -- este agente não chama nenhuma ferramenta
  externa; ele apenas produz um BRIEF de imagem/foto em texto.

## Passo a passo

### 1. Crie o Project

1. Acesse **chatgpt.com** -> menu lateral -> **Projects** -> **+ New project**.
2. Nome sugerido: `Mídia e Foto (media_photo)`.

### 2. Cole as Instructions

1. Abra o projeto -> **Instructions** (ícone de engrenagem).
2. Copie o conteúdo de `system_instruction.md` (ou o campo `instructions` de
   `customgpt_instructions.json` -- são o mesmo texto).
3. Cole nas Instructions do projeto.
4. Substitua os placeholders `[fornecer: ...]` pelos dados reais da sua marca
   (nome, tom de voz, valores) antes de publicar.

### 3. Suba os 12 arquivos de Knowledge

Em **Files** do projeto, suba os 12 arquivos de pilar deste bundle:

- `P01_knowledge.md` ... `P12_orchestration.md`

Todos os 12 -- este bundle não tem uma versão reduzida; os 12 pilares juntos
formam o contrato completo do builder para `multimodal_prompt`.

### 4. Capabilities

Este agente não precisa de nenhuma capability especial:
- **Web browsing**: não necessário (o agente não pesquisa nada ao vivo).
- **Code interpreter**: não necessário.
- **DALL-E / geração de imagem**: fora de escopo -- o agente entrega o BRIEF
  de texto (o multimodal prompt); a renderização real da imagem é uma etapa
  separada, fora deste bundle (ver `system_instruction.md`, seção PAPEL).

### 5. Teste

Inicie uma conversa dentro do project:

> `Criar um brief de foto para <cena/assunto>`

O agente deve:
1. Confirmar (ou perguntar) a cena/assunto da foto.
2. Produzir um artefato `multimodal_prompt` estruturado: modalidades,
   descrição da cena, parâmetros técnicos.
3. Manter a voz e os valores da marca configurados nas Instructions.
4. Nunca inventar dado de marca que não foi fornecido -- em vez disso, manter
   o placeholder `[fornecer: ...]` explícito.

## Fidelidade declarada: FULL

| Por quê | Detalhe |
|-------|---------|
| Sem Actions no design original | O agente só produz um brief em texto -- não há chamada de ferramenta externa a perder |
| Sem TIER de coleta de dados | Diferente de agentes de pesquisa, este não coleta preço/concorrente; não há degradação por falta de Actions |
| 12/12 pilares presentes | Nenhum pilar foi dobrado ou removido para caber no formato Projects |

Diferente de bundles que dependem de scraping/Actions (ex.: agentes de
pesquisa de mercado), o `media_photo` roda em fidelidade **full** em
qualquer plataforma -- inclusive na variante mais simples (Projects), porque
toda a capacidade do agente já está contida no texto das Instructions + nos
12 arquivos de Knowledge.

## Solução de problemas

- **"Ele pediu para eu subir uma imagem"** -> não deveria; o agente produz um
  BRIEF (texto) a partir de uma descrição, não analisa imagens de entrada.
  Se isso acontecer, reforce a seção PAPEL das Instructions.
- **"Ele inventou o tom de voz da marca"** -> reforce o guardrail: sem dado
  real, o campo deve aparecer como `[fornecer: ...]`, nunca uma suposição.
- **Quero usar Custom GPT em vez de Projects** -> use
  `customgpt_instructions.json` (campos `name`, `description`,
  `instructions`, `conversation_starters` prontos para colar na tela de
  configuração do Custom GPT) e suba os mesmos 12 arquivos como Knowledge.
- **Quero a versão combinada com todas as plataformas** -> veja `SETUP_pt-br.md`.
