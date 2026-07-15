// SPEC 10 W1 -- the L2 PUBLISH SEAM, api.ts wire contract.
//
// Proves ApiClient.setEntityPublished (the new method) sends the right request: a PATCH to
// /entity/{slug}/{id}/publish with body { published }, and the ONLY identity it carries is the
// Bearer JWT -- NO tenant_id in the path, body, or any header (the #1 rule -- mirrors
// updateEntity). The slug + id are URL-encoded.
//
// Exercises the REAL ApiClient (it does NOT mock @/lib/api) against a stubbed global.fetch.
// It DOES mock @/lib/config so apiUrl is set (config reads NEXT_PUBLIC_API_URL ONCE at import, so
// setting the env in the test is too late) and fixtures is false (the live fetch path). The
// component test (publish-toggle.test.tsx) is the one that mocks @/lib/api.

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

// Mock config so the live fetch path is taken (apiUrl set, fixtures off). Hoisted by vitest above
// the api import below, so ApiClient sees this config.
vi.mock("@/lib/config", () => ({
  config: { apiUrl: "http://api.test", fixtures: false },
}));

import { ApiClient } from "@/lib/api";

describe("ApiClient.setEntityPublished (wire contract)", () => {
  const TOKEN = "jwt-token-abc";
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    fetchMock = vi.fn(async () => ({
      ok: true,
      status: 200,
      json: async () => ({
        id: "row-1",
        name: "Alpha",
        published: true,
        published_at: "2026-06-25T00:00:00+00:00",
      }),
    }));
    global.fetch = fetchMock as unknown as typeof fetch;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("PATCHes /entity/{slug}/{id}/publish with body { published } and ONLY a Bearer (no tenant_id)", async () => {
    const client = new ApiClient(TOKEN);
    const rec = await client.setEntityPublished("products", "row-1", true);

    // The returned record carries the gate columns (published + published_at).
    expect(rec.published).toBe(true);
    expect(rec.published_at).toBeTruthy();

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];

    // PATCH to the publish sub-path (slug + id in the path; NEVER tenant_id).
    expect(init.method).toBe("PATCH");
    expect(String(url)).toContain("/entity/products/row-1/publish");
    expect(String(url)).not.toMatch(/tenant/i);

    // The body carries ONLY { published } -- no tenant_id (the backend derives it from the JWT).
    const body = JSON.parse(String(init.body));
    expect(body).toEqual({ published: true });
    expect(body).not.toHaveProperty("tenant_id");

    // The ONLY identity sent is the Bearer JWT.
    const headers = init.headers as Record<string, string>;
    expect(headers.authorization).toBe(`Bearer ${TOKEN}`);
    for (const k of Object.keys(headers)) {
      expect(k.toLowerCase()).not.toContain("tenant");
    }
  });

  it("sends published=false on unpublish and URL-encodes the id", async () => {
    const client = new ApiClient(TOKEN);
    await client.setEntityPublished("listings", "abc 1", false);
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    // the id is URL-encoded (a space -> %20), proving encodeURIComponent is applied.
    expect(String(url)).toContain("/entity/listings/abc%201/publish");
    expect(JSON.parse(String(init.body))).toEqual({ published: false });
  });
});
