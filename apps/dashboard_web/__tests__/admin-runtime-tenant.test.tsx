// ADMIN RUNTIME-TENANT (inc2) -- the ?tenant query param drives the admin THEME +
// preview-tenant at RUNTIME, while the DATA tenant_id stays strictly auth/RLS-bound.
//
// This suite proves the contract the founder asked for:
//   1. ?tenant=demo-orbit            -> the Orbit Tech admin theme (accent + brand).
//   2. no / "" / "cexai" / "default" -> the default CEXAI cyan (no override).
//   3. invalid / unknown slug        -> default, with NO crash and NO data leak.
//   4. SECURITY (load-bearing): the DATA tenant resolver (tenantFromSession) reads
//      ONLY the session JWT claim -- ?tenant can neither override nor conjure it.
//   5. wiring: <TenantThemeProvider> + Wordmark follow ?tenant at runtime (the
//      accent is applied to <html>, the preview brand is Orbit Tech's), and absent
//      ?tenant is byte-identical to the default.
//
// adminTheme/config read NEXT_PUBLIC_TENANT at module load, so the env-sensitive
// cases vi.stubEnv + vi.resetModules + re-import (mirrors orbit-admin-accent).

import { describe, it, expect, vi, afterEach, beforeEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";

const CEXAI_CYAN = "171 77% 64%"; // synapse.DEFAULT -- the default accent.
const ORBIT_BRAND_BLUE = "231 48% 48%"; // the RAW (too-dark) brand blue.

// A mutable holder so each render can set the ?tenant the mocked useSearchParams returns.
const nav = vi.hoisted(() => ({ params: new URLSearchParams() }));
vi.mock("next/navigation", () => ({
  useSearchParams: () => nav.params,
}));

afterEach(() => {
  cleanup();
  vi.unstubAllEnvs();
  vi.resetModules();
  // never leak an inline accent between cases.
  document.documentElement.removeAttribute("style");
});

beforeEach(() => {
  nav.params = new URLSearchParams();
  document.documentElement.removeAttribute("style");
});

/** Re-import lib/adminTheme under a given NEXT_PUBLIC_TENANT env (undefined => unset). */
async function loadAdminTheme(envTenant?: string) {
  vi.resetModules();
  vi.stubEnv("NEXT_PUBLIC_TENANT", envTenant ?? "");
  return import("@/lib/adminTheme");
}

/** Re-import the shell atoms (Wordmark + provider) under a fresh env. */
async function loadShell(envTenant?: string) {
  vi.resetModules();
  vi.stubEnv("NEXT_PUBLIC_TENANT", envTenant ?? "");
  const ui = await import("@/components/ui");
  const tt = await import("@/components/TenantTheme");
  return { Wordmark: ui.Wordmark, TenantThemeProvider: tt.TenantThemeProvider };
}

// --------------------------------------------------------------------------
// 1. ?tenant=demo-orbit -> the Orbit Tech theme (param drives, env unset).
// --------------------------------------------------------------------------

describe("?tenant=demo-orbit -> Orbit Tech admin theme", () => {
  it("resolveAdminThemeFromParam('demo-orbit') yields the on-dark Orbit Tech brand", async () => {
    const { resolveAdminThemeFromParam } = await loadAdminTheme(undefined); // env unset
    const theme = resolveAdminThemeFromParam("demo-orbit");
    expect(theme).not.toBeNull();
    expect(theme!.brandName).toBe("Orbit Tech");
    expect(theme!.logoPath).toBe("/tenants/demo-orbit/logo.png");
    // accent: brand hue 231, lightened off the raw 48 so it reads on ink; NOT cyan/raw.
    const [h, , l] = theme!.accentHsl.split(/\s+/).map((p) => parseInt(p, 10));
    expect(h).toBe(231);
    expect(l).toBeGreaterThanOrEqual(62);
    expect(theme!.accentHsl).not.toBe(CEXAI_CYAN);
    expect(theme!.accentHsl).not.toBe(ORBIT_BRAND_BLUE);
  });

  it("the param OVERRIDES the env: ?tenant=cexai beats NEXT_PUBLIC_TENANT only when it resolves", async () => {
    // param override is null for a default selector -> falls back to env (demo-orbit here).
    const { resolveAdminThemeParamOverride, resolveAdminThemeFromParam } =
      await loadAdminTheme("demo-orbit");
    expect(resolveAdminThemeParamOverride("cexai")).toBeNull(); // default selector -> no override
    expect(resolveAdminThemeFromParam("cexai")!.brandName).toBe("Orbit Tech"); // env stands
    // a KNOWN tenant slug DOES override (param wins over env).
    expect(resolveAdminThemeParamOverride("demo-orbit")!.brandName).toBe("Orbit Tech");
  });

  it("an array ?tenant=a&tenant=b takes the first entry", async () => {
    const { resolveAdminThemeFromParam } = await loadAdminTheme(undefined);
    expect(resolveAdminThemeFromParam(["demo-orbit", "acme"])!.brandName).toBe(
      "Orbit Tech",
    );
    expect(resolveAdminThemeFromParam(["acme", "demo-orbit"])).toBeNull(); // first is unknown
  });
});

// --------------------------------------------------------------------------
// 2. no param (and default selectors) -> default cyan, byte-identical.
// --------------------------------------------------------------------------

describe("no / default ?tenant -> the CEXAI cyan default (env unset)", () => {
  it("absent param (null / undefined / '') -> null theme (default)", async () => {
    const { resolveAdminThemeFromParam, resolveAdminThemeParamOverride } =
      await loadAdminTheme(undefined);
    for (const p of [null, undefined, ""] as const) {
      expect(resolveAdminThemeParamOverride(p)).toBeNull();
      expect(resolveAdminThemeFromParam(p)).toBeNull();
    }
  });

  it('"cexai" / "default" selectors -> null (no override)', async () => {
    const { resolveAdminThemeFromParam } = await loadAdminTheme(undefined);
    for (const sel of ["cexai", "default", "CEXAI", "Default"]) {
      expect(resolveAdminThemeFromParam(sel), `${sel} -> default`).toBeNull();
    }
  });
});

// --------------------------------------------------------------------------
// 3. invalid / unknown slug -> default, NO crash, NO leak.
// --------------------------------------------------------------------------

describe("invalid / unknown ?tenant -> default (no crash, no leak)", () => {
  it("an unknown but well-formed slug -> null", async () => {
    const { resolveAdminThemeFromParam, resolveAdminThemeParamOverride } =
      await loadAdminTheme(undefined);
    expect(resolveAdminThemeParamOverride("acme_unknown")).toBeNull();
    expect(resolveAdminThemeFromParam("acme_unknown")).toBeNull();
  });

  it("malformed slugs are rejected by SHAPE (path / SQL / space / uppercase / over-long)", async () => {
    const { isValidTenantSlug, resolveAdminThemeFromParam } =
      await loadAdminTheme(undefined);
    const bad = [
      "../../etc/passwd",
      "a b",
      "Demo-Orbit", // uppercase (public links emit lowercase)
      "drop table;",
      "x".repeat(65),
      "-leading",
      "_leading",
      ".leading",
      "a/b",
      "<script>",
    ];
    for (const slug of bad) {
      expect(isValidTenantSlug(slug), `${slug} invalid`).toBe(false);
      expect(resolveAdminThemeFromParam(slug), `${slug} -> default`).toBeNull();
    }
  });

  it("prototype keys never resolve to a theme and never throw (own-property lookup)", async () => {
    const { resolveAdminThemeFromParam, resolveAdminThemeParamOverride } =
      await loadAdminTheme(undefined);
    // "constructor"/"toString" pass the slug shape but are inherited prototype members;
    // "__proto__" fails the shape guard. None may resolve, none may throw.
    for (const slug of ["constructor", "toString", "valueof", "__proto__", "hasownproperty"]) {
      expect(() => resolveAdminThemeParamOverride(slug)).not.toThrow();
      expect(resolveAdminThemeFromParam(slug), `${slug} -> default`).toBeNull();
    }
  });
});

// --------------------------------------------------------------------------
// 4. SECURITY: the DATA tenant resolver reads ONLY the JWT -- never ?tenant.
// --------------------------------------------------------------------------

describe("DATA tenant_id is auth/RLS-bound -- ?tenant cannot reach it", () => {
  it("tenantFromSession returns the JWT claim regardless of a hostile ?tenant", async () => {
    vi.resetModules();
    // a URL that tries to assert ANOTHER tenant via the theme param:
    window.history.replaceState({}, "", "/dashboard?tenant=demo-orbit");
    nav.params = new URLSearchParams("tenant=demo-orbit");
    const { tenantFromSession } = await import("@/lib/supabase");

    // the data tenant follows the session JWT claim, NOT the URL param.
    const acme = { user: { app_metadata: { tenant_id: "tenant_acme" } } } as never;
    expect(tenantFromSession(acme)).toBe("tenant_acme");

    // ?tenant cannot CONJURE a data tenant when the JWT carries none (fail-closed).
    const noClaim = { user: { app_metadata: {} } } as never;
    expect(tenantFromSession(noClaim)).toBe("");
    expect(tenantFromSession(null)).toBe("");
  });

  it("the theme param and the data tenant are fully independent", async () => {
    vi.resetModules();
    const { resolveAdminThemeParamOverride } = await loadAdminTheme(undefined);
    const { tenantFromSession } = await import("@/lib/supabase");
    // ?tenant=demo-orbit themes the admin as Orbit Tech ...
    expect(resolveAdminThemeParamOverride("demo-orbit")!.brandName).toBe("Orbit Tech");
    // ... while the SAME request's data tenant stays whatever the JWT says (acme).
    const acme = { user: { app_metadata: { tenant_id: "tenant_acme" } } } as never;
    expect(tenantFromSession(acme)).toBe("tenant_acme");
  });
});

// --------------------------------------------------------------------------
// 5. WIRING: provider + Wordmark follow ?tenant at runtime.
// --------------------------------------------------------------------------

describe("TenantThemeProvider + Wordmark -- runtime ?tenant", () => {
  it("?tenant=demo-orbit -> Wordmark shows Orbit Tech + --accent applied to <html>", async () => {
    nav.params = new URLSearchParams("tenant=demo-orbit");
    const { Wordmark, TenantThemeProvider } = await loadShell(undefined); // env unset
    render(
      <TenantThemeProvider>
        <Wordmark />
      </TenantThemeProvider>,
    );
    // preview brand follows the param.
    expect(screen.getByText("Orbit Tech")).toBeInTheDocument();
    const img = screen.getByAltText(
      "Orbit Tech - Solucoes em Tecnologia",
    ) as HTMLImageElement;
    expect(img.getAttribute("src")).toBe("/tenants/demo-orbit/logo.png");
    // accent applied at runtime to the <html> inline style (brand hue 231).
    const accent = document.documentElement.style.getPropertyValue("--accent");
    expect(accent).toMatch(/^231 \d{1,3}% \d{1,3}%$/);
    expect(accent).not.toBe(CEXAI_CYAN);
  });

  it("no ?tenant + env unset -> Wordmark is CEXAI and NO inline --accent (byte-identical)", async () => {
    nav.params = new URLSearchParams(); // no tenant
    const { Wordmark, TenantThemeProvider } = await loadShell(undefined);
    render(
      <TenantThemeProvider>
        <Wordmark />
      </TenantThemeProvider>,
    );
    expect(screen.getByText("CEXAI")).toBeInTheDocument();
    // the provider touched nothing -> the tailwind cyan fallback stands.
    expect(document.documentElement.style.getPropertyValue("--accent")).toBe("");
  });

  it("unknown ?tenant -> Wordmark stays CEXAI and NO inline --accent (no leak)", async () => {
    nav.params = new URLSearchParams("tenant=acme_unknown");
    const { Wordmark, TenantThemeProvider } = await loadShell(undefined);
    render(
      <TenantThemeProvider>
        <Wordmark />
      </TenantThemeProvider>,
    );
    expect(screen.getByText("CEXAI")).toBeInTheDocument();
    expect(document.documentElement.style.getPropertyValue("--accent")).toBe("");
  });
});
