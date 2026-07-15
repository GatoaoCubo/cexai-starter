// =============================================================================
// product.atoms.ts -- the zod helper atoms + publish-gate counting helpers
// =============================================================================
//
// The LEAF module the field-manifest generator (lib/field-manifest/buildSchema.ts)
// imports its zod atoms from. It is deliberately a LEAF: it imports nothing from
// the field-manifest core and nothing from any tenant schema, so a future tenant
// schema module can derive FROM buildSchema while buildSchema reuses these exact
// atoms -- with no circular import.
//
// Ported near-verbatim from the reference implementation
// (lib/validations/product.atoms.ts). ZERO tenant literals --
// these are domain-neutral product validation primitives. The error strings are
// PT-BR (the dashboard's locale); diacritics are intentional (UI/content text,
// not executable ASCII surface).

import { z } from "zod";

// Wraps an optional numeric schema so an EMPTY value ("" or null) coming from a
// number <input> becomes undefined (persisted as NULL) instead of being coerced
// to 0 by z.coerce.number(). Any real value (including a typed 0) passes through
// untouched. Used for the numeric ficha fields (dims / weight_grams).
export const emptyToUndefined = <T extends z.ZodTypeAny>(schema: T) =>
  z.preprocess((v) => (v === "" || v === null ? undefined : v), schema);

// Validacao rigorosa para slug
export const slugSchema = z
  .string()
  .min(3, "Slug deve ter no mínimo 3 caracteres")
  .max(100, "Slug deve ter no máximo 100 caracteres")
  .regex(
    /^[a-z0-9]+(-[a-z0-9]+)*$/,
    "Slug deve conter apenas letras minúsculas, números e hífens (sem espaços ou caracteres especiais)",
  )
  .transform((val) => val.toLowerCase());

// Validacao rigorosa para URLs
export const urlSchema = z
  .string()
  .url("URL inválida")
  .max(500, "URL muito longa (máximo 500 caracteres)")
  .refine((url) => {
    try {
      const parsed = new URL(url);
      return ["http:", "https:"].includes(parsed.protocol);
    } catch {
      return false;
    }
  }, "URL deve usar protocolo HTTP ou HTTPS");

// Validacao rigorosa para preco
export const priceSchema = z
  .coerce
  .number()
  .positive("Preço deve ser positivo")
  .max(999999.99, "Preço muito alto (máximo R$ 999.999,99)")
  .multipleOf(0.01, "Preço deve ter no máximo 2 casas decimais");

// Validacao para custo (pode ser 0 ou positivo)
export const custoSchema = z
  .coerce
  .number()
  .min(0, "Custo não pode ser negativo")
  .max(999999.99, "Custo muito alto (máximo R$ 999.999,99)")
  .multipleOf(0.01, "Custo deve ter no máximo 2 casas decimais")
  .optional();

// Validacao para margem (percentual)
export const margemSchema = z
  .coerce
  .number()
  .min(1, "Margem mínima é 1%")
  .max(90, "Margem máxima é 90%")
  .multipleOf(0.01, "Margem deve ter no máximo 2 casas decimais");

// Validacao para imagem do media kit
export const mediaKitImageSchema = z.object({
  slot: z.number().min(1).max(9),
  url: z.string().url(),
  type: z.enum([
    "hero",
    "angle",
    "usage",
    "detail1",
    "detail2",
    "lifestyle1",
    "lifestyle2",
    "packaging",
    "comparison",
  ]),
  alt: z.string().max(200).optional(),
});

// Validacao rigorosa para arrays de texto
export const textArraySchema = z
  .array(
    z
      .string()
      .trim()
      .min(1, "Item não pode estar vazio")
      .max(500, "Item muito longo (máximo 500 caracteres)"),
  )
  .max(50, "Máximo de 50 itens permitidos");

// Validacao rigorosa para FAQ
export const faqItemSchema = z.object({
  question: z
    .string()
    .trim()
    .min(5, "Pergunta muito curta (mínimo 5 caracteres)")
    .max(200, "Pergunta muito longa (máximo 200 caracteres)"),
  answer: z
    .string()
    .trim()
    .min(10, "Resposta muito curta (mínimo 10 caracteres)")
    .max(1000, "Resposta muito longa (máximo 1000 caracteres)"),
});

export const faqSchema = z
  .array(faqItemSchema)
  .max(20, "Máximo de 20 perguntas permitidas");

// ---------------------------------------------------------------------------
// Publish-gate counting helpers -- the generated rules MUST count identically,
// so they live here too and the generator imports the SAME functions.
// ---------------------------------------------------------------------------

/** Count non-empty (trimmed) entries of a string[] field. */
export const countItems = (arr?: Array<string | null | undefined>): number =>
  (arr ?? []).filter((v) => typeof v === "string" && v.trim().length > 0).length;

/** Count FAQ entries that have both a question and an answer. */
export const countFaq = (
  faq?: Array<{ question?: string | null; answer?: string | null }>,
): number =>
  (faq ?? []).filter(
    (f) => (f?.question ?? "").trim().length > 0 && (f?.answer ?? "").trim().length > 0,
  ).length;

/** Length of a trimmed string field. */
export const textLen = (v?: string | null): number => (v ?? "").trim().length;

/** True when a numeric field is present and strictly greater than 0. */
export const isPositiveNumber = (v?: number | null): boolean =>
  typeof v === "number" && Number.isFinite(v) && v > 0;
