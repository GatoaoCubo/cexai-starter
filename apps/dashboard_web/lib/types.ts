// ----------------------------------------------------------------------------
// Wire contract types -- mirror apps/dashboard_api (the BACKEND is the source of
// truth; aligned to its tested endpoints, NOT the spec's B.3 draft paths).
//
//   GET  /capabilities          -> { tenant_id, capabilities: Card[] }
//   POST /capability/run         -> { capability, intent, options? } ->
//                                   CapabilityResultView  (SYNCHRONOUS -- the run
//                                   completes in one call; there is no run_id/poll)
//   GET  /results?capability=    -> { tenant_id, capability, results: ResultRow[],
//                                     note? }
//
// These are the ONLY shapes the frontend trusts. The backend resolves tenant_id
// from the verified JWT; the client never sends or sets it.
// ----------------------------------------------------------------------------

// MoldSection is the frozen output-section shape (lib/molds). A real generator emits
// these with REAL data (the molded-real seam) -- the SAME shape the mock mold uses.
import type { MoldField, MoldSection } from "@/lib/molds";
// MediaSlot is the editable media-slot shape (lib/dual_output_contract) -- one face of
// the dual-output asset's media ledger, rendered by DualOutputFace.
import type { MediaSlot } from "@/lib/dual_output_contract";

/**
 * One capability card. GET /capabilities returns these, ORGANIC per tenant
 * overlay. Mirrors cex_capability_registry.CapabilityRecord.to_card().
 */
export interface Card {
  /** stable capability id the dashboard sends back (e.g. "research"). */
  capability: string;
  /** human label for the card (e.g. "Research"). */
  label: string;
  /** which nucleus runs it (N01..N06) -- shown as provenance, not control. */
  nucleus: string;
  /** icon key resolved client-side to a glyph (lib/icons.tsx). */
  icon: string;
  /** whether this card is enabled for the tenant. Disabled => shown muted. */
  enabled: boolean;
  /** "base" (catalog) or "overlay" (tenant-custom). */
  source: string;
  /** richer title from the registry (falls back to label). */
  title?: string;
  /** optional one-line description from the registry. */
  description?: string;
  /** optional: kind/pillar/verb for the "function signature" line. */
  kind?: string;
  pillar?: string;
  verb?: string;
  /** seed text for the intent box (registry default_intent_hint). */
  default_intent_hint?: string;
  /**
   * OPTIONAL typed input contract (mission BRANDBOOK, Cell A). When present, the run
   * cockpit renders a TYPED FORM (one control per field) instead of the single free-text
   * intent box -- a field of type ``file`` (any-media upload), ``url``, or ``text`` alongside
   * the existing string/number/enum scalars. The backend RESOLVES rich materials (an uploaded
   * image -> a palette; an uploaded doc / a URL -> extracted text) before handing them to the
   * generator. Absent -> the free-text intent box (degrade-never). MIRRORS lib/molds.MoldField;
   * the registry's to_card() populates it per capability.
   */
  input_contract?: MoldField[];
}

/** GET /capabilities response envelope. */
export interface CapabilitiesResponse {
  tenant_id: string;
  capabilities: Card[];
}

// ----------------------------------------------------------------------------
// COMPOSITION CONTROL PLANE (mission DASHBOARD_COMPOSITION W2/W3).
//
//   GET   /capabilities-config                            -> CapabilitiesConfigResponse
//   PATCH /capabilities/{slug}  { action: attach|detach }  -> CapabilitiesConfigResponse
//
// The per-tenant ATTACH state behind the compose UI (ModuleManager). ``declared`` is
// the full module universe the tenant overlay exposes; ``enabled`` is the attached (ON)
// subset that renders as cards + can run; ``disabled`` is the declared-but-OFF subset.
// The grid (GET /capabilities) shows ONLY the enabled set -- attach makes a card appear,
// detach hides it (the dashboard re-composes). tenant_id is server-derived from the
// verified JWT; the client never sends it (mirrors every other endpoint).
// ----------------------------------------------------------------------------

/** The tenant's capability ATTACH state -- the compose UI's whole data source. */
export interface CapabilitiesConfig {
  /** every capability the tenant overlay declares (the module universe). */
  declared: string[];
  /** the attached (ON) subset -- these render as cards and can run. */
  enabled: string[];
  /** the declared-but-OFF (attached-but-off) subset. */
  disabled: string[];
}

/** GET /capabilities-config + PATCH /capabilities/{slug} response envelope. */
export interface CapabilitiesConfigResponse extends CapabilitiesConfig {
  tenant_id: string;
}

/**
 * Lifecycle of one capability run, as the UI models it. The backend run is
 * SYNCHRONOUS (POST /capability/run returns the result in one shot), so these
 * states are driven CLIENT-SIDE around the single request:
 *   running -> done | error
 * ("started" is retained as an initial UI tick before the request resolves.)
 */
export type RunStatus = "started" | "running" | "done" | "error";

/**
 * The result view of a run. Mirrors the backend CapabilityResult projection
 * (apps/dashboard_api/main.py::_result_to_view): the API NEVER includes any
 * credential/api_key. The 8F trace is shown verbatim.
 */
export interface CapabilityResultView {
  tenant_id: string;
  capability: string;
  kind: string;
  pillar: string;
  nucleus: string;
  /** the produced artifact (frontmatter + body). */
  artifact: string;
  /** F7 structural score (0..10). */
  score: number;
  /** gate result. */
  passed: boolean;
  /** produced | persisted | produced_unpersisted | error. */
  status?: string;
  /** the F5 model string actually used. */
  model_used?: string;
  /** row id in the tenant's own Supabase (tenant_data), if persisted. */
  record_id?: string | null;
  /** true iff the artifact landed in the tenant DB. */
  persisted?: boolean;
  /** the F1..F8 trace string. */
  trace?: string;
  errors?: string[];
  /**
   * OPTIONAL structured payload (ADDITIVE -- the core projection is unchanged). Three
   * shapes attach a typed report here so the UI can render a READABLE REPORT instead of raw MD:
   *   * ``pesquisa_produto``   -> ProductResearchResult (~30-field marketplace report)
   *   * ``research_universe``  -> ResearchUniverseReport (multi-source orchestrator report)
   *   * a molded-real capability -> MoldedStructuredResult (mold_id + REAL output_sections)
   * Absent for every other capability -- ResultView routes ONLY when this is present,
   * discriminating the shapes (a molded result carries ``mold_id`` -- checked FIRST; a
   * universe report carries ``seed_type`` + ``endpoint_status``; a product result has
   * neither -- mirrors the backend ``main.py::_is_universe_report`` + ResultView.asMold).
   * Degrade-never: a result that omits it still renders via the generic artifact view.
   */
  structured?:
    | ProductResearchResult
    | ResearchUniverseReport
    | MoldedStructuredResult;
  /**
   * OPTIONAL string projection of the report (the ?render_format=md|html path). The
   * backend attaches this ONLY when a run was requested with render_format set; for a
   * research_universe result it is the ``render_universe`` MD/HTML projection. Absent
   * by default (the structured report is the canonical surface). Mirrors
   * ``main.py`` view["render"].
   */
  render?: string;
  /** which projection ``render`` carries ("md" | "html"), echoed by the backend. */
  render_format?: string;
  /**
   * OPTIONAL mold id (ADDITIVE -- backward-compatible). When set, this result is a
   * MOLDED capability result: the typed I/O CONTRACT of a capability whose real
   * generator does not exist yet (the "mold" the founder pins before building).
   * ResultView routes it to <StructuredResultView> (the generic molded-result
   * view), discriminating it BEFORE the two bespoke verticals so a molded result
   * never misroutes to the product/universe renderer (see ResultView.asMold). The
   * id keys into the MOLDS registry (lib/molds.ts). Absent for every non-molded
   * result -> the existing routing (universe -> product -> generic) is unchanged.
   */
  mold_id?: string;
  /**
   * OPTIONAL example INPUT object for a molded result (key -> example value), built
   * from the mold's input_contract (lib/molds.inputExampleFor). It is the contract
   * "filled with an example" the UI surfaces; a real call would shape its form
   * payload after this. Absent for non-molded results.
   */
  input_example?: Record<string, unknown>;
  /**
   * OPTIONAL dual-output asset (ADDITIVE -- backward-compatible). A structured-generator
   * capability emits ONE asset with TWO coupled faces (mission DUAL2 -> W5; founder
   * directive 2026-06-21): the MACHINE face (.md + YAML the tenant's AI reads) and the
   * HUMAN audiovisual face (media slots: real <img>/<video>/<audio> when produced, an
   * editable upload-fallback when not). The backend forwards the raw cex_dual_output
   * .to_dual_output projection verbatim (main.py::_result_to_view). DualOutputFace renders
   * the human face ABOVE the routed body. Absent on 8F-build / universe / pesquisa kinds
   * -> ResultView renders exactly today's body (degrade-never).
   */
  dual_output?: DualOutputResult;
}

/**
 * The raw dual-output asset the backend forwards (cex_dual_output.to_dual_output): the
 * shared id + both coupled faces, FLAT + snake_case (the Python emitter shape, NOT the
 * reshaped DualOutputContract). DualOutputFace reads it defensively (it also tolerates a
 * reshaped {machine:{md}, human:{mediaSlots}} contract). Every field is optional so a thin
 * asset still renders. NO credential ever appears here (a pure structural projection).
 */
export interface DualOutputResult {
  /** the shared id coupling the two faces (the persisted tenant record id at runtime). */
  id?: string;
  /** the capability that produced the asset (e.g. "research", "marketplace_listing"). */
  capability?: string;
  /** the MACHINE face: the canonical .md + YAML frontmatter the tenant's AI reads. */
  machine_md?: string;
  /** the HUMAN face HTML export (a string; DualOutputFace renders from media_slots, NOT this). */
  human_html?: string;
  /** the editable media slots -- the audiovisual ledger DualOutputFace renders. */
  media_slots?: MediaSlot[];
  /** the parsed machine frontmatter (id/capability/tenant/created/media[]/...). */
  frontmatter?: Record<string, unknown>;
  /** true => a real run (the face shows "resultado real"); false => molded/simulated. */
  real?: boolean;
  /** any extra emitter keys (e.g. a reshaped machine/human projection); never dropped. */
  [key: string]: unknown;
}

/**
 * The response of PATCH /capability/{record_id}/media/{slot_key} -- the upload-persist wire. A
 * human upload was stored (base64-inline V1) and persisted into the slot: the regenerated
 * dual_output + the single updated slot (now status "generated" with the stored src) + lean
 * stored metadata. The DualOutputFace reads ``slot.src`` to flip the slot to "persisted".
 */
export interface UploadedMedia {
  tenant_id?: string;
  record_id?: string;
  slot_key?: string;
  /** the regenerated dual-output asset (media ledger + base64-elided machine .md). */
  dual_output?: DualOutputResult;
  /** the single slot that was filled (status "generated", src = the stored media). */
  slot?: MediaSlot;
  /** lean metadata about the stored bytes (never the bytes themselves twice). */
  stored?: { content_type?: string; bytes?: number; stored_as?: string };
  /** true => the row was updated (read-modify-write succeeded). */
  persisted?: boolean;
}

// ----------------------------------------------------------------------------
// MOLDED-REAL structured payload (mission MOLDED_REAL_SEAM).
//
// What a REAL capability generator (cex_run_capability -> capability_generators) emits
// as ``structured``: the SAME MoldSection shape the mock mold uses, but with REAL data.
// ``mold_id`` keys into the MOLDS registry (lib/molds) so ResultView.asMold routes it to
// <StructuredResultView> (checked BEFORE the universe/product verticals). ``real: true``
// tells the renderer to render THESE output_sections (not the static mock) and to DROP the
// "dados simulados" chip. Backward-compatible: a mock molded result (no ``structured``) is
// unchanged; only a real run carries this object. NO credential/api_key ever appears here.
// ----------------------------------------------------------------------------
export interface MoldedStructuredResult {
  /** the capability/mold key (e.g. "custom_intake_form") -- routes via ResultView.asMold. */
  mold_id: string;
  /** the REAL output sections (same frozen MoldSection shape as the mock; real data). */
  output_sections: MoldSection[];
  /** true => a real run (the renderer drops "dados simulados" + shows "resultado real"). */
  real?: boolean;
  /** the generator's F7 self-score (0..1); the outcome strip shows the seam-scaled 0..10. */
  score?: number;
  /** the generator's F7 gate verdict for this output. */
  passed?: boolean;
  /** canonical MD/JSON projection (provenance; the persisted/results body). */
  artifact?: string;
  /** optional provenance / caveats the generator declared (never fabricated). */
  notes?: string[];
  /** any extra generator keys not named here (never silently dropped). */
  [key: string]: unknown;
}

// ----------------------------------------------------------------------------
// PRODUCT-RESEARCH structured payload (capability ``pesquisa_produto``).
//
// The typed projection of the ~30-field product-research result -- the SAME field
// names the backend renderer iterates (_tools/cex_output_contract.PESQUISA_PRODUTO_-
// CONTRACT). This is the READ shape ResearchResultView renders as a human report
// (price strip + competitors table + keyword/SEO chips + gaps/opportunities + a
// confidence badge + a ready_for_ads banner). Every field is OPTIONAL: a result that
// computed fewer fields renders the cells it has and omits the rest (TOTAL, never
// throws on a missing field -- mirrors the renderer's "blank on missing" contract).
//
// NO credential/api_key appears here (allowlist projection, like every other DTO).
// ----------------------------------------------------------------------------

/** Per-field provenance object (the renderer's ``data_sources`` / ``category_paths``). */
export type ProvenanceMap = Record<string, string | number | boolean>;

export interface ProductResearchResult {
  // --- identity / provenance (9) --------------------------------------------
  tenant_id?: string;
  run_id?: string;
  product_id?: string;
  product_name?: string;
  run_timestamp?: string;
  data_freshness?: string;
  marketplaces_queried?: string[];
  marketplaces_failed?: string[];
  data_sources?: ProvenanceMap;
  // --- gate (2) -------------------------------------------------------------
  /** F7-style confidence 0..10 (drives the badge colour). */
  confidence_score?: number;
  /** the canonical gate: confidence>=7.5 AND competitors>=1 AND price_min>0 AND head_terms>=1. */
  ready_for_ads?: boolean;
  // --- pricing (4) ----------------------------------------------------------
  price_band_min?: number;
  price_band_max?: number;
  price_avg?: number;
  sweet_spot_price?: number;
  // --- competitive (8) ------------------------------------------------------
  top_competitor_name?: string;
  top_competitor_rating?: number;
  top_competitor_reviews?: number;
  competitors_count?: number;
  gaps?: string[];
  opportunities?: string[];
  differentiation_angle?: string;
  recommended_positioning?: string;
  // --- keywords / SEO (6) ---------------------------------------------------
  head_terms?: string[];
  longtails?: string[];
  synonyms?: string[];
  seo_inbound?: string[];
  seo_outbound?: string[];
  negative_keywords?: string[];
  // --- filing (1) -----------------------------------------------------------
  category_paths?: ProvenanceMap;
  // --- mandatory anti-hallucination flag ------------------------------------
  /** honest mock flag (true => the report shows a "DADOS SIMULADOS" notice). */
  mock?: boolean;
  /** any extra producer keys the contract did not name (never silently dropped). */
  [key: string]: unknown;
}

// ----------------------------------------------------------------------------
// RESEARCH-UNIVERSE structured payload (capability ``research_universe``).
//
// The typed projection of the multi-source orchestrator report -- the SAME shape the
// orchestrator emits (_tools/cex_research_universe.py::_empty_report) and the backend
// passes through verbatim in CapabilityResultView.structured. UniverseResultView renders
// it as a human report: a header (seed + seed_type + fetched_at), a per-source STATUS row
// (chips from endpoint_status), and SECTION CARDS (one per non-null section) with per-lane
// provenance. Honest by construction: a null/absent section is shown as "not run / blocked"
// and NEVER fabricated; mock is ALWAYS false (a blocked lane is honest-blocked, not simulated).
//
// The orchestrator-level keys are strongly typed; each lane returns its OWN nested shape, so
// the section VALUES stay flexible (UniverseSection) -- the renderer walks them generically.
// NO credential/api_key appears here (the orchestrator emits a pure data dict).
// ----------------------------------------------------------------------------

/**
 * Per-lane endpoint status. The string STARTS WITH one of: "ok" | "blocked" | "skipped"
 * | "failed" (often with a ": reason" suffix). UniverseResultView prefix-matches to a
 * tone (ok=green, blocked/skipped=amber, failed=red).
 */
export type EndpointStatusMap = Record<string, string>;

/** Per-lane provenance: a list of source/provenance strings the lane reported. */
export type DataSourcesMap = Record<string, string[] | null | undefined>;

/**
 * One section's payload. Each lane (cnpj / ibge / reclame_aqui / seo / ...) returns its own
 * nested dict, so a section is a flexible record. ``null`` is the honest "not run / blocked"
 * state. A renderer reads known fields defensively and otherwise summarizes the keys present.
 */
export type UniverseSection = Record<string, unknown> | null;

/**
 * The rolled-up sentiment aggregate (sections.sentiment_summary). Mirrors
 * cex_research_universe._empty_sentiment_summary. ``label`` is the honest non-committal "NEU"
 * when nothing was analyzed; counts are 0 (never a fabricated polarity); ``mock`` is false.
 */
export interface SentimentSummary {
  /** POS | NEU | NEG (honest "NEU" when analyzed=0). */
  label?: string | null;
  pos?: number | null;
  neu?: number | null;
  neg?: number | null;
  /** how many texts were analyzed (0 => the aggregate is honestly empty). */
  analyzed?: number | null;
  /** the engine tier used ("lexicon" | "model" | ...), null when none ran. */
  method?: string | null;
  /** provenance for the analyzed texts, when present. */
  data_sources?: string[] | null;
  /** honest mock flag (ALWAYS false for the orchestrator's aggregate). */
  mock?: boolean | null;
  /** optional note (e.g. "sentiment engine unavailable"). */
  note?: string;
  [key: string]: unknown;
}

/**
 * The fixed section keys the orchestrator always emits (every key present, honest null when a
 * lane did not run). ``social`` is a sub-map of {appstore?, reddit?, youtube?} records.
 */
export interface UniverseSections {
  /** CNPJ firmographics (cnpj lane). */
  identity?: UniverseSection;
  /** reserved alias slot (identity carries the cnpj record). */
  firmographics?: UniverseSection;
  /** IBGE market sizing (ibge lane). */
  market?: UniverseSection;
  /** Reclame Aqui reputation (reclame_aqui lane). */
  reputation?: UniverseSection;
  /** appstore / reddit / youtube sub-records. */
  social?: Record<string, UniverseSection> | null;
  /** SEO autocomplete keywords (seo lane). */
  keywords?: UniverseSection;
  /** multi-perspective question pool (questions lane). */
  questions?: UniverseSection;
  /** the rolled-up sentiment aggregate. */
  sentiment_summary?: SentimentSummary | null;
  [key: string]: unknown;
}

export interface ResearchUniverseReport {
  /** the input seed (a product / brand / CNPJ / app id / keyword). */
  seed?: string;
  /** the resolved seed type (cnpj | app | keyword | company | brand | ...). */
  seed_type?: string;
  /** the lanes the orchestrator actually attempted. */
  lanes_run?: string[];
  /** the lanes selected for this seed (the routing decision). */
  selected_lanes?: string[];
  /** the fixed-key section map (one entry per lane; honest null when not run). */
  sections?: UniverseSections;
  /** per-lane status -- the STATUS CHIPS source (ok | blocked | skipped | failed). */
  endpoint_status?: EndpointStatusMap;
  /** per-lane provenance strings. */
  data_sources?: DataSourcesMap;
  /** ISO-8601 capture timestamp, or null. */
  fetched_at?: string | null;
  /** honest mock flag (ALWAYS false -- a blocked lane is honest-blocked, never simulated). */
  mock?: boolean;
  /** any extra orchestrator keys not named here (never silently dropped). */
  [key: string]: unknown;
}

/**
 * One row of GET /results -- tenant-scoped recent artifacts. Mirrors the backend
 * row shape (apps/dashboard_api/main.py::_normalize_rows): {id, capability, kind,
 * created_at}. ``label``/``nucleus``/``score`` are optional convenience fields
 * the UI fills in from the card catalog (the backend row does not carry them).
 */
export interface ResultRow {
  id: string;
  capability: string;
  kind?: string;
  created_at: string;
  /** UI-derived (joined from the card catalog), not from the backend row. */
  label?: string;
  nucleus?: string;
  score?: number | null;
  /**
   * OPTIONAL canonical projection of the stored artifact (the ?render_format=md|html
   * path). The backend attaches this PER ROW only when GET /results is requested with
   * render_format set (main.py::_project_rendered_rows -> _render_payload): a persisted
   * research_universe row projects via render_universe, a product row via the marketplace
   * render, a plain row surfaces its canonical MD. Absent on the default (light) scan.
   * This is the ONLY artifact body the /results ledger carries -- there is NO
   * single-artifact-by-id GET on the backend, and the row does NOT carry the raw
   * ``structured`` payload (only this rendered string). The deep-link/inline view renders
   * THIS string (degrade-to-ledger-data, never fabricated).
   */
  render?: string;
}

/** GET /results response envelope. */
export interface ResultsResponse {
  tenant_id: string;
  capability?: string | null;
  results: ResultRow[];
  note?: string;
}

/** Identity the UI shows. tenant_id is read from the session, never set here. */
export interface SessionContext {
  email: string;
  tenant_id: string;
  /** display name for the tenant if the backend/overlay provides one. */
  tenant_label?: string;
  /** the raw access token, used as Bearer for backend calls. */
  access_token: string;
}

/** Normalized error surfaced to the UI. */
export interface ApiError {
  status: number;
  message: string;
  /** machine reason from the backend (e.g. capability_disabled). */
  reason?: string;
}

// ----------------------------------------------------------------------------
// HOME / ANALYTICS SHELL contract (GET /summary).
//
// A tenant-scoped overview the backend derives from the SAME data the cards +
// results read. No values are invented client-side: every number here is a
// projection of the tenant's own capabilities / results / integration health.
// Until the backend ships /summary, FIXTURES mode derives this shape locally
// (lib/fixtures.fxGetSummary) -- the component is identical in both modes.
// ----------------------------------------------------------------------------

/** One headline stat on the home shell (label + value, optional sub-line). */
export interface SummaryStat {
  /** stable key (e.g. "capabilities_enabled"). */
  key: string;
  label: string;
  value: number | string;
  /** optional context line under the number (e.g. "of 7 in catalog"). */
  hint?: string;
  /** optional tone for the value -- "synapse" | "signal" | "muted". */
  tone?: "synapse" | "signal" | "muted";
}

/** One row in the health/status strip (a wired surface + its live state). */
export interface HealthRow {
  /** stable key (e.g. "data_plane"). */
  key: string;
  label: string;
  /** ok = green, degraded = amber, down = red, unknown = grey. */
  state: "ok" | "degraded" | "down" | "unknown";
  /** short status detail (e.g. "RLS on . fixtures"). */
  detail?: string;
}

/** GET /summary response envelope -- the home shell's whole payload. */
export interface SummaryResponse {
  tenant_id: string;
  stats: SummaryStat[];
  /** the most recent runs (same shape the Results ledger uses). */
  recent: ResultRow[];
  health: HealthRow[];
}

// ----------------------------------------------------------------------------
// SETTINGS / TENANT SHELL contract (GET /settings).
//
// SECURE-BY-DEFAULT: the secrets surface reports CONFIGURED STATUS ONLY. A
// secret value is NEVER part of this shape -- the backend returns whether each
// named secret is present, never the value. The client cannot render what it
// is not given. Integrations report connection status, also value-free.
// ----------------------------------------------------------------------------

/** One integration the tenant overlay declares (status only -- no credentials). */
export interface IntegrationStatus {
  /** stable key (e.g. "mercadolivre"). */
  key: string;
  label: string;
  /** connected = wired + healthy, available = offered but not wired, error = wired but failing. */
  state: "connected" | "available" | "error";
  /** optional provenance line (e.g. "OAuth . api_client_meli"). */
  detail?: string;
}

/**
 * One secret's CONFIGURED STATUS. NEVER carries the value -- only whether the
 * named secret is present in the tenant's Vault. ``last_rotated`` is optional
 * metadata (ISO date), again never the secret itself.
 */
export interface SecretStatus {
  /** the secret NAME (e.g. "MERCADOLIVRE_CLIENT_SECRET") -- a name, not a value. */
  name: string;
  /** human label / what it's for. */
  label?: string;
  /** true iff the Vault has this secret configured. The value is never sent. */
  configured: boolean;
  /** optional ISO date of last rotation (metadata only). */
  last_rotated?: string;
}

/** GET /settings response envelope -- the tenant shell's whole payload. */
export interface TenantSettings {
  tenant_id: string;
  tenant_label?: string;
  /** the signed-in operator's email (provenance). */
  operator_email?: string;
  /** how identity/tenant binding works for this tenant (display copy). */
  identity_note?: string;
  integrations: IntegrationStatus[];
  /** status-only secret surface (Vault). Values are NEVER present. */
  secrets: SecretStatus[];
}

// ----------------------------------------------------------------------------
// GENERIC TENANT-DRIVEN CRUD contract (the "management" primitive).
//
// A DataManager renders a DataTable + edit form for ANY entity by being handed
// an EntitySchema (columns + fields + the entity name + the api slug). NOTHING
// about a specific entity is hardcoded in the component -- products, contacts,
// leads, etc. all plug in by passing a schema. The records are plain key->value
// maps so the same component serves every shape.
//
// SECURE-BY-DEFAULT: every write goes through ApiClient (auth'd Bearer); the
// client never sets tenant_id (the backend derives it from the JWT, RLS is the
// boundary). FIXTURES mode services these against an in-memory store.
// ----------------------------------------------------------------------------

/** A cell value in a generic record. Kept primitive so any entity fits. */
export type FieldValue = string | number | boolean | null;

/** One generic entity record: a flat map plus a stable id. */
export interface EntityRecord {
  id: string;
  /**
   * SPEC 10 W1 -- the L2 PUBLISH gate (TOP-LEVEL tenant_data columns, NOT payload). Surfaced
   * by EntityManager.list() so the DataManager renders the HONEST published/draft chip at rest;
   * the Publish/Unpublish toggle flips ``published`` via PATCH /entity/{slug}/{id}/publish. Both
   * optional + within FieldValue -> a non-publishable entity's record is byte-identical to before.
   */
  published?: boolean;
  published_at?: string | null;
  // ``| undefined`` so the optional named gate fields above are assignable to the index type
  // (a named optional widens its value type with undefined); any other key stays a FieldValue.
  [key: string]: FieldValue | undefined;
}

/** A column shown in the DataTable (read view). */
export interface EntityColumn {
  /** the record key this column reads. */
  key: string;
  /** column header. */
  label: string;
  /** render hint -- controls formatting only, never logic. */
  type?: "text" | "number" | "badge" | "boolean" | "date" | "currency";
  /** optional: this column is the row's primary label (bolded). */
  primary?: boolean;
  /** optional: align right (numbers). */
  align?: "left" | "right";
  /**
   * SECURE-BY-DEFAULT margin guard. When true this column is SENSITIVE (cost,
   * B2B price, margin, ...) and is EXCLUDED from the default table view for
   * EVERY tenant entity -- the leak is prevented BY CONSTRUCTION, not by a
   * per-tenant opt-in. A tenant marks a column ``admin_only`` in its overlay;
   * the projection (entities_config.py) passes it through and DataManager never
   * renders it in the default view. (``sensitive`` is accepted as a synonym in
   * the overlay; both project to this flag.)
   */
  admin_only?: boolean;
}

/** One editable field in the create/update form. */
export interface EntityField {
  /** the record key this field writes. */
  key: string;
  label: string;
  /** input kind. "select" uses ``options``; "textarea" for long text. */
  type: "text" | "number" | "textarea" | "select" | "boolean" | "date";
  required?: boolean;
  placeholder?: string;
  /** options for type=select. */
  options?: { value: string; label: string }[];
  /** optional helper text under the field. */
  help?: string;
  /**
   * SECURE-BY-DEFAULT margin guard (mirror of EntityColumn.admin_only). When
   * true this field is SENSITIVE and is EXCLUDED from the default edit form, so
   * the value is neither shown nor editable in the default surface for every
   * tenant entity. (``sensitive`` is accepted as a synonym in the overlay.)
   */
  admin_only?: boolean;
}

/**
 * The whole contract for ONE manageable entity. Pass this to <DataManager/> and
 * the table + form + CRUD wiring are generated. This object is what a tenant
 * overlay would supply (config-driven, not hardcoded per entity).
 */
export interface EntitySchema {
  /** stable slug used as the api path segment (e.g. "contacts"). */
  entity: string;
  /** singular noun for buttons/headings (e.g. "Contact"). */
  singular: string;
  /** plural noun for headings (e.g. "Contacts"). */
  plural: string;
  /** one-line description shown under the heading. */
  description?: string;
  /** which nucleus/kind backs this entity (provenance chip), optional. */
  nucleus?: string;
  /** icon key (lib/icons) for the shell, optional. */
  icon?: string;
  columns: EntityColumn[];
  fields: EntityField[];
  /** whether writes are allowed for this tenant/role (read-only if false). */
  writable?: boolean;
  /**
   * SPEC 10 W1 -- the L2 PUBLISH gate. When true, each row gets a Publish/Unpublish toggle
   * (DataManager) that flips the row's top-level ``published`` column via PATCH
   * /entity/{slug}/{id}/publish, making it eligible for the L2 anon public site (or retracting
   * it). The row's own ``published`` field drives the honest published/draft state. Absent /
   * false -> no toggle renders (zero-regression: a non-public entity is byte-identical to
   * before). A tenant opts an entity in via its overlay (``publishable: true``).
   */
  publishable?: boolean;
}

/** GET /entity/{slug} response envelope. */
export interface EntityListResponse {
  tenant_id: string;
  entity: string;
  records: EntityRecord[];
  note?: string;
}

/**
 * GET /entities-config response envelope -- the tenant's MANAGED-ENTITY SCHEMAS, sourced
 * from the tenant overlay (``managed_entities``), NOT a static map. This is the mold's
 * tenant-generic seam: a tenant declares which entities it manages (and their schema) in
 * its overlay; the management nav + routes are built from this list. MIRRORS the cards
 * path (GET /capabilities) -- one overlay file drives both surfaces. tenant_id is
 * server-derived from the JWT; the client never sends it.
 */
export interface EntitiesConfigResponse {
  tenant_id: string;
  entities: EntitySchema[];
}

// ----------------------------------------------------------------------------
// AGENTS catalog + READ surface contract (ADR adr_agents_sdk_dashboard, Phase A).
//
// An "Agent" in the dashboard is a typed catalog record (the agents-SDK layer
// ABOVE the single-shot capability card). This is the READ half only -- browse +
// inspect. There is NO run wire here: running an agent is a multi-step loop that
// lands in Phase B/C. The shapes MIRROR the backend Agent DTO
// (apps/dashboard_api/agents_config.py), aligned to its endpoints:
//
//   GET  /agents          -> { tenant_id, agents: Agent[] }   (overlay-gated, like cards)
//   GET  /agents/{id}      -> { tenant_id, agent: AgentDetail }
//
// tenant_id is server-derived from the JWT; the client never sends it. The DTO is
// a SECRET-FREE allowlist -- there is no credential/api_key field anywhere here.
// ----------------------------------------------------------------------------

/**
 * One agent in the catalog list. GET /agents returns these, overlay-gated per
 * tenant (the overlay ``agents:`` block enables/disables, exactly like a card's
 * enabled flag). Mirrors agents_config._dto_from_record.
 */
export interface Agent {
  /** stable agent id (the route segment + lookup key), e.g. "agent_card_n03". */
  id: string;
  /** human name for the card (falls back to id). */
  name: string;
  /** which nucleus the agent belongs to (N01..N07) -- shown as a badge. */
  nucleus: string;
  /** the artifact kind backing it (agent | agent_card) -- shown in the signature line. */
  kind: string;
  /** pillar, when the catalog/disk carries it ('' otherwise). */
  pillar?: string;
  /** one-line "what this agent does" (first capability or the description). */
  goal?: string;
  /** longer description from the registry record. */
  description?: string;
  /** domain grouping label from the registry ('' when absent). */
  domain?: string;
  /** the agent's tool grants (the toolkit chips). Empty when none declared. */
  tools: string[];
  /** model / model-tier the agent runs on ('' when the record carries none). */
  model?: string;
  /** whether this agent is enabled for the tenant. Disabled => shown muted. */
  enabled: boolean;
  /** provenance of the catalog record (e.g. "nucleus_card", "aitmpl_catalog"). */
  source?: string;
}

/** One row in a capabilities table on the agent detail page. */
export interface AgentCapability {
  capability: string;
  description?: string;
  /** tools this capability requires (free text from the artifact table). */
  tools?: string;
}

/** One SLA / routing key-value row on the agent detail page. */
export interface AgentSla {
  label: string;
  value: string;
}

/**
 * The fuller agent detail (GET /agents/{id}). Extends Agent with the persona +
 * capabilities + typed I/O schemas + SLA parsed from the agent / agent_card on
 * disk WHEN resolvable; absent fields just don't render (degrade-never). The run
 * cockpit is NOT here -- Phase A is read-only; running is Phase B/C.
 */
export interface AgentDetail extends Agent {
  /** the persona / overview prose, parsed from the artifact. */
  persona?: string;
  /** the Capabilities table rows. */
  capabilities?: AgentCapability[];
  /** the agent's Input JSON Schema (raw string, rendered in a <pre>). */
  input_schema?: string;
  /** the agent's Output JSON Schema (raw string, rendered in a <pre>). */
  output_schema?: string;
  /** SLA / routing key-value rows. */
  sla?: AgentSla[];
  /** the source artifact path (provenance). */
  artifact_path?: string;
}

/** GET /agents response envelope. */
export interface AgentsResponse {
  tenant_id: string;
  agents: Agent[];
}

/** GET /agents/{id} response envelope. */
export interface AgentResponse {
  tenant_id: string;
  agent: AgentDetail;
}

// ----------------------------------------------------------------------------
// CREWS catalog + READ surface contract (ADR adr_agents_sdk_dashboard, Phase D).
//
// A "Crew" in the dashboard is a multi-role TEAM (a crew_template artifact) -- the
// layer ABOVE single agents. This is the READ half only -- browse + inspect. There
// is NO run wire here: running a crew is the founder-gated control-plane step. The
// shapes MIRROR the backend Crew DTO (apps/dashboard_api/crews_config.py), aligned
// to its endpoints:
//
//   GET  /crews          -> { tenant_id, crews: Crew[] }   (overlay-gated, like agents)
//   GET  /crews/{id}      -> { tenant_id, crew: CrewDetail }
//
// tenant_id is server-derived from the JWT; the client never sends it. The DTO is a
// SECRET-FREE allowlist -- there is no credential/api_key field anywhere here.
// ----------------------------------------------------------------------------

/** The process topology of a crew. Mirrors the crew_template ``process`` field. */
export type CrewProcess = "sequential" | "hierarchical" | "consensus";

/**
 * One role in a crew's Roles table. ``agent`` is the role_assignment / agent binding;
 * ``goal`` is the reason/why; ``tools`` is supplementary context (never a secret).
 * Parsed from the crew_template Roles table -- absent fields just don't render.
 */
export interface CrewRole {
  /** the role_name (e.g. "market_researcher"). */
  name: string;
  /** the bound agent / role_assignment id (e.g. "p02_ra_copywriter.md"), when present. */
  agent?: string;
  /** the role's goal / reason (the "why this role") from the table. */
  goal?: string;
  /** optional supplementary context (e.g. a provider column). */
  tools?: string;
}

/**
 * One crew in the catalog list. GET /crews returns these, overlay-gated per tenant
 * (the overlay ``crews:`` block enables/disables, exactly like an agent's enabled
 * flag). Mirrors crews_config._dto_from_record.
 */
export interface Crew {
  /** stable crew id (the route segment + lookup key), e.g. "product_launch". */
  id: string;
  /** human name for the card (the crew_template title; falls back to the id). */
  name: string;
  /** which nucleus owns the crew (N01..N07) -- shown as a badge. */
  nucleus: string;
  /** the artifact kind backing it (crew_template) -- shown in the signature line. */
  kind: string;
  /** pillar (P12 for crews). */
  pillar?: string;
  /** the process topology (sequential | hierarchical | consensus) -- shown as a chip. */
  process: CrewProcess | string;
  /** how many roles the crew runs. */
  role_count: number;
  /** the crew's roles (name + agent/goal/tools). The list view shows the names. */
  roles: CrewRole[];
  /** one-line "what this crew ships" (the crew purpose / tldr). */
  goal?: string;
  /** longer description (mirrors goal for crews). */
  description?: string;
  /** domain grouping label from the crew_template ('' when absent). */
  domain?: string;
  /** whether this crew is enabled for the tenant. Disabled => shown muted. */
  enabled: boolean;
  /** provenance of the catalog record (e.g. the crew_template author). */
  source?: string;
}

/**
 * The fuller crew detail (GET /crews/{id}). Extends Crew with the handoff protocol
 * + provenance parsed from the crew_template on disk; absent fields just don't render
 * (degrade-never). The run cockpit is NOT here -- Phase D is read-only; running a crew
 * is the next, gated phase. The roles table + process topology travel on Crew already.
 */
export interface CrewDetail extends Crew {
  /** the handoff protocol id (e.g. "a2a-task-sequential"). */
  handoff_protocol?: string;
  /** the Handoff Protocol section prose (parsed from the crew_template). */
  handoff_note?: string;
  /** the source artifact path (provenance). */
  artifact_path?: string;
}

/** GET /crews response envelope. */
export interface CrewsResponse {
  tenant_id: string;
  crews: Crew[];
}

/** GET /crews/{id} response envelope. */
export interface CrewResponse {
  tenant_id: string;
  crew: CrewDetail;
}

// ----------------------------------------------------------------------------
// AGENT RUN contract (ADR adr_agents_sdk_dashboard, Phase B -- the single-step run).
//
//   POST /agent/run  { agent_id, inputs }  -> AgentRunResult   (SYNCHRONOUS, 1 step)
//
// SYNCHRONOUS, like POST /capability/run: the backend resolves the agent, ASSEMBLES
// its real contract (persona + Input/Output Schema + declared tools), runs ONE
// CEXAgent.build (one chat()), optionally persists, and returns the full result in
// ONE call -- there is NO run_id/poll (async + the multi-step tool loop are Phase C).
//
// The result MIRRORS CapabilityResultView (the SAME _result_to_view projection, no
// credential) plus the agent identity (agent_id/agent_name) + steps (always 1 here).
// ``inputs`` is the TYPED form payload (per the agent's Input Schema); an agent with
// no schema falls back to a single free-text intent carried as { intent: "..." }.
// tenant_id is server-derived from the JWT; the client never sends it.
// ----------------------------------------------------------------------------

/**
 * The result of one single-step agent run. Extends the capability result shape with
 * the agent identity. The API NEVER includes any credential/api_key (allowlist
 * projection). ``steps`` is 1 for this single-step contract (Phase C grows it).
 */
export interface AgentRunResultView extends CapabilityResultView {
  /** the agent that ran (echoed from the request). */
  agent_id: string;
  /** the agent's human name (provenance). */
  agent_name?: string;
  /** number of steps executed -- always 1 in the single-step contract. */
  steps?: number;
}

// ----------------------------------------------------------------------------
// ASYNC MULTI-STEP agent run contract (ADR adr_agents_sdk_dashboard, Phase C).
//
// The multi-step plan/act/observe runtime ABOVE the single-step run. Because a
// multi-step run is no longer instantaneous, the contract is ASYNC: the kickoff
// returns a run_id, and the client polls status OR streams step events.
//
//   POST /agent/runs            { agent_id, inputs, options? } -> AgentRunStarted (202)
//   GET  /agent/run/{run_id}     -> AgentRun                    (poll snapshot; OQ3 fallback)
//   GET  /agent/run/{run_id}/events -> SSE stream of AgentRunEvent  (OQ3 SSE transport)
//
// NOTE: POST /agent/run (singular) STAYS the SYNCHRONOUS single-step (Phase B)
// path; /agent/runs (plural) is the async multi-step entry. tenant_id is always
// server-derived from the JWT; a run_id is NOT a capability (the backend re-checks
// the run's tenant against the caller -> a foreign run_id is 404). The shapes
// MIRROR the backend agent_runs.py snapshots; no credential/api_key appears.
// ----------------------------------------------------------------------------

/** The status of an async agent run. Mirrors the agent_runs.status column. */
export type AgentRunStatus =
  | "running"
  | "completed"
  | "failed"
  | "refused"
  | "budget_exceeded";

/** The kind of one step in a multi-step run. Mirrors agent_steps.kind. */
export type AgentStepKind = "plan" | "act" | "observe" | "tool";

/**
 * One step of a multi-step agent run. Mirrors the backend agent_steps row /
 * cex_agent_loop.AgentStep view. ``tool``/``tool_io`` are present only on tool
 * steps; ``approval_id`` is set when an irreversible tool gated through HITL
 * (OQ8 emit-and-defer -- the tool was NOT executed, a human approval is pending).
 */
export interface AgentStep {
  /** 0-based order within the run. */
  index: number;
  kind: AgentStepKind;
  /** the step payload (reasoning / produced-artifact provenance / observation). */
  content: Record<string, FieldValue | FieldValue[] | Record<string, unknown>>;
  /** the tool name (tool steps only). */
  tool?: string | null;
  /** { args, result } for tool steps. */
  tool_io?: Record<string, unknown>;
  /** the pending HITL approval id when an irreversible tool was gated (OQ8). */
  approval_id?: string | null;
}

/**
 * The OQ4 budget accounting for a run -- the team_charter-style ceiling the loop
 * enforces (it STOPS + sets status 'budget_exceeded' when a ceiling is crossed).
 */
export interface AgentRunCost {
  steps_used: number;
  max_steps?: number | null;
  step_ceiling?: number;
  tokens_used?: number;
  max_tokens?: number | null;
}

/**
 * The full snapshot of an async agent run (GET /agent/run/{run_id}). Extends the
 * single-step result view with the run_id + the live step ledger + the budget
 * cost + a ``done`` flag. This is BOTH the poll payload and the terminal ``done``
 * SSE event body. No credential/api_key (allowlist projection).
 */
export interface AgentRun extends AgentRunResultView {
  /** the async handle -- the deterministic agent_runs row id the client polls. */
  run_id: string;
  /** the live run status. */
  status: AgentRunStatus | string;
  /** the plan/act/observe/tool step ledger, growing as the run progresses. */
  steps_log: AgentStep[];
  /** the OQ4 budget accounting (steps/tokens used vs the ceiling). */
  cost?: AgentRunCost;
  /** true once the run reached a terminal state. */
  done?: boolean;
}

/** POST /agent/runs response -- the async kickoff handle (HTTP 202). */
export interface AgentRunStarted {
  run_id: string;
  status: "running";
  tenant_id: string;
}

/**
 * One Server-Sent Event from GET /agent/run/{run_id}/events. The ``event:`` line
 * is the type; the ``data:`` line is the JSON below:
 *   - "step"      -> data is one AgentStep (a new step was recorded).
 *   - "done"      -> data is the terminal AgentRun snapshot.
 *   - "timeout"   -> data is { run_id, steps } (the stream capped before the run finished).
 *   - "not_found" -> data is { run_id } (the run is not the caller's tenant -> stream closes).
 */
export type AgentRunEventType = "step" | "done" | "timeout" | "not_found";

/** A decoded SSE frame from the events stream (the UI parses event+data). */
export interface AgentRunEvent {
  event: AgentRunEventType;
  /** the parsed ``data:`` JSON -- an AgentStep for "step", an AgentRun for "done", else a small object. */
  data: AgentStep | AgentRun | { run_id: string; steps?: number };
}
