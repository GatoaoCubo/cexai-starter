import { describe, it, expect } from "vitest";
import { isValidSlug, isValidKind } from "@/lib/slug";

// ----------------------------------------------------------------------------
// slug / kind validation -- the client-side allowlist that mirrors the backend's
// _SLUG_RE / _KIND_RE (^[a-z0-9][a-z0-9_-]{0,63}$). Defence-in-depth: a bad value
// renders <NotFound/> and never reaches the API. These assert the exact boundary.
// ----------------------------------------------------------------------------

describe("isValidSlug", () => {
  it("ACCEPTS a normal slug", () => {
    expect(isValidSlug("demo-acme")).toBe(true);
    expect(isValidSlug("acme3")).toBe(true);
    expect(isValidSlug("a")).toBe(true);
    expect(isValidSlug("tenant_data_123")).toBe(true);
    expect(isValidSlug("0abc")).toBe(true);
  });

  it("REJECTS a path-traversal fragment", () => {
    expect(isValidSlug("..")).toBe(false);
    expect(isValidSlug("../etc")).toBe(false);
    expect(isValidSlug("a/b")).toBe(false);
    expect(isValidSlug("a.b")).toBe(false); // no "." allowed at all
  });

  it("REJECTS internal spaces", () => {
    // An INTERNAL space is never allowed (the body class has no space).
    expect(isValidSlug("has space")).toBe(false);
    expect(isValidSlug("demo acme")).toBe(false);
    // Surrounding whitespace is TRIMMED before the shape test -- this mirrors the
    // backend's is_valid_slug (slug.strip()), so a stray surrounding space on an
    // otherwise-valid slug is accepted (and the value sent to the API is trimmed).
    expect(isValidSlug("  demo-acme  ")).toBe(true);
    expect(isValidSlug(" leadingspace ")).toBe(true);
  });

  it("REJECTS UPPERCASE (the allowlist is lowercase-only)", () => {
    expect(isValidSlug("DemoAcme")).toBe(false);
    expect(isValidSlug("ACME3")).toBe(false);
  });

  it("REJECTS a SQL fragment", () => {
    expect(isValidSlug("'; DROP TABLE tenant_slugs; --")).toBe(false);
    expect(isValidSlug("1 OR 1=1")).toBe(false);
    expect(isValidSlug("slug);select")).toBe(false);
  });

  it("REJECTS an over-long string (> 64 chars)", () => {
    expect(isValidSlug("a".repeat(64))).toBe(true); // exactly 64 (1 + 63) is OK
    expect(isValidSlug("a".repeat(65))).toBe(false);
  });

  it("REJECTS a leading - or _ (the first char must be [a-z0-9])", () => {
    expect(isValidSlug("-abc")).toBe(false);
    expect(isValidSlug("_abc")).toBe(false);
  });

  it("REJECTS non-strings and empties", () => {
    expect(isValidSlug("")).toBe(false);
    expect(isValidSlug(undefined)).toBe(false);
    expect(isValidSlug(null)).toBe(false);
    expect(isValidSlug(123)).toBe(false);
  });
});

describe("isValidKind", () => {
  it("ACCEPTS the configured public kinds", () => {
    expect(isValidKind("marketplace_listing")).toBe(true);
    expect(isValidKind("product_ad")).toBe(true);
  });

  it("REJECTS the same hostile shapes as the slug allowlist", () => {
    expect(isValidKind("..")).toBe(false);
    expect(isValidKind("Kind With Spaces")).toBe(false);
    expect(isValidKind("UPPER")).toBe(false);
    expect(isValidKind("'; DROP TABLE tenant_data; --")).toBe(false);
    expect(isValidKind("a".repeat(65))).toBe(false);
  });
});
