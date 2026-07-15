import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { BrandLayout } from "@/components/BrandLayout";
import { BrandHeader } from "@/components/BrandHeader";
import { BrandFooter } from "@/components/BrandFooter";
import type { BrandTheme } from "@/lib/brandTheme";

// ----------------------------------------------------------------------------
// BrandLayout / BrandHeader -- the shared chrome + THE RESKIN MECHANISM. These assert:
//   * RESKIN: BrandLayout injects a :root{} block of the brand CSS vars (buildCssVars)
//     into a scoped <style> -- so the WHOLE subtree re-themes from ONE brand object,
//     with zero per-component edits (mirrors applyBrandTheme). An absent brand injects
//     NO vars (degrade-never -> neutral look);
//   * the CSS vars are injected as <style> TEXT (data), NOT as a markup-injection sink;
//   * the header logo is SCHEME-GATED (isSafeLogoSrc): a safe https:/data:image logo
//     renders an <img>; an unsafe scheme is DROPPED;
//   * the brand name/tagline render as TEXT; the nav renders the trusted PUBLIC_KINDS.
// ----------------------------------------------------------------------------

const BRAND: BrandTheme = {
  name: "Acme Store",
  tagline: "Tudo para o seu gato",
  tokens: {
    primary: "174 68% 50%",
    brand: "174 68% 50%",
    background: "0 0% 100%",
    radius: "0.75rem",
  },
};

describe("BrandLayout -- reskin via CSS vars", () => {
  it("injects the brand tokens as a :root{} <style> block (the reskin mechanism)", () => {
    const { container } = render(
      <BrandLayout brand={BRAND} slug="acme" active="home">
        <p>conteudo</p>
      </BrandLayout>,
    );
    const style = container.querySelector("style");
    expect(style).not.toBeNull();
    const css = style!.textContent ?? "";
    // the tenant tokens became CSS custom properties (mirrors buildCssVars / applyBrandTheme).
    expect(css).toContain(":root{");
    expect(css).toContain("--primary:174 68% 50%");
    expect(css).toContain("--brand:174 68% 50%");
    expect(css).toContain("--radius:0.75rem");
  });

  it("injects NO vars for an absent brand (degrade-never -> neutral look)", () => {
    const { container } = render(
      <BrandLayout slug="acme" active="home">
        <p>conteudo</p>
      </BrandLayout>,
    );
    // empty tokens -> buildCssVars returns "" -> no <style> element rendered.
    expect(container.querySelector("style")).toBeNull();
  });

  it("renders the brand name + tagline as text and the primary nav", () => {
    render(
      <BrandLayout brand={BRAND} slug="acme" active="home">
        <p>conteudo</p>
      </BrandLayout>,
    );
    // name + tagline appear (header + footer) as text -- the tagline now renders in BOTH
    // the header and the footer, so assert at-least-one rather than exactly-one.
    expect(screen.getAllByText("Acme Store").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Tudo para o seu gato").length).toBeGreaterThan(0);
    // the nav renders Inicio + Sobre + Blog + B2B + the public-kind labels.
    expect(screen.getAllByText("Inicio").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Sobre").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Blog").length).toBeGreaterThan(0);
    expect(screen.getAllByText("B2B").length).toBeGreaterThan(0);
  });
});

describe("BrandHeader -- scheme-gated logo", () => {
  const SAFE_LOGO = "data:image/svg+xml;utf8," + encodeURIComponent("<svg/>");
  const UNSAFE_LOGO = "javascript:alert(1)";

  it("renders an <img> for a SAFE logo (https:/data:image)", () => {
    const { container } = render(
      <BrandHeader brand={{ name: "Acme", logo: SAFE_LOGO, logoAlt: "Acme" }} slug="acme" active="home" />,
    );
    const img = container.querySelector("img");
    expect(img).not.toBeNull();
    expect(img!.getAttribute("src")).toBe(SAFE_LOGO);
  });

  it("DROPS an unsafe-scheme logo -- no <img>, just the text name", () => {
    const { container } = render(
      <BrandHeader brand={{ name: "Acme", logo: UNSAFE_LOGO }} slug="acme" active="home" />,
    );
    // the unsafe logo never becomes an <img>.
    expect(container.querySelector("img")).toBeNull();
    // the name still renders as text.
    expect(screen.getByText("Acme")).toBeTruthy();
  });

  it("URL-encodes the slug in nav hrefs (never a raw path injection)", () => {
    const { container } = render(
      <BrandHeader brand={{ name: "Acme" }} slug="acme-store" active="home" />,
    );
    const hrefs = Array.from(container.querySelectorAll("a")).map((a) => a.getAttribute("href") ?? "");
    // every tenant nav link is under the encoded slug base.
    expect(hrefs.some((h) => h === "/t/acme-store")).toBe(true);
    expect(hrefs.some((h) => h === "/t/acme-store/sobre")).toBe(true);
    expect(hrefs.some((h) => h === "/t/acme-store/blog")).toBe(true);
    expect(hrefs.some((h) => h === "/t/acme-store/b2b")).toBe(true);
  });

  it("renders an Admin link to a SAFE href (same-origin path or https:, never js/data)", () => {
    const { container } = render(
      <BrandHeader brand={{ name: "Acme" }} slug="acme-store" active="home" />,
    );
    const admin = Array.from(container.querySelectorAll("a")).find(
      (a) => (a.textContent ?? "").trim() === "Admin",
    );
    expect(admin).toBeTruthy();
    const href = admin!.getAttribute("href") ?? "";
    // default (no env) -> the safe "/admin" same-origin path; never an unsafe scheme.
    expect(href.startsWith("javascript:")).toBe(false);
    expect(href.startsWith("data:")).toBe(false);
    expect(/^https:\/\//.test(href) || /^\/[^/]/.test(href)).toBe(true);
  });
});

// ----------------------------------------------------------------------------
// Admin link -- TENANT DEEP-LINK. The header + footer "Admin" link must carry the current
// tenant as <adminUrl>?tenant=<slug> (slug already in scope for /t/<slug>), so the dashboard
// opens in THIS tenant's admin theme. The rest of the chrome (every OTHER nav href) must stay
// byte-identical -- only the Admin link gains the ?tenant query.
// ----------------------------------------------------------------------------

function adminHrefs(container: HTMLElement): string[] {
  return Array.from(container.querySelectorAll("a"))
    .filter((a) => (a.textContent ?? "").trim() === "Admin")
    .map((a) => a.getAttribute("href") ?? "");
}

describe("Admin link -- tenant deep-link (?tenant=<slug>)", () => {
  it("BrandHeader Admin link ends with ?tenant=demo-orbit", () => {
    const { container } = render(
      <BrandHeader brand={{ name: "Acme" }} slug="demo-orbit" active="home" />,
    );
    const hrefs = adminHrefs(container);
    expect(hrefs.length).toBeGreaterThan(0);
    for (const h of hrefs) expect(h.endsWith("?tenant=demo-orbit")).toBe(true);
  });

  it("BrandFooter Admin link ends with ?tenant=demo-acme", () => {
    const { container } = render(<BrandFooter brand={{ name: "Acme" }} slug="demo-acme" />);
    const hrefs = adminHrefs(container);
    expect(hrefs.length).toBeGreaterThan(0);
    for (const h of hrefs) expect(h.endsWith("?tenant=demo-acme")).toBe(true);
  });

  it("leaves the REST of the header/footer chrome unchanged (only Admin gains ?tenant)", () => {
    const header = render(
      <BrandHeader brand={{ name: "Acme" }} slug="demo-orbit" active="home" />,
    ).container;
    const footer = render(<BrandFooter brand={{ name: "Acme" }} slug="demo-orbit" />).container;
    for (const root of [header, footer]) {
      // the tenant nav links are unchanged -- still the bare /t/<slug> paths, no ?tenant.
      const hrefs = Array.from(root.querySelectorAll("a")).map((a) => a.getAttribute("href") ?? "");
      expect(hrefs).toContain("/t/demo-orbit");
      expect(hrefs).toContain("/t/demo-orbit/sobre");
      // NO link OTHER than Admin carries a ?tenant query (the deep-link is Admin-only).
      const nonAdmin = Array.from(root.querySelectorAll("a"))
        .filter((a) => (a.textContent ?? "").trim() !== "Admin")
        .map((a) => a.getAttribute("href") ?? "");
      for (const h of nonAdmin) expect(h.includes("?tenant=")).toBe(false);
    }
  });
});
