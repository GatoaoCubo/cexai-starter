import { describe, it, expect } from "vitest";
import {
  buildCssVars,
  isHslTriplet,
  isCssLength,
} from "@/lib/brandTheme";
import type { BrandTheme } from "@/lib/brandTheme";

// ----------------------------------------------------------------------------
// brandTheme RENDER-BOUNDARY GUARD (defense-in-depth) -- the public site is the
// UNAUTHENTICATED surface, so buildCssVars must NOT blindly trust the write path.
// It RE-VALIDATES every token value against the same shape the Python validators
// enforce (is_hsl_triplet / is_css_length) and DROPS any malformed one -- the
// static fallback wins for that var instead of a hostile / broken value reaching
// :root{}. Dropping one bad token must never blank the rest (degrade-never).
//
// These assert the guard MIRRORS cex_moldgen_emit byte-for-byte AND that a
// malformed token is dropped while the valid siblings survive.
// ----------------------------------------------------------------------------

describe("isHslTriplet / isCssLength -- mirror the Python validators", () => {
  it("accepts a valid 'H S% L%' triplet", () => {
    expect(isHslTriplet("173 58% 39%")).toBe(true);
    expect(isHslTriplet("0 0% 100%")).toBe(true);
    expect(isHslTriplet("360 100% 100%")).toBe(true);
  });

  it("rejects out-of-range / malformed triplets", () => {
    expect(isHslTriplet("400 58% 39%")).toBe(false); // H > 360
    expect(isHslTriplet("173 120% 39%")).toBe(false); // S > 100
    expect(isHslTriplet("173 58% 250%")).toBe(false); // L > 100
    expect(isHslTriplet("173 58 39")).toBe(false); // no % units
    expect(isHslTriplet("red")).toBe(false);
    expect(isHslTriplet("")).toBe(false);
    expect(isHslTriplet(42 as unknown)).toBe(false);
  });

  it("accepts CSS lengths usable for --radius; rejects others", () => {
    expect(isCssLength("0.75rem")).toBe(true);
    expect(isCssLength("0")).toBe(true);
    expect(isCssLength("12px")).toBe(true);
    expect(isCssLength("50%")).toBe(true);
    expect(isCssLength("1em")).toBe(true);
    expect(isCssLength("173 58% 39%")).toBe(false);
    expect(isCssLength("1foo")).toBe(false);
    expect(isCssLength("")).toBe(false);
  });
});

describe("buildCssVars -- render-boundary guard drops malformed tokens", () => {
  it("emits only SHAPE-VALID tokens; a malformed token is dropped, siblings survive", () => {
    const theme: BrandTheme = {
      name: "Acme",
      tokens: {
        primary: "173 58% 39%", // valid HSL -> kept
        brand: "NOT-A-COLOR", // malformed -> dropped
        background: "999 200% 50%", // out-of-range -> dropped
        radius: "0.75rem", // valid length -> kept
        accent: "0 0% 7%", // valid HSL -> kept
      },
    };
    const css = buildCssVars(theme);
    // the valid tokens are present
    expect(css).toContain("--primary:173 58% 39%");
    expect(css).toContain("--accent:0 0% 7%");
    expect(css).toContain("--radius:0.75rem");
    // the malformed tokens are NEVER emitted -> the static fallback wins for them
    expect(css).not.toContain("NOT-A-COLOR");
    expect(css).not.toContain("--brand:");
    expect(css).not.toContain("--background:");
    expect(css).not.toContain("999");
  });

  it("rejects a radius that is not a CSS length (e.g. an HSL triplet)", () => {
    const css = buildCssVars({ tokens: { radius: "173 58% 39%" } });
    expect(css).not.toContain("--radius:");
  });

  it("rejects a token value that smuggles a raw CSS var ref (--x)", () => {
    // a value that tries to reference another var must be dropped (matches the
    // write-path value guard in validate_spec).
    const css = buildCssVars({ tokens: { primary: "var(--evil)" } as never });
    expect(css).not.toContain("--primary:");
    expect(css).not.toContain("evil");
  });

  it("drops a fontFamily carrying CSS-control chars; keeps a clean one", () => {
    const evil = buildCssVars({ fontFamily: "Inter; } body{display:none" });
    expect(evil).toBe(""); // no valid decls -> empty (degrade-never)
    const clean = buildCssVars({ fontFamily: "Inter, sans-serif" });
    expect(clean).toContain("--font-family-base:Inter, sans-serif");
  });

  it("an all-malformed theme yields an EMPTY string (neutral look, never broken)", () => {
    const css = buildCssVars({ tokens: { primary: "bad", brand: "also-bad" } });
    expect(css).toBe("");
  });

  it("a valid full theme emits a :root{} block (the happy path still works)", () => {
    const css = buildCssVars({
      tokens: { primary: "0 0% 7%", brand: "173 58% 39%", radius: "0.5rem" },
    });
    expect(css.startsWith(":root{")).toBe(true);
    expect(css.endsWith("}")).toBe(true);
    expect(css).toContain("--brand:173 58% 39%");
  });
});
