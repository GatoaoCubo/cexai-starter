"use client";

// ----------------------------------------------------------------------------
// ResearchResultView -- the RICH report view for the product-research vertical
// (capability "pesquisa_produto"). When a CapabilityResultView carries the typed
// ~30-field structured payload (CapabilityResultView.structured), this renders it
// as a READABLE REPORT instead of raw MD:
//
//   [outcome strip: score / gate / persisted]
//   [ready_for_ads banner]            <- the flagship "go / blocked" signal
//   [price-band stat strip]           <- min / avg / sweet-spot / max
//   [competitors table + count]       <- top rival rating/reviews, mapped count
//   [gaps + opportunities lists]      <- the two market-shape lists
//   [keyword / SEO chips]             <- head/longtail/synonyms/inbound/outbound/neg
//   [provenance: marketplaces + data_sources]
//   [-> Gerar anuncio  CTA]           <- the research->ads chain affordance
//   [toggle: structured report  <->  canonical MD-frontmatter]
//
// Reuses ResultView's shell language + the chip/panel/eyebrow utility classes +
// ScoreMeter. The MD toggle consumes the canonical projection: it prefers an
// on-demand ?render_format=md fetch (via the optional onFetchMd prop) and falls
// back to result.artifact (the persisted canonical MD the run already returned).
//
// PURE-READ + TOTAL: every field is optional; a missing field's block is omitted
// (never throws on absent data -- mirrors the backend renderer's "blank on missing"
// contract). tenant_id is shown as provenance only; no credential is ever present.
// ----------------------------------------------------------------------------

import { useState } from "react";
import type {
  CapabilityResultView,
  ProductResearchResult,
  ProvenanceMap,
} from "@/lib/types";
import { PESQUISA_PRODUTO_INPUT_CONTRACT, type MoldField } from "@/lib/molds";
import { ScoreMeter } from "./ui";
import { AlertIcon, ArrowRight, CheckIcon, ResearchIcon } from "./icons";

interface Props {
  result: CapabilityResultView;
  /** the typed payload (caller has already confirmed it is present). */
  research: ProductResearchResult;
  /**
   * Optional: fetch the canonical MD projection on demand (consumes the backend
   * ?render_format=md path). When absent, the MD toggle falls back to
   * result.artifact (the persisted canonical MD the run already returned).
   */
  onFetchMd?: () => Promise<string>;
  /**
   * Optional: the research->ads chain. When provided, a "-> Gerar anuncio" CTA is
   * shown; clicking it runs the chain and the returned ads result renders inline.
   * When absent, the CTA is still shown as a visible (honest) next-step affordance,
   * disabled, labelled as the pipeline's next stage.
   */
  onChainToAds?: () => Promise<CapabilityResultView>;
}

// --- small local formatting helpers (PURE) ----------------------------------

/** "R$ 1.234" -- a brand-neutral BRL-ish format; '--' when absent/non-numeric. */
function brl(value: number | undefined): string {
  if (typeof value !== "number" || Number.isNaN(value)) return "--";
  const rounded = Math.round(value);
  // group thousands with a dot (pt-BR style) without pulling in Intl locale data.
  const s = String(Math.abs(rounded)).replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  return `R$ ${rounded < 0 ? "-" : ""}${s}`;
}

function num(value: number | undefined): string {
  if (typeof value !== "number" || Number.isNaN(value)) return "--";
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}

function hasList(value: string[] | undefined): value is string[] {
  return Array.isArray(value) && value.length > 0;
}

function hasMap(value: ProvenanceMap | undefined): value is ProvenanceMap {
  return Boolean(value) && typeof value === "object" && Object.keys(value!).length > 0;
}

// --- chip / list primitives (reuse the .chip utility class) ------------------

function ChipRow({
  label,
  items,
  tone = "default",
}: {
  label: string;
  items: string[] | undefined;
  tone?: "default" | "synapse" | "danger";
}) {
  if (!hasList(items)) return null;
  const chipCls =
    tone === "synapse"
      ? "chip border-synapse/30 text-synapse"
      : tone === "danger"
        ? "chip border-danger/30 text-danger"
        : "chip";
  return (
    <div>
      <p className="mb-1.5 font-mono text-2xs uppercase tracking-wider text-text-faint">
        {label}
        <span className="ml-1.5 text-text-faint/70 normal-case">({items.length})</span>
      </p>
      <div className="flex flex-wrap gap-1.5">
        {items.map((it, i) => (
          <span key={`${it}-${i}`} className={chipCls}>
            {it}
          </span>
        ))}
      </div>
    </div>
  );
}

function BulletList({
  label,
  items,
  marker,
}: {
  label: string;
  items: string[] | undefined;
  marker: "gap" | "opp";
}) {
  if (!hasList(items)) return null;
  const dot = marker === "opp" ? "bg-synapse" : "bg-signal";
  return (
    <div className="rounded-lg border border-line bg-panel-sunken px-4 py-3">
      <p className="mb-2 font-mono text-2xs uppercase tracking-wider text-text-muted">
        {label}
        <span className="ml-1.5 text-text-faint normal-case">({items.length})</span>
      </p>
      <ul className="space-y-1.5">
        {items.map((it, i) => (
          <li key={`${it}-${i}`} className="flex items-start gap-2 text-sm text-text">
            <span className={`mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full ${dot}`} />
            <span>{it}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

/** A provenance object (marketplace -> path, or source -> count) as small badges. */
function ProvenanceBadges({
  label,
  map,
}: {
  label: string;
  map: ProvenanceMap | undefined;
}) {
  if (!hasMap(map)) return null;
  return (
    <div>
      <p className="mb-1.5 font-mono text-2xs uppercase tracking-wider text-text-faint">
        {label}
      </p>
      <div className="flex flex-wrap gap-1.5">
        {Object.entries(map).map(([k, v]) => (
          <span
            key={k}
            className="inline-flex items-center gap-1.5 rounded-pill border border-line bg-panel-sunken px-2.5 py-1 font-mono text-2xs text-text-muted"
          >
            <span className="text-text-faint">{k}</span>
            <span className="text-text">{String(v)}</span>
          </span>
        ))}
      </div>
    </div>
  );
}

// --- the confidence badge (mirrors the backend colour bands) -----------------

function ConfidenceBadge({ score }: { score: number | undefined }) {
  let cls = "border-line text-text-muted";
  let label = "confianca n/d";
  if (typeof score === "number") {
    label = `confianca ${score.toFixed(1)}/10`;
    if (score >= 7.5) cls = "border-synapse/40 bg-synapse/10 text-synapse";
    else if (score >= 5) cls = "border-signal/40 bg-signal/10 text-signal";
    else cls = "border-danger/40 bg-danger/10 text-danger";
  }
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-pill border px-2.5 py-1 font-mono text-2xs uppercase tracking-wider ${cls}`}
    >
      {label}
    </span>
  );
}

// --- the Input contract panel (the typed I/O contract, example-filled) -------
//
// Mirrors StructuredResultView's InputContractPanel idiom verbatim (same grid
// columns + chip/table tokens) so the bespoke vertical declares its typed INPUT
// the same way the 14 molded cards do. Source = PESQUISA_PRODUTO_INPUT_CONTRACT
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

export function ResearchResultView({
  result,
  research,
  onFetchMd,
  onChainToAds,
}: Props) {
  const [view, setView] = useState<"report" | "md">("report");
  const [md, setMd] = useState<string | null>(null);
  const [mdLoading, setMdLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  // chain-to-ads state
  const [adsResult, setAdsResult] = useState<CapabilityResultView | null>(null);
  const [adsLoading, setAdsLoading] = useState(false);
  const [adsError, setAdsError] = useState<string | null>(null);

  const ready = research.ready_for_ads === true;

  async function showMd() {
    setView("md");
    if (md !== null) return; // already resolved once
    // Prefer the on-demand canonical projection (?render_format=md); fall back to
    // the artifact the run already returned (also the canonical MD).
    if (onFetchMd) {
      setMdLoading(true);
      try {
        const text = await onFetchMd();
        setMd(text || result.artifact || "");
      } catch {
        setMd(result.artifact || "");
      } finally {
        setMdLoading(false);
      }
    } else {
      setMd(result.artifact || "");
    }
  }

  async function copyMd() {
    try {
      await navigator.clipboard.writeText(md ?? result.artifact ?? "");
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      /* clipboard blocked -- ignore */
    }
  }

  async function runChain() {
    if (!onChainToAds || adsLoading) return;
    setAdsLoading(true);
    setAdsError(null);
    try {
      const r = await onChainToAds();
      setAdsResult(r);
    } catch (err) {
      setAdsError(
        err instanceof Error ? err.message : "O anuncio nao pode ser gerado.",
      );
    } finally {
      setAdsLoading(false);
    }
  }

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
            Confianca
          </span>
          <ConfidenceBadge score={research.confidence_score} />
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

      {/* ---- view toggle: structured report <-> canonical MD ------------- */}
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 font-mono text-2xs text-text-faint">
          <span className="text-synapse">
            <ResearchIcon width={16} height={16} />
          </span>
          {research.product_name ? (
            <span className="text-text">{research.product_name}</span>
          ) : (
            <span>pesquisa_produto</span>
          )}
          {research.mock === true && (
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
            onClick={showMd}
            className={[
              "border-l border-line px-3 py-1 font-mono text-2xs uppercase tracking-wider transition-colors",
              view === "md"
                ? "bg-synapse/10 text-synapse"
                : "bg-panel-sunken text-text-muted hover:text-text",
            ].join(" ")}
          >
            md (AI)
          </button>
        </div>
      </div>

      {view === "report" ? (
        <div className="space-y-4">
          {/* ---- Contrato de input (the typed INPUT, like the molded cards) -- */}
          <InputContractPanel fields={PESQUISA_PRODUTO_INPUT_CONTRACT} />

          {/* ---- ready_for_ads banner -- the flagship go/blocked signal --- */}
          <div
            className={[
              "flex items-center gap-3 rounded-lg border px-4 py-3",
              ready
                ? "border-synapse/40 bg-synapse/[0.07]"
                : "border-signal/40 bg-signal/[0.07]",
            ].join(" ")}
          >
            <span
              className={[
                "grid h-7 w-7 shrink-0 place-items-center rounded-full",
                ready ? "bg-synapse text-ink" : "bg-signal/20 text-signal",
              ].join(" ")}
            >
              {ready ? <CheckIcon /> : <AlertIcon />}
            </span>
            <div>
              <p
                className={[
                  "font-display text-sm font-600",
                  ready ? "text-synapse" : "text-signal",
                ].join(" ")}
              >
                {ready ? "Pronto para anuncio" : "Pesquisa incompleta -- anuncio bloqueado"}
              </p>
              <p className="font-mono text-2xs text-text-faint">
                gate: confianca &ge; 7.5 . concorrentes &ge; 1 . preco_min &gt; 0 . head_terms &ge; 1
              </p>
            </div>
          </div>

          {/* ---- price-band stat strip ----------------------------------- */}
          <div>
            <p className="eyebrow mb-2">// preco de mercado</p>
            <div className="grid grid-cols-2 overflow-hidden rounded-card border border-line sm:grid-cols-4">
              {[
                { label: "minimo", value: brl(research.price_band_min) },
                { label: "medio", value: brl(research.price_avg) },
                {
                  label: "recomendado",
                  value: brl(research.sweet_spot_price),
                  hot: true,
                },
                { label: "maximo", value: brl(research.price_band_max) },
              ].map((s, i) => (
                <div
                  key={s.label}
                  className={[
                    "bg-panel px-4 py-3",
                    i < 3 ? "border-b border-line sm:border-b-0 sm:border-r" : "",
                    i % 2 === 0 ? "border-r border-line sm:border-r" : "",
                  ].join(" ")}
                >
                  <b
                    className={[
                      "block font-display text-xl font-600 leading-none",
                      s.hot ? "text-synapse" : "text-text",
                    ].join(" ")}
                  >
                    {s.value}
                  </b>
                  <span className="mt-1.5 block font-mono text-2xs uppercase tracking-wider text-text-muted">
                    {s.label}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* ---- competitors -------------------------------------------- */}
          {(research.top_competitor_name ||
            typeof research.competitors_count === "number") && (
            <div>
              <p className="eyebrow mb-2">
                // inteligencia competitiva
                {typeof research.competitors_count === "number" && (
                  <span className="ml-2 text-text-muted normal-case">
                    {research.competitors_count} mapeados
                  </span>
                )}
              </p>
              <div className="overflow-hidden rounded-card border border-line">
                <div className="grid grid-cols-[1.6fr_0.8fr_0.8fr] gap-4 border-b border-line bg-panel-sunken px-4 py-2 font-mono text-2xs uppercase tracking-wider text-text-faint">
                  <span>Principal concorrente</span>
                  <span className="text-right">Avaliacao</span>
                  <span className="text-right">Reviews</span>
                </div>
                <div className="grid grid-cols-[1.6fr_0.8fr_0.8fr] items-center gap-4 bg-panel px-4 py-3">
                  <span className="font-display text-sm font-600 text-text">
                    {research.top_competitor_name ?? "--"}
                  </span>
                  <span className="text-right font-mono text-sm text-text">
                    {num(research.top_competitor_rating)}
                    {typeof research.top_competitor_rating === "number" && (
                      <span className="text-text-faint"> / 5</span>
                    )}
                  </span>
                  <span className="text-right font-mono text-sm text-text">
                    {typeof research.top_competitor_reviews === "number"
                      ? research.top_competitor_reviews.toLocaleString("en-US")
                      : "--"}
                  </span>
                </div>
              </div>
              {(research.differentiation_angle || research.recommended_positioning) && (
                <div className="mt-2 space-y-1.5 rounded-lg border border-line bg-panel-sunken px-4 py-3 text-sm">
                  {research.recommended_positioning && (
                    <p className="text-text">
                      <span className="font-mono text-2xs uppercase tracking-wider text-text-faint">
                        Posicionamento:{" "}
                      </span>
                      {research.recommended_positioning}
                    </p>
                  )}
                  {research.differentiation_angle && (
                    <p className="text-text-muted">
                      <span className="font-mono text-2xs uppercase tracking-wider text-text-faint">
                        Angulo:{" "}
                      </span>
                      {research.differentiation_angle}
                    </p>
                  )}
                </div>
              )}
            </div>
          )}

          {/* ---- gaps + opportunities ----------------------------------- */}
          {(hasList(research.gaps) || hasList(research.opportunities)) && (
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <BulletList
                label="Lacunas do mercado"
                items={research.gaps}
                marker="gap"
              />
              <BulletList
                label="Oportunidades"
                items={research.opportunities}
                marker="opp"
              />
            </div>
          )}

          {/* ---- keyword / SEO chips ------------------------------------ */}
          {(hasList(research.head_terms) ||
            hasList(research.longtails) ||
            hasList(research.synonyms) ||
            hasList(research.seo_inbound) ||
            hasList(research.seo_outbound) ||
            hasList(research.negative_keywords)) && (
            <div className="space-y-3 rounded-card border border-line bg-panel px-4 py-4">
              <p className="eyebrow">// palavras-chave &amp; SEO</p>
              <ChipRow
                label="Principais (head terms)"
                items={research.head_terms}
                tone="synapse"
              />
              <ChipRow label="Cauda longa" items={research.longtails} />
              <ChipRow label="Sinonimos" items={research.synonyms} />
              <ChipRow label="SEO inbound" items={research.seo_inbound} />
              <ChipRow label="SEO outbound (ads)" items={research.seo_outbound} />
              <ChipRow
                label="Negativas"
                items={research.negative_keywords}
                tone="danger"
              />
            </div>
          )}

          {/* ---- provenance: marketplaces + sources --------------------- */}
          {(hasList(research.marketplaces_queried) ||
            hasList(research.marketplaces_failed) ||
            hasMap(research.data_sources) ||
            hasMap(research.category_paths)) && (
            <div className="space-y-3 rounded-card border border-line bg-panel-sunken px-4 py-4">
              <p className="eyebrow">// proveniencia</p>
              <ChipRow
                label="Marketplaces consultados"
                items={research.marketplaces_queried}
                tone="synapse"
              />
              <ChipRow
                label="Marketplaces sem dado"
                items={research.marketplaces_failed}
                tone="danger"
              />
              <ProvenanceBadges label="Origem dos dados" map={research.data_sources} />
              <ProvenanceBadges
                label="Categorias por marketplace"
                map={research.category_paths}
              />
              {(research.run_timestamp || research.data_freshness) && (
                <p className="font-mono text-2xs text-text-faint">
                  {research.run_timestamp && <>data/hora: {research.run_timestamp} </>}
                  {research.data_freshness && (
                    <>. dado mais antigo: {research.data_freshness}</>
                  )}
                </p>
              )}
            </div>
          )}
        </div>
      ) : (
        // ---- canonical MD-frontmatter view (the AI projection) ----------
        <div className="overflow-hidden rounded-lg border border-line">
          <div className="flex items-center justify-between border-b border-line bg-panel-sunken px-4 py-2">
            <span className="font-mono text-2xs uppercase tracking-wider text-text-muted">
              Canonical MD (render_format=md)
            </span>
            <button
              onClick={copyMd}
              className="font-mono text-2xs uppercase tracking-wider text-text-muted transition-colors hover:text-synapse"
            >
              {copied ? "copied" : "copy"}
            </button>
          </div>
          <pre className="max-h-[42vh] overflow-auto bg-ink-800 px-4 py-4 font-mono text-xs leading-relaxed text-text-muted">
            {mdLoading ? "loading canonical MD..." : md ?? result.artifact}
          </pre>
        </div>
      )}

      {/* ---- the research->ads chain affordance -------------------------- */}
      <div className="rounded-lg border border-line bg-panel-sunken px-4 py-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="font-mono text-2xs uppercase tracking-wider text-text-muted">
              Proximo passo do pipeline
            </p>
            <p className="mt-0.5 text-sm text-text">
              {ready
                ? "A pesquisa esta pronta -- gere o anuncio a partir destes dados."
                : "O pipeline encadeia pesquisa -> anuncio (gate incompleto)."}
            </p>
          </div>
          <button
            onClick={runChain}
            disabled={!onChainToAds || adsLoading}
            title={
              onChainToAds
                ? undefined
                : "A cadeia pesquisa->anuncio sera executada pelo runtime."
            }
            className="btn-primary disabled:opacity-40"
          >
            {adsLoading ? "Gerando anuncio..." : "Gerar anuncio"}
            {!adsLoading && <ArrowRight />}
          </button>
        </div>
        <p className="mt-2 font-mono text-2xs text-text-faint">
          research -&gt; anuncio . usa anuncio_open_vars (usps := opportunities +
          diferenciacao . competitor_gaps := lacunas)
        </p>
      </div>

      {adsError && (
        <div
          role="alert"
          className="flex items-start gap-2 rounded-lg border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger"
        >
          <span className="mt-0.5 shrink-0">
            <AlertIcon />
          </span>
          <span>{adsError}</span>
        </div>
      )}

      {/* ---- the chained ads result (rendered inline) -------------------- */}
      {adsResult && (
        <div className="rounded-card border border-synapse/30 bg-synapse/[0.04] p-4">
          <div className="mb-3 flex items-center gap-2">
            <span className="chip border-synapse/30 text-synapse">anuncio gerado</span>
            <span className="font-mono text-2xs text-text-faint">
              kind={adsResult.kind} . nucleus={adsResult.nucleus}
            </span>
          </div>
          <div className="mb-3 flex flex-wrap items-center gap-x-6 gap-y-2">
            <div className="flex items-center gap-2">
              <span className="font-mono text-2xs uppercase tracking-wider text-text-faint">
                Score
              </span>
              <ScoreMeter score={adsResult.score} />
            </div>
            {adsResult.persisted && (
              <span className="inline-flex items-center gap-1.5 text-sm text-text">
                <span className="h-1.5 w-1.5 rounded-full bg-synapse" />
                tenant data plane
              </span>
            )}
          </div>
          <pre className="max-h-[36vh] overflow-auto rounded-lg border border-line bg-ink-800 px-4 py-4 font-mono text-xs leading-relaxed text-text-muted">
            {adsResult.artifact}
          </pre>
        </div>
      )}

      {/* ---- identity line + errors (mirrors ResultView) ----------------- */}
      <div className="flex flex-wrap items-center gap-2 font-mono text-2xs text-text-faint">
        <span className="chip">{result.nucleus}</span>
        <span>kind={result.kind}</span>
        <span>pillar={result.pillar}</span>
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
