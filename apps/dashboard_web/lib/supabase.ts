// ----------------------------------------------------------------------------
// Supabase Auth client (browser singleton) + tenant extraction.
//
// Identity rule (spec B.3 INVARIANTS): the tenant_id comes ONLY from the
// session JWT under app_metadata.tenant_id. The client never sets it. This
// module is the single place that reads it, so the rest of the app cannot drift.
// ----------------------------------------------------------------------------

import {
  createClient,
  type Session,
  type SupabaseClient,
} from "@supabase/supabase-js";
import { config, hasSupabase } from "./config";

let _client: SupabaseClient | null = null;

/**
 * The browser Supabase client, or null in fixtures mode / when unconfigured.
 * Lazy + memoized so it is created once per tab.
 */
export function getSupabase(): SupabaseClient | null {
  if (!hasSupabase()) return null;
  if (_client) return _client;
  _client = createClient(config.supabaseUrl, config.supabaseAnonKey, {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true,
    },
  });
  return _client;
}

/**
 * Pull the tenant_id from a Supabase session.
 * Precedence mirrors the data-plane coalesce (spec 0b): app_metadata.tenant_id
 * is the end-user JWT claim (branch 2). We read defensively in case the claim
 * is nested under a custom claims object.
 */
export function tenantFromSession(session: Session | null): string {
  if (!session) return "";
  const user = session.user;
  const appMeta = (user?.app_metadata ?? {}) as Record<string, unknown>;
  const direct = appMeta["tenant_id"];
  if (typeof direct === "string" && direct.length > 0) return direct;

  // Some setups stamp it inside a `claims` sub-object.
  const claims = appMeta["claims"];
  if (claims && typeof claims === "object") {
    const nested = (claims as Record<string, unknown>)["tenant_id"];
    if (typeof nested === "string" && nested.length > 0) return nested;
  }
  return "";
}

/** Optional human label for the tenant, if the auth layer provides one. */
export function tenantLabelFromSession(session: Session | null): string | undefined {
  if (!session) return undefined;
  const appMeta = (session.user?.app_metadata ?? {}) as Record<string, unknown>;
  const label = appMeta["tenant_label"] ?? appMeta["tenant_name"];
  return typeof label === "string" && label.length > 0 ? label : undefined;
}
