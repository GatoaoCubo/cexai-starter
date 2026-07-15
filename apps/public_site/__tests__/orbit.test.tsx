import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { createElement } from "react";

// ----------------------------------------------------------------------------
// ORBIT TECH -- the SECOND tenant (P0-A rebrand: fictitious "Orbit Tech", formerly a
// real-brand fixture). The white-label flywheel proof: /t/demo-orbit renders the FULL
// storefront in Orbit Tech's identity (BLUE primary + RED highlight, IT-services vertical,
// its logo + partners + testimonials), from the SAME code, while /t/demo-acme stays
// UNCHANGED (cats + violet). These tests assert:
//   * the ORBIT TECH brand reskins via buildCssVars (blue --brand / --primary, red --
//     highlight, the tech radius) -- the reskin keystone fires for a totally different brand;
//   * the home renders Orbit Tech's SERVICE cards (no price, no fake buy), the logo, the
//     partners row, the about-stats, and the testimonials (flagged amostra);
//   * the IMAGERY FALLBACK has NO cat leak: not one Orbit Tech <img> points at "/images/
//     cat-*"; the hero/section/card art is the brand-gradient treatment, the only photos
//     are the committed Orbit Tech logo + partner logos;
//   * SECURITY re-asserted: every Orbit Tech <img> src is a safe shape (committed same-
//     origin "/images/..." OR https:/data:image), never an unsafe scheme;
//   * ZERO-REGRESSION: /t/demo-acme still renders cats + the violet token (unchanged).
//
// config.ts reads NEXT_PUBLIC_* once at import, so views are imported FRESH in fixtures
// mode (vi.resetModules + dynamic import after setting env), mirroring degrade.test.tsx.
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
  const fx = await import("@/lib/fixtures");
  return {
    HomeView: home.HomeView,
    CatalogView: catalog.CatalogView,
    AboutView: about.AboutView,
    SAMPLE_SLUG: fx.SAMPLE_SLUG,
    ORBIT_SLUG: fx.ORBIT_SLUG,
  };
}

/** Collect every <img> src in a rendered container. */
function imgSrcs(container: HTMLElement): string[] {
  return Array.from(container.querySelectorAll("img")).map((i) => i.getAttribute("src") ?? "");
}

describe("Orbit Tech home -- the white-label reskin (blue/red brand + IT services)", () => {
  it("reskins via buildCssVars: blue --brand/--primary + red --highlight + tech radius", async () => {
    const { HomeView, ORBIT_SLUG } = await loadViews();
    const { container } = render(createElement(HomeView, { slug: ORBIT_SLUG }));
    await waitFor(() => expect(screen.getByText("Categorias")).toBeTruthy());
    const style = container.querySelector("style");
    expect(style).not.toBeNull();
    const css = style!.textContent ?? "";
    // the BLUE brand tokens (royal blue 231 48% 48%) reached :root.
    expect(css).toContain("--brand:231 48% 48%");
    expect(css).toContain("--primary:231 48% 48%");
    // the RED highlight (4 90% 58%).
    expect(css).toContain("--highlight:4 90% 58%");
    // the tech radius.
    expect(css).toContain("--radius:0.625rem");
    // it is NOT the built-in sample's violet -- the reskin actually changed the palette.
    expect(css).not.toContain("258 60% 45%");
  });

  it("renders the brand name, the committed logo, and the SERVICE vertical CTA", async () => {
    const { HomeView, ORBIT_SLUG } = await loadViews();
    const { container } = render(createElement(HomeView, { slug: ORBIT_SLUG }));
    await waitFor(() => expect(screen.getByText("Categorias")).toBeTruthy());
    // the brand name renders.
    expect(screen.getAllByText("Orbit Tech").length).toBeGreaterThan(0);
    // the committed same-origin logo renders as an <img>.
    const logo = imgSrcs(container).find((s) => s.includes("/images/tenants/demo-orbit/logo.png"));
    expect(logo).toBeTruthy();
    // the service-vertical hero CTA ("Ver servicos", not "Ver catalogo").
    expect(screen.getAllByText("Ver servicos").length).toBeGreaterThan(0);
    expect(container.innerHTML).not.toContain("Ver catalogo");
  });

  it("renders SERVICE cards (title + WhatsApp CTA), no price, no fake checkout", async () => {
    const { HomeView, ORBIT_SLUG } = await loadViews();
    const { container } = render(createElement(HomeView, { slug: ORBIT_SLUG }));
    await waitFor(() => expect(screen.getByText("Categorias")).toBeTruthy());
    // a couple of the real services render in the home featured strip (first 3).
    expect(screen.getAllByText("Manutencao de Micro").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Reparo de Notebooks").length).toBeGreaterThan(0);
    // the WhatsApp CTA points at the brand's own fictitious channel (scheme-safe https).
    const wa = Array.from(container.querySelectorAll("a")).find((a) =>
      (a.getAttribute("href") ?? "").includes("api.whatsapp.com"),
    );
    expect(wa).toBeTruthy();
    expect(wa!.getAttribute("href")!.startsWith("https://")).toBe(true);
    // NO product price string leaks into the service surface (services have no price).
    expect(container.innerHTML).not.toContain("R$");
  });

  it("renders the PARTNERS row, the ABOUT-stats, and the TESTIMONIALS (flagged amostra)", async () => {
    const { HomeView, ORBIT_SLUG } = await loadViews();
    const { container } = render(createElement(HomeView, { slug: ORBIT_SLUG }));
    await waitFor(() => expect(screen.getByText("Categorias")).toBeTruthy());
    // partner logos (committed same-origin paths).
    const partners = imgSrcs(container).filter((s) => s.includes("/images/tenants/demo-orbit/partner-"));
    expect(partners.length).toBe(3);
    // the about-stats real numbers.
    expect(screen.getByText("+20 anos")).toBeTruthy();
    expect(screen.getByText("+10 mil")).toBeTruthy();
    // a fictitious testimonial author + the honest "amostra" flag on the testimonials.
    expect(screen.getByText("Fernanda Rocha (amostra)")).toBeTruthy();
    expect(screen.getAllByText("amostra").length).toBeGreaterThan(0);
    // social proof (Google 4.6 / 68).
    expect(screen.getByText("4.6")).toBeTruthy();
    expect(screen.getByText(/68 avaliacoes/)).toBeTruthy();
  });

  it("NO CAT LEAK: not one Orbit Tech <img> points at a cat photo; imagery is brand-gradient", async () => {
    const { HomeView, ORBIT_SLUG } = await loadViews();
    const { container } = render(createElement(HomeView, { slug: ORBIT_SLUG }));
    await waitFor(() => expect(screen.getByText("Categorias")).toBeTruthy());
    const srcs = imgSrcs(container);
    // NOT ONE cat photo (the deferred white-label gap is closed).
    for (const s of srcs) {
      expect(s.includes("/images/cat-")).toBe(false);
    }
    // the only photos are Orbit Tech's own committed assets (logo + partners).
    for (const s of srcs) {
      const ok = s.includes("/images/tenants/demo-orbit/");
      expect(ok).toBe(true);
    }
    // the brand-gradient hero uses the brand token (no cat-hero photo at all).
    expect(container.innerHTML).toContain("hsl(var(--brand))");
  });

  it("SECURITY: every Orbit Tech <img> src is a safe shape (no unsafe scheme leaks)", async () => {
    const { HomeView, ORBIT_SLUG } = await loadViews();
    const { container } = render(createElement(HomeView, { slug: ORBIT_SLUG }));
    await waitFor(() => expect(screen.getByText("Categorias")).toBeTruthy());
    for (const s of imgSrcs(container)) {
      expect(s.startsWith("javascript:")).toBe(false);
      expect(s.startsWith("http://")).toBe(false);
      expect(s.startsWith("data:text/html")).toBe(false);
      expect(s.startsWith("file:")).toBe(false);
      const ok = s.startsWith("/images/") || s.startsWith("https://") || s.startsWith("data:image/");
      expect(ok).toBe(true);
    }
  });

  // ROUND 2 -- the 3 runtime-proved leaks (icon / copy / nav). The earlier tests only
  // checked cat PHOTOS; these pin the icon-glyph, the false-commerce copy, and the nav.
  it("NO CAT ICON: the home contains no CatIcon path (M12 5 8.5 3) -- the 3rd pillar is neutral", async () => {
    const { HomeView, ORBIT_SLUG } = await loadViews();
    const { container } = render(createElement(HomeView, { slug: ORBIT_SLUG }));
    await waitFor(() => expect(screen.getByText("Categorias")).toBeTruthy());
    // the distinctive CatIcon ear path must NOT appear anywhere in the rendered SVG.
    expect(container.innerHTML).not.toContain("M12 5 8.5 3");
    // and the "feito com cuidado" pillar still renders (with the neutral heart glyph).
    expect(screen.getByText("Feito com cuidado")).toBeTruthy();
  });

  it("NO FALSE COMMERCE: a services tenant home shows no PIX/parcelamento/compra claim", async () => {
    const { HomeView, ORBIT_SLUG } = await loadViews();
    const { container } = render(createElement(HomeView, { slug: ORBIT_SLUG }));
    await waitFor(() => expect(screen.getByText("Categorias")).toBeTruthy());
    const html = container.innerHTML;
    expect(html).not.toContain("PIX");
    expect(html).not.toContain("parcelamento");
    expect(html).not.toContain("compra");
    // the vertical-aware support pillar replaces the checkout pillar.
    expect(screen.getByText("Atendimento humanizado")).toBeTruthy();
  });

  // ROUND 3: demo-orbit now has the sections that FIT its business -- a TECH blog + a
  // "Para Empresas" corporate area -- with its OWN content. So the chrome SHOWS Blog +
  // "Para Empresas" (NOT the retail "B2B" / "Anuncios" labels), plus a Loja external link.
  it("CHROME: the demo-orbit nav has Blog + 'Para Empresas' links + a Loja external link", async () => {
    const { HomeView, ORBIT_SLUG } = await loadViews();
    const { container } = render(createElement(HomeView, { slug: ORBIT_SLUG }));
    await waitFor(() => expect(screen.getByText("Categorias")).toBeTruthy());
    const anchors = Array.from(container.querySelectorAll("a"));
    const hrefs = anchors.map((a) => a.getAttribute("href") ?? "");
    // the Blog + b2b (Para Empresas) area links ARE present now.
    expect(hrefs.some((h) => h.endsWith("/t/demo-orbit/blog"))).toBe(true);
    expect(hrefs.some((h) => h.endsWith("/t/demo-orbit/b2b"))).toBe(true);
    // the b2b LABEL is "Para Empresas" (services), NOT the retail "B2B".
    expect(screen.getAllByText("Para Empresas").length).toBeGreaterThan(0);
    expect(screen.queryByText("B2B")).toBeNull();
    // "Anuncios" stays retail-only (demo-orbit publicKinds = [service]).
    expect(screen.queryByText("Anuncios")).toBeNull();
    // a Loja external link -> loja.orbittech.com.br, https-only + rel-hardened.
    const loja = anchors.find((a) => (a.getAttribute("href") ?? "").includes("loja.orbittech.com.br"));
    expect(loja).toBeTruthy();
    expect(loja!.getAttribute("href")!.startsWith("https://")).toBe(true);
    expect(loja!.getAttribute("rel")).toContain("nofollow");
  });
});

describe("Orbit Tech catalog -- the service vertical page", () => {
  it("renders the SERVICE cards on the /service catalog page (no price, WhatsApp CTA)", async () => {
    const { CatalogView, ORBIT_SLUG } = await loadViews();
    const { container } = render(
      createElement(CatalogView, { slug: ORBIT_SLUG, kind: "service" }),
    );
    await waitFor(() => expect(screen.getByText("Reparo de Notebooks")).toBeTruthy());
    // the page eyebrow is the service vertical, the count label is "servicos".
    expect(screen.getAllByText("Servicos").length).toBeGreaterThan(0);
    expect(screen.getByText(/servicos publicados/)).toBeTruthy();
    // no cat fallback tile leaks (services carry no image -> brand-treatment card, no img).
    for (const s of imgSrcs(container)) {
      expect(s.includes("/images/cat-")).toBe(false);
    }
  });
});

describe("Orbit Tech about -- brand identity reskinned", () => {
  it("renders the Orbit Tech about page with its name + the Servicos CTA link", async () => {
    const { AboutView, ORBIT_SLUG } = await loadViews();
    const { container } = render(createElement(AboutView, { slug: ORBIT_SLUG }));
    await waitFor(() => expect(screen.getByText("Sobre este catalogo")).toBeTruthy());
    expect(screen.getAllByText("Orbit Tech").length).toBeGreaterThan(0);
    // the about CTA links to the SERVICE kind (the tenant's own vertical), not cat kinds.
    const hrefs = Array.from(container.querySelectorAll("a")).map((a) => a.getAttribute("href") ?? "");
    expect(hrefs.some((h) => h.endsWith("/t/demo-orbit/service"))).toBe(true);
    expect(hrefs.some((h) => h.endsWith("/t/demo-orbit/marketplace_listing"))).toBe(false);
  });
});

describe("ZERO-REGRESSION: demo-acme is unchanged (cats + violet)", () => {
  it("demo-acme still paints the built-in sample brand token + cat hero photo (unchanged)", async () => {
    const { HomeView, SAMPLE_SLUG } = await loadViews();
    const { container } = render(createElement(HomeView, { slug: SAMPLE_SLUG }));
    await waitFor(() => expect(screen.getByText("Categorias")).toBeTruthy());
    const css = container.querySelector("style")!.textContent ?? "";
    // the built-in sample violet brand token is intact.
    expect(css).toContain("--brand:258 60% 45%");
    // demo-acme STILL ships its first-party cat photos (the photo treatment).
    const hasCat = imgSrcs(container).some((s) => s.startsWith("/images/cat-"));
    expect(hasCat).toBe(true);
    // ZERO-REGRESSION on the ICON: the retail vitrine 3rd pillar paints the CatIcon again
    // (the distinctive ear path), exactly as before the white-label reskin.
    expect(container.innerHTML).toContain("M12 5 8.5 3");
    // and it still shows the product vertical CTA + nav (not the services vertical).
    expect(screen.getAllByText("Ver catalogo").length).toBeGreaterThan(0);
    expect(container.innerHTML).not.toContain("Ver servicos");
  });

  it("demo-acme nav still shows the product kinds (Catalogo/Anuncios), not Servicos", async () => {
    const { HomeView, SAMPLE_SLUG } = await loadViews();
    render(createElement(HomeView, { slug: SAMPLE_SLUG }));
    await waitFor(() => expect(screen.getByText("Categorias")).toBeTruthy());
    expect(screen.getAllByText("Catalogo").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Anuncios").length).toBeGreaterThan(0);
  });
});
