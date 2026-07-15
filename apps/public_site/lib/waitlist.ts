// ----------------------------------------------------------------------------
// waitlist -- the GO_ONLINE A2 "modo-espera" (waitlist mode) client for
// /intake (spec cexai-specs/23_go_online/spec.md, User Story P1b + FR-003,
// tasks T200/T210/T211). Every /intake submission while the tenant is in
// waitlist mode lands ONE row in waitlist_intake (supabase/migrations/
// 20260711000001_waitlist_intake.sql) via this module.
//
// RLS POSTURE (the security contract this client is built around): anon
// INSERT-only, ZERO anon SELECT -- LGPD by design. A visitor can add
// themselves to the queue but can NEVER read it back, and can never see who
// else is on it. There is deliberately no getWaitlist()/listWaitlist() here --
// only the privileged service-role Postgres role can ever read this table
// (see the PROPOSAL comment on ApiClient.listWaitlist(),
// apps/dashboard_web/lib/api.ts).
//
// THE GATE IS LIGHT, NOT THE FULL brand_validate MIRROR (DECISIONS): only a
// valid-shaped email is required (EMAIL_LOOSE_PATTERN, reused verbatim from
// ./intake) -- everything else the visitor typed is best-effort and rides
// along as-is via buildAnswers(state), exactly like the "Baixar answers YAML"
// / "Resolver agora" paths already do.
//
// KNOWN GAP (flagged for N07, NOT this lane's fence to fix): next.config.mjs's
// Content-Security-Policy connect-src currently allow-lists ONLY 'self' + the
// FastAPI API origin ("there is NO Supabase origin in connect-src -- the
// public path has no auth", per that file's own header comment -- written
// before this module existed). A browser fetch from THIS module to the
// Supabase REST origin (https://<project>.supabase.co) will be BLOCKED by
// that CSP header in a production build unless connect-src is widened to
// include NEXT_PUBLIC_SUPABASE_URL's origin. apps/public_site/next.config.mjs
// is OUT OF THIS LANE'S HARD FENCE (GO_ONLINE A2 handoff lists only the files
// below) -- widening it is a one-line follow-up for N07/a future lane, not
// silently absorbed here. Unit tests below stub the Supabase client directly
// (jsdom does not enforce CSP), so this gap does NOT show up as a test
// failure -- only as a real blocked request in a deployed build.
//
// PURE + TOTAL where possible (isValidWaitlistEmail, buildWaitlistRow): never
// throws, never touches the network or the DOM. Only submitToWaitlist touches
// the network (one Supabase insert) -- its Supabase client is INJECTABLE (the
// tests pass a fake), and it is TOTAL: a missing config, a network failure, or
// an RLS/Postgres rejection all resolve { ok: false, error }, never throw.
// ASCII-only + diacritic-free (house style) -- new user-FACING copy for this
// feature lives in app/intake/page.tsx (accented, per DECISIONS), not here.
// ----------------------------------------------------------------------------

import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { EMAIL_LOOSE_PATTERN, buildAnswers, type IntakeState } from "@/lib/intake";

/** The table this client writes to (supabase/migrations/20260711000001_
 *  waitlist_intake.sql). anon may INSERT only -- see that migration's RLS. */
export const WAITLIST_TABLE = "waitlist_intake";

const SUPABASE_URL = (process.env.NEXT_PUBLIC_SUPABASE_URL || "").trim();
const SUPABASE_ANON_KEY = (process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "").trim();

/** True when both Supabase env vars are configured. Mirrors dashboard_web's
 *  hasSupabase() naming (apps/dashboard_web/lib/config.ts) -- same convention,
 *  a simpler (no-auth-mode) client: this form never authenticates anyone. */
export function hasWaitlistSupabase(): boolean {
  return Boolean(SUPABASE_URL && SUPABASE_ANON_KEY);
}

let _client: SupabaseClient | null = null;

/** The browser Supabase client, or null when unconfigured. Lazy + memoized,
 *  one per tab -- structural mirror of apps/dashboard_web/lib/supabase.ts's
 *  getSupabase(), simplified: anon-key only, no session persistence / auto
 *  refresh / URL session detection (this form never authenticates). */
export function getWaitlistSupabase(): SupabaseClient | null {
  if (!hasWaitlistSupabase()) return null;
  if (_client) return _client;
  _client = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    auth: { persistSession: false, autoRefreshToken: false, detectSessionInUrl: false },
  });
  return _client;
}

/** The light gate (DECISIONS: "not the full form gate, require ONLY a valid
 *  email"). Reuses EMAIL_LOOSE_PATTERN verbatim -- the SAME soft-warn shape
 *  check contact.email already uses elsewhere in this form, now used as a
 *  hard (blocking) gate for this ONE action only. PURE + TOTAL. */
export function isValidWaitlistEmail(email: string | null | undefined): boolean {
  return EMAIL_LOOSE_PATTERN.test((email ?? "").trim());
}

export interface WaitlistRow {
  email: string;
  /** audience.wtp_band -- the dashboard's sort key (T212). null when blank. */
  wtp_band: string | null;
  /** identity.brand_name -- best-effort display field. null when blank. */
  brand_name: string | null;
  /** The FULL buildAnswers(state) snapshot -- nothing typed elsewhere in the
   *  form is silently dropped, even though only email is required to submit. */
  answers: Record<string, unknown>;
}

/** Form state -> the insert row. Does NOT itself gate on email validity --
 *  callers check isValidWaitlistEmail(state["contact.email"]) first (the page
 *  decouples the button's disabled state from this pure builder). PURE +
 *  TOTAL: never throws, degrades every missing field to "" / null. */
export function buildWaitlistRow(state: IntakeState): WaitlistRow {
  const email = (state["contact.email"] ?? "").trim();
  const wtpBand = (state["audience.wtp_band"] ?? "").trim();
  const brandName = (state["identity.brand_name"] ?? "").trim();
  return {
    email,
    wtp_band: wtpBand || null,
    brand_name: brandName || null,
    // buildAnswers's return type is a plain nested-optional object (no
    // methods/class instances) -- safe to widen to Record<string, unknown> for
    // the jsonb column; the Supabase client JSON-serializes it either way.
    answers: buildAnswers(state) as unknown as Record<string, unknown>,
  };
}

export interface WaitlistSubmitResult {
  ok: boolean;
  /** Present only when ok === false. Never a secret / never a raw Postgres
   *  error object -- always a short, display-safe string. */
  error?: string;
}

/**
 * Insert one row into waitlist_intake. TOTAL: never throws -- a missing
 * config, an invalid email, a network failure, or a Postgres/RLS rejection
 * all resolve { ok: false, error }. `client` is injectable (unit tests pass a
 * fake implementing .from(table).insert(row) -- see __tests__/
 * waitlist.test.ts) and defaults to the lazy browser singleton.
 *
 * Deploy note (T213, documented -- never run by this build): the
 * notify_waitlist Edge Function (supabase/functions/notify_waitlist/index.ts)
 * is wired as a Database Webhook on THIS table's INSERT event, so a
 * successful call here also triggers a founder notification email once that
 * webhook is configured (`supabase functions deploy notify_waitlist`).
 */
export async function submitToWaitlist(
  row: WaitlistRow,
  client: SupabaseClient | null = getWaitlistSupabase(),
): Promise<WaitlistSubmitResult> {
  if (!client) {
    return {
      ok: false,
      error: "Supabase nao configurado (NEXT_PUBLIC_SUPABASE_URL / _ANON_KEY ausentes).",
    };
  }
  if (!isValidWaitlistEmail(row.email)) {
    return { ok: false, error: "e-mail invalido" };
  }
  try {
    const { error } = await client.from(WAITLIST_TABLE).insert({
      email: row.email.trim(),
      wtp_band: row.wtp_band,
      brand_name: row.brand_name,
      answers: row.answers,
    });
    if (error) {
      return { ok: false, error: error.message || "insert failed" };
    }
    return { ok: true };
  } catch (err) {
    return { ok: false, error: err instanceof Error ? err.message : String(err) };
  }
}
