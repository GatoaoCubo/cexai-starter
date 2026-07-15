import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { RatingRow, ReviewsBand } from "@/components/Rating";
import { ratingOf, reviewsOf } from "@/lib/brandText";
import type { PublicCatalogItem } from "@/lib/types";

// ----------------------------------------------------------------------------
// Rating (RatingRow + ReviewsBand) + the ratingOf/reviewsOf pure pickers.
//
// HONEST-EMPTY is the load-bearing contract: with NO rating/review fields the picker
// returns null/[] and the components render NOTHING (never a fabricated star/review).
// Plus: stars are MONOCHROME (foreground/border, not brand teal); the verified badge
// uses --success (text-success), NOT brand teal; review media is isSafeMediaSrc-gated.
// ----------------------------------------------------------------------------

function item(extra: Record<string, unknown>): PublicCatalogItem {
  return { id: "x", kind: "marketplace_listing", published_at: null, ...extra };
}

describe("ratingOf -- honest rating picker", () => {
  it("returns null when the payload has NO rating field", () => {
    expect(ratingOf(item({ review_count: 9 }))).toBeNull(); // count alone != rating
    expect(ratingOf(item({ title: "x" }))).toBeNull();
  });

  it("reads rating + count + verified when present", () => {
    const r = ratingOf(item({ rating: 4.7, review_count: 128, verified: true }));
    expect(r).not.toBeNull();
    expect(r!.value).toBeCloseTo(4.7);
    expect(r!.display).toBe("4.7");
    expect(r!.count).toBe(128);
    expect(r!.verified).toBe(true);
  });

  it("clamps to [0,5] and parses a pt-BR comma decimal", () => {
    expect(ratingOf(item({ rating: 9 }))!.value).toBe(5);
    expect(ratingOf(item({ nota: "4,5" }))!.value).toBeCloseTo(4.5);
  });
});

describe("reviewsOf -- honest review-list picker", () => {
  it("returns [] when there is no review array (a scalar count is NOT a list)", () => {
    expect(reviewsOf(item({ reviews: 12 }))).toEqual([]);
    expect(reviewsOf(item({}))).toEqual([]);
  });

  it("reads an explicit reviews_list array", () => {
    const rs = reviewsOf(
      item({ reviews_list: [{ author: "Ana", rating: 5, body: "bom" }] }),
    );
    expect(rs.length).toBe(1);
    expect(rs[0].author).toBe("Ana");
    expect(rs[0].body).toBe("bom");
    expect(rs[0].rating).toBe(5);
  });
});

describe("RatingRow -- honest-empty + monochrome + success-green verified", () => {
  it("renders NOTHING when rating is null (honest-empty)", () => {
    const { container } = render(<RatingRow rating={null} />);
    expect(container.firstChild).toBeNull();
  });

  it("renders the rating value + count when present", () => {
    const { container } = render(<RatingRow rating={ratingOf(item({ rating: 4.7, review_count: 128 }))} />);
    expect(container.textContent).toContain("4.7");
    expect(container.textContent).toContain("128");
  });

  it("uses status-green (text-success) for the verified badge -- NOT brand teal", () => {
    const { container } = render(
      <RatingRow rating={ratingOf(item({ rating: 4.7, verified: true }))} />,
    );
    expect(container.innerHTML).toContain("text-success");
    expect(container.textContent).toContain("verificado");
    // the verified affordance is not styled with the brand color.
    const badge = Array.from(container.querySelectorAll("span")).find((s) =>
      (s.textContent ?? "").includes("verificado"),
    );
    expect(badge!.className).not.toContain("text-brand");
  });

  it("stars are monochrome (foreground / border), never brand teal", () => {
    const { container } = render(<RatingRow rating={ratingOf(item({ rating: 3 }))} />);
    expect(container.innerHTML).toContain("text-foreground");
    expect(container.innerHTML).toContain("text-border");
    expect(container.innerHTML).not.toContain("text-brand");
  });
});

describe("ReviewsBand -- honest-empty + review media safe-src gate", () => {
  it("renders NOTHING with no reviews (honest-empty)", () => {
    const { container } = render(<ReviewsBand reviews={[]} />);
    expect(container.firstChild).toBeNull();
  });

  it("renders the review entries with data", () => {
    const { container } = render(
      <ReviewsBand reviews={reviewsOf(item({ reviews_list: [{ author: "Ana", body: "bom", rating: 5 }] }))} />,
    );
    expect(container.textContent).toContain("Ana");
    expect(container.textContent).toContain("bom");
    expect(container.textContent).toContain("Avaliacoes");
  });

  it("gates per-review media with isSafeMediaSrc (unsafe dropped, safe rendered)", () => {
    const SAFE = "https://cdn.example.com/r.jpg";
    const { container } = render(
      <ReviewsBand
        reviews={[
          { author: "A", rating: 5, body: "safe", media: SAFE },
          { author: "B", rating: 4, body: "unsafe", media: "javascript:alert(1)" },
          { author: "C", rating: 3, body: "mixed", media: "http://insecure/x.jpg" },
        ]}
      />,
    );
    const srcs = Array.from(container.querySelectorAll("img")).map((i) => i.getAttribute("src") ?? "");
    expect(srcs).toContain(SAFE);
    expect(srcs.some((s) => s.startsWith("javascript:"))).toBe(false);
    expect(srcs.some((s) => s.startsWith("http://"))).toBe(false);
  });
});
