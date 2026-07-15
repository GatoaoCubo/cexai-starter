import { describe, it, expect } from "vitest";
import {
  fxListEntitySchemas,
  fxListEntity,
  fxCreateEntity,
  fxDeleteEntity,
} from "@/lib/fixtures";
import type { EntitySchema } from "@/lib/types";

// ----------------------------------------------------------------------------
// SPEC 05 lead-gen suite, Phase 1c: the ``leads`` managed entity must appear in
// the Data tab (fixtures mode) with working CRUD -- the CRM seed (where scraped
// leads land). These tests exercise the SAME fixtures path the Data tab uses:
//   getEntitySchemas() -> ApiClient.listEntitySchemas() -> fxListEntitySchemas()
//   DataManager.load() -> ApiClient.listEntity()          -> fxListEntity()
// so a green run proves the entity + rows are present, shape-valid, honest, and
// CRUD-able offline -- without a backend.
//
// The NEVER-FABRICATE discipline (spec sec 4.6 / 5) is asserted directly on the
// seeded sample rows: a contact is either an honest public-access note or "--",
// never a real-looking email/phone.
// ----------------------------------------------------------------------------

const LEAD_CHANNELS = ["b2c_marketplace", "b2b_cnpj", "ugc_social"];
const LEAD_STATUSES = ["novo", "qualificado", "em_contato", "descartado"];
const LEAD_TYPES = ["pessoa", "empresa"];

async function leadsSchema(): Promise<EntitySchema> {
  const schemas = await fxListEntitySchemas();
  const leads = schemas.find((s) => s.entity === "leads");
  expect(leads, "the leads entity must be declared in the fixtures schemas").toBeDefined();
  return leads as EntitySchema;
}

describe("leads managed entity (fixtures)", () => {
  it("is present in the Data tab entity list and is writable", async () => {
    const schema = await leadsSchema();
    expect(schema.entity).toBe("leads");
    expect(schema.singular).toBe("Lead");
    expect(schema.plural).toBe("Leads");
    // writable so the Data tab renders create/edit/delete affordances.
    expect(schema.writable).not.toBe(false);
    expect(schema.nucleus).toBe("N01");
  });

  it("declares the spec sec-5 CRUD subset as columns + fields", async () => {
    const schema = await leadsSchema();
    const expectedKeys = [
      "nome",
      "tipo",
      "canal",
      "fonte",
      "contato",
      "sinal",
      "score",
      "status",
    ];
    const colKeys = schema.columns.map((c) => c.key);
    const fieldKeys = schema.fields.map((f) => f.key);
    for (const k of expectedKeys) {
      expect(colKeys, `column ${k}`).toContain(k);
      expect(fieldKeys, `field ${k}`).toContain(k);
    }
    // a primary column exists (the row label) and it is the lead name.
    const primary = schema.columns.find((c) => c.primary);
    expect(primary?.key).toBe("nome");
    // the enum fields offer exactly the spec's controlled vocabularies.
    const opt = (key: string) =>
      (schema.fields.find((f) => f.key === key)?.options ?? []).map((o) => o.value);
    expect(opt("tipo").sort()).toEqual([...LEAD_TYPES].sort());
    expect(opt("canal").sort()).toEqual([...LEAD_CHANNELS].sort());
    expect(opt("status").sort()).toEqual([...LEAD_STATUSES].sort());
    // no admin_only/sensitive columns on leads (none in the sec-5 CRUD subset).
    expect(schema.columns.some((c) => c.admin_only)).toBe(false);
    expect(schema.fields.some((f) => f.admin_only)).toBe(false);
  });

  it("seeds the 7 honest sample leads (mirrors MOLD_LEADGEN)", async () => {
    const rows = await fxListEntity("leads");
    expect(rows.length).toBe(7);
    // every seeded row is shape-valid against the controlled vocabularies.
    for (const r of rows) {
      expect(typeof r.nome).toBe("string");
      expect((r.nome as string).length).toBeGreaterThan(0);
      expect(LEAD_TYPES).toContain(r.tipo);
      expect(LEAD_CHANNELS).toContain(r.canal);
      expect(LEAD_STATUSES).toContain(r.status);
      // score is a confidence in [0, 1].
      expect(typeof r.score).toBe("number");
      expect(r.score as number).toBeGreaterThanOrEqual(0);
      expect(r.score as number).toBeLessThanOrEqual(1);
    }
    // the funnel is honestly mixed (not all "qualificado") -- proves the status lifecycle.
    const statuses = new Set(rows.map((r) => r.status));
    expect(statuses.has("qualificado")).toBe(true);
    expect(statuses.has("novo")).toBe(true);
    expect(statuses.has("descartado")).toBe(true);
  });

  it("never fabricates a contact in the sample rows (spec sec 4.6 / 5)", async () => {
    const rows = await fxListEntity("leads");
    // No seeded contact looks like a concrete email or phone number: it is an
    // honest public-access note or "--". This is the anti-fabrication contract.
    const EMAIL = /[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}/i;
    const PHONE = /\+?\d[\d\s().-]{6,}\d/; // a real-looking phone string
    for (const r of rows) {
      const contato = String(r.contato ?? "");
      expect(contato.length, `lead ${r.id} has a contact note`).toBeGreaterThan(0);
      expect(EMAIL.test(contato), `lead ${r.id} contact must not be a real email`).toBe(false);
      expect(PHONE.test(contato), `lead ${r.id} contact must not be a real phone`).toBe(false);
    }
    // at least one lead has the explicit "--" absent-contact marker.
    expect(rows.some((r) => String(r.contato).startsWith("--"))).toBe(true);
  });

  it("supports create + delete through the fixtures CRUD path", async () => {
    const before = (await fxListEntity("leads")).length;
    const created = await fxCreateEntity("leads", {
      nome: "Lead de teste (vitest)",
      tipo: "pessoa",
      canal: "ugc_social",
      fonte: "reddit",
      contato: "-- (sem contato publico)",
      sinal: "comentario de teste",
      score: 0.6,
      status: "novo",
    });
    expect(created.id).toMatch(/^leads-/);
    expect(created.nome).toBe("Lead de teste (vitest)");
    const after = await fxListEntity("leads");
    expect(after.length).toBe(before + 1);
    expect(after.some((r) => r.id === created.id)).toBe(true);

    // clean up so the seeded count stays stable for other tests / re-runs.
    await fxDeleteEntity("leads", created.id);
    const restored = await fxListEntity("leads");
    expect(restored.length).toBe(before);
    expect(restored.some((r) => r.id === created.id)).toBe(false);
  });
});
