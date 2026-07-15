import { describe, it, expect } from "vitest";
import {
  tenantConfigFor,
  isRegisteredTenant,
  TENANT_SLUGS,
  PUBLIC_KINDS,
  SAMPLE_SLUG,
  ORBIT_SLUG,
} from "@/lib/tenantConfig";
import { tenantSectionsFor, DEFAULT_SECTIONS } from "@/lib/tenantSections";
import { publicKindsFor } from "@/lib/publicKinds";
import { tenantContentFor } from "@/lib/tenantContent";
import { imageryFor } from "@/lib/tenantImagery";
import { buildHomeCopy } from "@/lib/brandText";
import { fxGetTenantInfo, fxGetCatalog } from "@/lib/fixtures";
import {
  blogPostsFor,
  blogCategoriesFor,
  b2bContentFor,
  blogSubtitleFor,
  SAMPLE_BLOG_POSTS,
  ORBIT_BLOG_POSTS,
} from "@/lib/storeContent";

// ============================================================================
// tenantConfig -- THE BYTE-IDENTICAL PROOF.
//
// One declarative source-of-truth (tenantConfigFor) now backs the six per-slug resolvers.
// This suite pins every accessor's output for 'demo-acme' and 'demo-orbit' (P0-A rebrand:
// fictitious tenants, replacing the former real-tenant / real-brand fixtures) to the KNOWN
// current values, and pins the unknown-slug retail default. If the relocation changed a
// single value, one of these fails.
//
// EXCEPTION (intentional, item #4): blogSubtitleFor('demo-orbit') is the ONE rendered value
// that changes -- the blog subtitle category is now per-tenant (shape.blog_subtitle_category),
// so demo-orbit shows "Seguranca" instead of the previously hard-coded cat "Bem-estar". The
// demo-acme subtitle stays byte-identical.
// ============================================================================

describe("tenantConfigFor -- registration + the unknown-slug retail default", () => {
  it("registers exactly demo-acme + demo-orbit; everything else degrades to retail default", () => {
    expect(TENANT_SLUGS).toEqual(["demo-acme", "demo-orbit"]);
    expect(SAMPLE_SLUG).toBe("demo-acme");
    expect(ORBIT_SLUG).toBe("demo-orbit");
    expect(isRegisteredTenant("demo-acme")).toBe(true);
    expect(isRegisteredTenant("demo-orbit")).toBe(true);
    expect(isRegisteredTenant("whoever")).toBe(false);
    expect(isRegisteredTenant("")).toBe(false);
  });

  it("an unknown slug resolves to the SAME retail-default config object (shared singleton)", () => {
    const a = tenantConfigFor("whoever");
    const b = tenantConfigFor("another-unknown");
    expect(a).toBe(b);
    expect(a.shape.vertical).toBe("retail");
    expect(a.shape.imagery_mode).toBe("brand"); // unknown ships no photos
    expect(a.shape.public_kinds).toBe(PUBLIC_KINDS);
  });

  // R-016: a prototype-pollution-shaped slug (e.g. "__proto__", "constructor") must
  // degrade to the SAME retail default as any other unknown slug -- NOT resolve via
  // the inherited Object.prototype chain (which would return Object.prototype itself
  // / the Object constructor, silently swallowed by ?? because neither is null/undefined,
  // and crash the first downstream reader that assumes a real TenantConfig shape.
  it("prototype-pollution-shaped slugs degrade to the retail default (never crash)", () => {
    const fallback = tenantConfigFor("whoever");
    for (const evil of ["__proto__", "constructor", "prototype", "toString", "hasOwnProperty"]) {
      const cfg = tenantConfigFor(evil);
      expect(cfg).toBe(fallback);
      expect(cfg.shape.vertical).toBe("retail");
      // the real-world crash site: callers read cfg.brand.tokens without optional
      // chaining (e.g. fixtures.ts, buildHomeCopy). This must not throw.
      expect(() => cfg.brand.tokens).not.toThrow();
      expect(cfg.brand.tokens).toBeTruthy();
    }
    expect(isRegisteredTenant("__proto__")).toBe(false);
    expect(isRegisteredTenant("constructor")).toBe(false);
  });
});

describe("shape -- the business-shape mirror (snake_case keys)", () => {
  it("demo-acme is the retail shape", () => {
    const s = tenantConfigFor("demo-acme").shape;
    expect(s.vertical).toBe("retail");
    expect(s.has_blog).toBe(true);
    expect(s.has_b2b).toBe(true);
    expect(s.b2b_mode).toBe("wholesale");
    expect(s.b2b_label).toBe("B2B");
    expect(s.imagery_mode).toBe("photos");
    expect(s.blog_subtitle_category).toBe("Bem-estar");
    expect(s.public_kinds.map((k) => k.kind)).toEqual(["marketplace_listing", "product_ad"]);
  });

  it("demo-orbit is the services shape (corporate b2b, brand imagery, services kind)", () => {
    const s = tenantConfigFor("demo-orbit").shape;
    expect(s.vertical).toBe("services");
    expect(s.has_blog).toBe(true);
    expect(s.has_b2b).toBe(true);
    expect(s.b2b_mode).toBe("corporate");
    expect(s.b2b_label).toBe("Para Empresas");
    expect(s.imagery_mode).toBe("brand");
    expect(s.blog_subtitle_category).toBe("Seguranca");
    expect(s.public_kinds.map((k) => k.kind)).toEqual(["service"]);
  });
});

describe("tenantSectionsFor -- byte-identical + reference-stable default", () => {
  it("demo-orbit sections", () => {
    expect(tenantSectionsFor("demo-orbit")).toEqual({
      blog: true,
      b2b: true,
      b2bLabel: "Para Empresas",
      blogLabel: "Blog",
    });
  });

  it("demo-acme + any unknown slug return the DEFAULT_SECTIONS object BY REFERENCE", () => {
    expect(tenantSectionsFor("demo-acme")).toBe(DEFAULT_SECTIONS);
    expect(tenantSectionsFor("whoever")).toBe(DEFAULT_SECTIONS);
    expect(DEFAULT_SECTIONS).toEqual({
      blog: true,
      b2b: true,
      b2bLabel: "B2B",
      blogLabel: "Blog",
    });
  });
});

describe("publicKindsFor -- byte-identical + reference-stable default", () => {
  it("demo-acme + unknown return the PUBLIC_KINDS array BY REFERENCE", () => {
    expect(publicKindsFor("demo-acme")).toBe(PUBLIC_KINDS);
    expect(publicKindsFor("whoever")).toBe(PUBLIC_KINDS);
    expect(PUBLIC_KINDS).toEqual([
      { kind: "marketplace_listing", label: "Catalogo", blurb: "Anuncios de produtos publicados." },
      { kind: "product_ad", label: "Anuncios", blurb: "Pecas de anuncio publicadas." },
    ]);
  });

  it("demo-orbit offers the single service kind with its own label", () => {
    expect(publicKindsFor("demo-orbit")).toEqual([
      { kind: "service", label: "Servicos", blurb: "Servicos de tecnologia e assistencia tecnica." },
    ]);
  });
});

describe("tenantContentFor -- byte-identical", () => {
  it("demo-acme + unknown carry NO extra content (null)", () => {
    expect(tenantContentFor("demo-acme")).toBeNull();
    expect(tenantContentFor("anything")).toBeNull();
  });

  it("demo-orbit carries the full extra content (partners/about/social/testimonials/contact)", () => {
    const c = tenantContentFor("demo-orbit")!;
    expect(c).not.toBeNull();
    expect(c.heroSubline).toBe("Especialistas em tecnologia -- confiabilidade comeca conosco.");
    expect(c.ctaLabel).toBe("Fale no WhatsApp");
    expect(c.partners?.length).toBe(3);
    expect(c.partners?.[0]).toEqual({ src: "/images/tenants/demo-orbit/partner-microsoft.png", alt: "Microsoft" });
    expect(c.aboutStats?.length).toBe(4);
    expect(c.aboutStats?.[0]).toEqual({ value: "+20 anos", label: "no mercado" });
    expect(c.socialProof).toEqual({ rating: 4.6, count: 68, source: "Google" });
    expect(c.testimonials?.length).toBe(3);
    expect(c.testimonials?.every((t) => t.sample)).toBe(true);
    expect(c.testimonials?.[0].author).toBe("Fernanda Rocha (amostra)");
    expect(c.contact?.phone).toBe("(11) 0000-0000");
    expect(c.contact?.email).toBe("contato@orbittech.com.br");
    expect(c.contact?.whatsapp).toBe("https://api.whatsapp.com/send?phone=551100000000");
    expect(c.contact?.instagram).toBe("orbittech_solucoes");
    expect(c.contact?.store).toBe("https://www.loja.orbittech.com.br");
  });
});

describe("imageryFor -- byte-identical", () => {
  it("demo-acme ships the EXACT first-party cat photos", () => {
    const im = imageryFor("demo-acme");
    expect(im.mode).toBe("photos");
    if (im.mode === "photos") {
      expect(im.hero).toBe("/images/cat-hero.jpg");
      expect(im.section).toBe("/images/cat-section.jpg");
      expect(im.cardFallback).toBe("/images/cat-product.jpg");
    }
  });

  it("demo-orbit + any unknown slug get the brand treatment (no cat leak)", () => {
    expect(imageryFor("demo-orbit").mode).toBe("brand");
    expect(imageryFor("some-other-tenant").mode).toBe("brand");
  });
});

describe("blogPostsFor / blogCategoriesFor -- byte-identical", () => {
  it("demo-acme + unknown -> the cat posts (6) + categories", () => {
    expect(blogPostsFor("demo-acme")).toBe(SAMPLE_BLOG_POSTS);
    expect(blogPostsFor("whoever")).toBe(SAMPLE_BLOG_POSTS);
    expect(SAMPLE_BLOG_POSTS.length).toBe(6);
    expect(SAMPLE_BLOG_POSTS[0].slug).toBe("ambiente-felino-enriquecido");
    expect(blogCategoriesFor("demo-acme")).toEqual(["Bem-estar", "Dicas", "Saude", "Curiosidades"]);
  });

  it("demo-orbit -> the tech posts (5) + tech categories", () => {
    expect(blogPostsFor("demo-orbit")).toBe(ORBIT_BLOG_POSTS);
    expect(ORBIT_BLOG_POSTS.length).toBe(5);
    expect(ORBIT_BLOG_POSTS[0].slug).toBe("ransomware-5-habitos-que-protegem-o-seu-pc");
    expect(blogCategoriesFor("demo-orbit")).toEqual([
      "Seguranca",
      "Cloud",
      "Manutencao",
      "Redes",
      "Licenciamento",
    ]);
  });
});

describe("blogSubtitleFor -- #4 (per-tenant category)", () => {
  it("demo-acme + unknown stay byte-identical to the historic hard-coded line", () => {
    const expected = "Bem-estar, dicas e curiosidades -- conteudo editorial da marca.";
    expect(blogSubtitleFor("demo-acme")).toBe(expected);
    expect(blogSubtitleFor("whoever")).toBe(expected);
  });

  it("demo-orbit shows its OWN category (the #4 fix -- INTENTIONAL change)", () => {
    expect(blogSubtitleFor("demo-orbit")).toBe(
      "Seguranca, dicas e curiosidades -- conteudo editorial da marca.",
    );
  });
});

describe("b2bContentFor -- byte-identical", () => {
  it("demo-acme + unknown -> the wholesale marker", () => {
    expect(b2bContentFor("demo-acme")).toEqual({ mode: "wholesale" });
    expect(b2bContentFor("whoever")).toEqual({ mode: "wholesale" });
  });

  it("demo-orbit -> the corporate content", () => {
    const b = b2bContentFor("demo-orbit");
    expect(b.mode).toBe("corporate");
    if (b.mode === "corporate") {
      expect(b.eyebrow).toBe("Para empresas");
      expect(b.heroTitle).toBe("Orbit Tech para Empresas");
      expect(b.offers.length).toBe(6);
      expect(b.offers[0].title).toBe("Contrato de manutencao mensal");
      expect(b.whoWeServe).toBe("Organizacoes de tecnologia, saude, contabilidade e muito mais.");
      expect(b.ctaLabel).toBe("Falar com um especialista");
      expect(b.ctaWhatsapp).toBe("https://api.whatsapp.com/send?phone=551100000000");
    }
  });
});

describe("buildHomeCopy -- vertical sourced from shape.vertical via slug", () => {
  it("slug=demo-acme -> retail copy (cat glyph + PIX claim)", () => {
    const copy = buildHomeCopy(tenantConfigFor("demo-acme").brand, { slug: "demo-acme" });
    expect(copy.pillars.find((p) => p.title === "Feito com cuidado")?.icon).toBe("cat");
    expect(copy.pillars.map((p) => p.body).join(" ")).toContain("PIX");
  });

  it("slug=demo-orbit -> services copy (heart glyph, support pillar, no PIX)", () => {
    const copy = buildHomeCopy(tenantConfigFor("demo-orbit").brand, { slug: "demo-orbit" });
    expect(copy.pillars.find((p) => p.title === "Feito com cuidado")?.icon).toBe("heart");
    const joined = copy.pillars.map((p) => p.title + " " + p.body).join(" ");
    expect(joined).not.toContain("PIX");
    expect(joined).toContain("Atendimento humanizado");
  });

  it("an explicit isService still wins over slug (back-compat for the existing caller)", () => {
    const copy = buildHomeCopy({ name: "Acme" }, { isService: true, slug: "demo-acme" });
    expect(copy.pillars.find((p) => p.title === "Feito com cuidado")?.icon).toBe("heart");
  });
});

describe("fixtures fxGetTenantInfo / fxGetCatalog -- byte-identical (brand + catalog derived)", () => {
  it("demo-acme tenant-info: synthetic id + the built-in sample brand tokens", () => {
    const info = fxGetTenantInfo("demo-acme")!;
    expect(info.tenant_id).toBe("tenant_sample_demo_acme");
    expect(info.slug).toBe("demo-acme");
    expect(info.published_at).toBeNull();
    expect(info.brand.name).toBe("Acme Pet Shop (amostra)");
    expect(info.brand.tagline).toBe("Produtos premium para gatos -- catalogo de demonstracao");
    expect(info.brand.tokens?.brand).toBe("258 60% 45%");
    expect(info.brand.tokens?.highlight).toBe("35 90% 45%");
    expect(info.brand.tokens?.radius).toBe("0.75rem");
  });

  it("demo-orbit tenant-info: synthetic id + the blue/red brand tokens + committed logo", () => {
    const info = fxGetTenantInfo("demo-orbit")!;
    expect(info.tenant_id).toBe("tenant_sample_demo_orbit");
    expect(info.brand.name).toBe("Orbit Tech");
    expect(info.brand.tagline).toBe("Solucoes em Tecnologia");
    expect(info.brand.logo).toBe("/images/tenants/demo-orbit/logo.png");
    expect(info.brand.tokens?.brand).toBe("231 48% 48%");
    expect(info.brand.tokens?.primary).toBe("231 48% 48%");
    expect(info.brand.tokens?.highlight).toBe("4 90% 58%");
    expect(info.brand.tokens?.radius).toBe("0.625rem");
  });

  it("an unknown slug -> null in BOTH endpoints (no-leak)", () => {
    expect(fxGetTenantInfo("no-such-tenant")).toBeNull();
    expect(fxGetCatalog("no-such-tenant", "marketplace_listing")).toBeNull();
  });

  it("demo-acme catalog: 4 marketplace_listings + 1 product_ad; an unknown kind -> empty", () => {
    const ml = fxGetCatalog("demo-acme", "marketplace_listing")!;
    expect(ml.items.length).toBe(4);
    expect(ml.items[0].id).toBe("ml_sample_0001");
    expect(ml.tenant_id).toBe("tenant_sample_demo_acme");
    expect(fxGetCatalog("demo-acme", "product_ad")!.items.length).toBe(1);
    expect(fxGetCatalog("demo-acme", "kind_with_no_rows")!.items.length).toBe(0);
  });

  it("demo-orbit catalog: 9 services; honours limit/offset paging", () => {
    const svc = fxGetCatalog("demo-orbit", "service")!;
    expect(svc.items.length).toBe(9);
    expect(svc.items[0].id).toBe("svc_orbit_0001");
    const paged = fxGetCatalog("demo-orbit", "service", 2, 1)!;
    expect(paged.items.length).toBe(2);
    expect(paged.items[0].id).toBe("svc_orbit_0002");
    expect(paged.limit).toBe(2);
    expect(paged.offset).toBe(1);
  });
});
