import { describe, it, expect } from "vitest";
import { isSafeLogoSrc } from "@/lib/brandTheme";
import { imageryFor } from "@/lib/tenantImagery";
import { publicKindsFor, PUBLIC_KINDS } from "@/lib/publicKinds";
import {
  tenantContentFor,
  isSafeContactHref,
  isPlainEmail,
  instagramUrl,
} from "@/lib/tenantContent";

// ----------------------------------------------------------------------------
// The white-label LIB layer -- the pure functions that make a second tenant render from
// the same code: the logo-src gate (now same-origin aware), the per-tenant imagery + kinds
// resolvers, and the contact-href scheme guard. These pin the security shapes + the
// zero-regression default (an unknown slug -> the built-in retail defaults).
// ----------------------------------------------------------------------------

describe("isSafeLogoSrc -- now accepts a same-origin root-relative path", () => {
  it("accepts https:, data:image, and a same-origin /path", () => {
    expect(isSafeLogoSrc("https://cdn.example.com/logo.png")).toBe(true);
    expect(isSafeLogoSrc("data:image/png;base64,AAAA")).toBe(true);
    expect(isSafeLogoSrc("/images/tenants/demo-orbit/logo.png")).toBe(true);
  });

  it("REJECTS unsafe schemes + cross-origin / protocol-relative shapes", () => {
    expect(isSafeLogoSrc("javascript:alert(1)")).toBe(false);
    expect(isSafeLogoSrc("data:text/html,<script>")).toBe(false);
    expect(isSafeLogoSrc("http://insecure.example/logo.png")).toBe(false);
    expect(isSafeLogoSrc("file:///etc/passwd")).toBe(false);
    // protocol-relative / cross-origin "//host" must NOT pass as same-origin.
    expect(isSafeLogoSrc("//evil.example/logo.png")).toBe(false);
    expect(isSafeLogoSrc("/\\evil.example/logo.png")).toBe(false);
    // a bare relative path is not allowed either.
    expect(isSafeLogoSrc("logo.png")).toBe(false);
    expect(isSafeLogoSrc("")).toBe(false);
  });
});

describe("imageryFor -- per-tenant decorative treatment", () => {
  it("demo-acme ships PHOTOS (the cat art, unchanged)", () => {
    const im = imageryFor("demo-acme");
    expect(im.mode).toBe("photos");
    if (im.mode === "photos") {
      expect(im.hero).toBe("/images/cat-hero.jpg");
      expect(im.section).toBe("/images/cat-section.jpg");
      expect(im.cardFallback).toBe("/images/cat-product.jpg");
    }
  });

  it("demo-orbit (and any unknown slug) gets the BRAND treatment (no photos -> no cat leak)", () => {
    expect(imageryFor("demo-orbit").mode).toBe("brand");
    expect(imageryFor("some-other-tenant").mode).toBe("brand");
  });
});

describe("publicKindsFor -- per-tenant kinds (zero-regression default)", () => {
  it("demo-orbit offers the SERVICE kind with its own label", () => {
    const k = publicKindsFor("demo-orbit");
    expect(k.length).toBe(1);
    expect(k[0].kind).toBe("service");
    expect(k[0].label).toBe("Servicos");
  });

  it("an unknown slug falls back to the default PUBLIC_KINDS (demo-acme unchanged)", () => {
    expect(publicKindsFor("demo-acme")).toBe(PUBLIC_KINDS);
    expect(publicKindsFor("whoever")).toBe(PUBLIC_KINDS);
    expect(PUBLIC_KINDS.map((k) => k.kind)).toEqual(["marketplace_listing", "product_ad"]);
  });
});

describe("tenantContentFor + contact-href guard", () => {
  it("demo-orbit carries partners, testimonials, social proof, and contact", () => {
    const c = tenantContentFor("demo-orbit");
    expect(c).not.toBeNull();
    expect(c!.partners?.length).toBe(3);
    expect(c!.testimonials?.length).toBe(3);
    expect(c!.testimonials?.every((t) => t.sample)).toBe(true); // honest amostra flag
    expect(c!.socialProof?.rating).toBe(4.6);
    expect(c!.contact?.whatsapp).toContain("api.whatsapp.com");
  });

  it("demo-acme carries NO extra content (null -> home unchanged)", () => {
    expect(tenantContentFor("demo-acme")).toBeNull();
    expect(tenantContentFor("anything")).toBeNull();
  });

  it("isSafeContactHref permits https/mailto/tel; rejects js/data/http", () => {
    expect(isSafeContactHref("https://api.whatsapp.com/send?phone=55119")).toBe(true);
    expect(isSafeContactHref("mailto:contato@orbittech.com.br")).toBe(true);
    expect(isSafeContactHref("tel:+551100000000")).toBe(true);
    expect(isSafeContactHref("javascript:alert(1)")).toBe(false);
    expect(isSafeContactHref("data:text/html,x")).toBe(false);
    expect(isSafeContactHref("http://insecure")).toBe(false);
    expect(isSafeContactHref(42)).toBe(false);
  });

  it("isPlainEmail + instagramUrl build only safe shapes", () => {
    expect(isPlainEmail("contato@orbittech.com.br")).toBe(true);
    expect(isPlainEmail("not-an-email")).toBe(false);
    expect(instagramUrl("orbittech_solucoes")).toBe("https://instagram.com/orbittech_solucoes");
    expect(instagramUrl("@orbittech_solucoes")).toBe("https://instagram.com/orbittech_solucoes");
    expect(instagramUrl("bad handle!")).toBe("");
    expect(instagramUrl("")).toBe("");
  });
});
