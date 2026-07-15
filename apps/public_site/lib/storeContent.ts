// ----------------------------------------------------------------------------
// storeContent -- the STATIC storefront content the public API does NOT carry.
//
// The public /tenant-info + /public/catalog contract carries the BRAND + the published
// CATALOG only -- there is no blog endpoint and no B2B endpoint. So the Blog and B2B
// pages render from curated, clearly-flagged SAMPLE content. It is HONEST BY
// CONSTRUCTION: every block is marked "amostra / dados simulados" and is NEVER claimed
// to be a tenant's real article or real wholesale offer.
//
// SOURCE OF TRUTH: the PER-TENANT blog posts/categories + B2B content moved to
// lib/tenantConfig (the single source of truth). The per-slug maps are GONE -- the
// resolvers (blogPostsFor / blogCategoriesFor / b2bContentFor / blogSubtitleFor) now DERIVE
// from tenantConfigFor(slug). The built-in retail default data + the services-vertical sample
// data are re-exported
// from tenantConfig so existing import sites + tests are unchanged. The SHARED, NOT-per-
// tenant content (the PT-BR trust row + the wholesale B2B sample blocks rendered when
// b2b.mode === "wholesale") stays defined here.
//
// First-party DECORATIVE cat PHOTOS live under /public/images/*.jpg (same-origin,
// NOT subject to isSafeMediaSrc -- that gate is only for tenant-PAYLOAD media). The
// blogCoverSrc helper resolves a BlogCover key to its /images/* path.
//
// ASCII-only + diacritic-free (house style). PURE DATA -- no React, no runtime.
// ----------------------------------------------------------------------------

import { tenantConfigFor } from "@/lib/tenantConfig";
import {
  SAMPLE_BLOG_POSTS,
  BLOG_CATEGORIES,
  ORBIT_BLOG_POSTS,
  ORBIT_BLOG_CATEGORIES,
  ORBIT_B2B,
  DEFAULT_B2B_CONTENT,
} from "@/lib/tenantConfig";

// Re-export the per-tenant blog/b2b data (it lives in tenantConfig now) so existing import
// sites + tests -- import { SAMPLE_BLOG_POSTS, ORBIT_BLOG_POSTS, ... } from
// "@/lib/storeContent" -- keep working unchanged (same array references).
export {
  SAMPLE_BLOG_POSTS,
  BLOG_CATEGORIES,
  ORBIT_BLOG_POSTS,
  ORBIT_BLOG_CATEGORIES,
  ORBIT_B2B,
  DEFAULT_B2B_CONTENT,
};

/** One PT-BR trust signal (monochrome row -- foreground icon + muted label). */
export interface TrustSignal {
  /** a short icon key the renderer maps to an inline SVG. */
  icon: "pix" | "card" | "shield" | "refresh" | "origin";
  /** the trust label (PT-BR, accents intentionally avoided per house style). */
  label: string;
}

/** The curated PT-BR trust row (design_system.md s9 -- monochrome, never a rainbow seal). */
export const TRUST_SIGNALS: readonly TrustSignal[] = [
  { icon: "pix", label: "PIX instantaneo" },
  { icon: "card", label: "12x sem juros" },
  { icon: "shield", label: "Compra 100% segura" },
  { icon: "refresh", label: "Troca gratis em 30 dias" },
  { icon: "origin", label: "Feito no Brasil" },
] as const;

// --- SAMPLE BLOG (amostra) ---------------------------------------------------
//
// There is no blog endpoint -- this is clearly-flagged sample editorial content. The POSTS
// + CATEGORIES per tenant live in lib/tenantConfig; the resolvers below derive from it.

/** A blog cover-art key -> a same-origin /images/* photo (first-party decorative). */
export type BlogCover =
  | "cat-blog-1"
  | "cat-blog-2"
  | "cat-blog-3"
  | "cat-section"
  | "cat-product"
  | "cat-hero";

/** One sample blog post. ``slug`` is the URL segment (validated by isValidKind-shape). */
export interface SampleBlogPost {
  /** URL slug -- lowercase, hyphenated (matches the kind/slug allowlist shape). */
  slug: string;
  /** the article category label. */
  category: string;
  /** the headline. */
  title: string;
  /** a one-paragraph deck / excerpt. */
  excerpt: string;
  /** estimated read time, e.g. "4 min". */
  readTime: string;
  /** the (sample) publish date as YYYY-MM-DD. */
  date: string;
  /** the cover-art key (a first-party same-origin /images photo). OPTIONAL: a brand-mode
   *  tenant (imagery_mode "brand" -- no photos) OMITS it and renders a brand-gradient tile,
   *  so a services/non-photo tenant carries NO photo-key on its posts. A photos-mode tenant
   *  (demo-acme) supplies it; the renderer only reads it when showPhotos is true. */
  cover?: BlogCover;
  /** the article body -- an array of paragraphs (rendered as text, never markup). */
  body: string[];
  /** whether this post is featured on the blog landing. */
  featured?: boolean;
}

/** Resolve a BlogCover key to its same-origin /images path (first-party, decorative). */
export function blogCoverSrc(cover: BlogCover): string {
  return "/images/" + cover + ".jpg";
}

/** Resolve the blog posts a tenant SLUG offers, DERIVED from its config. A registered tenant
 *  -> its posts; any other slug -> the DEFAULT built-in retail posts (zero-regression). TOTAL. */
export function blogPostsFor(slug: string): readonly SampleBlogPost[] {
  return tenantConfigFor(slug).blog.posts;
}

/** Resolve the blog category chips a tenant SLUG offers (matches blogPostsFor), DERIVED from
 *  its config. TOTAL. */
export function blogCategoriesFor(slug: string): readonly string[] {
  return tenantConfigFor(slug).blog.categories;
}

/** The blog-banner SUBTITLE for a tenant SLUG -- the leading category word comes from the
 *  tenant's ``shape.blog_subtitle_category`` (per-tenant: "Bem-estar" retail, "Seguranca"
 *  for a security-led services tenant), so a non-retail tenant no longer shows the
 *  hard-coded cat wellness line. Byte-identical to the historic line for demo-acme. TOTAL.
 *  ASCII-only. */
export function blogSubtitleFor(slug: string): string {
  const category = tenantConfigFor(slug).shape.blog_subtitle_category;
  return category + ", dicas e curiosidades -- conteudo editorial da marca.";
}

/** Find a sample post by slug WITHIN a tenant's post set (PER-TENANT, PURE + TOTAL). A
 *  services tenant resolves ONLY its own tech posts -- a cat-post slug -> undefined. */
export function findBlogPostFor(slug: string, postSlug: string): SampleBlogPost | undefined {
  const p = (postSlug ?? "").trim().toLowerCase();
  return blogPostsFor(slug).find((x) => x.slug === p);
}

/** Find a sample post by slug in the DEFAULT built-in retail set (PURE + TOTAL -- undefined when
 *  absent). Retained for back-compat; prefer findBlogPostFor for the per-tenant lookup. */
export function findSampleBlogPost(slug: string): SampleBlogPost | undefined {
  const s = (slug ?? "").trim().toLowerCase();
  return SAMPLE_BLOG_POSTS.find((p) => p.slug === s);
}

// --- SAMPLE B2B (amostra) ----------------------------------------------------
//
// The wholesale B2B sample blocks below are SHARED (not per-tenant): the B2BView renders
// them when the resolved b2b content is ``mode: "wholesale"`` (the built-in retail default).

/** One B2B value/benefit block. */
export interface B2BBenefit {
  title: string;
  body: string;
}

/** One B2B partner tier (sample -- never a binding commercial offer). */
export interface B2BTier {
  name: string;
  /** the qualifier line (e.g. minimum order). */
  qualifier: string;
  /** the headline benefit. */
  highlight: string;
  /** an illustrative discount band (e.g. "ate 15%") -- amostra, never a binding price. */
  discountBand: string;
  /** bullet benefits. */
  perks: string[];
  /** whether this is the recommended / featured tier. */
  featured?: boolean;
}

/** One onboarding step (how a partner joins). */
export interface B2BStep {
  step: number;
  title: string;
  body: string;
}

/** One B2B FAQ entry. */
export interface B2BFaq {
  question: string;
  answer: string;
}

/** The sample B2B value props -- generic wholesale benefits (flagged amostra in the UI). */
export const B2B_BENEFITS: readonly B2BBenefit[] = [
  {
    title: "Curadoria premium",
    body: "Um catalogo enxuto e selecionado -- produtos com giro comprovado, sem encalhe de estoque.",
  },
  {
    title: "Margem para o lojista",
    body: "Tabela de atacado pensada para o ponto de venda fisico e o e-commerce do parceiro.",
  },
  {
    title: "Suporte de marca",
    body: "Material de ponto de venda, fichas tecnicas e fotos prontas para o anuncio do parceiro.",
  },
  {
    title: "Logistica consolidada",
    body: "Frete agrupado e prazos previsiveis para o lojista parceiro -- menos custo por pedido.",
  },
  {
    title: "Catalogo sempre atualizado",
    body: "Fichas, fotos e precos de atacado num so lugar -- o parceiro anuncia sem retrabalho.",
  },
  {
    title: "Gestao no painel da marca",
    body: "O cadastro, os pedidos e as condicoes vivem no painel -- esta vitrine apenas apresenta o programa.",
  },
];

/** The sample B2B tiers -- ILLUSTRATIVE only (no checkout, no binding price). */
export const B2B_TIERS: readonly B2BTier[] = [
  {
    name: "Revenda",
    qualifier: "Pedido inicial a partir de 10 pecas",
    highlight: "Entrada no programa de parceiros",
    discountBand: "ate 12%",
    perks: ["Tabela de atacado", "Fichas tecnicas", "Frete consolidado"],
  },
  {
    name: "Parceiro",
    qualifier: "Pedido recorrente mensal",
    highlight: "Condicoes ampliadas e prioridade",
    discountBand: "ate 20%",
    featured: true,
    perks: [
      "Margem ampliada",
      "Material de PDV",
      "Lancamentos antecipados",
      "Suporte dedicado",
    ],
  },
  {
    name: "Distribuidor",
    qualifier: "Volume e cobertura regional",
    highlight: "Melhores condicoes e exclusividade por area",
    discountBand: "sob consulta",
    perks: [
      "Melhor tabela de atacado",
      "Exclusividade regional",
      "Co-marketing com a marca",
      "Gestor de conta",
    ],
  },
];

/** The illustrative pricing BANDS table (amostra -- never a binding price). */
export const B2B_PRICING_BANDS: readonly { volume: string; band: string; note: string }[] = [
  { volume: "10 a 49 pecas", band: "ate 12%", note: "Entrada (Revenda)" },
  { volume: "50 a 199 pecas", band: "ate 20%", note: "Recorrente (Parceiro)" },
  { volume: "200+ pecas", band: "sob consulta", note: "Volume (Distribuidor)" },
];

/** The sample onboarding steps. */
export const B2B_STEPS: readonly B2BStep[] = [
  {
    step: 1,
    title: "Conte sobre a sua loja",
    body: "Voce envia os dados da loja (CNPJ, canais de venda e volume estimado) pelo painel da marca.",
  },
  {
    step: 2,
    title: "Receba a tabela de atacado",
    body: "A equipe da marca valida o cadastro e libera a tabela de atacado e o material de apoio.",
  },
  {
    step: 3,
    title: "Comece a vender",
    body: "Com fichas, fotos e precos em maos, o parceiro anuncia nos seus proprios canais.",
  },
];

/** The sample B2B FAQ. */
export const B2B_FAQ: readonly B2BFaq[] = [
  {
    question: "Preciso de CNPJ para ser parceiro?",
    answer:
      "O programa de atacado e voltado a lojistas com CNPJ. O cadastro e a validacao acontecem no painel da marca -- esta vitrine apenas apresenta o programa.",
  },
  {
    question: "Os descontos desta pagina sao garantidos?",
    answer:
      "Nao. As faixas exibidas aqui sao ilustrativas (amostra). As condicoes finais sao definidas no contato, conforme volume e recorrencia.",
  },
  {
    question: "Qual o pedido minimo?",
    answer:
      "Varia por nivel. A faixa de entrada (Revenda) parte de um pedido inicial; niveis superiores pedem recorrencia ou volume.",
  },
  {
    question: "Como faco o pedido?",
    answer:
      "Os pedidos sao tratados no painel e no contato da marca. Esta vitrine publica nao tem carrinho nem fechamento de pedido.",
  },
];

/** The B2B trust signals row (reuses the generic e-commerce trust language). */
export const B2B_TRUST: readonly string[] = [
  "Sem cadastro nesta vitrine",
  "Condicoes tratadas no painel da marca",
  "Material de apoio incluso",
];

// ---------------------------------------------------------------------------
// PER-TENANT B2B CONTENT -- the built-in retail WHOLESALE area is one shape; a services
// tenant's "Para Empresas" / corporate area is ANOTHER. A discriminated B2BContent lets each
// tenant render the area that fits ITS business with ITS own content.
//
//   * ``mode: "wholesale"`` -- the built-in retail vertical: tiers + atacado pricing bands +
//     onboarding + FAQ (the SHARED B2B_* blocks above -> demo-acme UNCHANGED).
//   * ``mode: "corporate"`` -- a services vertical: corporate offers + who-we-
//     serve + a WhatsApp contact CTA + partners. NO fake checkout, NO atacado/wholesale
//     language. Honest: every block is sample copy flagged amostra in the UI.
//
// The per-tenant content (ORBIT_B2B / the wholesale marker) lives in lib/tenantConfig;
// b2bContentFor derives from it. The TYPES stay here (the content's contract).
// ---------------------------------------------------------------------------

/** One corporate offer (services tenant "Para Empresas" area). */
export interface CorporateOffer {
  title: string;
  body: string;
}

/** The built-in retail wholesale B2B content (the existing content, bundled for the resolver). The
 *  view renders this when ``mode === "wholesale"``. */
export interface WholesaleB2BContent {
  mode: "wholesale";
}

/** The services "Para Empresas" corporate content. The view renders this when
 *  ``mode === "corporate"`` -- no tiers, no atacado, a WhatsApp contact CTA instead. */
export interface CorporateB2BContent {
  mode: "corporate";
  /** the hero eyebrow (e.g. "Para empresas"). */
  eyebrow: string;
  /** the hero headline (e.g. "[Brand] para Empresas"). */
  heroTitle: string;
  /** the hero subline (the value promise). */
  heroSubline: string;
  /** the corporate offers (6). */
  offers: readonly CorporateOffer[];
  /** the "who we serve" line. */
  whoWeServe: string;
  /** the CTA button label (e.g. "Falar com um especialista"). */
  ctaLabel: string;
  /** the CTA WhatsApp deep link (https only; scheme-checked at the render boundary). */
  ctaWhatsapp: string;
}

/** The full per-tenant B2B content (a discriminated union). */
export type B2BContent = WholesaleB2BContent | CorporateB2BContent;

/** Resolve the B2B content a tenant SLUG offers, DERIVED from its config. A registered tenant
 *  -> its content; any other slug -> the built-in retail wholesale content (zero-regression).
 *  TOTAL. ASCII-only. */
export function b2bContentFor(slug: string): B2BContent {
  return tenantConfigFor(slug).b2b;
}
