"use client";

// ----------------------------------------------------------------------------
// /onboard -- the DEV-ONLY operator front-door for URL-first onboarding (inc3).
//
// Paste a tenant SITE URL (+ an optional slug) -> POST /api/onboard -> the Python bootstrap
// generates + persists a tenant_config under .cex/tenants/<slug>/ and the loader refreshes
// the preview registry. We then render the manifest result HONESTLY:
//   * ok        -> a link to the preview (/t/<slug>) + the resolved brand name + where the
//                  config was written + the detected business shape.
//   * not ok    -> the manifest's own errors + next_steps (NO fabrication -- we show exactly
//                  what the bootstrap reported, including [preencher] markers verbatim).
// This is an operator/dev affordance; the route is the security boundary (the dev gate +
// scheme/slug guards live server-side). A client component is fine -- it only talks to the
// same-origin /api/onboard.
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import { useState } from "react";
import type { OnboardApiResponse } from "@/lib/onboard";

export default function OnboardPage() {
  const [url, setUrl] = useState("");
  const [slug, setSlug] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<OnboardApiResponse | null>(null);
  const [transportError, setTransportError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (loading) return;
    setLoading(true);
    setResult(null);
    setTransportError(null);
    try {
      const res = await fetch("/api/onboard", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ url: url.trim(), slug: slug.trim() || undefined }),
      });
      // The route ALWAYS returns a JSON body (ok branch and every error branch alike).
      const data = (await res.json()) as OnboardApiResponse;
      setResult(data);
    } catch (err) {
      setTransportError(
        "Falha de rede ao chamar /api/onboard: " +
          (err instanceof Error ? err.message : String(err)),
      );
    } finally {
      setLoading(false);
    }
  }

  const ok = result?.ok === true;
  const errors = result?.errors ?? [];
  const nextSteps = result?.next_steps ?? [];
  const shapeVertical =
    result?.business_shape && typeof result.business_shape === "object"
      ? String((result.business_shape as Record<string, unknown>).vertical ?? "")
      : "";

  return (
    <main id="main-content" className="min-h-screen px-5 py-12">
      <div className="mx-auto w-full max-w-2xl space-y-8">
        <header className="space-y-2">
          <p className="eyebrow">CEXAI . onboarding (DEV)</p>
          <h1 className="font-display text-h1 text-foreground">Onboard de um tenant por URL</h1>
          <p className="text-base leading-relaxed text-muted-foreground">
            Cole o endereco do site de um tenant. O pipeline extrai a marca, gera o
            tenant_config (gravado apenas em .cex/tenants/&lt;slug&gt;/, nunca no banco) e o
            preview de /t/&lt;slug&gt; passa a existir. Ferramenta DEV-ONLY.
          </p>
          <p className="text-sm text-muted-foreground">
            Prefere a entrevista completa (form_v1, R-149)?{" "}
            <a href="/intake" className="font-medium text-foreground underline">
              /intake
            </a>
          </p>
        </header>

        <form
          onSubmit={onSubmit}
          className="space-y-5 rounded-card border border-border bg-card p-8 shadow-md"
        >
          <div className="space-y-2">
            <label htmlFor="onboard-url" className="block text-sm font-medium text-foreground">
              URL do site
            </label>
            <input
              id="onboard-url"
              type="url"
              required
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://exemplo.com.br"
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-base text-foreground outline-none focus:border-primary"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="onboard-slug" className="block text-sm font-medium text-foreground">
              Slug (opcional)
            </label>
            <input
              id="onboard-slug"
              type="text"
              value={slug}
              onChange={(e) => setSlug(e.target.value)}
              placeholder="derivado do host se vazio (ex.: exemplo)"
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-base text-foreground outline-none focus:border-primary"
            />
            <p className="text-sm text-muted-foreground">
              Vazio -&gt; derivado do host (minusculo, ^[a-z0-9][a-z0-9_-]&#123;0,63&#125;$).
            </p>
          </div>

          <button
            type="submit"
            disabled={loading || !url.trim()}
            className="inline-flex items-center justify-center rounded-md bg-primary px-5 py-2.5 text-base font-medium text-primary-foreground shadow-sm transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Gerando tenant..." : "Gerar tenant"}
          </button>
        </form>

        {transportError && (
          <div className="rounded-card border border-destructive/40 bg-destructive/5 p-5 text-sm text-destructive">
            {transportError}
          </div>
        )}

        {result && (
          <section
            aria-live="polite"
            className="space-y-4 rounded-card border border-border bg-card p-8 shadow-md"
          >
            {ok ? (
              <>
                <div className="flex items-center gap-2">
                  <span className="inline-block rounded-md bg-primary/10 px-2 py-0.5 text-xs font-semibold uppercase tracking-wide text-primary">
                    Tenant gerado
                  </span>
                </div>
                <h2 className="font-display text-h2 text-foreground">
                  {result.brand?.name || "(sem nome -- preencher)"}
                </h2>
                {result.brand?.tagline && (
                  <p className="text-base text-muted-foreground">{result.brand.tagline}</p>
                )}
                <dl className="space-y-1 text-sm text-muted-foreground">
                  <div className="flex gap-2">
                    <dt className="font-medium text-foreground">tenant_id:</dt>
                    <dd>{result.tenant_id}</dd>
                  </div>
                  {shapeVertical && (
                    <div className="flex gap-2">
                      <dt className="font-medium text-foreground">business shape:</dt>
                      <dd>{shapeVertical}</dd>
                    </div>
                  )}
                  {result.tenant_config_persisted && result.tenant_config_path && (
                    <div className="flex gap-2">
                      <dt className="font-medium text-foreground">config:</dt>
                      <dd className="break-all font-mono text-xs">{result.tenant_config_path}</dd>
                    </div>
                  )}
                </dl>
                {result.previewPath && (
                  <a
                    href={result.previewPath}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 rounded-md bg-primary px-4 py-2 text-base font-medium text-primary-foreground shadow-sm transition hover:opacity-90"
                  >
                    Abrir preview {result.previewPath} -&gt;
                  </a>
                )}
                {/* Even on success the bootstrap may carry non-fatal notes as errors[] -- show them. */}
                {errors.length > 0 && (
                  <ul className="list-disc space-y-1 pl-5 text-sm text-muted-foreground">
                    {errors.map((msg, i) => (
                      <li key={i}>{msg}</li>
                    ))}
                  </ul>
                )}
              </>
            ) : (
              <>
                <div className="flex items-center gap-2">
                  <span className="inline-block rounded-md bg-destructive/10 px-2 py-0.5 text-xs font-semibold uppercase tracking-wide text-destructive">
                    Nao gerado
                  </span>
                </div>
                <h2 className="font-display text-h2 text-foreground">O bootstrap reportou erros</h2>
                {errors.length > 0 ? (
                  <ul className="list-disc space-y-1 pl-5 text-sm text-destructive">
                    {errors.map((msg, i) => (
                      <li key={i}>{msg}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-muted-foreground">
                    Sem detalhes de erro retornados.
                  </p>
                )}
                {nextSteps.length > 0 && (
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-foreground">Proximos passos:</p>
                    <ol className="list-decimal space-y-1 pl-5 text-sm text-muted-foreground">
                      {nextSteps.map((step, i) => (
                        <li key={i}>{step}</li>
                      ))}
                    </ol>
                  </div>
                )}
              </>
            )}
          </section>
        )}
      </div>
    </main>
  );
}
