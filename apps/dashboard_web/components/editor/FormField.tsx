"use client";

// =============================================================================
// editor/FormField.tsx -- the react-hook-form field scaffold (shadcn-free)
// =============================================================================
//
// The reference renderers wrap every control in a shadcn FormField -> FormItem ->
// FormLabel/FormControl/FormDescription/FormMessage scaffold. The central
// dashboard ships no shadcn/ui, so this is a minimal, domain-neutral equivalent
// built on react-hook-form's <Controller> + the dashboard's existing CSS atoms
// (the same classes FieldHelpers.tsx uses: field labels, help text). It exposes
// the RHF `field` render-prop object (value/onChange/onBlur/name/ref) exactly the
// way the registry expects, and surfaces the field-level validation error as the
// "FormMessage". ZERO tenant literals.

import type { ReactNode } from "react";
import { Controller } from "react-hook-form";
import type { Control, ControllerRenderProps, FieldValues } from "react-hook-form";

export interface ManifestFormFieldProps {
  /** RHF control supplied by the caller. */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  control: Control<FieldValues>;
  /** Field name (== the manifest FieldDef.name). */
  name: string;
  /** Visible label. */
  label: string;
  /** Mark the label with a trailing "*". */
  required?: boolean;
  /** Helper/description text under the control. */
  helpText?: string;
  /** Renders the actual control given the RHF render-prop field object. */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  children: (rhf: ControllerRenderProps<FieldValues, string>) => ReactNode;
}

/**
 * Wrap a control in the standard label + control + help + error scaffold, wired
 * through RHF's Controller. The error message renders only when present (the
 * "FormMessage" analogue). The caller owns the <form> + control (like the live editor).
 */
export function ManifestFormField({
  control,
  name,
  label,
  required,
  helpText,
  children,
}: ManifestFormFieldProps) {
  return (
    <Controller
      control={control}
      name={name}
      render={({ field, fieldState }) => (
        <div>
          <p className="mb-1.5 font-mono text-2xs uppercase tracking-wider text-text-muted">
            {label}
            {required ? " *" : ""}
          </p>
          {children(field)}
          {helpText ? (
            <p className="mt-1 font-mono text-2xs text-text-faint">{helpText}</p>
          ) : null}
          {fieldState.error?.message ? (
            <p className="mt-1 font-mono text-2xs text-danger">{fieldState.error.message}</p>
          ) : null}
        </div>
      )}
    />
  );
}
