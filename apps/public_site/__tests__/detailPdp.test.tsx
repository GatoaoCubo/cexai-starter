import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { createElement } from "react";

// ----------------------------------------------------------------------------
// DetailView (PDP) -- the richer product page, driven through PublicApiClient (fixtures
// mode). These assert BOTH the storefront content AND the security invariants on the PDP:
//   * the gallery + price + description + specs render from the OPEN sample payload;
//   * the gallery renders ONLY safe-scheme images (the sample uses data:image URIs);
//   * the published dual face is present and its human_html is NOT injected into the live
//     DOM (it lives only in a sandboxed iframe -- re-asserted at the page level);
//   * an unsafe payload field never leaks into a src/href.
//
// config.ts reads NEXT_PUBLIC_* once at import -> import the view FRESH in fixtures mode.
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

async function loadDetail() {
  const detail = await import("@/components/views/DetailView");
  const fx = await import("@/lib/fixtures");
  return {
    DetailView: detail.DetailView,
    SAMPLE_SLUG: fx.SAMPLE_SLUG,
    ORBIT_SLUG: fx.ORBIT_SLUG,
  };
}

/** Collect every <img> src in a rendered container. */
function imgSrcs(container: HTMLElement): string[] {
  return Array.from(container.querySelectorAll("img")).map((i) => i.getAttribute("src") ?? "");
}

describe("DetailView (PDP) -- rich storefront product page", () => {
  it("renders gallery + price + description + specs for the sample listing", async () => {
    const { DetailView, SAMPLE_SLUG } = await loadDetail();
    const { container } = render(
      createElement(DetailView, {
        slug: SAMPLE_SLUG,
        kind: "marketplace_listing",
        id: "ml_sample_0001",
      }),
    );

    // title + price render (the title appears twice: the breadcrumb + the <h1>).
    await waitFor(() =>
      expect(screen.getAllByText(/Arranhador Torre para Gatos/).length).toBeGreaterThan(0),
    );
    expect(screen.getByText("R$ 199,00")).toBeTruthy();

    // the description block renders (long body, as text).
    expect(screen.getByText(/base reforcada antiderrapante e poste de sisal/)).toBeTruthy();

    // the specs block renders its labels + values.
    expect(screen.getByText("Especificacoes")).toBeTruthy();
    expect(screen.getByText("Material")).toBeTruthy();
    expect(screen.getByText(/Sisal substituivel \+ MDF reforcado/)).toBeTruthy();
    expect(screen.getByText("Peso suportado")).toBeTruthy();

    // the gallery rendered images -- ALL are safe data:image URIs (sample fixtures).
    const imgs = Array.from(container.querySelectorAll("img"));
    const galleryImgs = imgs.filter((i) => (i.getAttribute("src") ?? "").startsWith("data:image/"));
    expect(galleryImgs.length).toBeGreaterThan(0);
    // SECURITY: not one rendered <img> carries an unsafe scheme.
    for (const i of imgs) {
      const src = i.getAttribute("src") ?? "";
      expect(src.startsWith("javascript:")).toBe(false);
      expect(src.startsWith("http://")).toBe(false);
      expect(src.startsWith("data:text/html")).toBe(false);
      expect(src.startsWith("file:")).toBe(false);
    }
  });

  it("HONEST-EMPTY: a listing without rating/reviews renders NO rating row + NO sticky bar", async () => {
    const { DetailView, SAMPLE_SLUG } = await loadDetail();
    const { container } = render(
      createElement(DetailView, {
        slug: SAMPLE_SLUG,
        kind: "marketplace_listing",
        id: "ml_sample_0001", // sample listing carries NO rating + NO buy_url
      }),
    );
    await waitFor(() =>
      expect(screen.getAllByText(/Arranhador Torre para Gatos/).length).toBeGreaterThan(0),
    );
    // no fabricated rating affordance, no review count, no verified badge.
    expect(screen.queryByText("verificado")).toBeNull();
    expect(container.textContent).not.toContain("avaliacoes");
    // no buy_url on this item -> no mobile sticky buy bar.
    expect(container.querySelector('[data-testid="mobile-buy-bar"]')).toBeNull();
  });

  it("renders rating + verified + reviews band + mobile sticky CTA when the payload carries them", async () => {
    const { DetailView, SAMPLE_SLUG } = await loadDetail();
    const { container } = render(
      createElement(DetailView, {
        slug: SAMPLE_SLUG,
        kind: "marketplace_listing",
        id: "ml_sample_0004", // sample listing WITH rating + reviews + https buy_url
      }),
    );
    await waitFor(() =>
      expect(screen.getAllByText(/Fonte de Agua para Gatos/).length).toBeGreaterThan(0),
    );
    // rating row: value + count + verified badge (status green, not brand teal).
    expect(screen.getByText("4.7")).toBeTruthy();
    expect(screen.getByText("verificado")).toBeTruthy();
    expect(container.innerHTML).toContain("text-success");
    // reviews band rendered from the explicit reviews_list.
    expect(screen.getByText(/O que dizem/)).toBeTruthy();
    expect(screen.getByText(/Cliente A \(amostra\)/)).toBeTruthy();
    // the mobile sticky buy bar exists, links to the external https buy_url, rel-hardened.
    const bar = container.querySelector('[data-testid="mobile-buy-bar"]');
    expect(bar).not.toBeNull();
    const barLink = bar!.querySelector("a") as HTMLAnchorElement;
    expect(barLink.getAttribute("href")).toBe("https://example.com/amostra/fonte-de-agua");
    expect(barLink.getAttribute("rel")).toBe("noopener noreferrer nofollow");
    // SECURITY re-assert: no unsafe scheme reached any src on the page.
    for (const img of Array.from(container.querySelectorAll("img"))) {
      const src = img.getAttribute("src") ?? "";
      expect(src.startsWith("javascript:")).toBe(false);
      expect(src.startsWith("http://")).toBe(false);
      expect(src.startsWith("data:text/html")).toBe(false);
    }
  });

  it("re-asserts the no-leak: a known slug + a non-existent id -> NotFound", async () => {
    const { DetailView, SAMPLE_SLUG } = await loadDetail();
    render(
      createElement(DetailView, {
        slug: SAMPLE_SLUG,
        kind: "marketplace_listing",
        id: "ghost_id",
      }),
    );
    await waitFor(() => expect(screen.getByText("Nada por aqui")).toBeTruthy());
  });

  it("renders the product_ad PDP and keeps human_html OUT of the live DOM (sandbox only)", async () => {
    const { DetailView, SAMPLE_SLUG } = await loadDetail();
    const { container } = render(
      createElement(DetailView, {
        slug: SAMPLE_SLUG,
        kind: "product_ad",
        id: "ad_sample_0001",
      }),
    );

    await waitFor(() =>
      expect(screen.getAllByText(/Torre que aguenta gato de 8kg/).length).toBeGreaterThan(0),
    );
    // the dual face affordance for the tenant-authored HTML is present...
    expect(screen.getByText(/versao publicada/i)).toBeTruthy();
    // ...but the tenant <h1> from human_html is NOT injected into the live DOM (it lives
    // only inside the sandboxed iframe's srcDoc, which jsdom does not parse into parent).
    expect(container.innerHTML).not.toContain("<h1>Anuncio (amostra)</h1>");
    // and the internal scaffold marker never leaks to a visitor.
    expect(container.innerHTML).not.toContain("generation_pending");
  });

  // ROUND 2 FIX 2 -- the PDP per-view cat-leak blind spot. The earlier PDP tests only
  // covered the demo-acme sample; the demo-orbit PDP (no safe gallery -> the placeholder)
  // was leaking /images/cat-product.jpg. These pin BOTH faces of the imageryFor() branch.
  it("NO CAT LEAK on the demo-orbit PDP: the no-image placeholder is a brand-gradient (no cat photo)", async () => {
    const { DetailView, ORBIT_SLUG } = await loadDetail();
    const { container } = render(
      createElement(DetailView, {
        slug: ORBIT_SLUG,
        kind: "service",
        id: "svc_orbit_0001",
      }),
    );
    await waitFor(() =>
      expect(screen.getAllByText(/Manutencao de Micro/).length).toBeGreaterThan(0),
    );
    // not one rendered <img> points at a first-party cat photo.
    for (const s of imgSrcs(container)) {
      expect(s.includes("/images/cat-")).toBe(false);
    }
    // the placeholder is the white-label brand-gradient tile (brand token, not a photo).
    expect(container.innerHTML).toContain("hsl(var(--brand))");
    // NO false-commerce claim on a services tenant: the BR-commerce TrustRow (PIX / 12x /
    // Compra / Troca) is suppressed on the service PDP, same guard as Home + Footer.
    expect(container.innerHTML).not.toContain("PIX");
    expect(container.innerHTML).not.toContain("Compra 100%");
  });

  it("ZERO-REGRESSION: the demo-acme PDP placeholder still uses the first-party cat fallback", async () => {
    const { DetailView, SAMPLE_SLUG } = await loadDetail();
    // ad_sample_0001 (demo-acme product_ad) carries NO gallery image -> the no-safe-image
    // placeholder renders. demo-acme ships photos, so the placeholder MUST still be the
    // first-party /images/cat-product.jpg tile (byte-identical to before this fix).
    const { container } = render(
      createElement(DetailView, {
        slug: SAMPLE_SLUG,
        kind: "product_ad",
        id: "ad_sample_0001",
      }),
    );
    await waitFor(() =>
      expect(screen.getAllByText(/Torre que aguenta gato de 8kg/).length).toBeGreaterThan(0),
    );
    // the first-party cat-product fallback IS still used for the photo tenant.
    expect(imgSrcs(container).some((s) => s === "/images/cat-product.jpg")).toBe(true);
    // ZERO-REGRESSION: the retail PDP STILL shows the BR-commerce trust row.
    expect(container.innerHTML).toContain("PIX");
  });
});
