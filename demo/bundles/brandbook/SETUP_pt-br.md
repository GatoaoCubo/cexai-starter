# SETUP -- brandbook (Manual de Marca) -- guia combinado PT-BR

Guia geral do bundle `brandbook`. Para o passo a passo detalhado por
plataforma, veja os guias específicos:

- **ChatGPT (Projects ou Custom GPT)** -> `SETUP_chatgpt_projects.md`
- **Claude Projects** -> `SETUP_claude_projects.md`
- **Gemini Gems** -> `SETUP_gemini_gems.md`

> **Fidelidade**: `full` em qualquer plataforma. Diferente de bundles com
> Actions/tiers (ex.: pesquisa de mercado), o `brandbook` é 100%
> instructions + conhecimento -- não há chave de API, não há integração
> externa obrigatória, e nenhuma plataforma degrada a capacidade de geração
> das 8 seções.

## Arquivos do bundle (overview)

```
brandbook/
  P01_knowledge.md ... P12_orchestration.md  <- SUBA os 12 como Knowledge/Files
  system_instruction.md                       <- COLE como Instructions/System Prompt
  customgpt_instructions.json                 <- config pronta para Custom GPT (name/description/instructions/starters)
  README.md                                   <- overview + passo a passo rápido
  SETUP_*.md                                  <- este guia + os 3 específicos por plataforma
```

## O que é o agente brandbook

Um agente que monta um **Manual de Marca** completo (8 seções fixas) a
partir do que você fornecer: nome da marca (obrigatório), essência,
materiais (texto/URL/PDF colado) e paleta de cores. Onde faltar dado real,
ele emite um placeholder honesto `[fornecer: ...]` em vez de inventar --
essa é a regra Nunca-Fabricar, e vale para toda cor, fonte, exemplo de copy
ou métrica de conversão.

### As 8 seções produzidas

1. Identidade da Marca
2. Paleta de Cores
3. Tipografia
4. Persona da Marca
5. Uso do Logotipo
6. Estilo de Imagem
7. Framework de Mensagem
8. Faça e Não Faça

## Opção A -- ChatGPT (Projects ou Custom GPT)

Veja `SETUP_chatgpt_projects.md` para o passo a passo completo.

Resumo:
1. Crie um Project (plano free) ou um Custom GPT (plano Plus) em chatgpt.com.
2. Cole `system_instruction.md` (ou o campo `instructions` de
   `customgpt_instructions.json`) nas Instructions.
3. Suba os 12 arquivos `P0X_*.md` como Knowledge/Files.
4. Web Browsing é opcional (só ajuda a ler uma URL de material de marca).
5. Teste com: `Monte o manual de marca para Café Aurora`.

## Opção B -- Claude Projects

Veja `SETUP_claude_projects.md` para o passo a passo completo.

Resumo:
1. Crie um Project em claude.ai.
2. Cole `system_instruction.md` nas Project Instructions.
3. Suba os 12 arquivos `P0X_*.md` como Knowledge (sem limite de 20 arquivos).
4. Web search é opcional.
5. Teste com o mesmo prompt de exemplo.

## Opção C -- Gemini Gems

Veja `SETUP_gemini_gems.md` para o passo a passo completo.

Resumo:
1. Crie um Gem em gemini.google.com.
2. Cole `system_instruction.md` nas Instructions do Gem.
3. Suba os 12 arquivos `P0X_*.md` como Knowledge.
4. Extension Google Search é opcional.
5. Teste com o mesmo prompt de exemplo.

## Capabilities recomendadas por plataforma

| Capability | ChatGPT | Claude | Gemini |
|------------|---------|--------|--------|
| Web Browsing/Search (ler URL de material) | opcional | opcional | opcional (extension) |
| Code Interpreter | não usado | não usado | não usado |
| Actions / integrações externas | não usado (bundle sem Actions) | não usado | não usado |
| Upload de imagem (logotipo) na conversa | sim | sim | sim (multimodal nativo) |

## Como o agente coleta os dados de entrada

O agente pede, em ordem, os campos do schema de entrada (detalhe completo
em `P06_schema.md`):

- **brand_name** (obrigatório): nome da marca.
- **brand_essence** (opcional): essência em 1 frase.
- **brand_materials** (opcional): texto livre, URL do site, ou texto
  extraído de um PDF que você colar.
- **brand_materials_palette** (opcional): lista de cores em hex.

Se você não fornecer um campo opcional, o agente segue em frente e marca os
lugares correspondentes com `[fornecer: ...]` -- ele nunca pausa esperando
um campo opcional, e nunca inventa o valor no lugar dele.

## Como usar (fluxo típico)

1. Diga o nome da marca: `Monte o manual de marca para <nome da marca>`.
2. Cole a essência e qualquer material que você tiver (texto, paleta em
   hex, URL do site, descrição do logotipo).
3. O agente entrega as 8 seções em Markdown, prontas para copiar.
4. Revise os `[fornecer: ...]` que restarem e preencha com dado real da sua
   marca antes de considerar o manual finalizado.
5. Peça ajustes seção por seção sempre que quiser refinar tom, paleta ou
   framework de mensagem.

## Honestidade sobre o que este bundle É e NÃO É

Este bundle exportado é um **agente standalone completo** para a tarefa de
montar um manual de marca -- ele TEM a lógica completa das 8 seções + a
regra Nunca-Fabricar + o schema de entrada, e funciona igual em qualquer
uma das 3 plataformas.

Ele NÃO tem (isso vive só no CEXAI interno, descrito em `P04_tools.md`,
`P08_architecture.md` e `P10_memory.md` como contexto de arquitetura):
- a crew sequencial de 3 papéis (`brand_discovery`: Estrategista de Marca ->
  Arquiteto de Persona -> Estruturador Visual) que compõe o brandbook a
  partir de outros artefatos;
- os scripts `brand_audit.py` / `brand_ingest.py` / `brand_propagate.py` /
  `brand_validate.py`;
- o MCP `fetch` / `markitdown` / `canva` para raspar site, converter PDF ou
  exportar assets automaticamente;
- memória persistente entre sessões (`.cex/runtime/...`) -- aqui, a memória
  é a nativa da plataforma escolhida (histórico de conversa).

Nada disso é necessário para o agente cumprir a tarefa em uma única
conversa -- é só honestidade sobre o que é replicado no bundle exportado
vs. o que é exclusivo do CEXAI completo.

## Solução de problemas

- **"Ele inventou uma cor, fonte, exemplo de copy ou métrica"** -> P03,
  P05 e P11 proíbem isso explicitamente. Reforce: "onde não há dado real,
  use `[fornecer: ...]`, nunca invente."
- **Não conseguiu ler a URL do site da marca** -> esperado em sites com
  proteção anti-bot; cole o texto manualmente como `brand_materials`.
- **Muitos placeholders no resultado** -> normal na primeira rodada; forneça
  mais material e peça para o agente regenerar as seções afetadas.
- **Quer o manual em outro idioma** -> troque a linha `Idioma: pt-BR` em
  `system_instruction.md` antes de colar nas Instructions da plataforma
  escolhida.
- **Quer mudar a ordem ou o conteúdo das 8 seções** -> edite `P03_prompt.md`
  (ordem das seções) e `P05_output.md` (contrato de saída), depois resuba
  os arquivos atualizados como Knowledge.

## Compatibilidade entre plataformas

Os mesmos `system_instruction.md` + 12 arquivos `P0X_*.md` funcionam sem
nenhuma adaptação em ChatGPT, Claude e Gemini -- não há variante "enxuta"
neste bundle porque não há Actions/tiers para reduzir. Se você já configurou
o agente em uma plataforma e quer replicá-lo em outra, basta repetir os
passos 2 e 3 do guia correspondente com os mesmos arquivos.
