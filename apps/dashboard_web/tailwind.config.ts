import type { Config } from "tailwindcss";

/*
 * CEXAI Dashboard design tokens.
 *
 * Direction: "neural control surface" -- a sovereign-lab dark UI for a
 * technical operator, NOT a generic SaaS landing page. Boldness is spent in
 * ONE place: the 8F filament (the cyan plasma trace that fires F1..F8 when a
 * capability runs). Everything else is quiet graphite.
 *
 * Palette is named so intent is legible:
 *   ink      -- the deep base (the void the brain floats in)
 *   panel    -- raised surfaces (cards, rail)
 *   line     -- hairline borders
 *   synapse  -- the disciplined plasma accent (active filament + primary action)
 *   signal   -- amber, reserved for running/pending states
 *   text/mut -- foreground + muted foreground
 */
const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#0A0E14",
          800: "#0E141C",
          700: "#121821",
          600: "#161D27",
        },
        panel: {
          DEFAULT: "#121821",
          raised: "#161E29",
          sunken: "#0D131B",
        },
        line: {
          DEFAULT: "#1E2733",
          soft: "#19212B",
          strong: "#2A3543",
        },
        synapse: {
          // THE accent. CSS-var-driven so the admin's one accent reads as the
          // ACTIVE TENANT's brand (lib/adminTheme.ts injects :root{--accent}).
          // The fallback "171 77% 64%" is the EXACT current cyan (#5EEAD4 in HSL),
          // so with NO active tenant the value is never overridden -> byte-identical
          // default. The "/ <alpha-value>" form keeps every synapse/NN opacity
          // modifier (bg-synapse/10, border-synapse/30, ...) working unchanged.
          DEFAULT: "hsl(var(--accent, 171 77% 64%) / <alpha-value>)",
          bright: "#7DF1DE",
          deep: "#38BDF8",
          dim: "#2E5A55",
        },
        signal: {
          DEFAULT: "#F4B860",
          deep: "#E0973A",
        },
        danger: {
          DEFAULT: "#F77272",
          deep: "#D24F4F",
        },
        text: {
          DEFAULT: "#E6EDF3",
          muted: "#8B97A7",
          faint: "#5A6573",
        },
      },
      fontFamily: {
        display: ["var(--font-display)", "Space Grotesk", "system-ui", "sans-serif"],
        sans: ["var(--font-body)", "Inter", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "JetBrains Mono", "ui-monospace", "monospace"],
      },
      fontSize: {
        "2xs": ["0.6875rem", { lineHeight: "1rem", letterSpacing: "0.04em" }],
      },
      letterSpacing: {
        eyebrow: "0.22em",
      },
      borderRadius: {
        card: "14px",
        pill: "999px",
      },
      boxShadow: {
        panel: "0 1px 0 0 rgba(255,255,255,0.02) inset, 0 24px 48px -24px rgba(0,0,0,0.8)",
        glow: "0 0 0 1px rgba(94,234,212,0.35), 0 0 28px -4px rgba(94,234,212,0.45)",
        "glow-soft": "0 0 22px -6px rgba(94,234,212,0.35)",
      },
      backgroundImage: {
        "grid-faint":
          "linear-gradient(to right, rgba(255,255,255,0.025) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.025) 1px, transparent 1px)",
        "synapse-sheen":
          "linear-gradient(135deg, rgba(94,234,212,0.16) 0%, rgba(56,189,248,0.08) 45%, transparent 70%)",
      },
      backgroundSize: {
        grid: "44px 44px",
      },
      keyframes: {
        "filament-pulse": {
          "0%, 100%": { opacity: "0.35", transform: "scale(0.92)" },
          "50%": { opacity: "1", transform: "scale(1)" },
        },
        "filament-fire": {
          "0%": { opacity: "0.2", boxShadow: "0 0 0 0 rgba(94,234,212,0)" },
          "40%": { opacity: "1", boxShadow: "0 0 14px 2px rgba(94,234,212,0.6)" },
          "100%": { opacity: "0.55", boxShadow: "0 0 0 0 rgba(94,234,212,0)" },
        },
        "trace-sweep": {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(100%)" },
        },
        "rise-in": {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "pulse-dot": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.3" },
        },
        "spin-slow": {
          to: { transform: "rotate(360deg)" },
        },
      },
      animation: {
        "filament-pulse": "filament-pulse 1.6s ease-in-out infinite",
        "trace-sweep": "trace-sweep 1.8s ease-in-out infinite",
        "rise-in": "rise-in 0.5s cubic-bezier(0.22,1,0.36,1) both",
        "fade-in": "fade-in 0.4s ease both",
        "pulse-dot": "pulse-dot 1.2s ease-in-out infinite",
        "spin-slow": "spin-slow 1.1s linear infinite",
      },
    },
  },
  plugins: [],
};

export default config;
