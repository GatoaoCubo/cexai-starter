# Bundle de capability CEXAI: Marketplace Listing (Channel Projection) (`marketplace_listing`)

O **contrato de 12 pilares** para o kind `marketplace_listing`, mais a
configuração de setup pronta para qualquer assistente de IA.
Nucleus N06 . kind `marketplace_listing` . pillar P05.

Este é o formato "12 ISO" do CEXAI -- um arquivo de especificação por pilar
(P01-P12), exatamente o bundle mostrado no vídeo do curso. Suba os 12
arquivos de pilar como Knowledge em qualquer assistente, cole a instrução,
e ele vira um agente Marketplace Listing (Channel Projection) funcional:
você descreve o produto, ele devolve o anúncio pronto para o Mercado Livre
+ um relatório honesto de prontidão (PUBLISH-READY ou NOT-READY).

## Conteúdo (19 arquivos)

### Os 12 pilares (o contrato do builder)
- `P01_knowledge.md` -- conhecimento de domínio: mapeamento de campos G1->G2, vocabulário de condição.
- `P02_model.md` -- identidade do builder (persona, capacidades, regras).
- `P03_prompt.md` -- o processo pesquisar > compor > validar.
- `P04_tools.md` -- inventário de ferramentas + referências de runtime.
- `P05_output.md` -- o template exato de uma instância (frontmatter + 6 seções).
- `P06_schema.md` -- a fonte única da verdade: campos, seções e payload embutido.
- `P07_evals.md` -- os gates de qualidade (HARD + SOFT) e as ações por score.
- `P08_architecture.md` -- onde este kind se encaixa na arquitetura CEXAI.
- `P09_config.md` -- os parâmetros de construção (canal, moeda, limiar de aprovação).
- `P10_memory.md` -- padrões aprendidos + falhas recorrentes.
- `P11_feedback.md` -- sinais de recompensa e de regressão.
- `P12_orchestration.md` -- como a construção é despachada + o caminho de runtime real.

### Configuração pronta para uso
- `customgpt_instructions.json` -- a config de Custom GPT: nome, descrição,
  a string de `instructions` para colar, e os conversation starters.
- `system_instruction.md` -- a mesma instrução em formato de system prompt
  pronto para colar (Claude Projects, Gemini Gems, ou qualquer modelo).

### Guias de setup por plataforma
- `SETUP_chatgpt_projects.md` -- passo a passo no ChatGPT (Projects, plano
  free, ou Custom GPT, plano Plus).
- `SETUP_claude_projects.md` -- passo a passo no Claude Projects.
- `SETUP_gemini_gems.md` -- passo a passo no Gemini Gems.
- `SETUP_pt-br.md` -- guia combinado: visão geral + as 3 plataformas acima
  + o caminho "qualquer IA" + solução de problemas.

### Este arquivo
- `README.md` -- este arquivo.

## Como subir (passo a passo, em qualquer IA)

1. **Escolha sua plataforma** e abra o guia correspondente:
   - ChatGPT -> `SETUP_chatgpt_projects.md`
   - Claude -> `SETUP_claude_projects.md`
   - Gemini -> `SETUP_gemini_gems.md`
   - Qualquer outra IA (ou visão geral combinada) -> `SETUP_pt-br.md`
2. **Cole a instrução**: copie o conteúdo de `system_instruction.md` (ou o
   campo `instructions` de `customgpt_instructions.json`, no caso de
   Custom GPT) no campo de instruções/system prompt da plataforma.
3. **Suba os 12 arquivos de pilar** (`P01_knowledge.md` ...
   `P12_orchestration.md`) como Knowledge/Files/contexto do assistente.
4. **Preencha a marca**: troque cada placeholder `[fornecer: ...]` pelo
   nome, tom de voz e valores reais da sua marca.
5. **Teste** com um prompt como:
   `Mapeie uma cafeteira elétrica 110V para um anúncio no Mercado Livre -- título, preço, categoria, prontidão`
6. O agente devolve o payload ML (título, preço, categoria, condição,
   atributos, fotos, descrição) + o veredito de prontidão -- nunca publica
   sozinho; a publicação real continua sob seu controle.

Resumo rápido por plataforma (detalhe completo em cada `SETUP_*.md`):

| Plataforma | Onde colar a instrução | Onde subir os 12 arquivos |
|---|---|---|
| ChatGPT (Custom GPT) | aba Configure -> Instructions (campo `instructions` do JSON) | Knowledge |
| ChatGPT (Projects) | Instructions do projeto | Files |
| Claude (Project) | Project Instructions | Project Knowledge |
| Gemini (Gem) | Instructions do Gem | Knowledge do Gem |
| Qualquer outra IA | system prompt | anexo/contexto da conversa |

## Procedência / honestidade

Nunca-fabricar: qualquer marcador `[fornecer: ...]` é um campo sem dado
real de entrada -- preencha com os dados da sua própria marca antes de
usar. Os 12 pilares ISO são o contrato de builder genérico e público para
`marketplace_listing` -- nenhum dado de tenant real está incluído.
