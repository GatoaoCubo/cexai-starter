import { describe, it, expect } from "vitest";
import { isSafeMediaSrc } from "@/lib/mediaSafety";

// ----------------------------------------------------------------------------
// mediaSafety -- the produced-media scheme allowlist (the public-page media guard).
// A published payload's media field is forwarded VERBATIM by the backend, so the
// client MUST reject any hostile scheme before rendering. These assert the exact
// boundary: ALLOW https: + data:image|video|audio; REJECT everything else.
// ----------------------------------------------------------------------------

describe("isSafeMediaSrc", () => {
  it("ALLOWS https: URLs", () => {
    expect(isSafeMediaSrc("https://cdn.example.com/a.jpg")).toBe(true);
    expect(isSafeMediaSrc("HTTPS://CDN.EXAMPLE.COM/a.png")).toBe(true);
  });

  it("ALLOWS data:image / data:video / data:audio URIs", () => {
    expect(isSafeMediaSrc("data:image/png;base64,AAAA")).toBe(true);
    expect(isSafeMediaSrc("data:image/svg+xml;utf8,<svg/>")).toBe(true);
    expect(isSafeMediaSrc("data:video/mp4;base64,AAAA")).toBe(true);
    expect(isSafeMediaSrc("data:audio/mpeg;base64,AAAA")).toBe(true);
  });

  it("REJECTS javascript: (XSS)", () => {
    expect(isSafeMediaSrc("javascript:alert(1)")).toBe(false);
    expect(isSafeMediaSrc("JavaScript:alert(1)")).toBe(false);
  });

  it("REJECTS data:text/html (HTML smuggling)", () => {
    expect(isSafeMediaSrc("data:text/html;base64,PHNjcmlwdD4=")).toBe(false);
    expect(isSafeMediaSrc("data:text/html,<script>alert(1)</script>")).toBe(false);
  });

  it("REJECTS http: (mixed-content beacon)", () => {
    expect(isSafeMediaSrc("http://insecure.example.com/a.jpg")).toBe(false);
  });

  it("REJECTS file: and other schemes", () => {
    expect(isSafeMediaSrc("file:///etc/passwd")).toBe(false);
    expect(isSafeMediaSrc("ftp://example.com/a.jpg")).toBe(false);
    expect(isSafeMediaSrc("//cdn.example.com/a.jpg")).toBe(false);
  });

  it("REJECTS non-strings and empty/garbage values", () => {
    expect(isSafeMediaSrc("")).toBe(false);
    expect(isSafeMediaSrc("   ")).toBe(false);
    expect(isSafeMediaSrc(undefined)).toBe(false);
    expect(isSafeMediaSrc(null)).toBe(false);
    expect(isSafeMediaSrc(42)).toBe(false);
    expect(isSafeMediaSrc({})).toBe(false);
  });
});
