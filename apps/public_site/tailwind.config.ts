import type { Config } from "tailwindcss";

/*
 * CEXAI Public Site -- WHITE-LABEL STOREFRONT design system.
 *
 * This config IMPLEMENTS the reference retail storefront design_system.md contract:
 * refined PB-minimal -- black/white base + a VIOLET brand accent + AMBER highlight, a
 * SEMANTIC TYPE SCALE with negative tracking on headings, an 8px spacing ladder, and the
 * motion + a11y baseline.
 *
 * EVERY color resolves from a CSS custom property (the 24 BRAND-VARIABLE tokens +
 * the system-level status/gradient/shadow tokens). globals.css ships the built-in sample
 * values as the static :root default (no FOUC); BrandLayout injects buildCssVars(brand) ON TOP
 * at runtime, so the WHOLE multi-page site re-skins from ONE brand object -- the mold.
 *
 * tokenVar() maps a CSS var (an "H S% L%" triplet) to a Tailwind color that supports the
 * opacity modifier (<alpha-value>). The fallback keeps the neutral look when no brand is
 * injected (degrade-never).
 *
 * BACKWARD-COMPAT: the legacy neutral aliases (ink / panel / line / text / synapse /
 * signal / danger) are retained so any not-yet-migrated surface keeps compiling. New work
 * uses the semantic token names (background / foreground / brand / highlight / muted ...).
 */

// Map a CSS var (an "H S% L%" triplet) -> an hsl() Tailwind color with opacity support.
const tokenVar = (name: string, fallbackHsl: string) =>
  `hsl(var(${name}, ${fallbackHsl}) / <alpha-value>)`;

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
        // ---- the 24 BRAND-VARIABLE tokens (design_system.md s1) -----------------
        // These resolve to the tenant's injected --x at runtime; the fallback is the
        // built-in sample default so the no-tenant look is the sample PB-minimal look.
        background: tokenVar("--background", "0 0% 100%"),
        foreground: tokenVar("--foreground", "0 0% 4%"),
        card: {
          DEFAULT: tokenVar("--card", "0 0% 100%"),
          foreground: tokenVar("--card-foreground", "0 0% 4%"),
        },
        popover: {
          DEFAULT: tokenVar("--popover", "0 0% 100%"),
          foreground: tokenVar("--popover-foreground", "0 0% 4%"),
        },
        primary: {
          DEFAULT: tokenVar("--primary", "0 0% 7%"),
          foreground: tokenVar("--primary-foreground", "0 0% 100%"),
        },
        secondary: {
          DEFAULT: tokenVar("--secondary", "0 0% 96%"),
          foreground: tokenVar("--secondary-foreground", "0 0% 7%"),
        },
        muted: {
          DEFAULT: tokenVar("--muted", "0 0% 96%"),
          foreground: tokenVar("--muted-foreground", "0 0% 38%"),
        },
        accent: {
          DEFAULT: tokenVar("--accent", "0 0% 7%"),
          foreground: tokenVar("--accent-foreground", "0 0% 100%"),
        },
        border: tokenVar("--border", "0 0% 90%"),
        input: tokenVar("--input", "0 0% 90%"),
        ring: tokenVar("--ring", "0 0% 4%"),
        // brand (teal) = brand identity / primary action ONLY (accent discipline).
        brand: {
          DEFAULT: tokenVar("--brand", "173 58% 39%"),
          foreground: tokenVar("--brand-foreground", "0 0% 100%"),
          muted: tokenVar("--brand-muted", "173 41% 95%"),
        },
        // highlight (orange) = promo / urgency ONLY (never on the same surface as brand).
        highlight: {
          DEFAULT: tokenVar("--highlight", "24 95% 53%"),
          foreground: tokenVar("--highlight-foreground", "0 0% 100%"),
          muted: tokenVar("--highlight-muted", "33 100% 96%"),
        },

        // ---- SYSTEM-LEVEL status tokens (design_system.md s1, every tenant inherits) --
        success: tokenVar("--success", "142 76% 36%"),
        warning: tokenVar("--warning", "38 92% 50%"),
        info: tokenVar("--info", "199 89% 48%"),
        destructive: tokenVar("--destructive", "0 84% 60%"),

        // ---- LEGACY neutral aliases (back-compat; not-yet-migrated surfaces) ---------
        ink: { DEFAULT: "#0A0E14", 800: "#0E141C", 700: "#121821", 600: "#161D27" },
        panel: { DEFAULT: "#121821", raised: "#161E29", sunken: "#0D131B" },
        line: { DEFAULT: "#1E2733", soft: "#19212B", strong: "#2A3543" },
        synapse: { DEFAULT: "#5EEAD4", bright: "#7DF1DE", deep: "#38BDF8", dim: "#2E5A55" },
        signal: { DEFAULT: "#F4B860", deep: "#E0973A" },
        danger: { DEFAULT: "#F77272", deep: "#D24F4F" },
        text: { DEFAULT: "#E6EDF3", muted: "#8B97A7", faint: "#5A6573" },
      },

      fontFamily: {
        // brand-variable base font (--font-family-base injected by buildCssVars); the
        // next/font CSS vars are the static fallback.
        sans: [
          "var(--font-family-base)",
          "var(--font-body)",
          "Inter",
          "system-ui",
          "sans-serif",
        ],
        display: [
          "var(--font-family-base)",
          "var(--font-display)",
          "Inter",
          "system-ui",
          "sans-serif",
        ],
        mono: ["var(--font-mono)", "JetBrains Mono", "ui-monospace", "monospace"],
      },

      // ---- the SEMANTIC TYPE SCALE (design_system.md s3) ------------------------
      // clamp() sizes + negative tracking on display/h1/h2 = the premium feel.
      fontSize: {
        display: [
          "clamp(2rem, 5vw, 4rem)",
          { lineHeight: "1.2", letterSpacing: "-0.025em", fontWeight: "800" },
        ],
        h1: [
          "clamp(1.75rem, 4vw, 3rem)",
          { lineHeight: "1.2", letterSpacing: "-0.025em", fontWeight: "700" },
        ],
        h2: [
          "clamp(1.5rem, 3vw, 2.25rem)",
          { lineHeight: "1.2", letterSpacing: "-0.025em", fontWeight: "600" },
        ],
        h3: [
          "clamp(1.25rem, 2vw, 1.75rem)",
          { lineHeight: "1.5", letterSpacing: "0", fontWeight: "600" },
        ],
        eyebrow: ["0.75rem", { lineHeight: "1", letterSpacing: "0.1em" }],
        base: ["clamp(0.875rem, 1vw, 1rem)", { lineHeight: "1.5" }],
        lg: ["clamp(1rem, 1.5vw, 1.125rem)", { lineHeight: "1.5" }],
        sm: ["clamp(0.75rem, 0.875vw, 0.875rem)", { lineHeight: "1.5" }],
        "2xs": ["0.6875rem", { lineHeight: "1rem", letterSpacing: "0.04em" }],
      },

      letterSpacing: {
        tight: "-0.025em",
        wide: "0.025em",
        eyebrow: "0.1em",
      },
      lineHeight: { tight: "1.2", normal: "1.5", relaxed: "1.75" },

      borderRadius: {
        // brand-variable radius -- the tenant's --radius (built-in sample default 0.75rem).
        DEFAULT: "var(--radius, 0.75rem)",
        card: "var(--radius, 0.75rem)",
        lg: "var(--radius, 0.75rem)",
        md: "calc(var(--radius, 0.75rem) - 0.25rem)",
        sm: "calc(var(--radius, 0.75rem) - 0.4rem)",
        pill: "999px",
      },

      boxShadow: {
        sm: "0 1px 2px rgb(0 0 0 / 0.05)",
        md: "0 1px 2px rgb(0 0 0 / 0.06), 0 8px 24px rgb(0 0 0 / 0.08)",
        lg: "0 4px 6px rgb(0 0 0 / 0.08), 0 20px 36px rgb(0 0 0 / 0.12)",
        xl: "0 8px 12px rgb(0 0 0 / 0.10), 0 32px 64px rgb(0 0 0 / 0.18)",
        // legacy alias used by not-yet-migrated surfaces
        panel: "0 1px 2px rgb(0 0 0 / 0.06), 0 8px 24px rgb(0 0 0 / 0.08)",
      },

      transitionDuration: { fast: "120ms", base: "200ms", slow: "300ms" },
      transitionTimingFunction: {
        emphasized: "cubic-bezier(0.16, 1, 0.3, 1)",
        standard: "cubic-bezier(0.4, 0, 0.2, 1)",
      },

      backgroundImage: {
        "gradient-brand":
          "linear-gradient(135deg, hsl(var(--brand, 173 58% 39%)), hsl(var(--brand, 173 58% 50%)))",
      },

      keyframes: {
        "fade-in": { "0%": { opacity: "0" }, "100%": { opacity: "1" } },
        "fade-in-up": {
          "0%": { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "scale-in": {
          "0%": { opacity: "0", transform: "scale(0.97)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.4s cubic-bezier(0.16,1,0.3,1) both",
        "fade-in-up": "fade-in-up 0.7s cubic-bezier(0.16,1,0.3,1) both",
        "scale-in": "scale-in 0.3s cubic-bezier(0.16,1,0.3,1) both",
      },
    },
  },
  plugins: [],
};

export default config;
