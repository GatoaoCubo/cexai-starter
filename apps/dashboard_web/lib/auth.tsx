"use client";

// ----------------------------------------------------------------------------
// Auth context. Single source of session truth for the app.
//
// DUAL-MODE, selected by config.authMode (env NEXT_PUBLIC_CEXAI_AUTH -- mission
// ADDAY1B, the dev-login-revert done as a CONFIG FLIP, not a code rewrite):
//
//   "dev"      -> a local stub session (FIXTURE_TENANT), any credentials pass.
//                 The LOCAL default; never a real deploy. (NEXT_PUBLIC_CEXAI_AUTH=dev)
//   "supabase" -> REAL Supabase email/password; tenant_id is read from the JWT
//                 (app_metadata.tenant_id) and is the ONLY identity gate -- the gato
//                 admin deploy path (JWT -> backend verify -> RLS). (=supabase)
//
// Going from local to the real gato admin is FLIPPING ONE ENV VAR (+ the Supabase
// url/anon-key envs) -- no code change here. The session carries access_token (the
// Bearer for ApiClient) and tenant_id. Nothing in the app sets tenant_id; it is
// derived here, once. authMode is independent of config.fixtures (the data-layer
// mocks flag) -- see lib/config.ts.
// ----------------------------------------------------------------------------

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { config } from "./config";
import { FIXTURE_TENANT } from "./fixtures";
import {
  getSupabase,
  tenantFromSession,
  tenantLabelFromSession,
} from "./supabase";
import type { SessionContext } from "./types";

interface AuthState {
  /** null = signed out; undefined = still resolving (initial load). */
  session: SessionContext | null | undefined;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  /** True when the local dev-login stub is active (authMode="dev"). The login page
   *  reads this for the demo-credential prefill + the "offline preview" hint. */
  fixtures: boolean;
}

const Ctx = createContext<AuthState | null>(null);

const STUB_TOKEN = "fixtures-stub-token";

/** True when the local dev-login stub is the active auth path (NEXT_PUBLIC_CEXAI_AUTH=dev
 *  or the legacy fixtures default). False => the real Supabase path runs. */
const devAuth = config.authMode === "dev";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<SessionContext | null | undefined>(
    undefined,
  );

  // --- bootstrap existing session --------------------------------------------
  useEffect(() => {
    let active = true;

    if (devAuth) {
      // Restore a stub session if the tab marked itself signed-in.
      const flagged =
        typeof window !== "undefined" &&
        window.localStorage.getItem("cexai_fx_signed_in") === "1";
      setSession(
        flagged
          ? {
              email: FIXTURE_TENANT.email,
              tenant_id: FIXTURE_TENANT.tenant_id,
              tenant_label: FIXTURE_TENANT.tenant_label,
              access_token: STUB_TOKEN,
            }
          : null,
      );
      return;
    }

    const sb = getSupabase();
    if (!sb) {
      setSession(null);
      return;
    }

    sb.auth.getSession().then(({ data }) => {
      if (!active) return;
      setSession(toContext(data.session));
    });

    const { data: sub } = sb.auth.onAuthStateChange((_event, s) => {
      setSession(toContext(s));
    });

    return () => {
      active = false;
      sub.subscription.unsubscribe();
    };
  }, []);

  const signIn = useCallback(async (email: string, password: string) => {
    if (devAuth) {
      if (!email || !password) {
        throw new Error("Enter any email and password to continue.");
      }
      if (typeof window !== "undefined") {
        window.localStorage.setItem("cexai_fx_signed_in", "1");
      }
      setSession({
        email,
        tenant_id: FIXTURE_TENANT.tenant_id,
        tenant_label: FIXTURE_TENANT.tenant_label,
        access_token: STUB_TOKEN,
      });
      return;
    }

    const sb = getSupabase();
    if (!sb) throw new Error("Auth is not configured. Set Supabase env vars.");
    const { data, error } = await sb.auth.signInWithPassword({ email, password });
    if (error) throw new Error(error.message);

    const ctx = toContext(data.session);
    if (ctx && !ctx.tenant_id) {
      // Authenticated but no tenant claim -> cannot scope. Fail closed.
      await sb.auth.signOut();
      throw new Error(
        "Your account has no tenant assigned. Contact your operator.",
      );
    }
    setSession(ctx);
  }, []);

  const signOut = useCallback(async () => {
    if (devAuth) {
      if (typeof window !== "undefined") {
        window.localStorage.removeItem("cexai_fx_signed_in");
      }
      setSession(null);
      return;
    }
    const sb = getSupabase();
    if (sb) await sb.auth.signOut();
    setSession(null);
  }, []);

  const value = useMemo<AuthState>(
    // `fixtures` here means "the auth is a local dev stub" (the login page uses it for
    // the demo-credential prefill + the offline hint) -- now driven by authMode, so the
    // login UX tracks the real auth path, not the data-layer mocks flag.
    () => ({ session, signIn, signOut, fixtures: devAuth }),
    [session, signIn, signOut],
  );

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useAuth must be used within <AuthProvider>.");
  return ctx;
}

// --- helpers -----------------------------------------------------------------

import type { Session } from "@supabase/supabase-js";

function toContext(session: Session | null): SessionContext | null {
  if (!session) return null;
  return {
    email: session.user?.email ?? "unknown",
    tenant_id: tenantFromSession(session),
    tenant_label: tenantLabelFromSession(session),
    access_token: session.access_token,
  };
}
