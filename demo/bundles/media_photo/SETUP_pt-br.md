# SETUP -- media_photo (Mídia e Foto) -- guia combinado PT-BR

Guia geral do bundle `media_photo`. Para o passo a passo detalhado por
plataforma, veja os arquivos específicos:

- **ChatGPT (Projects ou Custom GPT)** -> `SETUP_chatgpt_projects.md`
- **Claude Projects** -> `SETUP_claude_projects.md`
- **Gemini Gems** -> `SETUP_gemini_gems.md`
- **Qualquer outra IA** -> este arquivo (seção "Opção D" abaixo)

> **Fidelidade deste bundle**: `full` em TODAS as plataformas. Diferente de
> bundles que dependem de scraping/Actions externas (ex.: agentes de
> pesquisa de mercado), o `media_photo` só produz um BRIEF de texto (um
> multimodal prompt) a partir da descrição do usuário -- não há ferramenta
> externa, chave de API, ou tier de coleta a perder ao trocar de plataforma.

## Arquivos do bundle (overview)

```
media_photo/
  P01_knowledge.md ... P12_orchestration.md   <- SUBA os 12 como Knowledge/Files
  customgpt_instructions.json                 <- COLE o campo "instructions" no Custom GPT
  system_instruction.md                       <- COLE como system prompt em qualquer IA
  SETUP_chatgpt_projects.md                   <- guia ChatGPT
  SETUP_claude_projects.md                    <- guia Claude
  SETUP_gemini_gems.md                        <- guia Gemini
  SETUP_pt-br.md                              <- este arquivo
  README.md                                   <- overview + passo a passo resumido
```

## Opção A -- ChatGPT (Custom GPT ou Projects)

Veja `SETUP_chatgpt_projects.md` para o passo a passo completo.

Resumo:
1. Custom GPT: Explore GPTs -> Create -> Configure. Cole o campo
   `instructions` de `customgpt_instructions.json` (também preenche `name`,
   `description` e `conversation_starters`).
   Projects: crie um Project e cole `system_instruction.md` nas Instructions.
2. Suba os 12 arquivos `P0X_*.md` como Knowledge/Files.
3. Nenhuma Action, nenhuma chave de API.
4. Fidelidade: `full`.

## Opção B -- Claude Projects

Veja `SETUP_claude_projects.md` para o passo a passo completo.

Resumo:
1. Crie um Claude Project.
2. Cole `system_instruction.md` nas Project instructions.
3. Suba os 12 arquivos de pilar em Project knowledge.
4. Nenhum MCP a configurar.
5. Fidelidade: `full`.

## Opção C -- Gemini Gems

Veja `SETUP_gemini_gems.md` para o passo a passo completo.

Resumo:
1. Crie um Gem.
2. Cole `system_instruction.md` nas Instructions do Gem.
3. Suba os 12 arquivos de pilar como Knowledge do Gem.
4. Nenhuma extension a habilitar.
5. Fidelidade: `full`.

## Opção D -- Qualquer outra IA (fallback universal)

Este bundle não exige nenhuma feature de plataforma específica (nem
Actions, nem MCP, nem extensions) -- qualquer assistente que aceite (1) um
system prompt colado e (2) arquivos de contexto/Knowledge funciona:

1. Cole o conteúdo de `system_instruction.md` como system prompt (ou
   equivalente: "custom instructions", "persona", "system message").
2. Se a plataforma aceitar upload de arquivos de contexto, suba os 12
   arquivos `P0X_*.md`. Se não aceitar, cole o conteúdo deles na própria
   conversa antes do primeiro pedido de brief.
3. Substitua os placeholders `[fornecer: ...]` pelos dados reais da sua
   marca.
4. Teste com: `Criar um brief de foto para <cena/assunto>`.

## O que este agente faz (e o que NÃO faz)

- **Faz**: produz um BRIEF de imagem/foto estruturado -- um artefato
  `multimodal_prompt` (nucleus N02, kind `multimodal_prompt`, pillar P03,
  verb `create`) com modalidades, descrição de cena e parâmetros técnicos.
- **NÃO faz**: não renderiza a imagem final. A renderização de mídia
  downstream (pipeline de ffmpeg / TTS) é uma etapa separada, fora do SDK,
  fora do escopo deste bundle (ver `system_instruction.md`, seção PAPEL).

## Como usar (fluxo típico)

1. Diga a cena/assunto: `Criar um brief de foto para <cena/assunto>`.
2. O agente confirma (ou pergunta) detalhes que faltarem na descrição.
3. Ele produz o artefato `multimodal_prompt`: modalidades envolvidas,
   descrição da cena, parâmetros técnicos (resolução, enquadramento, estilo,
   conforme aplicável).
4. Ele mantém a voz e os valores de marca configurados via os placeholders
   `[fornecer: ...]` preenchidos nas Instructions.
5. O brief resultante é o que você entrega para a etapa de renderização real
   (fora deste bundle).

## Solução de problemas

- **"Ele inventou o tom de voz da marca"** -> as GUARDRAILS proíbem isso.
  Reforce: sem dado real configurado, o campo deve aparecer como
  `[fornecer: ...]`, nunca uma suposição.
- **"Ele tentou gerar a imagem de verdade"** -> fora de escopo; reforce a
  seção PAPEL das Instructions (o agente produz o BRIEF, não a imagem).
- **Placeholders `[fornecer: ...]` aparecendo na saída** -> esperado até você
  preencher os dados reais da marca nas Instructions; não é um bug.
- **Quero uma plataforma que não está nesta lista** -> use a Opção D acima;
  o bundle não tem dependência de plataforma.

## Compatibilidade / manutenção

Este bundle segue a mesma arquitetura CEXAI dos demais bundles de
demonstração: 12 pilares (P01-P12) + `system_instruction.md` +
`customgpt_instructions.json` + `README.md`. Se os 12 arquivos de pilar
forem atualizados na fonte CEXAI, propague a mudança para cá e revise se
algum dos 4 guias de SETUP precisa de ajuste correspondente.
