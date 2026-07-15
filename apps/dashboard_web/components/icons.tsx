// ----------------------------------------------------------------------------
// Capability glyphs + brand mark. Hand-drawn line icons (currentColor, 1.6
// stroke) so they sit in the "systems instrument" aesthetic rather than a
// generic icon-pack look. Each capability maps to one glyph via iconFor().
// ----------------------------------------------------------------------------

import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement>;

const base = (props: IconProps) => ({
  width: 22,
  height: 22,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.6,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  ...props,
});

// Research (N01) -- an eye-over-aperture / scan.
export function ResearchIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <circle cx="11" cy="11" r="6" />
      <path d="M11 8.5v5M8.5 11h5" opacity="0.5" />
      <path d="m20 20-4.2-4.2" />
    </svg>
  );
}

// Ads / Copy (N02) -- a broadcast horn.
export function AdsIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M4 10v4l9 4V6l-9 4Z" />
      <path d="M13 8.5a3.5 3.5 0 0 1 0 7" opacity="0.6" />
      <path d="M4 14H3a1 1 0 0 1-1-1v-2a1 1 0 0 1 1-1h1" />
    </svg>
  );
}

// Media / Photo (N02) -- aperture blades.
export function MediaIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 3.5 8 12M20.5 12 12 8M12 20.5 16 12M3.5 12 12 16" opacity="0.7" />
    </svg>
  );
}

// Pricing (N06) -- a tier ladder / stacked value.
export function PricingIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M5 18h4v-4H5v4ZM10 18h4V9h-4v9ZM15 18h4V5h-4v13Z" />
    </svg>
  );
}

// Knowledge / Docs (N04) -- layered cards.
export function DocsIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <rect x="7" y="4" width="11" height="14" rx="1.5" />
      <path d="M5 7v11a1.5 1.5 0 0 0 1.5 1.5H15" opacity="0.6" />
      <path d="M10 8.5h5M10 11.5h5M10 14.5h3" opacity="0.7" />
    </svg>
  );
}

// Landing page (N03) -- a framed layout.
export function LandingIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <rect x="3.5" y="4.5" width="17" height="15" rx="1.5" />
      <path d="M3.5 9h17" />
      <path d="M7 13h6M7 16h4" opacity="0.7" />
      <circle cx="6" cy="6.7" r="0.6" fill="currentColor" stroke="none" />
    </svg>
  );
}

// Custom / overlay card -- a forked node (something the operator wired).
export function CustomIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <circle cx="6" cy="12" r="2" />
      <circle cx="18" cy="6.5" r="2" />
      <circle cx="18" cy="17.5" r="2" />
      <path d="M8 12 16 7M8 12l8 5" opacity="0.7" />
    </svg>
  );
}

// fallback
export function NodeIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <circle cx="12" cy="12" r="3" />
      <path d="M12 2v4M12 18v4M2 12h4M18 12h4" opacity="0.6" />
    </svg>
  );
}

// Table / dataset (generic managed entity).
export function TableIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <rect x="3.5" y="4.5" width="17" height="15" rx="1.5" />
      <path d="M3.5 9.5h17M3.5 14.5h17M9 9.5v10M15 9.5v10" opacity="0.7" />
    </svg>
  );
}

// Agent -- a standing node with an antenna (an autonomous worker, not a card).
export function AgentIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <rect x="5.5" y="9" width="13" height="9" rx="2" />
      <path d="M12 9V5.5M12 5.5a1.4 1.4 0 1 0 0-2.8 1.4 1.4 0 0 0 0 2.8Z" />
      <path d="M9.5 13h.01M14.5 13h.01" />
      <path d="M3.5 12.5v2M20.5 12.5v2" opacity="0.6" />
    </svg>
  );
}

// Crew -- a connected team of nodes (multi-role team, the layer above a single agent).
export function CrewIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <circle cx="12" cy="5.5" r="2.2" />
      <circle cx="5.5" cy="17" r="2.2" />
      <circle cx="18.5" cy="17" r="2.2" />
      <path d="M10.4 7.2 7 14.8M13.6 7.2 17 14.8M7.7 17h8.6" opacity="0.7" />
    </svg>
  );
}

const MAP: Record<string, (p: IconProps) => JSX.Element> = {
  research: ResearchIcon,
  ads: AdsIcon,
  media: MediaIcon,
  pricing: PricingIcon,
  docs: DocsIcon,
  landing: LandingIcon,
  custom: CustomIcon,
  table: TableIcon,
  agent: AgentIcon,
  crew: CrewIcon,
  // B2: the brandbook / brand-setup card uses the brand mark (the cubed-node glyph).
  brand: BrandMark,
};

// A nucleus -> capability-icon hint so an agent card can show a domain-appropriate
// glyph from its nucleus when it has no explicit icon key (read-only convenience).
const NUCLEUS_ICON: Record<string, string> = {
  N01: "research",
  N02: "ads",
  N03: "custom",
  N04: "docs",
  N05: "table",
  N06: "pricing",
  N07: "custom",
};

/** Resolve an icon for an agent by nucleus (falls back to the agent glyph). */
export function iconForNucleus(nucleus: string): (p: IconProps) => JSX.Element {
  const key = NUCLEUS_ICON[(nucleus || "").toUpperCase()];
  return key ? iconFor(key) : AgentIcon;
}

export function iconFor(key: string): (p: IconProps) => JSX.Element {
  return MAP[key] ?? NodeIcon;
}

// --- brand mark: a cubed node ("X" variable inside the brain) ----------------
export function BrandMark(props: IconProps) {
  return (
    <svg
      width={26}
      height={26}
      viewBox="0 0 32 32"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.7}
      strokeLinejoin="round"
      {...props}
    >
      {/* an isometric cube / the brain shell */}
      <path d="M16 3 28 9.5v13L16 29 4 22.5v-13L16 3Z" opacity="0.85" />
      <path d="M16 3v9M16 29v-9M16 16l12-6.5M16 16 4 9.5" opacity="0.35" />
      {/* the synapse at the core */}
      <circle cx="16" cy="16" r="2.4" fill="currentColor" stroke="none" />
    </svg>
  );
}

// Catalog -- a spec-sheet / quality-map (bullet list with a spine).
export function CatalogIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <rect x="4" y="3" width="16" height="18" rx="1.5" />
      <path d="M9 8h7M9 12h7M9 16h5" opacity="0.7" />
      <circle cx="6.5" cy="8" r="0.85" fill="currentColor" stroke="none" />
      <circle cx="6.5" cy="12" r="0.85" fill="currentColor" stroke="none" />
      <circle cx="6.5" cy="16" r="0.85" fill="currentColor" stroke="none" />
    </svg>
  );
}

// small utility glyphs
export function ArrowRight(props: IconProps) {
  return (
    <svg {...base({ width: 16, height: 16, ...props })}>
      <path d="M5 12h14M13 6l6 6-6 6" />
    </svg>
  );
}

export function CheckIcon(props: IconProps) {
  return (
    <svg {...base({ width: 16, height: 16, ...props })}>
      <path d="m5 12.5 4 4 10-10" />
    </svg>
  );
}

export function AlertIcon(props: IconProps) {
  return (
    <svg {...base({ width: 16, height: 16, ...props })}>
      <path d="M12 3 2 20h20L12 3Z" />
      <path d="M12 9v5M12 17h.01" />
    </svg>
  );
}

export function SignOutIcon(props: IconProps) {
  return (
    <svg {...base({ width: 16, height: 16, ...props })}>
      <path d="M9 4H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h3" />
      <path d="M15 8l4 4-4 4M19 12H9" />
    </svg>
  );
}

export function HistoryIcon(props: IconProps) {
  return (
    <svg {...base({ width: 16, height: 16, ...props })}>
      <path d="M3 12a9 9 0 1 0 3-6.7L3 8" />
      <path d="M3 4v4h4M12 8v4l3 2" />
    </svg>
  );
}

export function GridIcon(props: IconProps) {
  return (
    <svg {...base({ width: 16, height: 16, ...props })}>
      <rect x="3.5" y="3.5" width="7" height="7" rx="1" />
      <rect x="13.5" y="3.5" width="7" height="7" rx="1" />
      <rect x="3.5" y="13.5" width="7" height="7" rx="1" />
      <rect x="13.5" y="13.5" width="7" height="7" rx="1" />
    </svg>
  );
}

export function HomeIcon(props: IconProps) {
  return (
    <svg {...base({ width: 16, height: 16, ...props })}>
      <path d="M4 11 12 4l8 7" />
      <path d="M6 9.5V19a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V9.5" />
      <path d="M10 20v-5h4v5" opacity="0.7" />
    </svg>
  );
}

export function SettingsIcon(props: IconProps) {
  return (
    <svg {...base({ width: 16, height: 16, ...props })}>
      <circle cx="12" cy="12" r="3" />
      <path d="M12 2.5v3M12 18.5v3M21.5 12h-3M5.5 12h-3M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1M18.4 18.4l-2.1-2.1M7.7 7.7 5.6 5.6" opacity="0.7" />
    </svg>
  );
}

export function PlusIcon(props: IconProps) {
  return (
    <svg {...base({ width: 16, height: 16, ...props })}>
      <path d="M12 5v14M5 12h14" />
    </svg>
  );
}

export function TrashIcon(props: IconProps) {
  return (
    <svg {...base({ width: 16, height: 16, ...props })}>
      <path d="M4 7h16M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2" />
      <path d="M6 7v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V7" />
      <path d="M10 11v6M14 11v6" opacity="0.7" />
    </svg>
  );
}

export function PencilIcon(props: IconProps) {
  return (
    <svg {...base({ width: 16, height: 16, ...props })}>
      <path d="M4 20h4L19 9a2 2 0 0 0-3-3L5 16v4Z" />
      <path d="M14.5 6.5 17.5 9.5" opacity="0.7" />
    </svg>
  );
}

export function PlugIcon(props: IconProps) {
  return (
    <svg {...base({ width: 16, height: 16, ...props })}>
      <path d="M9 2v5M15 2v5" />
      <path d="M6 7h12v3a6 6 0 0 1-12 0V7Z" />
      <path d="M12 16v6" opacity="0.7" />
    </svg>
  );
}

export function KeyIcon(props: IconProps) {
  return (
    <svg {...base({ width: 16, height: 16, ...props })}>
      <circle cx="8" cy="8" r="4.5" />
      <path d="M11.2 11.2 20 20M16 16l2-2M18 18l2-2" opacity="0.85" />
    </svg>
  );
}

export function PulseIcon(props: IconProps) {
  return (
    <svg {...base({ width: 16, height: 16, ...props })}>
      <path d="M3 12h4l2-6 4 12 2-6h6" />
    </svg>
  );
}

export function RefreshIcon(props: IconProps) {
  return (
    <svg {...base({ width: 16, height: 16, ...props })}>
      <path d="M3 12a9 9 0 0 1 15-6.7L21 8" />
      <path d="M21 3v5h-5" />
      <path d="M21 12a9 9 0 0 1-15 6.7L3 16" opacity="0.7" />
      <path d="M3 21v-5h5" opacity="0.7" />
    </svg>
  );
}

export function LockIcon(props: IconProps) {
  return (
    <svg {...base({ width: 16, height: 16, ...props })}>
      <rect x="5" y="10.5" width="14" height="9" rx="1.5" />
      <path d="M8 10.5V8a4 4 0 0 1 8 0v2.5" />
      <circle cx="12" cy="15" r="1" fill="currentColor" stroke="none" />
    </svg>
  );
}
