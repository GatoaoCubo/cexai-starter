"use client";

// ----------------------------------------------------------------------------
// StructuredResultView -- the GENERIC molded-result view. When a
// CapabilityResultView carries a ``mold_id`` (and a mold output, either inline or
// resolved from the MOLDS registry), this renders it as a STRUCTURED CARD -- the
// same readable shape as the two bespoke verticals, but driven entirely by the
// capability's mold (lib/molds.ts):
//
//   [governance row: score / gate / persisted]         <- the F7 verdict, mirrors ResultView
//   [report header: capability . kind . honesty chip]  <- real / copy pendente / simulado
//   [Input contract panel: ENTRADA]                    <- the typed I/O contract,
//       a table of campo / tipo / obrigatorio / exemplo (filled with examples)
//   [output_sections, one card each: SAIDA]            <- the structured OUTPUT mold:
//       layout=fields -> key/value rows . table -> a grid . list -> chips
//   [toggle: raw JSON]                                 <- the underlying mold object
//
// Reuses UniverseResultView's shell language (the outcome strip, SectionCard,
// chip/eyebrow utility classes, ScoreMeter) -- NO new design language.
//
// HONEST BY CONSTRUCTION (3-state, data-driven): a mock molde shows "dados simulados"; a
// real run shows "resultado real"; a real STRUCTURE whose copy is still SCAFFOLD (the
// creative lane fell back) shows "copy pendente" -- the marker-bearing sections render an
// honest "aguardando copy real" empty-state and EVERY cell is sanitized, so the internal
// scaffold marker NEVER reaches the operator (lib/molds.sectionHasPendingCopy / stripPendingMarker).
//
// PURE-READ + TOTAL: every field is optional; an absent section / row simply does
// not render (never throws). No credential is ever present (the result is a
// mock-mold projection).
// ----------------------------------------------------------------------------

import { useMemo, useState } from "react";
import type { CapabilityResultView } from "@/lib/types";
import type { CapabilityMold, MoldField, MoldSection } from "@/lib/molds";
import { moldFor, sectionHasPendingCopy, stripPendingMarker } from "@/lib/molds";
import { ScoreMeter } from "./ui";
import { AlertIcon, CheckIcon, ResearchIcon, TableIcon } from "./icons";

interface Props {
  result: CapabilityResultView;
  /**
   * The mold to render. The caller (ResultView.asMold) resolves it from the
   * result's ``mold_id`` via moldFor(); when it cannot, it passes whatever the
   * result carried so this view degrades to the raw JSON rather than throwing.
   */
  mold?: CapabilityMold;
}

// --- small pure helpers (mirror the Universe/Research view idioms) -----------

/**
 * Render a cell value as a short display string ('' for nullish). Every string leaf is
 * passed through stripPendingMarker -- the scaffold marker is an INTERNAL signal and must
 * never reach the operator, even in a cell the section-level empty-state did not replace
 * (defense-in-depth; a marker-free string is returned unchanged).
 */
function cellText(v: unknown): string {
  if (v === null || v === undefined) return "";
  if (typeof v === "boolean") return v ? "sim" : "nao";
  if (typeof v === "number") return Number.isFinite(v) ? String(v) : "";
  if (Array.isArray(v)) return v.map((x) => cellText(x)).filter(Boolean).join(", ");
  return stripPendingMarker(String(v));
}

/** Format a MoldField.example for the contract table's "exemplo" column. */
function exampleText(ex: MoldField["example"]): string {
  if (Array.isArray(ex)) return ex.map((x) => String(x)).join(", ");
  return cellText(ex);
}

/**
 * Build the validation/rigor descriptors a field carries (all optional, added
 * by the all-nuclei refine pass). Returns a short label list -- one chip per
 * present constraint, [] when the field has none (so no empty noise renders).
 * Every access is guarded: a mold without these fields yields an empty array.
 */
function validationChips(f: MoldField): string[] {
  const out: string[] = [];
  if (Array.isArray(f.enum_values) && f.enum_values.length > 0) {
    out.push(`um de: ${f.enum_values.map((v) => String(v)).join(", ")}`);
  }
  const hasMinLen = typeof f.min_len === "number";
  const hasMaxLen = typeof f.max_len === "number";
  if (hasMinLen && hasMaxLen) out.push(`len ${f.min_len}-${f.max_len}`);
  else if (hasMinLen) out.push(`len >= ${f.min_len}`);
  else if (hasMaxLen) out.push(`len <= ${f.max_len}`);
  const hasMin = typeof f.min === "number";
  const hasMax = typeof f.max === "number";
  if (hasMin && hasMax) out.push(`${f.min}-${f.max}`);
  else if (hasMin) out.push(`>= ${f.min}`);
  else if (hasMax) out.push(`<= ${f.max}`);
  if (typeof f.pattern === "string" && f.pattern.length > 0) {
    out.push(`pattern ${f.pattern}`);
  }
  if (f.default !== null && f.default !== undefined) {
    out.push(`default ${cellText(f.default)}`);
  }
  return out;
}

// --- the Input contract panel (the typed I/O contract, example-filled) -------

function InputContractPanel({ fields }: { fields: MoldField[] }) {
  if (!Array.isArray(fields) || fields.length === 0) return null;
  return (
    <div className="overflow-hidden rounded-card border border-line">
      <div className="grid grid-cols-[1.4fr_0.8fr_0.7fr_1.8fr] gap-4 border-b border-line bg-panel-sunken px-4 py-2 font-mono text-2xs uppercase tracking-wider text-text-faint">
        <span>Campo</span>
        <span>Tipo</span>
        <span>Obrigatorio</span>
        <span>Exemplo</span>
      </div>
      <div className="divide-y divide-line">
        {fields.map((f) => {
          const checks = validationChips(f);
          return (
          <div
            key={f.key}
            className="grid grid-cols-[1.4fr_0.8fr_0.7fr_1.8fr] items-baseline gap-4 bg-panel px-4 py-2.5"
          >
            <span className="min-w-0">
              <span className="font-display text-sm font-600 text-text">{f.label}</span>
              <span className="ml-1.5 font-mono text-2xs text-text-faint">{f.key}</span>
              {f.note && (
                <span className="mt-0.5 block font-mono text-2xs text-text-faint">{f.note}</span>
              )}
              {checks.length > 0 && (
                <span className="mt-1 flex flex-wrap gap-1">
                  {checks.map((c, ci) => (
                    <span key={`${f.key}-v-${ci}`} className="chip normal-case">
                      {c}
                    </span>
                  ))}
                </span>
              )}
            </span>
            <span className="font-mono text-2xs text-text-muted">{f.type}</span>
            <span>
              {f.required ? (
                <span className="inline-flex items-center gap-1 text-synapse">
                  <span className="h-1.5 w-1.5 rounded-full bg-synapse" />
                  <span className="font-mono text-2xs uppercase tracking-wider">sim</span>
                </span>
              ) : (
                <span className="font-mono text-2xs uppercase tracking-wider text-text-faint">
                  nao
                </span>
              )}
            </span>
            <span className="min-w-0 break-words text-sm text-text">{exampleText(f.example)}</span>
          </div>
          );
        })}
      </div>
    </div>
  );
}

// --- honest empty-state for a section whose copy is still scaffold -----------
//
// Shown in place of a section's body when its copy has not been really generated yet
// (sectionHasPendingCopy). The typed SHAPE is real and stays framed; only the copy is
// pending -- so the operator sees an honest "aguardando copy real" instead of an internal
// marker. When a real run lands clean copy, this never triggers (the real hooks render).
function PendingCopyState() {
  return (
    <div className="flex items-start gap-2 rounded-card border border-dashed border-line bg-panel-sunken px-4 py-4 text-sm text-text-muted">
      <span className="mt-0.5 shrink-0 text-signal">
        <AlertIcon />
      </span>
      <span>
        <span className="font-display font-600 text-text">Aguardando copy real</span>
        {" -- "}a copy deste anuncio ainda nao foi gerada. A forma tipada esta pronta; as
        variantes reais aparecem aqui assim que a geracao com IA conectada rodar.
      </span>
    </div>
  );
}

// --- one OUTPUT section card (rendered per its layout) -----------------------

function OutputSectionCard({ section }: { section: MoldSection }) {
  // A section whose copy is still the scaffold placeholder renders the honest empty-state
  // instead of its (marker-bearing) body -- the rule is data-driven (presence of real copy).
  const pending = sectionHasPendingCopy(section);
  return (
    <div className="rounded-card border border-line bg-panel px-4 py-4">
      <div className="mb-3 flex items-center justify-between gap-3">
        <p className="eyebrow normal-case text-text-muted">{section.title}</p>
        <span className="flex items-center gap-2">
          {pending && (
            <span className="chip border-signal/30 text-signal">copy pendente</span>
          )}
          {section.contract_version && (
            <span className="chip">v{section.contract_version}</span>
          )}
          <span className="font-mono text-2xs uppercase tracking-wider text-text-faint">
            {section.layout}
          </span>
        </span>
      </div>
      {section.note && !pending && (
        <p className="mb-3 text-sm text-text-muted">{section.note}</p>
      )}
      {pending ? <PendingCopyState /> : <SectionBody section={section} />}
    </div>
  );
}

function SectionBody({ section }: { section: MoldSection }) {
  if (section.layout === "table") {
    const columns = section.columns ?? [];
    const rows = section.table ?? [];
    if (columns.length === 0 || rows.length === 0) {
      return <p className="text-sm text-text-muted">Sem dados nesta secao.</p>;
    }
    const colTypes = Array.isArray(section.column_types) ? section.column_types : [];
    const grid = { gridTemplateColumns: `repeat(${columns.length}, minmax(0, 1fr))` };
    return (
      <div className="overflow-x-auto">
        <div className="min-w-full overflow-hidden rounded-lg border border-line">
          <div
            className="grid gap-3 border-b border-line bg-panel-sunken px-3 py-2 font-mono text-2xs uppercase tracking-wider text-text-faint"
            style={grid}
          >
            {columns.map((c, i) => {
              const ct = colTypes[i];
              return (
                <span key={`h-${i}`} className={i === 0 ? "" : "text-right"}>
                  {c}
                  {typeof ct === "string" && ct.length > 0 && (
                    <span className="ml-1 lowercase text-text-faint/70">: {ct}</span>
                  )}
                </span>
              );
            })}
          </div>
          <div className="divide-y divide-line">
            {rows.map((row, ri) => (
              <div key={`r-${ri}`} className="grid gap-3 bg-panel px-3 py-2" style={grid}>
                {columns.map((_, ci) => {
                  const v = row[ci];
                  const isFirst = ci === 0;
                  return (
                    <span
                      key={`c-${ri}-${ci}`}
                      className={[
                        "min-w-0 break-words text-sm",
                        isFirst ? "font-600 text-text" : "text-right font-mono text-text-muted",
                      ].join(" ")}
                    >
                      {cellText(v)}
                    </span>
                  );
                })}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (section.layout === "list") {
    const items = (section.items ?? []).filter((s) => typeof s === "string" && s.length > 0);
    if (items.length === 0) {
      return <p className="text-sm text-text-muted">Sem itens nesta secao.</p>;
    }
    return (
      <div className="flex flex-wrap gap-1.5">
        {items.map((it, i) => (
          <span key={`${it}-${i}`} className="chip normal-case">
            {stripPendingMarker(it)}
          </span>
        ))}
      </div>
    );
  }

  // layout === "fields"
  const rows = (section.rows ?? []).filter((r) => r && r.label);
  if (rows.length === 0) {
    return <p className="text-sm text-text-muted">Sem campos nesta secao.</p>;
  }
  return (
    <div className="space-y-2.5">
      {rows.map((r, i) => (
        <div key={`${r.label}-${i}`} className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
          <span className="font-mono text-2xs uppercase tracking-wider text-text-faint">
            {r.label}
          </span>
          <span className="text-sm text-text">{cellText(r.value)}</span>
        </div>
      ))}
    </div>
  );
}

// ----------------------------------------------------------------------------

export function StructuredResultView({ result, mold }: Props) {
  const [view, setView] = useState<"report" | "raw">("report");
  const [copied, setCopied] = useState(false);

  // Resolve the mold: prefer the one the caller passed, else look it up by id.
  const moldId =
    result.mold_id ??
    (result.structured && typeof result.structured === "object"
      ? (result.structured as { mold_id?: string }).mold_id
      : undefined);
  const resolved = mold ?? (moldId ? moldFor(moldId) : undefined);

  // The raw JSON we surface in the "raw" toggle: the structured slot if present,
  // else a compact echo of the contract + sections we rendered.
  const rawJson = useMemo(() => {
    const payload =
      result.structured && typeof result.structured === "object"
        ? result.structured
        : {
            mold_id: moldId,
            input_example: result.input_example,
            output_sections: resolved?.output_sections,
          };
    try {
      return JSON.stringify(payload, null, 2);
    } catch {
      return "";
    }
  }, [result.structured, result.input_example, moldId, resolved]);

  async function copyRaw() {
    try {
      await navigator.clipboard.writeText(rawJson);
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      /* clipboard blocked -- ignore */
    }
  }

  // MOLDED-REAL seam (mission MOLDED_REAL_SEAM): a real generator attaches REAL
  // ``output_sections`` on ``structured`` (the SAME MoldSection shape as the mock). Prefer
  // those over the mold's static example; ``real === true`` additionally drops the "dados
  // simulados" chip + switches the banner to a "resultado real" affordance. Degrade-never +
  // TOTAL: an absent/old structured payload -> today's mock behavior, byte-identical.
  const structuredObj =
    result.structured && typeof result.structured === "object"
      ? (result.structured as { output_sections?: MoldSection[]; real?: boolean })
      : undefined;
  const realSections =
    structuredObj && Array.isArray(structuredObj.output_sections)
      ? structuredObj.output_sections
      : undefined;

  // Prefer the REAL sections when present; otherwise fall back to the mold's mock example.
  const sections =
    realSections && realSections.length > 0
      ? realSections
      : resolved?.output_sections ?? [];

  // HONESTY GUARD: a result can carry ``real: true`` yet still hold SCAFFOLD copy (the
  // creative lane fell back -- e.g. ads with no LLM credential). The copy is NOT real, so
  // the result is NOT "resultado real": demote it to the honest "copy pendente" framing.
  // Driven by the data (presence of the scaffold marker in any section), not the flag alone.
  const anyPendingCopy = sections.some(sectionHasPendingCopy);
  const isReal =
    structuredObj?.real === true &&
    !!realSections &&
    realSections.length > 0 &&
    !anyPendingCopy;

  return (
    <div className="animate-fade-in space-y-4">
      {/* ---- governance row: the F7 verdict travelling WITH the typed package ---- */}
      <div className="space-y-2">
      <p className="eyebrow">// governanca</p>
      <div className="flex flex-wrap items-center gap-x-6 gap-y-3 rounded-lg border border-line bg-panel-sunken px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="font-mono text-2xs uppercase tracking-wider text-text-faint">
            Score
          </span>
          <ScoreMeter score={result.score} />
        </div>
        <div className="flex items-center gap-2">
          <span className="font-mono text-2xs uppercase tracking-wider text-text-faint">
            Gate
          </span>
          {result.passed ? (
            <span className="inline-flex items-center gap-1 text-synapse">
              <CheckIcon /> <span className="text-sm">passed</span>
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-danger">
              <AlertIcon /> <span className="text-sm">below floor</span>
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <span className="font-mono text-2xs uppercase tracking-wider text-text-faint">
            Persisted
          </span>
          <span className="text-sm text-text">
            {result.persisted ? (
              <span className="inline-flex items-center gap-1.5">
                <span className="h-1.5 w-1.5 rounded-full bg-synapse" />
                tenant data plane
              </span>
            ) : (
              <span className="text-text-muted">not stored</span>
            )}
          </span>
        </div>
      </div>
      </div>

      {/* ---- report header + view toggle -------------------------------- */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2 font-mono text-2xs text-text-faint">
          <span className="text-synapse">
            <ResearchIcon width={16} height={16} />
          </span>
          <span className="text-text">{result.capability}</span>
          <span className="chip">kind={result.kind}</span>
          {resolved?.contract_version && (
            <span className="chip">contrato v{resolved.contract_version}</span>
          )}
          {/* honest 3-state: a real run shows "resultado real"; a real STRUCTURE whose copy
              is still scaffold shows "copy pendente"; a pure mock shows "dados simulados". */}
          {isReal ? (
            <span className="chip border-synapse/30 text-synapse">resultado real</span>
          ) : anyPendingCopy ? (
            <span className="chip border-signal/30 text-signal">copy pendente</span>
          ) : (
            <span className="chip border-danger/30 text-danger">dados simulados</span>
          )}
        </div>
        <div className="inline-flex overflow-hidden rounded-pill border border-line">
          <button
            onClick={() => setView("report")}
            className={[
              "px-3 py-1 font-mono text-2xs uppercase tracking-wider transition-colors",
              view === "report"
                ? "bg-synapse/10 text-synapse"
                : "bg-panel-sunken text-text-muted hover:text-text",
            ].join(" ")}
          >
            molde
          </button>
          <button
            onClick={() => setView("raw")}
            className={[
              "border-l border-line px-3 py-1 font-mono text-2xs uppercase tracking-wider transition-colors",
              view === "raw"
                ? "bg-synapse/10 text-synapse"
                : "bg-panel-sunken text-text-muted hover:text-text",
            ].join(" ")}
          >
            json
          </button>
        </div>
      </div>

      {/* ---- notice banner: honest 3-state -- real result / real structure with copy
           still pending / a pure mock molde. The caption below frames the differentiator:
           a TYPED + GOVERNED I/O package, not a raw LLM dump. */}
      {isReal ? (
        <div className="rounded-lg border border-synapse/40 bg-synapse/[0.07] px-4 py-3">
          <div className="flex items-start gap-3">
            <span className="mt-0.5 shrink-0 text-synapse">
              <CheckIcon />
            </span>
            <div>
              <p className="font-display text-sm font-600 text-synapse">
                Resultado real (contrato de I/O)
              </p>
              <p className="font-mono text-2xs text-text-faint">
                {resolved?.summary ??
                  "A forma tipada da capacidade -- dados reais conforme o contrato."}
              </p>
            </div>
          </div>
        </div>
      ) : anyPendingCopy ? (
        <div className="rounded-lg border border-signal/40 bg-signal/[0.07] px-4 py-3">
          <div className="flex items-start gap-3">
            <span className="mt-0.5 shrink-0 text-signal">
              <AlertIcon />
            </span>
            <div>
              <p className="font-display text-sm font-600 text-signal">
                Contrato tipado pronto -- copy real pendente
              </p>
              <p className="font-mono text-2xs text-text-faint">
                A estrutura tipada e governada esta pronta; a copy real do anuncio e gerada
                quando a IA conectada rodar. As secoes pendentes mostram o estado honesto --
                sem marcadores internos.
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className="rounded-lg border border-signal/40 bg-signal/[0.07] px-4 py-3">
          <div className="flex items-start gap-3">
            <span className="mt-0.5 shrink-0 text-signal">
              <AlertIcon />
            </span>
            <div>
              <p className="font-display text-sm font-600 text-signal">
                Molde de capacidade (contrato de I/O)
              </p>
              <p className="font-mono text-2xs text-text-faint">
                {resolved?.summary ??
                  "A forma tipada da capacidade -- exemplo simulado, ainda nao um resultado real."}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* the differentiator, stated plainly: 1 typed input contract -> N typed output
          sections, carried WITH its governance (score / gate / persistencia). */}
      <p className="font-mono text-2xs leading-relaxed text-text-faint">
        Pacote tipado + governado: 1 contrato de entrada
        {resolved ? ` (${resolved.input_contract.length} campos)` : ""} {"->"}{" "}
        {sections.length} {sections.length === 1 ? "secao" : "secoes"} de saida tipadas,
        com score / gate / persistencia. Nao e um dump de LLM.
      </p>

      {view === "report" ? (
        <div className="space-y-4">
          {/* ---- Input contract (the typed ENTRADA half of the I/O contract) -- */}
          <div className="space-y-2">
            <p className="eyebrow">
              // entrada -- contrato tipado
              {resolved ? ` (${resolved.input_contract.length})` : ""}
            </p>
            {resolved ? (
              <InputContractPanel fields={resolved.input_contract} />
            ) : (
              <p className="text-sm text-text-muted">
                Contrato de entrada indisponivel para este molde.
              </p>
            )}
          </div>

          {/* ---- structured output (the typed SAIDA half: one card per section) -- */}
          <div className="space-y-2">
            <p className="eyebrow">
              // saida -- {sections.length}{" "}
              {sections.length === 1 ? "secao tipada" : "secoes tipadas"}
            </p>
            {sections.length > 0 ? (
              <div className="grid grid-cols-1 gap-3">
                {sections.map((s, i) => (
                  <OutputSectionCard key={`${s.title}-${i}`} section={s} />
                ))}
              </div>
            ) : (
              <div className="flex items-start gap-2 rounded-card border border-line bg-panel px-4 py-4 text-sm text-text-muted">
                <span className="mt-0.5 shrink-0 text-text-faint">
                  <TableIcon />
                </span>
                <span>Saida estruturada indisponivel para este molde.</span>
              </div>
            )}
          </div>
        </div>
      ) : (
        // ---- raw JSON (the underlying mold object) ----------------------
        <div className="overflow-hidden rounded-lg border border-line">
          <div className="flex items-center justify-between border-b border-line bg-panel-sunken px-4 py-2">
            <span className="font-mono text-2xs uppercase tracking-wider text-text-muted">
              mold (json)
            </span>
            <button
              onClick={copyRaw}
              disabled={!rawJson}
              className="font-mono text-2xs uppercase tracking-wider text-text-muted transition-colors hover:text-synapse disabled:opacity-40"
            >
              {copied ? "copied" : "copy"}
            </button>
          </div>
          <pre className="max-h-[42vh] overflow-auto bg-ink-800 px-4 py-4 font-mono text-xs leading-relaxed text-text-muted">
            {rawJson || "// mold object unavailable"}
          </pre>
        </div>
      )}

      {/* ---- identity line + errors (mirrors ResultView) ----------------- */}
      <div className="flex flex-wrap items-center gap-2 font-mono text-2xs text-text-faint">
        <span className="chip">{result.nucleus}</span>
        <span>kind={result.kind}</span>
        <span>pillar={result.pillar}</span>
        {moldId && <span>mold={moldId}</span>}
        {result.record_id && <span>record={result.record_id}</span>}
      </div>

      {result.errors && result.errors.length > 0 && (
        <ul className="space-y-1 text-sm text-danger">
          {result.errors.map((e, i) => (
            <li key={i} className="flex items-start gap-2">
              <span className="mt-0.5">
                <AlertIcon />
              </span>
              {e}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
