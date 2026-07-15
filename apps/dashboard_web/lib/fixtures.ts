// ----------------------------------------------------------------------------
// FIXTURES mode (NEXT_PUBLIC_FIXTURES=1).
//
// In-memory mocks for /capabilities, /capability/run, /results so the whole UI
// runs + is reviewable WITHOUT the backend and WITHOUT Supabase.
//
// The shapes here are EXACTLY the wire contract (lib/types.ts), aligned to the
// REAL backend (apps/dashboard_api): the run is SYNCHRONOUS -- fxRunCapability
// resolves to a CapabilityResultView (after a short delay so the loading/8F
// states render), there is no run_id/poll. Swapping to the real backend
// (config.fixtures=false) changes nothing in the components.
// ----------------------------------------------------------------------------

import type {
  Agent,
  AgentDetail,
  AgentRun,
  AgentRunResultView,
  AgentRunStarted,
  AgentStep,
  CapabilitiesConfig,
  Card,
  CapabilityResultView,
  Crew,
  CrewDetail,
  DualOutputResult,
  EntityRecord,
  EntitySchema,
  HealthRow,
  IntegrationStatus,
  ProductResearchResult,
  ResearchUniverseReport,
  ResultRow,
  SecretStatus,
  SummaryResponse,
  SummaryStat,
  TenantSettings,
  UploadedMedia,
} from "./types";
import {
  inputExampleFor,
  moldFor,
  PENDING_COPY_MARKER,
  type MoldSection,
} from "./molds";
import { AD_CATALOG_SAMPLE_HTML } from "./fixtures/ad_catalog_sample";
import { LANDING_SAMPLE_HTML } from "./fixtures/landing_sample";
import { MEDIA_GALLERY_SAMPLE_HTML } from "./fixtures/media_gallery_sample";
import type { MediaKind, MediaSlot } from "./dual_output_contract";
import { config } from "./config";
import { resolveFlavor, type FixtureFlavor, type FixtureFlavorKey } from "./fixtureFlavor";

// FIXTURE FLAVOR (register R-012): the demo vocabulary (product/competitors/SEO/
// market stats/leads) is resolved ONCE from the tenant's business shape (retail |
// services -> neutral default) instead of being hardcoded to the pet-retail world.
// See lib/fixtureFlavor.ts for the table + the resolution rule.
const activeFlavor: FixtureFlavor = resolveFlavor(config.businessShape);

/** Fixed tenant context for offline review (a brand-neutral sample tenant). */
export const FIXTURE_TENANT = {
  email: "operator@demo.local",
  tenant_id: "11111111-1111-4111-8111-111111111111",
  tenant_label: "Sua Empresa",
};

/** The MVP base card set (spec B.5), with one disabled + one overlay-custom card. */
export const FIXTURE_CARDS: Card[] = [
  {
    capability: "research",
    label: "Research",
    title: "Research",
    nucleus: "N01",
    icon: "research",
    enabled: true,
    source: "base",
    description:
      "Compile a market or competitor scan into a typed, sourced knowledge card.",
    kind: "knowledge_card",
    pillar: "P01",
    verb: "analyze",
    default_intent_hint: "Research <topic> -- competitors, pricing, and market signals",
  },
  {
    capability: "ads",
    label: "Ads / Copy",
    title: "Ads and Copy",
    nucleus: "N02",
    icon: "ads",
    enabled: true,
    source: "base",
    description: "Brand-voice ad copy and campaign hooks, on tone and on length.",
    kind: "prompt_template",
    pillar: "P03",
    verb: "create",
    default_intent_hint: "Write ad copy for <product/offer> targeting <audience>",
  },
  {
    capability: "media_photo",
    label: "Media / Photo",
    title: "Media and Photo",
    nucleus: "N02",
    icon: "media",
    enabled: true,
    source: "base",
    description: "A structured photo / image brief the media pipeline can render.",
    kind: "multimodal_prompt",
    pillar: "P03",
    verb: "create",
    default_intent_hint: "Create a photo brief for <scene/subject>",
    // BRANDBOOK Cell A PROOF: a typed input_contract drives the run cockpit's typed form
    // (one control per field) instead of the free-text intent box. It exercises every control
    // -- text / string / file (any-media upload -> palette) / url (-> fetched text) / enum /
    // number. Fixtures-only demo; in live mode the registry's to_card() supplies input_contract
    // per capability (an absent contract -> the free-text intent box, degrade-never).
    input_contract: [
      {
        key: "scene",
        label: "Cena",
        type: "text",
        required: true,
        example: "Sala clara e moderna, planta desfocada ao fundo",
        note: "descreva o ambiente da foto",
      },
      {
        key: "subject",
        label: "Sujeito",
        type: "string",
        required: true,
        example: activeFlavor.photoSubjectExample,
      },
      {
        key: "reference_image",
        label: "Imagem de referencia",
        type: "file",
        required: false,
        example: "",
        note: "upload de qualquer midia -- uma imagem vira paleta de cores automaticamente",
      },
      {
        key: "brand_site",
        label: "Site da marca",
        type: "url",
        required: false,
        example: "https://example.com",
        note: "buscamos o texto da pagina para ancorar a voz da marca",
      },
      {
        key: "style",
        label: "Estilo",
        type: "enum",
        required: false,
        example: "lifestyle",
        enum_values: ["lifestyle", "packshot", "editorial", "minimalista"],
      },
      {
        key: "num_shots",
        label: "Numero de takes",
        type: "number",
        required: false,
        example: 5,
        note: "1-8 (default 5)",
      },
    ],
  },
  {
    capability: "pricing",
    label: "Pricing",
    title: "Pricing",
    nucleus: "N06",
    icon: "pricing",
    enabled: true,
    source: "base",
    description: "Tiers, funnels, and revenue framing grounded in your segment.",
    kind: "content_monetization",
    pillar: "P11",
    verb: "create",
    default_intent_hint: "Design pricing tiers for <product>",
  },
  {
    capability: "roi_calc",
    label: "ROI Calculator",
    title: "ROI Calculator",
    nucleus: "N06",
    icon: "pricing",
    enabled: true,
    source: "base",
    description:
      "Quantify hours and money saved, payback period, and annual return as an input-driven value proof.",
    kind: "roi_calculator",
    pillar: "P11",
    verb: "create",
    default_intent_hint:
      "Build an ROI case for <buyer/segment> -- team size, hourly rate, current effort",
  },
  {
    capability: "funnel_diag",
    label: "Funnel Diagnostic",
    title: "Funnel Diagnostic",
    nucleus: "N06",
    icon: "pricing",
    enabled: true,
    source: "base",
    description:
      "Find the highest-ROI leak across the funnel and rank the fixes by impact per effort.",
    kind: "tool_card",
    pillar: "P11",
    verb: "analyze",
    default_intent_hint:
      "Diagnose the funnel for <product> -- per-stage metrics, find the biggest leak",
  },
  {
    capability: "docs",
    label: "Knowledge / Docs",
    title: "Knowledge and Docs",
    nucleus: "N04",
    icon: "docs",
    enabled: true,
    source: "base",
    description: "Capture a process or fact set as RAG-ready documentation.",
    kind: "knowledge_card",
    pillar: "P01",
    verb: "document",
    default_intent_hint: "Capture <subject> as RAG-ready documentation",
  },
  // --- next-wave catalog-tuple cards (roadmap chain N01 -> N02/N06) ----------
  // Mirror of the new cexai_capability_catalog.yaml entries so the dashboard shows
  // them in fixtures mode. Every kind is non-frozen + present in kinds_meta.json.
  {
    capability: "tier_designer",
    label: "Plan Matrix",
    title: "Plan Matrix / Tier Designer",
    nucleus: "N06",
    icon: "pricing",
    enabled: true,
    source: "base",
    description:
      "Design a subscription plan matrix -- differentiated tiers, feature gating, and price anchoring.",
    kind: "subscription_tier",
    pillar: "P11",
    verb: "create",
    default_intent_hint:
      "Design the plan matrix for <product> -- 3 tiers, feature gating, anchor price",
  },
  {
    capability: "product_docs",
    label: "Product Docs",
    title: "Product Docs",
    nucleus: "N04",
    icon: "docs",
    enabled: true,
    source: "base",
    description: "Capture product documentation as a RAG-ready knowledge card.",
    kind: "knowledge_card",
    pillar: "P01",
    verb: "document",
    default_intent_hint: "Document <product/feature> -- setup, usage, and reference",
  },
  {
    capability: "email_builder",
    label: "Email Builder",
    title: "Email Builder",
    nucleus: "N02",
    icon: "ads",
    enabled: true,
    source: "base",
    description:
      "Generate a responsive HTML email prompt template -- subject, preheader, and on-brand body.",
    kind: "prompt_template",
    pillar: "P03",
    verb: "create",
    default_intent_hint:
      "Write a marketing email for <campaign/audience> -- subject, preheader, body",
  },
  {
    capability: "oauth_connect",
    label: "OAuth Connect",
    title: "OAuth Connect",
    nucleus: "N03",
    icon: "custom",
    enabled: true,
    source: "base",
    description:
      "Produce a typed OAuth app config -- scopes, redirect URIs, and token endpoints.",
    kind: "oauth_app_config",
    pillar: "P04",
    verb: "create",
    default_intent_hint:
      "Configure an OAuth connection to <provider> -- scopes + redirect URIs",
  },
  {
    capability: "competitor_benchmark",
    label: "Competitor Benchmark",
    title: "Competitor Benchmark Matrix",
    nucleus: "N01",
    icon: "research",
    enabled: true,
    source: "base",
    description:
      "Build a competitor benchmark matrix -- rivals scored across the dimensions that matter, with sourced cells.",
    kind: "competitive_matrix",
    pillar: "P01",
    verb: "analyze",
    default_intent_hint:
      "Benchmark <product> against <competitors> across price, features, and positioning",
  },
  // --- SPEC 05 lead-gen suite Phase 1a: the scraping/lead-gen vertical --------
  // Find leads around a seed across the available channels (B2C marketplace / B2B
  // CNPJ / UGC social) -> a typed lead LIST that seeds the CRM (the leads entity).
  // D1 reuses the research_pipeline kind (0 kinds_meta churn). Molded (MOLD_LEADGEN)
  // -> its fixtures run routes through buildMoldResult (honest mock, "dados simulados").
  {
    capability: "leadgen",
    label: "Captacao de Leads",
    title: "Captacao de Leads (Lead-gen / scraping)",
    nucleus: "N01",
    icon: "research",
    enabled: true,
    source: "base",
    description:
      "Encontra leads em torno de um seed nos canais disponiveis (marketplace, CNPJ, social) -- lista tipada com contato honesto e status, que alimenta o CRM.",
    kind: "research_pipeline",
    pillar: "P04",
    verb: "analyze",
    default_intent_hint:
      "Encontre leads para <perfil> a partir de <seed> -- marketplace, CNPJ, social",
  },
  // --- CRM / Contatos (capability "crm", kind demo_acme_crm) -- SPEC 08 ----------
  // The CRM card consumes what leadgen produces: a funnel/activity view OVER the
  // leads managed entity (the SAME tenant_data `leads` rows the Data tab shows).
  // It does NOT find leads (that is leadgen) -- it filters/ranks/derives over the
  // existing ones. Molded (MOLD_CRM) -> its fixtures run routes through
  // buildMoldResult (honest mock, "dados simulados"). kind demo_acme_crm is a
  // tenant-namespaced kind (overlay kinds_overlay.yaml -> P10, N05); 0 kinds_meta churn.
  {
    capability: "crm",
    label: "CRM / Contatos",
    title: "CRM / Contatos (funil sobre os leads)",
    nucleus: "N05",
    icon: "table",
    enabled: true,
    source: "overlay",
    description:
      "Funil + atividade sobre os leads ja captados: filtra por status/canal/score, ranqueia e deriva a proxima-melhor-acao de cada lead. Opera sobre a entidade leads -- nunca inventa um contato.",
    kind: "demo_acme_crm",
    pillar: "P10",
    verb: "analyze",
    default_intent_hint:
      "Mostre o funil de CRM -- priorize os leads qualificados e a proxima acao de cada um",
  },
  // --- Sales Assistant (capability "sales_assistant", kind demo_acme_sales_assistant) -- SPEC 09 --
  // The 3rd stage of the lead suite (scraping/leadgen -> CRM -> Sales Assistant): leadgen
  // FINDS the leads, the CRM RANKS the funnel, the Sales Assistant COACHES the outreach for
  // ONE chosen lead. It reads the ONE lead the operator picked (inputs['lead'] OR
  // inputs['leads']+lead_id) and TEMPLATES a grounded, rule-based outreach play. Molded
  // (MOLD_SALES_ASSISTANT) -> its fixtures run routes through buildMoldResult (honest mock,
  // "dados simulados"). kind demo_acme_sales_assistant is a tenant-namespaced kind (overlay
  // kinds_overlay.yaml -> P03, N02); 0 kinds_meta churn. PURE generator (no LLM/net/DB/clock).
  {
    capability: "sales_assistant",
    label: "Assistente de Vendas",
    title: "Assistente de Vendas (abordagem de um lead)",
    nucleus: "N02",
    icon: "ads",
    enabled: true,
    source: "overlay",
    description:
      "Coaching de abordagem para UM lead: perfil + abordagem derivada, descoberta, pitch (Hook aterrado no sinal real), objecoes, e-mail e cadencia. Aterra tudo no lead real -- claims/specs/precos sao [preencher], nunca inventados.",
    kind: "demo_acme_sales_assistant",
    pillar: "P03",
    verb: "create",
    default_intent_hint:
      "Monte a abordagem para este lead -- descoberta, pitch, objecoes, e-mail e cadencia",
  },
  // --- FLAGSHIP: product research -> ads (capability "pesquisa_produto") -----
  // The dual-output flagship: "Cole um produto -> anuncio completo". Resolves to
  // knowledge_card (0 new kinds); its result carries the typed 30-field
  // product-research payload (ResearchResultView renders the rich report). Mirror
  // of the cexai_capability_catalog.yaml entry shipped in Wave 1 (commit a7705e1245).
  {
    capability: "pesquisa_produto",
    label: "Pesquisa de Produto",
    title: "Pesquisa de Produto -> Anuncio",
    nucleus: "N01",
    icon: "research",
    enabled: true,
    source: "base",
    description:
      "Cole um produto: pesquisa preco, concorrentes e palavras-chave nos marketplaces, depois encadeia o anuncio pronto.",
    kind: "knowledge_card",
    pillar: "P01",
    verb: "analyze",
    default_intent_hint:
      "Pesquise <produto> nos marketplaces -- preco, concorrentes, palavras-chave",
  },
  {
    capability: "research_universe",
    label: "Research Universe",
    title: "Research Universe -- relatorio multi-fonte",
    nucleus: "N01",
    icon: "research",
    enabled: true,
    source: "base",
    description:
      "Um seed (produto / marca / CNPJ) abre as lanes de pesquisa relevantes e monta um relatorio multi-fonte com status honesto por fonte.",
    kind: "research_universe",
    pillar: "P01",
    verb: "analyze",
    default_intent_hint:
      "Pesquise <produto / marca / CNPJ> em todas as fontes",
  },
  {
    capability: "landing",
    label: "Landing Page",
    title: "Landing Page",
    nucleus: "N03",
    icon: "landing",
    enabled: true,
    source: "base",
    description: "A responsive, conversion-ready site page rendered from its molded outline.",
    kind: "landing_page",
    pillar: "P05",
    verb: "create",
    default_intent_hint: "Build a landing page for <product/offer>",
  },
  {
    capability: "custom_intake_form",
    label: "Client Intake",
    title: "Client Intake",
    nucleus: "N03",
    icon: "custom",
    enabled: true,
    source: "overlay",
    description:
      "Tenant-custom card from the overlay -- resolves to a tenant-specific intake kind.",
    kind: "custom_intake_form",
    pillar: "P05",
    verb: "create",
    default_intent_hint: "Capture a new client intake",
  },
  // --- COMPOSE PICKER: declared-but-DISABLED catalog (mission BUILD C) -----------
  // The founder's "the tenant pulls new capabilities and composes their own dashboard"
  // needs a NON-EMPTY pull-set offline. These three are DECLARED for the tenant overlay
  // but ship enabled:false -- so they do NOT render on the grid (fxListCards filters to
  // enabled, mirroring live GET /capabilities) yet DO surface in the compose picker as
  // "available to add". Each already has an authored mold (lib/molds.MOLDS:
  // marketplace_listing / sourcing_opportunity / product_match), so ATTACHING one makes
  // a real card appear AND a real molded result round-trip on run -- not a degrade-never
  // stub. They complete the lead-suite story: publish the ad (marketplace_listing), the
  // buy-side opportunity matrix (sourcing), and the catalog audit (product_match). Every
  // kind is non-frozen + present in kinds_meta.json. enabled:false is the load-bearing
  // bit -- it is what makes the picker have something to pull.
  {
    capability: "marketplace_listing",
    label: "Anuncio Marketplace",
    title: "Anuncio Marketplace (publicar no Mercado Livre)",
    nucleus: "N06",
    icon: "table",
    enabled: false,
    source: "overlay",
    description:
      "Transforma um produto do catalogo em um anuncio pronto para publicar no Mercado Livre -- payload tipado (maquina) + galeria HTML com slots de foto/video (humano).",
    kind: "marketplace_listing",
    pillar: "P05",
    verb: "create",
    default_intent_hint:
      "Monte o anuncio ML de <produto> -- titulo, descricao, marca, categoria",
  },
  {
    capability: "sourcing_opportunity",
    label: "Sourcing (compra)",
    title: "Sourcing -- matriz de oportunidade de compra",
    nucleus: "N06",
    icon: "pricing",
    enabled: false,
    source: "overlay",
    description:
      "Matriz de oportunidade buy-side sobre os catalogos dos fornecedores: ranqueia o que comprar por margem, demanda e risco -- nunca inventa um fornecedor.",
    kind: "opportunity_matrix",
    pillar: "P11",
    verb: "analyze",
    default_intent_hint:
      "Ranqueie as oportunidades de compra a partir dos catalogos dos fornecedores",
  },
  {
    capability: "product_match",
    label: "Match de Produto",
    title: "Match de Produto (auditoria de catalogo)",
    nucleus: "N01",
    icon: "research",
    enabled: false,
    source: "overlay",
    description:
      "Casa um produto do seu catalogo com a oferta de mercado e audita o gap de campos -- o que falta para o anuncio ficar publicavel.",
    kind: "product_match",
    pillar: "P01",
    verb: "analyze",
    default_intent_hint:
      "Compare <produto> com a oferta de mercado -- audite os campos faltantes",
  },
  // --- B2: BRANDBOOK -- the brand-SETUP capability -------------------------------
  // Surfaced as a runnable card ("Brandbook / Marca"). Its typed input_contract drives
  // the run cockpit (logo file upload -> data-uri, site URL, colour palette). Running it
  // produces the brand book AND (live mode) WRITES the tenant brand config so every other
  // capability re-personalizes from the new {{brand_*}} values. Mirrors the cexai catalog
  // entry + the cex_brandbook generator (capability_generators/brandbook.py). N06.
  {
    capability: "brandbook",
    label: "Brandbook / Marca",
    title: "Brandbook -- configurar a marca",
    nucleus: "N06",
    icon: "brand",
    enabled: true,
    source: "base",
    description:
      "Envie logo, site e paleta -> gera o brand book completo E grava a config da marca do tenant, personalizando TODAS as capacidades.",
    kind: "brandbook",
    pillar: "P05",
    verb: "create",
    default_intent_hint: "Monte o brand book de <marca> a partir dos materiais enviados",
    // The typed input contract (drives the RunModal form): logo upload (data-uri), site URL,
    // and the colour palette. brand_name is the only hard requirement (the brand identity).
    input_contract: [
      {
        key: "brand_name",
        label: "Nome da marca",
        type: "text",
        required: true,
        example: activeFlavor.storeLabel,
        note: "o nome da marca -- vira o {{brand_name}} difundido em todas as capacidades",
      },
      {
        key: "brand_essence",
        label: "Essencia (1 frase)",
        type: "text",
        required: false,
        example: activeFlavor.brandEssenceExample,
        note: "a essencia em uma frase -- vira a {{brand_tagline}}",
      },
      {
        key: "brand_materials_data_uri",
        label: "Logotipo (imagem)",
        type: "file",
        required: false,
        example: "",
        note: "upload do logotipo (PNG/SVG/WEBP) -- vira o logo da marca no header e no overlay",
      },
      {
        key: "brand_materials",
        label: "Brand book / site (URL ou texto)",
        type: "url",
        required: false,
        example: "https://example.com",
        note: "URL do site / brand book -- buscamos o texto para ancorar voz e persona",
      },
      {
        key: "brand_materials_palette",
        label: "Paleta de cores",
        type: "string[]",
        required: false,
        example: ["#1A3A5C", "#E8A020", "#FFFFFF", "#F0F0F0", "#2C2C2C"],
        note: "hex (#RRGGBB) na ordem primaria, secundaria, destaque, neutra, fundo -- viram os tokens de cor da marca",
      },
    ],
  },
];

/**
 * The brandbook capability card (B2) -- the brand-SETUP card, exported so the Settings
 * "Brand" section can open the SAME RunModal the grid uses (upload -> run -> brand book ->
 * brand config write-back). Resolved from FIXTURE_CARDS so it stays in lockstep with the
 * grid card (one source). The card carries the typed input_contract (logo upload + palette).
 * In live mode the grid card comes from /capabilities, but the Settings entry only needs a
 * card to seed the RunModal -- the backend resolves ``brandbook`` regardless of the source.
 */
export const brandbookCard: Card =
  FIXTURE_CARDS.find((c) => c.capability === "brandbook") ?? {
    capability: "brandbook",
    label: "Brandbook / Marca",
    nucleus: "N06",
    icon: "brand",
    enabled: true,
    source: "base",
    kind: "brandbook",
    pillar: "P05",
    verb: "create",
  };

/** The canonical 8F trace, rendered live during a fixtures run. */
export const F8_STEPS: { id: string; name: string; note: string }[] = [
  { id: "F1", name: "CONSTRAIN", note: "resolve kind + pillar, load schema" },
  { id: "F2", name: "BECOME", note: "load builder, inject sin lens" },
  { id: "F3", name: "INJECT", note: "knowledge cards + similar artifacts" },
  { id: "F4", name: "REASON", note: "plan sections + approach" },
  { id: "F5", name: "CALL", note: "model inference (F5)" },
  { id: "F6", name: "PRODUCE", note: "generate artifact" },
  { id: "F7", name: "GOVERN", note: "quality gate + score" },
  { id: "F8", name: "COLLABORATE", note: "persist to tenant DB + signal" },
];

// ----------------------------------------------------------------------------
// PER-CAPABILITY mock artifacts (FIXTURES mode).
//
// Each of the catalog cards that does NOT have a rich structured vertical
// (pesquisa_produto / research_universe already do) returns a CAPABILITY-SPECIFIC,
// realistic EXAMPLE artifact of ITS OWN kind -- not a one-size-fits-all
// knowledge_card. Every artifact is:
//   * THEMED on a sample pet-products brand (cat scratcher / pet e-commerce),
//     so the whole catalog reads as one coherent demo (same world as the
//     pesquisa_produto "arranhador" fixture).
//   * HONESTLY MOCK: frontmatter carries ``mock: true`` and a "(FIXTURES mode --
//     dados simulados)" notice, mirroring the anti-hallucination contract -- nothing
//     here looks like a real scrape / live result.
//   * ASCII-only + HTML-entity-free in the body text (the dashboard's house style):
//     "--" for em-dash, "->" for arrows, "R$" prices, no diacritics.
//
// NOTE (rendering contract): these return a rich MD string in ``artifact``; the
// generic ResultView <pre> renders them. A capability with NO mold attaches no
// ``structured`` payload -- ResultView's asResearch discriminator routes ANY bare
// structured payload to the product-research renderer, so a structured object
// without a ``mold_id`` would be MIS-RENDERED as a marketplace report. Rich MD is
// the correct, regression-free surface for the un-molded cards.
//
// MOLDED capabilities (lib/molds.MOLDS) are the exception: their run DOES attach a
// ``structured`` slot, but ALWAYS tagged with a ``mold_id`` so ResultView.asMold
// claims it FIRST (before asResearch) and routes it to StructuredResultView. See
// buildMoldResult + the moldFor() branch in fxRunCapability below.
// ----------------------------------------------------------------------------

/** Shared frontmatter block for a mock artifact (honest mock: true). */
function fmHead(
  idPrefix: string,
  kind: string,
  pillar: string,
  nucleus: string,
  title: string,
  tags: string[],
): string[] {
  const stamp = new Date().toISOString();
  return [
    "---",
    `id: ${idPrefix}_${Math.random().toString(36).slice(2, 8)}`,
    `kind: ${kind}`,
    `pillar: ${pillar}`,
    `nucleus: ${nucleus}`,
    `title: "${title.slice(0, 70)}"`,
    "version: 0.1.0",
    "quality: null",
    `created: "${stamp}"`,
    "mock: true",
    `tags: [${tags.join(", ")}]`,
    "---",
    "",
  ];
}

/** The honest "this is simulated" footer every mock artifact carries. */
const MOCK_NOTE =
  "> FIXTURES mode -- dados simulados (mock: true). Exemplo representativo, nao e um scrape/resultado real.";

/** Use the operator's intent when they typed one, else the themed default. */
function pick(intent: string, card: Card, fallback: string): string {
  const t = intent.trim();
  return t && t !== card.default_intent_hint ? t : fallback;
}

// ----------------------------------------------------------------------------
// ART* FALLBACK FLAVOR EXT (register R-269 second pass). These 14 art* functions
// + fakeArtifact's caller (buildArtifact) are DEAD CODE TODAY: buildArtifact only
// fires when moldFor(capability) is undefined (see the fallback branch below
// fxRunCapability's `if (moldFor(capability))` check), and every one of these
// 14 capabilities now has an authored mold (lib/molds.ts) -- so this whole path
// is unreachable under the current MOLDS registry. It exists as a DEGRADE-NEVER
// safety net (if a mold ever gets removed by regression, this fallback still
// renders SOMETHING for that capability). Converting these small per-function
// ext tables ensures that safety net can never silently resurrect the pet-retail
// world for a services/neutral tenant if that regression ever happens. Kept
// deliberately terser than the live molds.ts ext tables (these are simple
// markdown stubs, not the tested primary surface) -- but still zero-pet-leak.
// ----------------------------------------------------------------------------
interface ArtResearchExt {
  topic: string;
  resumo: readonly [string, string, string];
  /** Full literal "| {label} | Produto-lider | Preco | Rating | Reviews |" header row
   *  (fixed post-judge-review -- this used to be the hardcoded literal "Concorrente"
   *  for every flavor, incl. retail, where the pre-existing HEAD text was "Loja";
   *  retail keeps "Loja" for byte-identity, services/neutral get their own label). */
  headerRow: string;
  competitorRows: readonly [string, string, string];
  sinaisRows: readonly [string, string, string];
  recomendacao: readonly [string, string];
  fontes: readonly [string, string];
}

const ART_RESEARCH_EXT: Record<FixtureFlavorKey, ArtResearchExt> = {
  retail: {
    topic: "Mercado de arranhadores para gatos -- Brasil",
    resumo: [
      "Categoria de arranhadores/torres para gatos em alta no e-commerce BR: demanda",
      "puxada por tutores de apartamento e gatos adultos. Concorrencia concentrada em",
      "tres faixas de preco; pouca diferenciacao em durabilidade e pos-venda.",
    ],
    headerRow: "| Loja            | Produto-lider           | Preco   | Rating | Reviews |",
    competitorRows: [
      "| PetShop Premium | Torre Deluxe 1,5m       | R$ 389  | 4.7    | 2143    |",
      "| MiauHouse       | Arranhador Compacto     | R$ 149  | 4.4    | 880     |",
      "| GatoFeliz       | Poste Sisal 0,9m        | R$ 99   | 4.2    | 1310    |",
    ],
    sinaisRows: [
      "| Demanda    | Pico em datas comemorativas (Dia do Gato, Natal)| 0.81      |",
      "| Preco      | Sweet spot percebido em R$ 180-220              | 0.74      |",
      "| Lacuna     | Base antiderrapante reforcada raramente ofertada| 0.83      |",
    ],
    recomendacao: [
      "Posicionar na faixa intermediaria (R$ 199) com prova de durabilidade (sisal",
      "substituivel + base reforcada) e video de montagem para reduzir objecao.",
    ],
    fontes: [
      '- (fixture) mercadolivre.com.br -- busca "arranhador gato"',
      "- (fixture) amazon.com.br -- categoria Pet > Gatos",
    ],
  },
  services: {
    topic: "Mercado de suporte de TI terceirizado -- Brasil",
    resumo: [
      "Categoria de suporte de TI terceirizado em alta no mercado B2B BR: demanda",
      "puxada por PMEs sem TI interno. Concorrencia concentrada em tres faixas de",
      "preco; pouca diferenciacao em SLA e pos-contratacao.",
    ],
    headerRow: "| Empresa         | Produto-lider           | Preco   | Rating | Reviews |",
    competitorRows: [
      "| TechCare Solucoes | Plano Corporate       | R$ 799  | 4.7    | 214     |",
      "| InfraJa Suporte   | Suporte Essencial     | R$ 349  | 4.4    | 88      |",
      "| NuvemCerta TI     | Plano Basico          | R$ 199  | 4.2    | 131     |",
    ],
    sinaisRows: [
      "| Demanda    | Pico no inicio do trimestre fiscal (planejamento) | 0.81    |",
      "| Preco      | Sweet spot percebido em R$ 350-450/mes            | 0.74    |",
      "| Lacuna     | SLA por escrito com multa raramente ofertado      | 0.83    |",
    ],
    recomendacao: [
      "Posicionar na faixa intermediaria (R$ 399/mes) com prova de SLA (resposta",
      "em 2h + escalonamento automatico) e onboarding guiado para reduzir objecao.",
    ],
    fontes: ["- (fixture) g2.com -- busca \"suporte de ti terceirizado\"", "- (fixture) capterra.com.br -- categoria TI > Suporte Gerenciado"],
  },
  neutral: {
    topic: "Mercado de produtos de reposicao recorrente -- Brasil",
    resumo: [
      "Categoria de produtos de reposicao recorrente em alta no e-commerce BR: demanda",
      "puxada por clientes com consumo recorrente. Concorrencia concentrada em tres",
      "faixas de preco; pouca diferenciacao em durabilidade e pos-venda.",
    ],
    headerRow: "| Concorrente     | Produto-lider           | Preco   | Rating | Reviews |",
    competitorRows: [
      "| Concorrente A     | Linha Premium          | R$ 149  | 4.7    | 214     |",
      "| Concorrente B     | Linha Compacta         | R$ 99   | 4.4    | 88      |",
      "| Concorrente C     | Linha Basica           | R$ 69   | 4.2    | 131     |",
    ],
    sinaisRows: [
      "| Demanda    | Pico em datas comemorativas (Black Friday, Natal)| 0.81     |",
      "| Preco      | Sweet spot percebido em R$ 85-115                | 0.74     |",
      "| Lacuna     | Garantia estendida clara raramente ofertada      | 0.83     |",
    ],
    recomendacao: [
      "Posicionar na faixa intermediaria (R$ 99) com prova de durabilidade (garantia",
      "estendida) e video de demonstracao para reduzir objecao.",
    ],
    fontes: ['- (fixture) marketplace-a.com.br -- busca "produto exemplo"', "- (fixture) marketplace-b.com.br -- categoria Produtos > Categoria"],
  },
};

const artResearchExt = ART_RESEARCH_EXT[activeFlavor.key];

// --- research (knowledge_card): a competitor/pricing intel brief -------------
function artResearch(card: Card, intent: string): string {
  const topic = pick(intent, card, artResearchExt.topic);
  return [
    ...fmHead("kc_research", "knowledge_card", "P01", "N01", topic, [
      "research",
      "competitive",
      activeFlavor.tag,
      "fixture",
    ]),
    `# ${topic}`,
    "",
    "## Resumo executivo",
    "",
    ...artResearchExt.resumo,
    "",
    "## Concorrentes mapeados",
    "",
    artResearchExt.headerRow,
    "|-----------------|-------------------------|---------|--------|---------|",
    ...artResearchExt.competitorRows,
    "",
    "## Sinais de mercado",
    "",
    "| Dimensao   | Observacao                                      | Confianca |",
    "|------------|-------------------------------------------------|-----------|",
    ...artResearchExt.sinaisRows,
    "",
    "## Recomendacao",
    "",
    ...artResearchExt.recomendacao,
    "",
    "## Fontes",
    "",
    ...artResearchExt.fontes,
    "",
    MOCK_NOTE,
  ].join("\n");
}

interface ArtAdsExt {
  product: string;
  variantA: readonly [string, string, string];
  variantB: readonly [string, string, string, string];
  variantC: readonly [string, string];
  keywords: string;
}

const ART_ADS_EXT: Record<FixtureFlavorKey, ArtAdsExt> = {
  retail: {
    product: "Arranhador Torre para Gatos 1,2m",
    variantA: [
      "- Headline (40): Arranhador que aguenta gato de 8kg",
      "- Primary text (125): Cansou de arranhador que desmonta? Base reforcada",
      "  antiderrapante + sisal substituivel. Seu gato arranha, o movel sobrevive.",
    ],
    variantB: [
      "- Headline 1 (30): Arranhador Torre 1,2m",
      "- Headline 2 (30): Base Reforcada Antiderrapante",
      "- Description (90): Torre robusta para gatos adultos. Frete gratis acima de",
      "  R$ 250. Envio em 24h.",
    ],
    variantC: ["- Hook (sticker): -30% so hoje", "- Line: A torre que vira o brinquedo favorito do seu gato."],
    keywords: "arranhador para gatos, torre arranhador, arranhador gato grande",
  },
  services: {
    product: "Pacote de Suporte Tecnico Mensal",
    variantA: [
      "- Headline (40): Suporte que resolve chamado critico em 2h",
      "- Primary text (125): Cansou de suporte que so aparece quando ja quebrou?",
      "  SLA por escrito + atendimento remoto 24/7. Voce previne, o time resolve.",
    ],
    variantB: [
      "- Headline 1 (30): Suporte de TI Mensal",
      "- Headline 2 (30): SLA por Escrito Garantido",
      "- Description (90): Suporte robusto para PMEs. Auditoria de seguranca gratis",
      "  na 1a reuniao. Onboarding em 48h.",
    ],
    variantC: ["- Hook (sticker): -15% so na contratacao anual", "- Line: O suporte que vira parceiro da sua equipe de TI."],
    keywords: "suporte de ti para empresas, suporte tecnico remoto, consultoria de ti terceirizada",
  },
  neutral: {
    product: "Produto Exemplo A",
    variantA: [
      "- Headline (40): Produto que aguenta uso diario intenso",
      "- Primary text (125): Cansou de produto que quebra cedo? Garantia estendida",
      "  + suporte pos-venda. O uso diario nao desgasta, voce fica tranquilo.",
    ],
    variantB: [
      "- Headline 1 (30): Produto Exemplo A",
      "- Headline 2 (30): Garantia Estendida Inclusa",
      "- Description (90): Produto robusto para uso diario. Frete gratis acima de",
      "  um valor minimo. Envio em 24h.",
    ],
    variantC: ["- Hook (sticker): -15% so no lancamento", "- Line: O produto que vira favorito no seu dia a dia."],
    keywords: "produto exemplo, categoria exemplo, produto exemplo premium",
  },
};

const artAdsExt = ART_ADS_EXT[activeFlavor.key];

// --- ads (prompt_template): 2-3 ad variants with hooks + CTAs + lengths -------
function artAds(card: Card, intent: string): string {
  const product = pick(intent, card, artAdsExt.product);
  return [
    ...fmHead("pt_ads", "prompt_template", "P03", "N02", `Anuncios -- ${product}`, [
      "ads",
      "copy",
      activeFlavor.tag,
      "fixture",
    ]),
    `# Ad copy -- ${product}`,
    "",
    "Tres variantes prontas, por angulo, com gancho + CTA + limite de plataforma.",
    "",
    "## Variante A -- Meta Feed (gancho: durabilidade)",
    "",
    ...artAdsExt.variantA,
    "- CTA: Comprar agora",
    "",
    "## Variante B -- Google Search (gancho: intencao de compra)",
    "",
    ...artAdsExt.variantB,
    "- CTA: Ver oferta",
    "",
    "## Variante C -- Instagram Stories (gancho: FOMO)",
    "",
    ...artAdsExt.variantC,
    "- CTA: Arraste pra cima",
    "",
    "## Palavras-chave sugeridas",
    "",
    artAdsExt.keywords,
    "",
    MOCK_NOTE,
  ].join("\n");
}

interface ArtMediaPhotoExt {
  subject: string;
  cena: readonly [string, string];
  sujeito: readonly [string, string];
  angulo: string;
  shotList: readonly [string, string, string, string, string];
}

const ART_MEDIA_PHOTO_EXT: Record<FixtureFlavorKey, ArtMediaPhotoExt> = {
  retail: {
    subject: "Arranhador Torre para Gatos 1,2m",
    cena: [
      "Sala de apartamento clara e moderna, planta ao fundo desfocado, luz natural",
      "de janela lateral (golden hour suave). Tom acolhedor, pet-friendly.",
    ],
    sujeito: [
      "Gato adulto de porte medio (pelo cinza) usando a torre -- patas no sisal,",
      "expressao relaxada. Produto 100% visivel, base em destaque.",
    ],
    angulo: "| Angulo      | Nivel do gato (low angle), 3/4 frontal |",
    shotList: [
      "1. Hero: gato no topo da torre, produto inteiro no enquadramento.",
      "2. Detalhe: textura do sisal + base antiderrapante (close).",
      "3. Lifestyle: gato arranhando, tutor ao fundo desfocado.",
      "4. Escala: produto ao lado de um sofa para dar nocao de tamanho.",
      "5. Packshot: produto em fundo branco para o marketplace.",
    ],
  },
  services: {
    subject: "Pacote de Suporte Tecnico Mensal",
    cena: [
      "Sala de reuniao clara e moderna, planta ao fundo desfocada, luz natural",
      "de janela lateral (golden hour suave). Tom confiante, corporativo.",
    ],
    sujeito: [
      "Equipe tecnica em reuniao de atendimento -- expressao confiante e",
      "colaborativa. Atendimento 100% visivel, dashboard em destaque.",
    ],
    angulo: "| Angulo      | Nivel dos olhos (eye level), 3/4 frontal |",
    shotList: [
      "1. Hero: equipe reunida na sala de reuniao, atendimento completo no enquadramento.",
      "2. Detalhe: tela do dashboard de monitoramento + checklist de SLA (close).",
      "3. Lifestyle: tecnico atendendo chamado, cliente ao telefone ao fundo desfocado.",
      "4. Escala: equipe tecnica ao lado do rack de servidores para dar nocao de porte.",
      "5. Retrato: time em fundo neutro para o diretorio (G2/LinkedIn).",
    ],
  },
  neutral: {
    subject: "Produto Exemplo A",
    cena: [
      "Sala de estudio clara e moderna, fundo neutro desfocado, luz natural",
      "de janela lateral (golden hour suave). Tom neutro, profissional.",
    ],
    sujeito: [
      "Produto em cena de estudio, still-life organizado -- produto 100%",
      "visivel, base em destaque.",
    ],
    angulo: "| Angulo      | Nivel do produto (low angle), 3/4 frontal |",
    shotList: [
      "1. Hero: produto centralizado, produto inteiro no enquadramento.",
      "2. Detalhe: textura e acabamento do produto (close).",
      "3. Lifestyle: produto em uso, cliente ao fundo desfocado.",
      "4. Escala: produto ao lado de um objeto do dia a dia para dar nocao de tamanho.",
      "5. Packshot: produto em fundo branco para o marketplace.",
    ],
  },
};

const artMediaPhotoExt = ART_MEDIA_PHOTO_EXT[activeFlavor.key];

// --- media_photo (multimodal_prompt): a photo/image brief + shot list ---------
function artMediaPhoto(card: Card, intent: string): string {
  const subject = pick(intent, card, artMediaPhotoExt.subject);
  return [
    ...fmHead("mmp_photo", "multimodal_prompt", "P03", "N02", `Photo brief -- ${subject}`, [
      "media",
      "photo",
      activeFlavor.tag,
      "fixture",
    ]),
    `# Photo brief -- ${subject}`,
    "",
    "## Cena",
    "",
    ...artMediaPhotoExt.cena,
    "",
    "## Sujeito",
    "",
    ...artMediaPhotoExt.sujeito,
    "",
    "## Iluminacao + camera",
    "",
    "| Parametro   | Valor                                  |",
    "|-------------|----------------------------------------|",
    "| Luz         | Natural difusa + rebatedor branco      |",
    "| Lente       | 50mm f/2.0, ISO 200                     |",
    artMediaPhotoExt.angulo,
    "| Fundo       | Desfoque suave (bokeh), neutro          |",
    "",
    "## Shot list",
    "",
    ...artMediaPhotoExt.shotList,
    "",
    "## Negative prompt",
    "",
    "sem maos humanas em foco, sem logos de terceiros, sem fundo baguncado.",
    "",
    MOCK_NOTE,
  ].join("\n");
}

interface ArtPricingExt {
  product: string;
  rows: readonly [string, string, string, string, string, string];
  /** 2 narrative bullets under "Logica de ancoragem" (fixed post-judge-review --
   *  these used to be 2 hardcoded literals naming "frete gratis" (free shipping)
   *  and "brinquedo" (toy), both retail-only concepts, shown to every flavor.
   *  Each flavor's bullets now name the SAME Plus/Premium-gated perks its own
   *  `rows` table above already establishes -- retail/neutral keep shipping,
   *  services swaps in onboarding + the emergency-support perk. */
  anchorNotes: readonly [string, string];
}

const ART_PRICING_EXT: Record<FixtureFlavorKey, ArtPricingExt> = {
  retail: {
    product: "Loja de produtos para gatos (assinatura)",
    rows: [
      "| Preco / mes              | R$ 29    | R$ 79      | R$ 199    |",
      "| Caixa mensal de petiscos | 1        | 2          | 4         |",
      "| Brinquedo surpresa       | --       | 1/mes      | 2/mes     |",
      "| Frete                    | Pago     | Gratis     | Gratis    |",
      "| Desconto loja            | 5%       | 10%        | 15%       |",
      "| Consultoria pet (chat)   | --       | --         | Incluida  |",
    ],
    anchorNotes: [
      "- Basico captura o sensivel a preco; sem frete gratis para empurrar ao Plus.",
      "- Gating de valor: frete gratis e brinquedo so a partir do Plus.",
    ],
  },
  services: {
    product: "Pacote de Suporte de TI (assinatura)",
    rows: [
      "| Preco / mes              | R$ 39    | R$ 89      | R$ 169    |",
      "| Horas de suporte incluso | 2h       | 5h         | 12h       |",
      "| Consultoria de seguranca | --       | 1/mes      | 2/mes     |",
      "| Onboarding               | Pago     | Gratis     | Gratis    |",
      "| Desconto anual           | 5%       | 10%        | 15%       |",
      "| Suporte de emergencia 24/7| --      | --         | Incluida  |",
    ],
    anchorNotes: [
      "- Basico captura o sensivel a preco; sem onboarding gratis para empurrar ao Plus.",
      "- Gating de valor: onboarding gratis e suporte de emergencia so a partir do Plus.",
    ],
  },
  neutral: {
    product: "Loja de produtos (assinatura)",
    rows: [
      "| Preco / mes              | R$ 29    | R$ 79      | R$ 199    |",
      "| Caixa mensal de itens    | 1        | 2          | 4         |",
      "| Brinde surpresa          | --       | 1/mes      | 2/mes     |",
      "| Frete                    | Pago     | Gratis     | Gratis    |",
      "| Desconto loja            | 5%       | 10%        | 15%       |",
      "| Consultoria (chat)       | --       | --         | Incluida  |",
    ],
    anchorNotes: [
      "- Basico captura o sensivel a preco; sem frete gratis para empurrar ao Plus.",
      "- Gating de valor: frete gratis e brinde so a partir do Plus.",
    ],
  },
};

const artPricingExt = ART_PRICING_EXT[activeFlavor.key];

// --- pricing (content_monetization): a 3-tier table w/ gating + anchor --------
function artPricing(card: Card, intent: string): string {
  const product = pick(intent, card, artPricingExt.product);
  return [
    ...fmHead("cm_pricing", "content_monetization", "P11", "N06", `Pricing -- ${product}`, [
      "pricing",
      "monetization",
      activeFlavor.tag,
      "fixture",
    ]),
    `# Pricing tiers -- ${product}`,
    "",
    "Tres planos com ancoragem no plano do meio (Plus = mais vendido).",
    "",
    "## Tabela de planos",
    "",
    "| Recurso                  | Basico   | Plus (*)   | Premium   |",
    "|--------------------------|----------|------------|-----------|",
    ...artPricingExt.rows,
    "",
    "(*) Plano-ancora: posicionado como o melhor custo-beneficio.",
    "",
    "## Logica de ancoragem",
    "",
    "- Premium existe para fazer o Plus parecer barato (anchor alto).",
    ...artPricingExt.anchorNotes,
    "",
    "## Anual (incentivo)",
    "",
    "12 meses com 2 gratis (-16%): Plus R$ 790/ano em vez de R$ 948.",
    "",
    MOCK_NOTE,
  ].join("\n");
}

interface ArtRoiCalcExt {
  buyer: string;
}

const ART_ROI_CALC_EXT: Record<FixtureFlavorKey, ArtRoiCalcExt> = {
  retail: { buyer: "Pet shop que anuncia em marketplaces" },
  services: { buyer: "Empresa de suporte de TI que anuncia planos e pacotes" },
  neutral: { buyer: "Loja que anuncia produtos em marketplaces" },
};

const artRoiCalcExt = ART_ROI_CALC_EXT[activeFlavor.key];

// --- roi_calc (roi_calculator): inputs + hours/money saved + payback ----------
function artRoiCalc(card: Card, intent: string): string {
  const buyer = pick(intent, card, artRoiCalcExt.buyer);
  return [
    ...fmHead("roi_calc", "roi_calculator", "P11", "N06", `ROI -- ${buyer}`, [
      "roi",
      "value-proof",
      activeFlavor.tag,
      "fixture",
    ]),
    `# ROI -- ${buyer}`,
    "",
    "## Premissas (inputs)",
    "",
    "| Input                          | Valor      |",
    "|--------------------------------|------------|",
    "| Anuncios criados / mes         | 20         |",
    "| Horas por anuncio (manual)     | 1.5 h      |",
    "| Custo/hora do operador         | R$ 45      |",
    "| Horas/anuncio com CEXAI        | 0.3 h      |",
    "| Mensalidade CEXAI              | R$ 297     |",
    "",
    "## Calculo",
    "",
    "| Metrica                        | Valor      |",
    "|--------------------------------|------------|",
    "| Horas economizadas / mes       | 24 h       |",
    "| Economia bruta / mes           | R$ 1.080   |",
    "| Custo da ferramenta / mes      | R$ 297     |",
    "| Ganho liquido / mes            | R$ 783     |",
    "| Payback                        | ~8 dias    |",
    "| Retorno anual liquido          | R$ 9.396   |",
    "| ROI (12 meses)                 | ~3.6x      |",
    "",
    "## Leitura",
    "",
    "Mesmo descontando a mensalidade, a hora economizada se paga na 1a semana.",
    "O ganho cresce linear com o volume de anuncios.",
    "",
    MOCK_NOTE,
  ].join("\n");
}

// Fixed post-judge-review: this used to carry ONLY `product` while the entire
// funnel body (stage names, volumes, critical-stage pair, ranked fixes,
// projection) stayed 100% hardcoded shopping-cart literal for every flavor --
// "Adicionar ao carro" / "Iniciar checkout" shown verbatim to an IT-support
// tenant. Mirrors the CO-DESIGNED parallel scenario already established for
// the live MOLD_FUNNEL_DIAG (molds.ts FUNNEL_FLAVOR_EXT): services gets an
// actual B2B pipeline (Visitas->Lead->Proposta->Negociacao->Contrato), not a
// vocabulary swap of cart terms. The conv%/drop% shape per stage (44/56,
// 30/70, 40/60, 50/50) is STRUCTURAL and shared across all 3 flavors -- same
// invariant as the live mold -- only stage names + volumes vary; retail's
// exact literal strings are preserved byte-for-byte below.
interface ArtFunnelDiagExt {
  product: string;
  /** 5 full "| Etapa | Volume | Conversao | Drop |" markdown table rows. */
  etapasRows: readonly [string, string, string, string, string];
  /** Critical stage pair incl. the structural "(70% de drop)" suffix. */
  etapaCritica: string;
  /** Full sentence incl. trailing period. */
  perdaAbsolutaLine: string;
  /** 4 full "| # | Correcao | Impacto | Esforco |" markdown table rows. */
  correcoesRows: readonly [string, string, string, string];
  projecaoLine1: string;
  projecaoLine2: string;
}

const ART_FUNNEL_DIAG_EXT: Record<FixtureFlavorKey, ArtFunnelDiagExt> = {
  retail: {
    product: "Funil da loja de produtos para gatos",
    etapasRows: [
      "| Visitas            | 42.000  | --        | --      |",
      "| Ver produto        | 18.480  | 44%       | 56%     |",
      "| Adicionar ao carro | 5.544   | 30%       | 70%     |",
      "| Iniciar checkout   | 2.218   | 40%       | 60%     |",
      "| Compra             | 1.109   | 50%       | 50%     |",
    ],
    etapaCritica: "Produto -> Carrinho (70% de drop)",
    perdaAbsolutaLine: "~12.936 sessoes que veem o produto e nao adicionam.",
    correcoesRows: [
      "| 1 | Mostrar frete/prazo na pagina do produto   | Alto    | Baixo   |",
      "| 2 | Prova social (reviews) acima da dobra      | Alto    | Medio   |",
      "| 3 | Botao 'comprar' fixo no mobile             | Medio   | Baixo   |",
      "| 4 | Recuperacao de carrinho por e-mail         | Medio   | Medio   |",
    ],
    projecaoLine1: "Fechar 5 p.p. do drop produto->carrinho ~= +924 carrinhos/mes",
    projecaoLine2: "(~+185 compras com a conversao atual).",
  },
  services: {
    product: "Funil da empresa de suporte de TI terceirizado",
    etapasRows: [
      "| Visitas            | 8.000   | --        | --      |",
      "| Lead capturado     | 3.520   | 44%       | 56%     |",
      "| Proposta enviada   | 1.056   | 30%       | 70%     |",
      "| Negociacao         | 422     | 40%       | 60%     |",
      "| Contrato fechado   | 211     | 50%       | 50%     |",
    ],
    etapaCritica: "Lead capturado -> Proposta enviada (70% de drop)",
    perdaAbsolutaLine: "~2.464 leads que nao recebem proposta.",
    correcoesRows: [
      "| 1 | Enviar proposta formal em ate 24h              | Alto    | Baixo   |",
      "| 2 | Case de cliente (prova social) na captura      | Alto    | Medio   |",
      "| 3 | Follow-up automatico apos o lead capturado     | Medio   | Baixo   |",
      "| 4 | Lembrete de proposta pendente por e-mail       | Medio   | Medio   |",
    ],
    projecaoLine1: "Fechar 5 p.p. do drop lead->proposta ~= +176 propostas/mes",
    projecaoLine2: "(~+35 contratos com a conversao atual).",
  },
  neutral: {
    product: "Funil da loja de produtos",
    etapasRows: [
      "| Visitas            | 20.000  | --        | --      |",
      "| Ver produto        | 8.800   | 44%       | 56%     |",
      "| Adicionar ao carro | 2.640   | 30%       | 70%     |",
      "| Iniciar checkout   | 1.056   | 40%       | 60%     |",
      "| Compra             | 528     | 50%       | 50%     |",
    ],
    etapaCritica: "Ver produto -> Adicionar ao carro (70% de drop)",
    perdaAbsolutaLine: "~6.160 sessoes que veem o produto e nao adicionam.",
    correcoesRows: [
      "| 1 | Mostrar frete/prazo na pagina do produto   | Alto    | Baixo   |",
      "| 2 | Prova social (reviews) acima da dobra      | Alto    | Medio   |",
      "| 3 | Botao 'comprar' fixo no mobile             | Medio   | Baixo   |",
      "| 4 | Recuperacao de carrinho por e-mail         | Medio   | Medio   |",
    ],
    projecaoLine1: "Fechar 5 p.p. do drop produto->carrinho ~= +440 carrinhos/mes",
    projecaoLine2: "(~+88 compras com a conversao atual).",
  },
};

const artFunnelDiagExt = ART_FUNNEL_DIAG_EXT[activeFlavor.key];

// --- funnel_diag (tool_card): per-stage metrics + biggest leak + ranked fixes -
function artFunnelDiag(card: Card, intent: string): string {
  const product = pick(intent, card, artFunnelDiagExt.product);
  return [
    ...fmHead("tc_funnel", "tool_card", "P11", "N06", `Funnel diag -- ${product}`, [
      "funnel",
      "diagnostic",
      activeFlavor.tag,
      "fixture",
    ]),
    `# Funnel diagnostic -- ${product}`,
    "",
    "## Metricas por etapa (ultimos 30 dias)",
    "",
    "| Etapa              | Volume  | Conversao | Drop    |",
    "|--------------------|---------|-----------|---------|",
    ...artFunnelDiagExt.etapasRows,
    "",
    "## Maior vazamento",
    "",
    `${artFunnelDiagExt.etapaCritica}. Maior perda absoluta do funil:`,
    artFunnelDiagExt.perdaAbsolutaLine,
    "",
    "## Correcoes priorizadas (impacto / esforco)",
    "",
    "| # | Correcao                                   | Impacto | Esforco |",
    "|---|--------------------------------------------|---------|---------|",
    ...artFunnelDiagExt.correcoesRows,
    "",
    "## Projecao",
    "",
    artFunnelDiagExt.projecaoLine1,
    artFunnelDiagExt.projecaoLine2,
    "",
    MOCK_NOTE,
  ].join("\n");
}

interface ArtDocsExt {
  subject: string;
  objetivo: string;
  passos: readonly [string, string, string, string, string];
  manutencaoRows: readonly [string, string, string];
  problemas: readonly [string, string];
}

const ART_DOCS_EXT: Record<FixtureFlavorKey, ArtDocsExt> = {
  retail: {
    subject: "Como montar e manter o Arranhador Torre",
    objetivo: "Guia passo a passo para o cliente montar a torre e manter o sisal por mais tempo.",
    passos: [
      "1. Separe as 3 secoes e a base; confira os 6 parafusos inclusos.",
      "2. Fixe a base reforcada primeiro (chave Allen inclusa).",
      "3. Rosqueie as secoes de baixo para cima; aperte sem forcar.",
      "4. Posicione perto de uma janela -- gatos preferem pontos de observacao.",
      "5. Aplique catnip no topo na primeira semana para incentivar o uso.",
    ],
    manutencaoRows: [
      "| Aspirar pelos/po        | Semanal    |",
      "| Girar a secao de sisal  | Mensal     |",
      "| Trocar o sisal          | ~12 meses  |",
    ],
    problemas: [
      "- Torre balanca: reaperte a base e nivele o piso.",
      "- Gato ignora: reposicione perto do local de descanso + catnip.",
    ],
  },
  services: {
    subject: "Como implantar e manter o Pacote de Suporte Tecnico Mensal",
    objetivo: "Guia passo a passo para o cliente ativar o suporte e manter o SLA por mais tempo.",
    passos: [
      "1. Confirme o escopo do contrato e os pontos de contato principal/secundario.",
      "2. Instale o agente de monitoramento remoto (RMM) primeiro (token do tenant).",
      "3. Configure as janelas de manutencao de baixo impacto para alto impacto.",
      "4. Posicione o SLA por escrito -- empresas preferem resposta garantida.",
      "5. Agende a revisao de 30 dias na primeira semana para incentivar o uso.",
    ],
    manutencaoRows: [
      "| Revisar chamados abertos| Semanal    |",
      "| Auditar agentes RMM     | Mensal     |",
      "| Renovar contrato de SLA | ~12 meses  |",
    ],
    problemas: [
      "- SLA estoura: reveja a escala de plantao e o roteamento de chamados.",
      "- Cliente nao usa o portal: reagende o treinamento + lembrete por e-mail.",
    ],
  },
  neutral: {
    subject: "Como montar e manter o Produto Exemplo A",
    objetivo: "Guia passo a passo para o cliente montar o produto e manter o acabamento por mais tempo.",
    passos: [
      "1. Separe as 3 secoes e a base; confira os 6 parafusos inclusos.",
      "2. Fixe a base reforcada primeiro (chave Allen inclusa).",
      "3. Rosqueie as secoes de baixo para cima; aperte sem forcar.",
      "4. Posicione em local nivelado -- superficies planas evitam oscilacao.",
      "5. Siga o manual de instrucoes na primeira semana para incentivar o uso.",
    ],
    manutencaoRows: [
      "| Limpar com pano seco    | Semanal    |",
      "| Girar a secao de apoio  | Mensal     |",
      "| Trocar o acabamento     | ~12 meses  |",
    ],
    problemas: [
      "- Produto balanca: reaperte a base e nivele o piso.",
      "- Cliente nao usa: reposicione perto do local de uso habitual.",
    ],
  },
};

const artDocsExt = ART_DOCS_EXT[activeFlavor.key];

// --- docs (knowledge_card): a HOW-TO doc (distinct from product_docs / RAG) ---
function artDocs(card: Card, intent: string): string {
  const subject = pick(intent, card, artDocsExt.subject);
  return [
    ...fmHead("kc_docs", "knowledge_card", "P01", "N04", subject, [
      "docs",
      "how-to",
      activeFlavor.tag,
      "fixture",
    ]),
    `# ${subject}`,
    "",
    "## Objetivo",
    "",
    artDocsExt.objetivo,
    "",
    "## Passos",
    "",
    ...artDocsExt.passos,
    "",
    "## Manutencao",
    "",
    "| Tarefa                  | Frequencia |",
    "|-------------------------|------------|",
    ...artDocsExt.manutencaoRows,
    "",
    "## Problemas comuns",
    "",
    ...artDocsExt.problemas,
    "",
    MOCK_NOTE,
  ].join("\n");
}

interface ArtProductDocsExt {
  product: string;
  visaoGeral: readonly [string, string];
  instalacao: readonly [string, string, string, string, string];
  fieldRows: readonly [string, string, string, string];
  faq: readonly [string, string];
}

const ART_PRODUCT_DOCS_EXT: Record<FixtureFlavorKey, ArtProductDocsExt> = {
  retail: {
    product: "Comedouro Automatico WiFi -- setup e referencia",
    visaoGeral: [
      "Comedouro automatico com 4 refeicoes programaveis, reservatorio de 3L e",
      "controle pelo app (WiFi 2.4GHz). Documentacao de instalacao + referencia.",
    ],
    instalacao: [
      "1. Encaixe o reservatorio na base ate o clique.",
      "2. Ligue na tomada (5V) ou use 3 pilhas D (backup).",
      "3. No app, toque em 'Adicionar dispositivo' -> escaneie o QR da base.",
      "4. Conecte ao WiFi 2.4GHz (5GHz nao suportado).",
      "5. Programe ate 4 horarios + porcao (1-10 doses).",
    ],
    fieldRows: [
      "| porcao       | inteiro | 1-10 doses   | 2       |",
      "| horarios     | lista   | ate 4        | 2       |",
      "| som_chamada  | bool    | on/off       | on      |",
      "| modo_ferias  | bool    | on/off       | off     |",
    ],
    faq: [
      "- Trava na racao umida? Use apenas racao seca de 5-12mm.",
      "- Sem internet? As porcoes programadas seguem rodando offline.",
    ],
  },
  services: {
    product: "Agente de Monitoramento Remoto (RMM) -- setup e referencia",
    visaoGeral: [
      "Agente de monitoramento com heartbeat continuo, cache local e",
      "controle pelo painel web. Documentacao de instalacao + referencia.",
    ],
    instalacao: [
      "1. Baixe o instalador no portal do cliente e execute como administrador.",
      "2. Informe o token do tenant (enviado por e-mail) na tela de ativacao.",
      "3. No painel, toque em 'Adicionar dispositivo' -> aguarde status 'Online'.",
      "4. Selecione o grupo de politicas (Estacao/Servidor).",
      "5. Programe ate 4 janelas de manutencao + nivel de alerta.",
    ],
    fieldRows: [
      "| nivel_alerta      | enum    | baixo/medio/alto | medio |",
      "| janelas_manutencao| lista   | ate 4        | 2       |",
      "| modo_manutencao   | bool    | on/off       | off     |",
      "| alerta_disco_cheio| bool    | on/off       | on      |",
    ],
    faq: [
      "- Monitora Linux? Nao. Calibrado para Windows 10/11 e Server 2016+.",
      "- Sem internet? As politicas salvas seguem rodando offline (cache local).",
    ],
  },
  neutral: {
    product: "Dispenser Inteligente WiFi -- setup e referencia",
    visaoGeral: [
      "Dispenser automatico com 4 disparos programaveis, reservatorio de 3L e",
      "controle pelo app (WiFi 2.4GHz). Documentacao de instalacao + referencia.",
    ],
    instalacao: [
      "1. Encaixe o reservatorio na base ate o clique.",
      "2. Ligue na tomada (5V) ou use 3 pilhas D (backup).",
      "3. No app, toque em 'Adicionar dispositivo' -> escaneie o QR da base.",
      "4. Conecte ao WiFi 2.4GHz (5GHz nao suportado).",
      "5. Programe ate 4 horarios + dose (1-10 disparos).",
    ],
    fieldRows: [
      "| dose         | inteiro | 1-10 disparos| 2       |",
      "| horarios     | lista   | ate 4        | 2       |",
      "| som_notificacao | bool | on/off       | on      |",
      "| modo_pausa   | bool    | on/off       | off     |",
    ],
    faq: [
      "- Trava com conteudo umido? Use apenas material seco de 5-12mm.",
      "- Sem internet? Os disparos programados seguem rodando offline.",
    ],
  },
};

const artProductDocsExt = ART_PRODUCT_DOCS_EXT[activeFlavor.key];

// --- product_docs (knowledge_card): a product SETUP/reference doc -------------
function artProductDocs(card: Card, intent: string): string {
  const product = pick(intent, card, artProductDocsExt.product);
  return [
    ...fmHead("kc_proddocs", "knowledge_card", "P01", "N04", product, [
      "product_docs",
      "setup",
      "reference",
      activeFlavor.tag,
      "fixture",
    ]),
    `# ${product}`,
    "",
    "## Visao geral",
    "",
    ...artProductDocsExt.visaoGeral,
    "",
    "## Instalacao rapida",
    "",
    ...artProductDocsExt.instalacao,
    "",
    "## Referencia de campos",
    "",
    "| Campo        | Tipo    | Faixa        | Default |",
    "|--------------|---------|--------------|---------|",
    ...artProductDocsExt.fieldRows,
    "",
    "## FAQ",
    "",
    ...artProductDocsExt.faq,
    "",
    MOCK_NOTE,
  ].join("\n");
}

interface ArtTierDesignerExt {
  product: string;
  tierHeader: string;
  rows: readonly [string, string, string, string, string, string, string];
  gating: readonly [string, string];
}

const ART_TIER_DESIGNER_EXT: Record<FixtureFlavorKey, ArtTierDesignerExt> = {
  retail: {
    product: "Clube de Assinatura Premium",
    tierHeader: "| Feature                   | Filhote   | Adulto (*) | Multipet   |",
    rows: [
      "| Preco / mes               | R$ 39     | R$ 89      | R$ 169     |",
      "| Gatos cobertos            | 1         | 1          | Ate 4      |",
      "| Caixa de racao            | 2kg       | 5kg        | 12kg       |",
      "| Petiscos premium          | --        | 2/mes      | 5/mes      |",
      "| Brinquedo do mes          | --        | 1          | 2          |",
      "| Frete gratis              | --        | Sim        | Sim        |",
      "| Teleorientacao veterinaria| --        | --         | Incluida   |",
    ],
    gating: [
      "- Petisco premium + frete gratis comecam no Adulto (empurra upgrade do Filhote).",
      "- Multipet desbloqueia cobertura para >1 gato + vet -- alvo de tutores 2+ gatos.",
    ],
  },
  services: {
    product: "Plano de Suporte de TI Gerenciado",
    tierHeader: "| Feature                   | Basico    | Essencial (*)| Corporate  |",
    rows: [
      "| Preco / mes               | R$ 39     | R$ 89      | R$ 169     |",
      "| Estacoes cobertas         | 1         | 1          | Ate 4      |",
      "| Horas de suporte incluso  | 2h        | 5h         | 12h        |",
      "| Consultoria de seguranca  | --        | 2/mes      | 5/mes      |",
      "| Relatorio executivo       | --        | 1          | 2          |",
      "| Onboarding gratuito       | --        | Sim        | Sim        |",
      "| Suporte de emergencia 24/7| --        | --         | Incluida   |",
    ],
    gating: [
      "- Consultoria de seguranca + onboarding gratuito comecam no Essencial (empurra upgrade do Basico).",
      "- Corporate desbloqueia cobertura para >1 filial + suporte 24/7 -- alvo de empresas multi-filial.",
    ],
  },
  neutral: {
    product: "Clube de Assinatura Exemplo",
    tierHeader: "| Feature                   | Basico    | Padrao (*) | Familia    |",
    rows: [
      "| Preco / mes               | R$ 39     | R$ 89      | R$ 169     |",
      "| Membros cobertos          | 1         | 1          | Ate 4      |",
      "| Caixa mensal              | 2kg       | 5kg        | 12kg       |",
      "| Brinde premium            | --        | 2/mes      | 5/mes      |",
      "| Item extra do mes         | --        | 1          | 2          |",
      "| Frete gratis              | --        | Sim        | Sim        |",
      "| Consultoria online        | --        | --         | Incluida   |",
    ],
    gating: [
      "- Brinde premium + frete gratis comecam no Padrao (empurra upgrade do Basico).",
      "- Familia desbloqueia cobertura para >1 membro + consultoria -- alvo de clientes multi-membro.",
    ],
  },
};

const artTierDesignerExt = ART_TIER_DESIGNER_EXT[activeFlavor.key];

// --- tier_designer (subscription_tier): a plan matrix (tiers x features) ------
function artTierDesigner(card: Card, intent: string): string {
  const product = pick(intent, card, artTierDesignerExt.product);
  return [
    ...fmHead("st_tiers", "subscription_tier", "P11", "N06", `Plan matrix -- ${product}`, [
      "subscription_tier",
      "plan-matrix",
      activeFlavor.tag,
      "fixture",
    ]),
    `# Plan matrix -- ${product}`,
    "",
    "Matriz de planos (tiers x features) com gating progressivo.",
    "",
    artTierDesignerExt.tierHeader,
    "|---------------------------|-----------|------------|------------|",
    ...artTierDesignerExt.rows,
    "| Pausar/trocar quando quiser| Sim      | Sim        | Sim        |",
    "",
    "(*) Tier-ancora recomendado (melhor custo-beneficio).",
    "",
    "## Regras de gating",
    "",
    ...artTierDesignerExt.gating,
    "",
    "## Notas de migracao",
    "",
    "Upgrade e imediato (pro-rata); downgrade vale no proximo ciclo.",
    "",
    MOCK_NOTE,
  ].join("\n");
}

interface ArtEmailBuilderExt {
  campaign: string;
  assuntoA: string;
  assuntoB: string;
  preheader: string;
  heroTitulo: string;
  heroSub: string;
  heroBotao: string;
  provaBullets: string;
  provaSelo: string;
  oferta: string;
  ofertaBotao: string;
  rodapeEndereco: string;
}

const ART_EMAIL_BUILDER_EXT: Record<FixtureFlavorKey, ArtEmailBuilderExt> = {
  retail: {
    campaign: "Lancamento do Arranhador Torre 1,2m",
    assuntoA: "A torre que seu gato vai dominar (e que dura)",
    assuntoB: "Novidade: arranhador que aguenta gato grande -- 15% OFF",
    preheader: "Base reforcada, sisal substituivel e frete gratis acima de R$ 250.",
    heroTitulo: "Chegou a Torre 1,2m",
    heroSub: "Feita para gatos adultos e grandes.",
    heroBotao: "Quero a minha",
    provaBullets: "   - 3 bullets: base antiderrapante / sisal trocavel / montagem em 5 min",
    provaSelo: "4.7 estrelas (2.143 avaliacoes)",
    oferta: "15% OFF no lancamento + frete gratis acima de R$ 250.",
    ofertaBotao: "Comprar com desconto",
    rodapeEndereco: "loja",
  },
  services: {
    campaign: "Lancamento do Pacote de Suporte Tecnico Mensal",
    assuntoA: "O suporte que sua equipe de TI vai confiar (e que nao falha)",
    assuntoB: "Novidade: suporte que resolve chamado critico em 2h -- 15% OFF",
    preheader: "SLA por escrito, atendimento remoto 24/7 e onboarding em 48h.",
    heroTitulo: "Chegou o Suporte Mensal",
    heroSub: "Feito para empresas de pequeno e medio porte.",
    heroBotao: "Quero contratar",
    provaBullets: "   - 3 bullets: SLA por escrito / atendimento 24/7 / onboarding em 48h",
    provaSelo: "4.8 estrelas (312 avaliacoes)",
    oferta: "15% OFF na contratacao anual + auditoria de seguranca gratis.",
    ofertaBotao: "Garantir desconto",
    rodapeEndereco: "empresa",
  },
  neutral: {
    campaign: "Lancamento do Produto Exemplo A",
    assuntoA: "O produto que seu dia a dia vai dominar (e que dura)",
    assuntoB: "Novidade: produto que aguenta uso diario intenso -- 15% OFF",
    preheader: "Garantia estendida, suporte pos-venda e frete gratis acima de um valor minimo.",
    heroTitulo: "Chegou o Produto Exemplo A",
    heroSub: "Feito para uso diario intenso.",
    heroBotao: "Quero o meu",
    provaBullets: "   - 3 bullets: garantia estendida / suporte pos-venda / entrega rapida",
    provaSelo: "4.7 estrelas (2.143 avaliacoes)",
    oferta: "15% OFF no lancamento + frete gratis acima de um valor minimo.",
    ofertaBotao: "Comprar com desconto",
    rodapeEndereco: "loja",
  },
};

const artEmailBuilderExt = ART_EMAIL_BUILDER_EXT[activeFlavor.key];

// --- email_builder (prompt_template): subject + preheader + body blocks -------
function artEmailBuilder(card: Card, intent: string): string {
  const campaign = pick(intent, card, artEmailBuilderExt.campaign);
  return [
    ...fmHead("pt_email", "prompt_template", "P03", "N02", `Email -- ${campaign}`, [
      "email",
      "campaign",
      activeFlavor.tag,
      "fixture",
    ]),
    `# Marketing email -- ${campaign}`,
    "",
    "## Linha de assunto (A/B)",
    "",
    `- A: ${artEmailBuilderExt.assuntoA}`,
    `- B: ${artEmailBuilderExt.assuntoB}`,
    "",
    "## Preheader",
    "",
    artEmailBuilderExt.preheader,
    "",
    "## Corpo (blocos)",
    "",
    "1. HERO",
    `   - Titulo: ${artEmailBuilderExt.heroTitulo}`,
    `   - Sub: ${artEmailBuilderExt.heroSub}`,
    `   - Botao: ${artEmailBuilderExt.heroBotao}`,
    "",
    "2. PROVA",
    artEmailBuilderExt.provaBullets,
    `   - Selo: ${artEmailBuilderExt.provaSelo}`,
    "",
    "3. OFERTA",
    `   - ${artEmailBuilderExt.oferta}`,
    `   - Botao: ${artEmailBuilderExt.ofertaBotao}`,
    "",
    "4. RODAPE",
    `   - Link de descadastro + endereco da ${artEmailBuilderExt.rodapeEndereco} (CAN-SPAM/LGPD).`,
    "",
    MOCK_NOTE,
  ].join("\n");
}

interface ArtOauthConnectExt {
  provider: string;
  conectarSubstantivo: string;
  identityRows: readonly [string, string, string, string, string, string];
}

const ART_OAUTH_CONNECT_EXT: Record<FixtureFlavorKey, ArtOauthConnectExt> = {
  retail: {
    provider: "Mercado Livre",
    conectarSubstantivo: "loja",
    identityRows: [
      "| provider       | mercadolivre                                     |",
      "| client_id      | <SLOT: ML_CLIENT_ID>                             |",
      "| client_secret  | <SLOT: ML_CLIENT_SECRET>  (Vault -- nunca aqui)  |",
      "| auth_url       | https://auth.mercadolivre.com.br/authorization   |",
      "| token_url      | https://api.mercadolibre.com/oauth/token         |",
      "| grant_type     | authorization_code                               |",
    ],
  },
  services: {
    provider: "Google",
    conectarSubstantivo: "empresa",
    identityRows: [
      "| provider       | google                                            |",
      "| client_id      | <SLOT: GOOGLE_CLIENT_ID>                         |",
      "| client_secret  | <SLOT: GOOGLE_CLIENT_SECRET>  (Vault -- nunca aqui)|",
      "| auth_url       | https://accounts.google.com/o/oauth2/v2/auth     |",
      "| token_url      | https://oauth2.googleapis.com/token              |",
      "| grant_type     | authorization_code                               |",
    ],
  },
  neutral: {
    provider: "Mercado Livre",
    conectarSubstantivo: "loja",
    identityRows: [
      "| provider       | mercadolivre                                     |",
      "| client_id      | <SLOT: ML_CLIENT_ID>                             |",
      "| client_secret  | <SLOT: ML_CLIENT_SECRET>  (Vault -- nunca aqui)  |",
      "| auth_url       | https://auth.mercadolivre.com.br/authorization   |",
      "| token_url      | https://api.mercadolibre.com/oauth/token         |",
      "| grant_type     | authorization_code                               |",
    ],
  },
};

const artOauthConnectExt = ART_OAUTH_CONNECT_EXT[activeFlavor.key];

// --- oauth_connect (oauth_app_config): typed OAuth config (SLOTS only) --------
function artOauthConnect(card: Card, intent: string): string {
  const provider = pick(intent, card, artOauthConnectExt.provider);
  return [
    ...fmHead("oauth_cfg", "oauth_app_config", "P04", "N03", `OAuth -- ${provider}`, [
      "oauth",
      "integration",
      "config",
      "fixture",
    ]),
    `# OAuth app config -- ${provider}`,
    "",
    `Config tipada para conectar a ${artOauthConnectExt.conectarSubstantivo} ao provedor. SLOTS de credencial sao`,
    "placeholders -- nenhum segredo real e gravado nesta superficie.",
    "",
    "## Identidade do app",
    "",
    "| Campo          | Valor                                            |",
    "|----------------|--------------------------------------------------|",
    ...artOauthConnectExt.identityRows,
    "",
    "## Redirect URIs",
    "",
    "- https://app.example.com/oauth/callback",
    "- http://localhost:3000/oauth/callback  (dev)",
    "",
    "## Scopes",
    "",
    "| Scope   | Para que serve                     |",
    "|---------|------------------------------------|",
    "| read    | Ler anuncios, pedidos e perguntas  |",
    "| write   | Criar/editar anuncios              |",
    "| offline_access | Refresh token (sessao longa)|",
    "",
    "## Token handling",
    "",
    "- access_token: ~6h; refresh_token rotacionado a cada uso.",
    "- Armazenamento: Vault por tenant (nunca no cliente, nunca no repo).",
    "",
    MOCK_NOTE,
  ].join("\n");
}

interface ArtCompetitorBenchmarkExt {
  product: string;
  ourBrand: string;
  competitors: readonly [string, string, string];
  scoreRows: readonly [string, string, string, string, string, string];
  leitura: readonly [string, string, string];
}

const ART_COMPETITOR_BENCHMARK_EXT: Record<FixtureFlavorKey, ArtCompetitorBenchmarkExt> = {
  retail: {
    product: "Arranhador Torre (produto) vs concorrentes",
    ourBrand: "Minha Loja",
    competitors: ["PetShop Premium", "MiauHouse", "GatoFeliz"],
    scoreRows: [
      "| Preco (25%)          | 4.5   | 2.5             | 4.0       | 4.8       |",
      "| Durabilidade (25%)   | 4.7   | 4.5             | 3.0       | 2.8       |",
      "| Avaliacoes (20%)     | 4.0   | 4.7             | 4.4       | 4.2       |",
      "| Frete/prazo (15%)    | 4.2   | 4.0             | 3.5       | 3.8       |",
      "| Pos-venda (15%)      | 4.3   | 4.6             | 3.2       | 3.0       |",
      "| **Score ponderado**  | **4.36** | **3.92**     | **3.66**  | **3.74**  |",
    ],
    leitura: [
      "Minha Loja lidera o score ponderado por equilibrar preco competitivo com a maior",
      "durabilidade da amostra. PetShop Premium vence em reputacao/pos-venda mas perde",
      "muito em preco. GatoFeliz e o mais barato, porem o mais fraco em durabilidade.",
    ],
  },
  services: {
    product: "Pacote de Suporte de TI (produto) vs concorrentes",
    ourBrand: "Minha Empresa",
    competitors: ["TechCare Solucoes", "InfraJa Suporte", "NuvemCerta TI"],
    scoreRows: [
      "| Preco (25%)          | 4.5   | 2.5             | 4.0       | 4.8       |",
      "| Confiabilidade (25%) | 4.7   | 4.5             | 3.0       | 2.8       |",
      "| Avaliacoes (20%)     | 4.0   | 4.7             | 4.4       | 4.2       |",
      "| SLA/resposta (15%)   | 4.2   | 4.0             | 3.5       | 3.8       |",
      "| Pos-contratacao (15%)| 4.3   | 4.6             | 3.2       | 3.0       |",
      "| **Score ponderado**  | **4.36** | **3.92**     | **3.66**  | **3.74**  |",
    ],
    leitura: [
      "Minha Empresa lidera o score ponderado por equilibrar preco competitivo com a maior",
      "confiabilidade da amostra. TechCare Solucoes vence em reputacao/pos-contratacao mas",
      "perde muito em preco. NuvemCerta TI e a mais barata, porem a mais fraca em SLA.",
    ],
  },
  neutral: {
    product: "Produto Exemplo A (produto) vs concorrentes",
    ourBrand: "Minha Empresa",
    competitors: ["Concorrente A", "Concorrente B", "Concorrente C"],
    scoreRows: [
      "| Preco (25%)          | 4.5   | 2.5             | 4.0       | 4.8       |",
      "| Durabilidade (25%)   | 4.7   | 4.5             | 3.0       | 2.8       |",
      "| Avaliacoes (20%)     | 4.0   | 4.7             | 4.4       | 4.2       |",
      "| Frete/prazo (15%)    | 4.2   | 4.0             | 3.5       | 3.8       |",
      "| Pos-venda (15%)      | 4.3   | 4.6             | 3.2       | 3.0       |",
      "| **Score ponderado**  | **4.36** | **3.92**     | **3.66**  | **3.74**  |",
    ],
    leitura: [
      "Minha Empresa lidera o score ponderado por equilibrar preco competitivo com a maior",
      "durabilidade da amostra. Concorrente A vence em reputacao/pos-venda mas perde",
      "muito em preco. Concorrente C e o mais barato, porem o mais fraco em durabilidade.",
    ],
  },
};

const artCompetitorBenchmarkExt = ART_COMPETITOR_BENCHMARK_EXT[activeFlavor.key];

// --- competitor_benchmark (competitive_matrix): rivals x dims, scored ---------
function artCompetitorBenchmark(card: Card, intent: string): string {
  const product = pick(intent, card, artCompetitorBenchmarkExt.product);
  const [c1, c2, c3] = artCompetitorBenchmarkExt.competitors;
  return [
    ...fmHead("cmx_bench", "competitive_matrix", "P01", "N01", `Benchmark -- ${product}`, [
      "competitive_matrix",
      "benchmark",
      activeFlavor.tag,
      "fixture",
    ]),
    `# Competitor benchmark -- ${product}`,
    "",
    "Rivais pontuados (0-5) nas dimensoes que importam para a categoria.",
    "",
    `| Dimensao (peso)      | ${artCompetitorBenchmarkExt.ourBrand} | ${c1} | ${c2} | ${c3} |`,
    "|----------------------|-------|-----------------|-----------|-----------|",
    ...artCompetitorBenchmarkExt.scoreRows,
    "",
    "## Leitura de posicionamento",
    "",
    ...artCompetitorBenchmarkExt.leitura,
    "",
    "## Onde ganhar",
    "",
    "- Atacar o ponto fraco do lider (preco) sem ceder durabilidade.",
    "- Fechar o gap de reviews com prova social + apos-compra ativo.",
    "",
    MOCK_NOTE,
  ].join("\n");
}

interface ArtLandingExt {
  product: string;
  heroH1: string;
  heroSub: string;
  ctaSecundario: string;
  visual: string;
  secoes: readonly [string, string, string, string, string, string];
  ctaRepetidoAcao: string;
  seoRows: readonly [string, string, string, string, string];
}

const ART_LANDING_EXT: Record<FixtureFlavorKey, ArtLandingExt> = {
  retail: {
    product: "Arranhador Torre para Gatos 1,2m",
    heroH1: "A torre que seu gato domina -- e que nao desmonta",
    heroSub: "Base reforcada antiderrapante + sisal substituivel.",
    ctaSecundario: "Ver video de montagem",
    visual: "gato no topo da torre (foto hero).",
    secoes: [
      "1. Prova social -- 4.7 estrelas, 2.143 avaliacoes, selos de loja.",
      "2. Beneficios -- 3 cards: durabilidade / seguranca / facil montagem.",
      "3. Comparativo -- Minha Loja vs arranhador comum (tabela).",
      "4. Como funciona -- 3 passos com icones.",
      "5. FAQ -- aguenta gato grande? troca o sisal? frete?",
      "6. Oferta final -- preco R$ 199 + frete gratis acima de R$ 250.",
    ],
    ctaRepetidoAcao: "Comprar",
    seoRows: [
      "| title            | Arranhador Torre 1,2m para Gatos | Base Reforcada    |",
      "| meta description | Torre robusta para gatos adultos. Frete gratis...   |",
      "| slug             | /arranhador-torre-gatos-1-2m                         |",
      "| h1               | A torre que seu gato domina                          |",
      "| keywords         | arranhador para gatos, torre arranhador             |",
    ],
  },
  services: {
    product: "Pacote de Suporte Tecnico Mensal",
    heroH1: "O suporte que sua equipe de TI vai confiar -- e que nao falha",
    heroSub: "SLA por escrito + atendimento remoto 24/7.",
    ctaSecundario: "Ver como funciona o onboarding",
    visual: "equipe em reuniao de suporte (foto hero).",
    secoes: [
      "1. Prova social -- 4.8 estrelas, 312 avaliacoes, selos de certificacao.",
      "2. Beneficios -- 3 cards: confiabilidade / seguranca / onboarding rapido.",
      "3. Comparativo -- Minha Empresa vs suporte de TI comum (tabela).",
      "4. Como funciona -- 3 passos com icones.",
      "5. FAQ -- atende empresa pequena? SLA garantido? prazo de ativacao?",
      "6. Oferta final -- preco R$ 397/mes + auditoria de seguranca gratis.",
    ],
    ctaRepetidoAcao: "Falar com especialista",
    seoRows: [
      "| title            | Suporte de TI Mensal para Empresas | SLA por Escrito|",
      "| meta description | Suporte robusto para PMEs. SLA por escrito...       |",
      "| slug             | /suporte-de-ti-mensal-para-empresas                  |",
      "| h1               | O suporte que sua equipe de TI vai confiar           |",
      "| keywords         | suporte de ti para empresas, suporte tecnico remoto |",
    ],
  },
  neutral: {
    product: "Produto Exemplo A",
    heroH1: "O produto que seu dia a dia precisa -- e que nao falha",
    heroSub: "Garantia estendida + suporte pos-venda.",
    ctaSecundario: "Ver como funciona",
    visual: "produto em cena de estudio (foto hero).",
    secoes: [
      "1. Prova social -- 4.7 estrelas, 2.143 avaliacoes, selos de confianca.",
      "2. Beneficios -- 3 cards: durabilidade / seguranca / entrega rapida.",
      "3. Comparativo -- Minha Empresa vs produto comum (tabela).",
      "4. Como funciona -- 3 passos com icones.",
      "5. FAQ -- tem garantia estendida? troca facil? frete?",
      "6. Oferta final -- preco R$ 99 + frete gratis acima de um valor minimo.",
    ],
    ctaRepetidoAcao: "Comprar",
    seoRows: [
      "| title            | Produto Exemplo A | Garantia Estendida               |",
      "| meta description | Produto robusto para uso diario. Frete gratis...    |",
      "| slug             | /produto-exemplo-a                                   |",
      "| h1               | O produto que seu dia a dia precisa                  |",
      "| keywords         | produto exemplo, categoria exemplo                   |",
    ],
  },
};

const artLandingExt = ART_LANDING_EXT[activeFlavor.key];

// --- landing (landing_page): hero + sections + CTA + SEO outline --------------
function artLanding(card: Card, intent: string): string {
  const product = pick(intent, card, artLandingExt.product);
  return [
    ...fmHead("lp_landing", "landing_page", "P05", "N03", `Landing -- ${product}`, [
      "landing_page",
      "conversion",
      activeFlavor.tag,
      "fixture",
    ]),
    `# Landing page outline -- ${product}`,
    "",
    "## Hero",
    "",
    `- H1: ${artLandingExt.heroH1}`,
    `- Sub: ${artLandingExt.heroSub}`,
    `- CTA primario: ${artLandingExt.ctaRepetidoAcao} agora  |  CTA secundario: ${artLandingExt.ctaSecundario}`,
    `- Visual: ${artLandingExt.visual}`,
    "",
    "## Secoes",
    "",
    ...artLandingExt.secoes,
    "",
    "## CTA repetido",
    "",
    `Botao fixo no mobile + CTA ao fim de cada secao (mesma acao: ${artLandingExt.ctaRepetidoAcao}).`,
    "",
    "## SEO",
    "",
    "| Campo            | Valor                                               |",
    "|------------------|-----------------------------------------------------|",
    ...artLandingExt.seoRows,
    "",
    MOCK_NOTE,
  ].join("\n");
}

interface ArtCustomIntakeExt {
  title: string;
  fieldRows: readonly [string, string, string, string, string, string, string, string];
}

const ART_CUSTOM_INTAKE_EXT: Record<FixtureFlavorKey, ArtCustomIntakeExt> = {
  retail: {
    title: "Ficha de intake de cliente -- pet shop",
    fieldRows: [
      "| nome_tutor       | text      | sim         | Nome do responsavel     |",
      "| email            | email     | sim         | Contato principal       |",
      "| whatsapp         | tel       | sim         | DDD + numero            |",
      "| nome_pet         | text      | sim         | Nome do gato/pet        |",
      "| especie          | select    | sim         | gato / cachorro / outro |",
      "| porte            | select    | nao         | pequeno / medio / grande|",
      "| necessidades     | textarea  | nao         | Restricoes, alergias    |",
      "| aceite_lgpd      | checkbox  | sim         | Consentimento de dados  |",
    ],
  },
  services: {
    title: "Ficha de intake de cliente -- suporte de TI",
    fieldRows: [
      "| nome_contato     | text      | sim         | Nome do responsavel     |",
      "| email            | email     | sim         | Contato principal       |",
      "| whatsapp         | tel       | sim         | DDD + numero            |",
      "| nome_empresa     | text      | sim         | Nome da empresa         |",
      "| porte_empresa    | select    | sim         | pequena / media / grande|",
      "| segmento         | select    | nao         | varejo / servicos / outro|",
      "| necessidades     | textarea  | nao         | Requisitos, restricoes  |",
      "| aceite_lgpd      | checkbox  | sim         | Consentimento de dados  |",
    ],
  },
  neutral: {
    title: "Ficha de intake de cliente -- loja",
    fieldRows: [
      "| nome_cliente     | text      | sim         | Nome do responsavel     |",
      "| email            | email     | sim         | Contato principal       |",
      "| whatsapp         | tel       | sim         | DDD + numero            |",
      "| produto_interesse| text      | sim         | Produto de interesse    |",
      "| categoria        | select    | sim         | categoria_a / categoria_b / outro |",
      "| porte            | select    | nao         | pequeno / medio / grande|",
      "| necessidades     | textarea  | nao         | Restricoes, preferencias|",
      "| aceite_lgpd      | checkbox  | sim         | Consentimento de dados  |",
    ],
  },
};

const artCustomIntakeExt = ART_CUSTOM_INTAKE_EXT[activeFlavor.key];

// --- custom_intake_form (custom_intake_form): a tenant intake form spec -------
function artCustomIntake(card: Card, intent: string): string {
  const title = pick(intent, card, artCustomIntakeExt.title);
  return [
    ...fmHead("cif_intake", "custom_intake_form", "P05", "N03", title, [
      "custom_intake_form",
      "overlay",
      activeFlavor.tag,
      "fixture",
    ]),
    `# ${title}`,
    "",
    "Formulario de intake especifico do tenant (vindo do overlay).",
    "",
    "## Campos",
    "",
    "| Campo            | Tipo      | Obrigatorio | Observacao              |",
    "|------------------|-----------|-------------|-------------------------|",
    ...artCustomIntakeExt.fieldRows,
    "",
    "## Pos-envio",
    "",
    "- Grava no data plane do tenant (RLS por tenant_id).",
    "- Dispara e-mail de boas-vindas + tag de segmento.",
    "",
    MOCK_NOTE,
  ].join("\n");
}

/** Per-capability dispatch -> a tailored, honest-mock artifact of the card's kind.
 *  Unknown capabilities fall back to the generic knowledge_card (degrade-never). */
function buildArtifact(card: Card, intent: string): string {
  const builders: Record<string, (c: Card, i: string) => string> = {
    research: artResearch,
    ads: artAds,
    media_photo: artMediaPhoto,
    pricing: artPricing,
    roi_calc: artRoiCalc,
    funnel_diag: artFunnelDiag,
    docs: artDocs,
    product_docs: artProductDocs,
    tier_designer: artTierDesigner,
    email_builder: artEmailBuilder,
    oauth_connect: artOauthConnect,
    competitor_benchmark: artCompetitorBenchmark,
    landing: artLanding,
    custom_intake_form: artCustomIntake,
  };
  const build = builders[card.capability];
  return build ? build(card, intent) : fakeArtifact(card.capability, intent);
}

/** Generic fallback artifact (any capability without a tailored builder). */
function fakeArtifact(capability: string, intent: string): string {
  const stamp = new Date().toISOString();
  return [
    "---",
    `id: kc_${capability}_${Math.random().toString(36).slice(2, 8)}`,
    "kind: knowledge_card",
    "pillar: P01",
    "nucleus: N01",
    `title: "${intent.slice(0, 60) || "Untitled brief"}"`,
    "version: 0.1.0",
    "quality: null",
    `created: "${stamp}"`,
    "mock: true",
    "tags: [research, competitive, fixture]",
    "---",
    "",
    `# ${intent || "Research brief"}`,
    "",
    "## Summary",
    "",
    "A typed knowledge card produced by the CEXAI runtime in FIXTURES mode.",
    "This is mock output so the dashboard renders end-to-end without a backend.",
    "",
    "## Findings",
    "",
    "| Dimension | Observation | Confidence |",
    "|-----------|-------------|------------|",
    "| Market    | Demand is concentrated in mid-market.  | 0.78 |",
    "| Pricing   | Competitors cluster at three tiers.    | 0.71 |",
    "| Gap       | No sovereign / self-host option ships. | 0.83 |",
    "",
    "## Sources",
    "",
    "- (fixture) example-source-a.example",
    "- (fixture) example-source-b.example",
    "",
    MOCK_NOTE,
  ].join("\n");
}

// --- FLAGSHIP product-research fixture (capability "pesquisa_produto") --------
//
// A realistic, fully-populated 30-field ProductResearchResult so ResearchResultView
// renders the rich report end-to-end offline. mock:true is HONEST -- it surfaces the
// "dados simulados" notice (the anti-hallucination contract, n05 S6.2). The numbers
// are a coherent sample (a pet-product import case), NOT a real scrape.

const FIXTURE_RESEARCH: ProductResearchResult = {
  // identity / provenance
  tenant_id: FIXTURE_TENANT.tenant_id,
  run_id: "pq_demo_001",
  product_id: activeFlavor.productId,
  product_name: activeFlavor.productName,
  run_timestamp: new Date(Date.now() - 1000 * 60 * 4).toISOString(),
  data_freshness: new Date(Date.now() - 1000 * 60 * 60 * 20).toISOString(),
  marketplaces_queried: ["Mercado Livre", "Amazon BR", "Magalu", "Shopee"],
  marketplaces_failed: ["Shopee"],
  data_sources: { mercadolivre: 18, amazon: 11, magalu: 7 },
  // gate
  confidence_score: 8.4,
  ready_for_ads: true,
  // pricing
  price_band_min: 129,
  price_band_max: 389,
  price_avg: 232,
  sweet_spot_price: 199,
  // competitive
  top_competitor_name: activeFlavor.topCompetitorFull,
  top_competitor_rating: 4.7,
  top_competitor_reviews: 2143,
  competitors_count: 23,
  gaps: [...activeFlavor.gaps],
  opportunities: [...activeFlavor.opportunities],
  differentiation_angle: activeFlavor.differentiationAngle,
  recommended_positioning: activeFlavor.recommendedPositioning,
  // keywords / SEO
  head_terms: [...activeFlavor.seo.headTerms],
  longtails: [...activeFlavor.seo.longtails],
  synonyms: [...activeFlavor.seo.synonyms],
  seo_inbound: [...activeFlavor.seo.seoInbound],
  seo_outbound: [...activeFlavor.seo.seoOutbound],
  negative_keywords: [...activeFlavor.seo.negativeKeywords],
  // filing
  category_paths: {
    mercadolivre: activeFlavor.categoryPaths.a,
    amazon: activeFlavor.categoryPaths.b,
    magalu: activeFlavor.categoryPaths.c,
  },
  // anti-hallucination
  mock: true,
};

/** Build the canonical MD-frontmatter projection for a research payload (mirrors the
 *  backend cex_output_contract MD shape: yaml-ish frontmatter + code-fenced sections).
 *  This is what ?render_format=md returns; the run's ``artifact`` carries the same. */
function researchMd(r: ProductResearchResult): string {
  const scalar = (v: unknown): string => {
    if (v === null || v === undefined) return "";
    if (Array.isArray(v)) return v.map((x) => String(x)).join(", ");
    if (typeof v === "object") {
      return Object.entries(v as Record<string, unknown>)
        .map(([k, val]) => `${k}=${String(val)}`)
        .join(", ");
    }
    return String(v);
  };
  const fm = [
    "---",
    "schema_version: '1.0'",
    "schema_id: pesquisa_produto",
    `mock: ${r.mock === true}`,
    `confidence_score: ${r.confidence_score ?? 0}`,
    `ready_for_ads: ${r.ready_for_ads === true}`,
    `product_name: "${r.product_name ?? ""}"`,
    `price_band_min: ${r.price_band_min ?? 0}`,
    `price_band_max: ${r.price_band_max ?? 0}`,
    `price_avg: ${r.price_avg ?? 0}`,
    `sweet_spot_price: ${r.sweet_spot_price ?? 0}`,
    `competitors_count: ${r.competitors_count ?? 0}`,
    "anuncio_open_vars:",
    `  usps: [${[...(r.opportunities ?? []), r.differentiation_angle]
      .filter(Boolean)
      .map((x) => `"${x}"`)
      .join(", ")}]`,
    `  competitor_gaps: [${(r.gaps ?? []).map((x) => `"${x}"`).join(", ")}]`,
    `  sweet_spot_price: ${r.sweet_spot_price ?? 0}`,
    "---",
  ].join("\n");
  const sec = (title: string, fields: [string, unknown][]): string =>
    [
      `## ${title}`,
      "",
      "```",
      ...fields.map(([k, v]) => `${k}: ${scalar(v)}`),
      "```",
      "",
    ].join("\n");
  return [
    fm,
    "",
    `# ${r.product_name ?? "Pesquisa de Produto"}`,
    "",
    sec("Preco de Mercado", [
      ["price_band_min", r.price_band_min],
      ["price_avg", r.price_avg],
      ["sweet_spot_price", r.sweet_spot_price],
      ["price_band_max", r.price_band_max],
    ]),
    sec("Inteligencia Competitiva", [
      ["top_competitor_name", r.top_competitor_name],
      ["top_competitor_rating", r.top_competitor_rating],
      ["competitors_count", r.competitors_count],
      ["gaps", r.gaps],
      ["opportunities", r.opportunities],
    ]),
    sec("Palavras-Chave", [
      ["head_terms", r.head_terms],
      ["longtails", r.longtails],
      ["seo_outbound", r.seo_outbound],
      ["negative_keywords", r.negative_keywords],
    ]),
  ].join("\n");
}

/** Build the SYNCHRONOUS research CapabilityResultView (carries .structured + the
 *  canonical MD in .artifact) for the "pesquisa_produto" capability. */
function buildResearchResult(card: Card, intent: string): CapabilityResultView {
  const r: ProductResearchResult = {
    ...FIXTURE_RESEARCH,
    tenant_id: FIXTURE_TENANT.tenant_id,
    run_id: `pq_${Math.random().toString(36).slice(2, 8)}`,
    product_name:
      intent.trim() && intent.trim() !== card.default_intent_hint
        ? intent.trim().slice(0, 80)
        : FIXTURE_RESEARCH.product_name,
    run_timestamp: new Date().toISOString(),
  };
  return {
    tenant_id: FIXTURE_TENANT.tenant_id,
    capability: card.capability,
    kind: card.kind || "knowledge_card",
    pillar: card.pillar || "P01",
    nucleus: card.nucleus || "N01",
    artifact: researchMd(r),
    score: 9.0,
    passed: true,
    status: "persisted",
    model_used: "claude-sonnet-4-6 (fixture)",
    record_id: `row-${Math.random().toString(36).slice(2, 10)}`,
    persisted: true,
    trace: F8_STEPS.map((s) => `${s.id} ${s.name}: ok`).join("  |  "),
    errors: [],
    structured: r,
  };
}

// --- RESEARCH UNIVERSE fixture (capability "research_universe") ---------------
//
// The honest-null orchestrator report shape (mirrors cex_research_universe._empty_report):
// some lanes OK with real data, others honestly blocked/skipped (NEVER fabricated). mock is
// ALWAYS false. UniverseResultView renders the header + per-source status chips + section cards.

/** Build the SYNCHRONOUS universe CapabilityResultView (carries .structured = the report).
 *
 * SHOWCASE MOCK: this is the demo's flagship multi-source report, so EVERY section is
 * populated with rich, realistic sample pet data -- the full structured output, not
 * a sparse skeleton. It still routes for ANY typed seed (the lane fields fold the seed in),
 * and a brand/company-style default seed ("Minha Loja") lights every lane up naturally. Honest
 * by construction: mock STAYS true (the report carries the "dados simulados" chip), and ONE
 * lane is kept honestly skipped (influencer) so the per-lane honest-status feature is still
 * visible + truthful -- the rest report "ok" because the showcase has data for them. */
function buildUniverseResult(card: Card, intent: string): CapabilityResultView {
  const seed =
    intent.trim() && intent.trim() !== card.default_intent_hint
      ? intent.trim().slice(0, 80)
      : activeFlavor.storeLabel;
  const now = new Date().toISOString();

  const report: ResearchUniverseReport = {
    seed,
    seed_type: "brand",
    lanes_run: [
      "cnpj",
      "ibge",
      "reclame_aqui",
      "appstore",
      "reddit",
      "youtube",
      "seo",
      "questions",
      "sentiment",
      "influencer",
    ],
    selected_lanes: [
      "cnpj",
      "ibge",
      "reclame_aqui",
      "appstore",
      "reddit",
      "youtube",
      "seo",
      "questions",
      "sentiment",
      "influencer",
    ],
    sections: {
      // --- identity / firmographics (Receita CNPJ) --------------------------
      identity: {
        razao_social: activeFlavor.legalName,
        nome_fantasia: activeFlavor.storeLabel,
        cnpj: "00.000.000/0001-91",
        porte: "EPP (Empresa de Pequeno Porte)",
        situacao_cadastral: "ATIVA",
        atividade_principal: activeFlavor.activityDescription,
        natureza_juridica: "206-2 - Sociedade Empresaria Limitada",
        uf: "SP",
        municipio: "Sao Paulo",
      },
      firmographics: {
        fundacao: "2022",
        anos_atividade: 4,
        faixa_funcionarios: "11-50",
        capital_social: "R$ 120.000,00",
        segmento: activeFlavor.segment,
        canais: [...activeFlavor.channels],
      },
      // --- market sizing (flavor-driven -- see fixtureFlavor.ts) ------------
      market: { ...activeFlavor.market },
      // --- reputation (Reclame Aqui) ----------------------------------------
      reputation: {
        nota: 8.4,
        indice_reputacao: "OTIMO",
        reclamacoes_12m: 37,
        taxa_resposta: "98%",
        taxa_solucao: "91%",
        voltaria_a_fazer_negocio: "82%",
        tempo_medio_resposta: "11h",
        status_ra: "RA1000 (selo)",
      },
      // --- social: ALL THREE sub-records populated ---------------------------
      social: {
        appstore: {
          app: activeFlavor.appName,
          rating: 4.7,
          reviews: 1284,
          ranking_categoria: "#18 em Estilo de Vida (BR)",
          recent: [...activeFlavor.appReviews],
        },
        reddit: {
          threads: 9,
          subreddits: [...activeFlavor.socialCommunityTags],
          sentiment: "POS",
          top_thread: activeFlavor.socialTopThread,
        },
        youtube: {
          video_count: 24,
          total_views: 312000,
          top_titles: [...activeFlavor.youtubeTitles(seed)],
        },
      },
      // --- keywords / SEO (flavor-driven -- see fixtureFlavor.ts) -----------
      keywords: {
        head_terms: [seed, ...activeFlavor.keywordsHeadExtra],
        longtails: [...activeFlavor.keywordsLongtail],
        synonyms: [...activeFlavor.keywordsSynonyms],
      },
      // --- questions (multi-perspective) ------------------------------------
      questions: {
        question_count: 12,
        top_questions: [activeFlavor.questionsLead(seed), ...activeFlavor.questionsExtra],
      },
      // --- sentiment aggregate ----------------------------------------------
      sentiment_summary: {
        label: "POS",
        pos: 142,
        neu: 38,
        neg: 17,
        analyzed: 197,
        method: "lexicon+model",
        data_sources: ["youtube", "reddit", "appstore", "reclame_aqui"],
        mock: false,
      },
    },
    endpoint_status: {
      cnpj: "ok: receita federal",
      ibge: "ok: setor dimensionado",
      reclame_aqui: "ok: RA1000",
      appstore: "ok: 1284 reviews",
      reddit: "ok: 9 threads",
      youtube: "ok: 24 videos",
      seo: "ok",
      questions: "ok",
      sentiment: "ok: 197 analyzed",
      // ONE honest non-ok lane -- the per-lane honest-status feature stays visible + truthful.
      influencer: "skipped: lane nao habilitada para este tenant (mapeamento de influenciadores em roadmap)",
    },
    data_sources: {
      cnpj: ["receita_federal_cnpj"],
      ibge: ["ibge_sidra", "abinpet_2024"],
      reclame_aqui: ["reclame_aqui_public"],
      appstore: ["apple_app_store", "google_play"],
      reddit: ["reddit_public_json"],
      youtube: ["youtube_data_api_v3"],
      seo: ["google_autocomplete"],
      questions: ["multiperspective:seo+youtube+reddit"],
      sentiment: ["youtube", "reddit", "appstore", "reclame_aqui"],
    },
    fetched_at: now,
    mock: true,
  };

  return {
    tenant_id: FIXTURE_TENANT.tenant_id,
    capability: card.capability,
    kind: card.kind || "research_universe",
    pillar: card.pillar || "P01",
    nucleus: card.nucleus || "N01",
    artifact: universeMd(report),
    score: 9.0,
    passed: true,
    status: "persisted",
    model_used: "claude-sonnet-4-6 (fixture)",
    record_id: `row-${Math.random().toString(36).slice(2, 10)}`,
    persisted: true,
    trace: F8_STEPS.map((s) => `${s.id} ${s.name}: ok`).join("  |  "),
    errors: [],
    structured: report,
  };
}

/** A compact canonical-MD projection of a universe report (the ?render_format=md surface). */
function universeMd(r: ResearchUniverseReport): string {
  const lines: string[] = [
    "---",
    `id: universe_${Math.random().toString(36).slice(2, 8)}`,
    "kind: research_universe",
    "pillar: P01",
    "nucleus: N01",
    `title: "Research Universe -- ${(r.seed ?? "seed").slice(0, 50)}"`,
    "version: 1.0.0",
    "quality: null",
    `seed_type: ${r.seed_type ?? "unknown"}`,
    `fetched_at: "${r.fetched_at ?? ""}"`,
    `mock: ${r.mock === true ? "true" : "false"}`,
    "tags: [research_universe, multi-source, fixture]",
    "---",
    "",
    `# Research Universe -- ${r.seed ?? "seed"}`,
    "",
    ...(r.mock === true ? ["> DADOS SIMULADOS (fixtures mode).", ""] : []),
    "## Status por fonte",
    "",
  ];
  for (const [lane, status] of Object.entries(r.endpoint_status ?? {})) {
    lines.push(`- ${lane}: ${status}`);
  }
  const kw = r.sections?.keywords as { head_terms?: string[] } | null;
  if (kw && Array.isArray(kw.head_terms)) {
    lines.push("", "## Palavras-chave (head terms)", "", kw.head_terms.join(", "));
  }
  const sent = r.sections?.sentiment_summary;
  if (sent && typeof sent.analyzed === "number" && sent.analyzed > 0) {
    lines.push(
      "",
      "## Sentimento",
      "",
      `${sent.label} (pos ${sent.pos} / neu ${sent.neu} / neg ${sent.neg}, ${sent.analyzed} textos)`,
    );
  }
  lines.push("", "> Projecao render_universe (FIXTURES mode).");
  return lines.join("\n");
}

/** The ads artifact produced by the research->ads chain (consumes anuncio_open_vars). */
function fakeAdsArtifact(r: ProductResearchResult): string {
  const usps = [...(r.opportunities ?? []), r.differentiation_angle].filter(Boolean);
  const stamp = new Date().toISOString();
  return [
    "---",
    `id: ad_${Math.random().toString(36).slice(2, 8)}`,
    "kind: prompt_template",
    "pillar: P03",
    "nucleus: N02",
    `title: "Anuncio -- ${(r.product_name ?? "Produto").slice(0, 50)}"`,
    "version: 0.1.0",
    "quality: null",
    `created: "${stamp}"`,
    "source_chain: pesquisa_produto -> ads",
    "tags: [ads, copy, chain, fixture]",
    "---",
    "",
    `# ${r.product_name ?? "Produto"} -- anuncio pronto`,
    "",
    "## Titulo",
    "",
    `${r.product_name ?? "Produto"} | Base Reforcada Antiderrapante`,
    "",
    "## Bullets (USPs da pesquisa)",
    "",
    ...usps.slice(0, 4).map((u) => `- ${u}`),
    "",
    "## Preco sugerido",
    "",
    `R$ ${r.sweet_spot_price ?? "--"} (sweet spot da faixa R$ ${r.price_band_min ?? "--"}-${r.price_band_max ?? "--"})`,
    "",
    "## Palavras-chave (SEO outbound)",
    "",
    (r.seo_outbound ?? r.head_terms ?? []).join(", "),
    "",
    "> Gerado pela cadeia pesquisa->anuncio em FIXTURES mode (anuncio_open_vars).",
  ].join("\n");
}

// --- MOLDED capability result (capabilities with a mold but no real generator) ---
//
// For any capability that has an authored mold (lib/molds.MOLDS) but NOT a bespoke
// vertical, the run returns a MOLDED CapabilityResultView: it carries ``mold_id`` +
// ``input_example`` (the contract filled with the mold's example values) + a
// ``structured`` slot the StructuredResultView reads ({ mold_id, output_sections }).
// ResultView routes it via asMold (BEFORE asResearch). Honest-mock: the structured
// slot carries mock:true and the rendered card shows the "dados simulados" chip.
// The ``artifact`` keeps a short canonical-MD stub so the /results md projection +
// the copy affordance still work (the structured molde is the primary surface).
function buildMoldResult(card: Card, intent: string): CapabilityResultView {
  const mold = moldFor(card.capability)!; // caller checked moldFor() is defined
  const inputExample = inputExampleFor(mold);
  // honest-mock structured payload the StructuredResultView reads (mold_id +
  // output_sections), with mock:true so the "dados simulados" chip is truthful.
  const structured = {
    mold_id: mold.capability,
    input_example: inputExample,
    output_sections: mold.output_sections,
    mock: true as const,
  };
  const title = pick(intent, card, mold.summary).slice(0, 60);
  const artifact = [
    ...fmHead(
      `mold_${card.capability}`,
      card.kind || "knowledge_card",
      card.pillar || "P01",
      card.nucleus || "N01",
      `Molde -- ${card.label}`,
      [card.capability, "mold", "io-contract", "fixture"],
    ),
    `# Molde -- ${card.label}`,
    "",
    `> ${mold.summary}`,
    "",
    `Capacidade: ${title}`,
    "",
    "## Input contract",
    "",
    "| Campo | Tipo | Obrigatorio | Exemplo |",
    "|-------|------|-------------|---------|",
    ...mold.input_contract.map(
      (f) =>
        `| ${f.label} (${f.key}) | ${f.type} | ${f.required ? "sim" : "nao"} | ${
          Array.isArray(f.example) ? f.example.join(", ") : String(f.example)
        } |`,
    ),
    "",
    "## Structured output (secoes)",
    "",
    ...mold.output_sections.map((s) => `- ${s.title} (${s.layout})`),
    "",
    MOCK_NOTE,
  ].join("\n");

  return {
    tenant_id: FIXTURE_TENANT.tenant_id,
    capability: card.capability,
    kind: card.kind || "knowledge_card",
    pillar: card.pillar || "P01",
    nucleus: card.nucleus || "N01",
    artifact,
    score: 9.0,
    passed: true,
    status: "persisted",
    model_used: "claude-sonnet-4-6 (fixture)",
    record_id: `row-${Math.random().toString(36).slice(2, 10)}`,
    persisted: true,
    trace: F8_STEPS.map((s) => `${s.id} ${s.name}: ok`).join("  |  "),
    errors: [],
    mold_id: mold.capability,
    input_example: inputExample,
    structured,
  };
}

// DEV-ONLY scaffold repro (mission ADDAY1 W1b -- the OPERATOR CONSOLE UX pass).
//
// The clean fixtures mock path (buildMoldResult) never carries the scaffold marker, so the
// marker LEAK only reproduces against the live ads.py running WITHOUT an LLM credential. To
// prove the console renders that case as an HONEST empty-state offline, an ads intent that
// carries this token returns the EXACT shape the live scaffold emits: copy cells (the
// Variantes Hook column + the Teste A/B variants) stamped with the internal marker, with
// ``real: true`` + the scaffold note -- the two honesty traps the W1b fix defuses. Invisible
// to normal use (a real intent never carries the token); fixtures run in FIXTURES mode only.
export const SCAFFOLD_DEMO_TOKEN = "__scaffold_demo__";

function buildScaffoldAdsResult(card: Card): CapabilityResultView {
  const mold = moldFor("ads")!;
  // Mirror ads.py scaffold: stamp the marker onto the Variantes Hook column + the A/B variants.
  const sections: MoldSection[] = mold.output_sections.map((s) => {
    if (s.title === "Variantes" && Array.isArray(s.table)) {
      const hookIdx = (s.columns ?? []).indexOf("Hook");
      return {
        ...s,
        table: s.table.map((row) =>
          row.map((cell, ci) =>
            ci === hookIdx && typeof cell === "string"
              ? `${cell} ${PENDING_COPY_MARKER}`
              : cell,
          ),
        ),
      };
    }
    if (s.title === "Teste A/B" && Array.isArray(s.rows)) {
      return {
        ...s,
        rows: s.rows.map((r) =>
          /Variante [AB]/.test(r.label) && typeof r.value === "string"
            ? { ...r, value: `${r.value} ${PENDING_COPY_MARKER}` }
            : r,
        ),
      };
    }
    return s;
  });
  const base = buildMoldResult(card, "anuncio (scaffold demo)");
  return {
    ...base,
    mold_id: "ads",
    // real:true + scaffold copy is the exact honesty trap the console must defuse.
    structured: {
      mold_id: "ads",
      output_sections: sections,
      real: true,
      notes: ["generation_pending: scaffold (no credential or LLM failed)"],
    },
  };
}

// --- in-memory run progress (drives the 8F filament) -------------------------

// Map of capability-run start timestamps so fxRunProgress can animate the
// filament while a (synthetic) run is "in flight".
const RUN_STARTS = new Map<string, number>();
const RUN_DURATION_MS = 5200; // long enough to watch the 8F filament fire

// A by-id store of the produced results, so the Results deep-link can render a
// stored row's canonical projection offline (mirrors the LIVE path, where GET
// /results?render_format= attaches each row's ``render`` from the persisted
// payload). Keyed by record_id. Seeded rows (no backing result) are absent here
// -> the deep-link renders an honest "projection unavailable" note rather than a
// fabricated artifact (never-fabricate).
const RESULT_STORE = new Map<string, CapabilityResultView>();

// Seed history so the Results view is non-empty offline. Shape == ResultRow.
const RESULTS: ResultRow[] = [
  {
    id: "seed-pq-0001",
    capability: "pesquisa_produto",
    kind: "knowledge_card",
    created_at: new Date(Date.now() - 1000 * 60 * 12).toISOString(),
    label: "Pesquisa de Produto",
    nucleus: "N01",
    score: 9.0,
  },
  {
    id: "seed-0001",
    capability: "research",
    kind: "knowledge_card",
    created_at: new Date(Date.now() - 1000 * 60 * 42).toISOString(),
    label: "Research",
    nucleus: "N01",
    score: 9.1,
  },
  {
    id: "seed-0002",
    capability: "ads",
    kind: "prompt_template",
    created_at: new Date(Date.now() - 1000 * 60 * 180).toISOString(),
    label: "Ads / Copy",
    nucleus: "N02",
    score: 8.6,
  },
];

// Seed a handful of BACKED results (RESULT_STORE + a matching RESULTS row) across
// different capabilities, so the /results ledger shows variety AND the deep-link /
// inline projection renders real, capability-SPECIFIC MD offline (not just the
// honest "projection unavailable" the bare seed rows above demonstrate). Each uses
// the SAME per-capability builder a live run would, so the seeded body matches what
// running the card produces. Honest-mock throughout (artifact carries mock: true).
(function seedBackedResults() {
  const seeds: { capability: string; minutesAgo: number; score: number }[] = [
    { capability: "pricing", minutesAgo: 26, score: 9.2 },
    { capability: "competitor_benchmark", minutesAgo: 64, score: 9.0 },
    { capability: "roi_calc", minutesAgo: 95, score: 8.8 },
    { capability: "media_photo", minutesAgo: 150, score: 8.9 },
    { capability: "email_builder", minutesAgo: 320, score: 8.7 },
    // Spec 08 CRM: a sample CRM run (molded -> buildMoldResult; mock, real:false).
    { capability: "crm", minutesAgo: 38, score: 9.0 },
    // Spec 09 Sales Assistant: a sample outreach run (molded -> buildMoldResult; mock, real:false).
    { capability: "sales_assistant", minutesAgo: 22, score: 9.1 },
  ];
  for (const s of seeds) {
    const card = FIXTURE_CARDS.find((c) => c.capability === s.capability);
    if (!card) continue;
    const created = new Date(Date.now() - 1000 * 60 * s.minutesAgo).toISOString();
    const recordId = `seed-${s.capability}-${Math.random().toString(36).slice(2, 8)}`;
    // These seed capabilities all have an authored mold (lib/molds.MOLDS), so the
    // seeded result is the MOLDED structured view (mold_id + input_example +
    // structured) -- exactly what a live run of the card produces -- so the /results
    // deep-link renders the molded I/O view, not plain markdown. We then pin the
    // seed's score + record_id (the rest of the molded view is kept as-is).
    const view: CapabilityResultView = {
      ...buildMoldResult(card, ""),
      score: s.score,
      record_id: recordId,
    };
    RESULT_STORE.set(recordId, view);
    RESULTS.push({
      id: recordId,
      capability: s.capability,
      kind: view.kind,
      created_at: created,
      label: card.label,
      nucleus: card.nucleus,
      score: s.score,
    });
  }
  // Keep the ledger reverse-chronological (newest first), matching the live order.
  RESULTS.sort((a, b) => (a.created_at < b.created_at ? 1 : -1));
})();

// --- RESULTS PERSISTENCE (localStorage-backed, SSR-safe) ---------------------
//
// The static RESULTS / RESULT_STORE above are the BASELINE seeds (a fresh visitor
// still sees examples). Real runs are ADDITIONALLY persisted to localStorage so the
// /results ledger survives a reload / navigation: a run done in one page render is
// still there after the module is re-evaluated on the next load. We persist BOTH the
// light ledger row (so the list renders) AND its CapabilityResultView (so the
// deep-link / inline projection can render the stored artifact offline).
//
// SSR-safe: every localStorage/window touch is guarded by ``typeof window !==
// "undefined"`` (Next.js prerenders these pages on the server, where there is no
// localStorage). On the server this layer is a complete no-op -> the caller sees
// only the static seeds; on the client we hydrate once from localStorage on first
// read, then read/write through.

const RESULTS_LS_KEY = "cex_fixtures_results_v1";

/** The persisted shape: the ledger rows (newest-first) + their backing views by id. */
interface PersistedResults {
  rows: ResultRow[];
  views: Record<string, CapabilityResultView>;
}

// The hydrated client-side persisted state (null until first client read). On the
// server it stays null forever (SSR no-op).
let PERSISTED: PersistedResults | null = null;

function hasWindow(): boolean {
  return typeof window !== "undefined";
}

/** Hydrate PERSISTED from localStorage ONCE (client only). No-op on the server. */
function ensureHydrated(): PersistedResults {
  if (PERSISTED) return PERSISTED;
  const fresh: PersistedResults = { rows: [], views: {} };
  if (!hasWindow()) return fresh; // server: never touch localStorage; do NOT cache
  try {
    const raw = window.localStorage.getItem(RESULTS_LS_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as Partial<PersistedResults>;
      fresh.rows = Array.isArray(parsed.rows) ? parsed.rows : [];
      fresh.views =
        parsed.views && typeof parsed.views === "object" ? parsed.views : {};
    }
  } catch {
    /* corrupt/blocked storage -> start from an empty persisted layer (degrade-never) */
  }
  PERSISTED = fresh;
  return PERSISTED;
}

/** Write PERSISTED back to localStorage (client only). Swallows quota/security errors. */
function flushPersisted(): void {
  if (!hasWindow() || !PERSISTED) return;
  try {
    window.localStorage.setItem(RESULTS_LS_KEY, JSON.stringify(PERSISTED));
  } catch {
    /* storage full / blocked -> keep the in-memory copy; never throw on a fixture run */
  }
}

/**
 * Record one produced run so it survives reload: prepend its ledger row (newest
 * first) and store its backing view by record_id. ALSO mirrors into the in-memory
 * RESULTS / RESULT_STORE so the CURRENT render is immediately consistent (the
 * persisted layer is what survives the next module load). No-op-safe on the server
 * (the row still lands in the in-memory RESULTS for this render).
 */
function persistResult(row: ResultRow, view?: CapabilityResultView): void {
  // in-memory mirror (current render) -- unchanged behaviour for this page load
  RESULTS.unshift(row);
  if (view && view.record_id) RESULT_STORE.set(view.record_id as string, view);

  // durable layer (survives reload) -- client only
  const store = ensureHydrated();
  store.rows = [row, ...store.rows.filter((r) => r.id !== row.id)];
  if (view && view.record_id) store.views[view.record_id as string] = view;
  flushPersisted();
}

/**
 * The ledger the readers see: persisted rows FIRST (reverse-chronological -- they are
 * the newest), then the static seeds, delta-deduped by id (a persisted row shadows a
 * seed with the same id). Pure read; hydrates on first client call.
 */
function mergedResults(): ResultRow[] {
  const store = ensureHydrated();
  const seen = new Set<string>();
  const merged: ResultRow[] = [];
  for (const r of [...store.rows, ...RESULTS]) {
    if (seen.has(r.id)) continue;
    seen.add(r.id);
    merged.push(r);
  }
  return merged;
}

/** Resolve a stored view by id, preferring the persisted layer, then the in-memory seeds. */
function storedView(id: string): CapabilityResultView | undefined {
  const store = ensureHydrated();
  return store.views[id] ?? RESULT_STORE.get(id);
}

/** Update ONE stored view in place (in-memory mirror + durable layer). Used by the upload-persist
 *  fixture so a filled slot survives a reload, exactly like the live backend persists it. */
function persistResultView(recordId: string, view: CapabilityResultView): void {
  RESULT_STORE.set(recordId, view);
  const store = ensureHydrated();
  store.views[recordId] = view;
  flushPersisted();
}

/** Read a File as a base64 data URI (the base64-inline sink, client-side). Browser-only -- it
 *  runs in fixtures mode, which is always client-side. */
function fileToDataUri(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result || ""));
    reader.onerror = () => reject(new Error("could not read the file"));
    reader.readAsDataURL(file);
  });
}

/**
 * Fixtures upload-persist (mirror PATCH /capability/{record_id}/media/{slot_key}). Reads the file
 * as a data URI (the SAME shape the backend's base64-inline sink returns), flips the stored
 * result's slot empty -> generated, PERSISTS the view (so a re-open shows it filled), and returns
 * the UploadedMedia shape. Honest: the slot src becomes a real (local) data URI; no fabrication.
 */
export async function fxUploadSlotMedia(
  recordId: string,
  slotKey: string,
  file: File,
): Promise<UploadedMedia> {
  // a short beat so the component's "saving" state renders (mirrors a network round-trip).
  await new Promise((r) => setTimeout(r, 350));
  const src = await fileToDataUri(file);

  const view = storedView(recordId);
  let updatedSlot: MediaSlot | undefined;
  let dual: DualOutputResult | undefined;
  if (view && view.dual_output && Array.isArray(view.dual_output.media_slots)) {
    const slots = view.dual_output.media_slots.map((s) => {
      if (s.key === slotKey) {
        updatedSlot = { ...s, status: "generated", src };
        return updatedSlot;
      }
      return s;
    });
    if (updatedSlot) {
      dual = { ...view.dual_output, media_slots: slots };
      persistResultView(recordId, { ...view, dual_output: dual });
    }
  }
  if (!updatedSlot) {
    // unknown record/slot in fixtures -> mirror the backend 404 (the dropzone keeps the local preview).
    throw Object.assign(new Error("no media slot to update for this result."), {
      status: 404,
      reason: "unknown_slot",
    });
  }

  return {
    record_id: recordId,
    slot_key: slotKey,
    dual_output: dual,
    slot: updatedSlot,
    stored: {
      content_type: file.type || "application/octet-stream",
      bytes: file.size,
      stored_as: "inline_base64",
    },
    persisted: !!dual,
  };
}

export function fxListCards(): Card[] {
  // MIRRORS live GET /capabilities, which returns ONLY the tenant's ENABLED set
  // (apps/dashboard_api list_capability_cards is overlay-derived to the enabled subset):
  // the grid shows enabled cards, and the compose picker surfaces the DECLARED-but-
  // disabled set from /capabilities-config (fxGetCapabilitiesConfig) to pull from.
  // No-op for the historically all-enabled card set -> the grid is byte-unchanged; it is
  // load-bearing only now that the picker ships declared-but-disabled cards. fxSetCapability
  // (attach) flips ``enabled`` -> the next fxListCards includes the freshly-attached card
  // (the grid grows); detach removes it (the grid shrinks).
  return FIXTURE_CARDS.filter((c) => c.enabled).map((c) => ({ ...c }));
}

// ----------------------------------------------------------------------------
// COMPOSE control-plane fixtures (mission DASHBOARD_COMPOSITION W3).
//
// The attach state is DERIVED from FIXTURE_CARDS' ``enabled`` flags so the compose
// UI (ModuleManager) and the grid stay consistent offline:
//   declared = every fixture card ; enabled = the ones ON ; disabled = the rest.
// fxSetCapability flips the matching card's ``enabled`` (so a later fxListCards --
// and fxRunCapability's enabled-check -- reflect the toggle) and returns the NEW
// state, MIRRORING the backend PATCH contract (apps/dashboard_api/deps.mutate_-
// capability): an unknown action -> 400, an undeclared slug -> 409.
// ----------------------------------------------------------------------------

/**
 * The FULL declared catalog metadata (mission BUILD C): EVERY declared card -- enabled
 * AND disabled -- as rich {capability,label,title,description,kind,nucleus,...} rows. This
 * is what the compose picker reads to render rich "available to add" rows for the declared-
 * but-disabled set (which fxListCards / live GET /capabilities correctly OMIT). Distinct
 * from fxListCards (enabled-only grid) ON PURPOSE: the picker browses the WHOLE catalog,
 * the grid shows only what is attached. Live mode has no full-catalog endpoint yet, so
 * ApiClient.listCatalog degrades to [] there -> the picker humanizes the slug (unchanged,
 * zero-regression); fixtures mode serves this so the offline demo reads richly.
 */
export function fxListCatalog(): Card[] {
  return FIXTURE_CARDS.map((c) => ({ ...c }));
}

/** Derive {declared, enabled, disabled} from the current FIXTURE_CARDS enabled flags. */
function capabilitiesConfigFromCards(): CapabilitiesConfig {
  return {
    declared: FIXTURE_CARDS.map((c) => c.capability),
    enabled: FIXTURE_CARDS.filter((c) => c.enabled).map((c) => c.capability),
    disabled: FIXTURE_CARDS.filter((c) => !c.enabled).map((c) => c.capability),
  };
}

/** GET /capabilities-config (fixtures): the tenant's full attach state. */
export function fxGetCapabilitiesConfig(): CapabilitiesConfig {
  return capabilitiesConfigFromCards();
}

/** PATCH /capabilities/{slug} (fixtures): flip the card's enabled flag, return new state. */
export async function fxSetCapability(
  slug: string,
  action: "attach" | "detach",
): Promise<CapabilitiesConfig> {
  const norm = (action || "").trim().toLowerCase();
  if (norm !== "attach" && norm !== "detach") {
    // mirror the backend unknown_action -> 400.
    throw Object.assign(new Error("action must be 'attach' or 'detach'."), {
      status: 400,
      reason: "unknown_action",
    });
  }
  const card = FIXTURE_CARDS.find((c) => c.capability === slug);
  if (!card) {
    // a capability must be DECLARED to be attachable (mirror the backend not_declared -> 409).
    throw Object.assign(
      new Error(`Capability "${slug}" is not declared for your tenant.`),
      { status: 409, reason: "not_declared" },
    );
  }
  card.enabled = norm === "attach";
  return capabilitiesConfigFromCards();
}

/**
 * Synchronous run (mirrors POST /capability/run): refuses a disabled capability,
 * else waits RUN_DURATION_MS (so the loading + 8F filament render) and resolves
 * to a CapabilityResultView. Records the run into the in-memory results store.
 */
// --- DUAL-OUTPUT samples (mission DASHBOARD_COMPOSITION W5 + SEED-DUALOUTPUT) -
//
// Fixture dual-output assets so NEXT_PUBLIC_FIXTURES=1 renders the HUMAN audiovisual
// face (components/DualOutputFace) end-to-end OFFLINE. Each mirrors the raw
// cex_dual_output.to_dual_output projection the backend forwards: {id, capability,
// machine_md, human_html, media_slots, frontmatter, real}. Honest by construction:
//   * real:false (the face shows "dados simulados"),
//   * every "generated" slot's src is a CLEARLY-SAMPLE inline-SVG data URI (NEVER a
//     fabricated real photo), and
//   * every "empty" slot is the upload-fallback the founder directive requires (no src).
//
// SEED-DUALOUTPUT (founder directive "semar o mesmo padrao para tudo"): the face is
// UNIVERSAL, not research-only. The MEDIA-BEARING cards each carry a tailored sample:
//   * research    -- 1 generated figure + 1 empty audio (TTS narration)  -- pesquisa.
//   * media_photo -- 3 generated image shots (hero/detalhe/packshot) + 1 empty image upload.
//   * ads         -- 1 generated hero image + 1 empty video upload.
// EVERY OTHER capability returns undefined -> ResultView renders EXACTLY as today
// (degrade-never, zero-regression). NEVER-FABRICATE: generated = a clearly-sample
// placeholder asset only; any REAL media is left as an empty upload slot.

/** A clearly-sample inline-SVG figure (data URI) -- a placeholder, not a real photo. The
 *  optional caption/sub let multiple sample shots read as distinct while staying obviously
 *  placeholder; NO arg reproduces the original research figure byte-for-byte (zero-regression). */
function sampleFigureDataUri(
  caption = "FIGURA -- amostra (placeholder)",
  sub = "imagem de exemplo -- nao e uma foto real",
): string {
  const svg = [
    "<svg xmlns='http://www.w3.org/2000/svg' width='640' height='360' viewBox='0 0 640 360'>",
    "<rect width='640' height='360' fill='#0e1726'/>",
    "<rect x='1' y='1' width='638' height='358' fill='none' stroke='#1f2a3a'/>",
    "<circle cx='320' cy='150' r='52' fill='none' stroke='#2dd4bf' stroke-width='3'/>",
    "<path d='M296 150h48M320 126v48' stroke='#2dd4bf' stroke-width='3' opacity='0.45'/>",
    `<text x='320' y='250' fill='#8aa0b6' font-family='monospace' font-size='22' text-anchor='middle'>${caption}</text>`,
    `<text x='320' y='284' fill='#52677d' font-family='monospace' font-size='13' text-anchor='middle'>${sub}</text>`,
    "</svg>",
  ].join("");
  return `data:image/svg+xml,${encodeURIComponent(svg)}`;
}

/** The ``## Media`` body line for one slot (generated -> sample descriptor; empty -> fallback). */
function dualMediaLine(s: MediaSlot): string {
  if (s.status === "generated") {
    const what = s.kind === "image" ? "[amostra inline-svg]" : `[amostra ${s.kind}]`;
    return `${s.key} (${s.kind}): generated -> ${what}`;
  }
  return `${s.key} (${s.kind}): empty -> upload-fallback (vazio; aguarda upload/edicao do humano)`;
}

/** A scalar for a code-fenced machine-md line (compact, single line). Mirrors the Python
 *  cex_dual_output._scalar_for_fence: numbers verbatim, bool -> true/false, lists joined. */
function fenceScalar(v: unknown): string {
  if (v === null || v === undefined) return "";
  if (typeof v === "boolean") return v ? "true" : "false";
  if (typeof v === "number") return String(v);
  if (Array.isArray(v)) return v.map((x) => String(x)).join(", ");
  if (typeof v === "object") {
    return Object.entries(v as Record<string, unknown>)
      .map(([k, val]) => `${k}=${String(val)}`)
      .join(", ");
  }
  return String(v).split(/\s+/).join(" ");
}

/** Render ONE MoldSection into code-fence body lines (the STRUCTURED REPORT lines the
 *  tenant's AI reads). Mirrors cex_dual_output._section_fence_lines field-for-field:
 *  fields -> "label: value", table -> header + " | "-joined rows, list -> "- item". */
function sectionFenceLines(s: MoldSection): string[] {
  const out: string[] = [];
  if (s.layout === "fields" && Array.isArray(s.rows)) {
    for (const r of s.rows) out.push(`${r.label}: ${fenceScalar(r.value)}`);
  } else if (s.layout === "table") {
    const cols = (s.columns ?? []).map((c) => String(c));
    if (cols.length) out.push(cols.join(" | "));
    for (const row of s.table ?? []) {
      if (Array.isArray(row)) out.push(row.map((c) => fenceScalar(c)).join(" | "));
    }
  } else if (s.layout === "list" && Array.isArray(s.items)) {
    for (const it of s.items) {
      if (it !== null && it !== undefined && String(it).trim()) out.push(`- ${fenceScalar(it)}`);
    }
  }
  if (out.length === 0) out.push("(sem dados)");
  return out;
}

/** The STRUCTURED-REPORT body of the machine .md: each output_section rendered as
 *  ``## Title`` + an optional ``> note`` + a code fence of its values. Mirrors the body
 *  cex_dual_output._render_machine_md emits BEFORE the ## Media ledger -- so the fixtures'
 *  machine face carries the SAME AI-readable report the live backend persists (the founder's
 *  "mock reflects the expected machine artifact" rule applies to the .md face too). */
function sectionsToMachineMd(sections: MoldSection[]): string[] {
  const out: string[] = [];
  for (const s of sections) {
    const title = (s.title ?? "").trim();
    if (!title) continue;
    out.push(`## ${title}`);
    if (s.note && s.note.trim()) {
      out.push("");
      out.push(`> ${s.note.split(/\s+/).join(" ")}`);
    }
    out.push("");
    out.push("```");
    out.push(...sectionFenceLines(s));
    out.push("```");
    out.push("");
  }
  return out;
}

/** Build the canonical machine .md (YAML frontmatter + the STRUCTURED REPORT + a ## Media
 *  ledger) for a fixture dual-output asset. ``sections`` (the cap's output_sections) carry
 *  the AI-readable report -- when present the body renders them code-fenced exactly like the
 *  live cex_dual_output._render_machine_md, so the mock machine face == the expected one. An
 *  empty ``sections`` degrades to the media-only body (zero-regression). Frontmatter key order
 *  mirrors the Python emitter (sorted). */
function dualMachineMd(
  id: string,
  capability: string,
  slots: MediaSlot[],
  sections: MoldSection[] = [],
): string {
  const mediaFm = slots.flatMap((s) => [
    `- key: ${s.key}`,
    `  kind: ${s.kind}`,
    `  status: ${s.status}`,
  ]);
  return [
    "---",
    `capability: ${capability}`,
    "created: ''",
    `id: ${id}`,
    `kind: ${capability}`,
    "media:",
    ...mediaFm,
    "passed: true",
    "real: false",
    "schema_version: '1.0'",
    "score: 9.0",
    "tenant: ''",
    "---",
    `# ${id}`,
    "",
    ...sectionsToMachineMd(sections),
    "## Media",
    "",
    "```",
    ...slots.map(dualMediaLine),
    "```",
    "",
  ].join("\n");
}

/** Assemble a full fixture DualOutputResult (the flat snake_case emitter shape) from slots.
 *  ``sections`` (the cap's output_sections) seed the STRUCTURED REPORT in the machine .md so
 *  the machine face carries the AI-readable report the live backend persists (not just a media
 *  ledger). Absent -> media-only machine_md (degrade-never). */
function buildDualSample(
  id: string,
  capability: string,
  slots: MediaSlot[],
  sections: MoldSection[] = [],
): DualOutputResult {
  return {
    id,
    capability,
    real: false,
    machine_md: dualMachineMd(id, capability, slots, sections),
    human_html: `<section class="cex-dual"><header><h1>${capability}</h1></header></section>`,
    frontmatter: { id, capability, kind: capability, real: false, schema_version: "1.0" },
    media_slots: slots,
  };
}

// --- EXPORT-HTML (mission DASHBOARD_COMPOSITION) ------------------------
//
// A RICH, styled, standalone HTML rendering of a capability's SAMPLE structured
// output -- so the "Exportar HTML" / "Abrir" affordance on the human face exports an
// impressive + FAITHFUL page in fixtures mode (mirroring the look the real backend
// cex_dual_output.to_dual_output emits). NEVER-FABRICATE: sample data only -- the SAME
// mock content the .md / artifact face already carries -- and an HONEST badge
// ("amostra -- dados simulados"), NOT "resultado real" (these are mock: true). Caps
// NOT given a rich builder keep buildDualSample's minimal placeholder -> the export
// buttons stay hidden for them (degrade-never: the affordance only appears when there
// is a real document to export). ASCII-only + diacritic-free (the dashboard house style).

/** Wrap sample sections in a styled, self-contained ``<section>`` (scoped inline CSS + an
 *  honest header badge + footer). The component wraps this fragment in a minimal
 *  ``<!doctype html>`` shell on export, so it opens correctly standalone. */
function dualHtmlPage(title: string, sectionsHtml: string): string {
  return [
    '<section class="cex-export">',
    "<style>",
    ".cex-export{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;",
    "max-width:880px;margin:0 auto;padding:32px 24px;color:#0e1726;background:#fff;line-height:1.55}",
    ".cex-export header{border-bottom:2px solid #2dd4bf;padding-bottom:16px;margin-bottom:24px}",
    ".cex-export h1{font-size:26px;margin:0 0 10px}",
    ".cex-export .badge{display:inline-block;font:600 12px/1 monospace;letter-spacing:.06em;",
    "text-transform:uppercase;color:#9a6b00;background:#fff7e6;border:1px solid #ffd591;",
    "border-radius:6px;padding:5px 9px}",
    ".cex-export h2{font-size:18px;margin:28px 0 8px;color:#13202f}",
    ".cex-export p{margin:8px 0}",
    ".cex-export .note{color:#64748b;font-size:13px;font-style:italic;margin:6px 0 2px}",
    ".cex-export ul{margin:10px 0 12px;padding-left:22px}",
    ".cex-export li{margin:4px 0}",
    ".cex-export table{border-collapse:collapse;width:100%;margin:12px 0;font-size:14px}",
    ".cex-export th,.cex-export td{border:1px solid #dbe2ea;padding:7px 10px;text-align:left}",
    ".cex-export th{background:#f1f5f9}",
    ".cex-export footer{margin-top:28px;padding-top:14px;border-top:1px solid #dbe2ea;",
    "color:#64748b;font:13px/1.5 monospace}",
    "</style>",
    "<header>",
    `<h1>${title}</h1>`,
    '<span class="badge">amostra -- dados simulados</span>',
    "</header>",
    sectionsHtml,
    "<footer>CEXAI -- face humana (export). FIXTURES mode -- dados simulados (mock: true). ",
    "Exemplo representativo, nao e um scrape/resultado real.</footer>",
    "</section>",
  ].join("");
}

/** HTML-escape a value before injecting it into the export page. Mold values legitimately contain
 *  ``<`` / ``>`` / ``&`` (e.g. "<SLOT: IG_TOKEN>", "74d < 90d", "drop > 60%"); without escaping
 *  they would be parsed as bogus tags and the rich content would silently vanish from the page. */
function escHtml(v: unknown): string {
  return String(v)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/** Render a mold's RICH output_sections -- the SAME structured sections StructuredResultView shows
 *  on screen -- as the styled export body: ``fields`` -> a key/value table, ``table`` -> a grid,
 *  ``list`` -> bullets. The export thus mirrors the on-screen molded card faithfully (5-6 rich
 *  sections) instead of a hand-rolled thin subset. Degrade-never + TOTAL: a section missing its
 *  payload renders just its heading + note and never throws. */
function moldSectionsToHtml(sections: MoldSection[]): string {
  const out: string[] = [];
  for (const s of sections) {
    out.push(`<h2>${escHtml(s.title)}</h2>`);
    if (s.note) out.push(`<p class="note">${escHtml(s.note)}</p>`);
    if (s.layout === "fields" && Array.isArray(s.rows)) {
      out.push("<table><tbody>");
      for (const r of s.rows) {
        out.push(`<tr><th>${escHtml(r.label)}</th><td>${escHtml(r.value)}</td></tr>`);
      }
      out.push("</tbody></table>");
    } else if (s.layout === "table" && Array.isArray(s.columns) && Array.isArray(s.table)) {
      out.push(
        "<table><thead><tr>" +
          s.columns.map((c) => `<th>${escHtml(c)}</th>`).join("") +
          "</tr></thead><tbody>",
      );
      for (const row of s.table) {
        out.push("<tr>" + row.map((cell) => `<td>${escHtml(cell)}</td>`).join("") + "</tr>");
      }
      out.push("</tbody></table>");
    } else if (s.layout === "list" && Array.isArray(s.items)) {
      out.push("<ul>" + s.items.map((it) => `<li>${escHtml(it)}</li>`).join("") + "</ul>");
    }
  }
  return out.join("");
}

/** Render a capability's RICH mold (its output_sections) as a full styled export page. The export
 *  now mirrors the on-screen StructuredResultView (same mold -> same 5-6 rich sections), so
 *  "Exportar HTML" / "Abrir" produce a rich, faithful document -- not the old thin subset.
 *  Honest-mock: dualHtmlPage stamps the "amostra -- dados simulados" badge + mock footer. */
function htmlFromMold(capability: string, title: string): string {
  const mold = moldFor(capability);
  const body = mold ? moldSectionsToHtml(mold.output_sections) : "";
  return dualHtmlPage(title, body);
}

/** research -- the rich market/competitor scan (Resumo / Achados / Proveniencia / Fontes /
 *  Veredito), rendered from MOLD_RESEARCH: the SAME 5 sections the on-screen card shows. */
function htmlResearch(): string {
  return htmlFromMold("research", `Pesquisa de mercado -- ${activeFlavor.productName} (Brasil)`);
}

/** media_photo -- THE RENDERED PHOTO GALLERY (the media the cap produces), NOT the typed
 *  operator brief. The dashboard mock must reflect the EXPECTED human-facing result a
 *  supervisor reviews: for media_photo that is the gallery page (hero + the shot list as
 *  actual images: detalhe / lifestyle / escala / packshot + an empty "foto real" upload).
 *  The typed brief (MOLD_MEDIA_PHOTO output_sections: Brief / Iluminacao+camera / Shot list /
 *  Brand fit / Negative prompt / Compliance) STAYS on-screen via StructuredResultView; only
 *  this human_html (the "Abrir" / dual-output human face) is the rendered gallery. A FULL
 *  <!doctype html> doc with the honest "amostra -- dados simulados" badge -> DualOutputFace
 *  renders it unchanged. */
function htmlMediaPhoto(): string {
  return MEDIA_GALLERY_SAMPLE_HTML;
}

/** landing -- THE RENDERED LANDING PAGE (hero + prova social + beneficios + comparativo +
 *  como funciona + FAQ + oferta + CTA sticky), NOT the typed operator outline. The dashboard
 *  mock must reflect the EXPECTED human-facing result a supervisor reviews: for landing that
 *  is the page itself. The typed outline (MOLD_LANDING output_sections: Hero A/B / Secoes /
 *  CTA / Voz / Compliance) STAYS on-screen via StructuredResultView; only this human_html
 *  (the "Abrir" / dual-output human face) is the rendered landing page. A FULL <!doctype html>
 *  doc with the honest "amostra -- dados simulados" badge -> DualOutputFace renders it unchanged. */
function htmlLanding(): string {
  return LANDING_SAMPLE_HTML;
}

/** competitor_benchmark -- the rich benchmark report (Matriz / Evidencia / Leitura / Onde
 *  ganhar / Onde perdemos / Proveniencia / Veredito), rendered from MOLD_COMPETITOR_BENCHMARK:
 *  the SAME sections the on-screen card shows. A benchmark IS a report by nature, so a polished
 *  visual report is the right human face (not forced into a non-report shape). */
function htmlCompetitorBenchmark(): string {
  return htmlFromMold(
    "competitor_benchmark",
    `Benchmark competitivo -- ${activeFlavor.productName} (${activeFlavor.storeLabel} vs rivais)`,
  );
}

// --- BESPOKE-VERTICAL report projections (pesquisa_produto / research_universe) ----
//
// These two flagship verticals carry a bespoke structured payload (ProductResearchResult /
// ResearchUniverseReport), NOT the MoldSection shape. To honor the founder rule on BOTH faces
// for them too, project the payload into MoldSection[] -- which then drives (a) a POLISHED VISUAL
// REPORT human_html (moldSectionsToHtml -> dualHtmlPage) and (b) the STRUCTURED REPORT in the
// machine .md (sectionsToMachineMd). A report IS the expected artifact for these (they are
// reports by nature), so we keep the report shape -- just rendered cleanly, never a raw dump.

/** Project a ProductResearchResult into report sections (Preco / Competitivo / Palavras-chave /
 *  Veredito) -- the SAME data the on-screen ResearchResultView shows, as a clean report. */
function researchReportSections(r: ProductResearchResult): MoldSection[] {
  return [
    {
      title: "Preco de mercado",
      layout: "fields",
      rows: [
        { label: "Faixa minima", value: `R$ ${r.price_band_min ?? "--"}` },
        { label: "Preco medio", value: `R$ ${r.price_avg ?? "--"}` },
        { label: "Sweet spot", value: `R$ ${r.sweet_spot_price ?? "--"}` },
        { label: "Faixa maxima", value: `R$ ${r.price_band_max ?? "--"}` },
      ],
    },
    {
      title: "Inteligencia competitiva",
      layout: "fields",
      rows: [
        { label: "Concorrente lider", value: String(r.top_competitor_name ?? "--") },
        { label: "Nota do lider", value: String(r.top_competitor_rating ?? "--") },
        { label: "Avaliacoes do lider", value: String(r.top_competitor_reviews ?? "--") },
        { label: "Concorrentes mapeados", value: String(r.competitors_count ?? "--") },
        { label: "Angulo de diferenciacao", value: String(r.differentiation_angle ?? "--") },
        { label: "Posicionamento", value: String(r.recommended_positioning ?? "--") },
      ],
    },
    {
      title: "Lacunas e oportunidades",
      layout: "list",
      note: "Lacunas dos concorrentes + oportunidades para o anuncio.",
      items: [...(r.gaps ?? []), ...(r.opportunities ?? [])],
    },
    {
      title: "Palavras-chave",
      layout: "fields",
      rows: [
        { label: "Head terms", value: (r.head_terms ?? []).join(", ") },
        { label: "Long tails", value: (r.longtails ?? []).join(", ") },
        { label: "SEO outbound", value: (r.seo_outbound ?? []).join(", ") },
        { label: "Negativas", value: (r.negative_keywords ?? []).join(", ") },
      ],
    },
    {
      title: "Veredito",
      layout: "fields",
      rows: [
        { label: "Confianca", value: `${r.confidence_score ?? "--"} / 10` },
        { label: "Pronto para anuncio", value: r.ready_for_ads ? "Sim" : "Nao" },
        { label: "Marketplaces consultados", value: (r.marketplaces_queried ?? []).join(", ") },
        { label: "Marketplaces sem dado", value: (r.marketplaces_failed ?? []).join(", ") || "nenhum" },
      ],
    },
  ];
}

/** Project a ResearchUniverseReport into report sections (Status por fonte + per-lane cards) --
 *  the SAME data the on-screen UniverseResultView shows, as a clean multi-source report. */
function universeReportSections(rep: ResearchUniverseReport): MoldSection[] {
  const sections: MoldSection[] = [];
  const status = rep.endpoint_status ?? {};
  sections.push({
    title: "Status por fonte",
    layout: "table",
    note: "Status honesto por lane (ok | blocked | skipped | failed) -- nunca fabricado.",
    columns: ["Fonte", "Status"],
    table: Object.entries(status).map(([lane, st]) => [lane, String(st)]),
  });
  const s = rep.sections ?? {};
  const ident = s.identity as Record<string, unknown> | undefined;
  if (ident) {
    sections.push({
      title: "Identidade (CNPJ)",
      layout: "fields",
      rows: Object.entries(ident).map(([k, v]) => ({ label: k, value: String(v) })),
    });
  }
  const market = s.market as Record<string, unknown> | undefined;
  if (market) {
    sections.push({
      title: "Mercado (IBGE / setor)",
      layout: "fields",
      rows: Object.entries(market).map(([k, v]) => ({ label: k, value: String(v) })),
    });
  }
  const rep_ = s.reputation as Record<string, unknown> | undefined;
  if (rep_) {
    sections.push({
      title: "Reputacao (Reclame Aqui)",
      layout: "fields",
      rows: Object.entries(rep_).map(([k, v]) => ({ label: k, value: String(v) })),
    });
  }
  const kw = s.keywords as { head_terms?: string[]; longtails?: string[] } | undefined;
  if (kw) {
    sections.push({
      title: "Palavras-chave",
      layout: "fields",
      rows: [
        { label: "Head terms", value: (kw.head_terms ?? []).join(", ") },
        { label: "Long tails", value: (kw.longtails ?? []).join(", ") },
      ],
    });
  }
  const sent = s.sentiment_summary as
    | { label?: string; pos?: number; neu?: number; neg?: number; analyzed?: number }
    | undefined;
  if (sent && typeof sent.analyzed === "number") {
    sections.push({
      title: "Sentimento",
      layout: "fields",
      rows: [
        { label: "Rotulo", value: String(sent.label ?? "--") },
        { label: "Positivos", value: String(sent.pos ?? 0) },
        { label: "Neutros", value: String(sent.neu ?? 0) },
        { label: "Negativos", value: String(sent.neg ?? 0) },
        { label: "Analisados", value: String(sent.analyzed ?? 0) },
      ],
    });
  }
  return sections;
}

/** Enrich a bespoke-vertical dual asset (pesquisa_produto / research_universe) so BOTH faces
 *  carry the projected report: a polished VISUAL report human_html + the STRUCTURED REPORT in the
 *  machine .md (above the existing media ledger). Mutates + returns the same DualOutputResult.
 *  Degrade-never: an empty projection leaves the asset's media-only faces untouched. */
function enrichBespokeReport(
  dual: DualOutputResult,
  capability: string,
  title: string,
  sections: MoldSection[],
): DualOutputResult {
  if (!sections.length) return dual;
  // Human face: a clean, styled visual report (NOT a raw JSON dump).
  dual.human_html = dualHtmlPage(title, moldSectionsToHtml(sections));
  // Machine face: re-render the .md with the structured report ABOVE the media ledger.
  const slots = Array.isArray(dual.media_slots) ? (dual.media_slots as MediaSlot[]) : [];
  dual.machine_md = dualMachineMd(`dualout_${capability}`, capability, slots, sections);
  return dual;
}

/** ads -- THE CATALOG AD (the product_ad buyer page), NOT the typed operator report.
 *  The dashboard mock must reflect the EXPECTED human-facing result a supervisor reviews:
 *  for ads that is the buyer page (brandbar + hero + galeria + sobre + caracteristicas +
 *  oferta + ficha + FAQ), mirroring what the LIVE backend's cex_run_capability
 *  ._render_ad_mold_html produces (it swaps human_html -> the product_ad mold). The typed
 *  operator/governance sections (MOLD_ADS output_sections: Variantes / Teste A-B / Voz /
 *  Compliance / Keywords / Estrategia de funil) STAY on-screen via StructuredResultView --
 *  only this human_html (the "Abrir" / dual-output human face) is the catalog ad.
 *  It is a FULL <!doctype html> document carrying the honest "amostra -- dados simulados"
 *  badge, so DualOutputFace renders it as the buyer page unchanged. */
function htmlAds(): string {
  return AD_CATALOG_SAMPLE_HTML;
}

/** Rich-HTML builders for the EXPORT-HTML affordance, keyed by capability. A cap present here
 *  gets a faithful styled page; absent caps keep the minimal placeholder (no export buttons).
 *  research is enriched directly in dualResearch() (it uses a bespoke literal).
 *
 *  Per the founder "mock reflects the EXPECTED human artifact" rule, the human face is each
 *  cap's expected RENDERED artifact: media_photo -> the photo gallery, landing -> the landing
 *  page, ads -> the catalog ad; the report caps (competitor_benchmark, + research/pesquisa/
 *  universe wired elsewhere) -> a polished visual report. */
const DUAL_HTML: Record<string, () => string> = {
  media_photo: htmlMediaPhoto,
  ads: htmlAds,
  landing: htmlLanding,
  competitor_benchmark: htmlCompetitorBenchmark,
};

/** research -- 1 generated figure + 1 empty audio (TTS narration) slot (the pesquisa
 *  "relatorio audiovisual": a figura + um slot de narracao TTS). The machine .md now carries
 *  the STRUCTURED REPORT (MOLD_RESEARCH.output_sections, code-fenced) ABOVE the media ledger,
 *  mirroring the live cex_dual_output._render_machine_md -- so the machine face the tenant's AI
 *  reads is the report, not just a media ledger (the founder's "mock reflects the expected
 *  machine artifact" rule). */
function dualResearch(): DualOutputResult {
  const researchSlots: MediaSlot[] = [
    {
      key: "fig_1",
      kind: "image",
      status: "generated",
      src: sampleFigureDataUri(),
      alt: "Figura de exemplo do relatorio (amostra)",
      label: "Figura 1 -- amostra do relatorio",
      editable: true,
      uploadFallback: true,
    },
    {
      key: "audio_narration",
      kind: "audio",
      status: "empty",
      label: "Narracao (TTS) -- envie ou gere",
      editable: true,
      uploadFallback: true,
    },
  ];
  const researchSections = moldFor("research")?.output_sections ?? [];
  const machine_md = dualMachineMd(
    "dualout_research",
    "research",
    researchSlots,
    researchSections,
  );
  return {
    id: "dualout_research",
    capability: "research",
    real: false,
    machine_md,
    // EXPORT-HTML: a rich, styled standalone page (mirrors the backend human face) so the
    // "Exportar HTML" / "Abrir" affordance exports an impressive + faithful document.
    human_html: htmlResearch(),
    frontmatter: {
      id: "dualout_research",
      capability: "research",
      kind: "research",
      real: false,
      schema_version: "1.0",
    },
    media_slots: researchSlots,
  };
}

/** A compact per-slot spec for a seeded dual sample. ``generated`` slots carry a clearly-sample
 *  inline-SVG (image only -- the cap genuinely auto-produces this media kind); ``empty`` slots are
 *  upload-fallback (the gen did NOT auto-produce media -> the human attaches it). NEVER-FABRICATE. */
interface DualSlotSpec {
  key: string;
  kind: MediaKind;
  generated: boolean;
  label: string;
  caption?: string; // SVG title line (generated image only)
  sub?: string; // SVG sub line (generated image only)
  alt?: string;
}

/** Realize one spec into a MediaSlot (generated -> sample src; empty -> NO src, upload-fallback). */
function specToSlot(s: DualSlotSpec): MediaSlot {
  if (s.generated) {
    return {
      key: s.key,
      kind: s.kind,
      status: "generated",
      src: sampleFigureDataUri(s.caption, s.sub),
      alt: s.alt ?? s.label,
      label: s.label,
      editable: true,
      uploadFallback: true,
    };
  }
  return {
    key: s.key,
    kind: s.kind,
    status: "empty",
    label: s.label,
    editable: true,
    uploadFallback: true,
  };
}

// SEED-DUALOUTPUT (founder directive "semar o mesmo padrao para tudo"): EVERY demo capability
// carries the dual-output face -- the pattern is universal, not media-specific. The slot mix is
// HONEST per cap:
//   * GENERATED sample visuals ONLY where the cap genuinely auto-produces visual media
//     (media_photo / ads / landing creatives; the report FIGURE for pesquisa / research_universe).
//   * EMPTY upload-fallback everywhere the gen did NOT auto-produce media (the data / text / config
//     caps): the .md face still renders + an editable upload slot the human fills (a chart, a
//     diagram, a product photo, a banner). research keeps its own byte-identical literal below.
const DUAL_SPECS: Record<string, DualSlotSpec[]> = {
  // --- media-producing caps: generated sample creatives -----------------------
  media_photo: [
    { key: "hero", kind: "image", generated: true, label: "Hero -- amostra do brief",
      caption: "HERO -- amostra", sub: activeFlavor.heroMediaCaption,
      alt: "Hero shot de exemplo (amostra)" },
    { key: "detalhe", kind: "image", generated: true, label: "Detalhe -- amostra do brief",
      caption: "DETALHE -- amostra", sub: "textura do sisal (close) -- exemplo",
      alt: "Detalhe de exemplo (amostra)" },
    { key: "packshot", kind: "image", generated: true, label: "Packshot -- amostra do brief",
      caption: "PACKSHOT -- amostra", sub: "produto em fundo branco -- exemplo",
      alt: "Packshot de exemplo (amostra)" },
    { key: "foto_real_produto", kind: "image", generated: false,
      label: "Foto real do produto -- envie a sua" },
  ],
  ads: [
    { key: "hero_image", kind: "image", generated: true, label: "Hero do anuncio -- amostra",
      caption: "HERO AD -- amostra", sub: "imagem de heroi do anuncio -- exemplo, nao e foto real",
      alt: "Imagem hero do anuncio (amostra)" },
    { key: "video_ad", kind: "video", generated: false, label: "Video do anuncio -- envie o seu" },
  ],
  landing: [
    { key: "hero_landing", kind: "image", generated: true, label: "Hero da landing -- amostra",
      caption: "HERO LANDING -- amostra", sub: "secao hero da pagina -- exemplo, nao e arte final",
      alt: "Hero da landing (amostra)" },
    { key: "og_image", kind: "image", generated: false, label: "Imagem de compartilhamento (OG) -- envie" },
    { key: "video_demo", kind: "video", generated: false, label: "Video de demonstracao -- envie" },
  ],
  // --- report caps: a generated sample FIGURE + an empty audio (TTS) slot -------
  pesquisa_produto: [
    { key: "fig_mercado", kind: "image", generated: true, label: "Figura -- panorama de mercado (amostra)",
      caption: "FIGURA -- mercado (amostra)", sub: "grafico do relatorio -- exemplo, nao e real",
      alt: "Figura de mercado (amostra)" },
    { key: "audio_narracao", kind: "audio", generated: false,
      label: "Narracao do relatorio (TTS) -- envie ou gere" },
  ],
  research_universe: [
    { key: "fig_panorama", kind: "image", generated: true, label: "Figura -- panorama multi-fonte (amostra)",
      caption: "FIGURA -- panorama (amostra)", sub: "sintese visual do relatorio -- exemplo",
      alt: "Figura panorama (amostra)" },
    { key: "audio_resumo", kind: "audio", generated: false,
      label: "Resumo em audio (TTS) -- envie ou gere" },
  ],
  // --- data caps: the gen produces tables, NOT media -> empty chart upload slot -
  pricing: [
    { key: "grafico_planos", kind: "image", generated: false,
      label: "Grafico comparativo de planos -- envie ou gere" },
  ],
  roi_calc: [
    { key: "grafico_roi", kind: "image", generated: false,
      label: "Grafico de payback / ROI -- envie ou gere" },
  ],
  funnel_diag: [
    { key: "diagrama_funil", kind: "image", generated: false,
      label: "Diagrama do funil -- envie ou gere" },
  ],
  tier_designer: [
    { key: "matriz_planos", kind: "image", generated: false,
      label: "Arte da matriz de planos -- envie ou gere" },
  ],
  competitor_benchmark: [
    { key: "grafico_benchmark", kind: "image", generated: false,
      label: "Grafico do benchmark -- envie ou gere" },
  ],
  // --- text / docs / config caps: human attaches the supporting asset ----------
  docs: [
    { key: "diagrama_doc", kind: "image", generated: false,
      label: "Diagrama / screenshot do doc -- envie" },
  ],
  product_docs: [
    { key: "foto_produto", kind: "image", generated: false,
      label: "Foto / diagrama do produto -- envie" },
  ],
  email_builder: [
    { key: "banner_email", kind: "image", generated: false,
      label: "Banner do email -- envie ou gere" },
  ],
  oauth_connect: [
    { key: "diagrama_integracao", kind: "image", generated: false,
      label: "Diagrama da integracao (opcional) -- envie" },
  ],
  custom_intake_form: [
    { key: "mockup_form", kind: "image", generated: false,
      label: "Logo / mockup do formulario -- envie" },
  ],
  // B2: brandbook -- the logo + cover are UPLOADED (the gen never fabricates a logo), so every
  // slot is an editable upload-fallback. Mirrors the cex_brandbook media_requests() slots
  // (logo_primary / logo_dark / brand_cover / palette_visual). A logo upload fills the slot the
  // overlay write reads -- the human edits the visual, the AI operates the .md.
  brandbook: [
    { key: "logo_primary", kind: "image", generated: false,
      label: "Logo principal -- envie (fundo claro)" },
    { key: "logo_dark", kind: "image", generated: false,
      label: "Logo (versao escura) -- envie" },
    { key: "brand_cover", kind: "image", generated: false,
      label: "Capa do brandbook -- envie ou gere" },
    { key: "palette_visual", kind: "image", generated: false,
      label: "Swatches da paleta -- envie ou gere" },
  ],
};

/** Build the fixture dual-output asset for a capability. research uses its bespoke builder;
 *  every other DECLARED cap builds from its DUAL_SPECS; an unknown cap -> undefined
 *  (degrade-never: ResultView renders exactly today's body).
 *
 *  machine_md (the founder's "mock reflects the expected machine artifact" rule): the asset's
 *  machine .md carries the cap's STRUCTURED REPORT (its mold output_sections, code-fenced) above
 *  the media ledger -- the SAME shape the live cex_dual_output._render_machine_md persists. Caps
 *  with no mold (pesquisa_produto / research_universe handled in their bespoke branches) fall back
 *  to the media-only ledger here. */
function sampleDualOutputFor(capability: string): DualOutputResult | undefined {
  if (capability === "research") return dualResearch();
  const specs = DUAL_SPECS[capability];
  if (!specs) return undefined;
  // The cap's structured report (when it has an authored mold) seeds the machine .md body.
  const sections = moldFor(capability)?.output_sections ?? [];
  const dual = buildDualSample(
    `dualout_${capability}`,
    capability,
    specs.map(specToSlot),
    sections,
  );
  // EXPORT-HTML: swap the minimal placeholder for the cap's EXPECTED rendered human face where
  // one exists (media_photo -> gallery, landing -> page, ads -> catalog ad, competitor_benchmark
  // -> report). Caps without a rich builder keep the placeholder -> no export buttons.
  const richHtml = DUAL_HTML[capability];
  if (richHtml) dual.human_html = richHtml();
  return dual;
}

export async function fxRunCapability(
  capability: string,
  intent: string,
  // ``inputs`` (mission BRANDBOOK, Cell A) is the typed form payload. Accepted for call
  // parity with the live client; the RICH resolution (image -> palette, doc/url -> text)
  // is a BACKEND concern (cex_run_capability._resolve_inputs) -- fixtures stay mock, so
  // this is accepted and not re-resolved here (degrade-never).
  inputs?: Record<string, unknown>,
): Promise<CapabilityResultView> {
  void inputs;
  const card = FIXTURE_CARDS.find((c) => c.capability === capability);
  if (!card || !card.enabled) {
    // mimic the backend refusing a disabled capability (capability_disabled -> 403)
    throw Object.assign(
      new Error("This capability is not enabled for your tenant."),
      { status: 403, reason: "capability_disabled" },
    );
  }

  const runKey = `${capability}-${Date.now()}`;
  RUN_STARTS.set(runKey, Date.now());
  await new Promise((r) => setTimeout(r, RUN_DURATION_MS));
  RUN_STARTS.delete(runKey);

  // FLAGSHIP: the product-research vertical returns the typed structured payload
  // (ResearchResultView renders the rich report). Every other capability returns
  // the generic knowledge-card artifact below.
  if (capability === "pesquisa_produto") {
    const research = buildResearchResult(card, intent);
    // SEED-DUALOUTPUT: this bespoke branch returns BEFORE the molded/generic attach below,
    // so attach the audiovisual face here too (the founder's "pesquisa -> relatorio audiovisual").
    const pesquisaDual = sampleDualOutputFor(capability);
    if (pesquisaDual) {
      // Founder rule on BOTH faces: a POLISHED VISUAL report (human) + the STRUCTURED report in
      // the machine .md, projected from the same typed payload the on-screen report renders.
      const payload = (research.structured as ProductResearchResult) || FIXTURE_RESEARCH;
      enrichBespokeReport(
        pesquisaDual,
        capability,
        `Pesquisa de produto -- ${payload.product_name ?? "produto"}`,
        researchReportSections(payload),
      );
      research.dual_output = pesquisaDual;
    }
    persistResult(
      {
        id: research.record_id as string,
        capability,
        kind: research.kind,
        created_at: new Date().toISOString(),
        label: card.label,
        nucleus: card.nucleus,
        score: research.score,
      },
      research,
    );
    return research;
  }

  // RESEARCH UNIVERSE: the multi-source orchestrator report (UniverseResultView renders it).
  if (capability === "research_universe") {
    const universe = buildUniverseResult(card, intent);
    // SEED-DUALOUTPUT: bespoke branch -- attach the audiovisual face here too (figure + TTS slot).
    const universeDual = sampleDualOutputFor(capability);
    if (universeDual) {
      // Founder rule on BOTH faces: a POLISHED VISUAL report (human) + the STRUCTURED report in
      // the machine .md, projected from the same typed multi-source payload the on-screen report shows.
      const rep = universe.structured as ResearchUniverseReport | undefined;
      if (rep) {
        enrichBespokeReport(
          universeDual,
          capability,
          `Research Universe -- ${rep.seed ?? "seed"}`,
          universeReportSections(rep),
        );
      }
      universe.dual_output = universeDual;
    }
    persistResult(
      {
        id: universe.record_id as string,
        capability,
        kind: universe.kind,
        created_at: new Date().toISOString(),
        label: card.label,
        nucleus: card.nucleus,
        score: universe.score,
      },
      universe,
    );
    return universe;
  }

  // DEV-ONLY scaffold repro: an ads intent carrying SCAFFOLD_DEMO_TOKEN returns the
  // live-scaffold shape (marker-stamped copy + real:true) so the console's honest
  // empty-state can be proven offline. Invisible to normal use (see buildScaffoldAdsResult).
  if (capability === "ads" && intent.includes(SCAFFOLD_DEMO_TOKEN)) {
    const scaffolded = buildScaffoldAdsResult(card);
    persistResult(
      {
        id: scaffolded.record_id as string,
        capability,
        kind: scaffolded.kind,
        created_at: new Date().toISOString(),
        label: card.label,
        nucleus: card.nucleus,
        score: scaffolded.score,
      },
      scaffolded,
    );
    return scaffolded;
  }

  // MOLDED capabilities: a capability with an authored mold (but no bespoke
  // vertical) returns the typed I/O contract as a structured molded result
  // (StructuredResultView renders it; ResultView routes via asMold). Capabilities
  // WITHOUT a mold yet fall through to the generic markdown artifact below (Wave 2
  // adds molds for the rest). research_universe + pesquisa_produto are handled above.
  if (moldFor(capability)) {
    const molded = buildMoldResult(card, intent);
    // W5-FIX: ``research`` HAS a mold, so it returns HERE (molded branch) and never
    // reaches the generic branch below where the dual-output asset was attached --
    // that control-flow gap is why DualOutputFace rendered zero DOM. Attach the asset
    // on the molded result too so the human audiovisual face renders ABOVE the molded
    // structured view. sampleDualOutputFor is research-only -> every OTHER molded
    // capability (ads/pricing/roi_calc/...) gets undefined and renders exactly as today.
    const moldedDual = sampleDualOutputFor(capability);
    if (moldedDual) molded.dual_output = moldedDual;
    persistResult(
      {
        id: molded.record_id as string,
        capability,
        kind: molded.kind,
        created_at: new Date().toISOString(),
        label: card.label,
        nucleus: card.nucleus,
        score: molded.score,
      },
      molded,
    );
    return molded;
  }

  const score = Math.round((8.4 + Math.random() * 1.2) * 10) / 10;
  const result: CapabilityResultView = {
    tenant_id: FIXTURE_TENANT.tenant_id,
    capability,
    kind: card.kind || "knowledge_card",
    pillar: card.pillar || "P01",
    nucleus: card.nucleus || "N01",
    artifact: buildArtifact(card, intent),
    score,
    passed: true,
    status: "persisted",
    model_used: "claude-sonnet-4-6 (fixture)",
    record_id: `row-${Math.random().toString(36).slice(2, 10)}`,
    persisted: true,
    trace: F8_STEPS.map((s) => `${s.id} ${s.name}: ok`).join("  |  "),
    errors: [],
  };

  // W5: attach the fixture dual-output asset (research only) so DualOutputFace renders
  // the human audiovisual face offline. Every other capability leaves it unset (today's view).
  const dual = sampleDualOutputFor(capability);
  if (dual) result.dual_output = dual;

  persistResult(
    {
      id: result.record_id as string,
      capability,
      kind: result.kind,
      created_at: new Date().toISOString(),
      label: card.label,
      nucleus: card.nucleus,
      score: result.score,
    },
    result,
  );

  return result;
}

/**
 * GET /results mirror. Default: the light ledger rows. When ``renderFormat`` is set,
 * each row ADDITIONALLY carries ``render`` -- the canonical md/html projection of the
 * stored result (mirrors the backend _project_rendered_rows). A row WITHOUT a backing
 * result in RESULT_STORE (the seeded demo rows) gets render="" -> the deep-link shows an
 * honest "projection unavailable" note (never-fabricate). md echoes the result's already
 * canonical ``artifact`` / render_universe MD; html wraps it in a minimal <pre>.
 */
export function fxListResults(
  capability?: string,
  renderFormat?: "md" | "html",
): ResultRow[] {
  // persisted rows (survive reload) merged with the static seeds (newest first).
  const all = mergedResults();
  const rows = capability
    ? all.filter((r) => r.capability === capability)
    : all;
  return rows.map((r) => {
    const row: ResultRow = { ...r };
    if (renderFormat) {
      const stored = storedView(r.id);
      row.render = stored ? fxRenderStored(stored, renderFormat) : "";
    }
    return row;
  });
}

/** The md/html projection of a stored result (PURE). md = the canonical artifact;
 *  html = the artifact wrapped in an escaped <pre> (mirrors fxFetchResultRender). */
function fxRenderStored(
  result: CapabilityResultView,
  format: "md" | "html",
): string {
  const md = result.artifact || "";
  if (format === "html") {
    const escaped = md
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
    return `<article class="cex-artifact">\n<pre>${escaped}</pre>\n</article>`;
  }
  return md;
}

// --- FLAGSHIP research->ads chain + canonical-MD fetch (fixtures) -------------
//
// fxChainToAds: run the research->ads chain in fixtures mode -- given a research
// CapabilityResultView (which carries the typed payload in .structured), produce the
// ads CapabilityResultView the pipeline would emit (consuming anuncio_open_vars).
// Mirrors _tools/cex_run_pipeline.py (research -> render -> persist -> ads). Records
// the ads run into the history store. A short delay lets the CTA's loading state show.

export async function fxChainToAds(
  research: CapabilityResultView,
): Promise<CapabilityResultView> {
  await new Promise((r) => setTimeout(r, 1400));
  const payload = (research.structured as ProductResearchResult) || FIXTURE_RESEARCH;
  const adsCard = FIXTURE_CARDS.find((c) => c.capability === "ads");
  const score = Math.round((8.6 + Math.random() * 0.9) * 10) / 10;
  const result: CapabilityResultView = {
    tenant_id: FIXTURE_TENANT.tenant_id,
    capability: "ads",
    kind: adsCard?.kind || "prompt_template",
    pillar: adsCard?.pillar || "P03",
    nucleus: adsCard?.nucleus || "N02",
    artifact: fakeAdsArtifact(payload),
    score,
    passed: true,
    status: "persisted",
    model_used: "claude-sonnet-4-6 (fixture)",
    record_id: `row-${Math.random().toString(36).slice(2, 10)}`,
    persisted: true,
    trace: F8_STEPS.map((s) => `${s.id} ${s.name}: ok`).join("  |  "),
    errors: [],
  };
  persistResult(
    {
      id: result.record_id as string,
      capability: "ads",
      kind: result.kind,
      created_at: new Date().toISOString(),
      label: adsCard?.label || "Ads / Copy",
      nucleus: result.nucleus,
      score: result.score,
    },
    result,
  );
  return result;
}

/** Return the canonical MD projection for a result (?render_format=md path). In
 *  fixtures this just echoes the result's already-canonical ``artifact``. */
export async function fxFetchResultMd(
  result: CapabilityResultView,
): Promise<string> {
  await new Promise((r) => setTimeout(r, 200));
  return result.artifact || "";
}

/**
 * Return the render_universe md/html projection for a research_universe result
 * (?render_format=md|html path). In fixtures: MD echoes the result's already-canonical
 * ``artifact`` (the universeMd projection); HTML wraps it in a minimal <pre> so the raw
 * toggle's html tab shows a real derivative. A non-universe result returns the artifact
 * (degrade-never). Mirrors the backend's _render_universe_view (render_universe MD/HTML).
 */
export async function fxFetchResultRender(
  result: CapabilityResultView,
  format: "md" | "html",
): Promise<string> {
  await new Promise((r) => setTimeout(r, 200));
  const md = result.artifact || "";
  if (format === "html") {
    const escaped = md
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
    return `<article class="research-universe">\n<pre>${escaped}</pre>\n</article>`;
  }
  return md;
}

// --- HOME / ANALYTICS shell (GET /summary) -----------------------------------

/**
 * Derive the home summary from the SAME in-memory cards + results the rest of
 * the app uses -- nothing is invented. Mirrors what the backend /summary will
 * project from the tenant's own data. Every number is a real derivation.
 */
export function fxGetSummary(): SummaryResponse {
  const cards = FIXTURE_CARDS;
  const enabled = cards.filter((c) => c.enabled).length;
  const overlay = cards.filter((c) => c.source === "overlay").length;
  const nuclei = new Set(cards.map((c) => c.nucleus)).size;

  const ledger = mergedResults();
  const scored = ledger.filter((r) => typeof r.score === "number");
  const avg =
    scored.length > 0
      ? Math.round(
          (scored.reduce((s, r) => s + (r.score as number), 0) / scored.length) *
            10,
        ) / 10
      : 0;

  const stats: SummaryStat[] = [
    {
      key: "capabilities_enabled",
      label: "capabilities enabled",
      value: enabled,
      hint: `of ${cards.length} in catalog`,
      tone: "synapse",
    },
    {
      key: "runs_total",
      label: "artifacts produced",
      value: ledger.length,
      hint: "in your data plane",
    },
    {
      key: "avg_score",
      label: "avg quality",
      value: avg ? avg.toFixed(1) : "--",
      hint: "F7 structural score",
      tone: avg >= 9 ? "synapse" : avg >= 8 ? "synapse" : "signal",
    },
    {
      key: "custom_overlay",
      label: "custom (overlay)",
      value: overlay,
      hint: `${nuclei} nuclei wired`,
    },
  ];

  const health: HealthRow[] = [
    {
      key: "runtime",
      label: "8F runtime",
      state: "ok",
      detail: "F1..F8 ready",
    },
    {
      key: "data_plane",
      label: "Data plane",
      state: "ok",
      detail: "RLS on . fixtures",
    },
    {
      key: "auth",
      label: "Identity",
      state: "ok",
      detail: "tenant from JWT",
    },
    {
      key: "backend",
      label: "Backend",
      state: "degraded",
      detail: "fixtures (no live API)",
    },
  ];

  return {
    tenant_id: FIXTURE_TENANT.tenant_id,
    stats,
    recent: ledger.slice(0, 5).map((r) => ({ ...r })),
    health,
  };
}

// --- SETTINGS / TENANT shell (GET /settings) ---------------------------------

/**
 * Tenant settings for offline review. SECURE-BY-DEFAULT: the secrets list
 * carries CONFIGURED STATUS ONLY -- there is intentionally no ``value`` field
 * anywhere in this shape (SecretStatus has none). Integration + identity copy
 * is brand-neutral; a real tenant overlay supplies its own.
 */
export function fxGetSettings(): TenantSettings {
  const integrations: IntegrationStatus[] = [
    {
      key: "supabase_auth",
      label: "Supabase Auth",
      state: "connected",
      detail: "identity . tenant_id from JWT",
    },
    {
      key: "data_plane",
      label: "Tenant data plane",
      state: "connected",
      detail: "RLS by tenant_id",
    },
    {
      key: "object_store",
      label: "Object storage",
      state: "available",
      detail: "offered . not wired in fixtures",
    },
    {
      key: "social_publish",
      label: "Social publishing",
      state: "available",
      detail: "offered . tenant supplies key",
    },
  ];

  // NOTE: names only. The Vault holds the values; this surface never sees them.
  const secrets: SecretStatus[] = [
    {
      name: "API_PROVIDER_KEY",
      label: "Model provider key (BYO)",
      configured: true,
      last_rotated: new Date(Date.now() - 1000 * 60 * 60 * 24 * 12).toISOString(),
    },
    {
      name: "DATA_PLANE_URL",
      label: "Tenant Supabase URL",
      configured: true,
    },
    {
      name: "DATA_PLANE_SERVICE_KEY",
      label: "Tenant Supabase service key",
      configured: true,
      last_rotated: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString(),
    },
    {
      name: "SOCIAL_PUBLISH_KEY",
      label: "Social publishing key",
      configured: false,
    },
    {
      name: "OBJECT_STORE_KEY",
      label: "Object storage key",
      configured: false,
    },
  ];

  return {
    tenant_id: FIXTURE_TENANT.tenant_id,
    tenant_label: FIXTURE_TENANT.tenant_label,
    operator_email: FIXTURE_TENANT.email,
    identity_note:
      "Identity and tenant binding come from your account (JWT app_metadata.tenant_id). You never pick a tenant; the client never sends one. RLS on tenant_id is the boundary.",
    integrations,
    secrets,
  };
}

// --- MANAGED-ENTITY SCHEMAS (GET /entities-config) ---------------------------
//
// OVERLAY-DRIVEN IN LIVE MODE: the real backend reads the tenant overlay's
// ``managed_entities`` and returns EntitySchema[]. FIXTURES mode mirrors that
// with the brand-neutral demo schema below, so the management half renders
// end-to-end offline -- swapping to the real backend changes nothing in the
// components (same as fxListCards mirrors GET /capabilities).
//
// The GENERIC demo entity ("records") is deliberately brand-neutral: it proves
// the schema-driven CRUD primitive without pretending to be any one tenant's
// catalog. A real tenant declares its own (products, contacts, leads, ...) in
// its overlay -- it does NOT edit the component. This schema's columns/fields
// match the seeded ENTITY_STORE rows below so fixtures renders coherently.

const FIXTURE_ENTITY_SCHEMAS: EntitySchema[] = [
  {
    entity: "records",
    singular: "Record",
    plural: "Records",
    description:
      "A generic, tenant-managed table. This demonstrates the schema-driven CRUD primitive -- any tenant entity (products, contacts, leads) plugs in by supplying its own schema, not by editing the component.",
    nucleus: "N04",
    icon: "table",
    writable: true,
    columns: [
      { key: "name", label: "Name", primary: true },
      { key: "category", label: "Category", type: "badge" },
      { key: "status", label: "Status", type: "badge" },
      { key: "amount", label: "Amount", type: "currency", align: "right" },
      { key: "active", label: "Active", type: "boolean", align: "right" },
      { key: "updated_at", label: "Updated", type: "date", align: "right" },
    ],
    fields: [
      {
        key: "name",
        label: "Name",
        type: "text",
        required: true,
        placeholder: "A human-readable name",
        help: "Required. Shown as the row's primary label.",
      },
      {
        key: "category",
        label: "Category",
        type: "select",
        required: true,
        options: [
          { value: "alpha", label: "Alpha" },
          { value: "beta", label: "Beta" },
          { value: "gamma", label: "Gamma" },
        ],
        help: "A generic enum -- swap for any tenant taxonomy.",
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        required: true,
        options: [
          { value: "draft", label: "Draft" },
          { value: "active", label: "Active" },
          { value: "archived", label: "Archived" },
        ],
      },
      {
        key: "amount",
        label: "Amount",
        type: "number",
        placeholder: "0",
        help: "Stored as a plain number; rendered as currency in the table.",
      },
      { key: "active", label: "Active", type: "boolean" },
      {
        key: "notes",
        label: "Notes",
        type: "textarea",
        placeholder: "Optional free-form notes",
      },
    ],
  },

  // --- Contacts / CRM (writable) --------------------------------------------
  // A lightweight CRM table: a contact with a status pipeline + follow-up date.
  // Brand-neutral demo of the management primitive for a leads/contacts shape.
  {
    entity: "contacts",
    singular: "Contact",
    plural: "Contacts",
    description:
      "A simple CRM table -- people or accounts you track, with a status pipeline and a follow-up date.",
    nucleus: "N05",
    icon: "table",
    writable: true,
    columns: [
      { key: "nome", label: "Name", primary: true },
      { key: "cidade", label: "City" },
      { key: "segmento", label: "Segment" },
      { key: "status", label: "Status", type: "badge" },
      { key: "telefone", label: "Phone" },
    ],
    fields: [
      {
        key: "nome",
        label: "Name",
        type: "text",
        required: true,
        placeholder: "Person or account name",
        help: "Required. Shown as the row's primary label.",
      },
      { key: "cidade", label: "City", type: "text", placeholder: "City" },
      {
        key: "segmento",
        label: "Segment",
        type: "text",
        placeholder: "e.g. retail, wholesale, partner",
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        required: true,
        options: [
          { value: "new", label: "New" },
          { value: "contacted", label: "Contacted" },
          { value: "qualified", label: "Qualified" },
          { value: "won", label: "Won" },
          { value: "lost", label: "Lost" },
        ],
      },
      { key: "telefone", label: "Phone", type: "text", placeholder: "Phone" },
      {
        key: "next_followup",
        label: "Next follow-up",
        type: "date",
        help: "When to reach out next.",
      },
      {
        key: "notes",
        label: "Notes",
        type: "textarea",
        placeholder: "Optional free-form notes",
      },
    ],
  },

  // --- Leads / CRM seed (writable) -- SPEC 05 lead-gen suite Phase 1c -------
  // The destination where scraped leads land: the leadgen capability (N01) WRITES
  // tenant_data rows of kind="leads" (spec sec 4.5), and THIS managed_entity makes
  // them appear in the Data tab with generic CRUD -- the proto-CRM (spec sec 2 +
  // sec 5: the forward-compatible lead record). Columns are a CRUD subset of the
  // sec-5 lead record; sample rows mirror the SAME honest leads MOLD_LEADGEN shows
  // (contact NEVER fabricated -- "--" / "perfil publico" when not exposed). In live
  // mode a tenant declares this in its overlay (managed_entities); the fixtures
  // schema mirrors it so the CRM seed is reviewable offline (like every entity here).
  {
    entity: "leads",
    singular: "Lead",
    plural: "Leads",
    description:
      "Leads captados (scraping/lead-gen) que alimentam o CRM -- cada linha e um lead com contato honesto (nunca fabricado, ausente quando nao exposto), sinal de intencao, confianca (0-1) e status de funil.",
    nucleus: "N01",
    icon: "research",
    writable: true,
    columns: [
      { key: "nome", label: "Name / Handle", primary: true },
      { key: "tipo", label: "Type", type: "badge" },
      { key: "canal", label: "Channel", type: "badge" },
      { key: "fonte", label: "Source" },
      { key: "contato", label: "Contact" },
      { key: "sinal", label: "Signal" },
      { key: "score", label: "Score", type: "number", align: "right" },
      { key: "status", label: "Status", type: "badge" },
    ],
    fields: [
      {
        key: "nome",
        label: "Name / Handle",
        type: "text",
        required: true,
        placeholder: "Display name, razao social, or @handle",
        help: "Required. Only if actually found -- never invent a name.",
      },
      {
        key: "tipo",
        label: "Type",
        type: "select",
        required: true,
        options: [
          { value: "pessoa", label: "Pessoa (B2C)" },
          { value: "empresa", label: "Empresa (B2B)" },
        ],
      },
      {
        key: "canal",
        label: "Channel",
        type: "select",
        required: true,
        options: [
          { value: "b2c_marketplace", label: "B2C marketplace" },
          { value: "b2b_cnpj", label: "B2B CNPJ" },
          { value: "ugc_social", label: "UGC social" },
        ],
      },
      {
        key: "fonte",
        label: "Source",
        type: "text",
        placeholder: "ml | shopee | reddit | youtube | cnpj_gov | ...",
        help: "The specific source the lead came from.",
      },
      {
        key: "contato",
        label: "Contact",
        type: "text",
        placeholder: "-- when not exposed",
        help: "NEVER fabricated. Leave blank / '--' when no real contact was found.",
      },
      {
        key: "sinal",
        label: "Signal",
        type: "textarea",
        placeholder: "The intent signal, quoted from the source",
        help: "What triggered / qualified this lead.",
      },
      {
        key: "score",
        label: "Score",
        type: "number",
        placeholder: "0.0 - 1.0",
        help: "Confidence 0-1 (source count + agreement + freshness).",
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        required: true,
        options: [
          { value: "novo", label: "Novo" },
          { value: "qualificado", label: "Qualificado" },
          { value: "em_contato", label: "Em contato" },
          { value: "descartado", label: "Descartado" },
        ],
      },
    ],
  },

  // --- Products / Catalog (writable, MARGIN-SAFE) ---------------------------
  // Demonstrates the admin_only margin guard: custo (cost), preco_b2b (B2B
  // price), and margem (margin) are flagged admin_only -> EXCLUDED from the
  // default table view AND the edit form by construction (DataManager.viewSchema).
  // The public-safe price (preco) and stock remain visible. This is how a tenant
  // prevents a cost/margin leak for EVERY entity without editing the component.
  {
    entity: "products",
    singular: "Product",
    plural: "Products",
    description:
      "A product catalog. Cost, B2B price, and margin are admin-only -- hidden from the default view so margins never leak.",
    nucleus: "N03",
    icon: "table",
    writable: true,
    // SPEC 10 W5: products opt into the L2 publish gate, so each row carries a
    // draft/published state. DataManager renders the per-row Publish toggle (W1) and
    // the Content Review HITL page surfaces the DRAFT rows for approve -> publish. It
    // is also the entity the field_manifest "New via manifest" editor targets.
    publishable: true,
    columns: [
      { key: "nome", label: "Name", primary: true },
      { key: "sku", label: "SKU" },
      { key: "categoria", label: "Category", type: "badge" },
      { key: "preco", label: "Price", type: "currency", align: "right" },
      { key: "estoque", label: "Stock", type: "number", align: "right" },
      { key: "ativo", label: "Active", type: "boolean", align: "right" },
      // SENSITIVE -- never render in the default view (margin guard).
      { key: "custo", label: "Cost", type: "currency", align: "right", admin_only: true },
      {
        key: "preco_b2b",
        label: "B2B Price",
        type: "currency",
        align: "right",
        admin_only: true,
      },
      { key: "margem", label: "Margin", type: "number", align: "right", admin_only: true },
    ],
    fields: [
      {
        key: "nome",
        label: "Name",
        type: "text",
        required: true,
        placeholder: "Product name",
        help: "Required. Shown as the row's primary label.",
      },
      { key: "sku", label: "SKU", type: "text", placeholder: "Stock-keeping unit" },
      {
        key: "categoria",
        label: "Category",
        type: "text",
        placeholder: "Product category",
      },
      {
        key: "preco",
        label: "Price",
        type: "number",
        placeholder: "0",
        help: "Public-facing price; safe to display.",
      },
      { key: "estoque", label: "Stock", type: "number", placeholder: "0" },
      { key: "ativo", label: "Active", type: "boolean" },
      // SENSITIVE -- excluded from the default edit form (margin guard).
      {
        key: "custo",
        label: "Cost",
        type: "number",
        placeholder: "0",
        admin_only: true,
        help: "Admin-only. Hidden from the default form.",
      },
      {
        key: "preco_b2b",
        label: "B2B Price",
        type: "number",
        placeholder: "0",
        admin_only: true,
      },
      {
        key: "margem",
        label: "Margin",
        type: "number",
        placeholder: "0",
        admin_only: true,
      },
    ],
  },

  // --- Knowledge base (writable) --------------------------------------------
  {
    entity: "knowledge_base",
    singular: "Article",
    plural: "Knowledge base",
    description:
      "A tenant-managed knowledge base -- reference notes, processes, and facts captured for retrieval.",
    nucleus: "N04",
    icon: "docs",
    writable: true,
    columns: [
      { key: "name", label: "Name", primary: true },
      { key: "domain", label: "Domain" },
      { key: "tags", label: "Tags" },
      { key: "status", label: "Status", type: "badge" },
    ],
    fields: [
      {
        key: "name",
        label: "Name",
        type: "text",
        required: true,
        placeholder: "Article title",
        help: "Required. Shown as the row's primary label.",
      },
      {
        key: "domain",
        label: "Domain",
        type: "text",
        placeholder: "e.g. product, support, legal",
      },
      {
        key: "tags",
        label: "Tags",
        type: "text",
        placeholder: "comma-separated tags",
      },
      {
        key: "body",
        label: "Body",
        type: "textarea",
        placeholder: "The article content (markdown welcome)",
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          { value: "draft", label: "Draft" },
          { value: "published", label: "Published" },
          { value: "archived", label: "Archived" },
        ],
      },
    ],
  },

  // --- Glossary (writable) ---------------------------------------------------
  {
    entity: "glossary",
    singular: "Term",
    plural: "Glossary",
    description:
      "A controlled glossary -- terms with their definitions, domain, and aliases.",
    nucleus: "N04",
    icon: "docs",
    writable: true,
    columns: [
      { key: "term", label: "Term", primary: true },
      { key: "domain", label: "Domain" },
      { key: "aliases", label: "Aliases" },
    ],
    fields: [
      {
        key: "term",
        label: "Term",
        type: "text",
        required: true,
        placeholder: "The term being defined",
        help: "Required. Shown as the row's primary label.",
      },
      {
        key: "definition",
        label: "Definition",
        type: "textarea",
        required: true,
        placeholder: "The definition",
      },
      {
        key: "domain",
        label: "Domain",
        type: "text",
        placeholder: "e.g. finance, engineering",
      },
      {
        key: "aliases",
        label: "Aliases",
        type: "text",
        placeholder: "comma-separated synonyms",
      },
    ],
  },

  // ==========================================================================
  // NEXT-WAVE managed entities (roadmap theme 1: "one library spine, 6 surfaces").
  // All six are the SAME shipped DataManager primitive -- pure schema, ZERO new
  // component code. Brand-neutral demos here; a tenant declares its own in its
  // overlay (.cex/tenants/<tid>/overlay/capability_map.yaml managed_entities).
  // Cost/margin/sensitive columns are flagged admin_only (margin guard).
  // ==========================================================================

  // --- research_library (N01): persisted research outputs -------------------
  {
    entity: "research_library",
    singular: "Research item",
    plural: "Research library",
    description:
      "Persisted research outputs -- competitor scans, market briefs, and source notes captured for reuse.",
    nucleus: "N01",
    icon: "research",
    writable: true,
    columns: [
      { key: "titulo", label: "Title", primary: true },
      { key: "tipo", label: "Type", type: "badge" },
      { key: "fonte", label: "Source" },
      { key: "status", label: "Status", type: "badge" },
      { key: "created", label: "Created", type: "date", align: "right" },
    ],
    fields: [
      {
        key: "titulo",
        label: "Title",
        type: "text",
        required: true,
        placeholder: "Research item title",
        help: "Required. Shown as the row's primary label.",
      },
      {
        key: "tipo",
        label: "Type",
        type: "select",
        options: [
          { value: "competitor", label: "Competitor scan" },
          { value: "market", label: "Market" },
          { value: "icp", label: "ICP / segment" },
          { value: "pricing", label: "Pricing" },
        ],
      },
      { key: "fonte", label: "Source", type: "text", placeholder: "Origin / citation" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          { value: "draft", label: "Draft" },
          { value: "verified", label: "Verified" },
          { value: "archived", label: "Archived" },
        ],
      },
      {
        key: "resumo",
        label: "Summary",
        type: "textarea",
        placeholder: "Short summary of the finding",
      },
      {
        key: "created",
        label: "Created",
        type: "date",
        help: "When this item was captured.",
      },
    ],
  },

  // --- brand_assets (N02): generated media / copy ---------------------------
  {
    entity: "brand_assets",
    singular: "Brand asset",
    plural: "Brand assets",
    description:
      "Generated media and copy -- images, ad copy, and video briefs produced on-brand and tracked here.",
    nucleus: "N02",
    icon: "media",
    writable: true,
    columns: [
      { key: "nome", label: "Name", primary: true },
      { key: "tipo", label: "Type", type: "badge" },
      { key: "canal", label: "Channel" },
      { key: "url", label: "URL" },
      { key: "status", label: "Status", type: "badge" },
    ],
    fields: [
      {
        key: "nome",
        label: "Name",
        type: "text",
        required: true,
        placeholder: "Asset name",
        help: "Required. Shown as the row's primary label.",
      },
      {
        key: "tipo",
        label: "Type",
        type: "select",
        required: true,
        options: [
          { value: "image", label: "Image" },
          { value: "copy", label: "Copy" },
          { value: "video", label: "Video" },
        ],
      },
      {
        key: "canal",
        label: "Channel",
        type: "text",
        placeholder: "e.g. instagram, email, web",
      },
      { key: "url", label: "URL", type: "text", placeholder: "Asset URL (if hosted)" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          { value: "draft", label: "Draft" },
          { value: "approved", label: "Approved" },
          { value: "published", label: "Published" },
        ],
      },
    ],
  },

  // --- rag_sources (N04): indexable sources ---------------------------------
  // Maps to the chunk / embedding / vector builders -- each row is one source the
  // retrieval pipeline ingests + indexes.
  {
    entity: "rag_sources",
    singular: "Source",
    plural: "RAG sources",
    description:
      "Indexable sources for retrieval -- URLs, files, and knowledge bases the RAG pipeline chunks, embeds, and indexes.",
    nucleus: "N04",
    icon: "docs",
    writable: true,
    columns: [
      { key: "nome", label: "Name", primary: true },
      { key: "tipo", label: "Type", type: "badge" },
      { key: "url", label: "URL" },
      { key: "status", label: "Status", type: "badge" },
      { key: "last_indexed", label: "Indexed", type: "date", align: "right" },
    ],
    fields: [
      {
        key: "nome",
        label: "Name",
        type: "text",
        required: true,
        placeholder: "Source name",
        help: "Required. Shown as the row's primary label.",
      },
      {
        key: "tipo",
        label: "Type",
        type: "select",
        required: true,
        options: [
          { value: "url", label: "URL" },
          { value: "file", label: "File" },
          { value: "kb", label: "Knowledge base" },
        ],
      },
      { key: "url", label: "URL", type: "text", placeholder: "Source URL or path" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          { value: "pending", label: "Pending" },
          { value: "indexed", label: "Indexed" },
          { value: "failed", label: "Failed" },
        ],
      },
      {
        key: "last_indexed",
        label: "Last indexed",
        type: "date",
        help: "When the source was last chunked + embedded.",
      },
    ],
  },

  // --- faq (N04): support FAQ -----------------------------------------------
  {
    entity: "faq",
    singular: "FAQ entry",
    plural: "FAQ",
    description:
      "Support FAQ -- questions and their answers, grouped by category, for self-serve help and RAG grounding.",
    nucleus: "N04",
    icon: "docs",
    writable: true,
    columns: [
      { key: "pergunta", label: "Question", primary: true },
      { key: "categoria", label: "Category", type: "badge" },
      { key: "status", label: "Status", type: "badge" },
    ],
    fields: [
      {
        key: "pergunta",
        label: "Question",
        type: "text",
        required: true,
        placeholder: "The question being answered",
        help: "Required. Shown as the row's primary label.",
      },
      {
        key: "resposta",
        label: "Answer",
        type: "textarea",
        required: true,
        placeholder: "The answer (markdown welcome)",
      },
      {
        key: "categoria",
        label: "Category",
        type: "text",
        placeholder: "e.g. billing, shipping, account",
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          { value: "draft", label: "Draft" },
          { value: "published", label: "Published" },
          { value: "archived", label: "Archived" },
        ],
      },
    ],
  },

  // --- scheduled_jobs (N05): recurring jobs ---------------------------------
  {
    entity: "scheduled_jobs",
    singular: "Scheduled job",
    plural: "Scheduled jobs",
    description:
      "Recurring jobs -- a capability run on a cadence, with the next run time and an on/off switch.",
    nucleus: "N05",
    icon: "table",
    writable: true,
    columns: [
      { key: "nome", label: "Name", primary: true },
      { key: "capability", label: "Capability" },
      { key: "cadencia", label: "Cadence", type: "badge" },
      { key: "proximo_run", label: "Next run", type: "date", align: "right" },
      { key: "ativo", label: "Active", type: "boolean", align: "right" },
    ],
    fields: [
      {
        key: "nome",
        label: "Name",
        type: "text",
        required: true,
        placeholder: "Job name",
        help: "Required. Shown as the row's primary label.",
      },
      {
        key: "capability",
        label: "Capability",
        type: "text",
        placeholder: "e.g. research, product_docs",
        help: "Which dashboard capability this job runs.",
      },
      {
        key: "cadencia",
        label: "Cadence",
        type: "select",
        required: true,
        options: [
          { value: "daily", label: "Daily" },
          { value: "weekly", label: "Weekly" },
          { value: "monthly", label: "Monthly" },
        ],
      },
      {
        key: "proximo_run",
        label: "Next run",
        type: "date",
        help: "When the job runs next.",
      },
      { key: "ativo", label: "Active", type: "boolean" },
    ],
  },

  // --- offers_coupons (N06): offers + coupons (MARGIN-SAFE) ------------------
  // Demonstrates the admin_only margin guard on an offer entity: custo (cost) and
  // margem (margin) are admin_only -> hidden from the default table + form so the
  // economics behind a coupon never leak. codigo/desconto/validade stay visible.
  {
    entity: "offers_coupons",
    singular: "Offer",
    plural: "Offers & coupons",
    description:
      "Offers and coupon codes -- the public code, discount, and validity; cost and margin are admin-only so the economics never leak.",
    nucleus: "N06",
    icon: "pricing",
    writable: true,
    columns: [
      { key: "codigo", label: "Code", primary: true },
      { key: "desconto", label: "Discount", type: "number", align: "right" },
      { key: "valido_ate", label: "Valid until", type: "date", align: "right" },
      { key: "ativo", label: "Active", type: "boolean", align: "right" },
      // SENSITIVE -- never render in the default view (margin guard).
      { key: "custo", label: "Cost", type: "currency", align: "right", admin_only: true },
      { key: "margem", label: "Margin", type: "number", align: "right", admin_only: true },
    ],
    fields: [
      {
        key: "codigo",
        label: "Code",
        type: "text",
        required: true,
        placeholder: "COUPON code",
        help: "Required. Shown as the row's primary label.",
      },
      {
        key: "desconto",
        label: "Discount",
        type: "number",
        placeholder: "0",
        help: "Discount amount or percent (public-facing).",
      },
      {
        key: "valido_ate",
        label: "Valid until",
        type: "date",
        help: "Expiry date for the offer.",
      },
      { key: "ativo", label: "Active", type: "boolean" },
      // SENSITIVE -- excluded from the default edit form (margin guard).
      {
        key: "custo",
        label: "Cost",
        type: "number",
        placeholder: "0",
        admin_only: true,
        help: "Admin-only. Hidden from the default form.",
      },
      {
        key: "margem",
        label: "Margin",
        type: "number",
        placeholder: "0",
        admin_only: true,
      },
    ],
  },
];

/**
 * The demo tenant's managed-entity schemas (mirrors GET /entities-config). A
 * short delay lets the loading state render, exactly like the other fixtures.
 */
export async function fxListEntitySchemas(): Promise<EntitySchema[]> {
  await new Promise((r) => setTimeout(r, 120));
  return FIXTURE_ENTITY_SCHEMAS.map((s) => ({ ...s }));
}

// --- GENERIC ENTITY CRUD (GET/POST/PATCH/DELETE /entity/{slug}) ---------------

/**
 * In-memory per-entity stores so the management primitive is reviewable
 * offline. Keyed by entity slug -> rows. The shapes are plain EntityRecord maps
 * (id + flat key/value), so the same store serves any schema.
 *
 * Seeded ONLY for the generic "records" demo entity. Other slugs start empty
 * (the table shows its empty state until rows are created).
 */
const ENTITY_STORE: Record<string, EntityRecord[]> = {
  records: [
    {
      id: "rec-0001",
      name: "First example record",
      category: "alpha",
      status: "active",
      amount: 1200,
      active: true,
      notes: "Seeded so the table renders in fixtures mode.",
      updated_at: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
    },
    {
      id: "rec-0002",
      name: "Second example record",
      category: "beta",
      status: "draft",
      amount: 450,
      active: false,
      notes: "",
      updated_at: new Date(Date.now() - 1000 * 60 * 60 * 30).toISOString(),
    },
    {
      id: "rec-0003",
      name: "Third example record",
      category: "gamma",
      status: "archived",
      amount: 0,
      active: false,
      notes: "Shows the archived + currency=0 rendering.",
      updated_at: new Date(Date.now() - 1000 * 60 * 60 * 90).toISOString(),
    },
  ],
  contacts: [
    {
      id: "contact-0001",
      nome: "Northwind Trading",
      cidade: "Lisbon",
      segmento: "wholesale",
      status: "qualified",
      telefone: "+351 21 000 0000",
      next_followup: new Date(Date.now() + 1000 * 60 * 60 * 24 * 3).toISOString(),
      notes: "Seeded so the contacts table renders in fixtures mode.",
      updated_at: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString(),
    },
    {
      id: "contact-0002",
      nome: "Acme Retail",
      cidade: "Porto",
      segmento: "retail",
      status: "contacted",
      telefone: "+351 22 000 0000",
      next_followup: null,
      notes: "",
      updated_at: new Date(Date.now() - 1000 * 60 * 60 * 50).toISOString(),
    },
  ],
  // leads carries the SAME honest sample leads MOLD_LEADGEN shows (lib/molds.ts):
  // contact is NEVER a fabricated email/phone -- it is the honest public-access note
  // ("via ML perfil publico -- e-mail nao exposto") or "--" when no contact was
  // found. The count is honest (7 leads, not padded). This is the CRM seed: the
  // destination where the leadgen capability's scraped rows land (spec 05 sec 4.5/5).
  leads: [
    {
      id: "lead-0001",
      nome: activeFlavor.leads[0].nome,
      tipo: "empresa",
      canal: "b2c_marketplace",
      fonte: "ml",
      contato: "via ML (perfil publico) -- e-mail nao exposto",
      sinal: activeFlavor.leads[0].sinal,
      score: 0.82,
      status: "qualificado",
      updated_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    },
    {
      id: "lead-0002",
      nome: activeFlavor.leads[1].nome,
      tipo: "pessoa",
      canal: "ugc_social",
      fonte: "reddit",
      contato: "DM aberta no perfil publico -- sem e-mail/telefone",
      sinal: activeFlavor.leads[1].sinal,
      score: 0.78,
      status: "qualificado",
      updated_at: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString(),
    },
    {
      id: "lead-0003",
      nome: activeFlavor.leads[2].nome,
      tipo: "empresa",
      canal: "b2b_cnpj",
      fonte: "cnpj_gov",
      contato: "site publico + formulario de contato (sem e-mail direto)",
      sinal: activeFlavor.leads[2].sinal,
      score: 0.71,
      status: "qualificado",
      updated_at: new Date(Date.now() - 1000 * 60 * 60 * 6).toISOString(),
    },
    {
      id: "lead-0004",
      nome: activeFlavor.leads[3].nome,
      tipo: "pessoa",
      canal: "b2c_marketplace",
      fonte: "ml",
      contato: "-- (marketplace nao expoe o contato do comprador)",
      sinal: activeFlavor.leads[3].sinal,
      score: 0.69,
      status: "qualificado",
      updated_at: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString(),
    },
    {
      id: "lead-0005",
      nome: activeFlavor.leads[4].nome,
      tipo: "empresa",
      canal: "ugc_social",
      fonte: "youtube",
      contato: "e-mail comercial na aba Sobre (perfil publico) -- nao transcrito aqui",
      sinal: activeFlavor.leads[4].sinal,
      score: 0.66,
      status: "qualificado",
      updated_at: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(),
    },
    {
      id: "lead-0006",
      nome: activeFlavor.leads[5].nome,
      tipo: "pessoa",
      canal: "ugc_social",
      fonte: "reddit",
      contato: "-- (perfil sem contato publico)",
      sinal: activeFlavor.leads[5].sinal,
      score: 0.52,
      status: "novo",
      updated_at: new Date(Date.now() - 1000 * 60 * 60 * 20).toISOString(),
    },
    {
      id: "lead-0007",
      nome: activeFlavor.leads[6].nome,
      tipo: "pessoa",
      canal: "b2c_marketplace",
      fonte: "ml",
      contato: "-- (nenhum contato encontrado)",
      sinal: activeFlavor.leads[6].sinal,
      score: 0.41,
      status: "descartado",
      updated_at: new Date(Date.now() - 1000 * 60 * 60 * 30).toISOString(),
    },
  ],
  // products carries the SENSITIVE fields (custo/preco_b2b/margem) in its rows on
  // purpose: the margin guard (DataManager.viewSchema) must hide them from the
  // default view EVEN WHEN present in the record. Only preco/estoque/etc. render.
  // SPEC 10 W5: products is publishable, so each row carries the L2 publish gate
  // (published / published_at). Two are DRAFT (published:false) so the Content Review
  // HITL page has REAL drafts to approve -> publish; one is already published (it does
  // NOT appear in the review queue). The state is honest -- the review queue reflects
  // these exact gate flags, nothing fabricated.
  products: [
    {
      id: "product-0001",
      nome: "Sample Widget A",
      sku: "WGT-A-001",
      categoria: "widgets",
      preco: 49,
      estoque: 120,
      ativo: true,
      custo: 18,
      preco_b2b: 32,
      margem: 63,
      published: false,
      published_at: null,
      updated_at: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(),
    },
    {
      id: "product-0002",
      nome: "Sample Widget B",
      sku: "WGT-B-002",
      categoria: "widgets",
      preco: 89,
      estoque: 0,
      ativo: false,
      custo: 40,
      preco_b2b: 60,
      margem: 55,
      published: false,
      published_at: null,
      updated_at: new Date(Date.now() - 1000 * 60 * 60 * 36).toISOString(),
    },
    {
      id: "product-0003",
      nome: "Sample Widget C (live)",
      sku: "WGT-C-003",
      categoria: "widgets",
      preco: 129,
      estoque: 40,
      ativo: true,
      custo: 55,
      preco_b2b: 90,
      margem: 57,
      published: true,
      published_at: new Date(Date.now() - 1000 * 60 * 60 * 60).toISOString(),
      updated_at: new Date(Date.now() - 1000 * 60 * 60 * 60).toISOString(),
    },
  ],
};

function fxEntityRows(entity: string): EntityRecord[] {
  if (!ENTITY_STORE[entity]) ENTITY_STORE[entity] = [];
  return ENTITY_STORE[entity];
}

export async function fxListEntity(entity: string): Promise<EntityRecord[]> {
  await new Promise((r) => setTimeout(r, 220)); // let the loading state render
  return fxEntityRows(entity).map((r) => ({ ...r }));
}

export async function fxCreateEntity(
  entity: string,
  values: Record<string, unknown>,
): Promise<EntityRecord> {
  await new Promise((r) => setTimeout(r, 260));
  const rows = fxEntityRows(entity);
  const record: EntityRecord = {
    ...(values as EntityRecord),
    id: `${entity}-${Math.random().toString(36).slice(2, 9)}`,
    updated_at: new Date().toISOString(),
  };
  rows.unshift(record);
  return { ...record };
}

export async function fxUpdateEntity(
  entity: string,
  id: string,
  values: Record<string, unknown>,
): Promise<EntityRecord> {
  await new Promise((r) => setTimeout(r, 260));
  const rows = fxEntityRows(entity);
  const idx = rows.findIndex((r) => r.id === id);
  if (idx < 0) {
    throw Object.assign(new Error("Record not found."), {
      status: 404,
      reason: "not_found",
    });
  }
  rows[idx] = {
    ...rows[idx],
    ...(values as EntityRecord),
    id,
    updated_at: new Date().toISOString(),
  };
  return { ...rows[idx] };
}

/**
 * PATCH /entity/{slug}/{id}/publish -> flip the PUBLISHED gate offline (SPEC 10 W1). Mirrors
 * fxUpdateEntity: find the row, set ``published`` + ``published_at`` (now() on publish, null on
 * unpublish -- the SAME documented policy as the live backend), echo the updated record. A
 * missing id 404s exactly like fxUpdateEntity so the toggle's error path is mode-transparent.
 */
export async function fxSetEntityPublished(
  entity: string,
  id: string,
  published: boolean,
): Promise<EntityRecord> {
  await new Promise((r) => setTimeout(r, 220));
  const rows = fxEntityRows(entity);
  const idx = rows.findIndex((r) => r.id === id);
  if (idx < 0) {
    throw Object.assign(new Error("Record not found."), {
      status: 404,
      reason: "not_found",
    });
  }
  rows[idx] = {
    ...rows[idx],
    published,
    published_at: published ? new Date().toISOString() : null,
    id,
  };
  return { ...rows[idx] };
}

export async function fxDeleteEntity(
  entity: string,
  id: string,
): Promise<void> {
  await new Promise((r) => setTimeout(r, 200));
  const rows = fxEntityRows(entity);
  const idx = rows.findIndex((r) => r.id === id);
  if (idx >= 0) rows.splice(idx, 1);
}

/** elapsed fraction (0..1) of the most-recent active fixture run -- filament UI. */
export function fxRunProgress(): number {
  let latest = 0;
  for (const started of RUN_STARTS.values()) {
    if (started > latest) latest = started;
  }
  if (latest === 0) return 1;
  return Math.min(1, (Date.now() - latest) / RUN_DURATION_MS);
}

// --- AGENTS catalog + READ surface (GET /agents, /agents/{id}) ---------------
//
// OVERLAY-GATED IN LIVE MODE: the real backend reads the agent catalog
// (.cex/config/capability_registry.json) + the tenant overlay ``agents:`` block.
// FIXTURES mode mirrors that with the brand-neutral fixture agents below across
// several nuclei, so the Agents surface renders end-to-end offline -- swapping to
// the real backend changes nothing in the components (same as fxListCards mirrors
// GET /capabilities). These demo agents carry the FULL detail (persona +
// capabilities table + typed I/O JSON Schema + SLA) so the detail page is
// reviewable offline; the live detail degrades to whatever the artifact carries.
//
// READ-ONLY: there is NO run here. The detail page shows a DISABLED 'Run'
// affordance (multi-step run = Phase B/C). Nothing in this fixture wires a run.

const FIXTURE_AGENTS: AgentDetail[] = [
  {
    id: "research_analyst",
    name: "Research Analyst",
    nucleus: "N01",
    kind: "agent",
    pillar: "P02",
    domain: "research-intelligence",
    goal: "Compile sourced competitive + market intelligence into typed briefs.",
    description:
      "A multi-step research agent: scans sources, cross-references, scores confidence, and emits a typed knowledge card with citations.",
    tools: ["web_search", "document_loader", "retriever"],
    model: "claude-sonnet",
    enabled: true,
    source: "fixture",
    persona:
      "You are a relentless research analyst. You never speculate without a source, you always surface at least two alternatives, and you score every claim by confidence. Analytical Envy is your lens: an insatiable hunger for the next data point.",
    capabilities: [
      {
        capability: "Competitive scan",
        description: "Score rivals across the dimensions that matter, with sourced cells.",
        tools: "web_search, retriever",
      },
      {
        capability: "Market snapshot",
        description: "Size demand, segments, and pricing clusters for a category.",
        tools: "web_search",
      },
      {
        capability: "Source dossier",
        description: "Assemble and rank primary sources on a topic by freshness + authority.",
        tools: "document_loader",
      },
    ],
    input_schema: [
      "{",
      '  "topic": "string",',
      '  "depth": "shallow|standard|deep",',
      '  "competitors": ["string"]',
      "}",
    ].join("\n"),
    output_schema: [
      "{",
      '  "brief_id": "string (uuid4)",',
      '  "findings": [{ "dimension": "string", "observation": "string", "confidence": "number (0..1)" }],',
      '  "sources": ["string (url)"]',
      "}",
    ].join("\n"),
    sla: [
      { label: "Latency target", value: "< 90s p50" },
      { label: "Quality floor", value: "F7 score >= 8.0" },
      { label: "Fallback", value: "Gemini 2.5 Pro on rate limit" },
    ],
    artifact_path: "N01_intelligence/P02_model/p02_agent_research_analyst.md",
  },
  {
    id: "copy_writer",
    name: "Copy Writer",
    nucleus: "N02",
    kind: "agent",
    pillar: "P02",
    domain: "marketing-creative",
    goal: "Produce on-brand, on-length ad copy and campaign hooks.",
    description:
      "A creative agent that writes ad variants (urgency, FOMO, value) inside platform character limits, grounded in the brand voice.",
    tools: ["brand_voice", "formatter"],
    model: "claude-sonnet",
    enabled: true,
    source: "fixture",
    persona:
      "You write seductive, irresistible prose. Creative Lust is your lens. Every line earns its place; every CTA pulls. You stay inside the brand voice and never exceed the platform's character budget.",
    capabilities: [
      {
        capability: "Ad variants",
        description: "Three hooks (urgency / FOMO / value) for one offer, A/B ready.",
        tools: "brand_voice",
      },
      {
        capability: "Email body",
        description: "Subject + preheader + on-brand body for a campaign.",
        tools: "formatter",
      },
    ],
    input_schema: [
      "{",
      '  "offer": "string",',
      '  "audience": "string",',
      '  "channel": "instagram|email|web",',
      '  "tone": "string"',
      "}",
    ].join("\n"),
    output_schema: [
      "{",
      '  "variants": [{ "hook": "string", "body": "string", "cta": "string", "chars": "integer" }]',
      "}",
    ].join("\n"),
    sla: [
      { label: "Latency target", value: "< 45s p50" },
      { label: "Voice", value: "brand_config voice match" },
    ],
    artifact_path: "N02_marketing/P02_model/p02_agent_copy_writer.md",
  },
  {
    id: "dependency_scanner",
    name: "Dependency Scanner",
    nucleus: "N03",
    kind: "agent",
    pillar: "P02",
    domain: "security",
    goal: "Parse lockfiles, cross-reference CVE feeds, score CVSS, emit remediation.",
    description:
      "An engineering agent that becomes a dependency vulnerability scanner -- it parses lockfiles, looks up CVEs, scores CVSS, and triages a remediation report before code ships.",
    tools: ["Read", "Bash", "http_client"],
    model: "claude-sonnet",
    enabled: true,
    source: "fixture",
    persona:
      "You become a dependency vulnerability scanner. Inventive Pride is your lens: technical precision over hand-waving. You honor the failure modes -- abort on an unparseable lockfile, retry a flaky CVE feed, skip a private package you cannot resolve.",
    capabilities: [
      {
        capability: "Lockfile parsing",
        description: "Extract dependencies from package-lock.json, poetry.lock, Cargo.lock.",
        tools: "Read, parsers",
      },
      {
        capability: "CVE lookup",
        description: "Query NVD / GitHub Advisory / OSV.dev for known vulnerabilities.",
        tools: "http_client",
      },
      {
        capability: "Risk scoring",
        description: "Calculate CVSS v3.1 severity and rank by exploitability.",
        tools: "cvss",
      },
    ],
    input_schema: [
      "{",
      '  "project_path": "string",',
      '  "lockfile_type": "npm|pip|cargo",',
      '  "severity_threshold": "CRITICAL|HIGH"',
      "}",
    ].join("\n"),
    output_schema: [
      "{",
      '  "scan_id": "string (uuid4)",',
      '  "vulnerabilities": [{ "package": "string", "cve_id": "string", "severity": "string", "cvss_score": "number", "fixed_in": "string|null" }],',
      '  "summary": { "critical_count": "integer", "high_count": "integer" }',
      "}",
    ].join("\n"),
    sla: [
      { label: "Latency target", value: "< 120s for 500 deps" },
      { label: "Recovery", value: "abort / retry / skip per failure mode" },
    ],
    artifact_path: "N03_engineering/P02_model/p02_agent_dependency_scanner.md",
  },
  {
    id: "knowledge_curator",
    name: "Knowledge Curator",
    nucleus: "N04",
    kind: "agent",
    pillar: "P02",
    domain: "knowledge",
    goal: "Capture facts + processes as RAG-ready, versioned knowledge cards.",
    description:
      "A knowledge agent that ingests a source, chunks + structures it into a typed knowledge card, and registers it for retrieval -- with lineage and versioning.",
    tools: ["document_loader", "chunk_strategy", "vector_store"],
    model: "claude-haiku",
    enabled: true,
    source: "fixture",
    persona:
      "You are an insatiable curator. Knowledge Gluttony is your lens: completeness and depth. You never overwrite a fact without versioning it, and you ground every card in its source lineage.",
    capabilities: [
      {
        capability: "Ingest + chunk",
        description: "Load a source, split it by the configured chunk strategy.",
        tools: "document_loader, chunk_strategy",
      },
      {
        capability: "Index",
        description: "Embed + register chunks into the tenant vector store.",
        tools: "vector_store",
      },
    ],
    input_schema: [
      "{",
      '  "source_url": "string",',
      '  "domain": "string",',
      '  "chunk_size": "integer"',
      "}",
    ].join("\n"),
    output_schema: [
      "{",
      '  "card_id": "string",',
      '  "chunks_indexed": "integer",',
      '  "lineage": ["string"]',
      "}",
    ].join("\n"),
    sla: [
      { label: "Latency target", value: "< 60s per source" },
      { label: "Memory rule", value: "version, never overwrite" },
    ],
    artifact_path: "N04_knowledge/P02_model/p02_agent_knowledge_curator.md",
  },
  {
    id: "pricing_strategist",
    name: "Pricing Strategist",
    nucleus: "N06",
    kind: "agent",
    pillar: "P02",
    domain: "commercial",
    goal: "Design differentiated tiers + revenue framing grounded in the segment.",
    description:
      "A commercial agent that designs a subscription plan matrix -- differentiated tiers, feature gating, and price anchoring -- grounded in segment + competitor research.",
    tools: ["retriever", "roi_calculator"],
    model: "claude-sonnet",
    enabled: false,
    source: "fixture",
    persona:
      "You maximize every revenue stream without cannibalizing the line. Strategic Greed is your lens. You never price without market research -- you depend on the Research Analyst for segment data first.",
    capabilities: [
      {
        capability: "Tier design",
        description: "Three tiers (free / pro / enterprise) with feature gating.",
        tools: "retriever",
      },
      {
        capability: "ROI framing",
        description: "Quantify payback period and annual return for a buyer.",
        tools: "roi_calculator",
      },
    ],
    input_schema: [
      "{",
      '  "product": "string",',
      '  "segment": "string",',
      '  "competitors": ["string"]',
      "}",
    ].join("\n"),
    output_schema: [
      "{",
      '  "tiers": [{ "name": "string", "price": "number", "features": ["string"] }],',
      '  "anchor": "string"',
      "}",
    ].join("\n"),
    sla: [
      { label: "Dependency", value: "requires N01 segment research" },
      { label: "Guard", value: "no tier cannibalization" },
    ],
    artifact_path: "N06_commercial/P02_model/p02_agent_pricing_strategist.md",
  },
  {
    id: "ops_supervisor",
    name: "Ops Supervisor",
    nucleus: "N05",
    kind: "agent_card",
    pillar: "P08",
    domain: "operations",
    goal: "Gate quality, run tests, and coordinate deploy under a strict SLA.",
    description:
      "An operations agent card: it runs the quality gate, executes the test suite, and coordinates a deploy -- the gate is the gate, it does not negotiate.",
    tools: ["Bash", "code_executor"],
    model: "claude-sonnet",
    enabled: true,
    source: "fixture",
    persona:
      "Gating Wrath is your lens. The gate is the gate. You run the suite, you score, you block below the floor -- and you never negotiate the criteria.",
    capabilities: [
      {
        capability: "Quality gate",
        description: "Run F7 GOVERN gates and block a publish below the floor.",
        tools: "code_executor",
      },
      {
        capability: "Test + deploy",
        description: "Execute the suite, coordinate a gated deploy on green.",
        tools: "Bash",
      },
    ],
    sla: [
      { label: "Gate floor", value: "8.0 (block below)" },
      { label: "Deploy", value: "green-only, gated" },
      { label: "Latency target", value: "< 5min suite" },
    ],
    artifact_path: "N05_operations/P08_architecture/agent_card_n05.md",
  },
];

export function fxListAgents(): Agent[] {
  // Project to the list shape (the list omits the heavy detail fields, like the
  // backend's list_agents vs get_agent split). The detail fields are returned by
  // fxGetAgent.
  return FIXTURE_AGENTS.map((a) => ({
    id: a.id,
    name: a.name,
    nucleus: a.nucleus,
    kind: a.kind,
    pillar: a.pillar,
    goal: a.goal,
    description: a.description,
    domain: a.domain,
    tools: [...a.tools],
    model: a.model,
    enabled: a.enabled,
    source: a.source,
  }));
}

export async function fxGetAgent(id: string): Promise<AgentDetail> {
  await new Promise((r) => setTimeout(r, 160)); // let the loading state render
  const agent = FIXTURE_AGENTS.find((a) => a.id === id);
  if (!agent) {
    throw Object.assign(new Error("Agent not found."), {
      status: 404,
      reason: "unknown_agent",
    });
  }
  return JSON.parse(JSON.stringify(agent)) as AgentDetail;
}

// --- AGENT RUN (POST /agent/run -- single step, ADR Phase B) ------------------
//
// Mirrors fxRunCapability EXACTLY (the run is SYNCHRONOUS): refuses a disabled /
// unknown agent, drives the SAME run-progress mechanism so the 8F filament fires,
// then resolves to an AgentRunResultView. The fake artifact REFLECTS the assembled
// contract (the agent's persona + Output Schema honored) so the offline run is
// faithful to what the real backend's ASSEMBLE loader produces. Records the run into
// the in-memory results store (so the Results ledger shows it). No run_id/poll.

function fakeAgentArtifact(agent: AgentDetail, inputs: Record<string, unknown>): string {
  const stamp = new Date().toISOString();
  const topic =
    (typeof inputs.topic === "string" && inputs.topic) ||
    (typeof inputs.intent === "string" && inputs.intent) ||
    `${agent.name} output`;
  return [
    "---",
    `id: run_${agent.id}_${Math.random().toString(36).slice(2, 8)}`,
    `kind: ${agent.kind || "agent"}`,
    `pillar: ${agent.pillar || "P02"}`,
    `nucleus: ${agent.nucleus || "N01"}`,
    `agent: ${agent.id}`,
    `title: "${String(topic).slice(0, 60)}"`,
    "version: 0.1.0",
    "quality: null",
    `created: "${stamp}"`,
    "tags: [agent_run, single_step, fixture]",
    "---",
    "",
    `# ${agent.name} -- single-step run`,
    "",
    "## Contract honored",
    "",
    `Persona: ${agent.persona ? agent.persona.slice(0, 120) + "..." : "(none)"}`,
    `Declared tools (context only, not executed): ${(agent.tools ?? []).join(", ") || "none"}`,
    "",
    "## Output",
    "",
    "A typed artifact produced by the CEXAI agent runtime in FIXTURES mode --",
    "one CEXAgent.build (single chat()), the agent's Input/Output schema honored.",
    "Multi-step tool execution + async run_id land in Phase C.",
  ].join("\n");
}

export async function fxRunAgent(
  agentId: string,
  inputs: Record<string, unknown>,
): Promise<AgentRunResultView> {
  const agent = FIXTURE_AGENTS.find((a) => a.id === agentId);
  if (!agent) {
    throw Object.assign(new Error("This agent is not available for your tenant."), {
      status: 404,
      reason: "unresolved_capability",
    });
  }
  if (!agent.enabled) {
    // mimic the backend refusing a disabled/gated-out agent (capability_disabled -> 403)
    throw Object.assign(
      new Error("This agent is not enabled for your tenant."),
      { status: 403, reason: "capability_disabled" },
    );
  }

  const runKey = `agent-${agentId}-${Date.now()}`;
  RUN_STARTS.set(runKey, Date.now());
  await new Promise((r) => setTimeout(r, RUN_DURATION_MS));
  RUN_STARTS.delete(runKey);

  const score = Math.round((8.4 + Math.random() * 1.2) * 10) / 10;
  const result: AgentRunResultView = {
    tenant_id: FIXTURE_TENANT.tenant_id,
    agent_id: agentId,
    agent_name: agent.name,
    capability: agentId,
    kind: agent.kind || "agent",
    pillar: agent.pillar || "P02",
    nucleus: agent.nucleus || "N01",
    artifact: fakeAgentArtifact(agent, inputs),
    score,
    passed: true,
    status: "persisted",
    model_used: `${agent.model || "claude-sonnet-4-6"} (fixture)`,
    record_id: `row-${Math.random().toString(36).slice(2, 10)}`,
    persisted: true,
    steps: 1,
    trace: F8_STEPS.map((s) => `${s.id} ${s.name}: ok`).join("  |  "),
    errors: [],
  };

  persistResult(
    {
      id: result.record_id as string,
      capability: agentId,
      kind: result.kind,
      created_at: new Date().toISOString(),
      label: agent.name,
      nucleus: agent.nucleus,
      score: result.score,
    },
    result,
  );

  return result;
}

// --- ASYNC MULTI-STEP agent run (POST /agent/runs, GET /agent/run/{id}) -------
//
// The Phase C async contract: fxStartAgentRun registers an in-memory run with a
// stable run_id + a SCRIPTED plan/act/observe/tool step plan; fxGetAgentRun GROWS
// the run's steps_log by ONE step on each successive poll (a realistic arc:
// plan -> act -> tool -> observe -> ...), advancing cost.steps_used, until it reaches
// a terminal snapshot (status='completed', done=true) carrying the SAME terminal
// shape fxRunAgent produces for that agent (artifact/score/passed/trace). ONE tool
// step carries an approval_id so the cockpit's HITL "approval pending" chip is
// exercised. Credential-free + deterministic: the cockpit visibly animates while
// polling, with NO backend. Mirrors the live backend agent_runs.RunRecord.snapshot.

/** One scripted async run held in memory while the cockpit polls it. */
interface FixtureRun {
  run_id: string;
  agent_id: string;
  /** the full scripted step plan; steps_log reveals one more of these per poll. */
  plan: AgentStep[];
  /** how many steps of ``plan`` have been revealed so far. */
  revealed: number;
  /** the terminal result view (artifact/score/...), assembled at kickoff. */
  terminal: AgentRunResultView;
  /** the OQ4 budget ceiling for the run (steps + tokens). */
  step_ceiling: number;
  max_tokens: number;
}

// Stable run_id counter so fxStartAgentRun returns a deterministic handle.
let RUN_SEQ = 0;
const ASYNC_RUNS = new Map<string, FixtureRun>();

/**
 * Build the scripted multi-step plan for an agent. ~5-7 steps so the cockpit
 * visibly animates: plan -> act -> tool (with tool_io) -> tool (GATED, carries an
 * approval_id) -> observe -> act -> observe. The tool steps reflect the agent's
 * FIRST declared tool so the trace is faithful to its real contract.
 */
function buildStepPlan(
  agent: AgentDetail,
  inputs: Record<string, unknown>,
): AgentStep[] {
  const topic =
    (typeof inputs.topic === "string" && inputs.topic) ||
    (typeof inputs.intent === "string" && inputs.intent) ||
    (typeof inputs.offer === "string" && inputs.offer) ||
    `${agent.name} objective`;
  const tools = agent.tools ?? [];
  const tool0 = tools[0] || "tool";
  const tool1 = tools[1] || tool0;

  const steps: AgentStep[] = [
    {
      index: 0,
      kind: "plan",
      content: {
        thought: `Decompose the objective into a tool-using plan: ${String(topic).slice(0, 80)}`,
        subgoals: ["gather", "act", "verify"],
      },
    },
    {
      index: 1,
      kind: "act",
      content: {
        thought: `Select the first action and the tool to run (${tool0}).`,
        decision: `invoke ${tool0}`,
      },
    },
    {
      index: 2,
      kind: "tool",
      content: { note: `Ran ${tool0} (reversible) -- result folded into context.` },
      tool: tool0,
      tool_io: {
        args: { query: String(topic).slice(0, 60), depth: "standard" },
        result: { ok: true, items: 3, summary: `${tool0} returned 3 candidate sources.` },
      },
    },
    {
      index: 3,
      kind: "tool",
      content: {
        note: `Requested ${tool1} (IRREVERSIBLE) -- gated through HITL, NOT executed. Awaiting human approval.`,
      },
      tool: tool1,
      tool_io: {
        args: { action: "persist", target: "tenant_data_plane" },
      },
      // OQ8 emit-and-defer: an irreversible tool gated through HITL. The tool was
      // NOT executed; a human approval is pending. The cockpit shows the HITL chip.
      approval_id: `appr_${agent.id}_${Math.random().toString(36).slice(2, 8)}`,
    },
    {
      index: 4,
      kind: "observe",
      content: {
        observation: `Folded ${tool0} output into the working set; the gated action stays pending.`,
        confidence: 0.78,
      },
    },
    {
      index: 5,
      kind: "act",
      content: {
        thought: "Synthesize the typed artifact from the gathered + observed context.",
        decision: "produce artifact",
      },
    },
    {
      index: 6,
      kind: "observe",
      content: {
        observation: "Artifact passes the F7 structural gate; run is ready to finalize.",
        confidence: 0.84,
      },
    },
  ];
  return steps;
}

/**
 * POST /agent/runs (fixtures): refuse a disabled/unknown agent (same shape as the
 * backend), else register a scripted in-memory run with a stable run_id and return
 * the AgentRunStarted handle. The run does NOT advance here -- fxGetAgentRun reveals
 * one step per poll, so the cockpit animates as it polls.
 */
export async function fxStartAgentRun(
  agentId: string,
  inputs: Record<string, unknown>,
): Promise<AgentRunStarted> {
  const agent = FIXTURE_AGENTS.find((a) => a.id === agentId);
  if (!agent) {
    throw Object.assign(new Error("This agent is not available for your tenant."), {
      status: 404,
      reason: "unresolved_capability",
    });
  }
  if (!agent.enabled) {
    throw Object.assign(
      new Error("This agent is not enabled for your tenant."),
      { status: 403, reason: "capability_disabled" },
    );
  }

  RUN_SEQ += 1;
  const run_id = `run_${agentId}_${RUN_SEQ}`;
  const plan = buildStepPlan(agent, inputs);

  // The terminal result view -- the SAME shape fxRunAgent produces, so the cockpit's
  // ResultView renders the artifact/score/gate exactly like the single-step path.
  const score = Math.round((8.4 + Math.random() * 1.2) * 10) / 10;
  const terminal: AgentRunResultView = {
    tenant_id: FIXTURE_TENANT.tenant_id,
    agent_id: agentId,
    agent_name: agent.name,
    capability: agentId,
    kind: agent.kind || "agent",
    pillar: agent.pillar || "P02",
    nucleus: agent.nucleus || "N01",
    artifact: fakeAgentArtifact(agent, inputs),
    score,
    passed: true,
    status: "persisted",
    model_used: `${agent.model || "claude-sonnet-4-6"} (fixture)`,
    record_id: `row-${Math.random().toString(36).slice(2, 10)}`,
    persisted: true,
    steps: plan.length,
    trace: F8_STEPS.map((s) => `${s.id} ${s.name}: ok`).join("  |  "),
    errors: [],
  };

  ASYNC_RUNS.set(run_id, {
    run_id,
    agent_id: agentId,
    plan,
    revealed: 0,
    terminal,
    step_ceiling: plan.length,
    max_tokens: 16000,
  });

  return { run_id, status: "running", tenant_id: FIXTURE_TENANT.tenant_id };
}

/**
 * GET /agent/run/{run_id} (fixtures): the POLL snapshot. Reveals ONE more scripted
 * step per call (steps_log grows), advancing cost.steps_used, until every step is
 * revealed -- then returns the TERMINAL snapshot (status='completed', done=true) with
 * the artifact/score/passed/trace + records it into the Results ledger ONCE. A short
 * delay lets the polling UI breathe. Mirrors RunRecord.snapshot() (credential-free).
 */
export async function fxGetAgentRun(runId: string): Promise<AgentRun> {
  await new Promise((r) => setTimeout(r, 90));
  const run = ASYNC_RUNS.get(runId);
  if (!run) {
    throw Object.assign(new Error("No such run for this tenant."), {
      status: 404,
      reason: "unknown_run",
    });
  }

  // Reveal the next step (bounded by the plan length).
  if (run.revealed < run.plan.length) run.revealed += 1;
  const done = run.revealed >= run.plan.length;
  const steps_log = run.plan.slice(0, run.revealed);
  // Approximate token burn from steps so the budget meter moves honestly.
  const tokens_used = Math.min(run.max_tokens, run.revealed * 2100);

  const base: AgentRun = {
    ...run.terminal,
    run_id: run.run_id,
    status: done ? "completed" : "running",
    steps_log: steps_log.map((s) => ({ ...s })),
    steps: run.revealed,
    cost: {
      steps_used: run.revealed,
      max_steps: run.step_ceiling,
      step_ceiling: run.step_ceiling,
      tokens_used,
      max_tokens: run.max_tokens,
    },
    done,
  };

  if (!done) {
    // While running, the terminal-only fields are not yet meaningful: keep the
    // artifact empty + gate unresolved so the cockpit shows the live trace, not a
    // premature result (mirrors the backend's running snapshot).
    base.artifact = "";
    base.passed = false;
    base.persisted = false;
    base.record_id = null;
    return base;
  }

  // Terminal: record the run into the results store ONCE (so the Results ledger shows
  // it, surviving reload), exactly like fxRunCapability/fxRunAgent do. The dedupe guard
  // checks the merged ledger so a persisted terminal row is not re-added on re-poll.
  if (!mergedResults().some((r) => r.id === run.terminal.record_id)) {
    persistResult(
      {
        id: run.terminal.record_id as string,
        capability: run.agent_id,
        kind: run.terminal.kind,
        created_at: new Date().toISOString(),
        label: run.terminal.agent_name,
        nucleus: run.terminal.nucleus,
        score: run.terminal.score,
      },
      base,
    );
  }
  return base;
}

// --- CREWS catalog + READ surface (GET /crews, /crews/{id}) -------------------
//
// OVERLAY-GATED IN LIVE MODE: the real backend discovers the crew_template artifacts
// on disk (N0*/P12_orchestration/**/p12_ct_*.md) + the tenant overlay ``crews:`` block.
// FIXTURES mode mirrors that with the brand-neutral fixture crews below across several
// nuclei + all three process topologies (sequential / hierarchical / consensus), so the
// Crews surface renders end-to-end offline -- swapping to the real backend changes
// nothing in the components (same as fxListCards mirrors GET /capabilities). These demo
// crews carry the FULL detail (the roles table + handoff protocol + provenance) so the
// detail page is reviewable offline; the live detail degrades to whatever the
// crew_template carries.
//
// READ-ONLY: there is NO run here. A crew is the layer ABOVE single agents; running a
// crew is the founder-gated control-plane step. Nothing in this fixture wires a run.

const FIXTURE_CREWS: CrewDetail[] = [
  {
    id: "product_launch",
    name: "Product Launch Crew",
    nucleus: "N02",
    kind: "crew_template",
    pillar: "P12",
    process: "sequential",
    role_count: 4,
    goal: "Ship a cross-function product launch package: positioning, copy, assets, and a QA gate.",
    description:
      "A 4-role sequential crew that ships a new product launch package. Each role grounds on the previous artifact: market intel -> positioning copy -> visual assets -> QA gate.",
    domain: "product launch orchestration",
    enabled: true,
    source: "crew_template",
    roles: [
      {
        name: "market_researcher",
        agent: "p02_ra_market_researcher.md",
        goal: "Scan market + competitors, produce a positioning brief.",
      },
      {
        name: "copywriter",
        agent: "p02_ra_copywriter.md",
        goal: "Turn the brief into launch copy (tagline, headline, body).",
      },
      {
        name: "designer",
        agent: "p02_ra_designer.md",
        goal: "Compose the visual assets spec (hero, social, email header).",
      },
      {
        name: "qa_reviewer",
        agent: "p02_ra_qa_reviewer.md",
        goal: "Enforce the quality gate (9.0) on every deliverable.",
      },
    ],
    handoff_protocol: "a2a-task-sequential",
    handoff_note:
      "Each role writes a completion signal with artifact_path + quality_score. The next role reads the prior artifact before starting its own F1 CONSTRAIN.",
    artifact_path: "N02_marketing/P12_orchestration/p12_ct_product_launch.md",
  },
  {
    id: "cross_provider_council",
    name: "Cross-Provider Judging Council",
    nucleus: "N03",
    kind: "crew_template",
    pillar: "P12",
    process: "consensus",
    role_count: 4,
    goal: "Run N independent judges (one per LLM provider) against the same rubric to detect sycophancy.",
    description:
      "A consensus crew that runs 4 judges in parallel, each bound to a different LLM provider, against the same scoring_rubric -- then computes consensus_score + divergence_score to guard against single-model sycophancy.",
    domain: "consensus judging",
    enabled: true,
    source: "crew_template",
    roles: [
      {
        name: "judge_claude",
        agent: "p02_ra_council_judges (judge_claude)",
        goal: "Primary model -- high reasoning, potential self-bias.",
      },
      {
        name: "judge_gemini",
        agent: "p02_ra_council_judges (judge_gemini)",
        goal: "Cross-family diversity -- different training data.",
      },
      {
        name: "judge_gpt",
        agent: "p02_ra_council_judges (judge_gpt)",
        goal: "Cross-family diversity -- independent alignment.",
      },
      {
        name: "judge_ollama",
        agent: "p02_ra_council_judges (judge_ollama)",
        goal: "Local model -- no API dependency, different scale.",
      },
    ],
    handoff_protocol: "a2a-task-consensus",
    handoff_note:
      "All 4 judges run in parallel. Each writes a completion signal with score + rationale. An aggregator collects all 4 before computing consensus (judges never see each other's scores first).",
    artifact_path: "N03_engineering/P12_orchestration/p12_ct_cross_provider_council.md",
  },
  {
    id: "incident_response",
    name: "Incident Response Crew",
    nucleus: "N05",
    kind: "crew_template",
    pillar: "P12",
    process: "sequential",
    role_count: 4,
    goal: "Detect, contain, analyze, and document a production incident end-to-end.",
    description:
      "A 4-role sequential crew for production incidents: detect scope -> apply fix -> root cause -> incident report. Each role emits a discrete artifact the next consumes.",
    domain: "production incident management",
    enabled: true,
    source: "crew_template",
    roles: [
      {
        name: "detector",
        agent: "p02_ra_detector.md",
        goal: "Scan logs/metrics, triage severity, scope impact.",
      },
      {
        name: "responder",
        agent: "p02_ra_responder.md",
        goal: "Apply the fix, validate resolution, document actions taken.",
      },
      {
        name: "analyst",
        agent: "p02_ra_analyst.md",
        goal: "Root cause analysis, identify systemic patterns + failure modes.",
      },
      {
        name: "reporter",
        agent: "p02_ra_reporter.md",
        goal: "Write the incident report, update runbooks, create regression checks.",
      },
    ],
    handoff_protocol: "a2a-task-sequential",
    handoff_note:
      "Each role writes a completion signal with artifact_path + quality_score. The next role reads the prior artifact before starting. Signal path: .cex/runtime/signals/.",
    artifact_path:
      "N05_operations/P12_orchestration/crews/p12_ct_incident_response.md",
  },
  {
    id: "rag_pipeline",
    name: "RAG Pipeline Crew",
    nucleus: "N04",
    kind: "crew_template",
    pillar: "P12",
    process: "sequential",
    role_count: 3,
    goal: "Turn raw sources into a retrieval-ready index: load + chunk -> embed -> verify.",
    description:
      "A 3-role sequential crew that builds a retrieval pipeline -- a loader chunks sources, an embedder indexes them into the tenant vector store, and an evaluator verifies retrieval quality.",
    domain: "retrieval engineering",
    enabled: true,
    source: "crew_template",
    roles: [
      {
        name: "loader",
        agent: "p02_ra_loader.md",
        goal: "Load sources and split them by the configured chunk strategy.",
      },
      {
        name: "indexer",
        agent: "p02_ra_indexer.md",
        goal: "Embed + register chunks into the tenant vector store.",
      },
      {
        name: "retrieval_evaluator",
        agent: "p02_ra_retrieval_evaluator.md",
        goal: "Score retrieval precision/recall and flag gaps.",
      },
    ],
    handoff_protocol: "a2a-task-sequential",
    handoff_note:
      "Each role hands its artifact to the next via an a2a Task; the indexer needs the loader's chunks, the evaluator needs the live index.",
    artifact_path: "N04_knowledge/P12_orchestration/crews/p12_ct_rag_pipeline.md",
  },
  {
    id: "release_gate",
    name: "Release Gate Crew",
    nucleus: "N05",
    kind: "crew_template",
    pillar: "P12",
    process: "hierarchical",
    role_count: 4,
    goal: "Coordinate a gated release: a manager delegates test, security, and deploy checks.",
    description:
      "A hierarchical crew where a release manager coordinates workers -- it delegates the test suite, a security scan, and a deploy readiness check, then makes the green/no-go call.",
    domain: "release operations",
    enabled: true,
    source: "crew_template",
    roles: [
      {
        name: "release_manager",
        agent: "p02_ra_release_manager.md",
        goal: "Coordinate the workers, gather verdicts, make the green/no-go call.",
      },
      {
        name: "test_runner",
        agent: "p02_ra_test_runner.md",
        goal: "Run the suite, report pass/fail with coverage.",
      },
      {
        name: "security_scanner",
        agent: "p02_ra_security_scanner.md",
        goal: "Scan dependencies + secrets, block on a critical finding.",
      },
      {
        name: "deploy_checker",
        agent: "p02_ra_deploy_checker.md",
        goal: "Verify deploy readiness (migrations, config, rollback plan).",
      },
    ],
    handoff_protocol: "a2a-task-hierarchical",
    handoff_note:
      "The manager role fans out a2a Tasks to the workers and collects their signals; it owns the final gate decision (workers never deploy directly).",
    artifact_path: "N05_operations/P12_orchestration/crews/p12_ct_release_gate.md",
  },
  {
    id: "pricing_workshop",
    name: "Pricing Workshop Crew",
    nucleus: "N06",
    kind: "crew_template",
    pillar: "P12",
    process: "sequential",
    role_count: 3,
    goal: "Design a pricing model grounded in research: segment scan -> tier design -> ROI framing.",
    description:
      "A 3-role sequential crew that designs a pricing model -- it scans the segment, designs differentiated tiers with feature gating, and frames the ROI. Disabled for this tenant in the overlay.",
    domain: "commercial strategy",
    enabled: false,
    source: "crew_template",
    roles: [
      {
        name: "segment_researcher",
        agent: "p02_ra_segment_researcher.md",
        goal: "Scan the segment + competitor pricing (research first).",
      },
      {
        name: "tier_designer",
        agent: "p02_ra_tier_designer.md",
        goal: "Design 3 tiers with feature gating and an anchor price.",
      },
      {
        name: "roi_framer",
        agent: "p02_ra_roi_framer.md",
        goal: "Quantify payback period and annual return for the buyer.",
      },
    ],
    handoff_protocol: "a2a-task-sequential",
    handoff_note:
      "The tier designer must not price without the segment research; the ROI framer needs the tier matrix. Strict sequence prevents un-grounded pricing.",
    artifact_path: "N06_commercial/P12_orchestration/crews/p12_ct_pricing_workshop.md",
  },
];

export function fxListCrews(): Crew[] {
  // Project to the list shape (the list keeps roles so the card can show role count +
  // names, but the heavy handoff_note/artifact_path live on the detail). The detail
  // fields are returned by fxGetCrew.
  return FIXTURE_CREWS.map((c) => ({
    id: c.id,
    name: c.name,
    nucleus: c.nucleus,
    kind: c.kind,
    pillar: c.pillar,
    process: c.process,
    role_count: c.role_count,
    roles: c.roles.map((r) => ({ ...r })),
    goal: c.goal,
    description: c.description,
    domain: c.domain,
    enabled: c.enabled,
    source: c.source,
  }));
}

export async function fxGetCrew(id: string): Promise<CrewDetail> {
  await new Promise((r) => setTimeout(r, 160)); // let the loading state render
  const crew = FIXTURE_CREWS.find((c) => c.id === id);
  if (!crew) {
    throw Object.assign(new Error("Crew not found."), {
      status: 404,
      reason: "unknown_crew",
    });
  }
  return JSON.parse(JSON.stringify(crew)) as CrewDetail;
}
