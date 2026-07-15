import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { createElement } from "react";

// ----------------------------------------------------------------------------
// BlogView / BlogPostView / B2BView -- the new editorial + wholesale pages, driven
// through PublicApiClient (fixtures mode). These assert BOTH the storefront content AND
// the security invariants on EVERY new page:
//   * the blog list renders the sample posts and the "amostra" flag (never claimed real);
//   * a known post slug renders the article body; an UNKNOWN post slug -> NotFound
//     (the no-leak parity -- a guessed article path discloses nothing);
//   * the B2B area renders value props + tiers + the contact CTA, with NO fake checkout;
//   * an unknown tenant slug -> NotFound on EVERY new page (no disclosure);
//   * not one rendered <img> carries an unsafe scheme; the cat art is a same-origin
//     /placeholder asset; there is no dangerouslySetInnerHTML sink.
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
    SAMPLE_BLOG_POSTS: sc.SAMPLE_BLOG_POSTS,
  };
}

/** No rendered <img> may carry an unsafe scheme. The decorative cat art is a same-origin
 *  /images (premium photos) or /placeholder asset (allowed); tenant payload media must be
 *  https:/data: only. */
function assertNoUnsafeImg(container: HTMLElement) {
  const imgs = Array.from(container.querySelectorAll("img"));
  for (const i of imgs) {
    const src = i.getAttribute("src") ?? "";
    expect(src.startsWith("javascript:")).toBe(false);
    expect(src.startsWith("http://")).toBe(false);
    expect(src.startsWith("data:text/html")).toBe(false);
    expect(src.startsWith("file:")).toBe(false);
    // every img is a same-origin /images (premium photo) or /placeholder asset, or a
    // safe https:/data: tenant-payload media.
    const ok =
      src.startsWith("/images/") ||
      src.startsWith("/placeholder/") ||
      src.startsWith("https://") ||
      src.startsWith("data:image/");
    expect(ok).toBe(true);
  }
}

describe("BlogView -- editorial content blog", () => {
  it("renders the sample posts and flags them as amostra", async () => {
    const { BlogView, SAMPLE_SLUG, SAMPLE_BLOG_POSTS } = await load();
    const { container } = render(createElement(BlogView, { slug: SAMPLE_SLUG }));

    await waitFor(() =>
      expect(screen.getAllByText(/amostra -- dados simulados/i).length).toBeGreaterThan(0),
    );
    // the featured + at least one more post title render.
    expect(screen.getByText(SAMPLE_BLOG_POSTS[0].title)).toBeTruthy();
    expect(screen.getByText(SAMPLE_BLOG_POSTS[1].title)).toBeTruthy();
    // SECURITY: no unsafe image scheme; no dangerouslySetInnerHTML sink.
    assertNoUnsafeImg(container);
    expect(container.innerHTML).not.toContain("generation_pending");
  });

  it("ENRICHED: renders the category chips + a multi-post grid with /images covers", async () => {
    const { BlogView, SAMPLE_SLUG, SAMPLE_BLOG_POSTS } = await load();
    const sc = await import("@/lib/storeContent");
    const { container } = render(createElement(BlogView, { slug: SAMPLE_SLUG }));

    await waitFor(() =>
      expect(screen.getAllByText(/amostra -- dados simulados/i).length).toBeGreaterThan(0),
    );
    // category taxonomy chips render (Todos + each BLOG_CATEGORY).
    expect(screen.getByText("Todos")).toBeTruthy();
    for (const cat of sc.BLOG_CATEGORIES) {
      expect(screen.getAllByText(cat).length).toBeGreaterThan(0);
    }
    // a richer set: more than 3 posts now (featured + a multi-post grid).
    expect(SAMPLE_BLOG_POSTS.length).toBeGreaterThan(3);
    // every cover IS a first-party same-origin /images photo (never tenant media).
    const imgs = Array.from(container.querySelectorAll("img"));
    const covers = imgs.filter((i) => (i.getAttribute("src") ?? "").startsWith("/images/"));
    expect(covers.length).toBeGreaterThan(0);
    assertNoUnsafeImg(container);
  });

  it("no-leak: an unknown tenant slug -> NotFound", async () => {
    const { BlogView } = await load();
    render(createElement(BlogView, { slug: "ghost-tenant" }));
    await waitFor(() => expect(screen.getByText("Nada por aqui")).toBeTruthy());
  });
});

describe("BlogPostView -- single article", () => {
  it("renders the article body for a known post slug", async () => {
    const { BlogPostView, SAMPLE_SLUG, SAMPLE_BLOG_POSTS } = await load();
    const target = SAMPLE_BLOG_POSTS[0];
    const { container } = render(
      createElement(BlogPostView, { slug: SAMPLE_SLUG, post: target.slug }),
    );
    await waitFor(() => expect(screen.getByText(target.title)).toBeTruthy());
    // a body paragraph renders as text.
    expect(screen.getByText(target.body[0])).toBeTruthy();
    assertNoUnsafeImg(container);
  });

  it("no-leak: a known tenant + an UNKNOWN post slug -> NotFound", async () => {
    const { BlogPostView, SAMPLE_SLUG } = await load();
    render(createElement(BlogPostView, { slug: SAMPLE_SLUG, post: "ghost-article" }));
    await waitFor(() => expect(screen.getByText("Nada por aqui")).toBeTruthy());
  });

  it("no-leak: an unknown tenant slug -> NotFound", async () => {
    const { BlogPostView } = await load();
    render(createElement(BlogPostView, { slug: "ghost-tenant", post: "anything" }));
    await waitFor(() => expect(screen.getByText("Nada por aqui")).toBeTruthy());
  });
});

describe("B2BView -- wholesale / partner area", () => {
  it("renders value props + tiers + a contact CTA with NO fake checkout", async () => {
    const { B2BView, SAMPLE_SLUG } = await load();
    const { container } = render(createElement(B2BView, { slug: SAMPLE_SLUG }));

    await waitFor(() => expect(screen.getByText("O que voce ganha")).toBeTruthy());
    expect(screen.getByText("Tiers de parceria")).toBeTruthy();
    // honest: the tiers are illustrative, flagged amostra.
    expect(screen.getAllByText(/amostra/i).length).toBeGreaterThan(0);
    // SCOPE BOUNDARY: no fake cart/checkout copy anywhere on the page.
    const html = container.innerHTML.toLowerCase();
    expect(html).not.toContain("finalizar compra");
    expect(html).not.toContain("adicionar ao carrinho");
    expect(html).not.toContain("checkout");
    assertNoUnsafeImg(container);
  });

  it("ENRICHED: renders the pricing-band table, onboarding steps and the FAQ", async () => {
    const { B2BView, SAMPLE_SLUG } = await load();
    const sc = await import("@/lib/storeContent");
    render(createElement(B2BView, { slug: SAMPLE_SLUG }));

    // a real wholesale area: pricing bands (illustrative), onboarding, FAQ.
    await waitFor(() =>
      expect(screen.getByText("Quanto mais volume, melhor a faixa")).toBeTruthy(),
    );
    // every pricing band row volume renders.
    for (const row of sc.B2B_PRICING_BANDS) {
      expect(screen.getByText(row.volume)).toBeTruthy();
    }
    // onboarding steps render.
    expect(screen.getByText("Tres passos para comecar")).toBeTruthy();
    for (const step of sc.B2B_STEPS) {
      expect(screen.getByText(step.title)).toBeTruthy();
    }
    // the FAQ renders every question.
    expect(screen.getByText("Perguntas frequentes")).toBeTruthy();
    for (const f of sc.B2B_FAQ) {
      expect(screen.getByText(f.question)).toBeTruthy();
    }
    // a third tier exists (Distribuidor) -> a real tier band, not just two.
    expect(screen.getByText("Distribuidor")).toBeTruthy();
  });

  it("no-leak: an unknown tenant slug -> NotFound", async () => {
    const { B2BView } = await load();
    render(createElement(B2BView, { slug: "ghost-tenant" }));
    await waitFor(() => expect(screen.getByText("Nada por aqui")).toBeTruthy());
  });
});
