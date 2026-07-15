import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ProductFormShell } from "@/components/product-form";
import type { ProductDraft } from "@/components/product-form";
import { Pagination } from "@/components/ui";

// Smoke test for a core surface: the ProductFormShell (all 8 sections) renders,
// and the new Pagination control behaves at its boundaries (HARDEN mission).

function emptyDraft(): ProductDraft {
  return {
    slug: "",
    name: "",
    tagline: "",
    price: 0,
    images: [],
    description: "",
    long_description: "",
    why_it_works: "",
    benefits_functional: [],
    benefits_emotional: [],
    dims: { largura: "", altura: "", profundidade: "", unit: "cm" },
    materials: [],
    weight: "",
    custo: 0,
    margem_b2c: 0,
    margem_b2b: 0,
    seo_title: "",
    seo_description: "",
    seo_keywords: [],
    seo_alt_texts: [],
    quantity: 0,
    status: "draft",
    sku: "",
    shopify_variant_id: "",
  };
}

describe("ProductFormShell", () => {
  it("renders the masthead and every form section without crashing", () => {
    render(<ProductFormShell initialDraft={emptyDraft()} />);

    // empty name -> the placeholder title
    expect(screen.getByText("Untitled product")).toBeTruthy();

    // all eight section headings render
    for (const heading of [
      "// Basic info",
      "// Images",
      "// Description",
      "// Benefits",
      "// Dims / Specs",
      "// Pricing",
      "// SEO",
      "// Stock",
    ]) {
      expect(screen.getByText(heading)).toBeTruthy();
    }

    // the save footer is present (editable mode)
    expect(screen.getByRole("button", { name: "Salvar" })).toBeTruthy();
  });

  it("surfaces the 'nao vendavel' chip when there is no shopify_variant_id", () => {
    render(<ProductFormShell initialDraft={emptyDraft()} />);
    expect(screen.getByText("nao vendavel")).toBeTruthy();
  });
});

describe("Pagination", () => {
  it("renders nothing for a single page", () => {
    const { container } = render(
      <Pagination
        page={1}
        pageCount={1}
        total={5}
        start={1}
        end={5}
        canPrev={false}
        canNext={false}
        onPrev={() => {}}
        onNext={() => {}}
      />,
    );
    expect(container.querySelector('nav[aria-label="Pagination"]')).toBeNull();
  });

  it("renders the window line and disables prev on the first page", () => {
    const onNext = vi.fn();
    render(
      <Pagination
        page={1}
        pageCount={3}
        total={60}
        start={1}
        end={25}
        canPrev={false}
        canNext={true}
        onPrev={() => {}}
        onNext={onNext}
        unit="results"
      />,
    );

    expect(screen.getByText(/showing 1-25 of 60 results . page 1\/3/)).toBeTruthy();

    const prev = screen.getByRole("button", {
      name: "Previous page",
    }) as HTMLButtonElement;
    const next = screen.getByRole("button", {
      name: "Next page",
    }) as HTMLButtonElement;
    expect(prev.disabled).toBe(true);
    expect(next.disabled).toBe(false);

    fireEvent.click(next);
    expect(onNext).toHaveBeenCalledTimes(1);
  });
});
