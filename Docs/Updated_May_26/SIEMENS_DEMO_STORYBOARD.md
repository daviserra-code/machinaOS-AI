# Siemens / AI-Fair Keynote Storyboard

> **Goal:** leave the room convinced Machina OS is a category-defining,
> production-grade, local-first multi-agent operating layer.
>
> **Time budget:** 12 minutes (3 acts × 4 min). Pad to 20 min with Q&A.
> **Optional encore:** Act 4 (3 min) — *"MCP, Live and Remembering"* —
> deploys when the audience leans in on MCP after Act 3 and you want to
> close the loop with real, registered servers instead of stand-ins.
>
> **Killer artefact per act:** a branded HTML executive report opens in the
> browser, live, produced by real agents running real scans.

---

## Stage Setup (60 s before you start)

1. **Two windows visible:** VS Code (code editor on the right) + Machina OS
   desktop app (left, fullscreen-ready).
2. **Workspace set** to `demo-repos/acme-vulnerable/` via the Working-Directory
   picker (Ctrl+K → "working directory" → click). This repo ships planted
   vulnerabilities so the audits produce *real* findings on a *real* codebase.
3. **Internet off** (optional, for maximum effect). Tell the room:
   *"Everything you see runs on this laptop. No API calls leave this room."*
4. **Ollama running** locally with a small model (llama3.2:3b or similar)
   so planning stays quick. The LLM status dot in the bottom bar must be
   green.
5. **Studio view pre-loaded.** Open Studio (Ctrl+6). Leave canvas empty.

---

## Act 1 — "The Production-Readiness Audit" (4 min) · **Keynote**

> **Chain:** `production-readiness-audit`
> **What the audience sees:** agents swarm a repo, audit it across 4 dimensions,
> produce a branded HTML report, and open it in a browser — all in one click.

### 1a — The setup (30 s)

You say:
> "Here's a real microservice. Customer portal. Flask. Maybe 200 lines.
> The CTO wants it in production next week. The question every engineering
> manager asks: **is it ready?** Normally that's a week of audit work —
> security review, dep audit, test-coverage report, documentation check.
> Let's do it in 60 seconds."

**Action:** open VS Code briefly, show `src/users.py`, scroll past the
SQL-injection line. Let them see real code. Close it.

### 1b — Load the chain (20 s)

1. In Studio, click **"Open Chain"** → scroll to **🎯 Production Readiness
   Audit (Keynote)** → click.
2. The canvas auto-fits. Audience sees **8 nodes** wired together:
   `security-audit → dependency-check → code-quality-scan → documentation-audit
   → secrets grep → insecure-patterns grep → test inventory → system info
   → report.generate → browser.open_url`.

You say:
> "This chain composes **four sub-chains** — entire audit workflows — plus
> direct scans. That's the **chain-to-chain composition** we ship out of the
> box. Each sub-chain is itself reusable. Today we're wrapping them."

### 1c — Presenter mode (10 s) — **THE WOW**

1. Click the **Presenter** button in the Studio toolbar (or press **F9**).
2. The UI transforms: nav hidden, fullscreen canvas, branded status strip
   at the bottom shows `Steps 0/10 · Running — · Succeeded 0 · Failed 0 ·
   Data egress 0 B · LOCAL`.
3. Click **▶ Run chain** in the bottom-right.

### 1d — The swarm (2 min)

Narrate as nodes light up:

- *Amber pulse* on `security-audit` → sub-chain expands, grep runs, hits on
  `password`, `admin123`, `sk-live-AcmeProd-…`.
  > "That's the production API key — checked into source control. That one
  > finding alone would fail a SOC 2 audit."
- *Green check* on security-audit. `dependency-check` starts.
  > "Flask 1.0.2. Cryptography 2.6.1. Multiple CVEs each."
- *Green check* on dependency-check. `code-quality-scan` starts.
- `documentation-audit` runs.
- The four direct scans fire.
- `report.generate` runs (green in ~200 ms).
- `browser.open_url` fires.

### 1e — The payoff (60 s) — **THE REPORT OPENS**

A real browser tab pops up with a glassmorphic, branded executive report:
- Title: **Production Readiness Audit**
- Metric strip: 4 sub-chains · 6 agents · 20+ tool invocations · **0 B egress**
- Sections: **Security Findings** (5 findings with CWE IDs, locations,
  remediation) · **Dependency Risks** · **Test Coverage** · **Documentation &
  Compliance** · **Verdict: 🚨 NOT READY FOR PRODUCTION**.
- Footer: **SHA-256 audit hash** of the report contents.

You say:
> "This report landed in `<workspace>/reports/` as a static HTML file. The
> SHA-256 at the bottom is the tamper-evident hash of every finding. Our
> full SOC 2 audit log — hash-chained — is in the Security Center. Try
> getting that from a cloud coding assistant."

**Sit back. Let them look.**

### 1f — Closer (20 s)

> "That was **10 steps across 6 agents** orchestrated by **4 composed
> sub-chains**, producing an auditable report, in under a minute, fully
> on-prem. Now let me show you how those agents actually think."

Exit Presenter (ESC).

---

---

## Act 1.5 — "Chains Inside Chains" (2 min) · **Chain-to-Chain Composition**

> **Mode:** Live Studio canvas construction — not a pre-built chain. This
> act is a short, high-impact interlude best used when the Act 1 report
> lands well and the audience is still marvelling at the graph.
>
> **What the audience takes away:** the chain that just produced the report
> is itself composable. Any chain can be snapped into another chain as a
> single step. The whole system is recursive.

---

### 1.5a — The one-liner (10 s)

_Still on the Act 1 canvas. Point at any sub-chain node._

> "Each of these coloured steps? It's not a tool call. It's another
> chain — with its own steps, its own agents, its own audit trail.
> Let me show you how that's built, in about 90 seconds."

---

### 1.5b — Open the Chains palette tab (20 s)

1. Click **New Canvas** (blank icon in Studio toolbar).
2. In the left palette, click the **Chains** tab (4th tab, link icon,
   rose-coloured).

_The palette fills with all available chains — including `security-audit`,
`dependency-check`, `code-quality-scan` etc. — the sub-chains that just ran._

> "These are reusable chain components. I'm going to snap two of them
> into a new chain — one that didn't exist 60 seconds ago."

---

### 1.5c — Drag chains onto the canvas (40 s)

1. **Drag `security-audit`** from the palette onto the canvas.
   A rose-coloured node appears with a link icon and a `chain` badge.
   The step list preview on the node shows the sub-steps inside.
2. **Drag `dependency-check`** onto the canvas. Another rose node.
3. **Draw an edge** from the output port of `security-audit` to the
   input port of `dependency-check`.
4. Add one more normal tool node: **drag `report.generate`** from the
   Tools tab, wire it in.

Point at the canvas:
> "Three nodes. One is a whole audit chain. One is a dep-check chain.
> One is a report generator. Together they form a new chain — right now,
> no YAML, no config file."

---

### 1.5d — Save and execute (30 s)

1. Type a name in the chain name field: **"On-Demand Audit"**.
2. Click **Save**. The chain persists to SQLite.
3. Click **▶ Execute**.

_Nodes light up: `security-audit` (amber pulse → green), `dependency-check`
(amber → green), `report.generate` (green in ~200 ms)._

> "That just ran a full two-sub-chain audit pipeline. Every step inside
> each sub-chain ran. The parent chain saw a single green node. The
> recursion is transparent — and the audit log captures every level."

---

### 1.5e — Closer (10 s)

> "This is **chain-to-chain composition**. You don't redesign your
> workflows — you **compose** them. The same primitives, infinitely
> stackable. Up to 5 levels deep, with cycle detection."

---

## Act 2 — "Watch the Agents Negotiate" (3 min) · **Depth + Conditional Branching**

> **Chain:** `agent-negotiation-refactor` (9 steps · 3 conditionals · 1 cross-agent branch)
> **Mode:** Debug step-by-step — NOT the normal Execute button. This keeps
> the pace in the presenter's hands and lets each beat land before the
> next fires.
>
> **What the audience takes away:** agents have specialties and reputations;
> the chain itself branches on live evidence; the whole thing is
> transparent and auditable — not a black box.

---

### 2a — Tell the story before you touch anything (30 s)

_Stand away from the keyboard. Look at the audience._

> "A moment ago, the chain ran as a **fleet** — all agents in sync, no
> decisions to make. Now I want to show you what happens when there **is**
> a decision. Two specialists. One problem. Only one of them gets the
> contract. And the codebase decides who wins."

> "Think of it like a building inspection where two contractors send in bids.
> The building itself — the code — is the evidence. Whoever's track record
> fits the evidence best gets the job. That's the negotiation you're about
> to watch."

`[pause 2 s]`

---

### 2b — Canvas tour: show the shape before it runs (30 s)

Studio → Open Template→ **🎯 Multi-Agent Negotiation (Demo B)**.

_Wait for the canvas to auto-fit (about 1 s). Point at the screen._

> "Nine steps. Read it left to right."

**Point at the two scan nodes (nodes 1–2):**
> "First: two evidence-gathering probes. Code smells. TODOs. Both scan the
> same codebase. We're collecting evidence before we pick anyone."

**Point at the three amber diamond nodes (nodes 3–5):**
> "See the amber diamonds? Those are **gates**. They only open if the
> evidence says so. If there are no code smells, the security-auditor's
> bid never even gets drafted. The gate stays closed."

**Hover over the gate condition text on node 3:**
> "The condition is literally `smells:count not_empty`. No magic. Readable.
> Auditable."

**Point at the arrow crossing between lanes near the end:**
> "And here — this arrow **changes lanes** depending on what `git.status`
> returns. Clean working tree: the merge-inspection runs in the Git lane.
> Dirty tree: it re-routes to the Filesystem agent instead. Same chain,
> two possible worlds, decided at runtime."

`[pause 2 s]`

---

### 2c — Step-through execution: one beat at a time (90 s)

> "I'm going to use the **step debugger** — the same tool the team uses
> in development — so you can see exactly what fires and when. There's
> no fast-forward here."

1. In the Studio toolbar, click **🐛 Debug** (not the ▶ Run button).
   A debug control strip appears: **Step Over | Continue | Stop**.
2. The status tray opens at the bottom showing all 9 pending steps.

**Click Step Over** — first node starts (amber pulse).
> "Node 1 is running: `filesystem.grep` looking for code smells."

**Click Step Over** — node 1 completes (green check + flow animation on
the outgoing edge).
> "Found them. Five smell patterns. Those matches are now in the chain's
> memory — the next node will read them."

**Click Step Over** — second grep runs.
> "Node 2: looking for TODOs. Also found."

`[pause 1 s — let the audience see both green nodes]`

**Click Step Over** — gate node for Security-Auditor Bid evaluates.
> "Here's gate one. `smells:count not_empty` — is it? Yes. The gate opens."
> Amber badge → green. The bid step runs.

**Click Step Over** — Security-Auditor bid recorded.
> "The security-auditor's bid is drafted. Confidence score: **0.91**,
> driven by its history of finding eval() and injection patterns."

**Click Step Over** — gate for Refactorer Bid evaluates.
> "Gate two. TODOs found? Yes. The refactorer's bid opens."
> Green. The bid step runs.

**Click Step Over** — Negotiation Outcome step runs.
> "And this is the negotiation. Both bids are in. Capability-weighted
> resolution. Security wins on the smell surface — delta 0.13."

`[pause 2 s — let the win sink in]`

**Click Step Over** — `git.status` runs.
> "Now the branch question. Is the working tree clean or dirty?"

_Look at the canvas — the git.status node goes green._
> "Dirty. Uncommitted changes. Watch this."

**Click Step Over** — **the branch fires**.

The outgoing edge swings to the alternative lane. The alternate node
lights up amber.

> "Did you see that? The arrow re-routed. The merge-inspection step just
> moved from the Git agent to the Filesystem agent — automatically —
> because the live git state said 'not clean'. The chain adapted. **No
> code change. No re-deployment.** Just a condition and a new path."

`[pause 3 s — do not talk. Let them watch the canvas]`

**Click Continue** — remaining steps run to completion.

> "Report generating…"

`[pause 2 s while the browser opens]`

---

### 2d — Switch to Communications (30 s)

_After the browser opens — close it or move to background. Back in Machina._

Exit debug mode (ESC or Stop). Switch to **Agents view → Communications
sub-tab**.

_The communication graph has just been populated. Zoom in with scroll wheel._

> "Every message the agents exchanged is here. Hover over any edge."

_Hover an amber edge (negotiation)._

> "This tooltip tells you: who proposed, who countered, the confidence
> delta, the round number. The sequential numbers on the edges — **#1,
> #2, #3** — are the order the messages fired."

**Click the Negotiation Timeline** button on the negotiation card:
> "Round one: security-auditor proposes. Round two: refactorer counters —
> 'I can mitigate, not remove.' Round three: resolved by priority weight.
> Full replay. Immutable. Persisted to SQLite. That's your audit trail."

`[pause 1 s]`

> "After this run, the security-auditor's **reputation score** goes up on
> eval() patterns. Next time it competes for a similar task, it wins faster.
> **The agents learn this codebase.** Not a chatbot. A workforce."

---

### 2e — Report and closer (20 s)

The browser tab already shows the **Refactoring Negotiation Outcome**
report. Point at it briefly.

> "Metric strip: 2 bidders, 2 rounds, 3 conditional branches, 1 cross-agent
> re-routing. SHA-256 at the bottom. SOC 2 audit log has every step."

`[pause 1 s]`

> "A workforce. With a track record. With branching logic. With an audit
> trail. **Not a chatbot.**"

---

## Act 3 — "One Chain, Many Worlds" (3 min) · **MCP + Conditional Alerting**

> **Chain:** `mcp-cross-system-sweep` (12 steps · 7 subsystems · 2 conditional
> alert channels · 5 MCP-replaceable steps)
> **What the audience sees:** a single chain spanning **seven subsystems**
> with **two conditional alert channels** that route the outcome through
> either a Slack-style notification **or** a GitHub-issue-style incident
> ticket — depending on real-time git state. Each notification step is
> staged exactly where a real MCP server would slot in.

### 3a — The pitch (20 s)

You say:
> "Model Context Protocol — Anthropic's open standard. GitHub. Postgres.
> Slack. AWS. Any tool speaking MCP becomes an agent capability in Machina
> OS. **One chain. Many worlds. Zero glue code.** And — watch this —
> the chain decides which world to notify based on real data."

### 3b — Show the MCP registry (20 s)

Navigate to **MCP Protocol view** (Ctrl+9 or dock). Show the **Quick Pick**
panel: 14 curated npx packages — GitHub, Postgres, Slack, Brave Search,
Filesystem, SQLite, Memory, Git, AWS, etc.

> "Two clicks and a real GitHub MCP server is running in a subprocess. Same
> for Postgres. Same for Slack. These speak the **same tool dispatch** as
> our native integrations. Same chain plane. Same audit log."

### 3c — Open the chain in Studio (15 s)

Studio → Open Tmp → **🎯 MCP Universal Orchestrator (Demo C)**.

The canvas explodes with **12 nodes across 4 agent lanes**, with a
**diverging arrow pair** at the bottom — the conditional Slack/GitHub
branch.

Point at the canvas:
> "Seven probes. Two alert channels. The Slack notification only fires if
> the working tree is clean. The GitHub incident ticket only fires if it's
> dirty. **Mutually exclusive paths**. The chain decides."

Also point at the descriptions:
> "Notice the captions on each step — `(would-be: postgres.query via MCP)`,
> `(would-be: slack.post via MCP)`, `(would-be: github.create_issue via
> MCP)`. These are the **exact MCP tool names** that would replace the
> stand-ins. The chain shape doesn't change. Only the tool names do."

### 3d — Run in Presenter mode (90 s)

1. F9 → Presenter mode.
2. Click **▶ Run chain**. Narrate:

- **Phase 1 — Probe the host:** `system.info`, `system.disk`, `system.memory`
  all light green in rapid succession.
  > *"Three host probes — in production these are AWS / Prometheus /
  > Datadog MCP calls."*
- **Phase 2 — Probe the codebase:** `git.status`, `git.log`, `filesystem.tree`.
  > *"Three codebase probes — in production the git ones are GitHub MCP
  > calls against the remote."*
- **Phase 3 — DB-style audit:** `filesystem.grep DATABASE_URL` runs.
  > *"This is a stand-in for `postgres.query SELECT * FROM secrets WHERE
  > value LIKE …` via the Postgres MCP server. One MCP install away."*
- **Phase 4 — THE BRANCH FIRES.** Either:
  - 💬 **Slack #releases** node turns green (clean tree, ship signal posted)
  - 🚨 **Incident channel** node turns green (dirty tree, ticket filed)
  - **The other one stays grey/skipped.**

  > *"There. Mutually exclusive alert paths. The chain just decided which
  > channel gets the notification based on **live git state**. In
  > production these become real Slack messages and real GitHub issues —
  > with the **same chain shape**."*

### 3e — The report (30 s)

Report opens — **MCP Cross-System Sweep**. Metric strip: **7 subsystems
probed · 4 agents · 2 conditional alert paths · 5 MCP-replaceable steps
· 0 lines of glue code**.

The **Native today, MCP tomorrow** section spells out the migration:
- `notes.create '🚨 Incident…'` → `github.create_issue`
- `notes.create '💬 Slack…'`    → `slack.post`
- `filesystem.grep DATABASE_URL` → `postgres.query`

> "Same chain. Same conditions. Same audit trail. Just swap the tool
> names when the MCP servers come online. **No glue code. No re-design.**"

### 3f — Closer (30 s)

You say:
> "To recap: in twelve minutes you saw a multi-agent operating layer
> audit a codebase, **bid + branch + negotiate** over a refactor, and
> orchestrate **seven subsystems with conditional MCP-ready alerting**.
> All on this laptop. All auditable. All reversible.
>
> This is Machina OS. We ship as a 125 MB desktop installer. Windows,
> macOS, Linux. Zero prerequisites. Want the beta? Come talk to me."

---

## Act 4 — "MCP, Live and Remembering" (3 min) · **Optional Encore · The Agentic Internet**

> **One-line pitch to remember:** *"In Act 3 the MCP boxes were
> placeholders. In Act 4 they're real network calls to real third-party
> servers, and the result survives a reboot."*
>
> **When to deploy:** when the room leans in on MCP during Act 3 and you
> want to *prove* the swap-the-tool-name story is real, not theatre.
> Skip if you're tight on the 12-min clock.
>
> **What the audience takes away (3 plain-English claims):**
> 1. Machina can talk to **third-party servers** over an open protocol —
>    we'll call Anthropic's `fetch` and `memory` servers live.
> 2. One of those servers can hold **state on its own disk**, and we can
>    read that state back later — even after closing everything.
> 3. The user **never wrote any glue code**. Every server is registered
>    once, then any chain can use it.
>
> **Two chains you'll run:**
> - **MCP Live Recall (Encore)** — 6 steps · fetches a real URL, writes
>   to memory, reads it back, shows a report.
> - **MCP Recall Test (Encore B)** — 1 step · same memory query as
>   above, run from a fresh chain to prove the data was *persisted*, not
>   just kept in RAM.

### 4a — Set the scene (20 s)

_Exit Presenter mode. Switch to the **MCP Protocol view** (Ctrl+9)._

You say (slow, deliberate):
> "In Act 3 I said the MCP servers were standing in for placeholders.
> Now I'm going to swap them for **the real thing**. Same protocol.
> Different processes — running right here on this laptop."

Point at the Servers tab. **Four** green dots (the ones we actually use):
- `fetch` — official Anthropic, runs as `npx @tokenizin/mcp-npx-fetch`
- `memory` — official Anthropic, runs as `npx @modelcontextprotocol/server-memory`
- `sequential-thinking` — official Anthropic, runs as `npx ...sequential-thinking`
- `demo` — our reference server, 220 lines of stdlib Python, ships in the repo

> "Three of these come from Anthropic. The fourth is ours — proof anyone
> can build one in an afternoon. Each green dot is a separate **child
> process** with its own memory and its own disk. We're talking to them
> over stdin/stdout. That's MCP."

### 4b — The Prompts tab — what the spec actually says (25 s)

Click the **Prompts** sub-tab.

You say:
> "MCP defines three things a server can publish: **tools** (do
> something), **resources** (read something), and **prompts** (templated
> questions that aren't an LLM call)."

Point at the four populated cards (from the `demo` server):
**`summarize`, `code_review`, `brainstorm`** *(plus an extra)*.

> "Our demo server publishes all three surfaces. The other servers — like
> Anthropic's `memory` — only publish tools today, so the panel honestly
> shows *Method not found* for them. No ghost cards, no silent failures.
> What you see is what each server actually exposes."

### 4c — Walk through the chain on the canvas (20 s)

Studio → Open Chain → **MCP Live Recall (Encore)**.

The canvas auto-fits. Six nodes, top-to-bottom:

```
1. mcp.fetch.fetch_markdown        ← grab a real public README over HTTPS
2. mcp.demo.echo                   ← demo MCP "reasoning" stand-in
3. mcp.memory.create_entities      ← write a node into Anthropic's memory server
4. mcp.memory.search_nodes         ← read it back inside the SAME chain
5. report.generate                 ← render a branded HTML report
6. browser.open_url                ← open it in Chrome
```

Point at the first node and the third node:
> "Two completely different vendors. The first one fetches HTTP for us.
> The third one keeps a knowledge graph. We didn't write any code to
> connect them — we picked their names from a list."

### 4d — Run the chain · narrate one step at a time (70 s)

1. Hit **F9** → Presenter mode.
2. Click **▶ Run chain**.

As each node turns green, say *exactly* this — one sentence per step,
no fog:

- **Step 1 — `mcp.fetch.fetch_markdown` ✓ green**
  > *"That just made a real HTTPS request to GitHub through Anthropic's
  > fetch server. The bytes you'll see in the report came over the
  > network 200 milliseconds ago."*

- **Step 2 — `mcp.demo.echo` ✓ green**
  > *"That's our demo MCP server doing a stand-in for a reasoning step.
  > In a production deployment this would be Anthropic's
  > sequential-thinking server — it's the same protocol, same
  > integration."*

- **Step 3 — `mcp.memory.create_entities` ✓ green**
  > *"We just wrote a typed object — name, type, observations — into
  > Anthropic's memory server. **That's a different process holding state
  > for us, on its own disk.** We don't have a database here. The MCP
  > server is the database."*

- **Step 4 — `mcp.memory.search_nodes` ✓ green**
  > *"And we just **read it back** in the same chain. Round-trip
  > confirmed. Wrote, then read."*

- **Step 5 — `report.generate` ✓ green**
  > *"All step outputs went into a branded HTML file."*

- **Step 6 — `browser.open_url` ✓ green** → *report opens in Chrome*
  > *"Local file. Zero data left this laptop except that one HTTPS GET
  > to fetch the README."*

`[pause 3 s — let them read the report's title and section headings]`

### 4e — The persistence proof (40 s)

Exit Presenter (ESC). Close the report tab.

> "Now the part the AI demos usually skip. I'm going to close this
> chain, open a **completely separate** one-step chain, and ask the
> memory server: *do you still have that thing we wrote a minute ago?*"

Studio → Open Chain → **MCP Recall Test (Encore B)**.

Show the canvas — **one** node + a small report node:
```
1. mcp.memory.search_nodes   query="AnthropicCookbook"
2. report.generate           (renders the result)
3. browser.open_url
```

Click **▶ Execute**.

Two things happen in parallel — point at *both*:

1. **Studio results tray (left side)** — the node turns green and shows
   the raw JSON the MCP memory server returned: `{"entities":
   [{"name": "AnthropicCookbook", ...}]}`.
2. **Browser** — a new "MCP Memory Recall Test" report tab opens.

You say:
> "Same entity. Same observations. Same name. The memory server kept it
> for us in a separate npx process — and **if I rebooted this laptop
> right now and ran that one chain again, the answer would be
> identical**. That's the difference between an agent that *chats* and
> an agent that *operates*. Operators remember."

`[pause 2 s]`

### 4f — Closer (15 s)

> "To recap Act 4: **two real third-party MCP servers**, one round-trip
> write-then-read, and the result survives across runs. No glue code, no
> custom integration."

`[pause 1 s]`

> "Every MCP server you saw today is **one click away** in our Quick
> Pick panel — fourteen curated packages. We're not asking you to bet on
> us. We're asking you to bet on the **protocol**. We just happen to be
> the best place to run it."

---

## Presenter Checklist

Before you go on stage:

| Check | How |
|-------|-----|
| Workspace = `demo-repos/acme-vulnerable/` | Ctrl+K → working directory |
| LLM dot green | Bottom status bar |
| Ollama model pulled | `ollama list` — llama3.2:3b or similar |
| `reports/` folder empty | Fresh `rm demo-repos/acme-vulnerable/reports/*.html` |
| Notifications silenced | macOS Focus / Windows Focus Assist |
| Browser default set | So `browser.open_url` lands in the right window |
| Studio pre-loaded | `Ctrl+6` |
| Dry-run once | Full dress rehearsal ≥ 2 h before |
| **Act 4 only** — MCP servers connected | MCP view: 6 green dots (fetch, memory, sequential-thinking, git, demo-filesystem, demo) |
| **Act 4 only** — demo MCP server registered | `python scripts/demo_mcp_server.py` reachable; Prompts tab shows `summarize`, `code_review`, `brainstorm` |
| **Act 4 only** — memory MCP wiped | Delete the memory server's persisted graph file so first-run write is clean (or accept stale data as a feature: "look, it remembers from yesterday") |
| **Act 4 only** — fetch URL reachable | Test the URL the chain pulls (e.g. a public CHANGELOG) — internet on for this act, optional caveat to the "no egress" claim ("the *audit* runs offline; this encore demonstrates **opt-in** outbound MCP") |

### Fallback plan if a chain fails mid-demo

1. **Stay calm.** Exit Presenter (ESC), open Event Inspector (Ctrl+0 → Events),
   show the structured failure event with error code.
2. **Turn it into a talking point:** *"This is why we ship with structured
   error codes — the debugger knows exactly what broke. Cloud agents give
   you a vibe. We give you CWE IDs and SHA-256 hashes."*
3. **Retry the chain** — they're idempotent.
4. **Worst case** — pre-recorded video of a clean run, labelled "Demo
   fallback" on Desktop.

---

## Key Talking Points (memorise these)

1. **"Zero data egress. Zero."** Say it three times across the demo.
2. **"Cryptographic audit trail."** Every action. Hash-chained. SOC 2-ready.
3. **"Chain-to-chain composition."** Audits compose. Workflows compose.
4. **"Agents negotiate, learn reputations, auto-heal."** Not a chatbot.
5. **"MCP as a first-class citizen."** Any tool, any vendor, same plane.
6. **"125 MB installer. Zero prerequisites."** Desktop-first.
7. *(Act 4 only)* **"Operators remember. Chatbots don't."** Persistent
   knowledge graph across sessions, via the memory MCP server.
8. *(Act 4 only)* **"Vendors will ship prompts the way they ship APIs."**
   MCP prompt templates — invoked by chains, not by an LLM call.
7. **"Reversible by default."** Backups on overwrite. Approval gates. Rollback.

---

## What to Skip (stay disciplined)

- ❌ Don't show Settings. They want to see *doing*, not configuring.
- ❌ Don't explain the planner's heuristic routing. It's plumbing.
- ❌ Don't talk about the embedded Python distribution. Nobody cares.
- ❌ Don't list all 50+ chain templates. Show three. Ship the catalogue as
     a handout.
- ❌ Don't open any `.md` file on stage. Ever.

---

## Handout (post-talk)

Drop this on a USB / QR code:

- The three reports produced on stage (HTML files).
- `Docs/CHAIN_COMPOSITION_DEMOS.md` — deep-dive for engineers.
- `Docs/MULTI_AGENT_MANUAL.md` — how to build your own agents.
- `Docs/HETZNER_DEPLOYMENT_PROPOSAL.md` — for the customers who ask
  *"how do we run this for our team?"*.
- Binary installer (MSI / DEB / DMG).
