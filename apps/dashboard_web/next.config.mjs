/** @type {import('next').NextConfig} */

// ----------------------------------------------------------------------------
// Security headers (HARDEN mission, central-dashboard-hardening).
//
// The gato handoff flagged CSP-in-<meta> as an anti-pattern: a meta-tag CSP is
// applied late (after the parser has already seen earlier markup) and cannot
// carry frame-ancestors. We set the Content-Security-Policy as a real HTTP
// RESPONSE HEADER here (next runtime), which is the authoritative surface.
//
// This dashboard is a PURE CLIENT of the FastAPI backend (apps/dashboard_api):
// no server-side secrets, only NEXT_PUBLIC_* env. So the policy's only moving
// parts are the two outbound origins it must reach -- the API and Supabase --
// which we derive from the build-time env. When those are unset (e.g. a
// fixtures-only build that makes no network calls) connect-src degrades to
// 'self' -- never a broken page (degrade-never).
//
// KNOWN TRADEOFF (documented, not hidden): script-src/style-src keep
// 'unsafe-inline' because the Next app-router injects inline bootstrap +
// hydration scripts and Tailwind/next inject inline styles. A strict
// nonce-based CSP needs per-request middleware plumbing -- a larger change with
// real regression risk. The directives that matter most against the common
// attacks are already strict here: frame-ancestors 'none' (clickjacking),
// object-src 'none', base-uri 'self', form-action 'self', and a bounded
// connect-src/img-src (exfiltration surface). Tightening script-src to nonces
// is the documented follow-up.
// ----------------------------------------------------------------------------

const isDev = process.env.NODE_ENV !== "production";

/** Parse a URL string to its origin (scheme://host[:port]); null if unusable. */
function originOf(raw) {
  if (!raw) return null;
  try {
    return new URL(raw).origin;
  } catch {
    return null;
  }
}

/** Build the Content-Security-Policy value from the build-time env. */
function buildCsp() {
  const apiOrigin = originOf(process.env.NEXT_PUBLIC_API_URL);
  const supabaseOrigin = originOf(process.env.NEXT_PUBLIC_SUPABASE_URL);

  // connect-src: self + the two backends we actually call. Supabase realtime +
  // dev HMR ride websockets, so allow ws/wss to the same origins.
  const connect = ["'self'"];
  if (apiOrigin) connect.push(apiOrigin);
  if (supabaseOrigin) {
    connect.push(supabaseOrigin);
    connect.push(supabaseOrigin.replace(/^http/, "ws"));
  }
  if (isDev) connect.push("ws:");

  // script-src: 'unsafe-eval' is required by `next dev` (webpack eval); never
  // shipped to production.
  const script = ["'self'", "'unsafe-inline'"];
  if (isDev) script.push("'unsafe-eval'");

  const directives = [
    ["default-src", ["'self'"]],
    ["script-src", script],
    ["style-src", ["'self'", "'unsafe-inline'"]],
    // self-hosted next/font + the occasional data: font.
    ["font-src", ["'self'", "data:"]],
    // generated SVG data URIs, blob: upload previews, remote product images.
    ["img-src", ["'self'", "data:", "blob:", "https:"]],
    // audio/video result slots (generated data URIs + client blob previews).
    ["media-src", ["'self'", "data:", "blob:"]],
    ["connect-src", connect],
    ["worker-src", ["'self'", "blob:"]],
    ["manifest-src", ["'self'"]],
    ["base-uri", ["'self'"]],
    ["form-action", ["'self'"]],
    ["frame-ancestors", ["'none'"]],
    ["object-src", ["'none'"]],
  ];

  return directives.map(([name, values]) => `${name} ${values.join(" ")}`).join("; ");
}

const securityHeaders = [
  { key: "Content-Security-Policy", value: buildCsp() },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  {
    key: "Permissions-Policy",
    value: "camera=(), microphone=(), geolocation=()",
  },
];

const nextConfig = {
  reactStrictMode: true,
  // Build output dir: dev keeps `.next`; production (next build / next start)
  // goes to `.next-prod` so `next build` can never clobber a running
  // `next dev`'s `.next`. (build-guard, 2026-06-24)
  distDir: isDev ? ".next" : ".next-prod",
  // The dashboard is a pure client of the FastAPI backend (apps/dashboard_api).
  // No server-side secrets live here; the only env vars are NEXT_PUBLIC_*.
  experimental: {
    // keep the surface minimal -- no extra runtime
  },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: securityHeaders,
      },
    ];
  },
};

export default nextConfig;
