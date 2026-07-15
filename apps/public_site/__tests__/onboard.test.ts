import { describe, it, expect } from "vitest";
import {
  isOnboardEnabled,
  deriveSlugFromUrl,
  validateUrlScheme,
  parseManifest,
} from "@/lib/onboard";

// ----------------------------------------------------------------------------
// onboard -- the PURE core of the DEV-ONLY /onboard flow. The spawn orchestration in
// the route is integration (N07 tests it LIVE); these assert the load-bearing guards:
// the prod-refusal dev gate, the slug derivation (no path-escape), the URL scheme
// allowlist, and the manifest parse (ok / error / non-JSON).
// ----------------------------------------------------------------------------

describe("isOnboardEnabled (the HARD DEV GATE = the prod-refusal)", () => {
  it("is true ONLY when NODE_ENV==development AND CEXAI_ONBOARD_ENABLED==1", () => {
    expect(
      isOnboardEnabled({ NODE_ENV: "development", CEXAI_ONBOARD_ENABLED: "1" }),
    ).toBe(true);
  });

  it("REFUSES production even with the opt-in set (NODE_ENV gate)", () => {
    expect(
      isOnboardEnabled({ NODE_ENV: "production", CEXAI_ONBOARD_ENABLED: "1" }),
    ).toBe(false);
  });

  it("REFUSES dev without the explicit server-only opt-in", () => {
    expect(isOnboardEnabled({ NODE_ENV: "development" })).toBe(false);
    expect(
      isOnboardEnabled({ NODE_ENV: "development", CEXAI_ONBOARD_ENABLED: "0" }),
    ).toBe(false);
    expect(
      isOnboardEnabled({ NODE_ENV: "development", CEXAI_ONBOARD_ENABLED: "true" }),
    ).toBe(false); // must be EXACTLY "1"
  });

  it("REFUSES test / staging / undefined NODE_ENV", () => {
    expect(
      isOnboardEnabled({ NODE_ENV: "test", CEXAI_ONBOARD_ENABLED: "1" }),
    ).toBe(false);
    expect(
      isOnboardEnabled({ NODE_ENV: "staging", CEXAI_ONBOARD_ENABLED: "1" }),
    ).toBe(false);
    expect(isOnboardEnabled({ CEXAI_ONBOARD_ENABLED: "1" })).toBe(false);
  });

  it("is TOTAL on a null/undefined env", () => {
    expect(isOnboardEnabled(undefined)).toBe(false);
    expect(isOnboardEnabled(null)).toBe(false);
  });
});

describe("deriveSlugFromUrl", () => {
  it("derives the first host label, lowercased (https://MyBrand.com.br -> mybrand)", () => {
    expect(deriveSlugFromUrl("https://MyBrand.com.br")).toBe("mybrand");
    expect(deriveSlugFromUrl("https://MyBrand.com.br/some/path?q=1")).toBe("mybrand");
    expect(deriveSlugFromUrl("http://Vertex.com")).toBe("vertex");
  });

  it("strips a leading www.", () => {
    expect(deriveSlugFromUrl("https://www.acme.io")).toBe("acme");
    expect(deriveSlugFromUrl("https://WWW.Nimbus.com")).toBe("nimbus");
  });

  it("strips characters outside [a-z0-9] from the label", () => {
    // a hostname label may carry hyphens (and punycode xn--) -> stripped to [a-z0-9].
    expect(deriveSlugFromUrl("https://my-brand.com")).toBe("mybrand");
  });

  it("truncates to 63 chars (the slug body cap)", () => {
    const longLabel = "a".repeat(80);
    const slug = deriveSlugFromUrl(`https://${longLabel}.com`);
    expect(slug).toBe("a".repeat(63));
  });

  it("returns null for an unparseable / non-http input or empty host (no path-escape)", () => {
    expect(deriveSlugFromUrl("not a url")).toBeNull();
    expect(deriveSlugFromUrl("file:///etc/passwd")).toBeNull(); // file:// has no host
    expect(deriveSlugFromUrl("https://")).toBeNull(); // no host -> throws -> null
    expect(deriveSlugFromUrl("")).toBeNull();
    expect(deriveSlugFromUrl(undefined as unknown as string)).toBeNull();
    expect(deriveSlugFromUrl(123 as unknown as string)).toBeNull();
  });

  it("returns null when the label has no [a-z0-9] survivors (cannot path-escape)", () => {
    // a label of only hyphens strips to "" -> not a valid slug -> null.
    expect(deriveSlugFromUrl("https://--.example.com")).toBeNull();
  });
});

describe("validateUrlScheme (SSRF: scheme allowlist, not host allowlist)", () => {
  it("ACCEPTS http and https", () => {
    expect(validateUrlScheme("http://example.com")).toBe(true);
    expect(validateUrlScheme("https://example.com/path?x=1")).toBe(true);
    expect(validateUrlScheme("  https://example.com  ")).toBe(true); // trimmed
  });

  it("REJECTS file: / ftp: / data: / javascript:", () => {
    expect(validateUrlScheme("file:///etc/passwd")).toBe(false);
    expect(validateUrlScheme("ftp://host/x")).toBe(false);
    expect(validateUrlScheme("data:text/html,<script>alert(1)</script>")).toBe(false);
    expect(validateUrlScheme("javascript:alert(1)")).toBe(false);
  });

  it("REJECTS an unparseable / non-string value", () => {
    expect(validateUrlScheme("not a url")).toBe(false);
    expect(validateUrlScheme("")).toBe(false);
    expect(validateUrlScheme(undefined)).toBe(false);
    expect(validateUrlScheme(null)).toBe(false);
    expect(validateUrlScheme(42)).toBe(false);
  });
});

describe("parseManifest", () => {
  it("parses an OK manifest", () => {
    const stdout = JSON.stringify({
      ok: true,
      tenant_id: "mybrand",
      tenant_config_path: ".cex/tenants/mybrand/tenant_config.json",
      tenant_config_persisted: true,
      brand: { name: "MyBrand", tagline: "we build", domain: "mybrand.com", tokens: {} },
      errors: [],
      next_steps: ["set CEX_TENANT_ID=mybrand"],
    });
    const r = parseManifest(stdout);
    expect(r.error).toBeNull();
    expect(r.manifest).not.toBeNull();
    expect(r.manifest?.ok).toBe(true);
    expect(r.manifest?.tenant_id).toBe("mybrand");
    expect(r.manifest?.brand?.name).toBe("MyBrand");
  });

  it("parses an ERROR manifest (ok:false with errors) -- a soft failure, still valid JSON", () => {
    const stdout = JSON.stringify({
      ok: false,
      tenant_id: "mybrand",
      errors: ["onboard refused (fail-closed)"],
      next_steps: [],
    });
    const r = parseManifest(stdout);
    expect(r.error).toBeNull();
    expect(r.manifest?.ok).toBe(false);
    expect(r.manifest?.errors).toEqual(["onboard refused (fail-closed)"]);
  });

  it("recovers a manifest even with a stray log line on stdout (defensive slice)", () => {
    const stdout =
      "[some-tool] a stray warning line\n" +
      JSON.stringify({ ok: true, tenant_id: "acme" }) +
      "\n";
    const r = parseManifest(stdout);
    expect(r.error).toBeNull();
    expect(r.manifest?.tenant_id).toBe("acme");
  });

  it("returns a typed error for non-JSON / empty / a JSON non-object", () => {
    expect(parseManifest("boom {{{ not json").manifest).toBeNull();
    expect(parseManifest("boom {{{ not json").error).toBeTruthy();
    expect(parseManifest("").manifest).toBeNull();
    expect(parseManifest("   ").manifest).toBeNull();
    expect(parseManifest("[1,2,3]").manifest).toBeNull(); // array is not a manifest
    expect(parseManifest("42").manifest).toBeNull();
    expect(parseManifest(undefined).manifest).toBeNull();
  });
});
