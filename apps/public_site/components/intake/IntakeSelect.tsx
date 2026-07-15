"use client";

// ----------------------------------------------------------------------------
// IntakeSelect -- one labelled enum field of the /intake form. The options ARE
// the Python gate's enums (lib/intake ARCHETYPES/PRICING_MODELS/VERTICALS/
// B2B_MODES mirror brand_validate.py + cex_ingest_registry.py), so a select
// can only ever emit a valid literal (or "" = unanswered/required-pending).
// Same chrome idiom as IntakeField. ASCII-only + diacritic-free.
// ----------------------------------------------------------------------------

export interface IntakeSelectOption {
  value: string;
  label?: string;
}

export interface IntakeSelectProps {
  id: string;
  label: string;
  enKey: string;
  value: string;
  onChange: (value: string) => void;
  options: readonly (IntakeSelectOption | string)[];
  required?: boolean;
  placeholder?: string;
  hint?: string;
  error?: string;
}

export default function IntakeSelect({
  id,
  label,
  enKey,
  value,
  onChange,
  options,
  required,
  placeholder,
  hint,
  error,
}: IntakeSelectProps) {
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
      <select
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        aria-required={required || undefined}
        aria-invalid={error ? true : undefined}
        className="w-full rounded-md border border-border bg-background px-3 py-2 text-base text-foreground outline-none focus:border-primary"
      >
        <option value="">{placeholder ?? "-- selecione --"}</option>
        {options.map((opt) => {
          const o = typeof opt === "string" ? { value: opt } : opt;
          return (
            <option key={o.value} value={o.value}>
              {o.label ?? o.value}
            </option>
          );
        })}
      </select>
      {hint && !error && <p className="text-sm text-muted-foreground">{hint}</p>}
      {error && (
        <p role="alert" className="text-sm text-destructive">
          {error}
        </p>
      )}
    </div>
  );
}
