# MachinaOS MCP Manual

> A scripted walkthrough for every MCP capability in Machina OS.
> MachinaOS operates in a **dual role**: it is simultaneously an **MCP client** (consuming external servers such as memory, fetch, and sequential-thinking) and an **MCP server/provider** (exposing all its tools, resources, and prompts to external clients like Claude Desktop and Cursor).
> Each act exercises one capability end-to-end. Acts 1–7 cover the client role. Acts 8–12 cover the provider role. Acts 13–15 are integration and end-to-end scenarios.

---

## Prerequisites

```bash
# 1. Start MachinaOS
cd machina-os
python -m uvicorn apps.api.server:app --host 127.0.0.1 --port 8100

# 2. Open the UI
#    Navigate to http://127.0.0.1:8100
#    MCP view is the last nav item (or press Ctrl+K → type "mcp")

# 3. Node.js / npx required for default MCP servers (stdio transport)
#    Verify: npx --version
#    macOS/Linux: brew install node   |   Windows: winget install OpenJS.NodeJS

# 4. (Optional) GitHub MCP server — set env var before starting:
#    export GITHUB_PERSONAL_ACCESS_TOKEN=ghp_...

# 5. (Optional) SQLite MCP server — requires a --db-path argument in the form
```

---

## System Overview

| Metric | Value |
|--------|-------|
| MCP API Endpoints | 15 |
| Default MCP Servers | 5 (3 auto-connect on startup) |
| Bridge Classes | 3 — MCPToolBridge, MCPResourceBridge, MCPPromptBridge |
| Protocol Version | `2024-11-05` (JSON-RPC 2.0) |
| Builtin MCP Agent | `agent_mcp` (tool_filter: `mcp.*`) |
| Native Tools Exposed (Provider) | 52 |
| Virtual Tools (Provider) | 4 — `machina.create_task`, `machina.get_task`, `machina.list_tasks`, `machina.chat` |
| Resources (Provider) | 17 across 7 domains |
| Prompt Templates (Provider) | 4 — `plan_task`, `analyze_code`, `scrub_credentials`, `explain_error` |
| MCP UI Sub-Tabs | 4 — Server Registry, Discovered Tools, Resources, Prompts |

---

## Architecture at a Glance

```
┌──────────────────────── MachinaOS ────────────────────────────┐
│                                                               │
│   MCP CLIENT role                  MCP SERVER role            │
│   ─────────────────────────        ───────────────────────    │
│   MCPClient (stdio / SSE)          MCPServer (SSE transport)  │
│   MCPToolBridge   → tool registry  GET  /mcp/serve/sse        │
│   MCPResourceBridge → resources    POST /mcp/serve/messages   │
│   MCPPromptBridge   → prompts      GET  /mcp/serve/status     │
│   MCPServerRegistry (SQLite)                                  │
│                                                               │
│   External servers ◄───────────  ──────────► External clients │
│   (npx stdio, SSE)                           (Claude Desktop, │
│                                               Cursor, etc.)   │
└───────────────────────────────────────────────────────────────┘
```

---

## Act 1 — Boot Check: Default Servers Auto-Connect

**Goal:** Confirm the five pre-bundled MCP servers are in the registry and the three auto-connecting ones are live at startup.

MachinaOS ships with five server configs baked in. Three (`sequential-thinking`, `memory`, `fetch`) connect automatically on startup — no action needed. The other two (`github`, `sqlite`) require credentials or arguments before enabling.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 1.1 | Open `http://127.0.0.1:8100` and click **MCP** in the nav | Browser | MCP view loads with four sub-tabs: Server Registry, Discovered Tools, Resources, Prompts. |
| 1.2 | Open **Server Registry** tab | MCP view | Five server cards listed. Three show a green status dot (sequential-thinking, memory, fetch). Two show grey (github, sqlite). |
| 1.3 | Open **Discovered Tools** tab | MCP view | Tool cards populated from the three auto-connected servers. Names follow the `mcp.<server>.<tool>` pattern. |
| 1.4 | Restart MachinaOS and re-open the MCP view | Browser | Still exactly **5 servers** — no duplicates. The `mcp_defaults_seeded` preference flag prevents re-seeding. |
| 1.5 | Check the startup log in the terminal | Terminal | Lines for `_auto_connect_mcp_servers()` confirming sequential-thinking, memory, and fetch connected. |

**Default server reference:**

| Server | Auto-Connect | Requires |
|--------|-------------|---------|
| sequential-thinking | ✅ Yes | `npx` in PATH |
| memory | ✅ Yes | `npx` in PATH |
| fetch | ✅ Yes | `npx` in PATH |
| github | ❌ No | `GITHUB_PERSONAL_ACCESS_TOKEN` env var |
| sqlite | ❌ No | `--db-path` argument |

```bash
# API equivalent — verify from terminal
curl http://127.0.0.1:8100/mcp/servers       # 5 entries
curl http://127.0.0.1:8100/mcp/tools         # tools from auto-connected servers
```

**Pass criteria:** 5 servers in registry. 3 green dots. No duplicates on restart. Discovered Tools tab populated.

---

## Act 2 — Server Registry: Register, Connect, Remove

**Goal:** Register a custom MCP server, connect it, confirm tool discovery, then clean up.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 2.1 | In **Server Registry** click **Register new server** | MCP view | A form expands with fields: Name, Transport, Command, Args, Env, URL, Auto-Connect. |
| 2.2 | Fill in: Name = `demo-filesystem`, Transport = `stdio`, Command = `npx`, Args = `-y @modelcontextprotocol/server-filesystem ./` | Form | Form ready to submit. |
| 2.3 | Click **Register** | Form | New server card appears. Status dot is grey. Config saved to SQLite — survives restart. |
| 2.4 | Click **Connect** on the new card | Server card | MachinaOS spawns the npx subprocess, runs the MCP handshake, discovers tools. Dot turns green. |
| 2.5 | Switch to **Discovered Tools** tab | MCP view | New tools appear: `mcp.demo-filesystem.list_directory`, `mcp.demo-filesystem.read_file`, etc. |
| 2.6 | Switch back to **Server Registry**, click **Disconnect** | Server card | Dot turns grey. The `mcp.demo-filesystem.*` tools disappear from Discovered Tools. |
| 2.7 | Click **Delete** on the card | Server card | Card removed. Registry returns to 5 servers. |

> **Quick Pick panel:** The MCP view includes a curated list of 14 known `npx` packages. Type a package name in the form — it auto-highlights and fills the command, args, and env fields.

**Server config fields:**

| Field | Notes |
|-------|-------|
| `name` | Display name — also used to derive `server_id` |
| `transport` | `"stdio"` or `"sse"` |
| `command` | Executable: `npx`, `python`, etc. (stdio only) |
| `args` | Command arguments as space-separated string |
| `env` | Environment variables for the subprocess |
| `url` | HTTP endpoint (SSE transport only) |
| `auto_connect` | Connect automatically on MachinaOS startup |

```bash
# API equivalent — register via terminal
curl -X POST http://127.0.0.1:8100/mcp/servers \
  -H "Content-Type: application/json" \
  -d '{"name":"demo-filesystem","transport":"stdio","command":"npx","args":["-y","@modelcontextprotocol/server-filesystem","./"]}'
curl -X POST http://127.0.0.1:8100/mcp/servers/demo-filesystem/connect
curl -X DELETE http://127.0.0.1:8100/mcp/servers/demo-filesystem
```

**Pass criteria:** Server registered and persisted. Connect discovers tools. Disconnect removes tools. Delete clears config. Registry back to 5.

---

## Act 3 — MCP Tool Bridge: Invoke via Neural Link

**Goal:** Confirm that MCP-bridged tools are callable from the Neural Link chat interface.

When MachinaOS connects to a server, `MCPToolBridge` converts every tool it finds into a Machina `ToolSpec` with the `mcp.<server>.<tool>` name. These tools become first-class citizens — they appear in the Tools view, the Discovered Tools tab, and respond to Neural Link input.

> **Prerequisite:** The `fetch` server must be connected (green dot in Server Registry). Complete Acts 1–2 first, or click **Connect** on the `fetch` card now.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 3.1 | Type `mcp.fetch.fetch url=https://example.com` in Neural Link | Chat | Plan card: one step, tool = `mcp.fetch.fetch`, arguments = `{"url": "https://example.com"}`, **approval gate** appears. No LLM spinner. |
| 3.1b | Type `fetch https://example.com` in plain English | Chat | URL + keyword detected → same plan card, routed to `mcp.fetch.fetch_txt url=https://example.com` automatically. No dot-notation required. |
| 3.1c | Type `get content of github.com/trending` | Chat | URL detected → plan with `mcp.fetch.fetch_txt url=https://github.com/trending`. |
| 3.2 | Click **Approve** on any of the above | Chat plan card | Tool executes → result shown in the step row **and** as a result bubble in the chat stream. Step icon turns green via WebSocket. |
| 3.3 | Type `mcp.memory.create_entities` | Chat | Plan card with the memory server tool. Approval gate. |
| 3.4 | Open **Tools** view (Ctrl+3) | Nav | All `mcp.*` tools appear with MEDIUM risk badge alongside native tools. |
| 3.5 | Click any MCP tool card | Tools view | Tool name inserted into Neural Link — same as clicking any native tool. |
| 3.6 | Disconnect the `fetch` server (MCP view), then type `mcp.fetch.fetch url=https://example.com` | Chat | Plan card appears (routing works regardless), but step fails with **MCP_SERVER_NOT_CONNECTED** — the error message tells you to connect the server first. Reconnect → retry → succeeds. |

> **Why approval?** All MCP tools have `risk_level = MEDIUM` and `requires_approval = true`. This is intentional — MCP tools reach external subprocesses and deserve an explicit sign-off before execution.

> **Live result display:** After approval and execution, the plan card step icon turns green automatically (WebSocket `tool_finished` event) and the result appears both inside the step row and as a standalone result bubble in the chat stream.

> **Natural language shortcut:** If your input contains an HTTP/HTTPS URL and any keyword like `fetch`, `get content`, `download`, or `open url`, MachinaOS auto-routes to `mcp.fetch.fetch_txt` without requiring dot-notation syntax.

**Tool naming pattern:**
```
mcp.<server_name>.<tool_name>

Examples:
  mcp.sequential-thinking.sequentialthinking
  mcp.memory.create_entities
  mcp.fetch.fetch
  mcp.github.create_issue
```

```bash
# See all bridged tools with full metadata
curl http://127.0.0.1:8100/mcp/tools
```

**Pass criteria:** MCP tools callable from Neural Link. Approval gate fires. Tools appear/disappear on connect/disconnect. Risk level = MEDIUM on all.

---

## Act 4 — MCP Resource Bridge

**Goal:** Discover and read resources from connected external MCP servers.

MCP resources are read-only data feeds published by a server. The `/mcp/resources` endpoint queries every connected server's `resources/list` capability. Servers that don't implement the resources capability (most official servers fall in this category) are filtered out of the result list and surfaced separately under `servers_without_resources` so the UI can explain *why* the list is empty rather than rendering ghost cards.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 4.1 | Open **MCP** view → **Resources** sub-tab | MCP view | Resource cards grouped by server. Each shows name, URI, MIME type, description, and a **Read** button. |
| 4.2 | Click **Discover** | Resources tab | Refreshes from all connected servers. Cards have a `_server` attribution badge. |
| 4.3 | Click **Read** on any resource card | Resources tab | Content expands inline in the preview panel below — text, JSON, or structured data depending on the server. |
| 4.4 | If empty | Resources tab | Empty-state card lists every server that was checked + the reason each lacks resources (e.g. `fetch: MCP error -32601: Method not found`). |
| 4.5 | Disconnect a server, then click **Discover** | Resources tab | Resources from that server vanish from the list. |

```bash
# API equivalents
curl http://127.0.0.1:8100/mcp/resources
# Returns:
#   { "by_server": { "demo": [...] },
#     "resources": [...flat list with _server field...],
#     "count": 3,
#     "checked_servers": ["fetch","memory","demo",...],
#     "servers_without_resources": [
#       {"server":"fetch","reason":"MCP error -32601: Method not found"} ] }

curl -X POST http://127.0.0.1:8100/mcp/resources/read \
  -H "Content-Type: application/json" \
  -d '{"server":"demo","uri":"demo://about"}'
```

**Pass criteria:** Resources from servers that publish them appear as cards. Read returns content inline. Empty state names the checked servers and the reason for each. Disconnecting removes resources.

> **Heads-up:** None of the official `@modelcontextprotocol/server-*` packages (fetch, memory, sequential-thinking, filesystem, git) currently implement `resources/list`. To verify this tab end-to-end, register the bundled demo server (see Act 5b below) which publishes 3 demo resources.

---

## Act 5 — MCP Prompt Bridge

**Goal:** Discover and resolve prompt templates from connected external MCP servers.

MCP prompts are parameterised text templates published by a server. MachinaOS discovers them and makes them resolvable from the UI — click a prompt card, fill in the arguments, get back the resolved text. Same filtering pattern as Act 4: servers that don't implement `prompts/list` are excluded and reported under `servers_without_prompts`.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 5.1 | Open **MCP** view → **Prompts** sub-tab | MCP view | Prompt cards with name, description, server badge, and per-argument input fields (asterisk on required ones). |
| 5.2 | Fill in the required arguments | Prompts tab | Optional arguments can be left blank — required ones are flagged with `(required)` placeholder text. |
| 5.3 | Click **Resolve** | Prompts tab | Resolved prompt text returned by the server appears inline as JSON in the card's result panel. |
| 5.4 | Click **Discover** to refresh | Prompts tab | Prompt list updates from all connected servers. |
| 5.5 | If empty | Prompts tab | Empty-state card lists every checked server + the reason each lacks prompts. Suggests installing a server that publishes them. |

```bash
# API equivalents
curl http://127.0.0.1:8100/mcp/prompts
curl http://127.0.0.1:8100/mcp/prompts/flat
# Same shape as /mcp/resources — includes checked_servers + servers_without_prompts

curl -X POST http://127.0.0.1:8100/mcp/prompts/get \
  -H "Content-Type: application/json" \
  -d '{"server":"demo","name":"summarize","arguments":{"text":"Hello world"}}'
```

**Pass criteria:** Prompts from publishing servers appear with typed argument inputs. Resolve returns substituted text inline. Empty state explains why each server lacks prompts.

---

## Act 5b — Demo MCP Server (Reference Implementation)

**Goal:** Verify the Resources and Prompts tabs end-to-end with a known-good server, and have a tiny reference for building your own.

The repo ships [scripts/demo_mcp_server.py](../scripts/demo_mcp_server.py) — a single-file (~220 lines, stdlib only) MCP 2024-11-05 server that implements all three capabilities: 2 tools (`echo`, `ping`), 3 resources (`demo://about`, `demo://tips`, `demo://changelog`), 3 prompts (`summarize`, `code_review`, `brainstorm`).

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 5b.1 | Register via UI: **MCP → Servers → Add Server** with command `python` and args `["<repo>/scripts/demo_mcp_server.py"]`, then click **Connect** | MCP view | Server appears as `demo` with green dot, 2 tools registered (`mcp.demo.echo`, `mcp.demo.ping`). |
| 5b.2 | Open **Prompts** tab | MCP view | 3 cards: `summarize`, `code_review`, `brainstorm` — each with typed argument inputs. |
| 5b.3 | Fill `text=Hello world` on `summarize` and click **Resolve** | Prompts tab | Result panel shows the templated prompt with substituted text. |
| 5b.4 | Open **Resources** tab → click **Read** on `demo://tips` | MCP view | Markdown content displays inline in the preview panel. |
| 5b.5 | Open **Tools** tab | MCP view | `mcp.demo.echo` and `mcp.demo.ping` listed; invoke `mcp.demo.echo text=hi` from chat to verify tool execution. |

```bash
# API one-liner registration
curl -X POST http://127.0.0.1:8100/mcp/servers \
  -H "Content-Type: application/json" \
  -d '{"name":"demo","transport":"stdio","command":"python","args":["scripts/demo_mcp_server.py"],"enabled":true,"auto_connect":true}'
curl -X POST http://127.0.0.1:8100/mcp/servers/mcp_demo/connect
```

**Pass criteria:** Demo server connects. All three sub-tabs (Tools, Resources, Prompts) populate. Resolve and Read both return live content. The script doubles as a reference for building your own MCP servers.

---

## Act 6 — MCP-Aware Planner: Intent Routing

**Goal:** Confirm that typing an MCP tool name in Neural Link produces a deterministic plan with no LLM involved.

The intake module has a dedicated MCP detection path. When input contains a dot-notation token starting with `mcp.` that matches a registered tool, it routes to the `mcp_tool` intent and `_plan_mcp_tool()` builds the plan instantly — no LLM call, no delay.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 6.1 | Type `mcp.memory.create_entities` | Chat | Plan card appears immediately — no spinner, no delay. One step, `requires_approval: true`. |
| 6.2 | Type `mcp.fetch.fetch` | Chat | Same — instant plan, one step, approval gate. |
| 6.3 | Type `use sequential-thinking` | Chat | Server name detected in the input → routes to `mcp_tool` → plan card with the sequential-thinking tool. |
| 6.4 | Type `use the memory server` | Chat | Server name detected → plan card with the first memory tool found. |
| 6.5 | Type `fetch https://ai-radar.tech` (plain English) | Chat | URL + fetch keyword detected → routes to `mcp_tool` → plan with `mcp.fetch.fetch_txt url=https://ai-radar.tech`. No dot-notation, no LLM call. |
| 6.6 | Approve and execute any of the above | Chat | Tool runs via MCPClient.call_tool() → result shown in the plan card step row **and** as a chat bubble. Step icon turns green via WebSocket update. |
| 6.7 | Check **Timeline** after execution | Timeline | `mcp_tool` intent recorded. `tool_started` and `tool_finished` events visible. |

> **What this means:** You never need to remember endpoint syntax. Just type the tool name, describe the server, or paste a URL with a fetch keyword — MachinaOS routes it without touching the LLM.

```bash
# API equivalent — same routing, no LLM
curl -X POST http://127.0.0.1:8100/run \
  -H "Content-Type: application/json" \
  -d '{"input":"mcp.fetch.fetch"}'
```

**Pass criteria:** Plan appears instantly. No LLM latency. Intent = `mcp_tool`. Tool runs on approval. Timeline records the event.

---

## Act 7 — MCP Builtin Agent

**Goal:** Confirm the `agent_mcp` agent owns the `mcp.*` namespace and delegation routes correctly.

MachinaOS ships with six builtin agents. `agent_mcp` owns every MCP tool — its `tool_filter` is `["mcp.*"]`. All MCP tool calls route through it.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 7.1 | Click **Agents** (Ctrl+7) | Nav | Agent fleet list. Find the card labelled **mcp**. |
| 7.2 | Inspect the `agent_mcp` card | Agents view | `capabilities: ["mcp", "mcp_tool"]`, `tool_filter: ["mcp.*"]`, `enabled: true`. |
| 7.3 | Type `delegate to agent_mcp mcp.fetch.fetch` | Chat | Plan: delegate step pointing at `agent_mcp`, tool = `mcp.fetch.fetch`, approval gate. |
| 7.4 | Check **System Status Bar** | Bottom bar | Online count includes `agent_mcp`. |
| 7.5 | Check **Agents → Fleet** summary | Agents view | `total` count includes the MCP agent. |

```bash
curl http://127.0.0.1:8100/agents          # spot agent_mcp in array
curl http://127.0.0.1:8100/agents/summary  # fleet health counts
```

**Pass criteria:** `agent_mcp` in pool. `tool_filter = ["mcp.*"]`. Delegation routes to it. Summary count correct.

---

## Act 8 — MachinaOS as MCP Provider: Opening a Session

**Goal:** Open an SSE stream from MachinaOS (its provider role) and complete the MCP handshake.

> **This act and Acts 9–12 require two terminal windows side-by-side.** MachinaOS becomes the server; your terminals act as an external MCP client.

The provider uses Server-Sent Events: the client opens a long-lived GET stream and sends JSON-RPC requests to a POST endpoint. All responses arrive back on the stream.

**Step 1 — Check provider status (no session needed):**

```bash
curl http://127.0.0.1:8100/mcp/serve/status
# → {"sessions": 0, "tools": 56, "resources": 17, "prompts": 4}
```

**Step 2 — Terminal 1: open the SSE stream:**

```bash
curl -N http://127.0.0.1:8100/mcp/serve/sse
# First event:  {"session_id": "mcp_abc123def456"}
# Keepalive every 30 s: {"keepalive": true}
```

Copy the `session_id` value.

**Step 3 — Terminal 2: initialize the session:**

```bash
SESSION_ID="mcp_abc123def456"   # paste your actual value here

curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0", "id": 1, "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "my-client", "version": "1.0"}
    }
  }'
```

Watch Terminal 1 — the response arrives on the stream:

```json
{
  "jsonrpc": "2.0", "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
    "serverInfo": {"name": "machina-os", "version": "0.2.0"}
  }
}
```

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 8.1 | `GET /mcp/serve/status` | Terminal | sessions=0, tools=56, resources=17, prompts=4. |
| 8.2 | Open SSE stream | Terminal 1 | First event contains `session_id`. Keepalives every 30 s. |
| 8.3 | Send `initialize` | Terminal 2 | Response on Terminal 1 — server name = `machina-os`, protocol = `2024-11-05`. |
| 8.4 | Re-check status | Terminal | `sessions: 1` — your open stream is counted. |

**Pass criteria:** SSE returns `session_id`. Initialize response includes `machina-os` server name. Status shows 1 active session.

---

## Act 9 — Provider: Calling Native Tools

**Goal:** Call Machina's native tools through the MCP provider as an external client would.

All 52 native tools are exposed. The `mcp.*` prefix tools are excluded to prevent recursion. Each tool's `inputSchema` is derived from its `ToolSpec.params`. **All responses arrive in Terminal 1 (the SSE stream).**

```bash
SESSION_ID="mcp_..."   # from Act 8

# List all 56 tools (52 native + 4 virtual) — watch Terminal 1 for response
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":10,"method":"tools/list","params":{}}'

# Call filesystem.list
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":11,"method":"tools/call","params":{"name":"filesystem.list","arguments":{"path":"."}}}'

# Call git.status
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":12,"method":"tools/call","params":{"name":"git.status","arguments":{}}}'

# Call system.info
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":13,"method":"tools/call","params":{"name":"system.info","arguments":{}}}'
```

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 9.1 | Send `tools/list` | Terminal 2 | 56 tools on Terminal 1 SSE stream — no `mcp.*` in the list. |
| 9.2 | Call `filesystem.list` | Terminal 2 | Directory listing arrives on Terminal 1. |
| 9.3 | Call `git.status` | Terminal 2 | Branch name + clean/dirty status on Terminal 1. |
| 9.4 | Call `system.info` | Terminal 2 | OS, hostname, CPU count, Python version on Terminal 1. |

**Tool categories exposed:**

| Category | Count | Examples |
|----------|-------|---------|
| filesystem | 11 | list, read_file, write_file, tree, grep, copy, mkdir |
| git | 13 | status, log, diff, branch, commit, push, pull, tag, merge |
| system | 5 | status, info, memory, disk, env |
| process | 4 | list, info, start, stop |
| shell | 2 | run, run_safe |
| vscode | 7 | open_workspace, diff, read_diagnostics… |
| Virtual | 4 | machina.create_task, get_task, list_tasks, chat |

**Pass criteria:** 56 tools listed. No `mcp.*` in provider tools. All three tool calls return correct results on the SSE stream.

---

## Act 10 — Provider: Virtual Tools

**Goal:** Use the four MachinaOS-specific virtual tools — the bridge between an external MCP client and Machina's task engine.

These tools exist only in the provider interface. They let external clients (Claude Desktop, Cursor) create and monitor Machina tasks and send chat messages as if they were inside Neural Link.

```bash
SESSION_ID="mcp_..."

# Create a task from natural language (same as typing in Neural Link)
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":20,"method":"tools/call","params":{"name":"machina.create_task","arguments":{"goal":"list files in current directory"}}}'
# Terminal 1: {"task_id": "task_abc123", "status": "completed", ...}

# Check task status
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":21,"method":"tools/call","params":{"name":"machina.get_task","arguments":{"task_id":"task_abc123"}}}'

# List recent tasks
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":22,"method":"tools/call","params":{"name":"machina.list_tasks","arguments":{"limit":5}}}'

# Send a chat message
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":23,"method":"tools/call","params":{"name":"machina.chat","arguments":{"message":"What is MachinaOS?"}}}'
```

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 10.1 | Call `machina.create_task` | Terminal 2 | `task_id` on Terminal 1 SSE stream. Task runs inside MachinaOS. |
| 10.2 | Call `machina.get_task` | Terminal 2 | Status, step list, result data on Terminal 1. |
| 10.3 | Check **Timeline** in the browser | Browser | The task created externally appears in the task history. |
| 10.4 | Call `machina.chat` | Terminal 2 | Conversational reply on Terminal 1. |

**Pass criteria:** All 4 virtual tools in `tools/list`. `create_task` returns `task_id`. Task appears in UI Timeline. `chat` returns text.

---

## Act 11 — Provider: Reading Resources

**Goal:** Read live MachinaOS system state through the MCP resource interface.

MachinaOS exposes 17 resources across 7 domains. All use the `machina://` URI scheme. Resources are the cleanest way for an external client to inspect the running system without building any custom API calls.

```bash
SESSION_ID="mcp_..."

# List all 17 resources
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":30,"method":"resources/list","params":{}}'

# Workspace: detected languages
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":31,"method":"resources/read","params":{"uri":"machina://workspace/languages"}}'

# Agent fleet summary
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":32,"method":"resources/read","params":{"uri":"machina://agents/summary"}}'

# Last 50 system events
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":33,"method":"resources/read","params":{"uri":"machina://events/recent"}}'
```

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 11.1 | Send `resources/list` | Terminal 2 | 17 resources on Terminal 1 with URIs, names, descriptions. |
| 11.2 | Read `machina://workspace/languages` | Terminal 2 | Language list (Python, JavaScript, …) on Terminal 1. |
| 11.3 | Read `machina://agents/summary` | Terminal 2 | Fleet counts — online / degraded / offline, top performer. |
| 11.4 | Read `machina://events/recent` | Terminal 2 | JSON array of up to 50 recent events. |
| 11.5 | Read `machina://tasks/active` | Terminal 2 | Currently running or pending tasks. |

**Complete resource catalog:**

| Domain | URIs |
|--------|------|
| Workspace | `machina://workspace/languages`, `/frameworks`, `/tree`, `/key-files`, `/info` |
| Memory | `machina://memory/session`, `/task`, `/project`, `/preferences` |
| Events | `machina://events/recent`, `/types` |
| Security | `machina://security/audit/summary` |
| Agents | `machina://agents/summary`, `/list` |
| Tasks | `machina://tasks/active`, `/recent` |
| Telemetry | `machina://telemetry/summary` |

**Pass criteria:** 17 resources listed. Each `resources/read` returns structured content. All 7 domains represented.

---

## Act 12 — Provider: Prompt Templates

**Goal:** List and resolve the four prompt templates MachinaOS exposes to external clients.

These prompts call live MachinaOS services on resolution — `plan_task` calls the planner, `analyze_code` runs the security analyzer, `scrub_credentials` calls the scrubber with its 20+ regex patterns.

```bash
SESSION_ID="mcp_..."

# List all 4 prompts
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":40,"method":"prompts/list","params":{}}'

# plan_task — generate a structured execution plan
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":41,"method":"prompts/get","params":{"name":"plan_task","arguments":{"goal":"check git status and list Python files"}}}'

# analyze_code — 14-pattern security scan with CWE IDs
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":42,"method":"prompts/get","params":{"name":"analyze_code","arguments":{"code":"query = \"SELECT * FROM users WHERE id=\" + user_input","language":"python"}}}'

# scrub_credentials — redact API keys and tokens (20+ patterns)
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":43,"method":"prompts/get","params":{"name":"scrub_credentials","arguments":{"text":"api_key=sk-proj-abc123 token=ghp_myToken"}}}'

# explain_error — cause hints for an error message
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":44,"method":"prompts/get","params":{"name":"explain_error","arguments":{"error":"ConnectionRefusedError","context":"connecting to Ollama"}}}'
```

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 12.1 | Send `prompts/list` | Terminal 2 | 4 prompts on Terminal 1 — names, descriptions, argument schemas. |
| 12.2 | Resolve `plan_task` | Terminal 2 | Structured plan with step list on Terminal 1. |
| 12.3 | Resolve `analyze_code` (SQL injection example) | Terminal 2 | Finding: SQL injection, CWE-89, HIGH severity. |
| 12.4 | Resolve `scrub_credentials` | Terminal 2 | `sk-proj-abc123` → `***REDACTED***`. |
| 12.5 | Resolve `explain_error` | Terminal 2 | Explanation hints for `ConnectionRefusedError`. |

**Prompt reference:**

| Name | Calls | Required args |
|------|-------|---------------|
| `plan_task` | Planner | `goal` |
| `analyze_code` | SecurityAnalyzer | `code`, `language` |
| `scrub_credentials` | CredentialScrubber | `text` |
| `explain_error` | LLM / fallback | `error` |

**Pass criteria:** 4 prompts listed. `plan_task` returns steps. `analyze_code` detects SQL injection (CWE-89). `scrub_credentials` redacts secrets. `explain_error` provides hints.

---

## Act 13 — Connect Claude Desktop or Cursor

**Goal:** Point Claude Desktop or Cursor at MachinaOS so they gain access to all 56 tools, 17 resources, and 4 prompts.

### Claude Desktop (Windows)

Open `%APPDATA%\Claude\claude_desktop_config.json` and add:

```json
{
  "mcpServers": {
    "machina-os": {
      "url": "http://127.0.0.1:8100/mcp/serve/sse",
      "transport": "sse"
    }
  }
}
```

### Claude Desktop (macOS / Linux)

File: `~/Library/Application Support/Claude/claude_desktop_config.json` — same JSON content.

### Cursor

Add to Cursor's MCP settings the same `url` and `transport` values.

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 13.1 | Edit the config file and restart Claude Desktop | Desktop | MCP server entry appears. Tools, resources, prompts visible in Claude's tool list. |
| 13.2 | Ask Claude: *"list files in my project"* | Claude | Claude calls `filesystem.list` via MCP → directory listing from MachinaOS. |
| 13.3 | Ask Claude: *"create a task: check git status"* | Claude | Claude calls `machina.create_task` → MachinaOS runs `git.status`, result returned. |
| 13.4 | Ask Claude: *"what workspace am I in?"* | Claude | Claude reads `machina://workspace/info` → languages, frameworks, key files. |
| 13.5 | Ask Claude: *"scrub this: key=sk-abc123"* | Claude | Claude calls `scrub_credentials` → `***REDACTED***` returned. |
| 13.6 | Check provider status | Terminal | `sessions: 1`, `tools: 56`, `resources: 17`, `prompts: 4`. |

**Pass criteria:** External client connects. Tools, resources, prompts visible in Claude. Tool calls execute in MachinaOS and results return to Claude.

---

## Act 14 — MCP UI: All Four Sub-Tabs

**Goal:** Walk through every MCP sub-tab in the UI without touching the terminal.

Navigate to **MCP** in the nav bar (or press Ctrl+K → type `mcp`).

### Sub-Tab 1 — Server Registry

| # | Action | Expected Result |
|---|--------|-----------------|
| 14.1 | Open MCP → **Servers** | 5 server cards. Green dots for auto-connected, grey for disconnected. |
| 14.2 | Click **Connect** on `fetch` | Dot turns green. `mcp.fetch.*` tools appear in Discovered Tools. |
| 14.3 | Click **Disconnect** | Dot turns grey. Tools disappear. |
| 14.4 | Type a known npx package name in the Register form | Quick Pick panel highlights the match and auto-fills command, args, and env fields. |
| 14.5 | Register a server and **Delete** it | Card added then removed. Registry returns to the correct count. |

### Sub-Tab 2 — Discovered Tools

| # | Action | Expected Result |
|---|--------|-----------------|
| 14.6 | Open MCP → **Discovered Tools** | Grid of MCP-bridged tool cards. Name, description, risk badge, server source. A "Use MCP Tools in Plain English" guide card appears above the grid with clickable example prompts. |
| 14.7 | Click **Use** on a tool card | Tool name (or a smart prompt like `fetch https://example.com`) prefilled in Neural Link and Chat view focused. |
| 14.8 | Click an example in the NL guide card (e.g. *fetch https://ai-radar.tech*) | Chat view opens with that text prefilled ready to send. |

### Sub-Tab 3 — Resources

| # | Action | Expected Result |
|---|--------|-----------------|
| 14.8 | Open MCP → **Resources**, click **Discover** | Resources listed grouped by server with attribution badges. |
| 14.9 | Click **Read** on any resource | Content expands inline below the card. |

### Sub-Tab 4 — Prompts

| # | Action | Expected Result |
|---|--------|-----------------|
| 14.10 | Open MCP → **Prompts** | Prompt cards with name, description, argument badge list. |
| 14.11 | Click a prompt, fill in arguments, click **Resolve** | Resolved text appears below the form. |

**Pass criteria:** All 4 sub-tabs load. Server CRUD works. Quick Pick auto-fills. Tools click-to-chat. Resources readable inline. Prompts resolvable.

---

## Act 15 — End-to-End: Full MCP Round-Trip

**Scenario:** Audit a file for credentials, run a task, and receive the result — using both the UI (client role) and a terminal pair (provider role).

### Phase A — MachinaOS as Client (UI-only)

| # | Action | Where | Expected Result |
|---|--------|-------|-----------------|
| 15.1 | Open **MCP** → **Servers** | Browser | 5 servers. `memory` and `fetch` are green. |
| 15.2 | Type `mcp.fetch.fetch` in Neural Link | Chat | Instant plan card — no LLM delay. Approve → result from external server displayed. |
| 15.3 | Check **Timeline** | Timeline | `mcp_tool` intent recorded. `tool_started` and `tool_finished` events visible. |
| 15.4 | Open **MCP** → **Resources** → **Discover**, then **Read** `machina://workspace/info` | MCP view | Workspace languages, frameworks, and key files displayed inline. |

### Phase B — MachinaOS as Provider (two terminals)

```bash
# Terminal 1: open SSE stream
curl -N http://127.0.0.1:8100/mcp/serve/sse
# → copy session_id from first event

# Terminal 2: complete the round-trip
SESSION_ID="mcp_..."

# 1. Initialize
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"e2e","version":"1.0"}}}'

# 2. Scrub credentials via prompt
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"prompts/get","params":{"name":"scrub_credentials","arguments":{"text":"api_key=sk-proj-abc123def456 secret=myPassword123"}}}'

# 3. Create a task — runs inside MachinaOS
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"machina.create_task","arguments":{"goal":"check git status"}}}'

# 4. Read workspace info
curl -X POST "http://127.0.0.1:8100/mcp/serve/messages?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":4,"method":"resources/read","params":{"uri":"machina://workspace/info"}}'

# Terminal 1: Ctrl+C to close — session cleaned up automatically
```

| Step | Expected on Terminal 1 |
|------|----------------------|
| Initialize | `machina-os` server name, protocol `2024-11-05` |
| `scrub_credentials` | `sk-proj-abc123def456` → `***REDACTED***` |
| `machina.create_task` | `task_id` returned; task appears in UI Timeline |
| `resources/read` | Workspace languages, frameworks, key files |

**Pass criteria:** Both phases complete without errors. Client phase is UI-only. Provider phase: SSE, initialize, prompt, task, resource — all succeed.

---

## Quick Smoke Test

Run after startup to verify every MCP subsystem in under 30 seconds:

```powershell
$mcp = Invoke-RestMethod http://127.0.0.1:8100/mcp/servers
Write-Host "OK: MCP servers = $($mcp.Count)"

$mcpTools = Invoke-RestMethod http://127.0.0.1:8100/mcp/tools
Write-Host "OK: MCP bridged tools = $($mcpTools.Count)"

$mcpServe = Invoke-RestMethod http://127.0.0.1:8100/mcp/serve/status
Write-Host "OK: Provider — tools=$($mcpServe.tools) resources=$($mcpServe.resources) prompts=$($mcpServe.prompts)"

Write-Host "`n=== MCP smoke tests passed ==="
```

Expected:
```
OK: MCP servers = 5
OK: MCP bridged tools = <N from auto-connected servers>
OK: Provider — tools=56 resources=17 prompts=4

=== MCP smoke tests passed ===
```

---

## API Reference

### Server Management

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/mcp/servers` | List all registered server configurations |
| `POST` | `/mcp/servers` | Register a new server |
| `DELETE` | `/mcp/servers/{id}` | Delete a server configuration |
| `POST` | `/mcp/servers/{id}/connect` | Connect — spawn subprocess, discover tools/resources/prompts |
| `POST` | `/mcp/servers/{id}/disconnect` | Disconnect — clean shutdown, unregister tools |

### Client Bridge

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/mcp/tools` | All bridged MCP tools (full metadata) |
| `GET` | `/mcp/resources` | Resources grouped by server |
| `GET` | `/mcp/resources/flat` | Flat list with `_server` attribution |
| `POST` | `/mcp/resources/read` | Read resource — body: `{"server":"…","uri":"…"}` |
| `GET` | `/mcp/prompts` | Prompts grouped by server |
| `GET` | `/mcp/prompts/flat` | Flat list with `_server` attribution |
| `POST` | `/mcp/prompts/get` | Resolve a prompt — body: `{"server":"…","name":"…","arguments":{…}}` |

### SSE Provider

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/mcp/serve/sse` | SSE stream — returns `session_id`, then JSON-RPC responses + 30 s keepalives |
| `POST` | `/mcp/serve/messages?session_id=…` | JSON-RPC 2.0 dispatch (8 methods) |
| `GET` | `/mcp/serve/status` | sessions, tools, resources, prompts counts |

**Supported JSON-RPC methods:** `initialize`, `ping`, `tools/list`, `tools/call`, `resources/list`, `resources/read`, `prompts/list`, `prompts/get`

---

## Recommended Third-Party MCP Servers

The official `@modelcontextprotocol/server-*` packages are functional but minimal — most expose only **tools**, not resources or prompts. The list below is a curated set of third-party servers that extend MachinaOS in practical ways. All run via stdio unless noted.

### Productivity & Knowledge

| Server | Package / Command | Why it's useful | Caps |
|---|---|---|---|
| **Obsidian** | `npx -y @cyanheads/obsidian-mcp-server` (env: `OBSIDIAN_API_KEY` from Local REST API plugin) | Read/write Obsidian vault notes from chat. Great for the note-taker agent. | tools |
| **Notion** | `npx -y @suekou/mcp-notion-server` (env: `NOTION_API_TOKEN`) | Search pages, read DBs, create entries. | tools, resources |
| **Linear** | `npx -y mcp-remote https://mcp.linear.app/sse` (HTTP/SSE, OAuth via browser) | Issue tracking — list/create/update Linear issues. | tools, prompts |
| **Slack** | `npx -y @modelcontextprotocol/server-slack` (env: `SLACK_BOT_TOKEN`, `SLACK_TEAM_ID`) | Read/post Slack messages. | tools |
| **Todoist** | `npx -y @abhiz123/todoist-mcp-server` (env: `TODOIST_API_TOKEN`) | Manage tasks from chat. | tools |

### Browser & Web

| Server | Package / Command | Why it's useful | Caps |
|---|---|---|---|
| **Playwright** | `npx -y @playwright/mcp@latest` | Browse, click, type, screenshot real web pages. The most powerful browsing server. | tools |
| **Brave Search** | `npx -y @modelcontextprotocol/server-brave-search` (env: `BRAVE_API_KEY`) | Web search — better than naive scraping. | tools |
| **Tavily** | `npx -y tavily-mcp@latest` (env: `TAVILY_API_KEY`) | AI-optimized web search & extract; designed for LLMs. | tools |
| **Firecrawl** | `npx -y firecrawl-mcp` (env: `FIRECRAWL_API_KEY`) | Bulk site crawling and structured extraction. | tools |
| **Puppeteer** | `npx -y @modelcontextprotocol/server-puppeteer` | Lighter alternative to Playwright. | tools |

### Developer Tooling

| Server | Package / Command | Why it's useful | Caps |
|---|---|---|---|
| **GitHub** | `npx -y @modelcontextprotocol/server-github` (env: `GITHUB_PERSONAL_ACCESS_TOKEN`) | PRs, issues, repo search, file reads. Already in default registry. | tools |
| **GitLab** | `npx -y @modelcontextprotocol/server-gitlab` (env: `GITLAB_PERSONAL_ACCESS_TOKEN`) | GitLab equivalent of the GitHub server. | tools |
| **Sentry** | `npx -y @sentry/mcp-server` (env: `SENTRY_AUTH_TOKEN`) | Pull error reports / issues from Sentry. | tools, resources |
| **Docker** | `npx -y docker-mcp` | List/start/stop containers, view logs. | tools |
| **Kubernetes** | `npx -y mcp-server-kubernetes` | Inspect pods, deployments, logs. | tools |

### Data & Databases

| Server | Package / Command | Why it's useful | Caps |
|---|---|---|---|
| **Postgres** | `npx -y @modelcontextprotocol/server-postgres "postgresql://user:pass@host/db"` | Read-only SQL exploration. Exposes table schema as **resources**. | tools, **resources** |
| **SQLite** | `npx -y @modelcontextprotocol/server-sqlite --db-path /path/to.db` | Same as Postgres but for SQLite. Already in default registry. | tools, **resources** |
| **Redis** | `npx -y @modelcontextprotocol/server-redis "redis://localhost:6379"` | Inspect/query Redis keys. | tools |
| **Elasticsearch** | `npx -y @elastic/mcp-server-elasticsearch` (env: `ES_URL`, `ES_API_KEY`) | Search indices, read mappings. | tools |
| **Snowflake** | `uvx mcp-snowflake-server` (Python) | Query a Snowflake warehouse. | tools |

### LLM-Specialised

| Server | Package / Command | Why it's useful | Caps |
|---|---|---|---|
| **Sequential Thinking** | `npx -y @modelcontextprotocol/server-sequential-thinking` | Chain-of-thought reasoning helper. Already in default registry. | tools |
| **Memory** | `npx -y @modelcontextprotocol/server-memory` | Persistent knowledge graph. Already in default registry. | tools |
| **Time** | `uvx mcp-server-time` (Python) | Timezone-aware time conversion (LLMs are bad at this). | tools |
| **Fetch** | `uvx mcp-server-fetch` (Python, official) | Stricter fetch with robots.txt enforcement and HTML→Markdown. Cleaner alternative to `@tokenizin/mcp-npx-fetch`. | tools |

### Filesystem & Local

| Server | Package / Command | Why it's useful | Caps |
|---|---|---|---|
| **Filesystem (extended)** | `npx -y @modelcontextprotocol/server-filesystem /path/one /path/two` | Sandboxed file ops over multiple roots. Publishes files as **resources**. | tools, **resources** |
| **Everything** | `npx -y @modelcontextprotocol/everything` | Reference server that exposes ALL three caps (tools + resources + prompts) for testing. Same role as our [scripts/demo_mcp_server.py](../scripts/demo_mcp_server.py) but slightly larger. | tools, resources, prompts |

### Demo / Reference

| Server | Package / Command | Why it's useful | Caps |
|---|---|---|---|
| **Machina Demo** | `python scripts/demo_mcp_server.py` | Bundled in this repo. Smallest possible reference covering all 3 caps. Use it to verify the Resources / Prompts UI tabs. | tools, resources, prompts |

### Picking the right one

- **Need to see prompts in the UI?** Install `@modelcontextprotocol/everything`, the bundled `scripts/demo_mcp_server.py`, or the Linear server.
- **Need real resources?** Postgres, SQLite, Filesystem (extended), Sentry, or the demo server.
- **Browsing the web reliably?** Playwright + Tavily is the strongest combo.
- **Coding workflow?** GitHub + the existing `mcp_git` server (already registered) covers most of it.
- **Personal knowledge?** Obsidian or Notion + the bundled `note-taker` agent template.

> **Security note:** every third-party server runs as a local subprocess with the same privileges as MachinaOS. Read the source / readme before installing servers from unknown publishers, especially those requiring API tokens with broad scopes.

---

## Troubleshooting

> **`url= value` argument parsing (space between `=` and value)**
> The planner now handles this correctly — `url= https://…` (space after `=`) is collapsed automatically. Use `url=https://…` without a space for clarity.

> **No result visible after Approve**
> The plan card step now updates in real time via WebSocket (`tool_finished` event). If the step icon doesn't turn green, check that the WebSocket is connected (system status bar, bottom of screen). A result bubble also appears in the chat stream independently of the plan card.

> **`npx not found` — servers skip auto-connect**
> Install Node.js. On Windows ensure `npx.cmd` is in PATH. Verify with `npx --version`.

> **Auto-connect fails silently on startup**
> Check `GET /mcp/servers` for `"connected": false` entries, then try `POST /mcp/servers/{id}/connect` manually and read the response body for the error message.

> **Prompts / Resources tab shows empty state with "Method not found" for every server**
> Most official `@modelcontextprotocol/server-*` packages don't implement the `prompts/list` or `resources/list` capability — only `tools/list`. The empty state lists every server that was checked and the reason each lacks prompts/resources. To verify the tab end-to-end install a server that publishes them: see [Act 5b](#act-5b--demo-mcp-server-reference-implementation) for the bundled demo, or the **Recommended Third-Party MCP Servers** section above.

> **Tool namespace collision after reconnect**
> Disconnect first, then reconnect: `POST /disconnect` → `POST /connect`. This forces a fresh tool discovery pass.

> **SSE stream drops before 30 s keepalive**
> Reconnect (`curl -N …/mcp/serve/sse`), copy the new `session_id`, and re-send `initialize`. The old session is invalidated on disconnect.

> **MCP server subprocess hangs on connect**
> Test the package directly (`npx -y @package/name --help`). Check required env vars (e.g. `GITHUB_PERSONAL_ACCESS_TOKEN`). Force disconnect via `POST /mcp/servers/{id}/disconnect`.

> **MCP tools not callable from Chat without approval**
> All MCP tools require approval. Open the plan card that appeared in Neural Link and click **Approve** to proceed.

> **Notification-heavy server causes handshake timeout**
> The MachinaOS client reads up to 20 lines looking for the matching JSON-RPC `id`. If your server emits more unsolicited notifications, the handshake may appear to hang. Check the server docs for a flag to suppress startup notifications.
