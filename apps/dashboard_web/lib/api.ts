// ----------------------------------------------------------------------------
// Typed API client. ONE module the UI talks to. Two modes:
//
//   FIXTURES (config.fixtures)  -> in-memory mocks (lib/fixtures.ts), no network
//   REAL                        -> fetch against NEXT_PUBLIC_API_URL with the
//                                  Supabase JWT as `Authorization: Bearer <jwt>`
//
// Contract: the BACKEND (apps/dashboard_api/main.py) is the source of truth.
//   GET  /capabilities          -> { tenant_id, capabilities: Card[] }
//   POST /capability/run         { capability, intent, options? }
//                                -> CapabilityResultView  (SYNCHRONOUS: the run
//                                   completes in this one call -- no run_id/poll)
//   GET  /results?capability=    -> { tenant_id, capability, results, note? }
//
// Backend error envelope (all failures): { error: { type, reason, detail } }.
//
// INVARIANT: the client NEVER sends tenant_id. The backend derives it from the
// verified JWT. We only ever pass the bearer token.
// ----------------------------------------------------------------------------

import { config } from "./config";
import {
  fxCreateEntity,
  fxDeleteEntity,
  fxGetAgent,
  fxGetAgentRun,
  fxGetCapabilitiesConfig,
  fxGetCrew,
  fxGetSettings,
  fxGetSummary,
  fxListAgents,
  fxListCards,
  fxListCatalog,
  fxListCrews,
  fxListEntity,
  fxListEntitySchemas,
  fxListResults,
  fxRunAgent,
  fxRunCapability,
  fxSetCapability,
  fxSetEntityPublished,
  fxStartAgentRun,
  fxUpdateEntity,
  fxUploadSlotMedia,
} from "./fixtures";
import type {
  Agent,
  AgentDetail,
  AgentResponse,
  AgentRun,
  AgentRunResultView,
  AgentRunStarted,
  AgentsResponse,
  ApiError,
  CapabilitiesConfig,
  CapabilitiesConfigResponse,
  CapabilitiesResponse,
  Card,
  CapabilityResultView,
  Crew,
  CrewDetail,
  CrewResponse,
  CrewsResponse,
  EntitiesConfigResponse,
  EntityListResponse,
  EntityRecord,
  EntitySchema,
  ResultRow,
  ResultsResponse,
  SummaryResponse,
  TenantSettings,
  UploadedMedia,
} from "./types";

export class ApiClientError extends Error implements ApiError {
  status: number;
  reason?: string;
  constructor(status: number, message: string, reason?: string) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.reason = reason;
  }
}

/**
 * ONE row of the founder-side waitlist queue (GO_ONLINE A2, spec 23 FR-003).
 * Mirrors the promoted columns of supabase/migrations/20260711000001_
 * waitlist_intake.sql (id/email/wtp_band/brand_name/created_at) -- the light
 * ledger shape a queue table needs, not the full best-effort `answers` jsonb
 * blob. Defined HERE (not lib/types.ts) -- this lane's fence scopes the edit
 * to lib/api.ts only.
 */
export interface WaitlistRow {
  id: string;
  email: string;
  wtp_band: string | null;
  brand_name: string | null;
  created_at: string;
}

interface WaitlistResponse {
  rows: WaitlistRow[];
}

/** A client bound to one session's access token (the Bearer for backend calls). */
export class ApiClient {
  private token: string;

  constructor(accessToken: string) {
    this.token = accessToken;
  }

  private async req<T>(
    method: "GET" | "POST" | "PATCH" | "DELETE",
    path: string,
    body?: unknown,
  ): Promise<T> {
    if (!config.apiUrl) {
      throw new ApiClientError(
        0,
        "NEXT_PUBLIC_API_URL is not set. Set it, or run with NEXT_PUBLIC_FIXTURES=1.",
      );
    }
    let res: Response;
    try {
      res = await fetch(`${config.apiUrl}${path}`, {
        method,
        headers: {
          "content-type": "application/json",
          // The ONLY identity we send. No tenant_id -- the backend reads it
          // from this token's verified claim.
          authorization: `Bearer ${this.token}`,
        },
        body: body !== undefined ? JSON.stringify(body) : undefined,
        cache: "no-store",
      });
    } catch (err) {
      throw new ApiClientError(
        0,
        `Cannot reach the backend at ${config.apiUrl}. Is it running?`,
      );
    }

    if (!res.ok) {
      let reason: string | undefined;
      let message = `Request failed (${res.status}).`;
      try {
        const data = (await res.json()) as Record<string, unknown>;
        // The backend wraps every failure as { error: { type, reason, detail } }.
        const envelope = data.error;
        if (envelope && typeof envelope === "object") {
          const e = envelope as Record<string, unknown>;
          if (typeof e.reason === "string") reason = e.reason;
          if (typeof e.detail === "string" && e.detail) message = e.detail;
          else if (typeof e.reason === "string") message = e.reason;
        } else {
          // Defensive: tolerate a flat {detail|message|reason} body too.
          if (typeof data.detail === "string") message = data.detail;
          else if (typeof data.message === "string") message = data.message;
          if (typeof data.reason === "string") reason = data.reason;
        }
      } catch {
        // non-JSON error body; keep the default message
      }
      if (res.status === 401) message = "Your session expired. Sign in again.";
      throw new ApiClientError(res.status, message, reason);
    }

    if (res.status === 204) return undefined as T;
    return (await res.json()) as T;
  }

  // --- contract methods ------------------------------------------------------

  /** GET /capabilities -> the tenant's organic capability cards. */
  async listCards(): Promise<Card[]> {
    if (config.fixtures) return fxListCards();
    const body = await this.req<CapabilitiesResponse>("GET", "/capabilities");
    return body.capabilities ?? [];
  }

  // --- composition control plane (mission DASHBOARD_COMPOSITION W2/W3) ---
  //
  // The per-tenant ATTACH state behind the compose UI (components/ModuleManager).
  // MIRRORS listCards(): the JWT is the only identity sent; tenant_id is server-
  // derived. GET reads the {declared, enabled, disabled} state; PATCH attaches /
  // detaches ONE declared module and returns the NEW state. The grid (listCards)
  // re-composes after a toggle -- an attached module's card appears, a detached one
  // disappears (the backend GET /capabilities is filtered to the enabled set).

  /**
   * The FULL declared catalog metadata (mission BUILD C -- the compose picker's rich
   * source). Returns a Card for EVERY declared capability, enabled AND disabled, so the
   * picker can render rich "available to add" rows for the declared-but-disabled set that
   * {@link listCards} (live GET /capabilities) correctly OMITS (it is enabled-filtered).
   *
   * FIXTURES: resolves the full FIXTURE_CARDS metadata (fxListCatalog). LIVE: there is no
   * full-catalog endpoint yet, so this DEGRADES to [] -- the picker then falls back to a
   * humanized slug for available rows (exactly the pre-BUILD-C behaviour). Honest: never
   * fabricates a capability; it only enriches slugs the registry/overlay already declares.
   * tenant_id is server-derived (never sent), same as every other call.
   */
  async listCatalog(): Promise<Card[]> {
    if (config.fixtures) return fxListCatalog();
    // No live full-catalog route yet -> degrade to empty (the picker humanizes slugs).
    return [];
  }

  /** GET /capabilities-config -> the tenant's attach state (declared/enabled/disabled). */
  async getCapabilitiesConfig(): Promise<CapabilitiesConfig> {
    if (config.fixtures) return fxGetCapabilitiesConfig();
    const body = await this.req<CapabilitiesConfigResponse>(
      "GET",
      "/capabilities-config",
    );
    return {
      declared: body.declared ?? [],
      enabled: body.enabled ?? [],
      disabled: body.disabled ?? [],
    };
  }

  /**
   * PATCH /capabilities/{slug} { action } -> the NEW attach state. ``attach`` adds a
   * DECLARED module to the enabled set; ``detach`` removes it. FAIL-CLOSED on the
   * backend: an unknown action -> 400, an undeclared slug -> 409 (both surfaced as an
   * ApiClientError the caller renders inline, never a blank crash).
   */
  async setCapability(
    slug: string,
    action: "attach" | "detach",
  ): Promise<CapabilitiesConfig> {
    if (config.fixtures) return fxRun(() => fxSetCapability(slug, action));
    const body = await this.req<CapabilitiesConfigResponse>(
      "PATCH",
      `/capabilities/${encodeURIComponent(slug)}`,
      { action },
    );
    return {
      declared: body.declared ?? [],
      enabled: body.enabled ?? [],
      disabled: body.disabled ?? [],
    };
  }

  // --- agents catalog + READ surface (ADR Phase A) ---------------------------
  //
  // OVERLAY-GATED: GET /agents returns the tenant's visible agents from the agent
  // catalog + its overlay ``agents:`` block, EXACTLY as listCards() returns
  // overlay-gated capability cards. READ-ONLY -- there is no run wire here (running
  // an agent is the multi-step Phase B/C loop). tenant_id is server-derived from
  // the JWT; the client never sends it. MIRRORS listCards().

  /** GET /agents -> the tenant's visible agents (overlay-gated). */
  async listAgents(): Promise<Agent[]> {
    if (config.fixtures) return fxListAgents();
    const body = await this.req<AgentsResponse>("GET", "/agents");
    return body.agents ?? [];
  }

  /** GET /agents/{id} -> one agent's persona / capabilities / IO contract / SLA. */
  async getAgent(id: string): Promise<AgentDetail> {
    if (config.fixtures) return fxRun(() => fxGetAgent(id));
    const body = await this.req<AgentResponse>(
      "GET",
      `/agents/${encodeURIComponent(id)}`,
    );
    return body.agent;
  }

  // --- crews catalog + READ surface (ADR Phase D) ----------------------------
  //
  // The layer ABOVE single agents: a crew is a multi-role TEAM (crew_template).
  // OVERLAY-GATED: GET /crews returns the tenant's visible crews from the crew
  // catalog (the crew_template artifacts on disk) + its overlay ``crews:`` block,
  // EXACTLY as listAgents() returns overlay-gated agents. READ-ONLY -- there is no
  // run wire here (running a crew is the founder-gated control-plane step).
  // tenant_id is server-derived from the JWT; the client never sends it. MIRRORS
  // listAgents()/getAgent().

  /** GET /crews -> the tenant's visible crews (overlay-gated). */
  async listCrews(): Promise<Crew[]> {
    if (config.fixtures) return fxListCrews();
    const body = await this.req<CrewsResponse>("GET", "/crews");
    return body.crews ?? [];
  }

  /** GET /crews/{id} -> one crew's roles / process topology / handoff protocol. */
  async getCrew(id: string): Promise<CrewDetail> {
    if (config.fixtures) return fxRun(() => fxGetCrew(id));
    const body = await this.req<CrewResponse>(
      "GET",
      `/crews/${encodeURIComponent(id)}`,
    );
    return body.crew;
  }

  /**
   * POST /agent/run -- run ONE agent (single step) and return its result (ADR Phase B).
   * SYNCHRONOUS, exactly like runCapability: the backend resolves the agent, ASSEMBLES
   * its contract, runs ONE CEXAgent.build, (optionally) persists, and returns the full
   * AgentRunResultView in this single call -- there is NO run_id/poll (async + the
   * multi-step tool loop are Phase C). ``inputs`` is the typed form payload per the
   * agent's Input Schema, or { intent: "..." } free-text when the agent has no schema.
   * tenant_id is server-derived from the JWT; the client never sends it. CLONES
   * runCapability.
   */
  async runAgent(
    agentId: string,
    inputs: Record<string, unknown>,
    options?: Record<string, unknown>,
  ): Promise<AgentRunResultView> {
    if (config.fixtures) {
      try {
        return await fxRunAgent(agentId, inputs);
      } catch (err) {
        const e = err as { message?: string; status?: number; reason?: string };
        throw new ApiClientError(
          e.status ?? 400,
          e.message ?? "Agent run could not be started.",
          e.reason,
        );
      }
    }
    return this.req<AgentRunResultView>("POST", "/agent/run", {
      agent_id: agentId,
      inputs,
      ...(options ? { options } : {}),
    });
  }

  // --- ASYNC multi-step agent run (ADR Phase C) ------------------------------
  //
  // The multi-step plan/act/observe runtime ABOVE the single-step runAgent. Because
  // a multi-step run is no longer instantaneous, the contract is ASYNC: startAgentRun
  // kicks the run and returns a run_id (202); the cockpit then POLLS getAgentRun on an
  // interval until ``done``. POST /agent/runs (plural) is the async entry -- POST
  // /agent/run (singular) STAYS the synchronous single-step path. tenant_id is
  // server-derived from the JWT; the client never sends it. A run_id is NOT a
  // capability -- a foreign run_id resolves to 404 (the backend re-checks the run's
  // tenant against the caller). MIRRORS runAgent (both modes).
  //
  // TRANSPORT: the cockpit drives progress by POLLING getAgentRun (the documented OQ3
  // fallback), NOT the browser EventSource -- EventSource cannot send the
  // Authorization: Bearer header the backend requires, so polling the snapshot is the
  // auth-clean primary path (and it works identically in fixtures mode). A fetch-stream
  // SSE reader against /agent/run/{id}/events is a possible future live enhancement.

  /**
   * POST /agent/runs -- kick a MULTI-step agent run; returns the async handle (run_id)
   * IMMEDIATELY (HTTP 202). The run executes in the background; poll getAgentRun until
   * ``done``. ``inputs`` is the typed form payload per the agent's Input Schema, or
   * { intent: "..." } free-text when the agent has no schema. tenant_id is
   * server-derived from the JWT; the client never sends it. MIRRORS runAgent.
   */
  async startAgentRun(
    agentId: string,
    inputs: Record<string, unknown>,
    options?: Record<string, unknown>,
  ): Promise<AgentRunStarted> {
    if (config.fixtures) {
      try {
        return await fxStartAgentRun(agentId, inputs);
      } catch (err) {
        const e = err as { message?: string; status?: number; reason?: string };
        throw new ApiClientError(
          e.status ?? 400,
          e.message ?? "Agent run could not be started.",
          e.reason,
        );
      }
    }
    return this.req<AgentRunStarted>("POST", "/agent/runs", {
      agent_id: agentId,
      inputs,
      ...(options ? { options } : {}),
    });
  }

  /**
   * GET /agent/run/{run_id} -- the POLL snapshot of an async run (status + result +
   * the live step ledger + budget cost + a ``done`` flag). The cockpit polls this on
   * an interval until ``done``. A run owned by another tenant (or unknown) is 404
   * (mapped to ApiClientError by this.req). MIRRORS getAgent.
   */
  async getAgentRun(runId: string): Promise<AgentRun> {
    if (config.fixtures) return fxRun(() => fxGetAgentRun(runId));
    return this.req<AgentRun>(
      "GET",
      `/agent/run/${encodeURIComponent(runId)}`,
    );
  }

  /**
   * POST /capability/run -- run ONE capability and return its result.
   * SYNCHRONOUS: the backend builds + (optionally) persists, then returns the
   * full CapabilityResultView in this single call. ``capability`` goes in the
   * BODY (not the path).
   */
  async runCapability(
    capability: string,
    intent: string,
    options?: Record<string, unknown>,
    inputs?: Record<string, unknown>,
  ): Promise<CapabilityResultView> {
    if (config.fixtures) {
      try {
        return await fxRunCapability(capability, intent, inputs);
      } catch (err) {
        const e = err as { message?: string; status?: number; reason?: string };
        throw new ApiClientError(
          e.status ?? 400,
          e.message ?? "Run could not be started.",
          e.reason,
        );
      }
    }
    // ``inputs`` (mission BRANDBOOK, Cell A) is the typed form payload per the capability's
    // input_contract (file/url/text + scalars); omitted when the card has no contract so the
    // body stays byte-identical to a free-text intent run.
    return this.req<CapabilityResultView>("POST", "/capability/run", {
      capability,
      intent,
      ...(inputs ? { inputs } : {}),
      ...(options ? { options } : {}),
    });
  }

  /**
   * PATCH /capability/{record_id}/media/{slot_key} -- persist a human upload into a dual-output
   * media slot (the upload-persist wire). MULTIPART (a ``file`` part): unlike every other call we
   * do NOT set content-type -- the browser sets the multipart boundary itself. The slot flips
   * empty -> generated; the regenerated dual_output + the filled slot come back. tenant_id stays
   * server-derived from the Bearer (never sent). In fixtures mode it resolves the same shape
   * offline (fxUploadSlotMedia), so the component is mode-transparent.
   */
  async uploadSlotMedia(
    recordId: string,
    slotKey: string,
    file: File,
  ): Promise<UploadedMedia> {
    if (config.fixtures) return fxUploadSlotMedia(recordId, slotKey, file);
    if (!config.apiUrl) {
      throw new ApiClientError(
        0,
        "NEXT_PUBLIC_API_URL is not set. Set it, or run with NEXT_PUBLIC_FIXTURES=1.",
      );
    }
    const form = new FormData();
    form.append("file", file);
    const path = `/capability/${encodeURIComponent(recordId)}/media/${encodeURIComponent(
      slotKey,
    )}`;
    let res: Response;
    try {
      res = await fetch(`${config.apiUrl}${path}`, {
        method: "PATCH",
        // The ONLY identity we send. NO content-type -- the browser sets the multipart boundary.
        headers: { authorization: `Bearer ${this.token}` },
        body: form,
        cache: "no-store",
      });
    } catch (err) {
      throw new ApiClientError(
        0,
        `Cannot reach the backend at ${config.apiUrl}. Is it running?`,
      );
    }
    if (!res.ok) {
      let reason: string | undefined;
      let message = `Upload failed (${res.status}).`;
      try {
        const data = (await res.json()) as Record<string, unknown>;
        const envelope = data.error;
        if (envelope && typeof envelope === "object") {
          const e = envelope as Record<string, unknown>;
          if (typeof e.reason === "string") reason = e.reason;
          if (typeof e.detail === "string" && e.detail) message = e.detail;
          else if (typeof e.reason === "string") message = e.reason;
        }
      } catch {
        // non-JSON error body; keep the default message
      }
      if (res.status === 401) message = "Your session expired. Sign in again.";
      throw new ApiClientError(res.status, message, reason);
    }
    return (await res.json()) as UploadedMedia;
  }

  /**
   * GET /results[?capability=][&render_format=md|html] -> the tenant's recent artifacts.
   *
   * Default (no ``renderFormat``): the light row summary {id, capability, kind, created_at}
   * -- the history LEDGER. When ``renderFormat`` is "md" | "html", the backend ADDITIONALLY
   * attaches each row's ``render`` = its canonical projection (research_universe -> render_-
   * universe, product -> marketplace render, plain -> canonical MD) -- this is what the
   * results deep-link renders INLINE. The backend has NO single-artifact-by-id GET, so the
   * deep-link re-fetches THIS endpoint with render_format and matches the row by ``id``
   * (degrade-to-ledger-data; never an invented route). tenant_id stays server-derived from
   * the JWT, unchanged by render_format.
   */
  async listResults(
    capability?: string,
    renderFormat?: "md" | "html",
    limit?: number,
  ): Promise<ResultRow[]> {
    if (config.fixtures) return fxListResults(capability, renderFormat);
    const params = new URLSearchParams();
    if (capability) params.set("capability", capability);
    if (renderFormat) params.set("render_format", renderFormat);
    // Explicit fetch bound (HARDEN mission). The backend already caps server-side
    // (default 50 / max 200); passing ``limit`` makes the ceiling caller-controlled
    // instead of implicit. OMITTED by default -> the request is byte-identical to
    // before (server default applies) -> zero-regression. A positive integer is
    // clamped by the backend to its [1, 200] range.
    if (typeof limit === "number" && Number.isFinite(limit) && limit > 0) {
      params.set("limit", String(Math.floor(limit)));
    }
    const qs = params.toString() ? `?${params.toString()}` : "";
    const body = await this.req<ResultsResponse>("GET", `/results${qs}`);
    return body.results ?? [];
  }

  // --- home / settings shells ------------------------------------------------

  /**
   * GET /summary -> the tenant's home/analytics payload (stats + recent runs +
   * health). Derived from the tenant's own data; tenant_id is server-derived.
   */
  async getSummary(): Promise<SummaryResponse> {
    if (config.fixtures) return fxGetSummary();
    return this.req<SummaryResponse>("GET", "/summary");
  }

  /**
   * GET /settings -> the tenant context, integration status, and the
   * STATUS-ONLY secret surface. The response NEVER carries a secret value (see
   * SecretStatus in lib/types) -- the backend reports only whether each named
   * secret is configured.
   */
  async getSettings(): Promise<TenantSettings> {
    if (config.fixtures) return fxGetSettings();
    return this.req<TenantSettings>("GET", "/settings");
  }

  // --- waitlist queue (GO_ONLINE A2, spec 23 FR-003) --------------------------
  //
  // PROPOSAL for Onda B/a follow-up lane (fence extension required, not yet
  // approved): a new apps/dashboard_api/waitlist_reader.py, structurally
  // mirroring public_reader.py's SET LOCAL ROLE shape (service_role instead of
  // anon, no slug filter, ORDER BY wtp_band), wired through deps.py's existing
  // _resolve_public_session_factory-style registration seam.

  /**
   * GET /waitlist -> the founder-side lead queue (waitlist_intake rows, one
   * per /intake "modo-espera" signup), sorted by wtp_band. NOT YET LIVE:
   * apps/dashboard_api/* is out of this lane's fence (GO_ONLINE A2 DECISIONS)
   * -- there is no /waitlist route on the backend today, so in LIVE mode this
   * ALWAYS rejects with an ApiClientError. The caller
   * (app/dashboard/waitlist/page.tsx) treats that as an honest "pending
   * backend integration" state, never a broken page. FIXTURES mode returns an
   * empty array -- no fixture rows are fabricated for a table with no live
   * reader yet. tenant_id would be server-derived from the JWT once the route
   * exists, same as every other call; the client never sends one.
   */
  async listWaitlist(): Promise<WaitlistRow[]> {
    if (config.fixtures) return [];
    const body = await this.req<WaitlistResponse>("GET", "/waitlist");
    return body.rows ?? [];
  }

  // --- managed-entity SCHEMAS (the management primitive's config) ------------
  //
  // OVERLAY-DRIVEN: GET /entities-config returns the tenant's managed-entity
  // schemas from its overlay (``managed_entities``), NOT a static map. The
  // management nav + routes are built from this list -- a tenant declares its
  // own entities (products, contacts, leads) WITHOUT a code change. MIRRORS
  // listCards() (GET /capabilities); tenant_id is server-derived from the JWT.

  /** GET /entities-config -> the tenant's overlay-declared entity schemas. */
  async listEntitySchemas(): Promise<EntitySchema[]> {
    if (config.fixtures) return fxListEntitySchemas();
    const body = await this.req<EntitiesConfigResponse>(
      "GET",
      "/entities-config",
    );
    return body.entities ?? [];
  }

  // --- generic entity CRUD (the management primitive) ------------------------
  //
  // ONE set of methods serves EVERY entity -- the slug selects the table. The
  // client never sends tenant_id; the backend derives it from the JWT and RLS
  // scopes the rows. Writes are auth'd (Bearer) by construction.

  /** GET /entity/{slug} -> the tenant's rows for one entity. */
  async listEntity(entity: string, limit?: number): Promise<EntityRecord[]> {
    if (config.fixtures) return fxRun(() => fxListEntity(entity));
    // Explicit fetch bound (HARDEN mission), same contract as listResults: the
    // backend caps at 200 server-side; ``limit`` makes that caller-controlled.
    // OMITTED by default -> byte-identical request -> zero-regression.
    const params = new URLSearchParams();
    if (typeof limit === "number" && Number.isFinite(limit) && limit > 0) {
      params.set("limit", String(Math.floor(limit)));
    }
    const qs = params.toString() ? `?${params.toString()}` : "";
    const body = await this.req<EntityListResponse>(
      "GET",
      `/entity/${encodeURIComponent(entity)}${qs}`,
    );
    return body.records ?? [];
  }

  /** POST /entity/{slug} -> create one row. */
  async createEntity(
    entity: string,
    values: Record<string, unknown>,
  ): Promise<EntityRecord> {
    if (config.fixtures) return fxRun(() => fxCreateEntity(entity, values));
    return this.req<EntityRecord>(
      "POST",
      `/entity/${encodeURIComponent(entity)}`,
      values,
    );
  }

  /** PATCH /entity/{slug}/{id} -> update one row. */
  async updateEntity(
    entity: string,
    id: string,
    values: Record<string, unknown>,
  ): Promise<EntityRecord> {
    if (config.fixtures) return fxRun(() => fxUpdateEntity(entity, id, values));
    return this.req<EntityRecord>(
      "PATCH",
      `/entity/${encodeURIComponent(entity)}/${encodeURIComponent(id)}`,
      values,
    );
  }

  /**
   * PATCH /entity/{slug}/{id}/publish { published } -> flip the row's PUBLISHED gate
   * (SPEC 10 W1 -- the L2 publish seam). Setting ``published=true`` makes the row eligible
   * for the L2 anon public site; ``false`` retracts it. Returns the updated record carrying
   * the gate state (``published`` + ``published_at``). MIRRORS updateEntity EXACTLY: the
   * Bearer JWT is the ONLY identity sent -- tenant_id is NEVER in the body (the backend
   * derives it from the verified claim and the audited adapter's deny-before-DB seam scopes
   * the write). In fixtures mode it resolves the same shape offline so the toggle is
   * mode-transparent.
   */
  async setEntityPublished(
    entity: string,
    id: string,
    published: boolean,
  ): Promise<EntityRecord> {
    if (config.fixtures)
      return fxRun(() => fxSetEntityPublished(entity, id, published));
    return this.req<EntityRecord>(
      "PATCH",
      `/entity/${encodeURIComponent(entity)}/${encodeURIComponent(id)}/publish`,
      { published },
    );
  }

  /** DELETE /entity/{slug}/{id} -> remove one row. */
  async deleteEntity(entity: string, id: string): Promise<void> {
    if (config.fixtures) return fxRun(() => fxDeleteEntity(entity, id));
    await this.req<void>(
      "DELETE",
      `/entity/${encodeURIComponent(entity)}/${encodeURIComponent(id)}`,
    );
  }
}

/**
 * Run a fixtures call and re-wrap any thrown {status, reason, message} into an
 * ApiClientError, so callers handle ONE error type in both modes.
 */
async function fxRun<T>(fn: () => Promise<T>): Promise<T> {
  try {
    return await fn();
  } catch (err) {
    const e = err as { message?: string; status?: number; reason?: string };
    throw new ApiClientError(
      e.status ?? 400,
      e.message ?? "Request failed.",
      e.reason,
    );
  }
}
