import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { createElement } from "react";

// ----------------------------------------------------------------------------
// DEGRADE-NEVER + NO-LEAK at the page level (fixtures mode). These drive the real
// client views through PublicApiClient (fixtures branch) and assert the security
// keystone + the degrade behaviour across the WHOLE multi-page storefront:
//   * an unknown slug -> <NotFound/> ("Nada por aqui"), NEVER a crash, NEVER a
//     disclosure (the SAME view a non-public slug would render) -- on EVERY page
//     (home, catalog, PDP, about);
//   * a known slug + a kind with nothing published -> the branded empty shell
//     ("Nada publicado ainda"), NEVER a crash;
//   * a malformed slug -> <NotFound/> WITHOUT a fetch (defence-in-depth).
//
// config.ts reads NEXT_PUBLIC_* once at import, so the views are imported FRESH in
// fixtures mode (vi.resetModules + dynamic import after setting env).
// ----------------------------------------------------------------------------

const ORIGINAL_ENV = { ...process.env };

beforeEach(() => {
  vi.resetModules();
  process.env.NEXT_PUBLIC_FIXTURES = "1";
  delete process.env.NEXT_PUBLIC_API_URL;
});

afterEach(() => {
  vi.restoreAllMocks();
  process.env = { ...ORIGINAL_ENV };
});

async function loadViews() {
  const home = await import("@/components/views/HomeView");
  const catalog = await import("@/components/views/CatalogView");
  const about = await import("@/components/views/AboutView");
  const detail = await import("@/components/views/DetailView");
  const fx = await import("@/lib/fixtures");
  return {
    HomeView: home.HomeView,
    CatalogView: catalog.CatalogView,
    AboutView: about.AboutView,
    DetailView: detail.DetailView,
    SAMPLE_SLUG: fx.SAMPLE_SLUG,
  };
}

describe("HomeView -- branded storefront home + no-leak", () => {
  it("renders <NotFound/> for an unknown slug (no disclosure, no crash)", async () => {
    const { HomeView } = await loadViews();
    render(createElement(HomeView, { slug: "no-such-tenant" }));
    await waitFor(() => expect(screen.getByText("Nada por aqui")).toBeTruthy());
    // the unknown slug is NOT echoed back (it would confirm a guess).
    expect(screen.queryByText(/no-such-tenant/)).toBeNull();
  });

  it("renders <NotFound/> for a malformed slug WITHOUT crashing", async () => {
    const { HomeView } = await loadViews();
    render(createElement(HomeView, { slug: ".." }));
    await waitFor(() => expect(screen.getByText("Nada por aqui")).toBeTruthy());
  });

  it("renders the branded hero + section cards for the known sample slug", async () => {
    const { HomeView, SAMPLE_SLUG } = await loadViews();
    render(createElement(HomeView, { slug: SAMPLE_SLUG }));
    // the brand name renders in the hero (heading) and the category cards render the
    // configured PUBLIC_KINDS labels (no list-kinds fetch).
    await waitFor(() => expect(screen.getByText("Categorias")).toBeTruthy());
    expect(screen.getAllByText("Catalogo").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Anuncios").length).toBeGreaterThan(0);
    // the featured sample item title renders. The editorial hero now ALSO surfaces the
    // newest published item as a featured-product inset, so the title appears in BOTH the
    // hero inset and the featured strip -> assert at-least-one (not exactly-one).
    expect(screen.getAllByText(/Arranhador Torre para Gatos/).length).toBeGreaterThan(0);
    // the editorial hero inset (the asymmetric featured-product anchor) is present.
    expect(screen.getByText("Em destaque")).toBeTruthy();
  });

  it("WHITE-LABEL: the hero uses a first-party /images photo; pillars have no vertical leak", async () => {
    const { HomeView, SAMPLE_SLUG } = await loadViews();
    const { container } = render(createElement(HomeView, { slug: SAMPLE_SLUG }));
    await waitFor(() => expect(screen.getByText("Categorias")).toBeTruthy());
    // the hero backdrop is a same-origin /images photo (NOT tenant-payload media).
    const imgs = Array.from(container.querySelectorAll("img"));
    const heroPhoto = imgs.find((i) => (i.getAttribute("src") ?? "").startsWith("/images/"));
    expect(heroPhoto).toBeTruthy();
    // SECURITY (re-assert on the NEW hero featured-product inset): every rendered <img>
    // is either a first-party /images photo or a SAFE tenant-payload media src
    // (https:/data:image) -- the inset thumb is gated by isSafeMediaSrc just like the
    // cards + the gallery. Not one unsafe scheme leaks into a src.
    for (const i of imgs) {
      const src = i.getAttribute("src") ?? "";
      expect(src.startsWith("javascript:")).toBe(false);
      expect(src.startsWith("http://")).toBe(false);
      expect(src.startsWith("data:text/html")).toBe(false);
      expect(src.startsWith("file:")).toBe(false);
      const ok =
        src.startsWith("/images/") ||
        src.startsWith("https://") ||
        src.startsWith("data:image/");
      expect(ok).toBe(true);
    }
    // the value pillars are brand-agnostic editorial copy (derived from buildHomeCopy):
    // the pillar bodies must NOT carry the old hard-coded cat-vertical strings.
    expect(container.innerHTML).not.toContain("para o seu gato");
    expect(container.innerHTML).not.toContain("Pensado para felinos");
  });
});

describe("CatalogView -- branded empty shell + no-leak", () => {
  it("renders the branded empty shell for a known slug + an empty kind", async () => {
    const { CatalogView, SAMPLE_SLUG } = await loadViews();
    render(createElement(CatalogView, { slug: SAMPLE_SLUG, kind: "kind_with_no_rows" }));
    await waitFor(() => expect(screen.getByText("Nada publicado ainda")).toBeTruthy());
  });

  it("renders <NotFound/> for an unknown slug (no-leak)", async () => {
    const { CatalogView } = await loadViews();
    render(createElement(CatalogView, { slug: "no-such-tenant", kind: "marketplace_listing" }));
    await waitFor(() => expect(screen.getByText("Nada por aqui")).toBeTruthy());
  });

  it("renders the populated catalog for the known sample slug", async () => {
    const { CatalogView, SAMPLE_SLUG } = await loadViews();
    render(createElement(CatalogView, { slug: SAMPLE_SLUG, kind: "marketplace_listing" }));
    // the sample marketplace listing title renders (honest sample data).
    await waitFor(() =>
      expect(screen.getByText(/Arranhador Torre para Gatos/)).toBeTruthy(),
    );
  });
});

describe("AboutView -- brand identity + no-leak", () => {
  it("renders the brand about page for the known sample slug", async () => {
    const { AboutView, SAMPLE_SLUG } = await loadViews();
    render(createElement(AboutView, { slug: SAMPLE_SLUG }));
    await waitFor(() => expect(screen.getByText("Sobre este catalogo")).toBeTruthy());
    // the brand name renders (the heading); the honest transparency block is present.
    expect(screen.getByText("Transparencia")).toBeTruthy();
  });

  it("renders <NotFound/> for an unknown slug (no-leak)", async () => {
    const { AboutView } = await loadViews();
    render(createElement(AboutView, { slug: "no-such-tenant" }));
    await waitFor(() => expect(screen.getByText("Nada por aqui")).toBeTruthy());
  });

  it("renders <NotFound/> for a malformed slug WITHOUT crashing", async () => {
    const { AboutView } = await loadViews();
    render(createElement(AboutView, { slug: "../etc" }));
    await waitFor(() => expect(screen.getByText("Nada por aqui")).toBeTruthy());
  });
});

describe("DetailView (PDP) -- no-leak + degrade-to-list", () => {
  it("renders <NotFound/> for an unknown slug (no-leak)", async () => {
    const { DetailView } = await loadViews();
    render(
      createElement(DetailView, {
        slug: "no-such-tenant",
        kind: "marketplace_listing",
        id: "ml_sample_0001",
      }),
    );
    await waitFor(() => expect(screen.getByText("Nada por aqui")).toBeTruthy());
  });

  it("renders <NotFound/> for a known slug but an id that does not exist", async () => {
    const { DetailView, SAMPLE_SLUG } = await loadViews();
    render(
      createElement(DetailView, {
        slug: SAMPLE_SLUG,
        kind: "marketplace_listing",
        id: "does_not_exist",
      }),
    );
    await waitFor(() => expect(screen.getByText("Nada por aqui")).toBeTruthy());
  });
});
