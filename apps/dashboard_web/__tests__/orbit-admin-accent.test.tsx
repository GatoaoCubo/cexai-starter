// ORBIT TECH ADMIN THEME -- the ACCENT-INJECTION + header-logo proof (P0-A rebrand:
// fictitious "Orbit Tech", formerly a real-brand fixture named after this file's original
// test subject).
//
// The sibling orbit-admin-theme.test.ts proves the buildCssVars reskin (the
// 24-token brand cascade). THIS suite proves the actual admin-shell wiring the
// founder asked for: when the ACTIVE TENANT is Orbit Tech, the admin's ONE accent
// (tailwind synapse.DEFAULT, --accent) reads as Orbit Tech's BRAND BLUE -- derived
// to be AA-LEGIBLE on the near-black dark-lab surface -- and the header shows the
// Orbit Tech logo + name. With the DEFAULT (no active tenant) the emitted accent is
// the EXACT current cyan and the brand mark is the CEXAI mark -- byte-unchanged.
//
// The active tenant is selected by NEXT_PUBLIC_TENANT (config.activeTenant), read
// at module load. We vi.stubEnv + vi.resetModules so each case re-imports the
// modules under a fresh env -- ZERO-REGRESSION (no global mutation leaks; the env
// is unstubbed in afterEach).

import { describe, it, expect, vi, afterEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";

const CEXAI_CYAN = "171 77% 64%"; // synapse.DEFAULT (#5EEAD4) as HSL -- the default accent.
const ORBIT_BRAND_BLUE = "231 48% 48%"; // the RAW brand blue (too dark for dark-lab).

afterEach(() => {
  vi.unstubAllEnvs();
  vi.resetModules();
});

/** Re-import lib/adminTheme under a given NEXT_PUBLIC_TENANT value. */
async function loadAdminTheme(tenant: string | undefined) {
  vi.resetModules();
  if (tenant === undefined) {
    vi.stubEnv("NEXT_PUBLIC_TENANT", "");
  } else {
    vi.stubEnv("NEXT_PUBLIC_TENANT", tenant);
  }
  return import("@/lib/adminTheme");
}

// --------------------------------------------------------------------------
// 1. ON-DARK derivation: brand HUE preserved, but LEGIBLE on ink.
// --------------------------------------------------------------------------

describe("deriveOnDarkAccent -- hue-preserving, legible-on-dark", () => {
  it("keeps the Orbit Tech brand HUE (~231) but is NOT the raw dark brand blue", async () => {
    const { deriveOnDarkAccent } = await loadAdminTheme("demo-orbit");
    const onDark = deriveOnDarkAccent(ORBIT_BRAND_BLUE);
    expect(onDark).not.toBeNull();
    const [h, s, l] = onDark!.split(/\s+/).map((p) => parseInt(p, 10));
    // hue is unchanged (it is unmistakably the brand blue) ...
    expect(h).toBe(231);
    // ... but lightness was RAISED off the raw 48 (so it reads on near-black ink) ...
    expect(l).toBeGreaterThan(48);
    expect(l).toBeGreaterThanOrEqual(62); // into the legible band.
    // ... and saturation lifted to the floor (crisp, not muddy).
    expect(s).toBeGreaterThanOrEqual(72);
    // and it is decidedly NOT the raw brand triplet.
    expect(onDark).not.toBe(ORBIT_BRAND_BLUE);
  });

  it("returns null on a malformed brand triplet (caller degrades to the default)", async () => {
    const { deriveOnDarkAccent } = await loadAdminTheme("demo-orbit");
    expect(deriveOnDarkAccent("not-a-triplet")).toBeNull();
    expect(deriveOnDarkAccent("400 50% 50%")).toBeNull(); // out-of-range hue.
  });
});

// --------------------------------------------------------------------------
// 2. With activeTenant=demo-orbit: --accent is the on-dark brand blue + logo.
// --------------------------------------------------------------------------

describe("activeTenant=demo-orbit -- admin accent reads as Orbit Tech brand blue", () => {
  it("emits :root{--accent: <on-dark brand blue>} (NOT the cyan, NOT the raw 231 48% 48%)", async () => {
    const { resolveAdminTheme, buildAccentRootStyle } = await loadAdminTheme("demo-orbit");
    const theme = resolveAdminTheme();
    expect(theme).not.toBeNull();

    const style = buildAccentRootStyle(theme);
    expect(style.startsWith(":root{--accent:")).toBe(true);

    // the injected accent is the brand HUE 231, lightness RAISED -> legible.
    const m = /:root\{--accent:(\d{1,3}) (\d{1,3})% (\d{1,3})%\}/.exec(style);
    expect(m).not.toBeNull();
    const [h, s, l] = [m![1], m![2], m![3]].map((x) => parseInt(x, 10));
    expect(h).toBe(231); // brand hue.
    expect(l).toBeGreaterThanOrEqual(62); // lightened for legibility on ink.
    expect(s).toBeGreaterThanOrEqual(72);

    // NOT the default cyan, and NOT the raw (too-dark) brand blue.
    expect(style).not.toContain(CEXAI_CYAN);
    expect(style).not.toContain(ORBIT_BRAND_BLUE);
  });

  it("the injected accent passes the SAME HSL-shape guard buildCssVars uses", async () => {
    const { resolveAdminTheme } = await loadAdminTheme("demo-orbit");
    const { isHslTriplet } = await import("@/lib/brandTheme");
    const theme = resolveAdminTheme();
    expect(theme).not.toBeNull();
    expect(isHslTriplet(theme!.accentHsl)).toBe(true);
  });

  it("exposes the Orbit Tech logo path + brand name for the header", async () => {
    const { resolveAdminTheme } = await loadAdminTheme("demo-orbit");
    const theme = resolveAdminTheme();
    expect(theme!.brandName).toBe("Orbit Tech");
    expect(theme!.logoPath).toBe("/tenants/demo-orbit/logo.png");
  });
});

// --------------------------------------------------------------------------
// 3. DEFAULT (no / "default" / "cexai" tenant): cyan, no logo -- byte-unchanged.
// --------------------------------------------------------------------------

describe("default (no active tenant) -- the CEXAI cyan dark-lab, unchanged", () => {
  it("resolveAdminTheme() is null and NO accent is injected (cyan fallback stands)", async () => {
    const { resolveAdminTheme, buildAccentRootStyle, CEXAI_ACCENT_HSL } =
      await loadAdminTheme(undefined);
    const theme = resolveAdminTheme();
    expect(theme).toBeNull();
    // nothing injected -> the tailwind fallback (the exact current cyan) renders.
    expect(buildAccentRootStyle(theme)).toBe("");
    // and the documented default IS the exact current cyan.
    expect(CEXAI_ACCENT_HSL).toBe(CEXAI_CYAN);
  });

  it('"default" and "cexai" selectors also degrade to no override', async () => {
    for (const sel of ["default", "cexai", "DEFAULT", "CEXAI"]) {
      const { resolveAdminTheme, buildAccentRootStyle } = await loadAdminTheme(sel);
      const theme = resolveAdminTheme();
      expect(theme, `${sel} -> no theme`).toBeNull();
      expect(buildAccentRootStyle(theme)).toBe("");
    }
  });

  it("an UNKNOWN tenant id degrades to the default (no override, never throws)", async () => {
    const { resolveAdminTheme, buildAccentRootStyle } = await loadAdminTheme("acme_unknown");
    const theme = resolveAdminTheme();
    expect(theme).toBeNull();
    expect(buildAccentRootStyle(theme)).toBe("");
  });
});

// --------------------------------------------------------------------------
// 4. HEADER mark: Orbit Tech logo for the tenant, CEXAI brand mark for the default.
// --------------------------------------------------------------------------

/** Re-import the Wordmark component under a fresh NEXT_PUBLIC_TENANT env. */
async function loadWordmark(tenant: string | undefined) {
  vi.resetModules();
  vi.stubEnv("NEXT_PUBLIC_TENANT", tenant ?? "");
  const mod = await import("@/components/ui");
  return mod.Wordmark;
}

describe("Wordmark header -- tenant logo vs default brand mark", () => {
  it("renders the Orbit Tech logo (/tenants/demo-orbit/logo.png) + name for the tenant", async () => {
    const Wordmark = await loadWordmark("demo-orbit");
    render(<Wordmark />);
    const img = screen.getByAltText("Orbit Tech - Solucoes em Tecnologia") as HTMLImageElement;
    expect(img).toBeInTheDocument();
    expect(img.getAttribute("src")).toBe("/tenants/demo-orbit/logo.png");
    expect(screen.getByText("Orbit Tech")).toBeInTheDocument();
    cleanup();
  });

  it("renders the CEXAI brand MARK (an inline svg, no img) + 'CEXAI' for the default", async () => {
    const Wordmark = await loadWordmark(undefined);
    const { container } = render(<Wordmark />);
    // no tenant logo image at all.
    expect(container.querySelector("img")).toBeNull();
    // the inline brand-mark svg is present.
    expect(container.querySelector("svg")).not.toBeNull();
    expect(screen.getByText("CEXAI")).toBeInTheDocument();
    cleanup();
  });
});
