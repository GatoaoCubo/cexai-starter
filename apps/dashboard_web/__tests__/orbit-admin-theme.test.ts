// BUILD R2 -- ORBIT TECH ADMIN THEME + COMPOSITION PROOF (P0-A rebrand: fictitious
// "Orbit Tech", formerly a real-brand fixture named after this file's original test subject).
//
// Proves the SAME admin dashboard themes to Orbit Tech's brand (a fictitious IT-services
// tenant) instead of the default sample, at the two layers the founder asked for:
//
//   1. THEME -- buildCssVars(ORBIT_BRAND_SAMPLE) emits Orbit Tech's reskin into the
//      :root cascade: ROYAL BLUE primary/brand/accent/ring ("231 48% 48%") + RED
//      highlight ("4 90% 58%"), deliberately NOT the default sample's teal ("174 68% 50%").
//      The 24 token css-vars + the font line are present; the values are the EXACT ones
//      cex_tenant_bootstrap emitted into brand.config.ts for tenant=demo-orbit (one
//      reskin file, both surfaces).
//
//   2. COMPOSITION -- the dashboard composes Orbit Tech's enabled_capabilities through
//      the EXISTING registry attach model (fxSetCapability attach/detach -- the exact
//      path ApiClient uses in fixtures mode, mirroring the live PATCH /capabilities/{slug}
//      contract). An IT-services tenant pulls a sensible starter set; every attached slug
//      is DECLARED (never fabricated); an undeclared slug is refused 409. The grid grows
//      with the attached cards and shrinks back on detach.
//
// ZERO-REGRESSION: this is an ADD-ONLY test. It mutates the shared FIXTURE_CARDS enabled
// flags via fxSetCapability and RESTORES every card it touched in afterEach (the same
// self-restoring discipline as compose-picker.test.tsx / leads-fixture.test.ts), so the
// default theme + every existing suite stay byte-unchanged on re-run.

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import {
  buildCssVars,
  DEFAULT_BRAND_SAMPLE,
  ORBIT_BRAND_SAMPLE,
} from "@/lib/brandTheme";
import {
  fxGetCapabilitiesConfig,
  fxListCards,
  fxSetCapability,
} from "@/lib/fixtures";

// --------------------------------------------------------------------------
// 1. THEME -- buildCssVars emits Orbit Tech's blue/red :root (not the default teal).
// --------------------------------------------------------------------------

// Orbit Tech's load-bearing brand colours (the reskin axis):
const ORBIT_BLUE = "231 48% 48%"; // primary / brand / accent / ring
const ORBIT_RED = "4 90% 58%"; // highlight
const DEFAULT_TEAL = "174 68% 50%"; // the default sample's primary/brand

describe("Orbit Tech admin theme -- buildCssVars emits the blue/red reskin", () => {
  it("emits Orbit Tech's ROYAL BLUE on primary/brand/accent/ring", () => {
    const css = buildCssVars(ORBIT_BRAND_SAMPLE);
    expect(css.startsWith(":root{")).toBe(true);
    expect(css).toContain("--primary:" + ORBIT_BLUE);
    expect(css).toContain("--brand:" + ORBIT_BLUE);
    expect(css).toContain("--accent:" + ORBIT_BLUE);
    expect(css).toContain("--ring:" + ORBIT_BLUE);
  });

  it("emits Orbit Tech's RED highlight", () => {
    const css = buildCssVars(ORBIT_BRAND_SAMPLE);
    expect(css).toContain("--highlight:" + ORBIT_RED);
    expect(css).toContain("--highlight-foreground:0 0% 100%");
  });

  it("is NOT the default teal sample (the admin reads as Orbit Tech, not the sample)", () => {
    const orbit = buildCssVars(ORBIT_BRAND_SAMPLE);
    const defaultCss = buildCssVars(DEFAULT_BRAND_SAMPLE);
    // Orbit Tech carries no default teal anywhere in its cascade.
    expect(orbit).not.toContain(DEFAULT_TEAL);
    // and the two themes differ (same builder, different brand -> different :root).
    expect(orbit).not.toBe(defaultCss);
    // sanity: the default sample still emits its teal (the default is untouched).
    expect(defaultCss).toContain("--primary:" + DEFAULT_TEAL);
  });

  it("emits the full 24-token contract + the font line (zero-regression shape)", () => {
    const css = buildCssVars(ORBIT_BRAND_SAMPLE);
    // Orbit Tech's neutral surface + radius come through too.
    expect(css).toContain("--background:0 0% 100%");
    expect(css).toContain("--foreground:0 0% 13%");
    expect(css).toContain("--radius:0.625rem");
    expect(css).toContain("--font-family-base:Inter, -apple-system, Segoe UI, sans-serif");
    // 24 tokens + 1 font line = 25 declarations (every token value is valid -> none dropped).
    expect(css.replace(/^:root\{|\}$/g, "").split(";")).toHaveLength(25);
  });
});

// --------------------------------------------------------------------------
// 2. COMPOSITION -- compose Orbit Tech's enabled_capabilities via the attach model.
// --------------------------------------------------------------------------

// A sensible STARTER composition for an IT-services tenant. Each slug is a DECLARED
// base card; we attach the ones that aren't already on at rest and prove the round-trip.
// (research = service intelligence; ads/landing = service marketing; pricing = service
//  quoting; brandbook = the tenant's own brand book.) These mirror the bootstrap's
// DEFAULT_STARTER_CAPABILITIES that cex_tenant_bootstrap seeded for demo-orbit.
const ORBIT_COMPOSITION = ["research", "ads", "pricing", "landing", "brandbook"];

/** Snapshot the enabled flag of each card we will touch, so afterEach restores it
 *  EXACTLY (a card enabled at rest is re-enabled; a disabled one is re-disabled). */
function snapshotEnabled(slugs: string[]): Record<string, boolean> {
  const cfg = fxGetCapabilitiesConfig();
  const enabledSet = new Set(cfg.enabled);
  const snap: Record<string, boolean> = {};
  for (const s of slugs) snap[s] = enabledSet.has(s);
  return snap;
}

let baseline: Record<string, boolean> = {};

beforeEach(() => {
  baseline = snapshotEnabled(ORBIT_COMPOSITION);
});

afterEach(async () => {
  // restore every touched card to its at-rest enabled state (self-restoring discipline).
  for (const [slug, wasEnabled] of Object.entries(baseline)) {
    try {
      await fxSetCapability(slug, wasEnabled ? "attach" : "detach");
    } catch {
      /* declared slugs only; ignore */
    }
  }
});

describe("Orbit Tech admin -- composes enabled_capabilities via the registry attach model", () => {
  it("every Orbit Tech starter slug is DECLARED (never fabricates a capability)", () => {
    const cfg = fxGetCapabilitiesConfig();
    for (const slug of ORBIT_COMPOSITION) {
      expect(cfg.declared, `${slug} is declared`).toContain(slug);
    }
  });

  it("attaching the Orbit Tech set puts exactly those cards on the grid (attach model)", async () => {
    // First detach all five so we attach from a known-empty baseline for this set.
    for (const slug of ORBIT_COMPOSITION) {
      await fxSetCapability(slug, "detach");
    }
    let grid = fxListCards().map((c) => c.capability);
    for (const slug of ORBIT_COMPOSITION) {
      expect(grid, `${slug} off the grid while detached`).not.toContain(slug);
    }

    // Now COMPOSE Orbit Tech's dashboard: attach each starter capability.
    let cfg = fxGetCapabilitiesConfig();
    for (const slug of ORBIT_COMPOSITION) {
      cfg = await fxSetCapability(slug, "attach");
      expect(cfg.enabled, `${slug} now enabled`).toContain(slug);
      expect(cfg.disabled, `${slug} no longer disabled`).not.toContain(slug);
    }

    // the composed grid now carries every Orbit Tech capability (the admin surface is Orbit Tech's).
    grid = fxListCards().map((c) => c.capability);
    for (const slug of ORBIT_COMPOSITION) {
      expect(grid, `${slug} on the composed grid`).toContain(slug);
    }
  });

  it("attach -> grid grows by one + enabled +1; detach -> shrinks back (clean round-trip)", async () => {
    // exercise the round-trip on a single Orbit Tech card from its at-rest state.
    const slug = "pricing";
    await fxSetCapability(slug, "detach"); // known baseline: off
    const enabledBefore = fxGetCapabilitiesConfig().enabled.length;
    const gridBefore = fxListCards().length;
    expect(fxListCards().map((c) => c.capability)).not.toContain(slug);

    // ATTACH -> +1 enabled, grid grows by one, the card appears.
    const afterAttach = await fxSetCapability(slug, "attach");
    expect(afterAttach.enabled).toContain(slug);
    expect(afterAttach.enabled.length).toBe(enabledBefore + 1);
    const grown = fxListCards();
    expect(grown.length).toBe(gridBefore + 1);
    expect(grown.map((c) => c.capability)).toContain(slug);

    // DETACH -> back to baseline.
    const afterDetach = await fxSetCapability(slug, "detach");
    expect(afterDetach.enabled).not.toContain(slug);
    expect(afterDetach.enabled.length).toBe(enabledBefore);
    expect(fxListCards().length).toBe(gridBefore);
  });

  it("refuses an UNDECLARED Orbit-Tech-shaped slug (never force-enables a fake card) -- 409", async () => {
    // an IT-services-sounding but UNDECLARED slug must be refused, not fabricated.
    await expect(
      fxSetCapability("notebook_repair_quote", "attach"),
    ).rejects.toMatchObject({ status: 409, reason: "not_declared" });
  });
});
