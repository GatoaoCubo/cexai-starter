import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { createElement } from "react";

// ----------------------------------------------------------------------------
// HomeView VERTICAL is SHAPE-DRIVEN -- the white-label home reads the AUTHORITATIVE
// shape.vertical from the tenant config, NOT the fragile primaryKind==="service" heuristic
// off the catalog kinds. The bug this pins: a GENERATED services tenant whose published
// kinds are NOT literally "service" (e.g. "consulting_offer") used to fall through to the
// RETAIL home (wrong CTA "Ver catalogo" + a false PIX/parcelamento trust-row). Driving it
// from shape.vertical fixes that while keeping the seeded tenants byte-identical.
//
// These assert:
//   * a SERVICES-shape tenant whose kinds are NOT "service" STILL renders the services home
//     (CTA "Ver servicos", NO retail trust-row, the support pillar) -- the new capability;
//   * a RETAIL-shape generated tenant renders the retail home (CTA "Ver catalogo" + the
//     trust-row) -- the other branch;
//   * ZERO-REGRESSION: seeded demo-orbit (services) + demo-acme (retail) are unchanged.
//
// The retail trust-row is asserted via its STABLE aria-label ("Garantias de compra" -- the
// TrustRow ul). A generated tenant is injected exactly like generatedTenants.test.tsx
// (vi.doMock the static JSON registry + a FRESH dynamic import in fixtures mode); config.ts
// reads NEXT_PUBLIC_* once at import, so the view must be imported AFTER the env is set.
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

/** A minimal-but-valid brand token set (mirrors generatedTenants.test.tsx). buildCssVars
 *  re-validates each token at the render boundary, so this subset renders gracefully. */
const TOKENS = {
  background: "0 0% 100%",
  foreground: "0 0% 10%",
  primary: "210 60% 30%",
  primaryForeground: "0 0% 100%",
  brand: "210 60% 40%",
  brandForeground: "0 0% 100%",
  highlight: "30 90% 50%",
  radius: "0.5rem",
};

/** A GENERATED SERVICES tenant whose catalog kinds are NOT "service" -- the EXACT case the
 *  old primaryKind==="service" heuristic got WRONG (it rendered the retail home). The vertical
 *  is the authoritative discriminator; the kind is "consulting_offer". */
const GEN_SERVICES = {
  slug: "gen-svc",
  brand: {
    name: "GenServ (amostra)",
    tagline: "Servicos gerados -- prova shape-driven",
    logoAlt: "GenServ",
    tokens: TOKENS,
    fontFamily: "Inter, sans-serif",
  },
  shape: {
    vertical: "services",
    has_store: false,
    has_blog: false,
    has_b2b: false,
    b2b_mode: null,
    b2b_label: "B2B",
    imagery_mode: "brand",
    // the public kinds are NOT "service" -> the kind heuristic would have said RETAIL.
    public_kinds: [
      { kind: "consulting_offer", label: "Consultoria", blurb: "Ofertas de consultoria publicadas." },
    ],
    blog_subtitle_category: "",
  },
  content: null,
  imagery: null,
  blog: { categories: [], posts: [] },
  b2b: { mode: "wholesale" },
  catalog: {},
};

/** A GENERATED RETAIL tenant (the control) -- vertical retail, a product kind. */
const GEN_RETAIL = {
  slug: "gen-retail",
  brand: {
    name: "GenShop (amostra)",
    tagline: "Loja gerada -- prova shape-driven",
    logoAlt: "GenShop",
    tokens: TOKENS,
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

/** The stable selector for the retail BR-commerce trust row (TrustRow ul aria-label). */
const TRUST_ROW = '[aria-label="Garantias de compra"]';

const ORIGINAL_ENV = { ...process.env };

describe("HomeView vertical is SHAPE-DRIVEN (shape.vertical), not the primaryKind heuristic", () => {
  beforeEach(() => {
    vi.resetModules();
    process.env.NEXT_PUBLIC_FIXTURES = "1";
    delete process.env.NEXT_PUBLIC_API_URL;
    vi.doMock("@/lib/generatedTenants.json", () => ({
      default: { "gen-svc": GEN_SERVICES, "gen-retail": GEN_RETAIL },
    }));
  });

  afterEach(() => {
    vi.doUnmock("@/lib/generatedTenants.json");
    vi.resetModules();
    process.env = { ...ORIGINAL_ENV };
  });

  it("a SERVICES-shape tenant whose kinds are NOT 'service' STILL renders the services home", async () => {
    const { HomeView } = await import("@/components/views/HomeView");
    const { container } = render(createElement(HomeView, { slug: "gen-svc" }));
    await waitFor(() => expect(screen.getByText("Categorias")).toBeTruthy());
    // the SERVICES CTA -- NOT the retail "Ver catalogo".
    expect(screen.getAllByText("Ver servicos").length).toBeGreaterThan(0);
    expect(container.innerHTML).not.toContain("Ver catalogo");
    // NO retail trust-row (PIX/parcelamento would be a FALSE claim for a services tenant).
    expect(container.querySelector(TRUST_ROW)).toBeNull();
    expect(container.innerHTML).not.toContain("PIX");
    expect(container.innerHTML).not.toContain("12x sem juros");
    // the vertical-aware SUPPORT pillar replaces the checkout pillar.
    expect(screen.getByText("Atendimento humanizado")).toBeTruthy();
    // PROOF the kind heuristic would have FAILED: the primary kind is NOT "service" (its
    // label "Consultoria" renders in BOTH the Categorias cards and the footer nav).
    expect(screen.getAllByText("Consultoria").length).toBeGreaterThan(0);
    // the closing CTA is the services phrasing (woven with the generated brand name).
    expect(screen.getByText(/Conheca os servicos de GenServ/)).toBeTruthy();
  });

  it("a RETAIL-shape generated tenant renders the retail home (CTA + the trust-row)", async () => {
    const { HomeView } = await import("@/components/views/HomeView");
    const { container } = render(createElement(HomeView, { slug: "gen-retail" }));
    await waitFor(() => expect(screen.getByText("Categorias")).toBeTruthy());
    // the RETAIL CTA -- NOT the services "Ver servicos".
    expect(screen.getAllByText("Ver catalogo").length).toBeGreaterThan(0);
    expect(container.innerHTML).not.toContain("Ver servicos");
    // the retail BR-commerce trust-row IS present.
    expect(container.querySelector(TRUST_ROW)).not.toBeNull();
    expect(container.innerHTML).toContain("12x sem juros");
    // the retail commerce pillar (PIX) -- not the services support pillar.
    expect(container.innerHTML).toContain("PIX");
    expect(screen.queryByText("Atendimento humanizado")).toBeNull();
  });

  it("ZERO-REGRESSION: seeded demo-orbit (services) is unchanged -- services home, no trust-row", async () => {
    const { HomeView } = await import("@/components/views/HomeView");
    const { container } = render(createElement(HomeView, { slug: "demo-orbit" }));
    await waitFor(() => expect(screen.getByText("Categorias")).toBeTruthy());
    expect(screen.getAllByText("Ver servicos").length).toBeGreaterThan(0);
    expect(container.innerHTML).not.toContain("Ver catalogo");
    expect(container.querySelector(TRUST_ROW)).toBeNull();
    expect(container.innerHTML).not.toContain("PIX");
  });

  it("ZERO-REGRESSION: seeded demo-acme (retail) is unchanged -- retail home + trust-row", async () => {
    const { HomeView } = await import("@/components/views/HomeView");
    const { container } = render(createElement(HomeView, { slug: "demo-acme" }));
    await waitFor(() => expect(screen.getByText("Categorias")).toBeTruthy());
    expect(screen.getAllByText("Ver catalogo").length).toBeGreaterThan(0);
    expect(container.innerHTML).not.toContain("Ver servicos");
    expect(container.querySelector(TRUST_ROW)).not.toBeNull();
    expect(container.innerHTML).toContain("12x sem juros");
  });
});
