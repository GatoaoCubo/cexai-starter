"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { config } from "@/lib/config";
import { Wordmark } from "@/components/ui";
import { AlertIcon, ArrowRight } from "@/components/icons";
import { FilamentTrace } from "@/components/FilamentTrace";

export default function LoginPage() {
  const { session, signIn, fixtures } = useAuth();
  const router = useRouter();

  const [email, setEmail] = useState(fixtures ? "operator@demo.local" : "");
  const [password, setPassword] = useState(fixtures ? "demo" : "");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  // Already signed in? Bounce to the console.
  useEffect(() => {
    if (session) router.replace("/dashboard");
  }, [session, router]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await signIn(email.trim(), password);
      router.replace("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign-in failed.");
      setBusy(false);
    }
  }

  return (
    <main className="grid min-h-screen grid-cols-1 lg:grid-cols-[1.1fr_1fr]">
      {/* ---- Left: the thesis panel (the brain identity) ------------------- */}
      <section className="relative hidden overflow-hidden border-r border-line lg:flex lg:flex-col lg:justify-between lg:p-12">
        <div className="absolute inset-0 bg-synapse-sheen opacity-60" />
        <div
          className="absolute inset-0 opacity-[0.5]"
          style={{
            backgroundImage:
              "radial-gradient(circle at 1px 1px, rgba(94,234,212,0.12) 1px, transparent 0)",
            backgroundSize: "26px 26px",
          }}
        />

        <div className="relative z-10">
          <Wordmark />
        </div>

        <div className="relative z-10 max-w-xl animate-rise-in">
          <p className="eyebrow mb-5">The AI brain for your company</p>
          <h1 className="font-display text-5xl font-600 leading-[1.05] tracking-tight text-text">
            Every task becomes a{" "}
            <span className="text-synapse">typed asset</span>.
          </h1>
          <p className="mt-6 max-w-md text-text-muted">
            Run a capability and the 8-function pipeline does the work you
            can&apos;t -- constrain, inject, reason, produce, govern. The result
            lands in your own data plane, owned by you.
          </p>

          <div className="mt-12 max-w-md">
            <FilamentTrace progress={0.62} />
          </div>
        </div>

        <div className="relative z-10 flex items-center gap-6 font-mono text-2xs uppercase tracking-wider text-text-faint">
          <span>Composable</span>
          <span className="h-1 w-1 rounded-full bg-line-strong" />
          <span>Sovereign</span>
          <span className="h-1 w-1 rounded-full bg-line-strong" />
          <span>Self-assimilating</span>
        </div>
      </section>

      {/* ---- Right: the disciplined sign-in form --------------------------- */}
      <section className="flex flex-col justify-center px-6 py-12 sm:px-12">
        <div className="mx-auto w-full max-w-sm">
          <div className="mb-8 lg:hidden">
            <Wordmark />
          </div>

          <p className="eyebrow mb-3">Employee access</p>
          <h2 className="font-display text-2xl font-600 tracking-tight text-text">
            Sign in to your console
          </h2>
          <p className="mt-2 text-sm text-text-muted">
            Identity and tenant come from your account. You never pick a tenant.
          </p>

          {fixtures && (
            <div className="mt-5 rounded-lg border border-signal/25 bg-signal/5 px-3.5 py-2.5 text-xs text-signal">
              <span className="font-mono uppercase tracking-wider">
                Fixtures mode
              </span>{" "}
              -- any email + password signs in. No backend required.
            </div>
          )}

          <form onSubmit={onSubmit} className="mt-7 space-y-4" noValidate>
            <div>
              <label
                htmlFor="email"
                className="mb-1.5 block font-mono text-2xs uppercase tracking-wider text-text-muted"
              >
                Email
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="field"
                placeholder="you@company.com"
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="mb-1.5 block font-mono text-2xs uppercase tracking-wider text-text-muted"
              >
                Password
              </label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="field"
                placeholder="********"
              />
            </div>

            {error && (
              <div
                role="alert"
                className="flex items-start gap-2 rounded-lg border border-danger/30 bg-danger/5 px-3.5 py-2.5 text-sm text-danger"
              >
                <span className="mt-0.5 shrink-0">
                  <AlertIcon />
                </span>
                <span>{error}</span>
              </div>
            )}

            <button type="submit" className="btn-primary w-full" disabled={busy}>
              {busy ? "Signing in..." : "Enter console"}
              {!busy && <ArrowRight />}
            </button>
          </form>

          <p className="mt-8 font-mono text-2xs text-text-faint">
            {config.brandName} runtime
            {fixtures ? " -- offline preview" : " -- secured by Supabase Auth"}
          </p>
        </div>
      </section>
    </main>
  );
}
