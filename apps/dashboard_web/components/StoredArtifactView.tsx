"use client";

// ----------------------------------------------------------------------------
// StoredArtifactView -- the INLINE render of ONE stored result row (the Results
// deep-link). A persisted row from GET /results carries only a light summary
// {id, capability, kind, created_at}; its artifact BODY is fetched on demand as
// the backend's canonical PROJECTION via GET /results?render_format=md|html
// (main.py::_render_payload): a research_universe row -> render_universe, a
// product row -> the marketplace render, a plain row -> its canonical MD.
//
// HONEST BY CONSTRUCTION:
//   * This renders the EXACT string the backend persisted/projected -- never a
//     fabricated artifact. There is NO single-artifact-by-id GET on the backend
//     and the /results row does NOT carry the raw ``structured`` payload, so the
//     full per-section UniverseResultView/ResultView cards are NOT reconstructable
//     from a stored row -- we render the canonical md/html projection instead (the
//     same content the run-time toggle shows as its "raw" view). See the page
//     header note + the integrator notes for the backend gap.
//   * A row whose projection is empty (e.g. a seeded demo row, or a payload with
//     no projectable body) shows an explicit "projection unavailable" note, never
//     blank-as-success.
//   * No credential/token is ever present -- the projection is report text only.
//
// Style MIRRORS UniverseResultView's raw-projection panel exactly: the same
// md/html pill toggle, the same mono <pre> surface, the same copy affordance and
// token language (border-line / bg-panel-sunken / bg-ink-800 / text-text-muted).
// ----------------------------------------------------------------------------

import { useEffect, useState } from "react";

interface Props {
  /** the row id (provenance label + the key the fetch matches on). */
  recordId: string;
  /**
   * Fetch the canonical projection for THIS row in the given format. The page
   * wires this to ApiClient.listResults(capability, format) + a match on recordId
   * (fixtures + live both). Resolves '' when the backend attached no projection
   * for the row (honest "unavailable", never fabricated).
   */
  onFetchRender: (format: "md" | "html") => Promise<string>;
}

export function StoredArtifactView({ recordId, onFetchRender }: Props) {
  const [format, setFormat] = useState<"md" | "html">("md");
  const [cache, setCache] = useState<Record<"md" | "html", string | null>>({
    md: null,
    html: null,
  });
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  // Select a format; the effect below resolves+caches it once (the render is
  // stable for a persisted row, so each format is fetched at most once).
  const ensure = (fmt: "md" | "html") => setFormat(fmt);

  // Resolve the active format whenever it is not yet cached.
  useEffect(() => {
    let active = true;
    if (cache[format] !== null) return;
    setLoading(true);
    onFetchRender(format)
      .then((text) => {
        if (active) setCache((p) => ({ ...p, [format]: text ?? "" }));
      })
      .catch(() => {
        // degrade-never: a failed fetch resolves to an honest empty projection
        if (active) setCache((p) => ({ ...p, [format]: "" }));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [format, cache, onFetchRender]);

  async function copy() {
    try {
      await navigator.clipboard.writeText(cache[format] ?? "");
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      /* clipboard blocked -- ignore */
    }
  }

  const text = cache[format];
  const empty = text !== null && text.length === 0;

  return (
    <div className="animate-fade-in space-y-3">
      {/* ---- header: provenance + md/html toggle ----------------------- */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <span className="font-mono text-2xs text-text-faint">
          stored artifact . record={recordId}
        </span>
        <div className="inline-flex overflow-hidden rounded-pill border border-line">
          <button
            onClick={() => ensure("md")}
            className={[
              "px-3 py-1 font-mono text-2xs uppercase tracking-wider transition-colors",
              format === "md"
                ? "bg-synapse/10 text-synapse"
                : "bg-panel-sunken text-text-muted hover:text-text",
            ].join(" ")}
          >
            md
          </button>
          <button
            onClick={() => ensure("html")}
            className={[
              "border-l border-line px-3 py-1 font-mono text-2xs uppercase tracking-wider transition-colors",
              format === "html"
                ? "bg-synapse/10 text-synapse"
                : "bg-panel-sunken text-text-muted hover:text-text",
            ].join(" ")}
          >
            html
          </button>
        </div>
      </div>

      {/* ---- the canonical projection (md/html) ------------------------ */}
      <div className="overflow-hidden rounded-lg border border-line">
        <div className="flex items-center justify-between border-b border-line bg-panel-sunken px-4 py-2">
          <span className="font-mono text-2xs uppercase tracking-wider text-text-muted">
            render_format={format}
          </span>
          <button
            onClick={copy}
            disabled={!text}
            className="font-mono text-2xs uppercase tracking-wider text-text-muted transition-colors hover:text-synapse disabled:opacity-40"
          >
            {copied ? "copied" : "copy"}
          </button>
        </div>
        <pre className="max-h-[46vh] overflow-auto bg-ink-800 px-4 py-4 font-mono text-xs leading-relaxed text-text-muted">
          {loading
            ? "loading stored artifact..."
            : empty
              ? `Projecao ${format} indisponivel para este registro -- a linha do historico nao carrega um artefato projetavel (ou e um registro de exemplo).`
              : text}
        </pre>
      </div>
    </div>
  );
}
