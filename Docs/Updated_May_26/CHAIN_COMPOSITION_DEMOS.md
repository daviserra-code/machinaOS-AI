# Chain-to-Chain Composition — Demo Use Cases

This document demonstrates the **chain-to-chain composition** feature
introduced in Sprint 64.  A workflow chain may include steps with
`step_type: "chain"` that invoke another saved chain as a sub-routine.
The runtime executes sub-chains recursively (max depth 5) with cycle
detection, so a single click can drive multi-stage, branded workflows
made of small, reusable building blocks.

There are two ways to build composite chains:

| Path | Where | When to use |
|---|---|---|
| **From a built-in template** | **Studio → Tmpl** tab *or* **Agents view → Workflow Chains panel → Use Template** | Fastest. Pick a `*-composite` or `master-*` template; sub-chains are auto-instantiated for you. |
| **From scratch in the Studio** | **Studio → Chains** palette tab | Most flexible. Drag any saved chain onto the canvas as a chain-type node. |

> **⚠ Naming note:** "Workflow Chains" refers to the pipeline chain panel
> inside the **Agents** view (multi-step agent pipelines).  It is **not**
> the same as the **Workflow Composer** view (5th nav tab), which is the
> DSL-based single-agent workflow editor.  The easiest way to avoid the
> confusion is to use **Studio → Tmpl** tab — that is where composite
> templates such as *Master Audit* are most discoverable.

Both use the same execution engine — `RuntimeExecutor.run_workflow_chain`
with `_chain_depth` and `_visited_chains` tracking.

---

## Use case 1 — *Master Audit*

**Persona:** Engineering lead before a release cut.

**Goal:** Run security, dependency, and code-quality checks together
and end up with a single audit note in `notes/`.

### Steps in the demo

1. Open **Studio** → palette **Tmpl** tab → pick **Master Audit (Composite)**
   and load it onto the canvas.
   *(Alt path: **Agents** view → **Workflow Chains** panel → **Use Template** button.)*
2. The bus auto-creates three sub-chains (`security-audit`,
   `dependency-check`, `code-quality-scan`) and wires their real IDs
   into the parent chain in one shot.
3. Click **Execute**.  Watch the live timeline — each sub-chain shows up
   as one parent step that fans out into N child steps.
4. The final step is `notes.create` — open `notes/` and read the saved
   "Master Audit" note that consolidates the run.

### Why it sells

- Demonstrates **inspectability**: each sub-chain is a real saved chain
  the user can re-run, edit, or roll back independently.
- Demonstrates **reuse**: the same `security-audit` chain that powers
  this composite can be run on its own from the Templates picker.
- Demonstrates **auditability**: the consolidated note is a permanent
  artifact under the workspace, not an ephemeral chat reply.

### Talking points

- "Notice the parent chain has 4 steps but execution shows ~14 — the
  three composite steps each expanded into a real sub-chain."
- "The note in `notes/Master Audit-...md` is indexed and searchable
  next time you ask 'what was in the last audit?'."

---

## Use case 2 — *Daily Ops Sweep*

**Persona:** SRE / on-call engineer at the start of a shift.

**Goal:** Confirm deploy readiness, profile system health, and scan
recent logs in a single button-press, with a note for the handover.

### Steps in the demo

1. Open **Studio** → palette **Tmpl** tab → pick **Daily Ops (Composite)**.
   *(Alt path: **Agents** view → **Workflow Chains** panel → **Use Template** button.)*
2. Sub-chains created: `deploy-check`, `performance-profile`,
   `log-investigation`.
3. Click **Execute** — runs end-to-end in seconds (all read-only system /
   filesystem tools).
4. Final note: `notes/Daily Ops Sweep-...md`.

### Why it sells

- Coworking-flavoured: the persona is operational, not developer-only.
- **No risky actions** — entire sweep is LOW-risk read-only, perfect
  for demo mode and reviewer mode without approval prompts.
- Result is a tangible artifact a human can hand to the next shift.

### Talking points

- "This is what 'pre-flight check' looks like when the OS understands
  intent — not a dashboard you stare at, a chain you can replay."
- "Add this to your shell startup or a cron via `POST /workflow-chains/{id}/execute`."

---

## Use case 3 — *Client Onboarding Pack*

**Persona:** Solo consultant handing a project to a new client team.

**Goal:** Produce a single, opinionated bundle of "everything a new
person needs" — README, structure, key configs, doc inventory.

### Steps in the demo

1. Open **Studio** → palette **Tmpl** tab → pick **Client Onboarding Pack (Composite)**.
   *(Alt path: **Agents** view → **Workflow Chains** panel → **Use Template** button.)*
2. Sub-chains created: `onboarding-scan`, `project-scan`,
   `documentation-audit`.
3. Execute — produces three sub-chain outputs plus a consolidated note.

### Why it sells

- Showcases composition as a **product surface**, not a developer tool:
  the user thinks "give me an onboarding pack", not "run these three
  chains in order".
- Demonstrates **chain-template ergonomics** — the bus resolves
  references at instantiation time, so the user never sees raw
  `chain_id` strings.

### Talking points

- "If the client wants a tweaked version, click **Studio** → drop in or
  remove a sub-chain → save under a new name. No code."
- "Chains are SQLite-persisted (`chains.db`) — they survive restarts
  and ship with the workspace."

---

## Use case 4 — *Weekly Coworking Cycle*

**Persona:** Knowledge worker / freelancer at end of week.

**Goal:** Wrap up the week (review + notes inventory) and prep
tomorrow's brief in a single chain.

### Steps in the demo

1. Open **Studio** → palette **Tmpl** tab → pick **Weekly Coworking Cycle (Composite)**.
   *(Alt path: **Agents** view → **Workflow Chains** panel → **Use Template** button.)*
2. Sub-chains created: `weekly-review`, `knowledge-sweep`, `morning-brief`.
3. Execute — three sub-chains in sequence, each producing its own note.

### Why it sells

- Pure coworking — zero developer tooling required.  Uses the new
  productivity tool surface (`notes.*`, `time.*`, `text.*`).
- Demonstrates Machina OS as **"second brain orchestrator"**, not
  just a code assistant.

### Talking points

- "This is what an AI-native OS looks like for non-engineers — the
  primitives are notes, time, and search, but the orchestration story
  is the same as for code."
- "Three notes appear in `notes/` after one click.  Open the notes view
  and watch them stack up."

---

## Use case 5 — *Build your own composite (live)*

**Persona:** Anyone curious enough to compose chains themselves.

**Goal:** Show that composition is not just for built-in templates.

### Steps in the demo

1. Open **Studio** → palette → **Chains** tab.
2. Drag **Code Review** into the canvas, then **Security Audit**, then
   **Project Scan** (each becomes a chain-type node).
3. Drop a `notes.create` tool node at the end and wire it.
4. Click **Save** as `My Pre-Commit Health Check`.
5. Click **Execute**.

### Why it sells

- Demonstrates the **Studio chain palette** (Sprint 64) end-to-end.
- Result is a user-owned chain that can itself be referenced by a
  future composite — the system is recursive.

---

## Engineering notes

### How template references resolve

`AgentBus.create_chain_from_template` (in [`core/agents/bus.py`](core/agents/bus.py))
is now recursive.  If a step in a template carries a `chain_template`
key, the bus:

1. Looks up the referenced template name.
2. Materialises it (recursively, with cycle detection via `_seen`).
3. Wires the new sub-chain's real `chain_id` into the parent step.
4. Stores both parent and children in `chains.db`.

If a referenced template is missing (e.g. a future template was renamed
without updating callers) the parent step degrades to a benign
`system.status` no-op so the parent chain remains valid.

### Recursion limits

`RuntimeExecutor.run_workflow_chain` enforces:

- `MAX_CHAIN_DEPTH = 5` — composite chains 5 deep are fine; deeper
  raises a structured error.
- `_visited_chains` set — prevents A→B→A cycles even across templates.

### Persistence

Every sub-chain materialised by a composite template is saved to
`chains.db` as a first-class chain.  This means:

- Users can re-run any sub-chain on its own.
- Chains can be edited or rolled back independently of the parent.
- Deleting the parent does **not** cascade-delete sub-chains.

### Recommended demo order

1. *Master Audit* — wow factor, multi-tool fan-out.
2. *Daily Ops Sweep* — show coworking persona shift.
3. *Build your own* — invite the audience to compose.
4. *Client Onboarding* — close on the consulting / ops story.
