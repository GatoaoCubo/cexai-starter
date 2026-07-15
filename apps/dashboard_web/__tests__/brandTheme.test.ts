import { describe, it, expect } from "vitest";
import {
  buildCssVars,
  isHslTriplet,
  isCssLength,
  isValidTokenValue,
  DEFAULT_BRAND_SAMPLE,
  type BrandTheme,
} from "@/lib/brandTheme";

// Render-boundary token-value guard tests (HARDENING iter 2). The dashboard now
// re-validates each brand token VALUE before emitting it into the :root cascade,
// symmetric with the public_site mirror + the Python moldgen validator
// (cex_moldgen_emit.is_hsl_triplet / is_css_length). A malformed value is dropped;
// valid values pass through unchanged (ZERO-REGRESSION for existing theming).

describe("isHslTriplet (mirrors cex_moldgen_emit.is_hsl_triplet)", () => {
  it("accepts a well-formed triplet", () => {
    expect(isHslTriplet("174 68% 50%")).toBe(true);
    expect(isHslTriplet("0 0% 100%")).toBe(true);
  });
  it("accepts the boundary values (H<=360, S/L<=100)", () => {
    expect(isHslTriplet("360 100% 100%")).toBe(true);
  });
  it("rejects out-of-range channels", () => {
    expect(isHslTriplet("361 50% 50%")).toBe(false); // H > 360
    expect(isHslTriplet("200 101% 50%")).toBe(false); // S > 100
    expect(isHslTriplet("200 50% 101%")).toBe(false); // L > 100
  });
  it("rejects malformed / non-string values", () => {
    expect(isHslTriplet("not-a-color")).toBe(false);
    expect(isHslTriplet("#7C3AED")).toBe(false);
    expect(isHslTriplet("174 68 50")).toBe(false); // missing % signs
    expect(isHslTriplet("")).toBe(false);
    expect(isHslTriplet(undefined)).toBe(false);
    expect(isHslTriplet(42)).toBe(false);
  });
});

describe("isCssLength (mirrors cex_moldgen_emit.is_css_length)", () => {
  it("accepts CSS lengths usable for --radius", () => {
    expect(isCssLength("0.75rem")).toBe(true);
    expect(isCssLength("12px")).toBe(true);
    expect(isCssLength("0")).toBe(true);
    expect(isCssLength("  0.5rem  ")).toBe(true); // trimmed before matching
  });
  it("rejects unsupported units / malformed lengths", () => {
    expect(isCssLength("5vh")).toBe(false);
    expect(isCssLength("auto")).toBe(false);
    expect(isCssLength("12 px")).toBe(false);
    expect(isCssLength("")).toBe(false);
    expect(isCssLength(0)).toBe(false);
  });
});

describe("isValidTokenValue routes radius to length, the rest to HSL", () => {
  it("validates radius as a CSS length", () => {
    expect(isValidTokenValue("radius", "0.75rem")).toBe(true);
    expect(isValidTokenValue("radius", "174 68% 50%")).toBe(false);
  });
  it("validates colour tokens as HSL triplets", () => {
    expect(isValidTokenValue("primary", "174 68% 50%")).toBe(true);
    expect(isValidTokenValue("primary", "0.75rem")).toBe(false);
  });
});

describe("buildCssVars render-boundary guard", () => {
  it("passes the valid default sample through INTACT (zero-regression)", () => {
    const css = buildCssVars(DEFAULT_BRAND_SAMPLE);
    // every one of the 24 token css-vars is present + the font-family line.
    expect(css.startsWith(":root{")).toBe(true);
    expect(css).toContain("--primary:174 68% 50%");
    expect(css).toContain("--radius:0.75rem");
    expect(css).toContain("--brand:174 68% 50%");
    expect(css).toContain("--font-family-base:Inter, -apple-system, Segoe UI, sans-serif");
    // 24 tokens + 1 font line = 25 declarations.
    expect(css.replace(/^:root\{|\}$/g, "").split(";")).toHaveLength(25);
  });

  it("DROPS a malformed colour token value while keeping the valid ones", () => {
    const theme: BrandTheme = {
      tokens: {
        primary: "174 68% 50%", // valid -> emitted
        accent: "not-a-color", // malformed -> dropped
        secondary: "999 999% 999%", // out-of-range -> dropped
        radius: "0.75rem", // valid length -> emitted
      },
    };
    const css = buildCssVars(theme);
    expect(css).toContain("--primary:174 68% 50%");
    expect(css).toContain("--radius:0.75rem");
    expect(css).not.toContain("--accent");
    expect(css).not.toContain("not-a-color");
    expect(css).not.toContain("--secondary");
    expect(css).not.toContain("999");
  });

  it("DROPS a malformed radius value (wrong unit) but keeps valid colours", () => {
    const theme: BrandTheme = {
      tokens: { primary: "200 50% 40%", radius: "5vh" },
    };
    const css = buildCssVars(theme);
    expect(css).toContain("--primary:200 50% 40%");
    expect(css).not.toContain("--radius");
    expect(css).not.toContain("5vh");
  });

  it("drops a CSS-injection attempt smuggled as a token value", () => {
    const theme: BrandTheme = {
      // a value trying to close the decl + inject a rule fails the HSL shape -> dropped.
      tokens: { primary: "0 0% 0%;} body{display:none" },
    };
    const css = buildCssVars(theme);
    expect(css).toBe(""); // nothing valid -> empty (degrade-never)
    expect(css).not.toContain("display:none");
  });

  it("still emits fontFamily even when all tokens are dropped", () => {
    const theme: BrandTheme = {
      tokens: { primary: "bad" },
      fontFamily: "Inter, sans-serif",
    };
    const css = buildCssVars(theme);
    expect(css).toBe(":root{--font-family-base:Inter, sans-serif}");
  });

  it("returns '' for an empty theme (degrade-never, unchanged)", () => {
    expect(buildCssVars({})).toBe("");
    expect(buildCssVars({ tokens: {} })).toBe("");
  });
});

// fontFamily render-boundary guard (HARDENING iter 3 -- parity with public_site).
// The dashboard buildCssVars now guards its fontFamily branch with the SAME
// isSafeFontFamily helper the public_site mirror uses, so a hostile font stack
// carrying CSS-control chars (e.g. "Inter; } body{display:none") is DROPPED on
// BOTH surfaces and can never inject a live rule into the export-document <style>.
// A clean font stack still passes through unchanged (zero-regression).

describe("buildCssVars fontFamily guard (symmetric with public_site)", () => {
  it("emits a clean fontFamily unchanged", () => {
    const css = buildCssVars({ fontFamily: "Inter, -apple-system, Segoe UI, sans-serif" });
    expect(css).toBe(":root{--font-family-base:Inter, -apple-system, Segoe UI, sans-serif}");
  });

  it("DROPS a hostile fontFamily that smuggles a CSS rule via ; and braces", () => {
    const css = buildCssVars({ fontFamily: "Inter; } body{display:none" });
    expect(css).toBe(""); // hostile font dropped, no other decls -> empty (degrade-never)
    expect(css).not.toContain("display:none");
    expect(css).not.toContain("--font-family-base");
  });

  it("DROPS a hostile fontFamily but still emits the valid tokens beside it", () => {
    const css = buildCssVars({
      tokens: { primary: "174 68% 50%" }, // valid -> emitted
      fontFamily: "Arial<script>", // injection chars -> dropped
    });
    expect(css).toContain("--primary:174 68% 50%");
    expect(css).not.toContain("--font-family-base");
    expect(css).not.toContain("<script>");
  });

  it("DROPS a fontFamily that smuggles a raw CSS var ref (--)", () => {
    const css = buildCssVars({ fontFamily: "var(--x)" });
    expect(css).toBe("");
    expect(css).not.toContain("--font-family-base");
  });
});
