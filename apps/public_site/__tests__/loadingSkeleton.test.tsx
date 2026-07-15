import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render } from "@testing-library/react";
import { createElement } from "react";

// ----------------------------------------------------------------------------
// View loading-phase tests: the synchronous FIRST render of each view (before the
// async fetch resolves) is the loading phase, which must now show a content-shaped
// SKELETON (role=status, aria-busy, animate-pulse blocks) instead of the old plain
// "carregando..." text. Asserting the first paint exercises exactly that branch.
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

function assertSkeletonFirstPaint(container: HTMLElement) {
  // a busy status region with pulsing blocks, and NOT the old plain text loader.
  const region = container.querySelector('[role="status"]');
  expect(region).not.toBeNull();
  expect(region!.getAttribute("aria-busy")).toBe("true");
  expect(container.querySelectorAll(".animate-pulse").length).toBeGreaterThan(0);
  expect(container.textContent ?? "").not.toContain("carregando...");
}

describe("View loading phase renders a content-shaped skeleton", () => {
  it("HomeView shows a hero+grid skeleton while loading", async () => {
    const { HomeView } = await import("@/components/views/HomeView");
    const { SAMPLE_SLUG } = await import("@/lib/fixtures");
    const { container } = render(createElement(HomeView, { slug: SAMPLE_SLUG }));
    assertSkeletonFirstPaint(container);
  });

  it("CatalogView shows a header+grid skeleton while loading", async () => {
    const { CatalogView } = await import("@/components/views/CatalogView");
    const { SAMPLE_SLUG } = await import("@/lib/fixtures");
    const { container } = render(
      createElement(CatalogView, { slug: SAMPLE_SLUG, kind: "marketplace_listing" }),
    );
    assertSkeletonFirstPaint(container);
  });

  it("DetailView shows a gallery+buy-box skeleton while loading", async () => {
    const { DetailView } = await import("@/components/views/DetailView");
    const { SAMPLE_SLUG } = await import("@/lib/fixtures");
    const { container } = render(
      createElement(DetailView, {
        slug: SAMPLE_SLUG,
        kind: "marketplace_listing",
        id: "ml_sample_0001",
      }),
    );
    assertSkeletonFirstPaint(container);
  });
});
