"use client";

// ----------------------------------------------------------------------------
// /intake -- the R-149 form_v1 intake form as a web page (R-283). Renders ALL
// v1 fields of the template N02_marketing/P01_knowledge/p01_dq_tenant_intake_form.md
// grouped by its 3 personas (A Fundador(a), B Comercial, C Operacao), with the
// PT-BR labels + the EN contract keys and the template's `*` required markers.
//
// Validation is the client-side MIRROR of the Python gate (lib/intake
// .validateIntake <-> _tools/brand_validate.py): blocking errors = the
// validator's errors + the resolver's drop rules; warnings render inline and
// NEVER block (exactly like the CLI). Template guidance (tagline 10-100,
// icp 20+) renders as static hints only -- the CLI does not enforce it, so
// neither do we (parity-honest).
//
// SUBMIT PATHS (honest to this app's deploy model -- next.config.mjs declares
// the prod posture "PURE CLIENT ... no server-side secrets"):
//   (a) ALWAYS-ON download: "Baixar answers YAML" builds the answers file
//       CLIENT-SIDE ('#' header + JSON body -- JSON is a YAML subset, so the
//       Python resolver parses it as-is) and Blob-downloads it. Next step
//       commands (resolve + bootstrap) are displayed. This is the ONLY path
//       in prod. No backend is fabricated: nothing is persisted server-side.
//   (b) DEV-ONLY resolve: POST /api/intake (same hard gate family as
//       /api/onboard: NODE_ENV=development AND CEXAI_ONBOARD_ENABLED=1 -- 403
//       in any prod build BEFORE any I/O). The route writes the answers file
//       under .cex/runtime/intake/ and runs the CLI resolver; the result is
//       rendered HONESTLY (ok/fail + resolver warnings + emitted paths). The
//       bootstrap command is DISPLAYED, never auto-run.
//
// The URL-first path stays at /onboard (additive route -- zero regression).
// Credentials collect an env-var REF NAME only (R-276): literal secrets are
// rejected client-side and would be DROPPED loudly by the resolver anyway.
// GO_ONLINE A3 (2026-07-11): venda-BR copy is PT-BR ACCENTED (founder
// standard, spec 23_go_online Acceptance Scenario 3) -- the old "ASCII-only +
// diacritic-free" house style below no longer holds for this file's visible
// strings. Code identifiers (IntakeKey contract keys, enKey breadcrumbs)
// stay untouched; see N02_marketing/P01_knowledge/p01_dv_vocabulario_venda_pme.md.
// ----------------------------------------------------------------------------

import { useEffect, useMemo, useState } from "react";
import IntakeField from "@/components/intake/IntakeField";
import IntakeSelect from "@/components/intake/IntakeSelect";
import IntakeColorField from "@/components/intake/IntakeColorField";
import {
  ARCHETYPES,
  B2B_MODES,
  DESIGN_STYLES,
  INTAKE_DRAFT_STORAGE_KEY,
  LINK_KEYS,
  LOGO_STATUSES,
  PRICING_MODELS,
  VERTICALS,
  buildAnswers,
  buildAnswersFile,
  bootstrapCommand,
  emptyIntakeState,
  parseDraft,
  serializeDraft,
  validateIntake,
  type IntakeApiResponse,
  type IntakeKey,
  type IntakeState,
} from "@/lib/intake";
import {
  buildWaitlistRow,
  isValidWaitlistEmail,
  submitToWaitlist,
  type WaitlistSubmitResult,
} from "@/lib/waitlist";

/** Stable DOM id for a form_v1 dotted key ("identity.brand_name" ->
 *  "intake-identity-brand_name"). Tests target these ids. */
function fieldId(key: IntakeKey): string {
  return "intake-" + key.replace(/\./g, "-");
}

const FORMALITY_OPTIONS = [
  { value: "1", label: "1 -- muito informal" },
  { value: "2", label: "2 -- informal" },
  { value: "3", label: "3 -- neutro" },
  { value: "4", label: "4 -- formal" },
  { value: "5", label: "5 -- muito formal" },
] as const;

const SIM_NAO_OPTIONS = [
  { value: "sim", label: "sim" },
  { value: "nao", label: "nao" },
] as const;

export default function IntakePage() {
  const [state, setState] = useState<IntakeState>(() => emptyIntakeState());
  const [touched, setTouched] = useState<Partial<Record<IntakeKey, boolean>>>({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<IntakeApiResponse | null>(null);
  const [transportError, setTransportError] = useState<string | null>(null);
  const [downloaded, setDownloaded] = useState(false);
  // DP5 (v2, 2026-07-07): welcome acolhedor parametrizado + rascunho localStorage.
  const [visitorName, setVisitorName] = useState("");
  const [draftRestored, setDraftRestored] = useState(false);
  // GO_ONLINE A2 (2026-07-11): "Entrar na fila de espera" -- the modo-espera
  // waitlist join action. Independent submit lifecycle from onResolve/onDownload.
  const [waitlistSubmitting, setWaitlistSubmitting] = useState(false);
  const [waitlistResult, setWaitlistResult] = useState<WaitlistSubmitResult | null>(null);

  // Welcome acolhedor parametrizado (?nome= or ?marca= in the URL) -- browser-
  // only, best-effort, never load-bearing. Plain window.location.search (not
  // next/navigation's useSearchParams) so this page needs no Suspense boundary.
  useEffect(() => {
    try {
      const params = new URLSearchParams(window.location.search);
      const nome = (params.get("nome") || params.get("marca") || "").trim();
      if (nome) setVisitorName(nome);
    } catch {
      // best-effort personalization only -- never blocks the form.
    }
  }, []);

  // Rascunho (DP5): restore ONCE on mount, after the empty initial render (so
  // there is no hydration mismatch -- the first paint matches the server's).
  useEffect(() => {
    try {
      const restored = parseDraft(window.localStorage.getItem(INTAKE_DRAFT_STORAGE_KEY));
      if (restored) {
        setState(restored);
        setDraftRestored(true);
      }
    } catch {
      // localStorage unavailable (privacy mode, etc.) -- degrade silently.
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Rascunho (DP5): auto-save on every change. Cheap (one form, one key) --
  // no debounce needed.
  useEffect(() => {
    try {
      window.localStorage.setItem(INTAKE_DRAFT_STORAGE_KEY, serializeDraft(state));
    } catch {
      // storage full/disabled -- never crash the form over a draft-save failure.
    }
  }, [state]);

  function clearDraft() {
    try {
      window.localStorage.removeItem(INTAKE_DRAFT_STORAGE_KEY);
    } catch {
      /* ignore */
    }
    setDraftRestored(false);
  }

  const { errors, warnings } = useMemo(() => validateIntake(state), [state]);
  const errorCount = Object.keys(errors).length;
  const canEmit = errorCount === 0;
  // GO_ONLINE A2: the waitlist join gate is LIGHT (DECISIONS -- "not the full
  // form gate"), decoupled from canEmit/errors['contact.email'] on purpose.
  const waitlistEmailValid = isValidWaitlistEmail(state["contact.email"]);

  const set = (key: IntakeKey) => (value: string) => {
    setState((s) => ({ ...s, [key]: value }));
    setTouched((t) => (t[key] ? t : { ...t, [key]: true }));
  };
  // Inline error policy: a pristine empty field shows only its `*` marker; a
  // touched field (or any non-empty value) shows its blocking error inline.
  const err = (key: IntakeKey): string | undefined =>
    touched[key] || (state[key] ?? "").trim() !== "" ? errors[key] : undefined;
  const warn = (key: IntakeKey): string | undefined => warnings[key];

  const slug = state["tenant.slug"].trim();
  const answersFileName = (slug || "empresa") + "_form_answers.yaml";
  const resolveCmd =
    "python _tools/cex_ingest_registry.py --resolve " +
    answersFileName +
    " \\\n    --out brand_init.yaml --provenance provenance.json --emit-shape shape.json";
  const consumeCmd = bootstrapCommand(slug || null, "brand_init.yaml");

  function onDownload() {
    if (!canEmit) return;
    const text = buildAnswersFile(state);
    // DP5: clear-on-submit. The answers were built successfully (valid text,
    // gate passed) -- that IS the submission. This is decoupled from the
    // browser Blob-download MECHANISM below on purpose: a.click() on a
    // download-attributed anchor gives JS no success/failure signal in any
    // environment (browser or jsdom), so gating the draft-clear on it would
    // make "did we submit" depend on an unobservable OS-level detail.
    clearDraft();
    try {
      const blob = new Blob([text], { type: "application/yaml;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = answersFileName;
      a.click();
      URL.revokeObjectURL(url);
      setDownloaded(true);
    } catch {
      // jsdom / very old browsers: no Blob-download support. Nothing persisted,
      // nothing fabricated -- the CLI commands below remain the honest path.
      setDownloaded(false);
    }
  }

  function onDiscardDraft() {
    clearDraft();
    setState(emptyIntakeState());
    setTouched({});
  }

  async function onResolve(e: React.FormEvent) {
    e.preventDefault();
    if (!canEmit || submitting) return;
    setSubmitting(true);
    setResult(null);
    setTransportError(null);
    try {
      const res = await fetch("/api/intake", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ answers: buildAnswers(state) }),
      });
      // The route ALWAYS returns a JSON body (ok branch and every error branch).
      const data = (await res.json()) as IntakeApiResponse;
      setResult(data);
      if (data.ok) clearDraft(); // DP5: a successful resolve is a "submission" too.
    } catch (err2) {
      setTransportError(
        "Falha de rede ao chamar /api/intake: " +
          (err2 instanceof Error ? err2.message : String(err2)),
      );
    } finally {
      setSubmitting(false);
    }
  }

  // GO_ONLINE A2: join the waitlist ("modo-espera"). Mirrors onResolve's
  // try/catch/finally shape; submitToWaitlist itself is TOTAL (never throws --
  // see lib/waitlist.ts) so the catch below is a defensive backstop, not the
  // primary error path.
  async function onJoinWaitlist() {
    if (!waitlistEmailValid || waitlistSubmitting) return;
    setWaitlistSubmitting(true);
    setWaitlistResult(null);
    try {
      const row = buildWaitlistRow(state);
      const res = await submitToWaitlist(row);
      setWaitlistResult(res);
    } catch (err3) {
      setWaitlistResult({
        ok: false,
        error: err3 instanceof Error ? err3.message : String(err3),
      });
    } finally {
      setWaitlistSubmitting(false);
    }
  }

  const ok = result?.ok === true;
  const resultErrors = result?.errors ?? [];
  const resolverWarnings = result?.resolver_warnings ?? [];

  return (
    <main id="main-content" className="min-h-screen px-5 py-12">
      <div className="mx-auto w-full max-w-3xl space-y-8">
        <header className="space-y-2">
          <p className="eyebrow">CEXAI . intake (form_v1 + v2)</p>
          <h1 className="font-display text-h1 text-foreground">
            {visitorName ? `Bem-vindo(a), ${visitorName}!` : "Seja bem-vindo(a)!"}
          </h1>
          <p className="text-base leading-relaxed text-muted-foreground">
            Briefing do seu negócio -- uma entrevista vira um brand_init.yaml
            que o bootstrap consome. Quanto mais detalhe você der aqui, menos revisão
            vem depois: cada resposta alimenta uma parte real do seu site, admin e
            marca. Campos com <span className="text-destructive">*</span> são o gate
            brand_validate (14 obrigatórios); os demais 17 (v2) são opcionais e
            NUNCA bloqueiam -- avisos só orientam.
          </p>
          <p className="text-sm text-muted-foreground">
            Prefere o caminho rapido por URL (2 campos)?{" "}
            <a href="/onboard" className="font-medium text-foreground underline">
              /onboard
            </a>
          </p>
          <p className="text-sm text-muted-foreground">
            Rascunho salvo automaticamente neste navegador enquanto voce digita.
            {draftRestored && (
              <>
                {" "}Rascunho restaurado -- continue de onde parou.{" "}
                <button
                  type="button"
                  onClick={onDiscardDraft}
                  className="font-medium text-foreground underline"
                >
                  Descartar e comecar do zero
                </button>
              </>
            )}
          </p>
        </header>

        <form onSubmit={onResolve} className="space-y-8">
          {/* ---- Persona A -- Fundador(a) [S1->S3] ---------------------------- */}
          <section className="space-y-5 rounded-card border border-border bg-card p-8 shadow-md">
            <div className="space-y-1">
              <h2 className="font-display text-h2 text-foreground">
                Fase 1 de 3 -- Quem e a sua marca{" "}
                <span className="font-mono text-2xs font-normal text-muted-foreground">
                  (Persona A -- Fundador(a))
                </span>
              </h2>
              <p className="text-sm text-muted-foreground">
                Identidade, voz, publico, visual e posicionamento -- o coracao da marca.
              </p>
            </div>

            <div className="grid gap-5 sm:grid-cols-2">
              <IntakeField
                id={fieldId("contact.name")}
                label="Seu nome"
                enKey="contact.name"
                value={state["contact.name"]}
                onChange={set("contact.name")}
                placeholder="Ana Souza"
                hint="Quem esta respondendo esse formulario? Opcional."
                error={err("contact.name")}
                warning={warn("contact.name")}
              />
              <IntakeField
                id={fieldId("contact.email")}
                label="Seu e-mail"
                enKey="contact.email"
                value={state["contact.email"]}
                onChange={set("contact.email")}
                placeholder="ana@suamarca.com.br"
                hint="Para retorno, se precisarmos esclarecer algo. Nunca vira credencial."
                error={err("contact.email")}
                warning={warn("contact.email")}
              />
            </div>

            <IntakeField
              id={fieldId("identity.brand_name")}
              label="Nome da marca?"
              enKey="identity.brand_name"
              required
              value={state["identity.brand_name"]}
              onChange={set("identity.brand_name")}
              placeholder="Cafe Borealis"
              error={err("identity.brand_name")}
            />
            <IntakeField
              id={fieldId("identity.legal_name")}
              label="Razao social (se diferente do nome fantasia)"
              enKey="identity.legal_name"
              value={state["identity.legal_name"]}
              onChange={set("identity.legal_name")}
              placeholder="Borealis Comercio de Cafes LTDA"
              hint="Ex.: Borealis Comercio de Cafes LTDA. Opcional, uso fiscal futuro."
              error={err("identity.legal_name")}
              warning={warn("identity.legal_name")}
            />
            <IntakeField
              id={fieldId("identity.brand_tagline")}
              label="Tagline?"
              enKey="identity.brand_tagline"
              required
              value={state["identity.brand_tagline"]}
              onChange={set("identity.brand_tagline")}
              hint="Guia do template: 10-100 caracteres (orientação, não bloqueia)."
              error={err("identity.brand_tagline")}
            />
            <IntakeField
              id={fieldId("identity.brand_mission")}
              label="Missao (por que)?"
              enKey="identity.brand_mission"
              required
              kind="textarea"
              value={state["identity.brand_mission"]}
              onChange={set("identity.brand_mission")}
              error={err("identity.brand_mission")}
            />
            <IntakeField
              id={fieldId("identity.brand_values")}
              label="3-5 valores"
              enKey="identity.brand_values"
              required
              kind="textarea"
              value={state["identity.brand_values"]}
              onChange={set("identity.brand_values")}
              hint="Um por linha (ou separados por virgula). Minimo 3 (gate); recomendado 3-7."
              error={err("identity.brand_values")}
              warning={warn("identity.brand_values")}
            />
            <IntakeField
              id={fieldId("identity.brand_story")}
              label="Historia da marca"
              enKey="identity.brand_story"
              kind="textarea"
              value={state["identity.brand_story"]}
              onChange={set("identity.brand_story")}
              hint="Opcional. Se citar o dominio da loja, o distill aproveita (store-domain lift)."
              error={err("identity.brand_story")}
            />
            <IntakeField
              id={fieldId("identity.vision")}
              label="Visao da empresa (onde quer chegar)"
              enKey="identity.vision"
              kind="textarea"
              value={state["identity.vision"]}
              onChange={set("identity.vision")}
              placeholder="Ser a assinatura de cafe especial mais confiavel do Brasil ate 2030"
              hint="Ex.: Ser a assinatura de cafe especial mais confiavel do Brasil ate 2030."
              error={err("identity.vision")}
              warning={warn("identity.vision")}
            />
            <IntakeSelect
              id={fieldId("archetype.brand_archetype")}
              label="Arquetipo (12)"
              enKey="archetype.brand_archetype"
              required
              value={state["archetype.brand_archetype"]}
              onChange={set("archetype.brand_archetype")}
              options={ARCHETYPES}
              hint="Sempre uma escolha humana -- nunca auto-extraido de um site."
              error={err("archetype.brand_archetype")}
            />
            <IntakeField
              id={fieldId("archetype.brand_personality")}
              label="Personalidade (3-5)"
              enKey="archetype.brand_personality"
              kind="textarea"
              value={state["archetype.brand_personality"]}
              onChange={set("archetype.brand_personality")}
              hint="Um por linha (ou separados por virgula). Ex.: proximo, curioso, transparente."
              error={err("archetype.brand_personality")}
            />
            <IntakeField
              id={fieldId("voice.tone")}
              label="Tom de voz"
              enKey="voice.tone"
              required
              value={state["voice.tone"]}
              onChange={set("voice.tone")}
              placeholder="proximo, direto, sem jargao"
              error={err("voice.tone")}
            />
            <div className="grid gap-5 sm:grid-cols-2">
              <IntakeSelect
                id={fieldId("voice.formality")}
                label="Formalidade 1-5"
                enKey="voice.formality"
                required
                value={state["voice.formality"]}
                onChange={set("voice.formality")}
                options={FORMALITY_OPTIONS}
                error={err("voice.formality")}
              />
              <IntakeField
                id={fieldId("voice.language")}
                label="Idioma xx-XX"
                enKey="voice.language"
                value={state["voice.language"]}
                onChange={set("voice.language")}
                placeholder="pt-BR"
                error={err("voice.language")}
                warning={warn("voice.language")}
              />
            </div>
            <div className="grid gap-5 sm:grid-cols-2">
              <IntakeField
                id={fieldId("voice.do")}
                label="Sempre fazer (3)"
                enKey="voice.do"
                kind="textarea"
                value={state["voice.do"]}
                onChange={set("voice.do")}
                hint="Um por linha."
                error={err("voice.do")}
              />
              <IntakeField
                id={fieldId("voice.dont")}
                label="Nunca fazer (3)"
                enKey="voice.dont"
                kind="textarea"
                value={state["voice.dont"]}
                onChange={set("voice.dont")}
                hint="Um por linha."
                error={err("voice.dont")}
              />
            </div>
            <IntakeField
              id={fieldId("audience.icp")}
              label="Cliente ideal"
              enKey="audience.icp"
              required
              kind="textarea"
              value={state["audience.icp"]}
              onChange={set("audience.icp")}
              placeholder="Quem prepara cafe coado ou espresso em casa e quer regularidade sem virar especialista"
              hint="Guia do template: 20+ caracteres (orientação, não bloqueia)."
              error={err("audience.icp")}
            />
            <IntakeField
              id={fieldId("audience.transformation")}
              label="Transformacao (From X to Y through Z)"
              enKey="audience.transformation"
              required
              value={state["audience.transformation"]}
              onChange={set("audience.transformation")}
              placeholder="From cafe sem data de torra to xicara fresca through assinatura direta"
              error={err("audience.transformation")}
              warning={warn("audience.transformation")}
            />
            <IntakeField
              id={fieldId("audience.wtp_band")}
              label="Que faixa de preco seu publico espera pagar?"
              enKey="audience.wtp_band"
              value={state["audience.wtp_band"]}
              onChange={set("audience.wtp_band")}
              placeholder="R$ 29-149"
              hint="Formato R$ MIN-MAX. Ex.: R$ 29-149 -- alimenta o pricing fastpath direto, sem custo de IA."
              error={err("audience.wtp_band")}
              warning={warn("audience.wtp_band")}
            />
            <IntakeField
              id={fieldId("audience.demographics")}
              label="Publico: idade, genero, estilo de vida, interesses"
              enKey="audience.demographics"
              kind="textarea"
              value={state["audience.demographics"]}
              onChange={set("audience.demographics")}
              hint="Ex.: 25-40 anos, urbano, interessado em sustentabilidade e cafe de qualidade."
              error={err("audience.demographics")}
            />
            <div className="space-y-1.5">
              <p className="text-sm font-medium text-foreground">
                3 cores HEX<span aria-hidden="true" className="text-destructive"> *</span>{" "}
                <span className="font-mono text-2xs font-normal text-muted-foreground">
                  visual.colors
                </span>
              </p>
              <div className="grid gap-5 sm:grid-cols-3">
                <IntakeColorField
                  id={fieldId("visual.colors.primary")}
                  label="Primaria"
                  enKey="primary"
                  required
                  value={state["visual.colors.primary"]}
                  onChange={set("visual.colors.primary")}
                  error={err("visual.colors.primary")}
                />
                <IntakeColorField
                  id={fieldId("visual.colors.secondary")}
                  label="Secundaria"
                  enKey="secondary"
                  required
                  value={state["visual.colors.secondary"]}
                  onChange={set("visual.colors.secondary")}
                  error={err("visual.colors.secondary")}
                />
                <IntakeColorField
                  id={fieldId("visual.colors.accent")}
                  label="Acento"
                  enKey="accent"
                  required
                  value={state["visual.colors.accent"]}
                  onChange={set("visual.colors.accent")}
                  error={err("visual.colors.accent")}
                />
              </div>
            </div>
            <IntakeField
              id={fieldId("visual.colors_description")}
              label="Ou descreva as cores (se não souber o HEX exato)"
              enKey="visual.colors_description"
              kind="textarea"
              value={state["visual.colors_description"]}
              onChange={set("visual.colors_description")}
              hint="Ex.: verde musgo, marrom terroso e um toque dourado -- nós ajudamos a derivar o HEX. Preencha isso OU as 3 cores acima (não precisa dos dois)."
              error={err("visual.colors_description")}
              warning={warn("visual.colors_description")}
            />
            <div className="grid gap-5 sm:grid-cols-2">
              <IntakeField
                id={fieldId("visual.colors_avoid")}
                label="Cores que voce NAO quer"
                enKey="visual.colors_avoid"
                kind="textarea"
                value={state["visual.colors_avoid"]}
                onChange={set("visual.colors_avoid")}
                hint="Um por linha. Ex.: rosa choque, neon."
                error={err("visual.colors_avoid")}
              />
              <IntakeField
                id={fieldId("visual.style_avoid")}
                label="Estilos que voce NAO quer"
                enKey="visual.style_avoid"
                kind="textarea"
                value={state["visual.style_avoid"]}
                onChange={set("visual.style_avoid")}
                hint="Um por linha. Ex.: infantil, corporativo frio."
                error={err("visual.style_avoid")}
              />
            </div>
            <div className="grid gap-5 sm:grid-cols-2">
              <IntakeSelect
                id={fieldId("visual.design_style")}
                label="Estilo de design"
                enKey="visual.design_style"
                value={state["visual.design_style"]}
                onChange={set("visual.design_style")}
                options={DESIGN_STYLES}
                error={err("visual.design_style")}
                hint="Ex.: minimalista, vintage, moderno."
              />
              <IntakeSelect
                id={fieldId("visual.logo_status")}
                label="Você já tem logotipo?"
                enKey="visual.logo_status"
                value={state["visual.logo_status"]}
                onChange={set("visual.logo_status")}
                options={LOGO_STATUSES}
                error={err("visual.logo_status")}
              />
            </div>
            <IntakeField
              id={fieldId("visual.logo")}
              label="Logo (URL)"
              enKey="visual.logo"
              kind="url"
              value={state["visual.logo"]}
              onChange={set("visual.logo")}
              placeholder="https://exemplo.com.br/logo.svg"
              error={err("visual.logo")}
            />
            <IntakeField
              id={fieldId("visual.references")}
              label="Identidades visuais que voce admira (links ou nomes)"
              enKey="visual.references"
              kind="textarea"
              value={state["visual.references"]}
              onChange={set("visual.references")}
              hint="Um por linha. Ex.: https://instagram.com/outramarca ou 'a paleta da marca X'."
              error={err("visual.references")}
            />
            <div className="grid gap-5 sm:grid-cols-2">
              <IntakeField
                id={fieldId("visual.fonts.heading")}
                label="Fonte de titulos"
                enKey="visual.fonts.heading"
                value={state["visual.fonts.heading"]}
                onChange={set("visual.fonts.heading")}
                placeholder="Fraunces"
                error={err("visual.fonts.heading")}
              />
              <IntakeField
                id={fieldId("visual.fonts.body")}
                label="Fonte de texto"
                enKey="visual.fonts.body"
                value={state["visual.fonts.body"]}
                onChange={set("visual.fonts.body")}
                placeholder="Inter"
                error={err("visual.fonts.body")}
              />
            </div>
            <IntakeField
              id={fieldId("positioning.category")}
              label="Categoria / mercado"
              enKey="positioning.category"
              required
              value={state["positioning.category"]}
              onChange={set("positioning.category")}
              placeholder="cafe especial em assinatura (D2C)"
              error={err("positioning.category")}
            />
            <IntakeField
              id={fieldId("positioning.uvp")}
              label="UVP (proposta unica de valor)"
              enKey="positioning.uvp"
              required
              kind="textarea"
              value={state["positioning.uvp"]}
              onChange={set("positioning.uvp")}
              hint="Ex.: Assinatura de cafe especial com torra na semana do envio."
              error={err("positioning.uvp")}
              warning={warn("positioning.uvp")}
            />
            <IntakeField
              id={fieldId("positioning.offerings")}
              label="Produtos/servicos que voce oferece"
              enKey="positioning.offerings"
              kind="textarea"
              value={state["positioning.offerings"]}
              onChange={set("positioning.offerings")}
              hint="Ex.: assinatura mensal, venda avulsa em graos, cursos de metodo de preparo."
              error={err("positioning.offerings")}
            />
            <IntakeField
              id={fieldId("positioning.content_pillars")}
              label="Pilares de conteudo"
              enKey="positioning.content_pillars"
              kind="textarea"
              value={state["positioning.content_pillars"]}
              onChange={set("positioning.content_pillars")}
              hint="Um por linha (ou separados por virgula)."
              error={err("positioning.content_pillars")}
            />
          </section>

          {/* ---- Persona B -- Comercial [S2] ---------------------------------- */}
          <section className="space-y-5 rounded-card border border-border bg-card p-8 shadow-md">
            <div className="space-y-1">
              <h2 className="font-display text-h2 text-foreground">
                Fase 2 de 3 -- Negocio, mercado e canais{" "}
                <span className="font-mono text-2xs font-normal text-muted-foreground">
                  (Persona B -- Comercial)
                </span>
              </h2>
              <p className="text-sm text-muted-foreground">
                Modelo de negócio, shape, canais, links e o identificador da sua marca.
              </p>
            </div>

            <div className="grid gap-5 sm:grid-cols-2">
              <IntakeSelect
                id={fieldId("monetization.pricing_model")}
                label="Modelo de preco (6)"
                enKey="monetization.pricing_model"
                required
                value={state["monetization.pricing_model"]}
                onChange={set("monetization.pricing_model")}
                options={PRICING_MODELS}
                error={err("monetization.pricing_model")}
              />
              <IntakeField
                id={fieldId("monetization.currency")}
                label="Moeda"
                enKey="monetization.currency"
                required
                value={state["monetization.currency"]}
                onChange={set("monetization.currency")}
                placeholder="BRL"
                hint="Emitida em maiusculas (a mesma coercao do resolver)."
                error={err("monetization.currency")}
              />
            </div>
            <IntakeField
              id={fieldId("monetization.tiers")}
              label="Tiers"
              enKey="monetization.tiers"
              kind="textarea"
              value={state["monetization.tiers"]}
              onChange={set("monetization.tiers")}
              hint="Um por linha. Convencao: b2c-*, b2b-*, marketplace-*."
              error={err("monetization.tiers")}
            />
            <IntakeField
              id={fieldId("location.channels")}
              label="Canais de venda"
              enKey="location.channels"
              kind="textarea"
              value={state["location.channels"]}
              onChange={set("location.channels")}
              hint="Um por linha. Ex.: loja propria: https://loja.exemplo.com.br"
              error={err("location.channels")}
            />
            <IntakeField
              id={fieldId("location.city_state")}
              label="Cidade / Estado"
              enKey="location.city_state"
              value={state["location.city_state"]}
              onChange={set("location.city_state")}
              placeholder="Patrocinio - MG"
              hint="Ex.: Patrocinio - MG."
              error={err("location.city_state")}
            />

            <div className="space-y-1.5">
              <p className="text-sm font-medium text-foreground">
                Mercado{" "}
                <span className="font-mono text-2xs font-normal text-muted-foreground">
                  market.*
                </span>
              </p>
              <IntakeField
                id={fieldId("market.competitors")}
                label="Principais concorrentes (nomes ou links)"
                enKey="market.competitors"
                kind="textarea"
                value={state["market.competitors"]}
                onChange={set("market.competitors")}
                hint="Um por linha. Ex.: Cafe do Ponto, https://outramarca.com.br"
                error={err("market.competitors")}
              />
              <IntakeField
                id={fieldId("market.edge_notes")}
                label="O que voce admira ou quer superar nos concorrentes"
                enKey="market.edge_notes"
                kind="textarea"
                value={state["market.edge_notes"]}
                onChange={set("market.edge_notes")}
                hint="Ex.: eles não mostram a data de torra; queremos ser mais transparentes."
                error={err("market.edge_notes")}
              />
              <IntakeField
                id={fieldId("market.trends")}
                label="Tendencias do seu mercado que valem observar"
                enKey="market.trends"
                kind="textarea"
                value={state["market.trends"]}
                onChange={set("market.trends")}
                hint="Ex.: cafe descafeinado especial crescendo, assinaturas flexiveis."
                error={err("market.trends")}
              />
            </div>

            <IntakeField
              id={fieldId("applications.surfaces")}
              label="Onde a identidade sera mais usada"
              enKey="applications.surfaces"
              kind="textarea"
              value={state["applications.surfaces"]}
              onChange={set("applications.surfaces")}
              hint="Um por linha. Ex.: loja online, redes sociais, embalagem, papelaria, uniformes."
              error={err("applications.surfaces")}
            />

            <div className="space-y-1.5">
              <p className="text-sm font-medium text-foreground">
                Confirma o shape do negocio?{" "}
                <span className="font-mono text-2xs font-normal text-muted-foreground">
                  shape_confirm.*
                </span>
              </p>
              <p className="text-sm text-muted-foreground">
                Opcional -- uma resposta humana faz o shape virar committed=true.
                O que ficar em branco continua com o veredito do detector.
              </p>
              <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                <IntakeSelect
                  id={fieldId("shape_confirm.vertical")}
                  label="Vertical"
                  enKey="vertical"
                  value={state["shape_confirm.vertical"]}
                  onChange={set("shape_confirm.vertical")}
                  options={VERTICALS}
                  error={err("shape_confirm.vertical")}
                />
                <IntakeSelect
                  id={fieldId("shape_confirm.has_store")}
                  label="Tem loja?"
                  enKey="has_store"
                  value={state["shape_confirm.has_store"]}
                  onChange={set("shape_confirm.has_store")}
                  options={SIM_NAO_OPTIONS}
                  error={err("shape_confirm.has_store")}
                />
                <IntakeSelect
                  id={fieldId("shape_confirm.has_blog")}
                  label="Tem blog?"
                  enKey="has_blog"
                  value={state["shape_confirm.has_blog"]}
                  onChange={set("shape_confirm.has_blog")}
                  options={SIM_NAO_OPTIONS}
                  error={err("shape_confirm.has_blog")}
                />
                <IntakeSelect
                  id={fieldId("shape_confirm.has_b2b")}
                  label="Atende B2B?"
                  enKey="has_b2b"
                  value={state["shape_confirm.has_b2b"]}
                  onChange={set("shape_confirm.has_b2b")}
                  options={SIM_NAO_OPTIONS}
                  error={err("shape_confirm.has_b2b")}
                />
                <IntakeSelect
                  id={fieldId("shape_confirm.b2b_mode")}
                  label="Modo B2B"
                  enKey="b2b_mode"
                  value={state["shape_confirm.b2b_mode"]}
                  onChange={set("shape_confirm.b2b_mode")}
                  options={B2B_MODES}
                  error={err("shape_confirm.b2b_mode")}
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <p className="text-sm font-medium text-foreground">
                Links (https)
                {" "}
                <span className="font-mono text-2xs font-normal text-muted-foreground">
                  links.*
                </span>
              </p>
              <p className="text-sm text-muted-foreground">
                Apenas URLs https:// absolutas -- o sanitizador canonico descarta o resto.
              </p>
              <div className="grid gap-5 sm:grid-cols-2">
                {LINK_KEYS.map((key) => {
                  const stateKey = ("links." + key) as IntakeKey;
                  return (
                    <IntakeField
                      key={key}
                      id={fieldId(stateKey)}
                      label={key}
                      enKey={"links." + key}
                      kind="url"
                      value={state[stateKey]}
                      onChange={set(stateKey)}
                      placeholder={"https://" + (key === "website" ? "exemplo.com.br" : "...")}
                      error={err(stateKey)}
                    />
                  );
                })}
              </div>
            </div>

            <IntakeField
              id={fieldId("tenant.slug")}
              label="Identificador da sua marca"
              enKey="tenant.slug"
              value={state["tenant.slug"]}
              onChange={set("tenant.slug")}
              placeholder="borealis-cafe"
              hint="Padrão ^[a-z0-9][a-z0-9_-]{0,63}$ -- vira o identificador único da sua marca no sistema."
              error={err("tenant.slug")}
            />
          </section>

          {/* ---- Persona C -- Operacao [S1] ----------------------------------- */}
          <section className="space-y-5 rounded-card border border-border bg-card p-8 shadow-md">
            <div className="space-y-1">
              <h2 className="font-display text-h2 text-foreground">
                Fase 3 de 3 -- Fontes e integracoes{" "}
                <span className="font-mono text-2xs font-normal text-muted-foreground">
                  (Persona C -- Operacao)
                </span>
              </h2>
              <p className="text-sm text-muted-foreground">
                Fontes de ingestao (registradas para os extratores) e refs FASE-2.
              </p>
            </div>

            <IntakeField
              id={fieldId("sources.site_url")}
              label="URL do site"
              enKey="sources.site_url"
              kind="url"
              value={state["sources.site_url"]}
              onChange={set("sources.site_url")}
              placeholder="https://exemplo.com.br"
              hint="Alimenta o extrator url (pre-preenche a marca)."
              error={err("sources.site_url")}
            />
            <IntakeField
              id={fieldId("sources.snapshot")}
              label="Snapshot HTML/PDF (caminho/ref)"
              enKey="sources.snapshot"
              value={state["sources.snapshot"]}
              onChange={set("sources.snapshot")}
              hint="Referencia de arquivo local -- roteada aos extratores html_snapshot/pdf."
              error={err("sources.snapshot")}
            />
            <IntakeField
              id={fieldId("sources.brandbook")}
              label="Ja tem brandbook? (arquivo/URL)"
              enKey="sources.brandbook"
              value={state["sources.brandbook"]}
              onChange={set("sources.brandbook")}
              error={err("sources.brandbook")}
            />
            <IntakeField
              id={fieldId("catalog.source_ref")}
              label="Catalogo (ref) -- FASE-2"
              enKey="catalog.source_ref"
              value={state["catalog.source_ref"]}
              onChange={set("catalog.source_ref")}
              hint="Slot do importador R-165: a ref e REGISTRADA, nunca resolvida no v1."
              error={err("catalog.source_ref")}
            />

            <div className="space-y-1.5 rounded-md border border-destructive/40 bg-destructive/5 p-4">
              <p className="text-sm font-medium text-foreground">
                CRM (ref) -- FASE-2, somente referencia (R-276)
              </p>
              <p className="text-sm text-muted-foreground">
                Informe apenas o NOME de uma variavel de ambiente (ex.: BOREALIS_CRM_KEY)
                -- nunca um segredo literal. O valor real vive em .env (via
                boot/load_dotenv.ps1); o resolver DESCARTA qualquer coisa fora do padrao
                e este formulario nunca persiste segredos.
              </p>
              <IntakeField
                id={fieldId("credentials.crm_ref")}
                label="CRM env-var ref"
                enKey="credentials.crm_ref"
                value={state["credentials.crm_ref"]}
                onChange={set("credentials.crm_ref")}
                placeholder="BOREALIS_CRM_KEY"
                error={err("credentials.crm_ref")}
              />
            </div>
          </section>

          {/* ---- Actions ------------------------------------------------------ */}
          <section className="space-y-4 rounded-card border border-border bg-card p-8 shadow-md">
            {errorCount > 0 ? (
              <p className="text-sm text-muted-foreground">
                {errorCount} campo(s) obrigatorio(s) pendente(s) ou com valor invalido.
                Avisos (amarelos) não bloqueiam -- o gate da CLI também só avisa.
              </p>
            ) : (
              <p className="text-sm text-muted-foreground">
                Pronto: o gate client-side (espelho do brand_validate) passou.
              </p>
            )}
            <div className="flex flex-wrap items-center gap-3">
              <button
                type="button"
                onClick={onDownload}
                disabled={!canEmit}
                className="inline-flex items-center justify-center rounded-md bg-primary px-5 py-2.5 text-base font-medium text-primary-foreground shadow-sm transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Baixar answers YAML
              </button>
              <button
                type="submit"
                disabled={!canEmit || submitting}
                className="inline-flex items-center justify-center rounded-md border border-border bg-background px-5 py-2.5 text-base font-medium text-foreground shadow-sm transition hover:bg-secondary disabled:cursor-not-allowed disabled:opacity-50"
              >
                {submitting ? "Resolvendo..." : "Resolver agora (DEV)"}
              </button>
              <button
                type="button"
                onClick={onJoinWaitlist}
                disabled={!waitlistEmailValid || waitlistSubmitting}
                className="inline-flex items-center justify-center rounded-md border border-border bg-background px-5 py-2.5 text-base font-medium text-foreground shadow-sm transition hover:bg-secondary disabled:cursor-not-allowed disabled:opacity-50"
              >
                {waitlistSubmitting ? "Entrando na fila..." : "Entrar na fila de espera"}
              </button>
            </div>
            <p className="text-sm text-muted-foreground">
              &quot;Resolver agora&quot; e DEV-ONLY (mesmo gate do /onboard: NODE_ENV=development
              + CEXAI_ONBOARD_ENABLED=1; em prod a rota responde 403 antes de qualquer I/O).
              O download funciona SEMPRE -- este site e um cliente puro, nada e enviado
              a um servidor.
            </p>
            <p className="text-sm text-muted-foreground">
              &quot;Entrar na fila de espera&quot; grava apenas o seu e-mail (campo &quot;Seu
              e-mail&quot; acima) -- é o único campo obrigatório para essa ação; o restante do
              formulário viaja junto, do jeito que estiver preenchido, mesmo incompleto.
              {!waitlistEmailValid && (
                <> Preencha um e-mail válido em &quot;Seu e-mail&quot; para habilitar.</>
              )}
            </p>
            {waitlistResult && (
              <p
                aria-live="polite"
                className={
                  "text-sm " + (waitlistResult.ok ? "text-muted-foreground" : "text-destructive")
                }
              >
                {waitlistResult.ok
                  ? "Você está na fila -- entraremos em contato em breve."
                  : "Não foi possível entrar na fila: " +
                    (waitlistResult.error || "erro desconhecido") +
                    "."}
              </p>
            )}
            <div className="space-y-1">
              <p className="text-sm font-medium text-foreground">
                Proximo passo apos baixar ({answersFileName}):
              </p>
              <pre className="overflow-x-auto rounded-md border border-border bg-background p-3 font-mono text-xs text-foreground">
                {resolveCmd + "\n" + consumeCmd}
              </pre>
              {downloaded && (
                <p className="text-sm text-muted-foreground">
                  Arquivo gerado no navegador -- nada foi enviado a nenhum servidor.
                </p>
              )}
            </div>
          </section>
        </form>

        {transportError && (
          <div className="rounded-card border border-destructive/40 bg-destructive/5 p-5 text-sm text-destructive">
            {transportError}
          </div>
        )}

        {result && (
          <section
            aria-live="polite"
            className="space-y-4 rounded-card border border-border bg-card p-8 shadow-md"
          >
            {ok ? (
              <>
                <div className="flex items-center gap-2">
                  <span className="inline-block rounded-md bg-primary/10 px-2 py-0.5 text-xs font-semibold uppercase tracking-wide text-primary">
                    Resolvido
                  </span>
                </div>
                <h2 className="font-display text-h2 text-foreground">
                  {result.summary || "form_v1 resolvido"}
                </h2>
                <dl className="space-y-1 text-sm text-muted-foreground">
                  {result.answers_path && (
                    <div className="flex gap-2">
                      <dt className="font-medium text-foreground">answers:</dt>
                      <dd className="break-all font-mono text-xs">{result.answers_path}</dd>
                    </div>
                  )}
                  {result.brand_init_path && (
                    <div className="flex gap-2">
                      <dt className="font-medium text-foreground">brand_init:</dt>
                      <dd className="break-all font-mono text-xs">{result.brand_init_path}</dd>
                    </div>
                  )}
                  {result.provenance_path && (
                    <div className="flex gap-2">
                      <dt className="font-medium text-foreground">provenance:</dt>
                      <dd className="break-all font-mono text-xs">{result.provenance_path}</dd>
                    </div>
                  )}
                  {result.shape_path && (
                    <div className="flex gap-2">
                      <dt className="font-medium text-foreground">shape:</dt>
                      <dd className="break-all font-mono text-xs">{result.shape_path}</dd>
                    </div>
                  )}
                </dl>
                {resolverWarnings.length > 0 && (
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-foreground">
                      Avisos do resolver (não bloqueiam):
                    </p>
                    <ul className="list-disc space-y-1 pl-5 text-sm text-warning">
                      {resolverWarnings.map((msg, i) => (
                        <li key={i}>{msg}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {result.bootstrap_cmd && (
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-foreground">
                      Consumir (rodar manualmente -- o formulario NUNCA executa o bootstrap):
                    </p>
                    <pre className="overflow-x-auto rounded-md border border-border bg-background p-3 font-mono text-xs text-foreground">
                      {result.bootstrap_cmd}
                    </pre>
                  </div>
                )}
              </>
            ) : (
              <>
                <div className="flex items-center gap-2">
                  <span className="inline-block rounded-md bg-destructive/10 px-2 py-0.5 text-xs font-semibold uppercase tracking-wide text-destructive">
                    Nao resolvido
                  </span>
                </div>
                <h2 className="font-display text-h2 text-foreground">
                  O resolver reportou erros
                </h2>
                {resultErrors.length > 0 ? (
                  <ul className="list-disc space-y-1 pl-5 text-sm text-destructive">
                    {resultErrors.map((msg, i) => (
                      <li key={i}>{msg}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-muted-foreground">
                    Sem detalhes de erro retornados.
                  </p>
                )}
                <p className="text-sm text-muted-foreground">
                  Sem backend disponivel? Use &quot;Baixar answers YAML&quot; -- o arquivo
                  baixado alimenta o MESMO resolver via CLI (comandos acima).
                </p>
              </>
            )}
          </section>
        )}
      </div>
    </main>
  );
}
