# Runtime: run the NATIVE claude CLI against ANY model

> Reference-only absorption of the free-claude-code (fcc) pattern.
> Scoped in `docs/archive/WHITEPAPER_CEX_DISTILL.md` B.4/B.5. No proxy code is copied --
> this is `~10 lines over infra that already exists`.

## What this is

CEXAI already routes "any model" three ways (config-driven): native CLI per
nucleus (`cli: claude|gemini|codex|ollama` in `.cex/config/nucleus_models.yaml`),
a cross-provider `fallback_chain`, and a **LiteLLM proxy on `:4000`**
(`boot/litellm_proxy.ps1`, OpenAI-compatible + an Anthropic `/v1/messages`
passthrough, 100+ providers).

The one fcc trick CEXAI had not wired is the **CLI-transport seam**: keep the
*native* `claude` TUI / agents / tools and only divert its HTTP transport to
CEXAI's own proxy via `ANTHROPIC_BASE_URL`. That is what this profile adds.

```
  native `claude` CLI (unchanged)
        |
        v   ANTHROPIC_BASE_URL=http://localhost:4000
  LiteLLM proxy  :4000   <-- routing / fallback / 8F-governed clients
        |
        v   model_list entry in .cex/config/litellm_config.yaml
  ANY backend: Anthropic | Ollama (free) | Groq | Cerebras | DeepSeek | ...
```

The provider is **always** a config parameter (YAML / env / Credential), never
an `if` in code.

## Quick start (Windows)

```powershell
# starts the proxy if needed, wires the seam, launches native claude
powershell -File boot/cex_anymodel.ps1

# OR: just wire env + print how-to (no launch); dot-source to keep it in YOUR shell
. boot/cex_anymodel.ps1 -NoLaunch
```

POSIX shell equivalent (the proxy is Windows-booted today; on Mac/Linux run
LiteLLM yourself, then):

```bash
export ANTHROPIC_BASE_URL=http://localhost:4000
export ANTHROPIC_AUTH_TOKEN=cex-no-auth   # sentinel: skips the native login gate
claude                                     # runs on whatever the proxy routes to
```

## Pick the model -- ONE edit to `.cex/config/litellm_config.yaml`

The native `claude` CLI sends an Anthropic model id (e.g. `claude-sonnet-4-...`).
The shipped `model_list` only declares the `cex-n0X` aliases, so add a catch-all
entry that maps whatever the CLI asks for onto the backend you want. LiteLLM
matches exact names first, then wildcards, so the `cex-n0X` entries are
untouched. (LiteLLM wildcard routing: https://docs.litellm.ai/docs/wildcard_routing)

### Recipe A -- FREE / local (no API key) -- the headline use case

```yaml
model_list:
  # ... keep the existing cex-n0X entries ...
  - model_name: "*"                      # catch every model id the CLI sends
    litellm_params:
      model: ollama/gemma2:9b            # serve it from a free local model
      api_base: http://localhost:11434
```

`ollama serve` must be running. Now `claude` (TUI + tools) runs entirely offline.

### Recipe B -- transparent Anthropic passthrough (real Claude, just proxied)

Use this to keep real Claude but route through CEXAI for logging / governance.

```yaml
  - model_name: "*"
    litellm_params:
      model: "anthropic/*"               # forward the asked model to Anthropic
      api_key: os.environ/ANTHROPIC_API_KEY
```

### Recipe C -- the provider menu (same menu fcc advertises)

Drop in any of these as the catch-all `litellm_params.model` (set the matching
`*_API_KEY` in `.env`). LiteLLM supplies the correct transport per provider.

| Provider          | `model:` value                         | Key env var          | Notes |
|-------------------|----------------------------------------|----------------------|-------|
| Ollama (local)    | `ollama/gemma2:9b`                      | (none)               | keyless, offline |
| LM Studio (local) | `openai/<model>` + `api_base :1234/v1` | (none)               | keyless, OpenAI-compat |
| llama.cpp (local) | `openai/<model>` + `api_base :8080/v1` | (none)               | keyless, OpenAI-compat |
| Anthropic         | `anthropic/claude-sonnet-4-5`          | `ANTHROPIC_API_KEY`  | passthrough |
| OpenAI            | `openai/gpt-4o`                        | `OPENAI_API_KEY`     | |
| Groq              | `groq/llama-3.3-70b-versatile`         | `GROQ_API_KEY`       | fast, cheap |
| Cerebras          | `cerebras/llama3.1-70b`                | `CEREBRAS_API_KEY`   | fast |
| DeepSeek          | `deepseek/deepseek-chat`               | `DEEPSEEK_API_KEY`   | |
| Gemini            | `gemini/gemini-2.5-flash`              | `GEMINI_API_KEY`     | |
| OpenRouter        | `openrouter/<author>/<model>`          | `OPENROUTER_API_KEY` | 200+ models |

Full LiteLLM provider list: https://docs.litellm.ai/docs/providers

## Auth model (fail-closed by default)

`boot/cex_anymodel.ps1` makes the **sentinel token double as the proxy
`master_key`** when it starts the proxy: it exports `LITELLM_MASTER_KEY=<token>`
before launching `litellm_proxy.ps1` (whose config reads
`master_key: os.environ/LITELLM_MASTER_KEY`). The native CLI then sends the same
token as `ANTHROPIC_AUTH_TOKEN`. They match -> the proxy authenticates -> inbound
auth stays **fail-CLOSED** (a stronger posture than fcc's blank-disables default).

- Custom secret: `-Token mysecret` (used as both the CLI token and the master key).
- Keyless / fail-open (fcc style): `-Token ""` runs the proxy with no master key.
- **Already running your own proxy** (`-NoProxy`): this helper cannot change its
  key -- set `-Token` to match that proxy's `LITELLM_MASTER_KEY`, or run it keyless.

## Codex (OpenAI Responses wire) -- symmetric variant

The Codex CLI reads `~/.codex/config.toml`. Point it at the same proxy
(LiteLLM exposes a Responses bridge):

```toml
[model_providers.cex]
base_url = "http://localhost:4000/v1"
wire_api = "responses"
```

Then run Codex with `-c model_provider=cex` and a sentinel
`FCC_CODEX_API_KEY` / `OPENAI_API_KEY` matching the proxy key.

## Smoke / verify

```bash
# the path the proxy boots from now exists (was the .cex/P09_config bug)
powershell -Command "Test-Path .cex/config/litellm_config.yaml"   # -> True

# ASCII gate on the new + edited scripts
python _tools/cex_sanitize.py --check --scope boot/cex_anymodel.ps1
python _tools/cex_sanitize.py --check --scope boot/litellm_proxy.ps1

# proxy health (after boot)
curl http://localhost:4000/health/liveliness
```

## Proven live (dogfooded 2026-06-28)

Booted the proxy from `.venv_litellm` against `ollama/gemma2:9b` and ran BOTH wires end-to-end:

```bash
# the Anthropic wire (what the native claude CLI uses under the hood)
curl -s http://localhost:4000/v1/messages -H "x-api-key: cex-no-auth" \
  -H "anthropic-version: 2023-06-01" -H "content-type: application/json" \
  -d '{"model":"cex-n07","max_tokens":64,"messages":[{"role":"user","content":"oi"}]}'
# -> HTTP 200, full Anthropic envelope (native req -> LiteLLM -> ollama -> translated back)

# the NATIVE claude CLI, redirected, answering on a LOCAL model
# (--model cex-n07 only exists in the proxy config, so success == it went through the seam)
ANTHROPIC_BASE_URL=http://localhost:4000 ANTHROPIC_AUTH_TOKEN=cex-no-auth ANTHROPIC_API_KEY= \
  claude --model cex-n07 -p "o que e o CEXAI?" --strict-mcp-config --mcp-config '{"mcpServers":{}}'
# -> exit 0, answered by gemma2:9b
```

**REQUIRED for the native CLI**: `.cex/config/litellm_config.yaml` carries `litellm_settings: drop_params: true`.
The claude CLI sends Anthropic-only params (e.g. `context_management`) that a local model (ollama) rejects with a 400;
`drop_params` strips them before forwarding. Without it the native-CLI seam fails on the first call. (Found by
dogfooding -- static analysis missed it; running it surfaced it.)

## Per-provider egress / SOCKS5 (E2)

LiteLLM makes every upstream call through `httpx`, which honors the standard
proxy environment variables **process-globally** -- so the simplest egress
control needs **no install and no code**:

```powershell
# Windows: route ALL provider traffic the proxy makes through one HTTP/HTTPS egress
$env:HTTP_PROXY  = "http://user:pass@egress.host:8080"
$env:HTTPS_PROXY = "http://user:pass@egress.host:8080"
$env:NO_PROXY    = "localhost,127.0.0.1"   # keep Ollama on :11434 direct
powershell -File boot/litellm_proxy.ps1
```

```bash
# POSIX equivalent
export HTTPS_PROXY=http://user:pass@egress.host:8080
export NO_PROXY=localhost,127.0.0.1
```

### SOCKS5 needs the httpx socks extra

`httpx` cannot speak SOCKS5 until the `socks` extra (the `socksio` package) is
installed into the **same** interpreter that runs the proxy -- the dedicated
`.venv_litellm` (currently `litellm 1.83.7`, Python 3.12). It is **not** present
by default:

```powershell
# one-time, into the venv that boot/litellm_proxy.ps1 launches
.venv_litellm\Scripts\python.exe -m pip install "httpx[socks]"

# then point httpx at a SOCKS5 endpoint (ALL_PROXY covers every scheme)
$env:ALL_PROXY = "socks5://127.0.0.1:1080"
powershell -File boot/litellm_proxy.ps1
```

> There is no dedicated requirements file feeding `.venv_litellm` (it is built
> ad-hoc: `py -3.12 -m venv .venv_litellm` then
> `pip install "litellm[proxy]" pyyaml`). Run the `pip install "httpx[socks]"`
> above against that venv when you need SOCKS5; it adds `socksio` only and does
> not disturb the proven-live seam.

### Per-provider (not global) egress -- config recipe

The env vars above are global: every model in `model_list` shares one egress.
For **different** egress per backend, scope it at the provider entry in
`.cex/config/litellm_config.yaml`. LiteLLM forwards a model entry's
`litellm_params` to the provider client, so an OpenAI-compatible / Anthropic
backend can carry its own proxy while a local Ollama entry stays direct:

```yaml
model_list:
  # local backend -- no proxy, talks straight to Ollama
  - model_name: cex-local
    litellm_params:
      model: ollama/gemma2:9b
      api_base: http://localhost:11434

  # remote backend -- egress through a dedicated SOCKS5 hop
  - model_name: cex-remote
    litellm_params:
      model: anthropic/claude-sonnet-4-5
      api_key: os.environ/ANTHROPIC_API_KEY
      proxy: socks5://127.0.0.1:1080      # provider-scoped; needs httpx[socks]
```

Honest caveat: provider-scoped proxying depends on the underlying SDK accepting
the kwarg, and it still requires `httpx[socks]` in `.venv_litellm` for SOCKS5.
The fully-isolated, always-works alternative is to run **one proxy instance per
egress profile** (each with its own `HTTPS_PROXY`/`ALL_PROXY` and port) and let
`nucleus_models.yaml` route nuclei to the matching port -- coarser, but it needs
no per-SDK support.

## What free-claude-code does that this does NOT (off the routing-decision path)

Scope check: "multi-model routing" is the **routing-decision path** -- which
model gets the request, fallback/cost/health/coverage, and the protocol
translation that makes the request *reach* the model. On that path CEXAI is at
parity or ahead (`cex_router.py` EMA/health/cost + 10 `fallback_chain`s; the
bundled LiteLLM covers the wire translation, proven live end-to-end). The two
items below are genuine free-claude-code (fcc) edges, but both sit **off** that
path -- they are output-robustness and token-saving tricks aimed at **weak local
models**, not routing decisions. Listed transparently, each with its honest
CEXAI nearest analog.

### E1 -- weak-local-model wire-salvage (fcc has it; CEXAI does not)

fcc tries to rescue malformed output from a weak local model *after* the model
has already been chosen:

- **broken-SSE mid-stream recovery** -- reconnect/resume when a flaky local
  server drops the event stream part-way.
- **truncated tool-JSON repair** -- patch a tool-call argument blob the model
  cut off mid-token.
- **heuristic plaintext -> tool-call extraction** -- when a weak model emits no
  structured `tool_use` block, scrape the prose for an intended call.

CEXAI nearest analog (honest -- it *avoids* the failure rather than *salvaging*
it): the **auto-mode safety classifier + structured-generator seam** keeps
tool/format-critical work inside typed generators instead of parsing a weak
model's raw free-text into tool calls, so the broken-tool-text failure mode is
designed out of the hot path. And the **LiteLLM forward-to-real-upstream
default** means CEXAI's shipped backend is a frontier model whose output is
already well-formed -- the weak-model salvage problem mostly does not arise.
What CEXAI does **not** have is fcc's transport-layer repair for when you point
the seam at a genuinely weak local model; in that exact configuration fcc is
more forgiving, and we do not pretend otherwise.

### E3 -- transport-layer mock short-circuit (fcc has it; CEXAI does not)

fcc can short-circuit `/v1/messages` at the transport layer with a canned/mock
response to save tokens during development.

CEXAI nearest analog (honest -- token-saving, but at the orchestration layer,
not a transport mock): **`cex_prompt_cache`** returns cached results on repeat
intents, and **`cex_preflight`** (local TF-IDF + Haiku rerank) trims context
~70% *before* the call -- both cut token burn, but neither is a wire-level
canned reply. The shipped transport behavior is the opposite: LiteLLM
**forwards to the real upstream** by default. CEXAI has **no** transport-layer
mock short-circuit on `/v1/messages`.

> E2 (per-provider/SOCKS5 egress) is the one on-path-adjacent fcc edge that is
> cheaply closeable -- the recipe above closes it with a single `pip install`.
> E1 and E3 are deliberately left as fcc-only: they pay off only when the
> backend is a weak local model, which is off the routing-decision question.

## Why reference-only (not a forked proxy)

CEXAI's differentiator -- 8F + quality-gate + governance -- is orthogonal to and
absent from the fcc proxy. Copying a 37k-star FastAPI proxy would be redundant:
the heavy machinery (LiteLLM + `nucleus_models.yaml` + fallback + capability
filter) already exists. Absorbing only the **pattern** (one launcher + two env
vars + a config menu) closes the seam over infra CEXAI already runs.
