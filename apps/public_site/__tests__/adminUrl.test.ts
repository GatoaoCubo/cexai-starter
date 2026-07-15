import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";

// ----------------------------------------------------------------------------
// config.adminUrl -- the header "Admin" link target normalizer. SECURITY: it must accept
// ONLY an https: absolute URL, a same-origin "/path", or a LOOPBACK-only plain-http URL
// (http://localhost[:port] / http://127.0.0.1[:port] -- R-368, local dev admin servers), and
// DROP everything else (javascript:, data:, "//host" protocol-relative, any non-loopback http:)
// to the safe "/admin" default.
// A tenant value can never be placed here (it is a build-time env), but the normalizer is
// the defence so a misconfigured env can never inject an unsafe scheme into an href.
//
// config.ts reads NEXT_PUBLIC_* once at import, so each case imports the module FRESH.
// ----------------------------------------------------------------------------

const ORIGINAL_ENV = { ...process.env };

beforeEach(() => {
  vi.resetModules();
  delete process.env.NEXT_PUBLIC_ADMIN_URL;
});

afterEach(() => {
  vi.restoreAllMocks();
  process.env = { ...ORIGINAL_ENV };
});

async function adminUrl(value?: string): Promise<string> {
  // config.ts caches its module-level `config` at import; reset modules per call so each
  // assertion re-reads the env (otherwise a second call in one test reuses the first).
  vi.resetModules();
  if (value === undefined) delete process.env.NEXT_PUBLIC_ADMIN_URL;
  else process.env.NEXT_PUBLIC_ADMIN_URL = value;
  const { config } = await import("@/lib/config");
  return config.adminUrl;
}

describe("config.adminUrl normalizer", () => {
  it("defaults to /admin when unset", async () => {
    expect(await adminUrl(undefined)).toBe("/admin");
  });

  it("accepts an https: absolute URL", async () => {
    expect(await adminUrl("https://dash.example.com")).toBe("https://dash.example.com");
  });

  it("accepts a same-origin /path", async () => {
    expect(await adminUrl("/dashboard")).toBe("/dashboard");
    expect(await adminUrl("/")).toBe("/");
  });

  it("DROPS a javascript: scheme -> /admin", async () => {
    expect(await adminUrl("javascript:alert(1)")).toBe("/admin");
  });

  it("DROPS a data: scheme -> /admin", async () => {
    expect(await adminUrl("data:text/html,<script>")).toBe("/admin");
  });

  it("DROPS an http: (insecure, non-loopback) URL -> /admin", async () => {
    expect(await adminUrl("http://insecure.example.com")).toBe("/admin");
    expect(await adminUrl("http://evil.com")).toBe("/admin");
  });

  it("DROPS a protocol-relative //host -> /admin", async () => {
    expect(await adminUrl("//evil.example.com")).toBe("/admin");
  });

  // --------------------------------------------------------------------------
  // R-368: loopback-only plain-http exception (local dev admin server). The distill
  // engine emits .env.local with NEXT_PUBLIC_ADMIN_URL=http://localhost:3001; the
  // pre-R-368 https-or-path-only rule silently dropped that to /admin -> 404.
  // --------------------------------------------------------------------------
  it("R-368: accepts http://localhost with a port", async () => {
    expect(await adminUrl("http://localhost:3001")).toBe("http://localhost:3001");
  });

  it("R-368: accepts http://127.0.0.1 with a port", async () => {
    expect(await adminUrl("http://127.0.0.1:3001")).toBe("http://127.0.0.1:3001");
  });

  it("R-368: accepts loopback http with no port", async () => {
    expect(await adminUrl("http://localhost")).toBe("http://localhost");
    expect(await adminUrl("http://127.0.0.1")).toBe("http://127.0.0.1");
  });

  it("R-368: accepts loopback http with a path", async () => {
    expect(await adminUrl("http://localhost:3001/admin")).toBe("http://localhost:3001/admin");
  });

  it("R-368: loopback host match is case-insensitive", async () => {
    expect(await adminUrl("http://LOCALHOST:3001")).toBe("http://LOCALHOST:3001");
    expect(await adminUrl("HTTP://localhost:3001")).toBe("HTTP://localhost:3001");
  });

  it("R-368: still DROPS a loopback-lookalike host -> /admin", async () => {
    // "localhost" must be the WHOLE host, not a prefix/suffix of a hostile domain.
    expect(await adminUrl("http://localhost.evil.com")).toBe("/admin");
    expect(await adminUrl("http://evil-localhost.com")).toBe("/admin");
    // 127.0.0.1 must be the exact address, not a prefix of a different IP.
    expect(await adminUrl("http://127.0.0.10")).toBe("/admin");
  });

  it("R-368: does not widen https: to accept a loopback-only relaxation", async () => {
    // the loopback exception is http-ONLY; https: was already unconditionally accepted
    // (any host) before R-368 and stays that way -- no change in behavior here.
    expect(await adminUrl("https://localhost:3001")).toBe("https://localhost:3001");
  });
});

// ----------------------------------------------------------------------------
// adminUrlForTenant(slug) -- the tenant DEEP-LINK builder. The public site "Admin" link
// becomes <adminUrl>?tenant=<slug> so the dashboard opens in THIS tenant's admin theme.
// SECURITY: ?tenant drives the admin THEME + preview ONLY (the dashboard binds DATA tenant
// to the auth/RLS session, never the URL). It must: encode the slug, append "&" when the
// adminUrl already has a query, and NEVER produce an unsafe scheme (config.adminUrl is the
// already-normalized https:/same-origin constant, so the deep-link inherits that safety).
// ----------------------------------------------------------------------------

async function adminFor(slug: string, value?: string): Promise<string> {
  vi.resetModules();
  if (value === undefined) delete process.env.NEXT_PUBLIC_ADMIN_URL;
  else process.env.NEXT_PUBLIC_ADMIN_URL = value;
  const { adminUrlForTenant } = await import("@/lib/config");
  return adminUrlForTenant(slug);
}

describe("adminUrlForTenant -- tenant deep-link", () => {
  it("appends ?tenant=<slug> to the default same-origin /admin", async () => {
    expect(await adminFor("demo-orbit")).toBe("/admin?tenant=demo-orbit");
    expect(await adminFor("demo-acme")).toBe("/admin?tenant=demo-acme");
  });

  it("ends with ?tenant=<slug> for demo-orbit and demo-acme", async () => {
    expect((await adminFor("demo-orbit")).endsWith("?tenant=demo-orbit")).toBe(true);
    expect((await adminFor("demo-acme")).endsWith("?tenant=demo-acme")).toBe(true);
  });

  it("appends to an absolute https admin origin", async () => {
    expect(await adminFor("demo-orbit", "https://dash.example.com/")).toBe(
      "https://dash.example.com/?tenant=demo-orbit",
    );
  });

  it("uses & when the adminUrl already carries a query", async () => {
    expect(await adminFor("demo-orbit", "https://dash.example.com/?next=1")).toBe(
      "https://dash.example.com/?next=1&tenant=demo-orbit",
    );
    // same rule for a same-origin path with an existing query.
    expect(await adminFor("demo-acme", "/admin?foo=bar")).toBe("/admin?foo=bar&tenant=demo-acme");
  });

  it("URL-encodes the slug (never a raw query injection)", async () => {
    expect(await adminFor("a b&c")).toBe("/admin?tenant=a%20b%26c");
  });

  it("returns the bare adminUrl for an empty slug (degrade-never)", async () => {
    expect(await adminFor("   ")).toBe("/admin");
  });

  it("never produces an unsafe scheme, even with a hostile env", async () => {
    // the env is dropped to the safe /admin default by the normalizer; the deep-link stays
    // a same-origin path (no javascript:/data: can be produced).
    const href = await adminFor("demo-orbit", "javascript:alert(1)");
    expect(href.startsWith("javascript:")).toBe(false);
    expect(href.startsWith("data:")).toBe(false);
    expect(href).toBe("/admin?tenant=demo-orbit");
  });
});
