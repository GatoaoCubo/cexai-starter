// SPEC 10 W5 -- the L3 FINISH: mount the field_manifest <ManifestForm> live + the
// content-review HITL page.
//
// Two surfaces under test, both driven OFFLINE (no network):
//   1. <ManifestEntityForm> -- the live mount of the field_manifest mold. It renders
//      required manifest fields, BLOCKS submit when a required field is empty (zod via
//      buildSchema, surfaced as inline errors), and on a valid submit calls
//      ApiClient.createEntity(slug, values) with the typed payload.
//   2. <ContentReview> -- the HITL gate. It lists REAL drafts (published !== true) read
//      via listEntity, approve calls setEntityPublished(slug, id, true), and the
//      approved item leaves the draft list. An all-published entity -> honest empty.
//
// The ApiClient is a real injected instance here (the components take a client prop),
// so we pass a hand-rolled fake exposing the spied methods -- no module mock needed.

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";

import { ManifestEntityForm } from "@/components/ManifestEntityForm";
import { ContentReview } from "@/components/ContentReview";
import { productManifest } from "@/lib/field-manifest";
import type { ApiClient } from "@/lib/api";
import type { EntityRecord, EntitySchema } from "@/lib/types";

// A minimal fake ApiClient: only the methods these components call, as spies.
function fakeClient(over: Partial<Record<string, ReturnType<typeof vi.fn>>> = {}) {
  return {
    createEntity: vi.fn(),
    listEntity: vi.fn(),
    setEntityPublished: vi.fn(),
    ...over,
  } as unknown as ApiClient & {
    createEntity: ReturnType<typeof vi.fn>;
    listEntity: ReturnType<typeof vi.fn>;
    setEntityPublished: ReturnType<typeof vi.fn>;
  };
}

// A publishable product schema mirroring the fixture (the review queue source).
function productSchema(): EntitySchema {
  return {
    entity: "products",
    singular: "Product",
    plural: "Products",
    icon: "table",
    writable: true,
    publishable: true,
    columns: [
      { key: "nome", label: "Name", primary: true },
      { key: "sku", label: "SKU" },
      { key: "preco", label: "Price", type: "currency", align: "right" },
      // admin_only must NOT appear in the review preview (margin guard).
      { key: "custo", label: "Cost", type: "currency", admin_only: true },
    ],
    fields: [],
  };
}

describe("ManifestEntityForm -- live mount of the field_manifest mold", () => {
  it("renders manifest-driven required fields", () => {
    const client = fakeClient();
    render(
      <ManifestEntityForm
        entity="products"
        singular="Product"
        manifest={productManifest}
        client={client}
      />,
    );
    // The manifest's first required field ("Nome do Produto") renders, with its
    // required marker, plus a section heading -- proof the form came from the manifest.
    expect(screen.getByText("Nome do Produto *")).toBeTruthy();
    expect(screen.getByText("Identidade")).toBeTruthy();
    // the submit affordance.
    expect(
      screen.getByRole("button", { name: /Create product/i }),
    ).toBeTruthy();
  });

  it("BLOCKS submit when required fields are empty (no createEntity call)", async () => {
    const client = fakeClient();
    render(
      <ManifestEntityForm
        entity="products"
        singular="Product"
        manifest={productManifest}
        client={client}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: /Create product/i }));
    // The honest validation summary appears and createEntity is NEVER called.
    await screen.findByRole("alert");
    expect(screen.getByText(/need(s)? attention/i)).toBeTruthy();
    expect(client.createEntity).not.toHaveBeenCalled();
  });

  it("submits createEntity(slug, typed values) when the required fields are filled", async () => {
    const client = fakeClient({
      createEntity: vi.fn().mockResolvedValue({ id: "products-newid", nome: "Cama Donut" }),
    });
    render(
      <ManifestEntityForm
        entity="products"
        singular="Product"
        manifest={productManifest}
        client={client}
      />,
    );

    // Fill the required text/number fields the base schema enforces. (Arrays/optional
    // fields are valid empty; status defaults to "draft" so the publish gate is inert.)
    type Fill = { label: string; value: string };
    const fills: Fill[] = [
      { label: "Nome do Produto *", value: "Cama Donut Teste" },
      { label: "Slug (URL) *", value: "cama-donut-teste" },
      { label: "Descrição Curta *", value: "Uma cama confortavel para gatos." },
      { label: "Preço Final (R$) *", value: "199.90" },
      { label: "Quantidade em Estoque *", value: "10" },
      { label: "Título SEO (max 60 caracteres) *", value: "Cama Donut para Gatos" },
      {
        label: "Meta Description (50-160 caracteres) *",
        value: "Uma cama donut super confortavel e duravel para o seu gato dormir tranquilo.",
      },
    ];
    // "images" is required (>=1). The ImageUploader exposes a URL text input; add one.
    for (const f of fills) {
      const labelEl = screen.getByText(f.label);
      const wrapper = labelEl.parentElement as HTMLElement;
      const control = wrapper.querySelector("input, textarea") as HTMLInputElement;
      fireEvent.change(control, { target: { value: f.value } });
    }
    // images: find the "Imagens e Videos" field block and add a URL via its text input.
    const imagesLabel = screen.getByText("Imagens e Vídeos *");
    const imagesWrap = imagesLabel.parentElement as HTMLElement;
    const urlInput = imagesWrap.querySelector(
      'input[type="url"], input[type="text"], input',
    ) as HTMLInputElement | null;
    if (urlInput) {
      fireEvent.change(urlInput, {
        target: { value: "https://example.com/cama.jpg" },
      });
      // ImageUploader commits the URL on Enter.
      fireEvent.keyDown(urlInput, { key: "Enter", code: "Enter" });
    }

    fireEvent.click(screen.getByRole("button", { name: /Create product/i }));

    await waitFor(() => {
      expect(client.createEntity).toHaveBeenCalledTimes(1);
    });
    const [slug, values] = client.createEntity.mock.calls[0];
    expect(slug).toBe("products");
    // the typed payload carries the values the operator entered (zod-coerced).
    expect(values.name).toBe("Cama Donut Teste");
    expect(values.slug).toBe("cama-donut-teste");
    expect(values.price).toBe(199.9);
    expect(values.quantity).toBe(10);
    // status defaulted to draft (a draft create, publish gate inert).
    expect(values.status).toBe("draft");
  });
});

describe("ContentReview -- the content-review HITL gate", () => {
  let client: ReturnType<typeof fakeClient>;

  beforeEach(() => {
    client = fakeClient();
    // Two drafts + one published row (the published one must NOT be listed).
    client.listEntity = vi.fn().mockResolvedValue([
      { id: "product-0001", nome: "Sample Widget A", sku: "WGT-A-001", preco: 49, custo: 18, published: false },
      { id: "product-0002", nome: "Sample Widget B", sku: "WGT-B-002", preco: 89, custo: 40, published: false },
      { id: "product-0003", nome: "Sample Widget C", sku: "WGT-C-003", preco: 129, custo: 55, published: true },
    ] as EntityRecord[]);
    client.setEntityPublished = vi.fn().mockResolvedValue({
      id: "product-0001",
      nome: "Sample Widget A",
      published: true,
      published_at: "2026-06-25T00:00:00+00:00",
    });
  });

  it("lists ONLY the draft rows (published rows are excluded)", async () => {
    render(<ContentReview client={client} schemas={[productSchema()]} />);
    await screen.findByText("Sample Widget A");
    expect(screen.getByText("Sample Widget B")).toBeTruthy();
    // the published row is NOT in the review queue.
    expect(screen.queryByText("Sample Widget C")).toBeNull();
    // the count line reflects 2 drafts.
    expect(screen.getByText(/2 to review/)).toBeTruthy();
  });

  it("does NOT show admin_only columns in the review preview (margin guard)", async () => {
    render(<ContentReview client={client} schemas={[productSchema()]} />);
    await screen.findByText("Sample Widget A");
    // "Cost" is admin_only -> excluded; "SKU" (a normal column) is shown.
    expect(screen.queryByText("Cost")).toBeNull();
    expect(screen.getAllByText("SKU").length).toBeGreaterThanOrEqual(1);
  });

  it("approve -> setEntityPublished(slug, id, true) and the item leaves the list", async () => {
    render(<ContentReview client={client} schemas={[productSchema()]} />);
    await screen.findByText("Sample Widget A");

    // Approve the FIRST draft (row-0001).
    const approveButtons = screen.getAllByRole("button", {
      name: /Approve and publish Product/i,
    });
    fireEvent.click(approveButtons[0]);

    await waitFor(() => {
      expect(client.setEntityPublished).toHaveBeenCalledWith("products", "product-0001", true);
    });
    // the approved item leaves the draft QUEUE. Assert via the card's provenance line
    // (id=product-0001 appears ONLY in its review card, never in the success banner),
    // so we test the queue specifically -- not the "Published <label>" confirmation.
    await waitFor(() => {
      expect(screen.queryByText(/id=product-0001/)).toBeNull();
    });
    // B remains in the queue; the count dropped to 1.
    expect(screen.getByText(/id=product-0002/)).toBeTruthy();
    expect(screen.getByText(/1 to review/)).toBeTruthy();
  });

  it("shows an honest empty state when there are no drafts", async () => {
    client.listEntity = vi.fn().mockResolvedValue([
      { id: "p1", nome: "Live One", published: true },
    ] as EntityRecord[]);
    render(<ContentReview client={client} schemas={[productSchema()]} />);
    await screen.findByText("Nada para revisar");
    expect(client.setEntityPublished).not.toHaveBeenCalled();
  });

  it("shows the empty state when no entity is publishable", async () => {
    const notPublishable: EntitySchema = { ...productSchema(), publishable: false };
    render(<ContentReview client={client} schemas={[notPublishable]} />);
    await screen.findByText("Nada para revisar");
    // a non-publishable entity is never even read for drafts.
    expect(client.listEntity).not.toHaveBeenCalled();
  });
});
