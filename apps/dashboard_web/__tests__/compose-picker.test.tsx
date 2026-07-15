// Mission BUILD C -- the COMPOSE PICKER ("pull capabilities, compose your own dashboard").
//
// The founder's model made real: a tenant browses the platform catalog, PULLS a declared-
// but-disabled capability (attach), and its card appears on the grid; REMOVES one (detach)
// and it leaves. These tests prove that round-trip end-to-end in FIXTURES mode, at two
// layers:
//
//   1. Fixtures contract (direct fx* calls, the exact path ApiClient uses in fixtures mode):
//      attach -> the grid set grows + enabled count +1; detach -> shrinks; the picker only
//      ever shows DECLARED capabilities (never an invented one); the round-trip is clean.
//   2. Component wiring: the real CapabilitiesPage (grid + picker) -- opening the picker
//      shows the available (declared-but-disabled) set, and clicking "Add" grows the GRID
//      and bumps the enabled stat. ZERO-REGRESSION: a closed picker leaves the grid showing
//      exactly the enabled cards (the disabled ones are absent, mirroring live).
//
// Driven offline by FORCING fixtures mode (mock @/lib/config) so the REAL ApiClient routes
// to lib/fixtures, and mocking @/lib/auth for a token. fxSetCapability mutates the shared
// FIXTURE_CARDS module state, so every test RESTORES the disabled set it touched (the same
// self-restoring discipline as leads-fixture.test.ts) to keep re-runs stable.

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor, within } from "@testing-library/react";

// Force the DATA-LAYER into fixtures mode regardless of env. authMode is irrelevant here
// (the page reads config.fixtures via ApiClient, and useAuth is mocked below).
vi.mock("@/lib/config", () => ({
  config: { fixtures: true, authMode: "dev", apiUrl: "", brandName: "CEXAI" },
  hasSupabase: () => false,
}));

// A stable session so CapabilitiesPage builds an ApiClient and renders.
vi.mock("@/lib/auth", () => ({
  useAuth: () => ({
    session: {
      access_token: "jwt-test",
      tenant_id: "11111111-1111-4111-8111-111111111111",
      tenant_label: "Demo Tenant",
      email: "operator@demo.local",
    },
  }),
}));

import {
  fxGetCapabilitiesConfig,
  fxListCards,
  fxListCatalog,
  fxSetCapability,
} from "@/lib/fixtures";
import { ModuleManager } from "@/components/ModuleManager";
import CapabilitiesPage from "@/app/dashboard/page";

// The three declared-but-DISABLED capabilities BUILD C ships as the offline pull-set. Each
// has an authored mold, so attaching one produces a real molded result (not a stub).
const PULL_SET = ["marketplace_listing", "sourcing_opportunity", "product_match"];

/** Re-disable every capability in the pull-set (restore the shipped disabled state). */
async function restorePullSet() {
  for (const slug of PULL_SET) {
    // detach == set enabled:false. Tolerate already-detached (idempotent).
    try {
      await fxSetCapability(slug, "detach");
    } catch {
      /* declared check only throws for unknown slugs; these are declared */
    }
  }
}

beforeEach(async () => {
  await restorePullSet();
});

afterEach(async () => {
  await restorePullSet();
});

describe("compose picker -- fixtures contract", () => {
  it("ships the declared-but-disabled pull-set (the picker is non-empty offline)", () => {
    const cfg = fxGetCapabilitiesConfig();
    // every pull-set slug is DECLARED but DISABLED at rest -> available to add.
    for (const slug of PULL_SET) {
      expect(cfg.declared, `${slug} declared`).toContain(slug);
      expect(cfg.disabled, `${slug} disabled`).toContain(slug);
      expect(cfg.enabled, `${slug} not enabled`).not.toContain(slug);
    }
    // disabled is a non-empty subset of declared -> the picker has something to pull.
    expect(cfg.disabled.length).toBeGreaterThanOrEqual(PULL_SET.length);
    // declared = enabled + disabled, partitioned (no leaks, no dupes).
    expect(new Set([...cfg.enabled, ...cfg.disabled]).size).toBe(cfg.declared.length);
    expect(cfg.enabled.some((s) => cfg.disabled.includes(s))).toBe(false);
  });

  it("the grid (fxListCards) OMITS disabled cards (mirrors live GET /capabilities)", () => {
    const grid = fxListCards().map((c) => c.capability);
    for (const slug of PULL_SET) {
      expect(grid, `${slug} not on the grid while disabled`).not.toContain(slug);
    }
    // but the FULL catalog (the picker's rich source) DOES include them.
    const catalog = fxListCatalog().map((c) => c.capability);
    for (const slug of PULL_SET) {
      expect(catalog, `${slug} in the full catalog`).toContain(slug);
    }
  });

  it("attach -> grid grows + enabled count +1; detach -> shrinks back", async () => {
    const slug = "marketplace_listing";
    const beforeCfg = fxGetCapabilitiesConfig();
    const beforeGrid = fxListCards().length;
    expect(fxListCards().map((c) => c.capability)).not.toContain(slug);

    // ATTACH (pull it in).
    const afterAttach = await fxSetCapability(slug, "attach");
    expect(afterAttach.enabled).toContain(slug);
    expect(afterAttach.disabled).not.toContain(slug);
    expect(afterAttach.enabled.length).toBe(beforeCfg.enabled.length + 1);
    // the grid grew by exactly one and now includes the attached card.
    const grownGrid = fxListCards();
    expect(grownGrid.length).toBe(beforeGrid + 1);
    expect(grownGrid.map((c) => c.capability)).toContain(slug);

    // DETACH (remove it) -> the grid shrinks back to the original set.
    const afterDetach = await fxSetCapability(slug, "detach");
    expect(afterDetach.enabled).not.toContain(slug);
    expect(afterDetach.disabled).toContain(slug);
    expect(afterDetach.enabled.length).toBe(beforeCfg.enabled.length);
    expect(fxListCards().length).toBe(beforeGrid);
    expect(fxListCards().map((c) => c.capability)).not.toContain(slug);
  });

  it("refuses an UNDECLARED slug (never fabricates a capability) -- 409 not_declared", async () => {
    await expect(fxSetCapability("totally_made_up_capability", "attach")).rejects.toMatchObject({
      status: 409,
      reason: "not_declared",
    });
    // and an unknown action is rejected too (400 unknown_action) -- the FAIL-CLOSED contract.
    // (cast past the "attach"|"detach" type to exercise the runtime guard the backend mirrors.)
    await expect(
      fxSetCapability("marketplace_listing", "sideways" as "attach" | "detach"),
    ).rejects.toMatchObject({
      status: 400,
      reason: "unknown_action",
    });
  });
});

describe("compose picker -- component", () => {
  it("renders the available (declared-but-disabled) set with Add actions", async () => {
    render(
      <ModuleManager
        open
        accessToken="jwt-test"
        cards={fxListCards()}
        onClose={() => {}}
        onChanged={() => {}}
      />,
    );
    // the picker frames the founder's model.
    await screen.findByText(/Your composition -- pull what you need/i);
    // each pull-set capability is offered with its OWN "Add <label>" action (these are the
    // declared-but-disabled modules -- the rich label comes from the full catalog metadata).
    const addLabels: Record<string, RegExp> = {
      marketplace_listing: /Add Anuncio Marketplace/i,
      sourcing_opportunity: /Add Sourcing/i,
      product_match: /Add Match de Produto/i,
    };
    for (const slug of PULL_SET) {
      const addBtn = await screen.findByRole("button", { name: addLabels[slug] });
      expect(addBtn).toBeTruthy();
    }
    // honest count line: "<on> on . <available> available . <declared> declared". The "."
    // separators are matched literally (escaped) so the assertion is exact.
    const cfg = fxGetCapabilitiesConfig();
    expect(
      screen.getByText(
        new RegExp(
          `${cfg.enabled.length} on \\. ${cfg.disabled.length} available \\. ${cfg.declared.length} declared`,
        ),
      ),
    ).toBeTruthy();
  });

  it("shows ONLY declared capabilities -- no invented module appears", async () => {
    render(
      <ModuleManager
        open
        accessToken="jwt-test"
        cards={fxListCards()}
        onClose={() => {}}
        onChanged={() => {}}
      />,
    );
    await screen.findByText(/Your composition/i);
    const cfg = fxGetCapabilitiesConfig();
    // Every "Add"/"Remove" action label must correspond to a DECLARED slug. We assert the
    // total row count equals the declared count (enabled rows + available rows).
    const actions = screen
      .getAllByRole("button")
      .filter((b) => /^(Add|Remove) /i.test(b.getAttribute("aria-label") || ""));
    expect(actions.length).toBe(cfg.declared.length);
  });

  it("clicking Add in the picker grows the GRID and bumps the enabled stat", async () => {
    render(<CapabilitiesPage />);

    // The grid loads the enabled cards; the disabled pull-set is absent at rest.
    await screen.findByText("What do you want to create?");
    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Add module" })).toBeTruthy(),
    );
    // marketplace_listing is NOT on the grid yet (it is disabled).
    expect(screen.queryByRole("button", { name: /Run Anuncio Marketplace/i })).toBeNull();

    // capture the enabled stat hero value before the pull.
    const enabledBefore = fxGetCapabilitiesConfig().enabled.length;

    // open the picker.
    fireEvent.click(screen.getByRole("button", { name: "Add module" }));
    const dialog = await screen.findByRole("dialog", { name: /Compose your dashboard/i });

    // pull marketplace_listing in (its Add button inside the picker).
    const addBtn = await within(dialog).findByRole("button", {
      name: /Add Anuncio Marketplace/i,
    });
    fireEvent.click(addBtn);

    // the grid re-composes (onChanged=load): the marketplace card now appears as a runnable
    // grid card. (It renders even with the picker still open -- the grid is behind it.)
    await waitFor(() =>
      expect(
        screen.getByRole("button", { name: /Run Anuncio Marketplace/i }),
      ).toBeTruthy(),
    );
    // and the enabled stat bumped by one (the fixtures state grew).
    expect(fxGetCapabilitiesConfig().enabled.length).toBe(enabledBefore + 1);
  });
});
