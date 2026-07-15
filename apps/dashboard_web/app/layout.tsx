import type { Metadata, Viewport } from "next";
import { Suspense } from "react";
import { Space_Grotesk, Inter, JetBrains_Mono } from "next/font/google";
import { AuthProvider } from "@/lib/auth";
import { resolveAdminTheme, buildAccentRootStyle } from "@/lib/adminTheme";
import { TenantThemeProvider } from "@/components/TenantTheme";
import "./globals.css";

const display = Space_Grotesk({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-display",
  display: "swap",
});

const body = Inter({
  subsets: ["latin"],
  variable: "--font-body",
  display: "swap",
});

const mono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Sua Empresa -- Capability Console",
  description:
    "The AI brain for your company. Run typed capabilities, land results in your own data plane.",
};

export const viewport: Viewport = {
  themeColor: "#0A0E14",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Per-tenant ACCENT injection (an active-tenant admin theme example). The SERVER paint stays
  // BUILD-TIME (config.activeTenant = NEXT_PUBLIC_TENANT): for an active env tenant we
  // emit ONLY a shape-guarded :root{--accent: <on-dark brand triplet>} -- the one accent
  // the dark-lab admin reads through (tailwind synapse.DEFAULT); for the default (no env
  // tenant) accentStyle is "" -> nothing injected, the tailwind cyan fallback stands ->
  // byte-identical. The RUNTIME ?tenant override (admin runtime-tenant) is layered on top
  // by <TenantThemeProvider> below -- it ONLY mutates --accent when ?tenant resolves to a
  // known tenant, so the absent/invalid/unknown case keeps this server paint untouched.
  const adminTheme = resolveAdminTheme();
  const accentStyle = buildAccentRootStyle(adminTheme);

  return (
    <html
      lang="en"
      className={`${display.variable} ${body.variable} ${mono.variable}`}
      suppressHydrationWarning
    >
      <head>
        {accentStyle ? (
          // Only the shape-guarded accent triplet text reaches this <style>;
          // no auth/data, no new injection sink.
          <style id="cexai-tenant-accent">{accentStyle}</style>
        ) : null}
      </head>
      <body>
        {/* TenantThemeProvider reads ?tenant via useSearchParams (Client hook) -> a
            Suspense boundary keeps Next from de-opting static routes to CSR. It drives
            the RUNTIME admin theme + the preview brand (Wordmark) ONLY; the data tenant
            stays auth/RLS-bound inside AuthProvider. */}
        <Suspense fallback={null}>
          <TenantThemeProvider>
            <AuthProvider>{children}</AuthProvider>
          </TenantThemeProvider>
        </Suspense>
      </body>
    </html>
  );
}
