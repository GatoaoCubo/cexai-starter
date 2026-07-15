import type { Metadata, Viewport } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

// ----------------------------------------------------------------------------
// Root layout for the L2 PUBLIC SITE. UNAUTHENTICATED (no AuthProvider, no JWT).
//
// FONTS: Inter is the built-in sample brand default (design_system.md: --font-family-base =
// 'Inter'). It backs both --font-body (the base font) and --font-display (the
// storefront uses Inter for headings too -- the premium feel comes from the negative
// tracking + the type scale, not a separate display face). A tenant can override the
// base font at runtime via buildCssVars (--font-family-base). JetBrains Mono backs the
// occasional mono device (eyebrow code marks).
// ----------------------------------------------------------------------------

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
  title: "Catalogo publico -- Sua Empresa",
  description:
    "Vitrine publica do catalogo de um tenant Sua Empresa. Somente itens publicados sao visiveis -- nenhum login e necessario.",
};

export const viewport: Viewport = {
  themeColor: "#ffffff",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="pt-br"
      className={`${body.variable} ${mono.variable}`}
      suppressHydrationWarning
    >
      <body>
        {/* Skip link -- off-screen until focused; targets the page main content (a11y). */}
        <a href="#main-content" className="skip-link">
          Ir para o conteudo
        </a>
        {children}
      </body>
    </html>
  );
}
