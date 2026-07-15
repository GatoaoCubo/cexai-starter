"use client";

// ----------------------------------------------------------------------------
// IntakeColorField -- one HEX color of the visual.colors trio. A native color
// picker synced with a free-text hex input: the picker always writes a valid
// #rrggbb; the text input lets an operator paste a brandbook value, and the
// pure validator (E5 mirror: ^#[0-9a-fA-F]{6}$, brand_validate.py:121-129)
// flags anything malformed inline. ASCII-only + diacritic-free.
// ----------------------------------------------------------------------------

import { HEX_PATTERN } from "@/lib/intake";

export interface IntakeColorFieldProps {
  id: string;
  label: string;
  enKey: string;
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
  error?: string;
}

export default function IntakeColorField({
  id,
  label,
  enKey,
  value,
  onChange,
  required,
  error,
}: IntakeColorFieldProps) {
  // <input type="color"> only accepts a valid hex value; fall back to black
  // for the SWATCH ONLY (the real state keeps whatever the user typed).
  const swatch = HEX_PATTERN.test(value.trim()) ? value.trim().toLowerCase() : "#000000";

  return (
    <div className="space-y-1.5">
      <label htmlFor={id} className="block text-sm font-medium text-foreground">
        {label}
        {required && (
          <span aria-hidden="true" className="text-destructive">
            {" "}
            *
          </span>
        )}{" "}
        <span className="font-mono text-2xs font-normal text-muted-foreground">
          {enKey}
        </span>
      </label>
      <div className="flex items-center gap-2">
        <input
          type="color"
          value={swatch}
          onChange={(e) => onChange(e.target.value)}
          aria-label={label + " (seletor de cor)"}
          className="h-10 w-12 shrink-0 cursor-pointer rounded-md border border-border bg-background p-1"
        />
        <input
          id={id}
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="#3B2A20"
          aria-required={required || undefined}
          aria-invalid={error ? true : undefined}
          className="w-full rounded-md border border-border bg-background px-3 py-2 font-mono text-base text-foreground outline-none focus:border-primary"
        />
      </div>
      {error && (
        <p role="alert" className="text-sm text-destructive">
          {error}
        </p>
      )}
    </div>
  );
}
