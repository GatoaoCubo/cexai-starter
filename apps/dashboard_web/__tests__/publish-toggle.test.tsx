// SPEC 10 W1 -- the L2 PUBLISH SEAM, frontend component half.
//
// DataManager's Publish/Unpublish toggle -- proves the UI: a publishable entity renders the
// honest published/draft status + a toggle that calls setEntityPublished with the FLIPPED state,
// then reloads. A non-publishable entity renders NO toggle (zero-regression).
//
// Driven offline: this file mocks @/lib/api's ApiClient (spy on the methods) + @/lib/auth's
// useAuth (supply a token) so the component is tested without a network. The api.ts WIRE shape
// (path/body/no-tenant-leak) is proven separately in publish-api.test.ts (which uses the REAL
// ApiClient against a stubbed fetch -- it must NOT mock @/lib/api).

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";

import type { EntityRecord, EntitySchema } from "@/lib/types";

// Spy handles the mocked ApiClient exposes so the test can assert calls + drive returns.
const apiSpies = {
  listEntity: vi.fn(),
  setEntityPublished: vi.fn(),
  deleteEntity: vi.fn(),
  createEntity: vi.fn(),
  updateEntity: vi.fn(),
};

// Mock the api module: ApiClient is a class whose instances expose the spies. ApiClientError is
// re-exported as a real Error subclass (DataManager imports it for messageOf).
vi.mock("@/lib/api", () => {
  class ApiClientError extends Error {
    status: number;
    reason?: string;
    constructor(status: number, message: string, reason?: string) {
      super(message);
      this.name = "ApiClientError";
      this.status = status;
      this.reason = reason;
    }
  }
  class ApiClient {
    constructor(_token: string) {}
    listEntity = apiSpies.listEntity;
    setEntityPublished = apiSpies.setEntityPublished;
    deleteEntity = apiSpies.deleteEntity;
    createEntity = apiSpies.createEntity;
    updateEntity = apiSpies.updateEntity;
  }
  return { ApiClient, ApiClientError };
});

// Mock useAuth so DataManager gets a token (-> it builds a client).
vi.mock("@/lib/auth", () => ({
  useAuth: () => ({
    session: { access_token: "jwt-token-abc", tenant_id: "t-a", email: "x@y.z" },
  }),
}));

import { DataManager } from "@/components/DataManager";

function schema(publishable: boolean): EntitySchema {
  return {
    entity: "products",
    singular: "Product",
    plural: "Products",
    columns: [{ key: "name", label: "Name", primary: true }],
    fields: [{ key: "name", label: "Name", type: "text" }],
    writable: true,
    publishable,
  };
}

describe("DataManager publish toggle", () => {
  beforeEach(() => {
    apiSpies.listEntity.mockReset();
    apiSpies.setEntityPublished.mockReset();
    // Two rows: one already published, one draft.
    apiSpies.listEntity.mockResolvedValue([
      { id: "row-1", name: "Alpha", published: false },
      { id: "row-2", name: "Beta", published: true },
    ] as EntityRecord[]);
    apiSpies.setEntityPublished.mockResolvedValue({
      id: "row-1",
      name: "Alpha",
      published: true,
      published_at: "2026-06-25T00:00:00+00:00",
    });
  });

  it("renders an honest published/draft status for a publishable entity", async () => {
    render(<DataManager schema={schema(true)} />);
    // wait for the rows to load.
    await screen.findByText("Alpha");
    // the draft row shows "draft", the published row shows "public" (honest from the row state).
    expect(screen.getAllByText("draft").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("public").length).toBeGreaterThanOrEqual(1);
  });

  it("flips the draft row with the FLIPPED state then reloads", async () => {
    render(<DataManager schema={schema(true)} />);
    await screen.findByText("Alpha");

    // row-1 is draft -> its toggle is labelled "Publish Product".
    const publishBtn = screen.getByRole("button", { name: "Publish Product" });
    fireEvent.click(publishBtn);

    await waitFor(() => {
      expect(apiSpies.setEntityPublished).toHaveBeenCalledTimes(1);
    });
    // called with the entity slug, the row id, and the FLIPPED state (draft -> true).
    expect(apiSpies.setEntityPublished).toHaveBeenCalledWith("products", "row-1", true);
    // a reload (listEntity) happens after the flip: once on mount + once after the toggle.
    await waitFor(() => {
      expect(apiSpies.listEntity).toHaveBeenCalledTimes(2);
    });
  });

  it("unpublishes the published row (flips true -> false)", async () => {
    render(<DataManager schema={schema(true)} />);
    await screen.findByText("Beta");
    // row-2 is published -> its toggle is labelled "Unpublish Product".
    const unpublishBtn = screen.getByRole("button", { name: "Unpublish Product" });
    fireEvent.click(unpublishBtn);
    await waitFor(() => {
      expect(apiSpies.setEntityPublished).toHaveBeenCalledWith("products", "row-2", false);
    });
  });

  it("renders NO publish toggle when the entity is not publishable (zero-regression)", async () => {
    render(<DataManager schema={schema(false)} />);
    await screen.findByText("Alpha");
    expect(screen.queryByRole("button", { name: /Publish Product/ })).toBeNull();
    expect(screen.queryByRole("button", { name: /Unpublish Product/ })).toBeNull();
    // and no status chips either.
    expect(screen.queryByText("public")).toBeNull();
    expect(screen.queryByText("draft")).toBeNull();
  });
});
