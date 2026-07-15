"use client";

import { ProductFormShell } from "@/components/product-form";
import type { ProductDraft } from "@/components/product-form";
import { config } from "@/lib/config";
import Link from "next/link";

// Honest sample product -- no real prices, no real IDs.
// shopify_variant_id is intentionally empty to demonstrate the warning.
const SAMPLE_PRODUCT: ProductDraft = {
  slug: "caneca-gato-ceramica",
  name: "Caneca Gato Ceramica",
  tagline: "O cafe fica mais gostoso com o gato certo.",
  price: 89.9,
  images: [
    "/assets/sample-caneca-frente.jpg",
    "/assets/sample-caneca-lateral.jpg",
    "/assets/sample-caneca-detalhe.jpg",
  ],
  description:
    "Caneca de ceramica com design exclusivo de gato. Capacidade 350ml, resistente a micro-ondas e lava-loucas.",
  long_description:
    "Fabricada em ceramica de alta qualidade com acabamento esmaltado. O design foi criado para capturar a personalidade unica de cada gato. Cada peca apresenta pequenas variacoes naturais do processo artesanal.",
  why_it_works:
    "A ceramica de alta densidade reten o calor 3x mais que o vidro comum, mantendo sua bebida quente por mais tempo. O esmalte interior e certificado livre de chumbo e cadmio.",
  benefits_functional: [
    "Reten calor ate 45 minutos",
    "Capacidade 350ml",
    "Apta para micro-ondas",
    "Resistente a lava-loucas",
  ],
  benefits_emotional: [
    "Expressa amor por gatos",
    "Presente memoravel",
    "Exclusividade artesanal",
  ],
  dims: { largura: "10", altura: "11", profundidade: "10", unit: "cm" },
  materials: ["Ceramica", "Esmalte sem chumbo"],
  weight: "380g",
  custo: 18,
  margem_b2c: 80,
  margem_b2b: 60,
  seo_title: "Caneca Gato Ceramica 350ml | Minha Loja",
  seo_description:
    "Caneca de ceramica com ilustracao exclusiva de gato. 350ml, resistente a micro-ondas e lava-loucas. Presente perfeito para amantes de gatos.",
  seo_keywords: [
    "caneca gato",
    "caneca ceramica gato",
    "presente gato",
    "xicara gato",
  ],
  seo_alt_texts: [
    "Caneca ceramica branca com ilustracao de gato laranja vista de frente",
    "Caneca ceramica gato vista de lado mostrando o cabo",
    "Detalhe do esmaltado interno da caneca de ceramica",
  ],
  quantity: 47,
  status: "active",
  sku: "CAN-GAT-CER-001",
  shopify_variant_id: "",
};

export default function ProductPage() {
  return (
    <div className="mx-auto max-w-4xl">
      {/* Demo banner */}
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3 rounded-lg border border-line bg-panel px-4 py-3">
        <p className="font-mono text-2xs text-text-faint">
          mode={config.fixtures ? "fixtures" : "live"} -- demo product -- no
          backend save
        </p>
        <Link
          href="/dashboard/catalog"
          className="font-mono text-2xs text-synapse hover:underline"
        >
          &lt;- back to catalog
        </Link>
      </div>

      <ProductFormShell initialDraft={SAMPLE_PRODUCT} />
    </div>
  );
}
