// R-019 -- "Default color palette renders silently with no disclosure when tenant brand
// tokens are unmapped" (docs/AUDIT_CLAIMS_VS_REALITY_2026_07_02.md D1.7, corrected PARTIAL).
//
// Proves the fix: lib/brandTheme.ts's buildCssVars() and lib/adminTheme.ts's
// resolveAdminTheme() now call the shared warnTokenFallback() dev-only disclosure hook
// whenever a SUPPLIED (non-empty) token/brand value fails its shape guard and the code
// silently falls back to a base/default value -- console.warn ONLY when
// NODE_ENV==="development" (the same dev-gate convention as lib/exportAgent.ts), never in
// a deployed build, and NEVER for a simply-ABSENT optional field (a partial theme is
// legitimate, not a bug -- only a present-but-rejected value is a real signal).
//
// ZERO-REGRESSION is asserted throughout: every existing "malformed value dropped" /
// "unknown tenant -> default cyan" outcome is unchanged -- this row only ADDS a disclosure
// side-effect, never changes what gets rendered.
//
// Harness mirrors the sibling suites (vi.stubEnv + vi.resetModules; vi.doMock for the
// generated JSON registry per generated-admin-theme.test.tsx; vi.doMock+importOriginal for
// a synthetic ORBIT_BRAND_SAMPLE per this file's own manual-row cases).

import { describe, it, expect, vi, afterEach } from "vitest";

afterEach(() => {
  vi.unstubAllEnvs();
  vi.resetModules();
  vi.doUnmock("@/lib/generatedAdminThemes.json");
  vi.doUnmock("@/lib/brandTheme");
});

/** Re-import lib/brandTheme fresh under a given NODE_ENV. */
async function loadBrandTheme(nodeEnv: string) {
  vi.resetModules();
  vi.stubEnv("NODE_ENV", nodeEnv);
  return import("@/lib/brandTheme");
}

/** Re-import lib/adminTheme fresh with a SYNTHETIC generated registry + NODE_ENV. */
async function loadAdminThemeWithGenerated(registry: unknown, nodeEnv: string) {
  vi.resetModules();
  vi.stubEnv("NODE_ENV", nodeEnv);
  vi.stubEnv("NEXT_PUBLIC_TENANT", "");
  vi.doMock("@/lib/generatedAdminThemes.json", () => ({ default: registry }));
  return import("@/lib/adminTheme");
}

/** Re-import lib/adminTheme fresh with demo-orbit's brand.tokens.primary REPLACED (the
 *  manual ADMIN_TENANTS row is keyed off the SAME ORBIT_BRAND_SAMPLE export). */
async function loadAdminThemeWithCorruptOrbitPrimary(primary: unknown, nodeEnv: string) {
  vi.resetModules();
  vi.stubEnv("NODE_ENV", nodeEnv);
  vi.stubEnv("NEXT_PUBLIC_TENANT", "demo-orbit");
  vi.doMock("@/lib/brandTheme", async (importOriginal) => {
    const actual = await importOriginal<typeof import("@/lib/brandTheme")>();
    return {
      ...actual,
      ORBIT_BRAND_SAMPLE: {
        ...actual.ORBIT_BRAND_SAMPLE,
        tokens: { ...actual.ORBIT_BRAND_SAMPLE.tokens, primary },
      },
    };
  });
  return import("@/lib/adminTheme");
}

// --------------------------------------------------------------------------
// 1. warnTokenFallback -- the shared disclosure hook itself.
// --------------------------------------------------------------------------
describe("warnTokenFallback (the shared dev-only disclosure hook)", () => {
  it("logs console.warn when NODE_ENV==='development'", async () => {
    const { warnTokenFallback } = await loadBrandTheme("development");
    const spy = vi.spyOn(console, "warn").mockImplementation(() => {});
    warnTokenFallback("something fell back to default");
    expect(spy).toHaveBeenCalledTimes(1);
    expect(spy.mock.calls[0][0]).toContain("something fell back to default");
    spy.mockRestore();
  });

  it("stays SILENT outside development (test / production)", async () => {
    for (const env of ["test", "production", ""]) {
      const { warnTokenFallback } = await loadBrandTheme(env);
      const spy = vi.spyOn(console, "warn").mockImplementation(() => {});
      warnTokenFallback("should not be logged");
      expect(spy).not.toHaveBeenCalled();
      spy.mockRestore();
      vi.resetModules();
    }
  });

  it("never throws even if console.warn itself throws (degrade-never)", async () => {
    const { warnTokenFallback } = await loadBrandTheme("development");
    const spy = vi.spyOn(console, "warn").mockImplementation(() => {
      throw new Error("console shim exploded");
    });
    expect(() => warnTokenFallback("x")).not.toThrow();
    spy.mockRestore();
  });
});

// --------------------------------------------------------------------------
// 2. buildCssVars -- disclose a SUPPLIED-but-malformed token; stay silent for an
//    ABSENT one; zero-regression on the emitted CSS itself either way.
// --------------------------------------------------------------------------
describe("buildCssVars token-fallback disclosure", () => {
  it("warns (dev) when a SUPPLIED colour token fails its shape guard", async () => {
    const { buildCssVars } = await loadBrandTheme("development");
    const spy = vi.spyOn(console, "warn").mockImplementation(() => {});
    const css = buildCssVars({ tokens: { primary: "174 68% 50%", accent: "not-a-color" } });
    // zero-regression: same drop behaviour as before the fix.
    expect(css).toContain("--primary:174 68% 50%");
    expect(css).not.toContain("--accent");
    // NEW: the drop is now disclosed.
    expect(spy).toHaveBeenCalledTimes(1);
    expect(spy.mock.calls[0][0]).toContain("accent");
    spy.mockRestore();
  });

  it("does NOT warn for a token that was simply never supplied", async () => {
    const { buildCssVars } = await loadBrandTheme("development");
    const spy = vi.spyOn(console, "warn").mockImplementation(() => {});
    const css = buildCssVars({ tokens: { primary: "174 68% 50%" } }); // secondary etc. absent
    expect(css).toContain("--primary:174 68% 50%");
    expect(spy).not.toHaveBeenCalled(); // absent != malformed -- no false-positive noise.
    spy.mockRestore();
  });

  it("warns on a malformed fontFamily but stays silent when fontFamily is absent", async () => {
    const { buildCssVars } = await loadBrandTheme("development");
    const spy = vi.spyOn(console, "warn").mockImplementation(() => {});
    buildCssVars({ fontFamily: "Inter; } body{display:none" });
    expect(spy).toHaveBeenCalledTimes(1);
    expect(spy.mock.calls[0][0]).toContain("fontFamily");
    spy.mockClear();
    buildCssVars({ tokens: { primary: "174 68% 50%" } }); // no fontFamily at all
    expect(spy).not.toHaveBeenCalled();
    spy.mockRestore();
  });

  it("stays silent outside development even though the value is still dropped", async () => {
    const { buildCssVars } = await loadBrandTheme("test");
    const spy = vi.spyOn(console, "warn").mockImplementation(() => {});
    const css = buildCssVars({ tokens: { accent: "not-a-color" } });
    expect(css).toBe(""); // still dropped -- fallback behaviour unchanged.
    expect(spy).not.toHaveBeenCalled(); // but no console noise in non-dev.
    spy.mockRestore();
  });

  it("zero-regression: a fully-valid theme emits identical CSS and never warns", async () => {
    const { buildCssVars, DEFAULT_BRAND_SAMPLE } = await loadBrandTheme("development");
    const spy = vi.spyOn(console, "warn").mockImplementation(() => {});
    const css = buildCssVars(DEFAULT_BRAND_SAMPLE);
    expect(css).toContain("--primary:174 68% 50%");
    expect(css.replace(/^:root\{|\}$/g, "").split(";")).toHaveLength(25);
    expect(spy).not.toHaveBeenCalled();
    spy.mockRestore();
  });
});

// --------------------------------------------------------------------------
// 3. adminTheme GENERATED-entry branch: source="brand" + missing/malformed primary.
// --------------------------------------------------------------------------
describe("resolveAdminTheme -- generated-entry disclosure", () => {
  const MONO_SVG =
    '<svg xmlns="http://www.w3.org/2000/svg" width="8" height="8"><rect width="8" height="8"/></svg>';

  it("warns (dev) + falls back to the default cyan when source='brand' has NO primary", async () => {
    const registry = {
      acme: {
        brand: { name: "Acme Co", logoAlt: "Acme Co", tokens: {} }, // no primary
        logoPath: null,
        monogramSvg: MONO_SVG,
        title: "Acme Co -- Capability Console",
        source: "brand",
      },
    };
    const { resolveAdminTheme, CEXAI_ACCENT_HSL } = await loadAdminThemeWithGenerated(
      registry,
      "development",
    );
    const spy = vi.spyOn(console, "warn").mockImplementation(() => {});
    const theme = resolveAdminTheme("acme");
    expect(theme).not.toBeNull();
    expect(theme!.accentHsl).toBe(CEXAI_ACCENT_HSL); // zero-regression fallback.
    expect(spy).toHaveBeenCalledTimes(1);
    expect(spy.mock.calls[0][0]).toContain("acme");
    expect(spy.mock.calls[0][0]).toContain("missing");
    spy.mockRestore();
  });

  it("warns (dev) + falls back to the default cyan when source='brand' has a MALFORMED primary", async () => {
    const registry = {
      acme: {
        brand: { name: "Acme Co", logoAlt: "Acme Co", tokens: { primary: "not-a-color" } },
        logoPath: null,
        monogramSvg: MONO_SVG,
        title: "Acme Co -- Capability Console",
        source: "brand",
      },
    };
    const { resolveAdminTheme, CEXAI_ACCENT_HSL } = await loadAdminThemeWithGenerated(
      registry,
      "development",
    );
    const spy = vi.spyOn(console, "warn").mockImplementation(() => {});
    const theme = resolveAdminTheme("acme");
    expect(theme!.accentHsl).toBe(CEXAI_ACCENT_HSL);
    expect(spy).toHaveBeenCalledTimes(1);
    expect(spy.mock.calls[0][0]).toContain("malformed");
    spy.mockRestore();
  });

  it("does NOT warn for the honest source='default' case (never a bug)", async () => {
    const registry = {
      bare: {
        brand: { name: "Bare Co", logoAlt: "Bare Co", tokens: {} },
        logoPath: null,
        monogramSvg: MONO_SVG,
        title: "Bare Co -- Capability Console",
        source: "default",
      },
    };
    const { resolveAdminTheme, CEXAI_ACCENT_HSL } = await loadAdminThemeWithGenerated(
      registry,
      "development",
    );
    const spy = vi.spyOn(console, "warn").mockImplementation(() => {});
    const theme = resolveAdminTheme("bare");
    expect(theme!.accentHsl).toBe(CEXAI_ACCENT_HSL);
    expect(spy).not.toHaveBeenCalled(); // source="default" is an honest, undisclosed default.
    spy.mockRestore();
  });

  it("zero-regression: a WELL-FORMED source='brand' entry derives its accent and never warns", async () => {
    const registry = {
      acme: {
        brand: { name: "Acme Co", logoAlt: "Acme Co", tokens: { primary: "286 64% 42%" } },
        logoPath: null,
        monogramSvg: MONO_SVG,
        title: "Acme Co -- Capability Console",
        source: "brand",
      },
    };
    const { resolveAdminTheme, CEXAI_ACCENT_HSL } = await loadAdminThemeWithGenerated(
      registry,
      "development",
    );
    const spy = vi.spyOn(console, "warn").mockImplementation(() => {});
    const theme = resolveAdminTheme("acme");
    expect(theme!.accentHsl).not.toBe(CEXAI_ACCENT_HSL); // a REAL derived accent, not the default.
    expect(spy).not.toHaveBeenCalled();
    spy.mockRestore();
  });

  it("stays silent outside development even when it would warn in dev", async () => {
    const registry = {
      acme: {
        brand: { name: "Acme Co", logoAlt: "Acme Co", tokens: {} },
        logoPath: null,
        monogramSvg: MONO_SVG,
        title: "Acme Co -- Capability Console",
        source: "brand",
      },
    };
    const { resolveAdminTheme, CEXAI_ACCENT_HSL } = await loadAdminThemeWithGenerated(
      registry,
      "test",
    );
    const spy = vi.spyOn(console, "warn").mockImplementation(() => {});
    const theme = resolveAdminTheme("acme");
    expect(theme!.accentHsl).toBe(CEXAI_ACCENT_HSL); // fallback unchanged.
    expect(spy).not.toHaveBeenCalled(); // but no console noise outside dev.
    spy.mockRestore();
  });
});

// --------------------------------------------------------------------------
// 4. adminTheme MANUAL-row branch (ADMIN_TENANTS['demo-orbit']): a corrupted
//    brand.tokens.primary on the CURATED entry itself.
// --------------------------------------------------------------------------
describe("resolveAdminTheme -- manual ADMIN_TENANTS-row disclosure", () => {
  it("warns (dev) + returns null when demo-orbit's primary is malformed", async () => {
    const { resolveAdminTheme } = await loadAdminThemeWithCorruptOrbitPrimary(
      "not-a-color",
      "development",
    );
    const spy = vi.spyOn(console, "warn").mockImplementation(() => {});
    const theme = resolveAdminTheme("demo-orbit");
    expect(theme).toBeNull(); // zero-regression: still degrades to the default cyan.
    expect(spy).toHaveBeenCalledTimes(1);
    expect(spy.mock.calls[0][0]).toContain("demo-orbit");
    expect(spy.mock.calls[0][0]).toContain("malformed");
    spy.mockRestore();
  });

  it("warns (dev) + returns null when demo-orbit's primary is MISSING", async () => {
    const { resolveAdminTheme } = await loadAdminThemeWithCorruptOrbitPrimary(
      undefined,
      "development",
    );
    const spy = vi.spyOn(console, "warn").mockImplementation(() => {});
    const theme = resolveAdminTheme("demo-orbit");
    expect(theme).toBeNull();
    expect(spy).toHaveBeenCalledTimes(1);
    expect(spy.mock.calls[0][0]).toContain("missing");
    spy.mockRestore();
  });

  it("zero-regression: the REAL (unmocked, well-formed) demo-orbit entry never warns", async () => {
    vi.resetModules();
    vi.stubEnv("NODE_ENV", "development");
    vi.stubEnv("NEXT_PUBLIC_TENANT", "demo-orbit");
    const { resolveAdminTheme } = await import("@/lib/adminTheme");
    const spy = vi.spyOn(console, "warn").mockImplementation(() => {});
    const theme = resolveAdminTheme("demo-orbit");
    expect(theme).not.toBeNull();
    expect(theme!.brandName).toBe("Orbit Tech");
    expect(spy).not.toHaveBeenCalled();
    spy.mockRestore();
  });
});
