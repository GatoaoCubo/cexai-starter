// =============================================================================
// productManifest.ts -- the FIRST tenant instance of a field_manifest (proof input)
// =============================================================================
//
// This is the ONLY file in lib/field-manifest/ that holds tenant sample
// literals. The generic core (types/buildSchema/renderers/ManifestForm) is fed
// THIS manifest to prove the schema-to-form mold. Central mints a new product
// editor per tenant by keeping the generic core and swapping THIS file.
//
// Ported from the reference implementation (lib/field-manifest/productManifest.ts).
// It is the FIRST `field_manifest` kind instance/template.
//
// Field set + publish rules mirror the proven live schema:
//   - benefits_functional minCount 3, usage_guide minCount 3, faq minCount 3
//   - long_description minLength 120
//   - numeric dims (dim_length_cm/width/height) positive
//   - weight_grams positive
// tenantParam:true marks tenant-specific fields (documentation for the distiller).

import type { ProductManifest } from "./types";

// The 14 sections of the product editor.
const SECTIONS = [
  { id: "identity", title: "Identidade" },
  { id: "media", title: "Mídia" },
  { id: "short_description", title: "Descrição Curta" },
  { id: "detailed_content", title: "Conteúdo Detalhado" },
  { id: "benefits", title: "Benefícios" },
  { id: "specs", title: "Características" },
  { id: "usage_care", title: "Guia de Uso e Cuidados" },
  { id: "faq", title: "FAQ" },
  { id: "links", title: "Links e Relacionamentos" },
  { id: "pricing", title: "Precificação B2C/B2B" },
  { id: "media_kit", title: "Media Kit B2B" },
  { id: "stock_status", title: "Estoque e Status" },
  { id: "seo", title: "SEO" },
  { id: "marketplace_codes", title: "Códigos de Marketplace" },
] as const;

export const productManifest: ProductManifest = {
  sections: SECTIONS.map((s) => ({ id: s.id, title: s.title })),
  fields: [
    // -- Identidade --------------------------------------------------------
    {
      name: "name",
      label: "Nome do Produto",
      kind: "text",
      section: "identity",
      required: true,
      min: 3,
      max: 100,
      placeholder: "Ex: Cama Donut Premium",
    },
    {
      name: "slug",
      label: "Slug (URL)",
      kind: "slug",
      section: "identity",
      required: true,
      max: 100,
      placeholder: "ex: produto-exemplo",
    },
    {
      name: "tagline",
      label: "Tagline",
      kind: "text",
      section: "identity",
      max: 200,
      placeholder: "Frase curta de destaque",
    },

    // -- Mídia -------------------------------------------------------------
    {
      name: "images",
      label: "Imagens e Vídeos",
      kind: "images",
      section: "media",
      required: true,
      max: 9,
      helpText: "Primeira imagem/vídeo será a capa. Máximo 9 arquivos.",
    },

    // -- Descrição Curta ---------------------------------------------------
    {
      name: "description",
      label: "Descrição Curta",
      kind: "textarea",
      section: "short_description",
      required: true,
      min: 20,
      max: 10000,
      placeholder: "Resumo do produto (1-2 frases)",
    },

    // -- Conteúdo Detalhado ------------------------------------------------
    {
      name: "long_description",
      label: "Descrição Longa",
      kind: "textarea",
      section: "detailed_content",
      max: 5000,
      placeholder: "Descrição completa com parágrafos (2-3 parágrafos)",
      // Publish gate: >= 120 chars.
      publish: { rule: "minLength", threshold: 120, label: "uma descrição longa" },
    },
    {
      name: "why_it_works",
      label: "Por Que Funciona",
      kind: "textarea",
      section: "detailed_content",
      max: 2000,
      placeholder: "Explicação técnica ou comportamental",
      tenantParam: true, // tenant etologia-felina angle
    },

    // -- Benefícios --------------------------------------------------------
    {
      name: "benefits_functional",
      label: "Benefícios Funcionais",
      kind: "tags",
      section: "benefits",
      max: 20,
      placeholder: "Ex: Suporta até 8kg",
      helpText: "Benefícios práticos e técnicos do produto",
      // Publish gate: >= 3.
      publish: { rule: "minCount", threshold: 3, label: "benefícios funcionais" },
    },
    {
      name: "benefits_emotional",
      label: "Benefícios Emocionais",
      kind: "tags",
      section: "benefits",
      max: 20,
      placeholder: "Ex: Reduz ansiedade do gato",
      helpText: "Como o produto melhora o bem-estar",
      tenantParam: true, // tenant emotional/pet-wellbeing angle
    },

    // -- Características ----------------------------------------------------
    {
      name: "features",
      label: "Características Principais",
      kind: "tags",
      section: "specs",
      max: 20,
      placeholder: "Ex: Material impermeável",
    },
    {
      name: "brand",
      label: "Marca",
      kind: "text",
      section: "specs",
      max: 100,
      placeholder: "Ex: Sua Marca",
      helpText: "Marca ou fabricante do produto (aparece na ficha técnica)",
    },
    {
      name: "dimensions",
      label: "Dimensões (texto)",
      kind: "text",
      section: "specs",
      max: 100,
      placeholder: "Ex: 50 × 50 × 20 cm",
      helpText: "Texto livre exibido na ficha técnica da página.",
    },
    {
      name: "weight",
      label: "Peso (texto)",
      kind: "text",
      section: "specs",
      max: 50,
      placeholder: "Ex: ~900 g",
      helpText: "Texto livre exibido na ficha técnica da página.",
    },
    {
      name: "dim_length_cm",
      label: "Comprimento (cm)",
      kind: "number",
      section: "specs",
      min: 0,
      max: 100000,
      placeholder: "Ex: 50",
      // Publish gate: numeric dims L+W+H all positive (maps one error to length).
      publish: {
        rule: "positive",
        label:
          "as dimensões numéricas (comprimento, largura e altura em cm, cada uma maior que zero)",
        companions: ["dim_width_cm", "dim_height_cm"],
      },
    },
    {
      name: "dim_width_cm",
      label: "Largura (cm)",
      kind: "number",
      section: "specs",
      min: 0,
      max: 100000,
      placeholder: "Ex: 50",
    },
    {
      name: "dim_height_cm",
      label: "Altura (cm)",
      kind: "number",
      section: "specs",
      min: 0,
      max: 100000,
      placeholder: "Ex: 20",
    },
    {
      name: "weight_grams",
      label: "Peso (g)",
      kind: "number",
      section: "specs",
      min: 0,
      max: 10000000,
      placeholder: "Ex: 900",
      helpText: "Em gramas.",
      // Publish gate: weight_grams positive.
      publish: { rule: "positive", label: "o peso numérico em gramas (maior que zero)" },
    },
    {
      name: "materials",
      label: "Materiais",
      kind: "tags",
      section: "specs",
      max: 10,
      placeholder: "Ex: Algodão premium",
    },
    {
      name: "colors",
      label: "Cores Disponíveis",
      kind: "tags",
      section: "specs",
      max: 10,
      placeholder: "Ex: Cinza",
    },
    {
      name: "indicacao_porte",
      label: "Indicação por Porte",
      kind: "tags",
      section: "specs",
      max: 10,
      placeholder: "Ex: Pequeno",
      helpText: "Sugestões: Pequeno, Médio, Grande",
      tenantParam: true, // tenant pet-size audience tag
    },
    {
      name: "indicacao_idade",
      label: "Indicação por Idade",
      kind: "tags",
      section: "specs",
      max: 10,
      placeholder: "Ex: Filhote",
      helpText: "Sugestões: Filhote, Adulto, Sênior",
      tenantParam: true, // tenant pet-age audience tag
    },

    // -- Guia de Uso e Cuidados --------------------------------------------
    {
      name: "usage_guide",
      label: "Como Usar (passos numerados)",
      kind: "orderedArray",
      section: "usage_care",
      max: 20,
      numbered: true, // numbers the "Como Usar" steps (1. 2. 3.)
      placeholder: "Ex: Desembale o produto",
      // Publish gate: >= 3 steps.
      publish: { rule: "minCount", threshold: 3, label: "passos no modo de uso" },
    },
    {
      name: "care_instructions",
      label: "Cuidados e Manutenção",
      kind: "orderedArray",
      section: "usage_care",
      max: 20,
      placeholder: "Ex: Lavar à mão com água fria",
    },
    {
      name: "box_contents",
      label: "Conteúdo da Caixa",
      kind: "orderedArray",
      section: "usage_care",
      max: 10,
      placeholder: "Ex: 1 produto (cor escolhida)",
    },
    {
      name: "warranty",
      label: "Garantia",
      kind: "textarea",
      section: "usage_care",
      max: 500,
      placeholder: "Ex: 30 dias contra defeitos",
    },
    {
      name: "shipping_info",
      label: "Informações de Envio",
      kind: "textarea",
      section: "usage_care",
      max: 1000,
      placeholder: "Ex: Enviamos para todo Brasil",
    },

    // -- FAQ ---------------------------------------------------------------
    {
      name: "faq",
      label: "Perguntas Frequentes",
      kind: "faq",
      section: "faq",
      max: 20,
      // Publish gate: >= 3 FAQ pairs.
      publish: { rule: "minCount", threshold: 3, label: "perguntas no FAQ" },
    },

    // -- Links e Relacionamentos -------------------------------------------
    {
      name: "purchase_link",
      label: "Link de Compra",
      kind: "text",
      section: "links",
      placeholder: "https://loja.example.com/...",
    },
    {
      name: "whatsapp_link",
      label: "Link WhatsApp",
      kind: "text",
      section: "links",
      placeholder: "https://wa.me/...",
    },
    {
      name: "mercadolivre_link",
      label: "Link Mercado Livre",
      kind: "text",
      section: "links",
      placeholder: "https://produto.mercadolivre.com.br/...",
      helpText: "Link alternativo para compra no Mercado Livre",
    },
    {
      name: "related_products",
      label: "Produtos Relacionados (slugs)",
      kind: "tags",
      section: "links",
      max: 10,
      placeholder: "Ex: produto-exemplo",
      helpText: "Insira os slugs dos produtos relacionados",
    },

    // -- Precificação B2C/B2B ----------------------------------------------
    {
      name: "custo",
      label: "Custo (R$)",
      kind: "number",
      section: "pricing",
      min: 0,
      placeholder: "Ex: 19.80",
      helpText: "Preço de compra/fornecedor",
    },
    {
      name: "margem_b2c",
      label: "Margem B2C (%)",
      kind: "number",
      section: "pricing",
      placeholder: "80",
      helpText: "Varejo (padrão: 38%)",
      default: 38,
      tenantParam: true, // tenant dual-margin B2B/B2C pricing model
    },
    {
      name: "margem_b2b",
      label: "Margem B2B (%)",
      kind: "number",
      section: "pricing",
      placeholder: "60",
      helpText: "Atacado (padrão: 13.5%)",
      default: 13.5,
      tenantParam: true, // tenant dual-margin B2B/B2C pricing model
    },
    {
      name: "preco_b2c",
      label: "Preço B2C (Varejo)",
      kind: "price",
      section: "pricing",
      helpText: "Calculado a partir do custo + margem B2C",
      tenantParam: true,
    },
    {
      name: "preco_b2b",
      label: "Preço B2B (Atacado)",
      kind: "price",
      section: "pricing",
      helpText: "Calculado a partir do custo + margem B2B",
      tenantParam: true,
    },

    // -- Media Kit B2B -----------------------------------------------------
    {
      name: "has_media_kit",
      label: "Media Kit Ativo",
      kind: "boolean",
      section: "media_kit",
      default: false,
      helpText: "Disponibilizar kit de imagens para revendedores B2B",
      tenantParam: true, // tenant B2B media-kit capability
    },
    {
      name: "media_kit_images",
      label: "Imagens do Media Kit",
      kind: "mediaKit",
      section: "media_kit",
      max: 9,
      tenantParam: true,
    },

    // -- Estoque e Status --------------------------------------------------
    {
      name: "price",
      label: "Preço Final (R$)",
      kind: "price",
      section: "stock_status",
      required: true,
      placeholder: "0.00",
      helpText: "Preço de venda (igual ao B2C)",
    },
    {
      name: "quantity",
      label: "Quantidade em Estoque",
      kind: "number",
      section: "stock_status",
      required: true,
      min: 0,
      placeholder: "0",
      default: 0,
    },
    {
      name: "status",
      label: "Status",
      kind: "select",
      section: "stock_status",
      required: true,
      options: [
        { value: "draft", label: "Rascunho" },
        { value: "published", label: "Publicado" },
        { value: "archived", label: "Arquivado" },
      ],
      placeholder: "Selecione o status",
    },

    // -- SEO ---------------------------------------------------------------
    {
      name: "seo_title",
      label: "Título SEO (max 60 caracteres)",
      kind: "text",
      section: "seo",
      required: true,
      min: 10,
      max: 60,
      placeholder: "Título otimizado para busca",
    },
    {
      name: "seo_description",
      label: "Meta Description (50-160 caracteres)",
      kind: "textarea",
      section: "seo",
      required: true,
      min: 50,
      max: 160,
      placeholder: "Descrição otimizada para busca",
    },
    {
      name: "seo_og_image",
      label: "Imagem OG (URL)",
      kind: "text",
      section: "seo",
      placeholder: "https://...",
      helpText: "Imagem que aparece ao compartilhar nas redes sociais",
    },
    {
      name: "seo_keywords",
      label: "Palavras-chave Primárias (max 10)",
      kind: "tags",
      section: "seo",
      max: 10,
      placeholder: "Ex: cama para gatos",
    },
    {
      name: "seo_long_tail_keywords",
      label: "Long-tail Keywords (max 50)",
      kind: "tags",
      section: "seo",
      max: 50,
      placeholder: "Ex: cama donut para gatos grandes",
      helpText: "Frases longas e específicas com alta intenção de compra",
    },
    {
      name: "seo_alt_texts",
      label: "Alt Texts para Imagens (max 20)",
      kind: "orderedArray",
      section: "seo",
      max: 20,
      placeholder: "Descrição detalhada da imagem",
      helpText: "Um alt text descritivo para cada imagem do produto",
    },
    {
      name: "seo_canonical",
      label: "URL Canônica",
      kind: "text",
      section: "seo",
      placeholder: "https://example.com/produtos/...",
      helpText: "URL principal do produto (evita conteúdo duplicado)",
    },

    // -- Códigos de Marketplace --------------------------------------------
    {
      name: "gtin",
      label: "GTIN / EAN",
      kind: "text",
      section: "marketplace_codes",
      max: 14,
      placeholder: "Ex: 7891234567890",
      helpText:
        "Código de barras (EAN-13 / UPC). Principal código exigido pelos marketplaces.",
    },
    {
      name: "mpn",
      label: "MPN (Código do Fabricante)",
      kind: "text",
      section: "marketplace_codes",
      max: 70,
      placeholder: "Ex: ABC-1234",
      helpText: "Manufacturer Part Number -- usado quando não há GTIN.",
    },
    {
      name: "model",
      label: "Modelo",
      kind: "text",
      section: "marketplace_codes",
      max: 100,
      placeholder: "Ex: Donut Premium",
      helpText: "Nome ou número do modelo do produto.",
    },
    {
      name: "condition",
      label: "Condição",
      kind: "select",
      section: "marketplace_codes",
      default: "new",
      options: [
        { value: "new", label: "Novo" },
        { value: "used", label: "Usado" },
        { value: "refurbished", label: "Recondicionado" },
      ],
      placeholder: "Selecione a condição",
      helpText: "Estado do produto (padrão: Novo).",
    },
    {
      name: "attributes",
      label: "Atributos por Categoria",
      kind: "keyValue",
      section: "marketplace_codes",
      max: 50,
      helpText:
        "Campos específicos da categoria (chave-valor) usados na publicação para marketplaces.",
    },
  ],
};
