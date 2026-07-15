import { describe, it, expect, afterEach, vi } from "vitest";
import { render, act } from "@testing-library/react";
import { MobileBuyBar } from "@/components/MobileBuyBar";

// ----------------------------------------------------------------------------
// MobileBuyBar -- the mobile (lg:hidden) sticky buy CTA. These lock:
//   * it mirrors the SAME external buy_url, rel-hardened (noopener noreferrer nofollow),
//     target=_blank -- NEVER a fake cart/checkout;
//   * it is lg:hidden (desktop uses the sticky buy-box);
//   * IntersectionObserver-hide: while the watched in-page CTA is ON screen the bar is
//     translated off (hidden); once it leaves the bar slides in;
//   * degrade-never: no IntersectionObserver -> the bar stays visible (CTA reachable).
// ----------------------------------------------------------------------------

const ORIGINAL_IO = (globalThis as { IntersectionObserver?: unknown }).IntersectionObserver;

afterEach(() => {
  vi.restoreAllMocks();
  (globalThis as { IntersectionObserver?: unknown }).IntersectionObserver = ORIGINAL_IO;
  document.body.innerHTML = "";
});

/** Install a controllable IntersectionObserver mock. Returns a fn to drive intersection. */
function installIO() {
  let cb: ((entries: { isIntersecting: boolean }[]) => void) | null = null;
  class MockIO {
    constructor(c: (entries: { isIntersecting: boolean }[]) => void) {
      cb = c;
    }
    observe() {}
    disconnect() {}
  }
  (globalThis as { IntersectionObserver?: unknown }).IntersectionObserver =
    MockIO as unknown as typeof IntersectionObserver;
  return {
    fire: (isIntersecting: boolean) => act(() => cb?.([{ isIntersecting }])),
  };
}

describe("MobileBuyBar -- sticky mobile CTA", () => {
  it("renders the external buy_url rel-hardened, lg:hidden, no fake cart", () => {
    const { container } = render(
      <MobileBuyBar buyUrl="https://example.com/buy" watchId="missing-anchor" />,
    );
    const bar = container.querySelector('[data-testid="mobile-buy-bar"]') as HTMLElement;
    expect(bar).not.toBeNull();
    expect(bar.className).toContain("lg:hidden");
    expect(bar.className).toContain("fixed");

    const link = container.querySelector("a") as HTMLAnchorElement;
    expect(link.getAttribute("href")).toBe("https://example.com/buy");
    expect(link.getAttribute("target")).toBe("_blank");
    expect(link.getAttribute("rel")).toBe("noopener noreferrer nofollow");
    // no fake cart: there is no form/button[type=submit]/input.
    expect(container.querySelector("form")).toBeNull();
    expect(container.querySelector('button[type="submit"]')).toBeNull();
    expect(container.querySelector("input")).toBeNull();
  });

  it("renders NOTHING when buyUrl is empty", () => {
    const { container } = render(<MobileBuyBar buyUrl="" />);
    expect(container.firstChild).toBeNull();
  });

  it("stays VISIBLE when IntersectionObserver is unavailable (degrade-never)", () => {
    delete (globalThis as { IntersectionObserver?: unknown }).IntersectionObserver;
    // an anchor exists, but no IO -> safe default = visible.
    const anchor = document.createElement("a");
    anchor.id = "cta";
    document.body.appendChild(anchor);
    const { container } = render(<MobileBuyBar buyUrl="https://example.com/buy" watchId="cta" />);
    const bar = container.querySelector('[data-testid="mobile-buy-bar"]') as HTMLElement;
    expect(bar.className).toContain("translate-y-0");
    expect(bar.className).not.toContain("translate-y-full");
  });

  it("HIDES while the in-page CTA is on screen, SHOWS once it scrolls away", () => {
    const io = installIO();
    const anchor = document.createElement("a");
    anchor.id = "cta";
    document.body.appendChild(anchor);
    const { container } = render(<MobileBuyBar buyUrl="https://example.com/buy" watchId="cta" />);

    // in-page CTA on screen -> bar hidden (translated off).
    io.fire(true);
    let bar = container.querySelector('[data-testid="mobile-buy-bar"]') as HTMLElement;
    expect(bar.className).toContain("translate-y-full");
    expect(bar.getAttribute("aria-hidden")).toBe("true");

    // in-page CTA scrolled away -> bar shown.
    io.fire(false);
    bar = container.querySelector('[data-testid="mobile-buy-bar"]') as HTMLElement;
    expect(bar.className).toContain("translate-y-0");
    expect(bar.getAttribute("aria-hidden")).toBeNull();
  });
});
