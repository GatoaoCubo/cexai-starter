/** @type {import('next').NextConfig} */

// ----------------------------------------------------------------------------
// Security headers for the L2 PUBLIC SITE (spec 10 W1-frontend).
//
// MIRRORS apps/dashboard_web/next.config.mjs (CSP as a real HTTP RESPONSE
// HEADER, not a <meta> tag -- a meta CSP is applied late and cannot carry
// frame-ancestors). KEY DIFFERENCES vs the dashboard:
//   * this app is UNAUTHENTICATED and talks to ONE backend (the public API);
//     there is NO Supabase origin in connect-src (the public path has no auth).
//   * media here is TENANT-AUTHORED published content (img/video/audio), so the
//     media/img directives allow https: + data: (the same scheme allowlist the
//     client enforces in mediaSafety.isSafeMediaSrc).
//
// The public site is a PURE CLIENT of the FastAPI backend (apps/dashboard_api,
// /public/* routes): no server-side secrets, only NEXT_PUBLIC_* env. So the
// only outbound origin the policy must reach is the API, derived from the
// build-time env. When it is unset (a fixtures-only build that makes no network
// calls) connect-src degrades to 'self' -- never a broken page (degrade-never).
//
// KNOWN TRADEOFF (documented, mirrors the dashboard): script-src/style-src keep
// 'unsafe-inline' because the Next app-router injects inline bootstrap +
// hydration scripts and Tailwind/next inject inline styles. The directives that
// matter most are strict: frame-ancestors 'none' (clickjacking), object-src
// 'none', base-uri 'self', form-action 'self', and a bounded connect-src.
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

  // connect-src: self + the ONE backend we call (the public API). No Supabase
  // here -- the public path is unauthenticated.
  const connect = ["'self'"];
  if (apiOrigin) connect.push(apiOrigin);
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
    // tenant-authored published images: data: URIs + remote https: CDN refs.
    // (mediaSafety.isSafeMediaSrc gates the same scheme set on the client.)
    ["img-src", ["'self'", "data:", "https:"]],
    // tenant-authored published audio/video slots (data: URIs + https: refs).
    ["media-src", ["'self'", "data:", "https:"]],
    // the human_html iframe is a srcDoc doc under sandbox="" (no allow-scripts ->
    // scripts are blocked regardless of CSP); frame-src 'self' covers a srcDoc frame.
    ["frame-src", ["'self'"]],
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
  // dev keeps `.next`; production goes to `.next-prod` so `next build` can never
  // clobber a running `next dev`'s `.next` (mirrors the dashboard).
  distDir: isDev ? ".next" : ".next-prod",
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
