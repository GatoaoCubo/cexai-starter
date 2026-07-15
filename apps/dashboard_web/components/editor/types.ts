// =============================================================================
// editor/types.ts -- shared types for the domain-neutral editor sub-components
// =============================================================================
//
// The field-manifest renderer registry binds these widgets to react-hook-form.
// ZERO tenant literals -- pure structural types lifted from the reference proving
// ground (the MediaKitImage shape mirrors mediaKitImageSchema in product.atoms.ts).

/** One FAQ pair edited by the FAQEditor. */
export interface FAQItem {
  question: string;
  answer: string;
}

/** A media-kit slot image (B2B kit). Mirrors mediaKitImageSchema in product.atoms.ts. */
export interface MediaKitImage {
  slot: number;
  url: string;
  type:
    | "hero"
    | "angle"
    | "usage"
    | "detail1"
    | "detail2"
    | "lifestyle1"
    | "lifestyle2"
    | "packaging"
    | "comparison";
  alt?: string;
}
