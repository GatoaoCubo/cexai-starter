// ----------------------------------------------------------------------------
// NotFound -- the NO-LEAK "not found" view. SERVER-SAFE presentational.
//
// THE no-leak contract (the security keystone, client half): an unknown slug, a
// non-public slug, a malformed slug/kind, AND a missing detail id ALL render THIS
// SAME view. It NEVER discloses whether a tenant exists or whether a slug is merely
// private -- they are indistinguishable, exactly as the backend's 404
// public_not_found is indistinguishable (apps/dashboard_api/public_routes.py).
//
// So this view says nothing tenant-specific: no "tenant X is private", no slug
// echo that would confirm a guess. Just a neutral "nada por aqui".
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import Link from "next/link";

export function NotFound({
  message,
}: {
  /** an OPTIONAL neutral sub-message (e.g. "este item nao existe"). MUST NOT reveal
   *  tenant existence/visibility -- keep it generic. */
  message?: string;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center px-5">
      <div className="w-full max-w-md space-y-4 rounded-card border border-border bg-card p-10 text-center shadow-md">
        <p className="eyebrow">404</p>
        <h1 className="font-display text-h1 text-foreground">Nada por aqui</h1>
        <p className="text-base text-muted-foreground">
          {message ?? "Este endereco nao corresponde a um catalogo publico."}
        </p>
        <div className="pt-2">
          <Link href="/" className="btn-outline">
            Voltar ao inicio
          </Link>
        </div>
      </div>
    </div>
  );
}
