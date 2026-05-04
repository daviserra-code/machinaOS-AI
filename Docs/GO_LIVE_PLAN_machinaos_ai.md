# Go-Live Plan — Machina OS Public Demo (backend half)

**Status:** Draft v2 · 4 May 2026
**Owner:** Davide (operator) + 1 dev pair-runner
**Target:** A visitor on the marketing site `machinaos.ai` clicks
**"Try the live demo"** and lands in a working Machina OS session
inside 10 s — shopfloor-copilot style.
**Prerequisite work already done:** Hetzner servers provisioned, demo
mode + HMAC auth + seed workspace + guided tour all shipped (Sprints
41–43), deployment architecture spec exists
([HETZNER_DEPLOYMENT_PROPOSAL.md](HETZNER_DEPLOYMENT_PROPOSAL.md)).

---

## Repository split — who owns what

`machinaos.ai` (the marketing domain) is **not** owned by this repo.
It lives in a separate VS Code project / GitHub repo:

> **Marketing repo:** [`daviserra-code/machinaOS-AI`](https://github.com/daviserra-code/machinaOS-AI)

That repo owns the apex domain, the landing page, the cookie banner,
the privacy / ToS pages, and the "Try live" CTA button. **All the
work in §3 → WS3 (marketing landing page) belongs to that repo, not
this one.**

This plan covers only the backend half — the demo *destination*:

| Concern                                                  | Repo                       |
|----------------------------------------------------------|----------------------------|
| Apex `machinaos.ai`, landing page, marketing copy        | `machinaOS-AI` (other)     |
| `Try live` button + redirect to demo entry URL           | `machinaOS-AI` (other)     |
| Privacy notice, ToS, cookie banner                       | `machinaOS-AI` (other)     |
| **Demo entry endpoint** (`POST /demo/start`)             | **this repo**              |
| **Live app** at e.g. `https://demo.machinaos.ai/app/`    | **this repo** (Hetzner)    |
| Token issuer + admin pages                               | **this repo** (Hetzner)    |
| Backups, rate limit, demo mode tool gating, sessions     | **this repo** (Hetzner)    |
| Docker / Caddy / Ollama infra                            | **this repo** (Hetzner)    |

The handshake between the two repos is intentionally narrow:

```
   machinaos.ai (marketing repo)         demo.machinaos.ai (this repo)
┌──────────────────────────────┐       ┌──────────────────────────────┐
│  Static landing page          │       │  Caddy + FastAPI on Hetzner   │
│  "Try live" button            │ ────► │  POST /demo/start             │
│  (single <a href> or fetch)   │       │  → sets cookie, redirects to  │
│                               │       │    /app/                      │
└──────────────────────────────┘       └──────────────────────────────┘
```

Two practical implementations, pick one (default = A):

- **(A) Cross-domain redirect.** `Try live` button on `machinaos.ai`
  links to `https://demo.machinaos.ai/demo/start`. The demo backend
  mints the session, sets the cookie on `demo.machinaos.ai`, then
  302-redirects to `https://demo.machinaos.ai/app/`. Simplest, no
  cross-origin cookie problems, no CORS preflight.
- **(B) Same-origin AJAX.** Marketing site fetches `POST
  https://api.machinaos.ai/demo/start` from JS. Requires CORS
  whitelisting `https://machinaos.ai` and a cookie domain trick. More
  fragile, no real benefit.

We pick **(A)**. The marketing repo only needs to know one URL:
`https://demo.machinaos.ai/demo/start`.

---

## 0. North-star user journey (what we're shipping)

```
   machinaos.ai                  demo.machinaos.ai/demo/start          demo.machinaos.ai/app/
┌──────────────────────┐    ┌──────────────────────────────────┐    ┌──────────────────────────┐
│  Marketing landing    │    │  Demo entry endpoint              │    │  Live Machina OS UI       │
│  (other repo)         │    │  · rate-limit, capacity check     │    │  · seed workspace loaded  │
│  · pitch              │ →  │  · spawns DemoSessionManager      │ →  │  · guided tour auto-runs  │
│  · 3 demo cards       │    │  · sets httpOnly cookie           │    │  · 30-min countdown badge │
│  · "Try live" → href  │    │  · 302 → /app/                    │    │  · "Reset" + "Extend"     │
└──────────────────────┘    └──────────────────────────────────┘    └──────────────────────────┘
```

Three personas, one demo URL:

| Visitor type     | Path                                          | Mode       | TTL  | Friction |
|------------------|-----------------------------------------------|------------|------|----------|
| Anonymous (cold) | "Try live" → `demo.machinaos.ai/demo/start`   | `DEMO`     | 30 m | 0 clicks |
| Invited reviewer | `demo.machinaos.ai/?token=<…>`                | `REVIEWER` | 24 h | 0 clicks |
| Press / investor | `demo.machinaos.ai/?token=<…>`                | `REVIEWER` | 7 d  | 0 clicks |
| Internal ops     | basic-auth `demo.machinaos.ai/admin`          | `INTERNAL` | n/a  | login    |

---

## 1. Scope & non-scope

### In scope (this repo)
- Demo backend reachable at `https://demo.machinaos.ai`.
- One-click `POST /demo/start` entry that mints an anonymous demo
  session server-side (no signup form, no LLM key, no GitHub PAT).
- Token-based reviewer flow already specified in §4 of
  [HETZNER_DEPLOYMENT_PROPOSAL.md](HETZNER_DEPLOYMENT_PROPOSAL.md).
- **Production + staging both on `fsn1-1` (CPX62)** as two separate
  docker-compose stacks behind two Caddy vhosts, sharing
  shopfloor-copilot's existing Ollama. **`nbg1-1` (CPX42) is reserved
  for ai-radar and is not part of this deployment.**
- Restic backup, fail2ban, UFW, single-origin CORS that whitelists
  exactly `https://machinaos.ai`.
- Operator runbook + 1 dry-run before going public.

### Out of scope (other repo or deferred)
- The `machinaos.ai` landing page, "Try live" button, privacy notice,
  cookie banner — owned by `daviserra-code/machinaOS-AI`.
- Any signup / email collection.
- GPU instance for low-latency LLM (start CPU; upgrade only if the
  demo feels sluggish).
- Multi-region failover beyond the existing fsn1-1 ↔ nbg1-1 pair.
- Stripe / billing — the demo is free.

---

## 1b. The two questions that need answering up front

These are the two unknowns the operator flagged. Both have to be
resolved on day 0; they shape several downstream tasks.

### Q1 — What LLM does the live demo use? Where does it run?

The desktop product lets the user pick from 7 providers (Ollama,
OpenAI, Gemini, Claude, OpenRouter, LM Studio, GitHub Copilot). On a
**public, anonymous, free demo** none of those choices map cleanly,
so we make one deliberate decision and freeze it.

**Provider choice:**

| Option                            | Cost / month       | Latency      | Privacy story | Recommended? |
|-----------------------------------|--------------------|--------------|---------------|--------------|
| **Ollama (self-hosted, CPU)**     | €0 (sunk hardware) | 8b ≈ 25 tok/s · 70b ≈ 3-8 tok/s | "nothing leaves the box" — strongest | **Yes (default)** |
| OpenAI / Claude / Gemini via key  | Pay-per-token, unbounded for an open demo | < 1 s | weakens the local-first pitch + bill risk | No (v1) |
| OpenRouter prepaid                | Capped, lowest devops effort | < 1 s | still external, still costs money | Backup only |
| Per-visitor BYO key field          | €0 to us           | depends      | confusing, abuse risk | No |

**Decision (provider):** Ollama, model
`llama3.1:8b-instruct-q4_K_M`, fixed across all sessions. The 70b
upgrade is a post-launch trigger (§9) once latency on 8b is verifiably
sub-2 s.

**Where Ollama actually runs — the multi-tenant problem (revised):**

The two Hetzner VMs already host other things, and **a third VM is not
in the budget**:

- `fsn1-1` (CPX62, 16 vCPU / 32 GB) hosts **shopfloor-copilot** and
  its **existing Ollama** instance. shopfloor-copilot is mostly used
  by the operator alone, with async background routines — low,
  bursty, internal traffic.
- `nbg1-1` (CPX42, 8 vCPU / 16 GB) hosts **ai-radar**, a
  public-facing product getting **~6,000 visits/day** (sustained
  ~0.07 req/s, peaks ~1 req/s). This is the more sensitive tenant.

Ollama 8b on CPU saturates 8-12 cores for 5-15 s per generation. We
must pick which existing tenant absorbs that cost. After weighing:

| Placement option | Ollama cost falls on... | ai-radar (public) | shopfloor-copilot (internal) | Pick? |
|---|---|---|---|---|
| **A — Reuse shopfloor-copilot's existing Ollama on `fsn1-1`; demo container on `fsn1-1` too** | shopfloor-copilot | **Untouched** — nbg1-1 stays sacred | Async routines occasionally wait 5-15 s for LLM. Operator sees this 5% of the time. | **Yes (default)** |
| B — New Ollama on `nbg1-1`; demo container on `fsn1-1`, calls Ollama via private network | ai-radar | TTFB spikes from ~50 ms to multiple seconds during every demo prompt; affects 6k visits/day | Untouched | **No — unacceptable for a production product at that traffic** |
| C — Dedicated 3rd VM (CPX41, ~€18/mo) | Nobody existing | Untouched | Untouched | Out of budget for v1; revisit post-launch (§9) |

**Decision (placement):** **Option A** — the demo reuses the Ollama
that shopfloor-copilot already runs on `fsn1-1`. One Ollama instance,
one model resident in RAM (~6-9 GB), serves both apps. ai-radar
on `nbg1-1` is **completely untouched** and stays in production-grade
isolation.

**The trade-off, stated honestly:** when a demo visitor is mid-prompt,
shopfloor-copilot's LLM-dependent routines may wait an extra 5-15 s.
Given shopfloor-copilot is internal and the operator is its main user,
this is the cheapest acceptable cost. Ollama serializes incoming
requests by default — no risk of OOM from concurrent generations — and
the 25-session concurrency cap (WS2.5) plus 5/min/IP rate limit on
`/demo/start` (WS2.1) bound the worst case.

**Staging without a third VM:** `staging-demo.machinaos.ai` runs as a
second docker-compose stack on `fsn1-1` behind a separate Caddy vhost.
It shares the same Ollama. nbg1-1 is reserved for ai-radar.

**What this means in practice:**
- The demo container runs on `fsn1-1` and is started with `MACHINA_LLM_PROVIDER=ollama`, `MACHINA_LLM_URL=http://host.docker.internal:11434` *(reusing shopfloor-copilot's existing instance)*, `MACHINA_LLM_MODEL=llama3.1:8b-instruct-q4_K_M`. No API key. No second Ollama installed anywhere.
- The Settings → LLM panel in the demo UI is **read-only** in `DemoMode.DEMO` (see `WS2.7` for the branded overlay).
- A per-session token budget caps runaway prompts (default `MACHINA_DEMO_MAX_TOKENS_PER_SESSION=50_000`). Task `WS2.8`.
- On the marketing landing page (other repo), one of the trust-strip bullets reads **"Runs on its own server, no third-party AI keys required"** — the truthful one-liner the LLM choice unlocks.
- ai-radar on `nbg1-1` is unaffected: nothing about its box changes.
- shopfloor-copilot is the willing co-tenant: documented in R2.

### Q2 — What "local machine" is the demo actually operating on?

The desktop product orchestrates the user's actual laptop. On a public
demo there is no laptop — every visitor shares one server. The
question becomes: *what filesystem, what processes, what shell does
each visitor see?*

**Decision:** every demo session gets a **disposable, per-session
sandbox workspace** rooted under `/data/sessions/<session_id>/`. That
directory is the only filesystem any tool can touch.

| Surface             | What the visitor sees                                         | How it's enforced                                  |
|---------------------|---------------------------------------------------------------|----------------------------------------------------|
| Filesystem          | A copy of the seed workspace (`acme-vulnerable` or similar) at `/data/sessions/<sid>/workspace/` | Existing `_validate_path` workspace boundary; `set_workspace_root()` called at session creation |
| Shell               | **Blocked entirely** in `DemoMode.DEMO` (`shell.run` not in `DEMO_SAFE_TOOLS`) | Existing tool gating |
| Processes           | `process.list` returns the **container's** processes, not the host's. `process.stop` blocked. | `BLOCKED_TOOLS` in `core/demo/mode.py` |
| Git                 | Read-only (`git.status`, `git.log`, `git.diff`) against the seed workspace, which has a pre-baked `.git` | `DEMO_SAFE_TOOLS` whitelist |
| Browser / VS Code   | `browser.open_url` opens the URL inside the **container's** xvfb window — the visitor never sees it. **Disabled** in demo mode. | Add `browser.*` and `vscode.*` to `BLOCKED_TOOLS` for `DEMO`; allowed in `REVIEWER` only for `browser.find_recent` if useful |
| MCP servers          | The four servers used in the Siemens storyboard (`fetch`, `memory`, `sequential-thinking`, `demo`) are **pre-registered** at container start. Adding new MCP servers blocked in `DEMO`. | New env var `MACHINA_MCP_AUTOSTART=fetch,memory,sequential-thinking,demo`; `mcp.servers.add` excluded from demo whitelist |
| GitHub PAT          | None. The Settings → GitHub panel is hidden in demo mode.    | Existing demo nav restrictions (`DEMO_NAV_VIEWS`) |
| Network egress      | The container has **no outbound internet** except: (a) Ollama on the host (already loopback), (b) MCP `fetch` which goes through Anthropic's npx server (it does the egress, not us). | docker-compose `internal: true` network + a single bridge to the host loopback; explicit allowlist in iptables for the MCP fetch server |

The lifecycle of one visitor:

```
visitor clicks "Try live"
  └─► POST /demo/start
        ├─ DemoSessionManager.create(mode=DEMO, ttl=30m) → sid
        ├─ os.makedirs(/data/sessions/<sid>/workspace) and copy seed tree
        ├─ MachinaCore-per-session: new instance with workspace_root pinned
        │  to that path; same Ollama, same MCP servers (shared, read-only)
        ├─ set cookie machina_demo=<sid>
        └─ 302 → /app/
... visitor uses the app ...
30 min later (or when they close the tab):
  └─► DemoSessionManager.expire_stale() (existing 60s ScheduledTask)
        ├─ shutil.rmtree(/data/sessions/<sid>) — full wipe
        ├─ in-memory MachinaCore released
        └─ telemetry row {session_ended, sid_hash, duration, tools_used}
```

Two implementation notes that are easy to get wrong:

1. **One MachinaCore instance per session, or one shared core?** For
   the v1 demo we share a single core and route requests through a
   per-session workspace context. Spinning up a fresh core per visitor
   is overkill (each one boots SQLite stores, MCP subprocesses, and
   eats RAM). A new task `WS2.9` adds a request-scoped
   `workspace_root` override so the existing core picks the right
   sandbox per request.
2. **Seed-workspace bloat over time.** Every new session copies the
   seed tree (~1 MB). At 25 concurrent sessions that's 25 MB — fine.
   The disk-watchdog at 80 % (R4) catches any stuck sessions that
   never clean up.

---

## 2. Workstreams

Five parallel tracks. Each has one accountable owner. Tracks are
independent enough to run concurrently in week 1.

| #   | Track                                   | Owner    | Deliverable                                                  |
|-----|-----------------------------------------|----------|--------------------------------------------------------------|
| WS1 | **Infra & deploy**                      | Davide   | `fsn1-1` running prod + staging stacks behind Caddy + TLS; `nbg1-1` untouched (ai-radar) |
| WS2 | **Anonymous-session entry + sandbox**   | Dev pair | `POST /demo/start`, cookie flow, per-session workspace, locked LLM |
| WS3 | **Marketing handshake (other repo)**    | Davide   | One URL contract + CORS allowlist; landing work happens in `machinaOS-AI` |
| WS4 | **Token issuer + admin UI**             | Dev pair | `machina-issuer` container + `/admin/issue` page             |
| WS5 | **Operations & legal (backend half)**   | Davide   | Runbook, on-call, status page, GDPR self-check for demo telemetry |

Critical path: **WS1 → WS2** is the blocking sequence.  WS3/WS4/WS5
can run in parallel after Day 2. The marketing landing page is on the
`machinaOS-AI` repo's own timeline and only blocks the public
announcement, not the demo backend going live.

---

## 3. Detailed task list per workstream

### WS1 — Infra & deploy

| ID    | Task                                                                                                                                  | Day  | Depends on |
|-------|---------------------------------------------------------------------------------------------------------------------------------------|------|------------|
| WS1.1 | Add DNS records in the `machinaOS-AI` repo's zone: A `demo` → `46.224.66.48`, A `staging-demo` → `46.224.66.48` (same box, different Caddy vhost), AAAA + CAA per §2 of proposal. (Apex `@` and `www` stay pointed at the marketing host.) | D1 | — |
| WS1.2 | SSH-harden both VMs (key-only, UFW 22/80/443, fail2ban)                                                                               | D1   | WS1.1      |
| WS1.2b | **No private network needed** — the demo and Ollama are co-located on `fsn1-1`, ai-radar on `nbg1-1` stays untouched. Verify the existing shopfloor-copilot Ollama on `fsn1-1` already has `llama3.1:8b-instruct-q4_K_M` pulled; if not, `ollama pull llama3.1:8b-instruct-q4_K_M` (one-time, ~5 GB download) | D1 | WS1.2 |
| WS1.3 | On `fsn1-1`: install Docker CE + Caddy 2 (with `caddy-rate-limit`). **Do not install a second Ollama** — reuse shopfloor-copilot's. Confirm `curl http://127.0.0.1:11434/api/tags` from the host returns the model list. **Do not touch nbg1-1** beyond the SSH-hardening from WS1.2 — ai-radar is the only tenant there | D2 | WS1.2b |
| WS1.4 | Build & push Machina image (`--with-rag`); deploy on `fsn1-1` via `docker-compose.yml` with `MACHINA_MODE=demo`, `MACHINA_DEMO_HOST=https://demo.machinaos.ai`, `MACHINA_LLM_PROVIDER=ollama`, `MACHINA_LLM_URL=http://host.docker.internal:11434` *(reuses shopfloor-copilot's existing Ollama)*, `MACHINA_LLM_MODEL=llama3.1:8b-instruct-q4_K_M`, `MACHINA_MCP_AUTOSTART=fetch,memory,sequential-thinking,demo`, generated `MACHINA_REVIEWER_SECRET` | D2 | WS1.3 |
| WS1.5 | Apply Caddyfile from §3 of proposal on `fsn1-1` with **two vhosts**: `demo.machinaos.ai` (production demo container) and `staging-demo.machinaos.ai` (staging container). CORS `allow_origins=https://machinaos.ai`. Verify auto-TLS; confirm `https://demo.machinaos.ai/health` returns 200 | D2 | WS1.4 |
| WS1.6 | Spin up the **staging demo container as a second compose stack on `fsn1-1`** (different ports, different sandbox dir, same Ollama). nbg1-1 is reserved for ai-radar and is not part of this deployment | D3 | WS1.5 |
| WS1.7 | Wire Restic → Hetzner Storage Box (1 TB, ~€4/mo); first backup; verify restore                                                        | D4   | WS1.5      |
| WS1.8 | systemd unit for the docker-compose stack with restart-on-failure                                                                     | D4   | WS1.4      |

### WS2 — Anonymous-session entry (the "Try live" button)

This is the **only new code** required for go-live (everything else is
config or infra).  The shopfloor-copilot pattern is: visitor clicks
once, server provisions an isolated session, redirects them straight
into the working app.

| ID    | Task                                                                                                                                                  | Day | Depends on |
|-------|-------------------------------------------------------------------------------------------------------------------------------------------------------|-----|------------|
| WS2.1 | Add `POST /demo/start` endpoint: rate-limited per IP (stricter than the global 60/min — recommend 5/min/IP), creates a `DemoSessionManager` session in `DemoMode.DEMO` with 30-min TTL, returns `{session_id}` and sets `machina_demo` httpOnly cookie | D2  | —          |
| WS2.2 | Server-side rendering: when an unauthenticated request hits `/`, the landing page reads the cookie; if a valid session exists, the "Try live" button text becomes "Resume your session (29:14 left)" | D3  | WS2.1      |
| WS2.3 | Client-side: countdown badge in the top bar (existing demo badge) shows remaining TTL; "Extend" button (anonymous → +15 min once, capped at 60 m total) | D3  | WS2.1      |
| WS2.4 | "Reset workspace" button calls existing `POST /demo/reset` scoped to the visitor's session                                                            | D3  | WS2.1      |
| WS2.5 | Concurrency cap: refuse new anonymous sessions if `len(active_sessions) > 25` and surface a friendly "demo at capacity, try in a minute" page         | D4  | WS2.1      |
| WS2.6 | Telemetry: append `{event: "demo_start", ip_hash, user_agent, ts}` to `telemetry.db`; never store raw IP                                              | D4  | WS2.1      |
| WS2.7 | Lock the LLM panel in `DemoMode.DEMO` with a **branded overlay**: backend still rejects `PUT /llm/config` with 403 (security boundary), and the UI intercepts the response to show a glassmorphic modal — Material `lock` icon + headline *"This demo runs on a shared model"* + body explaining "Everyone gets the same Ollama · llama3.1:8b for a fair, predictable experience" + two CTAs: *"Install the desktop app"* (links to repo / future download) and *"Got it"* (dismiss). Same overlay component reused for blocked tools (`DEMO_TOOL_BLOCKED`) so the visual language is consistent. The Settings → LLM panel itself shows the field disabled with a small 🔒 badge instead of a writable input | D3 | WS2.1 |
| WS2.8 | Per-session token budget: count Ollama tokens in `DemoTelemetry`, enforce `MACHINA_DEMO_MAX_TOKENS_PER_SESSION` (default 50000), surface a friendly "demo budget exhausted — click Reset" banner when exceeded | D4 | WS2.1 |
| WS2.9 | Per-session sandbox workspace: on `/demo/start`, copy seed tree to `/data/sessions/<sid>/workspace/`, route every tool call through a request-scoped `workspace_root`; on session expiry, `shutil.rmtree` the directory | D3 | WS2.1 |

### WS3 — Marketing handshake (coordination only)

All landing-page work lives in the [`daviserra-code/machinaOS-AI`](https://github.com/daviserra-code/code/machinaOS-AI)
repo. This workstream's job is to give that repo exactly what it needs
from us, and nothing more.

| ID    | Task                                                                                                                                       | Day | Depends on |
|-------|--------------------------------------------------------------------------------------------------------------------------------------------|-----|------------|
| WS3.1 | Send the marketing repo a 1-page integration brief: the public URL (`https://demo.machinaos.ai/demo/start`), the redirect contract, the cookie name (`machina_demo`), the recommended `<a>` markup, and three deep-link variants (`?prefill=code-review`, `?prefill=security-sweep`, `?prefill=daily-brief`) | D2 | — |
| WS3.2 | Implement the `?prefill=<chain-id>` query param on `/demo/start`: if present and the chain exists in templates, the spawned session lands on `/app/#/studio?chain=<id>` instead of the home dashboard | D3 | WS2.1 |
| WS3.3 | Whitelist `https://machinaos.ai` (and `https://www.machinaos.ai`) in the API's CORS config; nothing else                                  | D2 | WS1.5 |
| WS3.4 | Add a press-friendly hero screenshot pack to `/srv/static/press/` (PNG + WebP) the marketing repo can hot-link                            | D4 | WS1.5 |
| WS3.5 | Open a tracking issue in the `machinaOS-AI` repo titled "Wire 'Try live' button to demo.machinaos.ai" with a checklist mirroring this workstream | D1 | — |

### WS4 — Token issuer + admin

| ID    | Task                                                                                                                                                       | Day | Depends on |
|-------|------------------------------------------------------------------------------------------------------------------------------------------------------------|-----|------------|
| WS4.1 | Build `machina-issuer` container per §4.3 of proposal                                                                                                      | D3  | WS1.4      |
| WS4.2 | Add `/issue/*` route to Caddy with basic-auth (operator-only)                                                                                              | D3  | WS4.1      |
| WS4.3 | Add `/admin/issue` HTML page (basic-auth) — form: reviewer-id, TTL hours, generates redeem URL, copies to clipboard, logs row to `issued_tokens.db`        | D4  | WS4.1      |
| WS4.4 | Add `/admin/sessions` view (basic-auth): table of active demo sessions, mode, TTL remaining, "kick" button                                                 | D5  | WS4.1      |
| WS4.5 | Add `/admin/reset` button calling `POST /demo/reset` to wipe demo state between guided sessions                                                            | D5  | WS4.1      |

### WS5 — Operations & legal (backend half)

Legal copy (Privacy, ToS, cookie banner) lives on the marketing site
and belongs to the `machinaOS-AI` repo. This workstream covers only the
backend obligations and the data the demo backend itself collects.

| ID    | Task                                                                                                                                              | Day | Depends on |
|-------|---------------------------------------------------------------------------------------------------------------------------------------------------|-----|------------|
| WS5.1 | Send the marketing repo a 1-page "data we collect" memo (session_id, ip_hash, user_agent, tool-invocation counts, retention 30 d, no LLM keys, no GitHub PAT) so they can write the public Privacy Notice accurately | D1 | — |
| WS5.2 | Status page: `https://demo.machinaos.ai/status` — API health + Ollama health + active session count + queue depth, JSON + tiny HTML view         | D4 | WS1.5 |
| WS5.3 | On-call rota (probably just Davide for v1 — document anyway): who responds to a fail2ban alert, who can SSH, escalation chain                    | D2 | — |
| WS5.4 | Incident playbook: 1-pager for the five likely failure modes (Ollama OOM, disk full, fail2ban locked own IP, DNS misconfig, runaway demo session) with the fix command | D3 | — |
| WS5.5 | GDPR self-check for backend telemetry: legal basis (legitimate interest), retention 30 days, deletion script (`scripts/purge_demo_telemetry.py`); send result to marketing repo for inclusion in their public Privacy Notice | D4 | WS5.1 |

---

## 4. Two-week timeline

```
        Mon       Tue       Wed       Thu       Fri       Mon       Tue       Wed       Thu       Fri
       D1        D2        D3        D4        D5        D8        D9        D10       D11       D12
WS1   ┃DNS+SSH ┃Docker  ┃Staging ┃Restic+ ┃         ┃         ┃         ┃         ┃         ┃
       ┃        ┃Ollama  ┃        ┃systemd ┃         ┃         ┃         ┃         ┃         ┃
WS2            ┃/demo   ┃Cookie+ ┃Cap+tok ┃         ┃         ┃         ┃         ┃         ┃
                ┃start   ┃LLM lock┃budget  ┃         ┃         ┃         ┃         ┃         ┃
                ┃        ┃sandbox ┃telem   ┃         ┃         ┃         ┃         ┃         ┃
WS3   ┃Open    ┃Brief + ┃Prefill ┃Press   ┃         ┃         ┃         ┃         ┃         ┃
       ┃issue   ┃CORS    ┃param   ┃pack    ┃         ┃         ┃         ┃         ┃         ┃
WS4                      ┃Issuer ┃Admin   ┃Sessions┃         ┃         ┃         ┃         ┃
                          ┃cont.  ┃UI      ┃+reset  ┃         ┃         ┃         ┃         ┃
WS5   ┃Data    ┃On-call ┃Playb.  ┃Status+ ┃         ┃         ┃         ┃         ┃         ┃
       ┃memo    ┃        ┃        ┃GDPR    ┃         ┃         ┃         ┃         ┃         ┃

DRY-RUN  ─────────────────────────────────────────────► D8 internal walkthrough (3 personas)
SOFT-LAUNCH ──────────────────────────────────────────► D10 staging-demo URL shared with 5 friendly testers
PUBLIC LAUNCH ────────────────────────────────────────► D12 marketing repo flips its CTA to demo.machinaos.ai
```

Slip budget: 3 working days. The public-launch date is also gated on the
`machinaOS-AI` repo finishing its landing page — coordinate explicitly
before committing to D12.

---

## 5. Definition-of-done for "publicly launched"

The demo is live when **all** of these are true:

1. ☐ Hitting `https://demo.machinaos.ai/demo/start` from a clean
   browser sets the cookie and lands the visitor in a working
   Machina OS UI inside 10 s.
2. ☐ The session shows a TTL countdown badge and auto-expires.
3. ☐ `shell.run`, `process.stop`, `filesystem.delete`, `vscode.*`,
   `browser.open_url`, `mcp.servers.add` are blocked in `DemoMode.DEMO`.
4. ☐ The Settings → LLM panel is read-only and shows `Ollama · llama3.1:8b`. Attempting to edit triggers the branded overlay modal (not a raw 403).
5. ☐ Each session writes only inside `/data/sessions/<sid>/`; expiry
   removes that directory entirely.
6. ☐ Reviewer token redemption works end-to-end (mint → redeem → cookie
   → REVIEWER mode → can save a note, cannot run shell).
7. ☐ Restic backup ran successfully at least once.
8. ☐ A killed container restarts automatically (systemd test).
9. ☐ Caddy serves `https://demo.machinaos.ai` with A+ TLS rating
   (ssllabs.com/ssltest).
10. ☐ CORS allows `https://machinaos.ai` and rejects everything else
    (verify with `curl -H 'Origin: https://evil.example' -i …`).
11. ☐ Status page returns green for API + Ollama + Caddy + MCP autostart.
12. ☐ Dry-run with 3 personas (anonymous, reviewer, operator) all
    succeeded with no manual intervention.

---

## 6. Risk register

| #   | Risk                                                                  | Likelihood | Impact | Mitigation                                                                                            |
|-----|-----------------------------------------------------------------------|------------|--------|-------------------------------------------------------------------------------------------------------|
| R1  | Ollama 70b too slow → demo feels broken                               | Medium     | High   | Default to `llama3.1:8b` for launch; benchmark 70b on fsn1-1 before promoting                         |
| R2  | Concurrent demo prompts starve shopfloor-copilot's LLM routines | Medium | Low (internal, async) | Ollama serializes by default; 25-session concurrency cap + 5/min/IP rate limit; shopfloor-copilot is internal-only and tolerates async waits |
| R2b | ai-radar (6k visits/day, on `nbg1-1`) degrades because of demo traffic | **N/A by design** | High *if it happened* | Demo + Ollama live on `fsn1-1` only; nbg1-1 is reserved for ai-radar exclusively (Q1, Option A). Verified by checklist line "nothing demo-related touches nbg1-1" |
| R3  | Visitor abuses `shell.run_safe` to mine / scan                         | Low        | High   | `DemoMode.DEMO` blocks shell entirely; reviewers get only `REVIEWER` extras; per-tool execution limits already enforced |
| R4  | Disk fills with notes/reports → API stalls                             | Medium     | Medium | `DemoSessionManager` already wipes session dirs on expiry; add disk-watchdog at 80 % to trigger reset |
| R5  | Token leaks publicly → 7-day press token gives wide access              | Low        | Medium | Reviewer tokens are per-`reviewer_id`; rotate `MACHINA_REVIEWER_SECRET` to invalidate all tokens at once |
| R6  | DNS / TLS misconfig blocks launch day                                   | Low        | High   | Stage on `staging.machinaos.ai` first; only flip apex DNS after staging dry-run passes                |
| R7  | A visitor screenshots a previous session's leftover data                | Low        | Medium | `DemoMode.DEMO` uses fresh session-scoped workspace; no cross-session reads possible                 |
| R8  | GDPR complaint about IP logging                                        | Low        | Low    | Hash IP at intake (WS2.6); delete telemetry > 30 days (WS5.7)                                         |
| R9  | Hetzner outage in Falkenstein (`fsn1-1` down) | Low | High | Demo is offline until fsn1-1 returns. **No automatic failover** in v1: `nbg1-1` runs ai-radar and cannot host the demo without evicting it. Runbook documents manual recovery (restic restore on a freshly provisioned CPX62 in another DC, ~30 min RTO). Acceptable for a free demo. Revisit if demo SLA tightens. |
| R10 | First impression on press = stale demo (someone else's mid-task state) | Medium     | Medium | Auto-reset every session; "Reset" button always visible; `/admin/reset` between scheduled press demos |

---

## 7. Pre-launch checklist (the day before public)

```
[ ] DNS A demo.machinaos.ai → 46.224.66.48
[ ] DNS A staging-demo.machinaos.ai → 46.224.66.48 (same box, different vhost)
[ ] curl https://demo.machinaos.ai/health → 200
[ ] curl https://staging-demo.machinaos.ai/health → 200
[ ] SSL Labs grade ≥ A on demo.machinaos.ai
[ ] /demo/start sets cookie + redirects to /app/
[ ] Anonymous can run filesystem.list, cannot run shell.run
[ ] LLM Settings panel shows Ollama · llama3.1:8b read-only; edit attempt shows branded overlay (not raw 403)
[ ] fsn1-1: shopfloor-copilot's Ollama reachable from the demo container at http://host.docker.internal:11434/api/tags
[ ] fsn1-1: only **one** Ollama process running (`pgrep -c ollama` returns 1)
[ ] nbg1-1: nothing demo-related installed; only ai-radar + system services running (`docker ps` shows no machina-* containers)
[ ] Per-session sandbox /data/sessions/<sid>/ created and removed on expiry
[ ] Reviewer token mint → redeem → can run notes.create
[ ] CORS rejects requests from origins other than https://machinaos.ai
[ ] Restic last-snapshot < 24 h
[ ] systemctl status machina-stack → active (running)
[ ] fail2ban-client status → caddy + sshd jails active
[ ] disk < 60 % on fsn1-1 (nbg1-1 not in scope)
[ ] Ollama responds on http://127.0.0.1:11434/api/tags within 2 s
[ ] All four MCP servers (fetch, memory, sequential-thinking, demo) green
[ ] /admin/sessions accessible behind basic-auth, not over public path
[ ] Marketing repo confirmed the 'Try live' button points at demo.machinaos.ai/demo/start
[ ] Status page green
[ ] Operator phone has SSH key + runbook URL bookmarked
```

---

## 8. Soft-launch & feedback loop

D10 (soft launch): share `https://staging-demo.machinaos.ai/demo/start`
privately with 5 friendly testers (mix of devs + non-devs). The
marketing repo's button still points nowhere public at this stage.
Collect:

- Time to first visible result (target < 30 s from CTA click).
- Confusion points in the guided tour.
- Any unexpected `403`/`500` from the demo middleware.
- Sub-15-min churn vs. >15-min engaged sessions in `telemetry.db`.

Triage feedback for 48 h, ship one polish pass, then announce publicly
on D12.

---

## 9. Post-launch (week 3–4)

| Item                                              | Trigger                                       |
|---------------------------------------------------|-----------------------------------------------|
| Promote 70b model                                  | Median LLM latency < 2 s on 8b for a week     |
| Add Hetzner LB11 in front of both VMs             | > 100 unique sessions/day                     |
| Add Plausible / Umami self-hosted analytics        | Need conversion data for the marketing CTA    |
| Add **press@machinaos.ai** mailbox + auto-reply   | Inbound press requests start arriving         |
| Move LLM to GPU instance (GEX44 or rented A100)   | 70b feels slow even after the upgrade         |
| Public status page (`status.machinaos.ai`)        | First real outage incident                    |

---

## 10. Decisions needed from operator (before D1)

1. ☐ Confirm we control the `machinaos.ai` DNS zone (add `demo.` and `staging-demo.` subdomains there) and that the marketing repo is OK with us owning those subdomains.
2. ☐ Confirm SSH key access to both `46.224.66.48` and `46.224.91.14`.
3. ☐ Confirm both servers can be wiped (no other workloads to preserve).
4. ☐ Choose backup destination: Hetzner Storage Box (default) or Backblaze B2.
5. ☐ Approve initial 5/min/IP rate limit on `/demo/start`.
6. ☐ Approve initial concurrent-session cap of 25.
7. ☐ Approve **30-min** TTL for anonymous sessions.
8. ☐ Approve **Ollama + llama3.1:8b** as the locked LLM for v1 (Q1).
8b. ☐ Approve **reusing shopfloor-copilot's existing Ollama on `fsn1-1`** (no second Ollama installed). Demo + staging both run on `fsn1-1`; `nbg1-1` is reserved for ai-radar and untouched.
8c. ☐ Acknowledge the trade-off: shopfloor-copilot routines may wait 5–15 s for LLM responses while a demo visitor is mid-prompt. Acceptable because shopfloor-copilot is internal-only.
9. ☐ Approve **per-session sandbox under `/data/sessions/<sid>/`** as the only filesystem visible to demo tools (Q2).
10. ☐ Approve **`MACHINA_DEMO_MAX_TOKENS_PER_SESSION=50_000`** as the default per-session LLM budget.
11. ☐ Provide a single ASCII operator handle for the `admin` basic-auth user (will be hashed with bcrypt and stored as `ADMIN_BCRYPT_HASH` env var).
12. ☐ Open the tracking issue on `machinaOS-AI` so the marketing-side work starts in parallel.

A 30-minute kickoff covering items 1–12 unblocks the entire 12-day plan.
