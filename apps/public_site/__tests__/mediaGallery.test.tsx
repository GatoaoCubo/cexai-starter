import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MediaGallery } from "@/components/MediaGallery";

// ----------------------------------------------------------------------------
// MediaGallery -- the PDP image gallery. SECURITY-FIRST: the gallery receives RAW,
// tenant-controlled URL candidates (forwarded verbatim by the backend) and MUST gate
// EVERY one with isSafeMediaSrc before it becomes an <img src>. These assert:
//   * a SAFE candidate (https: / data:image) renders an <img>;
//   * an UNSAFE candidate (javascript:, http:, data:text/html, file:) is DROPPED -- it
//     never renders a tag and never appears as a src;
//   * zero safe candidates -> renders nothing (degrade-never);
//   * thumbnails switch the main image (read-only interaction only).
// ----------------------------------------------------------------------------

const SAFE_A = "data:image/svg+xml;utf8," + encodeURIComponent("<svg/>");
const SAFE_B = "https://cdn.example.com/b.jpg";
const UNSAFE_JS = "javascript:alert(1)";
const UNSAFE_HTTP = "http://insecure.example.com/c.jpg";
const UNSAFE_HTML = "data:text/html,<script>alert(1)</script>";
const UNSAFE_FILE = "file:///etc/passwd";

function srcs(container: HTMLElement): string[] {
  return Array.from(container.querySelectorAll("img")).map((i) => i.getAttribute("src") ?? "");
}

describe("MediaGallery -- safe-src gate", () => {
  it("renders an <img> for a SAFE candidate", () => {
    const { container } = render(<MediaGallery candidates={[SAFE_A]} alt="produto" />);
    const all = srcs(container);
    expect(all).toContain(SAFE_A);
  });

  it("DROPS every unsafe-scheme candidate -- none reaches an <img src>", () => {
    const { container } = render(
      <MediaGallery
        candidates={[UNSAFE_JS, SAFE_A, UNSAFE_HTTP, UNSAFE_HTML, UNSAFE_FILE, SAFE_B]}
        alt="produto"
      />,
    );
    const all = srcs(container);
    // the two safe ones are present...
    expect(all).toContain(SAFE_A);
    expect(all).toContain(SAFE_B);
    // ...and NOT ONE unsafe scheme leaked into any src.
    for (const bad of [UNSAFE_JS, UNSAFE_HTTP, UNSAFE_HTML, UNSAFE_FILE]) {
      expect(all.some((s) => s === bad)).toBe(false);
    }
  });

  it("renders NOTHING when no candidate is safe (degrade-never)", () => {
    const { container } = render(
      <MediaGallery candidates={[UNSAFE_JS, UNSAFE_HTTP, UNSAFE_HTML]} alt="x" />,
    );
    expect(container.firstChild).toBeNull();
    expect(container.querySelector("img")).toBeNull();
  });

  it("renders NOTHING for an empty candidate list", () => {
    const { container } = render(<MediaGallery candidates={[]} alt="x" />);
    expect(container.firstChild).toBeNull();
  });

  it("switches the main image when a thumbnail is clicked (read-only)", () => {
    const { container } = render(<MediaGallery candidates={[SAFE_A, SAFE_B]} alt="produto" />);
    // main image starts on the first safe candidate.
    const main = container.querySelector("img");
    expect(main!.getAttribute("src")).toBe(SAFE_A);
    // a thumbnail strip exists (2 safe -> thumbnails render); clicking the 2nd selects it.
    const thumbs = screen.getAllByRole("listitem");
    expect(thumbs.length).toBe(2);
    fireEvent.click(thumbs[1]);
    // the main image now shows the second safe candidate.
    const mainAfter = container.querySelector("img");
    expect(mainAfter!.getAttribute("src")).toBe(SAFE_B);
    // READ-ONLY: no upload affordance anywhere.
    expect(container.querySelector('input[type="file"]')).toBeNull();
  });
});
