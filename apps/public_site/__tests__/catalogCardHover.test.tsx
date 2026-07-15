import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { CatalogCard } from "@/components/CatalogCard";
import type { PublicCatalogItem } from "@/lib/types";

// ----------------------------------------------------------------------------
// CatalogCard 2nd-image hover swap. SECURITY-FIRST: the hover (2nd) image is
// tenant-payload media and MUST pass isSafeMediaSrc before it can become an <img src>,
// exactly like the primary thumbnail. These assert:
//   * with >=2 SAFE images -> a 2nd, group-hover overlay <img> renders (object-cover);
//   * with 1 safe image -> NO overlay (only the primary image);
//   * an UNSAFE 2nd candidate is DROPPED -- it never becomes the hover image, and no
//     unsafe scheme reaches any src.
// ----------------------------------------------------------------------------

const SAFE_A = "data:image/svg+xml;utf8," + encodeURIComponent("<svg/>");
const SAFE_B = "https://cdn.example.com/b.jpg";
const UNSAFE_JS = "javascript:alert(1)";
const UNSAFE_HTTP = "http://insecure.example.com/c.jpg";

function makeItem(images: string[]): PublicCatalogItem {
  return {
    id: "x1",
    kind: "marketplace_listing",
    published_at: null,
    title: "Produto",
    images,
  };
}

function imgSrcs(container: HTMLElement): string[] {
  return Array.from(container.querySelectorAll("img")).map((i) => i.getAttribute("src") ?? "");
}

describe("CatalogCard -- 2nd-image hover swap (isSafeMediaSrc gated)", () => {
  it("renders a group-hover 2nd image when >=2 SAFE images exist", () => {
    const { container } = render(<CatalogCard item={makeItem([SAFE_A, SAFE_B])} slug="demo" />);
    const srcs = imgSrcs(container);
    expect(srcs).toContain(SAFE_A);
    expect(srcs).toContain(SAFE_B);
    // the 2nd image is the hover overlay: absolutely positioned + fades in on hover.
    const overlay = Array.from(container.querySelectorAll("img")).find(
      (i) => i.getAttribute("src") === SAFE_B,
    );
    expect(overlay).toBeTruthy();
    expect(overlay!.className).toContain("group-hover:opacity-100");
    expect(overlay!.className).toContain("object-cover");
    expect(overlay!.className).toContain("absolute");
  });

  it("renders NO overlay with only one safe image", () => {
    const { container } = render(<CatalogCard item={makeItem([SAFE_A])} slug="demo" />);
    // exactly one product img (the primary); no group-hover overlay.
    const overlays = Array.from(container.querySelectorAll("img")).filter((i) =>
      (i.className ?? "").includes("group-hover:opacity-100"),
    );
    expect(overlays.length).toBe(0);
  });

  it("DROPS an unsafe 2nd candidate -- it never becomes the hover image", () => {
    // primary SAFE, 2nd candidate UNSAFE -> only one safe image -> no hover overlay.
    const { container } = render(
      <CatalogCard item={makeItem([SAFE_A, UNSAFE_JS, UNSAFE_HTTP])} slug="demo" />,
    );
    const srcs = imgSrcs(container);
    // no unsafe scheme reached any src.
    for (const bad of [UNSAFE_JS, UNSAFE_HTTP]) {
      expect(srcs.some((s) => s === bad)).toBe(false);
    }
    // and no hover overlay (the 2nd safe image does not exist).
    const overlays = Array.from(container.querySelectorAll("img")).filter((i) =>
      (i.className ?? "").includes("group-hover:opacity-100"),
    );
    expect(overlays.length).toBe(0);
  });

  it("promotes the 2nd SAFE image even when an unsafe one sits between", () => {
    // SAFE_A, UNSAFE, SAFE_B -> safe list = [A, B] -> B is the hover overlay.
    const { container } = render(
      <CatalogCard item={makeItem([SAFE_A, UNSAFE_HTTP, SAFE_B])} slug="demo" />,
    );
    const overlay = Array.from(container.querySelectorAll("img")).find((i) =>
      (i.className ?? "").includes("group-hover:opacity-100"),
    );
    expect(overlay).toBeTruthy();
    expect(overlay!.getAttribute("src")).toBe(SAFE_B);
    expect(imgSrcs(container).some((s) => s === UNSAFE_HTTP)).toBe(false);
  });
});
