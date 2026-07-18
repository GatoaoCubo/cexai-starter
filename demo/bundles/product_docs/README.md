# Bundle de capacidade CEXAI: Product Docs (`product_docs`)

O **contrato de 12 pilares** para o kind `knowledge_card`, mais a configuração de setup.
Nucleus N04 . kind `knowledge_card` . pillar P01.

Este é o formato CEXAI "12 ISO" -- um arquivo de especificação por pilar
(P01-P12), exatamente o bundle mostrado no vídeo do curso. Suba os 12
arquivos de pilar como Knowledge em qualquer assistente, cole a instrução, e
ele vira um agente Product Docs funcional.

## Conteúdo (19 arquivos)
- `P01_knowledge.md` ... `P12_orchestration.md` -- os 12 ISOs de pilar (o
  contrato de builder para este kind: uma especificação por pilar, P01-P12).
- `customgpt_instructions.json` -- a configuração do Custom GPT: name,
  description, a string `instructions` para colar, e os conversation
  starters.
- `system_instruction.md` -- a mesma instrução como um system prompt pronto
  para colar (para Claude Projects, Gemini ou qualquer modelo).
- `README.md` -- este arquivo.
- `SETUP_chatgpt_projects.md` -- guia de setup para ChatGPT Projects (plano
  free, sem Custom GPT).
- `SETUP_claude_projects.md` -- guia de setup para Claude Projects.
- `SETUP_gemini_gems.md` -- guia de setup para Gemini Gems.
- `SETUP_pt-br.md` -- guia combinado com a visão geral de todas as opções de
  runtime.

## Passo a passo: subir em qualquer IA

1. Escolha seu runtime (ChatGPT, Claude ou Gemini) e abra o guia
   `SETUP_*.md` correspondente para o passo a passo detalhado -- ou siga o
   resumo abaixo.
2. Crie um novo agente/projeto/GPT/Gem na plataforma escolhida.
3. Cole a instrução:
   - **ChatGPT (Custom GPT):** Explore GPTs -> Create -> Configure. Cole o
     campo `instructions` de `customgpt_instructions.json` na caixa de
     Instructions.
   - **ChatGPT (Projects, plano free), Claude (Project), Gemini (Gem) ou
     qualquer outra IA:** cole o conteúdo de `system_instruction.md` no
     campo de instruções/system prompt.
4. Suba os 12 arquivos `P0X_*.md` (P01_knowledge.md até P12_orchestration.md)
   como Knowledge/Files/contexto do projeto.
5. Confira as capabilities recomendadas: nenhuma capability especial é
   necessária (sem navegação web, sem code interpreter, sem geração de
   imagem) -- este agente trabalha somente com o conteúdo que você fornece
   e com os 12 pilares carregados.
6. Teste com um prompt como: `Documente a funcionalidade de exportação CSV
   do meu produto -- setup, uso e referência`.
7. Guias detalhados por runtime:
   - ChatGPT Projects (free) -> `SETUP_chatgpt_projects.md`
   - Claude Projects -> `SETUP_claude_projects.md`
   - Gemini Gems -> `SETUP_gemini_gems.md`
   - Visão geral combinada -> `SETUP_pt-br.md`

## Procedência / honestidade
Nunca fabricar: todo marcador `[fornecer: ...]` é um campo sem dado real --
preencha com a sua própria marca antes de usar. Os 12 ISOs de pilar são o
contrato de builder genérico e público para `knowledge_card` -- sem dado de
tenant algum.
