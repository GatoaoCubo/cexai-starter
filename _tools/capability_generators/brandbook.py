#!/usr/bin/env python3
# -*- coding: ascii -*-
"""brandbook -- N06 CAPGEN: complete brand book from rich materials.

KIND = "brandbook" (capability slug = kind; auto-registered by @register).

INPUT CONTRACT (MoldField[]-shaped -- Cell A seam):
  brand_name          (text, required)    -- brand/company name
  brand_essence       (text, optional)    -- essence in 1 sentence
  brand_materials     (text, optional)    -- free-text description OR URL/PDF path
  brand_materials_text  (text, optional)  -- text extracted from PDF/URL by Cell A
  brand_materials_palette (text, optional)-- JSON array of hex strings extracted from logo
                                             OR comma-sep hex list e.g. "#1A2B3C,#FFFFFF"

OUTPUT SECTIONS (8, frozen shape -- matches the brandbook kind contract):
  1. Identidade da Marca (fields)   -- name, essence, positioning
  2. Paleta de Cores     (table)    -- hex swatches + role + usage
  3. Tipografia          (fields)   -- typeface stack + usage
  4. Persona da Marca    (fields)   -- archetype, voice, tone, 3 copy samples
  5. Uso do Logotipo     (list)     -- logo do/don't guidelines
  6. Estilo de Imagem    (fields)   -- mood, photography, filters
  7. Framework de Mensagem (table) -- message x audience x channel x priority
  8. Dos e Nao-Faca     (table)    -- do column / don't column

NEVER-FABRICATE: a section with insufficient input renders an honest
  "[fornecer: ...]" editable placeholder, not invented brand claims.
DEGRADE-NEVER: missing optional fields default; never crashes.
ASCII-only source per .claude/rules/ascii-code-rule.md.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Mapping, Optional, Tuple

from ._base import (
    effective_kind,
    fields_section,
    list_section,
    register,
    structured_output,
    table_section,
)

KIND = "brandbook"
GENERATOR_VERSION = "1.0.0"
RUN_MODE = "offline-scaffold"

# Default color-role labels (ordered by visual hierarchy)
_PALETTE_ROLES = [
    "Primaria",
    "Secundaria",
    "Destaque/Accent",
    "Neutra",
    "Fundo",
]

# Minimum luma heuristic: whether a hex is "light" (for contrast notes)
_HEX_RE = re.compile(r"#[0-9A-Fa-f]{6}")

# Default typography stack when not provided
_DEFAULT_TYPEFACES = [
    ("Primaria (headings)", "[fornecer: ex. Montserrat Bold]"),
    ("Secundaria (corpo)", "[fornecer: ex. Open Sans Regular]"),
    ("Display / especial", "[fornecer: ex. Playfair Display]"),
    ("Escala de tamanhos", "[fornecer: ex. h1=48px, h2=32px, body=16px]"),
]

# Logo guidelines -- ALWAYS emitted as a list (rich or placeholder)
_LOGO_DEFAULTS = [
    "[fornecer: versao principal do logotipo (fundo claro)]",
    "[fornecer: versao invertida do logotipo (fundo escuro)]",
    "Espaco de protecao: ao menos 1x a altura do simbolo em volta",
    "[fornecer: tamanho minimo em pixels/mm]",
    "Nao distorcer proporcoes -- usar somente as versoes aprovadas",
    "[fornecer: versoes proibidas (ex. sem fundo, monocromatico)]",
]

# Imagery style -- ALWAYS emitted as fields
_IMAGERY_DEFAULTS = [
    ("Mood geral", "[fornecer: ex. confiante, acessivel, moderno]"),
    ("Estilo de fotografia", "[fornecer: ex. lifestyle, produto plano, editorial]"),
    ("Paleta de filtros", "[fornecer: ex. quente, dessaturado, alto contraste]"),
    ("Elementos proibidos", "[fornecer: ex. fotos de banco 'generico', rostos borrados]"),
]


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _parse_palette(raw: Any) -> List[str]:
    """Parse the brand_materials_palette value into a list of hex strings.

    Accepts:
      - JSON array of strings: '["#1A2B3C", "#FFFFFF"]'
      - comma/space-sep list:  "#1A2B3C, #FFFFFF"
      - a single hex:          "#1A2B3C"
    Returns [] when nothing valid is found. NEVER fabricates a hex. TOTAL."""
    raw_s = str(raw or "").strip()
    if not raw_s:
        return []
    # try JSON array
    if raw_s.startswith("["):
        try:
            parsed = json.loads(raw_s)
            if isinstance(parsed, list):
                return [str(h).strip() for h in parsed if _HEX_RE.match(str(h).strip())]
        except Exception:
            pass
    # try comma/space delimited
    tokens = [t.strip() for t in re.split(r"[,\s]+", raw_s) if t.strip()]
    return [t for t in tokens if _HEX_RE.match(t)]


def _hex_luma(hex_color: str) -> float:
    """Approximate perceived luminance of a hex color (0=black, 1=white). TOTAL."""
    try:
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    except Exception:
        return 0.5


def _palette_rows(colors: List[str]) -> List[List[Any]]:
    """Build table rows for the palette section. Each color gets a role label.

    When fewer colors than roles exist, remaining roles get [fornecer: hex].
    NEVER fabricates a hex value. NEVER invents a color."""
    rows: List[List[Any]] = []
    roles = list(_PALETTE_ROLES)
    for i, role in enumerate(roles):
        if i < len(colors):
            hex_val = colors[i]
            luma = _hex_luma(hex_val)
            contrast = "texto escuro" if luma > 0.5 else "texto claro"
            rows.append([role, hex_val, contrast, "Uso principal"])
        else:
            rows.append([role, "[fornecer: hex]", "--", "Uso principal"])
    return rows


def _identity_rows(inputs: Mapping[str, Any]) -> List[Tuple[str, str]]:
    """Build the Identidade section field rows from inputs. NEVER fabricates. TOTAL."""
    brand_name = str(inputs.get("brand_name") or "").strip()
    essence = str(inputs.get("brand_essence") or inputs.get("essence") or "").strip()
    materials_text = str(inputs.get("brand_materials_text") or inputs.get("brand_materials") or "").strip()

    # Try to extract a positioning hint from materials text (first 200 chars as a hint).
    positioning_hint = ""
    if materials_text:
        snippet = materials_text[:200].replace("\n", " ").strip()
        if snippet:
            positioning_hint = snippet + ("..." if len(materials_text) > 200 else "")

    return [
        ("Nome da marca", brand_name or "[fornecer: nome da marca]"),
        ("Essencia (1 frase)", essence or "[fornecer: essencia em 1 frase -- ex. 'Conforto premium para pets']"),
        ("Proposta de valor", "[fornecer: o que a marca entrega que outros nao entregam]"),
        ("Posicionamento", positioning_hint or "[fornecer: posicionamento no mercado -- ex. premium / acessivel / nicho]"),
        ("Missao", "[fornecer: missao em 1-2 frases]"),
        ("Valores centrais", "[fornecer: 3-5 valores -- ex. confian,ca, inovacao, sustentabilidade]"),
    ]


def _typography_rows(materials_text: str) -> List[Tuple[str, str]]:
    """Typography fields. Honest defaults when no type spec is in the materials. TOTAL."""
    # Future: parse font names from materials_text via regex
    # For now: always honest placeholders (never fabricate a font name)
    return _DEFAULT_TYPEFACES


def _persona_rows(materials_text: str) -> List[Tuple[str, str]]:
    """Persona fields: archetype, voice, tone, 3 copy samples. NEVER fabricates. TOTAL."""
    has_text = bool(materials_text.strip())
    if has_text:
        # We have source material -- extract tone cues by presence of marker words.
        # This is a HEURISTIC: we note the presence, not invent copy.
        text_lower = materials_text.lower()
        formal = any(w in text_lower for w in ["profissional", "empresa", "solucao", "corporativo"])
        casual = any(w in text_lower for w in ["voce", "gente", "facil", "simples", "amigo"])
        tone = "Formal e confiante" if formal else ("Casual e acessivel" if casual else "[fornecer: tom -- ex. confiante, descontraido, tecnico]")
    else:
        tone = "[fornecer: tom -- ex. confiante, descontraido, tecnico]"

    return [
        ("Arquetipo", "[fornecer: arquetipo -- ex. Heroi, Cuidador, Criador, Explorador]"),
        ("Voz da marca", "[fornecer: voz em 3 adjetivos -- ex. clara, direta, inspiradora]"),
        ("Tom geral", tone),
        ("Tom em situacoes criticas", "[fornecer: ex. empatiico e resolutivo em reclamacoes]"),
        ("Copy sample 1 -- headline", "[fornecer: headline principal da pagina inicial]"),
        ("Copy sample 2 -- beneficio", "[fornecer: frase de beneficio -- ex. 'Entregamos em 24h']"),
        ("Copy sample 3 -- CTA", "[fornecer: chamada para acao -- ex. 'Experimente gratis']"),
    ]


def _messaging_rows() -> List[List[str]]:
    """Messaging framework rows (3 default entries). NEVER fabricates. TOTAL."""
    return [
        ["[fornecer: mensagem principal]", "[fornecer: publico]", "[fornecer: canal]", "Alta"],
        ["[fornecer: mensagem de suporte]", "[fornecer: publico]", "[fornecer: canal]", "Media"],
        ["[fornecer: prova social / depoimento]", "Todos", "Site / social", "Alta"],
    ]


def _dodonts_rows(materials_text: str) -> List[List[str]]:
    """Do/don't rows. NEVER fabricates brand claims. TOTAL."""
    return [
        ["Usar a voz ativa e direta", "Usar jargoes tecnicos sem explicacao"],
        ["Citar beneficios concretos (numeros, prazos)", "Fazer promessas sem comprovacao"],
        ["Manter consistencia de paleta e tipografia", "Misturar fontes nao aprovadas"],
        ["[fornecer: faca especifico da marca]", "[fornecer: nao-faca especifico da marca]"],
    ]


# --------------------------------------------------------------------------- #
# Media hooks (DUAL2 seam -- canonical unprefixed names)
# --------------------------------------------------------------------------- #

def media_requests(inputs: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Declare media slots for the brandbook dual-output face.

    Slots:
      logo_primary   -- image: the primary logo file
      logo_dark      -- image: the dark/inverse logo variant
      brand_cover    -- image: the brandbook cover / hero image
      palette_visual -- image: visual color swatch export
    NEVER fabricates a src. All start as upload-fallback; produced_media fills real srcs."""
    return [
        {"key": "logo_primary", "kind": "image", "section": "Uso do Logotipo", "label": "Logo principal"},
        {"key": "logo_dark", "kind": "image", "section": "Uso do Logotipo", "label": "Logo (versao escura)"},
        {"key": "brand_cover", "kind": "image", "section": None, "label": "Capa do brandbook"},
        {"key": "palette_visual", "kind": "image", "section": "Paleta de Cores", "label": "Swatches de paleta"},
    ]


def produced_media(inputs: Mapping[str, Any]) -> Dict[str, Any]:
    """Return any already-produced media from inputs.

    For now: if brand_materials_data_uri is present, map it to logo_primary.
    All other slots stay upload-fallback (NEVER fabricate a src). TOTAL."""
    produced: Dict[str, Any] = {}
    data_uri = str(inputs.get("brand_materials_data_uri") or "").strip()
    if data_uri and data_uri.startswith("data:image"):
        produced["logo_primary"] = {"src": data_uri, "alt": "Logo enviado"}
    return produced


# --------------------------------------------------------------------------- #
# The generator
# --------------------------------------------------------------------------- #

@register(KIND)
def build(
    inputs: Mapping[str, Any], *, credential: "Optional[Any]" = None,
    resolved_kind: Optional[str] = None,
) -> dict:
    """Build a complete brandbook StructuredOutput from brand materials.

    Parses brand_name / brand_essence / brand_materials_text / brand_materials_palette
    and emits 8 output_sections covering the full brandbook surface.

    NEVER-FABRICATE: every section without sufficient input renders an honest
      '[fornecer: ...]' placeholder. No invented brand claims or hex colors.

    Designed for cex_dual_output.to_dual_output: call
      to_dual_output("brandbook", struct,
                     media_requests=media_requests(inputs),
                     produced_media=produced_media(inputs))
    to get both faces (HUMAN audiovisual brandbook + MACHINE .md+YAML).

    ``resolved_kind`` (mission R-333): the PER-TENANT RESOLVED kind the caller
    (cex_run_capability) already holds, embedded verbatim into the artifact JSON
    self-description instead of the module KIND constant. None/blank falls back to KIND.
    """
    notes: List[str] = []
    _kind = effective_kind(resolved_kind, KIND)

    # F1 CONSTRAIN -- parse inputs (degrade-never on missing optional fields)
    brand_name = str(inputs.get("brand_name") or "").strip()
    brand_essence = str(inputs.get("brand_essence") or "").strip()
    materials_text = str(inputs.get("brand_materials_text") or inputs.get("brand_materials") or "").strip()
    palette_raw = inputs.get("brand_materials_palette") or inputs.get("palette") or ""

    if not brand_name:
        notes.append("[WARN] brand_name not provided -- placeholders emitted for identity section")
    if not materials_text:
        notes.append("[INFO] no brand materials text -- honest placeholders emitted for persona/messaging")

    # F3 INJECT -- extract structured brand signals from inputs
    colors = _parse_palette(palette_raw)
    has_palette = bool(colors)
    has_text = bool(materials_text)

    if has_palette:
        notes.append("Palette extracted: %d color(s)" % len(colors))
    else:
        notes.append("[INFO] no palette extracted -- color placeholders emitted; provide brand_materials_palette")

    # F6 PRODUCE -- 8 output sections

    # 1. Identidade da Marca
    identity_rows = _identity_rows(inputs)
    s1 = fields_section(
        "Identidade da Marca",
        identity_rows,
        note="Fundacao da marca. Preencha os campos [fornecer: ...] com os valores reais.",
    )

    # 2. Paleta de Cores
    palette_rows = _palette_rows(colors)
    s2 = table_section(
        "Paleta de Cores",
        ["Funcao", "Hex", "Contraste", "Uso principal"],
        palette_rows,
        column_types=["string", "string", "string", "string"],
        key_col_index=0,
        note=(
            ("Paleta extraida de " + str(len(colors)) + " cor(es) fornecida(s).")
            if has_palette
            else "Paleta nao extraida -- substitua os [fornecer: hex] pelos valores reais da marca."
        ),
    )

    # 3. Tipografia
    type_rows = _typography_rows(materials_text)
    s3 = fields_section(
        "Tipografia",
        type_rows,
        note="Defina as fontes aprovadas. Consistencia tipografica e decisiva para reconhecimento da marca.",
    )

    # 4. Persona da Marca
    persona_rows = _persona_rows(materials_text)
    s4 = fields_section(
        "Persona da Marca",
        persona_rows,
        note=(
            "Persona inferida do texto de materiais. Valide e complete os campos [fornecer: ...]."
            if has_text
            else "Preencha a persona -- arquetipo, voz e os 3 copy samples sao obrigatorios para o time de copy."
        ),
    )

    # 5. Uso do Logotipo
    s5 = list_section(
        "Uso do Logotipo",
        _LOGO_DEFAULTS,
        note="Guia de uso do logotipo. Substitua os [fornecer: ...] com as versoes e regras reais.",
    )

    # 6. Estilo de Imagem
    s6 = fields_section(
        "Estilo de Imagem",
        _IMAGERY_DEFAULTS,
        note="Define o DNA visual das imagens. Consistencia visual constroi autoridade de marca.",
    )

    # 7. Framework de Mensagem
    msg_rows = _messaging_rows()
    s7 = table_section(
        "Framework de Mensagem",
        ["Mensagem", "Publico-alvo", "Canal", "Prioridade"],
        msg_rows,
        column_types=["string", "string", "string", "string"],
        key_col_index=0,
        note="Mapeamento mensagem x publico x canal. Emite ROI direto: mensagem certa, canal certo, pessoa certa.",
    )

    # 8. Dos e Nao-Faca
    dodonts = _dodonts_rows(materials_text)
    s8 = table_section(
        "Dos e Nao-Faca",
        ["Fazer", "Nao Fazer"],
        dodonts,
        column_types=["string", "string"],
        key_col_index=0,
        note="Guardrails de comunicacao. Impede inconsistencias que diluem o valor da marca.",
    )

    sections = [s1, s2, s3, s4, s5, s6, s7, s8]

    # F7 GOVERN -- gate: brand_name is the only hard requirement
    score = 1.0
    missing: List[str] = []

    if not brand_name:
        score -= 0.20
        missing.append("brand_name")
        notes.append("[FAIL] brand_name missing -- required for brandbook identity")

    if not has_palette:
        score -= 0.10
        notes.append("[WARN] palette missing -- color section uses placeholders")

    if not has_text:
        score -= 0.10
        notes.append("[WARN] materials text missing -- persona/messaging use placeholders")

    if not brand_essence:
        score -= 0.05
        notes.append("[INFO] brand_essence not provided -- identity section uses placeholder")

    score = max(0.0, score)
    passed = (not bool(missing)) and score >= 0.60

    # Build the machine artifact (the canonical .md projection)
    artifact_meta: Dict[str, Any] = {
        "kind": _kind,
        "generator_version": GENERATOR_VERSION,
        "brand_name": brand_name or None,
        "sections_count": len(sections),
        "palette_colors": colors,
        "has_materials_text": has_text,
        "missing_required": missing,
    }

    return structured_output(
        KIND,
        sections,
        passed=passed,
        score=score,
        artifact=json.dumps(artifact_meta, ensure_ascii=True),
        real=True,
        notes=notes,
    )


# --------------------------------------------------------------------------- #
# Domain contract (Missao A / MOLDED_REAL_SEAM export-deepening) -- the REAL domain law
# this generator enforces, exposed for cex_export_agent.py to bake into an exported agent
# package (system_instruction GROUNDING + a new knowledge/domain_contract.md bundle file)
# instead of a generic ISO-scaffold. Discovered via capability_generators._base.
# get_domain_contract (module-level convention -- see that function's docstring).
#
# SINGLE SOURCE OF TRUTH: every value below is a REFERENCE to one of the SAME 5 module
# constants build() reads above (_PALETTE_ROLES, _HEX_RE, _DEFAULT_TYPEFACES,
# _LOGO_DEFAULTS, _IMAGERY_DEFAULTS) -- never a re-typed literal -- so an exported bundle
# can never drift from what build() actually enforces at runtime. The ONE derived step is
# a mechanical filter over _LOGO_DEFAULTS using the SAME "[fornecer:" placeholder marker
# this module's own NEVER-FABRICATE convention already uses (see the module docstring): a
# live filter over the SAME list elements, splitting the 2 fixed law lines (protection
# space, no-distortion rule) from the 4 placeholder scaffold lines -- never a hand-copied
# second list.
#
# HONEST FRAMING (what is deliberately NOT included, and why): the Identidade/Persona/
# Framework de Mensagem/Dos-e-Nao-Faca sections build their rows from literals INSIDE
# their own functions (_identity_rows / _persona_rows / _messaging_rows / _dodonts_rows),
# not module-level constants -- including the formal/casual tone heuristic in
# _persona_rows. There is nothing to reference there without either re-typing (a second,
# driftable copy of the same fact) or refactoring those functions (out of scope for this
# seam). Rather than fabricate a structure that is not truly a standalone constant, this
# domain_contract() stays scoped to the 5 real constants + says so explicitly in `notes`.
# GENERATOR_VERSION (brandbook.py never declared a separate CONTRACT_VERSION) is reused
# verbatim as the versioning field, matching the same constant structured_output() itself
# introspects for the artifact envelope.
# --------------------------------------------------------------------------- #
def domain_contract() -> dict:
    """The REAL domain law brandbook.py enforces on every generated brandbook artifact
    (Missao A). Returns a structured, JSON-serialisable dict -- never {} for THIS
    generator (brandbook DOES declare domain law: the palette role hierarchy, the hex
    validation pattern, the logo-usage law split from its own scaffold placeholders, and
    the typography/imagery field scaffolds; {} is only the _base.py no-op default for a
    generator with none)."""
    return {
        "contract_version": GENERATOR_VERSION,
        "palette_role_hierarchy": list(_PALETTE_ROLES),
        "hex_color_validation_pattern": _HEX_RE.pattern,
        "logo_usage_law": [line for line in _LOGO_DEFAULTS if "[fornecer:" not in line],
        "logo_usage_scaffold": [line for line in _LOGO_DEFAULTS if "[fornecer:" in line],
        "typography_fields_scaffold": [
            {"field": label, "default_scaffold": value} for (label, value) in _DEFAULT_TYPEFACES
        ],
        "imagery_style_fields_scaffold": [
            {"field": label, "default_scaffold": value} for (label, value) in _IMAGERY_DEFAULTS
        ],
        "notes": [
            "brandbook.py declares no standalone voice/tone enum or output-section-title "
            "constant -- persona/identity/messaging/do-donts content is generated inline "
            "per-run inside its own functions (_identity_rows/_persona_rows/_messaging_rows/"
            "_dodonts_rows), not module-level constants, so it is not represented here "
            "(never re-typed, to avoid a second, driftable copy of the same fact).",
            "the 8 output_sections themselves (Identidade da Marca/Paleta de Cores/"
            "Tipografia/Persona da Marca/Uso do Logotipo/Estilo de Imagem/Framework de "
            "Mensagem/Dos e Nao-Faca) are a frozen structural contract enforced by build()'s "
            "section assembly -- see this module's own docstring for the full ordered list.",
        ],
    }


__all__ = [
    "KIND",
    "GENERATOR_VERSION",
    "RUN_MODE",
    "build",
    "media_requests",
    "produced_media",
    # Missao A / MOLDED_REAL_SEAM: the real domain-law contract (cex_export_agent.py).
    "domain_contract",
]
