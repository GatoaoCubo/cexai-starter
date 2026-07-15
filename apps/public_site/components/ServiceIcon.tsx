// ----------------------------------------------------------------------------
// ServiceIcon -- maps a service-card ``icon`` key (a trusted string from the catalog
// payload) to one of the inline SVG glyphs. SERVER-SAFE presentational. The icon key is
// rendered ONLY by lookup into a fixed map (never as markup), so an unknown / hostile key
// simply falls back to a neutral glyph -- it can never inject anything. ASCII-only.
// ----------------------------------------------------------------------------

import {
  WrenchIcon,
  RemoteIcon,
  LaptopIcon,
  CloudIcon,
  NetworkIcon,
  CubeIcon,
  DatabaseIcon,
  GamepadIcon,
  ShieldIcon,
  SparkleIcon,
} from "@/components/icons";

interface IconProps {
  width?: number;
  height?: number;
  className?: string;
}

/** The fixed key -> glyph map. An unknown key -> the neutral SparkleIcon fallback. */
const MAP: Record<string, (p: IconProps) => JSX.Element> = {
  wrench: WrenchIcon,
  remote: RemoteIcon,
  laptop: LaptopIcon,
  cloud: CloudIcon,
  network: NetworkIcon,
  cube: CubeIcon,
  database: DatabaseIcon,
  gamepad: GamepadIcon,
  shield: ShieldIcon,
};

export function ServiceIcon({
  icon,
  width = 24,
  height = 24,
  className,
}: {
  icon: unknown;
  width?: number;
  height?: number;
  className?: string;
}) {
  const key = typeof icon === "string" ? icon.trim().toLowerCase() : "";
  const Glyph = MAP[key] ?? SparkleIcon;
  return <Glyph width={width} height={height} className={className} />;
}
