"use client";

// ----------------------------------------------------------------------------
// Renders a completed CapabilityResultView: the score + gate + persistence
// status, then the produced artifact (frontmatter + body) in a mono surface
// with a copy action. No credential/api_key is ever present in this shape.
// ----------------------------------------------------------------------------

import { useState } from "react";
import type {
  CapabilityResultView,
  DualOutputResult,
  ProductResearchResult,
  ResearchUniverseReport,
  UploadedMedia,
} from "@/lib/types";
import type { CapabilityMold } from "@/lib/molds";
import { moldFor } from "@/lib/molds";
import { ScoreMeter } from "./ui";
import { CheckIcon, AlertIcon } from "./icons";
import { ResearchResultView } from "./ResearchResultView";
import { UniverseResultView } from "./UniverseResultView";
import { StructuredResultView } from "./StructuredResultView";
import { DualOutputFace } from "./DualOutputFace";
import { RenderBoundary } from "./RenderBoundary";

/**
 * Detect a MOLDED capability result and return its mold, else null. A result is
 * molded when it carries a ``mold_id`` (top-level, or inside ``structured``) -- an
 * EXPLICIT, unambiguous flag the run sets for capabilities whose real generator
 * does not exist yet (the typed I/O contract / "mold"). This MUST be checked
 * BEFORE asResearch: asResearch returns ANY structured object as a product report,
 * so a molded result that also rode ``structured`` would otherwise misroute to the
 * marketplace renderer. Degrade-never: an unknown ``mold_id`` (not in MOLDS) still
 * routes here (StructuredResultView shows the honest "indisponivel" + raw JSON)
 * rather than falling through to a wrong renderer. No mold_id -> null (unchanged
 * universe -> product -> generic routing for every existing result).
 */
function asMold(result: CapabilityResultView): CapabilityMold | null | "unresolved" {
  const fromTop = result.mold_id;
  const fromStructured =
    result.structured && typeof result.structured === "object"
      ? (result.structured as { mold_id?: string }).mold_id
      : undefined;
  const moldId = fromTop ?? fromStructured;
  if (!moldId) return null;
  return moldFor(moldId) ?? "unresolved";
}

/**
 * Detect a research-universe result and return its typed report, else null.
 * A result is research-universe when its ``kind`` is "research_universe" OR its
 * structured payload carries the orchestrator's signature keys (``seed_type`` +
 * ``endpoint_status``) -- the SAME discriminator the backend uses
 * (main.py::_is_universe_report). This MUST be checked before asResearch since both
 * verticals ride the ``structured`` slot. Degrade-never: a universe result WITHOUT a
 * structured payload falls through to the generic view (the canonical MD still renders).
 */
function asUniverse(
  result: CapabilityResultView,
): ResearchUniverseReport | null {
  const s = result.structured;
  if (!s || typeof s !== "object") return null;
  const looksUniverse =
    result.kind === "research_universe" ||
    ("seed_type" in s && "endpoint_status" in s);
  return looksUniverse ? (s as ResearchUniverseReport) : null;
}

/**
 * Detect a product-research result and return its typed payload, else null.
 * A result is product-research when it carries the structured payload (the
 * backend attaches it for the ``pesquisa_produto`` vertical) AND it is NOT a
 * universe report (checked first). Other capabilities return null -> the generic
 * artifact view below renders them. Degrade-never: a product-research result
 * WITHOUT a structured payload falls through to the generic view.
 */
function asResearch(
  result: CapabilityResultView,
): ProductResearchResult | null {
  const s = result.structured;
  if (s && typeof s === "object") return s as ProductResearchResult;
  return null;
}

/**
 * Detect a dual-output asset and return it, else null. A result carries one when its
 * structured-generator run emitted the dual-surface asset (cex_dual_output.to_dual_output,
 * forwarded by the backend). It is returned only when it has a RENDERABLE surface -- at
 * least one media slot OR a machine .md (in either the flat emitter shape or a reshaped
 * {machine,human} contract) -- so a thin/garbage asset degrades to null and ResultView
 * renders exactly today's body. Independent of the body routing above: the dual face
 * renders ABOVE whatever sub-view the result routes to (degrade-never, zero-regression).
 */
function asDual(result: CapabilityResultView): DualOutputResult | null {
  const d = result.dual_output;
  if (!d || typeof d !== "object") return null;
  const flatSlots = Array.isArray(d.media_slots) && d.media_slots.length > 0;
  const flatMd = typeof d.machine_md === "string" && d.machine_md.length > 0;
  const human = (d as { human?: { mediaSlots?: unknown } }).human;
  const humanSlots =
    !!human && Array.isArray(human.mediaSlots) && human.mediaSlots.length > 0;
  const machine = (d as { machine?: { md?: unknown } }).machine;
  const machineMd =
    !!machine && typeof machine.md === "string" && machine.md.length > 0;
  return flatSlots || flatMd || humanSlots || machineMd ? d : null;
}

interface ResultViewProps {
  result: CapabilityResultView;
  /** passthrough to ResearchResultView: fetch the canonical MD on demand. */
  onFetchMd?: () => Promise<string>;
  /** passthrough to ResearchResultView: run the research->ads chain. */
  onChainToAds?: () => Promise<CapabilityResultView>;
  /** passthrough to UniverseResultView: fetch a raw md/html projection on demand. */
  onFetchRender?: (format: "md" | "html") => Promise<string>;
  /** passthrough to DualOutputFace: persist a human upload into a media slot (upload-persist). */
  onUploadMedia?: (slotKey: string, file: File) => Promise<UploadedMedia>;
}

export function ResultView({
  result,
  onFetchMd,
  onChainToAds,
  onFetchRender,
  onUploadMedia,
}: ResultViewProps) {
  const [copied, setCopied] = useState(false);

  // The dual-output audiovisual face (mission DASHBOARD_COMPOSITION W5) renders
  // ABOVE whatever body the result routes to. Absent on results without a dual_output
  // asset -> ``body`` is returned directly below (degrade-never, byte-identical to before).
  const dual = asDual(result);

  // The existing routing, captured so the dual face can wrap it. Inner indentation is
  // left as-is (cosmetic only); each branch still returns its bespoke sub-view unchanged.
  const body = ((): JSX.Element => {

  // Route MOLDED results FIRST -- a result with a ``mold_id`` is the typed I/O
  // contract of a not-yet-built capability; it must win BEFORE asResearch (which
  // would otherwise claim its ``structured`` slot as a product report). An
  // "unresolved" mold_id still renders here (honest degrade), never falls through.
  const mold = asMold(result);
  if (mold) {
    return (
      <StructuredResultView
        result={result}
        mold={mold === "unresolved" ? undefined : mold}
      />
    );
  }

  // Route research-universe results to the multi-source report FIRST (both verticals
  // ride ``structured``, so the universe discriminator must win). Then product-research.
  // Everything else uses the generic artifact view below. RunModal/AgentRunModal call
  // <ResultView/> unchanged -- the routing is internal so no caller needs to know the vertical.
  const universe = asUniverse(result);
  if (universe) {
    return (
      <UniverseResultView
        result={result}
        report={universe}
        onFetchRender={onFetchRender}
      />
    );
  }

  const research = asResearch(result);
  if (research) {
    return (
      <ResearchResultView
        result={result}
        research={research}
        onFetchMd={onFetchMd}
        onChainToAds={onChainToAds}
      />
    );
  }

  async function copy() {
    try {
      await navigator.clipboard.writeText(result.artifact);
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      /* clipboard blocked -- ignore */
    }
  }

  return (
    <div className="animate-fade-in space-y-4">
      {/* outcome strip */}
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

      {/* identity line */}
      <div className="flex flex-wrap items-center gap-2 font-mono text-2xs text-text-faint">
        <span className="chip">{result.nucleus}</span>
        <span>kind={result.kind}</span>
        <span>pillar={result.pillar}</span>
        {result.record_id && <span>record={result.record_id}</span>}
      </div>

      {/* the artifact */}
      <div className="overflow-hidden rounded-lg border border-line">
        <div className="flex items-center justify-between border-b border-line bg-panel-sunken px-4 py-2">
          <span className="font-mono text-2xs uppercase tracking-wider text-text-muted">
            Artifact
          </span>
          <button
            onClick={copy}
            className="font-mono text-2xs uppercase tracking-wider text-text-muted transition-colors hover:text-synapse"
          >
            {copied ? "copied" : "copy"}
          </button>
        </div>
        <pre className="max-h-[42vh] overflow-auto bg-ink-800 px-4 py-4 font-mono text-xs leading-relaxed text-text-muted">
          {result.artifact}
        </pre>
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

  })();

  // Degrade-never: no dual_output -> return EXACTLY today's routed body. Otherwise
  // render the human audiovisual face ABOVE it (the two coupled faces, on screen).
  // The face is wrapped in a RenderBoundary so a future render throw inside it (e.g. a
  // malformed dual asset from the real backend) degrades to a small "[previa
  // indisponivel]" note instead of erasing the entire result view.
  if (!dual) return body;
  return (
    <div className="animate-fade-in space-y-6">
      <RenderBoundary
        fallback={
          <p className="font-mono text-2xs text-text-faint">
            [previa audiovisual indisponivel]
          </p>
        }
      >
        <DualOutputFace
          dual={dual}
          recordId={
            typeof result.record_id === "string" ? result.record_id : undefined
          }
          onUploadMedia={onUploadMedia}
        />
      </RenderBoundary>
      {body}
    </div>
  );
}
