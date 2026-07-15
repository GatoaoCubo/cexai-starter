// ----------------------------------------------------------------------------
// StructuredSections -- the READ-ONLY typed renderer for a published payload's
// MoldSection[] body. EXTRACTED from apps/dashboard_web/components/
// StructuredResultView (SectionBody + OutputSectionCard + the cell helpers),
// stripped to the public surface: NO governance row, NO view toggle, NO mock-mold
// resolution -- it renders ONLY the sections it is GIVEN (a published asset's own).
//
// Renders STRICTLY from the typed contract (never dangerouslySetInnerHTML). The
// honest pending-copy rule is preserved verbatim: a section whose copy is still the
// internal scaffold marker renders an "aguardando copy real" empty-state, and every
// leaf cell is sanitized (stripPendingMarker) so the marker can never reach a public
// visitor.
//
// PURE-READ + TOTAL: every field is optional; an absent section / row simply does
// not render (never throws). ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import type { MoldSection } from "@/lib/molds";
import { sectionHasPendingCopy, stripPendingMarker } from "@/lib/molds";
import { AlertIcon } from "./icons";

/** Render a cell value as a short display string ('' for nullish). Every string
 *  leaf passes through stripPendingMarker -- the scaffold marker is INTERNAL and
 *  must never reach a visitor (defense-in-depth; a marker-free string is unchanged). */
function cellText(v: unknown): string {
  if (v === null || v === undefined) return "";
  if (typeof v === "boolean") return v ? "sim" : "nao";
  if (typeof v === "number") return Number.isFinite(v) ? String(v) : "";
  if (Array.isArray(v)) return v.map((x) => cellText(x)).filter(Boolean).join(", ");
  return stripPendingMarker(String(v));
}

/** The honest empty-state shown in place of a section whose copy is still scaffold. */
function PendingCopyState() {
  return (
    <div className="flex items-start gap-2 rounded-card border border-dashed border-border bg-secondary px-4 py-4 text-sm text-muted-foreground">
      <span className="mt-0.5 shrink-0 text-highlight">
        <AlertIcon />
      </span>
      <span>
        <span className="font-display font-semibold text-foreground">Aguardando conteudo</span>
        {" -- "}esta secao ainda nao tem conteudo final publicado.
      </span>
    </div>
  );
}

function SectionBody({ section }: { section: MoldSection }) {
  if (section.layout === "table") {
    const columns = section.columns ?? [];
    const rows = section.table ?? [];
    if (columns.length === 0 || rows.length === 0) {
      return <p className="text-sm text-muted-foreground">Sem dados nesta secao.</p>;
    }
    const colTypes = Array.isArray(section.column_types) ? section.column_types : [];
    const grid = { gridTemplateColumns: `repeat(${columns.length}, minmax(0, 1fr))` };
    return (
      <div className="overflow-x-auto">
        <div className="min-w-full overflow-hidden rounded-lg border border-border">
          <div
            className="grid gap-3 border-b border-border bg-secondary px-3 py-2 text-2xs font-medium uppercase tracking-wide text-muted-foreground"
            style={grid}
          >
            {columns.map((c, i) => {
              const ct = colTypes[i];
              return (
                <span key={`h-${i}`} className={i === 0 ? "" : "text-right"}>
                  {c}
                  {typeof ct === "string" && ct.length > 0 && (
                    <span className="ml-1 lowercase text-muted-foreground/70">: {ct}</span>
                  )}
                </span>
              );
            })}
          </div>
          <div className="divide-y divide-line">
            {rows.map((row, ri) => (
              <div key={`r-${ri}`} className="grid gap-3 bg-card px-3 py-2" style={grid}>
                {columns.map((_, ci) => {
                  const v = row[ci];
                  const isFirst = ci === 0;
                  return (
                    <span
                      key={`c-${ri}-${ci}`}
                      className={[
                        "min-w-0 break-words text-sm",
                        isFirst ? "font-semibold text-foreground" : "text-right font-mono text-muted-foreground",
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
      return <p className="text-sm text-muted-foreground">Sem itens nesta secao.</p>;
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
    return <p className="text-sm text-muted-foreground">Sem campos nesta secao.</p>;
  }
  return (
    <div className="space-y-2.5">
      {rows.map((r, i) => (
        <div key={`${r.label}-${i}`} className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
          <span className="text-2xs font-medium uppercase tracking-wide text-muted-foreground">
            {r.label}
          </span>
          <span className="text-sm text-foreground">{cellText(r.value)}</span>
        </div>
      ))}
    </div>
  );
}

function OutputSectionCard({ section }: { section: MoldSection }) {
  const pending = sectionHasPendingCopy(section);
  return (
    <div className="rounded-card border border-border bg-card px-4 py-4">
      <div className="mb-3 flex items-center justify-between gap-3">
        <p className="eyebrow normal-case text-muted-foreground">{section.title}</p>
        <span className="flex items-center gap-2">
          {pending && (
            <span className="chip border-highlight/30 text-highlight">conteudo pendente</span>
          )}
          {section.contract_version && (
            <span className="chip">v{section.contract_version}</span>
          )}
          <span className="text-2xs font-medium uppercase tracking-wide text-muted-foreground">
            {section.layout}
          </span>
        </span>
      </div>
      {section.note && !pending && (
        <p className="mb-3 text-sm text-muted-foreground">{section.note}</p>
      )}
      {pending ? <PendingCopyState /> : <SectionBody section={section} />}
    </div>
  );
}

/**
 * Render a list of typed sections (a published asset's structured body). Returns
 * null when there are none -> the caller decides the empty surface. PURE-READ.
 */
export function StructuredSections({ sections }: { sections?: MoldSection[] }) {
  const list = Array.isArray(sections) ? sections : [];
  if (list.length === 0) return null;
  return (
    <div className="grid grid-cols-1 gap-3">
      {list.map((s, i) => (
        <OutputSectionCard key={`${s.title}-${i}`} section={s} />
      ))}
    </div>
  );
}
