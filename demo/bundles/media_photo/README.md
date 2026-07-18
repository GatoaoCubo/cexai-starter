# Bundle de capacidade CEXAI: Mídia e Foto (`media_photo`)

O **contrato de 12 pilares** para o kind `multimodal_prompt`, mais a configuração de setup.
Nucleus N02 . kind `multimodal_prompt` . pillar P03.

Este é o formato "12 ISO" da CEXAI -- um arquivo de especificação por pilar
(P01-P12), exatamente o bundle mostrado no vídeo do curso. Suba os 12
arquivos de pilar como Knowledge em qualquer assistente, cole a instrução, e
ele vira um agente de Mídia e Foto funcional.

## Conteúdo (19 arquivos)
- `P01_knowledge.md` ... `P12_orchestration.md` -- os 12 ISOs de pilar (o
  contrato do builder para este kind: uma especificação por pilar, P01-P12).
- `customgpt_instructions.json` -- a config de Custom GPT: nome, descrição,
  a string `instructions` para colar, e os conversation starters.
- `system_instruction.md` -- a mesma instrução como system prompt pronto
  para colar (para Claude Projects, Gemini Gems ou qualquer modelo).
- `SETUP_chatgpt_projects.md` -- passo a passo para ChatGPT (Projects e
  Custom GPT).
- `SETUP_claude_projects.md` -- passo a passo para Claude Projects.
- `SETUP_gemini_gems.md` -- passo a passo para Gemini Gems.
- `SETUP_pt-br.md` -- guia combinado (todas as plataformas + "qualquer IA").
- `README.md` -- este arquivo.

## Upload -- passo a passo (qualquer IA)

1. **Escolha a plataforma** e o guia de setup correspondente:
   - ChatGPT (Custom GPT ou Projects) -> `SETUP_chatgpt_projects.md`
   - Claude (Projects) -> `SETUP_claude_projects.md`
   - Gemini (Gems) -> `SETUP_gemini_gems.md`
   - Qualquer outra IA -> `SETUP_pt-br.md` (fallback universal)
2. **Suba os 12 arquivos de pilar** (`P01_knowledge.md` ... `P12_orchestration.md`)
   como Knowledge / Files / base de conhecimento da plataforma escolhida.
3. **Cole a instrução**:
   - Custom GPT: cole o campo `instructions` de `customgpt_instructions.json`
     (o mesmo arquivo já traz `name`, `description` e `conversation_starters`
     prontos para os campos correspondentes).
   - Qualquer outra plataforma (Claude, Gemini, Projects, ou qualquer IA):
     cole o conteúdo de `system_instruction.md` como system prompt.
4. **Preencha os placeholders** `[fornecer: ...]` com os dados reais da sua
   marca (nome, tom de voz, valores) antes de publicar.
5. **Teste**: peça "Criar um brief de foto para <cena/assunto>" e confira se
   o agente devolve um brief de imagem/foto estruturado (um multimodal
   prompt), sem inventar dados de marca que não foram fornecidos.

## Upload (3 formas resumidas)
- **ChatGPT (Custom GPT):** Explore GPTs -> Create -> Configure. Suba os
  12 arquivos `P0X_*.md` como Knowledge. Cole o campo `instructions` de
  `customgpt_instructions.json` na caixa de Instructions.
- **Claude (Project):** cole `system_instruction.md` nas Custom
  instructions; anexe os 12 arquivos de pilar ao project knowledge.
- **Qualquer IA:** cole `system_instruction.md` como system prompt.

## Proveniência / honestidade
Nunca fabricar: todo marcador `[fornecer: ...]` é um campo sem entrada real
-- preencha com os dados da sua marca antes de usar. Os 12 ISOs de pilar são
o contrato de builder genérico e público para `multimodal_prompt` -- sem
dado de tenant.
