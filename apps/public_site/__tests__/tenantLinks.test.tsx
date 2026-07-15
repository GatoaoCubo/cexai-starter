import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import {
  isSafeHref,
  safeLinkEntries,
  tenantLinksFor,
  tenantStoreUrl,
  tenantConfigFor,
} from "@/lib/tenantConfig";
import { BrandFooter, TenantPresenceRow } from "@/components/BrandFooter";

// ----------------------------------------------------------------------------
// TENANT LINKS CONTRACT -- the OPTIONAL external web+social presence block.
//
// Asserts the full contract:
//   * isSafeHref / safeLinkEntries SANITIZE: only an absolute https: URL survives; a
//     javascript:/data:/http:/protocol-relative/relative/mailto/tel link is REJECTED (never
//     rendered) -- this is the UNAUTHENTICATED public surface;
//   * the SoT (tenantConfig) carries the 5 FICTITIOUS demo-orbit links (P0-A rebrand: these
//     deliberately do NOT resolve to a real company) + reconciles WhatsApp;
//   * the nav "Loja" derives from links.store (byte-identical value for demo-orbit);
//   * the footer presence row renders demo-orbit's links and renders NOTHING for a tenant
//     with no links (demo-acme/unknown) -- graceful, no empty row;
//   * the EXISTING footer content (the nav Loja value + the copyright line) is unchanged.
// ----------------------------------------------------------------------------

describe("isSafeHref -- the https-only external-link guard", () => {
  it("accepts ONLY an absolute https URL", () => {
    expect(isSafeHref("https://www.orbittech.com.br/")).toBe(true);
    expect(isSafeHref("https://br.linkedin.com/company/orbittech-solucoes")).toBe(true);
  });

  it("rejects javascript:/data:/http:/protocol-relative/relative/mailto/tel/whitespace/empty/non-string", () => {
    expect(isSafeHref("javascript:alert(1)")).toBe(false);
    expect(isSafeHref("data:text/html;base64,PHNjcmlwdD4=")).toBe(false);
    expect(isSafeHref("http://insecure.example.com")).toBe(false);
    expect(isSafeHref("//evil.example.com")).toBe(false); // protocol-relative
    expect(isSafeHref("/relative/path")).toBe(false);
    expect(isSafeHref("mailto:x@y.com")).toBe(false);
    expect(isSafeHref("tel:+5511999999999")).toBe(false);
    expect(isSafeHref("https://has space.com")).toBe(false); // embedded whitespace
    expect(isSafeHref("https://")).toBe(false); // no host
    expect(isSafeHref("")).toBe(false);
    expect(isSafeHref(null)).toBe(false);
    expect(isSafeHref(undefined)).toBe(false);
    expect(isSafeHref(123 as unknown)).toBe(false);
  });
});

describe("safeLinkEntries -- sanitize + order + reconcile (the data behind the render)", () => {
  it("drops every UNSAFE scheme and keeps only https (a javascript:/data: link is rejected)", () => {
    const entries = safeLinkEntries({
      website: "javascript:alert(1)", // dropped
      store: "data:text/html,<script>", // dropped
      instagram: "//evil.example.com", // dropped (protocol-relative)
      linkedin: "http://insecure.example", // dropped (http)
      facebook: "https://www.facebook.com/orbittechinfo/", // KEPT
    });
    expect(entries.map((e) => e.key)).toEqual(["facebook"]);
    expect(entries[0].href).toBe("https://www.facebook.com/orbittechinfo/");
  });

  it("orders entries by the fixed platform order and reconciles whatsapp", () => {
    const base = {
      youtube: "https://youtube.com/x",
      website: "https://site",
      instagram: "https://ig",
      whatsapp: "https://wa.me/123",
    };
    // no pre-existing whatsapp control -> whatsapp IS rendered, in fixed order (last).
    expect(safeLinkEntries(base).map((e) => e.key)).toEqual([
      "website",
      "instagram",
      "youtube",
      "whatsapp",
    ]);
    // a whatsapp control already exists elsewhere -> reconcile (omit the duplicate).
    expect(
      safeLinkEntries(base, { hasContactWhatsapp: true }).map((e) => e.key),
    ).toEqual(["website", "instagram", "youtube"]);
  });

  it("absent/empty links -> [] (honest-empty)", () => {
    expect(safeLinkEntries(undefined)).toEqual([]);
    expect(safeLinkEntries(null)).toEqual([]);
    expect(safeLinkEntries({})).toEqual([]);
  });
});

describe("tenantLinksFor / tenantStoreUrl -- the SoT-derived presence + nav Loja", () => {
  it("demo-orbit exposes its 5 fictitious links, in order, WITHOUT a duplicate whatsapp", () => {
    const entries = tenantLinksFor("demo-orbit");
    expect(entries.map((e) => e.key)).toEqual([
      "website",
      "store",
      "instagram",
      "linkedin",
      "facebook",
    ]);
    expect(entries.map((e) => e.href)).toEqual([
      "https://www.orbittech.com.br/",
      "https://www.loja.orbittech.com.br",
      "https://www.instagram.com/orbittech_solucoes/",
      "https://br.linkedin.com/company/orbittech-solucoes",
      "https://www.facebook.com/orbittechinfo/",
    ]);
    // every emitted href is a safe absolute https URL.
    for (const e of entries) expect(isSafeHref(e.href)).toBe(true);
    // whatsapp is NOT in the row (reconciled -- it keeps the dedicated contact CTA control).
    expect(entries.some((e) => e.key === "whatsapp")).toBe(false);
  });

  it("demo-acme + any unknown slug expose NO links (honest-empty)", () => {
    expect(tenantLinksFor("demo-acme")).toEqual([]);
    expect(tenantLinksFor("whoever")).toEqual([]);
    // the SoT carries no links block for the demo / unknown tenant.
    expect(tenantConfigFor("demo-acme").links).toBeUndefined();
    expect(tenantConfigFor("whoever").links).toBeUndefined();
  });

  it("the nav Loja DERIVES from links.store -- demo-orbit byte-identical, demo-acme empty", () => {
    expect(tenantStoreUrl("demo-orbit")).toBe("https://www.loja.orbittech.com.br");
    expect(tenantStoreUrl("demo-acme")).toBe("");
    expect(tenantStoreUrl("whoever")).toBe("");
  });
});

describe("TenantPresenceRow -- the render boundary sanitizes every href", () => {
  it("renders ONLY safe https links; a javascript:/data: link is NOT rendered", () => {
    const { container } = render(
      <TenantPresenceRow
        links={{
          website: "https://www.orbittech.com.br/",
          instagram: "javascript:alert(1)", // hostile -> must NOT render
          facebook: "data:text/html,<script>alert(1)</script>", // hostile -> must NOT render
        }}
      />,
    );
    const anchors = Array.from(container.querySelectorAll("a"));
    expect(anchors.map((a) => a.getAttribute("href"))).toEqual([
      "https://www.orbittech.com.br/",
    ]);
    // the hostile schemes never reached the DOM at all.
    expect(container.innerHTML).not.toContain("javascript:");
    expect(container.innerHTML).not.toContain("data:text/html");
    // hardened external link: target + rel.
    expect(anchors[0].getAttribute("target")).toBe("_blank");
    expect(anchors[0].getAttribute("rel")).toContain("noopener");
    expect(anchors[0].getAttribute("rel")).toContain("noreferrer");
  });

  it("renders NOTHING (no nav, no anchor) when no safe link exists -- graceful, no empty row", () => {
    const { container } = render(
      <TenantPresenceRow links={{ website: "javascript:void(0)", store: "//evil" }} />,
    );
    expect(container.querySelector("nav")).toBeNull();
    expect(container.querySelector("a")).toBeNull();
  });

  it("reconciles whatsapp at the render boundary (hasContactWhatsapp drops the duplicate)", () => {
    const links = { website: "https://site", whatsapp: "https://wa.me/1" };
    const withWa = render(<TenantPresenceRow links={links} />);
    expect(withWa.container.querySelectorAll("a").length).toBe(2);
    const noWa = render(<TenantPresenceRow links={links} hasContactWhatsapp />);
    expect(
      Array.from(noWa.container.querySelectorAll("a")).map((a) => a.getAttribute("href")),
    ).toEqual(["https://site"]);
  });
});

describe("BrandFooter -- presence row wired + EXISTING content byte-identical", () => {
  it("demo-orbit: footer shows the 5 sanitized presence links + keeps the nav Loja + copyright", () => {
    const brand = tenantConfigFor("demo-orbit").brand;
    const { container } = render(<BrandFooter brand={brand} slug="demo-orbit" />);
    const anchors = Array.from(container.querySelectorAll("a"));
    const hrefs = anchors.map((a) => a.getAttribute("href") ?? "");

    // the presence row exists and carries all 5 demo-orbit links.
    expect(container.querySelector('nav[aria-label="Redes e canais"]')).not.toBeNull();
    for (const u of [
      "https://www.orbittech.com.br/",
      "https://www.loja.orbittech.com.br",
      "https://www.instagram.com/orbittech_solucoes/",
      "https://br.linkedin.com/company/orbittech-solucoes",
      "https://www.facebook.com/orbittechinfo/",
    ]) {
      expect(hrefs.includes(u)).toBe(true);
    }
    // sanitized: NO unsafe scheme anywhere in the footer.
    for (const h of hrefs) {
      expect(h.startsWith("javascript:")).toBe(false);
      expect(h.startsWith("data:")).toBe(false);
      expect(h.startsWith("http://")).toBe(false);
    }

    // EXISTING footer content unchanged: the nav "Loja" link (now sourced from links.store,
    // byte-identical value + its original rel) ...
    const loja = anchors.find((a) => (a.textContent ?? "").trim() === "Loja");
    expect(loja).toBeTruthy();
    expect(loja!.getAttribute("href")).toBe("https://www.loja.orbittech.com.br");
    expect(loja!.getAttribute("rel")).toContain("nofollow");
    expect(loja!.getAttribute("rel")).toContain("noopener");
    // ... and the copyright line (byte-identical).
    const year = new Date().getFullYear();
    expect(container.textContent).toContain(
      `(c) ${year} Orbit Tech -- catalogo publicado via CEXAI.`,
    );
  });

  it("demo-acme: NO presence row (graceful) + NO external Loja (zero-regression) + copyright intact", () => {
    const brand = tenantConfigFor("demo-acme").brand;
    const { container } = render(<BrandFooter brand={brand} slug="demo-acme" />);
    // no presence row at all.
    expect(container.querySelector('nav[aria-label="Redes e canais"]')).toBeNull();
    const anchors = Array.from(container.querySelectorAll("a"));
    // no external Loja link + no demo-orbit link leak into the demo footer.
    expect(anchors.some((a) => (a.textContent ?? "").trim() === "Loja")).toBe(false);
    expect(
      anchors.some((a) => (a.getAttribute("href") ?? "").includes("loja.orbittech")),
    ).toBe(false);
    // the existing copyright still renders, byte-identical (the built-in sample brand name).
    const year = new Date().getFullYear();
    expect(container.textContent).toContain(
      `(c) ${year} Acme Pet Shop (amostra) -- catalogo publicado via CEXAI.`,
    );
  });
});
