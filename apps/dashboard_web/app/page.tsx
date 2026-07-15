"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { Wordmark } from "@/components/ui";

/**
 * Entry route. Resolves the session, then routes:
 *   signed in  -> /dashboard
 *   signed out -> /login
 * Shows a quiet boot state while the session resolves.
 */
export default function Home() {
  const { session } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (session === undefined) return; // still resolving
    router.replace(session ? "/dashboard" : "/login");
  }, [session, router]);

  return (
    <main className="grid min-h-screen place-items-center">
      <div className="flex flex-col items-center gap-5 animate-fade-in">
        <div className="animate-filament-pulse">
          <Wordmark />
        </div>
        <p className="font-mono text-2xs uppercase tracking-eyebrow text-text-faint">
          initializing console
        </p>
      </div>
    </main>
  );
}
