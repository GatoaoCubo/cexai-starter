import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import {
  buildWaitlistRow,
  isValidWaitlistEmail,
  submitToWaitlist,
  WAITLIST_TABLE,
  type WaitlistRow,
} from "@/lib/waitlist";
import { emptyIntakeState } from "@/lib/intake";

// ----------------------------------------------------------------------------
// lib/waitlist.ts -- the GO_ONLINE A2 "modo-espera" client. Covers:
//   * isValidWaitlistEmail -- the light gate (EMAIL_LOOSE_PATTERN reuse).
//   * buildWaitlistRow -- form state -> insert row, PURE + TOTAL: promotes
//     email/wtp_band/brand_name and carries the FULL best-effort answers
//     snapshot (nothing typed elsewhere in the form is dropped).
//   * submitToWaitlist -- the injectable-client insert path: success, an
//     RLS/Postgres rejection, a network throw, a missing config, an invalid
//     email -- ALL resolve { ok, error? }, NEVER throw (TOTAL).
//   * hasWaitlistSupabase / getWaitlistSupabase -- env-driven (module-scope
//     singleton, mirrors apps/dashboard_web/lib/supabase.ts): reset + fresh
//     dynamic import per test, same convention as __tests__/publicApi.test.ts.
//
// isValidWaitlistEmail/buildWaitlistRow/submitToWaitlist/WAITLIST_TABLE do NOT
// depend on env for their behaviour (submitToWaitlist is ALWAYS called here
// with an explicit client -- the env-driven default parameter is never
// exercised), so they are safe to import statically once at the top; only the
// hasWaitlistSupabase/getWaitlistSupabase block needs a fresh module per test.
// ----------------------------------------------------------------------------

const ORIGINAL_ENV = { ...process.env };

beforeEach(() => {
  vi.resetModules();
  delete process.env.NEXT_PUBLIC_SUPABASE_URL;
  delete process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
});

afterEach(() => {
  vi.restoreAllMocks();
  process.env = { ...ORIGINAL_ENV };
});

/** A minimal fake SupabaseClient -- only the .from(table).insert(row) shape
 *  submitToWaitlist actually calls. Records every call for assertions. */
function fakeClient(result: { error: { message: string } | null }) {
  const insert = vi.fn(async (_row: unknown) => result);
  const from = vi.fn((_table: string) => ({ insert }));
  return { client: { from } as unknown as Parameters<typeof submitToWaitlist>[1], from, insert };
}

describe("isValidWaitlistEmail", () => {
  it("accepts a well-shaped email (trims first)", () => {
    expect(isValidWaitlistEmail("ana@suamarca.com.br")).toBe(true);
    expect(isValidWaitlistEmail("  ana@suamarca.com.br  ")).toBe(true);
  });

  it("rejects empty / missing / malformed values", () => {
    expect(isValidWaitlistEmail("")).toBe(false);
    expect(isValidWaitlistEmail(undefined)).toBe(false);
    expect(isValidWaitlistEmail(null)).toBe(false);
    expect(isValidWaitlistEmail("not-an-email")).toBe(false);
    expect(isValidWaitlistEmail("missing-domain@")).toBe(false);
  });
});

describe("buildWaitlistRow", () => {
  it("promotes email/wtp_band/brand_name and carries the full answers snapshot", () => {
    const state = emptyIntakeState();
    state["contact.email"] = "ana@suamarca.com.br";
    state["audience.wtp_band"] = "R$ 29-149";
    state["identity.brand_name"] = "Cafe Borealis";
    state["identity.brand_tagline"] = "tagline de teste";

    const row = buildWaitlistRow(state);
    expect(row.email).toBe("ana@suamarca.com.br");
    expect(row.wtp_band).toBe("R$ 29-149");
    expect(row.brand_name).toBe("Cafe Borealis");
    // the full best-effort snapshot rides along -- nothing typed is dropped,
    // even though only email is required to submit.
    expect(row.answers).toMatchObject({
      form_version: 1,
      identity: { brand_name: "Cafe Borealis", brand_tagline: "tagline de teste" },
    });
  });

  it("degrades blank optional fields to null, never throws on an all-empty state", () => {
    const row = buildWaitlistRow(emptyIntakeState());
    expect(row.email).toBe("");
    expect(row.wtp_band).toBeNull();
    expect(row.brand_name).toBeNull();
    expect(row.answers).toEqual({ form_version: 1 });
  });

  it("trims whitespace on the promoted fields", () => {
    const state = emptyIntakeState();
    state["contact.email"] = "  ana@suamarca.com.br  ";
    state["audience.wtp_band"] = "  R$ 29-149  ";
    const row = buildWaitlistRow(state);
    expect(row.email).toBe("ana@suamarca.com.br");
    expect(row.wtp_band).toBe("R$ 29-149");
  });
});

describe("submitToWaitlist", () => {
  const validRow: WaitlistRow = {
    email: "ana@suamarca.com.br",
    wtp_band: "R$ 29-149",
    brand_name: "Cafe Borealis",
    answers: { form_version: 1 },
  };

  it("inserts into WAITLIST_TABLE and resolves ok:true on success", async () => {
    const { client, from, insert } = fakeClient({ error: null });
    const res = await submitToWaitlist(validRow, client);
    expect(res).toEqual({ ok: true });
    expect(from).toHaveBeenCalledWith(WAITLIST_TABLE);
    expect(insert).toHaveBeenCalledTimes(1);
    const [sentRow] = insert.mock.calls[0] as [Record<string, unknown>];
    expect(sentRow).toMatchObject({
      email: "ana@suamarca.com.br",
      wtp_band: "R$ 29-149",
      brand_name: "Cafe Borealis",
    });
  });

  it("resolves ok:false with the Postgres/RLS error message, never throws", async () => {
    const { client } = fakeClient({
      error: { message: "new row violates row-level security policy" },
    });
    const res = await submitToWaitlist(validRow, client);
    expect(res.ok).toBe(false);
    expect(res.error).toContain("row-level security");
  });

  it("resolves ok:false (never throws) when the client rejects (network failure)", async () => {
    const insert = vi.fn(async () => {
      throw new Error("network down");
    });
    const from = vi.fn((_table: string) => ({ insert }));
    const res = await submitToWaitlist(validRow, {
      from,
    } as unknown as Parameters<typeof submitToWaitlist>[1]);
    expect(res).toEqual({ ok: false, error: "network down" });
  });

  it("resolves ok:false without ever calling the client when the email is invalid", async () => {
    const { client, from } = fakeClient({ error: null });
    const res = await submitToWaitlist({ ...validRow, email: "not-an-email" }, client);
    expect(res.ok).toBe(false);
    expect(from).not.toHaveBeenCalled();
  });

  it("resolves ok:false without a network call when Supabase is unconfigured (null client)", async () => {
    const res = await submitToWaitlist(validRow, null);
    expect(res.ok).toBe(false);
    expect(res.error).toContain("Supabase");
  });
});

describe("hasWaitlistSupabase / getWaitlistSupabase (env-driven)", () => {
  it("is false / null when env vars are unset (fresh module)", async () => {
    const mod = await import("@/lib/waitlist");
    expect(mod.hasWaitlistSupabase()).toBe(false);
    expect(mod.getWaitlistSupabase()).toBeNull();
  });

  it("is true / non-null once both env vars are set (fresh module)", async () => {
    process.env.NEXT_PUBLIC_SUPABASE_URL = "https://example.supabase.co";
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY = "test-anon-key";
    const mod = await import("@/lib/waitlist");
    expect(mod.hasWaitlistSupabase()).toBe(true);
    expect(mod.getWaitlistSupabase()).not.toBeNull();
  });

  it("memoizes the client -- two calls return the SAME instance", async () => {
    process.env.NEXT_PUBLIC_SUPABASE_URL = "https://example.supabase.co";
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY = "test-anon-key";
    const mod = await import("@/lib/waitlist");
    const a = mod.getWaitlistSupabase();
    const b = mod.getWaitlistSupabase();
    expect(a).toBe(b);
  });
});
