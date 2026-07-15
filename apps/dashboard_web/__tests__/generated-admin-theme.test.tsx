// R-006 ADMIN THEMING BRIDGE -- the GENERATED per-tenant theme registry
// (lib/generatedAdminThemes.json) consumed by lib/adminTheme.ts.
//
// Proves the 3 GDP-ratified decisions at the consumption seam:
//   D1: a generated source="brand" entry derives its on-dark accent from the brand
//       primary (hue-preserving); a source="default" entry keeps the EXACT default
//       cyan accent (the mechanic's honest default -- never a fabricated colour).
//   D2: a known tenant with no logo renders its MONOGRAM (data-URI img) -- never the
//       CEXAI mark, never empty. Unknown tenant -> the CEXAI mark, byte-identical.
//   D3: precedence manual ADMIN_TENANTS row > generated entry > default; per-tenant
//       <title> + favicon applied by the provider ONLY when the theme carries them.
//
// Harness mirrors admin-runtime-tenant.test.tsx (vi.stubEnv + vi.resetModules) plus
// vi.doMock of the generated JSON registry (per-test synthetic registries).

import { describe, it, expect, vi, afterEach, beforeEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";

const CEXAI_CYAN = "171 77% 64%"; // synapse.DEFAULT -- the default accent.

const MONO_SVG =
  '<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128"><rect width="128" height="128" fill="#123456"/><text>AC</text></svg>';

/** A well-formed generated entry for a brand WITH colours (source="brand"). */
function acmeBrandEntry() {
  return {
    brand: {
      name: "ACME Corp",
      logoAlt: "ACME Corp",
      tokens: { primary: "286 64% 42%" },
    },
    logoPath: null,
    monogramSvg: MONO_SVG,
    title: "ACME Corp -- Capability Console",
    source: "brand",
  };
}

/** A well-formed generated entry for a brand WITHOUT colours (source="default"). */
function bareDefaultEntry() {
  return {
    brand: { name: "Bare Co", logoAlt: "Bare Co", tokens: { primary: "222 15% 12%" } },
    logoPath: null,
    monogramSvg: MONO_SVG,
    title: "Bare Co -- Capability Console",
    source: "default",
  };
}

// A mutable holder so each render can set the ?tenant the mocked useSearchParams returns.
const nav = vi.hoisted(() => ({ params: new URLSearchParams() }));
vi.mock("next/navigation", () => ({
  useSearchParams: () => nav.params,
}));

afterEach(() => {
  cleanup();
  vi.unstubAllEnvs();
  vi.resetModules();
  vi.doUnmock("@/lib/generatedAdminThemes.json");
  document.documentElement.removeAttribute("style");
  document.title = "";
  document.getElementById("cexai-tenant-favicon")?.remove();
});

beforeEach(() => {
  nav.params = new URLSearchParams();
});

/** Re-import lib/adminTheme with a SYNTHETIC generated registry + env tenant. */
async function loadAdminTheme(registry: unknown, envTenant?: string) {
  vi.resetModules();
  vi.stubEnv("NEXT_PUBLIC_TENANT", envTenant ?? "");
  vi.doMock("@/lib/generatedAdminThemes.json", () => ({ default: registry }));
  return import("@/lib/adminTheme");
}

/** Re-import the shell atoms (Wordmark + provider) with a synthetic registry. */
async function loadShell(registry: unknown, envTenant?: string) {
  vi.resetModules();
  vi.stubEnv("NEXT_PUBLIC_TENANT", envTenant ?? "");
  vi.doMock("@/lib/generatedAdminThemes.json", () => ({ default: registry }));
  const ui = await import("@/components/ui");
  const tt = await import("@/components/TenantTheme");
  return { Wordmark: ui.Wordmark, TenantThemeProvider: tt.TenantThemeProvider };
}

// --------------------------------------------------------------------------
// 1. GENERATE + CONSUME (D1): a generated source="brand" entry themes the admin.
// --------------------------------------------------------------------------

describe("generated source='brand' entry -> derived on-dark accent", () => {
  it("resolveAdminTheme('acme') yields brand name, hue-preserved accent, monogram, title", async () => {
    const { resolveAdminTheme } = await loadAdminTheme({ acme: acmeBrandEntry() });
    const theme = resolveAdminTheme("acme");
    expect(theme).not.toBeNull();
    expect(theme!.brandName).toBe("ACME Corp");
    expect(theme!.title).toBe("ACME Corp -- Capability Console");
    expect(theme!.monogramSvg).toBe(MONO_SVG);
    expect(theme!.logoPath).toBeNull();
    // accent: brand hue 286 preserved, lightness lifted into the AA band; NOT the cyan.
    const [h, , l] = theme!.accentHsl.split(/\s+/).map((p) => parseInt(p, 10));
    expect(h).toBe(286);
    expect(l).toBeGreaterThanOrEqual(62);
    expect(theme!.accentHsl).not.toBe(CEXAI_CYAN);
  });

  it("the env tenant (NEXT_PUBLIC_TENANT) resolves through the generated registry too", async () => {
    const { resolveAdminTheme, buildAccentRootStyle } = await loadAdminTheme(
      { acme: acmeBrandEntry() },
      "acme",
    );
    const theme = resolveAdminTheme();
    expect(theme!.brandName).toBe("ACME Corp");
    // the server-injected style carries the derived accent (shape-guarded).
    expect(buildAccentRootStyle(theme)).toMatch(/^:root\{--accent:286 \d{1,3}% \d{1,3}%\}$/);
  });

  it("a malformed primary in a generated brand entry keeps the default cyan (degrade-never)", async () => {
    const entry = acmeBrandEntry();
    entry.brand.tokens = { primary: "not-a-triplet" };
    const { resolveAdminTheme } = await loadAdminTheme({ acme: entry });
    const theme = resolveAdminTheme("acme");
    expect(theme).not.toBeNull(); // identity (name/monogram/title) still applies...
    expect(theme!.accentHsl).toBe(CEXAI_CYAN); // ...but the accent never fabricates.
  });
});

// --------------------------------------------------------------------------
// 2. HONEST DEFAULT (D1): source="default" keeps the EXACT default cyan accent.
// --------------------------------------------------------------------------

describe("generated source='default' entry -> identity without a fabricated accent", () => {
  it("accent is byte-identical to the default cyan; monogram + title still carried", async () => {
    const { resolveAdminTheme, CEXAI_ACCENT_HSL } = await loadAdminTheme({
      bare: bareDefaultEntry(),
    });
    const theme = resolveAdminTheme("bare");
    expect(theme).not.toBeNull();
    expect(theme!.accentHsl).toBe(CEXAI_ACCENT_HSL);
    expect(theme!.accentHsl).toBe(CEXAI_CYAN);
    expect(theme!.brandName).toBe("Bare Co");
    expect(theme!.monogramSvg).toBe(MONO_SVG);
  });

  it("an entry claiming an unknown source is treated as 'default' (fail-toward-default)", async () => {
    const entry = bareDefaultEntry();
    (entry as Record<string, unknown>).source = "totally-brand-trust-me";
    const { resolveAdminTheme } = await loadAdminTheme({ bare: entry });
    expect(resolveAdminTheme("bare")!.accentHsl).toBe(CEXAI_CYAN);
  });
});

// --------------------------------------------------------------------------
// 3. PRECEDENCE (D3): manual ADMIN_TENANTS row > generated entry > default.
// --------------------------------------------------------------------------

describe("manual row WINS over a generated entry for the same slug", () => {
  it("a generated 'demo-orbit' impostor never shadows the manual Orbit Tech row", async () => {
    const impostor = {
      brand: { name: "Imposter", logoAlt: "Imposter", tokens: { primary: "100 70% 40%" } },
      logoPath: "/tenants/imposter/logo.png",
      monogramSvg: MONO_SVG,
      title: "Imposter -- Capability Console",
      source: "brand",
    };
    const { resolveAdminTheme } = await loadAdminTheme({ "demo-orbit": impostor });
    const theme = resolveAdminTheme("demo-orbit");
    expect(theme!.brandName).toBe("Orbit Tech"); // the MANUAL row
    expect(theme!.logoPath).toBe("/tenants/demo-orbit/logo.png");
    expect(theme!.accentHsl).toMatch(/^231 /); // manual brand hue, not the impostor's 100
    expect(theme!.title).toBeNull(); // manual row declares no title -> untouched
    expect(theme!.monogramSvg).toBeNull();
  });

  it("generated fills the slugs the manual map does NOT cover", async () => {
    const { resolveAdminTheme } = await loadAdminTheme({ acme: acmeBrandEntry() });
    expect(resolveAdminTheme("acme")!.brandName).toBe("ACME Corp"); // generated
    expect(resolveAdminTheme("demo-orbit")!.brandName).toBe("Orbit Tech"); // manual
    expect(resolveAdminTheme("nobody")).toBeNull(); // default
  });
});

// --------------------------------------------------------------------------
// 4. DEGRADE-NEVER: {} registry and malformed entries are byte-identical to today.
// --------------------------------------------------------------------------

describe("degrade-never: empty/malformed generated registries", () => {
  it("an empty registry ({}) -> unknown slug -> null (the default cyan dark-lab)", async () => {
    const { resolveAdminTheme, resolveAdminThemeFromParam } = await loadAdminTheme({});
    expect(resolveAdminTheme("acme")).toBeNull();
    expect(resolveAdminThemeFromParam("acme")).toBeNull();
  });

  it("a non-object registry / array registry -> empty (no crash)", async () => {
    for (const bad of ["nope", 42, null, ["x"]]) {
      const { resolveAdminTheme } = await loadAdminTheme(bad);
      expect(resolveAdminTheme("acme")).toBeNull();
    }
  });

  it("malformed entries are DROPPED (brand missing, nothing renderable, bad slug key)", async () => {
    const { resolveAdminTheme } = await loadAdminTheme({
      nobrand: { logoPath: null, monogramSvg: MONO_SVG, source: "brand" },
      nothing: { brand: { name: "", tokens: {} }, monogramSvg: "not-svg", source: "brand" },
      "Bad Slug!": acmeBrandEntry(),
      cexai: acmeBrandEntry(), // a default selector can never become a generated key
    });
    expect(resolveAdminTheme("nobrand")).toBeNull();
    expect(resolveAdminTheme("nothing")).toBeNull();
    expect(resolveAdminTheme("bad slug!")).toBeNull();
    expect(resolveAdminTheme("cexai")).toBeNull();
  });

  it("a non-same-origin / traversal logoPath is nulled (monogram then renders)", async () => {
    const external = acmeBrandEntry();
    external.logoPath = "https://evil.example/logo.png" as unknown as null;
    const traversal = acmeBrandEntry();
    traversal.logoPath = "/tenants/../secrets.png" as unknown as null;
    const { resolveAdminTheme } = await loadAdminTheme({
      acme: external,
      trav: traversal,
    });
    expect(resolveAdminTheme("acme")!.logoPath).toBeNull();
    expect(resolveAdminTheme("trav")!.logoPath).toBeNull();
  });

  it("prototype-member slugs never resolve through the generated registry (no crash)", async () => {
    const { resolveAdminTheme } = await loadAdminTheme({ acme: acmeBrandEntry() });
    for (const slug of ["constructor", "tostring", "hasownproperty", "valueof"]) {
      expect(() => resolveAdminTheme(slug)).not.toThrow();
      expect(resolveAdminTheme(slug)).toBeNull();
    }
  });
});

// --------------------------------------------------------------------------
// 5. WORDMARK (D2): monogram renders for a known logo-less tenant; CEXAI mark
//    stays ONLY for the default.
// --------------------------------------------------------------------------

describe("Wordmark monogram branch (D2: never a CEXAI mark for a known tenant)", () => {
  it("?tenant=acme (generated, no logo) -> data-URI monogram img, not the CEXAI mark", async () => {
    nav.params = new URLSearchParams("tenant=acme");
    const { Wordmark, TenantThemeProvider } = await loadShell({ acme: acmeBrandEntry() });
    render(
      <TenantThemeProvider>
        <Wordmark />
      </TenantThemeProvider>,
    );
    expect(screen.getByText("ACME Corp")).toBeInTheDocument();
    const img = screen.getByAltText("ACME Corp") as HTMLImageElement;
    expect(img.getAttribute("src")!.startsWith("data:image/svg+xml")).toBe(true);
  });

  it("no tenant -> the CEXAI inline-svg mark, byte-identical (zero-regression)", async () => {
    nav.params = new URLSearchParams();
    const { Wordmark, TenantThemeProvider } = await loadShell({});
    const { container } = render(
      <TenantThemeProvider>
        <Wordmark />
      </TenantThemeProvider>,
    );
    expect(screen.getByText("CEXAI")).toBeInTheDocument();
    expect(container.querySelector("svg")).not.toBeNull(); // the inline BrandMark
    expect(container.querySelector("img")).toBeNull();
  });
});

// --------------------------------------------------------------------------
// 6. TITLE + FAVICON (D3): applied opt-in by the provider, restored on unmount.
// --------------------------------------------------------------------------

describe("per-tenant <title> + favicon (D3)", () => {
  it("?tenant=acme sets document.title + a monogram favicon link; unmount restores", async () => {
    document.title = "CEXAI -- Capability Console";
    nav.params = new URLSearchParams("tenant=acme");
    const { Wordmark, TenantThemeProvider } = await loadShell({ acme: acmeBrandEntry() });
    const view = render(
      <TenantThemeProvider>
        <Wordmark />
      </TenantThemeProvider>,
    );
    expect(document.title).toBe("ACME Corp -- Capability Console");
    const link = document.getElementById("cexai-tenant-favicon") as HTMLLinkElement;
    expect(link).not.toBeNull();
    expect(link.getAttribute("href")!.startsWith("data:image/svg+xml")).toBe(true);
    view.unmount();
    expect(document.title).toBe("CEXAI -- Capability Console"); // restored
    expect(document.getElementById("cexai-tenant-favicon")).toBeNull(); // removed
  });

  it("a theme WITHOUT title/monogram (the manual Orbit Tech row) touches neither", async () => {
    document.title = "CEXAI -- Capability Console";
    nav.params = new URLSearchParams("tenant=demo-orbit");
    const { Wordmark, TenantThemeProvider } = await loadShell({});
    render(
      <TenantThemeProvider>
        <Wordmark />
      </TenantThemeProvider>,
    );
    expect(document.title).toBe("CEXAI -- Capability Console"); // untouched
    expect(document.getElementById("cexai-tenant-favicon")).toBeNull(); // untouched
  });
});
