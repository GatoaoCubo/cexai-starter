import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { createElement } from "react";
import { tenantSectionsFor, DEFAULT_SECTIONS } from "@/lib/tenantSections";

// ----------------------------------------------------------------------------
// tenantSections -- ROUND 3: each tenant has the sections that FIT ITS business, with ITS
// OWN content (not OFF, not cat content):
//   * a SERVICES tenant (demo-orbit, fictitious "Orbit Tech") offers a TECH blog + a
//     "Para Empresas" corporate area -> the nav SHOWS Blog + "Para Empresas" links,
//     BlogView/B2BView render ORBIT TECH'S OWN content (tech posts + corporate offers),
//     and there is NO cat/atacado leak;
//   * the DEFAULT (demo-acme + any unknown slug) keeps the built-in retail sections (blog +
//     b2b ON, label "B2B") -> demo-acme's cat blog + pet wholesale are UNCHANGED.
//
// config.ts reads NEXT_PUBLIC_* once at import -> import each view FRESH in fixtures mode.
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

async function load() {
  const blog = await import("@/components/views/BlogView");
  const post = await import("@/components/views/BlogPostView");
  const b2b = await import("@/components/views/B2BView");
  const fx = await import("@/lib/fixtures");
  const sc = await import("@/lib/storeContent");
  return {
    BlogView: blog.BlogView,
    BlogPostView: post.BlogPostView,
    B2BView: b2b.B2BView,
    SAMPLE_SLUG: fx.SAMPLE_SLUG,
    ORBIT_SLUG: fx.ORBIT_SLUG,
    SAMPLE_BLOG_POSTS: sc.SAMPLE_BLOG_POSTS,
    ORBIT_BLOG_POSTS: sc.ORBIT_BLOG_POSTS,
  };
}

/** The cat/pet-vertical leak markers a services surface must NEVER contain. */
const GATO_MARKERS = /gato|felin|arranhad|ronron|atacado|Revenda(?!\b.*nao)/i;

describe("tenantSectionsFor -- the per-tenant nav/sections + LABEL resolver", () => {
  it("demo-orbit (services) has blog + b2b ON, with the 'Para Empresas' b2b label", () => {
    expect(tenantSectionsFor("demo-orbit")).toEqual({
      blog: true,
      b2b: true,
      b2bLabel: "Para Empresas",
      blogLabel: "Blog",
    });
  });

  it("an unknown slug + demo-acme fall back to the DEFAULT retail sections ('B2B' label)", () => {
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

describe("demo-orbit BLOG -- renders TECH posts, no cat content", () => {
  it("BlogView(demo-orbit) renders the tech posts (flagged amostra), no cat leak", async () => {
    const { BlogView, ORBIT_SLUG, ORBIT_BLOG_POSTS } = await load();
    const { container } = render(createElement(BlogView, { slug: ORBIT_SLUG }));
    await waitFor(() =>
      expect(screen.getAllByText(/amostra -- dados simulados/i).length).toBeGreaterThan(0),
    );
    // a tech post title renders (the Ransomware featured post).
    expect(
      screen.getByText("Ransomware: 5 habitos que protegem o seu PC"),
    ).toBeTruthy();
    // a second tech post renders too.
    expect(ORBIT_BLOG_POSTS.length).toBe(5);
    // NO cat content leaks into the services blog.
    expect(GATO_MARKERS.test(container.innerHTML)).toBe(false);
    // NO cat photo cover -- demo-orbit is imagery mode "brand" (gradient tiles only).
    const imgs = Array.from(container.querySelectorAll("img")).map((i) => i.getAttribute("src") ?? "");
    for (const s of imgs) expect(s.includes("/images/cat-")).toBe(false);
  });

  it("BlogPostView(demo-orbit, <tech post>) renders that article body, no cat leak", async () => {
    const { BlogPostView, ORBIT_SLUG, ORBIT_BLOG_POSTS } = await load();
    const target = ORBIT_BLOG_POSTS[0];
    const { container } = render(
      createElement(BlogPostView, { slug: ORBIT_SLUG, post: target.slug }),
    );
    await waitFor(() => expect(screen.getByText(target.title)).toBeTruthy());
    expect(screen.getByText(target.body[0])).toBeTruthy();
    expect(GATO_MARKERS.test(container.innerHTML)).toBe(false);
  });

  it("BlogPostView(demo-orbit, <a CAT post slug>) -> NotFound (no cross-tenant leak)", async () => {
    const { BlogPostView, ORBIT_SLUG, SAMPLE_BLOG_POSTS } = await load();
    const catPost = SAMPLE_BLOG_POSTS[0].slug; // a demo-acme cat-post slug
    const { container } = render(
      createElement(BlogPostView, { slug: ORBIT_SLUG, post: catPost }),
    );
    await waitFor(() => expect(screen.getByText("Nada por aqui")).toBeTruthy());
    expect(GATO_MARKERS.test(container.innerHTML)).toBe(false);
  });
});

describe("demo-orbit B2B -- renders 'Para Empresas' corporate content, no atacado", () => {
  it("B2BView(demo-orbit) renders corporate offers + WhatsApp CTA, no atacado/Revenda", async () => {
    const { B2BView, ORBIT_SLUG } = await load();
    const { container } = render(createElement(B2BView, { slug: ORBIT_SLUG }));
    await waitFor(() => expect(screen.getByText("Orbit Tech para Empresas")).toBeTruthy());
    // a corporate offer renders.
    expect(screen.getByText("Contrato de manutencao mensal")).toBeTruthy();
    // the who-we-serve line.
    expect(screen.getByText(/contabilidade/)).toBeTruthy();
    // the CTA points at the brand's own fictitious WhatsApp channel (scheme-safe https), rel-hardened.
    const wa = Array.from(container.querySelectorAll("a")).find((a) =>
      (a.getAttribute("href") ?? "").includes("api.whatsapp.com"),
    );
    expect(wa).toBeTruthy();
    expect(wa!.getAttribute("href")!.startsWith("https://")).toBe(true);
    expect(wa!.getAttribute("rel")).toContain("noopener");
    // NO atacado / wholesale / Revenda / Distribuidor / pet copy.
    expect(GATO_MARKERS.test(container.innerHTML)).toBe(false);
    expect(container.innerHTML).not.toContain("Distribuidor");
    // SCOPE BOUNDARY: no fake checkout.
    const html = container.innerHTML.toLowerCase();
    expect(html).not.toContain("finalizar compra");
    expect(html).not.toContain("checkout");
  });

  it("the corporate area flags its sample content amostra", async () => {
    const { B2BView, ORBIT_SLUG } = await load();
    render(createElement(B2BView, { slug: ORBIT_SLUG }));
    await waitFor(() => expect(screen.getByText("Orbit Tech para Empresas")).toBeTruthy());
    expect(screen.getAllByText(/amostra/i).length).toBeGreaterThan(0);
  });
});

describe("demo-orbit CHROME -- Servicos / Blog / Para Empresas + Loja external link", () => {
  it("the demo-orbit nav shows Blog + 'Para Empresas' links and a https Loja link", async () => {
    const { BlogView, ORBIT_SLUG } = await load();
    const { container } = render(createElement(BlogView, { slug: ORBIT_SLUG }));
    await waitFor(() =>
      expect(screen.getAllByText(/amostra -- dados simulados/i).length).toBeGreaterThan(0),
    );
    const anchors = Array.from(container.querySelectorAll("a"));
    const hrefs = anchors.map((a) => a.getAttribute("href") ?? "");
    // Servicos (the publicKind), Blog, and the b2b area links are present.
    expect(hrefs.some((h) => h.endsWith("/t/demo-orbit/service"))).toBe(true);
    expect(hrefs.some((h) => h.endsWith("/t/demo-orbit/blog"))).toBe(true);
    expect(hrefs.some((h) => h.endsWith("/t/demo-orbit/b2b"))).toBe(true);
    // the b2b nav LABEL is "Para Empresas" (services), not the retail "B2B".
    expect(screen.getAllByText("Para Empresas").length).toBeGreaterThan(0);
    // the Loja external link -> loja.orbittech.com.br, https-only + rel-hardened.
    const loja = anchors.find((a) => (a.getAttribute("href") ?? "").includes("loja.orbittech.com.br"));
    expect(loja).toBeTruthy();
    expect(loja!.getAttribute("href")!.startsWith("https://")).toBe(true);
    expect(loja!.getAttribute("rel")).toContain("nofollow");
    expect(loja!.getAttribute("rel")).toContain("noopener");
  });
});

describe("ZERO-REGRESSION: demo-acme keeps its retail blog + b2b (cat content unchanged)", () => {
  it("BlogView(demo-acme) still renders the sample cat posts (blog stays ON)", async () => {
    const { BlogView, SAMPLE_SLUG, SAMPLE_BLOG_POSTS } = await load();
    const { container } = render(createElement(BlogView, { slug: SAMPLE_SLUG }));
    await waitFor(() =>
      expect(screen.getAllByText(/amostra -- dados simulados/i).length).toBeGreaterThan(0),
    );
    expect(screen.getByText(SAMPLE_BLOG_POSTS[0].title)).toBeTruthy();
    // demo-acme is the cat tenant -> its blog DOES carry the cat markers (unchanged).
    expect(GATO_MARKERS.test(container.innerHTML)).toBe(true);
  });

  it("B2BView(demo-acme) still renders the wholesale program (b2b stays ON)", async () => {
    const { B2BView, SAMPLE_SLUG } = await load();
    const { container } = render(createElement(B2BView, { slug: SAMPLE_SLUG }));
    await waitFor(() => expect(screen.getByText("O que voce ganha")).toBeTruthy());
    // the Revenda/Distribuidor tiers still render for the retail tenant (unchanged).
    expect(screen.getByText("Distribuidor")).toBeTruthy();
    expect(GATO_MARKERS.test(container.innerHTML)).toBe(true);
  });

  it("demo-acme chrome STILL shows the Blog + B2B nav links + NO Loja link (retail unchanged)", async () => {
    const { BlogView, SAMPLE_SLUG } = await load();
    const { container } = render(createElement(BlogView, { slug: SAMPLE_SLUG }));
    await waitFor(() =>
      expect(screen.getAllByText(/amostra -- dados simulados/i).length).toBeGreaterThan(0),
    );
    const anchors = Array.from(container.querySelectorAll("a"));
    const hrefs = anchors.map((a) => a.getAttribute("href") ?? "");
    expect(hrefs.some((h) => h.endsWith("/t/demo-acme/blog"))).toBe(true);
    expect(hrefs.some((h) => h.endsWith("/t/demo-acme/b2b"))).toBe(true);
    // the b2b label stays "B2B" for the retail tenant.
    expect(screen.getAllByText("B2B").length).toBeGreaterThan(0);
    // demo-acme has NO external Loja link (zero-regression -- the link is opt-in).
    expect(hrefs.some((h) => h.includes("loja.orbittech.com.br"))).toBe(false);
  });
});
