import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import IntakePage from "@/app/intake/page";

// ----------------------------------------------------------------------------
// /intake -- RTL smoke of the form page (R-283). The PURE rules live in
// lib/intake (tested in intake.test.ts); here we assert the page WIRING:
// the 3 persona sections render, actions stay disabled until the required
// tier is valid, an invalid value surfaces its inline (blocking) error, the
// download path is always present, and the DEV resolve result -- ok, fail,
// and the 403 prod-refusal -- renders HONESTLY with the download fallback.
// ----------------------------------------------------------------------------

afterEach(() => {
  vi.unstubAllGlobals();
  // v2 (2026-07-07): the page now auto-saves a localStorage draft on every
  // keystroke (DP5). Vitest shares ONE jsdom window/localStorage across every
  // it() in this file -- without this clear, a later test's fresh <IntakePage
  // /> mount would silently RESTORE a draft an EARLIER test wrote, breaking
  // the "starts empty" assumption several tests below depend on.
  window.localStorage.clear();
});

/** Fill every REQUIRED field with a valid value (ids are the page's stable
 *  "intake-<dotted-key-with-dashes>" contract). */
function fillRequired(container: HTMLElement) {
  const type = (id: string, value: string) => {
    const el = container.querySelector("#" + id);
    if (!el) throw new Error("missing field #" + id);
    fireEvent.change(el, { target: { value } });
  };
  type("intake-identity-brand_name", "Cafe Borealis");
  type("intake-identity-brand_tagline", "Cafes especiais do cerrado");
  type("intake-identity-brand_mission", "Levar cafe especial rastreavel a quem prepara em casa");
  type("intake-identity-brand_values", "rastreabilidade\nfrescor\nsimplicidade");
  type("intake-archetype-brand_archetype", "everyman");
  type("intake-voice-tone", "proximo e direto");
  type("intake-voice-formality", "2");
  type("intake-audience-icp", "Quem prepara cafe coado em casa e quer frescor");
  type("intake-audience-transformation", "From cafe velho to xicara fresca through assinatura");
  type("intake-visual-colors-primary", "#3B2A20");
  type("intake-visual-colors-secondary", "#F4EDE3");
  type("intake-visual-colors-accent", "#C97B3D");
  type("intake-positioning-category", "cafe especial em assinatura");
  type("intake-positioning-uvp", "Assinatura de cafe especial com torra na semana do envio");
  type("intake-monetization-pricing_model", "hybrid");
  type("intake-monetization-currency", "BRL");
}

function getButtons() {
  const download = screen.getByRole("button", { name: "Baixar answers YAML" });
  const resolve = screen.getByRole("button", { name: /Resolver agora \(DEV\)/ });
  return { download, resolve };
}

describe("/intake page", () => {
  it("renders the 3 persona sections of the R-149 template", () => {
    render(<IntakePage />);
    expect(
      screen.getByRole("heading", { name: /Persona A -- Fundador\(a\)/ }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /Persona B -- Comercial/ }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /Persona C -- Operacao/ }),
    ).toBeInTheDocument();
  });

  it("renders the R-276 refs-only credentials warning (never a literal secret)", () => {
    render(<IntakePage />);
    expect(screen.getByText(/nunca um segredo literal/)).toBeInTheDocument();
    expect(screen.getByText(/R-276/)).toBeInTheDocument();
  });

  it("keeps BOTH actions present but disabled until the required tier is valid", () => {
    const { container } = render(<IntakePage />);
    const { download, resolve } = getButtons();
    expect(download).toBeDisabled();
    expect(resolve).toBeDisabled();

    fillRequired(container);
    expect(download).toBeEnabled();
    expect(resolve).toBeEnabled();
  });

  it("surfaces an inline blocking error for an invalid HEX and disables the actions again", () => {
    const { container } = render(<IntakePage />);
    fillRequired(container);
    fireEvent.change(container.querySelector("#intake-visual-colors-primary")!, {
      target: { value: "#GGGGGG" },
    });
    expect(screen.getByText(/HEX invalido/)).toBeInTheDocument();
    const { download, resolve } = getButtons();
    expect(download).toBeDisabled();
    expect(resolve).toBeDisabled();
  });

  it("renders a DEV resolve SUCCESS honestly (summary + paths + consume command, never auto-run)", async () => {
    const fetchMock = vi.fn(async () => ({
      json: async () => ({
        ok: true,
        summary: "[OK] resolved form_v1: 28 field(s) emitted, 0 warning(s), 0 deferred, 0 unmapped",
        resolver_warnings: [],
        answers_path: ".cex/runtime/intake/borealis-cafe_x_answers.yaml",
        brand_init_path: ".cex/runtime/intake/borealis-cafe_x_brand_init.yaml",
        provenance_path: ".cex/runtime/intake/borealis-cafe_x_provenance.json",
        shape_path: ".cex/runtime/intake/borealis-cafe_x_shape.json",
        bootstrap_cmd:
          "python _tools/cex_bootstrap.py --tenant borealis-cafe --from-file .cex/runtime/intake/borealis-cafe_x_brand_init.yaml",
      }),
    }));
    vi.stubGlobal("fetch", fetchMock);

    const { container } = render(<IntakePage />);
    fillRequired(container);
    fireEvent.submit(container.querySelector("form")!);

    await waitFor(() => expect(screen.getByText("Resolvido")).toBeInTheDocument());
    expect(fetchMock).toHaveBeenCalledOnce();
    const resultSection = within(
      container.querySelector('section[aria-live="polite"]') as HTMLElement,
    );
    expect(resultSection.getByText(/28 field\(s\) emitted/)).toBeInTheDocument();
    // The brand_init path renders twice ON PURPOSE (the dd row + inside the
    // consume command) -- both inside the result section.
    expect(
      resultSection.getAllByText(/borealis-cafe_x_brand_init\.yaml/).length,
    ).toBeGreaterThanOrEqual(1);
    // The consume command is DISPLAYED, never executed.
    expect(
      resultSection.getByText(/python _tools\/cex_bootstrap\.py --tenant borealis-cafe/),
    ).toBeInTheDocument();
  });

  it("renders the 403 prod-refusal honestly and points at the always-on download fallback", async () => {
    const fetchMock = vi.fn(async () => ({
      json: async () => ({
        ok: false,
        errors: [
          "/api/intake is DEV-ONLY. It is enabled only when NODE_ENV=development AND the " +
            "server-only CEXAI_ONBOARD_ENABLED=1 -- it can never run in a prod/deployed build.",
        ],
      }),
    }));
    vi.stubGlobal("fetch", fetchMock);

    const { container } = render(<IntakePage />);
    fillRequired(container);
    fireEvent.submit(container.querySelector("form")!);

    await waitFor(() => expect(screen.getByText("Nao resolvido")).toBeInTheDocument());
    // Scoped to the result section: "DEV-ONLY" also appears (on purpose) in the
    // page's static note under the actions.
    const resultSection = within(
      container.querySelector('section[aria-live="polite"]') as HTMLElement,
    );
    expect(resultSection.getByText(/DEV-ONLY/)).toBeInTheDocument();
    // The fallback copy: the downloaded file feeds the SAME resolver via CLI.
    expect(
      resultSection.getByText(/o arquivo baixado alimenta o MESMO resolver via CLI/),
    ).toBeInTheDocument();
  });

  it("renders a transport failure honestly (no fabricated result)", async () => {
    const fetchMock = vi.fn(async () => {
      throw new Error("boom");
    });
    vi.stubGlobal("fetch", fetchMock);

    const { container } = render(<IntakePage />);
    fillRequired(container);
    fireEvent.submit(container.querySelector("form")!);

    await waitFor(() =>
      expect(screen.getByText(/Falha de rede ao chamar \/api\/intake/)).toBeInTheDocument(),
    );
  });
});

// ----------------------------------------------------------------------------
// v2 (2026-07-07, decision_manifest_intake_v2_2026_07_07.yaml): fases nomeadas,
// welcome acolhedor, the 17 new optional fields, and localStorage draft
// persistence (DP5). PURE VALIDATION logic already covered in intake.test.ts --
// these are page-level WIRING smoke tests.
// ----------------------------------------------------------------------------
describe("/intake page -- v2: fases nomeadas + welcome", () => {
  it("keeps the 3 original Persona headings AND surfaces named 'Fase N de 3' labels", () => {
    render(<IntakePage />);
    expect(screen.getByRole("heading", { name: /Fase 1 de 3/ })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /Fase 2 de 3/ })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /Fase 3 de 3/ })).toBeInTheDocument();
    // the pre-existing R-283 assertions must STILL resolve (zero regression).
    expect(
      screen.getByRole("heading", { name: /Persona A -- Fundador\(a\)/ }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /Persona B -- Comercial/ }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /Persona C -- Operacao/ }),
    ).toBeInTheDocument();
  });

  it("renders a generic warm welcome with no ?nome= URL param", () => {
    render(<IntakePage />);
    expect(
      screen.getByRole("heading", { name: /Seja bem-vindo\(a\)!/ }),
    ).toBeInTheDocument();
  });

  it("renders the 17 new fields as visibly optional (no required marker)", () => {
    const { container } = render(<IntakePage />);
    expect(container.querySelector("#intake-market-competitors")).toBeInTheDocument();
    expect(container.querySelector("#intake-audience-wtp_band")).toBeInTheDocument();
    expect(container.querySelector("#intake-contact-name")).toBeInTheDocument();
    expect(container.querySelector("#intake-applications-surfaces")).toBeInTheDocument();
    expect(
      container.querySelector("#intake-market-competitors")?.getAttribute("aria-required"),
    ).toBeNull();
  });
});

describe("/intake page -- v2: a malformed optional field WARNS but never blocks", () => {
  it("an out-of-format wtp_band shows a warning and keeps actions enabled", () => {
    const { container } = render(<IntakePage />);
    fillRequired(container);
    fireEvent.change(container.querySelector("#intake-audience-wtp_band")!, {
      target: { value: "bem barato" },
    });
    expect(
      screen.getByText(/sem 2 numeros, o pricing fastpath usa uma faixa padrao/),
    ).toBeInTheDocument();
    const { download, resolve } = getButtons();
    expect(download).toBeEnabled();
    expect(resolve).toBeEnabled();
  });
});

describe("/intake page -- v2: localStorage draft (DP5)", () => {
  it("persists typed values to localStorage as the user types", () => {
    const { container } = render(<IntakePage />);
    fireEvent.change(container.querySelector("#intake-identity-brand_name")!, {
      target: { value: "Estufa Aurora" },
    });
    const raw = window.localStorage.getItem("cexai_intake_draft_v1");
    expect(raw).toBeTruthy();
    expect(raw).toContain("Estufa Aurora");
  });

  it("restores a draft from localStorage on a fresh mount", async () => {
    const first = render(<IntakePage />);
    fireEvent.change(
      first.container.querySelector("#intake-identity-brand_name")!,
      { target: { value: "Estufa Aurora" } },
    );
    first.unmount();

    render(<IntakePage />);
    await waitFor(() => {
      const input = screen.getByDisplayValue("Estufa Aurora");
      expect(input).toBeInTheDocument();
    });
    expect(screen.getByText(/Rascunho restaurado/)).toBeInTheDocument();
  });

  it("clears the draft after a successful download", () => {
    const { container } = render(<IntakePage />);
    fillRequired(container);
    expect(window.localStorage.getItem("cexai_intake_draft_v1")).toContain("Cafe Borealis");

    const { download } = getButtons();
    fireEvent.click(download);

    const raw = window.localStorage.getItem("cexai_intake_draft_v1");
    const parsed = raw ? (JSON.parse(raw) as { state: Record<string, string> }) : null;
    expect(parsed?.state?.["identity.brand_name"] ?? "").toBe("");
  });

  it("clears the draft after a successful DEV resolve (ok:true)", async () => {
    const fetchMock = vi.fn(async () => ({
      json: async () => ({ ok: true, summary: "[OK] resolved form_v1: 1 field(s)" }),
    }));
    vi.stubGlobal("fetch", fetchMock);

    const { container } = render(<IntakePage />);
    fillRequired(container);
    fireEvent.submit(container.querySelector("form")!);

    await waitFor(() => expect(screen.getByText("Resolvido")).toBeInTheDocument());
    const raw = window.localStorage.getItem("cexai_intake_draft_v1");
    const parsed = raw ? (JSON.parse(raw) as { state: Record<string, string> }) : null;
    expect(parsed?.state?.["identity.brand_name"] ?? "").toBe("");
  });

  it("'Descartar e comecar do zero' clears both the draft and the visible form", async () => {
    const first = render(<IntakePage />);
    fireEvent.change(
      first.container.querySelector("#intake-identity-brand_name")!,
      { target: { value: "Estufa Aurora" } },
    );
    first.unmount();

    const { container } = render(<IntakePage />);
    await waitFor(() => expect(screen.getByText(/Rascunho restaurado/)).toBeInTheDocument());

    fireEvent.click(screen.getByRole("button", { name: /Descartar e comecar do zero/ }));

    // the visible form resets immediately...
    expect(
      (container.querySelector("#intake-identity-brand_name") as HTMLInputElement).value,
    ).toBe("");
    // ...and the (now-empty) state the auto-save effect persists right back
    // carries NO leftover value either -- restoring it later would be a no-op,
    // functionally identical to "no draft".
    const raw = window.localStorage.getItem("cexai_intake_draft_v1");
    const parsed = raw ? (JSON.parse(raw) as { state: Record<string, string> }) : null;
    expect(parsed?.state?.["identity.brand_name"] ?? "").toBe("");
  });
});
