import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { createElement } from "react";

// ----------------------------------------------------------------------------
// generatedTenants -- THE CLOSE-THE-LOOP (preview) PROOF.
//
// A bootstrap GENERATES a tenant OFFLINE -> the dev predev step writes the merged
// { slug: tenant_config } map into lib/generatedTenants.json -> lib/tenantConfig STATICALLY
// imports that registry and merges it UNDER the seeded CONFIGS. This suite pins:
//
//   1. THE GATE + MERGE (pure): isUsableGeneratedConfig + buildGeneratedRegistry accept a
//      valid entry, normalize a partial one to safe empties, DROP a seeded-slug collision,
//      and skip an invalid entry. (No mock, no env -- the functions are pure.)
//   2. THE DEFAULT (committed {} -> zero-regression): with the committed empty registry,
//      TENANT_SLUGS / isRegisteredTenant / tenantConfigFor are BYTE-IDENTICAL to before
//      (only demo-acme + demo-orbit; an unknown slug is the shared retail-default singleton).
//   3. THE LOOP (real wiring + a view render): with a generated entry INJECTED into the
//      static JSON registry (via vi.doMock), the REAL tenantConfigFor / isRegisteredTenant /
//      fxGetTenantInfo resolve it, and HomeView renders ITS brand + shape (the generated
//      brand token reaches :root, no seeded/cat leak) -- proving "1 input -> a tenant appears
//      in the preview" with no hand-seeding. A seeded-slug collision still NEVER overrides.
//
// NOTE (P0-A rebrand): the hypothetical bootstrap-GENERATED example tenant below uses the
// slug "generated-co" -- deliberately NOT "demo-acme" / "demo-orbit", which are now the real
// SEEDED slugs (P0-A renamed them from the former real-tenant fixtures). Reusing a seeded
// slug here would silently flip these tests (buildGeneratedRegistry would DROP the entry
// as a seeded-slug collision instead of accepting it as a fresh generated tenant).
//
// config.ts reads NEXT_PUBLIC_* once at import, so the view test imports FRESH in fixtures
// mode (vi.resetModules + env + dynamic import), mirroring orbit.test.tsx / degrade.test.tsx.
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

// The REAL module (committed registry = {}). Used for the PURE + default-{} groups. The
// injected-tenant group uses vi.doMock + a FRESH dynamic import instead.
import {
  buildGeneratedRegistry,
  isUsableGeneratedConfig,
  tenantConfigFor,
  isRegisteredTenant,
  TENANT_SLUGS,
} from "@/lib/tenantConfig";

// A SAMPLE bootstrap-GENERATED tenant_config (the proof slug "generated-co", NOT a seeded
// slug). imagery_mode "brand" (no photos), with a DISTINCTIVE GREEN brand token so a render
// assertion can prove THIS generated brand reached :root (never a seeded one). Plain object
// -> passed as `unknown`.
const GENERATED_SAMPLE = {
  slug: "generated-co",
  brand: {
    name: "Generated Co (amostra)",
    tagline: "Bootstrap-gerado -- prova do loop",
    logoAlt: "Generated Co",
    tokens: {
      background: "0 0% 100%",
      foreground: "0 0% 10%",
      primary: "120 60% 30%",
      primaryForeground: "0 0% 100%",
      brand: "120 60% 40%",
      brandForeground: "0 0% 100%",
      highlight: "30 90% 50%",
      radius: "0.5rem",
    },
    fontFamily: "Inter, sans-serif",
  },
  shape: {
    vertical: "retail",
    has_store: true,
    has_blog: false,
    has_b2b: false,
    b2b_mode: null,
    b2b_label: "B2B",
    imagery_mode: "brand",
    public_kinds: [
      { kind: "marketplace_listing", label: "Catalogo", blurb: "Itens publicados." },
    ],
    blog_subtitle_category: "",
  },
  content: null,
  imagery: null,
  blog: { categories: [], posts: [] },
  b2b: { mode: "wholesale" },
  catalog: {},
};

// ============================================================================
// 1. THE GATE + MERGE (pure functions)
// ============================================================================

describe("isUsableGeneratedConfig -- the minimal honest gate (brand.tokens + shape)", () => {
  it("accepts an entry that carries brand.tokens AND a shape", () => {
    expect(isUsableGeneratedConfig(GENERATED_SAMPLE)).toBe(true);
  });

  it("rejects entries missing brand.tokens or shape, and non-objects", () => {
    expect(isUsableGeneratedConfig({ brand: {}, shape: {} })).toBe(false); // no tokens
    expect(isUsableGeneratedConfig({ brand: { tokens: {} } })).toBe(false); // no shape
    expect(isUsableGeneratedConfig({ shape: {} })).toBe(false); // no brand
    expect(isUsableGeneratedConfig(null)).toBe(false);
    expect(isUsableGeneratedConfig("nope")).toBe(false);
  });
});

describe("buildGeneratedRegistry -- merge UNDER the seeded configs", () => {
  it("accepts a valid entry and normalizes it to a TOTAL config", () => {
    const reg = buildGeneratedRegistry({ "generated-co": GENERATED_SAMPLE });
    expect(Object.keys(reg)).toEqual(["generated-co"]);
    const cfg = reg["generated-co"];
    expect(cfg.slug).toBe("generated-co");
    expect(cfg.brand.name).toBe("Generated Co (amostra)");
    expect(cfg.shape.vertical).toBe("retail");
    expect(cfg.shape.imagery_mode).toBe("brand");
    expect(cfg.catalog).toEqual({});
    expect(cfg.blog.posts).toEqual([]);
    expect(cfg.imagery).toBeNull();
    expect(cfg.b2b).toEqual({ mode: "wholesale" });
  });

  it("NEVER overrides a seeded tenant -- a demo-acme / demo-orbit key is dropped", () => {
    const reg = buildGeneratedRegistry({
      "demo-acme": GENERATED_SAMPLE, // valid shape, but a SEEDED slug -> dropped
      "demo-orbit": GENERATED_SAMPLE,
    });
    expect(reg).toEqual({});
  });

  it("skips an invalid entry + a blank slug; keeps the valid ones; {}/null -> {}", () => {
    const reg = buildGeneratedRegistry({
      "": GENERATED_SAMPLE, // blank slug -> skipped
      broken: { brand: { name: "x" }, shape: {} }, // no tokens -> skipped
      okay: GENERATED_SAMPLE,
    });
    expect(Object.keys(reg)).toEqual(["okay"]);
    expect(buildGeneratedRegistry({})).toEqual({});
    expect(buildGeneratedRegistry(null)).toEqual({});
    expect(buildGeneratedRegistry("nope")).toEqual({});
  });

  it("a PARTIAL config (gate passes, collections missing) normalizes to safe empties", () => {
    const reg = buildGeneratedRegistry({
      "demo-partial": {
        brand: { name: "P", tokens: { brand: "10 50% 50%" } },
        shape: { vertical: "services" },
      },
    });
    const cfg = reg["demo-partial"];
    expect(cfg).toBeTruthy();
    expect(cfg.shape.vertical).toBe("services");
    expect(cfg.shape.public_kinds).toEqual([]); // defaulted
    expect(cfg.shape.b2b_label).toBe("B2B"); // defaulted
    expect(cfg.blog).toEqual({ categories: [], posts: [] }); // defaulted
    expect(cfg.catalog).toEqual({}); // defaulted
    expect(cfg.content).toBeNull();
    expect(cfg.imagery).toBeNull();
    expect(cfg.b2b).toEqual({ mode: "wholesale" });
  });

  it("drops a cross-origin imagery block (keeps only same-origin /paths)", () => {
    const reg = buildGeneratedRegistry({
      "demo-x": {
        brand: { name: "X", tokens: { brand: "10 50% 50%" } },
        shape: { vertical: "retail", imagery_mode: "photos" },
        imagery: { hero: "https://evil.example/x.jpg", section: "//host/y.jpg", cardFallback: "/images/ok.jpg" },
      },
    });
    // not all three are same-origin "/paths" -> imagery normalizes to null (brand treatment)
    expect(reg["demo-x"].imagery).toBeNull();
  });
});

// ============================================================================
// 2. THE DEFAULT (committed {} registry) -- byte-identical, zero-regression
// ============================================================================

describe("default committed registry ({}) -- byte-identical, zero-regression", () => {
  it("TENANT_SLUGS is exactly the seeded pair", () => {
    expect(TENANT_SLUGS).toEqual(["demo-acme", "demo-orbit"]);
  });

  it("only the seeded slugs register; generated-co + unknown do not", () => {
    expect(isRegisteredTenant("demo-acme")).toBe(true);
    expect(isRegisteredTenant("demo-orbit")).toBe(true);
    expect(isRegisteredTenant("generated-co")).toBe(false);
    expect(isRegisteredTenant("whoever")).toBe(false);
  });

  it("seeded brands resolve unchanged; an unknown slug is the SAME retail-default singleton", () => {
    expect(tenantConfigFor("demo-acme").brand.name).toBe("Acme Pet Shop (amostra)");
    expect(tenantConfigFor("demo-orbit").brand.name).toBe("Orbit Tech");
    const a = tenantConfigFor("whoever");
    const b = tenantConfigFor("another-unknown");
    expect(a).toBe(b); // shared singleton (identity preserved)
    expect(a.shape.vertical).toBe("retail");
  });
});

// ============================================================================
// 3. THE LOOP -- a GENERATED tenant injected into the static registry resolves through the
//    REAL accessors + renders in the preview (vi.doMock + fresh dynamic import).
// ============================================================================

const ORIGINAL_ENV = { ...process.env };

describe("a GENERATED tenant resolves through the real accessors + renders in the preview", () => {
  beforeEach(() => {
    vi.resetModules();
    process.env.NEXT_PUBLIC_FIXTURES = "1";
    delete process.env.NEXT_PUBLIC_API_URL;
    // Inject the registry that lib/tenantConfig's STATIC import picks up. Includes:
    //   * a VALID generated tenant (generated-co),
    //   * an INVALID entry (no tokens) -> must be skipped,
    //   * a SEEDED-slug collision (demo-orbit) -> must NEVER override the seeded config.
    vi.doMock("@/lib/generatedTenants.json", () => ({
      default: {
        "generated-co": GENERATED_SAMPLE,
        "broken-gen": { brand: { name: "x" }, shape: {} },
        "demo-orbit": { ...GENERATED_SAMPLE, slug: "demo-orbit" },
      },
    }));
  });

  afterEach(() => {
    vi.doUnmock("@/lib/generatedTenants.json");
    vi.resetModules();
    process.env = { ...ORIGINAL_ENV };
  });

  it("tenantConfigFor + isRegisteredTenant + TENANT_SLUGS resolve the generated tenant", async () => {
    const tc = await import("@/lib/tenantConfig");
    // the generated tenant resolves
    expect(tc.isRegisteredTenant("generated-co")).toBe(true);
    expect(tc.tenantConfigFor("generated-co").brand.name).toBe("Generated Co (amostra)");
    expect(tc.tenantConfigFor("generated-co").shape.vertical).toBe("retail");
    // TENANT_SLUGS includes the generated slug AND keeps the seeded pair
    expect(tc.TENANT_SLUGS).toContain("generated-co");
    expect(tc.TENANT_SLUGS).toContain("demo-acme");
    expect(tc.TENANT_SLUGS).toContain("demo-orbit");
    // the invalid entry is skipped (honest)
    expect(tc.isRegisteredTenant("broken-gen")).toBe(false);
    // SEEDED WINS: the demo-orbit collision did NOT override the seeded brand
    expect(tc.tenantConfigFor("demo-orbit").brand.name).toBe("Orbit Tech");
    // seeded demo-acme stays byte-identical under the mock
    expect(tc.tenantConfigFor("demo-acme").brand.name).toBe("Acme Pet Shop (amostra)");
    // an unknown slug still degrades to the shared retail-default singleton
    expect(tc.tenantConfigFor("nope")).toBe(tc.tenantConfigFor("nobody"));
  });

  it("fixtures fxGetTenantInfo resolves the generated tenant brand (no-leak preserved)", async () => {
    const fx = await import("@/lib/fixtures");
    const info = fx.fxGetTenantInfo("generated-co");
    expect(info).not.toBeNull();
    expect(info!.slug).toBe("generated-co");
    expect(info!.brand.name).toBe("Generated Co (amostra)");
    expect(info!.brand.tokens?.brand).toBe("120 60% 40%");
    expect(fx.fxGetTenantInfo("no-such-tenant")).toBeNull(); // unknown still null
  });

  it("HomeView renders the generated tenant brand + shape (green --brand, brand-gradient, no cat leak)", async () => {
    const { HomeView } = await import("@/components/views/HomeView");
    const { container } = render(createElement(HomeView, { slug: "generated-co" }));
    await waitFor(() => expect(screen.getByText("Categorias")).toBeTruthy());
    // the GENERATED brand name renders (hero + chrome)
    expect(screen.getAllByText("Generated Co (amostra)").length).toBeGreaterThan(0);
    // the GENERATED green brand token reached :root (the reskin keystone fired for it)
    const css = container.querySelector("style")?.textContent ?? "";
    expect(css).toContain("--brand:120 60% 40%");
    // it is NOT a seeded tenant -- no built-in sample violet token leaked
    expect(css).not.toContain("258 60% 45%");
    // imagery_mode "brand" -> the brand-gradient hero (no photo, no cat leak)
    expect(container.innerHTML).toContain("hsl(var(--brand))");
    for (const img of Array.from(container.querySelectorAll("img"))) {
      expect((img.getAttribute("src") ?? "").includes("/images/cat-")).toBe(false);
    }
  });
});
