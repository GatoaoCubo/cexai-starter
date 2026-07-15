"use client";

// ----------------------------------------------------------------------------
// UniverseResultView -- the RICH report view for the research-universe vertical
// (capability "research_universe"). When a CapabilityResultView carries the typed
// multi-source orchestrator report (CapabilityResultView.structured, discriminated
// by seed_type + endpoint_status), this renders it as a READABLE REPORT instead of
// raw MD:
//
//   [outcome strip: score / gate / persisted]            <- mirrors ResultView
//   [report header: seed . seed_type . fetched_at]        <- what was researched
//   [per-source STATUS row]                               <- endpoint_status -> chips
//                                                            (ok=green / blocked|skipped=amber / failed=red)
//   [SECTION CARDS, one per non-null section]             <- identity/market/reputation/
//                                                            social/keywords/questions/sentiment
//     each card: its real data (defensively rendered) + per-lane provenance,
//     OR an honest "not run / blocked" state (NEVER fabricated)
//   [toggle: structured report  <->  raw MD/HTML]         <- ?render_format projection
//
// Reuses ResultView/ResearchResultView's shell language + the chip/panel/eyebrow
// utility classes + ScoreMeter. The raw toggle prefers the projection the backend
// already attached (result.render) or an on-demand ?render_format fetch (onFetchRender),
// and is honest when neither is available.
//
// PURE-READ + TOTAL: every field is optional; a section that is null/absent renders as
// honestly "not run / blocked" (never throws on absent data -- mirrors the orchestrator's
// honest-null skeleton). mock is ALWAYS false; tenant_id is provenance only; no credential
// is ever present (the orchestrator emits a pure data dict).
// ----------------------------------------------------------------------------

import { useState } from "react";
import type {
  CapabilityResultView,
  DataSourcesMap,
  ResearchUniverseReport,
  SentimentSummary,
  UniverseSection,
  UniverseSections,
} from "@/lib/types";
import { RESEARCH_UNIVERSE_INPUT_CONTRACT, type MoldField } from "@/lib/molds";
import { ScoreMeter } from "./ui";
import { AlertIcon, CheckIcon, ResearchIcon } from "./icons";

interface Props {
  result: CapabilityResultView;
  /** the typed universe report (caller has already confirmed it is present). */
  report: ResearchUniverseReport;
  /**
   * Optional: fetch a raw projection on demand (consumes the backend ?render_format
   * path). Given "md" | "html" it resolves the render_universe string. When absent,
   * the raw toggle falls back to result.render (the projection the backend attached
   * when the run was requested with render_format), then to an honest "not available".
   */
  onFetchRender?: (format: "md" | "html") => Promise<string>;
}

// --- status -> tone (prefix-match the endpoint_status string) ----------------
//
// The orchestrator's status STARTS WITH one of: ok | blocked | skipped | failed
// (often "blocked: <reason>"). We prefix-match to the token palette:
//   ok -> synapse (green) . blocked|skipped -> signal (amber) . failed -> danger (red).

type StatusTone = "ok" | "warn" | "fail" | "unknown";

function statusTone(status: string | undefined): StatusTone {
  const s = (status || "").trim().toLowerCase();
  if (s.startsWith("ok")) return "ok";
  if (s.startsWith("blocked") || s.startsWith("skipped")) return "warn";
  if (s.startsWith("failed")) return "fail";
  return "unknown";
}

const TONE_CHIP: Record<StatusTone, string> = {
  ok: "border-synapse/40 bg-synapse/10 text-synapse",
  warn: "border-signal/40 bg-signal/10 text-signal",
  fail: "border-danger/40 bg-danger/10 text-danger",
  unknown: "border-line text-text-muted",
};

const TONE_DOT: Record<StatusTone, string> = {
  ok: "bg-synapse",
  warn: "bg-signal",
  fail: "bg-danger",
  unknown: "bg-text-faint",
};

// --- small pure helpers ------------------------------------------------------

/** "reclame_aqui" / "seo-keywords" -> "Reclame Aqui". Humanize a lane/field key. */
function humanize(key: string): string {
  return key
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase())
    .trim();
}

function isPlainObject(v: unknown): v is Record<string, unknown> {
  return Boolean(v) && typeof v === "object" && !Array.isArray(v);
}

/** A section is "present" when it is a non-empty object (null/{}/[] => not run). */
function sectionPresent(value: UniverseSection): value is Record<string, unknown> {
  return isPlainObject(value) && Object.keys(value).length > 0;
}

/** Render a scalar primitive as a short string; '' for non-scalars. */
function scalarText(v: unknown): string {
  if (v === null || v === undefined) return "";
  if (typeof v === "string") return v;
  if (typeof v === "number") return Number.isFinite(v) ? String(v) : "";
  if (typeof v === "boolean") return v ? "sim" : "nao";
  return "";
}

/** Status keys we surface as the per-source chips / honest-empty notes. */
function nonEmptyStatuses(
  endpointStatus: ResearchUniverseReport["endpoint_status"],
): [string, string][] {
  if (!isPlainObject(endpointStatus)) return [];
  return Object.entries(endpointStatus)
    .filter(([, v]) => typeof v === "string" && v.trim().length > 0)
    .map(([k, v]) => [k, String(v)] as [string, string]);
}

// --- provenance badges (per-lane data_sources) -------------------------------

function ProvenanceLine({
  sources,
}: {
  sources: string[] | null | undefined;
}) {
  if (!Array.isArray(sources) || sources.length === 0) return null;
  return (
    <div className="mt-3 flex flex-wrap items-center gap-1.5">
      <span className="font-mono text-2xs uppercase tracking-wider text-text-faint">
        fonte
      </span>
      {sources.map((src, i) => (
        <span
          key={`${src}-${i}`}
          className="inline-flex items-center rounded-pill border border-line bg-panel-sunken px-2.5 py-1 font-mono text-2xs text-text-muted"
        >
          {src}
        </span>
      ))}
    </div>
  );
}

// --- a defensive, generic field renderer for a heterogeneous lane payload ----
//
// Each lane returns its OWN nested shape, so we render its fields generically and
// HONESTLY (real data only): scalars as label/value rows, string-arrays as chips,
// nested objects as compact key/value badges. We never invent fields -- only what the
// lane actually returned is shown. Internal hooks (e.g. each item's "sentiment") and
// echoed control keys are skipped to keep the card readable.

const SKIP_KEYS = new Set([
  "endpoint_status",
  "data_sources",
  "mock",
  "sentiment", // per-item enrichment hook (rolled up in sentiment_summary)
]);

function FieldRows({ data }: { data: Record<string, unknown> }) {
  const entries = Object.entries(data).filter(([k, v]) => {
    if (SKIP_KEYS.has(k)) return false;
    if (v === null || v === undefined) return false;
    if (Array.isArray(v) && v.length === 0) return false;
    if (isPlainObject(v) && Object.keys(v).length === 0) return false;
    return true;
  });

  if (entries.length === 0) {
    return (
      <p className="text-sm text-text-muted">
        Sem campos legiveis nesta secao.
      </p>
    );
  }

  return (
    <div className="space-y-2.5">
      {entries.map(([key, value]) => (
        <FieldRow key={key} label={humanize(key)} value={value} />
      ))}
    </div>
  );
}

function FieldRow({ label, value }: { label: string; value: unknown }) {
  // string[] -> chips
  if (Array.isArray(value)) {
    const items = value
      .map((v) => (isPlainObject(v) ? JSON.stringify(v) : scalarText(v)))
      .filter((s) => s.length > 0)
      .slice(0, 24);
    if (items.length === 0) return null;
    return (
      <div>
        <p className="mb-1.5 font-mono text-2xs uppercase tracking-wider text-text-faint">
          {label}
          <span className="ml-1.5 normal-case text-text-faint/70">
            ({value.length})
          </span>
        </p>
        <div className="flex flex-wrap gap-1.5">
          {items.map((it, i) => (
            <span key={`${it}-${i}`} className="chip normal-case">
              {it}
            </span>
          ))}
        </div>
      </div>
    );
  }

  // nested object -> compact key/value badges
  if (isPlainObject(value)) {
    const pairs = Object.entries(value)
      .map(([k, v]) => [k, scalarText(v)] as [string, string])
      .filter(([, v]) => v.length > 0)
      .slice(0, 12);
    if (pairs.length === 0) return null;
    return (
      <div>
        <p className="mb-1.5 font-mono text-2xs uppercase tracking-wider text-text-faint">
          {label}
        </p>
        <div className="flex flex-wrap gap-1.5">
          {pairs.map(([k, v]) => (
            <span
              key={k}
              className="inline-flex items-center gap-1.5 rounded-pill border border-line bg-panel-sunken px-2.5 py-1 font-mono text-2xs text-text-muted"
            >
              <span className="text-text-faint">{humanize(k)}</span>
              <span className="text-text">{v}</span>
            </span>
          ))}
        </div>
      </div>
    );
  }

  // scalar -> label / value row
  const text = scalarText(value);
  if (!text) return null;
  return (
    <div className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
      <span className="font-mono text-2xs uppercase tracking-wider text-text-faint">
        {label}
      </span>
      <span className="text-sm text-text">{text}</span>
    </div>
  );
}

// --- one SECTION CARD --------------------------------------------------------
//
// Present section -> its real data + provenance. Null/absent -> honest "not run /
// blocked", carrying the lane's endpoint_status reason when there is one.

function SectionCard({
  title,
  lane,
  value,
  status,
  sources,
  children,
}: {
  title: string;
  /** the lane key (for the status/provenance lookup label). */
  lane: string;
  value: UniverseSection;
  status?: string;
  sources?: string[] | null;
  /** optional custom body (e.g. the sentiment card); defaults to FieldRows. */
  children?: React.ReactNode;
}) {
  const present = sectionPresent(value) || Boolean(children);
  const tone = statusTone(status);

  return (
    <div className="rounded-card border border-line bg-panel px-4 py-4">
      <div className="mb-3 flex items-center justify-between gap-3">
        <p className="eyebrow normal-case text-text-muted">{title}</p>
        {status && (
          <span
            className={`inline-flex items-center gap-1.5 rounded-pill border px-2.5 py-1 font-mono text-2xs uppercase tracking-wider ${TONE_CHIP[tone]}`}
          >
            <span className={`h-1.5 w-1.5 rounded-full ${TONE_DOT[tone]}`} />
            {status}
          </span>
        )}
      </div>

      {present ? (
        <>
          {children ?? (
            <FieldRows data={value as Record<string, unknown>} />
          )}
          <ProvenanceLine sources={sources} />
        </>
      ) : (
        <div className="flex items-start gap-2 text-sm text-text-muted">
          <span className="mt-0.5 shrink-0 text-text-faint">
            <AlertIcon />
          </span>
          <span>
            {tone === "warn" || tone === "fail"
              ? `${humanize(lane)} nao retornou dados (${status}).`
              : "Esta fonte nao foi executada para este seed."}
          </span>
        </div>
      )}
    </div>
  );
}

// --- the sentiment card (the one typed section) ------------------------------

function SentimentCard({
  summary,
  status,
  sources,
}: {
  summary: SentimentSummary | null | undefined;
  status?: string;
  sources?: string[] | null;
}) {
  const analyzed =
    typeof summary?.analyzed === "number" ? summary.analyzed : 0;
  const present = Boolean(summary) && analyzed > 0;
  const label = (summary?.label || "NEU").toUpperCase();
  const labelTone =
    label === "POS" ? "ok" : label === "NEG" ? "fail" : "warn";

  return (
    <SectionCard
      title="Sentimento (agregado)"
      lane="sentiment"
      value={present ? (summary as Record<string, unknown>) : null}
      status={status}
      sources={sources ?? summary?.data_sources ?? null}
    >
      {present ? (
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={`inline-flex items-center gap-1.5 rounded-pill border px-2.5 py-1 font-mono text-2xs uppercase tracking-wider ${TONE_CHIP[labelTone]}`}
            >
              <span className={`h-1.5 w-1.5 rounded-full ${TONE_DOT[labelTone]}`} />
              {label}
            </span>
            <span className="font-mono text-2xs text-text-faint">
              {analyzed} {analyzed === 1 ? "texto" : "textos"} analisados
              {summary?.method ? ` . ${summary.method}` : ""}
            </span>
          </div>
          <div className="grid grid-cols-3 overflow-hidden rounded-lg border border-line">
            {[
              { k: "pos", label: "positivo", tone: "text-synapse", v: summary?.pos },
              { k: "neu", label: "neutro", tone: "text-text", v: summary?.neu },
              { k: "neg", label: "negativo", tone: "text-danger", v: summary?.neg },
            ].map((c, i) => (
              <div
                key={c.k}
                className={`bg-panel-sunken px-3 py-2.5 ${i < 2 ? "border-r border-line" : ""}`}
              >
                <b className={`block font-display text-lg font-600 leading-none ${c.tone}`}>
                  {typeof c.v === "number" ? c.v : "--"}
                </b>
                <span className="mt-1 block font-mono text-2xs uppercase tracking-wider text-text-muted">
                  {c.label}
                </span>
              </div>
            ))}
          </div>
        </div>
      ) : (
        // honest empty aggregate (analyzed=0 -> nothing to summarize, not a fabricated polarity)
        <p className="text-sm text-text-muted">
          Nenhum texto analisado -- sem polaridade a reportar.
          {summary?.note ? ` (${summary.note})` : ""}
        </p>
      )}
    </SectionCard>
  );
}

// --- the Input contract panel (the typed I/O contract, example-filled) -------
//
// Mirrors StructuredResultView's InputContractPanel idiom verbatim (same grid
// columns + chip/table tokens) so the bespoke vertical declares its typed INPUT
// the same way the 14 molded cards do. Source = RESEARCH_UNIVERSE_INPUT_CONTRACT
// (lib/molds.ts). Compact: campo / tipo / obrigatorio / exemplo.

function exampleText(ex: MoldField["example"]): string {
  if (Array.isArray(ex)) return ex.map((x) => String(x)).join(", ");
  if (ex === null || ex === undefined) return "";
  if (typeof ex === "boolean") return ex ? "sim" : "nao";
  return String(ex);
}

function InputContractPanel({ fields }: { fields: MoldField[] }) {
  if (!Array.isArray(fields) || fields.length === 0) return null;
  return (
    <div className="space-y-2">
      <p className="eyebrow">// contrato de input</p>
      <div className="overflow-hidden rounded-card border border-line">
        <div className="grid grid-cols-[1.4fr_0.8fr_0.7fr_1.8fr] gap-4 border-b border-line bg-panel-sunken px-4 py-2 font-mono text-2xs uppercase tracking-wider text-text-faint">
          <span>Campo</span>
          <span>Tipo</span>
          <span>Obrigatorio</span>
          <span>Exemplo</span>
        </div>
        <div className="divide-y divide-line">
          {fields.map((f) => (
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
          ))}
        </div>
      </div>
    </div>
  );
}

// ----------------------------------------------------------------------------

export function UniverseResultView({ result, report, onFetchRender }: Props) {
  const [view, setView] = useState<"report" | "raw">("report");
  const [rawFormat, setRawFormat] = useState<"md" | "html">("md");
  const [raw, setRaw] = useState<Record<"md" | "html", string | null>>({
    md: null,
    html: null,
  });
  const [rawLoading, setRawLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const sections: UniverseSections = report.sections ?? {};
  const endpointStatus = report.endpoint_status ?? {};
  const dataSources: DataSourcesMap = report.data_sources ?? {};
  const statuses = nonEmptyStatuses(endpointStatus);

  const okCount = statuses.filter(([, v]) => statusTone(v) === "ok").length;

  // social sub-records (appstore / reddit / youtube)
  const social = isPlainObject(sections.social) ? sections.social : null;
  const socialEntries = social
    ? Object.entries(social).filter(([, v]) => sectionPresent(v as UniverseSection))
    : [];

  function laneStatus(lane: string): string | undefined {
    const v = endpointStatus[lane];
    return typeof v === "string" && v.trim() ? v : undefined;
  }
  function laneSources(lane: string): string[] | null {
    const v = dataSources[lane];
    return Array.isArray(v) ? v : null;
  }

  async function showRaw(format: "md" | "html") {
    setView("raw");
    setRawFormat(format);
    if (raw[format] !== null) return; // resolved once per format
    // Prefer the on-demand projection; fall back to what the backend already attached
    // (result.render, when the run carried the matching render_format); else honest empty.
    if (onFetchRender) {
      setRawLoading(true);
      try {
        const text = await onFetchRender(format);
        setRaw((p) => ({ ...p, [format]: text || fallbackRender(format) }));
      } catch {
        setRaw((p) => ({ ...p, [format]: fallbackRender(format) }));
      } finally {
        setRawLoading(false);
      }
    } else {
      setRaw((p) => ({ ...p, [format]: fallbackRender(format) }));
    }
  }

  /** What we can show without a fetch: the matching render the backend already attached. */
  function fallbackRender(format: "md" | "html"): string {
    if (result.render && (result.render_format ?? "md") === format) {
      return result.render;
    }
    return "";
  }

  async function copyRaw() {
    try {
      await navigator.clipboard.writeText(raw[rawFormat] ?? "");
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      /* clipboard blocked -- ignore */
    }
  }

  const rawText = raw[rawFormat];
  const rawEmpty = rawText !== null && rawText.length === 0;

  return (
    <div className="animate-fade-in space-y-4">
      {/* ---- outcome strip (mirrors ResultView) -------------------------- */}
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
            Fontes
          </span>
          <span className="text-sm text-text">
            {okCount}/{statuses.length || 0} ok
          </span>
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

      {/* ---- report header + view toggle -------------------------------- */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2 font-mono text-2xs text-text-faint">
          <span className="text-synapse">
            <ResearchIcon width={16} height={16} />
          </span>
          {report.seed ? (
            <span className="text-text">{report.seed}</span>
          ) : (
            <span>research_universe</span>
          )}
          {report.seed_type && (
            <span className="chip">seed_type={report.seed_type}</span>
          )}
          {report.fetched_at && <span>. {report.fetched_at}</span>}
          {report.mock === true && (
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
            relatorio
          </button>
          <button
            onClick={() => showRaw("md")}
            className={[
              "border-l border-line px-3 py-1 font-mono text-2xs uppercase tracking-wider transition-colors",
              view === "raw" && rawFormat === "md"
                ? "bg-synapse/10 text-synapse"
                : "bg-panel-sunken text-text-muted hover:text-text",
            ].join(" ")}
          >
            md
          </button>
          <button
            onClick={() => showRaw("html")}
            className={[
              "border-l border-line px-3 py-1 font-mono text-2xs uppercase tracking-wider transition-colors",
              view === "raw" && rawFormat === "html"
                ? "bg-synapse/10 text-synapse"
                : "bg-panel-sunken text-text-muted hover:text-text",
            ].join(" ")}
          >
            html
          </button>
        </div>
      </div>

      {view === "report" ? (
        <div className="space-y-4">
          {/* ---- Contrato de input (the typed INPUT, like the molded cards) -- */}
          <InputContractPanel fields={RESEARCH_UNIVERSE_INPUT_CONTRACT} />

          {/* ---- per-source STATUS row -------------------------------- */}
          {statuses.length > 0 && (
            <div className="rounded-card border border-line bg-panel-sunken px-4 py-4">
              <p className="eyebrow mb-2.5">// fontes (status por lane)</p>
              <div className="flex flex-wrap gap-1.5">
                {statuses.map(([lane, status]) => {
                  const tone = statusTone(status);
                  return (
                    <span
                      key={lane}
                      title={status}
                      className={`inline-flex items-center gap-1.5 rounded-pill border px-2.5 py-1 font-mono text-2xs ${TONE_CHIP[tone]}`}
                    >
                      <span className={`h-1.5 w-1.5 rounded-full ${TONE_DOT[tone]}`} />
                      <span className="uppercase tracking-wider">{humanize(lane)}</span>
                      <span className="normal-case opacity-80">{status}</span>
                    </span>
                  );
                })}
              </div>
            </div>
          )}

          {/* ---- SECTION CARDS (one per non-null section) ------------- */}
          <div className="grid grid-cols-1 gap-3">
            <SectionCard
              title="Identidade (CNPJ)"
              lane="cnpj"
              value={sections.identity ?? null}
              status={laneStatus("cnpj")}
              sources={laneSources("cnpj")}
            />
            {/* firmographics: only renders when the lane returned a record (else omitted,
                not an honest-empty card -- it shares the cnpj lane's status/provenance). */}
            {sectionPresent(sections.firmographics ?? null) && (
              <SectionCard
                title="Firmografia"
                lane="cnpj"
                value={sections.firmographics ?? null}
                status={laneStatus("cnpj")}
                sources={laneSources("cnpj")}
              />
            )}
            <SectionCard
              title="Mercado (IBGE)"
              lane="ibge"
              value={sections.market ?? null}
              status={laneStatus("ibge")}
              sources={laneSources("ibge")}
            />
            <SectionCard
              title="Reputacao (Reclame Aqui)"
              lane="reclame_aqui"
              value={sections.reputation ?? null}
              status={laneStatus("reclame_aqui")}
              sources={laneSources("reclame_aqui")}
            />

            {/* social sub-records: one card per present sub-lane, else honest blocked */}
            {socialEntries.length > 0 ? (
              socialEntries.map(([key, value]) => (
                <SectionCard
                  key={key}
                  title={`Social -- ${humanize(key)}`}
                  lane={key}
                  value={value as UniverseSection}
                  status={laneStatus(key)}
                  sources={laneSources(key)}
                />
              ))
            ) : (
              <SectionCard
                title="Social (appstore / reddit / youtube)"
                lane="social"
                value={null}
                status={
                  laneStatus("reddit") ||
                  laneStatus("youtube") ||
                  laneStatus("appstore")
                }
                sources={null}
              />
            )}

            <SectionCard
              title="Palavras-chave (SEO)"
              lane="seo"
              value={sections.keywords ?? null}
              status={laneStatus("seo")}
              sources={laneSources("seo")}
            />
            <SectionCard
              title="Perguntas (multi-perspectiva)"
              lane="questions"
              value={sections.questions ?? null}
              status={laneStatus("questions")}
              sources={laneSources("questions")}
            />
            <SentimentCard
              summary={sections.sentiment_summary ?? null}
              status={laneStatus("sentiment")}
              sources={laneSources("sentiment")}
            />
          </div>
        </div>
      ) : (
        // ---- raw MD/HTML projection (render_universe via ?render_format) ----
        <div className="overflow-hidden rounded-lg border border-line">
          <div className="flex items-center justify-between border-b border-line bg-panel-sunken px-4 py-2">
            <span className="font-mono text-2xs uppercase tracking-wider text-text-muted">
              render_universe (render_format={rawFormat})
            </span>
            <button
              onClick={copyRaw}
              disabled={!rawText}
              className="font-mono text-2xs uppercase tracking-wider text-text-muted transition-colors hover:text-synapse disabled:opacity-40"
            >
              {copied ? "copied" : "copy"}
            </button>
          </div>
          <pre className="max-h-[42vh] overflow-auto bg-ink-800 px-4 py-4 font-mono text-xs leading-relaxed text-text-muted">
            {rawLoading
              ? "loading projection..."
              : rawEmpty
                ? `Projecao ${rawFormat} indisponivel -- rode com ?render_format=${rawFormat} para o relatorio bruto.`
                : rawText}
          </pre>
        </div>
      )}

      {/* ---- identity line + errors (mirrors ResultView) ----------------- */}
      <div className="flex flex-wrap items-center gap-2 font-mono text-2xs text-text-faint">
        <span className="chip">{result.nucleus}</span>
        <span>kind={result.kind}</span>
        <span>pillar={result.pillar}</span>
        {report.seed_type && <span>seed_type={report.seed_type}</span>}
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
