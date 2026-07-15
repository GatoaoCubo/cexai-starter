// ----------------------------------------------------------------------------
// TrustRow -- the PT-BR premium TRUST SIGNALS row (design_system.md s9).
// SERVER-SAFE presentational (no hooks, no state, no fetch).
//
// MONOCHROME by design: foreground icon + muted-foreground label, on the brand's own
// tokens -- NOT a rainbow seal row. This preserves the PB-minimal identity and re-skins
// with the brand automatically (it reads the design-token utility classes). The copy is
// GENERIC e-commerce trust language (PIX / parcelamento / SSL / troca / origem) defined
// in lib/storeContent -- it is not a tenant-specific claim.
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import { TRUST_SIGNALS, type TrustSignal } from "@/lib/storeContent";
import {
  CardIcon,
  MapPinIcon,
  PixIcon,
  RefreshIcon,
  ShieldIcon,
} from "@/components/icons";

function TrustIcon({ icon }: { icon: TrustSignal["icon"] }) {
  const cls = "text-foreground";
  switch (icon) {
    case "pix":
      return <PixIcon className={cls} />;
    case "card":
      return <CardIcon className={cls} />;
    case "shield":
      return <ShieldIcon className={cls} />;
    case "refresh":
      return <RefreshIcon className={cls} />;
    case "origin":
      return <MapPinIcon className={cls} />;
    default:
      return <ShieldIcon className={cls} />;
  }
}

export function TrustRow({ className = "" }: { className?: string }) {
  return (
    <ul
      aria-label="Garantias de compra"
      className={[
        "flex flex-wrap items-center gap-x-6 gap-y-3",
        className,
      ].join(" ")}
    >
      {TRUST_SIGNALS.map((s) => (
        <li key={s.label} className="flex items-center gap-2">
          <span aria-hidden="true" className="shrink-0">
            <TrustIcon icon={s.icon} />
          </span>
          <span className="text-sm font-medium text-muted-foreground">{s.label}</span>
        </li>
      ))}
    </ul>
  );
}
