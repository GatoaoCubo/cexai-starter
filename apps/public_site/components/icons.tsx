// Minimal inline SVG icons for the public site (subset of the dashboard's icons).
// Stroke-based, currentColor, sized by props. ASCII-only.

interface IconProps {
  width?: number;
  height?: number;
  className?: string;
}

function base(props: IconProps) {
  return {
    width: props.width ?? 16,
    height: props.height ?? 16,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.8,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    className: props.className,
  };
}

export function CheckIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M20 6 9 17l-5-5" />
    </svg>
  );
}

export function AlertIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z" />
      <line x1="12" y1="9" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  );
}

export function TableIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <rect x="3" y="3" width="18" height="18" rx="2" />
      <path d="M3 9h18M3 15h18M9 3v18M15 3v18" />
    </svg>
  );
}

export function ArrowRightIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M5 12h14M13 6l6 6-6 6" />
    </svg>
  );
}

export function CatIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M12 5 8.5 3v3.5M12 5l3.5-2v3.5" />
      <path d="M5.5 9.5C5.5 6.5 8.4 5 12 5s6.5 1.5 6.5 4.5V14a4.5 4.5 0 0 1-4.5 4.5h-4A4.5 4.5 0 0 1 5.5 14Z" />
      <path d="M9.5 11h.01M14.5 11h.01" />
      <path d="M12 13v1.5M10.5 15.5h3" />
    </svg>
  );
}

export function ClockIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3 2" />
    </svg>
  );
}

export function CalendarIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <rect x="3" y="4" width="18" height="17" rx="2" />
      <path d="M3 9h18M8 2v4M16 2v4" />
    </svg>
  );
}

export function ShieldIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M12 3 5 6v5c0 4.5 3 7.5 7 9 4-1.5 7-4.5 7-9V6Z" />
      <path d="m9.5 12 1.8 1.8L15 10" />
    </svg>
  );
}

export function PixIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M12 3.5 20.5 12 12 20.5 3.5 12Z" />
      <path d="M8 8l4 4 4-4M8 16l4-4 4 4" />
    </svg>
  );
}

export function CardIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <rect x="2.5" y="5" width="19" height="14" rx="2" />
      <path d="M2.5 9.5h19M6 15h4" />
    </svg>
  );
}

export function RefreshIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M21 12a9 9 0 1 1-2.6-6.4M21 4v4h-4" />
    </svg>
  );
}

export function MapPinIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M12 21s-7-5.2-7-11a7 7 0 0 1 14 0c0 5.8-7 11-7 11Z" />
      <circle cx="12" cy="10" r="2.5" />
    </svg>
  );
}

/** A SOLID star -- filled with currentColor (so the parent text color drives it).
 *  Used for the monochrome rating row; partial fill is done by the caller via an
 *  overflow-clip width wrapper, not by this glyph. */
export function StarIcon(props: IconProps) {
  return (
    <svg
      width={props.width ?? 16}
      height={props.height ?? 16}
      viewBox="0 0 24 24"
      fill="currentColor"
      stroke="none"
      className={props.className}
      aria-hidden="true"
    >
      <path d="M12 2.5l2.9 5.88 6.49.94-4.7 4.58 1.11 6.46L12 17.3l-5.8 3.06 1.1-6.46-4.69-4.58 6.49-.94L12 2.5Z" />
    </svg>
  );
}

export function SparkleIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M12 3v4M12 17v4M3 12h4M17 12h4" />
      <path d="M12 8c.6 2.4 1.6 3.4 4 4-2.4.6-3.4 1.6-4 4-.6-2.4-1.6-3.4-4-4 2.4-.6 3.4-1.6 4-4Z" />
    </svg>
  );
}

/** A brand-NEUTRAL "feito com cuidado" glyph (an outline heart). White-label safe -- it
 *  carries no vertical (no cat-face), so it is the default 3rd home pillar for any tenant. */
export function HeartIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M12 20s-7-4.4-9.3-9A4.7 4.7 0 0 1 12 6.5 4.7 4.7 0 0 1 21.3 11C19 15.6 12 20 12 20Z" />
    </svg>
  );
}

/** A support / atendimento glyph (a headset) -- the 2nd home pillar for a SERVICES tenant
 *  (an honest "atendimento humanizado" claim, never a checkout/PIX claim). */
export function HeadsetIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M4 13v-1a8 8 0 0 1 16 0v1" />
      <rect x="2.5" y="13" width="4" height="6" rx="1.5" />
      <rect x="17.5" y="13" width="4" height="6" rx="1.5" />
      <path d="M20 19v.5a3 3 0 0 1-3 3h-3" />
    </svg>
  );
}

// --- service-vertical icons (IT services storefront) ------------------------

export function WrenchIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M14.7 6.3a4 4 0 0 1-5 5L4 17v3h3l5.7-5.7a4 4 0 0 1 5-5l-2.6 2.6-1.4-1.4Z" />
    </svg>
  );
}

export function RemoteIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <rect x="3" y="4" width="18" height="12" rx="2" />
      <path d="M8 20h8M12 16v4" />
      <path d="M9 10h6M9 7h3" />
    </svg>
  );
}

export function LaptopIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <rect x="4" y="5" width="16" height="11" rx="1.5" />
      <path d="M2 20h20M9 20l1-2h4l1 2" />
    </svg>
  );
}

export function CloudIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M7 18a4 4 0 0 1-.5-7.97A5 5 0 0 1 16 9.5a3.5 3.5 0 0 1 1 6.83" />
      <path d="M12 13v6M12 13l-2 2M12 13l2 2" />
    </svg>
  );
}

export function NetworkIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <rect x="9" y="2" width="6" height="5" rx="1" />
      <rect x="3" y="17" width="6" height="5" rx="1" />
      <rect x="15" y="17" width="6" height="5" rx="1" />
      <path d="M12 7v5M6 17v-2h12v2M12 12v3" />
    </svg>
  );
}

export function CubeIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M12 2.5 21 7v10l-9 4.5L3 17V7Z" />
      <path d="M12 2.5V21.5M3 7l9 4.5L21 7" />
    </svg>
  );
}

export function DatabaseIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <ellipse cx="12" cy="5" rx="8" ry="3" />
      <path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5" />
      <path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3" />
    </svg>
  );
}

export function GamepadIcon(props: IconProps) {
  return (
    <svg {...base(props)}>
      <path d="M6 8h12a4 4 0 0 1 4 4 4 4 0 0 1-7.2 2.4l-.6-.9H9.8l-.6.9A4 4 0 0 1 2 12a4 4 0 0 1 4-4Z" />
      <path d="M7 11v2M6 12h2M15 11.5h.01M17.5 13h.01" />
    </svg>
  );
}
