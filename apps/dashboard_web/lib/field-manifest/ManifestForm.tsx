"use client";

// =============================================================================
// ManifestForm -- render a whole product editor from a ProductManifest.
// =============================================================================
//
// Groups fields by section (in manifest order) and renders each through the
// FIELD_KIND_RENDERERS registry, using the SAME ManifestFormField scaffold the
// registry wraps each control in. The caller owns the <form> wrapper + the RHF
// control, exactly like the live editor -- this component only lays out the
// fields. ZERO tenant literals.
//
// Ported from the reference implementation (lib/field-manifest/ManifestForm.tsx).
// The only adaptation: the shadcn <Separator> -> a plain <hr>
// (the central dashboard ships no shadcn/ui).

import { Fragment } from "react";
import type { Control, FieldValues } from "react-hook-form";
import { FIELD_KIND_RENDERERS } from "./renderers";
import type { ProductManifest } from "./types";

export interface ManifestFormProps {
  manifest: ProductManifest;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  control: Control<FieldValues>;
}

export function ManifestForm({ manifest, control }: ManifestFormProps) {
  return (
    <div className="space-y-6">
      {manifest.sections.map((section, sectionIndex) => {
        const fields = manifest.fields.filter((f) => f.section === section.id);
        if (fields.length === 0) return null;

        return (
          <Fragment key={section.id}>
            {sectionIndex > 0 ? <hr className="my-6 border-line" /> : null}
            <h3 className="mb-4 text-lg font-semibold text-text">{section.title}</h3>
            <div className="space-y-4">
              {fields.map((field) => {
                const Renderer = FIELD_KIND_RENDERERS[field.kind];
                return <Renderer key={field.name} field={field} control={control} />;
              })}
            </div>
          </Fragment>
        );
      })}
    </div>
  );
}
