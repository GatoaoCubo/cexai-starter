import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import {
  DualOutputFacePublic,
  type PublicDualOutput,
} from "@/components/DualOutputFacePublic";

// ----------------------------------------------------------------------------
// DualOutputFacePublic -- the READ-ONLY public face. These assert the security +
// honesty contract:
//   * renders the structured payload (typed sections), as TEXT;
//   * renders media ONLY when the src passes isSafeMediaSrc; an unsafe-src slot
//     becomes a static "midia indisponivel" placeholder (no <img> for it);
//   * exposes NO edit/upload affordance (no file input, no dropzone copy);
//   * NEVER injects raw human_html into the live DOM -- it lives ONLY inside a
//     sandboxed <iframe srcDoc> with NO allow-scripts.
// ----------------------------------------------------------------------------

const SAFE_IMG = "data:image/svg+xml;utf8," + encodeURIComponent("<svg/>");
const UNSAFE_IMG = "javascript:alert(1)";

function baseAsset(over: Partial<PublicDualOutput> = {}): PublicDualOutput {
  return {
    id: "rec_1",
    capability: "marketplace_listing",
    real: false,
    sections: [
      {
        title: "Ficha",
        layout: "fields",
        rows: [
          { label: "Altura", value: "1,2 m" },
          { label: "Material", value: "Sisal" },
        ],
      },
    ],
    ...over,
  };
}

describe("DualOutputFacePublic", () => {
  it("renders the typed structured payload as text", () => {
    render(<DualOutputFacePublic dual={baseAsset()} />);
    expect(screen.getByText("Ficha")).toBeTruthy();
    expect(screen.getByText("Altura")).toBeTruthy();
    expect(screen.getByText("1,2 m")).toBeTruthy();
    expect(screen.getByText("Material")).toBeTruthy();
  });

  it("renders a SAFE-src media slot as an <img>", () => {
    const dual = baseAsset({
      media_slots: [
        { key: "hero", kind: "image", status: "generated", src: SAFE_IMG, alt: "hero", editable: true, uploadFallback: true },
      ],
    });
    const { container } = render(<DualOutputFacePublic dual={dual} />);
    const img = container.querySelector("img");
    expect(img).not.toBeNull();
    expect(img!.getAttribute("src")).toBe(SAFE_IMG);
  });

  it("DROPS an UNSAFE-src media slot -- no <img>, a placeholder instead", () => {
    const dual = baseAsset({
      media_slots: [
        { key: "hero", kind: "image", status: "generated", src: UNSAFE_IMG, alt: "x", editable: true, uploadFallback: true },
      ],
    });
    const { container } = render(<DualOutputFacePublic dual={dual} />);
    // no <img> rendered for the unsafe slot.
    expect(container.querySelector("img")).toBeNull();
    // the static placeholder is shown instead (never a broken/hostile tag).
    expect(screen.getByText("midia indisponivel")).toBeTruthy();
  });

  it("renders the empty/placeholder shell for an empty slot (no upload affordance)", () => {
    const dual = baseAsset({
      media_slots: [
        { key: "hero", kind: "image", status: "empty", editable: true, uploadFallback: true },
      ],
    });
    const { container } = render(<DualOutputFacePublic dual={dual} />);
    expect(screen.getByText("midia indisponivel")).toBeTruthy();
    // READ-ONLY: there is NO file input and NO dropzone upload copy anywhere.
    expect(container.querySelector('input[type="file"]')).toBeNull();
    expect(screen.queryByText(/enviar imagem/i)).toBeNull();
    expect(screen.queryByText(/arraste/i)).toBeNull();
    expect(screen.queryByText(/trocar/i)).toBeNull();
  });

  it("NEVER injects human_html into the live DOM -- only a sandboxed iframe carries it", () => {
    const html =
      "<!doctype html><html><body><h1>tenant authored</h1>" +
      "x".repeat(220) + // long enough to earn the affordance
      "</body></html>";
    const { container } = render(<DualOutputFacePublic dual={baseAsset({ human_html: html })} />);

    // The live DOM does NOT contain the tenant <h1> text injected directly (it lives
    // inside the iframe's srcDoc, which jsdom does not parse into the parent DOM).
    expect(screen.queryByText("tenant authored")).toBeNull();

    // The affordance is a toggle; the iframe is only mounted once opened. Assert the
    // component is wired to render it via a SANDBOXED iframe (srcDoc + sandbox="" +
    // NO allow-scripts) by checking the toggle exists and no live-DOM injection path
    // is present (no element carries the raw html as innerHTML).
    expect(screen.getByText(/versao publicada/i)).toBeTruthy();
    // there is no dangerouslySetInnerHTML sink: no node in the tree has the tenant
    // markup as its innerHTML on the live page.
    expect(container.innerHTML).not.toContain("<h1>tenant authored</h1>");
  });

  it("a SAFE human_html iframe (once shown) uses sandbox with NO allow-scripts", () => {
    // Render and force the toggle open via the DOM (click the toggle button).
    const html = "<!doctype html><html><body>ok " + "y".repeat(220) + "</body></html>";
    const { container } = render(<DualOutputFacePublic dual={baseAsset({ human_html: html })} />);
    const toggle = screen.getByRole("button", { name: /versao publicada/i });
    fireEvent.click(toggle);
    const iframe = container.querySelector("iframe");
    expect(iframe).not.toBeNull();
    // the sandbox attribute is present and EMPTY (no allow-scripts -> scripts blocked).
    expect(iframe!.getAttribute("sandbox")).toBe("");
    const sandbox = iframe!.getAttribute("sandbox") ?? "";
    expect(sandbox.includes("allow-scripts")).toBe(false);
    // it carries the html via srcDoc (isolated), not as a same-origin src.
    expect(iframe!.getAttribute("srcdoc")).toContain("ok");
  });

  it("renders nothing when the asset has no renderable surface (degrade-never)", () => {
    const { container } = render(
      <DualOutputFacePublic dual={{ id: "x", capability: "k" }} />,
    );
    expect(container.firstChild).toBeNull();
  });

  it("shows 'amostra' for a not-real asset and 'resultado real' for a real one", () => {
    const { rerender } = render(<DualOutputFacePublic dual={baseAsset({ real: false })} />);
    expect(screen.getByText("amostra")).toBeTruthy();

    rerender(<DualOutputFacePublic dual={baseAsset({ real: true })} />);
    expect(screen.getByText("resultado real")).toBeTruthy();
  });

  it("sanitizes the internal scaffold marker out of a published section (never leaks)", () => {
    const dual = baseAsset({
      sections: [
        {
          title: "Variantes",
          layout: "list",
          items: ["hook real", "ainda (generation_pending) aqui"],
        },
      ],
    });
    const { container } = render(<DualOutputFacePublic dual={dual} />);
    // the raw marker is NEVER present in the rendered DOM.
    expect(container.innerHTML).not.toContain("generation_pending");
  });
});
