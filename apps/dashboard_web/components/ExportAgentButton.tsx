"use client";

// ----------------------------------------------------------------------------
// "Exportar agente" -- export ONE capability as a portable agent package to an external
// runtime (GPT Builder / Claude Project / MCP). Lives on the capability view (RunModal):
// it exports the capability's AGENT DEFINITION (system instructions + A2A agent_card + I/O
// contract), independent of whether you ran it.
//
// FLOW: click "Exportar agente" -> a small target picker opens (GPT Builder / Claude / MCP)
// -> pick one -> POST /api/export-agent { tenant, capability, target } -> on success the
// route streams a .zip which we download; on a refusal the route returns JSON we surface.
//
// DEV-GATED (mirrors /api/onboard): this is a dev/operator affordance. The SERVER route is
// the security boundary (NODE_ENV + the server-only CEXAI_EXPORT_ENABLED); here we only
// gate the UI affordance on NODE_ENV==="development" so a prod build never shows a button
// that would 403. Honest loading / error / done states. ASCII-only + diacritic-free.
// ----------------------------------------------------------------------------

import { useState } from "react";
import {
  EXPORT_TARGETS,
  EXPORT_TARGET_LABELS,
  exportZipFilename,
  type ExportApiError,
  type ExportTarget,
} from "@/lib/exportAgent";
import { AlertIcon, CheckIcon } from "./icons";

interface Props {
  /** the tenant SLUG (the .cex/tenants/<slug> key -- the brand/overlay source). */
  tenant: string;
  /** the capability slug to export (Card.capability). */
  capability: string;
  /** optional: disable the control (e.g. while a run is in flight). */
  disabled?: boolean;
}

// Dev-only affordance. The route ALSO enforces NODE_ENV + CEXAI_EXPORT_ENABLED server-side;
// gating the UI on NODE_ENV here keeps a prod build from showing a button that can only 403.
const EXPORT_UI_ENABLED = process.env.NODE_ENV === "development";

const SLUG_RE = /^[a-z0-9][a-z0-9_-]{0,63}$/;

export function ExportAgentButton({ tenant, capability, disabled }: Props) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState<ExportTarget | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState<string | null>(null);

  if (!EXPORT_UI_ENABLED) return null;

  const slugOk = SLUG_RE.test(tenant) && SLUG_RE.test(capability);

  async function exportTo(target: ExportTarget) {
    if (busy) return;
    setBusy(target);
    setError(null);
    setDone(null);
    try {
      const res = await fetch("/api/export-agent", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ tenant, capability, target }),
      });
      const ctype = res.headers.get("content-type") || "";
      if (res.ok && ctype.includes("application/zip")) {
        // Stream the zip to a browser download.
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = exportZipFilename(tenant, capability, target);
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
        setDone(EXPORT_TARGET_LABELS[target]);
        setOpen(false);
      } else {
        // Honest error path -- the route returns JSON { ok:false, errors }.
        let msg = `Falha ao exportar (${res.status}).`;
        try {
          const data = (await res.json()) as ExportApiError;
          if (Array.isArray(data.errors) && data.errors.length) {
            msg = data.errors.join(" ");
          }
        } catch {
          /* keep the default message */
        }
        setError(msg);
      }
    } catch (err) {
      setError(
        "Falha de rede ao chamar /api/export-agent: " +
          (err instanceof Error ? err.message : String(err)),
      );
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="mt-3">
      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          disabled={disabled || !slugOk}
          onClick={() => {
            setOpen((o) => !o);
            setError(null);
          }}
          aria-expanded={open}
          aria-haspopup="menu"
          className="inline-flex items-center gap-1.5 rounded-lg border border-line bg-panel-sunken px-3 py-1.5 font-mono text-2xs uppercase tracking-wider text-text-muted transition-colors hover:border-synapse/40 hover:text-synapse disabled:cursor-not-allowed disabled:opacity-50"
        >
          <DownloadGlyph />
          Exportar agente
        </button>

        {done && (
          <span className="inline-flex items-center gap-1 font-mono text-2xs text-synapse">
            <CheckIcon />
            baixado ({done})
          </span>
        )}
      </div>

      {!slugOk && (
        <p className="mt-1.5 font-mono text-2xs text-text-faint">
          exportacao indisponivel -- tenant/capacidade sem slug valido
        </p>
      )}

      {/* the target picker (GPT Builder / Claude Project / MCP) */}
      {open && slugOk && (
        <div
          role="menu"
          aria-label="Escolha o destino da exportacao"
          className="mt-2 rounded-lg border border-line bg-panel-sunken px-3 py-3"
        >
          <p className="mb-2 font-mono text-2xs uppercase tracking-wider text-text-faint">
            // exportar para
          </p>
          <div className="flex flex-wrap gap-2">
            {EXPORT_TARGETS.map((t) => (
              <button
                key={t}
                type="button"
                role="menuitem"
                disabled={busy !== null}
                onClick={() => exportTo(t)}
                className={[
                  "inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 font-mono text-2xs uppercase tracking-wider transition-colors",
                  busy === t
                    ? "cursor-wait border-line bg-panel text-text-faint"
                    : busy !== null
                      ? "cursor-not-allowed border-line bg-panel text-text-faint opacity-60"
                      : "border-synapse/40 bg-synapse/10 text-synapse hover:bg-synapse/20",
                ].join(" ")}
              >
                {busy === t ? "exportando..." : EXPORT_TARGET_LABELS[t]}
              </button>
            ))}
          </div>
          <p className="mt-2 font-mono text-2xs text-text-faint">
            pacote portatil de 1 capacidade -- instrucoes + agent_card (A2A) + contrato de
            I/O. Nunca inventa dados: campos sem entrada viram [fornecer: ...].
          </p>
        </div>
      )}

      {error && (
        <div
          role="alert"
          className="mt-2 flex items-start gap-1.5 rounded-lg border border-danger/30 bg-danger/5 px-3 py-2 text-2xs text-danger"
        >
          <span className="mt-px shrink-0">
            <AlertIcon />
          </span>
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}

/** A small inline download glyph (avoids touching the shared icons pack). */
function DownloadGlyph() {
  return (
    <svg
      width="12"
      height="12"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </svg>
  );
}
