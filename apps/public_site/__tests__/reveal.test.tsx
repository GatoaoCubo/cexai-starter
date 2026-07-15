import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { Reveal } from "@/components/Reveal";

// ----------------------------------------------------------------------------
// Reveal -- the reveal-on-scroll motion wrapper. The CRAFT addition must NEVER hide
// content from assistive tech, crawlers, or tests. These lock that contract:
//   * the wrapped content is ALWAYS in the DOM (present + readable), regardless of
//     whether IntersectionObserver fired -- motion only animates opacity/transform;
//   * with prefers-reduced-motion the element is shown in its resting state with NO
//     transition class (it never animates), honouring the a11y baseline;
//   * when IntersectionObserver is unavailable (jsdom / SSR) the content shows
//     immediately (degrade-never);
//   * the polymorphic `as` prop renders the requested element.
// ----------------------------------------------------------------------------

const ORIGINAL_MATCH_MEDIA = window.matchMedia;
const ORIGINAL_IO = (globalThis as { IntersectionObserver?: unknown }).IntersectionObserver;

afterEach(() => {
  vi.restoreAllMocks();
  window.matchMedia = ORIGINAL_MATCH_MEDIA;
  (globalThis as { IntersectionObserver?: unknown }).IntersectionObserver = ORIGINAL_IO;
});

describe("Reveal -- motion wrapper (content always present)", () => {
  beforeEach(() => {
    // jsdom has no IntersectionObserver by default -> the degrade-never path (show now).
    // Make it explicit so the test is not environment-dependent.
    delete (globalThis as { IntersectionObserver?: unknown }).IntersectionObserver;
  });

  it("renders its children immediately when IntersectionObserver is absent (degrade-never)", () => {
    render(<Reveal>conteudo revelado</Reveal>);
    const el = screen.getByText("conteudo revelado");
    expect(el).toBeTruthy();
    // shown -> opacity-100 (no lingering opacity-0 that would hide it from a viewer).
    expect(el.className).toContain("opacity-100");
    expect(el.className).not.toContain("opacity-0");
  });

  it("does NOT attach a transition when prefers-reduced-motion is set", () => {
    window.matchMedia = ((q: string) => ({
      matches: true,
      media: q,
      onchange: null,
      addEventListener: () => {},
      removeEventListener: () => {},
      addListener: () => {},
      removeListener: () => {},
      dispatchEvent: () => false,
    })) as unknown as typeof window.matchMedia;

    render(<Reveal>sem animacao</Reveal>);
    const el = screen.getByText("sem animacao");
    expect(el).toBeTruthy();
    // reduced motion -> the resting (un-armed) class, no transition utility.
    expect(el.className).toContain("opacity-100");
    expect(el.className).not.toContain("transition-");
  });

  it("renders the polymorphic element requested via `as`", () => {
    const { container } = render(
      <Reveal as="section" className="x-marker">
        secao
      </Reveal>,
    );
    const section = container.querySelector("section.x-marker");
    expect(section).not.toBeNull();
    expect(section!.textContent).toBe("secao");
  });
});
