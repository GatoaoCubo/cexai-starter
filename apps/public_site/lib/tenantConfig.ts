// ----------------------------------------------------------------------------
// tenantConfig -- THE single declarative source-of-truth per tenant slug.
//
// THE PROBLEM this fixes: the per-tenant facts (which sections a tenant offers, its
// public kinds, its extra storefront content, its blog/b2b content, its decorative
// imagery, its fixtures brand + catalog) used to live in SIX parallel per-slug maps
// (SECTIONS_BY_SLUG, PUBLIC_KINDS_BY_SLUG, CONTENT_BY_SLUG, BLOG_*_BY_SLUG /
// B2B_CONTENT_BY_SLUG, IMAGERY_BY_SLUG, fixtures TENANTS). Adding/auditing a tenant
// meant editing six files in lockstep -- and the BUSINESS SHAPE (retail vs services,
// has-blog, b2b mode, imagery treatment) was implicit, scattered, and re-derived ad hoc.
//
// So this module collapses all of that into ONE TenantConfig per slug. Every public_site
// accessor now DERIVES from tenantConfigFor(slug): the six resolvers became thin reads of
// this config. The refactor RELOCATES the existing literals into the config -- it changes
// NO value: tenantConfigFor("demo-acme") and tenantConfigFor(<any registered slug>) reproduce
// today's EXACT values, and an unknown slug still degrades to the retail default
// (built-in-sample-shaped) exactly as before.
//
// DEPENDENCY DIRECTION (no runtime cycle): this module is the LEAF that owns the data. It
// imports only TYPES from the domain modules (erased at runtime). Every domain module
// (tenantSections / publicKinds / tenantContent / storeContent / tenantImagery / fixtures /
// brandText) imports tenantConfigFor FROM here, one-way -- so this module never imports any
// of them at runtime.
//
// BACKEND mirror: cex_business_shape emits the `shape` object below (snake_case keys, same
// names). The shape is the master discriminator the bootstrap carries.
//
// ASCII-only + diacritic-free (house style). PURE DATA + PURE FUNCTIONS -- no React.
// ----------------------------------------------------------------------------

import type { BrandTheme } from "@/lib/brandTheme";
import type { PublicCatalogItem } from "@/lib/types";
import type { PublicKind } from "@/lib/publicKinds";
import type { TenantContent } from "@/lib/tenantContent";
import type {
  SampleBlogPost,
  B2BContent,
  CorporateB2BContent,
  WholesaleB2BContent,
} from "@/lib/storeContent";

// The CLOSE-THE-LOOP bridge registry (committed default {}). A dev predev step
// (scripts/load-generated-tenants.mjs) reads `.cex/tenants/*/tenant_config.json` and writes
// the merged { slug: tenant_config } map here. This is a STATIC import on purpose: it bundles
// into BOTH the server and the CLIENT (HomeView is a client component), so a GENERATED tenant
// resolves client-side -- a server-only fs read would never reach the browser bundle. On a
// fresh checkout / in prod this is {} (zero generated tenants; prod resolves via the backend).
import generatedRaw from "@/lib/generatedTenants.json";
import { tenantData as SELF_DATA } from "@/lib/tenantData.generated";

// ============================================================================
// THE FROZEN TenantConfig CONTRACT
// ============================================================================

/** The master vertical discriminator. */
export type Vertical = "retail" | "services";
/** The B2B area flavour (null when the tenant runs no B2B area). */
export type B2BMode = "wholesale" | "corporate";
/** The decorative-imagery treatment. */
export type ImageryMode = "photos" | "brand";

/** THE business shape (the backend `cex_business_shape` detects this; keys mirror it
 *  EXACTLY in snake_case). Every public_site surface derives its on/off + labels + vertical
 *  awareness from here. */
export interface TenantShape {
  /** master discriminator: a product-retail vitrine vs a services vitrine. */
  vertical: Vertical;
  /** whether the tenant operates a product store (detected independently of vertical --
   *  a services tenant CAN have one, e.g. its own online Loja). */
  has_store: boolean;
  /** whether the tenant runs a content blog. */
  has_blog: boolean;
  /** whether the tenant runs a B2B / corporate area. */
  has_b2b: boolean;
  /** the B2B flavour: retail wholesale vs services corporate; null when has_b2b is false. */
  b2b_mode: B2BMode | null;
  /** the nav/page label for the b2b area ("B2B" retail/wholesale; "Para Empresas" services). */
  b2b_label: string;
  /** the decorative imagery treatment (first-party photos vs a brand-gradient). */
  imagery_mode: ImageryMode;
  /** the curated public catalog kinds the landing page links to. */
  public_kinds: readonly PublicKind[];
  /** the leading blog-subtitle category word (per-tenant -- "Bem-estar" retail, "Seguranca"
   *  for a security-led services tenant). "" when has_blog is false. */
  blog_subtitle_category: string;
}

/** The decorative photo paths for a photo-shipping tenant (same-origin /images/...). */
export interface TenantImageryPaths {
  /** full-bleed hero backdrop photo. */
  hero: string;
  /** the editorial "A marca" band photo. */
  section: string;
  /** the catalog-card decorative fallback tile. */
  cardFallback: string;
}

/** The tenant's blog content (curated sample editorial -- flagged amostra in the UI). */
export interface TenantBlogConfig {
  /** the blog category filter chips. */
  categories: readonly string[];
  /** the sample blog posts. */
  posts: readonly SampleBlogPost[];
}

/** THE tenant's external web + social presence -- an OPTIONAL block on the contract. It is
 *  BOTH an INPUT (from the bootstrap spec / form, or auto-detected by ingest) and an OUTPUT
 *  (the site footer presence row + the nav "Loja"/site derivation). ALL fields optional --
 *  only the links that EXIST render (honest-empty; never fabricate a URL). Every value is
 *  sanitized at the render boundary (isSafeHref: absolute https: only) before it becomes an
 *  href on this UNAUTHENTICATED public surface. Keys mirror the backend
 *  cex_brand_extract materials["links"] / cex_business_shape / cex_tenant_bootstrap. */
export interface TenantLinks {
  /** the canonical tenant website. */
  website?: string;
  /** the online store / loja URL (also the source the nav "Loja" link DERIVES from). */
  store?: string;
  /** Instagram profile URL. */
  instagram?: string;
  /** LinkedIn company/profile URL. */
  linkedin?: string;
  /** Facebook page URL. */
  facebook?: string;
  /** YouTube channel URL. */
  youtube?: string;
  /** WhatsApp deep link. MAY already live in content.contact.whatsapp -- the presence row
   *  RECONCILES (it never renders a duplicate WhatsApp control when contact.whatsapp exists). */
  whatsapp?: string;
  /** X / Twitter profile URL (optional). */
  x?: string;
  /** TikTok profile URL (optional). */
  tiktok?: string;
}

/** THE single declarative source-of-truth per tenant slug. ALL public_site surfaces derive
 *  from tenantConfigFor(slug); no parallel per-slug maps survive. */
export interface TenantConfig {
  /** the public slug (the archetype slug for the retail default). */
  slug: string;
  /** the tenant's public brand -- maps 1:1 to BrandTheme. */
  brand: BrandTheme;
  /** the business shape (the backend mirror + vertical awareness live here). */
  shape: TenantShape;
  /** the extra storefront content (partners / about / social proof / contact); null when
   *  the tenant ships none (the home renders without those sections). */
  content: TenantContent | null;
  /** the decorative photo paths; null when imagery_mode is "brand" (the gradient treatment). */
  imagery: TenantImageryPaths | null;
  /** the blog content (categories + posts). */
  blog: TenantBlogConfig;
  /** the B2B area content (a discriminated union -- wholesale vs corporate). */
  b2b: B2BContent;
  /** the published catalog, keyed by kind (the fixtures rows). */
  catalog: Record<string, PublicCatalogItem[]>;
  /** the tenant's external web + social presence (OPTIONAL). Absent -> no footer presence
   *  row + no nav "Loja" (honest-empty). Each URL is sanitized at the render boundary
   *  (isSafeHref: absolute https: only). */
  links?: TenantLinks;
}

// ============================================================================
// IDENTITY CANON (P0-A rebrand, 2026-07-10) -- fictitious demo tenants ONLY.
//
// Both seeded tenants below are 100% fictitious. Format-valid-but-fake contact data
// only; no real CNPJ / phone / address / third-party person or company identity may
// ever be reintroduced here. Keep BOTH apps + every test aligned to this ONE canon:
//
//   demo-acme  (retail)   -- "Acme Pet Shop (amostra)". Keeps the pet/cat vertical
//                            role (first-party cat photos are generic product shots,
//                            not PII). Fake CNPJ shape 00.000.000/0001-91; fake phone
//                            shape (11) 0000-0000.
//   demo-orbit (services) -- "Orbit Tech" (replaces the former real-tenant IT-services
//                            brand references). Keeps the SERVICES vertical role
//                            (admin accent, service catalog, corporate B2B). Same
//                            fake-contact convention; fictitious testimonial authors;
//                            de-identified address/region.
//
// Namespaced kinds (dashboard_web lib/fixtures.ts + lib/molds.ts, tenant-namespaced
// overlay kinds): demo_acme_crm, demo_acme_sales_assistant.
// ============================================================================

// ============================================================================
// TENANT SLUGS (the registered white-label tenants)
// ============================================================================

/** The ONE original sample slug (the built-in product-retail vertical, fictitious
 *  "Acme Pet Shop"). The name flags it as a sample; any slug NOT registered resolves
 *  to the retail default (and, in fixtures, null). */
export const SAMPLE_SLUG = "demo-acme";

/** The SECOND fixtures tenant -- a totally different vertical (IT services, fictitious
 *  "Orbit Tech") proving the storefront generalizes from the SAME code (the
 *  white-label flywheel proof). */
export const ORBIT_SLUG = "demo-orbit";

// ============================================================================
// BRANDS (maps 1:1 to BrandTheme -- the 24 moldgen tokens + visual fields)
// ============================================================================

// The SAMPLE brand is a FULLY SYNTHETIC retail palette (refined PB-minimal: white base,
// near-black foreground, violet brand, amber highlight) -- deliberately NOT any real tenant's
// identity (S5 confidentiality fix: this fixture ships to EVERY distilled tenant unconditionally
// -- see RETAIL_DEFAULT_CONFIG below -- so it must never carry a live brand's real name, logo, or
// production color tokens). Swap these 24 values and the WHOLE site re-skins (the mold proof).
const SAMPLE_BRAND: BrandTheme = {
  name: "Acme Pet Shop (amostra)",
  tagline: "Produtos premium para gatos -- catalogo de demonstracao",
  logoAlt: "Acme Pet Shop (amostra)",
  // a SAFE data:image logo (https:/data:image only -- isSafeLogoSrc) so the hero +
  // header + about logo paths render in fixtures mode. PB-minimal: a generic abstract mark
  // (a rounded square + dot) -- deliberately NOT any real brand's wordmark or glyph.
  logo:
    "data:image/svg+xml;utf8," +
    encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" width="132" height="40">' +
        '<rect x="4" y="8" width="24" height="24" rx="6" fill="#4c3b9e"/>' +
        '<circle cx="16" cy="20" r="6" fill="#ffffff"/>' +
        '<text x="36" y="27" fill="#0a0a0a" font-family="Inter,system-ui,sans-serif" ' +
        'font-size="15" font-weight="800" letter-spacing="-0.5">Acme</text></svg>',
    ),
  // The 24 BRAND-VARIABLE tokens -- a SYNTHETIC placeholder palette (violet/amber), not any
  // real tenant's production design_system.md values.
  tokens: {
    background: "0 0% 100%",
    foreground: "0 0% 4%",
    card: "0 0% 100%",
    cardForeground: "0 0% 4%",
    popover: "0 0% 100%",
    popoverForeground: "0 0% 4%",
    primary: "0 0% 7%",
    primaryForeground: "0 0% 100%",
    secondary: "0 0% 96%",
    secondaryForeground: "0 0% 7%",
    muted: "0 0% 96%",
    mutedForeground: "0 0% 38%",
    accent: "0 0% 7%",
    accentForeground: "0 0% 100%",
    border: "0 0% 90%",
    input: "0 0% 90%",
    ring: "0 0% 4%",
    brand: "258 60% 45%",
    brandForeground: "0 0% 100%",
    brandMuted: "258 45% 95%",
    highlight: "35 90% 45%",
    highlightForeground: "0 0% 100%",
    highlightMuted: "38 100% 96%",
    radius: "0.75rem",
  },
  fontFamily: "Inter, -apple-system, Segoe UI, sans-serif",
};

/** Orbit Tech's brand -- BLUE primary + RED highlight, neutral greys, a tech radius. The 24
 *  tokens are the reskin: swap these and the WHOLE site repaints in Orbit Tech's identity.
 *  ``logo`` is the committed same-origin PNG (isSafeLogoSrc now permits a root-relative
 *  /path -- a first-party asset on our own origin). */
const ORBIT_BRAND: BrandTheme = {
  name: "Orbit Tech",
  tagline: "Solucoes em Tecnologia",
  logoAlt: "Orbit Tech",
  logo: "/images/tenants/demo-orbit/logo.png",
  tokens: {
    background: "0 0% 100%",
    foreground: "0 0% 13%",
    card: "0 0% 100%",
    cardForeground: "0 0% 13%",
    popover: "0 0% 100%",
    popoverForeground: "0 0% 13%",
    primary: "231 48% 48%",
    primaryForeground: "0 0% 100%",
    secondary: "210 16% 96%",
    secondaryForeground: "231 48% 48%",
    muted: "210 16% 96%",
    mutedForeground: "215 16% 47%",
    accent: "231 48% 48%",
    accentForeground: "0 0% 100%",
    border: "0 0% 90%",
    input: "0 0% 90%",
    ring: "231 48% 48%",
    brand: "231 48% 48%",
    brandForeground: "0 0% 100%",
    brandMuted: "231 48% 96%",
    highlight: "4 90% 58%",
    highlightForeground: "0 0% 100%",
    highlightMuted: "4 90% 96%",
    radius: "0.625rem",
  },
  fontFamily: "Inter, -apple-system, Segoe UI, sans-serif",
};

// ============================================================================
// CATALOGS (the fixtures published rows, per kind) -- honestly flagged real: false
// ============================================================================

/** Build a tiny inline SVG as a SAFE data:image URI (a sample swatch). PURE + ASCII. */
function sampleSvg(label: string, bg: string, fg: string): string {
  return (
    "data:image/svg+xml;utf8," +
    encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360">' +
        '<rect width="480" height="360" fill="' + bg + '"/>' +
        '<text x="240" y="190" fill="' + fg + '" font-family="monospace" font-size="20" ' +
        'text-anchor="middle">' + label + "</text>" +
        "</svg>",
    )
  );
}

const SAMPLE_MARKETPLACE_LISTINGS: PublicCatalogItem[] = [
  {
    id: "ml_sample_0001",
    kind: "marketplace_listing",
    published_at: "2026-06-20T12:00:00Z",
    real: false,
    title: "Arranhador Torre para Gatos 1,2m (amostra)",
    price: "R$ 199,00",
    summary:
      "Amostra de anuncio publicado -- base reforcada antiderrapante, sisal substituivel. Dados simulados.",
    description:
      "Arranhador torre de 1,2 m com base reforcada antiderrapante e poste de sisal " +
      "substituivel. Estrutura em MDF revestido. Amostra publicada -- dados simulados, " +
      "nao representa um produto real a venda.",
    // a multi-image GALLERY (SAFE data:image URIs) so the PDP exercises the gallery.
    images: [
      sampleSvg("amostra frente", "#f4f4f5", "#0a0a0a"),
      sampleSvg("amostra lateral", "#e8f4f2", "#1d6b62"),
      sampleSvg("amostra base", "#f4f4f5", "#0a0a0a"),
    ],
    // a SPECS object (scalar values) so the PDP renders the attributes block.
    specs: {
      Altura: "1,2 m",
      Material: "Sisal substituivel + MDF reforcado",
      "Peso suportado": "ate 8 kg",
      Cor: "Bege",
      Montagem: "5 minutos",
    },
    // a typed sections body the public structured renderer can show.
    sections: [
      {
        title: "Ficha",
        layout: "fields",
        rows: [
          { label: "Altura", value: "1,2 m" },
          { label: "Material", value: "Sisal substituivel + base MDF reforcada" },
          { label: "Peso suportado", value: "ate 8 kg" },
        ],
      },
      {
        title: "Destaques",
        layout: "list",
        items: ["Base antiderrapante", "Sisal trocavel", "Montagem em 5 min"],
      },
    ],
    // a dual_output asset (flat emitter shape) with ONE generated image slot
    // (a safe data: URI sample) so the detail page exercises the media renderer.
    dual_output: {
      id: "ml_sample_0001",
      capability: "marketplace_listing",
      real: false,
      machine_md:
        "---\nid: ml_sample_0001\ncapability: marketplace_listing\nreal: false\n---\n\n# Arranhador Torre (amostra)\n\nAmostra de face maquina -- dados simulados.",
      media_slots: [
        {
          key: "hero",
          kind: "image",
          status: "generated",
          // a tiny inline SVG data: URI -- a SAFE sample media src (data:image/...).
          src:
            "data:image/svg+xml;utf8," +
            encodeURIComponent(
              '<svg xmlns="http://www.w3.org/2000/svg" width="320" height="200">' +
                '<rect width="320" height="200" fill="#0E141C"/>' +
                '<text x="160" y="105" fill="#5EEAD4" font-family="monospace" font-size="16" text-anchor="middle">amostra hero</text>' +
                "</svg>",
            ),
          alt: "Imagem de amostra do arranhador",
          editable: true,
          uploadFallback: true,
        },
      ],
      frontmatter: { id: "ml_sample_0001", capability: "marketplace_listing", real: false },
    },
  },
  {
    id: "ml_sample_0002",
    kind: "marketplace_listing",
    published_at: "2026-06-19T09:30:00Z",
    real: false,
    title: "Comedouro Antiformiga (amostra)",
    price: "R$ 49,00",
    summary: "Amostra de segundo anuncio publicado -- dados simulados.",
    image: sampleSvg("comedouro", "#e8f4f2", "#1d6b62"),
  },
  {
    id: "ml_sample_0003",
    kind: "marketplace_listing",
    published_at: "2026-06-17T11:15:00Z",
    real: false,
    title: "Tapete Gelado para Gatos (amostra)",
    price: "R$ 129,00",
    summary:
      "Amostra de terceiro anuncio publicado -- alivio termico no verao. Dados simulados.",
    image: sampleSvg("tapete gelado", "#f4f4f5", "#0a0a0a"),
    specs: {
      Tamanho: "50 x 40 cm",
      Material: "Gel atoxico",
      Limpeza: "Pano umido",
    },
  },
  {
    // A sample listing that EXERCISES the optional rating + reviews + sticky-CTA paths:
    // it carries a rating, a review count, a verified flag, a reviews_list, a SAFE
    // https buy_url, AND a 2-image gallery (for the card hover-swap). Honestly flagged.
    id: "ml_sample_0004",
    kind: "marketplace_listing",
    published_at: "2026-06-16T08:00:00Z",
    real: false,
    title: "Fonte de Agua para Gatos (amostra)",
    price: "R$ 159,00",
    summary:
      "Amostra com avaliacoes publicadas -- fonte com filtro. Dados simulados.",
    description:
      "Fonte de agua de 2 L com filtro de carvao e bomba silenciosa. Amostra publicada " +
      "-- dados simulados, nao representa um produto real a venda.",
    images: [
      sampleSvg("amostra fonte", "#f4f4f5", "#0a0a0a"),
      sampleSvg("amostra fonte 2", "#e8f4f2", "#1d6b62"),
    ],
    // an external https buy URL -> exercises the buy CTA + the mobile sticky bar.
    buy_url: "https://example.com/amostra/fonte-de-agua",
    // a HONEST rating + count + verified flag (only here -> the other items render nothing).
    rating: 4.7,
    review_count: 128,
    verified: true,
    reviews_list: [
      { author: "Cliente A (amostra)", rating: 5, body: "Meu gato adorou. Amostra." },
      { author: "Cliente B (amostra)", rating: 4, body: "Silenciosa. Dados simulados." },
    ],
  },
];

const SAMPLE_PRODUCT_ADS: PublicCatalogItem[] = [
  {
    id: "ad_sample_0001",
    kind: "product_ad",
    published_at: "2026-06-18T15:45:00Z",
    real: false,
    title: "Anuncio: Torre que aguenta gato de 8kg (amostra)",
    summary: "Amostra de anuncio brand-voice publicado -- dados simulados.",
    sections: [
      {
        title: "Variantes",
        layout: "table",
        columns: ["Plataforma", "Hook", "CTA"],
        table: [
          ["Meta Feed", "Seu gato arranha tudo?", "Comprar agora"],
          ["Google", "Arranhador Torre 1,2m", "Ver oferta"],
        ],
      },
    ],
    // a human_html export string (a real document) so the detail page exercises the
    // SANDBOXED iframe path. It is tenant-authored -> rendered ONLY in a sandboxed
    // iframe (no allow-scripts), never injected into the live DOM.
    human_html:
      '<!doctype html><html lang="pt-br"><head><meta charset="utf-8"><title>Anuncio amostra</title></head>' +
      "<body><h1>Anuncio (amostra)</h1><p>Esta e a face humana exportada de um anuncio publicado de amostra. " +
      "Dados simulados.</p><p>Hook: <strong>Seu gato arranha tudo?</strong></p></body></html>",
  },
];

/** The built-in sample catalog, keyed by kind. A kind absent here -> an empty catalog (the
 *  branded empty shell), exactly like a live tenant with no rows of that kind. */
const SAMPLE_CATALOG: Record<string, PublicCatalogItem[]> = {
  marketplace_listing: SAMPLE_MARKETPLACE_LISTINGS,
  product_ad: SAMPLE_PRODUCT_ADS,
};

/** One services-vertical SERVICE -> a catalog item of kind "service". NO price, NO buy_url. The
 *  ``icon`` field drives the service-card glyph (mapped to an inline SVG by the renderer);
 *  the WhatsApp/contact CTA lives in the view (not a per-item field). Honestly real: false
 *  (a demo render of the brand's public services). */
function orbitService(
  n: string,
  title: string,
  summary: string,
  icon: string,
): PublicCatalogItem {
  return {
    id: "svc_orbit_" + n,
    kind: "service",
    published_at: "2026-06-24T12:00:00Z",
    real: false,
    title,
    summary,
    icon,
  };
}

const ORBIT_SERVICES: PublicCatalogItem[] = [
  orbitService(
    "0001",
    "Manutencao de Micro",
    "Diagnostico, limpeza, troca de pecas e otimizacao do seu computador de mesa.",
    "wrench",
  ),
  orbitService(
    "0002",
    "Atendimento Remoto",
    "Suporte rapido a distancia para resolver problemas sem sair de casa ou da empresa.",
    "remote",
  ),
  orbitService(
    "0003",
    "Reparo de Notebooks",
    "Troca de tela, teclado, bateria e reparo de placa para notebooks de todas as marcas.",
    "laptop",
  ),
  orbitService(
    "0004",
    "Cloud Backup",
    "Backup automatico na nuvem para proteger seus dados contra perdas e ransomware.",
    "cloud",
  ),
  orbitService(
    "0005",
    "Infraestrutura de Rede",
    "Projeto e instalacao de redes cabeadas e wireless para residencias e empresas.",
    "network",
  ),
  orbitService(
    "0006",
    "Impressoes 3D",
    "Prototipagem e impressao 3D sob demanda para pecas, projetos e brindes.",
    "cube",
  ),
  orbitService(
    "0007",
    "Licencas Microsoft",
    "Windows e Office originais com licenciamento correto e suporte na ativacao.",
    "shield",
  ),
  orbitService(
    "0008",
    "Recuperacao de Dados",
    "Recuperacao de arquivos de HDs, SSDs e cartoes danificados ou formatados.",
    "database",
  ),
  orbitService(
    "0009",
    "Montagem de Micro Gamer",
    "Montagem personalizada de PCs gamer com selecao de pecas para o seu orcamento.",
    "gamepad",
  ),
];

/** Orbit Tech's catalog, keyed by kind. Only the "service" kind has rows. */
const ORBIT_CATALOG: Record<string, PublicCatalogItem[]> = {
  service: ORBIT_SERVICES,
};

// ============================================================================
// PUBLIC KINDS (the curated catalog kinds the landing page links to)
// ============================================================================

/** The curated public catalog kinds -- the DEFAULT set (the built-in product-retail vertical).
 *  There is no list-kinds endpoint; this is the documented source of truth. */
export const PUBLIC_KINDS: readonly PublicKind[] = [
  {
    kind: "marketplace_listing",
    label: "Catalogo",
    blurb: "Anuncios de produtos publicados.",
  },
  {
    kind: "product_ad",
    label: "Anuncios",
    blurb: "Pecas de anuncio publicadas.",
  },
] as const;

/** Orbit Tech's public kinds: a single SERVICE kind with its own label (NOT the retail
 *  Catalogo/Anuncios). The labels/blurbs are STATIC build-time constants (never
 *  tenant-controlled), so the nav stays injection-free. */
const ORBIT_KINDS: readonly PublicKind[] = [
  {
    kind: "service",
    label: "Servicos",
    blurb: "Servicos de tecnologia e assistencia tecnica.",
  },
] as const;

// ============================================================================
// EXTRA STOREFRONT CONTENT (partners / about / social proof / testimonials / contact)
// ============================================================================

// The services-vertical fixture -- a FICTITIOUS IT-SERVICES brand rendered as a storefront
// demo (P0-A rebrand: no real company, no real contact data, no real testimonial authors).
// NOTE (S5 confidentiality fix): unlike the const declarations below (stripped for every OTHER
// tenant by the apps-collapse codemod, since it only removes VariableStatement nodes), this
// header COMMENT is a standalone line the codemod's AST walk does not capture as the
// declaration's leading trivia -- so it survives into every distilled tenant's tree regardless
// of self/foreign. It must therefore stay tenant-agnostic prose (no real domain/brand literal).
// Diacritic-free ASCII per house style ("Solucoes" not the accented form).
const ORBIT_CONTENT: TenantContent = {
  heroSubline:
    "Especialistas em tecnologia -- confiabilidade comeca conosco.",
  ctaLabel: "Fale no WhatsApp",
  partners: [
    { src: "/images/tenants/demo-orbit/partner-microsoft.png", alt: "Microsoft" },
    { src: "/images/tenants/demo-orbit/partner-bitdefender.png", alt: "BitDefender" },
    { src: "/images/tenants/demo-orbit/partner-intelbras.png", alt: "Intelbras" },
  ],
  aboutStats: [
    { value: "+20 anos", label: "no mercado" },
    { value: "+10 mil", label: "atendimentos" },
    { value: "Tecnicos", label: "especializados" },
    { value: "Grande SP", label: "atendimento regional" },
  ],
  aboutBody:
    "Ha mais de 20 anos a Orbit Tech atende empresas e pessoas na Grande Sao Paulo " +
    "com assistencia tecnica, infraestrutura e solucoes em tecnologia. Mais de 10 mil " +
    "atendimentos realizados por uma equipe de tecnicos especializados.",
  socialProof: { rating: 4.6, count: 68, source: "Google" },
  testimonials: [
    {
      author: "Fernanda Rocha (amostra)",
      body:
        "Cliente da Orbit Tech ha 18 anos -- precos imbativeis, pagamento facilitado, " +
        "atendimento humanizado.",
      sample: true,
    },
    {
      author: "Roberto Alves (amostra)",
      body: "Muito bom. A competencia impera nesse local.",
      sample: true,
    },
    {
      author: "Juliana Prado (amostra)",
      body: "Atendimento excelente, profissionais excelentes.",
      sample: true,
    },
  ],
  contact: {
    phone: "(11) 0000-0000",
    email: "contato@orbittech.com.br",
    address: "Av. Central 1000, Sao Paulo, SP",
    whatsapp: "https://api.whatsapp.com/send?phone=551100000000",
    instagram: "orbittech_solucoes",
    store: "https://www.loja.orbittech.com.br",
  },
};

// ============================================================================
// BLOG (sample editorial -- ALL flagged amostra in the UI)
// ============================================================================

/** The built-in retail blog category filter chips. */
const BLOG_CATEGORIES: readonly string[] = [
  "Bem-estar",
  "Dicas",
  "Saude",
  "Curiosidades",
] as const;

/** The built-in retail sample blog posts. */
const SAMPLE_BLOG_POSTS: readonly SampleBlogPost[] = [
  {
    slug: "ambiente-felino-enriquecido",
    category: "Bem-estar",
    title: "Como montar um ambiente enriquecido para o seu gato",
    excerpt:
      "Verticalidade, arranhadores e esconderijos: os tres pilares de um lar que respeita o instinto felino.",
    readTime: "5 min",
    date: "2026-06-18",
    cover: "cat-section",
    featured: true,
    body: [
      "Este e um artigo de AMOSTRA (dados simulados) que demonstra o layout editorial do blog. O conteudo abaixo e ilustrativo e nao substitui orientacao veterinaria.",
      "Gatos sao territoriais e exploram o espaco em tres dimensoes. Oferecer prateleiras, nichos e arranhadores altos transforma uma sala comum em um territorio rico para o animal.",
      "A regra pratica: para cada gato da casa, garanta ao menos um ponto alto, um esconderijo fechado e uma superficie de arranhar vertical e estavel.",
      "Rotina e consistencia importam mais do que novidades caras. Um ambiente previsivel reduz o estresse e o comportamento destrutivo.",
    ],
  },
  {
    slug: "escolher-arranhador-certo",
    category: "Dicas",
    title: "O arranhador certo para o tamanho e o peso do seu gato",
    excerpt:
      "Altura, base e material fazem toda a diferenca. Um guia rapido para nao errar na escolha.",
    readTime: "4 min",
    date: "2026-06-12",
    cover: "cat-blog-1",
    featured: true,
    body: [
      "Artigo de AMOSTRA -- dados simulados, apenas para demonstrar o post individual do blog.",
      "Um bom arranhador precisa ser mais alto que o gato esticado e ter uma base larga e pesada o suficiente para nao tombar durante o uso.",
      "O sisal natural costuma ser o material preferido pela maioria dos gatos; modelos com poste substituivel prolongam a vida util do produto.",
    ],
  },
  {
    slug: "sinais-de-estresse-felino",
    category: "Saude",
    title: "Cinco sinais sutis de estresse que muitos tutores ignoram",
    excerpt:
      "Da higiene excessiva ao apetite irregular -- aprenda a ler os recados silenciosos do seu gato.",
    readTime: "6 min",
    date: "2026-06-05",
    cover: "cat-blog-2",
    body: [
      "Artigo de AMOSTRA (dados simulados). Em caso de mudanca de comportamento, consulte sempre um medico-veterinario.",
      "Mudancas na rotina de sono, na frequencia ao banheiro ou no apetite costumam ser os primeiros indicadores de que algo no ambiente incomoda o animal.",
      "Observar e registrar padroes ajuda o veterinario a chegar mais rapido a uma causa.",
    ],
  },
  {
    slug: "rotina-de-alimentacao-saudavel",
    category: "Saude",
    title: "Rotina de alimentacao: porcoes, horarios e hidratacao",
    excerpt:
      "Pequenos ajustes na rotina alimentar fazem diferenca no peso, na pelagem e na disposicao do animal.",
    readTime: "5 min",
    date: "2026-05-28",
    cover: "cat-blog-3",
    body: [
      "Artigo de AMOSTRA (dados simulados), apenas para demonstrar mais um post no grid editorial.",
      "Porcoes fracionadas ao longo do dia tendem a respeitar melhor o habito felino de comer pouco e muitas vezes do que uma unica refeicao volumosa.",
      "Fontes de agua corrente e multiplos pontos de hidratacao incentivam o consumo de liquido, um fator de protecao para a saude renal.",
    ],
  },
  {
    slug: "curiosidades-sobre-o-ronronar",
    category: "Curiosidades",
    title: "Por que os gatos ronronam (e nem sempre e por felicidade)",
    excerpt:
      "O ronronar e um sinal complexo: conforto, autocura e ate pedido de atencao podem estar por tras dele.",
    readTime: "3 min",
    date: "2026-05-20",
    cover: "cat-product",
    body: [
      "Artigo de AMOSTRA -- dados simulados, demonstrando a categoria Curiosidades.",
      "O ronronar aparece em contextos de conforto, mas tambem em situacoes de estresse ou dor, funcionando como um mecanismo de autoconforto.",
      "A frequencia do ronronar fica numa faixa associada, em estudos, a processos de regeneracao -- mais um motivo para observar o contexto, nao so o som.",
    ],
  },
  {
    slug: "tendencias-pet-premium-2026",
    category: "Dicas",
    title: "Tendencias do mercado pet premium para 2026",
    excerpt:
      "Personalizacao, bem-estar e sustentabilidade moldam o que tutores exigentes vao buscar no proximo ano.",
    readTime: "7 min",
    date: "2026-05-12",
    cover: "cat-hero",
    body: [
      "Artigo de AMOSTRA (dados simulados), para demonstrar um post mais longo no blog.",
      "A demanda por produtos premium cresce junto com a humanizacao do animal: tutores buscam itens duraveis, seguros e com design para a casa.",
      "Sustentabilidade e rastreabilidade da origem passam a ser criterios de compra, e nao apenas um diferencial de marketing.",
    ],
  },
];

/** The Orbit Tech blog category chips (tech editorial -- the services vertical's own topics). */
const ORBIT_BLOG_CATEGORIES: readonly string[] = [
  "Seguranca",
  "Cloud",
  "Manutencao",
  "Redes",
  "Licenciamento",
] as const;

/** The Orbit Tech sample tech blog posts -- ALL flagged amostra in the UI. Tenant-derived: a
 *  brand-mode tenant ships no photos, so each post OMITS cover (the view paints a brand
 *  gradient). No retail/photo content leaks in. */
const ORBIT_BLOG_POSTS: readonly SampleBlogPost[] = [
  {
    slug: "ransomware-5-habitos-que-protegem-o-seu-pc",
    category: "Seguranca",
    title: "Ransomware: 5 habitos que protegem o seu PC",
    excerpt:
      "Backup, atualizacao, antivirus, senhas fortes e desconfiar de anexos -- os cinco habitos que reduzem o risco de um sequestro de dados.",
    readTime: "5 min",
    date: "2026-06-20",
    featured: true,
    body: [
      "Artigo de AMOSTRA (dados simulados) que demonstra o layout editorial do blog tecnico da Orbit Tech. O conteudo abaixo e ilustrativo e nao substitui uma avaliacao tecnica do seu ambiente.",
      "1) Backup regular e testado: a unica defesa que realmente recupera os dados depois de um ataque e uma copia que voce sabe que funciona. Automatize e valide a restauracao periodicamente.",
      "2) Atualizacao em dia: sistema operacional, navegador e aplicativos corrigem falhas exploradas por ransomware. Atualizar nao e opcional, e a primeira barreira.",
      "3) Antivirus ativo e atualizado: uma protecao de endpoint reconhecida (parceiro oficial BitDefender) bloqueia a maioria das ameacas antes que executem.",
      "4) Senhas fortes e unicas: reuso de senha transforma um vazamento em invasao geral. Use um gerenciador e ative a verificacao em duas etapas.",
      "5) Desconfiar de anexos e links: a porta de entrada mais comum ainda e o e-mail. Na duvida, nao abra -- confirme com quem enviou por outro canal.",
    ],
  },
  {
    slug: "backup-em-nuvem-por-que-depender-de-um-hd-so-e-arriscado",
    category: "Cloud",
    title: "Backup em nuvem: por que depender de um HD so e arriscado",
    excerpt:
      "A regra 3-2-1, automacao e um teste de recuperacao confiavel -- por que um unico disco nunca deveria ser o seu unico backup.",
    readTime: "4 min",
    date: "2026-06-14",
    featured: true,
    body: [
      "Artigo de AMOSTRA -- dados simulados, apenas para demonstrar o post individual do blog tecnico.",
      "A regra 3-2-1: mantenha 3 copias dos dados, em 2 midias diferentes, com 1 copia fora do local. Um HD externo na mesma mesa atende zero dessas condicoes.",
      "Automacao importa: um backup que depende de alguem lembrar de copiar arquivos vai falhar justamente no dia em que for preciso. A nuvem agenda e executa sozinha.",
      "Recuperacao testada: backup que nunca foi restaurado e so uma esperanca. Um teste periodico de recuperacao confirma que os dados voltam mesmo.",
    ],
  },
  {
    slug: "notebook-lento-vale-a-pena-reparar-ou-trocar",
    category: "Manutencao",
    title: "Notebook lento: vale a pena reparar ou trocar?",
    excerpt:
      "Diagnostico antes de decidir: muitas vezes um SSD resolve. Quando o reparo compensa e quando a troca e o melhor custo x beneficio.",
    readTime: "5 min",
    date: "2026-06-07",
    body: [
      "Artigo de AMOSTRA (dados simulados). Em caso de lentidao, um diagnostico tecnico identifica a causa real antes de qualquer gasto.",
      "Diagnostico primeiro: lentidao raramente significa que o aparelho acabou. Disco mecanico saturado, pouca memoria ou superaquecimento por poeira sao causas comuns e baratas de resolver.",
      "A troca do disco por um SSD costuma ser a melhoria de maior impacto por menor custo -- a maquina volta a responder como nova.",
      "Custo x beneficio: quando o reparo passa de uma fracao razoavel do valor de um aparelho novo, ou quando a plataforma ja nao recebe atualizacoes, a troca compensa. O tecnico aponta o ponto de virada.",
    ],
  },
  {
    slug: "wi-fi-que-aguenta-o-escritorio-o-basico-de-uma-rede-corporativa",
    category: "Redes",
    title: "Wi-Fi que aguenta o escritorio: o basico de uma rede corporativa",
    excerpt:
      "Cabeamento bem feito, cobertura sem pontos cegos e seguranca de rede -- os fundamentos de uma rede que nao trava no horario de pico.",
    readTime: "6 min",
    date: "2026-05-30",
    body: [
      "Artigo de AMOSTRA -- dados simulados, demonstrando a categoria Redes.",
      "Cabeamento estruturado: pontos de acesso bem distribuidos e ligados por cabo entregam estabilidade que um roteador domestico sozinho nunca alcanca em um escritorio.",
      "Cobertura sem pontos cegos: um levantamento simples mapeia onde o sinal cai. Equipamentos profissionais (parceiro oficial Intelbras) cobrem o ambiente sem zonas mortas.",
      "Seguranca de rede: rede de visitantes separada da rede interna, senhas fortes e firmware atualizado evitam que um convidado vire um risco para a operacao.",
    ],
  },
  {
    slug: "licenca-microsoft-original-o-que-muda-na-pratica",
    category: "Licenciamento",
    title: "Licenca Microsoft original: o que muda na pratica",
    excerpt:
      "Suporte, atualizacoes de seguranca e conformidade -- o que a empresa ganha (e o risco que evita) ao usar licenca original.",
    readTime: "4 min",
    date: "2026-05-22",
    body: [
      "Artigo de AMOSTRA (dados simulados), apenas para demonstrar mais um post no grid editorial.",
      "Suporte e atualizacoes: licenca original recebe correcoes de seguranca e suporte oficial. Software pirata fica sem patches -- e cada falha sem correcao e uma porta aberta.",
      "Conformidade: para empresas, usar software irregular e risco juridico e de imagem. A licenca em ordem e parte da governanca, nao um detalhe.",
      "Como parceiro oficial Microsoft, a Orbit Tech orienta o licenciamento certo para o tamanho da operacao -- sem pagar a mais por algo que a empresa nao usa.",
    ],
  },
];

// ============================================================================
// B2B CONTENT (a discriminated union -- wholesale vs corporate)
// ============================================================================

/** The default built-in retail wholesale B2B content marker (the view renders the wholesale tiers/
 *  pricing/onboarding/FAQ from the shared B2B_* constants in storeContent). */
const DEFAULT_B2B_CONTENT: WholesaleB2BContent = { mode: "wholesale" };

/** The Orbit Tech "Para Empresas" corporate content (sample copy, flagged amostra). */
const ORBIT_B2B: CorporateB2BContent = {
  mode: "corporate",
  eyebrow: "Para empresas",
  heroTitle: "Orbit Tech para Empresas",
  heroSubline:
    "TI que nao para -- suporte, infraestrutura e seguranca para a sua operacao.",
  offers: [
    {
      title: "Contrato de manutencao mensal",
      body: "Manutencao preventiva e corretiva com previsibilidade de custo -- a sua TI cuidada todo mes, sem surpresa.",
    },
    {
      title: "Suporte remoto + presencial",
      body: "Atendimento remoto agil para o dia a dia e visita tecnica presencial quando o problema pede maos no equipamento.",
    },
    {
      title: "Infraestrutura e redes",
      body: "Projeto e manutencao de cabeamento, Wi-Fi corporativo e servidores -- uma base estavel para a operacao crescer.",
    },
    {
      title: "Backup e seguranca gerenciados",
      body: "Backup automatizado, antivirus e politicas de seguranca monitoradas -- os seus dados protegidos e recuperaveis.",
    },
    {
      title: "Licenciamento de software",
      body: "Licenca original e em conformidade -- parceiro oficial Microsoft, BitDefender e Intelbras, com a orientacao certa para a sua operacao.",
    },
    {
      title: "Atendimento prioritario com SLA",
      body: "Prazos de resposta acordados em contrato -- a sua empresa atendida primeiro, com compromisso de tempo.",
    },
  ],
  whoWeServe:
    "Organizacoes de tecnologia, saude, contabilidade e muito mais.",
  ctaLabel: "Falar com um especialista",
  ctaWhatsapp: "https://api.whatsapp.com/send?phone=551100000000",
};

// ============================================================================
// IMAGERY (decorative photo paths -- only a photo-shipping tenant has them)
// ============================================================================
// ============================================================================
// LINKS (the tenant's external web + social presence -- INPUT + rendered OUTPUT)
// ============================================================================

/** Orbit Tech's FICTITIOUS external presence (P0-A rebrand -- these URLs deliberately do
 *  NOT resolve to any real company; they exist only to exercise the presence-row renderer).
 *  ``store`` is the SAME loja.orbittech.com.br the nav "Loja" link derives from
 *  (byte-identical). WhatsApp is intentionally OMITTED here: it already has a dedicated CTA
 *  control via content.contact.whatsapp, so the presence row reconciles and never renders a
 *  duplicate WhatsApp affordance. YouTube is also omitted (honest-empty -- no fabricated
 *  channel URL is minted for a fictitious tenant). */
const ORBIT_LINKS: TenantLinks = {
  website: "https://www.orbittech.com.br/",
  store: "https://www.loja.orbittech.com.br",
  instagram: "https://www.instagram.com/orbittech_solucoes/",
  linkedin: "https://br.linkedin.com/company/orbittech-solucoes",
  facebook: "https://www.facebook.com/orbittechinfo/",
};

// ============================================================================
// THE TENANT CONFIGS (the assembled source-of-truth, per slug)
// ============================================================================
/** demo-orbit -- the IT-SERVICES vertical: a brand-gradient treatment (NO photos), a tech
 *  blog, a "Para Empresas" corporate area, and a service catalog. */
const ORBIT_CONFIG: TenantConfig = {
  slug: ORBIT_SLUG,
  brand: ORBIT_BRAND,
  shape: {
    vertical: "services",
    has_store: true,
    has_blog: true,
    has_b2b: true,
    b2b_mode: "corporate",
    b2b_label: "Para Empresas",
    imagery_mode: "brand",
    public_kinds: ORBIT_KINDS,
    blog_subtitle_category: "Seguranca",
  },
  content: ORBIT_CONTENT,
  imagery: null,
  blog: { categories: ORBIT_BLOG_CATEGORIES, posts: ORBIT_BLOG_POSTS },
  b2b: ORBIT_B2B,
  catalog: ORBIT_CATALOG,
  links: ORBIT_LINKS,
};

/** The RETAIL DEFAULT -- what an UNKNOWN slug resolves to (built-in-sample-shaped EXACTLY as
 *  today): the retail sections + kinds + cat blog + wholesale b2b, but the BRAND-gradient
 *  imagery (an unknown slug never ships photos) and an EMPTY catalog (an unknown slug is not a
 *  registered fixture tenant -> fixtures return null for it; the catalog here is never
 *  surfaced). The brand mirrors the SAMPLE_BRAND archetype (a fully synthetic identity, never
 *  a real tenant's) so nothing real is ever leaked for an unknown slug. This config object is
 *  the SHARED singleton an unknown slug resolves to -- so the historic reference-stable
 *  defaults (DEFAULT_SECTIONS, PUBLIC_KINDS) hold by identity. */
const RETAIL_DEFAULT_CONFIG: TenantConfig = { ...SELF_DATA };

/** The SEEDED tenants, keyed by slug. A slug ABSENT here (and not GENERATED) -> the retail
 *  default. These are byte-frozen -- a generated tenant can NEVER override them. */
const CONFIGS: Record<string, TenantConfig> = { ["starter"]: SELF_DATA };

// ============================================================================
// GENERATED TENANTS (the close-the-loop bridge -- merged UNDER the seeded CONFIGS)
//
// A bootstrap-GENERATED tenant config (the dev predev step wrote it into
// lib/generatedTenants.json from `.cex/tenants/<slug>/tenant_config.json`) is merged here so
// the preview renders /t/<slug> with NO hand-seeding. THREE invariants hold:
//   1. SEEDED WINS: a generated entry whose slug collides with a SEEDED tenant slug (e.g.
//      demo-acme) is DROPPED -- the seeded tenant is byte-identical, always.
//   2. HONEST GATE: an entry is accepted ONLY if it carries brand.tokens + a shape; anything
//      else is skipped (never crash, never fabricate). An accepted entry is NORMALIZED to a
//      TOTAL config (safe-empty collections) so even a PARTIAL config renders gracefully.
//   3. ZERO-REGRESSION DEFAULT: the committed registry is {} -> GENERATED is empty -> every
//      accessor behaves EXACTLY as before (unknown slug still degrades to the retail default
//      by the same shared singleton).
// ============================================================================

/** Coerce to a plain array (else []). TOTAL. */
function asArrayOf<T>(v: unknown): T[] {
  return Array.isArray(v) ? (v as T[]) : [];
}

/** True iff ``v`` is a SAME-ORIGIN root-relative "/path" (NOT "//host" / "/\"). Mirrors the
 *  path arm of isSafeLogoSrc -- generated imagery is trusted only when same-origin (a
 *  generated config can never point the decorative art at a cross-origin URL). */
function isSameOriginPath(v: unknown): v is string {
  return typeof v === "string" && /^\/[^/\\]/.test(v.trim());
}

/** The MINIMAL structural gate for a GENERATED entry: it MUST carry brand.tokens (an object)
 *  AND a shape (an object). Everything else is skipped (honest -- no crash, no fabrication).
 *  Token VALUES are not trusted here -- buildCssVars re-validates each one at the render
 *  boundary and the logo is scheme-gated by isSafeLogoSrc; this is only the shape gate. */
export function isUsableGeneratedConfig(value: unknown): boolean {
  if (!value || typeof value !== "object") return false;
  const v = value as Record<string, unknown>;
  const brand = v.brand as Record<string, unknown> | undefined;
  const hasBrandTokens =
    !!brand &&
    typeof brand === "object" &&
    !!brand.tokens &&
    typeof brand.tokens === "object";
  const hasShape = !!v.shape && typeof v.shape === "object";
  return hasBrandTokens && hasShape;
}

/** Normalize a raw shape into a TOTAL TenantShape with a safe default for EVERY field, so a
 *  partial generated config renders gracefully (empty sections, never fabricated). */
function normalizeGeneratedShape(raw: unknown): TenantShape {
  const s = (raw && typeof raw === "object" ? raw : {}) as Record<string, unknown>;
  const b2bMode: B2BMode | null =
    s.b2b_mode === "wholesale" || s.b2b_mode === "corporate" ? s.b2b_mode : null;
  return {
    vertical: (s.vertical === "services" ? "services" : "retail") as Vertical,
    has_store: s.has_store === true,
    has_blog: s.has_blog === true,
    has_b2b: s.has_b2b === true,
    b2b_mode: b2bMode,
    b2b_label: typeof s.b2b_label === "string" ? s.b2b_label : "B2B",
    imagery_mode: (s.imagery_mode === "photos" ? "photos" : "brand") as ImageryMode,
    public_kinds: asArrayOf<PublicKind>(s.public_kinds),
    blog_subtitle_category:
      typeof s.blog_subtitle_category === "string" ? s.blog_subtitle_category : "",
  };
}

/** Normalize the imagery block: trusted ONLY when it carries three SAME-ORIGIN "/path"
 *  strings (else null -> the brand-gradient treatment; no cross-origin photo leak). */
function normalizeGeneratedImagery(raw: unknown): TenantImageryPaths | null {
  if (!raw || typeof raw !== "object") return null;
  const im = raw as Record<string, unknown>;
  if (
    isSameOriginPath(im.hero) &&
    isSameOriginPath(im.section) &&
    isSameOriginPath(im.cardFallback)
  ) {
    return {
      hero: im.hero.trim(),
      section: im.section.trim(),
      cardFallback: im.cardFallback.trim(),
    };
  }
  return null;
}

/** Normalize the b2b block to a valid discriminated B2BContent (else the wholesale marker --
 *  the same honest default an unknown slug gets). */
function normalizeGeneratedB2b(raw: unknown): B2BContent {
  if (raw && typeof raw === "object") {
    const mode = (raw as Record<string, unknown>).mode;
    if (mode === "wholesale" || mode === "corporate") return raw as B2BContent;
  }
  return { mode: "wholesale" };
}

/** Normalize an ACCEPTED (already gated) raw entry into a TOTAL TenantConfig. The brand passes
 *  through (every token is RE-VALIDATED at the render boundary by buildCssVars; the logo is
 *  scheme-gated by isSafeLogoSrc). Shape + collections are defaulted so no view crashes; tenant
 *  URLs (links / content.contact / catalog media) are sanitized at THEIR render boundaries. */
function normalizeGeneratedConfig(slug: string, raw: unknown): TenantConfig {
  const v = raw as Record<string, unknown>;
  const blogRaw = (v.blog && typeof v.blog === "object" ? v.blog : {}) as Record<
    string,
    unknown
  >;
  const cfg: TenantConfig = {
    slug,
    brand: v.brand as BrandTheme,
    shape: normalizeGeneratedShape(v.shape),
    content:
      v.content && typeof v.content === "object" ? (v.content as TenantContent) : null,
    imagery: normalizeGeneratedImagery(v.imagery),
    blog: {
      categories: asArrayOf<string>(blogRaw.categories),
      posts: asArrayOf<SampleBlogPost>(blogRaw.posts),
    },
    b2b: normalizeGeneratedB2b(v.b2b),
    catalog:
      v.catalog && typeof v.catalog === "object"
        ? (v.catalog as Record<string, PublicCatalogItem[]>)
        : {},
  };
  if (v.links && typeof v.links === "object") cfg.links = v.links as TenantLinks;
  return cfg;
}

/** Build the validated GENERATED registry from the raw JSON map: skip an entry that fails the
 *  minimal gate (brand.tokens + shape) AND any slug that collides with a SEEDED tenant
 *  (generated NEVER overrides a SEEDED slug). Each accepted entry is normalized to a
 *  TOTAL config. TOTAL -- never throws. Exported for tests. */
export function buildGeneratedRegistry(raw: unknown): Record<string, TenantConfig> {
  const out: Record<string, TenantConfig> = {};
  if (!raw || typeof raw !== "object") return out;
  for (const [rawSlug, value] of Object.entries(raw as Record<string, unknown>)) {
    const s = (rawSlug ?? "").trim();
    if (!s) continue;
    if (Object.prototype.hasOwnProperty.call(CONFIGS, s)) continue; // never override seeded
    if (!isUsableGeneratedConfig(value)) continue; // honest: skip an invalid entry
    out[s] = normalizeGeneratedConfig(s, value);
  }
  return out;
}

/** The GENERATED tenants, built ONCE from the committed JSON (default {} -> empty on a fresh
 *  checkout / in prod). Merged UNDER CONFIGS so it can never override a seeded tenant. */
const GENERATED: Record<string, TenantConfig> = buildGeneratedRegistry(generatedRaw);

/** The registered white-label tenant slugs: the SEEDED slugs first, then any GENERATED slugs
 *  (already de-duped against the seeded ones). The fixtures layer uses this to honour the
 *  no-leak contract (an unknown slug -> null). With the committed {} registry this is exactly
 *  the SEEDED slugs' keys (zero-regression). */
export const TENANT_SLUGS: readonly string[] = [
  ...Object.keys(CONFIGS),
  ...Object.keys(GENERATED),
];

/** True iff ``slug`` is a registered white-label tenant (a SEEDED one OR a valid GENERATED
 *  one), NOT an unknown slug that merely degrades to the retail default. TOTAL. */
export function isRegisteredTenant(slug: string): boolean {
  const s = (slug ?? "").trim();
  return (
    Object.prototype.hasOwnProperty.call(CONFIGS, s) ||
    Object.prototype.hasOwnProperty.call(GENERATED, s)
  );
}

/**
 * Resolve a tenant SLUG to its declarative TenantConfig. A SEEDED tenant (e.g. demo-acme)
 * -> its specific config; a GENERATED tenant -> its normalized config; ANY other
 * slug -> the RETAIL DEFAULT (built-in-sample-shaped, EXACTLY as today). Seeded ALWAYS wins
 * over generated. TOTAL -- never throws. ASCII-only.
 *
 * HARDENING: the lookup is OWN-PROPERTY only -- mirrors resolveAdminTheme's guard
 * (apps/dashboard_web/lib/adminTheme.ts). A prototype-pollution-shaped slug (e.g.
 * "__proto__", "constructor") must never resolve via the inherited Object.prototype
 * chain (which is truthy and not caught by ?? ), or every downstream reader that
 * assumes a real TenantConfig shape (cfg.brand.tokens, cfg.shape.vertical, ...)
 * crashes. Plain bracket access CONFIGS[s] returns Object.prototype itself for
 * "__proto__" and the Object constructor for "constructor" -- neither is null or
 * undefined, so ?? never falls through to the retail default.
 */
export function tenantConfigFor(slug: string): TenantConfig {
  const s = (slug ?? "").trim();
  if (Object.prototype.hasOwnProperty.call(CONFIGS, s)) return CONFIGS[s];
  if (Object.prototype.hasOwnProperty.call(GENERATED, s)) return GENERATED[s];
  return RETAIL_DEFAULT_CONFIG;
}

// ----------------------------------------------------------------------------
// EXTERNAL-LINK SANITIZER + RESOLVER (the render-boundary guard for the links contract)
// ----------------------------------------------------------------------------

/** True iff ``href`` is SAFE to place in an EXTERNAL <a href> on the UNAUTHENTICATED public
 *  surface: ONLY an absolute ``https://`` URL (non-empty, no whitespace). Rejects
 *  javascript:, data:, http:, protocol-relative ("//host"), mailto:/tel:, and any relative
 *  path. Mirrors the https-only posture of isSafeLogoSrc / isSafeMediaSrc. TOTAL -- never
 *  throws. ASCII-only. */
export function isSafeHref(href: unknown): boolean {
  if (typeof href !== "string") return false;
  return /^https:\/\/[^\s]+$/i.test(href.trim());
}

/** One resolved, render-ready external link (a SAFE https href + a stable platform key +
 *  an ASCII display label). */
export interface TenantLinkEntry {
  /** the platform key (stable -- usable as a React key / icon selector). */
  key: keyof TenantLinks;
  /** the SAFE https href (already passed isSafeHref). */
  href: string;
  /** the ASCII display label (the platform name). */
  label: string;
}

/** The fixed render order + ASCII labels for the external-presence row. */
const TENANT_LINK_ORDER: ReadonlyArray<{ key: keyof TenantLinks; label: string }> = [
  { key: "website", label: "Site" },
  { key: "store", label: "Loja" },
  { key: "instagram", label: "Instagram" },
  { key: "linkedin", label: "LinkedIn" },
  { key: "facebook", label: "Facebook" },
  { key: "youtube", label: "YouTube" },
  { key: "x", label: "X" },
  { key: "tiktok", label: "TikTok" },
  { key: "whatsapp", label: "WhatsApp" },
];

/** Resolve a raw links block to render-ready entries: sanitize (drop any non-https URL),
 *  order (the fixed TENANT_LINK_ORDER), and RECONCILE WhatsApp. Renders ONLY links that
 *  EXIST and pass isSafeHref (honest-empty; a fabricated / unsafe URL is dropped). When the
 *  tenant already exposes a WhatsApp control elsewhere (``hasContactWhatsapp`` -- typically
 *  content.contact.whatsapp), the WhatsApp link is OMITTED so the row never renders a
 *  duplicate control (per the links contract). TOTAL. ASCII-only. */
export function safeLinkEntries(
  links: TenantLinks | null | undefined,
  opts?: { hasContactWhatsapp?: boolean },
): TenantLinkEntry[] {
  const l: TenantLinks = links ?? {};
  const hasWa = opts?.hasContactWhatsapp ?? false;
  const out: TenantLinkEntry[] = [];
  for (const { key, label } of TENANT_LINK_ORDER) {
    if (key === "whatsapp" && hasWa) continue; // reconcile: no duplicate WhatsApp control
    const url = (l[key] ?? "").trim();
    if (isSafeHref(url)) out.push({ key, href: url, label });
  }
  return out;
}

/** Resolve a SLUG to its render-ready external-link entries (SAFE https only, fixed order).
 *  DERIVES from the SoT (tenantConfigFor(slug).links) and reconciles WhatsApp against the
 *  tenant's content.contact.whatsapp. This is EXACTLY what the footer presence row renders.
 *  demo-acme + any unknown slug -> [] (honest-empty). TOTAL. */
export function tenantLinksFor(slug: string): TenantLinkEntry[] {
  const cfg = tenantConfigFor(slug);
  return safeLinkEntries(cfg.links, {
    hasContactWhatsapp: isSafeHref((cfg.content?.contact?.whatsapp ?? "").trim()),
  });
}

/** The tenant's SAFE external store URL ("" when none / unsafe) -- the nav "Loja" link
 *  DERIVES from links.store (stop hard-coding it). For a services-vertical tenant with its
 *  own webstore, this is byte-identical to its historic hard-coded value. TOTAL. */
export function tenantStoreUrl(slug: string): string {
  const url = (tenantConfigFor(slug).links?.store ?? "").trim();
  return isSafeHref(url) ? url : "";
}

// ----------------------------------------------------------------------------
// RE-EXPORTS for the domain modules + tests (the data moved here; these keep the existing
// import sites -- "@/lib/publicKinds" PUBLIC_KINDS, "@/lib/storeContent" SAMPLE_BLOG_POSTS,
// etc. -- working unchanged). They are re-exported from their domain modules in turn.
// ----------------------------------------------------------------------------

export {
  BLOG_CATEGORIES,
  SAMPLE_BLOG_POSTS,
  ORBIT_BLOG_CATEGORIES,
  ORBIT_BLOG_POSTS,
  ORBIT_B2B,
  DEFAULT_B2B_CONTENT,
  ORBIT_CONTENT,
};
