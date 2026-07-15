"use client";

// ----------------------------------------------------------------------------
// IntakeField -- one labelled text/url/textarea field of the /intake form.
// Chrome follows the /onboard idiom verbatim (label block text-sm font-medium +
// input w-full rounded-md border-border bg-background focus:border-primary).
// Shows the PT-BR label + the EN dotted key (the form_v1 contract key), the
// template's `*` required marker, a muted hint, and the inline error/warning
// the pure validator (lib/intake.validateIntake) computed. Errors are
// blocking (mirror of brand_validate ERRORS + resolver drops); warnings never
// block (mirror of brand_validate WARNINGS). ASCII-only + diacritic-free.
// ----------------------------------------------------------------------------

export interface IntakeFieldProps {
  id: string;
  label: string;
  /** The form_v1 dotted key (e.g. "identity.brand_name") -- shown as the
   *  machine contract next to the human label. */
  enKey: string;
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
  kind?: "text" | "url" | "textarea";
  placeholder?: string;
  hint?: string;
  error?: string;
  warning?: string;
}

const INPUT_CLASS =
  "w-full rounded-md border border-border bg-background px-3 py-2 text-base " +
  "text-foreground outline-none focus:border-primary";

export default function IntakeField({
  id,
  label,
  enKey,
  value,
  onChange,
  required,
  kind = "text",
  placeholder,
  hint,
  error,
  warning,
}: IntakeFieldProps) {
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
      {kind === "textarea" ? (
        <textarea
          id={id}
          rows={3}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          aria-required={required || undefined}
          aria-invalid={error ? true : undefined}
          className={INPUT_CLASS}
        />
      ) : (
        <input
          id={id}
          type={kind}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          aria-required={required || undefined}
          aria-invalid={error ? true : undefined}
          className={INPUT_CLASS}
        />
      )}
      {hint && !error && <p className="text-sm text-muted-foreground">{hint}</p>}
      {error && (
        <p role="alert" className="text-sm text-destructive">
          {error}
        </p>
      )}
      {!error && warning && <p className="text-sm text-warning">{warning}</p>}
    </div>
  );
}
