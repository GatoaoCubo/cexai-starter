import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";

// ----------------------------------------------------------------------------
// PublicApiClient -- the UNAUTHENTICATED public client. These tests cover:
//   * FIXTURES mode (NEXT_PUBLIC_FIXTURES=1): tenant-info + catalog resolve offline;
//     an unknown slug -> null (no-leak); an unknown kind -> empty items.
//   * REAL mode (NEXT_PUBLIC_API_URL set, fetch stubbed): the response shape, the
//     { error: { type, reason, detail } } envelope -> ApiClientError, the no-leak
//     404 (public_not_found) -> null, and the security invariants (NO Authorization
//     header, NO tenant_id ever sent; only slug + kind reach the API).
//
// config.ts reads NEXT_PUBLIC_* once at import, so each mode imports the module
// FRESH after setting env (vi.resetModules + dynamic import).
// ----------------------------------------------------------------------------

const ORIGINAL_ENV = { ...process.env };

beforeEach(() => {
  vi.resetModules();
  // start from a clean slate every test
  delete process.env.NEXT_PUBLIC_FIXTURES;
  delete process.env.NEXT_PUBLIC_API_URL;
});

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  process.env = { ...ORIGINAL_ENV };
});

async function loadFixturesClient() {
  process.env.NEXT_PUBLIC_FIXTURES = "1";
  const mod = await import("@/lib/publicApi");
  const fx = await import("@/lib/fixtures");
  return { publicApi: mod.publicApi, ApiClientError: mod.ApiClientError, SAMPLE_SLUG: fx.SAMPLE_SLUG };
}

async function loadRealClient(apiUrl = "https://api.example.test") {
  process.env.NEXT_PUBLIC_API_URL = apiUrl;
  const mod = await import("@/lib/publicApi");
  return { publicApi: mod.publicApi, ApiClientError: mod.ApiClientError };
}

describe("PublicApiClient -- fixtures mode", () => {
  it("resolves the sample tenant-info and a populated catalog offline", async () => {
    const { publicApi, SAMPLE_SLUG } = await loadFixturesClient();

    const info = await publicApi.getTenantInfo(SAMPLE_SLUG);
    expect(info).not.toBeNull();
    expect(info!.slug).toBe(SAMPLE_SLUG);
    expect(typeof info!.tenant_id).toBe("string");
    expect(info!.brand?.name).toContain("amostra"); // honestly flagged sample

    const catalog = await publicApi.getCatalog(SAMPLE_SLUG, "marketplace_listing");
    expect(catalog).not.toBeNull();
    expect(catalog!.kind).toBe("marketplace_listing");
    expect(catalog!.items.length).toBeGreaterThan(0);
    // every sample item is honestly flagged not-real.
    for (const it of catalog!.items) {
      expect(it.real).toBe(false);
      expect(typeof it.id).toBe("string");
    }
  });

  it("returns null for an unknown slug (no-leak miss), in BOTH endpoints", async () => {
    const { publicApi } = await loadFixturesClient();
    expect(await publicApi.getTenantInfo("no-such-tenant")).toBeNull();
    expect(await publicApi.getCatalog("no-such-tenant", "marketplace_listing")).toBeNull();
  });

  it("returns an EMPTY items list for a known slug + a kind with nothing published", async () => {
    const { publicApi, SAMPLE_SLUG } = await loadFixturesClient();
    const catalog = await publicApi.getCatalog(SAMPLE_SLUG, "kind_with_no_rows");
    expect(catalog).not.toBeNull();
    expect(catalog!.items).toEqual([]);
  });

  it("returns null (never fetches) for a malformed slug / kind", async () => {
    const { publicApi, SAMPLE_SLUG } = await loadFixturesClient();
    expect(await publicApi.getTenantInfo("..")).toBeNull();
    expect(await publicApi.getCatalog(SAMPLE_SLUG, "Bad Kind")).toBeNull();
  });
});

describe("PublicApiClient -- real mode (fetch stubbed)", () => {
  it("parses a 200 catalog response shape", async () => {
    const { publicApi } = await loadRealClient();
    const body = {
      tenant_id: "tid_1",
      slug: "demo-acme",
      kind: "product_ad",
      items: [{ id: "x1", kind: "product_ad", published_at: null }],
      limit: 50,
      offset: 0,
    };
    const fetchMock = vi.fn(async () =>
      new Response(JSON.stringify(body), { status: 200, headers: { "content-type": "application/json" } }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const res = await publicApi.getCatalog("demo-acme", "product_ad");
    expect(res).toEqual(body);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("NEVER sends an Authorization header or a tenant_id; only slug + kind reach the API", async () => {
    const { publicApi } = await loadRealClient();
    const fetchMock = vi.fn(async () =>
      new Response(JSON.stringify({ tenant_id: "t", slug: "demo-acme", kind: "product_ad", items: [], limit: 50, offset: 0 }), {
        status: 200,
        headers: { "content-type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await publicApi.getCatalog("demo-acme", "product_ad", 10, 0);

    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    // the request URL carries slug + kind (+ limit/offset) -- and NOTHING tenant.
    expect(url).toContain("/public/catalog");
    expect(url).toContain("slug=demo-acme");
    expect(url).toContain("kind=product_ad");
    expect(url.toLowerCase()).not.toContain("tenant_id");
    // no auth header of any casing; credentials omitted.
    const headers = (init.headers ?? {}) as Record<string, string>;
    const headerKeys = Object.keys(headers).map((k) => k.toLowerCase());
    expect(headerKeys).not.toContain("authorization");
    expect(headerKeys).not.toContain("cookie");
    expect(init.credentials).toBe("omit");
  });

  it("maps a 404 public_not_found to null (no-leak), NOT an error", async () => {
    const { publicApi } = await loadRealClient();
    const fetchMock = vi.fn(async () =>
      new Response(
        JSON.stringify({ error: { type: "public_not_found", reason: "unknown_slug", detail: "no public tenant for this slug" } }),
        { status: 404, headers: { "content-type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    expect(await publicApi.getTenantInfo("demo-acme")).toBeNull();
    expect(await publicApi.getCatalog("demo-acme", "product_ad")).toBeNull();
  });

  it("throws ApiClientError (with reason) for a NON-404 error envelope", async () => {
    const { publicApi, ApiClientError } = await loadRealClient();
    const fetchMock = vi.fn(async () =>
      new Response(
        JSON.stringify({ error: { type: "server_error", reason: "boom", detail: "something broke" } }),
        { status: 500, headers: { "content-type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(publicApi.getCatalog("demo-acme", "product_ad")).rejects.toBeInstanceOf(ApiClientError);
    try {
      await publicApi.getCatalog("demo-acme", "product_ad");
    } catch (err) {
      const e = err as InstanceType<typeof ApiClientError>;
      expect(e.status).toBe(500);
      expect(e.reason).toBe("boom");
      expect(e.message).toBe("something broke"); // detail becomes the message
    }
  });

  it("throws ApiClientError(0) when the backend is unreachable", async () => {
    const { publicApi, ApiClientError } = await loadRealClient();
    const fetchMock = vi.fn(async () => {
      throw new TypeError("network down");
    });
    vi.stubGlobal("fetch", fetchMock);

    await expect(publicApi.getTenantInfo("demo-acme")).rejects.toBeInstanceOf(ApiClientError);
    try {
      await publicApi.getTenantInfo("demo-acme");
    } catch (err) {
      expect((err as InstanceType<typeof ApiClientError>).status).toBe(0);
    }
  });

  it("a malformed slug returns null WITHOUT calling fetch (defence-in-depth)", async () => {
    const { publicApi } = await loadRealClient();
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    expect(await publicApi.getTenantInfo("..")).toBeNull();
    expect(await publicApi.getCatalog("demo-acme", "Bad Kind")).toBeNull();
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
