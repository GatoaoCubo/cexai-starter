import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { Skeleton } from "@/components/Skeleton";

// ----------------------------------------------------------------------------
// Skeleton -- the content-shaped loading primitive. These lock:
//   * a single Skeleton block renders a pulsing (animate-pulse) decorative div;
//   * the composed shapes (HeroGrid / CatalogGrid / Pdp) render multiple blocks +
//     announce themselves as busy (role=status, aria-busy) to assistive tech;
//   * the blocks are aria-hidden (decorative scaffold, not read out).
// The pulse auto-disables under prefers-reduced-motion via the GLOBAL CSS rule in
// globals.css (not asserted here -- it is a stylesheet rule, not a class toggle).
// ----------------------------------------------------------------------------

function pulses(container: HTMLElement): Element[] {
  return Array.from(container.querySelectorAll(".animate-pulse"));
}

describe("Skeleton -- loading placeholder primitive", () => {
  it("renders a pulsing, decorative block", () => {
    const { container } = render(<Skeleton className="h-4 w-10" />);
    const block = container.firstElementChild as HTMLElement;
    expect(block).toBeTruthy();
    expect(block.className).toContain("animate-pulse");
    expect(block.getAttribute("aria-hidden")).toBe("true");
  });

  it("HeroGrid renders a busy region with multiple skeleton blocks", () => {
    const { container } = render(<Skeleton.HeroGrid />);
    const region = container.querySelector('[role="status"]');
    expect(region).not.toBeNull();
    expect(region!.getAttribute("aria-busy")).toBe("true");
    expect(pulses(container).length).toBeGreaterThan(3);
  });

  it("CatalogGrid renders a busy region with a card grid of skeletons", () => {
    const { container } = render(<Skeleton.CatalogGrid />);
    const region = container.querySelector('[role="status"]');
    expect(region).not.toBeNull();
    expect(region!.getAttribute("aria-busy")).toBe("true");
    expect(pulses(container).length).toBeGreaterThan(6);
  });

  it("Pdp renders a busy region shaped like the product page (gallery + buy-box)", () => {
    const { container } = render(<Skeleton.Pdp />);
    const region = container.querySelector('[role="status"]');
    expect(region).not.toBeNull();
    expect(region!.getAttribute("aria-busy")).toBe("true");
    expect(pulses(container).length).toBeGreaterThan(5);
  });
});
