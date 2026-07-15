// Product catalog editing types -- canonical schema aligned to
// docs/schema/product_catalog_schema.yaml (the N05 cell owns the YAML source).

export interface ProductDims {
  largura: string;
  altura: string;
  profundidade: string;
  unit: "cm" | "mm" | "m" | "in";
}

export type ProductStatus = "draft" | "active" | "archived";

export interface ProductDraft {
  // basic
  slug: string;
  name: string;
  tagline: string;
  price: number;
  // images -- ordered, max 9
  images: string[];
  // description
  description: string;
  long_description: string;
  why_it_works: string;
  // benefits
  benefits_functional: string[];
  benefits_emotional: string[];
  // specs
  dims: ProductDims;
  materials: string[];
  weight: string;
  // pricing
  custo: number;
  margem_b2c: number;
  margem_b2b: number;
  // seo
  seo_title: string;
  seo_description: string;
  seo_keywords: string[];
  seo_alt_texts: string[];
  // stock
  quantity: number;
  status: ProductStatus;
  sku: string;
  shopify_variant_id: string;
}

export interface SectionProps {
  draft: ProductDraft;
  onChange: (patch: Partial<ProductDraft>) => void;
}
