import { describe, it, expect } from "vitest";
import { render, fireEvent } from "@testing-library/react";
import { MediaGallery } from "@/components/MediaGallery";

// ----------------------------------------------------------------------------
// MediaGallery object-fit switch. The main image defaults to object-contain (safe for
// an unknown ratio: letterbox, never crop). On load it reads the image's natural
// dimensions and switches to object-cover ONLY for a near-square photo (within ~10% of
// 1:1). These assert:
//   * default (pre-load / unknown dims) -> object-contain;
//   * a near-square natural ratio -> object-cover after load;
//   * an extreme (banner) ratio -> stays object-contain after load.
// jsdom does not compute naturalWidth/Height, so the test stubs them before firing load.
// ----------------------------------------------------------------------------

const SAFE = "https://cdn.example.com/p.jpg";

function mainImg(container: HTMLElement): HTMLImageElement {
  // the first <img> is the main image (thumbnails follow when >1 candidate).
  return container.querySelector("img") as HTMLImageElement;
}

function fireLoadWithDims(img: HTMLImageElement, w: number, h: number) {
  Object.defineProperty(img, "naturalWidth", { value: w, configurable: true });
  Object.defineProperty(img, "naturalHeight", { value: h, configurable: true });
  fireEvent.load(img);
}

describe("MediaGallery -- natural-aspect object-fit switch", () => {
  it("defaults to object-contain before load (safe default)", () => {
    const { container } = render(<MediaGallery candidates={[SAFE]} alt="p" />);
    expect(mainImg(container).className).toContain("object-contain");
    expect(mainImg(container).className).not.toContain("object-cover");
  });

  it("switches to object-cover for a near-square image", () => {
    const { container } = render(<MediaGallery candidates={[SAFE]} alt="p" />);
    fireLoadWithDims(mainImg(container), 1000, 1000); // 1:1 -> near-square
    expect(mainImg(container).className).toContain("object-cover");
    expect(mainImg(container).className).not.toContain("object-contain");
  });

  it("keeps object-contain for an extreme (banner) ratio", () => {
    const { container } = render(<MediaGallery candidates={[SAFE]} alt="p" />);
    fireLoadWithDims(mainImg(container), 1600, 400); // 4:1 -> extreme
    expect(mainImg(container).className).toContain("object-contain");
    expect(mainImg(container).className).not.toContain("object-cover");
  });

  it("treats unknown natural dims (0) as the safe contain default", () => {
    const { container } = render(<MediaGallery candidates={[SAFE]} alt="p" />);
    fireLoadWithDims(mainImg(container), 0, 0);
    expect(mainImg(container).className).toContain("object-contain");
  });
});
